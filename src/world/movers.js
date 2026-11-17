// Things that move by themselves (docs/population.md §1): the delivery robot she can ride (a
// `platform`), the gulls (one creature with a few states and a rule per place), the stage's light,
// the casino's chips, and deck 9's housekeeping hour: the vacuum that darts out of a doorway, the
// towel stack, the sprinkler, the door that flies open, the "Do Not Disturb" door. Pictures:
// assets/sprites/things (tools/build_things.py).

import { PLAYER, CRY } from '../config.js';
import { sfx } from '../sfx.js';

const M = 48;

// The delivery robot (deck 6's forward cabins): a tall tray-carrying robot that trundles the
// corridor. It stops and beeps while she is in its way; she hops onto its top and it carries her
// along. Never a scare.
export class Robot {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;
        this.x = def.x;
        this.dir = 1;
        this.pausedUntil = 0;
        this.sprite = s.add.image(def.x, def.y, 'things', 'robot').setOrigin(0.5, 1).setDepth(D.props + 0.04);
        this.w = this.sprite.width + 6;
        this.h = this.sprite.height - 1;
        this.zone = s.add.zone(def.x, def.y, this.w, this.h).setOrigin(0.5, 1);
        s.physics.add.existing(this.zone, true);
        // (Its run short of any door or wall across the deck: ShipScene `stopShort`.)
        const span = s.spanOn(def.x, def.x0, def.x1, def.y, this.w / 2);
        this.x0 = span.lo;
        this.x1 = span.hi;
        this.beep = s.add.text(def.x, def.y - this.h - 6, '♪', {
            fontFamily: 'Verdana, sans-serif', fontSize: '9px', fontStyle: 'bold', color: '#0b5e65', resolution: 4,
        }).setOrigin(0.5, 1).setDepth(D.fx).setVisible(false);
        world.add([this.sprite, this.beep]);
    }

    addCollider(p) {
        this.scene.physics.add.collider(p, this.zone, null, () => this.scene.route === 'inside');
    }

    // A tangerine come to rest on its top rides along with it, hers to take back (walking over it
    // on the robot); docs/plan-three-uses.md §2. Never taken: it stays a loose tangerine.
    offered(t) {
        const d = this.def, top = d.y - this.h;
        if (t.route !== 'inside' || Math.abs(t.img.y + 3 - top) > (t.rider === this ? 1 : 8)) return false;
        if (t.rider !== this) {
            if (Math.abs(t.img.x - this.x) > this.w / 2 + 4 || t.img.body.velocity.y < 0) return false;
            // (Come down on its top, it stays there: a bounce would have it off so small a top.)
            t.rider = this;
            t.rideDx = Phaser.Math.Clamp(t.img.x - this.x, -this.w / 2 + 6, this.w / 2 - 6);
            t.img.y = top - 3;
            this.scene.loose.rest(t);
        }
        t.img.x = this.x + t.rideDx;
        const e = this.scene.save.loose.find(o => o.id === t.id);
        if (e) e.x = Math.round(t.img.x);
        return false;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (Math.abs(p.x - this.x) > 900 || Math.abs(p.y - d.y) > 300) return;
        const onFloor = p.body.blocked.down || p.body.touching.down;
        const riding = onFloor && s.route === 'inside' && Math.abs(p.y - (d.y - this.h)) < 4 && Math.abs(p.x - this.x) < this.w / 2 + PLAYER.bodyWidth / 2;
        // In its way: on the floor ahead of it, within two metres.
        const ahead = (p.x - this.x) * this.dir;
        const blocked = !riding && s.route === 'inside' && Math.abs(p.y - d.y) < 30 && ahead > 0 && ahead < 2 * M + this.w / 2;
        this.beep.setVisible(blocked && Math.floor(time / 300) % 2 === 0).setPosition(this.x, d.y - this.h - 6);
        // (Its beep: as she gets in its way, and again every so often while she stays there.)
        if (blocked && (!this.wasBlocked || time > this.beepAt)) {
            this.beepAt = time + 1200;
            sfx.at(this.x, d.y).robotBeep();
        }
        this.wasBlocked = blocked;
        if (blocked || time < this.pausedUntil) return;
        let to = this.x + this.dir * d.v * M * dt;
        if (to >= this.x1) { to = this.x1; this.dir = -1; this.pausedUntil = time + 900; }
        else if (to <= this.x0) { to = this.x0; this.dir = 1; this.pausedUntil = time + 900; }
        const dx = to - this.x;
        this.x = to;
        this.sprite.x = this.zone.x = to;
        this.sprite.setFlipX(this.dir < 0);
        this.zone.body.updateFromGameObject();
        // She rides along on its top.
        if (riding && s.mode === 'play') {
            p.x += dx;
            p.body.x += dx;
        }
    }
}

// A gull (population §5): perched somewhere, it flaps up out of her way when she comes near and
// settles again when she has gone (`shy`). The ones that swoop come with the open decks.
export class Gull {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;
        this.rise = 0;              // how far up it has flown, 0 to 1
        this.sprite = s.add.image(def.x, def.y, 'things', 'gull-perched').setOrigin(0.5, 1)
            .setDepth(def.route === 'inside' ? D.props + 0.06 : D.player + 0.34).setFlipX(!!def.flip);
        world.add([this.sprite]);
        this.items = [this.sprite];
        this.awaySince = 0;
    }

    // Her cry: up and away for a while.
    heard() {
        const d = this.def;
        if (this.world.hears(d.x, d.y + 40, d.route ?? 'inside')) this.scaredUntil = this.scene.time.now + 4000;
    }

    // A tangerine on the deck below its rail: down to it, and off with it; the rail clear 8 s
    // (docs/plan-three-uses.md §2).
    offered(t) {
        const s = this.scene, d = this.def;
        if (this.taking || s.time.now < (this.goneUntil ?? 0) || t.route !== (d.route ?? 'inside')) return false;
        if (Math.abs(t.img.x - d.x) > 3 * M || t.img.y < d.y - 10 || t.img.y > d.y + 80) return false;
        this.taking = true;
        this.world.gullTakes(this.sprite, t, () => {
            this.taking = false;
            this.goneUntil = s.time.now + 8000;
            this.rise = 1;
        });
        return true;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (this.taking) return;
        const on = (d.route === 'inside' || d.route === s.route) && time >= (this.goneUntil ?? 0);
        this.sprite.setVisible(on);
        if (!on) return;
        const near = Math.abs(p.x - d.x) < 3 * M && Math.abs(p.y - d.y) < 90 || time < (this.scaredUntil ?? 0);
        if (near) this.awaySince = time;
        const up = near || time - this.awaySince < 1400;
        if (up && this.rise === 0) sfx.at(d.x, d.y).flap();
        this.rise = Phaser.Math.Clamp(this.rise + (up ? 2.2 : -1.3) * dt, 0, 1);
        if (this.rise === 0) {
            this.sprite.setFrame('gull-perched').setPosition(d.x, d.y);
            return;
        }
        // In the air: flapping, bobbing, a little off to the side it faces.
        const flap = Math.floor(time / 130) % 2;
        const frames = s.textures.get('things');
        this.sprite.setFrame(flap && frames.has('gull-down') ? 'gull-down' : 'gull-up');
        const ease = this.rise * this.rise * (3 - 2 * this.rise);
        this.sprite.setPosition(d.x + (d.flip ? -1 : 1) * 10 * ease, d.y - 46 * ease + Math.sin(time / 240) * 2 * ease + (flap ? 2 : 0));
    }
}

// A stage light on its cable (population: `haz_lights`). Until its flag it is hauled up short and
// lights its spot; after (the rival's crash shook the rig) it hangs low and swings like a
// pendulum: at the bottom of its arc it is at her head's height, "Bonked"; at the ends it is over it.
export class SwingLight {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, top, floor, flag, short, long, amp (degrees), period (s) }
        this.cone = s.add.graphics().setDepth(D.decor + 0.3);
        this.g = s.add.graphics().setDepth(D.player + 0.3);
        world.add([this.cone, this.g]);
        this.wasOn = world.progress.has(def.flag);
        this.t0 = null;
        this.lamp = { x: def.x, y: def.top + def.short };
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        const near = Math.abs(p.x - d.x) < 800 && Math.abs(p.y - d.floor) < 300;
        this.g.setVisible(near);
        this.cone.setVisible(near);
        if (!near) return;
        const on = this.world.progress.has(d.flag);
        // (Already swinging when the game was loaded; or it starts now, dropping out to one side.)
        if (on && this.t0 === null) this.t0 = this.wasOn ? time - 60000 : time;
        const DROP = 900;
        let len = d.short, angle = 0;
        if (on) {
            const e = time - this.t0;
            // (Its cable creaks as it drops out, and once each swing.)
            const turn = e < DROP ? -1 : Math.floor((e - DROP) / (d.period * 1000));
            if (turn !== this.turn) {
                this.turn = turn;
                sfx.at(d.x, d.floor).creak();
            }
            if (e < DROP) {
                const k = Phaser.Math.Easing.Sine.InOut(e / DROP);
                len = d.short + (d.long - d.short) * k;
                angle = d.amp * k;
            } else {
                len = d.long;
                angle = d.amp * Math.cos((2 * Math.PI * (e - DROP)) / (d.period * 1000));
            }
        }
        const a = Phaser.Math.DegToRad(angle);
        const x = d.x + len * Math.sin(a), y = d.top + len * Math.cos(a);
        this.lamp = { x, y, swinging: on };
        const g = this.g.clear();
        g.lineStyle(1, 0x2e222f, 1).lineBetween(d.x, d.top, x, y - 5);
        g.fillStyle(0x2e222f, 1).fillRect(d.x - 3, d.top - 1, 6, 3);
        // The lamp: a black can with a warm lens, turned the way its cable hangs.
        const ux = Math.sin(a), uy = Math.cos(a);
        g.fillStyle(0x2e222f, 1).fillCircle(x, y, 7);
        g.fillStyle(0x625565, 1).fillCircle(x - ux * 2, y - uy * 2, 4);
        g.fillStyle(0xfbff86, 1).fillCircle(x + ux * 4, y + uy * 4, 3.5);
        // Its light on the stage.
        const fx = x + (d.floor - y) * Math.tan(a) * 0.6;
        this.cone.clear().fillStyle(0xfbff86, 0.1).fillTriangle(x, y, fx - 20, d.floor, fx + 20, d.floor);
        this.cone.fillStyle(0xfbff86, 0.12).fillEllipse(fx, d.floor - 1, 40, 5);
        if (!on || time - this.t0 < DROP || s.mode !== 'play' || s.route !== 'inside') return;
        if (Math.abs(p.x - x) < 7 + PLAYER.bodyWidth / 2 && p.y - PLAYER.bodyHeight < y + 6 && p.y > y - 6) {
            if (this.world.carry) this.world.carryBox.spill(x, false, 'light');
            else if (s.lungeSafe()) this.world.lunged('light', x);
            else {
                sfx.bonk();
                s.scareContact(x, 'light');
            }
        }
    }
}

// A slot machine that pays out by itself (population: `haz_chips`): every so often its lights race
// (the tell), then chips spill across the floor in front of it for a few seconds. Running on them
// she slips; standing still or hopped over, they are nothing.
export class Spill {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, y, half (px), top (px up to the machine's lights) }
        this.state = 'idle';
        this.at = null;
        this.lights = s.add.graphics().setDepth(D.decor + 0.3);
        this.chips = s.add.graphics().setDepth(D.props + 0.1);
        world.add([this.lights, this.chips]);
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (Math.abs(p.x - d.x) > 800 || Math.abs(p.y - d.y) > 200) return;
        this.at ??= time + Phaser.Math.Between(3000, 9000);
        if (this.state === 'idle' && time > this.at) {
            this.state = 'tell';
            this.at = time + 1500;
            sfx.at(d.x, d.y).slot();
        } else if (this.state === 'tell') {
            // The lights race along its top.
            const g = this.lights.clear(), lit = Math.floor(time / 90) % 6;
            for (let i = 0; i < 6; i++) g.fillStyle(i === lit || i === (lit + 3) % 6 ? 0xfbff86 : 0xae2334, 1).fillRect(d.x - 17 + i * 6, d.y - d.top, 4, 3);
            if (time > this.at) {
                this.state = 'spilled';
                this.at = time + 4000;
                this.lights.clear();
                this.pour();
                sfx.at(d.x, d.y).chips();
            }
        } else if (this.state === 'spilled') {
            const left = this.at - time;
            this.chips.setAlpha(left < 700 ? (Math.floor(time / 90) % 2 ? 0.35 : 1) : 1);
            const onFloor = p.body.blocked.down || p.body.touching.down;
            if (s.mode === 'play' && s.route === 'inside' && onFloor && Math.abs(p.y - d.y) < 3 && Math.abs(p.x - d.x) < d.half
                && Math.abs(p.body.velocity.x) > 20) {
                if (this.world.carry) this.world.carryBox.spill(d.x, false, 'chips');
                else if (s.lungeSafe()) this.world.lunged('chips', d.x);
                else {
                    sfx.slip();
                    s.scareContact(p.x - Math.sign(p.body.velocity.x) * 10, 'chips');
                }
            }
            if (left <= 0) {
                this.state = 'idle';
                this.at = time + Phaser.Math.Between(8000, 14000);
                this.chips.clear();
            }
        }
    }

    // The chips, scattered over its two metres of floor.
    pour() {
        const d = this.def, g = this.chips.clear();
        const colours = [0xe83b3b, 0x4d9be6, 0x1ebc73, 0xf3ecdd, 0xf9c22b];
        // (Thick on the floor, heaped toward the machine: seen at a glance.)
        for (let i = 0; i < 70; i++) {
            const off = Phaser.Math.Between(-d.half + 4, d.half - 4);
            const x = d.x + off, up = Phaser.Math.Between(0, Math.abs(off) < d.half / 2 ? 5 : 2);
            g.fillStyle(0x2e222f, 1).fillRect(x - 3, d.y - 3 - up, 7, 3);
            g.fillStyle(colours[i % colours.length], 1).fillRect(x - 2, d.y - 3 - up, 5, 2);
            g.fillStyle(0xffffff, 0.7).fillRect(x - 1, d.y - 3 - up, 2, 1);
        }
    }
}
// --- Region 4: deck 9's "housekeeping hour" (docs/population.md) -----------------------------------

// On this hazard's deck, in the corridor, at play.
const here = (s, d) => s.route === 'inside' && s.mode === 'play' && Math.abs(s.player.y - d.y) < 100;
// Of the cabin doors' places in a def's `doors`, the ones where a cabin door is drawn (the corridor
// leaves one out beside a lift's, a crew door, a stair hall: no hand reaches out of a wall there).
// Where the breakfast stewardess's hands hold her tray in each frame of her `carry` walk: px ahead
// of her middle, px over her feet (found frame by frame, as the eaters' fists).
const TRAY_HANDS = [[16, 33]];
// The breakfast stewardess behind her trolley: her middle this far from its middle, her hands on its
// handle in her `push` clip (drawn with the trolley there, 2026-11-17).
const HANDLE = 26;
const realDoors = (s, d) => (d.real ??= d.doors.filter(x => (s.cabinDoorsDrawn ?? []).some(c => c.y === d.y && Math.abs(c.x - x) < 6)));
const nearby = (s, d) => Math.abs(s.player.x - d.x) < 800 && Math.abs(s.player.y - d.y) < 300;

// The robot vacuum in the doorway of the cabin being cleaned (population: `haz_vacuum_9`). Its red
// eye blinks while she is coming; as she comes into reach it rattles, then darts out along the
// corridor at her (a fright; a jump as it rattles clears it; the dash sends it spinning) and backs
// in again, harmless. Then it stays in until she has gone away and come again.
export class Darter {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, y, reach, dart }
        this.sprite = s.add.image(def.x, def.y, 'vacuum').setOrigin(0.5, 1).setDepth(D.props + 0.02);
        this.eye = s.add.image(def.x, def.y - 8, 'dot').setTint(0xe83b3b).setDepth(D.props + 0.03);
        world.add([this.sprite, this.eye]);
        this.state = 'in';
        this.armed = true;
        this.at = 0;
        this.rest();
    }

    // In the doorway: small and dim, half in the cabin's dark.
    rest() {
        this.sprite.setPosition(this.def.x, this.def.y).setScale(0.8).setTint(0x9babb2).setAngle(0).setAlpha(1);
    }

    // A tangerine under it, thrown or lying: swallowed, and it chokes (docs/plan-three-uses.md §2).
    offered(t) {
        const s = this.scene, v = this.sprite;
        if (this.state === 'dead' || this.state === 'spun' || !s.loose.near(t, v.x, this.def.y, 12, 12)) return false;
        s.loose.remove(t);
        s.tweens.killTweensOf(v);
        this.state = 'dead';
        this.eye.setVisible(false);
        v.setScale(1).clearTint();
        this.world.choke(v);
        this.at = s.time.now + 700;
        return true;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def, v = this.sprite;
        // Choked: dead where it stands, smoking, until she has left the deck.
        if (this.state === 'dead') {
            if (s.route !== 'inside' || Math.abs(p.y - d.y) > s.deckPitch / 2) this.home(time);
            else if (time > this.at) {
                this.at = time + 900;
                this.world.drops(v.x, v.y - 10, 0x8a8a8a, -1);
            }
            return;
        }
        if (!nearby(s, d)) return;
        const dx = p.x - d.x, on = here(s, d) && Math.abs(p.y - d.y) < 40;
        const within = on && Math.abs(dx) < d.reach;
        this.eye.setVisible(this.state === 'in' && this.armed && on && Math.abs(dx) < d.reach * 2.3 && Math.floor(time / 130) % 2 === 0);
        if (this.state === 'in') {
            if (!within && time > this.at) this.armed = true;
            if (within && this.armed) {
                this.armed = false;
                this.state = 'wait';
                this.at = time + 300;
                this.dir = dx < 0 ? -1 : 1;
                sfx.at(d.x, d.y).vacRev();
            }
        } else if (this.state === 'wait') {
            v.x = d.x + (Math.floor(time / 40) % 2 ? 1 : -1);
            if (time > this.at) {
                this.state = 'out';
                v.setScale(1).clearTint().setFlipX(this.dir < 0);
                sfx.at(d.x, d.y).vacDart();
                // Out fast, a breath, and back in slowly: only on its way out is it a fright.
                s.tweens.add({
                    targets: v, x: s.stopShort(d.x, d.x + this.dir * d.dart, d.y, 9), duration: 400, ease: 'Quad.easeOut', hold: 160,
                    onComplete: () => {
                        if (this.state !== 'out') return;
                        this.state = 'back';
                        v.setFlipX(this.dir > 0);
                        s.tweens.add({ targets: v, x: d.x, duration: 700, ease: 'Sine.easeInOut', onComplete: () => { if (this.state === 'back') this.home(s.time.now + 1200); } });
                    },
                });
            }
        } else if (this.state === 'out') {
            const hit = here(s, d) && Math.abs(v.x - d.x) > 14 && Math.abs(p.x - v.x) < PLAYER.bodyWidth / 2 + 6
                && p.y > v.y - 6 && p.y - PLAYER.bodyHeight < v.y;
            if (!hit) return;
            if (s.isLunging()) {
                // Sent spinning; it creeps home after a while.
                s.tweens.killTweensOf(v);
                this.state = 'spun';
                s.smash(v.x, v.y - 3);
                s.tweens.add({ targets: v, angle: 720, alpha: 0.6, duration: 900, ease: 'Quad.easeOut', onComplete: () => this.home(s.time.now + 4000) });
            } else if (this.world.carry) {
                this.world.carryBox.spill(v.x, false, 'vacuum', { vx: this.dir * 300 });
            } else {
                s.scareContact(v.x, 'vacuum', { vx: this.dir * 300 });
            }
        }
    }

    home(until) {
        this.state = 'in';
        this.at = until;
        this.rest();
    }
}

// A tall stack of fresh towels by the open cabin's door (population: `haz_towels_9`): it sways. A
// jump landed beside it, or the dash, brings it down on that side: "Buried" if she is still under
// it. Walked past, it only wobbles. It is stacked again once she has gone.
export class TowelStack {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, y }
        TowelStack.textures(s);
        this.stool = s.add.image(def.x, def.y, 'towel-stool').setOrigin(0.5, 1).setDepth(D.props - 0.03);
        this.stack = s.add.image(def.x, def.y - 12, 'towel-stack').setOrigin(0.5, 1).setDepth(D.props - 0.02);
        this.heap = s.add.image(def.x, def.y, 'towel-heap').setOrigin(0.5, 1).setDepth(D.player + 0.06).setVisible(false);
        world.add([this.stool, this.stack, this.heap]);
        this.state = 'up';
        this.wasOnFloor = true;
    }

    static textures(s) {
        if (s.textures.exists('towel-stack')) return;
        const g = s.make.graphics({ x: 0, y: 0 }, false);
        // The stack: fourteen folded towels, white and pale blue, none quite square on the one below.
        for (let i = 0; i < 14; i++) {
            const y = 70 - (i + 1) * 5, off = [0, 1, -1, 1, 0, -1, 0, 2, -1, 0, 1, -1, 0, 1][i];
            g.fillStyle(0x9babb2, 1).fillRect(2 + off, y, 22, 5);
            g.fillStyle(i % 4 === 2 ? 0x8fd3ff : 0xffffff, 1).fillRect(3 + off, y, 20, 4);
            g.fillStyle(i % 4 === 2 ? 0x4d9be6 : 0xc7dcd0, 1).fillRect(3 + off, y + 3, 20, 1);
        }
        g.generateTexture('towel-stack', 28, 70);
        g.clear();
        // The stool it stands on.
        g.fillStyle(0x7a4528, 1).fillRect(1, 0, 24, 3).fillRect(3, 3, 2, 9).fillRect(21, 3, 2, 9);
        g.fillStyle(0xcd683d, 1).fillRect(2, 0, 22, 2);
        g.generateTexture('towel-stool', 26, 12);
        g.clear();
        // The same towels in a heap on the floor.
        const lie = [[2, 9, 0], [20, 10, 1], [38, 9, 0], [10, 5, 1], [28, 5, 0], [46, 10, 1], [18, 1, 0], [36, 1, 2]];
        for (const [x, y, c] of lie) {
            g.fillStyle(0x9babb2, 1).fillRoundedRect(x, y, 20, 6, 2);
            g.fillStyle([0xffffff, 0xf2f6f6, 0x8fd3ff][c], 1).fillRoundedRect(x + 1, y, 18, 5, 2);
        }
        g.generateTexture('towel-heap', 68, 16);
        g.destroy();
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (!nearby(s, d)) return;
        const dx = p.x - d.x, on = here(s, d) && Math.abs(p.y - d.y) < 70;
        const onFloor = p.body.blocked.down || p.body.touching.down;
        // A landing is a real one: she was a hand's breadth up at least (being set down somewhere is
        // none), and it is her body's feet that count (her picture is a frame behind as she lands).
        if (!onFloor) this.peak = Math.max(this.peak ?? 0, d.y - p.body.bottom);
        const landed = onFloor && !this.wasOnFloor && Math.abs(p.body.bottom - d.y) < 4 && (this.peak ?? 0) > 8;
        if (onFloor) this.peak = 0;
        this.wasOnFloor = onFloor;
        if (this.state === 'up') {
            // The tell: it sways, more the nearer she is.
            const close = on && Math.abs(dx) < 130;
            this.stack.setAngle(Math.sin(time / (close ? 150 : 520)) * (close ? 3.2 : 1));
            if (on && Math.abs(dx) < 48 && (landed || s.isLunging())) {
                this.state = 'falling';
                this.dir = dx < 0 ? -1 : 1;
                sfx.at(d.x, d.y).cloth();
                s.tweens.add({
                    targets: this.stack, angle: this.dir * 86, duration: 360, ease: 'Quad.easeIn',
                    onComplete: () => this.down(),
                });
            }
        } else if (this.state === 'down' && (Math.abs(dx) > 560 || s.route !== 'inside')) {
            // Stacked again behind her back.
            this.state = 'up';
            this.stack.setVisible(true).setAngle(0);
            this.heap.setVisible(false);
        }
    }

    down() {
        const s = this.scene, p = s.player, d = this.def;
        this.state = 'down';
        const cx = d.x + this.dir * 36;
        this.stack.setVisible(false);
        this.heap.setVisible(true).setPosition(cx, d.y);
        sfx.at(cx, d.y).towelFall();
        if (here(s, d) && Math.abs(p.x - cx) < 38 && p.y > d.y - 40 && !s.lungeSafe()) {
            // Under it: only her hair shows for a moment.
            this.heap.setPosition(p.x, d.y - 26).setScale(1, 2.6);
            s.tweens.add({ targets: this.heap, y: d.y, scaleY: 1, duration: 900, delay: 500, ease: 'Bounce.easeOut' });
            if (this.world.carry) this.world.carryBox.spill(d.x, false, 'towels');
            else s.scareContact(d.x, 'towels');
        }
    }
}

// A ceiling sprinkler being tested (population: `haz_sprinkler`): every `period` seconds it drips
// for a moment (the tell), then rains for `on` seconds on the two metres under it: "Drenched".
export class Sprinkler {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, y, top, half, period, on, offset }
        this.head = s.add.graphics().setDepth(D.decor + 0.3);
        this.head.fillStyle(0x9babb2, 1).fillRect(def.x - 4, def.top + 8, 8, 2).fillRect(def.x - 1, def.top + 10, 2, 3);
        this.head.fillStyle(0xe83b3b, 1).fillRect(def.x - 1, def.top + 13, 2, 2);
        this.head.fillStyle(0xc7dcd0, 1).fillRect(def.x - 3, def.top + 15, 6, 1);
        this.rain = s.add.graphics().setDepth(D.player + 0.3);
        world.add([this.head, this.rain]);
        this.wet = 0;
    }

    // Where it is in its round: 'tell', 'on' or 'off'.
    phase(time) {
        const d = this.def, t = (time / 1000 + d.offset) % d.period;
        return t < 0.8 ? 'tell' : t < 0.8 + d.on ? 'on' : 'off';
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def, g = this.rain.clear();
        // (Out on the ship's side the hallways are behind its plating.)
        if (!nearby(s, d) || s.route === 'promenade') return;
        const phase = this.phase(time), top = d.top + 16;
        // (Its sound, once in each round: the ticks of the tell, then its rain for what is left of it.)
        const round = (time / 1000 + d.offset) / d.period, key = phase + Math.floor(round);
        if (key !== this.sounded) {
            this.sounded = key;
            if (phase === 'tell') sfx.at(d.x, d.y).tick();
            else if (phase === 'on') sfx.at(d.x, d.y).spray(Math.max(0.2, 0.8 + d.on - (round % 1) * d.period));
        }
        if (phase === 'tell') {
            // Three slow drops.
            const y = top + ((time * 0.3) % (d.y - top));
            g.fillStyle(0x8fd3ff, 1).fillRect(d.x - 1, y, 2, 4);
            g.fillStyle(0xffffff, 1).fillRect(d.x - 1, y, 1, 1);
        } else if (phase === 'on') {
            this.wet = 1;
            for (let i = 0; i < 22; i++) {
                const k = (i * 0.618034) % 1, spread = (k * 2 - 1) * d.half;
                const f = ((time * 0.42 + i * 53) % 112) / 112;
                const x = d.x + spread * (0.25 + 0.75 * f), y = top + f * (d.y - top);
                g.fillStyle(i % 3 ? 0x8fd3ff : 0xffffff, 0.95).fillRect(x, y, 1, 5);
            }
            for (let i = 0; i < 6; i++) {
                const x = d.x - d.half + ((time * 0.11 + i * 41) % (d.half * 2));
                g.fillStyle(0xffffff, 0.8).fillRect(x, d.y - 2 - (Math.floor(time / 70 + i) % 2), 2, 1);
            }
            if (here(s, d) && Math.abs(p.x - d.x) < d.half - 5 && !s.gliding) {
                if (this.world.carry) this.world.carryBox.spill(d.x, false, 'sprinkler');
                else s.scareContact(d.x, 'sprinkler');
            }
        } else {
            this.wet = Math.max(0, this.wet - dt / 2.2);
        }
        // The puddle it leaves, drying.
        if (this.wet > 0) g.fillStyle(0x8fd3ff, 0.35 * this.wet).fillEllipse(d.x, d.y - 1, d.half * 2 - 6, 4);
    }
}

// A cabin door that flies open as she comes by (population: `haz_swing`): the handle rattles (the
// tell), then the door swings out across the corridor: "Bonked" if she is at it. Whoever opened it
// looks out, and shuts it again. It takes a cabin door's place.
export class SwingDoor {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, y, reach, delay (s), who }
        this.shut = s.add.image(def.x, def.y, 'shipart', 'door-cabin-bg').setOrigin(0.5, 1).setDepth(D.decor + 0.1);
        this.dark = s.add.rectangle(def.x, def.y - 2, 28, 70, 0x2e222f).setOrigin(0.5, 1).setDepth(D.decor + 0.1).setVisible(false);
        this.leaf = s.add.image(def.x + 14, def.y, 'shipart', 'door-cabin').setOrigin(0, 1).setDepth(D.props + 0.2).setTint(0xd9c4b8).setVisible(false);
        world.add([this.shut, this.dark, this.leaf]);
        this.who = world.people.add({ id: `${def.id}_who`, who: def.who, x: def.x - 2, y: def.y - 2, route: 'inside', face: -1, idle: 'idle', layer: 'back', owned: true });
        if (this.who) this.who.gone = true;
        this.state = 'shut';
        this.armed = true;
        this.at = 0;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (!nearby(s, d)) return;
        const dx = p.x - d.x, within = here(s, d) && Math.abs(p.y - d.y) < 40 && Math.abs(dx) < d.reach;
        if (this.state === 'shut') {
            if (!within && time > this.at) this.armed = true;
            if (within && this.armed) {
                this.armed = false;
                this.state = 'rattle';
                this.at = time + d.delay * 1000;
                this.rattleAt = time + 300;
                sfx.at(d.x, d.y).rattle();
            }
        } else if (this.state === 'rattle') {
            this.shut.x = d.x + (Math.floor(time / 45) % 2 ? 1 : -1);
            if (time > this.at) {
                // Open: the leaf swings out toward us and across the corridor.
                this.state = 'burst';
                this.at = time + 380;
                this.shut.setVisible(false).setX(d.x);
                this.dark.setVisible(true);
                this.leaf.setVisible(true).setScale(0.2, 1);
                s.tweens.add({ targets: this.leaf, scaleX: 0.42, duration: 220, ease: 'Back.easeOut' });
                sfx.at(d.x, d.y).doorBang();
                if (this.who) {
                    this.who.gone = false;
                    this.who.dir = dx < 0 ? -1 : 1;
                    this.world.people.place(this.who);
                    this.world.people.refresh();
                }
            } else if (time > this.rattleAt) {
                // (The handle again, while it shakes.)
                this.rattleAt = time + 300;
                sfx.at(d.x, d.y).rattle();
            }
        } else if (this.state === 'burst') {
            if (here(s, d) && Math.abs(p.y - d.y) < 40 && dx > -18 && dx < 34) {
                this.state = 'open';
                this.at = time + 1500;
                if (this.world.carry) this.world.carryBox.spill(d.x + 20, false, 'door');
                else s.scareContact(d.x + 14, 'door');
            } else if (time > this.at) {
                this.state = 'open';
                this.at = time + 1500;
            }
        } else if (this.state === 'open' && time > this.at) {
            this.state = 'shut';
            this.at = time + 1500;
            this.shut.setVisible(true);
            this.dark.setVisible(false);
            this.leaf.setVisible(false);
            if (this.who) {
                this.who.gone = true;
                this.world.people.refresh();
            }
            sfx.at(d.x, d.y).doorShut();
        }
    }
}

// A cabin door with a "Do Not Disturb" card on its handle (population: `haz_dnd`). E at it: whoever
// is in is not dressed for visitors: "Startled". Left alone, nothing.
export class DndDoor {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x, y, who }
        this.shut = s.add.image(def.x, def.y, 'shipart', 'door-cabin').setOrigin(0.5, 1).setDepth(D.decor + 0.1);
        this.card = s.add.graphics().setDepth(D.decor + 0.12);
        this.card.fillStyle(0x2e222f, 1).fillRect(def.x + 7, def.y - 41, 7, 15);
        this.card.fillStyle(0xe83b3b, 1).fillRect(def.x + 8, def.y - 40, 5, 13);
        this.card.fillStyle(0xffffff, 1).fillRect(def.x + 9, def.y - 39, 3, 2).fillRect(def.x + 9, def.y - 34, 3, 1).fillRect(def.x + 9, def.y - 32, 3, 1);
        this.dark = s.add.rectangle(def.x, def.y - 2, 28, 70, 0x2e222f).setOrigin(0.5, 1).setDepth(D.decor + 0.1).setVisible(false);
        world.add([this.shut, this.card, this.dark]);
        this.who = world.people.add({ id: `${def.id}_who`, who: def.who, x: def.x, y: def.y - 2, route: 'inside', face: -1, layer: 'back', owned: true });
        if (this.who) this.who.gone = true;
        this.busy = false;
        world.things.push({ ...def, items: [], reach: 16, interact: () => this.knock() });
    }

    // Her cry within three metres of it brings them to the door, and that is a fright even in a
    // lunge (it is no contact); with a tray, a spill.
    heard() {
        const d = this.def;
        if (!this.world.hears(d.x, d.y, 'inside', 3 * M)) return;
        this.scene.time.delayedCall(300, () => this.knock(true, true));
    }

    // (`heard`: a clatter outside, or her cry, brought them to the door: a fright only if she is by
    // it; `cried`: her own cry did, and nothing forgives it; `look`: a tangerine in the trays did,
    // and they look about and see nobody: no fright, wherever she is.)
    knock(heard, cried = false, look = false) {
        const s = this.scene, p = s.player, d = this.def;
        if (this.busy || (this.world.carry && !heard)) return false;
        this.busy = true;
        // Her knuckles on it (E), the door, and whoever is in.
        if (!heard) sfx.knock();
        sfx.at(d.x, d.y).door();
        if (this.who) sfx.at(d.x, d.y).oh();
        this.shut.setVisible(false);
        this.card.setVisible(false);
        this.dark.setVisible(true);
        if (this.who) {
            this.who.gone = false;
            this.who.dir = p.x < d.x ? -1 : 1;
            this.world.people.place(this.who);
            this.world.people.refresh();
            if (look) {
                // (This way and that, at the empty corridor.)
                this.world.people.idle(this.who);
                for (let i = 1; i <= 3; i++) s.time.delayedCall(i * 420, () => { this.who.dir = -this.who.dir; this.world.people.place(this.who); });
            } else this.world.people.play(this.who, 'shriek');
        }
        const by = !look && (!heard || (Math.abs(p.x - d.x) < 3 * M && Math.abs(p.y - d.y) < 60));
        if (by && cried && this.world.carry) this.world.carryBox.spill(d.x, false, 'dnd', { force: cried });
        else if (by && !this.world.carry) s.scareContact(d.x + (p.x < d.x ? 12 : -12), 'dnd', { force: cried });
        s.time.delayedCall(look ? 1900 : 1700, () => {
            this.shut.setVisible(true);
            this.card.setVisible(true);
            this.dark.setVisible(false);
            if (this.who) {
                this.who.gone = true;
                this.world.people.refresh();
            }
            sfx.at(d.x, d.y).doorShut();
            this.busy = false;
        });
        return true;
    }

    update() {}
}

// --- Region 1's decks filled (docs/plan-three-uses.md §4.2; step 4, 2026-11-16) ------------------

// A suitcase on its wheels in a cabin corridor (population: `haz_suitcase_4`): it rolls to and fro
// between two door frames with the ship's slow roll, slowing at each end with a creak before it
// comes back. Hop it: walked into, it is a bump. In a lunge it is sent rolling to the corridor's
// end, and stays there. A thrown tangerine only bounces off it.
export class Roller {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        // (Its roll short of any door or wall across the deck: ShipScene `stopShort`.)
        const span = s.spanOn((def.x0 + def.x1) / 2, def.x0, def.x1, def.y, Roller.HALF);
        this.def = def = { ...def, x0: span.lo, x1: span.hi };   // { x0, x1, y, v (m/s, its fastest) }
        // (Its handle pulled up: the one she rides in her gag, 6b, cut from that picture.)
        this.sprite = s.add.image(def.x0, def.y, 'things', 'suitcase-rolling').setOrigin(0.5, 1).setDepth(D.props + 0.03);
        world.add([this.sprite]);
        this.mid = (def.x0 + def.x1) / 2;
        this.half = (def.x1 - def.x0) / 2;
        this.period = 2 * Math.PI * this.half / (def.v * M);    // seconds for a roll there and back
        this.x = def.x0;
        this.phase = 0;
        this.parked = false;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (!nearby(s, d) || this.parked) return;
        const was = Math.sin(this.phase);
        this.phase += dt * 2 * Math.PI / this.period;
        this.x = this.mid - this.half * Math.cos(this.phase);
        // (At an end: the creak, as it stops and comes back.)
        if (Math.sign(Math.sin(this.phase)) !== Math.sign(was)) sfx.at(this.x, d.y).creak();
        this.sprite.setX(this.x).setAngle(Math.sin(this.phase) * 4);
        // Her against it (its height is a hop's).
        if (!here(s, d) || Math.abs(p.x - this.x) > PLAYER.bodyWidth / 2 + 8 || p.y <= d.y - Roller.HOP || p.y - PLAYER.bodyHeight >= d.y) return;
        if (s.isLunging()) {
            // Sent rolling to the corridor's end, the way she was going; it stays there.
            this.parked = true;
            const away = p.body.velocity.x < 0 ? -1 : 1;
            s.smash(this.x, d.y - 16, false);
            sfx.at(this.x, d.y).creak();
            s.tweens.add({ targets: this.sprite, x: s.stopShort(this.x, away > 0 ? d.x1 + 3 * M : d.x0 - 3 * M, d.y, Roller.HALF), angle: away * 12, duration: 1400, ease: 'Quad.easeOut',
                onComplete: () => this.sprite.setAngle(0) });
        } else if (this.world.carry) {
            this.world.carryBox.spill(this.x, false, 'suitcase', { vx: Math.sin(this.phase) * 50 });
        } else {
            // (Rolled into her back, she rides it to the end of its roll, 6b: it waits meanwhile.)
            // (Standing at an end of its roll, it sets off for the other end with her.)
            const vx = Math.sin(this.phase) * this.half * 2 * Math.PI / this.period;
            const dir = Math.abs(vx) > 5 ? Math.sign(vx) : this.x < this.mid ? 1 : -1;
            const ride = { x: this.x, y: d.y, dir, v: vx, endX: dir > 0 ? d.x1 : d.x0,
                           hide: () => { this.parked = true; this.sprite.setVisible(false); },
                           show: () => { this.parked = false; this.sprite.setVisible(true).setAngle(0); } };
            s.scareContact(this.x, 'suitcase', { vx, ride });
        }
    }
}
// Her feet over this, she clears it: its body (the handle is a thin rail she passes).
Roller.HOP = 30;
Roller.HALF = 12;               // px from its middle to its front

// The dog's lead (the dog and its owner made together, the user, 2026-11-17: "the lady and the dog
// are loosely connected, the leash looks weird and glitches on its connecting ends"): where it
// leaves her fist and where it is clipped to the collar, px from the sprite's foot (in front, up),
// measured in every frame of their clips on the people's sheet (her fist is still in all of her
// idle's); the picture's own colours; how high its lowest point hangs over the carpet; where the
// fruit is in the dog's mouth.
const LEAD = {
    fist: [7.5, 32],
    collar: { stand: [2.5, 12],
              walk: [[0.5, 13], [0.5, 12], [0.5, 12], [0.5, 13], [0.5, 13], [0.5, 12], [0.5, 12], [1.5, 13]],
              run: [[4.5, 12], [4.5, 12], [4.5, 9], [4.5, 9], [4.5, 10], [3.5, 11]],
              sit: [[2.5, 12], [3.5, 11], [3.5, 11], [2.5, 11], [2.5, 11], [2.5, 11], [2.5, 11], [2.5, 11], [2.5, 11]] },
    core: 0x6e2727, edge: 0x2e222f,
    low: 3,
    mouth: [10, 11],
};
// A point of a person's picture in the world: `at` px in front of its middle (the way it faces) and
// up from its feet, on the px the sprite is drawn at.
// (By where the person is, not its sprite, which is only placed while she is near.)
const leadEnd = (p, at) => ({ x: Math.round(p.x) + (p.dir < 0 ? -at[0] : at[0]), y: p.sprite.y - at[1] });
// A straight run of points from a to b, one a px.
const lineOf = (a, b) => {
    const n = Math.max(1, Math.abs(b.x - a.x), Math.abs(b.y - a.y));
    return Array.from({ length: n + 1 }, (_, i) => ({ x: a.x + (b.x - a.x) * i / n, y: a.y + (b.y - a.y) * i / n }));
};

// A small dog on a long lead (population: `haz_dog_4`), its owner in her cabin's doorway holding
// the other end. The dog trots about within the lead's reach and sits now and then; where the lead
// sags to the carpet it is a line to hop: run into, she trips on it (the user, 2026-11-16): with a
// tangerine on her she stumbles forward and it flies on ahead of her; without, she falls flat on
// her belly, dizzy, and goes back to her checkpoint (`tripped`). At first it held her back like a
// wall, then it was a stagger with nothing lost. A
// tangerine rolled within its reach it fetches and brings back to her feet: not spent; three
// fetches and its owner hands her the tennis ball. Her cry: it howls back and runs round its
// owner's legs, the lead lying flat 5 s. In a lunge it jumps aside.
export class Fetcher {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x: the doorway, y, who: the owner, reach: px, gives }
        // (Her cabin's door standing open behind her.)
        world.add([s.add.image(def.x, def.y, 'shipart', 'door-cabin-ajar').setOrigin(0.5, 1).setDepth(D.decor + 0.1)]);
        this.owner = world.people.add({ id: `${def.id}_owner`, who: def.who, x: def.x, y: def.y, route: 'inside', face: 1,
                                        idle: 'idle', layer: 'back', owned: true });
        this.dog = world.people.add({ id: `${def.id}_dog`, who: 'dog', x: def.x + 60, y: def.y, route: 'inside', face: 1, owned: true });
        // (Over the dog: from behind it the lead runs along its back to the collar, as in their picture;
        // and under her, so that her fist closes over its end.)
        this.lead = s.add.graphics().setDepth(D.props + 0.06);
        this.owner.sprite.setDepth(D.props + 0.07);
        world.add([this.lead]);
        this.state = 'sit';
        this.at = 0;
        this.fetches = 0;
        this.flatUntil = 0;
    }

    // Where the lead leaves her fist, and where it is clipped to the dog's collar: measured in every
    // frame of their clips (LEAD), in world px; the sprites are drawn at whole px (roundPixels).
    hand() {
        return leadEnd(this.owner, LEAD.fist);
    }

    collar() {
        const g = this.dog, f = Number(g.sprite.frame.name);
        let at = LEAD.collar.stand;
        for (const [clip, frames] of Object.entries(g.meta.anims)) {
            const i = frames.indexOf(f);
            if (i >= 0 && LEAD.collar[clip]) at = LEAD.collar[clip][i] ?? at;
        }
        return leadEnd(g, at);
    }

    // Where she meets the lead (`trip`), as it always was: a little over halfway from her hand to the
    // dog; the lead's lowest point, LEAD.low px over the carpet (the user, 2026-11-17: hung at her
    // waist, it could not trip her; "make the leash hang lower").
    sag() {
        const h = this.hand(), c = this.collar();
        return { x: h.x + (c.x - h.x) * 0.62, y: this.def.y - LEAD.low };
    }

    // The lead's line, point by point from her fist to the collar: down from her fist to its lowest
    // point and up again to the collar, each side a curve level at the bottom; or after her cry along
    // the carpet.
    curve(time) {
        const h = this.hand(), c = this.collar(), floor = this.def.y - 1;
        if (time < this.flatUntil) {
            const foot = { x: h.x + Math.sign(c.x - h.x) * 3, y: floor };
            return [...lineOf(h, foot), ...lineOf(foot, { x: c.x, y: floor }), ...lineOf({ x: c.x, y: floor }, c)];
        }
        const m = this.sag();
        const hang = (end) => {
            const n = Math.ceil(Math.abs(m.x - end.x) + Math.abs(m.y - end.y)) + 1;
            return Array.from({ length: n + 1 }, (_, i) => {
                const t = i / n;
                return { x: end.x + (m.x - end.x) * t, y: m.y + (end.y - m.y) * (1 - t) ** 2 };
            });
        };
        return [...hang(h), ...hang(c).reverse()];
    }

    go(state, ms = 0) {
        this.state = state;
        this.at = this.scene.time.now + ms;
    }

    // Where the lead lets it go: its reach either way from the doorway, short of any door or wall
    // across the deck (ShipScene `stopShort`: the lead does not go through walls).
    range() {
        const d = this.def;
        return (this.span ??= this.scene.spanOn(d.x, d.x - d.reach, d.x + d.reach, d.y, 10));
    }

    // Her cry: a howl back at her, and round its owner's legs: the lead lies flat a while.
    heard() {
        const d = this.def, s = this.scene;
        if (!this.dog || !this.world.hears(this.dog.x, d.y) || this.state === 'fetch' || this.state === 'back') return;
        sfx.at(this.dog.x, d.y).howl();
        this.flatUntil = s.time.now + 5000;
        this.target = d.x + 14;
        this.go('wind', 5000);
    }

    // A tangerine on the carpet within its reach: it fetches it.
    offered(t) {
        const d = this.def, s = this.scene, g = this.dog;
        if (!g || this.state === 'fetch' || this.state === 'back' || this.state === 'wind' || t.route !== 'inside') return false;
        const r = this.range();
        if (Math.abs(t.img.y + 3 - d.y) > 6 || t.img.x < r.lo || t.img.x > r.hi) return false;
        this.fruit = s.loose.claim(t).setAngle(0);
        this.target = this.fruit.x;
        sfx.at(g.x, d.y).bark();
        this.go('fetch');
        return true;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def, g = this.dog, P = this.world.people;
        if (!g || !nearby(s, d)) return;
        const speed = { walk: 40, fetch: 150, back: 130, wind: 120 }[this.state] ?? 0;
        if (speed) {
            if (this.state === 'back') this.target = p.x - (p.x > g.x ? 14 : -14);
            const r = this.range(), to = Phaser.Math.Clamp(this.target, r.lo, r.hi);
            const step = Math.sign(to - g.x) * Math.min(Math.abs(to - g.x), speed * dt);
            if (step) g.dir = step > 0 ? 1 : -1;
            g.x += step;
            P.anim(g, this.state === 'walk' ? 'walk' : 'run');
            const there = Math.abs(to - g.x) < 1;
            if (this.state === 'fetch' && there) {
                // In its mouth, and back to her.
                this.go('back');
            } else if (this.state === 'back') {
                this.fruit?.setPosition(g.x + g.dir * LEAD.mouth[0], d.y - LEAD.mouth[1]);
                if (there || Math.abs(p.x - g.x) < 22) this.drop();
            } else if (this.state === 'walk' && there) {
                this.go('sit', Phaser.Math.Between(1800, 3800));
            } else if (this.state === 'wind' && time > this.at) {
                this.go('sit', 1200);
            }
        } else if (this.state === 'sit') {
            if (!P.anim(g, 'sit', { loop: false })) g.sprite.setFrame(g.meta.stand);
            if (time > this.at) {
                const r = this.range();
                this.target = Phaser.Math.Between(r.lo + 10, r.hi - 10);
                this.go('walk');
            }
        } else if (this.state === 'aside' && time > this.at) {
            this.go('sit', 1500);
        }
        P.place(g);
        const o = this.owner, face = g.x < o.x ? -1 : 1;
        if (o.dir !== face) {
            o.dir = face;
            P.place(o);
        }
        this.drawLead(time);
        this.trip(p, time);
    }

    // The tangerine at her feet, hers again; three of them and its owner hands her the tennis ball.
    drop() {
        const s = this.scene, d = this.def;
        const img = this.fruit;
        this.fruit = null;
        if (img) {
            s.loose.make({ x: img.x, y: d.y - 3, route: 'inside' }, true);
            img.destroy();
        }
        this.fetches += 1;
        this.go('sit', 2500);
        if (this.fetches >= 3 && !this.world.save.keeps.includes(d.gives)) {
            const o = this.owner;
            this.world.pop(o.x, d.y - PLAYER.height - 6, 'heart', 1500);
            sfx.at(o.x, d.y).giggle();
            s.time.delayedCall(700, () => this.world.giveKeep(d.gives, s.player.x, s.player.y - PLAYER.height));
        }
    }

    // The lead in the picture's own pixels: a line of its red-brown with its dark outline round it,
    // down from her fist to just over the carpet and up to the collar, or after her
    // cry round her feet and along the carpet.
    drawLead(time) {
        const floor = this.def.y - 1, pts = this.curve(time);
        // Whole px, joined side by side (no diagonal gaps), then a dark px under each: 2 px thick (the
        // picture's 3, its outline on both sides, was too thick, the user).
        const core = new Map();
        let last = null;
        for (const q of pts) {
            const x = Math.floor(q.x), y = Math.round(q.y);
            if (last && last.x !== x && last.y !== y) core.set(`${x},${last.y}`, [x, last.y]);
            core.set(`${x},${y}`, [x, y]);
            last = { x, y };
        }
        // (Lying round her feet after her cry the dog is at her feet too: the lead under it then.)
        const g = this.lead.clear().setDepth(this.scene.DEPTH.props + (time < this.flatUntil ? 0.04 : 0.06));
        g.fillStyle(LEAD.edge, 1);
        for (const [x, y] of core.values()) {
            if (y + 1 <= floor && !core.has(`${x},${y + 1}`)) g.fillRect(x, y + 1, 1, 1);
        }
        g.fillStyle(LEAD.core, 1);
        for (const [x, y] of core.values()) g.fillRect(x, y, 1, 1);
    }

    // The lead where it lies on the carpet: crossed on her feet, she trips on it (a stagger, slowed
    // a moment); hopped, or in a lunge, it is nothing.
    trip(p, time) {
        const s = this.scene, d = this.def, m = this.sag();
        if (s.isLunging() && here(s, d) && Math.abs(p.x - this.dog.x) < 20 && this.state !== 'aside') this.jumpAside(p);
        const side = Math.sign(p.x - m.x) || 1;
        // (Only crossing the line itself, from right beside it: a teleport or a fright's walk back
        // across it is no trip.)
        const crossed = this.side && side !== this.side && Math.abs(p.x - m.x) < 24;
        if (crossed && time >= this.flatUntil && here(s, d) && !s.isLunging() && p.y >= d.y - 6) {
            sfx.at(this.dog.x, d.y).bark();
            // (From behind her: she goes on the way she was going, forward.)
            s.scareContact(p.x - side * 10, 'lead');
        }
        this.side = side;
    }

    jumpAside(p) {
        const s = this.scene, g = this.dog, d = this.def;
        this.go('aside', 900);
        sfx.at(g.x, d.y).bark();
        const r = this.range(), to = Phaser.Math.Clamp(g.x + (g.x < p.x ? -1 : 1) * 40, r.lo, r.hi);
        s.tweens.add({ targets: g, x: to, duration: 300, ease: 'Quad.easeOut' });
    }
}

// The paper round (population: `haz_papers_5`): a steward with a stack of folded papers walks a
// cabin corridor and skims one along the carpet to each door. A paper sliding is a thing to hop:
// stepped on, she slips, and it shoots on from under her foot to its door. A moment after it
// stops there, the door opens a crack and a hand takes it in (the user, 2026-11-16: lying there
// it looked like a thing to pick up). At the end of the round he turns and walks back. Her cry:
// he stands aside a while. A tangerine thrown to him: he catches it and
// stands aside to eat it (spent). In a lunge she is through the papers.
export class Skimmer {
    static SPEED = 5.5 * M;     // a paper's slide, px/s (about 260)
    static BRAKE = Skimmer.SPEED * Skimmer.SPEED / M;   // stopping in the last half metre to its door
    static REACH = 9;           // px between its middle and hers when her foot is on it
    constructor(world, def) {
        const s = world.scene;
        this.world = world;
        this.scene = s;
        // (His round is one corridor's: short of any door or wall across the deck, ShipScene `stopShort`.)
        const span = s.spanOn((def.x0 + def.x1) / 2, def.x0, def.x1, def.y, 10);
        this.def = def = { ...def, x0: span.lo, x1: span.hi };   // { x0, x1, y, v (m/s), who, doors: [x] }
        this.p = world.people.add({ id: def.id, who: def.who, x: def.x0, y: def.y, route: 'inside', face: 1, owned: true });
        this.x = def.x0;
        this.dir = 1;
        this.until = 0;
        this.papers = [];
        this.next = 0;              // the door whose paper is next
    }

    heard() {
        const s = this.scene, d = this.def;
        if (!this.p || !this.world.hears(this.x, d.y)) return;
        this.until = Math.max(this.until, s.time.now + CRY.startleMs);
        this.world.pop(this.x, d.y - PLAYER.height - 6, 'alert', 1200);
        sfx.at(this.x, d.y).oh();
    }

    // A tangerine thrown to him: caught, and eaten standing aside.
    offered(t) {
        const s = this.scene, d = this.def, p = this.p;
        if (!p || !t.thrown || this.flicking || !s.loose.near(t, this.x, d.y, 14, 50)) return false;
        const img = s.loose.claim(t).setDepth(p.sprite.depth + 0.01);
        this.until = s.time.now + 8000;
        this.eating = true;
        sfx.at(this.x, d.y).take();
        this.world.people.eat(p, img, () => { this.eating = false; });
        return true;
    }

    update(dt, time) {
        const s = this.scene, her = s.player, d = this.def, P = this.world.people, p = this.p;
        if (!p || !nearby(s, d)) return;
        if (time >= this.until && !this.flicking) {
            this.x += this.dir * d.v * M * dt;
            if (this.x >= d.x1) { this.x = d.x1; this.dir = -1; this.until = time + 1200; this.next = 0; }
            else if (this.x <= d.x0) { this.x = d.x0; this.dir = 1; this.until = time + 1200; this.next = 0; }
            // A door's paper is sent from five metres short of it (the user: from further away), both
            // ways: going back he skims them to the doors behind him (the user: a constant obstacle).
            const doors = realDoors(s, d);
            const ahead = this.dir > 0 ? doors.filter(x => x - 5 * M >= d.x0) : doors.filter(x => x + 5 * M <= d.x1).reverse();
            const door = ahead[this.next];
            if (door !== undefined && (this.x - (door - this.dir * 5 * M)) * this.dir >= 0) this.flick(door);
        }
        if (!this.flicking && !this.eating) {
            if (time < this.until) {
                p.sprite.anims.stop();
                p.sprite.setFrame(p.meta.stand);
            } else P.anim(p, 'walk');
        }
        p.x = this.x;
        p.dir = this.dir;
        P.place(p);
        this.slide(dt, her);
    }

    // He bends and sends one along the carpet to the door.
    flick(door) {
        const s = this.scene, d = this.def, p = this.p;
        this.next += 1;
        this.flicking = true;
        this.world.people.play(p, 'flick').then(() => { this.flicking = false; });
        s.time.delayedCall(220, () => {
            // (The paper the user picked of two generated, `assets/source/things/paper-sliding.png`;
            // its curled edge trailing, as in the first picture of her clips with it.)
            const dir = Math.sign(door - (this.x + this.dir * 10)) || 1;
            const img = s.add.image(this.x + this.dir * 10, d.y, 'things', 'paper-sliding').setOrigin(0.5, 1)
                .setFlipX(dir < 0).setDepth(s.DEPTH.props + 0.02);
            this.world.add([img]);
            sfx.at(this.x, d.y).paperSlide();
            this.papers.push({ img, v: Skimmer.SPEED, door, dir });
        });
    }

    // The papers on the carpet: sliding to their doors, where a hand takes each in.
    slide(dt, her) {
        const s = this.scene, d = this.def;
        for (const q of this.papers) {
            // Lying at its door until it is taken in, it is as slippery: stepped on, she slips (once).
            if (q.done) {
                if (!q.hit && !q.taking && this.under(q, her)) {
                    q.hit = true;
                    if (this.world.carry) this.world.carryBox.spill(q.img.x, false, 'papers', { vx: 0, lying: true });
                    else s.scareContact(q.img.x, 'papers', { vx: 0, lying: true, ride: this.onHer(q) });
                }
                continue;
            }
            const left = Math.abs(q.door - q.img.x);
            if (left < 0.5) {
                q.done = true;
                q.v = 0;
                q.img.x = q.door;
                s.time.delayedCall(2000, () => this.takeIn(q));
                continue;
            }
            // At a steady speed right to her foot (the user, 2026-11-17: slowing as it reached her,
            // her fall did not convince), braking only in its last half metre to its door.
            q.v = Math.min(Skimmer.SPEED, Math.sqrt(2 * Skimmer.BRAKE * left));
            q.img.x += q.dir * Math.min(Math.max(q.v, 20) * dt, left);
            // Under her foot as it slides: she slips (once); with a tangerine on her (no gag) it
            // goes on to its door.
            if (!q.hit && this.under(q, her)) {
                q.hit = true;
                // (From where it came: its middle may be a step past hers by the frame it is seen.)
                const from = q.img.x - q.dir * 20;
                if (this.world.carry) this.world.carryBox.spill(from, false, 'papers', { vx: q.dir * q.v });
                else s.scareContact(from, 'papers', { vx: q.dir * q.v, ride: this.onHer(q) });
            }
        }
    }

    // Her foot on a paper (not in a lunge: she is through them): its middle within a few px of
    // hers, where her clip's first picture has it (a foot on its near half).
    under(q, her) {
        const s = this.scene, d = this.def;
        return here(s, d) && !s.isLunging() && Math.abs(her.x - q.img.x) < Skimmer.REACH && her.y > d.y - 4;
    }

    // The paper that hit her is the one in her gag (4a, 4b): her clip is set down by where it is
    // (`x`), and the world's own taken away (the ship scene's `fallGag` calls `hide`).
    onHer(q) {
        return {
            x: q.img.x,
            hide: () => {
                q.gone = true;
                q.img.destroy();
                this.papers = this.papers.filter(o => o !== q);
            },
        };
    }

    // A paper at its door taken in (`world.handTakes`).
    takeIn(q) {
        const s = this.scene, d = this.def;
        if (q.gone) return;
        this.world.handTakes(q.door, d.y, [q.img], d.y - 2);
        q.taking = true;
        s.time.delayedCall(560, () => { this.papers = this.papers.filter(o => o !== q); });
    }
}


// The breakfast round (population: `haz_breakfast_5`; the user, 2026-11-16: the stewardess with a
// tray given a purpose, an obstacle): a room-service stewardess takes breakfast door to door. Her
// trolley parked a step short of a door, she takes a breakfast tray from it and carries it to the
// door in both hands (her `carry` walk; the tray is a picture of its own, `breakfast-tray`), knocks,
// and a hand takes the tray in; she walks back empty-handed and wheels the trolley on to the next
// door (and at the last, back again). Only doors that are drawn (`realDoors`). The trolley is a low
// thing to hop; walked into with a tray, she drops it with a crash (a fright). Her cry: she stops and
// stands aside a while. A tangerine thrown to her: she catches it and puts it on the next tray, in
// with the breakfast (spent). In a lunge she is spun round.
export class Breakfast {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { doors: [x], y, who }
        this.i = 0;                 // the door she is at, or going to
        this.dir = 1;
        this.p = world.people.add({ id: def.id, who: def.who, x: def.doors[0] - 80, y: def.y, route: 'inside', face: 1, owned: true });
        this.cartX = def.doors[0] - 46;
        this.x = this.cartX - HANDLE;
        // (Under her, a hair below her depth: her hands are on its handle.)
        this.cart = s.add.image(this.cartX, def.y, 'shipart', 'service-cart').setOrigin(0.5, 1).setDepth(D.props + 0.04);
        this.tray = world.image(0, 0, 'thing:breakfast-tray').setOrigin(0.5, 1).setVisible(false);
        world.add([this.cart, this.tray]);
        // (A low thing to hop: solid, as the other carts on the decks are.)
        this.zone = s.add.zone(this.cartX, def.y, this.cart.width - 6, this.cart.height - 3).setOrigin(0.5, 1);
        s.physics.add.existing(this.zone, true);
        // (In a lunge she is past it, as past her: the user, 2026-11-16.)
        world.solids.push({ id: `${def.id}_cart`, route: 'inside', zone: this.zone, items: [this.cart], through: true });
        this.state = 'push';
        this.until = 0;
        this.holding = false;
        this.d = { x: def.doors[0], y: def.y };
    }

    // (Only those she can wheel the trolley to from the first without a door across the deck: a
    // service cart does not go through one, ShipScene `stopShort`.)
    doors() {
        const s = this.scene, d = this.def;
        return (this.reach ??= realDoors(s, d).filter(x => s.stopShort(d.doors[0], x, d.y, 30) === x));
    }

    // Where the trolley stands for a door: a step short of it on the side she comes from.
    park() {
        return this.doors()[this.i] - this.dir * 46;
    }

    heard() {
        const s = this.scene, d = this.def;
        if (!this.p || !this.world.hears(this.x, d.y)) return;
        this.until = Math.max(this.until, s.time.now + CRY.startleMs);
        this.world.pop(this.x, d.y - PLAYER.height - 6, 'alert', 1200);
        sfx.at(this.x, d.y).oh();
    }

    // A tangerine thrown to her: caught, and onto the next tray, in with the breakfast.
    offered(t) {
        const s = this.scene, d = this.def;
        if (!this.p || !t.thrown || this.fruit || !s.loose.near(t, this.x, d.y, 14, 50)) return false;
        this.fruit = s.loose.claim(t).setAngle(0);
        sfx.at(this.x, d.y).take();
        return true;
    }

    walkTo(to, speed, dt) {
        const step = Math.sign(to - this.x) * Math.min(Math.abs(to - this.x), speed * dt);
        this.x += step;
        return step;
    }

    update(dt, time) {
        const s = this.scene, her = s.player, d = this.def, P = this.world.people, p = this.p;
        const doors = this.doors();
        if (!p || !doors.length || !nearby(s, this.d)) return;
        const door = doors[this.i], speed = 0.8 * M;
        let moving = 0;
        if (time >= this.until) {
            if (this.state === 'push') {
                // Wheeling the trolley on to the next door, she behind it.
                const to = this.park(), step = Math.sign(to - this.cartX) * Math.min(Math.abs(to - this.cartX), speed * dt);
                this.cartX += step;
                this.x = this.cartX - this.dir * HANDLE;
                moving = step;
                if (!step) {
                    // A tray from the trolley.
                    this.state = 'carry';
                    this.holding = true;
                    sfx.at(this.cartX, d.y).take();
                }
            } else if (this.state === 'carry') {
                moving = this.walkTo(door - this.dir * 14, speed, dt);
                if (!moving) this.serve(door);
            } else if (this.state === 'return') {
                moving = this.walkTo(this.cartX - this.dir * HANDLE, speed, dt);
                if (!moving) {
                    // On to the next door; past the last, back the other way.
                    if (this.i + this.dir < 0 || this.i + this.dir >= doors.length) this.dir = -this.dir;
                    this.i = Phaser.Math.Clamp(this.i + this.dir, 0, doors.length - 1);
                    this.state = 'push';
                }
            }
        }
        p.x = this.x;
        p.dir = moving ? Math.sign(moving) : this.dir;
        // (Bumped from behind, she turns round to see.)
        if (time < (this.turnUntil ?? 0)) p.dir = this.turnTo;
        // (Wheeling her trolley, her hands on its handle, `push`: stopped, she holds its first frame.)
        const clip = this.holding ? 'carry' : this.state === 'push' && p.meta.anims.push ? 'push' : 'walk';
        if (moving) P.anim(p, clip);
        else if (clip !== 'walk') {
            p.sprite.anims.stop();
            p.sprite.setFrame(p.meta.anims[clip][0]);
        } else if (p.state !== 'acting') P.idle(p);
        P.place(p);
        this.cart.setX(this.cartX).setFlipX(this.dir < 0);
        this.zone.x = this.cartX;
        this.zone.body.updateFromGameObject();
        this.holdTray(p);
        this.bump(her, time);
        this.trolleyHit(her, time, this.state === 'push' ? moving : 0, dt);
    }

    // Her trolley met (the user, 2026-11-17: most of the round she wheels it): she runs into it,
    // wheeled or parked, or it is wheeled into her, on the floor by it (over it in a jump, or on it,
    // nothing). The stewardess stops a while; the trip is drawn under the world's own trolley
    // (`ride.hide()` raises it over her), set down by its middle.
    trolleyHit(her, time, step, dt) {
        const s = this.scene, d = this.def, D = s.DEPTH;
        if (!here(s, d) || time < (this.bumpedAt ?? 0) + 2500) return;
        if (her.y < d.y - 6 || her.y - PLAYER.bodyHeight >= d.y) return;
        const dx = her.x - this.cartX, side = Math.sign(dx) || 1;
        if (Math.abs(dx) > (this.cart.width - 6) / 2 + PLAYER.bodyWidth / 2 + 2) return;
        const b = her.body, pressing = side < 0 ? b.touching.right || b.blocked.right : b.touching.left || b.blocked.left;
        const herInto = pressing || b.velocity.x * -side > 20, cartInto = step && Math.sign(step) === side;
        if (!herInto && !cartInto) return;
        this.bumpedAt = time;
        this.until = time + 1500;
        // (Someone just past it, where a trip over it would land: the stewardess behind it as she
        // wheels it, or at the door it is parked by.)
        const crowded = (this.x - this.cartX) * -side > 0 && Math.abs(this.x - this.cartX) < 90;
        const cart = this.cart;
        s.scareContact(this.cartX, 'trolley', { vx: cartInto ? step / dt : 0, dir: this.dir, crowded, ride: {
            x: this.cartX, y: d.y, hide: () => cart.setDepth(s.player.depth + 0.02), show: () => cart.setDepth(D.props + 0.04) } });
    }

    // The tray in her hands, at their height in each frame of her carry (TRAY_HANDS), in front of
    // her; a tangerine she caught on it.
    holdTray(p) {
        const show = this.holding && !this.giving;
        this.tray.setVisible(show);
        if (!show) {
            if (this.fruit && !this.giving) this.fruit.setPosition(this.cartX + 4, this.def.y - this.cart.height - 3).setDepth(this.cart.depth + 0.01);
            return;
        }
        const i = p.sprite.anims.isPlaying ? (p.sprite.anims.currentFrame?.index ?? 1) - 1 : 0;
        const [hx, hy] = TRAY_HANDS[i] ?? TRAY_HANDS[0];
        this.tray.setPosition(p.x + p.dir * hx, p.y - hy).setFlipX(p.dir < 0).setDepth(p.sprite.depth + 0.01);
        this.fruit?.setPosition(this.tray.x + p.dir * 9, this.tray.y - 3).setDepth(this.tray.depth + 0.01);
    }

    // At the door: a knock, a hand takes the tray in (and the tangerine on it), and back.
    serve(door) {
        const s = this.scene, d = this.def;
        this.state = 'serving';
        sfx.at(door, d.y).knock();
        s.time.delayedCall(170, () => sfx.at(door, d.y).knock());
        s.time.delayedCall(550, () => {
            // (Knocked out of her hands while she knocked: nothing to hand over.)
            if (this.state !== 'serving' || !this.holding) return;
            // (The tray handed over: a copy, taken from her hands where they hold it (`shrink`: slid
            // to the door it crossed her), her hands held out until it is gone, `giving`.)
            const given = this.world.image(this.tray.x, this.tray.y, 'thing:breakfast-tray').setOrigin(0.5, 1)
                .setFlipX(this.tray.flipX).setDepth(this.tray.depth);
            this.world.add([given]);
            const fruit = this.fruit;
            this.fruit = null;
            this.giving = true;
            this.world.handTakes(door, d.y, [given, fruit].filter(Boolean), this.tray.y - 1, () => {
                this.state = 'return';
                this.until = s.time.now + 300;
            }, { shrink: true, took: () => {
                this.holding = false;
                this.giving = false;
            } });
        });
    }

    // Walked into: with a tray in her hands she drops it with a crash; a fright either way (with a
    // tray of her own, a spill).
    bump(her, time) {
        const s = this.scene, d = this.def;
        if (!here(s, d) || time < (this.bumpedAt ?? 0) + 2500) return;
        // (A tray in her hands meets her first: on its side, from its front edge, TRAY_HANDS' reach
        // and half the tray, 34 px ahead of her middle; else her body's edge, 13 px.)
        const ahead = (her.x - this.x) * (this.p?.dir ?? 1) > 0, carrying = this.holding && !this.giving;
        const reach = carrying && ahead ? PLAYER.bodyWidth / 2 + 34 : PLAYER.bodyWidth / 2 + 13;
        if (Math.abs(her.x - this.x) > reach || her.y <= d.y - 40 || her.y - PLAYER.bodyHeight >= d.y) return;
        this.bumpedAt = time;
        if (s.isLunging()) {
            // Spun round, and on again.
            s.time.addEvent({ delay: 90, repeat: 7, callback: () => this.p.sprite.setFlipX(!this.p.sprite.flipX) });
            sfx.at(this.x, d.y).oh();
            return;
        }
        // (With a tray in her hands, her gag with it: 10a, 10b, `GAGS` trayFront, trayBack.)
        const tray = this.holding && !this.giving;
        if (tray) {
            // (Down it goes, and she goes back for another.)
            sfx.at(this.x, d.y).crash();
            const dropped = this.world.image(this.tray.x, this.tray.y, 'thing:breakfast-tray').setOrigin(0.5, 1).setDepth(this.tray.depth);
            this.world.add([dropped]);
            // (Flat onto the carpet: turned on the way down, level as it lands, never into the floor.)
            s.tweens.add({ targets: dropped, angle: { from: 0, to: this.p.dir * 25 }, duration: 130, yoyo: true });
            s.tweens.add({ targets: dropped, y: d.y, duration: 260, ease: 'Quad.easeIn',
                onComplete: () => s.tweens.add({ targets: dropped, alpha: 0, delay: 1500, duration: 400, onComplete: () => dropped.destroy() }) });
            this.holding = false;
            this.state = 'return';
        }
        this.until = time + 1500;
        // (Her hands empty: she herself, 10f; with her back to her, she turns round.)
        if (!tray && (her.x - this.x) * (this.p?.dir ?? 1) < 0) {
            this.turnTo = Math.sign(her.x - this.x);
            this.turnUntil = time + 1500;
        }
        if (this.world.carry) this.world.carryBox.spill(this.x, false, tray ? 'breakfast' : 'stewardess', { dir: this.p?.dir ?? 0 });
        else s.scareContact(this.x, tray ? 'breakfast' : 'stewardess', { dir: this.p?.dir ?? 0, ride: { tray, y: d.y } });
    }
}
