// Region 8, "Top deck + funnel" (GAME_DESIGN.md §6.1.3, docs/population.md deck 12, the roof, the
// funnel and §6.8): deck 12's own things (the old lady's sunbed across the sun deck's walk, the
// basketballs out of the sports court, Teppanyaki's flares, the gulls on the bow), the funnel's
// (gusts and circling gulls on its stairway, the horn, the telescope), and the region's part of
// the story, mixed into the Story: the old lady's mojito, the engineer's coffee, the horn and what
// it sets off (the security officer drops his card, the old lady bolts and leaves her parasol and
// her book, the gulls leave the bow, Bumbot runs for it), the engineer's book, the court's quirk.
// Places come from maps/world.json (`topdeck`).

import { PLAYER } from '../config.js';
import { sfx } from '../sfx.js';
import { writeSave } from '../save.js';
import { Gusts, PerchGull } from './outside.js';

const M = 48;
const HALF = PLAYER.height / 2;
const near = (s, x, y, dx = 900, dy = 320) => Math.abs(s.player.x - x) < dx && Math.abs(s.player.y - y) < dy;
const onFloor = body => body.blocked.down || body.touching.down;

// The old lady on her sunbed across the walk (population: `npc_oldlady`): a block too wide and too
// high for a tray's hop; a jump clears it (landing on it she slides on over: nobody stands on the
// old lady). She glares at whoever comes near, and dozes once she has had her mojito.
export class OldLady {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;
        // The sunbed stays when she has gone; her bags and her towel go with her.
        const bed = s.add.image(def.x, def.y, 'sunbed').setOrigin(0.5, 1).setDepth(D.props + 0.03);
        const bag = s.add.image(def.x - 39, def.y, 'shipart', 'beach-bag').setOrigin(0.5, 1).setDepth(D.props + 0.06);
        const duffel = s.add.image(def.x + 30, def.y, 'shipart', 'duffel-bag').setOrigin(0.5, 1).setDepth(D.props + 0.02);
        const towel = s.add.image(def.x + 22, def.y - 11, 'rail-towel').setOrigin(0.5, 0).setTint(0xfbb954).setAngle(-90).setDepth(D.props + 0.04);
        world.add([bed, bag, duffel, towel]);
        const zone = s.add.zone(def.x, def.y, def.half * 2, def.tall).setOrigin(0.5, 1);
        s.physics.add.existing(zone, true);
        world.things.push({ id: 'prop_sunbed', x: def.x, y: def.y, route: 'inside', items: [bed] });
        const block = { id: 'blk_oldlady', x: def.x, y: def.y, route: 'inside', items: [bag, duffel, towel], zone, until: 'flag:horn' };
        world.things.push(block);
        world.solids.push(block);
        this.zone = zone;
        this.glaring = false;
        this.zAt = 0;
    }

    get lady() { return this.world.people.byId.npc_oldlady; }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def, L = this.lady, people = this.world.people;
        if (!L?.on || !near(s, d.x, d.y)) return;
        if (L.state === 'acting' && !this.glaring) return;          // in a scene of her own
        const close = s.route === 'inside' && Math.abs(p.y - d.y) < 60 && Math.abs(p.x - d.x) < 4 * M;
        if (this.world.progress.has('lady')) {
            if (L.idle !== 'dozing' || L.still) {
                L.idle = 'dozing';
                L.still = '';
                this.glaring = false;
                people.idle(L);
            }
            if (time > this.zAt) {
                this.zAt = time + 1500;
                const z = s.add.text(L.x + 8, d.y - 58, 'z', { fontFamily: 'Verdana, sans-serif', fontSize: '8px', fontStyle: 'bold', color: '#4d65b4', resolution: 4 })
                    .setOrigin(0.5).setDepth(s.DEPTH.fx);
                this.world.add([z]);
                s.tweens.add({ targets: z, x: z.x + 10, y: z.y - 18, alpha: 0, scale: 1.6, duration: 1400, onComplete: () => z.destroy() });
            }
        } else if (close && !this.glaring) {
            this.glare();
        } else if (!close && this.glaring && L.state !== 'acting') {
            this.glaring = false;
            L.still = '';
            people.idle(L);
        }
        // Landing on her: on over, the way she was going.
        const body = p.body;
        if (s.mode === 'play' && s.route === 'inside' && this.zone.body.enable && onFloor(body)
            && Math.abs(p.x - d.x) < d.half + PLAYER.bodyWidth / 2 && Math.abs(body.bottom - (d.y - d.tall)) < 3) {
            this.way ??= Math.abs(body.velocity.x) > 20 ? Math.sign(body.velocity.x) : p.flipX ? -1 : 1;
            body.velocity.x = this.way * 170;
            if (!this.world.progress.has('lady') && time > (this.hmphAt ?? 0)) {
                this.hmphAt = time + 1600;
                this.glare();
            }
        } else {
            this.way = null;
        }
    }

    glare() {
        const L = this.lady;
        this.glaring = true;
        L.still = 'glare';
        this.world.people.play(L, 'glare');
    }
}

// Basketballs out of the sports court (population: `haz_balls`): every few seconds one comes off a
// hoop's rim (the rattle is the tell), bounces twice along the walk and rolls back: "Bonked". The
// two hoops take turns.
export class Balls {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x: the hoop, y, dir, reach, period, offset }
        this.rim = { x: def.x + def.dir * 24, y: def.y - 93 };
        this.ball = s.add.image(this.rim.x, this.rim.y, 'shipart', 'basketball').setDepth(D.player + 0.03).setVisible(false);
        this.shadow = s.add.ellipse(this.rim.x, def.y - 1, 10, 3, 0x2e222f, 0.4).setDepth(D.props + 0.01).setVisible(false);
        world.add([this.ball, this.shadow]);
        this.hitAt = 0;
    }

    // Where the ball is `t` s into its turn: { x, y: px over the floor, a: alpha } or null.
    at(t) {
        const d = this.def, x0 = this.rim.x + d.dir * 8, R = d.reach * d.dir, drop = d.y - this.rim.y - 5;
        if (t < 0.5) return { x: this.rim.x + Math.sin(t * 40) * 2, y: drop + 4, a: 1, tell: true };
        t -= 0.5;
        if (t < 0.42) return { x: this.rim.x + d.dir * 8 * (t / 0.42), y: drop * (1 - (t / 0.42) ** 2), a: 1 };
        t -= 0.42;
        const hop = (t0, len, h, xa, xb) => {
            const k = (t - t0) / len;
            return { x: x0 + R * (xa + (xb - xa) * k), y: 4 * h * k * (1 - k), a: 1 };
        };
        if (t < 0.56) return hop(0, 0.56, 44, 0, 0.5);
        if (t < 0.98) return hop(0.56, 0.42, 22, 0.5, 0.82);
        if (t < 1.4) return { x: x0 + R * (0.82 + 0.18 * ((t - 0.98) / 0.42)), y: 0, a: 1 };
        if (t < 1.7) return { x: x0 + R, y: 0, a: 1 };
        // Back to the cage's foot, and in under its net.
        if (t < 2.7) {
            const k = (t - 1.7) / 1.0;
            return { x: x0 + R * (1 - k), y: 0, a: k > 0.8 ? (1 - k) * 5 : 1, back: true };
        }
        return null;
    }

    update(dt, time) {
        const s = this.scene, d = this.def, p = s.player;
        if (!near(s, d.x, d.y, 700, 200)) {
            this.ball.setVisible(false);
            this.shadow.setVisible(false);
            return;
        }
        const t = ((time / 1000 + d.offset) % d.period);
        const q = this.at(t);
        this.ball.setVisible(!!q);
        this.shadow.setVisible(!!q && !q.tell);
        if (!q) return;
        if (q.tell && !this.told) {
            this.told = true;
            sfx.rattle();
        }
        if (!q.tell) this.told = false;
        const y = d.y - 5 - q.y;
        this.ball.setPosition(q.x, y).setAlpha(q.a).setAngle((q.x * 6) % 360);
        this.shadow.setPosition(q.x, d.y - 1).setAlpha(q.a * Math.max(0.15, 0.45 - q.y / 200));
        if (q.tell || q.back || s.mode !== 'play' || s.route !== 'inside' || time < this.hitAt) return;
        const hit = Math.abs(p.x - q.x) < PLAYER.bodyWidth / 2 + 5 && y > p.y - PLAYER.height - 3 && y < p.y + 2 && Math.abs(p.y - d.y) < 80;
        if (!hit) return;
        this.hitAt = time + 1500;
        if (this.world.carry) this.world.carryBox.spill(q.x);
        else s.scareContact(q.x, 'bonked');
    }
}

// A teppanyaki grill's flare (population: `haz_flare`): the chef's flourish, sparks on the plate,
// and a ball of flame over the counter and the way past it for a second: "Singed" (a tray is
// spilled). The two grills take turns.
export class Flare {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, y, half, period, on, offset, chef }
        this.g = s.add.graphics().setDepth(D.player + 0.04);
        this.glow = s.add.rectangle(def.x, def.y - 64, def.half * 2 + 90, 128, 0xf9c22b, 0).setDepth(D.decor + 0.3);
        world.add([this.g, this.glow]);
        this.hitAt = 0;
    }

    // 'calm', 'tell' (how far into it, 0-1) or 'on' (0-1).
    phase(time) {
        const d = this.def, t = (time / 1000 + d.offset) % d.period;
        if (t >= d.period - d.on) return ['on', (t - (d.period - d.on)) / d.on];
        if (t >= d.period - d.on - 0.9) return ['tell', (t - (d.period - d.on - 0.9)) / 0.9];
        return ['calm', 0];
    }

    update(dt, time) {
        const s = this.scene, d = this.def, p = s.player, g = this.g.clear();
        if (!near(s, d.x, d.y, 700, 200)) return;
        const [phase, k] = this.phase(time);
        const top = d.y - 31;
        if (phase === 'calm') {
            this.told = false;
            this.glow.setFillStyle(0xf9c22b, 0);
            // A little steam off the plate.
            const a = (time / 900) % 1;
            g.fillStyle(0xffffff, 0.5 * (1 - a)).fillRect(d.x - 6 + Math.sin(time / 300) * 2, top - 4 - a * 14, 2, 3);
            return;
        }
        if (phase === 'tell') {
            if (!this.told) {
                this.told = true;
                const chef = this.world.people.byId[d.chef];
                if (chef?.on && chef.state !== 'acting') this.world.people.play(chef, 'flourish');
                sfx.rattle();
            }
            this.glow.setFillStyle(0xf9c22b, 0.1 * k);
            for (let i = 0; i < 7; i++) {
                const a = (time / 260 + i * 0.37) % 1;
                g.fillStyle(i % 2 ? 0xfbff86 : 0xf9c22b, 1 - a).fillRect(d.x + Math.sin(i * 2.4) * 14 + a * Math.sin(i) * 8, top - a * (10 + i * 3), 2, 2);
            }
            return;
        }
        // The flame: up fast, hanging, and gone.
        const env = k < 0.18 ? k / 0.18 : k > 0.75 ? Math.max(0, (1 - k) / 0.25) : 1;
        this.glow.setFillStyle(0xf9c22b, 0.22 * env);
        const w = d.half * env, cy = d.y - 54;
        const blob = (colour, alpha, sx, sy, dy) => {
            g.fillStyle(colour, alpha);
            for (let i = 0; i < 9; i++) {
                const f = (i - 4) / 4, lick = Math.sin(time / 55 + i * 1.9) * 7;
                g.fillEllipse(d.x + f * w * sx * 0.8, cy + dy + Math.abs(f) * 14 + lick * 0.4, w * sx * 0.55, (62 - Math.abs(f) * 26 + lick) * sy * env);
            }
        };
        blob(0xe83b3b, 0.85, 1, 1, 0);
        blob(0xf79617, 0.9, 0.8, 0.82, 5);
        blob(0xf9c22b, 0.95, 0.6, 0.62, 10);
        blob(0xfbff86, 1, 0.36, 0.4, 15);
        if (k < 0.1 && !this.lit) sfx.whoosh();
        this.lit = k < 0.9;
        if (env < 0.7 || s.mode !== 'play' || s.route !== 'inside' || time < this.hitAt) return;
        if (Math.abs(p.x - d.x) > d.half - 8 || Math.abs(p.y - d.y) > 90 || p.y < d.y - 100) return;
        this.hitAt = time + 1500;
        if (this.world.carry) this.world.carryBox.spill(d.x);
        else s.scareContact(d.x, 'singed');
    }
}

// The funnel's wind and its gulls (population: `gust_funnel`, `gull_funnel`). On the stairway a
// gust is no time to climb: moving in one she loses her footing and slides back down the flight.
// Two gulls circle the lattice; every so often, in a lull, one marks her on the stairs and comes
// down at the spot: "Swooped", unless she has moved on.
export class FunnelWind {
    constructor(world, def, gusts) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;
        this.gusts = gusts;
        const f = world.data.funnel;
        this.centre = { x: (f.shoulder[0] + f.head[0]) / 2 - 70, y: (f.shoulder[1] + f.head[1]) / 2 - 90 };
        this.gulls = Array.from({ length: def.gulls }, (_, i) => {
            const sprite = s.add.image(this.centre.x, this.centre.y, 'things', 'gull-up').setDepth(D.player + 0.34);
            world.add([sprite]);
            return { sprite, i, x: this.centre.x, y: this.centre.y };
        });
        this.mark = s.add.ellipse(0, 0, 22, 5, 0x2e222f, 0.5).setDepth(D.player - 0.01).setVisible(false);
        world.add([this.mark]);
        this.state = 'circle';
        this.cycle = -1;
        this.turn = 0;
    }

    onStairs() {
        const s = this.scene;
        return s.mode === 'stairs' && s.flight?.outside;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def, g = this.def.gust;
        if (!near(s, this.centre.x, this.centre.y, 1100, 700)) return;
        const flap = Math.floor(time / 130) % 2 ? 'gull-down' : 'gull-up';
        // The slip: she was climbing when it blew.
        const on = this.onStairs();
        if (on && !s.stairSlip && this.gusts.phase(time) === 'blow' && this.lastFlight === s.flight && Math.abs(s.stairT - this.lastT) > 1e-5 && s.stairT > 0.02) {
            s.stairSlip = true;
            this.world.say('Ой-йой!', 800);
            sfx.whoosh();
        }
        this.lastFlight = on ? s.flight : null;
        this.lastT = s.stairT;
        // The gulls: round the lattice, the diver out of its circle.
        const diver = this.gulls[this.turn % this.gulls.length];
        for (const b of this.gulls) {
            if (b === diver && this.state !== 'circle') continue;
            const a = time / 1700 + b.i * Math.PI;
            const tx = this.centre.x + Math.cos(a) * 170, ty = this.centre.y + Math.sin(a) * 70 + Math.sin(a * 2.3) * 12;
            b.x += (tx - b.x) * Math.min(1, dt * 3);
            b.y += (ty - b.y) * Math.min(1, dt * 3);
            b.sprite.setFrame(flap).setPosition(b.x, b.y).setFlipX(Math.sin(a) > 0);
        }
        const t = (time / 1000) % g.every, cycle = Math.floor(time / 1000 / g.every);
        if (this.state === 'circle') {
            // In a lull, with time to get clear before the next gust.
            const due = cycle !== this.cycle && cycle % Math.max(1, Math.round(d.swoop / g.every)) === 0 && t > 0.3 && t < 1.0;
            if (due && on && !s.stairSlip) {
                this.cycle = cycle;
                this.state = 'mark';
                this.at = time + 1000;
                this.target = { x: p.x, y: p.y };
                this.mark.setPosition(p.x, p.y - 1).setVisible(true).setScale(0.4);
                s.tweens.add({ targets: this.mark, scale: 1.2, duration: 1000 });
                sfx.whoosh();
            }
        } else if (this.state === 'mark') {
            diver.x += (this.target.x - diver.x) * Math.min(1, dt * 5);
            diver.y += (this.target.y - 108 - diver.y) * Math.min(1, dt * 5);
            diver.sprite.setFrame(flap).setPosition(diver.x, diver.y).setFlipX(this.target.x < diver.x);
            if (time > this.at) {
                this.state = 'dive';
                this.at = time + 230;
                this.from = { x: diver.x, y: diver.y };
            }
        } else if (this.state === 'dive') {
            const k = 1 - Math.max(0, this.at - time) / 230;
            diver.x = this.from.x + (this.target.x - this.from.x) * k;
            diver.y = this.from.y + (this.target.y - 30 - this.from.y) * k * k;
            diver.sprite.setFrame('gull-down').setPosition(diver.x, diver.y);
            if (time > this.at) {
                this.mark.setVisible(false);
                const hit = this.onStairs() && Math.abs(p.x - this.target.x) < 17 && Math.abs(p.y - this.target.y) < 30;
                if (hit) s.scareContact(this.target.x + (p.flipX ? -8 : 8), 'swooped');
                this.state = 'circle';
                this.turn++;
            }
        }
    }
}

// A flock of gulls sitting about the bow (population: `gull_bow_a`, `gull_bow_b`) until the horn
// sends them off in a cloud.
export class Flock {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { id, x0, x1, y, n }
        this.birds = Array.from({ length: def.n }, (_, i) => {
            // (About the two ends of the stretch: a pool's two rims, a windscreen's length.)
            const k = def.n > 1 ? i / (def.n - 1) : 0.5;
            const x = Math.round(def.x0 + (def.x1 - def.x0) * (k < 0.5 ? k * 0.36 : 1 - (1 - k) * 0.36) + ((i * 37) % 9) - 4);
            const sprite = s.add.image(x, def.y, 'things', 'gull-perched').setOrigin(0.5, 1).setFlipX(i % 2 === 0).setDepth(D.props + 0.06);
            world.add([sprite]);
            return { sprite, x, i };
        });
        world.things.push({ id: def.id, x: (def.x0 + def.x1) / 2, y: def.y, route: 'inside', items: this.birds.map(b => b.sprite), until: 'flag:horn' });
    }

    update(dt, time) {
        const s = this.scene, d = this.def;
        if (this.gone || !near(s, (d.x0 + d.x1) / 2, d.y, 800, 300)) return;
        // Now and then one shuffles, or stretches a wing.
        for (const b of this.birds) {
            if (b.up) continue;
            const beat = Math.floor(time / 900 + b.i * 1.7) % 7 === 0;
            b.sprite.y = d.y - (beat && Math.floor(time / 110) % 2 ? 1 : 0);
        }
    }

    // Up and away over the bow, all at once. Resolves when the sky is clear.
    liftOff() {
        const s = this.scene, d = this.def;
        this.gone = true;
        return Promise.all(this.birds.map((b, i) => new Promise(resolve => {
            b.up = true;
            const flap = s.time.addEvent({ delay: 110, loop: true, callback: () => b.sprite.setFrame(b.sprite.frame.name === 'gull-up' ? 'gull-down' : 'gull-up') });
            b.sprite.setOrigin(0.5, 0.5).setFrame('gull-up').setFlipX(true).setDepth(s.DEPTH.fx - 0.1);
            s.tweens.add({
                targets: b.sprite, x: b.x - 260 - i * 36, y: d.y - 250 - ((i * 53) % 90), duration: 2100 + i * 90, delay: i * 70, ease: 'Sine.easeIn',
                onComplete: () => { flap.remove(); b.sprite.setVisible(false); resolve(); },
            });
        })));
    }
}

// --- The region's part of the story (mixed into the Story) --------------------------------------

export const topdeck = {
    setupTopdeck() {
        const s = this.scene, w = this.world, T = w.data.topdeck, D = s.DEPTH;
        if (!T) return;
        this.T = T;
        this.topdeckTextures();
        w.movers.push(this.oldLady = new OldLady(w, T.lady));
        for (const b of T.balls) w.movers.push(new Balls(w, b));
        this.flares = T.flares.map(f => new Flare(w, f));
        w.movers.push(...this.flares);
        this.flocks = T.flocks.map(f => new Flock(w, f));
        w.movers.push(...this.flocks);

        // The court's ball, lying by the cage.
        const C = T.court;
        this.courtBall = s.add.image(C.ballX, C.y - 5, 'shipart', 'basketball').setDepth(D.props + 0.04);
        w.add([this.courtBall]);
        w.things.push({ id: 'sec_court', x: C.ballX, y: C.y, route: 'inside', items: [this.courtBall], reach: 16, interact: () => this.court() });

        // The aft terrace: gusts over it and over the sun cover below; towels on the deck chairs'
        // backs (they flap first); a gull on the end rail.
        const tr = T.terrace;
        this.terraceGusts = new Gusts(w, { ...tr, route: 'inside' });
        w.movers.push(this.terraceGusts);
        w.winds.push(this.terraceGusts);
        w.movers.push(new PerchGull(w, { ...tr.gull, route: 'inside' }));

        // The funnel: the wind on the roof, the stairway and the top, its windsocks; the gulls.
        const F = T.funnel, f = w.data.funnel;
        this.funnelGusts = new Gusts(w, { gust: F.gust, towels: [], x0: F.x0, x1: F.x1, top: F.y - 60, bottom: F.roofY, route: 'inside' });
        w.movers.push(this.funnelGusts);
        w.winds.push(this.funnelGusts);
        const sock = (x, y, i) => {
            const pole = s.add.rectangle(x, y, 2, 40, 0xe8eaec).setOrigin(0.5, 1).setDepth(D.exterior + 0.075);
            const img = s.add.image(x + 1, y - 39, 'windsock').setOrigin(0.5, 0).setDepth(D.exterior + 0.08);
            w.add([pole, img]);
            this.funnelGusts.flappers.push({ img, k: 3.6, i });
        };
        sock(f.shoulder[0] - 44, f.shoulder[1], 1);
        sock(f.x1 - 10, f.y - 30, 2);
        sock(F.ladderX + 34, F.roofY, 3);
        w.movers.push(this.funnelWind = new FunnelWind(w, F, this.funnelGusts));

        // On the top: the horn on its post, its cord; the engineer's toolbox and lunch box; the
        // lookout telescope at the aft rail.
        const top = f.y, hx = F.hornX;
        const post = s.add.graphics().setDepth(D.exterior + 0.076);
        post.fillStyle(0x9babb2, 1).fillRect(hx - 2, top - 104, 4, 104);
        post.fillStyle(0xe8eaec, 1).fillRect(hx - 2, top - 104, 1, 104).fillRect(hx - 12, top - 94, 22, 3);
        // (Two brass trumpets, their bells forward.)
        for (const [dy, len] of [[-103, 30], [-90, 22]]) {
            post.fillStyle(0x2e222f, 1).fillRect(hx - len - 3, top + dy - 1, len + 4, 8).fillTriangle(hx - len - 3, top + dy + 3, hx - len - 13, top + dy - 6, hx - len - 13, top + dy + 12);
            post.fillStyle(0xf9c22b, 1).fillRect(hx - len - 2, top + dy, len + 2, 6).fillTriangle(hx - len - 2, top + dy + 3, hx - len - 12, top + dy - 4, hx - len - 12, top + dy + 10);
            post.fillStyle(0xfbff86, 1).fillRect(hx - len - 2, top + dy + 1, len, 1);
            post.fillStyle(0xd9a43b, 1).fillRect(hx - len - 12, top + dy - 4, 1, 14);
        }
        this.cord = s.add.graphics().setDepth(D.exterior + 0.077);
        this.drawCord(0);
        const box = s.add.image(F.toolboxX, top, 'toolbox').setOrigin(0.5, 1).setDepth(D.exterior + 0.08);
        const scope = s.add.image(F.telescopeX, top, 'shipart', 'telescope').setOrigin(0.5, 1).setFlipX(true).setDepth(D.exterior + 0.08);
        w.add([post, this.cord, box, scope]);
        w.things.push({ id: 'sec_horn', x: hx + 8, y: top, route: 'inside', items: [], reach: 20, interact: () => this.horn() });
        w.things.push({ id: 'sec_telescope', x: F.telescopeX, y: top, route: 'inside', items: [], reach: 18, interact: () => this.telescope() });

        // Bumbot on the horn's bracket, out of reach, against the sky (population:
        // `bb_glimpse_funnel`) until it sounds under him.
        this.hornCat = s.add.sprite(hx + 4, top - 94, 'bumbot').setOrigin(0.5, 1).setDepth(D.exterior + 0.09).setFlipX(true);
        this.hornCat.play('bumbot-sit');
        w.add([this.hornCat]);
        this.refreshTopdeck();
    },

    topdeckTextures() {
        const s = this.scene;
        const make = (key, w, h, draw) => {
            if (s.textures.exists(key)) return;
            const g = s.make.graphics({ x: 0, y: 0 }, false);
            draw(g);
            g.generateTexture(key, w, h);
            g.destroy();
        };
        // A sunbed seen from the side: white frame, a striped mattress, its head end up (forward).
        make('sunbed', 62, 27, g => {
            const ink = 0x2e222f;
            g.fillStyle(ink, 1).fillRect(8, 12, 54, 7).fillRect(12, 18, 3, 9).fillRect(52, 18, 3, 9);
            g.fillStyle(ink, 1).fillPoints([{ x: 0, y: 2 }, { x: 5, y: 0 }, { x: 15, y: 12 }, { x: 15, y: 19 }, { x: 8, y: 19 }], true);
            g.fillStyle(0xf4f4f4, 1).fillRect(9, 16, 52, 2).fillRect(13, 18, 1, 8).fillRect(53, 18, 1, 8);
            g.fillStyle(0x4d9be6, 1).fillRect(12, 13, 49, 3);
            for (let x = 16; x < 60; x += 8) g.fillStyle(0xffffff, 1).fillRect(x, 13, 4, 3);
            g.fillStyle(0x4d9be6, 1).fillPoints([{ x: 2, y: 3 }, { x: 5, y: 2 }, { x: 13, y: 12 }, { x: 13, y: 16 }, { x: 10, y: 16 }], true);
            g.fillStyle(0xffffff, 1).fillPoints([{ x: 5, y: 6 }, { x: 7, y: 5 }, { x: 10, y: 9 }, { x: 8, y: 10 }], true);
        });
        // The engineer's toolbox, his lunch box open on it.
        make('toolbox', 34, 22, g => {
            const ink = 0x2e222f;
            g.fillStyle(ink, 1).fillRect(0, 9, 34, 13).fillRect(11, 5, 12, 5);
            g.fillStyle(0xe83b3b, 1).fillRect(1, 10, 32, 11);
            g.fillStyle(0xae2334, 1).fillRect(1, 18, 32, 3).fillRect(1, 13, 32, 1);
            g.fillStyle(0xc7dcd0, 1).fillRect(14, 12, 6, 3).fillRect(12, 6, 10, 1).fillRect(12, 6, 1, 4).fillRect(21, 6, 1, 4);
            g.fillStyle(ink, 1).fillRect(20, 3, 13, 7);
            g.fillStyle(0x4d9be6, 1).fillRect(21, 4, 11, 5);
            g.fillStyle(0xffffff, 1).fillRect(22, 5, 4, 2);
        });
        // A windsock, hanging limp from its pole's top (the wind lifts it).
        make('windsock', 8, 26, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, 8, 26);
            for (let i = 0; i < 5; i++) g.fillStyle(i % 2 ? 0xffffff : 0xe83b3b, 1).fillRect(1 + (i > 2 ? 1 : 0), 1 + i * 5, 6 - (i > 2 ? 2 : 0), 5);
        });
        this.world.icon('cocktail');
    },

    drawCord(pull) {
        const F = this.T.funnel, top = this.world.data.funnel.y, x = F.hornX + 8, g = this.cord.clear();
        g.fillStyle(0xab947a, 1).fillRect(x, top - 93, 1, 44 + pull);
        g.fillStyle(0x2e222f, 1).fillRect(x - 2, top - 49 + pull, 5, 8);
        g.fillStyle(0xe83b3b, 1).fillRect(x - 1, top - 48 + pull, 3, 6);
    },

    refreshTopdeck() {
        if (!this.T) return;
        const horn = this.P.has('horn');
        this.hornCat?.setVisible(!horn && !this.hornCatGone);
        // The parts of the top that stand over her deck show only from outside.
    },

    updateTopdeck(dt, time) {
        const s = this.scene, w = this.world, her = s.player, T = this.T;
        if (!T) return;
        // How the old lady is passed, the first time she is stopped by the sunbed.
        const L = T.lady;
        if (s.mode === 'play' && s.route === 'inside' && !this.P.has('horn') && !w.save.seen.includes('hint-sunbed')
            && Math.abs(her.y - L.y) < 4 && Math.abs(Math.abs(her.x - L.x) - L.half - PLAYER.bodyWidth / 2) < 3 && her.body.velocity.x === 0
            && (her.body.blocked.left || her.body.blocked.right || her.body.touching.left || her.body.touching.right)) {
            w.save.seen.push('hint-sunbed');
            w.hint(w.carry ? 'No way past her with a tray' : 'Jump over, or ↓ to drop through the walk');
        }
        // The engineer on his break turns to her.
        const e = this.who('npc_engineer_read');
        if (e?.on && e.state !== 'acting' && Math.abs(her.y - e.y) < 8 && Math.abs(her.x - e.x) < 3 * M) {
            const dir = her.x < e.x ? -1 : 1;
            if (dir !== e.dir) {
                e.dir = dir;
                this.people.place(e);
            }
        }
    },

    // E at the old lady (population: `npc_oldlady`): her mojito from Topsiders' bar. She drinks it
    // and dozes off; her thanks roll out of her bag: two tangerines.
    oldLadyDrink() {
        const L = this.near('npc_oldlady', this.T.lady.half + 34), w = this.world, s = this.scene;
        if (!L || this.P.has('lady')) return false;
        if (w.carry?.kind !== 'cocktail') {
            if (w.carry) return false;
            w.nudge(L);
            return true;
        }
        L.state = 'acting';
        this.oldLady.glaring = false;
        w.cut(async () => {
            const her = s.player;
            her.setFlipX(L.x < her.x);
            await w.wait(200);
            w.carryBox.give();
            const glass = s.add.image(her.x + (her.flipX ? -12 : 12), her.y - 34, 'shipart', 'umbrella-cocktail').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.05);
            w.add([glass]);
            sfx.pickup();
            await w.tween({ targets: glass, x: L.x + 13, y: L.y - 34, duration: 380, ease: 'Sine.easeInOut' });
            // A long sip, and another; a sigh.
            L.still = '';
            L.idle = 'read';
            this.people.idle(L);
            L.state = 'acting';
            for (let i = 0; i < 2; i++) {
                await w.tween({ targets: glass, y: L.y - 43, angle: -28, duration: 260 });
                await w.wait(420);
                await w.tween({ targets: glass, y: L.y - 34, angle: 0, duration: 220 });
                await w.wait(240);
            }
            const heart = s.add.text(L.x + 4, L.y - 62, '♥', { fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#e83b3b', resolution: 4 }).setOrigin(0.5).setDepth(s.DEPTH.fx);
            w.add([heart]);
            s.tweens.add({ targets: heart, y: heart.y - 16, alpha: 0, duration: 1000, onComplete: () => heart.destroy() });
            await w.tween({ targets: glass, x: L.x + 30, y: L.y - 23, duration: 300 });
            this.ladyGlass = glass;
            L.state = 'idle';
            sfx.checkpoint();
            // (Her bag has tipped: what was in it.)
            w.sparkle(this.T.lady.x - 39, L.y - 10);
            this.P.setFlag('lady');
        });
        return true;
    },

    // E at the engineer with his coffee, still hot (population: `scn_engineer`): he drinks, waves
    // her up, unhooks the chain and climbs the ladder to the roof. From then on he is on the top.
    engineerCoffee() {
        const e = this.near('npc_engineer', 46), w = this.world, s = this.scene, F = this.T.funnel;
        if (!e || this.P.has('engineer')) return false;
        if (w.carry?.kind !== 'coffee') {
            if (w.carry) return false;
            w.nudge(e);
            return true;
        }
        e.state = 'acting';
        w.cut(async () => {
            const her = s.player;
            her.setFlipX(e.x < her.x);
            e.dir = her.x < e.x ? -1 : 1;
            this.people.place(e);
            await w.wait(200);
            w.carryBox.give();
            const cup = s.add.image(her.x + (her.flipX ? -12 : 12), her.y - 34, 'shipart', 'coffee-cup').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.05);
            w.add([cup]);
            sfx.pickup();
            await w.tween({ targets: cup, x: e.x + e.dir * 11, y: e.y - 36, duration: 380, ease: 'Sine.easeInOut' });
            cup.setVisible(!e.meta.anims.drink);
            await this.people.play(e, 'drink', { times: 2 });
            cup.destroy();
            e.state = 'acting';
            const steam = s.add.text(e.x + e.dir * 4, e.y - 66, '♨', { fontFamily: 'Verdana, sans-serif', fontSize: '10px', color: '#cd683d', resolution: 4 }).setOrigin(0.5).setDepth(s.DEPTH.fx);
            w.add([steam]);
            s.tweens.add({ targets: steam, y: steam.y - 14, alpha: 0, duration: 900, onComplete: () => steam.destroy() });
            await w.wait(300);
            await this.people.play(e, 'wave');
            e.state = 'acting';
            // The chain off its hook, and up he goes.
            const gate = w.gates.find(g => g.needs === 'engineer');
            e.dir = F.ladderX < e.x ? -1 : 1;
            this.people.place(e);
            this.people.anim(e, 'walk');
            await w.tween({ targets: e, x: F.ladderX - e.dir * 10, duration: Math.abs(F.ladderX - e.x) * 12 + 80, onUpdate: () => this.people.place(e) });
            sfx.rattle();
            if (gate?.extra) await w.tween({ targets: gate.extra, alpha: 0, duration: 260 });
            e.x = F.ladderX;
            this.people.place(e);
            if (!this.people.anim(e, 'climb')) this.people.anim(e, 'walk');
            await w.tween({ targets: e.sprite, y: e.y - 150, duration: 1700 });
            await w.tween({ targets: e.sprite, alpha: 0, duration: 200 });
            e.gone = true;
            // (The technical door beside it is hers to come back to from now on: population `cp_technical`.)
            const cp = s.checkpoints.find(c => c.id === 'cp_technical');
            if (cp && !cp.active) {
                s.lightCheckpoint(cp, true);
                w.save.activated.push(cp.id);
            }
            this.P.setFlag('engineer');
            gate?.extra?.forEach(i => i.setAlpha(1));
        });
        return true;
    },

    // E at the engineer on his break, after the horn: he lends her what he is reading, the ninth book.
    engineerBook() {
        const e = this.near('npc_engineer_read', 40), w = this.world, s = this.scene;
        if (!e || this.P.has('book9') || w.carry) return false;
        e.state = 'acting';
        w.cut(async () => {
            const her = s.player;
            her.setFlipX(e.x < her.x);
            e.dir = her.x < e.x ? -1 : 1;
            this.people.place(e);
            e.sprite.anims.stop();
            e.sprite.setFrame(e.meta.stand);
            await w.wait(350);
            await w.handOver(e, '@book-9', () => w.giveBook(9));
            e.idle = 'idle';
            this.people.idle(e);
            this.P.setFlag('book9');
        });
        return true;
    },

    // E at the ball by the court (population: `sec_court`): she shoots, and scores.
    court() {
        const s = this.scene, w = this.world, C = this.T.court, her = s.player, ball = this.courtBall;
        if (w.carry || this.shooting) return false;
        this.shooting = true;
        w.cut(async () => {
            const dir = C.hoopX < her.x ? -1 : 1;
            const rim = { x: C.hoopX - dir * 24, y: C.y - 93 };
            her.setFlipX(dir < 0);
            sfx.pickup();
            await w.tween({ targets: ball, x: her.x + dir * 8, y: her.y - 40, duration: 220 });
            if (s.anims.exists('her-throw')) her.anims.play('her-throw');
            else s.pose('rise');
            await w.tween({ targets: ball, y: her.y - 62, duration: 240, ease: 'Quad.easeOut' });
            sfx.jump();
            // Up, over, and through.
            const from = { x: ball.x, y: ball.y }, peak = rim.y - 34;
            await new Promise(resolve => s.tweens.addCounter({
                from: 0, to: 1, duration: 760,
                onUpdate: tw => {
                    const k = tw.getValue();
                    const y = k < 0.6 ? from.y + (peak - from.y) * (1 - (1 - k / 0.6) ** 2) : peak + (rim.y - peak) * ((k - 0.6) / 0.4) ** 2;
                    ball.setPosition(from.x + (rim.x - from.x) * k, y).setAngle(k * 720);
                },
                onComplete: resolve,
            }));
            s.pose('stand');
            sfx.ding();
            w.sparkle(rim.x, rim.y + 6, 0xfbff86);
            await w.tween({ targets: ball, y: C.y - 5, duration: 330, ease: 'Quad.easeIn' });
            sfx.land();
            await w.tween({ targets: ball, y: C.y - 30, x: ball.x - dir * 20, duration: 220, ease: 'Quad.easeOut' });
            await w.tween({ targets: ball, y: C.y - 5, x: ball.x - dir * 20, duration: 220, ease: 'Quad.easeIn' });
            await w.tween({ targets: ball, x: C.ballX, angle: 0, duration: 700, ease: 'Sine.easeOut' });
            if (!w.save.seen.includes('sec_court')) {
                w.save.seen.push('sec_court');
                writeSave(w.save);
            }
            this.shooting = false;
        });
        return true;
    },

    // E at the telescope (population: `sec_telescope`): through it, a balcony far forward, and a
    // frame on its wall.
    telescope() {
        const s = this.scene, w = this.world, look = this.T.funnel.look, her = s.player, cam = s.cameras.main;
        if (w.carry) return false;
        w.cut(async () => {
            her.setFlipX(this.T.funnel.telescopeX < her.x);
            if (s.anims.exists('her-idle-look')) her.anims.play('her-idle-look');
            await w.wait(350);
            await w.tween({ targets: s.fade, alpha: 1, duration: 200 });
            if (!s.textures.exists('scope-mask')) {
                const W = s.scale.width, H = s.scale.height;
                const tex = s.textures.createCanvas('scope-mask', W, H), c = tex.getContext();
                c.fillStyle = '#0d0b14';
                c.fillRect(0, 0, W, H);
                c.globalCompositeOperation = 'destination-out';
                c.beginPath();
                c.arc(W / 2, H / 2, H * 0.4, 0, Math.PI * 2);
                c.fill();
                c.globalCompositeOperation = 'source-over';
                c.strokeStyle = '#2e222f';
                c.lineWidth = 6;
                c.beginPath();
                c.arc(W / 2, H / 2, H * 0.4, 0, Math.PI * 2);
                c.stroke();
                tex.refresh();
            }
            const mask = s.add.image(0, 0, 'scope-mask').setOrigin(0);
            s.uiLayer.add(mask);
            s.uiLayer.bringToTop(s.fade);
            cam.stopFollow();
            cam.centerOn(look.x - 60, look.y - 10);
            w.peek = 'promenade';
            w.refresh();
            const glint = s.add.image(look.x, look.y, 'dot').setTint(0xfbff86).setDepth(s.DEPTH.fx);
            w.add([glint]);
            s.tweens.add({ targets: glint, alpha: { from: 0.2, to: 1 }, scale: { from: 1, to: 3 }, duration: 420, yoyo: true, repeat: -1 });
            await w.tween({ targets: s.fade, alpha: 0, duration: 250 });
            // It swings along the balconies to the frame.
            await new Promise(resolve => cam.pan(look.x, look.y - 10, 1300, 'Sine.easeInOut', true, (_, k) => { if (k === 1) resolve(); }));
            await w.wait(1900);
            await w.tween({ targets: s.fade, alpha: 1, duration: 200 });
            glint.destroy();
            mask.destroy();
            w.peek = null;
            w.refresh();
            cam.startFollow(her, true, 0.15, 0.15);
            cam.setFollowOffset(0, HALF);
            cam.centerOn(her.x, her.y - HALF);
            s.pose('stand');
            await w.tween({ targets: s.fade, alpha: 0, duration: 250 });
            if (!w.save.seen.includes('sec_telescope')) {
                w.save.seen.push('sec_telescope');
                writeSave(w.save);
            }
        });
        return true;
    },

    // E at the horn's cord (population: `scn_horn`). The first time, with the engineer's leave:
    // the blast, and what it sets off, shown from up here by the camera. After that, a toot.
    horn() {
        const s = this.scene, w = this.world, P = this.P, her = s.player, F = this.T.funnel, top = w.data.funnel.y;
        if (w.carry) return false;
        if (!P.has('engineer') && !P.openAll) return false;
        const first = !P.has('horn');
        w.cut(async () => {
            her.setFlipX(F.hornX + 8 < her.x);
            if (s.anims.exists('her-pull')) her.anims.play('her-pull');
            else s.pose('rise');
            await w.wait(260);
            await new Promise(resolve => s.tweens.addCounter({ from: 0, to: 9, duration: 160, onUpdate: tw => this.drawCord(tw.getValue()), onComplete: resolve }));
            this.blast(first ? 1500 : 500);
            if (first) this.catOffTheHorn();
            await w.wait(first ? 1300 : 450);
            s.tweens.addCounter({ from: 9, to: 0, duration: 260, onUpdate: tw => this.drawCord(tw.getValue()) });
            s.pose('stand');
            if (!first) return;
            await this.cascade();
            P.setFlag('horn');
        });
        return true;
    },

    // The blast: the top shakes, rings of sound leave the trumpets, the pipes cough smoke.
    blast(ms) {
        const s = this.scene, w = this.world, F = this.T.funnel, top = w.data.funnel.y;
        sfx.horn?.(ms / 1000);
        s.cameras.main.shake(ms, 0.006);
        for (let i = 0; i * 170 < ms; i++) {
            s.time.delayedCall(i * 170, () => {
                const ring = s.add.ellipse(F.hornX - 44, top - 96, 8, 16).setStrokeStyle(2, 0xffffff, 0.9).setDepth(s.DEPTH.fx);
                w.add([ring]);
                s.tweens.add({ targets: ring, x: ring.x - 150, scaleX: 5, scaleY: 7, alpha: 0, duration: 700, ease: 'Quad.easeOut', onComplete: () => ring.destroy() });
            });
        }
        for (let i = 0; i < 8; i++) {
            const puff = s.add.image(F.hornX - 180 + i * 46 + (i % 2) * 14, top - 96, 'puff').setDepth(s.DEPTH.exterior + 0.03).setScale(0.3).setAlpha(0.9);
            w.add([puff]);
            s.tweens.add({ targets: puff, x: puff.x + 120, y: puff.y - 150 - (i % 3) * 30, scale: 2.2, alpha: 0, duration: 1500 + i * 60, delay: i * 50, onComplete: () => puff.destroy() });
        }
    },

    // Bumbot, on the horn when it sounds: straight up, then down the lattice's front and away
    // forward along the roof.
    catOffTheHorn() {
        const s = this.scene, w = this.world, cat = this.hornCat, f = w.data.funnel;
        if (!cat?.visible) return;
        this.hornCatGone = true;
        sfx.mrrp();
        cat.play('bumbot-jump');
        s.tweens.chain({
            targets: cat,
            tweens: [
                { y: cat.y - 34, duration: 200, ease: 'Quad.easeOut' },
                { x: f.head[0] + 4, y: f.head[1], duration: 280, ease: 'Quad.easeIn', onComplete: () => cat.play('bumbot-run') },
                { x: f.shoulder[0], y: f.shoulder[1], duration: 620 },
                { x: f.foot[0], y: f.foot[1], duration: 240 },
                { x: f.foot[0] - 260, duration: 520, onComplete: () => cat.setVisible(false) },
            ],
        });
    },

    // What the horn sets off (population: `scn_horn`): the camera goes to the sun deck, where the
    // security officer jumps, drops his card and runs for the bridge, and the old lady bolts,
    // leaving her parasol and her book; then to the bow, where the gulls go up in a cloud; and back.
    async cascade() {
        const s = this.scene, w = this.world, cam = s.cameras.main, T = this.T, her = s.player, D = s.DEPTH;
        const pan = (x, y, ms) => new Promise(resolve => cam.pan(x, y, ms, 'Sine.easeInOut', true, (_, k) => { if (k === 1) resolve(); }));
        const streak = (fromX, toX, y, ms, delay = 0) => {
            const cat = s.add.sprite(fromX, y, 'bumbot').setOrigin(0.5, 1).setDepth(D.player + 0.05).setFlipX(toX < fromX);
            cat.play('bumbot-run');
            w.add([cat]);
            s.tweens.add({ targets: cat, x: toX, duration: ms, delay, onStart: () => sfx.mrrp(), onComplete: () => cat.destroy() });
        };
        const L = T.lady, lady = this.who('npc_oldlady'), rival = this.who('riv_sundeck');
        cam.stopFollow();
        s.viewOverride = 12;
        await pan((L.x + L.rivalX) / 2, L.y - HALF - 20, 1500);
        // He shoots through, forward; the officer jumps out of his skin, and his card out of his pocket.
        streak(L.rivalX + 420, L.x - 520, L.y, 1500, 150);
        const acts = [];
        if (rival?.on) {
            acts.push((async () => {
                rival.state = 'acting';
                rival.sprite.anims.stop();
                rival.sprite.setFrame(rival.meta.stand);
                await w.wait(350);
                const card = s.add.image(rival.x + 6, rival.y - 30, 'shipart', 'key-card').setScale(0.5).setTint(0xfbe38a).setDepth(D.props + 0.09);
                w.add([card]);
                await w.tween({ targets: rival.sprite, y: rival.y - 22, duration: 170, ease: 'Quad.easeOut', yoyo: true });
                s.tweens.add({ targets: card, x: L.cardX, y: L.y - 5, angle: 360, duration: 520, ease: 'Quad.easeIn' });
                this.dropped = card;
                await w.wait(300);
                rival.dir = -1;
                this.people.place(rival);
                this.people.anim(rival, 'walk', { speed: 2.3 });
                // (Over the sunbed in his stride.)
                const hop = s.time.addEvent({ delay: 16, loop: true, callback: () => {
                    const d = Math.abs(rival.x - L.x);
                    rival.sprite.y = rival.y - (d < 60 ? (1 - (d / 60) ** 2) * 42 : 0);
                } });
                await w.tween({ targets: rival, x: L.x - 560, duration: 2500, onUpdate: () => this.people.place(rival) });
                hop.remove();
                rival.gone = true;
                rival.items.forEach(i => i.setVisible(false));
            })());
        }
        if (lady?.on) {
            acts.push((async () => {
                lady.state = 'acting';
                lady.still = '';
                this.oldLady.glaring = false;
                await w.wait(250);
                const bang = s.add.text(lady.x, lady.y - 70, '!', { fontFamily: 'Verdana, sans-serif', fontSize: '12px', fontStyle: 'bold', color: '#2e222f', stroke: '#ffffff', strokeThickness: 3, resolution: 4 })
                    .setOrigin(0.5, 1).setDepth(D.fx);
                w.add([bang]);
                s.tweens.add({ targets: bang, alpha: 0, delay: 500, duration: 200, onComplete: () => bang.destroy() });
                await w.tween({ targets: lady.sprite, y: lady.sprite.y - 12, duration: 150, ease: 'Quad.easeOut', yoyo: true });
                // Her bags under her arm, and off, forward.
                const bags = w.things.find(t => t.id === 'blk_oldlady')?.items ?? [];
                await this.people.play(lady, 'bolt');
                lady.state = 'acting';
                lady.sprite.y = lady.y;
                if (!this.people.anim(lady, 'fleeing')) this.people.anim(lady, 'read');
                s.tweens.add({ targets: [...bags, this.ladyGlass].filter(Boolean), x: '-=560', alpha: { from: 1, to: 0.9 }, duration: 2300 });
                await w.tween({ targets: lady, x: lady.x - 560, duration: 2300, onUpdate: () => this.people.place(lady) });
                lady.gone = true;
                lady.items.forEach(i => i.setVisible(false));
                [...bags, this.ladyGlass].filter(Boolean).forEach(i => i.setVisible(false));
            })());
        }
        await w.wait(2700);
        // The bow: he streaks across, and the gulls are gone.
        const [a, b] = [this.flocks.find(f => f.def.id === 'gull_bow_a'), this.flocks.find(f => f.def.id === 'gull_bow_b')];
        const bowX = a ? (a.def.x0 + a.def.x1) / 2 - 90 : 3300;
        await pan(bowX, L.y - HALF - 34, 1700);
        streak(bowX + 380, bowX - 420, L.y, 1300, 100);
        await w.wait(350);
        a?.liftOff();
        await w.wait(450);
        b?.liftOff();
        await w.wait(1900);
        await Promise.all(acts);
        await pan(her.x, her.y - HALF, 1900);
        s.viewOverride = null;
        cam.startFollow(her, true, 0.15, 0.15);
        cam.setFollowOffset(0, HALF);
        this.dropped?.destroy();
        this.dropped = null;
    },
};
