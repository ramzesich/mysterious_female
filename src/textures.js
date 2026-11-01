// Placeholder sprites, drawn from text pixel maps at boot. They exist so the ship is playable and
// tunable before the real pixel art is made (§2.1); swap them out, don't polish them. Bumbusik
// herself is real art now: assets/sprites/her.png, built by tools/build_sprites.py.

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
    D: '#33373e', // inside an escape trunk
    M: '#6c737c',
    a: '#f28c28', // trunk arrow lamp, lit
    A: '#ffd98a',
};

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
        ...Array(18).fill('..t..............t..'),
        '..T..............T..',
    ],
};

// Crew cabin door, 28x74: sized to her, like every human-scale thing on board (§2.1). Closed until
// she passes it; activated, it stands ajar with warm light spilling out of the cabin, so an active
// checkpoint reads from across the deck (§5.5).
function doorRows(open) {
    const rows = [];
    for (let y = 0; y < 74; y++) {
        let row = '';
        for (let x = 0; x < 28; x++) {
            const frame = x <= 1 || x >= 26 || y <= 1;
            if (frame) row += 'd';
            else if (open && x <= 9) row += x >= 8 ? 'L' : 'Y';                                                             // lit gap
            else if (y >= 11 && y <= 16 && x >= 13 && x <= 22) row += y === 11 || y === 16 || x === 13 || x === 22 ? 'm' : 'W'; // number plate
            else if (y >= 37 && y <= 38 && x >= (open ? 12 : 19) && x <= (open ? 14 : 23)) row += 'd';                     // handle
            else row += open && x === 10 ? 'm' : 'p';                                                                         // door edge
        }
        rows.push(row);
    }
    return rows;
}

// An escape trunk's door, open (§5.1): the leaf swung out to one side, and the ladder in the dark
// shaft behind it. Closed, it is the plain crew door.
export const TRUNK_INSIDE = { x0: 5, x1: 26, y0: 2 }; // the doorway she shows through, door-local
function trunkOpenRows() {
    const rows = [];
    for (let y = 0; y < 74; y++) {
        let row = '';
        for (let x = 0; x < 28; x++) {
            if (x <= 1 || x >= 26 || y <= 1) row += 'd';                     // frame
            else if (x <= 4) row += x === 4 ? 'm' : 'p';                     // the leaf, edge-on
            else if (x === 8 || x === 23) row += 'M';                        // ladder rails
            else if (x > 8 && x < 23 && y % 9 === 5) row += 'm';             // rungs
            else row += 'D';
        }
        rows.push(row);
    }
    return rows;
}

// Arrow lamps above a trunk door, 9x7: amber when she can go that way, grey when she can't.
function arrowRows(up, lit) {
    const rows = [];
    for (let y = 0; y < 7; y++) {
        let row = '';
        for (let x = 0; x < 9; x++) {
            const corner = (x === 0 || x === 8) && (y === 0 || y === 6);
            const step = up ? y - 2 : 4 - y;                                  // 0 at the arrow's tip
            if (corner) row += '.';
            else if (x === 0 || x === 8 || y === 0 || y === 6) row += 'd';
            else if (step >= 0 && step <= 2 && Math.abs(x - 4) <= step) row += lit ? (step === 0 ? 'A' : 'a') : 'm';
            else row += 'D';
        }
        rows.push(row);
    }
    return rows;
}

// A card reader beside a locked door, 6x10; its light is tinted to the card's colour (§6.2).
const READER = ['dddddd', 'dppppd', 'dWWWWd', 'dWWWWd', 'dppppd', 'dpddpd', 'dppppd', 'dppppd', 'dppppd', 'dddddd'];

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
    for (const [key, rows] of Object.entries(SPRITES)) makeSingle(scene, key, rows);
    makeSingle(scene, 'door', doorRows(false));
    makeSingle(scene, 'door-on', doorRows(true));
    makeSingle(scene, 'lamp', LAMP.off);
    makeSingle(scene, 'lamp-on', LAMP.on);
    makeSingle(scene, 'trunk-open', trunkOpenRows());
    for (const up of [true, false]) {
        makeSingle(scene, `arrow-${up ? 'up' : 'down'}`, arrowRows(up, false));
        makeSingle(scene, `arrow-${up ? 'up' : 'down'}-on`, arrowRows(up, true));
    }
    makeSingle(scene, 'reader', READER);

    // Life ring, 24x24 (about 75 cm across, at her scale): red and white quarters.
    const ring = scene.textures.createCanvas('lifering', 24, 24);
    const rctx = ring.getContext();
    rctx.lineWidth = 6;
    for (let q = 0; q < 4; q++) {
        rctx.strokeStyle = q % 2 ? '#f4f4f4' : '#e04848';
        rctx.beginPath();
        rctx.arc(12, 12, 8, (q * Math.PI) / 2, ((q + 1) * Math.PI) / 2);
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
