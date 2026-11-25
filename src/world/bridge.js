// Near-catch 6 (GAME_DESIGN.md §6.1, region 9; remade 2026-11-25, docs/near-catch-6-remake-log.md), mixed into the
// Story: the bridge's forward end on deck 10. Bumbot washes on the console's aft end, the alarm station beside him;
// behind him, in front of the console, the security officer frozen mid-creep on tiptoe, his net raised; under the
// ceiling at the forward end, the escape hatch, shut. At the sight of them she is taken: she goes down on her heels,
// holds out a hand and calls him softly (the user: "Just don't use the cry as a call"); he looks, gets up and hops
// onto the station, over its big red button, toward her hand; the officer, seeing her get him first, hurries after
// him and swings; Bumbot springs, and the hoop comes down on the button where he stood: the alarm. It lets the
// hatch's lid drop and its ladder down; Bumbot, back on the console behind the officer, runs along it, leaps onto
// the ladder and climbs it into the hatch; the officer tugs his net free of the station and goes over backward, the
// net over his own head. She looks up after Bumbot, and is hers again, facing the ladder.
//
// One clock (`T`, ms of the game's time since the scene began) and everything a function of it, on the ship scene's
// scripted update (the storyboard's own clock: assets/source/bridge/storyboard.py). Where things stand and when:
// `BRIDGE` in src/config.js; the pieces and the clips: tools/build_bridge.py, assets/ship/bridge/bridge.json.
//
// Also here: the alarm's light and sound, from the scene until Bumbot is caught; and her way out, up the ladder into
// the hatch (her picture cut between the hatch's mouth and the balcony's floor over it, the bridge kept open until
// she is out: `hatchCut`, `hatchDeck`).

import { BRIDGE } from '../config.js';
import { sfx } from '../sfx.js';
import { rumble } from '../rumble.js';
import { t } from '../lang.js';

const near = (s, x, y, rx, ry) => Math.abs(s.player.x - x) < rx && Math.abs(s.player.y - y) < ry;

export const bridge = {
    setupBridge() {
        const s = this.scene, w = this.world, D = s.DEPTH, R = this.B?.bridge;
        const cat = s.cats.find(c => c.flag === 'bb6');
        if (!cat || !R || !s.textures.exists('bridge-net')) return;
        const L = s.cache.json.get('bridge-layout'), F = R.y, C = L.clips;
        cat.custom = true;              // (its own scene: not the ship scene's `nearCatch`)
        const img = (key, x, y, depth) => s.add.image(x, y, key).setOrigin(0).setDepth(depth);
        // The alarm station, hard against the console's aft end; its beacon's lamp lit, and a glow round it.
        const sx = R.stationX + L.station.dx, sy = F + L.station.dy;
        const station = img('bridge-station', sx, sy, D.decor + 0.1);
        const lamp = img('bridge-beacon', sx + L.station.lamp[0], sy + L.station.lamp[1], D.decor + 0.11).setVisible(false);
        const glow = s.add.graphics().setDepth(D.decor + 0.105);
        // The escape hatch: its ladder (behind her as she climbs it), its collar over the ladder's top, its lid.
        const hx = R.hatchX, mouth = R.ceil + L.collar.dy + L.collar.h;
        const ladder = img('bridge-ladder', hx + L.ladder.dx, R.ceil + L.ladder.top, D.ladders).setVisible(false);
        const collar = img('bridge-collar', hx + L.collar.dx, R.ceil + L.collar.dy, D.ladders + 0.02);
        const lid = s.add.sprite(hx + L.lid.dx - L.lid.hinge[0], R.ceil + L.lid.dy - L.lid.hinge[1], 'bridge-lid', 0).setOrigin(0).setDepth(D.ladders + 0.01);
        // The officer, in his own clips: one sprite, its strip and frame set by the clock.
        const officer = s.add.sprite(0, 0, 'bridge-stalk', 0).setOrigin(0).setDepth(D.props + 0.05);
        // Bumbot's climb, where its pictures were made; cut at the hatch's mouth as he goes in.
        const climb = s.add.sprite(C.climb.x0, C.climb.y0, 'bridge-climb', 0).setOrigin(0).setDepth(D.props).setVisible(false);
        // Her own picture's top, over the balcony's floor, as she climbs out (`updateBridge`).
        const top = s.add.image(0, 0, 'her').setVisible(false);
        // The alarm's red light over the bridge.
        const wash = s.add.rectangle(R.x0, F - 128, R.x1 - R.x0, 128, 0xe83b3b, 0).setOrigin(0).setDepth(D.player + 0.3);
        w.add([station, lamp, glow, ladder, collar, lid, officer, climb, top, wash]);
        this.bridge = { cat, R, L, C, F, station, lamp, glow, ladder, collar, lid, officer, climb, top, wash, mouth,
                        sat: cat.sprite.y, alarm: false, state: null };
        this.bridgeShow();
    },

    // Where a clip's frame lies: the officer's by his own x (`stalk`, `creep`), or where its pictures were made.
    officerAt(strip, frame, x) {
        const q = this.bridge, c = q.C[strip], o = q.officer;
        if (o.texture.key !== `bridge-${strip}`) o.setTexture(`bridge-${strip}`, frame);
        else if (o.frame.name !== frame) o.setFrame(frame);
        if ('x' in c) o.setPosition(Math.round(x) - c.x, q.F - c.floor - 1);
        else o.setPosition(c.x0, c.y0);
        o.setVisible(true);
    },

    // The ladder let down out of the collar: its lowest `k` of its length shown, hung from the collar.
    ladderDown(k) {
        const q = this.bridge, l = q.ladder, shown = Math.round(l.height * Math.min(1, Math.max(0, k)));
        l.setVisible(shown > 0).setCrop(0, l.height - shown, l.width, shown).setY(q.R.ceil + q.L.ladder.top - (l.height - shown));
    },

    // As it stands outside the scene: before he has been (the hatch shut, the officer frozen mid-creep), or after (the
    // button down, the hatch open, its ladder down, the officer sat under his own net until Bumbot is caught).
    bridgeShow() {
        const q = this.bridge, P = this.P;
        if (!q || q.playing) return;
        const after = P.has('bb6'), open = after || P.flagSet('alarm'), caught = P.has('catch');
        const state = `${after}${open}${caught}`;
        if (state === q.state) return;
        q.state = state;
        q.station.setTexture(after ? 'bridge-station-down' : 'bridge-station');
        q.lid.setFrame(open ? q.L.lid.frames - 1 : 0);
        this.ladderDown(open ? 1 : 0);
        q.climb.setVisible(false);
        q.officer.setVisible(!caught);
        if (!caught) this.officerAt(after ? 'netted' : 'stalk', 0, q.R.stationX + BRIDGE.officer0);
        if (after) {
            q.cat.gone = q.cat.away = true;
            q.cat.sprite.setVisible(false);
        }
    },

    // The deck the view keeps while she climbs out of the hatch: the bridge's, until she stands on the balcony (the
    // ship scene's cut-away would close the bridge's side over her legs half way up: `world.deckHeld`).
    hatchDeck() {
        const q = this.bridge, s = this.scene;
        if (!q || s.mode !== 'ladder' || Math.abs(s.player.x - q.R.hatchX) > 9 || s.player.y <= q.R.ceil - 14) return null;
        return 10;
    },

    // Her picture on the hatch's ladder: nothing of her between the hatch's mouth and the balcony's floor over it (she
    // is inside the collar and the deck's slab: behind its near side). The ship scene cuts her picture to what is under
    // the mouth (`world.herCut`); what is over the balcony's floor, behind its bulwark, is drawn here (`updateBridge`).
    hatchCut() {
        const q = this.bridge, s = this.scene, p = s.player;
        if (!q || s.route !== 'inside' || Math.abs(p.x - q.R.hatchX) > 9 || p.y > q.F || p.y <= q.R.ceil - 14) return null;
        if (p.y - 60 > q.mouth) return null;            // (all of her under the mouth still)
        return [-Infinity, Infinity, q.mouth];
    },

    updateBridge(dt, time) {
        const q = this.bridge, s = this.scene, P = this.P;
        if (!q) return;
        const p = s.player, R = q.R, F = q.F;
        this.bridgeShow();
        // --- Outside the scene: the officer's wobble before, his sigh after; the picture given back after the scene.
        if (!q.playing && q.officer.visible) {
            if (P.has('bb6')) {
                const u = time % BRIDGE.sighEvery;
                this.officerAt('netted', u < 8 * BRIDGE.sighMs ? Math.floor(u / BRIDGE.sighMs) % 8 : 0);
            } else {
                this.officerAt('stalk', Math.floor(time / BRIDGE.wobbleMs) % 8, R.stationX + BRIDGE.officer0);
            }
        }
        // (The picture goes ahead of her as she comes up to them, by how near she is: at the line where she is taken the
        // hatch, at the bridge's forward end, is already well inside it. Led only from the take-over, the officer and
        // the hatch stood at the screen's edge at that moment.)
        const line = R.stationX + BRIDGE.sight;
        const coming = !q.playing && !q.cat.gone && !q.cat.hidden && s.route === 'inside' && p.x > R.x0 && p.x < R.x1 && p.y <= F + 1 && p.y > F - 100;
        if (coming) {
            q.lead = Math.min(1, Math.max(0, 1 - (p.x - line) / BRIDGE.leadIn));
            s.cameras.main.followOffset.x = BRIDGE.ahead * q.lead;
        } else if (!q.playing && q.lead) {
            q.lead = Math.max(0, q.lead - dt * 1000 / BRIDGE.aheadBack);
            s.cameras.main.followOffset.x = BRIDGE.ahead * q.lead;
        }
        // --- Her way out: her picture's top, over the balcony's floor, while the rest of her is in the hatch.
        const cut = this.hatchCut(), balcony = R.ceil - 16;
        if (cut && p.visible && p.y - 60 < balcony) {
            const rows = Math.max(0, Math.min(p.height, balcony - (p.y - p.displayOriginY)));
            q.top.setTexture(p.texture.key, p.frame.name).setDisplayOrigin(p.displayOriginX, p.displayOriginY).setPosition(p.x, p.y)
                .setFlipX(p.flipX).setDepth(p.depth).setCrop(0, 0, p.width, rows).setVisible(rows > 0);
        } else if (q.top.visible) {
            q.top.setVisible(false);
        }
        // --- The alarm, from the scene until Bumbot is caught: the beacon, the red light, the whoops.
        // (Seen only from deck 10 itself: from the balcony above, the bridge is behind the ship's side.)
        const on = (q.alarm || P.has('alarm')) && !P.has('catch') && p.y > F - 132 && p.y <= F + 2;
        if (on && near(s, (R.x0 + R.x1) / 2, F, 900, 200)) {
            const k = (Math.sin(time / 260) + 1) / 2;
            // (Whoop after whoop for its first seconds; after that, and whenever she comes back to the bridge, only
            // now and then: it would wear.)
            if (time > (q.soundAt ?? 0)) {
                q.loudUntil ??= time + (q.alarm ? BRIDGE.loudMs : 0);
                q.soundAt = time + (time < q.loudUntil ? 1000 : 6000);
                sfx.at(R.stationX, F).alarm(2);
            }
            q.wash.setFillStyle(0xe83b3b, 0.05 + 0.13 * k);
            const lit = k > 0.25 || time < (q.litUntil ?? 0);
            q.lamp.setVisible(lit);
            q.glow.clear();
            if (lit) {
                const gx = q.lamp.x + q.lamp.width / 2, gy = q.lamp.y + q.lamp.height / 2;
                q.glow.fillStyle(0xff6050, 0.18).fillCircle(gx, gy, 9).fillStyle(0xff8c6e, 0.28).fillCircle(gx, gy, 5);
            }
        } else if (q.wash.fillAlpha || q.lamp.visible) {
            q.wash.setFillStyle(0xe83b3b, 0);
            q.lamp.setVisible(false);
            q.glow.clear();
        }
        // --- She comes within sight of them on the bridge's floor: the scene. In a jump across that line she comes
        // straight down where she crossed it, and the scene begins as she lands.
        if (q.cat.gone || q.cat.hidden || s.mode !== 'play' || s.route !== 'inside') return;
        if (p.x > line || p.x < R.x0 || p.y > F + 1 || p.y < F - BRIDGE.airUp) return;
        if (p.body.blocked.down || p.body.touching.down) {
            if (Math.abs(p.y - F) <= 1) this.bridgeBeat();
            return;
        }
        q.cat.gone = true;
        s.mode = 'scripted';
        p.body.setVelocityX(0);
        p.body.setAccelerationX(0);
        s.script = () => {
            if (p.body.blocked.down || p.body.touching.down || p.y >= F) {
                s.script = null;
                this.bridgeBeat();
            } else {
                s.pose(p.body.velocity.y < 0 ? 'rise' : 'fall');
            }
        };
    },

    bridgeBeat() {
        const q = this.bridge, s = this.scene, w = this.world, p = s.player, k = q.cat.sprite, { R, L, C, F } = q;
        const B = BRIDGE, D = s.DEPTH, pace = p.anims.timeScale;
        const her = s.cache.json.get('her-meta').anims, cat = s.cache.json.get('bumbot-meta').anims;
        q.cat.gone = true;
        q.playing = true;
        s.mode = 'scripted';
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.y = F;
        if (s.crawling) s.crawling = false;
        p.setFlipX(true);               // (forward: the way she came, the way he goes)
        p.anims.stop();
        p.anims.timeScale = 1;
        // (With something in her hands she cannot hold one out: she stands and calls, and the rest is the same.)
        const hands = !w.carry && !s.holding && !!her.call;
        const herFrame = (clip, i) => p.setFrame(her[clip][Math.min(her[clip].length - 1, i)]);
        const catFrame = (clip, i) => k.setFrame(cat[clip][Math.min(cat[clip].length - 1, i)]);

        // Where everyone is: Bumbot on the console, then on the station's top, then back on the console, forward; the
        // officer from his stalk to where his net's clip was made.
        const st = R.stationX, c0 = k.x, c1 = st, c2 = st + B.back, onCon = F - B.onConsole, onSt = F - B.onStation;
        const o0 = st + B.officer0, o1 = C.net.x0 + B.netX;
        // The clock's marks that follow from the clips' lengths.
        const clangAt = B.swingAt + 2 / B.swingFps * 1000;          // the hoop is down in the net clip's fourth picture
        const satAt = B.fallAt + (C.net.frames - 1 - B.fallFrom) / B.fallFps * 1000;
        const goneAt = B.climbAt + (C.climb.frames - 1) / B.climbFps * 1000;
        const endAt = Math.max(B.freeAt, satAt + 150, goneAt + 100);

        k.anims.stop();
        k.setFlipX(false).setScale(1);
        let T = 0, steps = 0, rung = 0;
        const lead0 = q.lead ?? 0;
        const did = {};
        const once = (key, at, fn) => { if (!did[key] && T >= at) { did[key] = true; fn(); } };
        const end = () => {
            s.script = null;
            q.playing = false;
            q.state = null;
            p.body.enable = true;
            p.body.reset(p.x, p.y);
            p.anims.timeScale = pace;
            s.pose('stand');
            p.setFlipX(true);               // (the way on: the ladder)
            k.setVisible(false).setDepth(D.props);
            q.climb.setVisible(false);
            q.cat.away = true;
            s.mode = 'play';
            this.P.setFlag('bb6');          // (and with it `alarm`: the ladder is hers)
            this.bridgeShow();
        };

        s.script = (dt) => {
            T += dt * 1000;
            // (The picture ahead of her, as it came to be on her way up; from a jump across the line, eased in now.)
            q.lead = Math.max(lead0, Math.min(1, T / B.aheadMs));
            s.cameras.main.followOffset.x = B.ahead * q.lead;

            // --- She: down on her heels with a hand out; her call; beckoning; startled up at the clang; her look up
            // after him.
            if (hands) {
                if (T < B.crouchAt) herFrame('stand', 0);
                else if (T < B.callAt) herFrame('call', 1 + Math.floor((T - B.crouchAt) / B.crouchMs));
                else if (T < clangAt + B.startAfter) herFrame('call-loop', Math.floor((T - B.callAt) / B.beckonMs) % her['call-loop'].length);
                else if (T < clangAt + B.startAfter + 7 * B.upMs) herFrame('call-up', 1 + Math.floor((T - clangAt - B.startAfter) / B.upMs));
                else if (T < B.lookUpAt) herFrame('stand', 0);
                else herFrame(her['look-up'] ? 'look-up' : 'stand', Math.floor((T - B.lookUpAt) / B.lookMs));
            } else {
                herFrame(T >= B.lookUpAt && her['look-up'] ? 'look-up' : 'stand', T >= B.lookUpAt ? Math.floor((T - B.lookUpAt) / B.lookMs) : 0);
            }
            once('call', B.callAt, () => {
                w.say(t('call.kitty'), B.callMs);
                sfx.pspsps();
            });

            // --- Bumbot ---
            if (T < B.lookAt) {
                catFrame('wash', Math.floor(T / B.washMs) % cat.wash.length);
            } else if (T < B.upAt) {
                catFrame('sat', Math.floor((T - B.lookAt) / 150) % cat.sat.length);
            } else if (T < B.hopAt) {
                catFrame('stand-up', Math.floor((T - B.upAt) / B.standMs));
            } else if (T < B.thereAt) {
                // (From the console onto the station's top, over its button: the leap's frames each on its lowest
                // pixel, the arc the scene's.)
                const u = (T - B.hopAt) / (B.thereAt - B.hopAt);
                k.setPosition(c0 + (c1 - c0) * u, onCon + (onSt - onCon) * u - B.hopUp * Math.sin(Math.PI * u));
                catFrame('leap', 4 + Math.floor(u * 9));
            } else if (T < B.springAt) {
                k.setPosition(c1, onSt);
                catFrame('idle', Math.floor((T - B.thereAt) / 120) % cat.idle.length);
            } else if (T < B.landAt) {
                // (Up off the station and back over the officer in one long arc, onto the console's top behind him:
                // the user at the preview, of a landing on the officer's cap: "in the air between the consoles".)
                const u = (T - B.springAt) / (B.landAt - B.springAt);
                // (Straight up first: sideways from the start he crossed the officer's raised net.)
                k.setPosition(c1 + (c2 - c1) * u ** 1.7, onSt + (onCon - onSt) * u - B.springUp * Math.sin(Math.PI * u ** 0.6));
                k.setFlipX(u > 0.12).setDepth(D.props + 0.1);
                catFrame('leap', 2 + Math.floor(u * 12));
            } else if (T < B.climbAt) {
                // (Crouched on the console, his head to the hatch as it opens.)
                k.setPosition(c2, onCon).setFlipX(true).setDepth(D.props);
                if (T < B.landAt + 140) catFrame('sat', 0); else catFrame('idle', Math.floor((T - B.landAt) / 130) % cat.idle.length);
            } else if (!q.cat.away) {
                // (His climb: one clip, from his run along the console onto the ladder and up it; cut at the hatch's mouth.)
                const f = Math.min(C.climb.frames - 1, Math.floor((T - B.climbAt) / 1000 * B.climbFps));
                k.setVisible(false);
                q.climb.setFrame(f).setCrop(0, q.mouth - C.climb.y0, C.climb.w, C.climb.h).setVisible(T < goneAt);
                if (f >= B.rungFrom && f > rung + 1 && T < goneAt) { rung = f; sfx.at(R.hatchX, F - 60).scramble(); }
            }
            once('look', B.lookAt, () => sfx.at(k.x, k.y).mrrp());
            once('there', B.thereAt, () => sfx.at(k.x, k.y).meow());
            once('spring', B.springAt, () => { rumble('bolt'); sfx.at(k.x, k.y).mrrp(); });
            once('land', B.landAt, () => sfx.at(k.x, k.y).scramble());

            // --- The officer: frozen; after Bumbot on tiptoe, one round of his creep; his net's clip on its schedule.
            if (T < B.creepAt) {
                this.officerAt('stalk', Math.floor(T / B.wobbleMs) % 8, o0);
            } else if (T < B.swingAt) {
                const f = (T - B.creepAt) / 1000 * B.creepFps, u = Math.min(1, f / 8);
                this.officerAt('creep', Math.floor(f) % 8, o0 + (o1 - o0) * u);
                if (f >= steps * 4) { steps++; sfx.at(q.officer.x + 64, F).tiptoe(); }
            } else if (T < clangAt) {
                this.officerAt('net', Math.min(3, 1 + Math.floor((T - B.swingAt) / 1000 * B.swingFps)));
            } else if (T < B.tugAt) {
                this.officerAt('net', B.stuck[Math.floor((T - clangAt) / B.stuckMs) % B.stuck.length]);
            } else if (T < B.fallAt) {
                this.officerAt('net', Math.min(B.fallFrom - 1, B.tugFrom + Math.floor((T - B.tugAt) / 1000 * B.tugFps)));
            } else {
                this.officerAt('net', Math.min(C.net.frames - 1, B.fallFrom + Math.floor((T - B.fallAt) / 1000 * B.fallFps)));
            }
            once('swing', B.swingAt, () => { sfx.at(o1, F).hey(); sfx.at(o1, F).net(); });
            once('free', B.fallAt, () => sfx.at(o1, F).net());
            once('sat', satAt - 120, () => { sfx.at(o1, F).thump(); sfx.at(o1, F).grumble(); });

            // --- The button, the alarm ---
            once('clang', clangAt, () => {
                q.station.setTexture('bridge-station-down');
                q.alarm = true;
                q.litUntil = s.time.now + 300;
                q.soundAt = s.time.now + B.whoopAfter;
                sfx.at(st, F).clang();
                rumble('alarm');
                s.cameras.main.shake(260, 0.006);
                const bx = q.station.x + L.station.button[0], by = q.station.y + L.station.button[1] + 6;
                w.sparkle(bx - 7, by - 5, 0xfbff86);
                w.sparkle(bx + 8, by - 6, 0xfbff86);
            });

            // --- The hatch: its lid drops, its ladder comes down ---
            if (T >= B.lidAt) {
                const f = Math.min(L.lid.frames - 1, 1 + Math.floor((T - B.lidAt) / B.lidMs));
                if (q.lid.frame.name !== f) q.lid.setFrame(f);
            }
            once('lid', B.lidAt, () => sfx.at(R.hatchX, R.ceil).hatch());
            if (T >= B.ladderAt) {
                const u = Math.min(1, (T - B.ladderAt) / (B.downAt - B.ladderAt));
                this.ladderDown(1 - (1 - u) ** 2);
                const n = Math.floor(u * B.ratchets);
                if (n > (did.rat ?? 0) && u < 1) { did.rat = n; sfx.at(R.hatchX, R.ceil + 40).ratchet(); }
            }
            once('down', B.downAt, () => sfx.at(R.hatchX, F).thump());

            if (T >= goneAt) q.cat.away = true;
            if (T >= endAt) end();
        };
    },
};
