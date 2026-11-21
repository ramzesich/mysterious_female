// The ship's signs, drawn as pixel art at their own size (the user, 2026-11-21: the plain white text
// boxes made over, sign by sign, each kept to its place and about its old size): the crew doors' plates,
// the cards on the rope barriers, the notices and plaques on the walls. Each is one picture, made once
// per text and look into a texture of its own (`sign:<look>:<text>`), in a 5 px pixel font drawn here
// (capitals, a px between letters), on a plate drawn by rule: a 1 px rim, a face, a lit top edge or a
// band where the look has one. Flat by nature, so drawn in code (CLAUDE.md, "Art").
//
// `sign(scene, x, y, text, look)` returns an Image, placed and layered like the text it stands for (its
// origin, depth and visibility are the caller's); `signText` says what it reads (tools/check_overlaps.py).
// The ship's own signs stay in English in both languages (src/lang.js).

const GLYPHS = {
    A: '.#.|#.#|###|#.#|#.#', B: '##.|#.#|##.|#.#|##.', C: '.##|#..|#..|#..|.##', D: '##.|#.#|#.#|#.#|##.',
    E: '###|#..|##.|#..|###', F: '###|#..|##.|#..|#..', G: '.##|#..|#.#|#.#|.##', H: '#.#|#.#|###|#.#|#.#',
    I: '###|.#.|.#.|.#.|###', J: '..#|..#|..#|#.#|.#.', K: '#.#|#.#|##.|#.#|#.#', L: '#..|#..|#..|#..|###',
    M: '#...#|##.##|#.#.#|#...#|#...#', N: '#..#|##.#|#.##|#..#|#..#', O: '.#.|#.#|#.#|#.#|.#.',
    P: '##.|#.#|##.|#..|#..', Q: '.#.|#.#|#.#|#.#|.##', R: '##.|#.#|##.|#.#|#.#', S: '.##|#..|.#.|..#|##.',
    T: '###|.#.|.#.|.#.|.#.', U: '#.#|#.#|#.#|#.#|###', V: '#.#|#.#|#.#|#.#|.#.', W: '#...#|#...#|#.#.#|##.##|#...#',
    X: '#.#|#.#|.#.|#.#|#.#', Y: '#.#|#.#|.#.|.#.|.#.', Z: '###|..#|.#.|#..|###',
    0: '###|#.#|#.#|#.#|###', 1: '.#.|##.|.#.|.#.|###', 2: '##.|..#|.#.|#..|###', 3: '##.|..#|.#.|..#|##.',
    4: '#.#|#.#|###|..#|..#', 5: '###|#..|##.|..#|##.', 6: '.##|#..|###|#.#|###', 7: '###|..#|.#.|.#.|.#.',
    8: '###|#.#|###|#.#|###', 9: '###|#.#|###|..#|##.',
    ':': '.|#|.|#|.', '.': '.|.|.|.|#', ',': '.|.|.|#|#', '!': '#|#|#|.|#', "'": '#|#|.|.|.', '-': '..|..|##|..|..',
    '&': '.#..|#.#.|.#.#|#.#.|.#.#', '/': '..#|..#|.#.|#..|#..', '↑': '..#..|.###.|#.#.#|..#..|..#..', ' ': '..',
};
const CAP = 5;      // px of a capital
const LEAD = 1;     // px between lines

// The looks, as the user chose them from mock-ups at each place (2026-11-21).
export const SIGN_LOOKS = {
    steel: { face: '#c7dcd0', ink: '#2e222f', rim: '#625565', light: '#ffffff' },   // a crew door's plate
    navy: { face: '#323353', ink: '#ffffff', rim: '#7f708a' },                      // ...on a dark wall
    rope: { face: '#323353', ink: '#fbb954', rim: '#f9c22b', wrap: 40 },            // a rope barrier's card
    notice: { face: '#f9c22b', ink: '#2e222f', rim: '#4c3e24' },                    // a security notice
    bulletin: { face: '#ffffff', ink: '#ae2334', rim: '#9babb2', band: '#ae2334' }, // a white notice, red band
    plaque: { face: '#4d65b4', ink: '#ffffff', rim: '#323353', light: '#8fd3ff' },  // the promenade's plaques
    painted: { ink: '#4d65b4' },                                                    // words on the wall itself
    card: { face: '#fdcbb0', ink: '#45293f', rim: '#cd683d' },                      // a card on a door
};

const glyph = ch => (GLYPHS[ch] ?? GLYPHS[' ']).split('|');
const width = line => [...line].reduce((w, ch) => w + glyph(ch)[0].length + 1, 0) - 1;

// The lines a text is set in: its own line breaks; a line wider than `wrap` split in two at the space
// that leaves the wider half narrowest (REHEARSAL / IN PROGRESS).
function lines(text, wrap) {
    return text.toUpperCase().split('\n').flatMap(line => {
        if (!wrap || width(line) <= wrap) return [line];
        const words = line.split(' ');
        let best = [line];
        for (let i = 1; i < words.length; i++) {
            const two = [words.slice(0, i).join(' '), words.slice(i).join(' ')];
            if (best.length === 1 || Math.max(...two.map(width)) < Math.max(...best.map(width))) best = two;
        }
        return best;
    });
}

// The sign's pixels: [w, h, set(x, y, colour)] drawn into an ImageData.
function draw(text, look) {
    const L = SIGN_LOOKS[look], rows = lines(text, L.wrap);
    const tw = Math.max(1, ...rows.map(width)), th = rows.length * CAP + (rows.length - 1) * LEAD;
    const plate = !!L.face, band = L.band ? 2 : 0;
    const w = plate ? tw + 4 : tw, h = plate ? th + 4 + band : th;
    const px = [];
    const set = (x, y, c) => px.push([x, y, c]);
    if (plate) {
        for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
            set(x, y, x === 0 || y === 0 || x === w - 1 || y === h - 1 ? L.rim : L.face);
        }
        if (L.light) for (let x = 1; x < w - 1; x++) set(x, 1, L.light);
        if (band) for (let y = 1; y <= 2; y++) for (let x = 1; x < w - 1; x++) set(x, y, L.band);
    }
    const left = plate ? 2 : 0, top = plate ? 2 + band : 0;
    rows.forEach((row, n) => {
        let x = left + Math.floor((tw - width(row) + 1) / 2);
        for (const ch of row) {
            const g = glyph(ch);
            g.forEach((r, y) => [...r].forEach((p, i) => { if (p === '#') set(x + i, top + n * (CAP + LEAD) + y, L.ink); }));
            x += g[0].length + 1;
        }
    });
    return { w, h, px };
}

const rgb = c => [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)];

// A sign reading `text` in the look `look` (SIGN_LOOKS), its middle at (x, y) until the caller sets an origin.
export function sign(scene, x, y, text, look) {
    const key = `sign:${look}:${text}`;
    if (!scene.textures.exists(key)) {
        // (No words, no sign: a block with none hangs nothing on its rope.)
        const { w, h, px } = String(text ?? '').trim() ? draw(String(text), look) : { w: 1, h: 1, px: [] };
        const tex = scene.textures.createCanvas(key, w, h);
        const ctx = tex.getContext(), img = ctx.createImageData(w, h);
        for (const [px_, py, c] of px) {
            const i = (py * w + px_) * 4, [r, g, b] = rgb(c);
            img.data[i] = r; img.data[i + 1] = g; img.data[i + 2] = b; img.data[i + 3] = 255;
        }
        ctx.putImageData(img, 0, 0);
        tex.refresh();
    }
    const image = scene.add.image(x, y, key);
    image.signText = String(text ?? '');
    return image;
}
