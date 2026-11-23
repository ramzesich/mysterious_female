// The library's books (GAME_DESIGN.md §6.1.2, "her own thread"): fourteen of them are out on the ship (`BOOKS`).
// A book is a pocket item; the return trolley takes the ones she carries and the librarian shelves
// each into its gap on the shelf behind her desk, so the shelf shows how far the collection is. In any
// of the Library's armchairs or on her bed she chooses one of the books she carries and reads it: its
// first page shows (`read()`). Also here: the photo slots' and the pages' full-screen panel.

import { VIEW, BOOKS, PLAYER } from '../config.js';
import { t } from '../lang.js';
import { pixelText } from '../pixeltext.js';
import { writeSave } from '../save.js';
import { sfx } from '../sfx.js';

// Each book's colours, its small picture's and its spine's, from its cover (tools/build_covers.py, plan-the-rest §2.3):
// the cover's ground (its commonest colour but the outlines') and its title's colour, for the label.
export const BOOK_COLOURS = [0xf7f5ef, 0x009e3a, 0x004ca3, 0xe6edd2, 0x363b1e, 0x000815, 0xede9d0, 0x0a0c14, 0x878787,
    0xf6e7b6, 0x7cefff, 0xc72c02, 0x020207, 0x4ebefb];
export const BOOK_ACCENTS = [0xb09256, 0xe2f4e2, 0xfebe04, 0xb21c28, 0xf0f0e8, 0x60dead, 0xc41c24, 0x96c4de, 0xfafafa,
    0x1e1814, 0x7a1e22, 0x96d6ee, 0xd6a85c, 0xc92a0f];
// The stamp on a given-back book's small cover in the row: a green disc 11 px across with a white check mark in it
// (the user, 2026-11-22), at the cover's column 4 and row 10.
const STAMP = [
    '...GGGGG...',
    '.GGGGGGGGG.',
    '.GGGGGGGGG.',
    'GGGGGGGGWGG',
    'GGGGGGGWWGG',
    'GWWGGGWWGGG',
    'GGWWGWWGGGG',
    'GGGWWWGGGGG',
    '.GGGWGGGGG.',
    '.GGGGGGGGG.',
    '...GGGGG...',
];
const SLOT = 8;         // px per book on the shelf
const SPINE = 7;        // a spine's width there, its outline in
// The books back on the shelf are washed toward the wall as the Library's background is, so they do not read
// as things to pick up (the user, 2026-11-21); `tools/build_ship_art.py`'s `WALL` and its washes.
const SHELF_WASH = 0.12;
const washed = c => [16, 8, 0].reduce((v, sh) => {
    const a = (c >> sh) & 255, w = (0xe9dfcc >> sh) & 255;
    return v | (Math.round(a + (w - a) * SHELF_WASH) << sh);
}, 0);

export class Library {
    constructor(world) {
        this.world = world;
        this.scene = world.scene;
    }

    get save() { return this.scene.save; }

    held() {
        return Object.keys(this.save.books).filter(n => this.save.books[n] === 'held').map(Number);
    }

    returned() {
        return Object.keys(this.save.books).filter(n => this.save.books[n] === 'returned').map(Number);
    }

    build(data) {
        if (!data) return;
        const s = this.scene, D = s.DEPTH, w = this.world;
        this.data = data;
        // The shelf with a gap for each book, on the wall behind her desk: a board on the bookcases' tops.
        // (Its board runs over the two bookcases under it, from the first's left side to the second's
        // right, with no brackets under it: the user, 2026-11-21. The gaps are centred on it.)
        const { x0, x1, y } = data.shelf;
        // (The board itself is generated, the user's choice of two, 2026-11-22: `assets/sprites/book-shelf.png`, its
        // plain middle lengthened to the shelf's 125 px; the shadow behind the books and their gaps are drawn.)
        const g = s.add.graphics().setDepth(D.decor + 0.2);
        g.fillStyle(0x46291f, 0.35).fillRect(x0 + 2, y - 15, x1 - x0 - 4, 15);
        for (let n = 1; n <= BOOKS; n++) g.fillStyle(0x2e222f, 0.5).fillRect(this.slotX(n), y - 13, SPINE, 13);
        const board = s.add.image(x0, y, 'book-shelf').setOrigin(0).setDepth(D.decor + 0.2);
        this.shelfBooks = s.add.graphics().setDepth(D.decor + 0.21);
        w.add([g, board, this.shelfBooks]);
        // The return trolley by her desk, and the red reading chair by the window.
        this.textures();
        const trolley = s.add.image(data.trolley.x, data.trolley.y, 'book-trolley').setOrigin(0.5, 1).setDepth(D.props - 0.03);
        const chair = s.add.image(data.chair.x, data.chair.y, 'shipart', 'reading-chair').setOrigin(0.5, 1).setDepth(D.props - 0.03);
        const lamp = s.add.image(data.chair.x - 22, data.chair.y, 'shipart', 'floor-lamp').setOrigin(0.5, 1).setDepth(D.props - 0.04);
        w.add([trolley, chair, lamp]);
        w.things.push({ id: 'src_trolley', x: data.trolley.x, y: data.trolley.y, route: 'inside', items: [trolley], reach: 22,
            interact: () => this.giveBack() });
        // (Her clip in an armchair is 68 px square, the chair's foot on its bottom row, its middle at column 34.)
        (data.chairs ?? [data.chair]).forEach((c, i) => {
            const seat = { kind: 'chair', x: c.x, left: c.x - 34, top: c.y - 68 };
            w.things.push({ id: i ? `sec_chair_${i}` : 'sec_chair', x: c.x, y: c.y, route: 'inside', items: i ? [] : [chair, lamp], reach: 14,
                interact: () => this.read(seat) });
        });
        // The reading nook's armchair (the same red reading chair, `tools/draw_rooms.py`'s `nook`, at its column 124):
        // all fourteen to read again, once they are all back (the user, 2026-11-22).
        const nook = (w.data?.rooms ?? []).find(r => r.id === 'nook');
        if (nook) {
            const x = nook.x0 + 124;
            const seat = { kind: 'nook', x, left: x - 34, top: nook.floor - 68 };
            w.things.push({ id: 'sec_chair_nook', x, y: nook.floor, route: 'nook', items: [], reach: 14, interact: () => this.read(seat) });
        }
        // Her bed in cabin 8206 (the ship scene's `cabin`, built after the world): E standing on it. Her clip there is
        // the cabin picture's columns 108 to 239 and rows 28 to 127; she sits at column 196.
        s.events.once('update', () => {
            const cab = s.cabin;
            if (!cab) return;
            const x0 = cab.door - 59, top = cab.floor - 32;
            const seat = { kind: 'bed', x: x0 + 196, left: x0 + 108, top: cab.floor - 100 };
            w.things.push({ id: 'sec_bed', x: x0 + 187, y: top, route: 'cabin', items: [], reach: 50,
                interact: () => s.onBed() && this.read(seat) });
        });
        this.refresh();
    }

    // (The return trolley is generated now, the user's choice of three, 2026-11-22: `assets/sprites/book-trolley.png`,
    // loaded by the boot scene; drawn here until then.)
    textures() {
        const s = this.scene;
        if (s.textures.exists('photo-frame')) return;
        const g = s.make.graphics({ x: 0, y: 0 }, false);
        const ink = 0x2e222f;
        // A photo slot's frame on a wall, and an open book in her hands.
        g.fillStyle(ink, 1).fillRect(0, 0, 20, 16);
        g.fillStyle(0xd9a43b, 1).fillRect(1, 1, 18, 14);
        g.fillStyle(0xf3ecdd, 1).fillRect(3, 3, 14, 10);
        g.fillStyle(0xf68181, 1).fillRect(7, 6, 2, 2).fillRect(11, 6, 2, 2).fillRect(7, 7, 6, 2).fillRect(8, 9, 4, 1).fillRect(9, 10, 2, 1);
        g.generateTexture('photo-frame', 20, 16);
        g.clear();
        g.fillStyle(ink, 1).fillRect(0, 1, 13, 7);
        g.fillStyle(0xf3ecdd, 1).fillRect(1, 2, 5, 5).fillRect(7, 2, 5, 5);
        g.fillStyle(0x9babb2, 1).fillRect(2, 3, 3, 1).fillRect(2, 5, 3, 1).fillRect(8, 3, 3, 1).fillRect(8, 5, 3, 1);
        g.generateTexture('book-open', 13, 9);
        g.destroy();
    }

    // Where book n's gap starts on the shelf (px): the fourteen centred on the board.
    slotX(n) {
        const { x0, x1 } = this.data.shelf;
        return x0 + Math.floor((x1 - x0 - (BOOKS * SLOT - (SLOT - SPINE))) / 2) + (n - 1) * SLOT;
    }

    // The shelf: each book that is back stands in its own gap.
    refresh() {
        if (!this.shelfBooks) return;
        const { y } = this.data.shelf;
        const g = this.shelfBooks.clear();
        for (const n of this.returned()) {
            const x = this.slotX(n), h = 11 + (n * 7) % 3;
            g.fillStyle(washed(0x2e222f), 1).fillRect(x, y - h - 1, SPINE, h + 1);
            g.fillStyle(washed(BOOK_COLOURS[n - 1]), 1).fillRect(x + 1, y - h, SPINE - 2, h);
            g.fillStyle(washed(BOOK_ACCENTS[n - 1]), 1).fillRect(x + 2, y - h + 2, SPINE - 4, 1);
        }
    }

    // E at the trolley (the user, 2026-11-22): one book on her goes back at once; with more, the row opens on the
    // books she carries and she chooses which goes back, one at a time, the row opening again on the rest until none
    // is left or she keeps them (Esc). The librarian shelves each. A book given back is hers no more to read (it stays
    // in the row, greyed, and in the HUD's count).
    giveBack() {
        const w = this.world;
        let books = this.heldInOrder();
        if (!books.length) return false;
        const librarian = w.people.byId.npc_librarian;
        w.cut(async () => {
            const several = books.length > 1;
            while (books.length) {
                let n = books[0];
                if (several) {
                    n = await this.choose(books, books.length - 1, { verb: 'return' });
                    if (n == null) break;
                }
                sfx.give();
                if (librarian?.on) await w.people.play(librarian, 'shelve');
                else await w.wait(300);
                this.save.books[n] = 'returned';
                this.refresh();
                const { y } = this.data.shelf, x = this.slotX(n) + 3;
                w.sparkle(x, y - 7);
                sfx.at(x, y).book();
                writeSave(this.save);
                await w.wait(250);
                books = this.heldInOrder();
                if (!several) break;
            }
            if (this.returned().length === BOOKS) {
                sfx.done();
                w.progress.setFlag('books_all');
            }
        });
        return true;
    }

    // Every place she reads (the user, 2026-11-21): the Library's seven armchairs (the red one by the lamp and the
    // two at each reading table, `data.chairs`) and her bed in cabin 8206. E there: she sits (her reading clips,
    // `tools/build_reading.py`), the books she carries show in a row (`choose()`), ← and → pick one, E reads it
    // (she opens it, its first page shows), and back to the row; Esc, B or Space stand her up. Any book she carries,
    // as often as she likes; none carried, she sits a moment and gets up. The row shows every book she has found
    // (the user, 2026-11-22), those given back greyed and stamped, not to be read; in the reading nook's armchair
    // (`kind: 'nook'`, open once all fourteen are back) all fourteen are hers to read again.
    read(seat) {
        const w = this.world, s = this.scene, p = s.player;
        if (w.carry || this.reading) return false;
        const bed = seat.kind === 'bed';
        // (Each clip's frames: sitting down, the pose she holds while she chooses, opening the book and reading.)
        const SIT = bed ? [0, 1, 2, 3] : [0, 1, 2, 3, 4];
        const OPEN = bed ? [4, 5, 6, 7, 8, 9] : [7, 8, 9, 10, 11, 12, 13];
        // (With the towel round her hair after the shower, the bed's clip with it: the user, 2026-11-23.)
        const name = bed ? (s.towel ? 'bed-towel' : 'bed') : 'chair';
        this.reading = true;
        w.cut(async () => {
            const y = p.y;
            p.x = seat.x;
            p.setFlipX(bed);
            p.body.enable = false;
            p.setVisible(false);
            const pic = s.add.image(seat.left, seat.top, 'reading', `${name}-0`).setOrigin(0).setDepth(s.DEPTH.player);
            w.add([pic]);
            this.readingPic = pic;
            const play = async (frames, fps = 9) => {
                for (const i of frames) {
                    pic.setFrame(`${name}-${i}`);
                    await w.wait(1000 / fps);
                }
            };
            // (Her popups stand over her seated head: the reading sheet keeps its heads, src/popup.js.)
            const standTop = y - PLAYER.height;
            await play(SIT);
            const head = s.popups.headOf(pic);
            s.alertOver = head ? -Math.max(0, Math.round(head.top - standTop)) : 0;
            const nook = seat.kind === 'nook';
            const books = nook ? this.allInOrder() : this.foundInOrder();
            const greyed = nook ? () => false : k => this.save.books[k] !== 'held';
            if (!books.length) {
                await w.wait(1100);
            } else {
                const last = books.map(k => !greyed(k)).lastIndexOf(true);
                let at = last >= 0 ? last : books.length - 1;
                for (;;) {
                    const n = await this.choose(books, at, { greyed });
                    if (n == null) break;
                    at = books.indexOf(n);
                    sfx.page();
                    await play(OPEN);
                    await this.panel(`page-${n}`);
                    if (!this.save.read.includes(n)) this.save.read.push(n);
                    writeSave(this.save);
                    await play([...OPEN].reverse().concat(SIT.slice(-1)), 14);
                }
            }
            s.alertOver = 0;
            await play([...SIT].reverse(), 11);
            pic.destroy();
            this.readingPic = null;
            p.setVisible(true);
            p.y = y;
            p.body.enable = true;
            p.body.reset(p.x, y);
            if (!bed) s.pose('front');
            s.stillSince = s.time.now + 4000;       // (on the bed: no bounce right after)
            this.reading = false;
        });
        return true;
    }

    // The books she carries, in the order she got them (`save.bookOrder`; any set held otherwise, by number, after).
    heldInOrder() {
        return this.inOrder(this.held());
    }

    // Every book she has found, carried or given back, in the order she got them.
    foundInOrder() {
        return this.inOrder(this.held().concat(this.returned()));
    }

    // All fourteen (the reading nook): those she found in the order she got them, then the rest by number.
    allInOrder() {
        return this.inOrder(Array.from({ length: BOOKS }, (_, i) => i + 1));
    }

    inOrder(set) {
        const order = (this.save.bookOrder ?? []).filter(n => set.includes(n));
        return order.concat(set.filter(n => !order.includes(n)).sort((a, b) => a - b));
    }

    // A book is hers: held, and its place in the order she got them.
    got(n) {
        n = Number(n);
        this.save.books[n] = 'held';
        this.save.bookOrder ??= [];
        if (!this.save.bookOrder.includes(n)) this.save.bookOrder.push(n);
    }

    // The row of the books she carries, over a soft dark backdrop at the top of the screen, the chosen one raised in
    // a pale frame and its title under the row in the pages' lettering (the user's mock-ups, 2026-11-21). ← and →
    // move along it, E reads (resolves the book's number), Esc, B or Space leave (resolves null). The first time,
    // a hint over her says how (`hint.read`, once in a game: `save.seen`). `greyed(n)`: a book given back, greyed with
    // a red stamp mark, the word stamped beside its title when it is the chosen one, and E does nothing on it (the
    // user's choice, 2026-11-22: the word is wider than a book in a full row). `verb: 'return'`: the trolley's row,
    // its own hint. While the row is open the HUD fades (a full row reaches under it).
    choose(books, at, { greyed = () => false, verb = 'read' } = {}) {
        const s = this.scene, S = 3;
        return new Promise(resolve => {
            const n = books.length, bw = 18 * S, room = VIEW.width - 120;
            let gap = n > 1 ? Math.min(8 * S, Math.floor((room - n * bw) / (n - 1))) : 0;
            gap -= gap % S;
            const roww = n * bw + (n - 1) * gap;
            let titleW = Math.max(...books.map(k => s.textures.get(`book-title-${k}`).getSourceImage().width)) * S;
            const stamp = books.some(greyed) ? this.stamp() : null;
            if (stamp) titleW += 2 * (stamp.w + 12);
            const pad = 4 * S, top = 8, lift = 4 * S, titleH = 16 * S;
            const bw2 = Math.max(roww, titleW) + 2 * pad, bh = pad + lift + 24 * S + 2 * S + titleH + pad;
            const x0 = Math.round((VIEW.width - bw2) / 2);
            const back = s.add.image(x0 - 8, top - 8, this.backdrop(bw2, bh)).setOrigin(0);
            const items = [back];
            const rowX = Math.round((VIEW.width - roww) / 2);
            const covers = books.map((k, i) => {
                const img = s.add.image(rowX + i * (bw + gap), 0, this.cover(k, greyed(k))).setOrigin(0).setScale(S);
                if (greyed(k)) img.setAlpha(0.75);
                items.push(img);
                return img;
            });
            const rim = s.add.image(0, 0, 'book-rim').setOrigin(0).setScale(S);
            const title = s.add.image(VIEW.width / 2, top + pad + lift + 24 * S + 2 * S, `book-title-${books[at]}`).setOrigin(0.5, 0).setScale(S);
            items.push(rim, title);
            const word = stamp && s.add.image(0, 0, stamp.key).setOrigin(0, 0.5).setScale(2);
            if (word) items.push(word);
            s.uiLayer.add(items);
            const hud = s.uiLayer.list.filter(o => !items.includes(o) && o.visible && o.alpha > 0).map(o => [o, o.alpha]);
            hud.forEach(([o]) => s.tweens.add({ targets: o, alpha: 0, duration: 160 }));
            this.choosing = { books, verb, get at() { return at; } };
            const show = () => {
                covers.forEach((c, i) => c.setY(top + pad + (i === at ? 0 : lift)));
                rim.setPosition(covers[at].x - S, top + pad - S);
                title.setTexture(`book-title-${books[at]}`);
                if (word) word.setVisible(greyed(books[at])).setPosition(Math.round(title.x + title.displayWidth / 2 + 12),
                    Math.round(title.y + 8 * S));
            };
            show();
            s.tweens.add({ targets: items, alpha: { from: 0, to: 1 }, duration: 160 });
            const seen = `hint:${verb}`;
            if (!this.save.seen.includes(seen)) {
                this.save.seen.push(seen);
                writeSave(this.save);
                this.world.say(t(`hint.${verb}${s.controls.device === 'pad' ? '.pad' : ''}`), 3000, { kind: 'plate' });
            }
            const done = v => {
                s.events.off('postupdate', poll);
                this.choosing = null;
                s.tweens.add({ targets: items, alpha: 0, duration: 140, onComplete: () => items.forEach(o => o.destroy()) });
                hud.forEach(([o, a]) => o.active && s.tweens.add({ targets: o, alpha: a, duration: 160 }));
                resolve(v);
            };
            const poll = () => {
                const i = s.controls.state;
                if (i.leftPressed && at > 0) { at--; sfx.page(); show(); }
                else if (i.rightPressed && at < n - 1) { at++; sfx.page(); show(); }
                else if (i.activatePressed) {
                    if (greyed(books[at])) sfx.book();      // (given back: not hers to read now)
                    else done(books[at]);
                } else if (i.escapePressed || i.jumpPressed) done(null);
            };
            // (A key counts only in the frame it is pressed: the E that sat her down was half a second ago.)
            s.events.on('postupdate', poll);
        });
    }

    // A book's small cover for the row (18 x 24, shown at 3x): its cover's colour, a darker spine edge, its title's
    // colour for a label. Greyed (given back): its colours to grey and a green stamp on its lower half, a disc with a
    // white check mark (the user, 2026-11-22). And the pale frame round the chosen one.
    cover(n, grey = false) {
        const s = this.scene, key = `book-cover-${n}${grey ? '-grey' : ''}`;
        if (s.textures.exists(key)) return key;
        const mini = `cover-mini-${n}`;
        if (s.textures.exists(mini)) {
            // Her cover's picture, small (tools/build_covers.py's mini-<n>); greyed: its colours to grey, the stamp on it.
            this.rim();
            if (!grey) return mini;
            const src = s.textures.get(mini).getSourceImage();
            const tex = s.textures.createCanvas(key, 18, 24), ctx = tex.getContext();
            ctx.drawImage(src, 0, 0);
            const img = ctx.getImageData(0, 0, 18, 24), d = img.data;
            for (let i = 0; i < d.length; i += 4) {
                const v = Math.round(70 + (0.3 * d[i] + 0.59 * d[i + 1] + 0.11 * d[i + 2]) * 0.45);
                d[i] = d[i + 1] = d[i + 2] = v;
            }
            ctx.putImageData(img, 0, 0);
            STAMP.forEach((row, y) => [...row].forEach((ch, x) => {
                if (ch === '.') return;
                ctx.fillStyle = ch === 'G' ? '#1ebc73' : '#f4f4ec';
                ctx.fillRect(4 + x, 10 + y, 1, 1);
            }));
            tex.refresh();
            return key;
        }
        const ash = c => {
            const v = 0.3 * ((c >> 16) & 255) + 0.59 * ((c >> 8) & 255) + 0.11 * (c & 255), g = Math.round(70 + v * 0.45);
            return (g << 16) | (g << 8) | g;
        };
        const tone = c => (grey ? ash(c) : c);
        const c = BOOK_COLOURS[n - 1], dark = [16, 8, 0].reduce((v, sh) => v | (Math.round(((c >> sh) & 255) * 0.75) << sh), 0);
        const g = s.make.graphics({ x: 0, y: 0 }, false);
        g.fillStyle(0x2e222f, 1).fillRect(1, 1, 16, 22);
        g.fillStyle(tone(c), 1).fillRect(2, 2, 14, 20);
        g.fillStyle(tone(dark), 1).fillRect(2, 2, 2, 20);
        g.fillStyle(tone(BOOK_ACCENTS[n - 1]), 1).fillRect(6, 6, 8, 3);
        if (grey) {
            // (the stamp: `STAMP`, at the top of this file)
            STAMP.forEach((row, y) => [...row].forEach((ch, x) => {
                if (ch !== '.') g.fillStyle(ch === 'G' ? 0x1ebc73 : 0xf4f4ec, 1).fillRect(4 + x, 10 + y, 1, 1);
            }));
        }
        g.generateTexture(key, 18, 24);
        g.destroy();
        this.rim();
        return key;
    }

    // The pale frame round the chosen book in the row.
    rim() {
        const s = this.scene;
        if (s.textures.exists('book-rim')) return;
        const g = s.make.graphics({ x: 0, y: 0 }, false);
        g.fillStyle(0xfbff86, 1).fillRect(0, 0, 20, 1).fillRect(0, 25, 20, 1).fillRect(0, 0, 1, 26).fillRect(19, 0, 1, 26);
        g.generateTexture('book-rim', 20, 26);
        g.destroy();
    }

    // A photo in a gold frame (a dark outline, two px of gold lit along its top, a dark line inside): made once.
    framed(key) {
        const s = this.scene, out = `${key}-framed`;
        if (s.textures.exists(out)) return out;
        const src = s.textures.get(key).getSourceImage(), B = 4, W = src.width + 2 * B, H = src.height + 2 * B;
        const tex = s.textures.createCanvas(out, W, H), ctx = tex.getContext();
        ctx.imageSmoothingEnabled = false;
        const r = (c, x, y, w, h) => { ctx.fillStyle = c; ctx.fillRect(x, y, w, h); };
        r('#2e222f', 0, 0, W, H);
        r('#d9a43b', 1, 1, W - 2, H - 2);
        r('#f0c860', 1, 1, W - 2, 1);
        r('#a8782a', 1, H - 2, W - 2, 1);
        r('#2e222f', B - 1, B - 1, src.width + 2, src.height + 2);
        ctx.drawImage(src, B, B);
        tex.refresh();
        return out;
    }

    // The word stamped beside a given-back book's title (`book.returned`, in the menu's plate lettering at 2x), green,
    // in a green frame (the user, 2026-11-22); made once per language.
    stamp() {
        const s = this.scene, text = t('book.returned'), key = `book-stamp-green-${text}`;
        if (!s.textures.exists(key)) {
            const word = s.textures.get(pixelText(s, `${key}-word`, 'S', text, { bands: ['#1ebc73'], outline: '#0b3b26', thick: 0, shadow: 0 }))
                .getSourceImage();
            const W = word.width + 8, H = word.height + 6;
            const tex = s.textures.createCanvas(key, W, H), ctx = tex.getContext();
            ctx.imageSmoothingEnabled = false;
            ctx.fillStyle = 'rgba(8, 36, 22, 0.55)';
            ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = '#1ebc73';
            ctx.fillRect(0, 0, W, 1); ctx.fillRect(0, H - 1, W, 1); ctx.fillRect(0, 0, 1, H); ctx.fillRect(W - 1, 0, 1, H);
            ctx.drawImage(word, 4, 3);
            tex.refresh();
        }
        const img = s.textures.get(key).getSourceImage();
        return { key, w: img.width * 2 };
    }

    // The row's backdrop: a rounded rectangle of the night's dark, see-through (two thirds), its rim feathered
    // a few px (the user: "slightly more transparent, smooth the edges"); made at the size it is asked for.
    backdrop(w, h) {
        const s = this.scene, F = 8, key = `book-backdrop-${w}x${h}`;
        if (s.textures.exists(key)) return key;
        const tex = s.textures.createCanvas(key, w + 2 * F, h + 2 * F);
        const ctx = tex.getContext();
        ctx.filter = 'blur(3.5px)';
        ctx.fillStyle = 'rgba(13, 11, 20, 0.667)';
        ctx.beginPath();
        ctx.roundRect(F, F, w, h, 15);
        ctx.fill();
        tex.refresh();
        return key;
    }

    // A picture over the whole screen (a book's page, a photo, cabin 8206's desk at `scale` 2), until she presses a key.
    panel(key, { scale = 0 } = {}) {
        const s = this.scene;
        return new Promise(resolve => {
            const dim = s.add.rectangle(0, 0, VIEW.width, VIEW.height, 0x0d0b14, 0.82).setOrigin(0);
            const exists = s.textures.exists(key);
            // (A photo slot's picture in its gold frame, as the small one on the wall: the user, 2026-11-22.)
            const framed = exists && key.startsWith('photo-');
            const pic = s.add.image(VIEW.width / 2, VIEW.height / 2, framed ? this.framed(key) : exists ? key : 'photo-frame');
            // (A framed photo leaves 38 px over and under it: La Cucina's, 176 x 232 framed, then shows at 2x, the nook's at 3x.)
            pic.setScale(scale || Math.max(1, Math.floor(Math.min((VIEW.width - 160) / pic.width, (VIEW.height - (framed ? 76 : 100)) / pic.height))));
            s.uiLayer.add([dim, pic]);
            s.tweens.add({ targets: [dim, pic], alpha: { from: 0, to: 1 }, duration: 220 });
            sfx.page();
            const close = () => {
                s.tweens.add({ targets: [dim, pic], alpha: 0, duration: 180, onComplete: () => { dim.destroy(); pic.destroy(); resolve(); } });
            };
            // Any key, after a moment (so the key that opened it does not close it).
            s.time.delayedCall(450, () => {
                const poll = () => {
                    const i = s.controls.state;
                    if (i.activatePressed || i.jumpPressed || i.leftPressed || i.rightPressed || i.escapePressed || i.startPressed) {
                        s.events.off('postupdate', poll);
                        close();
                    }
                };
                s.events.on('postupdate', poll);
            });
        });
    }
}
