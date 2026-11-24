// Region 8, "Top deck + funnel" (GAME_DESIGN.md §6.1.3, docs/population.md deck 12, the roof, the
// funnel and §6.8): deck 12's own things (the old lady's sunbed across the sun deck's walk, the
// basketballs out of the sports court, Teppanyaki's flares, the gulls on the bow), the funnel's
// (gusts and circling gulls on its stairway, the horn, the telescope), and the region's part of
// the story, mixed into the Story: the old lady's mojito, the engineer's coffee, the horn and what
// it sets off (the security officer drops his card, the old lady bolts and leaves her parasol and
// her book, the gulls leave the bow, Bumbot runs for it), the engineer's book, the court's quirk.
// Places come from maps/world.json (`topdeck`).

import { PLAYER, GAGS, FLARE, HAND_OVER } from '../config.js';
import { sfx } from '../sfx.js';
import { rumble, rumbleNow } from '../rumble.js';
import { t } from '../lang.js';
import { writeSave } from '../save.js';
import { Gusts, PerchGull } from './outside.js';

const M = 48;
const HALF = PLAYER.height / 2;
// A funnel gull's dive, px a second on average (speeding up as it comes): a fraction slower than the
// 470 its old dive from just over her head made (the user, 2026-11-18).
const FUNNEL_DIVE = 320;
const near = (s, x, y, dx = 900, dy = 320) => Math.abs(s.player.x - x) < dx && Math.abs(s.player.y - y) < dy;
// She is on the deck whose floor is y (in the air over it too). A thing drawn over her layer that belongs to a deck is
// drawn only then: from the deck under it, it showed through that deck's closed side (the court's ball, 2026-11-19).
const onDeck = (s, y) => s.player.y <= y + 4 && s.player.y > y - 140;
const onFloor = body => body.blocked.down || body.touching.down;

// The old lady on her sunbed across the walk (population: `npc_oldlady`): a block too wide and too
// high for a tray's hop; a jump clears it (landing on it she slides on over: nobody stands on the
// old lady). She glares at whoever comes near, and dozes once she has had her mojito.
// The sushi chef's trade (§4 2.1, thing 7, the user's, 2026-11-20): a tangerine for Bumbot's tin of sardines.
// Measured in his built frames (px ahead of his middle, px up from his feet, facing east): his palm's top in
// `take` (the tangerine sits on it), his fist in `catch` (the tangerine behind it), the tin's left and its
// bottom in `give`'s last frame (the world's tin, `thing:sardine-tin`, takes over there exactly). She stands
// `spot` px before him, on his front, to hand it over (the nigiri stand behind him since).
const SUSHI = {
    id: 'amb_sushi_chef', item: 'keep_sardines', keep: 'keep:cat:sardines', spot: 36, reach: 46,
    palm: [[11, 48], [22, 32], [14, 32], [24, 42], [24, 42], [24, 42], [24, 42], [24, 42], [24, 42]],
    fist: [[11, 47], [10, 37], [10, 50], [19, 61], [15, 61], [14, 61], [14, 61], [14, 61], [14, 61]],
    tin: { left: 15, w: 13, bottom: 41 },
    // A throw that reaches him: within `hitX` px of his middle, between `top` and `low` px over his feet
    // (above the glass case: the case itself is not him).
    hitX: 22, top: 70, low: 38,
};

export class OldLady {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;
        // The sunbed stays when she has gone; her bags and her towel go with her.
        const bed = s.add.image(def.x, def.y, 'sunbed').setOrigin(0.5, 1).setDepth(D.props + 0.03);
        const bag = s.add.image(def.x - 39, def.y, 'shipart', 'beach-bag').setOrigin(0.5, 1).setDepth(D.props + 0.06);
        // (Clear of the bed's foot, beside her parasol, not under the bed: the audit, 2026-11-15.)
        const duffel = s.add.image(def.x + 46, def.y, 'shipart', 'duffel-bag').setOrigin(0.5, 1).setDepth(D.props + 0.02);
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
                if (this.snored = !this.snored) sfx.at(L.x, d.y).snore();       // (every other "z")
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
                sfx.creak();
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
        sfx.at(L.x, L.y).grumble();
    }
}

// Basketballs on the sports court (population: `haz_balls`), each hoop's own player shooting at it (the user,
// 2026-11-19: "place two different basketball players on either side ... and make them throw the balls through their
// respective rings"; `tools/build_court.py`). A round of `period` s, the two hoops half a round apart: the jump shot
// (its wind-up is the tell), the ball from the hand up through the ring, down, bouncing twice along the walk toward
// its player and lying at their feet ("Bonked" from the throw until it lands the second time); they pick it up (the ball the game's until
// their hands take it), dribble, and shoot again. Everything is a function of the round's clock. The ball in their
// hands is washed as they are: the game's ball turns to and from its washed picture at the hand-overs.
const SHOT_FPS = 12, IDLE_FPS = 4, PICK_FPS = 10, DRIB_FPS = 10;
const FLIGHT = 0.6, DROP = 0.26, PICK = 3.2;
export class Balls {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x: the hoop, y, dir, reach, period, offset }
        this.rim = { x: def.x + def.dir * 24, y: def.y - 93 };
        this.x0 = this.rim.x + def.dir * 8;
        this.restX = this.x0 + def.dir * def.reach;
        // The player: facing the hoop, the ball lying at their toes at the rest spot.
        const m = s.cache.json.get('court-meta');
        this.m = m;
        this.who = def.dir > 0 ? 'man' : 'woman';
        this.face = -def.dir;
        const rc = m.ball[this.who].rest[0];
        this.player = s.add.sprite(this.restX, def.y, 'court', m.anims[this.who].shoot[0])
            .setOrigin((this.face < 0 ? m.cell - 1 - rc : rc) / m.cell, (m.feet + 1) / m.cell)
            .setFlipX(this.face < 0).setDepth(D.props + 0.03);
        const [cx, cy] = m.ball[this.who].release;
        this.release = { x: this.restX + this.face * (cx - rc), y: def.y - 1 - (m.feet - cy) };
        this.tR = (m.release - 1) / SHOT_FPS;
        this.ball = s.add.image(this.rim.x, this.rim.y, 'shipart', 'basketball').setDepth(D.player + 0.03).setVisible(false);
        this.ballLt = s.add.image(this.rim.x, this.rim.y, 'shipart', 'basketball-lt').setDepth(D.player + 0.031).setVisible(false);
        this.shadow = s.add.ellipse(this.rim.x, def.y - 1, 10, 3, 0x2e222f, 0.4).setDepth(D.props + 0.01).setVisible(false);
        world.add([this.player, this.ball, this.ballLt, this.shadow]);
        // (Through the ring: behind the hoop's own picture, its rim's front and net drawn over it.)
        const hoop = [...s.children.list, ...(s.worldLayer?.list ?? [])]
            .find(o => o.frame?.name?.startsWith?.('basketball-hoop') && Math.abs(o.x - def.x) < 48 && Math.abs(o.y - def.y) < 160);
        this.behind = hoop ? hoop.depth - 0.001 : D.props;
        this.hitAt = 0;
        this.turn = null;
        this.sounded = {};      // (not `heard`: every mover's `heard()` answers her cry)
    }

    // A lobbed tangerine coming down through the rim: it scores, a cheer, and it comes down again
    // (docs/plan-three-uses.md §2).
    offered(t) {
        const s = this.scene, r = this.rim, b = t.img.body;
        if (!t.thrown || !t.lob || t.scored || b.velocity.y <= 0 || Math.abs(t.img.x - r.x) > 8 || Math.abs(t.img.y - r.y) > 8) return false;
        t.scored = true;
        b.velocity.x *= 0.2;
        sfx.at(r.x, r.y).swish();
        sfx.at(r.x, r.y).cheer(1.4);
        this.world.sparkle(r.x, r.y + 6, 0xfbff86);
        return false;
    }

    // In a lunge she meets the ball: headed up and over, it comes down at its player's feet.
    lunged(kind, fromX) {
        const s = this.scene, d = this.def;
        if (kind !== 'ball' || !this.ball.visible || !this.turn || this.turn.off || Math.abs(this.ball.x - fromX) > 12) return false;
        sfx.at(this.ball.x, this.ball.y).bounce();
        this.away('headed', s.time.now, this.ball.x, d.y - 5 - this.ball.y, 0, false);
        return true;
    }

    // The ball sent off its way (off her in a hit, or headed in a lunge), back at its player's feet by the pick-up.
    away(kind, time, x, h, dir, front) {
        const T = this.turn, P = this.def.period;
        const at = this.clock(time);
        const o = { kind, at, x, h, dir, front };
        if (kind === 'rebound') {
            o.land = x + dir * 60;
            o.rest = Math.min(at + 0.6 + Math.abs(this.restX - o.land) / 120, P - 1.1);
        } else o.rest = Math.min(at + 0.7, P - 1.1);
        T.off = o;
        T.pickAt = Math.max(PICK, o.rest + 0.15);
    }

    clock(time) {
        return (time / 1000 + this.def.offset) % this.def.period;
    }

    // Where the ball is `t` s into the round: { x, h: px over the floor, lt: how washed (0 to 1), behind, hits,
    // rest } or null while it is in the player's hands.
    at(t) {
        const d = this.def, T = this.turn, grab = T.pickAt + (this.m.grab - 1) / PICK_FPS;
        if (t >= grab) return null;
        const washed = Math.max(0, Math.min(1, (t - (grab - 0.2)) / 0.2));
        const o = T.off;
        if (o && t >= o.at) {
            const k = t - o.at;
            if (o.kind === 'rebound') {
                if (k < 0.6) {
                    const u = k / 0.6;
                    return { x: o.x + (o.land - o.x) * u, h: o.h * (1 - u) + 4 * (o.front ? 30 : 40) * u * (1 - u), lt: 0 };
                }
                const u = Math.min(1, (t - o.at - 0.6) / Math.max(0.01, o.rest - o.at - 0.6));
                return { x: o.land + (this.restX - o.land) * u, h: 0, lt: washed, rest: u >= 1 };
            }
            const u = Math.min(1, k / Math.max(0.01, o.rest - o.at));
            return { x: o.x + (this.restX - o.x) * u, h: o.h * (1 - u) + 4 * 34 * u * (1 - u), lt: washed, rest: u >= 1 };
        }
        if (t < this.tR) return null;
        let k = t - this.tR;
        const drop = d.y - this.rim.y - 5, from = { x: this.release.x, h: d.y - 5 - this.release.y };
        if (k < FLIGHT) {
            // Up from the hand and down into the ring.
            const u = k / FLIGHT, peak = drop + 30;
            const h = u < 0.6 ? from.h + (peak - from.h) * (1 - (1 - u / 0.6) ** 2) : peak + (drop - peak) * ((u - 0.6) / 0.4) ** 2;
            return { x: from.x + (this.rim.x - from.x) * u, h, lt: Math.max(0, 1 - k / 0.2), hits: true };
        }
        k -= FLIGHT;
        // (Down through the net at the speed it came down into the ring (its flight's last 0.4 a parabola of 30 px),
        // falling faster, onto the walk.)
        const v = 2 * 30 / (0.4 * FLIGHT), g = 2 * (drop - v * DROP) / DROP ** 2;
        if (k < DROP) {
            const h = Math.max(0, drop - v * k - g * k * k / 2);
            return { x: this.rim.x + d.dir * 8 * (k / DROP), h, lt: 0, hits: true };
        }
        k -= DROP;
        const R = this.restX - this.x0;
        // (It hits her from the throw until it comes down on the walk the second time (the user, 2026-11-19): its first
        // hop, not the second or its roll.)
        const hop = (t0, len, hh, xa, xb, hits) => {
            const v = (k - t0) / len;
            return { x: this.x0 + R * (xa + (xb - xa) * v), h: 4 * hh * v * (1 - v), lt: 0, hits };
        };
        if (k < 0.56) return hop(0, 0.56, 44, 0, 0.5, true);
        if (k < 0.98) return hop(0.56, 0.42, 22, 0.5, 0.82, false);
        if (k < 1.4) return { x: this.x0 + R * (0.82 + 0.18 * ((k - 0.98) / 0.42)), h: 0, lt: washed };
        return { x: this.restX, h: 0, lt: washed, rest: true };
    }

    // The player's frame `t` s into the round.
    frame(t) {
        const A = this.m.anims[this.who], P = this.def.period, pk = this.turn.pickAt;
        if (t < 12 / SHOT_FPS) return A.shoot[1 + Math.floor(t * SHOT_FPS)];
        if (t < pk) return A.idle[Math.floor((t - 12 / SHOT_FPS) * IDLE_FPS) % 4];
        if (t < pk + 0.8) return A.pick[1 + Math.floor((t - pk) * PICK_FPS)];
        if (t < pk + 1.6 && pk + 1.6 <= P) return A.dribble[1 + Math.floor((t - pk - 0.8) * DRIB_FPS)];
        return A.shoot[0];
    }

    // A sound once a round, at its moment.
    once(key, t, at, play) {
        const n = this.turn.n;
        if (t >= at && this.sounded[key] !== n) {
            this.sounded[key] = n;
            play();
        }
    }

    update(dt, time) {
        const s = this.scene, d = this.def, p = s.player;
        if (!near(s, d.x, d.y, 700, 200) || !onDeck(s, d.y)) {
            this.ball.setVisible(false);
            this.ballLt.setVisible(false);
            this.shadow.setVisible(false);
            return;
        }
        const t = this.clock(time), n = Math.floor((time / 1000 + d.offset) / d.period);
        if (this.turn?.n !== n) this.turn = { n, pickAt: PICK, off: null };
        this.player.setFrame(this.frame(t));
        const q = this.at(t);
        this.ball.setVisible(!!q);
        this.ballLt.setVisible(!!q && q.lt > 0);
        this.shadow.setVisible(!!q);
        // (The swish through the net, each time it comes down on the walk, the dribble's bounce.)
        if (!this.turn.off) {
            this.once('toss', t, this.tR, () => sfx.at(this.release.x, this.release.y).toss());
            this.once('swish', t, this.tR + FLIGHT, () => sfx.at(this.rim.x, this.rim.y).swish());
            for (const [i, b] of [this.tR + FLIGHT + DROP, this.tR + FLIGHT + DROP + 0.56, this.tR + FLIGHT + DROP + 0.98].entries()) {
                this.once(`bounce${i}`, t, b, () => sfx.at(q ? q.x : this.restX, d.y).bounce());
            }
        }
        const pk = this.turn.pickAt;
        if (pk + 1.6 <= d.period) this.once('dribble', t, pk + 0.8 + 0.3, () => sfx.at(this.restX, d.y).bounce());
        if (!q) return;
        const y = d.y - 5 - q.h;
        // (In the ring and its net, behind the hoop's picture: its rim's front and the net over it. Above the rim it is
        // in front of the board, which stands over the net.)
        const inNet = Math.abs(q.x - this.rim.x) < 12 && y > this.rim.y + 1 && y < d.y - 62;
        const depth = inNet ? this.behind : s.DEPTH.player + 0.03;
        this.ball.setPosition(q.x, y).setAngle((q.x * 6) % 360).setDepth(depth);
        this.ballLt.setPosition(q.x, y).setAngle((q.x * 6) % 360).setDepth(depth + 0.001).setAlpha(q.lt);
        this.shadow.setPosition(q.x, d.y - 1).setAlpha(Math.max(0.15, 0.45 - q.h / 200));
        if (!q.hits || this.turn.off || s.mode !== 'play' || s.route !== 'inside' || time < this.hitAt) return;
        const hit = Math.abs(p.x - q.x) < PLAYER.bodyWidth / 2 + 5 && y > p.y - PLAYER.height - 3 && y < p.y + 2 && Math.abs(p.y - d.y) < 80;
        if (!hit) return;
        this.hitAt = time + 1500;
        sfx.bounce();
        if (this.world.carry) return this.world.carryBox.spill(q.x, false, 'ball');
        // (In her face, the side she faces, as the scenario reads it (14a): it bounces back off her, away in front of
        // her; on the back of her head (14b) it pops up higher and on over her as she goes down: the same way. Then it
        // rolls to its player's feet.)
        const face = p.flipX ? -1 : 1;
        this.away('rebound', time, q.x, q.h, face, (q.x - p.x) * face > 0);
        s.scareContact(q.x, 'ball');
    }
}

// A teppanyaki grill's flare (population: `haz_flare`): the chef's flourish, sparks on the plate,
// and a ball of flame over the counter and the way past it for a second: "Singed" (a tray is
// spilled; with nothing in her hands, her gag: `ride()`). With no one near, the two grills take
// turns by their clock. **The chef answers her coming** (the user, 2026-11-18: run past a clock's
// flare, it went up behind her): she runs at a quiet grill and his flourish starts so that the flame
// is up as she gets there (`FLARE`); stopped at the flourish, she lets it flare and passes in the
// lull after it (`coolMs`).
export class Flare {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, y, half, period, on, offset, chef }
        this.g = s.add.graphics().setDepth(D.player + 0.04);
        this.glow = s.add.rectangle(def.x, def.y - 64, def.half * 2 + 90, 128, 0xf9c22b, 0).setDepth(D.decor + 0.3);
        // (The smoke that wraps her, 19: over her and over the flame.)
        this.sg = s.add.graphics().setDepth(D.player + 0.05);
        world.add([this.g, this.glow, this.sg]);
        this.hitAt = 0;
        // (When the next flourish starts, ms of the scene's clock: the clock's own first, as the
        // grills took turns before, `offset` s apart; and when the lull after the last one ends.)
        const lead = (((def.period - def.on - FLARE.tellS - def.offset) % def.period) + def.period) % def.period;
        this.next = s.time.now + lead * 1000;
        this.coolUntil = 0;
    }

    // Her cry startles the chef: his next flare comes late (not one already alight).
    heard() {
        const s = this.scene, d = this.def;
        const now = s.time.now;
        if (!this.world.hears(d.x, d.y) || this.phase(now)[0] === 'on') return;
        this.next = Math.max(this.next, now) + FLARE.lateMs;
        this.coolUntil = Math.max(this.coolUntil, now + FLARE.lateMs);
        const chef = this.world.people.byId[d.chef];
        if (chef?.on) this.world.pop(chef.x, chef.y - PLAYER.height - 6, 'alert', 1000);
    }

    // 19, the ship scene's `thingGag` (`gags` sheet, tools/build_gags.py): a puff of black smoke
    // wraps her where the flame caught her, and under it she jumps back out of its reach (`back` px
    // past it, `slideMs`; doors and walls stop her) and is in her soot picture; it thins (`clearMs`):
    // her face black, her hair on end and singed; she blinks, a wisp of smoke curling off her hair,
    // and coughs out a puff of smoke; then her checkpoint.
    ride() {
        const s = this.scene, d = this.def, p = s.player, g = GAGS.flare;
        return {
            play: (done) => {
                const m = s.cache.json.get('gags-meta');
                const dir = p.flipX ? -1 : 1, side = Math.sign(p.x - d.x) || -dir;
                const pic = s.add.sprite(p.x, d.y, 'gags', m.anims['flare-blink'][0])
                    .setOrigin(0.5, m.floor / m.cell).setFlipX(dir < 0).setDepth(p.depth);
                this.world.add([pic]);
                this.pic = pic;
                const x0 = pic.x, end = s.stopShort(x0, d.x + side * (d.half + g.back), d.y, 16);
                this.smoke = { x: x0, t: 0 };
                // (Drawn at once: she is in her soot picture from this very frame.)
                this.drawSmoke(this.sg.clear());
                sfx.yelpHot();
                let t = 0;
                s.time.delayedCall(g.coverMs + g.clearMs * 0.6 + g.holdSootMs, () => {
                    pic.play('gags-flare-blink');
                    pic.once('animationcomplete-gags-flare-blink', () => {
                        pic.play('gags-flare-cough');
                        s.time.delayedCall(g.coughAtMs, () => sfx.at(pic.x, d.y).herCough());
                        pic.once('animationcomplete-gags-flare-cough', () => done());
                    });
                });
                s.script = (dt) => {
                    t += dt * 1000;
                    const u = Math.min(1, t / g.slideMs);
                    pic.x = x0 + (end - x0) * (1 - (1 - u) * (1 - u));
                    this.smoke.x = x0 + (pic.x - x0) * 0.7;
                    this.smoke.t = t;
                    p.x = pic.x;
                };
            },
            show: () => {
                this.pic?.destroy();
                this.pic = null;
                this.smoke = null;
            },
        };
    }

    // The smoke round her (19): thick to `coverMs`, a few embers in it, then thinning and rising over
    // `clearMs`.
    drawSmoke(g) {
        const b = this.smoke, G = GAGS.flare;
        if (!b) return;
        const k = Math.max(0, (b.t - G.coverMs) / G.clearMs);
        if (k >= 1) return;
        const a = 1 - k * k, y = this.def.y;
        // (Three columns of five over her, her hair on end and all, so that nothing of her shows.)
        for (let i = 0; i < 15; i++) {
            const ox = (i % 3 - 1) * 15 + ((i * 7) % 5) - 2, oy = 8 + Math.floor(i / 3) * 17 + ((i * 11) % 5);
            const r = 13 + ((i * 13) % 5) + k * 8;
            g.fillStyle(i % 4 ? 0x3e3546 : 0x625565, a)
                .fillCircle(b.x + ox * (1 + k * 0.6), y - oy - k * 26 + Math.sin(b.t / 200 + i) * 2, r);
        }
        if (b.t > G.coverMs) return;
        for (let i = 0; i < 6; i++) {
            const e = (b.t / G.coverMs + i * 0.17) % 1;
            g.fillStyle(i % 2 ? 0xf9c22b : 0xf79617, 1 - e)
                .fillRect(b.x + Math.sin(i * 2.3) * (14 + e * 12), y - 30 - i * 9 - e * 18, 2, 2);
        }
    }

    // 'calm', 'tell' (how far into it, 0-1) or 'on' (0-1).
    phase(time) {
        const d = this.def, t = (time - this.next) / 1000;
        if (t >= 0 && t < FLARE.tellS) return ['tell', t / FLARE.tellS];
        if (t >= FLARE.tellS && t < FLARE.tellS + d.on) return ['on', (t - FLARE.tellS) / d.on];
        return ['calm', 0];
    }

    update(dt, time) {
        const s = this.scene, d = this.def, p = s.player, g = this.g.clear();
        this.drawSmoke(this.sg.clear());
        // (A flare over: the lull, and the clock's next one.)
        if (time >= this.next + (FLARE.tellS + d.on) * 1000) {
            const end = this.next + (FLARE.tellS + d.on) * 1000;
            this.coolUntil = Math.max(this.coolUntil, end + FLARE.coolMs);
            this.next = end + (d.period - d.on - FLARE.tellS) * 1000;
        }
        if (!near(s, d.x, d.y, 700, 200) || !onDeck(s, d.y)) return;
        let [phase, k] = this.phase(time);
        // She runs at the quiet grill: the flourish starts now if the flame, once up, would meet her
        // as she gets to it (her speed, the flourish and the flame's rise: `riseS`). Not once she is
        // nearer than `nearK` of that: the flame would go up behind her.
        if (phase === 'calm' && time >= this.coolUntil && s.mode === 'play' && s.route === 'inside' && Math.abs(p.y - d.y) < 60) {
            const v = p.body?.velocity.x ?? 0, gap = Math.abs(p.x - d.x) - (d.half - 8);
            if (Math.abs(v) > 20 && Math.sign(v) === Math.sign(d.x - p.x) && gap <= Math.abs(v) * (FLARE.tellS + FLARE.riseS) && gap >= Math.abs(v) * (FLARE.tellS + FLARE.riseS) * FLARE.nearK) {
                this.next = time;
                [phase, k] = this.phase(time);
            }
        }
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
                sfx.at(d.x, d.y).tick();
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
        if (k < 0.1 && !this.lit) sfx.at(d.x, d.y).flare();
        this.lit = k < 0.9;
        if (env < 0.7 || s.mode !== 'play' || s.route !== 'inside' || time < this.hitAt) return;
        if (Math.abs(p.x - d.x) > d.half - 8 || Math.abs(p.y - d.y) > 90 || p.y < d.y - 100) return;
        this.hitAt = time + 1500;
        if (this.world.carry) this.world.carryBox.spill(d.x, false, 'flare');
        else s.scareContact(d.x, 'flare', { ride: this.ride() });
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
        this.state = 'circle';
        this.turn = 0;
    }

    // Her cry: a gull diving at her breaks off and climbs away.
    heard() {
        if (this.state !== 'dive') return;
        const v = this.dive, diver = this.gulls[this.turn % this.gulls.length];
        if (!this.world.hears(v.tx, v.ty, this.scene.route)) return;
        this.flier = diver;
        diver.away = { until: this.scene.time.now + 900, dir: v.tx < v.fx ? 1 : -1 };
        this.state = 'circle';
        this.turn++;
    }

    onStairs() {
        const s = this.scene;
        return s.mode === 'stairs' && s.flight?.outside;
    }

    // A tangerine on the deck round the funnel: one goes after it, and none swoops for 10 s
    // (docs/plan-three-uses.md §2).
    offered(t) {
        const c = this.centre, s = this.scene;
        if (this.state !== 'circle' || this.taker || Math.abs(t.img.x - c.x) > 300 || t.img.y < c.y - 100 || t.img.y > c.y + 400) return false;
        // (Only on something: a gull came down to one in the air and stood on nothing, part 5.)
        const on = t.img.body && (t.img.body.blocked.down || t.img.body.touching.down);
        if (!t.resting && !on) return false;
        const b = this.gulls[(this.turn + 1) % this.gulls.length];
        // (On the stairway it waits until the fruit lies still, and stands on the fruit's tread, or on the
        // one under it looking up a step; never in the step above.)
        const foot = t.img.y + 3, tread = x => s.treadTop(x) ?? 1e9;
        if (Math.abs(tread(t.img.x) - foot) <= 4 && !t.resting) return false;
        const downhill = tread(t.img.x - 6) > tread(t.img.x + 6) ? 1 : -1;
        const side = Math.abs(tread(t.img.x - 6) - foot) <= 4 ? 1 : Math.abs(tread(t.img.x + 6) - foot) <= 4 ? -1 : downhill;
        this.taker = b;
        this.quietUntil = s.time.now + 10000;
        this.world.gullTakes(b.sprite, t, () => {
            this.taker = null;
            b.sprite.setVisible(true);
        }, { side, footAt: x => s.treadTop(x) });
        return true;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def, g = this.def.gust;
        if (!near(s, this.centre.x, this.centre.y, 1100, 700)) return;
        const flap = Math.floor(time / 130) % 2 ? 'gull-down' : 'gull-up';
        // While it blows she holds on to the rail and does not move (the user, 2026-11-18, for the slide
        // back down the flight it was: "Looks weird"); the ship scene's `updateStairs` plays it.
        const on = this.onStairs();
        const blowing = on && this.gusts.phase(time) === 'blow';
        if (blowing && !s.stairWind) this.world.say(t('say.whoa'), 800);
        s.stairWind = blowing;
        // A gust on the funnel's stairway: a faint tremor while it blows.
        if (blowing) rumbleNow('gust', 400);
        // The gulls: round the lattice, the diver out of its circle.
        const diver = this.gulls[this.turn % this.gulls.length];
        for (const b of this.gulls) {
            if ((b === diver && this.state !== 'circle') || b === this.taker || b === this.flier) continue;
            const a = time / 1700 + b.i * Math.PI;
            const tx = this.centre.x + Math.cos(a) * 170, ty = this.centre.y + Math.sin(a) * 70 + Math.sin(a * 2.3) * 12;
            // (Back from a dive or from flying off: an easy climb back into the circle, not a snap.)
            const k = Math.min(1, dt * (b.back ? 0.9 : 3));
            b.x += (tx - b.x) * k;
            b.y += (ty - b.y) * k;
            if (b.back && Math.hypot(tx - b.x, ty - b.y) < 24) b.back = false;
            b.sprite.setFrame(flap).setPosition(b.x, b.y).setFlipX(Math.sin(a) > 0);
        }
        // A dive (the user, 2026-11-18: "Make the gull just dive in my direction ... from a few random
        // positions when in flight. Without a pause, or without taking a prepared position"; the hover
        // and the mark it had made it rare in play): every so often, between gusts, while she is on
        // the stairway, the next gull breaks off from wherever it is in its circle and dives straight
        // at where she is, speeding up. She can still step out of its way: it swoops on past and climbs
        // away. `swoop` (s) sets how often: a gap of a quarter to a half and more of it, at random.
        const calm = this.gusts.phase(time) === 'calm';
        this.nextAt ??= time + Phaser.Math.Between(250, 550) * d.swoop;
        if (this.state === 'circle') {
            if (on && calm && !s.stairCling && !this.flier && time > this.nextAt && time > (this.quietUntil ?? 0)) {
                const tx = p.x, ty = p.y - PLAYER.height * 0.6;
                const dist = Math.hypot(tx - diver.x, ty - diver.y);
                this.state = 'dive';
                this.dive = { fx: diver.x, fy: diver.y, tx, ty, t0: time, ms: Math.max(350, dist / FUNNEL_DIVE * 1000) };
                sfx.at(diver.x, diver.y).gullDive();
            }
        } else if (this.state === 'dive') {
            const v = this.dive, k = Math.min(1, (time - v.t0) / v.ms), e = k * (0.4 + 0.6 * k);
            diver.x = v.fx + (v.tx - v.fx) * e;
            diver.y = v.fy + (v.ty - v.fy) * e;
            const dir = v.tx < v.fx ? -1 : 1;
            diver.sprite.setFrame('gull-down').setPosition(diver.x, diver.y).setFlipX(dir < 0);
            // (Its body through hers, all the way down: not only where it was aimed.)
            const hit = this.onStairs() && Math.abs(p.x - diver.x) < 12 && diver.y > p.y - PLAYER.height && diver.y < p.y - 6;
            if (hit) s.scareContact(diver.x, 'funnelgull', { snatch: diver.sprite });
            if (hit || k >= 1) {
                // Having hit her it flies on, out over the sea (with the tangerine, if it took one), and
                // only then comes back round (the user, 2026-11-18: it "just disappeared immediately");
                // having missed, it swoops on past the way it was going and climbs away.
                this.flier = diver;
                diver.away = { until: time + (hit ? 1700 : 900), dir: hit ? -1 : dir };
                this.state = 'circle';
                this.turn++;
                this.nextAt = time + Phaser.Math.Between(250, 550) * d.swoop;
            }
        }
        const fl = this.flier;
        if (fl) {
            fl.x += fl.away.dir * 150 * dt;
            fl.y -= 55 * dt;
            fl.sprite.setFrame(flap).setPosition(fl.x, fl.y).setFlipX(fl.away.dir < 0);
            if (time > fl.away.until) {
                fl.away = null;
                fl.back = true;
                this.flier = null;
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
            // (On the windscreen's rail, `front`, they are nearer to us than she is: over her as she jumps by, and over
            // the windscreen drawn over her; the user, 2026-11-23.)
            const sprite = s.add.image(x, def.y, 'things', 'gull-perched').setOrigin(0.5, 1).setFlipX(i % 2 === 0)
                .setDepth(def.front ? D.player + 0.05 : D.props + 0.06);
            world.add([sprite]);
            return { sprite, x, i };
        });
        world.things.push({ id: def.id, x: (def.x0 + def.x1) / 2, y: def.y, route: 'inside', items: this.birds.map(b => b.sprite), until: 'flag:horn' });
    }

    update(dt, time) {
        const s = this.scene, d = this.def;
        if (this.gone || !near(s, (d.x0 + d.x1) / 2, d.y, 800, 300)) return;
        if (d.front) this.dodge(dt, time);
        // Now and then one shuffles, or stretches a wing.
        for (const b of this.birds) {
            if (b.up) continue;
            const beat = Math.floor(time / 900 + b.i * 1.7) % 7 === 0;
            b.sprite.y = d.y - (beat && Math.floor(time / 110) % 2 ? 1 : 0);
        }
    }

    // A jump at the gulls on the windscreen's rail (the user, 2026-11-23): the one her head comes up at takes off a little,
    // up and aside out of her way, flapping, and sits down again once she has landed. On the scene's clock (`k`, 0 sat,
    // 1 up), not a tween's.
    dodge(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        const onFloor = p.body.blocked.down || p.body.touching.down;
        const head = p.y - PLAYER.height;
        for (const b of this.birds) {
            if (b.up && !b.dodge) continue;
            if (!b.dodge) {
                if (s.mode === 'play' && s.route === 'inside' && !onFloor && Math.abs(p.x - b.x) < 24
                    && head < d.y + 8 && p.y > d.y - 40) {
                    b.up = true;
                    b.dodge = { k: 0, side: Math.sign(b.x - p.x) || 1, landed: 0 };
                    sfx.at(b.x, d.y).flap();
                }
                continue;
            }
            const D = b.dodge;
            // (Up while she is in the air; down a moment (0.15 s) after she lands.)
            D.landed = onFloor ? D.landed + dt : 0;
            const up = D.landed < 0.15;
            D.k = up ? Math.min(1, D.k + dt / 0.22) : Math.max(0, D.k - dt / 0.4);
            const e = Math.sin(D.k * Math.PI / 2);
            if (D.k === 0 && !up) {
                b.sprite.setFrame('gull-perched').setPosition(b.x, d.y);
                b.dodge = null;
                b.up = false;
                continue;
            }
            b.sprite.setFrame(Math.floor(time / 110) % 2 ? 'gull-up' : 'gull-down')
                .setPosition(Math.round(b.x + D.side * 10 * e), Math.round(d.y - 34 * e));
        }
    }

    // A tangerine by the flock: the nearest goes after it, and flies back (docs/plan-three-uses.md §2).
    offered(t) {
        const s = this.scene, d = this.def;
        if (this.gone || t.route !== 'inside' || t.img.x < d.x0 - 60 || t.img.x > d.x1 + 60 || Math.abs(t.img.y + 3 - d.y) > 12) return false;
        const free = this.birds.filter(b => !b.up);
        if (!free.length) return false;
        const b = free.reduce((a, c) => Math.abs(c.x - t.img.x) < Math.abs(a.x - t.img.x) ? c : a);
        b.up = true;
        this.world.gullTakes(b.sprite, t, () => {
            const flap = s.time.addEvent({ delay: 110, loop: true, callback: () => b.sprite.setFrame(b.sprite.frame.name === 'gull-up' ? 'gull-down' : 'gull-up') });
            b.sprite.setVisible(true).setFrame('gull-up').setPosition(b.x + 70, d.y - 110);
            s.tweens.add({ targets: b.sprite, x: b.x, y: d.y, duration: 1100, delay: 2500, ease: 'Sine.easeOut',
                onComplete: () => { flap.remove(); b.sprite.setFrame('gull-perched'); b.up = false; } });
        });
        return true;
    }

    // Her cry: the flock lifts a little, all at once, and settles again.
    heard() {
        const s = this.scene, d = this.def;
        if (this.gone || !this.birds.some(b => this.world.hears(b.x, d.y))) return;
        sfx.at((d.x0 + d.x1) / 2, d.y).flap();
        this.birds.forEach((b, i) => {
            if (b.up) return;
            b.up = true;
            const flap = s.time.addEvent({ delay: 110, loop: true, callback: () => b.sprite.setFrame(b.sprite.frame.name === 'gull-up' ? 'gull-down' : 'gull-up') });
            b.sprite.setFrame('gull-up');
            s.tweens.add({ targets: b.sprite, y: d.y - 30 - (i % 3) * 8, duration: 420, delay: i * 40, ease: 'Quad.easeOut', yoyo: true, hold: 500,
                onComplete: () => { flap.remove(); b.sprite.setFrame('gull-perched').setY(d.y); b.up = false; } });
        });
    }

    // Up and away over the bow, all at once. Resolves when the sky is clear.
    liftOff() {
        const s = this.scene, d = this.def;
        this.gone = true;
        sfx.gull();
        sfx.flap();
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
        // The funnel's white base carried on under the stairway's lower flight, out to its foot (the user,
        // 2026-11-18: moved out 12 px from the lattice, the flight's foot stood past the base, the sky
        // showing under its steps): as far up as the white goes, 64 px; the casing takes over above.
        const [fx, fy] = f.foot, [sx, sy] = f.shoulder, up = 64;
        const lx = fx + (sx - fx) * up / (fy - sy);
        const hull = s.add.graphics().setDepth(D.exterior + 0.045);
        hull.fillStyle(0xe8eaec, 1).fillPoints([{ x: fx, y: fy }, { x: lx, y: fy - up }, { x: lx + 40, y: fy - up }, { x: fx + 40, y: fy }], true);
        w.add([hull]);
        // And the lattice's navy frame carried out to the upper flight, whose steps stand 12 px out from it
        // (the user, 2026-11-18: the sky showed between them at the bend).
        const frame = s.add.graphics().setDepth(D.exterior + 0.045);
        const [tx, ty] = f.head;
        frame.fillStyle(0x323353, 1).fillPoints([{ x: sx, y: sy }, { x: tx, y: ty }, { x: tx + 14, y: ty }, { x: sx + 14, y: sy }], true);
        w.add([frame]);
        sock(f.shoulder[0] - 44, f.shoulder[1], 1);
        sock(f.x1 - 10, f.y - 30, 2);
        sock(f.foot[0] + 8, F.roofY, 3);           // (by the stairway's foot, wherever it stands)
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
    },

    updateTopdeck(dt, time) {
        const s = this.scene, w = this.world, her = s.player, T = this.T;
        if (!T) return;
        const L = T.lady;
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
            sfx.give();
            await w.tween({ targets: glass, x: L.x + 13, y: L.y - 34, duration: 380, ease: 'Sine.easeInOut' });
            // A long sip, and another; a sigh.
            L.still = '';
            L.idle = 'read';
            this.people.idle(L);
            L.state = 'acting';
            for (let i = 0; i < 2; i++) {
                await w.tween({ targets: glass, y: L.y - 43, angle: -28, duration: 260 });
                sfx.at(L.x, L.y).sip();
                await w.wait(420);
                await w.tween({ targets: glass, y: L.y - 34, angle: 0, duration: 220 });
                await w.wait(240);
            }
            const heart = s.add.text(L.x + 4, L.y - 62, '♥', { fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#e83b3b', resolution: 4 }).setOrigin(0.5).setDepth(s.DEPTH.fx);
            w.add([heart]);
            sfx.at(L.x, L.y).aah();
            s.tweens.add({ targets: heart, y: heart.y - 16, alpha: 0, duration: 1000, onComplete: () => heart.destroy() });
            await w.tween({ targets: glass, x: L.x + 30, y: L.y - 23, duration: 300 });
            sfx.at(glass.x, glass.y).clink();
            this.ladyGlass = glass;
            L.state = 'idle';
            sfx.done();
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
            sfx.give();
            await w.tween({ targets: cup, x: e.x + e.dir * 11, y: e.y - 36, duration: 380, ease: 'Sine.easeInOut' });
            cup.setVisible(!e.meta.anims.drink);
            await this.people.play(e, 'drink', { times: 2 });
            cup.destroy();
            e.state = 'acting';
            const steam = s.add.text(e.x + e.dir * 4, e.y - 66, '♨', { fontFamily: 'Verdana, sans-serif', fontSize: '10px', color: '#cd683d', resolution: 4 }).setOrigin(0.5).setDepth(s.DEPTH.fx);
            w.add([steam]);
            sfx.at(e.x, e.y).aah();
            s.tweens.add({ targets: steam, y: steam.y - 14, alpha: 0, duration: 900, onComplete: () => steam.destroy() });
            await w.wait(300);
            sfx.done();
            await this.people.play(e, 'wave');
            e.state = 'acting';
            // The chain off its hook, and up he goes.
            const gate = w.gates.find(g => g.needs === 'engineer');
            e.dir = F.ladderX < e.x ? -1 : 1;
            this.people.place(e);
            this.people.anim(e, 'walk');
            await w.tween({ targets: e, x: F.ladderX - e.dir * 10, duration: Math.abs(F.ladderX - e.x) * 12 + 80, onUpdate: () => this.people.place(e) });
            sfx.at(F.ladderX, e.y).ratchet();
            if (gate?.extra) await w.tween({ targets: gate.extra, alpha: 0, duration: 260 });
            e.x = F.ladderX;
            this.people.place(e);
            if (!this.people.anim(e, 'climb')) this.people.anim(e, 'walk');
            s.time.addEvent({ delay: 280, repeat: 5, callback: () => sfx.at(e.x, e.sprite.y).rung() });
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

    // E at the sushi chef (population: `amb_sushi_chef`; his cloud shows a tangerine): with a tangerine, she
    // offers it with a small bow (her apology's clip), he takes it over the glass case, puts it away, and hands
    // her Bumbot's tin of sardines (7) across. With none, his cloud hops. Her hands full: nothing.
    sushi() {
        const c = this.near(SUSHI.id, SUSHI.reach), w = this.world, s = this.scene;
        if (!c || this.P.has('sushi') || c.state === 'acting') return false;
        if (w.carry) return false;
        if (s.save.tangerines <= 0 && !s.infiniteTangerines()) {
            w.nudge(c);
            return true;
        }
        c.state = 'acting';
        w.cut(async () => {
            const her = s.player, spot = c.x - SUSHI.spot;
            // (To his front, the case's bare end: from his back she walks round.)
            if (Math.abs(her.x - spot) > 2) {
                her.setFlipX(spot < her.x);
                s.pose('run', 0.6);
                await w.tween({ targets: her, x: spot, duration: Math.abs(spot - her.x) / 70 * 1000 });
            }
            s.pose('stand');
            her.setFlipX(false);
            c.dir = -1;
            this.people.place(c);
            await w.wait(150);
            // Her bow, the tangerine held out in both hands (behind her, her hands over it).
            if (s.anims.exists('her-apology')) s.herClip('her-apology');
            const fruit = s.add.image(her.x + HAND_OVER.dx, her.y - HAND_OVER.dy, 'tangerine').setOrigin(0.5, 0.6)
                .setDepth(her.depth - 0.01).setVisible(false);
            w.add([fruit]);
            const show = () => fruit.setVisible((her.anims.currentFrame?.index ?? 1) - 1 >= HAND_OVER.frame);
            her.on('animationupdate', show);
            if (!s.infiniteTangerines()) s.save.tangerines -= 1;
            s.refreshHud();
            // His hand out over the case as hers come up.
            await w.wait(300);
            await this.people.play(c, 'take', { stay: true });
            await w.wait(Math.max(0, HAND_OVER.giveMs - 300 - 650));
            her.off('animationupdate', show);
            fruit.setVisible(true);
            sfx.give();
            const palm = this.sushiAt(c, SUSHI.palm.at(-1));
            await w.tween({ targets: fruit, x: palm.x, y: palm.y - 6, duration: 320, ease: 'Sine.easeInOut' });
            fruit.setOrigin(0.5, 1).setPosition(palm.x, palm.y).setDepth(c.sprite.depth - 0.001);
            this.P.setFlag('sushi');
            s.pose('stand');
            await w.wait(250);
            // Down behind the case with it, and up again with the tin.
            await this.sushiCarry(c, 'take-back', fruit, [...SUSHI.palm].reverse(), [0.5, 1], 0, 42);
            fruit.destroy();
            await w.wait(350);
            await this.people.play(c, 'give', { stay: true });
            await w.wait(200);
            const tin = this.sushiTin(c);
            const backDown = this.people.play(c, 'give-back');
            sfx.at(c.x, c.y).give();
            tin.setDepth(s.DEPTH.player + 0.05);
            await w.tween({ targets: tin, x: her.x - tin.width / 2 + 4, y: her.y - 34, duration: 420, ease: 'Sine.easeInOut' });
            tin.destroy();
            w.giveKeep(SUSHI.keep, her.x, her.y - 40);
            await backDown;
        });
        return true;
    },

    // A thrown tangerine that reaches the sushi chef over his case (or nearly: the user, 2026-11-20, "only if it hits
    // him, or almost hits him"): he catches it, puts it away, and sets the tin of sardines on the case's top for her
    // to take (`keep_sardines`, shown by `flag:sushi_tin`).
    sushiOffered(t) {
        const c = this.who(SUSHI.id), s = this.scene, w = this.world;
        if (!t.thrown || !c?.on || c.state === 'acting' || this.P.has('sushi') || t.route !== c.route) return false;
        const x = t.img.x, y = t.img.y;
        if (Math.abs(x - c.x) > SUSHI.hitX || y < c.y - SUSHI.top || y > c.y - SUSHI.low) return false;
        const fruit = s.loose.claim(t);
        c.state = 'acting';
        this.P.setFlag('sushi');
        // (Caught facing where it came from.)
        c.dir = x < c.x ? -1 : 1;
        if (Math.abs(x - c.x) < 4) c.dir = s.player.x < c.x ? -1 : 1;
        this.people.place(c);
        sfx.at(c.x, c.y).take();
        (async () => {
            await this.sushiCarry(c, 'catch', fruit, SUSHI.fist, [0.5, 0.5], 3);
            await w.wait(400);
            await this.sushiCarry(c, 'catch-back', fruit, [...SUSHI.fist].reverse(), [0.5, 0.5], 0, 55);
            fruit.destroy();
            // To the case's front (his own way), and the tin set down on it.
            c.dir = -1;
            this.people.place(c);
            await w.wait(300);
            await this.people.play(c, 'give', { stay: true });
            await w.wait(200);
            const tin = this.sushiTin(c);
            const pick = w.things.find(k => k.id === SUSHI.item)?.pick;
            const backDown = this.people.play(c, 'give-back');
            if (pick) await w.tween({ targets: tin, x: pick.x - pick.displayWidth * pick.originX, y: pick.y + pick.displayHeight * (1 - pick.originY), duration: 140, ease: 'Quad.easeIn' });
            sfx.at(c.x, c.y).clink();
            tin.destroy();
            this.P.setFlag('sushi_tin');
            w.refresh();
            await backDown;
        })();
        return true;
    },

    // A world point of the sushi chef's frame: [px ahead of his middle, px up from his feet] (east-facing).
    sushiAt(c, [dx, up]) {
        const sp = c.sprite;
        // (A flipped frame is mirrored in place: its column c lands at 79 - c of the cell.)
        return { x: Math.round(sp.x) + (sp.flipX ? -dx - 1 : dx), y: Math.round(sp.y) - up };
    },

    // One of his clips with the tangerine in his hand: it follows `points` (one per frame); `from` the first
    // frame it is held in (before, it flies there, a tween as long as those frames).
    // `low`: once his hand is lower than so many px over his feet the tangerine is put away (gone from his
    // hand, not shown at his chin on its way down).
    sushiCarry(c, clip, fruit, points, origin, from = 0, low = 0) {
        const s = this.scene, fps = c.meta.fps?.[clip] ?? 10;
        fruit.setOrigin(...origin).setDepth(c.sprite.depth - 0.001);
        const at = i => this.sushiAt(c, points[Math.min(points.length - 1, i)]);
        if (from > 0) s.tweens.add({ targets: fruit, ...at(from), duration: from / fps * 1000, ease: 'Sine.easeOut' });
        const follow = (anim, f) => {
            const i = f.index - 1;
            if (i >= from) fruit.setPosition(at(i).x, at(i).y);
            if (low && points[Math.min(points.length - 1, i)][1] < low) fruit.setVisible(false);
        };
        c.sprite.on('animationupdate', follow);
        return this.people.play(c, clip, { stay: true }).then(() => c.sprite.off('animationupdate', follow));
    },

    // The world's tin of sardines where his `give` clip's last frame holds it (his frame shown without it next).
    sushiTin(c) {
        const s = this.scene, sp = c.sprite, T = SUSHI.tin;
        const left = sp.flipX ? Math.round(sp.x) - T.left - T.w : Math.round(sp.x) + T.left;
        const tin = s.add.image(left, Math.round(sp.y) - T.bottom, 'things', 'sardine-tin').setOrigin(0, 1).setDepth(sp.depth + 0.002);
        this.world.add([tin]);
        return tin;
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
            sfx.take();
            await w.tween({ targets: ball, x: her.x + dir * 8, y: her.y - 40, duration: 220 });
            if (s.anims.exists('her-throw')) her.anims.play('her-throw');
            else s.pose('rise');
            await w.tween({ targets: ball, y: her.y - 62, duration: 240, ease: 'Quad.easeOut' });
            sfx.toss();
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
            sfx.at(rim.x, rim.y).swish();
            if (!w.save.seen.includes('sec_court')) sfx.secret();
            w.sparkle(rim.x, rim.y + 6, 0xfbff86);
            await w.tween({ targets: ball, y: C.y - 5, duration: 330, ease: 'Quad.easeIn' });
            sfx.at(ball.x, C.y).bounce();
            await w.tween({ targets: ball, y: C.y - 30, x: ball.x - dir * 20, duration: 220, ease: 'Quad.easeOut' });
            await w.tween({ targets: ball, y: C.y - 5, x: ball.x - dir * 20, duration: 220, ease: 'Quad.easeIn' });
            sfx.at(ball.x, C.y).bounce();
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
            sfx.scope();
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
            if (w.save.seen.includes('sec_telescope')) sfx.sparkle();
            else sfx.secret();
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
        const s = this.scene, w = this.world, P = this.P, her = s.player, F = this.T.funnel;
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
        sfx.horn(ms / 1000);
        rumble('horn', ms);
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
        sfx.at(cat.x, cat.y).meow();
        cat.play('bumbot-jump');
        s.tweens.chain({
            targets: cat,
            tweens: [
                { y: cat.y - 34, duration: 200, ease: 'Quad.easeOut' },
                { x: f.head[0] + 4, y: f.head[1], duration: 280, ease: 'Quad.easeIn', onComplete: () => { cat.play('bumbot-run'); sfx.at(cat.x, cat.y).scramble(); } },
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
            s.tweens.add({ targets: cat, x: toX, duration: ms, delay, onStart: () => sfx.scramble(), onComplete: () => cat.destroy() });
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
                sfx.yelp();
                await w.tween({ targets: rival.sprite, y: rival.y - 22, duration: 170, ease: 'Quad.easeOut', yoyo: true });
                s.tweens.add({ targets: card, x: L.cardX, y: L.y - 5, angle: 360, duration: 520, ease: 'Quad.easeIn', onComplete: () => sfx.sparkle() });
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
                sfx.oh();
                s.tweens.add({ targets: bang, alpha: 0, delay: 500, duration: 200, onComplete: () => bang.destroy() });
                await w.tween({ targets: lady.sprite, y: lady.sprite.y - 12, duration: 150, ease: 'Quad.easeOut', yoyo: true });
                // Her bags under her arm, and off, forward.
                const bags = w.things.find(t => t.id === 'blk_oldlady')?.items ?? [];
                sfx.scrape();
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
