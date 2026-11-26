// The HUD (the user, 2026-11-20; docs/progress-decisions.md, "The HUD"): nothing at the start; each
// thing shows from the moment it is first hers, and stays.
//
// - One row: the tangerines in a slot of their own on the left (kept free before the first one),
//   then the things to find, Bumbot's, hers, her husband's (each kind's count of its total) and the
//   books, from left to right in the order she first finds them; each keeps the width of its
//   largest count, so nothing moves once placed.
// - Under it the four key cards, each in its own place: a faint outline until it is hers.
// - At the top right, on the row's line, her two utilities once hers, the grip socks and the parasol (the user,
//   2026-11-26): from the right edge in the order she gets them, each as its close-up closes.
// - The first tangerine flies from where it was to its slot, and the count shows as it lands; a
//   card flies out from behind its close-up as that closes; a kind's count shows as its close-up
//   closes, a little bigger, settling to its size. A count going up bumps its picture.
//
// The pictures: `tools/build_hud.py` (`hud` atlas, every one with a light rim but the cards), drawn
// at 2 screen px a pixel; the numbers in the popups' lettering (Galmuri9, src/popup.js), white with a
// navy outline. Positions are in the HUD's pixels (half the screen's), as in the approved mock-up.

import { TALLY, BOOKS } from './config.js';

const S = 2;                    // screen px a HUD pixel
const LEFT = 12;                // the row's left edge
const ROW = 32;                 // the row's bottom line: the rims' lowest row
const GAP = 3;                  // from a picture to its number
const APART = 10;               // from a number to the next picture
const CARDS_Y = 42, CARD_STEP = 15;
const CARD_ORDER = ['deck', 'ent', 'hk', 'off'];
const KINDS = ['cat', 'her', 'him', 'book'];
const TOOLS = ['socks', 'parasol'];     // her verbs shown as a picture (`verb:<name>`, the user's Paint files)
const RIGHT = 11;                       // their rims' right edge from the screen's, as the tangerine's rim on the left
const TOOL_GAP = 6;                     // between two utilities
const NAVY = '#1d2b53';
// Letters the lettering lacks, drawn for the HUD (`tools/build_hud.py`, in the `hud` atlas): the ∞.
const OWN = { 0x221e: 12 };
const POP = { from: 1.3, ms: 220 };     // a count's first showing
const BUMP = { to: 1.2, ms: 70 };       // a count going up

export class Hud {
    constructor(scene) {
        this.s = scene;
        this.F = scene.cache.json.get('popup-layout').font;
        const save = scene.save;
        // What is shown, kept: the tangerines' slot from the first one, the kinds in the order found.
        save.hud ??= {
            tangerine: save.tangerines > 0,
            order: KINDS.filter(k => this.count(k) > 0),
            cards: save.cards.length > 0,
        };
        save.hud.tools ??= TOOLS.filter(t => save.verbs.includes(t));
        this.pending = new Set();         // kinds and cards waiting for their close-up to close
        this.items = {};
        this.slotX = {};
        // The tangerines.
        this.items.tangerine = this.counter('tangerine', 'x 56', LEFT);
        this.start = LEFT + this.items.tangerine.width;
        // The kinds: their places are given in the order they are found.
        for (const k of KINDS) this.items[k] = this.counter(k, k === 'book' ? `${BOOKS}/${BOOKS}` : '8/8', 0);
        // Her utilities.
        this.tools = Object.fromEntries(TOOLS.map(t => [t, this.tool(t)]));
        // The cards.
        this.cards = CARD_ORDER.map((card, i) => {
            const x = (LEFT + i * CARD_STEP) * S, y = CARDS_Y * S;
            const ghost = scene.add.image(x, y, 'hud', `card-${card}-ghost`).setOrigin(0).setScale(S);
            const img = scene.add.image(x, y, 'hud', `card-${card}`).setOrigin(0).setScale(S);
            scene.uiLayer.add([ghost, img]);
            return { card, ghost, img };
        });
        this.refresh(true);
    }

    // A utility's picture (with its rim), hidden.
    tool(key) {
        const f = this.s.textures.getFrame('hud', key);
        const icon = this.s.add.image(0, 0, 'hud', key).setScale(S).setVisible(false);
        this.s.uiLayer.add(icon);
        return { key, w: f.cutWidth, h: f.cutHeight, icon, shown: false };
    }

    // A picture and its number, at `x` (the picture's left, in HUD px), hidden.
    counter(key, widest, x) {
        const s = this.s, f = s.textures.getFrame('hud', key);
        const w = f.cutWidth - 2, h = f.cutHeight - 2;           // the picture without its rim
        const icon = s.add.image(0, 0, 'hud', key).setScale(S).setVisible(false);
        const tkey = `hud-text-${key}`;
        const tw = this.textWidth(widest);
        const canvas = s.textures.exists(tkey) ? s.textures.get(tkey) : s.textures.createCanvas(tkey, tw + 2, this.F.height + 2);
        const text = s.add.image(0, 0, tkey).setOrigin(0).setScale(S).setVisible(false);
        s.uiLayer.add([icon, text]);
        const c = { key, w, h, icon, text, canvas, shown: false, value: null, width: w + GAP + tw + APART };
        this.place(c, x);
        return c;
    }

    place(c, x) {
        c.x = x;
        // (The rimmed picture a pixel up and left of the picture; its middle, for the pop.)
        c.icon.setPosition((x - 1 + (c.w + 2) / 2) * S, (ROW - (c.h + 2) + 1 + (c.h + 2) / 2) * S);
        // (The digits' lowest row on the row's line less two, as the approved mock-up has them.)
        c.text.setPosition((x + c.w + GAP) * S, (ROW - 2 - this.F.base - 1) * S);
    }

    // The lettering's width of `str`, with its outline.
    textWidth(str) {
        let w = 0;
        for (const ch of str) w += this.adv(ch.codePointAt(0));
        return w + 1;
    }

    adv(code) {
        return OWN[code] ?? this.F.adv[code] ?? this.F.adv[32];
    }

    // The number, white with a navy outline, drawn into the counter's own canvas.
    write(c, str) {
        if (c.value === str) return;
        c.value = str;
        const s = this.s, ctx = c.canvas.getContext(), W = c.canvas.width, H = c.canvas.height;
        ctx.clearRect(0, 0, W, H);
        const white = document.createElement('canvas');
        white.width = W; white.height = H;
        const g = white.getContext('2d');
        let x = 1;
        for (const ch of str) {
            const code = ch.codePointAt(0), name = `g${code}`;
            const f = code === 32 ? null : OWN[code] ? s.textures.getFrame('hud', name) : s.textures.getFrame('popups', name);
            if (f) g.drawImage(f.source.image, f.cutX, f.cutY, f.cutWidth, f.cutHeight, x, 1, f.cutWidth, f.cutHeight);
            x += this.adv(code);
        }
        const navy = document.createElement('canvas');
        navy.width = W; navy.height = H;
        const n = navy.getContext('2d');
        n.drawImage(white, 0, 0);
        n.globalCompositeOperation = 'source-in';
        n.fillStyle = NAVY;
        n.fillRect(0, 0, W, H);
        for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [-1, 1], [1, -1]]) ctx.drawImage(navy, dx, dy);
        ctx.drawImage(white, 0, 0);
        c.canvas.refresh();
    }

    count(kind) {
        const save = this.s.save;
        if (kind === 'book') return Object.keys(save.books).length;
        return save.keeps.filter(k => k.startsWith(`keep:${kind}:`)).length;
    }

    total(kind) {
        return kind === 'book' ? BOOKS : this.s.world?.data?.finale?.totals?.keeps?.[kind] ?? 0;
    }

    // Show `c`: at once (`quiet`, a game loaded), or a little bigger, settling.
    show(c, quiet) {
        c.shown = true;
        c.icon.setVisible(true);
        c.text?.setVisible(true);
        if (quiet) return;
        this.s.tweens.killTweensOf(c.icon);
        c.icon.setScale(S * POP.from);
        this.s.tweens.add({ targets: c.icon, scale: S, duration: POP.ms, ease: 'Quad.easeOut' });
    }

    bump(c) {
        this.s.tweens.killTweensOf(c.icon);
        c.icon.setScale(S);
        this.s.tweens.add({ targets: c.icon, scale: S * BUMP.to, duration: BUMP.ms, yoyo: true, ease: 'Quad.easeOut' });
    }

    // Everything from the save. `quiet`: no pops (the HUD's first drawing).
    refresh(quiet = false) {
        const s = this.s, save = s.save, H = save.hud;
        // The tangerines: from the first that has landed (`landed()`), or any she has at the start.
        const t = this.items.tangerine;
        const infinite = s.infiniteTangerines?.();
        if (!H.tangerine && (infinite || (quiet && save.tangerines > 0))) H.tangerine = true;
        this.write(t, infinite ? 'x ∞' : `x ${Math.max(0, save.tangerines - (s.flying ?? 0))}`);
        if (H.tangerine && !t.shown) this.show(t, true);
        // The kinds: a new one takes the next place (unless its close-up is still open).
        for (const k of KINDS) {
            if (this.count(k) > 0 && !H.order.includes(k) && !this.pending.has(k)) H.order.push(k);
        }
        let x = this.start;
        for (const k of H.order) {
            const c = this.items[k];
            if (c.x !== x) this.place(c, x);
            x += c.width;
            if (this.pending.has(k)) continue;
            const str = `${this.count(k)}/${this.total(k)}`;
            const grew = c.shown && c.value !== str;
            this.write(c, str);
            if (!c.shown) this.show(c, quiet);
            else if (grew && !quiet) this.bump(c);
        }
        // Her utilities: a new one takes the next place leftward (unless its close-up is still open).
        for (const t of TOOLS) {
            if (s.save.verbs.includes(t) && !H.tools.includes(t) && !this.pending.has(t)) H.tools.push(t);
        }
        let right = s.scale.gameSize.width / S - RIGHT;
        for (const t of H.tools) {
            const c = this.tools[t];
            // (Its rimmed picture's lowest row on the row's line, as the counts' pictures.)
            c.icon.setPosition((right - c.w / 2) * S, (ROW + 1 - c.h / 2) * S);
            right -= c.w + TOOL_GAP;
            if (!c.shown) this.show(c, quiet);
        }
        // The cards: the row from the first card that has arrived; each held one once it has.
        if (!H.cards && save.cards.some(c => !this.pending.has(`card:${c}`))) H.cards = true;
        for (const c of this.cards) {
            const held = save.cards.includes(c.card) && !this.pending.has(`card:${c.card}`);
            c.ghost.setVisible(H.cards && !held);
            if (!c.img.scene) continue;
            c.img.setVisible(H.cards && held);
        }
    }

    // A kind or a card that will show when its close-up closes (`release`).
    expect(name) {
        this.pending.add(name);
    }

    // (`below`: the close-up's lowest piece, which a card starts behind.)
    release(name, below = null) {
        if (!this.pending.delete(name)) return;
        if (name.startsWith('card:')) this.flyCard(name.slice(5), below);
        else this.refresh();
    }

    // A card out from behind its close-up (the middle of the screen) to its place.
    flyCard(card, below = null) {
        const s = this.s, slot = this.cards.find(c => c.card === card);
        if (!slot) return this.refresh();
        // (From the card's own middle in its close-up, under its lanyard: the close-up stands in the
        // screen's middle at 2x, the card's body 30 of its px under that.)
        const from = { x: s.scale.gameSize.width / 2, y: s.scale.gameSize.height / 2 + 60 };
        const to = { x: slot.img.x + slot.img.displayWidth / 2, y: slot.img.y + slot.img.displayHeight / 2 };
        const img = s.add.image(from.x, from.y, 'hud', `card-${card}`).setScale(S);
        s.uiLayer.add(img);
        // (Behind the close-up while it fades; in front of everything once that is gone.)
        const list = s.uiLayer.list;
        if (below && list.includes(below)) Phaser.Utils.Array.MoveBelow(list, img, below);
        s.time.delayedCall(170, () => { if (img.scene) Phaser.Utils.Array.BringToTop(s.uiLayer.list, img); });
        this.pending.add(`card:${card}`);
        const k = { v: 0 };
        s.tweens.add({
            targets: k, v: 1, duration: TALLY.ms + 150, ease: 'Sine.easeInOut',
            onUpdate: () => img.setPosition(from.x + (to.x - from.x) * k.v, from.y + (to.y - from.y) * k.v - Math.sin(Math.PI * k.v) * TALLY.arc),
            onComplete: () => {
                img.destroy();
                this.pending.delete(`card:${card}`);
                const first = !s.save.hud.cards;
                this.refresh();
                if (first) this.cards.forEach(c => { if (c.ghost.visible) { c.ghost.setAlpha(0); s.tweens.add({ targets: c.ghost, alpha: 1, duration: 300 }); } });
                slot.img.setOrigin(0.5).setPosition(to.x, to.y);
                s.tweens.add({ targets: slot.img, scale: { from: S * POP.from, to: S }, duration: POP.ms, ease: 'Quad.easeOut' });
            },
        });
    }

    // Where a tangerine flying to the count lands (screen px), and the scale it lands at.
    tangerineTarget() {
        const c = this.items.tangerine;
        // (The game's tangerine stands on its point 0.6 down: `setOrigin(0.5, 0.6)`.)
        return { x: c.icon.x, y: c.icon.y + 0.1 * c.h * S, scale: S };
    }

    // A tangerine has landed on the count: it shows (the first), or bumps.
    landed() {
        const c = this.items.tangerine, s = this.s;
        if (!s.save.hud.tangerine) {
            s.save.hud.tangerine = true;
            this.refresh();
            this.show(c, false);
        } else {
            this.refresh();
            this.bump(c);
        }
    }

    // D with none on her: the count blinks once.
    blink() {
        const t = this.items.tangerine.text;
        this.s.tweens.killTweensOf(t);
        t.setAlpha(1);
        this.s.tweens.add({ targets: t, alpha: 0.15, duration: 110, yoyo: true, repeat: 1, onComplete: () => t.setAlpha(1) });
    }

    // For the playtests: what each count shows ('' while hidden).
    state() {
        const out = {};
        for (const [k, c] of Object.entries(this.items)) out[k] = c.shown ? c.value : '';
        out.tools = (this.s.save.hud.tools ?? []).filter(t => this.tools[t].shown);
        out.cards = this.cards.filter(c => c.img.visible).map(c => c.card);
        out.order = [...this.s.save.hud.order];
        return out;
    }
}
