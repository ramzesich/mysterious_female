"""The reading nook's photo small on its wall (`thumb-slot_nook`): PixelLab's 20 x 26 redraw of the recoloured picture
(`assets/source/photos/nook/thumb2.png`), faded as an old print and its oranges and yellows (the lion, the cream ground)
taken mostly out (the user, 2026-11-22: "a bit more washed-out coloring", "the orange/yellow much less prominent"), in a
gold frame with a dark outline: `assets/ship/photos/thumb-slot_nook.png` (26 x 32).

    python tools/frame_nook_thumb.py
"""
import colorsys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "photos" / "nook"
WARM = 0.25          # how much of the oranges' and yellows' colour is left
FADE = 0.35          # how far every colour goes toward the print's paper
PAPER = (226, 222, 214)


def main():
    t = Image.open(SRC / "thumb2.png").convert("RGBA")
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
    f.save(ROOT / "assets" / "ship" / "photos" / "thumb-slot_nook.png")
    print("wrote thumb-slot_nook.png", f.size)


if __name__ == "__main__":
    main()
