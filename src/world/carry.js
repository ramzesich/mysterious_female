// Carrying (GAME_DESIGN.md §6.1.2): a tray in her hands. Tray rules: stairs and elevators only (no
// ladders, trunks, wall jumps, crawling, swimming or the dash: the scene and the verbs ask
// `world.carry`), a low hop instead of a jump, and a bump from a hazard or a person spills it with a
// clatter, never a scare: she fetches another where she got it, which always has more. Some loads
// melt or cool (a meter on the HUD). E hands the thing over to whoever wants it.
// A fragile load (the wedding cake, region 9) has no clock: it sways. Every start, stop, turn and
// landing sets it swaying more, standing or walking steadily lets it settle, and swayed too far it
// goes over: the meter on the HUD is how steady it stands.

import { sfx } from '../sfx.js';
import { rumble } from '../rumble.js';
import { t } from '../lang.js';
import { VIEW } from '../config.js';

// What a tray can hold: how it is drawn (a piece of the ship's atlas on the tray, or drawn here),
// whether it runs out (`ms`: a melting cone, a cooling cup), whether it is too heavy to hop with.
export const LOADS = {
    lunch: { draw: 'cloche' },
    cone: { draw: 'cone', ms: 45000, bare: true },
    stub: { draw: 'stub', ms: 45000, bare: true },
    coffee: { frame: 'coffee-cup', ms: 50000, hot: true },
    cocktail: { frame: 'umbrella-cocktail' },
    cake: { thing: 'wedding-cake', fragile: true },
    canister: { draw: 'canister', heavy: true, bare: true },
    // The deliveries (plan-the-rest §5 3.2), each a tray with its own rule. 1, the vase of flowers (deck 8 midships): a
    // narrower tray (`tray`, px; the user, 2026-11-23), the bouquet before her face, and round the screen the flowers
    // she sees the hallway through (`view`, the user's frame: `assets/source/things/delivery/`).
    vase: { thing: 'delivery-vase', tray: 18, view: 'flower-frame' },
    // 2, the pot of tea (deck 10 midships): it cools as the coffee does, the HUD's meter orange to blue, steam from its
    // spout; a tray 22 px long and 3 tall (the user, 2026-11-23: "a bit thinner"); the pot drawn by hand
    // (`assets/source/things/delivery/draw_teapot.py`), its spout the way she faces.
    tea: { thing: 'delivery-teapot', tray: 22, ms: 45000, hot: true, spout: [9, 7] },
    // 3, the stack of pillows (deck 9 aft): on her forearms, no tray (the user, 2026-11-23: her tray pose first); the low
    // hop as every load (the user: "why does she jump too high?", the plan's full jump dropped); three pillows, each a piece
    // (`stack`, on the one under it), so that a spill scatters them (`soft`: they tumble flat; the user: "they fall down as
    // a single block"); the top one slides off ahead of her when she stops short from a run (`slides`), and E at it puts it
    // back (her crouch, `carry-crouch`).
    pillows: { thing: 'delivery-pillow-bottom', stack: ['delivery-pillow-mid', 'delivery-pillow-top'], bare: true, soft: true, slides: true },
};

// Stopping short with the pillows: a run of at least `runS` s at more than `fast` px/s, then her speed under `still` px/s on
// the floor; the top pillow slides `ahead` px on before it lands.
export const SLIDE = { runS: 0.3, fast: 100, still: 5, ahead: 14 };

// Her crouch with a load (`carry-crouch`'s three frames): where the load stands in each, as `HOP_HOLDS` (her fists measured:
// 4, 8 and 13 px lower than standing), and each frame's time going down (back up the same, reversed).
const CROUCH_HOLDS = [[14, 27], [14, 23], [14, 18]];
const CROUCH_MS = 90;

// Her hop with a load (`carry-rise`, `carry-apex`, `carry-fall` in her sheet): where the load stands in each, [px ahead of
// her middle, px up from her feet], by her fists (the user, 2026-11-23: it hung in the air before her as she jumped).
const HOP_HOLDS = [['carry-rise', [7, 28]], ['carry-apex', [10, 19]], ['carry-fall', [11, 18]]];

// A fragile load's sway: what each start or stop, turn on the move and landing adds (1: it goes
// over), and how much settles in a second.
export const SWAY = { startStop: 0.26, turn: 0.42, landing: 0.5, settle: 0.24 };

export class Carry {
    constructor(world) {
        this.world = world;
        this.scene = world.scene;
        this.kind = null;
        this.items = [];
    }

    textures() {
        const s = this.scene;
        const make = (key, w, h, draw) => {
            if (s.textures.exists(key)) return;
            const g = s.make.graphics({ x: 0, y: 0 }, false);
            draw(g);
            g.generateTexture(key, w, h);
            g.destroy();
        };
        make('tray', 26, 4, g => {
            g.fillStyle(0x2e222f, 1).fillRect(1, 0, 24, 4);
            g.fillStyle(0xc7dcd0, 1).fillRect(2, 1, 22, 2);
            g.fillStyle(0xffffff, 1).fillRect(3, 1, 8, 1);
        });
        // (A narrower one, the same drawing: the vase's.)
        make('tray-18', 18, 4, g => {
            g.fillStyle(0x2e222f, 1).fillRect(1, 0, 16, 4);
            g.fillStyle(0xc7dcd0, 1).fillRect(2, 1, 14, 2);
            g.fillStyle(0xffffff, 1).fillRect(3, 1, 6, 1);
        });
        // (The teapot's: as long as the pot and its cup, a row thinner.)
        make('tray-22', 22, 3, g => {
            g.fillStyle(0x2e222f, 1).fillRect(1, 0, 20, 3);
            g.fillStyle(0xc7dcd0, 1).fillRect(2, 1, 18, 1);
            g.fillStyle(0xffffff, 1).fillRect(3, 1, 6, 1);
        });
        make('load-cloche', 18, 12, g => {
            g.fillStyle(0x2e222f, 1).fillEllipse(9, 12, 18, 22);
            g.fillStyle(0xc7dcd0, 1).fillEllipse(9, 12, 16, 20);
            g.fillStyle(0xffffff, 1).fillRect(5, 4, 3, 2);
            g.fillStyle(0x2e222f, 1).fillRect(7, 0, 4, 3);
            g.fillStyle(0xf9c22b, 1).fillRect(8, 1, 2, 1);
        });
        // A soft serve in its cone: a proper swirl, and a stub.
        make('load-cone', 9, 17, g => {
            g.fillStyle(0x2e222f, 1).fillTriangle(0, 8, 9, 8, 4.5, 17).fillRect(1, 5, 7, 4).fillRect(2, 2, 5, 3).fillRect(3, 0, 3, 2);
            g.fillStyle(0xe6904e, 1).fillTriangle(1, 9, 8, 9, 4.5, 16);
            g.fillStyle(0xab6f3a, 1).fillRect(3, 10, 1, 1).fillRect(5, 11, 1, 1).fillRect(4, 13, 1, 1);
            g.fillStyle(0xffffff, 1).fillRect(2, 6, 5, 2).fillRect(3, 3, 3, 3).fillRect(4, 1, 1, 2);
            g.fillStyle(0xf9d9c8, 1).fillRect(2, 7, 5, 1).fillRect(3, 5, 3, 1);
        });
        make('load-stub', 9, 12, g => {
            g.fillStyle(0x2e222f, 1).fillTriangle(0, 3, 9, 3, 4.5, 12).fillRect(2, 1, 5, 3);
            g.fillStyle(0xe6904e, 1).fillTriangle(1, 4, 8, 4, 4.5, 11);
            g.fillStyle(0xab6f3a, 1).fillRect(3, 5, 1, 1).fillRect(5, 6, 1, 1).fillRect(4, 8, 1, 1);
            g.fillStyle(0xffffff, 1).fillRect(3, 2, 3, 2);
        });
        make('load-canister', 16, 22, g => {
            g.fillStyle(0x2e222f, 1).fillRect(0, 2, 16, 20).fillRect(4, 0, 8, 3);
            g.fillStyle(0xc7dcd0, 1).fillRect(1, 3, 14, 18);
            g.fillStyle(0xf68181, 1).fillRect(1, 9, 14, 6);
            g.fillStyle(0xffffff, 1).fillRect(3, 4, 2, 16);
        });
    }

    // E at a source: the thing is in her hands.
    take(kind) {
        const s = this.scene, D = s.DEPTH, load = LOADS[kind];
        this.drop();
        this.textures();
        this.kind = kind;
        this.until = load.ms ? s.time.now + load.ms : null;
        const top = load.thing ? s.add.image(0, 0, 'things', load.thing)
            : load.frame ? s.add.image(0, 0, 'shipart', load.frame) : s.add.image(0, 0, `load-${load.draw}`);
        top.setOrigin(0.5, 1).setDepth(D.player + 0.012);
        this.wobble = 0;
        this.st = null;
        this.run = 0;
        this.items = [top];
        // (A stack of pieces, each on the one under it.)
        for (const piece of load.stack ?? []) this.items.push(s.add.image(0, 0, 'things', piece).setOrigin(0.5, 1));
        if (!load.bare) this.items.unshift(s.add.image(0, 0, load.tray ? `tray-${load.tray}` : 'tray').setOrigin(0.5, 1).setDepth(D.player + 0.011));
        this.world.add(this.items);
        this.world.carry = { kind, ...load };
        sfx.take();
        this.world.refresh();
        this.update();
    }

    drop() {
        this.clearFallen();
        this.items.forEach(i => i.destroy());
        this.items = [];
        this.kind = null;
        this.world.carry = null;
    }

    // Handed over: gone from her hands (the story takes it from there).
    give() {
        const kind = this.kind;
        this.drop();
        this.world.refresh();
        return kind;
    }

    // A bump: the tray goes flying, with a clatter. Never a scare. Whatever she has on her: no
    // tangerine saves a tray (the user, 2026-11-19; docs/plan-the-rest.md §3 1.2a). `own`: her own
    // feet (a load swayed over, into a pool with it). (`what`, `opts`: what hit her, as
    // `scareContact`'s; only the blink after a gull's take keeps it.)
    spill(fromX, own = false, what = null, opts = {}) {
        if (!this.kind) return;
        const s = this.scene, p = s.player;
        if (!own && s.isSafe()) return;
        this.clearFallen();
        const away = p.x >= fromX ? 1 : -1;
        const flying = this.items, kind = this.kind;
        rumble('spill');
        // (The steel canister rings; pillows land soft; anything else is crockery, or lands like it.)
        if (this.kind === 'canister') sfx.clang();
        else if (LOADS[kind].soft) sfx.flump();
        else if (['cake', 'cone', 'stub'].includes(this.kind)) sfx.splat();
        else sfx.crash();
        this.items = [];
        this.kind = null;
        this.world.carry = null;
        // (Each turned about its middle and set down on the floor she stands on by how tall it stands once turned, never
        // into it (the user, 2026-11-23: the vase sank through the floor): the tray upside down, what was on it on its
        // side.)
        const floor = s.grounded ? p.y : (s.takeoffY ?? p.y);
        // (Soft things, the pillows, tumble apart and land flat, each its own way: the higher in the stack, the further.)
        const soft = LOADS[kind]?.soft;
        flying.forEach((img, k) => {
            const tray = img.texture.key.startsWith('tray') && flying.length > 1;
            const turn = tray || soft ? 180 : 270, half = (turn % 180 ? img.width : img.height) / 2;
            img.setOrigin(0.5, 0.5).setPosition(img.x, img.y - img.height / 2);
            const far = soft ? [10, 34, 58][k] ?? 30 : 26 + k * 10, rise = soft ? 12 + k * 9 : 18;
            s.tweens.add({ targets: img, x: img.x + away * far, angle: away * (soft ? turn * (k % 2 ? 1 : 2) : turn), duration: soft ? 560 + k * 90 : 520 });
            s.tweens.add({ targets: img, y: img.y - rise, duration: 180, ease: 'Quad.easeOut', yoyo: false,
                onComplete: () => s.tweens.add({ targets: img, y: floor - half, duration: 300, ease: 'Quad.easeIn',
                    onComplete: () => s.tweens.add({ targets: img, alpha: 0, delay: 700, duration: 300, onComplete: () => img.destroy() }) }) });
        });
        s.smash(p.x + away * 20, p.y - 8, false);      // (its own sound is above)
        // A start, no more: she is knocked back a step. (`still`: a hit that plays its own gag as well, the trays.)
        if (!opts.still) {
            p.body.velocity.x = away * 120;
            p.body.velocity.y = -90;
            this.world.say(t('say.oops'), 700);
        }
        this.world.refresh();
    }

    // A load she sees the world through (`view`: the vase's flowers): a picture the screen's size round its edges, on the
    // screen's own layer under the HUD (so a look-out's zoom leaves it as it is), faded in as she takes it and out as it
    // leaves her hands; not while something is seen close, nor in a view zoomed out from her.
    showView() {
        const s = this.scene, key = this.kind && LOADS[this.kind].view;
        // (Never in a view zoomed out from her, a look-out's or the outside view: the user, 2026-11-23.)
        const zoomedOut = !!s.overview || s.cameras.main.zoom < VIEW.zoom - 0.01;
        const on = !!key && !s.viewing && !s.intro && !zoomedOut;
        if (on && (!this.view || this.view.texture.key !== key)) {
            this.view?.destroy();
            this.view = s.add.image(0, 0, key).setOrigin(0).setScale(VIEW.width / s.textures.get(key).getSourceImage().width).setAlpha(0);
            s.uiLayer.addAt(this.view, 0);
        }
        if (!this.view) return;
        const dt = Math.min(0.05, s.game.loop.delta / 1000);
        this.view.alpha = zoomedOut ? 0 : on ? Math.min(1, this.view.alpha + dt / 0.35) : Math.max(0, this.view.alpha - dt / 0.35);
        this.view.setVisible(this.view.alpha > 0);
    }

    // Each frame: the tray rides in front of her, at her hands; a load that runs out is lost.
    update() {
        if (!this.kind) return;
        const s = this.scene, p = s.player;
        const front = p.flipX ? -1 : 1;
        // (In her hop's three poses the load is where her fists are in that frame, px ahead of her middle and up:
        // tucked, her hands come nearer her feet; `assets/source/her/carry-jump/`.)
        const hold = HOP_HOLDS.find(([pose]) => s.herFrames?.[pose] === p.frame.name);
        // (Turned to face us, in the lift and the like, the load is at her middle in front of her; her back to us, at her
        // middle behind her; in profile again, at her hands. The user, 2026-11-23.)
        const fr = p.texture.key === 'her' ? Number(p.frame.name) : NaN;
        const F = s.herFrames ?? {};
        const facing = fr === F['carry-front'] || fr === F.front ? 1 : fr === F['carry-back'] || fr === F.back ? -1 : 0;
        const [dx, up] = facing ? [0, 31] : this.crouchHold ?? (hold ? hold[1] : [14, 31]);
        const x = Math.round(p.x + front * dx), y = Math.round(p.y - up + (s.grounded ? 0 : -1));
        let top = y;
        // (Drawn as she is, one step nearer us, the tray under its load: her depth wherever she is, behind a flight's wall or a
        // deck's floor on the stairs, in a pool, and her blink after a scare. The user, 2026-11-23: the vase was drawn over
        // the decks while she went up the stairs behind them. Her back to us, one step behind her, the load still over its
        // tray.)
        const n = this.items.length;
        const near = (img, k) => img.setDepth(p.depth + 0.001 * (facing < 0 ? k - n : k + 1)).setAlpha(p.alpha);
        this.items.forEach(near);
        for (const img of this.items) {
            // (Turned the way she faces: the teapot's spout ahead of her.)
            img.setPosition(x, top).setFlipX(p.flipX).setVisible(p.visible);
            // (What is on a tray stands on its top row; a stack's top on the rest.)
            top -= img.texture.key.startsWith('tray') ? img.height - 1 : LOADS[this.kind].stack ? img.height : 0;
        }
        this.slides();
        if (LOADS[this.kind].fragile && this.sway(x)) return;
        // A hot cup or pot steams (less as it cools): a pot from its spout's tip (`spout`, px ahead of its middle and up).
        const load = LOADS[this.kind];
        if (load.hot && p.visible && s.time.now > (this.steamAt ?? 0)) {
            this.steamAt = s.time.now + 260 + (1 - (this.left() ?? 1)) * 700;
            const [sx, sy] = load.spout ?? [0, 6];
            const wisp = s.add.rectangle(x + front * sx + Phaser.Math.Between(-1, 1), top - sy - 2, 1, 3, 0xffffff, 0.8).setDepth(this.items.at(-1).depth + 0.0005);
            this.world.add([wisp]);
            s.tweens.add({ targets: wisp, y: wisp.y - 12, x: wisp.x + Phaser.Math.Between(-3, 3), alpha: 0, duration: 700, onComplete: () => wisp.destroy() });
        }
        if (this.until && s.time.now > this.until) {
            // Melted, or gone cold: it is no use now.
            const kind = this.kind;
            this.drop();
            this.world.say(kind === 'cone' || kind === 'stub' ? '💧' : '❄', 900);
            this.world.refresh();
        }
    }

    // The pillows' rule: stopped short from a run, the top pillow slides on ahead of her and lands on the floor.
    slides() {
        const s = this.scene, p = s.player, load = LOADS[this.kind];
        if (!load.slides || this.fallen || s.mode !== 'play') { this.run = 0; return; }
        const dt = Math.min(0.05, s.game.loop.delta / 1000), vx = Math.abs(p.body.velocity.x);
        if (vx > SLIDE.fast) this.run += dt;
        else if (vx < SLIDE.still && s.grounded) {
            if (this.run >= SLIDE.runS) this.slideOff();
            this.run = 0;
        }
    }

    slideOff() {
        const s = this.scene, p = s.player, w = this.world;
        const img = this.items.pop(), dir = p.flipX ? -1 : 1, floor = p.y;
        const x = Math.round(img.x + dir * SLIDE.ahead);
        img.setDepth(s.DEPTH.player - 0.01);          // (on the floor, behind her as she crosses it)
        s.tweens.add({ targets: img, x, duration: 420, ease: 'Quad.easeOut' });
        s.tweens.add({ targets: img, y: img.y - 4, duration: 120, ease: 'Quad.easeOut',
            onComplete: () => s.tweens.add({ targets: img, y: floor, duration: 260, ease: 'Quad.easeIn', onComplete: () => sfx.at(x, floor).flump() }) });
        w.say(t('say.whoa'), 700);
        // (E at it: she crouches and it goes back on top.)
        this.fallen = { id: 'pillow_fallen', x, y: floor, route: s.route, items: [img], reach: 36, interact: () => this.pickUp() };
        w.things.push(this.fallen);
    }

    clearFallen() {
        if (!this.fallen) return;
        const w = this.world, i = w.things.indexOf(this.fallen);
        if (i >= 0) w.things.splice(i, 1);
        this.fallen.items.forEach(img => img.destroy());
        this.fallen = null;
    }

    // E at the fallen pillow: she crouches with the stack, the pillow goes back on top, she stands.
    pickUp() {
        const s = this.scene, p = s.player, w = this.world, f = this.fallen;
        if (!f || !this.kind || w.picking) return false;
        w.picking = true;
        const frames = s.cache.json.get('her-meta').anims['carry-crouch'];
        p.setFlipX(f.x < p.x);
        w.cut(async () => {
            const at = k => { p.anims.stop(); p.setTexture('her', frames[k]); this.crouchHold = CROUCH_HOLDS[k]; this.update(); };
            for (const k of [0, 1, 2]) { at(k); await w.wait(CROUCH_MS); }
            // (Down: the pillow comes up from the floor onto the stack, in a little arc.)
            const img = f.items[0], rest = this.items.at(-1);
            w.things.splice(w.things.indexOf(f), 1);
            this.fallen = null;
            img.setDepth(p.depth + 0.003).setFlipX(p.flipX);
            const tx = rest.x, ty = rest.y - rest.height;
            sfx.flump();
            await w.tween({ targets: img, x: { value: tx, ease: 'Sine.easeInOut' }, y: { value: ty, ease: 'Back.easeOut' }, duration: 220 });
            img.setPosition(tx, ty);
            this.items.push(img);
            this.update();
            await w.wait(110);
            for (const k of [2, 1, 0]) { at(k); await w.wait(CROUCH_MS); }
            this.crouchHold = null;
            w.picking = false;
        });
        return true;
    }

    // A fragile load's sway (the cake): what her feet do sets it going, time settles it. True if
    // it has gone over.
    sway(x) {
        const s = this.scene, p = s.player, dt = Math.min(0.05, s.game.loop.delta / 1000);
        const vx = p.body.velocity.x, moving = Math.abs(vx) > 20, dir = Math.sign(vx);
        this.st ??= { moving, dir, since: 0, air: 0 };
        const st = this.st;
        if (s.mode === 'play') {
            // (A start or a stop counts once it has lasted a moment, a landing after a real hop: her
            // speed and her footing both flicker for a frame now and then.)
            st.since = moving !== st.moving ? st.since + dt : 0;
            if (st.since > 0.07) {
                st.moving = moving;
                st.since = 0;
                if (dir) st.dir = dir;
                this.wobble += SWAY.startStop;
            } else if (moving && st.moving && dir !== st.dir) {
                st.dir = dir;
                this.wobble += SWAY.turn;
            }
            if (!s.grounded) st.air += dt;
            else {
                if (st.air > 0.12) this.wobble += SWAY.landing;
                st.air = 0;
            }
        }
        this.wobble = Math.max(0, this.wobble - SWAY.settle * dt);
        // (Its warning, once each time it passes two thirds of the way over.)
        if (this.wobble > 0.66 && !this.warned) sfx.wobble();
        this.warned = this.wobble > 0.66;
        const top = this.items.at(-1), k = Math.min(1, this.wobble);
        top.setAngle(Math.sin(s.time.now / (110 - 50 * k)) * 13 * k).setX(x + Math.sin(s.time.now / (110 - 50 * k)) * 2 * k);
        if (this.wobble < 1) return false;
        this.world.say(t('say.ohno'), 900);
        this.spill(p.x - (p.flipX ? -1 : 1) * 10, true);
        return true;
    }

    // How much of a melting or cooling load is left, 1 to 0 (for a fragile one: how steady it
    // stands); null for one that keeps.
    left() {
        if (this.kind && LOADS[this.kind].fragile) return Math.max(0, 1 - this.wobble);
        if (!this.kind || !this.until) return null;
        const ms = LOADS[this.kind].ms;
        return Math.max(0, (this.until - this.scene.time.now) / ms);
    }
}
