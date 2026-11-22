"""Cabin 8206 seen close (docs/plan-the-rest.md §4 2.4, the user's, 2026-11-22): two generated pictures shown over the
whole screen, each with its things on it from their finds, bare where one is not found yet.

- **The desk** (E at the desk, any time): her four things and his four (`assets/source/closeups/desk/`).
- **The bed** (E at Bumbot asleep on it, the day after): him and his eight (`assets/source/closeups/bed/`).

Each from PixelLab's redraw of a rough made of the close-ups (each folder's README has the ids):
    tries/tryN.png  the chosen redraw (the user's choice of three)
    full.png        it mended (`mend`): written here
    bare.png        the picture with none of the things: every thing's box filled along its row from the left of the
                    box, its surfaces being flat colours (free and exact, no inpaint); Bumbot stays on the bed
    <keep>.png      each thing alone, at its place on the whole canvas: what differs from the bare picture in its box
    layout.json     each piece's box
and the game's copies in `assets/ship/<scene>/` (each piece cut to its box).

    python tools/build_desk.py
"""
import json
from pathlib import Path

import cv2
import numpy as np

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

PINK = (0xfc, 0xd3, 0xcb)


def mend_desk(im):
    px = im.load()
    # The sleep mask: two stray light marks on its left (they read as "67"): its own pink.
    for y in range(122, 134):
        for x in range(151, 168):
            if px[x, y][:3] in ((0xfa, 0xf9, 0xe9), (0xec, 0xe3, 0xcb)):
                px[x, y] = PINK + (255,)
    # (His t-shirt's logo is the redraw's own: at this size its two words are a light smudge under the badge, as small
    # print is seen from afar; drawn as strokes, they read as a barcode.)
    return im


def bare_bed(full, boxes):
    """The bed with none of his things: along the row as the desk's, but where that crosses an edge that runs down
    (the user's massage gun stands across the runner's edge and the cushions' seam; the ball and the wool reach up into
    the cushion and the pillow): over the bed's top (above row 111) the row just over the box, the cushions and the
    pillow running straight down to it; in the runner (columns 59 to 119, its rims too, from row 111) the same column 48
    rows lower (its chevrons repeat every 16 rows from row 122; rows 111 to 121 are plain, as row 183 is)."""
    a = np.array(full)
    out = bare_of(full, boxes)
    cover = np.zeros(a.shape[:2], bool)
    for x0, y0, x1, y1 in boxes.values():
        cover[y0 - 1:y1 + 2, x0 - 1:x1 + 2] = True
    for x0, y0, x1, y1 in boxes.values():
        for y in range(y0 - 1, y1 + 2):
            for x in range(x0 - 1, x1 + 2):
                if y < 111:
                    out[y, x] = a[y0 - 2, x]
                elif 59 <= x <= 119:
                    out[y, x] = a[183 if y < 122 else y + 48, x]
                elif y == 111:
                    # (The cushions' bottom edge: a line under a cushion, the pillow's own colours under the pillow:
                    # the edge of the nearest open column that is the same thing over the box.)
                    above = a[y0 - 2, x]
                    xs = [u for u in range(a.shape[1]) if not cover[111, u] and (a[y0 - 2, u] == above).all()]
                    out[y, x] = a[111, min(xs, key=lambda u: abs(u - x))]
    return out


def mend_bed(im):
    # The redraw left its last row empty: the row above it again (the bed's foot, flat).
    a = np.array(im)
    a[-1] = a[-2]
    return Image.fromarray(a)


SCENES = {
    "desk": dict(
        tries="try1.png", mend=mend_desk,
        # Each thing's box on the canvas (x0, y0, x1, y1, inclusive), measured on full.png by its pixels that are none
        # of the surface's (the wall, the desk's back edge, its top, edge and front); where two touch, the line
        # between them (the plant's pot and the t-shirt's collar: row 128/129; the book and the diary: column
        # 324/325; the mask and the handheld: by colour, `pieces`).
        boxes={
            "flag": (35, 64, 82, 132),
            "plant": (84, 63, 120, 128),
            "tshirt": (45, 129, 146, 173),
            "sleepmask": (145, 120, 205, 152),
            "handheld": (196, 128, 275, 171),
            "pick": (287, 144, 312, 171),
            "bookmark": (266, 69, 324, 135),
            "diary": (325, 69, 365, 135),
        }),
    "bed": dict(
        tries="try-photo2-v3.png", mend=mend_bed, bits=True, bare=bare_bed,
        # Each of his eight, measured on full.png the same way (the bed's top and front, the runner, the cushions,
        # the pillow, the wall), and 2 px more all round (their light rims are the bed's colours): none touches
        # another or him.
        boxes={k: (x0 - 2, y0 - 2, x1 + 2, y1 + 2) for k, (x0, y0, x1, y1) in {
            "massage": (18, 99, 78, 164),
            "car": (272, 145, 306, 168),
            "bell": (321, 147, 349, 168),
            "feather": (150, 154, 198, 168),
            "snack": (212, 155, 256, 168),
            "ball": (282, 103, 317, 136),
            "wool": (322, 105, 351, 136),
            "sardines": (364, 143, 392, 168),
        }.items()}),
}


def bare_of(full, boxes):
    a = np.array(full)
    out = a.copy()
    # (Every box together: a row is filled from the nearest pixel left of them all.)
    cover = np.zeros(a.shape[:2], bool)
    for x0, y0, x1, y1 in boxes.values():
        cover[y0 - 1:y1 + 2, x0 - 1:x1 + 2] = True
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if cover[y, x]:
                out[y, x] = out[y, x - 1]
    return out


def pieces(full, bare, boxes, bits=False):
    a = np.array(full)
    diff = np.any(a != bare, axis=2)
    got = {}
    for name, (x0, y0, x1, y1) in boxes.items():
        own = np.zeros(diff.shape, bool)
        own[y0:y1 + 1, x0:x1 + 1] = diff[y0:y1 + 1, x0:x1 + 1]
        got[name] = own
    # (The desk's) The mask's tip and the handheld's grip share columns 196 to 205: the mask's pixels are its pinks
    # (red over 0xd0), the handheld's its darks; a dark px with pink on three sides is the mask's.
    if "sleepmask" in got and "handheld" in got:
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
                d = [((x - (b[0] + b[2]) / 2) ** 2 + (y - (b[1] + b[3]) / 2) ** 2) for b in (boxes[n1], boxes[n2])]
                got[n2 if d[0] < d[1] else n1][y, x] = False
    # A bit apart from a thing's body is the surface's (a few px of the desk's back edge by the flag): it goes back to
    # the bare picture, the thing keeps its largest piece. (`bits`: the bed's are the things' own, specks the redraw
    # put round them; left on the bare bed they showed where a thing had been.)
    loose = np.zeros(diff.shape, bool)
    for name, own in ({} if bits else got).items():
        n, lab, st, _ = cv2.connectedComponentsWithStats(own.astype(np.uint8), connectivity=8)
        if n > 2:
            keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            for i in range(1, n):
                if i != keep:
                    print(f"  {name}: {st[i, cv2.CC_STAT_AREA]} px at {st[i, 0]},{st[i, 1]} back to the picture")
                    loose |= lab == i
            own &= lab == keep
    # (And a px of the 1 px ring round a box that the fill changed is the surface's own: the bed's pillow edge.)
    # (With `bits`, the thing's whose box is nearest: specks just past its edge.)
    ring = diff.copy()
    for own in got.values():
        ring &= ~own
    if bits:
        for y, x in zip(*np.where(ring)):
            d = {n: max(b[0] - x, x - b[2], 0) + max(b[1] - y, y - b[3], 0) for n, b in boxes.items()}
            got[min(d, key=d.get)][y, x] = True
    else:
        loose |= ring
    bare[loose] = a[loose]
    diff &= ~loose
    taken = np.zeros(diff.shape, bool)
    for name, own in got.items():
        assert not (taken & own).any(), name
        taken |= own
    assert not (diff & ~taken).any(), "a changed px in no box"
    return got


def build(scene, cfg):
    src = ROOT / "assets" / "source" / "closeups" / scene
    out = ROOT / "assets" / "ship" / scene
    full = cfg["mend"](Image.open(src / "tries" / cfg["tries"]).convert("RGBA"))
    full.save(src / "full.png")
    bare = cfg.get("bare", bare_of)(full, cfg["boxes"])
    got = pieces(full, bare, cfg["boxes"], cfg.get("bits", False))    # (puts a thing's loose bits back into `bare`)
    Image.fromarray(bare).save(src / "bare.png")
    layout = {}
    for name, own in got.items():
        a = np.array(full).copy()
        a[~own] = 0
        Image.fromarray(a).save(src / f"{name}.png")
        ys, xs = np.where(own)
        layout[name] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1 - int(xs.min()), int(ys.max()) + 1 - int(ys.min())]
    (src / "layout.json").write_text(json.dumps(layout, indent=1))
    # The game's: the bare picture, each thing cut to its box, and where each box is (`assets/ship/<scene>/`).
    out.mkdir(parents=True, exist_ok=True)
    Image.fromarray(bare).save(out / "bare.png")
    for name, (x, y, w, h) in layout.items():
        Image.open(src / f"{name}.png").crop((x, y, x + w, y + h)).save(out / f"{name}.png")
    (out / "layout.json").write_text(json.dumps(layout))
    print(f"{scene}: wrote full.png, bare.png, the {len(layout)} pieces and layout.json in", src.relative_to(ROOT))


def main():
    for scene, cfg in SCENES.items():
        build(scene, cfg)


if __name__ == "__main__":
    main()
