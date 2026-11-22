"""Cabin 8206's desk seen close (docs/plan-the-rest.md §4 2.4, the user's, 2026-11-22): E at the desk shows it over
the whole screen, her four things and his four on it, each from its find; a thing not found yet leaves bare desk.

From PixelLab's redraw of a rough made of the close-ups (`assets/source/closeups/desk/`, its README has the ids):
    tries/try1.png  the chosen redraw (the user's choice of three)
    full.png        it mended (`mend()`): written here
    bare.png        the desk with nothing on it: every thing's box filled along its row from the left of the box, the
                    wall, the desk's back edge, its top, edge and front being flat colours (free and exact, no inpaint)
    <keep>.png      each thing alone, at its place on the whole canvas: what differs from the bare desk in its box
    layout.json     each piece's box
and the game's copies in `assets/ship/desk/` (each piece cut to its box).

    python tools/build_desk.py
"""
import json
from pathlib import Path

import cv2
import numpy as np

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "closeups" / "desk"
OUT = ROOT / "assets" / "ship" / "desk"

PINK = (0xfc, 0xd3, 0xcb)


def mend(im):
    px = im.load()
    # The sleep mask: two stray light marks on its left (they read as "67"): its own pink.
    for y in range(122, 134):
        for x in range(151, 168):
            if px[x, y][:3] in ((0xfa, 0xf9, 0xe9), (0xec, 0xe3, 0xcb)):
                px[x, y] = PINK + (255,)
    # (His t-shirt's logo is the redraw's own: at this size its two words are a light smudge under the badge, as small
    # print is seen from afar; drawn as strokes, they read as a barcode.)
    return im


# The desk's flat colours: the wall, its back edge, its top, its edge and its front.
SURFACE = [(0xec, 0xe3, 0xcb), (0x79, 0x42, 0x27), (0xcd, 0x85, 0x54), (0x9c, 0x5a, 0x35), (0xb8, 0x71, 0x43)]
# Each thing's box on the canvas (x0, y0, x1, y1, inclusive), measured on full.png by its pixels that are none of
# the surface's; where two touch, the line between them (the plant's pot and the t-shirt's collar: row 128/129; the
# book and the diary: column 324/325; the mask and the handheld: by colour, below).
BOXES = {
    "flag": (35, 64, 82, 132),
    "plant": (84, 63, 120, 128),
    "tshirt": (45, 129, 146, 173),
    "sleepmask": (145, 120, 205, 152),
    "handheld": (196, 128, 275, 171),
    "pick": (287, 144, 312, 171),
    "bookmark": (266, 69, 324, 135),
    "diary": (325, 69, 365, 135),
}


def bare_desk(full):
    a = np.array(full)
    out = a.copy()
    # (Every box together: a row is filled from the nearest pixel left of them all.)
    cover = np.zeros(a.shape[:2], bool)
    for x0, y0, x1, y1 in BOXES.values():
        cover[y0 - 1:y1 + 2, x0 - 1:x1 + 2] = True
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if cover[y, x]:
                out[y, x] = out[y, x - 1]
    return out


def pieces(full, bare):
    a = np.array(full)
    diff = np.any(a != bare, axis=2)
    got = {}
    for name, (x0, y0, x1, y1) in BOXES.items():
        own = np.zeros(diff.shape, bool)
        own[y0:y1 + 1, x0:x1 + 1] = diff[y0:y1 + 1, x0:x1 + 1]
        got[name] = own
    # The mask's tip and the handheld's grip share columns 196 to 205: the mask's pixels are its pinks (red over
    # 0xd0), the handheld's its darks; a dark px with pink on three sides is the mask's.
    both = got["sleepmask"] & got["handheld"]
    pink = a[..., 0] > 0xd0
    for y, x in zip(*np.where(both)):
        near = sum(pink[y + dy, x + dx] for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)))
        mine = pink[y, x] or near >= 3
        got["sleepmask"][y, x] = mine
        got["handheld"][y, x] = not mine
    # Elsewhere a px in two boxes is the one whose box's middle is nearer (the flag's stand and the t-shirt's sleeve).
    names = list(got)
    for i, n1 in enumerate(names):
        for n2 in names[i + 1:]:
            for y, x in zip(*np.where(got[n1] & got[n2])):
                d = [((x - (b[0] + b[2]) / 2) ** 2 + (y - (b[1] + b[3]) / 2) ** 2) for b in (BOXES[n1], BOXES[n2])]
                got[n2 if d[0] < d[1] else n1][y, x] = False
    # A bit apart from a thing's body is the desk's (a few px of its back edge by the flag): it goes back to the bare
    # desk, the thing keeps its largest piece.
    loose = np.zeros(diff.shape, bool)
    for name, own in got.items():
        n, lab, st, _ = cv2.connectedComponentsWithStats(own.astype(np.uint8), connectivity=8)
        if n > 2:
            keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            for i in range(1, n):
                if i != keep:
                    print(f"  {name}: {st[i, cv2.CC_STAT_AREA]} px at {st[i, 0]},{st[i, 1]} back to the desk")
                    loose |= lab == i
            own &= lab == keep
    bare[loose] = a[loose]
    diff &= ~loose
    taken = np.zeros(diff.shape, bool)
    for name, own in got.items():
        assert not (taken & own).any(), name
        taken |= own
    assert not (diff & ~taken).any(), "a changed px in no box"
    return got


def main():
    full = mend(Image.open(SRC / "tries" / "try1.png").convert("RGBA"))
    full.save(SRC / "full.png")
    bare = bare_desk(full)
    got = pieces(full, bare)                # (puts a thing's loose bits back into `bare`)
    Image.fromarray(bare).save(SRC / "bare.png")
    layout = {}
    for name, own in got.items():
        a = np.array(full).copy()
        a[~own] = 0
        Image.fromarray(a).save(SRC / f"{name}.png")
        ys, xs = np.where(own)
        layout[name] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1 - int(xs.min()), int(ys.max()) + 1 - int(ys.min())]
    (SRC / "layout.json").write_text(json.dumps(layout, indent=1))
    # The game's: the bare desk, each thing cut to its box, and where each box is (`assets/ship/desk/`).
    OUT.mkdir(parents=True, exist_ok=True)
    Image.fromarray(bare).save(OUT / "bare.png")
    for name, (x, y, w, h) in layout.items():
        Image.open(SRC / f"{name}.png").crop((x, y, x + w, y + h)).save(OUT / f"{name}.png")
    (OUT / "layout.json").write_text(json.dumps(layout))
    print("wrote full.png, bare.png, the eight pieces and layout.json in", SRC.relative_to(ROOT))


if __name__ == "__main__":
    main()
