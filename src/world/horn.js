// The horn's scene (region 8; the user's remake, 2026-11-27, docs/horn-remake-log.md), mixed into the Story.
//
// Nobody sends her to the cord: Bumbot sits on the horn's top bar out of her reach, the cord hangs beside her, and the
// pull is her own try at getting him down (the user: "Let her just see Bumbot on top of the horn, the cord, and the
// move is quite obvious from there. This makes the scene like a near catch"). One clock (`HORN` in src/config.js),
// everything a function of it:
//   - she pulls; the horn sounds over her head, one prolonged blast, and she lets go and claps her hands over her ears;
//   - Bumbot shoots straight up off the bar in a fright, comes down on the platform forward of her and is gone down
//     the stairway;
//   - what the blast sets off is 53 m forward of her and 13 m under her, so it is shown in a live panel under the top
//     (`src/inset.js`) while the horn still sounds, the camera never leaving her: the sun deck (the security officer
//     off his knees into the air, his card out of his pocket; the old lady up and away, everything of hers left;
//     Bumbot through, and the officer after him over the sunbed), then the bow (both flocks of gulls up);
//   - the horn stops, the panel shuts, she takes her hands down, looks up at the empty bar, and is hers.
// After that the cord gives a toot.
import { HORN, HORN_FISTS, HORN_REST } from '../config.js';
import { sfx } from '../sfx.js';
import { rumble } from '../rumble.js';
import { Inset } from '../inset.js';

const CLIP_COLS = 9;            // assets/ship/horn/clips.png: a clip to a row, cells of 96 x 112 (tools/build_horn.py)

export const horn = {
    // E at the horn's cord (population: `sec_horn`).
    horn() {
        const s = this.scene, w = this.world, her = s.player;
        if (w.carry || s.holding || s.mode !== 'play') return false;
        if (!this.P.has('horn')) {
            this.hornScene();
            return true;
        }
        w.cut(async () => {
            const left = this.cordAt.x < her.x, x = this.pullX(left);
            her.setFlipX(left);
            if (Math.abs(her.x - x) > 1) {
                s.pose('run', 0.6);
                await w.tween({ targets: her, x, duration: Math.min(400, Math.abs(her.x - x) * 16) });
                her.setFlipX(left);
            }
            her.x = x;
            her.anims.play('her-pull');
            this.pulling = true;
            await w.wait(320);
            this.blast(500);
            await w.wait(450);
            this.cordBack();
            s.pose('stand');
        });
        return true;
    },

    // She lets go: the handle swings back up to where it hangs.
    cordBack() {
        const s = this.scene;
        this.pulling = false;
        const from = this.cordHandle.y, rest = this.world.data.funnel.y - HORN_REST;
        s.tweens.addCounter({ from, to: rest, duration: 260, ease: 'Sine.easeOut', onUpdate: tw => this.drawCord(0, tw.getValue()) });
    },

    // The blast: the top shakes (hard at first, then a tremble as long as it sounds), rings of sound leave the
    // trumpets, the pipes cough smoke.
    blast(ms) {
        const s = this.scene, w = this.world, F = this.T.funnel, top = w.data.funnel.y, cam = s.cameras.main;
        sfx.horn(ms / 1000);
        rumble('horn', ms);
        const hard = Math.min(ms, HORN.shakeMs);
        cam.shake(hard, HORN.shake);
        if (ms > hard) s.time.delayedCall(hard, () => cam.shake(ms - hard, HORN.tremble));
        for (let i = 0; i * HORN.ringMs < ms; i++) {
            s.time.delayedCall(i * HORN.ringMs, () => {
                const ring = s.add.ellipse(F.hornX - 44, top - 96, 8, 16).setStrokeStyle(2, 0xffffff, 0.9).setDepth(s.DEPTH.fx);
                w.add([ring]);
                s.tweens.add({ targets: ring, x: ring.x - 150, scaleX: 5, scaleY: 7, alpha: 0, duration: 700, ease: 'Quad.easeOut', onComplete: () => ring.destroy() });
            });
        }
        s.smokeBurst(ms);
    },

    // The scene's own pictures: the officer's and the old lady's clips made for it, Bumbot on the sun deck, the card.
    hornActors() {
        if (this.hornOwn) return this.hornOwn;
        const s = this.scene, w = this.world, D = s.DEPTH;
        const sprite = depth => s.add.sprite(0, 0, 'horn-clips', 0).setOrigin(0.5, 1).setDepth(depth).setVisible(false);
        const officer = sprite(D.props + 0.08), lady = sprite(D.props + 0.08);
        // (Bumbot on the sun deck is on the people's layer, behind its railing as they are.)
        const runner = s.add.sprite(0, 0, 'bumbot').setOrigin(0.5, 1).setDepth(D.props + 0.09).setFlipX(true).setVisible(false);
        w.add([officer, lady, runner]);
        return (this.hornOwn = { officer, lady, runner });
    },

    hornScene() {
        const s = this.scene, w = this.world, P = this.P, p = s.player, H = HORN, D = s.DEPTH;
        const top = w.data.funnel.y, L = this.T.lady, cat = this.hornCat;
        const her = s.cache.json.get('her-meta').anims, cats = s.cache.json.get('bumbot-meta').anims;
        const clips = s.cache.json.get('horn-clips-meta').clips, people = s.cache.json.get('people-meta').people;
        const own = this.hornActors(), rival = this.who('riv_sundeck'), lady = this.who('npc_oldlady');
        const pace = p.anims.timeScale, left = this.cordAt.x < p.x, x0 = this.pullX(left);
        this.inset ??= new Inset(s);

        s.mode = 'scripted';
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.setFlipX(left);
        s.pose('run', 0.6);
        const herFrame = (clip, i) => p.setFrame(her[clip][Math.max(0, Math.min(her[clip].length - 1, i))]);
        const catFrame = (sp, clip, i) => sp.setFrame(cats[clip][Math.max(0, Math.min(cats[clip].length - 1, i))]);
        const clipAt = (clip, i) => Math.max(0, Math.min(clips[clip].frames - 1, i));
        const clipFrame = (sp, clip, i) => sp.setFrame(clips[clip].row * CLIP_COLS + clipAt(clip, i));
        // (A clip's own rise, of which `keep` is kept: how far its frame is set down.)
        const sunk = (clip, i, keep) => Math.round(clips[clip].up[clipAt(clip, i)] * (1 - keep));

        // --- Where everyone is.
        const seat = { x: cat.x, y: cat.y }, landX = Math.min(x0, this.cordAt.x) - H.cat.land;
        const view = { x: (L.x + L.rivalX) / 2, floorY: L.y, foot: H.panel.foot };
        const flocks = ['gull_bow_a', 'gull_bow_b'].map(id => this.flocks.find(f => f.def.id === id));
        const bowX = flocks[0] ? (Math.min(...flocks[0].birds.map(b => b.x)) + Math.max(...flocks[0].birds.map(b => b.x))) / 2 : 3400;
        const edge = { left: view.x - H.panel.w / 2, right: view.x + H.panel.w / 2 };
        const rx = rival?.x ?? L.rivalX, lx = lady?.x ?? L.x, floor = L.y;
        // The clock's marks that follow from the others.
        const catT = at => H.catAt + (edge.right + 24 - at) / H.catRun * 1000;       // when Bumbot is at a spot on the sun deck
        const leap0 = L.x + H.catLeap[0], leap1 = L.x - H.catLeap[1];
        const turnAt = catT(rx - 6) + H.turnMs, chargeAt = turnAt + H.chargeAfter;
        const off0 = L.x + H.hurdle[0], off1 = L.x - H.hurdle[1];
        const hurdleAt = chargeAt + (rx - off0) / H.charge * 1000, hurdleMs = (off0 - off1) / H.hurdle[2] * 1000;
        const boltEnd = H.ladyAt + 9 * H.boltMs;
        const hornEnd = H.blastAt + H.blastMs, downAt = hornEnd + H.downAfter, lookAt = downAt + 5 * H.earsMs;
        const endAt = lookAt + 8 * H.lookMs + H.endHold;

        let T = -1, did = {}, fistY = null, card = null;
        const once = (key, at, fn) => { if (!did[key] && T >= at) { did[key] = true; fn(); } };
        const end = () => {
            s.script = null;
            p.body.enable = true;
            p.body.reset(p.x, p.y);
            p.anims.timeScale = pace;
            s.pose('stand');
            s.mode = 'play';
            s.viewOverride = null;
            this.hornCatGone = true;
            cat.setVisible(false);
            for (const sp of Object.values(own)) sp.setVisible(false);
            for (const q of [rival, lady]) {
                if (!q) continue;
                q.gone = true;
                q.sprite.setVisible(false);
                q.items.forEach(i => i.setVisible(false));
            }
            card?.items.forEach((it, j) => it.setPosition(card.home[j].x, card.home[j].y));
            P.setFlag('horn');
            s.shrug();
        };

        s.script = dt => {
            // --- A step or two to where her fist closes on the handle, then the clock.
            if (T < 0) {
                const d = x0 - p.x, step = H.stepSpeed * dt;
                if (Math.abs(d) > step) { p.x += Math.sign(d) * step; return; }
                p.x = x0;
                p.setFlipX(left);
                p.anims.stop();
                p.anims.timeScale = 1;
                T = 0;
                s.viewOverride = 12;            // (deck 12 shown as it is from its own floor: the panel looks at it)
                for (const q of [rival, lady]) if (q) { q.state = 'acting'; q.sprite.anims.stop(); }
                if (rival) rival.sprite.setFrame(people.rival.anims.peek[4]);
                if (lady) { lady.still = ''; this.oldLady.glaring = false; }
            }
            T += dt * 1000;

            // --- She: the pull, her hands over her ears while it sounds, down again, a look up at the empty bar.
            if (T < H.letGo) {
                const i = Math.min(4, Math.floor(T / H.pullMs));
                herFrame('pull', i);
                fistY = p.getTopLeft().y + HORN_FISTS[i][1] - 4;
                this.drawCord(0, fistY);
            } else if (T < downAt) {
                const u = T - H.letGo;
                herFrame('ears', u < 4 * H.earsMs ? 1 + Math.floor(u / H.earsMs) : [5, 6, 7, 8, 7, 6][Math.floor((u - 4 * H.earsMs) / H.trembleMs) % 6]);
                const k = Math.min(1, u / H.cordMs), rest = top - HORN_REST;
                this.drawCord(0, fistY + (rest - fistY) * (1 - (1 - k) ** 2));
            } else if (T < lookAt) herFrame('ears', 4 - Math.floor((T - downAt) / H.earsMs));
            else herFrame('look-up', Math.floor((T - lookAt) / H.lookMs));
            once('blast', H.blastAt, () => this.blast(H.blastMs));

            // --- Bumbot: straight up off the bar, back arched; down onto the platform forward of her; away.
            const C = H.cat, c0 = H.blastAt, c1 = c0 + C.upMs, c2 = c1 + C.hang, c3 = c2 + C.fallMs, c4 = c3 + C.crouch;
            if (T >= c0 && !did.catGone) {
                cat.anims.stop();
                if (T < c2) {
                    const k = Math.min(1, (T - c0) / C.upMs);
                    catFrame(cat, 'fright', T < c1 ? 1 + Math.floor((T - c0) / C.frameMs) : 4 + Math.floor((T - c1) / C.frameMs) % 5);
                    cat.setPosition(seat.x - C.drift * k, seat.y - C.up * (1 - (1 - k) ** 2));
                } else if (T < c3) {
                    const k = (T - c2) / C.fallMs;
                    catFrame(cat, 'fright', 4 + Math.floor((T - c1) / C.frameMs) % 5);
                    cat.setPosition(seat.x - C.drift + (landX - seat.x + C.drift) * k, seat.y - C.up + (top - seat.y + C.up) * k * k);
                } else if (T < c4) {
                    catFrame(cat, 'leap', cats.leap.length - 1);
                    cat.setPosition(landX, top);
                } else {
                    catFrame(cat, 'run', Math.floor((T - c4) / C.runMs) % cats.run.length);
                    cat.setPosition(landX - (T - c4) / 1000 * C.run, top);
                    if (cat.x < s.cameras.main.worldView.x - 30) { did.catGone = true; cat.setVisible(false); this.hornCatGone = true; }
                }
            }
            once('meow', c0, () => sfx.meow());
            once('landed', c3, () => sfx.scramble());

            // --- The panel: the sun deck, then the bow.
            once('sun', H.sunAt, () => this.inset.show(H.panel, view));
            once('bow', H.bowAt, () => this.inset.move({ x: bowX, floorY: floor, foot: H.bowFoot }));
            once('shut', hornEnd - H.shutBefore, () => this.inset.hide());

            // --- The officer: off his knees into the air, his card out of his pocket; Bumbot past him; after him, over
            // the sunbed.
            if (rival && T >= H.startAt) {
                const o = own.officer, mine = on => { o.setVisible(on); rival.sprite.setVisible(!on); };
                if (T < H.startAt + 9 * H.startMs) {
                    mine(true);
                    const i = Math.floor((T - H.startAt) / H.startMs);
                    clipFrame(o, 'start', i);
                    o.setPosition(rx, floor + sunk('start', i, H.startRise)).setFlipX(false);
                } else if (T < chargeAt) {
                    mine(false);
                    rival.sprite.setFrame(people.rival.stand).setPosition(rx, floor).setFlipX(T >= turnAt);
                } else if (T < hurdleAt || T >= hurdleAt + hurdleMs) {
                    mine(false);
                    const after = T >= hurdleAt + hurdleMs;
                    const x = after ? off1 - (T - hurdleAt - hurdleMs) / 1000 * H.charge : rx - (T - chargeAt) / 1000 * H.charge;
                    rival.sprite.setFrame(people.rival.anims.charge[Math.floor((T - chargeAt) / H.chargeMs) % 8]).setPosition(x, floor).setFlipX(true);
                    if (x < edge.left - 60) rival.sprite.setVisible(false);
                } else {
                    mine(true);
                    const k = (T - hurdleAt) / hurdleMs;
                    const i = Math.floor(k * 9);
                    clipFrame(o, 'hurdle', i);
                    o.setPosition(off0 + (off1 - off0) * k, floor + sunk('hurdle', i, H.hurdleRise)).setFlipX(true);
                }
            }
            once('yelp', H.startAt + H.startMs, () => sfx.yelp());
            // (His card: out of his pocket at the top of his start, over his shoulder, down to where it will lie.)
            const cardAt = H.startAt + H.cardFrame * H.startMs;
            // (The world's own card, the one that will lie there: shown from now, moved to its place.)
            once('card', cardAt, () => {
                card = P.cards?.find(c => c.card === 'off');
                if (!card) return;
                card.home = card.items.map(i => ({ x: i.x, y: i.y }));
                card.items.forEach(i => i.setVisible(true));
            });
            if (card && T >= cardAt) {
                const k = Math.min(1, (T - cardAt) / H.cardMs), h0 = card.home[0];
                const dx = (rx + 4 - h0.x) * (1 - k), dy = (floor - 58 - h0.y) * (1 - k) - H.cardUp * 4 * k * (1 - k);
                card.items.forEach((it, j) => it.setPosition(card.home[j].x + dx, card.home[j].y + dy));
                if (k === 1) once('cardDown', 0, () => { sfx.sparkle(); w.sparkle(h0.x, h0.y - 4, w.cardColour('off')); });
            }

            // --- The old lady: up off her sunbed and away, her book in her hand; everything else of hers stays.
            if (lady && T >= H.ladyAt) {
                const o = own.lady;
                if (T < boltEnd) {
                    // (Off the sunbed onto the floor in her last two frames: she sits `dy` px over it.)
                    const i = Math.floor((T - H.ladyAt) / H.boltMs);
                    lady.sprite.setFrame(people.oldlady.anims.bolt[i]).setY(floor - (lady.dy ?? 0) * (i < 7 ? 1 : i === 7 ? 0.5 : 0));
                } else {
                    lady.sprite.setVisible(false);
                    const x = lx - H.ladyStep - (T - boltEnd) / 1000 * H.hurry;
                    clipFrame(o, 'hurry', Math.floor((T - boltEnd) / H.hurryMs) % 8);
                    o.setPosition(x, floor).setFlipX(true).setVisible(x > edge.left - 60);
                }
            }
            once('oh', H.ladyAt + 3 * H.boltMs, () => sfx.oh());

            // --- Bumbot through the sun deck: past the officer, over the sunbed.
            if (T >= H.catAt) {
                const r = own.runner, x = edge.right + 24 - (T - H.catAt) / 1000 * H.catRun;
                const k = (leap0 - x) / (leap0 - leap1), up = k > 0 && k < 1 ? H.catLeap[2] * 4 * k * (1 - k) : 0;
                if (up) catFrame(r, 'leap', Math.floor(k * cats.leap.length));
                else catFrame(r, 'run', Math.floor((T - H.catAt) / H.cat.runMs) % cats.run.length);
                r.setPosition(x, floor - up).setVisible(x > edge.left - 40);
            }
            once('scramble', H.catAt + 200, () => sfx.scramble());

            // --- The bow: the windscreen's six cross the sky, the kids' pool's six go up.
            once('fly', H.flyAt, () => flocks[1]?.liftOff((b, i) => ({ x: bowX + 420 + i * 50, y: floor - 34 - (i * 17) % 30, ms: H.flyMs + i * 70 })));
            once('lift', H.liftAt, () => flocks[0]?.liftOff());

            if (T >= endAt) end();
        };
    },
};
