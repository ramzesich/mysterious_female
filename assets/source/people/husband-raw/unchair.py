"""His seated clips (skeleton-v3, east): the generator drew a brown chair under him (a backrest behind his back, a leg,
the seat's edge under his thighs). Taken out by its own colours below his neck, then its outline (dark pixels with
nothing of his beside them). The game's patio chair is drawn behind him, its near arm in front (the people's `cover`).
<clip>/east/<i>.png to <clip>/clean/<i>.png. `python unchair.py <clip> ...`"""
import os, sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CHAIR = {(0x4b, 0x38, 0x2d), (0x69, 0x4e, 0x42), (0x38, 0x29, 0x21), (0x42, 0x2e, 0x21)}
NECK = 44          # rows from here down (his hair is above)
BACK = 37          # his back's column: the chair's backrest is behind it
SEAT = 58          # the seat's row: the chair's seat and leg are under it (the shadow under his chin has its brown)


def dark(c):
    return sum(c) < 3 * 24


def clean(a):
    a = a.copy()
    h, w = a.shape[:2]
    gone = 0
    for y in range(NECK, h):
        for x in range(w):
            if a[y, x, 3] and tuple(a[y, x, :3]) in CHAIR and (x <= BACK or y >= SEAT):
                a[y, x] = 0
                gone += 1
    for _ in range(3):
        drop = []
        for y in range(NECK, h):
            for x in range(w):
                if not a[y, x, 3] or not dark(tuple(int(v) for v in a[y, x, :3])):
                    continue
                near = [a[v, u] for v in range(max(0, y - 1), min(h, y + 2)) for u in range(max(0, x - 1), min(w, x + 2)) if (v, u) != (y, x)]
                if not any(n[3] and not dark(tuple(int(v) for v in n[:3])) for n in near):
                    drop.append((y, x))
        for y, x in drop:
            a[y, x] = 0
        gone += len(drop)
    return a, gone


if __name__ == "__main__":
    for clip in sys.argv[1:]:
        src = os.path.join(HERE, clip, "east")
        out = os.path.join(HERE, clip, "clean")
        os.makedirs(out, exist_ok=True)
        for f in sorted(os.listdir(src), key=lambda s: int(s.split(".")[0])):
            a, gone = clean(np.array(Image.open(os.path.join(src, f)).convert("RGBA")))
            Image.fromarray(a).save(os.path.join(out, f))
            print(clip, f, gone)
