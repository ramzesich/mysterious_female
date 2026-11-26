import { VIEW, PLAYER, CRY, LUNGE, POCKET, MISHAP_SCENES, GAGS, HAND_OVER, TALLY, THROW, IDLE, BUMBOT, LIFT, SIDEWALK, SWIM, BED_JOY, PROMENADE, CUT_SHADOW, LOCKED_PARTS, LONG_FALL_MARGIN, SHOWER, VERBS, HOLDING, SHRUG } from '../config.js';
import { wire } from '../wire.js';
import { Controls } from '../controls.js';
import { scenario } from '../world/mishaps.js';
import { sfx } from '../sfx.js';
import { t, has } from '../lang.js';
import { loadSave, writeSave } from '../save.js';
import { Progression, CARD_COLOURS } from '../progression.js';
import { rumble, rumbleWith } from '../rumble.js';
import { GLASS_LEAF, TRUNK_INSIDE } from '../textures.js';
import { Sea } from '../sea.js';
import { Backdrop, FarGulls, HORIZON_ABOVE, HORIZON_SETTLE, DUSK_LIGHT } from '../background.js';
import { World, OUTSIDE } from '../world/world.js';
import { Soundscape } from '../world/soundscape.js';
import { LooseTangerines } from '../world/tangerine.js';
import { runFrame } from '../world/movers.js';
import { verbs } from '../world/verbs.js';
import { balcony } from '../world/balcony.js';
import { Intro } from '../intro.js';
import { Popups } from '../popup.js';
import { Hud } from '../hud.js';
import { sign } from '../signs.js';
import { Highlight } from '../highlight.js';

// Tile ids from the tileset (see tools/build_slice_map.py).
const LADDER_TOP = 3;
const RAILING = 4;
const RAILING_STOP = 10;   // px short of a leaning railing's foot that she stops
const MIRROR_REACH = 14;   // px from her crew cabin's mirror that E fixes her hair at it

const DEPTH = {
    sky: 0, sea: 1, back: 2, decor: 3, stairs: 4, playerBehind: 5, balustrade: 5.1,
    glassShaft: 5.15, glassCar: 5.2, inGlassCar: 5.25, glassDoors: 5.3,
    frontStairs: 5.4, onFrontStairs: 5.45, frontBalustrade: 5.5, walkFloor: 5.6,
    solid: 6, ladders: 7, liftCar: 7.4, inLift: 7.6, props: 8, exterior: 8.6,
    poolTank: 8.66, swimmer: 8.67, poolWater: 8.68, player: 9, deckDim: 9.7, fx: 10,
};

const approach = (value, target, step) =>
    value < target ? Math.min(value + step, target) : Math.max(value - step, target);

const GAG_SHEETS = new Set(['gags', 'her-mishaps', 'towels', 'drill']);   // the sheets whose clips have a gag's sounds
const HALF = PLAYER.height / 2;
const LAMP_RISE = 81; // the checkpoint lamp sits just above the 74px door
// Each cabin deck's framed pictures between its doors, in the order they hang (their art: `DECK_PICTURES` in
// tools/build_ship_art.py). Deck 4 safety posters, 5 paintings of the ship, 6 old charts and port maps, 8 seascapes,
// 9 botanical prints, 10 old liners' posters.
const DECK_PICTURES = {
    4: ['roster', 'lifejacket', 'escape-plan', 'firstaid', 'lifeboat'].map(n => `d4-${n}`),
    5: ['ship-sea', 'ship-harbour', 'ship-islands', 'ship-bow'].map(n => `d5-${n}`),
    6: ['chart-harbour', 'port-town', 'islands', 'chart-rose'].map(n => `d6-${n}`),
    8: ['waves', 'lighthouse', 'sailboat', 'sunset'].map(n => `d8-${n}`),
    9: ['fern', 'flower', 'lemon', 'monstera'].map(n => `d9-${n}`),
    10: ['liner', 'bow', 'night', 'funnels'].map(n => `d10-${n}`),
};
const DOOR = { width: 28, height: 74 };
const LEAF = 18; // each of an elevator's two sliding door leaves
// Cabin 8206's drawing (tools/draw_cabin.py): its width, where its door is, the ceiling's height
// over the floor, how close to its side walls she can go, and the bed she can jump onto: its ends
// and its top over the floor (the user, 2026-11-06).
const CABIN = { width: 240, doorX: 59, height: 128, stop: 20, bed: [138, 236], bedTop: 32,
                window: [143, 37, 35, 37],   // its glass: x, y, w, h
                doorWindow: [14, 17, 16, 19],     // the glass seen through its open door, in the door's image
                shower: [6, 44, 40, 123],         // the shower room's door, x0, y0, x1, y1 (tools/draw_cabin.py's SHOWER)
                towel: [28, 79], slide: 18 };     // her towel hung on its handle; how far the door slides open
// The linen room's drawing (tools/draw_linen.py), the same way; and the heap of towels (its middle
// and its top over the floor, from the room's left edge), and the vent (its opening's ends).
const LINEN = { width: 240, doorX: 180, height: 128, stop: 20, mouth: 26 };    // (`mouth`: the shaft's mouth's end, tools/population.py's SHAFT)
// The Chapel's drawing (tools/draw_chapel.py, deck 12), the same way.
const CHAPEL = { width: 312, doorX: 59, height: 128, stop: 20 };
const ROOM_DIM = 0.88; // how dark the world round a room she is in goes
// The dim over a hull showing at `a` while a deck is crossfaded to its inside (a look-out's): the hull's colour and the
// dim's together are the dimmed hull's, mixed with the inside, at every step (`(1 - t)` dimmed hull + `t` inside: the
// hull's alpha `(1-t)(1-r) / ((1-t)(1-r) + t)`, its dim `1 - t`, here from the alpha).
const lookDim = a => 1 - (1 - ROOM_DIM) * (1 - a) / (1 - ROOM_DIM + a * ROOM_DIM);
// The room doors' plates washed toward the background (`washPlates`; the user, 2026-11-24, all ten, at 20%: their doors'
// own 35% was "too strong"), and the wall they are washed toward (src/highlight.js's WALL, the doors' too).
const WASHED_PLATES = ['LINEN', 'LAUNDRY', 'DRY STORE', 'STAGE MGR', 'PANTRY', 'GALLEY', 'COLD ROOM', 'STAGE DOOR', 'LIGHTING'];
const PLATE_WASH = 0.2;
const PLATE_WALL = [0xe9, 0xdf, 0xcc];
const BOAT_DEPTH = DEPTH.player + 0.06;   // the boats hanging on the walkway, in front of her (the drill's too)
const WALK_RAIL_DEPTH = DEPTH.player + 0.04;   // the walkway's railing, over her (behind a boat's inside while she is in it)
const WALK_LIFT = 2;
// A pool's tank: its wall's foot, px under the pool's floor (the tank's tiles are drawn in rows of 8 from 4 px under the
// deck: `poolTanks`); the water is drawn down to it.
const TANK_FOOT = 4;
// Her climb into the lifeboat's roof hatch (`roofSteps`): the hatch's far rim and near lip, px over the walkway's floor
// (tools/build_hatch.py's pieces: the boat's rows 26 and 37, its floor at 120); each frame's ms (her front frame and her
// back frame on the roof held longer); how far down her back frame stands in the opening; her `climb-out` frames sinking
// in: [which, its hands' lowest row, px lower] (the last 10 px lower, the user: "Frame 13 is the same as 12. Shift her down").
// (`backDown`: her back frame a little lower, stepping toward the opening: the user, "shift her down a little on frame 9".)
// (`reach`: how far from the hatch's middle E takes her in, and it glows: about the hatch's width, the user, 2026-11-21:
// "Widen the area behind the boat where we can enter the hatch".)
const ROOF = { reach: 26, far: 94, lip: 83, frameMs: 120, frontMs: 300, turnMs: 140, backMs: 200, backDown: 3, inOpening: 22,
               sink: [[2, 56, 0], [1, 44, 0], [0, 44, 10]] };   // her picture's px higher on the boat walkway (the user, 2026-11-21: "shift her two pixels up")
// The bridge's back wall (deck 10): its thickness; how far she goes from its door before it shuts.
const BULKHEAD = { width: 12, shutAway: 70 };

// How stairs look (§5.3, the user's photos): the stair cores' flights, and the atrium's curving
// staircase.
const STAIR_LOOKS = {
    // The funnel's steel stairway (§6.1.10): grating treads, white rails.
    steel: { carpet: 0x9babb2, fleck: 0x625565, nosing: 0x3e3546, side: 0x7f708a, edge: 0x3e3546, thickness: 5,
             glass: false, plain: true, brass: 0xe3e7ea, rail: 0xe8eaec, railLight: 0xffffff },
    core: { carpet: 0x0b5e65, fleck: 0x4d9be6, nosing: 0x2e222f, side: 0xd8cdb8, edge: 0xb9ab90, thickness: 8,
            glass: true, brass: 0xd9a43b, rail: 0xcd683d, railLight: 0xe6904e },
    atrium: { carpet: 0x0b5e65, fleck: 0x8ff8e2, nosing: 0x2e222f, side: 0xf4efe4, edge: 0xd9a43b, thickness: 10,
              glass: false, brass: 0xd9a43b, rail: 0xcd683d, railLight: 0xe6904e },
};

// How a side walk looks (§5.3): the atrium's balconies, and deck 12's walk over the pools.
const SIDEWALK_LOOKS = {
    atrium: { floor: 0x484a77, fleck: 0x8fd3ff, front: 0xf1e8cf, edge: 0xd9a43b, riser: 0xb9a98a,
              light: 0xfff1c9, rail: 0xd9a43b, post: 0xb08a2e },
    deck: { floor: 0xab947a, fleck: 0x9a8469, front: 0xf4f4f4, edge: 0xc7cdd2, riser: 0xc7cdd2,
            light: null, rail: 0xcd683d, post: 0xe3e7ea },
};

// Each hazard gets its own fright (§5.6): her word for it, in the game's language (src/lang.js).
// What she cries at a hit (a scenario's `word`).
const fright = w => has(`fright.${w}`) ? t(`fright.${w}`) : '!';

// Down after a trip or a slip (scareDown), flat on her belly or on her bottom: her picture this many px lower, from this
// frame of her fall on (the frames where she is down), so that she lies or sits on the carpet, not over it (the sit too
// since 2026-11-26, the user: "shifted down by two pixels. In all the occasions").
const LIE_DROP = { px: 2, frame: 3 };

// What Bumbot does at a spot sitting down: he gets up off his haunches before he leaps (`BUMBOT.getUp`).
const SITTING = new Set(['wash', 'bat', 'sit', 'sat']);

export class ShipScene extends Phaser.Scene {
    constructor() {
        super('ship');
    }

    create() {
        this.save = loadSave();
        // The regions, cards, flags and locks (§6.1, src/progression.js).
        this.progress = new Progression(this);
        this.controls = new Controls(this);
        rumbleWith(this.controls);
        this.worldLayer = this.add.layer();
        this.uiLayer = this.add.layer();
        this.DEPTH = DEPTH;
        // The gags' own sounds, on their clips' frames (`GAGS[...].sounds`, §3 1.3): any sprite of
        // the gag sheets, while the gag of her last hit plays. (Before the world, which makes some.)
        this.sys.events.on('addedtoscene', go => {
            // (A sprite put into a layer is added again: one listener each.)
            if (!go.anims || !GAG_SHEETS.has(go.texture?.key) || go.gagEars) return;
            go.gagEars = true;
            const at = (anim, frame) => {
                if (this.mode === 'play') return;
                const s = GAGS[MISHAP_SCENES[this.lastMishap?.id]?.gag]?.sounds?.[anim.key]?.[frame.index];
                if (s) [].concat(s).forEach(n => sfx.at(go.x, go.y)[n]());
            };
            go.on('animationstart', at).on('animationupdate', at);
        });
        // Every popup over a head (src/popup.js; the people's wishes are made with the world).
        this.popups = new Popups(this);
        // The plan's world (§6.1, docs/population.md; src/world/): rooms, people, things, the outside.
        this.world = new World(this);

        this.buildMap();
        this.buildObjects();
        this.world.build();
        // What the plan puts inside a deck in front of her (the ball pit's front wall, the pillow
        // fort) is behind the ship's side from outside: it shows only as its deck is cut open
        // (found in step 11's render of the whole ship: both showed through the closed side).
        for (const t of this.world.things) {
            if (t.route !== 'inside') continue;
            for (const i of t.items || []) {
                if (i.depth > DEPTH.exterior && i.depth < DEPTH.deckDim) this.behindShell(i, t.x ?? i.x, t.y ?? i.y);
            }
        }
        this.buildPlayer();
        this.world.addColliders(this.player);
        // Tangerines loose in the world: knocked out of her pocket (src/world/tangerine.js).
        this.loose = new LooseTangerines(this);
        this.loose.addColliders();
        this.buildCameras();
        this.buildHud();
        this.world.buildHud(this.uiLayer);

        this.mode = 'play'; // play | ladder | stairs | trunk | lift | swim | scripted
        this.lungeUntil = 0;
        this.safeUntil = 0;
        this.flinchUntil = 0;
        this.throwUntil = 0;
        this.throwing = null;
        this.cryGapUntil = 0;
        this.bubbleUntil = 0;
        this.lastTrailAt = 0;
        this.jumpBufferedAt = -Infinity;
        this.script = null;

        this.spawnAt(this.initialSpawn());
        // The ambience and her footsteps (src/world/soundscape.js).
        this.soundscape = new Soundscape(this);
        window.__ship = this; // handle for headless tests and the console
        window.__sfx = sfx;
        // The welcome screen and the intro (docs/intro.md; src/intro.js), in this scene's own
        // picture; `?play` goes straight to the game, as it skipped the title.
        this.fromAfar = false;
        this.intro = new URLSearchParams(location.search).has('play') ? null : new Intro(this);
    }

    // --- Building --------------------------------------------------------------------------

    buildMap() {
        const map = this.make.tilemap({ key: 'ship' });
        this.map = map;
        const props = Array.isArray(map.properties)
            ? Object.fromEntries(map.properties.map(p => [p.name, p.value]))
            : map.properties || {};
        this.mapProps = props;
        this.deckPitch = props.deckPitch;
        this.hullMinX = props.hullMinX;
        this.hullMaxX = props.hullMaxX;
        this.waterY = props.waterY;

        const W = map.widthInPixels;
        const H = map.heightInPixels;
        const tiles = map.addTilesetImage('placeholder', 'tiles');

        // The sea reaches far past the map on every side, so the outside view (O), zoomed right
        // out, shows sky, sea and the ship, never the void (the user, 2026-11-07). Behind it all,
        // the sky, the far sea and the archipelago, fixed to the screen (§5.2).
        const OUT = 2 * W;
        this.farGulls = new FarGulls();
        this.backdrop = new Backdrop(this, { waterY: this.waterY, depth: DEPTH.sky, gulls: this.farGulls });
        const back = map.createLayer('background', tiles).setDepth(DEPTH.back);
        this.solidLayer = map.createLayer('solid', tiles).setDepth(DEPTH.solid);
        this.ladderLayer = map.createLayer('ladders', tiles).setDepth(DEPTH.ladders);
        // The outer shell over everything (§5.3): the deck she is on is cut away, its tiles faded.
        this.exteriorLayer = map.createLayer('exterior', tiles).setDepth(DEPTH.exterior);
        // The pools' tiles below their deck's floor (deck 11's two, deck 12's kids' pool), each out
        // of sight from the deck under it; each tile knows its pool's deck.
        this.poolTile = props.poolTile;
        this.poolTiles = [];
        // The whole tank drawn again over the shell and its windows, its tiled back wall, sides and
        // floor, so the pools have their floor seen from their deck (the user); the water goes over it.
        this.poolTanks = {};
        const floors = JSON.parse(props.deckFloors);
        const spans = JSON.parse(props.poolSpans || '[]');
        this.solidLayer.forEachTile(t => {
            if (t.index !== props.poolTile) return;
            const span = spans.find(([a, b, d]) => t.pixelX >= a && t.pixelX < b && t.y > floors[d] && t.y <= floors[d] + 3);
            if (!span) return;
            t.poolDeck = span[2];
            this.poolTiles.push(t);
        });
        for (const [a, b, deck] of spans) {
            const g = this.poolTanks[deck] ??= this.add.graphics().setDepth(DEPTH.poolTank);
            const top = floors[deck] * 16;
            for (let x = a; x < b; x += 8) {
                for (let y = top + 4; y < top + 48; y += 8) {
                    const edge = x < a + 16 || x >= b - 16 || y >= top + 32;
                    g.fillStyle(edge ? 0x8fd3ff : 0x4d9be6, 1).fillRect(x, y, 8, 8);
                    g.fillStyle(edge ? 0xe3f4fb : 0x8fd3ff, 1).fillRect(x, y, 8, 1).fillRect(x, y, 1, 8);
                }
            }
        }
        this.deckFloors = JSON.parse(props.deckFloors);
        // What she can use pulses where E would act on it (src/highlight.js), washed as the props round it are.
        this.highlight = new Highlight(this, props.washLevels ? JSON.parse(props.washLevels) : null);
        // (Once the doors' washes at rest are worked out, their plates take them: `washPlates`.)
        const plates = () => {
            if (!this.highlight.restDone) return;
            this.events.off('postupdate', plates);
            this.washPlates();
        };
        this.events.on('postupdate', plates);
        const cut = this.cutIds = new Set(String(props.exteriorCut).split(',').map(Number));
        this.shellTiles = {};
        this.shellAlpha = {};
        // A room with its own piece of shell (the bridge): cut away while she is in it, the rest of
        // its deck closed; closed while she is anywhere else.
        this.shellRooms = JSON.parse(props.shellRooms || '[]');
        const allCut = new Set();
        this.exteriorLayer.forEachTile(t => {
            if (!cut.has(t.index)) return;
            const deck = this.deckOfRow(t.y);
            const room = this.shellRooms.find(r => r.deck === deck && t.pixelX >= r.x0 && t.pixelX < r.x1);
            (this.shellTiles[room ? room.key : deck] ||= []).push(t);
            allCut.add(`${t.x},${t.y}`);
        });
        for (const deck of Object.keys(this.shellTiles)) this.shellAlpha[deck] = 1;
        this.viewDeck = null;
        // The cut-out's edges in shadow (§5.3, the user, 2026-11-03), so the deck she is on reads
        // as the inside of the ship: a soft dark band inside the opening wherever the shell goes on,
        // deepest under the deck above. It shows as the deck is cut away.
        this.cutShadows = {};
        // Where the deck ends in the ship's wall, a strip of that wall is drawn over her, so as she
        // runs into it, she goes behind it (the user, 2026-11-03).
        const endCover = this.endCoverGfx = this.add.container(0, 0).setDepth(DEPTH.player + 0.05);
        const coverW = props.endCover || 32;
        // The plating's seams (tools/shell_paint.py), for the white walls the game draws itself.
        this.seams = JSON.parse(props.plateSeams || 'null');
        for (const [key, list] of Object.entries(this.shellTiles)) {
            const deck = parseInt(key, 10);
            const own = new Set(list.map(t => `${t.x},${t.y}`));
            const g = this.add.graphics().setDepth(DEPTH.exterior + 0.01).setAlpha(0);
            const band = (x, y, w, h, side, depth) => {
                const steps = Math.ceil(depth / 2);
                for (let i = 0; i < steps; i++) {
                    g.fillStyle(CUT_SHADOW.colour, CUT_SHADOW.alpha * (1 - i / steps) ** 1.6);
                    if (side === 'top') g.fillRect(x, y + i * 2, w, 2);
                    else if (side === 'bottom') g.fillRect(x, y + h - (i + 1) * 2, w, 2);
                    else if (side === 'left') g.fillRect(x + i * 2, y, 2, h);
                    else g.fillRect(x + w - (i + 1) * 2, y, 2, h);
                }
            };
            for (const t of list) {
                // An open deck's floor edge (no indoors above it) casts no shadow: it isn't inside.
                if (t.y === this.deckFloors[deck] && !own.has(`${t.x},${t.y - 1}`)) continue;
                const shell = (dx, dy) => {
                    if (own.has(`${t.x + dx},${t.y + dy}`)) return false;
                    const n = this.exteriorLayer.getTileAt(t.x + dx, t.y + dy);
                    return !!n && n.index > 0;
                };
                const [x, y, w, h] = [t.pixelX, t.pixelY, t.width, t.height];
                if (shell(0, -1)) band(x, y, w, h, 'top', CUT_SHADOW.top);
                if (shell(0, 1)) band(x, y, w, h, 'bottom', CUT_SHADOW.bottom);
                if (shell(-1, 0)) band(x, y, w, h, 'left', CUT_SHADOW.ends);
                if (shell(1, 0)) band(x, y, w, h, 'right', CUT_SHADOW.ends);
                // (Not where a room's own shell meets its deck's: that is no end of the deck.)
                const air = t.y !== this.deckFloors[deck];
                const end = dx => shell(dx, 0) && !allCut.has(`${t.x + dx},${t.y}`);
                const cover = cx => {
                    // (The lowest strip, over the floor, reaches `PLAYER.sink` into it: her feet hidden whole.)
                    const hh = t.y + 1 === this.deckFloors[deck] ? h + PLAYER.sink : h;
                    this.plateTiles(endCover, cx, y, coverW, hh);
                    (this.endCovers ||= []).push({ x: cx, y, w: coverW, h: hh });
                };
                if (air && end(-1)) cover(x - coverW);
                if (air && end(1)) cover(x + w);
            }
            this.cutShadows[key] = g;
        }
        // Where a deck steps back, the shell slopes across the step, so the outline runs smoothly.
        // Its plating is painted as the side's tiles are (step 11): the seams run on across it.
        const colour = c => Phaser.Display.Color.HexStringToColor(c).color;
        this.shellSlopes = JSON.parse(props.shellSlopes || '[]').map(s => {
            const g = this.add.graphics().setDepth(DEPTH.exterior);
            g.fillStyle(0xe8eaec, 1).fillPoints([{ x: s.x1, y: s.yTop }, { x: s.x0, y: s.yFloor }, { x: s.x1, y: s.yFloor }], true);
            for (const [x, y, w, h, c] of s.marks || []) g.fillStyle(colour(c), 1).fillRect(x, y, w, h);
            return { deck: s.deck, end: s.end, gfx: g, x0: Math.min(s.x0, s.x1), x1: Math.max(s.x0, s.x1), yTop: s.yTop, yFloor: s.yFloor };
        });
        // Under each slope, the floor's own row of the side copied over it, `PLAYER.sink` tall: where the
        // slope hides her (the stern terraces), her lowest row, drawn into the floor's row, is hidden too;
        // the picture is the same pixels, so nothing else changes. It fades and stands as its slope does.
        for (const q of this.shellSlopes.slice()) {
            const foot = this.plateCopy(q.x0, q.yFloor, q.x1 - q.x0, PLAYER.sink, DEPTH.exterior);
            this.shellSlopes.push({ deck: q.deck, end: q.end, gfx: foot, foot: true });
        }
        // The shell's details (§5.3): windows, balconies, portholes, the funnel, the mast, the domes;
        // each on its deck's wall, fading with it, or always there ("fixed").
        for (const [owner, shapes] of Object.entries(JSON.parse(props.shellDetails || '{}'))) {
            const g = this.add.graphics().setDepth(DEPTH.exterior + 0.05);
            for (const s of shapes) {
                if (s[0] === 'r') g.fillStyle(colour(s[5]), 1).fillRect(s[1], s[2], s[3], s[4]);
                else if (s[0] === 'c') g.fillStyle(colour(s[4]), 1).fillCircle(s[1], s[2], s[3]);
                else g.fillStyle(colour(s[2]), 1).fillPoints(s[1].map(([x, y]) => ({ x, y })), true);
            }
            this.shellSlopes.push({ deck: owner === 'fixed' ? null : owner.includes(':') ? owner : Number(owner), gfx: g });
        }

        this.solidLayer.setCollisionByExclusion([-1]);
        // A ladder's top is a one-way floor: solid to stand on, open to climb through. A railing
        // where an open deck ends stays solid but is drawn with the same railing as the decks'
        // sides (white rails, a wooden handrail), one piece standing on its foot. Where the ship's
        // side slopes in toward it from below, it leans on in at the same angle, carrying the slope
        // on up over the deck (the user, 2026-11-06).
        const slopesBelow = JSON.parse(props.shellSlopes || '[]');
        const railings = [];
        this.solidLayer.forEachTile(t => {
            if (t.index === LADDER_TOP) t.setCollision(false, false, true, false);
            if (t.index !== RAILING) return;
            t.setAlpha(0);
            if (this.solidLayer.getTileAt(t.x, t.y + 1)?.index === RAILING) return;
            const x = t.pixelX + t.width / 2, deck = this.deckOfRow(t.y);
            const s = slopesBelow.find(s => s.deck === deck - 1 && Math.abs(s.x1 - x) <= 24);
            // Each stands in from the deck's end, its outer foot where the floor ends (the user,
            // 2026-11-06): inward is the side the deck's floor goes on.
            const inward = s ? (s.x0 < s.x1 ? 1 : -1) : (this.solidLayer.getTileAt(t.x + 1, t.y + 1)?.index > 0 ? 1 : -1);
            const footX = t.pixelX + (inward > 0 ? 0 : t.width) + inward * this.textures.getFrame('shipart', 'railing-bg').width / 2;
            const img = s ? this.leaningRailing(footX, t.pixelY + t.height, Math.abs(s.x1 - s.x0) / (s.yFloor - s.yTop), inward)
                : this.add.image(footX, t.pixelY + t.height, 'shipart', 'railing-bg').setOrigin(0.5, 1);
            // A leaning railing reaches in over the deck, in front of her: she stands behind it, and
            // stops a little short of its foot (the user, 2026-11-06). An upright one, at deck 7's
            // ends, is in front of her too (the user, 2026-11-07).
            railings.push(this.withFoot(img).setDepth(DEPTH.player + 0.04));
            // From outside, a leaning railing is behind its deck's wall: it shows only while she
            // is on its deck (in front of her, as above) or that deck is cut away (the user,
            // 2026-11-07).
            if (s) (this.leaningRailings ||= []).push({ deck, img });
            if (s) {
                const edge = footX + inward * t.width / 2;
                const stop = this.add.zone(edge + inward * RAILING_STOP / 2, t.pixelY, RAILING_STOP, 2 * t.height);
                this.physics.add.existing(stop, true);
                (this.railingStops ||= []).push(stop);
            }
        });

        // The sea (§5.2, the user, 2026-11-07): rows of waves in front of the hull's foot, foam
        // along its waterline from the stem to the stern, the bow wave, the wake.
        const hullRow = this.waterY / 16 - 1;
        const hullCols = [];
        for (const layer of [this.exteriorLayer, this.solidLayer]) {
            layer.forEachTile(t => { if (t.index > 0 && t.y === hullRow) hullCols.push(t.x); });
        }
        this.seaView = new Sea(this, {
            x0: -OUT, x1: W + OUT, y: this.waterY, bottom: H + OUT,
            bowX: Math.min(...hullCols) * 16, sternX: (Math.max(...hullCols) + 1) * 16,
            depth: DEPTH.exterior + 0.25, front: DEPTH.exterior + 0.3,     // the hull's foot under water
        });
        this.worldLayer.add([...this.backdrop.objects, ...this.seaView.objects, back, this.solidLayer, this.ladderLayer, ...railings, this.exteriorLayer,
            ...Object.values(this.cutShadows), ...this.shellSlopes.map(s => s.gfx), endCover, ...Object.values(this.poolTanks)]);
        this.buildDeckDim(coverW);
    }

    // The world round the deck she is on, dimmed as round a room she is in (the user, 2026-11-08),
    // walls at the deck's ends included. One fixed panel for everything past the decks, and each
    // deck's opening (its own piece of shell, a room's, and the strip `wall` wide each way where
    // the two meet, with the door between them) dimmed as far as that part of the shell is closed.
    buildDeckDim(wall) {
        // Past a deck's open stretch the panels reach the whole ship's length: deck 3's is only its
        // crew corridor (82-98 m), and a fixed 4000 px left its hull aft of 181 m undimmed (the
        // user saw it from deck 4, 2026-11-15).
        const far = this.map.widthInPixels + 4000;
        const panel = () => {
            const g = this.add.graphics().setDepth(DEPTH.deckDim).setAlpha(0).setVisible(false);
            this.worldLayer.add(g);
            return g.fillStyle(0x0d0b14, ROOM_DIM);
        };
        const decks = {};
        for (const [key, list] of Object.entries(this.shellTiles)) {
            const deck = parseInt(key, 10), floor = this.deckFloors[deck];
            const air = list.filter(t => t.y !== floor);
            const floorAt = new Set(list.filter(t => t.y === floor).map(t => t.x));
            let a = Math.min(...air.map(t => t.x)), b = Math.max(...air.map(t => t.x));
            // An open part of the deck has a floor and no shell over it: it runs on to the floor's end.
            while (floorAt.has(a - 1)) a--;
            while (floorAt.has(b + 1)) b++;
            (decks[deck] ||= []).push({ keys: [key], x0: a * 16, x1: (b + 1) * 16, y0: Math.min(...air.map(t => t.pixelY)), y1: (floor + 1) * 16 });
        }
        const pieces = [], outer = panel();
        const bands = Object.values(decks).map(parts => {
            parts.sort((p, q) => p.x0 - q.x0);
            for (let i = parts.length - 1; i > 0; i--) {
                const [l, r] = [parts[i - 1], parts[i]];
                parts.push({ keys: [...l.keys, ...r.keys], x0: r.x0 - wall, x1: r.x0 + wall, y0: r.y0, y1: r.y1 });
                l.x1 -= wall;
                r.x0 += wall;
            }
            pieces.push(...parts);
            return { x0: Math.min(...parts.map(p => p.x0)), x1: Math.max(...parts.map(p => p.x1)), y0: parts[0].y0, y1: parts[0].y1 };
        }).sort((p, q) => p.y0 - q.y0);
        for (const { x0, x1, y0, y1 } of bands) {
            outer.fillRect(x0 - far, y0, far, y1 - y0);
            outer.fillRect(x1, y0, far, y1 - y0);
        }
        const [top, bottom] = [bands[0].y0, bands[bands.length - 1].y1];
        const [left, right] = [Math.min(...bands.map(b => b.x0)) - far, Math.max(...bands.map(b => b.x1)) + far];
        outer.fillRect(left, top - far, right - left, far);
        outer.fillRect(left, bottom, right - left, far);
        for (const p of pieces) {
            p.gfx = panel().fillRect(p.x0, p.y0, p.x1 - p.x0, p.y1 - p.y0);
            p.dim = 1;
        }
        this.deckDim = { outer, pieces, shown: 0 };
    }

    // Each frame, with the cut-away. Never over her: a piece she is in stays clear (she is drawn
    // under the dim, so that what stands in front of her on other decks goes dark with the rest).
    updateDeckDim(dt) {
        const d = this.deckDim, p = this.player;
        // Out in the open, with no ship's side beside her at that deck's height, nothing is dimmed
        // (the user, 2026-11-08).
        const open = this.viewDeck !== null
            && !this.exteriorLayer.getTileAt(Math.floor(p.x / 16), this.deckFloors[Math.round(this.viewDeck)] - 4);
        // (`dimHeld`: a scripted way from one deck into another that holds the view by `viewOverride` and is still hers:
        // down the pool's hatch, the decks dimmed as they are for her.)
        const on = this.route === 'inside' && this.viewDeck !== null && !open && (this.viewOverride == null || this.dimHeld) ? 1 : 0;
        const smooth = dt > 0 && this.route === 'inside';
        // (`dimOverride`: the intro brings the dark on with the opening of deck 3's side.)
        d.shown = this.dimOverride != null ? this.dimOverride : smooth ? approach(d.shown, on, dt * 6) : on;
        d.outer.setVisible(d.shown > 0).setAlpha(d.shown);
        for (const c of d.pieces) {
            // (Her head counts in the deck above only past its floor, not in the ceiling under it:
            // jumping on deck 4's climb shelf, her head touched the ceiling and deck 5's dim lifted
            // and came back each jump, the user, 2026-11-17. A piece reaches 16 px under its floor.)
            const hers = p.x >= c.x0 && p.x < c.x1 && p.y > c.y0 && p.y - PLAYER.height < c.y1 - 16
                // (Dropping out of the pool's hatch her head is still at the deck above's height: that deck is not hers.)
                && (!this.dimHeld || c.keys.some(k => parseInt(k, 10) === Math.round(this.viewDeck)));
            // (A deck a look-out opens is dimmed as its hull still shows, hers or not, so that the hull and its dim fade
            // together: `world.lookOpen`, the cut-away.)
            const look = this.world?.lookOpen, looked = look && c.keys.some(k => look[k]);
            const dim = looked ? Math.min(...c.keys.map(k => look[k] ? lookDim(this.shellAlpha[k]) : this.shellAlpha[k]))
                : hers ? 0 : Math.min(...c.keys.map(k => this.shellAlpha[k]));
            c.dim = smooth && !looked ? approach(c.dim, dim, dt * 8) : dim;
            c.gfx.setVisible(d.shown > 0 && c.dim > 0).setAlpha(d.shown * c.dim);
        }
    }

    buildObjects() {
        const prop = (o, name, fallback) => (o.properties || []).find(p => p.name === name)?.value ?? fallback;
        this.checkpoints = [];
        this.tangerines = [];
        this.flights = [];
        this.vacuums = [];
        this.cats = [];
        this.rooms = [];
        this.bulkheads = [];
        this.places = {};
        this.promenade = null;
        this.route = 'inside';
        this.trunks = [];
        this.lifts = [];
        this.walks = [];
        this.pools = [];
        this.walkGroup = this.physics.add.staticGroup();
        this.crates = this.physics.add.staticGroup();
        // A flight's balustrade is in front of her while she climbs it, behind her when she passes.
        // The atrium's flights in front of the glass elevator are drawn on their own, over it.
        const stairsGfx = {
            back: this.add.graphics().setDepth(DEPTH.stairs),
            backRail: this.add.graphics().setDepth(DEPTH.balustrade),
            front: this.add.graphics().setDepth(DEPTH.frontStairs),
            frontRail: this.add.graphics().setDepth(DEPTH.frontBalustrade),
        };
        const decorGfx = this.add.graphics().setDepth(DEPTH.decor);
        // The walls' own lines (panel seams), behind every door and fitting on them.
        this.wallGfx = this.add.graphics().setDepth(DEPTH.decor - 0.05);
        this.worldLayer.add([this.wallGfx, decorGfx, ...Object.values(stairsGfx)]);
        // The sea-view windows show the live background (§5.2, the user, 2026-11-07): a copy of it
        // over the wall, cut to their panes; whatever is on the glass (glints, mullions, curtains)
        // goes on `glassGfx` over it.
        this.windowView = this.addWindowView(DEPTH.decor + 0.005);
        this.glassGfx = this.add.graphics().setDepth(DEPTH.decor + 0.006);
        this.worldLayer.add(this.glassGfx);

        const objects = this.map.getObjectLayer('objects').objects;
        const endWalls = [];
        // Trunk doors take the place of any cabin door drawn where they stand.
        this.trunkDoorSpots = objects.filter(o => o.type === 'trunk')
            .flatMap(o => String(prop(o, 'floors', '')).split(',').map(y => ({ x: o.x, y: Number(y) })));
        // So do crew doors (checkpoints): no cabin door crowds another door.
        this.doorSpots = [...this.trunkDoorSpots, ...objects.filter(o => o.type === 'checkpoint').map(o => ({ x: o.x, y: o.y }))];
        // So does the bridge's door, in its wall across the deck.
        this.doorSpots.push(...objects.filter(o => o.type === 'bulkhead').map(o => ({ x: o.x, y: o.y })));
        // Cabin 8206's open door takes the place of its cabin door; so does the linen room's.
        this.openCabinDoors = objects.filter(o => o.type === 'cabin' || o.type === 'linen').map(o => ({ x: o.x, y: o.y }));
        // And the plan's rooms and checkpoints (maps/world.json).
        this.doorSpots.push(...this.world.doorSpots());
        this.openCabinDoors.push(...this.world.doorSpots());

        for (const o of objects) {
            switch (o.type) {
                case 'spawn':
                    this.spawnPoint = { id: 'spawn', x: o.x, y: o.y };
                    break;

                case 'place':
                    this.places[o.name] = { id: o.name, x: o.x, y: o.y, route: prop(o, 'route', 'inside') };
                    break;

                case 'progression':
                case 'region':
                case 'card':
                case 'trigger':
                    this.progress.addObject(o, prop);
                    break;

                case 'checkpoint':
                    this.addCheckpoint(o.name, o.x, o.y);
                    break;

                case 'tangerine': {
                    // Everything rests on something (§6.3): here, a small side table.
                    const table = this.add.image(o.x, o.y, 'sidetable').setOrigin(0.5, 1).setDepth(DEPTH.decor);
                    this.worldLayer.add(table);
                    this.addTangerine(o.name, o.x, o.y - table.height);
                    break;
                }

                case 'stairs': {
                    const [a, b] = o.polyline.map(p => ({ x: o.x + p.x, y: o.y + p.y }));
                    const [bottom, top] = a.y > b.y ? [a, b] : [b, a];
                    const flight = {
                        name: o.name, bottom, top, lock: prop(o, 'lock', ''),
                        curve: prop(o, 'curve', false), front: prop(o, 'front', false), look: prop(o, 'look', ''),
                    };
                    flight.length = this.flightLength(flight);
                    this.flights.push(flight);
                    // The funnel's stairway is outside, on the funnel: over the ship's side, she in front of it.
                    if (flight.look === 'steel') {
                        flight.outside = true;
                        const [fg, fr] = [this.add.graphics().setDepth(DEPTH.exterior + 0.06), this.add.graphics().setDepth(DEPTH.player + 0.3)];
                        this.worldLayer.add([fg, fr]);
                        this.drawStairs(fg, fr, flight);
                        this.stairTreads(flight);
                    } else if (flight.front) this.drawStairs(stairsGfx.front, stairsGfx.frontRail, flight);
                    else this.drawStairs(stairsGfx.back, stairsGfx.backRail, flight);
                    break;
                }

                case 'breakable': {
                    if (this.save.broken.includes(o.name)) break;
                    const crate = this.crates.create(o.x + o.width / 2, o.y + o.height / 2, 'crate');
                    crate.setDepth(DEPTH.props);
                    crate.name = o.name;
                    this.worldLayer.add(crate);
                    break;
                }

                case 'vacuum': {
                    // (The one she rides in her gag, 5b: cut from that picture, tools/build_things.py.
                    // Set 2 px down into the carpet's top line, and her ride with it, `ride.y`: the
                    // user, 2026-11-17.) In front of the doors it passes (at `DEPTH.props` too, added after it: the stage
                    // manager's door hid it, the user, 2026-11-26).
                    const sprite = this.add.image(o.x, o.y + 2, 'things', 'robot-vacuum').setOrigin(0.5, 1).setDepth(DEPTH.props + 0.01);
                    this.worldLayer.add(sprite);
                    this.vacuums.push({
                        sprite, alive: true, dir: 1,
                        minX: prop(o, 'minX', o.x - 80), maxX: prop(o, 'maxX', o.x + 80), speed: prop(o, 'speed', 40),
                    });
                    break;
                }

                case 'bumbot':
                    this.addCat(o.name, o.x, o.y, prop(o, 'activity', 'wash'), prop(o, 'escape', 1));
                    break;

                case 'trunk':
                    this.buildTrunk(o, prop(o, 'floors', ''), prop(o, 'oneWay', false), prop(o, 'card', null));
                    break;

                case 'atrium':
                    this.buildAtrium(o, prop(o, 'levels', ''));
                    break;

                case 'sidewalk':
                    this.buildSidewalk(o, prop(o, 'style', 'atrium'), prop(o, 'dropThrough', false));
                    break;

                case 'pool':
                    this.buildPool(o, prop(o, 'deck', 11));
                    break;

                case 'lift':
                    this.buildLift(o, prop(o, 'floors', ''), prop(o, 'decks', ''), prop(o, 'regions', ''), prop(o, 'glass', false));
                    break;

                case 'prop': {
                    // Furniture and fittings (§5.3): on the floor, on another piece, or on the wall.
                    const piece = this.add.image(o.x, o.y - prop(o, 'dy', 0), 'shipart', prop(o, 'frame', ''))
                        .setOrigin(0.5, 1).setDepth(prop(o, 'front', false) ? DEPTH.player + 0.04 : DEPTH.decor + 0.1)
                        .setFlipX(prop(o, 'flip', false));
                    if (prop(o, 'front', false) && prop(o, 'dy', 0) === 0) this.withFoot(piece);
                    this.worldLayer.add(piece);
                    // A piece in front of her under a deck's sloped front plate (the mooring deck's railing, which
                    // runs on to deck 7's wall): behind the plate while it is shown, in front of her once it is
                    // cut away (the user, 2026-11-18: the plating should "hide the balcony railings behind them").
                    const slope = prop(o, 'front', false) && this.shellSlopes.find(q => q.x0 !== undefined
                        && o.x + piece.width / 2 > q.x0 && o.x - piece.width / 2 < q.x1 && o.y > q.yTop && o.y - piece.height < q.yFloor);
                    if (slope) (this.underSlopes ||= []).push({ slope, img: piece });
                    break;
                }

                case 'sign': {
                    // A brass plaque in the lobbies (the deck number), a paper sign elsewhere.
                    const plaque = prop(o, 'style', '') === 'plaque';
                    const text = this.add.text(o.x, o.y, prop(o, 'text', ''), {
                        fontFamily: 'Verdana, sans-serif', fontSize: '7px', fontStyle: plaque ? 'bold' : 'normal',
                        color: plaque ? '#45293f' : '#8f846f', backgroundColor: plaque ? '#d9a43b' : '#f3ecdd',
                        padding: { x: 3, y: 2 }, resolution: 4,
                    }).setOrigin(0.5).setDepth(DEPTH.decor);
                    this.worldLayer.add(text);
                    break;
                }

                case 'livery': {
                    // The bow's hull (§5.3): white plating with a smooth edge along the raked stem,
                    // over the tiles' steps; and the ship's sun livery, the real one, in pieces by
                    // the wall each is painted on, so each fades with its deck's cut-away.
                    const stem = String(prop(o, 'stem', '')).split(',').map(pair => {
                        const [x, y] = pair.split(':').map(Number);
                        return { x, y };
                    });
                    // Its aft side the block's end, or two tiles aft of the stem where the stem, raking
                    // aft toward the waterline, passes it: the outline must never cross itself, or
                    // the fill strays over the decks (the user saw a wedge on deck 4, 2026-11-08).
                    const right = o.x + o.width;
                    const back = stem.map(q => ({ x: Math.max(right, q.x + 32), y: q.y })).reverse();
                    // Under the hull's tiles, which carry the plating's seams and marks (step 11): it
                    // shows only along the stem, forward of the first tiles; the seams run on
                    // across it there as marks.
                    const plating = this.add.graphics().setDepth(DEPTH.solid - 0.05);
                    plating.fillStyle(0xe8eaec, 1).fillPoints([...stem, ...back], true);
                    for (const [x, y, w, h, c] of JSON.parse(this.mapProps.stemMarks || '[]')) {
                        plating.fillStyle(Phaser.Display.Color.HexStringToColor(c).color, 1).fillRect(x, y, w, h);
                    }
                    // The stern's counter (the user, 2026-11-14): under deck 3 the transom curves
                    // forward down to the waterline. Its smooth edge, aft of the hull's last tiles
                    // in each row, is drawn the same way, the plating's marks across it.
                    const edge = String(this.mapProps.sternEdge || '').split(',').filter(Boolean).map(pair => {
                        const [x, y] = pair.split(':').map(Number);
                        return { x, y };
                    });
                    if (edge.length) {
                        const inner = edge.map(q => ({ x: q.x - 40, y: q.y })).reverse();
                        plating.fillStyle(0xe8eaec, 1).fillPoints([...edge, ...inner], true);
                        for (const [x, y, w, h, c] of JSON.parse(this.mapProps.sternMarks || '[]')) {
                            plating.fillStyle(Phaser.Display.Color.HexStringToColor(c).color, 1).fillRect(x, y, w, h);
                        }
                    }
                    this.worldLayer.add(plating);
                    // Over the shell, under its windows and balconies.
                    for (const piece of String(prop(o, 'pieces', '')).split(',').filter(Boolean)) {
                        const [frame, x, y, owner] = piece.split(':');
                        const img = this.add.image(Number(x), Number(y), 'livery', frame).setOrigin(0).setDepth(DEPTH.exterior + 0.02);
                        this.worldLayer.add(img);
                        const deck = owner === 'fixed' ? null : owner.includes(':') ? owner : Number(owner);
                        this.shellSlopes.push({ deck, gfx: img });
                        // Where the wall at a deck's end is drawn over her, its paint is drawn
                        // over that strip too.
                        for (const c of this.endCovers || []) {
                            const cx = Math.max(c.x, img.x), cy = Math.max(c.y, img.y);
                            const cw = Math.min(c.x + c.w, img.x + img.width) - cx, ch = Math.min(c.y + c.h, img.y + img.height) - cy;
                            if (cw <= 0 || ch <= 0) continue;
                            const top = this.add.image(img.x, img.y, 'livery', frame).setOrigin(0)
                                .setCrop(cx - img.x, cy - img.y, cw, ch).setDepth(DEPTH.player + 0.051);
                            this.worldLayer.add(top);
                            this.shellSlopes.push({ deck, gfx: top });
                        }
                    }
                    break;
                }

                case 'promenade':
                    this.buildPromenade(o, prop);
                    break;

                case 'cabin':
                    this.buildCabin(o, prop);
                    break;

                case 'chapel':
                    this.buildChapel(o);
                    break;
                case 'linen':
                    this.buildLinenRoom(o, prop);
                    break;

                case 'bulkhead':
                    this.buildBulkhead(o, prop(o, 'x0', o.x - 600), prop(o, 'key', ''), prop(o, 'text', ''),
                        prop(o, 'sub', ''), prop(o, 'leaf', 'door-crew'), prop(o, 'colour', '#ae2334'),
                        { width: prop(o, 'width', BULKHEAD.width), swing: prop(o, 'swing', -1), wall: prop(o, 'wall', ''), frame: prop(o, 'frame', ''),
                          lock: prop(o, 'lock', ''), signUp: prop(o, 'sign_up', 0) });
                    break;

                // Outdoors with no way in (deck 7's stern strip, §5.3; the aft terraces behind decks
                // 8-10's end walls): while she is on it the ship's side stays closed, the deck's
                // inside out of sight (the user, 2026-11-06).
                case 'outdoors': {
                    // A strip of plating over the wall's edge beside it, there only while she is on
                    // it, so nothing of her shows past the wall.
                    const end = prop(o, 'end', 'aft');
                    const cover = this.plateCopy(end === 'aft' ? o.x - 16 : o.x + o.width, o.y - this.deckPitch + 16, 16, this.deckPitch - 16 + PLAYER.sink,
                        DEPTH.player + 0.05).setVisible(false);
                    (this.outdoors ||= []).push({ x0: o.x, x1: o.x + o.width, floor: o.y, cover });
                    // The sloped stern plating over it is drawn in front of her, and stays there at
                    // all times, the deck cut open or not: she is always hidden behind it (the user).
                    const deck = prop(o, 'deck', 7);
                    this.shellSlopes.filter(s => s.deck === deck && s.end === end).forEach(s => {
                        s.gfx.setDepth(DEPTH.player + 0.05);
                        s.always = true;
                    });
                    break;
                }

                case 'bulwark': {
                    // An open deck's white bulwark and glass windscreen, in front of her (deck 11's
                    // front, the user): she is hidden behind the white and seen through the glass.
                    // `glass`: how tall the windscreen stands (deck 12's: a tall one, §6.1.9).
                    const g = this.add.graphics().setDepth(DEPTH.player + 0.04);
                    const top = prop(o, 'glass', 48);
                    g.fillStyle(0xbfe6f5, 0.45).fillRect(o.x, o.y - top, o.width, top - 24);
                    g.fillStyle(0xe8eaec, 1).fillRect(o.x, o.y - 24, o.width, 24 + PLAYER.sink);
                    g.fillStyle(0xcd683d, 1).fillRect(o.x, o.y - top - 2, o.width, 2);
                    if (top > 48) g.fillStyle(0xffffff, 0.35).fillRect(o.x, o.y - top + 10, o.width, 1);
                    for (let x = o.x; x < o.x + o.width; x += 48) g.fillStyle(0xe8eaec, 1).fillRect(x, o.y - top - 2, 2, top - 22);
                    this.worldLayer.add(g);
                    break;
                }

                case 'glasswall': {
                    // Deck 11's glass walls along its open stretches, in white frames (the user's
                    // photo from deck 12): from its floor up to deck 12's, behind everything on it.
                    const g = this.add.graphics().setDepth(DEPTH.back + 0.5);
                    const x1 = o.x + o.width;
                    if (prop(o, 'style', '') === 'railing') {
                        // The Great Outdoors' glass railing on the far side (the user): glass panes
                        // between white posts, an orange handrail on top.
                        const rail = o.y - 44;
                        g.fillStyle(0xbfe6f5, 0.45).fillRect(o.x, rail, o.width, 44);
                        for (let x = o.x; x < x1; x += 48) g.fillStyle(0xe8eaec, 1).fillRect(x, rail, 2, 44);
                        g.fillStyle(0xe8eaec, 1).fillRect(x1 - 2, rail, 2, 44);
                        g.fillStyle(0xcd683d, 1).fillRect(o.x, rail - 2, o.width, 3);
                        this.worldLayer.add(g);
                        break;
                    }
                    const top = o.y - this.deckPitch + 16, h = o.y - top;
                    g.fillStyle(0xbfe6f5, 0.22).fillRect(o.x, top, o.width, h);
                    g.fillStyle(0xffffff, 0.25).fillRect(o.x, top + 8, o.width, 2);
                    g.fillStyle(0xe8eaec, 1).fillRect(o.x, top, o.width, 3);
                    for (let x = o.x; x < x1; x += 48) g.fillStyle(0xe8eaec, 1).fillRect(x, top, 2, h);
                    g.fillStyle(0xe8eaec, 1).fillRect(x1 - 2, top, 2, h);
                    this.worldLayer.add(g);
                    break;
                }

                case 'funnel':
                    this.buildFunnel(o);
                    break;

                case 'nameboard': {
                    // The ship's name under the funnel: white letters on a navy board, outside.
                    const g = this.add.graphics().setDepth(DEPTH.exterior + 0.05);
                    g.fillStyle(0x1d2b53, 1).fillRect(o.x, o.y, o.width, o.height);
                    g.fillStyle(0x9babb2, 1).fillRect(o.x, o.y, o.width, 1).fillRect(o.x, o.y + o.height - 1, o.width, 1);
                    const t = this.add.text(o.x + o.width / 2, o.y + o.height / 2 + 1, prop(o, 'text', ''), {
                        fontFamily: 'Verdana, sans-serif', fontSize: '18px', fontStyle: 'bold', color: '#ffffff', resolution: 4,
                    }).setOrigin(0.5).setDepth(DEPTH.exterior + 0.06);
                    t.setLetterSpacing?.(3);
                    t.setScale(Math.min(1, (o.width - 16) / t.width));
                    this.worldLayer.add([g, t]);
                    break;
                }

                case 'endwall': {
                    // The ship's wall where a deck's indoors end at an open stretch of deck (§5.3):
                    // drawn over her as she passes straight through it, as if through a door hidden
                    // in it (the user: deck 7's front, 2026-11-03; deck 8's ends, 2026-11-06).
                    this.plateCopy(o.x, o.y - this.deckPitch + 16, o.width, this.deckPitch - 16 + PLAYER.sink, DEPTH.player + 0.06);
                    // Some are locked (§6.1, `END_WALL_LOCKS`): the progression puts a barrier in them.
                    endWalls.push({ id: o.name, x0: o.x, x1: o.x + o.width, floor: o.y, lock: prop(o, 'lock', '') });
                    break;
                }

                case 'decor':
                    if (prop(o, 'kind') === 'windows') this.drawWindows(decorGfx, o);
                    if (prop(o, 'kind') === 'bridgewindows') this.drawBridgeWindows(decorGfx, o);
                    if (prop(o, 'kind') === 'spinnakerwindows') this.drawSpinnakerWindows(decorGfx, o);
                    if (prop(o, 'kind') === 'chess') this.drawChess(decorGfx, o);
                    if (prop(o, 'kind') === 'court') this.drawCourt(decorGfx, o);
                    if (prop(o, 'kind') === 'pergola') this.drawPergola(decorGfx, o);
                    if (prop(o, 'kind') === 'shuffle') this.drawShuffleboard(decorGfx, o);
                    if (prop(o, 'kind') === 'bunting') this.drawBunting(decorGfx, o);
                    if (prop(o, 'kind') === 'canopy') this.drawCanopy(o);
                    if (prop(o, 'kind') === 'suncover') this.drawSunCover(o, String(prop(o, 'posts', '')).split(',').map(Number));
                    if (prop(o, 'kind') === 'sauna') this.drawSauna(decorGfx, o);
                    if (prop(o, 'kind') === 'showerbox') this.drawShowerBox(o);
                    if (prop(o, 'kind') === 'gangway') this.drawGangway(decorGfx, o);
                    if (prop(o, 'kind') === 'crewdeck') this.drawCrewDeck(o);
                    if (prop(o, 'kind') === 'shelldoor') this.drawShellDoor(decorGfx, o);
                    if (prop(o, 'kind') === 'portico') this.drawPortico(decorGfx, o, prop(o, 'text', ''));
                    if (prop(o, 'kind') === 'dinewindows') this.drawDiningWindows(decorGfx, o, prop(o, 'xs', ''), prop(o, 'style', ''));
                    if (prop(o, 'kind') === 'pillars') this.drawPillars(decorGfx, o, prop(o, 'xs', ''), prop(o, 'style', ''));
                    if (prop(o, 'kind') === 'wavepanel') this.drawWavePanel(decorGfx, o);
                    if (prop(o, 'kind') === 'downlights') this.drawDownlights(decorGfx, o);
                    if (prop(o, 'kind') === 'resdesk') this.drawReservationsDesk(decorGfx, o, prop(o, 'text', ''));
                    if (prop(o, 'kind') === 'coffers') this.drawCoffers(decorGfx, o);
                    if (prop(o, 'kind') === 'lettering') this.drawLettering(o, prop(o, 'text', ''));
                    if (prop(o, 'kind') === 'stage') this.drawStage(decorGfx, o);
                    if (prop(o, 'kind') === 'doorway') this.drawDoorway(decorGfx, o, prop(o, 'text', ''), prop(o, 'hang', ''), prop(o, 'post', true));
                    if (prop(o, 'kind') === 'marquee') this.drawMarquee(decorGfx, o, prop(o, 'text', ''));
                    if (prop(o, 'kind') === 'burlpanel') this.drawBurlPanel(decorGfx, o);
                    if (prop(o, 'kind') === 'directory') this.drawDirectory(decorGfx, o);
                    if (prop(o, 'kind') === 'cove') this.drawCove(decorGfx, o);
                    if (prop(o, 'kind') === 'cabindoors') {
                        this.drawCabinDoors(decorGfx, o, prop(o, 'first', 0), prop(o, 'last', 0), prop(o, 'coreBefore', false), prop(o, 'coreAfter', false));
                    }
                    break;
            }
        }
        // The locks' readers, ropes and barriers, now that the flights, doors and walls are built.
        this.progress.build(endWalls);
    }

    // A piece of the ship's side drawn again (over her at a deck's end, over a wall she passes
    // behind): the side's own painted tiles there (step 11, tools/shell_paint.py), so its seams and
    // marks run on across it; plain plating where the side has no tile.
    plateTiles(box, x, y, w, h) {
        const ts = this.map.tilesets[0], tex = this.textures.get('tiles');
        let flat = null;
        for (let ty = Math.floor(y / 16) * 16; ty < y + h; ty += 16) {
            for (let tx = Math.floor(x / 16) * 16; tx < x + w; tx += 16) {
                const cx = Math.max(tx, x), cy = Math.max(ty, y);
                const cw = Math.min(tx + 16, x + w) - cx, ch = Math.min(ty + 16, y + h) - cy;
                const t = this.exteriorLayer.getTileAt(tx / 16, ty / 16);
                const at = t && t.index > 0 ? ts.getTileTextureCoordinates(t.index) : null;
                if (!at) {
                    if (!flat) box.add(flat = this.add.graphics());
                    flat.fillStyle(0xe8eaec, 1).fillRect(cx, cy, cw, ch);
                    continue;
                }
                const name = `t${t.index}`;
                if (!tex.has(name)) tex.add(name, 0, at.x, at.y, 16, 16);
                const img = this.add.image(tx, ty, 'tiles', name).setOrigin(0);
                if (cw < 16 || ch < 16) img.setCrop(cx - tx, cy - ty, cw, ch);
                box.add(img);
            }
        }
        return box;
    }

    // Something inside a deck drawn in front of her: from outside it is behind the ship's side, so
    // it is there only as far as its deck (or its room's own piece of the side) is cut open.
    behindShell(item, x, y) {
        const t = this.exteriorLayer.getTileAt(Math.floor(x / 16), Math.floor((y - 24) / 16));
        if (!t || !this.cutIds.has(t.index)) return;
        const deck = this.deckOfY(y);
        const room = this.shellRooms.find(r => r.deck === deck && x >= r.x0 && x < r.x1);
        (this.insideFronts ||= []).push({ key: room ? room.key : deck, item });
    }

    plateCopy(x, y, w, h, depth) {
        const box = this.plateTiles(this.add.container(0, 0).setDepth(depth), x, y, w, h);
        this.worldLayer.add(box);
        return box;
    }

    // The plating's seams across a white wall the game draws itself (the promenade's closed ends),
    // in line with the side's own beside it.
    plateSeams(g, x, y, w, h, colours = this.seams) {
        if (!this.seams) return;
        const { first, pitch } = this.seams, { seam, lit } = colours;
        const hex = c => Phaser.Display.Color.HexStringToColor(c).color;
        for (let sy = first + Math.ceil((y - first) / pitch) * pitch; sy < y + h; sy += pitch) {
            g.fillStyle(hex(seam), 1).fillRect(x, sy, w, 1);
            if (sy + 1 < y + h) g.fillStyle(hex(lit), 1).fillRect(x, sy + 1, w, 1);
        }
    }

    // A point along a flight, t from 0 (its foot) to 1 (its top). The atrium's curving staircase
    // (§5.3) sweeps: shallow at its foot, steeper toward the top; the cores' flights are straight.
    // --- Deck 6's promenade (§5.3) ------------------------------------------------------------
    // Outside the rooms along the ship's side, two decks tall. On it the deck is not cut away: she
    // walks in front of the white wall, the railing, columns and enclosed ends in front of her, the
    // lifeboats overhead. Each piece fades with the decks it stands across, like the shell.

    buildPromenade(o, prop) {
        const list = name => String(prop(o, name, '')).split(',').filter(Boolean);
        const floor = prop(o, 'floor', 0);
        const top7 = floor - this.deckPitch;        // deck 7's floor
        // The davits hang from deck 7's ceiling, the underside of deck 8's floor (the user, 2026-11-06).
        const hang = top7 - this.deckPitch + 16;
        const pr = this.promenade = {
            x0: o.x, x1: o.x + o.width, floor,
            doors: list('doors').map(Number),
        };
        // The side's own two rows under its floor's line drawn again over what lies on it (a tangerine's lowest
        // row reached into them, through the hull, the user, 2026-11-20: as her feet did, which are cut short
        // there); only while she is out on it (inside, the deck below may be open there).
        pr.edge = this.plateCopy(pr.x0, floor, pr.x1 - pr.x0, 2, DEPTH.exterior + 0.135).setVisible(false);
        const enclosed = list('enclosed').map(pair => pair.split(':').map(Number));
        // Each boat: its x, its picture, its two hooks' x in it and each one's eye's top below its top.
        const boats = list('boats').map(s => {
            const [x, key, h1, h2, e1, e2] = s.split(':');
            return { x: Number(x), key, hooks: [Number(h1), Number(h2)], eyes: [Number(e1), Number(e2)] };
        });
        const columns = list('columns').map(Number);
        const add = (deck, depth) => {
            const g = this.add.graphics().setDepth(depth);
            this.worldLayer.add(g);
            this.shellSlopes.push({ deck, gfx: g });
            return g;
        };
        const behind = add(6, DEPTH.exterior + 0.08);
        const front = add(6, DEPTH.player + 0.3);
        const high = add([6, 7], DEPTH.exterior + 0.06);
        // The walkway's railing: over her and what stands on the walkway, under the boats hanging outside it
        // (the user, 2026-11-21: "behind the boats, but cover the player and the box with the book").
        const walkRail = this.walkRail = add([6, 7], WALK_RAIL_DEPTH);
        const columnsGfx = add([6, 7], DEPTH.player + 0.32);

        // The deck underfoot, beige, and under the enclosed ends the wall in their shade.
        behind.fillStyle(0xab947a, 1).fillRect(pr.x0, floor - 3, pr.x1 - pr.x0, 3);
        for (const [a, b] of enclosed) behind.fillStyle(0xd5d9dc, 1).fillRect(a, floor - 128, b - a, 125);
        // The doors back in, on the wall.
        for (const x of pr.doors) {
            const door = this.add.image(x, floor, 'shipart', 'door-deck').setOrigin(0.5, 1).setDepth(DEPTH.exterior + 0.09);
            this.worldLayer.add(door);
            this.shellSlopes.push({ deck: 6, gfx: door });
        }

        // The enclosed ends: a white wall in front of her with large glassless openings.
        const OPEN_W = 80, PIER = 24, SILL = 30, LINTEL = 100;
        for (const [a, b] of enclosed) {
            front.fillStyle(0xe8eaec, 1).fillRect(a, floor - 128, b - a, 128 - LINTEL).fillRect(a, floor - SILL, b - a, SILL + PLAYER.sink);
            this.plateSeams(front, a, floor - 128, b - a, 128 - LINTEL);
            const n = Math.floor((b - a - PIER) / (OPEN_W + PIER));
            const pier = (b - a - n * OPEN_W) / (n + 1);
            // The promenade's ends are closed (back in only through the doors): a wall she runs into
            // at the end pier's inner edge, so she stops in the first opening, partly behind it.
            if (a === pr.x0) this.addRouteWall(a + pier + PROMENADE.endStop, -1, floor, 'promenade');
            if (b === pr.x1) this.addRouteWall(b - pier - PROMENADE.endStop, 1, floor, 'promenade');
            for (let i = 0; i <= n; i++) {
                front.fillStyle(0xe8eaec, 1).fillRect(a + i * (OPEN_W + pier), floor - LINTEL, pier, LINTEL - SILL);
                this.plateSeams(front, a + i * (OPEN_W + pier), floor - LINTEL, pier, LINTEL - SILL);
            }
            for (let i = 0; i < n; i++) {
                const x = a + pier + i * (OPEN_W + pier);
                front.fillStyle(0xc7dcd0, 1).fillRect(x, floor - LINTEL, OPEN_W, 2).fillRect(x, floor - SILL, OPEN_W, 2);
            }
        }

        // The open middle: a white railing with a wooden handrail, a life ring every few bays.
        const ra = enclosed[0][1], rb = enclosed[enclosed.length - 1][0];
        front.fillStyle(0xffffff, 1);
        for (const y of [floor - 9, floor - 19]) front.fillRect(ra, y, rb - ra, 2);
        for (let x = ra; x <= rb; x += 48) front.fillRect(x - 1, floor - 30, 3, 30 + PLAYER.sink);
        front.fillStyle(0xab947a, 1).fillRect(ra, floor - 31, rb - ra, 3);
        front.fillStyle(0x7f708a, 1).fillRect(ra, floor - 28, rb - ra, 1);
        // Life rings hung from the handrail between two posts, about every 12 m along the open
        // railing, clear of the doors; never on the enclosed ends' wall (the user, 2026-11-07).
        for (let rx = ra + 24 + 4 * 48; rx < rb - 48; rx += 12 * 48) {
            let x = rx;
            while (pr.doors.some(d => Math.abs(x - d) < 60)) x += 48;
            if (x > rb - 48) break;
            const ring = this.add.image(x, floor - 28, 'shipart', 'life-ring').setOrigin(0.5, 0).setDepth(DEPTH.player + 0.31);
            this.worldLayer.add(ring);
            this.shellSlopes.push({ deck: 6, gfx: ring });
        }

        // The opening is a shaded recess, two decks tall, its ends rounded (the user's side photo,
        // 2026-11-07): its back wall in shade, round portholes on it and a glazed bay.
        const recess = add([6, 7], DEPTH.exterior + 0.055);
        recess.fillStyle(0xc9ced3, 1).fillRoundedRect(pr.x0, hang, pr.x1 - pr.x0, floor - hang, 22);
        // Its plating as the side's (step 11), in the recess's shade: the same seams, panel joints
        // staggered between them, the shade deepest right under the overhang and under the walkway.
        const SHADED = { seam: '#bcc2c8', lit: '#cfd4d8' };
        this.plateSeams(recess, pr.x0 + 24, hang + 22, pr.x1 - pr.x0 - 48, floor - hang - 44, SHADED);
        const { first = 0, pitch = 72 } = this.seams || {};
        for (let y = first + Math.ceil((hang + 22 - first) / pitch) * pitch, row = 0; y < floor - 22; y += pitch, row++) {
            for (let x = pr.x0 + 150 + (row % 2) * 168; x < pr.x1 - 30; x += 336) {
                recess.fillStyle(0xbfc5cb, 1).fillRect(x, y + 2, 1, Math.min(pitch - 2, floor - 3 - y - 2));
            }
        }
        recess.fillStyle(0xb6bcc3, 1).fillRect(pr.x0 + 14, hang, pr.x1 - pr.x0 - 28, 4);
        recess.fillStyle(0xbdc3c9, 1).fillRect(pr.x0 + 10, hang + 4, pr.x1 - pr.x0 - 20, 7);
        recess.fillStyle(0xc3c9ce, 1).fillRect(pr.x0 + 6, hang + 11, pr.x1 - pr.x0 - 12, 5);
        recess.fillStyle(0xbdc3c9, 1).fillRect(pr.x0 + 2, top7 + 1, pr.x1 - pr.x0 - 4, 2);
        recess.fillStyle(0xc3c9ce, 1).fillRect(pr.x0 + 2, top7 + 3, pr.x1 - pr.x0 - 4, 2);
        for (const x of list('portholes').map(Number)) {
            recess.fillStyle(0x9babb2, 1).fillCircle(x, floor - 72, 12);
            recess.fillStyle(0x323353, 1).fillCircle(x, floor - 72, 10);
            recess.fillStyle(0x8fd3ff, 1).fillRect(x - 6, floor - 78, 3, 1);
        }
        for (const [a, b] of list('glazed').map(s => s.split(':').map(Number))) {
            recess.fillStyle(0x9babb2, 1).fillRect(a, hang + 16, b - a, floor - hang - 20);
            for (let x = a + 3; x < b - 3; x += 32) {
                const w = Math.min(28, b - 3 - x);
                recess.fillStyle(0x484a77, 1).fillRect(x, hang + 19, w, top7 - hang - 30);
                recess.fillStyle(0x484a77, 1).fillRect(x, top7 + 6, w, floor - top7 - 10);
                recess.fillStyle(0x8fd3ff, 0.5).fillRect(x + 3, hang + 22, 2, top7 - hang - 40);
            }
        }
        // White columns from the deck up to deck 8's overhang; between them, behind the boats, the
        // white walkway at deck 7's floor (the user's side photo, 2026-11-07). Each boat hangs high,
        // under the overhang, from a short davit arm over each of its hooks, on its cables. All
        // washed out a little, background like the boats (the user, 2026-11-06).
        walkRail.fillStyle(0xf4f4f4, 1).fillRect(pr.x0, top7 - 6, pr.x1 - pr.x0, 6);
        walkRail.fillStyle(0xc7dcd0, 1).fillRect(pr.x0, top7, pr.x1 - pr.x0, 1);
        walkRail.fillStyle(0xf4f4f4, 1).fillRect(pr.x0, top7 - 30, pr.x1 - pr.x0, 2);
        for (let x = pr.x0 + 24; x < pr.x1; x += 48) walkRail.fillRect(x, top7 - 30, 2, 24);
        // A column within an enclosed end stands behind its wall, seen through its openings and over
        // it (the user, 2026-11-07).
        const behindWall = add([6, 7], DEPTH.player + 0.29);
        for (const x of columns) {
            const g = enclosed.some(([a, b]) => x > a && x < b) ? behindWall : columnsGfx;
            g.fillStyle(0xf7f8f8, 1).fillRect(x - 5, hang, 10, floor - hang + PLAYER.sink);
            g.fillStyle(0xd3e1da, 1).fillRect(x + 2, hang, 3, floor - hang);
            g.fillStyle(0xe8eaec, 1).fillRect(x - 7, floor - 4, 14, 4);
        }
        const drop = 8;                              // the boats' tops under the overhang, their keels clear of the enclosed ends' walls
        for (const { x, key, hooks, eyes } of boats) {
            hooks.forEach((h, i) => {
                const hook = x + h;
                high.fillStyle(0xf7f8f8, 1).fillRect(hook - 14, hang, 28, 6);
                high.fillStyle(0xd3e1da, 1).fillRect(hook - 14, hang + 5, 28, 1);
                // (Steel wire rope, as on the drill's winch: src/wire.js.)
                wire(high, hook, hang + 6, hang + drop + eyes[i] + 1);
            });
            // (In front of her on the walkway, as they hang outside its railing: the user, 2026-11-21, "She has to
            // move behind the boats, obscured by them". The drill's boat is so already: src/world/outside.js.)
            const boat = this.add.image(x, hang + drop, key).setOrigin(0).setDepth(BOAT_DEPTH);
            (this.boatPics ??= []).push(boat);
            this.worldLayer.add(boat);
            this.shellSlopes.push({ deck: [6, 7], gfx: boat });
        }
    }

    // An invisible wall at one end of the promenade or of cabin 8206, there only while she is on that
    // route. `x` is where her middle stops; `side` is -1 at the fore end, 1 at the aft end.
    addRouteWall(x, side, floor, route) {
        const w = 32;
        const edge = x + side * PLAYER.bodyWidth / 2;
        const zone = this.add.zone(edge + side * w / 2, floor - this.deckPitch / 2, w, this.deckPitch);
        this.physics.add.existing(zone, true);
        zone.route = route;
        (this.routeWalls ||= []).push(zone);
    }

    // The railing, leaning, its foot at (x, y): each row up from its foot shifted `k` px per px of
    // height toward `dir` (1 aft, at a deck's forward end; -1 forward, at its aft end). Its texture
    // is made once per slope.
    leaningRailing(x, y, k, dir) {
        const key = `railing-lean-${dir}-${k.toFixed(2)}`;
        const frame = this.textures.getFrame('shipart', 'railing-bg');
        const { width: w, height: h } = frame;
        const lean = Math.ceil(k * (h - 1));
        if (!this.textures.exists(key)) {
            const canvas = this.textures.createCanvas(key, w + lean, h);
            const ctx = canvas.getContext();
            for (let row = 0; row < h; row++) {
                const shift = Math.round(k * (h - 1 - row));
                ctx.drawImage(frame.source.image, frame.cutX, frame.cutY + row, w, 1, dir < 0 ? lean - shift : shift, row, w, 1);
            }
            canvas.refresh();
        }
        // The foot's middle is w/2 in from the foot's own side of the texture.
        const footX = dir < 0 ? lean + w / 2 : w / 2;
        return this.add.image(x, y, key).setOrigin(footX / (w + lean), 1);
    }

    // --- Cabin 8206 (§5.3) --------------------------------------------------------------------
    // The user's own cabin on the cruise, on deck 8: its door stands open, a brass number beside it
    // and the steward's linen cart. E at the door and she is inside: the room as in her photo shows
    // where the corridor was, the deck still cut open, everything round it dimmed almost to black
    // (the user, 2026-11-06: as the linen room; it was first cut into the ship's side).

    buildCabin(o, prop) {
        const x0 = o.x - CABIN.doorX;
        const c = this.cabin = { door: o.x, floor: o.y, number: prop(o, 'number', 0) };
        const door = this.add.image(o.x, o.y, 'cabin-door-open').setOrigin(0.5, 1).setDepth(DEPTH.props);
        // Through the open door, the window at the far wall shows the live sea too (the user).
        const [dx, dy, dw, dh] = CABIN.doorWindow;
        this.windowView.mask.fillRect(o.x - door.width / 2 + dx, o.y - door.height + dy, dw, dh);
        const plate = this.add.text(o.x + 21, o.y - 50, String(c.number), {
            fontFamily: 'Verdana, sans-serif', fontSize: '6px', fontStyle: 'bold', color: '#45293f',
            backgroundColor: '#d9a43b', padding: { left: 2, right: 2, top: 1, bottom: 1 }, resolution: 4,
        }).setOrigin(0, 0.5).setDepth(DEPTH.props);
        const cart = this.add.image(o.x - 36, o.y, 'shipart', 'towel-trolley-bg').setOrigin(0.5, 1).setDepth(DEPTH.decor + 0.115);
        c.room = this.add.image(x0, o.y - CABIN.height, 'cabin-8206').setOrigin(0).setDepth(DEPTH.exterior + 0.12).setVisible(false);
        const dim = this.roomDim(c.room);
        this.worldLayer.add([door, plate, cart, dim, c.room]);
        // Its picture window's glass is clear in the drawing: the live sea and sky behind it.
        const [wx, wy, ww, wh] = CABIN.window;
        this.cabinView = this.addWindowView(DEPTH.exterior + 0.115);
        this.cabinView.mask.fillRect(x0 + wx, o.y - CABIN.height + wy, ww, wh);
        this.cabinView.view.setVisible(false);
        c.view = this.cabinView.view;
        // Her towel, once she has hung it on the shower door's handle on her way out (the user,
        // 2026-11-08); it stays there until her next shower.
        const [tx, ty] = CABIN.towel;
        c.towel = this.add.image(x0 + tx, o.y - CABIN.height + ty, 'cabin-shower-towel').setOrigin(0)
            .setDepth(DEPTH.exterior + 0.125).setVisible(false);
        this.worldLayer.add(c.towel);
        this.rooms.push({ route: 'cabin', door: o.x, floor: o.y, room: c.room, dim, inDeck: true });
        this.addRouteWall(x0 + CABIN.stop, -1, o.y, 'cabin');
        this.addRouteWall(x0 + CABIN.width - CABIN.stop, 1, o.y, 'cabin');
        // The bed holds her from above, like a side walk (the user, 2026-11-06: she can jump on it).
        const [a, b] = CABIN.bed;
        c.bed = this.add.zone(x0 + (a + b) / 2, o.y - CABIN.bedTop + 4, b - a, 8);
        this.physics.add.existing(c.bed, true);
    }

    // Bumbot at one of his spots (§4), doing `activity`; he runs off toward `escape` (1 aft, -1
    // forward). One in a room behind a door (the linen room's) is drawn over that room and shows
    // only there; he lies `lift` px up (on the towels), and gets away at `exitX`.
    addCat(name, x, y, activity, escape, { route = 'inside', lift = 0, exitX = null } = {}) {
        const depth = route === 'inside' ? DEPTH.props : DEPTH.exterior + 0.13;
        const sprite = this.add.sprite(x, y - lift, 'bumbot').setOrigin(0.5, 1).setDepth(depth);
        // (Asleep he breathes in his clip's own frames since his sprites were made again, 2026-11-24: it was one still
        // stretched by a tween. Sat down, he goes on sitting: his tail, an ear, a blink.)
        sprite.play(`bumbot-${activity}`);
        if (activity === 'sit') sprite.anims.chain('bumbot-sat');
        // (Fishing at a rim, his paw goes down past his floor: that clip's frames keep `BUMBOT.under` px under it.)
        if (activity === 'fish') sprite.y += BUMBOT.under;
        // (Eating off the floor: his small bites as his head goes down, each round of the clip; part 5.)
        if (activity === 'eat') sprite.on('animationupdate', (a, f) => { if (a.key === 'bumbot-eat' && f.index === 1 && sprite.visible) sfx.at(sprite.x, sprite.y).nom(); });
        if (route !== 'inside') sprite.setVisible(false);
        this.worldLayer.add(sprite);
        const cat = { name, sprite, escape, gone: false, away: false, route, floor: y, exitX, activity };
        this.cats.push(cat);
        return cat;
    }

    // --- The linen room (§4, §5.3) --------------------------------------------------------------
    // Housekeeping's linen room on deck 9, off the cabin corridor (the user, 2026-11-06: she can go
    // in): a regular crew door, shut (the user, 2026-11-24: it was held open, the room seen through it), pulsing when she is
    // at it as every door she can use (src/highlight.js), a plate beside it. E at the door and she is inside: the room
    // shows where the corridor was, the deck still cut open, everything round it dimmed almost to
    // black. Racks of folded towels, a heap of them on the floor, a vent. (Bumbot slept there until
    // his spots were taken out, 2026-11-07, §4.)

    buildLinenRoom(o, prop) {
        const x0 = o.x - LINEN.doorX;
        const door = this.add.image(o.x, o.y, 'shipart', 'door-crew').setOrigin(0.5, 1).setDepth(DEPTH.props);
        const plate = sign(this, o.x + 20, o.y - 50, 'LINEN', 'steel').setOrigin(0, 0.5).setDepth(DEPTH.props);
        const room = this.add.image(x0, o.y - LINEN.height, 'linen-room').setOrigin(0).setDepth(DEPTH.exterior + 0.12).setVisible(false);
        const dim = this.roomDim(room);
        this.worldLayer.add([door, plate, dim, room]);
        // (`also`: the room stays in view from the shaft that opens off it, one picture with it: src/world/world.js.)
        const linen = { route: 'linen', also: 'duct', door: o.x, floor: o.y, room, dim, inDeck: true };
        this.rooms.push(linen);
        // Locked until she has the Housekeeping card (§6.1.5): the same shut door either way, so nothing is shown for it.
        const shut = { setVisible: () => shut };
        this.progress.roomDoor(linen, prop(o, 'lock', ''), shut, o.x, o.y);
        // (Forward, the end of the shaft's mouth is her wall, at every height: standing she is too tall to go into it or
        // under it. With the room's own stop, 6 px further forward, she ran off the parked cart's end and dropped into
        // the gap under the mouth: the user, 2026-11-23. On hands and knees on the cart she goes in: `updateDuct`.)
        this.addRouteWall(x0 + LINEN.mouth + PLAYER.bodyWidth / 2, -1, o.y, 'linen');
        this.addRouteWall(x0 + LINEN.width - LINEN.stop, 1, o.y, 'linen');
    }

    // A room door's plate toned down toward the background (the user, 2026-11-24: "the plates same background'ish tone as
    // the doors"): the doors she can use are washed at rest like the background doors beside them (src/highlight.js's
    // `restDoors`), and their plates stood out at full contrast. Each plate named in `WASHED_PLATES` gets its own picture
    // washed by `PLATE_WASH`, every pixel toward the corridor wall (the doors' own sum), as a texture of its own; nothing
    // pulses with it. Once, after the doors' washes are worked out.
    washPlates() {
        const seen = new Set();
        for (const o of [...this.worldLayer.list, ...this.children.list]) {
            const m = /^sign:[a-z]+:(.*)$/.exec(String(o.texture?.key ?? ''));
            if (!m || seen.has(o) || !WASHED_PLATES.includes(m[1])) continue;
            seen.add(o);
            const key = `${o.texture.key}:w${Math.round(PLATE_WASH * 100)}`;
            if (!this.textures.exists(key)) {
                const src = o.texture.getSourceImage(), tex = this.textures.createCanvas(key, src.width, src.height), ctx = tex.getContext();
                ctx.drawImage(src, 0, 0);
                ctx.globalCompositeOperation = 'source-atop';
                ctx.fillStyle = `rgba(${PLATE_WALL.join(',')},${PLATE_WASH})`;
                ctx.fillRect(0, 0, src.width, src.height);
                tex.refresh();
            }
            o.setTexture(key);
        }
    }

    // --- The Chapel (§5.3) ---------------------------------------------------------------------
    // Off deck 12's forward lobby (the user, 2026-11-07: a room behind a door, like the linen room):
    // its door held open, a plate beside it. E at the door and she is inside: the chapel, from the
    // user's photo, shows where the lobby was, everything round it dimmed almost to black.

    buildChapel(o) {
        const x0 = o.x - CHAPEL.doorX;
        const door = this.add.image(o.x, o.y, 'chapel-door-open').setOrigin(0.5, 1).setDepth(DEPTH.props);
        const plate = this.add.text(o.x + 21, o.y - 50, 'CHAPEL', {
            fontFamily: 'Verdana, sans-serif', fontSize: '5px', fontStyle: 'bold', color: '#45293f',
            backgroundColor: '#d9a43b', padding: { left: 2, right: 2, top: 1, bottom: 1 }, resolution: 4,
        }).setOrigin(0, 0.5).setDepth(DEPTH.props);
        const room = this.add.image(x0, o.y - CHAPEL.height, 'chapel-room').setOrigin(0).setDepth(DEPTH.exterior + 0.12).setVisible(false);
        const dim = this.roomDim(room);
        this.worldLayer.add([door, plate, dim, room]);
        this.rooms.push({ route: 'chapel', door: o.x, floor: o.y, room, dim, inDeck: true });
        this.addRouteWall(x0 + CHAPEL.stop, -1, o.y, 'chapel');
        this.addRouteWall(x0 + CHAPEL.width - CHAPEL.stop, 1, o.y, 'chapel');
    }

    // --- Walls across a deck, with a door (§5.3) -----------------------------------------------
    // A wall across the deck, its door seen from the side: shut, a slab in the doorway; E opens it,
    // swung flat against the wall, seen face on. The door shuts once she is away. At the back of a
    // part of the deck with its own piece of the ship's side (the bridge on deck 10, the spa on
    // deck 11: `key`), from outside it is out of sight and inside it only it is cut open (the user,
    // 2026-11-06). The sauna's two ends are such walls too, cedar, with glass doors.

    buildBulkhead(o, x0, key, text, sub, leaf, colour, { width = BULKHEAD.width, swing = -1, wall = '', frame = '', lock = '', signUp = 0 } = {}) {
        const x = o.x, floor = o.y, w = width;
        const ceiling = floor - this.deckPitch + 16;
        const head = floor - DOOR.height - 2;
        const glass = leaf === 'glass';
        // A glass door's frame and handle: cedar (the sauna's), or steel (between the ship's parts).
        const steel = frame === 'steel';
        const rim = steel ? 0x9babb2 : 0x7a4528, grip = steel ? 0x625565 : 0x46291f;
        const g = this.add.graphics().setDepth(DEPTH.props);
        const tone = wall ? Phaser.Display.Color.HexStringToColor(wall).color : 0x9babb2;
        g.fillStyle(tone, 1).fillRect(x - w / 2, ceiling, w, head - ceiling);
        if (!wall) g.fillStyle(0xc7dcd0, 1).fillRect(x - w / 2 + 2, ceiling, 2, head - ceiling);
        g.fillStyle(wall ? 0x46291f : 0x625565, 1).fillRect(x - w / 2, head, w, 2);
        // Shut: the door edge on, its handle sticking out on each side: white steel, or glass. A
        // one-way glass door: its push bar's end and its closer on its free side, nothing on the
        // other (generated; the user, 2026-11-18: "the door profile should also differ").
        const oneway = glass && steel && lock.startsWith('oneway');
        const free = oneway ? Number(lock.split(':')[1]) : 0;
        const shut = oneway
            ? this.add.image(free < 0 ? x - 10 : x - 2, floor, 'door-glass-oneway-edge').setOrigin(0, 1).setFlipX(free > 0).setDepth(DEPTH.props)
            : this.add.graphics().setDepth(DEPTH.props);
        if (oneway) {
            // (Its picture: assets/source/ship/pushbar/.)
        } else if (glass) {
            shut.fillStyle(rim, 1).fillRect(x - 2, head + 2, 4, floor - head - 2);
            shut.fillStyle(0xbfe6f5, 1).fillRect(x - 1, head + 4, 2, floor - head - 8);
            shut.fillStyle(rim, 1).fillRect(x - 5, floor - 36, 10, 3);
        } else {
            shut.fillStyle(0x9babb2, 1).fillRect(x - 3, head + 2, 6, floor - head - 2);
            shut.fillStyle(0xffffff, 1).fillRect(x - 2, head + 2, 4, floor - head - 2);
            shut.fillStyle(0x625565, 1).fillRect(x - 7, floor - 36, 14, 2);
        }
        // Open: swung back against the wall (on the room's side), seen face on.
        const edge = x + swing * w / 2;
        let open;
        // (A one-way door: its push bar across it, generated from this very leaf, the rest of it the
        // same; the user, 2026-11-18. The design's "fire-exit doors with a push bar on one side only".)
        if (oneway) {
            const lx = swing < 0 ? edge - 28 : edge;
            open = this.add.image(lx, floor, 'door-glass-pushbar').setOrigin(0, 1).setDepth(DEPTH.decor + 0.2).setVisible(false);
        } else if (glass) {
            // A glass door in its frame, a handle.
            open = this.add.graphics().setDepth(DEPTH.decor + 0.2).setVisible(false);
            const lx = swing < 0 ? edge - 28 : edge;
            open.fillStyle(rim, 1).fillRect(lx, head + 2, 28, floor - head - 2);
            open.fillStyle(0xbfe6f5, 0.85).fillRect(lx + 3, head + 5, 22, floor - head - 10);
            open.fillStyle(0xffffff, 0.6).fillRect(lx + 6, head + 8, 2, 30);
            open.fillStyle(grip, 1).fillRect(swing < 0 ? lx + 3 : lx + 22, floor - 40, 3, 10);
        } else {
            open = this.add.image(edge, floor, 'shipart', leaf).setOrigin(swing < 0 ? 1 : 0, 1).setDepth(DEPTH.decor + 0.2).setVisible(false);
        }
        const parts = [g, shut, open];
        // Its sign on the outer side.
        if (text) {
            parts.push(this.add.text(x + w / 2 + 6, floor - 52 - signUp, sub ? `${text}\n${sub}` : text, {
                fontFamily: 'Verdana, sans-serif', fontSize: '5px', fontStyle: 'bold', color: '#ffffff', align: 'center',
                backgroundColor: colour, padding: { left: 2, right: 2, top: 1, bottom: 1 }, resolution: 4,
            }).setOrigin(0, 0.5).setDepth(DEPTH.props));
        }
        const zone = this.add.zone(x, floor - this.deckPitch / 2, w, this.deckPitch);
        this.physics.add.existing(zone, true);
        // A wall where a room's piece of shell meets the deck's: drawn over the shell, so it shows
        // from either side, while either is cut open.
        if (key) {
            g.setDepth(DEPTH.exterior + 0.02);
            shut.setDepth(DEPTH.exterior + 0.02);
        }
        this.worldLayer.add(parts);
        const deck = key.split(':')[0];
        const b = { id: o.name, x, w, x0, floor, key, deck, lock, open: false, shut, wall: g, openDoor: open, zone };
        this.bulkheads.push(b);
        // (A one-way door she has come through from its free side stays propped open for good: its
        // plain side has nothing to open it by; the user, 2026-11-18.)
        if (oneway && this.save.opened.includes(o.name)) this.propOpen(b);
    }

    propOpen(b) {
        b.ajar = true;
        this.setBulkheadOpen(b, true);
    }

    // E at a wall's shut door: it opens.
    useBulkheadDoor() {
        const p = this.player;
        const b = this.bulkheads.find(b => !b.open && Math.abs(p.y - b.floor) <= 4 && Math.abs(p.x - b.x) <= 24);
        if (!b || this.route !== 'inside') return false;
        // Its lock (§6.1): a card, a one-way door, a rope until something has happened.
        const res = this.progress.doorPasses(b, p.x < b.x ? -1 : 1);
        if (!res.ok) {
            this.showLock(res);
            return true;
        }
        this.setBulkheadOpen(b, true);
        if (res.through && b.lock.startsWith('oneway')) this.propOpen(b);
        sfx.doorHeavy();
        return true;
    }

    setBulkheadOpen(b, open) {
        b.open = open;
        b.shut.setVisible(!open);
        b.openDoor.setVisible(open);
    }

    // The doors across a deck, and its walls, stop whatever moves along it, not only her (the user,
    // 2026-11-17; docs/plan-three-uses.md §1.8). A thing stops short of a door's face, shut or open
    // (one she holds open would shut on it), never on top of it; a person may open a door with no
    // lock, go through, and it shuts behind them (`holdDoor`, people.js `walk`); a locked one (a
    // card, one way, a rope, the story's) turns them back, since one held open would let her by.
    // `half`: px from the thing's middle to its front, the way it goes.

    // How far a thing at x on the floor y can go toward `to`: there, or short of the first door or
    // wall on the way (never back from where it is).
    stopShort(x, to, y, half = 0, gap = 2) {
        const dir = Math.sign(to - x);
        if (!dir) return to;
        const cut = stop => { if ((to - stop) * dir > 0) to = (stop - x) * dir > 0 ? stop : x; };
        for (const b of this.bulkheads) {
            if (Math.abs(b.floor - y) <= 4 && (b.x - x) * dir > 0) cut(b.x - dir * (b.w / 2 + half + gap));
        }
        // A wall: the solid layer at a body's height over the floor.
        const T = 16, first = Math.floor((x + dir * half) / T) + dir, last = Math.floor((to + dir * half) / T);
        for (let c = first; (last - c) * dir >= 0; c += dir) {
            if (!(this.solidLayer.getTileAtWorldXY(c * T + T / 2, y - 20)?.index > 0)) continue;
            cut((dir > 0 ? c * T : (c + 1) * T) - dir * (half + gap));
            break;
        }
        return to;
    }

    // ... and short of a balcony's partition on her route (which only she goes round):
    // what runs off her along the balconies stops at the next one (the gull on her head, 20; her
    // tiptoe away from an occupied balcony, 24). One she already stands by stops it where it is.
    partitionShort(x, to, y, half = 0, gap = 2) {
        const dir = Math.sign(to - x);
        if (!dir) return to;
        if (this.route !== OUTSIDE) return to;
        for (const g of this.world.data.outside.partitions ?? []) {
            if (Math.abs(g.y - y) > 6 || (g.x - x) * dir <= 0) continue;
            const stop = g.x - dir * (3 + half + gap);
            const at = (stop - x) * dir > 0 ? stop : x;
            if ((to - at) * dir > 0) to = at;
        }
        return to;
    }

    // A span lo..hi round x on the floor y, cut short by the doors and walls either side.
    spanOn(x, lo, hi, y, half = 0, gap = 2) {
        return { lo: this.stopShort(x, lo, y, half, gap), hi: this.stopShort(x, hi, y, half, gap) };
    }

    // The door across the floor y that a thing at x going `dir` reaches within `reach` px of its
    // front, or null.
    doorAhead(x, dir, y, half = 0, reach = 12) {
        let best = null, near = Infinity;
        for (const b of this.bulkheads) {
            const gap = (b.x - x) * dir - b.w / 2 - half;
            if (Math.abs(b.floor - y) <= 4 && (b.x - x) * dir > 0 && gap <= reach && gap < near) {
                best = b;
                near = gap;
            }
        }
        return best;
    }

    // A person may open it: no lock.
    mayOpen(b) {
        return !b.lock;
    }

    // A person opens a door and holds it while going through (`who`: anything to know them by); it
    // shuts once no one holds it and she is away (`updateBulkhead`).
    holdDoor(b, who) {
        (b.held ??= new Set()).add(who);
        if (b.open) return false;
        this.setBulkheadOpen(b, true);
        sfx.at(b.x, b.floor).doorHeavy();
        return true;
    }

    letGoDoor(b, who) {
        b.held?.delete(who);
    }

    // Each frame: a door shuts behind her once she is away from it; a wall shows while its deck is
    // cut open on either side of it.
    updateBulkhead() {
        const p = this.player;
        for (const b of this.bulkheads) {
            const onDeck = this.route === 'inside' && p.y <= b.floor + 4 && p.y > b.floor - this.deckPitch;
            // (One left ajar stays so: the Library's aft door, after Bumbot.)
            // (Nor one a person is going through: `holdDoor`.)
            if (b.open && !b.ajar && !b.held?.size && !(onDeck && Math.abs(p.x - b.x) < BULKHEAD.shutAway)) this.setBulkheadOpen(b, false);
            if (!b.key) continue;
            const open = 1 - Math.min(this.shellAlpha[b.deck] ?? 1, this.shellAlpha[b.key] ?? 1);
            b.wall.setAlpha(open);
            b.shut.setAlpha(open);
        }
    }

    // The world round a room she is in (cabin 8206, the linen room), dimmed almost to black: four
    // dark panels framing it.
    // (Over everything she is under, the balconies' railings and partitions on the decks round the room included: under
    // them, they showed undimmed over it, the user, 2026-11-24, at the linen room. It frames the room, so neither the room
    // nor she is under it.)
    roomDim(room) {
        const dim = this.add.graphics().setDepth(DEPTH.player + 0.35).setVisible(false);
        const far = 4000, { x, y, width, height } = room;
        dim.fillStyle(0x0d0b14, ROOM_DIM);
        dim.fillRect(x - far, y - far, width + 2 * far, far);
        dim.fillRect(x - far, y + height, width + 2 * far, far);
        dim.fillRect(x - far, y, far, height);
        dim.fillRect(x + width, y, far, height);
        return dim;
    }

    // A checkpoint (§5.5): a door with its lamp, on a deck or on a balcony. `door`: its picture, the white crew door
    // or a place's own (the theatre's padded ones, the panelled rooms' wood ones: plan-the-rest §7e), lit as its
    // `-ajar` twin; `door: null`: at a door that is drawn already (a room's, cabin 8206's, a trunk's): the lamp only.
    addCheckpoint(id, x, y, { route = 'inside', door = 'door-crew', rise = LAMP_RISE } = {}) {
        const depth = route === 'inside' ? DEPTH.props : DEPTH.exterior + 0.1;
        const items = [];
        const sprite = door ? this.add.image(x, y, 'shipart', door).setOrigin(0.5, 1).setDepth(depth) : null;
        if (sprite) items.push(sprite);
        const glow = this.add.image(x, y - rise, 'glow').setDepth(depth).setVisible(false);
        const lamp = this.add.image(x, y - rise, 'lamp').setDepth(depth);
        items.push(glow, lamp);
        this.worldLayer.add(items);
        const cp = { id, x, y, route, door: sprite, frame: door, rise, lamp, glow, active: false, items };
        this.checkpoints.push(cp);
        if (this.save.activated.includes(id)) this.lightCheckpoint(cp, false);
        return cp;
    }

    // A tangerine resting at (x, y), unless she has it already; one on another route (the cabin's)
    // is drawn over that route's room and shows only there.
    addTangerine(id, x, y, route = 'inside') {
        if (this.save.collected.includes(id)) return;
        // (In a pile, a higher one is behind a lower one: the crew cabin's bowl.)
        const depth = (route === 'inside' ? DEPTH.props : DEPTH.exterior + 0.13) + y * 1e-7;
        const sprite = this.add.image(x, y, 'tangerine').setOrigin(0.5, 1).setDepth(depth);
        const glint = this.add.image(sprite.x - 2, sprite.y - 6, 'dot').setDepth(depth).setAlpha(0);
        this.tweens.add({ targets: glint, alpha: 1, duration: 120, yoyo: true, repeat: -1, repeatDelay: 2400, delay: Phaser.Math.Between(0, 2000) });
        this.worldLayer.add([sprite, glint]);
        const t = { id, sprite, glint, route };
        this.tangerines.push(t);
        return t;
    }

    // A door at her feet to another route: the promenade's (deck 6), or a room's (cabin 8206, the
    // linen room).
    routeDoorAt(x, y) {
        const door = this.promenadeDoorAt(x, y);
        if (door !== null && (this.route === 'inside' || this.route === 'promenade')) {
            return { x: door, to: this.route === 'promenade' ? 'inside' : 'promenade' };
        }
        if (this.route === 'duct') return null;
        for (const r of this.rooms) {
            // A room of the plan's (src/world/): each of its doors leads somewhere of its own.
            if (r.doors) {
                if (r.hidden) continue;
                for (const d of r.doors) {
                    if (this.route === r.route && Math.abs(y - r.floor) <= 4 && Math.abs(x - d.x) < 16) {
                        return { x: d.outX, y: d.outY, to: d.outRoute, room: r, d, leaving: true };
                    }
                    // (A boat's roof hatch takes her in from anywhere under its width: `ROOF.reach`.)
                    if (this.route === d.outRoute && Math.abs(y - d.outY) <= 4 && Math.abs(x - d.outX) < (d.kind === 'roof' ? ROOF.reach : 16)) {
                        return { x: d.x, y: r.floor, to: r.route, room: r, d };
                    }
                }
                continue;
            }
            if ((this.route === 'inside' || this.route === r.route) && Math.abs(y - r.floor) <= 4 && Math.abs(x - r.door) < 16) {
                return { x: r.door, to: this.route === r.route ? 'inside' : r.route, room: r };
            }
        }
        return null;
    }

    promenadeDoorAt(x, y) {
        const pr = this.promenade;
        if (!pr || Math.abs(y - pr.floor) > 4) return null;
        return pr.doors.find(d => Math.abs(x - d) < 16) ?? null;
    }

    // E at a promenade door or a room's: a quick fade, and she is on the other side of it.
    useRouteDoor() {
        const p = this.player;
        const door = this.routeDoorAt(p.x, p.y);
        if (door === null) return false;
        if (this.towel && this.route === 'cabin') return this.hangTowel();
        // A room whose crew door needs a card (the linen room), going in; a door of the plan's rooms
        // has its own lock (src/world/).
        let lock = { ok: true };
        if (door.d) lock = this.world.doorPasses(door);
        else if (door.room?.lockSpec && door.to !== 'inside') lock = this.progress.passes(door.room.lockSpec, 0, '');
        if (!lock.ok) {
            if (!lock.quiet) this.showLock(lock);
            return true;
        }
        // (A boat's roof hatch: she climbs up into it, or out of it and down behind the boat.)
        if (door.d?.kind === 'roof') return this.textures.exists('mantle-front') && this.roofClimb(door);
        // (A crew door that her card opens: the reader's beep first.)
        if (door.room?.lockSpec?.kind === 'card' && door.to !== 'inside') sfx.beep();
        sfx.door();
        this.travel(door.x, door.y ?? p.y, door.to);
        return true;
    }

    // The lifeboat's roof hatch (the user, 2026-11-21; its frames approved together as one GIF): going in (E behind the
    // boat at the hatch) she pulls herself up over the hatch's far rim facing us, her hands held on it (`mantle-front`, her
    // own character), stands on the roof, turns side-on and her back to us, steps into the opening and sinks in with her
    // hands on its rim (her own frames), cut by its near lip; the fade, and she is on the top of the ladder inside, for
    // the player to climb down. Out: up that ladder past its top (`roofOut`), no E, and the same frames the other way.
    // Her body waits on the walkway, the camera with it: what shows is a picture of her (`roofPic`), between the
    // hatch's back and its lip, cut where the frame says.
    roofClimb(door) {
        if (door.leaving) return false;
        const p = this.player, d = door.d;
        this.roofHold();
        const pic = this.roofPic();
        this.roofRun(pic, this.roofSteps(d), () => {
            pic.destroy();
            sfx.door();
            this.travel(d.x, door.y, door.to, () => {
                // On the top of the ladder inside, for the player to climb down.
                const L = this.world.roofLadderOf(door.room);
                p.setVisible(true);
                this.enterLadder(L.x, L.y1, L.y0, L.out, L.ceil);
                p.y = L.start;
                this.updateLadder({}, 0);
                this.world.onLadder = L;
            });
        });
        return true;
    }

    // Out of the lifeboat (up its ladder past the top): the fade, then the climb's frames the other way, out of the
    // hatch, turning to face us on the roof, and down the boat's far side; then she is on the walkway behind the boat.
    roofOut(room, d) {
        const p = this.player;
        this.mode = 'scripted';
        // (Hidden before the fade: `travel` stands her up, and her standing frame showed a moment over the boat's inside,
        // in the air: the user, 2026-11-21, "a flashing frame showing her standing in the air in profile".)
        p.setVisible(false);
        p.setCrop();
        sfx.door();
        this.travel(d.outX, d.outY, d.outRoute, () => {
            this.roofHold();
            const pic = this.roofPic();
            this.roofRun(pic, this.roofSteps(d).reverse(), () => {
                pic.destroy();
                p.body.enable = true;
                p.body.reset(d.outX, d.outY);
                p.setVisible(true);
                this.pose('stand');
                this.mode = 'play';
            });
        });
    }

    // The lifeboat's hatch glows faintly while she stands where E takes her in (behind the boat, under it), fading in and
    // out (the user, 2026-11-21: "add a faint glow from inside the hatch").
    updateRoofGlow(dt) {
        const p = this.player;
        for (const g of this.world.roofGlows ?? []) {
            const here = this.route === g.d.outRoute && this.mode === 'play' && Math.abs(p.x - g.d.outX) < ROOF.reach && Math.abs(p.y - g.d.outY) <= 4;
            g.shown = approach(g.shown, here ? 1 : 0, dt * 3);
            g.glow.setVisible(g.shown > 0).setAlpha(g.shown);
        }
    }

    // Her body held where it is, hidden, while a picture of her climbs.
    roofHold() {
        const p = this.player;
        this.mode = 'scripted';
        this.script = null;
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.setVisible(false);
    }

    roofPic() {
        const s = this.add.image(0, 0, 'her', this.herFrames.front).setOrigin(0).setDepth(DEPTH.player + 0.065).setVisible(false);
        this.worldLayer.add(s);
        return s;
    }

    // The climb in, frame by frame: [ms, texture, frame, its top left's x and y, the row it is cut at] in the world,
    // from the hatch's middle over the walkway's floor (`d.outX`, `d.outY`): the hatch's far rim `ROOF.far` px up, its
    // near lip `ROOF.lip` (tools/build_hatch.py). Her own sheet's cells are 84 px, her middle at 42, her feet on row 83.
    roofSteps(d) {
        const mf = this.cache.json.get('mantle-front-meta'), F = this.herFrames, x = d.outX;
        const far = d.outY - ROOF.far, lip = d.outY - ROOF.lip, cell = PLAYER.cell, mid = cell / 2;
        const steps = [];
        // Up over the far rim, her hands on it (each frame's hands' lowest row a px over it), cut at it.
        mf.hands.forEach((h, i) => steps.push([ROOF.frameMs, 'mantle-front', i, x - mf.x, far - 1 - h, far]));
        // On the roof behind the opening, her feet on the far rim: facing us, side-on, her back to us.
        for (const [f, ms, down] of [[F.front, ROOF.frontMs, 0], [F.stand, ROOF.turnMs, 0], [F.back, ROOF.backMs, ROOF.backDown]]) {
            steps.push([ms, 'her', f, x - mid, far - cell + 1 + down, null]);
        }
        // Into the opening, the near lip at her thighs; then down it, her hands on its rim (her `climb-out` frames).
        steps.push([ROOF.frameMs, 'her', F.back, x - mid, lip + ROOF.inOpening - cell, lip]);
        const out = this.climbOutFrames;
        for (const [f, hands, down] of ROOF.sink) steps.push([ROOF.frameMs, 'her', out[f], x - mid, lip - 1 - hands + down, lip]);
        return steps;
    }

    // Shows `steps` (from `roofSteps`) on `pic` one after another, on the scene's clock (as the tests step it), then `done`.
    roofRun(pic, steps, done) {
        let ms = 0, i = -1;
        const show = ([, key, frame, x, y, cut]) => {
            pic.setTexture(key, frame).setPosition(x, y).setVisible(true);
            if (cut == null) pic.setCrop();
            else pic.setCrop(0, 0, pic.width, Math.max(0, cut - y));
        };
        const run = (_, dt) => {
            ms += dt;
            let at = 0, k = 0;
            while (k < steps.length && ms >= at + steps[k][0]) at += steps[k++][0];
            if (k >= steps.length) {
                this.events.off('update', run);
                done();
                return;
            }
            if (k !== i) show(steps[i = k]);
        };
        this.events.on('update', run);
    }

    // A quick fade, and she is somewhere else: through a door to another route, down a chute, out of
    // a duct. `then` runs as she arrives.
    travel(x, y, route, then = null, viewDeck = null) {
        const p = this.player;
        this.mode = 'scripted';
        this.script = null;
        p.body.setVelocity(0, 0);
        this.pose('stand');
        const cam = this.cameras.main;
        cam.fadeOut(PROMENADE.fadeMs, 0, 0, 0);
        cam.once('camerafadeoutcomplete', () => {
            this.route = route;
            if (route !== 'cabin') this.setTowel(false);  // hung up in the cabin
            p.body.reset(x, y);
            this.takeoffY = y;
            // (`viewDeck`: the deck she drops into, from just under the one above: the pool's hatch.)
            this.viewDeck = viewDeck;
            this.grounded = false;
            this.updateCutaway(0);
            cam.centerOn(p.x, p.y - HALF);
            cam.fadeIn(PROMENADE.fadeMs * 1.3, 0, 0, 0);
            this.mode = 'play';
            then?.();
        });
    }

    stairPoint(f, t) {
        const { bottom: a, top: b } = f;
        if (!f.curve) return { x: Phaser.Math.Linear(a.x, b.x, t), y: Phaser.Math.Linear(a.y, b.y, t) };
        const c = { x: a.x + (b.x - a.x) * 0.6, y: a.y - (a.y - b.y) * 0.35 }; // about 28° at the foot, 56° at the top
        const u = 1 - t;
        return { x: u * u * a.x + 2 * u * t * c.x + t * t * b.x, y: u * u * a.y + 2 * u * t * c.y + t * t * b.y };
    }

    // How many steps a flight is drawn with: one each 8 px of its rise. Step i's corner is at `i / steps`.
    stairSteps(f) {
        return Math.max(2, Math.round((f.bottom.y - f.top.y) / 8));
    }

    // The funnel's stairway, out over the open air, has treads for a tangerine to land on: one thrown off
    // the funnel's top bounces down it step by step (it fell straight through them, part 5). She walks
    // its flights by their line; these are only the fruit's (`LooseTangerines.addColliders`).
    stairTreads(f) {
        const steps = this.stairSteps(f), at = t => {
            const q = this.stairPoint(f, t);
            return { x: Math.round(q.x), y: Math.round(q.y) };
        };
        for (let i = 0; i < steps; i++) {
            const p0 = at(i / steps), p1 = at((i + 1) / steps);
            const x = Math.min(p0.x, p1.x), w = Math.max(1, Math.abs(p1.x - p0.x)), h = Math.max(2, p0.y - p1.y);
            const z = this.add.zone(x, p1.y, w, h).setOrigin(0);
            this.physics.add.existing(z, true);
            (this.treads ||= []).push(z);
        }
    }

    // The top of the funnel stairway's tread at x, if there is one there.
    treadTop(x) {
        return this.treads?.find(z => x >= z.x && x < z.x + z.width)?.y ?? null;
    }

    flightLength(f) {
        let length = 0;
        for (let i = 1; i <= 24; i++) length += Phaser.Math.Distance.BetweenPoints(this.stairPoint(f, (i - 1) / 24), this.stairPoint(f, i / 24));
        return length;
    }

    // Stairs are in the background plane: she walks up them "behind" the floor slabs (§5.1). Drawn
    // from the user's photos (§5.3): blue carpet on the treads with a dark nosing, the flight's
    // side face below them; in front, a glass balustrade in brass under a wooden handrail in the
    // cores, gold ring scrollwork and a curled rail end on the atrium's curving staircase.
    drawStairs(g, front, f) {
        const look = STAIR_LOOKS[f.look] || (f.curve ? STAIR_LOOKS.atrium : STAIR_LOOKS.core);
        const steps = this.stairSteps(f);
        // On whole pixels, so nothing shimmers as the camera glides.
        const at = t => {
            const q = this.stairPoint(f, t);
            return { x: Math.round(q.x), y: Math.round(q.y) };
        };
        for (let i = 0; i < steps; i++) {
            const p0 = at(i / steps);
            const p1 = at((i + 1) / steps);
            const x = Math.min(p0.x, p1.x);
            const w = Math.max(1, Math.abs(p1.x - p0.x));
            // The step: its side face down to the flight's underside, its carpeted tread, its nosing.
            g.fillStyle(look.side, 1).fillRect(x, p1.y, w, p0.y - p1.y + look.thickness);
            g.fillStyle(look.carpet, 1).fillRect(x, p1.y, w, 3);
            g.fillStyle(look.fleck, 1).fillRect(x + w / 2, p1.y + 1, 1, 1);
            g.fillStyle(look.nosing, 1).fillRect(p1.x < p0.x ? x : x + w - 1, p1.y, 1, 4);
        }
        // The underside's edge, along the flight.
        g.lineStyle(1, look.edge, 1);
        for (let i = 0; i < steps; i++) {
            const p0 = at(i / steps);
            const p1 = at((i + 1) / steps);
            g.lineBetween(p0.x, p0.y + look.thickness, p1.x, p1.y + look.thickness);
        }

        // The balustrade, a rail height above the treads.
        const h = SIDEWALK.railHeight;
        const line = Array.from({ length: 25 }, (_, i) => at(i / 24));
        if (look.glass) {
            front.fillStyle(0x8fd3ff, 0.22);
            front.fillPoints([...line.map(q => ({ x: q.x, y: q.y - 2 })), ...line.slice().reverse().map(q => ({ x: q.x, y: q.y - h }))], true);
            for (let i = 0; i <= 24; i += 6) front.fillStyle(look.brass, 1).fillRect(line[i].x, line[i].y - h, 1, h - 2);
        } else if (look.plain) {
            // Steel: a post every so often, a mid rail.
            for (let i = 0; i <= 24; i += 4) front.fillStyle(look.brass, 1).fillRect(line[i].x, line[i].y - h, 1, h);
            for (let i = 0; i < 24; i++) front.lineStyle(1, look.brass, 1).lineBetween(line[i].x, line[i].y - h / 2, line[i + 1].x, line[i + 1].y - h / 2);
        } else {
            // Gold scrollwork: a row of rings between a gold bottom rail and the handrail.
            front.lineStyle(1, look.brass, 1);
            for (let i = 0; i < 24; i++) {
                front.lineBetween(line[i].x, line[i].y - 3, line[i + 1].x, line[i + 1].y - 3);
                front.strokeCircle(line[i].x, line[i].y - h / 2 - 1, 3);
            }
            front.fillStyle(look.rail, 1).fillCircle(line[0].x, line[0].y - h + 3, 3);  // the curl at its foot
        }
        for (let i = 0; i < 24; i++) {
            front.lineStyle(2, look.rail, 1).lineBetween(line[i].x, line[i].y - h, line[i + 1].x, line[i + 1].y - h);
            front.lineStyle(1, look.railLight, 1).lineBetween(line[i].x, line[i].y - h - 1, line[i + 1].x, line[i + 1].y - h - 1);
        }
    }

    // The gangway lobby (the user's photo): cream panelling, a heavy fire door held open against
    // the wall at either end, and a dark blue runner mat on the carpet by the shell door.
    drawGangway(g, o) {
        const top = o.y - this.deckPitch + 16;
        for (let x = o.x + 24; x < o.x + o.width - 16; x += 32) this.wallGfx.fillStyle(0xe3dccb, 1).fillRect(x, top, 1, o.y - top);
        // (A fire door held open at each end was drawn here; the lobby's ends are walls with real
        // doors now, as between every part of the ship: the user, 2026-11-07.)
    }

    // --- Deck 5's rooms (§5.3, the user's photos) ------------------------------------------------

    // La Cucina's entrance: a white marble portico, two columns under a pediment with its name.
    drawPortico(g, o, text) {
        const cx = o.x;
        const y = o.y;
        const marble = 0xefebe2, vein = 0xd6d0c3, edge = 0xb9b2a3;
        for (const side of [-1, 1]) {
            const x = cx + side * 23 - 5;
            g.fillStyle(edge, 1).fillRect(x - 3, y - 9, 16, 9);
            g.fillStyle(marble, 1).fillRect(x - 2, y - 8, 14, 7);
            g.fillStyle(marble, 1).fillRect(x, y - 88, 10, 80);
            g.fillStyle(vein, 1).fillRect(x + 3, y - 86, 1, 76).fillRect(x + 6, y - 86, 1, 76);
            g.fillStyle(edge, 1).fillRect(x + 9, y - 88, 1, 80);
            g.fillStyle(marble, 1).fillRect(x - 2, y - 93, 14, 5);
            g.fillStyle(edge, 1).fillRect(x - 2, y - 89, 14, 1);
        }
        g.fillStyle(marble, 1).fillRect(cx - 38, y - 105, 76, 12);
        g.fillStyle(edge, 1).fillRect(cx - 38, y - 94, 76, 1).fillRect(cx - 38, y - 105, 76, 1);
        g.fillStyle(marble, 1).fillTriangle(cx - 40, y - 105, cx + 40, y - 105, cx, y - 121);
        g.fillStyle(vein, 1).fillTriangle(cx - 30, y - 107, cx + 30, y - 107, cx, y - 118);
        const name = this.add.text(cx, y - 99, text, {
            fontFamily: 'Georgia, serif', fontSize: '8px', fontStyle: 'bold', color: '#4c3e24', resolution: 4,
        }).setOrigin(0.5).setDepth(DEPTH.decor + 0.01);
        this.worldLayer.add(name);
    }

    // Windows on the dining rooms' wall, the live sea in them, with beige drapes (La Cucina) or white
    // sheer curtains (the Four Seasons, the Seven Seas). Drawn on the back wall: the sea view is
    // what those rooms are about (the user, 2026-11-03).
    drawDiningWindows(g, o, xs, style) {
        const y = o.y;
        for (const cx of String(xs).split(',').filter(Boolean).map(Number)) {
            const x = cx - 17, top = y - 100, w = 34, h = 50;
            g.fillStyle(style === 'drapes' ? 0x46291f : 0xf4f4f4, 1).fillRect(x - 2, top - 2, w + 4, h + 4);
            this.windowView.mask.fillRect(x, top, w, h);
            const f = this.glassGfx;                    // on the glass and in front of it
            f.fillStyle(0xffffff, 0.35).fillRect(x + 3, top + 4, 8, 2);
            if (style === 'drapes') {
                f.fillStyle(0xd9c7a5, 1).fillRect(x - 6, top - 4, 9, h + 18).fillRect(x + w - 3, top - 4, 9, h + 18);
                f.fillStyle(0xbfa985, 1).fillRect(x - 3, top - 4, 1, h + 18).fillRect(x + w + 1, top - 4, 1, h + 18);
                f.fillStyle(0xc9b48f, 1).fillRect(x - 8, top - 8, w + 16, 6);
            } else {
                f.fillStyle(0xffffff, 0.6).fillRect(x - 3, top - 4, 8, h + 10).fillRect(x + w - 5, top - 4, 8, h + 10);
                f.fillStyle(0xffffff, 1).fillRect(x - 6, top - 6, w + 12, 3);
            }
        }
    }

    // Pillars floor to ceiling: burl wood with a brass ring (the Four Seasons, like the atrium's), or
    // white columns (the Seven Seas).
    drawPillars(g, o, xs, style) {
        const y = o.y, top = y - this.deckPitch + 16;
        for (const cx of String(xs).split(',').filter(Boolean).map(Number)) {
            if (style === 'burl') {
                g.fillStyle(0x9e4539, 1).fillRect(cx - 5, top, 10, y - top);
                g.fillStyle(0xcd683d, 1).fillRect(cx - 3, top, 3, y - top);
                g.fillStyle(0xd9a43b, 1).fillRect(cx - 7, y - 96, 14, 3);
            } else {
                // Marble, like La Cucina's portico: fluted, outlined, a capital and a base.
                const edge = 0xb9b2a3;
                g.fillStyle(edge, 1).fillRect(cx - 8, top, 16, y - top);
                g.fillStyle(0xefebe2, 1).fillRect(cx - 7, top + 8, 14, y - top - 17);
                g.fillStyle(0xd6d0c3, 1).fillRect(cx - 3, top + 10, 1, y - top - 21).fillRect(cx + 1, top + 10, 1, y - top - 21);
                g.fillStyle(0xd6d0c3, 1).fillRect(cx + 4, top + 8, 3, y - top - 17);
                g.fillStyle(0xefebe2, 1).fillRect(cx - 10, top, 20, 7).fillRect(cx - 10, y - 9, 20, 9);
                g.fillStyle(edge, 1).fillRect(cx - 10, top + 7, 20, 1).fillRect(cx - 10, y - 10, 20, 1);
            }
        }
    }

    // The Seven Seas' backlit glass panel: blue waves behind a lattice, in a gilded frame.
    drawWavePanel(g, o) {
        const x0 = o.x, x1 = o.x + o.width, top = o.y - 112, bottom = o.y - 14;
        g.fillStyle(0xc9b48f, 1).fillRect(x0 - 3, top - 3, x1 - x0 + 6, bottom - top + 6);
        const bands = [0x8fd3ff, 0x6fbcef, 0x4d9be6, 0x4d83cf, 0x4d65b4, 0x484a77];
        const bandH = (bottom - top) / bands.length;
        bands.forEach((c, i) => g.fillStyle(c, 1).fillRect(x0, top + i * bandH, x1 - x0, bandH + 1));
        for (let k = 0; k < 7; k++) {
            const base = top + 8 + k * 14;
            for (let x = x0; x < x1; x += 1) {
                const wy = base + Math.round(4 * Math.sin((x - x0) / 11 + k * 1.3));
                g.fillStyle(k < 3 ? 0xffffff : 0xcfeeff, 0.75).fillRect(x, wy, 1, 2);
            }
        }
        g.fillStyle(0xe8eaec, 0.7);
        for (let x = x0 + 26; x < x1 - 4; x += 27) g.fillRect(x, top, 2, bottom - top);
        for (let y = top + 24; y < bottom - 4; y += 25) g.fillRect(x0, y, x1 - x0, 2);
    }

    // Deck 5's Restaurant Reservations desk (the user's photo): a curved grey counter, a black top,
    // brass letters on the burl-wood wall over it.
    drawReservationsDesk(g, o, text) {
        const cx = o.x, y = o.y, w = 56, h = 34;
        g.fillStyle(0x7f8a92, 1).fillRoundedRect(cx - w / 2, y - h, w, h, { tl: 10, tr: 10, bl: 0, br: 0 });
        g.fillStyle(0x9babb2, 1).fillRoundedRect(cx - w / 2 + 3, y - h + 4, w - 10, h - 4, { tl: 8, tr: 4, bl: 0, br: 0 });
        for (let x = cx - w / 2 + 8; x < cx + w / 2 - 6; x += 8) g.fillStyle(0x8a959d, 1).fillRect(x, y - h + 6, 1, h - 6);
        g.fillStyle(0x2e222f, 1).fillRoundedRect(cx - w / 2 - 3, y - h - 4, w + 6, 5, 2);
        g.fillStyle(0x625565, 1).fillRect(cx - w / 2, y - h - 4, w, 1);
        const name = this.add.text(cx, y - 92, text, {
            fontFamily: 'Georgia, serif', fontSize: '8px', fontStyle: 'bold', color: '#e6b85c', resolution: 4,
        }).setOrigin(0.5).setDepth(DEPTH.decor + 0.01);
        this.worldLayer.add(name);
    }

    // The Windjammer's coffered ceiling: mahogany beams, dark green panels between.
    drawCoffers(g, o) {
        const top = o.y - this.deckPitch + 16;
        g.fillStyle(0x46291f, 1).fillRect(o.x, top, o.width, 10);
        for (let x = o.x; x < o.x + o.width; x += 40) {
            g.fillStyle(0x163028, 1).fillRect(x + 5, top + 2, 30, 6);
            g.fillStyle(0x5e3d2c, 1).fillRect(x, top, 5, 12);
        }
        g.fillStyle(0x5e3d2c, 1).fillRect(o.x, top + 10, o.width, 2);
    }

    // Big letters on a wall: the Photo Gallery's name.
    drawLettering(o, text) {
        const label = this.add.text(o.x, o.y - 117, text, {
            fontFamily: 'Verdana, sans-serif', fontSize: '10px', color: '#9a9a96', resolution: 4,
        }).setOrigin(0.5).setDepth(DEPTH.decor + 0.01);
        label.setLetterSpacing?.(2);
        this.worldLayer.add(label);
    }

    // The Stardust Lounge's stage: one picture (tools/build_stage.py; it was rectangles drawn here until 2026-11-24):
    // velvet curtains under a swagged valance, a lighting bar, a star cloth, the boards, the band's drum kit. Its
    // boards run 6 px forward of the curtain: the picture's own first columns, mirrored.
    drawStage(g, o) {
        if (!this.textures.exists('stage-back')) return;
        const back = this.add.image(o.x, o.y, 'stage-back').setOrigin(0, 1).setDepth(DEPTH.decor + 0.005);
        const lip = this.add.image(o.x, o.y, 'stage-back').setOrigin(0, 1).setDepth(DEPTH.decor + 0.005);
        lip.setCrop(0, lip.height - 10, 6, 10).setScale(-1, 1);
        this.worldLayer.add([back, lip]);
    }

    // A room open off a corridor: a light wood post where the corridor's wall ends, the room's brass
    // plaque on its own wall beside it.
    drawDoorway(g, o, text, hang, post = true) {
        const x = o.x, y = o.y, ceiling = y - this.deckPitch + 16;
        // (Where a wall with a door stands, its plaque only: the wall is the post.)
        if (post) {
            g.fillStyle(0xc9b48f, 1).fillRect(x - 3, ceiling, 6, y - ceiling);
            g.fillStyle(0xab947a, 1).fillRect(x + 2, ceiling, 1, y - ceiling);
        }
        if (text) {
            const plaque = this.add.text(x + 12, y - 96, text, {
                fontFamily: 'Verdana, sans-serif', fontSize: '7px', fontStyle: 'bold', color: '#45293f',
                backgroundColor: '#d9a43b', padding: { x: 3, y: 2 }, resolution: 4,
            }).setOrigin(0, 0.5).setDepth(DEPTH.decor + 0.01);
            this.worldLayer.add(plaque);
            // With open sky behind it, it hangs from the ceiling on two cords (nothing floats).
            if (hang) {
                const top = Math.round(plaque.y - plaque.height / 2);
                for (const cx of [x + 15, x + 12 + plaque.width - 4]) g.fillStyle(0x625565, 1).fillRect(cx, ceiling, 1, top - ceiling);
            }
        }
    }

    // The theatre's entrance: a gilded portal, its name lit up in a marquee of bulbs over it.
    drawMarquee(g, o, text) {
        const cx = o.x, y = o.y, w = 96, top = y - 118;
        for (const side of [-1, 1]) {
            const x = cx + side * (w / 2 - 4) - 4;
            g.fillStyle(0xd9a43b, 1).fillRect(x, top + 26, 8, y - top - 26);
            g.fillStyle(0xf9c22b, 1).fillRect(x + 2, top + 26, 2, y - top - 26);
        }
        g.fillStyle(0x6e2727, 1).fillRect(cx - w / 2, top, w, 26);
        g.fillStyle(0xd9a43b, 1).fillRect(cx - w / 2, top, w, 2).fillRect(cx - w / 2, top + 24, w, 2);
        for (let x = cx - w / 2 + 4; x < cx + w / 2 - 2; x += 6) {
            g.fillStyle(0xfbff86, 1).fillRect(x, top + 3, 2, 2).fillRect(x, top + 21, 2, 2);
        }
        const name = this.add.text(cx, top + 13, text, {
            fontFamily: 'Georgia, serif', fontSize: '9px', fontStyle: 'bold', color: '#fbff86', resolution: 4,
        }).setOrigin(0.5).setDepth(DEPTH.decor + 0.01);
        this.worldLayer.add(name);
    }

    // A burl-wood panel on a wall (the atrium on deck 7, the user's photos), for the ports' plaques.
    drawBurlPanel(g, o) {
        const top = o.y - this.deckPitch + 22, bottom = o.y - 6;
        g.fillStyle(0x9e4539, 1).fillRect(o.x - 2, top - 2, o.width + 4, bottom - top + 4);
        g.fillStyle(0xb5653a, 1).fillRect(o.x, top, o.width, bottom - top);
        for (let i = 0; i < o.width * (bottom - top) / 90; i++) {
            const x = o.x + ((i * 37) % o.width), y = top + ((i * 53) % (bottom - top));
            g.fillStyle(i % 3 ? 0x9e4539 : 0xcd683d, 1).fillRect(x, y, 2, 1);
        }
    }

    // A deck's directory board in a lobby (the user's deck 8 photo): blue in a brass frame, the
    // deck's plan in white across its top, its rooms listed below.
    drawDirectory(g, o) {
        const top = o.y - 72, w = o.width, h = 42;
        g.fillStyle(0xd9a43b, 1).fillRect(o.x, top, w, h);
        g.fillStyle(0x323353, 1).fillRect(o.x + 2, top + 2, w - 4, h - 4);
        g.fillStyle(0x4d65b4, 1).fillRect(o.x + 3, top + 3, w - 6, 6);
        g.fillStyle(0xf28c28, 1).fillRect(o.x + 4, top + 4, 4, 4);
        g.fillStyle(0xffffff, 1).fillRect(o.x + 10, top + 5, w - 14, 1);
        g.fillStyle(0xffffff, 1).fillRect(o.x + 4, top + 12, w - 8, 5);
        g.fillStyle(0x4d9be6, 1).fillRect(o.x + 6, top + 13, w - 12, 3);
        for (let i = 0; i < 7; i++) {
            g.fillStyle(i % 3 ? 0xc7dcd0 : 0xf9c22b, 1).fillRect(o.x + 4, top + 20 + i * 2.5, 3 + (i * 5) % 9 + 6, 1);
        }
    }

    // A warm light hidden along the top of a wall, as round the atrium (the user's photos).
    drawCove(g, o) {
        const y = o.y - this.deckPitch + 16;
        g.fillStyle(0xfbb954, 0.9).fillRect(o.x, y + 3, o.width, 1);
        for (let i = 0; i < 6; i++) g.fillStyle(0xfbb954, 0.35 * (1 - i / 6)).fillRect(o.x, y + 4 + i, o.width, 1);
    }

    // Warm downlights along a room's ceiling.
    drawDownlights(g, o) {
        const y = o.y - this.deckPitch + 16;
        for (let x = o.x + 24; x < o.x + o.width; x += 48) {
            g.fillStyle(0xfbff86, 1).fillRect(x - 2, y, 4, 2);
            g.fillStyle(0xfbff86, 0.18).fillRect(x - 5, y + 2, 10, 3);
        }
    }

    // A copy of the live background (§5.2) at `depth`, shown only where `mask` (a graphics filled
    // with window panes, in world space) is drawn; its horizon where it is outside, so the sea in
    // the windows lines up with the sea past the open decks (the user, 2026-11-08).
    addWindowView(depth) {
        const backdrop = new Backdrop(this, { waterY: this.waterY, depth: 0, gulls: this.farGulls });
        const view = this.add.container(0, 0, backdrop.objects).setScrollFactor(0).setDepth(depth);
        const mask = this.make.graphics({ add: false }).fillStyle(0xffffff, 1);
        view.enableFilters();
        view.filters.internal.addMask(mask);
        this.worldLayer.add(view);
        return { backdrop, view, mask };
    }

    // Windows along a wall, looking out to sea: the bridge's.
    drawWindows(g, o) {
        for (let x = o.x; x + 18 <= o.x + o.width; x += 24) {
            g.fillStyle(0xf4f4f4, 1).fillRect(x, o.y, 18, o.height);
            this.windowView.mask.fillRect(x + 2, o.y + 2, 14, o.height - 4);
            this.glassGfx.fillStyle(0xffffff, 0.3).fillRect(x + 3, o.y + 3, 2, o.height - 10);
        }
    }

    // The bridge's side windows (the user, 2026-11-06): big panes in white frames, mullions between
    // them, the live sea and sky in each.
    drawBridgeWindows(g, o) {
        const n = Math.max(1, Math.round(o.width / 66));
        const pane = (o.width - 4) / n;
        g.fillStyle(0xe8eaec, 1).fillRect(o.x, o.y, o.width, o.height);
        for (let i = 0; i < n; i++) {
            const x = Math.round(o.x + 4 + i * pane), w = Math.round(pane) - 4, h = o.height - 8;
            this.windowView.mask.fillRect(x, o.y + 4, w, h);
            this.glassGfx.fillStyle(0xffffff, 0.35).fillRect(x + 3, o.y + 7, 2, h - 12);
            this.glassGfx.fillStyle(0x9babb2, 1).fillRect(x, o.y + 4 + h - 1, w, 1);
        }
        g.fillStyle(0x9babb2, 1).fillRect(o.x, o.y + o.height - 2, o.width, 2);
    }

    // Deck 12's sports court (NCL's plan): painted green with white lines, in a tall net cage on
    // white posts, the net behind it (she plays in front of it).
    drawCourt(g, o) {
        const x0 = o.x, x1 = o.x + o.width, y = o.y, top = y - 120;
        g.fillStyle(0x239063, 1).fillRect(x0, y - 2, o.width, 2);
        for (const x of [x0 + 4, (x0 + x1) / 2 - 1, x1 - 6]) g.fillStyle(0xffffff, 1).fillRect(x, y - 2, 2, 2);
        g.fillStyle(0x165a4c, 0.35);
        for (let x = x0; x <= x1; x += 4) g.fillRect(x, top, 1, y - top - 2);
        for (let yy = top; yy < y - 2; yy += 4) g.fillRect(x0, yy, o.width, 1);
        const posts = Math.max(2, Math.round(o.width / 96) + 1);
        for (let i = 0; i < posts; i++) {
            const x = Math.round(x0 + i * (o.width - 3) / (posts - 1));
            g.fillStyle(0xe8eaec, 1).fillRect(x, top, 3, y - top);
            g.fillStyle(0x9babb2, 1).fillRect(x + 2, top, 1, y - top);
        }
        g.fillStyle(0xe8eaec, 1).fillRect(x0, top, o.width, 3);
    }

    // Over deck 11's chess set (the user's photo from deck 12): white pipes on tall blue posts.
    drawPergola(g, o) {
        const top = o.y - 112;
        const posts = [o.x, o.x + o.width / 2, o.x + o.width - 4].map(Math.round);
        for (const x of posts) {
            g.fillStyle(0x4d65b4, 1).fillRect(x, top, 4, o.y - top);
            g.fillStyle(0x4d9be6, 1).fillRect(x + 1, top, 1, o.y - top);
        }
        g.fillStyle(0xf4f4f4, 1).fillRect(o.x - 4, top - 3, o.width + 8, 3);
        g.fillStyle(0xc7dcd0, 1).fillRect(o.x - 4, top, o.width + 8, 1);
        g.fillStyle(0xf4f4f4, 1).fillRect(o.x - 4, top + 14, o.width + 8, 2);
    }

    // Shuffleboard courts painted along the deck: a blue lane, its scoring triangle's white lines.
    drawShuffleboard(g, o) {
        const y = o.y;
        g.fillStyle(0x4d9be6, 1).fillRect(o.x, y - 2, o.width, 2);
        for (let x = o.x + 20; x < o.x + o.width - 20; x += 22) g.fillStyle(0xffffff, 1).fillRect(x, y - 2, 1, 2);
        for (const x of [o.x + 2, o.x + o.width - 4]) g.fillStyle(0xf9c22b, 1).fillRect(x, y - 2, 2, 2);
    }

    // Los Lobos' paper flags (papel picado), strung in swags under the ceiling.
    drawBunting(g, o) {
        const ceiling = o.y - this.deckPitch + 16;
        const colours = [0xe83b3b, 0xf9c22b, 0x1ebc73, 0x4d9be6, 0xf04f78, 0xfb6b1d];
        const swag = 96;
        let i = 0;
        for (let a = o.x; a < o.x + o.width - 8; a += swag) {
            const b = Math.min(a + swag, o.x + o.width);
            for (let x = a + 4; x < b - 4; x += 8, i++) {
                const t = (x - a) / (b - a);
                const sag = Math.round(4 + 14 * Math.sin(Math.PI * t));
                g.fillStyle(0x3e3546, 1).fillRect(x, ceiling + sag, 8, 1);
                g.fillStyle(colours[i % colours.length], 1).fillRect(x + 1, ceiling + sag + 1, 6, 5);
                g.fillRect(x + 2, ceiling + sag + 6, 4, 1);
            }
        }
    }

    // The Spinnaker Lounge's windows (the user's photos): tall panes in white frames looking out to
    // sea, beige curtains gathered at both sides of each under a wood pelmet, a white sill, and a
    // brass handrail along them on brackets.
    drawSpinnakerWindows(g, o) {
        const y = o.y, x0 = o.x, x1 = o.x + o.width;
        const top = y - 118, sill = y - 46;
        const n = Math.max(1, Math.round(o.width / 80));
        const unit = o.width / n;
        // The panes: one white-framed window per unit, the live sea and sky in it.
        for (let i = 0; i < n; i++) {
            const a = Math.round(x0 + i * unit), b = Math.round(x0 + (i + 1) * unit);
            g.fillStyle(0xf4f4f4, 1).fillRect(a, top, b - a, sill - top);
            const gx = a + 4, gw = b - a - 8, gy = top + 4, gh = sill - top - 6;
            this.windowView.mask.fillRect(gx, gy, gw, gh);
            this.glassGfx.fillStyle(0xffffff, 0.3).fillRect(gx + 4, gy + 3, 2, gh - 8);
            this.glassGfx.fillStyle(0xe8eaec, 1).fillRect(Math.round((a + b) / 2) - 1, top, 2, sill - top);   // the mullion
        }
        g = this.glassGfx;                              // the rest hangs in front of the glass
        // The sill, white. (A dark ledge under it was dropped: it made no sense, the user.)
        g.fillStyle(0xf4f4f4, 1).fillRect(x0 - 4, sill - 2, o.width + 8, 3);
        // A wood pelmet along the top; under it the curtains, gathered at each window's sides and
        // tied back at sill height, their folds in darker beige.
        g.fillStyle(0x9e6a3f, 1).fillRect(x0 - 6, top - 6, o.width + 12, 6);
        g.fillStyle(0xc28d5a, 1).fillRect(x0 - 6, top - 6, o.width + 12, 1);
        const tie = 0.62;
        for (let i = 0; i <= n; i++) {
            const mid = Math.round(x0 + i * unit);
            for (let yy = top; yy < sill + 1; yy++) {
                // Full where it hangs from the pelmet, drawn in to the tie-back, flaring out below.
                const t = (yy - top) / (sill - top);
                const w = t < tie ? 6 + 16 * Math.pow(1 - t / tie, 1.4) : 6 + 8 * Math.pow((t - tie) / (1 - tie), 0.8);
                const a = Math.round(mid - w / 2), ww = Math.max(2, Math.round(w));
                g.fillStyle(0xe6d6b8, 1).fillRect(a, yy, ww, 1);
                // Its folds follow the gathering: darker lines at fixed fractions of its width, the
                // edges shaded.
                for (const f of [0.3, 0.62]) g.fillStyle(0xc8b38e, 1).fillRect(a + Math.round(ww * f), yy, 1, 1);
                g.fillStyle(0xd2bf9a, 1).fillRect(a + ww - 1, yy, 1, 1);
                g.fillStyle(0xf4ead8, 1).fillRect(a, yy, 1, 1);
            }
            // The tie-back: a cord round it.
            const ty = Math.round(top + (sill - top) * tie);
            g.fillStyle(0xab947a, 1).fillRect(mid - 4, ty - 1, 8, 2);
            g.fillStyle(0xf9c22b, 1).fillRect(mid - 1, ty - 1, 2, 2);
        }
        // The brass handrail along the windows, on brackets.
        const rail = sill + 12;
        g.fillStyle(0xf9c22b, 1).fillRect(x0 - 4, rail, o.width + 8, 2);
        g.fillStyle(0xcd683d, 1).fillRect(x0 - 4, rail + 2, o.width + 8, 1);
        for (let x = x0 + 10; x < x1; x += 64) g.fillStyle(0xab947a, 1).fillRect(x, rail + 2, 2, 5);
    }

    // The giant chess set on deck 11 (the user's photo from deck 12): its board a checked mat on the
    // deck, knee-high pieces standing on it, white and black, seen from the side.
    drawChess(g, o) {
        const y = o.y;
        for (let x = o.x, i = 0; x < o.x + o.width; x += 8, i++) {
            g.fillStyle(i % 2 ? 0x2e222f : 0xf4f4f4, 1).fillRect(x, y - 2, Math.min(8, o.x + o.width - x), 2);
        }
        const piece = (cx, kind, white) => {
            const [fill, edge] = white ? [0xf4f4f4, 0x9babb2] : [0x2e222f, 0x625565];
            const r = (x, yy, w, h) => g.fillStyle(fill, 1).fillRect(cx + x, y - 2 - yy - h, w, h);
            g.fillStyle(edge, 1).fillRect(cx - 6, y - 4, 12, 2);
            r(-5, 0, 10, 2);
            if (kind === 'pawn') { r(-3, 2, 6, 8); g.fillStyle(fill, 1).fillCircle(cx, y - 16, 4); }
            if (kind === 'rook') { r(-4, 2, 8, 14); r(-5, 16, 10, 3); r(-5, 19, 2, 2); r(-1, 19, 2, 2); r(3, 19, 2, 2); }
            if (kind === 'knight') { r(-4, 2, 8, 10); r(-4, 12, 6, 8); r(-7, 15, 5, 4); r(0, 20, 2, 2); }
            if (kind === 'bishop') { r(-3, 2, 6, 12); g.fillStyle(fill, 1).fillEllipse(cx, y - 19, 7, 10); r(-1, 23, 2, 2); }
            if (kind === 'queen') { r(-3, 2, 6, 16); r(-5, 18, 10, 3); r(-5, 21, 2, 3); r(-1, 21, 2, 4); r(3, 21, 2, 3); }
            if (kind === 'king') { r(-3, 2, 6, 18); r(-5, 20, 10, 3); r(-1, 23, 2, 6); r(-3, 25, 6, 2); }
            g.fillStyle(edge, 1).fillRect(cx + (white ? 2 : -3), y - 8, 1, 4);
        };
        const set = ['rook', 'pawn', 'knight', 'king', 'pawn', 'queen', 'bishop', 'pawn'];
        set.forEach((kind, i) => piece(o.x + 10 + i * ((o.width - 20) / (set.length - 1)), kind, i % 3 !== 1));
    }

    // The sauna, built into the spa (the user): a small room of dark cedar, its front cut away like
    // every room's, a glass door at its near end, a warm lamp; its benches and stove are pieces.
    drawSauna(g, o) {
        const ceiling = o.y - this.deckPitch + 16, w = o.width;
        g.fillStyle(0xb5703f, 1).fillRect(o.x, ceiling, w, o.y - ceiling);
        for (let y = ceiling + 5; y < o.y; y += 6) g.fillStyle(0x9a5b33, 1).fillRect(o.x, y, w, 1);
        g.fillStyle(0x7a4528, 1).fillRect(o.x, ceiling, w, 6);
        // (Its two ends are walls across the deck with glass doors: see buildBulkhead.)
        // A warm lamp in the corner, its glow kept within the sauna's walls (the user); a thermometer;
        // a bucket and ladle on the floor.
        for (let i = 4; i >= 1; i--) {
            const r = 4 * i;
            g.fillStyle(0xfbb954, 0.07).fillRect(o.x + w - 18 - r, ceiling + 6, Math.min(2 * r, 12 + r), r + 14);
        }
        g.fillStyle(0xfbff86, 1).fillRect(o.x + w - 21, ceiling + 18, 6, 4);
        g.fillStyle(0xe6904e, 1).fillRect(o.x + 18, o.y - 70, 3, 12);
        g.fillStyle(0xae2334, 1).fillRect(o.x + 19, o.y - 62, 1, 3);
        g.fillStyle(0x7a4528, 1).fillRect(o.x + w - 30, o.y - 7, 8, 7);
        g.fillStyle(0x9a5b33, 1).fillRect(o.x + w - 23, o.y - 13, 1, 7).fillRect(o.x + w - 24, o.y - 13, 4, 1);
        // Its name on a wooden plaque over the door.
        const name = this.add.text(o.x + 22, ceiling + 14, 'SAUNA', {
            fontFamily: 'Georgia, serif', fontSize: '6px', fontStyle: 'bold', color: '#fbe9a6', resolution: 4,
        }).setOrigin(0, 0.5).setDepth(DEPTH.decor + 0.05);
        this.worldLayer.add(name);
    }

    // A white canopy on two posts over the hot tub (as on the real ship, the user).
    drawCanopy(o) {
        const g = this.add.graphics().setDepth(DEPTH.decor + 0.15);
        const top = o.y - 84;
        g.fillStyle(0xe8eaec, 1).fillRect(o.x - 4, top, 3, o.y - top);
        g.fillStyle(0xe8eaec, 1).fillRect(o.x + o.width + 1, top, 3, o.y - top);
        g.fillStyle(0xf4f4f4, 1).fillRect(o.x - 10, top - 6, o.width + 20, 6);
        g.fillStyle(0xc7dcd0, 1).fillRect(o.x - 10, top - 1, o.width + 20, 1);
        for (let x = o.x - 8; x < o.x + o.width + 10; x += 8) g.fillStyle(0xf4f4f4, 1).fillTriangle(x, top, x + 8, top, x + 4, top + 3);
        this.worldLayer.add(g);
    }

    // The Great Outdoors' sun cover (the user, 2026-11-07): cream canvas hooked to the aft edge of
    // deck 12, running aft over the first tables on white posts, sagging a little between its
    // supports, its near edge's valance all along it. Behind her; and she can walk on top of it (the
    // user): from deck 12's aft terrace she hops the rail and drops onto it, landing from above, and
    // walks off its end down to the tables. From below she jumps and walks through it.
    drawSunCover(o, posts) {
        const g = this.add.graphics().setDepth(DEPTH.decor + 0.15);
        const ceiling = o.y - this.deckPitch + 16, postTop = o.y - 112;
        for (const x of posts) {
            g.fillStyle(0xe8eaec, 1).fillRect(x - 2, postTop, 4, o.y - postTop);
            g.fillStyle(0x9babb2, 1).fillRect(x + 1, postTop, 1, o.y - postTop);
            g.fillStyle(0x9babb2, 1).fillRect(x - 4, o.y - 3, 8, 3);
        }
        // Its supports, bow to stern: deck 12's edge, then each post's top.
        const pts = [[o.x, ceiling], ...posts.map(x => [x, postTop])];
        const surface = [];
        this.cover = { x0: o.x, surface };
        for (let i = 0; i < pts.length - 1; i++) {
            const [a, ya] = pts[i], [b, yb] = pts[i + 1];
            for (let x = a; x <= b; x++) {
                const t = (x - a) / (b - a);
                const y = Math.round(ya + (yb - ya) * t + 6 * Math.sin(Math.PI * t));
                // The canvas, and its near edge's valance hanging all along it: soft stripes, a
                // scalloped hem.
                g.fillStyle(0xf4ead8, 1).fillRect(x, y, 1, 4);
                // Its top holds her, its height kept for every x (coverTopAt).
                surface[Math.round(x - o.x)] = y;
                g.fillStyle(0xd8c8a8, 1).fillRect(x, y + 4, 1, 1);
                const stripe = Math.floor((x - o.x) / 8) % 2 ? 0xf4ead8 : 0xbfe6f5;
                const hem = 9 + Math.round(2 * Math.sin(((x - o.x) % 12) / 12 * Math.PI));
                g.fillStyle(stripe, 1).fillRect(x, y + 5, 1, hem);
                g.fillStyle(0xd8c8a8, 1).fillRect(x, y + 5 + hem, 1, 1);
            }
        }
        this.worldLayer.add(g);
    }

    // --- The funnel (the user's photos, 2026-11-07) ---------------------------------------------
    // On its white base under the name board: a navy casing, then the open lattice, navy struts
    // over its dark inside, raked back at the front; the NCL logo on its aft part, white letters
    // over waves in three blues; grey exhaust pipes on top, and white smoke drifting aft from them.

    buildFunnel(o) {
        const fa = o.x, fb = o.x + o.width, base = o.y;
        const g = this.add.graphics().setDepth(DEPTH.exterior + 0.04);
        const navy = 0x323353, deep = 0x1d2040, strut = 0x404574;
        g.fillStyle(0xe8eaec, 1).fillPoints([{ x: fa, y: base }, { x: fb, y: base }, { x: fb - 4, y: base - 64 }, { x: fa + 6, y: base - 64 }], true);
        g.fillStyle(0xc7dcd0, 1).fillRect(fa + 6, base - 66, fb - fa - 10, 2);
        // The casing.
        const c0 = base - 64, c1 = base - 108;
        g.fillStyle(navy, 1).fillPoints([{ x: fa + 14, y: c0 }, { x: fb - 8, y: c0 }, { x: fb - 18, y: c1 }, { x: fa + 60, y: c1 }], true);
        g.fillStyle(strut, 1).fillRect(fa + 58, c1, fb - fa - 76, 3);
        // The lattice: its outline points, bottom fore and aft, top aft and fore.
        const top = base - 500;
        const L = [{ x: fa + 150, y: c1 }, { x: fb - 90, y: c1 }, { x: fb - 150, y: top }, { x: fa + 560, y: top }];
        g.fillStyle(deep, 1).fillPoints(L, true);
        const edge = (t, side) => side === 0
            ? { x: L[0].x + (L[3].x - L[0].x) * t, y: c1 + (top - c1) * t }
            : { x: L[1].x + (L[2].x - L[1].x) * t, y: c1 + (top - c1) * t };
        g.lineStyle(10, navy, 1).strokePoints(L, true);
        for (let k = 1; k < 5; k++) {
            const a = edge(k / 5, 0), b = edge(k / 5, 1);
            g.lineStyle(6, navy, 1).lineBetween(a.x, a.y, b.x, b.y);
        }
        // Its struts: an X across each panel of each bay, inside the frame.
        const lerp = (p, q, t) => ({ x: p.x + (q.x - p.x) * t, y: p.y + (q.y - p.y) * t });
        g.lineStyle(3, strut, 1);
        for (let k = 0; k < 5; k++) {
            const a0 = edge(k / 5, 0), b0 = edge(k / 5, 1), a1 = edge((k + 1) / 5, 0), b1 = edge((k + 1) / 5, 1);
            for (let j = 0; j < 4; j++) {
                const bl = lerp(a0, b0, j / 4), br = lerp(a0, b0, (j + 1) / 4);
                const tl = lerp(a1, b1, j / 4), tr = lerp(a1, b1, (j + 1) / 4);
                g.lineBetween(bl.x, bl.y, tr.x, tr.y);
                g.lineBetween(br.x, br.y, tl.x, tl.y);
                g.lineBetween(tr.x, tr.y, br.x, br.y);
            }
        }
        // The NCL logo on its aft part.
        const lx = fb - 470, ly = top + 110, lw = 170, lh = 240;
        g.fillStyle(0x8fb6dc, 1).fillRect(lx, ly, lw, lh);
        g.fillStyle(0x6d93c4, 1).fillRect(lx, ly + lh * 0.58, lw, lh * 0.14);
        g.fillStyle(0x4d65b4, 1).fillRect(lx, ly + lh * 0.72, lw, lh * 0.14);
        g.fillStyle(0x323a72, 1).fillRect(lx, ly + lh * 0.86, lw, lh * 0.14);
        g.fillStyle(0xd8e8f6, 1).fillRect(lx + 20, ly + lh * 0.52, lw - 40, 4);
        const ncl = this.add.text(lx + lw / 2, ly + lh * 0.3, 'NCL', {
            fontFamily: 'Verdana, sans-serif', fontSize: '60px', fontStyle: 'bold', color: '#ffffff', resolution: 2,
        }).setOrigin(0.5).setDepth(DEPTH.exterior + 0.045);
        // The exhaust pipes on top.
        const pipes = [];
        for (const [dx, h, w] of [[30, 70, 34], [80, 90, 30], [126, 80, 36], [178, 96, 30], [300, 84, 34]]) {
            const x = L[3].x + dx;
            g.fillStyle(0x7a6e66, 1).fillRect(x, top - h, w, h);
            g.fillStyle(0x9b8e84, 1).fillRect(x + 4, top - h, 6, h);
            g.fillStyle(0x3e3546, 1).fillRect(x, top - h, w, 6);
            pipes.push({ x: x + w / 2, y: top - h });
        }
        this.worldLayer.add([g, ncl]);
        // A bit of white smoke: puffs rising from the pipes, drifting aft, swelling and fading.
        if (!this.textures.exists('puff')) {
            const pg = this.make.graphics({ x: 0, y: 0 }, false);
            pg.fillStyle(0xffffff, 1).fillCircle(32, 32, 32);
            pg.generateTexture('puff', 64, 64);
            pg.destroy();
        }
        this.smoke = [];
        pipes.forEach((p, i) => {
            for (let k = 0; k < 3; k++) {
                const puff = this.add.image(p.x, p.y, 'puff').setDepth(DEPTH.exterior + 0.03).setAlpha(0);
                this.worldLayer.add(puff);
                const tween = this.tweens.add({
                    targets: puff, x: p.x + 260, y: p.y - 200, scale: { from: 0.5, to: 2.6 }, alpha: { from: 0.8, to: 0 },
                    duration: 4200, delay: i * 500 + k * 1400, repeat: -1, ease: 'Sine.easeOut',
                });
                this.smoke.push(tween);
            }
        });
    }

    // The far background laid out for the camera as it stands. (A look-out's zoom out, `world.lookFar`, 0 to 1: the
    // horizon goes down onto the waterline with it, and the far background keeps its size on the screen, as in play.)
    layBackdrop(flow) {
        const cam = this.cameras.main, far = this.world?.lookFar ?? 0, outside = !!this.overview || this.fromAfar;
        const horizon = far > 0 && !outside && this.horizonOnScreen !== undefined
            ? this.horizonOnScreen + ((this.waterY - cam.scrollY - cam.height / 2) * cam.zoom + cam.height / 2 - this.horizonOnScreen) * far
            : this.horizonOnScreen;
        const keep = far > 0 && !outside ? VIEW.zoom / cam.zoom : 1;
        this.backdrop.update(flow, outside, horizon, this.fromAfar ? this.intro?.look : null, keep);
    }

    // --- The outside view (the user, 2026-11-07) ------------------------------------------------
    // O: the camera draws back to show the whole ship from outside, every deck's side closed, her
    // hidden and the game paused; +/- zoom on the middle, the mouse wheel toward the pointer; the
    // movement keys do nothing there (the user, 2026-11-07); O or Esc and she is back where she was.

    // (`still`: the sea, the sky and the gulls hold still too, for a picture stitched from many
    // views: tools/render_ship.py.)
    enterOverview(still = false) {
        const cam = this.cameras.main;
        const ov = this.overview = { zoom: cam.zoom, scrollX: cam.scrollX, scrollY: cam.scrollY, still };
        this.physics.pause();
        this.time.paused = true;
        this.tweens.pauseAll();
        for (const t of this.smoke || []) t.resume();       // the funnel's smoke keeps drifting
        this.player.setVisible(false);
        this.uiCam.setVisible(false);
        // (A bubble over someone by her would hang on the closed side: away; the game brings it back.)
        for (const q of this.world.people.list) q.bubbleItems?.forEach(i => i.setVisible(false));
        // The canvas fills the whole window while it is open, sky and sea to its edges, no bars at
        // its sides (the user, 2026-11-07); play keeps its 16:9 view.
        this.scale.scaleMode = Phaser.Scale.EXPAND;
        this.scale.displaySize.setAspectMode(Phaser.Structs.Size.NONE);   // (FIT's 16:9 lock off)
        this.scale.refresh();
        cam.setSize(this.scale.width, this.scale.height);
        this.washCam.setSize(this.scale.width, this.scale.height);      // the evening light, over all of it
        this.duskWash.setSize(this.scale.width, this.scale.height);
        cam.stopFollow();
        cam.removeBounds();
        ov.fit = this.scale.width / (this.map.widthInPixels * 0.94);
        cam.setZoom(ov.fit);
        // The ship and the horizon low in the frame, by half the ship's height (waterline to the
        // funnel's top), so the sky and its clouds have room over it (the user, 2026-11-08).
        if (this.shipTop === undefined) {
            this.shipTop = this.waterY;
            this.solidLayer.forEachTile(t => { if (t.index > 0) this.shipTop = Math.min(this.shipTop, t.pixelY); });
        }
        cam.centerOn(this.map.widthInPixels / 2, this.waterY - 4 * this.deckPitch - (this.waterY - this.shipTop) / 2);
        ov.wheel = (pointer, objects, dx, dy) => this.zoomOverview(dy > 0 ? 1 / 1.25 : 1.25, pointer);
        this.input.on('wheel', ov.wheel);
        this.updateCutaway(1);
    }

    zoomOverview(factor, pointer = null) {
        const cam = this.cameras.main;
        // Toward the pointer: the world point under it stays under it.
        const before = pointer ? cam.getWorldPoint(pointer.x, pointer.y) : null;
        cam.setZoom(Phaser.Math.Clamp(cam.zoom * factor, this.overview.fit, VIEW.zoom));
        if (before) {
            cam.preRender();
            const after = cam.getWorldPoint(pointer.x, pointer.y);
            cam.scrollX += before.x - after.x;
            cam.scrollY += before.y - after.y;
        }
    }

    updateOverview(input, dt) {
        if (input.zoomInPressed) this.zoomOverview(1.25);
        if (input.zoomOutPressed) this.zoomOverview(1 / 1.25);
        this.updateCutaway(dt);
    }

    leaveOverview() {
        const cam = this.cameras.main, ov = this.overview;
        this.input.off('wheel', ov.wheel);
        this.overview = null;
        this.scale.scaleMode = Phaser.Scale.FIT;
        this.scale.displaySize.setAspectMode(Phaser.Structs.Size.FIT);
        this.scale.displaySize.setAspectRatio(VIEW.width / VIEW.height);
        this.scale.setGameSize(VIEW.width, VIEW.height);
        this.scale.refresh();
        cam.setSize(VIEW.width, VIEW.height);
        this.washCam.setSize(VIEW.width, VIEW.height);
        this.duskWash.setSize(VIEW.width, VIEW.height);
        cam.setZoom(ov.zoom);
        cam.setBounds(0, -560, this.map.widthInPixels, this.map.heightInPixels + 560);   // above the map: the funnel's top
        // Centred on her at once (where following would take it anyway), and the horizon in its
        // place with it, so nothing glides after the switch (the user, 2026-11-08).
        // (startFollow clears the follow offset: set again, or the camera sits half her height low.)
        cam.startFollow(this.player, true, 0.15, 0.15);
        cam.setFollowOffset(0, HALF);
        cam.centerOn(this.player.x, this.player.y - HALF);
        this.horizonOnScreen = undefined;
        this.player.setVisible(true);
        this.uiCam.setVisible(true);
        this.tweens.resumeAll();
        this.time.paused = false;
        this.physics.resume();
        this.updateCutaway(1);
    }

    // The top of the sun cover under x, or null past its ends.
    coverTopAt(x) {
        const c = this.cover;
        const y = c ? c.surface[Math.round(x - c.x0)] : undefined;
        return y === undefined ? null : y;
    }

    // The pool shower's cubicle: a roof on corner posts, frosted glass walls to shoulder height, the
    // shower showing through them.
    drawShowerBox(o) {
        const g = this.add.graphics().setDepth(DEPTH.decor + 0.15);
        const roof = o.y - 74;
        g.fillStyle(0xffffff, 0.45).fillRect(o.x, o.y - 56, o.width, 52);
        g.fillStyle(0xc7dcd0, 1).fillRect(o.x, o.y - 56, o.width, 1);
        g.fillStyle(0x9babb2, 1).fillRect(o.x - 2, roof, 2, o.y - roof).fillRect(o.x + o.width, roof, 2, o.y - roof);
        g.fillStyle(0xe8eaec, 1).fillRect(o.x - 5, roof - 4, o.width + 10, 5);
        g.fillStyle(0x9babb2, 1).fillRect(o.x - 5, roof, o.width + 10, 1);
        this.worldLayer.add(g);
    }

    // Deck 3's crew corridor, where the game starts (the user, 2026-11-14): a working corridor,
    // plainer than the guests'. Painted panels over a green dado and a grey kick strip, a steel
    // handrail on brackets; under the deck above a grey pipe, the red fire main and a cable tray
    // on hangers, tube lights under them. All on the wall, behind every door and fitting.
    drawCrewDeck(o) {
        const g = this.wallGfx;
        const top = o.y - this.deckPitch + 16, x0 = o.x, x1 = o.x + o.width, w = o.width;
        for (let x = x0 + 40; x < x1 - 8; x += 48) g.fillStyle(0xd9cdb6, 1).fillRect(x, top, 1, o.y - top - 40);
        g.fillStyle(0xc5d0b4, 1).fillRect(x0, o.y - 40, w, 40);
        g.fillStyle(0x9aa888, 1).fillRect(x0, o.y - 40, w, 1);
        g.fillStyle(0x9babb2, 1).fillRect(x0, o.y - 4, w, 4);
        g.fillStyle(0x7f708a, 1).fillRect(x0, o.y - 4, w, 1);
        // The handrail, at about her hip, a bracket under it every metre and a half.
        for (let x = x0 + 16; x < x1 - 4; x += 72) g.fillStyle(0x7f708a, 1).fillRect(x, o.y - 32, 1, 4);
        g.fillStyle(0xe3e7ea, 1).fillRect(x0, o.y - 34, w, 1);
        g.fillStyle(0x9babb2, 1).fillRect(x0, o.y - 33, w, 2);
        // Under the deck above: the pipes and the tray, a hanger every two metres.
        g.fillStyle(0xf6f3ec, 1).fillRect(x0, top, w, 2);
        g.fillStyle(0xc7dcd0, 1).fillRect(x0, top + 4, w, 1);
        g.fillStyle(0x9babb2, 1).fillRect(x0, top + 5, w, 3);
        g.fillStyle(0xe83b3b, 1).fillRect(x0, top + 10, w, 1);
        g.fillStyle(0xae2334, 1).fillRect(x0, top + 11, w, 2);
        g.fillStyle(0x625565, 1).fillRect(x0, top + 16, w, 1);
        for (let x = x0 + 6; x < x1; x += 6) g.fillStyle(0x625565, 1).fillRect(x, top + 15, 1, 1);
        for (let x = x0 + 30; x < x1 - 4; x += 96) {
            g.fillStyle(0x7f708a, 1).fillRect(x, top + 2, 1, 15);
            g.fillStyle(0x9babb2, 1).fillRect(x - 1, top + 4, 3, 5);        // a flange on the pipe
            g.fillStyle(0x7a2634, 1).fillRect(x - 1, top + 10, 3, 3);       // and on the main
        }
        // The tube lights, between the hangers.
        for (let x = x0 + 62; x + 32 < x1; x += 96) {
            g.fillStyle(0x9babb2, 1).fillRect(x, top + 18, 32, 2);
            g.fillStyle(0xfbff86, 1).fillRect(x + 2, top + 20, 28, 1);
        }
    }

    drawShellDoor(g, o) {
        g.fillStyle(0xd9cdb6, 1);
        g.fillRect(o.x, o.y, o.width, o.height);
        g.lineStyle(2, 0xb9ab90, 1);
        g.strokeRect(o.x + 2, o.y + 2, o.width - 4, o.height - 2);
        g.lineBetween(o.x + o.width / 2, o.y + 2, o.x + o.width / 2, o.y + o.height);
        g.fillStyle(0xa9c8d8, 1);
        g.fillCircle(o.x + o.width / 4, o.y + 16, 4);
        g.fillCircle(o.x + (o.width * 3) / 4, o.y + 16, 4);
    }

    // A cabin corridor, as in the user's photos (§5.3): a white ceiling with round downlights, a
    // wooden handrail, terracotta cabin doors every 4 m (192px), a few with vacation stickers, and
    // now and then a framed picture. All muted, so none of it reads as interactive.
    drawCabinDoors(g, o, first, last, coreBefore, coreAfter) {
        const CABIN_DOOR_CLEAR = 100;    // px, centre to centre
        const ceiling = o.y - this.deckPitch + 16;
        g.fillStyle(0xf6f3ec, 1);
        g.fillRect(o.x, ceiling, o.width, 3);
        g.fillStyle(0xd8b29a, 1);
        g.fillRect(o.x, o.y - 33, o.width, 2);     // the handrail, at about her hip
        g.fillStyle(0xc49a80, 1);
        g.fillRect(o.x, o.y - 31, o.width, 1);

        // Each cabin deck its own framed pictures (plan-the-rest §6, the user's sets, 2026-11-24; `DECK_PICTURES` in
        // tools/build_ship_art.py): any other corridor keeps the old three.
        const pictures = (DECK_PICTURES[this.deckOfY(o.y)] ?? ['sea', 'ship', 'art']).map(n => `picture-${n}-bg`);
        const parts = [];
        // (A picture is not hung behind a tall thing of the plan's world that stands against the wall,
        // the towel stack, or anywhere a tall trolley is pushed along: it goes to the nearest gap with
        // nothing on its wall and nothing of the world in front of it; the user, 2026-11-18. `gaps`:
        // each gap and whether its wall is taken.)
        const ents = (this.cache.json.get('world')?.ents ?? []).filter(e => e.y === o.y && e.route === 'inside');
        const rolls = (e, x, by) => (e.kind === 'push' && e.tall === true && x > e.min - by && x < e.max + by)
            || (e.kind === 'robot' && x > e.x0 - by && x < e.x1 + by);   // (and a delivery robot's run, §7f 15)
        const tall = (gap) => ents.some(e => (e.kind === 'stack' && Math.abs(e.x - gap) < 40) || rolls(e, gap, 40));
        const gaps = [], moved = [];
        for (let x = o.x + 60, n = Math.round(o.x / 192); x + 30 < o.x + o.width; x += 192, n++) {
            const gap = x + 15 + 96;                 // halfway to the next door
            g.fillStyle(0xfffbe8, 1);
            g.fillEllipse(gap, ceiling + 3, 8, 3);
            const inside = gap + 20 < o.x + o.width;
            gaps.push({ gap, taken: !inside || n % 3 === 1 || n % 6 === 3 || n % 8 === 5
                || ents.some(e => Math.abs(e.x - gap) < 60 || rolls(e, gap, 60)) || this.doorSpots.some(t => t.y === o.y && Math.abs(gap - t.x) < 60) });
            // (A porthole she looks out of takes the place of the gap's picture: population `PORTHOLES`.)
            const porthole = ents.some(e => e.kind === 'porthole' && Math.abs(e.x - gap) < 60);
            if (n % 3 === 1 && inside && !porthole) {
                if (tall(gap)) moved.push({ gap, frame: pictures[n % pictures.length] });
                else parts.push(this.add.image(gap, o.y - 50, 'shipart', pictures[n % pictures.length]).setDepth(DEPTH.decor + 0.1));
            }
            // Now and then an extinguisher on the wall, or an exit sign up high, between doors.
            // (Kept 50 px from a door put in a cabin door's place, clear of its card reader: one hung
            // under the reader of deck 4's crew door, the user, 2026-11-17.)
            if (n % 6 === 3 && gap + 20 < o.x + o.width) {
                const by = this.doorSpots.find(t => t.y === o.y && Math.abs(gap - t.x) < 50);
                const ex = by ? by.x + (gap >= by.x ? 50 : -50) : gap;
                parts.push(this.add.image(ex, o.y - 14, 'shipart', 'extinguisher-bg').setOrigin(0.5, 1).setDepth(DEPTH.decor + 0.1));
            }
            if (n % 8 === 5 && gap + 20 < o.x + o.width) parts.push(this.add.image(gap, o.y - 100, 'shipart', 'exit-sign-bg').setOrigin(0.5, 1).setDepth(DEPTH.decor + 0.1));
            // No cabin door right beside a trunk's or a crew door (the user, 2026-11-03).
            if (this.doorSpots.some(t => t.y === o.y && Math.abs(x + 15 - t.x) < CABIN_DOOR_CLEAR)) continue;
            // (Beside a towel stack a door stands 8 px nearer to it, its fallen heap plainly across the frame's foot: the
            // user, 2026-11-26; the same rule as `nudged()` in tools/build_world.py, for the doors placed in its slots.)
            const stack = ents.find(e => e.kind === 'stack' && Math.abs(e.x - (x + 17)) < 100);
            const x0 = x;
            if (stack) x += stack.x > x + 17 ? 8 : -8;
            if (this.openCabinDoors.some(t => t.y === o.y && Math.abs(x + 17 - t.x) < 4)) { x = x0; continue; }
            // Most doors are plain; about one in six has stickers, each its own.
            const frame = (n * 7) % 6 === 0 ? `door-cabin-stickers-${1 + (n % 3)}-bg` : 'door-cabin-bg';
            // (Kept: the doors there are, for those who go door to door: the paper rounds, breakfast.)
            (this.cabinDoorsDrawn ??= []).push({ x: x + 17, y: o.y });
            parts.push(this.add.image(x, o.y, 'shipart', frame).setOrigin(0, 1).setDepth(DEPTH.decor + 0.1));
            x = x0;
            // Now and then a housekeeping trolley or a room-service cart left by a door.
            const cart = n % 9 === 4 ? 'towel-trolley-bg' : n % 11 === 7 ? 'service-cart-bg' : null;
            // (None where a tall trolley of the plan's world is pushed: the steward's, 2026-11-18.)
            if (cart && x + 64 < o.x + o.width && !ents.some(e => rolls(e, x + 48, 50))) parts.push(this.add.image(x + 48, o.y, 'shipart', cart).setOrigin(0.5, 1).setDepth(DEPTH.decor + 0.115));
            // (Over the doors and the wall, under whoever walks past it, `back`'s 0.12: deck 10's officer went behind it, the
            // user, 2026-11-26: "should obscure the trolley, not be behind it".)
        }
        for (const m of moved) {
            const free = gaps.filter(q => !q.taken).sort((a, b) => Math.abs(a.gap - m.gap) - Math.abs(b.gap - m.gap))[0];
            if (!free) continue;
            free.taken = true;
            parts.push(this.add.image(free.gap, o.y - 50, 'shipart', m.frame).setDepth(DEPTH.decor + 0.1));
            (this.picturesMoved ??= []).push({ from: m.gap, to: free.gap, y: o.y });
        }
        // By a stair core, a brass plaque with the corridor's cabin numbers and an arrow along it.
        // (The arrow is drawn: at this size the font's arrow comes out blank.)
        const plaque = (x, dir) => {
            const text = this.add.text(x, o.y - 96, `${first}\u2013${last}`, {
                fontFamily: 'Verdana, sans-serif', fontSize: '6px', fontStyle: 'bold', color: '#45293f',
                backgroundColor: '#d9a43b', padding: { left: dir < 0 ? 8 : 2, right: dir > 0 ? 8 : 2, top: 1, bottom: 1 },
                resolution: 4,
            }).setOrigin(0.5).setDepth(DEPTH.decor + 0.1);
            const tip = x + (dir * text.width) / 2 - dir * 2;
            const arrow = this.add.triangle(0, 0, tip, o.y - 96, tip - dir * 4, o.y - 99, tip - dir * 4, o.y - 93, 0x45293f)
                .setOrigin(0).setDepth(DEPTH.decor + 0.2);
            parts.push(text, arrow);
        };
        if (coreBefore) plaque(o.x + 36, 1);
        if (coreAfter) plaque(o.x + o.width - 36, -1);
        this.worldLayer.add(parts);
    }

    // An escape trunk (§5.1): a crew door on each deck it serves, top to bottom, with ▲/▼ lamps above
    // and, if it needs a card, a reader beside it.
    buildTrunk(o, floors, oneWay, card) {
        const ys = String(floors).split(',').map(Number);
        const trunk = {
            id: o.name, x: o.x, top: ys[0], bottom: ys[ys.length - 1], oneWay, card,
            opened: !oneWay || this.save.opened.includes(o.name), doors: [],
        };
        for (const y of ys) {
            const door = {
                trunk, y, open: false,
                sprite: this.add.image(o.x, y, 'shipart', 'door-crew').setOrigin(0.5, 1).setDepth(DEPTH.props),
                up: this.add.image(o.x - 5, y - LAMP_RISE, 'arrow-up').setDepth(DEPTH.props),
                down: this.add.image(o.x + 5, y - LAMP_RISE, 'arrow-down').setDepth(DEPTH.props),
            };
            this.worldLayer.add([door.sprite, door.up, door.down]);
            if (card) {
                const rx = o.x + DOOR.width / 2 + 6;
                const reader = this.add.image(rx, y - 40, 'reader').setDepth(DEPTH.props);
                const light = this.add.rectangle(rx, y - 42, 4, 2, CARD_COLOURS[card] ?? 0xffffff).setDepth(DEPTH.props);
                this.worldLayer.add([reader, light]);
            }
            trunk.doors.push(door);
        }
        this.lightTrunk(trunk);
        this.trunks.push(trunk);
    }

    // A lit arrow is a way she can go from that door. A one-way trunk's lower doors stay dark, and
    // shut from outside, until she has come down through it once.
    lightTrunk(trunk) {
        trunk.doors.forEach((d, i) => {
            const usable = this.trunkUsableFrom(d);
            d.up.setTexture(usable && i > 0 ? 'arrow-up-on' : 'arrow-up');
            d.down.setTexture(usable && i < trunk.doors.length - 1 ? 'arrow-down-on' : 'arrow-down');
        });
    }

    trunkUsableFrom(door) {
        return door.trunk.opened || door.y === door.trunk.top;
    }

    // The atrium (§5.3): open from its floor on deck 5 up to a skylight under deck 11, its decks
    // crossing it on side walks. Behind them, burl-wood pillars with a brass ring at each level.
    buildAtrium(o, levels) {
        const x0 = o.x;
        const x1 = o.x + o.width;
        const top = o.y;
        const bottom = o.y + o.height;
        const g = this.add.graphics().setDepth(DEPTH.decor);
        this.worldLayer.add(g);
        // The skylight dome (the user's photo central_area (2)), seen from below: a shallow bowl of
        // glass right under deck 11's floor, ribbed in white, edged in brass.
        const cx = (x0 + x1) / 2;
        const rx = 130;
        const ry = 26;
        const bowl = [];
        for (let i = 0; i <= 32; i++) {
            const a = (Math.PI * i) / 32;
            bowl.push({ x: Math.round(cx - rx * Math.cos(a)), y: Math.round(top + ry * Math.sin(a)) });
        }
        g.fillStyle(0xcfeeff, 1).fillPoints(bowl, true);
        g.lineStyle(1, 0xffffff, 1);
        for (let k = -4; k <= 4; k++) {
            const bx = cx + k * 30;
            g.lineBetween(cx, top + ry - 6, bx, top + Math.round(ry * Math.sqrt(Math.max(0, 1 - ((bx - cx) / rx) ** 2))));
        }
        g.lineStyle(1, 0xd9a43b, 1).strokePoints(bowl, false);
        // Burl-wood pillars, floor to ceiling, clear of the staircase round the glass elevator.
        for (const px of [x0 + 22, cx - 250, cx + 240, x1 - 32]) {
            g.fillStyle(0x9e4539, 1).fillRect(px, top, 10, bottom - top);
            g.fillStyle(0xcd683d, 1).fillRect(px + 2, top, 3, bottom - top);
            for (const y of String(levels).split(',').map(Number)) g.fillStyle(0xd9a43b, 1).fillRect(px - 2, y + 4, 14, 3);
        }
    }

    // A side walk (§5.3): a walkway level with its deck's floor, across an open space, behind a
    // glass railing; she simply runs along it. Indoors in the atrium's colours, outdoors in the open
    // deck's. Deck 12's, over the pools, lets her drop through with ↓.
    buildSidewalk(o, style, dropThrough) {
        const x0 = o.x;
        const x1 = o.x + o.width;
        const y = o.y;
        const look = SIDEWALK_LOOKS[style] || SIDEWALK_LOOKS.atrium;
        const back = this.add.graphics().setDepth(DEPTH.walkFloor);
        const front = this.add.graphics().setDepth(DEPTH.player + 0.5);
        this.worldLayer.add([back, front]);
        (this.deckFronts ||= []).push({ deck: this.deckOfY(y), gfx: front });

        // The walkway: its floor on top, its front with an edge, a light under it.
        back.fillStyle(look.front, 1).fillRect(x0, y, x1 - x0, 12);
        back.fillStyle(look.floor, 1).fillRect(x0, y, x1 - x0, 3);
        for (let px = x0 + 2; px < x1; px += 6) back.fillStyle(look.fleck, 1).fillRect(px, y + 1, 2, 1);
        back.fillStyle(look.edge, 1).fillRect(x0, y + 3, x1 - x0, 1);
        if (look.light) back.fillStyle(look.light, 1).fillRect(x0, y + 12, x1 - x0, 2);
        // The railing in front of it: glass panels between posts, a handrail along the top.
        const railTop = y - SIDEWALK.railHeight;
        front.fillStyle(0x8fd3ff, 0.22).fillRect(x0, railTop, x1 - x0, SIDEWALK.railHeight + PLAYER.sink);
        front.fillStyle(look.rail, 1).fillRect(x0, railTop, x1 - x0, 2);
        for (let px = x0; px <= x1; px += 40) front.fillStyle(look.post, 1).fillRect(px, railTop, 1, SIDEWALK.railHeight + PLAYER.sink);

        // The walkway itself: floor from above.
        const walk = { x0, x1, y, dropThrough, atrium: style === 'atrium' };
        walk.zone = this.add.zone(x0, y, x1 - x0, 6).setOrigin(0);
        walk.zone.walk = walk;
        this.physics.add.existing(walk.zone, true);
        this.walkGroup.add(walk.zone);
        this.walks.push(walk);
    }

    // A pool on deck 11 or 12 (§5.3): water she can jump into and swim in. Its front is drawn over
    // her, a little see-through, so she is in it rather than on it.
    // From the deck under a pool's or lower, it is out of sight and out of the way.
    underPools(deck = 11) {
        return this.viewDeck !== null && Math.round(this.viewDeck) < deck;
    }

    buildPool(o, deck) {
        const water = this.add.graphics().setDepth(DEPTH.poolWater);
        // (Drawn down to the foot of the tank's wall, `TANK_FOOT` px under the pool's own floor: the wall's last row of
        // tiles ends there, and a strip of it showed dry under the water: the user, 2026-11-24, "The water in the pool
        // isn't all the way down".)
        water.fillStyle(0x4d9be6, 0.55).fillRect(o.x, o.y, o.width, o.height + TANK_FOOT);
        water.fillStyle(0x8fd3ff, 0.9).fillRect(o.x, o.y, o.width, 1);
        const ripples = this.add.tileSprite(o.x, o.y + 1, o.width, 2, 'sea').setOrigin(0).setAlpha(0.5).setDepth(DEPTH.poolWater + 0.01);
        this.worldLayer.add([water, ripples]);
        this.pools.push({ x0: o.x, x1: o.x + o.width, y: o.y, bottom: o.y + o.height, foot: o.y + o.height + TANK_FOOT, ripples, water, deck });
    }

    // An elevator (§5.1). A core one has landing doors on every deck and a car that travels out of
    // sight; the atrium's glass one is a single car, seen on its rails. Floors run top to bottom.
    buildLift(o, floors, decks, regions, glass) {
        const ys = String(floors).split(',').map(Number);
        const ds = String(decks).split(',').map(Number);
        const rs = String(regions).split(',').map(Number);
        const lift = {
            id: o.name, x: o.x, glass,
            floors: ys.map((y, i) => ({ y, deck: ds[i], region: rs[i] })),
            at: ys.length - 1, carY: ys[ys.length - 1],
        };
        if (glass) {
            // Rails up the atrium wall, from the lowest floor to under the top deck's ceiling.
            const top = ys[0] - this.deckPitch + 16;
            const rails = this.add.graphics().setDepth(DEPTH.decor);
            rails.fillStyle(0x9aa3ad, 1);
            for (const dx of [-39, 37]) rails.fillRect(o.x + dx, top, 2, lift.carY - top);
            // The glass elevator's dark column, as in the user's photos: the curving staircase
            // passes behind it, and it hides her there.
            rails.fillStyle(0x313638, 1).setDepth(DEPTH.glassShaft).fillRect(o.x - 36, top, 72, lift.carY - top);
            rails.fillStyle(0x625565, 1).fillRect(o.x - 26, top, 2, lift.carY - top).fillRect(o.x + 22, top, 1, lift.carY - top);
            lift.car = this.add.image(o.x, 0, 'glass-car').setOrigin(0.5, 1).setDepth(DEPTH.glassCar);
            this.worldLayer.add([rails, lift.car]);
            lift.leaves = this.makeLeaves(o.x, 'glass-leaf', DEPTH.glassDoors, GLASS_LEAF);
            this.placeCar(lift);
        } else {
            for (const f of lift.floors) {
                const car = this.add.image(o.x, f.y, 'lift-car').setOrigin(0.5, 1).setDepth(DEPTH.liftCar);
                const frame = this.add.image(o.x, f.y, 'lift-frame').setOrigin(0.5, 1).setDepth(DEPTH.props + 0.1);
                const number = this.add.text(o.x, f.y - 82, String(f.deck), {
                    fontFamily: 'Verdana, sans-serif', fontSize: '7px', fontStyle: 'bold', color: '#f28c28', backgroundColor: '#14161c',
                    padding: { x: 2, y: 1 }, resolution: 4,
                }).setOrigin(0.5).setDepth(DEPTH.props);
                // The deck's number on a red disc beside the doors (the user's deck 8 photo).
                const disc = this.add.circle(o.x - 27, f.y - 46, 4, 0xae2334).setDepth(DEPTH.props);
                const digit = this.add.text(o.x - 27, f.y - 46, String(f.deck), {
                    fontFamily: 'Verdana, sans-serif', fontSize: '5px', fontStyle: 'bold', color: '#ffffff', resolution: 4,
                }).setOrigin(0.5).setDepth(DEPTH.props);
                this.worldLayer.add([disc, digit]);
                this.worldLayer.add([car, frame, number]);
                f.leaves = this.makeLeaves(o.x, 'lift-leaf', DEPTH.props);
                this.setLeaves(f.leaves, f.y, 0);
            }
        }
        this.lifts.push(lift);
    }

    makeLeaves(x, texture, depth, width = LEAF) {
        const left = this.add.image(x - width, 0, texture).setOrigin(0, 1).setDepth(depth);
        const right = this.add.image(x, 0, texture).setOrigin(0, 1).setDepth(depth);
        this.worldLayer.add([left, right]);
        return { left, right, width, open: 0 };
    }

    // Leaves slide apart into the wall: each shows only the part still in the doorway.
    setLeaves(leaves, y, open) {
        leaves.open = open;
        const w = leaves.width * (1 - open);
        for (const [leaf, cropX] of [[leaves.left, 0], [leaves.right, leaves.width - w]]) {
            leaf.y = y;
            leaf.setVisible(w >= 1);
            if (w >= 1) leaf.setCrop(cropX, 0, w, DOOR.height);
        }
    }

    placeCar(lift) {
        lift.car.y = lift.carY + 3; // its floor sits just under the deck's floor line
        this.setLeaves(lift.leaves, lift.carY, lift.leaves.open);
    }

    buildPlayer() {
        const meta = this.cache.json.get('her-meta');
        this.herFrames = meta.frames;
        this.towelFrames = this.cache.json.get('her-towel-meta').frames;
        // With Bumbot in her arms (§6.1.9, src/world/finale.js): her own sheet of it.
        this.catFrames = this.cache.json.get('her-cat-meta').frames;
        this.holding ??= false;             // (the story has set it already in a game saved on the way home)
        this.climbOutFrames = meta.anims['climb-out'];
        this.idleAt = 0;
        const p = this.physics.add.sprite(0, 0, 'her', this.herFrames.stand).setOrigin(0.5, 1).setDepth(DEPTH.player);
        p.body.setSize(PLAYER.bodyWidth, PLAYER.bodyHeight);
        this.herDrop(0, p);
        p.body.setMaxVelocity(10000, PLAYER.maxFall);
        this.worldLayer.add(p);
        this.player = p;
        // Her own clips' sounds on their frames (frame from 0): her lick of the cone at his table (part 5).
        // (And her stroke's splash, on the frame her kick begins.)
        const HER_SOUNDS = { 'her-lick-cone': [[3, 'lick']], 'her-swim': [[SWIM.strokeAt, 'stroke']] };
        p.on('animationupdate', (anim, frame) => {
            const at = HER_SOUNDS[anim.key]?.find(([i]) => i === frame.index - 1);
            if (at) sfx[at[1]]();
        });

        // The pools are sunk below their deck's floor, into the ceiling of the deck under it: from
        // there (seen from it, or jumping in it) they are not there (the user, 2026-11-06).
        // Outside (the promenade, the boat walkway, the balconies) she is in front of the ship's side:
        // only the outside's own floors and walls hold her (src/world/).
        // In one of the plan's rooms only the deck's floor holds her: a room by a deck's end lies over
        // the ship's structure there.
        this.physics.add.collider(p, this.solidLayer, null, (_, tile) => {
            if (this.route === OUTSIDE || this.route === 'duct') return false;
            const room = this.world.rooms[this.route];
            if (room?.def && tile.pixelY < room.floor) return false;
            return tile.index !== this.poolTile || !this.underPools(tile.poolDeck);
        });
        this.physics.add.collider(p, this.routeWalls || [], null, (_, zone) => zone.route === this.route);
        for (const b of this.bulkheads) this.physics.add.collider(p, b.zone, null, () => !b.open && this.route === 'inside');
        this.progress.addColliders(p);
        this.physics.add.collider(p, this.railingStops || []);
        if (this.cabin) {
            this.physics.add.collider(p, this.cabin.bed, null, (_, bed) =>
                this.route === 'cabin' && p.body.velocity.y >= 0 && p.body.bottom <= bed.body.top + 10);
        }
        // A side walk holds her coming down onto it, unless she is dropping through it.
        this.droppingThrough = null;
        // (Out over the atrium under the open parasol, she floats down in front of its walks.)
        this.physics.add.collider(p, this.walkGroup, null, (_, zone) =>
            (!zone.walk.route || zone.walk.route === this.route)
            && this.droppingThrough !== zone.walk && !(zone.walk.atrium && this.overRail && this.gliding)
            && p.body.velocity.y >= 0 && p.body.bottom <= zone.body.top + 10);
        this.physics.add.collider(p, this.crates, null, (_, crate) => {
            if (!this.isLunging()) return true;
            this.smash(crate.x, crate.y);
            this.save.broken.push(crate.name);
            crate.disableBody(true, true);
            return false;
        });
    }

    buildCameras() {
        const cam = this.cameras.main;
        cam.setZoom(VIEW.zoom);
        cam.setBounds(0, -560, this.map.widthInPixels, this.map.heightInPixels + 560);   // above the map: the funnel's top
        cam.setDeadzone(40, 24);
        cam.ignore(this.uiLayer);

        // The sunset's light on the ship (§6.1.9): the whole picture multiplied by a warm colour,
        // by a camera of its own between the world's and the HUD's (so the outside view, which
        // hides the HUD, keeps it); the sky and the sea are drawn to look themselves under it
        // (background.js).
        this.washLayer = this.add.layer();
        this.duskWash = this.add.rectangle(0, 0, VIEW.width, VIEW.height, 0xffffff).setOrigin(0)
            .setBlendMode(Phaser.BlendModes.MULTIPLY).setVisible(false);
        this.washLayer.add(this.duskWash);
        cam.ignore(this.washLayer);
        this.washCam = this.cameras.add(0, 0, VIEW.width, VIEW.height);
        this.washCam.ignore([this.worldLayer, this.uiLayer]);
        this.setDusk(this.dusk ?? 0);       // (the story may have set it already: a game saved at sunset)

        // The HUD gets its own unzoomed camera, so its text stays crisp.
        this.uiCam = this.cameras.add(0, 0, VIEW.width, VIEW.height);
        this.uiCam.ignore([this.worldLayer, this.washLayer]);
    }

    buildHud() {
        // Her cry and the words over her (src/popup.js): in the world, so they move exactly with her
        // (drawn by the screen's own camera they jittered a pixel as the world camera glided), from her
        // head in whichever picture shows her; Bumbot's "Meow!" from his (`alert.from`).
        const herHead = (alert = false) => {
            if (alert && this.alert?.from === 'bumbot' && this.holding) {
                const h = this.popups.headOf(this.player, 'her-cat-bumbot');
                if (h) return h;
            }
            const h = this.popups.herHead();
            // (`alertOver`: over a thing held over her head, the inside-out parasol, its top that many px
            // over her standing height: the tail stops over it.)
            return h && this.alertOver ? { ...h, top: Math.min(h.top, this.player.y - PLAYER.height - this.alertOver) } : h;
        };
        this.bubble = this.popups.make('shout', herHead, 0).setText(CRY.shout);
        this.alert = this.popups.make('auto', () => herHead(true), 0);
        this.fade = this.add.rectangle(0, 0, VIEW.width, VIEW.height, 0x0d1422).setOrigin(0).setAlpha(0);
        this.debugText = this.add.text(VIEW.width - 12, 12, '', { fontFamily: 'monospace', fontSize: '14px', color: '#ffffff' })
            .setOrigin(1, 0).setVisible(new URLSearchParams(location.search).has('debug'));
        // The sound's sign, shown a moment when M switches it: a loudspeaker, crossed out when muted.
        this.soundSign = this.add.graphics().setAlpha(0);
        // The counts and the cards (src/hud.js): nothing until the first of each is hers.
        this.hud = new Hud(this);
        this.uiLayer.add([this.fade, this.debugText, this.soundSign]);
    }

    // (Under the HUD's top right, where her utilities stand since 2026-11-26: src/hud.js.)
    showSoundSign(muted) {
        const g = this.soundSign, x = VIEW.width - 64, y = 88;
        g.clear();
        g.fillStyle(0x1d2b53, 0.85).fillRoundedRect(x - 12, y - 10, 62, 44, 6);
        g.fillStyle(0xffffff, 1).fillRect(x, y + 6, 10, 12);
        g.fillTriangle(x + 8, y + 12, x + 20, y, x + 20, y + 24);
        g.lineStyle(3, muted ? 0xe83b3b : 0xffffff, 1);
        if (muted) g.lineBetween(x + 26, y + 4, x + 42, y + 20).lineBetween(x + 42, y + 4, x + 26, y + 20);
        else g.beginPath().arc(x + 22, y + 12, 8, -0.9, 0.9).strokePath().beginPath().arc(x + 22, y + 12, 15, -0.9, 0.9).strokePath();
        this.tweens.killTweensOf(g);
        g.setAlpha(1);
        this.tweens.add({ targets: g, alpha: 0, delay: 1300, duration: 400 });
    }

    // The sunset coming on (0 the day, 1 the full sunset): the sky, the sea, the windows' copies of
    // them, and the evening light on everything.
    setDusk(k) {
        this.dusk = k;
        this.backdrop.setDusk(k);
        this.seaView.setDusk(k);
        for (const w of [this.windowView, this.cabinView, this.roomView]) w?.backdrop.setDusk(k);
        const [r, g, b] = DUSK_LIGHT.map(v => Math.round(255 * (1 + (v - 1) * k)));
        this.duskWash?.setFillStyle((r << 16) | (g << 8) | b).setVisible(k > 0);
    }

    refreshHud() {
        this.hud?.refresh();
    }

    // A tangerine is hers (picked up, handed back, the piñata's): one more at once, and its picture
    // flies from where it was, (x, y) in the world, to the HUD's count, which changes as it lands
    // (docs/plan-three-uses.md §1.7); the first one shows the count (src/hud.js). Several follow
    // each other.
    gainTangerine(x, y) {
        this.save.tangerines += 1;
        sfx.tangerine();
        const cam = this.cameras.main, view = cam.worldView, time = this.time.now;
        const from = { x: (x - view.x) * cam.zoom, y: (y - view.y) * cam.zoom };
        const to = this.hud.tangerineTarget();
        const delay = Math.max(0, (this.tallyNext ?? 0) - time);
        this.tallyNext = time + delay + TALLY.gapMs;
        this.flying = (this.flying ?? 0) + 1;
        this.refreshHud();
        const img = this.add.image(from.x, from.y, 'tangerine').setOrigin(0.5, 0.6).setScale(cam.zoom).setVisible(delay === 0);
        this.uiLayer.add(img);
        const k = { v: 0 };
        this.tweens.add({
            targets: k, v: 1, delay, duration: TALLY.ms, ease: 'Sine.easeIn',
            onStart: () => img.setVisible(true),
            onUpdate: () => img.setPosition(from.x + (to.x - from.x) * k.v, from.y + (to.y - from.y) * k.v - Math.sin(Math.PI * k.v) * TALLY.arc)
                .setScale(cam.zoom + (to.scale - cam.zoom) * k.v),
            onComplete: () => {
                img.destroy();
                this.flying -= 1;
                sfx.tally();
                this.hud.landed();
            },
        });
    }

    // D with none on her: the count blinks once, and that is all.
    blinkCount() {
        this.hud.blink();
    }

    // --- Spawning --------------------------------------------------------------------------

    // ?at=<place> starts her at a named place, for testing (README); otherwise her last checkpoint.
    initialSpawn() {
        const at = this.places[new URLSearchParams(location.search).get('at')];
        return at || this.checkpoints.find(c => c.active && c.id === this.save.lastCheckpoint) || this.spawnPoint;
    }

    // She always comes back at the activated checkpoint closest to where she was: same deck
    // first, then the nearest deck, then the nearest along the deck (§5.5).
    // She never comes back behind a door shut to her (plan-the-rest §7e): one on her deck with a wall across it between
    // the checkpoint and where she was, whose door would not open to her coming from the checkpoint's side (a one-way
    // door not yet come through, a card or a flag she lacks), is left out; with none left, the rule gives way.
    closestCheckpoint(x, y) {
        return this.nearestCheckpoint(x, y, true) || this.nearestCheckpoint(x, y, false) || this.spawnPoint;
    }

    // Whether a wall across the deck between the checkpoint c and x would keep her from coming back to x from it.
    shutBetween(c, x) {
        if (c.route !== 'inside' || this.route !== 'inside') return false;
        const lo = Math.min(c.x, x), hi = Math.max(c.x, x), side = c.x < x ? -1 : 1;
        const walls = [...this.bulkheads.map(b => ({ x: b.x, floor: b.floor, lock: b.lockSpec, id: b.id })),
            ...this.progress.barriers.map(w => ({ x: w.x, floor: w.zone.y + this.deckPitch / 2 - 8, lock: w.lock, id: w.id }))];
        return walls.some(w => w.lock && Math.abs(w.floor - c.y) <= 4 && w.x > lo && w.x < hi && !this.progress.passes(w.lock, side, w.id).ok);
    }

    nearestCheckpoint(x, y, ruled) {
        let best = null;
        let bestScore = Infinity;
        for (const c of this.checkpoints) {
            if (!c.active) continue;
            if (ruled && Math.round(Math.abs(c.y - y) / this.deckPitch) === 0 && this.shutBetween(c, x)) continue;
            // (One on the route she is on, a hallway's or a balcony's, before any other.)
            const score = Math.round(Math.abs(c.y - y) / this.deckPitch) * 1e6 + Math.abs(c.x - x)
                + (c.route !== this.route && (this.route === 'inside' || this.route === OUTSIDE) ? 3e6 : 0);
            if (score < bestScore) {
                best = c;
                bestScore = score;
            }
        }
        return best;
    }

    spawnAt(point, { emerge = false } = {}) {
        const p = this.player;
        p.clearAlpha().setCrop().setVisible(true).setDepth(DEPTH.player).setFlipX(false);
        this.inTrunk = null;
        this.resetVerbs();
        this.route = point.route || 'inside';
        this.liftRun = null;
        this.liftMove = null;
        this.hideLiftPanel();
        this.pose('stand');
        p.body.enable = true;
        p.body.reset(point.x, point.y);
        p.body.allowGravity = true;
        this.grounded = true;
        this.takeoffY = point.y;
        this.horizonOnScreen = undefined;               // the horizon snaps to her new floor
        this.setTowel(false);
        this.lastGroundedAt = this.time.now;
        this.alert.setVisible(false);

        const cam = this.cameras.main;
        cam.startFollow(p, true, 0.15, 0.15);
        cam.setFollowOffset(0, HALF);
        cam.centerOn(p.x, p.y - HALF);
        // The cut-away goes straight to her deck, rather than sliding over from the deck she left
        // (after a scare she stood in front of the hull for a moment, the user, 2026-11-06).
        this.viewDeck = this.route === 'inside' ? Math.round(this.deckAt(point.y)) : null;
        this.updateCutaway(0);

        if (!emerge) {
            this.mode = 'play';
            return;
        }
        // Stepping out of the crew cabin door.
        this.mode = 'scripted';
        sfx.door();
        p.setAlpha(0);
        if (point.door && point.route === 'inside') {
            point.door.setAlpha(0.5);
            this.tweens.add({ targets: point.door, alpha: 1, duration: 400 });
        }
        this.tweens.add({ targets: p, alpha: 1, duration: 350, onComplete: () => { this.mode = 'play'; } });
    }

    // --- Main loop -------------------------------------------------------------------------

    update(time, delta) {
        const dt = Math.min(delta, 50) / 1000;
        const input = this.controls.update();
        // The welcome screen and the intro move the camera: before the sky is laid out for it.
        this.intro?.update(input, dt);
        // The ship is under way bow first (§5.2): the sea streams past toward the stern, even in
        // the outside view.
        const flow = this.overview?.still ? 0 : dt;
        this.seaView.update(flow);
        // The horizon (§5.2): on the screen, gliding to its place over the floor she stands on (on
        // stairs, ladders and lifts, over her feet); while she is in the air it holds still on the
        // screen, as far things do, so a jump doesn't move it (the user, 2026-11-08).
        const cam = this.cameras.main;
        const ground = this.mode === 'play' || this.mode === 'scripted' ? this.takeoffY : this.player.y;
        const target = (ground - HORIZON_ABOVE - cam.scrollY - cam.height / 2) * cam.zoom + cam.height / 2;
        if (this.horizonOnScreen === undefined) this.horizonOnScreen = target;
        else if (!this.overview && (this.mode === 'play' ? this.grounded : this.mode !== 'scripted')) {
            this.horizonOnScreen += (target - this.horizonOnScreen) * (1 - Math.exp(-dt / HORIZON_SETTLE));
        }
        this.farGulls.update(flow);
        // (In the intro's wide views the far background holds still: its drift aft is how it looks
        // from the ship under way, and that camera is not on the ship. The user saw the islands
        // and clouds slide past a sun that stood still.)
        this.layBackdrop(this.fromAfar ? 0 : flow);
        this.soundscape.update(dt);
        if (input.mutePressed) this.showSoundSign(sfx.toggle());
        for (const w of [this.windowView, this.cabinView, this.roomView]) if (w?.view.visible) w.backdrop.update(dt, false, this.horizonOnScreen);
        // (What she sees a load through, the vase's flowers, every frame: the outside view holds the world still, and the
        // frame must be gone in it at once.)
        this.world?.carryBox.showView();
        // (Under the intro the game itself holds still: only the ship's side opens and shuts.)
        if (this.intro) {
            this.updateCutaway(dt);
            return;
        }
        // The outside view (O): the whole ship from outside, every deck closed, the game paused.
        // (Opened from a porthole by E: any movement key brings her back too, the user, 2026-11-23.)
        const moved = input.leftPressed || input.rightPressed || input.upPressed || input.downPressed || input.jumpPressed;
        if (input.outsidePressed || (this.overview && (input.escapePressed || (this.overview.porthole && moved)))) {
            if (this.overview) this.leaveOverview(); else this.enterOverview();
        }
        if (this.overview) {
            this.updateOverview(input, dt);
            return;
        }

        this.updateVacuums(dt);
        this.world.update(dt, time, input);
        // (A look-out's zoom moves the camera in the world's update: the far background laid again for it, or it lags a
        // frame behind the zoom and its edges show.)
        if (this.world.lookFar > 0) this.layBackdrop(0);
        this.loose.update(dt);
        if (this.mode === 'play') this.updatePlay(input, dt, time);
        else if (this.mode === 'push') this.updatePush(input, dt, time);
        else if (this.mode === 'ladder') this.updateLadder(input, dt, time);
        else if (this.mode === 'stairs') this.updateStairs(input, dt, time);
        else if (this.mode === 'trunk') this.updateTrunk(input, dt);
        else if (this.mode === 'lift') this.updateLift(input, dt);
        else if (this.mode === 'swim') this.updateSwim(input, dt);
        else if (this.script) this.script(dt, time);
        for (const pool of this.pools) pool.ripples.tilePositionX += dt * 6;
        this.closeTrunkDoors();
        this.closeLiftDoors();
        this.updateCutaway(dt);
        this.updateBulkhead();
        this.progress.update();

        // Inside a trunk or an elevator she is out of everyone's way.
        if (this.mode === 'play' || this.mode === 'ladder' || this.mode === 'stairs') this.checkPickups();
        if (this.mode === 'play' || this.mode === 'ladder' || this.mode === 'stairs') this.checkCheckpoints();
        if ((this.mode === 'play' || this.mode === 'ladder' || this.mode === 'stairs') && this.route === 'inside') {
            this.checkVacuums();
        }
        // Bumbot on her route: in the corridors, or asleep in the linen room.
        if (this.mode === 'play' || this.mode === 'ladder' || this.mode === 'stairs') this.checkBumbot();
        this.updateLunge(time);
        this.updatePocket(time);
        this.updateOverlays();
    }

    updatePlay(input, dt, time) {
        const p = this.player;
        const body = p.body;
        let onFloor = body.blocked.down || body.touching.down;
        // The sun cover's top is a curved floor she lands on from above and walks along, its height
        // known at every x: coming down onto it (her feet above it last frame, at or below it now)
        // she stands exactly on it, so her walk never stumbles down its curve (the user saw it with
        // stepped pieces). From below she passes through.
        // Standing on it last frame, she follows it down its curve too (it can drop faster under her
        // than she starts to fall).
        const top = this.coverTopAt(p.x);
        const was = this.feetWas ?? p.y;
        const landing = was <= top + 2 && p.y >= top - 1;
        const following = this.onCover && top - p.y >= 0 && top - p.y <= 6;
        if (!onFloor && top !== null && this.route === 'inside' && body.velocity.y >= 0 && (landing || following)) {
            const dy = top - p.y;
            p.y += dy;
            body.y += dy;
            body.velocity.y = 0;
            onFloor = true;
        }
        this.onCover = onFloor && top !== null && Math.abs(top - p.y) < 1;
        this.feetWas = p.y;

        if (onFloor) {
            if (!this.grounded) {
                sfx.land(this.soundscape.floor());
                // Down a deck or so on her feet (not a glide's soft landing): a small thud.
                if (!this.gliding && p.y - this.takeoffY > this.deckPitch * 0.6) rumble('land');
            }
            // (Not in the hop's first moment: her body can still report the floor she has just left.)
            if (this.overRail && time - this.overRailAt > 250) {
                this.overRail = false;
                p.setDepth(DEPTH.player);
            }
            if (this.gliding) {
                this.gliding = false;
                this.world.showParasol(false);
                sfx.parasolShut();
            }
            this.glideArmed = false;                 // (a press in the air, held on: only for that fall)
            this.grounded = true;
            this.airThrown = false;                  // (one throw a jump: hers again once she has landed)
            this.airThrowUntil = 0;
            this.lastGroundedAt = time;
            this.takeoffY = p.y;
        } else {
            this.grounded = false;
        }

        // A mishap in the air: it plays when she lands (docs/plan-three-uses.md §1.6).
        if (this.gagPending && this.grounded) {
            const g = this.gagPending;
            this.gagPending = null;
            this.flinchUntil = 0;
            this.mishap(g.sc, g.fromX, g.ride);
            return;
        }
        // A gull's take: her duck (or a hit in the air, waiting for her landing).
        if (time < this.flinchUntil) {
            if (this.gagPending && GAGS[this.gagPending.sc.gag]?.drop) body.velocity.x = 0;
            body.velocity.x = approach(body.velocity.x, 0, POCKET.slow * dt);
            return;
        }
        // (A throw in the air: off her hand on the swing, while she flies on.)
        if (this.throwing?.air && time >= this.throwing.at) this.releaseThrow();
        // Throwing (F): she stands for it, and the tangerine leaves her hand on the swing.
        if (time < this.throwUntil) {
            body.velocity.x = approach(body.velocity.x, 0, PLAYER.groundDecel * dt);
            if (this.throwing && time >= this.throwing.at) this.releaseThrow();
            return;
        }

        if (onFloor && input.activatePressed && this.world.interact()) return;
        if (onFloor && input.activatePressed && !this.holding && this.progress.tryPickup()) return;
        if (onFloor && input.activatePressed && !this.holding && this.tryShower()) return;
        if (onFloor && input.activatePressed && this.tryMirror()) return;
        if (onFloor && input.activatePressed && this.useRouteDoor()) return;
        if (onFloor && input.activatePressed && this.useBulkheadDoor()) return;
        // On the promenade, or in the cabin, the stairs, ladders, trunks and elevators are out of reach.
        const inside = this.route === 'inside';
        if (inside && onFloor && input.activatePressed && this.callLift()) return;
        // (With Bumbot in her arms: no trunks, no ladders, no hop over a rail.)
        const hands = !this.holding;
        if (hands && inside && onFloor && input.activatePressed) this.activateTrunkDoor();
        if (hands && inside && onFloor && (input.up || input.down) && this.tryTrunk(input)) return;
        // Held, not just pressed, so holding ↓ carries her on down the next flight at a landing.
        if (inside && onFloor && (input.up || input.down || input.left || input.right) && this.tryStairs(input)) return;
        if (hands && inside && (input.up || input.down) && this.tryLadder(input)) return;
        if (hands && (input.up || input.down) && this.world.tryLadder(input, onFloor)) return;
        // With the parasol: over an atrium walk's railing with ↓ and jump, to float down the atrium.
        if (onFloor && inside && input.down && input.jumpPressed && this.overTheRail()) return;
        // On the balconies, in the grip socks, Space at a partition is one of her three moves there (round it; with ↑ or
        // ↓, from anywhere on a balcony, up or down a partition's fin: src/world/balcony.js). Nothing takes her through
        // a balcony's floor or out over its rail.
        if (this.route === OUTSIDE) {
            this.balconyHints();
            if (hands && input.jumpPressed && this.tryBalcony(input)) return;
        }
        // Through a side walk with ↓ (inside: deck 12's walk over the pools).
        if (onFloor && this.route !== OUTSIDE && input.downPressed && this.dropThroughWalk()) return;

        if (input.dashPressed) this.tryCry(time);
        if (input.throwPressed && this.tryThrow(input, time, onFloor) && onFloor) return;

        // The verbs (§6.1.2, src/world/verbs.js): crawling under things, a kick off a wall in grip
        // socks, a glide under the parasol.
        const crawling = this.updateCrawl(input, onFloor);
        const aside = this.updateAside(input, onFloor);
        const lunging = this.isLunging();
        // (Waist deep in the kids' club's ball pit she wades: src/world/bow.js.)
        const speed = crawling ? VERBS.crawlSpeed : PLAYER.runSpeed * (lunging ? LUNGE.speed : 1) * (this.wading ? 0.5 : 1)
            * (this.holding ? HOLDING.speed : 1);
        let dir = aside ? 0 : (input.right ? 1 : 0) - (input.left ? 1 : 0);
        // (Her shrug at a block is cut short by a fresh step or a jump, not by a key held against the block: `shrug`.)
        if (this.idle === 'shrug' && (input.leftPressed || input.rightPressed || input.jumpPressed)) {
            this.idle = null;
            this.shrugDone();
        }
        // (The lunge carries her on the way she faces whether a way is held or not.)
        if (lunging && !dir && !aside) dir = p.flipX ? -1 : 1;
        if (time < this.kickUntil) dir = this.kickDir;      // a wall kick carries her off the wall a moment
        // On wet tiles without the grip socks (src/world/hazards.js) she slides on the way she came.
        const slipping = onFloor && !!this.slipDir;
        if (slipping) dir = this.slipDir;
        const accel = (onFloor ? (dir ? PLAYER.groundAccel : PLAYER.groundDecel) : PLAYER.airAccel) * (lunging ? 2 : 1);
        body.velocity.x = approach(body.velocity.x, dir * speed, accel * dt);
        if (dir) p.setFlipX(dir < 0);

        if (input.jumpPressed) this.jumpBufferedAt = time;
        // (The ice cream mix's canister is too heavy to hop with: §6.1.2.)
        const canJump = !crawling && !this.world.carry?.heavy && (onFloor || time - this.lastGroundedAt < PLAYER.coyoteMs);
        let jumped = false;
        if (canJump && time - this.jumpBufferedAt < PLAYER.jumpBufferMs) {
            body.velocity.y = -PLAYER.jumpVelocity * this.jumpScale();
            this.jumpBufferedAt = -Infinity;
            this.lastGroundedAt = -Infinity;
            jumped = true;
            if (this.jumpScale() < 1) sfx.hop(); else sfx.jump();
        } else if (!onFloor && this.tryWallJump(input, time)) {
            this.jumpBufferedAt = -Infinity;
            jumped = true;
        }
        // (A press in the air that was not a jump or a wall kick: the parasol's, `updateGlide`.)
        this.glidePress = !onFloor && !jumped && input.jumpPressed;
        if (input.jumpReleased && body.velocity.y < -PLAYER.jumpCutVelocity && !(time - this.kickedAt < 700)) {
            body.velocity.y = -PLAYER.jumpCutVelocity;
        }
        const sliding = !onFloor && this.updateWallSlide(dir);
        if (sliding && time > (this.slideSoundAt ?? 0)) {
            this.slideSoundAt = time + 170;
            sfx.wallSlide();
        }
        const gliding = !onFloor && this.updateGlide(input, dt);
        this.world.push(dt, onFloor);

        const pool = this.pools.find(w => p.x > w.x0 && p.x < w.x1 && p.y > w.y + SWIM.entry && p.y < w.bottom + 16);
        if (pool && this.holding) {
            // (Bumbot will not have it: back onto the side she came from.)
            const back = p.x - pool.x0 < pool.x1 - p.x ? pool.x0 - PLAYER.bodyWidth / 2 - 1 : pool.x1 + PLAYER.bodyWidth / 2 + 1;
            p.body.reset(back, pool.y);
            if (time > (this.mewAt ?? 0)) {
                this.mewAt = time + 2500;
                this.world.say(t('say.meow'), 900, { from: 'bumbot' });
                sfx.meow();
            }
        } else if (pool) return this.enterPool(pool);

        if (!onFloor) {
            if (p.x < this.hullMinX || p.x > this.hullMaxX) {
                if (p.y >= this.waterY) return this.scareOverboard();
            } else if (p.y - this.takeoffY > this.deckPitch + LONG_FALL_MARGIN) {
                return this.scareFall();
            }
        }

        if (crawling) this.poseCrawl(body.velocity.x);
        else if (aside) this.pose('back');
        else if (gliding) this.pose(this.anims.exists('her-glide') ? 'glide' : 'apex');
        else if (sliding) this.pose(this.herFrames.wallslide !== undefined ? 'wallslide' : 'fall');
        else if (!onFloor && time < this.kickUntil + 160 && this.herFrames.wallkick !== undefined) this.pose('wallkick');
        else if (!onFloor && time < this.airThrowUntil) {
            // (Her throw in the air plays over her jump; until its clip is approved, her jump's top stands in.)
            if (!this.anims.exists('her-airtoss')) this.pose('apex');
        }
        else if (!onFloor) this.pose(body.velocity.y < -60 ? 'rise' : body.velocity.y < 60 ? 'apex' : 'fall');
        else if (slipping) this.pose(this.herFrames.slip !== undefined ? 'slip' : 'apex');
        else if (Math.abs(body.velocity.x) > 10) this.pose('run', lunging ? 1.8 : Math.abs(body.velocity.x) / PLAYER.runSpeed);
        else this.standStill(time, dir);

        // Standing still on the bed long enough: she bounces on it.
        const still = onFloor && !dir && Math.abs(body.velocity.x) < 10 && !input.up && !input.down && !input.jump;
        if (!still) this.stillSince = time;
        else if (!this.holding && this.onBed() && time - (this.stillSince ?? time) > BED_JOY.idleMs) {
            // (Reading on it is E now, with any book she carries: `Library.read()`, the user, 2026-11-21.)
            if (!this.world.library.reading) this.startBedJoy();
        }
    }

    // --- Cabin 8206's shower (§5.3) ------------------------------------------------------------
    // The user's secret (2026-11-08): E at the shower room's door and it slides open; she steps in,
    // the door closes, and through its frosted glass she washes her hair, steam rising over it and
    // small notes as she sings; then she steps out with a towel round her head.

    // E in front of her crew cabin's standing mirror (it is at the room's forward wall, where she
    // stops): she turns to it and fixes her hair, once a press (the user, 2026-11-23: on E, no
    // longer by standing there).
    tryMirror() {
        const p = this.player, mirror = this.world.rooms[this.route]?.mirror;
        if (mirror === undefined || this.holding || this.world.carry || !this.anims.exists('her-hair')) return false;
        if (Math.abs(p.x - mirror) > MIRROR_REACH) return false;
        p.body.setVelocityX(0);
        p.setFlipX(true);                  // (the mirror is forward of her: to her left)
        this.idle = 'hair';
        p.anims.play('her-hair');
        this.stillSince = this.time.now;
        return true;
    }

    tryShower() {
        const c = this.cabin, p = this.player;
        if (!c || this.route !== 'cabin') return false;
        const [a, , b] = CABIN.shower;
        if (p.x < c.room.x + a - SHOWER.reach || p.x > c.room.x + b + SHOWER.reach) return false;
        this.startShower();
        return true;
    }

    startShower() {
        const c = this.cabin, p = this.player;
        const [a, top, b, bottom] = CABIN.shower;
        const x0 = c.room.x + a, y0 = c.room.y + top, floor = c.room.y + bottom - 2;
        const depth = c.room.depth + 0.001;
        const at = key => this.add.image(x0, y0, key).setOrigin(0).setDepth(depth).setVisible(false);
        // The stall's inside, her behind the glass, the glass; the door slid open.
        const s = this.showerScene = {
            inside: at('cabin-shower-inside'), open: at('cabin-shower-open').setDepth(depth + 0.003),
            glass: at('cabin-shower-glass').setDepth(depth + 0.002),
            her: this.add.sprite(x0 + (b - a) / 2 + 1, floor, 'her', this.herFrames.front).setOrigin(0.5, 1)
                .setDepth(depth + 0.001).setVisible(false),
        };
        this.worldLayer.add([s.inside, s.open, s.glass, s.her]);
        this.mode = 'scripted';
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        // The opening, where the door slid from: its right half. A towel on the handle slides with it.
        const doorway = x0 + (b - a) * 0.72;
        const towelX = c.towel.x;
        const shut = closed => {
            s.open.setVisible(!closed);
            c.towel.x = towelX - (closed ? 0 : CABIN.slide);
            sfx.doorSlide();
        };
        shut(false);
        let t = 0, phase = 'walk';
        this.script = dt => {
            t += dt * 1000;
            if (phase === 'walk') {
                const dx = doorway - p.x;
                if (Math.abs(dx) > 1) {
                    p.x += Math.sign(dx) * Math.min(Math.abs(dx), SHOWER.walkSpeed * dt);
                    p.setFlipX(dx < 0);
                    this.pose('run', 0.6);
                    return;
                }
                // Her back to us, and in she goes.
                this.pose('back');
                this.tweens.add({ targets: p, alpha: 0, duration: SHOWER.stepMs });
                phase = 'in';
                t = 0;
            } else if (phase === 'in' && t > SHOWER.stepMs) {
                p.setVisible(false).setAlpha(1);
                shut(true);
                [s.inside, s.glass, s.her].forEach(o => o.setVisible(true));
                s.her.anims.play('her-shower');
                sfx.shower(SHOWER.showerMs / 1000);
                phase = 'shower';
                t = 0;
            } else if (phase === 'shower' && t > SHOWER.showerMs) {
                shut(false);
                [s.inside, s.glass, s.her].forEach(o => o.setVisible(false));
                // Out she comes, facing us, the towel round her head (from the handle, if it was there).
                this.setTowel(true);
                c.towel.x = towelX;
                p.x = doorway;
                p.setFlipX(false).setVisible(true).setAlpha(0);
                this.pose('front');
                this.tweens.add({ targets: p, alpha: 1, duration: SHOWER.stepMs });
                phase = 'out';
                t = 0;
            } else if (phase === 'out' && t > SHOWER.stepMs + 450) {
                shut(true);
                this.endShower();
                return;
            }
            this.showerFx(x0, y0, b - a, phase === 'shower', dt);
        };
    }

    // Steam curling up over the stall and small notes rising from it while she sings (`on`); both
    // drift up and fade.
    showerFx(x0, y0, w, on, dt) {
        const s = this.showerScene;
        s.steamAt = (s.steamAt ?? 0) - dt * 1000;
        s.noteAt = (s.noteAt ?? SHOWER.noteEveryMs) - dt * 1000;
        if (!on) return;
        if (s.steamAt <= 0) {
            s.steamAt = SHOWER.steamEveryMs;
            const puff = this.add.circle(x0 + 4 + Math.random() * (w - 8), y0 + 2, 2 + Math.random() * 2, 0xffffff, 0.55)
                .setDepth(s.open.depth + 0.001);
            this.worldLayer.add(puff);
            this.tweens.add({
                targets: puff, y: puff.y - 18 - Math.random() * 10, x: puff.x + (Math.random() - 0.5) * 8,
                scale: 2.2, alpha: 0, duration: 1400, onComplete: () => puff.destroy(),
            });
        }
        if (s.noteAt <= 0) {
            s.noteAt = SHOWER.noteEveryMs;
            sfx.hum(s.notes = (s.notes ?? -1) + 1);
            const note = this.add.text(x0 + w / 2 + (Math.random() - 0.5) * w * 0.6, y0 - 2, Math.random() < 0.5 ? '\u266a' : '\u266b', {
                fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#45293f', resolution: 4,
            }).setOrigin(0.5, 1).setDepth(s.open.depth + 0.002);
            this.worldLayer.add(note);
            const sway = (Math.random() < 0.5 ? -1 : 1) * (6 + Math.random() * 6);
            this.tweens.add({ targets: note, y: note.y - 30, duration: 1800, ease: 'Sine.easeOut', onComplete: () => note.destroy() });
            this.tweens.add({ targets: note, x: note.x + sway, duration: 900, yoyo: true, ease: 'Sine.easeInOut' });
            this.tweens.add({ targets: note, alpha: 0, delay: 1000, duration: 800 });
        }
    }

    // On her way out with the towel on: it goes from her head onto the shower door's handle, a moment
    // to see it there, then out through the cabin's door as usual (the user, 2026-11-08: she doesn't
    // walk over to it).
    hangTowel() {
        const c = this.cabin, p = this.player;
        this.mode = 'scripted';
        p.body.setVelocity(0, 0);
        this.setTowel(false);
        this.pose('stand');
        c.towel.setAlpha(0);
        this.tweens.add({ targets: c.towel, alpha: 1, duration: 250 });
        this.script = null;
        this.time.delayedCall(SHOWER.hangMs, () => {
            this.mode = 'play';
            this.useRouteDoor();
        });
        return true;
    }

    endShower() {
        const p = this.player, s = this.showerScene;
        [s.inside, s.open, s.glass, s.her].forEach(o => o.destroy());
        this.showerScene = null;
        this.script = null;
        this.mode = 'play';
        p.body.enable = true;
        p.body.reset(p.x, p.y);
        this.pose('stand');
        this.stillSince = this.time.now;
    }

    // --- Bouncing on the cabin's bed (§5.3) ---------------------------------------------------

    onBed() {
        const c = this.cabin;
        return c && this.route === 'cabin' && Math.abs(this.player.y - c.bed.body.top) < 2;
    }

    // She turns to us and bounces on the bed for joy, in place, hopping from one foot to the other,
    // her arms waving up and down; any key and she stops. Her frames and her hops run off one
    // clock: off the bed with a foot up (frames 0 and 4), landing on both (2 and 6).
    startBedJoy() {
        const p = this.player;
        const y = p.y;
        const clip = this.anims.get(this.towel ? 'her-towel-bed-joy' : 'her-bed-joy');
        const frames = clip.frames.map(f => f.frame.name);
        p.setTexture(clip.frames[0].textureKey);
        this.mode = 'scripted';
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.anims.stop();
        p.setFlipX(false);
        let t = 0;
        this.script = dt => {
            const i = this.controls.state;
            if (i.left || i.right || i.up || i.down || i.jumpPressed || i.dashPressed || i.activatePressed) {
                this.endBedJoy(y);
                // (E stops her bouncing and does what E does on the bed: she sits down to read, `Library.read()`.)
                if (i.activatePressed) this.world.interact();
                return;
            }
            t += dt * 1000;
            const phase = (t % BED_JOY.cycleMs) / BED_JOY.cycleMs;
            p.setFrame(frames[Math.floor(phase * frames.length)]);
            // Each hop: on the bed a moment around the landing, in the air the rest, highest at its
            // middle, a foot up.
            const g = ((phase * 2) % 1 + 0.35) % 1;
            if (g >= BED_JOY.air && !(this.bedG >= BED_JOY.air)) sfx.boing();       // each landing: the springs
            this.bedG = g;
            p.y = g < BED_JOY.air ? y - Math.round(BED_JOY.hop * Math.sin(Math.PI * g / BED_JOY.air)) : y;
        };
    }

    endBedJoy(y) {
        const p = this.player;
        this.script = null;
        this.mode = 'play';
        p.y = y;
        p.body.enable = true;
        p.body.reset(p.x, p.y);
        this.pose('stand');
        this.stillSince = this.time.now;
    }

    // Standing still is her plain side pose; after a while one of her idles plays once (§3).
    standStill(time, dir) {
        const p = this.player;
        // (Her hair at her cabin's mirror plays on E: `tryMirror`.)
        // (Her shrug at a block plays on with a key held against it, facing us; then she faces the way she did.)
        if (this.idle === 'shrug') {
            if (p.anims.isPlaying && p.anims.currentAnim?.key === 'her-shrug') {
                p.setFlipX(false);
                return;
            }
            // (Cut short by her run, the run's own pace is hers now: nothing to give back.)
            if (p.anims.currentAnim?.key !== 'her-shrug') this.shrugScale = undefined;
            this.shrugDone(dir ? dir < 0 : this.shrugFacing);
        }
        if (this.idle) {
            if (p.anims.isPlaying && !dir) return;
            this.idle = null;
            this.idleAt = time + Phaser.Math.Between(IDLE.gapMs[0], IDLE.gapMs[1]);
        }
        if (dir || time < this.idleAt || this.world.carry) {
            if (dir) this.idleAt = Math.max(this.idleAt, time + IDLE.firstMs);
            this.pose('stand');
            return;
        }
        // (With Bumbot in her arms: she bends her head to him.)
        if (this.holding) {
            this.idle = 'stroke';
            p.anims.play('her-cat-stroke');
            return;
        }
        // Never the same one twice in a row.
        const choices = IDLE.anims.filter(name => name !== this.lastIdle);
        this.idle = this.lastIdle = Phaser.Utils.Array.GetRandom(choices);
        p.anims.play(`${this.towel ? 'her-towel' : 'her'}-${this.idle}`);
    }

    // --- Ladders ---------------------------------------------------------------------------

    ladderTileAt(x, y) {
        const t = this.ladderLayer.getTileAtWorldXY(x, y);
        return t && t.index > 0 ? t : null;
    }

    tryLadder(input) {
        const p = this.player;
        const tile = input.up ? this.ladderTileAt(p.x, p.y - HALF) : this.ladderTileAt(p.x, p.y + 2);
        if (!tile) return false;
        // Shut until something has happened (the bridge's hatch, §6.1.9), or no way with a tray.
        if (this.world.ladderShut(tile.pixelX + tile.width / 2, p.y)) return false;

        let top = tile.y;
        let bottom = tile.y;
        while (this.ladderLayer.getTileAt(tile.x, top - 1)?.index > 0) top--;
        while (this.ladderLayer.getTileAt(tile.x, bottom + 1)?.index > 0) bottom++;
        this.ladder = {
            x: tile.pixelX + tile.width / 2,
            topY: top * tile.height,
            bottomY: (bottom + 1) * tile.height,
        };

        this.mode = 'ladder';
        p.body.enable = false;
        p.x = this.ladder.x;
        p.setFlipX(false);
        this.pose('climb');
        this.ladderPose = 'climb';
        return true;
    }

    updateLadder(input, dt, time) {
        const p = this.player;
        const L = this.ladder;
        const v = (input.down ? 1 : 0) - (input.up ? 1 : 0);
        p.y = Phaser.Math.Clamp(p.y + v * PLAYER.climbSpeed * dt, L.topY, L.bottomY);
        if (L.ceil != null) {
            const hide = Math.max(0, Math.min(p.height, Math.round(L.ceil - (p.y - p.displayOriginY))));
            p.setCrop(0, hide, p.width, p.height - hide);
        }

        // Her hands reach to about head height. Once that is above the last rung there is nothing
        // to grab, so her hands come down: climbing out of the hatch, or starting down into it.
        // (Not on a ladder that goes on out of the picture, the lifeboat's: she climbs it all the way.)
        const handsAboveLadder = !L.out && p.y - PLAYER.height * 0.85 < L.topY;
        if (handsAboveLadder) {
            // Her hands stay on the hatch rim as she rises: head, shoulder, then waist height.
            const risen = (L.topY - (p.y - PLAYER.height * 0.85)) / (PLAYER.height * 0.85);
            const frames = this.climbOutFrames;
            this.pose('climb-out');
            p.setFrame(frames[Math.min(frames.length - 1, Math.floor(risen * frames.length))]);
            this.ladderPose = 'climb-out';
        } else {
            if (this.ladderPose !== 'climb') this.pose('climb');
            this.ladderPose = 'climb';
            if (v) p.anims.resume();
            else p.anims.pause();
        }

        const atTop = p.y <= L.topY;
        const atBottom = p.y >= L.bottomY;
        if (L.out && atTop && input.up) {
            L.out();
            return;
        }
        if (input.jumpPressed) {
            this.leaveLadderOrStairs();
            p.body.velocity.y = -PLAYER.jumpVelocity * 0.6;
            sfx.jump();
        } else if ((atTop && input.up) || (atBottom && input.down) || ((atTop || atBottom) && (input.left || input.right))) {
            this.leaveLadderOrStairs();
        }
    }

    // Onto a ladder that is not on the map's ladder layer (the lifeboat station's, outside).
    enterLadder(x, topY, bottomY, out = null, ceil = null) {
        const p = this.player;
        // (`out`: past its top she goes somewhere else, the lifeboat's ladder up into its hatch; `ceil`: her picture is
        // cut there, the ceiling she climbs through, the user, 2026-11-21: "she has to be cut off on top".)
        this.ladder = { x, topY, bottomY, out, ceil };
        this.mode = 'ladder';
        p.body.enable = false;
        p.x = x;
        p.setFlipX(false);
        this.pose('climb');
        this.ladderPose = 'climb';
        return true;
    }

    leaveLadderOrStairs() {
        const p = this.player;
        this.mode = 'play';
        this.downLatch = true;          // (a ↓ held from the climb does not crawl her: verbs.js `updateCrawl`)
        p.setCrop();
        p.setDepth(DEPTH.player);
        this.pose('stand');
        p.body.enable = true;
        p.body.reset(p.x, p.y);
        this.takeoffY = p.y;
    }

    // --- Pools (§5.3): she swims, breaststroke -------------------------------------------------

    enterPool(pool) {
        const p = this.player;
        if (this.world.carry) this.world.carryBox.spill(p.x - (p.flipX ? -1 : 1), true);   // her own doing
        this.mode = 'swim';
        this.pool = pool;
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        this.swimUp = 0;
        this.swimRest = 0;
        p.y = pool.y + SWIM.float;
        p.setDepth(DEPTH.swimmer);
        sfx.splash();
        this.splash(p.x, pool.y);
        this.pose('swim');
    }

    // Her height in the water: lying in her stroke the waterline is at her shoulders; upright she kneels on the pool's
    // floor, her head out (never lower than its floor as the water goes down the drain).
    swimY() {
        const pool = this.pool, lying = pool.y + SWIM.float, k = this.swimUp ?? 0;
        return Math.min(pool.bottom, lying + (pool.bottom - lying) * k * k * (3 - 2 * k));
    }

    // Her picture in the water, the one place it is set (the user, 2026-11-25: "I want her swimming animation
    // enriched"): her stroke while she moves; at rest the stroke runs out to its glide and holds there, and when she
    // is to come up (`wantUp`: she has rested `SWIM.restMs`, or a scene says so) she comes upright, `swimUp` from 0 to
    // 1 through her rise's frames, and bobs there; moving again, back down through the same frames. A scene's own
    // clip of her upright (her call) is left to play.
    swimShow(dt, wantUp, moving) {
        const p = this.player, A = p.anims;
        if (this.holding || this.towel || !this.anims.exists('her-swim-peek')) {
            this.swimUp = 0;
            this.pose('swim', moving ? 1 : 0.4);
            p.y = this.swimY();
            return;
        }
        let up = this.swimUp ?? 0;
        const key = A.currentAnim?.key;
        if (up <= 0) {
            if (key !== 'her-swim') this.pose('swim');
            const i = (A.currentFrame?.index ?? 1) - 1;
            A.timeScale = moving ? 1 : i === 0 ? 0 : wantUp ? SWIM.settle : 1;
            if (wantUp && !moving) {
                if (i === 0) up = 0.001;
                else if (SWIM.tucked.includes(i)) up = SWIM.tuckedAt;
                if (up > 0) sfx.splashSmall();
            }
        } else {
            up = Phaser.Math.Clamp(up + dt * 1000 * (wantUp && !moving ? 1 / SWIM.riseMs : -1 / SWIM.diveMs), 0, 1);
        }
        if (up >= 1) {
            if (key !== 'her-swim-tread' && !(key === 'her-swim-cry' && A.isPlaying)) {
                A.play('her-swim-tread');
                A.timeScale = 1;
            }
        } else if (up > 0) {
            const frames = this.anims.get('her-swim-peek').frames, n = Math.round(up * (frames.length - 1));
            if (key !== 'her-swim-peek' || A.currentFrame !== frames[n]) {
                A.play('her-swim-peek');
                A.pause(frames[n]);
            }
        } else if (this.swimUp > 0) {
            // (Back in her stroke, from its first frame.)
            A.play('her-swim');
            A.timeScale = moving ? 1 : 0;
        }
        this.swimUp = up;
        p.y = this.swimY();
        this.swimRings(moving);
    }

    // The water she disturbs: rings going out along the surface from where she breaks it (her shoulders in her
    // stroke, her neck upright), and the water she leaves behind her while she moves.
    swimRings(moving) {
        const p = this.player, pool = this.pool;
        if (!this.swimG) {
            this.swimG = this.add.graphics().setDepth(DEPTH.poolWater + 0.02);
            this.worldLayer.add(this.swimG);
        }
        const g = this.swimG.clear();
        if (!pool || pool.bottom - pool.y < 16) return;
        const t = this.time.now, y = Math.round(pool.y), f = p.flipX ? -1 : 1, up = this.swimUp ?? 0;
        const cx = p.x + f * 14 * (1 - up), half = 9 - 4 * up;
        for (let i = 0; i < 2; i++) {
            const k = (t / SWIM.ringMs + i * 0.5) % 1, r = half + 2 + k * 12, w = 3 + Math.round(k * 3);
            g.fillStyle(0xffffff, 0.85 * (1 - k)).fillRect(Math.round(cx - r - w), y, w, 1).fillRect(Math.round(cx + r), y, w, 1);
        }
        if (moving) {
            for (let i = 0; i < 3; i++) {
                const k = (t / 420 + i / 3) % 1;
                g.fillStyle(0xc7e7ff, 0.8 * (1 - k)).fillRect(Math.round(cx - f * (half + 8 + k * 26)) - 2, y + (i % 2), 4, 1);
            }
        }
    }

    // ←/→ swims along the pool; jump climbs out, onto the deck at its edge or back in the water.
    updateSwim(input, dt) {
        const p = this.player;
        const pool = this.pool;
        const dir = (input.right ? 1 : 0) - (input.left ? 1 : 0);
        if (dir) p.setFlipX(dir < 0);
        // (Coming down from upright she is not yet at her stroke's speed.)
        p.x = Phaser.Math.Clamp(p.x + dir * SWIM.speed * (1 - (this.swimUp ?? 0)) * dt, pool.x0 + SWIM.margin, pool.x1 - SWIM.margin);
        this.swimRest = dir ? 0 : (this.swimRest ?? 0) + dt * 1000;
        this.swimShow(dt, !dir && this.swimRest >= SWIM.restMs, !!dir);
        if (input.jumpPressed) {
            this.mode = 'play';
            this.swimUp = 0;
            this.swimG?.clear();
            this.pool = null;
            p.setDepth(DEPTH.player);
            p.y = pool.y - 2;
            p.body.enable = true;
            p.body.reset(p.x, p.y);
            p.body.velocity.y = -PLAYER.jumpVelocity;
            p.body.velocity.x = (p.flipX ? -1 : 1) * PLAYER.runSpeed * 0.6;
            this.takeoffY = pool.y;
            sfx.splashSmall();
            sfx.jump();
        }
    }

    // --- Side walks (§5.3) -----------------------------------------------------------------------

    // ↓ on deck 12's walk over the pools: she lets go over the railing and drops (into a pool, if
    // she is over one). Nowhere else: in the atrium ↓ only ever takes the stairs.
    dropThroughWalk() {
        const p = this.player;
        const walk = this.route === OUTSIDE ? this.world.dropFloorAt(p.x, p.y, this.progress.knows('parasol'))
            : this.walks.find(w => w.dropThrough && p.x >= w.x0 && p.x <= w.x1 && Math.abs(p.y - w.y) < 2);
        if (!walk) return false;
        this.droppingThrough = walk;
        // (Outside with the parasol: over the balcony's rail, so that under it she floats on down
        // past the balconies below, and lands on one when she closes it.)
        this.overRail = this.route === OUTSIDE && this.progress.knows('parasol');
        this.overRailAt = this.time.now;
        p.body.velocity.y = -PLAYER.jumpVelocity * 0.35;
        this.time.delayedCall(450, () => { if (this.droppingThrough === walk) this.droppingThrough = null; });
        return true;
    }

    // With the parasol, ↓ and jump on one of the atrium's walks: a hop over its glass railing, out
    // over the atrium. Under the open parasol she floats down in front of the walks below, all the
    // way to the atrium's floor; closing it, she comes down on the next walk.
    overTheRail() {
        const p = this.player;
        if (!this.progress.knows('parasol') || this.world.carry || this.holding) return false;
        const walk = this.walks.find(w => w.atrium && p.x >= w.x0 + 24 && p.x <= w.x1 - 24 && Math.abs(p.y - w.y) < 2);
        if (!walk) return false;
        this.overRail = true;
        this.overRailAt = this.time.now;
        this.droppingThrough = walk;
        if (this.crawling) this.setCrawl(false);
        p.setDepth(DEPTH.fx - 0.5);
        p.body.velocity.y = -PLAYER.jumpVelocity * 0.5;
        this.jumpBufferedAt = -Infinity;
        this.lastGroundedAt = -Infinity;
        this.time.delayedCall(900, () => { if (this.droppingThrough === walk) this.droppingThrough = null; });
        sfx.jump();
        return true;
    }

    // --- The outer shell's cut-away (§5.3) -----------------------------------------------------

    deckOfRow(row) {
        for (const [deck, floor] of Object.entries(this.deckFloors)) {
            if (row <= floor && row > floor - this.deckPitch / 16) return Number(deck);
        }
        return null;
    }

    deckOfY(y) {
        return this.deckOfRow(Math.floor((y - 1) / 16));
    }

    // Where she is, in decks, as a number: whole on a deck's floor, between two while she climbs
    // stairs, a ladder or a trunk, or rides an elevator, so the cut-away crossfades with her.
    deckAt(y) {
        const floors = Object.entries(this.deckFloors).map(([d, r]) => [Number(d), r * 16]).sort((a, b) => b[1] - a[1]);
        for (let i = 0; i < floors.length - 1; i++) {
            const [d, f] = floors[i];
            const above = floors[i + 1][1];
            if (y <= f && y >= above) return d + (f - y) / (f - above);
        }
        return y > floors[0][1] ? floors[0][0] : floors[floors.length - 1][0];
    }

    updateCutaway(dt) {
        const p = this.player;
        const moving = this.mode === 'stairs' || this.mode === 'ladder' || this.mode === 'trunk'
            || (this.mode === 'lift' && this.liftMove?.carriesHer) || (this.mode === 'play' && this.overRail && this.route === 'inside');
        let target;
        // Outside on the promenade every deck shows its shell; and outdoors where there is no way in
        // (deck 7's stern strip, the aft terraces). In a room (cabin 8206, the linen room) the deck
        // stays cut open, the room over it.
        const outdoors = this.outdoors?.find(a => p.x >= a.x0 && p.x <= a.x1 && p.y <= a.floor + 4 && p.y > a.floor - this.deckPitch);
        for (const a of this.outdoors || []) a.cover.setVisible(a === outdoors);
        // A room shown in the deck's own place (the linen room) keeps the deck cut open.
        const inDeck = this.route === 'inside' || this.rooms.some(r => r.route === this.route && r.inDeck);
        // (`viewOverride`: the camera is away from her, looking at a deck: the horn's scene.)
        if (this.viewOverride != null) target = this.viewOverride;
        // (A look-out's zoom out shows the ship from outside: every deck closed, as in the outside view.)
        else if (this.world?.lookFar > 0) target = null;
        else if (!inDeck || outdoors || this.overview || this.fromAfar || p.y <= this.world.roofY + 2) target = null;
        // (`world.deckHeld`: up the bridge's hatch the bridge stays open until she is out on the balcony over it; by her
        // height its side closed over her legs half way up.)
        else if (moving) target = this.world?.deckHeld?.() ?? this.deckAt(p.y);
        else if (this.mode === 'swim') target = this.deckAt(this.pool.y);
        // (In the shaft, in the slab between two decks: the deck it sets out from, the one below opened by `world.lookOpen`.)
        else if (this.route === 'duct') target = this.world.data.duct.deck;
        else if (this.mode === 'scripted' && p.y >= this.waterY - 4) target = null;  // overboard: all shell
        else if (this.mode === 'play' && !(p.body.blocked.down || p.body.touching.down)) target = this.viewDeck;  // in the air
        // (And falling from a scare in the air, as she was: the decks she drops past stay closed; cut open
        // one by one, the parts of the side at the bow came and went, the user, 2026-11-18.)
        else if (this.airScare) target = this.viewDeck;
        else target = Math.round(this.deckAt(p.y));
        if (target === null || target === undefined) {
            this.viewDeck = null;
        } else if (this.viewDeck === null || moving) {
            this.viewDeck = target;
        } else {
            this.viewDeck = approach(this.viewDeck, target, dt * 4);
        }
        // In a room with its own shell (the bridge), only it is cut away; elsewhere it stays closed
        // (when the parts are locked: `LOCKED_PARTS`; for now it opens with its deck).
        const room = this.route !== 'inside' || this.overview ? null : this.shellRooms.find(r => p.x >= r.x0 && p.x < r.x1
            && p.y <= this.deckFloors[r.deck] * 16 + 4 && p.y > this.deckFloors[r.deck] * 16 - this.deckPitch);
        for (const deck of Object.keys(this.shellTiles)) {
            let alpha = this.viewDeck === null ? 1 : Phaser.Math.Clamp(Math.abs(parseInt(deck, 10) - this.viewDeck), 0, 1);
            const ownRoom = this.shellRooms.find(r => r.key === deck);
            if (LOCKED_PARTS.on && (ownRoom ? ownRoom !== room : room && String(room.deck) === deck)) alpha = 1;
            // (A look-out opens the deck its view is of, with the camera's way to it, and a drop under it the decks she
            // falls through: `world.lookOpen`, 0 to 1. A crossfade from the hull dimmed to the deck's inside, never the
            // hull undimmed (the user, 2026-11-23): the hull's alpha here, its dim in `updateDeckDim`.)
            const look = this.viewDeck !== null && this.world?.lookOpen?.[deck];
            if (look) alpha = Math.min(alpha, (1 - look) * (1 - ROOM_DIM) / ((1 - look) * (1 - ROOM_DIM) + look));
            // A room's shell and its deck's swap with a quick fade as she goes through its door.
            if (dt > 0 && (ownRoom || this.shellRooms.some(r => String(r.deck) === deck))) {
                alpha = approach(this.shellAlpha[deck], alpha, dt * 6);
            }
            if (Math.abs(alpha - this.shellAlpha[deck]) < 0.02 && alpha !== 0 && alpha !== 1) continue;
            if (alpha === this.shellAlpha[deck]) continue;
            this.shellAlpha[deck] = alpha;
            for (const t of this.shellTiles[deck]) t.alpha = alpha;
            this.cutShadows[deck].setAlpha(1 - alpha);
        }
        for (const { deck, gfx } of this.deckFronts || []) gfx.setAlpha(1 - (this.shellAlpha[deck] ?? 0));
        for (const { key, item } of this.insideFronts || []) item.setAlpha(1 - (this.shellAlpha[key] ?? 0));
        const under = `${this.underPools(11)},${this.underPools(12)}`;
        if (under !== this.poolsHidden) {
            this.poolsHidden = under;
            for (const t of this.poolTiles) t.alpha = this.underPools(t.poolDeck) ? 0 : 1;
            for (const [deck, g] of Object.entries(this.poolTanks)) g.setVisible(!this.underPools(Number(deck)));
            for (const pool of this.pools) [pool.water, pool.ripples].forEach(s => s.setVisible(!this.underPools(pool.deck)));
            // (What the world draws in a tank, the first pool's ladder, grate and hatch: `world.poolPieces`.)
            for (const e of this.world?.poolPieces ?? []) e.obj.setVisible(e.want && !this.underPools(e.deck));
        }
        // (The strips of the ship's wall drawn over her at a deck's ends: not over a room she is in.)
        this.endCoverGfx.setVisible(this.route === 'inside' || this.route === OUTSIDE);
        for (const r of this.rooms) {
            // (`roomFade`: a room's picture and its dim held at an alpha of their own, whatever her route, while a scene
            // crossfades it with the hull: the laundry chute, src/world/story.js.)
            const f = this.roomFade?.[r.route];
            const on = f !== undefined ? f > 0 : this.route === r.route;
            for (const [o, show] of [[r.room, on || (f === undefined && this.route === r.also)], [r.dim, on], [r.front, on]]) {
                if (!o) continue;
                o.setVisible(show && !this.overview && !this.fromAfar);
                o.alpha = f ?? 1;
            }
        }
        this.world?.shaftAway?.(!!this.overview || !!this.fromAfar);
        // Inside a boat (the lifeboat, a room entered from outside), the boat's own picture and its hatch, drawn in
        // front of her outside, are not drawn over its inside (the user, 2026-11-21: "the inside of the boat is now
        // not shown").
        const boatRoom = this.overview || this.fromAfar ? null : this.rooms.find(r => r.route === this.route && r.inDeck === false);
        for (const b of this.boatPics || []) {
            b.setVisible(!boatRoom || b.x + b.width <= boatRoom.room.x || b.x >= boatRoom.room.x + boatRoom.room.width);
        }
        for (const r of this.rooms) if (r.inDeck === false) r.outside?.forEach(o => o.setVisible(r !== boatRoom && !r.hidden));
        this.walkRail?.setDepth(boatRoom ? DEPTH.exterior + 0.06 : WALK_RAIL_DEPTH);
        this.updateRoofGlow(dt);
        this.cabin?.view.setVisible(this.route === 'cabin' && !this.overview);
        this.roomView?.view.setVisible(!this.overview && !!this.rooms.find(r => r.route === this.route)?.windows);
        this.cabin?.towel.setVisible(this.route === 'cabin' && !this.overview && !!this.save.towelHung);
        for (const cat of this.cats) {
            if (cat.route !== 'inside') cat.sprite.setVisible(cat.route === this.route && !cat.away && !cat.hidden);
        }
        for (const t of this.tangerines) {
            if (t.route !== 'inside' && t.sprite.active) [t.sprite, t.glint].forEach(s => s.setVisible(t.route === this.route));
        }
        const shown = deck => deck === null ? 1 : this.shellAlpha[deck] ?? 1;
        // (Inside a room on a deck with balconies, that deck's balcony fronts and partitions, drawn over her, are not drawn
        // across the room: they ran over the balcony cabins' insides, the user, 2026-11-24. Round the room the dim hides
        // them anyway.)
        const roomIn = this.rooms.find(r => r.route === this.route && r.room?.visible);
        const roomDeck = roomIn ? this.deckOfY(p.y) : null;
        for (const { deck, gfx, always, balcony } of this.shellSlopes) {
            gfx.setAlpha(balcony && deck === roomDeck ? 0
                : always ? 1 : Array.isArray(deck) ? Math.min(...deck.map(shown)) : shown(deck));
        }
        // (The deck she stands on, or last stood on while she is in the air or falling from a scare: gliding
        // down past the bow, the decks' leaning railings at their forward ends showed on the closed side one
        // after another as she passed their heights, the user, 2026-11-18.)
        const air = this.airScare || (this.mode === 'play' && !(p.body.blocked.down || p.body.touching.down));
        if (!air || this.floorDeck === undefined) this.floorDeck = this.deckOfY(p.y);
        const onDeck = this.floorDeck;
        for (const { deck, img } of this.leaningRailings || []) img.setAlpha(onDeck === deck ? 1 : 1 - shown(deck));
        // (A plate always drawn in front of her, an open deck's that stays closed, covers them as it is.)
        for (const { slope, img } of this.underSlopes || []) {
            const depth = slope.always || shown(slope.deck) === 0 ? DEPTH.player + 0.04 : DEPTH.exterior - 0.01;
            if (img.depth !== depth) img.setDepth(depth);
        }
        // On the promenade's deck (deck 6, outside) her lowest row is left off (the user, 2026-11-20: "Hide the
        // bottom line of her feet on the promenade"): her picture cut that many rows short while she stands there.
        const pr = this.promenade;
        const onProm = !!pr && this.route === 'promenade' && Math.abs(p.y - pr.floor) < 2 && p.x >= pr.x0 && p.x <= pr.x1;
        if (pr) pr.edge.setVisible(this.route === 'promenade');
        if (onProm) p.setCrop(0, 0, PLAYER.cell, PLAYER.cell - PLAYER.sink);
        else if (this.promCrop) p.setCrop();
        this.promCrop = onProm;
        // On the boat walkway (deck 7's height, outside, up to deck 8's balconies) her picture is drawn `WALK_LIFT` px
        // higher, her body where it is; changed only while she plays (a gag sets her picture its own way).
        const top7 = pr && pr.floor - this.deckPitch;
        const onWalk = !!pr && this.route === 'promenade' && p.y <= top7 + 2 && p.y > top7 - this.deckPitch + 2 && p.x >= pr.x0 && p.x <= pr.x1;
        if (this.mode === 'play') {
            const px = this.herDropPx() - PLAYER.sink;
            if (onWalk && px !== -WALK_LIFT) this.herDrop(-WALK_LIFT);
            else if (!onWalk && px === -WALK_LIFT) this.herDrop(0);
            // (And in the first pool's dry tank a few px lower, on its floor's strip of tiles: `world.tankDrop`.)
            const tank = onWalk ? 0 : this.world.tankDrop?.(p) ?? 0;
            if (!onWalk && (tank || this.tankDropped) && px !== tank) this.herDrop(tank);
            this.tankDropped = tank > 0;
        }
        // On a balcony her picture is cut at its partitions and at a row's end (`balconyRoom`): what reached past
        // one showed on the next balcony or over the ship's side (the user, 2026-11-21). (Phaser 4 crops a picture
        // turned by `flipX` with its content shifted by width - 2 x - w: so while she is on a balcony a stand-in of
        // her is drawn, turned by its scale, which crops true, and her own picture is cropped to nothing.)
        // (And on the boat walkway at its two ends, where it meets the ship's side: the user, 2026-11-21, "the same way
        // we fixed this issue on the balconies".)
        // (And at the linen room's shaft, until the view has gone over to the shaft: nothing of her past the room's wall
        // while the room is what is shown; the user, 2026-11-24: "She should be shown inside only when the camera
        // transitioned to the shaft". `world.herCut`.)
        const onBalcony = !onProm && p.visible && this.route === OUTSIDE ? this.world.balconyRoom(p.x, p.y) : null;
        const balc = !onProm && p.visible ? (this.route === OUTSIDE ? onBalcony ?? (onWalk ? [pr.x0, pr.x1] : null)
            : this.world.herCut?.() ?? null) : null;
        // (On a balcony, once the grip socks are hers, she wears them: the same frames of her sheet in the socks.)
        const key = onBalcony && p.texture.key === 'her' && this.progress.knows('socks') ? 'her-socks' : p.texture.key;
        const pic = this.balconyPic;
        if (balc) {
            const left = p.x - p.displayOriginX, rw = p.width;
            const a = Math.max(0, balc[0] - left), b = Math.min(rw, balc[1] - left);
            const q = this.balconyPic ??= this.add.image(0, 0, p.texture.key);
            if (!this.worldLayer.list.includes(q)) this.worldLayer.add(q);
            // (Scaled by -1 a picture turns about its origin; `flipX` keeps it in place: x moved to match.)
            q.setTexture(key, p.frame.name).setDisplayOrigin(p.displayOriginX, p.displayOriginY)
                .setPosition(p.flipX ? p.x - 2 * p.displayOriginX + rw : p.x, p.y).setScale(p.flipX ? -1 : 1, 1)
                .setAlpha(p.alpha).setDepth(p.depth).setVisible(b > a);
            for (const k of ['tint', 'tint2', 'tintMode', 'tintTopLeft', 'tintTopRight', 'tintBottomLeft', 'tintBottomRight']) {
                if (k in p && q[k] !== p[k]) q[k] = p[k];
            }
            // (A third number: a row of the world over which nothing of her is drawn, the bridge's hatch's mouth.)
            const top = balc[2] == null ? 0 : Phaser.Math.Clamp(Math.round(balc[2] - (p.y - p.displayOriginY)), 0, p.height);
            q.setCrop(p.flipX ? rw - b : a, top, Math.max(0, b - a), p.height - top);
            Phaser.Utils.Array.MoveAbove(this.worldLayer.list, q, p);
            p.setCrop(0, 0, 0, 0);
        } else if (this.balconyCrop) {
            pic?.setVisible(false);
            if (!onProm) p.setCrop();
        }
        this.balconyCrop = !!balc;
        this.updateDeckDim(dt);
    }

    // --- Escape trunks (§5.1) -----------------------------------------------------------------

    trunkDoorAt(x, y) {
        for (const t of this.trunks) {
            if (Math.abs(x - t.x) > 10) continue;
            const door = t.doors.find(d => Math.abs(y - d.y) < 4);
            if (door) return door;
        }
        return null;
    }

    // E at a trunk door opens it, if her cards and the trunk allow it from this side.
    activateTrunkDoor() {
        const door = this.trunkDoorAt(this.player.x, this.player.y);
        if (!door || door.open) return;
        if (this.world.carry) {
            this.world.say('🪜 ✋');           // a ladder: not with her hands full
            return;
        }
        if (!this.hasCard(door.trunk.card)) {
            this.showLocked(door.trunk.card);
        } else if (!this.trunkUsableFrom(door)) {
            sfx.rattle();
            this.tweens.add({ targets: door.sprite, x: door.trunk.x + 1, duration: 40, yoyo: true, repeat: 2 });
        } else {
            this.openTrunkDoor(door);
        }
    }

    openTrunkDoor(door) {
        door.open = true;
        door.sprite.setTexture('trunk-open');
        sfx.doorHeavy();
    }

    // A door shuts by itself once she has stepped away from it, or climbed out of its doorway.
    closeTrunkDoors() {
        const p = this.player;
        for (const t of this.trunks) {
            for (const d of t.doors) {
                if (!d.open) continue;
                const keep = this.mode === 'trunk'
                    ? this.inTrunk === t && p.y > d.y - DOOR.height && p.y - PLAYER.height < d.y
                    : Math.abs(p.x - t.x) < 22 && Math.abs(p.y - d.y) < 40;
                if (keep) continue;
                d.open = false;
                d.sprite.setTexture('shipart', 'door-crew');
                sfx.at(d.sprite.x, d.y).doorShut();
            }
        }
    }

    // At an open door, ↑/↓ takes the ladder behind it, in a direction it goes from there.
    tryTrunk(input) {
        const p = this.player;
        const door = this.trunkDoorAt(p.x, p.y);
        if (!door?.open) return false;
        const t = door.trunk;
        if ((input.up && door.y === t.top) || (input.down && door.y === t.bottom)) return false;

        this.mode = 'trunk';
        this.inTrunk = t;
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.x = t.x;
        p.y = door.y;
        p.setFlipX(false).setDepth(DEPTH.props + 0.5);
        this.pose('climb');
        this.showInDoorways();
        return true;
    }

    updateTrunk(input, dt) {
        const p = this.player;
        const t = this.inTrunk;
        const v = (input.down ? 1 : 0) - (input.up ? 1 : 0);
        const y0 = p.y;
        const doorNear = () => t.doors.find(d => Math.abs(p.y - d.y) < PLAYER.trunkSettle);

        if (v) p.y = Phaser.Math.Clamp(p.y + v * PLAYER.climbSpeed * dt, t.top, t.bottom);
        else if (doorNear()) p.y = approach(p.y, doorNear().y, PLAYER.climbSpeed * dt); // settles level with it
        if (p.y !== y0) p.anims.resume();
        else p.anims.pause();

        // Reaching a door opens it from inside: ←/→ steps out, or she climbs on and it shuts behind her.
        const door = doorNear();
        if (door && !door.open) this.openTrunkDoor(door);
        const side = (input.right ? 1 : 0) - (input.left ? 1 : 0);
        if (side && door) this.stepOutOfTrunk(door, side);
        else this.showInDoorways();
    }

    // She steps out of an open door onto that deck. Coming out below the top of a one-way trunk
    // opens it for good.
    stepOutOfTrunk(door, side) {
        const p = this.player;
        const t = door.trunk;
        if (!t.opened && door.y !== t.top) {
            t.opened = true;
            this.save.opened.push(t.id);
            this.lightTrunk(t);
        }
        this.inTrunk = null;
        p.y = door.y;
        p.setCrop().setVisible(true).setFlipX(side < 0);
        this.leaveLadderOrStairs();
        this.grounded = true;
    }

    // Inside, the walls and decks hide her (no cutaway, §5.1): she shows only through an open
    // doorway. Doorways are further apart than she is tall, so at most one shows her at a time.
    showInDoorways() {
        const p = this.player;
        const cell = PLAYER.cell;
        const left = p.x - cell / 2;
        const top = p.y - cell;
        for (const d of this.inTrunk.doors) {
            if (!d.open) continue;
            const doorLeft = d.trunk.x - DOOR.width / 2;
            const x0 = Math.max(left, doorLeft + TRUNK_INSIDE.x0);
            const x1 = Math.min(left + cell, doorLeft + TRUNK_INSIDE.x1);
            const y0 = Math.max(top, d.y - DOOR.height + TRUNK_INSIDE.y0);
            const y1 = Math.min(top + cell, d.y);
            if (x1 > x0 && y1 > y0) {
                p.setVisible(true).setCrop(x0 - left, y0 - top, x1 - x0, y1 - y0);
                return;
            }
        }
        p.setVisible(false);
    }

    // --- Elevators (§5.1) ----------------------------------------------------------------------

    liftAt(x, y) {
        for (const lift of this.lifts) {
            if (Math.abs(x - lift.x) > 14 || lift.busy) continue;
            const i = lift.floors.findIndex(f => Math.abs(y - f.y) < 4);
            if (i >= 0) return { lift, i };
        }
        return null;
    }

    // The doors on floor i: a core elevator's landing doors, or the glass car's own when it is there.
    leavesAt(lift, i) {
        if (!lift.glass) return lift.floors[i].leaves;
        return lift.at === i ? lift.leaves : null;
    }

    slideLeaves(leaves, y, to, done) {
        this.tweens.killTweensOf(leaves);
        if (leaves.open === to) {
            done?.();
            return;
        }
        sfx.at(leaves.right.x, y).doorSlide();
        this.tweens.add({
            targets: leaves, open: to, duration: LIFT.doorMs * Math.abs(to - leaves.open),
            onUpdate: () => this.setLeaves(leaves, y, leaves.open),
            onComplete: () => { this.setLeaves(leaves, y, to); done?.(); },
        });
    }

    // E at the doors: they open and the button panel shows; first, if the car is on another deck,
    // it comes to fetch her, the panel's display counting it in.
    callLift() {
        const p = this.player;
        const spot = this.liftAt(p.x, p.y);
        if (!spot) return false;
        const { lift, i } = spot;
        this.mode = 'lift';
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        this.pose('stand');
        this.liftRun = { lift, here: i, cursor: i, choosing: false };
        this.showLiftPanel();
        const open = () => this.slideLeaves(this.leavesAt(lift, i), lift.floors[i].y, 1, () => { this.liftRun.choosing = true; });
        // A car on another deck comes to fetch her first, seen or (in a core) out of sight, so every
        // ride starts from where she stands.
        if (lift.at !== i) this.moveCar(lift, i, false, open);
        else open();
        return true;
    }

    updateLift(input, dt) {
        if (this.liftMove) {
            this.stepCar(dt);
            return;
        }
        const run = this.liftRun;
        if (!run?.choosing) return;
        const floors = run.lift.floors;
        if (input.upPressed || input.downPressed) {
            // Only the decks she can reach light up; the cursor skips the rest.
            const step = input.upPressed ? -1 : 1;
            let c = run.cursor + step;
            while (c >= 0 && c < floors.length && !this.progress.regionOpen(floors[c].region)) c += step;
            if (c >= 0 && c < floors.length) run.cursor = c;
            this.refreshLiftPanel();
        } else if (input.activatePressed) {
            if (run.cursor === run.here) this.leaveLift();
            else this.ride();
        } else if (input.left || input.right) {
            this.leaveLift();
        }
    }

    // Back to play. The doors stay open until she steps away.
    leaveLift() {
        const p = this.player;
        this.hideLiftPanel();
        this.liftRun = null;
        this.mode = 'play';
        p.setDepth(DEPTH.player);
        this.pose('stand');
        p.body.enable = true;
        p.body.reset(p.x, p.y);
        this.takeoffY = p.y;
    }

    // She steps in and turns to us, the doors close, the car goes, a ding, and they open. The panel
    // goes once a deck is chosen: the camera following the car shows the ride.
    ride() {
        const run = this.liftRun;
        const { lift, here, cursor } = run;
        const p = this.player;
        run.choosing = false;
        this.hideLiftPanel();
        p.setFlipX(lift.x < p.x);
        this.pose('run', 0.6);
        this.tweens.add({
            targets: p, x: lift.x, duration: 150,
            onComplete: () => {
                p.setDepth(lift.glass ? DEPTH.inGlassCar : DEPTH.inLift);
                this.pose('front');
                this.slideLeaves(this.leavesAt(lift, here), lift.floors[here].y, 0, () => {
                    if (!lift.glass) p.setVisible(false); // a core car travels out of sight
                    this.moveCar(lift, cursor, true, () => {
                        p.setVisible(true);
                        sfx.liftDing();
                        this.slideLeaves(this.leavesAt(lift, cursor), lift.floors[cursor].y, 1, () => this.leaveLift());
                    });
                });
            },
        });
    }

    moveCar(lift, to, carriesHer, arrive) {
        if (lift.glass) this.setLeaves(lift.leaves, lift.carY, 0);
        this.liftMove = { lift, to, carriesHer, arrive };
        const s = Math.abs(lift.floors[to].y - lift.carY) / LIFT.speed;
        if (s > 0.2) (carriesHer ? sfx : sfx.at(lift.x, lift.carY)).liftMove(s);
    }

    stepCar(dt) {
        const m = this.liftMove;
        const lift = m.lift;
        const target = lift.floors[m.to].y;
        lift.carY = approach(lift.carY, target, LIFT.speed * dt);
        if (lift.glass) this.placeCar(lift);
        if (m.carriesHer) this.player.y = lift.carY;
        this.refreshLiftPanel();
        if (lift.carY !== target) return;
        lift.at = m.to;
        this.liftMove = null;
        m.arrive();
    }

    // Doors left open shut once she has stepped away from them.
    closeLiftDoors() {
        if (this.mode === 'lift') return;
        const p = this.player;
        for (const lift of this.lifts) {
            lift.floors.forEach((f, i) => {
                const leaves = this.leavesAt(lift, i);
                if (!leaves || leaves.open === 0 || this.tweens.isTweening(leaves)) return;
                const near = this.mode === 'play' && Math.abs(p.x - lift.x) < 26 && Math.abs(p.y - f.y) < 40;
                if (!near) this.slideLeaves(leaves, f.y, 0);
            });
        }
    }

    // The button panel: a display counting the decks, then a button per deck. The ones she can
    // reach are lit, the rest greyed out; a dot marks where the car is.
    showLiftPanel() {
        this.hideLiftPanel();
        const floors = this.liftRun.lift.floors;
        const rowH = 32;
        const w = 76;
        const h = floors.length * rowH + 60;
        const x = VIEW.width / 2 + 120;
        const y = (VIEW.height - h) / 2;
        const items = [this.add.rectangle(x, y, w, h, 0xc9ced3).setOrigin(0).setStrokeStyle(3, 0x5b6470)];
        const display = this.add.text(x + w / 2, y + 26, '', {
            fontFamily: 'monospace', fontSize: '22px', color: '#f28c28', backgroundColor: '#14161c',
            padding: { x: 8, y: 2 },
        }).setOrigin(0.5);
        items.push(display);
        const buttons = floors.map((f, i) => {
            const by = y + 60 + i * rowH + rowH / 2;
            const circle = this.add.circle(x + w / 2 + 6, by, 12);
            const label = this.add.text(x + w / 2 + 6, by, String(f.deck), {
                fontFamily: 'Verdana, sans-serif', fontSize: '13px', fontStyle: 'bold',
            }).setOrigin(0.5);
            const dot = this.add.circle(x + 14, by, 4, 0xf28c28);
            items.push(circle, label, dot);
            return { circle, label, dot };
        });
        this.uiLayer.add(items);
        this.liftPanel = { items, buttons, display };
        this.refreshLiftPanel();
    }

    refreshLiftPanel() {
        const panel = this.liftPanel;
        if (!panel || !this.liftRun) return;
        const { lift, cursor } = this.liftRun;
        const carAt = lift.floors.reduce((best, f, i) =>
            (Math.abs(f.y - lift.carY) < Math.abs(lift.floors[best].y - lift.carY) ? i : best), 0);
        panel.buttons.forEach((b, i) => {
            const ok = this.progress.regionOpen(lift.floors[i].region);
            const chosen = i === cursor;
            b.circle.setFillStyle(chosen ? 0xf28c28 : ok ? 0x5b6470 : 0x9aa3ad)
                .setStrokeStyle(2, chosen ? 0xffd98a : ok ? 0x2a2f36 : 0xb0b7be);
            b.label.setColor(chosen ? '#1d2b53' : ok ? '#ffffff' : '#c9ced3');
            b.dot.setVisible(i === carAt);
        });
        const target = this.liftMove ? lift.floors[this.liftMove.to].y : lift.carY;
        const arrow = target < lift.carY ? '▲' : target > lift.carY ? '▼' : ' ';
        panel.display.setText(`${arrow}${lift.floors[carAt].deck}`.padStart(3, ' '));
    }

    hideLiftPanel() {
        this.liftPanel?.items.forEach(item => item.destroy());
        this.liftPanel = null;
    }

    // --- Stairs ----------------------------------------------------------------------------

    tryStairs(input) {
        const p = this.player;
        const reach = PLAYER.stairsBoardReach;
        for (const f of this.flights) {
            // The funnel's stairway is what is in front of her, out on the funnel: walked into, she is
            // on it (the user, 2026-11-18: walking left off its top she dropped past it). Inside, a flight
            // is behind the floor she walks along, and only ↑ or ↓ takes her onto it.
            const down = Math.sign(f.bottom.x - f.top.x);
            const walkUp = f.outside && !input.down && (down < 0 ? input.right : input.left);
            const walkDown = f.outside && !input.up && (down < 0 ? input.left : input.right);
            if ((input.up || walkUp) && Math.abs(p.x - f.bottom.x) < reach && Math.abs(p.y - f.bottom.y) < 4) {
                const res = this.progress.flightPasses(f, true);
                if (!res.ok && f.lockSpec?.kind === 'block') this.world.story.onBlocked(f.lockSpec.id);
                return res.ok ? this.enterStairs(f, 0) : this.showLock(res);
            }
            if ((input.down || walkDown) && Math.abs(p.x - f.top.x) < reach && Math.abs(p.y - f.top.y) < 4) {
                const res = this.progress.flightPasses(f, false);
                return res.ok ? this.enterStairs(f, 1) : this.showLock(res);
            }
        }
        return false;
    }

    // Her cards (§6.1.5); ?cards=all opens every lock, for testing (src/progression.js).
    hasCard(card) {
        return this.progress.hasCard(card);
    }

    // A lock she can't pass: the card it needs over her; a block whose sign stands by says it already (she shrugs, it
    // lights up); just the lock: its padlock over her, and she shrugs (the user, 2026-11-24).
    showLock(res) {
        if (res.card) return this.showLocked(res.card);
        return this.blockedBy(res.sign ? this.signNear(this.player.x, this.player.y) : null, res.sign ? `🚧 ${res.sign}` : '🔒');
    }

    // A way she can't go: with a `sign` in sight that says why, no words, a shrug and the sign lit a moment; with none,
    // `text` over her (the old way), and the shrug.
    blockedBy(sign, text) {
        if (!sign) {
            if (this.time.now >= (this.lockedUntil || 0)) this.shrug();
            return this.showLocked(null, text);
        }
        if (this.time.now < (this.lockedUntil || 0)) return false;
        this.lockedUntil = this.time.now + 900;
        sfx.rattle();
        this.flashSign(sign);
        // (What stopped her, for the playtests: the sign's words, and whether she shrugged.)
        this.lastBlocked = { text: sign.signText ?? sign.text ?? '', at: this.time.now, shrug: this.shrug() };
        return false;
    }

    // The sign of a block nearest her, in sight: a rope's card (src/progression.js), a ladder's chain (src/world/world.js).
    signNear(x, y) {
        const signs = [...(this.progress.blockDrawings ?? []).map(d => d.items[1]), ...(this.world.gates ?? []).map(g => g.extra?.[1])];
        let best = null, bestD = Infinity;
        for (const o of signs) {
            if (!o?.visible || Math.abs(o.y - y) > 100) continue;
            const d = Math.abs(o.x - x);
            if (d < SHRUG.signReach && d < bestD) { best = o; bestD = d; }
        }
        return best;
    }

    // The sign lights up a moment: its own picture added over it, in and out (SHRUG). (In its layer at its depth, a
    // hair over it, not on top of everything: she may stand in front of it.)
    flashSign(sign) {
        if (sign.flashing) return;
        // (A text sign, the ladders' chains, is drawn at 4x its size: a picture of its own made from its canvas, or
        // only its top left corner lit, the user saw.)
        let key = sign.texture.key, frame = sign.frame.name;
        if (sign.type === 'Text') {
            key = `glow:${sign.text}`;
            frame = undefined;
            if (!this.textures.exists(key)) {
                const c = document.createElement('canvas');
                c.width = sign.canvas.width;
                c.height = sign.canvas.height;
                c.getContext('2d').drawImage(sign.canvas, 0, 0);
                this.textures.addCanvas(key, c);
            }
        }
        const glow = this.add.image(sign.x, sign.y, key, frame).setOrigin(sign.originX, sign.originY)
            .setDisplaySize(sign.displayWidth, sign.displayHeight).setBlendMode(Phaser.BlendModes.ADD).setAlpha(0);
        glow.setDepth(sign.depth + 0.001);
        if (this.worldLayer.list.includes(sign)) this.worldLayer.add(glow);
        sign.flashing = true;
        this.tweens.add({
            targets: glow, alpha: SHRUG.glow, duration: SHRUG.flashMs / 2, yoyo: true, ease: 'Sine.easeInOut',
            onComplete: () => { glow.destroy(); sign.flashing = false; },
        });
    }

    // She turns to us and shrugs, once (her `shrug`), where she stands; then back the way she faced. Played as an idle
    // is (`standStill`): a fresh step or a jump cuts it short, a key held against the block does not. Not with her
    // hands full, in the towel, crawling, in the air, or again before `SHRUG.againMs`.
    shrug() {
        const p = this.player;
        if (this.mode !== 'play' || this.holding || this.world.carry || this.towel || this.crawling || !this.anims.exists('her-shrug')) return false;
        // (On her feet: off the stairs onto a roped-off landing her body has not met the floor in the first frame.)
        if (this.grounded === false || this.time.now < (this.shrugAgain ?? 0)) return false;
        this.shrugAgain = this.time.now + SHRUG.againMs;
        this.shrugAt = this.time.now;
        this.shrugFacing = p.flipX;
        this.idle = 'shrug';
        p.setFlipX(false);
        // (On a clock of its own: her stand is a still frame, which leaves her run's last slowing as it was, and the shrug
        // played at that, "very much slow", the user. Her idles keep playing at that pace, on purpose (the user:
        // quicker they "looked like twitching"), so it is given back when the shrug ends: `shrugDone`.)
        this.shrugScale = p.anims.timeScale;
        p.anims.timeScale = 1;
        p.anims.play('her-shrug');
        return true;
    }

    // The shrug over or cut short: her facing and her clips' pace as they were before it.
    shrugDone(facing = this.shrugFacing) {
        const p = this.player;
        if (this.shrugScale !== undefined) p.anims.timeScale = this.shrugScale;
        this.shrugScale = undefined;
        if (facing !== undefined) p.setFlipX(facing);
    }

    // A flight up that her cards don't open: the card it needs shows above her for a moment.
    showLocked(card, text = null) {
        if (this.time.now < (this.lockedUntil || 0)) return false;
        this.lockedUntil = this.time.now + 900;
        const shown = text ?? t('lock.card', this.progress.cardName(card));
        if (card) sfx.deny(); else sfx.rattle();
        this.alert.setText(shown, { card }).setVisible(true);
        // Held at the lock, it shows again before this runs: hide it only once the last one is over,
        // whatever she is doing by then (on the stairs, in a lift), unless a fright has taken it over.
        this.time.delayedCall(900, () => {
            if (this.time.now >= this.lockedUntil && this.alert.text === shown) this.alert.setVisible(false);
        });
        return false;
    }

    enterStairs(flight, t) {
        this.mode = 'stairs';
        this.flight = flight;
        this.stairT = t;
        this.player.body.enable = false;
        this.player.setDepth(flight.outside ? DEPTH.player : flight.front ? DEPTH.onFrontStairs : DEPTH.playerBehind);
        this.placeOnStairs();
        return true;
    }

    placeOnStairs() {
        const q = this.stairPoint(this.flight, this.stairT);
        this.player.x = q.x;
        this.player.y = q.y;
    }

    updateStairs(input, dt, time) {
        const p = this.player;
        const f = this.flight;
        const upward = Math.sign(f.top.x - f.bottom.x); // which horizontal direction climbs
        // A gust on the funnel's stairway (src/world/topdeck.js): she crouches and holds on to the rail
        // while it blows, facing the way she faced, and stands back up when it drops; meanwhile she does
        // not move (the user, 2026-11-18).
        // A hit's reaction on the stairs (a funnel gull's swoop, with a tangerine on her): she stays where
        // she is while it plays.
        if (time < this.flinchUntil) {
            this.placeOnStairs();
            return;
        }
        if (this.stairWind || this.stairCling) {
            const c = this.stairCling ??= { way: (p.flipX ? -1 : 1) === upward ? 'up' : 'down', phase: null };
            const key = `her-cling-${c.way}`;
            if (!this.anims.exists(`${key}-in`)) {
                this.stairCling = null;
                this.pose('stand');
                return;
            }
            const play = (phase, then) => {
                c.phase = phase;
                p.anims.play(`${key}-${phase}`);
                if (then) p.once(`animationcomplete-${key}-${phase}`, () => { if (this.stairCling === c && c.phase === phase) then(); });
            };
            if (!c.phase) play('in', () => play('hold'));
            if (!this.stairWind && c.phase !== 'out') play('out', () => {
                this.stairCling = null;
                this.pose('stand');
            });
            return;
        }
        let v = 0;
        if (input.up || (upward > 0 ? input.right : input.left)) v = 1;
        else if (input.down || (upward > 0 ? input.left : input.right)) v = -1;

        this.stairT = Phaser.Math.Clamp(this.stairT + (v * PLAYER.stairsSpeed * dt) / f.length, 0, 1);
        this.placeOnStairs();
        if (v) {
            p.setFlipX(v * upward < 0);
            this.pose('run', 0.8);
        } else {
            this.pose('stand');
        }

        // The funnel's stairway turns on its shoulder, where there is no deck to step onto: straight
        // on from one flight to the next.
        if (f.outside && ((this.stairT >= 1 && v > 0) || (this.stairT <= 0 && v < 0))) {
            const [end, other, t] = v > 0 ? ['top', 'bottom', 0] : ['bottom', 'top', 1];
            const next = this.flights.find(g => g !== f && g.outside && Math.abs(g[other].x - f[end].x) < 3 && Math.abs(g[other].y - f[end].y) < 3);
            if (next) {
                this.flight = next;
                this.stairT = t;
                return;
            }
        }
        if ((this.stairT >= 1 && v > 0) || (this.stairT <= 0 && v < 0)) this.leaveLadderOrStairs();
    }

    // Her pose: a looping animation (run, climb) at an optional speed, or a single frame. Anything
    // but standing still ends an idle and restarts the wait for the next one.
    pose(name, speed = 1) {
        const p = this.player;
        if (name !== 'stand') {
            this.idle = null;
            this.idleAt = this.time.now + IDLE.firstMs;
        }
        // With Bumbot in her arms (the way home): her clips with him, and her standing with him
        // for anything she has none for.
        if (this.holding) {
            if (this.anims.exists(`her-cat-${name}`)) {
                p.anims.play(`her-cat-${name}`, true);
                p.anims.timeScale = speed;
            } else {
                p.anims.stop();
                p.setTexture('her-cat', this.catFrames[name] ?? this.catFrames.stand);
            }
            return;
        }
        // With the towel on (after the shower), her towel clips where there is one.
        const towel = this.towel && (this.anims.exists(`her-towel-${name}`) || this.towelFrames[name] !== undefined);
        // With a tray in her hands (§6.1.2), her carrying clips where there is one.
        if (this.world?.carry && !towel) {
            if (this.anims.exists(`her-carry-${name}`)) {
                p.anims.play(`her-carry-${name}`, true);
                p.anims.timeScale = speed;
                return;
            }
            if (this.herFrames[`carry-${name}`] !== undefined) {
                p.anims.stop();
                p.setTexture('her', this.herFrames[`carry-${name}`]);
                return;
            }
        }
        const key = `${towel ? 'her-towel' : 'her'}-${name}`;
        if (this.anims.exists(key)) {
            p.anims.play(key, true);
            p.anims.timeScale = speed;
        } else {
            p.anims.stop();
            p.setTexture(towel ? 'her-towel' : 'her', (towel ? this.towelFrames : this.herFrames)[name]);
        }
    }

    // The towel round her head (cabin 8206's shower): on as she steps out, taken off and hung on the
    // shower door's handle when she leaves the cabin (or starts again elsewhere), where it stays.
    setTowel(on) {
        if (this.towel && !on) this.save.towelHung = true;
        if (on) this.save.towelHung = false;
        this.towel = on;
    }

    // --- Pickups, checkpoints, hazards ---------------------------------------------------------

    checkPickups() {
        const p = this.player;
        for (const t of this.tangerines) {
            if (!t.sprite.active || t.route !== this.route) continue;
            if (Math.abs(p.x - t.sprite.x) < 12 && t.sprite.y > p.y - PLAYER.height && t.sprite.y - 8 < p.y) {
                this.save.collected.push(t.id);
                this.gainTangerine(t.sprite.x, t.sprite.y - 5);
                // (Its picture is the one that flies to the count: §1.7.)
                t.glint.destroy();
                t.sprite.destroy();
                t.sprite.active = false;
                this.refreshHud();
            }
        }
    }

    checkCheckpoints() {
        const p = this.player;
        for (const c of this.checkpoints) {
            // (Past its door on its floor, or in a jump over that floor: out of the second pool she
            // comes down beyond the pool attendant's hut.)
            if (c.route !== this.route || Math.abs(p.x - c.x) > 8 || p.y > c.y + 6 || p.y < c.y - 70) continue;
            if (!c.active) {
                this.lightCheckpoint(c, true);
                this.save.activated.push(c.id);
            }
            if (this.save.lastCheckpoint !== c.id || !c.saved) {
                this.save.lastCheckpoint = c.id;
                writeSave(this.save);
                this.checkpoints.forEach(o => { o.saved = o === c; });
            }
        }
    }

    // A door's picture changed for another (shut, ajar), standing where it stood. A piece whose
    // leaf reaches under the floor line (the open crew door: its `foot` in the atlas,
    // tools/build_ship_art.py) is stood by its frame, not by its lowest pixel.
    setDoorArt(door, frame) {
        const f = this.textures.getFrame('shipart', frame);
        return door.setTexture('shipart', frame).setOrigin(0.5, 1 - (f.customData?.foot || 0) / f.height);
    }

    // An active checkpoint has to read from across the deck: the door stands ajar with the cabin
    // light on, and a green lamp above it glows.
    lightCheckpoint(c, celebrate) {
        c.active = true;
        if (c.door) this.setDoorArt(c.door, `${c.frame}-ajar`);
        c.lamp.setTexture('lamp-on');
        c.glow.setVisible(true).setAlpha(0.55);
        this.tweens.add({ targets: c.glow, alpha: 0.25, scale: 0.8, duration: 1100, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        if (!celebrate) return;
        sfx.checkpoint();
        this.tweens.add({ targets: c.lamp, scale: 1.8, duration: 160, yoyo: true, ease: 'Quad.easeOut' });
        for (let i = 0; i < 14; i++) {
            const angle = (Math.PI * 2 * i) / 14;
            const spark = this.add.image(c.x, c.y - c.rise, 'dot').setTint(0x7dffa0).setDepth(DEPTH.fx);
            this.worldLayer.add(spark);
            this.tweens.add({
                targets: spark, x: c.x + Math.cos(angle) * 22, y: c.y - c.rise + Math.sin(angle) * 22, alpha: 0,
                duration: 500, ease: 'Quad.easeOut', onComplete: () => spark.destroy(),
            });
        }
    }

    // Something here of the scene's own takes a tangerine loose near it (docs/plan-three-uses.md §2):
    // deck 4's vacuum swallows it and chokes.
    offeredHere(t) {
        for (const v of this.vacuums) {
            if (!v.alive || v.ridden || !this.loose.near(t, v.sprite.x, v.sprite.y, 10, 12)) continue;
            this.loose.remove(t);
            v.alive = false;
            v.puffAt = this.time.now + 700;
            this.world.choke(v.sprite);
            return true;
        }
        return false;
    }

    updateVacuums(dt) {
        const p = this.player;
        for (const v of this.vacuums) {
            if (v.ridden) continue;                 // (in her gag, 5b: it is in her picture)
            // Choked on a tangerine: dead, smoking now and then, until she has left the deck.
            if (!v.alive) {
                if (this.route !== 'inside' || Math.abs(p.y - v.sprite.y) > this.deckPitch / 2) {
                    v.alive = true;
                    v.sprite.clearTint().setAngle(0).setAlpha(1);
                } else if (this.time.now > v.puffAt) {
                    v.puffAt = this.time.now + 900;
                    this.world.drops(v.sprite.x, v.sprite.y - 10, 0x8a8a8a, -1);
                }
                continue;
            }
            if (v.asideUntil) {
                if (this.time.now < v.asideUntil) continue;
                v.asideUntil = 0;
                v.sprite.setAngle(0).setAlpha(1);
            }
            v.sprite.x += v.dir * v.speed * dt;
            if (v.sprite.x > v.maxX) v.dir = -1;
            else if (v.sprite.x < v.minX) v.dir = 1;
            v.sprite.setFlipX(v.dir < 0);
        }
    }

    checkVacuums() {
        const p = this.player;
        for (const v of this.vacuums) {
            if (!v.alive || v.ridden) continue;
            const s = v.sprite;
            const hit = Math.abs(p.x - s.x) < (PLAYER.bodyWidth / 2 + s.width / 2 - 2) && p.y > s.y - s.height + 2 && p.y - PLAYER.bodyHeight < s.y;
            if (!hit) continue;
            if (v.asideUntil) continue;
            if (this.isLunging()) {
                // Shoved aside, spinning, into a doorway for a while (population: `haz_vacuum_4`).
                v.asideUntil = this.time.now + 6000;
                this.smash(s.x, s.y - 3);
                s.setAlpha(0.6);
                this.tweens.add({ targets: s, angle: 720, duration: 900, ease: 'Quad.easeOut' });
            } else if (this.world.carry) {
                // (Its place with its height: without `y` the spill's sound had no distance, threw every frame, and the game
                // hung, the user, 2026-11-26, carrying the pills.)
                this.world.touched({ x: s.x, y: s.y, touch: { kind: 'spill' } });
            } else {
                // (From behind she rides it off down the corridor, 5b: it is hidden meanwhile.)
                const ride = { x: s.x, y: s.y, dir: v.dir, v: v.speed,
                               hide: () => { v.ridden = true; s.setVisible(false); },
                               show: () => { v.ridden = false; s.setVisible(true); } };
                this.scareContact(s.x, 'vacuum', { vx: v.dir * v.speed, ride });
                return;
            }
        }
    }

    // --- Bumbot ------------------------------------------------------------------------------

    checkBumbot() {
        const p = this.player;
        if (this.mode !== 'play') return;
        for (const cat of this.cats) {
            const s = cat.sprite;
            // (`custom`: a beat with its whole scene of its own: the pool's, src/world/lido.js.)
            if (cat.gone || cat.hidden || cat.custom || cat.route !== this.route || Math.abs(p.y - cat.floor) > 8 || Math.abs(p.x - s.x) > BUMBOT.noticeReach) continue;
            this.nearCatch(cat);
            return;
        }
    }

    // A near-catch (§4): input locked, she walks up and bends down to pick him up, and just before
    // her hands get there he leaps away. For now he runs off the screen toward his escape side and
    // is gone; the real spots send him somewhere she can't follow yet.
    nearCatch(cat) {
        const p = this.player;
        const s = cat.sprite;
        cat.gone = true;
        this.mode = 'scripted';
        this.script = null;
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        const toward = s.x >= p.x ? 1 : -1;
        p.setFlipX(toward < 0);
        let catAway = false;
        let herDone = false;
        const finish = () => {
            if (!catAway || !herDone) return;
            p.body.enable = true;
            p.body.reset(p.x, p.y);
            this.pose('stand');
            this.mode = 'play';
            // One of the plan's beats (§6.1.8): what his escape changes.
            if (cat.flag) this.progress.setFlag(cat.flag);
        };

        // Up to arm's length from him, at a walk.
        const stopX = s.x - toward * BUMBOT.reachGap;
        const walkMs = Math.max(0, (Math.abs(stopX - p.x) / (PLAYER.runSpeed * 0.6)) * 1000);
        this.pose('run', 0.6);
        this.tweens.add({
            targets: p, x: stopX, duration: walkMs,
            onComplete: () => {
                p.anims.play('her-reach');
                cat.onReach?.();
                const away = () => {
                    cat.away = true;
                    cat.onAway?.();
                    s.setVisible(false).stop();
                    this.script = null;
                    catAway = true;
                    finish();
                };
                let leapt = false, onLeapt = null;
                // He hears her a beat before her hands arrive: a startled leap, then gone. (One of
                // the plan's beats may have something happen first, `before`, and his own way out,
                // `flee`: the stage's, src/world/story.js.)
                this.time.delayedCall(BUMBOT.startleMs, async () => {
                    if (cat.before) await cat.before();
                    this.tweens.killTweensOf(s);
                    // (Out of what he was doing first, quick: awake and up, or up off his haunches; then the leap.)
                    const up = BUMBOT.getUp[cat.activity === 'asleep' ? 'asleep' : SITTING.has(cat.activity) ? 'sat' : ''];
                    if (up) {
                        s.setScale(1).play({ key: `bumbot-${up[0]}`, startFrame: up[1], frameRate: up[2] });
                        await new Promise(resolve => s.once('animationcomplete', resolve));
                    }
                    cat.onLeap?.();
                    rumble('bolt');
                    s.setScale(1).setFlipX(cat.escape < 0).play('bumbot-startle');
                    leapt = true;
                    onLeapt?.();
                    this.time.delayedCall(BUMBOT.leapMs, () => {
                        sfx.mrrp();
                        if (cat.flee) {
                            cat.flee(s, away);
                            return;
                        }
                        s.play('bumbot-run');
                        s.y = cat.floor;
                        this.script = (dt) => {
                            s.x += cat.escape * BUMBOT.runSpeed * dt;
                            const view = this.cameras.main.worldView;
                            const out = cat.exitX !== null ? (s.x - cat.exitX) * cat.escape >= 0
                                : s.x < view.x - 40 || s.x > view.right + 40;
                            if (out) away();
                        };
                    });
                });
                // Left reaching at nothing for a moment (from his leap), then she straightens up and turns to us.
                p.once('animationcomplete-her-reach', async () => {
                    if (!leapt) await new Promise(resolve => { onLeapt = resolve; });
                    this.time.delayedCall(BUMBOT.holdMs, () => {
                        p.anims.play('her-straighten');
                        p.once('animationcomplete-her-straighten', () => {
                            // (Turned to us, she shrugs: the user, 2026-11-24. Then back the way she faced.)
                            const facing = p.flipX, pace = p.anims.timeScale;
                            const done = () => this.time.delayedCall(BUMBOT.frontMs, () => { p.setFlipX(facing); p.anims.timeScale = pace; herDone = true; finish(); });
                            if (!this.anims.exists('her-shrug')) {
                                this.pose('front');
                                return done();
                            }
                            p.setFlipX(false);
                            p.anims.timeScale = 1;
                            p.anims.play('her-shrug');
                            // (Her shrug's last frame is held: it is her facing us already; her front still is not
                            // shown after it. The user, 2026-11-24.)
                            p.once('animationcomplete-her-shrug', () => done());
                        });
                    });
                });
            },
        });
    }

    smash(x, y, sound = true) {
        if (sound) sfx.at(x, y).smash();
        for (let i = 0; i < 10; i++) {
            const b = this.add.image(x, y, 'dot').setDepth(DEPTH.fx).setTint(0xc9a26a);
            this.worldLayer.add(b);
            this.tweens.add({
                targets: b,
                x: x + Phaser.Math.Between(-24, 24),
                y: y + Phaser.Math.Between(-20, 8),
                alpha: 0,
                duration: Phaser.Math.Between(250, 450),
                onComplete: () => b.destroy(),
            });
        }
    }

    // Water thrown up where she goes in: blue and white drops that rise and fall back.
    splash(x, y) {
        const colours = [0x8fd3ff, 0x4d9be6, 0xffffff];
        for (let i = 0; i < 12; i++) {
            const d = this.add.image(x, y, 'dot').setDepth(DEPTH.fx).setTint(colours[i % colours.length]);
            this.worldLayer.add(d);
            const dx = Phaser.Math.Between(-22, 22);
            const rise = Phaser.Math.Between(10, 26);
            this.tweens.add({ targets: d, x: x + dx, duration: 520, onComplete: () => d.destroy() });
            this.tweens.add({ targets: d, y: y - rise, duration: 220, ease: 'Quad.easeOut', yoyo: true, hold: 20 });
            this.tweens.add({ targets: d, alpha: 0, delay: 300, duration: 220 });
        }
    }

    // --- D: the cry, and the lunge with it (docs/plan-three-uses.md §1.1) -------------------------

    isLunging() {
        return this.lungeUntil > this.time.now;
    }

    // During the lunge and a breath after it nothing frightens her by contact.
    lungeSafe() {
        return this.lungeUntil + LUNGE.safeTailMs > this.time.now;
    }

    // ?tangerines=infinite: D never uses one up, for testing.
    infiniteTangerines() {
        return new URLSearchParams(location.search).get('tangerines') === 'infinite';
    }

    // Every D costs one tangerine, whatever it does. The cry startles what is in her way; with the
    // lunge learned (near-catch 1) and her hands free, the lunge goes with it. Not crawling, nor
    // with Bumbot in her arms (ladders, stairs, the pool are modes of their own: no D there).
    tryCry(time) {
        if (this.crawling || this.holding || time < this.cryGapUntil || this.isLunging()) return;
        if (this.save.tangerines <= 0 && !this.infiniteTangerines()) {
            this.blinkCount();
            return;
        }
        if (!this.infiniteTangerines()) this.save.tangerines -= 1;
        this.cryGapUntil = time + CRY.gapMs;
        this.bubbleUntil = time + CRY.bubbleMs;
        sfx.cry();
        const lunge = this.progress.knows('dash') && !this.world.carry;
        if (lunge) {
            this.lungeUntil = time + LUNGE.ms;
            sfx.lunge();
            rumble('lunge');
        }
        const p = this.player;
        this.world.shout(p.x, p.y, this.route);
        this.refreshHud();
    }

    updateLunge(time) {
        const lunging = this.isLunging();
        if (this.wasLunging && !lunging) sfx.lungeEnd();
        this.wasLunging = lunging;

        if (lunging && this.mode === 'play' && time - this.lastTrailAt > 45 && Math.abs(this.player.body.velocity.x) > 10) {
            this.lastTrailAt = time;
            const p = this.player;
            const ghost = this.add.image(p.x, p.y, 'her', p.frame.name).setOrigin(0.5, 1)
                .setFlipX(p.flipX).setAlpha(0.45).setDepth(DEPTH.player - 0.5);
            this.worldLayer.add(ghost);
            this.tweens.add({ targets: ghost, alpha: 0, duration: 260, onComplete: () => ghost.destroy() });
        }
    }

    // --- The throw (docs/plan-three-uses.md §1.2) ----------------------------------------------

    // F: one tangerine thrown underarm the way she faces: a roll, or with ↑ a lob. On her feet,
    // hands free: not with a tray, crawling, gliding, in a lunge or holding Bumbot (ladders,
    // stairs, the pool are modes of their own). No cursor: she aims by where she stands.
    tryThrow(input, time, onFloor) {
        if (this.crawling || this.holding || this.gliding || this.world.carry || this.isLunging()) return false;
        // (In the air: once a jump, and not kicking off a wall.)
        if (!onFloor && (this.airThrown || this.throwing || time < this.kickUntil + 160)) return false;
        if (this.save.tangerines <= 0 && !this.infiniteTangerines()) {
            this.blinkCount();
            return false;
        }
        const p = this.player;
        if (!onFloor) {
            this.airThrown = true;
            this.throwing = { at: time + THROW.airReleaseMs, lob: !!input.up, dir: p.flipX ? -1 : 1, air: true };
            this.airThrowUntil = time + THROW.airMs;
            if (this.anims.exists('her-airtoss')) p.anims.play('her-airtoss');
            return true;
        }
        this.throwing = { at: time + THROW.releaseMs, lob: !!input.up, dir: p.flipX ? -1 : 1 };
        this.throwUntil = time + THROW.ms;
        // (Until her clip is made, her reach stands in.)
        p.anims.play(this.anims.exists('her-toss') ? 'her-toss' : 'her-reach');
        return true;
    }

    // It leaves her hand: one less, a real thing in the world (src/world/tangerine.js).
    releaseThrow() {
        const p = this.player, { lob, dir, air } = this.throwing;
        this.throwing = null;
        if (this.save.tangerines <= 0 && !this.infiniteTangerines()) return;
        if (!this.infiniteTangerines()) this.save.tangerines -= 1;
        const k = lob ? THROW.lob : air ? THROW.air : THROW.roll;
        // (In the air: from her hand where the swing has it, with some of her own speed along.)
        const hand = air ? THROW.airHand : THROW.hand, handY = air ? THROW.airHandY : THROW.handY;
        const along = air ? p.body.velocity.x * THROW.carry : 0;
        this.loose.throw(p.x + dir * hand, p.y - handY, dir * k.vx + along, -k.vy, lob);
        sfx.toss();
        this.refreshHud();
    }

    // --- A gull's take (docs/plan-the-rest.md §3 1.2a) ------------------------------------------

    // Blinking after a gull's take: nothing can touch her.
    isSafe() {
        return this.safeUntil > this.time.now;
    }

    // A gull that comes down on her (`pocket` in `MISHAP_SCENES`: 20, 21, 22), with a tangerine on her:
    // it flies off with one (`snatch`: its sprite), she ducks, blinks, and keeps her place and whatever
    // she carries (under the parasol she glides on). True if it took one. Every other hit is its gag
    // and her checkpoint, whatever she carries (the user, 2026-11-19).
    pocket(fromX, sc, { snatch = null } = {}) {
        if (!sc.pocket || (this.save.tangerines <= 0 && !this.infiniteTangerines())) return false;
        if (!this.infiniteTangerines()) this.save.tangerines -= 1;
        const p = this.player, time = this.time.now;
        this.safeUntil = time + POCKET.safeMs;
        sfx.pocket();
        rumble('spill');
        if (snatch) this.world.snatch(snatch, p.x, p.y - PLAYER.height + 8);
        // (Under the parasol she keeps on gliding: only the blink. A throw under way is dropped.)
        if ((this.mode === 'play' || this.mode === 'stairs') && !this.gliding) {
            this.throwUntil = 0;
            this.throwing = null;
            const clip = `her-${sc.react}`;
            if (this.anims.exists(clip)) {
                this.flinchUntil = time + POCKET.recoverMs;
                this.herClip(clip);
            } else {
                this.flinchUntil = time + POCKET.flinchMs;
                if (this.anims.exists('her-hit')) this.herClip('her-hit');
            }
            p.body.velocity.x = 0;
            p.body.velocity.y = 0;
        }
        this.refreshHud();
        return true;
    }

    // One of her clips played at its own speed (her run's leaves its pace on her sprite).
    herClip(key) {
        this.player.anims.timeScale = 1;
        this.player.anims.play(key);
    }

    // A tangerine held out in both hands as an apology, her head bowed; the hand at `fromX` takes it
    // (spent, never loose). No hit plays it since 1.2a (23 and 24 are her tiptoe always); kept for
    // part 2's sardines, the Sushi Bar's chef taking one from her hands (docs/plan-the-rest.md).
    handOver(fromX) {
        const p = this.player, dir = p.flipX ? -1 : 1, time = this.time.now;
        this.flinchUntil = time + HAND_OVER.ms;
        if (this.anims.exists('her-apology')) this.herClip('her-apology');
        // (Behind her, her hands over it.)
        const fruit = this.add.image(p.x + dir * HAND_OVER.dx, p.y - HAND_OVER.dy, 'tangerine').setOrigin(0.5, 0.6)
            .setDepth(p.depth - 0.01).setVisible(false);
        this.worldLayer.add(fruit);
        const show = () => fruit.setVisible((p.anims.currentFrame?.index ?? 1) - 1 >= HAND_OVER.frame);
        p.on('animationupdate', show);
        this.time.delayedCall(HAND_OVER.giveMs, () => {
            p.off('animationupdate', show);
            fruit.setVisible(true);
            sfx.give();
            this.tweens.add({ targets: fruit, x: fromX, y: p.y - HAND_OVER.dy - 4, alpha: 0, duration: 380, ease: 'Quad.easeIn', onComplete: () => fruit.destroy() });
        });
    }

    updatePocket(time) {
        const safe = this.isSafe();
        if (safe) this.player.setAlpha(Math.floor(time / 70) % 2 ? 0.5 : 1);
        else if (this.wasSafe) this.player.setAlpha(1);
        this.wasSafe = safe;
    }

    // --- Scares (never death, §5.6) ------------------------------------------------------------

    beginScare() {
        this.mode = 'scripted';
        this.airScare = false;
        this.safeUntil = 0;
        this.flinchUntil = 0;
        this.gagPending = null;
        this.throwUntil = 0;
        this.throwing = null;
        this.lungeUntil = 0;
        this.bubbleUntil = 0;
        this.player.body.enable = false;
        this.cameras.main.stopFollow();
    }

    // The two facts read at every hit (docs/plan-three-uses.md §1.6): which side of her it is on
    // (front: the way she faces, at this moment) and who was moving: she, toward it, faster than
    // 20 px a second; it, toward her (`vx`, its speed along the deck), faster than 5. `dir`: the
    // way it faces, for a person; `lying`: a thing at rest on the floor.
    hitFacts(fromX, vx = 0, dir = 0, lying = false, crowded = false) {
        const p = this.player, facing = p.flipX ? -1 : 1, toward = Math.sign(fromX - p.x) || facing;
        return { front: toward === facing, she: p.body.velocity.x * toward > 20, it: vx * -toward > 5, faces: dir === -toward, lying, crowded };
    }

    // She is hit by `what` (an obstacle of `MISHAPS`) from `fromX`: in a lunge she is through; a gull
    // with a tangerine on her takes one (`pocket()`); otherwise her mishap and her checkpoint. Which
    // scenario it is comes from the side and who was moving (src/world/mishaps.js); returns its
    // number, or null when nothing happened. `force`: no contact (her own cry at a "Do Not Disturb"
    // door): a lunge does not help. `snatch`: the gull that takes the tangerine. `ride`: how the
    // thing carries her off, for a gag with it (`rideGag`).
    scareContact(fromX, what, { vx = 0, dir = 0, lying = false, crowded = false, force = false, snatch = null, ride = null } = {}) {
        const p = this.player;
        if (this.holding || this.gagPending) return null;   // nothing scares her on the way home (§6.1.9)
        if (this.viewing) return null;                      // nor while a thing she got is shown close (`world.closeup`)
        // In a lunge she is through: what touched her gives way in its own manner.
        if (this.lungeSafe() && !force) {
            this.world.lunged(what, fromX);
            return null;
        }
        // Blinking after a gull's take, nothing touches her.
        if (this.isSafe()) return null;
        const id = scenario(what, this.hitFacts(fromX, vx, dir, lying, crowded)), sc = MISHAP_SCENES[id];
        // (A slow thing she stands looking at does not knock her over: it is the thing's to stop.)
        if (!sc || sc.nothing) return id;
        this.lastMishap = { what, id, time: this.time.now };
        if (!this.pocket(fromX, sc, { snatch })) this.mishap(sc, fromX, ride);
        return id;
    }

    // Her mishap (§1.6): the gag, and her checkpoint; the keys do nothing until
    // the fade. A hit in the air plays it when she lands. Until a scenario's own gag is made, the
    // built fall on its side stands in (`down`), or she runs off.
    mishap(sc, fromX, ride = null) {
        const p = this.player;
        if (this.mode === 'play' && !this.grounded) {
            this.gagPending = { sc, fromX, ride };
            this.flinchUntil = this.time.now + 10000;
            // (A gag that knocks the jump out of her (`drop`, the court's balls): she stops where she was hit and drops
            // straight down, the gag where she lands (the user, 2026-11-19: it played where her jump would have ended).)
            // Stiff at once (her standing frame, the gag's first), her word at the hit.
            if (sc.gag && GAGS[sc.gag].drop) {
                p.body.setVelocity(0, Math.max(0, p.body.velocity.y));
                this.pose('stand');
                this.alert.setText(fright(GAGS[sc.gag].word ?? sc.word)).setVisible(true);
            }
            return;
        }
        if (sc.gag && GAGS[sc.gag].crawl && this.anims.exists('drill-crawl')) return this.crawlGag(sc, fromX);
        if (sc.gag && GAGS[sc.gag].stairs && this.mode === 'stairs' && this.flight?.outside) return this.stairsGag(sc);
        if (sc.gag && GAGS[sc.gag].sorry && this.anims.exists('gags-dnd-tiptoe')) return this.sorryGag(sc, fromX);
        if (sc.gag && ride?.play) return this.thingGag(sc, ride);
        if (sc.gag && GAGS[sc.gag].jog && (ride?.person || !GAGS[sc.gag].his && !GAGS[sc.gag].bounce)) return this.jogGag(sc, ride?.person ?? null);
        if (sc.gag && ride?.person && this.anims.exists(GAGS[sc.gag].clip)) return this.cartGag(sc, ride.person);
        if (sc.gag && ride && this.anims.exists(GAGS[sc.gag].ride)) return this.rideGag(sc, ride);
        if (sc.gag && this.anims.exists(GAGS[sc.gag].fall) && (!GAGS[sc.gag].tray || ride?.tray) && (GAGS[sc.gag].at === undefined || ride)) return this.fallGag(sc, ride);
        if (sc.down) return this.scareDown(sc);
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        const away = p.x >= fromX ? 1 : -1;
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(sc.word)).setVisible(true);
        // Her reaction, as with a tangerine on her (shivering, arching), or her start; then off.
        const clip = sc.react !== 'apology' && this.anims.exists(`her-${sc.react}`) ? `her-${sc.react}` : 'her-hit';
        if (this.anims.exists(clip)) this.herClip(clip);
        else this.pose('rise');
        p.setFlipX(away > 0);
        this.script = null;
        this.tweens.add({
            targets: p, y: p.y - 14, duration: 170, yoyo: true, ease: 'Quad.easeOut',
            onComplete: () => {
                sfx.runOff();
                this.script = (dt, time) => {
                    p.x += away * 260 * dt;
                    this.pose('run', 2);
                    const view = this.cameras.main.worldView;
                    if (p.x < view.x - 20 || p.x > view.right + 20) this.respawn();
                };
            },
        });
    }

    // Her gag at a "Do Not Disturb" door (23), the door opened on its guest: "Oh, sorry!", a startled hop, both hands
    // over her eyes, blushing; then she turns away from the door and tiptoes off, quick, to the next wall or door
    // across the deck (`stopShort`: a beat there, then her checkpoint) or out of the screen; on an occupied balcony (24) the
    // same, away from its guests to the partition ahead (`partitionShort`). One picture of her
    // (the `gags` sheet's dnd-cover and dnd-tiptoe), first facing her way, then away from the door.
    sorryGag(sc, fromX) {
        const p = this.player, g = GAGS[sc.gag], gm = this.cache.json.get('gags-meta');
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(g.word ?? sc.word)).setVisible(true);
        this.script = null;
        const y = p.y, away = p.x >= fromX ? 1 : -1;
        const s = this.add.sprite(p.x, y, 'gags', gm.anims['dnd-cover'][0]).setOrigin(gm.dnd.x / gm.cell, gm.floor / gm.cell)
            .setFlipX(p.flipX).setDepth(p.depth);
        this.worldLayer.add(s);
        p.setVisible(false);
        this.gagEnd = () => { s.destroy(); p.setVisible(true); };
        s.play('gags-dnd-cover');
        s.once('animationcomplete-gags-dnd-cover', () => {
            if (this.gagEnd === null) return;
            s.setFlipX(away < 0).play('gags-dnd-tiptoe');
            // (`sorryStop`: where a scene wants her to stop instead, the restrooms' mirror after the stall's knock; the
            // user, 2026-11-25: "let her always go to the mirror, stop there, and then respawn".)
            const wall = this.sorryStop ?? this.partitionShort(s.x, this.stopShort(s.x, s.x + away * 4800, y, 12), y, 12);
            this.sorryStop = null;
            this.script = (dt) => {
                s.x += away * g.speed * dt;
                const view = this.cameras.main.worldView;
                if ((s.x - wall) * away >= 0) {
                    // (At a wall: she stops there, still covering her eyes.)
                    s.x = wall;
                    this.script = null;
                    s.anims.stop();
                    s.setFrame(gm.anims['dnd-tiptoe'][0]);
                    this.time.delayedCall(g.holdMs, () => this.respawn());
                } else if (s.x < view.x - 30 || s.x > view.right + 30) this.respawn();
                // (Her word over her head goes with her.)
                p.x = s.x;
            };
        });
    }

    // Her gag with the thing that hit her (§1.6: the vacuum, 5a and 5b; the suitcase, 6a to 6c):
    // whichever side it came from and whoever was moving, she rides it off (the user, 2026-11-16:
    // "I prefer the ride in all cases"), one picture of her with it, drawn together (`her-mishaps`),
    // facing the way it carries her (from the front she turns round onto it); the world's own is
    // hidden until she comes out of her door. `ride`: { x, y: the thing's middle and its floor, dir: the way it
    // carries her, v: its speed, px/s; endX: where its roll ends (the suitcase); hide(), show() }.
    rideGag(sc, ride) {
        // (A thing of another colour plays its own clips, `GAGS['<gag>-<look>']` over the gag's: deck 5's red suitcase.)
        const p = this.player, g = ride.look ? { ...GAGS[sc.gag], ...GAGS[`${sc.gag}-${ride.look}`] } : GAGS[sc.gag], dir = ride.dir;
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(g.word ?? sc.word)).setVisible(true);
        ride.hide();
        const s = this.add.sprite(p.x - dir * g.her, ride.y, 'her-mishaps').setOrigin(0.5, 1)
            .setFlipX(dir < 0).setDepth(p.depth);
        this.worldLayer.add(s);
        p.setVisible(false);
        this.gagEnd = () => { s.destroy(); p.setVisible(true); ride.show(); };
        s.play(g.sit);
        s.once(`animationcomplete-${g.sit}`, () => s.play(g.ride));
        let v = Math.abs(ride.v), tipped = false, k = 1;
        if (g.rideS) {
            // The suitcase's ride takes `rideS` from wherever she is hit: the time its profile
            // (cruise at `top`, then speed = px left x `slow`, at least `least`) would take over
            // this roll, and every speed scaled to match; never under `pace`.
            const L = Math.max(0, (ride.endX - (p.x - dir * g.her)) * dir), knee = g.top / g.slow, floor = g.least / g.slow;
            const T = Math.max(0, L - knee) / g.top + Math.log(Math.max(Math.min(L, knee), floor) / floor) / g.slow + floor / g.least;
            k = Math.max(g.pace ?? 1, T / g.rideS);
        }
        // (A door or a wall across the deck stops the ride short of it, `stopShort`: a beat there,
        // and her checkpoint.)
        const wall = this.stopShort(s.x, s.x + dir * 4800, ride.y, 16);
        this.script = (dt) => {
            if (sc.gag === 'vacuum') {
                // Off down the corridor, faster and faster, out of the screen.
                v = Math.min(g.speed, v + g.accel * dt);
                s.x += dir * v * dt;
                const view = this.cameras.main.worldView;
                if ((s.x - wall) * dir >= 0) {
                    s.x = wall;
                    this.script = null;
                    s.anims.pause();
                    sfx.at(s.x, ride.y).thump();
                    this.time.delayedCall(700, () => this.respawn());
                } else if (s.x < view.x - 60 || s.x > view.right + 60) this.respawn();
            } else if (!tipped) {
                // On to the end of its roll, slowing; there it creaks and tips her off.
                const left = (ride.endX - s.x) * dir;
                v = k * Math.max(g.least, Math.min(g.top, left * g.slow));
                const step = dir * Math.min(v * dt, Math.max(0, left));
                s.x += step;
                // (Its roll is seven metres: the view slides along with her, exactly as she goes,
                // and never up or down. A camera follow started here snapped the view onto her.)
                this.cameras.main.scrollX += step;
                if (left <= 0.5) {
                    tipped = true;
                    sfx.at(s.x, ride.y).creak();
                    s.play(g.tip);
                    s.once(`animationcomplete-${g.tip}`, () => {
                        if (g.dazed && this.anims.exists(g.dazed)) s.play(g.dazed);
                        this.time.delayedCall(g.holdMs, () => this.respawn());
                    });
                }
            }
            // (Her word over her head goes with her.)
            p.x = s.x + dir * (sc.gag === 'vacuum' ? 0 : 4);
        };
    }

    // Her gag where she stands, one picture of her with the thing (§1.6: the papers, 4a and 4b),
    // facing her way; set down so that its thing is where the world's own is (`ride.x`, the gag's
    // `paper`), which is taken away (`ride.hide()`), on its floor (`ride.y`: hit up on something,
    // the trolley's top, she comes down to the floor, never sits on the air when it moves on). She
    // stays down a while, then her checkpoint.
    fallGag(sc, ride) {
        const p = this.player, g = GAGS[sc.gag];
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(g.word ?? sc.word)).setVisible(true);
        this.script = null;
        ride?.hide?.();
        // (Set down by the thing in the clip's own facing: turned, the other way.)
        const face = (p.flipX ? -1 : 1) * (g.turn ? -1 : 1), at = g.at ?? g.paper;
        const x = ride?.x !== undefined && at !== undefined ? ride.x - face * at : p.x - face * (g.her ?? 0);
        // (`turn`: hit from behind, she turns round to face it, the clip drawn to her other side.)
        const s = this.add.sprite(x, ride?.y ?? p.y, 'her-mishaps').setOrigin(0.5, 1)
            .setFlipX(g.turn ? !p.flipX : p.flipX).setDepth(p.depth);
        this.worldLayer.add(s);
        p.setVisible(false);
        this.gagEnd = () => { s.destroy(); p.setVisible(true); ride?.show?.(); };
        s.play(g.fall);
        s.once(`animationcomplete-${g.fall}`, () => this.time.delayedCall(g.holdMs, () => this.respawn()));
    }

    // A gag the thing plays itself, one picture of it with her (the towel stack, 18: `TowelStack.ride`
    // in src/world/movers.js): she is hidden while `ride.play(done)` runs its clips; when it says it
    // is done, `holdMs`, then her checkpoint, and `ride.show()` puts the thing back as it is left.
    thingGag(sc, ride) {
        const p = this.player, g = GAGS[sc.gag];
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(g.word ?? sc.word)).setVisible(true);
        this.script = null;
        p.setVisible(false);
        p.body.setVelocity(0, 0);
        this.gagEnd = () => { p.setVisible(true); ride.show?.(); };
        ride.play(() => this.time.delayedCall(g.holdMs, () => this.respawn()));
    }

    // Gag 21 (§1.6), a funnel gull's swoop on the stairway with none on her: from the step's corner
    // nearest her she sits down hard, facing down the flight, and at once bumps down on her bottom, a
    // step each three frames at a constant pace (bump 3, 5, 7, the step down at 5), down to the lower
    // flight's second step; there the foot's clip takes her off onto the roof, slumped; she sits there
    // dizzy, butterflies over her head; then her checkpoint. The `gags` sheet's stairs-sit, -bump, -foot, drawn at her depth (the rail in front of
    // her), each frame stood on its corner (`stairs` in its data); her own sprite, hidden, goes along
    // for the camera and the word over her head.
    stairsGag(sc) {
        const p = this.player, g = GAGS[sc.gag], gm = this.cache.json.get('gags-meta'), A = gm.anims;
        const corner = (f, t) => {
            const q = this.stairPoint(f, t);
            return { x: Math.round(q.x), y: Math.round(q.y) };
        };
        const below = f => this.flights.find(h => h !== f && h.outside && Math.abs(h.top.x - f.bottom.x) < 3 && Math.abs(h.top.y - f.bottom.y) < 3);
        // The corners from hers down: a flight's own down to its first (its bottom is the next one's
        // top), the last flight's down to its second.
        const corners = [];
        let f = this.flight, i = Math.round(this.stairT * this.stairSteps(f));
        for (;;) {
            const n = this.stairSteps(f), next = below(f);
            for (; i >= (next ? 1 : 2); i--) corners.push(corner(f, i / n));
            if (!next) break;
            f = next;
            i = this.stairSteps(f);
        }
        if (!corners.length) corners.push(corner(f, 2 / this.stairSteps(f)));   // (on its last two steps)
        const foot = corner(f, 0), flip = f.top.x > f.bottom.x;
        const seq = A['stairs-sit'].map(fr => ({ fr, at: corners[0] }));
        for (let k = 0; k < corners.length - 1;) {
            for (const b of [3, 5, 7]) {
                if (b === 5) k = Math.min(k + 1, corners.length - 1);
                seq.push({ fr: A['stairs-bump'][b], at: corners[k], thump: b === 5 });
            }
        }
        A['stairs-foot'].forEach((fr, j) => seq.push({ fr, at: foot, foot: true, thump: j === 4 }));
        // (Then dizzy where she slumped, butterflies over her head, at its own pace.)
        for (let l = 0; l < g.dazedLoops; l++) for (const fr of A['stairs-dazed']) seq.push({ fr, at: foot, foot: true, ms: g.dazedMs });
        let t = 0;
        for (const q of seq) { q.t = t; t += q.ms ?? g.frameMs; }

        this.beginScare();
        this.scareFrom = { x: foot.x, y: foot.y };
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(g.word ?? sc.word)).setVisible(true);
        this.script = null;
        p.setVisible(false);
        const spr = this.add.sprite(corners[0].x, corners[0].y, 'gags').setDepth(p.depth).setFlipX(flip);
        const cam = this.cameras.main;
        cam.startFollow(p, true, 0.15, 0.15);
        cam.setFollowOffset(0, HALF);
        // (Phaser mirrors a frame in place, its origin still counted from the left of what is drawn: the
        // corner's column is counted from the right.)
        const origin = ([cx, cy]) => [(flip ? gm.cell - 1 - cx : cx) / gm.cell, cy / gm.cell];
        const [oc, of] = [origin(gm.stairs.corner), origin(gm.stairs.foot)];
        const t0 = this.time.now;
        let shown = -1, done = false;
        const step = () => {
            const e = this.time.now - t0;
            let j = shown < 0 ? 0 : shown;
            while (j + 1 < seq.length && seq[j + 1].t <= e) j++;
            if (j !== shown) {
                for (let q = shown + 1; q <= j; q++) if (seq[q].thump) sfx.land(seq[q].foot ? 'deck' : 'metal');
                shown = j;
                const s = seq[j];
                spr.setFrame(s.fr).setOrigin(...(s.foot ? of : oc)).setPosition(s.at.x, s.at.y);
                p.x = s.at.x;
                p.y = s.at.y;
            }
            if (!done && e >= t + g.holdMs) {
                done = true;
                this.respawn();
            }
        };
        this.events.on('update', step);
        step();
        this.gagEnd = () => {
            this.events.off('update', step);
            spr.destroy();
            p.setVisible(true);
        };
    }

    // Her gag with the porter and his cart (§1.6, 8a to 8d; `GAGS` cartDrape, cartPush, cartSit,
    // cartBounce): one picture of her (with the cart in it for 8a and 8c, set down by the world's
    // cart's middle, which is hidden), while the porter stands, follows her with his cart, wheels
    // her on or turns round. Doors and walls stop him (`stopShort`). Then her checkpoint; he walks on.
    cartGag(sc, q) {
        const p = this.player, g = GAGS[sc.gag], pe = this.world.people, face = p.flipX ? -1 : 1;
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(g.word ?? sc.word)).setVisible(true);
        this.script = null;
        const dx = q.attached[0]?.dx ?? 24, walk = q.walk.clip ?? 'walk', v = q.walk.v * 48;
        // (He stands at his handle: his push's first frame, held.)
        const hold = () => { q.sprite.anims.stop(); q.sprite.setFrame(q.meta.anims[walk]?.[0] ?? q.meta.stand); };
        const move = (x) => { q.x = x; pe.place(q); };
        q.state = 'acting';
        q.busy = true;
        hold();
        // (Each picture has her facing east: 8a's cart coming at her, 8c's up behind her. Set down
        // where she stands; the porter is brought the last few px up to it.)
        const x = g.cart ? p.x + face * g.cartAt : p.x - face * g.her;
        if (g.cart) move(x - q.dir * dx);
        const s = this.add.sprite(x, q.y, 'her-mishaps').setOrigin(0.5, 1).setFlipX(face < 0).setDepth(p.depth);
        this.worldLayer.add(s);
        p.setVisible(false);
        if (g.cart) for (const a of q.attached) a.img.setVisible(false);
        this.gagEnd = () => {
            s.destroy();
            p.setVisible(true);
            for (const a of q.attached) a.img.setVisible(true);
            q.busy = false;
            pe.place(q);
            pe.idle(q);
            q.pausedUntil = this.time.now + 600;
        };
        const end = () => this.time.delayedCall(g.holdMs, () => this.respawn());
        s.play(g.clip);
        if (g.fronts) {
            // 8b: he pushes on, blind behind his bags, the cart's front at hers, till she is down.
            pe.anim(q, walk);
            this.script = () => {
                const k = Math.min((s.anims.currentFrame?.index ?? 1) - 1, g.fronts.length - 1);
                const want = p.x + face * g.fronts[k], at = q.x + q.dir * (dx + 14);
                // (Only ever on toward her, never further than she is pushed.)
                if ((want - at) * q.dir > 0) move(this.stopShort(q.x, q.x + (want - at), q.y, dx + 14));
            };
            s.once(`animationcomplete-${g.clip}`, () => { this.script = null; hold(); end(); });
        } else if (g.walkOnMs) {
            // 8d: he walks on a few steps before he notices, then turns round to her (his cart
            // stays where it is, in front of him).
            pe.anim(q, walk);
            const stop = this.stopShort(q.x, q.x + q.dir * (v * g.walkOnMs / 1000), q.y, dx + 14);
            this.script = (dt) => {
                const step = Math.min(v * dt, Math.abs(stop - q.x));
                move(q.x + q.dir * step);
                if (Math.abs(stop - q.x) < 0.5) {
                    this.script = null;
                    q.sprite.anims.stop();
                    q.sprite.setFrame(q.meta.stand).setFlipX(q.dir > 0);
                }
            };
            s.once(`animationcomplete-${g.clip}`, end);
        } else if (g.rideM) {
            // 8c: sat in his bags; he wheels her on, sees her and tips his cap.
            s.once(`animationcomplete-${g.clip}`, () => {
                const to = this.stopShort(s.x, s.x + q.dir * g.rideM * 48, q.y, 16);
                pe.anim(q, walk);
                this.script = (dt) => {
                    const step = Math.min(v * dt, Math.abs(to - s.x));
                    s.x += q.dir * step;
                    move(q.x + q.dir * step);
                    p.x = s.x;
                    if (Math.abs(to - s.x) < 0.5) {
                        this.script = null;
                        pe.anim(q, g.tip, { loop: false });
                        q.sprite.once('animationcomplete', () => { hold(); end(); });
                    }
                };
            });
        } else {
            // 8a: over the bags, her legs kicking; he stands there.
            s.once(`animationcomplete-${g.clip}`, () => { if (g.loop) s.play(g.loop); end(); });
        }
    }

    // Her gags with the jogger (§1.6, 9a to 9d; `GAGS` jogSpin, jogBowled, jogShoved, jogBounce): her clip
    // where she stands (`gags` sheet, her middle at `jog.x` of its cell, or `jog[at]`'s first, its second
    // where she ends): 9b he runs into her standing facing him, bowled back onto her bottom; 9a head on, both
    // running, spun round like a top (a clip from each odd frame of her run, an even one taken as the next);
    // 9c into her back, she stumbles and belly-flops. In 9b and 9c he stops where he met her, his far arm up
    // to scratch the back of his head, sorry (his `sorry` clip, then `scratch` until her checkpoint); in 9a
    // he runs on. Where she ends dizzy (`dazed`), her own dazed clip takes over from the clip's last frame
    // (its first frame). 9d: 8d's bounce off his back (`cartGag`'s picture), and he never notices. The stage's
    // light plays 9a's and 9c's (12a, 12b): no one with it (`q` null), on the floor she stands on. The court's
    // basketballs (14a, 14b) the same way, with their own clips (`meta: 'ball'`) and a lying loop after them (`lie`).
    jogGag(sc, q) {
        const p = this.player, g = GAGS[sc.gag], pe = this.world.people, face = p.flipX ? -1 : 1;
        const m = this.cache.json.get('gags-meta');
        const n = runFrame(p);
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(g.word ?? sc.word)).setVisible(true);
        this.script = null;
        p.body.setVelocity(0, 0);
        const end = () => this.time.delayedCall(g.holdMs, () => this.respawn());
        if (g.bounce) {
            // 9d: as 8d's picture is placed; he runs on.
            const s = this.add.sprite(p.x - face * g.her, q.y, 'her-mishaps').setOrigin(0.5, 1).setFlipX(face < 0).setDepth(p.depth);
            this.worldLayer.add(s);
            p.setVisible(false);
            this.gagEnd = () => { s.destroy(); p.setVisible(true); };
            s.play(g.clip);
            s.once(`animationcomplete-${g.clip}`, end);
            return;
        }
        // (Not running, or landed from a jump: the spin from her standing frame.)
        const tag = n >= 0 ? (n % 2 ? n : (n + 1) % 8) : '-stand';
        const clip = g.clips ? `${g.clips}${tag}` : g.clip;
        const mm = m[g.meta ?? 'jog'];
        const [x0, x1] = g.at ? mm[g.at] : [mm.x, mm.x];
        // (A frame anchored at column c, flipped, takes origin (cell - 1 - c) / cell.)
        const ox = (face < 0 ? m.cell - 1 - x0 : x0) / m.cell;
        const s = this.add.sprite(p.x, q ? q.y : p.y, 'gags').setOrigin(ox, m.floor / m.cell).setFlipX(face < 0).setDepth(p.depth);
        this.worldLayer.add(s);
        // (Where the clip carries her on, a door or a wall across the deck ahead stops her short of it: the clip
        // starts as far back as it would have taken her through.)
        if (x1 !== x0) s.x -= face * (x1 - x0) - (this.stopShort(p.x, p.x + face * (x1 - x0), s.y, 12) - p.x);
        p.setVisible(false);
        if (g.his) {
            q.state = 'acting';
            q.busy = true;
            // (A door he was going through shuts behind him: held open, its leaf drawn in front of them
            // hid her fall.)
            if (q.through) {
                this.letGoDoor(q.through, q);
                q.through = null;
            }
            // (Turned to her, where he met her.)
            q.dir = p.x < q.x ? -1 : 1;
            pe.place(q);
            pe.anim(q, g.his, { loop: false });
            q.sprite.once('animationcomplete', () => { if (q.busy) pe.anim(q, g.loop); });
        }
        this.gagEnd = () => {
            s.destroy();
            p.setVisible(true);
            if (!g.his) return;
            q.busy = false;
            pe.place(q);
            pe.idle(q);
            q.pausedUntil = this.time.now + 600;
        };
        s.play(clip);
        s.once(`animationcomplete-${clip}`, () => {
            // (14a, 14b: lying where the clip ends, the butterflies circling; a run's clip ends further on.)
            if (g.lie) {
                s.x += face * mm.dx[g.at][tag];
                s.play(g.lie);
            }
            if (g.dazed && this.anims.exists(`her-dazed-${g.dazed}`)) {
                // Her own dazed clip from where the clip ends (its last frame is that clip's first).
                s.setVisible(false);
                p.x = s.x + face * (x1 - x0);
                p.setVisible(true);
                this.herDrop(LIE_DROP.px);
                this.herClip(`her-dazed-${g.dazed}`);
            }
            end();
        });
    }

    // 15, the drill's boat (the user, 2026-11-21): bumped on the head as she runs under it, she sinks onto all fours,
    // dizzy, the butterflies over her head (`drill-drop`), and crawls out from under it the way she was facing
    // (`drill-crawl`, `GAGS.boat.crawl` px a second) until she is clear of its end; the boat comes down as far as her
    // back (`DrillBoat`, `DRILL.pinPx`). Then `holdMs` and her checkpoint. Its pictures: tools/build_drill.py.
    crawlGag(sc, fromX) {
        const p = this.player, g = GAGS[sc.gag], face = p.flipX ? -1 : 1, m = this.cache.json.get('drill-meta');
        const boat = this.world.story.drill;
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(g.word ?? sc.word)).setVisible(true);
        this.script = null;
        p.body.setVelocity(0, 0);
        // (A frame anchored at column c, flipped, takes origin (cell - 1 - c) / cell.)
        const ox = (face < 0 ? m.cell - 1 - m.herX : m.herX) / m.cell;
        const s = this.add.sprite(p.x, p.y + this.herDropPx(), 'drill', m.drop[2]).setOrigin(ox, (m.herFloor + 1) / m.cell)
            .setFlipX(face < 0).setDepth(p.depth);
        this.worldLayer.add(s);
        p.setVisible(false);
        let crawl = null;
        const stop = () => this.events.off('update', crawl);
        this.gagEnd = () => { stop(); s.destroy(); p.setVisible(true); };
        s.play('drill-drop');
        s.once('animationcomplete-drill-drop', () => {
            s.play('drill-crawl');
            // Toward the boat's end on her side of its middle, short of a door or a wall, never off the screen and for
            // `crawlMs` at most (the user, 2026-11-21): then her checkpoint, as soon as the other gags end.
            const end = boat ? boat.cx + face * (boat.w / 2 + 22) : s.x + face * 60;
            // (The camera is on her body, where she was hit: the screen's edge is half its width from there.)
            const edge = p.x + face * (VIEW.width / 2 - 40);
            // (After `crawlMs` the screen fades to her checkpoint while she crawls on: she is still crawling when it is
            // dark, the user, 2026-11-21: "Don't stop her crouch until the screen fades away completely". Her sprite goes
            // with the fade's end, `gagEnd`.)
            const to = this.stopShort(s.x, face > 0 ? Math.min(end, edge) : Math.max(end, edge), s.y, 12);
            let ms = 0;
            crawl = (_, dt) => {
                ms += dt;
                if (ms >= g.crawlMs && !this.respawning) this.respawn();
                const left = to - s.x;
                if (Math.abs(left) >= 0.5 && Math.sign(left) === face) s.x += face * Math.min(Math.abs(left), g.crawl * dt / 1000);
            };
            this.events.on('update', crawl);
        });
    }

    // A slip or a trip with no tangerine on her (the user, 2026-11-16): she goes down, on her
    // bottom (`slipfall`) or flat on her belly (`tripfall`), then dazed where she fell, butterflies
    // circling over her head (`dazed-sit`, `dazed-lie`: drawn with her, as the user asked), and
    // then back at her checkpoint.
    scareDown(sc) {
        const p = this.player, slip = sc.down === 'sit';
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        sfx.scare();
        rumble('bump');
        this.alert.setText(fright(sc.word)).setVisible(true);
        this.script = null;
        const clip = slip ? 'her-slipfall' : 'her-tripfall';
        if (!this.anims.exists(clip)) {
            this.time.delayedCall(1600, () => this.respawn());
            return;
        }
        this.herClip(clip);
        // Down, flat on her belly or on her bottom, she is drawn 2 px lower, from the fall's first frame on the floor
        // until she is back at her checkpoint (the user, 2026-11-17: she lay a px or two over the carpet; 2026-11-26, the
        // sit the same; her cell ends at her lowest px, her hand under her chin, so it is done here, not in the art).
        {
            const down = () => {
                if (p.anims.currentAnim?.key !== clip || (p.anims.currentFrame?.index ?? 1) - 1 >= LIE_DROP.frame) {
                    this.herDrop(LIE_DROP.px);
                    p.off('animationupdate', down);
                }
            };
            p.on('animationupdate', down);
        }
        // Someone who comes to her while she lies there (the dog's lick, `Fetcher.lick()`) puts a
        // promise in `down.holds`: her checkpoint waits for each of them.
        const down = this.down = { holds: [] };
        // (`downMs`: dazed a shorter while than the stand-in's.)
        p.once(`animationcomplete-${clip}`, () => {
            const dazed = slip ? 'her-dazed-sit' : 'her-dazed-lie';
            if (this.anims.exists(dazed)) this.herClip(dazed);
            this.time.delayedCall(sc.downMs ?? 2100, () => Promise.all(down.holds).then(() => {
                if (this.down === down) this.respawn();
            }));
        });
    }

    // How many px lower than her body her picture is drawn now (`herDrop`): a picture that takes
    // her place (a gag) is set down by it too.
    herDropPx() {
        const p = this.player;
        return Math.round(p.height - p.displayOriginY);
    }

    // Hit in the air under the parasol (a gull across her way down to the bow): it is knocked out
    // of her hands, and down she goes out of the bottom of the screen.
    scareAir(what, { snatch = null } = {}) {
        const p = this.player;
        if (this.mode !== 'play') return;
        const id = scenario(what, {}), sc = MISHAP_SCENES[id];
        if (this.isSafe()) return;
        this.lastMishap = { what, id, time: this.time.now };    // (as every hit: its gag's sounds and the playtests read it)
        if (this.pocket(p.x - (p.flipX ? -1 : 1) * 10, sc, { snatch })) return;
        this.gliding = false;
        this.world.showParasol(false);
        this.takeoffY = p.y;
        if (sc.gag && GAGS[sc.gag]?.air && this.cache.json.get('gags-meta')?.anims['parasol-flip']) return this.parasolGag(sc);
        sfx.scare();
        rumble('bump');
        this.scareFall();
        this.alert.setText(fright(sc.word)).setVisible(true);
        if (this.anims.exists('her-hit')) this.herClip('her-hit');
    }

    // 22: a gull across her glide with no tangerine on her. One picture of her with the parasol (its
    // frame 0 is her glide's with the world's parasol, to the px): it is blown inside out while she still
    // sinks at the glide's pace, then she looks up at it and kicks her legs as she drops, a softer fall
    // than a closed parasol's; the camera lets go and she leaves the bottom of the screen.
    parasolGag(sc) {
        const p = this.player, g = GAGS[sc.gag], gm = this.cache.json.get('gags-meta'), A = gm.anims['parasol-flip'];
        this.beginScare();
        this.airScare = true;
        this.scareFrom = { x: p.x, y: this.takeoffY };
        sfx.scare();
        sfx.parasolShut();
        rumble('bump');
        this.alert.setText(fright(g.word ?? sc.word)).setVisible(true);
        p.setVisible(false);
        const flip = p.flipX, [fx, fy] = gm.parasol.feet;
        // (Phaser mirrors a frame in place: flipped, her feet's edge is counted from the right.)
        // (In front of everything, as her fall is: she drops past the decks.)
        const spr = this.add.sprite(p.x, p.y, 'gags', A[1]).setDepth(DEPTH.fx).setFlipX(flip)
            .setOrigin((flip ? gm.cell - fx : fx) / gm.cell, fy / gm.cell);
        this.alertOver = fy - 16 - PLAYER.height + 2;          // (her word over the parasol's top, not on it)
        const flipFor = 3 * g.flipMs;
        let vy = Math.min(p.body.velocity.y, VERBS.glideFall), e = 0, top = fy - 16;   // (the parasol's top over her feet)
        this.script = (dt) => {
            e += dt * 1000;
            if (e >= flipFor) vy = Math.min(vy + g.fall * dt, g.maxFall);
            p.y += vy * dt;
            const k = e < flipFor ? 1 + Math.floor(e / g.flipMs) : 4 + Math.floor((e - flipFor) / g.kickMs) % 5;
            spr.setFrame(A[k]).setPosition(Math.round(p.x), Math.round(p.y));
            // (Out of the screen once the parasol's top is: it stands `top` px over her feet.)
            if (p.y - top > this.cameras.main.worldView.bottom) this.respawn();
        };
        this.gagEnd = () => {
            spr.destroy();
            p.setVisible(true);
            this.alertOver = 0;
        };
    }

    // Longer than one deck: the camera lets go and she drops out of the bottom of the screen.
    scareFall() {
        const p = this.player;
        let vy = p.body.velocity.y;
        this.beginScare();
        this.airScare = true;
        this.scareFrom = { x: p.x, y: this.takeoffY };
        p.setDepth(DEPTH.fx);
        this.pose('fall');
        sfx.fall();
        rumble('fall');
        this.script = (dt) => {
            vy = Math.min(vy + PLAYER.gravity * dt, PLAYER.maxFall * 1.5);
            p.y += vy * dt;
            if (p.y - 40 > this.cameras.main.worldView.bottom) this.respawn();
        };
    }

    // Overboard: no drowning. A splash, then she bobs up smiling in a life ring, waving to us.
    scareOverboard() {
        const p = this.player;
        this.beginScare();
        this.scareFrom = { x: Phaser.Math.Clamp(this.player.x, this.hullMinX + 16, this.hullMaxX - 16), y: this.takeoffY };
        this.cameras.main.startFollow(p, true, 0.15, 0.15);
        sfx.splash();
        rumble('overboard');
        this.splash(p.x, this.waterY);
        // Facing the camera, smiling and waving; only her top half shows above the water.
        const shown = PLAYER.cell - PLAYER.height + 32;
        this.pose('wave');
        p.setCrop(0, 0, PLAYER.cell, shown).setDepth(DEPTH.fx);
        p.y = this.waterY + PLAYER.cell - shown; // the crop's bottom edge sits on the water
        // The ring, seen from the side, round her waist: its far half behind her, its near half in front.
        const { width, height } = this.textures.getFrame('shipart', 'life-ring-side');
        const half = Math.floor(height / 2);
        const ring = [
            this.add.image(p.x, this.waterY, 'shipart', 'life-ring-side').setCrop(0, 0, width, half).setDepth(DEPTH.fx - 0.5),
            this.add.image(p.x, this.waterY, 'shipart', 'life-ring-side').setCrop(0, half, width, height - half).setDepth(DEPTH.fx + 0.5),
        ];
        this.worldLayer.add(ring);
        this.tweens.add({ targets: [p, ...ring], y: '-=2', duration: 300, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        this.script = null;
        this.time.delayedCall(1300, () => {
            this.respawn(() => {
                this.tweens.killTweensOf([p, ...ring]);
                ring.forEach(r => r.destroy());
            });
        });
    }

    // Something drawn in front of her that stands on her floor line (a railing, a fort, a bulwark's foot)
    // reaches `PLAYER.sink` px lower, its bottom row drawn again: her picture is drawn that much lower than
    // her foot, and where her feet are hidden behind it her lowest row must be too (the user, 2026-11-20).
    // Its placement is kept: the picture grows downward only. For an image with its origin at its foot.
    withFoot(img) {
        const n = PLAYER.sink, f = img.frame;
        if (!n) return img;
        const key = `${img.texture.key}~${f.name}~foot`;
        if (!this.textures.exists(key)) {
            const c = this.textures.createCanvas(key, f.cutWidth, f.cutHeight + n), ctx = c.getContext(), src = f.source.image;
            ctx.drawImage(src, f.cutX, f.cutY, f.cutWidth, f.cutHeight, 0, 0, f.cutWidth, f.cutHeight);
            for (let k = 1; k <= n; k++) ctx.drawImage(src, f.cutX, f.cutY + f.cutHeight - 1, f.cutWidth, 1, 0, f.cutHeight - 1 + k, f.cutWidth, 1);
            c.refresh();
        }
        const ox = img.originX;
        return img.setTexture(key).setOrigin(ox, f.cutHeight / (f.cutHeight + n));
    }

    // Her picture drawn `px` lower than her body (0: as always, which is `PLAYER.sink` lower than its foot),
    // its body kept where it is.
    herDrop(px, p = this.player) {
        const down = px + PLAYER.sink;
        p.setDisplayOrigin(p.width / 2, p.height - down);
        p.body.setOffset((PLAYER.cell - p.body.width) / 2, PLAYER.cell - p.body.height - down);
    }

    respawn(cleanup) {
        if (this.respawning) return;
        this.respawning = true;
        this.script = null;
        this.down = null;
        const from = this.scareFrom || { x: this.player.x, y: this.player.y };
        // (Over the bow she comes back where the glide starts: src/world/finale.js.)
        const target = this.world.story.respawnFor?.(from) || this.closestCheckpoint(from.x, from.y);
        this.tweens.add({
            targets: this.fade, alpha: 1, duration: 220,
            onComplete: () => {
                cleanup?.();
                this.gagEnd?.();                     // a gag's picture gone, the thing back in its place
                this.gagEnd = null;
                this.world.carryBox.drop();          // a tray is not hers to keep through a scare
                this.tweens.killTweensOf(this.player);
                this.herDrop(0);
                this.airScare = false;
                this.spawnAt(target, { emerge: true });
                this.tweens.add({ targets: this.fade, alpha: 0, duration: 260 });
                this.respawning = false;
                this.scareFrom = null;               // (no scare under way: src/popup.js keeps her popups in the view again)
            },
        });
    }

    // --- Screen-space overlays ------------------------------------------------------------------

    updateOverlays() {
        const p = this.player;
        const x = Math.round(p.x);
        const y = Math.round(p.y - (this.crawling ? 30 : PLAYER.height) - 3);
        this.bubble.setVisible(this.time.now < this.bubbleUntil).setPosition(x, y);
        // (`alertOver`: px more, over a thing held over her head, the inside-out parasol.)
        this.alert.setPosition(x, y - (this.alertOver ?? 0));
        if (this.debugText.visible) {
            this.debugText.setText(`${this.mode}  x ${p.x.toFixed(0)}  y ${p.y.toFixed(0)}  takeoff ${this.takeoffY?.toFixed(0)}`);
        }
    }
}

// Crawling, the wall jump, the glide, pushing (src/world/verbs.js).
Object.assign(ShipScene.prototype, verbs, balcony);
