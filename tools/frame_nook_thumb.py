"""A photo slot's picture small on its wall (`thumb-slot_<name>`): PixelLab's 20 x 26 redraw of its picture, in a gold
frame with a dark outline: `assets/ship/photos/thumb-slot_<name>.png` (26 x 32).

- `nook`: the reading nook's (`assets/source/photos/nook/thumb2.png`), faded as an old print and its oranges and yellows
  (the lion, the cream ground) taken mostly out (the user, 2026-11-22: "a bit more washed-out coloring", "the
  orange/yellow much less prominent").
- `cucina`: the two of them at La Cucina's window table (`assets/source/photos/cucina/thumb.png`, from try 4, the user's
  choice, 2026-11-23), as it came.
- `lifeboat`: "I ❤ BAT YAM" on its beach promenade (`assets/source/photos/lifeboat/thumb.png`, from try 1, the user's
  choice, 2026-11-25), as it came.

    python tools/frame_nook_thumb.py [nook|cucina|lifeboat ...]      (all of them by default)
"""
import colorsys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PAPER = (226, 222, 214)
# name: (its small redraw, how much of the oranges' and yellows' colour is left, how far every colour goes toward the
# print's paper)
SLOTS = {"nook": ("thumb2.png", 0.25, 0.35), "cucina": ("thumb.png", 1.0, 0.0), "lifeboat": ("thumb.png", 1.0, 0.0)}


def frame(name):
    src, WARM, FADE = SLOTS[name]
    SRC = ROOT / "assets" / "source" / "photos" / name
    t = Image.open(SRC / src).convert("RGBA")
    px = t.load()
    for y in range(t.height):
        for x in range(t.width):
            r, g, b, a = px[x, y]
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if 0.02 <= h <= 0.2:                       # orange to yellow
                s *= WARM
            r, g, b = (round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))
            r, g, b = (round(v + (p - v) * FADE) for v, p in zip((r, g, b), PAPER))
            px[x, y] = (r, g, b, a)
    W, H = t.width + 6, t.height + 6
    f = Image.new("RGBA", (W, H), (0x2e, 0x22, 0x2f, 255))
    f.paste((0xd9, 0xa4, 0x3b, 255), (1, 1, W - 1, H - 1))
    f.paste((0xf0, 0xc8, 0x60, 255), (1, 1, W - 1, 2))
    f.alpha_composite(t, (3, 3))
    f.save(SRC / "framed.png")
    f.save(ROOT / "assets" / "ship" / "photos" / f"thumb-slot_{name}.png")
    print(f"wrote thumb-slot_{name}.png", f.size)


if __name__ == "__main__":
    import sys
    for name in sys.argv[1:] or SLOTS:
        frame(name)
