// The welcome screen, the start sequence and the game's intro (docs/intro.md, the user's own
// document; built 2026-11-14). All of it is the ship scene's own picture, so one runs into the next
// with no cut:
//
//   The welcome screen: the sun in the middle of the sky with a few clouds round it, dimmed and out
//   of focus; over it the game's name and two big buttons, PLAY and LANGUAGE (English or
//   Ukrainian: src/lang.js). ↑/↓ and Enter, Space or E, or the mouse.
//   The start sequence: the menu melts away, the sky comes into focus and to its full brightness.
//   The intro: the camera tilts down to the sea and the Baltic shore (gulls, the sun's glitter on
//   the water), pans right until the whole ship has come in from the right, then zooms in on
//   deck 3: its side opens on the crew corridor, the door marked CREW, her cabin behind it, and
//   her at her standing mirror. Close on her (the user: "only her profile up from her waist
//   together with a part of the mirror"), drawn bigger and finer, and the mirror with her (the
//   `her-close` sheet and `close-mirror`: tools/build_closeup.py): she straightens her name badge,
//   which says BUMBUSIK. The camera draws back to the game's own view, her usual figure in the
//   bigger one's place; she turns from the mirror to the door, the HUD comes up and she is the
//   player's.
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

import { VIEW, PLAYER } from './config.js';
import { sfx } from './sfx.js';
import { t, nextLanguage } from './lang.js';
import { writeSave } from './save.js';
import { cloudTexture } from './background.js';

const HALF = PLAYER.height / 2;
// The parts, in order, and the seconds each takes: a new game's, and a game's under way.
export const PARTS = {
    full: [['focus', 2.4], ['sky', 0.8], ['down', 4.6], ['sea', 2.4], ['right', 6.6], ['ship', 1.3], ['dive', 5.6],
           ['corridor', 0.9], ['door', 2.8], ['her', 3.0], ['badge', 3.6], ['out', 3.2], ['turn', 0.8]],
    back: [['focus', 2.0], ['sky', 0.5], ['down', 3.2], ['sea', 1.2], ['right', 4.6], ['ship', 0.8], ['near', 2.4]],
};
const DIM = 0.36;                 // the welcome screen's shade over the sky
const BLUR = 2.0;                 // ...and how far out of focus it is
const CLOSE_BLUR = 2.6;           // the cabin behind her in the close-up
// The close-up: its zoom (her finer portrait is eight pixels to one of the game's, so two of the
// screen's to each of its own), the view's middle from where she stands (px forward of her, px
// over the floor: her profile from the waist up, the mirror's edge beside her), and the zooms
// between which her portrait comes in over her game figure (it ends at her waist: it is whole
// only once the view's foot has come up to there).
const CLOSE = { zoom: 16, forward: 5, up: 46, from: 12.6, full: 15.4 };
const SUN_UP = 365;               // the sun over the horizon, in screen px of the wide view
const HORIZON = 140;               // the horizon under the middle of the screen in the wide views
const PAN = 960;                  // how far left of the ship the sea's view is, in screen px
const DOOR_ZOOM = 5;              // how close the camera is as the cabin shows
const MIRROR_X = 34;              // where she stands at her mirror, from the cabin's left edge
// The few clouds round the sun: [px right of it, px under it, texels wide, screen px a texel, seed].
const CLOUDS = [[-250, 56, 96, 3, 5], [228, -74, 84, 3, 12], [150, 110, 60, 2, 23], [-190, -112, 52, 2, 31], [372, 62, 70, 2, 44],
                [-420, -30, 64, 2, 57]];
// The gulls over the sea: [px right of the sea view's middle, px over the horizon, px/s, screen px a texel].
const GULLS = [[-330, 96, 26, 2], [-60, 150, -18, 2], [210, 60, 22, 2], [380, 128, -30, 3], [-200, 40, 34, 3], [60, 206, 14, 2]];

const clamp01 = v => Math.min(1, Math.max(0, v));
const smooth = k => k * k * (3 - 2 * k);
const smoother = k => k * k * k * (k * (k * 6 - 15) + 10);
const lerp = (a, b, k) => a + (b - a) * k;

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
        this.buildCloseUp();
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
            return { img, x: this.sunX + dx * u, drift: (size === 3 ? 2.2 : 1.3) * u };
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

    // Her finer portrait and the finer piece of her mirror for the close-up, on a camera of their
    // own over the world's, so the cabin behind them can go out of focus while they stay sharp.
    // (With no portrait drawn, tools/build_closeup.py says so, and her game figure stays.)
    buildCloseUp() {
        const s = this.s, room = s.world.rooms.crewcabin;
        this.heroLayer = s.add.layer();
        this.heroCam = s.cameras.add(0, 0, VIEW.width, VIEW.height).setVisible(false);
        const meta = s.cache.json.get('her-close-meta');
        this.close = this.full && meta?.portrait && s.textures.exists('her-close') ? meta : null;
        if (!this.close) return;
        const k = 1 / meta.perWorld;
        this.glass = s.add.image(room.def.x0 + meta.mirror.at[0], room.floor + meta.mirror.at[1], 'close-mirror').setOrigin(0).setScale(k).setAlpha(0);
        this.hero = s.add.image(room.def.x0 + MIRROR_X + meta.at[0], room.floor + meta.at[1], 'her-close', meta.frames.stand)
            .setOrigin(0).setScale(k).setAlpha(0);
        this.heroLayer.add([this.glass, this.hero]);
    }

    // --- The welcome screen -----------------------------------------------------------------------

    buildMenu() {
        const s = this.s, { width: W, height: H } = VIEW;
        this.menuLayer = s.add.layer();
        this.menuCam = s.cameras.add(0, 0, W, H);
        for (const c of [s.cameras.main, s.washCam, s.uiCam]) c.ignore([this.menuLayer, this.heroLayer]);
        this.heroCam.ignore([s.worldLayer, s.washLayer, s.uiLayer, this.menuLayer]);
        this.menuCam.ignore([s.worldLayer, s.washLayer, s.uiLayer, this.heroLayer]);
        this.shade = s.add.rectangle(0, 0, W, H, 0x0d1422).setOrigin(0).setAlpha(DIM);
        this.title = s.add.text(W / 2, 196, '', {
            fontFamily: 'Georgia, serif', fontSize: '96px', color: '#ffffff', stroke: '#1d2b53', strokeThickness: 9,
        }).setOrigin(0.5);
        this.buttons = ['play', 'language'].map((id, i) => {
            const y = 352 + i * 82, w = 372, h = 64;
            const box = s.add.graphics();
            const label = s.add.text(W / 2, y, '', { fontFamily: 'Georgia, serif', fontSize: '32px', fontStyle: 'bold', color: '#1d2b53' }).setOrigin(0.5);
            const zone = s.add.zone(W / 2, y, w, h).setInteractive({ useHandCursor: true });
            zone.on('pointerover', () => this.select(i));
            zone.on('pointerdown', () => { this.select(i); this.press(); });
            return { id, y, w, h, box, label, zone };
        });
        this.menu = [this.title, ...this.buttons.flatMap(b => [b.box, b.label, b.zone])];
        this.menuLayer.add([this.shade, ...this.menu]);
        this.refreshMenu();
    }

    refreshMenu() {
        const W = VIEW.width;
        this.title.setText(t('title'));
        this.buttons.forEach((b, i) => {
            const on = i === this.selected;
            b.label.setText(b.id === 'play' ? t('menu.play') : `${t('menu.language')}: ${t('language.name')}`);
            b.box.clear();
            b.box.fillStyle(0x1d2b53, 0.55).fillRoundedRect(W / 2 - b.w / 2 + 3, b.y - b.h / 2 + 5, b.w, b.h, 14);
            b.box.fillStyle(on ? 0xffffff : 0xe6edf2, 1).fillRoundedRect(W / 2 - b.w / 2, b.y - b.h / 2, b.w, b.h, 14);
            b.box.lineStyle(on ? 5 : 3, on ? 0xf28c28 : 0x1d2b53, 1).strokeRoundedRect(W / 2 - b.w / 2, b.y - b.h / 2, b.w, b.h, 14);
        });
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
        let reveal = 0, hero = 0;
        if (this.full) {
            const door = this.p('door'), her = this.p('her'), out = this.p('out');
            const room = s.world.rooms.crewcabin, herX = room.def.x0 + MIRROR_X;
            const mid = { x: herX - CLOSE.forward, y: room.floor - CLOSE.up };
            const play = { x: herX, y: room.floor - HALF };
            if (door > 0) z = VIEW.zoom * (DOOR_ZOOM / VIEW.zoom) ** smooth(door);
            if (her > 0) {
                z = DOOR_ZOOM * (CLOSE.zoom / DOOR_ZOOM) ** smooth(her);
                cx = lerp(to.x, mid.x, smooth(her));
                cy = lerp(to.y, mid.y, smooth(her));
            }
            if (out > 0) {
                z = CLOSE.zoom * (VIEW.zoom / CLOSE.zoom) ** smooth(out);
                cx = lerp(mid.x, play.x, smooth(out));
                cy = lerp(mid.y, play.y, smooth(out));
            }
            reveal = door >= 1 ? 1 : clamp01((door - 0.55) / 0.45);
            hero = this.close && her > 0 ? clamp01((z - CLOSE.from) / (CLOSE.full - CLOSE.from)) : 0;
        }
        // (The blur first: it changes the camera's size, and the camera is centred after.)
        this.setBlur(BLUR * (1 - smooth(focus)) + CLOSE_BLUR * hero);
        cam.setZoom(z);
        cam.centerOn(cx, cy);
        this.zoom = z;

        // The ship: closed from afar; then deck 3's side opens on the corridor (a new game), or
        // the game's own cut-away takes over where she is.
        s.fromAfar = z < 0.6;
        s.horizonOnScreen = undefined;
        if (this.full) {
            const open = clamp01(Math.log(z / 0.7) / Math.log(1.7 / 0.7));
            s.viewOverride = s.fromAfar ? null : 2 + smooth(open);
            this.cabin(reveal);
            this.closeUp(hero, cx, cy, z);
        }

        // The welcome's shade and blur, lifting; the menu melting away; at a short intro's end
        // the picture going over to the game through the dark.
        const melt = this.stage === 'welcome' ? 1 : 1 - clamp01(this.T / 0.6);
        for (const o of this.menu) o.setAlpha(melt);
        this.title.setY(196 - (1 - melt) * 26);
        this.shade.setAlpha(this.full ? DIM * (1 - smooth(focus)) : Math.max(DIM * (1 - smooth(focus)), clamp01((this.p('near') - 0.62) / 0.38)));

        // The sun, its clouds, the glitter, the gulls: all gone by the time the ship fills the view.
        const far = 1 - clamp01((z / this.fit - 1.25) / 1.6);
        const now = this.clock;
        for (const o of this.dressing) o.setVisible(far > 0);
        if (far > 0) {
            this.sun.setAlpha(far);
            this.glow.setAlpha(far * (0.9 + 0.1 * Math.sin(now * 1.7)));
            this.rays.forEach((r, f) => r.setAlpha(far * (0.5 + 0.5 * Math.sin(now * 1.3 + f * Math.PI))));
            for (const c of this.clouds) c.img.setX(c.x + now * c.drift).setAlpha(0.92 * far);
            this.ripples.setAlpha(0.6 * far).tilePositionX = -now * 7;
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

    // The middle of the corridor's view: the door marked CREW, from its floor to its sign.
    door() {
        const d = this.s.world.rooms.crewcabin.def.doors[0];
        return { x: d.outX, y: d.outY - 50 };
    }

    // Her cabin showing in the corridor's place, and her in it at her mirror, as `k` goes 0 to 1.
    cabin(k) {
        const s = this.s, p = s.player, room = s.world.rooms.crewcabin;
        const inside = k > 0;
        if (inside !== (s.route === room.route)) {
            s.route = inside ? room.route : 'inside';
            p.body.reset(inside ? room.def.x0 + MIRROR_X : room.def.doors[0].outX, room.floor);
            s.takeoffY = room.floor;
            s.pose('stand');
        }
        room.room.setAlpha(k);
        room.dim.setAlpha(k);
        // At her mirror she is turned to it; back at the game's scale she turns to the door, by
        // way of facing us.
        const turn = this.p('turn'), pose = turn > 0.3 && turn < 0.65 ? 'front' : 'stand';
        if (pose !== this.posed) s.pose(this.posed = pose);
        p.setVisible(inside).setAlpha(k).setFlipX(turn < 0.65);
    }

    // Her portrait and the mirror's finer piece over the game's own, as `k` goes 0 to 1 and back;
    // the portrait's frame by the clock: still, then her hand to her badge and down again.
    closeUp(k, cx, cy, z) {
        const s = this.s, c = this.close;
        this.heroCam.setVisible(!!c && k > 0);
        if (!c) return;
        this.hero.setAlpha(k);
        this.glass.setAlpha(k);
        if (k <= 0) return;
        this.heroCam.setZoom(z);
        this.heroCam.centerOn(cx, cy);
        const badge = this.p('badge'), list = c.frames.badge;
        this.hero.setFrame(badge <= 0 ? c.frames.stand : list[Math.min(list.length - 1, Math.floor(badge * list.length))]);
        s.player.setAlpha(1 - k);
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
        if (this.full) this.cabin(1);
        p.setVisible(true).setAlpha(1);
        for (const o of [...this.dressing, ...this.menu]) o.destroy();
        this.hero?.destroy();
        this.glass?.destroy();
        s.cameras.remove(this.heroCam);
        s.fromAfar = false;
        s.viewOverride = null;
        s.viewDeck = null;
        s.horizonOnScreen = undefined;
        cam.setZoom(VIEW.zoom);
        cam.setBounds(0, -560, s.map.widthInPixels, s.map.heightInPixels + 560);
        cam.startFollow(p, true, 0.15, 0.15);
        cam.setFollowOffset(0, HALF);
        cam.centerOn(p.x, p.y - HALF);
        s.updateCutaway(0);
        s.mode = 'play';
        s.grounded = true;
        s.lastGroundedAt = s.time.now;
        s.uiCam.setVisible(true).setAlpha(0);
        s.tweens.add({ targets: s.uiCam, alpha: 1, duration: 700, delay: through ? 300 : 0 });
        this.shade.setAlpha(through ? 1 : 0);
        s.tweens.add({ targets: this.shade, alpha: 0, duration: through ? 500 : 1, onComplete: () => {
            this.shade.destroy();
            s.cameras.remove(this.menuCam);
            s.intro = null;
        } });
        if (!s.save.intro) {
            s.save.intro = true;
            writeSave(s.save);
        }
    }
}
