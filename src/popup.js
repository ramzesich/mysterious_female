// Every popup over someone's head (the user, 2026-11-20: "we're refining the looks of every popup in
// the game ... a nice framing, and differentiate between [speech] bubbles and thought clouds"):
//
// - **speech**: what is said aloud (her words at a mishap, "Oops!", Bumbot's "Meow!"): a bubble whose
//   tail comes from the direction of the middle of the speaker's head and stops short of it ("not
//   connected to it", the user);
// - **thought**: what is thought (a lock and its card, her hands too full for a ladder, the people's
//   wishes): a cloud whose two small circles lead the same way;
// - **shout**: her cry, a burst with no tail over her head, following her;
// - **plate**: the game's own hints, on the brass plate.
//
// The art is built by tools/build_popups.py (`popups` atlas, `popup-layout`): generated frames sized to
// their words by a band of each whose two edges match, repeated or taken out (`sizeTo`), generated icons, and
// Galmuri9 set at its own pixel size. Where a head is, frame by frame, is `heads` (tools/build_heads.py):
// whichever of her pictures shows her (her sheet, a gag's sprite, the towels'), the people's, Bumbot's in
// her arms. Placed each frame after everything has moved: over the head, inside the view, clear of the
// other popups (hers first), the tail drawn from the bubble to the head.

const GAP = 3;              // px between a tail's tip (or the last circle) and the head's top
const TAIL = 7;             // px of tail under a bubble, at most
const MARGIN = 3;           // px kept from the view's edges
const PAD = { speech: [8, 5], thought: [11, 7], shout: [16, 10], plate: [9, 6] };
const FRAME = { speech: 'speech', thought: 'thought', shout: 'shout', plate: 'plate' };
const INK = { speech: '#2e222f', thought: '#2e222f', shout: '#ae2334', plate: '#fbb954' };
// What a popup's text says in pictures (the old emoji), and what is no picture at all.
const EMOJI = { '🔒': 'padlock', '🪜': 'ladder', '✋': 'hand', '💧': 'drop', '❄': 'snow' };
const DROPPED = new Set(['🚧']);
const HER_SHEETS = ['her', 'her-towel', 'her-cat', 'her-mishaps', 'gags', 'towels'];

export class Popups {
    constructor(scene) {
        this.s = scene;
        this.L = scene.cache.json.get('popup-layout');
        this.heads = frameHeads(scene, scene.cache.json.get('heads') ?? {});
        this.list = [];
        this.pixels = {};
        scene.events.on('postupdate', this.update, this);
        scene.events.once('shutdown', () => scene.events.off('postupdate', this.update, this));
    }

    // A popup of `kind` ('auto': speech, or a thought for one that is only pictures or a lock) over
    // the head `speaker()` returns ({ x, y, top } in the world, or null), `rank` lower placed first.
    make(kind, speaker, rank = 1) {
        const p = new Popup(this, kind, speaker, rank);
        this.list.push(p);
        return p;
    }

    // A person's wish (src/world/people.js): a thought cloud with its picture over their head, bobbing
    // a little. Returns what stands for the old bubble and its icon (`bubbleItems`): `setVisible`, its
    // picture changed by `setTexture` (a `world.icon()` key, `pict-<name>`), a hop by tweening `y`;
    // `setPosition` is theirs to call and ignored (it places itself from their head).
    wish(person, icon) {
        const speaker = () => {
            const h = person.sprite?.visible !== false && person.sprite?.texture?.key === 'people' ? this.headOf(person.sprite) : null;
            if (h) return h;
            const top = person.y - (person.dy ?? 0) - 59;
            return { x: person.x + (person.bubbleDx ?? 0), y: top + 9, top };
        };
        const pop = this.make('thought', speaker, 2).setText('', { icon, bob: true });
        const stand = {
            setVisible: v => { pop.setVisible(v); return stand; },
            setPosition: () => stand,
            setTexture: key => { pop.setText('', { icon: String(key).replace(/^pict-/, ''), bob: true }); return stand; },
            get visible() { return pop.visible; },
            get y() { return pop.y; },
            set y(v) { pop.y = v; },
        };
        // (The icon's stand-in takes the same calls but no hop: the tween is given both.)
        const pic = {
            setVisible: () => pic,
            setPosition: () => pic,
            setTexture: key => { stand.setTexture(key); return pic; },
            get visible() { return pop.visible; },
            get y() { return 0; },
            set y(v) {},
            // (What the picture is, as a `world.icon()` key: the playtests ask.)
            get texture() { return { key: `pict-${pop.opts.icon}` }; },
        };
        return [stand, pic];
    }

    // Where a sprite's head is now: { x, y, top } in the world, from its frame's entry in `heads`
    // (`which`: another figure's in the same picture, Bumbot's in her arms), or null.
    headOf(sprite, which = null) {
        if (!sprite?.frame) return null;
        const table = this.heads[which ?? sprite.texture.key];
        const h = table?.[sprite.frame.name];
        if (!h) return null;
        const w = sprite.frame.width, sx = Math.abs(sprite.scaleX), sy = Math.abs(sprite.scaleY);
        const left = sprite.x - sprite.originX * w * sx, top = sprite.y - sprite.originY * sprite.frame.height * sy;
        // (Phaser mirrors a flipped frame in place: the same box, its columns the other way.)
        const hx = sprite.flipX ? w - 1 - h[0] : h[0];
        return { x: left + (hx + 0.5) * sx, y: top + (h[1] + 0.5) * sy, top: top + h[2] * sy };
    }

    // Her head, in whichever picture shows her now: her own sprite, or (in a gag, where she is hidden)
    // the sprite of one of her sheets nearest her.
    herHead() {
        const s = this.s, p = s.player;
        if (p.visible && p.alpha > 0) return this.headOf(p);
        let best = null, bestD = 260;
        for (const o of s.worldLayer.list) {
            if (!o.visible || !o.frame || !HER_SHEETS.includes(o.texture?.key)) continue;
            const h = this.headOf(o);
            if (!h) continue;
            const d = Math.abs(h.x - p.x) + Math.abs(h.y - p.y) * 0.5;
            if (d < bestD) { best = h; bestD = d; }
        }
        return best;
    }

    // A frame's pixels, once: { w, h, data } (RGBA).
    framePixels(name) {
        if (this.pixels[name]) return this.pixels[name];
        const f = this.s.textures.getFrame('popups', name);
        const c = document.createElement('canvas');
        c.width = f.cutWidth; c.height = f.cutHeight;
        const ctx = c.getContext('2d');
        ctx.drawImage(f.source.image, f.cutX, f.cutY, f.cutWidth, f.cutHeight, 0, 0, f.cutWidth, f.cutHeight);
        return (this.pixels[name] = { w: c.width, h: c.height, data: ctx.getImageData(0, 0, c.width, c.height).data });
    }

    // The texture of a popup with these contents: its frame fitted round them, them in its middle.
    // `items`: [{ text, bold } | { icon }]. Returns its key (made once).
    texture(kind, items) {
        const key = `popup:${kind}:${items.map(i => i.icon ? `[${i.icon}]` : `${i.bold ? '*' : ''}${i.text}`).join('|')}`;
        const s = this.s;
        if (s.textures.exists(key)) return key;
        const F = this.L.font, glyphH = F.base - F.top + 1;
        // The contents' size: words on the cap height, pictures centred on it, 3 px apart.
        const parts = items.map(i => {
            if (i.icon) {
                const f = s.textures.getFrame('popups', `icon-${i.icon}`);
                return { ...i, w: f.cutWidth, h: f.cutHeight };
            }
            const adv = i.bold ? F.advBold : F.adv;
            let w = 0;
            for (const ch of i.text) w += adv[ch.codePointAt(0)] ?? adv[32];
            return { ...i, w, h: glyphH };
        });
        const cw = parts.reduce((a, q) => a + q.w, 0) + 3 * (parts.length - 1);
        const ch = Math.max(...parts.map(q => q.h));
        const [px, py] = PAD[kind];
        const B = this.L.bands[FRAME[kind]];
        const body = sizeTo(sizeTo(this.framePixels(FRAME[kind]), cw + 2 * px, 1, B.x), ch + 2 * py, 0, B.y);
        const canvas = s.textures.createCanvas(key, body.w, body.h);
        const ctx = canvas.getContext();
        ctx.putImageData(new ImageData(new Uint8ClampedArray(body.data), body.w, body.h), 0, 0);
        let x = Math.floor((body.w - cw) / 2);
        const mid = Math.floor((body.h - ch) / 2) + Math.floor(ch / 2) - (kind === 'shout' ? 0 : 1);
        for (const q of parts) {
            if (q.icon) {
                const f = s.textures.getFrame('popups', `icon-${q.icon}`);
                ctx.drawImage(f.source.image, f.cutX, f.cutY, f.cutWidth, f.cutHeight, x, mid - Math.floor(q.h / 2), q.w, q.h);
            } else {
                this.letters(ctx, q.text, x, mid - Math.floor(glyphH / 2) - F.top, q.bold, INK[kind]);
            }
            x += q.w + 3;
        }
        canvas.refresh();
        return key;
    }

    // Words in the lettering, in `colour` (the glyphs are white: drawn on a scratch canvas, coloured
    // there, then laid on).
    letters(ctx, text, x, y, bold, colour) {
        const F = this.L.font, adv = bold ? F.advBold : F.adv;
        let w = 4;
        for (const ch of text) w += adv[ch.codePointAt(0)] ?? adv[32];
        const c = document.createElement('canvas');
        c.width = w + 4; c.height = F.height;
        const g = c.getContext('2d');
        let gx = 0;
        for (const ch of text) {
            const code = ch.codePointAt(0), name = `${bold ? 'b' : 'g'}${code}`;
            if (this.s.textures.getFrame('popups', name) && code !== 32) {
                const f = this.s.textures.getFrame('popups', name);
                g.drawImage(f.source.image, f.cutX, f.cutY, f.cutWidth, f.cutHeight, gx, 0, f.cutWidth, f.cutHeight);
            }
            gx += adv[code] ?? adv[32];
        }
        g.globalCompositeOperation = 'source-in';
        g.fillStyle = colour;
        g.fillRect(0, 0, c.width, c.height);
        ctx.drawImage(c, x, y);
    }

    update() {
        const shown = this.list.filter(p => p.shown());
        shown.sort((a, b) => a.rank - b.rank);
        const view = this.s.cameras.main.worldView, placed = [];
        for (const p of shown) {
            p.place(view, placed);
            placed.push(p);
        }
        for (const p of this.list) if (!shown.includes(p)) p.hide();
    }
}

// A popup: the API of the text it replaces (`setText`, `setVisible`, `text`, `visible`,
// `setPosition`), so the game's many calls stay as they were.
class Popup {
    constructor(owner, kind, speaker, rank) {
        this.o = owner;
        this.s = owner.s;
        this.kind = kind;
        this.speaker = speaker;
        this.rank = rank;
        this._text = '';
        this._visible = false;
        this.opts = {};
        this.at = null;                 // where the game last set it (used when no head is known)
        this.y = 0;                     // a hop (`world.nudge`'s tween)
        const D = this.s.DEPTH;
        this.img = this.s.add.image(0, 0, '__DEFAULT').setOrigin(0).setDepth(D.fx + 1).setVisible(false);
        this.tail = this.s.add.graphics().setDepth(D.fx + 1.01).setVisible(false);
        this.dots = [0, 1].map(i => this.s.add.image(0, 0, 'popups', `thought-dot${i}`).setOrigin(0).setDepth(D.fx + 1).setVisible(false));
        this.s.worldLayer.add([this.img, this.tail, ...this.dots]);
        this.box = null;                // where its body is drawn now, eased
    }

    get text() { return this._text; }
    get visible() { return this._visible; }

    setText(text, opts = {}) {
        this._text = text;
        this.opts = opts;
        this.from = opts.from ?? null;          // whose words they are, when not hers (Bumbot's)
        this.key = null;
        return this;
    }

    setVisible(v) {
        if (v && !this._visible) this.box = null;           // (a new showing starts in place)
        this._visible = !!v;
        if (!v) this.hide();
        return this;
    }

    setPosition(x, y) {
        this.at = { x, y };
        return this;
    }

    setDepth() { return this; }

    // What it shows: [{ text } | { icon }], and its kind.
    contents() {
        const items = [];
        if (this.opts.icon) items.push({ icon: this.opts.icon });
        let word = '';
        const flush = () => { if (word.trim()) items.push({ text: word.trim(), bold: this.kind === 'shout' }); word = ''; };
        for (const ch of this._text) {
            const c = ch.replace('️', '');
            if (EMOJI[c]) {
                flush();
                items.push({ icon: EMOJI[c] });
                // (A lock's card, after its padlock.)
                if (c === '🔒' && this.opts.card) items.push({ icon: `card-${this.opts.card}` });
            } else if (!DROPPED.has(c) && c !== '️') word += ch;
        }
        flush();
        let kind = this.opts.kind ?? this.kind;
        if (kind === 'auto') kind = items.length && (items.every(i => i.icon) || items[0].icon) ? 'thought' : 'speech';
        return { items, kind };
    }

    shown() {
        return this._visible && (this._text || this.opts.icon);
    }

    hide() {
        this.img.setVisible(false);
        this.tail.setVisible(false);
        this.dots.forEach(d => d.setVisible(false));
    }

    // Placed over its head: its body eased toward the spot (a head that bobs with a stride does not
    // shake it), inside the view, clear of `placed`; the tail or the circles toward the head.
    place(view, placed) {
        const { items, kind } = this.contents();
        if (!this.key || this.keyKind !== kind) {
            this.key = this.o.texture(kind, items);
            this.keyKind = kind;
            this.img.setTexture(this.key);
        }
        const W = this.img.width, H = this.img.height;
        let head = this.speaker?.() ?? null;
        if (!head && this.at) head = { x: this.at.x, y: this.at.y + 10, top: this.at.y };
        if (!head) return this.hide();
        const lift = kind === 'shout' ? 4 : kind === 'plate' ? 6 : GAP + TAIL + 2;
        // (`side`: set out to one side, its tail coming at the head aslant: Bumbot's "Meow!" in her
        // arms, his head under her chin, would have it down across her face.)
        const side = this.from === 'bumbot' ? (this.s.player.flipX ? -1 : 1) : 0;
        let x = Math.round(head.x - W / 2 + side * (W / 2 + 2)), y = Math.round(head.top - lift - H);
        // Inside the view, then clear of those already placed: aside, the shorter way, then up.
        const clampX = v => Math.max(view.x + MARGIN, Math.min(view.right - MARGIN - W, v));
        x = clampX(x);
        y = Math.max(view.y + MARGIN, y);
        for (let k = 0; k < 4; k++) {
            const hit = placed.find(q => q.box && x < q.box.x + q.box.w + 2 && x + W + 2 > q.box.x && y < q.box.y + q.box.h + 2 && y + H + 2 > q.box.y);
            if (!hit) break;
            const left = hit.box.x - 2 - W, right = hit.box.x + hit.box.w + 2;
            const nx = side ? (side > 0 ? right : left) : Math.abs(left - x) <= Math.abs(right - x) ? left : right;
            if (clampX(nx) === nx) x = nx; else y = hit.box.y - 2 - H;
        }
        // (A head that bobs a px or two with a stride leaves it where it is; any more and it follows at
        // once, 2 px behind: it never lags a jump.)
        if (!this.box || this.box.w !== W || this.box.h !== H) this.box = { x, y, w: W, h: H };
        else {
            const follow = (a, b) => (Math.abs(b - a) <= 2 ? a : b - Math.sign(b - a) * 2);
            this.box = { x: follow(this.box.x, x), y: follow(this.box.y, y), w: W, h: H };
        }
        const bob = kind === 'thought' && this.opts.bob ? Math.round(Math.sin(this.s.time.now / 300) * 1.5) : 0;
        const bx = this.box.x, by = this.box.y + Math.round(this.y) + bob;
        this.img.setPosition(bx, by).setVisible(true);
        this.tail.clear().setVisible(false);
        this.dots.forEach(d => d.setVisible(false));
        if (kind === 'speech') this.drawTail(bx, by, W, H, head);
        else if (kind === 'thought') this.drawDots(bx, by, W, H, head);
    }

    // The tail: from the bubble's bottom, a wedge 7 px wide toward the middle of the head, ending GAP
    // over the head's top, in the bubble's own colours (its outline opened where they join).
    drawTail(bx, by, W, H, head) {
        const T = this.o.L.tail, g = this.tail;
        const ink = Phaser.Display.Color.HexStringToColor(T.ink).color;
        const fill = Phaser.Display.Color.HexStringToColor(T.fill).color;
        const shade = Phaser.Display.Color.HexStringToColor(T.shade).color;
        const base = by + H - 1;
        const cx = Math.max(bx + 8, Math.min(bx + W - 9, Math.round(head.x)));
        let tipY = Math.round(head.top - GAP);
        tipY = Math.max(base + 3, Math.min(base + TAIL + 6, tipY));
        const k = (tipY - base) / Math.max(1, head.y - base);
        const tipX = Math.round(cx + (head.x - cx) * Math.min(1, k));
        // (Where they join: the outline and the shade under it opened.)
        g.fillStyle(fill, 1).fillRect(cx - 2, base - 2, 5, 3);
        for (let r = base + 1; r <= tipY; r++) {
            const t = (r - base) / (tipY - base);
            const l = Math.round((cx - 3) + (tipX - (cx - 3)) * t), rr = Math.round((cx + 3) + (tipX - (cx + 3)) * t);
            if (rr - l >= 2) {
                g.fillStyle(fill, 1).fillRect(l + 1, r, rr - l - 1, 1);
                g.fillStyle(shade, 1).fillRect(rr - 1, r, 1, 1);
            }
            g.fillStyle(ink, 1).fillRect(l, r, 1, 1).fillRect(rr, r, 1, 1);
        }
        g.setVisible(true);
    }

    // A thought's two circles, the bigger by the cloud, the smaller nearer the head, on the line to it.
    drawDots(bx, by, W, H, head) {
        const sx = Math.max(bx + 6, Math.min(bx + W - 6, head.x)), sy = by + H - 2;
        const ex = head.x, ey = head.top - GAP;
        if (ey - sy < 4) return;
        [0.4, 0.82].forEach((f, i) => {
            const d = this.dots[i];
            d.setPosition(Math.round(sx + (ex - sx) * f - d.width / 2), Math.round(sy + (ey - sy) * f - d.height / 2)).setVisible(true);
        });
    }
}

// `heads` (tools/build_heads.py, kept by clip: { sheet: { clip: [[x, y, top] | null, ...] } }) laid on
// each sheet's frame numbers from its own data (`<sheet>-meta`; Bumbot's in her arms from her-cat's): a
// clip added to a sheet moves nothing, and a clip remade with another count of frames is left out (no
// head: the popup stands over where she is) until the tool is run again.
function frameHeads(scene, byClip) {
    const out = {};
    for (const [sheet, clips] of Object.entries(byClip)) {
        const meta = scene.cache.json.get(`${sheet === 'her-cat-bumbot' ? 'her-cat' : sheet}-meta`);
        if (!meta) continue;
        const anims = sheet === 'people'
            ? Object.fromEntries(Object.entries(meta.people ?? {}).flatMap(([who, m]) => [
                ...Object.entries(m.anims ?? {}).map(([c, v]) => [`${who}.${c}`, v]),
                // (Their still poses, single frames outside the clips.)
                ...['stand', 'front', 'back'].filter(k => Number.isInteger(m[k])).map(k => [`${who}.@${k}`, [m[k]]]),
            ]))
            : meta.anims ?? {};
        const table = out[sheet] = {};
        for (const [clip, row] of Object.entries(clips)) {
            const frames = anims[clip];
            if (!Array.isArray(frames) || frames.length !== row.length) continue;
            frames.forEach((f, k) => { if (row[k]) table[f] = row[k]; });
        }
    }
    return out;
}

// A frame sized along `axis` (1 across, 0 down) to at least `target` px by its band [c, c + p)
// (tools/build_popups.py: the two edge lines most alike, a whole bump or spike of a cloud or a burst):
// repeated as often as it takes, or taken out once when it is too big. `img`: { w, h, data }.
export function sizeTo(img, target, axis, [c, p]) {
    const n = axis === 1 ? img.w : img.h, lines = [];
    if (target < n) {
        if (n - p < target) return img;
        for (let i = 0; i < n; i++) if (i < c || i >= c + p) lines.push(i);
        return remap(img, lines, axis);
    }
    const times = Math.ceil((target - n) / p);
    for (let i = 0; i < c + p; i++) lines.push(i);
    for (let k = 0; k < times; k++) for (let i = c; i < c + p; i++) lines.push(i);
    for (let i = c + p; i < n; i++) lines.push(i);
    return remap(img, lines, axis);
}

// The lines kept, in order: a band repeated once more, or taken out.
function remap(img, lines, axis) {
    const w = axis === 1 ? lines.length : img.w, h = axis === 1 ? img.h : lines.length;
    const data = new Uint8ClampedArray(w * h * 4);
    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            const sx = axis === 1 ? lines[x] : x, sy = axis === 1 ? y : lines[y];
            const si = (sy * img.w + sx) * 4, di = (y * w + x) * 4;
            data[di] = img.data[si]; data[di + 1] = img.data[si + 1]; data[di + 2] = img.data[si + 2]; data[di + 3] = img.data[si + 3];
        }
    }
    return { w, h, data };
}
