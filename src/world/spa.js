// The spa's massage (deck 11, region 9; the user, 2026-11-22), mixed into the Story. The masseur (`amb_masseur`) gives
// his guest (`amb_massage_guest`, lying face down on the second table in a towel wrap) the whole massage, round and round
// (`MASSAGE.rounds`: behind the table facing us, his stretch at her feet, in front of it his back to us, his stretch at her
// head). E at the table: at once he goes behind the table's middle (round its head) and stands, the table, the guest and
// Bumbusik in front of him, while the guest gets up and goes into the sauna (its glass door opened on her way, she in front of it) and sits on
// its bench facing us; Bumbusik climbs on and lies face down and gets the same massage, once round; she gets up, to him
// at the table's head, and, the first time, he tosses her Bumbot's massage gun (6, `MASSAGE.keep`). Then the guest
// gets up, comes back and lies down on the table again, and he goes on with her (the user's). Again any time, nothing
// given. E at the other, empty table: he comes over at once and gives her the same there, the guest lying on hers and
// waiting; then he goes back to her.
// Their clips: tools/cast.py (`masseur`, `massage_guest`); hers: `massage-lie` in her sheet, backwards to get up.
// (Every step here can be cut short: `run.stop`, set by E, ends the guest's massage where it is.)

import { MASSAGE } from '../config.js';

export const spa = {
    setupSpa() {
        const m = this.who('amb_masseur'), g = this.who('amb_massage_guest');
        if (!m || !g) return;
        m.home = m.x;
        this.spaState = { busy: false };
        this.spaHome(m, g);
    },

    // The guest's table: its middle and half its length (its picture in the ship's art, at the masseur's spot).
    spaTable() {
        const m = this.who('amb_masseur');
        return this.spaTables().find(t => Math.abs(t.x - m.home) < 6) ?? { x: m.home, half: 32 };
    },

    // Both of the spa's massage tables, the empty one and the guest's (their pictures, on the guest's deck, within 6 m).
    spaTables() {
        if (!this.spaTablePics) {
            const s = this.scene, m = this.who('amb_masseur');
            this.spaTablePics = s.worldLayer.list.filter(o => o.texture?.key === 'shipart' && String(o.frame?.name).startsWith('massage-table')
                && Math.abs(o.y - m.y) < 4 && Math.abs(o.x - m.home) < 6 * 48).map(o => ({ x: o.x, half: o.displayWidth / 2 }));
        }
        return this.spaTablePics;
    },

    // His depth: behind the table (under the ship's furniture, `decor + 0.1`, and whoever lies on it) or in front of it:
    // over the table and the guest, and over Bumbusik while she lies on the table (he is nearer us), but under her while
    // she stands or walks by (the user, 2026-11-22: "the player has to obscure him").
    spaDepth(m, behind) {
        const D = this.scene.DEPTH;
        m.sprite.setDepth(behind ? D.decor + 0.09 : this.spaHerOn ? D.player + 0.03 : D.decor + 0.13);
        m.behind = behind;
    },

    // His picture `MASSAGE.lower` px lower in profile and with his back to us; facing us behind the table, as drawn (the user).
    spaLow(p, low) {
        if (p.who !== 'masseur') return;
        p.sprite.y = p.y - (p.dy ?? 0) + (low ? MASSAGE.lower : 0);
    },

    // As it is when she comes: the guest lying on the table, he giving her the massage round and round.
    spaHome(m, g) {
        const { x, half } = this.spaTable();
        if (this.spaRun) this.spaRun.stop = true;
        g.gone = false;
        g.x = x;
        g.dir = 1;
        g.state = 'acting';
        g.sprite.anims.stop();
        g.sprite.setFrame(g.meta.anims.up[0]);
        g.sprite.setDepth(this.scene.DEPTH.decor + 0.12);
        this.people.place(g);
        m.x = x;
        m.dir = 1;
        m.idle = null;
        m.state = 'acting';
        m.spaEnd = null;
        this.spaDepth(m, true);
        this.people.place(m);
        this.world.refresh();
        this.spaLoop(m);
    },

    // His massage of the guest, round and round, from where he is.
    spaLoop(m) {
        const { x, half } = this.spaTable();
        const left = x - half - MASSAGE.end, right = x + half + MASSAGE.end;
        m.spaEnd = null;
        const run = this.spaRun = { stop: false };
        run.done = (async () => {
            while (!run.stop) await this.spaRounds(run, MASSAGE.rounds, { head: left, foot: right }, x);
        })();
    },

    // E at a table: her massage. At the guest's, the guest goes to the sauna meanwhile; at the empty one, the guest lies
    // on hers and waits, and he comes over (the user, 2026-11-22: "I want us to be able to use the other table as well").
    massage() {
        const st = this.spaState, m = this.who('amb_masseur'), g = this.who('amb_massage_guest');
        if (!st || st.busy || !m?.on) return false;
        const s = this.scene, w = this.world, her = s.player;
        if (s.route !== 'inside' || Math.abs(her.y - m.y) > 8 || w.carry) return false;
        const t = this.spaTables().find(t => Math.abs(her.x - t.x) <= MASSAGE.reach);
        if (!t) return false;
        st.busy = true;
        const home = this.spaTable(), guestTable = Math.abs(t.x - home.x) < 1, X = t.x;
        // (A table's head is its left end, the pillow's; its foot the right.)
        const head = X - t.half - MASSAGE.end, foot = X + t.half + MASSAGE.end;
        const homeHead = home.x - home.half - MASSAGE.end;
        w.cut(async () => {
            her.setFlipX(X < her.x);
            // 1. At once: he stops where he is and goes behind her table's middle (round its head if he is in front), and
            // at the guest's table the guest gets up and goes to the sauna's bench.
            if (this.spaRun) {
                this.spaRun.stop = true;
                this.spaRun = null;
            }
            const run = { stop: false };
            const placed = (async () => {
                await this.spaRoundTo(run, m, head, X, true);
                this.spaStand(m);
            })();
            // 2. She lies down on the table (at the guest's, once the guest is up).
            if (guestTable) await this.spaGuestUp(g, X);
            await this.spaWalkHer(X);
            await this.spaHerClip(1);
            await placed;
            // 3. Her massage, once round (`MASSAGE.rounds`): behind the table, a stretch at her feet, in front his back to
            // us, a stretch at her head.
            m.spaEnd = null;
            await this.spaRounds(run, MASSAGE.rounds, { head, foot }, X);
            // 4. She gets up, to him at the table's head.
            this.spaFace(m, X);
            await this.spaHerClip(-1);
            // 5. The first time, his gift: Bumbot's massage gun, tossed to her.
            her.setFlipX(m.x < X);
            s.pose('stand');
            if (!w.save.keeps.includes(MASSAGE.keep)) {
                this.spaLow(m, true);
                await w.tossOver(m, 'thing:massage-gun', null, null, MASSAGE.toss);
                w.giveKeep(MASSAGE.keep, her.x, her.y - 40, { quiet: true });
            }
            m.state = 'acting';
            m.sprite.anims.stop();
            m.sprite.setFrame(m.meta.stand);
            this.spaLow(m, true);
            // 6. (She is free.) He goes behind the guest's table again, round its head; the guest comes back from the sauna
            // and lies down (or lay there waiting), and he goes on with her.
            (async () => {
                const back = { stop: false };
                await this.spaRoundTo(back, m, homeHead, home.x, true);
                this.spaStand(m);
                if (guestTable) await this.spaGuestBack(g, home.x);
                this.spaLoop(m);
                st.busy = false;
            })();
        });
        return true;
    },

    // The rounds in turn: a massage from behind the table ('front') or in front of it ('back') at its middle, or a stretch
    // at one of its ends ('head', 'foot', from `ends`), going round the table's end where he must change sides.
    async spaRounds(run, rounds, ends, X) {
        const m = this.who('amb_masseur');
        for (const r of rounds) {
            if (run.stop) return;
            if (r === 'front' || r === 'back') {
                const behind = r === 'front';
                await this.spaRoundTo(run, m, m.spaEnd ?? ends.head, X, behind);
                if (run.stop) return;
                await this.spaRub(run, m, behind ? 'mf' : 'mb');
            } else {
                m.spaEnd = ends[r];
                await this.spaWalk(run, m, m.spaEnd, m.behind);
                if (run.stop) return;
                this.spaFace(m, X);
                await this.spaPlay(run, m, 'stretch-slow');
            }
        }
    },

    // He turns to face x.
    spaFace(p, x) {
        p.dir = x < p.x ? -1 : 1;
        this.people.place(p);
    },

    // Standing still, facing us.
    spaStand(m) {
        m.sprite.anims.stop();
        m.dir = 1;
        this.people.place(m);
        m.sprite.setFrame(m.meta.front ?? m.meta.stand);
        this.spaLow(m, false);
    },

    // A clip of his (or hers) played `times` over, ended early by `run.stop`.
    async spaPlay(run, p, clip, times = 1) {
        if (run.stop || !p.meta.anims[clip]) return;
        this.people.anim(p, clip, { loop: false });
        p.sprite.anims.play({ key: `people-${p.who}-${clip}`, repeat: times - 1 });
        this.spaLow(p, !clip.startsWith('mf-'));
        while (p.sprite.anims.isPlaying && !run.stop) await this.world.wait(16);
    },

    // He walks to x at `speed` px a second, behind the table or in front of it; ended early by `run.stop`.
    async spaWalk(run, p, x, behind, speed = MASSAGE.walk) {
        if (run.stop) return;
        this.spaDepth(p, behind);
        if (Math.abs(x - p.x) < 0.5) return;
        const s = this.scene;
        p.dir = x < p.x ? -1 : 1;
        this.people.anim(p, 'walk');
        this.spaLow(p, true);
        let last = s.time.now;
        while (!run.stop && Math.abs(x - p.x) >= 0.5) {
            await this.world.wait(16);
            // (Cut short: whatever comes next has him now; this walk neither moves him nor sets his picture again. It
            // had stopped his next walk's clip, and he slid over in his standing picture: the user, 2026-11-22.)
            if (run.stop) return;
            const now = s.time.now, step = speed * (now - last) / 1000;
            last = now;
            p.x = Math.abs(x - p.x) <= step ? x : p.x + p.dir * step;
            this.people.place(p);
        }
        p.sprite.anims.stop();
        p.sprite.setFrame(p.meta.stand);
        this.people.place(p);
    },

    // To the table's middle on one side or the other: round its end first if he is on the wrong side.
    async spaRoundTo(run, m, end, X, behind) {
        if (m.behind !== behind) {
            await this.spaWalk(run, m, end, m.behind);
            if (run.stop) return;
            this.spaDepth(m, behind);
        }
        await this.spaWalk(run, m, X, behind);
    },

    // A round of massage: his bow, the kneading, his straightening (`mf`: behind the table, facing us; `mb`: his back to us).
    async spaRub(run, m, set) {
        m.dir = 1;
        this.people.place(m);
        await this.spaPlay(run, m, `${set}-bow`);
        await this.spaPlay(run, m, `${set}-knead`, MASSAGE.knead);
        await this.spaPlay(run, m, `${set}-rise`);
    },

    // The guest gets up off the table, stands, and goes into the sauna through its glass door (in front of its open leaf),
    // turns to us and sits down on its bench (`MASSAGE.bench`, m), there till Bumbusik's massage is over.
    async spaGuestUp(g, X) {
        const s = this.scene, run = { stop: false };
        await this.spaPlay(run, g, 'up');
        g.x = X + MASSAGE.guestUp;
        g.dir = 1;
        g.sprite.setDepth(s.DEPTH.props + 0.05);
        this.people.place(g);
        // (Off she goes: Bumbusik lies down meanwhile.)
        g.going = (async () => {
            await this.spaGuestWalk(g, this.spaBenchX());
            g.dir = 1;
            this.people.place(g);
            g.sprite.setFrame(g.meta.front ?? g.meta.stand);
            await this.world.wait(250);
            await this.spaPlay(run, g, 'sit');
        })();
    },

    // ... and back: up from the bench, out of the sauna, to the table, and down onto it as she got up, backwards.
    async spaGuestBack(g, X) {
        const s = this.scene, run = { stop: false };
        await g.going;
        await this.spaPlay(run, g, 'sit-up');
        g.sprite.setFrame(g.meta.stand);
        await this.world.wait(200);
        await this.spaGuestWalk(g, X + MASSAGE.guestUp);
        // (Her clips on the table are drawn round its middle: standing, she is `guestUp` px right of it.)
        g.x = X;
        g.dir = 1;
        this.people.place(g);
        g.sprite.setDepth(s.DEPTH.decor + 0.12);
        await this.spaPlay(run, g, 'lie');
        g.sprite.anims.stop();
        g.sprite.setFrame(g.meta.anims.up[0]);
    },

    // The bench she sits on in the sauna: its seat's middle, `MASSAGE.bench` px aft of the table's.
    spaBenchX() {
        return this.spaTable().x + MASSAGE.bench;
    },

    // The guest walks to x at her pace, a glass door on the way opened and held while she goes through.
    async spaGuestWalk(g, x) {
        const s = this.scene;
        g.dir = x < g.x ? -1 : 1;
        this.people.anim(g, 'walk');
        this.people.place(g);
        let last = s.time.now;
        while (Math.abs(x - g.x) >= 0.5) {
            await this.world.wait(16);
            const b = s.doorAhead(g.x, g.dir, g.y, 6, 4);
            if (b && !g.through) {
                g.through = b;
                s.holdDoor(b, g);
            }
            if (g.through && (g.x - g.through.x) * g.dir > g.through.w / 2 + 14) {
                s.letGoDoor(g.through, g);
                g.through = null;
            }
            const now = s.time.now, step = MASSAGE.guestWalk * (now - last) / 1000;
            last = now;
            g.x = Math.abs(x - g.x) <= step ? x : g.x + g.dir * step;
            this.people.place(g);
        }
        if (g.through) {
            const b = g.through;
            g.through = null;
            this.world.wait(400).then(() => s.letGoDoor(b, g));
        }
        g.sprite.anims.stop();
        g.sprite.setFrame(g.meta.stand);
    },

    // She walks to the table's middle on its near side.
    async spaWalkHer(X) {
        const s = this.scene, her = s.player, w = this.world;
        if (Math.abs(her.x - X) > 1) {
            her.setFlipX(X < her.x);
            s.pose('run', 0.6);
            await w.tween({ targets: her, x: X, duration: Math.abs(X - her.x) / 70 * 1000 });
        }
        s.pose('stand');
        her.setFlipX(false);
    },

    // Her climb onto the table and lying down (dir 1), or getting up off it (dir -1): her sheet's frames in turn.
    async spaHerClip(dir) {
        const s = this.scene, her = s.player, w = this.world;
        const frames = s.cache.json.get('her-meta').anims['massage-lie'];
        her.anims.stop();
        her.setFlipX(false);
        her.body.enable = false;
        // (On the table from her first frame of climbing on to her last of getting off: he is over her in front of it.)
        const m = this.who('amb_masseur');
        this.spaHerOn = true;
        this.spaDepth(m, m.behind);
        const list = dir > 0 ? frames : [...frames].reverse();
        for (const f of list) {
            her.setTexture('her', f);
            await w.wait(MASSAGE.climbMs);
        }
        if (dir < 0) {
            her.body.enable = true;
            s.pose('stand');
            this.spaHerOn = false;
            this.spaDepth(m, m.behind);
        }
    },

};
