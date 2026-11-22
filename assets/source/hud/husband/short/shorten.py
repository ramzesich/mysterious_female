"""His views with one row of his forehead taken out, as on his HUD icon (the user, 2026-11-22: "Remove one line from
my forehead, like we did on the icon"). The row is one of two alike on his forehead (the back of his head in the north
view); everything over it comes down a px, his feet stay where they were. ../<view>.png to <view>.png here."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = {"east": 6, "west": 6, "south": 6, "south-bear": 6, "north": 8}
for view, row in ROWS.items():
    a = np.array(Image.open(os.path.join(HERE, "..", f"{view}.png")).convert("RGBA"))
    out = np.zeros_like(a)
    out[1:row + 1] = a[:row]
    out[row + 1:] = a[row + 1:]
    Image.fromarray(out).save(os.path.join(HERE, f"{view}.png"))
    print(view, "row", row)
