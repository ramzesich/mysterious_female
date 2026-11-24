// Near-catch 4, the linen room (deck 9; remade 2026-11-24 on the user's own structure, docs/near-catch-4-remake-log.md):
// "The laundry cart has stack of pillows on top of it. We cannot jump past it, or on top of it. We only have to push
// it. When we push it, Bumbot jumps (like now), the pillows scatter, and we are able to jump on top of the cart and
// enter the vent." Mixed into the Story.
//
// The cart is the empty one, a wall to the ceiling while the pillows are in it (`wall` on the pushable). Asleep on the
// bottle shelf, he is off the moment the cart bumps his shelf (`PILLOWS.gap`): his leap at the cover on the shaft's
// mouth, which begins its fall as his paws reach it (he was in the mouth with the cover still on), and in over it. His
// spring beside the stack knocks the top two pillows aft, over her, to the aft rack; the lower two ride the cart on and
// slide off behind it (tools/build_linen_pillows.py: one generated clip in two layers, those in the cart moved with the
// game's cart, those in the air kept where the room has them). She is not held: the push only goes on by itself until
// the last pillows are off the cart, so that they land where they were made to. The one hint of crawling is given
// when she first stands on the cart after it.

import { sfx } from '../sfx.js';
import { t } from '../lang.js';
import { rumble } from '../rumble.js';
import { PILLOWS } from '../config.js';

// His body's columns in his asleep frame (of 64): the cart's front is measured from their aft end.
const BB4_SPAN = [19, 49];
const CART_HALF = 22.5;         // the cart's picture, 45 px wide, about its middle

export const linen = {
    setupLinen() {
        const s = this.scene, w = this.world, L = s.cache.json.get('linen-pillows');
        const cat = s.cats.find(c => c.flag === 'bb4'), cart = w.pushables.find(p => p.id === 'cart_linen');
        if (cat) { cat.custom = true; this.bb4 = cat; }
        if (!cat || !cart || !L || !s.textures.exists('linen-pillows-ride')) return;
        const room = w.rooms.linen, floor = room.floor, depth = cart.items[0].depth;
        // (The sheets' frames: each a cell of its picture, in a row.)
        for (const [key, part, n] of [['linen-pillows-ride', L.ride, L.release], ['linen-pillows-free', L.free, L.frames]]) {
            const tex = s.textures.get(key);
            if (!tex.has(0)) for (let i = 0; i < n; i++) tex.add(i, 0, i * part.cell[0], 0, part.cell[0], part.cell[1]);
        }
        // Where the clip stands in the room: its x from the cart picture's left edge as he goes, which is `gap` from
        // his body's aft end.
        const x0 = Math.round(cat.sprite.x) - 32 + BB4_SPAN[1] + PILLOWS.gap - 1;
        // The pillows in the cart: its picture's own middle is the cart's, so that the two are rounded as one.
        const ride = s.add.sprite(cart.x, floor + L.ride.y, 'linen-pillows-ride', 0)
            .setOrigin((CART_HALF - L.ride.x) / L.ride.cell[0], 0).setDepth(depth + 0.001);
        const free = s.add.sprite(x0 + L.free.x, floor + L.free.y, 'linen-pillows-free', 0).setOrigin(0).setDepth(depth + 0.001).setAlpha(0);
        // As they lie afterwards: behind the cart and her.
        const lie = (key, at) => s.add.image(x0 + at.x, floor + at.y, key).setOrigin(0).setDepth(depth - 0.005);
        const near = lie('linen-pillows-near', L.near), far = lie('linen-pillows-far', L.far);
        w.add([ride, free, near, far]);
        w.things.push({ id: 'linen_pillows_air', x: x0, y: floor, route: 'linen', items: [free] });
        w.things.push({ id: 'linen_pillows_near', x: x0 + L.near.x + L.near.w / 2, y: floor, route: 'linen', items: [near], after: 'flag:bb4' });
        w.things.push({ id: 'linen_pillows_far', x: x0 + L.far.x + L.far.w / 2, y: floor, route: 'linen', items: [far], after: 'flag:bb4' });
        const q = this.linen = { L, cat, cart, ride, free, near, far, x0, floor, frame: 0, T: null };
        if (this.P.has('bb4')) {
            ride.setVisible(false).setAlpha(0);
            // (A game loaded with the beat done and the cart not yet at the mouth: it stands where the last pillows left
            // it, forward of the two on the floor, not back at its start on top of them.)
            const left = Math.round(x0 + CART_HALF + L.cartLeft[L.release]);
            if (!this.P.has(cart.flag) && cart.x > left) cart.moveTo(left);
        } else {
            // (With the cart: shown with it, pulsing with it, moved with it after the physics.)
            cart.items.push(ride);
            const move = cart.moveTo;
            cart.moveTo = (to) => { move(to); ride.x = to; };
        }
    },

    // The cart's front past his body's aft end by `-gap`: he is off.
    updateLinen(time) {
        const q = this.linen, s = this.scene;
        if (!q) return;
        this.linenHint();
        if (q.over) return;
        if (q.T === null) {
            if (q.cat.gone || q.cat.hidden || s.route !== 'linen' || this.P.has('bb4')) return;
            const sp = q.cat.sprite, aft = sp.x - 32 + (sp.flipX ? 64 - BB4_SPAN[0] : BB4_SPAN[1]);
            if (q.cart.x - CART_HALF > aft + PILLOWS.gap) return;
            this.linenGoes(time);
        }
        this.linenScene(time);
    },

    // The one hint of crawling (the rule: every new mechanic explained once): over her the first time she stands on
    // the cart once he is gone, wherever it stands (the user, 2026-11-24: "The tooltip has to show (after the Bumbot's
    // escape) only when we jump on top of the cart"; it showed as he went).
    linenHint() {
        const q = this.linen, s = this.scene, p = s.player, P = this.P;
        if (q.hinted || !P.has('bb4') || s.route !== 'linen' || s.mode !== 'play') return;
        if (P.has('hint_crawl')) { q.hinted = true; return; }
        const on = (p.body.blocked.down || p.body.touching.down) && Math.abs(p.y - (q.floor - q.cart.rim)) < 1
            && Math.abs(p.x - q.cart.x) <= q.cart.width / 2 + p.body.width / 2;
        if (!on) return;
        q.hinted = true;
        P.setFlag('hint_crawl');
        this.world.say(t(s.controls.device === 'pad' ? 'hint.crawl.pad' : 'hint.crawl'), PILLOWS.hintMs, { kind: 'plate' });
    },

    linenGoes(time) {
        const q = this.linen, s = this.scene, d = this.world.data.duct, sp = q.cat.sprite;
        q.cat.gone = true;
        q.T = time;
        s.tweens.killTweensOf(sp);
        sp.setScale(1);
        rumble('bolt');
        sfx.mrrp();
        // His leap: from the shelf to the mouth's lip, `up` px over the shaft's floor for her (the mouth as drawn opens
        // that much higher: the user, "it is shown from below the entrance").
        q.from = { x: sp.x, y: sp.y };
        q.lip = { x: d.mouthX + 12, y: d.upper - PILLOWS.up };
        sp.setFlipX(d.mouthX < sp.x).play('bumbot-leap');
        q.free.setAlpha(1);
        // The push goes on by itself until the last pillows are off the cart (they were made to land behind where it
        // then stands).
        if (s.pushing === q.cart) s.pushHeld = time + q.L.release * 1000 / PILLOWS.fps;
    },

    linenScene(time) {
        const q = this.linen, s = this.scene, w = this.world, d = w.data.duct, sh = w.shaft, sp = q.cat.sprite, L = q.L;
        const T = time - q.T;
        // Bumbot: the leap; the cover knocked as his paws reach it; in on his belly, his picture cut at the room's wall.
        if (!q.cat.away) {
            if (T >= PILLOWS.coverAt && !q.knocked) {
                q.knocked = true;
                if (sh.cover.visible) this.coverFalls();
                sfx.at(sp.x, q.floor).scramble();
            }
            if (T < PILLOWS.leapMs) {
                const k = T / PILLOWS.leapMs, e = 1 - (1 - k) * (1 - k);
                sp.setPosition(q.from.x + (q.lip.x - q.from.x) * e, q.from.y + (q.lip.y - q.from.y) * e);
            } else {
                if (!q.in) {
                    q.in = true;
                    q.depth = sp.depth;
                    q.flip = sp.flipX;
                    // (Turned by its scale for the cut: Phaser 4 crops a picture turned by `flipX` wrong.)
                    q.turn = q.flip ? -1 : 1;
                    sp.setDepth(sh.mouth.depth - 0.001).play('bumbot-crawl').setFlipX(false).setScale(q.turn, 1);
                }
                const k = Math.min(1, (T - PILLOWS.leapMs) / PILLOWS.crawlMs), e = 1 - Math.cos(k * Math.PI / 2);
                sp.setPosition(q.lip.x + (d.mouthX - 34 - q.lip.x) * e, q.lip.y);
                sp.setCrop(0, 0, Phaser.Math.Clamp(Math.round(q.turn < 0 ? sp.x + 32 - d.wallX : 64), 0, 64), 64);
                if (k >= 1) {
                    sp.setCrop().setScale(1).setFlipX(q.flip).setDepth(q.depth).setVisible(false).stop();
                    q.cat.away = true;
                    q.near.setAlpha(0);
                    q.far.setAlpha(0);
                    this.P.setFlag('bb4');          // (crawling is hers: `flagGives`; its hint when she is up on the cart, `linenHint`)
                }
            }
        }
        // The pillows: the clip's frame by the clock.
        const i = Math.min(L.frames - 1, Math.floor(T * PILLOWS.fps / 1000));
        if (i !== q.frame) {
            for (let f = q.frame + 1; f <= i; f++) {
                for (const [at, name, part] of PILLOWS.sounds) if (at === f) sfx.at(q.x0 + L[part].x + L[part].w / 2, q.floor)[name]();
            }
            q.frame = i;
            q.free.setFrame(i);
            if (i < L.release) q.ride.setFrame(i);
            else if (!q.off) {
                // The last two are off it: the cart is a cart again, hers to stand on.
                q.off = true;
                const at = q.cart.items.indexOf(q.ride);
                if (at >= 0) q.cart.items.splice(at, 1);
                q.ride.setVisible(false).setAlpha(0);
                q.cart.unwall?.();
            }
        }
        if (i >= L.frames - 1 && q.cat.away) {
            q.free.setAlpha(0);
            q.near.setAlpha(1);
            q.far.setAlpha(1);
            q.over = true;
        }
    },

    // The cover's fall (`fall` in assets/ship/shaft/shaft.json, tools/build_shaft.py): its frames' squares from where it
    // hung to where it lies, dropping as a thing falls (slow at first) while it turns, frame by frame, a quarter toward
    // the wall; on the floor a clang, a hop of 2 px tipped back a frame, and it settles; then the world's flat cover.
    coverFalls() {
        const s = this.scene, sh = this.world.shaft, F = sh.fall, c = sh.cover, down = sh.down, half = F.cell / 2;
        const last = F.frames - 1;
        const sp = s.add.sprite(F.start[0] + half, F.start[1] + half, 'shaft-cover-fall', 0).setDepth(c.depth);
        this.world.add([sp]);
        c.setVisible(false);
        this.coverDown = false;
        // (The flat one is shown by the world as the beat's flag is set, which comes before it lands: kept clear till then.)
        down.setAlpha(0);
        const t = { k: 0 };
        const place = (k, lift = 0) => sp.setPosition(Math.round(F.start[0] + half + (F.end[0] - F.start[0]) * k),
                                                      Math.round(F.start[1] + half + (F.end[1] - F.start[1]) * k * k) - lift);
        s.tweens.add({
            targets: t, k: 1, duration: 420, ease: 'Linear',
            onUpdate: () => { place(t.k); sp.setFrame(Math.min(last, Math.round(t.k * last))); },
            onComplete: () => {
                place(1);
                sp.setFrame(last);
                sfx.at(sp.x, sp.y).clang();
                const hop = { h: 0 };
                s.tweens.add({
                    targets: hop, h: 1, duration: 200, ease: 'Linear',
                    onUpdate: () => { const u = Math.sin(hop.h * Math.PI); place(1, Math.round(2 * u)); sp.setFrame(u > 0.5 ? last - 1 : last); },
                    onComplete: () => { sp.destroy(); down.setVisible(true).setAlpha(1); this.coverDown = true; },
                });
            },
        });
    },
};
