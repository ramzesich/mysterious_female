"""The popups' art (the user, 2026-11-20: "we're refining the looks of every popup in the game ... a nice
framing, and differentiate between [speech] bubbles and thought clouds"): the frames, the icons and
the lettering, into the atlas `assets/sprites/popups.png` + `.json` (key `popups`) and the layout
`assets/sprites/popup-layout.json`, which `src/popup.js` reads.

- **The frames** are generated (`assets/source/popups/tries/`, its README has the jobs), the user's
  picks of 2026-11-20: a speech bubble (its own tail taken off: the game draws one toward the head
  of whoever speaks), a thought cloud (its two small circles kept apart, laid by the game toward
  the head), a shout (her cry, no tail), the hints' brass plate, a key cap. The game sizes each to
  its words by repeating a band of it whose two edges match, or taking it out once (`band`, chosen
  here; `sizeTo` in src/popup.js), so bumps and spikes stay whole.
- **The icons** are generated too (one sheet of 64, the picks in `ICONS`); a lock's card is cut from
  the card's own close-up (`assets/sprites/closeups.png`), shrunk by majority.
- **The lettering** is Galmuri9 (SIL OFL 1.1, `assets/source/popups/font/`, a subset of Latin,
  Cyrillic and arrows) set at its own pixel size, 10, every glyph a whole-pixel picture; a bold
  of it (each glyph widened a pixel, a pixel more apart) for the cry.

    python tools/build_popups.py
"""
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "popups"
TRIES = SRC / "tries"
OUT = ROOT / "assets" / "sprites"
FONT = SRC / "font" / "Galmuri9-subset.ttf"
SIZE = 10                          # Galmuri9's own pixel size
LIFT = 3

# The user's picks (2026-11-20), by candidate index in each sheet (the sheets number them from 1).
FRAMES = {"speech": 8, "thought": 9, "shout": 1, "plate": 0}
ICONS = {"padlock": 1, "ladder": 3, "hand": 7, "drop": 10, "snow": 13, "tray": 16, "pills": 19, "book": 22,
         "cart": 26, "softserve": 28, "camera": 31, "canister": 33, "door": 37, "cocktail": 40, "coffee": 43,
         "horn": 46, "cake": 50, "key": 52, "pad-a": 55, "pad-stick": 58}
CARDS = ["deck", "ent", "hk", "off"]
CARD_SIZE = (12, 18)

# Every letter a popup may need: Latin, Cyrillic, punctuation, arrows.
CHARS = ([chr(c) for c in range(0x20, 0x7F)] + [chr(c) for c in range(0x410, 0x450)]
         + list("ЄІЇҐєіїґЁё«»—–’‘“”…←→↑↓·"))


def crop(a):
    ys, xs = np.nonzero(a[:, :, 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def load(name, i):
    return crop(np.array(Image.open(TRIES / name / f"{i}.png").convert("RGBA")))


def speech():
    """The bubble without its tail: the rows under the body's bottom outline go, and the bottom
    rows where the tail joined are made again from a column of the plain bottom."""
    a = load("speech", FRAMES["speech"]).copy()
    w = (a[:, :, 3] > 0).sum(axis=1)
    bottom = max(r for r in range(len(w)) if w[r] > 0.6 * w.max())
    tail_cols = np.nonzero(a[bottom + 1:, :, 3].any(axis=0))[0]
    a = a[:bottom + 1].copy()
    clean = next(x for x in range(a.shape[1] // 2, a.shape[1]) if x not in tail_cols)
    for x in range(tail_cols.min() - 3, tail_cols.max() + 4):
        a[bottom - 2:bottom + 1, x] = a[bottom - 2:bottom + 1, clean]
    return a


def thought():
    """The cloud and its two small circles apart, biggest first."""
    a = load("thought", FRAMES["thought"])
    lab, k = ndimage.label(a[:, :, 3] > 0)
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, k + 1))
    parts = []
    for l in np.argsort(sizes)[::-1] + 1:
        p = a.copy()
        p[lab != l] = 0
        parts.append(crop(p))
    return parts[0], parts[1:3]


def card(name):
    """A lock's card: its close-up's card (under the clip, without the lanyard) shrunk by majority
    inside, its outline drawn round again a pixel wide (shrunk, the outline was lost)."""
    d = json.load(open(OUT / "closeups.json"))["frames"][f"card-{name}"]["frame"]
    im = np.array(Image.open(OUT / "closeups.png").convert("RGBA"))[d["y"]:d["y"] + d["h"], d["x"]:d["x"] + d["w"]]
    w = (im[:, :, 3] > 0).sum(axis=1)
    top = next(r for r in range(len(w)) if w[r] >= 0.9 * w.max())
    c = crop(im[top:].copy())
    ink = tuple(int(v) for v in c[c.shape[0] // 2, 0])
    W, H = CARD_SIZE
    out = np.zeros((H, W, 4), np.uint8)
    out[1:-1, 1:-1] = majority(c[2:-2, 2:-2], W - 2, H - 2)
    out[0, 1:-1] = out[-1, 1:-1] = out[1:-1, 0] = out[1:-1, -1] = ink
    return out


def majority(a, w, h):
    """Shrunk by the most common colour of each block (a small picture stays crisp)."""
    H, W = a.shape[:2]
    out = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        for x in range(w):
            b = a[y * H // h:max(y * H // h + 1, (y + 1) * H // h), x * W // w:max(x * W // w + 1, (x + 1) * W // w)].reshape(-1, 4)
            cols, counts = np.unique(b, axis=0, return_counts=True)
            out[y, x] = cols[counts.argmax()]
    return out


TIGHT = set("ШЩшщМмЖжЫы")


def glyphs(bold):
    f = ImageFont.truetype(str(FONT), SIZE)
    asc, desc = f.getmetrics()
    out = {}
    for ch in CHARS:
        adv = round(f.getlength(ch))
        # (3 px over the ascent: the breve of Й and the dots of Ї and Ё reach over it.)
        im = Image.new("L", (adv + 4, asc + desc + LIFT))
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        d.text((0, LIFT), ch, font=f, fill=255)
        a = np.array(im) > 127
        if bold:
            # (In the letters whose stems stand a px apart, never into that px: Щ, ш, м were filled solid in her
            # "Щоб вас дощ намочив!", 2026-11-28. The rest as they were, her cry's К and ю with them.)
            src = a.copy()
            gap = np.zeros_like(a)
            if ch in TIGHT:
                gap[:, 1:-1] = src[:, :-2] & ~src[:, 1:-1] & src[:, 2:]
            a[:, 1:] |= src[:, :-1] & ~gap[:, 1:]
            adv += 1 if ch != " " else 0
        cols = np.nonzero(a.any(axis=0))[0]
        wide = max(adv, cols.max() + 1 if len(cols) else 0)
        g = np.zeros((a.shape[0], wide, 4), np.uint8)
        g[a[:, :wide]] = (255, 255, 255, 255)
        out[ch] = (g, adv)
    return out, asc, desc


def ink_rows(gl, chars):
    rows = [np.nonzero(gl[c][0][:, :, 3].any(axis=1))[0] for c in chars if gl[c][0][:, :, 3].any()]
    return min(r.min() for r in rows), max(r.max() for r in rows)


def band(a, axis, pmin, pmax=24):
    """The band [c, c + p) a frame is sized by (src/popup.js repeats it, or takes it out once): in
    its middle, its two edge lines the most alike, the widest of the best; at least `pmin` (a cloud's
    or a burst's is a whole bump or spike)."""
    n = a.shape[axis]
    lo, hi = int(n * 0.3), int(n * 0.7) + 1
    line = (lambda i: a[:, i]) if axis == 1 else (lambda i: a[i])
    best = None
    for c in range(lo, hi):
        for p in range(pmin, pmax + 1):
            if c + p > hi:
                break
            d = int(np.abs(line(c).astype(int) - line(c + p).astype(int)).sum())
            if best is None or (d, -p) < best[0]:
                best = ((d, -p), c, p)
    return [best[1], best[2]]


def pack(pieces):
    """Rows of pieces, 1 px apart, into one sheet; returns it and each piece's place."""
    width, x, y, row, places = 512, 0, 0, 0, {}
    for name, a in pieces:
        h, w = a.shape[:2]
        if x + w > width:
            x, y, row = 0, y + row + 1, 0
        places[name] = (x, y, w, h)
        x += w + 1
        row = max(row, h)
    sheet = np.zeros((y + row, width, 4), np.uint8)
    for name, a in pieces:
        px, py, w, h = places[name]
        sheet[py:py + h, px:px + w] = a
    return sheet, places


def tangerine():
    """The game's own tangerine (`FRUIT` in src/textures.js, read from there): a wish's icon (the sushi
    chef's, 7) and the HUD's (tools/build_hud.py)."""
    js = (ROOT / "src" / "textures.js").read_text(encoding="utf-8")
    pal = dict(re.findall(r"^\s+(\w): '(#[0-9a-f]{6})'", js.split("const FRUIT_PALETTE")[1].split("};")[0], re.M))
    rows = re.findall(r"'([.\w]+)'", js.split("const FRUIT = {")[1].split("],")[0])
    a = np.zeros((len(rows), len(rows[0]), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c in pal:
                h = pal[c]
                a[y, x] = (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)
    return a


def main():
    pieces = [("speech", speech())]
    cloud, circles = thought()
    shout, plate = load("shout", FRAMES["shout"]), load("plate", FRAMES["plate"])
    # (A frame with straight sides repeats a line; a cloud a bump, a burst a spike.)
    # (Down a cloud's sides two rows are the same: one of them repeats without a seam.)
    bands = {name: {"x": band(a, 1, mx), "y": band(a, 0, my)}
             for name, a, mx, my in (("speech", pieces[0][1], 1, 1), ("thought", cloud, 5, 1), ("shout", shout, 5, 5), ("plate", plate, 1, 1))}
    pieces += [("thought", cloud)] + [(f"thought-dot{i}", c) for i, c in enumerate(circles)]
    pieces += [("shout", shout), ("plate", plate)]
    for name, i in ICONS.items():
        pieces.append((f"icon-{name}", crop(np.array(Image.open(TRIES / "icons" / f"{i}.png").convert("RGBA")))))
    for c in CARDS:
        pieces.append((f"icon-card-{c}", card(c)))
    # (Not generated: the game's own tangerine, a wish's icon, 2026-11-20.)
    pieces.append(("icon-tangerine", tangerine()))
    regular, asc, desc = glyphs(False)
    bold, _, _ = glyphs(True)
    for ch, (g, adv) in regular.items():
        pieces.append((f"g{ord(ch)}", g))
    for ch, (g, adv) in bold.items():
        pieces.append((f"b{ord(ch)}", g))
    sheet, places = pack(pieces)
    Image.fromarray(sheet).save(OUT / "popups.png")
    frames = {name: {"frame": {"x": x, "y": y, "w": w, "h": h}, "rotated": False, "trimmed": False,
                     "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h}, "sourceSize": {"w": w, "h": h}}
              for name, (x, y, w, h) in places.items()}
    json.dump({"frames": frames, "meta": {"image": "popups.png", "size": {"w": sheet.shape[1], "h": sheet.shape[0]}, "scale": "1"}},
              open(OUT / "popups.json", "w"), separators=(",", ":"))
    cap = ink_rows(regular, "ABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЬЮЯ")
    low = ink_rows(regular, "gjpqyруд")
    layout = {
        "font": {"height": asc + desc + LIFT, "top": int(cap[0]), "base": int(cap[1]), "low": int(low[1]),
                 "adv": {str(ord(c)): a for c, (g, a) in regular.items()},
                 "advBold": {str(ord(c)): a for c, (g, a) in bold.items()}},
        "bands": bands,
        "icons": sorted(list(ICONS) + [f"card-{c}" for c in CARDS] + ["tangerine"]),
        # The colours the game draws a speech tail in, the bubble's own.
        "tail": {"ink": "#2e222f", "fill": "#ffffff", "shade": "#9babb2"},
    }
    json.dump(layout, open(OUT / "popup-layout.json", "w"), indent=1)
    print(f"popups.png {sheet.shape[1]}x{sheet.shape[0]}, {len(pieces)} pieces")


if __name__ == "__main__":
    main()
