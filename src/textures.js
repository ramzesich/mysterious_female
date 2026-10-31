// Placeholder sprites, drawn from text pixel maps at boot. They exist so the ship is playable and
// tunable before the real pixel art is made (§2.1); swap them out, don't polish them.

const PALETTE = {
    k: '#2a1f1d', // hair
    s: '#f3cfb6', // skin
    e: '#f2c14e', // earring, epaulettes, gold
    w: '#ffffff', // blouse
    g: '#d9dee5', // blouse shading
    r: '#c8343f', // neck scarf
    n: '#1d2b53', // skirt
    b: '#14161c', // shoes
    o: '#f28c28', // tangerine
    O: '#d9711a',
    l: '#4c9a2a', // leaf
    c: '#9a6a3a', // crate
    C: '#7a5028',
    d: '#5b6470', // dark grey
    m: '#9aa3ad', // mid grey
    p: '#c9ced3', // pale grey
    u: '#2f9bd6', // blue light
    R: '#e04848', // life ring red
    W: '#f4f4f4',
    y: '#3fbf5f', // green light
    G: '#b8f5c4', // green light highlight
    Y: '#ffd98a', // warm cabin light
    L: '#fff1c9',
    t: '#b9ad97', // background furniture, muted
    T: '#a39780',
};

// Bumbusik, facing right, 16x48. The frames share everything above the hem.
const HER_TOP = [
    '......kkkk......',
    '....kkkkkkkk....',
    '...kkkkkkkkkk...',
    '..kkkkkkkkkkkk..',
    '..kkkkkkkkssss..',
    '..kkkkkksssssk..',
    '..kkkkksssksss..',
    '..kkkkksssssss..',
    '..kkkkksssssss..',
    '..kkkkesssssss..',
    '..kkkkkssssss...',
    '..kkkkkksssss...',
    '..kkkkkkkssss...',
    '..kkkkk..sss....',
    '.kkkkkk..sss....',
    '.kkkkkgrrrrrg...',
    '.kk.ewwwwwwwe...',
    'k...wwwwwwwgw...',
    '...wwwwwwwwgww..',
    '...wwwwwwwwgww..',
    '...swwwwwwwgws..',
    '...swwwwwwwgws..',
    '...swwwwwwwgws..',
    '...swwwwwwwgws..',
    '...swwwwwwwgws..',
    '...snnnnnnnnns..',
    '...snnnnnnnnns..',
    '....nnnnnnnnn...',
    '....nnnnnnnnn...',
    '....nnnnnnnnn...',
    '...nnnnnnnnnnn..',
    '...nnnnnnnnnnn..',
    '...nnnnnnnnnnn..',
    '...nnnnnnnnnnn..',
];

const BLANK = '................';
const LEGS = {
    stand: [
        ...Array(12).fill('.....ss..ss.....'),
        '....bbb..bbb....', '....bbb..bbbb...',
    ],
    run1: [
        '....ss....ss....', '....ss....ss....', '...ss......ss...', '...ss......ss...',
        '..ss........ss..', '..ss........ss..', '..ss.........ss.', '.ss..........ss.',
        '.ss..........ss.', '.ss...........ss', '.bb...........bb', 'bbb...........bb',
        BLANK, BLANK,
    ],
    run2: [
        '......ss.ss.....', '......ss.ss.....', '......sssss.....', '.......sss......',
        '.......ss.......', '.......ss.......', '.......ss.......', '.......ss.......',
        '.......sss......', '.......sss......', '.......bbb......', '.......bbbb.....',
        BLANK, BLANK,
    ],
    jump: [
        '.....ss..ss.....', '.....ss...ss....', '....ss.....ss...', '....ss.....ss...',
        '....ss.....ss...', '....bbb....bbb..', '....bbb....bbb..',
        ...Array(7).fill(BLANK),
    ],
};

// Climbing, seen from behind: hair down her back, arms up on the rungs.
const HER_CLIMB = [
    '......kkkk......',
    's...kkkkkkkk...s',
    's..kkkkkkkkkk..s',
    ...Array(10).fill('s.kkkkkkkkkkkk.s'),
    'w.kkkkkkkkkkkk.w',
    'w.ekkkkkkkkkke.w',
    'w.kkkkkkkkkkkk.w',
    'wkkkkkkkkkkkkkkw',
    'wkwkkkkkkkkkkwkw',
    '..wewwwwwwwwew..',
    ...Array(6).fill('...wwwwwwwwww...'),
    ...Array(5).fill('...nnnnnnnnnn...'),
    ...Array(4).fill('..nnnnnnnnnnnn..'),
    ...Array(12).fill('.....ss..ss.....'),
    '.....bb..bb.....', '.....bb..bb.....',
];

const SPRITES = {
    tangerine: [
        '....ll..',
        '...lll..',
        '..oooo..',
        '.oooooo.',
        '.oooooO.',
        '.ooooOO.',
        '..oOOO..',
        '........',
    ],
    crate: [
        'CCCCCCCCCCCCCCCC',
        'CccccccccccccccC',
        'CcCccccccccccCcC',
        'CccCccccccccCccC',
        'CcccCccccccCcccC',
        'CccccCccccCccccC',
        'CcccccCccCcccccC',
        'CccccccCCccccccC',
        'CccccccCCccccccC',
        'CcccccCccCcccccC',
        'CccccCccccCccccC',
        'CcccCccccccCcccC',
        'CccCccccccccCccC',
        'CcCccccccccccCcC',
        'CccccccccccccccC',
        'CCCCCCCCCCCCCCCC',
    ],
    vacuum: [
        '.....dddddd.....',
        '...ddmmmmmmdd...',
        '..dmmmmuummmmd..',
        '.dmmmmmmmmmmmmd.',
        'dddddddddddddddd',
        '.d............d.',
    ],
    // A small side table, background furniture (muted, so it never reads as something to stand on).
    sidetable: [
        'TTTTTTTTTTTTTTTTTTTT',
        'tttttttttttttttttttt',
        'tttttttttttttttttttt',
        ...Array(14).fill('..t..............t..'),
        '..T..............T..',
    ],
};

// Crew cabin door, 24x60: sized to her, like every human-scale thing on board (§2.1). Closed until
// she passes it; activated, it stands ajar with warm light spilling out of the cabin, so an active
// checkpoint reads from across the deck (§5.5).
function doorRows(open) {
    const rows = [];
    for (let y = 0; y < 60; y++) {
        let row = '';
        for (let x = 0; x < 24; x++) {
            const frame = x <= 1 || x >= 22 || y <= 1;
            if (frame) row += 'd';
            else if (open && x <= 8) row += x >= 7 ? 'L' : 'Y';                                                             // lit gap
            else if (y >= 9 && y <= 13 && x >= 11 && x <= 19) row += y === 9 || y === 13 || x === 11 || x === 19 ? 'm' : 'W'; // number plate
            else if (y >= 30 && y <= 31 && x >= (open ? 11 : 16) && x <= (open ? 13 : 19)) row += 'd';                     // handle
            else row += open && x === 9 ? 'm' : 'p';                                                                         // door edge
        }
        rows.push(row);
    }
    return rows;
}

const LAMP = {
    off: ['.dddddd.', 'dmmmmmmd', 'dmmmmmmd', '.dddddd.'],
    on: ['.dddddd.', 'dGyyyyGd', 'dyyyyyyd', '.dddddd.'],
};

function paint(ctx, rows, ox = 0, oy = 0) {
    rows.forEach((row, y) => {
        [...row].forEach((ch, x) => {
            if (ch === '.' || !PALETTE[ch]) return;
            ctx.fillStyle = PALETTE[ch];
            ctx.fillRect(ox + x, oy + y, 1, 1);
        });
    });
}

function makeSingle(scene, key, rows) {
    const tex = scene.textures.createCanvas(key, rows[0].length, rows.length);
    paint(tex.getContext(), rows);
    tex.refresh();
}

export function makeTextures(scene) {
    // Bumbusik: one strip, five 16x48 frames.
    const frames = ['stand', 'run1', 'run2', 'jump', 'climb'];
    const her = scene.textures.createCanvas('her', 16 * frames.length, 48);
    const ctx = her.getContext();
    frames.forEach((name, i) => {
        const rows = name === 'climb' ? HER_CLIMB : [...HER_TOP, ...LEGS[name]];
        paint(ctx, rows, i * 16, 0);
        her.add(name, 0, i * 16, 0, 16, 48);
    });
    her.refresh();

    for (const [key, rows] of Object.entries(SPRITES)) makeSingle(scene, key, rows);
    makeSingle(scene, 'door', doorRows(false));
    makeSingle(scene, 'door-on', doorRows(true));
    makeSingle(scene, 'lamp', LAMP.off);
    makeSingle(scene, 'lamp-on', LAMP.on);

    // Life ring, 20x20 (about 75 cm across, at her scale): red and white quarters.
    const ring = scene.textures.createCanvas('lifering', 20, 20);
    const rctx = ring.getContext();
    rctx.lineWidth = 5;
    for (let q = 0; q < 4; q++) {
        rctx.strokeStyle = q % 2 ? '#f4f4f4' : '#e04848';
        rctx.beginPath();
        rctx.arc(10, 10, 7, (q * Math.PI) / 2, ((q + 1) * Math.PI) / 2);
        rctx.stroke();
    }
    ring.refresh();

    // Soft round glow, used behind the lit checkpoint lamp.
    const glow = scene.textures.createCanvas('glow', 32, 32);
    const gctx = glow.getContext();
    const rad = gctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    rad.addColorStop(0, 'rgba(120, 255, 150, 0.9)');
    rad.addColorStop(1, 'rgba(120, 255, 150, 0)');
    gctx.fillStyle = rad;
    gctx.fillRect(0, 0, 32, 32);
    glow.refresh();

    // Sky: a vertical gradient strip, stretched across the world.
    const sky = scene.textures.createCanvas('sky', 4, 256);
    const sctx = sky.getContext();
    const grad = sctx.createLinearGradient(0, 0, 0, 256);
    grad.addColorStop(0, '#5fb8f0');
    grad.addColorStop(1, '#cdeeff');
    sctx.fillStyle = grad;
    sctx.fillRect(0, 0, 4, 256);
    sky.refresh();

    // Sea: a tile of small waves, scrolled to show the ship under way.
    const sea = scene.textures.createCanvas('sea', 32, 32);
    const wctx = sea.getContext();
    wctx.fillStyle = '#2a7fbf';
    wctx.fillRect(0, 0, 32, 32);
    wctx.fillStyle = '#3f95d1';
    wctx.fillRect(0, 0, 32, 3);
    wctx.fillStyle = '#7cc3ee';
    for (const [x, y, w] of [[2, 0, 6], [18, 1, 5], [10, 9, 4], [25, 14, 5], [4, 21, 3], [16, 27, 4]]) {
        wctx.fillRect(x, y, w, 1);
    }
    sea.refresh();

    // Small white square for particles.
    const dot = scene.textures.createCanvas('dot', 2, 2);
    dot.getContext().fillStyle = '#ffffff';
    dot.getContext().fillRect(0, 0, 2, 2);
    dot.refresh();
}
