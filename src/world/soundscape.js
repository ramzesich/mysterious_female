// What she hears that nothing in particular makes (§5.2): the sea along the side, the engines low
// in the ship, the wind up top, the ventilation indoors, water lapping in the pools; the small
// steady sounds of a few places; and her own going, footstep by footstep, on whatever is under her.
// Each layer's loudness is set here from where she is; the layers themselves are in src/sfx.js.

import { SOUND } from '../config.js';
import { sfx } from '../sfx.js';
import { OUTSIDE } from './world.js';

const M = 48;
// Places with a sound of their own, heard only near them: where (px), within what reach, what, and
// how often (seconds, from..to).
const PLACES = [
    // The casino on deck 7: chips somewhere, a machine paying out.
    { deck: 7, x: 480 + 161 * M, reach: 13 * M, every: [1.8, 5], play: (x, y) => (Math.random() < 0.6 ? sfx.at(x, y).chips() : sfx.at(x, y).slot()), spread: 9 * M },
    // The bridge on deck 10: the radar's sweep.
    { deck: 10, x: 2040, reach: 8 * M, every: [3.6, 3.6], play: (x, y) => sfx.at(x, y).ping() },
];

export class Soundscape {
    constructor(scene) {
        this.scene = scene;
        this.levelsAt = 0;
        this.walked = 0;
        this.rolled = 0;
        this.last = null;
        this.gullAt = 6;
        this.clock = 0;
        this.placeAt = PLACES.map(() => 0);
    }

    // Out in the open: on the outside route, or on a deck with no ship's side beside her.
    open() {
        const s = this.scene, p = s.player;
        if (s.overview || s.fromAfar || s.route === OUTSIDE) return true;
        if (s.route !== 'inside') return false;
        const deck = s.deckOfY(p.y);
        if (deck === null) return true;             // over deck 12: the roof, the funnel
        return !s.exteriorLayer.getTileAt(Math.floor(p.x / 16), s.deckFloors[deck] - 4);
    }

    // What is under her feet: 'carpet' inside, 'deck' on the open decks' planks, 'metal' on the
    // roof and the funnel, 'duct' in the duct.
    floor() {
        const s = this.scene;
        if (s.route === 'duct') return 'duct';
        if (s.route === 'inside' && s.deckOfY(s.player.y) === null) return 'metal';
        return this.open() ? 'deck' : 'carpet';
    }

    update(dt) {
        const s = this.scene, p = s.player;
        this.clock += dt;
        // Her ears are where she is; while a scene shows somewhere else (the horn's cascade, a look
        // through the telescope), where the camera is.
        const view = s.cameras.main.worldView;
        const away = Math.abs(view.centerX - p.x) > 300 || Math.abs(view.centerY - p.y) > 220;
        if (away && !s.overview) sfx.listen(view.centerX, view.centerY + 40);
        else sfx.listen(p.x, p.y - 30);
        if (this.clock >= this.levelsAt) {
            this.levelsAt = this.clock + 0.15;
            sfx.ambience(this.levels());
        }
        if (s.overview || s.intro) return;
        this.steps();
        this.places(dt);
        // Out on deck, a gull somewhere off the ship now and then.
        this.gullAt -= dt;
        if (this.gullAt <= 0) {
            this.gullAt = 9 + Math.random() * 14;
            if (this.open()) sfx.at(p.x + (Math.random() < 0.5 ? -1 : 1) * (380 + Math.random() * 260), p.y - 120).gull();
        }
    }

    // How loud each layer is where she stands (0 to 1).
    levels() {
        const s = this.scene, p = s.player;
        // From outside (O) the whole ship is in front of us: the sea and the wind.
        if (s.overview || s.fromAfar) return { sea: 1, wind: 0.5, engine: 0.15 };
        const high = Phaser.Math.Clamp((s.deckAt(p.y) - 4) / 8, 0, 1);        // 0 on deck 4, 1 on deck 12
        const open = this.open();
        const inRoom = s.route !== 'inside' && s.route !== OUTSIDE;       // a room behind a door, the duct
        const engine = 0.12 + 0.88 * (1 - high) ** 1.6;
        // A pool with water in it, near enough to hear it lap; in it, little else.
        let water = 0;
        for (const pool of s.pools) {
            if (!pool.water.visible || Math.abs(pool.y - p.y) > 100) continue;
            const d = Math.max(0, pool.x0 - p.x, p.x - pool.x1);
            water = Math.max(water, 1 - d / (8 * M));
        }
        if (s.mode === 'swim') return { sea: 0.15, wind: 0.1, engine: engine * 0.4, water: 1 };
        if (open) return { sea: 0.95 - 0.5 * high, wind: 0.22 + 0.6 * high, engine: engine * 0.45, water };
        if (s.route === 'duct') return { sea: 0.03, engine: engine * 1.2, air: 1.3 };
        if (inRoom) return { sea: 0.06, engine: engine * 0.8, air: 0.5 };
        return { sea: 0.14, engine, air: 0.8, water: water * 0.3 };
    }

    // Her feet, her hands on a ladder's rungs, a cart's wheels, her strokes in the pool: one sound
    // for each stretch she has covered, whatever moves her (her own run, a scene's walk).
    steps() {
        const s = this.scene, p = s.player;
        // (The intro walks her out of her door and sounds her steps on her clip's own frames.)
        if (s.intro) { this.last = null; this.walked = 0; return; }
        const was = this.last ?? { x: p.x, y: p.y, mode: s.mode };
        const dx = Math.abs(p.x - was.x), dy = Math.abs(p.y - was.y);
        this.last = { x: p.x, y: p.y, mode: s.mode };
        // (Put somewhere else by a door, a scene or a fright: not walked.)
        if (dx + dy > 40 || was.mode !== s.mode || !p.visible || p.alpha < 0.5) {
            this.walked = 0;
            return;
        }
        const stride = SOUND.stride;
        if (s.mode === 'ladder' || s.mode === 'trunk') {
            this.walked += dy;
            if (this.walked >= 15) { this.walked = 0; sfx.rung(); }
        } else if (s.mode === 'stairs') {
            this.walked += Math.hypot(dx, dy);
            if (this.walked >= stride) { this.walked = 0; sfx.step(s.flight?.outside ? 'metal' : 'stair'); }
        } else if (s.mode === 'swim') {
            this.walked += dx;
            if (this.walked >= 44) { this.walked = 0; sfx.stroke(); }
        } else if (s.mode === 'push') {
            this.walked += dx;
            this.rolled += dx;
            if (this.walked >= stride) { this.walked = 0; sfx.step(this.floor()); }
            if (this.rolled >= 20) { this.rolled = 0; sfx.roll(); }
        } else if ((s.mode === 'play' && s.grounded && !s.wading && !s.slipDir) || (s.mode === 'scripted' && dy === 0 && dx > 0)) {
            // Running, or walking with something in her hands: a step as a foot comes down in her clip (SOUND.runSteps,
            // SOUND.carrySteps); else by the floor walked.
            const clip = p.anims.isPlaying ? p.anims.currentAnim?.key : null;
            const feet = clip === 'her-run' ? SOUND.runSteps : clip === 'her-carry-run' ? SOUND.carrySteps : null;
            if (!s.crawling && feet) {
                const i = (p.anims.currentFrame?.index ?? 1) - 1;
                if (i !== this.runFrame && feet.includes(i)) sfx.step(this.floor());
                this.runFrame = i;
                this.walked = 0;
                return;
            }
            this.runFrame = -1;
            this.walked += dx;
            const each = s.crawling ? stride * 0.8 : s.isLunging() ? stride * 1.35 : stride;
            if (this.walked >= each) { this.walked = 0; sfx.step(s.crawling && s.route !== 'duct' ? 'crawl' : this.floor()); }
        }
    }

    places(dt) {
        const s = this.scene, p = s.player;
        if (s.route !== 'inside') return;
        const deck = s.deckOfY(p.y);
        PLACES.forEach((place, i) => {
            if (place.deck !== deck || Math.abs(p.x - place.x) > place.reach + SOUND.far) return;
            this.placeAt[i] -= dt;
            if (this.placeAt[i] > 0) return;
            const [a, b] = place.every;
            this.placeAt[i] = a + Math.random() * (b - a);
            place.play(place.x + (Math.random() - 0.5) * 2 * (place.spread ?? 0), p.y - 30);
        });
    }
}
