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

// Crew cabin door, 16x32, closed. The light above the handle turns green once activated.
function doorRows(light) {
    const rows = [];
    for (let y = 0; y < 32; y++) {
        let row = '';
        for (let x = 0; x < 16; x++) {
            const frame = x === 0 || x === 15 || y === 0;
            if (frame) row += 'd';
            else if (y >= 5 && y <= 8 && x >= 4 && x <= 11) row += y === 5 || y === 8 || x === 4 || x === 11 ? 'm' : 'W'; // number plate
            else if (y >= 16 && y <= 17 && x >= 11 && x <= 13) row += 'd';                                               // handle
            else if (y === 13 && x >= 11 && x <= 12) row += light;                                                        // card reader light
            else row += 'p';
        }
        rows.push(row);
    }
    return rows;
}

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
    makeSingle(scene, 'door', doorRows('R'));
    makeSingle(scene, 'door-on', doorRows('y'));

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
