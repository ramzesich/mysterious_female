// The plan's world (GAME_DESIGN.md §6.1, docs/population.md): what tools/population.py puts on the
// ship, read from maps/world.json: the rooms behind doors, the outside route (the promenade, the
// boat walkway, the balconies), the funnel's top, the duct, and every thing in place: checkpoints,
// tangerines, pickups, Bumbot's beats, switches, carts to push. The ship scene asks it what is at
// her feet (E, ladders, grips for a wall jump) and tells it what has happened (flags).

import { PLAYER, SWIM, CRY, MISHAPS, BED_JOY, VIEW, BOOKS } from '../config.js';
import { parseLock } from '../progression.js';
import { writeSave } from '../save.js';
import { sfx } from '../sfx.js';
import { rumble, rumbleNow } from '../rumble.js';
import { People } from './people.js';
import { Carry } from './carry.js';
import { Story } from './story.js';
import { Library, BOOK_COLOURS, BOOK_ACCENTS } from './library.js';
import { Robot, Gull, BellGull, SwingLight, Spill, Darter, TowelStack, Sprinkler, SwingDoor, DndDoor, Roller, Fetcher, Skimmer, Breakfast } from './movers.js';
import { WetPatch, FoodGulls, Queue, Trays } from './hazards.js';
import { Rounds } from './outside.js';
import { sign, SIGN_LOOKS } from '../signs.js';

export const OUTSIDE = 'promenade';     // the outside route (deck 6's promenade came first)
const ROOM = { height: 128, stop: 20 };
const OK = { ok: true };
// The knitting lady in her armchair: the chair was drawn round her own seated pose (its picture's
// left edge 16 px behind her middle, its foot on her floor), so she sits in it exactly.
const KNIT_SIT = { dx: 16, up: 0 };

// How a bare room looks until it is drawn (tools/draw_rooms.py): wall, skirting, floor.
const LOOKS = {
    laundry: [0xdfe8e2, 0x9babb2, 0x92a984], store: [0xc9c2b0, 0x7f708a, 0x8e98a3], crewcabin: [0xe6dcc8, 0xab947a, 0x4d65b4],
    pantry: [0xd9dee0, 0x9babb2, 0x8e98a3], galley: [0xeef2f2, 0x9babb2, 0xc7dcd0], nook: [0x6e4a3a, 0x45293f, 0xae2334],
    dressing: [0xe8c4c0, 0xab6f7a, 0x7f708a], lighting: [0x2e222f, 0x45293f, 0x3e3546], lifeboat: [0xf28c28, 0xcd683d, 0x9babb2],
    cabin: [0xefe6d2, 0xd8b29a, 0x4d65b4], balcabin: [0xefe6d2, 0xd8b29a, 0x4d65b4], adjoin: [0xefe6d2, 0xd8b29a, 0x4d65b4],
    coldroom: [0xcfeaf5, 0x8fd3ff, 0x9babb2],
};
const START_CHECKPOINT = 'cp_crew';     // her crew cabin's door on deck 3 (the user, 2026-11-14; it was the gangway's)
const DOOR_ART = { crew: 'door-crew', cabin: 'door-cabin', open: 'door-cabin-ajar', hatch: 'door-watertight' };
// The lifeboat's roof hatch (tools/build_hatch.py): its two pieces' top lefts from the walkway's floor under the hatch's
// middle (the boat's column 112, where E takes her in; the back at its column 91 and row 26, the lip at 90 and 37, the
// floor at its row 120).
const HATCH_PIECE = { back: { x: 91 - 112, y: 26 - 120 }, front: { x: 90 - 112, y: 37 - 120 } };
// The middle of its dark opening (the boat's rows 28 to 36), from the same point: where its glow comes from.
const HATCH_GLOW = { x: 2, y: 32 - 120 };
// Its ladder inside (tools/draw_rooms.py's): where she is put on it coming in (her head in the hatch), and how far she climbs
// it going out, until she is through the hatch and out of the picture.
const ROOF_LADDER = { start: 62, out: 128 };

// A gull's beak in each of its frames (the things atlas, px from the frame's top left): its tip's column
// and its row, for a tangerine carried in it (`inBeak`).
const GULL_BEAKS = { 'gull-up': [29, 16.5], 'gull-down': [27, 5.5], 'gull-perched': [19, 2] };

export class World {
    constructor(scene) {
        this.scene = scene;
        this.data = scene.cache.json.get('world');
        this.roofY = this.data.funnel.foot[1];
        this.carry = null;          // what she has in her hands (a tray: §6.1.2), from step 1
        this.things = [];           // everything placed: { id, x, y, route, needs, items, interact, done }
        this.pushables = [];
        this.low = [];              // things she must crawl under: { route, x0, x1, y }
        this.lows = [];             // and what stands over each: its zone, its picture
        this.grips = this.data.grips;
        this.pending = [];          // tangerines that appear on a flag
        this.solids = [];           // things to hop: standing carts
        this.breakables = [];       // things the dash goes through: stacked luggage, crates
        this.people = new People(this);
        this.carryBox = new Carry(this);
        this.story = new Story(this);
        this.library = new Library(this);
        this.movers = [];           // the delivery robot, the gulls
        this.winds = [];            // gusts, each over its own stretch (src/world/outside.js)
        this.peek = null;           // a route whose things show from afar (the telescope's view)
        this.built = false;
    }

    get save() { return this.scene.save; }
    get progress() { return this.scene.progress; }

    // Doors on the cabin corridors that take a cabin door's place (rooms, checkpoints).
    doorSpots() {
        const rooms = this.data.rooms.flatMap(r => r.doors.filter(d => d.outRoute === 'inside').map(d => ({ x: d.outX, y: d.outY })));
        // (And the doors that do something by themselves: the one that flies open, "Do Not Disturb";
        // the dog's owner's, open behind her.)
        const own = ['checkpoint', 'swingdoor', 'dnd', 'opendoor', 'dog'];
        const cps = this.data.ents.filter(e => own.includes(e.kind) && e.route === 'inside').map(e => ({ x: e.x, y: e.y }));
        return [...rooms, ...cps];
    }

    // --- Building -----------------------------------------------------------------------------

    build() {
        // ?did=horn,wedding: story flags set from the start, to look at a later state without
        // playing to it (README; for testing).
        const did = new URLSearchParams(location.search).get('did');
        for (const f of (did ?? '').split(',')) if (f && !this.save.flags.includes(f)) this.save.flags.push(f);
        // ?books=3,8,11 (or `all`): she starts carrying those books, in that order (README; for testing reading).
        const books = new URLSearchParams(location.search).get('books');
        const list = books === 'all' ? Array.from({ length: BOOKS }, (_, i) => i + 1) : (books ?? '').split(',').map(Number);
        for (const n of list) if (n >= 1 && n <= BOOKS && !this.save.books[n]) this.library.got(n);
        // (`books_all` means every book is back: the shelf full, as in play, the HUD counting fourteen.)
        if (this.save.flags.includes('books_all')) {
            for (let n = 1; n <= BOOKS; n++) {
                this.library.got(n);
                this.save.books[n] = 'returned';
            }
        }
        this.makeTextures();
        this.buildRooms();
        this.buildOutside();
        this.buildFunnel();
        this.buildDuct();
        for (const e of this.data.ents) this.buildEnt(e);
        this.library.build(this.data.library);
        this.buildSpecials();
        this.story.setup();
        // The key cards lying on a table or on the deck twinkle as the pickups do.
        for (const c of this.progress.cards) this.glint(c.items[0]);
        this.built = true;
        if (this.progress.has('drain')) this.drainPool(true);
        this.refresh();
    }

    depthFor(route) {
        const D = this.scene.DEPTH;
        return route === 'inside' ? D.props : D.exterior + 0.13;
    }

    add(items) {
        this.scene.worldLayer.add(items);
        return items;
    }

    // Small pictures drawn here until the real ones are made (the steps of docs/build-plan.md).
    makeTextures() {
        const s = this.scene;
        const make = (key, w, h, draw) => {
            if (s.textures.exists(key)) return;
            const g = s.make.graphics({ x: 0, y: 0 }, false);
            draw(g);
            g.generateTexture(key, w, h);
            g.destroy();
        };
        this.carryBox.textures();
        // A pickup's glint (the user, 2026-11-20: "a tiny spark animation", "much softer, and slower", "also
        // rotate"): a four-point star, "+" and "x" (the only turns whose rays are straight in pixels: "every
        // frame shall have the rays straight", the user) at three sizes (a dot, its arms one px, two px),
        // frame `turn * 3 + size`. Turned by its frames in eighth-turns, never by rotating the picture, which
        // left ragged pixels ("LCD traces").
        if (!s.textures.exists('spark')) {
            const c = s.textures.createCanvas('spark', 6 * 7, 7), ctx = c.getContext();
            const W = '#ffffff', Y = '#fbff86';
            // One arm's pixels at each turn, near to far (the other three arms are it turned by 90).
            const ARMS = [[[1, 0], [2, 0]], [[1, 1], [2, 2]]];
            for (let turn = 0; turn < 2; turn++) {
                for (let size = 0; size < 3; size++) {
                    const f = turn * 3 + size, px = (x, y, col) => { ctx.fillStyle = col; ctx.fillRect(f * 7 + 3 + x, 3 + y, 1, 1); };
                    px(0, 0, W);
                    ARMS[turn].slice(0, size).forEach(([x, y], d) => {
                        const col = d === size - 1 ? Y : W;
                        px(x, y, col); px(-y, x, col); px(-x, -y, col); px(y, -x, col);
                    });
                    c.add(f, 0, f * 7, 0, 7, 7);
                }
            }
            c.refresh();
        }
        // Region 6: the pool attendant's hut (a checkpoint's door stands in it); the painter's bucket.
        make('pool-hut', 50, 96, g => {
            g.fillStyle(0x2e222f, 1).fillRect(3, 8, 44, 88);
            g.fillStyle(0xf4f4f4, 1).fillRect(4, 9, 42, 87);
            g.fillStyle(0xc7dcd0, 1).fillRect(4, 9, 3, 87).fillRect(43, 9, 3, 87);
            g.fillStyle(0x2e222f, 1).fillRect(0, 2, 50, 8);
            g.fillStyle(0x4d9be6, 1).fillRect(1, 3, 48, 6);
            for (let x = 1; x < 49; x += 12) g.fillStyle(0xffffff, 1).fillRect(x, 3, 6, 6);
            g.fillStyle(0xe83b3b, 1).fillRect(21, 12, 8, 2).fillRect(24, 9, 2, 8);
        });
        make('paint-bucket', 14, 12, g => {
            g.fillStyle(0x2e222f, 1).fillRect(1, 3, 12, 9).fillRect(0, 2, 14, 2);
            g.fillStyle(0x9babb2, 1).fillRect(2, 4, 10, 7);
            g.fillStyle(0x4d9be6, 1).fillRect(1, 2, 12, 1).fillRect(4, 4, 3, 5);
            g.fillStyle(0x2e222f, 1).fillRect(3, 0, 8, 1).fillRect(2, 1, 1, 1).fillRect(11, 1, 1, 1);
        });
        BOOK_COLOURS.forEach((c, i) => make(`book-${i + 1}`, 10, 13, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 10, 13);
            g.fillStyle(c, 1).fillRect(1, 1, 8, 11);
            g.fillStyle(0xf3ecdd, 1).fillRect(8, 2, 1, 9);
            g.fillStyle(BOOK_ACCENTS[i], 1).fillRect(3, 3, 4, 1);
        }));
        // (The grip socks and the stage manager's pills were drawn here until 2026-11-20: now their
        // close-ups' pictures, `grip-socks` and `pills-bottle` among the things.)
        // (The old lady's parasol, furled and open, is PixelLab's: `parasol-closed`, `parasol-open`
        // among the things.)
        make('switch-box', 14, 22, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 14, 22);
            g.fillStyle(0xf9c22b, 1).fillRect(1, 1, 12, 20);
            g.fillStyle(0xae2334, 1).fillRect(5, 4, 4, 10);
        });
        // One photo in the gallery's rows (`sec_cat_photo`): an empty deck, a black tail leaving the frame.
        make('photo-cat', 26, 25, g => {
            g.fillStyle(0x7a4528, 1).fillRect(0, 0, 26, 25);
            g.fillStyle(0xd8cdb8, 1).fillRect(2, 2, 22, 21);
            g.fillStyle(0x9fc4d6, 1).fillRect(3, 3, 20, 10);
            g.fillStyle(0x7fa8bd, 1).fillRect(3, 11, 20, 2);
            g.fillStyle(0xc9b79a, 1).fillRect(3, 13, 20, 9);
            g.fillStyle(0xab947a, 1).fillRect(3, 16, 20, 1).fillRect(3, 19, 20, 1);
            g.fillStyle(0x2e222f, 1).fillRect(20, 14, 3, 6).fillRect(18, 9, 2, 6).fillRect(19, 8, 2, 2).fillRect(19, 13, 3, 2);
        });
        // The Library's "QUIET PLEASE" rope stand as Bumbot left it: both posts down, the rope slack
        // between them, the sign face up on the floor.
        make('rope-down', 46, 9, g => {
            const ink = 0x2e222f, gold = 0xd9a43b, pale = 0xf9c22b;
            for (const x of [0, 26]) {
                g.fillStyle(ink, 1).fillRect(x, 1, 4, 8).fillRect(x + 3, 3, 16, 4).fillRect(x + 18, 2, 3, 6);
                g.fillStyle(gold, 1).fillRect(x + 1, 2, 2, 6).fillRect(x + 4, 4, 14, 2);
                g.fillStyle(pale, 1).fillRect(x + 19, 3, 1, 4).fillRect(x + 4, 4, 14, 1);
            }
            g.fillStyle(0xae2334, 1).fillRect(17, 7, 4, 1).fillRect(20, 8, 8, 1).fillRect(27, 7, 3, 1);
            g.fillStyle(ink, 1).fillRect(8, 0, 13, 3);
            g.fillStyle(0xf3ecdd, 1).fillRect(9, 0, 11, 2);
        });
        // The stage: the microphone's cable, coiled on the boards.
        make('cable', 24, 5, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 3, 24, 2).fillRect(8, 1, 9, 2).fillRect(6, 2, 2, 2).fillRect(17, 2, 2, 2);
            g.fillStyle(0x625565, 1).fillRect(9, 2, 7, 1);
        });
        // The Art Gallery's painting of a black cat on its easel (`sec_cat_painting`).
        make('easel-cat', 36, 61, g => {
            const ink = 0x2e222f, wood = 0x7a4528;
            g.fillStyle(wood, 1).fillRect(17, 0, 2, 8).fillRect(6, 40, 2, 21).fillRect(28, 40, 2, 21).fillRect(17, 40, 2, 16).fillRect(4, 38, 28, 3);
            g.fillStyle(ink, 1).fillRect(3, 6, 30, 33);
            g.fillStyle(0xd9a43b, 1).fillRect(4, 7, 28, 31);
            g.fillStyle(0xf68181, 1).fillRect(6, 9, 24, 27);
            g.fillStyle(0xf9c22b, 1).fillCircle(24, 15, 4);
            // The sitter: a black cat, its back to us, its tail curled, one ear turned.
            g.fillStyle(0x14121a, 1).fillEllipse(16, 29, 12, 13).fillCircle(16, 20, 5).fillTriangle(11, 18, 12, 12, 15, 17).fillTriangle(21, 18, 20, 12, 17, 17);
            g.fillRect(21, 32, 6, 2).fillRect(26, 28, 2, 5);
            g.fillStyle(0xb9e04c, 1).fillRect(13, 19, 2, 2).fillRect(17, 19, 2, 2);
        });
        // The theatre's scenery flats, leaning by the aft flight (`blk_scenery`): a palm, a setting sun.
        make('flat-palm', 30, 62, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 30, 62);
            g.fillStyle(0x8fd3ff, 1).fillRect(1, 1, 28, 60);
            g.fillStyle(0xf9c22b, 1).fillRect(1, 48, 28, 13);
            g.fillStyle(0x7a4528, 1).fillRect(13, 20, 4, 30);
            g.fillStyle(0x1ebc73, 1).fillEllipse(8, 18, 14, 6).fillEllipse(22, 18, 14, 6).fillEllipse(15, 13, 8, 12).fillEllipse(6, 24, 8, 5).fillEllipse(24, 24, 8, 5);
            g.fillStyle(0xab947a, 1).fillRect(1, 30, 28, 1).fillRect(14, 1, 1, 60);
        });
        make('flat-sun', 36, 46, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 36, 46);
            g.fillStyle(0xf68181, 1).fillRect(1, 1, 34, 44);
            g.fillStyle(0xf9c22b, 1).fillCircle(18, 26, 10);
            g.fillStyle(0x4d65b4, 1).fillRect(1, 27, 34, 18);
            g.fillStyle(0xf9c22b, 1).fillRect(12, 30, 12, 1).fillRect(14, 34, 8, 1).fillRect(16, 38, 4, 1);
            g.fillStyle(0xab947a, 1).fillRect(1, 22, 34, 1).fillRect(17, 1, 1, 44);
        });
        make('crate-big', 30, 26, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 30, 26);
            g.fillStyle(0xab947a, 1).fillRect(1, 1, 28, 24);
            g.fillStyle(0x7a4528, 1).fillRect(1, 7, 28, 1).fillRect(1, 18, 28, 1).fillRect(9, 1, 1, 24).fillRect(20, 1, 1, 24);
            g.fillStyle(0xf28c28, 1).fillRect(12, 10, 6, 6);
            g.fillStyle(0x1ebc73, 1).fillRect(14, 9, 2, 1);
        });
        // Region 5: the duct's grille in deck 8's ceiling, shut and hanging open; paw prints in dust;
        // party balloons, one and a bunch on their strings; an open cabin with the sea in its window.
        make('grille-shut', 32, 8, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 32, 8);
            g.fillStyle(0x9babb2, 1).fillRect(1, 1, 30, 6);
            g.fillStyle(0x3e3546, 1);
            for (let x = 3; x < 30; x += 4) g.fillRect(x, 2, 2, 4);
        });
        make('grille-open', 34, 30, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 32, 8);
            g.fillStyle(0x0d0b14, 1).fillRect(1, 1, 30, 6);
            g.fillStyle(0x2e222f, 1).fillRect(27, 6, 7, 24);
            g.fillStyle(0x9babb2, 1).fillRect(28, 7, 5, 22);
            g.fillStyle(0x3e3546, 1);
            for (let y = 9; y < 28; y += 4) g.fillRect(29, y, 3, 2);
        });
        make('paws', 346, 5, g => {
            g.fillStyle(0x625565, 0.85);
            for (let x = 4, n = 0; x < 340; x += 13, n++) {
                const y = n % 2 ? 3 : 1;
                g.fillRect(x, y, 3, 2).fillRect(x - 1, y - 1, 1, 1).fillRect(x + 1, y - 1, 1, 1).fillRect(x + 3, y - 1, 1, 1);
            }
        });
        make('balloon', 16, 20, g => {
            g.fillStyle(0x2e222f, 1).fillEllipse(8, 9, 16, 18).fillTriangle(6, 17, 10, 17, 8, 20);
            g.fillStyle(0xffffff, 1).fillEllipse(8, 9, 14, 16);
            g.fillStyle(0xffffff, 1).fillTriangle(7, 17, 9, 17, 8, 19);
        });
        make('balloons', 48, 58, g => {
            const bunch = [[10, 13, 0xe83b3b], [24, 9, 0xf9c22b], [38, 14, 0x4d9be6], [16, 27, 0xf68181], [32, 26, 0x1ebc73], [24, 39, 0xf28c28]];
            g.lineStyle(1, 0xf3ecdd, 1);
            for (const [x, y] of bunch) g.lineBetween(x, y + 8, 24, 57);
            for (const [x, y, c] of bunch) {
                g.fillStyle(0x2e222f, 1).fillEllipse(x, y, 17, 19);
                g.fillStyle(c, 1).fillEllipse(x, y, 15, 17);
                g.fillStyle(0xffffff, 0.8).fillRect(x - 4, y - 5, 2, 3);
            }
        });
        make('peek-sea', 34, 74, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 34, 74);
            g.fillStyle(0xece3cf, 1).fillRect(2, 2, 30, 72);
            // (Inside a room, washed 30% toward the wall, as the knitting lady's: the user, 2026-11-18,
            // "Let's make its interior more washed out colors, like we usually do".)
            const wash = c => {
                const w = 0xece3cf, k = 0.3, ch = sh => Math.round(((c >> sh) & 255) * (1 - k) + ((w >> sh) & 255) * k);
                return (ch(16) << 16) | (ch(8) << 8) | ch(0);
            };
            const fill = c => g.fillStyle(wash(c), 1);
            fill(0x7f708a).fillRect(7, 9, 24, 2);
            fill(0xcd683d).fillRect(10, 12, 20, 28);
            fill(0x8fd3ff).fillRect(12, 14, 16, 24);
            fill(0x4d9be6).fillRect(12, 27, 16, 11);
            fill(0xffffff).fillRect(12, 26, 16, 1).fillRect(15, 17, 6, 2).fillRect(14, 31, 4, 1).fillRect(21, 34, 5, 1);
            fill(0x7f708a).fillRect(8, 11, 3, 31).fillRect(29, 11, 3, 31);
            fill(0x9e4539).fillRect(8, 66, 24, 6);
            fill(0xffffff).fillRect(8, 52, 24, 14);
            fill(0xc7dcd0).fillRect(8, 59, 24, 1);
            fill(0x0b5e65).fillRect(15, 52, 8, 14);
            g.fillStyle(0x9babb2, 1).fillRect(2, 72, 30, 2);
            // The door's leaf, swung in against the wall.
            g.fillStyle(0x9e4539, 1).fillRect(2, 2, 5, 70);
            g.fillStyle(0xcd683d, 1).fillRect(3, 3, 3, 68);
        });
        // Region 1's (docs/plan-three-uses.md §4.2): her open cabin, an armchair just inside the door.
        // (The climb's shelf, the knitting lady's basket and the little desk flags are generated now:
        // `things`, the art rule looked back over, the user, 2026-11-17.)
        make('peek-knit', 34, 74, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 34, 74);
            g.fillStyle(0xece3cf, 1).fillRect(2, 2, 30, 72);
            // A picture on the wall within, in a gilt frame: a red flower in a vase (the user,
            // 2026-11-16: a green and blue landscape read as a flag upside down). Below it, the end
            // of her bed with its runner. Inside a room, washed 30% toward the wall (CLAUDE.md;
            // the user, 2026-11-16: they had been in full colours).
            const wash = c => {
                const w = 0xece3cf, k = 0.3, ch = sh => Math.round(((c >> sh) & 255) * (1 - k) + ((w >> sh) & 255) * k);
                return (ch(16) << 16) | (ch(8) << 8) | ch(0);
            };
            const fill = (c, x, y, w, h) => g.fillStyle(wash(c), 1).fillRect(x, y, w, h);
            fill(0xa05b53, 14, 10, 14, 16);
            fill(0xf9c22b, 15, 11, 12, 14);
            fill(0xf3ecdd, 16, 12, 10, 12);
            fill(0x239063, 21, 16, 1, 5); fill(0x239063, 19, 18, 2, 1); fill(0x239063, 22, 17, 2, 1);
            fill(0xe83b3b, 20, 13, 3, 3);
            fill(0xf9c22b, 21, 14, 1, 1);
            fill(0x4d9be6, 19, 21, 5, 3);
            fill(0x2e222f, 8, 52, 24, 20);
            fill(0xffffff, 9, 53, 23, 13);
            fill(0xc7dcd0, 9, 60, 23, 1);
            fill(0x905ea9, 9, 56, 23, 3);
            fill(0x6e2727, 9, 66, 23, 6);
            g.fillStyle(0x9babb2, 1).fillRect(2, 72, 30, 2);
            // The door's leaf, swung in against the wall.
            g.fillStyle(0x9e4539, 1).fillRect(2, 2, 5, 70);
            g.fillStyle(0xcd683d, 1).fillRect(3, 3, 3, 68);
        });
        make('hatch-lid', 28, 5, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 28, 5);
            g.fillStyle(0x9babb2, 1).fillRect(1, 1, 26, 3);
            g.fillStyle(0xf9c22b, 1).fillRect(12, 1, 4, 3);
        });
    }

    // --- Rooms behind doors (population §1 `room`) ---------------------------------------------

    buildRooms() {
        const s = this.scene, D = s.DEPTH;
        this.rooms = {};
        for (const def of this.data.rooms) {
            const key = s.textures.exists(`room-${def.id}`) ? `room-${def.id}` : this.bareRoom(def);
            const img = s.add.image(def.x0, def.floor - ROOM.height, key).setOrigin(0).setDepth(D.exterior + 0.12).setVisible(false);
            const dim = s.roomDim(img);
            this.add([dim, img]);
            // (Its pixels in front of the things that lie in it, over its tangerines: tools/draw_rooms.py.)
            const front = def.front ? s.add.image(def.x0, def.floor - ROOM.height, `room-${def.id}-front`).setOrigin(0)
                .setDepth(D.exterior + 0.135).setVisible(false) : null;
            if (front) this.add([front]);
            // (A room entered from outside, the lifeboat, is seen through the ship's closed side: the deck behind it
            // is not cut open, the user, 2026-11-21: "The cut away must show the outside of the hull".)
            const room = { id: def.id, route: def.id, door: def.doors[0].outX, floor: def.floor, room: img, dim, front,
                           inDeck: !def.doors.some(d => d.outRoute === OUTSIDE),
                           doors: def.doors, def, needs: def.needs, hidden: false, outside: [] };
            // (Its dim then goes over what the outside draws in front of her too, the balconies' fronts: they showed
            // undimmed over it. It frames the room, so neither the room nor she is under it.)
            if (!room.inDeck) dim.setDepth(D.player + 0.35);
            for (const d of def.doors) {
                d.lockSpec = parseLock(d.lock);
                const out = d.outRoute === OUTSIDE;
                const art = DOOR_ART[d.kind];
                // A way in through a boat's roof hatch (the lifeboat, the user, 2026-11-21): the hatch laid on its boat,
                // in front of her as the boat is (tools/build_hatch.py: her climb up into it, the scene's `roofClimb`).
                if (d.kind === 'roof') {
                    // Its ladder inside, up to the hatch: on its top as she comes in; up past its top, out.
                    // (`y1` its top as far as she climbs, out of the picture through the hatch; `start` where she is put on it
                    // coming in, her head in the hatch; `ceil` the room's top, where her picture is cut.)
                    (this.roofLadders ??= []).push({ room, x: d.x, y0: def.floor, y1: def.floor - ROOF_LADDER.out,
                        start: def.floor - ROOF_LADDER.start, ceil: def.floor - ROOM.height, routeBottom: def.id, routeTop: null,
                        out: () => s.roofOut(room, d) });
                    // (Its back, the far rim and the dark opening, behind her picture; its near lip over it.)
                    // (A faint warm glow out of the opening while she stands where E takes her in: the user, 2026-11-21. The
                    // inside's lamp light, in soft layers over the opening's dark, under its lip; faded in and out by the
                    // ship scene, `updateRoofGlow`.)
                    const glow = s.add.graphics().setDepth(D.player + 0.063).setAlpha(0);
                    const gx = d.outX + HATCH_GLOW.x, gy = d.outY + HATCH_GLOW.y;
                    glow.fillStyle(0xfbb954, 0.35).fillRect(gx - 17, gy - 3, 35, 8);
                    for (const [w, h, a] of [[30, 10, 0.16], [44, 20, 0.08], [58, 32, 0.05]]) glow.fillStyle(0xfbb954, a).fillEllipse(gx, gy - h / 4, w, h);
                    this.add([glow]);
                    room.outside.push(glow);
                    (this.roofGlows ??= []).push({ glow, d, shown: 0 });
                    for (const [part, depth] of [['back', D.player + 0.062], ['front', D.player + 0.068]]) {
                        const at = HATCH_PIECE[part];
                        const hatch = s.add.image(d.outX + at.x, d.outY + at.y, 'things', `lifeboat-hatch-${part}`).setOrigin(0).setDepth(depth);
                        this.add([hatch]);
                        room.outside.push(hatch);
                        s.shellSlopes.push({ deck: [6, 7], gfx: hatch });
                    }
                }
                if (art) {
                    // (Outside, the lifeboat's hatch is on the boat, which is in front of her: ShipScene's BOAT_DEPTH.)
                    const door = s.add.image(d.outX, d.outY, 'shipart', art).setOrigin(0.5, 1).setDepth(out ? D.player + 0.065 : D.props);
                    this.add([door]);
                    room.outside.push(door);
                    if (out) s.shellSlopes.push({ deck: [6, 7], gfx: door });
                }
                if (d.plate) {
                    // (Aft of its door, or forward of it where the deck ends just aft: `plateSide`.)
                    // (`plateUp`: a sign over the door, above a checkpoint's lamp: her crew cabin's.)
                    const side = d.plateSide ?? 1;
                    // (Brushed steel; navy on a dark wall, `plateStyle`: src/signs.js.)
                    const plate = sign(s, d.plateUp ? d.outX : d.outX + 20 * side, d.outY - (d.plateUp ? 93 : 50), d.plate, d.plateStyle ?? 'steel')
                        .setOrigin(d.plateUp ? 0.5 : side > 0 ? 0 : 1, 0.5).setDepth(D.props);
                    this.add([plate]);
                    room.outside.push(plate);
                }
                if (d.lockSpec?.kind === 'card') this.progress.reader(d.outX - 22, d.outY, d.lockSpec.card);
            }
            // (Her crew cabin's door, where the game starts, is lit from the start: population §2.5.)
            if (def.checkpoint === START_CHECKPOINT && !this.save.activated.includes(def.checkpoint)) this.save.activated.push(def.checkpoint);
            if (def.checkpoint) s.addCheckpoint(def.checkpoint, def.doors[0].outX, def.doors[0].outY, { door: null });
            s.rooms.push(room);
            // (Her crew cabin's forward end is her standing mirror: she stops in front of it.)
            if (def.mirror) room.mirror = def.x0 + def.mirror;
            s.addRouteWall(def.x0 + (def.mirror ?? ROOM.stop), -1, def.floor, def.id);
            s.addRouteWall(def.x0 + def.width - ROOM.stop, 1, def.floor, def.id);
            this.rooms[def.id] = room;
        }
        // The ones built before the plan, by their routes, for things placed in them.
        for (const r of s.rooms) if (!this.rooms[r.route]) this.rooms[r.route] = r;
    }

    // A bare room: its wall, ceiling, skirting and floor in its look's colours, a door at each way out.
    bareRoom(def) {
        const s = this.scene, key = `bare-${def.id}`;
        const [wall, trim, floor] = LOOKS[def.look] || LOOKS.cabin;
        const W = def.width, H = ROOM.height + 16;
        const tex = s.textures.createCanvas(key, W, H);
        const ctx = tex.getContext();
        const hex = c => `#${c.toString(16).padStart(6, '0')}`;
        const rect = (x, y, w, h, c) => { ctx.fillStyle = hex(c); ctx.fillRect(x, y, w, h); };
        rect(0, 0, W, H, wall);
        rect(0, 0, W, 8, 0xf4f6f3);
        rect(0, 8, W, 1, trim);
        for (let x = 0; x < W; x += 48) rect(x, 9, 1, ROOM.height - 13, trim);
        rect(0, ROOM.height - 4, W, 4, trim);
        rect(0, ROOM.height, W, 4, floor);
        rect(0, ROOM.height + 4, W, 12, 0x8e98a3);
        for (const d of def.doors) {
            const x = Math.round(d.x - def.x0);
            if (d.kind === 'balcony') {
                // A glass door onto the balcony, the sky in it.
                rect(x - 22, ROOM.height - 82, 44, 82, 0xf4f4f4);
                rect(x - 19, ROOM.height - 79, 38, 79, 0x8fd3ff);
                rect(x - 19, ROOM.height - 30, 38, 30, 0x4d9be6);
                rect(x - 1, ROOM.height - 79, 2, 79, 0xf4f4f4);
                continue;
            }
            const frame = s.textures.getFrame('shipart', DOOR_ART[d.kind] || 'door-crew');
            ctx.drawImage(frame.source.image, frame.cutX, frame.cutY, frame.width, frame.height,
                x - Math.round(frame.width / 2), ROOM.height - frame.height, frame.width, frame.height);
        }
        tex.refresh();
        return key;
    }

    // Whether a door of one of the plan's rooms lets her through (the scene's routeDoorAt found it).
    doorPasses({ d, leaving }) {
        const P = this.progress, lock = d.lockSpec;
        if (!lock || P.openAll) return OK;
        switch (lock.kind) {
            case 'card':
                return leaving || P.hasCard(lock.card) ? OK : { ok: false, card: lock.card };
            case 'oneway':
                // Shut from the corridor until she has come out through it (an aired balcony cabin).
                if (leaving) {
                    P.markOpened(d.id);
                    return OK;
                }
                return this.save.opened.includes(d.id) ? OK : { ok: false };
            case 'flag':
                if (P.has(lock.id)) return OK;
                // From inside, opening it is the scene (the balcony guest let back in).
                if (leaving) {
                    P.setFlag(lock.id);
                    return { ok: false, quiet: true };
                }
                return { ok: false };
        }
        return OK;
    }

    // --- The outside route (§6.1.3, region 7) ---------------------------------------------------
    // The promenade's deck, the boat walkway at deck 7's height, the balconies of decks 8-10: floors
    // she lands on from above (and drops through with ↓ and jump), partitions between balconies that
    // only a wall jump gets over, the glass fronts drawn over her.

    buildOutside() {
        const s = this.scene, D = s.DEPTH, out = this.data.outside;
        this.platZones = [];
        this.wallZones = [];
        for (const pl of out.platforms) {
            const zone = s.add.zone(pl.x0, pl.y, pl.x1 - pl.x0, pl.solid ? 16 : 6).setOrigin(0);
            s.physics.add.existing(zone, true);
            zone.plat = pl;
            this.platZones.push(zone);
        }
        for (const w of out.walls) {
            const zone = s.add.zone(w.x, (w.y0 + w.y1) / 2, w.w, w.y1 - w.y0);
            s.physics.add.existing(zone, true);
            this.wallZones.push(zone);
        }
        // Each deck's balcony fronts, over her: pale glass she shows through, the white rail on top.
        const fronts = {};
        for (const gl of out.glass) {
            const g = fronts[gl.deck] ??= s.add.graphics().setDepth(D.player + 0.3);
            // (Thin: the fronts are drawn to the ship's scale and come up to her eyes.)
            g.fillStyle(0xa3c4d4, 0.28).fillRect(gl.x0, gl.y - 48, gl.x1 - gl.x0, 40);
            g.fillStyle(0xc7e4ef, 0.5).fillRect(gl.x0, gl.y - 36, gl.x1 - gl.x0, 1);
            g.fillStyle(0xf4f4f4, 1).fillRect(gl.x0, gl.y - 50, gl.x1 - gl.x0, 3);
            g.fillStyle(0xf4f4f4, 1).fillRect(gl.x0, gl.y - 8, gl.x1 - gl.x0, 8 + PLAYER.sink);
        }
        for (const [deck, g] of Object.entries(fronts)) {
            this.add([g]);
            s.shellSlopes.push({ deck: Number(deck), gfx: g });
        }
        // The ship's side drawn again over her where her picture reaches past her body (the user, 2026-11-21: it
        // showed through a partition and through the hull past a row's end): each partition's panel (its colours as
        // the map builder draws it; its foot, under the glass's sill, the side's own painted tiles). At the fronts'
        // depth, faded with their deck as they are.
        const panels = {};
        this.balconyWalls = {};     // a balcony floor's y: [x0, x1, kind] of each partition's panel and each row's end
        for (const c of out.covers ?? []) {
            (this.balconyWalls[c.y] ??= []).push([c.x0, c.x1, c.kind]);
            const depth = D.player + 0.3, parts = [];
            if (c.kind === 'panel') {
                const g = panels[c.deck] ??= s.add.graphics().setDepth(depth);
                const h = c.y - 8 - c.y0;
                g.fillStyle(0xf4f4f4, 1).fillRect(c.x0, c.y0, c.x1 - c.x0, h);
                g.fillStyle(0xc7dcd0, 1).fillRect(c.x1 - 1, c.y0, 1, h).fillRect(c.x0, c.y0, c.x1 - c.x0, 1);
                parts.push(s.plateCopy(c.x0, c.y - 8, c.x1 - c.x0, 8 + PLAYER.sink, depth));
            }
            // (A row's end is not drawn again: windows and lamps on the side there are not its tiles, and a copy hid
            // them. Her picture is cut at it instead, at any height, the wall running floor to ceiling: `balconyRoom`.)
            parts.forEach(gfx => s.shellSlopes.push({ deck: c.deck, gfx }));
        }
        for (const [deck, g] of Object.entries(panels)) {
            this.add([g]);
            s.shellSlopes.push({ deck: Number(deck), gfx: g });
        }
        // Ladders between routes: the lifeboat station's, from the promenade's gate up its column.
        this.ladders = this.data.ladders.map(L => {
            const g = s.add.graphics().setDepth(D.exterior + 0.09);
            g.fillStyle(0xe8eaec, 1).fillRect(L.x - 7, L.y1 - 6, 2, L.y0 - L.y1 + 6).fillRect(L.x + 5, L.y1 - 6, 2, L.y0 - L.y1 + 6);
            for (let y = L.y0 - 6; y > L.y1; y -= 8) g.fillStyle(0xc7dcd0, 1).fillRect(L.x - 6, y, 12, 2);
            this.add([g]);
            s.shellSlopes.push({ deck: [6, 7], gfx: g });
            const lock = parseLock(L.lock);
            if (lock?.kind === 'card') {
                const reader = s.add.image(L.x + 14, L.y0 - 40, 'reader').setDepth(D.exterior + 0.09);
                const light = s.add.rectangle(L.x + 14, L.y0 - 42, 4, 2, this.cardColour(lock.card)).setDepth(D.exterior + 0.09);
                this.add([reader, light]);
                s.shellSlopes.push({ deck: [6, 7], gfx: reader }, { deck: [6, 7], gfx: light });
            }
            return { ...L, lockSpec: lock };
        });
        // The bridge's hatch and its like: ladders on the map shut until something has happened.
        this.gates = this.data.ladderGates.map(g => {
            const tiles = [];
            s.ladderLayer.forEachTile(t => {
                if (t.index > 0 && Math.abs(t.pixelX + 8 - g.x) < 2 && t.pixelY >= g.y0 - 2 && t.pixelY < g.y1) tiles.push(t);
            });
            if (!g.hide) {
                // In plain sight, a chain across its foot with a sign on it (the technical ladder).
                const chain = s.add.graphics().setDepth(D.props + 0.02);
                for (let x = -12; x <= 12; x += 3) {
                    chain.fillStyle(Math.abs(x) % 2 ? 0x625565 : 0x9babb2, 1).fillRect(g.x + x - 1, g.y1 - 36 + Math.round(4 - (x * x) / 36), 2, 2);
                }
                chain.fillStyle(0x625565, 1).fillRect(g.x - 14, g.y1 - 44, 2, 12).fillRect(g.x + 12, g.y1 - 44, 2, 12);
                const sign = s.add.text(g.x, g.y1 - 23, g.sign ?? '', {
                    fontFamily: 'Verdana, sans-serif', fontSize: '4px', fontStyle: 'bold', color: '#ffffff', backgroundColor: '#ae2334', align: 'center',
                    padding: { x: 1, y: 1 }, resolution: 4,
                }).setOrigin(0.5).setDepth(D.props + 0.03);
                this.add([chain, sign]);
                return { ...g, tiles, extra: [chain, sign] };
            }
            const lid = s.add.image(g.x, g.y0 + 16, 'hatch-lid').setOrigin(0.5, 0).setDepth(D.props);
            this.add([lid]);
            return { ...g, tiles, lid };
        });
    }

    cardColour(card) {
        return { deck: 0x4d9be6, ent: 0xe83b3b, hk: 0x1ebc73, off: 0xf9c22b }[card] ?? 0xffffff;
    }

    // The open width of the balcony she is on: her picture is cut to it, since what reaches past a partition would
    // show on the next balcony, and past a row's end over the ship's side (the user, 2026-11-21). A partition counts
    // while all of her is under its panel's top (her head 60 px over her feet; over it she may lean across); a row's
    // end, its wall running to the ceiling, at any height under it. Null off the balconies.
    balconyRoom(x, y) {
        for (const [fy, list] of Object.entries(this.balconyWalls ?? {})) {
            const f = Number(fy);
            if (y > f + 2 || y < f - 116) continue;
            const low = y >= f - (this.data.outside.partition - 60);
            let left = -Infinity, right = Infinity;
            for (const [a, b, kind] of list) {
                if (kind === 'panel' && !low) continue;
                if (b <= x + 1) left = Math.max(left, b);
                if (a >= x - 1) right = Math.min(right, a);
            }
            if (left > -Infinity || right < Infinity) return [Math.max(left, x - 200), Math.min(right, x + 200)];
        }
        return null;
    }

    // A balcony's floor at her feet that she can drop through: only where a floor of the route lies one deck under
    // her to land on (a balcony, the walkway), or with the parasol, any floor of it under her to float down to (the
    // user, 2026-11-21: "she shouldn't jump down" where no balcony is underneath; it had been the long fall).
    dropFloorAt(x, y, floating = false) {
        const at = this.platZones.find(z => z.plat.drop && x >= z.plat.x0 && x <= z.plat.x1 && Math.abs(y - z.plat.y) < 2)?.plat;
        if (!at) return null;
        const under = this.platZones.some(z => x >= z.plat.x0 && x <= z.plat.x1
            && (floating ? z.plat.y > y + 2 : Math.abs(z.plat.y - (y + 144)) < 2));   // (a deck: 144 px)
        return under ? at : null;
    }

    // ↑/↓ at a ladder between routes.
    tryLadder(input, onFloor) {
        const s = this.scene, p = s.player;
        if (this.carry || !onFloor) return false;
        for (const L of this.ladders.concat(this.roofLadders ?? [])) {
            if (Math.abs(p.x - L.x) > 10) continue;
            const atFoot = input.up && s.route === L.routeBottom && Math.abs(p.y - L.y0) < 4;
            const atTop = input.down && s.route === L.routeTop && Math.abs(p.y - L.y1) < 4;
            if (!atFoot && !atTop) continue;
            // Its gate: a card from below, free from above.
            if (atFoot && L.lockSpec?.kind === 'card' && !this.progress.hasCard(L.lockSpec.card)) {
                s.showLocked(L.lockSpec.card);
                return true;
            }
            this.onLadder = L;
            return s.enterLadder(L.x, L.y1, L.y0, L.out, L.ceil);
        }
        return false;
    }

    // The ladder inside a room entered through a roof hatch (the lifeboat).
    roofLadderOf(room) {
        return (this.roofLadders ?? []).find(L => L.room === room);
    }

    // A ladder on the map she can't take now: a tray in her hands, or its hatch still shut.
    ladderShut(x, y) {
        if (this.carry) return true;
        const gate = this.gates.find(g => Math.abs(x - g.x) < 9 && y >= g.y0 - 6 && y <= g.y1 + 6 && !this.progress.flagSet(g.needs));
        if (gate?.sign) {
            this.scene.showLocked(null, `🚧 ${gate.sign.replace('\n', ': ')}`);
            this.story.onBlocked(gate.needs);
        }
        return !!gate;
    }

    // A grip beside her for a wall jump: { away } the side to kick to (0: either, a pillar).
    gripAt(p) {
        const s = this.scene, half = PLAYER.bodyWidth / 2;
        for (const g of this.grips) {
            if (g.route !== s.route) continue;
            if (p.y < g.y0 + 4 || p.y - PLAYER.bodyHeight > g.y1) continue;
            const dx = p.x - g.x;
            if (Math.abs(dx) - (g.w / 2 + half) > 5) continue;
            if (g.side && Math.sign(dx) !== g.side) continue;
            // (`over`: a balcony's partition: its panel's top, which a kick vaults.)
            return { away: Math.abs(dx) < 3 ? 0 : Math.sign(dx), over: !!g.over, top: g.y1 - (g.panel ?? 0), x: g.x };
        }
        return null;
    }

    lowAt(x, y) {
        const route = this.scene.route;
        return this.low.some(z => z.route === route && x > z.x0 && x < z.x1 && Math.abs(y - z.y) < 6);
    }

    // --- The funnel's top (§6.1.10) -------------------------------------------------------------

    buildFunnel() {
        const s = this.scene, D = s.DEPTH, f = this.data.funnel;
        const x0 = f.x0 - 18, w = f.x1 - x0;
        const back = s.add.graphics().setDepth(D.exterior + 0.07);
        const front = s.add.graphics().setDepth(D.player + 0.3);
        // A steel grating along the lattice's top, white rails behind and in front.
        back.fillStyle(0x7f708a, 1).fillRect(x0, f.y, w, 5);
        back.fillStyle(0x9babb2, 1).fillRect(x0, f.y, w, 2);
        for (let x = x0 + 2; x < f.x1; x += 4) back.fillStyle(0x3e3546, 1).fillRect(x, f.y + 2, 1, 2);
        for (const g of [back, front]) {
            const top = g === back ? f.y - 34 : f.y - 30;
            g.fillStyle(0xe8eaec, 1).fillRect(f.x0 + 14, top, f.x1 - f.x0 - 14, 2).fillRect(f.x0 + 14, top + 14, f.x1 - f.x0 - 14, 1);
            for (let x = f.x0 + 14; x <= f.x1; x += 44) g.fillRect(Math.min(x, f.x1 - 2), top, 2, f.y - top + (g === front ? PLAYER.sink : 0));
        }
        this.add([back, front]);
        const walk = { x0, x1: f.x1, y: f.y, dropThrough: false };
        walk.zone = s.add.zone(x0, f.y, w, 6).setOrigin(0);
        walk.zone.walk = walk;
        s.physics.add.existing(walk.zone, true);
        s.walkGroup.add(walk.zone);
        s.walks.push(walk);
        // She stops at its aft end's rail.
        const stop = s.add.zone(f.x1 + 4, f.y - 40, 8, 80);
        s.physics.add.existing(stop, true);
        (s.railingStops ||= []).push(stop);
        // The engineer's locker, the top's checkpoint (population §2.5).
        s.addCheckpoint('cp_funnel', f.x0 + 60, f.y, { door: 'door-crew' }).items.forEach(i => i.setDepth(D.exterior + 0.08));
    }

    // --- The duct (population §6.5) -------------------------------------------------------------
    // A crawl space at deck 9's floor, from the linen room's vent forward to a grille over deck 8's
    // corridor. It shows in the deck's place, dimmed round it, like a room.

    buildDuct() {
        const s = this.scene, D = s.DEPTH, d = this.data.duct;
        const W = d.x1 - d.x0, H = 60;
        if (!s.textures.exists('room-duct')) {
            const tex = s.textures.createCanvas('room-duct', W, H);
            const ctx = tex.getContext();
            const rect = (x, y, w, h, c) => { ctx.fillStyle = c; ctx.fillRect(x, y, w, h); };
            rect(0, 0, W, H, '#1a141c');
            // Its steel: a lit band along the top, a shadow along the floor, a flange at each joint
            // with its rivets, a hanger up to the deck above at every other one.
            rect(0, 12, W, 34, '#4a4458');
            rect(0, 12, W, 2, '#7f708a');
            rect(0, 14, W, 1, '#625565');
            rect(0, 40, W, 6, '#3e3546');
            rect(0, 44, W, 2, '#625565');
            for (let x = 0, n = 0; x < W; x += 64, n++) {
                rect(x, 12, 3, 34, '#3e3546');
                rect(x + 3, 12, 1, 34, '#625565');
                for (const y of [17, 27, 37]) rect(x + 1, y, 1, 1, '#9babb2');
                if (n % 2) rect(x + 1, 0, 1, 12, '#3e3546');
            }
            // Dust along the floor, cobwebs in a few corners, and his paw prints going forward.
            for (let x = 5; x < W; x += 11) rect(x + (x * 7) % 5, 43, 2, 1, '#7f708a');
            ctx.strokeStyle = '#9babb2';
            ctx.lineWidth = 1;
            for (const x of [196.5, 452.5, 772.5, 1028.5]) {
                ctx.beginPath();
                ctx.moveTo(x, 14.5); ctx.lineTo(x + 9, 14.5);
                ctx.moveTo(x, 14.5); ctx.lineTo(x, 23.5);
                ctx.moveTo(x, 20.5); ctx.quadraticCurveTo(x + 4, 19.5, x + 6, 14.5);
                ctx.moveTo(x, 17.5); ctx.quadraticCurveTo(x + 2, 17, x + 3, 14.5);
                ctx.stroke();
            }
            for (let x = W - 40, n = 0; x > 90; x -= 21, n++) {
                const y = n % 2 ? 42 : 40;
                rect(x, y, 3, 2, '#2e222f');
                rect(x - 1, y - 1, 1, 1, '#2e222f');
                rect(x + 1, y - 2, 1, 1, '#2e222f');
                rect(x + 3, y - 1, 1, 1, '#2e222f');
            }
            // A branch going up, with a fan in it (too small for her; a draught).
            rect(672, 0, 30, 13, '#4a4458');
            rect(672, 0, 1, 13, '#3e3546');
            rect(701, 0, 1, 13, '#3e3546');
            rect(676, 3, 22, 2, '#2e222f');
            rect(676, 7, 22, 2, '#2e222f');
            // Grilles in its floor, the light of what is below coming up through them.
            const light = { lobby: '#fff1c9', dome: '#8fd3ff', balloons: '#f68181', snore: '#b9a98a', exit: '#fff1c9' };
            for (const g of [...d.grilles, { x: d.exitX, what: 'exit' }]) {
                const x = g.x - d.x0;
                rect(x - 15, 43, 30, 4, '#2e222f');
                rect(x - 14, 44, 28, 3, light[g.what]);
                ctx.globalAlpha = 0.22;
                ctx.fillStyle = light[g.what];
                ctx.beginPath();
                ctx.moveTo(x - 13, 44); ctx.lineTo(x + 13, 44); ctx.lineTo(x + 9, 14); ctx.lineTo(x - 9, 14);
                ctx.fill();
                ctx.globalAlpha = 1;
                for (let k = -12; k < 14; k += 5) rect(x + k, 44, 1, 3, '#2e222f');
            }
            tex.refresh();
        }
        const img = s.add.image(d.x0, d.floor - 46, 'room-duct').setOrigin(0).setDepth(D.exterior + 0.12).setVisible(false);
        const dim = s.roomDim(img);
        this.add([dim, img]);
        const room = { route: 'duct', door: -9999, floor: d.floor, room: img, dim, inDeck: true, doors: [] };
        s.rooms.push(room);
        this.ductFloor = s.add.zone(d.x0, d.floor, W, 16).setOrigin(0);
        s.physics.add.existing(this.ductFloor, true);
        s.addRouteWall(d.x0 + 24, -1, d.floor, 'duct');
        s.addRouteWall(d.x1 - 24, 1, d.floor, 'duct');
        // What is under each grille (tools/draw_rooms.py `peeks`): a framed look down, shown while
        // she is over it; and what comes up through it.
        this.peeks = d.grilles.filter(g => s.textures.exists(`peek-${g.what}`)).map(g => {
            const frame = s.add.rectangle(g.x, d.floor + 20, 68, 48, 0x2e222f).setOrigin(0.5, 0).setDepth(D.exterior + 0.124);
            const pic = s.add.image(g.x, d.floor + 22, `peek-${g.what}`).setOrigin(0.5, 0).setDepth(D.exterior + 0.125);
            const beam = s.add.triangle(0, 0, g.x - 13, d.floor + 1, g.x + 13, d.floor + 1, g.x, d.floor + 20, 0xfff1c9, 0.35)
                .setOrigin(0).setDepth(D.exterior + 0.123);
            const items = [frame, pic, beam];
            items.forEach(i => i.setAlpha(0));
            this.add(items);
            return { ...g, items, shown: 0 };
        });
        // The fan in the branch: two blades turning.
        this.ductFan = s.add.rectangle(d.x0 + 687, d.floor - 40, 20, 2, 0x9babb2).setDepth(D.exterior + 0.125).setVisible(false);
        // His eyes in the dark ahead of her (the first time through): two green points that keep
        // their distance, and are gone at the far grille.
        this.ductEyes = s.add.graphics().setDepth(D.exterior + 0.126).setVisible(false);
        this.ductEyes.fillStyle(0xb9e04c, 1).fillRect(-4, -1, 2, 2).fillRect(2, -1, 2, 2);
        this.ductEyes.fillStyle(0xffffff, 1).fillRect(-4, -1, 1, 1).fillRect(2, -1, 1, 1);
        this.add([this.ductFan, this.ductEyes]);
    }

    // The linen room's laundry cart, once it stands under the vent; and whether she is on it.
    onLinenCart() {
        const s = this.scene, p = s.player, cart = this.pushables.find(t => t.id === 'cart_linen');
        if (!cart || s.route !== 'linen' || cart.x < cart.max) return null;
        const onFloor = p.body.blocked.down || p.body.touching.down;
        return onFloor && Math.abs(p.x - cart.x) < 18 && Math.abs(p.y - (cart.y - cart.rim)) < 4 ? cart : null;
    }

    updateDuct(input, time) {
        const s = this.scene, p = s.player, d = this.data.duct, P = this.progress;
        const inDuct = s.route === 'duct';
        // (The duct runs where the atrium's walk is: its glass railing, drawn in front of her, hides.)
        if (inDuct !== this.wasInDuct) {
            this.wasInDuct = inDuct;
            for (const f of s.deckFronts ?? []) f.gfx.setVisible(!inDuct);
        }
        // The fan, the peeks, his eyes.
        this.ductFan.setVisible(inDuct);
        if (inDuct) this.ductFan.setAngle((time / 3) % 360);
        for (const k of this.peeks) {
            const want = inDuct && Math.abs(p.x - k.x) < 34 ? 1 : 0;
            if (want !== k.shown) {
                k.shown = want;
                s.tweens.add({ targets: k.items, alpha: want, duration: 260 });
                if (want && k.what === 'balloons') sfx.at(k.x, d.floor).toot();
            }
            // (The sleeper under the grille snores on for as long as she looks down at him.)
            if (k.shown && k.what === 'snore' && time > (k.snoreAt ?? 0)) {
                k.snoreAt = time + 2600;
                sfx.at(k.x, d.floor).snore();
            }
        }
        const eyes = this.ductEyes;
        if (inDuct && !P.has('duct') && !this.eyesGone) {
            this.eyesX = Math.min(this.eyesX ?? p.x - 170, p.x - 150);
            if (this.eyesX <= d.exitX + 6) {
                this.eyesGone = true;
                eyes.setVisible(false);
                sfx.at(this.eyesX, d.floor).mrrp();
            } else {
                eyes.setVisible(Math.floor(time / 2600) % 5 !== 4 || (time % 2600) > 160).setPosition(this.eyesX, d.floor - 9);
            }
        } else {
            eyes.setVisible(false);
        }
        if (s.mode !== 'play') return;
        // In: on the laundry cart under the vent, down on hands and knees. Out: back the same way,
        // or down through the far grille. (A key held through a way in or out would carry her
        // straight back: it must be let go once.)
        if (!input.right) this.ductLatch = false;
        if (!input.down) this.ventLatch = false;
        const cart = this.onLinenCart();
        if (cart && s.crawling && !this.ventLatch) {
            this.ductLatch = this.ventLatch = true;
            s.travel(d.x1 - 60, d.floor, 'duct', () => p.setFlipX(true));
        } else if (inDuct && input.right && !this.ductLatch && p.x >= d.x1 - 44) {
            this.ductLatch = this.ventLatch = true;
            const back = this.pushables.find(t => t.id === 'cart_linen'), linen = this.rooms.linen;
            s.travel(back.x, linen.floor - back.rim - 1, 'linen', () => p.setFlipX(true));
        } else if (inDuct && input.downPressed && Math.abs(p.x - d.exitX) < 30) {
            sfx.clang();
            s.travel(d.dropX, d.floor + 30, 'inside', () => P.setFlag('duct'));
        }
    }

    // --- Things in place ------------------------------------------------------------------------

    buildEnt(e) {
        const s = this.scene, D = s.DEPTH;
        const depth = this.depthFor(e.route);
        switch (e.kind) {
            case 'checkpoint': {
                // (`bare`: on a balcony, at an ajar balcony door: only the lamp, over the door.)
                const cp = e.bare ? s.addCheckpoint(e.id, e.x, e.y, { route: e.route, door: null, rise: 112 })
                    : s.addCheckpoint(e.id, e.x, e.y, { route: e.route });
                const deck = e.bare ? s.deckOfY(e.y) : [6, 7];
                if (e.route === OUTSIDE) cp.items.forEach(i => s.shellSlopes.push({ deck, gfx: i }));
                break;
            }
            case 'tangerine':
                if (e.needs && !this.met(e.needs)) this.pending.push(e);
                else this.placeTangerine(e);
                break;
            case 'item': {
                if (this.itemTaken(e)) break;
                const [type, name] = e.what.split(':');
                const key = type === 'book' ? `book-${name}` : `icon-${name}`;
                const items = [];
                let y = e.y;
                if (e.on != null) {
                    y -= e.on;              // on a piece already there
                } else if (e.route === 'inside') {
                    const table = s.add.image(e.x, e.y, 'sidetable').setOrigin(0.5, 1).setDepth(D.decor + 0.2);
                    items.push(table);
                    y -= table.height;
                }
                const img = (e.frame ? this.image(e.x, y, e.frame) : s.add.image(e.x, y, key)).setOrigin(0.5, 1).setDepth(depth + 0.01);
                this.glint(img);
                // The near part of the furniture it is in, drawn again in front of it (`cover`: the seat's
                // near arm over the diary's foot). It stays when the thing is taken: the same pixels.
                if (e.cover) {
                    const c = s.add.image(e.cover.x, e.y, 'shipart', e.cover.frame).setOrigin(0.5, 1).setDepth(depth + 0.02);
                    c.setCrop(0, c.height - e.cover.rows, c.width, e.cover.rows);
                    this.add([c]);
                }
                items.push(img);
                this.add(items);
                // (`level`: where it lies, for her standing up there with it: a book on a bed. A thing
                // to find up high, on the climb's shelf, is hers only from up there, or once a lob
                // has knocked it down: `high`.)
                const thing = { ...e, level: y, items, pick: img, high: type === 'keep' && e.on > 40 && e.from == null, interact: () => this.take(thing) };
                this.things.push(thing);
                break;
            }
            case 'cat': {
                const cat = s.addCat(e.id, e.x, e.y, e.activity, e.escape, { route: e.route, lift: e.lift ?? 0, exitX: e.exitX });
                cat.flag = e.id;
                cat.needs = e.needs;
                if (this.progress.has(e.id)) {
                    cat.gone = cat.away = true;
                    cat.sprite.setVisible(false);
                }
                break;
            }
            case 'switch': {
                const img = s.add.image(e.x, e.y, 'switch-box').setOrigin(0.5, 1).setDepth(depth);
                const label = s.add.text(e.x, e.y - 26, e.label, {
                    fontFamily: 'Verdana, sans-serif', fontSize: '5px', fontStyle: 'bold', color: '#2e222f', backgroundColor: '#f9c22b',
                    padding: { x: 1, y: 1 }, resolution: 4,
                }).setOrigin(0.5).setDepth(depth);
                this.add([img, label]);
                const thing = { ...e, items: [img, label], interact: () => {
                    if (this.progress.has(e.flag)) return false;
                    this.progress.setFlag(e.flag);
                    s.sparkle?.(e.x, e.y - 20);
                    sfx.lever();
                    return true;
                } };
                this.things.push(thing);
                break;
            }
            case 'person':
                this.people.add(e);
                break;
            case 'prop': {
                // A piece of the ship's atlas that the plan adds, in full colour: on the floor, `dy` up
                // on something, in front of her or behind.
                const d = e.front ? D.player + 0.04 : e.back ? D.decor + 0.11 : depth - 0.02;
                const img = this.image(e.x, e.y - (e.dy ?? 0), e.frame).setOrigin(0.5, 1).setDepth(d).setFlipX(!!e.flip).setAngle(e.angle ?? 0);
                if (e.front && !e.dy) s.withFoot(img);
                this.add([img]);
                this.things.push({ ...e, items: [img], img });
                break;
            }
            case 'solid': {
                // Something standing in the way that she hops (a room-service cart).
                const img = this.image(e.x, e.y, e.frame).setOrigin(0.5, 1).setDepth(depth - 0.01).setFlipX(!!e.flip);
                const zone = s.add.zone(e.x, e.y, img.width - 6, img.height - 3).setOrigin(0.5, 1);
                s.physics.add.existing(zone, true);
                this.add([img]);
                const thing = { ...e, items: [img], zone };
                this.solids.push(thing);
                this.things.push(thing);
                break;
            }
            case 'shelf': {
                // A shelf on the wall under the ceiling, on two brackets: the climb's top
                // (docs/plan-three-uses.md §4.2). She stands on it.
                const img = this.image(e.x, e.y - e.up, 'thing:wall-shelf').setOrigin(0.5, 0).setDepth(D.decor + 0.2);
                const zone = s.add.zone(e.x, e.y - e.up + 4, img.width, 4).setOrigin(0.5, 1);
                s.physics.add.existing(zone, true);
                this.add([img]);
                const thing = { ...e, items: [img], zone };
                this.solids.push(thing);
                this.things.push(thing);
                break;
            }
            case 'deskflags': {
                // Little desk flags of the cruise's ports on Shore excursions' desk, hers among them.
                const items = e.flags.map((f, i) => this.image(e.x - 18 + i * 9, e.y - e.on, `thing:flag-${f}`).setOrigin(0.5, 1).setDepth(depth + 0.01));
                this.add(items);
                this.things.push({ ...e, items });
                break;
            }
            case 'knitter': {
                // The lady knitting on her own armchair in the corridor, by her cabin's door, her basket
                // beside her with the wool in it (docs/plan-three-uses.md §4.2; the wool: ITEMS
                // `keep_wool`; the user, 2026-11-16: she had sat in her open doorway).
                const chair = this.image(e.x, e.y, 'thing:knit-chair').setOrigin(0, 1).setDepth(D.decor + 0.11);
                const basket = this.image(e.basket, e.y, 'thing:knit-basket').setOrigin(0.5, 1).setDepth(D.decor + 0.2);
                this.add([chair, basket]);
                this.people.add({ id: `${e.id}_who`, who: e.who, x: e.x + KNIT_SIT.dx, y: e.y - KNIT_SIT.up, route: 'inside', face: 1,
                                  idle: 'knit', layer: 'back' });
                this.things.push({ ...e, items: [chair, basket] });
                break;
            }
            case 'breakfast':
                this.movers.push(new Breakfast(this, e));
                break;
            case 'roller':
                this.movers.push(new Roller(this, e));
                break;
            case 'dog':
                this.movers.push(new Fetcher(this, e));
                break;
            case 'skimmer':
                this.movers.push(new Skimmer(this, e));
                break;
            case 'breakable': {
                // Stacked luggage, crates: the dash goes through them; otherwise they are in the way
                // (low ones can be hopped).
                if (this.save.broken.includes(e.id)) break;
                const items = [];
                let w = 0, h = 0;
                for (const [frame, dx, dy] of e.pieces) {
                    // ("@name": drawn by the game, not a piece of the atlas.) In front of what it hides.
                    const img = (frame.startsWith('@') ? s.add.image(e.x + dx, e.y - dy, frame.slice(1)) : s.add.image(e.x + dx, e.y - dy, 'shipart', frame))
                        .setOrigin(0.5, 1).setDepth(depth + 0.03);
                    items.push(img);
                    w = Math.max(w, Math.abs(dx) * 2 + img.width);
                    h = Math.max(h, dy + img.height);
                }
                // (`hang`: it hangs on a string, this many px up to its foot: only it is in the way,
                // at head height; on hands and knees she passes under it.)
                const zone = e.hang ? s.add.zone(e.x, e.y - e.hang, w - 4, h - e.hang - 2).setOrigin(0.5, 1)
                    : s.add.zone(e.x, e.y, w - 6, h - 3).setOrigin(0.5, 1);
                s.physics.add.existing(zone, true);
                if (e.string) items.push(s.add.rectangle(e.x, e.y - ROOM.height, 1, ROOM.height - h + 2, 0xab947a).setOrigin(0.5, 0).setDepth(depth + 0.029));
                this.add(items);
                const thing = { ...e, items, zone };
                if (e.hang) {
                    thing.lowZone = { route: e.route, x0: e.x - w / 2 - 16, x1: e.x + w / 2 + 16, y: e.y };
                    this.low.push(thing.lowZone);
                }
                this.breakables.push(thing);
                this.things.push(thing);
                break;
            }
            case 'source': {
                // A tray to take (population §1 `source`): it always has more.
                const items = [];
                if (e.show) {
                    this.carryBox.textures();
                    // (One of the game's own pictures, or a piece of the ship's atlas.)
                    for (const [key, dy] of e.show) {
                        const img = s.textures.exists(key) ? s.add.image(e.x, e.y - dy, key) : this.image(e.x, e.y - dy, key);
                        items.push(img.setOrigin(0.5, 1).setDepth(depth + 0.03));
                    }
                    this.add(items);
                }
                this.things.push({ ...e, items, reach: 22, interact: () => {
                    // (`when`: there to see, but hers to take only then.)
                    if (this.carry || (e.when && !this.cond(e.when))) return false;
                    this.carryBox.take(e.gives);
                    return true;
                } });
                break;
            }
            case 'platform': {
                // A roof she can stand on, landing from above (the hot tub's canopy); a bed in a room, there
                // only while she is in it (the maid's cabin's: `route`).
                const walk = { x0: e.x0, x1: e.x1, y: e.y, dropThrough: false, route: e.route === 'inside' ? null : e.route };
                walk.zone = s.add.zone(e.x0, e.y, e.x1 - e.x0, 6).setOrigin(0);
                walk.zone.walk = walk;
                s.physics.add.existing(walk.zone, true);
                s.walkGroup.add(walk.zone);
                s.walks.push(walk);
                // What of the room is in front of her while she stands on it (`front`: the swan on the
                // maid's bed); on the floor she is in front of it, as of the rest of the room.
                if (e.front) {
                    walk.front = s.add.image(e.roomX, e.roomY - ROOM.height, `room-${e.front}`).setOrigin(0).setDepth(D.player + 0.01).setVisible(false);
                    this.add([walk.front]);
                    (this.bedFronts ??= []).push(walk);
                }
                break;
            }
            case 'wet':
                this.movers.push(new WetPatch(this, e));
                break;
            case 'foodgull': {
                const gulls = new FoodGulls(this, e);
                this.movers.push(gulls);
                (this.foodGulls ??= {})[e.id] = gulls;
                break;
            }
            case 'queue':
                this.movers.push(new Queue(this, e));
                break;
            case 'trays':
                this.movers.push(new Trays(this, e));
                break;
            case 'rounds':
                this.movers.push(new Rounds(this, e));
                break;
            case 'robot': {
                const robot = new Robot(this, e);
                this.movers.push(robot);
                this.robots = [...(this.robots ?? []), robot];
                break;
            }
            case 'gull':
                this.movers.push(new Gull(this, e));
                break;
            case 'bellgull':
                this.movers.push(new BellGull(this, e));
                break;
            case 'light':
                this.movers.push(new SwingLight(this, e));
                break;
            case 'spill':
                this.movers.push(new Spill(this, e));
                break;
            case 'darter':
                this.movers.push(new Darter(this, e));
                break;
            case 'stack':
                this.movers.push(new TowelStack(this, e));
                break;
            case 'sprinkler':
                this.movers.push(new Sprinkler(this, e));
                break;
            case 'swingdoor':
                this.movers.push(new SwingDoor(this, e));
                break;
            case 'dnd':
                this.movers.push(new DndDoor(this, e));
                break;
            case 'opendoor': {
                // A cabin door standing open, in a cabin door's place (region 5): a party's, with its
                // balloons out in the corridor; a made-up cabin's, the sea in its window.
                const items = [];
                if (e.what === 'sea') {
                    items.push(s.add.image(e.x, e.y, 'peek-sea').setOrigin(0.5, 1).setDepth(D.decor + 0.1));
                } else if (e.what === 'knit') {
                    // The knitting lady's cabin, its door open behind her chair (case 'knitter').
                    items.push(s.add.image(e.x, e.y, 'peek-knit').setOrigin(0.5, 1).setDepth(D.decor + 0.1));
                } else {
                    items.push(s.add.image(e.x, e.y, 'shipart', 'door-cabin-ajar').setOrigin(0.5, 1).setDepth(D.decor + 0.1));
                    const tied = s.add.image(e.x + 9, e.y - 34, 'balloons').setOrigin(0.5, 1).setDepth(D.decor + 0.15);
                    s.tweens.add({ targets: tied, y: tied.y - 2, angle: { from: -2, to: 2 }, duration: 1300, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
                    items.push(tied);
                    // Loose ones: two on the floor, one up against the ceiling.
                    for (const [dx, dy, tint] of [[-27, 0, 0xf68181], [-41, 0, 0x4d9be6], [-22, 108, 0xf9c22b], [52, 108, 0xb9e04c]]) {
                        items.push(s.add.image(e.x + dx, e.y - dy, 'balloon').setOrigin(0.5, 1).setTint(tint).setDepth(D.decor + 0.14));
                    }
                }
                this.add(items);
                this.things.push({ ...e, items });
                break;
            }
            case 'low': {
                // Something she must crawl under or through (a blanket fort): solid above her on
                // hands and knees; its picture, if it has one, in front of her.
                const zone = s.add.zone(e.x, e.y - 30, e.x1 - e.x0, 98).setOrigin(0.5, 1);
                s.physics.add.existing(zone, true);
                this.low.push({ route: e.route, x0: e.x0 - 18, x1: e.x1 + 18, y: e.y });
                const items = e.frame ? [s.withFoot(this.image(e.x, e.y, e.frame).setOrigin(0.5, 1).setDepth(D.player + 0.04))] : [];
                this.add(items);
                const thing = { ...e, items, zone };
                this.lows.push(thing);
                this.things.push(thing);
                break;
            }
            case 'jackpot': {
                // The slot machine with a glint (population: `sec_jackpot`): E, once: its lights, a
                // ding, and what it pays out (tangerines that need its flag).
                const glint = s.add.image(e.x + 9, e.y - (e.dy ?? 40), 'dot').setTint(0xfbff86).setDepth(depth + 0.02);
                this.add([glint]);
                s.tweens.add({ targets: glint, alpha: { from: 0.1, to: 1 }, scale: { from: 0.6, to: 1.6 }, duration: 500, yoyo: true, repeat: -1, repeatDelay: 900 });
                const thing = { ...e, items: [glint], reach: 16, until: `flag:${e.flag}`, interact: () => {
                    this.cut(async () => {
                        sfx.slot();
                        for (let i = 0; i < 5; i++) {
                            this.sparkle(e.x + Phaser.Math.Between(-14, 14), e.y - 30 - i * 9, [0xfbff86, 0xe83b3b, 0xffffff][i % 3]);
                            await this.wait(140);
                        }
                        sfx.chips();
                        sfx.secret();
                        this.progress.setFlag(e.flag);
                    });
                    return true;
                } };
                this.things.push(thing);
                break;
            }
            case 'slot': {
                // A photo slot (§6.1.11): a framed picture in a secret place; E opens it full screen.
                this.library.textures();
                // (its own picture small in a frame, where it has one: `thumb-<id>`; the gold frame with a heart otherwise)
                const img = s.add.image(e.x, e.y - (e.dy ?? 56), s.textures.exists(`thumb-${e.id}`) ? `thumb-${e.id}` : 'photo-frame')
                    .setDepth(depth + 0.01);
                this.add([img]);
                this.things.push({ ...e, items: [img], reach: 16, interact: () => {
                    this.cut(async () => {
                        if (!this.save.seen.includes(e.id)) sfx.secret();
                        await this.library.panel(`photo-${e.id}`);
                        if (!this.save.seen.includes(e.id)) {
                            this.save.seen.push(e.id);
                            writeSave(this.save);
                        }
                    });
                    return true;
                } });
                break;
            }
            case 'quirk': {
                // A moment of hers with no reward (§6.1.11): E on the thing, or standing still by it.
                const thing = { reach: 20, ...e, items: [], quirk: true };
                if (e.trigger === 'E') thing.interact = () => this.quirk(thing);
                this.things.push(thing);
                break;
            }
            case 'sign': {
                // A plate by a door (brass, its name), a notice, a plaque, words painted on the wall: the
                // looks of src/signs.js; the brass name plates are still text.
                const text = SIGN_LOOKS[e.style] ? sign(s, e.x, e.y - (e.dy ?? 52), e.text, e.style) : s.add.text(e.x, e.y - (e.dy ?? 52), e.text, {
                    fontFamily: 'Verdana, sans-serif', fontSize: `${e.size ?? 5}px`, fontStyle: 'bold', align: 'center',
                    color: '#45293f', backgroundColor: '#d9a43b',
                    padding: { left: 2, right: 2, top: 1, bottom: 1 }, resolution: 4, wordWrap: e.wrap ? { width: e.wrap } : undefined,
                });
                text.setOrigin(0.5).setDepth(e.route === OUTSIDE ? D.exterior + 0.09 : D.decor + 0.25);
                this.add([text]);
                this.things.push({ ...e, items: [text] });
                break;
            }
            case 'push': {
                const img = this.image(e.x, e.y, e.frame).setOrigin(0.5, 1).setDepth(depth + 0.02);
                this.add([img]);
                const done = () => !e.flag || this.progress.has(e.flag);
                const x = done() ? e.max : e.x;
                // (`tall`: jammed in a doorway, it fills it until it is free; "top": it stands by the
                // wall, she walks past it, and only its rim holds her when she jumps onto it.)
                const top = e.tall === 'top';
                const rim = top ? (this.data.linen?.cartTop ?? 36) : img.height - 4;
                const zone = s.add.zone(x, e.y, img.width - 4, e.tall === true && !done() ? 128 : rim).setOrigin(0.5, 1);
                s.physics.add.existing(zone, true);
                img.x = x;
                // (A tall one, free: too tall to hop, it stands back against the wall, out of her
                // way: the steward's trolley, the user, 2026-11-17.)
                const aside = () => { zone.body.enable = false; img.setDepth(D.decor + 0.11); };
                if (e.tall === true && done()) aside();
                const thing = { ...e, x, items: [img], zone, width: img.width - 4, min: e.min, max: e.max, sides: e.sides ?? 0, top, rim,
                    moveTo: to => {
                        thing.x = img.x = zone.x = to;
                        if (to >= e.max && e.flag && !this.progress.has(e.flag)) {
                            // Free of the doorway: it stands in the corridor, low enough to hop; a
                            // tall one stands back against the wall.
                            zone.setSize(img.width - 4, rim);
                            if (e.tall === true) aside();
                            this.progress.setFlag(e.flag);
                            s.pushing = null;
                            s.mode = 'play';
                        }
                        zone.body.updateFromGameObject();
                    } };
                this.pushables.push(thing);
                this.things.push(thing);
                break;
            }
        }
    }

    itemTaken(e) {
        const [type, name] = e.what.split(':');
        if (type === 'keep') return this.save.keeps.includes(e.what);
        if (type === 'verb') return this.save.verbs.includes(name);
        if (type === 'book') return !!this.save.books[name];
        return this.save.items.includes(name) || this.save.seen.includes(e.id);
    }

    placeTangerine(e) {
        const s = this.scene, D = s.DEPTH;
        if (this.save.collected.includes(e.id)) return;
        if (e.until && this.cond(e.until)) return;
        let y = e.y;
        if (e.on === 'table') {
            if (e.first) {
                const out = e.route === OUTSIDE;
                const table = out ? s.add.image(e.x + 4, e.y, 'shipart', 'outdoor-table').setOrigin(0.5, 1).setDepth(D.exterior + 0.1)
                    : s.add.image(e.x + (e.id.includes('#') ? 4 : 0), e.y, 'sidetable').setOrigin(0.5, 1).setDepth(D.decor + 0.2);
                this.add([table]);
                if (out) this.things.push({ id: `${e.id}-table`, x: e.x, y: e.y, route: OUTSIDE, items: [table] });
            }
            // (On its top: a side table's is its picture's top row.)
            y -= e.route === OUTSIDE ? 24 : s.textures.get('sidetable').getSourceImage().height;
        } else {
            y -= e.on;
        }
        const t = s.addTangerine(e.id, e.x, y, e.route);
        if (t && e.until) t.until = e.until;
    }

    // Tangerines whose time is over leave, picked up or not (`until`: cabin 8206's on the day after). Not counted.
    dropTangerines() {
        const s = this.scene;
        s.tangerines = (s.tangerines || []).filter(t => {
            if (!t.until || !this.cond(t.until)) return true;
            t.glint.destroy();
            t.sprite.destroy();
            return false;
        });
    }

    // E at a pickup: a verb, a book, a pocket item. (Nothing says how a verb is used: no hint
    // pops up anywhere in the game, finding out is part of it: the user, 2026-11-14.)
    take(thing) {
        const s = this.scene;
        const [type, name] = thing.what.split(':');
        if (type === 'verb') {
            this.progress.learn(name);
            this.closeup(name);
        } else if (type === 'book') {
            this.library.got(name);
            this.sparkle(thing.x, thing.pick.y - 6, 0xf68181);
            this.cover(name);
        } else if (type === 'keep') {
            // (Its kind's count shows, or goes up, as its close-up closes: src/hud.js.)
            const kind = thing.what.split(':')[1];
            s.hud?.expect(kind);
            this.save.keeps.push(thing.what);
            this.sparkle(thing.x, thing.pick.y - 4, 0xf9c22b);
            this.closeup(thing.what.split(':')[2], () => s.hud?.release(kind));
        } else {
            this.save.items.push(name);
            this.closeup(name);
        }
        thing.done = true;
        thing.pick.destroy();
        thing.items = thing.items.filter(i => i !== thing.pick);
        if (type !== 'verb') sfx.take();
        writeSave(this.save);
        this.refresh();
        return true;
    }

    // A thing to find handed to her (the dog's owner's tennis ball): `what` is "keep:<whose>:<name>".
    giveKeep(what, x, y) {
        if (this.save.keeps.includes(what)) return;
        const kind = what.split(':')[1];
        this.scene.hud?.expect(kind);
        this.save.keeps.push(what);
        sfx.take();
        this.sparkle(x, y, 0xf9c22b);
        writeSave(this.save);
        this.refresh();
        this.closeup(what.split(':')[2], () => this.scene.hud?.release(kind));
    }

    // A thing she has just got, seen close (the user, 2026-11-19: "A and C"): its picture
    // (tools/build_closeups.py, the world's pixel size) in the middle of the screen over a dim, a warm
    // light behind it; she holds still and nothing touches her (`scene.viewing`) until any key. Every
    // thing to find and every key card; the books' covers the same way (`cover()`). The
    // playtests skip it (`window.__skipCloseups`) but where it is what they check. `then(dim)`: called
    // as it starts to close (or at once, with none shown), with what lies lowest in it: the HUD's card
    // flies out from behind it.
    // (`texture`, `dim`, `shadow`, `glow`: a picture of its own, the dim's alpha, a faint shadow, the light's scale.)
    closeup(frame, then = null, { texture = 'closeups', dim: dimAlpha = 0.62, shadow = false, glow: glowScale = 1 } = {}) {
        const s = this.scene;
        const pictured = texture === 'closeups' ? s.textures.get('closeups').has(frame) : s.textures.exists(texture);
        if (window.__skipCloseups || !pictured) {
            then?.();
            return;
        }
        if (!s.textures.exists('closeup-glow')) {
            const size = 360, c = s.textures.createCanvas('closeup-glow', size, size), ctx = c.getContext();
            const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
            g.addColorStop(0, 'rgba(255, 240, 214, 0.62)');
            g.addColorStop(0.45, 'rgba(255, 240, 214, 0.32)');
            g.addColorStop(1, 'rgba(255, 240, 214, 0)');
            ctx.fillStyle = g;
            ctx.fillRect(0, 0, size, size);
            c.refresh();
        }
        this.cut(() => new Promise(resolve => {
            s.viewing = true;
            const cx = VIEW.width / 2, cy = VIEW.height / 2;
            const dim = s.add.rectangle(0, 0, VIEW.width, VIEW.height, 0x0d1422, dimAlpha).setOrigin(0);
            const glow = s.add.image(cx, cy, 'closeup-glow').setScale(glowScale);
            const pic = s.add.image(cx, cy, texture, frame).setScale(2);
            const all = [dim, glow];
            // (a book's faint shadow, 4 px down and right)
            if (shadow) all.push(s.add.rectangle(cx + 4, cy + 4, pic.width * 2, pic.height * 2, 0x000000, 0.35));
            all.push(pic);
            s.uiLayer.add(all);
            s.tweens.add({ targets: all, alpha: { from: 0, to: 1 }, duration: 200 });
            const close = () => {
                then?.(dim);
                s.tweens.add({ targets: all, alpha: 0, duration: 160, onComplete: () => {
                    all.forEach(o => o.destroy());
                    s.viewing = false;
                    resolve();
                } });
            };
            // Any key, after a moment (so the E that took it does not close it at once).
            s.time.delayedCall(450, () => {
                const poll = () => {
                    const i = s.controls.state;
                    if (i.activatePressed || i.jumpPressed || i.leftPressed || i.rightPressed || i.escapePressed || i.startPressed
                        || i.dashPressed || i.throwPressed || i.upPressed || i.downPressed) {
                        s.events.off('postupdate', poll);
                        close();
                    }
                };
                s.events.on('postupdate', poll);
            });
        }));
    }

    // A book given to her (the honeymooners' thanks): hers to carry to the Library.
    giveBook(n) {
        this.library.got(n);
        writeSave(this.save);
        this.refresh();
        this.cover(n);
    }

    // A book she has just got, its cover seen close (plan-the-rest §2.3; the user, 2026-11-18: "the screen is dimmed
    // slightly, a generated book cover is shown in the center of the screen with the title and author"): her own
    // copy's cover (tools/build_covers.py) at 2x over a lighter dim than a found thing's, with the same warm light
    // behind it (the user's B of two, 2026-11-22), until any key. A book is got once, so each cover shows once.
    cover(n) {
        this.closeup(undefined, null, { texture: `cover-${n}`, dim: 0.35, shadow: true, glow: 1.4 });
    }

    // The scripted places that are not rooms: the pool's hatch, the stage's trap door, the linen
    // room's chute.
    buildSpecials() {
        const s = this.scene, D = s.DEPTH;
        const h = this.data.hatchPool;
        const lid = s.add.image(h.x, h.y + 32, 'hatch-lid').setOrigin(0.5, 1).setDepth(D.poolTank + 0.005);
        this.add([lid]);
        this.things.push({ id: 'hatch_pool', x: h.x, y: h.y + 32, route: 'inside', needs: 'drain', items: [lid], reach: 16,
            interact: () => { sfx.hatch(); s.travel(h.x, h.y + 32 + 16 + PLAYER.bodyHeight + 2, 'inside', null, 10); return true; } });
        const linen = this.rooms.linen;
        if (linen) {
            // (Her own cabin's door is a checkpoint: population §2.5, `cp_8206`.)
            const own = s.rooms.find(r => r.route === 'cabin');
            if (own) s.addCheckpoint('cp_8206', own.door, own.floor, { door: null });
            // The laundry chute's hatch, low in the wall by the door (drawn in the room's picture):
            // E, and down she goes to the laundry on deck 4 (population: `scn_chute`).
            this.things.push({ id: 'chute', x: this.data.linen.chuteX, y: linen.floor, route: 'linen', items: [], reach: 16,
                interact: () => this.story.chute() });
        }
    }

    updateSpecials(time) {
        const s = this.scene, p = s.player, P = this.progress;
        this.updateGlints(time);
        for (const w of this.bedFronts ?? []) {
            w.front.setVisible(s.route === w.route && Math.abs(p.y - w.y) < 2 && p.x >= w.x0 - 8 && p.x <= w.x1 + 8);
        }
        if (s.mode !== 'play') return;
        const onFloor = p.body.blocked.down || p.body.touching.down;
        // The stage's trap door (population: `haz_trapdoor`): after the rehearsal's beat, standing on
        // it drops her one deck into the galley; no scare.
        const t = this.data.trapdoor;
        if (s.route === 'inside' && onFloor && P.has('bb3') && Math.abs(p.x - t.x) < 10 && Math.abs(p.y - t.y) < 2) {
            const to = this.rooms[t.room];
            sfx.trapdoor();
            s.travel(t.landX, to.floor - 80, t.room, () => P.setFlag('trapdoor'));
            return;
        }
        // (The tip of the bow, §6.1.9: src/world/finale.js.)
    }

    // --- What the story and the people use ------------------------------------------------------

    // A condition from the data: "flag:bb1", "region:2", "card:deck", "carry:lunch", "verb:dash",
    // "block:cleaner" (lifted), "broken:<id>"; "!" in front turns it round. What has really happened:
    // ?cards=all fakes none of it.
    cond(text) {
        if (!text) return true;
        // ("a&b": both; the evening of the catch is "flag:catch&!flag:home".)
        if (text.includes('&')) return text.split('&').every(t => this.cond(t));
        if (text.startsWith('!')) return !this.cond(text.slice(1));
        const [kind, v] = text.split(':');
        const save = this.save;
        switch (kind) {
            case 'flag': return save.flags.includes(v);
            case 'region': return save.regions.includes(Number(v));
            case 'card': return save.cards.includes(v);
            case 'verb': return save.verbs.includes(v);
            case 'carry': return this.carry?.kind === v;
            case 'books': return v === 'held' ? this.library.held().length > 0 : this.library.returned().length === BOOKS;
            case 'broken': return save.broken.includes(v);
            case 'block': return this.progress.blockLifted(v) && !this.progress.openAll;
        }
        return false;
    }

    // A pictogram for a speech bubble (requests are never words: §6.1.2), drawn here.
    icon(name) {
        const s = this.scene, key = `pict-${name}`;
        if (s.textures.exists(key)) return key;
        const g = s.make.graphics({ x: 0, y: 0 }, false);
        const ink = 0x2e222f;
        const draw = {
            tray: () => {
                g.fillStyle(ink, 1).fillRect(0, 10, 16, 3).fillEllipse(8, 10, 14, 16).fillRect(7, 0, 2, 3);
                g.fillStyle(0xc7dcd0, 1).fillRect(1, 11, 14, 1).fillEllipse(8, 10, 12, 14);
                g.fillStyle(0xffffff, 1).fillRect(4, 5, 2, 2);
                g.fillStyle(0xffffff, 1).fillRect(0, 13, 16, 3);
            },
            pills: () => {
                g.fillStyle(ink, 1).fillRect(3, 3, 10, 12).fillRect(4, 0, 8, 4);
                g.fillStyle(0xf9c22b, 1).fillRect(4, 4, 8, 10);
                g.fillStyle(0xffffff, 1).fillRect(5, 1, 6, 2).fillRect(5, 7, 6, 4);
                g.fillStyle(0xe83b3b, 1).fillRect(7, 7, 2, 4).fillRect(6, 8, 4, 2);
            },
            book: () => {
                g.fillStyle(ink, 1).fillRect(2, 1, 12, 14);
                g.fillStyle(0xae2334, 1).fillRect(3, 2, 10, 12);
                g.fillStyle(0xf3ecdd, 1).fillRect(11, 3, 1, 10).fillRect(5, 4, 5, 1).fillRect(5, 6, 4, 1);
            },
            cart: () => {
                g.fillStyle(ink, 1).fillRect(1, 2, 14, 10).fillRect(2, 12, 3, 3).fillRect(11, 12, 3, 3);
                g.fillStyle(0xc7dcd0, 1).fillRect(2, 3, 12, 8);
                g.fillStyle(0x4d9be6, 1).fillRect(3, 4, 10, 2).fillRect(3, 8, 10, 2);
            },
            softserve: () => {
                g.fillStyle(ink, 1).fillTriangle(3, 8, 13, 8, 8, 16).fillRect(4, 5, 8, 4).fillRect(5, 2, 6, 3).fillRect(7, 0, 2, 2);
                g.fillStyle(0xe6904e, 1).fillTriangle(5, 9, 11, 9, 8, 14);
                g.fillStyle(0xf68181, 1).fillRect(5, 6, 6, 2).fillRect(6, 3, 4, 3).fillRect(7, 1, 2, 2);
                g.fillStyle(0xffffff, 1).fillRect(6, 4, 1, 1).fillRect(5, 6, 2, 1);
            },
            canister: () => {
                g.fillStyle(ink, 1).fillRect(3, 3, 10, 13).fillRect(6, 0, 4, 4);
                g.fillStyle(0xc7dcd0, 1).fillRect(4, 4, 8, 11);
                g.fillStyle(0xf68181, 1).fillRect(4, 8, 8, 4);
                g.fillStyle(0xffffff, 1).fillRect(5, 5, 1, 9).fillRect(7, 1, 2, 2);
            },
            door: () => {
                g.fillStyle(ink, 1).fillRect(3, 0, 10, 16);
                g.fillStyle(0x8fd3ff, 1).fillRect(4, 1, 8, 14);
                g.fillStyle(0xffffff, 1).fillRect(5, 2, 1, 9).fillRect(7, 2, 1, 5);
                g.fillStyle(ink, 1).fillRect(9, 8, 2, 2);
            },
            camera: () => {
                g.fillStyle(ink, 1).fillRect(1, 4, 14, 10).fillRect(4, 2, 5, 3);
                g.fillStyle(0x625565, 1).fillRect(2, 5, 12, 8);
                g.fillStyle(ink, 1).fillCircle(8, 9, 4);
                g.fillStyle(0x8fd3ff, 1).fillCircle(8, 9, 3);
                g.fillStyle(0xffffff, 1).fillRect(7, 7, 1, 1).fillRect(12, 6, 2, 1);
            },
            // Region 8: a tall glass with mint and a straw; a steaming cup; the ship's horn.
            cocktail: () => {
                g.fillStyle(ink, 1).fillRect(4, 3, 8, 13).fillRect(10, 0, 2, 5);
                g.fillStyle(0xc7dcd0, 1).fillRect(5, 4, 6, 11);
                g.fillStyle(0xb9e04c, 1).fillRect(5, 7, 6, 8);
                g.fillStyle(0x239063, 1).fillRect(6, 6, 2, 2).fillRect(8, 9, 2, 2).fillRect(6, 12, 2, 1);
                g.fillStyle(0xffffff, 1).fillRect(5, 5, 1, 9);
                g.fillStyle(0xe83b3b, 1).fillRect(10, 1, 1, 6);
            },
            coffee: () => {
                g.fillStyle(ink, 1).fillRect(2, 7, 10, 9).fillRect(12, 9, 3, 5);
                g.fillStyle(0xffffff, 1).fillRect(3, 8, 8, 7).fillRect(12, 10, 2, 3);
                g.fillStyle(ink, 1).fillRect(12, 11, 1, 1);
                g.fillStyle(0x7a4528, 1).fillRect(3, 8, 8, 2);
                g.fillStyle(0x9babb2, 1).fillRect(4, 3, 1, 3).fillRect(5, 1, 1, 2).fillRect(8, 4, 1, 2).fillRect(9, 1, 1, 3);
            },
            // Region 9: a wedding cake, three tiers.
            cake: () => {
                g.fillStyle(ink, 1).fillRect(1, 10, 14, 6).fillRect(3, 5, 10, 6).fillRect(5, 1, 6, 5);
                g.fillStyle(0xffffff, 1).fillRect(2, 11, 12, 4).fillRect(4, 6, 8, 4).fillRect(6, 2, 4, 3);
                g.fillStyle(0xf68181, 1).fillRect(2, 13, 12, 1).fillRect(4, 8, 8, 1).fillRect(6, 3, 4, 1);
                g.fillStyle(0xe83b3b, 1).fillRect(7, 0, 2, 2);
            },
            horn: () => {
                g.fillStyle(ink, 1).fillRect(5, 5, 9, 6).fillTriangle(6, 8, 0, 1, 0, 15);
                g.fillStyle(0xf9c22b, 1).fillRect(6, 6, 7, 4).fillTriangle(6, 8, 1, 3, 1, 13);
                g.fillStyle(0xfbff86, 1).fillRect(6, 6, 7, 1);
                g.fillStyle(0xab947a, 1).fillRect(11, 11, 1, 3);
                g.fillStyle(0xe83b3b, 1).fillRect(10, 13, 3, 3);
            },
        }[name];
        (draw ?? (() => g.fillStyle(ink, 1).fillRect(6, 2, 4, 8).fillRect(6, 12, 4, 3)))();
        g.generateTexture(key, 16, 16);
        g.destroy();
        return key;
    }

    // A picture: a piece of the ship's atlas, one of the plan's things ("thing:robot"), or one the
    // game draws ("@tray").
    image(x, y, frame) {
        const s = this.scene;
        if (frame.startsWith('@')) return s.add.image(x, y, frame.slice(1));
        if (frame.startsWith('thing:')) return s.add.image(x, y, 'things', frame.slice(6));
        return s.add.image(x, y, 'shipart', frame);
    }

    // A burst of gold sparks at a spot.
    sparkle(x, y, tint = 0xf9c22b) {
        const s = this.scene;
        for (let i = 0; i < 10; i++) {
            const a = (Math.PI * 2 * i) / 10;
            const spark = s.add.image(x, y, 'dot').setTint(tint).setDepth(s.DEPTH.fx);
            this.add([spark]);
            s.tweens.add({ targets: spark, x: x + Math.cos(a) * 18, y: y + Math.sin(a) * 18, alpha: 0, duration: 450, onComplete: () => spark.destroy() });
        }
    }

    // A pickup lying somewhere glints now and then (the user, 2026-11-20: "a much softer, and slower spark
    // on the top right corner of every item"): a small star at its top right corner, fading in as it grows
    // and out as it shrinks over 1.6 s, turning a quarter round slowly as it shows (the user), once every 2.5 to
    // 3.5 s on the scene's clock, each thing in its own
    // time. Not the things handed to her or made for her, nor the tangerines. It goes with the picture:
    // hidden with it, gone once it is taken.
    // (`at()`: where it shows, if not the picture's top right corner; `when()`: only while it is true;
    // `small`: a size smaller, its arms one px: the bell's collar in the gull's beak, the user, 2026-11-20.)
    glint(img, { at = null, when = null, small = false } = {}) {
        const s = this.scene;
        const spark = s.add.image(0, 0, 'spark', 0).setDepth(img.depth + 0.005).setVisible(false);
        this.add([spark]);
        (this.glints ??= []).push({ img, spark, at, when, small, period: Phaser.Math.Between(2500, 3500), offset: Phaser.Math.Between(0, 3500) });
    }

    updateGlints(time) {
        const LONG = 1600, PEAK = 0.8;
        this.glints = (this.glints ?? []).filter(g => {
            if (!g.img.active) { g.spark.destroy(); return false; }
            const into = (time + g.offset) % g.period;
            const on = g.img.visible && g.img.alpha > 0.5 && into < LONG && (!g.when || g.when());
            g.spark.setVisible(on);
            if (!on) return true;
            // Eight steps: it grows over two, turns an eighth each step, shrinks over the last two; it fades
            // in and out as it does.
            const SIZES = g.small ? [0, 1, 1, 1, 1, 1, 1, 0] : [0, 1, 2, 2, 2, 2, 1, 0], step = Math.min(7, Math.floor(8 * into / LONG));
            const k = Math.sin(Math.PI * into / LONG);                     // 0, up to 1 halfway, back to 0
            const b = g.img.getBounds(), pt = g.at ? g.at() : { x: b.right - 1, y: b.y + 1 };
            g.spark.setPosition(Math.round(pt.x), Math.round(pt.y))
                .setFrame((step % 2) * 3 + SIZES[step]).setAlpha(PEAK * Math.max(0.35, k));
            return true;
        });
    }

    // A word over her for a moment (her own exclamations; `opts` for src/popup.js: `kind`, a hint's
    // 'plate'; `from`, 'bumbot' for his "Meow!" in her arms).
    say(text, ms = 900, opts = {}) {
        const s = this.scene;
        s.lockedUntil = s.time.now + ms;
        s.alert.setText(text, opts).setVisible(true);
        sfx.bubble();
        s.time.delayedCall(ms, () => { if (s.alert.text === text) s.alert.setVisible(false); });
    }

    // Someone who wants something shows it again: their bubble hops.
    nudge(person) {
        const s = this.scene;
        if (!person.bubbleItems) return;
        sfx.at(person.x, person.y).bubble();
        s.tweens.add({ targets: person.bubbleItems, y: '-=5', duration: 110, yoyo: true, repeat: 1 });
    }

    // A scripted moment: her input is off while `fn` runs (an async function), then play goes on.
    cut(fn) {
        const s = this.scene, p = s.player;
        s.mode = 'scripted';
        s.script = null;
        p.body.setVelocity(0, 0);
        s.pose('stand');
        // (One moment may begin before another has quite ended: play goes on after the last.)
        this.cuts = (this.cuts ?? 0) + 1;
        const done = () => {
            this.cuts--;
            if (s.mode === 'scripted' && !this.cuts) s.mode = 'play';
            this.refresh();
        };
        Promise.resolve().then(fn).then(done, err => { console.error(err); done(); });
    }

    wait(ms) {
        return new Promise(resolve => this.scene.time.delayedCall(ms, resolve));
    }

    tween(config) {
        return new Promise(resolve => this.scene.tweens.add({ ...config, onComplete: resolve }));
    }

    // Loose pictures at a spot, bottom to top (a tray and its load in someone's hands).
    prop(x, y, ...keys) {
        const s = this.scene;
        const items = keys.map((key, i) => s.add.image(x, y - i * 3, key).setOrigin(0.5, 1).setDepth(s.DEPTH.props + 0.1 + i * 0.01));
        this.add(items);
        return items;
    }

    // Someone hands her a thing: it crosses from their hands to hers, sparkles, and `then` it is hers.
    async handOver(person, frame, then, tint) {
        const s = this.scene, p = s.player;
        const img = this.image(person.x + person.dir * 12, person.y - 34, frame).setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.05);
        if (tint) img.setTint(tint);
        this.add([img]);
        if (person.meta.anims.give) this.people.play(person, 'give');
        await this.wait(350);
        sfx.at(person.x, person.y).give();
        await this.tween({ targets: img, x: p.x, y: p.y - 40, duration: 420, ease: 'Sine.easeInOut' });
        await this.received(img, frame, then);
    }

    // Someone tosses her a thing, with a clip of theirs (`clip`): it is in their fingers in the frames
    // `held` names ({ frame: [px ahead of their middle, px up from their feet] }, behind their hand),
    // leaves them at frame `release` from `from`, and flies to her chest in a lob, on the game's clock
    // (the scene's `update`, not a tween: the lesson of the tennis ball); then as `handOver`.
    tossOver(person, frame, then, tint, { clip, held, release, from }) {
        const s = this.scene, p = s.player, sp = person.sprite;
        if (!person.meta.anims[clip]) return this.handOver(person, frame, then, tint);
        const img = this.image(0, 0, frame).setOrigin(0.5, 0.5).setDepth(sp.depth - 0.001).setVisible(false);
        if (tint) img.setTint(tint);
        this.add([img]);
        const at = ([dx, up]) => img.setPosition(Math.round(person.x) + person.dir * dx, sp.y - up);
        return new Promise(resolve => {
            const hold = (anim, f) => {
                const i = f.index - 1;
                if (held[i]) at(held[i]).setVisible(true);
                else if (i < release) img.setVisible(false);
                if (i < release) return;
                sp.off('animationupdate', hold);
                at(from).setVisible(true).setDepth(s.DEPTH.player + 0.05);
                sfx.at(person.x, person.y).give();
                // (A lob: its top a fifth of the way across, at least 12 px over where it left; it
                // comes down on her where she is by then, if she has gone on meanwhile.)
                const x0 = img.x, y0 = img.y, tx0 = p.x, ty = p.y - 40, g = 400;
                const top = Math.max(12, Math.abs(tx0 - x0) * 0.2), vy = -Math.sqrt(2 * g * (y0 - Math.min(y0, ty) + top));
                const T = (-vy + Math.sqrt(Math.max(0, vy * vy - 2 * g * (y0 - ty)))) / g, t0 = s.time.now;
                const fly = () => {
                    const t = Math.min(T, (s.time.now - t0) / 1000);
                    const tx = tx0 + (p.x - tx0) * t / T;
                    img.setPosition(x0 + (tx - x0) * t / T, y0 + vy * t + g * t * t / 2);
                    if (t < T) return;
                    s.events.off('update', fly);
                    this.received(img, frame, then).then(resolve);
                };
                s.events.on('update', fly);
            };
            sp.on('animationupdate', hold);
            this.people.play(person, clip);
        });
    }

    // A thing handed or tossed to her has reached her: a sparkle, and it is hers.
    async received(img, frame, then) {
        const s = this.scene;
        if (frame === 'key-card') sfx.card();
        else sfx.take();
        for (let i = 0; i < 10; i++) {
            const a = (Math.PI * 2 * i) / 10;
            const spark = s.add.image(img.x, img.y - 8, 'dot').setTint(0xf9c22b).setDepth(s.DEPTH.fx);
            this.add([spark]);
            s.tweens.add({ targets: spark, x: img.x + Math.cos(a) * 20, y: img.y - 8 + Math.sin(a) * 20, alpha: 0, duration: 450, onComplete: () => spark.destroy() });
        }
        await this.tween({ targets: img, y: img.y - 14, alpha: 0, duration: 380 });
        img.destroy();
        then?.();
    }

    // A prop knocked over (the Seven Seas' fruit bowl, by Bumbot).
    topple(id) {
        const t = this.things.find(x => x.id === id);
        if (!t?.img || t.toppled) return;
        t.toppled = true;
        this.scene.tweens.add({ targets: t.img, angle: -100, x: t.img.x - 10, y: t.img.y + 4, duration: 260, ease: 'Quad.easeIn' });
        sfx.at(t.x, t.y).crash();
    }

    // One of her quirks: she turns to the thing and does her bit; any key after a moment ends it.
    quirk(thing) {
        const s = this.scene, p = s.player;
        if (thing.gag === 'bed') return this.peekBed(thing);
        if (this.carry || !s.anims.exists(`her-${thing.clip}`)) return false;
        this.cut(async () => {
            p.setFlipX(thing.face ? thing.face < 0 : thing.x < p.x);
            p.anims.play(`her-${thing.clip}`);
            // (Something near joins in: the disco ball throws its lights while she dances.)
            if (thing.glitter) {
                const [gx, gy] = thing.glitter;
                for (let i = 0; i * 400 < thing.ms; i++) {
                    s.time.delayedCall(i * 400, () => this.sparkle(gx + Phaser.Math.Between(-8, 8), gy + Phaser.Math.Between(-5, 5), [0xffffff, 0xf9c22b, 0x8fd3ff, 0xf68181][i % 4]));
                }
            }
            if (thing.say) this.say(thing.say, thing.ms);
            // (Her bow on the stage is to a house that claps; her dance has a beat to it.)
            if (thing.clip === 'bow') sfx.clap(thing.ms / 1000);
            if (thing.clip === 'dance') for (let i = 0; i * 500 < thing.ms; i++) s.time.delayedCall(i * 500, () => sfx.thump());
            await this.wait(thing.ms);
            s.pose('stand');
            if (!this.save.seen.includes(thing.id)) {
                sfx.secret();
                this.save.seen.push(thing.id);
                writeSave(this.save);
            }
        });
        return true;
    }

    // Deck 8's open cabin (`sec_peek_sea`; the user, 2026-11-18: "since it now reads as interactable,
    // let's add some gag at the E press"): she steps in and bounces on its made-up
    // bed, seen through the door: cut to its opening (her head under the lintel at each bounce), washed
    // 30% toward the wall as the room is ("she's in the background"); out again, she straightens her
    // badge. Any key ends the bouncing.
    peekBed(thing) {
        const s = this.scene, p = s.player, door = this.things.find(t => t.id === thing.door);
        if (!door || this.carry || s.holding || s.towel) return false;
        const meta = s.cache.json.get('her-meta');
        // (The opening, past the leaf swung in: the picture's columns 7 to 31, rows 2 to 72.)
        const x0 = door.x - 10, x1 = door.x + 14, top = door.y - 72, BED = 22;
        const ghost = s.add.sprite(p.x, p.y, 'her').setOrigin(0.5, 1).setTint(0xece3cf).setTintMode(Phaser.TintModes.FILL).setAlpha(0.3).setVisible(false);
        this.add([ghost]);
        let inside = false;
        const cut = () => {
            if (!inside) { p.setCrop(); ghost.setVisible(false); return; }
            const fw = p.frame.width, fh = p.frame.height, left = Math.round(p.x) - fw / 2;
            let cx = x0 - left;
            const cw = x1 - x0 + 1, cy = top - (Math.round(p.y) - fh), ch = door.y - top;
            if (p.flipX) cx = fw - (cx + cw);
            p.setCrop(cx, cy, cw, ch);
            ghost.setTexture(p.texture.key, p.frame.name).setPosition(p.x, p.y).setFlipX(p.flipX)
                .setDepth(p.depth + 0.001).setCrop(cx, cy, cw, ch).setVisible(true);
        };
        s.events.on('postupdate', cut);
        const side = p.x < door.x ? -1 : 1, floor = p.y;
        const move = (to, ms, key = 'x') => this.tween({ targets: p, [key]: to, duration: ms });
        this.cut(async () => {
            try {
                p.body.enable = false;
                // In at the door, her back to us, at once (the user, 2026-11-18: a glance each way first
                // was "the delay after the E press").
                s.pose('run');
                p.setFlipX(door.x + 2 < p.x);
                await move(door.x + 2, Math.abs(door.x + 2 - p.x) * 7 + 40);
                s.pose('back');
                inside = true;
                await this.wait(260);
                // Up onto the bed.
                s.pose('rise');
                await move(floor - BED - 6, 140, 'y');
                await move(floor - BED, 90, 'y');
                // Bouncing, facing us, as on her own cabin's bed.
                const frames = meta.anims['bed-joy'];
                p.anims.stop();
                p.setFlipX(false);
                await new Promise(done => {
                    let t = 0, g0 = 0;
                    const step = (time, delta) => {
                        const i = s.controls.state;
                        t += delta;
                        const phase = (t % BED_JOY.cycleMs) / BED_JOY.cycleMs;
                        p.setTexture('her', frames[Math.floor(phase * frames.length)]);
                        const g = ((phase * 2) % 1 + 0.35) % 1;
                        if (g >= BED_JOY.air && !(g0 >= BED_JOY.air)) sfx.at(door.x, door.y).boing();
                        g0 = g;
                        p.y = floor - BED - (g < BED_JOY.air ? Math.round(BED_JOY.hop * Math.sin(Math.PI * g / BED_JOY.air)) : 0);
                        const key = t > 300 && (i.left || i.right || i.up || i.down || i.jumpPressed || i.dashPressed || i.activatePressed);
                        if (key || t > BED_JOY.cycleMs * 4) {
                            s.events.off('update', step);
                            done();
                        }
                    };
                    s.events.on('update', step);
                });
                // Down, and out the way she came.
                s.pose('fall');
                await move(floor, 130, 'y');
                s.pose('front');
                await this.wait(160);
                inside = false;
                s.pose('run');
                p.setFlipX(side < 0);
                await move(door.x + side * 30, 200);
                // Straightening her badge.
                p.anims.stop();
                for (const f of meta.anims.badge) {
                    p.setTexture('her', f);
                    await this.wait(110);
                }
            } finally {
                s.events.off('postupdate', cut);
                inside = false;
                p.setCrop();
                ghost.destroy();
                p.y = floor;
                p.body.enable = true;
                p.body.reset(p.x, floor);
                s.pose('stand');
            }
            if (!this.save.seen.includes(thing.id)) {
                sfx.secret();
                this.save.seen.push(thing.id);
                writeSave(this.save);
            }
        });
        return true;
    }

    // Standing still by a quirk's spot long enough sets it off.
    updateQuirks(time) {
        const s = this.scene, p = s.player;
        if (s.mode !== 'play') return;
        const still = Math.abs(p.body.velocity.x) < 5 && (p.body.blocked.down || p.body.touching.down);
        for (const t of this.things) {
            if (!t.quirk || !t.trigger.startsWith('still') || !this.shown(t)) continue;
            // (Still at the spot: counted from when she stopped there, not from before she came.)
            if (!still || Math.abs(p.x - t.x) > (t.reach ?? 20) || Math.abs(p.y - t.y) > 8) {
                t.stillSince = null;
                continue;
            }
            t.stillSince ??= time;
            if (time - t.stillSince > Number(t.trigger.split(':')[1]) * 1000 && time > (t.again ?? 0)) {
                t.again = time + 15000;
                t.stillSince = null;
                this.quirk(t);
            }
        }
    }

    // She has run into someone (the people's `touch`): a fright that fits, or with a tray a spill.
    touched(person) {
        const s = this.scene, t = person.touch;
        if (s.time.now < (this.touchCool ?? 0) || s.mode !== 'play') return;
        // (In a lunge she is through them: src/world/people.js has what each does about it.)
        if (!this.carry && s.lungeSafe()) {
            this.lunged(t.fright, person.x);
            return;
        }
        // (Their speed along the deck and their facing: which way the hit takes her, §1.6.)
        const walking = person.walk && s.time.now >= (person.pausedUntil ?? 0);
        const how = { vx: walking ? person.dir * person.walk.v * 48 : 0, dir: person.dir ?? 0 };
        if (this.carry) {
            this.touchCool = s.time.now + 1200;
            sfx.at(person.x, person.y).oh();
            this.carryBox.spill(person.x, false, t.fright || null, how);
        } else if (t.kind === 'scare') {
            if (!s.holding) sfx.at(person.x, person.y).hey();
            // (The porter's cart: who is in it, for her gag with him, 8a to 8d; the jogger, for 9b.)
            s.scareContact(person.x, t.fright, { ...how, ride: t.fright === 'cart' || t.fright === 'jogger' ? { person } : null });
        }
    }

    // --- D: the cry and the lunge (docs/plan-three-uses.md §1.1, §2) ----------------------------

    // "Кісюнічка!!!": everyone and everything within the cry's reach on her deck and route hears
    // it (`heard()`), each in its own manner; machines do not.
    shout(x, y, route) {
        this.cry = { x, y, route, time: this.scene.time.now };
        this.people.heard(this.cry);
        for (const m of this.movers) m.heard?.(this.cry);
        this.story.heard(this.cry);
    }

    // Whether a thing at (x, y) on `route` is within the last cry's reach: on her deck, near her.
    hears(x, y, route = 'inside', reach = CRY.reach) {
        const c = this.cry;
        return !!c && c.route === route && Math.abs(x - c.x) < reach && Math.abs(y - c.y) < 70;
    }

    // In a lunge something would have frightened her by contact: she is through. What touched her
    // gives way in its own manner (each mover's and person's `lunged()`); a few leave a mark on her.
    // Once for each thing, however many frames she is in it.
    lunged(kind, fromX) {
        const s = this.scene, p = s.player, time = s.time.now;
        const key = `${kind}@${Math.round(fromX / 24)}`;
        this.lungedAt ??= {};
        if (time < (this.lungedAt[key] ?? 0)) return;
        this.lungedAt[key] = time + 1500;
        for (const m of this.movers) if (m.lunged?.(kind, fromX)) return;
        if (this.people.lunged(kind, fromX)) return;
        const head = p.y - PLAYER.height + 6;
        const mark = MISHAPS[kind]?.mark;
        if (mark === 'wet') this.drops(p.x, head, 0x8fd3ff, 1);
        else if (mark) this.drops(p.x, head, mark === 'soot' ? 0x625565 : 0xffffff, -1);
    }

    // A gull takes the tangerine from her as it swoops (docs/plan-three-uses.md §1.6, 20 to 22): it
    // goes from (x, y) to its beak and away with it.
    snatch(sprite, x, y) {
        const s = this.scene, t0 = s.time.now;
        // (In its beak: behind the bird, so that the beak closes over the fruit's top, frame by frame;
        // the user, 2026-11-18: it sat on the gull's back.)
        const img = s.add.image(x, y, 'tangerine').setOrigin(0.5, 0.6).setDepth(sprite.depth - 0.001);
        this.add([img]);
        const follow = () => {
            const k = Math.min(1, (s.time.now - t0) / 160);
            const b = this.inBeak(sprite);
            img.setOrigin(0.5, 0.6 + (0.15 - 0.6) * k);
            img.setPosition(x + (b.x - x) * k, y + (b.y - y) * k).setAlpha(sprite.alpha);
            if (s.time.now - t0 > (sprite.snatchMs ?? 1800) || !sprite.visible || !sprite.active) {
                s.events.off('postupdate', follow);
                img.destroy();
            }
        };
        // (After the bird has moved and flapped this frame: placed before it, the fruit took the other
        // wing frame's beak every other frame, 5 px off.)
        s.events.on('postupdate', follow);
    }

    // A tangerine loose near something (src/world/tangerine.js), each frame until one wants it:
    // whoever takes it has it (`offered(t)` true; it calls `this.scene.loose.remove(t)` or keeps it).
    offered(t) {
        if (this.scene.offeredHere?.(t) || this.lobbedInto(t)) return true;
        for (const m of this.movers) if (m.offered?.(t)) return true;
        return !!this.people.offered?.(t) || !!this.story.offered?.(t);
    }

    // Something at a cabin's door taken in by whoever is inside (the paper round's papers, the
    // breakfasts): the door opens a crack at its handle's side (these doors have their handles on
    // the left), a hand reaches out at `handY` and draws the things in, and the door shuts. `took()`
    // once the hand has drawn them in (whoever held them out lowers their hands then), `done()` once
    // the door is shut. `shrink`: taken from where they are held, not slid to the door: they shrink
    // a little, as if drawn in through it, and are gone (the breakfast tray: slid sideways it
    // crossed the stewardess holding it, the user, 2026-11-17).
    handTakes(door, y, things, handY, done, { took, shrink = false } = {}) {
        const s = this.scene, D = s.DEPTH, x = door - 11;
        const crack = s.add.rectangle(x, y - 2, 4, 68, 0x2e222f).setOrigin(0.5, 1).setDepth(D.decor + 0.15).setScale(0, 1);
        // (The hand in its shirt cuff is generated, `things`' `door-hand`, reaching to the right; it had
        // been a 4 x 2 rectangle: the art rule looked back over, the user, 2026-11-17.)
        const near = things[0];
        const hand = s.add.image(x, handY, 'things', 'door-hand').setOrigin(0.5, 1).setDepth(D.props + 0.03).setVisible(false)
            .setFlipX(near.x < x);
        this.add([crack, hand]);
        sfx.at(door, y).door();
        s.tweens.chain({ tweens: [
            { targets: crack, scaleX: 1, duration: 200 },
            { targets: hand, x: near.x - Math.sign(near.x - x) * 3, duration: 260, onStart: () => hand.setVisible(true) },
            ...(shrink ? [
                { targets: things, scale: 0.75, duration: 220, ease: 'Sine.easeIn' },
                { targets: [hand, ...things], alpha: 0, duration: 110, onComplete: () => { hand.destroy(); things.forEach(t => t.destroy()); took?.(); } },
            ] : [
                { targets: [hand, ...things], x, duration: 300, ease: 'Sine.easeIn', onComplete: () => { hand.destroy(); things.forEach(t => t.destroy()); took?.(); } },
            ]),
            { targets: crack, scaleX: 0, duration: 200, onComplete: () => { crack.destroy(); sfx.at(door, y).doorShut(); done?.(); } },
        ] });
    }

    // Where a tangerine hangs from a gull's beak, its stem in it: the beak's tip and row in each of the
    // gull's frames (the things atlas, measured from its pixels: the orange beak), through the sprite's
    // origin and flip. The fruit is drawn with origin (0.5, 0.15), just short of the tip.
    inBeak(sprite) {
        const b = GULL_BEAKS[sprite.frame.name] ?? [sprite.width - 1, sprite.height / 2];
        const left = sprite.x - sprite.originX * sprite.width, top = sprite.y - sprite.originY * sprite.height;
        const dir = sprite.flipX ? -1 : 1;
        const tip = sprite.flipX ? left + sprite.width - 1 - b[0] : left + b[0] + 1;
        return { x: tip - dir * 2, y: top + b[1] + 0.5 };
    }

    // A gull comes down to a tangerine, pecks at it and flies off with it in its beak
    // (docs/plan-three-uses.md §2). The bird's sprite is the caller's: left hidden at the end, its
    // origin as it was, for the caller to bring back; `done()` then.
    gullTakes(sprite, t, done) {
        const s = this.scene, img = s.loose.claim(t);
        const ox = sprite.originX, oy = sprite.originY;
        const x = img.x, foot = img.y + 3, off = x < sprite.x ? -1 : 1;
        const down = s.textures.get('things').has('gull-down');
        img.setDepth(sprite.depth - 0.001);
        sprite.setOrigin(0.5, 1).setVisible(true).setAlpha(1).setFlipX(off < 0);
        const flap = s.time.addEvent({ delay: 120, loop: true, callback: () => sprite.setFrame(sprite.frame.name === 'gull-up' && down ? 'gull-down' : 'gull-up') });
        sfx.at(x, foot).gull();
        // (It lands just short of it, the fruit before its beak; a few pecks; away with it.)
        s.tweens.add({ targets: sprite, x: x - off * 6, y: foot, duration: 520, ease: 'Sine.easeIn', onComplete: () => {
            flap.paused = true;
            sprite.setFrame('gull-perched');
            s.tweens.add({ targets: sprite, y: foot - 1, duration: 140, yoyo: true, repeat: 3, onComplete: () => {
                flap.paused = false;
                sfx.at(x, foot).flap();
                // (In its beak, placed after the bird has moved and flapped each frame.)
                const hold = () => {
                    const b = this.inBeak(sprite);
                    img.setOrigin(0.5, 0.15).setPosition(b.x, b.y).setAlpha(sprite.alpha);
                };
                s.events.on('postupdate', hold);
                s.tweens.add({ targets: sprite, x: x + off * 90, y: foot - 140, alpha: 0, duration: 1000, ease: 'Quad.easeIn',
                    onComplete: () => {
                        s.events.off('postupdate', hold);
                        flap.remove();
                        img.destroy();
                        sprite.setVisible(false).setAlpha(1).setOrigin(ox, oy);
                        done?.();
                    } });
            } });
        } });
    }

    // A machine that has swallowed a tangerine (a vacuum): dead where it stands, a wisp of smoke off
    // it now and then (each caller on its own clock), until she has left the deck.
    choke(sprite) {
        sprite.setTint(0x6b6e72).setAngle(-8);
        sfx.at(sprite.x, sprite.y).vacChoke();
        this.drops(sprite.x, sprite.y - 10, 0x8a8a8a, -1);
    }

    // A few drops off her (`dir` 1: falling, water), or a wisp off her hair (-1: rising, smoke).
    drops(x, y, colour, dir) {
        const s = this.scene;
        for (let i = 0; i < 6; i++) {
            const d = s.add.image(x + Phaser.Math.Between(-7, 7), y + Phaser.Math.Between(-3, 3), 'dot').setTint(colour).setDepth(s.DEPTH.fx);
            this.add([d]);
            s.tweens.add({ targets: d, y: d.y + dir * Phaser.Math.Between(12, 22), x: d.x + Phaser.Math.Between(-4, 4), alpha: 0,
                duration: Phaser.Math.Between(380, 620), delay: i * 50, onComplete: () => d.destroy() });
        }
    }

    // A pictogram over a spot for a moment (a "!" startled, a heart, a finger to the lips).
    pop(x, y, icon, ms = 1500) {
        const s = this.scene, D = s.DEPTH, w = 22, h = 20;
        const g = s.add.graphics().setDepth(D.fx + 0.5).setPosition(x, y);
        g.fillStyle(0x2e222f, 1).fillRoundedRect(-w / 2 - 1, -h - 1, w + 2, h + 2, 4);
        g.fillStyle(0xffffff, 1).fillRoundedRect(-w / 2, -h, w, h, 3);
        g.fillStyle(0x2e222f, 1).fillTriangle(-4, 1, 4, 1, 0, 6);
        g.fillStyle(0xffffff, 1).fillTriangle(-3, 0, 3, 0, 0, 4);
        // (The cry's two answers are generated, a heart and a speaker crossed out for a quiet place; the
        // finger to the lips never read at a bubble's size: the user, 2026-11-17.)
        const pict = { heart: 'icon-heart', shh: 'icon-mute' }[icon];
        const img = (pict ? s.add.image(x, y - h / 2, 'things', pict) : s.add.image(x, y - h / 2, this.icon(icon))).setDepth(D.fx + 0.51);
        this.add([g, img]);
        s.tweens.add({ targets: [g, img], y: '-=4', duration: 120, yoyo: true });
        s.time.delayedCall(ms, () => {
            s.tweens.add({ targets: [g, img], alpha: 0, duration: 200, onComplete: () => { g.destroy(); img.destroy(); } });
        });
        return [g, img];
    }

    // --- Each frame -----------------------------------------------------------------------------

    update(dt, time, input) {
        const s = this.scene, p = s.player;
        if (!this.built || !p) return;
        // Off a ladder between routes: she is on the route of the end she left it at.
        if (this.onLadder && s.mode !== 'ladder') {
            const L = this.onLadder;
            s.route = p.y <= L.y1 + 2 ? L.routeTop : L.routeBottom;
            this.onLadder = null;
        }
        this.updateDuct(input, time);
        this.updateSpecials(time);
        if (s.route !== this.lastRoute) this.refresh();
        this.people.update(dt, time);
        for (const m of this.movers) m.update(dt, time);
        this.carryBox.update();
        this.story.update(dt, time, input);
        this.updateQuirks(time);
        this.updateHud();
        // (Her raised fist is 6 to 9 px in front of her middle, 49 to 53 px over her feet, in both
        // frames of the glide: the shaft comes up out of it, the crook hangs under it, and the
        // parasol is drawn behind her so that the hand is on the shaft, not under it.)
        if (this.parasol?.visible) this.parasol.setPosition(p.x + (p.flipX ? -8 : 8), p.y - PLAYER.height + 18).setFlipX(p.flipX).setDepth(p.depth - 0.01);
    }

    // Gusts along the ship's side push her aft while she is in the air (src/world/outside.js).
    push(dt, onFloor) {
        const x = this.scene.player.x;
        for (const g of this.winds) g.push(dt, onFloor);
        // A gust carrying her (the balconies, the bow): a faint tremor while it does.
        if (this.scene.player.x !== x) rumbleNow('gust', 400);
        this.offPartition();
    }

    // A balcony's partition is a wall, never a ledge: coming down on its top she slips off it, to
    // the side she is more on.
    offPartition() {
        const s = this.scene, p = s.player;
        if (s.route !== OUTSIDE || p.body.velocity.y < 0) return;
        const half = PLAYER.bodyWidth / 2;
        for (const z of this.wallZones) {
            const dx = p.x - z.x, reach = z.width / 2 + half;
            if (z.width > 6 || Math.abs(dx) >= reach || p.body.bottom < z.body.top - 3 || p.body.bottom > z.body.top + 12) continue;
            // (The way she is going, if she is going anywhere: a vault carries on over it.)
            const vx = p.body.velocity.x;
            const to = z.x + (Math.abs(vx) > 20 ? Math.sign(vx) : dx >= 0 ? 1 : -1) * (reach + 0.5);
            p.body.x += to - p.x;
            p.x = to;
            return;
        }
    }

    // E: a cart's end, a pickup, a switch, a hatch.
    interact() {
        const s = this.scene, p = s.player;
        if (s.holding) return false;        // Bumbot in her arms: no hand for anything
        if (this.story.interact()) return true;
        for (const t of this.pushables) {
            if (this.carry) break;          // her hands are full
            if (t.route !== s.route || Math.abs(p.y - t.y) > 4 || (t.flag && this.progress.has(t.flag) && !t.free)) continue;
            if (!this.met(t.needs)) continue;
            const side = p.x < t.x ? -1 : 1;
            if (t.sides && side !== t.sides) continue;
            const end = t.width / 2 + PLAYER.bodyWidth / 2;
            // (A cart by the wall: she steps to its end and takes hold.)
            if (t.top && Math.abs(Math.abs(p.x - t.x) - end) < 18) p.body.reset(t.x + side * (end + 1), p.y);
            if (Math.abs(Math.abs(p.x - t.x) - end) < 10) return s.startPush(t);
        }
        for (const t of this.things) {
            if (!t.interact || t.done || !this.shown(t)) continue;
            if (Math.abs(p.x - t.x) > (t.reach ?? 18)) continue;
            // (`from`: taken only standing that high, the plant from the maid's bed; else from the floor or up there.)
            if (t.from != null ? Math.abs(p.y - (t.y - t.from)) > 4 : (Math.abs(p.y - t.y) > 8 && Math.abs(p.y - (t.level ?? t.y)) > 8)) continue;
            if (t.high && Math.abs(p.y - t.level) > 8) continue;
            if (t.interact() !== false) return true;
        }
        return false;
    }

    // `needs`: a flag's name, or a condition ("broken:<id>").
    met(needs) {
        return !needs || (needs.includes(':') ? this.cond(needs) : this.progress.has(needs));
    }

    shown(t) {
        if (t.done || !this.met(t.needs)) return false;
        if (t.after && !this.cond(t.after)) return false;
        if (t.until && this.cond(t.until)) return false;
        return t.route === 'inside' || t.route === this.scene.route || t.route === this.peek;
    }

    showParasol(on) {
        const s = this.scene;
        if (!this.parasol) {
            if (!on) return;
            this.parasol = s.add.image(0, 0, 'things', 'parasol-open').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.02);
            this.add([this.parasol]);
        }
        this.parasol.setVisible(on);
    }

    // What a flag changes (the builder's `flagGives`): a verb learned at a beat, another flag.
    onFlag(name) {
        for (const g of this.data.flagGives[name] || []) {
            const [type, what] = g.split(':');
            if (type === 'verb') {
                this.progress.learn(what);
            } else {
                this.progress.setFlag(what);
            }
        }
        if (name === 'drain') this.drainPool(false);
        this.story.onFlag(name);
        this.refresh();
    }

    // The first pool drains (population §6.7): its water goes, and with it the swimming; the hatch
    // in the tank's floor shows.
    drainPool(atOnce) {
        const s = this.scene, h = this.data.hatchPool;
        const pool = s.pools.find(w => h.x > w.x0 && h.x < w.x1 && w.deck === 11);
        if (!pool) return;
        const out = () => {
            // No water left: no swimming; if she was in it, she stands in the tank.
            s.pools = s.pools.filter(w => w !== pool);
            if (s.mode === 'swim' && s.pool === pool) {
                s.mode = 'play';
                s.pool = null;
                s.player.setDepth(s.DEPTH.player);
                s.player.body.enable = true;
                s.player.body.reset(s.player.x, pool.bottom);
                s.takeoffY = pool.bottom;
                s.pose('stand');
            }
            [pool.water, pool.ripples].forEach(o => o.setVisible(false));
            pool.gurgle?.destroy();
        };
        if (atOnce) return out();
        // Over five seconds its surface sinks to the tank's floor, and she sinks with it; a whirl
        // of bubbles over the drain.
        const top = pool.y, depth = pool.bottom - pool.y;
        pool.gurgle = s.add.graphics().setDepth(s.DEPTH.poolWater + 0.02);
        this.add([pool.gurgle]);
        sfx.at(h.x, top).drain(5);
        rumble('drain');
        s.tweens.addCounter({
            from: 0, to: 1, duration: 5000,
            onUpdate: tw => {
                const k = tw.getValue(), y = top + depth * k;
                pool.y = y;
                pool.water.clear().fillStyle(0x4d9be6, 0.55).fillRect(pool.x0, y, pool.x1 - pool.x0, pool.bottom - y);
                pool.water.fillStyle(0x8fd3ff, 0.9).fillRect(pool.x0, y, pool.x1 - pool.x0, 1);
                pool.ripples.y = y + 1;
                const g = pool.gurgle.clear(), t = s.time.now;
                for (let i = 0; i < 5; i++) {
                    const a = t / 140 + i * 1.26, r = 9 - i * 1.4;
                    g.fillStyle(0xffffff, 0.8).fillRect(h.x + Math.cos(a) * r, Math.min(pool.bottom - 2, y + 2 + i), 2, 1);
                }
                if (s.mode === 'swim' && s.pool === pool) {
                    // (Too shallow to swim: her feet find the floor.)
                    if (pool.bottom - y < 16) out();
                    else s.player.y = Math.min(y + SWIM.float, pool.bottom);
                }
            },
            onComplete: out,
        });
    }

    // What shows now: things whose flag has come, things in the room she is in; rooms that appear.
    refresh() {
        if (!this.built) return;
        const s = this.scene, P = this.progress;
        this.lastRoute = s.route;
        for (const e of this.pending.slice()) {
            if (!this.met(e.needs)) continue;
            this.pending.splice(this.pending.indexOf(e), 1);
            this.placeTangerine(e);
        }
        for (const t of this.things) {
            const on = this.shown(t);
            for (const i of t.items) i.setVisible(on);
            if (t.zone?.body && (t.until || t.after)) t.zone.body.enable = on;
        }
        this.people.refresh();
        this.library.refresh();
        for (const r of Object.values(this.rooms)) {
            if (!r.def) continue;
            r.hidden = !!r.needs && !P.has(r.needs);
            r.outside.forEach(o => o.setVisible(!r.hidden));
        }
        for (const cat of s.cats) {
            if (!cat.flag) continue;
            cat.hidden = !P.has(cat.needs);
            if (cat.route === 'inside') cat.sprite.setVisible(!cat.hidden && !cat.away);
        }
        for (const g of this.gates || []) {
            const open = P.flagSet(g.needs);
            if (g.hide) g.tiles.forEach(t => t.setAlpha(open ? 1 : 0));
            g.lid?.setVisible(!open);
            g.extra?.forEach(i => i.setVisible(!open));
        }
        // The books' and the things to find's counts (src/hud.js).
        s.hud?.refresh();
    }

    addColliders(p) {
        const s = this.scene;
        s.physics.add.collider(p, this.platZones, null, (_, z) => s.route === OUTSIDE
            && (z.plat.solid || (s.droppingThrough !== z.plat && !(s.overRail && s.gliding && z.plat.drop)
                && p.body.velocity.y >= 0 && p.body.bottom <= z.body.top + 10)));
        // (A partition is a wall, never a ledge: coming down on its top she slips off it.)
        s.physics.add.collider(p, this.wallZones, null, (_, z) => s.route === OUTSIDE && p.body.bottom > z.body.top + 5);
        s.physics.add.collider(p, this.ductFloor, null, () => s.route === 'duct');
        for (const t of this.pushables) {
            s.physics.add.collider(p, t.zone, null, () => t.route === s.route
                && (!t.top || (p.body.velocity.y >= 0 && p.body.bottom <= t.zone.body.top + 10 && s.pushing !== t)));
        }
        for (const t of this.lows) s.physics.add.collider(p, t.zone, null, () => t.route === s.route);
        // (`through`: one that a lunge goes past, the breakfast trolley.)
        for (const t of this.solids) s.physics.add.collider(p, t.zone, null, () => t.route === s.route && !(t.through && s.isLunging()));
        for (const r of this.robots ?? []) r.addCollider(p);
        // The lunge goes through a breakable, and it is gone for good.
        for (const t of this.breakables) {
            s.physics.add.collider(p, t.zone, null, () => {
                if (t.route !== s.route || t.done) return false;
                if (!s.isLunging()) return true;
                this.breakThing(t);
                return false;
            });
        }
    }

    // A breakable smashed (by her lunge; the piñata by a lob too): gone for good.
    breakThing(t) {
        const s = this.scene;
        t.done = true;
        s.smash(t.x, t.y - (t.hang ?? 0) - 12);
        if (t.hang) this.confetti(t.x, t.y - t.hang - 10, t.y);
        if (t.lowZone) this.low = this.low.filter(z => z !== t.lowZone);
        this.save.broken.push(t.id);
        t.items.forEach(i => i.destroy());
        t.items = [];
        t.zone.destroy();
        this.refresh();
    }

    // A lobbed tangerine that meets a thing hung up (the piñata) brings it down: three for one
    // (docs/plan-three-uses.md §2). Anything else breakable it only bounces off.
    lobbedInto(t) {
        if (!t.thrown || !t.lob) return false;
        const x = t.img.x, y = t.img.y;
        // A thing to find up on a shelf: knocked off it, down to the floor, hers from there; the
        // tangerine bounces off it and goes on.
        for (const k of this.things) {
            if (!k.high || k.done || k.route !== t.route || !k.pick?.active) continue;
            const b = k.pick.getBounds();
            if (x < b.left - 4 || x > b.right + 4 || y < b.top - 4 || y > b.bottom + 4) continue;
            k.high = false;
            k.level = k.y;
            t.img.body.velocity.x *= -0.4;
            sfx.at(k.x, k.y).plop();
            this.scene.tweens.add({ targets: k.pick, y: k.y, angle: 180, duration: 420, ease: 'Bounce.easeOut' });
            return false;
        }
        for (const b of this.breakables) {
            if (!b.hang || b.done || b.route !== t.route) continue;
            const z = b.zone.body;
            if (x < z.left - 4 || x > z.right + 4 || y < z.top - 4 || y > z.bottom + 4) continue;
            this.scene.loose.remove(t);
            this.breakThing(b);
            return true;
        }
        return false;
    }

    // A burst of paper and sweets, coming down to the floor (the pinata).
    confetti(x, y, floor) {
        const s = this.scene, colours = [0xe83b3b, 0xf9c22b, 0x4d9be6, 0x1ebc73, 0xf68181, 0xffffff];
        for (let i = 0; i < 26; i++) {
            const bit = s.add.rectangle(x + Phaser.Math.Between(-6, 6), y, 2 + (i % 2), 2, colours[i % colours.length]).setDepth(s.DEPTH.fx);
            this.add([bit]);
            const dx = Phaser.Math.Between(-46, 46);
            s.tweens.add({ targets: bit, x: bit.x + dx * 0.5, y: y - Phaser.Math.Between(8, 30), duration: 200, ease: 'Quad.easeOut',
                onComplete: () => s.tweens.add({ targets: bit, x: bit.x + dx * 0.5, y: floor - 1, angle: Phaser.Math.Between(-200, 200),
                    duration: Phaser.Math.Between(500, 900), ease: 'Quad.easeIn',
                    onComplete: () => s.tweens.add({ targets: bit, alpha: 0, delay: 2500, duration: 600, onComplete: () => bit.destroy() }) }) });
        }
    }

    // What she carries, on the HUD, with how much of it is left (a melting cone, a cooling cup).
    updateHud() {
        if (!this.hudCarry) return;
        const left = this.carryBox.left();
        this.hudCarry.back.setVisible(left !== null);
        this.hudCarry.bar.setVisible(left !== null);
        // (A cone melts: blue, red when nearly gone. A cup cools: orange while hot, blue when nearly cold.)
        const hot = this.carry?.kind === 'coffee';
        if (left !== null) this.hudCarry.bar.setSize(100 * left, 6).setFillStyle(hot ? (left > 0.35 ? 0xf79617 : 0x4d9be6) : left > 0.35 ? 0x8fd3ff : 0xe83b3b);
    }

    // What she carries and how much of it is left, a bar under the cards (the counts: src/hud.js).
    buildHud(layer) {
        const s = this.scene;
        const back = s.add.rectangle(24, 146, 104, 10, 0x1d2b53).setOrigin(0).setVisible(false);
        const bar = s.add.rectangle(26, 148, 100, 6, 0x8fd3ff).setOrigin(0).setVisible(false);
        this.hudCarry = { back, bar };
        layer.add([back, bar]);
        this.refresh();
    }
}
