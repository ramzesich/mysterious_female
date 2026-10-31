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

// Bumbusik, facing right, 12x32. The frames share everything above the hem.
const HER_TOP = [
    '....kkkk....',
    '...kkkkkk...',
    '..kkkkkkkk..',
    '..kkksssss..',
    '..kkssksks..',
    '..kkssssss..',
    '..kkesssss..',
    '..kkkssss...',
    '.kkkk.ss....',
    'k.kkgrrrg...',
    '..ewwwwwwe..',
    '..wwwwwwww..',
    '..wwwwwwgw..',
    '.swwwwwwgws.',
    '.swwwwwwgws.',
    '.swwwwwwgws.',
    '.snnnnnnnns.',
    '..nnnnnnnn..',
    '..nnnnnnnn..',
    '..nnnnnnnn..',
    '..nnnnnnnn..',
    '.nnnnnnnnnn.',
    '.nnnnnnnnnn.',
];

const LEGS = {
    stand: [
        '...ss..ss...', '...ss..ss...', '...ss..ss...', '...ss..ss...',
        '...ss..ss...', '...ss..ss...', '...ss..ss...', '...bb..bbb..', '...bbb.bbb..',
    ],
    run1: [
        '...ss...ss..', '..ss....ss..', '..ss.....ss.', '.ss......ss.',
        '.ss.......ss', '.ss.......ss', 'bb........bb', 'bbb.......bb', '............',
    ],
    run2: [
        '....ss.ss...', '....ss.ss...', '....sss.....', '.....ss.....',
        '.....ss.....', '.....sss....', '.....bbb....', '.....bbbb...', '............',
    ],
    jump: [
        '...ss..ss...', '...ss...ss..', '..ss.....ss.', '..ss.....ss.',
        '..bb.....bb.', '..bbb....bbb', '............', '............', '............',
    ],
};

// Climbing, seen from behind: hair down her back, arms up on the rungs.
const HER_CLIMB = [
    's...kkkk...s',
    's..kkkkkk..s',
    's.kkkkkkkk.s',
    's.kkkkkkkk.s',
    's.kkkkkkkk.s',
    's.kkkkkkkk.s',
    'w.ekkkkkke.w',
    'w.kkkkkkkk.w',
    'wkkkkkkkkkkw',
    'wkwkkkkkkwkw',
    '.wewwwwwwew.',
    '..wwwwwwww..',
    '..wwwwwwww..',
    '..wwwwwwww..',
    '..wwwwwwww..',
    '..wwwwwwww..',
    '..nnnnnnnn..',
    '..nnnnnnnn..',
    '..nnnnnnnn..',
    '..nnnnnnnn..',
    '..nnnnnnnn..',
    '.nnnnnnnnnn.',
    '.nnnnnnnnnn.',
    '...ss..ss...', '...ss..ss...', '...ss..ss...', '...ss..ss...',
    '...ss..ss...', '...ss..ss...', '...ss..ss...', '...bb..bb...', '...bb..bb...',
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
        'TTTTTTTTTTTTTT',
        'tttttttttttttt',
        '.T..........T.',
        '.t..........t.',
        '.t..........t.',
        '.t..........t.',
        '.t..........t.',
        '.t..........t.',
        '.T..........T.',
    ],
    lifering: [
        '....RRRRRR....',
        '..RRWWWWWWRR..',
        '.RWWW....WWWR.',
        '.RW........WR.',
        'RW..........WR',
        'RW..........WR',
        'RR..........RR',
        '.RR........RR.',
        '.RRRW....WRRR.',
        '..RRRWWWWRRR..',
        '....RRRRRR....',
    ],
};

// Crew cabin door, 16x32. Closed until she passes it; activated, it stands ajar with warm light
// spilling out of the cabin, so an active checkpoint reads from across the deck (§5.5).
function doorRows(open) {
    const rows = [];
    for (let y = 0; y < 32; y++) {
        let row = '';
        for (let x = 0; x < 16; x++) {
            const frame = x === 0 || x === 15 || y === 0;
            if (frame) row += 'd';
            else if (open && x <= 5) row += x >= 4 ? 'L' : 'Y';                                                          // lit gap
            else if (y >= 5 && y <= 8 && x >= 7 && x <= 12) row += y === 5 || y === 8 || x === 7 || x === 12 ? 'm' : 'W'; // number plate
            else if (y >= 16 && y <= 17 && x >= (open ? 7 : 11) && x <= (open ? 8 : 13)) row += 'd';                     // handle
            else row += open && x === 6 ? 'm' : 'p';                                                                       // door edge
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
    // Bumbusik: one strip, five 12x32 frames.
    const frames = ['stand', 'run1', 'run2', 'jump', 'climb'];
    const her = scene.textures.createCanvas('her', 12 * frames.length, 32);
    const ctx = her.getContext();
    frames.forEach((name, i) => {
        const rows = name === 'climb' ? HER_CLIMB : [...HER_TOP, ...LEGS[name]];
        paint(ctx, rows, i * 12, 0);
        her.add(name, 0, i * 12, 0, 12, 32);
    });
    her.refresh();

    for (const [key, rows] of Object.entries(SPRITES)) makeSingle(scene, key, rows);
    makeSingle(scene, 'door', doorRows(false));
    makeSingle(scene, 'door-on', doorRows(true));
    makeSingle(scene, 'lamp', LAMP.off);
    makeSingle(scene, 'lamp-on', LAMP.on);

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
