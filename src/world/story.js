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
        this.setupHousekeeping();
    }

    // E. True if something here took it.
    interact() {
        return this.officer() || this.pills() || this.photo();
    }

    update(dt, time) {
        this.glimpseStairs(time);
        this.glimpseLift(time);
        this.flash(time);
        this.rivalOnPromenade(dt, time);
        this.glimpseWindow(time);
        this.shush(time);
        this.sneezes(time);
        this.updateHousekeeping(dt, time);
    }

    onFlag(name) {
        if (name === 'bb3') this.showTrap();
        if (name === 'cart_free') this.stewardThanks();
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

    // --- Region 4 -----------------------------------------------------------------------------

    // Housekeeping (population §6.5-6.6): near-catch 4's own way out (into the vent), the keys shown
    // at the laundry cart, the steward at his jammed cart, the uniform in the laundry's washer.
    setupHousekeeping() {
        const s = this.scene, w = this.world, L = w.data.linen;
        const bb4 = s.cats.find(c => c.flag === 'bb4');
        if (bb4) bb4.flee = (sprite, done) => this.intoTheVent(sprite, done);
        this.linenCart = w.pushables.find(t => t.id === 'cart_linen');
        if (this.linenCart) {
            this.cartKey = w.glyph(0, this.linenCart.y - 54, 'E');
            this.ventKey = w.glyph(0, this.linenCart.y - L.cartTop - 72, '↓');
        }
        this.stewardCart = w.pushables.find(t => t.id === 'cart_steward');
        // The security officer's uniform, going round in the laundry's third washer while he waits.
        const laundry = w.rooms.laundry;
        if (laundry) {
            const g = s.add.graphics().setDepth(s.DEPTH.exterior + 0.13);
            g.fillStyle(0x323353, 1).fillCircle(0, 0, 5).fillStyle(0x4d65b4, 1).fillRect(-4, -1, 5, 3);
            g.fillStyle(0xf9c22b, 1).fillRect(1, -3, 2, 2).fillStyle(0xffffff, 1).fillRect(-2, 2, 3, 1);
            g.setPosition(laundry.def.x0 + 153, laundry.floor - 18);
            w.add([g]);
            s.tweens.add({ targets: g, angle: 360, duration: 1300, repeat: -1 });
            w.things.push({ id: 'wash_uniform', x: g.x, y: laundry.floor, route: 'laundry', items: [g], after: 'region:4', until: 'region:6' });
        }
    }

    updateHousekeeping(dt, time) {
        const s = this.scene, w = this.world, P = this.P, her = s.player;
        // The steward pulls at his cart from its far end, and goes along with it as she pushes.
        const st = this.who('npc_steward'), cart = this.stewardCart;
        if (st && cart && st.state !== 'acting') {
            const free = P.has('cart_free');
            const x = cart.x + 35;
            if (st.x !== x || st.free !== free) {
                st.x = x;
                st.dir = -1;
                st.free = free;
                st.idle = free ? 'idle' : 'tug';
                this.people.idle(st);
                this.people.place(st);
            }
            // (His card, if the thanks were cut short: loaded after the cart was freed.)
            if (free && !P.save.cards.includes('hk') && s.mode === 'play' && s.route === 'inside'
                && Math.abs(her.y - st.y) < 4 && Math.abs(her.x - st.x) < 110) this.stewardThanks();
        }
        // The keys in the linen room: E at the cart's end once he is in the vent, ↓ on it under the vent.
        const lc = this.linenCart;
        if (lc) {
            const inRoom = s.route === 'linen' && s.mode === 'play';
            const under = lc.x >= lc.max;
            this.cartKey.setVisible(inRoom && P.has('bb4') && !under).setX(lc.x - 22);
            this.ventKey.setVisible(inRoom && under && !P.has('duct')).setX(lc.x);
        }
        // Out of the chute with a towel on her head: it stays a few steps, then slides off.
        if (this.hat) {
            const off = time > this.hatUntil || s.route !== 'laundry';
            this.hat.setPosition(her.x, her.y - 57);
            if (off && !this.hatGoing) {
                this.hatGoing = true;
                const hat = this.hat;
                s.tweens.add({ targets: hat, y: her.y - 2, x: her.x - 12, angle: -80, alpha: 0.9, duration: 420, ease: 'Quad.easeIn',
                    onComplete: () => s.tweens.add({ targets: hat, alpha: 0, duration: 1500, delay: 2500, onComplete: () => hat.destroy() }) });
                this.hat = null;
            }
        }
        this.glimpseBalcony();
    }

    // Bumbot's way out of the linen room: a leap from the towels up to the vent, and he squeezes in.
    intoTheVent(sprite, done) {
        const s = this.scene, w = this.world, L = w.data.linen, floor = w.rooms.linen.floor;
        sprite.setFlipX(L.ventX < sprite.x).play('bumbot-jump');
        s.tweens.add({
            targets: sprite, x: L.ventX - 10, y: floor - L.sill + 1, duration: 320, ease: 'Quad.easeOut',
            onComplete: () => {
                sfx.mrrp();
                s.tweens.add({
                    targets: sprite, x: L.ventX + 6, scaleX: 0.3, scaleY: 0.8, alpha: 0, duration: 460, ease: 'Sine.easeIn',
                    onComplete: () => { sprite.setScale(1).setAlpha(1); done(); },
                });
            },
        });
    }

    // The steward (population: `npc_steward`, `scn_card_hk`): his cart is free; he mops his brow,
    // thanks her, and hands his card over it: she is doing his rounds now.
    stewardThanks() {
        const st = this.who('npc_steward'), w = this.world, s = this.scene;
        if (!st || this.thanking || this.P.save.cards.includes('hk')) return;
        this.thanking = true;
        w.cut(async () => {
            const her = s.player;
            her.setFlipX(st.x < her.x);
            st.idle = 'idle';
            st.dir = her.x < st.x ? -1 : 1;
            this.people.place(st);
            await w.wait(200);
            await this.people.play(st, 'thanks');
            await w.wait(150);
            await w.handOver(st, 'key-card', () => this.P.open('cards', 'hk'), w.cardColour('hk'));
            this.P.setFlag('steward');
            this.thanking = false;
        });
    }

    // The honeymooners (population: `npc_honeymooners`, `scn_photo`): E, and she takes their picture
    // with their camera: the flash, their kiss; the fourth book is their thanks. Then they go in.
    photo() {
        const bride = this.who('npc_bride'), groom = this.who('npc_groom');
        if (this.P.has('photo') || !bride?.on || !groom?.on) return false;
        if (!this.near('npc_bride', 70) && !this.near('npc_groom', 70)) return false;
        const w = this.world, s = this.scene, her = s.player;
        if (w.carry) return false;
        w.cut(async () => {
            const mid = (bride.x + groom.x) / 2, side = her.x < mid ? -1 : 1;
            const face = side < 0 ? 1 : -1;                 // the way she looks at them
            her.setFlipX(face < 0);
            // Their camera crosses to her.
            const cam = s.add.image(bride.x, bride.y - 34, w.icon('camera')).setDepth(s.DEPTH.player + 0.05).setScale(0.7);
            w.add([cam]);
            sfx.pickup();
            await w.tween({ targets: cam, x: her.x + face * 9, y: her.y - 30, duration: 380, ease: 'Sine.easeInOut' });
            // They turn to each other; she raises it.
            bride.dir = 1;
            groom.dir = -1;
            this.people.place(bride);
            this.people.place(groom);
            if (s.anims.exists('her-camera')) her.anims.play('her-camera');
            await w.tween({ targets: cam, x: her.x + face * 10, y: her.y - 49, duration: 300 });
            this.people.play(bride, 'kiss');
            this.people.play(groom, 'kiss');
            await w.wait(620);
            sfx.ding();
            s.cameras.main.flash(260, 255, 255, 255);
            for (let i = 0; i < 3; i++) {
                const heart = s.add.text(mid + (i - 1) * 9, bride.y - 62, '♥', { fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#e83b3b', resolution: 4 })
                    .setOrigin(0.5).setDepth(s.DEPTH.fx);
                w.add([heart]);
                s.tweens.add({ targets: heart, y: heart.y - 20 - i * 5, alpha: 0, duration: 1100, delay: i * 140, onComplete: () => heart.destroy() });
            }
            await w.wait(950);
            // The camera goes back; the book comes.
            s.pose('stand');
            bride.dir = groom.dir = side;
            this.people.place(bride);
            this.people.place(groom);
            await w.tween({ targets: cam, x: bride.x + side * 10, y: bride.y - 34, duration: 380, ease: 'Sine.easeInOut' });
            cam.destroy();
            await w.handOver(bride, '@book-4', () => w.giveBook(4));
            // And in they go, at their door.
            const door = groom.x - 7;
            for (const p of [groom, bride]) {
                p.dir = door < p.x ? -1 : 1;
                this.people.anim(p, 'idle');
                await w.tween({ targets: p, x: door, duration: Math.abs(door - p.x) * 9 + 60, onUpdate: () => this.people.place(p) });
                sfx.door();
                await w.tween({ targets: p.sprite, alpha: 0, scale: 0.92, duration: 220 });
            }
            this.P.setFlag('photo');
            for (const p of [groom, bride]) p.sprite.setAlpha(1).setScale(1);
        });
        return true;
    }

    // The linen room's chute (population: `scn_chute`): a whoosh in the dark, and she lands in the
    // laundry's cart of towels on deck 4, a towel on her head.
    chute() {
        const s = this.scene, w = this.world, to = w.rooms.laundry, L = w.data.linen;
        if (!to || w.carry) return false;
        sfx.whoosh();
        s.travel(L.laundryCartX, to.floor - 60, 'laundry', () => this.outOfTheChute());
        return true;
    }

    outOfTheChute() {
        const s = this.scene, w = this.world, to = w.rooms.laundry, x = w.data.linen.laundryCartX, floor = to.floor;
        const her = s.player;
        her.body.enable = false;
        her.setPosition(x, floor - 92);
        w.cut(async () => {
            her.body.enable = false;
            // The cart's front, over her: she drops in behind it.
            const cover = s.add.image(to.room.x, to.room.y, to.room.texture.key).setOrigin(0).setDepth(s.DEPTH.player + 0.05)
                .setCrop(x - to.def.x0 - 24, 98, 48, 30);
            w.add([cover]);
            s.pose('fall');
            await w.tween({ targets: her, y: floor - 16, duration: 300, ease: 'Quad.easeIn' });
            sfx.smash();
            for (let i = 0; i < 7; i++) {
                const t = s.add.rectangle(x + Phaser.Math.Between(-12, 12), floor - 34, 7, 4, i % 3 ? 0xffffff : 0x8fd3ff).setDepth(s.DEPTH.fx);
                w.add([t]);
                s.tweens.add({ targets: t, x: t.x + Phaser.Math.Between(-22, 22), y: { from: t.y, to: t.y - Phaser.Math.Between(18, 40) }, angle: Phaser.Math.Between(-90, 90),
                    alpha: 0, duration: 700, ease: 'Quad.easeOut', onComplete: () => t.destroy() });
            }
            s.pose('stand');
            this.hat = s.add.image(her.x, her.y - 57, this.hatTexture()).setDepth(s.DEPTH.player + 0.06);
            w.add([this.hat]);
            this.hatGoing = false;
            this.hatUntil = s.time.now + 60000;
            const follow = s.time.addEvent({ delay: 16, loop: true, callback: () => this.hat?.setPosition(her.x, her.y - 57) });
            await w.wait(1100);
            // Out over its side.
            s.pose('rise');
            her.setFlipX(true);
            await w.tween({ targets: her, x: x - 20, y: floor - 46, duration: 220, ease: 'Quad.easeOut' });
            s.pose('fall');
            await w.tween({ targets: her, x: x - 40, y: floor, duration: 220, ease: 'Quad.easeIn' });
            follow.remove();
            cover.destroy();
            her.body.enable = true;
            her.body.reset(x - 40, floor);
            s.takeoffY = floor;
            this.hatUntil = s.time.now + 4500;
            this.P.setFlag('chute');
        });
    }

    hatTexture() {
        const s = this.scene, key = 'towel-hat';
        if (!s.textures.exists(key)) {
            const g = s.make.graphics({ x: 0, y: 0 }, false);
            g.fillStyle(0x9babb2, 1).fillRoundedRect(0, 0, 20, 8, 3).fillRect(0, 5, 5, 9).fillRect(15, 5, 5, 7);
            g.fillStyle(0xffffff, 1).fillRoundedRect(1, 1, 18, 6, 2).fillRect(1, 5, 3, 8).fillRect(16, 5, 3, 6);
            g.fillStyle(0x8fd3ff, 1).fillRect(1, 11, 3, 1).fillRect(16, 9, 3, 1);
            g.generateTexture(key, 20, 14);
            g.destroy();
        }
        return key;
    }

    // From the balcony cabin's balcony (population: `bb_glimpse_balcony`): Bumbot sits on top of the
    // partition at its aft end, washing; he looks at her, and is gone up to the balcony above. Once.
    // (A deck up, as the plan had him, is out of her view.)
    glimpseBalcony() {
        const s = this.scene, g = this.world.data.glimpseBalcony, P = this.P;
        if (!g || P.has('glimpse_balcony') || s.route !== 'promenade' || s.mode !== 'play') return;
        const her = s.player;
        if (Math.abs(her.y - g.y) > 4 || her.x < g.x0 || her.x > g.x1) return;
        P.setFlag('glimpse_balcony');
        const cat = s.add.sprite(g.x1 + 3, g.topY + 1, 'bumbot').setOrigin(0.5, 1).setDepth(s.DEPTH.player + 0.35).setFlipX(true);
        cat.play('bumbot-wash');
        this.world.add([cat]);
        s.time.delayedCall(1500, () => {
            sfx.mrrp();
            cat.play('bumbot-jump');
            s.tweens.add({ targets: cat, x: cat.x + 26, y: g.topY - 70, duration: 420, ease: 'Quad.easeOut',
                onComplete: () => s.tweens.add({ targets: cat, alpha: 0, y: g.topY - 84, duration: 160, onComplete: () => cat.destroy() }) });
        });
    }
}
