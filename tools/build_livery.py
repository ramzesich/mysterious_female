"""The ship's sun livery (GAME_DESIGN.md §5.3, the outside of the ship), from PixelLab tiles to one
picture at the game's scale.

The tiles were generated with create_image_pixflux from the user's side photo, straightened into
game pixels and cut into pieces at a third of the game's scale (the photos stay in reference/, never
committed): gen-*.png at img2img strength 150 from the photo (they kept its windows), then p2-*.png
at strength 120 from gen-*.png with the windows painted over from the paint round them (clean). Here
every pixel of p2-*.png is sorted into the livery's flat colours, and each colour is enlarged on its
own, smoothly, then the strongest wins at each game pixel, so the edges stay crisp at three times
the size. Overlapping tiles fade into each other.

Writes assets/source/livery/livery.png (transparent where the hull is plain white), whose top-left
corner is at ORIGIN in the map; the map builder cuts it by the decks it lies across.
    python tools/build_livery.py
"""

import numpy as np
import cv2
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "livery"
SCALE = 3
# Each tile's top-left corner in map pixels.
TILES = {"t1": (384, 643), "t2": (1484, 643), "t3": (2384, 643), "sun": (3240, 643), "t5": (4290, 643),
         "a1": (5390, 1280), "a2": (6490, 1280), "a3": (7590, 1280)}
ORIGIN = (384, 640)
SIZE = (8806, 1272)           # to 9190 x 1912: past the ribbons' tips, down under the lowest one
FADE = 500                    # map pixels over which the bow's hard smoothing eases off
SOFTEN = 4.0                  # map pixels: how much each colour's edge is rounded before it is snapped
FEATHER = 120                 # map pixels over which overlapping tiles fade
SHIFT = 30 * 48               # the sun and all aft of it moved forward by 30 m (the user, 2026-11-07: it
                              # sat too far back; the sun fills the forward block's plain side)
DROP = 144                    # and all of it lowered by a deck (the user, 2026-11-07)
SQUEEZE_TO = 3240             # in the photo's layout: the bow's bands, up to here, squeezed to fit
# The sun's disc, drawn exactly where the generated one is (centre and radius in map pixels, after the
# shift): concentric rings, as painted on the real ship, from the outside in (fraction of the radius
# where each ring ends, colour index); the white centre is the hull.
DISC = (3180 - 16 * 48, 1125 + DROP, 255)
RINGS = [(1.0, 2), (0.84, 3), (0.62, 4), (0.47, 5), (0.37, 7), (0.18, 0)]

# The livery's colours (Resurrect 64). 0 is the plain hull, left transparent; 1 the grey shadow
# strokes. The generated tiles use a few dozen exact colours each (muted, embossed: the photo's
# overcast day); each goes to the livery colour it stands for by its hue and lightness.
COLOURS = [None, "#9babb2", "#ae2334", "#e83b3b", "#ea4f36", "#fb6b1d", "#f79617", "#f9c22b", "#d5e04b"]


def classify(bgr):
    """Each pixel's livery colour."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(int)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    out = np.zeros(h.shape, np.uint8)
    grey = s < 50
    out[grey & (v < 175)] = 1                                   # the shadow strokes; lighter is hull
    red = ~grey & ((h <= 6) | (h >= 165))
    out[red & (v < 115)] = 2
    out[red & (v >= 115)] = 3
    out[~grey & (h >= 7) & (h <= 9)] = np.where(v[~grey & (h >= 7) & (h <= 9)] >= 150, 4, 3)
    mid = ~grey & (h >= 10) & (h <= 16)
    out[mid] = np.where(v[mid] >= 140, 5, 4)
    out[~grey & (h >= 17) & (h <= 18)] = 6
    out[~grey & (h >= 19) & (h <= 26)] = 7
    out[~grey & (h >= 27) & (h <= 40)] = 8
    return out


def clean(lab):
    """Grey that is not a stroke made hull: a stroke runs right along the paint, thin; broad grey
    away from it is the generated hull's shading or seams. Then specks (a few pixels of one colour
    inside another) merged into their surroundings."""
    from scipy.ndimage import distance_transform_edt
    grey = (lab == 1).astype(np.uint8)
    thick = cv2.morphologyEx(grey, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    near = cv2.dilate((lab >= 2).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    lab[(thick > 0) | ((grey > 0) & (near == 0))] = 0
    # A stroke is long; short grey patches are what is left of the photo's windows.
    n, comp, st, _ = cv2.connectedComponentsWithStats((lab == 1).astype(np.uint8), connectivity=8)
    length = np.maximum(st[:, cv2.CC_STAT_WIDTH], st[:, cv2.CC_STAT_HEIGHT])
    lab[(lab == 1) & (length[comp] < 28)] = 0
    small = np.zeros(lab.shape, bool)
    for c in range(len(COLOURS)):
        n, comp, st, _ = cv2.connectedComponentsWithStats((lab == c).astype(np.uint8), connectivity=4)
        small |= (lab == c) & (st[comp, cv2.CC_STAT_AREA] < {0: 8, 1: 8, 2: 120, 3: 120}.get(c, 30))
    if small.any():
        _, (iy, ix) = distance_transform_edt(small, return_indices=True)
        lab = lab[iy, ix]
    return lab


def smooth(label, sigma, strong=None, weight=None):
    """Each pixel takes the colour most present round it (within about `sigma` pixels): edges
    rounded, notches filled, thin drips and specks gone. Where `weight` is above 0, the reach is
    blended toward `strong`."""
    best = np.zeros(label.shape, np.float32)
    out = np.zeros(label.shape, np.uint8)
    cols = slice(0, int(np.nonzero(weight[0] > 0)[0].max()) + 1) if weight is not None else slice(None)
    for c in range(len(COLOURS)):
        m = (label == c).astype(np.float32)
        score = cv2.GaussianBlur(m, (0, 0), sigma)
        if weight is not None:
            hard = cv2.GaussianBlur(m[:, cols], (0, 0), strong)
            w = weight[:, cols]
            score[:, cols] = score[:, cols] * (1 - w) + hard * w
        win = score > best
        best[win] = score[win]
        out[win] = c
    return out


def moved(X):
    """Where in the photo's layout the livery's column X (map pixels) is taken from: the sun and all
    aft of it SHIFT pixels forward of where the photo has it (the user: it sat too far back), the
    bow's bands squeezed between the stem and the sun to make room."""
    X = np.asarray(X, np.float32)
    a, b = ORIGIN[0], SQUEEZE_TO
    return np.where(X >= b - SHIFT, X + SHIFT, a + (X - a) * (b - a) / (b - SHIFT - a))


def feather(w, h):
    """A tile's weight: full inside, fading to its edges over FEATHER map pixels."""
    x = np.minimum(np.arange(w), np.arange(w)[::-1]) / FEATHER
    y = np.minimum(np.arange(h), np.arange(h)[::-1]) / FEATHER
    return np.clip(np.minimum.outer(y, x), 0.02, 1).astype(np.float32)


def build():
    W, H = SIZE
    best = np.zeros((H, W), np.float32)
    label = np.zeros((H, W), np.uint8)
    tiles = []
    for name, (x, y) in TILES.items():
        lab = clean(classify(cv2.imread(str(SRC / f"p2-{name}.png"))))
        h, w = lab.shape
        tiles.append((x - ORIGIN[0], y - ORIGIN[1], lab, feather(w * SCALE, h * SCALE)))
    for c in range(len(COLOURS)):
        score = np.zeros((H, W), np.float32)
        weight = np.zeros((H, W), np.float32)
        for x, y, lab, wt in tiles:
            soft = cv2.resize((lab == c).astype(np.float32), (lab.shape[1] * SCALE, lab.shape[0] * SCALE),
                              interpolation=cv2.INTER_CUBIC)
            soft = cv2.GaussianBlur(soft, (0, 0), SOFTEN)
            sh, sw = min(soft.shape[0], H - y), min(soft.shape[1], W - x)
            score[y:y + sh, x:x + sw] += soft[:sh, :sw] * wt[:sh, :sw]
            weight[y:y + sh, x:x + sw] += wt[:sh, :sw]
        score /= np.maximum(weight, 1e-6)
        mapx = np.tile(moved(np.arange(W) + ORIGIN[0]) - ORIGIN[0], (H, 1)).astype(np.float32)
        mapy = np.repeat(np.arange(H, dtype=np.float32)[:, None] - DROP, W, 1)
        score = cv2.remap(score, mapx, mapy, cv2.INTER_LINEAR, borderValue=0)
        win = score > best
        best[win] = score[win]
        label[win] = c
    # Edges rounded a little everywhere; the bow's bands, long plain swooshes, smoothed hard, so the
    # notches and drips left where the photo's windows and hull door were painted over go (the
    # user, 2026-11-07), easing back over FADE pixels toward the sun's rays. Grey there is what is
    # left of them too.
    bow = int(DISC[0] - DISC[2] * 2.2 - ORIGIN[0])
    weight = np.clip((bow + FADE - np.arange(W)) / FADE, 0, 1).astype(np.float32)[None, :]
    label = smooth(label, 3, 24, weight)
    label[(label == 1) & (weight > 0)] = 0
    # Spots left of the photo's windows inside a band: small, with paint all round. They take the
    # band's colour.
    for c in range(2, len(COLOURS)):
        n, comp, st, _ = cv2.connectedComponentsWithStats((label == c).astype(np.uint8), connectivity=8)
        for i in np.nonzero(st[:, cv2.CC_STAT_AREA] < 2000)[0]:
            if i == 0:
                continue
            x, y, w, h = st[i, :4]
            x0, y0 = max(0, x - 3), max(0, y - 3)
            sub = comp[y0:y + h + 3, x0:x + w + 3] == i
            ring = cv2.dilate(sub.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~sub
            around = label[y0:y + h + 3, x0:x + w + 3][ring]
            if around.size and (around >= 2).all():
                label[y0:y + h + 3, x0:x + w + 3][sub] = np.bincount(around).argmax()
    cx, cy, r = DISC[0] - ORIGIN[0], DISC[1] - ORIGIN[1], DISC[2]
    ys, xs = np.ogrid[0:H, 0:W]
    d = np.hypot(xs - cx, ys - cy)
    label[(d > r) & (d <= r + 14) & (label != 1)] = 0     # a white gap round it, as on the ship
    for frac, c in RINGS:
        label[d <= r * frac] = c
    out = np.zeros((H, W, 4), np.uint8)
    for c, colour in enumerate(COLOURS):
        if colour:
            out[label == c] = [int(colour[5:7], 16), int(colour[3:5], 16), int(colour[1:3], 16), 255]
    path = SRC / "livery.png"
    cv2.imwrite(str(path), out)
    return path


if __name__ == "__main__":
    print("wrote", build().relative_to(ROOT))
