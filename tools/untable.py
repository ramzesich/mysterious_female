"""The spa's massage table taken out of the clips made with it (the massage scene, the user, 2026-11-22): each clip was
generated with the game's own table in its pictures (assets/source/ship/massage-table-2/frame_0.png, at `table` in the
clip's `layout.json`), so the figure lies on it and climbs it where it stands; the game draws its own table, so each
frame keeps the figure alone. A px is the table's where it is within 40 (summed channels) of the table's own px at that
spot; then only the figure's largest piece is kept (specks the generator left round the table).

    python tools/untable.py            (every clip below: raw/<i>.png to clean/<i>.png; then copy the guest's into
                                        assets/source/people/massage_guest/up/ and build the sheets)
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "assets" / "source" / "ship" / "massage-table-2" / "frame_0.png"
CLIPS = [
    ROOT / "assets" / "source" / "her" / "massage-lie",            # she climbs on and lies face down (raw2: the second try)
    ROOT / "assets" / "source" / "people" / "massage_guest-raw" / "up",  # the guest gets up and stands
]
RAW = {"massage-lie": "raw2", "up": "raw"}
# Frames moved down this many px after: the guest on the table 2 px lower (the user, 2026-11-22: "should also be lowered at
# least two pixels", and one more, "move the lady one pixel down when she is on the table"), less as she sits up,
# none once her feet are on the floor (frame 11 on).
LOWER = {"up": [3] * 9 + [2, 1] + [0] * 6}


# Her clip: greys of hers whose nearest palette colour is the dusky mauve her sheet turns pink-peach (`966c6c`, her skin's
# shading; tools/build_sprites.py's remap) take their next nearest instead: the generator shaded her blouse and lit her hair
# with warm greys, and in the game they were pink spots over her (the user, 2026-11-22). Her skin's own colours are not grey.
UNPINK = {"massage-lie"}
MAUVE = (0x96, 0x6c, 0x6c)


def unpink(a):
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from palettize import load_palette, srgb_to_lab
    pal = [(c, srgb_to_lab(c)) for c in load_palette() if tuple(c) != MAUVE]
    mauve = srgb_to_lab(MAUVE)
    out = a.copy()
    for y, x in zip(*np.where(a[..., 3] > 0)):
        rgb = tuple(int(v) for v in a[y, x, :3])
        if max(rgb) - min(rgb) > 40:
            continue                     # (a colour, not a grey: her skin, her scarf)
        lab = srgb_to_lab(rgb)
        dist = lambda p: sum((u - v) ** 2 for u, v in zip(lab, p))
        best = min(pal, key=lambda p: dist(p[1]))
        if dist(mauve) < dist(best[1]):
            out[y, x, :3] = best[0]
    return out


# Then, as her sheet will draw it (palette and remap), a pink-peach px that is no shading at an edge: by the blouse's
# whites it is the blouse's grey shade; inside her skin (no dark outline beside it) her skin's middle tone. The clip's
# skin was speckled pink, twice her standing frame's (the user: "too many pink pixels over her").
PINK, SKIN, BLOUSE_SHADE = (0xf6, 0x81, 0x81), (0xfc, 0xa7, 0x90), (0x9b, 0xab, 0xb2)
WHITES = {(0xff, 0xff, 0xff), (0xc7, 0xdc, 0xd0), (0x9b, 0xab, 0xb2)}


def unspeckle(a):
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from palettize import palettize
    from build_sprites import HER
    built = np.array(palettize(Image.fromarray(a.astype(np.uint8)), HER["remap"])).astype(int)
    out = a.copy()
    h, w = a.shape[:2]
    for y, x in zip(*np.where(built[..., 3] > 0)):
        if tuple(built[y, x, :3]) != PINK:
            continue
        nb = [tuple(built[v, u, :3]) for v, u in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
              if 0 <= v < h and 0 <= u < w and built[v, u, 3] > 0]
        if sum(c in WHITES for c in nb) >= 2:
            out[y, x, :3] = BLOUSE_SHADE
        elif len(nb) == 4 and not any(sum(c) < 150 for c in nb):
            out[y, x, :3] = SKIN
    return out


# The guest's clip: in each column, nothing below her lowest dark outline px (the bottom edge of her body, her slippers'
# soles): what hung there were the table's pad and pillow, redrawn a little off and so left in (the user, 2026-11-22: a
# glitch under her while she lies on the table, drawn over it). Then specks under 4 px.
UNDER = {"up"}


def under(a):
    out = a.copy()
    op = a[..., 3] > 0
    dark = op & (a[..., :3].sum(2) < 150)
    low = [int(np.where(dark[:, x])[0][-1]) if dark[:, x].any() else None for x in range(a.shape[1])]
    for x in range(a.shape[1]):
        # (The lowest outline within 3 px either side: a column whose own lowest dark px is high up (the turban's edge over
        # towel or skin) follows the body's bottom edge beside it.)
        near = [low[u] for u in range(max(0, x - 3), min(a.shape[1], x + 4)) if low[u] is not None]
        if near:
            out[max(near) + 1:, x] = 0
    # (And a light px hanging off her edge, with the air on two of its four sides or more: a leftover of the pad or the
    # pillow, a few times over.)
    for _ in range(4):
        op = out[..., 3] > 0
        light = op & (out[..., :3].sum(2) >= 150)
        air = np.zeros(op.shape, int)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            air += ~np.roll(np.roll(op, dy, 0), dx, 1)
        out[light & (air >= 2)] = 0
    m = (out[..., 3] > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] < 4:
            out[lab == k] = 0
    return out


def clean(folder):
    lay = json.loads((folder / "layout.json").read_text())
    tab = Image.open(TABLE).convert("RGBA")
    tab = np.array(tab.crop(tab.getbbox())).astype(int)
    tx, ty = lay["table"]
    raw = folder / RAW[folder.name]
    out = folder / "clean"
    out.mkdir(exist_ok=True)
    n = len(list(raw.glob("*.png")))
    for i in range(n):
        a = np.array(Image.open(raw / f"{i}.png").convert("RGBA")).astype(int)
        h, w = tab.shape[:2]
        box = a[ty:ty + h, tx:tx + w]
        near = (np.abs(box[..., :3] - tab[..., :3]).sum(2) < 40) & (tab[..., 3] > 0)
        box[near] = 0
        # (Below the table's top, outside its own px, nothing is hers but her legs: kept as drawn.)
        m = (a[..., 3] > 0).astype(np.uint8)
        k, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        if k > 1:
            big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            a[lab != big] = 0
        if folder.name in UNPINK:
            a = unspeckle(unpink(a))
        if folder.name in UNDER:
            a = under(a)
        down = LOWER.get(folder.name, [0] * n)[i]
        if down:
            a = np.roll(a, down, axis=0)
            a[:down] = 0
        Image.fromarray(a.astype(np.uint8)).save(out / f"{i}.png")
    print(folder.relative_to(ROOT), n, "frames cleaned")


if __name__ == "__main__":
    for f in CLIPS:
        clean(f)
