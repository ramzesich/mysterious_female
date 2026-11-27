// The open decks' and the hallways' hazards that came with the pool deck (docs/population.md, deck
// 11 and deck 10's hallway under it): the wet patch under a pool shower and the deck chair at its end,
// the gulls that dive at food carried in the open, the buffet queue, the room-service trays left on
// a hallway's floor. Like src/world/movers.js, each takes its place from maps/world.json.

import { PLAYER, CRY, GAGS } from '../config.js';
import { sfx } from '../sfx.js';
import { t } from '../lang.js';

const M = 48;
const here = (s, d) => s.route === 'inside' && s.mode === 'play' && Math.abs(s.player.y - d.y) < 100;
const nearby = (s, d) => Math.abs(s.player.x - d.x) < 900 && Math.abs(s.player.y - d.y) < 300;

// What a gull will dive at.
export const FOOD = ['cone', 'stub', 'lunch', 'cake'];

// A wet patch by the pool showers (population: `haz_wet`, `haz_deckchair`): the shower over it runs, its tray brims
// over, and a puddle lies across the floor under it (drawn on the floor's face, as if seen a little from above: seen
// edge-on, against the sea in the windows, water did not read; the user chose this look of four, 2026-11-19). Without
// the grip socks she slides across it the way she came, with no stopping and no turning, splashing. The deck chair
// stands still at its aft end, its front legs in the puddle: sliding at it she goes over it face first (7a, `ride`);
// a jump clears it. (It slid at her once, with no cause the user could see: it stands since 2026-11-19.) In the socks
// the tiles hold.
export class WetPatch {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, chairX }
        // (The shower's head over the patch's middle, 48 px up; its tray 24 px forward of that to 16 aft.)
        this.head = { x: Math.round((def.x0 + def.x1) / 2) + 1, y: def.y - 48 };
        this.tray = [this.head.x - 24, this.head.x + 16];
        this.water = s.add.graphics().setDepth(D.props + 0.05);
        this.drawPuddle();
        this.fx = s.add.graphics().setDepth(D.props + 0.06);
        this.spray = s.add.graphics().setDepth(D.player + 0.01);
        this.chair = s.add.image(def.chairX, def.y, 'shipart', 'deck-chair').setOrigin(0.5, 1).setDepth(D.props + 0.02).setFlipX(true);
        world.add([this.water, this.fx, this.spray, this.chair]);
        this.state = 'rest';
        this.slip = 0;
        this.drops = [];
        this.dropAt = 0;
    }

    // The puddle: a flat lens of water on the floor's face, its rim darker; the tray brimming over.
    drawPuddle() {
        const g = this.water, d = this.def, y = d.y, L = d.x0 + 2, R = d.x1 - 2;
        for (let x = L; x < R; x++) {
            const u = (x - L) / (R - L) * 2 - 1;
            const h = Math.max(0, Math.round(2.6 * Math.sqrt(1 - u * u) + 0.3 * Math.sin(x * 0.7)));
            if (!h) continue;
            g.fillStyle(0x4d9be6, 1).fillRect(x, y + 2 - h, 1, 2 * h);
            g.fillStyle(0x8fd3ff, 1).fillRect(x, y + 3 - h, 1, Math.max(1, 2 * h - 2));
            g.fillStyle(0x4d65b4, 1).fillRect(x, y + 1 + h, 1, 1);
        }
        const [t0, t1] = this.tray;
        g.fillStyle(0x4d9be6, 1).fillRect(t0, y - 2, t1 - t0 + 4, 2);
        g.fillStyle(0x8fd3ff, 1).fillRect(t0 + 1, y - 2, t1 - t0 + 2, 1);
        g.fillStyle(0xffffff, 1).fillRect(t0 + 4, y - 2, 5, 1).fillRect(t0 + 26, y - 2, 7, 1);
    }

    // What moves: the shower's streaks falling into the tray, the puddle's glints, the splashes off her feet.
    drawWater(time) {
        const g = this.fx.clear(), d = this.def, y = d.y, h = this.head, fall = 36;
        for (let i = 0; i < 9; i++) {
            const dx = (i % 5) * 2 - 4 + (i > 4 ? 1 : 0);
            const k = (time / 1000 * 1.6 + i * 0.37) % 1;
            g.fillStyle(i % 2 ? 0xffffff : 0x8fd3ff, 1).fillRect(h.x + dx + Math.round(dx * k * 0.6), h.y + 2 + Math.round(k * fall), 1, 3);
        }
        // (A splash where the streaks meet the tray.)
        if (Math.floor(time / 90) % 2) g.fillStyle(0xffffff, 1).fillRect(h.x - 9, y - 5, 1, 1).fillRect(h.x + 8, y - 6, 1, 1);
        else g.fillStyle(0xffffff, 1).fillRect(h.x - 6, y - 7, 1, 1).fillRect(h.x + 5, y - 5, 1, 1);
        const L = d.x0 + 2, W = d.x1 - d.x0 - 4;
        for (const [o, w] of [[0.1, 6], [0.38, 9], [0.64, 5], [0.86, 3]]) {
            const x = L + Math.round(((o + time / 9000) % 1) * (W - 10)) + 5;
            g.fillStyle(0xffffff, 1).fillRect(x, y + 1, w, 1);
        }
        const s = this.spray.clear();
        for (const q of this.drops) s.fillStyle(q.c, 1).fillRect(Math.round(q.x), Math.round(q.y), 1, 1);
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def, c = this.chair;
        if (!nearby(s, d)) return;
        this.drawWater(time);
        const onFloor = p.body.blocked.down || p.body.touching.down;
        const on = here(s, d) && Math.abs(p.y - d.y) < 2 && onFloor && p.x > d.x0 && p.x < d.x1;
        const socks = this.world.progress.knows('socks');
        // Sliding: the way she was going as she stepped on, until the patch ends or she is in the air.
        if (on && !socks) {
            if (!this.slip) {
                this.slip = p.body.velocity.x < -5 ? -1 : p.body.velocity.x > 5 ? 1 : (p.flipX ? -1 : 1);
                sfx.slip();
            }
        } else if (onFloor || !here(s, d)) {
            this.slip = 0;
        }
        s.slipDir = this.slip && here(s, d) ? this.slip : 0;
        // Splashes off her feet as she slides: thrown up and back, falling to the floor.
        if (s.slipDir && on && time > this.dropAt) {
            this.dropAt = time + 45;
            for (let i = 0; i < 2; i++) {
                this.drops.push({ x: p.x - s.slipDir * (2 + Math.random() * 4), y: d.y - 1, vx: -s.slipDir * (20 + Math.random() * 50),
                                  vy: -(50 + Math.random() * 70), c: Math.random() < 0.5 ? 0xffffff : 0x8fd3ff });
            }
        }
        this.drops = this.drops.filter(q => {
            q.vy += 500 * dt;
            q.x += q.vx * dt;
            q.y += q.vy * dt;
            return q.y < d.y;
        });
        // The chair: sliding into it she goes over it (it stands 18 px past her middle as they meet, as in her clip).
        if (this.state === 'rest' && this.slip && here(s, d) && Math.sign(c.x - p.x) === this.slip && Math.abs(c.x - p.x) <= 18 && p.y > d.y - 20) {
            this.slip = 0;
            s.slipDir = 0;
            sfx.at(c.x, d.y).scrape();
            this.state = 'hit';
            if (this.world.carry) this.world.carryBox.spill(c.x, false, 'deckchair', { vx: 0 });
            else s.scareContact(c.x, 'deckchair', { ride: this.ride() });
        } else if (this.state === 'hit' && s.mode === 'play' && Math.abs(c.x - p.x) > 30) {
            // (Once she is clear of it, it can trip her again.)
            this.state = 'rest';
        }
    }

    // 7a, the ship scene's `thingGag`: its own clip with her (`gags` sheet, `chair-sledge`, tools/build_gags.py), from
    // her slip frame 0 with the world's chair 18 px ahead of her: it trips her, she dives face first onto it, it folds
    // flat, and from the clip's `sledFrom` she sleds on it the way she dived, slowing from her slide to a stop
    // (`GAGS.sledge`). The world's chair is hidden meanwhile, and back in its place after. (7b's clip, the chair
    // reaching her back and collapsing under her, `chair-collapse`, waits in the sheet: a chair that stands cannot.)
    ride() {
        const s = this.scene, d = this.def, p = s.player, c = this.chair, g = GAGS.sledge;
        const dir = p.flipX ? -1 : 1, v0 = Math.abs(p.body.velocity.x);
        return {
            play: (done) => {
                const m = s.cache.json.get('gags-meta'), at = m.sledge.x;
                c.setVisible(false);
                // (Flipped, a frame anchored at column `at` stands by column cell - 1 - at.)
                const pic = s.add.sprite(p.x, d.y, 'gags', m.anims['chair-sledge'][0]).setOrigin((dir > 0 ? at : m.cell - 1 - at) / m.cell, m.floor / m.cell)
                    .setFlipX(dir < 0).setDepth(p.depth);
                this.world.add([pic]);
                this.pic = pic;
                pic.play('gags-sledge');
                sfx.at(p.x, d.y).creak();
                pic.once('animationcomplete-gags-sledge', () => done());
                let t = 0, thumped = false;
                const end = dir > 0 ? d.x1 + g.reach : d.x0 - g.reach;
                s.script = (dt) => {
                    if (pic.anims.currentFrame.index < g.sledFrom) return;
                    if (!thumped) {
                        thumped = true;
                        sfx.at(pic.x, d.y).thump();
                    }
                    t += dt * 1000;
                    const k = Math.max(0, 1 - t / g.slideMs);
                    pic.x += dir * v0 * k * dt;
                    if ((pic.x - end) * dir > 0) pic.x = end;
                    p.x = pic.x;
                    if (!k) s.script = null;
                };
            },
            show: () => {
                this.pic?.destroy();
                this.pic = null;
                c.setVisible(true);
                this.state = 'rest';
                this.slip = 0;
            },
        };
    }
}

// Gulls over a stretch of open deck (population: `gull_pool`, `gull_go`): they wheel overhead, or
// one sits on the rail. While she carries food there one of them dives at it: it hangs over the
// spot where she will be when it comes down (`TELL_MS`), then dives on it. If she is there, it has
// her cone (never a fright: she fetches another). The way past: not to be under it when it drops.
// (No shadow on the deck: the user, 2026-11-23, "Remove the spot shadow under the gull"; and a
// shorter hover, 950 ms then: "too easy to avoid ... but don't make it impossible to avoid".)
const TELL_MS = 600;
// With her cone (or a tangerine) it flies up and off the screen (`up`, ms), stays away (`away`), and flies back to its
// perch or its round (`back`); a dive that misses, or her cry in its tell, sends it straight back. Each leg is placed
// by the time since it began, never moved a step a frame: the birds are only updated while she is near, and a bird
// left mid-flight when she jumped away stayed in the air there (the user, 2026-11-23).
const FLIGHT = { up: 1400, away: 5000, back: 1800, off: { x: 300, y: -230 } };
export class FoodGulls {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, count, perch: { x, y }, off: a flag that keeps them away }
        // Those that circle (the pool's, `gull_pool`) wheel in the open sky over deck 12, above its railing, over the
        // opening above the pool: under deck 12's band they had flown as if under a ceiling (the user, 2026-11-19).
        // They are behind the ship's side up there (from deck 11 out of view) and come down past deck 12's band, in
        // front of her once under it (`band`). A perched one (the Great Outdoors') waits on its rail. None gives a
        // shadow (the user: "Remove the shadow spot", the pool's, 2026-11-19; the Great Outdoors', 2026-11-23).
        this.high = !def.perch;
        this.top = this.high ? def.y - 206 : def.y - 112;
        this.band = def.y - 128;
        this.birds = [];
        // (A perched one starts on its perch: from the circling ones' start it stood on air over the stretch until she came
        // near, seen from afar, in the outside view and the intro; the user, 2026-11-27.)
        const x = def.perch?.x ?? def.x, y = def.perch?.y ?? this.top;
        for (let i = 0; i < def.count; i++) {
            const sprite = s.add.image(x, y, 'things', def.perch ? 'gull-perched' : 'gull-up').setOrigin(0.5, 1).setDepth(D.player + 0.34);
            this.birds.push({ sprite, phase: i * Math.PI, x, y });
        }
        this.loot = s.add.image(0, 0, 'load-cone').setOrigin(0.5, 1).setDepth(D.player + 0.35).setVisible(false);
        world.add([...this.birds.map(b => b.sprite), this.loot]);
        this.state = 'idle';
        this.at = 0;
        this.diver = this.birds[0];
    }

    // Kept off for good (the kid squirts them): they wheel higher, and never dive.
    off() {
        return !!this.def.off && this.world.progress.has(this.def.off);
    }

    // Where a bird waits: wheeling over the stretch, or on its perch.
    home(b, time) {
        const d = this.def;
        const scared = time < (this.scaredUntil ?? 0);
        if (d.perch && !scared) return { x: d.perch.x, y: d.perch.y, perched: true };
        const t = time / 1900 + b.phase, r = (d.x1 - d.x0) / 2 + 60;
        return { x: d.x + Math.cos(t) * r, y: this.top - (this.off() ? 34 : 0) - (scared ? 50 : 0) + Math.sin(t * 2) * 9, dir: -Math.sin(t) };
    }

    // Her cry: they scatter higher a while, and a dive still in its tell is called off.
    heard() {
        const d = this.def, s = this.scene, c = this.world.cry;
        if (!this.world.hears(Phaser.Math.Clamp(c.x, d.x0, d.x1), d.y)) return;
        this.scaredUntil = s.time.now + CRY.startleMs;
        if (this.state === 'mark') {
            sfx.at(this.diver.x, this.diver.y).flap();
            this.flyBack(s.time.now, 2800);
        }
    }

    // A tangerine on the deck under them: one comes down for it and goes off with it, and they
    // leave her cone alone for 10 s (docs/plan-three-uses.md §2).
    offered(t) {
        const d = this.def, s = this.scene;
        if (this.state !== 'idle' || this.off() || t.route !== 'inside' || t.img.x < d.x0 - 40 || t.img.x > d.x1 + 40
            || Math.abs(t.img.y + 3 - d.y) > 12) return false;
        this.fruit = s.loose.claim(t);
        // (Down just short of it, facing it, the fruit before its beak.)
        const side = this.diver.x < this.fruit.x ? -1 : 1;
        this.diver.sprite.setFlipX(side > 0);
        this.pounce(this.fruit.x + side * 7);
        this.at = s.time.now + 1600;
        return true;
    }

    // Off the screen with what it took, then back after `FLIGHT.away` (`rearm`: ms after it is back before it dives again).
    flyOff(time, rearm) {
        const b = this.diver;
        this.state = 'up';
        this.leg = { t0: time, from: { x: b.x, y: b.y }, to: { x: b.x + FLIGHT.off.x, y: b.y + FLIGHT.off.y }, rearm };
    }

    // Straight back to its perch (or its round).
    flyBack(time, rearm) {
        const b = this.diver;
        this.state = 'back';
        this.loot.setVisible(false);
        b.sprite.setVisible(true);
        this.leg = { t0: time, from: { x: b.x, y: b.y }, rearm };
    }

    // A cone dropped on the deck: one comes down for it, stays a moment, and goes.
    pounce(x) {
        if (this.state !== 'idle') return;
        this.state = 'pounce';
        this.targetX = x;
        this.at = this.scene.time.now + 2600;
        sfx.at(x, this.def.y).gull();
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (!nearby(s, d)) return;
        const frames = s.textures.get('things');
        const flap = Math.floor(time / 130) % 2 && frames.has('gull-down') ? 'gull-down' : 'gull-up';
        for (const b of this.birds) {
            if (this.high) b.sprite.setDepth(b.y - 12 > this.band ? s.DEPTH.player + 0.34 : s.DEPTH.exterior - 0.05);
            if (b === this.diver && this.state !== 'idle') continue;
            const h = this.home(b, time);
            b.x += (h.x - b.x) * Math.min(1, dt * 4);
            b.y += (h.y - b.y) * Math.min(1, dt * 4);
            const settled = h.perched && Math.abs(b.x - h.x) < 2 && Math.abs(b.y - h.y) < 2;
            b.sprite.setFrame(settled ? 'gull-perched' : flap).setPosition(b.x, b.y).setFlipX(h.perched ? false : h.dir < 0);
        }
        const carry = this.world.carry;
        const food = carry && FOOD.includes(carry.kind);
        const inZone = here(s, d) && Math.abs(p.y - d.y) < 60 && p.x > d.x0 && p.x < d.x1;
        const b = this.diver;
        if (this.state === 'idle') {
            if (food && inZone && !this.off() && time > this.at) {
                // Where she will be if she keeps on as she goes: it goes to hang over that spot.
                this.state = 'mark';
                this.at = time + TELL_MS;
                this.targetX = Phaser.Math.Clamp(p.x + p.body.velocity.x * TELL_MS / 1000, d.x0 + 6, d.x1 - 6);
                sfx.at(b.x, d.y).gull();
            }
        } else if (this.state === 'mark') {
            // It hangs over the spot.
            b.x += (this.targetX - b.x) * Math.min(1, dt * 5);
            b.y += (this.top + 26 - b.y) * Math.min(1, dt * 5);
            b.sprite.setFrame(flap).setPosition(b.x, b.y);
            if (time > this.at) {
                this.state = 'dive';
                this.diveMs = this.high ? 420 : 230;
                this.at = time + this.diveMs;
                this.from = { x: b.x, y: b.y };
                sfx.at(this.targetX, d.y).gullDive();
            }
        } else if (this.state === 'dive') {
            const k = 1 - Math.max(0, this.at - time) / this.diveMs;
            b.x = this.from.x + (this.targetX - this.from.x) * k;
            b.y = this.from.y + (d.y - 30 - this.from.y) * k * k;
            b.sprite.setFrame('gull-down').setPosition(b.x, b.y);
            if (time > this.at) {
                const got = this.world.carry && FOOD.includes(this.world.carry.kind) && here(s, d) && !s.gliding
                    && Math.abs(p.x - this.targetX) < 17 && p.y > d.y - 30;
                if (got) {
                    const kind = this.world.carry.kind;
                    this.world.carryBox.give();
                    this.loot.setTexture(kind === 'stub' ? 'load-stub' : kind === 'cone' ? 'load-cone' : 'tray').setVisible(true);
                    this.world.say(t('say.hey'), 900);
                    this.stolen = (this.stolen ?? 0) + 1;
                }
                // (Up and off the screen with her cone; missed, back to its perch.)
                sfx.at(this.targetX, d.y).flap();
                if (got) this.flyOff(time, 2800);
                else this.flyBack(time, 2800);
            }
        } else if (this.state === 'up') {
            const L = this.leg, k = Math.min(1, (time - L.t0) / FLIGHT.up);
            b.x = L.from.x + (L.to.x - L.from.x) * k;
            b.y = L.from.y + (L.to.y - L.from.y) * k * (2 - k);
            b.sprite.setFrame(flap).setFlipX(false).setPosition(b.x, b.y);
            this.loot.setPosition(b.x, b.y + 6);
            if (k >= 1) {
                this.loot.setVisible(false);
                b.sprite.setVisible(false);
                this.state = 'away';
                this.at = L.t0 + FLIGHT.up + FLIGHT.away;     // (from when it went: not from when she came back)
            }
        } else if (this.state === 'away') {
            if (time > this.at) {
                this.flyBack(this.at, this.leg.rearm);   // (from where it went off the screen, when it set off back)
            }
        } else if (this.state === 'back') {
            const L = this.leg, h = this.home(b, time), k = Math.min(1, (time - L.t0) / FLIGHT.back), e = k * k * (3 - 2 * k);
            b.x = L.from.x + (h.x - L.from.x) * e;
            b.y = L.from.y + (h.y - L.from.y) * e;
            b.sprite.setFrame(k >= 1 && h.perched ? 'gull-perched' : flap).setFlipX(k < 1 && h.x < L.from.x).setPosition(b.x, b.y);
            if (k >= 1) {
                this.state = 'idle';
                this.at = time + L.rearm;
            }
        } else if (this.state === 'pounce') {
            // Down beside the mess on the deck; a few pecks; away.
            const landed = Math.abs(b.x - this.targetX) < 2 && Math.abs(b.y - d.y) < 2;
            b.x += (this.targetX - b.x) * Math.min(1, dt * 5);
            b.y += (d.y - b.y) * Math.min(1, dt * 5);
            b.sprite.setFrame(landed ? 'gull-perched' : flap).setPosition(b.x, landed ? d.y - (Math.floor(time / 160) % 2) : b.y);
            if (time > this.at && this.fruit) {
                // (Off with the tangerine in its beak.)
                this.fruit.destroy();
                this.fruit = null;
                this.loot.setTexture('tangerine').setVisible(true);
                sfx.at(this.targetX, d.y).flap();
                this.flyOff(time, 10000);
            } else if (time > this.at) {
                this.state = 'idle';
                this.at = time + 1500;
            }
        }
    }
}

// The buffet queue (population: `haz_queue`): six passengers with full trays shuffling from the
// buffet along the aisle, in two threes. Each is a body in her way that she can't walk through (no
// fright: she is held back) and hops, one at a time. For a crew member with a tray in her hands
// they turn aside against the tables and let her by. They come out from behind the buffet and go
// in behind the ice cream counter, round and round.
export class Queue {
    constructor(world, def) {
        const s = world.scene;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, v (m/s), who: [...] }
        this.len = def.x1 - def.x0;
        const offsets = [0, 46, 92, 300, 346, 392];
        this.people = def.who.map((who, i) => {
            const p = world.people.add({ id: `${def.id}_${i + 1}`, who, x: def.x0, y: def.y, route: 'inside', face: 1, owned: true });
            if (p) p.along = (this.len * 0.2 + offsets[i % offsets.length] + Math.floor(i / offsets.length) * 520) % this.len;
            return p;
        }).filter(Boolean);
        this.span = 392;
    }

    // Her cry: they turn aside against the tables, as for a tray, a while.
    heard() {
        const time = this.scene.time.now;
        if (this.people.some(p => this.world.hears(p.x, this.def.y))) this.criedUntil = time + CRY.startleMs;
    }

    update(dt, time) {
        const s = this.scene, her = s.player, d = this.def, P = this.world.people;
        if (!nearby(s, d)) return;
        // A shuffle: a few steps, a wait. While anyone has turned aside for her, the whole line stands still (the user,
        // 2026-11-19: turned away, they slid on forward).
        const tray = !!this.world.carry;
        const yieldsAt = p => (tray && here(s, d) && Math.abs(her.y - d.y) < 60 && Math.abs(her.x - p.x) < 62) || time < (this.criedUntil ?? 0);
        const moving = (time % 2000) < 1150 && !this.people.some(yieldsAt);
        for (const p of this.people) {
            if (moving) p.along = (p.along + d.v * M * 1.74 * dt) % this.len;
            p.x = d.x0 + p.along;
            // Out from behind the buffet, in behind the ice cream counter: faint and out of the way at the ends.
            const edge = Math.min(p.along, this.len - p.along);
            const hidden = edge < 26;
            // For crew with a tray: turned aside, their backs to her, and she squeezes by in front of them. (They went
            // 5 depths back once, behind the café's tables and chairs: the user, 2026-11-19.)
            const yields = yieldsAt(p);
            if (yields !== p.aside) {
                p.aside = yields;
                if (yields) {
                    p.sprite.anims.stop();
                    p.sprite.setFrame(p.meta.back ?? p.meta.stand);
                }
            }
            if (!p.aside) {
                if (moving && P.anim(p, 'walk')) { /* walking */ } else {
                    p.sprite.anims.stop();
                    p.sprite.setFrame(p.meta.stand);
                }
            }
            p.sprite.setAlpha(Phaser.Math.Clamp(edge / 26, 0, 1));
            P.place(p);
            p.blocking = !hidden && !p.aside;
            if (!p.blocking || !here(s, d)) continue;
            // In her way: she is held at their side (over their heads she is clear).
            const dx = her.x - p.x, reach = PLAYER.bodyWidth / 2 + 8;
            if (Math.abs(dx) < reach && her.y > d.y - 42 && Math.abs(her.y - d.y) < 60) {
                const side = dx === 0 ? (her.flipX ? 1 : -1) : Math.sign(dx);
                const to = p.x + side * reach;
                her.body.x += to - her.x;
                her.x = to;
                if (her.body.velocity.x * side < 0) her.body.velocity.x = 0;
                if (time > (this.bumpAt ?? 0)) {
                    this.bumpAt = time + 1500;
                    sfx.at(p.x, d.y).grumble();
                }
            }
        }
    }
}

// A room-service tray left on a hallway's floor outside a "Do Not Disturb" door (population:
// `haz_trays`): the breakfast stewardess's own tray (the user, 2026-11-18: "a normal-looking tray,
// like the one that the breakfast lady hangs out to the doors"), its cloche, glass and vase pieces of
// its picture. Run onto, it shoots on ahead with her standing on it, the way she was going, arms
// wheeling, out of the screen; its dishes fly off behind her; a crash, and the door opens on the
// guest looking after her (3; docs/plan-three-uses.md §1.6). Its clips (`gags` sheet,
// tools/build_gags.py) start from her own run frame 1, 3, 5 or 7 (one each quarter of her stride, 20
// px: one of them always comes with the tray's near end within her hop, `HOP`, px past her toe), the world's
// tray lying where it is until she lands on it, then hidden, the clip's base carrying her. Landed on
// from a jump, or walked onto standing, the hit's own fall. A jump clears it.
// (The ride starts once her toe is this near the tray's near end, px: 22 at first, and the gag began before she touched
// it, the user, 2026-11-23; a little past it still rides.)
const HOP = [-8, 4];
// The tray's picture in pieces (px in `breakfast-tray`, 24 x 12): its base, and what stands on it.
const TRAY_PIECES = { base: [0, 10, 24, 2], cloche: [0, 0, 12, 10], glass: [12, 0, 4, 10], vase: [16, 0, 8, 10] };
// A tray's own things drawn as one picture that must fly apart (each lands on its own side: the two wine glasses, as one
// picture turned they stood one on the other in the air, the user, 2026-11-23): [x, y, w, h] in the picture.
const DISH_PIECES = { 'wine-glasses': [[0, 0, 8, 15], [10, 0, 8, 15]] };
export class Trays {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, door: the id of its DndDoor, flag }
        const tex = s.textures.get('things'), f = tex.get('breakfast-tray');
        for (const [k, [x, y, w, h]] of Object.entries(TRAY_PIECES))
            if (!tex.has(`btray-${k}`)) tex.add(`btray-${k}`, f.sourceIndex, f.cutX + x, f.cutY + y, w, h);
        const tx = Math.round((def.x0 + def.x1) / 2), left = tx - 12, top = def.y - 12;
        const piece = (k, dz) => s.add.image(left + TRAY_PIECES[k][0], top + TRAY_PIECES[k][1], 'things', `btray-${k}`).setOrigin(0, 0).setDepth(D.props + dz);
        // (`def.dishes`: its own things on the trays' base instead of the breakfast's, [the ship's atlas piece, px from its
        // middle]: deck 8's ice bucket and glasses.)
        const own = (frame, dx) => {
            const ship = s.textures.get('shipart'), whole = ship.get(frame);
            const at = tx + dx - Math.round(whole.width / 2), top = def.y - 2 - whole.height;
            return (DISH_PIECES[frame] ?? [[0, 0, whole.width, whole.height]]).map(([x, y, w, h], i) => {
                const name = DISH_PIECES[frame] ? `${frame}#${i}` : frame;
                if (!ship.has(name)) ship.add(name, whole.sourceIndex, whole.cutX + x, whole.cutY + y, w, h);
                return s.add.image(at + x, top + y, 'shipart', name).setOrigin(0, 0).setDepth(D.props + 0.03);
            });
        };
        const base = piece('base', 0.02), dishes = def.dishes ? def.dishes.flatMap(([f, dx]) => own(f, dx)) : ['cloche', 'glass', 'vase'].map(k => piece(k, 0.03));
        this.items = [base, ...dishes];
        this.trays = [{ x: tx, base, dishes }];
        for (const img of this.items) img.setData({ x: img.x, y: img.y });
        world.add(this.items);
        this.armed = true;
    }

    // A tangerine rolled into it: the clatter, and the door opens on nobody; the tray is safe to
    // cross while the guest looks about (docs/plan-three-uses.md §2). It lies there, hers again.
    offered(t) {
        const s = this.scene, d = this.def;
        if (this.gone || !this.armed || this.scattered || t.route !== 'inside' || t.img.x < d.x0 || t.img.x > d.x1 || Math.abs(t.img.y + 3 - d.y) > 10) return false;
        this.armed = false;
        sfx.at(t.img.x, d.y).crash();
        this.rattle();
        s.time.delayedCall(380, () => this.door()?.knock(true, false, true));
        return false;
    }

    door() { return this.world.movers.find(m => m.def?.id === this.def.door); }

    // The dishes off it, tumbling `away`, each to lie on its side on the floor: turned about its middle, a quarter turn
    // and more, its middle half its width over the floor.
    tumble(dishes, away) {
        const s = this.scene, d = this.def;
        dishes.forEach((img, i) => {
            img.setOrigin(0.5, 0.5).setPosition(img.x + img.width / 2, img.y + img.height / 2);
            s.tweens.add({ targets: img, x: img.x + away * (18 + i * 14), y: d.y - img.width / 2, angle: away * (90 + i * 180), duration: 380 + i * 60, ease: 'Quad.easeOut' });
        });
    }

    // A tangerine lying on it (deck 8's, in the ice bucket) goes flying with its things, back the way she came, and lies
    // loose on the floor, hers to pick up (it would hang in the air where the bucket was).
    fruitOff(dir) {
        const s = this.scene, d = this.def, tx = this.trays[0].x;
        // (Raised on its things, not lying on the floor among them: deck 10's rolls out from among its trays by itself.)
        const t = s.tangerines.find(q => q.sprite.active && q.route === 'inside' && Math.abs(q.sprite.x - tx) < 14 && d.y - q.sprite.y >= 4 && d.y - q.sprite.y < 20);
        if (!t) return;
        this.world.save.collected.push(t.id);
        const { x, y } = t.sprite;
        t.glint.destroy();
        t.sprite.destroy();
        t.sprite.active = false;
        s.loose.throw(x, y - 4, -dir * 70, -110, true);
    }

    // (The dishes jump on it.)
    rattle() {
        this.trays.forEach(t => t.dishes.forEach((img, i) => this.scene.tweens.add({ targets: img, y: img.y - 2 - i, duration: 80, yoyo: true, repeat: 2 })));
    }

    // Everything back where it lay (once she has gone).
    restore() {
        this.scattered = false;
        this.items.forEach(img => { this.scene.tweens.killTweensOf(img); img.setOrigin(0, 0).setPosition(img.getData('x'), img.getData('y')).setAngle(0).setVisible(true); });
        this.trays.forEach(t => t.base.setDepth(this.scene.DEPTH.props + 0.02));
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (this.riding) return;
        // (`until`: gone for good once it holds: the Seven Seas' once the lunch is delivered, plan-the-rest §7f.)
        if (this.gone || (d.until && this.world.cond(d.until))) {
            if (!this.gone) { this.gone = true; this.armed = false; this.items.forEach(img => img.setVisible(false)); }
            return;
        }
        // (Far off, at a checkpoint after a ride: ready again.)
        if (!nearby(s, d)) {
            this.armed = true;
            if (this.scattered) this.restore();
            return;
        }
        const onFloor = p.body.blocked.down || p.body.touching.down;
        // (Just come down: her body settles on the floor a frame or two after it touches.)
        if (!onFloor) this.airAt = time;
        const landed = onFloor && time - (this.airAt ?? -1e9) < 150;
        const t = this.trays[0];
        const on = here(s, d) && Math.abs(p.y - d.y) < 2 && onFloor && Math.abs(p.x - t.x) < 14;
        const near = here(s, d) && Math.abs(p.y - d.y) < 2 && onFloor && Math.abs(p.x - t.x) < 80;
        if (!near) {
            if (Math.abs(p.x - d.x) > 3 * M) this.armed = true;
            // (Scattered or ridden off: set straight again once she is well away.)
            if (this.scattered && Math.abs(p.x - d.x) > 8 * M) this.restore();
            return;
        }
        if (!this.armed) return;
        // Landed on it from a jump: off on it the way she jumped (her facing, straight up).
        if (landed && on && !s.isLunging()) {
            const vx = p.body.velocity.x;
            return this.hit(t, s.cache.json.get('gags-meta').tray.clips['7'], Math.abs(vx) > 20 ? Math.sign(vx) : (p.flipX ? -1 : 1));
        }
        // Running at it: at a quarter of her stride (her run frame 1, 3, 5 or 7) with its near end within
        // her hop.
        // (Her run with a load in her hands is her carry run, stride for stride: the load spills as she hops on, 2026-11-23.)
        const dir = p.flipX ? -1 : 1, run = ['her-run', 'her-carry-run'].includes(p.anims.currentAnim?.key) && !s.isLunging();
        if (run) {
            // (Its clip from the quarter of her stride she shows, or the next one: the pose she would show next.)
            const clips = s.cache.json.get('gags-meta').tray.clips, i = p.anims.currentFrame.index - 1;
            const clip = clips[i] ?? clips[(i + 1) % 8];
            if (clip) {
                const gap = (t.x - dir * 12 - (p.x + dir * clip.toe)) * dir;
                if (gap >= HOP[0] && gap <= HOP[1]) return this.hit(t, clip);
            }
            // (Never through it: on it with no hop taken, the fall.)
            if (on) this.hit(null);
            return;
        }
        if (on) this.hit(null);
    }

    // On it: ridden off (`t`, from `clip`, with none on her; `land`: come down on it from a jump,
    // the way it carries her), or the fall; in a lunge, scattered.
    hit(t, clip, land = 0) {
        const s = this.scene, p = s.player, d = this.def;
        this.armed = false;
        sfx.crash();
        if (d.flag) this.world.progress.setFlag(d.flag);
        if (s.isLunging()) {
            // Through it in a lunge: scattered with a clatter, and the door flies open after she
            // has gone.
            this.scattered = true;
            const away = p.body.velocity.x < 0 ? -1 : 1;
            // (The base slid along the floor, the dishes over on their sides on it: the user, 2026-11-23, "scattered items
            // should all be on the floor".)
            this.trays.forEach(t => s.tweens.add({ targets: t.base, x: t.base.x + away * Phaser.Math.Between(8, 20), duration: 260, ease: 'Quad.easeOut' }));
            this.tumble(this.trays.flatMap(t => t.dishes), away);
            this.fruitOff(-away);
            s.time.delayedCall(900, () => this.door()?.knock(true));
            return;
        }
        this.started = false;
        const at = t?.x ?? this.trays[0].x;
        // (With a load in her hands it spills, and the tray plays its gag all the same: the one hit that is both, the
        // user, 2026-11-23, "this tray breaks the vase, but the sliding gag isn't triggered"; every other hit with a load
        // is a spill only.)
        if (this.world.carry) this.world.carryBox.spill(at, false, 'trays', { still: true });
        s.scareContact(at, 'trays', { ride: t ? this.ride(t, clip, land) : null });
        // (Not ridden off: it clatters where it lies, and the door opens on the guest, who looks
        // about.)
        if (this.started) return;
        this.rattle();
        s.time.delayedCall(380, () => this.door()?.knock(true, false, true));
    }

    // 3, the ship scene's `thingGag`. Run onto: her run frame (the clip's frame 0), the hop stretched onto
    // the tray's near end (frames 1 and 2, smoothly, never slower than she ran). Landed on from a jump
    // (`land`, the way it carries her): from the clip's landing on it, frame 3, where she is, the tray
    // skidding the last px under her feet. Then the world's own base under her (her clips are her
    // alone; `trayAt`, the base's place in each frame), carried on faster and faster, the arms wheeling,
    // out of the screen (a door or a wall across the deck stops it: `stopShort`). The dishes fly off
    // behind her as she lands.
    ride(t, clip, land = 0) {
        const s = this.scene, d = this.def, p = s.player, g = GAGS.tray;
        const m = s.cache.json.get('gags-meta'), dir = land || (p.flipX ? -1 : 1), c = m.cell, X = m.tray.x;
        return {
            play: (done) => {
                this.started = true;
                this.riding = true;
                this.scattered = true;
                const x0 = p.x, first = land ? 3 : 0;
                const pic = s.add.sprite(x0, d.y, 'gags', m.anims[clip.key][first]).setOrigin((dir > 0 ? X : c - X) / c, m.floor / c)
                    .setFlipX(dir < 0).setDepth(p.depth);
                this.world.add([pic]);
                this.pic = pic;
                t.base.setDepth(p.depth - 0.01);
                // The base's left px under the clip at x for its frame k, and the clip's x for the base's
                // left px at b.
                const off = k => (dir > 0 ? clip.trayAt[k] - X : X - clip.trayAt[k] - 24);
                const L0 = t.base.x;
                // Where the base goes: run onto, from where it lies (its near end under the hop's
                // landing); landed on, from under her where she came down.
                let B = land ? x0 + off(first) : L0, ahead = 0, v = PLAYER.runSpeed, landed = !!land, hop = 0, skid = 0;
                const wall = s.stopShort(B + 12, B + 12 + dir * 4800, d.y, 16);
                // (Her body moves about 10 px on in the clip's hop; with the tray's near end close the
                // hop is played quicker, so that she never goes slower than she ran; never slower than
                // its own pace, or her first frame would hold while she glides.)
                const quick = land ? 1 : Math.min(2.5, Math.max(1, PLAYER.runSpeed * 0.142 / Math.max(1, (L0 - off(2) - x0) * dir + 10)));
                pic.play({ key: `gags-${clip.key}`, startFrame: first });
                pic.anims.timeScale = quick;
                pic.once(`animationcomplete-gags-${clip.key}`, () => pic.play(`gags-${clip.key}-wheel`));
                const fly = () => {
                    this.tumble(t.dishes, -dir);
                    sfx.at(t.x, d.y).crash();
                    this.fruitOff(dir);
                };
                if (land) fly();
                s.script = (dt) => {
                    // (Its frame of the clip: the wheeling loop is its frames 5 to 8.)
                    const k = pic.anims.currentAnim?.key === `gags-${clip.key}` ? pic.anims.currentFrame.index - 1 : 4 + pic.anims.currentFrame.index;
                    if (k >= 2 && !landed) { landed = true; fly(); }
                    hop += dt;
                    if (k < 2) pic.x = x0 + (L0 - off(2) - x0) * Math.min(1, hop * quick / 0.142);
                    else {
                        pic.anims.timeScale = 1;
                        v = Math.min(g.speed, v + g.accel * dt);
                        ahead += v * dt;
                        pic.x = B + dir * ahead - off(k);
                        // (Landed on: the tray skids from where it lay to under her feet.)
                        skid = Math.min(1, skid + dt / 0.1);
                        const under = B + dir * ahead;
                        t.base.x = land ? L0 + dir * ahead + (under - dir * ahead - L0) * skid : under;
                    }
                    p.x = pic.x;
                    const view = s.cameras.main.worldView;
                    if ((t.base.x + 12 - wall) * dir >= 0 || pic.x < view.x - 70 || pic.x > view.right + 70) {
                        s.script = null;
                        pic.setVisible(false);
                        t.base.setVisible(false);
                        sfx.at(pic.x, d.y).crash();
                        // The guest looks out after her.
                        s.time.delayedCall(250, () => this.door()?.knock(true, false, true));
                        s.time.delayedCall(1100, () => done());
                    }
                };
            },
            show: () => {
                this.pic?.destroy();
                this.pic = null;
                this.riding = false;
                // (Back at her checkpoint behind the fade: the tray and its dishes back where they lay.)
                this.restore();
            },
        };
    }
}
