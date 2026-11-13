// The ship's people (GAME_DESIGN.md §6.1.6, docs/population.md §1 and §7): crew who ask for things,
// passengers who are in the way, and scenery people. Each stands, or walks a loop (stopping here and
// there), may carry something with them (a cart), may show a pictogram bubble when she is near, and
// may do something when she touches them: a fright, a spilled tray. Sprites: assets/sprites/people
// (tools/cast.py, tools/build_people.py).

import { PLAYER } from '../config.js';

const M = 48;                           // px per metre
const BUBBLE = { w: 22, h: 20, rise: 8 };

export class People {
    constructor(world) {
        this.world = world;
        this.scene = world.scene;
        this.meta = this.scene.cache.json.get('people-meta')?.people ?? {};
        this.list = [];
        this.byId = {};
    }

    has(who) {
        return !!this.meta[who];
    }

    // One person from the population's data: { id, who, x, y, route, face, idle, walk, touch, carry,
    // until, after, layer, bubble }.
    add(def) {
        const s = this.scene, D = s.DEPTH;
        const meta = this.meta[def.who];
        if (!meta) return null;            // not drawn yet
        const inside = def.route === 'inside';
        const depth = !inside ? D.exterior + 0.135 : def.layer === 'behind' ? D.decor + 0.09 : def.layer === 'back' ? D.decor + 0.12
            : def.layer === 'front' ? D.player + 0.02 : D.props + 0.05;
        const sprite = s.add.sprite(def.x, def.y - (def.dy ?? 0), 'people', meta.stand).setOrigin(0.5, 1).setDepth(depth);
        sprite.setFlipX((def.face ?? 1) < 0);
        this.world.add([sprite]);
        const p = { ...def, sprite, meta, items: [sprite], dir: def.face ?? 1, x: def.x, pausedUntil: 0, attached: [], state: 'idle' };
        // What goes along with them (the porter's cart): pieces of the ship's atlas, in front or behind.
        for (const a of def.carry ?? []) {
            // ("@name": a picture drawn by the game, not a piece of the atlas: a tray.)
            this.world.carryBox.textures();
            const img = (a.frame.startsWith('@') ? s.add.image(def.x, def.y, a.frame.slice(1)) : s.add.image(def.x, def.y, 'shipart', a.frame))
                .setOrigin(0.5, 1).setDepth(depth + (a.front ? 0.01 : -0.01));
            this.world.add([img]);
            p.attached.push({ ...a, img });
            p.items.push(img);
        }
        if (def.bubble) {
            const g = s.add.graphics().setDepth(D.fx + 0.5);
            g.fillStyle(0x2e222f, 1).fillRoundedRect(-BUBBLE.w / 2 - 1, -BUBBLE.h - 1, BUBBLE.w + 2, BUBBLE.h + 2, 4);
            g.fillStyle(0xffffff, 1).fillRoundedRect(-BUBBLE.w / 2, -BUBBLE.h, BUBBLE.w, BUBBLE.h, 3);
            g.fillStyle(0x2e222f, 1).fillTriangle(-4, 1, 4, 1, 0, 6);
            g.fillStyle(0xffffff, 1).fillTriangle(-3, 0, 3, 0, 0, 4);
            const icon = s.add.image(0, 0, this.world.icon(def.bubble.icon)).setDepth(D.fx + 0.51);
            this.world.add([g, icon]);
            p.bubbleItems = [g, icon];
            g.setVisible(false);
            icon.setVisible(false);
        }
        this.idle(p);
        this.place(p);
        this.list.push(p);
        this.byId[def.id] = p;
        return p;
    }

    anim(p, clip, { loop = true, speed = 1 } = {}) {
        const frames = p.meta.anims[clip];
        if (!frames) return false;
        const key = `people-${p.who}-${clip}`;
        const s = this.scene;
        if (!s.anims.exists(key)) {
            s.anims.create({ key, frames: frames.map(f => ({ key: 'people', frame: f })), frameRate: p.meta.fps[clip] ?? 8, repeat: -1 });
        }
        if (p.sprite.anims.currentAnim?.key !== key || !p.sprite.anims.isPlaying) p.sprite.anims.play({ key, repeat: loop ? -1 : 0 });
        p.sprite.anims.timeScale = speed;
        return true;
    }

    idle(p) {
        p.state = 'idle';
        if (!p.idle || !this.anim(p, p.idle)) {
            p.sprite.anims.stop();
            p.sprite.setFrame(p.meta.stand);
        }
    }

    // A clip played once (a shake of the head, eating), then back to idling. Resolves when it is over.
    play(p, clip, { times = 1, hold = 0 } = {}) {
        return new Promise(resolve => {
            const frames = p.meta.anims[clip];
            if (!frames) {
                this.scene.time.delayedCall(600 + hold, resolve);
                return;
            }
            const key = `people-${p.who}-${clip}`;
            if (!this.scene.anims.exists(key)) {
                this.scene.anims.create({ key, frames: frames.map(f => ({ key: 'people', frame: f })), frameRate: p.meta.fps[clip] ?? 8, repeat: -1 });
            }
            p.state = 'acting';
            p.sprite.anims.play({ key, repeat: times - 1 });
            p.sprite.once('animationcomplete', () => {
                this.scene.time.delayedCall(hold, () => {
                    if (p.state === 'acting') this.idle(p);
                    resolve();
                });
            });
        });
    }

    place(p) {
        p.sprite.x = p.x;
        p.sprite.setFlipX(p.dir < 0);
        for (const a of p.attached) {
            a.img.x = p.x + p.dir * a.dx;
            a.img.y = p.y - (a.dy ?? 0);
            a.img.setFlipX(p.dir < 0 !== !!a.flip);
        }
    }

    shown(p) {
        const P = this.world.progress;
        if (p.gone) return false;
        if (p.until && this.world.cond(p.until)) return false;
        if (p.after && !this.world.cond(p.after)) return false;
        return p.route === 'inside' || p.route === this.scene.route;
    }

    refresh() {
        for (const p of this.list) {
            const on = this.shown(p);
            p.on = on;
            for (const i of p.items) i.setVisible(on);
            if (!on) p.bubbleItems?.forEach(i => i.setVisible(false));
        }
    }

    update(dt, time) {
        const s = this.scene, her = s.player;
        const playing = s.mode === 'play' || s.mode === 'push';
        for (const p of this.list) {
            if (!p.on) continue;
            // Only near her does anyone move: the ship is long.
            const near = Math.abs(p.x - her.x) < 900 && Math.abs(p.y - her.y) < 400;
            if (p.walk && near && p.state !== 'acting') this.walk(p, dt, time);
            if (p.bubbleItems) {
                const b = p.bubble;
                const show = playing && s.route === p.route && Math.abs(her.x - p.x) < (b.range ?? 4) * M && Math.abs(her.y - p.y) < 40
                    && (!b.when || this.world.cond(b.when)) && (!b.unless || !this.world.cond(b.unless));
                const bob = Math.round(Math.sin(time / 300) * 1.5);
                const by = p.y - (p.dy ?? 0) - PLAYER.height - BUBBLE.rise + bob;
                p.bubbleItems[0].setVisible(show).setPosition(p.x, by);
                p.bubbleItems[1].setVisible(show).setPosition(p.x, by - BUBBLE.h / 2);
            }
            if (p.touch && playing && s.route === p.route && !p.aside && this.touching(p, her)) this.world.touched(p);
        }
    }

    // A loop between two ends, with a pause at each end and at the stops on the way (the waiter at his
    // tables: turned to the table he is out of the aisle, and she can slip past).
    walk(p, dt, time) {
        const w = p.walk;
        if (time < p.pausedUntil) return;
        if (p.aside) {
            p.aside = false;
            p.sprite.setDepth(p.sprite.depth + 0.2);
        }
        const before = p.x;
        p.x += p.dir * w.v * M * dt;
        if (p.x >= w.b) { p.x = w.b; p.dir = -1; p.pausedUntil = time + (w.endMs ?? 600); }
        else if (p.x <= w.a) { p.x = w.a; p.dir = 1; p.pausedUntil = time + (w.endMs ?? 600); }
        // (Its own name for the clip, or "walk".)
        if (time < p.pausedUntil) this.idle(p);
        else if (!this.anim(p, w.clip ?? 'walk')) p.sprite.setFrame(p.meta.stand);
        for (const stop of w.stops ?? []) {
            if ((before - stop) * (p.x - stop) <= 0 && before !== p.x && time >= p.pausedUntil) {
                p.x = stop;
                p.pausedUntil = time + (w.stopMs ?? 2200);
                p.aside = true;
                p.sprite.setDepth(p.sprite.depth - 0.2);
                p.sprite.anims.stop();
                p.sprite.setFrame(p.meta.back ?? p.meta.front ?? p.meta.stand);
                break;
            }
        }
        this.place(p);
    }

    // Her body against theirs (and their cart's): `touch.w` wide round them (shifted ahead by
    // `touch.dx` the way they face), `touch.h` tall; over it she is clear.
    touching(p, her) {
        const t = p.touch;
        const cx = p.x + p.dir * (t.dx ?? 0);
        if (Math.abs(her.x - cx) > t.w / 2 + PLAYER.bodyWidth / 2) return false;
        return her.y > p.y - t.h && her.y - PLAYER.bodyHeight < p.y;
    }
}
