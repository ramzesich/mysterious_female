// The story's own moments (GAME_DESIGN.md §6.1.3, docs/population.md §6): what the people do when
// she brings them what they asked for, what Bumbot's beats change, the glimpses. The world asks this
// first when she presses E, each frame, and when a flag is set or a lock stops her. One part per
// region, in the order of docs/build-plan.md.

import { sfx } from '../sfx.js';

const M = 48;

export class Story {
    constructor(world) {
        this.world = world;
        this.scene = world.scene;
    }

    get P() { return this.world.progress; }
    get people() { return this.world.people; }
    who(id) { return this.world.people.byId[id]; }

    // Her near someone, on their floor.
    near(id, reach = 40) {
        const p = this.who(id), her = this.scene.player;
        return p && p.on && this.scene.route === p.route && Math.abs(her.x - p.x) < reach && Math.abs(her.y - p.y) < 8 ? p : null;
    }

    // Once everything is built: hooks on Bumbot's beats, the scenes that wait for her.
    setup() {
        const s = this.scene;
        const cat = flag => s.cats.find(c => c.flag === flag);
        const bb1 = cat('bb1');
        if (bb1) {
            // Near-catch 1 (population §6.1): the scream that becomes her battle cry; the fruit bowl goes over.
            bb1.onReach = () => { s.bubbleUntil = s.time.now + 1700; sfx.dash(); };
            bb1.onLeap = () => this.world.topple('prop_bowl_7s');
        }
        const bb2 = cat('bb2');
        if (bb2) bb2.onAway = () => this.ropeIntoDoor();
        // The Library's aft door, once he has knocked the rope stand into it: ajar for good.
        if (this.P.has('bb2')) this.leaveAjar();
        this.setupLift();
        this.setupStage();
    }

    // E. True if something here took it.
    interact() {
        return this.officer() || this.pills();
    }

    update(dt, time) {
        this.glimpseStairs(time);
        this.glimpseLift(time);
        this.flash(time);
        this.rivalOnPromenade(dt, time);
        this.glimpseWindow(time);
        this.shush(time);
        this.sneezes(time);
    }

    onFlag(name) {
        if (name === 'bb3') this.showTrap();
    }

    // A lock stopped her (a block's id): whoever keeps it reacts.
    onBlocked(id) {
        if (id === 'search') {
            const rival = this.who('riv_rope');
            if (rival?.on && rival.state !== 'acting') this.people.play(rival, 'shake');
        }
    }

    // --- Region 1 -----------------------------------------------------------------------------

    // The gangway officer (population: `npc_officer`, `scn_card_deck`): his lunch, then his card.
    officer() {
        const o = this.near('npc_officer', 44);
        if (!o || this.P.save.cards.includes('deck')) return false;
        const w = this.world, s = this.scene;
        if (w.carry?.kind !== 'lunch') {
            // Nothing for him yet: he shows what he wants again.
            w.nudge(o);
            return true;
        }
        w.cut(async () => {
            s.player.setFlipX(o.x < s.player.x);
            await w.wait(250);
            w.carryBox.give();
            const plate = w.prop(o.x + o.dir * 13, o.y - 30, 'tray', 'load-cloche');
            await this.people.play(o, 'eat', { times: 3 });
            plate.forEach(i => i.destroy());
            await w.wait(200);
            // His card: she is doing his rounds now.
            await w.handOver(o, 'key-card', () => this.P.open('cards', 'deck'));
            this.P.setFlag('lunch');
        });
        return true;
    }

    // Bumbot's tail up the forward stairs, right past the security officer at his rope, who doesn't
    // notice (population §6.1, moved to where she can see it: the first time she comes by after the
    // Seven Seas).
    glimpseStairs(time) {
        const s = this.scene, P = this.P;
        if (P.has('glimpse1') || !P.has('bb1') || s.mode !== 'play' || s.route !== 'inside') return;
        const f = s.flights.find(g => g.name === 'stairs-forward-5-6');
        const her = s.player;
        if (!f || Math.abs(her.y - f.bottom.y) > 4 || Math.abs(her.x - f.bottom.x) > 5.5 * M) return;
        P.setFlag('glimpse1');
        const cat = s.add.sprite(f.bottom.x, f.bottom.y, 'bumbot').setOrigin(0.5, 1).setDepth(s.DEPTH.playerBehind);
        cat.play('bumbot-run').setFlipX(f.top.x < f.bottom.x);
        s.worldLayer.add(cat);
        sfx.mrrp();
        s.tweens.addCounter({
            from: 0, to: 1, duration: 1500,
            onUpdate: tw => {
                const q = s.stairPoint(f, tw.getValue());
                cat.setPosition(q.x, q.y);
            },
            onComplete: () => cat.destroy(),
        });
    }

    // --- Region 2 -----------------------------------------------------------------------------

    // Near-catch 2 (population §6.3): bolting out of the Library he knocks the "QUIET PLEASE" rope
    // stand into its aft door, which swings ajar and stays so. (The flag opens the door; the rope
    // lies where it fell: a prop that comes with the flag.)
    ropeIntoDoor() {
        const s = this.scene;
        const rope = this.P.blockDrawings.filter(d => d.id === 'flag:bb2').flatMap(d => d.items);
        sfx.smash();
        s.tweens.add({ targets: rope, angle: 90, x: '+=14', duration: 220, ease: 'Quad.easeIn' });
        this.leaveAjar();
    }

    leaveAjar() {
        const s = this.scene;
        const door = s.bulkheads.find(b => b.id === 'part-door-6-194');
        if (!door) return;
        door.ajar = true;
        s.setBulkheadOpen(door, true);
    }

    // The librarian (population: `npc_librarian`): a finger to her lips when she runs past her desk.
    shush(time) {
        const l = this.who('npc_librarian'), s = this.scene, her = s.player;
        if (!l?.on || l.state === 'acting' || s.mode !== 'play' || s.route !== 'inside' || time < (this.shushAt ?? 0)) return;
        if (Math.abs(her.y - l.y) > 8 || Math.abs(her.x - l.x) > 3 * M) return;
        if (Math.abs(her.body.velocity.x) < 120 && !s.isDashing()) return;
        this.shushAt = time + 6000;
        l.dir = her.x < l.x ? -1 : 1;
        this.people.place(l);
        this.people.play(l, 'shush', { hold: 300 }).then(() => {
            l.dir = -1;
            this.people.place(l);
        });
    }

    // The glass elevator's glimpse (population §6.2): until she has seen it, the car waits at deck 6
    // with Bumbot sitting in it, its doors open; as she comes near they close and it rises to deck
    // 9, where she can't go yet, and comes back empty. Her input stays free.
    setupLift() {
        const s = this.scene;
        const lift = s.lifts.find(l => l.glass);
        if (!lift || this.P.has('bb_lift') || this.P.openAll) return;      // (?cards=all: the elevator is just an elevator)
        const at = lift.floors.findIndex(f => f.deck === 6);
        if (at < 0) return;
        lift.busy = true;
        lift.at = at;
        lift.carY = lift.floors[at].y;
        s.setLeaves(lift.leaves, lift.carY, 1);
        s.placeCar(lift);
        const cat = s.add.sprite(lift.x, lift.carY, 'bumbot').setOrigin(0.5, 1).setDepth(s.DEPTH.inGlassCar);
        cat.play('bumbot-sit');
        s.worldLayer.add(cat);
        this.liftScene = { lift, cat, state: 'waiting' };
    }

    glimpseLift() {
        const g = this.liftScene, s = this.scene;
        if (!g || g.state !== 'waiting' || s.route !== 'inside') return;
        const her = s.player, lift = g.lift;
        if (Math.abs(her.y - lift.carY) > 6 || Math.abs(her.x - lift.x) > 4 * M) return;
        g.state = 'going';
        const top = lift.floors.find(f => f.deck === 9).y, home = lift.carY;
        const ride = (to, ms, done) => s.tweens.addCounter({
            from: lift.carY, to, duration: ms, ease: 'Sine.easeInOut',
            onUpdate: tw => {
                lift.carY = tw.getValue();
                s.placeCar(lift);
                g.cat?.setY(lift.carY);
            },
            onComplete: done,
        });
        // The doors slide shut on him, and up he goes.
        s.tweens.addCounter({
            from: 1, to: 0, duration: 320,
            onUpdate: tw => s.setLeaves(lift.leaves, lift.carY, tw.getValue()),
            onComplete: () => {
                sfx.mrrp();
                ride(top, 2600, () => {
                    g.cat.destroy();
                    g.cat = null;
                    s.time.delayedCall(900, () => ride(home, 2600, () => {
                        lift.busy = false;
                        g.state = 'done';
                        this.P.setFlag('bb_lift');
                    }));
                });
            },
        });
    }

    // The Photo Studio's flash (population: `haz_flash`): every few seconds the softboxes glow, then
    // flash; caught in it she stops and poses for a second, the screen whites. No scare: a gag.
    flash(time) {
        const s = this.scene, f = this.world.data.flash;
        if (!f) return;
        const her = s.player;
        if (Math.abs(her.x - (f.x0 + f.x1) / 2) > 700 || Math.abs(her.y - f.y) > 200) return;
        this.flashAt ??= time + 2500;
        if (!this.flashGlow) {
            this.flashGlow = s.add.rectangle((f.x0 + f.x1) / 2, f.y - 60, f.x1 - f.x0, 120, 0xfff1c9, 0).setDepth(s.DEPTH.decor + 0.3);
            this.world.add([this.flashGlow]);
        }
        const left = this.flashAt - time;
        // The tell: the lamps warm up.
        this.flashGlow.setFillStyle(0xfff1c9, left < 700 && left > 0 ? 0.25 * (1 - left / 700) : 0);
        if (left > 0) return;
        this.flashAt = time + f.period * 1000;
        const white = s.add.rectangle((f.x0 + f.x1) / 2, f.y - 64, f.x1 - f.x0 + 60, 128, 0xffffff, 0.95).setDepth(s.DEPTH.fx + 2);
        this.world.add([white]);
        s.tweens.add({ targets: white, alpha: 0, duration: 500, onComplete: () => white.destroy() });
        const caught = s.mode === 'play' && s.route === 'inside' && Math.abs(her.y - f.y) < 4 && her.x > f.x0 && her.x < f.x1 && !this.world.carry;
        if (!caught) return;
        s.cameras.main.flash(300, 255, 255, 255);
        this.world.cut(async () => {
            if (s.anims.exists('her-pose')) her.anims.play('her-pose');
            else s.pose('front');
            await this.world.wait(1000);
            s.pose('stand');
        });
    }

    // The rival on the promenade, peering under the boats with his net (population: `riv_prom`): a
    // glimpse. When she is near enough to see him well he hurries off, away from her, faster than
    // she runs: in at the first promenade door on his way, or out of sight along the deck.
    rivalOnPromenade(dt, time) {
        const r = this.who('riv_prom'), s = this.scene;
        if (!r || !r.on || this.P.has('riv_prom') || r.state === 'gone') return;
        const her = s.player;
        if (r.state !== 'fleeing') {
            if (s.route !== r.route || Math.abs(her.y - r.y) > 8 || Math.abs(her.x - r.x) > 4.2 * M) return;
            r.state = 'fleeing';
            r.dir = her.x < r.x ? 1 : -1;
            this.people.anim(r, 'walk', { speed: 1.9 });
            this.fleeFrom = r.x;
        }
        r.x += r.dir * 185 * dt;
        this.people.place(r);
        const run = Math.abs(r.x - this.fleeFrom);
        const door = (s.promenade?.doors ?? []).some(d => Math.abs(d - r.x) < 6) && run > 40;
        if (door || run > 9 * M) {
            r.state = 'gone';
            if (door) sfx.door();
            r.items.forEach(i => s.tweens.add({ targets: i, alpha: 0, duration: door ? 160 : 300 }));
            s.time.delayedCall(320, () => this.P.setFlag('riv_prom'));
        }
    }

    // A black shape in a promenade porthole (population: `bb_glimpse_window`): two ears come up
    // behind the glass as she passes, and duck.
    glimpseWindow() {
        const s = this.scene, g = this.world.data.glimpseWindow;
        if (!g || this.P.has('glimpse_window') || s.route !== 'promenade' || s.mode !== 'play') return;
        const her = s.player;
        if (Math.abs(her.y - g.floor) > 4 || Math.abs(her.x - g.x) > 3.5 * M) return;
        this.P.setFlag('glimpse_window');
        const ears = s.add.graphics().setDepth(s.DEPTH.exterior + 0.09);
        ears.fillStyle(0x14121a, 1).fillEllipse(0, 4, 14, 10).fillTriangle(-6, 2, -5, -6, -1, 0).fillTriangle(6, 2, 5, -6, 1, 0);
        ears.fillStyle(0xb9e04c, 1).fillRect(-4, 2, 2, 1).fillRect(2, 2, 2, 1);
        ears.setPosition(g.x, g.y + 14);
        this.world.add([ears]);
        // (Clipped to the porthole's glass by staying low in it.)
        s.tweens.add({ targets: ears, y: g.y + 3, duration: 380, ease: 'Quad.easeOut', hold: 900, yoyo: true, onComplete: () => ears.destroy() });
        sfx.mrrp();
    }

    // --- Region 3 -----------------------------------------------------------------------------

    // The stage (population §6.4, as built: `world.data.stage`): the trap door's seam, the fly rope,
    // and near-catch 3's own way of going: the rival bursts in, trips, and goes down the trap door;
    // Bumbot rides the fly rope up into the flies.
    setupStage() {
        const s = this.scene, st = this.world.data.stage, D = s.DEPTH;
        if (!st) return;
        // The trap door: a seam in the stage's front until it has given way, then a hole, its lid up.
        this.trapSeam = s.add.graphics().setDepth(D.decor + 0.3);
        this.trapSeam.lineStyle(1, 0x3b2a20, 1).strokeRect(st.trapX - 12.5, st.floor - 7.5, 25, 7);
        this.trapSeam.fillStyle(0xd9a43b, 1).fillRect(st.trapX - 2, st.floor - 5, 4, 2);
        this.trapHole = s.add.graphics().setDepth(D.decor + 0.3);
        this.trapHole.fillStyle(0x0d0b14, 1).fillRect(st.trapX - 13, st.floor - 8, 26, 8);
        this.trapHole.fillStyle(0x2e222f, 1).fillRect(st.trapX - 13, st.floor - 8, 26, 1);
        this.trapHole.fillStyle(0x3b2a20, 1).fillRect(st.trapX - 17, st.floor - 30, 4, 30);
        this.trapHole.fillStyle(0x74503a, 1).fillRect(st.trapX - 16, st.floor - 29, 2, 28);
        // The fly rope, a loop at its end: he rides it up, and it stays hauled up after.
        this.rope = s.add.graphics().setDepth(D.props + 0.02);
        this.world.add([this.trapSeam, this.trapHole, this.rope]);
        this.drawRope(this.P.has('bb3') ? st.top + 34 : st.floor - 40);
        this.showTrap();
        const bb3 = s.cats.find(c => c.flag === 'bb3');
        if (bb3) {
            bb3.before = () => this.rivalTrips();
            bb3.flee = (sprite, done) => this.upTheRope(sprite, done);
        }
    }

    showTrap() {
        const open = this.P.has('bb3') || this.trapOpen;
        this.trapSeam?.setVisible(!open);
        this.trapHole?.setVisible(!!open);
    }

    drawRope(endY) {
        const st = this.world.data.stage, g = this.rope.clear();
        g.fillStyle(0x7a4528, 1).fillRect(st.ropeX - 1, st.top + 12, 2, endY - st.top - 12);
        g.fillStyle(0xab947a, 1);
        for (let y = st.top + 14; y < endY; y += 4) g.fillRect(st.ropeX - 1, y, 1, 2);
        g.lineStyle(2, 0x7a4528, 1).strokeEllipse(st.ropeX, endY + 5, 8, 10);
        this.ropeEnd = endY;
    }

    // The rival runs in through the curtain behind her with his net, trips on the microphone's
    // cable, and goes head first onto the trap door, which gives way under him.
    async rivalTrips() {
        const s = this.scene, w = this.world, st = w.data.stage;
        const sm = this.who('npc_stagemanager');
        if (sm?.on) this.people.play(sm, 'flap', { times: 2 });
        const r = this.people.add({ id: 'riv_stage', who: 'rival', x: st.wingX, y: st.floor, route: 'inside', face: 1 });
        if (!r) return;
        r.on = true;
        const place = () => this.people.place(r);
        this.people.anim(r, 'walk', { speed: 2.4 });
        await w.tween({ targets: r, x: st.cableX, duration: (Math.abs(st.cableX - st.wingX) / 230) * 1000, onUpdate: place });
        this.people.play(r, 'trip');
        sfx.dash();
        await w.tween({ targets: r, x: st.trapX - 4, duration: 440, ease: 'Quad.easeOut', onUpdate: place });
        this.trapOpen = true;
        this.showTrap();
        sfx.smash();
        s.cameras.main.shake(200, 0.004);
        await w.tween({ targets: r.sprite, y: st.floor + 56, alpha: 0, duration: 340, ease: 'Quad.easeIn' });
        r.gone = true;
        r.items.forEach(i => i.setVisible(false));
        // Flour comes up out of the hole: he has found the galley's sacks.
        for (let i = 0; i < 12; i++) {
            const dot = s.add.image(st.trapX + Phaser.Math.Between(-9, 9), st.floor - 4, 'dot').setTint(0xf3ecdd).setDepth(s.DEPTH.fx).setScale(2);
            w.add([dot]);
            s.tweens.add({ targets: dot, y: dot.y - Phaser.Math.Between(16, 40), x: dot.x + Phaser.Math.Between(-10, 10), alpha: 0, duration: 700, delay: i * 25, onComplete: () => dot.destroy() });
        }
        await w.wait(420);
    }

    // Bumbot's way out: a leap onto the fly rope's loop, and up with it into the flies.
    upTheRope(sprite, done) {
        const s = this.scene, st = this.world.data.stage;
        sprite.setFlipX(st.ropeX < sprite.x).play('bumbot-jump');
        s.tweens.add({
            targets: sprite, x: st.ropeX, y: st.floor - 30, duration: 240, ease: 'Quad.easeOut',
            onComplete: () => {
                sprite.anims.pause();
                const from = this.ropeEnd, to = st.top + 34;
                s.tweens.addCounter({
                    from: 0, to: 1, duration: 950, ease: 'Sine.easeIn',
                    onUpdate: tw => {
                        const k = tw.getValue();
                        this.drawRope(from + (to - from) * k);
                        sprite.y = this.ropeEnd + 10;
                        sprite.setAlpha(k > 0.8 ? (1 - k) * 5 : 1);
                    },
                    onComplete: () => { sprite.setAlpha(1); done(); },
                });
            },
        });
    }

    // The stage manager (population: `npc_stagemanager`): allergic to the cat on his stage, he
    // sneezes every few seconds until he has his pills.
    sneezes(time) {
        const m = this.who('npc_stagemanager'), s = this.scene;
        if (!m?.on || m.state === 'acting' || this.P.save.cards.includes('ent') || s.mode !== 'play') return;
        if (Math.abs(s.player.x - m.x) > 700 || Math.abs(s.player.y - m.y) > 200) return;
        this.sneezeAt ??= time + 2500;
        if (time < this.sneezeAt) return;
        this.sneezeAt = time + 5000;
        this.people.play(m, 'sneeze');
    }

    // E at him after the beat: his pills from his cabin on deck 4, then his card (`scn_card_ent`).
    pills() {
        const m = this.near('npc_stagemanager', 44);
        if (!m || !this.P.has('bb3') || this.P.save.cards.includes('ent')) return false;
        const w = this.world, s = this.scene, save = this.P.save;
        if (!save.items.includes('pills')) {
            w.nudge(m);
            return true;
        }
        w.cut(async () => {
            const her = s.player;
            her.setFlipX(m.x < her.x);
            m.dir = her.x < m.x ? -1 : 1;
            this.people.place(m);
            await w.wait(250);
            // The bottle crosses from her hands to his.
            const bottle = s.add.image(her.x, her.y - 34, 'icon-pills').setDepth(s.DEPTH.player + 0.05);
            w.add([bottle]);
            sfx.pickup();
            await w.tween({ targets: bottle, x: m.x + m.dir * 10, y: m.y - 36, duration: 380, ease: 'Sine.easeInOut' });
            bottle.destroy();
            save.items = save.items.filter(i => i !== 'pills');
            // One more sneeze, the last; then his card: she is running his errands now.
            await this.people.play(m, 'sneeze');
            await w.wait(250);
            await w.handOver(m, 'key-card', () => this.P.open('cards', 'ent'), 0xff7a7a);
            this.P.setFlag('pills');
        });
        return true;
    }
}
