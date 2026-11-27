// Synthesised sound (§7.1): every effect and the ambience are made here in code, no audio files.
//
//   sfx.door()                 an effect, heard at her ears
//   sfx.at(x, y).door()        the same from a place in the world: fainter with distance (a deck up
//                              or down counts for more than the same way along), a little to its
//                              side, silent out of earshot. For anything on a clock of its own.
//   sfx.hold('whirr')          an effect held for as long as something runs (a motor while a key is
//                              held): returns `{ stop() }`, which fades it out; `sfx.at(x, y).hold(...)` too
//   sfx.listen(x, y)           where her ears are (the ship scene, each frame)
//   sfx.ambience({ sea, ... }) how loud each layer of the ambience should be now (0 to 1)
//   sfx.toggle()               mute on and off (M in the game), remembered in the browser
//
// Sound is on with SOUND.on (src/config.js); `?sound=off` in the URL silences it for a session,
// (A bare `?sound` turned it on while SOUND.on was false: gone, 2026-11-24.) The context starts on the first key or click.
// What was played is counted in `sfx.counts` and listed in `sfx.log` whether it was heard or not
// (the playtests read them). `tools/soundboard.html` plays every one of them by a button;
// `python tools/check_sound.py` renders them all and measures them.

import { SOUND } from './config.js';

const params = new URLSearchParams(location.search);
const KEY = 'bumbusik-sound';
const enabled = SOUND.on && params.get('sound') !== 'off';
let muted = localStorage.getItem(KEY) === 'off';
let live = null;        // the page's context and its chain
let off = null;         // an offline one, while a tool renders
let cur = null;         // the effect being built: its context, where it goes, when it starts
let nextPos = null;
const ear = { x: 0, y: 0, set: false };
const lastAt = {};
const log = [], counts = {};
const GAP = 0.03;       // the same effect twice within this many seconds is one

// Effects -> fx \
//                 master -> a compressor (several loud things at once never clip) -> out
// Ambience -> amb /
function chain(ctx, offline = false) {
    const master = ctx.createGain();
    master.gain.value = muted && !offline ? 0 : SOUND.volume;
    const squash = ctx.createDynamicsCompressor();
    squash.threshold.value = -10;
    squash.knee.value = 8;
    squash.ratio.value = 4;
    squash.attack.value = 0.003;
    squash.release.value = 0.2;
    master.connect(squash).connect(ctx.destination);
    const fx = ctx.createGain();
    fx.gain.value = SOUND.effects;
    fx.connect(master);
    const amb = ctx.createGain();
    amb.gain.value = SOUND.ambience;
    amb.connect(master);
    const n = ctx.sampleRate * 2, noise = ctx.createBuffer(1, n, ctx.sampleRate), d = noise.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    return { ctx, master, fx, amb, noise, layers: null, offline };
}

function audio() {
    if (off) return off;
    if (!enabled) return null;
    if (!live) {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return null;
        live = chain(new Ctx());
    }
    // Not started yet (no key pressed), or put to sleep by the browser: nothing is queued up to
    // burst out later.
    if (live.ctx.state !== 'running') {
        live.ctx.resume?.().catch(() => {});
        return null;
    }
    return live;
}
for (const e of ['keydown', 'pointerdown']) window.addEventListener(e, () => audio(), { passive: true });

// (`held`: its voices are made `HOLD` s long and kept, for `stop()` to fade out and end: a handle is returned.)
const HOLD = 30;
const NONE = { stop() {} };
function play(name, args, held = false) {
    const pos = nextPos;
    nextPos = null;
    counts[name] = (counts[name] || 0) + 1;
    log.push(name);
    if (log.length > 300) log.shift();
    const a = audio();
    if (!a || (muted && !a.offline)) return held ? NONE : undefined;
    const now = a.ctx.currentTime;
    let dest = a.fx;
    if (!a.offline) {
        // (Out of earshot first: a far one must not take the turn of a near one in the same moment.)
        let level = 1, dx = 0;
        if (pos && ear.set) {
            dx = pos.x - ear.x;
            const d = Math.hypot(dx, (pos.y - ear.y) * SOUND.deckWeight);
            level = d <= SOUND.near ? 1 : 1 - (d - SOUND.near) / (SOUND.far - SOUND.near);
            if (level <= 0.03) return held ? NONE : undefined;
        }
        if (!held && now - (lastAt[name] ?? -1) < GAP) return;
        lastAt[name] = now;
        if (pos && ear.set) {
            const g = a.ctx.createGain();
            g.gain.value = level * level;
            if (a.ctx.createStereoPanner) {
                const pan = a.ctx.createStereoPanner();
                pan.pan.value = Math.max(-0.7, Math.min(0.7, dx / 420));
                g.connect(pan).connect(a.fx);
            } else g.connect(a.fx);
            dest = g;
        }
    }
    let hold = null;
    if (held) {
        hold = a.ctx.createGain();
        hold.connect(dest);
        dest = hold;
    }
    const sources = [];
    cur = { c: a.ctx, a, dest, t: now + 0.005, sources };
    try {
        SOUNDS[name](...(held ? [HOLD, ...args] : args));
    } finally {
        cur = null;
    }
    if (!held) return;
    let done = false;
    return {
        stop(fade = 0.12) {
            if (done) return;
            done = true;
            const t = a.ctx.currentTime;
            hold.gain.setTargetAtTime(0, t, fade / 4);
            for (const src of sources) try { src.stop(t + fade + 0.05); } catch { /* already over */ }
        },
    };
}

// --- The voices every effect is made of -------------------------------------------------------------

// A value over an effect's length: a number, [from, to], or [[part of the length, value], ...].
function ramp(param, t0, dur, spec) {
    if (typeof spec === 'number') return void param.setValueAtTime(spec, t0);
    if (typeof spec[0] === 'number') spec = [[0, spec[0]], [1, spec[1]]];
    param.setValueAtTime(spec[0][1], t0);
    for (const [k, v] of spec.slice(1)) param.exponentialRampToValueAtTime(Math.max(v, 0.001), t0 + k * dur);
}

// Its loudness over its length: up in `attack`, then dying away to its end; with `release`, held
// until that long before the end; or a drawn `shape` (values 0 to 1, ending in 0).
function shaped(g, t0, dur, o) {
    const vol = o.vol ?? 0.1;
    if (o.shape) {
        g.gain.setValueAtTime(0, t0);
        g.gain.setValueCurveAtTime(Float32Array.from(o.shape, v => v * vol), t0 + 0.001, dur);
        return;
    }
    const attack = Math.min(o.attack ?? 0.004, dur * 0.5);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.linearRampToValueAtTime(vol, t0 + attack);
    if (o.release != null) g.gain.setValueAtTime(vol, t0 + Math.max(attack, dur - o.release));
    // (Down to a fiftieth by the end, then cut: dying away to nothing, most of its length was unheard.)
    g.gain.exponentialRampToValueAtTime(vol / 50, t0 + dur - 0.008);
    g.gain.linearRampToValueAtTime(0, t0 + dur);
}

// source -> (a low-pass `lp`) -> (a tremolo `trem`: [times a second, depth]) -> its loudness -> out
function finish(node, t0, dur, o) {
    const c = cur.c;
    let last = node;
    if (o.lp) {
        const f = c.createBiquadFilter();
        f.type = 'lowpass';
        f.Q.value = o.lq ?? 0.7;
        ramp(f.frequency, t0, dur, o.lp);
        last.connect(f);
        last = f;
    }
    if (o.trem) {
        const g = c.createGain(), l = c.createOscillator(), d = c.createGain();
        g.gain.value = 1 - o.trem[1] / 2;
        l.frequency.value = o.trem[0];
        d.gain.value = o.trem[1] / 2;
        l.connect(d).connect(g.gain);
        l.start(t0);
        l.stop(t0 + dur + 0.05);
        cur.sources.push(l);
        last.connect(g);
        last = g;
    }
    const g = c.createGain();
    shaped(g, t0, dur, o);
    last.connect(g);
    g.connect(cur.dest);
}

// A note. `to`: it slides there; `path`: its pitch over its length; `vib`: [times a second, Hz];
// `t`: seconds after the effect's start.
function tone(freq, dur, o = {}) {
    const c = cur.c, t0 = cur.t + (o.t ?? 0);
    const osc = c.createOscillator();
    osc.type = o.type ?? 'triangle';
    ramp(osc.frequency, t0, dur, o.path ?? (o.to ? [freq, o.to] : freq));
    if (o.vib) {
        const l = c.createOscillator(), d = c.createGain();
        l.frequency.value = o.vib[0];
        d.gain.value = o.vib[1];
        l.connect(d).connect(osc.frequency);
        l.start(t0);
        l.stop(t0 + dur + 0.05);
        cur.sources.push(l);
    }
    finish(osc, t0, dur, o);
    osc.start(t0);
    osc.stop(t0 + dur + 0.04);
    cur.sources.push(osc);
}

// Noise through one filter: `lo` (low-pass), `band` or `hp` (high-pass), each a value over its
// length as above; `q` the filter's sharpness.
function noise(dur, o = {}) {
    const c = cur.c, t0 = cur.t + (o.t ?? 0);
    const src = c.createBufferSource();
    src.buffer = cur.a.noise;
    src.loop = true;
    const f = c.createBiquadFilter();
    f.type = o.band ? 'bandpass' : o.hp ? 'highpass' : 'lowpass';
    f.Q.value = o.q ?? 0.8;
    ramp(f.frequency, t0, dur, o.band ?? o.hp ?? o.lo ?? 1800);
    src.connect(f);
    finish(f, t0, dur, { ...o, lp: null });
    src.start(t0, Math.random() * 1.5);
    src.stop(t0 + dur + 0.04);
    cur.sources.push(src);
}

const r = (a, b) => a + Math.random() * (b - a);
const hz = m => 440 * 2 ** ((m - 69) / 12);         // a MIDI note's pitch

// A struck bell or glass: a note with its overtones, the high ones dying first.
function bell(f, dur, vol, t = 0, ratios = [1, 2.76, 5.4, 8.93]) {
    ratios.forEach((k, i) => tone(f * k, dur / (1 + i * 0.7), { type: 'sine', vol: vol / (1 + i * 1.3), t }));
}
// Struck metal: overtones that are not in tune with each other, and the knock itself.
function clank(f, dur, vol, t = 0) {
    [1, 1.47, 2.09, 2.56, 3.39].forEach((k, i) => tone(f * k, dur / (1 + i * 0.4), { type: i ? 'triangle' : 'square', vol: vol / (1.6 + i), t, lp: 3200 }));
    noise(0.03, { hp: 2500, vol: vol * 0.7, t });
}
// Something soft and heavy coming down.
function thud(f, dur, vol, t = 0) {
    tone(f, dur, { type: 'sine', to: f * 0.55, vol, t });
}
// Notes one after another.
function run(notes, each, o = {}) {
    notes.forEach((f, i) => tone(f, (o.len ?? 1.6) * each, { ...o, t: (o.t ?? 0) + i * each }));
}
// A person's voice without words: a buzz through a mouth that opens and closes. `path` is its pitch.
function voice(path, dur, vol, t = 0, o = {}) {
    tone(path[0][1], dur, { type: 'sawtooth', path, vol, t, lp: o.lp ?? [[0, 800], [0.35, 1700], [1, 950]], lq: 2.2,
        attack: 0.02, release: dur * 0.35, vib: o.vib ?? [5.5, path[0][1] * 0.012] });
}
// A drawn loudness: `n` points from a function of 0..1, the last one 0.
function shape(n, fn) {
    const a = new Float32Array(n);
    for (let i = 0; i < n - 1; i++) a[i] = Math.max(0, Math.min(1, fn(i / (n - 1), i)));
    return a;
}
// Many hands clapping for `s` seconds, swelling and thinning out.
function applause(s, vol, t = 0) {
    const n = Math.round(s * 300);
    for (const band of [1300, 2100, 3000]) {
        noise(s, { band, q: 1.1, vol, t, shape: shape(n, k => (Math.random() < 0.3 ? r(0.5, 1) : 0.12) * Math.min(1, k * 5) * (1 - k) ** 0.8) });
    }
}
// A bubble rising: a short note that slides up.
function bloop(f, vol, t = 0) {
    tone(f, 0.07, { type: 'sine', to: f * 1.7, vol, t, attack: 0.01 });
}

// --- The effects --------------------------------------------------------------------------------------

const her = {
    jump: () => { tone(360, 0.13, { to: 740, vol: 0.144 }); noise(0.06, { band: 900, vol: 0.072 }); },
    // With a tray in her hands, or Bumbot in her arms: a small careful one.
    hop: () => tone(330, 0.1, { to: 520, vol: 0.104 }),
    // Her feet coming down on: 'carpet' (inside), 'deck' (the open decks' planks), 'metal', 'duct'.
    land: (on = 'carpet') => {
        thud(on === 'deck' ? 150 : 120, 0.09, 0.2);
        if (on === 'deck') noise(0.04, { band: 1400, q: 2, vol: 0.14 });
        else if (on === 'metal') clank(520, 0.12, 0.05);
        else if (on === 'duct') { tone(230, 0.16, { to: 180, vol: 0.12 }); noise(0.08, { band: 500, q: 3, vol: 0.16 }); }
        else noise(0.07, { lo: 480, vol: 0.16 });
    },
    // One footstep on the same, or on a 'stair', or a 'crawl''s shuffle.
    step: (on = 'carpet') => {
        if (on === 'deck') { noise(0.03, { band: 1700, q: 2.5, vol: 0.207 }); tone(170, 0.035, { type: 'sine', vol: 0.092 }); }
        else if (on === 'metal') { tone(r(760, 860), 0.06, { vol: 0.0805 }); noise(0.02, { hp: 3500, vol: 0.069 }); }
        else if (on === 'duct') { tone(r(210, 250), 0.08, { to: 190, vol: 0.115 }); noise(0.05, { band: 500, q: 3, vol: 0.23 }); }
        else if (on === 'stair') { noise(0.04, { lo: 900, vol: 0.161 }); tone(140, 0.03, { type: 'sine', vol: 0.069 }); }
        else if (on === 'crawl') noise(0.09, { lo: 520, vol: 0.115, attack: 0.03 });
        else noise(0.045, { lo: 650, vol: 0.19 });
    },
    // A ladder's rung under her hand.
    rung: () => { tone(r(600, 700), 0.05, { vol: 0.08 }); noise(0.015, { hp: 3000, vol: 0.06 }); },
    // A kick off a wall in the grip socks: the sole's squeak, then up.
    wallKick: () => { tone(1500, 0.05, { type: 'sine', to: 2100, vol: 0.04 }); noise(0.05, { band: 900, vol: 0.1 }); tone(330, 0.11, { to: 640, vol: 0.1, t: 0.02 }); },
    // Sliding down a wall on the socks.
    wallSlide: () => noise(0.14, { band: [1800, 1300], q: 3, vol: 0.15, attack: 0.03 }),
    // The parasol snapping open over her, and folding.
    parasolOpen: () => { noise(0.16, { band: [450, 1500], q: 0.9, vol: 0.2, attack: 0.06 }); thud(210, 0.06, 0.14, 0.14); },
    parasolShut: () => noise(0.1, { band: [1300, 420], q: 0.9, vol: 0.3 }),
    // "Кісюнічка!!!" (D): a bright rising cry, then its four syllables.
    cry: () => {
        tone(620, 0.18, { type: 'sawtooth', to: 1250, vol: 0.09, lp: 3200 });
        [1000, 1250, 1000, 1400].forEach((f, i) => tone(f, 0.09, { type: 'square', vol: 0.06, t: 0.18 + i * 0.07, lp: 3600 }));
    },
    // The lunge with it: a rush of air past her, and its end, a breath out.
    lunge: () => { noise(0.32, { band: [700, 2600], q: 0.8, vol: 0.16, attack: 0.04 }); thud(160, 0.05, 0.1, 0.1); },
    lungeEnd: () => tone(700, 0.16, { to: 400, vol: 0.112 }),
    // A hit taken by the pocket: a soft knock, and the tangerine popping out of it.
    pocket: () => { thud(200, 0.07, 0.16); tone(520, 0.09, { type: 'sine', to: 880, vol: 0.07, t: 0.04 }); noise(0.03, { band: 1800, vol: 0.06, t: 0.04 }); },
    // Her reactions to a hit taken by the pocket (docs/plan-three-uses.md §1.6), each with it: a
    // yelp at a flare's heat, a splutter at water in her face, a gasp at water down her back, a
    // sniff as she rubs her nose after a door.
    yelpHot: () => { tone(900, 0.07, { type: 'square', to: 1700, vol: 0.07, lp: 3600 }); tone(1500, 0.1, { type: 'square', to: 1100, vol: 0.05, t: 0.08, lp: 3200 }); },
    splutter: () => { [0, 0.09, 0.17].forEach((t, i) => noise(0.06, { band: [700 + i * 200, 2400], q: 1.2, vol: 0.12, t })); tone(420, 0.12, { type: 'sawtooth', to: 300, vol: 0.04, t: 0.05, lp: 1400 }); },
    gasp: () => { noise(0.22, { band: [1200, 3800], q: 0.9, vol: 0.1, attack: 0.04 }); tone(700, 0.18, { type: 'sine', to: 1100, vol: 0.05 }); },
    sniff: () => { noise(0.08, { band: [2200, 4200], q: 1.4, vol: 0.09 }); noise(0.1, { band: [2400, 4600], q: 1.4, vol: 0.08, t: 0.12 }); },
    // Her gags' own (§3 1.3, 2026-11-19; played on their clips' frames, `GAGS[...].sounds`):
    // spun round like a top (9a, 12a): a whirl that rises and falls over her turns.
    spin: () => { noise(0.62, { band: [[0, 600], [0.5, 1500], [1, 500]], q: 2, vol: 0.2, attack: 0.05, trem: [7, 0.6] }); tone(480, 0.62, { type: 'sine', path: [[0, 480], [0.5, 1100], [1, 420]], vol: 0.04, vib: [7, 60] }); },
    // Flat on her belly or her back on the floor (9c, 12b, 10c; the balls' and the boat's stiff fall): a slap and the floor.
    bellyFlop: () => { noise(0.05, { band: 1400, q: 0.8, vol: 0.26 }); thud(120, 0.16, 0.26, 0.01); noise(0.12, { lo: 500, vol: 0.12, t: 0.02 }); },
    // Tiptoeing off (23, 24): one tiny step, a soft tick.
    tiptoe: () => { noise(0.035, { band: 2600, q: 2, vol: 0.2 }); tone(r(1250, 1450), 0.04, { type: 'sine', vol: 0.06 }); },
    // Her cough, out of the steam or the soot (17, 19): two short light ones.
    herCough: () => [0, 0.18].forEach((t, i) => { noise(0.08, { band: [1500, 900], q: 1, vol: 0.2 - i * 0.05, t, attack: 0.008 }); voice([[0, 560], [1, 440]], 0.07, 0.035, t); }),
    // Her sneeze, soaked (16, 11a, 11b): a little breath in, then the "choo".
    herSneeze: () => { voice([[0, 520], [1, 680]], 0.14, 0.04, 0, { lp: [[0, 900], [1, 1800]] }); noise(0.16, { hp: [2400, 3800], vol: 0.1, t: 0.18, attack: 0.008 }); voice([[0, 780], [1, 460]], 0.12, 0.05, 0.18); },
    // A fright: her yelp.
    scare: () => { tone(760, 0.11, { type: 'square', to: 1480, vol: 0.08, lp: 3400 }); tone(1480, 0.14, { type: 'square', to: 1000, vol: 0.07, t: 0.11, lp: 3400 }); },
    // Running off after one.
    runOff: () => noise(0.35, { band: [500, 1500], q: 0.8, vol: 0.14, attack: 0.08 }),
    // A long fall out of the picture.
    fall: () => { tone(1300, 0.7, { type: 'sine', to: 280, vol: 0.09, attack: 0.03 }); noise(0.6, { band: [1400, 500], vol: 0.07, attack: 0.1 }); },
    // Into the water, all of her; and a small one (a jet, a paw, stepping out).
    splash: () => {
        noise(0.55, { lo: [2800, 500], vol: 0.3, attack: 0.01 });
        thud(240, 0.28, 0.16);
        for (let i = 0; i < 4; i++) bloop(r(700, 1500), 0.04, 0.16 + i * r(0.05, 0.09));
    },
    splashSmall: () => { noise(0.2, { lo: [2600, 800], vol: 0.182 }); bloop(r(800, 1200), 0.04, 0.06); },
    // A swimming stroke.
    stroke: () => noise(0.22, { lo: [900, 1900], vol: 0.091, attack: 0.08 }),
    // The cabin's shower running for `s` seconds, and a note of the song she hums in it (n = 0, 1, 2...).
    shower: (s = 4) => noise(s, { hp: 2600, vol: 0.036, attack: 0.3, release: 0.4 }),
    hum: (n = 0) => { const f = hz([72, 76, 79, 76, 81, 79, 77, 74][n % 8]); tone(f, 0.42, { type: 'sine', vol: 0.06, attack: 0.05, vib: [5.5, f * 0.012] }); },
    // The cabin's bed under her bounce.
    boing: () => tone(150, 0.3, { type: 'sine', path: [[0, 150], [0.25, 330], [1, 170]], vol: 0.168, vib: [17, 14] }),
    // Leaning into a cart: its wheels turning (one turn; called as it rolls).
    roll: () => { noise(0.12, { lo: 260, vol: 0.28, attack: 0.03 }); tone(r(900, 1100), 0.03, { type: 'sine', vol: 0.03, t: 0.05 }); },
    // Wading through the kids' ball pit: a few of its balls knocking.
    balls: () => { for (let i = 0; i < 5; i++) tone(r(500, 1300), 0.03, { type: 'sine', vol: 0.05, t: r(0, 0.18) }); },
};

const ship = {
    // A door on hinges opening (the latch, the leaf); shutting; one that slides (a lift's leaves, a
    // balcony's glass, the shower's); a steel one (an escape trunk, a wall across a deck).
    door: () => { noise(0.025, { hp: 2600, vol: 0.09 }); thud(150, 0.1, 0.14, 0.03); },
    doorShut: () => { thud(130, 0.1, 0.18); noise(0.02, { hp: 2600, vol: 0.08, t: 0.05 }); },
    doorSlide: () => noise(0.32, { band: [800, 1700], q: 1.2, vol: 0.1, attack: 0.1 }),
    doorHeavy: () => { thud(95, 0.26, 0.24); noise(0.07, { band: 1100, vol: 0.14 }); tone(480, 0.08, { type: 'square', vol: 0.03, lp: 1500, t: 0.02 }); },
    // One that flies open by itself, with a bang.
    doorBang: () => { thud(125, 0.2, 0.3); noise(0.09, { lo: 1600, vol: 0.26 }); },
    // A door that won't open from this side: two dull knocks of the handle.
    rattle: () => [0, 0.09].forEach(t => { noise(0.06, { lo: 520, vol: 0.2, t }); tone(310, 0.03, { type: 'square', vol: 0.02, lp: 900, t }); }),
    // A card reader: yes, and no (also a rope or a sign in her way).
    beep: () => { tone(1320, 0.07, { type: 'square', vol: 0.04, lp: 4000 }); tone(1760, 0.11, { type: 'square', vol: 0.04, lp: 4000, t: 0.08 }); },
    deny: () => [0, 0.15].forEach(t => tone(185, 0.12, { type: 'square', vol: 0.07, lp: 1200, t })),
    // A hatch's steel lid.
    hatch: () => { clank(310, 0.3, 0.14); thud(90, 0.15, 0.14, 0.02); },
    // Any struck metal: a grille kicked out of the duct, a pan.
    clang: () => clank(260, 0.45, 0.18),
    // An elevator: its car under way for `s` seconds, and its bell.
    liftMove: (s = 1) => { tone(72, s, { type: 'sine', path: [[0, 62], [0.2, 84], [0.8, 84], [1, 62]], vol: 0.06, attack: 0.15, release: 0.2 }); noise(s, { lo: 300, vol: 0.036, attack: 0.15, release: 0.2 }); },
    liftDing: () => { bell(988, 0.5, 0.07); bell(784, 0.7, 0.07, 0.16); },
    // The stage's trap going from under someone.
    trapdoor: () => { noise(0.04, { band: 1500, vol: 0.2 }); thud(160, 0.22, 0.24, 0.02); },
    // Down the laundry chute, and into the towels at its foot.
    chute: () => { noise(0.75, { band: [500, 1900], q: 1.4, vol: 0.2, attack: 0.1 }); tone(640, 0.75, { type: 'sine', to: 210, vol: 0.05 }); },
    flump: () => { noise(0.2, { lo: 320, vol: 0.51, attack: 0.02 }); thud(90, 0.21, 0.12); },
    // A rope whipping away (the stage's, into a door).
    whip: () => noise(0.14, { band: [1200, 4200], q: 1.6, vol: 0.16, attack: 0.04 }),
    // Old wood or a hinge complaining.
    creak: () => tone(300, 0.4, { type: 'sawtooth', path: [[0, 290], [0.5, 400], [1, 330]], vol: 0.05, lp: 1100, lq: 4, attack: 0.08, vib: [11, 9] }),
    // Something of wood or crockery going to pieces under the dash; and the same, generic.
    smash: () => { noise(0.2, { lo: [3000, 700], vol: 0.3 }); for (let i = 0; i < 4; i++) noise(0.03, { band: r(900, 2600), q: 3, vol: 0.14, t: r(0.02, 0.2) }); thud(140, 0.12, 0.14); },
    // Crockery, fruit, a tray going over.
    crash: () => { noise(0.14, { hp: 1800, vol: 0.2 }); for (let i = 0; i < 6; i++) bell(r(1700, 3600), 0.12, 0.035, r(0, 0.26), [1, 2.3]); thud(170, 0.1, 0.1); },
    // Something soft going over: a cake, an ice cream cone.
    splat: () => { noise(0.16, { lo: [1500, 320], vol: 0.3, attack: 0.01 }); thud(120, 0.1, 0.14); bloop(r(240, 320), 0.05, 0.05); },
    // A load on her tray swaying near to going over: two anxious little notes.
    wobble: () => { tone(520, 0.07, { type: 'sine', to: 470, vol: 0.06 }); tone(560, 0.08, { type: 'sine', to: 500, vol: 0.06, t: 0.1 }); },
    // A lever thrown.
    lever: () => { tone(170, 0.08, { type: 'square', to: 100, vol: 0.08, lp: 700 }); noise(0.02, { hp: 2000, vol: 0.09, t: 0.06 }); },
    // A bookcase, a wall sliding aside.
    rumble: () => { noise(0.9, { lo: 240, vol: 0.204, attack: 0.15, release: 0.3 }); tone(48, 0.9, { type: 'sine', vol: 0.072, attack: 0.15, release: 0.3, trem: [13, 0.5] }); },
    // The gate's bars coming down, one clank each.
    ratchet: () => clank(r(420, 520), 0.09, 0.08),
    // The ship's horn: three low notes together, with the breath of the steam.
    horn: (s = 3) => {
        for (const [f, v] of [[103.8, 0.04], [130.8, 0.034], [155.6, 0.026]]) {
            for (const d of [-0.5, 0.6]) {
                tone(f + d, s, { type: 'sawtooth', vol: v, attack: Math.min(0.18, s / 4), release: Math.min(0.45, s / 3),
                    lp: [[0, 260], [0.12, 1000], [0.9, 900], [1, 240]], trem: [5.2, 0.08] });
            }
        }
        tone(51.9, s, { type: 'sine', vol: 0.09, attack: Math.min(0.25, s / 4), release: Math.min(0.5, s / 3) });
        noise(s, { band: 420, q: 0.7, vol: 0.045, attack: Math.min(0.2, s / 4), release: Math.min(0.4, s / 3) });
    },
    // The bridge's alarm: `n` whoops, half a second each.
    alarm: (n = 2) => {
        for (let i = 0; i < n; i++) {
            tone(520, 0.44, { type: 'sawtooth', path: [[0, 520], [0.85, 1040], [1, 1040]], vol: 0.1, lp: 2600, t: i * 0.5, attack: 0.02, release: 0.05 });
        }
    },
};

const finds = {
    // A tangerine; something into her hands (a tray, a cup, a load); something handed over.
    tangerine: () => { tone(880, 0.08, { vol: 0.1 }); tone(1320, 0.13, { vol: 0.1, t: 0.06 }); },
    // That tangerine landing at the HUD's count after its flight (§1.7): a small soft pluck.
    tally: () => { tone(1760, 0.05, { type: 'sine', vol: 0.06 }); tone(2640, 0.07, { type: 'sine', vol: 0.04, t: 0.03 }); },
    pickup: () => { tone(880, 0.08, { vol: 0.1 }); tone(1320, 0.13, { vol: 0.1, t: 0.06 }); },
    take: () => { tone(620, 0.06, { vol: 0.09 }); tone(930, 0.1, { vol: 0.09, t: 0.05 }); },
    give: () => { tone(930, 0.06, { vol: 0.09 }); tone(700, 0.11, { vol: 0.09, t: 0.05 }); },
    // A checkpoint's lamp coming on.
    checkpoint: () => { run([523, 659, 784], 0.07, { vol: 0.1, len: 2.2 }); tone(1568, 0.5, { type: 'sine', vol: 0.03, t: 0.14 }); },
    // A key card; a new way to move; an errand done; a secret found.
    card: () => run([1047, 1319, 1568, 2093], 0.06, { vol: 0.08, len: 2.4 }),
    verb: () => { run([392, 523, 659, 784], 0.08, { vol: 0.09, len: 2 }); [523, 659, 784, 1047].forEach(f => tone(f, 0.7, { type: 'sine', vol: 0.045, t: 0.34, attack: 0.02 })); },
    done: () => { run([659, 784, 1047], 0.07, { vol: 0.09, len: 2 }); [784, 988, 1319].forEach(f => tone(f, 0.5, { type: 'sine', vol: 0.04, t: 0.2 })); },
    secret: () => [1568, 2093, 1760, 2637, 2349, 3136].forEach((f, i) => tone(f, 0.22, { type: 'sine', vol: 0.05, t: i * 0.055 })),
    // A glint: three small high notes.
    sparkle: () => [2093, 2637, 3136].forEach((f, i) => tone(f, 0.16, { type: 'sine', vol: 0.04, t: i * 0.05 })),
    // Paper: a page turned, a book pushed home on its shelf.
    page: () => noise(0.14, { hp: [2500, 5000], vol: 0.09, attack: 0.04 }),
    book: () => { thud(210, 0.105, 0.14); noise(0.1, { hp: 3000, vol: 0.075, attack: 0.03 }); },
    // A camera.
    shutter: () => { noise(0.015, { hp: 3000, vol: 0.16 }); noise(0.025, { hp: 2200, vol: 0.14, t: 0.07 }); },
    // Her bubble or theirs popping up; a little heart.
    bubble: () => { tone(900, 0.035, { vol: 0.068 }); tone(1250, 0.05, { vol: 0.068, t: 0.03 }); },
    heart: () => { tone(784, 0.14, { type: 'sine', vol: 0.07 }); tone(988, 0.24, { type: 'sine', vol: 0.07, t: 0.1 }); },
    // Bumbot's collar bell: a little jingle bell shaken, as the gull lets it go and as it lands on the deck.
    jingle: () => { for (let i = 0; i < 4; i++) bell(r(3900, 4700), 0.2, 0.03, i * 0.055 + r(0, 0.02), [1, 1.58, 2.37]); },
    // One struck bell: an elevator's, a counter's.
    ding: () => { bell(988, 0.4, 0.07); bell(784, 0.6, 0.07, 0.14); },
    // Air moved by something quick, generic.
    whoosh: () => noise(0.35, { band: [500, 1300], q: 0.8, vol: 0.14, attack: 0.1 }),
    // The welcome screen: a plate chosen with the arrows, or the language switched.
    choose: () => tone(2000, 0.035, { type: 'square', vol: 0.09, lp: 5000 }),
    // The intro's camera diving down from the sky into the ship: a soft rush of air, swelling.
    swell: () => noise(2.2, { band: [300, 1400], q: 0.7, vol: 0.09, attack: 1.5, release: 0.35 }),
    // Sound switched on again (M).
    soundOn: () => run([660, 990], 0.07, { vol: 0.08 }),
};

const cat = {
    // Bumbot: his "mrrp" as he slips away, a meow, his purr for `s` seconds, his claws on the floor.
    mrrp: () => { tone(520, 0.09, { to: 820, vol: 0.1 }); tone(820, 0.15, { to: 560, vol: 0.09, t: 0.09 }); },
    meow: () => tone(600, 0.5, { type: 'sawtooth', path: [[0, 590], [0.25, 900], [0.6, 840], [1, 610]], vol: 0.07,
        lp: [[0, 1100], [0.3, 2700], [1, 1300]], lq: 3, attack: 0.04, release: 0.2, vib: [6, 7] }),
    purr: (s = 1.6) => {
        const n = Math.round(s * 400), breath = k => 0.35 + 0.65 * Math.sin(Math.PI * ((k * s / 0.8) % 1)) ** 0.7;
        noise(s, { lo: 210, vol: 0.3, shape: shape(n, (k, i) => (1 - ((i / 16) % 1)) * breath(k)) });
        tone(54, s, { type: 'sawtooth', vol: 0.07, lp: 320, shape: shape(n, (k, i) => (1 - ((i / 16) % 1)) * breath(k)) });
    },
    // His small quick bites, eating off the floor.
    nom: () => [0, 0.11, 0.22].forEach(t => noise(0.04, { lo: [2400, 900], vol: 0.08, t, attack: 0.01 })),
    scramble: () => { for (let i = 0; i < 6; i++) noise(0.018, { hp: 2800, vol: 0.09, t: i * 0.045 + r(0, 0.01) }); },
};

const people = {
    // Someone humming in a shut stall (the restrooms by the Chapel): a phrase of a tune through the door, muffled (n: which).
    stallHum: (n = 0) => {
        // (Louder than at first and its door a little less thick: the user could not hear anyone, 2026-11-25. Its phrases
        // are src/world/soundscape.js's STALL_TUNES, which draws a note over the stall for each.)
        const tunes = [[67, 69, 71, 67], [72, 71, 69, 67, 69], [64, 67, 69, 67], [71, 72, 74, 72, 71]];
        tunes[n % 4].forEach((m, i) => voice([[0, hz(m - 12)], [1, hz(m - 12) * 1.01]], 0.3, 0.1, i * 0.32, { lp: [[0, 600], [0.5, 950], [1, 700]] }));
    },
    // Voices without words. A shout at her ("Гей!"), a startled "oh", a kid's giggle, a man's yelp
    // as his feet go, a grumble, a pleased "aah".
    hey: () => voice([[0, 300], [0.3, 440], [1, 380]], 0.24, 0.1),
    oh: () => voice([[0, 520], [1, 360]], 0.2, 0.08, 0, { lp: [[0, 1300], [1, 800]] }),
    giggle: () => [1050, 1250, 1100, 1350, 1150].forEach((f, i) => tone(f, 0.07, { vol: 0.06, t: i * 0.075, to: f * 1.12 })),
    yelp: () => voice([[0, 330], [0.35, 620], [1, 300]], 0.36, 0.1),
    grumble: () => voice([[0, 150], [0.5, 130], [1, 110]], 0.4, 0.09, 0, { lp: [[0, 500], [1, 380]], vib: [9, 5] }),
    aah: () => voice([[0, 330], [0.4, 390], [1, 350]], 0.5, 0.07, 0, { lp: [[0, 900], [0.4, 1500], [1, 1100]] }),
    // Someone asleep behind a door: in, and out.
    snore: () => { noise(0.8, { band: [170, 240], q: 4, vol: 0.65, attack: 0.5, trem: [28, 0.6] }); tone(880, 0.5, { type: 'sine', to: 700, vol: 0.0156, t: 0.95, attack: 0.1 }); },
    // Hands: clapping for `s` seconds; with voices on top.
    clap: (s = 1.6) => applause(s, 0.2),
    cheer: (s = 2.2) => { applause(s, 0.18); for (let i = 0; i < 4; i++) voice([[0, r(330, 420)], [0.5, r(520, 680)], [1, r(420, 520)]], r(0.5, 0.9), 0.035, r(0, s * 0.4)); },
    // A kiss.
    kiss: () => { tone(1300, 0.06, { type: 'sine', to: 2500, vol: 0.112 }); tone(2100, 0.2, { type: 'sine', vol: 0.048, t: 0.08 }); },
    // An officer's whistle.
    whistle: () => tone(2200, 0.5, { type: 'sine', vol: 0.06, attack: 0.02, release: 0.06, vib: [28, 60] }),
    // A sneeze, a "shh", someone chewing, a man's short laugh.
    sneeze: () => { voice([[0, 420], [1, 520]], 0.16, 0.05, 0, { lp: [[0, 700], [1, 1400]] }); noise(0.2, { hp: [1800, 3200], vol: 0.09, t: 0.17, attack: 0.01 }); voice([[0, 600], [1, 330]], 0.16, 0.07, 0.17); },
    shush: () => noise(0.45, { band: [3600, 4600], q: 1.2, vol: 0.07, attack: 0.08, release: 0.12 }),
    // Her soft call to Bumbot on the bridge (near-catch 6): three short hisses, "pss-pss-pss".
    pspsps: () => [0, 0.17, 0.34].forEach(t => noise(0.1, { band: [5200, 6800], q: 1.4, vol: 0.07, t, attack: 0.012, release: 0.05 })),
    munch: () => [0, 0.17, 0.34].forEach(t => noise(0.07, { lo: [1300, 500], vol: 0.14, t, attack: 0.015 })),
    // A sip from a cup or a glass, and its swallow; a lick of an ice cream cone.
    sip: () => { noise(0.24, { band: [1100, 2600], q: 2.5, vol: 0.08, attack: 0.05, trem: [38, 0.5] }); tone(240, 0.09, { type: 'sine', to: 150, vol: 0.05, t: 0.32 }); },
    lick: () => noise(0.16, { band: [2600, 1700], q: 1.8, vol: 0.11, attack: 0.04 }),
    laugh: () => [0, 0.13, 0.26, 0.39].forEach((t, i) => voice([[0, 300 - i * 18], [1, 240 - i * 14]], 0.1, 0.07 - i * 0.01, t, { vib: [0, 0] })),
    // Knuckles on a door, once.
    knock: () => { thud(210, 0.06, 0.2); noise(0.02, { band: 900, vol: 0.12 }); },
    // Someone going over: a tumble.
    tumble: () => [0, 0.11, 0.2].forEach((t, i) => { thud(140 - i * 20, 0.09, 0.2 - i * 0.04, t); noise(0.05, { lo: 600, vol: 0.14, t }); }),
    // A party horn through a door.
    toot: () => tone(440, 0.3, { type: 'sawtooth', path: [[0, 400], [0.15, 470], [1, 455]], vol: 0.06, lp: 2200, lq: 3, attack: 0.02, release: 0.05 }),
    // Wedding bells: two, ringing on.
    bells: () => { bell(659, 1.8, 0.07, 0, [0.5, 1, 1.19, 1.5, 2, 2.51]); bell(523, 2, 0.07, 0.32, [0.5, 1, 1.19, 1.5, 2, 2.51]); bell(784, 1.6, 0.06, 0.64, [0.5, 1, 1.19, 1.5, 2, 2.51]); },
    // The piano in the atrium: note `n` of the tune she picks out.
    piano: (n = 0) => {
        const f = hz([64, 67, 72, 71, 67, 69, 65, 67, 64, 62, 60, 64, 67, 72, 74, 72][n % 16]);
        tone(f, 0.9, { type: 'triangle', vol: 0.1, attack: 0.005 });
        tone(f * 2, 0.5, { type: 'sine', vol: 0.03 });
        tone(f * 3, 0.25, { type: 'sine', vol: 0.012 });
    },
};

const things = {
    // The delivery robot with her in its way.
    robotBeep: () => [0, 0.13].forEach(t => tone(1400, 0.07, { type: 'square', vol: 0.042, lp: 4000, t })),
    // Housekeeping's vacuum: its motor winding up (the tell), and its dart.
    vacRev: () => tone(170, 0.32, { type: 'sawtooth', to: 560, vol: 0.112, lp: 1500 }),
    // The small dog on deck 4's lead: a yap (two short barks), and its howl back at her cry.
    bark: () => [0, 0.14].forEach(t => { tone(820, 0.08, { type: 'sawtooth', path: [[0, 760], [0.3, 980], [1, 640]], vol: 0.07, lp: 2600, t, attack: 0.01 }); noise(0.05, { band: 1400, vol: 0.08, t }); }),
    howl: () => tone(620, 1.0, { type: 'sawtooth', path: [[0, 520], [0.35, 880], [0.8, 820], [1, 560]], vol: 0.06, lp: 2200, lq: 3, attack: 0.1, release: 0.3, vib: [6, 14] }),
    // A folded paper skimmed along the carpet (the paper round).
    paperSlide: () => noise(0.4, { band: [2600, 1600], q: 1.2, vol: 0.12, attack: 0.02, release: 0.2 }),
    // A vacuum that has swallowed a tangerine: the motor chokes, sputters and winds down.
    vacChoke: () => { tone(420, 0.8, { type: 'sawtooth', path: [[0, 420], [0.25, 560], [1, 80]], vol: 0.08, lp: 1400, trem: [16, 0.6] }); [0.12, 0.34, 0.58].forEach(t => noise(0.08, { lo: [900, 300], vol: 0.22, t })); },
    vacDart: () => { tone(560, 0.5, { type: 'sawtooth', path: [[0, 560], [0.2, 720], [1, 420]], vol: 0.07, lp: 1700 }); noise(0.5, { band: 1100, vol: 0.12, attack: 0.05 }); },
    // Cloth: a stack of towels leaning, and coming down; a sheet in the wind.
    cloth: () => { noise(0.1, { lo: 900, vol: 0.2, attack: 0.03 }); noise(0.1, { lo: 900, vol: 0.16, attack: 0.03, t: 0.13 }); },
    towelFall: () => { noise(0.32, { lo: [1200, 300], vol: 0.34, attack: 0.03 }); thud(85, 0.2, 0.14, 0.1); },
    flap: () => { for (let i = 0; i < 5; i++) noise(0.06, { band: r(600, 1000), q: 1.2, vol: 0.14, attack: 0.02, t: i * 0.075 }); },
    // A sprinkler: the ticks before it, and its rain for `s` seconds.
    tick: () => [0, 0.14, 0.28].forEach(t => tone(2400, 0.025, { type: 'square', vol: 0.042, lp: 5000, t })),
    spray: (s = 1.2) => noise(s, { hp: 3200, vol: 0.066, attack: 0.08, release: 0.3 }),
    // A thin jet of water (the kid's pistol).
    jet: () => noise(0.24, { band: [2800, 1700], q: 1.6, vol: 0.2, attack: 0.02 }),
    // Her foot going on a wet floor.
    slip: () => { tone(900, 0.24, { type: 'sine', to: 1600, vol: 0.06, vib: [22, 40] }); noise(0.25, { band: [700, 1500], vol: 0.1, attack: 0.05 }); },
    // Furniture dragged or rocking: a deck chair's legs.
    scrape: () => noise(0.3, { band: [620, 760], q: 5, vol: 0.75, attack: 0.04, trem: [34, 0.7] }),
    // A gull: its cry (three falling calls); taking off; diving at her.
    gull: () => [0, 0.2, 0.4].forEach((t, i) => tone(1500, 0.17, { type: 'sawtooth', path: [[0, 1250 - i * 60], [0.25, 1650 - i * 80], [1, 1100 - i * 60]], vol: 0.045 - i * 0.008, lp: 3400, lq: 2, t, attack: 0.015 })),
    gullDive: () => { tone(1700, 0.34, { type: 'sawtooth', path: [[0, 1750], [1, 1150]], vol: 0.05, lp: 3400, lq: 2, attack: 0.02 }); noise(0.4, { band: [1400, 600], vol: 0.12, attack: 0.12 }); },
    // Wind: a gust rising and dying over `s` seconds.
    gust: (s = 1.6) => noise(s, { band: [[0, 320], [0.45, 950], [1, 380]], q: 1.1, vol: 0.204, attack: s * 0.4 }),
    // The pool emptying: `s` seconds of gurgle, and the last suck.
    drain: (s = 2.6) => {
        noise(s, { lo: [700, 260], vol: 0.2, attack: 0.2, release: 0.4, trem: [7, 0.5] });
        for (let i = 0, n = Math.round(s * 9); i < n; i++) bloop(r(160, 420) * (1 - 0.4 * i / n), 0.07, (i + r(0, 0.8)) * s / n);
        tone(300, 0.4, { type: 'sine', to: 90, vol: 0.1, t: s - 0.3 });
    },
    // The soft serve machine: its motor for `s` seconds (held while she holds E: `sfx.hold('whirr')`), its
    // running down when she lets go; a cough when it is empty.
    // The restrooms' hand dryer for `s` seconds: a blower's rush and its motor under it.
    dryer: (s = 2.4) => {
        noise(s, { band: 900, q: 0.6, vol: 0.16, attack: 0.15, release: 0.35 });
        noise(s, { hp: 2400, vol: 0.05, attack: 0.15, release: 0.35 });
        tone(210, s, { type: 'sawtooth', vol: 0.03, lp: 700, attack: 0.15, release: 0.3, trem: [37, 0.3] });
    },
    whirr: (s = 1) => tone(118, s, { type: 'sawtooth', vol: 0.06, lp: 520, attack: 0.08, release: 0.12, trem: [31, 0.4] }),
    whirrDown: () => tone(118, 0.35, { type: 'sawtooth', to: 62, vol: 0.05, lp: [520, 300], trem: [24, 0.4] }),
    cough: () => [0, 0.16].forEach(t => noise(0.1, { lo: [900, 350], vol: 0.26, t })),
    // A drink poured, glass on glass, a cup put down.
    pour: () => { for (let i = 0; i < 9; i++) bloop(r(500, 900) + i * 40, 0.035, i * 0.07 + r(0, 0.03)); noise(0.7, { band: 2400, q: 1.5, vol: 0.05, attack: 0.1 }); },
    clink: () => { bell(2637, 0.224, 0.05, 0, [1, 2.3]); bell(3520, 0.32, 0.04, 0.03, [1, 2.3]); },
    // A dull knock on the head (a lamp, a door's leaf).
    bonk: () => { thud(190, 0.12, 0.26); tone(560, 0.07, { type: 'sine', vol: 0.05 }); noise(0.02, { band: 800, vol: 0.12 }); },
    // A small soft thing dropped on the deck.
    plop: () => { thud(230, 0.07, 0.14); noise(0.04, { lo: 700, vol: 0.12 }); },
    // The hot tub bubbling for `s` seconds.
    bubbles: (s = 1.2) => { for (let i = 0, n = Math.round(s * 14); i < n; i++) bloop(r(260, 620), 0.035, r(0, s)); noise(s, { lo: 500, vol: 0.08, attack: 0.15, release: 0.3 }); },
    // A flash unit charging: its rising whine.
    flashCharge: (s = 0.7) => tone(1800, s, { type: 'sine', to: 5200, vol: 0.02, attack: s * 0.6 }),
    // The casino: chips, and a machine's little win.
    chips: () => { for (let i = 0; i < 7; i++) tone(r(2600, 4200), 0.025, { vol: 0.056, t: r(0, 0.22) }); },
    // The theatre's popcorn: the tub's rustle as it tips (the tell), and the popcorn pattering onto the carpet.
    popcornRustle: () => { for (let i = 0; i < 6; i++) noise(0.05, { band: r(2200, 3400), q: 1.4, vol: 0.09, attack: 0.01, t: i * 0.11 + r(0, 0.04) }); },
    popcornSpill: () => { for (let i = 0; i < 10; i++) noise(0.02, { band: r(1500, 2600), q: 2, vol: 0.1, t: r(0, 0.35) }); },
    slot: () => run([hz(84), hz(88), hz(91), hz(96)].sort(() => Math.random() - 0.5), 0.07, { vol: 0.0455, len: 1.8 }),
    // The court: a ball on the deck, through the air, through the net.
    bounce: () => { thud(165, 0.1, 0.26); noise(0.025, { band: 650, q: 2, vol: 0.14 }); tone(420, 0.06, { type: 'sine', vol: 0.03, t: 0.01 }); },
    toss: () => noise(0.2, { band: [700, 1300], vol: 0.1, attack: 0.07 }),
    swish: () => noise(0.2, { band: [3200, 1500], q: 1.4, vol: 0.2, attack: 0.03 }),
    // Teppanyaki's burner flaring up; the sauna's stove letting off steam for `s` seconds.
    flare: () => { noise(0.55, { lo: [[0, 260], [0.25, 1700], [1, 220]], vol: 0.242, attack: 0.1 }); for (let i = 0; i < 5; i++) noise(0.012, { hp: 3000, vol: 0.0385, t: r(0.15, 0.5) }); },
    steam: (s = 1) => noise(s, { hp: 4200, vol: 0.066, attack: Math.min(0.15, s / 3), release: Math.min(0.4, s / 2) }),
    // A net swung through the air.
    net: () => noise(0.18, { band: [900, 3600], q: 1.5, vol: 0.2, attack: 0.07 }),
    // The kids' slide under her.
    slide: () => { noise(0.8, { band: [700, 1600], q: 1.6, vol: 0.2, attack: 0.1 }); tone(700, 0.8, { type: 'sine', path: [[0, 700], [0.45, 1350], [1, 620]], vol: 0.05, vib: [7, 16], attack: 0.06 }); },
    // A telescope's draw-tube.
    scope: () => { tone(520, 0.14, { type: 'sine', to: 1500, vol: 0.05 }); noise(0.015, { hp: 3000, vol: 0.09, t: 0.14 }); },
    // Small steady things of a place: the bridge's radar, a party's beat through its door.
    ping: () => { tone(1480, 0.5, { type: 'sine', vol: 0.09 }); tone(1480, 0.4, { type: 'sine', vol: 0.028, t: 0.24 }); },
    thump: () => thud(78, 0.15, 0.3),
    // The gags' things (§3 1.3, 2026-11-19; on their clips' frames, `GAGS[...].sounds`):
    // the porter's luggage cart bumped (8a to 8d): its rail's knock, the bags rocking on it.
    cartBump: () => { clank(330, 0.16, 0.1); thud(150, 0.12, 0.18, 0.01); [0.07, 0.15].forEach(t => noise(0.05, { lo: 700, vol: 0.12, t })); },
    // The breakfast trolley jolted (10c, 10d, 10f): cups and plates jingling on it, its wheels.
    trolleyRattle: () => { for (let i = 0; i < 5; i++) bell(r(2300, 3400), 0.1, 0.03, r(0, 0.2), [1, 2.3]); noise(0.22, { lo: 600, vol: 0.12, trem: [24, 0.6] }); },
    // A basketball on her head (14a, 14b): a hollow rubber bonk.
    headBonk: () => { tone(330, 0.16, { type: 'sine', path: [[0, 380], [0.15, 300], [1, 250]], vol: 0.16 }); noise(0.025, { band: 700, q: 1.5, vol: 0.14 }); tone(660, 0.08, { type: 'triangle', vol: 0.03 }); },
    // The drill's boat on her head (15): a hollow wooden thump.
    boatThump: () => { thud(105, 0.24, 0.3); noise(0.06, { band: 450, q: 1.2, vol: 0.2 }); tone(210, 0.12, { type: 'triangle', to: 180, vol: 0.05, lp: 900 }); },
    // The towel stack's heap landing on her (18): soft, muffled, heavy.
    towelFlump: () => { noise(0.28, { lo: [700, 200], vol: 0.4, attack: 0.02 }); thud(80, 0.18, 0.12, 0.03); },
};

const ending = {
    // The sun going down before her: a quiet chord, swelling and going for `s` seconds.
    sunset: (s = 5) => [196, 246.9, 293.7, 370, 587.3].forEach((f, i) => tone(f, s, { type: 'sine', vol: 0.0315 - i * 0.004, attack: s * 0.35, t: i * 0.25 })),
    // Bumbot in her arms.
    caught: () => { [392, 494, 587, 784].forEach((f, i) => tone(f, 1.6, { type: 'sine', vol: 0.042, t: i * 0.09, attack: 0.03 })); [1568, 1976, 2349].forEach((f, i) => tone(f, 0.3, { type: 'sine', vol: 0.021, t: 0.5 + i * 0.08 })); },
    // The win screen: four chords, picked out and left ringing.
    win: () => {
        [[60, 64, 67, 72], [65, 69, 72, 77], [67, 71, 74, 79], [72, 76, 79, 84]].forEach((chord, c) => {
            chord.forEach((m, i) => bell(hz(m), c === 3 ? 2.4 : 0.9, c === 3 ? 0.055 : 0.045, c * 0.52 + i * 0.07, [1, 2, 3.01]));
        });
        tone(hz(36), 3.6, { type: 'sine', vol: 0.042, attack: 0.3 });
    },
};

const GROUPS = { 'Her': her, 'The ship': ship, 'Finds and signs': finds, 'Bumbot': cat, 'People': people, 'Things': things, 'The end': ending };
const SOUNDS = Object.assign({}, ...Object.values(GROUPS));

// --- The ambience: layers that run all the time, each as loud as the game says -------------------------

function startAmbience(a) {
    const c = a.ctx;
    const src = rate => {
        const s = c.createBufferSource();
        s.buffer = a.noise;
        s.loop = true;
        s.playbackRate.value = rate;
        s.start(0, Math.random() * 1.5);
        return s;
    };
    const filter = (type, f, q = 0.7) => {
        const n = c.createBiquadFilter();
        n.type = type;
        n.frequency.value = f;
        n.Q.value = q;
        return n;
    };
    const gain = v => { const g = c.createGain(); g.gain.value = v; return g; };
    const lfo = (hz, depth, param) => { const o = c.createOscillator(); o.frequency.value = hz; o.start(); o.connect(gain(depth)).connect(param); };
    const osc = (type, f) => { const o = c.createOscillator(); o.type = type; o.frequency.value = f; o.start(); return o; };
    const layer = build => { const g = gain(0); build(g); g.connect(a.amb); return g; };
    a.layers = {
        // The sea along the side: a low wash that swells and sinks, and the hiss of its foam.
        sea: layer(g => {
            const wash = gain(0.3);
            lfo(0.09, 0.13, wash.gain);
            lfo(0.151, 0.08, wash.gain);
            src(0.9).connect(filter('lowpass', 520)).connect(wash).connect(g);
            const hiss = gain(0.04);
            lfo(0.113, 0.028, hiss.gain);
            src(1.1).connect(filter('bandpass', 2600, 0.5)).connect(hiss).connect(g);
        }),
        // The engines, felt more than heard: low notes with a slow throb.
        engine: layer(g => {
            const throb = gain(0.14);
            lfo(1.9, 0.02, throb.gain);
            const low = filter('lowpass', 300);
            osc('sine', 46.2).connect(gain(0.5)).connect(low);
            osc('sine', 92.9).connect(gain(0.3)).connect(low);
            osc('triangle', 138.6).connect(gain(0.1)).connect(low);
            src(0.7).connect(filter('lowpass', 110)).connect(gain(0.5)).connect(low);
            low.connect(throb).connect(g);
        }),
        // The wind over the open decks, never quite steady.
        wind: layer(g => {
            const band = filter('bandpass', 520, 1.1);
            lfo(0.07, 170, band.frequency);
            lfo(0.23, 90, band.frequency);
            const blow = gain(0.34);
            lfo(0.13, 0.15, blow.gain);
            lfo(0.31, 0.07, blow.gain);
            src(1).connect(band).connect(blow).connect(g);
        }),
        // Inside: the ventilation's hush.
        air: layer(g => src(0.8).connect(filter('highpass', 180)).connect(filter('lowpass', 850)).connect(gain(0.07)).connect(g)),
        // Water in a pool, lapping at its side.
        water: layer(g => {
            const lap = gain(0.2);
            lfo(0.7, 0.1, lap.gain);
            lfo(1.13, 0.065, lap.gain);
            const band = filter('bandpass', 950, 1);
            lfo(0.43, 260, band.frequency);
            src(1.2).connect(band).connect(lap).connect(g);
        }),
    };
}

function ambience(levels) {
    const a = audio();
    if (!a) return;
    if (!a.layers) startAmbience(a);
    const now = a.ctx.currentTime;
    for (const [name, node] of Object.entries(a.layers)) {
        const v = Math.max(0, Math.min(1.5, levels[name] ?? 0));
        if (a.offline) node.gain.value = v;
        else node.gain.setTargetAtTime(v, now, 0.5);
    }
}

// --- What the game calls --------------------------------------------------------------------------------

export const sfx = {
    unlock: () => audio(),
    // (Only for an effect whose first argument is its length in seconds.)
    hold: (name, ...args) => play(name, args, true),
    at(x, y) {
        nextPos = { x, y };
        return sfx;
    },
    listen(x, y) {
        ear.x = x;
        ear.y = y;
        ear.set = true;
    },
    ambience,
    get muted() {
        return muted;
    },
    get enabled() {
        return enabled;
    },
    get running() {
        return !!live && live.ctx.state === 'running';
    },
    toggle() {
        muted = !muted;
        localStorage.setItem(KEY, muted ? 'off' : 'on');
        if (live) live.master.gain.setTargetAtTime(muted ? 0 : SOUND.volume, live.ctx.currentTime, 0.03);
        if (!muted) sfx.soundOn();
        return muted;
    },
    counts,
    log,
    // For the tools: the effects by group, and one of them (or the ambience at some levels)
    // rendered to samples.
    groups: Object.fromEntries(Object.entries(GROUPS).map(([k, v]) => [k, Object.keys(v)])),
    layers: ['sea', 'engine', 'wind', 'air', 'water'],
    // (An effect that takes something is shown on the soundboard once for each of these.)
    demos: {
        land: [['carpet'], ['deck'], ['metal'], ['duct']],
        step: [['carpet'], ['deck'], ['metal'], ['duct'], ['stair'], ['crawl']],
        horn: [[3], [0.5]],
        piano: [[0], [1], [2], [3]],
        hum: [[0], [1], [2]],
    },
    async render(name, args = [], seconds = 2, rate = 44100) {
        const ctx = new OfflineAudioContext(2, Math.ceil(seconds * rate), rate);
        off = chain(ctx, true);
        try {
            if (name === 'ambience') ambience(args[0] || {});
            else play(name, args);
        } finally {
            off = null;
        }
        const buf = await ctx.startRendering();
        return [buf.getChannelData(0), buf.getChannelData(1)];
    },
};
for (const name of Object.keys(SOUNDS)) sfx[name] = (...args) => play(name, args);
