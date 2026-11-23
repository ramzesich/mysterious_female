"""Her hair in front of her forearms in the embrace (the user, 2026-11-23: "She is hugging herself, not him"): her arms
go round his neck, which is behind her head, so her forearms are behind her hair and only her raised upper arms show.
Her back view's own hair (`back-96.png`, `../rotations/north.png` on the frames' 96 px canvas; the head did not move)
drawn again over each frame of `raw/`. Out: `clean/`."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
B = np.array(Image.open(os.path.join(HERE, "back-96.png")).convert("RGBA")).astype(int)
lum = B[..., :3].mean(axis=2)
# (Her hair's own colours above her skirt, and the dark outline that touches them: not her hanging arms' outlines.)
core = (B[..., 3] > 0) & (lum >= 25) & (lum < 100) & (np.arange(96)[:, None] < 54)
grown = np.zeros_like(core)
for dy in (-1, 0, 1):
    for dx in (-1, 0, 1):
        grown |= np.roll(np.roll(core, dy, 0), dx, 1)
HAIR = grown & (B[..., 3] > 0) & (lum < 100) & (np.arange(96)[:, None] < 54)
os.makedirs(os.path.join(HERE, "clean"), exist_ok=True)
for i in range(3):
    a = np.array(Image.open(os.path.join(HERE, "raw", f"{i}.png")).convert("RGBA"))
    a[HAIR] = B[HAIR]
    Image.fromarray(a).save(os.path.join(HERE, "clean", f"{i}.png"))
print("hair px", int(HAIR.sum()))
