"""Pixelzone (GGBotNet, CC0: `assets/source/pages/Pixelzone.ttf`) drawn at its own pixel size exactly as designed.

FreeType's hinting at 16 px moves some of its small parts: Й's and й's breve came out as two dots a row above their bar
(the user, 2026-11-22: "cannot spell Й properly. It adds two dots"), and ё was bent too. So each line is drawn eight
times larger, where hinting no longer moves anything, and read back at the middle of every pixel. (Й and й themselves are
mended in the font file: И and и with a 2 px line a row above, the user's choice; `assets/source/pages/README.md`.) The advances are the
font's own (`FONT.getlength` at 16 px), so layouts measured with it stay as they were.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont

PATH = Path(__file__).resolve().parent.parent / "assets" / "source" / "pages" / "Pixelzone.ttf"
SIZE, K = 16, 8
FONT = ImageFont.truetype(str(PATH), SIZE)
_BIG = ImageFont.truetype(str(PATH), SIZE * K)


def mask(s):
    """The line's pixels at 16 px as an "L" image (255 inked), as wide as its advance + 2 and 16 rows high."""
    w = int(FONT.getlength(s)) + 2
    big = Image.new("L", (w * K, SIZE * K), 0)
    d = ImageDraw.Draw(big)
    d.fontmode = "1"
    d.text((0, 0), s, font=_BIG, fill=255)
    return Image.fromarray(np.array(big)[K // 2::K, K // 2::K])


def text(im, xy, s, fill):
    """Draws the line `s` on the RGBA picture `im` with its top left at `xy` (as ImageDraw.text would), in `fill`."""
    m = mask(s)
    colour = Image.new("RGBA", m.size, fill if isinstance(fill, tuple) else ImageColor.getcolor(fill, "RGBA"))
    colour.putalpha(m)
    im.alpha_composite(colour, (round(xy[0]), round(xy[1])))

