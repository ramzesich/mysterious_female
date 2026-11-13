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
