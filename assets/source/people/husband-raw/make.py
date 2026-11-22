"""His seated clips, ready for the people sheet (the user, 2026-11-22), from skeleton-v3's frames (`<clip>/east/`):

- One face: skeleton-v3 redraws his head a little in every frame (the first frame of the first try "distorted"); the
  head (rows `HEAD`) is the donor frame's in all of them. He breathes from the chest; his head holds still.
- One pair of legs: they do not move while he sits, so the donor frame's (rows `LEGS`) in all of them.
- "My far leg should be behind the table": his legs apart (the far one reaching forward under the table); what shows of
  the far one (right of the near leg's outline, `FAR_FROM` per row) is taken out of every frame into a picture of its
  own, `far` (one frame, the same canvas), which the game draws behind the map's furniture (the people's `under`).

Out: `out/<name>/<i>.png` and `out/far/0.png`; the approved go to `assets/source/people/husband/`."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = {"sit-idle-2": "idle"}
DONOR = 2
HEAD = (18, 40)
LEGS = (66, 80)
# The first column of the far leg in each row (the near leg's outline is the column before it).
FAR_FROM = {66: 59, 67: 57, 68: 57, 69: 57, 70: 56, 71: 55, 72: 55, 73: 54, 74: 56, 75: 58, 76: 58, 77: 58}


def load(clip, i):
    return np.array(Image.open(os.path.join(HERE, clip, "east", f"{i}.png")).convert("RGBA"))


def save(a, *p):
    path = os.path.join(HERE, "out", *p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(a).save(path)


far = None
for clip, name in CLIPS.items():
    donor = load(clip, DONOR)
    n = len(os.listdir(os.path.join(HERE, clip, "east")))
    for i in range(n):
        a = load(clip, i)
        a[HEAD[0]:HEAD[1]] = donor[HEAD[0]:HEAD[1]]
        a[LEGS[0]:LEGS[1]] = donor[LEGS[0]:LEGS[1]]
        if far is None:
            far = np.zeros_like(a)
            for y, x0 in FAR_FROM.items():
                far[y, x0:] = a[y, x0:]
        for y, x0 in FAR_FROM.items():
            a[y, x0:] = 0
        save(a, name, f"{i}.png")
save(far, "far", "0.png")
print("ok")
