"""The Seven Seas' pass (deck 5 aft, near-catch 1; remade 2026-11-24, docs/near-catch-1-remake-log.md): its
pieces, from the generated pictures in assets/source/pass/gen/ (its README has the jobs) into assets/ship/pass/.

    python tools/build_pass.py

- `counter.png`: the serving counter (the user's choice of two, the walnut one), redrawn by PixelLab from a flat
  rough drawn in the game's own picture of the place, cut out by what differs from the place.
- `bowl-fall.png`: the fruit bowl's fall off the counter's forward end, a row of frames of the picture it was made
  in (96 x 64, the bowl standing at column 81, the floor's line at row 56), the bowl and its fruit cut out by what
  differs from the place. The clip's frame 0 is the game's own bowl standing, so it is not in the sheet; its last
  frame is what lies there afterwards.
- `plate.png`: the lunch Bumbot is at.
- `pass.json`: where each stands from the counter's forward end on the floor's line.

Nothing here is put on the palette: the counter is as the user approved it, and the bowl's frames are PixelLab's
from the game's own (palettized) bowl.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "pass" / "gen"
OUT = ROOT / "assets" / "ship" / "pass"

# The pictures the pieces were made in, in px from the counter's forward end (its left) on the floor's line:
# the counter's (160 x 64) has that point at (15, 52), the bowl's (96 x 64) at (63, 56).
COUNTER_AT = (15, 52)
FALL_AT = (63, 56)
COUNTER = "b"                       # the user's choice of the two tries
FALL = "a"                          # the fall's try used
FALL_FRAMES = [3, 4, 5, 6, 7, 8, 9, 12]     # (1 and 2 are smeared)
BOWL_X = 18                         # the bowl's middle from the counter's end, as it stands in the fall's start picture


def differs(a, b, more):
    return np.abs(a.astype(int) - b.astype(int)).sum(axis=2) > more


def counter():
    base = np.asarray(Image.open(SRC / "base-crop.png").convert("RGB"))
    t = np.asarray(Image.open(SRC / f"counter-{COUNTER}.png").convert("RGB"))
    m = differs(t, base, 40)
    m[:, :8] = False; m[:, 156:] = False; m[:12] = False; m[COUNTER_AT[1]:] = False     # the place's own edges and floor
    lab, n = ndi.label(m)
    keep = ndi.binary_fill_holes(lab == 1 + int(np.argmax(ndi.sum(m, lab, range(1, n + 1)))))
    ys, xs = np.nonzero(keep)
    out = np.zeros((*keep.shape, 4), np.uint8)
    out[..., :3] = t; out[..., 3] = keep * 255
    img = Image.fromarray(out).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    assert xs.min() == COUNTER_AT[0] and ys.max() + 1 == COUNTER_AT[1], (xs.min(), ys.max())
    return img, keep


def fall(counter_mask):
    bg = np.asarray(Image.open(SRC / "bowl-bg.png").convert("RGB"))
    # (Nothing of the bowl is ever in front of the counter: its pixels are the place's.)
    ox, oy = FALL_AT[0] - COUNTER_AT[0], FALL_AT[1] - COUNTER_AT[1]
    solid = np.zeros(bg.shape[:2], bool)
    h, w = counter_mask.shape
    for y in range(64):
        for x in range(96):
            cx, cy = x - ox, y - oy
            if 0 <= cx < w and 0 <= cy < h and counter_mask[cy, cx]:
                solid[y, x] = True
    frames = []
    for i in FALL_FRAMES:
        f = np.asarray(Image.open(SRC / f"fall-{FALL}" / f"{i:02d}.png").convert("RGB"))
        m = differs(f, bg, 60) & ~solid
        m[FALL_AT[1] + 1:] = False                  # under the floor's line the carpet is the place's
        lab, n = ndi.label(m, structure=np.ones((3, 3)))
        sizes = ndi.sum(m, lab, range(1, n + 1))
        keep = ndi.binary_fill_holes(np.isin(lab, [j + 1 for j, s in enumerate(sizes) if s >= 10]))
        out = np.zeros((64, 96, 4), np.uint8)
        out[..., :3] = f; out[..., 3] = keep * 255
        frames.append(Image.fromarray(out))
    sheet = Image.new("RGBA", (96 * len(frames), 64))
    for k, f in enumerate(frames):
        sheet.paste(f, (96 * k, 0))
    return sheet, len(frames)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c, mask = counter()
    c.save(OUT / "counter.png")
    sheet, n = fall(mask)
    sheet.save(OUT / "bowl-fall.png")
    p = Image.open(SRC / "plate.png").convert("RGBA")
    p = p.crop(p.getbbox())
    p.save(OUT / "plate.png")
    layout = {
        "counter": {"w": c.width, "h": c.height},
        # (A frame of the fall stands with its column `x` at the counter's end and its row `y` on the floor's line.)
        "fall": {"w": 96, "h": 64, "frames": n, "x": FALL_AT[0], "y": FALL_AT[1], "bowl": BOWL_X},
        "plate": {"w": p.width, "h": p.height},
    }
    (OUT / "pass.json").write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("counter", c.size, "| fall", n, "frames | plate", p.size)


if __name__ == "__main__":
    main()
