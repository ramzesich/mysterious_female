"""The massage table without its back legs (the user, 2026-11-22: "delete the back table legs"): tries/3.png (the chosen
try) to frame_0.png. Its box on the 80 x 36 canvas starts at (7, 8); under the top (from row 14 of the box) the back legs
are the dark columns inside the front ones: 6 to 9 at the left end, 55 to 57 at the right."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, "tries", "3.png")).convert("RGBA")
x0, y0 = 7, 8
px = im.load()
for cols in (range(6, 10), range(55, 58)):
    for y in range(y0 + 14, im.height):
        for c in cols:
            px[x0 + c, y] = (0, 0, 0, 0)
im.save(os.path.join(HERE, "frame_0.png"))
print("wrote frame_0.png")
