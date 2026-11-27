// The far background (§5.2, the user, 2026-11-07): a Baltic archipelago, low rocky islands with
// pines, red cottages and lighthouses, far away and washed out in the haze; the sky over it with a
// few clouds, the far sea under it. Drawn in code. The horizon stays at one height on the screen,
// about her eye level, so it shows through the open decks, the promenade and the windows; in the
// outside view (O) it lies on the waterline. The islands drift slowly aft as the ship sails, the
// clouds slower still, and they shift a little when she runs (the near islands more than the far).
//
// Everything here is fixed to the camera (scroll factor 0) and laid out on the screen each frame,
// so it never lags behind the camera; the near sea, the foam and the wake are the world's (sea.js).
//
// The sunset (§5.2, §6.1.9: only for the final catch and the way home): a second sky and sea in
// bands of dusk colours, the sun half sunk at the horizon ahead of the bow with its path of light
// on the water, faded in over the day's by `setDusk(k)`; the clouds, the islands and the ripples
// take a tint. The ship's own evening light is a warm wash over the whole picture (the ship
// scene's `duskWash`, a multiply by `DUSK_LIGHT`), so the dusk colours here are written as they
// should look and divided by that light before they are drawn (`dusk()`).

const HAZE = '#cdeeff';           // the sky at the horizon; distance fades everything toward it
const SKY_TOP = '#5fb8f0';
const SKY_FADE = 220;             // px over the horizon the sky takes to deepen to SKY_TOP
const SEA_FAR = '#9fd2f0';        // the sea at the horizon, in the haze
const SEA_NEAR = '#5aa8e6';       // ...and further down, where it meets the near sea's first row
const SEA_FADE = 70;
// Where the horizon settles: this high over the floor she last stood on, about the top of her head
// (the user, 2026-11-08: a little over her eyes). It is fixed to the screen from moment to moment,
// far away as it is, so a jump hardly moves it; but it glides to that height over her floor
// (`HORIZON_SETTLE` s to go most of the way), so the camera's slack never leaves it out of place.
// The evening light on everything (a multiply: 1 leaves a channel as it is).
export const DUSK_LIGHT = [1, 0.84, 0.74];
// The sky at sunset from the top down to the horizon, in bands; the sea under it, far and near.
const DUSK_SKY = ['#584c78', '#7b5586', '#a65d88', '#d36c7c', '#ee8a76', '#f8a771', '#fcc47f', '#fde09a'];
const DUSK_SEA_FAR = '#c08aa0';
const DUSK_SEA_NEAR = '#7a6699';
const DUSK_TINTS = { clouds: '#ff9c9c', ripples: '#ffb08a', islands: '#7a5f86', gulls: '#6a4f6e' };
const DUSK_BAND = 14;                       // px a colour of DUSK_SKY (blended)
const SUN = { at: 0.2, up: 5 };             // how far across the view, its middle over the horizon
export const HORIZON_ABOVE = 58;
const PAD = 8;
export const HORIZON_SETTLE = 1.0;
// The outside view (O) is laid out in the world, not on the screen (the user, 2026-11-14: a picture
// of the whole ship stitched from many views had a strip of sky and a row of clouds for each row
// of views): the islands and the clouds are this many world pixels to each of theirs, so they are
// the size they were on a 1920 px wide screen and grow with the ship when the view is zoomed; the
// sky deepens over `OUTSIDE_SKY` world pixels up from the horizon. `OUTSIDE_CLOUDS`: the rows of
// clouds, each [world px over the horizon, world px to a pixel, how solid, where along the strip
// it starts]: small and faint low over the horizon, far off; bigger and nearer higher up.
const OUTSIDE_SIZE = { islands: 10, clouds: 8 };
const OUTSIDE_SKY = 2400;
const OUTSIDE_CLOUDS = [[330, 4, 0.7, 1100], [1150, 6, 0.8, 420], [2500, 8, 0.85, 0]];

// Each layer: [texture height, how far into the haze (0-1), drift aft px/s, share of her running,
// how far under the horizon its islands sit (px), seed].
const LAYERS = {
    far: [26, 0.72, 2, 0.015, 0, 3],
    near: [44, 0.42, 4.5, 0.035, 3, 9],
};
const STRIP_W = 4096;             // one stretch of the archipelago, then it comes round again

function rng(seed) {
    let s = seed >>> 0;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

function hex(c) {
    return [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
}

// A dusk colour as it has to be drawn to look itself under the evening light.
export function dusk(c) {
    return `rgb(${hex(c).map((v, i) => Math.min(255, Math.round(v / DUSK_LIGHT[i]))).join(',')})`;
}

const num = c => Number('0x' + c.slice(1));
// White at k = 0, `c` at k = 1: a tint coming on.
function tintTo(c, k) {
    const [r, g, b] = hex(c).map(v => Math.round(255 + (v - 255) * k));
    return (r << 16) | (g << 8) | b;
}

// A colour faded `w` of the way into the haze.
function hazed(c, w) {
    const a = hex(c), h = hex(HAZE);
    return `rgb(${a.map((v, i) => Math.round(v + (h[i] - v) * w)).join(',')})`;
}

// One layer of islands along a strip, their feet on its bottom row. Granite humps, most
// of them under a pine forest of spiky crowns, now and then a red cottage at the forest's edge or
// a lighthouse on a bare rock; between them open water. Colours from Resurrect 64, then hazed.
function islandStrip(scene, key, h, haze, seed) {
    const tex = scene.textures.createCanvas(key, STRIP_W, h);
    const ctx = tex.getContext();
    const rand = rng(seed);
    const C = {};
    for (const [k, c] of Object.entries({
        rock: '#966c6c', rockLit: '#ab947a', rockTop: '#c7dcd0', pine: '#374e4a', pineLit: '#547e64',
        red: '#b33831', redDark: '#6e2727', roof: '#3e3546', white: '#ffffff', glass: '#f9c22b',
        surf: '#ffffff',
    })) C[k] = hazed(c, haze);
    const px = (x, y, c, w = 1, hh = 1) => {
        ctx.fillStyle = c;
        ctx.fillRect(((x % STRIP_W) + STRIP_W) % STRIP_W, y, w, hh);
    };
    const foot = h - 1;                                // the row the islands stand on
    const scale = h / 44;                              // the far layer is smaller all over
    let x = Math.round(rand() * 60);
    while (x < STRIP_W) {
        const len = Math.round((30 + rand() ** 1.6 * 260) * scale);
        const rockH = Math.max(1, Math.round((1 + rand() * 3) * scale));
        const wooded = len > 24 * scale && rand() < 0.8;
        const treeH = Math.round((6 + rand() * 9) * scale);
        // The rock: low and smooth, a long flat back sloping into the water at each end, the end
        // toward the sun paler.
        const lean = 0.35 + rand() * 0.3;
        const top = [];
        for (let i = 0; i < len; i++) {
            const t = i / (len - 1);
            const u = t < lean ? t / lean : (1 - t) / (1 - lean);
            top.push(Math.round(rockH * Math.sin(Math.min(1, u * 2.2) * Math.PI / 2)));
        }
        for (let i = 0; i < len; i++) {
            if (!top[i]) continue;
            px(x + i, foot - top[i] + 1, C.rock, 1, top[i]);
            px(x + i, foot - top[i] + 1, i < len * lean ? C.rockTop : C.rockLit);
        }
        // The forest: a dense dark mass over the rock's back, rising from its edges to the middle,
        // its top a row of pointed pine crowns, the left side of each lit.
        let gapAt = -1;
        if (wooded) {
            const a = Math.round(len * (0.06 + rand() * 0.1)), b = Math.round(len * (0.94 - rand() * 0.1));
            if (rand() < 0.45 && b - a > 30 * scale) gapAt = a + Math.round((b - a) * (0.2 + rand() * 0.6));
            const crown = new Array(len).fill(0);
            for (let i = a; i < b; i += 2 + Math.floor(rand() * 2 * scale)) {
                if (gapAt >= 0 && Math.abs(i - gapAt) < 6 * scale) continue;
                const t = (i - a) / Math.max(1, b - a);
                const th = treeH * Math.sin(Math.min(1, Math.min(t, 1 - t) * 3) * Math.PI / 2) ** 0.6 * (0.8 + rand() * 0.35);
                const half = Math.max(1, th * 0.3);
                for (let k = -Math.ceil(half); k <= Math.ceil(half); k++) {
                    const j = i + k;
                    if (j < 0 || j >= len) continue;
                    crown[j] = Math.max(crown[j], Math.round(th * (1 - Math.abs(k) / (half + 1))));
                }
            }
            for (let j = 0; j < len; j++) {
                if (crown[j] < 1) continue;
                const ground = foot - top[j] + 1;
                px(x + j, ground - crown[j], C.pine, 1, crown[j]);
                if (j > 0 && crown[j] > crown[j - 1]) px(x + j, ground - crown[j], C.pineLit, 1, Math.min(crown[j], 1 + crown[j] - crown[j - 1]));
            }
        }
        // A red cottage in the forest's clearing, white corners, a dark roof, a lit window.
        if (gapAt >= 0) {
            const ground = foot - top[gapAt] + 1;
            const w = Math.max(4, Math.round(8 * scale)), hh = Math.max(3, Math.round(5 * scale));
            const cx = x + gapAt - (w >> 1);
            px(cx, ground - hh, C.red, w, hh);
            px(cx, ground - hh, C.white, 1, hh);
            px(cx + w - 1, ground - hh, C.white, 1, hh);
            for (let r = 0; r < Math.ceil(w / 2); r++) px(cx - 1 + r, ground - hh - 1 - r, C.roof, w + 2 - 2 * r);
            if (w >= 6) px(cx + 2, ground - hh + 1, C.white, 2, 2);
        }
        // A lighthouse on a bare rock: white, a red band, its lantern on top.
        if (!wooded && rand() < 0.5) {
            const i = Math.round(len * lean), ground = foot - top[i] + 1;
            const th = Math.max(6, Math.round(15 * scale)), w = Math.max(2, Math.round(3 * scale));
            px(x + i - 1, ground - th, C.white, w, th);
            px(x + i - 1, ground - Math.round(th * 0.62), C.red, w, Math.max(1, Math.round(3 * scale)));
            px(x + i - 2, ground - th - 1, C.roof, w + 2, 1);
            px(x + i - 1, ground - th - 3, C.glass, w, 2);
            px(x + i - 1, ground - th - 4, C.red, w, 1);
        }
        // Surf breaking white at the rock's foot, here and there.
        for (let i = 0; i < len; i += 2 + Math.floor(rand() * 6)) {
            if (top[i] && rand() < 0.5) px(x + i, foot, C.surf, 1 + Math.floor(rand() * 3), 1);
        }
        x += len + Math.round((10 + rand() ** 2 * 220) * scale);
    }
    tex.refresh();
}

// The far clouds: a strip of small soft clouds, generated, hazed toward the horizon's colour
// (tools/build_sky.py, `sky-strip`; the user chose them for the intro's sky, 2026-11-20, over the
// heaps of round puffs drawn here before). Nearly solid: the haze is in their colours.
const CLOUD_ALPHA = 0.85;
// In play the strip's foot is this far over the horizon on the screen (40 at first; 52 since the user, 2026-11-23: "the
// cloud cannot obscure the gulls" on the Spinnaker balcony's windscreen: its lowest clouds behind their white heads read
// as over them). Its clouds are in its rows 9 to 47, so they stand 61 to 99 px over the horizon, 3 px under the screen's
// top at their highest.
const CLOUDS_UP = 52;

// The far sea's ripples: faint short dashes, finer and fewer toward the horizon, so it reads as
// the same water as the near sea's rows of waves (sea.js) where they meet.
const RIPPLES_H = 160;
function rippleStrip(scene) {
    const w = 512;
    const tex = scene.textures.createCanvas('bg-ripples', w, RIPPLES_H);
    const ctx = tex.getContext();
    const rand = rng(41);
    for (let y = 2; y < RIPPLES_H; y += 1 + Math.floor(rand() * 2)) {
        const t = Math.min(1, y / SEA_FADE);
        const n = Math.round(4 + 22 * t);
        for (let i = 0; i < n; i++) {
            ctx.fillStyle = hazed(rand() < 0.15 ? '#ffffff' : '#c7f0ff', 0.6 - 0.45 * t);
            ctx.fillRect(Math.floor(rand() * w), y, 1 + Math.floor(rand() * (1 + 6 * t)), 1);
        }
    }
    tex.refresh();
}

// A far gull: a dark "M" a few pixels wide, in three frames, its wings up, level and down; a whole
// flap is up, level, down, level. Hazed like everything out there.
const GULL = [
    ['X.....X', '.X...X.', '..XXX..', '.......'],
    ['.......', 'XX...XX', '..X.X..', '...X...'],
    ['.......', '...X...', '.XX.XX.', 'X.....X'],
];
function gullSheet(scene) {
    const w = GULL[0][0].length, h = GULL[0].length;
    const tex = scene.textures.createCanvas('bg-gull', w * GULL.length, h);
    const ctx = tex.getContext();
    ctx.fillStyle = hazed('#3e3546', 0.4);
    GULL.forEach((rows, f) => {
        rows.forEach((row, y) => [...row].forEach((c, x) => { if (c === 'X') ctx.fillRect(f * w + x, y, 1, 1); }));
        tex.add(f, 0, f * w, 0, w, h);
    });
    tex.refresh();
}

// The far gulls (§5.2, the user, 2026-11-08): a few of them crossing the sky over the islands, each
// at its own height and pace, flapping, now and then gliding a while; once off one side, another
// comes in from either. Their places are kept here once for the scene and drawn by every Backdrop
// (the sky outside and the windows' copies), so the same gull is in the same place in each.
export class FarGulls {
    constructor(count = 4) {
        this.rand = rng(77);
        this.time = 0;
        this.birds = Array.from({ length: count }, () => this.spawn(true));
    }

    // `u`: how far across the view (0 its left edge, 1 its right), `up`: px over the horizon,
    // `speed`: views a second, its sign the way it flies.
    spawn(anywhere = false) {
        const r = this.rand, dir = r() < 0.5 ? -1 : 1;
        return {
            u: anywhere ? r() : dir > 0 ? -0.03 : 1.03, up: 16 + r() * 70, speed: dir * (0.012 + r() * 0.02),
            rate: 6 + r() * 3, phase: r() * 10, glide: 0, bobPhase: r() * 6,
        };
    }

    update(dt) {
        this.time += dt;
        this.birds = this.birds.map(b => {
            b.u += b.speed * dt;
            if (b.glide > 0) b.glide -= dt;
            else if (this.rand() < dt * 0.08) b.glide = 1 + this.rand() * 2.5;
            return b.u < -0.05 || b.u > 1.05 ? this.spawn() : b;
        });
    }

    // Each gull's frame and its rise and fall with the wingbeats.
    pose(b) {
        if (b.glide > 0) return { frame: 1, bob: 0 };
        const step = Math.floor((this.time + b.phase) * b.rate) % 4;
        return { frame: [0, 1, 2, 1][step], bob: Math.round(Math.sin((this.time + b.bobPhase) * 1.3) * 1.5) };
    }
}

function gradient(scene, key, h, stops) {
    const tex = scene.textures.createCanvas(key, 4, h);
    const ctx = tex.getContext();
    const g = ctx.createLinearGradient(0, 0, 0, h);
    stops.forEach(([at, c]) => g.addColorStop(at, c));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 4, h);
    tex.refresh();
}

// A path of light on the water under a sun (the intro's and the sunset's; plan-the-rest §7b, the user:
// "more realistically-looking sun and reflections"): glints on the far sea's rows, thick under the sun
// and thinning out to the sides, longer and further apart as they come nearer, each flickering on a
// clock of its own (no two frames taking turns). A glint: [x, row, length, kind (0 under the sun, 1,
// 2 out to the sides), how bright, phase, rate]; `drawGlints` paints them as they are at `now` in the
// kinds' colours, moved `dx`.
export function pathGlints(w, h, seed) {
    const rand = rng(seed), glints = [];
    const normal = () => (rand() + rand() + rand() + rand() - 2) / 0.58;      // about N(0, 1)
    let y = 0, row = 0;
    while (y < h) {
        const k = y / h, spread = 8 + (w / 2 - 14) * k ** 0.85;
        const n = Math.round(10 + 8 * (1 - k));
        for (let i = 0; i < n; i++) {
            const off = normal() * spread * 0.42;
            if (Math.abs(off) > spread) continue;
            const near = 1 - Math.abs(off) / spread;
            const len = 1 + Math.floor(rand() * (2 + Math.floor(6 * k * near + 1)));
            const kind = near > 0.6 ? 0 : near > 0.3 ? 1 : 2;
            const bright = near > 0.45 ? 1 : 0.47 + 0.78 * near;
            glints.push([Math.round(w / 2 + off - len / 2), Math.floor(y), len, kind, bright, rand() * 6.3, 1.4 + rand() * 2.8]);
        }
        y += 1 + k * 3.2 + (row++ % 2) * 0.6;
    }
    return glints;
}
export function drawGlints(tex, glints, colours, now, dx = 0) {
    const ctx = tex.getContext();
    ctx.clearRect(0, 0, tex.width, tex.height);
    for (const [x, y, len, kind, bright, phase, rate] of glints) {
        const k = Math.max(0, Math.sin(now * rate + phase));
        const a = bright * k * k;
        if (a < 0.08) continue;
        ctx.globalAlpha = Math.min(1, a);
        ctx.fillStyle = colours[kind];
        ctx.fillRect(x + dx, y, len, 1);
    }
    ctx.globalAlpha = 1;
    tex.refresh();
}

// The sunset's own pictures: the sky blended from its colours (the lowest and brightest at the
// horizon; in flat bands until the user chose it smooth, 2026-11-20), the sea under it, and the
// canvas its path of light is drawn on each frame. Its sun, glow, rays and clouds are built art
// (tools/build_sky.py: `skyart`'s `dusk-*`, `sky-dusk-*`, `sky-layout`'s `dusk`).
const PATH = { w: 170, h: SEA_FADE + RIPPLES_H };
const PATH_COLOURS = ['#fff0c8', '#fdc88c', '#f08c8c'].map(dusk);
function duskTextures(scene) {
    gradient(scene, 'bg-sky-dusk', DUSK_BAND * DUSK_SKY.length, DUSK_SKY.map((c, i) => [i / (DUSK_SKY.length - 1), dusk(c)]));
    gradient(scene, 'bg-sea-dusk', SEA_FADE, [[0, dusk(DUSK_SEA_FAR)], [1, dusk(DUSK_SEA_NEAR)]]);
    scene.textures.createCanvas('bg-sunpath', PATH.w, PATH.h);
}

function makeTextures(scene) {
    if (scene.textures.exists('bg-far')) return;
    for (const [name, [h, haze, , , , seed]] of Object.entries(LAYERS)) islandStrip(scene, `bg-${name}`, h, haze, seed);
    rippleStrip(scene);
    gullSheet(scene);
    gradient(scene, 'bg-sky', SKY_FADE, [[0, SKY_TOP], [1, HAZE]]);
    gradient(scene, 'bg-sea', SEA_FADE, [[0, SEA_FAR], [1, SEA_NEAR]]);
    duskTextures(scene);
}

export class Backdrop {
    constructor(scene, { waterY, depth, gulls = null }) {
        makeTextures(scene);
        this.scene = scene;
        this.waterY = waterY;
        this.gulls = gulls;
        const fixed = o => o.setOrigin(0).setScrollFactor(0);
        this.skyTop = fixed(scene.add.rectangle(0, 0, 4, 4, Number('0x' + SKY_TOP.slice(1)))).setDepth(depth);
        this.sky = fixed(scene.add.image(0, 0, 'bg-sky')).setDepth(depth);
        this.clouds = fixed(scene.add.tileSprite(0, 0, 4, 60, 'sky-strip')).setDepth(depth + 0.01).setAlpha(CLOUD_ALPHA);
        // (The outside view's lower rows; its highest is `clouds` itself.)
        this.cloudRows = OUTSIDE_CLOUDS.slice(0, -1).map(() => fixed(scene.add.tileSprite(0, 0, 4, 60, 'sky-strip')).setDepth(depth + 0.01).setVisible(false));
        this.sea = fixed(scene.add.image(0, 0, 'bg-sea')).setDepth(depth + 0.02);
        this.seaDeep = fixed(scene.add.rectangle(0, 0, 4, 4, Number('0x' + SEA_NEAR.slice(1)))).setDepth(depth + 0.02);
        this.ripples = fixed(scene.add.tileSprite(0, 0, 4, RIPPLES_H, 'bg-ripples')).setDepth(depth + 0.025);
        this.layers = Object.entries(LAYERS).map(([name, [h, , drift, follow, base]], i) => ({
            s: fixed(scene.add.tileSprite(0, 0, 4, h, `bg-${name}`)).setDepth(depth + 0.03 + i * 0.001),
            h, drift, follow, base,
        }));
        this.gullSprites = (gulls?.birds || []).map(() => scene.add.sprite(0, 0, 'bg-gull', 0)
            .setOrigin(0.5, 1).setScrollFactor(0).setDepth(depth + 0.015));
        // The sunset's twins, each just over the day's (see the top of this file).
        this.duskTop = fixed(scene.add.rectangle(0, 0, 4, 4, Phaser.Display.Color.ValueToColor(dusk(DUSK_SKY[0])).color)).setDepth(depth + 0.001);
        this.duskSky = fixed(scene.add.image(0, 0, 'bg-sky-dusk')).setDepth(depth + 0.001);
        this.sunGlow = scene.add.image(0, 0, 'sky-dusk-glow').setScrollFactor(0).setDepth(depth + 0.004);
        this.sun = scene.add.image(0, 0, 'skyart', 'dusk-sun').setScrollFactor(0).setDepth(depth + 0.005);
        // Its god rays and its clouds round it, worked out together (tools/build_sky.py), and its far
        // clouds, taking over from the day's as it comes on.
        const L = this.duskLayout = scene.cache.json.get('sky-layout').dusk;
        this.duskRays = scene.add.image(0, 0, 'sky-dusk-rays').setOrigin(0).setScrollFactor(0).setDepth(depth + 0.006);
        this.duskClouds = L.clouds.map(c => scene.add.image(0, 0, 'skyart', c.frame).setScrollFactor(0).setDepth(depth + 0.012));
        this.duskStrip = fixed(scene.add.tileSprite(0, 0, 4, 60, 'sky-dusk-strip')).setDepth(depth + 0.011);
        this.duskRows = this.cloudRows.map(() => fixed(scene.add.tileSprite(0, 0, 4, 60, 'sky-dusk-strip')).setDepth(depth + 0.011).setVisible(false));
        this.duskSea = fixed(scene.add.image(0, 0, 'bg-sea-dusk')).setDepth(depth + 0.021);
        this.duskDeep = fixed(scene.add.rectangle(0, 0, 4, 4, Phaser.Display.Color.ValueToColor(dusk(DUSK_SEA_NEAR)).color)).setDepth(depth + 0.021);
        this.sunPath = scene.add.image(0, 0, 'bg-sunpath').setOrigin(0.5, 0).setScrollFactor(0).setDepth(depth + 0.026);
        this.glints = pathGlints(PATH.w, PATH.h, 91);
        this.duskOnly = [this.duskTop, this.duskSky, this.sunGlow, this.sun, this.duskRays, ...this.duskClouds, this.duskStrip,
            this.duskSea, this.duskDeep, this.sunPath];
        this.time = 0;
        // (In drawing order: the windows' copies are drawn as a container, which keeps the list's.)
        this.objects = [this.skyTop, this.duskTop, this.sky, this.duskSky, this.sunGlow, this.sun, this.duskRays, ...this.cloudRows,
            this.clouds, ...this.duskRows, this.duskStrip, ...this.duskClouds, this.sea, this.duskSea, this.seaDeep, this.duskDeep, this.ripples, this.sunPath, ...this.layers.map(l => l.s),
            ...this.gullSprites];
        this.setDusk(0);
    }

    // The sunset coming on: 0 the day, 1 the full sunset.
    setDusk(k) {
        this.dusk = k;
        for (const o of this.duskOnly) o.setAlpha(k).setVisible(k > 0);
        // (The day's far clouds give way to the sunset's, which are lit by it.)
        this.clouds.setTint(tintTo(DUSK_TINTS.clouds, k)).setAlpha(CLOUD_ALPHA * (1 - k));
        this.cloudRows.forEach((c, i) => c.setTint(tintTo(DUSK_TINTS.clouds, k)).setAlpha(OUTSIDE_CLOUDS[i][2] * (1 - k)));
        this.duskStrip.setAlpha(CLOUD_ALPHA * k);
        this.duskRows.forEach((c, i) => c.setAlpha(OUTSIDE_CLOUDS[i][2] * k));
        this.ripples.setTint(tintTo(DUSK_TINTS.ripples, k));
        for (const l of this.layers) l.s.setTint(tintTo(DUSK_TINTS.islands, k));
        for (const g of this.gullSprites) g.setTint(tintTo(DUSK_TINTS.gulls, k));
    }

    // Lay it all out for this frame, fixed to the camera: the horizon `horizonOnScreen` px from the
    // top of the screen, or in the outside view (`outside`) on the waterline. `far`: the outside
    // view's sizes for this one (the intro's wide views: `{ islands }`, world px to a pixel). `keep`: in play, how much
    // bigger than a pixel to a pixel everything is drawn, so that under a zoom out (a look-out's, `VIEW.zoom / zoom`) the
    // far background keeps the size it has on the screen in play, only its horizon moving.
    update(dt, outside = false, horizonOnScreen = 0, far = null, keep = 1) {
        this.time += dt;
        const cam = this.scene.cameras.main;
        const z = cam.zoom, W = cam.width, H = cam.height, cx = W / 2, cy = H / 2;
        // A scroll-factor-0 object at (x, y) shows at the screen's centre plus (x - centre) x zoom:
        // the world spot for a screen spot, and the screen's size in world pixels.
        const wx = sx => cx + (sx - cx) / z, wy = sy => cy + (sy - cy) / z;
        // (`PAD` px past the screen's edge all round: a shake of the picture, the horn's, moves it that far.)
        const left = wx(0) - PAD, top = wy(0) - PAD, width = W / z + 2 * PAD, bottom = wy(H) + PAD;
        if (outside) horizonOnScreen = (this.waterY - cam.scrollY - cy) * z + cy;
        const hy = Math.round(wy(horizonOnScreen));

        // From outside the sky deepens over a fixed stretch of the world, not into a thin line.
        const fade = outside ? OUTSIDE_SKY : SKY_FADE * keep, seaFade = SEA_FADE * (outside ? 1 : keep);
        this.sky.setPosition(left, hy - fade).setDisplaySize(width, fade);
        this.skyTop.setPosition(left, top).setSize(width, Math.max(0, hy - fade - top));
        this.sea.setPosition(left, hy).setDisplaySize(width, seaFade);
        this.seaDeep.setPosition(left, hy + seaFade).setSize(width, Math.max(0, bottom - hy - seaFade));
        if (this.dusk > 0) {
            // (Its bands keep their height in play; zoomed right out they stretch with the day's sky.)
            const bands = outside ? fade : DUSK_BAND * DUSK_SKY.length * keep;
            this.duskSky.setPosition(left, hy - bands).setDisplaySize(width, bands);
            this.duskTop.setPosition(left, top).setSize(width, Math.max(0, hy - bands - top));
            this.duskSea.setPosition(left, hy).setDisplaySize(width, seaFade);
            this.duskDeep.setPosition(left, hy + seaFade).setSize(width, Math.max(0, bottom - hy - seaFade));
            // The sun ahead of the bow, half sunk; its path of light on the water under it.
            const k = outside ? OUTSIDE_SIZE.islands : keep;
            const sx = Math.round(left + width * SUN.at), sy = hy - SUN.up * k, L = this.duskLayout;
            this.sun.setScale(k).setPosition(sx, sy);
            this.sunGlow.setScale(k / 2).setPosition(sx, sy);
            this.duskRays.setScale(k / 2).setPosition(sx + L.rays.x * k, sy + L.rays.y * k);
            this.duskClouds.forEach((c, i) => c.setScale(k).setPosition(sx + L.clouds[i].x * k, sy + L.clouds[i].y * k));
            this.sunPath.setScale(k).setPosition(sx, hy);
            // (Drawn once a frame, though the windows' views have backdrops of their own.)
            const tex = this.scene.textures.get('bg-sunpath');
            if (tex.drawnAt !== this.scene.time.now) {
                tex.drawnAt = this.scene.time.now;
                drawGlints(tex, this.glints, PATH_COLOURS, this.time);
            }
        }
        const run = cam.scrollX;
        // From outside (`OUTSIDE_SIZE`, `OUTSIDE_CLOUDS`) the islands and the clouds are far bigger
        // than a pixel to a pixel, or they would shrink to nothing with the ship, and they stand in
        // the world: `shown` is the world x of the screen's left edge, which each strip starts
        // from. In play they are fixed to the screen and only shift a little as she runs, and the
        // clouds stand well up in the sky (the user, 2026-11-08).
        const sc = outside ? OUTSIDE_SIZE.clouds : keep, si = outside ? far?.islands ?? OUTSIDE_SIZE.islands : keep;
        const shown = run + left, sr = outside ? 1 : keep;
        this.ripples.setScale(sr).setPosition(left, hy).setSize(width / sr, RIPPLES_H);
        this.ripples.tilePositionX = Math.round((outside ? shown : run * 0.05) / sr - this.time * 8);
        const cloudFoot = outside ? hy - OUTSIDE_CLOUDS.at(-1)[0] : hy - CLOUDS_UP * keep;
        this.clouds.setScale(sc).setPosition(left, cloudFoot - 60 * sc).setSize(width / sc, 60);
        this.clouds.tilePositionX = Math.round((outside ? shown : run * 0.01) / sc - this.time * 1.2);
        this.duskStrip.setScale(sc).setPosition(this.clouds.x, this.clouds.y).setSize(width / sc, 60);
        this.duskStrip.tilePositionX = this.clouds.tilePositionX;
        this.cloudRows.forEach((c, i) => {
            const [up, size, , start] = OUTSIDE_CLOUDS[i];
            c.setVisible(outside);
            if (!outside) return;
            c.setScale(size).setPosition(left, hy - up - 60 * size).setSize(width / size, 60);
            c.tilePositionX = Math.round(shown / size + start - this.time * 1.2 * (size / sc));
        });
        this.duskRows.forEach((d, i) => {
            const c = this.cloudRows[i];
            d.setVisible(outside && this.dusk > 0);
            if (outside) d.setScale(c.scaleX).setPosition(c.x, c.y).setSize(c.width, 60).tilePositionX = c.tilePositionX;
        });
        for (const l of this.layers) {
            l.s.setScale(si).setPosition(left, hy - (l.h - 1 - l.base) * si).setSize(width / si, l.h);
            l.s.tilePositionX = Math.round((outside ? shown : run * l.follow) / si - this.time * l.drift);
        }
        // The far gulls, over the islands: across the screen in play, across the world from outside.
        const span = outside ? this.scene.map?.widthInPixels ?? width : width, from = outside ? -run : left;
        this.gullSprites.forEach((g, i) => {
            const b = this.gulls.birds[i], { frame, bob } = this.gulls.pose(b);
            g.setFrame(frame).setScale(si).setPosition(Math.round(from + b.u * span), Math.round(hy - (b.up + bob) * si));
        });
    }
}
