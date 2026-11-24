// The story's own moments (GAME_DESIGN.md §6.1.3, docs/population.md §6): what the people do when
// she brings them what they asked for, what Bumbot's beats change, the glimpses. The world asks this
// first when she presses E, each frame, and when a flag is set or a lock stops her. One part per
// region, in the order of docs/build-plan.md.

import { sfx } from '../sfx.js';
import { PLAYER, CHUTE, BUMBOT } from '../config.js';
import { rumble } from '../rumble.js';
import { lido } from './lido.js';
import { outside } from './outside.js';
import { topdeck } from './topdeck.js';
import { bow } from './bow.js';
import { finale } from './finale.js';
import { spa } from './spa.js';

const M = 48;

// The steward and his jammed trolley (region 4): his `tug` is a picture of the two, drawn with the
// trolley's middle this far behind his frame's middle; let go of it, he stands this far from it.
const STEWARD_TUG = 17, STEWARD_FREE = 35;
// Near-catch 4 (the linen room): his body's columns in his asleep frame (of 64), and how near she or the laundry cart comes
// before he is off (the user, 2026-11-23: "she almost touches him, or the cart almost touches him, by a couple of pixels").
const BB4_SPAN = [19, 49], BB4_GAP = 2;
// (On the stage's fly rope: where the rope stands in his clip's frames, px before his middle.)
const ROPE_CAT = { x: 16.5 };
// (His head in that picture, px aft of its middle: his bubble over it.)
const STEWARD_HEAD = 22;
// His card tossed to her, his `toss` clip (frames 0 to 7): in his fingers at his pocket in frames 3
// and 4 (px ahead of his middle, px up from his feet), out of his hand as it swings open in frame 5.
const STEWARD_TOSS = { clip: 'toss', held: { 3: [1, 40], 4: [3, 41] }, release: 5, from: [19, 37] };

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
            bb1.onReach = () => { s.bubbleUntil = s.time.now + 1700; sfx.cry(); };
            bb1.onLeap = () => this.world.topple('prop_bowl_7s');
        }
        const bb2 = cat('bb2');
        if (bb2) bb2.onAway = () => this.ropeIntoDoor();
        // The Library's aft door, once he has knocked the rope stand into it: ajar for good.
        if (this.P.has('bb2')) this.leaveAjar();
        this.setupLift();
        this.setupStage();
        this.setupHousekeeping();
        this.setupLido();
        this.setupOutside();
        this.setupTopdeck();
        this.setupBow();
        this.setupFinale();
        this.setupSpa();
    }

    // E. True if something here took it.
    interact() {
        return this.officer() || this.pills() || this.photo() || this.feedKid() || this.husband()
            || this.oldLadyDrink() || this.engineerCoffee() || this.engineerBook() || this.plannerCake() || this.sushi()
            || this.massage();
    }

    update(dt, time, input) {
        this.updateLido(dt, time, input);
        this.updateOutside(dt, time, input);
        this.updateTopdeck(dt, time, input);
        this.updateBow(dt, time, input);
        this.updateFinale(dt, time, input);
        this.glimpseStairs(time);
        this.glimpseLift(time);
        this.flash(time);
        this.rivalOnPromenade(dt, time);
        this.glimpseWindow(time);
        this.shush(time);
        this.sneezes(time);
        this.updateHousekeeping(dt, time);
        this.party(time);
    }

    onFlag(name) {
        if (name === 'bb3') this.showTrap();
        if (name === 'cart_free') this.stewardThanks();
        if (name === 'duct') this.outOfTheDuct();
        if (name === 'guest') this.guestIn();
        this.refreshLido();
        this.refreshOutside();
        this.refreshTopdeck();
        this.refreshBow();
        this.refreshFinale();
    }

    // A lock stopped her (a block's id): whoever keeps it reacts.
    onBlocked(id) {
        // (The technical ladder's chain: the engineer shows what he would like first.)
        if (id === 'engineer') {
            const e = this.who('npc_engineer');
            if (e?.on) this.world.nudge(e);
        }
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
            for (let i = 0; i < 3; i++) s.time.delayedCall(300 + i * 700, () => sfx.at(o.x, o.y).munch());
            await this.people.play(o, 'eat', { times: 3 });
            plate.forEach(i => i.destroy());
            await w.wait(200);
            // His card: she is doing his rounds now.
            await w.handOver(o, 'key-card', () => this.P.open('cards', 'deck'));
            this.P.setFlag('lunch');
            sfx.done();
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
        sfx.at(f.bottom.x, f.bottom.y).scramble();
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
        sfx.whip();
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

    // Her cry, where the story answers it (docs/plan-three-uses.md §2): the librarian's shush and
    // her rope's sign rattling, Bumbot looking up at his spot, the kid with the water pistol (lido),
    // Bumbot at the tip of the bow (finale).
    heard(cry) {
        const w = this.world, s = this.scene, her = s.player;
        const l = this.who('npc_librarian');
        if (l?.on && w.hears(l.x, l.y)) {
            this.shushAt = 0;
            this.shush(s.time.now, true);
        }
        const rope = this.P.blockDrawings?.find(b => b.id === 'flag:bb2');
        const sign = rope?.items[1];
        if (sign?.visible && w.hears(sign.x, rope.items[0].y)) {
            s.tweens.add({ targets: sign, angle: { from: -8, to: 8 }, duration: 70, yoyo: true, repeat: 4, onComplete: () => sign.setAngle(0) });
            sfx.at(sign.x, sign.y).rattle();
        }
        // Bumbot at one of his spots: ears up, a look at her for half a second; the beat is what it was.
        for (const cat of s.cats) {
            const c = cat.sprite;
            if (cat.gone || cat.hidden || !c.visible || !w.hears(c.x, cat.floor, cat.route)) continue;
            const was = c.flipX;
            c.setFlipX(her.x < c.x);
            s.tweens.add({ targets: c, y: c.y - 2, duration: 90, yoyo: true });
            s.time.delayedCall(500, () => { if (!cat.gone) c.setFlipX(was); });
        }
        this.kidHeard(cry);
        this.tipHeard(cry);
    }

    // A tangerine loose near something the story answers (docs/plan-three-uses.md §2): Bumbot at a
    // spot bats a thrown one back; Bumbot at the tip of the bow backs off (finale); the kid catches
    // and eats it (lido); one over the Spinnaker's keys plays a note (bow). True if it was taken.
    offered(t) {
        return this.catBats(t) || !!this.tipOffered?.(t) || !!this.kidOffered?.(t) || !!this.pianoOffered?.(t)
            || !!this.sushiOffered?.(t);
    }

    // Bumbot at one of his spots, a thrown tangerine coming at him: he bats it straight back to her,
    // sniffs his paw and pulls a face. Not spent; the beat is what it was.
    catBats(t) {
        const s = this.scene, her = s.player;
        if (!t.thrown) return false;
        for (const cat of s.cats) {
            const c = cat.sprite;
            // (Not asleep: he sleeps through it, as he did when his sleep was one still. Fishing, his frames stand
            // `BUMBOT.under` px low: back on his floor for the bat, and down again after.)
            if (cat.gone || cat.hidden || cat.batting || !c.visible || !c.anims.isPlaying || cat.activity === 'asleep'
                || !s.loose.near(t, c.x, c.y, 14, 24, cat.route)) continue;
            cat.batting = true;
            const back = her.x < c.x ? -1 : 1, was = c.anims.currentAnim.key, flip = c.flipX, low = cat.activity === 'fish' ? BUMBOT.under : 0;
            c.y -= low;
            c.setFlipX(back < 0).play('bumbot-bat');
            t.thrown = false;
            t.pickableAt = s.time.now + 300;
            t.img.body.setVelocity(back * 210, -170);
            sfx.at(c.x, c.y).plop();
            s.time.delayedCall(450, () => {
                if (cat.gone) return;
                c.play('bumbot-wash');
                sfx.at(c.x, c.y).mrrp();
            });
            s.time.delayedCall(1700, () => {
                cat.batting = false;
                if (!cat.gone) { c.setFlipX(flip).play(was); c.y += low; }
            });
            return true;
        }
        return false;
    }

    // The librarian (population: `npc_librarian`): a finger to her lips when she runs past her desk,
    // or cries out near it (`cried`).
    shush(time, cried = false) {
        const l = this.who('npc_librarian'), s = this.scene, her = s.player;
        if (!l?.on || l.state === 'acting' || s.mode !== 'play' || s.route !== 'inside' || time < (this.shushAt ?? 0)) return;
        if (!cried && (Math.abs(her.y - l.y) > 8 || Math.abs(her.x - l.x) > 3 * M)) return;
        if (!cried && Math.abs(her.body.velocity.x) < 120 && !s.isLunging()) return;
        this.shushAt = time + 6000;
        l.dir = her.x < l.x ? -1 : 1;
        this.people.place(l);
        sfx.at(l.x, l.y).shush();
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
        sfx.at(lift.x, home).doorSlide();
        s.tweens.addCounter({
            from: 1, to: 0, duration: 320,
            onUpdate: tw => s.setLeaves(lift.leaves, lift.carY, tw.getValue()),
            onComplete: () => {
                sfx.at(lift.x, home).mrrp();
                sfx.at(lift.x, home).liftMove(2.6);
                ride(top, 2600, () => {
                    g.cat.destroy();
                    g.cat = null;
                    s.time.delayedCall(900, () => {
                        sfx.at(lift.x, home).liftMove(2.6);
                        ride(home, 2600, () => {
                            sfx.at(lift.x, home).liftDing();
                            lift.busy = false;
                            g.state = 'done';
                            this.P.setFlag('bb_lift');
                        });
                    });
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
        // (Only while she is inside on its deck: its white, drawn over everything, showed through the ship's
        // side to her on the promenade outside the studio, the user, 2026-11-20, and to her on deck 7 above it.)
        if (s.route !== 'inside' || Math.abs(her.y - f.y) > 72) {
            this.flashGlow?.setFillStyle(0xfff1c9, 0);
            return;
        }
        this.flashAt ??= time + 2500;
        if (!this.flashGlow) {
            this.flashGlow = s.add.rectangle((f.x0 + f.x1) / 2, f.y - 60, f.x1 - f.x0, 120, 0xfff1c9, 0).setDepth(s.DEPTH.decor + 0.3);
            this.world.add([this.flashGlow]);
        }
        const left = this.flashAt - time;
        // The tell: the lamps warm up.
        this.flashGlow.setFillStyle(0xfff1c9, left < 700 && left > 0 ? 0.25 * (1 - left / 700) : 0);
        if (left < 700 && !this.flashCharged) sfx.at((f.x0 + f.x1) / 2, f.y).flashCharge(0.7);
        this.flashCharged = left < 700;
        if (left > 0) return;
        this.flashAt = time + f.period * 1000;
        const white = s.add.rectangle((f.x0 + f.x1) / 2, f.y - 64, f.x1 - f.x0 + 60, 128, 0xffffff, 0.95).setDepth(s.DEPTH.fx + 2);
        this.world.add([white]);
        sfx.at((f.x0 + f.x1) / 2, f.y).shutter();
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
            sfx.at(r.x, r.y).oh();
            this.fleeFrom = r.x;
        }
        r.x += r.dir * 185 * dt;
        this.people.place(r);
        const run = Math.abs(r.x - this.fleeFrom);
        const door = (s.promenade?.doors ?? []).some(d => Math.abs(d - r.x) < 6) && run > 40;
        if (door || run > 9 * M) {
            r.state = 'gone';
            if (door) sfx.at(r.x, r.y).door();
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
        sfx.at(g.x, g.floor).meow();
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
        // (Open: its own picture, the lid up on its hinge, a ladder's top in the opening, its middle the drop's:
        // `assets/source/ship/trapdoor/`, 2026-11-19; it was a black box and a stick, "that black rectangle".)
        this.trapHole = s.add.image(st.trapX - 15, st.floor + 1, 'trapdoor-open').setOrigin(0, 1).setDepth(D.decor + 0.3);
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
        const r = this.people.add({ id: 'riv_stage', who: 'rival', x: st.wingX, y: st.floor, route: 'inside', face: 1, owned: true });
        if (!r) return;
        r.on = true;
        const place = () => this.people.place(r);
        this.people.anim(r, 'walk', { speed: 2.4 });
        await w.tween({ targets: r, x: st.cableX, duration: (Math.abs(st.cableX - st.wingX) / 230) * 1000, onUpdate: place });
        this.people.play(r, 'trip');
        sfx.at(r.x, r.y).yelp();
        await w.tween({ targets: r, x: st.trapX - 4, duration: 440, ease: 'Quad.easeOut', onUpdate: place });
        this.trapOpen = true;
        this.showTrap();
        sfx.at(st.trapX, st.floor).trapdoor();
        s.cameras.main.shake(200, 0.004);
        await w.tween({ targets: r.sprite, y: st.floor + 56, alpha: 0, duration: 340, ease: 'Quad.easeIn' });
        sfx.at(st.trapX, st.floor).flump();
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
        // (On the rope he has a clip of his own since he was made again, 2026-11-24: the catch with his front paws, his
        // hind paws into the loop, a look back down. Made with the rope in its picture and the rope taken out: the
        // game's own is behind him. The rope stands `ROPE_CAT.x` px before his middle in those frames, and they keep
        // `BUMBOT.under` px under his floor.)
        const west = st.ropeX < sprite.x, at = st.ropeX + (west ? 1 : -1) * ROPE_CAT.x;
        sprite.setFlipX(west).play('bumbot-leap');
        s.tweens.add({
            targets: sprite, x: at, y: st.floor - 30, duration: 240, ease: 'Quad.easeOut',
            onComplete: () => {
                sprite.setDepth(this.rope.depth + 0.001).play({ key: 'bumbot-rope', startFrame: 2 });
                sfx.at(st.ropeX, st.floor).whip();
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
        sfx.at(m.x, m.y).sneeze();
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
            const bottle = s.add.image(her.x, her.y - 34, 'things', 'pills-bottle').setDepth(s.DEPTH.player + 0.05);
            w.add([bottle]);
            sfx.give();
            await w.tween({ targets: bottle, x: m.x + m.dir * 10, y: m.y - 36, duration: 380, ease: 'Sine.easeInOut' });
            bottle.destroy();
            save.items = save.items.filter(i => i !== 'pills');
            // One more sneeze, the last; then his card: she is running his errands now.
            sfx.at(m.x, m.y).sneeze();
            await this.people.play(m, 'sneeze');
            await w.wait(250);
            await w.handOver(m, 'key-card', () => this.P.open('cards', 'ent'), 0xff7a7a);
            this.P.setFlag('pills');
            sfx.done();
        });
        return true;
    }

    // --- Region 4 -----------------------------------------------------------------------------


    // Housekeeping (population §6.5-6.6): near-catch 4's own way out (into the vent), the keys shown
    // at the laundry cart, the steward at his jammed cart, the uniform in the laundry's washer.
    setupHousekeeping() {
        const s = this.scene, w = this.world, L = w.data.linen;
        // (Near-catch 4 is a scene of its own since 2026-11-23, the user's: asleep on the bottle shelf, he is off into the
        // vent the moment she, or the laundry cart she pushes, all but touches him; her walk-up and reach are not played.)
        const bb4 = s.cats.find(c => c.flag === 'bb4');
        if (bb4) { bb4.custom = true; this.bb4 = bb4; }
        // (The cover on the shaft's mouth until he knocks it off, and where it lies after: the world's, `buildDuct`.)
        this.linenCart = w.pushables.find(t => t.id === 'cart_linen');
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
        this.bb4Wakes();
        // The steward pulls at his trolley's handle, and goes along with it as she pushes: one picture
        // of the two (his `tug`, the world's trolley hidden meanwhile), set by the trolley's middle
        // (`STEWARD_TUG`); free, he stands back from it (`STEWARD_FREE`).
        const st = this.who('npc_steward'), cart = this.stewardCart;
        // (Thanking her, and after while she is by him: turned to her wherever she goes, once he has
        // stepped off the handle.)
        if (st && !this.stewardStepping && (this.thanking || (P.has('cart_free') && st.state !== 'acting'
            && Math.abs(her.y - st.y) < 4 && Math.abs(her.x - st.x) < 4 * 48))) this.faceHer(st);
        if (st && cart && st.state !== 'acting' && !this.thanking) {
            const free = P.has('cart_free');
            cart.items[0].setVisible(free);
            st.bubbleDx = free ? 0 : STEWARD_HEAD;
            const x = cart.x + (free ? STEWARD_FREE : STEWARD_TUG);
            // (While she pushes it along he steps back with it, `tugwalk`; stopped, he tugs.)
            // (Moved within the last 150 ms: a frame without a step is no stop.)
            if (this.lastCartX !== undefined && cart.x !== this.lastCartX) this.cartMovedAt = time;
            this.lastCartX = cart.x;
            const moving = !free && time - (this.cartMovedAt ?? -1e9) < 150;
            const idle = free ? 'idle' : moving ? 'tugwalk' : 'tug';
            if (st.x !== x || st.free !== free || st.idle !== idle) {
                st.x = x;
                st.dir = -1;
                st.free = free;
                st.idle = idle;
                this.people.idle(st);
                this.people.place(st);
            }
            // (His card, if the thanks were cut short: loaded after the cart was freed.)
            if (free && !P.save.cards.includes('hk') && s.mode === 'play' && s.route === 'inside'
                && Math.abs(her.y - st.y) < 4 && Math.abs(her.x - st.x) < 110) this.stewardThanks();
        }
        // Out of the chute with a towel on her head: it slides off the moment she moves or jumps (the user, 2026-11-24: "Let
        // the towel fall down from our head as soon as we move or jump"; it had stayed a few steps).
        // (Watched only once she has stood on the floor in play: in the first frame after the climb out her body was not
        // yet on it, read as a jump, and the towel fell by itself, the user, 2026-11-24. Out of the room, the towel and the
        // one lying on its floor are the room's, and go: "If we exit into the corridor immediately, the towel is there".)
        if (this.hat) {
            const body = her.body, play = s.mode === 'play' && body.enable, down = body.blocked.down || body.touching.down;
            if (!this.hatArmed && play && down) this.hatArmed = true;
            const moved = this.hatArmed && play && (Math.abs(body.velocity.x) > 5 || body.velocity.y < -5 || !down);
            if (s.route !== 'laundry') this.hatAway();
            else if (moved && !this.hatGoing) this.hatOff();
        }
        if (this.towelDown && s.route !== 'laundry') this.hatAway();
        this.glimpseBalcony();
    }

    // Near-catch 4: she, or the cart she pushes, within `BB4_GAP` px of him asleep on the shelf (his body's own columns
    // in his frame, `BB4_SPAN`), and he is off into the vent. The beat's flag (crawling learned) once he is in.
    bb4Wakes() {
        const s = this.scene, w = this.world, cat = this.bb4, p = s.player;
        if (!cat || cat.gone || cat.hidden || s.route !== 'linen' || this.P.has('bb4')) return;
        const sp = cat.sprite, left = sp.x - 32 + (sp.flipX ? 64 - BB4_SPAN[1] : BB4_SPAN[0]), right = left + BB4_SPAN[1] - BB4_SPAN[0];
        const near = (a, b) => a <= right + BB4_GAP && b >= left - BB4_GAP;
        const cart = this.linenCart, half = cart ? cart.items[0].width / 2 : 0;
        if (!near(p.body.left, p.body.right) && !(cart && near(cart.x - half, cart.x + half))) return;
        cat.gone = true;
        s.tweens.killTweensOf(sp);
        sp.setScale(1);
        rumble('bolt');
        sfx.mrrp();
        this.intoTheVent(sp, () => {
            cat.away = true;
            sp.setVisible(false).stop();
            this.P.setFlag('bb4');
        });
    }

    // Bumbot's way out of the linen room: a leap from the shelf at the cover on the shaft's mouth, forward of him, which
    // comes off, turns a quarter toward the wall as it drops, its foot kicked out, and lands flat on the floor in front of
    // the mouth with a clang and a small bounce (the user, 2026-11-24: "let it fall flat on the ground, rotating while
    // falling"; it had slid down to lean by the wall); and he is in, and gone down the shaft the way it leads, toward the
    // bow. (The mouth's near side is drawn over him: he goes into it, not across it.)
    intoTheVent(sprite, done) {
        const s = this.scene, w = this.world, d = w.data.duct, floor = w.rooms.linen.floor, sh = w.shaft;
        sprite.setFlipX(d.mouthX < sprite.x).play('bumbot-leap');
        s.tweens.add({
            targets: sprite, x: d.mouthX + 12, y: d.upper + 1, duration: 320, ease: 'Quad.easeOut',
            onComplete: () => {
                if (sh.cover.visible) this.coverFalls();
                sfx.at(sprite.x, floor).scramble();
                const depth = sprite.depth;
                // (In on his belly, flat and long: his crawl since he was made again, 2026-11-24; he was squeezed
                // narrow by a scale.)
                // Nothing of him past the room's forward wall, as of her (`world.herCut`): his picture is cut there as he
                // goes in. (Turned by its scale for that: Phaser 4 crops a picture turned by `flipX` wrong.)
                const flip = sprite.flipX, turn = flip ? -1 : 1;
                sprite.setDepth(sh.mouth.depth - 0.001).play('bumbot-crawl').setFlipX(false).setScale(turn, 1);
                const cut = () => {
                    const keep = Phaser.Math.Clamp(Math.round(turn < 0 ? sprite.x + 32 - d.wallX : 64), 0, 64);
                    sprite.setCrop(0, 0, keep, 64);
                };
                cut();
                s.tweens.add({
                    targets: sprite, x: d.mouthX - 34, duration: 420, ease: 'Sine.easeIn', onUpdate: cut,
                    onComplete: () => { sprite.setCrop().setScale(1).setFlipX(flip).setDepth(depth); done(); },
                });
            },
        });
    }

    // The cover's fall (`fall` in assets/ship/shaft/shaft.json, tools/build_shaft.py): its frames' squares from where it
    // hung to where it lies, dropping as a thing falls (slow at first) while it turns, frame by frame, a quarter toward
    // the wall; on the floor a clang, a hop of 2 px tipped back a frame, and it settles; then the world's flat cover.
    coverFalls() {
        const s = this.scene, sh = this.world.shaft, F = sh.fall, c = sh.cover, down = sh.down, half = F.cell / 2;
        const last = F.frames - 1;
        const sp = s.add.sprite(F.start[0] + half, F.start[1] + half, 'shaft-cover-fall', 0).setDepth(c.depth);
        this.world.add([sp]);
        c.setVisible(false);
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
                    onComplete: () => { sp.destroy(); down.setVisible(true).setAlpha(1); },
                });
            },
        });
    }

    // The steward (population: `npc_steward`, `scn_card_hk`): his cart is free; he mops his brow,
    // thanks her, and tosses his card to her: she is doing his rounds now. Short, and she is free to
    // go on meanwhile; he keeps turned to her, and his card follows her (the user, 2026-11-18: it
    // "takes too long", and he did not turn as she ran past him).
    stewardThanks() {
        const st = this.who('npc_steward'), w = this.world, s = this.scene;
        if (!st || this.thanking || this.P.save.cards.includes('hk')) return;
        this.thanking = true;
        this.stewardStepping = false;
        (async () => {
            // (Let go of the handle: he steps back off it, `STEWARD_FREE` from its middle.)
            const to = this.stewardCart ? this.stewardCart.x + STEWARD_FREE : st.x;
            if (Math.abs(to - st.x) > 1) {
                this.stewardStepping = true;
                st.state = 'acting';
                st.dir = Math.sign(to - st.x);
                this.people.anim(st, 'walk');
                const step = { x: st.x };
                await w.tween({ targets: step, x: to, duration: Math.abs(to - st.x) / 80 * 1000,
                                onUpdate: () => { st.x = step.x; this.people.place(st); } });
                st.free = true;
                this.stewardStepping = false;
            }
            st.idle = 'idle';
            this.faceHer(st);
            this.people.idle(st);
            sfx.at(st.x, st.y).aah();
            await this.people.play(st, 'thanks', { speed: 1.8 });
            // (Out of his shirt pocket and tossed to her: `STEWARD_TOSS`.)
            await w.tossOver(st, 'key-card', () => this.P.open('cards', 'hk'), w.cardColour('hk'), STEWARD_TOSS);
            this.P.setFlag('steward');
            sfx.done();
            this.thanking = false;
            w.refresh();
        })().catch(err => { console.error(err); this.thanking = false; });
    }

    // (Someone turned to her where she is now.)
    faceHer(p) {
        const dir = this.scene.player.x < p.x ? -1 : 1;
        if (p.dir !== dir) { p.dir = dir; this.people.place(p); }
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
            sfx.take();
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
            sfx.at(mid, bride.y).kiss();
            await w.wait(620);
            sfx.shutter();
            sfx.at(mid, bride.y).heart();
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
            sfx.give();
            await w.tween({ targets: cam, x: bride.x + side * 10, y: bride.y - 34, duration: 380, ease: 'Sine.easeInOut' });
            cam.destroy();
            await w.handOver(bride, '@book-4', () => w.giveBook(4));
            // And in they go, at their door.
            const door = groom.x - 7;
            for (const p of [groom, bride]) {
                p.dir = door < p.x ? -1 : 1;
                this.people.anim(p, 'idle');
                await w.tween({ targets: p, x: door, duration: Math.abs(door - p.x) * 9 + 60, onUpdate: () => this.people.place(p) });
                sfx.at(door, p.y).door();
                await w.tween({ targets: p.sprite, alpha: 0, scale: 0.92, duration: 220 });
            }
            this.P.setFlag('photo');
            sfx.done();
            for (const p of [groom, bride]) p.sprite.setAlpha(1).setScale(1);
        });
        return true;
    }

    // The linen room's chute (population: `scn_chute`; the user, 2026-11-24): E at its hatch, low in the wall. She steps
    // to it, turns her back to us, crouches, pushes the flap in and slides in head first (one generated clip of her on the
    // room's own picture of the hatch, `chute-in`, tools/build_laundry_chute.py). The moment she is gone the room fades
    // into the ship's closed side (0.15 s) and the view drops with her, five decks in 2 s, nothing of her shown; just
    // before she comes out the laundry fades in round the chute's outlet, and she drops out of it into the cart of towels.
    chute() {
        const s = this.scene, w = this.world, to = w.rooms.laundry, L = w.data.linen, lin = w.rooms.linen;
        if (!to || w.carry || this.chuting) return false;
        const C = s.cache.json.get('chute'), her = s.player, x = L.chuteX;
        this.chuting = true;
        w.cut(async () => {
            her.body.enable = false;
            her.body.setVelocity(0, 0);
            // To the hatch's middle, and her back to us.
            if (Math.abs(her.x - x) > 1) {
                her.setFlipX(x < her.x);
                s.pose('run', 0.6);
                await w.tween({ targets: her, x, duration: Math.abs(her.x - x) / 70 * 1000 });
            }
            s.pose('back');
            await w.wait(120);
            const clip = s.add.sprite(lin.room.x + C.in.at[0], lin.room.y + C.in.at[1] + 1, 'chute-in', 0).setOrigin(0)
                .setDepth(s.DEPTH.player + 0.01);
            w.add([clip]);
            her.setVisible(false);
            if (!s.anims.exists('chute-in')) s.anims.create({ key: 'chute-in', frames: s.anims.generateFrameNumbers('chute-in'), frameRate: 12 });
            clip.on('animationupdate', (a, f) => {
                if (f.index === 6) sfx.at(x, lin.floor).hatch();
                if (f.index === 9) sfx.at(x, lin.floor).chute();
            });
            clip.play('chute-in');
            // (Down the moment her feet are in, with no hold on the empty hatch: the clip's frame 13 of 16.)
            await new Promise(done => {
                const gone = (a, f) => { if (f.index >= CHUTE.goneFrame) { clip.off('animationupdate', gone); done(); } };
                clip.on('animationupdate', gone);
                clip.once('animationcomplete', done);
            });
            await this.chuteDrop(clip);
        });
        return true;
    }

    // The way down: the linen room fades into the hull, the view falls with her (she is not drawn) from the hatch to the
    // laundry's outlet in `SHAFT`-like real time, the laundry fades in a moment before she shows, and she drops out of
    // the outlet, her picture cut at its mouth, into the cart of towels.
    async chuteDrop(clip) {
        const s = this.scene, w = this.world, to = w.rooms.laundry, lin = w.rooms.linen, her = s.player;
        const C = s.cache.json.get('chute'), x = w.data.linen.chuteX;
        const mouth = to.room.y + C.outlet.y + C.outlet.h;            // the outlet's mouth, its lowest row
        const fade = CHUTE.fadeMs;
        // Into the hull: the hatch's room fading out over the closed side, the view starting down.
        s.roomFade = { linen: 1, laundry: 0 };
        s.route = 'chute';
        // (The view held on her the whole way down: following at its usual ease it trailed 70 px behind her by the end,
        // and her dive out of the outlet happened under the screen's edge.)
        s.cameras.main.setLerp(0.15, 1);
        s.viewDeck = null;
        her.setPosition(x, lin.floor);
        const y0 = lin.floor, y1 = mouth;
        const start = s.time.now;
        let shown = false;
        await new Promise(done => {
            const step = () => {
                const t = s.time.now - start;
                const k = Math.min(1, t / CHUTE.dropMs);
                // (Slow at first, as down a steep chute: her feet's way from the hatch's floor to the outlet's mouth.)
                her.setPosition(x, y0 + (y1 - y0) * k * k);
                s.roomFade.linen = Math.max(0, 1 - t / fade);
                clip.setAlpha(s.roomFade.linen).setVisible(t <= fade);
                s.roomFade.laundry = Phaser.Math.Clamp((t - (CHUTE.dropMs - fade - CHUTE.leadMs)) / fade, 0, 1);
                if (s.roomFade.laundry >= 1 && !shown) {
                    shown = true;
                    s.route = 'laundry';
                    // (Its own deck open behind it until she lands: by her height, still high in the room, the cut-away
                    // would open the deck above.)
                    s.viewDeck = s.viewOverride = Math.round(s.deckAt(to.floor));
                    w.refresh();
                }
                if (k >= 1) {
                    s.events.off('update', step);
                    done();
                }
            };
            s.events.on('update', step);
        });
        clip.destroy();
        s.roomFade = null;
        if (s.route !== 'laundry') { s.route = 'laundry'; w.refresh(); }
        await this.outOfTheChute(mouth);
    }

    // Out of the outlet and into the cart (the user, 2026-11-24): she falls head first out of its mouth (her picture of the
    // dive, cut at the mouth) and into the heap of towels, the cart drawn over her, until she is all in; then she stands
    // up in it, the towel on her head, and climbs out over the cart's side. The towel slides off a few steps on
    // (`hatOff`).
    async outOfTheChute(mouth) {
        const s = this.scene, w = this.world, to = w.rooms.laundry, x = w.data.linen.laundryCartX, floor = to.floor;
        const her = s.player, C = s.cache.json.get('chute');
        her.body.enable = false;
        her.setVisible(false);
        her.setFlipX(false);
        // (The cart over her: its own pixels in the room's picture, from the heap's top down through the floor's slab,
        // so that nothing of her shows in it or under it.)
        const top = floor - C.cart.h, half = Math.ceil(C.cart.w / 2);
        const cover = s.add.image(to.room.x, to.room.y, to.room.texture.key).setOrigin(0).setDepth(s.DEPTH.player + 0.05)
            .setCrop(x - to.room.x - half, top - to.room.y, 2 * half, to.room.height - (top - to.room.y));
        w.add([cover]);
        // Head first out of the mouth: her dive's top (her feet) starts in the outlet, its foot (her head) at the mouth.
        const D = C.dive;
        const dive = s.add.image(x, mouth - D.h, 'chute-dive').setOrigin(0.5, 0).setDepth(s.DEPTH.player);
        w.add([dive]);
        const cut = () => {
            const hidden = Phaser.Math.Clamp(mouth - dive.y, 0, D.h);
            dive.setCrop(0, hidden, D.w, D.h - hidden);
        };
        cut();
        // (Falling on at the speed she came down the chute at, under gravity, until her head is at the cart's floor.)
        const v0 = 2 * (mouth - w.rooms.linen.floor) / (CHUTE.dropMs / 1000);
        const way = (floor - CHUTE.binFloor) - (mouth);           // her head from the mouth to the cart's floor
        const t = (Math.sqrt(v0 * v0 + 2 * PLAYER.gravity * way) - v0) / PLAYER.gravity;
        await w.tween({ targets: dive, y: dive.y + way, duration: t * 1000, ease: 'Quad.easeIn', onUpdate: cut });
        dive.destroy();
        sfx.flump();
        s.cameras.main.setLerp(0.15, 0.15);
        // She stands up in it, the towel on her head, from under the heap to knee-deep in it.
        s.pose('stand');
        her.setPosition(x, floor + CHUTE.under);
        her.setVisible(true);
        this.hat = s.add.image(0, 0, 'chute-towel').setOrigin(0).setDepth(s.DEPTH.player + 0.04);
        w.add([this.hat]);
        // (Placed after the physics has moved her, each frame: placed before it, in the update, it trailed her by a
        // frame's way and slid off the back of her head as she ran, the user, 2026-11-24.)
        if (!this.hatFollow) {
            this.hatFollow = () => this.placeHat();
            s.events.on('postupdate', this.hatFollow);
        }
        this.hatGoing = false;
        this.hatArmed = false;
        this.placeHat();
        await w.wait(CHUTE.lieMs);
        await w.tween({ targets: her, y: floor - CHUTE.sink, duration: CHUTE.riseMs, ease: 'Back.easeOut' });
        // (Over the heap now: in front of the cart again, as she climbs out.)
        this.hat.setDepth(s.DEPTH.player + 0.06);
        await w.wait(700);
        // Out over its side.
        s.pose('rise');
        her.setFlipX(true);
        await w.tween({ targets: her, x: x - 20, y: top - 12, duration: 240, ease: 'Quad.easeOut' });
        s.pose('fall');
        await w.tween({ targets: her, x: x - half - 22, y: floor, duration: 260, ease: 'Quad.easeIn' });
        cover.destroy();
        her.body.enable = true;
        her.body.reset(her.x, floor);
        s.takeoffY = floor;
        // (The view no longer held on the laundry's deck: held, the corridor's decks round it were left undimmed once she
        // went out, the user, 2026-11-24.)
        s.viewOverride = null;
        this.chuting = false;
        this.P.setFlag('chute');
    }

    // The towel slides off her head and falls like cloth (the user, 2026-11-24: "it has to behave like a towel, not like
    // a brick, and lay down flat as a towel, before it disappears"): its generated fall from where it lay on her head,
    // opening and fluttering down to lie flat on the floor where it slid off; a while there, then gone.
    hatOff() {
        const s = this.scene, w = this.world, her = s.player, hat = this.hat, F = s.cache.json.get('chute').fall;
        this.hat = null;
        sfx.cloth();
        const flip = hat.flipX;
        // (Its first frame is the towel as it lay on her head: placed on it; the floor under it is her floor.)
        const x = flip ? hat.x + hat.width - (F.cell - F.towel[0]) : hat.x - F.towel[0];
        const y0 = hat.y - F.towel[1], floor = her.y + PLAYER.sink;
        const y1 = floor - F.foot;
        hat.destroy();
        if (!s.anims.exists('chute-towel-fall')) {
            s.anims.create({ key: 'chute-towel-fall', frames: s.anims.generateFrameNumbers('chute-towel-fall'), frameRate: 11 });
        }
        // (In front of her as it slides off her head, as it lay on it; on the floor, behind her as she walks past it.)
        const sp = this.towelDown = s.add.sprite(x, y0, 'chute-towel-fall', 0).setOrigin(0).setFlipX(flip).setDepth(s.DEPTH.player + 0.06);
        w.add([sp]);
        // (The clip's own fall is a few px short of her floor or past it: made up over its frames.)
        const n = F.frames - 1;
        sp.on('animationupdate', (a, f) => sp.setY(Math.round(y0 + (y1 - y0) * (f.index - 1) / n)));
        sp.play('chute-towel-fall');
        sp.once('animationcomplete', () => {
            sp.setY(y1).setDepth(s.DEPTH.player - 0.02);
            s.tweens.add({ targets: sp, alpha: 0, duration: 1500, delay: 2500, onComplete: () => {
                sp.destroy();
                if (this.towelDown === sp) this.towelDown = null;
            } });
        });
    }

    // The towel gone at once, on her head or on the floor: she has left the laundry.
    hatAway() {
        const s = this.scene;
        this.hat?.destroy();
        this.hat = null;
        if (this.towelDown) {
            s.tweens.killTweensOf(this.towelDown);
            this.towelDown.destroy();
            this.towelDown = null;
        }
    }

    // The towel on her head, where it lies on her picture (`towel` in assets/ship/chute/chute.json: from her feet and her
    // middle), turned the way she faces.
    placeHat() {
        const her = this.scene.player, T = this.scene.cache.json.get('chute').towel, hat = this.hat;
        if (!hat || this.hatGoing) return;
        const flip = her.flipX;
        hat.setFlipX(flip).setPosition(her.x + (flip ? -T.dx - T.w : T.dx), her.y + PLAYER.sink + T.dy);
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
            sfx.at(cat.x, g.y).mrrp();
            cat.play('bumbot-leap');
            s.tweens.add({ targets: cat, x: cat.x + 26, y: g.topY - 70, duration: 420, ease: 'Quad.easeOut',
                onComplete: () => s.tweens.add({ targets: cat, alpha: 0, y: g.topY - 84, duration: 160, onComplete: () => cat.destroy() }) });
        });
    }

    // --- Region 5 -----------------------------------------------------------------------------

    // Out of the shaft's last grille into deck 8's forward corridor (population: `door_duct_exit`):
    // the grille swings open under her, dust comes down with her.
    outOfTheDuct() {
        const s = this.scene, w = this.world, d = w.data.duct;
        for (let i = 0; i < 9; i++) {
            const dot = s.add.image(d.dropX + Phaser.Math.Between(-12, 12), d.lower + 6, 'dot').setTint(0xb9a98a).setDepth(s.DEPTH.fx).setScale(1.5);
            w.add([dot]);
            s.tweens.add({ targets: dot, y: d.dropY - Phaser.Math.Between(4, 60), x: dot.x + Phaser.Math.Between(-8, 8), alpha: 0, duration: Phaser.Math.Between(700, 1300), delay: i * 40, onComplete: () => dot.destroy() });
        }
    }

    // The party behind the door with the balloons (population: `amb_party`): its music comes out
    // into the corridor as notes while she is near.
    // (`above`: she is in the shaft over the corridor, src/world/world.js: its beat comes up through the grille.)
    party(time, above = false) {
        const s = this.scene, w = this.world;
        this.partyDoor ??= w.things.find(t => t.id === 'amb_party') ?? null;
        const d = this.partyDoor, her = s.player;
        if (!d || Math.abs(her.x - d.x) > 330) return;
        if (above ? s.route !== 'duct' : (s.route !== 'inside' || Math.abs(her.y - d.y) > 8)) return;
        if (time < (this.noteAt ?? 0)) return;
        this.noteAt = time + 520;
        // Its beat through the door, and now and then a party horn.
        sfx.at(d.x, d.y).thump();
        if (Math.floor(time / 520) % 12 === 0) sfx.at(d.x, d.y).toot();
        // (Above the world as every other small mark, so that no one at the door covers them (V10, the user,
        // 2026-11-24); heard from the shaft over it they stay at the wall's depth, under the shaft's dark.)
        const note = s.add.text(d.x + Phaser.Math.Between(-8, 14), d.y - 50, ['♪', '♫', '♪'][Math.floor(time / 520) % 3], {
            fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: ['#e83b3b', '#4d9be6', '#905ea9'][Math.floor(time / 520) % 3], resolution: 4,
        }).setOrigin(0.5).setDepth(above ? s.DEPTH.decor + 0.3 : s.DEPTH.fx);
        w.add([note]);
        s.tweens.add({ targets: note, y: note.y - 34, x: note.x + Phaser.Math.Between(-14, 14), alpha: 0, duration: 1500, ease: 'Sine.easeOut', onComplete: () => note.destroy() });
    }
}

// Regions 6 (Lido), 7 (Outside) and 8 (Top deck + funnel) have files of their own.
Object.assign(Story.prototype, lido);
Object.assign(Story.prototype, outside);
Object.assign(Story.prototype, topdeck);
Object.assign(Story.prototype, bow);
Object.assign(Story.prototype, finale);
Object.assign(Story.prototype, spa);
