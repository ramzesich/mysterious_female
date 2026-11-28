"""Her massage pad (try 3, the user's choice, 2026-11-28): every rosette 4 px left, and one more at the right end of the
top and the middle rows, the row's last repeated at its own spacing. Each rosette a tile (its box and 1 px); its place
filled with the fabric's own colour for that row (the crowns over the curve: the top edge and the empty ground).
    python rows.py OUT [the blue's factor]"""
import sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image

HERE = Path(__file__).parent
a = np.array(Image.open(HERE / "3-cut.png").convert("RGBA")).astype(int)
H, W = a.shape[:2]
SHIFT = -4
light = (a[..., :3].min(2) > 150) & (a[..., 3] > 0)
n, lab, st, _ = cv2.connectedComponentsWithStats(light.astype(np.uint8), connectivity=8)
tiles = []
for i in range(1, n):
    x, y, w, h, area = st[i]
    if area < 20: continue
    tiles.append((y, x, w, h))
rows = {"top": [t for t in tiles if t[0] < 18], "mid": [t for t in tiles if 18 <= t[0] < 30], "bot": [t for t in tiles if t[0] >= 30]}
for k in rows: rows[k].sort(key=lambda t: t[1])
print({k: [(t[1], t[0], t[2], t[3]) for t in v] for k, v in rows.items()})
# (A crown's tile stops at row 20, where the crowns end: below it are the middle row's spikes.)
box = lambda k, y, x, w, h: (max(0, x - 1), max(0, y - 1), min(W, x + w + 1), min(21 if k == "top" else H, y + h + 1))
boxes = [box(k, *t) for k in rows for t in rows[k]]
taken = np.zeros((H, W), bool)
for x0, y0, x1, y1 in boxes: taken[y0:y1, x0:x1] = True
fabric = (a[..., 2] > a[..., 0] + 40) & (a[..., 3] > 0) & ~taken
src = a.copy()
out = a.copy()
TOP = 15                                   # the pad's flat top row
edge = np.median(a[TOP, 105:116][:, :4], axis=0) if True else None
for x0, y0, x1, y1 in boxes:
    for y in range(y0, y1):
        for x in range(x0, x1):
            if y < TOP:
                out[y, x] = 0
            elif y == TOP and y0 < TOP:
                out[y, x] = edge
            else:
                f = a[y][fabric[y]]
                out[y, x] = np.median(f, axis=0) if len(f) else out[y, x]
def paste(box, dx):
    x0, y0, x1, y1 = box
    t = src[y0:y1, x0:x1]
    for yy in range(y1 - y0):
        for xx in range(x1 - x0):
            p = t[yy, xx]
            if p[3] == 0: continue
            X = x0 + xx + dx
            if 0 <= X < W: out[y0 + yy, X] = p
for k, v in rows.items():
    for t in v:
        paste(box(k, *t), SHIFT)
    if k in ("top", "mid"):
        pitch = round((v[-1][1] - v[0][1]) / (len(v) - 1))
        y, x, w, h = v[-1]
        paste(box(k, *v[-1]), SHIFT + pitch)
        print(k, "pitch", pitch, "new at", x + SHIFT + pitch)
# The pad's own blue darker (the user, 2026-11-28): its fabric's px, not the rosettes or the piping.
K = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
blue = (out[..., 2] > out[..., 0] + 40) & (out[..., 3] > 0) & (out[..., :3].min(2) < 150)
out = out.astype(float); out[blue, :3] *= K
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(sys.argv[1])
