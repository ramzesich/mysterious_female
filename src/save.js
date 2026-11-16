import { SAVE_KEY, devFresh } from './config.js';

// Progress lives in the browser (localStorage) and is written at every checkpoint (§5.5).

function emptySave() {
    // `regions` she has opened (§6.1.3), her `cards`, the `flags` of what has happened (Bumbot's
    // beats, the horn, the wedding...), the one-way doors and trunks `opened` both ways.
    // Her `verbs` (the dash, crawling, the grip socks, the parasol: §6.1.2), the library's `books`
    // (number -> "held", "returned"; `read` the ones she has read), her pocket `items`, the quirks
    // and secrets she has `seen`; the tangerines lying `loose` where they stopped (src/world/tangerine.js);
    // the things she has found (`keeps`, "keep:<whose>:<name>", docs/plan-three-uses.md §4.1).
    return { activated: [], collected: [], broken: [], opened: [], cards: [], regions: [], flags: [], verbs: [], books: {}, read: [],
             items: [], seen: [], tangerines: 0, loose: [], keeps: [], lastCheckpoint: null };
}

export function loadSave() {
    // (While the game is made, every load is a new game: `DEV_FRESH` in src/config.js.)
    if (devFresh()) return emptySave();
    if (new URLSearchParams(location.search).has('reset')) {
        localStorage.removeItem(SAVE_KEY);
    }
    try {
        const data = JSON.parse(localStorage.getItem(SAVE_KEY));
        return data ? { ...emptySave(), ...data } : emptySave();
    } catch {
        return emptySave();
    }
}

export function writeSave(save) {
    if (devFresh()) return;
    localStorage.setItem(SAVE_KEY, JSON.stringify(save));
}
