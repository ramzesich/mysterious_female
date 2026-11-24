// The game's two languages (the user, 2026-11-14): English, the default, and Ukrainian. Every text
// the game says to the player has both: the title, the win screen, a lock's popup, her own
// exclamations. `t(key, ...)` gives the text in the language chosen.
//
// What is not here, and stays as it is in both: the ship's own signs and plates (La Cucina, LINEN,
// DECK 5: they are part of the picture of an English-speaking ship), her «Кісюнічка!!!» (§3.2: the
// exact text), and everything said without words (the pictogram bubbles, ♥, ♪, !).
//
// The choice is kept in the browser (`bumbusik-lang`); `?lang=ua` or `?lang=en` sets it for one
// session without keeping it. Ukrainian is `ua` (the user, 2026-11-17: "uk is short for United
// Kingdom"); a choice kept as `uk` before is read as `ua`. The welcome screen's LANGUAGE button (src/intro.js) calls
// `nextLanguage()`.

const KEY = 'bumbusik-lang';

export const LANGUAGES = ['en', 'ua'];

const TEXTS = {
    en: {
        'language.name': 'English',
        // The welcome screen (docs/intro.md): the game's name and its two buttons. They are set in
        // capitals in the menu's own lettering, which has the letters these need and not every
        // other (tools/build_menu.py; the `lang` playtest says when one is missing).
        'title': 'Bumbusik',
        'menu.play': 'PLAY',
        'menu.language': 'LANGUAGE',
        // The two hints (the user asked for each): how to move and jump, over her once as the intro
        // hands her over (2026-11-20; with the controller in use, its own buttons); what E is for,
        // the first time she walks past her door (2026-11-14).
        'hint.move': '← and → to move, Space to jump',
        'hint.move.pad': 'Left stick to move, A to jump',
        'hint.interact': 'E to interact',
        'hint.dash': 'D to dash',
        'hint.dash.pad': 'B to dash',
        // (Crawling, as Bumbot is gone into the linen room's vent: near-catch 4, 2026-11-24.)
        'hint.crawl': '↓ to crawl',
        'hint.crawl.pad': 'Left stick down to crawl',
        // Choosing a book to read, in an armchair or on her bed (the first time the row shows).
        'hint.read': '← and → to choose, E to read, Esc to get up',
        'hint.read.pad': 'Left stick to choose, X to read, B to get up',
        // Giving books back at the Library's trolley with more than one on her (the first time the row shows there).
        'hint.return': '← and → to choose, E to give it back, Esc to keep the rest',
        'hint.return.pad': 'Left stick to choose, X to give it back, B to keep the rest',
        // Stamped beside a given-back book's title in the row (the menu's plate lettering: capitals).
        'book.returned': 'RETURNED',
        // The win screen (§6.4).
        'win.line': 'Bumbot is home.',
        'win.tally': (found, tangerines, books, photos, slots, shelf) =>
            `Tangerines ${found} of ${tangerines}      Books back on the shelf ${books} of ${shelf}      Pictures found ${photos} of ${slots}`,
        'win.go': 'Press E: the ship is still yours to wander',
        // A lock she has no card for (§6.1.5).
        'lock.card': name => `🔒 ${name} card`,
        'card.deck': 'Deck', 'card.ent': 'Entertainment', 'card.hk': 'Housekeeping', 'card.off': "Officer's",
        // Her frights, one for each hazard (§5.6).
        'fright.vacuum': 'Eeek!', 'fright.bumped': 'Oops!', 'fright.bonked': 'Ouch!', 'fright.slipped': 'Whoa!', 'fright.tripped': 'Whoops!',
        'fright.drenched': 'Brrr!', 'fright.buried': 'Mmmph!', 'fright.startled': 'Oh, sorry!', 'fright.splashed': 'Aaah!',
        'fright.swooped': 'Shoo!', 'fright.fogged': 'Pfff!', 'fright.singed': 'Hot!',
        'fright.ride': 'Weeeee!',      // carried off on the vacuum (docs/plan-three-uses.md §1.6, 5b)
        'fright.bumpy': 'Ow-ow-ow!',   // bumped down the funnel's stairway on her bottom (21)
        'fright.whoa': 'Whoa-whoa-whoa!',   // her parasol blown inside out, she drops (22)
        // What she and the others say in a word.
        'say.thanks': 'Thank you!', 'say.oops': 'Oops!', 'say.ohno': 'Oh no, no, no!', 'say.whoa': 'Whoa!', 'say.hey': 'Hey!', 'say.meow': 'Meow!',
        'say.knock': 'knock',
    },
    ua: {
        'language.name': 'Українська',
        'title': 'Бумбусік',
        'menu.play': 'ГРАТИ',
        'menu.language': 'МОВА',
        'hint.move': '← і → — рухатися, пробіл — стрибати',
        'hint.move.pad': 'Лівий стік — рухатися, A — стрибати',
        'hint.interact': 'E — взаємодіяти',
        'hint.dash': 'D — ривок',
        'hint.dash.pad': 'B — ривок',
        'hint.crawl': '↓ — повзти',
        'hint.crawl.pad': 'Лівий стік униз — повзти',
        'hint.read': '← і → — вибрати, E — читати, Esc — встати',
        'hint.read.pad': 'Лівий стік — вибрати, X — читати, B — встати',
        'hint.return': '← і → — вибрати, E — повернути, Esc — залишити решту',
        'hint.return.pad': 'Лівий стік — вибрати, X — повернути, B — залишити решту',
        'book.returned': 'ПОВЕРНЕНО',
        'win.line': 'Бумбот удома.',
        'win.tally': (found, tangerines, books, photos, slots, shelf) =>
            `Мандаринки: ${found} з ${tangerines}      Книжки на полиці: ${books} з ${shelf}      Знайдені світлини: ${photos} з ${slots}`,
        'win.go': 'Натисни E: корабель і далі твій, гуляй скільки хочеш',
        'lock.card': name => `🔒 ${name} картка`,
        'card.deck': 'Палубна', 'card.ent': 'Розважальна', 'card.hk': 'Господарська', 'card.off': 'Офіцерська',
        'fright.vacuum': 'Іііі!', 'fright.bumped': 'Ой!', 'fright.bonked': 'Ай!', 'fright.slipped': 'Ой-йой!', 'fright.tripped': 'Ой-ой!',
        'fright.drenched': 'Бррр!', 'fright.buried': 'Мммф!', 'fright.startled': 'Ой, вибачте!', 'fright.splashed': 'Ааа!',
        'fright.swooped': 'Киш!', 'fright.fogged': 'Пхх!', 'fright.singed': 'Гаряче!',
        'fright.ride': 'Уіііііііі!',
        'fright.bumpy': 'Ай-ай-ай!',
        'fright.whoa': 'Ой-ой-ой!',
        'say.thanks': 'Дякую!', 'say.oops': 'Ой!', 'say.ohno': 'Ой-ой-ой!', 'say.whoa': 'Ой-йой!', 'say.hey': 'Гей!', 'say.meow': 'Мяу!',
        'say.knock': 'тук',
    },
};

function chosen() {
    const asked = new URLSearchParams(location.search).get('lang');
    if (LANGUAGES.includes(asked)) return asked;
    try {
        const kept = localStorage.getItem(KEY)?.replace(/^uk$/, 'ua');
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
