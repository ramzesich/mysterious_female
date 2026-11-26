// Near-catch 3 (GAME_DESIGN.md §6.1, region 3; remade 2026-11-24, docs/near-catch-3-remake-log.md), mixed into the
// Story: the Stardust Lounge's stage on deck 6. Bumbot washes at centre stage in a spotlight of his own, the fly
// rope's loop over him; the stage manager is turned to his two dancers, rehearsing at the aft curtain, his back to
// the cat. As she comes in front of the forward curtain she is taken and starts toward him on tiptoe; the stage
// manager turns, starts back and thrusts his clipboard at the cat; the dancers stop; the rival runs out of the
// forward wing ahead of her, and she starts back; Bumbot leaps into the loop; under the hanging lamp the rival leaps
// at him, his net swung overhead, and the net catches the lamp: he hangs on it and swings, and the lamp, which is
// the other end of the rope's line, comes down as the loop with Bumbot goes up behind the valance; he drops onto the
// stage's hatch, which gives way, and is gone into the galley's flour; the lamp, let go, swings from there for good;
// she looks up after Bumbot, turns to us, shrugs, and is free; the stage manager sneezes for the first time.
//
// One clock (`T`, ms of the game's time since the scene began) and everything a function of it, on the ship
// scene's scripted update. Where things stand: the stage's data (`STAGE` in tools/population.py), `STAGE` in
// src/config.js, and the pieces' own layout, assets/ship/stage/stage.json (tools/build_stage.py).

import { STAGE } from '../config.js';
import { sfx } from '../sfx.js';
import { rumble } from '../rumble.js';

// (On the fly rope: where the rope stands in his clip's frames, px before his middle; he hangs this far under
// the loop's top.)
const ROPE_CAT = { x: 16.5, y: 10 };
const ROPE = { dark: 0x7a4528, light: 0xab947a };

export const stage = {
    setupStage() {
        const s = this.scene, w = this.world, st = w.data.stage, D = s.DEPTH;
        if (!st || !s.textures.exists('stage-snag')) return;
        const L = s.cache.json.get('stage-layout');
        const cat = s.cats.find(c => c.flag === 'bb3');
        // The hatch: a seam in the boards until it has given way, then open, its lid up, a ladder's top in it.
        const shut = s.add.image(st.x + L.trap.shut[0], st.top + L.trap.shut[1], 'stage-trap-shut').setOrigin(0).setDepth(D.decor + 0.3);
        const open = s.add.image(st.x + L.trap.open[0], st.top + L.trap.open[1], 'stage-trap-open').setOrigin(0).setDepth(D.decor + 0.3);
        // His spotlight: the lighting bar's lantern over him, its cone and its pool on the boards (flat by nature).
        const spot = s.add.graphics().setDepth(D.decor + 0.3);
        const cx = cat ? cat.sprite.x : st.ropeX - ROPE_CAT.x, half = STAGE.spot.half;
        spot.fillStyle(0xfbff86, STAGE.spot.cone).fillTriangle(st.spotX, st.top + L.stage.lens, cx - half, st.floor, cx + half, st.floor);
        spot.fillStyle(0xfbff86, STAGE.spot.pool).fillEllipse(cx, st.floor - 2, half * 2, 5);
        // The fly rope, a loop at its end; the valance again over what goes up behind it.
        const rope = s.add.graphics().setDepth(D.props + 0.02);
        const valance = s.add.image(st.x, st.top, 'stage-valance').setOrigin(0).setDepth(D.props + 0.1);
        // The rival's clip and the flour, each where its picture was made.
        const snag = s.add.sprite(st.x + L.snag.x, st.top, 'stage-snag', 0).setOrigin(0).setDepth(D.player + 0.31).setVisible(false);
        const puff = s.add.sprite(st.x + L.puff.x, st.top + L.puff.y, 'stage-puff', 0).setOrigin(0).setDepth(D.props + 0.2).setVisible(false);
        w.add([shut, open, spot, rope, valance, snag, puff]);
        const light = w.movers.find(m => m.def?.id === 'haz_light');
        this.stage = { cat, L, st, shut, open, rope, snag, puff, light, up: st.floor - STAGE.loop };
        if (cat) cat.custom = true;              // (its own scene: not the ship scene's `nearCatch`)
        if (this.P.has('bb3')) this.stageAfter();
        else {
            open.setVisible(false);
            this.drawRope(this.stage.up);
        }
    },

    drawRope(endY) {
        const q = this.stage, st = q.st, g = q.rope.clear(), y0 = st.top + 12;
        q.ropeEnd = endY;
        if (endY > y0) {
            g.fillStyle(ROPE.dark, 1).fillRect(st.ropeX - 1, y0, 2, endY - y0);
            g.fillStyle(ROPE.light, 1);
            for (let y = y0 + 2; y < endY; y += 4) g.fillRect(st.ropeX - 1, y, 1, 2);
        }
        g.lineStyle(2, ROPE.dark, 1).strokeEllipse(st.ropeX, endY + 5, 8, 10);
    },

    // As it is once he has been: the hatch open, the loop hauled up behind the valance, the lamp low and swinging
    // (its own flag), the stage manager turned to the hole.
    stageAfter() {
        const q = this.stage;
        if (!q) return;
        q.shut.setVisible(false);
        q.open.setVisible(true);
        q.snag.setVisible(false);
        this.drawRope(q.up - STAGE.ropeGain * (q.light ? q.light.def.long - q.light.def.short : 44));
        if (q.cat) {
            q.cat.gone = q.cat.away = true;
            q.cat.sprite.setVisible(false);
        }
        const m = this.who('npc_stagemanager');
        if (m && m.state !== 'acting') {
            m.dir = -1;
            this.people.place(m);
        }
    },

    // She comes within `sight` of him on his floor: the scene. In a jump across that line she comes straight down
    // where she crossed it, and the scene begins as she lands (as at the pass and in the Library).
    updateStage() {
        const q = this.stage, s = this.scene;
        if (!q?.cat || q.cat.gone || q.cat.hidden || s.mode !== 'play' || s.route !== 'inside') return;
        const p = s.player, F = q.st.floor, dx = q.cat.sprite.x - p.x;
        if (Math.abs(dx) > STAGE.sight || p.y > F + 1 || p.y < F - STAGE.airUp) return;
        if (p.body.blocked.down || p.body.touching.down) {
            if (Math.abs(p.y - F) <= 1) this.stageBeat();
            return;
        }
        q.cat.gone = true;
        s.mode = 'scripted';
        p.body.setVelocityX(0);
        p.body.setAccelerationX(0);
        s.script = () => {
            if (p.body.blocked.down || p.body.touching.down || p.y >= F) {
                s.script = null;
                this.stageBeat();
            } else {
                s.pose(p.body.velocity.y < 0 ? 'rise' : 'fall');
            }
        };
    },

    stageBeat() {
        const q = this.stage, s = this.scene, w = this.world, p = s.player, k = q.cat.sprite, { st, L } = q;
        const F = st.floor, k0 = k.x, pace = p.anims.timeScale, light = q.light;
        const sm = this.who('npc_stagemanager'), dancers = ['amb_dancer_her', 'amb_dancer_him'].map(id => this.who(id)).filter(d => d?.on);
        q.cat.gone = true;
        s.mode = 'scripted';
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.y = F;
        if (s.crawling) s.crawling = false;
        const side = p.x <= k0 ? 1 : -1;
        p.setFlipX(side < 0);
        // (With something in her hands she only stands and watches. Forward of the curtain, as she comes, she starts
        // toward him on tiptoe; anywhere else, where only every lock open can have put her, she stands.)
        const hands = !w.carry && !s.holding && s.anims.exists('her-start-back') && s.anims.exists('her-look-up');
        const creep = hands && side > 0 && k0 - p.x > STAGE.sight - 30 && s.anims.exists('her-creep-tiptoe');
        const x0 = p.x;

        // The rival: out of the wing at a run, his clip from where its first frame has him; its frames by the clock.
        const clipX = st.x + L.snag.x + L.snag.start;
        const clipAt = STAGE.rivalAt + (clipX - st.wingX) / STAGE.rivalSpeed * 1000;
        // (His clip's steps: each a frame and how long it is shown; `at[i]` when step i begins, from the clip's start.)
        const clip = STAGE.clip, at = [0];
        for (const [, ms] of clip) at.push(at.at(-1) + ms);
        const stepOf = (t) => { let i = 0; while (i < clip.length - 1 && t >= at[i + 1]) i++; return i; };
        const first = (f) => at[clip.findIndex(c => c[0] === f)];
        const openAt = clipAt + first(L.snag.open), goneAt = clipAt + at.at(-1);
        // Bumbot: up from his washing at the shout; a leap into the loop as the rival comes out, the catch; then the
        // loop goes up as the lamp comes down.
        const leapAt = STAGE.rivalAt + STAGE.leapAfter, ropeAt = leapAt + STAGE.leapMs;
        const hangX = st.ropeX - ROPE_CAT.x, hangY = q.up + ROPE_CAT.y;
        const lens0 = L.snag.lens[0][1], fall = light ? light.def.long - light.def.short : L.snag.lens[L.snag.open][1] - lens0;
        const drop = (f) => (f >= L.snag.open ? fall : L.snag.lens[f][1] - lens0);
        const lensAt = (f) => ({ x: st.x + L.snag.x + L.snag.lens[f][0] + 1, y: st.top + L.snag.lens[f][1] });
        const backAt = STAGE.rivalAt + STAGE.backAfter, lookAt = goneAt + STAGE.lookAfter, shrugAt = lookAt + STAGE.shrugAfter;
        const sneezeAt = goneAt + STAGE.sneezeAfter;

        let T = 0, herDone = false, steps = 0, rival = null, step = -1;
        const did = {};
        const once = (key, at, fn) => { if (!did[key] && T >= at) { did[key] = true; fn(); } };
        const end = () => {
            s.script = null;
            p.body.enable = true;
            p.body.reset(p.x, p.y);
            p.anims.timeScale = pace;
            s.pose('stand');
            p.setFlipX(side < 0);
            s.cameras.main.followOffset.x = 0;
            k.setCrop();
            q.snag.setVisible(false);
            s.mode = 'play';
            this.sneezeAt = s.time.now + Math.max(0, sneezeAt + STAGE.sneezeEvery - T);
            this.P.setFlag('bb3');          // (the hatch open, the lamp swinging, his pills wanted: `stageAfter`)
        };

        p.anims.timeScale = 1;
        if (creep) p.anims.play('her-creep-tiptoe'); else s.pose('stand');
        s.script = (dt) => {
            T += dt * 1000;
            // (The picture goes ahead of her: the whole stage in it, to its aft curtain.)
            if (side > 0) s.cameras.main.followOffset.x = -STAGE.ahead * Math.min(1, T / STAGE.aheadMs);

            // --- The stage manager and his dancers ---
            once('notice', STAGE.noticeAt, () => {
                if (!sm?.on) return;
                sm.dir = k0 < sm.x ? -1 : 1;
                this.people.place(sm);
                this.people.play(sm, 'notice', { stay: true });
            });
            once('stop', STAGE.danceStop, () => {
                for (const d of dancers) {
                    d.dir = k0 < d.x ? -1 : 1;
                    this.people.place(d);
                    this.people.play(d, 'startle', { stay: true }).then(() => { d.idle = 'idle'; this.people.idle(d); });
                }
            });
            once('sneeze', sneezeAt, () => {
                if (!sm?.on) return;
                sfx.at(sm.x, sm.y).sneeze();
                this.people.play(sm, 'sneeze');
            });

            // --- She ---
            if (creep && T < STAGE.tipMs) {
                p.x = x0 + STAGE.tipFps * STAGE.tipPx * T / 1000;
                if (T >= steps * 4 / STAGE.tipFps * 1000) { steps++; sfx.tiptoe(); }
            }
            // (The shout stops her mid-step; the rival out of the wing ahead of her, she starts back.)
            once('freeze', STAGE.tipMs, () => { if (creep) p.anims.pause(); });
            once('back', backAt, () => {
                if (!hands) return;
                p.anims.play('her-start-back');
                sfx.gasp();
            });
            once('look', lookAt, () => { if (hands) p.anims.play('her-look-up'); });
            once('front', shrugAt, () => {
                // (Turned to us, she shrugs, as after every near-catch. With her hands full she only looks on.)
                const after = () => s.time.delayedCall(STAGE.afterMs, () => { herDone = true; });
                if (!hands || !s.anims.exists('her-shrug')) return after();
                p.setFlipX(false);
                p.anims.play('her-shrug');
                p.once('animationcomplete-her-shrug', () => after());
            });

            // --- The rival ---
            once('rival', STAGE.rivalAt, () => {
                rival = this.people.add({ id: 'riv_stage', who: 'rival', x: st.wingX, y: F, route: 'inside', face: 1, owned: true });
                if (!rival) return;
                rival.on = true;
                rival.sprite.anims.stop();
                // (Out from behind the proscenium's edge: his picture cut there, as someone in a doorway's.)
                this.people.doorway(rival, st.x + STAGE.wingEdge, st.x + 2000, st.top - 200, F + 8);
            });
            if (rival && T < clipAt) {
                rival.x = st.wingX + (T - STAGE.rivalAt) / 1000 * STAGE.rivalSpeed;
                // (His run's frames on the clock, so that the clip's first frame is the next one of his stride.)
                const n = rival.meta.anims.charge.length, left = Math.ceil((clipAt - T) * STAGE.runFps / 1000);
                rival.sprite.setFrame(rival.meta.anims.charge[(((n - 1 - left) % n) + n) % n]);
                this.people.place(rival);
            }
            once('clip', clipAt, () => {
                if (rival) {
                    rival.gone = true;
                    rival.on = false;
                    rival.items.forEach(i => i.setVisible(false));
                }
                q.snag.setFrame(0).setVisible(true);
            });
            if (T >= clipAt) {
                const i = stepOf(T - clipAt);
                if (i !== step) {
                    const f = clip[i][0], again = clip.slice(0, i).some(c => c[0] === f);
                    step = i;
                    q.snag.setFrame(f);
                    // (The lamp is the game's own, behind his net: where each frame's was measured, until he lets go.)
                    if (light && f >= 1 && f < L.snag.open) light.hold(lensAt(f));
                    if (f === STAGE.swishFrame) sfx.at(clipX, F).swish();
                    if (f === STAGE.hookFrame) s.cameras.main.shake(120, 0.002);
                    // (The lamp's cable takes his weight, and again each time he swings back on it.)
                    if (f === STAGE.hookFrame || (again && f === STAGE.hookFrame + 1)) sfx.at(clipX, F).creak();
                }
            }
            once('open', openAt, () => {
                q.shut.setVisible(false);
                q.open.setVisible(true);
                sfx.at(st.trapX, F).trapdoor();
                sfx.at(st.trapX, F).yelp();
                s.cameras.main.shake(200, 0.004);
                if (light) light.release(lensAt(L.snag.open - 1), STAGE.kickMs);
            });
            once('gone', goneAt, () => {
                q.snag.setVisible(false);
                sfx.at(st.trapX, F).flump();
                q.puff.setVisible(true).play('stage-puff');
                q.puff.once('animationcomplete', () => q.puff.setVisible(false));
            });

            // --- Bumbot ---
            once('up', STAGE.catUp, () => k.play({ key: 'bumbot-stand-up', startFrame: STAGE.upFrom, frameRate: STAGE.upFps }));
            once('leap', leapAt, () => {
                k.setFlipX(false).play('bumbot-leap');
                rumble('bolt');
                sfx.at(k.x, k.y).mrrp();
            });
            if (T >= leapAt && T < ropeAt) {
                const u = (T - leapAt) / STAGE.leapMs, e = 1 - (1 - u) * (1 - u);
                k.setPosition(k0 + (hangX - k0) * e, F + (hangY - F) * e);
            }
            once('rope', ropeAt, () => {
                k.setPosition(hangX, hangY).setDepth(q.rope.depth + 0.001).play({ key: 'bumbot-rope', startFrame: STAGE.ropeFrom, frameRate: STAGE.ropeFps });
            });
            if (T >= clipAt && !q.cat.away) {
                // (The loop's rise for the lamp's drop, between his clip's frames too: one line, its two ends.)
                const t = T - clipAt, i = stepOf(t), j = Math.min(clip.length - 1, i + 1);
                const d = drop(clip[i][0]) + (drop(clip[j][0]) - drop(clip[i][0])) * Math.min(1, (t - at[i]) / clip[i][1]);
                const endY = q.up - STAGE.ropeGain * d;
                if (endY !== q.ropeEnd) {
                    if (!did.whisk && d > 1) { did.whisk = true; sfx.at(st.ropeX, F).whip(); }
                    this.drawRope(endY);
                }
                if (T >= ropeAt) {
                    k.y = q.ropeEnd + ROPE_CAT.y;
                    // (Nothing of him over the stage's top: he is behind its valance, then gone into the flies.)
                    const cut = Math.max(0, st.top - (k.y - k.height));
                    if (cut > 0) k.setCrop(0, cut, k.width, k.height - cut);
                    if (t >= first(L.snag.open + 1)) {
                        q.cat.away = true;
                        k.setVisible(false).stop();
                    }
                }
            }

            if (herDone && q.cat.away && T >= goneAt + STAGE.settleMs) end();
        };
    },
};
