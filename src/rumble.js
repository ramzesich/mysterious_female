// The Xbox controller's rumble (GAME_DESIGN.md §3.1; the user's ten moments, 2026-11-15): a few
// moments only, so that a rumble always means something. Each is a list of pulses, [start ms,
// length ms, the strong (low) motor, the weak (high) motor], played on the controller she plays
// with; nothing when she plays on the keyboard, or the browser can't (`vibrationActuator`).

const EFFECTS = {
    bump: [[0, 150, 0.6, 0.8]],                                   // a scare: a bump, a bonk, a splash
    fall: [[0, 260, 1, 0.5]],                                     // a scare: a long fall, the heavy thud
    overboard: [[0, 220, 1, 0.7], [220, 200, 0.45, 0.25]],         // a scare: the big splash, fading
    land: [[0, 80, 0.4, 0.1]],                                    // down a deck on her feet
    lunge: [[0, 120, 0.3, 0.7]],                                  // the lunge starting
    spill: [[0, 100, 0, 0.45]],                                   // a tray spilled: a light tick
    bolt: [[0, 80, 0.2, 0.45], [160, 80, 0.2, 0.45]],              // Bumbot bolting at a near-catch
    alarm: [0, 500, 1000, 1500].map(t => [t, 250, 0.5, 0.6]),     // the bridge's alarm, with its lights
    drain: [[0, 5000, 0.22, 0.04]],                               // the pool draining
    gust: [[0, 450, 0.08, 0.22]],                                 // a gust pushing her
    catch: [[0, 120, 0.35, 0.15], [280, 170, 0.5, 0.2]],           // the catch: a heartbeat
};

let controls = null;
const timers = [];
// Every effect played, for the playtests (a fake controller has no motors).
export const rumbleLog = [];

export function rumbleWith(c) {
    controls = c;
}

// (From the browser's current reading of the controller: Chrome hands out a fresh snapshot each time.)
function motors() {
    const pad = controls?.padInUse();
    if (!pad) return null;
    return navigator.getGamepads?.()[pad.index]?.vibrationActuator ?? pad.pad?.vibrationActuator ?? null;
}

function pulse(ms, strong, weak) {
    const a = motors();
    a?.playEffect?.('dual-rumble', { startDelay: 0, duration: ms, strongMagnitude: strong, weakMagnitude: weak })
        ?.catch?.(() => {});
}

// A moment's rumble; `ms` stretches a one-pulse effect to the moment's length (the horn's blast).
export function rumble(name, ms = null) {
    const list = name === 'horn' ? [[0, ms ?? 1500, 1, 0.2]] : EFFECTS[name];
    if (!list || !controls?.padInUse()) return;
    rumbleLog.push(name);
    if (rumbleLog.length > 100) rumbleLog.shift();
    timers.splice(0).forEach(clearTimeout);
    for (const [at, len, strong, weak] of list) {
        if (at === 0) pulse(len, strong, weak);
        else timers.push(setTimeout(() => pulse(len, strong, weak), at));
    }
}

// A rumble for something that lasts (a gust pushing her): at most once in `every` ms.
let lastAt = {};
export function rumbleNow(name, every) {
    const now = performance.now();
    if (now - (lastAt[name] ?? -Infinity) < every) return;
    lastAt[name] = now;
    rumble(name);
}
