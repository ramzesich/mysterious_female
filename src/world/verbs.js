// Her new ways to move (GAME_DESIGN.md §6.1.2), mixed into the ship scene: crawling, the wall jump
// in grip socks, the glide under the parasol, pushing a cart. Each is learned on the way (the
// progression's `knows`), and none of them works with a tray in her hands.

import { PLAYER, VERBS, HOLDING } from '../config.js';
import { sfx } from '../sfx.js';
// Her body's px clear of a cart's end while she pushes it: her middle 29 px from a cart 39 px wide, a
// whole px so that it never flickers (it was 27.5: drawn 27 or 28; the user, 2026-11-18, "shift her a
// pixel back").
const PUSH_GAP = 2.5;

export const verbs = {
    resetVerbs() {
        this.kickUntil = 0;
        this.kickDir = 0;
        this.kickedAt = -Infinity;
        this.gliding = false;
        this.glideArmed = false;
        this.stairWind = false;
        this.stairCling = null;
        this.overRail = false;
        this.outRail = false;
        if (this.bal) {
            this.bal = null;
            this.script = null;
            this.player.body.setAllowGravity(true);
            this.player.setVisible(true);
        }
        this.balLow?.setVisible(false);
        this.balHigh?.setVisible(false);
        this.pushing = null;
        this.aside = false;
        if (this.crawling) this.setCrawl(false);
        this.crawling = false;
        this.world?.showParasol(false);
    },

    // --- Crawling: ↓ on the floor, then ←/→ -------------------------------------------------------
    // Under a laundry line, through a pillow fort, along the duct. She stays down while there is
    // something over her.
    updateCrawl(input, onFloor) {
        const p = this.player;
        // (Under something low she stays down; standing, it stops her like a wall.)
        const low = this.route === 'duct' || (this.crawling && this.world.lowAt(p.x, p.y));
        const can = this.progress.knows('crawl') && !this.world.carry && !this.isLunging() && !this.holding;
        // (Once down she stays down while ↓ is held: changing her body's size unsettles the floor a frame.)
        // (↓ still held from climbing down a ladder or stairs does not put her down: it must be let go first, the
        // user, 2026-11-21: "when the climb down finishes, she automatically crouches".)
        if (!input.down) this.downLatch = false;
        // (Nor where ↓ and Space is her way down a balcony's partition or a column: src/world/balcony.js.)
        const want = low || (input.down && !this.downLatch && can && (onFloor || this.crawling) && !this.balconyWayDown());
        if (want !== this.crawling) this.setCrawl(want);
        return this.crawling;
    },

    setCrawl(on) {
        const body = this.player.body;
        const h = on ? VERBS.crawlHeight : PLAYER.bodyHeight;
        const w = on ? 30 : PLAYER.bodyWidth;
        body.setSize(w, h);
        body.setOffset((PLAYER.cell - w) / 2, PLAYER.cell - h - PLAYER.sink);
        this.crawling = on;
    },

    poseCrawl(vx) {
        const p = this.player;
        this.idle = null;
        this.idleAt = this.time.now + 4000;
        if (this.anims.exists('her-crawl')) {
            // (At its own pace: her run's clip is played at her speed, `pose('run', |vx| / runSpeed)`, and what it was
            // last set to stayed, a fraction of it if she had been slowing down: the crawl then played "very slow",
            // the user, 2026-11-24, after the shaft's slide and not every time.)
            p.anims.timeScale = 1;
            if (Math.abs(vx) > 5) p.anims.play('her-crawl', true);
            else { p.anims.play('her-crawl', true); p.anims.pause(); }
            return;
        }
        // Until her crawl is drawn: bent right down, as when she reaches for Bumbot.
        p.anims.stop();
        p.setTexture('her', this.cache.json.get('her-meta').anims.reach[4]);
    },

    // --- The wall jump: grip socks (region 6) -----------------------------------------------------
    // In the air beside a grip (a pillar, a column, plating marked for it), jump kicks her up and away; she can steer
    // back and kick again, so one wall is enough to climb. (Not on the balconies: a partition is no wall to kick off;
    // her moves there are her own, src/world/balcony.js.)
    tryWallJump(input, time) {
        const p = this.player, body = p.body;
        if (!this.progress.knows('socks') || this.world.carry || this.holding) return false;
        if (!(time - this.jumpBufferedAt < PLAYER.jumpBufferMs)) return false;
        const grip = this.world.gripAt(p);
        if (!grip) return false;
        if (input.up) {
            // With up held: straight up it (a pole, a pillar, the plating), kick after kick.
            body.velocity.y = -PLAYER.jumpVelocity * VERBS.kickUp;
            body.velocity.x = 0;
            this.kickDir = 0;
        } else {
            const away = grip.away || (p.flipX ? 1 : -1);
            body.velocity.y = -PLAYER.jumpVelocity * VERBS.kickUp;
            body.velocity.x = away * VERBS.kickAway;
            this.kickDir = away;
        }
        const away = this.kickDir || (p.flipX ? -1 : 1);
        this.kickUntil = time + VERBS.kickMs;
        this.kickedAt = time;           // (letting go of jump doesn't cut a kick short)
        this.takeoffY = p.y;           // a fall is measured from her last hold
        p.setFlipX(away < 0);
        sfx.wallKick();
        return true;
    },

    // Pressed against a grip while falling, she slides down it slowly.
    updateWallSlide(dir) {
        const p = this.player, body = p.body;
        if (!this.progress.knows('socks') || this.world.carry || this.holding || body.velocity.y <= 0 || !dir) return false;
        const grip = this.world.gripAt(p);
        if (!grip || (grip.away && grip.away !== -dir)) return false;
        body.velocity.y = Math.min(body.velocity.y, VERBS.slideFall);
        this.takeoffY = p.y;
        return true;
    },

    // --- The glide: the parasol (region 8) --------------------------------------------------------
    // It opens while she holds jump in the air, falling: she sinks slowly and steers. Only a press made in
    // the air counts (the user, 2026-11-19: "it should open only on the second jump press (when we're in the
    // air). It stays open as long we hold that jump press"): a jump from the floor held on does not open
    // it. Letting go shuts it. A fall is measured from where she shuts it, so letting go high up is still a
    // long fall.
    updateGlide(input) {
        const p = this.player, body = p.body;
        this.glideArmed = input.jump && (this.glideArmed || this.glidePress);
        const on = this.progress.knows('parasol') && !this.world.carry && !this.holding && this.glideArmed && body.velocity.y > 0 && !this.crawling;
        if (on) {
            body.velocity.y = Math.min(body.velocity.y, VERBS.glideFall);
            this.takeoffY = p.y;
        }
        if (on !== this.gliding) {
            this.gliding = on;
            this.world.showParasol(on);
            if (on) sfx.parasolOpen(); else sfx.parasolShut();
        }
        return on;
    },

    // Standing aside (the promenade's WALKING lane, by the wall): ↑ held on the promenade's deck, she
    // steps back against the wall and the jogger runs by.
    updateAside(input, onFloor) {
        const pr = this.promenade;
        const on = !!pr && this.route === 'promenade' && onFloor && input.up && Math.abs(this.player.y - pr.floor) < 2
            && !this.world.carry;
        this.aside = on;
        return on;
    },

    // A jump with a tray is a low hop (§6.1.2); with Bumbot in her arms, a careful one.
    jumpScale() {
        return this.world.carry ? VERBS.hop : this.holding ? HOLDING.jump : 1;
    },

    // --- Pushing: E at a cart's end, then walk ----------------------------------------------------
    startPush(thing) {
        const p = this.player;
        this.pushing = thing;
        this.pushSince = this.time.now;
        this.mode = 'push';
        this.pushSide = p.x < thing.x ? -1 : 1;        // which side of it she stands on
        p.setFlipX(this.pushSide > 0);
        // (Her hands on its end, a px clear of its body: the user, 2026-11-18, "shift her a pixel back".)
        this.pushGap = thing.width / 2 + PLAYER.bodyWidth / 2 + PUSH_GAP;
        p.body.reset(thing.x + this.pushSide * this.pushGap, p.y);
        if (!this.pushFollowOn) {
            this.pushFollowOn = true;
            this.events.on('postupdate', () => this.pushFollow());
        }
        return true;
    },

    // The cart she pushes, at her gap ahead of her where the physics has just put her.
    pushFollow() {
        const t = this.pushing;
        if (!t || this.mode !== 'push') return;
        const at = Phaser.Math.Clamp(this.player.x - this.pushSide * this.pushGap, t.min, t.max);
        if (at !== t.x) t.moveTo(at);
    },

    updatePush(input, dt, time) {
        const p = this.player, body = p.body, t = this.pushing;
        // (`pushHeld`: until then the push goes on by itself, whatever the keys: the linen room's cart rolls on from under
        // its pillows as Bumbot scatters them, 0.7 s, src/world/linen.js.)
        const held = time < (this.pushHeld ?? 0);
        const dir = held ? -this.pushSide : (input.right ? 1 : 0) - (input.left ? 1 : 0);
        const onFloor = body.blocked.down || body.touching.down;
        // Letting go: E again, a jump, stepping back from it, or the floor going from under her.
        // (Not in the first moment: stepping up to its end, her body has not met the floor again yet.)
        const fresh = time - this.pushSince < 200;
        if (!fresh && !held && (input.activatePressed || input.jumpPressed || dir === this.pushSide || !onFloor)) {
            this.pushing = null;
            this.mode = 'play';
            return;
        }
        // She walks at the push's pace and the cart rolls on ahead of her, at her gap from it (the
        // user, 2026-11-18: one px further back), to the end of its way; there it holds her.
        // (The cart is set after the physics has moved her, before the frame is drawn: `pushFollow`.)
        const ahead = -this.pushSide, end = ahead > 0 ? t.max : t.min;
        const vx = dir === ahead && (end - t.x) * ahead > 0 ? dir * VERBS.pushSpeed : 0;
        body.velocity.x = vx;
        if (this.anims.exists('her-push')) {
            // (At its own pace: a walk at 0.6 before it, near-catch 4's in the linen room, had left her steps slow and
            // sliding, the user, 2026-11-23.)
            p.anims.timeScale = 1;
            p.anims.play('her-push', true);
            if (!vx) p.anims.pause();
        } else if (vx) this.pose('run', 0.5);
        else this.pose('stand');
    },
};
