// The far background (§5.2, the user, 2026-11-07): a Baltic archipelago, low rocky islands with
// pines, red cottages and lighthouses, far away and washed out in the haze; the sky over it with a
// few clouds, the far sea under it. Drawn in code. The horizon stays at one height on the screen,
// about her eye level, so it shows through the open decks, the promenade and the windows; in the
// outside view (O) it lies on the waterline. The islands drift slowly aft as the ship sails, the
// clouds slower still, and they shift a little when she runs (the near islands more than the far).
//
// Everything here is fixed to the camera (scroll factor 0) and laid out on the screen each frame,
// so it never lags behind the camera; the near sea, the foam and the wake are the world's (sea.js).

const HAZE = '#cdeeff';           // the sky at the horizon; distance fades everything toward it
const SKY_TOP = '#5fb8f0';
const SKY_FADE = 220;             // px over the horizon the sky takes to deepen to SKY_TOP
const SEA_FAR = '#9fd2f0';        // the sea at the horizon, in the haze
const SEA_NEAR = '#5aa8e6';       // ...and further down, where it meets the near sea's first row
const SEA_FADE = 70;
export const HORIZON = 0.43;      // the horizon's height on the screen, from the top (her eyes)
const OUTSIDE_SIZE = { islands: 1.5, clouds: 1.2 };

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

// Fair-weather clouds: heaps of round puffs, the biggest in the middle and highest, the smaller
// ones lower at the sides, so each cloud's underside is lumpy, not a flat line (the user,
// 2026-11-08); each puff's lower rim shaded. Drawn see-through (`CLOUD_ALPHA`), so they sit back in
// the sky's haze rather than in front of it.
const CLOUD_ALPHA = 0.5;
function cloudStrip(scene) {
    const w = 2048, h = 60;
    const tex = scene.textures.createCanvas('bg-clouds', w, h);
    const ctx = tex.getContext();
    const rand = rng(21);
    const blob = (cx, cy, rx, ry) => {
        for (let yy = -Math.ceil(ry); yy <= Math.ceil(ry); yy++) {
            const half = Math.floor(rx * Math.sqrt(Math.max(0, 1 - (yy / ry) ** 2)));
            if (half > 0) ctx.fillRect(Math.round(cx - half), Math.round(cy + yy), half * 2, 1);
        }
    };
    let x = 40;
    while (x < w - 140) {
        const cw = 34 + Math.round(rand() * 80), base = 26 + Math.round(rand() * (h - 40));
        const n = 4 + Math.floor(rand() * 4);
        const puffs = [];
        for (let p = 0; p < n; p++) {
            const t = (p + 0.5) / n, mid = 1 - Math.abs(t - 0.5) * 2;      // 1 in the middle
            const r = (cw / n) * (0.6 + 0.5 * mid + rand() * 0.35);
            puffs.push([x + cw * t + (rand() - 0.5) * 4, base - r * (0.2 + 0.5 * mid) + (rand() - 0.5) * 3, r]);
        }
        ctx.fillStyle = '#c7dcd0';                      // the shaded rims
        for (const [cx, cy, r] of puffs) blob(cx, cy, r, r * 0.8);
        ctx.fillStyle = '#ffffff';                      // the sunlit body, a little higher
        for (const [cx, cy, r] of puffs) blob(cx, cy - Math.max(1, r * 0.22), r * 0.95, r * 0.75);
        x += cw + 60 + Math.round(rand() * 300);
    }
    tex.refresh();
}

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

function gradient(scene, key, h, stops) {
    const tex = scene.textures.createCanvas(key, 4, h);
    const ctx = tex.getContext();
    const g = ctx.createLinearGradient(0, 0, 0, h);
    stops.forEach(([at, c]) => g.addColorStop(at, c));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 4, h);
    tex.refresh();
}

function makeTextures(scene) {
    if (scene.textures.exists('bg-far')) return;
    for (const [name, [h, haze, , , , seed]] of Object.entries(LAYERS)) islandStrip(scene, `bg-${name}`, h, haze, seed);
    cloudStrip(scene);
    rippleStrip(scene);
    gradient(scene, 'bg-sky', SKY_FADE, [[0, SKY_TOP], [1, HAZE]]);
    gradient(scene, 'bg-sea', SEA_FADE, [[0, SEA_FAR], [1, SEA_NEAR]]);
}

export class Backdrop {
    constructor(scene, { waterY, depth }) {
        makeTextures(scene);
        this.scene = scene;
        this.waterY = waterY;
        const fixed = o => o.setOrigin(0).setScrollFactor(0);
        this.skyTop = fixed(scene.add.rectangle(0, 0, 4, 4, Number('0x' + SKY_TOP.slice(1)))).setDepth(depth);
        this.sky = fixed(scene.add.image(0, 0, 'bg-sky')).setDepth(depth);
        this.clouds = fixed(scene.add.tileSprite(0, 0, 4, 60, 'bg-clouds')).setDepth(depth + 0.01).setAlpha(CLOUD_ALPHA);
        this.sea = fixed(scene.add.image(0, 0, 'bg-sea')).setDepth(depth + 0.02);
        this.seaDeep = fixed(scene.add.rectangle(0, 0, 4, 4, Number('0x' + SEA_NEAR.slice(1)))).setDepth(depth + 0.02);
        this.ripples = fixed(scene.add.tileSprite(0, 0, 4, RIPPLES_H, 'bg-ripples')).setDepth(depth + 0.025);
        this.layers = Object.entries(LAYERS).map(([name, [h, , drift, follow, base]], i) => ({
            s: fixed(scene.add.tileSprite(0, 0, 4, h, `bg-${name}`)).setDepth(depth + 0.03 + i * 0.001),
            h, drift, follow, base,
        }));
        this.time = 0;
        this.objects = [this.skyTop, this.sky, this.clouds, this.sea, this.seaDeep, this.ripples, ...this.layers.map(l => l.s)];
    }

    // Lay it all out for this frame. `outside`: the outside view, the horizon on the waterline.
    update(dt, outside = false) {
        this.time += dt;
        const cam = this.scene.cameras.main;
        const z = cam.zoom, W = cam.width, H = cam.height, cx = W / 2, cy = H / 2;
        // A scroll-factor-0 object at (x, y) shows at the screen's centre plus (x - centre) x zoom:
        // the world spot for a screen spot, and the screen's size in world pixels.
        const wx = sx => cx + (sx - cx) / z, wy = sy => cy + (sy - cy) / z;
        const left = wx(0), top = wy(0), width = W / z, bottom = wy(H);
        const horizonOnScreen = outside ? (this.waterY - cam.scrollY - cy) * z + cy : H * HORIZON;
        const hy = Math.round(wy(horizonOnScreen));

        // Zoomed right out, the sky fades over most of its height, not into a thin line.
        const fade = outside ? Math.max(SKY_FADE, (hy - top) * 0.7) : SKY_FADE;
        this.sky.setPosition(left, hy - fade).setDisplaySize(width, fade);
        this.skyTop.setPosition(left, top).setSize(width, Math.max(0, hy - fade - top));
        this.sea.setPosition(left, hy).setDisplaySize(width, SEA_FADE);
        this.seaDeep.setPosition(left, hy + SEA_FADE).setSize(width, Math.max(0, bottom - hy - SEA_FADE));
        const run = cam.scrollX;
        // Zoomed right out (the outside view), the islands and the clouds keep a size on the
        // screen rather than shrinking to nothing with the ship, and the clouds stand up in the
        // sky, half way from the horizon to the top; in play too they stand well up in it (the user,
        // 2026-11-08). `OUTSIDE_SIZE`: the screen pixels for each of their pixels there.
        const scale = k => outside ? Math.max(1, k / z) : 1;
        const sc = scale(OUTSIDE_SIZE.clouds), si = scale(OUTSIDE_SIZE.islands);
        this.ripples.setPosition(left, hy).setSize(width, RIPPLES_H);
        this.ripples.tilePositionX = Math.round(run * 0.05 - this.time * 8);
        const cloudFoot = outside ? wy(horizonOnScreen / 2) : hy - 40;    // in play, well up in the sky
        this.clouds.setScale(sc).setPosition(left, cloudFoot - 60 * sc).setSize(width / sc, 60);
        this.clouds.tilePositionX = Math.round(run * 0.01 / sc - this.time * 1.2);
        for (const l of this.layers) {
            l.s.setScale(si).setPosition(left, hy - (l.h - 1 - l.base) * si).setSize(width / si, l.h);
            l.s.tilePositionX = Math.round(run * l.follow / si - this.time * l.drift);
        }
    }
}
