"""Draws the lifeboat by hand (GAME_DESIGN.md §5.3, the outer shell, step 3): seen side-on, as in
the user's photo of the ship's side: a red-orange canopy over a white hull, a row of small windows,
the steering cupola aft, and a release hook at each end where the davit's cable takes it. Resurrect
64 colours only, a one-colour outline like the other pieces on board. Bow to the left.

Writes assets/source/ship/lifeboats/drawn.png and the game's copy, assets/ship/lifeboat.png. Run from the repo root:
    python tools/draw_lifeboat.py [--preview out.png]
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "source" / "ship" / "lifeboats" / "drawn.png"
GAME = ROOT / "assets" / "ship" / "lifeboat.png"

W, H = 300, 100
OUTLINE = "#2e222f"
HULL, HULL_SHADE, HULL_DARK = "#ffffff", "#c7dcd0", "#9babb2"
RUB = "#3e3546"
CANOPY, CANOPY_LIT, CANOPY_SHADE = "#e83b3b", "#ea4f36", "#ae2334"
GLASS, GLASS_LIT = "#323353", "#4d65b4"
STEEL = "#9babb2"

GUNWALE = 56          # where the canopy sits on the hull
KEEL = 94             # the hull's lowest row


def draw():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # The hull: a full, rounded bow on the left, a rounder stern on the right, a flat bottom.
    hull = [(10, GUNWALE), (290, GUNWALE), (296, 62), (296, 72), (290, 82), (276, 90), (254, KEEL),
            (48, KEEL), (26, 90), (12, 80), (5, 68), (5, 60)]
    d.polygon(hull, fill=HULL)
    # The underside in shade: every hull pixel in the lowest rows, following the curve.
    px = im.load()
    for y in range(KEEL - 9, KEEL + 1):
        for x in range(W):
            if px[x, y][3]:
                px[x, y] = Image.new("RGB", (1, 1), HULL_DARK if y >= KEEL - 2 else HULL_SHADE).getpixel((0, 0)) + (255,)
    # The rubbing strake along the gunwale, and a second one lower down.
    d.line([(8, GUNWALE + 1), (292, GUNWALE + 1)], fill=RUB, width=3)
    d.line([(18, GUNWALE + 18), (288, GUNWALE + 18)], fill=HULL_SHADE, width=2)

    # The canopy: a long low loaf, a little higher amidships.
    d.rounded_rectangle([14, 28, 286, GUNWALE], radius=20, fill=CANOPY)
    d.rounded_rectangle([40, 24, 230, 40], radius=8, fill=CANOPY)
    d.line([(48, 27), (222, 27)], fill=CANOPY_LIT, width=2)
    d.line([(26, 33), (40, 33)], fill=CANOPY_LIT, width=2)
    d.rectangle([18, GUNWALE - 5, 282, GUNWALE - 1], fill=CANOPY_SHADE)
    # The steering cupola aft, its windows all round.
    d.rounded_rectangle([206, 8, 250, 32], radius=8, fill=CANOPY)
    d.rectangle([210, 14, 246, 20], fill=GLASS)
    d.line([(212, 15), (220, 15)], fill=GLASS_LIT)
    d.line([(212, 10), (244, 10)], fill=CANOPY_LIT)
    # Small windows along the canopy's side, and the boarding hatch amidships.
    for x in list(range(36, 116, 16)) + list(range(152, 200, 16)) + [262]:
        d.rectangle([x, 40, x + 7, 45], fill=GLASS)
        d.line([(x + 1, 41), (x + 3, 41)], fill=GLASS_LIT)
    d.rounded_rectangle([122, 34, 144, GUNWALE - 6], radius=3, outline=CANOPY_SHADE)
    d.line([(124, 45), (128, 45)], fill=CANOPY_SHADE)
    # The release hooks at each end, where the davit's cables take the boat.
    for x in (52, 268):
        top = 20 if x < 200 else 24
        d.rectangle([x - 2, top, x + 2, top + 8], fill=STEEL)
        d.ellipse([x - 4, top - 6, x + 4, top + 2], outline=STEEL, width=2)

    # A one-colour outline round the whole silhouette.
    a = im.split()[3]
    px, ap = im.load(), a.load()
    for y in range(H):
        for x in range(W):
            if ap[x, y]:
                continue
            if any(0 <= x + dx < W and 0 <= y + dy < H and ap[x + dx, y + dy]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = Image.new("RGB", (1, 1), OUTLINE).getpixel((0, 0)) + (255,)
    return im


if __name__ == "__main__":
    im = draw()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT)
    im.save(GAME)
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        bg = Image.new("RGBA", (W + 20, H + 20), "#e8eaec")
        bg.alpha_composite(im, (10, 10))
        bg.resize((bg.width * 3, bg.height * 3), Image.NEAREST).save(out)
    print(OUT.relative_to(ROOT), im.size)
