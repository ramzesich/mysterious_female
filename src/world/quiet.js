// Near-catch 2 (GAME_DESIGN.md §6.1, region 2; remade 2026-11-24, docs/near-catch-2-remake-log.md), mixed into the
// Story: the Library's aft end on deck 6. Bumbot asleep on top of the return trolley (the user: "He sleeps on top of
// the book return basket"), so that he, the "QUIET PLEASE" rope and the aft door are in one picture. At the sight of
// him she is taken; the librarian's finger goes to her lips; she creeps up on tiptoe and reaches for him at his
// height (the user's choice); he wakes as she reaches, leaps off the trolley as her hands arrive, lands, and bolts
// aft straight through the rope: the stand goes over into the door (its clip, tools/build_quiet.py), which swings
// open away from the knock and stays so, the stand lying in its doorway; the librarian starts and looks at the
// door; she straightens, turns to us, shrugs, and is free.
//
// One clock (`T`, ms of the game's time since the scene began) and everything a function of it, on the ship
// scene's scripted update. Where things stand: `QUIET` in src/config.js, from his spot (`BEATS` in
// tools/population.py) and the rope's own place; the fall's frames: assets/ship/quiet/quiet.json.

import { BUMBOT, QUIET } from '../config.js';
import { sfx } from '../sfx.js';
import { rumble } from '../rumble.js';

const CARD = { face: 0x323353, rim: 0xf9c22b };         // the rope's card seen edge on (src/signs.js, `rope`)

export const quiet = {
    setupQuiet() {
        const s = this.scene, w = this.world;
        const cat = s.cats.find(c => c.flag === 'bb2');
        if (!cat || !s.textures.exists('quiet-stand-fall')) return;
        const L = s.cache.json.get('quiet-layout').fall;
        const rope = this.P.blockDrawings.find(d => d.id === 'flag:bb2');
        const door = s.bulkheads.find(b => b.id === 'part-door-6-194');
        if (!rope || !door) return;
        cat.custom = true;              // (its own scene: not the ship scene's `nearCatch`)
        const [stand, card] = rope.items, F = cat.floor;
        // The fall: a frame stands with its column `x` at the stand's left, its row `y` on the floor's line.
        const fall = s.add.sprite(stand.x - stand.width / 2 - L.x, F - L.y, 'quiet-stand-fall', 0).setOrigin(0).setDepth(stand.depth - 0.01).setVisible(false);      // (he goes through in front of it)
        // The card as it falls (a copy of the rope's own, which the block hides with its flag), and lying: edge on.
        const drop = s.add.image(card.x, card.y, card.texture.key).setOrigin(0.5).setDepth(card.depth).setVisible(false);
        const flat = s.add.graphics().setDepth(stand.depth - 0.005).setVisible(false);
        const cw = card.width, fx = Math.round(card.x + QUIET.card[0] - cw / 2);
        flat.fillStyle(CARD.face, 1).fillRect(fx, F - 2, cw, 2);
        flat.fillStyle(CARD.rim, 1).fillRect(fx, F - 2, 1, 2).fillRect(fx + cw - 1, F - 2, 1, 2).fillRect(fx, F - 2, cw, 1);
        w.add([fall, drop, flat]);
        this.quiet = { cat, L, F, top: cat.sprite.y, rope, stand, card, door, fall, drop, flat };
        if (this.P.has('bb2')) this.quietAfter();
    },

    // As it is once he has been: the stand lying in the doorway, its card flat on the floor, the door open for good.
    quietAfter() {
        const q = this.quiet;
        if (!q) return;
        const stood = !this.P.openAll;          // (`?cards=all`: no rope was ever there)
        q.fall.setFrame(q.L.frames - 1).setVisible(stood);
        q.flat.setVisible(stood);
        q.drop.setVisible(false);
        q.cat.gone = q.cat.away = true;
        q.cat.sprite.setVisible(false);
        this.leaveAjar();
    },

    // She comes within `sight` of him on his floor: the scene. In a jump across that line she comes straight down
    // where she crossed it, and the scene begins as she lands (as at the pass: he cannot be jumped over).
    updateQuiet() {
        const q = this.quiet, s = this.scene;
        if (!q || q.cat.gone || q.cat.hidden || s.mode !== 'play' || s.route !== 'inside') return;
        const p = s.player, dx = q.cat.sprite.x - p.x;
        if (Math.abs(dx) > QUIET.sight || p.y > q.F + 1 || p.y < q.F - QUIET.airUp) return;
        if (p.body.blocked.down || p.body.touching.down) {
            if (Math.abs(p.y - q.F) <= 1) this.quietBeat();
            return;
        }
        q.cat.gone = true;
        s.mode = 'scripted';
        p.body.setVelocityX(0);
        p.body.setAccelerationX(0);
        s.script = () => {
            if (p.body.blocked.down || p.body.touching.down || p.y >= q.F) {
                s.script = null;
                this.quietBeat();
            } else {
                s.pose(p.body.velocity.y < 0 ? 'rise' : 'fall');
            }
        };
    },

    quietBeat() {
        const q = this.quiet, s = this.scene, w = this.world, p = s.player, k = q.cat.sprite, { F, top, L } = q;
        const k0 = k.x, pace = p.anims.timeScale, lib = this.who('npc_librarian');
        q.cat.gone = true;
        s.mode = 'scripted';
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.y = F;
        if (s.crawling) s.crawling = false;
        // (Forward of him, as she comes: he bolts aft. Aft of him she can only be with every lock open.)
        const side = p.x <= k0 ? 1 : -1;
        p.setFlipX(side < 0);
        // (With something in her hands she cannot reach: she stops where she is, and he wakes all the same.)
        const hands = !w.carry && !s.holding && s.anims.exists('her-creep-tiptoe') && s.anims.exists('her-creep-reach');
        const stood = q.stand.visible;          // (the rope is there: not with `?cards=all`)

        // Her creep: on tiptoe from where she is to arm's length, at the pace her planted toes slide by.
        const x0 = p.x, stop = hands ? k0 - side * Math.min(QUIET.gap, Math.abs(k0 - x0)) : x0;
        const tipMs = Math.abs(stop - x0) / (QUIET.tipFps * QUIET.tipPx) * 1000;
        // He wakes as she reaches, and leaps as her hands arrive.
        const wakeAt = tipMs + QUIET.wakeAt;
        const leapAt = wakeAt + (s.anims.get('bumbot-wake').frames.length - QUIET.wakeFrom) / QUIET.wakeFps * 1000;
        const landAt = leapAt + QUIET.leapMs, landX = k0 + QUIET.land;
        // Into the stand: his nose at its forward post; he ploughs through it, and the door is open before him.
        const hitX = stood ? q.stand.x - q.stand.width / 2 - QUIET.nose : q.door.x - 24 - QUIET.nose;
        const hitAt = landAt + Math.max(0, hitX - landX) / BUMBOT.runSpeed * 1000;
        const doorAt = hitAt + (stood ? L.door * QUIET.fallMs : 0);
        const doorX = hitX + QUIET.plough * (doorAt - hitAt) / 1000;
        const backAt = landAt + QUIET.backAfter;
        const frontAt = backAt + (hands ? QUIET.backFrames / QUIET.backFps * 1000 : QUIET.watchMs);

        let T = 0, herDone = false, steps = 0;
        const did = {};
        const once = (key, at, fn) => { if (!did[key] && T >= at) { did[key] = true; fn(); } };
        const end = () => {
            s.script = null;
            p.body.enable = true;
            p.body.reset(p.x, p.y);
            p.anims.timeScale = pace;
            s.pose('stand');
            p.setFlipX(false);              // (the way he went)
            s.cameras.main.followOffset.x = 0;
            s.mode = 'play';
            this.P.setFlag('bb2');          // (the door is open for good: `quietAfter`)
        };

        if (hands) {
            p.anims.timeScale = 1;
            if (tipMs > 0) p.anims.play('her-creep-tiptoe'); else s.pose('stand');
        } else {
            s.pose('stand');
        }
        s.script = (dt) => {
            T += dt * 1000;
            // (The picture goes a little ahead of her as she creeps: the door comes well inside it. It was at the
            // screen's edge, she being 220 px from that edge as she walks aft.)
            if (side > 0) s.cameras.main.followOffset.x = -QUIET.ahead * Math.min(1, T / QUIET.aheadMs);

            // --- The librarian: a finger to her lips (she gives it to anyone running past her desk; if she has not
            // yet, now), a start at the crash, a look at the door.
            once('shush', QUIET.shushAt, () => {
                if (!lib?.on || lib.state === 'acting') return;
                this.shushAt = s.time.now + 6000;
                lib.dir = p.x < lib.x ? -1 : 1;
                this.people.place(lib);
                sfx.at(lib.x, lib.y).shush();
                this.people.play(lib, 'shush', { hold: 300 });
            });
            once('start', doorAt, () => {
                if (!lib?.on) return;
                this.people.play(lib, 'flinch').then(() => {
                    lib.dir = 1;
                    this.people.place(lib);
                    s.time.delayedCall(QUIET.lookMs, () => { lib.dir = -1; this.people.place(lib); });
                });
            });

            // --- She ---
            if (hands && T < tipMs) {
                p.x = x0 + (stop - x0) * T / tipMs;
                // (Her toes on the carpet: a step each half round of the clip.)
                if (T >= steps * 4 / QUIET.tipFps * 1000) { steps++; sfx.tiptoe(); }
            }
            once('reach', tipMs, () => {
                if (!hands) return;
                p.x = stop;
                p.anims.play('her-creep-reach');
            });
            once('back', backAt, () => { if (hands) p.anims.play('her-creep-back'); });
            once('front', frontAt, () => {
                // (Turned to us, she shrugs, as after every near-catch; her `shrug` at its own pace, then a moment.
                // With her hands full she only looks after him.)
                const after = () => s.time.delayedCall(QUIET.afterMs, () => { herDone = true; });
                if (!hands || !s.anims.exists('her-shrug')) return after();
                p.setFlipX(false);
                p.anims.timeScale = 1;
                p.anims.play('her-shrug');
                p.once('animationcomplete-her-shrug', () => after());
            });

            // --- He ---
            once('wake', wakeAt, () => k.play({ key: 'bumbot-wake', startFrame: QUIET.wakeFrom, frameRate: QUIET.wakeFps }));
            // (From its second frame: the first is him reared straight up, which is a jump on the spot's.)
            once('leap', leapAt, () => {
                k.setFlipX(false).play({ key: 'bumbot-leap', startFrame: 1, frameRate: (s.anims.get('bumbot-leap').frames.length - 1) / QUIET.leapMs * 1000 });
                rumble('bolt');
                sfx.at(k.x, k.y).mrrp();
            });
            if (T >= leapAt && T < landAt) {
                // (Off the trolley over the desk's corner and down to the floor: the leap's frames each on its lowest
                // pixel, the arc the scene's.)
                const u = (T - leapAt) / QUIET.leapMs;
                k.setPosition(k0 + (landX - k0) * u, top + (F - top) * u - 4 * QUIET.arc * u * (1 - u));
            }
            // (On the floor he is on our side of the stand and its card: he goes through in front of them.)
            once('land', landAt, () => { k.setPosition(landX, F).setDepth(q.card.depth + 0.04).play('bumbot-run'); sfx.at(k.x, k.y).scramble(); });
            if (T >= landAt && !q.cat.away) {
                k.x = T < hitAt ? landX + (T - landAt) / 1000 * BUMBOT.runSpeed
                    : T < doorAt ? hitX + (T - hitAt) / 1000 * QUIET.plough
                    : doorX + (T - doorAt) / 1000 * BUMBOT.runSpeed;
                if (k.x > Math.max(s.cameras.main.worldView.right, q.door.x) + 40) {
                    q.cat.away = true;
                    k.setVisible(false).stop();
                }
            }

            // --- The stand, its card, the door ---
            once('hit', hitAt, () => {
                if (!stood) return;
                q.stand.setVisible(false);
                q.card.setVisible(false);
                q.fall.setFrame(0).setVisible(true);
                q.drop.setPosition(q.card.x, q.card.y).setScale(1).setVisible(true);
                sfx.at(q.stand.x, F).rattle();
            });
            if (stood && T >= hitAt) {
                const f = Math.min(L.frames - 1, Math.floor((T - hitAt) / QUIET.fallMs));
                if (q.fall.frame.name !== f) q.fall.setFrame(f);
                // (Its card goes down with the rope and turns face up: seen from the side, it thins to its edge.)
                const u = Math.min(1, (T - hitAt) / QUIET.cardMs), h = q.card.height;
                const thin = 1 - (1 - 2 / h) * u, low = q.card.y + (F - 1 - q.card.y) * u * u;
                q.drop.setPosition(q.card.x + QUIET.card[0] * u, low).setScale(1, thin);
                once('flat', hitAt + QUIET.cardMs, () => { q.drop.setVisible(false); q.flat.setVisible(true); });
                once('down', hitAt + (L.frames - 1) * QUIET.fallMs, () => sfx.at(q.stand.x, F).thump());
            }
            once('door', doorAt, () => {
                q.door.ajar = true;
                s.setBulkheadOpen(q.door, true);
                sfx.at(q.door.x, F).doorHeavy();
            });

            if (herDone && q.cat.away) end();
        };
    },
};
