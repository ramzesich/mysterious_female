"""The Great Outdoors' table and chairs made beige (the user, 2026-11-22: "Make it beige. Also, make the chairs beige"):
each colour put on one beige ramp by its lightness (the table's white top and grey pedestal as they are, the chair's teak
lifted to the table's light). The table: tries/5.png to frame_0.png here; the chair: ../patio-chair/tries/5.png to
../patio-chair/frame_0.png."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RAMP = [(0.0, "2e2418"), (0.35, "6e5a40"), (0.6, "a8926e"), (0.8, "cdb994"), (1.0, "ece0c4")]


def ramp(k):
    k = min(1.0, max(0.0, k))
    for (a, ca), (b, cb) in zip(RAMP, RAMP[1:]):
        if k <= b:
            t = (k - a) / (b - a)
            ca, cb = (np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)]) for c in (ca, cb))
            return np.round(ca + (cb - ca) * t).astype(np.uint8)


def beige(src, out, lo, hi, k0, k1):
    a = np.array(Image.open(src).convert("RGBA"))
    b = a.getbbox() if False else Image.fromarray(a).getbbox()
    for y, x in zip(*np.where(a[..., 3] > 0)):
        L = 0.299 * a[y, x, 0] + 0.587 * a[y, x, 1] + 0.114 * a[y, x, 2]
        a[y, x, :3] = ramp(k0 + (L - lo) / (hi - lo) * (k1 - k0))
    Image.fromarray(a).crop((b[0], 0, b[2], b[3])).save(out)


beige(os.path.join(HERE, "tries", "5.png"), os.path.join(HERE, "frame_0.png"), 0, 255, 0, 1)
beige(os.path.join(HERE, "..", "patio-chair", "tries", "5.png"), os.path.join(HERE, "..", "patio-chair", "frame_0.png"), 60, 195, 0.3, 0.95)
