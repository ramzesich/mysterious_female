// Region 6's part of the story (GAME_DESIGN.md §6.1.3 "Lido", docs/population.md deck 11 and scene
// 7), mixed into the Story: Bumbot fishing at the pool and what the kid's water pistol does about it,
// the pool draining; the kid on the aft pool deck (a hazard, then an ally); the soft serve machine
// and its swirl; the cone for the kid, the canister, the table with her husband; the chess set, the
// hot tub; the wet paw prints aft. Places come from maps/world.json (`lido`).

import { PLAYER, SWIM } from '../config.js';
import { sfx } from '../sfx.js';
import { writeSave } from '../save.js';

const M = 48;
// The swirl: how long a full one takes (ms), and where it is a stub, perfect, or too much.
const SWIRL = { ms: 2400, none: 0.14, perfect: 0.58, over: 0.84, max: 1.08 };
const KID = { walk: 46, run: 150, sees: 4 * M, jet: 3 * M, every: 2500, tell: 480, hide: 10000 };

export const lido = {
    setupLido() {
        const s = this.scene, w = this.world, L = w.data.lido, D = s.DEPTH, P = this.P;
        if (!L) return;
        this.L = L;
        this.lidoTextures();
        // Near-catch 5 has its own scene: he fishes at the first pool's aft rim, facing the water.
        const cat = s.cats.find(c => c.flag === 'bb5');
        if (cat) {
            cat.custom = true;
            cat.sprite.setFlipX(true);
        }
        this.poolCat = cat;
        // The drain's lever on its housing, by the rim.
        this.lever = s.add.image(L.leverX, L.y, P.has('drain') ? 'lever-down' : 'lever-up').setOrigin(0.5, 1).setDepth(D.props - 0.03);
        // The kid's jets of water; the wet paw prints aft; the chess pawn she moves.
        this.jetG = s.add.graphics().setDepth(D.player + 0.2);
        this.paws = s.add.graphics().setDepth(D.props - 0.04).setAlpha(0);
        this.paws.fillStyle(0x4d65b4, 0.8);
        for (let x = L.pawsA, n = 0; x < L.pawsB; x += 14, n++) {
            const y = L.y - (n % 2 ? 2 : 4);
            this.paws.fillRect(x, y, 3, 2).fillRect(x - 1, y - 1, 1, 1).fillRect(x + 1, y - 2, 1, 1).fillRect(x + 3, y - 1, 1, 1);
        }
        this.pawn = s.add.image(L.chessX + 14, L.y - 2, 'chess-pawn').setOrigin(0.5, 1).setDepth(D.decor + 0.3);
        if (this.P.save.seen.includes('sec_chess')) this.pawn.x += 16;
        // The machine: its light (green: it has mix), the cone under its spout, the swirl's meter.
        this.mLight = s.add.rectangle(L.machineX + 9, L.y - 39, 3, 2, 0x1ebc73).setDepth(D.decor + 0.3);
        this.mCone = s.add.graphics().setDepth(D.props + 0.04).setVisible(false);
        this.mMeter = s.add.graphics().setDepth(D.fx + 0.4).setVisible(false);
        this.mKey = w.glyph(L.machineX, L.y - 62, 'hold E');
        w.add([this.lever, this.jetG, this.paws, this.pawn, this.mLight, this.mCone, this.mMeter]);
        w.things.push({ id: 'src_icecream', x: L.machineX, y: L.y, route: 'inside', items: [], reach: 22, interact: () => this.machine() });
        w.things.push({ id: 'sec_chess', x: L.chessX, y: L.y, route: 'inside', items: [], reach: 26, interact: () => this.chess() });
        w.things.push({ id: 'sec_hottub', x: L.tubX, y: L.y, route: 'inside', needs: 'bb5', items: [], reach: 22, interact: () => this.hotTub() });
        // The kid: ducked down in the hot tub until the beat (his cap over its rim); on the deck after.
        const kid = this.who('npc_kid');
        if (kid) {
            kid.mode = 'patrol';
            kid.dir = -1;
            kid.nextSquirt = 0;
            kid.pauseUntil = 0;
        }
        this.refreshLido();
    },

    lidoTextures() {
        const s = this.scene;
        const make = (key, w, h, draw) => {
            if (s.textures.exists(key)) return;
            const g = s.make.graphics({ x: 0, y: 0 }, false);
            draw(g);
            g.generateTexture(key, w, h);
            g.destroy();
        };
        const housing = g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 14, 16, 12);
            g.fillStyle(0x9babb2, 1).fillRect(1, 15, 14, 10);
            g.fillStyle(0xf9c22b, 1).fillRect(1, 21, 14, 2);
            g.fillStyle(0x2e222f, 1).fillRect(3, 21, 2, 2).fillRect(7, 21, 2, 2).fillRect(11, 21, 2, 2);
            g.fillStyle(0x625565, 1).fillRect(6, 15, 4, 2);
        };
        make('lever-up', 16, 26, g => {
            housing(g);
            g.fillStyle(0x2e222f, 1).fillRect(6, 3, 4, 13).fillRect(5, 0, 6, 5);
            g.fillStyle(0xc7dcd0, 1).fillRect(7, 5, 2, 10);
            g.fillStyle(0xe83b3b, 1).fillRect(6, 1, 4, 3);
        });
        make('lever-down', 16, 26, g => {
            housing(g);
            g.fillStyle(0x2e222f, 1).fillRect(8, 10, 8, 4).fillRect(12, 9, 4, 6);
            g.fillStyle(0xc7dcd0, 1).fillRect(8, 11, 5, 2);
            g.fillStyle(0xe83b3b, 1).fillRect(13, 10, 2, 4);
        });
        make('chess-pawn', 12, 20, g => {
            g.fillStyle(0x625565, 1).fillRect(0, 18, 12, 2);
            g.fillStyle(0x2e222f, 1).fillRect(1, 16, 10, 2).fillRect(3, 8, 6, 8).fillCircle(6, 5, 4);
        });
    },

    // What shows by what has happened: the lever, the machine's light, his bubble's picture.
    refreshLido() {
        const P = this.P, L = this.L;
        if (!L) return;
        this.lever?.setTexture(P.has('drain') ? 'lever-down' : 'lever-up');
        const empty = P.has('kid_fed') && !P.has('refilled');
        this.mLight?.setFillStyle(empty ? 0xe83b3b : 0x1ebc73);
        const h = this.who('npc_husband');
        if (h?.bubbleItems) h.bubbleItems[1].setTexture(this.world.icon(P.has('refilled') ? 'softserve' : 'canister'));
    },

    updateLido(dt, time, input) {
        const s = this.scene, L = this.L;
        if (!L) return;
        const her = s.player;
        const near = Math.abs(her.y - L.y) < 300;
        if (!near) return;
        this.poolWatch(time);
        this.kidInTub(time);
        this.kidOnDeck(dt, time);
        this.swirling(dt, time, input);
        if (this.soaking && time > this.soaking.from && (input.jumpPressed || input.activatePressed || input.leftPressed || input.rightPressed
            || input.upPressed || input.downPressed)) this.soaking.out = true;
        // The paw prints dry.
        if (this.pawsAt) {
            const k = 1 - (time - this.pawsAt) / 90000;
            this.paws.setAlpha(Phaser.Math.Clamp(k * 1.6, 0, 0.85));
            if (k <= 0) this.pawsAt = 0;
        }
        this.mKey.setVisible(s.mode === 'play' && s.route === 'inside' && !this.world.carry && !this.P.save.seen.includes('swirl')
            && Math.abs(her.y - L.y) < 4 && Math.abs(her.x - L.machineX) < 60 && !(this.P.has('kid_fed') && !this.P.has('refilled')));
    },

    // --- Near-catch 5 (population §6.7) ---------------------------------------------------------

    // She comes to him swimming (the pool fills the deck from side to side), or along the rim.
    poolWatch() {
        const s = this.scene, L = this.L, cat = this.poolCat, her = s.player;
        if (!cat || cat.gone || cat.hidden || this.P.has('bb5') || s.route !== 'inside') return;
        const pool = L.pools[0];
        const swimming = s.mode === 'swim' && s.pool && s.pool.x1 === pool.x1 && her.x > pool.x1 - 112;
        const onFloor = her.body.enable && (her.body.blocked.down || her.body.touching.down);
        const onDeck = s.mode === 'play' && onFloor && Math.abs(her.y - L.y) < 4 && Math.abs(her.x - cat.sprite.x) < 76;
        if (swimming || onDeck) this.poolBeat(swimming);
    },

    async poolBeat(swimming) {
        const s = this.scene, w = this.world, L = this.L, cat = this.poolCat, her = s.player;
        const pool = s.pools.find(q => q.x1 === L.pools[0].x1), c = cat.sprite;
        const tub = this.who('npc_kid_tub');
        cat.gone = true;
        s.mode = 'scripted';
        s.script = null;
        her.body.setVelocity(0, 0);
        const surface = pool ? pool.y : L.y + 4;
        if (swimming) {
            // To the rim under him, her chin on it.
            s.pose('swim', 0.8);
            her.setFlipX(false);
            await w.tween({ targets: her, x: pool.x1 - SWIM.margin, duration: Math.abs(pool.x1 - SWIM.margin - her.x) * 12 });
            s.pose('swim', 0);
        } else {
            her.setFlipX(c.x < her.x);
            s.pose('stand');
        }
        await w.wait(250);
        s.bubbleUntil = s.time.now + 1500;
        sfx.dash();
        await w.wait(700);
        // The kid comes up out of the hot tub behind him, and lets fly.
        this.tubBusy = true;
        if (tub) {
            tub.dir = -1;
            this.people.place(tub);
            await w.tween({ targets: tub.sprite, y: this.tubBase() - 17, duration: 240, ease: 'Back.easeOut' });
            this.people.play(tub, 'squirt');
        }
        await w.wait(300);
        sfx.splash();
        this.jet(L.tubX - 15, L.y - 44, c.x + 5, L.y - 15, 420);
        await w.wait(200);
        // Hit: he goes straight up, and comes down in the pool.
        s.tweens.killTweensOf(c);
        c.setScale(1).setFlipX(true).play('bumbot-jump');
        sfx.mrrp();
        const inX = Math.max(L.pools[0].x0 + 30, L.pools[0].x1 - 84);
        await w.tween({ targets: c, x: (c.x + inX) / 2 + 6, y: L.y - 56, duration: 300, ease: 'Quad.easeOut' });
        await w.tween({ targets: c, x: inX, y: surface + 6, duration: 260, ease: 'Quad.easeIn' });
        s.splash(inX, surface);
        sfx.splash();
        c.setVisible(false);
        if (!swimming && pool) {
            // And she, reaching after him, goes in too.
            s.pose('fall');
            her.body.enable = false;
            await w.tween({ targets: her, x: pool.x1 - 30, y: surface + SWIM.float, duration: 320, ease: 'Quad.easeIn' });
            s.splash(her.x, surface);
            sfx.splash();
            her.setDepth(s.DEPTH.swimmer);
            s.pose('swim', 0);
            swimming = true;
        } else {
            her.setFlipX(true);
        }
        if (tub) s.tweens.add({ targets: tub.sprite, y: this.tubBase(), duration: 400, delay: 500, ease: 'Sine.easeIn' });
        await w.wait(650);
        // Up the ladder beside her, dripping, onto the lever's housing; he shakes himself dry.
        c.setVisible(true).setFlipX(false).setPosition(L.ladderX, surface + 12).play('bumbot-run');
        await w.tween({ targets: c, y: L.y, duration: 420 });
        if (swimming) her.setFlipX(false);
        c.play('bumbot-jump');
        await w.tween({ targets: c, x: L.leverX - 2, y: L.y - 26, duration: 240, ease: 'Quad.easeOut' });
        if (s.anims.exists('bumbot-shake')) c.play('bumbot-shake');
        else s.tweens.add({ targets: c, scaleX: { from: 0.86, to: 1.12 }, duration: 70, yoyo: true, repeat: 5 });
        for (let i = 0; i < 16; i++) {
            const d = s.add.image(c.x, c.y - 12, 'dot').setTint(i % 3 ? 0x8fd3ff : 0xffffff).setDepth(s.DEPTH.fx);
            w.add([d]);
            const a = Math.PI * (1 + i / 15);
            s.tweens.add({ targets: d, x: d.x + Math.cos(a) * Phaser.Math.Between(16, 40), y: d.y + Math.sin(a) * Phaser.Math.Between(8, 26) + 14,
                alpha: 0, duration: 520, delay: i * 30, onComplete: () => d.destroy() });
        }
        sfx.splash();
        await w.wait(820);
        c.setScale(1);
        // His jump off it throws the lever. Then aft along the pools' far side, and gone.
        c.play('bumbot-jump').setFlipX(false);
        this.lever.setTexture('lever-down');
        sfx.smash();
        s.cameras.main.shake(180, 0.003);
        await w.tween({ targets: c, x: L.leverX + 30, y: L.y, duration: 200, ease: 'Quad.easeIn' });
        c.play('bumbot-run').setDepth(s.DEPTH.decor + 0.05);
        const view = s.cameras.main.worldView;
        await w.tween({ targets: c, x: view.right + 60, duration: ((view.right + 60 - c.x) / 300) * 1000 });
        cat.away = true;
        c.setVisible(false).stop();
        this.tubBusy = false;
        this.pawsAt = s.time.now;
        // Play goes on, in the water if that is where she is; the flag pulls the plug (`drain`).
        if (swimming && pool) {
            s.mode = 'swim';
            s.pool = pool;
            her.body.enable = false;
            her.setDepth(s.DEPTH.swimmer);
        } else {
            s.mode = 'play';
        }
        this.P.setFlag('bb5');
    },

    tubBase() {
        const tub = this.who('npc_kid_tub');
        return tub ? tub.y - (tub.dy ?? 0) : 0;
    },

    // Before the beat: now and then his eyes come up over the hot tub's rim, and go down again.
    kidInTub(time) {
        const tub = this.who('npc_kid_tub'), s = this.scene;
        if (!tub?.on || this.tubBusy || time < (this.tubAt ?? 0)) return;
        if (Math.abs(s.player.x - tub.x) > 700) return;
        this.tubAt = time + 3600;
        s.tweens.add({ targets: tub.sprite, y: this.tubBase() - 9, duration: 320, yoyo: true, hold: 700, ease: 'Sine.easeInOut' });
    },

    // A jet from a water pistol: drops along a line for a moment.
    jet(x0, y0, x1, y1, ms) {
        const s = this.scene, g = this.jetG, t0 = s.time.now;
        const ev = s.time.addEvent({ delay: 16, loop: true, callback: () => {
            const k = (s.time.now - t0) / ms;
            g.clear();
            if (k >= 1) {
                ev.remove();
                return;
            }
            const reach = Math.min(1, k * 3);
            for (let i = 0; i <= 14; i++) {
                const f = (i / 14) * reach;
                const x = x0 + (x1 - x0) * f, y = y0 + (y1 - y0) * f + Math.sin(f * Math.PI) * -5;
                g.fillStyle(i % 3 ? 0x8fd3ff : 0xffffff, 0.95).fillRect(x - 1, y - 1, 3, 2);
            }
            if (k > 0.33) for (let i = 0; i < 4; i++) g.fillStyle(0xffffff, 0.9).fillRect(x1 + Math.cos(i * 1.7 + k * 20) * 6, y1 + Math.sin(i * 2.1 + k * 17) * 5, 2, 2);
        } });
    },

    // --- The kid with the water pistol (population: `npc_kid`) ------------------------------------

    // Up and down the aft pool deck. Until he has had his soft serve he squirts her when she is in
    // front of him within four metres, every two and a half seconds: he brings the pistol up (the
    // tell), then a jet three metres long: "Splashed"; over the jet, or behind him, she is safe. The
    // dash sends him running to the far end, where he keeps his back turned ten seconds. With a cone
    // in her hands he stands and waits for it. Fed, he squirts the gulls instead.
    kidOnDeck(dt, time) {
        const k = this.who('npc_kid'), s = this.scene, w = this.world, L = this.L, P = this.P;
        if (!k?.on || k.state === 'acting') return;
        const her = s.player, dx = her.x - k.x;
        const playing = s.mode === 'play' && s.route === 'inside';
        const level = Math.abs(her.y - k.y) < 40;
        const fed = P.has('kid_fed');
        const cone = w.carry && (w.carry.kind === 'cone' || w.carry.kind === 'stub');
        const face = dir => { k.dir = dir; this.people.place(k); };
        const stand = () => { if (k.pose !== 'stand') { k.pose = 'stand'; this.people.idle(k); } };
        const step = (speed, clipSpeed = 1) => {
            k.x = Phaser.Math.Clamp(k.x + k.dir * speed * dt, L.kidA, L.kidB);
            k.pose = 'walk';
            if (!this.people.anim(k, 'walk', { speed: clipSpeed })) k.sprite.setFrame(k.meta.stand);
            this.people.place(k);
        };
        if (k.mode === 'hide') {
            if (time > k.waitUntil) {
                k.mode = 'patrol';
                k.pose = null;
                k.dir = -1;
            }
            return;
        }
        if (k.mode === 'flee') {
            k.dir = 1;
            step(KID.run, 2.2);
            if (k.x >= L.kidB) {
                k.mode = 'hide';
                k.waitUntil = time + KID.hide;
                k.sprite.anims.stop();
                k.sprite.setFrame(k.meta.back ?? k.meta.stand);
            }
            return;
        }
        if (k.mode === 'tell') {
            if (time < k.waitUntil) return;
            // The jet: along his line of fire, at the height of his hands.
            k.mode = 'patrol';
            k.pauseUntil = time + 420;
            k.nextSquirt = time + KID.every;
            const end = k.x + k.dir * KID.jet;
            this.jet(k.x + k.dir * 13, k.y - 25, end, k.y - 22, 380);
            sfx.splash();
            s.time.delayedCall(110, () => {
                const ahead = (her.x - k.x) * k.dir;
                const hit = s.mode === 'play' && s.route === 'inside' && ahead > 4 && ahead < KID.jet && her.y > k.y - 20 && Math.abs(her.y - k.y) < 40;
                if (!hit || P.has('kid_fed')) return;
                if (w.carry) w.carryBox.spill(k.x);
                else s.scareContact(k.x, 'splashed');
            });
            return;
        }
        // Her shout sends him running.
        if (!fed && playing && level && s.isDashing() && Math.abs(dx) < KID.sees) {
            k.mode = 'flee';
            sfx.rattle();
            return;
        }
        // A cone for him: he waits for it, turned to her.
        if (!fed && cone && playing && level && Math.abs(dx) < 6 * M) {
            face(dx < 0 ? -1 : 1);
            stand();
            return;
        }
        if (time < k.pauseUntil) {
            stand();
            return;
        }
        if (!fed && playing && level && dx * k.dir > 6 && Math.abs(dx) < KID.sees && time > k.nextSquirt) {
            k.mode = 'tell';
            k.waitUntil = time + KID.tell;
            k.pose = 'aim';
            if (!this.people.anim(k, 'squirt')) k.sprite.setFrame(k.meta.stand);
            sfx.rattle();
            return;
        }
        // The security officer on his knees at a lounger gets it too, now and then; and, once the
        // kid is on her side, the gulls overhead.
        const riv = this.who('riv_loungers');
        if (riv?.on && riv.state !== 'acting' && time > (k.nextRival ?? 6000) && (riv.x - k.x) * k.dir > 20 && Math.abs(riv.x - k.x) < 110) {
            k.nextRival = time + 14000;
            k.pauseUntil = time + 700;
            stand();
            this.jet(k.x + k.dir * 13, k.y - 25, riv.x, riv.y - 20, 380);
            sfx.splash();
            this.people.play(riv, 'shake');
            return;
        }
        if (fed && time > (k.nextGull ?? 0)) {
            k.nextGull = time + 5200;
            k.pauseUntil = time + 800;
            stand();
            this.jet(k.x + k.dir * 10, k.y - 30, k.x + k.dir * 46, k.y - 118, 420);
            sfx.splash();
            return;
        }
        step(KID.walk);
        if (k.x <= L.kidA || k.x >= L.kidB) {
            face(k.x <= L.kidA ? 1 : -1);
            k.pauseUntil = time + 500;
        }
    },

    // E at him with what she has made: a stub he hands back to the deck, with a face; a proper
    // swirl he eats, and from then on he is on her side.
    feedKid() {
        const k = this.near('npc_kid', 44), w = this.world, s = this.scene;
        if (!k || this.P.has('kid_fed') || k.mode === 'flee') return false;
        const kind = w.carry?.kind;
        if (kind !== 'cone' && kind !== 'stub') {
            if (w.carry) return false;
            w.nudge(k);
            return true;
        }
        const state = k.state;
        k.state = 'acting';
        w.cut(async () => {
            const her = s.player;
            her.setFlipX(k.x < her.x);
            k.dir = her.x < k.x ? -1 : 1;
            this.people.place(k);
            this.people.idle(k);
            k.state = 'acting';
            await w.wait(200);
            w.carryBox.give();
            const img = s.add.image(her.x + (her.flipX ? -12 : 12), her.y - 31, kind === 'cone' ? 'load-cone' : 'load-stub').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.05);
            w.add([img]);
            sfx.pickup();
            await w.tween({ targets: img, x: k.x + k.dir * 9, y: k.y - 22, duration: 340, ease: 'Sine.easeInOut' });
            if (kind === 'stub') {
                // He looks at it, and at her.
                await w.wait(500);
                for (let i = 0; i < 2; i++) {
                    k.dir = -k.dir;
                    this.people.place(k);
                    await w.wait(170);
                    k.dir = -k.dir;
                    this.people.place(k);
                    await w.wait(170);
                }
                await w.tween({ targets: img, y: k.y - 1, x: img.x + k.dir * 8, angle: 100, duration: 300, ease: 'Quad.easeIn' });
                s.tweens.add({ targets: img, alpha: 0, delay: 900, duration: 500, onComplete: () => img.destroy() });
                w.foodGulls?.gull_pool?.pounce(img.x);
                k.state = state === 'acting' ? 'idle' : state;
                k.pose = null;
                k.nextSquirt = s.time.now + 3000;
                return;
            }
            img.setPosition(k.x + k.dir * 8, k.y - 27).setDepth(k.sprite.depth + 0.01);
            const eating = this.people.play(k, 'eat', { times: 3 });
            for (let i = 1; i <= 3; i++) s.time.delayedCall(i * 800, () => img.active && img.setScale(1, 1 - i * 0.28));
            await eating;
            img.destroy();
            k.state = 'acting';
            for (let i = 0; i < 3; i++) {
                const heart = s.add.text(k.x + (i - 1) * 8, k.y - 50, '♥', { fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#e83b3b', resolution: 4 })
                    .setOrigin(0.5).setDepth(s.DEPTH.fx);
                w.add([heart]);
                s.tweens.add({ targets: heart, y: heart.y - 18 - i * 4, alpha: 0, duration: 1000, delay: i * 130, onComplete: () => heart.destroy() });
            }
            sfx.checkpoint();
            await w.wait(700);
            k.state = 'idle';
            k.pose = null;
            // The machine has given its last: that is the next thing.
            this.P.setFlag('kid_fed');
        });
        return true;
    },

    // --- The soft serve machine (§6.1.2) ----------------------------------------------------------

    // E at it. With the canister: she pours the mix in. Empty: it sputters. Else hold E: the swirl.
    machine() {
        const s = this.scene, w = this.world, P = this.P, L = this.L, her = s.player;
        if (w.carry?.kind === 'canister') {
            w.cut(async () => {
                her.setFlipX(L.machineX < her.x);
                if (s.anims.exists('her-pour')) her.anims.play('her-pour');
                await w.wait(350);
                w.carryBox.give();
                const can = s.add.image(L.machineX - 2, L.y - 58, 'load-canister').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.05).setAngle(150);
                w.add([can]);
                sfx.rattle();
                for (let i = 0; i < 12; i++) {
                    const d = s.add.rectangle(can.x + 2, can.y - 2, 2, 3, 0xfdf2e3).setDepth(s.DEPTH.fx);
                    w.add([d]);
                    s.tweens.add({ targets: d, y: L.y - 44, duration: 260, delay: i * 90, onComplete: () => d.destroy() });
                }
                await w.wait(1300);
                can.destroy();
                s.pose('stand');
                sfx.checkpoint();
                w.sparkle(L.machineX, L.y - 34, 0x1ebc73);
                P.setFlag('refilled');
            });
            return true;
        }
        if (w.carry) return false;
        if (P.has('kid_fed') && !P.has('refilled')) {
            // Empty: a cough, a puff. Her husband knows what it wants.
            sfx.rattle();
            const puff = s.add.image(L.machineX + 3, L.y - 24, 'dot').setTint(0xc7dcd0).setScale(2).setDepth(s.DEPTH.fx);
            w.add([puff]);
            s.tweens.add({ targets: puff, y: puff.y - 14, alpha: 0, scale: 4, duration: 600, onComplete: () => puff.destroy() });
            s.tweens.add({ targets: this.mLight, alpha: 0.2, duration: 90, yoyo: true, repeat: 3 });
            const h = this.who('npc_husband');
            if (h) w.nudge(h);
            return true;
        }
        // The swirl: hers to time.
        s.mode = 'scripted';
        s.script = null;
        her.body.setVelocity(0, 0);
        her.setFlipX(L.machineX + 3 < her.x);
        if (s.anims.exists('her-push')) {
            her.anims.play('her-push');
            her.anims.pause();
        } else s.pose('stand');
        this.swirl = { k: 0 };
        sfx.rattle();
        return true;
    },

    swirling(dt, time, input) {
        const sw = this.swirl, s = this.scene, L = this.L;
        if (!sw) return;
        if (s.mode !== 'scripted') {
            this.swirl = null;
            this.mCone.setVisible(false);
            this.mMeter.setVisible(false);
            return;
        }
        if (input.activate && sw.k < SWIRL.max) sw.k += (dt * 1000) / SWIRL.ms;
        const k = sw.k;
        // The cone under the spout, its swirl rising; and the meter: grey, green, red.
        const cx = L.machineX + 3, cy = L.y - 21, h = Math.round(k * 13);
        const c = this.mCone.clear().setVisible(true);
        const lean = k > SWIRL.over ? Math.round((k - SWIRL.over) * 14) : 0;
        c.fillStyle(0x2e222f, 1).fillTriangle(cx - 4, cy, cx + 5, cy, cx + 0.5, cy + 9);
        c.fillStyle(0xe6904e, 1).fillTriangle(cx - 3, cy + 1, cx + 4, cy + 1, cx + 0.5, cy + 8);
        for (let i = 0; i < h; i++) {
            const wd = Math.max(1, 6 - Math.floor(i / 2.6)), off = Math.round((lean * i) / 13);
            c.fillStyle(0x2e222f, 1).fillRect(cx - wd / 2 - 0.5 + off, cy - 1 - i, wd + 2, 1);
            c.fillStyle(i % 3 === 2 ? 0xf9d9c8 : 0xffffff, 1).fillRect(cx - wd / 2 + 0.5 + off, cy - 1 - i, wd, 1);
        }
        const mx = L.machineX - 31, my = L.y - 86, H = 40;
        const m = this.mMeter.clear().setVisible(true);
        m.fillStyle(0x2e222f, 1).fillRect(mx - 1, my - 1, 9, H + 2);
        m.fillStyle(0x9babb2, 1).fillRect(mx, my, 7, H);
        const band = (a, b, col) => m.fillStyle(col, 1).fillRect(mx, my + H - Math.round(Math.min(1, b) * H), 7, Math.round((Math.min(1, b) - a) * H));
        band(SWIRL.perfect, SWIRL.over, 0x1ebc73);
        band(SWIRL.over, 1, 0xe83b3b);
        const at = my + H - Math.round(Math.min(1, k) * H);
        m.fillStyle(0xffffff, 1).fillRect(mx - 3, at - 1, 13, 2);
        m.fillStyle(0x2e222f, 1).fillRect(mx - 3, at + 1, 13, 1);
        if (input.activate && k < SWIRL.max) return;
        // Let go (or it has gone over by itself).
        this.swirl = null;
        this.mMeter.setVisible(false);
        this.mCone.setVisible(false);
        s.mode = 'play';
        s.pose('stand');
        if (k < SWIRL.none) return;
        if (!this.P.save.seen.includes('swirl')) {
            this.P.save.seen.push('swirl');
            writeSave(this.P.save);
        }
        const kind = k < SWIRL.perfect ? 'stub' : k <= SWIRL.over ? 'cone' : 'toppled';
        this.lastSwirl = kind;
        if (kind === 'toppled') return this.toppled(cx, cy);
        if (kind === 'cone') sfx.checkpoint();
        // With every errand done, it is hers: she eats it where she stands (population: `sec_cone`).
        if (this.P.has('table')) return this.forHerself(kind);
        this.world.carryBox.take(kind);
    },

    // Too much: it goes over, onto the deck, and a gull is on it at once.
    toppled(x, y) {
        const s = this.scene, w = this.world, L = this.L;
        const img = s.add.image(x, y + 8, 'load-cone').setOrigin(0.5, 1).setDepth(s.DEPTH.props + 0.05);
        w.add([img]);
        w.say('Ой!', 700);
        s.tweens.add({ targets: img, x: x - 16, y: L.y, angle: -110, duration: 380, ease: 'Quad.easeIn', onComplete: () => {
            sfx.smash();
            w.foodGulls?.gull_go?.pounce(img.x - 4);
            s.tweens.add({ targets: img, alpha: 0, delay: 1700, duration: 700, onComplete: () => img.destroy() });
        } });
    },

    forHerself(kind) {
        const s = this.scene, w = this.world, her = s.player;
        w.cut(async () => {
            const img = s.add.image(her.x + (her.flipX ? -9 : 9), her.y - 33, kind === 'cone' ? 'load-cone' : 'load-stub').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.05);
            w.add([img]);
            // (Her clip holds her hand to her mouth: the cone is drawn in it.)
            if (s.anims.exists('her-lick')) {
                her.anims.play('her-lick');
                img.setPosition(her.x + (her.flipX ? -8 : 8), her.y - 37);
            } else s.pose('front');
            for (let i = 0; i < 3; i++) {
                await w.wait(650);
                img.setScale(1, 1 - (i + 1) * 0.28);
            }
            img.destroy();
            await w.wait(200);
            s.pose('stand');
            if (!this.P.save.seen.includes('sec_cone')) {
                this.P.save.seen.push('sec_cone');
                writeSave(this.P.save);
            }
        });
    },

    // --- Her husband, at the first table (population: `npc_husband`, `scn_table`) -----------------

    husband() {
        const h = this.near('npc_husband', 50), w = this.world, s = this.scene, P = this.P;
        if (!h) return false;
        const kind = w.carry?.kind;
        if (P.has('table')) {
            if (w.carry) return false;
            this.people.play(h, 'wave');
            return true;
        }
        if (kind === 'cone' && P.has('refilled')) {
            this.tableScene(h);
            return true;
        }
        if (w.carry && kind !== 'stub' && kind !== 'cone') return false;
        // Not yet, or not that one: he shows again what is wanted (once the machine has run empty).
        if (kind === 'stub' && P.has('refilled')) this.people.play(h, 'laugh');
        w.nudge(h);
        return true;
    },

    // A proper cone of her own, and she sits down with him: they eat, looking at the wake; the
    // picture of the two of them stands on the table after; and he gives her the book he borrowed.
    tableScene(h) {
        const s = this.scene, w = this.world, L = this.L, her = s.player;
        w.cut(async () => {
            const seat = L.tableX + 23;
            s.pose('run', 0.6);
            her.setFlipX(seat < her.x);
            her.body.enable = false;
            await w.tween({ targets: her, x: seat, duration: Math.abs(seat - her.x) * 11 + 60 });
            her.setFlipX(true);
            const sat = s.anims.exists('her-sit-eat');
            if (sat) {
                w.carryBox.give();
                her.anims.play('her-sit-eat');
                her.anims.chain('her-eat-sat');
            } else if (s.anims.exists('her-read')) {
                her.anims.play('her-read');
                her.anims.pause();
            }
            this.people.anim(h, 'eat');
            h.state = 'acting';
            for (let i = 0; i < 4; i++) {
                await w.wait(950);
                const heart = s.add.text(L.tableX + (i % 2 ? 5 : -5), L.y - 52, '♥', { fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#e83b3b', resolution: 4 })
                    .setOrigin(0.5).setDepth(s.DEPTH.fx);
                w.add([heart]);
                s.tweens.add({ targets: heart, y: heart.y - 22, alpha: 0, duration: 1100, onComplete: () => heart.destroy() });
            }
            await w.wait(500);
            if (w.carry) w.carryBox.give();
            // The picture, on the table between them.
            this.P.setFlag('table');
            w.sparkle(L.tableX, L.y - 40);
            sfx.checkpoint();
            await w.wait(700);
            this.people.idle(h);
            await w.handOver(h, '@book-6', () => w.giveBook(6));
            s.pose('stand');
            her.body.enable = true;
            her.body.reset(her.x, L.y);
        });
    },

    // --- Secrets ------------------------------------------------------------------------------

    // The giant chess set: she moves a pawn.
    chess() {
        const s = this.scene, w = this.world, her = s.player;
        if (w.carry) return false;
        w.cut(async () => {
            const p = this.pawn, from = p.x, to = from + (this.pawnOut ? -16 : 16);
            const stand = p.x + (this.pawnOut ? 14 : -14);
            her.setFlipX(stand < her.x);
            s.pose('run', 0.6);
            await w.tween({ targets: her, x: stand, duration: Math.abs(stand - her.x) * 9 + 40 });
            her.setFlipX(to < her.x);
            if (s.anims.exists('her-push')) her.anims.play('her-push');
            await w.tween({ targets: [p, her], x: `+=${to - from}`, duration: 520, ease: 'Sine.easeInOut' });
            this.pawnOut = !this.pawnOut;
            sfx.land();
            s.pose('stand');
            her.body.reset(her.x, her.y);
            await w.wait(250);
            if (!this.P.save.seen.includes('sec_chess')) {
                this.P.save.seen.push('sec_chess');
                writeSave(this.P.save);
            }
        });
        return true;
    },

    // The hot tub: she gets in, up to her shoulders, steam rising; any key and she is out.
    hotTub() {
        const s = this.scene, w = this.world, L = this.L, her = s.player;
        if (w.carry || this.who('npc_kid_tub')?.on) return false;
        w.cut(async () => {
            const back = { x: her.x, depth: her.depth };
            her.body.enable = false;
            s.pose('rise');
            await w.tween({ targets: her, x: L.tubX, y: L.y - 30, duration: 240, ease: 'Quad.easeOut' });
            her.setDepth(s.DEPTH.decor + 0.095);
            s.pose('front');
            await w.tween({ targets: her, y: L.y + 2, duration: 200, ease: 'Quad.easeIn' });
            s.splash(L.tubX, L.y - 38);
            sfx.splash();
            const t0 = s.time.now;
            const steam = s.time.addEvent({ delay: 170, loop: true, callback: () => {
                const d = s.add.image(L.tubX + Phaser.Math.Between(-18, 18), L.y - 40, 'dot').setTint(0xffffff).setAlpha(0.7).setScale(2).setDepth(s.DEPTH.props + 0.3);
                w.add([d]);
                s.tweens.add({ targets: d, y: d.y - Phaser.Math.Between(20, 42), x: d.x + Phaser.Math.Between(-6, 6), alpha: 0, scale: 3.4, duration: 1500, onComplete: () => d.destroy() });
                her.y = L.y + 2 + Math.round(Math.sin(s.time.now / 500));
            } });
            // (Any key, after a moment: `soaking` is read each frame, in updateLido.)
            this.soaking = { from: t0 + 1800, out: false };
            while (!this.soaking.out && s.time.now - t0 < 12000) await w.wait(60);
            this.soaking = null;
            steam.remove();
            her.setDepth(back.depth);
            s.pose('rise');
            await w.tween({ targets: her, y: L.y - 34, duration: 220, ease: 'Quad.easeOut' });
            s.pose('fall');
            await w.tween({ targets: her, x: back.x, y: L.y, duration: 220, ease: 'Quad.easeIn' });
            her.body.enable = true;
            her.body.reset(her.x, L.y);
            s.pose('stand');
            if (!this.P.save.seen.includes('sec_hottub')) {
                this.P.save.seen.push('sec_hottub');
                writeSave(this.P.save);
            }
        });
        return true;
    },
};
