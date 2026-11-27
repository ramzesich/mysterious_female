// Splash Academy's kids (deck 7; plan-the-rest §7f, the user, 2026-11-27: the toddlers and the counsellor out, "1 and 2"):
// the pillow siege over the pillow castle, and two kids playing tag between the doorway from Entourage and the castle's
// aft side. Gone to bed on the evening of the catch, as the toddlers were (`until`). Each takes its place from
// maps/world.json (`bow.siege`, `bow.tag`).

import { PLAYER, SIEGE, TAG } from '../config.js';
import { sfx } from '../sfx.js';

const M = 48;
const nearby = (s, d) => Math.abs(s.player.x - d.x) < 900 && Math.abs(s.player.y - d.y) < 300;
const inPlay = (s, d) => s.mode === 'play' && s.route === 'inside' && Math.abs(s.player.y - d.y) < 100;

// The pillow siege (population: `haz_siege`): the knight forward of the castle and the king aft of it, facing it, lob one
// pillow to each other over it. The one who has it stands over it lying at their toes (their `throw`'s first frame, the
// pillow in it), picks it up and throws: from the frame it leaves their hands it is the game's, turning a quarter at a
// time over the castle and down onto the other's toes, where it is their `throw`'s first frame again. On its way it
// bonks her (26): she plops down with it on her head (her gag; the pillow hidden), the thrower cheers, and once she is
// back at her checkpoint the other has it at their toes. Her cry or her dash near one: the nearer ducks.
export class PillowSiege {
    constructor(world, def) {
        const s = world.scene;
        this.world = world;
        this.scene = s;
        this.def = def;             // { id, x: the middle, y, knightX, kingX, until }
        const add = (who, x, face) => world.people.add({ id: `${def.id}_${who.slice(7)}`, who, x, y: def.y, route: 'inside',
                                                         face, owned: true, layer: 'back', until: def.until });
        this.kids = [add('splash_knight', def.knightX, 1), add('splash_king', def.kingX, -1)].filter(Boolean);
        this.pillow = s.add.image(0, 0, 'things', 'splash-pillow').setDepth(s.DEPTH.player + 0.03).setVisible(false);
        world.add([this.pillow]);
        this.holder = 0;            // who has it (the knight first)
        this.phase = 'wait';
        this.k = 0;
        this.fly = null;
        this.hitAt = 0;
    }

    frames(p, clip) {
        return p.meta.anims[clip];
    }

    // Their own frame: a clip played by the scene (a duck, a cheer) runs by itself until it is over.
    still(p, frame) {
        if (p.playing) return;
        p.sprite.anims.stop();
        p.sprite.setFrame(frame);
    }

    playing(p, clip, ms, loop = false) {
        const P = this.world.people;
        p.playing = true;
        P.anim(p, clip, { loop });
        p.busyUntil = this.scene.time.now + ms;
    }

    heard(cry) {
        if (!cry || cry.route !== 'inside') return;
        this.duck(cry.x);
    }

    lunged(kind, fromX) {
        if (kind !== 'pillow') return false;
        // (She is through it: it flies on.)
        this.duck(fromX);
        return true;
    }

    // The nearer one ducks, the pillow held back while they do.
    duck(x) {
        const s = this.scene, d = this.def;
        if (!this.kids.length || !this.kids[0].on || Math.abs(s.player.y - d.y) > 70) return;
        const p = this.kids.reduce((a, b) => Math.abs(a.x - x) < Math.abs(b.x - x) ? a : b);
        if (Math.abs(p.x - x) > 4 * M) return;
        this.playing(p, 'duck', SIEGE.duckS * 1000);
        p.ducking = true;
        sfx.at(p.x, d.y).giggle();
    }

    // Back at her checkpoint after a bonk: the other one has it at their toes.
    restart() {
        this.lost = false;
        this.fly = null;
        this.pillow.setVisible(false);
        this.holder = this.target ?? 1 - this.holder;
        this.phase = 'wait';
        this.k = 0;
    }

    update(dt, time) {
        const s = this.scene, d = this.def, her = s.player;
        if (this.kids.length < 2 || !this.kids[0].on || !nearby(s, d)) {
            this.pillow.setVisible(false);
            return;
        }
        const P = this.world.people;
        for (const p of this.kids) {
            if (p.playing && time >= p.busyUntil) {
                p.playing = false;
                p.ducking = false;
            }
        }
        const h = this.kids[this.holder], o = this.kids[1 - this.holder], T = this.frames(h, 'throw');
        if (this.lost) {
            this.still(h, h.meta.stand);
            this.still(o, o.meta.stand);
            return;
        }
        if (this.phase === 'wait') {
            this.still(h, T[0]);
            if (!this.fly) this.still(o, o.meta.stand);
            if (!h.ducking) this.k += dt;
            if (this.k >= SIEGE.wait) {
                this.phase = 'throw';
                this.k = 0;
            }
        } else if (this.phase === 'throw') {
            if (h.ducking) {
                // (A duck while it is in their hands: it starts over from their toes.)
                this.phase = 'wait';
                this.k = 0;
            } else {
                this.k += dt;
                const [rel, ax, ay] = SIEGE.release[h.who];
                const f = 1 + Math.floor(this.k * SIEGE.fps);
                if (f >= rel && !this.fly) this.launch(h, o, ax, ay);
                if (f < T.length) this.still(h, T[f]);
                else {
                    this.still(h, h.meta.stand);
                    this.phase = 'flying';
                }
                this.still(o, o.meta.stand);
            }
        }
        if (this.fly) this.flying(dt, time, her);
    }

    launch(h, o, ax, ay) {
        const d = this.def;
        this.fly = { u: 0, x0: h.x + h.dir * ax, y0: d.y - ay, x1: o.x + o.dir * SIEGE.lie, y1: d.y - SIEGE.lieUp, from: h, to: o };
        this.target = this.kids.indexOf(o);
        sfx.at(h.x, d.y).toss();
    }

    flying(dt, time, her) {
        const s = this.scene, d = this.def, F = this.fly;
        F.u = Math.min(1, F.u + dt / SIEGE.flight);
        const u = F.u, base = F.y0 + (F.y1 - F.y0) * u;
        // (A lob whose peak is `peak` px over the floor: the line from hand to toes bowed up by what that takes.)
        const mid = (F.y0 + F.y1) / 2, bow = mid - (d.y - SIEGE.peak);
        const x = Math.round(F.x0 + (F.x1 - F.x0) * u), y = Math.round(base - 4 * bow * u * (1 - u));
        this.pillow.setVisible(true).setPosition(x, y).setAngle(90 * Math.floor(u * 8)).setFlipX(F.to.dir < 0);
        if (u >= 1) {
            // Down at the other's toes: their throw's first frame has it from here.
            this.fly = null;
            this.pillow.setVisible(false);
            sfx.at(x, d.y).towelFlump();
            this.holder = this.target;
            this.phase = 'wait';
            this.k = 0;
            return;
        }
        if (!inPlay(s, d) || time < this.hitAt) return;
        const hit = Math.abs(her.x - x) < PLAYER.bodyWidth / 2 + 6 && y > her.y - PLAYER.height - 4 && y < her.y;
        if (!hit) return;
        this.hitAt = time + 1500;
        if (this.world.carry) return this.world.carryBox.spill(x, false, 'pillow');
        const id = s.scareContact(x, 'pillow', { vx: (F.x1 - F.x0) / SIEGE.flight, ride: { hide: () => this.pillow.setVisible(false), show: () => this.restart() } });
        if (!id) return;
        // On her head: the thrower cheers; it is the other's again once she is back at her checkpoint.
        this.lost = true;
        this.fly = null;
        this.pillow.setVisible(false);
        this.playing(F.from, 'cheer', SIEGE.cheerS * 1000, true);
        sfx.at(F.from.x, d.y).giggle();
        // (Should her gag never give it back, a while after.)
        s.time.delayedCall(6000, () => this.lost && this.restart());
    }
}

// Tag (population: `haz_tag`): two kids run laps over their stretch, one chasing the other. At an end the one ahead turns
// back, they meet, giggles, and the tagged one counts a moment and chases the other the other way. Run into her (or she
// into them): on her bottom (27), and both freeze, giggling. A hop clears them (they come to her waist). Her cry or her
// dash near them: both freeze like statues a while.
export class Tag {
    constructor(world, def) {
        this.world = world;
        this.scene = world.scene;
        this.def = def;             // { id, x: the middle, y, x0, x1, until }
        const add = (who, x, face) => world.people.add({ id: `${def.id}_${who.slice(7)}`, who, x, y: def.y, route: 'inside',
                                                         face, owned: true, layer: 'back', until: def.until });
        this.kids = [add('splash_runner', def.x0 + 150, 1), add('splash_chaser', def.x0 + 40, 1)].filter(Boolean);
        this.lead = 0;              // who is ahead
        this.phase = 'chase';
        this.k = 0;
        this.hitAt = 0;
        this.frozenUntil = 0;
    }

    heard(cry) {
        if (!cry || cry.route !== 'inside' || !this.kids.length) return;
        if (this.kids.some(p => this.world.hears(p.x, this.def.y))) this.freeze(TAG.freezeS);
    }

    lunged(kind, fromX) {
        if (kind !== 'kid') return false;
        this.freeze(TAG.freezeS);
        return true;
    }

    freeze(sec) {
        const time = this.scene.time.now;
        if (time < this.frozenUntil) return;
        this.frozenUntil = time + sec * 1000;
        for (const p of this.kids) this.world.people.anim(p, 'freeze', { loop: false });
        sfx.at(this.kids[0].x, this.def.y).giggle();
    }

    run(p, dir, v, dt) {
        p.dir = dir;
        p.x += dir * v * M * dt;
        this.world.people.anim(p, 'run', { speed: v / TAG.pace });
    }

    stand(p, face) {
        if (face) p.dir = face;
        p.sprite.anims.stop();
        p.sprite.setFrame(p.meta.stand);
    }

    update(dt, time) {
        const s = this.scene, d = this.def, her = s.player, P = this.world.people;
        if (this.kids.length < 2 || !this.kids[0].on || !nearby(s, d)) return;
        const L = this.kids[this.lead], C = this.kids[1 - this.lead];
        if (time < this.frozenUntil) {
            for (const p of this.kids) P.place(p);
            return;
        }
        if (this.phase === 'chase') {
            let to = L.x + L.dir * TAG.lead * M * dt;
            if (to > d.x1 || to < d.x0) L.dir = -L.dir;         // at an end, back the way they came
            this.run(L, L.dir, TAG.lead, dt);
            L.x = Phaser.Math.Clamp(L.x, d.x0, d.x1);
            this.run(C, Math.sign(L.x - C.x) || C.dir, TAG.chase, dt);
            if (Math.abs(L.x - C.x) < 10) {
                // Tagged: giggles, face to face.
                this.phase = 'tag';
                this.k = 0;
                this.stand(L, Math.sign(C.x - L.x) || -C.dir);
                this.stand(C, Math.sign(L.x - C.x) || C.dir);
                sfx.at(L.x, d.y).giggle();
            }
        } else if (this.phase === 'tag') {
            this.k += dt;
            if (this.k >= TAG.tagS) {
                // The one who was chasing runs off, away from the wall nearer them; the tagged one counts.
                const away = C.x - d.x0 < d.x1 - C.x ? 1 : -1;
                this.lead = 1 - this.lead;
                this.phase = 'count';
                this.k = 0;
                C.dir = away;
            }
        } else if (this.phase === 'count') {
            this.k += dt;
            // (Now `L` is the one ahead: the old chaser off and away; `C` stands, counting.)
            this.run(L, L.dir, TAG.lead, dt);
            if (L.x > d.x1 || L.x < d.x0) {
                L.dir = -L.dir;
                L.x = Phaser.Math.Clamp(L.x, d.x0, d.x1);
            }
            this.stand(C, Math.sign(L.x - C.x) || C.dir);
            if (this.k >= TAG.countS) this.phase = 'chase';
        }
        for (const p of this.kids) P.place(p);
        // Into her, or she into them: over their heads she is clear.
        if (!inPlay(s, d) || time < this.hitAt) return;
        for (const p of this.kids) {
            if (Math.abs(her.x - p.x) < TAG.reach && her.y > d.y - TAG.clear) {
                this.hitAt = time + 1500;
                const moving = this.phase !== 'tag';
                if (this.world.carry) this.world.carryBox.spill(p.x, false, 'kid');
                else if (s.scareContact(p.x, 'kid', { vx: moving ? p.dir * TAG.lead * M : 0, dir: p.dir })) this.freeze(2);
                return;
            }
        }
    }
}
