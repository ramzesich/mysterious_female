"""Her Albuca (try 2, the user's choice, 2026-11-28): the plant moved so that its bulb is over the pot's middle and
sunk into the soil, the picture's own soil and pot drawn back over it (nothing drawn in). python sink.py DX DY OUT"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
a = np.array(Image.open(HERE / "2-edit-photo.png").convert("RGBA"))
H, W = a.shape[:2]
POT = {(0x68, 0x30, 0x1e), (0x87, 0x53, 0x2d), (0xb1, 0x83, 0x5d), (0x75, 0x44, 0x26)}
X0, X1 = 44, 83                     # the pot's columns (its rim 47 to 81), the hanging leaves outside them
pot = np.zeros((H, W), bool)
for y in range(86, H):
    for x in range(X0, X1 + 1):
        pot[y, x] = a[y, x, 3] > 0 and tuple(a[y, x, :3]) in POT
# The soil: rows 83 to 85 inside the rim, its dark browns; where the bulb stood, the soil's own px from its left.
dark = lambda p: p[3] > 0 and int(p[:3].sum()) < 200 and not (int(p[1]) > int(p[0]) + 15)   # (its two dark browns; the olive by the bulb is the bulb's)
soil = np.zeros((H, W), bool)
band = a.copy()
for y in (83, 84, 85):
    xs = [x for x in range(47, 82) if dark(a[y, x])]
    lo, hi = min(xs), max(xs)
    for x in range(lo, hi + 1):
        soil[y, x] = dark(a[y, x])         # (only the picture's own soil: none drawn in where the bulb stood, the user)
plant = (a[..., 3] > 0) & ~pot & ~(soil & np.array([[dark(a[y, x]) for x in range(W)] for y in range(H)]))
dx, dy, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
res = np.zeros_like(a)
ys, xs = np.where(plant)
for y, x in zip(ys, xs):
    if 0 <= y + dy < H and 0 <= x + dx < W:
        res[y + dy, x + dx] = a[y, x]
res[soil] = band[soil]
res[pot] = a[pot]
Image.fromarray(res).save(out)
