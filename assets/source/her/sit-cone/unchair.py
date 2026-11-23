"""Takes out the chair skeleton-v3 drew under her in `raw/` (a mauve chair; the user, 2026-11-23: she sits in the game's
own patio chair): its two mauves (`CHAIR`) below her hair, and its lavender (`EDGE`) only where it touches them (the
same lavender shades her blouse); then any dark outline pixel left with nothing of her beside it. Out: `clean/`."""
import os
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CHAIR = {(111, 89, 89), (122, 104, 120), (128, 130, 133), (119, 121, 122), (112, 112, 113)}   # (the 4th frame's in greys)
EDGE = {(123, 129, 161)}
FROM_ROW = 50


def clean(a):
    h, w = a.shape[:2]
    col = lambda y, x: tuple(int(v) for v in a[y, x, :3])
    gone = np.zeros((h, w), bool)
    q = deque()
    for y in range(FROM_ROW, h):
        for x in range(w):
            if a[y, x, 3] and col(y, x) in CHAIR:
                gone[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v, u = y + dy, x + dx
            if 0 <= v < h and 0 <= u < w and not gone[v, u] and a[v, u, 3] and col(v, u) in EDGE | CHAIR:
                gone[v, u] = True
                q.append((v, u))
    a = a.copy()
    a[gone] = 0
    # Dark outline pixels left alone (the chair's own outline): nothing of hers but dark beside them.
    for _ in range(2):
        dark = (a[..., 3] > 0) & (a[..., :3].max(axis=2) < 40)
        her = (a[..., 3] > 0) & ~dark
        near = np.zeros_like(her)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                near |= np.roll(np.roll(her, dy, 0), dx, 1)
        a[dark & ~near & (np.arange(h)[:, None] >= FROM_ROW)] = 0
    return a


os.makedirs(os.path.join(HERE, "clean"), exist_ok=True)
for f in sorted(os.listdir(os.path.join(HERE, "raw"))):
    a = np.array(Image.open(os.path.join(HERE, "raw", f)).convert("RGBA"))
    Image.fromarray(clean(a)).save(os.path.join(HERE, "clean", f))
print("ok")
