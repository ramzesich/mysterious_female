"""The theatre's popcorn (part 11's item 12, the user, 2026-11-27): the man with the tub (`amb_audience_3`, `aud_popcorn`)
tips it and the popcorn lies on the aisle's floor in front of him (the chips' slip, scenario 1).

From `assets/source/people/aud_popcorn-raw/tip/cut/` (its `cut.py`: the approved PixMiniMax clip, the game's seat split
round him):
- his clip `tip` into `assets/source/people/aud_popcorn/tip/<k>.png`: each frame's 80 px cell (the start's canvas
  from (4, 8)), him and the kernels in the air, in play order (`ORDER`); the people build washes it as it washes him.
  Run `tools/build_people.py` after.
- the kernels lying on the floor, frame by frame, as one strip `assets/ship/popcorn.png` (frames `BOX`'s size, on the
  palette, unwashed: what she slips on is in full colour), with `assets/ship/popcorn.json`: each strip frame's clip
  frame, and where the box stands from his middle and the floor.
"""
import json
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palettize import palettize

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
CUT = R + "assets/source/people/aud_popcorn-raw/tip/cut/"
CLIP = R + "assets/source/people/aud_popcorn/tip/"
OUT = R + "assets/ship/"
# His cell on the clip's canvas, and his middle and floor there.
CELL = (4, 8, 84, 88)
MID, FLOOR = 44, 88
# The clip's frames in play order (13 and 14 left out: `cut.py`).
ORDER = list(range(3, 13)) + [15, 16]
# The lying kernels' box on the canvas (every frame's fit in it).
BOX = (48, 80, 128, 88)


def main():
    os.makedirs(CLIP, exist_ok=True)
    for old in os.listdir(CLIP):
        os.remove(CLIP + old)
    strip, frames = [], []
    for k, i in enumerate(ORDER):
        Image.open(CUT + f"{i}.png").convert("RGBA").crop(CELL).save(CLIP + f"{k}.png")
        lying = Image.open(CUT + f"floor-{i}.png").convert("RGBA")
        bb = lying.getbbox()
        if bb:
            assert bb[0] >= BOX[0] and bb[1] >= BOX[1] and bb[2] <= BOX[2] and bb[3] <= BOX[3], (i, bb)
            strip.append(palettize(lying.crop(BOX)))
            frames.append(k)
    w, h = BOX[2] - BOX[0], BOX[3] - BOX[1]
    sheet = Image.new("RGBA", (w * len(strip), h))
    for n, im in enumerate(strip):
        sheet.alpha_composite(im, (n * w, 0))
    sheet.save(OUT + "popcorn.png")
    # Its first kernel and its last from his middle (the slip's span), from the last frame.
    last = Image.open(CUT + f"floor-{ORDER[-1]}.png").getbbox()
    meta = {"w": w, "h": h, "frames": frames, "clip": len(ORDER),
            "dx": BOX[0] - MID, "dy": FLOOR - BOX[3], "span": [last[0] - MID, last[2] - MID]}
    with open(OUT + "popcorn.json", "w") as f:
        json.dump(meta, f)
    print("tip", len(ORDER), "frames; lying", len(strip), meta)


if __name__ == "__main__":
    main()
