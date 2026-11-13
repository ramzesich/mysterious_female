// The open decks' and the hallways' hazards that came with the pool deck (docs/population.md, deck
// 11 and deck 10's hallway under it): the wet patch and the deck chair that slides at her across it,
// the gulls that dive at food carried in the open, the buffet queue, the room-service trays left on
// a hallway's floor. Like src/world/movers.js, each takes its place from maps/world.json.

import { PLAYER } from '../config.js';
import { sfx } from '../sfx.js';

const M = 48;
const here = (s, d) => s.route === 'inside' && s.mode === 'play' && Math.abs(s.player.y - d.y) < 100;
const nearby = (s, d) => Math.abs(s.player.x - d.x) < 900 && Math.abs(s.player.y - d.y) < 300;

// What a gull will dive at.
export const FOOD = ['cone', 'stub', 'lunch', 'cake'];

// A wet patch by the pool showers (population: `haz_wet`, `haz_deckchair`). Without the grip socks
// she slides across it the way she came, with no stopping and no turning, and the deck chair at
// its aft end rocks (the tell) and slides at her: "Bumped"; a jump clears it. In the socks the tiles
// hold, and the chair stays where it is.
export class WetPatch {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, chairX }
        const g = s.add.graphics().setDepth(D.decor + 0.3);
        const w = def.x1 - def.x0;
        g.fillStyle(0x8fd3ff, 0.3).fillRect(def.x0 + 3, def.y - 3, w - 6, 3);
        g.fillStyle(0x8fd3ff, 0.3).fillRect(def.x0, def.y - 2, w, 2);
        g.fillStyle(0xffffff, 0.75);
        for (let x = def.x0 + 7; x < def.x1 - 8; x += 17) g.fillRect(x + (x % 3), def.y - 2, 6, 1);
        this.shine = s.add.rectangle(def.x0, def.y - 3, 5, 1, 0xffffff, 0.9).setOrigin(0, 0).setDepth(D.decor + 0.31);
        this.chair = s.add.image(def.chairX, def.y, 'shipart', 'deck-chair').setOrigin(0.5, 1).setDepth(D.props + 0.02).setFlipX(true);
        world.add([g, this.shine, this.chair]);
        this.state = 'rest';
        this.at = 0;
        this.slip = 0;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def, c = this.chair;
        if (!nearby(s, d)) return;
        this.shine.x = d.x0 + 4 + ((time * 0.03) % (d.x1 - d.x0 - 12));
        const onFloor = p.body.blocked.down || p.body.touching.down;
        const on = here(s, d) && Math.abs(p.y - d.y) < 2 && onFloor && p.x > d.x0 && p.x < d.x1;
        const socks = this.world.progress.knows('socks');
        // Sliding: the way she was going as she stepped on, until the patch ends or she is in the air.
        if (on && !socks) {
            if (!this.slip) {
                this.slip = p.body.velocity.x < -5 ? -1 : p.body.velocity.x > 5 ? 1 : (p.flipX ? -1 : 1);
                sfx.whoosh();
            }
        } else if (onFloor || !here(s, d)) {
            this.slip = 0;
        }
        s.slipDir = this.slip && here(s, d) ? this.slip : 0;
        // The chair: it rocks, then slides the patch's length at her, waits, and slides home again.
        if (this.state === 'rest') {
            if (this.slip) {
                this.state = 'rock';
                this.at = time + 450;
                sfx.rattle();
            }
        } else if (this.state === 'rock') {
            c.setAngle(Math.sin(time / 38) * 7);
            if (time > this.at) {
                c.setAngle(0);
                this.state = 'slide';
                sfx.whoosh();
            }
        } else if (this.state === 'slide') {
            c.x -= 235 * dt;
            if (c.x <= d.x0 + 8) {
                c.x = d.x0 + 8;
                this.state = 'far';
                this.at = time + 1600;
            }
            const hit = here(s, d) && Math.abs(p.x - c.x) < PLAYER.bodyWidth / 2 + 11 && p.y > d.y - 20;
            if (hit) {
                this.state = 'far';
                this.at = time + 1600;
                this.slip = 0;
                s.slipDir = 0;
                if (this.world.carry) this.world.carryBox.spill(c.x);
                else s.scareContact(c.x, 'bumped');
            }
        } else if (this.state === 'far') {
            if (time > this.at && !this.slip) this.state = 'home';
        } else if (this.state === 'home') {
            c.x = Math.min(d.chairX, c.x + 60 * dt);
            if (c.x >= d.chairX) this.state = 'rest';
        }
    }
}

// Gulls over a stretch of open deck (population: `gull_pool`, `gull_go`): they wheel overhead, or
// one sits on the rail. While she carries food there one of them dives at it: its shadow shows on
// the deck where she will be in a second, then it comes down on that spot. If she is there, it has
// her cone (never a fright: she fetches another). The way past: not to be where the shadow is.
export class FoodGulls {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, count, perch: { x, y }, off: a flag that keeps them away }
        this.top = def.y - 112;
        this.birds = [];
        for (let i = 0; i < def.count; i++) {
            const sprite = s.add.image(def.x, this.top, 'things', def.perch ? 'gull-perched' : 'gull-up').setOrigin(0.5, 1).setDepth(D.player + 0.34);
            this.birds.push({ sprite, phase: i * Math.PI, x: def.x, y: this.top });
        }
        this.shadow = s.add.ellipse(def.x, def.y - 1, 22, 5, 0x2e222f, 0.45).setDepth(D.decor + 0.32).setVisible(false);
        this.loot = s.add.image(0, 0, 'load-cone').setOrigin(0.5, 1).setDepth(D.player + 0.35).setVisible(false);
        world.add([...this.birds.map(b => b.sprite), this.shadow, this.loot]);
        this.state = 'idle';
        this.at = 0;
        this.diver = this.birds[0];
    }

    // Kept off for good (the kid squirts them): they wheel higher, and never dive.
    off() {
        return !!this.def.off && this.world.progress.has(this.def.off);
    }

    // Where a bird waits: wheeling over the stretch, or on its perch.
    home(b, time) {
        const d = this.def;
        if (d.perch) return { x: d.perch.x, y: d.perch.y, perched: true };
        const t = time / 1900 + b.phase, r = (d.x1 - d.x0) / 2 + 60;
        return { x: d.x + Math.cos(t) * r, y: this.top - (this.off() ? 34 : 0) + Math.sin(t * 2) * 9, dir: -Math.sin(t) };
    }

    // A cone dropped on the deck: one comes down for it, stays a moment, and goes.
    pounce(x) {
        if (this.state !== 'idle') return;
        this.state = 'pounce';
        this.targetX = x;
        this.at = this.scene.time.now + 2600;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (!nearby(s, d)) return;
        const frames = s.textures.get('things');
        const flap = Math.floor(time / 130) % 2 && frames.has('gull-down') ? 'gull-down' : 'gull-up';
        for (const b of this.birds) {
            if (b === this.diver && this.state !== 'idle') continue;
            const h = this.home(b, time);
            b.x += (h.x - b.x) * Math.min(1, dt * 4);
            b.y += (h.y - b.y) * Math.min(1, dt * 4);
            const settled = h.perched && Math.abs(b.x - h.x) < 2 && Math.abs(b.y - h.y) < 2;
            b.sprite.setFrame(settled ? 'gull-perched' : flap).setPosition(b.x, b.y).setFlipX(h.perched ? false : h.dir < 0);
        }
        const carry = this.world.carry;
        const food = carry && FOOD.includes(carry.kind);
        const inZone = here(s, d) && Math.abs(p.y - d.y) < 60 && p.x > d.x0 && p.x < d.x1;
        const b = this.diver;
        if (this.state === 'idle') {
            if (food && inZone && !this.off() && time > this.at) {
                // Its shadow, where she will be if she keeps on as she goes.
                this.state = 'mark';
                this.at = time + 950;
                this.targetX = Phaser.Math.Clamp(p.x + p.body.velocity.x * 0.95, d.x0 + 6, d.x1 - 6);
                this.shadow.setPosition(this.targetX, d.y - 1).setVisible(true).setScale(0.4);
                s.tweens.add({ targets: this.shadow, scale: 1.2, duration: 950 });
                sfx.whoosh();
            }
        } else if (this.state === 'mark') {
            // It hangs over the spot.
            b.x += (this.targetX - b.x) * Math.min(1, dt * 5);
            b.y += (this.top + 26 - b.y) * Math.min(1, dt * 5);
            b.sprite.setFrame(flap).setPosition(b.x, b.y);
            if (time > this.at) {
                this.state = 'dive';
                this.at = time + 230;
                this.from = { x: b.x, y: b.y };
            }
        } else if (this.state === 'dive') {
            const k = 1 - Math.max(0, this.at - time) / 230;
            b.x = this.from.x + (this.targetX - this.from.x) * k;
            b.y = this.from.y + (d.y - 30 - this.from.y) * k * k;
            b.sprite.setFrame('gull-down').setPosition(b.x, b.y);
            if (time > this.at) {
                this.shadow.setVisible(false);
                const got = this.world.carry && FOOD.includes(this.world.carry.kind) && here(s, d)
                    && Math.abs(p.x - this.targetX) < 17 && p.y > d.y - 30;
                if (got) {
                    const kind = this.world.carry.kind;
                    this.world.carryBox.give();
                    this.loot.setTexture(kind === 'stub' ? 'load-stub' : kind === 'cone' ? 'load-cone' : 'tray').setVisible(true);
                    this.world.say('Гей!', 900);
                    sfx.pickup();
                    this.stolen = (this.stolen ?? 0) + 1;
                }
                this.state = 'up';
                this.at = time + 900;
            }
        } else if (this.state === 'up') {
            b.y -= 150 * dt;
            b.x += 60 * dt;
            b.sprite.setFrame(flap).setPosition(b.x, b.y);
            this.loot.setPosition(b.x, b.y + 6);
            if (time > this.at) {
                this.loot.setVisible(false);
                this.state = 'idle';
                this.at = time + 2800;
            }
        } else if (this.state === 'pounce') {
            // Down beside the mess on the deck; a few pecks; away.
            const landed = Math.abs(b.x - this.targetX) < 2 && Math.abs(b.y - d.y) < 2;
            b.x += (this.targetX - b.x) * Math.min(1, dt * 5);
            b.y += (d.y - b.y) * Math.min(1, dt * 5);
            b.sprite.setFrame(landed ? 'gull-perched' : flap).setPosition(b.x, landed ? d.y - (Math.floor(time / 160) % 2) : b.y);
            if (time > this.at) {
                this.state = 'idle';
                this.at = time + 1500;
            }
        }
    }
}

// The buffet queue (population: `haz_queue`): six passengers with full trays shuffling from the
// buffet along the aisle, in two threes. Each is a body in her way that she can't walk through (no
// fright: she is held back) and hops, one at a time. For a crew member with a tray in her hands
// they turn aside against the tables and let her by. They come out from behind the buffet and go
// in behind the ice cream counter, round and round.
export class Queue {
    constructor(world, def) {
        const s = world.scene;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, v (m/s), who: [...] }
        this.len = def.x1 - def.x0;
        const offsets = [0, 46, 92, 300, 346, 392];
        this.people = def.who.map((who, i) => {
            const p = world.people.add({ id: `${def.id}_${i + 1}`, who, x: def.x0, y: def.y, route: 'inside', face: 1 });
            if (p) {
                p.along = (this.len * 0.2 + offsets[i % offsets.length] + Math.floor(i / offsets.length) * 520) % this.len;
                p.depth0 = p.sprite.depth;
            }
            return p;
        }).filter(Boolean);
        this.span = 392;
    }

    update(dt, time) {
        const s = this.scene, her = s.player, d = this.def, P = this.world.people;
        if (!nearby(s, d)) return;
        // A shuffle: a few steps, a wait.
        const moving = (time % 2000) < 1150;
        const tray = !!this.world.carry;
        for (const p of this.people) {
            if (moving) p.along = (p.along + d.v * M * 1.74 * dt) % this.len;
            p.x = d.x0 + p.along;
            // Out from behind the buffet, in behind the ice cream counter: faint and out of the way at the ends.
            const edge = Math.min(p.along, this.len - p.along);
            const hidden = edge < 26;
            // For crew with a tray: turned aside, against the tables.
            const yields = tray && here(s, d) && Math.abs(her.y - d.y) < 60 && Math.abs(her.x - p.x) < 62;
            if (yields !== p.aside) {
                p.aside = yields;
                p.sprite.setDepth(p.depth0 - (yields ? 5 : 0));
                if (yields) {
                    p.sprite.anims.stop();
                    p.sprite.setFrame(p.meta.back ?? p.meta.stand);
                }
            }
            if (!p.aside) {
                if (moving && P.anim(p, 'walk')) { /* walking */ } else {
                    p.sprite.anims.stop();
                    p.sprite.setFrame(p.meta.stand);
                }
            }
            p.sprite.setAlpha(Phaser.Math.Clamp(edge / 26, 0, 1));
            P.place(p);
            p.blocking = !hidden && !p.aside;
            if (!p.blocking || !here(s, d)) continue;
            // In her way: she is held at their side (over their heads she is clear).
            const dx = her.x - p.x, reach = PLAYER.bodyWidth / 2 + 8;
            if (Math.abs(dx) < reach && her.y > d.y - 42 && Math.abs(her.y - d.y) < 60) {
                const side = dx === 0 ? (her.flipX ? 1 : -1) : Math.sign(dx);
                const to = p.x + side * reach;
                her.body.x += to - her.x;
                her.x = to;
                if (her.body.velocity.x * side < 0) her.body.velocity.x = 0;
                if (time > (this.bumpAt ?? 0)) {
                    this.bumpAt = time + 700;
                    sfx.land();
                }
            }
        }
    }
}

// Room-service trays left on a hallway's floor outside a "Do Not Disturb" door (population:
// `haz_trays`): walked onto, they clatter, and the door flies open on someone not dressed for
// visitors: "Startled". A jump clears them.
export class Trays {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x0, x1, y, door: the id of its DndDoor, flag }
        world.carryBox.textures();
        this.items = [];
        const n = 3, w = def.x1 - def.x0;
        for (let i = 0; i < n; i++) {
            const x = def.x0 + 14 + (i * (w - 28)) / (n - 1);
            const tray = s.add.image(x, def.y, 'tray').setOrigin(0.5, 1).setDepth(D.props + 0.02);
            const top = s.add.image(x + (i % 2 ? 3 : -2), def.y - 3, i === 1 ? 'load-cloche' : 'shipart', i === 1 ? undefined : 'coffee-cup')
                .setOrigin(0.5, 1).setDepth(D.props + 0.03);
            this.items.push(tray, top);
        }
        world.add(this.items);
        this.armed = true;
    }

    update(dt, time) {
        const s = this.scene, p = s.player, d = this.def;
        if (!nearby(s, d)) return;
        const onFloor = p.body.blocked.down || p.body.touching.down;
        const on = here(s, d) && Math.abs(p.y - d.y) < 2 && onFloor && p.x > d.x0 && p.x < d.x1;
        if (!on) {
            if (Math.abs(p.x - d.x) > 3 * M) this.armed = true;
            return;
        }
        if (!this.armed) return;
        this.armed = false;
        sfx.smash();
        this.world.progress.setFlag(d.flag);
        this.items.forEach((img, i) => s.tweens.add({ targets: img, y: img.y - 5 - (i % 3) * 2, angle: (i % 2 ? 9 : -9), duration: 90, yoyo: true, repeat: 2 }));
        const door = this.world.movers.find(m => m.def?.id === d.door);
        // (If she is still there: gone at once, she only hears it.)
        s.time.delayedCall(380, () => { if (here(s, d) && Math.abs(s.player.x - d.x) < 3 * M) door?.knock(); });
    }
}
