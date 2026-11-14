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
//   scale, on the door marked CREW. The door opens, she steps out and stands by it, straightens
//   her name badge (her `badge` clip), and turns to go: the HUD comes up, she is the player's,
//   and a word over her says what E is for (the one hint in the game: the user asked for it).
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
import { cloudTexture } from './background.js';
import { pixelText } from './pixeltext.js';

const HALF = PLAYER.height / 2;
// The parts, in order, and the seconds each takes: a new game's, and a game's under way.
export const PARTS = {
    // (The sea is held only a moment before the camera goes right: the user, on seeing it wait.)
    full: [['focus', 2.4], ['sky', 0.8], ['down', 4.6], ['sea', 0.5], ['right', 6.6], ['ship', 1.3], ['dive', 5.6],
           ['corridor', 1.0], ['step', 1.6], ['badge', 2.4], ['turn', 0.6]],
    back: [['focus', 2.0], ['sky', 0.5], ['down', 3.2], ['sea', 0.4], ['right', 4.6], ['ship', 0.8], ['near', 2.4]],
};
const DIM = 0.36;                 // the welcome screen's shade over the sky
// The menu: where the name and the two plates stand on the screen, and the lettering's colours
// from the top of a letter down (the name's: the sun livery's; a plate's: cream, gold when chosen).
const MENU = { title: 178, first: 336, step: 90,
               sunny: ['#fbff86', '#f9c22b', '#f9c22b', '#f79617', '#fb6b1d'], gold: ['#fbff86', '#f9c22b', '#f79617'],
               cream: ['#ffffff', '#ffffff', '#fdcbb0'] };
const BLUR = 2.0;                 // ...and how far out of focus it is
const HINT_MS = 6000;             // how long "E to interact" stays over her
const SUN_UP = 365;               // the sun over the horizon, in screen px of the wide view
const HORIZON = 140;               // the horizon under the middle of the screen in the wide views
const PAN = 960;                  // how far left of the ship the sea's view is, in screen px
// The few clouds round the sun: [px right of it, px under it, texels wide, screen px a texel, seed].
const CLOUDS = [[-250, 56, 96, 3, 5], [228, -74, 84, 3, 12], [150, 110, 60, 2, 23], [-190, -112, 52, 2, 31], [372, 62, 70, 2, 44],
                [-420, -30, 64, 2, 57]];
// The gulls over the sea: [px right of the sea view's middle, px over the horizon, px/s, screen px a texel].
const GULLS = [[-330, 96, 26, 2], [-60, 150, -18, 2], [210, 60, 22, 2], [380, 128, -30, 3], [-200, 40, 34, 3], [60, 206, 14, 2]];

const clamp01 = v => Math.min(1, Math.max(0, v));
const smooth = k => k * k * (3 - 2 * k);
const smoother = k => k * k * k * (k * (k * 6 - 15) + 10);

function rng(seed) {
    let s = seed >>> 0;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

// The intro's own pictures: the day's sun (its disc, its glow, two sets of rays that take turns),
// and the sun's glitter on the water in two frames.
function makeTextures(scene) {
    if (scene.textures.exists('intro-sun')) return;
    const R = 15, d = R * 2 + 1;
    let tex = scene.textures.createCanvas('intro-sun', d, d), ctx = tex.getContext();
    for (let y = 0; y < d; y++) {
        const half = Math.floor(Math.sqrt(Math.max(0, (R + 0.4) ** 2 - (y - R) ** 2)));
        if (!half) continue;
        ctx.fillStyle = '#ffe9a0';
        ctx.fillRect(R - half, y, half * 2 + 1, 1);
        if (half > 2) {
            ctx.fillStyle = '#fffbe2';
            ctx.fillRect(R - half + 2, y, half * 2 - 3, 1);
        }
    }
    tex.refresh();
    const G = 180;
    tex = scene.textures.createCanvas('intro-sunglow', G, G);
    ctx = tex.getContext();
    const g = ctx.createRadialGradient(G / 2, G / 2, R - 3, G / 2, G / 2, G / 2);
    g.addColorStop(0, 'rgba(255,250,214,0.85)');
    g.addColorStop(0.22, 'rgba(255,246,200,0.38)');
    g.addColorStop(0.55, 'rgba(255,244,196,0.12)');
    g.addColorStop(1, 'rgba(255,244,196,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, G, G);
    tex.refresh();
    for (const f of [0, 1]) {
        const S = 140;
        tex = scene.textures.createCanvas(`intro-rays-${f}`, S, S);
        ctx = tex.getContext();
        const n = 12;
        for (let i = 0; i < n; i++) {
            const a = (i + f * 0.5) / n * Math.PI * 2, long = i % 2 === 0;
            const r0 = R + 5, r1 = R + (long ? 44 : 26) - f * 6, w = 0.05;
            const grad = ctx.createLinearGradient(S / 2 + Math.cos(a) * r0, S / 2 + Math.sin(a) * r0, S / 2 + Math.cos(a) * r1, S / 2 + Math.sin(a) * r1);
            grad.addColorStop(0, 'rgba(255,248,205,0.75)');
            grad.addColorStop(1, 'rgba(255,248,205,0)');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.moveTo(S / 2 + Math.cos(a - w) * r0, S / 2 + Math.sin(a - w) * r0);
            ctx.lineTo(S / 2 + Math.cos(a) * r1, S / 2 + Math.sin(a) * r1);
            ctx.lineTo(S / 2 + Math.cos(a + w) * r0, S / 2 + Math.sin(a + w) * r0);
            ctx.closePath();
            ctx.fill();
        }
        tex.refresh();
    }
    // The glitter: short bright dashes on the water, thick under the sun and thinning to the
    // sides, longer as they come nearer.
    const W = 300, H = 120;
    for (const f of [0, 1]) {
        tex = scene.textures.createCanvas(`intro-glitter-${f}`, W, H);
        ctx = tex.getContext();
        const rand = rng(301 + f * 13);
        for (let y = 1; y < H; y += 1 + Math.floor(rand() * 2)) {
            const k = y / H, spread = 16 + (W / 2 - 20) * k ** 0.8;
            const n = 3 + Math.round(4 * (1 - k));
            for (let i = 0; i < n; i++) {
                const off = (rand() + rand() + rand() - 1.5) / 1.5 * spread;
                const len = 2 + Math.floor(rand() * (2 + 7 * k));
                const near = Math.abs(off) < spread * 0.3;
                ctx.fillStyle = near ? (rand() < 0.6 ? '#ffffff' : '#fff6cf') : (rand() < 0.5 ? '#fff6cf' : '#c7f0ff');
                ctx.globalAlpha = near ? 1 : 0.75;
                ctx.fillRect(Math.round(W / 2 + off - len / 2), y, len, 1);
            }
        }
        ctx.globalAlpha = 1;
        tex.refresh();
    }
    CLOUDS.forEach(([, , w, , seed], i) => cloudTexture(scene, `intro-cloud-${i}`, w, seed));
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
        this.glow = add(s.add.image(this.sunX, this.sunY, 'intro-sunglow').setScale(2 * u).setDepth(D.sky + 0.006));
        this.rays = [0, 1].map(f => add(s.add.image(this.sunX, this.sunY, `intro-rays-${f}`).setScale(2 * u).setDepth(D.sky + 0.007)));
        this.sun = add(s.add.image(this.sunX, this.sunY, 'intro-sun').setScale(2 * u).setDepth(D.sky + 0.008));
        this.clouds = CLOUDS.map(([dx, dy, , size], i) => {
            const img = add(s.add.image(0, this.sunY + dy * u, `intro-cloud-${i}`).setScale(size * u).setDepth(D.sky + 0.012).setAlpha(0.92));
            return { img, x: this.sunX + dx * u };
        });
        // On the water, over the sea's own rows and under the hull's foam: the far sea's ripples
        // at the game's pixel size, and the sun's glitter.
        const left = this.sunX - VIEW.width * u, right = this.shipX + VIEW.width * u;
        this.ripples = add(s.add.tileSprite(left, s.waterY, (right - left) / (2 * u), 160, 'bg-ripples').setOrigin(0)
            .setScale(2 * u).setDepth(D.exterior + 0.26).setAlpha(0.6));
        this.glitter = add(s.add.image(this.sunX, s.waterY, 'intro-glitter-0').setOrigin(0.5, 0).setScale(2 * u).setDepth(D.exterior + 0.27));
        this.sparks = Array.from({ length: 14 }, (_, i) => {
            const r = rng(700 + i * 17), k = r();
            const spark = add(s.add.image(this.sunX + (r() - 0.5) * (60 + 380 * k) * u, s.waterY + (10 + 170 * k) * u, 'dot')
                .setScale((k > 0.5 ? 4 : 2) * u).setDepth(D.exterior + 0.28));
            return { spark, phase: r() * 6, rate: 2 + r() * 3 };
        });
        this.gulls = GULLS.map(([dx, up, speed, size], i) => {
            const img = add(s.add.sprite(0, s.waterY - up * u, 'bg-gull', 0).setOrigin(0.5, 1).setScale(size * u).setDepth(D.fx)
                .setTint(size === 3 ? 0x8f8aa0 : 0xc8c6d4).setFlipX(speed < 0));
            return { img, x0: dx, y: s.waterY - up * u, speed, phase: i * 1.7, rate: 5 + (i % 3) };
        });
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
        this.refreshMenu();
    }

    press() {
        if (this.stage !== 'welcome') return;
        sfx.unlock();
        if (this.buttons[this.selected].id === 'language') {
            nextLanguage();
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
            if (!this.held) this.T += dt;
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
            const open = clamp01(Math.log(z / 0.7) / Math.log(1.7 / 0.7));
            s.viewOverride = s.fromAfar || this.p('corridor') >= 1 ? null : 2 + smooth(open);
            // (The dark round her deck comes with the corridor's opening, not after it: the user.)
            s.dimOverride = s.fromAfar ? 0 : smooth(open);
            this.arrive(this.p('step'), this.p('badge'), this.p('turn'));
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
            this.glow.setAlpha(far * (0.9 + 0.1 * Math.sin(now * 1.7)));
            this.rays.forEach((r, f) => r.setAlpha(far * (0.5 + 0.5 * Math.sin(now * 1.3 + f * Math.PI))));
            // (Nothing here drifts: the sun stands still, and whatever slid past it looked wrong.
            // The water only sways a little in place; the gulls and the glitter are the life in it.)
            for (const c of this.clouds) c.img.setX(c.x).setAlpha(0.92 * far);
            this.ripples.setAlpha(0.6 * far).tilePositionX = Math.round(Math.sin(now * 0.9) * 2);
            this.glitter.setAlpha(far).setTexture(`intro-glitter-${Math.floor(now * 3.2) % 2}`);
            for (const k of this.sparks) k.spark.setAlpha(far * Math.max(0, Math.sin(now * k.rate + k.phase)) ** 3);
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

    // Her coming out: the door opens, she is in it, facing us (`step` 0 to 1); she straightens her
    // badge (`badge`); she turns to go (`turn`). Each by the clock, so any moment can be shown.
    arrive(step, badge, turn) {
        const s = this.s, p = s.player, room = s.world.rooms.crewcabin;
        const open = step > 0.06 && step < 0.82;
        s.setDoorArt(room.outside[0], open ? 'door-crew-ajar' : 'door-crew');
        if (open && !this.doorHeard && this.stage === 'running' && !this.held) sfx.at(p.x, p.y).door();
        this.doorHeard = open || this.doorHeard && step > 0;
        const shown = clamp01((step - 0.16) / 0.34);
        p.setVisible(shown > 0).setAlpha(shown).setFlipX(false);
        const clip = s.herFrames && s.cache.json.get('her-meta').anims.badge;
        let frame = turn >= 0.5 ? s.herFrames.stand : s.herFrames.front;
        if (clip && badge > 0 && badge < 1) frame = clip[Math.min(clip.length - 1, Math.floor(badge * clip.length))];
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
        if (this.full) this.arrive(1, 1, 1);
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
        // The one hint in the game (the user, 2026-11-14: "Add a hint popup, saying 'E to
        // interact'"), over her as she is handed over at a new game's start.
        if (this.full) s.time.delayedCall(through ? 700 : 250, () => s.world.say(t('hint.interact'), HINT_MS));
        if (!s.save.intro) {
            s.save.intro = true;
            writeSave(s.save);
        }
    }
}
