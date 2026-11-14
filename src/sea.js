// The sea round the ship (§5.2, the user, 2026-11-07): drawn in code. Rows of waves from the
// waterline down, the far ones small and slow, the near ones bigger and faster, each row gently
// rising and falling, sun glints on them; white foam along the waterline, a bow wave at the stem,
// the wake streaming from the stern. The ship is under way bow first, the bow on the left, so the
// water streams past toward the stern, to the right.

import { dusk } from './background.js';

// From the waterline down: [height, crest colour, water colour, trough colour, speed px/s, wave
// length px, bob px]. The last row runs on to the bottom.
const BANDS = [
    [6, '#c7f0ff', '#5aa8e6', '#4d93d6', 14, 24, 0],
    [12, '#a9dcf7', '#4d9be6', '#428bd4', 18, 32, 0.5],
    [20, '#8fd3ff', '#4489d6', '#3a79c2', 24, 48, 1],
    [30, '#8fd3ff', '#3a7cc8', '#336db4', 32, 72, 1.5],
    [44, '#7cc3ee', '#336fb8', '#2c61a6', 42, 104, 2],
    [64, '#6fb6e6', '#2c63a8', '#265597', 54, 150, 2],
];
const DEEP = ['#265597', '#1f4a87', '#1b4178'];   // the rest, darkening down
// At sunset (§6.1.9; background.js has the sky's side of it): each row's crest, water and trough,
// and the deep water; laid over the day's rows and faded in by `setDusk(k)`. Written as they should
// look, and drawn divided by the evening light (`dusk()`).
const DUSK_BANDS = [
    ['#fdcbb0', '#7a6699', '#6e5c90'],
    ['#fca790', '#735f95', '#67558a'],
    ['#fca790', '#6b5890', '#5f4d84'],
    ['#f68181', '#62508a', '#57467e'],
    ['#ed8099', '#594882', '#4e3f76'],
    ['#cf657f', '#50407a', '#45376d'],
];
const DUSK_DEEP = ['#45376d', '#3a2f60', '#322853'];
const DUSK_FOAM = [0xff, 0xd9, 0xc8];

// A small fixed random sequence, so the sea looks the same every time.
function rng(seed) {
    let s = seed >>> 0;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

// One row's texture: water with crests along its top, a trough under each, glints; it tiles
// across (whole wave lengths over its width).
function bandTexture(scene, key, h, [crest, water, trough], waveLen, seed, glint = '#ffffff') {
    const w = waveLen * Math.max(4, Math.round(256 / waveLen));
    const tex = scene.textures.createCanvas(key, w, h);
    const ctx = tex.getContext();
    const rand = rng(seed);
    ctx.fillStyle = water;
    ctx.fillRect(0, 0, w, h);
    // Two lines of waves per row, offset; each wave a crest arc with its dark side under it.
    for (const [row, phase] of [[Math.round(h * 0.2), 0], [Math.round(h * 0.65), 0.5]]) {
        for (let x0 = 0; x0 < w; x0 += waveLen) {
            const start = x0 + Math.round((phase + rand() * 0.3) * waveLen) % waveLen;
            const len = Math.round(waveLen * (0.35 + rand() * 0.3));
            const lift = Math.max(1, Math.round(h * 0.12));
            for (let i = 0; i < len; i++) {
                const t = i / (len - 1);
                const y = row - Math.round(Math.sin(t * Math.PI) * lift);
                const x = (start + i) % w;
                ctx.fillStyle = trough;
                ctx.fillRect(x, y + 1, 1, Math.max(1, Math.round(h * 0.1)));
                ctx.fillStyle = crest;
                ctx.fillRect(x, y, 1, 1);
            }
            // A glint now and then on the crest.
            if (rand() < 0.5) {
                ctx.fillStyle = glint;
                const gx = (start + Math.round(len * (0.3 + rand() * 0.4))) % w;
                ctx.fillRect(gx, row - Math.max(1, Math.round(h * 0.12)), Math.max(1, Math.round(waveLen / 16)), 1);
            }
        }
    }
    tex.refresh();
}

// The foam along the waterline: white blobs and a broken white line, tiling across.
function foamTexture(scene) {
    const w = 192, h = 10;
    const tex = scene.textures.createCanvas('sea-foam', w, h);
    const ctx = tex.getContext();
    const rand = rng(7);
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.fillRect(0, 0, w, 2);
    for (let i = 0; i < 46; i++) {
        const x = Math.floor(rand() * w), bw = 2 + Math.floor(rand() * 7), bh = 1 + Math.floor(rand() * 4);
        ctx.fillStyle = rand() < 0.6 ? '#ffffff' : '#e3f4fb';
        for (let dx = 0; dx < bw; dx++) ctx.fillRect((x + dx) % w, 1, 1, bh - (dx === 0 || dx === bw - 1 ? 1 : 0));
    }
    for (let i = 0; i < 24; i++) {
        ctx.fillStyle = 'rgba(255,255,255,0.7)';
        ctx.fillRect(Math.floor(rand() * w), 4 + Math.floor(rand() * 5), 1 + Math.floor(rand() * 3), 1);
    }
    tex.refresh();
}

// The bow wave: white water heaped against the stem, highest there and sloping forward down to
// the sea, spilling a little under the waterline, spray over it; a few frames. `BOW_UNDER` px of it
// lie under the waterline. Aft of the stem it falls away along the ship's side and breaks up into
// the foam there (the user, 2026-11-14: it stopped at its highest, a straight edge, "cut off"):
// `BOW_FORE` px of the frame lie forward of its peak, `BOW_TAIL` aft.
const BOW_UNDER = 9, BOW_FORE = 96, BOW_TAIL = 80;
function bowWaveTextures(scene) {
    const w = BOW_FORE + BOW_TAIL, h = 44, frames = 4, peak = 30;
    const tex = scene.textures.createCanvas('sea-bow', w * frames, h);
    const ctx = tex.getContext();
    const water = h - BOW_UNDER;                         // the waterline's row in the frame
    for (let f = 0; f < frames; f++) {
        const rand = rng(31 + f);
        const ox = f * w;
        for (let x = 0; x < w; x++) {
            const aft = x >= BOW_FORE;
            const s = aft ? (x - BOW_FORE) / (BOW_TAIL - 1) : 0;     // aft of the stem: 0 at it, 1 where it has run out
            const t = aft ? (1 - s) ** 1.7 : x / (BOW_FORE - 1);     // its height: 0 ahead, 1 at the stem, 0 again aft
            const top = Math.round(water - 2 - peak * (aft ? t : t ** 2.2) - Math.sin((x + f * 6) / 4) * (0.5 + t));
            const bottom = Math.round(water + 1 + (BOW_UNDER - 2) * (aft ? (1 - s) ** 1.2 : t ** 1.5) + rand() * 2);
            for (let y = top; y < Math.min(h, bottom); y++) {
                const under = y >= water;                // churned water under the line
                if (!aft && t < 0.25 && rand() < 0.5 - t) continue;       // the leading edge breaking up
                if (aft && s > 0.55 && rand() < (s - 0.55) * 1.6) continue;   // and the tail, into the foam along the side
                if (under && rand() < 0.3) continue;
                const u = rand();
                ctx.fillStyle = under ? (u < 0.5 ? '#c7f0ff' : '#8fd3ff') : (u < 0.82 ? '#ffffff' : '#c7f0ff');
                ctx.fillRect(ox + x, y, 1, 1);
            }
            for (let k = 0; k < 3; k++) {                // spray thrown up and forward
                if (rand() < 0.4 * t) {
                    ctx.fillStyle = rand() < 0.6 ? '#ffffff' : 'rgba(255,255,255,0.6)';
                    ctx.fillRect(ox + x - Math.floor(rand() * 4), top - 1 - Math.floor(rand() * 7 * t), 1, 1);
                }
            }
        }
        tex.add(f, 0, ox, 0, w, h);
    }
    tex.refresh();
}

// The wake: streaks of foam streaming aft from the stern on the top rows of waves (on the surface
// at the ship's distance), white near the stern, paler and fewer aft as the trail widens. Drawn
// anew as they move, into a canvas `WAKE_W` x `WAKE_H`; `WAKE_ABOVE` px of it lie over the waterline.
const WAKE_W = 1000, WAKE_H = 40, WAKE_ABOVE = 4;
const WAKE_COLOURS = ['#ffffff', '#ffffff', '#e3f4fb', '#c7f0ff', '#8fd3ff'];

class Wake {
    constructor(scene, x, y, depth) {
        const key = 'sea-wake';
        if (scene.textures.exists(key)) scene.textures.remove(key);
        this.tex = scene.textures.createCanvas(key, WAKE_W, WAKE_H);
        this.ctx = this.tex.getContext();
        this.img = scene.add.image(x, y - WAKE_ABOVE, key).setOrigin(0).setDepth(depth);
        this.rand = rng(53);
        this.streaks = Array.from({ length: 420 }, () => this.spawn(WAKE_W * this.rand() ** 1.5));
        this.wait = 0;
    }

    // A streak at `x` aft of the stern: how far out from the trail's middle it lies (most near
    // it), its length, how fast it drifts, how far it lasts before it melts.
    spawn(x = this.rand() * 12) {
        const r = this.rand;
        return { x, side: r() ** 1.6, len: 3 + r() * 14, speed: 50 + r() * 30, life: r() };
    }

    update(dt) {
        for (let i = 0; i < this.streaks.length; i++) {
            const k = this.streaks[i];
            k.x += k.speed * dt;
            if (k.x / WAKE_W > k.life ** 0.6 || k.x > WAKE_W) this.streaks[i] = this.spawn();
        }
        this.wait -= dt;
        if (this.wait > 0) return;
        this.wait = 1 / 15;
        const ctx = this.ctx;
        ctx.clearRect(0, 0, WAKE_W, WAKE_H);
        for (const k of this.streaks) {
            const t = k.x / WAKE_W;                     // 0 at the stern, 1 at the trail's end
            const spread = 3 + 30 * t ** 0.8;           // the trail widening aft
            const y = WAKE_ABOVE + 1 + Math.round(k.side * spread);
            const len = Math.max(1, Math.round(k.len * (1 - 0.6 * t)));
            const c = Math.min(WAKE_COLOURS.length - 1, Math.floor((t * 0.8 + k.side * 0.5) * WAKE_COLOURS.length));
            ctx.fillStyle = WAKE_COLOURS[c];
            ctx.fillRect(Math.round(k.x), y, len, 1);
            if (t < 0.06 && k.side < 0.3) {             // the boil just behind the stern
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(Math.round(k.x), y - 1 - Math.floor(k.life * WAKE_ABOVE * (1 - t / 0.06)), Math.max(1, len >> 1), 1);
            }
        }
        this.tex.refresh();
    }
}

// The foam along the waterline carried on aft of the stern for `TAIL_W` px, the same pattern moving
// with it, fewer of its pixels kept the further aft, so it melts into the wake. Each pixel's fate
// is fixed by its place in the pattern, so the foam breaks up without flickering as it moves.
const TAIL_W = 112;

class FoamTail {
    constructor(scene, foam, x, y, depth) {
        const key = 'sea-foam-tail';
        if (scene.textures.exists(key)) scene.textures.remove(key);
        const src = scene.textures.get('sea-foam').getSourceImage();
        this.srcW = src.width;
        this.srcH = src.height;
        this.pixels = src.getContext('2d').getImageData(0, 0, src.width, src.height).data;
        this.tex = scene.textures.createCanvas(key, TAIL_W, this.srcH);
        this.ctx = this.tex.getContext();
        this.img = scene.add.image(x, y, key).setOrigin(0).setDepth(depth);
        this.foam = foam;
        this.offset = x - foam.x;              // the tail's first column along the foam's pattern
        this.last = null;
    }

    update() {
        const shift = Math.round(this.offset + this.foam.tilePositionX);
        if (shift === this.last) return;
        this.last = shift;
        const { ctx, pixels, srcW, srcH } = this;
        ctx.clearRect(0, 0, TAIL_W, srcH);
        for (let x = 0; x < TAIL_W; x++) {
            const sx = ((shift + x) % srcW + srcW) % srcW;
            const keep = (1 - x / TAIL_W) ** 1.4;
            for (let y = 0; y < srcH; y++) {
                const i = (y * srcW + sx) * 4;
                if (!pixels[i + 3]) continue;
                // A fixed random number per pixel of the pattern, and a little more loss low down.
                const h = (Math.imul(sx * 73 + y * 151, 2654435761) >>> 0) / 4294967296;
                if (h > keep * (1 - y / (srcH * 2))) continue;
                ctx.fillStyle = `rgba(${pixels[i]},${pixels[i + 1]},${pixels[i + 2]},${pixels[i + 3] / 255})`;
                ctx.fillRect(x, y, 1, 1);
            }
        }
        this.tex.refresh();
    }
}

export function makeSeaTextures(scene) {
    if (scene.textures.exists('sea-band-0')) return;
    BANDS.forEach(([h, crest, water, trough, , len], i) => bandTexture(scene, `sea-band-${i}`, h, [crest, water, trough], len, 11 + i));
    // (The same waves in the sunset's colours: the same seed, so each crest keeps its place.)
    BANDS.forEach(([h, , , , , len], i) => bandTexture(scene, `sea-dusk-${i}`, h, DUSK_BANDS[i].map(dusk), len, 11 + i, dusk('#fff6cf')));
    for (const [key, colours] of [['sea-deep', DEEP], ['sea-deep-dusk', DUSK_DEEP.map(dusk)]]) {
        const deep = scene.textures.createCanvas(key, 4, 256);
        const ctx = deep.getContext();
        const grad = ctx.createLinearGradient(0, 0, 0, 256);
        colours.forEach((c, i) => grad.addColorStop(i / (colours.length - 1), c));
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 4, 256);
        deep.refresh();
    }
    foamTexture(scene);
    bowWaveTextures(scene);
}

// The sea in the world: rows from the waterline `y` over [x0, x1], the deep water under them to
// `bottom`; the foam along the hull from `bowX` to `sternX`, the bow wave at `bowX`, the wake from
// `sternX`. `depth` is the sea's own depth, in front of the hull (its foot is under water); `front`
// the depth of the foam over the waterline.
export class Sea {
    constructor(scene, { x0, x1, y, bottom, bowX, sternX, depth, front }) {
        makeSeaTextures(scene);
        this.scene = scene;
        this.rows = [];
        let top = y;
        const w = x1 - x0;
        BANDS.forEach(([h, , , , speed, , bob], i) => {
            // Each row reaches a little under the next, so its rising and falling leaves no gap.
            const s = scene.add.tileSprite(x0, top, w, h + 3, `sea-band-${i}`).setOrigin(0).setDepth(depth + i * 0.001);
            const d = scene.add.tileSprite(x0, top, w, h + 3, `sea-dusk-${i}`).setOrigin(0).setDepth(depth + i * 0.001 + 0.0005);
            this.rows.push({ s, d, top, speed, bob, phase: i * 1.3 });
            top += h;
        });
        this.deep = scene.add.image(x0, top, 'sea-deep').setOrigin(0).setDisplaySize(w, Math.max(1, bottom - top)).setDepth(depth - 0.001);
        this.deepDusk = scene.add.image(x0, top, 'sea-deep-dusk').setOrigin(0).setDisplaySize(w, Math.max(1, bottom - top)).setDepth(depth - 0.0005);
        // Foam along the waterline, from the stem to the stern.
        this.foam = scene.add.tileSprite(bowX, y - 2, sternX - bowX, 10, 'sea-foam').setOrigin(0).setDepth(front);
        // The bow wave against the stem.
        this.bow = scene.add.sprite(bowX + 10, y + BOW_UNDER, 'sea-bow', 0)
            .setOrigin(BOW_FORE / (BOW_FORE + BOW_TAIL), 1).setDepth(front + 0.001);
        // The wake: churned white water trailing aft from the stern.
        this.wake = new Wake(scene, sternX - 4, y, front - 0.001);
        // The foam runs on past the stern, breaking up into the wake (the user, 2026-11-07: it was
        // cut off square at the stern).
        this.tail = new FoamTail(scene, this.foam, sternX, y - 2, front);
        this.time = 0;
        this.objects = [...this.rows.flatMap(r => [r.s, r.d]), this.deep, this.deepDusk, this.foam, this.bow, this.wake.img, this.tail.img];
        this.setDusk(0);
    }

    // The sunset coming on (0 the day, 1 the full sunset): its rows over the day's, the foam warmer.
    setDusk(k) {
        this.dusk = k;
        for (const r of this.rows) r.d.setAlpha(k).setVisible(k > 0);
        this.deepDusk.setAlpha(k).setVisible(k > 0);
        const [r, g, b] = DUSK_FOAM.map(v => Math.round(255 + (v - 255) * k));
        for (const o of [this.foam, this.bow, this.wake.img, this.tail.img]) o.setTint((r << 16) | (g << 8) | b);
    }

    update(dt) {
        this.time += dt;
        for (const r of this.rows) {
            r.s.tilePositionX -= r.speed * dt;
            r.s.y = Math.round(r.top + Math.sin(this.time * 1.4 + r.phase) * r.bob);
            if (this.dusk > 0) {
                r.d.tilePositionX = r.s.tilePositionX;
                r.d.y = r.s.y;
            }
        }
        this.foam.tilePositionX -= 70 * dt;
        this.tail.update();
        this.wake.update(dt);
        this.bow.setFrame(Math.floor(this.time * 7) % 4);
    }
}
