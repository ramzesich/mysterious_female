"""His near hand drawn again over her in the embrace (the user, 2026-11-23: "His only visible hand shall embrace her"):
in steps 2 and 3 of his `embrace` clip both hands meet at his waist, behind her lower back; his hand's own pixels (skin,
and the dark outline beside it) in that box are cut out, laid out as the people sheet places his frame (an 80 px cell,
the 96 px frame centred, its feet on the cell's bottom row: `cell_of` in tools/build_people.py), and the game draws
them over her: `assets/sprites/hug-hand-<n>.png`."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "..", "..", "sprites")
CELL = 80
BOX = (43, 46, 52, 55)          # x0, y0, x1, y1: round his clasped hands, in the 96 px frame


def skin(a):
    r, g, b, al = [a[..., i].astype(int) for i in range(4)]
    return (al > 0) & (r >= 170) & (g >= 110) & (g <= 210) & (b >= 80) & (b <= 190) & (r - b >= 40)


for n in (1, 2):
    a = np.array(Image.open(os.path.join(HERE, f"{n}.png")).convert("RGBA"))
    s = skin(a)
    near = np.zeros_like(s)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            near |= np.roll(np.roll(s, dy, 0), dx, 1)
    dark = (a[..., 3] > 0) & (a[..., :3].max(axis=2) < 60)
    keep = np.zeros_like(s)
    x0, y0, x1, y1 = BOX
    keep[y0:y1, x0:x1] = (s | (dark & near))[y0:y1, x0:x1]
    hand = np.zeros_like(a)
    hand[keep] = a[keep]
    feet = np.where((a[..., 3] > 0).any(axis=1))[0].max()
    cell = Image.new("RGBA", (CELL, CELL))
    cell.alpha_composite(Image.fromarray(hand).crop(((96 - CELL) // 2, feet + 1 - CELL, (96 - CELL) // 2 + CELL, feet + 1)))
    cell.save(os.path.join(OUT, f"hug-hand-{n}.png"))
    print(n, "hand px", int(keep.sum()), "feet row", feet)
