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
    coffee: { frame: 'coffee-cup', ms: 50000 },
    cocktail: { frame: 'umbrella-cocktail' },
    cake: { thing: 'wedding-cake', fragile: true },
    canister: { draw: 'canister', heavy: true, bare: true },
    // The deliveries (plan-the-rest §5 3.2), each a tray with its own rule. 1, the vase of flowers (deck 8 midships): a
    // narrower tray (`tray`, px; the user, 2026-11-23), the bouquet before her face, and round the screen the flowers
    // she sees the hallway through (`view`, the user's frame: `assets/source/things/delivery/`).
    vase: { thing: 'delivery-vase', tray: 18, view: 'flower-frame' },
};

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
        this.items = [top];
        if (!load.bare) this.items.unshift(s.add.image(0, 0, load.tray ? `tray-${load.tray}` : 'tray').setOrigin(0.5, 1).setDepth(D.player + 0.011));
        this.world.add(this.items);
        this.world.carry = { kind, ...load };
        sfx.take();
        this.world.refresh();
        this.update();
    }

    drop() {
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
        const away = p.x >= fromX ? 1 : -1;
        const flying = this.items;
        rumble('spill');
        // (The steel canister rings; anything else is crockery, or lands like it.)
        if (this.kind === 'canister') sfx.clang();
        else if (['cake', 'cone', 'stub'].includes(this.kind)) sfx.splat();
        else sfx.crash();
        this.items = [];
        this.kind = null;
        this.world.carry = null;
        // (Each turned about its middle and set down on the floor she stands on by how tall it stands once turned, never
        // into it (the user, 2026-11-23: the vase sank through the floor): the tray upside down, what was on it on its
        // side.)
        const floor = s.grounded ? p.y : (s.takeoffY ?? p.y);
        flying.forEach((img, k) => {
            const tray = img.texture.key.startsWith('tray') && flying.length > 1;
            const turn = tray ? 180 : 270, half = (turn % 180 ? img.width : img.height) / 2;
            img.setOrigin(0.5, 0.5).setPosition(img.x, img.y - img.height / 2);
            s.tweens.add({ targets: img, x: img.x + away * (26 + k * 10), angle: away * turn, duration: 520 });
            s.tweens.add({ targets: img, y: img.y - 18, duration: 180, ease: 'Quad.easeOut', yoyo: false,
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
        const [dx, up] = hold ? hold[1] : [14, 31];
        const x = Math.round(p.x + front * dx), y = Math.round(p.y - up + (s.grounded ? 0 : -1));
        let top = y;
        for (const img of this.items) {
            img.setPosition(x, top).setVisible(p.visible && s.mode !== 'lift');
            top -= img.texture.key.startsWith('tray') ? 3 : 0;
        }
        if (LOADS[this.kind].fragile && this.sway(x)) return;
        // A hot cup steams (less as it cools).
        if (this.kind === 'coffee' && p.visible && s.time.now > (this.steamAt ?? 0)) {
            this.steamAt = s.time.now + 260 + (1 - (this.left() ?? 1)) * 700;
            const wisp = s.add.rectangle(x + Phaser.Math.Between(-1, 1), top - 6, 1, 3, 0xffffff, 0.8).setDepth(s.DEPTH.player + 0.013);
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
