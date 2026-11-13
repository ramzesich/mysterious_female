// Progression (GAME_DESIGN.md §6.1; every lock in docs/population.md §2.6): the regions she has
// opened, her cards, the flags of what has happened, and the locks that read them: flights of
// stairs, doors in the walls across the decks, the walls at the decks' ends, the elevators' landings.
// The data comes from the map (tools/ship_layout.py through the map builder). Step 0 of
// docs/build-plan.md: the cards lie where their givers will stand, and triggers stand in for scenes.

import { KEY_CARDS } from './config.js';
import { writeSave } from './save.js';

// The readers' and the HUD's colours (Resurrect 64).
export const CARD_COLOURS = { deck: 0x4d9be6, ent: 0xe83b3b, hk: 0x1ebc73, off: 0xf9c22b };
const CARD_NAMES = { deck: 'Deck', ent: 'Entertainment', hk: 'Housekeeping', off: "Officer's" };
const CARD_ORDER = ['deck', 'ent', 'hk', 'off'];

// "card:off:-1", "oneway:1", "flag:bb2", "block:wedding", "region:3", "" (none).
export function parseLock(text) {
    if (!text) return null;
    const [kind, a, b] = String(text).split(':');
    if (kind === 'card') return { kind, card: a, free: Number(b ?? 0) };
    if (kind === 'oneway') return { kind, free: Number(a) };
    if (kind === 'block') return { kind, id: a, side: Number(b ?? -1) };
    return { kind, id: a };
}

export class Progression {
    constructor(scene) {
        this.scene = scene;
        this.save = scene.save;
        this.regions = [];      // { n, deck, route, x0, x1 }
        this.cards = [];        // pickups on their tables
        this.triggers = [];
        this.blocks = {};       // id -> { what, sign, lift }
        this.blockDrawings = []; // { id, items }
        this.barriers = [];
        this.roomDoors = [];
        const flag = new URLSearchParams(location.search).get('cards');
        // ?cards=all: every lock open, for testing round the ship (README).
        this.openAll = flag === 'all' || !KEY_CARDS.required;
    }

    // --- The map's objects --------------------------------------------------------------------

    addObject(o, prop) {
        const s = this.scene;
        switch (o.type) {
            case 'progression':
                this.blocks = JSON.parse(prop(o, 'blocks', '{}'));
                break;
            case 'region':
                this.regions.push({ n: prop(o, 'region', 0), deck: prop(o, 'deck', 0), route: prop(o, 'route', 'inside'), x0: o.x, x1: o.x + o.width });
                break;
            case 'card': {
                const card = prop(o, 'card', '');
                // On a small side table: nothing floats (§6.3).
                const table = s.add.image(o.x, o.y, 'sidetable').setOrigin(0.5, 1).setDepth(3);
                const top = o.y - table.height;
                const img = s.add.image(o.x, top, 'shipart', 'key-card').setOrigin(0.5, 1).setDepth(3.1);
                const band = s.add.rectangle(o.x - 6, top - 9, 13, 3, CARD_COLOURS[card]).setOrigin(0).setDepth(3.11);
                s.worldLayer.add([table, img, band]);
                // The table stays when the card is taken.
                this.cards.push({ card, x: o.x, y: o.y, needs: prop(o, 'needs', ''), items: [img, band] });
                break;
            }
            case 'trigger':
                this.triggers.push({ flag: prop(o, 'flag', ''), needs: prop(o, 'needs', ''), x0: o.x, x1: o.x + o.width, y0: o.y, y1: o.y + o.height });
                break;
        }
    }

    // After every object is built: the readers and blocks on the flights, the locked doors' signs,
    // the barriers in the walls at the decks' ends.
    build(endWalls) {
        const s = this.scene;
        for (const f of s.flights) {
            f.lockSpec = parseLock(f.lock);
            if (!f.lockSpec) continue;
            if (f.lockSpec.kind === 'block') {
                // A rope across each end, its sign hung on it.
                for (const end of [f.bottom, f.top]) this.ropeAt(end.x, end.y, f.lockSpec.id);
            }
        }
        for (const b of s.bulkheads) {
            b.lockSpec = parseLock(b.lock);
            if (!b.lockSpec) continue;
            if (b.lockSpec.kind === 'card') {
                for (const side of [-1, 1]) {
                    if (side !== b.lockSpec.free) this.reader(b.x + side * 20, b.floor, b.lockSpec.card);
                }
            } else if (b.lockSpec.kind === 'block' || b.lockSpec.kind === 'flag') {
                // On the side she comes to it from (the Library's rope in its reading room).
                this.ropeAt(b.x + (b.lockSpec.side ?? -1) * 26, b.floor, b.lockSpec.kind === 'block' ? b.lockSpec.id : `flag:${b.lockSpec.id}`);
            }
        }
        for (const w of endWalls) {
            const lock = parseLock(w.lock);
            if (!lock) continue;
            // A thin barrier at the face she can't come through, so she stops where she can be
            // seen, not hidden inside the wall; both faces for a lock with no free side.
            const faces = lock.kind === 'oneway' ? [lock.free < 0 ? w.x1 : w.x0] : [w.x0, w.x1];
            for (const x of faces) {
                const zone = s.add.zone(x, w.floor - s.deckPitch / 2 + 8, 4, s.deckPitch - 16);
                s.physics.add.existing(zone, true);
                this.barriers.push({ id: w.id, lock, zone, x });
            }
        }
        this.refresh();
    }

    // A crew door to a room (the linen room) that needs a card: shut, its reader beside it, until
    // she has the card; then held open as drawn.
    roomDoor(room, lockText, shutImage, x, floor) {
        room.lockSpec = parseLock(lockText);
        if (!room.lockSpec) return;
        if (room.lockSpec.kind === 'card') this.reader(x + 22, floor, room.lockSpec.card);
        this.roomDoors.push({ room, shutImage });
        this.refresh();
    }

    reader(x, floor, card) {
        const s = this.scene;
        const reader = s.add.image(x, floor - 40, 'reader').setDepth(8);
        const light = s.add.rectangle(x, floor - 42, 4, 2, CARD_COLOURS[card] ?? 0xffffff).setDepth(8);
        s.worldLayer.add([reader, light]);
    }

    ropeAt(x, floor, id) {
        const s = this.scene;
        const rope = s.add.image(x, floor, 'shipart', 'rope-barrier').setOrigin(0.5, 1).setDepth(8);
        const text = this.blocks[id]?.sign ?? (id === 'flag:bb2' ? 'QUIET PLEASE' : '');
        // Hung on the rope, within its posts: long signs wrap onto two lines.
        const sign = s.add.text(x, floor - 15, text, {
            fontFamily: 'Verdana, sans-serif', fontSize: '5px', fontStyle: 'bold', color: '#45293f',
            backgroundColor: '#f3ecdd', padding: { x: 1, y: 1 }, resolution: 4, align: 'center',
            wordWrap: { width: 34 },
        }).setOrigin(0.5).setDepth(8.01);
        s.worldLayer.add([rope, sign]);
        this.blockDrawings.push({ id, items: [rope, sign] });
    }

    // The barriers' colliders, once she exists.
    addColliders(player) {
        for (const b of this.barriers) {
            this.scene.physics.add.collider(player, b.zone, null, () => this.barrierHolds(b));
        }
    }

    // --- What is open -------------------------------------------------------------------------

    hasCard(card) {
        return this.openAll || !card || this.save.cards.includes(card);
    }

    regionOpen(n) {
        return this.openAll || !n || this.save.regions.includes(n);
    }

    flagSet(name) {
        return this.openAll || !name || this.save.flags.includes(name);
    }

    // Whether something has really happened (never opened by ?cards=all: the story's own state).
    has(name) {
        return !name || this.save.flags.includes(name);
    }

    // Her ways to move (§6.1.2): the dash, crawling, the grip socks, the parasol.
    knows(verb) {
        return this.openAll || this.save.verbs.includes(verb);
    }

    learn(verb) {
        if (!this.save.verbs.includes(verb)) this.open('verbs', verb);
    }

    blockLifted(id) {
        if (this.openAll) return true;
        if (id.startsWith('flag:')) return this.flagSet(id.slice(5));
        const lift = parseLock(this.blocks[id]?.lift);
        if (!lift) return false;
        return lift.kind === 'region' ? this.regionOpen(Number(lift.id)) : this.flagSet(lift.id);
    }

    // Whether a lock lets her through from `side` (-1 coming from the bow side, 1 from the stern),
    // and if not, what to show: { ok, card, sign }. A one-way door she has come through from its
    // free side is open both ways for good (`id` in the save's `opened`).
    passes(lock, side, id) {
        if (!lock || this.openAll) return { ok: true };
        switch (lock.kind) {
            case 'card':
                return this.hasCard(lock.card) || (lock.free && side === lock.free) ? { ok: true } : { ok: false, card: lock.card };
            case 'oneway':
                return side === lock.free || this.save.opened.includes(id) ? { ok: true, through: side === lock.free } : { ok: false };
            case 'flag':
                return this.flagSet(lock.id) ? { ok: true } : { ok: false, sign: lock.id === 'bb2' ? 'QUIET PLEASE' : '' };
            case 'block':
                return this.blockLifted(lock.id) ? { ok: true } : { ok: false, sign: this.blocks[lock.id]?.sign };
        }
        return { ok: true };
    }

    // A flight: up needs its card (free coming down, the fire door's escape side); a block stops
    // her both ways.
    flightPasses(flight, up) {
        const lock = flight.lockSpec;
        if (!lock || this.openAll) return { ok: true };
        if (lock.kind === 'card' && !up) return { ok: true };
        return this.passes(lock, 0, flight.name);
    }

    // A door in a wall across the deck, opened with E from `side`.
    doorPasses(b, side) {
        const res = this.passes(b.lockSpec, side, b.id);
        if (res.ok && res.through) this.markOpened(b.id);
        return res;
    }

    markOpened(id) {
        if (this.save.opened.includes(id)) return;
        this.save.opened.push(id);
        writeSave(this.save);
    }

    // A wall at a deck's end holds her unless its lock lets her through from where she was a moment
    // ago (her body's last position, so she is never pushed back out of a wall she walked into).
    barrierHolds(b) {
        const s = this.scene, body = s.player.body;
        if (s.route !== 'inside') return false;
        const was = body.prev.x + body.width / 2;
        const res = this.passes(b.lock, was < b.x ? -1 : 1, b.id);
        if (res.ok && res.through) this.markOpened(b.id);
        if (!res.ok) s.showLock(res);
        return !res.ok;
    }

    // --- Each frame ---------------------------------------------------------------------------

    update() {
        const s = this.scene, p = s.player;
        // `frozen`: nothing opens, for the playtests' sweep, which teleports her round the ship.
        if (this.frozen || s.mode === 'lift' || s.mode === 'trunk' || s.mode === 'scripted') return;
        // The region she stands in.
        const deck = s.deckOfY(p.y);
        if (deck) {
            for (const r of this.regions) {
                if (r.deck !== deck || r.route !== s.route || p.x < r.x0 || p.x >= r.x1) continue;
                // (The balconies are region 7's only in the grip socks: before, the balcony cabin's
                // balcony is a dead end of region 4's.)
                if (r.n === 7 && r.route !== 'inside' && !this.knows('socks')) continue;
                if (!this.save.regions.includes(r.n)) this.open('regions', r.n);
                break;
            }
        }
        // The stand-ins for scenes.
        for (const t of this.triggers) {
            if (this.save.flags.includes(t.flag) || !this.flagSet(t.needs) || s.route !== 'inside') continue;
            if (p.x >= t.x0 && p.x < t.x1 && p.y > t.y0 && p.y <= t.y1 + 4) this.setFlag(t.flag);
        }
    }

    open(list, value) {
        this.save[list].push(value);
        writeSave(this.save);
        this.refresh();
    }

    setFlag(name) {
        if (this.save.flags.includes(name)) return;
        this.open('flags', name);
        this.scene.world?.onFlag(name);
    }

    // E by a card on its table: hers.
    tryPickup() {
        const s = this.scene, p = s.player;
        const c = this.cards.find(c => c.items[0].visible && Math.abs(p.x - c.x) < 18 && Math.abs(p.y - c.y) < 6);
        if (!c) return false;
        this.open('cards', c.card);
        s.sparkle?.(c.x, c.y - 30);
        return true;
    }

    // Blocks lifted, cards shown or taken, the HUD's slots.
    refresh() {
        for (const d of this.blockDrawings) d.items.forEach(i => i.setVisible(!this.blockLifted(d.id)));
        for (const { room, shutImage } of this.roomDoors) shutImage.setVisible(!this.passes(room.lockSpec, 0, '').ok);
        for (const c of this.cards) {
            const there = !this.save.cards.includes(c.card) && (!c.needs || this.save.flags.includes(c.needs));
            c.items.forEach(i => i.setVisible(there));
        }
        this.hudSlots?.forEach(({ card, rect }) => rect.setFillStyle(CARD_COLOURS[card], this.save.cards.includes(card) ? 1 : 0.15));
        this.scene.world?.refresh();
    }

    // Four card slots under the tangerine count (§2.8 of the population spec), lit when held.
    buildHud(layer) {
        const s = this.scene;
        this.hudSlots = CARD_ORDER.map((card, i) => {
            const rect = s.add.rectangle(24 + i * 30, 92, 24, 16, CARD_COLOURS[card], 0.15).setOrigin(0).setStrokeStyle(2, 0x1d2b53);
            layer.add(rect);
            return { card, rect };
        });
        this.refresh();
    }

    cardName(card) {
        return CARD_NAMES[card] ?? card;
    }
}
