// What she can use, shown where she can use it (the user, 2026-11-23, plan-the-rest §7c, from GIF mock-ups of
// every kind): while she stands where E would act on a thing, the thing's colours pulse between its own state and
// the other one, and settle back when she leaves. A thing drawn in full colour (a door, a pickup, a lift) pulses
// down to the wash of the props round it and back; a thing drawn muted like the props (the pool bar, the jackpot
// slots, the captain's door) pulses up to its full colours and back. People never change; a pickup's glint stays
// as it is (it is for spotting a thing from afar).
//
// The wash is the one the ship's props have (tools/build_ship_art.py's `muted`: each colour toward the corridor
// wall, by the place's level from tools/wash_levels.py, the map's `washLevels`), or a room's (30% toward its own
// wall, tools/draw_rooms.py's WASH). It is drawn as a copy of the thing's picture filled with the wall's colour
// over it at the wash's strength (the same sum, colour by colour), so nothing new is drawn and nothing is built;
// a muted map piece is shown by its full twin with that copy over it at rest, which is the muted twin exactly.
//
// **Doors are secrets too** (the user, 2026-11-23: "make all doors look like their background neighboring doors. Or,
// like other background things around them, if there are no doors"): at rest every door she can use is washed as the
// background doors beside it are (the guest cabins' 35%), or as the props round it, or inside a room as the room
// (30% toward its wall); a trunk's door with nothing round it 20% (the user). The pulse brings it up to full colour.
// Left as they are (the user): the lifts, the glass doors across the deck, deck 11's lone steel one, the balconies'
// doors, the lifeboat's roof hatch, the shower's door; the captain's door and the nook's bookcase are muted already. `restDoors`, once the world is built.
//
// Which thing is the one E would act on is asked as the ship scene asks it (`ShipScene.update`'s E chain: the
// world's things and carts, a key card, the shower, the mirror, a route's door, a door across the deck, a lift, a
// trunk's door), in that order, the first one only. The story's E with people is theirs and shows nothing.

import { MASSAGE, PLAYER, SHOWER } from './config.js';

const PERIOD = 1600;        // ms, full colour to the wash and back
const SETTLE = 270;         // ms, from the deepest pulse back to its own state once she has gone
const WALL = 0xe9dfcc;      // the corridor wall the props are washed toward (tools/build_ship_art.py's WALL)
const ROOM_WASH = 0.3;      // a room's wash toward its own wall (tools/draw_rooms.py, draw_cabin.py, draw_linen.py)
const SUFFIX = { '-bg': 0.35, '-w20': 0.20, '-lt': 0.12 };
// (Her crew cabin's door pulsed down to 40% once, "only for this door here"; muted at rest since, it pulses up.)
const TRUNK_ALONE = 0.2;    // a trunk's door with no background door and no prop round it (the user, 2026-11-23)
const SKIP_DOORS = /^(roof|balcony|bookcase)$/;   // a room's doors left as they are: the lifeboat's hatch, the
                                                  // balconies' (the user: to be worked on), the nook's bookcase (muted)
const ROOM_WALLS = { 'cabin-8206': 0xece3cf, 'linen-room': 0xdfe8e2 };   // (draw_cabin.py's, draw_linen.py's WALL)
// Figures never change (the user: "People shall not change tones at all"), nor Bumbot.
const FIGURES = /^(people|bumbot|her|court|reading|drill|gags|towels)/;
// Things whose picture is a map piece (their own `items` hold none, or a small thing on it): the piece's name
// without its wash's suffix (or a texture's key), found where the thing stands.
const PIECES = {
    src_icecream: 'ice-cream-machine', src_coffee: 'coffee-station', src_cocktail: 'pool-bar', src_lunch: 'service-station',
    sec_swan: 'ice-swan', sec_jackpot: 'slot-pair', sec_hottub: 'hot-tub', sec_slide: 'kids-slide', sec_piano: 'grand-piano',
    sec_captain: 'door-cabin', sec_telescope: 'telescope', sec_chess: 'chess-pawn', sec_peek_sea: 'peek-sea',
    sec_oddbook: 'bookcase', sec_chair: 'reading-chair',
};
// Things drawn into a room's picture: the room's picture, a box [x, y, w, h] in it a px wider than the thing all
// round but at its foot (the wall round it is found from the box's edge: `boxPicture`), and whether the thing is
// kept in full colour in the room (its `Room.full`, `keep`) or washed with the rest.
const IN_ROOM = {
    // (`depth`: deeper than the room's 30%: the mirror "slightly stronger", the shower's pale door hardly showed;
    // the user, 2026-11-23.)
    mirror: { key: 'room-crewcabin', box: [2, 57, 25, 71], full: true, depth: 0.4 },   // tools/draw_rooms.py: her mirror
    shower: { key: 'cabin-8206', box: [5, 43, 37, 81], full: true, depth: 0.4 },       // tools/draw_cabin.py: SHOWER (kept)
    // The desk alone, its top and its body down to the floor (the user, 2026-11-23, circled: "only the table itself
    // should pulse. Without the trash bin, without the TV, without the desk's other parts"): by the shapes
    // tools/draw_cabin.py draws it with (`keep`, its own px), the bin standing in it cut out (`cut`), the phone and
    // the programme on its top left out (above its top's row).
    sec_desk: { key: 'cabin-8206', box: [92, 88, 37, 36], full: false,
        keep: [[92, 88, 128, 92], [94, 93, 126, 123]], cut: [[105, 104, 119, 123]] },
    sec_bed: { key: 'cabin-8206', box: [137, 57, 101, 71], full: false },     // her bed (ShipScene's CABIN.bed)
    chute: { key: 'linen-room', box: [7, 82, 35, 37], full: true },           // tools/draw_linen.py: the chute's hatch (kept)
};

// A copy cut as its picture is (a door's leaf drawn in front of her as she steps out of it is the door's picture
// cut to the leaf: copied whole, the doorway's part of the copy lay over her).
function sameCut(o, c) {
    const k = o._crop;
    if (o.isCropped && k) {
        if (!c.isCropped || c._crop.x !== k.x || c._crop.y !== k.y || c._crop.width !== k.width || c._crop.height !== k.height) {
            c.setCrop(k.x, k.y, k.width, k.height);
        }
    } else if (c.isCropped) c.setCrop();
}

export class Highlight {
    constructor(scene, levels) {
        this.s = scene;
        this.levels = levels;
        this.on = new Map();        // key -> { parts, p, since, base, k }
        this.walls = {};
        this.rest = new Map();      // a door's picture -> its wash at rest { over, k }; `restDoors`
        this.restBox = new Map();   // a room door drawn in its room's picture, by its box -> { over, k }
        this.skipped = [];          // doors with nothing to take a tone from (for the tests and the log)
        this.restOff = false;       // (for pictures of before and after: the doors' wash at rest not drawn)
        scene.events.on('postupdate', (time, delta) => this.update(time, delta));
    }

    // --- Which thing E would act on, now --------------------------------------------------------------------
    target() {
        const s = this.s, p = s.player, w = s.world;
        if (!w || s.mode !== 'play' || s.intro || s.viewing || !s.grounded || s.script) return null;
        // The world's: carts first, then its things (world.interact's order; the story's people are theirs).
        const massage = this.massageTable();
        if (massage) return massage;
        for (const t of w.pushables) {
            if (w.carry || s.holding) break;
            if (t.route !== s.route || Math.abs(p.y - t.y) > 4 || (t.flag && w.progress.has(t.flag) && !t.free)) continue;
            if (!w.met(t.needs)) continue;
            const side = p.x < t.x ? -1 : 1;
            if (t.sides && side !== t.sides) continue;
            const end = t.width / 2 + PLAYER.bodyWidth / 2;
            if (Math.abs(Math.abs(p.x - t.x) - end) < (t.top ? 18 : 10)) return { key: `push:${t.id}`, thing: t, items: t.items };
        }
        for (const t of w.things) {
            if (!t.interact || t.done || !w.shown(t) || (s.holding && !t.look)) continue;
            if (Math.abs(p.x - t.x) > (t.reach ?? 18)) continue;
            if (t.from != null ? Math.abs(p.y - (t.y - t.from)) > 4 : (Math.abs(p.y - t.y) > 8 && Math.abs(p.y - (t.level ?? t.y)) > 8)) continue;
            if (t.high && Math.abs(p.y - t.level) > 8) continue;
            return { key: `thing:${t.id}`, thing: t };
        }
        if (!s.holding) {
            const c = s.progress.cards.find(c => c.items[0].visible && Math.abs(p.x - c.x) < 18 && Math.abs(p.y - c.y) < 6);
            if (c) return { key: `card:${c.card}`, items: c.items, x: c.x, y: c.y };
            // (ShipScene.tryShower: the stall's columns 6 to 40 of the cabin's picture, CABIN.shower, and SHOWER.reach.)
            const cab = s.cabin;
            if (cab && s.route === 'cabin' && p.x >= cab.room.x + 6 - SHOWER.reach && p.x <= cab.room.x + 40 + SHOWER.reach) {
                return { key: 'shower', room: 'shower' };
            }
        }
        const mirror = w.rooms[s.route]?.mirror;
        if (mirror !== undefined && !s.holding && !w.carry && Math.abs(p.x - mirror) <= 14) return { key: 'mirror', room: 'mirror' };
        const door = s.routeDoorAt(p.x, p.y);
        if (door) {
            const x = door.d ? (door.leaving ? door.d.x : door.d.outX) : (door.room ? door.room.door : door.x);
            return { key: `door:${x}:${Math.round(p.y)}`, door: { x, y: p.y } };
        }
        if (s.route === 'inside') {
            const b = s.bulkheads.find(b => !b.open && Math.abs(p.y - b.floor) <= 4 && Math.abs(p.x - b.x) <= 24);
            if (b) return { key: `bulkhead:${b.id}`, bulkhead: b };
            const lift = s.liftAt(p.x, p.y);
            if (lift) return { key: `lift:${lift.lift.x}:${lift.i}`, lift: { x: lift.lift.x, y: lift.lift.floors[lift.i].y } };
            const td = !s.holding && s.trunkDoorAt(p.x, p.y);
            if (td && !td.open) return { key: `trunk:${td.sprite.x}:${td.y}`, items: [td.sprite] };
        }
        return null;
    }

    // The spa's tables: E there is the story's massage (src/world/spa.js), a table being a map piece.
    massageTable() {
        const s = this.s, w = s.world, st = w.story;
        if (!st?.spaState || st.spaState.busy || s.route !== 'inside' || w.carry || s.holding) return null;
        const m = st.who?.('amb_masseur');
        if (!m?.on || Math.abs(s.player.y - m.y) > 8) return null;
        const t = st.spaTables().find(t => Math.abs(s.player.x - t.x) <= MASSAGE.reach);
        return t ? { key: `massage:${t.x}`, piece: { name: 'massage-table', x: t.x, y: m.y } } : null;
    }

    // --- Its pictures -------------------------------------------------------------------------------------
    parts(tg) {
        const s = this.s;
        const pics = [];
        const add = (obj, extra = {}) => { if (obj && obj.texture && !FIGURES.test(obj.texture.key)) pics.push({ obj, ...extra }); };
        if (tg.room) {
            const R = IN_ROOM[tg.room];
            const obj = this.find(o => o.texture?.key === R.key)[0];
            if (obj) add(obj, { box: R.box, full: R.full, room: R.key, keep: R.keep, cut: R.cut, depth: R.depth });
        } else if (tg.thing && IN_ROOM[tg.thing.id]) {
            const R = IN_ROOM[tg.thing.id];
            const obj = this.find(o => o.texture?.key === R.key)[0];
            if (obj) add(obj, { box: R.box, full: R.full, room: R.key, keep: R.keep, cut: R.cut, depth: R.depth });
        } else if (tg.piece) {
            const o = this.piece(tg.piece.name, tg.piece.x, tg.piece.y, 40);
            if (o) add(o);
        } else if (tg.thing) {
            const t = tg.thing, name = PIECES[t.id] ?? (t.id.startsWith('sec_chair_') ? 'reading-chair' : null)
                ?? (t.id.startsWith('haz_dnd') ? 'door-cabin-dnd' : null);
            if (name) {
                const o = this.piece(name, t.x, t.level ?? t.y, (t.reach ?? 18) + 16);
                if (o) add(o);
            } else {
                for (const i of t.items ?? []) if (i?.type === 'Image' || i?.type === 'Sprite') add(i);
            }
        } else if (tg.items) {
            for (const i of tg.items) if (i?.type === 'Image' || i?.type === 'Sprite') add(i);
        } else if (tg.door && s.route !== 'inside' && s.route !== 'promenade') {
            // Inside a room, its way out is drawn in the room's own picture (in full colour, `Room.full`): the door's
            // box there, the wall round it taken out (the corridor's door picture is behind the room's, unseen).
            const obj = this.find(o => o.visible && o.texture.key === this.roomKey())[0];
            if (obj) add(obj, { box: this.doorBox(obj, tg.door.x, tg.door.y), full: true, room: this.roomKey() });
        } else if (tg.door) {
            const { x, y } = tg.door;
            const o = this.find(o => (o.type === 'Image' || o.type === 'Sprite') && o.visible
                && (/^door/.test(o.texture.key) || /^door/.test(String(o.frame.name)))
                && Math.abs(o.getBounds().centerX - x) < 20 && Math.abs(o.getBounds().bottom - y) < 8)
                .sort((a, b) => Math.abs(a.getBounds().centerX - x) - Math.abs(b.getBounds().centerX - x))[0];
            if (o) add(o);
        } else if (tg.lift) {
            const { x, y } = tg.lift;
            for (const o of this.find(o => ['lift-leaf', 'lift-frame'].includes(o.texture?.key) && o.visible
                && Math.abs(o.getBounds().centerX - x) < 24 && Math.abs(o.getBounds().bottom - y) < 8)) add(o);
        } else if (tg.bulkhead) {
            add(this.shutPicture(tg.bulkhead));
        }
        return pics;
    }

    // A room door's box in its room's picture: 17 px either side of its middle, 84 up from the floor.
    doorBox(obj, x, y) {
        const tl = obj.getTopLeft(), dx = Math.round(x - tl.x), fy = Math.round(y - tl.y);
        const x0 = Math.max(0, dx - 17), y0 = Math.max(0, fy - 84);
        return [x0, y0, Math.min(obj.width, dx + 18) - x0, fy - y0];
    }

    // --- Doors at rest, washed like what stands round them ------------------------------------------------------
    restDoors() {
        const s = this.s, w = s.world;
        const all = this.find(o => o.getBounds && (o.type === 'Image' || o.type === 'Sprite'));
        const B = o => o.getBounds();
        const muted = o => /-(bg|w20|lt)$/.test(String(o.frame.name));
        const isDoor = o => /door/.test(o.texture.key) || /door/.test(String(o.frame.name));
        // The level round a door: the background doors beside it, else the props round it.
        const level = (x, y) => {
            const nb = all.filter(o => isDoor(o) && muted(o) && Math.abs(B(o).bottom - y) < 10 && Math.abs(B(o).centerX - x) > 24
                && Math.abs(B(o).centerX - x) < 420).sort((a, b) => Math.abs(B(a).centerX - x) - Math.abs(B(b).centerX - x))[0];
            const pr = nb ?? all.filter(o => o.texture.key === 'shipart' && muted(o) && !/^(door|railing)/.test(o.frame.name)
                && Math.abs(B(o).bottom - y) < 12 && Math.abs(B(o).centerX - x) < 160).sort((a, b) => Math.abs(B(a).centerX - x) - Math.abs(B(b).centerX - x))[0];
            return pr ? SUFFIX[Object.keys(SUFFIX).find(k => pr.frame.name.endsWith(k))] : null;
        };
        const at = (x, y) => all.filter(o => isDoor(o) && !muted(o) && !FIGURES.test(o.texture.key)
            && Math.abs(B(o).centerX - x) < 20 && Math.abs(B(o).bottom - y) < 10);
        const wash = (pics, k, what) => {
            if (k == null) { this.skipped.push(what); return; }
            for (const o of pics) if (o && !this.rest.has(o)) {
                const over = this.copy(o, WALL);
                this.rest.set(o, { over, k });
            }
        };
        const roomPic = route => all.find(o => o.texture.key === (route === 'cabin' ? 'cabin-8206' : route === 'linen' ? 'linen-room'
            : route === 'chapel' ? 'chapel-room' : `room-${route}`));
        const inside = (route, x, y) => {
            const obj = roomPic(route);
            if (!obj) return;
            const box = this.doorBox(obj, x, y), key = `${obj.texture.key}:${box.join(',')}`;
            if (this.restBox.has(key)) return;
            const over = this.boxPicture(obj, { box }, 'full', ROOM_WASH, this.wallOf(obj.texture.key));
            this.restBox.set(key, { over, k: ROOM_WASH, o: obj });
        };
        for (const r of s.rooms) {
            const doors = r.doors ?? [{ x: r.door, outX: r.door, outY: r.floor, outRoute: 'inside' }];
            for (const d of doors) {
                if (SKIP_DOORS.test(d.kind ?? '') || r.hidden) continue;
                if (d.outRoute === 'inside' || d.outRoute === 'promenade') wash(at(d.outX, d.outY), level(d.outX, d.outY), `room ${r.route} at ${d.outX}`);
                inside(r.route, d.x, r.floor);
            }
        }
        if (s.promenade) for (const x of s.promenade.doors) wash(at(x, s.promenade.floor), level(x, s.promenade.floor), `promenade door at ${x}`);
        // The doors across the deck: the glass ones (one-way ones too) stay as they are (the user: "Leave all the glass
        // doors as they are now"), and a steel one with nothing round it (deck 11's, by the lido): only the steel ones
        // by something take its tone.
        for (const b of s.bulkheads) {
            const glass = b.shut.type !== 'Graphics' || b.shut.commandBuffer?.includes(0xbfe6f5);
            const k = level(b.x, b.floor);
            if (glass || k == null) continue;
            wash([this.shutPicture(b), b.openDoor].filter(o => o?.texture), k, `door across deck at ${b.x},${b.floor}`);
        }
        for (const t of s.trunks) for (const d of t.doors) wash([d.sprite], level(t.x, d.y) ?? TRUNK_ALONE, `trunk at ${t.x},${d.y}`);
        for (const t of w.things) if (/^haz_dnd/.test(t.id)) wash(at(t.x, t.y), level(t.x, t.y), `${t.id}`);
        this.restDone = true;
    }

    // The washes at rest follow their doors (a door opened, shut, slid, shown or hidden); one pulsing is the pulse's.
    restSync() {
        for (const [o, r] of this.rest) {
            const c = r.over;
            if (!o.scene || !c.scene) continue;
            if (c.texture.key !== o.texture.key || c.frame.name !== o.frame.name) c.setTexture(o.texture.key, o.frame.name);
            c.setPosition(o.x, o.y).setOrigin(o.originX, o.originY).setFlip(o.flipX, o.flipY).setScale(o.scaleX, o.scaleY);
            sameCut(o, c);
            const g = o.hlOver;
            c.setVisible((g ? g.visible : o.visible) && !this.restOff);
            if (!r.pulsing) c.setAlpha(r.k * (g ? g.alpha : o.alpha));
        }
        for (const r of this.restBox.values()) {
            if (!r.over.scene) continue;
            r.over.setVisible(r.o.visible && !this.restOff);
            if (!r.pulsing) r.over.setAlpha(r.k * r.o.alpha);
        }
    }

    // Every picture of the scene that passes `test` (in layers too).
    find(test) {
        const out = [];
        const walk = list => { for (const o of list) { if (o.list && o.type !== 'Text') walk(o.list); else if (o.texture && o.frame && !o.hlCopy && test(o)) out.push(o); } };
        walk(this.s.children.list);
        return out;
    }

    // A map piece by its name (any wash), at a thing's place: the nearest whose foot is on its floor.
    piece(name, x, y, reach) {
        const base = n => String(n).replace(/-(bg|w20|lt)$/, '');
        return this.find(o => o.visible && (o.texture.key === name || (o.texture.key === 'shipart' && base(o.frame.name) === name)))
            .filter(o => { const b = o.getBounds(); return b.right > x - reach && b.left < x + reach && b.bottom > y - 12 && b.top < y + 4; })
            .sort((a, b) => Math.abs(a.getBounds().centerX - x) - Math.abs(b.getBounds().centerX - x))[0] ?? null;
    }

    // A side-on door across the deck is drawn in code: copied once into a picture of its own to be washed as one.
    shutPicture(b) {
        const g = b.shut;
        if (g.type !== 'Graphics') return g;
        const key = `hl-shut:${b.id}`;
        const x0 = b.x - 10, y0 = b.floor - 110;
        if (!this.s.textures.exists(key)) {
            const dt = this.s.textures.addDynamicTexture(key, 20, 110);
            dt.draw(g, -x0, -y0);
            dt.render();
        }
        b.shutPic ??= this.s.make.image({ x: x0, y: y0, key, add: false }).setOrigin(0).setVisible(false);
        b.shutPic.depth = g.depth;
        b.shutPic.hlOver = g;          // (drawn over the Graphics itself, which stays)
        return b.shutPic;
    }

    // --- How far it washes, and toward what -----------------------------------------------------------------
    wallOf(key) {
        if (ROOM_WALLS[key] !== undefined) return ROOM_WALLS[key];
        if (this.walls[key] !== undefined) return this.walls[key];
        // (A room of tools/draw_rooms.py: its wall is the commonest colour along its row 12, under the ceiling.)
        const tex = this.s.textures.get(key), w = tex.source[0].width, count = {};
        for (let x = 0; x < w; x++) {
            const c = this.s.textures.getPixel(x, 12, key);
            if (c && c.alpha) { const v = (c.red << 16) | (c.green << 8) | c.blue; count[v] = (count[v] ?? 0) + 1; }
        }
        const best = Object.entries(count).sort((a, b) => b[1] - a[1])[0];
        return (this.walls[key] = best ? Number(best[0]) : WALL);
    }

    // The level of the props round a thing (the user: "to the level of muteness of props that surround it"): the
    // nearest washed map piece on its floor within 96 px; with none, its place's (tools/wash_levels.py's table:
    // the balconies', a place's, the deck's).
    placeLevel(x, y) {
        const s = this.s, L = this.levels;
        if (s.route !== 'inside' && s.route !== 'promenade') return ROOM_WASH;
        const near = this.find(o => o.visible && o.texture.key === 'shipart' && /-(bg|w20|lt)$/.test(o.frame.name)
            && !/^(door|railing)/.test(o.frame.name))
            .map(o => [o, o.getBounds()]).filter(([, b]) => Math.abs(b.bottom - y) < 10 && Math.abs(b.centerX - x) < 96)
            .sort((a, b) => Math.abs(a[1].centerX - x) - Math.abs(b[1].centerX - x))[0];
        if (near) return SUFFIX[Object.keys(SUFFIX).find(k => near[0].frame.name.endsWith(k))];
        if (!L) return 0.2;
        const deck = Math.round(s.deckAt(y - 2));
        if (s.route === 'promenade' && deck >= 8) return L.balconies / 100;
        const place = L.places.find(([d, a, b]) => d === deck && x >= a && x < b);
        return (place ? place[3] : (L.decks[deck] ?? L.default)) / 100;
    }

    roomKey() {
        const s = this.s, r = s.route;
        if (r === 'cabin') return 'cabin-8206';
        if (r === 'linen') return 'linen-room';
        if (r === 'chapel') return 'chapel-room';
        return `room-${r}`;
    }

    // --- The pulse --------------------------------------------------------------------------------------------
    start(tg, time) {
        const s = this.s, parts = [];
        for (const pic of this.parts(tg)) {
            const o = pic.obj;
            const rest = pic.box ? this.restBox.get(`${o.texture.key}:${pic.box.join(',')}`) : this.rest.get(o);
            if (rest) {
                // A door washed at rest: its own wash pulses off it.
                rest.pulsing = true;
                parts.push({ o, over: rest.over, mode: 'rest', k: rest.k, rest, box: pic.box });
                continue;
            }
            const suffix = Object.keys(SUFFIX).find(x => String(o.frame.name).endsWith(x));
            const inRoom = s.route !== 'inside' && s.route !== 'promenade';
            let mode, k, wash, frame = null;
            if (pic.box && !pic.full) {
                // Washed into a room's picture: its full colours worked back out of the wash, shown over it.
                mode = 'unwash'; k = ROOM_WASH; wash = this.wallOf(pic.room);
            } else if (suffix && s.textures.get(o.texture.key).has(o.frame.name.slice(0, -suffix.length))) {
                // A muted map piece: its full twin, the wash over it at rest.
                mode = 'muted'; k = SUFFIX[suffix]; wash = WALL; frame = o.frame.name;
                o.setFrame(frame.slice(0, -suffix.length));
            } else {
                mode = 'full'; wash = pic.box || inRoom ? this.wallOf(pic.room ?? this.roomKey()) : WALL;
                k = pic.depth ?? (pic.box || inRoom ? ROOM_WASH : this.placeLevel(o.x, s.player.y));
            }
            const over = pic.box ? this.boxPicture(o, pic, mode, k, wash) : this.copy(o, wash);
            parts.push({ o, over, mode, k, frame, box: pic.box });
        }
        return { parts, p: 0, since: time };
    }

    // A copy of a picture filled with `wash`, laid just over it (in its layer, if it has one).
    copy(o, wash) {
        const s = this.s;
        const c = s.add.image(o.x, o.y, o.texture.key, o.frame.name).setTint(wash).setTintMode(Phaser.TintModes.FILL).setAlpha(0);
        c.hlCopy = true;                    // (not a piece of the map: `find` and the tests skip it)
        this.place(o.hlOver ?? o, c);
        return c;
    }

    // A thing drawn into a room's picture, as a picture of its own: the box cut out, the wall round the thing taken
    // away (the colours along the box's top and sides, flooded in from there: the user saw the whole box pulse as a
    // pale frame), and for a thing washed with the room its colours worked back out (c = (m - k w) / (1 - k)).
    // A full thing's copy is filled with the wall's colour, as `copy`; an unwashed one is laid over it as it is.
    // (A thing given by its shapes, `keep` and `cut` in the picture's px, is cut by them instead of by the wall.)
    boxPicture(o, pic, mode, k, wash) {
        const box = pic.box;
        const s = this.s, key = `hl-box:${o.texture.key}:${box.join(',')}:${mode}`;
        if (!s.textures.exists(key)) {
            const [bx, by, bw, bh] = box, f = o.frame;
            const tex = s.textures.createCanvas(key, bw, bh), ctx = tex.getContext();
            ctx.drawImage(f.source.image, f.cutX + bx, f.cutY + by, bw, bh, 0, 0, bw, bh);
            const img = ctx.getImageData(0, 0, bw, bh), d = img.data;
            const at = (x, y) => (y * bw + x) * 4, rgb = i => (d[i] << 16) | (d[i + 1] << 8) | d[i + 2];
            const ring = [];
            for (let x = 0; x < bw; x++) ring.push([x, 0]);
            for (let y = 0; y < bh - 1; y++) ring.push([0, y], [bw - 1, y]);       // (not the foot: it stands there)
            const wall = new Set(ring.map(([x, y]) => rgb(at(x, y))));
            const out = new Uint8Array(bw * bh), todo = pic.keep ? [] : [...ring];
            if (pic.keep) {
                const inside = (rects, x, y) => (rects ?? []).some(([x0, y0, x1, y1]) => x >= x0 && x <= x1 && y >= y0 && y <= y1);
                for (let y = 0; y < bh; y++) for (let x = 0; x < bw; x++) {
                    const X = bx + x, Y = by + y;
                    if (!inside(pic.keep, X, Y) || inside(pic.cut, X, Y)) out[y * bw + x] = 1;
                }
            }
            while (todo.length) {
                const [x, y] = todo.pop();
                if (x < 0 || y < 0 || x >= bw || y >= bh || out[y * bw + x] || !wall.has(rgb(at(x, y)))) continue;
                out[y * bw + x] = 1;
                todo.push([x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]);
            }
            const W = [(wash >> 16) & 255, (wash >> 8) & 255, wash & 255];
            for (let n = 0; n < bw * bh; n++) {
                const i = n * 4;
                if (out[n]) { d[i + 3] = 0; continue; }
                if (mode === 'unwash' && d[i + 3]) {
                    for (let j = 0; j < 3; j++) d[i + j] = Math.max(0, Math.min(255, Math.round((d[i + j] - k * W[j]) / (1 - k))));
                }
            }
            ctx.putImageData(img, 0, 0);
            tex.refresh();
        }
        const tl = o.getTopLeft();
        const c = s.add.image(tl.x + box[0], tl.y + box[1], key).setOrigin(0).setAlpha(0);
        if (mode !== 'unwash') c.setTint(wash).setTintMode(Phaser.TintModes.FILL);
        c.hlCopy = true;
        this.place(o, c);
        return c;
    }

    place(o, c) {
        const L = o.displayList;
        c.setScrollFactor(o.scrollFactorX, o.scrollFactorY);
        if (L && L.list && L !== this.s.children) {
            L.add(c);
            Phaser.Utils.Array.MoveAbove(L.list, c, o);
        }
        c.setDepth(o.depth + 0.0005);
    }

    end(e) {
        for (const part of e.parts) {
            if (part.rest) { part.rest.pulsing = false; continue; }    // (its wash at rest stays)
            if (part.frame && part.o.scene) part.o.setFrame(part.frame);
            part.over.destroy();
        }
    }

    update(time, delta) {
        if (!this.restDone && this.s.world && this.s.rooms?.length) this.restDoors();
        this.restSync();
        const tg = this.target();
        const key = tg?.key ?? null;
        if (key && !this.on.has(key)) this.on.set(key, this.start(tg, time));
        for (const [k, e] of this.on) {
            if (k === key) {
                // (Back in reach while it settles: on from where it is.)
                if (e.leaving) { e.since = time - (Math.acos(1 - 2 * Math.min(e.p, 1)) / (2 * Math.PI)) * PERIOD; e.leaving = false; }
                e.p = (1 - Math.cos(2 * Math.PI * (time - e.since) / PERIOD)) / 2;
            } else {
                e.leaving = true;
                e.p = Math.max(0, e.p - delta / SETTLE);
                if (e.p === 0) { this.end(e); this.on.delete(k); continue; }
            }
            for (const part of e.parts) {
                const o = part.o, c = part.over;
                if (!o.scene || !c.scene) continue;          // (taken away meanwhile: a pickup picked up)
                const a = part.mode === 'muted' || part.mode === 'rest' ? part.k * (1 - e.p) : part.mode === 'full' ? part.k * e.p : e.p;
                if (!part.box) {
                    c.setTexture(o.texture.key, o.frame.name).setPosition(o.x, o.y).setOrigin(o.originX, o.originY)
                        .setFlip(o.flipX, o.flipY).setScale(o.scaleX, o.scaleY);
                    sameCut(o, c);
                }
                c.setVisible(o.hlOver ? o.hlOver.visible : o.visible).setAlpha(a * (o.hlOver ? 1 : o.alpha));
            }
        }
    }

    // For the tests: what pulses now.
    state() {
        return [...this.on].map(([key, e]) => ({ key, p: e.p, leaving: !!e.leaving,
            parts: e.parts.map(x => ({ mode: x.mode, k: x.k, frame: x.o.frame.name, alpha: x.over.alpha })) }));
    }
}
