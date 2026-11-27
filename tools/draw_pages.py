"""Sets the fourteen books' pages (GAME_DESIGN.md §6.1.2): read in the Library's red chair (book 5 on her bed
in cabin 8206), each book shows its own first page: the opening of the real book, in its own language and
script, readable (the user, 2026-11-21: "Text only for all the books"; the drawn hint pages are gone).

A page is cream paper, its title small at the top over a rule (a running head), then the book's text from its
very start, justified, a line of its own for each paragraph (each line of dialogue), whole sentences only, as
many as fit; the lines left over at the foot are spread between the lines so that the text covers the page
(the user: "cover the entire page. Don't break sentences"). Hebrew is set right to left, right-aligned.

The lettering is Pixelzone (GGBotNet, CC0: `assets/source/pages/Pixelzone.ttf`), at its own pixel size (a
16 px em, a 9 px capital): it has Latin with the Polish letters, Ukrainian and Russian Cyrillic, and Hebrew.
The texts are `assets/source/pages/<nn>.txt`, one paragraph a line; where each came from is in that folder's
README. A book with no text yet has a title page (its title and author) instead.

    python tools/draw_pages.py [--preview out.png]

Writes assets/ship/pages/page-<n>.png (260 x 146; the game shows them at 3x: `Library.panel()`) and title-<n>.png
(the title alone, for the row of books she chooses from: `Library.choose()`).
"""

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import pixelzone

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "pages"
OUT = ROOT / "assets" / "ship" / "pages"
W, H = 260, 146
PAPER, EDGE, INK, SOFT = "#f3ecdd", "#d8cdb8", "#3e3546", "#9babb2"
FONT, SIZE, LEADING = SRC / "Pixelzone.ttf", 16, 12
MARGIN = 14                     # the text's left and right margins
SPREAD_MAX = 2                  # lines left over that are spread over the page; more and the text stays at the top

# Each book's running head and author (GAME_DESIGN.md §6.1.2's table), as printed on her copy.
BOOKS = {
    1: ("Atomic Habits", "James Clear"),
    2: ("Harry Potter and the Chamber of Secrets", "J.K. Rowling"),
    3: ("Танґо смерті", "Юрій Винничук"),
    4: ("Unexpected Lessons in Love", "Lucy Dillon"),
    5: ("Її війна", "Євгенія Подобна"),
    6: ("Harry Potter and the Philosopher's Stone", "J.K. Rowling"),
    7: ("Понаїхали", "Артем Чапай"),
    8: ("Niebieskie nitki", "Małgorzata Gutowska-Adamczyk"),
    9: ("Двор", "Аркадий Львов"),
    10: ("Боря, выйди с моря", "Рафаил Гругман"),
    11: ("נערה במעיל כחול", "מוניקה הסה"),
    12: ("Poczwarka", "Dorota Terakowska"),
    13: ("Daughters of Warsaw", "Maria Frances"),
    14: ("Pachinko", "Min Jin Lee"),
    # (On Splash Academy's bookshelf, 2026-11-27: its title, author, text and cover are the user's, to come.)
    15: ("Book fifteen", "(to come)"),
}
HEBREW = re.compile(r"[֐-׿]")
DASH_ON = re.compile(r"[—–-]\s*[^\sA-ZА-ЯЁҐЄІЇ]")    # "— принимая находку": the sentence goes on


# Books whose page may end a sentence at a colon too (the user, 2026-11-22: book 4's second paragraph has a sentence
# one line longer than the page has left; "Long sentence, broken at the colon").
COLON = {4}


def sentences(par, colon=False):
    """A paragraph's whole sentences: each ends at . ? ! or … before a space, unless what follows goes on with a
    dash and a small letter ("— Это мне? — принимая находку, …" is one sentence). With `colon`, at a colon too."""
    out = []
    for piece in [x for x in re.split(r"(?<=[.?!…:])\s+" if colon else r"(?<=[.?!…])\s+", par) if x]:
        if out and DASH_ON.match(piece):
            out[-1] += " " + piece
        else:
            out.append(piece)
    return out


def wrap(words, font, width):
    lines, cur = [], []
    for w in words:
        if cur and font.getlength(" ".join(cur + [w])) > width:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def layout(pars, font, width, rows, colon=False):
    """Whole sentences from the start, as many as fit in `rows` lines: [(words, last line of its paragraph)]."""
    best, taken = [], {}
    for pi, par in enumerate(pars):
        ss = sentences(par, colon)
        for si in range(len(ss)):
            taken[pi] = " ".join(ss[: si + 1])
            out = []
            for p in sorted(taken):
                ls = wrap(taken[p].split(), font, width)
                out += [(l, k == len(ls) - 1) for k, l in enumerate(ls)]
            if len(out) > rows:
                return best
            best = out
    return best


def visual(words, rtl):
    """Words in the order they are drawn from left to right (Hebrew: each word's letters and the line reversed)."""
    return [w[::-1] for w in words][::-1] if rtl else words


def page(n):
    title, author = BOOKS[n]
    font = ImageFont.truetype(str(FONT), SIZE)
    im = Image.new("RGBA", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle([0, 0, W - 1, H - 1], outline=INK)
    d.rectangle([3, 3, W - 4, H - 4], outline=EDGE)
    x0, x1 = MARGIN, W - MARGIN
    src = SRC / f"{n:02d}.txt"
    if not src.exists():
        # No text yet: a title page, its title and author in the middle.
        for k, (t, c) in enumerate(((title, INK), (author, SOFT))):
            t = " ".join(visual(t.split(), bool(HEBREW.search(t))))
            pixelzone.text(im, ((W - font.getlength(t)) // 2, H // 2 - LEADING + k * (LEADING + 4)), t, c)
        return im
    pars = [l.strip() for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    rtl = bool(HEBREW.search(pars[0]))
    head = " ".join(visual(title.split(), rtl))
    pixelzone.text(im, ((W - font.getlength(head)) // 2, 6), head, SOFT)
    d.line([(x0, 6 + LEADING + 1), (x1, 6 + LEADING + 1)], fill=EDGE)
    top = 6 + LEADING + 5
    rows = (H - 8 - top) // LEADING
    lines = layout(pars, font, x1 - x0, rows, n in COLON)
    spare = (rows - len(lines)) * LEADING if rows - len(lines) <= SPREAD_MAX else 0
    for i, (words, last) in enumerate(lines):
        y = top + i * LEADING + (round(spare * i / (len(lines) - 1)) if len(lines) > 1 else 0)
        words = visual(words, rtl)
        if last or len(words) == 1:
            t = " ".join(words)
            pixelzone.text(im, (x1 - font.getlength(t) if rtl else x0, y), t, INK)
            continue
        gap = (x1 - x0 - sum(font.getlength(w) for w in words)) / (len(words) - 1)
        x = x0
        for w in words:
            pixelzone.text(im, (round(x), y), w, INK)
            x += font.getlength(w) + gap
    return im


def title(n):
    """The book's title alone, in the pages' lettering, cream, on nothing: under the row she chooses from (the game
    shows it at 3x). Every row a letter reaches (from the top of a Hebrew lamed or the dots of a Ukrainian yi to the
    tail of a Polish ogonek) is kept."""
    font = ImageFont.truetype(str(FONT), SIZE)
    t = BOOKS[n][0]
    t = " ".join(visual(t.split(), bool(HEBREW.search(t))))
    # (Every title the same height on the same line, its letters' rows 1 to 14, so none moves as the choice does.)
    im = Image.new("RGBA", (int(font.getlength(t)) + 2, 16), (0, 0, 0, 0))
    pixelzone.text(im, (1, 0), t, PAPER)
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    done = [page(n) for n in BOOKS]
    for n, im in zip(BOOKS, done):
        im.save(OUT / f"page-{n}.png")
        title(n).save(OUT / f"title-{n}.png")
    print("wrote", len(done), "pages in", OUT.relative_to(ROOT))
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        sheet = Image.new("RGBA", (W * 2 + 12, (H + 4) * 7 + 4), "#1a141c")
        for i, im in enumerate(done):
            sheet.alpha_composite(im, (4 + (i % 2) * (W + 4), 4 + (i // 2) * (H + 4)))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(out)


if __name__ == "__main__":
    main()
