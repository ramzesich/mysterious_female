"""The back view of his massage: his hands, drawn over his back, painted out (from behind they are hidden in front of
him). Writes massage-back/<i>.png beside the raw clip."""
import os
import numpy as np
from PIL import Image
RAW = r"C:\Users\ramze\Development\mysterious_female\assets\source\people\masseur-raw"
src = os.path.join(RAW, "massage", "north"); out = os.path.join(RAW, "massage-back"); os.makedirs(out, exist_ok=True)
for i in range(7):   # (7: his arms at his sides, as drawn)
    a = np.array(Image.open(os.path.join(src, f"{i}.png")).convert("RGBA")).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    op = al > 0
    skin = op & (r - b > 45) & (r > 90)
    dark = op & (r + g + b < 120)
    ys = np.where(op.any(1))[0]; top = ys[0]
    # the collar: the first row under the hair with the shirt's white
    white = op & (r > 200) & (g > 200) & (b > 200)
    collar = np.where(white.any(1))[0][0]
    skin[:collar + 2] = False
    if not skin.any():
        Image.fromarray(a.astype(np.uint8)).save(os.path.join(out, f"{i}.png")); print(i, "none"); continue
    band = np.where(skin.any(1))[0]; y0, y1 = band[0] - 1, band[-1] + 1
    # his sides: the outer columns of the shirt on the nearest rows above and below the band
    def sides(y):
        xs = np.where(op[y] & ~skin[y])[0]
        return xs[0], xs[-1]
    above = sides(y0 - 1); below = sides(y1 + 1)
    fixed = a.copy()
    for y in range(y0, y1 + 1):
        k = (y - y0) / max(1, y1 - y0)
        L = round(above[0] + (below[0] - above[0]) * k); R = round(above[1] + (below[1] - above[1]) * k)
        for x in range(L + 1, R):
            # (the whole band inside his outline: the shirt's column straight down from the row over it)
            # (one row for every frame, the upper back under his collar, so the back does not flicker as the clip loops)
            fixed[y, x] = a[collar + 4, x] if not (skin[collar + 4, x] or dark[collar + 4, x]) else fixed[y, x - 1]
        for x in (L, R):
            if skin[y, x] or not op[y, x]:
                fixed[y, x] = (1, 2, 5, 255)
    Image.fromarray(fixed.astype(np.uint8)).save(os.path.join(out, f"{i}.png")); print(i, "band", y0, y1, above, below)
