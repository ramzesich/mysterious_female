"""His walk (east): where his back's outline on the shirt's rows is 2 or more px of black (the far arm's shadow drawn
outside him), only its inner px kept, his 1 px outline. walk/east/<i>.png to walk-clean/<i>.png."""
import os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for i in range(6):
    a = np.array(Image.open(os.path.join(HERE, "walk", "east", f"{i}.png")).convert("RGBA")).astype(int)
    op = a[..., 3] > 0
    dark = op & (a[..., :3].sum(2) < 120)
    light = op & (a[..., :3].min(2) > 140)
    n = 0
    for y in range(a.shape[0]):
        xs = np.where(op[y])[0]
        if not len(xs) or not light[y].any() or not 30 <= y <= 58:   # (the shirt's rows only, not his shoes)
            continue
        x = xs[0]
        # a run of dark from his back edge inward, with the shirt after it
        run = 0
        while dark[y, x + run]:
            run += 1
        if run >= 2 and light[y, x + run]:
            a[y, x:x + run - 1] = 0
            n += run - 1
    Image.fromarray(a.astype(np.uint8)).save(os.path.join(HERE, "walk-clean", f"{i}.png"))
    print(i, n, "px off his back")
