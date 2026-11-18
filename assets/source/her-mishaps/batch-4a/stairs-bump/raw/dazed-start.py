"""Gag 21's dizzy end: its start (and end) picture, `raw/dazed-start.png`: the foot's stage, her last foot
frame (slumped), and the suitcase gag's two butterflies (`her-mishaps/suitcase-dazed/start.png`) set over her
head as they are over hers there (their lowest px the same height over the top of her head, their middle
over her head's)."""
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[3]
sc = np.array(Image.open(SRC / "her-mishaps" / "suitcase-dazed" / "start.png").convert("RGBA")).astype(int)
r, g, b, a = sc[..., 0], sc[..., 1], sc[..., 2], sc[..., 3]
fly = (a > 0) & (r > 100) & (r >= g) & (g > b + 40)
fly[45:] = False
ys, xs = np.nonzero(fly)
# (Her head there: her px under the butterflies, not theirs.)
herA = (a > 0) & ~fly
hy = np.nonzero(herA.any(1))[0].min()
hx = np.nonzero(herA[hy:hy + 6].any(0))[0]
gap, mid = hy - ys.max(), (hx.min() + hx.max()) / 2
foot = np.array(Image.open(HERE.parent / "foot" / "6.png").convert("RGBA"))
fa = foot[..., 3] > 0
fy = np.nonzero(fa.any(1))[0].min()
fx = np.nonzero(fa[fy:fy + 6].any(0))[0]
dx = round((fx.min() + fx.max()) / 2 - mid)
dy = fy - gap - ys.max()
print("butterflies moved by", dx, dy, "head top", fy, "gap", gap)
out = Image.open(HERE / "foot-stage.png").convert("RGBA")
out.alpha_composite(Image.fromarray(foot))
px = out.load()
for y, x in zip(ys, xs):
    # (Their dark outline px too: those next to a yellow one, from the same picture.)
    px[int(x + dx), int(y + dy)] = tuple(int(v) for v in sc[y, x])
for y in range(max(0, ys.min() - 1), ys.max() + 2):
    for x in range(max(0, xs.min() - 1), xs.max() + 2):
        if a[y, x] and not fly[y, x] and sc[y, x, :3].sum() < 40 and fly[max(0, y - 1):y + 2, max(0, x - 1):x + 2].any() and y < hy - 1:
            px[int(x + dx), int(y + dy)] = tuple(int(v) for v in sc[y, x])
out.save(HERE / "dazed-start.png")
