// Region 7, "Outside" (GAME_DESIGN.md §6.1.3, docs/population.md decks 8-10's balconies, the boat
// walkway and §6.9): the balconies' own things (gusts along the ship's side, gulls perched on the
// rails that swoop on anyone who lingers, laundry lines across a folded partition, balconies with
// someone on them), the boat drill on the walkway, the steward on his rounds in deck 8's hallway;
// and the region's part of the story, mixed into the Story: the ajar balcony doors, the guest
// locked out on his balcony, the security officer at the tender. Places come from maps/world.json
// (`balcony`, `drill`).

import { PLAYER } from '../config.js';
import { sfx } from '../sfx.js';
import { FOOD } from './hazards.js';

const M = 48;
const OUT = 'promenade';            // the outside route's name (src/world/world.js)
const UNIT = 125;                   // a balcony, px
const TOWELS = [0xf68181, 0x8fd3ff, 0xfbb954, 0xb9e04c, 0xffffff];
const nearby = (s, d) => Math.abs(s.player.x - d.x) < 900 && Math.abs(s.player.y - d.y) < 320;
const deckOf = (def, y) => 8 + Math.round((def.bottom - y) / 144);

// Gusts along the ship's side (population: `gust_balc`): every few seconds the towels on the rails
// and the laundry flap (the tell), then the wind blows aft for a moment: in the air on the balconies
// she is carried aft with it. A vault aft goes further; a vault forward, or a climb, falls short.
export class Gusts {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // maps/world.json `balcony`
        this.flappers = [];         // what the wind moves: { img, k: how freely, i }
        def.towels.forEach((t, i) => {
            const img = s.add.image(t.x, t.y, 'rail-towel').setOrigin(0.5, 0).setTint(TOWELS[t.tint % TOWELS.length]).setDepth(D.player + 0.31);
            world.add([img]);
            s.shellSlopes.push({ deck: deckOf(def, t.y + 50), gfx: img });
            this.flappers.push({ img, k: 1, i });
        });
        this.streaks = s.add.graphics().setDepth(D.player + 0.45);
        world.add([this.streaks]);
        this.told = false;
    }

    phase(time) {
        const g = this.def.gust, t = (time / 1000) % g.every;
        return t < g.every - g.blow - g.tell ? 'calm' : t < g.every - g.blow ? 'tell' : 'blow';
    }

    // On the balconies (or in the air over one).
    out() {
        const s = this.scene, p = s.player, d = this.def;
        return s.route === OUT && p.y <= d.bottom + 2 && p.y > d.top - 80 && p.x > d.x0 - 40 && p.x < d.x1 + 40;
    }

    update(dt, time) {
        const s = this.scene, phase = this.phase(time), view = s.cameras.main.worldView;
        const force = phase === 'blow' ? 1 : phase === 'tell' ? 0.5 : 0;
        for (const f of this.flappers) {
            if (f.img.x < view.x - 60 || f.img.x > view.right + 60) continue;
            // (Hung by its top: blown aft, its foot swings aft and it flutters.)
            const flutter = Math.sin(time / (force ? 55 : 700) + f.i * 1.7);
            f.img.setAngle(force ? -f.k * force * (16 + flutter * 9) : flutter * 1.5 * f.k);
        }
        const g = this.streaks.clear();
        const out = this.out();
        if (phase === 'calm') this.told = false;
        else if (out && !this.told) {
            this.told = true;
            sfx.whoosh();
        }
        if (phase !== 'blow' || !out) return;
        // The wind itself: streaks of spray going aft across the view.
        for (let i = 0; i < 9; i++) {
            const x = view.x - 40 + ((time * 0.75 + i * 149) % (view.width + 80));
            const y = view.y + 24 + ((i * 67) % (view.height - 48));
            const len = 14 + (i * 7) % 16;
            g.fillStyle(0xffffff, 0.75).fillRect(x, y, len, 1);
            g.fillStyle(0xffffff, 0.4).fillRect(x - 6, y, 6, 1).fillRect(x + len + 3, y + 1, 4, 1);
        }
    }

    // Called by the scene each frame of play, after her own speed is set.
    push(dt, onFloor) {
        const s = this.scene, p = s.player;
        if (onFloor || s.mode !== 'play' || this.phase(s.time.now) !== 'blow' || !this.out()) return;
        const dx = this.def.gust.drift * dt;
        p.x += dx;
        p.body.x += dx;
    }
}

// A gull perched on a balcony's rail (population: `gull_8`...): she lingers near it for two
// seconds and it goes up; its shadow shows where she stands, and a second later it comes down on
// that spot: "Swooped" (or, if she carries food, the food is gone). Keeping on the move is the way.
export class PerchGull {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, y: the rail's top, floor }
        this.sprite = s.add.image(def.x, def.y, 'things', 'gull-perched').setOrigin(0.5, 1).setDepth(D.player + 0.34);
        this.shadow = s.add.ellipse(def.x, def.floor - 1, 22, 5, 0x2e222f, 0.45).setDepth(D.exterior + 0.14).setVisible(false);
        world.add([this.sprite, this.shadow]);
        s.shellSlopes.push({ deck: deckOf(world.data.balcony, def.floor), gfx: this.sprite });
        this.state = 'perched';
        this.linger = 0;
        this.at = 0;
        this.x = def.x;
        this.y = def.y;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (!nearby(s, d)) return;
        const frames = s.textures.get('things');
        const flap = Math.floor(time / 130) % 2 && frames.has('gull-down') ? 'gull-down' : 'gull-up';
        const near = s.route === OUT && s.mode === 'play' && Math.abs(p.y - d.floor) < 70 && Math.abs(p.x - d.x) < 2.6 * M;
        if (this.state === 'perched') {
            this.linger = near ? this.linger + dt : Math.max(0, this.linger - dt * 2);
            this.sprite.setFrame('gull-perched').setPosition(d.x, d.y - (this.linger > 1.2 ? Math.floor(time / 110) % 2 : 0));
            if (near) this.sprite.setFlipX(p.x < d.x);
            if (this.linger > 2 && time > this.at) {
                this.state = 'mark';
                this.at = time + 1000;
                this.targetX = p.x;
                this.shadow.setPosition(this.targetX, d.floor - 1).setVisible(true).setScale(0.4);
                s.tweens.add({ targets: this.shadow, scale: 1.2, duration: 1000 });
                sfx.whoosh();
            }
        } else if (this.state === 'mark') {
            // It hangs over the spot.
            this.x += (this.targetX - this.x) * Math.min(1, dt * 5);
            this.y += (d.floor - 108 - this.y) * Math.min(1, dt * 5);
            this.sprite.setFrame(flap).setPosition(this.x, this.y).setFlipX(this.targetX < this.x);
            if (time > this.at) {
                this.state = 'dive';
                this.at = time + 230;
                this.from = { x: this.x, y: this.y };
            }
        } else if (this.state === 'dive') {
            const k = 1 - Math.max(0, this.at - time) / 230;
            this.x = this.from.x + (this.targetX - this.from.x) * k;
            this.y = this.from.y + (d.floor - 30 - this.from.y) * k * k;
            this.sprite.setFrame('gull-down').setPosition(this.x, this.y);
            if (time > this.at) {
                this.shadow.setVisible(false);
                const hit = s.route === OUT && s.mode === 'play' && Math.abs(p.x - this.targetX) < 17
                    && p.y > d.floor - 30 && p.y < d.floor + 8;
                if (hit) {
                    const carry = this.world.carry;
                    if (carry && FOOD.includes(carry.kind)) {
                        this.world.carryBox.give();
                        this.world.say('Гей!', 900);
                        sfx.pickup();
                    } else s.scareContact(this.targetX + (p.flipX ? -8 : 8), 'swooped');
                }
                this.state = 'back';
                this.at = time + 2600;
            }
        } else {
            // Up, round, and back to its rail.
            this.x += (d.x - this.x) * Math.min(1, dt * 2.2);
            this.y += (d.y - this.y) * Math.min(1, dt * 2.2) - (Math.abs(this.x - d.x) > 20 ? 50 * dt : 0);
            const home = Math.abs(this.x - d.x) < 2 && Math.abs(this.y - d.y) < 2;
            this.sprite.setFrame(flap).setPosition(this.x, this.y).setFlipX(d.x < this.x);
            if (home) {
                this.state = 'perched';
                this.linger = 0;
                this.x = d.x;
                this.y = d.y;
            }
        }
    }
}

// A laundry line (population: `haz_line`): two balconies made one, the partition between them
// folded back against the wall, and a line of washing strung across the gap from the ceiling's
// edge. No vault there (nothing to kick off): she goes under it on hands and knees. It flaps
// before a gust.
export class Laundry {
    constructor(world, def, gusts) {
        const s = world.scene, D = s.DEPTH, x = def.x, y = def.y;
        const deck = deckOf(world.data.balcony, y);
        this.def = def;
        // Over the partition the ship's side has drawn there: the recess's wall and the glass
        // front run on; the panel, folded flat against the wall.
        const g = s.add.graphics().setDepth(D.exterior + 0.06);
        g.fillStyle(0x5d6f86, 1).fillRect(x - 3, y - 89, 6, 42);
        g.fillStyle(0xa3c4d4, 1).fillRect(x - 3, y - 48, 6, 40);
        g.fillStyle(0xc7e4ef, 1).fillRect(x - 3, y - 36, 6, 1);
        g.fillStyle(0xf4f4f4, 1).fillRect(x - 3, y - 50, 6, 3);
        g.fillStyle(0xf4f4f4, 1).fillRect(x + 3, y - 106, 9, 2).fillRect(x + 10, y - 104, 2, 57);
        g.fillStyle(0xc7dcd0, 1).fillRect(x + 12, y - 104, 1, 57);
        // The line, from hook to hook under the ceiling's edge, sagging.
        const line = s.add.graphics().setDepth(D.player + 0.05);
        const sag = dx => y - 110 + Math.round(9 * (1 - (dx / 54) ** 2));
        line.fillStyle(0xf4f4f4, 1).fillRect(x - 56, y - 112, 3, 3).fillRect(x + 53, y - 112, 3, 3);
        for (let dx = -54; dx <= 54; dx++) line.fillStyle(0x625565, 1).fillRect(x + dx, sag(dx), 1, 1);
        const items = [g, line];
        // The washing: long things in the middle (down to her knees), small ones at the ends.
        const wash = [['cloth-sock', -46], ['cloth-tee', -33], ['cloth-towel', -13], ['cloth-dress', 7], ['cloth-towel-b', 27], ['cloth-shorts', 45]];
        wash.forEach(([key, dx], i) => {
            const img = s.add.image(x + dx, sag(dx), key).setOrigin(0.5, 0).setDepth(D.player + 0.05 + i * 0.001);
            items.push(img);
            gusts.flappers.push({ img, k: 0.45, i: i + def.x });
        });
        world.add(items);
        items.forEach(i => s.shellSlopes.push({ deck, gfx: i }));
        // Above her on hands and knees it is solid.
        const zone = s.add.zone(x, y - 30, 30, 98).setOrigin(0.5, 1);
        s.physics.add.existing(zone, true);
        world.low.push({ route: OUT, x0: x - 15 - 18, x1: x + 15 + 18, y });
        world.lows.push({ id: def.id, route: OUT, zone, items: [] });
    }

    update() {}
}

// A balcony with someone on it, a "Do Not Disturb" card on each of its partitions (population:
// `haz_sunbather`): she lands on it: "Startled". The way past it is by another deck.
export class Occupied {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, frame }
        const img = world.image((def.x0 + def.x1) / 2 + 3, def.y, def.frame).setOrigin(0.5, 1).setDepth(D.exterior + 0.12);
        const items = [img];
        for (const x of [def.x0 + 3, def.x1 + 3]) {
            items.push(s.add.image(x, def.y - 76, 'dnd-tag').setOrigin(0.5, 0).setDepth(D.player + 0.32));
        }
        this.bang = s.add.text(img.x, def.y - 62, '!', {
            fontFamily: 'Verdana, sans-serif', fontSize: '12px', fontStyle: 'bold', color: '#e83b3b', stroke: '#ffffff', strokeThickness: 3, resolution: 4,
        }).setOrigin(0.5, 1).setDepth(D.fx).setVisible(false);
        world.add([...items, this.bang]);
        const deck = deckOf(world.data.balcony, def.y);
        items.forEach(i => s.shellSlopes.push({ deck, gfx: i }));
        this.d = { x: img.x, y: def.y };
        this.hit = false;
    }

    update() {
        const s = this.scene, p = s.player, d = this.def;
        if (!nearby(s, this.d)) return;
        const onFloor = p.body.blocked.down || p.body.touching.down;
        const on = s.route === OUT && s.mode === 'play' && onFloor && Math.abs(p.y - d.y) < 2 && p.x > d.x0 + 6 && p.x < d.x1;
        if (!on) {
            if (s.mode === 'play') this.hit = false;
            return;
        }
        if (this.hit) return;
        this.hit = true;
        this.bang.setVisible(true);
        s.time.delayedCall(1300, () => this.bang.setVisible(false));
        s.scareContact(this.d.x, 'startled');
    }
}

// The boat drill on the walkway (population: `haz_drill`): a rescue boat on its falls in the gap
// between the boats. Hoisted right up she walks under it; every few seconds, after a jolt and the
// winch's lamp (the tell), the crew lower it onto the walkway and hoist it again. Under it as it
// comes down: "Bumped". Down, it is in her way.
export class DrillBoat {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x: its forward end, y: the walkway, top: deck 8's floor, period, down, tell }
        const tex = s.textures.get('rescue-boat').getSourceImage();
        this.w = tex.width;
        this.h = tex.height;
        this.cx = def.x + this.w / 2;
        this.up = def.top + 6;
        this.low = def.y - 8 - this.h;
        this.d = { x: this.cx, y: def.y };
        // The davit's two arms under the overhang, a lamp on the forward one.
        const arms = s.add.graphics().setDepth(D.exterior + 0.08);
        this.hooks = [def.x + Math.round(this.w * 0.2), def.x + Math.round(this.w * 0.8)];
        for (const hx of this.hooks) {
            arms.fillStyle(0xf7f8f8, 1).fillRect(hx - 14, def.top + 16, 28, 6);
            arms.fillStyle(0xd3e1da, 1).fillRect(hx - 14, def.top + 21, 28, 1);
        }
        this.lamp = s.add.rectangle(this.hooks[0] - 18, def.top + 19, 4, 4, 0xfbb954).setDepth(D.player + 0.07);
        this.falls = s.add.graphics().setDepth(D.player + 0.055);
        this.boat = s.add.image(def.x, this.up, 'rescue-boat').setOrigin(0).setDepth(D.player + 0.06);
        this.shade = s.add.ellipse(this.cx, def.y - 1, this.w - 30, 5, 0x2e222f, 0.3).setDepth(D.exterior + 0.14);
        const items = [arms, this.lamp, this.falls, this.boat, this.shade];
        world.add(items);
        items.forEach(i => s.shellSlopes.push({ deck: [6, 7], gfx: i }));
        this.k = 0;
    }

    // How far down it is at `time`, 0 hoisted to 1 on the walkway; and whether the tell is on.
    at(time) {
        const d = this.def, t = (time / 1000) % d.period, lower = 1.1, hoist = 1.6;
        if (t < d.tell) return { k: 0, tell: true, t };
        const u = t - d.tell;
        if (u < lower) return { k: u / lower, coming: true };
        if (u < lower + d.down) return { k: 1 };
        if (u < lower + d.down + hoist) return { k: 1 - (u - lower - d.down) / hoist };
        return { k: 0 };
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (!nearby(s, this.d)) return;
        const a = this.at(time);
        const ease = a.k * a.k * (3 - 2 * a.k);
        const y = Math.round(this.up + (this.low - this.up) * ease) + (a.tell ? (Math.floor(time / 70) % 2) : 0);
        this.boat.y = y;
        this.lamp.setFillStyle(a.tell || a.coming ? (Math.floor(time / 140) % 2 ? 0xe83b3b : 0xfbb954) : 0x625565);
        this.shade.setScale(0.5 + 0.5 * ease, 1).setAlpha(0.15 + 0.3 * ease);
        const g = this.falls.clear();
        for (const hx of this.hooks) g.fillStyle(0x7a7480, 1).fillRect(hx, d.top + 22, 1, Math.max(0, y + 6 - d.top - 22));
        if (a.tell && !this.rang) {
            this.rang = true;
            sfx.rattle();
        } else if (!a.tell) this.rang = false;
        // Her under it.
        if (s.route !== OUT || s.mode !== 'play' || Math.abs(p.y - d.y) > 30) return;
        const keel = y + this.h - 4, head = p.y - PLAYER.bodyHeight;
        const half = this.w / 2 - 14 + PLAYER.bodyWidth / 2;
        if (Math.abs(p.x - this.cx) >= half || head >= keel) return;
        if (a.coming) {
            s.scareContact(this.cx, 'bumped');
            return;
        }
        // Down, or still too low on its way up: she is held at its end.
        const side = p.x < this.cx ? -1 : 1;
        const to = this.cx + side * half;
        p.body.x += to - p.x;
        p.x = to;
        if (p.body.velocity.x * side < 0) p.body.velocity.x = 0;
    }
}

// The steward on his rounds (population: `haz_steward_rounds`): up and down deck 8's hallway
// behind his cart. The two of them fill it: she is held back, and carried along if he comes at her
// (never a fright). At some doors he pulls the cart in and knocks: for a few seconds the way is free.
export class Rounds {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, v (m/s), stops: [x], wait (s), who }
        this.p = world.people.add({ id: def.id, who: def.who, x: def.x0, y: def.y, route: 'inside', face: 1 });
        this.cart = s.add.image(def.x0, def.y, 'shipart', 'service-cart').setOrigin(0.5, 1).setDepth(D.props + 0.06);
        this.swan = s.add.image(def.x0, def.y - 28, 'shipart', 'towel-swan').setOrigin(0.5, 1).setDepth(D.props + 0.061);
        this.dark = s.add.rectangle(0, def.y - 2, 28, 70, 0x2e222f).setOrigin(0.5, 1).setDepth(D.decor + 0.105).setVisible(false);
        world.add([this.cart, this.swan, this.dark]);
        this.x = def.x0 + 40;
        this.dir = 1;
        this.until = 0;             // waiting (at an end, in a doorway) until then
        this.aside = false;
        this.depth = this.p?.sprite.depth ?? 0;
        this.d = { x: (def.x0 + def.x1) / 2, y: def.y };
    }

    update(dt, time) {
        const s = this.scene, her = s.player, d = this.def, P = this.world.people, p = this.p;
        if (!p || !nearby(s, this.d)) return;
        const D = s.DEPTH;
        if (time >= this.until) {
            if (this.aside) {
                this.aside = false;
                this.dark.setVisible(false);
                sfx.door();
            }
            const before = this.x;
            this.x += this.dir * d.v * M * dt;
            if (this.x >= d.x1) { this.x = d.x1; this.dir = -1; this.until = time + 900; }
            else if (this.x <= d.x0) { this.x = d.x0; this.dir = 1; this.until = time + 900; }
            for (const stop of d.stops) {
                // (His cart's nose at the door.)
                const nose = stop - this.dir * 26;
                if ((before - nose) * (this.x - nose) <= 0 && before !== this.x && time >= this.until) {
                    this.x = nose;
                    this.until = time + d.wait * 1000;
                    this.aside = true;
                    this.dark.setPosition(stop, d.y - 2).setVisible(true);
                    sfx.door();
                    break;
                }
            }
        }
        const moving = time >= this.until;
        p.x = this.x;
        p.dir = this.dir;
        if (this.aside) {
            // In the doorway: the cart's nose in, him behind it with his back to us.
            p.x = this.x + this.dir * 26 - this.dir * 9;
            p.sprite.anims.stop();
            p.sprite.setFrame(p.meta.back ?? p.meta.stand).setDepth(D.decor + 0.12).setScale(0.94);
            this.cart.setPosition(this.x + this.dir * 26 + this.dir * 7, d.y - 2).setDepth(D.decor + 0.11).setScale(0.9);
        } else {
            p.sprite.setDepth(this.depth).setScale(1);
            if (moving && (P.anim(p, 'push') || P.anim(p, 'walk'))) { /* walking */ } else {
                p.sprite.anims.stop();
                p.sprite.setFrame(p.meta.stand);
            }
            this.cart.setPosition(this.x + this.dir * 26, d.y).setDepth(D.props + 0.06).setScale(1).setFlipX(this.dir < 0);
        }
        this.swan.setPosition(this.cart.x, this.cart.y - 28 * this.cart.scaleY).setDepth(this.cart.depth + 0.001).setScale(this.cart.scaleX)
            .setFlipX(this.dir < 0);
        P.place(p);
        if (this.aside || s.route !== 'inside' || (s.mode !== 'play' && s.mode !== 'push') || Math.abs(her.y - d.y) > 100) return;
        // Across the hallway: his back to the cart's nose.
        const a = Math.min(this.x - this.dir * 15, this.x + this.dir * 39), b = Math.max(this.x - this.dir * 15, this.x + this.dir * 39);
        const half = PLAYER.bodyWidth / 2;
        if (her.x <= a - half || her.x >= b + half) return;
        const side = her.x < (a + b) / 2 ? -1 : 1;
        const to = side < 0 ? a - half : b + half;
        her.body.x += to - her.x;
        her.x = to;
        if (her.body.velocity.x * side < 0) her.body.velocity.x = 0;
        if (time > (this.bumpAt ?? 0)) {
            this.bumpAt = time + 900;
            sfx.land();
        }
    }
}

// --- The region's part of the story (mixed into the Story) --------------------------------------

export const outside = {
    setupOutside() {
        const s = this.scene, w = this.world, B = w.data.balcony, D = s.DEPTH;
        if (!B) return;
        this.outsideTextures();
        this.gusts = w.gusts = new Gusts(w, B);
        w.movers.push(this.gusts);
        for (const f of B.furniture) {
            const img = s.add.image(f.x, f.y, 'shipart', f.frame).setOrigin(0.5, 1).setFlipX(!!f.flip).setDepth(D.exterior + 0.09);
            w.add([img]);
            s.shellSlopes.push({ deck: deckOf(B, f.y), gfx: img });
        }
        for (const g of B.perch) w.movers.push(new PerchGull(w, g));
        for (const l of B.lines) w.movers.push(new Laundry(w, l, this.gusts));
        for (const o of B.occupied) w.movers.push(new Occupied(w, o));
        if (w.data.drill) w.movers.push(this.drill = new DrillBoat(w, w.data.drill));
        // The ajar balcony doors: the glass slid aside, the cabin's light, a curtain blowing out.
        this.ajar = {};
        for (const room of Object.values(w.rooms)) {
            for (const d of room.doors ?? []) {
                if (d.kind !== 'balcony') continue;
                const door = s.add.image(d.outX, d.outY - 8, 'balcony-ajar').setOrigin(0.5, 1).setDepth(D.exterior + 0.07);
                const curtain = s.add.image(d.outX + 10, d.outY - 100, 'balcony-curtain').setOrigin(0.5, 0).setDepth(D.exterior + 0.075);
                w.add([door, curtain]);
                const deck = deckOf(B, d.outY);
                s.shellSlopes.push({ deck, gfx: door }, { deck, gfx: curtain });
                this.gusts.flappers.push({ img: curtain, k: 0.5, i: d.outX });
                this.ajar[room.id] = [door, curtain];
            }
        }
        this.refreshOutside();
    },

    outsideTextures() {
        const s = this.scene;
        const make = (key, w, h, draw) => {
            if (s.textures.exists(key)) return;
            const g = s.make.graphics({ x: 0, y: 0 }, false);
            draw(g);
            g.generateTexture(key, w, h);
            g.destroy();
        };
        // A towel over a rail: white, tinted by the game; two stripes.
        make('rail-towel', 12, 24, g => {
            g.fillStyle(0xffffff, 1).fillRect(0, 0, 12, 23).fillRect(1, 23, 10, 1);
            g.fillStyle(0xc7dcd0, 1).fillRect(0, 4, 12, 2).fillRect(0, 17, 12, 2).fillRect(11, 0, 1, 23);
        });
        const cloth = (key, w, h, colour, shade, extra) => make(key, w, h, g => {
            g.fillStyle(0x625565, 1).fillRect(1, 0, 2, 3).fillRect(w - 3, 0, 2, 3);        // the pegs
            g.fillStyle(colour, 1).fillRect(0, 2, w, h - 2);
            g.fillStyle(shade, 1).fillRect(w - 2, 2, 2, h - 2).fillRect(0, h - 2, w, 2);
            extra?.(g);
        });
        cloth('cloth-towel', 17, 69, 0xf68181, 0xc34d6d, g => g.fillStyle(0xffffff, 1).fillRect(0, 10, 17, 3).fillRect(0, 56, 17, 3));
        cloth('cloth-towel-b', 16, 64, 0x4d9be6, 0x3a6fb5, g => g.fillStyle(0xfbff86, 1).fillRect(0, 20, 16, 4).fillRect(0, 30, 16, 4));
        cloth('cloth-dress', 16, 68, 0xfbb954, 0xe6904e, g => {
            g.fillStyle(0xffffff, 1);
            for (let y = 8; y < 64; y += 9) g.fillRect(3 + (y % 2) * 6, y, 2, 2).fillRect(10 - (y % 2) * 6, y + 4, 2, 2);
        });
        cloth('cloth-tee', 15, 20, 0xffffff, 0xc7dcd0, g => g.fillStyle(0x1ebc73, 1).fillRect(4, 8, 7, 5));
        cloth('cloth-shorts', 13, 15, 0x1ebc73, 0x239063, g => g.fillStyle(0x239063, 1).fillRect(6, 8, 1, 7));
        cloth('cloth-sock', 6, 14, 0xffffff, 0xc7dcd0, g => g.fillStyle(0xe83b3b, 1).fillRect(0, 4, 6, 2));
        // A "Do Not Disturb" card hung on a partition.
        make('dnd-tag', 9, 17, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 2, 9, 15).fillRect(3, 0, 3, 3);
            g.fillStyle(0xe83b3b, 1).fillRect(1, 3, 7, 13);
            g.fillStyle(0xffffff, 1).fillRect(4, 1, 1, 2).fillRect(2, 6, 5, 2).fillRect(2, 10, 5, 1).fillRect(2, 12, 5, 1);
        });
        // An ajar balcony door: the glass slid aside on the lit cabin.
        make('balcony-ajar', 34, 98, g => {
            g.fillStyle(0xf4f4f4, 1).fillRect(0, 0, 34, 98);
            g.fillStyle(0xfdf0c8, 1).fillRect(2, 2, 30, 96);
            g.fillStyle(0xf9c22b, 0.35).fillRect(2, 60, 30, 38);
            g.fillStyle(0x8fd3ff, 0.55).fillRect(22, 2, 10, 96);          // the glass, slid aside
            g.fillStyle(0xffffff, 0.8).fillRect(24, 6, 1, 80);
            g.fillStyle(0xc7dcd0, 1).fillRect(21, 2, 1, 96);
        });
        make('balcony-curtain', 12, 78, g => {
            g.fillStyle(0xffffff, 0.92).fillRect(0, 0, 12, 76).fillRect(1, 76, 10, 2);
            g.fillStyle(0xc7dcd0, 1).fillRect(3, 0, 1, 76).fillRect(8, 0, 1, 76);
        });
    },

    // The guest's balcony door is shut until she has let him in.
    refreshOutside() {
        const guest = this.ajar?.guest10;
        if (guest) guest.forEach(i => i.setVisible(this.P.has('guest')));
    },

    updateOutside(dt, time) {
        const s = this.scene, w = this.world, her = s.player;
        if (!w.data.balcony) return;
        this.rivalOnWalkway(time);
        // The guest on his balcony waves at her when she is in sight of him.
        const g = this.who('npc_balcony_guest');
        if (g?.on && s.route === OUT && g.state !== 'acting') {
            const near = Math.abs(her.y - g.y) < 150 && Math.abs(her.x - g.x) < 6 * M;
            if (near) {
                g.dir = her.x < g.x ? -1 : 1;
                this.people.place(g);
                if (time > (this.guestWaveAt ?? 0)) {
                    this.guestWaveAt = time + 3400;
                    this.people.play(g, 'wave');
                }
            }
        }
        // How the partitions are crossed, the first time she is out on a balcony in the socks.
        if (s.route === OUT && s.mode === 'play' && this.P.knows('socks') && !w.save.seen.includes('hint-balcony')
            && her.y <= w.data.balcony.bottom + 2 && (her.body.blocked.down || her.body.touching.down)) {
            w.save.seen.push('hint-balcony');
            w.hint('Partition: jump, jump again to vault it. With ↑ held: up its pole');
        }
    },

    // The security officer on the boat walkway, looking into a tender (population: `riv_walkway`):
    // once, as she comes along; he sees her, salutes, and hurries off aft.
    rivalOnWalkway(time) {
        const s = this.scene, r = this.who('riv_walkway'), her = s.player;
        if (!r?.on || this.rivWalking || s.route !== OUT || s.mode !== 'play') return;
        if (Math.abs(her.y - r.y) > 6 || Math.abs(her.x - r.x) > 3.4 * M) return;
        this.rivWalking = true;
        r.state = 'acting';
        r.dir = her.x < r.x ? -1 : 1;
        this.people.place(r);
        r.sprite.anims.stop();
        r.sprite.setFrame(r.meta.stand);
        const bang = s.add.text(r.x, r.y - 64, '!', {
            fontFamily: 'Verdana, sans-serif', fontSize: '12px', fontStyle: 'bold', color: '#2e222f', stroke: '#ffffff', strokeThickness: 3, resolution: 4,
        }).setOrigin(0.5, 1).setDepth(s.DEPTH.fx);
        this.world.add([bang]);
        s.time.delayedCall(700, () => {
            bang.destroy();
            r.dir = 1;
            this.people.place(r);
            this.people.anim(r, 'walk', { speed: 1.8 });
            const end = r.x + 7 * M;
            s.tweens.add({
                targets: r, x: end, duration: 2100,
                onUpdate: () => { this.people.place(r); r.sprite.setAlpha(Math.min(1, (end - r.x) / 60)); },
                onComplete: () => { this.P.setFlag('riv_walkway'); },
            });
        });
    },

    // She opens his balcony door from inside (population: `scn_guest`): he comes in, thanks her,
    // and gives her the book he was reading out there: the seventh. His balcony door stays ajar.
    guestIn() {
        const s = this.scene, w = this.world, her = s.player, room = w.rooms.guest10;
        const g = this.who('npc_guest_in');
        if (!room || !g) {
            w.giveBook(7);
            return;
        }
        const door = room.doors.find(d => d.kind === 'balcony').x, rest = g.x;
        w.cut(async () => {
            sfx.door();
            g.state = 'acting';
            g.x = door + 6;
            g.dir = -1;
            this.people.place(g);
            g.sprite.setAlpha(0);
            // She steps back from the door; he comes in from the balcony.
            her.setFlipX(false);
            s.pose('run', 1);
            await w.tween({ targets: her, x: door - 44, duration: 420 });
            her.body.reset(her.x, her.y);
            s.pose('stand');
            this.people.anim(g, 'walk');
            await w.tween({ targets: g.sprite, alpha: 1, duration: 200 });
            await w.tween({ targets: g, x: door - 14, duration: 500, onUpdate: () => this.people.place(g) });
            await this.people.play(g, 'thanks');
            await w.wait(150);
            await w.handOver(g, '@book-7', () => w.giveBook(7));
            await w.wait(250);
            // And goes to sit down with a sigh: at home again.
            this.people.anim(g, 'walk');
            g.state = 'acting';
            await w.tween({ targets: g, x: rest, duration: Math.abs(g.x - rest) * 14, onUpdate: () => this.people.place(g) });
            this.people.idle(g);
        });
    },
};
