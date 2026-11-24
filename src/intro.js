// The welcome screen, the start sequence and the game's intro (docs/intro.md, the user's own
// document; built 2026-11-14, its ending redone the same day on their word). All of it is the ship
// scene's own picture, so one runs into the next with no cut:
//
//   The welcome screen: the sun in the middle of the sky with a few clouds round it, dimmed and out
//   of focus; over it the game's name and two big buttons, PLAY and LANGUAGE (English or
//   Ukrainian: src/lang.js), in pixel lettering on brass plates (src/pixeltext.js). ↑/↓ and
//   Enter, Space or E, or the mouse.
//   The start sequence: the menu melts away, the sky comes into focus and to its full brightness.
//   The intro: the camera tilts down to the sea and the Baltic shore (gulls, the sun's glitter on
//   the water), pans right until the whole ship has come in from the right, then zooms in on
//   deck 3: its side opens on the crew corridor, and the camera stops there at the game's own
//   scale, on the door marked CREW. The door opens and she walks out of it, a few steps to the
//   left (her `walk` clip), and stops, straightens her name badge (her `badge` clip), and turns to
//   go on to the left: the HUD comes up, she is the player's; and the first time she walks past her
//   door, a word over her says what E is for (the one hint in the game: the user asked for it).
//   (A first ending went on in through the door to a close-up of her at her mirror; the user saw
//   it and had it dropped: "The transition scene doesn't work at all".)
//
// A game already under way (a save past the start) gets the same welcome and the same sky, sea and
// ship, a little quicker, and then the camera closes in on wherever she is and the picture fades
// over to the game. Esc ends the intro at once (for the tenth time one sees it); `?play` skips the
// welcome and the intro altogether, as it skipped the title; `?intro=<part>` starts at a part of it
// (`PARTS`), for looking at one.
//
// How it is made: one clock (`T`, seconds since PLAY) and everything a function of it (the
// camera, what is open, what is shown), so any moment can be shown by itself and Esc is only the
// clock set to its end. The wide views use the outside view's sky (laid out in the world:
// src/background.js) with the islands at the game's own pixel size; the sun, its clouds, the gulls
// and the glitter are the intro's own, at that size too, and fade away as the camera goes in.
// Nothing far off drifts in these views (in play the islands and clouds drift aft, the ship being
// under way; this camera stands still): only the gulls fly and the water glitters.

import { VIEW, PLAYER, IDLE } from './config.js';
import { sfx } from './sfx.js';
import { t, nextLanguage } from './lang.js';
import { writeSave } from './save.js';
import { pixelText } from './pixeltext.js';
import { pathGlints, drawGlints } from './background.js';

const HALF = PLAYER.height / 2;
// The parts, in order, and the seconds each takes: a new game's, and a game's under way.
export const PARTS = {
    // (The sea is held only a moment before the camera goes right: the user, on seeing it wait.)
    full: [['focus', 2.4], ['sky', 0.8], ['down', 4.6], ['sea', 0.5], ['right', 6.6], ['ship', 1.3], ['dive', 5.6],
           ['corridor', 1.0], ['step', 0.4], ['walk', 0], ['badge', 2.4], ['turn', 0.6]],
    back: [['focus', 2.0], ['sky', 0.5], ['down', 3.2], ['sea', 0.4], ['right', 4.6], ['ship', 0.8], ['near', 2.4]],
};
// Sounds at moments of the clock, [part, how far into it, effect], each once as the clock passes it (none while held
// at a moment or sought): the gulls over the sea in the wide views, the rush of the dive into the ship, a rustle at her
// badge (part 5: the intro had a checkpoint's chime, a door and her steps). The sea and the wind are the ambience's.
const CUES = {
    full: [['sky', 0.4, 'gull'], ['down', 0.55, 'gull'], ['right', 0.35, 'gull'], ['right', 0.8, 'gull'], ['dive', 0.3, 'swell'], ['badge', 0.2, 'cloth']],
    back: [['sky', 0.3, 'gull'], ['right', 0.5, 'gull'], ['near', 0.05, 'swell']],
};
const DIM = 0.36;                 // the welcome screen's shade over the sky
// The menu: where the name and the two plates stand on the screen, and the lettering's colours
// from the top of a letter down (the name's: the sun livery's; a plate's: cream, gold when chosen). The whole menu
// stands 60 px higher than it was (the user's 3 of four, 2026-11-21).
const MENU = { title: 118, first: 276, step: 90,
               sunny: ['#fbff86', '#f9c22b', '#f9c22b', '#f79617', '#fb6b1d'], gold: ['#fbff86', '#f9c22b', '#f79617'],
               cream: ['#ffffff', '#ffffff', '#fdcbb0'] };
const BLUR = 2.0;                 // ...and how far out of focus it is
const HINT_MS = 3000;             // how long a hint stays over her (6 s first, then 4; "even a bit earlier": the user, 2026-11-20)
const HINT_AT = -14;              // "E to interact" as she reaches her door going right: her middle at its near edge
                                  // (16 px past its middle first: she was past the door by then, the user)
// Out of her door, walking straight to the left, a few steps (the user, 2026-11-20: "walk, not
// run"; no stop facing us in the doorway): how far (56 px, "a bit earlier" than the 72 where the
// notice board hung: the board moved left of that, tools/build_ship_map.py); her pace (her walk clip's frames a
// second, and the px a second its planted foot slides back at that rate: about 4.4 px a frame);
// the clip's frames where a foot comes down (a footstep); when the door shuts behind her (until
// then its open leaf, swung toward us, is drawn over her, and she steps out past its edge: `leaf`,
// the first of the open door's columns that are the leaf, the ones before it the jamb and the
// light in the gap, which she is in front of); and how long she stands still facing left before
// she turns to us. The part `walk` is her walk and that stop.
const WALK = { px: 56, speed: 44, fps: 10, steps: [3, 7], shut: 0.65, leaf: 6, stop: 0.25 };
WALK.secs = WALK.px / WALK.speed;
PARTS.full.find(q => q[0] === 'walk')[1] = WALK.secs + WALK.stop;
const SUN_UP = 365;               // the sun over the horizon, in screen px of the wide view
const HORIZON = 140;               // the horizon under the middle of the screen in the wide views
const PAN = 960;                  // how far left of the ship the sea's view is, in screen px
// The gulls over the sea: [px right of the sea view's middle, px over the horizon, px/s, screen px a texel].
const GULLS = [[-330, 96, 26, 2], [-60, 150, -18, 2], [210, 60, 22, 2], [380, 128, -30, 3], [-200, 40, 34, 3], [60, 206, 14, 2]];

const clamp01 = v => Math.min(1, Math.max(0, v));
const smooth = k => k * k * (3 - 2 * k);
const smoother = k => k * k * k * (k * (k * 6 - 15) + 10);

function rng(seed) {
    let s = seed >>> 0;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

// The sun's path on the water (a path of light under the sun only, the user): glints on the far sea's
// rows, each flickering on a clock of its own, swaying with the ripples (`pathGlints`, `drawGlints` in
// src/background.js, the sunset's too). Texels two screen px each.
const PATH = { w: 300, h: 120 };
const PATH_COLOURS = ['#fffffa', '#fff4d0', '#c8ecff'];

// The intro's own pictures: the sun, its bloom, its god rays and the clouds round it are built art
// (tools/build_sky.py: `skyart`, `sky-glow`, `sky-rays`, `sky-layout`); the path of light is drawn here,
// each frame.
function makeTextures(scene) {
    if (!scene.textures.exists('intro-glitter')) scene.textures.createCanvas('intro-glitter', PATH.w, PATH.h);
}

export class Intro {
    constructor(scene) {
        const s = this.s = scene, cam = s.cameras.main, params = new URLSearchParams(location.search);
        makeTextures(s);
        // A new game (nothing saved past its start) gets all of it; a game under way the short one.
        const start = !s.save.lastCheckpoint || s.save.lastCheckpoint === 'cp_crew';
        this.full = start && !s.save.intro && !params.has('at') && !!s.world.rooms.crewcabin;
        let at = 0;
        this.parts = PARTS[this.full ? 'full' : 'back'].map(([name, len]) => ({ name, from: (at += len) - len, len }));
        this.length = at;
        this.T = 0;
        this.clock = 0;
        this.stage = 'welcome';                 // welcome | running | done
        this.selected = 0;

        // The wide views: the whole ship across the screen, and what a screen pixel is in the world.
        const W = s.map.widthInPixels;
        this.fit = VIEW.width / (W * 0.94);
        const u = this.u = 1 / this.fit;
        this.shipX = W / 2;
        this.farY = s.waterY - HORIZON * u;
        this.sunX = this.shipX - PAN * u;
        this.sunY = s.waterY - SUN_UP * u;
        // (The islands two screen pixels to each of theirs, as in play; a texel in the world.)
        this.look = { islands: 2 * u };

        cam.stopFollow();
        cam.removeBounds();
        s.player.setVisible(false);
        s.uiCam.setVisible(false);
        s.mode = 'scripted';
        s.script = null;
        s.fromAfar = true;

        this.buildDressing();
        this.buildMenu();
        const part = this.parts.find(p => p.name === params.get('intro'));
        if (part) this.play(part.from);
        this.apply(0);
    }

    // --- What the wide views have of their own ---------------------------------------------------

    buildDressing() {
        const s = this.s, u = this.u, D = s.DEPTH, items = this.dressing = [];
        const add = o => { items.push(o); s.worldLayer.add(o); return o; };
        // The sun (B3 of three mock-ups, the user, 2026-11-20): a soft disc and its bloom, no rays of
        // its own, just over a cloud's top; the god rays are the clouds' shadows in its light, worked
        // out from where they stand; a little of the bloom over the cloud it is behind.
        const L = s.cache.json.get('sky-layout'), at = (x, y) => [this.sunX + x * u, this.sunY + y * u];
        this.glow = add(s.add.image(this.sunX, this.sunY, 'sky-glow').setScale(u).setDepth(D.sky + 0.006));
        this.sun = add(s.add.image(this.sunX, this.sunY, 'skyart', 'sun').setScale(2 * u).setDepth(D.sky + 0.008));
        this.rays = add(s.add.image(...at(L.rays.x, L.rays.y), 'sky-rays').setOrigin(0).setScale(u).setDepth(D.sky + 0.009));
        this.clouds = L.clouds.map(c => add(s.add.image(...at(c.x, c.y), 'skyart', c.frame).setScale(2 * u).setDepth(D.sky + 0.012)));
        this.flare = add(s.add.image(this.sunX, this.sunY, 'sky-glow').setScale(0.6 * u).setDepth(D.sky + 0.013));
        // On the water, over the sea's own rows and under the hull's foam: the far sea's ripples
        // at the game's pixel size, and the sun's glitter.
        const left = this.sunX - VIEW.width * u, right = this.shipX + VIEW.width * u;
        this.ripples = add(s.add.tileSprite(left, s.waterY, (right - left) / (2 * u), 160, 'bg-ripples').setOrigin(0)
            .setScale(2 * u).setDepth(D.exterior + 0.26).setAlpha(0.6));
        this.glitter = add(s.add.image(this.sunX, s.waterY, 'intro-glitter').setOrigin(0.5, 0).setScale(2 * u).setDepth(D.exterior + 0.27));
        this.glints = pathGlints(PATH.w, PATH.h, 301);
        this.gulls = GULLS.map(([dx, up, speed, size], i) => {
            const img = add(s.add.sprite(0, s.waterY - up * u, 'bg-gull', 0).setOrigin(0.5, 1).setScale(size * u).setDepth(D.fx)
                .setTint(size === 3 ? 0x8f8aa0 : 0xc8c6d4).setFlipX(speed < 0));
            return { img, x0: dx, y: s.waterY - up * u, speed, phase: i * 1.7, rate: 5 + (i % 3) };
        });
    }

    // The path of light as it is at `now`, moved `dx` texels with the ripples.
    drawPath(now, dx) {
        drawGlints(this.s.textures.get('intro-glitter'), this.glints, PATH_COLOURS, now, dx);
    }

    // --- The welcome screen -----------------------------------------------------------------------

    buildMenu() {
        const s = this.s, { width: W, height: H } = VIEW;
        this.menuLayer = s.add.layer();
        this.menuCam = s.cameras.add(0, 0, W, H);
        for (const c of [s.cameras.main, s.washCam, s.uiCam]) c.ignore(this.menuLayer);
        this.menuCam.ignore([s.worldLayer, s.washLayer, s.uiLayer]);
        this.shade = s.add.rectangle(0, 0, W, H, 0x0d1422).setOrigin(0).setAlpha(DIM);
        // The game's name in the sun livery's colours; two ship's name plates, brass round navy
        // enamel, for PLAY and LANGUAGE; a tangerine by the one chosen (the user chose the style
        // from three, 2026-11-14: tools/build_menu.py, src/pixeltext.js). All at two screen
        // pixels to one of the art's.
        this.title = s.add.image(W / 2, MENU.title, 'menu', 'plate').setScale(2);
        this.marker = s.add.image(0, 0, 'tangerine').setScale(3);
        this.buttons = ['play', 'language'].map((id, i) => {
            const y = MENU.first + i * MENU.step;
            const plate = s.add.image(W / 2, y, 'menu', 'plate').setScale(2);
            const label = s.add.image(W / 2, y, 'menu', 'plate').setScale(2);
            const zone = s.add.zone(W / 2, y, plate.displayWidth, plate.displayHeight).setInteractive({ useHandCursor: true });
            zone.on('pointerover', () => this.select(i));
            zone.on('pointerdown', () => { this.select(i); this.press(); });
            return { id, y, plate, label, zone, text: '' };
        });
        this.menu = [this.title, this.marker, ...this.buttons.flatMap(b => [b.plate, b.label, b.zone])];
        this.menuLayer.add([this.shade, ...this.menu]);
        this.refreshMenu();
    }

    // The menu's words in the language chosen, the chosen entry lit: its letters gold, its plate
    // bright, the tangerine beside it.
    refreshMenu() {
        const s = this.s;
        this.titleText = t('title').toUpperCase();
        this.title.setTexture(pixelText(s, 'menu-title', 'T', this.titleText, { bands: MENU.sunny, thick: 2 }));
        this.buttons.forEach((b, i) => {
            const on = i === this.selected;
            b.text = t(`menu.${b.id}`).toUpperCase();
            b.label.setTexture(pixelText(s, `menu-${b.id}`, 'S', b.text, { bands: on ? MENU.gold : MENU.cream, outline: '#2e222f' }));
            b.plate.setTint(on ? 0xffffff : 0xcfcfd6);
        });
        const b = this.buttons[this.selected];
        this.marker.setPosition(VIEW.width / 2 - b.plate.displayWidth / 2 - 24, b.y);
    }

    select(i) {
        if (this.stage !== 'welcome' || i === this.selected) return;
        this.selected = i;
        sfx.choose();
        this.refreshMenu();
    }

    press() {
        if (this.stage !== 'welcome') return;
        sfx.unlock();
        if (this.buttons[this.selected].id === 'language') {
            nextLanguage();
            sfx.choose();
            this.refreshMenu();
            return;
        }
        sfx.checkpoint();
        this.play(0);
    }

    // PLAY: the clock starts (`from`: at a later part, for a look at it).
    play(from) {
        this.stage = 'running';
        this.T = from;
        for (const b of this.buttons) b.zone.disableInteractive();
    }

    // --- The clock ----------------------------------------------------------------------------------

    // How far through a part the clock is: 0 before it, 1 after.
    p(name) {
        const part = this.parts.find(q => q.name === name);
        return part ? clamp01((this.T - part.from) / part.len) : 0;
    }

    // To a part's `k` (0 its start, 1 its end), held there: for the playtests and for pictures.
    seek(name, k = 0, hold = true) {
        const part = this.parts.find(q => q.name === name);
        if (!part) return false;
        if (this.stage === 'welcome') this.play(0);
        this.T = part.from + part.len * k;
        this.held = hold;
        this.apply(0);
        return true;
    }

    update(input, dt) {
        if (this.stage === 'done') return;
        this.clock += dt;
        if (this.stage === 'welcome') {
            if (input.upPressed || input.downPressed) this.select(1 - this.selected);
            if (input.startPressed || input.activatePressed) this.press();
        } else {
            const was = this.T;
            if (!this.held) this.T += dt;
            for (const [name, k, fx] of CUES[this.full ? 'full' : 'back']) {
                const part = this.parts.find(q => q.name === name), at = part && part.from + part.len * k;
                if (part && was < at && this.T >= at) sfx[fx]();
            }
            if (input.escapePressed || this.T >= this.length) {
                this.finish(input.escapePressed || !this.full);
                return;
            }
        }
        this.apply(dt);
    }

    // Everything as it is at the clock's time.
    apply(dt) {
        const s = this.s, cam = s.cameras.main, u = this.u, p = s.player;
        const focus = this.stage === 'welcome' ? 0 : this.p('focus');

        // The camera. Far off it moves by whole screen pixels, so the small ship does not shimmer.
        const step = v => Math.round(v) * u;
        let z = this.fit;
        let cx = this.sunX + step(smoother(this.p('right')) * PAN);
        let cy = this.sunY + step(smoother(this.p('down')) * (SUN_UP - HORIZON));
        const to = this.full ? this.door() : { x: p.x, y: p.y - HALF };
        // (Her few steps out: the camera goes with her, easing, and is on her as she stops.)
        if (this.full) to.x -= WALK.px * smooth(clamp01(this.p('walk') * (WALK.secs + WALK.stop) / WALK.secs));
        const dive = this.p(this.full ? 'dive' : 'near');
        if (dive > 0) {
            // In on a point: the zoom doubles and doubles again, the point coming to the middle.
            const end = this.full ? VIEW.zoom : 0.42;
            z = this.fit * (end / this.fit) ** smoother(dive);
            const off = (this.fit / z) * (1 - smooth(dive));
            cx = to.x + (cx - to.x) * off;
            cy = to.y + (cy - to.y) * off;
        }
        // (The blur first: it changes the camera's size, and the camera is centred after.)
        this.setBlur(BLUR * (1 - smooth(focus)));
        cam.setZoom(z);
        cam.centerOn(cx, cy);
        this.zoom = z;

        // The ship: closed from afar; then deck 3's side opens on the corridor (a new game), the
        // rest of the ship going dim round it as it does, and once the camera has stopped there
        // the game's own cut-away takes over; or it does where she is (a game under way).
        s.fromAfar = z < 0.6;
        s.horizonOnScreen = undefined;
        if (this.full) {
            // (It opens as the zoom goes from 1.6 to 1.99, the camera all but settled on the corridor:
            // from 0.7 to 1.7 it was "a bit early", the user's C of four, 2026-11-21.)
            const open = clamp01(Math.log(z / 1.6) / Math.log(1.99 / 1.6));
            s.viewOverride = s.fromAfar || this.p('corridor') >= 1 ? null : 2 + smooth(open);
            // (The dark round her deck comes with the corridor's opening, not after it: the user.)
            s.dimOverride = s.fromAfar ? 0 : smooth(open);
            this.arrive(this.p('step'), this.p('walk'), this.p('badge'), this.p('turn'));
        }

        // The welcome's shade and blur, lifting; the menu melting away; at a short intro's end
        // the picture going over to the game through the dark.
        const melt = this.stage === 'welcome' ? 1 : 1 - clamp01(this.T / 0.6);
        for (const o of this.menu) o.setAlpha(melt);
        this.title.setY(MENU.title - (1 - melt) * 26);
        if (melt > 0) this.marker.setY(this.buttons[this.selected].y + Math.round(Math.sin(this.clock * 4) * 1.5) * 2);
        this.shade.setAlpha(this.full ? DIM * (1 - smooth(focus)) : Math.max(DIM * (1 - smooth(focus)), clamp01((this.p('near') - 0.62) / 0.38)));

        // The sun, its clouds, the glitter, the gulls: all gone by the time the ship fills the view.
        const far = 1 - clamp01((z / this.fit - 1.25) / 1.6);
        const now = this.clock;
        for (const o of this.dressing) o.setVisible(far > 0);
        if (far > 0) {
            this.sun.setAlpha(far);
            const breath = 0.9 + 0.1 * Math.sin(now * 1.7);
            this.glow.setAlpha(far * breath);
            this.flare.setAlpha(far * 0.35 * breath);
            this.rays.setAlpha(far * (0.85 + 0.15 * Math.sin(now * 0.6)));
            // (Nothing here drifts: the sun stands still, and whatever slid past it looked wrong.
            // The water only sways a little in place; the gulls and the glitter are the life in it.)
            for (const c of this.clouds) c.setAlpha(far);
            const sway = Math.round(Math.sin(now * 0.9) * 2);
            this.ripples.setAlpha(0.6 * far).tilePositionX = sway;
            this.glitter.setAlpha(far);
            this.drawPath(now, -sway);
            const span = 1500;
            for (const g of this.gulls) {
                const x = ((g.x0 + g.speed * now + span / 2) % span + span) % span - span / 2;
                const flap = Math.floor((now + g.phase) * g.rate) % 4;
                g.img.setFrame([0, 1, 2, 1][flap]).setAlpha(far)
                    .setPosition(this.sunX + x * u, g.y + Math.round(Math.sin(now * 1.1 + g.phase) * 2) * u);
            }
        }
    }

    // The door marked CREW: where the camera stops, at the game's own framing of her standing there.
    door() {
        const d = this.s.world.rooms.crewcabin.def.doors[0];
        return { x: d.outX, y: d.outY - HALF };
    }

    // Her coming out: the door opens (`step` 0 to 1); she walks out of it to the left, the door
    // shutting behind her, and stops (`walk`); she turns to us and straightens her badge (`badge`);
    // she turns to go (`turn`). Each by the clock, so any moment can be shown.
    arrive(step, walk, badge, turn) {
        const s = this.s, p = s.player, room = s.world.rooms.crewcabin;
        const secs = walk * (WALK.secs + WALK.stop);            // into the walk, in seconds
        const open = step > 0.15 && secs < WALK.shut;
        s.setDoorArt(room.outside[0], open ? 'door-crew-ajar' : 'door-crew');
        if (open && !this.doorHeard && this.stage === 'running' && !this.held) sfx.at(p.x, p.y).door();
        this.doorHeard = open || this.doorHeard && step > 0;
        const anims = s.herFrames && s.cache.json.get('her-meta').anims;
        const going = walk > 0 && badge === 0;                  // walking, or stopped and still facing left
        p.x = this.door().x - WALK.px * clamp01(secs / WALK.secs);
        p.setVisible(walk > 0).setAlpha(1).setFlipX(going || turn >= 0.5);     // (she turns to go left: the user, 2026-11-20)
        // (In the doorway the door's open leaf is over her: a copy of the open door, cut to the leaf.)
        const door = room.outside[0];
        if (!this.leaf) {
            this.leaf = s.add.image(0, 0, 'shipart', 'door-crew-ajar');
            s.worldLayer.add(this.leaf);
        }
        const f = this.leaf.frame;
        this.leaf.setPosition(door.x, door.y).setOrigin(door.originX, door.originY).setDepth(p.depth + 0.01)
            .setCrop(WALK.leaf, 0, f.width - WALK.leaf, f.height).setVisible(open && walk > 0);
        let frame = turn >= 0.5 ? s.herFrames.stand : s.herFrames.front;
        if (going) {
            const clip = anims.walk ?? anims.run;
            const i = secs < WALK.secs ? Math.floor(secs * WALK.fps) % clip.length : -1;
            frame = i >= 0 ? clip[i] : s.herFrames.stand;
            if (i !== this.stepFrame && WALK.steps.includes(i) && this.stage === 'running' && !this.held) sfx.step(s.soundscape.floor());
            this.stepFrame = i;
        }
        if (anims && badge > 0 && badge < 1) frame = anims.badge[Math.min(anims.badge.length - 1, Math.floor(badge * anims.badge.length))];
        if (p.anims.isPlaying) p.anims.stop();
        p.setTexture('her', frame);
    }

    setBlur(amount) {
        const cam = this.s.cameras.main;
        if (amount < 0.02) {
            if (this.blur) {
                cam.filters.internal.remove(this.blur);
                cam.setViewport(0, 0, VIEW.width, VIEW.height);
            }
            this.blur = null;
            return;
        }
        if (!this.blur) {
            // (A blur darkens the picture's edges, where it has nothing to mix in: the camera
            // draws `PAD` px more all round while it is out of focus, and the edges fall outside.)
            const PAD = 48;
            cam.setViewport(-PAD, -PAD, VIEW.width + 2 * PAD, VIEW.height + 2 * PAD);
            this.blur = cam.filters.internal.addBlur(2, 2, 2, 1, 0xffffff, 6);
        }
        this.blur.strength = amount;
    }

    // The game's: the camera hers, the HUD up. `through`: through the dark (a short intro's end,
    // or Esc), the picture coming up from black.
    finish(through) {
        const s = this.s, cam = s.cameras.main, p = s.player;
        this.stage = 'done';
        this.T = this.length;
        this.setBlur(0);
        if (this.full) this.arrive(1, 1, 1, 1);
        this.leaf?.destroy();
        p.setVisible(true).setAlpha(1);
        s.pose('stand');
        for (const o of [...this.dressing, ...this.menu]) o.destroy();
        s.fromAfar = false;
        s.viewOverride = null;
        s.dimOverride = null;
        // (Coming in through the dark, everything is set at once; at the intro's own end it is
        // as the game has it already, and nothing may jump.)
        if (through) s.viewDeck = null;
        s.horizonOnScreen = undefined;
        cam.setZoom(VIEW.zoom);
        cam.setBounds(0, -560, s.map.widthInPixels, s.map.heightInPixels + 560);
        cam.startFollow(p, true, 0.15, 0.15);
        cam.setFollowOffset(0, HALF);
        cam.centerOn(p.x, p.y - HALF);
        if (through) s.updateCutaway(0);
        s.mode = 'play';
        s.grounded = true;
        s.lastGroundedAt = s.time.now;
        // (Her idles wait their usual while from now: she had begun to tap her foot at once.)
        s.idle = null;
        s.idleAt = s.time.now + IDLE.firstMs;
        s.uiCam.setVisible(true).setAlpha(0);
        s.tweens.add({ targets: s.uiCam, alpha: 1, duration: 700, delay: through ? 300 : 0 });
        this.shade.setAlpha(through ? 1 : 0);
        s.tweens.add({ targets: this.shade, alpha: 0, duration: through ? 500 : 1, onComplete: () => {
            this.shade.destroy();
            s.cameras.remove(this.menuCam);
            s.intro = null;
        } });
        // The game's two hints, each once in a new game. How to move and jump (the user, 2026-11-20:
        // "When we get the controls after she faces left, place a one time popup"), over her as she
        // is handed over, in the words of what she plays with (the controller's buttons while it is
        // the one in use, and switched over if she takes up the other while it shows). What E is
        // for (the user, 2026-11-14: "Add a hint popup, saying 'E to interact'"), the first time
        // she walks past her cabin's door in the corridor (the user, 2026-11-20; she is handed over
        // a few steps to the left of it); it takes the bubble over if the first is still up.
        if (this.full) {
            const past = this.door().x + HINT_AT;
            const moveText = () => t(s.controls.device === 'pad' ? 'hint.move.pad' : 'hint.move');
            let move = null, moveUntil = 0, doorDone = false;
            s.time.delayedCall(through ? 700 : 250, () => {
                move = moveText();
                moveUntil = s.time.now + HINT_MS;
                s.world.say(move, HINT_MS, { kind: 'plate' });
            });
            const watch = () => {
                const showing = move && s.alert.visible && s.alert.text === move;
                if (showing && moveText() !== move) {
                    const now = moveText();
                    s.alert.setText(now, { kind: 'plate' });
                    s.time.delayedCall(Math.max(0, moveUntil - s.time.now), () => { if (s.alert.text === now) s.alert.setVisible(false); });
                    move = now;
                }
                if (!doorDone && s.mode === 'play' && s.route === 'inside' && p.x >= past) {
                    doorDone = true;
                    s.world.say(t('hint.interact'), HINT_MS, { kind: 'plate' });
                }
                if (doorDone && move && s.time.now >= moveUntil) s.events.off('update', watch);
            };
            s.events.on('update', watch);
        }
        if (!s.save.intro) {
            s.save.intro = true;
            writeSave(s.save);
        }
    }
}
