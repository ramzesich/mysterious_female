// Region 9, "The bow" (GAME_DESIGN.md §6.1.3, docs/population.md decks 7, 9, 10, 11 and 12 forward,
// §6.9-6.10 and 6.12): the region's own things (the sauna's steam, the kids' club's ball pit, the
// step class's boards, the bridge's alarm) and its part of the story, mixed into the Story: the
// wedding planner and the cake (carried from Cagney's: a fragile load, src/world/carry.js), the
// party filing into the chapel and the ceremony there, the Spinnaker's piano, the kids' pool's
// slide, the captain's door, near-catch 6 on the bridge (the security officer's net comes down on
// the alarm panel, the hatch's ladder drops, Bumbot is up it), and the Library's odd book, which
// opens the reading nook once all ten books are back. Places come from maps/world.json (`bow`).

import { PLAYER } from '../config.js';
import { sfx } from '../sfx.js';
import { writeSave } from '../save.js';

const M = 48;
const HALF = PLAYER.height / 2;
const near = (s, x, y, dx = 900, dy = 320) => Math.abs(s.player.x - x) < dx && Math.abs(s.player.y - y) < dy;
const BALLS = [0xe83b3b, 0xf9c22b, 0x4d9be6, 0x1ebc73, 0x905ea9, 0xf68181];

// The sauna's steam (population: `haz_steam`): every few seconds a cloud of it rolls out of the
// sauna's aft door over the way past: "Fogged" (a tray is spilled). Wisps at the door's top and a
// hiss are the tell.
export class Steam {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x: the door, y, x1: how far it rolls, period, on, tell }
        this.g = s.add.graphics().setDepth(D.player + 0.04);
        world.add([this.g]);
        this.hitAt = 0;
    }

    // 'calm', 'tell' or 'on', and how far into it (0-1).
    phase(time) {
        const d = this.def, t = (time / 1000) % d.period;
        if (t >= d.period - d.on) return ['on', (t - (d.period - d.on)) / d.on];
        if (t >= d.period - d.on - d.tell) return ['tell', (t - (d.period - d.on - d.tell)) / d.tell];
        return ['calm', 0];
    }

    update(dt, time) {
        const s = this.scene, d = this.def, p = s.player, g = this.g.clear();
        if (!near(s, d.x, d.y, 700, 200)) return;
        const [phase, k] = this.phase(time);
        if (phase === 'calm') {
            this.told = false;
            return;
        }
        const top = d.y - 112;
        if (phase === 'tell') {
            if (!this.told) {
                this.told = true;
                sfx.whoosh();
            }
            // Wisps curling out over the door's top.
            for (let i = 0; i < 5; i++) {
                const a = (time / 300 + i * 0.23) % 1;
                g.fillStyle(0xffffff, 0.7 * (1 - a)).fillCircle(d.x + 4 + a * 16 + Math.sin(i * 2.1) * 3, top + 6 - a * 10 + i * 2, 2 + a * 3);
            }
            return;
        }
        // The cloud: out of the door, rolling aft and up, thinning.
        const env = k < 0.15 ? k / 0.15 : k > 0.7 ? Math.max(0, (1 - k) / 0.3) : 1;
        const reach = (d.x1 - d.x) * Math.min(1, k * 2.4 + 0.25);
        for (let i = 0; i < 16; i++) {
            const f = ((i * 0.618 + time / 900) % 1);
            const x = d.x + 4 + f * reach, y = d.y - 14 - ((i * 37) % 80) - Math.sin(time / 240 + i) * 5 - f * 10;
            g.fillStyle(i % 3 ? 0xffffff : 0xc7dcd0, (0.75 - f * 0.35) * env).fillCircle(x, y, 9 + ((i * 13) % 8) + f * 6);
        }
        if (env < 0.6 || s.mode !== 'play' || s.route !== 'inside' || time < this.hitAt) return;
        if (p.x < d.x + 2 || p.x > d.x + reach - 6 || Math.abs(p.y - d.y) > 80) return;
        this.hitAt = time + 1500;
        if (this.world.carry) this.world.carryBox.spill(d.x);
        else s.scareContact(d.x, 'fogged');
    }
}

// The ball pit across Entourage (population: `haz_ballpit`): a padded box of coloured balls,
// waist deep. Over its end wall with a hop, and she wades through it at half her speed, the balls
// in front of her to the waist, popping up round her. No fright. One ball in it is a tangerine.
export class BallPit {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, tangerine: its id, tanX }
        const { x0, x1, y } = def, w = x1 - x0;
        const ball = (g, x, yy, i) => {
            g.fillStyle(0x2e222f, 1).fillCircle(x, yy, 4);
            g.fillStyle(BALLS[i % BALLS.length], 1).fillCircle(x, yy, 3);
            g.fillStyle(0xffffff, 0.8).fillRect(x - 2, yy - 2, 1, 1);
        };
        // (Drawn once into two pictures: as live graphics its hundreds of balls cost ten frames a
        // second, everywhere on the ship.)
        const bake = (key, h, draw) => {
            if (!s.textures.exists(key)) {
                const g = s.make.graphics({ x: 0, y: 0 }, false);
                draw(g);
                g.generateTexture(key, w, h);
                g.destroy();
            }
            return s.add.image(x0, y, key).setOrigin(0, 1);
        };
        // Behind her: the back wall's padding and the balls against it.
        const back = bake('ballpit-back', 40, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 0, w, 40);
            g.fillStyle(0x4d65b4, 1).fillRect(1, 1, w - 2, 39);
            g.fillStyle(0x4d9be6, 1).fillRect(1, 1, w - 2, 4);
            for (let x = 24; x < w - 8; x += 36) g.fillStyle(0x323353, 1).fillRect(x, 5, 1, 35);
            for (let i = 0, x = 9; x < w - 6; x += 6, i++) ball(g, x + (i % 2), 12 - ((i * 7) % 5), i * 5 + 2);
        }).setDepth(D.decor + 0.3);
        // In front of her: balls to her waist, and the padded front wall with its end posts.
        const front = bake('ballpit-front', 32, g => {
            for (let row = 0; row < 4; row++) {
                for (let i = 0, x = 8 + (row % 2) * 3; x < w - 6; x += 6, i++) ball(g, x, 4 + row * 5 + ((i * 5 + row) % 3), i * 7 + row * 3);
            }
            g.fillStyle(0x2e222f, 1).fillRect(0, 19, w, 13);
            g.fillStyle(0xe83b3b, 1).fillRect(1, 20, w - 2, 11);
            g.fillStyle(0xf68181, 1).fillRect(1, 20, w - 2, 2);
            g.fillStyle(0xae2334, 1).fillRect(1, 29, w - 2, 2);
            for (let x = 36; x < w - 8; x += 36) g.fillStyle(0xae2334, 1).fillRect(x, 22, 1, 9);
            for (const ex of [0, w - 8]) {
                g.fillStyle(0x2e222f, 1).fillRect(ex, 6, 8, 26);
                g.fillStyle(0xf9c22b, 1).fillRect(ex + 1, 7, 6, 24);
                g.fillStyle(0xfbff86, 1).fillRect(ex + 1, 7, 6, 2);
            }
        }).setDepth(D.player + 0.04);
        // The one that is not a ball: orange, a leaf on it, a glint now and then.
        this.odd = s.add.graphics().setDepth(D.player + 0.045);
        this.odd.fillStyle(0x2e222f, 1).fillCircle(def.tanX, y - 29, 4);
        this.odd.fillStyle(0xf79617, 1).fillCircle(def.tanX, y - 29, 3);
        this.odd.fillStyle(0x1ebc73, 1).fillRect(def.tanX, y - 34, 2, 2);
        this.odd.fillStyle(0xffffff, 1).fillRect(def.tanX - 2, y - 31, 1, 1);
        world.add([back, front, this.odd]);
        // Its end walls: a hop takes her over one.
        for (const ex of [x0 + 4, x1 - 4]) {
            const zone = s.add.zone(ex, y, 8, 24).setOrigin(0.5, 1);
            s.physics.add.existing(zone, true);
            world.solids.push({ id: `${def.id}_wall`, x: ex, y, route: 'inside', items: [], zone });
        }
        world.things.push({ id: def.id, x: (x0 + x1) / 2, y, route: 'inside', items: [back, front] });
        this.popAt = 0;
    }

    update(dt, time) {
        const s = this.scene, d = this.def, p = s.player;
        this.odd.setVisible(!s.save.collected.includes(d.tangerine));
        const inside = s.route === 'inside' && Math.abs(p.y - d.y) < 30 && p.x > d.x0 + 8 && p.x < d.x1 - 8;
        if (inside !== this.inside) {
            this.inside = inside;
            s.wading = inside;
        }
        if (!inside || Math.abs(p.body.velocity.x) < 10 || time < this.popAt) return;
        // Balls pop up round her as she pushes through.
        this.popAt = time + 110;
        const g = s.add.graphics().setDepth(s.DEPTH.player + 0.05);
        const c = BALLS[Math.floor(time / 110) % BALLS.length];
        g.fillStyle(0x2e222f, 1).fillCircle(0, 0, 4);
        g.fillStyle(c, 1).fillCircle(0, 0, 3);
        g.setPosition(p.x + Phaser.Math.Between(-9, 9), d.y - 28);
        this.world.add([g]);
        s.tweens.add({ targets: g, y: d.y - 40 - Phaser.Math.Between(0, 12), x: g.x + Phaser.Math.Between(-12, 12), duration: 220, ease: 'Quad.easeOut', yoyo: true, onComplete: () => g.destroy() });
    }
}

// --- The region's part of the story (mixed into the Story) --------------------------------------

export const bow = {
    setupBow() {
        const s = this.scene, w = this.world, B = w.data.bow, D = s.DEPTH;
        if (!B) return;
        this.B = B;
        w.movers.push(new Steam(w, B.steam));
        w.movers.push(this.pit = new BallPit(w, B.pit));

        // The step class's boards, one in front of each of its two.
        const boards = s.add.graphics().setDepth(D.decor + 0.115);
        for (const b of B.steps) {
            boards.fillStyle(0x2e222f, 1).fillRect(b.x - 14, b.y - 7, 28, 7);
            boards.fillStyle(0x4d9be6, 1).fillRect(b.x - 13, b.y - 6, 26, 3);
            boards.fillStyle(0x8fd3ff, 1).fillRect(b.x - 13, b.y - 6, 26, 1);
            boards.fillStyle(0x625565, 1).fillRect(b.x - 12, b.y - 3, 5, 3).fillRect(b.x + 7, b.y - 3, 5, 3);
        }
        w.add([boards]);

        // What E does here: the piano, the slide's ladder, the captain's door, the odd book.
        w.things.push({ id: 'sec_piano', x: B.piano.x, y: B.piano.y, route: 'inside', items: [], reach: 14, interact: () => this.piano() });
        w.things.push({ id: 'sec_slide', x: B.slide.ladderX, y: B.slide.y, route: 'inside', items: [], reach: 12, interact: () => this.slide() });
        w.things.push({ id: 'sec_captain', x: B.captain.x, y: B.captain.y, route: 'inside', items: [], reach: 14, interact: () => this.knock() });

        // The odd book on the Library's bookcase: a spine that sticks out a little; with all ten
        // back it glints. Behind the bookcase, once it has swung: a doorway, lamp light in it.
        const N = B.nook;
        this.oddBook = s.add.graphics().setDepth(D.decor + 0.2);
        this.oddBook.fillStyle(0x2e222f, 1).fillRect(-3, -12, 6, 13);
        this.oddBook.fillStyle(0x0b5e65, 1).fillRect(-2, -11, 4, 11);
        this.oddBook.fillStyle(0xf9c22b, 1).fillRect(-2, -8, 4, 1).fillRect(-2, -3, 4, 1);
        this.oddBook.setPosition(N.x + 9, N.y - N.up);
        this.oddGlint = s.add.image(N.x + 9, N.y - N.up - 8, 'dot').setTint(0xfbff86).setDepth(D.decor + 0.21);
        s.tweens.add({ targets: this.oddGlint, alpha: { from: 0.1, to: 1 }, scale: { from: 0.6, to: 1.8 }, duration: 500, yoyo: true, repeat: -1, repeatDelay: 700 });
        this.nookWay = s.add.graphics().setDepth(D.decor + 0.19);
        this.nookWay.fillStyle(0x2e222f, 1).fillRect(N.x - 31, N.y - 58, 62, 58);
        this.nookWay.fillStyle(0x46291f, 1).fillRect(N.x - 29, N.y - 56, 58, 56);
        this.nookWay.fillStyle(0xf9c22b, 0.35).fillRect(N.x - 22, N.y - 52, 44, 52);
        this.nookWay.fillStyle(0xfbff86, 0.35).fillRect(N.x - 12, N.y - 48, 24, 48);
        // (The bookcase itself, swung open on its hinges: seen edge-on at the doorway's side.)
        this.nookWay.fillStyle(0x2e222f, 1).fillRect(N.x + 25, N.y - 58, 8, 58);
        this.nookWay.fillStyle(0x7a4528, 1).fillRect(N.x + 26, N.y - 57, 6, 56);
        for (let y = N.y - 50; y < N.y - 6; y += 11) this.nookWay.fillStyle(0xab947a, 1).fillRect(N.x + 26, y, 6, 1);
        w.add([this.oddBook, this.oddGlint, this.nookWay]);
        w.things.push({ id: 'sec_oddbook', x: N.x + 9, y: N.y, route: 'inside', items: [], reach: 18, until: 'flag:nook', interact: () => this.oddBookPull() });

        // The bridge's alarm: a red wash over the bridge and the panel's beacon, once it has gone off.
        const R = B.bridge;
        this.alarmWash = s.add.rectangle(R.x0, R.y - 128, R.x1 - R.x0, 128, 0xe83b3b, 0).setOrigin(0).setDepth(D.player + 0.3);
        this.alarmBeam = s.add.graphics().setDepth(D.player + 0.31);
        w.add([this.alarmWash, this.alarmBeam]);
        const bb6 = s.cats.find(c => c.flag === 'bb6');
        if (bb6) {
            bb6.before = () => this.netOnTheAlarm();
            bb6.flee = (sprite, done) => this.upTheHatch(sprite, done);
        }
        this.refreshBow();
    },

    refreshBow() {
        if (!this.B) return;
        const P = this.P, nook = P.has('nook');
        this.oddBook?.setVisible(!nook);
        this.oddGlint?.setVisible(!nook && P.has('books_all'));
        this.nookWay?.setVisible(nook);
    },

    updateBow(dt, time) {
        const s = this.scene, w = this.world, P = this.P, B = this.B, her = s.player;
        if (!B) return;
        const play = s.mode === 'play';
        // The planner shows what she is waiting for; from then on the cake is hers to take.
        const pl = this.who('npc_planner');
        if (pl?.on && play && !P.has('cake_asked') && s.route === 'inside' && Math.abs(her.y - pl.y) < 8 && Math.abs(her.x - pl.x) < 4.5 * M) {
            P.setFlag('cake_asked');
        }
        // The cake in her hands the first time: how it is carried.
        if (w.carry?.kind === 'cake' && !w.save.seen.includes('hint-cake')) {
            w.save.seen.push('hint-cake');
            w.hint('Steady! Every start, stop and turn sets the cake swaying');
        }
        // A cake gone over: the pastry chef's sigh, the next time she stands before him.
        const has = w.carry?.kind === 'cake';
        if (this.hadCake && !has && !this.handing && !P.has('wedding')) this.sighDue = true;
        this.hadCake = has;
        const chef = this.who('npc_pastrychef');
        if (this.sighDue && chef?.on && chef.state !== 'acting' && play && Math.abs(her.y - chef.y) < 8 && Math.abs(her.x - chef.x) < 3 * M) {
            this.sighDue = false;
            this.people.play(chef, 'sigh');
        }
        // The spa's receptionist bows to whoever comes in.
        const rec = this.who('amb_spa_reception');
        if (rec?.on && rec.state !== 'acting' && play && Math.abs(her.y - rec.y) < 8) {
            const close = Math.abs(her.x - rec.x) < 2.6 * M;
            if (close && !this.bowed) this.people.play(rec, 'bow');
            this.bowed = close || (this.bowed && Math.abs(her.x - rec.x) < 5 * M);
        }
        // In the chapel, the first time after the party has gone in: the ceremony.
        if (play && s.route === 'chapel' && P.has('wedding') && !P.has('ceremony') && !this.inCeremony) this.ceremony();
        // The alarm, from near-catch 6 until Bumbot is caught.
        // (Seen only from deck 10 itself: from the balcony above, the bridge is behind the ship's side.)
        const R = B.bridge;
        const on = (this.alarmOn || P.has('alarm')) && !P.has('catch') && her.y > R.y - 132 && her.y <= R.y + 2;
        if (on && near(s, (R.x0 + R.x1) / 2, R.y, 900, 200)) {
            const k = (Math.sin(time / 260) + 1) / 2;
            this.alarmWash.setFillStyle(0xe83b3b, 0.05 + 0.13 * k);
            const g = this.alarmBeam.clear(), bx = R.panelX, by = R.y - 62, a = time / 300;
            g.fillStyle(0xfbff86, 0.9).fillCircle(bx, by, 2 + k);
            g.fillStyle(0xe83b3b, 0.35).fillTriangle(bx, by, bx + Math.cos(a) * 60 - 8, by + Math.sin(a) * 14 - 6, bx + Math.cos(a) * 60 + 8, by + Math.sin(a) * 14 + 6);
            g.fillStyle(0xe83b3b, 0.35).fillTriangle(bx, by, bx - Math.cos(a) * 60 - 8, by - Math.sin(a) * 14 - 6, bx - Math.cos(a) * 60 + 8, by - Math.sin(a) * 14 + 6);
        } else if (this.alarmWash.fillAlpha) {
            this.alarmWash.setFillStyle(0xe83b3b, 0);
            this.alarmBeam.clear();
        }
    },

    // E at the wedding planner (population: `npc_planner`, `scn_wedding`): the cake from Cagney's.
    // She takes it and leads the party through the lobbies into the chapel; the way forward is clear.
    plannerCake() {
        const pl = this.near('npc_planner', 46), w = this.world, s = this.scene, P = this.P;
        if (!pl || P.has('wedding')) return false;
        if (w.carry?.kind !== 'cake') {
            if (w.carry) return false;
            if (!P.has('cake_asked')) P.setFlag('cake_asked');
            w.nudge(pl);
            return true;
        }
        pl.state = 'acting';
        this.handing = true;
        w.cut(async () => {
            const her = s.player, D = s.DEPTH, W = this.B.wedding, cam = s.cameras.main;
            const pan = (x, y, ms) => new Promise(resolve => cam.pan(x, y, ms, 'Sine.easeInOut', true, (_, k) => { if (k === 1) resolve(); }));
            her.setFlipX(pl.x < her.x);
            pl.dir = her.x < pl.x ? -1 : 1;
            this.people.place(pl);
            await w.wait(200);
            w.carryBox.give();
            const cake = s.add.image(her.x + (her.flipX ? -14 : 14), her.y - 34, 'things', 'wedding-cake').setOrigin(0.5, 1).setDepth(D.player + 0.05);
            w.add([cake]);
            sfx.pickup();
            await w.tween({ targets: cake, x: pl.x + pl.dir * 13, y: pl.y - 30, duration: 420, ease: 'Sine.easeInOut' });
            sfx.checkpoint();
            w.sparkle(cake.x, cake.y - 20);
            await w.wait(350);
            // The rope off, the doors open, and in they go: the couple first, the guests, the planner
            // last with the cake.
            const ropes = P.blockDrawings.filter(d => d.id === 'wedding').flatMap(d => d.items);
            s.tweens.add({ targets: ropes, alpha: 0, duration: 250 });
            for (const id of W.doors) {
                const d = s.bulkheads.find(b => b.id === id);
                if (d) {
                    d.ajar = true;
                    s.setBulkheadOpen(d, true);
                }
            }
            cam.stopFollow();
            s.viewOverride = 12;
            const party = ['amb_wed_d', 'amb_wed_c', 'amb_wed_b', 'amb_wed_a', 'amb_wed_groom', 'amb_wed_bride'].map(id => this.who(id)).filter(p => p?.on);
            const walkIn = async (p, delay, carried) => {
                p.state = 'acting';
                await w.wait(delay);
                p.dir = -1;
                this.people.place(p);
                this.people.anim(p, 'walk', { speed: 1.25 });
                const place = () => {
                    this.people.place(p);
                    carried?.setPosition(p.x - 13, p.y - 30);
                };
                await w.tween({ targets: p, x: W.chapelX + 6, duration: Math.abs(p.x - W.chapelX) * 7, onUpdate: place });
                await w.tween({ targets: [p.sprite, carried].filter(Boolean), alpha: 0, duration: 220 });
                p.gone = true;
                p.items.forEach(i => i.setVisible(false));
                p.sprite.setAlpha(1);
            };
            const going = party.map((p, i) => walkIn(p, 400 + i * 300));
            going.push(walkIn(pl, 400 + party.length * 300 + 200, cake));
            await pan(W.lookX, W.y - HALF - 20, 1300);
            await pan(W.chapelX + 150, W.y - HALF - 20, 2600);
            await Promise.all(going);
            cake.destroy();
            await w.wait(300);
            await pan(her.x, her.y - HALF, 1500);
            s.viewOverride = null;
            cam.startFollow(her, true, 0.15, 0.15);
            cam.setFollowOffset(0, HALF);
            for (const id of W.doors) {
                const d = s.bulkheads.find(b => b.id === id);
                if (d) d.ajar = false;
            }
            this.handing = false;
            P.setFlag('wedding');
            ropes.forEach(i => i.setAlpha(1));
        });
        return true;
    },

    // The ceremony (population: `scn_ceremony`): the first time she steps into the chapel after the
    // party. A kiss, hearts, confetti; then a frame on the wall that was not there (`slot_chapel`).
    ceremony() {
        const s = this.scene, w = this.world, D = s.DEPTH;
        this.inCeremony = true;
        w.cut(async () => {
            const bride = this.who('amb_cer_bride'), groom = this.who('amb_cer_groom'), a = this.who('amb_cer_a');
            await w.wait(700);
            if (!bride?.on || !groom?.on) {
                this.P.setFlag('ceremony');
                return;
            }
            const mid = (bride.x + groom.x) / 2, y = bride.y;
            // Confetti from above, all the way through.
            const confetti = s.time.addEvent({ delay: 70, loop: true, callback: () => {
                const c = s.add.rectangle(mid + Phaser.Math.Between(-70, 70), y - 118, 2, 2, BALLS[Phaser.Math.Between(0, BALLS.length - 1)]).setDepth(D.fx);
                w.add([c]);
                s.tweens.add({ targets: c, y: y - 4, x: c.x + Phaser.Math.Between(-14, 14), angle: 360, duration: Phaser.Math.Between(1300, 2000), onComplete: () => c.destroy() });
            } });
            await w.wait(900);
            this.people.play(groom, 'kiss');
            await this.people.play(bride, 'kiss');
            sfx.checkpoint();
            for (let i = 0; i < 5; i++) {
                const heart = s.add.text(mid + Phaser.Math.Between(-10, 10), y - 62, '♥', { fontFamily: 'Verdana, sans-serif', fontSize: '9px', color: '#e83b3b', resolution: 4 }).setOrigin(0.5).setDepth(D.fx);
                w.add([heart]);
                s.tweens.add({ targets: heart, y: heart.y - 26 - i * 4, x: heart.x + Phaser.Math.Between(-12, 12), alpha: 0, duration: 1300, delay: i * 160, onComplete: () => heart.destroy() });
            }
            if (a?.on) this.people.play(a, 'sip');
            await w.wait(1900);
            confetti.remove();
            await w.wait(700);
            this.P.setFlag('ceremony');
            const slot = w.things.find(t => t.id === 'slot_chapel');
            if (slot) w.sparkle(slot.x, slot.y - (slot.dy ?? 60));
        });
    },

    // E at the Spinnaker's grand piano (population: `sec_piano`): a few notes.
    piano() {
        const s = this.scene, w = this.world, her = s.player, B = this.B.piano;
        if (w.carry || this.playing) return false;
        this.playing = true;
        w.cut(async () => {
            her.setFlipX(false);
            her.x = B.x;
            her.body.reset(her.x, her.y);
            await w.wait(150);
            const notes = s.time.addEvent({ delay: 330, loop: true, callback: () => {
                sfx.ding();
                const n = s.add.text(B.x + 22 + Phaser.Math.Between(-6, 10), B.y - 58, Phaser.Math.Between(0, 1) ? '♪' : '♫', { fontFamily: 'Verdana, sans-serif', fontSize: '10px', color: '#2e222f', stroke: '#ffffff', strokeThickness: 2, resolution: 4 })
                    .setOrigin(0.5).setDepth(s.DEPTH.fx);
                w.add([n]);
                s.tweens.add({ targets: n, y: n.y - 26, x: n.x + Phaser.Math.Between(-8, 14), alpha: 0, duration: 1100, onComplete: () => n.destroy() });
            } });
            if (s.anims.exists('her-keys')) her.anims.play({ key: 'her-keys', repeat: 2 });
            await w.wait(2500);
            notes.remove();
            s.pose('stand');
            if (!w.save.seen.includes('sec_piano')) {
                w.save.seen.push('sec_piano');
                writeSave(w.save);
            }
            this.playing = false;
        });
        return true;
    },

    // E at the kids' pool's slide (population: `sec_slide`): up its ladder, down its chute, and
    // into the pool with a splash.
    slide() {
        const s = this.scene, w = this.world, her = s.player, S = this.B.slide;
        if (w.carry || this.sliding) return false;
        this.sliding = true;
        w.cut(async () => {
            her.body.enable = false;
            her.setFlipX(true);
            her.x = S.ladderX;
            if (s.anims.exists('her-climb')) her.anims.play('her-climb');
            await w.tween({ targets: her, y: S.y - S.top, x: S.topX, duration: 620 });
            s.pose('rise');
            await w.wait(180);
            sfx.whoosh();
            s.pose('fall');
            await w.tween({ targets: her, x: S.x0 + 4, y: S.y - 8, duration: 420, ease: 'Quad.easeIn' });
            // Off the chute's foot, over the rim.
            await w.tween({ targets: her, x: S.poolX, y: S.y - 14, duration: 200 });
            her.body.enable = true;
            her.body.reset(her.x, her.y);
            her.body.setVelocity(-60, 40);
            if (!w.save.seen.includes('sec_slide')) {
                w.save.seen.push('sec_slide');
                writeSave(w.save);
            }
            this.sliding = false;
        });
        return true;
    },

    // E at the captain's door (population: `sign_captain`): a polite knock. Nobody answers.
    knock() {
        const s = this.scene, w = this.world, her = s.player, C = this.B.captain;
        if (w.carry || this.knocking) return false;
        this.knocking = true;
        w.cut(async () => {
            her.x = C.x - 4;
            her.body.reset(her.x, her.y);
            if (s.anims.exists('her-knock')) her.anims.play('her-knock');
            else s.pose('back');
            for (let i = 0; i < 3; i++) {
                await w.wait(i ? 230 : 380);
                sfx.land();
                const t = s.add.text(C.x + 12 + i * 5, C.y - 52 - i * 4, 'тук', { fontFamily: 'Verdana, sans-serif', fontSize: '6px', fontStyle: 'bold', color: '#2e222f', stroke: '#ffffff', strokeThickness: 2, resolution: 4 })
                    .setOrigin(0.5).setDepth(s.DEPTH.fx);
                w.add([t]);
                s.tweens.add({ targets: t, y: t.y - 10, alpha: 0, duration: 700, onComplete: () => t.destroy() });
            }
            await w.wait(900);
            s.pose('back');
            w.say('…', 900);
            await w.wait(900);
            s.pose('stand');
            if (!w.save.seen.includes('sec_captain')) {
                w.save.seen.push('sec_captain');
                writeSave(w.save);
            }
            this.knocking = false;
        });
        return true;
    },

    // E at the odd book (population: `scn_nook`): stuck, until all ten books are back on the shelf.
    // Then it tips, something clicks, and the bookcase swings open on the reading nook.
    oddBookPull() {
        const s = this.scene, w = this.world, N = this.B.nook;
        if (w.carry || this.P.has('nook') || this.pulling) return false;
        this.pulling = true;
        w.cut(async () => {
            const her = s.player;
            her.setFlipX(N.x + 9 < her.x);
            if (s.anims.exists('her-pull')) her.anims.play('her-pull');
            await w.wait(300);
            await w.tween({ targets: this.oddBook, angle: -24, duration: 160 });
            if (!this.P.has('books_all')) {
                // It will not come: there are gaps on the shelf yet.
                sfx.land();
                await w.tween({ targets: this.oddBook, angle: 0, duration: 200 });
                s.pose('stand');
                w.say('?', 800);
                this.pulling = false;
                return;
            }
            sfx.rattle();
            await w.wait(350);
            s.cameras.main.shake(260, 0.004);
            sfx.door();
            this.nookWay.setVisible(true).setAlpha(0);
            this.oddGlint.setVisible(false);
            await w.tween({ targets: this.nookWay, alpha: 1, duration: 700 });
            w.sparkle(N.x, N.y - 30);
            sfx.checkpoint();
            s.pose('stand');
            this.pulling = false;
            this.P.setFlag('nook');
        });
        return true;
    },

    // Near-catch 6, before Bumbot leaps (population §6.10): the security officer, who has been
    // creeping up on him from the forward end, swings his net: it comes down on the alarm panel.
    // Red light, and the emergency hatch lets its ladder down.
    async netOnTheAlarm() {
        const s = this.scene, w = this.world, R = this.B.bridge;
        const r = this.who('riv_bridge');
        if (r?.on) {
            r.state = 'acting';
            r.dir = 1;
            this.people.anim(r, 'walk', { speed: 1.8 });
            await w.tween({ targets: r, x: R.swatX, duration: Math.abs(R.swatX - r.x) * 7 + 60, onUpdate: () => this.people.place(r) });
            sfx.dash();
            this.people.play(r, 'swing', { hold: 60000 });
            await w.wait(520);
        }
        // The net on the panel.
        sfx.smash();
        s.cameras.main.shake(260, 0.006);
        w.sparkle(R.panelX - 14, R.y - 22, 0xfbff86);
        this.alarmOn = true;
        sfx.horn?.(0.5);
        await w.wait(250);
    },

    // His way out: over the security officer's head onto the helm, along the console, and up the
    // ladder the hatch has just let down.
    upTheHatch(sprite, done) {
        const s = this.scene, w = this.world, R = this.B.bridge;
        const gate = w.gates.find(g => g.needs === 'alarm');
        // The hatch: its lid swings away, its ladder comes down rung by rung.
        this.P.setFlag('alarm');
        if (gate) {
            const tiles = [...gate.tiles].sort((a, b) => a.pixelY - b.pixelY);
            tiles.forEach(t => t.setAlpha(0));
            tiles.forEach((t, i) => s.time.delayedCall(60 + i * 55, () => { t.setAlpha(1); if (i % 2 === 0) sfx.land(); }));
        }
        const ladderX = gate?.x ?? R.x0 + 20, top = gate?.y0 ?? R.y - 144;
        sprite.setFlipX(true).play('bumbot-jump');
        s.tweens.chain({
            targets: sprite,
            tweens: [
                { x: R.helmX, y: R.y - 44, duration: 260, ease: 'Quad.easeOut' },
                { x: R.consoleX, y: R.y - 46, duration: 240, onStart: () => sprite.play('bumbot-run') },
                { x: ladderX, y: R.y - 60, duration: 200, ease: 'Quad.easeOut', onStart: () => sprite.play('bumbot-jump') },
                { y: top - 6, duration: 620, onComplete: () => sprite.setAlpha(0) },
            ],
            onComplete: () => {
                sprite.setAlpha(1);
                // The officer: on the floor by the helm, done for the day.
                const r = this.who('riv_bridge');
                if (r?.on) {
                    this.people.play(r, 'sit', { hold: 60000 });
                    s.tweens.add({ targets: r, x: R.sitX, duration: 300, onUpdate: () => this.people.place(r) });
                }
                s.time.delayedCall(700, done);
            },
        });
    },
};
