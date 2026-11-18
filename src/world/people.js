// The ship's people (GAME_DESIGN.md §6.1.6, docs/population.md §1 and §7): crew who ask for things,
// passengers who are in the way, and scenery people. Each stands, or walks a loop (stopping here and
// there), may carry something with them (a cart), may show a pictogram bubble when she is near, and
// may do something when she touches them: a fright, a spilled tray. Sprites: assets/sprites/people
// (tools/cast.py, tools/build_people.py).

import { PLAYER, CRY, PEOPLE_IDLE } from '../config.js';
import { sfx } from '../sfx.js';

const M = 48;                           // px per metre
// Where the eating hand's fist is in each frame of someone's `bite` clip (found frame by frame on
// the 96 px frames, composed offline with the fruit at the game's offsets, 2026-11-16): px ahead of
// their middle, px over their feet. The tangerine sits in it all the way, drawn behind the figure
// so that the fingers close over it: to the mouth, a bite (frames 2 and 3), the hand down, chewing.
const FISTS = {
    porter: [[17, 35], [14, 41], [6, 46], [9, 46], [17, 36], [17, 36], [17, 35], [17, 35]],
    paperboy: [[14, 36], [13, 41], [10, 48], [11, 46], [12, 38], [12, 38], [13, 38], [13, 38]],
    paperwoman: [[13, 37], [10, 43], [8, 49], [10, 47], [12, 38], [12, 38], [13, 37], [13, 37]],
};
// Whose hand the fruit is drawn over, covering the palm (the user, 2026-11-16: the steward's sat
// behind his palm); the others' fingers close over it.
const FRUIT_OVER = new Set(['paperboy', 'paperwoman']);
const BITES = ['tangerine', 'tangerine-bit1', 'tangerine-bit2'];
const BUBBLE = { w: 22, h: 20, rise: 8 };

// A clip's frames a second: an idle clip on the idles' own clock (`PEOPLE_IDLE`), any other its sheet's.
const clipFps = (p, clip) => (/^idle\d*$/.test(clip) ? PEOPLE_IDLE.fps : p.meta.fps[clip] ?? 8);

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
        // (`pose`: turned to us at a rail ("front"), or away, reading a wall ("back").)
        const sprite = s.add.sprite(def.x, def.y - (def.dy ?? 0), 'people', meta[def.pose] ?? meta.stand).setOrigin(0.5, 1).setDepth(depth);
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
        // Built furniture they stand behind, drawn again in front of them (a bar's counter).
        for (const c of def.cover ?? []) {
            const img = s.add.image(c.x, def.y - (c.dy ?? 0), 'shipart', c.frame).setOrigin(0.5, 1).setDepth(depth + 0.005);
            this.world.add([img]);
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
            s.anims.create({ key, frames: frames.map(f => ({ key: 'people', frame: f })), frameRate: clipFps(p, clip), repeat: -1 });
        }
        if (p.sprite.anims.currentAnim?.key !== key || !p.sprite.anims.isPlaying) p.sprite.anims.play({ key, repeat: loop ? -1 : 0 });
        p.sprite.anims.timeScale = speed;
        return true;
    }

    idle(p) {
        p.state = 'idle';
        // (`still`: held in a clip's last frame: sat down on the floor.)
        if (p.still && p.meta.anims[p.still]) {
            p.sprite.anims.stop();
            p.sprite.setFrame(p.meta.anims[p.still].at(-1));
            return;
        }
        if (!p.idle || !this.anim(p, p.idle)) {
            p.sprite.anims.stop();
            p.sprite.setFrame(p.meta[p.pose] ?? p.meta.stand);
        }
    }

    // A clip played once (a shake of the head, eating), then back to idling. Resolves when it is over.
    play(p, clip, { times = 1, hold = 0, speed = 1 } = {}) {
        return new Promise(resolve => {
            const frames = p.meta.anims[clip];
            if (!frames) {
                this.scene.time.delayedCall(600 + hold, resolve);
                return;
            }
            const key = `people-${p.who}-${clip}`;
            if (!this.scene.anims.exists(key)) {
                this.scene.anims.create({ key, frames: frames.map(f => ({ key: 'people', frame: f })), frameRate: clipFps(p, clip), repeat: -1 });
            }
            p.state = 'acting';
            p.sprite.anims.play({ key, repeat: times - 1 });
            p.sprite.anims.timeScale = speed;
            p.sprite.once('animationcomplete', () => {
                p.sprite.anims.timeScale = 1;
                this.scene.time.delayedCall(hold, () => {
                    if (p.state === 'acting') this.idle(p);
                    resolve();
                });
            });
        });
    }

    // Someone looking out of a doorway is inside the room: seen only through its opening (`x0`..`x1`,
    // `top`..`bottom`, world px), never over the frame or the wall beside it (the user, 2026-11-18:
    // a boy's cap stuck through the door frame).
    doorway(p, x0, x1, top, bottom) {
        if (!p) return;
        p.door = { x0, x1, top, bottom };
        this.cropToDoor(p);
    }

    // (Their picture cut to the opening, in the picture's own unflipped px: turned, mirrored.)
    cropToDoor(p) {
        const d = p.door, sp = p.sprite, fw = sp.frame.width, fh = sp.frame.height;
        const left = sp.x - fw * sp.originX, top = sp.y - fh * sp.originY;
        const a = Math.max(0, Math.min(fw, d.x0 - left)), b = Math.max(0, Math.min(fw, d.x1 - left));
        const u0 = sp.flipX ? fw - b : a;
        const v0 = Math.max(0, d.top - top), v1 = Math.min(fh, d.bottom - top);
        sp.setCrop(u0, v0, b - a, v1 - v0);
    }

    place(p) {
        p.sprite.x = p.x;
        p.sprite.setFlipX(p.dir < 0);
        if (p.door) this.cropToDoor(p);
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
        return p.route === 'inside' || p.route === this.scene.route || p.route === this.world.peek;
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
                // (Its pop, but not again each time a scene or her going to and fro hides it a moment.)
                if (show && !p.bubbleShown && time > (p.bubbleQuietUntil ?? 0)) sfx.at(p.x, p.y).bubble();
                if (show) p.bubbleQuietUntil = time + 6000;
                p.bubbleShown = show;
                // (`bubbleDx`: over his own head in a picture of him with something, px from its middle.)
                const bx = p.x + (p.bubbleDx ?? 0);
                p.bubbleItems[0].setVisible(show).setPosition(bx, by);
                p.bubbleItems[1].setVisible(show).setPosition(bx, by - BUBBLE.h / 2);
            }
            if (p.touch && playing && s.route === p.route && !p.aside && !p.busy && !s.aside && this.touching(p, her)) this.world.touched(p);
        }
    }

    // Her cry (src/world/world.js `shout`): within its reach on her deck, a walker in her way stops
    // and turns aside for a while, a "!" over him; anyone else standing about turns to look, a heart
    // over the few who like cats, a finger to the lips in a quiet place (`hear` in the data; "own":
    // their part of the story answers it). Each is deaf to the next cry for a while.
    heard(cry) {
        const time = this.scene.time.now, her = this.scene.player;
        for (const p of this.list) {
            if (!p.on || p.owned || p.hear === 'own' || p.state === 'acting' || p.busy || time < (p.deafUntil ?? 0)) continue;
            if (!this.world.hears(p.x, p.y, p.route)) continue;
            p.deafUntil = time + CRY.deafMs;
            const top = p.y - (p.dy ?? 0) - PLAYER.height - 6;
            if (p.walk) {
                this.standAside(p);
                continue;
            }
            if (p.hear === '♥' || p.hear === 'shh') this.world.pop(p.x, top, p.hear === '♥' ? 'heart' : 'shh', 1500);
            // Turned to her a moment: only those standing about (not one at work at something, sat
            // down, or turned to us or to a wall, who must keep facing what they do).
            if (p.idle === 'idle' && !p.pose && !p.still) {
                const was = p.dir, to = her.x < p.x ? -1 : 1;
                if (to === was) continue;
                p.dir = to;
                this.place(p);
                this.scene.time.delayedCall(CRY.startleMs, () => {
                    if (p.dir !== to || p.state === 'acting') return;
                    p.dir = was;
                    this.place(p);
                });
            }
        }
    }

    // A walker startled (by her cry, or by walking into her when the pocket took the hit): he stops
    // and stands aside for a while, a "!" over him.
    standAside(p) {
        const time = this.scene.time.now;
        if (!p.aside) {
            p.aside = true;
            p.sprite.setDepth(p.sprite.depth - 0.2);
        }
        // (Against the wall, out of her way: a little further from us, as the steward at a door.)
        p.cried = true;
        for (const i of p.items) i.setScale(0.94);
        p.pausedUntil = Math.max(p.pausedUntil, time + CRY.startleMs);
        // (The jogger jogs on the spot, looking round; the others freeze mid-step, holding
        // what they carry as they were: their standing frame would leave a tray in the air.)
        if (p.walk.clip !== 'run') p.sprite.anims.pause();
        this.world.pop(p.x, p.y - (p.dy ?? 0) - PLAYER.height - 6, 'alert', 1200);
        sfx.at(p.x, p.y).oh();
    }

    // A tangerine loose at someone's feet (docs/plan-three-uses.md §2). The porter stops to pick it
    // up and peels it by the wall (10 s clear); the waiter stops and pockets it; both spent. The
    // jogger hops it without a look. Anyone else standing about turns to look at it a moment.
    // True if it was taken.
    offered(t) {
        const s = this.scene, time = s.time.now, loose = s.loose;
        for (const p of this.list) {
            if (!p.on || p.owned || p.hear === 'own' || p.state === 'acting' || p.busy || p.gone) continue;
            if (p.walk && p.touch) {
                // (Anywhere along what she would bump into: his cart's front too, so that he stops
                // for it before his cart reaches her.)
                if (!loose.near(t, p.x + p.dir * (p.touch.dx ?? 0), p.y, p.touch.w / 2 + 4, 14, p.route)) continue;
                if (p.walk.clip === 'run') {
                    if (time < (p.hopUntil ?? 0)) continue;
                    p.hopUntil = time + 700;
                    s.tweens.add({ targets: p.sprite, y: p.y - 10, duration: 170, yoyo: true, ease: 'Quad.easeOut' });
                    continue;
                }
                this.takeFruit(p, t, p.touch.kind === 'spill' ? 'pocket' : 'peel');
                return true;
            }
            // Standing about: a look at it, a while.
            if (t.resting || p.walk || p.idle !== 'idle' || p.pose || p.still || time < (p.lookUntil ?? 0)) continue;
            if (t.route !== p.route || Math.abs(t.img.x - p.x) > 2 * M || Math.abs(t.img.y - p.y) > 50) continue;
            p.lookUntil = time + 4000;
            const was = p.dir, to = t.img.x < p.x ? -1 : 1;
            if (to === was) continue;
            p.dir = to;
            this.place(p);
            s.time.delayedCall(1800, () => {
                if (p.dir !== to || p.state === 'acting') return;
                p.dir = was;
                this.place(p);
            });
        }
        return false;
    }

    // A walker takes it: `peel`, stood by the wall eating it 10 s; `pocket`, in his pocket and on.
    takeFruit(p, t, how) {
        const s = this.scene, time = s.time.now;
        const img = s.loose.claim(t);
        this.standAside(p);
        p.pausedUntil = time + (how === 'peel' ? 10000 : 2000);
        sfx.at(p.x, p.y).take();
        // (Up into his hand, at his front.)
        img.setDepth(p.sprite.depth + 0.01);
        s.tweens.add({ targets: img, x: p.x + p.dir * 9, y: p.y - 27, duration: 260, ease: 'Sine.easeOut', onComplete: () => {
            if (how === 'pocket') {
                s.tweens.add({ targets: img, y: img.y + 6, alpha: 0, duration: 300, delay: 250, onComplete: () => img.destroy() });
                return;
            }
            const was = p.state;
            p.state = 'acting';
            this.eat(p, img, () => {
                p.state = was === 'acting' ? 'idle' : was;
                if (p.walk.clip !== 'run') p.sprite.anims.pause();
            });
        } });
    }

    // Someone eats a tangerine held in their hand (the user, 2026-11-16: "to their mouths, bite,
    // remove leftover food from their mouths, chew; the food has to stay in their hands"): their
    // `bite` clip three times, the fruit at their fist in every frame (FISTS), bitten at each bite
    // and gone at the third. `done` when they have finished.
    eat(p, img, done) {
        const s = this.scene, fists = FISTS[p.who], frames = p.meta.anims.bite;
        if (!fists || !frames) {
            img.destroy();
            done?.();
            return;
        }
        const key = `people-${p.who}-bite`;
        if (!s.anims.exists(key)) s.anims.create({ key, frames: frames.map(f => ({ key: 'people', frame: f })), frameRate: p.meta.fps.bite ?? 6 });
        let bites = 0;
        const hold = () => {
            const i = (p.sprite.anims.currentFrame?.index ?? 1) - 1, [fx, fy] = fists[i] ?? fists[0];
            // (Behind the figure, the fingers over it; but over a cart of theirs that is drawn over
            // them, the porter's trolley as he stands aside, or it would be hidden behind it.)
            const over = Math.max(-Infinity, ...p.attached.map(a => a.img.depth));
            img.setPosition(p.x + p.dir * fx, p.y - (p.dy ?? 0) - fy).setFlipX(p.dir < 0)
                .setDepth(over > p.sprite.depth ? over + 0.001 : p.sprite.depth + (FRUIT_OVER.has(p.who) ? 0.001 : -0.001));
            // (The bite: at the mouth; the hand comes away with a piece gone.)
            if (i === 2 && img.getData('bitten') !== bites) {
                img.setData('bitten', bites);
                sfx.at(p.x, p.y).munch();
            }
            if (i === 4 && img.getData('bitten') === bites) {
                bites += 1;
                if (bites < BITES.length) img.setTexture(BITES[bites]);
                else img.setVisible(false);
            }
        };
        const update = () => hold();
        p.sprite.on('animationupdate', update);
        p.sprite.anims.play({ key, repeat: BITES.length - 1 });
        hold();
        p.sprite.once('animationcomplete', () => {
            p.sprite.off('animationupdate', update);
            img.destroy();
            done?.();
        });
    }

    // In a lunge she went through someone (`touch`): the porter's cart knocked rolling, he after
    // it; the jogger spun round like a top. True if it was one of them.
    lunged(kind, fromX) {
        const s = this.scene, her = s.player;
        const p = this.list.find(q => q.touch && q.on && Math.abs(q.x - fromX) < 1);
        if (!p) return false;
        const away = her.x < p.x ? 1 : -1;
        if (p.attached.length && p.walk) {
            // The cart goes rolling two metres the way she was going; he runs after it.
            // (Short of a door: a cart left to itself does not open one.)
            const lead = away === p.dir ? this.ends(p).front : this.ends(p).back;
            const roll = s.stopShort(p.x, Phaser.Math.Clamp(p.x + away * 2 * M, p.walk.a, p.walk.b), p.y, lead) - p.x;
            p.busy = true;
            p.state = 'acting';
            sfx.at(p.x, p.y).oh();
            this.world.pop(p.x, p.y - (p.dy ?? 0) - PLAYER.height - 6, 'alert', 1000);
            for (const a of p.attached) s.tweens.add({ targets: a.img, x: a.img.x + roll, duration: 650, ease: 'Quad.easeOut' });
            s.time.delayedCall(350, () => {
                this.anim(p, p.walk.clip ?? 'walk', { speed: 1.8 });
                s.tweens.add({ targets: p, x: p.x + roll, duration: 700, ease: 'Sine.easeInOut',
                    onUpdate: () => { p.sprite.x = p.x; },
                    onComplete: () => { p.busy = false; this.place(p); this.idle(p); } });
            });
            return true;
        }
        if (p.walk) {
            // Spun round, and on again.
            p.busy = true;
            p.state = 'acting';
            sfx.at(p.x, p.y).oh();
            let n = 0;
            s.time.addEvent({ delay: 90, repeat: 7, callback: () => {
                p.sprite.setFlipX(!p.sprite.flipX);
                if (++n === 8) {
                    p.busy = false;
                    this.place(p);
                    this.idle(p);
                }
            } });
            return true;
        }
        return false;
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
        if (p.cried) {
            p.cried = false;
            for (const i of p.items) i.setScale(1);
            p.sprite.anims.resume();
        }
        const before = p.x;
        if (this.door(p, time)) return;
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

    // From their middle to their front and their back, the way they face (their cart's ends).
    ends(p) {
        const t = p.touch;
        return t ? { front: (t.dx ?? 0) + t.w / 2, back: t.w / 2 - (t.dx ?? 0) } : { front: 10, back: 10 };
    }

    // A door across the deck on their way (the user, 2026-11-17; ShipScene `stopShort`): one with no
    // lock they open, a moment at its handle, and go through, holding it till their back is past;
    // a locked one turns them back short of it, as at an end of their walk. True while they wait.
    door(p, time) {
        const s = this.scene, w = p.walk, { front, back } = this.ends(p);
        if (p.through && (p.x - p.through.x) * p.throughDir - back > p.through.w / 2 + 8) {
            s.letGoDoor(p.through, p);
            p.through = null;
        }
        const b = s.doorAhead(p.x, p.dir, p.y, front, 10);
        if (!b || b === p.through) return false;
        if (s.mayOpen(b)) {
            p.through = b;
            p.throughDir = p.dir;
            if (!s.holdDoor(b, p)) return false;
            p.pausedUntil = time + 450;
        } else {
            p.x = s.stopShort(p.x, p.x + p.dir * 10, p.y, front);
            p.dir = -p.dir;
            p.pausedUntil = time + (w.endMs ?? 600);
        }
        this.idle(p);
        this.place(p);
        return true;
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
