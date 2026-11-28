// Near-catch 1 (GAME_DESIGN.md §6.1, region 1; remade 2026-11-24, docs/near-catch-1-remake-log.md), mixed into the
// Story: the Seven Seas' pass on deck 5 aft. Bumbot on its counter at the officer's lunch; at the sight of him she
// stops and cries, and after a little pause dashes at him (the user: "She has to learn the dash here, so I suggest she
// cries and dashes at him"; then, on playing it: "make her cry, and then dash, with a little pause in between"; in
// play D gives both at once); he looks back, turns and bolts forward along the counter behind her, into the fruit bowl, which
// goes off the counter's end (its clip, tools/build_pass.py), three tangerines out of it; he leaps down and is off
// through the restaurant; she turns after him, turns to us, shrugs, and is free: "D to dash".
//
// One clock (`T`, ms of the game's time since the scene began) and everything a function of it, on the ship
// scene's scripted update: nothing waits on a tween's own clock. Where things stand: `PASS` in src/config.js, from
// his spot (`BEATS` in tools/population.py); the pieces' sizes: assets/ship/pass/pass.json.

import { PLAYER, BUMBOT, CRY, LUNGE, PASS } from '../config.js';
import { sfx } from '../sfx.js';
import { t } from '../lang.js';
import { rumble } from '../rumble.js';

export const pass = {
    setupPass() {
        const s = this.scene, w = this.world, D = s.DEPTH;
        const cat = s.cats.find(c => c.flag === 'bb1');
        if (!cat || !s.textures.exists('pass-counter')) return;
        const L = s.cache.json.get('pass-layout');
        const x0 = cat.sprite.x + PASS.counter, F = cat.floor, top = F - L.counter.h;
        cat.custom = true;              // (its own scene: not the ship scene's `nearCatch`)
        // The counter: behind everything that stands on it and behind her. The plate: in front of his nose.
        const counter = s.add.image(x0, F, 'pass-counter').setOrigin(0, 1).setDepth(D.props - 0.05);
        const plate = s.add.image(cat.sprite.x + PASS.plate, top, 'pass-plate').setOrigin(0.5, 1).setDepth(D.props + 0.005);
        // The bowl's fall: a frame stands with its column `x` at the counter's end, its row `y` on the floor's line.
        const fall = s.add.sprite(x0 - L.fall.x, F - L.fall.y, 'pass-bowl-fall', 0).setOrigin(0).setDepth(D.props - 0.01).setVisible(false);
        w.add([counter, plate, fall]);
        this.pass = { cat, L, x0, F, top, counter, plate, fall, bowl: w.things.find(x => x.id === 'prop_bowl_7s') };
        if (this.P.has('bb1')) this.passAfter();
    },

    // As it is once he has been: the bowl on the floor, its fruit spilled.
    passAfter() {
        const q = this.pass;
        if (!q) return;
        q.bowl?.img.setVisible(false);
        if (q.bowl) q.bowl.items = [];          // (the world's refresh shows a thing's items again)
        q.fall.setFrame(q.L.fall.frames - 1).setVisible(true);
        q.cat.gone = q.cat.away = true;
        q.cat.sprite.setVisible(false);
    },

    // She comes within `sight` of him on his floor: the scene. In a jump across that line she comes straight down
    // where she crossed it, and the scene begins as she lands: he cannot be jumped over (he could before, and the
    // scene then began behind him with her hung over the floor).
    updatePass() {
        const q = this.pass, s = this.scene;
        if (!q || q.cat.gone || q.cat.hidden || s.mode !== 'play' || s.route !== 'inside') return;
        const p = s.player, dx = q.cat.sprite.x - p.x;
        if (Math.abs(dx) > PASS.sight || p.y > q.F + 1 || p.y < q.F - PASS.airUp) return;
        if (p.body.blocked.down || p.body.touching.down) {
            if (Math.abs(p.y - q.F) <= 1) this.passBeat();
            return;
        }
        q.cat.gone = true;
        s.mode = 'scripted';
        p.body.setVelocityX(0);
        p.body.setAccelerationX(0);
        s.script = () => {
            if (p.body.blocked.down || p.body.touching.down || p.y >= q.F) {
                s.script = null;
                this.passBeat();
            } else {
                s.pose(p.body.velocity.y < 0 ? 'rise' : 'fall');
            }
        };
    },

    passBeat() {
        const q = this.pass, s = this.scene, w = this.world, p = s.player, k = q.cat.sprite, { F, top, L } = q;
        const k0 = k.x, pace = p.anims.timeScale;
        q.cat.gone = true;
        s.mode = 'scripted';
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.y = F;
        if (s.crawling) s.crawling = false;
        p.setFlipX(false);

        // Her dash: from where she is to his spot, at the lunge's speed, `pause` ms after her cry (the user: "a little
        // pause in between"; only here). (From nearer than a dash worth seeing, later still, so that he is off before
        // she is in front of him.)
        const x0 = p.x, stop = Math.max(x0, k0 + PASS.stop), v = PLAYER.runSpeed * LUNGE.speed;
        const dashMs = (stop - x0) / v * 1000, dashAt = Math.max(PASS.pause, PASS.minMs - dashMs), arrive = dashAt + dashMs;
        // His part, by her arrival: a look back over his shoulder, a turn, and off as she is `boltBefore` ms short.
        const runAt = Math.max(PASS.lookAt + PASS.lookMs + PASS.turnMs, arrive - PASS.boltBefore), turnAt = runAt - PASS.turnMs;
        const hitAt = runAt + (-PASS.hit) / BUMBOT.runSpeed * 1000;             // his nose at the bowl
        const leapAt = runAt + (-PASS.leap) / BUMBOT.runSpeed * 1000;           // off the counter's end
        const landAt = leapAt + PASS.leapMs, landX = k0 + PASS.land;
        const fallAt = hitAt + PASS.slideMs;                                    // the bowl's own clip takes over
        const frontAt = Math.max(arrive, hitAt) + PASS.watchMs;                 // she turns to us

        // The bowl's three tangerines: each from the bowl's mouth through the air to the floor, a small bounce, a roll
        // to where the data has it (tools/population.py `tan_5_bowl_*`).
        const fruit = [];
        const spill = () => {
            for (const e of w.pending.filter(e => e.id.startsWith('tan_5_bowl'))) {
                w.pending.splice(w.pending.indexOf(e), 1);
                w.placeTangerine(e);
                const tan = s.tangerines.find(x => x.id === e.id);
                if (!tan) continue;
                const i = fruit.length;
                tan.glint.setVisible(false);
                fruit.push({ tan, rest: e.x, from: [q.x0 + PASS.mouth[0] - 4 * i, F + PASS.mouth[1] - 3 * i], lands: e.x + PASS.roll[0] + PASS.roll[1] * i,
                             at: fallAt + i * 45, air: PASS.air + 35 * i, rollMs: PASS.rollMs + 120 * i });
                tan.sprite.setPosition(...fruit[i].from);
            }
        };
        const moveFruit = (T) => {
            for (const f of fruit) {
                const a = T - f.at, sp = f.tan.sprite;
                if (a < 0) continue;
                if (a < f.air) {
                    // (Up a little, then down to the floor at `air` ms.)
                    const u = a / f.air, g = 900, ta = f.air / 1000, vy = (F - f.from[1] - 0.5 * g * ta * ta) / ta, ts = a / 1000;
                    sp.setPosition(f.from[0] + (f.lands - f.from[0]) * u, Math.min(F, f.from[1] + vy * ts + 0.5 * g * ts * ts));
                } else {
                    const u = Math.min(1, (a - f.air) / f.rollMs), b = Math.min(1, (a - f.air) / PASS.bounceMs);
                    if (!f.landed) { f.landed = true; sfx.at(sp.x, F).roll(); }
                    sp.setPosition(f.lands + (f.rest - f.lands) * (1 - (1 - u) * (1 - u)), F - 4 * PASS.bounce * b * (1 - b));
                    if (u === 1 && !f.done) {
                        f.done = true;
                        f.tan.glint.setPosition(sp.x - 2, sp.y - 6).setVisible(true);
                    }
                }
            }
        };

        let T = 0, trailAt = 0, herDone = false;
        const did = {};
        const once = (key, at, fn) => { if (!did[key] && T >= at) { did[key] = true; fn(); } };
        const end = () => {
            s.script = null;
            fruit.forEach(f => { f.tan.sprite.setPosition(f.rest, F); f.tan.glint.setPosition(f.rest - 2, F - 6).setVisible(true); });
            p.body.enable = true;
            p.body.reset(p.x, p.y);
            p.anims.timeScale = pace;
            s.pose('stand');
            p.setFlipX(true);               // (the way he went)
            s.mode = 'play';
            this.P.setFlag('bb1');          // (the lunge is hers, the lunch is hers to take: `flagGives`, `src_lunch`)
            // The one hint of a new move (the user: "D to dash", both languages, and the controller's button).
            w.say(t(s.controls.device === 'pad' ? 'hint.dash.pad' : 'hint.dash'), PASS.hintMs, { kind: 'plate' });
        };

        // She stops where she is and cries; the dash, with its own sound and rumble, comes after the pause.
        s.pose('stand');
        s.cryOut(CRY.bubbleMs);
        s.script = (dt) => {
            T += dt * 1000;

            // --- She ---
            once('dash', dashAt, () => { s.pose('run', 1.8); sfx.lunge(); rumble('lunge'); });
            if (T >= dashAt && T < arrive) {
                p.x = x0 + (T - dashAt) / 1000 * v;
                if (T - trailAt > 45) {
                    trailAt = T;
                    const ghost = s.add.image(p.x, p.y, 'her', p.frame.name).setOrigin(0.5, 1).setAlpha(0.45).setDepth(s.DEPTH.player - 0.5);
                    s.worldLayer.add(ghost);
                    s.tweens.add({ targets: ghost, alpha: 0, duration: 260, onComplete: () => ghost.destroy() });
                }
            }
            once('arrive', arrive, () => { p.x = stop; s.pose('stand'); sfx.lungeEnd(); });
            once('turn', Math.max(arrive, fallAt) + PASS.turnHer, () => p.setFlipX(true));
            once('front', frontAt, () => {
                // (Turned to us, she shrugs: the user, 2026-11-24; her `shrug` at its own pace, then a moment.)
                p.setFlipX(false);
                const after = () => s.time.delayedCall(PASS.afterMs, () => { herDone = true; });
                if (!s.anims.exists('her-shrug')) { s.pose('front'); return after(); }
                p.anims.timeScale = 1;
                p.anims.play('her-shrug');
                // (Her shrug's last frame is held: her front still is not shown after it. The user, 2026-11-24.)
                p.once('animationcomplete-her-shrug', () => after());
            });

            // --- He ---
            once('look', PASS.lookAt, () => k.play({ key: 'bumbot-look-back', frameRate: PASS.lookFrames / PASS.lookMs * 1000 }));
            once('looked', Math.min(turnAt, PASS.lookAt + PASS.lookMs), () => k.anims.pause());
            once('turnHim', turnAt, () => {
                k.play({ key: 'bumbot-turn', frameRate: s.anims.get('bumbot-turn').frames.length / PASS.turnMs * 1000 });
                sfx.at(k.x, k.y).mrrp();
            });
            once('run', runAt, () => { k.setFlipX(true).play('bumbot-run'); rumble('bolt'); sfx.at(k.x, k.y).scramble(); });
            if (T >= runAt && T < leapAt) k.x = k0 - (T - runAt) / 1000 * BUMBOT.runSpeed;
            // (From its second frame: the first is him reared straight up, which is a jump on the spot's.)
            once('leap', leapAt, () => k.play({ key: 'bumbot-leap', startFrame: 1, frameRate: (s.anims.get('bumbot-leap').frames.length - 1) / PASS.leapMs * 1000 }));
            if (T >= leapAt && T < landAt) {
                // (Off the counter's end over the falling bowl and down to the floor: the leap's frames each on its
                // lowest pixel, the arc the scene's.)
                const u = (T - leapAt) / PASS.leapMs;
                k.setPosition(k0 + PASS.leap + (landX - k0 - PASS.leap) * u, top + (F - top) * u - 4 * PASS.arc * u * (1 - u));
            }
            once('land', landAt, () => { k.setPosition(landX, F).play('bumbot-run'); });
            if (T >= landAt && !q.cat.away) {
                k.x = landX - (T - landAt) / 1000 * BUMBOT.runSpeed;
                if (k.x < s.cameras.main.worldView.x - 40) {
                    q.cat.away = true;
                    k.setVisible(false).stop();
                }
            }

            // --- The bowl ---
            if (q.bowl?.img.visible && T >= hitAt && T < fallAt) q.bowl.img.x = q.bowl.x - PASS.slide * (T - hitAt) / PASS.slideMs;
            once('hit', hitAt, () => sfx.at(q.x0, top).plop());
            once('fall', fallAt, () => {
                q.bowl?.img.setVisible(false);
                if (q.bowl) q.bowl.items = [];
                q.fall.setFrame(0).setVisible(true);
                spill();
            });
            if (T >= fallAt) {
                const f = Math.min(L.fall.frames - 1, Math.floor((T - fallAt) / 1000 * PASS.fallFps));
                if (q.fall.frame.name !== f) q.fall.setFrame(f);
                once('crash', fallAt + PASS.landFrame / PASS.fallFps * 1000, () => sfx.at(q.x0, F).crash());
            }
            moveFruit(T);

            if (herDone && q.cat.away) end();
        };
    },
};
