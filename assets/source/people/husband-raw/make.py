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
# folder: (clip, its frames in order, the donor's head pasted in). The gestures keep their own heads (his face acts:
# the laugh tips it back, the cone meets his mouth); every clip gets the donor's legs and loses its far leg.
CLIPS = {
    "sit-idle-2/east": ("idle", range(8), True),
    "sit-wave-2/east": ("wave", range(7), False),      # its 8th frame came out thinner and upright: the idle follows
    "sit-laugh/east": ("laugh", range(7), False),
    "sit-give/east": ("give", range(7), False),
    "eat-cone/e1": ("eat", range(8), False),          # PixMiniMax from eat-cone/still-s1.png; 0 is that still, 8 ~ 0
}
DONOR = 2
# A frame's head taken from another frame of the same clip in the same pose: the give's held frames (one pose) redrew
# his brow dark, a stern look as he hands her the book; the first held frame's face in all three.
FACE_FROM = {"sit-give/east": {3: 2, 4: 2}}
HEAD = (18, 40)
LEGS = (66, 80)
# The first column of the far leg in each row (the near leg's outline is the column before it).
FAR_FROM = {66: 59, 67: 57, 68: 57, 69: 57, 70: 56, 71: 55, 72: 55, 73: 54, 74: 56, 75: 58, 76: 58, 77: 58}


def load(folder, i):
    return np.array(Image.open(os.path.join(HERE, folder, f"{i}.png")).convert("RGBA"))


def save(a, *p):
    path = os.path.join(HERE, "out", *p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(a).save(path)


far = None
donor = load("sit-idle-2/east", DONOR)
for folder, (name, frames, head) in CLIPS.items():
    for k, i in enumerate(frames):
        a = load(folder, i)
        if head:
            a[HEAD[0]:HEAD[1]] = donor[HEAD[0]:HEAD[1]]
        elif i in FACE_FROM.get(folder, {}):
            a[HEAD[0]:HEAD[1]] = load(folder, FACE_FROM[folder][i])[HEAD[0]:HEAD[1]]
        a[LEGS[0]:LEGS[1]] = donor[LEGS[0]:LEGS[1]]
        if far is None:
            far = np.zeros_like(a)
            for y, x0 in FAR_FROM.items():
                far[y, x0:] = a[y, x0:]
        for y, x0 in FAR_FROM.items():
            a[y, x0:] = 0
        save(a, name, f"{k}.png")
save(far, "far", "0.png")
print("ok")
