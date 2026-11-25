// Region 10, "Sunset", and the end (GAME_DESIGN.md §6.1.9, docs/population.md §6.11): the balcony
// forward of the spa, where the sky turns; the glide down to the mooring deck through the wind
// and past two gulls; Bumbot at the tip of the bow, who backs away from anyone coming at him and
// comes to anyone standing still; the way home with him in her arms; cabin 8206 and the win
// screen. The region's own things (the wind over the bow, the crossing gulls) and its part of the
// story, mixed into the Story. Places come from maps/world.json (`finale`). The sunset's colours
// are in src/background.js and src/sea.js; her look with him in her arms is the ship scene's
// (`holding`).

import { PLAYER, VIEW, WIN_MESSAGE, BOOKS } from '../config.js';
import { sfx } from '../sfx.js';
import { rumble } from '../rumble.js';
import { t, pick } from '../lang.js';
import { writeSave } from '../save.js';
import { Gusts } from './outside.js';

const M = 48;
const HALF = PLAYER.height / 2;
const BED_TOP = 32;                 // cabin 8206's mattress over its floor (the ship scene's CABIN)
// Bumbot at the tip: he bolts from her coming within `spook`; he minds her standing still within
// `near`; he comes at `come` px/s, never nearer than `gap`; `stillMs` of standing still and he is hers.
const TIP = { spook: 2.3 * M, near: 7.5 * M, come: 34, gap: 44, stillMs: 3000, back: 110, dart: 6 * M };
// A crossing gull's dart at her (the user, 2026-11-18: flown into, it was "indistinguishable from the gull
// just flying around ... it should dart toward us a little bit (not too fast)"): with her ahead of it within
// `ahead` px and `rise` px up or down, it cries and darts straight at where she is then (no homing: she can
// still steer out of its way or let the parasol go; it aims where her drift takes her), at `speed` px/s, for at most `ms`; then on, back to its
// height at `climb` px/s, and no dart again for `rest` ms.
const DART = { ahead: 130, rise: 80, speed: 170, ms: 1100, climb: 45, rest: 2500 };
const BELLY = 5;

// The wind over the bow (population: `gust_finale`): as along the ship's side, it blows aft every
// few seconds and carries her with it in the air; windsocks on the balcony's rail and at the stem
// show it coming, and so do thin streaks at the forward edge of the view. Only from the alarm to
// the catch.
export class FinaleWind extends Gusts {
    constructor(world, F) {
        super(world, { gust: F.gust, towels: [], x0: F.mooring.x0 - 200, x1: F.balcony.x1, top: F.balcony.y - 60, bottom: F.mooring.y, route: 'inside' });
        const s = this.scene, D = s.DEPTH;
        this.F = F;
        F.socks.forEach((k, i) => {
            const pole = s.add.rectangle(k.x, k.y, 2, 46, 0xe8eaec).setOrigin(0.5, 1).setDepth(D.props + 0.03);
            const cap = s.add.rectangle(k.x, k.y - 46, 4, 2, 0x9babb2).setOrigin(0.5, 1).setDepth(D.props + 0.03);
            const img = s.add.image(k.x + 1, k.y - 45, 'windsock').setOrigin(0.5, 0).setDepth(D.props + 0.035);
            world.add([pole, cap, img]);
            this.flappers.push({ img, k: 3.6, i });
        });
    }

    active() {
        const P = this.world.progress;
        return P.has('alarm') && !P.has('catch');
    }

    phase(time) {
        return this.active() ? super.phase(time) : 'calm';
    }

    // On the balcony, or in the open air forward of it down to the mooring deck (not inside the
    // decks behind the sloped front).
    out() {
        const s = this.scene, p = s.player, F = this.F;
        if (s.route !== 'inside') return false;
        if (Math.abs(p.y - F.balcony.y) < 70 && p.x > F.balcony.x0 - 40 && p.x < F.balcony.x1) return true;
        if (p.y < F.balcony.y - 140 || p.y > F.mooring.y + 2) return false;
        return p.x < (p.y <= F.terrace.y + 2 ? F.balcony.x0 + 6 : F.mooring.wallX);
    }

    update(dt, time) {
        super.update(dt, time);
        if (this.phase(time) !== 'tell' || !this.out()) return;
        // The tell in the air: thin streaks coming in at the forward edge of the view.
        const view = this.scene.cameras.main.worldView, g = this.streaks;
        for (let i = 0; i < 6; i++) {
            const x = view.x + ((time * 0.4 + i * 37) % 70);
            const y = view.y + 30 + ((i * 53) % (view.height - 60));
            g.fillStyle(0xffffff, 0.5).fillRect(x, y, 8 + (i * 5) % 8, 1);
        }
    }
}

// The two gulls that cross her way down (population: the finale's gulls): each flies level, to
// and fro, at its own height. Flown into, it knocks the parasol out of her hands: "Swooped".
export class Crossers {
    constructor(world, defs, story) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.story = story;
        this.birds = defs.map((d, i) => {
            // (Hung by its underside, so that its two flap pictures, 22 px and 10 px tall, keep its head and
            // body where they are and only the wings beat: by their middles the body jumped 5 px a flap, and
            // at the top of the view, standing on the bow under the low one, it came and went, the user,
            // 2026-11-18. `BELLY`: its underside under the point it flies at.)
            const sprite = s.add.image(d.x0, d.y, 'things', 'gull-up').setOrigin(0.5, 1).setDepth(D.player + 0.34).setVisible(false);
            world.add([sprite]);
            return { ...d, sprite, i, x: d.x0, dir: 1 };
        });
    }

    // Where a gull is at `time` (ms), and which way it is going: where it starts.
    at(b, time) {
        const span = b.x1 - b.x0, t = ((time / 1000) * b.v + b.i * span * 0.6) % (2 * span);
        return t < span ? { x: b.x0 + t, dir: 1 } : { x: b.x1 - (t - span), dir: -1 };
    }

    update(dt, time) {
        const s = this.scene, p = s.player, P = this.world.progress;
        const on = P.has('alarm') && !P.has('catch');
        const air = s.mode === 'play' && s.route === 'inside' && !s.grounded;
        const chest = p.y - HALF;
        for (const b of this.birds) {
            b.sprite.setVisible(on);
            if (!on) continue;
            if (b.fly === undefined) Object.assign(b, this.at(b, time), { fly: b.y, rest: 0 });
            const was = b.dir;
            if (this.parked) {
                b.dart = null;
                b.fly = b.y;
            } else if (b.dart) {
                // Straight at where she was, until it has gone past it or for `ms`.
                const d = b.dart;
                b.x += d.vx * dt;
                b.fly += d.vy * dt;
                if (time - d.t0 > DART.ms || (b.x - d.tx) * Math.sign(d.vx) > 24) {
                    b.dart = null;
                    b.rest = time + DART.rest;
                }
            } else {
                // Level, to and fro across its span; after a dart, back to its own height.
                b.x += b.dir * b.v * dt;
                if (b.x > b.x1) { b.x = b.x1; b.dir = -1; }
                if (b.x < b.x0) { b.x = b.x0; b.dir = 1; }
                b.fly += Phaser.Math.Clamp(b.y - b.fly, -DART.climb * dt, DART.climb * dt);
                const dx = p.x - b.x, dy = chest - b.fly;
                if (air && time > b.rest && Math.sign(dx) === b.dir && Math.abs(dx) > 20 && Math.abs(dx) < DART.ahead && Math.abs(dy) < DART.rise) {
                    // (At where she will be when it gets there, as she drifts on now: she sinks under the parasol.)
                    const v = p.body.velocity, lead = Math.hypot(dx, dy) / DART.speed;
                    const ax = dx + v.x * lead, ay = dy + v.y * lead, k = DART.speed / Math.hypot(ax, ay);
                    b.dart = { t0: time, tx: p.x + v.x * lead, vx: ax * k, vy: ay * k };
                    sfx.at(b.x, b.fly).gullDive();
                }
            }
            if (b.dart) b.dir = Math.sign(b.dart.vx);
            if (b.dir !== was && !b.dart) sfx.at(b.x, b.fly).gull();
            const y = b.fly + (b.dart ? 0 : Math.round(Math.sin(time / 420 + b.i * 2) * 3));
            // (Darting, its wings beat twice as fast.)
            const beat = b.dart ? 65 : 130;
            b.sprite.setPosition(Math.round(b.x), Math.round(y) + BELLY).setFrame(Math.floor(time / beat) % 2 ? 'gull-down' : 'gull-up').setFlipX(b.dir < 0);
            // (Only in the air: on a deck she is under its flight.)
            const hit = air && Math.abs(p.x - b.x) < 14 && y > p.y - PLAYER.height + 2 && y < p.y - 4;
            if (hit) sfx.at(b.x, y).gull();
            if (hit) s.scareAir('crossgull', { snatch: b.sprite });
        }
    }
}

// --- The region's part of the story (mixed into the Story) --------------------------------------

export const finale = {
    setupFinale() {
        const s = this.scene, w = this.world, F = w.data.finale, D = s.DEPTH;
        if (!F) return;
        this.F = F;
        this.finaleWind = new FinaleWind(w, F);
        w.movers.push(this.finaleWind);
        w.winds.push(this.finaleWind);
        w.movers.push(this.crossers = new Crossers(w, F.gulls, this));

        // Bumbot at the tip of the bow, looking out at the sea ahead, from the sunset on.
        const Mo = F.mooring;
        // (Behind the deck's railing, as she is: it is drawn over them both (the user, 2026-11-25: "place Bumbot behind
        // the railings on the bow. The railings have to obscure him"; he sat on our side of it, on the deck's very
        // edge, since step 10, when his old small sprite could hardly be seen through it). In front of her, though:
        // at the catch he comes to her feet.)
        this.tipCat = s.add.sprite(Mo.catX, Mo.y, 'bumbot').setOrigin(0.5, 1).setDepth(D.player + 0.02).setFlipX(true);
        this.tipCat.play('bumbot-sit').anims.chain('bumbot-sat');
        w.add([this.tipCat]);
        w.things.push({ id: 'bb_tip', x: Mo.catX, y: Mo.y, route: 'inside', items: [this.tipCat], after: 'flag:sunset', until: 'flag:catch' });
        this.tip = { still: 0, hearts: 0, spooks: 0, busy: false, coming: false };

        // At home, from the day after: asleep on the cabin's bed; E by him, and he purrs, and the bed is seen close with
        // his things round him, each from its find (the user, 2026-11-22: `world.seenClose('bed')`). From the floor only:
        // on the bed E is her reading (her seat is 18 px from him; the user: "she still has to have access to the bed's
        // reading spot").
        const H = F.home;
        this.bedCat = s.add.sprite(H.catX, H.y - BED_TOP, 'bumbot').setOrigin(0.5, 1).setDepth(w.depthFor('cabin') + 0.02).play('bumbot-asleep');
        w.add([this.bedCat]);
        w.things.push({ id: 'bb_home', x: H.catX, y: H.y, route: 'cabin', items: [this.bedCat], after: 'flag:home', reach: 26,
            interact: () => { if (s.viewing) return false; this.purr(); return w.seenClose('bed'); } });
        this.refreshFinale();
    },

    // What the flags mean for her and the sky: Bumbot in her arms from the catch until they are
    // home; the sunset from the balcony's scene on, after the ending too (the user, 2026-11-23: the exploration
    // after the ending in the ending's state).
    refreshFinale() {
        const s = this.scene, P = this.P;
        if (!this.F) return;
        if (!this.catching && !this.homing) s.holding = P.has('catch') && !P.has('home');
        const dusk = P.has('sunset') ? 1 : 0;
        if (!this.turning && !this.homing && s.dusk !== dusk) s.setDusk(dusk);
    },

    updateFinale(dt, time) {
        const s = this.scene, P = this.P, F = this.F, her = s.player;
        if (!F) return;
        const play = s.mode === 'play';
        // Out of the hatch, onto the balcony forward of the spa, the first time: the sky turns.
        const B = F.balcony;
        if (play && P.has('alarm') && !P.has('sunset') && !this.turning && s.route === 'inside' && s.grounded
            && Math.abs(her.y - B.y) < 2 && her.x > B.x0 && her.x < B.x1 - 6) this.sunsetScene();
        if (P.has('sunset') && !P.has('catch')) this.updateTip(dt, time);
        // (Someone on the mooring deck before any of it, down from deck 8's terrace, has nothing to
        // do there, and the only way off is over the rail: hers to find out.)
        // Home: the cabin, with him in her arms.
        if (play && s.holding && s.route === 'cabin' && !this.homing) this.homeScene();
        if (s.holding && play) this.updateWelcome(time);
    },

    // After a fright over the bow (the gulls, the sea), she is back where the glide starts: the
    // balcony forward of the spa; before the alarm, deck 8's terrace, the only way she can have come.
    respawnFor(from) {
        const s = this.scene, P = this.P, F = this.F;
        if (!F || s.route !== 'inside' || P.has('catch') || !from) return null;
        const forward = from.x < F.balcony.x0 + 8 && from.y > F.balcony.y - 200
            && (from.y <= F.terrace.y + 2 || from.x < F.mooring.wallX);
        if (!forward) return null;
        return P.has('alarm') ? { x: F.balcony.backX, y: F.balcony.y, route: 'inside' } : { x: F.terrace.x, y: F.terrace.y, route: 'inside' };
    },

    heart(x, y, n = 1) {
        const s = this.scene;
        sfx.at(x, y).heart();
        for (let i = 0; i < n; i++) {
            const h = s.add.text(x + (n > 1 ? Phaser.Math.Between(-12, 12) : 0), y, '♥', { fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#e83b3b', resolution: 4 })
                .setOrigin(0.5).setDepth(s.DEPTH.fx);
            this.world.add([h]);
            s.tweens.add({ targets: h, y: y - 22 - i * 4, x: h.x + Phaser.Math.Between(-6, 6), alpha: 0, duration: 1200, delay: i * 150, onComplete: () => h.destroy() });
        }
    },

    // The sunset (population: `scn_sunset`): she comes out of the hatch, the day turns to evening,
    // and the camera goes forward and down to the tip of the bow, where Bumbot settles; then back.
    sunsetScene() {
        const s = this.scene, w = this.world, F = this.F, cam = s.cameras.main;
        this.turning = true;
        w.cut(async () => {
            const her = s.player, Mo = F.mooring, cat = this.tipCat;
            const pan = (x, y, ms) => new Promise(resolve => cam.pan(x, y, ms, 'Sine.easeInOut', true, (_, k) => { if (k === 1) resolve(); }));
            her.setFlipX(true);
            await w.wait(500);
            sfx.sunset(4.5);
            s.tweens.addCounter({ from: 0, to: 1, duration: 4500, ease: 'Sine.easeInOut', onUpdate: t => s.setDusk(t.getValue()) });
            await w.wait(2200);
            // He trots the last of the way to the tip and sits, looking out.
            cam.stopFollow();
            cat.setVisible(true).setPosition(Mo.catX + 150, Mo.y).setFlipX(true).play('bumbot-run');
            cat.anims.timeScale = 0.55;
            const there = pan(Mo.catX + 150, Mo.y - HALF - 14, 3200);
            await w.wait(1500);
            await w.tween({ targets: cat, x: Mo.catX, duration: 1900 });
            cat.anims.timeScale = 1;
            cat.play('bumbot-sit');
            sfx.meow();
            await there;
            await w.wait(1700);
            await pan(her.x, her.y - HALF, 2800);
            cam.startFollow(her, true, 0.15, 0.15);
            cam.setFollowOffset(0, HALF);
            this.turning = false;
            this.P.setFlag('sunset');
        });
    },

    // Bumbot at the tip (population: `scn_catch`; GAME_DESIGN.md §6.1.9): all game she ran at him
    // and he ran. Here too: coming at him she drives him back along the deck, and cornered he darts
    // past her. Standing still, she lets him come; three seconds of it and he is hers.
    updateTip(dt, time) {
        const s = this.scene, her = s.player, Mo = this.F.mooring, cat = this.tipCat, T = this.tip;
        if (T.busy || this.catching) return;
        const on = s.mode === 'play' && s.route === 'inside' && Math.abs(her.y - Mo.y) < 34 && her.x < Mo.wallX;
        if (!on) {
            T.still = 0;
            T.hearts = 0;
            return;
        }
        const dx = cat.x - her.x, dist = Math.abs(dx), vx = her.body.velocity.x;
        const sit = () => {
            if (!T.coming) return;
            T.coming = false;
            cat.anims.timeScale = 1;
            cat.play('bumbot-sit');
        };
        if (Math.abs(vx) > 8 || !s.grounded) {
            sit();
            T.still = 0;
            T.hearts = 0;
            if (dist < TIP.near) cat.setFlipX(dx > 0);              // he keeps an eye on her
            if (Math.abs(vx) > 8 && Math.sign(vx) === Math.sign(dx) && dist < TIP.spook) this.spook(Math.sign(dx));
            return;
        }
        if (dist > TIP.near) {
            sit();
            T.still = 0;
            return;
        }
        T.still += dt * 1000;
        cat.setFlipX(dx > 0);
        // After a second of it he comes, a few steps at a time.
        if (T.still > 1000 && dist > TIP.gap) {
            if (!T.coming) {
                T.coming = true;
                cat.play('bumbot-run');
                cat.anims.timeScale = 0.45;
                sfx.at(cat.x, cat.y).meow();
            }
            cat.x -= Math.sign(dx) * TIP.come * dt;
        } else {
            sit();
        }
        if (Math.floor(T.still / 1000) > T.hearts) {
            T.hearts = Math.floor(T.still / 1000);
            this.heart(cat.x, cat.y - 28);
        }
        if (T.still >= TIP.stillMs) this.catchScene();
    },

    // Her cry at the tip of the bow: he backs off, as when she moves.
    tipHeard(cry) {
        const cat = this.tipCat, T = this.tip, her = this.scene.player;
        if (!cat || !T || T.busy || this.catching || !cat.visible || !this.world.hears(cat.x, this.F.mooring.y)) return;
        this.spook(cat.x < her.x ? -1 : 1);
    },

    // A thrown tangerine coming at him at the tip: he backs off from it, as when she moves. It rolls on.
    // (Only one coming at him: a lob over his head that lands behind him and rolls away sent him after
    // it, part 5.)
    tipOffered(t) {
        const cat = this.tipCat, T = this.tip;
        if (!t.thrown || !cat || !T || T.busy || this.catching || !cat.visible) return false;
        if (Math.abs(t.img.x - cat.x) > 2 * M || Math.abs(t.img.y + 3 - this.F.mooring.y) > 30) return false;
        if ((cat.x - t.img.x) * t.img.body.velocity.x <= 0) return false;
        this.spook(cat.x < t.img.x ? -1 : 1);
        return false;
    },

    // He goes: back along the deck away from her, or, with no deck left behind him, past her.
    spook(dir) {
        const s = this.scene, w = this.world, her = s.player, Mo = this.F.mooring, cat = this.tipCat, T = this.tip;
        T.busy = true;
        T.spooks++;
        T.still = 0;
        T.hearts = 0;
        T.coming = false;
        cat.anims.timeScale = 1;
        sfx.at(cat.x, cat.y).mrrp();
        const limit = dir < 0 ? Mo.x0 : Mo.x1, room = Math.abs(limit - cat.x);
        const settle = () => {
            cat.setFlipX(cat.x > her.x).play('bumbot-sit');
            T.busy = false;
        };
        if (room > 60) {
            const to = cat.x + dir * Math.min(room, TIP.back);
            cat.setFlipX(dir < 0).play('bumbot-run');
            s.tweens.add({ targets: cat, x: to, duration: Math.abs(to - cat.x) / 0.3, onComplete: settle });
        } else {
            const to = Phaser.Math.Clamp(her.x - dir * TIP.dart, Mo.x0 + 30, Mo.x1 - 30);
            cat.setFlipX(dir > 0).play({ key: 'bumbot-leap', startFrame: 2 });
            sfx.at(cat.x, cat.y).scramble();
            s.time.delayedCall(140, () => cat.play('bumbot-run'));
            s.tweens.add({ targets: cat, x: to, duration: Math.abs(to - cat.x) / 0.32, onComplete: settle });
        }
    },

    // The catch: she has stopped chasing. She turns to the sea and spreads her arms in the wind;
    // he comes to her feet; she bends with her arms out, as at every near-catch, and this time he
    // jumps into them.
    catchScene() {
        const s = this.scene, w = this.world, P = this.P, Mo = this.F.mooring;
        this.catching = true;
        w.cut(async () => {
            const her = s.player, cat = this.tipCat;
            cat.anims.timeScale = 1;
            cat.play('bumbot-sit');
            her.setFlipX(false);
            her.anims.play('her-arms-wide');            // (drawn facing the sea ahead: not mirrored)
            await w.wait(1700);
            // Round to her front, or behind her if she stands at the rail itself.
            const side = her.x - 26 >= Mo.x0 - 12 ? -1 : 1, front = her.x + side * 26;
            cat.setFlipX(front < cat.x).play('bumbot-run');
            cat.anims.timeScale = 0.5;
            await w.tween({ targets: cat, x: front, duration: Math.max(350, Math.abs(cat.x - front) / 0.07) });
            cat.anims.timeScale = 1;
            cat.setFlipX(side > 0).play('bumbot-sit');
            sfx.at(cat.x, cat.y).meow();
            this.heart(cat.x, cat.y - 28);
            await w.wait(1000);
            her.setFlipX(side < 0);
            her.anims.play('her-reach');
            await w.wait(520);
            cat.play('bumbot-leap');
            await w.tween({ targets: cat, x: her.x + side * 9, y: her.y - 22, duration: 230, ease: 'Quad.easeOut' });
            cat.setVisible(false).setY(Mo.y);
            s.holding = true;
            s.pose('stand');
            sfx.caught();
            rumble('catch');
            sfx.purr(2.8);
            this.heart(her.x, her.y - PLAYER.height - 2, 6);
            await w.wait(1500);
            s.pose('front');
            await w.wait(1300);
            await w.tween({ targets: s.fade, alpha: 1, duration: 500 });
            P.setFlag('catch');
            await w.wait(400);
            her.setFlipX(false);
            s.pose('stand');
            await w.tween({ targets: s.fade, alpha: 0, duration: 700 });
            this.catching = false;
        });
    },

    // The way home: those she helped stand outside her cabin; each claps her in as she comes by.
    updateWelcome(time) {
        const s = this.scene, her = s.player;
        for (const [id, clip] of [['amb_home_steward', 'thanks'], ['amb_home_manager', 'applaud'], ['amb_home_engineer', 'wave'], ['amb_home_planner', 'applaud'], ['amb_counsellor', 'cheer']]) {
            const p = this.who(id);
            if (!p?.on || s.route !== p.route || Math.abs(her.y - p.y) > 8) continue;
            const d = Math.abs(her.x - p.x);
            if (p.walk || id === 'amb_counsellor') {
                // (The counsellor claps all day; for these two she has a heart as well.)
                if (d < 2 * M && !p.hearted) {
                    p.hearted = true;
                    this.heart(p.x, p.y - PLAYER.height - 4);
                    if (id === 'amb_counsellor') sfx.at(p.x, p.y).cheer(2.2);
                }
                continue;
            }
            // Turned to her as she comes and as she goes; clapping while she is near.
            const near = d < 5.5 * M;
            if (near && p.state !== 'acting') {
                p.dir = her.x < p.x ? -1 : 1;
                this.people.place(p);
                if (!this.people.anim(p, clip)) this.people.idle(p);
                if (!p.greeted) {
                    p.greeted = true;
                    if (clip === 'applaud') sfx.at(p.x, p.y).clap(2.2);
                    else if (clip === 'wave') sfx.at(p.x, p.y).hey();
                    else sfx.at(p.x, p.y).aah();
                }
                p.welcoming = true;
                if (!p.hearted && d < 1.6 * M) {
                    p.hearted = true;
                    this.heart(p.x, p.y - PLAYER.height - 4);
                }
            } else if (!near && p.welcoming) {
                p.welcoming = false;
                this.people.idle(p);
            }
        }
    },

    // Cabin 8206 (population: `scn_home`): her husband is waiting. She steps up onto the bed, Bumbot
    // goes from her arms onto it and curls up between them, she sits down by him. Then the win
    // screen; and after it, the next day.
    homeScene() {
        const s = this.scene, w = this.world, P = this.P, H = this.F.home;
        this.homing = true;
        w.cut(async () => {
            const her = s.player, cat = this.bedCat, top = H.y - BED_TOP;
            const husband = this.who('npc_husband_home');
            await w.wait(500);
            if (husband?.on) this.heart(husband.x, husband.y - 50, 2);
            // To the bed's foot, up onto it, and along it to its head.
            her.body.enable = false;
            her.setFlipX(false);
            s.pose('run', 0.8);
            await w.tween({ targets: her, x: H.stepX, duration: Math.abs(H.stepX - her.x) / 0.1 });
            s.pose('rise');
            await w.tween({ targets: her, x: H.stepX + 12, y: top - 12, duration: 200, ease: 'Quad.easeOut' });
            await w.tween({ targets: her, x: H.stepX + 24, y: top, duration: 170, ease: 'Quad.easeIn' });
            sfx.land();
            s.pose('run', 0.8);
            await w.tween({ targets: her, x: H.sitX, duration: Math.abs(H.sitX - her.x) / 0.09 });
            her.setFlipX(true);
            s.pose('stand');
            await w.wait(600);
            // Out of her arms, onto the bed; round once, and down in a ball.
            cat.setVisible(true).setPosition(her.x - 10, her.y - 24).setFlipX(true).play({ key: 'bumbot-leap', startFrame: 3 });
            sfx.at(cat.x, cat.y).mrrp();
            s.holding = false;
            s.pose('stand');
            await w.tween({ targets: cat, x: H.catX, y: top, duration: 320, ease: 'Quad.easeIn' });
            // (His own clips since he was made again, 2026-11-24: he turns round on the spot, lies down and sleeps,
            // breathing; it was his run slowed and mirrored twice, then one still.)
            cat.play('bumbot-turn');
            await new Promise(resolve => cat.once('animationcomplete', resolve));
            cat.setFlipX(false).play({ key: 'bumbot-lie-down', frameRate: 14 });
            await new Promise(resolve => cat.once('animationcomplete', resolve));
            cat.play('bumbot-asleep');
            sfx.at(cat.x, cat.y).purr(2.9);
            // She sits down by him, her legs over the bed's side.
            if (s.anims.exists('her-read')) {
                her.anims.play('her-read');
                await w.tween({ targets: her, y: top + 13, duration: 500, ease: 'Quad.easeOut' });
            }
            this.heart(cat.x, cat.y - 16, 4);
            if (husband?.on) this.heart(husband.x, husband.y - 50, 2);
            await w.wait(2400);
            await this.winScreen();
            // After the win screen: he sleeps on, she is up; the evening goes on.
            await w.tween({ targets: s.fade, alpha: 1, duration: 600 });
            her.setFlipX(false);
            her.y = top;
            s.pose('stand');
            her.body.enable = true;
            her.body.reset(her.x, top);
            s.stillSince = s.time.now + 6000;           // no bounce on the bed just yet: he is asleep
            this.homing = false;
            P.setFlag('home');
            writeSave(w.save);
            await w.wait(500);
            await w.tween({ targets: s.fade, alpha: 0, duration: 900 });
        });
    },

    // E by him, asleep on the bed, any day after: a purr (and the bed seen close, `setupFinale`).
    purr() {
        const cat = this.bedCat, now = this.scene.time.now;
        if (now > (this.purrAt ?? 0)) {
            this.purrAt = now + 1600;
            sfx.at(cat.x, cat.y).purr(1.6);
        }
        // (No hearts: the bed seen close covers him at once, the user, 2026-11-22.)
        this.scene.tweens.add({ targets: cat, scaleY: 1.06, duration: 260, yoyo: true, repeat: 1 });
        return true;
    },

    // The win screen (§6.1.9, §6.4): over the three of them in the cabin. The game's name, that he is
    // home, what she found on the way; the user's own message under it once it is written
    // (`WIN_MESSAGE` in src/config.js). Any key, after a moment, and the game goes on.
    winScreen() {
        const s = this.scene, w = this.world, save = w.save, T = this.F.totals;
        return new Promise(resolve => {
            const cx = VIEW.width / 2;
            const serif = { fontFamily: 'Georgia, serif', color: '#ffffff', stroke: '#1d2b53' };
            const band = s.add.rectangle(0, 0, VIEW.width, 178, 0x0d0b14, 0.62).setOrigin(0);
            const title = s.add.text(cx, 50, t('title'), { ...serif, fontSize: '72px', strokeThickness: 8 }).setOrigin(0.5);
            const line = s.add.text(cx, 108, t('win.line'), { ...serif, fontSize: '30px', strokeThickness: 5 }).setOrigin(0.5);
            const found = save.collected.filter(id => id.startsWith('tan_')).length;
            const books = Object.values(save.books).filter(b => b === 'returned').length;
            const photos = save.seen.filter(id => id.startsWith('slot_')).length;
            const tally = s.add.text(cx, 148, t('win.tally', found, T.tangerines, books, photos, T.slots, BOOKS),
                { fontFamily: 'Verdana, sans-serif', fontSize: '15px', color: '#fdcbb0' }).setOrigin(0.5);
            const message = pick(WIN_MESSAGE);
            const note = s.add.text(cx, 176, message, { ...serif, fontSize: '22px', strokeThickness: 4, fontStyle: 'italic', align: 'center', wordWrap: { width: VIEW.width - 160 } }).setOrigin(0.5, 0);
            const go = s.add.text(cx, VIEW.height - 34, t('win.go'), { fontFamily: 'Verdana, sans-serif', fontSize: '15px', color: '#ffffff', stroke: '#1d2b53', strokeThickness: 4 }).setOrigin(0.5).setVisible(false);
            if (message) band.setSize(VIEW.width, 176 + note.height + 16);
            const items = [band, title, line, tally, note, go];
            s.uiLayer.add(items);
            this.winItems = items;
            s.tweens.add({ targets: [band, title, line, tally, note], alpha: { from: 0, to: 1 }, duration: 900 });
            sfx.win();
            s.time.delayedCall(2200, () => {
                go.setVisible(true);
                s.tweens.add({ targets: go, alpha: { from: 0.4, to: 1 }, duration: 700, yoyo: true, repeat: -1 });
                const poll = () => {
                    const i = s.controls.state;
                    if (!(i.activatePressed || i.jumpPressed || i.startPressed)) return;
                    s.events.off('postupdate', poll);
                    s.tweens.killTweensOf(go);
                    s.tweens.add({ targets: items, alpha: 0, duration: 500, onComplete: () => { items.forEach(o => o.destroy()); this.winItems = null; resolve(); } });
                };
                s.events.on('postupdate', poll);
            });
        });
    },
};
