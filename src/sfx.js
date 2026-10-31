// Synthesised sound effects (§7.1). No audio files. The context starts on the first user gesture,
// which the title screen's Start always provides.

let ctx = null;

function audio() {
    if (!ctx) {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return null;
        ctx = new Ctx();
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
}

function tone(freq, duration, { type = 'square', volume = 0.06, slideTo = null, delay = 0 } = {}) {
    const a = audio();
    if (!a) return;
    const t0 = a.currentTime + delay;
    const osc = a.createOscillator();
    const gain = a.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t0);
    if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, t0 + duration);
    gain.gain.setValueAtTime(volume, t0);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duration);
    osc.connect(gain).connect(a.destination);
    osc.start(t0);
    osc.stop(t0 + duration + 0.02);
}

function noise(duration, { volume = 0.08, delay = 0, lowpass = 1800 } = {}) {
    const a = audio();
    if (!a) return;
    const t0 = a.currentTime + delay;
    const buffer = a.createBuffer(1, Math.ceil(a.sampleRate * duration), a.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
    const src = a.createBufferSource();
    src.buffer = buffer;
    const filter = a.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = lowpass;
    const gain = a.createGain();
    gain.gain.setValueAtTime(volume, t0);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duration);
    src.connect(filter).connect(gain).connect(a.destination);
    src.start(t0);
}

export const sfx = {
    unlock: () => audio(),
    jump: () => tone(420, 0.1, { slideTo: 720, volume: 0.04 }),
    land: () => noise(0.05, { volume: 0.03, lowpass: 600 }),
    pickup: () => { tone(880, 0.07, { type: 'triangle' }); tone(1320, 0.1, { type: 'triangle', delay: 0.06 }); },
    checkpoint: () => [523, 659, 784].forEach((f, i) => tone(f, 0.14, { type: 'triangle', delay: i * 0.07 })),
    // Her happy shout: a bright rising chirp, then a little trill.
    dash: () => {
        tone(600, 0.18, { type: 'sawtooth', slideTo: 1200, volume: 0.05 });
        [1000, 1250, 1000, 1400].forEach((f, i) => tone(f, 0.08, { type: 'square', volume: 0.04, delay: 0.18 + i * 0.07 }));
    },
    dashEnd: () => tone(700, 0.15, { type: 'triangle', slideTo: 400, volume: 0.04 }),
    smash: () => noise(0.18, { volume: 0.09, lowpass: 2400 }),
    scare: () => { tone(900, 0.12, { type: 'square', slideTo: 1500, volume: 0.05 }); tone(1500, 0.1, { type: 'square', volume: 0.04, delay: 0.12 }); },
    whoosh: () => noise(0.35, { volume: 0.05, lowpass: 900 }),
    splash: () => { noise(0.4, { volume: 0.1, lowpass: 1400 }); tone(300, 0.2, { type: 'sine', slideTo: 120, volume: 0.05 }); },
    door: () => tone(330, 0.08, { type: 'triangle', volume: 0.05 }),
    // A short rising-then-falling "mrrp" as Bumbot slips away.
    mrrp: () => { tone(520, 0.09, { type: 'triangle', slideTo: 820, volume: 0.05 }); tone(820, 0.14, { type: 'triangle', slideTo: 560, volume: 0.04, delay: 0.09 }); },
};
