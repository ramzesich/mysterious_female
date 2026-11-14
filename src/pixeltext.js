// Words set in the game's own pixel lettering (the welcome screen's menu: src/intro.js). The
// letters' shapes are in the `menu` atlas (tools/build_menu.py: two generated letterings, `T` the
// name's, 24 px high, and `S` the signs', 12 px, with the Ukrainian capitals built from the Latin
// ones); here they get their look: filled in bands of colour from the top down, an outline round
// them, a shadow under. The picture is drawn once into a texture; show it at twice its size, as a
// pixel of the game's is two of the screen's.

const INK = '#2e222f';

// The letters of `text` the lettering `font` has no shape for (the menu is in capitals).
export function missing(scene, font, text) {
    const tex = scene.textures.get('menu');
    return [...text.toUpperCase()].filter(ch => ch !== ' ' && !tex.has(`${font}-${ch.codePointAt(0).toString(16).padStart(4, '0')}`));
}

// `bands`: the fill's colours from the top down, each as high as the others; `outline` and how
// thick it is; `shadow`: how far under (0: none). Makes (or makes again) the texture `key` and
// returns it.
export function pixelText(scene, key, font, text, { bands = ['#ffffff'], outline = '#323353', thick = 1, shadow = 1 } = {}) {
    const tex = scene.textures.get('menu');
    const glyphs = [];
    const cell = tex.get(`${font}-0048`).height;        // (every letter of a lettering is as high as its H's cell)
    let w = 0;
    for (const ch of text.toUpperCase()) {
        const name = `${font}-${ch.codePointAt(0).toString(16).padStart(4, '0')}`;
        if (ch === ' ' || !tex.has(name)) {
            w += ch === ' ' ? Math.round(cell / 3) : 0;
            continue;
        }
        const f = tex.get(name);
        glyphs.push({ f, x: w });
        w += f.width + Math.max(1, cell >> 4);
    }
    w = Math.max(1, w - Math.max(1, cell >> 4));
    const pad = thick + shadow + 1, W = w + 2 * pad, H = cell + 2 * pad;
    const layer = () => {
        const c = document.createElement('canvas');
        c.width = W;
        c.height = H;
        const ctx = c.getContext('2d');
        ctx.imageSmoothingEnabled = false;
        return [c, ctx];
    };
    // The letters as they are, white.
    const [mask, m] = layer();
    for (const { f, x } of glyphs) m.drawImage(f.source.image, f.cutX, f.cutY, f.width, f.height, pad + x, pad, f.width, f.height);
    // Grown by the outline's thickness all round, in one colour: the outline, and its shadow.
    const grown = colour => {
        const [c, ctx] = layer();
        for (let dy = -thick; dy <= thick; dy++) for (let dx = -thick; dx <= thick; dx++) ctx.drawImage(mask, dx, dy);
        ctx.globalCompositeOperation = 'source-in';
        ctx.fillStyle = colour;
        ctx.fillRect(0, 0, W, H);
        return c;
    };
    // The fill: bands over the letters' own height.
    const [fill, f] = layer();
    f.drawImage(mask, 0, 0);
    f.globalCompositeOperation = 'source-atop';         // (each band only where the letters are, the rest kept)
    const top = pad + Math.round(cell * 0.12), high = Math.round(cell * 0.76);
    bands.forEach((c, i) => {
        f.fillStyle = c;
        const y = i ? top + Math.round(high * i / bands.length) : 0;
        f.fillRect(0, y, W, H - y);
    });
    if (scene.textures.exists(key)) scene.textures.remove(key);
    const out = scene.textures.createCanvas(key, W, H);
    const ctx = out.getContext();
    ctx.imageSmoothingEnabled = false;
    if (shadow) ctx.drawImage(grown(INK), 0, shadow + 1);
    if (thick) ctx.drawImage(grown(outline), 0, 0);
    ctx.drawImage(fill, 0, 0);
    out.refresh();
    return key;
}
