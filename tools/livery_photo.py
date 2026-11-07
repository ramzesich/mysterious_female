"""The livery's generation inputs, from the user's side photo (GAME_DESIGN.md §8, the livery).

Only needed to generate the livery's tiles again; `tools/build_livery.py` builds the game's livery
from the tiles already in assets/source/livery/. Reads reference/photos/side-full.jpg (git-ignored,
never committed) and writes into %TEMP%/bumbusik-playtest/livery:

    python tools/livery_photo.py straighten    # the photo in game pixels: straight.png
    python tools/livery_photo.py tiles         # the first pass's inputs: in-<tile>.png (400 px wide)
    python tools/livery_photo.py unwindow      # the second pass's inputs: un-<tile>.png, from gen-*.png

Each tile then goes through PixelLab's create_image_pixflux at its size, img2img: in-* at strength
150 gives gen-*, un-* at 120 gives p2-* (descriptions: "flat graphic livery painted on a smooth
plain white ship hull: ..., no windows, no seams, no doors"). Save both into assets/source/livery/.
"""

import os
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ship_map as b  # noqa: E402
from build_livery import ORIGIN, SCALE, SRC, TILES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("TEMP", "/tmp")) / "bumbusik-playtest" / "livery"
TOP, BOTTOM = 640, 1830           # map rows straightened (the photo's layout, before the user's moves)


def straighten():
    """The side photo into game pixels. Along the ship: anchors in metres (the stem, the sun's
    disc, the promenade's opening, the boats, the glazed bay), linear between them. Up and down: at
    the bow its top edge to deck 7's floor and the waterline to the game's; from the sun aft the
    promenade's floor to deck 6's at 2.8 game px per photo px; blended between."""
    E = b.exact_x
    ax = [(504, 60), (3599, 1068), (4081, 1218), (5232, 1510), (E(100.8), 1590), (E(113), 1740),
          (E(123.4), 1850), (E(131), 1970), (E(143), 2225), (E(155.6), 2395), (E(166.6), 2562)]
    gx = np.arange(ORIGIN[0], E(185)).astype(float)
    G, P = np.array([a for a, _ in ax], float), np.array([p for _, p in ax], float)
    px = np.interp(gx, G, P)
    lo, hi = gx < G[0], gx > G[-1]
    px[lo] = P[0] + (gx[lo] - G[0]) * (P[1] - P[0]) / (G[1] - G[0])
    px[hi] = P[-1] + (gx[hi] - G[-1]) * (P[-1] - P[-3]) / (G[-1] - G[-3])
    kb = (b.WATER_ROW * 16 - b.floor_y(7)) / (1907 - 1598)
    t = np.clip((px - 600) / (950 - 600), 0, 1)
    k = kb * (1 - t) + 2.8 * t
    g0 = b.floor_y(7) * (1 - t) + b.floor_y(6) * t
    p0 = 1598 * (1 - t) + 1683 * t
    gy = np.arange(TOP, BOTTOM).astype(float)
    mapx = np.tile(px.astype(np.float32), (len(gy), 1))
    mapy = (p0[None, :] + (gy[:, None] - g0[None, :]) / k[None, :]).astype(np.float32)
    img = cv2.imread(str(ROOT / "reference" / "photos" / "side-full.jpg"))
    # The ship's name and the dark hull door on the bow: not part of the livery.
    box = img[1690:1755, 530:1010]
    text = cv2.dilate((cv2.cvtColor(box, cv2.COLOR_BGR2HSV)[..., 2] < 62).astype(np.uint8), np.ones((9, 9), np.uint8))
    img[1690:1755, 530:1010] = cv2.inpaint(box, text, 5, cv2.INPAINT_TELEA)
    door = np.zeros(img.shape[:2], np.uint8)
    door[1765:1830, 610:705] = 1
    img = cv2.inpaint(img, door, 9, cv2.INPAINT_TELEA)
    # Even out the overcast day's light: each pixel over the hull's local white.
    white = cv2.GaussianBlur(cv2.dilate(img, np.ones((61, 61), np.uint8)), (0, 0), 25).astype(float)
    img = np.clip(img.astype(float) / np.maximum(white, 40) * 250, 0, 255).astype(np.uint8)
    out = cv2.remap(img, mapx, mapy, cv2.INTER_CUBIC, borderValue=(255, 255, 255))
    # White where the game has no hull for it: the promenade's opening, forward of the stem, over
    # the forecastle.
    H, W = out.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    gy, gx = ys + TOP, xs + ORIGIN[0]
    m = (gx - b.exact_x(0)) / 48
    out[(m >= 99) & (gy < b.floor_y(6))] = 255
    stem = np.array([b.stem_x(y / 16) for y in range(TOP, TOP + H)])
    out[gx < stem[:, None] + 2] = 255
    out[(gy < b.floor_y(7)) & (m < 30)] = 255
    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / "straight.png"), out)
    return out


def tiles():
    """Each tile's piece of the straightened photo, at a third of the game's scale."""
    img = cv2.imread(str(OUT / "straight.png"))
    for name, (x, y) in TILES.items():
        h = 1104 if y < 1000 else 540                      # the aft tiles: under the promenade only
        c = img[y - TOP:y - TOP + h, x - ORIGIN[0]:x - ORIGIN[0] + 1200]
        cv2.imwrite(str(OUT / f"in-{name}.png"), cv2.resize(c, (400, h // SCALE), interpolation=cv2.INTER_AREA))


def unwindow():
    """The first pass kept the photo's windows: their near-black panes and their small grey rims
    painted over from the paint nearest them, for the second pass."""
    from scipy.ndimage import distance_transform_edt
    for name in TILES:
        g = cv2.imread(str(SRC / f"gen-{name}.png"))
        hsv = cv2.cvtColor(g, cv2.COLOR_BGR2HSV).astype(int)
        h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
        core = (v < 35) | ((v < 72) & (s < 140)) | ((s >= 50) & (h > 40) & (h < 160))
        grey = ((s < 50) & (v >= 90) & (v < 175)).astype(np.uint8)
        n, comp, st, _ = cv2.connectedComponentsWithStats(grey, connectivity=8)
        core |= (grey > 0) & (st[comp, cv2.CC_STAT_AREA] < 60) & (st[comp, cv2.CC_STAT_WIDTH] < 16) \
            & (st[comp, cv2.CC_STAT_HEIGHT] < 16)
        holes = cv2.dilate(core.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))).astype(bool)
        _, (iy, ix) = distance_transform_edt(holes, return_indices=True)
        cv2.imwrite(str(OUT / f"un-{name}.png"), cv2.medianBlur(g[iy, ix], 3))


if __name__ == "__main__":
    {"straighten": straighten, "tiles": tiles, "unwindow": unwindow}[sys.argv[1]]()
    print("wrote into", OUT)
