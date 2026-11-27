// Region 9, "The bow" (GAME_DESIGN.md §6.1.3, docs/population.md decks 7, 9, 10, 11 and 12 forward,
// §6.9-6.10 and 6.12): the region's own things (the sauna's steam, the kids' club's ball pit, the
// step class's boards, the bridge's alarm) and its part of the story, mixed into the Story: the
// wedding planner and the cake (carried from Cagney's: a fragile load, src/world/carry.js), the
// party filing into the chapel and the ceremony there, the Spinnaker's piano, the kids' pool's
// slide, the captain's door, near-catch 6 on the bridge (its own module since its remake, src/world/bridge.js; it was: the security officer's net comes down on
// the alarm panel, the hatch's ladder drops, Bumbot is up it), and the Library's odd book, which
// opens the reading nook once all fourteen books are back. Places come from maps/world.json (`bow`).

import { PLAYER, GAGS } from '../config.js';
import { sfx } from '../sfx.js';
import { rumble } from '../rumble.js';
import { t } from '../lang.js';
import { writeSave } from '../save.js';
import { PillowSiege, Tag } from './splash.js';

const M = 48;
const HALF = PLAYER.height / 2;
const near = (s, x, y, dx = 900, dy = 320) => Math.abs(s.player.x - x) < dx && Math.abs(s.player.y - y) < dy;
const BALLS = [0xe83b3b, 0xf9c22b, 0x4d9be6, 0x1ebc73, 0x905ea9, 0xf68181];

// The sauna's steam (population: `haz_steam`; the user, 2026-11-22: no longer rolling out of its aft door): up from the
// stove's coals inside the sauna, on a clock, a timing obstacle to pass as the sprinkler is. The tell: the coals glow
// and hiss, a few wisps curl up off them. Then a column of it rises from the coals to the ceiling and spreads under it,
// thinning; every puff kept inside the sauna's walls and under its ceiling (`x0`, `x1`, `top`: nothing of it outside).
// Caught in the column by the stove: "Fogged" (a tray is spilled), her gag 17 there in the sauna, then her checkpoint.
export class Steam {
    constructor(world, def) {
        const s = world.scene, D = s.DEPTH;
        this.world = world;
        this.scene = s;
        this.def = def;             // { x: the stove's middle, y: the floor, half, x0, x1, top, coals, period, on, tell }
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

    // A puff of steam, cut to fit inside the sauna: never past its walls or over its ceiling.
    puff(g, x, y, r, colour, alpha) {
        const d = this.def;
        r = Math.min(r, x - d.x0, d.x1 - x, y - d.top);
        if (r >= 1 && alpha > 0) g.fillStyle(colour, alpha).fillCircle(x, y, r);
    }

    // 17, the ship scene's `thingGag` (`gags` sheet, tools/build_gags.py): a burst of the steam wraps
    // her where she is (from her run she slides to a stop, `slideMs`, short of the sauna's doors), and under it she is in
    // her puff picture; it thins (`clearMs`): her hair frizzed into a huge puff, she fans herself and swoons, sitting down
    // dazed; then her checkpoint.
    ride() {
        const s = this.scene, d = this.def, p = s.player, g = GAGS.steam;
        return {
            play: (done) => {
                const m = s.cache.json.get('gags-meta');
                const dir = p.flipX ? -1 : 1, v = Math.abs(p.body?.velocity.x ?? 0) > 20 ? PLAYER.runSpeed : 0;
                const pic = s.add.sprite(p.x, d.y, 'gags', m.anims['steam-fan'][0])
                    .setOrigin(0.5, m.floor / m.cell).setFlipX(dir < 0).setDepth(p.depth);
                this.world.add([pic]);
                this.pic = pic;
                // (Doors and walls stop her slide: she stays in the sauna.)
                const x0 = pic.x, end = s.stopShort(pic.x, pic.x + dir * v * g.slideMs / 2000, d.y, 16);
                this.burst = { x: pic.x, t: 0 };
                // (Drawn at once: she is in her puff picture from this very frame.)
                this.drawBurst(this.g);
                sfx.at(pic.x, d.y).steam(0.6);
                let t = 0, coughed = false;
                s.time.delayedCall(g.coverMs + g.clearMs * 0.6 + g.holdPuffMs, () => {
                    pic.play('gags-steam-fan');
                    pic.once('animationcomplete-gags-steam-fan', () => {
                        pic.play('gags-steam-swoon');
                        s.time.delayedCall(g.plopAtMs, () => sfx.at(pic.x, d.y).plop());
                        pic.once('animationcomplete-gags-steam-swoon', () => done());
                    });
                });
                s.script = (dt) => {
                    t += dt * 1000;
                    const u = Math.min(1, t / g.slideMs);
                    pic.x = x0 + (end - x0) * (1 - (1 - u) * (1 - u));
                    if (!coughed && t > g.coverMs * 0.6) { coughed = true; sfx.at(pic.x, d.y).herCough(); }
                    this.burst.x = pic.x;
                    this.burst.t = t;
                    p.x = pic.x;
                };
            },
            show: () => {
                this.pic?.destroy();
                this.pic = null;
                this.burst = null;
            },
        };
    }

    // The burst round her (17): thick to `coverMs`, then thinning and rising over `clearMs`; inside the sauna's walls.
    drawBurst(g) {
        const b = this.burst, G = GAGS.steam;
        if (!b) return;
        const k = Math.max(0, (b.t - G.coverMs) / G.clearMs);
        if (k >= 1) return;
        const a = 1 - k * k, y = this.def.y;
        // (Three columns of five over her, her hair's puff and all, so that nothing of her shows.)
        for (let i = 0; i < 15; i++) {
            const ox = (i % 3 - 1) * 15 + ((i * 7) % 5) - 2, oy = 8 + Math.floor(i / 3) * 17 + ((i * 11) % 5);
            const r = 13 + ((i * 13) % 5) + k * 8;
            this.puff(g, b.x + ox * (1 + k * 0.6), y - oy - k * 26 + Math.sin(b.t / 200 + i) * 2, r, i % 4 ? 0xffffff : 0xc7dcd0, a);
        }
    }

    update(dt, time) {
        const s = this.scene, d = this.def, p = s.player, g = this.g.clear();
        this.drawBurst(g);
        // (Only while she is inside on its deck: drawn over her layer, it rose through the closed side of deck 11
        // under the Spinnaker, 2026-11-20.)
        if (!near(s, d.x, d.y, 700, 200) || s.route !== 'inside' || Math.abs(p.y - d.y) > 72) return;
        const [phase, k] = this.phase(time);
        if (phase === 'calm') {
            this.told = false;
            this.blown = false;
            return;
        }
        const coals = d.y - d.coals;
        if (phase === 'tell') {
            if (!this.told) {
                this.told = true;
                sfx.at(d.x, d.y).steam(0.3);
            }
            // The coals glow, and wisps curl up off them.
            for (let i = 0; i < 6; i++) {
                const glow = 0.5 + 0.5 * Math.sin(time / 90 + i * 1.7);
                g.fillStyle(i % 2 ? 0xfb6b1d : 0xf9c22b, 0.55 * glow).fillRect(d.x - 9 + i * 3, coals - 1 + (i % 2), 2, 1);
            }
            for (let i = 0; i < 5; i++) {
                const a = (time / 420 + i * 0.21) % 1;
                this.puff(g, d.x - 6 + i * 3 + Math.sin(time / 200 + i * 2.1) * 2, coals - 4 - a * 22, 1.5 + a * 2.5, 0xffffff, 0.7 * (1 - a) * k);
            }
            return;
        }
        // The column: up from the coals to the ceiling, then out under it toward the walls, thinning as it goes.
        if (!this.blown) {
            this.blown = true;
            sfx.at(d.x, d.y).steam(Math.max(0.3, d.on));
        }
        const env = k < 0.15 ? k / 0.15 : k > 0.7 ? Math.max(0, (1 - k) / 0.3) : 1;
        // (Dispersing to the sides as it rises, not only up (the user, 2026-11-22): each puff drifts out to its own side,
        // the higher the further, a cone; `puff` keeps it inside the walls.)
        const rise = coals - d.top, up = rise * Math.min(1, k * 3 + 0.2);
        for (let i = 0; i < 26; i++) {
            const f = (i * 0.618 + time / 700) % 1;             // how far up this puff is, 0 at the coals
            if (f * rise > up) continue;
            // (its own way out, -1 to 1, scattered: a sequence in step with `f` lined the puffs up in one leaning curve)
            const side = ((Math.sin(i * 12.9898 + 4.1) * 43758.5453) % 1 + 1) % 1 * 2 - 1;
            const y = coals - f * rise * (0.85 + 0.15 * Math.abs(side));
            const x = d.x + side * Math.sqrt(f) * 64 + Math.sin(time / 230 + i * 1.3) * (2 + f * 4);
            this.puff(g, x, y, 5 + f * 8 + ((i * 13) % 4), i % 3 ? 0xffffff : 0xc7dcd0, (0.8 - f * 0.35) * env);
        }
        // (Under the ceiling, once it is up there: spreading toward both walls.)
        const spread = Math.max(0, k * 3 + 0.2 - 1) / 1.2;
        for (let i = 0; i < 14 && spread > 0; i++) {
            const f = ((i * 0.381 + time / 1100) % 1) * Math.min(1, spread);
            const side = i % 2 ? 1 : -1, reach = side > 0 ? d.x1 - d.x : d.x - d.x0;
            const x = d.x + side * f * reach, y = d.top + 10 + ((i * 7) % 12) + Math.sin(time / 260 + i) * 2;
            this.puff(g, x, y, 8 + ((i * 11) % 5) + f * 4, i % 3 ? 0xffffff : 0xc7dcd0, (0.6 - f * 0.4) * env);
        }
        // Caught in the column by the stove.
        if (env < 0.6 || s.mode !== 'play' || s.route !== 'inside' || time < this.hitAt) return;
        if (Math.abs(p.x - d.x) > d.half + 6 || Math.abs(p.y - d.y) > 80) return;
        this.hitAt = time + 1500;
        if (this.world.carry) this.world.carryBox.spill(d.x, false, 'steam');
        else s.scareContact(d.x, 'steam', { ride: this.ride() });
    }
}

// The DJ's fog machine at Bliss (population: `FOG`, `haz_fog`; plan-the-rest §7f, 5, the user's choices, 2026-11-26): a
// small machine on the floor at the DJ booth's front, its nozzle forward. On the sauna's clock: the tell (its light
// blinks red, wisps leave the nozzle, a hiss), then a low puff rolls forward along the floor under the disco ball, rising
// a little as it goes, and thins. Caught in it, under its top (a hop over its low front clears it): gag 17, as the sauna's
// steam (`Steam.ride`, its cloud kept inside Bliss's walls). Drawn only while she is inside on deck 6.
// The machine's picture (`fog-machine`, 31 x 17, tools/build_things.py): its light at px 10 to 13 of rows 3 and 4, its
// nozzle's mouth at its left end, row 11.
const FOG_PIC = { w: 31, h: 17, light: [10, 3, 4, 2], nozzle: 11 };
export class Fog extends Steam {
    constructor(world, def) {
        super(world, def);
        const s = world.scene, D = s.DEPTH;
        this.machine = s.add.image(def.x, def.y, 'things', 'fog-machine').setOrigin(0.5, 1).setDepth(D.props);
        this.lamp = s.add.graphics().setDepth(D.props + 0.01);
        world.add([this.machine, this.lamp]);
        // (Solid, as the standing carts: she hops it, never walks through it.)
        const zone = s.add.zone(def.x, def.y, FOG_PIC.w - 6, FOG_PIC.h - 3).setOrigin(0.5, 1);
        s.physics.add.existing(zone, true);
        world.solids.push({ id: def.id, route: 'inside', zone });
        this.left = def.x - Math.round(FOG_PIC.w / 2);
        this.mouth = { x: this.left, y: def.y - FOG_PIC.h + FOG_PIC.nozzle };
    }

    // The puff's top over the floor at `x` (px up), and how far forward it has rolled (0 to 1) at `k` of its time.
    reachAt(k) { return Math.min(1, k / 0.3); }
    topAt(x) { const f = Math.max(0, Math.min(1, (this.mouth.x - x) / this.def.reach)); return 9 + f * 17; }

    // (A puff of the machine's, never past the trunk's door's frame, `stop`. The gag's cloud round her is not cut there: cut,
    // it ended in a hard edge down the door; it drifts in front of it inside Bliss's walls, as the sauna's.)
    fogPuff(g, x, y, r, colour, alpha) {
        this.puff(g, x, y, Math.min(r, x - this.def.stop), colour, alpha);
    }

    update(dt, time) {
        const s = this.scene, d = this.def, p = s.player, g = this.g.clear();
        this.lamp.clear();
        this.drawBurst(g);
        if (!near(s, d.x, d.y, 700, 200) || s.route !== 'inside' || Math.abs(p.y - d.y) > 72) return;
        const [phase, k] = this.phase(time), m = this.mouth;
        if (phase === 'calm') {
            this.told = false;
            this.blown = false;
            return;
        }
        if (phase === 'tell') {
            if (!this.told) {
                this.told = true;
                sfx.at(m.x, d.y).steam(0.3);
            }
            // Its light blinks red; wisps curl out of the nozzle.
            const [lx, ly, lw, lh] = FOG_PIC.light;
            if (Math.floor(time / 150) % 2 === 0) this.lamp.fillStyle(0xe83b3b, 1).fillRect(this.left + lx, d.y - FOG_PIC.h + ly, lw * 2, lh);
            for (let i = 0; i < 4; i++) {
                const a = (time / 380 + i * 0.25) % 1;
                this.fogPuff(g, m.x - 2 - a * 16, m.y - a * 6 + Math.sin(time / 150 + i * 2) * 1.5, 1.5 + a * 2.5, 0xffffff, 0.7 * (1 - a) * k);
            }
            return;
        }
        if (!this.blown) {
            this.blown = true;
            sfx.at(m.x, d.y).steam(Math.max(0.3, d.on));
        }
        const env = k < 0.12 ? k / 0.12 : k > 0.7 ? Math.max(0, (1 - k) / 0.3) : 1;
        const out = this.reachAt(k) * d.reach;
        // The puff: rolling forward low along the floor from the nozzle, rising and swelling as it goes; its rolls turn.
        for (let i = 0; i < 30; i++) {
            const f = (i * 0.618 + time / 900) % 1;
            if (f * d.reach > out) continue;
            const x = m.x - f * d.reach + Math.sin(time / 240 + i * 1.7) * (1 + f * 3);
            const r = 3 + f * 7 + ((i * 13) % 3);
            const y = Math.min(d.y - r * 0.6, m.y - f * 9 + Math.sin(time / 300 + i) * 1.5);
            this.fogPuff(g, x, y, r, i % 3 ? 0xffffff : 0xc7dcd0, (0.5 - f * 0.2) * env);
        }
        // Caught in it: under its top where she stands, inside its reach.
        if (env < 0.6 || s.mode !== 'play' || s.route !== 'inside' || time < this.hitAt) return;
        const body = PLAYER.bodyWidth / 2;
        if (p.x + body < m.x - out || p.x - body > m.x + 2 || Math.abs(p.y - d.y) > 80) return;
        if (p.y < d.y - this.topAt(Math.min(m.x, p.x + body))) return;
        this.hitAt = time + 1500;
        if (this.world.carry) this.world.carryBox.spill(p.x, false, 'steam');
        else s.scareContact(m.x, 'steam', { ride: this.ride() });
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
        s.withFoot(front);          // (to her floor's own row: her feet hidden whole)
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
        s.behindShell(this.odd, def.tanX, y);       // (behind the ship's side from outside, as the pit's front is)
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
        if (time > (this.soundAt ?? 0)) {
            this.soundAt = time + 330;
            sfx.balls();
        }
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
        // Splash Academy's kids: the pillow siege over the castle, and tag aft of it (src/world/splash.js).
        if (B.siege) w.movers.push(new PillowSiege(w, B.siege));
        if (B.tag) w.movers.push(new Tag(w, B.tag));

        // (The step class's boards are in its two's own clip since 2026-11-26: they step up onto them, tools/cast.py.)

        // What E does here: the piano, the slide's ladder, the captain's door, the odd book.
        w.things.push({ id: 'sec_piano', x: B.piano.x, y: B.piano.y, route: 'inside', items: [], reach: 14, interact: () => this.piano() });
        w.things.push({ id: 'sec_slide', x: B.slide.ladderX, y: B.slide.y, route: 'inside', items: [], reach: 12, interact: () => this.slide() });
        w.things.push({ id: 'sec_captain', x: B.captain.x, y: B.captain.y, route: 'inside', items: [], reach: 14, interact: () => this.knock() });

        // The odd book on the Library's bookcase: standing in the top shelf of its third glass door among
        // the lit books, a dark teal spine with two gold bands a px taller than they are (the user,
        // 2026-11-21: it had hung on the glass's front). `N.up` is its foot, on that shelf (the bookcase's
        // row 14; its columns 38 to 40). With all fourteen back it glints. Behind the bookcase, once it has slid
        // aside (the user, 2026-11-22): the entrance to the reading nook, a wooden casing round a view of the nook's
        // lamp and armchair, washed as a background is (`nookEntrance()`).
        const N = B.nook;
        this.oddBook = s.add.graphics().setDepth(D.decor + 0.2);
        this.oddBook.fillStyle(0x0b5e65, 1).fillRect(-1, -6, 3, 7);
        this.oddBook.fillStyle(0xf9c22b, 1).fillRect(-1, -4, 3, 1).fillRect(-1, -1, 3, 1);
        this.oddBook.setPosition(N.x + 8, N.y - N.up);
        this.oddGlint = s.add.image(N.x + 9, N.y - N.up - 7, 'dot').setTint(0xfbff86).setDepth(D.decor + 0.21);
        s.tweens.add({ targets: this.oddGlint, alpha: { from: 0.1, to: 1 }, scale: { from: 0.6, to: 1.8 }, duration: 500, yoyo: true, repeat: -1, repeatDelay: 700 });
        // (Under the bookcases: the bookcase that slides is between it and the other one, `nookCases()`.)
        this.nookWay = s.add.image(N.x, N.y, this.nookEntrance()).setOrigin(0.5, 1).setDepth(D.decor + 0.09).setVisible(false);
        w.add([this.oddBook, this.oddGlint, this.nookWay]);
        w.things.push({ id: 'sec_oddbook', x: N.x + 9, y: N.y, route: 'inside', items: [], reach: 18, until: 'flag:nook', interact: () => this.oddBookPull() });

        // (The bridge's alarm and near-catch 6: src/world/bridge.js, `setupBridge`.)
        this.refreshBow();
    },

    refreshBow() {
        if (!this.B) return;
        const P = this.P, nook = P.has('nook');
        this.oddBook?.setVisible(!nook);
        this.oddGlint?.setVisible(!nook && P.has('books_all'));
        this.nookWay?.setVisible(nook);
        const cases = this.nookCases();
        if (cases && nook && !this.pulling) cases.slide.setX(cases.home + cases.slide.width);
    },

    // The Library's two bookcases by the odd book: the one it stands in (it slides) and the one to its right (it slides
    // behind that one). Found once among the built props by their picture.
    nookCases() {
        if (this.cases) return this.cases;
        const s = this.scene, N = this.B.nook;
        const all = [s.children.list, ...s.children.list.filter(l => l.list).map(l => l.list)].flat()
            .filter(o => o.frame?.name?.startsWith?.('bookcase') && Math.abs(o.y - N.y) < 2);
        const slide = all.find(o => Math.abs(o.x - N.x) < 4);
        const other = slide && all.find(o => o !== slide && Math.abs(o.x - (slide.x + slide.width)) < 4);
        if (!slide || !other) return null;
        slide.setDepth(other.depth - 0.002);
        return (this.cases = { slide, other, home: slide.x });
    },

    // The way into the reading nook, as the bookcase leaves it (the user, 2026-11-22: "a proper entrance to the reading
    // room, with the reading room's background's relevant parts washed out and visible"): the nook's own picture
    // (`tools/draw_rooms.py`'s `nook`) at its lamp and armchair, washed 35% toward its wall as a background is, in a
    // wooden casing of the Library's dark wood, the bookcase's size.
    nookEntrance() {
        const s = this.scene, key = 'nook-entrance';
        if (s.textures.exists(key)) return key;
        const W = 62, H = 58, FLOOR = 128, src = s.textures.get('room-nook').getSourceImage();
        const tex = s.textures.createCanvas(key, W, H), ctx = tex.getContext();
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(src, 94, FLOOR - H + 3, W - 6, H - 3, 3, 3, W - 6, H - 3);
        const img = ctx.getImageData(0, 0, W, H), d = img.data, wall = [0x7a, 0x30, 0x45];
        for (let i = 0; i < d.length; i += 4) for (let c = 0; c < 3; c++) d[i + c] = Math.round(d[i + c] + (wall[c] - d[i + c]) * 0.35);
        ctx.putImageData(img, 0, 0);
        // The casing: a dark outer line, the wood, a lit edge along its inside; the threshold a darker board.
        const r = (c, x, y, w, h) => { ctx.fillStyle = c; ctx.fillRect(x, y, w, h); };
        r('#2e222f', 0, 0, W, 3); r('#2e222f', 0, 0, 3, H); r('#2e222f', W - 3, 0, 3, H);
        r('#7a4528', 1, 1, W - 2, 2); r('#7a4528', 1, 1, 2, H - 1); r('#7a4528', W - 3, 1, 2, H - 1);
        r('#ab947a', 2, 2, W - 4, 1); r('#ab947a', 2, 2, 1, H - 2);
        r('#46291f', 3, H - 1, W - 6, 1);
        tex.refresh();
        return key;
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
        // A cake gone over: the pastry chef's sigh, the next time she stands before him.
        const has = w.carry?.kind === 'cake';
        if (this.hadCake && !has && !this.handing && !P.has('wedding')) this.sighDue = true;
        this.hadCake = has;
        const chef = this.who('npc_pastrychef');
        if (this.sighDue && chef?.on && chef.state !== 'acting' && play && Math.abs(her.y - chef.y) < 8 && Math.abs(her.x - chef.x) < 3 * M) {
            this.sighDue = false;
            this.people.play(chef, 'sigh');
            sfx.at(chef.x, chef.y).grumble();
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
            sfx.give();
            await w.tween({ targets: cake, x: pl.x + pl.dir * 13, y: pl.y - 30, duration: 420, ease: 'Sine.easeInOut' });
            sfx.at(pl.x, pl.y).aah();
            sfx.done();
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
            sfx.doorHeavy();
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
            sfx.bells();
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
            sfx.at(mid, y).kiss();
            sfx.at(mid, y).bells();
            sfx.at(mid, y).cheer(2.6);
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
            if (slot) sfx.at(slot.x, slot.y).sparkle();
        });
    },

    // A tangerine coming down on the Spinnaker's keys: a note where it lands (docs/plan-three-uses.md
    // §2). It rolls on. (Her hands are on the keys a little ahead of where she stands to play.)
    pianoOffered(t) {
        const B = this.B?.piano, s = this.scene;
        if (!B || t.route !== 'inside' || t.img.body.velocity.y <= 0 || s.time.now < (t.noteAt ?? 0)) return false;
        const x = t.img.x, y = t.img.y;
        if (x < B.x + 6 || x > B.x + 40 || y < B.y - 34 || y > B.y - 18) return false;
        t.noteAt = s.time.now + 400;
        sfx.at(x, y).piano(Phaser.Math.Between(0, 15));
        const n = s.add.text(x, y - 12, '♪', { fontFamily: 'Verdana, sans-serif', fontSize: '10px', color: '#2e222f', stroke: '#ffffff', strokeThickness: 2, resolution: 4 })
            .setOrigin(0.5).setDepth(s.DEPTH.fx);
        this.world.add([n]);
        s.tweens.add({ targets: n, y: n.y - 22, alpha: 0, duration: 900, onComplete: () => n.destroy() });
        return false;
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
            let key = 0;
            const notes = s.time.addEvent({ delay: 330, loop: true, callback: () => {
                sfx.piano(key++);
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
                sfx.secret();
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
            s.time.addEvent({ delay: 150, repeat: 3, callback: () => sfx.rung() });
            await w.tween({ targets: her, y: S.y - S.top, x: S.topX, duration: 620 });
            s.pose('rise');
            await w.wait(180);
            sfx.slide();
            s.pose('fall');
            await w.tween({ targets: her, x: S.x0 + 4, y: S.y - 8, duration: 420, ease: 'Quad.easeIn' });
            // Off the chute's foot, over the rim.
            await w.tween({ targets: her, x: S.poolX, y: S.y - 14, duration: 200 });
            her.body.enable = true;
            her.body.reset(her.x, her.y);
            her.body.setVelocity(-60, 40);
            if (!w.save.seen.includes('sec_slide')) {
                sfx.secret();
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
                sfx.knock();
                const knock = s.add.text(C.x + 12 + i * 5, C.y - 52 - i * 4, t('say.knock'), { fontFamily: 'Verdana, sans-serif', fontSize: '6px', fontStyle: 'bold', color: '#2e222f', stroke: '#ffffff', strokeThickness: 2, resolution: 4 })
                    .setOrigin(0.5).setDepth(s.DEPTH.fx);
                w.add([knock]);
                s.tweens.add({ targets: knock, y: knock.y - 10, alpha: 0, duration: 700, onComplete: () => knock.destroy() });
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

    // E at the odd book (population: `scn_nook`): stuck, until all fourteen books are back on the shelf.
    // Then it tips, something clicks, the bookcase shudders with puffs of dust rising at both its sides, and slides
    // to the right behind the other bookcase, the nook's entrance open where it stood (the user, 2026-11-22; the
    // screen does not shake).
    oddBookPull() {
        const s = this.scene, w = this.world, N = this.B.nook;
        if (w.carry || this.P.has('nook') || this.pulling) return false;
        this.pulling = true;
        w.cut(async () => {
            const her = s.player;
            her.setFlipX(N.x + 8 < her.x);
            if (s.anims.exists('her-pull')) her.anims.play('her-pull');
            await w.wait(300);
            await w.tween({ targets: this.oddBook, angle: -24, duration: 160 });
            if (!this.P.has('books_all')) {
                // It will not come: there are gaps on the shelf yet.
                sfx.book();
                await w.tween({ targets: this.oddBook, angle: 0, duration: 200 });
                s.pose('stand');
                w.say('?', 800);
                this.pulling = false;
                return;
            }
            sfx.at(N.x, N.y).lever();
            this.oddGlint.setVisible(false);
            await w.wait(350);
            const cases = this.nookCases();
            sfx.at(N.x, N.y).rumble();
            this.nookWay.setVisible(true).setAlpha(1);
            if (cases) {
                const { slide, home } = cases, book = this.oddBook, bookX = book.x;
                // It shudders, a px either way, while dust puffs up at its two sides, low and high.
                const puff = (x, y, flip) => {
                    const p = s.add.sprite(x, y, 'dust-puff', 0).setOrigin(0.5, 1).setFlipX(flip).setDepth(slide.depth + 0.003);
                    w.add([p]);
                    let f = 0;
                    const ev = s.time.addEvent({ delay: 90, repeat: 7, callback: () => {
                        f++;
                        if (f > 7) { p.destroy(); return; }
                        p.setFrame(f).setY(p.y - 1).setX(p.x + (flip ? -0.5 : 0.5));
                    } });
                    return ev;
                };
                const sides = [[home - slide.width / 2 - 2, true], [home + slide.width / 2 + 2, false]];
                [0, 140, 300, 470].forEach((t, i) => s.time.delayedCall(t, () => sides.forEach(([x, flip]) =>
                    puff(x + (flip ? -1 : 1) * (i % 2), N.y - [0, 18, 6, 34][i], flip))));
                for (let i = 0; i < 9; i++) {
                    const dx = i % 2 ? -1 : 1;
                    slide.setX(home + dx);
                    book.setX(bookX + dx);
                    await w.wait(70);
                }
                slide.setX(home);
                book.setX(bookX);
                await w.wait(250);
                // Then it slides aside, behind its neighbour, the odd book with it (behind the neighbour too).
                book.setDepth(slide.depth + 0.0005);
                await w.tween({ targets: [slide, book], x: `+=${slide.width}`, duration: 1400, ease: 'Sine.easeInOut' });
                book.setVisible(false);
            } else {
                await w.tween({ targets: this.nookWay, alpha: { from: 0, to: 1 }, duration: 700 });
            }
            w.sparkle(N.x, N.y - 30);
            sfx.secret();
            s.pose('stand');
            this.pulling = false;
            this.P.setFlag('nook');
        });
        return true;
    },

};
