// Things that move by themselves (docs/population.md §1): the delivery robot she can ride (a
// `platform`), the gulls (one creature with a few states and a rule per place). Pictures:
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
