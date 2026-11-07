"""Draws the ship's boats by hand (GAME_DESIGN.md §5.3, the outer shell), seen side-on as in the
user's side photo of the ship (2026-11-07), at their real size next to her (48 px a metre):

- the lifeboat: a red-orange canopy over a white hull, a row of small windows, the steering cupola
  aft, a release hook at each end where the davit's cable takes it; about 10 m long;
- the tender: an enclosed white boat with a grey roof and two rows of dark windows, the wheelhouse
  forward on top; about 9.8 m;
- the rescue boat: a small open orange boat with a grey console and an outboard; about 6 m.

Resurrect 64 colours only, a one-colour outline like the other pieces on board. Bow to the left.
Each is drawn in a 300 x 100 design and scaled to its size, so the shapes keep their proportions.

Writes assets/source/ship/lifeboats/<name>.png and the game's copies, assets/ship/<name>.png
(lifeboat.png, tender.png, rescue-boat.png), washed out a little toward the ship's white plating:
they are background, like every muted prop (the user, 2026-11-06). Run from the repo root:
    python tools/draw_lifeboat.py [--preview out.png]
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source" / "ship" / "lifeboats"
GAME = ROOT / "assets" / "ship"

PLATING, MUTE = (0xE8, 0xEA, 0xEC), 0.35     # what the boats fade toward, and how far (as the -bg props)
OUTLINE = "#2e222f"
HULL, HULL_SHADE, HULL_DARK = "#ffffff", "#c7dcd0", "#9babb2"
RUB = "#3e3546"
CANOPY, CANOPY_LIT, CANOPY_SHADE = "#e83b3b", "#ea4f36", "#ae2334"
ORANGE, ORANGE_LIT, ORANGE_SHADE = "#fb6b1d", "#f79617", "#cd683d"
GLASS, GLASS_LIT = "#323353", "#4d65b4"
STEEL, ROOF, ROOF_LIT = "#9babb2", "#7f708a", "#9babb2"

# Each boat's size in game px (length, height): its length after the user's photo.
# (A little smaller than life, 85%, so they hang clear of the promenade's walls: the user, 2026-11-07.)
SIZES = {"lifeboat": (408, 128), "tender": (400, 128), "rescue-boat": (252, 74)}
# Where each boat's two cables take it, from its left edge (as fractions of its length), and how far
# down its picture the hooks' eyes are: the game hangs it by these.
HOOKS = {"lifeboat": ((0.173, 0.893), 0.13), "tender": ((0.173, 0.893), 0.13), "rescue-boat": ((0.2, 0.8), 0.3)}


class Pen:
    """Draws in the 300 x 100 design's coordinates onto a boat of the given size."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.sx, self.sy = w / 300, h / 100
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def p(self, x, y):
        return (round(x * self.sx), round(y * self.sy))

    def poly(self, pts, fill):
        self.d.polygon([self.p(x, y) for x, y in pts], fill=fill)

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, radius=0):
        a, b = self.p(x0, y0), self.p(x1, y1)
        if radius:
            self.d.rounded_rectangle([a, b], radius=round(radius * min(self.sx, self.sy)), fill=fill, outline=outline)
        else:
            self.d.rectangle([a, b], fill=fill, outline=outline)

    def line(self, x0, y0, x1, y1, fill, width=1):
        self.d.line([self.p(x0, y0), self.p(x1, y1)], fill=fill, width=max(1, round(width * self.sy)))

    def shade_below(self, y_from, y_dark, keel):
        """Every hull pixel in the lowest rows in shade, following the curve."""
        px = self.im.load()
        for y in range(round(y_from * self.sy), min(self.h, round(keel * self.sy) + 1)):
            for x in range(self.w):
                if px[x, y][3]:
                    px[x, y] = rgba(HULL_DARK if y >= y_dark * self.sy else HULL_SHADE)

    def outline(self):
        a = self.im.split()[3]
        px, ap = self.im.load(), a.load()
        for y in range(self.h):
            for x in range(self.w):
                if ap[x, y]:
                    continue
                if any(0 <= x + dx < self.w and 0 <= y + dy < self.h and ap[x + dx, y + dy]
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    px[x, y] = rgba(OUTLINE)
        return self.im


def rgba(hexcolour):
    return tuple(int(hexcolour[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


HULL_SHAPE = [(10, 56), (290, 56), (296, 62), (296, 72), (290, 82), (276, 90), (254, 94),
              (48, 94), (26, 90), (12, 80), (5, 68), (5, 60)]


def hooks(pen, top_fore=20, top_aft=24):
    for x in (52, 268):
        top = top_fore if x < 200 else top_aft
        pen.rect(x - 1.5, top, x + 1.5, top + 8, fill=STEEL)
        pen.d.ellipse([pen.p(x - 4, top - 6), pen.p(x + 4, top + 2)], outline=STEEL, width=2)


def lifeboat():
    pen = Pen(*SIZES["lifeboat"])
    pen.poly(HULL_SHAPE, HULL)
    pen.shade_below(85, 92, 94)
    pen.line(8, 57, 292, 57, RUB, 3)
    pen.line(18, 74, 288, 74, HULL_SHADE, 2)
    # The canopy: a long low loaf, a little higher amidships.
    pen.rect(14, 28, 286, 56, fill=CANOPY, radius=20)
    pen.rect(40, 24, 230, 40, fill=CANOPY, radius=8)
    pen.line(48, 27, 222, 27, CANOPY_LIT, 2)
    pen.rect(18, 51, 282, 55, fill=CANOPY_SHADE)
    # The steering cupola aft, its windows all round.
    pen.rect(206, 8, 250, 32, fill=CANOPY, radius=8)
    pen.rect(210, 14, 246, 20, fill=GLASS)
    pen.line(212, 10, 244, 10, CANOPY_LIT)
    # Small windows along the canopy's side, and the boarding hatch amidships.
    for x in list(range(36, 116, 12)) + list(range(152, 200, 12)) + [262]:
        pen.rect(x, 40, x + 6, 45, fill=GLASS)
    pen.rect(122, 34, 144, 50, outline=CANOPY_SHADE, radius=3)
    hooks(pen)
    return pen.outline()


def tender():
    pen = Pen(*SIZES["tender"])
    pen.poly(HULL_SHAPE, HULL)
    pen.shade_below(85, 92, 94)
    pen.line(8, 57, 292, 57, RUB, 3)
    pen.line(18, 74, 288, 74, HULL_SHADE, 2)
    # Its enclosed cabin: white sides, a grey roof, two rows of windows; the wheelhouse forward.
    pen.rect(16, 26, 284, 56, fill=HULL, radius=6)
    pen.rect(16, 22, 284, 28, fill=ROOF, radius=4)
    pen.line(20, 23, 280, 23, ROOF_LIT, 1)
    for row in (32, 44):
        for x in range(26, 276, 14):
            pen.rect(x, row, x + 10, row + 7, fill=GLASS)
    pen.rect(40, 8, 96, 24, fill=HULL, radius=4)
    pen.rect(44, 12, 92, 18, fill=GLASS)
    pen.rect(40, 6, 96, 9, fill=ROOF, radius=2)
    # Its rails along the roof.
    pen.line(110, 16, 270, 16, STEEL, 1)
    for x in range(110, 272, 20):
        pen.line(x, 16, x, 22, STEEL, 1)
    hooks(pen, 4, 12)
    return pen.outline()


def rescue_boat():
    pen = Pen(*SIZES["rescue-boat"])
    # An open boat: an orange inflatable collar round a grey hull, a console amidships, an outboard.
    pen.poly([(8, 56), (282, 56), (290, 64), (286, 80), (60, 92), (24, 86), (8, 70)], STEEL)
    pen.rect(4, 44, 292, 66, fill=ORANGE, radius=18)
    pen.line(14, 48, 280, 48, ORANGE_LIT, 3)
    pen.line(14, 62, 284, 62, ORANGE_SHADE, 3)
    pen.rect(130, 14, 172, 44, fill=HULL, radius=4)
    pen.rect(134, 16, 168, 26, fill=GLASS)
    pen.rect(258, 18, 292, 56, fill=RUB, radius=4)
    pen.rect(270, 56, 280, 88, fill=RUB)
    for x in (60, 240):
        pen.rect(x - 1.5, 18, x + 1.5, 44, fill=STEEL)
    return pen.outline()


def washed(im):
    out = im.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (*(round(c + (t - c) * MUTE) for c, t in zip((r, g, b), PLATING)), a)
    return out


if __name__ == "__main__":
    SOURCE.mkdir(parents=True, exist_ok=True)
    boats = {"lifeboat": lifeboat(), "tender": tender(), "rescue-boat": rescue_boat()}
    for name, im in boats.items():
        im.save(SOURCE / f"{name}.png")
        washed(im).save(GAME / f"{name}.png")
        print(f"{name}: {im.size}")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        W = sum(im.width for im in boats.values()) + 80
        bg = Image.new("RGBA", (W, 200), "#e8eaec")
        x = 20
        for im in boats.values():
            bg.alpha_composite(washed(im), (x, 200 - 20 - im.height))
            x += im.width + 20
        bg.save(out)
