"""Her own face in every frame of `clean2/` (the user, 2026-11-23: "Her face is distorted while she's eating"; skeleton-v3
redraws the head each frame: puffed red lips, closed eyes, a swollen chin): her standing sprite's head
(`assets/source/her/rotations/east.png`, rows `HEAD`, the face in every other scene of hers) placed where each frame's
own head best matches it, that head cleared first (a box a few px wider in front, for the puffed lips). Out: `faced/`."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
STAND = np.array(Image.open(os.path.join(HERE, "..", "rotations", "east.png")).convert("RGBA")).astype(int)
HEAD = (4, 21)
H = STAND[HEAD[0]:HEAD[1]]
M = H[..., 3] > 0
cols = np.where(M.any(axis=0))[0]
C0, C1 = cols.min(), cols.max()


def place(F):
    best = None
    for oy in range(10, 45):
        for ox in range(0, F.shape[1] - H.shape[1] + 1):
            P = F[oy:oy + H.shape[0], ox:ox + H.shape[1]]
            e = ((np.abs(P[..., :3] - H[..., :3]).sum(axis=2)) * M).sum() / M.sum() + 200 * ((P[..., 3] == 0) & M).mean()
            if best is None or e < best[0]:
                best = (e, ox, oy)
    return best


os.makedirs(os.path.join(HERE, "faced"), exist_ok=True)
for f in sorted(os.listdir(os.path.join(HERE, "clean2")), key=lambda s: int(s.split(".")[0])):
    F = np.array(Image.open(os.path.join(HERE, "clean2", f)).convert("RGBA")).astype(int)
    e, ox, oy = place(F)
    out = F.copy()
    out[oy:oy + H.shape[0] - 3, ox + C0:ox + C1 + 4] = 0           # her own head (the last rows: her neck, kept)
    sub = out[oy:oy + H.shape[0], ox:ox + H.shape[1]]
    sub[M] = H[M]
    Image.fromarray(out.astype(np.uint8)).save(os.path.join(HERE, "faced", f))
    print(f, "head at", ox, oy, "match", round(e, 1))
