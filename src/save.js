import { SAVE_KEY } from './config.js';

// Progress lives in the browser (localStorage) and is written at every checkpoint (§5.5).

function emptySave() {
    return { activated: [], collected: [], broken: [], cards: ['crew'], tangerines: 0, lastCheckpoint: null };
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
