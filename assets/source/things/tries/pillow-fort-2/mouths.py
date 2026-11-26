"""Splash Academy's fort with a tunnel mouth in profile at each end, as the linen room's shaft mouth is drawn (the user,
2026-11-26: "The openings should be in profile. Look how the shaft in the linen room is implemented. We can place
something similar here, behind the stack of pillows, on both sides"). From each stack outward: the tunnel's near side,
the blanket's fabric; its hemmed rim; the inside's dark slot seen past it; a thin far rim. The near side and rim are in
front of her (`pillow-fort.png`), the slot and the far rim behind her (`pillow-fort-back.png`), so that at a mouth on hands
and knees she is in it.

    python mouths.py rough            the flat rough on the approved fort (rough-mouths.png)
    python mouths.py split <redraw>   the redraw cut into the two pictures, by the rough's own geometry
"""
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
OUT = HERE.parent.parent
PAD = 14                                   # px added at each end
W, H = 176 + 2 * PAD, 64
TOP = 28                                   # the mouth's top row (the blanket over it)
STRIPES = [(36, 159, 222), (246, 240, 240), (233, 104, 168), (246, 240, 240)]
HEM = (176, 70, 120)
DARK = (50, 44, 60)
OUTL = (46, 34, 47)
# Columns, from the outer edge in: far rim, slot, near rim (hem), near side (fabric) up to the stack.
FAR, SLOT, RIM = (1, 2), (2, 6), (6, 8)
EDGE = 6                                   # the redraw's slots lie within this many columns of each end


def cols(side, a, b):
    return range(a, b) if side == 0 else range(W - b, W - a)


def rough():
    fort = Image.open(HERE / "redraw-s23.png").convert("RGBA")
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for side in (0, 1):
        for x in cols(side, RIM[1], PAD + 6):         # the near side: the blanket's fabric, striped on the slant
            for y in range(TOP, H):
                k = ((x if side == 0 else W - 1 - x) + y) // 4
                im.putpixel((x, y), STRIPES[k % 4] + (255,))
        for x in cols(side, *RIM):
            for y in range(TOP, H):
                im.putpixel((x, y), HEM + (255,))
        for x in cols(side, *SLOT):
            for y in range(TOP + 2, H):
                im.putpixel((x, y), DARK + (255,))
        for x in cols(side, *FAR):
            for y in range(TOP + 2, H):
                im.putpixel((x, y), STRIPES[2] + (255,))
        for y in range(TOP, H):                          # the near side's top edge, a fold under the roof
            pass
    im.alpha_composite(fort, (PAD, 0))
    for side in (0, 1):                                  # outlines round the mouth
        for y in range(TOP, H):
            x = 0 if side == 0 else W - 1
            im.putpixel((x, y), OUTL + (255,))
        for x in cols(side, 0, PAD + 6):
            if not fort_px(fort, x - PAD, TOP - 1):
                im.putpixel((x, TOP - 1), OUTL + (255,))
    im.save(HERE / "rough-mouths.png")
    return im


def fort_px(fort, x, y):
    return 0 <= x < fort.width and 0 <= y < fort.height and fort.getpixel((x, y))[3] > 0


def split(path):
    """The redraw's slots sit at the very outer columns (it moved them from the rough's): the dark pixels within `EDGE`
    columns of each end, from the mouth's top down, go behind her; the rest stays in front."""
    red = Image.open(path).convert("RGBA")
    front, back = red.copy(), Image.new("RGBA", red.size, (0, 0, 0, 0))
    lum = lambda p: 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]
    for side in (0, 1):
        for x in cols(side, 0, EDGE):
            for y in range(TOP + 2, H):
                p = red.getpixel((x, y))
                if p[3] and lum(p) < 75:
                    back.putpixel((x, y), p)
                    front.putpixel((x, y), (0, 0, 0, 0))
    front.save(OUT / "pillow-fort.png")
    back.save(OUT / "pillow-fort-back.png")
    print("front and back", red.size)


if __name__ == "__main__":
    rough() if sys.argv[1] == "rough" else split(sys.argv[2])
