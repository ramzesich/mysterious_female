"""Takes out the dark brown chair skeleton-v3 drew under her in `raw2/` (the sit-down and the lick, one clip). Its darks
are her hair's too, so it goes by its shape: its own mauves (`OWN`) anywhere; a chair dark (`DARK`) with one of them beside
it in its row (the backrest's and the legs' outlines); and the seat's rows (where its lavender runs, a row either side),
there every chair colour, and near-black only where nothing of her is beside it. Out: `clean2/`."""
import os

import numpy as np
from scipy import ndimage
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OWN = {(111, 89, 89), (122, 104, 120), (64, 47, 55)}
DARK = {(52, 35, 43), (35, 23, 36), (24, 13, 22), (80, 61, 67)}
SEAT_RUN = {(122, 104, 120)}
FROM_ROW = 50


def clean(a):
    h, w = a.shape[:2]
    c = [[tuple(int(v) for v in a[y, x, :3]) if a[y, x, 3] else None for x in range(w)] for y in range(h)]
    # (Below her shoulders only: the chair's lavender is her hair's sheen too.)
    own = np.array([[c[y][x] in OWN and y >= FROM_ROW for x in range(w)] for y in range(h)])
    gone = own.copy()
    for y in range(h):
        for x in range(w):
            if c[y][x] in DARK and (own[y, max(0, x - 1)] or own[y, min(w - 1, x + 1)]):
                gone[y, x] = True
    seat = [y for y in range(FROM_ROW, h) if sum(c[y][x] in SEAT_RUN for x in range(w)) >= 5]
    if seat:
        for y in range(min(seat) - 1, max(seat) + 2):
            xs = [x for x in range(w) if c[y][x] in SEAT_RUN]
            lo, hi = min(xs or [0]), max(xs or [w - 1])
            for x in range(max(0, lo - 2), min(w, hi + 3)):
                if c[y][x] in DARK | OWN:
                    gone[y, x] = True
    a = a.copy()
    a[gone] = 0
    for _ in range(2):
        dark = (a[..., 3] > 0) & (a[..., :3].max(axis=2) < 40)
        her = (a[..., 3] > 0) & ~dark
        near = np.zeros_like(her)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                near |= np.roll(np.roll(her, dy, 0), dx, 1)
        a[dark & ~near & (np.arange(h)[:, None] >= 56)] = 0
    # Specks of the chair left loose: anything not joined to her (her largest piece).
    lab, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        a[(lab > 0) & (lab != 1 + int(np.argmax(sizes)))] = 0
    return a


os.makedirs(os.path.join(HERE, "clean2"), exist_ok=True)
for f in sorted(os.listdir(os.path.join(HERE, "raw2"))):
    Image.fromarray(clean(np.array(Image.open(os.path.join(HERE, "raw2", f)).convert("RGBA")))).save(os.path.join(HERE, "clean2", f))
print("ok")
