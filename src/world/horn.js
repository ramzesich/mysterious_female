// The horn's scene (region 8; the user's remake, 2026-11-27, docs/horn-remake-log.md), mixed into the Story.
//
// Nobody sends her to the cord: Bumbot sits on the horn's top bar out of her reach, the cord hangs beside her, and the
// pull is her own try at getting him down (the user: "Let her just see Bumbot on top of the horn, the cord, and the
// move is quite obvious from there. This makes the scene like a near catch"). One clock (`HORN` in src/config.js),
// everything a function of it, in three places the camera pans between (the user, of a live panel under the top: "I
// don't like the panels. Let's revert to the view ... What moves things around is running Bumbot, not the horn"; of
// cuts: "I liked the pans"):
//   - the top: she pulls; the horn sounds over her head and she claps her hands over her ears; Bumbot shoots straight
//     up off the bar in a fright, comes down on the platform forward of her and is gone down the stairway; it stops, she
//     takes her hands down and turns the way he went;
//   - the sun deck: quiet, the officer on his knees at the loungers, the old lady reading. Bumbot comes through: past
//     the officer, who is off his knees into the air, his card out of his pocket; over the sunbed, and the old lady is
//     up and away, everything of hers left; the officer after him, over the sunbed in his stride;
//   - the bow: he runs by the kids' pool, straight across at the deck's height as the old scene had him (the user's
//     choice of three ways), and its six gulls go up one by one as he reaches them;
//   - back to her: she shrugs, and is hers.
// After that the cord gives a toot.
import { PLAYER, HORN, HORN_FISTS, HORN_REST } from '../config.js';
import { sfx } from '../sfx.js';
import { rumble } from '../rumble.js';

const HALF = PLAYER.height / 2;
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

    // The blast: the top shakes, rings of sound leave the trumpets, the pipes cough smoke.
    blast(ms) {
        const s = this.scene, w = this.world, F = this.T.funnel, top = w.data.funnel.y, cam = s.cameras.main;
        sfx.horn(ms / 1000);
        rumble('horn', ms);
        cam.shake(ms, HORN.shake);
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
        const s = this.scene, w = this.world, P = this.P, p = s.player, H = HORN, cam = s.cameras.main;
        const top = w.data.funnel.y, L = this.T.lady, cat = this.hornCat;
        const her = s.cache.json.get('her-meta').anims, cats = s.cache.json.get('bumbot-meta').anims;
        const clips = s.cache.json.get('horn-clips-meta').clips, people = s.cache.json.get('people-meta').people;
        const own = this.hornActors(), rival = this.who('riv_sundeck'), lady = this.who('npc_oldlady');
        const pace = p.anims.timeScale, left = this.cordAt.x < p.x, x0 = this.pullX(left);

        s.mode = 'scripted';
        p.body.setVelocity(0, 0);
        p.body.enable = false;
        p.setFlipX(left);
        s.pose('run', 0.6);
        const herFrame = (clip, i) => p.setFrame(her[clip][Math.max(0, Math.min(her[clip].length - 1, i))]);
        const catFrame = (sp, clip, i) => sp.setFrame(cats[clip][Math.max(0, Math.min(cats[clip].length - 1, i))]);
        const clipFrame = (sp, clip, i) => sp.setFrame(clips[clip].row * CLIP_COLS + Math.max(0, Math.min(clips[clip].frames - 1, i)));
        // A place the camera goes to: its floor where the top's own is on the screen (so the horizon holds). A pan: from
        // where the camera is at its start, eased in and out, by the clock.
        const place = x => ({ x: Math.round(x), y: floor + cam.worldView.height / 2 - H.floorAt });
        let from = null;
        const pan = (key, at, ms, to) => {
            if (T < at || did[key + 'Done']) return;
            if (!did[key]) {
                did[key] = true;
                cam.stopFollow();
                from = { x: cam.worldView.centerX, y: cam.worldView.centerY };
            }
            const k = Math.min(1, (T - at) / ms), e = 0.5 - Math.cos(k * Math.PI) / 2;
            cam.centerOn(from.x + (to.x - from.x) * e, from.y + (to.y - from.y) * e);
            if (k === 1) did[key + 'Done'] = true;
        };

        // --- Where everyone is.
        const seat = { x: cat.x, y: cat.y }, landX = Math.min(x0, this.cordAt.x) - H.cat.land;
        const floor = L.y, sunX = (L.x + L.rivalX) / 2, half = cam.worldView.width / 2;
        const flocks = ['gull_bow_a', 'gull_bow_b'].map(id => this.flocks.find(f => f.def.id === id));
        const perch = flocks[0]?.birds.map(b => b.x) ?? [3246, 3597];
        const bowX = (Math.min(...perch) + Math.max(...perch)) / 2;
        const rx = rival?.x ?? L.rivalX, lx = lady?.x ?? L.x;
        // The clock's marks, each from the one before: Bumbot's run through the sun deck sets them.
        const in0 = sunX + half + 24, catAt = H.sunAt + H.panSun + H.sunCalm;
        const catT = at => catAt + (in0 - at) / H.catRun * 1000;                // when he is at a spot on the sun deck
        const leap0 = L.x + H.catLeap[0], leap1 = L.x - H.catLeap[1];
        const startAt = catT(rx + H.startBefore), turnAt = startAt + 9 * H.startMs + H.turnMs, chargeAt = turnAt + H.chargeAfter;
        const ladyAt = catT(lx + H.boltBefore), boltEnd = ladyAt + 9 * H.boltMs;
        const off0 = L.x + H.hurdle[0], off1 = L.x - H.hurdle[1];
        const hurdleAt = chargeAt + (rx - off0) / H.charge * 1000, hurdleMs = (off0 - off1) / H.hurdle[2] * 1000;
        const goneAt = hurdleAt + hurdleMs + (off1 - (sunX - half) + 40) / H.charge * 1000;        // the officer out of the shot
        const bowAt = goneAt + H.sunHold, bowThere = bowAt + H.panBow, runAt = bowThere + H.bowCalm, in1 = bowX + half + 24;
        const backAt = runAt + H.bowHold, endAt = backAt + H.panBack + H.endHold;
        const hornEnd = H.blastAt + H.blastMs, downAt = hornEnd + H.downAfter, turnHer = downAt + 5 * H.earsMs + H.turnAfter;

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
                s.viewOverride = 12;            // (deck 12 as it is from its own floor, for the shots to come: nothing changes up here)
                for (const q of [rival, lady]) if (q) { q.state = 'acting'; q.sprite.anims.stop(); }
                if (rival) rival.sprite.setFrame(people.rival.anims.peek[4]);
                if (lady) { lady.still = ''; this.oldLady.glaring = false; lady.sprite.setFrame(people.oldlady.anims.read[0]); }
            }
            T += dt * 1000;

            // --- She: the pull, her hands over her ears while it sounds, down again, a turn the way he went.
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
            } else if (T < downAt + 5 * H.earsMs) herFrame('ears', 4 - Math.floor((T - downAt) / H.earsMs));
            else { herFrame('stand', 0); p.setFlipX(T >= turnHer ? true : left); }
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
                    if (cat.x < landX - 400) { did.catGone = true; cat.setVisible(false); this.hornCatGone = true; }
                }
            }
            once('meow', c0, () => sfx.meow());
            once('landed', c3, () => sfx.scramble());

            // --- The camera: to the sun deck, on to the bow, back to her.
            pan('sun', H.sunAt, H.panSun, place(sunX));
            pan('bow', bowAt, H.panBow, place(bowX));
            pan('back', backAt, H.panBack, { x: p.x, y: p.y - HALF });
            once('follow', backAt + H.panBack, () => {
                cam.startFollow(p, true, 0.15, 0.15);
                cam.setFollowOffset(0, HALF);
            });

            // --- Bumbot through the sun deck: past the officer, over the sunbed; then through the bow's shot.
            const r = own.runner;
            if (T >= catAt && T < bowAt) {
                const x = in0 - (T - catAt) / 1000 * H.catRun;
                const k = (leap0 - x) / (leap0 - leap1), up = k > 0 && k < 1 ? H.catLeap[2] * 4 * k * (1 - k) : 0;
                if (up) catFrame(r, 'leap', Math.floor(k * cats.leap.length));
                else catFrame(r, 'run', Math.floor((T - catAt) / H.cat.runMs) % cats.run.length);
                r.setPosition(x, floor - up).setDepth(s.DEPTH.props + 0.09).setVisible(x > sunX - half - 40);
            } else if (T >= runAt && T < backAt) {
                catFrame(r, 'run', Math.floor((T - runAt) / H.cat.runMs) % cats.run.length);
                // (By the kids' pool, across it at the deck's height: the user, of the windscreen's rail I had put him on.)
                r.setPosition(in1 - (T - runAt) / 1000 * H.catRun, floor).setDepth(s.DEPTH.props + 0.09).setVisible(true);
            } else r.setVisible(false);
            once('scramble', catAt, () => sfx.scramble());
            once('scramble2', runAt, () => sfx.scramble());

            // --- The officer: off his knees into the air as Bumbot shoots past him, his card out of his pocket; a look
            // after him; after him, over the sunbed.
            // (He goes on forward as the camera passes him on its way to the bow.)
            if (rival && T >= startAt && T < bowThere) {
                const o = own.officer, mine = on => { o.setVisible(on); rival.sprite.setVisible(!on); };
                if (T < startAt + 9 * H.startMs) {
                    mine(true);
                    clipFrame(o, 'start', Math.floor((T - startAt) / H.startMs));
                    o.setPosition(rx, floor).setFlipX(false);
                } else if (T < chargeAt) {
                    mine(false);
                    rival.sprite.setFrame(people.rival.stand).setPosition(rx, floor).setFlipX(T >= turnAt);
                } else if (T < hurdleAt || T >= hurdleAt + hurdleMs) {
                    mine(false);
                    const after = T >= hurdleAt + hurdleMs;
                    const x = after ? off1 - (T - hurdleAt - hurdleMs) / 1000 * H.charge : rx - (T - chargeAt) / 1000 * H.charge;
                    rival.sprite.setFrame(people.rival.anims.charge[Math.floor((T - chargeAt) / H.chargeMs) % 8]).setPosition(x, floor).setFlipX(true);
                } else {
                    mine(true);
                    const k = (T - hurdleAt) / hurdleMs;
                    clipFrame(o, 'hurdle', Math.floor(k * 9));
                    o.setPosition(off0 + (off1 - off0) * k, floor).setFlipX(true);
                }
            }
            once('officerOff', bowThere, () => { own.officer.setVisible(false); rival?.sprite.setVisible(false); own.lady.setVisible(false); });
            once('yelp', startAt + H.startMs, () => sfx.yelp());
            // (His card: out of his pocket at the top of his start, over his shoulder, down to where it will lie. The
            // world's own card, the one that will lie there: shown from now, moved to its place.)
            const cardAt = startAt + H.cardFrame * H.startMs;
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

            // --- The old lady: Bumbot over her sunbed, and she is up off it and away, her book in her hand; everything
            // else of hers stays.
            if (lady && T >= ladyAt && T < bowThere) {
                const o = own.lady;
                if (T < boltEnd) {
                    // (Off the sunbed onto the floor in her last two frames: she sits `dy` px over it.)
                    const i = Math.floor((T - ladyAt) / H.boltMs);
                    lady.sprite.setFrame(people.oldlady.anims.bolt[i]).setY(floor - (lady.dy ?? 0) * (i < 7 ? 1 : i === 7 ? 0.5 : 0));
                } else {
                    lady.sprite.setVisible(false);
                    const x = lx - H.ladyStep - (T - boltEnd) / 1000 * H.hurry;
                    clipFrame(o, 'hurry', Math.floor((T - boltEnd) / H.hurryMs) % 8);
                    o.setPosition(x, floor).setFlipX(true).setVisible(true);
                }
            }
            once('oh', ladyAt + 3 * H.boltMs, () => sfx.oh());

            // --- The bow: the kids' pool's six go up one by one as he reaches each; the windscreen's six, forward of the
            // picture, a moment later, unseen.
            once('lift', runAt, () => flocks[0]?.liftOff((b, i) => ({ x: b.x - 260 - i * 36, y: b.y - 250 - (i * 53) % 90, ms: H.liftMs + i * 90,
                ease: 'Quad.easeOut', delay: Math.max(24 + H.liftSeen, in1 - b.x - H.liftBefore) / H.catRun * 1000 })));
            once('lift2', runAt + H.bowHold - 200, () => flocks[1]?.liftOff());

            if (T >= endAt) end();
        };
    },
};
