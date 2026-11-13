// The plan's world (GAME_DESIGN.md §6.1, docs/population.md): what tools/population.py puts on the
// ship, read from maps/world.json: the rooms behind doors, the outside route (the promenade, the
// boat walkway, the balconies), the funnel's top, the duct, and every thing in place: checkpoints,
// tangerines, pickups, Bumbot's beats, switches, carts to push. The ship scene asks it what is at
// her feet (E, ladders, grips for a wall jump) and tells it what has happened (flags).

import { PLAYER } from '../config.js';
import { parseLock } from '../progression.js';
import { writeSave } from '../save.js';
import { sfx } from '../sfx.js';
import { People } from './people.js';
import { Carry } from './carry.js';
import { Story } from './story.js';
import { Library } from './library.js';
import { Robot, Gull, SwingLight, Spill, Darter, TowelStack, Sprinkler, SwingDoor, DndDoor } from './movers.js';

export const OUTSIDE = 'promenade';     // the outside route (deck 6's promenade came first)
const ROOM = { height: 128, stop: 20 };
const OK = { ok: true };

// How a bare room looks until it is drawn (tools/draw_rooms.py): wall, skirting, floor.
const LOOKS = {
    laundry: [0xdfe8e2, 0x9babb2, 0x92a984], store: [0xc9c2b0, 0x7f708a, 0x8e98a3], crewcabin: [0xe6dcc8, 0xab947a, 0x4d65b4],
    pantry: [0xd9dee0, 0x9babb2, 0x8e98a3], galley: [0xeef2f2, 0x9babb2, 0xc7dcd0], nook: [0x6e4a3a, 0x45293f, 0xae2334],
    dressing: [0xe8c4c0, 0xab6f7a, 0x7f708a], lighting: [0x2e222f, 0x45293f, 0x3e3546], lifeboat: [0xf28c28, 0xcd683d, 0x9babb2],
    cabin: [0xefe6d2, 0xd8b29a, 0x4d65b4], balcabin: [0xefe6d2, 0xd8b29a, 0x4d65b4], adjoin: [0xefe6d2, 0xd8b29a, 0x4d65b4],
    coldroom: [0xcfeaf5, 0x8fd3ff, 0x9babb2],
};
const DOOR_ART = { crew: 'door-crew', cabin: 'door-cabin', open: 'door-cabin-ajar', hatch: 'door-watertight' };
const BOOK_COLOURS = [0xae2334, 0x4d9be6, 0x1ebc73, 0xf9c22b, 0x905ea9, 0xf68181, 0x0b5e65, 0xcd683d, 0x323353, 0xe83b3b];
const HINTS = {
    dash: 'D: «Кісюнічка!!!»', crawl: '↓ then ← →: crawl', socks: 'Jump at a wall: kick off it', parasol: 'Hold jump in the air: glide',
};

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
        this.built = false;
    }

    get save() { return this.scene.save; }
    get progress() { return this.scene.progress; }

    // Doors on the cabin corridors that take a cabin door's place (rooms, checkpoints).
    doorSpots() {
        const rooms = this.data.rooms.flatMap(r => r.doors.filter(d => d.outRoute === 'inside').map(d => ({ x: d.outX, y: d.outY })));
        // (And the doors that do something by themselves: the one that flies open, "Do Not Disturb".)
        const own = ['checkpoint', 'swingdoor', 'dnd'];
        const cps = this.data.ents.filter(e => own.includes(e.kind) && e.route === 'inside').map(e => ({ x: e.x, y: e.y }));
        return [...rooms, ...cps];
    }

    // --- Building -----------------------------------------------------------------------------

    build() {
        this.makeTextures();
        this.buildRooms();
        this.buildOutside();
        this.buildFunnel();
        this.buildDuct();
        for (const e of this.data.ents) this.buildEnt(e);
        this.library.build(this.data.library);
        this.buildSpecials();
        this.story.setup();
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
        BOOK_COLOURS.forEach((c, i) => make(`book-${i + 1}`, 10, 13, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 10, 13);
            g.fillStyle(c, 1).fillRect(1, 1, 8, 11);
            g.fillStyle(0xf3ecdd, 1).fillRect(8, 2, 1, 9).fillRect(3, 3, 4, 1);
        }));
        make('icon-socks', 12, 12, g => {
            g.fillStyle(0x2e222f, 1).fillRect(2, 0, 6, 9).fillRect(2, 7, 10, 5);
            g.fillStyle(0xf68181, 1).fillRect(3, 1, 4, 8).fillRect(3, 8, 8, 3);
            g.fillStyle(0xffffff, 1).fillRect(3, 1, 4, 2).fillRect(5, 9, 1, 1).fillRect(8, 9, 1, 1);
        });
        make('icon-pills', 8, 12, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 2, 8, 10).fillRect(1, 0, 6, 3);
            g.fillStyle(0xf9c22b, 1).fillRect(1, 3, 6, 8);
            g.fillStyle(0xffffff, 1).fillRect(2, 1, 4, 1).fillRect(2, 5, 4, 3);
        });
        make('icon-parasol', 14, 30, g => {
            g.fillStyle(0x2e222f, 1).fillRect(6, 0, 2, 30);
            g.fillStyle(0xe83b3b, 1).fillRect(4, 2, 6, 16);
            g.fillStyle(0xffffff, 1).fillRect(6, 2, 2, 16);
            g.fillStyle(0xab947a, 1).fillRect(5, 27, 4, 3);
        });
        make('parasol-open', 46, 40, g => {
            g.fillStyle(0x2e222f, 1).fillRect(22, 8, 2, 32);
            g.fillStyle(0xe83b3b, 1).fillEllipse(23, 12, 46, 22);
            g.fillStyle(0xffffff, 1).fillEllipse(23, 12, 14, 22).fillEllipse(8, 13, 6, 12).fillEllipse(38, 13, 6, 12);
            g.fillStyle(0x000000, 0).fillRect(0, 13, 46, 27);
        });
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
            const room = { id: def.id, route: def.id, door: def.doors[0].outX, floor: def.floor, room: img, dim, inDeck: true,
                           doors: def.doors, def, needs: def.needs, hidden: false, outside: [] };
            for (const d of def.doors) {
                d.lockSpec = parseLock(d.lock);
                const out = d.outRoute === OUTSIDE;
                const art = DOOR_ART[d.kind];
                if (art) {
                    const door = s.add.image(d.outX, d.outY, 'shipart', art).setOrigin(0.5, 1).setDepth(out ? D.exterior + 0.1 : D.props);
                    this.add([door]);
                    room.outside.push(door);
                    if (out) s.shellSlopes.push({ deck: [6, 7], gfx: door });
                }
                if (d.plate) {
                    const plate = s.add.text(d.outX + 20, d.outY - 50, d.plate, {
                        fontFamily: 'Verdana, sans-serif', fontSize: '5px', fontStyle: 'bold', color: '#3e3546',
                        backgroundColor: '#ffffff', padding: { left: 2, right: 2, top: 1, bottom: 1 }, resolution: 4,
                    }).setOrigin(0, 0.5).setDepth(D.props);
                    this.add([plate]);
                    room.outside.push(plate);
                }
                if (d.lockSpec?.kind === 'card') this.progress.reader(d.outX - 22, d.outY, d.lockSpec.card);
            }
            if (def.checkpoint) s.addCheckpoint(def.checkpoint, def.doors[0].outX, def.doors[0].outY, { door: null });
            s.rooms.push(room);
            s.addRouteWall(def.x0 + ROOM.stop, -1, def.floor, def.id);
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
            g.fillStyle(0xf4f4f4, 1).fillRect(gl.x0, gl.y - 8, gl.x1 - gl.x0, 8);
        }
        for (const [deck, g] of Object.entries(fronts)) {
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
            const lid = s.add.image(g.x, g.y0 + 16, 'hatch-lid').setOrigin(0.5, 0).setDepth(D.props);
            this.add([lid]);
            return { ...g, tiles, lid };
        });
    }

    cardColour(card) {
        return { deck: 0x4d9be6, ent: 0xe83b3b, hk: 0x1ebc73, off: 0xf9c22b }[card] ?? 0xffffff;
    }

    // A balcony's floor at her feet that she can drop through.
    dropFloorAt(x, y) {
        return this.platZones.find(z => z.plat.drop && x >= z.plat.x0 && x <= z.plat.x1 && Math.abs(y - z.plat.y) < 2)?.plat ?? null;
    }

    // ↑/↓ at a ladder between routes.
    tryLadder(input, onFloor) {
        const s = this.scene, p = s.player;
        if (this.carry || !onFloor) return false;
        for (const L of this.ladders) {
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
            return s.enterLadder(L.x, L.y1, L.y0);
        }
        return false;
    }

    // A ladder on the map she can't take now: a tray in her hands, or its hatch still shut.
    ladderShut(x, y) {
        if (this.carry) return true;
        return this.gates.some(g => Math.abs(x - g.x) < 9 && y >= g.y0 - 6 && y <= g.y1 + 6 && !this.progress.flagSet(g.needs));
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
            return { away: Math.abs(dx) < 3 ? 0 : Math.sign(dx) };
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
            for (let x = f.x0 + 14; x <= f.x1; x += 44) g.fillRect(Math.min(x, f.x1 - 2), top, 2, f.y - top);
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
        // The key at the way out.
        this.ductKey = this.glyph(d.exitX, d.floor - 40, '↓', D.exterior + 0.127);
        this.add([this.ductFan, this.ductEyes]);
    }

    // A key's cap bobbing over a spot: what to press here. Hidden until shown.
    glyph(x, y, text, depth) {
        const s = this.scene;
        const cap = s.add.text(x, y, text, {
            fontFamily: 'Verdana, sans-serif', fontSize: '7px', fontStyle: 'bold', color: '#2e222f', backgroundColor: '#ffffff',
            padding: { left: 3, right: 3, top: 1, bottom: 1 }, resolution: 4,
        }).setOrigin(0.5).setDepth(depth ?? s.DEPTH.fx + 0.4).setVisible(false);
        this.add([cap]);
        s.tweens.add({ targets: cap, y: y - 3, duration: 420, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        return cap;
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
                if (want && k.what === 'snore') sfx.rattle();
                if (want && k.what === 'balloons') sfx.ding();
            }
        }
        this.ductKey.setVisible(inDuct && s.mode === 'play' && Math.abs(p.x - d.exitX) < 60);
        const eyes = this.ductEyes;
        if (inDuct && !P.has('duct') && !this.eyesGone) {
            this.eyesX = Math.min(this.eyesX ?? p.x - 170, p.x - 150);
            if (this.eyesX <= d.exitX + 6) {
                this.eyesGone = true;
                eyes.setVisible(false);
                sfx.mrrp();
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
            sfx.smash();
            s.travel(d.dropX, d.floor + 30, 'inside', () => P.setFlag('duct'));
        }
    }

    // --- Things in place ------------------------------------------------------------------------

    buildEnt(e) {
        const s = this.scene, D = s.DEPTH;
        const depth = this.depthFor(e.route);
        switch (e.kind) {
            case 'checkpoint': {
                // The gangway's is lit from the start (population §2.5).
                if (e.id === 'cp_gangway' && !this.save.activated.includes(e.id)) this.save.activated.push(e.id);
                const cp = s.addCheckpoint(e.id, e.x, e.y, { route: e.route });
                if (e.route === OUTSIDE) cp.items.forEach(i => s.shellSlopes.push({ deck: [6, 7], gfx: i }));
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
                const img = s.add.image(e.x, y, key).setOrigin(0.5, 1).setDepth(depth + 0.01);
                items.push(img);
                this.add(items);
                const thing = { ...e, items, pick: img, interact: () => this.take(thing) };
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
                    sfx.checkpoint();
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
                this.add([img]);
                this.things.push({ ...e, items: [img], img });
                break;
            }
            case 'solid': {
                // Something standing in the way that she hops (a room-service cart).
                const img = s.add.image(e.x, e.y, 'shipart', e.frame).setOrigin(0.5, 1).setDepth(depth - 0.01).setFlipX(!!e.flip);
                const zone = s.add.zone(e.x, e.y, img.width - 6, img.height - 3).setOrigin(0.5, 1);
                s.physics.add.existing(zone, true);
                this.add([img]);
                const thing = { ...e, items: [img], zone };
                this.solids.push(thing);
                this.things.push(thing);
                break;
            }
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
                const zone = s.add.zone(e.x, e.y, w - 6, h - 3).setOrigin(0.5, 1);
                s.physics.add.existing(zone, true);
                this.add(items);
                const thing = { ...e, items, zone };
                this.breakables.push(thing);
                this.things.push(thing);
                break;
            }
            case 'source': {
                // A tray to take (population §1 `source`): it always has more.
                const items = [];
                if (e.show) {
                    this.carryBox.textures();
                    for (const [key, dy] of e.show) items.push(s.add.image(e.x, e.y - dy, key).setOrigin(0.5, 1).setDepth(depth + 0.03));
                    this.add(items);
                }
                this.things.push({ ...e, items, reach: 22, interact: () => {
                    if (this.carry) return false;
                    this.carryBox.take(e.gives);
                    return true;
                } });
                break;
            }
            case 'robot': {
                const robot = new Robot(this, e);
                this.movers.push(robot);
                this.robots = [...(this.robots ?? []), robot];
                break;
            }
            case 'gull':
                this.movers.push(new Gull(this, e));
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
            case 'low': {
                // Something she must crawl under or through (a blanket fort): solid above her on
                // hands and knees; its picture, if it has one, in front of her.
                const zone = s.add.zone(e.x, e.y - 30, e.x1 - e.x0, 98).setOrigin(0.5, 1);
                s.physics.add.existing(zone, true);
                this.low.push({ route: e.route, x0: e.x0 - 18, x1: e.x1 + 18, y: e.y });
                const items = e.frame ? [this.image(e.x, e.y, e.frame).setOrigin(0.5, 1).setDepth(D.player + 0.04)] : [];
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
                        sfx.ding();
                        for (let i = 0; i < 5; i++) {
                            this.sparkle(e.x + Phaser.Math.Between(-14, 14), e.y - 30 - i * 9, [0xfbff86, 0xe83b3b, 0xffffff][i % 3]);
                            await this.wait(140);
                        }
                        sfx.checkpoint();
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
                const img = s.add.image(e.x, e.y - (e.dy ?? 56), 'photo-frame').setDepth(depth + 0.01);
                this.add([img]);
                this.things.push({ ...e, items: [img], reach: 16, interact: () => {
                    this.cut(async () => {
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
                // A plate by a door, a poster, a notice.
                const style = {
                    plate: { color: '#45293f', backgroundColor: '#d9a43b' },
                    poster: { color: '#ae2334', backgroundColor: '#f3ecdd' },
                    note: { color: '#3e3546', backgroundColor: '#ffffff' },
                }[e.style ?? 'plate'];
                const text = s.add.text(e.x, e.y - (e.dy ?? 52), e.text, {
                    fontFamily: 'Verdana, sans-serif', fontSize: `${e.size ?? 5}px`, fontStyle: 'bold', align: 'center', ...style,
                    padding: { left: 2, right: 2, top: 1, bottom: 1 }, resolution: 4, wordWrap: e.wrap ? { width: e.wrap } : undefined,
                }).setOrigin(0.5).setDepth(e.route === OUTSIDE ? D.exterior + 0.09 : D.decor + 0.25);
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
                const thing = { ...e, x, items: [img], zone, width: img.width - 4, min: e.min, max: e.max, sides: e.sides ?? 0, top, rim,
                    moveTo: to => {
                        thing.x = img.x = zone.x = to;
                        if (to >= e.max && e.flag && !this.progress.has(e.flag)) {
                            // Free of the doorway: it stands in the corridor, low enough to hop.
                            zone.setSize(img.width - 4, rim);
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
        if (type === 'verb') return this.save.verbs.includes(name);
        if (type === 'book') return !!this.save.books[name];
        return this.save.items.includes(name) || this.save.seen.includes(e.id);
    }

    placeTangerine(e) {
        const s = this.scene, D = s.DEPTH;
        if (this.save.collected.includes(e.id)) return;
        let y = e.y;
        if (e.on === 'table') {
            if (e.first) {
                const out = e.route === OUTSIDE;
                const table = out ? s.add.image(e.x + 4, e.y, 'shipart', 'outdoor-table').setOrigin(0.5, 1).setDepth(D.exterior + 0.1)
                    : s.add.image(e.x + (e.id.includes('#') ? 4 : 0), e.y, 'sidetable').setOrigin(0.5, 1).setDepth(D.decor + 0.2);
                this.add([table]);
                if (out) this.things.push({ id: `${e.id}-table`, x: e.x, y: e.y, route: OUTSIDE, items: [table] });
            }
            y -= e.route === OUTSIDE ? 24 : 12;
        } else {
            y -= e.on;
        }
        s.addTangerine(e.id, e.x, y, e.route);
    }

    // E at a pickup: a verb (with its key glyph, shown once), a book, a pocket item.
    take(thing) {
        const s = this.scene;
        const [type, name] = thing.what.split(':');
        if (type === 'verb') {
            this.progress.learn(name);
            this.hint(HINTS[name]);
        } else if (type === 'book') {
            this.save.books[name] = 'held';
            this.sparkle(thing.x, thing.pick.y - 6, 0xf68181);
        } else {
            this.save.items.push(name);
        }
        thing.done = true;
        thing.pick.destroy();
        thing.items = thing.items.filter(i => i !== thing.pick);
        sfx.pickup();
        writeSave(this.save);
        this.refresh();
        return true;
    }

    // A book given to her (the honeymooners' thanks): hers to carry to the Library.
    giveBook(n) {
        this.save.books[n] = 'held';
        writeSave(this.save);
        this.refresh();
    }

    // A key glyph over her for a few seconds: how a new verb is used.
    hint(text) {
        const s = this.scene;
        if (!text) return;
        s.lockedUntil = s.time.now + 3200;
        s.alert.setText(text).setVisible(true);
        s.time.delayedCall(3200, () => { if (s.alert.text === text) s.alert.setVisible(false); });
    }

    // The scripted places that are not rooms: the pool's hatch, the stage's trap door, the linen
    // room's chute, the tip of the bow.
    buildSpecials() {
        const s = this.scene, D = s.DEPTH;
        const h = this.data.hatchPool;
        const lid = s.add.image(h.x, h.y + 32, 'hatch-lid').setOrigin(0.5, 1).setDepth(D.poolTank + 0.005);
        this.add([lid]);
        this.things.push({ id: 'hatch_pool', x: h.x, y: h.y + 32, route: 'inside', needs: 'drain', items: [lid], reach: 16,
            interact: () => { sfx.door(); s.travel(h.x, h.y + 32 + 16 + PLAYER.bodyHeight + 2, 'inside', null, 10); return true; } });
        const linen = this.rooms.linen;
        if (linen) {
            // The laundry chute's hatch, low in the wall by the door (drawn in the room's picture):
            // E, and down she goes to the laundry on deck 4 (population: `scn_chute`).
            this.things.push({ id: 'chute', x: this.data.linen.chuteX, y: linen.floor, route: 'linen', items: [], reach: 16,
                interact: () => this.story.chute() });
        }
    }

    updateSpecials(time) {
        const s = this.scene, p = s.player, P = this.progress;
        if (s.mode !== 'play') return;
        const onFloor = p.body.blocked.down || p.body.touching.down;
        // The stage's trap door (population: `haz_trapdoor`): after the rehearsal's beat, standing on
        // it drops her one deck into the galley; no scare.
        const t = this.data.trapdoor;
        if (s.route === 'inside' && onFloor && P.has('bb3') && Math.abs(p.x - t.x) < 10 && Math.abs(p.y - t.y) < 2) {
            const to = this.rooms[t.room];
            sfx.whoosh();
            s.travel(t.landX, to.floor - 80, t.room, () => P.setFlag('trapdoor'));
            return;
        }
        // The tip of the bow (§6.1.9): once he has run there, standing still, she has him.
        const c = this.data.catch;
        if (c && s.route === 'inside' && onFloor && P.has('alarm') && !P.has('catch') && Math.abs(p.y - c.y) < 2 && p.x < c.x) {
            if (Math.abs(p.body.velocity.x) > 5) this.stillAt = time;
            else if (time - (this.stillAt ?? time) > 3000) {
                P.setFlag('catch');
                this.hint('♥');
            }
        } else {
            this.stillAt = time;
        }
    }

    // --- What the story and the people use ------------------------------------------------------

    // A condition from the data: "flag:bb1", "region:2", "card:deck", "carry:lunch", "verb:dash",
    // "block:cleaner" (lifted), "broken:<id>"; "!" in front turns it round. What has really happened:
    // ?cards=all fakes none of it.
    cond(text) {
        if (!text) return true;
        if (text.startsWith('!')) return !this.cond(text.slice(1));
        const [kind, v] = text.split(':');
        const save = this.save;
        switch (kind) {
            case 'flag': return save.flags.includes(v);
            case 'region': return save.regions.includes(Number(v));
            case 'card': return save.cards.includes(v);
            case 'verb': return save.verbs.includes(v);
            case 'carry': return this.carry?.kind === v;
            case 'books': return v === 'held' ? this.library.held().length > 0 : this.library.returned().length === 10;
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
            camera: () => {
                g.fillStyle(ink, 1).fillRect(1, 4, 14, 10).fillRect(4, 2, 5, 3);
                g.fillStyle(0x625565, 1).fillRect(2, 5, 12, 8);
                g.fillStyle(ink, 1).fillCircle(8, 9, 4);
                g.fillStyle(0x8fd3ff, 1).fillCircle(8, 9, 3);
                g.fillStyle(0xffffff, 1).fillRect(7, 7, 1, 1).fillRect(12, 6, 2, 1);
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

    // A word over her for a moment (her own exclamations).
    say(text, ms = 900) {
        const s = this.scene;
        s.lockedUntil = s.time.now + ms;
        s.alert.setText(text).setVisible(true);
        s.time.delayedCall(ms, () => { if (s.alert.text === text) s.alert.setVisible(false); });
    }

    // Someone who wants something shows it again: their bubble hops.
    nudge(person) {
        const s = this.scene;
        if (!person.bubbleItems) return;
        s.tweens.add({ targets: person.bubbleItems, y: '-=5', duration: 110, yoyo: true, repeat: 1 });
    }

    // A scripted moment: her input is off while `fn` runs (an async function), then play goes on.
    cut(fn) {
        const s = this.scene, p = s.player;
        s.mode = 'scripted';
        s.script = null;
        p.body.setVelocity(0, 0);
        s.pose('stand');
        const done = () => {
            if (s.mode === 'scripted') s.mode = 'play';
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
        await this.tween({ targets: img, x: p.x, y: p.y - 40, duration: 420, ease: 'Sine.easeInOut' });
        sfx.checkpoint();
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
        sfx.smash();
    }

    // One of her quirks: she turns to the thing and does her bit; any key after a moment ends it.
    quirk(thing) {
        const s = this.scene, p = s.player;
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
            await this.wait(thing.ms);
            s.pose('stand');
            if (!this.save.seen.includes(thing.id)) {
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
        if (this.carry) {
            this.touchCool = s.time.now + 1200;
            this.carryBox.spill(person.x);
        } else if (t.kind === 'scare') {
            s.scareContact(person.x, t.fright);
        }
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
        this.story.update(dt, time);
        this.updateQuirks(time);
        this.updateHud();
        if (this.parasol?.visible) this.parasol.setPosition(p.x + (p.flipX ? -3 : 3), p.y - PLAYER.height + 12);
    }

    // Gusts along the ship's side push her aft while she is in the air (from region 7's step).
    push() {}

    // E: a cart's end, a pickup, a switch, a hatch.
    interact() {
        const s = this.scene, p = s.player;
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
            if (Math.abs(p.x - t.x) > (t.reach ?? 18) || Math.abs(p.y - t.y) > 8) continue;
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
        return t.route === 'inside' || t.route === this.scene.route;
    }

    showParasol(on) {
        const s = this.scene;
        if (!this.parasol) {
            if (!on) return;
            this.parasol = s.add.image(0, 0, 'parasol-open').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.02);
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
                if (what !== 'dash') this.hint(HINTS[what]);
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
        s.pools = s.pools.filter(w => w !== pool);
        if (s.mode === 'swim' && s.pool === pool) {
            // The water goes from under her: she stands in the tank.
            s.mode = 'play';
            s.pool = null;
            s.player.setDepth(s.DEPTH.player);
            s.player.body.enable = true;
            s.player.body.reset(s.player.x, pool.y);
        }
        const gone = () => [pool.water, pool.ripples].forEach(o => o.setVisible(false));
        if (atOnce) gone();
        else s.tweens.add({ targets: [pool.water, pool.ripples], alpha: 0, duration: 5000, onComplete: gone });
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
            g.tiles.forEach(t => t.setAlpha(open ? 1 : 0));
            g.lid.setVisible(!open);
        }
        this.hudBooks?.setText(`📖 ${Object.keys(this.save.books).length}/10`);
        this.hudBooks?.setAlpha(Object.keys(this.save.books).length ? 1 : 0.35);
    }

    addColliders(p) {
        const s = this.scene;
        s.physics.add.collider(p, this.platZones, null, (_, z) => s.route === OUTSIDE
            && (z.plat.solid || (s.droppingThrough !== z.plat && p.body.velocity.y >= 0 && p.body.bottom <= z.body.top + 10)));
        s.physics.add.collider(p, this.wallZones, null, () => s.route === OUTSIDE);
        s.physics.add.collider(p, this.ductFloor, null, () => s.route === 'duct');
        for (const t of this.pushables) {
            s.physics.add.collider(p, t.zone, null, () => t.route === s.route
                && (!t.top || (p.body.velocity.y >= 0 && p.body.bottom <= t.zone.body.top + 10 && s.pushing !== t)));
        }
        for (const t of this.lows) s.physics.add.collider(p, t.zone, null, () => t.route === s.route);
        for (const t of this.solids) s.physics.add.collider(p, t.zone, null, () => t.route === s.route);
        for (const r of this.robots ?? []) r.addCollider(p);
        // The dash goes through a breakable, and it is gone for good.
        for (const t of this.breakables) {
            s.physics.add.collider(p, t.zone, null, () => {
                if (t.route !== s.route || t.done) return false;
                if (!s.isDashing()) return true;
                t.done = true;
                s.smash(t.x, t.y - 12);
                this.save.broken.push(t.id);
                t.items.forEach(i => i.destroy());
                t.items = [];
                t.zone.destroy();
                this.refresh();
                return false;
            });
        }
    }

    // The first tangerine after the scream: the dash's key (population §6.1).
    onTangerine() {
        if (this.progress.knows('dash') && !this.save.seen.includes('hint-dash')) {
            this.save.seen.push('hint-dash');
            this.hint(HINTS.dash);
        }
    }

    // What she carries, on the HUD, with how much of it is left (a melting cone, a cooling cup).
    updateHud() {
        if (!this.hudCarry) return;
        const left = this.carryBox.left();
        this.hudCarry.back.setVisible(left !== null);
        this.hudCarry.bar.setVisible(left !== null);
        if (left !== null) this.hudCarry.bar.setSize(100 * left, 6).setFillStyle(left > 0.35 ? 0x8fd3ff : 0xe83b3b);
    }

    // The books' count, under the card slots (population §2.8).
    buildHud(layer) {
        const s = this.scene;
        this.hudBooks = s.add.text(24, 114, '', {
            fontFamily: 'Verdana, sans-serif', fontSize: '18px', color: '#ffffff', stroke: '#1d2b53', strokeThickness: 4,
        });
        const back = s.add.rectangle(24, 146, 104, 10, 0x1d2b53).setOrigin(0).setVisible(false);
        const bar = s.add.rectangle(26, 148, 100, 6, 0x8fd3ff).setOrigin(0).setVisible(false);
        this.hudCarry = { back, bar };
        layer.add([this.hudBooks, back, bar]);
        this.refresh();
    }
}
