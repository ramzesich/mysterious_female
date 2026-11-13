// Things that move by themselves (docs/population.md §1): the delivery robot she can ride (a
// `platform`), the gulls (one creature with a few states and a rule per place), the stage's light,
// the casino's chips, and deck 9's housekeeping hour: the vacuum that darts out of a doorway, the
// towel stack, the sprinkler, the door that flies open, the "Do Not Disturb" door. Pictures:
// assets/sprites/things (tools/build_things.py).

import { PLAYER } from '../config.js';
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
        this.beep = s.add.text(def.x, def.y - this.h - 6, '♪', {
            fontFamily: 'Verdana, sans-serif', fontSize: '9px', fontStyle: 'bold', color: '#0b5e65', resolution: 4,
        }).setOrigin(0.5, 1).setDepth(D.fx).setVisible(false);
        world.add([this.sprite, this.beep]);
    }

    addCollider(p) {
        this.scene.physics.add.collider(p, this.zone, null, () => this.scene.route === 'inside');
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
        if (blocked && !this.wasBlocked) sfx.pickup();
        this.wasBlocked = blocked;
        if (blocked || time < this.pausedUntil) return;
        let to = this.x + this.dir * d.v * M * dt;
        if (to >= d.x1) { to = d.x1; this.dir = -1; this.pausedUntil = time + 900; }
        else if (to <= d.x0) { to = d.x0; this.dir = 1; this.pausedUntil = time + 900; }
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

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        const on = d.route === 'inside' || d.route === s.route;
        this.sprite.setVisible(on);
        if (!on) return;
        const near = Math.abs(p.x - d.x) < 3 * M && Math.abs(p.y - d.y) < 90;
        if (near) this.awaySince = time;
        const up = near || time - this.awaySince < 1400;
        if (up && this.rise === 0) sfx.whoosh?.();
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
            if (this.world.carry) this.world.carryBox.spill(x);
            else s.scareContact(x, 'bonked');
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
            sfx.ding();
        } else if (this.state === 'tell') {
            // The lights race along its top.
            const g = this.lights.clear(), lit = Math.floor(time / 90) % 6;
            for (let i = 0; i < 6; i++) g.fillStyle(i === lit || i === (lit + 3) % 6 ? 0xfbff86 : 0xae2334, 1).fillRect(d.x - 17 + i * 6, d.y - d.top, 4, 3);
            if (time > this.at) {
                this.state = 'spilled';
                this.at = time + 4000;
                this.lights.clear();
                this.pour();
                sfx.smash();
            }
        } else if (this.state === 'spilled') {
            const left = this.at - time;
            this.chips.setAlpha(left < 700 ? (Math.floor(time / 90) % 2 ? 0.35 : 1) : 1);
            const onFloor = p.body.blocked.down || p.body.touching.down;
            if (s.mode === 'play' && s.route === 'inside' && onFloor && Math.abs(p.y - d.y) < 3 && Math.abs(p.x - d.x) < d.half
                && Math.abs(p.body.velocity.x) > 20) {
                if (this.world.carry) this.world.carryBox.spill(d.x);
                else s.scareContact(p.x - Math.sign(p.body.velocity.x) * 10, 'slipped');
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

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def, v = this.sprite;
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
                sfx.rattle();
            }
        } else if (this.state === 'wait') {
            v.x = d.x + (Math.floor(time / 40) % 2 ? 1 : -1);
            if (time > this.at) {
                this.state = 'out';
                v.setScale(1).clearTint().setFlipX(this.dir < 0);
                sfx.whoosh();
                // Out fast, a breath, and back in slowly: only on its way out is it a fright.
                s.tweens.add({
                    targets: v, x: d.x + this.dir * d.dart, duration: 400, ease: 'Quad.easeOut', hold: 160,
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
            if (s.isDashing()) {
                // Sent spinning; it creeps home after a while.
                s.tweens.killTweensOf(v);
                this.state = 'spun';
                s.smash(v.x, v.y - 3);
                s.tweens.add({ targets: v, angle: 720, alpha: 0.6, duration: 900, ease: 'Quad.easeOut', onComplete: () => this.home(s.time.now + 4000) });
            } else if (this.world.carry) {
                this.world.carryBox.spill(v.x);
            } else {
                s.scareContact(v.x, 'vacuum');
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
            if (on && Math.abs(dx) < 48 && (landed || s.isDashing())) {
                this.state = 'falling';
                this.dir = dx < 0 ? -1 : 1;
                sfx.rattle();
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
        sfx.smash();
        if (here(s, d) && Math.abs(p.x - cx) < 38 && p.y > d.y - 40) {
            // Under it: only her hair shows for a moment.
            this.heap.setPosition(p.x, d.y - 26).setScale(1, 2.6);
            s.tweens.add({ targets: this.heap, y: d.y, scaleY: 1, duration: 900, delay: 500, ease: 'Bounce.easeOut' });
            if (this.world.carry) this.world.carryBox.spill(d.x);
            else s.scareContact(d.x, 'buried');
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
                if (this.world.carry) this.world.carryBox.spill(d.x);
                else s.scareContact(d.x, 'drenched');
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
        this.who = world.people.add({ id: `${def.id}_who`, who: def.who, x: def.x - 2, y: def.y - 2, route: 'inside', face: -1, idle: 'idle', layer: 'back' });
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
                sfx.rattle();
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
                sfx.smash();
                if (this.who) {
                    this.who.gone = false;
                    this.who.dir = dx < 0 ? -1 : 1;
                    this.world.people.place(this.who);
                    this.world.people.refresh();
                }
            }
        } else if (this.state === 'burst') {
            if (here(s, d) && Math.abs(p.y - d.y) < 40 && dx > -18 && dx < 34) {
                this.state = 'open';
                this.at = time + 1500;
                if (this.world.carry) this.world.carryBox.spill(d.x + 20);
                else s.scareContact(d.x + 14, 'bonked');
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
            sfx.door();
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
        this.who = world.people.add({ id: `${def.id}_who`, who: def.who, x: def.x, y: def.y - 2, route: 'inside', face: -1, layer: 'back' });
        if (this.who) this.who.gone = true;
        this.busy = false;
        world.things.push({ ...def, items: [], reach: 16, interact: () => this.knock() });
    }

    // (`heard`: a clatter outside brought them to the door: a fright only if she is by it.)
    knock(heard) {
        const s = this.scene, p = s.player, d = this.def;
        if (this.busy || (this.world.carry && !heard)) return false;
        this.busy = true;
        sfx.door();
        this.shut.setVisible(false);
        this.card.setVisible(false);
        this.dark.setVisible(true);
        if (this.who) {
            this.who.gone = false;
            this.who.dir = p.x < d.x ? -1 : 1;
            this.world.people.place(this.who);
            this.world.people.refresh();
            this.world.people.play(this.who, 'shriek');
        }
        const by = !heard || (Math.abs(p.x - d.x) < 3 * M && Math.abs(p.y - d.y) < 60);
        if (by && !this.world.carry) s.scareContact(d.x + (p.x < d.x ? 12 : -12), 'startled');
        s.time.delayedCall(1700, () => {
            this.shut.setVisible(true);
            this.card.setVisible(true);
            this.dark.setVisible(false);
            if (this.who) {
                this.who.gone = true;
                this.world.people.refresh();
            }
            sfx.rattle();
            this.busy = false;
        });
        return true;
    }

    update() {}
}
