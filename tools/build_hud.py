"""The HUD's art (the user, 2026-11-20; docs/progress-decisions.md, "The HUD"): one atlas,
`assets/sprites/hud.png` + `.json`, every picture on it from its approved source, nothing redrawn.

- `tangerine`: the game's own tangerine (`FRUIT` in src/textures.js, read from there);
- `cat`: Bumbot's face, the generated try the user chose (#3 of `assets/source/hud/tries/bumbot/`,
  kept as `assets/source/hud/face-bumbot.png`), cut to his outline, the two pixels under his left
  cheek cleared (the user);
- `her`: her face and shoulders from her front view (`assets/source/her/rotations/south.png`);
- `him`: her husband's, from his approved front view with the bear (`assets/source/hud/husband/
  south-bear.png`), one row of his forehead taken out (the user: "making my icon shorter");
- `book`: the popups' book icon (the same generated try);
- `card-<card>`: the popups' key card (cut from its close-up), the slot at its top filled white
  (the user: "fix the triangular cuts"); `card-<card>-ghost`: its outline, faint, for a card not held.

- `socks`, `parasol`: her two utilities, shown at the top right once hers (the user, 2026-11-26): **the user's own
  Paint files, `assets/source/hud/socks-by-hand.png` and `parasol-by-hand.png`, never written by a tool**, magenta
  (#FF00FF) empty (white is the socks' grip dots and the parasol's stripes). The socks began as generated try 7
  (`assets/source/hud/tries/socks/`, its README), mirrored, a copy behind it 4 px left and 3 px up; the parasol as the
  game's open parasol shrunk by majority (`tools/build_things.py`), outlined.
- `g8734`: an ∞ for `?tangerines=infinite` (the lettering has none): two of the font's loops crossing
  in the middle, as tall as the x and on its rows, in a glyph's frame (white; `src/hud.js` outlines it).

Every picture but the cards gets a light rim a pixel wide (the user: it holds them on any
background). The game draws them at 2 screen px a pixel (`src/hud.js`).

    python tools/build_hud.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

from build_popups import card, crop, TRIES, pack, tangerine

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source"
OUT = ROOT / "assets" / "sprites"
CARDS = ["deck", "ent", "hk", "off"]
RIM = (255, 255, 255, 110)
SLOT = [(5, 1), (6, 1), (7, 1), (5, 2), (6, 2)]      # the card's slot, x, y
GHOST_EDGE, GHOST_FILL = 150, 40


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def rim(a):
    """A light ring a pixel wide round the picture (4-neighbours), the picture a pixel in."""
    h, w = a.shape[:2]
    out = np.zeros((h + 2, w + 2, 4), np.uint8)
    m = np.zeros((h + 2, w + 2), bool)
    m[1:-1, 1:-1] = a[:, :, 3] > 0
    ring = np.zeros_like(m)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        ring |= np.roll(np.roll(m, dy, 0), dx, 1)
    out[ring & ~m] = RIM
    out[1:-1, 1:-1][a[:, :, 3] > 0] = a[a[:, :, 3] > 0]
    return out


def ghost(a):
    m = a[:, :, 3] > 0
    inner = np.ones_like(m)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        inner &= np.roll(np.roll(m, dy, 0), dx, 1)
    edge = m & ~inner
    out = np.zeros_like(a)
    out[edge] = (255, 255, 255, GHOST_EDGE)
    out[m & ~edge] = (255, 255, 255, GHOST_FILL)
    return out


INFINITY = [".###...###.",
            "#...#.#...#",
            "#....#....#",
            "#....#....#",
            "#...#.#...#",
            ".###...###."]
INFINITY_TOP = 7            # its top row in a glyph's frame: the x's rows, 7 to 12 (the user: "center it against the X")


def by_hand(name):
    """A picture the user edits in Paint: magenta is empty, cut to what is drawn."""
    a = rgba(SRC / "hud" / f"{name}-by-hand.png")
    a[(a[:, :, 0] == 255) & (a[:, :, 1] == 0) & (a[:, :, 2] == 255)] = 0
    return crop(a)


def infinity():
    a = np.zeros((14, len(INFINITY[0]) + 1, 4), np.uint8)
    for y, row in enumerate(INFINITY):
        for x, c in enumerate(row):
            if c == "#":
                a[INFINITY_TOP + y, x] = (255, 255, 255, 255)
    return a


def main():
    cat = crop(rgba(SRC / "hud" / "face-bumbot.png"))
    cat[19, 1, 3] = cat[19, 2, 3] = 0
    cat[19, 1] = cat[19, 2] = 0
    her = rgba(SRC / "her" / "rotations" / "south.png")[2:26, 20:42]
    him = np.delete(rgba(SRC / "hud" / "husband" / "south-bear.png")[1:28, 19:44], 5, axis=0)
    book = crop(np.array(Image.open(TRIES / "icons" / "22.png").convert("RGBA")))
    pieces = [("tangerine", rim(tangerine())), ("cat", rim(cat)), ("her", rim(her)), ("him", rim(him)), ("book", rim(book))]
    for c in CARDS:
        a = card(c)
        for x, y in SLOT:
            a[y, x] = (255, 255, 255, 255)
        pieces += [(f"card-{c}", a), (f"card-{c}-ghost", ghost(a))]
    pieces += [(n, rim(by_hand(n))) for n in ("socks", "parasol")]
    pieces.append(("g8734", infinity()))
    sheet, places = pack(pieces)
    Image.fromarray(sheet).save(OUT / "hud.png")
    frames = {n: {"frame": {"x": x, "y": y, "w": w, "h": h}, "rotated": False, "trimmed": False,
                  "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h}, "sourceSize": {"w": w, "h": h}}
              for n, (x, y, w, h) in places.items()}
    json.dump({"frames": frames, "meta": {"image": "hud.png", "size": {"w": sheet.shape[1], "h": sheet.shape[0]}, "scale": "1"}},
              open(OUT / "hud.json", "w"))
    for n, (x, y, w, h) in places.items():
        print(f"{n:16} {w} x {h}")


if __name__ == "__main__":
    main()
