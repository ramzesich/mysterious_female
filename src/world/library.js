// The library's books (GAME_DESIGN.md §6.1.2, "her own thread"): ten of them are out on the ship.
// A book is a pocket item; the return trolley takes the ones she carries and the librarian shelves
// each into its gap on the shelf behind her desk, so the shelf shows how far the collection is. In
// the red reading chair she reads the next book she has not read: its page shows a drawing that
// hints at one hidden thing on the ship. Also here: the photo slots' and the pages' full-screen panel.

import { VIEW } from '../config.js';
import { writeSave } from '../save.js';
import { sfx } from '../sfx.js';

export const BOOK_COLOURS = [0xae2334, 0x4d9be6, 0x1ebc73, 0xf9c22b, 0x905ea9, 0xf68181, 0x0b5e65, 0xcd683d, 0x323353, 0xe83b3b];
const SLOT = 9;         // px per book on the shelf

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
        // The shelf with ten gaps, on the wall behind her desk: a board on brackets, a brass plate.
        const { x0, y } = data.shelf;
        const width = 10 * SLOT + 8;
        const g = s.add.graphics().setDepth(D.decor + 0.2);
        g.fillStyle(0x7a4528, 1).fillRect(x0 - 2, y, width + 4, 3);
        g.fillStyle(0x46291f, 1).fillRect(x0 - 2, y + 3, width + 4, 1).fillRect(x0 + 4, y + 3, 2, 6).fillRect(x0 + width - 6, y + 3, 2, 6);
        g.fillStyle(0x46291f, 0.35).fillRect(x0, y - 15, width, 15);
        for (let i = 0; i < 10; i++) g.fillStyle(0x2e222f, 0.5).fillRect(x0 + 4 + i * SLOT, y - 13, SLOT - 2, 13);
        this.shelfBooks = s.add.graphics().setDepth(D.decor + 0.21);
        w.add([g, this.shelfBooks]);
        // The return trolley by her desk, and the red reading chair by the window.
        this.textures();
        const trolley = s.add.image(data.trolley.x, data.trolley.y, 'book-trolley').setOrigin(0.5, 1).setDepth(D.props - 0.03);
        const chair = s.add.image(data.chair.x, data.chair.y, 'shipart', 'reading-chair').setOrigin(0.5, 1).setDepth(D.props - 0.03);
        const lamp = s.add.image(data.chair.x - 22, data.chair.y, 'shipart', 'floor-lamp').setOrigin(0.5, 1).setDepth(D.props - 0.04);
        w.add([trolley, chair, lamp]);
        w.things.push({ id: 'src_trolley', x: data.trolley.x, y: data.trolley.y, route: 'inside', items: [trolley], reach: 22,
            interact: () => this.giveBack() });
        w.things.push({ id: 'sec_chair', x: data.chair.x, y: data.chair.y, route: 'inside', items: [chair, lamp], reach: 16,
            interact: () => this.read() });
        this.refresh();
    }

    textures() {
        const s = this.scene;
        if (s.textures.exists('book-trolley')) return;
        const g = s.make.graphics({ x: 0, y: 0 }, false);
        const ink = 0x2e222f;
        g.fillStyle(ink, 1).fillRect(2, 14, 30, 16).fillRect(4, 30, 4, 4).fillRect(26, 30, 4, 4).fillRect(0, 4, 3, 12);
        g.fillStyle(0xab947a, 1).fillRect(3, 15, 28, 14);
        g.fillStyle(0x7a4528, 1).fillRect(3, 21, 28, 1);
        // A few books waiting on it, and its sign: an arrow down into the trolley.
        [[5, 0xf68181], [9, 0x4d9be6], [13, 0xf9c22b]].forEach(([x, c]) => g.fillStyle(c, 1).fillRect(x, 7, 3, 8));
        g.fillStyle(ink, 1).fillRect(18, 0, 14, 12);
        g.fillStyle(0xf3ecdd, 1).fillRect(19, 1, 12, 10);
        g.fillStyle(0xae2334, 1).fillRect(24, 2, 2, 5).fillTriangle(21, 6, 29, 6, 25, 10);
        g.generateTexture('book-trolley', 34, 34);
        g.clear();
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

    // The shelf: each book that is back stands in its own gap.
    refresh() {
        if (!this.shelfBooks) return;
        const { x0, y } = this.data.shelf;
        const g = this.shelfBooks.clear();
        for (const n of this.returned()) {
            const x = x0 + 4 + (n - 1) * SLOT, h = 11 + (n * 7) % 3;
            g.fillStyle(0x2e222f, 1).fillRect(x, y - h - 1, SLOT - 2, h + 1);
            g.fillStyle(BOOK_COLOURS[n - 1], 1).fillRect(x + 1, y - h, SLOT - 4, h);
            g.fillStyle(0xf3ecdd, 1).fillRect(x + 2, y - h + 2, SLOT - 6, 1);
        }
    }

    // E at the trolley: the books she carries go back; the librarian shelves them.
    giveBack() {
        const w = this.world, s = this.scene;
        const books = this.held();
        if (!books.length) return false;
        const librarian = w.people.byId.npc_librarian;
        w.cut(async () => {
            sfx.pickup();
            for (const n of books) {
                if (librarian?.on) await w.people.play(librarian, 'shelve');
                else await w.wait(300);
                this.save.books[n] = 'returned';
                this.refresh();
                const { x0, y } = this.data.shelf;
                w.sparkle(x0 + 7 + (n - 1) * SLOT, y - 7);
                sfx.checkpoint();
                await w.wait(250);
            }
            writeSave(this.save);
            if (this.returned().length === 10) w.progress.setFlag('books_all');
        });
        return true;
    }

    // E at the reading chair: she sits and reads the next book she has not read; its page shows.
    read() {
        const w = this.world, s = this.scene, p = s.player;
        if (w.carry) return false;
        const next = Object.keys(this.save.books).map(Number).sort((a, b) => a - b).find(n => !this.save.read.includes(n));
        w.cut(async () => {
            const chair = this.data.chair;
            p.setFlipX(false);
            p.x = chair.x - 2;
            p.body.reset(p.x, p.y);
            const seated = s.anims.exists('her-read');
            if (seated) {
                p.anims.play('her-read');
                await w.wait(700);
            }
            const book = s.add.image(p.x + 10, p.y - (seated ? 24 : 32), 'book-open').setDepth(s.DEPTH.player + 0.02);
            w.add([book]);
            await w.wait(next ? 900 : 1800);
            if (next) {
                await this.panel(`page-${next}`);
                this.save.read.push(next);
                writeSave(this.save);
            }
            book.destroy();
            s.pose('stand');
        });
        return true;
    }

    // On her own bed with the fifth book, not read yet: she sits down on its edge and reads it there,
    // as in the Library's chair.
    readOnBed() {
        const w = this.world, s = this.scene, p = s.player;
        if (this.save.books['5'] !== 'held' || this.save.read.includes(5) || w.carry || this.reading) return false;
        this.reading = true;
        this.textures();
        const y = p.y;
        w.cut(async () => {
            p.setFlipX(false);
            p.body.enable = false;
            const seated = s.anims.exists('her-read');
            if (seated) {
                p.anims.play('her-read');
                // (Her seat comes down onto the mattress; her legs hang over its side.)
                await w.tween({ targets: p, y: y + 13, duration: 500, ease: 'Quad.easeOut' });
                await w.wait(200);
            }
            const book = s.add.image(p.x + 10, p.y - (seated ? 24 : 32), 'book-open').setDepth(s.DEPTH.player + 0.02);
            w.add([book]);
            await w.wait(900);
            await this.panel('page-5');
            this.save.read.push(5);
            writeSave(this.save);
            book.destroy();
            s.pose('stand');
            p.y = y;
            p.body.enable = true;
            p.body.reset(p.x, y);
            s.stillSince = s.time.now + 4000;       // no bounce right after
            this.reading = false;
        });
        return true;
    }

    // A picture over the whole screen (a book's page, a photo), until she presses a key.
    panel(key) {
        const s = this.scene;
        return new Promise(resolve => {
            const dim = s.add.rectangle(0, 0, VIEW.width, VIEW.height, 0x0d0b14, 0.82).setOrigin(0);
            const exists = s.textures.exists(key);
            const pic = s.add.image(VIEW.width / 2, VIEW.height / 2, exists ? key : 'photo-frame');
            pic.setScale(Math.floor(Math.min((VIEW.width - 160) / pic.width, (VIEW.height - 100) / pic.height)));
            s.uiLayer.add([dim, pic]);
            s.tweens.add({ targets: [dim, pic], alpha: { from: 0, to: 1 }, duration: 220 });
            sfx.pickup();
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
