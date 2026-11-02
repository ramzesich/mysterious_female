import { VIEW, PLAYER, DASH, IDLE, BUMBOT, LIFT, SIDEWALK, SWIM, LONG_FALL_MARGIN } from '../config.js';
import { Controls } from '../controls.js';
import { sfx } from '../sfx.js';
import { loadSave, writeSave } from '../save.js';
import { GLASS_LEAF, TRUNK_INSIDE } from '../textures.js';

// Tile ids from the tileset (see tools/build_slice_map.py).
const LADDER_TOP = 3;

const DEPTH = {
    sky: 0, sea: 1, back: 2, decor: 3, stairs: 4, playerBehind: 5, balustrade: 5.1,
    glassShaft: 5.15, glassCar: 5.2, inGlassCar: 5.25, glassDoors: 5.3,
    frontStairs: 5.4, onFrontStairs: 5.45, frontBalustrade: 5.5, walkFloor: 5.6,
    solid: 6, ladders: 7, liftCar: 7.4, inLift: 7.6, props: 8, player: 9, fx: 10,
};

const approach = (value, target, step) =>
    value < target ? Math.min(value + step, target) : Math.max(value - step, target);

const HALF = PLAYER.height / 2;
const LAMP_RISE = 81; // the checkpoint lamp sits just above the 74px door
const DOOR = { width: 28, height: 74 };
const LEAF = 18; // each of an elevator's two sliding door leaves

// How stairs look (§5.3, the user's photos): the stair cores' flights, and the atrium's curving
// staircase.
const STAIR_LOOKS = {
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

// The key cards' colours, shown on the readers beside locked doors (§6.2, proposed).
const CARD_COLOURS = { hotel: 0x2f9bd6, technical: 0xe04848, captain: 0xf2c14e };

// Each hazard gets its own fright (§5.6).
const FRIGHTS = { vacuum: 'Іііі!' };

export class ShipScene extends Phaser.Scene {
    constructor() {
        super('ship');
    }

    create() {
        this.save = loadSave();
        this.controls = new Controls(this);
        this.worldLayer = this.add.layer();
        this.uiLayer = this.add.layer();

        this.buildMap();
        this.buildObjects();
        this.buildPlayer();
        this.buildCameras();
        this.buildHud();

        this.mode = 'play'; // play | ladder | stairs | trunk | lift | swim | scripted
        this.dashUntil = 0;
        this.bubbleUntil = 0;
        this.lastTrailAt = 0;
        this.jumpBufferedAt = -Infinity;
        this.script = null;

        this.spawnAt(this.initialSpawn());
        window.__ship = this; // handle for headless tests and the console
    }

    // --- Building --------------------------------------------------------------------------

    buildMap() {
        const map = this.make.tilemap({ key: 'ship' });
        this.map = map;
        const props = Array.isArray(map.properties)
            ? Object.fromEntries(map.properties.map(p => [p.name, p.value]))
            : map.properties || {};
        this.deckPitch = props.deckPitch;
        this.hullMinX = props.hullMinX;
        this.hullMaxX = props.hullMaxX;
        this.waterY = props.waterY;

        const W = map.widthInPixels;
        const H = map.heightInPixels;
        const tiles = map.addTilesetImage('placeholder', 'tiles');

        const sky = this.add.image(0, 0, 'sky').setOrigin(0).setDisplaySize(W, this.waterY).setDepth(DEPTH.sky);
        this.sea = this.add.tileSprite(0, this.waterY, W, H - this.waterY, 'sea').setOrigin(0).setDepth(DEPTH.sea);
        const back = map.createLayer('background', tiles).setDepth(DEPTH.back);
        this.solidLayer = map.createLayer('solid', tiles).setDepth(DEPTH.solid);
        this.ladderLayer = map.createLayer('ladders', tiles).setDepth(DEPTH.ladders);

        this.solidLayer.setCollisionByExclusion([-1]);
        // A ladder's top is a one-way floor: solid to stand on, open to climb through.
        this.solidLayer.forEachTile(t => {
            if (t.index === LADDER_TOP) t.setCollision(false, false, true, false);
        });

        this.worldLayer.add([sky, this.sea, back, this.solidLayer, this.ladderLayer]);
    }

    buildObjects() {
        const prop = (o, name, fallback) => (o.properties || []).find(p => p.name === name)?.value ?? fallback;
        this.checkpoints = [];
        this.tangerines = [];
        this.flights = [];
        this.vacuums = [];
        this.cats = [];
        this.places = {};
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
        this.worldLayer.add([decorGfx, ...Object.values(stairsGfx)]);

        const objects = this.map.getObjectLayer('objects').objects;
        // Trunk doors take the place of any cabin door drawn where they stand.
        this.trunkDoorSpots = objects.filter(o => o.type === 'trunk')
            .flatMap(o => String(prop(o, 'floors', '')).split(',').map(y => ({ x: o.x, y: Number(y) })));

        for (const o of objects) {
            switch (o.type) {
                case 'spawn':
                    this.spawnPoint = { id: 'spawn', x: o.x, y: o.y };
                    break;

                case 'place':
                    this.places[o.name] = { id: o.name, x: o.x, y: o.y };
                    break;

                case 'checkpoint': {
                    const door = this.add.image(o.x, o.y, 'shipart', 'door-crew').setOrigin(0.5, 1).setDepth(DEPTH.props);
                    const glow = this.add.image(o.x, o.y - LAMP_RISE, 'glow').setDepth(DEPTH.props).setVisible(false);
                    const lamp = this.add.image(o.x, o.y - LAMP_RISE, 'lamp').setDepth(DEPTH.props);
                    this.worldLayer.add([door, glow, lamp]);
                    const cp = { id: o.name, x: o.x, y: o.y, door, lamp, glow, active: false };
                    this.checkpoints.push(cp);
                    if (this.save.activated.includes(o.name)) this.lightCheckpoint(cp, false);
                    break;
                }

                case 'tangerine': {
                    if (this.save.collected.includes(o.name)) break;
                    // Everything rests on something (§6.3): here, a small side table.
                    const table = this.add.image(o.x, o.y, 'sidetable').setOrigin(0.5, 1).setDepth(DEPTH.decor);
                    const sprite = this.add.image(o.x, o.y - table.height, 'tangerine').setOrigin(0.5, 1).setDepth(DEPTH.props);
                    const glint = this.add.image(sprite.x + 2, sprite.y - 6, 'dot').setDepth(DEPTH.props).setAlpha(0);
                    this.tweens.add({ targets: glint, alpha: 1, duration: 120, yoyo: true, repeat: -1, repeatDelay: 2400, delay: Phaser.Math.Between(0, 2000) });
                    this.worldLayer.add([table, sprite, glint]);
                    this.tangerines.push({ id: o.name, sprite, glint });
                    break;
                }

                case 'stairs': {
                    const [a, b] = o.polyline.map(p => ({ x: o.x + p.x, y: o.y + p.y }));
                    const [bottom, top] = a.y > b.y ? [a, b] : [b, a];
                    const flight = {
                        name: o.name, bottom, top, card: prop(o, 'card', null),
                        curve: prop(o, 'curve', false), front: prop(o, 'front', false),
                    };
                    flight.length = this.flightLength(flight);
                    this.flights.push(flight);
                    if (flight.front) this.drawStairs(stairsGfx.front, stairsGfx.frontRail, flight);
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
                    const sprite = this.add.image(o.x, o.y, 'vacuum').setOrigin(0.5, 1).setDepth(DEPTH.props);
                    this.worldLayer.add(sprite);
                    this.vacuums.push({
                        sprite, alive: true, dir: 1,
                        minX: prop(o, 'minX', o.x - 80), maxX: prop(o, 'maxX', o.x + 80), speed: prop(o, 'speed', 40),
                    });
                    break;
                }

                case 'bumbot': {
                    const activity = prop(o, 'activity', 'wash');
                    const sprite = this.add.sprite(o.x, o.y, 'bumbot').setOrigin(0.5, 1).setDepth(DEPTH.props);
                    if (activity === 'asleep') {
                        // One still pose that breathes, slowly.
                        sprite.setFrame(this.cache.json.get('bumbot-meta').frames.asleep);
                        this.tweens.add({ targets: sprite, scaleY: 1.06, duration: 1400, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
                    } else {
                        sprite.play(`bumbot-${activity}`);
                    }
                    this.worldLayer.add(sprite);
                    this.cats.push({ name: o.name, sprite, escape: prop(o, 'escape', 1), gone: false });
                    break;
                }

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
                    this.buildPool(o);
                    break;

                case 'lift':
                    this.buildLift(o, prop(o, 'floors', ''), prop(o, 'decks', ''), prop(o, 'cards', ''), prop(o, 'glass', false));
                    break;

                case 'prop': {
                    // Furniture and fittings (§5.3): on the floor, on another piece, or on the wall.
                    const piece = this.add.image(o.x, o.y - prop(o, 'dy', 0), 'shipart', prop(o, 'frame', ''))
                        .setOrigin(0.5, 1).setDepth(DEPTH.decor + 0.1).setFlipX(prop(o, 'flip', false));
                    this.worldLayer.add(piece);
                    break;
                }

                case 'sign': {
                    const text = this.add.text(o.x, o.y, prop(o, 'text', ''), {
                        fontFamily: 'Verdana, sans-serif', fontSize: '7px', color: '#8f846f',
                        backgroundColor: '#f3ecdd', padding: { x: 3, y: 2 }, resolution: 4,
                    }).setOrigin(0.5).setDepth(DEPTH.decor);
                    this.worldLayer.add(text);
                    break;
                }

                case 'decor':
                    if (prop(o, 'kind') === 'shelldoor') this.drawShellDoor(decorGfx, o);
                    if (prop(o, 'kind') === 'cabindoors') this.drawCabinDoors(decorGfx, o);
                    break;
            }
        }
    }

    // A point along a flight, t from 0 (its foot) to 1 (its top). The atrium's curving staircase
    // (§5.3) sweeps: shallow at its foot, steeper toward the top; the cores' flights are straight.
    stairPoint(f, t) {
        const { bottom: a, top: b } = f;
        if (!f.curve) return { x: Phaser.Math.Linear(a.x, b.x, t), y: Phaser.Math.Linear(a.y, b.y, t) };
        const c = { x: a.x + (b.x - a.x) * 0.6, y: a.y - (a.y - b.y) * 0.35 }; // about 28° at the foot, 56° at the top
        const u = 1 - t;
        return { x: u * u * a.x + 2 * u * t * c.x + t * t * b.x, y: u * u * a.y + 2 * u * t * c.y + t * t * b.y };
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
        const look = f.curve ? STAIR_LOOKS.atrium : STAIR_LOOKS.core;
        const steps = Math.max(2, Math.round((f.bottom.y - f.top.y) / 8));
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
    drawCabinDoors(g, o) {
        const ceiling = o.y - this.deckPitch + 16;
        g.fillStyle(0xf6f3ec, 1);
        g.fillRect(o.x, ceiling, o.width, 3);
        g.fillStyle(0xd8b29a, 1);
        g.fillRect(o.x, o.y - 33, o.width, 2);     // the handrail, at about her hip
        g.fillStyle(0xc49a80, 1);
        g.fillRect(o.x, o.y - 31, o.width, 1);

        const pictures = ['picture-sea-bg', 'picture-ship-bg', 'picture-art-bg'];
        const parts = [];
        for (let x = o.x + 60, n = Math.round(o.x / 192); x + 30 < o.x + o.width; x += 192, n++) {
            const gap = x + 15 + 96;                 // halfway to the next door
            g.fillStyle(0xfffbe8, 1);
            g.fillEllipse(gap, ceiling + 3, 8, 3);
            if (n % 3 === 1 && gap + 20 < o.x + o.width) {
                parts.push(this.add.image(gap, o.y - 50, 'shipart', pictures[n % pictures.length]).setDepth(DEPTH.decor + 0.1));
            }
            if (this.trunkDoorSpots.some(t => t.y === o.y && x < t.x + 22 && x + 30 > t.x - 22)) continue;
            // Most doors are plain; about one in six has stickers, each its own.
            const frame = (n * 7) % 6 === 0 ? `door-cabin-stickers-${1 + (n % 3)}-bg` : 'door-cabin-bg';
            parts.push(this.add.image(x, o.y, 'shipart', frame).setOrigin(0, 1).setDepth(DEPTH.decor + 0.1));
        }
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

    // The atrium (§5.3): open from its floor on deck 5 up to a skylight under deck 10, its decks
    // crossing it on side walks. Behind them, burl-wood pillars with a brass ring at each level.
    buildAtrium(o, levels) {
        const x0 = o.x;
        const x1 = o.x + o.width;
        const top = o.y;
        const bottom = o.y + o.height;
        const g = this.add.graphics().setDepth(DEPTH.decor);
        this.worldLayer.add(g);
        // The skylight dome (the user's photo central_area (2)), seen from below: a shallow bowl of
        // glass right under deck 10's floor, ribbed in white, edged in brass.
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

        // The walkway: its floor on top, its front with an edge, a light under it.
        back.fillStyle(look.front, 1).fillRect(x0, y, x1 - x0, 12);
        back.fillStyle(look.floor, 1).fillRect(x0, y, x1 - x0, 3);
        for (let px = x0 + 2; px < x1; px += 6) back.fillStyle(look.fleck, 1).fillRect(px, y + 1, 2, 1);
        back.fillStyle(look.edge, 1).fillRect(x0, y + 3, x1 - x0, 1);
        if (look.light) back.fillStyle(look.light, 1).fillRect(x0, y + 12, x1 - x0, 2);
        // The railing in front of it: glass panels between posts, a handrail along the top.
        const railTop = y - SIDEWALK.railHeight;
        front.fillStyle(0x8fd3ff, 0.22).fillRect(x0, railTop, x1 - x0, SIDEWALK.railHeight);
        front.fillStyle(look.rail, 1).fillRect(x0, railTop, x1 - x0, 2);
        for (let px = x0; px <= x1; px += 40) front.fillStyle(look.post, 1).fillRect(px, railTop, 1, SIDEWALK.railHeight);

        // The walkway itself: floor from above.
        const walk = { x0, x1, y, dropThrough };
        walk.zone = this.add.zone(x0, y, x1 - x0, 6).setOrigin(0);
        walk.zone.walk = walk;
        this.physics.add.existing(walk.zone, true);
        this.walkGroup.add(walk.zone);
        this.walks.push(walk);
    }

    // A pool on deck 11 (§5.3): water she can jump into and swim in. Its front is drawn over her,
    // a little see-through, so she is in it rather than on it.
    buildPool(o) {
        const water = this.add.graphics().setDepth(DEPTH.player + 0.4);
        water.fillStyle(0x4d9be6, 0.55).fillRect(o.x, o.y, o.width, o.height);
        water.fillStyle(0x8fd3ff, 0.9).fillRect(o.x, o.y, o.width, 1);
        const ripples = this.add.tileSprite(o.x, o.y + 1, o.width, 2, 'sea').setOrigin(0).setAlpha(0.5).setDepth(DEPTH.player + 0.45);
        this.worldLayer.add([water, ripples]);
        this.pools.push({ x0: o.x, x1: o.x + o.width, y: o.y, bottom: o.y + o.height, ripples });
    }

    // An elevator (§5.1). A core one has landing doors on every deck and a car that travels out of
    // sight; the atrium's glass one is a single car, seen on its rails. Floors run top to bottom.
    buildLift(o, floors, decks, cards, glass) {
        const ys = String(floors).split(',').map(Number);
        const ds = String(decks).split(',').map(Number);
        const cs = String(cards).split(',');
        const lift = {
            id: o.name, x: o.x, glass,
            floors: ys.map((y, i) => ({ y, deck: ds[i], card: cs[i] })),
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
        this.climbOutFrames = meta.anims['climb-out'];
        this.idleAt = 0;
        const p = this.physics.add.sprite(0, 0, 'her', this.herFrames.stand).setOrigin(0.5, 1).setDepth(DEPTH.player);
        p.body.setSize(PLAYER.bodyWidth, PLAYER.bodyHeight);
        p.body.setOffset((PLAYER.cell - PLAYER.bodyWidth) / 2, PLAYER.cell - PLAYER.bodyHeight);
        p.body.setMaxVelocity(10000, PLAYER.maxFall);
        this.worldLayer.add(p);
        this.player = p;

        this.physics.add.collider(p, this.solidLayer);
        // A side walk holds her coming down onto it, unless she is dropping through it.
        this.droppingThrough = null;
        this.physics.add.collider(p, this.walkGroup, null, (_, zone) =>
            this.droppingThrough !== zone.walk && p.body.velocity.y >= 0 && p.body.bottom <= zone.body.top + 10);
        this.physics.add.collider(p, this.crates, null, (_, crate) => {
            if (!this.isDashing()) return true;
            this.smash(crate.x, crate.y);
            this.save.broken.push(crate.name);
            crate.disableBody(true, true);
            return false;
        });
    }

    buildCameras() {
        const cam = this.cameras.main;
        cam.setZoom(VIEW.zoom);
        cam.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels);
        cam.setDeadzone(40, 24);
        cam.ignore(this.uiLayer);

        // The HUD gets its own unzoomed camera, so its text stays crisp.
        this.uiCam = this.cameras.add(0, 0, VIEW.width, VIEW.height);
        this.uiCam.ignore(this.worldLayer);
    }

    buildHud() {
        const textStyle = {
            fontFamily: 'Verdana, sans-serif', fontSize: '24px', color: '#ffffff',
            stroke: '#1d2b53', strokeThickness: 5,
        };
        const icon = this.add.image(24, 20, 'tangerine').setOrigin(0).setScale(4);
        this.hudCount = this.add.text(62, 22, '', textStyle);
        this.dashBarBack = this.add.rectangle(24, 62, 164, 12, 0x1d2b53).setOrigin(0);
        this.dashBar = this.add.rectangle(26, 64, 160, 8, 0xf28c28).setOrigin(0);
        this.bubble = this.add.text(0, 0, DASH.shout, {
            fontFamily: 'Verdana, sans-serif', fontSize: '22px', fontStyle: 'bold', color: '#c8343f',
            backgroundColor: '#ffffff', padding: { x: 10, y: 6 },
        }).setOrigin(0.5, 1);
        this.alert = this.add.text(0, 0, '', {
            fontFamily: 'Verdana, sans-serif', fontSize: '22px', fontStyle: 'bold', color: '#1d2b53',
            backgroundColor: '#ffffff', padding: { x: 8, y: 4 },
        }).setOrigin(0.5, 1).setVisible(false);
        this.fade = this.add.rectangle(0, 0, VIEW.width, VIEW.height, 0x0d1422).setOrigin(0).setAlpha(0);
        this.debugText = this.add.text(VIEW.width - 12, 12, '', { fontFamily: 'monospace', fontSize: '14px', color: '#ffffff' })
            .setOrigin(1, 0).setVisible(new URLSearchParams(location.search).has('debug'));
        this.uiLayer.add([icon, this.hudCount, this.dashBarBack, this.dashBar, this.bubble, this.alert, this.fade, this.debugText]);
        this.refreshHud();
    }

    refreshHud() {
        this.hudCount.setText(`× ${this.save.tangerines}`);
        const left = Math.max(0, this.dashUntil - this.time.now);
        const dashing = left > 0;
        this.dashBarBack.setVisible(dashing);
        this.dashBar.setVisible(dashing).setSize(160 * (left / DASH.durationMs), 8);
    }

    // --- Spawning --------------------------------------------------------------------------

    // ?at=<place> starts her at a named place, for testing (README); otherwise her last checkpoint.
    initialSpawn() {
        const at = this.places[new URLSearchParams(location.search).get('at')];
        return at || this.checkpoints.find(c => c.active && c.id === this.save.lastCheckpoint) || this.spawnPoint;
    }

    // She always comes back at the activated checkpoint closest to where she was: same deck
    // first, then the nearest deck, then the nearest along the deck (§5.5).
    closestCheckpoint(x, y) {
        let best = null;
        let bestScore = Infinity;
        for (const c of this.checkpoints) {
            if (!c.active) continue;
            const score = Math.round(Math.abs(c.y - y) / this.deckPitch) * 1e6 + Math.abs(c.x - x);
            if (score < bestScore) {
                best = c;
                bestScore = score;
            }
        }
        return best || this.spawnPoint;
    }

    spawnAt(point, { emerge = false } = {}) {
        const p = this.player;
        p.clearAlpha().setCrop().setVisible(true).setDepth(DEPTH.player).setFlipX(false);
        this.inTrunk = null;
        this.liftRun = null;
        this.liftMove = null;
        this.hideLiftPanel();
        this.pose('stand');
        p.body.enable = true;
        p.body.reset(point.x, point.y);
        p.body.allowGravity = true;
        this.grounded = true;
        this.takeoffY = point.y;
        this.lastGroundedAt = this.time.now;
        this.alert.setVisible(false);

        const cam = this.cameras.main;
        cam.startFollow(p, true, 0.15, 0.15);
        cam.setFollowOffset(0, HALF);
        cam.centerOn(p.x, p.y - HALF);

        if (!emerge) {
            this.mode = 'play';
            return;
        }
        // Stepping out of the crew cabin door.
        this.mode = 'scripted';
        sfx.door();
        p.setAlpha(0);
        if (point.door) {
            point.door.setAlpha(0.5);
            this.tweens.add({ targets: point.door, alpha: 1, duration: 400 });
        }
        this.tweens.add({ targets: p, alpha: 1, duration: 350, onComplete: () => { this.mode = 'play'; } });
    }

    // --- Main loop -------------------------------------------------------------------------

    update(time, delta) {
        const dt = Math.min(delta, 50) / 1000;
        const input = this.controls.update();
        this.sea.tilePositionX += dt * 12; // the ship is under way (§5.2)

        this.updateVacuums(dt);
        if (this.mode === 'play') this.updatePlay(input, dt, time);
        else if (this.mode === 'ladder') this.updateLadder(input, dt, time);
        else if (this.mode === 'stairs') this.updateStairs(input, dt, time);
        else if (this.mode === 'trunk') this.updateTrunk(input, dt);
        else if (this.mode === 'lift') this.updateLift(input, dt);
        else if (this.mode === 'swim') this.updateSwim(input, dt);
        else if (this.script) this.script(dt, time);
        for (const pool of this.pools) pool.ripples.tilePositionX += dt * 6;
        this.closeTrunkDoors();
        this.closeLiftDoors();

        // Inside a trunk or an elevator she is out of everyone's way.
        if (this.mode === 'play' || this.mode === 'ladder' || this.mode === 'stairs') {
            this.checkPickups();
            this.checkCheckpoints();
            this.checkVacuums();
            this.checkBumbot();
        }
        this.updateDash(time);
        this.updateOverlays();
    }

    updatePlay(input, dt, time) {
        const p = this.player;
        const body = p.body;
        const onFloor = body.blocked.down || body.touching.down;

        if (onFloor) {
            if (!this.grounded) sfx.land();
            this.grounded = true;
            this.lastGroundedAt = time;
            this.takeoffY = p.y;
        } else {
            this.grounded = false;
        }

        if (onFloor && input.activatePressed && this.callLift()) return;
        if (onFloor && input.activatePressed) this.activateTrunkDoor();
        if (onFloor && (input.up || input.down) && this.tryTrunk(input)) return;
        // Held, not just pressed, so holding ↓ carries her on down the next flight at a landing.
        if (onFloor && (input.up || input.down) && this.tryStairs(input)) return;
        if ((input.up || input.down) && this.tryLadder(input)) return;
        if (onFloor && input.downPressed) this.dropThroughWalk();

        if (input.dashPressed) this.tryDash(time);

        const dashing = this.isDashing();
        const speed = PLAYER.runSpeed * (dashing ? DASH.speedMultiplier : 1);
        const dir = (input.right ? 1 : 0) - (input.left ? 1 : 0);
        const accel = (onFloor ? (dir ? PLAYER.groundAccel : PLAYER.groundDecel) : PLAYER.airAccel) * (dashing ? 2 : 1);
        body.velocity.x = approach(body.velocity.x, dir * speed, accel * dt);
        if (dir) p.setFlipX(dir < 0);

        if (input.jumpPressed) this.jumpBufferedAt = time;
        const canJump = onFloor || time - this.lastGroundedAt < PLAYER.coyoteMs;
        if (canJump && time - this.jumpBufferedAt < PLAYER.jumpBufferMs) {
            body.velocity.y = -PLAYER.jumpVelocity;
            this.jumpBufferedAt = -Infinity;
            this.lastGroundedAt = -Infinity;
            sfx.jump();
        }
        if (input.jumpReleased && body.velocity.y < -PLAYER.jumpCutVelocity) {
            body.velocity.y = -PLAYER.jumpCutVelocity;
        }

        const pool = this.pools.find(w => p.x > w.x0 && p.x < w.x1 && p.y > w.y + SWIM.entry && p.y < w.bottom + 16);
        if (pool) return this.enterPool(pool);

        if (!onFloor) {
            if (p.x < this.hullMinX || p.x > this.hullMaxX) {
                if (p.y >= this.waterY) return this.scareOverboard();
            } else if (p.y - this.takeoffY > this.deckPitch + LONG_FALL_MARGIN) {
                return this.scareFall();
            }
        }

        if (!onFloor) this.pose(body.velocity.y < -60 ? 'rise' : body.velocity.y < 60 ? 'apex' : 'fall');
        else if (Math.abs(body.velocity.x) > 10) this.pose('run', dashing ? 1.8 : Math.abs(body.velocity.x) / PLAYER.runSpeed);
        else this.standStill(time, dir);
    }

    // Standing still is her plain side pose; after a while one of her idles plays once (§3).
    standStill(time, dir) {
        const p = this.player;
        if (this.idle) {
            if (p.anims.isPlaying && !dir) return;
            this.idle = null;
            this.idleAt = time + Phaser.Math.Between(IDLE.gapMs[0], IDLE.gapMs[1]);
        }
        if (dir || time < this.idleAt) {
            if (dir) this.idleAt = Math.max(this.idleAt, time + IDLE.firstMs);
            this.pose('stand');
            return;
        }
        // Never the same one twice in a row.
        const choices = IDLE.anims.filter(name => name !== this.lastIdle);
        this.idle = this.lastIdle = Phaser.Utils.Array.GetRandom(choices);
        p.anims.play(`her-${this.idle}`);
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

        // Her hands reach to about head height. Once that is above the last rung there is nothing
        // to grab, so her hands come down: climbing out of the hatch, or starting down into it.
        const handsAboveLadder = p.y - PLAYER.height * 0.85 < L.topY;
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
        if (input.jumpPressed) {
            this.leaveLadderOrStairs();
            p.body.velocity.y = -PLAYER.jumpVelocity * 0.6;
            sfx.jump();
        } else if ((atTop && input.up) || (atBottom && input.down) || ((atTop || atBottom) && (input.left || input.right))) {
            this.leaveLadderOrStairs();
        }
    }

    leaveLadderOrStairs() {
        const p = this.player;
        this.mode = 'play';
        p.setDepth(DEPTH.player);
        this.pose('stand');
        p.body.enable = true;
        p.body.reset(p.x, p.y);
        this.takeoffY = p.y;
    }

    // --- Pools (§5.3): she swims, breaststroke -------------------------------------------------

    enterPool(pool) {
        const p = this.player;
        this.mode = 'swim';
        this.pool = pool;
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.y = pool.y + SWIM.float;
        sfx.splash();
        this.splash(p.x, pool.y);
        this.pose('swim');
    }

    // ←/→ swims along the pool; jump climbs out, onto the deck at its edge or back in the water.
    updateSwim(input, dt) {
        const p = this.player;
        const pool = this.pool;
        const dir = (input.right ? 1 : 0) - (input.left ? 1 : 0);
        if (dir) p.setFlipX(dir < 0);
        p.x = Phaser.Math.Clamp(p.x + dir * SWIM.speed * dt, pool.x0 + SWIM.margin, pool.x1 - SWIM.margin);
        this.pose('swim', dir ? 1 : 0.4);
        if (input.jumpPressed) {
            this.mode = 'play';
            this.pool = null;
            p.y = pool.y - 2;
            p.body.enable = true;
            p.body.reset(p.x, p.y);
            p.body.velocity.y = -PLAYER.jumpVelocity;
            p.body.velocity.x = (p.flipX ? -1 : 1) * PLAYER.runSpeed * 0.6;
            this.takeoffY = pool.y;
            sfx.jump();
        }
    }

    // --- Side walks (§5.3) -----------------------------------------------------------------------

    // ↓ on deck 12's walk over the pools: she lets go over the railing and drops (into a pool, if
    // she is over one). Nowhere else: in the atrium ↓ only ever takes the stairs.
    dropThroughWalk() {
        const p = this.player;
        const walk = this.walks.find(w => w.dropThrough && p.x >= w.x0 && p.x <= w.x1 && Math.abs(p.y - w.y) < 2);
        if (!walk) return false;
        this.droppingThrough = walk;
        p.body.velocity.y = -PLAYER.jumpVelocity * 0.35;
        this.time.delayedCall(450, () => { if (this.droppingThrough === walk) this.droppingThrough = null; });
        return true;
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
        sfx.door();
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
                sfx.door();
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
            if (Math.abs(x - lift.x) > 14) continue;
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
        sfx.door();
        this.tweens.add({
            targets: leaves, open: to, duration: LIFT.doorMs * Math.abs(to - leaves.open),
            onUpdate: () => this.setLeaves(leaves, y, leaves.open),
            onComplete: () => { this.setLeaves(leaves, y, to); done?.(); },
        });
    }

    // E at the doors: they open and the button panel shows. The glass car, if it is on another
    // deck, comes to fetch her first.
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
        if (lift.at !== i && lift.glass) this.moveCar(lift, i, false, open);
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
            while (c >= 0 && c < floors.length && !this.hasCard(floors[c].card)) c += step;
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
                        sfx.ding();
                        this.slideLeaves(this.leavesAt(lift, cursor), lift.floors[cursor].y, 1, () => this.leaveLift());
                    });
                });
            },
        });
    }

    moveCar(lift, to, carriesHer, arrive) {
        if (lift.glass) this.setLeaves(lift.leaves, lift.carY, 0);
        this.liftMove = { lift, to, carriesHer, arrive };
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
            const ok = this.hasCard(lift.floors[i].card);
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
            if (input.up && Math.abs(p.x - f.bottom.x) < reach && Math.abs(p.y - f.bottom.y) < 4) {
                if (!this.hasCard(f.card)) return this.showLocked(f.card);
                return this.enterStairs(f, 0);
            }
            if (input.down && Math.abs(p.x - f.top.x) < reach && Math.abs(p.y - f.top.y) < 4) return this.enterStairs(f, 1);
        }
        return false;
    }

    // Her cards (§6.2): her own crew card from the start; ?cards=all unlocks everything for testing.
    hasCard(card) {
        return !card || this.save.cards.includes(card) || new URLSearchParams(location.search).get('cards') === 'all';
    }

    // A flight up that her cards don't open: the card it needs shows above her for a moment.
    showLocked(card) {
        if (this.time.now < (this.lockedUntil || 0)) return false;
        this.lockedUntil = this.time.now + 900;
        this.alert.setText(`🔒 ${card[0].toUpperCase()}${card.slice(1)} card`).setVisible(true);
        // Held at the lock, it shows again before this runs: hide it only once the last one is over.
        this.time.delayedCall(900, () => { if (this.mode === 'play' && this.time.now >= this.lockedUntil) this.alert.setVisible(false); });
        return false;
    }

    enterStairs(flight, t) {
        this.mode = 'stairs';
        this.flight = flight;
        this.stairT = t;
        this.player.body.enable = false;
        this.player.setDepth(flight.front ? DEPTH.onFrontStairs : DEPTH.playerBehind);
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
        const key = `her-${name}`;
        if (this.anims.exists(key)) {
            p.anims.play(key, true);
            p.anims.timeScale = speed;
        } else {
            p.anims.stop();
            p.setFrame(this.herFrames[name]);
        }
    }

    // --- Pickups, checkpoints, hazards ---------------------------------------------------------

    checkPickups() {
        const p = this.player;
        for (const t of this.tangerines) {
            if (!t.sprite.active) continue;
            if (Math.abs(p.x - t.sprite.x) < 12 && t.sprite.y > p.y - PLAYER.height && t.sprite.y - 8 < p.y) {
                this.save.tangerines += 1;
                this.save.collected.push(t.id);
                sfx.pickup();
                t.glint.destroy();
                this.tweens.add({ targets: t.sprite, y: t.sprite.y - 12, alpha: 0, duration: 250, onComplete: () => t.sprite.destroy() });
                t.sprite.active = false;
                this.refreshHud();
            }
        }
    }

    checkCheckpoints() {
        const p = this.player;
        for (const c of this.checkpoints) {
            if (Math.abs(p.x - c.x) > 8 || Math.abs(p.y - c.y) > 6) continue;
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

    // An active checkpoint has to read from across the deck: the door stands ajar with the cabin
    // light on, and a green lamp above it glows.
    lightCheckpoint(c, celebrate) {
        c.active = true;
        c.door.setTexture('shipart', 'door-crew-ajar');
        c.lamp.setTexture('lamp-on');
        c.glow.setVisible(true).setAlpha(0.55);
        this.tweens.add({ targets: c.glow, alpha: 0.25, scale: 0.8, duration: 1100, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        if (!celebrate) return;
        sfx.checkpoint();
        this.tweens.add({ targets: c.lamp, scale: 1.8, duration: 160, yoyo: true, ease: 'Quad.easeOut' });
        for (let i = 0; i < 14; i++) {
            const angle = (Math.PI * 2 * i) / 14;
            const spark = this.add.image(c.x, c.y - LAMP_RISE, 'dot').setTint(0x7dffa0).setDepth(DEPTH.fx);
            this.worldLayer.add(spark);
            this.tweens.add({
                targets: spark, x: c.x + Math.cos(angle) * 22, y: c.y - LAMP_RISE + Math.sin(angle) * 22, alpha: 0,
                duration: 500, ease: 'Quad.easeOut', onComplete: () => spark.destroy(),
            });
        }
    }

    updateVacuums(dt) {
        for (const v of this.vacuums) {
            if (!v.alive) continue;
            v.sprite.x += v.dir * v.speed * dt;
            if (v.sprite.x > v.maxX) v.dir = -1;
            else if (v.sprite.x < v.minX) v.dir = 1;
            v.sprite.setFlipX(v.dir < 0);
        }
    }

    checkVacuums() {
        const p = this.player;
        for (const v of this.vacuums) {
            if (!v.alive) continue;
            const s = v.sprite;
            const hit = Math.abs(p.x - s.x) < (PLAYER.bodyWidth / 2 + 6) && p.y > s.y - 6 && p.y - PLAYER.bodyHeight < s.y;
            if (!hit) continue;
            if (this.isDashing()) {
                v.alive = false;
                this.smash(s.x, s.y - 3);
                s.destroy();
            } else {
                this.scareContact(s.x, 'vacuum');
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
            if (cat.gone || Math.abs(p.y - s.y) > 8 || Math.abs(p.x - s.x) > BUMBOT.noticeReach) continue;
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
        };

        // Up to arm's length from him, at a walk.
        const stopX = s.x - toward * BUMBOT.reachGap;
        const walkMs = Math.max(0, (Math.abs(stopX - p.x) / (PLAYER.runSpeed * 0.6)) * 1000);
        this.pose('run', 0.6);
        this.tweens.add({
            targets: p, x: stopX, duration: walkMs,
            onComplete: () => {
                p.anims.play('her-reach');
                // He hears her a beat before her hands arrive: a startled leap, then gone.
                this.time.delayedCall(BUMBOT.startleMs, () => {
                    this.tweens.killTweensOf(s);
                    s.setScale(1).setFlipX(cat.escape < 0).play('bumbot-jump');
                    this.time.delayedCall(BUMBOT.leapMs, () => {
                        sfx.mrrp();
                        s.play('bumbot-run');
                        this.script = (dt) => {
                            s.x += cat.escape * BUMBOT.runSpeed * dt;
                            const view = this.cameras.main.worldView;
                            if (s.x < view.x - 40 || s.x > view.right + 40) {
                                s.setVisible(false).stop();
                                this.script = null;
                                catAway = true;
                                finish();
                            }
                        };
                    });
                });
                // Left reaching at nothing for a moment, then she straightens up and turns to us.
                p.once('animationcomplete-her-reach', () => {
                    this.time.delayedCall(BUMBOT.holdMs, () => {
                        p.anims.play('her-straighten');
                        p.once('animationcomplete-her-straighten', () => {
                            this.pose('front');
                            this.time.delayedCall(BUMBOT.frontMs, () => { herDone = true; finish(); });
                        });
                    });
                });
            },
        });
    }

    smash(x, y) {
        sfx.smash();
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

    // --- The dash --------------------------------------------------------------------------

    isDashing() {
        return this.dashUntil > this.time.now;
    }

    tryDash(time) {
        if (this.isDashing() || this.save.tangerines <= 0) return;
        this.save.tangerines -= 1;
        this.dashUntil = time + DASH.durationMs;
        this.bubbleUntil = time + DASH.bubbleMs;
        sfx.dash();
        this.refreshHud();
    }

    updateDash(time) {
        const dashing = this.isDashing();
        if (this.wasDashing && !dashing) sfx.dashEnd();
        this.wasDashing = dashing;
        if (dashing || this.dashBar.visible) this.refreshHud();

        if (dashing && this.mode === 'play' && time - this.lastTrailAt > 45 && Math.abs(this.player.body.velocity.x) > 10) {
            this.lastTrailAt = time;
            const p = this.player;
            const ghost = this.add.image(p.x, p.y, 'her', p.frame.name).setOrigin(0.5, 1)
                .setFlipX(p.flipX).setAlpha(0.45).setDepth(DEPTH.player - 0.5);
            this.worldLayer.add(ghost);
            this.tweens.add({ targets: ghost, alpha: 0, duration: 260, onComplete: () => ghost.destroy() });
        }
    }

    // --- Scares (never death, §5.6) ------------------------------------------------------------

    beginScare() {
        this.mode = 'scripted';
        this.dashUntil = 0;
        this.bubbleUntil = 0;
        this.player.body.enable = false;
        this.cameras.main.stopFollow();
    }

    // A fright that fits what got her, then she runs off the screen.
    scareContact(fromX, kind) {
        const p = this.player;
        this.beginScare();
        this.scareFrom = { x: p.x, y: p.y };
        const away = p.x >= fromX ? 1 : -1;
        sfx.scare();
        this.alert.setText(FRIGHTS[kind] || '!').setVisible(true);
        this.pose('rise');
        p.setFlipX(away < 0);
        this.script = null;
        this.tweens.add({
            targets: p, y: p.y - 14, duration: 170, yoyo: true, ease: 'Quad.easeOut',
            onComplete: () => {
                sfx.whoosh();
                this.script = (dt, time) => {
                    p.x += away * 260 * dt;
                    this.pose('run', 2);
                    const view = this.cameras.main.worldView;
                    if (p.x < view.x - 20 || p.x > view.right + 20) this.respawn();
                };
            },
        });
    }

    // Longer than one deck: the camera lets go and she drops out of the bottom of the screen.
    scareFall() {
        const p = this.player;
        let vy = p.body.velocity.y;
        this.beginScare();
        this.scareFrom = { x: p.x, y: this.takeoffY };
        p.setDepth(DEPTH.fx);
        this.pose('fall');
        sfx.whoosh();
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

    respawn(cleanup) {
        if (this.respawning) return;
        this.respawning = true;
        this.script = null;
        const from = this.scareFrom || { x: this.player.x, y: this.player.y };
        const target = this.closestCheckpoint(from.x, from.y);
        this.tweens.add({
            targets: this.fade, alpha: 1, duration: 220,
            onComplete: () => {
                cleanup?.();
                this.tweens.killTweensOf(this.player);
                this.spawnAt(target, { emerge: true });
                this.tweens.add({ targets: this.fade, alpha: 0, duration: 260 });
                this.respawning = false;
            },
        });
    }

    // --- Screen-space overlays ------------------------------------------------------------------

    updateOverlays() {
        const cam = this.cameras.main;
        const p = this.player;
        const sx = (p.x - cam.worldView.x) * cam.zoom;
        const sy = (p.y - PLAYER.height - 6 - cam.worldView.y) * cam.zoom;
        this.bubble.setVisible(this.time.now < this.bubbleUntil).setPosition(sx, sy);
        this.alert.setPosition(sx, sy);
        if (this.debugText.visible) {
            this.debugText.setText(`${this.mode}  x ${p.x.toFixed(0)}  y ${p.y.toFixed(0)}  takeoff ${this.takeoffY?.toFixed(0)}`);
        }
    }
}
