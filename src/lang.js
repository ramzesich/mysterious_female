// The game's two languages (the user, 2026-11-14): English, the default, and Ukrainian. Every text
// the game says to the player has both: the title, the win screen, a lock's popup, her own
// exclamations. `t(key, ...)` gives the text in the language chosen.
//
// What is not here, and stays as it is in both: the ship's own signs and plates (La Cucina, LINEN,
// DECK 5: they are part of the picture of an English-speaking ship), her «Кісюнічка!!!» (§3.2: the
// exact text), and everything said without words (the pictogram bubbles, ♥, ♪, !).
//
// The choice is kept in the browser (`bumbusik-lang`); `?lang=uk` or `?lang=en` sets it for one
// session without keeping it. The welcome screen's LANGUAGE button (src/intro.js) calls
// `nextLanguage()`.

const KEY = 'bumbusik-lang';

export const LANGUAGES = ['en', 'uk'];

const TEXTS = {
    en: {
        'language.name': 'English',
        // The welcome screen (docs/intro.md): the game's name and its two buttons. They are set in
        // capitals in the menu's own lettering, which has the letters these need and not every
        // other (tools/build_menu.py; the `lang` playtest says when one is missing).
        'title': 'Bumbusik',
        'menu.play': 'PLAY',
        'menu.language': 'LANGUAGE',
        // The one hint (the user asked for it, 2026-11-14): over her as the intro hands her over.
        'hint.interact': 'E to interact',
        // The win screen (§6.4).
        'win.line': 'Bumbot is home.',
        'win.tally': (found, tangerines, books, photos, slots) =>
            `Tangerines ${found} of ${tangerines}      Books back on the shelf ${books} of 10      Pictures found ${photos} of ${slots}`,
        'win.go': 'Press E: the ship is still yours to wander',
        // A lock she has no card for (§6.1.5).
        'lock.card': name => `🔒 ${name} card`,
        'card.deck': 'Deck', 'card.ent': 'Entertainment', 'card.hk': 'Housekeeping', 'card.off': "Officer's",
        // Her frights, one for each hazard (§5.6).
        'fright.vacuum': 'Eeek!', 'fright.bumped': 'Oops!', 'fright.bonked': 'Ouch!', 'fright.slipped': 'Whoa!', 'fright.tripped': 'Whoops!',
        'fright.drenched': 'Brrr!', 'fright.buried': 'Mmmph!', 'fright.startled': 'Oh, sorry!', 'fright.splashed': 'Aaah!',
        'fright.swooped': 'Shoo!', 'fright.fogged': 'Pfff!', 'fright.singed': 'Hot!',
        'fright.ride': 'Weeeee!',      // carried off on the vacuum (docs/plan-three-uses.md §1.6, 5b)
        // What she and the others say in a word.
        'say.oops': 'Oops!', 'say.ohno': 'Oh no, no, no!', 'say.whoa': 'Whoa!', 'say.hey': 'Hey!', 'say.meow': 'Meow!',
        'say.knock': 'knock',
    },
    uk: {
        'language.name': 'Українська',
        'title': 'Бумбусік',
        'menu.play': 'ГРАТИ',
        'menu.language': 'МОВА',
        'hint.interact': 'E — взаємодіяти',
        'win.line': 'Бумбот удома.',
        'win.tally': (found, tangerines, books, photos, slots) =>
            `Мандаринки: ${found} з ${tangerines}      Книжки на полиці: ${books} з 10      Знайдені світлини: ${photos} з ${slots}`,
        'win.go': 'Натисни E: корабель і далі твій, гуляй скільки хочеш',
        'lock.card': name => `🔒 ${name} картка`,
        'card.deck': 'Палубна', 'card.ent': 'Розважальна', 'card.hk': 'Господарська', 'card.off': 'Офіцерська',
        'fright.vacuum': 'Іііі!', 'fright.bumped': 'Ой!', 'fright.bonked': 'Ай!', 'fright.slipped': 'Ой-йой!', 'fright.tripped': 'Ой-ой!',
        'fright.drenched': 'Бррр!', 'fright.buried': 'Мммф!', 'fright.startled': 'Ой, вибачте!', 'fright.splashed': 'Ааа!',
        'fright.swooped': 'Киш!', 'fright.fogged': 'Пхх!', 'fright.singed': 'Гаряче!',
        'fright.ride': 'Віііі!',
        'say.oops': 'Ой!', 'say.ohno': 'Ой-ой-ой!', 'say.whoa': 'Ой-йой!', 'say.hey': 'Гей!', 'say.meow': 'Мяу!',
        'say.knock': 'тук',
    },
};

function chosen() {
    const asked = new URLSearchParams(location.search).get('lang');
    if (LANGUAGES.includes(asked)) return asked;
    try {
        const kept = localStorage.getItem(KEY);
        if (LANGUAGES.includes(kept)) return kept;
    } catch { /* no storage: the default */ }
    return LANGUAGES[0];
}

let lang = chosen();

export function language() {
    return lang;
}

// Chosen by the player: kept for the next time.
export function setLanguage(to) {
    if (!LANGUAGES.includes(to)) return lang;
    lang = to;
    try { localStorage.setItem(KEY, to); } catch { /* not kept, then */ }
    return lang;
}

export function nextLanguage() {
    return setLanguage(LANGUAGES[(LANGUAGES.indexOf(lang) + 1) % LANGUAGES.length]);
}

// The text for `key` in the language chosen (English where the other has none, the key itself
// where neither has). A text that takes numbers or names is a function of them.
export function t(key, ...args) {
    const text = TEXTS[lang][key] ?? TEXTS.en[key];
    if (text === undefined) return key;
    return typeof text === 'function' ? text(...args) : text;
}

// Does `key` have a text? (A fright with none shows "!".)
export function has(key) {
    return key in TEXTS.en;
}

// One text given in both languages where it is written (`WIN_MESSAGE` in src/config.js).
export function pick(both) {
    return typeof both === 'string' ? both : both?.[lang] ?? both?.en ?? '';
}

// Every key, for the playtest: both languages must have the same.
export const KEYS = Object.fromEntries(LANGUAGES.map(l => [l, Object.keys(TEXTS[l])]));
