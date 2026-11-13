import { SAVE_KEY } from './config.js';

// Progress lives in the browser (localStorage) and is written at every checkpoint (§5.5).

function emptySave() {
    // `regions` she has opened (§6.1.3), her `cards`, the `flags` of what has happened (Bumbot's
    // beats, the horn, the wedding...), the one-way doors and trunks `opened` both ways.
    // Her `verbs` (the dash, crawling, the grip socks, the parasol: §6.1.2), the library's `books`
    // (number -> "held", "returned"; `read` the ones she has read), her pocket `items`, the quirks
    // and secrets she has `seen`.
    return { activated: [], collected: [], broken: [], opened: [], cards: [], regions: [], flags: [], verbs: [], books: {}, read: [],
             items: [], seen: [], tangerines: 0, lastCheckpoint: null };
}

export function loadSave() {
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
    localStorage.setItem(SAVE_KEY, JSON.stringify(save));
}
