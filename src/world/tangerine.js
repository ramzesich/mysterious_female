// A tangerine loose in the world (docs/plan-three-uses.md §1.2, §1.3, §3): knocked out of her
// pocket by a hit, or thrown (F: `throw`). One real thing, whichever it was: it bounces and
// rolls, off steps and edges, stops against anything solid, and lies where it stopped until she
// walks over it, today or next week (`save.loose`). Off the hull it goes into the sea, gone; in a
// pool it floats. While it is loose it is offered each frame to whatever is near
// (`world.offered(t)`): the first to want it has it.

import { PLAYER, LOOSE } from '../config.js';
import { sfx } from '../sfx.js';
import { OUTSIDE } from './world.js';

let made = 0;

export class LooseTangerines {
    constructor(scene) {
        this.scene = scene;
        this.all = [];
        this.group = scene.physics.add.group();
        scene.save.loose ??= [];
        // The ones she left lying, where she left them.
        for (const e of scene.save.loose) this.make(e, true);
    }

    // The same floors and walls as hers, by its own route (ShipScene.buildPlayer, World.addColliders).
    addColliders() {
        const s = this.scene, w = s.world;
        const route = o => o.loose.route;
        // (Phaser hands a group against a single body over in the other order: the tangerine first.)
        const add = (other, test) => s.physics.add.collider(this.group, other, null,
            test && ((a, b) => a.loose ? test(a, b) : test(b, a)));
        add(s.solidLayer, (o, tile) => {
            const r = route(o);
            if (r === OUTSIDE || r === 'duct') return false;
            const room = w.rooms[r];
            return !(room?.def && tile.pixelY < room.floor);
        });
        add(s.routeWalls || [], (o, zone) => zone.route === route(o));
        for (const b of s.bulkheads) add(b.zone, o => !b.open && route(o) === 'inside');
        add(s.railingStops || []);
        if (s.cabin) add(s.cabin.bed, (o, bed) => route(o) === 'cabin' && o.body.velocity.y >= 0 && o.body.bottom <= bed.body.top + 6);
        // (A side walk, a balcony's floor: from above only.)
        add(s.walkGroup, (o, zone) => route(o) === 'inside' && o.body.velocity.y >= 0 && o.body.bottom <= zone.body.top + 6);
        add(s.crates, o => route(o) === 'inside');
        add(w.platZones, (o, z) => route(o) === OUTSIDE
            && (z.plat.solid || (o.body.velocity.y >= 0 && o.body.bottom <= z.body.top + 6)));
        add(w.wallZones, o => route(o) === OUTSIDE);
        if (w.ductFloor) add(w.ductFloor, o => route(o) === 'duct');
        for (const t of [...w.pushables, ...w.lows, ...w.solids]) add(t.zone, o => t.route === route(o));
        for (const t of w.breakables) add(t.zone, o => !t.done && t.route === route(o));
        for (const r of w.robots ?? []) add(r.zone, o => route(o) === 'inside');
        // (A rope or a fire door that holds her holds it.)
        for (const b of s.progress.barriers) add(b.zone, o => route(o) === 'inside' && s.progress.barrierHolds(b));
    }

    // Knocked out of her pocket at (x, y), flying off the way `away` says (§1.3).
    knock(x, y, away, f = 1) {
        const k = LOOSE.knock;
        const t = this.make({ x, y, route: this.scene.route }, false);
        t.img.body.setVelocity(away * k.vx * f, -k.vy);
        t.pickableAt = this.scene.time.now + LOOSE.pickDelayMs;
        return t;
    }

    // Thrown from her hand at (x, y) (§1.2): a roll, or a lob. `thrown` while it flies and rolls,
    // for whatever answers only a throw (Bumbot bats it back).
    throw(x, y, vx, vy, lob) {
        const t = this.make({ x, y, route: this.scene.route }, false);
        t.img.body.setVelocity(vx, vy);
        t.thrown = true;
        t.lob = lob;
        t.pickableAt = this.scene.time.now + LOOSE.pickDelayMs;
        return t;
    }

    make(e, resting) {
        const s = this.scene;
        const id = e.id ?? `loose_${Date.now().toString(36)}_${made++}`;
        const outside = e.route !== 'inside';
        // (Its position is the fruit's middle, under its leaves, so that it turns about itself as
        // it rolls: src/textures.js.)
        const img = this.group.create(e.x, e.y, 'tangerine').setOrigin(0.5, 0.6)
            .setDepth(outside ? s.DEPTH.exterior + 0.13 : s.DEPTH.props + 0.05);
        s.worldLayer.add(img);
        // (The fruit fills the picture's rows 2 to 9 and its ten columns; the body is the fruit,
        // a pixel in from its sides.)
        img.body.setSize(8, 8).setOffset(1, 2);
        img.body.setBounce(LOOSE.bounce, LOOSE.bounce);
        img.body.setMaxVelocity(1000, PLAYER.maxFall);
        const t = { id, img, route: e.route, resting: false, floating: !!e.float, spin: 0, still: 0, vyWas: 0, pickableAt: 0 };
        img.loose = t;
        this.all.push(t);
        if (!s.save.loose.some(o => o.id === id)) s.save.loose.push({ id, x: e.x, y: e.y, route: e.route });
        if (resting) this.rest(t);
        return t;
    }

    // At rest: a tangerine on the floor like any other, kept where it lies.
    rest(t) {
        t.resting = true;
        t.thrown = false;
        t.img.body.setVelocity(0, 0);
        t.img.disableBody(false, false);
        const e = this.scene.save.loose.find(o => o.id === t.id);
        if (e) Object.assign(e, { x: Math.round(t.img.x), y: Math.round(t.img.y), float: t.floating || undefined });
        if (t.floating) {
            this.scene.tweens.add({ targets: t.img, y: t.img.y + 1, duration: 600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        }
    }

    // Gone: picked up, taken by something, or lost to the sea.
    remove(t) {
        this.claim(t).destroy();
    }

    // Taken by something that carries it off itself (a gull in its beak): no longer loose nor
    // saved, its picture handed over, the taker's to move and destroy.
    claim(t) {
        const s = this.scene;
        this.all = this.all.filter(o => o !== t);
        s.save.loose = s.save.loose.filter(o => o.id !== t.id);
        s.tweens.killTweensOf(t.img);
        t.img.disableBody(false, false);
        return t.img.setAngle(0);
    }

    update(dt) {
        const s = this.scene, p = s.player, time = s.time.now;
        for (const t of [...this.all]) {
            const img = t.img, b = img.body;
            // (Shown on its own route; one inside shows wherever the deck does, as the others.)
            img.setVisible(t.route === 'inside' || t.route === s.route);
            if (this.pickedUp(t, p, time)) continue;
            // (Lying still too: a vacuum comes by, a gull comes down to it.)
            if (s.world.offered?.(t)) continue;
            if (t.resting) continue;
            // Over the side: into the sea, gone. Off the bottom of the map: gone.
            if ((img.x < s.hullMinX || img.x > s.hullMaxX) && img.y >= s.waterY) {
                s.splash(img.x, s.waterY);
                sfx.at(img.x, s.waterY).splashSmall();
                this.remove(t);
                continue;
            }
            if (img.y > s.map.heightInPixels + 200) {
                this.remove(t);
                continue;
            }
            // Into a pool: it floats, to be swum to.
            const pool = t.route === 'inside' && s.pools.find(w => img.x > w.x0 && img.x < w.x1 && img.y > w.y + 2 && img.y < w.bottom + 16);
            if (pool) {
                sfx.at(img.x, pool.y).splashSmall();
                img.setPosition(img.x, pool.y).setAngle(0);
                t.floating = true;
                this.rest(t);
                continue;
            }
            const onFloor = b.blocked.down || b.touching.down;
            if (onFloor && t.vyWas > LOOSE.thudAt) sfx.at(img.x, img.y).plop();
            if (onFloor && t.vyWas > LOOSE.hardAt) b.velocity.x *= LOOSE.landKeep;
            if (onFloor) b.velocity.x = approachZero(b.velocity.x, LOOSE.rollDecel * dt);
            t.vyWas = b.velocity.y;
            // It turns as it rolls, a quarter at a time (an 8 px fruit turned by degrees only blurs).
            t.spin += b.velocity.x * dt / 3;
            img.setAngle(Math.round(t.spin / (Math.PI / 2)) * 90);
            if (onFloor && Math.abs(b.velocity.x) < LOOSE.rest && Math.abs(b.velocity.y) < 25) {
                t.still += dt;
                if (t.still > 0.15) this.rest(t);
            } else t.still = 0;
        }
    }

    // Is it at (x, y) on `route`, give or take `dx` and `dy`? `y` is a floor (feet), as people's are:
    // what its own foot is measured against (a taker's test).
    near(t, x, y, dx, dy, route = 'inside') {
        return t.route === route && Math.abs(t.img.x - x) < dx && Math.abs(t.img.y + 3 - y) < dy;
    }

    // She walks over it (or swims to it), as she would any tangerine.
    pickedUp(t, p, time) {
        const s = this.scene, img = t.img, foot = img.y + 3;
        if (time < t.pickableAt || t.route !== s.route) return false;
        if (!['play', 'ladder', 'stairs', 'swim'].includes(s.mode)) return false;
        const near = t.floating
            ? Math.abs(p.x - img.x) < 14 && Math.abs(p.y - img.y) < 60
            : Math.abs(p.x - img.x) < LOOSE.reach && foot > p.y - PLAYER.height && foot - 8 < p.y;
        if (!near) return false;
        s.gainTangerine(img.x, img.y);
        s.tweens.killTweensOf(img);
        this.all = this.all.filter(o => o !== t);
        s.save.loose = s.save.loose.filter(o => o.id !== t.id);
        // (Its picture is the one that flies to the count: §1.7.)
        img.destroy();
        s.refreshHud();
        return true;
    }
}

function approachZero(v, by) {
    return v > 0 ? Math.max(0, v - by) : Math.min(0, v + by);
}
