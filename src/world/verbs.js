// Her new ways to move (GAME_DESIGN.md §6.1.2), mixed into the ship scene: crawling, the wall jump
// in grip socks, the glide under the parasol, pushing a cart. Each is learned on the way (the
// progression's `knows`), and none of them works with a tray in her hands.

import { PLAYER, VERBS } from '../config.js';
import { sfx } from '../sfx.js';

export const verbs = {
    resetVerbs() {
        this.kickUntil = 0;
        this.kickDir = 0;
        this.kickedAt = -Infinity;
        this.gliding = false;
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
        const can = this.progress.knows('crawl') && !this.world.carry && !this.isDashing();
        // (Once down she stays down while ↓ is held: changing her body's size unsettles the floor a frame.)
        const want = low || (input.down && can && (onFloor || this.crawling));
        if (want !== this.crawling) this.setCrawl(want);
        return this.crawling;
    },

    setCrawl(on) {
        const body = this.player.body;
        const h = on ? VERBS.crawlHeight : PLAYER.bodyHeight;
        const w = on ? 30 : PLAYER.bodyWidth;
        body.setSize(w, h);
        body.setOffset((PLAYER.cell - w) / 2, PLAYER.cell - h);
        this.crawling = on;
    },

    poseCrawl(vx) {
        const p = this.player;
        this.idle = null;
        this.idleAt = this.time.now + 4000;
        if (this.anims.exists('her-crawl')) {
            if (Math.abs(vx) > 5) p.anims.play('her-crawl', true);
            else { p.anims.play('her-crawl', true); p.anims.pause(); }
            return;
        }
        // Until her crawl is drawn: bent right down, as when she reaches for Bumbot.
        p.anims.stop();
        p.setTexture('her', this.cache.json.get('her-meta').anims.reach[4]);
    },

    // --- The wall jump: grip socks (region 6) -----------------------------------------------------
    // In the air beside a grip (a balcony's partition, a pillar, plating marked for it), jump kicks
    // her up and away; she can steer back and kick again, so one wall is enough to climb.
    tryWallJump(input, time) {
        const p = this.player, body = p.body;
        if (!this.progress.knows('socks') || this.world.carry) return false;
        if (!(time - this.jumpBufferedAt < PLAYER.jumpBufferMs)) return false;
        const grip = this.world.gripAt(p);
        if (!grip) return false;
        if (input.up) {
            // With up held: straight up it (a pole, a pillar, the plating), kick after kick.
            body.velocity.y = -PLAYER.jumpVelocity * VERBS.kickUp;
            body.velocity.x = 0;
            this.kickDir = 0;
        } else if (grip.over) {
            // A balcony's partition: up and over its panel, the way she is going.
            if (p.y < grip.top + 8) return false;       // over its top already
            const dir = (input.right ? 1 : 0) - (input.left ? 1 : 0) || (p.flipX ? -1 : 1);
            const rise = p.y - grip.top + VERBS.vaultClear;
            body.velocity.y = -Math.max(Math.sqrt(2 * PLAYER.gravity * rise), VERBS.vaultMin);
            body.velocity.x = dir * PLAYER.runSpeed;
            this.kickDir = dir;
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
        sfx.jump();
        return true;
    },

    // Pressed against a grip while falling, she slides down it slowly.
    updateWallSlide(dir) {
        const p = this.player, body = p.body;
        if (!this.progress.knows('socks') || this.world.carry || body.velocity.y <= 0 || !dir) return false;
        const grip = this.world.gripAt(p);
        if (!grip || (grip.away && grip.away !== -dir)) return false;
        if (grip.over && p.y < grip.top) return false;      // over a partition's panel there is only its pole
        body.velocity.y = Math.min(body.velocity.y, VERBS.slideFall);
        this.takeoffY = p.y;
        return true;
    },

    // --- The glide: the parasol (region 8) --------------------------------------------------------
    // It opens only while she holds jump in the air, falling: she sinks slowly and steers. A fall is
    // measured from where she closes it, so letting go high up is still a long fall.
    updateGlide(input) {
        const p = this.player, body = p.body;
        const on = this.progress.knows('parasol') && !this.world.carry && input.jump && body.velocity.y > 0 && !this.crawling;
        if (on) {
            body.velocity.y = Math.min(body.velocity.y, VERBS.glideFall);
            this.takeoffY = p.y;
        }
        if (on !== this.gliding) {
            this.gliding = on;
            this.world.showParasol(on);
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

    // A jump with a tray is a low hop (§6.1.2).
    jumpScale() {
        return this.world.carry ? VERBS.hop : 1;
    },

    // --- Pushing: E at a cart's end, then walk ----------------------------------------------------
    startPush(thing) {
        const p = this.player;
        this.pushing = thing;
        this.pushSince = this.time.now;
        this.mode = 'push';
        this.pushSide = p.x < thing.x ? -1 : 1;        // which side of it she stands on
        p.setFlipX(this.pushSide > 0);
        return true;
    },

    updatePush(input, dt, time) {
        const p = this.player, body = p.body, t = this.pushing;
        const dir = (input.right ? 1 : 0) - (input.left ? 1 : 0);
        const onFloor = body.blocked.down || body.touching.down;
        // Letting go: E again, a jump, stepping back from it, or the floor going from under her.
        // (Not in the first moment: stepping up to its end, her body has not met the floor again yet.)
        const fresh = time - this.pushSince < 200;
        if (!fresh && (input.activatePressed || input.jumpPressed || dir === this.pushSide || !onFloor)) {
            this.pushing = null;
            this.mode = 'play';
            return;
        }
        // The cart rolls ahead of her and she keeps pace with it (it holds her otherwise).
        let vx = 0;
        if (dir === -this.pushSide) {
            const to = Phaser.Math.Clamp(t.x + dir * VERBS.pushSpeed * dt, t.min, t.max);
            vx = (to - t.x) / dt;
            if (to !== t.x) t.moveTo(to);
        }
        body.velocity.x = vx;
        if (this.anims.exists('her-push')) {
            p.anims.play('her-push', true);
            if (!vx) p.anims.pause();
        } else if (vx) this.pose('run', 0.5);
        else this.pose('stand');
    },
};
