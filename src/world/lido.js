// Region 6's part of the story (GAME_DESIGN.md §6.1.3 "Lido", docs/population.md deck 11 and scene
// 7), mixed into the Story: Bumbot fishing at the pool and what the kid's water pistol does about it,
// the pool draining; the kid on the aft pool deck (a hazard, then an ally); the soft serve machine
// and its swirl; the cone for the kid, the canister, the table with her husband; the chess set, the
// hot tub; the wet paw prints aft. Places come from maps/world.json (`lido`).

import { PLAYER, SWIM } from '../config.js';
import { sfx } from '../sfx.js';
import { t } from '../lang.js';
import { writeSave } from '../save.js';
import { soakRide, runFrame } from './movers.js';

const M = 48;
// The swirl: how long a full one takes (ms), and where it is a stub, perfect, or too much.
// (`aside`: px from the spout she stands at while it fills, to one side, so the cone shows: the user, 2026-11-23.)
const SWIRL = { ms: 2400, none: 0.14, perfect: 0.58, over: 0.84, max: 1.08, aside: 18 };
// The kiss at his table: her place from his middle (px), how many hearts, ms between them.
const KISS = { dx: 6, hearts: 7, every: 450 };
const KID = { walk: 46, run: 150, sees: 4 * M, jet: 3 * M, every: 2500, tell: 480, hide: 10000, fruit: 15000 };
// Near-catch 5's scene (docs/pool-remake-log.md). The hot tub: the rows of its picture from `rim` down are its near
// wall, drawn again in front of whoever is in it; the kid stands in it `in` px over the deck, `duck` px lower right
// down out of sight, `peek` px lower with his cap showing over the near rim; his pistol's muzzle from his feet.
const TUB = { rim: 15, in: 12, duck: 34, peek: 24, muzzle: [-21, -27] };
// Bumbot in it: how far into the pool from her he lands (px), how deep he swims (his feet under the surface, so that
// his head and back show over it), how deep he goes as he plunges in (his feet, all of him under), his paddle (px/s), where his paws are from the lever's grip, how he is thrown.
const CAT = { in: 44, swim: 12, under: 27, paddle: 52, paw: 2, over: 38, lands: 42, short: 5 };

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
        // The drain's lever on its stand, by the rim (tools/build_pool.py: armed, its swing, thrown).
        const lay = this.leverLay = s.cache.json.get('pool-layout').lever;
        const strip = s.textures.get('pool-lever-strip');
        for (let i = 0; i < lay.frames; i++) if (!strip.has(i)) strip.add(i, 0, i * lay.w, 0, lay.w, lay.h);
        this.lever = s.add.image(L.leverX + lay.dx, L.y + lay.dy, 'pool-lever-strip', P.has('drain') ? lay.frames - 1 : 0).setOrigin(0)
            .setDepth(D.props - 0.03);
        // The kid is in the hot tub, not behind it: in front of its far rim and its water, behind its near wall (the
        // tub's own picture drawn again from its near rim down).
        const tubPic = w.mapPiece('hot-tub', L.tubX, L.y), kidIn = this.who('npc_kid_tub');
        if (tubPic && kidIn) {
            this.tubFront = s.add.image(tubPic.x, tubPic.y, 'shipart', tubPic.frame.name).setOrigin(tubPic.originX, tubPic.originY)
                .setDepth(tubPic.depth + 0.004).setCrop(0, TUB.rim, tubPic.width, tubPic.height - TUB.rim);
            w.add([this.tubFront]);
            kidIn.sprite.setDepth(tubPic.depth + 0.002).setY(this.tubBase());
        }
        // The kid's jets of water; the wet paw prints aft; the chess pawn she moves.
        this.jetG = s.add.graphics().setDepth(D.player + 0.2);
        this.paws = s.add.graphics().setDepth(D.props - 0.04).setAlpha(0);
        this.paws.fillStyle(0x4d65b4, 0.8);
        for (let x = L.pawsA, n = 0; x < L.pawsB; x += 14, n++) {
            // (Each print heads aft, the way he ran: its pad, its three toes to the right of it; on the deck's planks, 4 px
            // lower than at first. The user, 2026-11-24: they pointed up, and stood over the deck's line.)
            const y = L.y - (n % 2 ? 2 : 4) + 3;
            this.paws.fillRect(x - 1, y, 2, 3).fillRect(x + 1, y - 1, 1, 1).fillRect(x + 2, y + 1, 1, 1).fillRect(x + 1, y + 3, 1, 1);
        }
        this.pawn = s.add.image(L.chessX + 14, L.y - 2, 'chess-pawn').setOrigin(0.5, 1).setDepth(D.decor + 0.3);
        if (this.P.save.seen.includes('sec_chess')) this.pawn.x += 16;
        // The machine: its light (green: it has mix), the cone under its spout, the swirl's meter.
        this.mLight = s.add.rectangle(L.machineX + 9, L.y - 39, 3, 2, 0x1ebc73).setDepth(D.decor + 0.3);
        this.mCone = s.add.graphics().setDepth(D.props + 0.04).setVisible(false);
        this.mMeter = s.add.graphics().setDepth(D.fx + 0.4).setVisible(false);
        this.catG = s.add.graphics().setDepth(D.poolWater + 0.03);
        // (His jump's frames carry a rise of their own: how far his lowest paw is over each frame's foot, so that a leap
        // can be placed by his paws.)
        this.jumpGap = {};
        const jump = s.anims.get('bumbot-jump');
        if (jump) {
            const src = s.textures.get('bumbot').getSourceImage();
            const cv = document.createElement('canvas'), cx = cv.getContext('2d', { willReadFrequently: true });
            for (const { frame: f } of jump.frames) {
                cv.width = f.cutWidth;
                cv.height = f.cutHeight;
                cx.clearRect(0, 0, cv.width, cv.height);
                cx.drawImage(src, f.cutX, f.cutY, f.cutWidth, f.cutHeight, 0, 0, f.cutWidth, f.cutHeight);
                const d = cx.getImageData(0, 0, cv.width, cv.height).data;
                let last = cv.height - 1;
                scan: for (; last > 0; last--) for (let x = 0; x < cv.width; x++) if (d[(last * cv.width + x) * 4 + 3] > 0) break scan;
                this.jumpGap[f.name] = cv.height - 1 - last;
            }
        }
        w.add([this.lever, this.jetG, this.catG, this.paws, this.pawn, this.mLight, this.mCone, this.mMeter]);
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
        make('chess-pawn', 12, 20, g => {
            g.fillStyle(0x625565, 1).fillRect(0, 18, 12, 2);
            g.fillStyle(0x2e222f, 1).fillRect(1, 16, 10, 2).fillRect(3, 8, 6, 8).fillCircle(6, 5, 4);
        });
    },

    // What shows by what has happened: the lever, the machine's light, his bubble's picture.
    refreshLido() {
        const P = this.P, L = this.L;
        if (!L) return;
        if (this.lever && !this.tubBusy) this.lever.setFrame(P.has('drain') ? this.leverLay.frames - 1 : 0);

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
        // (The tub's near wall drawn again is only for the kid in it: it does not pulse with the tub.)
        this.tubFront?.setVisible(!!this.who('npc_kid_tub')?.on);
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

    // The scene (remade 2026-11-24, docs/pool-remake-log.md). From the deck beside him she dives at him, he hops over
    // her dive, and she is in the pool; from here on it is the same as when she comes to him swimming: under him at
    // the rim, nose to nose. The kid stands up in the hot tub behind him and squirts him in the back: out over her head
    // he goes, into the water behind her. He paddles back past her to the rim, his head and back over the surface, hops
    // out, shakes himself dry; then away aft, by the nearest high thing: up onto the drain lever's grip, which goes over
    // under him toward the hot tub and throws him across it; the kid ducks. The lever thrown, the pool drains.
    async poolBeat(swimming) {
        const s = this.scene, w = this.world, L = this.L, cat = this.poolCat, her = s.player, D = s.DEPTH;
        const pool = s.pools.find(q => q.x1 === L.pools[0].x1), c = cat.sprite;
        const tub = this.who('npc_kid_tub'), lay = this.leverLay;
        cat.gone = true;
        s.mode = 'scripted';
        s.script = null;
        her.body.setVelocity(0, 0);
        // (Her place in the water under him: a little short of the rim, so that her hand, stretched up, is a few px short
        // of him: at the rim itself it lay on his chest.)
        const surface = pool ? pool.y : L.y + 4, rim = L.pools[0].x1, home = c.x, spot = rim - SWIM.margin - CAT.short;
        // (Him in a leap along an arc: his paws from where they are to a place, `lift` px over the straight line at its
        // middle; his jump's clip from frame `from`, paced to last the leap, its own rise taken out frame by frame.)
        const gap = () => this.jumpGap[c.frame.name] ?? 0;
        const paws = { x: c.x, y: c.y };
        const hop = (x1, y1, ms, lift, from = 1) => {
            const n = s.anims.get('bumbot-jump').frames.length;
            c.play({ key: 'bumbot-jump', startFrame: from });
            c.anims.timeScale = (n - from) / 12 * 1000 / ms;
            const x0 = paws.x, y0 = paws.y, k = { v: 0 };
            return w.tween({ targets: k, v: 1, duration: ms, onUpdate: () => {
                paws.x = x0 + (x1 - x0) * k.v;
                paws.y = y0 + (y1 - y0) * k.v - lift * 4 * k.v * (1 - k.v);
                c.setPosition(paws.x, paws.y + gap());
            } }).then(() => { c.anims.timeScale = 1; });
        };
        // (Crouched as he lands, his paws at a place: the jump's last frame, held.)
        const crouch = (x, y) => {
            const fr = s.anims.get('bumbot-jump').frames;
            c.play('bumbot-jump');
            c.anims.pause(fr.at(-1));
            paws.x = x;
            paws.y = y;
            c.setPosition(x, y + gap());
        };
        const sit = () => { c.play('bumbot-sit'); c.anims.setCurrentFrame(c.anims.currentAnim.frames.at(-1)); c.anims.pause(); };
        // (Under him at the rim she looks up out of the water and stretches an arm up after him, and holds it there,
        // straining, still lying in the water as she swims: her own clip, generated from her swim's first frame; the
        // user, 2026-11-24.)
        const reach = () => {
            if (!s.anims.exists('her-swim-reach')) return s.pose('swim', 0);
            her.anims.timeScale = 1;
            her.anims.play('her-swim-reach');
            her.anims.chain('her-swim-strain');
        };
        s.tweens.killTweensOf(c);
        c.setScale(1);
        if (swimming) {
            // To the rim under him, her chin on it.
            s.pose('swim', 0.8);
            her.setFlipX(false);
            await w.tween({ targets: her, x: spot, duration: Math.abs(spot - her.x) * 12 });
            c.setFlipX(true);
            sit();
            reach();
            await w.wait(450);
            // (Her cry is over before the kid stands up: its popup is where he and Bumbot are.)
            s.bubbleUntil = s.time.now + 900;
            sfx.cry();
            await w.wait(1000);
        } else {
            her.setFlipX(c.x < her.x);
            s.pose('stand');
            await w.wait(200);
            s.bubbleUntil = s.time.now + 1200;
            sfx.cry();
            await w.wait(380);
            if (pool) {
                her.body.enable = false;
                // He hops straight up out of her hands and comes down where he sat.
                sfx.at(c.x, c.y).meow();
                const up = hop(home, L.y, 560, 46);
                if (her.x >= c.x) {
                    // From aft of him: a flat dive under his hop, off the rim and in.
                    if (s.anims.exists('her-tripfall')) her.anims.play('her-tripfall');
                    else s.pose('fall');
                    await w.tween({ targets: her, x: rim + 6, duration: Math.abs(her.x - rim - 6) * 3.4 + 80 });
                } else {
                    // On the rim's edge already: a grab at the air, a step back, and off it.
                    if (s.anims.exists('her-reach')) her.anims.play('her-reach');
                    await w.wait(260);
                    s.pose('fall');
                }
                await w.tween({ targets: her, x: rim - 34, y: surface + SWIM.float, duration: 280, ease: 'Quad.easeIn' });
                s.splash(her.x, surface);
                sfx.splash();
                her.setDepth(D.swimmer);
                s.pose('swim', 0);
                await up;
                c.setFlipX(true);
                sit();
                await w.wait(350);
                // She comes up under him.
                her.setFlipX(false);
                s.pose('swim', 0.8);
                await w.tween({ targets: her, x: spot, duration: Math.abs(spot - her.x) * 12 });
                reach();
                swimming = true;
                await w.wait(700);
            }
        }
        // The kid stands up in the hot tub behind him, and lets fly.
        this.tubBusy = true;
        const tubUp = this.tubBase() - TUB.duck;
        if (tub) {
            // (A peek of his under way would take him down again.)
            s.tweens.killTweensOf(tub.sprite);
            tub.dir = -1;
            this.people.place(tub);
            sfx.at(tub.x, tub.y).giggle();
            await w.tween({ targets: tub.sprite, y: tubUp, duration: 240, ease: 'Back.easeOut' });
            this.people.play(tub, 'squirt', { stay: true });
        }
        await w.wait(300);
        const mx = L.tubX + TUB.muzzle[0], my = tubUp + TUB.muzzle[1];
        sfx.at(mx, my).jet();
        this.jet(mx, my, c.x + 7, L.y - 13, 420);
        await w.wait(200);
        // Hit in the back: out over the water he goes, over her head, and in behind her; her arm comes down.
        if (swimming) s.pose('swim', 0);
        c.setFlipX(true);
        sfx.at(c.x, c.y).meow();
        const inX = Math.max(L.pools[0].x0 + 30, spot - CAT.in);
        await hop(inX, surface + 8, 520, 30, 2);
        s.splash(inX, surface);
        s.splash(inX + 5, surface - 2);
        sfx.at(inX, surface).splash();
        if (swimming) her.setFlipX(true);
        // Under he goes, in sight through the water as she is (the user, 2026-11-24: he was gone from the picture
        // until he came up), turns, and comes up paddling for the rim, past her, his head and back over the water.
        c.setDepth(D.swimmer - 0.001).play('bumbot-run');
        c.anims.timeScale = 0.75;
        c.setPosition(inX, surface + 8);
        await w.tween({ targets: c, y: Math.min(surface + CAT.under, L.tankY + 4), duration: 240, ease: 'Quad.easeOut' });
        c.setFlipX(false);
        await w.tween({ targets: c, y: surface + CAT.swim, duration: 300, ease: 'Sine.easeInOut' });
        sfx.at(inX, surface).splashSmall();
        const wake = this.catG;
        await w.tween({ targets: c, x: rim - 9, duration: (rim - 9 - inX) / CAT.paddle * 1000, onUpdate: () => {
            if (swimming && c.x > her.x - 4) her.setFlipX(false);
            // (The water he pushes: a few light strokes at his chest and behind him.)
            const t = s.time.now;
            wake.clear();
            for (let i = 0; i < 4; i++) {
                const bx = c.x - 12 + i * 8 + Math.round(Math.sin(t / 90 + i * 1.7) * 2);
                wake.fillStyle(i % 2 ? 0xffffff : 0xc7e7ff, 0.9).fillRect(Math.round(bx), surface - (i % 2), 3, 1);
            }
        } });
        wake.clear();
        // Out over the rim, streaming, and he shakes himself dry.
        c.anims.timeScale = 1;
        c.setDepth(D.props);
        sfx.at(rim, surface).splashSmall();
        paws.x = c.x;
        paws.y = surface + 2;
        await hop(home, L.y, 300, 12, 2);
        if (s.anims.exists('bumbot-shake')) c.play('bumbot-shake');
        for (let i = 0; i < 16; i++) {
            const d = s.add.image(c.x, c.y - 12, 'dot').setTint(i % 3 ? 0x8fd3ff : 0xffffff).setDepth(D.fx);
            w.add([d]);
            const a = Math.PI * (1 + i / 15);
            s.tweens.add({ targets: d, x: d.x + Math.cos(a) * Phaser.Math.Between(16, 40), y: d.y + Math.sin(a) * Phaser.Math.Between(8, 26) + 14,
                alpha: 0, duration: 520, delay: 180 + i * 30, onComplete: () => d.destroy() });
        }
        sfx.at(c.x, c.y).splashSmall();
        await w.wait(820);
        // Away aft, by the nearest high thing: up onto the lever's grip.
        c.setFlipX(false);
        const grip = i => [L.leverX + lay.grips[i][0], L.y + lay.grips[i][1] + CAT.paw];
        paws.x = c.x;
        paws.y = L.y;
        await hop(...grip(0), 260, 10);
        crouch(...grip(0));
        await w.wait(90);
        // It goes over under him, toward the hot tub: he rides it down.
        sfx.at(L.leverX, L.y).creak();
        const thrown = lay.frames - 3;
        for (let i = 1; i <= thrown; i++) {
            this.lever.setFrame(i);
            crouch(...grip(i));
            await w.wait(60);
        }
        sfx.at(L.leverX, L.y).lever();
        sfx.at(L.leverX, L.y).clang();
        s.cameras.main.shake(180, 0.003);
        // And is thrown off it across the tub; the kid ducks.
        if (tub) s.tweens.add({ targets: tub.sprite, y: this.tubBase(), duration: 170, ease: 'Quad.easeIn' });
        sfx.at(c.x, c.y).mrrp();
        const landX = L.tubX + CAT.lands;
        const flung = hop(landX, L.y, 460, CAT.over, 2);
        // (The lever's bounce on its stop.)
        await w.wait(70);
        this.lever.setFrame(lay.frames - 2);
        await w.wait(70);
        this.lever.setFrame(lay.frames - 1);
        await flung;
        // Aft along the second pool's far side, and gone.
        c.play('bumbot-run').setDepth(D.decor + 0.05);
        sfx.at(c.x, c.y).scramble();
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
            her.setDepth(D.swimmer);
        } else {
            s.mode = 'play';
        }
        this.P.setFlag('bb5');
    },

    // Where the kid's feet are while he is right down in the tub, out of sight behind its near wall.
    tubBase() {
        return this.L.y - TUB.in + TUB.duck;
    },

    // Before the beat: now and then his eyes come up over the hot tub's rim, and go down again.
    kidInTub(time) {
        const tub = this.who('npc_kid_tub'), s = this.scene;
        if (!tub?.on || this.tubBusy || time < (this.tubAt ?? 0)) return;
        if (Math.abs(s.player.x - tub.x) > 700) return;
        this.tubAt = time + 3600;
        s.tweens.add({ targets: tub.sprite, y: this.tubBase() - (TUB.duck - TUB.peek), duration: 320, yoyo: true, hold: 700, ease: 'Sine.easeInOut' });
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
            // A stream 2 px thick, a point every 2 px of it: light blue over mid blue, white glints, so
            // that it reads against the pale sky and sea in the windows (the user chose it from six,
            // 2026-11-19; it was light blue and white dots).
            const reach = Math.min(1, k * 3), n = Math.max(4, Math.ceil(Math.abs(x1 - x0) * reach / 2));
            for (let i = 0; i <= n; i++) {
                const f = (i / n) * reach;
                const x = x0 + (x1 - x0) * f, y = y0 + (y1 - y0) * f + Math.sin(f * Math.PI) * -5;
                g.fillStyle(0x8fd3ff, 1).fillRect(x - 1, y, 2, 1);
                g.fillStyle(0x4d9be6, 1).fillRect(x - 1, y + 1, 2, 1);
                if (i % 6 < 2) g.fillStyle(0xffffff, 1).fillRect(x - 1, y, 2, 1);
            }
            if (k > 0.33) for (let i = 0; i < 5; i++) {
                g.fillStyle(i % 2 ? 0xffffff : 0x4d9be6, 1).fillRect(x1 + Math.cos(i * 1.7 + k * 20) * 6, y1 + Math.sin(i * 2.1 + k * 17) * 5, 2, 2);
            }
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
            sfx.at(k.x, k.y).jet();
            s.time.delayedCall(110, () => {
                const ahead = (her.x - k.x) * k.dir;
                const hit = s.mode === 'play' && s.route === 'inside' && ahead > 4 && ahead < KID.jet && her.y > k.y - 20 && Math.abs(her.y - k.y) < 40;
                if (!hit || P.has('kid_fed')) return;
                sfx.splashSmall();
                if (w.carry) return w.carryBox.spill(k.x, false, 'jet');
                // With none on her, the wet gag (16's, the user, 2026-11-19), and she squelches off
                // away from him. (From her run its clips start on an odd frame of her stride: the
                // hit waits for one, a frame at most.)
                const soak = (tries) => {
                    if (s.mode !== 'play') return;
                    if (runFrame(her) % 2 === 0 && tries > 0) return s.time.delayedCall(16, () => soak(tries - 1));
                    s.scareContact(k.x, 'jet', { ride: soakRide(s, L.y, her.x >= k.x ? 1 : -1) });
                };
                soak(10);
            });
            return;
        }
        // Her shout sends him running.
        if (!fed && playing && level && s.isLunging() && Math.abs(dx) < KID.sees) {
            k.mode = 'flee';
            sfx.at(k.x, k.y).oh();
            return;
        }
        // A cone for him: he waits for it, turned to her; not on the spot of the security officer on his knees at a
        // lounger, but a step clear of him first (the user, 2026-11-19: the two of them in one place, the eating hidden).
        if (!fed && cone && playing && level && Math.abs(dx) < 6 * M) {
            // (He kneels facing `front`, his net and head 30 px before his middle, his legs 42 behind; the kid 10 px clear.)
            const riv = this.who('riv_loungers'), front = riv?.sprite.flipX ? -1 : 1;
            const rel = riv?.on ? (k.x - riv.x) * front : Infinity;
            if (rel > -46 && rel < 40) {
                let away = rel >= -6 ? front : -front;
                const to = riv.x + away * (away === front ? 40 : 46);
                if (to < L.kidA || to > L.kidB) away = -away;
                face(away);
                step(KID.walk);
                return;
            }
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
            sfx.at(k.x, k.y).giggle();
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
            sfx.at(k.x, k.y).jet();
            s.time.delayedCall(200, () => sfx.at(riv.x, riv.y).grumble());
            this.people.play(riv, 'shake');
            return;
        }
        if (fed && time > (k.nextGull ?? 0)) {
            k.nextGull = time + 5200;
            k.pauseUntil = time + 800;
            stand();
            this.jet(k.x + k.dir * 10, k.y - 30, k.x + k.dir * 46, k.y - 118, 420);
            sfx.at(k.x, k.y).jet();
            return;
        }
        step(KID.walk);
        if (k.x <= L.kidA || k.x >= L.kidB) {
            face(k.x <= L.kidA ? 1 : -1);
            k.pauseUntil = time + 500;
        }
    },

    // Her cry draws his fire: he turns and squirts at her at once (in a lunge he runs and hides
    // instead: kidOnDeck). Once he is on her side, nothing.
    kidHeard(cry) {
        const k = this.who('npc_kid'), s = this.scene, her = s.player;
        if (!k?.on || k.state === 'acting' || this.P.has('kid_fed') || s.isLunging()) return;
        if (k.mode === 'flee' || k.mode === 'hide' || k.mode === 'tell' || !this.world.hears(k.x, k.y)) return;
        k.dir = her.x < k.x ? -1 : 1;
        this.people.place(k);
        k.mode = 'tell';
        k.waitUntil = s.time.now + 160;
        k.pose = 'aim';
        if (!this.people.anim(k, 'squirt')) k.sprite.setFrame(k.meta.stand);
    },

    // A tangerine thrown to him: he catches it, turns his back and eats it out of sight (his hands
    // hold his water pistol in every pose he has), and keeps his back turned 15 s
    // (docs/plan-three-uses.md §2). Spent.
    kidOffered(t) {
        const k = this.who('npc_kid'), s = this.scene;
        if (!t.thrown || !k?.on || k.state === 'acting' || k.mode === 'flee' || !s.loose.near(t, k.x, k.y, 14, 50)) return false;
        // (Caught at his front, facing where it came from; then his back to her.)
        k.dir = t.img.body.velocity.x > 0 ? -1 : 1;
        k.mode = 'patrol';
        this.people.place(k);
        const img = s.loose.claim(t).setPosition(k.x + k.dir * 8, k.y - 24).setDepth(k.sprite.depth + 0.01);
        sfx.at(k.x, k.y).take();
        k.state = 'acting';
        s.time.delayedCall(450, () => {
            img.destroy();
            k.state = 'idle';
            k.pose = null;
            k.mode = 'hide';
            k.waitUntil = s.time.now + KID.fruit;
            k.sprite.anims.stop();
            k.sprite.setFrame(k.meta.back ?? k.meta.stand);
            for (let i = 0; i < 3; i++) s.time.delayedCall(700 + i * 1300, () => sfx.at(k.x, k.y).munch());
        });
        return true;
    },

    // E at him with what she has made: a stub he hands back to the deck, with a face; a proper
    // swirl he eats, and from then on he is on her side. She hands it over from a step away (if she
    // is closer, she steps back first, so that she does not stand over him), and is free as soon as
    // it is in his hand: he eats, or turns the stub down, by himself (the user, 2026-11-19: she
    // hid him while he ate, and could not move).
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
            const her = s.player, GAP = 24;
            const side = Math.sign(her.x - k.x) || -(k.dir || 1);
            const spot = k.x + side * GAP;
            if (Math.abs(her.x - k.x) < GAP - 2) {
                // (A step back to arm's length: away from him, then round to face him.)
                her.setFlipX(side < 0);
                s.pose('run', 0.6);
                await w.tween({ targets: her, x: spot, duration: Math.abs(spot - her.x) / 60 * 1000 });
                s.pose('stand');
            }
            her.setFlipX(k.x < her.x);
            k.dir = her.x < k.x ? -1 : 1;
            this.people.place(k);
            this.people.idle(k);
            k.state = 'acting';
            await w.wait(200);
            w.carryBox.give();
            const img = s.add.image(her.x + (her.flipX ? -12 : 12), her.y - 31, kind === 'cone' ? 'load-cone' : 'load-stub').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.05);
            w.add([img]);
            sfx.give();
            // (A proper cone into his fist as his eating clip's first frame holds it: 3 px before his middle, its tip
            // 19 px up; a stub to his hand.)
            const to = kind === 'cone' ? { x: k.x + k.dir * 3, y: k.y - 19 } : { x: k.x + k.dir * 9, y: k.y - 22 };
            await w.tween({ targets: img, ...to, duration: 340, ease: 'Sine.easeInOut' });
            img.setDepth(k.sprite.depth + 0.01);
            // (In his hand: she is free; what he does with it goes on by itself.)
            this.kidHas(k, img, kind, state);
        });
        return true;
    },

    // The kid with what she gave him: a stub turned down, or a proper swirl eaten.
    async kidHas(k, img, kind, state) {
        const w = this.world, s = this.scene;
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
            sfx.at(img.x, k.y).plop();
            s.tweens.add({ targets: img, alpha: 0, delay: 900, duration: 500, onComplete: () => img.destroy() });
            w.foodGulls?.gull_pool?.pounce(img.x);
            k.state = state === 'acting' ? 'idle' : state;
            k.pose = null;
            k.nextSquirt = s.time.now + 3000;
            return;
        }
        // (His eating clip has the cone in his fist, his pistol tucked in his waistband: three licks, the swirl
        // smaller each time, then a bite of the cone. `assets/source/people/kid-eat-cone/`.)
        img.destroy();
        // (Fed from the moment he has it: his bubble asking for one goes, and the machine has given its last.)
        this.P.setFlag('kid_fed');
        const eating = this.people.play(k, 'eat', { times: 1 });
        for (const f of [3, 6, 12]) s.time.delayedCall(f / 7 * 1000, () => sfx.at(k.x, k.y).munch());
        await eating;
        k.state = 'acting';
        for (let i = 0; i < 3; i++) {
            const heart = s.add.text(k.x + (i - 1) * 8, k.y - 50, '♥', { fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#e83b3b', resolution: 4 })
                .setOrigin(0.5).setDepth(s.DEPTH.fx);
            w.add([heart]);
            s.tweens.add({ targets: heart, y: heart.y - 18 - i * 4, alpha: 0, duration: 1000, delay: i * 130, onComplete: () => heart.destroy() });
        }
        sfx.at(k.x, k.y).heart();
        await w.wait(700);
        k.state = 'idle';
        k.pose = null;
        // The machine has given its last: that is the next thing.
        sfx.done();
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
                sfx.pour();
                s.time.delayedCall(650, () => sfx.pour());
                for (let i = 0; i < 12; i++) {
                    const d = s.add.rectangle(can.x + 2, can.y - 2, 2, 3, 0xfdf2e3).setDepth(s.DEPTH.fx);
                    w.add([d]);
                    s.tweens.add({ targets: d, y: L.y - 44, duration: 260, delay: i * 90, onComplete: () => d.destroy() });
                }
                await w.wait(1300);
                can.destroy();
                s.pose('stand');
                sfx.done();
                w.sparkle(L.machineX, L.y - 34, 0x1ebc73);
                P.setFlag('refilled');
            });
            return true;
        }
        if (w.carry) return false;
        if (P.has('kid_fed') && !P.has('refilled')) {
            // Empty: a cough, a puff. Her husband knows what it wants.
            sfx.at(L.machineX, L.y).cough();
            const puff = s.add.image(L.machineX + 3, L.y - 24, 'dot').setTint(0xc7dcd0).setScale(2).setDepth(s.DEPTH.fx);
            w.add([puff]);
            s.tweens.add({ targets: puff, y: puff.y - 14, alpha: 0, scale: 4, duration: 600, onComplete: () => puff.destroy() });
            s.tweens.add({ targets: this.mLight, alpha: 0.2, duration: 90, yoyo: true, repeat: 3 });
            const h = this.who('npc_husband');
            if (h) w.nudge(h);
            return true;
        }
        // The swirl: hers to time. She steps to the machine's side (the side she came from), clear of its spout, and faces
        // the cone filling under it (the user, 2026-11-23: in front of it she hid the cone).
        s.mode = 'scripted';
        s.script = null;
        her.body.setVelocity(0, 0);
        const spout = L.machineX + 3, side = her.x < spout ? -1 : 1, stand = spout + side * SWIRL.aside;
        her.setFlipX(stand > spout);
        const face = () => {
            her.setFlipX(stand > spout);
            if (s.anims.exists('her-push')) {
                her.anims.play('her-push');
                her.anims.pause();
            } else s.pose('stand');
        };
        if (Math.abs(her.x - stand) > 1) {
            s.pose('run', 0.6);
            her.setFlipX(stand < her.x);
            s.tweens.add({ targets: her, x: stand, duration: Math.abs(stand - her.x) * 9 + 40, onComplete: face });
        } else face();
        this.swirl = { k: 0 };
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
        // (Its motor, for as long as it runs: a stretch of it, begun again as the last one ends.)
        if (input.activate && sw.k < SWIRL.max && time >= (sw.soundAt ?? 0)) {
            sw.soundAt = time + 280;
            sfx.at(L.machineX, L.y).whirr(0.4);
        }
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
        if (kind === 'cone') sfx.done();
        // With every errand done and him away from his table (from the catch on, after the ending too), it is hers: she
        // eats it where she stands (population: `sec_cone`). While he is at his table every cone can be his (the user,
        // 2026-11-23).
        if (this.P.has('table') && this.P.has('catch')) return this.forHerself(kind);
        this.world.carryBox.take(kind);
    },

    // Too much: it goes over, onto the deck, and a gull is on it at once.
    toppled(x, y) {
        const s = this.scene, w = this.world, L = this.L;
        const img = s.add.image(x, y + 8, 'load-cone').setOrigin(0.5, 1).setDepth(s.DEPTH.props + 0.05);
        w.add([img]);
        w.say(t('say.oops'), 700);
        s.tweens.add({ targets: img, x: x - 16, y: L.y, angle: -110, duration: 380, ease: 'Quad.easeIn', onComplete: () => {
            sfx.at(img.x, L.y).plop();
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
                sfx.secret();
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
        // A perfect cone: she sits down with him, every time while he is at his table (the user, 2026-11-23: "Feeding the
        // husband should work every time"); his book only the first time.
        if (kind === 'cone' && P.has('refilled')) {
            this.tableScene(h);
            return true;
        }
        if (P.has('table')) {
            if (!w.carry) {
                this.kiss(h);
                return true;
            }
            if (kind !== 'stub') return false;
            this.people.play(h, 'laugh');
            sfx.at(h.x, h.y).laugh();
            return true;
        }
        if (w.carry && kind !== 'stub' && kind !== 'cone') return false;
        // Not fed yet, her hands empty: he waves (the user, 2026-11-23), and his bubble shows what he wants.
        if (!w.carry) this.people.play(h, 'wave');
        // Not yet, or not that one: he shows again what is wanted (once the machine has run empty).
        if (kind === 'stub' && P.has('refilled')) {
            this.people.play(h, 'laugh');
            sfx.at(h.x, h.y).laugh();
        }
        w.nudge(h);
        return true;
    },

    // Once he has been fed, E with her hands empty (the user, 2026-11-23): he stands up from his chair facing us (his front
    // view; the chair's near arm and his far leg away meanwhile), she steps up a few px to his right with her back to us,
    // in front of him, and they kiss: hearts rise, more than at the meal; he sits back down, and she is hers again,
    // facing the way she was going.
    kiss(h) {
        const s = this.scene, w = this.world, L = this.L, her = s.player, P = this.people;
        const facing = her.flipX;
        w.cut(async () => {
            h.state = 'acting';
            h.sprite.anims.stop();
            h.sprite.setFrame(h.meta.front ?? h.meta.stand).setFlipX(false);
            h.underPic?.setVisible(false);
            h.coverPics.forEach(c => c.setVisible(false));
            const spot = Math.round(h.x) + KISS.dx;
            s.pose('run', 0.6);
            her.setFlipX(spot < her.x);
            her.body.enable = false;
            await w.tween({ targets: her, x: spot, duration: Math.abs(spot - her.x) * 11 + 60 });
            s.pose('back');
            // The embrace: her arms up round his neck, his round her, his near hand on her back (drawn over her).
            const hug = h.meta.anims.embrace && s.anims.exists('her-embrace');
            let hand = null;
            if (hug) {
                her.anims.play('her-embrace');
                await P.play(h, 'embrace', { stay: true });
                hand = s.add.image(h.sprite.x, h.sprite.y, 'hug-hand-2').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.02);
                w.add([hand]);
            }
            for (let i = 0; i < KISS.hearts; i++) {
                await w.wait(KISS.every);
                const heart = s.add.text(spot - 3 + (i % 3) * 3, L.y - 66, '♥', { fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#e83b3b', resolution: 4 })
                    .setOrigin(0.5).setDepth(s.DEPTH.fx);
                w.add([heart]);
                sfx.heart();
                s.tweens.add({ targets: heart, y: heart.y - 26, x: heart.x + (i % 2 ? 4 : -4), alpha: 0, duration: 1200, onComplete: () => heart.destroy() });
            }
            await w.wait(700);
            if (hug) {
                hand.destroy();
                her.anims.playReverse('her-embrace');
                h.sprite.anims.playReverse(`people-${h.who}-embrace`);
                await w.wait(420);
            }
            h.underPic?.setVisible(true);
            h.coverPics.forEach(c => c.setVisible(true));
            P.idle(h);
            her.setFlipX(facing);
            s.pose('stand');
            her.body.enable = true;
            her.body.reset(her.x, L.y);
        });
    },

    // A proper cone of her own, and she sits down with him: they eat, looking at the wake; the
    // picture of the two of them stands on the table after; and he gives her the book he borrowed.
    tableScene(h) {
        const s = this.scene, w = this.world, L = this.L, her = s.player;
        w.cut(async () => {
            // (She stands 12 px past the table's middle, facing him, and sits back into the patio chair across from
            // him: her clip lands her back on its backrest, 7 px further back than first placed, the user, 2026-11-23;
            // the chair's near arm is drawn again over her lap, as over his. Her cone is the one she carried, in her
            // fist in every frame: `assets/source/her/sit-cone/`.)
            const seat = L.tableX + 12;
            s.pose('run', 0.6);
            her.setFlipX(seat < her.x);
            her.body.enable = false;
            await w.tween({ targets: her, x: seat, duration: Math.abs(seat - her.x) * 11 + 60 });
            her.setFlipX(true);
            const sat = s.anims.exists('her-sit-cone');
            let arm = null;
            if (sat) {
                w.carryBox.give();
                arm = s.add.image(2 * L.tableX - (h.cover?.[0]?.x ?? L.tableX - 17), L.y, 'shipart', 'patio-chair-arm-w20').setOrigin(0.5, 1).setFlipX(true)
                    .setDepth(s.DEPTH.player + 0.01);
                w.add([arm]);
                her.anims.play('her-sit-cone');
                her.anims.chain('her-lick-cone');
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
                sfx.heart();
                s.tweens.add({ targets: heart, y: heart.y - 22, alpha: 0, duration: 1100, onComplete: () => heart.destroy() });
            }
            await w.wait(500);
            if (w.carry) w.carryBox.give();
            // (Both cones eaten.)
            if (sat) her.anims.play('her-sat');
            // Done: their photo is up on La Cucina's wall from now on (`slot_cucina`, deck 5); here only his book follows.
            this.P.setFlag('table');
            sfx.done();
            await w.wait(700);
            this.people.idle(h);
            // (His book the first time only.)
            if (!this.P.save.books?.['1']) await w.handOver(h, '@book-1', () => w.giveBook(1));
            if (sat) {
                her.anims.play('her-sit-up');
                await new Promise(r => her.once('animationcomplete', r));
                arm.destroy();
            }
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
            sfx.scrape();
            await w.tween({ targets: [p, her], x: `+=${to - from}`, duration: 520, ease: 'Sine.easeInOut' });
            this.pawnOut = !this.pawnOut;
            sfx.knock();
            s.pose('stand');
            her.body.reset(her.x, her.y);
            await w.wait(250);
            if (!this.P.save.seen.includes('sec_chess')) {
                sfx.secret();
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
            sfx.splashSmall();
            const t0 = s.time.now;
            const steam = s.time.addEvent({ delay: 170, loop: true, callback: () => {
                const d = s.add.image(L.tubX + Phaser.Math.Between(-18, 18), L.y - 40, 'dot').setTint(0xffffff).setAlpha(0.7).setScale(2).setDepth(s.DEPTH.props + 0.3);
                w.add([d]);
                s.tweens.add({ targets: d, y: d.y - Phaser.Math.Between(20, 42), x: d.x + Phaser.Math.Between(-6, 6), alpha: 0, scale: 3.4, duration: 1500, onComplete: () => d.destroy() });
                her.y = L.y + 2 + Math.round(Math.sin(s.time.now / 500));
            } });
            // (Any key, after a moment: `soaking` is read each frame, in updateLido.)
            this.soaking = { from: t0 + 1800, out: false };
            for (let at = 0; !this.soaking.out && s.time.now - t0 < 12000; await w.wait(60)) {
                if (s.time.now < at) continue;
                at = s.time.now + 1100;
                sfx.bubbles(1.3);
            }
            this.soaking = null;
            steam.remove();
            her.setDepth(back.depth);
            s.pose('rise');
            sfx.splashSmall();
            await w.tween({ targets: her, y: L.y - 34, duration: 220, ease: 'Quad.easeOut' });
            s.pose('fall');
            await w.tween({ targets: her, x: back.x, y: L.y, duration: 220, ease: 'Quad.easeIn' });
            her.body.enable = true;
            her.body.reset(her.x, L.y);
            s.pose('stand');
            if (!this.P.save.seen.includes('sec_hottub')) {
                sfx.secret();
                this.P.save.seen.push('sec_hottub');
                writeSave(this.P.save);
            }
        });
        return true;
    },
};
