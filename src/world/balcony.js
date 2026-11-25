// Her three moves on the balconies of decks 8 to 10 (region 7; the remake of 2026-11-25, docs/balconies-remake-log.md),
// mixed into the ship scene. A balcony has no wall to kick off: the only way from one to another is outside its rail.
// So, in the grip socks, at a partition:
//
//   Space            along: she jumps to the partition's outer edge, crosses in front of it and drops on its other side
//   ↑ and Space      up:    onto the rail on her own side, onto the partition's fin, up it to the rail above, in off it
//   ↓ and Space      down:  the same the other way
//
// Each is its clips' frames on one clock (`assets/ship/balconies/moves.png`, tools/build_balconies.py): the mount (onto
// the rail), the swing (onto the fin, a foot on the rail each side of it), the climb (perch to perch) and the crossing.
// Up is mount, swing, climb, then the swing and the mount backwards on the deck above; down, the same with the climb
// backwards. The clips are drawn for her forward of the partition; aft of it they are mirrored.
//
// **The layering is one rule** (the user: "Look carefully how she transitions from behind the balcony glass to in
// front of it"): what of her is under the top of the rail of the balcony she is inside of is behind its glass, its
// rail and its partition (her own depth: the fronts and the panels are drawn over her); what is over that rail's top,
// and all of her while she is out on the fin, is in front of everything. Two pictures of the same frame, cut at the
// rail's top.

import { BALCONY, PLAYER } from '../config.js';
import { sfx } from '../sfx.js';
import { t } from '../lang.js';

const OUT = 'promenade';

export const balcony = {
    // The partition she is at: within reach of its middle, her feet on its balcony's floor or in a jump over it.
    partitionAt() {
        const p = this.player, list = this.world.data.outside.partitions ?? [];
        for (const P of list) {
            if (p.y > P.y + 2 || p.y < P.y - 70) continue;
            const dx = p.x - P.x;
            if (Math.abs(dx) > BALCONY.reach || Math.abs(dx) < 3) continue;
            return { P, side: dx < 0 ? -1 : 1 };
        }
        return null;
    },

    // A column of the boat walkway she is at: on the walkway at its foot, or on deck 8's balcony over it. The climb on
    // its outside is the fin's (the same clips); over it there is no partition to hold, so she hops onto and off deck
    // 8's rail (her jump's frames).
    columnAt() {
        const p = this.player;
        for (const C of this.world.data.outside.columns ?? []) {
            const dx = p.x - C.x;
            if (Math.abs(dx) > BALCONY.reach) continue;
            if (p.y <= C.y + 2 && p.y > C.y - 70 && Math.abs(dx) >= 4) return { C, side: dx < 0 ? -1 : 1, foot: true };
            if (p.y <= C.top + 2 && p.y > C.top - 70) return { C, side: dx < 0 ? -1 : 1, foot: false };
        }
        return null;
    },

    // Whether ↓ and Space would take her down from where she stands (so that ↓ held for it does not put her on her
    // hands and knees first).
    balconyWayDown() {
        if (this.route !== OUT || !this.progress.knows('socks') || this.world.carry || this.holding) return false;
        const at = this.partitionAt();
        if (at && (at.side < 0 ? at.P.downFore : at.P.downAft)) return true;
        const c = this.columnAt();
        return !!c && !c.foot;
    },

    // Whether someone is on the balcony forward (-1) or aft (1) of a partition, on the floor y.
    balconyTaken(P, side, y) {
        const ux = P.x - 3 + (side < 0 ? -this.world.data.outside.unit : 0);
        return (this.world.data.balcony.occupied ?? []).find(o => o.x0 === ux && o.y === y) ?? null;
    },

    // Space in play on the outside route: a move, if she is at a partition and the way is there.
    tryBalcony(input) {
        const p = this.player;
        if (!this.progress.knows('socks') || this.world.carry || this.holding) return false;
        const col = input.up || input.down ? this.columnAt() : null;
        if (col && (col.foot ? input.up && !!this.world.balconyFloor(col.C.x, col.C.top) : input.down)) {
            // (The column's own middle and floors, in a partition's terms; the walkway's picture of her is `lift` px up.)
            const C = col.C, P = { x: C.x, y: col.foot ? C.y - BALCONY.lift : C.top, column: C };
            this.startBalcony(P, col.foot ? col.side : 0, col.foot ? 'up' : 'down', col.side, col.foot ? C.top : C.y - BALCONY.lift);
            return true;
        }
        const at = this.partitionAt();
        if (!at) return false;
        const { P, side } = at, pitch = this.deckPitch;
        let kind, to = side, floor = P.y;
        if (input.up) {
            if (!(side < 0 ? P.upFore : P.upAft)) return false;
            kind = 'up'; floor = P.y - pitch;
        } else if (input.down) {
            if (!(side < 0 ? P.downFore : P.downAft)) return false;
            kind = 'down'; floor = P.y + pitch;
        } else {
            // (Along: only toward the partition, the way she is going or facing; and only where a balcony is beyond it.)
            const dir = (input.right ? 1 : 0) - (input.left ? 1 : 0) || (p.flipX ? -1 : 1);
            if (dir !== -side || !(side < 0 ? P.aft : P.fore)) return false;
            kind = 'along'; to = -side;
        }
        this.startBalcony(P, side, kind, to, floor);
        return true;
    },

    // The frames of a move, in order: [clip, frame, ms, the floor its cell is placed from, the floor of the balcony she is
    // inside of at it (null: out on the fin)].
    balconySteps(kind, y, floor, column = false) {
        const B = BALCONY, L = this.cache.json.get('balcony-layout').moves.clips;
        const A = this.cache.json.get('her-meta').anims;
        const run = (clip, ms, at, inside, back = false, from = 0) => {
            const n = L[clip].at.length, out = [];
            for (let k = from; k < n; k++) out.push([clip, back ? n - 1 - k : k, ms, at, inside]);
            return out;
        };
        if (kind === 'along') return run('along', B.alongMs, y, y);
        // (The climb's cells are placed from the lower floor of the two.)
        const low = Math.max(y, floor);
        // (At a column: the mount and the swing only at the walkway's rail; on deck 8 a hop, her own sheet's frames.)
        if (column && kind === 'up') return [...run('mount', B.mountMs, y, y, false, 1), ...run('swing', B.mountMs, y, y),
            ...run('climb', B.climbMs, low, null, false, 1), ['her', A.fall[0], B.hopMs, floor, floor]];
        if (column) return [['her', A.rise[0], B.hopMs, y, y], ...run('climb', B.climbMs, low, null, true),
            ...run('swing', B.mountMs, floor, floor, true, 1), ...run('mount', B.mountMs, floor, floor, true)];
        return [...run('mount', B.mountMs, y, y, false, 1), ...run('swing', B.mountMs, y, y),
            ...run('climb', B.climbMs, low, null, kind === 'down', 1),
            ...run('swing', B.mountMs, floor, floor, true, 1), ...run('mount', B.mountMs, floor, floor, true)];
    },

    startBalcony(P, side, kind, to, floor) {
        if (!side) side = to;
        const p = this.player, D = this.DEPTH;
        if (this.crawling) this.setCrawl(false);
        const steps = this.balconySteps(kind, P.y, floor, !!P.column);
        if (P.column && kind === 'down') side = to;         // (the side of the column she comes down on: where she stood over it)
        // (Someone on the balcony she is making for: she sees them from the rail, and goes back the way she came.)
        const taken = this.balconyTaken(P, to, floor);
        const peek = !taken ? -1 : kind === 'along' ? BALCONY.peek : steps.findIndex((s, i) => i > 0 && s[4] === floor && s[0] === 'swing');
        this.bal = { P, side, kind, to, floor, steps, i: 0, t: 0, x0: p.x, y0: P.column && kind === 'up' ? P.column.y : P.y, taken, peek, back: false, held: 0 };
        this.mode = 'scripted';
        this.script = (dt, time) => this.updateBalcony(dt, time);
        this.idle = null;
        this.jumpBufferedAt = -Infinity;
        p.body.setVelocity(0, 0);
        p.body.setAllowGravity(false);
        p.setVisible(false);
        for (const k of ['balLow', 'balHigh']) {
            const q = this[k] ??= this.add.image(0, 0, 'balcony-moves', 0).setOrigin(0, 0);
            if (!this.worldLayer.list.includes(q)) this.worldLayer.add(q);
            q.setDepth(k === 'balLow' ? D.player : D.player + BALCONY.front).setVisible(true);
        }
        sfx.wallKick();
        this.showBalcony();
    },

    // The frame of the moment: its two pictures, cut at the rail's top of the balcony she is inside of; and her body
    // (unseen) where the frame has her, for the camera and the cut-away.
    showBalcony() {
        const b = this.bal, p = this.player;
        const lay = this.cache.json.get('balcony-layout'), L = lay.moves, [cw, ch] = L.cell;
        const [clip, k, , at, inside] = b.steps[b.i];
        const mirror = b.side > 0;
        let key = 'balcony-moves', frame, x, y, w = cw, h = ch;
        if (clip === 'her') {
            // (Her own sheet's frame, in the socks: a hop onto or off the rail over a column, her feet `hop` px up.)
            key = 'her-socks'; frame = k; w = h = PLAYER.cell;
            x = b.P.x + (mirror ? w / 2 : -w / 2); y = at - BALCONY.hop - h + 1;
        } else {
            const c = L.clips[clip], [ox, oy] = c.at[k];
            frame = c.first + k; x = mirror ? b.P.x - ox : b.P.x + ox; y = at + oy;
        }
        const cut = inside == null ? h : Phaser.Math.Clamp(inside - lay.rail - y, 0, h);       // rows of the cell over the rail's top
        this.balHigh.setTexture(key, frame).setPosition(x, y).setScale(mirror ? -1 : 1, 1).setCrop(0, 0, w, cut).setVisible(cut > 0);
        this.balLow.setTexture(key, frame).setPosition(x, y).setScale(mirror ? -1 : 1, 1).setCrop(0, cut, w, h - cut).setVisible(cut < h);
        // Her body: along, from where she stood to where the crossing sets her down; up and down, at the partition,
        // from floor to floor as she climbs.
        const u = b.steps.length > 1 ? b.i / (b.steps.length - 1) : 1;
        const n0 = b.steps.findIndex(s => s[4] == null), n1 = b.steps.length - 1 - [...b.steps].reverse().findIndex(s => s[4] == null);
        const v = n0 < 0 ? 0 : Phaser.Math.Clamp((b.i - n0) / Math.max(1, n1 - n0), 0, 1);
        const px = b.kind === 'along' ? Phaser.Math.Linear(b.x0, b.P.x + b.to * BALCONY.stand, u) : Phaser.Math.Linear(b.x0, b.P.x + b.side * BALCONY.stand, Math.min(1, u * 6));
        const py = b.kind === 'along' ? b.y0 : Phaser.Math.Linear(b.y0, b.P.column && b.kind === 'down' ? b.P.column.y : b.floor, v);
        p.setPosition(px, py);
        p.body.reset(px, py);
        p.body.setAllowGravity(false);
    },

    updateBalcony(dt, time) {
        const b = this.bal, p = this.player;
        if (!b) return;
        const step = b.steps[b.i];
        // (A gust while she is out on the fin: she holds on until it drops.)
        const out = step[4] == null && this.world.gusts?.phase(time) === 'blow';
        if (b.held > 0) b.held -= dt * 1000;
        else if (!out) b.t += dt * 1000;
        while (b.t >= b.steps[b.i][2]) {
            b.t -= b.steps[b.i][2];
            if (!b.back && b.i === b.peek) {
                // The balcony she was making for has someone on it: seen from the rail. A beat, and back.
                b.back = true;
                b.held = BALCONY.peekMs;
                b.taken && this.world.balconySeen?.(b.taken);
                break;
            }
            b.i += b.back ? -1 : 1;
            if (b.i < 0 || b.i >= b.steps.length) return this.endBalcony();
            const s = b.steps[b.i];
            if (s[0] === 'climb' && s[1] % 4 === 0) sfx.rung();
        }
        this.showBalcony();
    },

    endBalcony() {
        const b = this.bal, p = this.player;
        this.bal = null;
        this.script = null;
        this.mode = 'play';
        this.balLow.setVisible(false);
        this.balHigh.setVisible(false);
        const back = b.back;
        // Where the move leaves her: along, just past the partition and a few px up, coming down the way she went; up and
        // down, stood at the partition on the other floor, turned to it; turned back from an occupied balcony, where
        // she started.
        const side = back || b.kind !== 'along' ? b.side : b.to;
        const col = b.P.column, onto = col && b.kind === 'up';           // (off a column's top: on deck 8's rail, over the column)
        const x = onto ? b.P.x : b.P.x + side * BALCONY.stand, y = back ? b.y0 : col && !onto ? col.y : b.floor;
        const air = b.kind === 'along' ? BALCONY.drop : onto ? BALCONY.hop : 0;
        p.setPosition(x, y - air).setVisible(true);
        p.body.reset(x, y - air);
        p.body.setAllowGravity(true);
        p.setFlipX(b.kind === 'along' ? (back ? b.side < 0 : b.to < 0) : side > 0);
        this.takeoffY = p.y;
        this.lastGroundedAt = -Infinity;
        this.progress.setFlag(b.kind === 'along' ? 'did_round' : 'did_climb');
        if (back && b.taken) this.scareContact(b.taken.x0 + this.world.data.outside.unit / 2, 'balcony');
    },

    // With the parasol, ↓ and Space on a balcony away from its partitions: a hop out over its rail. Out there she is in
    // front of the ship's side all the way down, past the balconies and the boat walkway under her, to the promenade.
    overBalconyRail() {
        const p = this.player;
        if (!this.progress.knows('parasol') || this.world.carry || this.holding) return false;
        if (!this.world.balconyFloor(p.x, p.y)) return false;
        if (this.crawling) this.setCrawl(false);
        this.overRail = true;
        this.outRail = true;
        this.overRailAt = this.time.now;
        p.setDepth(this.DEPTH.fx - 0.5);
        p.body.velocity.y = -PLAYER.jumpVelocity * 0.6;
        this.jumpBufferedAt = -Infinity;
        this.lastGroundedAt = -Infinity;
        sfx.jump();
        return true;
    },

    // The moves' hints, each once, the first time she can use it: at a partition she can go round; and, once she has
    // gone round one, at a partition with a way up or down.
    balconyHints() {
        const P = this.progress;
        if (this.route !== OUT || !P.knows('socks') || this.world.carry || this.holding) return;
        const round = P.flagSet('hint_round'), climb = P.flagSet('hint_climb');
        if (round && climb) return;
        const at = this.partitionAt();
        if (!at || !(this.player.body.blocked.down || this.player.body.touching.down)) return;
        const pad = this.controls.device === 'pad' ? '.pad' : '';
        const { P: part, side } = at;
        if (!round) {
            if (!(side < 0 ? part.aft : part.fore) || this.balconyTaken(part, -side, part.y)) return;
            P.setFlag('hint_round');
            this.hintRoundAt = this.time.now;
            this.world.say(t(`hint.round${pad}`), BALCONY.hintMs, { kind: 'plate' });
        } else if (P.flagSet('did_round') && this.time.now - (this.hintRoundAt ?? -Infinity) > BALCONY.hintGap
            && (side < 0 ? part.upFore || part.downFore : part.upAft || part.downAft)) {
            P.setFlag('hint_climb');
            this.world.say(t(`hint.climb${pad}`), BALCONY.hintMs, { kind: 'plate' });
        }
    },
};
