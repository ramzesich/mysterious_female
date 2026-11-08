"""Draws cabin 8206 by hand (GAME_DESIGN.md §5.3, deck 8): the user's own cabin on the cruise, an
oceanview on the starboard side, seen as in her photo (`guest_cabin_inside_with_portrait_window`):
from the door toward the picture window, the bow on the left, as the game sees the ship. A mirrored
wardrobe and the door back out, the wood desk unit with its shelves, the TV and a pouf, the window
in a wood surround with grey curtains, the grey sofa with teal cushions, the blue lobster drawing,
and the bed along the far wall, its head to the right, a teal runner across its foot.

Also the open door seen from the corridor: the cabin door's frame, its leaf swung in, the room
beyond it.

Writes assets/source/ship/cabin/interior.png and door-open.png and the game's copies,
assets/ship/cabin-8206.png and assets/ship/cabin-door-open.png. Run from the repo root:
    python tools/draw_cabin.py [--preview out.png]
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source" / "ship" / "cabin"
GAME = ROOT / "assets" / "ship"
W, H = 240, 144          # 5 m of cabin; its wall up to the ceiling (128 px) and the floor's slab
FLOOR = 128              # her feet: the top of the slab

INK = "#2e222f"
WALL, WALL_SEAM, WALL_SHADE = "#ece3cf", "#ddd2bb", "#d8cdb8"
CEILING = "#f6f3ec"
WOOD, WOOD_DARK, WOOD_LIGHT = "#cd683d", "#9e4539", "#e6904e"
CARPET, CARPET_FLECK, CARPET_DARK = "#9babb2", "#7f708a", "#8e98a3"
WHITE, PALE, GREY, SLATE = "#ffffff", "#c7dcd0", "#9babb2", "#625565"
TEAL, TEAL_LIGHT = "#0b5e65", "#0b8a8f"
SKY, SEA, SEA_DARK, SHORE = "#8fd3ff", "#4d65b4", "#484a77", "#547e64"


BED_TOP = 96               # the mattress's top, where she stands on the bed (ShipScene's CABIN.bed)
WASH = 0.3                 # how far the background fades toward the wall
PAINTING = SOURCE / "lobster-pixellab.png"


def wash(im, y0, y1):
    """Fades a band of the picture toward the wall colour."""
    px = im.load()
    w = tuple(int(WALL[i:i + 2], 16) for i in (1, 3, 5))
    for y in range(y0, y1):
        for x in range(im.width):
            c = px[x, y]
            px[x, y] = (*(round(v + (t - v) * WASH) for v, t in zip(c[:3], w)), c[3])


def painting():
    """The painting from PixelLab as it came (the user preferred it to a version remapped to blues),
    only the bits of the photo's frame it caught at the edges whitened."""
    art = Image.open(PAINTING).convert("RGBA")
    px = art.load()
    for y in range(art.height):
        for x in range(art.width):
            r_, g, b, a = px[x, y]
            if r_ > b + 12 or a < 128:
                px[x, y] = (0xf4, 0xf4, 0xf0, 255)
    return art


def interior():
    im = Image.new("RGBA", (W, H), WALL)
    d = ImageDraw.Draw(im)
    r = lambda x0, y0, x1, y1, c: d.rectangle([x0, y0, x1, y1], fill=c)

    # The ceiling with a wood cornice, three downlights; the wall's panel seams; the skirting.
    r(0, 0, W - 1, 5, CEILING)
    r(0, 6, W - 1, 7, WOOD)
    r(0, 8, W - 1, 8, WOOD_DARK)
    for x in (58, 122, 196):
        r(x - 3, 5, x + 3, 5, "#fbff86")
    for x in range(0, W, 48):
        r(x, 9, x, FLOOR - 5, WALL_SEAM)
    r(0, FLOOR - 4, W - 1, FLOOR - 1, GREY)
    r(0, FLOOR - 4, W - 1, FLOOR - 4, SLATE)
    # The floor: grey carpet, flecked, over the deck's slab.
    r(0, FLOOR, W - 1, FLOOR + 3, CARPET)
    for x in range(1, W, 5):
        d.point((x, FLOOR + 1 + (x * 7) % 3), fill=CARPET_FLECK)
    r(0, FLOOR + 4, W - 1, H - 2, CARPET_DARK)
    r(0, H - 1, W - 1, H - 1, "#6f7882")

    # A mirrored wardrobe by the door.
    r(6, 30, 40, FLOOR - 5, WOOD_DARK)
    r(8, 32, 38, FLOOR - 5, WOOD)
    for x0 in (10, 24):
        r(x0, 34, x0 + 12, FLOOR - 8, PALE)
        for i in range(0, 60, 14):
            d.line([(x0 + 1, 60 + i), (x0 + 8, 52 + i)], fill=WHITE)
        r(x0 + 12 if x0 == 10 else x0, 34, x0 + 12 if x0 == 10 else x0, FLOOR - 8, GREY)
    r(22, 70, 23, 76, GREY)

    # The door back out to the corridor (its inside face): wood, a lever, the escape plan, and the
    # "do not disturb" card on the handle.
    # It stands on the skirting's line, like the wardrobe and the desk (the user, 2026-11-06).
    x0, top = 45, FLOOR - 80
    r(x0, top, x0 + 28, FLOOR - 5, WOOD_DARK)
    r(x0 + 2, top + 2, x0 + 26, FLOOR - 5, WOOD)
    r(x0 + 3, top + 3, x0 + 3, FLOOR - 6, WOOD_LIGHT)
    r(x0 + 8, top + 12, x0 + 20, top + 28, WHITE)                # the escape plan
    r(x0 + 9, top + 14, x0 + 19, top + 14, "#1ebc73")
    d.line([(x0 + 10, top + 18), (x0 + 18, top + 24)], fill="#1ebc73")
    r(x0 + 10, top + 20, x0 + 13, top + 22, GREY)
    r(x0 + 21, top + 40, x0 + 25, top + 41, GREY)                # the lever
    r(x0 + 21, top + 42, x0 + 24, top + 50, "#ae2334")           # the card
    r(x0 + 22, top + 44, x0 + 23, top + 44, WHITE)

    # The desk unit: a tall wood column of glass shelves, the desk, the TV on its arm, a pouf.
    r(80, 20, 92, FLOOR - 5, WOOD_DARK)
    r(81, 21, 91, FLOOR - 5, WOOD)
    for y in (34, 48, 62):
        r(82, y, 90, y, PALE)
        r(82, y + 1, 90, y + 1, WOOD_DARK)
    r(84, 30, 86, 33, WHITE)                                      # a glass, a box of tissues
    r(87, 58, 90, 61, PALE)
    r(92, 22, 128, 24, WOOD_DARK)                                 # the shelf over the desk
    r(92, 88, 128, 92, WOOD_DARK)                                 # the desk top
    r(92, 88, 128, 88, WOOD_LIGHT)
    r(94, 93, 126, FLOOR - 5, WOOD)
    r(94, 104, 126, 104, WOOD_DARK)
    r(108, 97, 112, 98, WOOD_LIGHT)
    r(96, 84, 104, 87, INK)                                       # the phone
    r(97, 83, 99, 83, INK)
    r(106, 85, 109, 87, WHITE)                                    # the daily programme; two tangerines
                                                                  # sit beside it (ShipScene's CABIN.desk)
    r(93, 56, 95, 60, INK)                                        # the TV's arm, its screen
    r(96, 44, 124, 64, INK)
    r(98, 46, 122, 62, "#3e3546")
    d.line([(99, 47), (106, 47)], fill=SLATE)
    r(106, 106, 118, FLOOR - 5, WHITE)                            # the pouf: white, a teal band
    r(105, 104, 119, 107, TEAL)
    r(106, 104, 118, 104, TEAL_LIGHT)

    # The picture window in a wood surround, grey curtains. Its glass is left clear: the game shows
    # the live sea and sky behind it (WINDOW in ShipScene.js's CABIN; §5.2, 2026-11-08).
    r(136, 30, 184, 80, WOOD_DARK)
    r(138, 32, 182, 78, WOOD)
    d.rounded_rectangle([141, 35, 179, 75], radius=4, fill=WHITE)
    d.rounded_rectangle([143, 37, 177, 73], radius=3, fill=(0, 0, 0, 0))
    r(159, 36, 161, 74, PALE)                                     # the window's middle bar
    r(130, 26, 190, 27, GREY)                                     # the curtain rail
    for x0, x1 in ((129, 141), (179, 191)):                       # the curtains, folded
        r(x0, 28, x1, 86, SLATE)
        for x in range(x0 + 2, x1, 3):
            r(x, 28, x, 86, "#7f708a" if (x - x0) % 6 else "#3e3546")
        r(x0, 86, x1, 86, "#3e3546")

    # The painting over the sofa: the one in her photo, a feathery blue sea creature on white,
    # converted by PixelLab (image_to_pixelart, faithful; 1 generation), in a thin silver frame.
    r(197, 32, 228, 73, GREY)
    r(198, 33, 227, 72, WHITE)
    im.alpha_composite(painting(), (199, 33))

    # The sofa along the wall under the window, mostly behind the bed: its back and cushions.
    d.rounded_rectangle([144, 84, 210, 104], radius=3, fill="#576573")
    r(146, 86, 208, 87, "#6f7f8c")
    r(144, 94, 148, 104, "#4a5562")
    r(206, 94, 210, 104, "#4a5562")
    for x0 in (152, 174, 190):
        d.rounded_rectangle([x0, 86, x0 + 12, 98], radius=2, fill=TEAL)
        r(x0 + 2, 88, x0 + 6, 88, TEAL_LIGHT)

    r(236, 72, 239, FLOOR - 1, WOOD_DARK)                         # the bed's headboard panel

    # All of that is background, washed out a little toward the wall (the user, 2026-11-06); the
    # bed, drawn next, keeps its colours. The floor she stands on stays as it is.
    wash(im, 0, FLOOR)
    bed = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(bed)

    # The bed, its head against the right wall: white sheets falling to the floor, pillows, and the
    # teal runner across its foot, patterned in grey. She can jump onto it (BED_TOP).
    d.rounded_rectangle([138, BED_TOP, 236, FLOOR - 1], radius=3, fill=WHITE)
    r(140, 104, 236, 104, PALE)
    r(140, 112, 236, FLOOR - 1, "#e8eff0")
    r(140, FLOOR - 2, 236, FLOOR - 1, PALE)
    d.rounded_rectangle([212, 86, 236, 99], radius=4, fill=WHITE)  # pillows
    d.rounded_rectangle([200, 90, 222, 100], radius=4, fill="#f2f6f6")
    r(203, 98, 220, 98, PALE)
    r(154, 95, 176, FLOOR - 4, TEAL)                              # the runner
    r(154, 95, 176, 96, TEAL_LIGHT)
    for y in range(100, FLOOR - 6, 6):
        d.line([(156, y + 4), (165, y), (174, y + 4)], fill=GREY)
    r(154, FLOOR - 4, 176, FLOOR - 4, "#094a50")

    im.alpha_composite(bed)

    # The cabin shows where the corridor was, the deck around it dimmed by the game (the user,
    # 2026-11-06, as the linen room): the ceiling's shadow as along the corridor, and its two side
    # walls, plain.
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for i in range(8):
        a = int(0.45 * 255 * (1 - i / 8) ** 1.6)
        sd.rectangle([0, i * 2, W - 1, i * 2 + 1], fill=(0x2e, 0x22, 0x2f, a))
    im = Image.alpha_composite(im, shade)
    d = ImageDraw.Draw(im)
    for x0, x1 in ((0, 3), (W - 4, W - 1)):
        d.rectangle([x0, 0, x1, H - 1], fill=WALL_SHADE)
        d.rectangle([x0 + 1, 0, x1 - 1, H - 1], fill=WALL_SEAM)
    return im


def open_door():
    """The cabin door, propped open, from the corridor: its frame from the atlas's cabin door, the
    leaf swung in against the left, the cabin beyond: the wall, the window's light, the bed."""
    atlas = Image.open(GAME / "ship.png").convert("RGBA")
    door = atlas.crop((0, 0, 34, 74))                              # door-cabin (see build_ship_art)
    px = door.load()
    # The leaf: the door's own wood inside the frame.
    leaf = [(x, y) for y in range(74) for x in range(34) if px[x, y][:3] == (0xcd, 0x68, 0x3d)]
    x0 = min(x for x, _ in leaf); x1 = max(x for x, _ in leaf)
    y0 = min(y for _, y in leaf)
    d = ImageDraw.Draw(door)
    r = lambda a, b, c, e, col: d.rectangle([a, b, c, e], fill=col)
    r(x0, y0, x1, 73, WALL)
    r(x0, y0, x1, y0 + 2, CEILING)
    r(x0 + 9, y0 + 12, x1, y0 + 34, WOOD)                         # the window, at the far wall
    r(x0 + 11, y0 + 14, x1, y0 + 24, SKY)
    r(x0 + 11, y0 + 25, x1, y0 + 32, SEA)
    r(x0 + 7, y0 + 10, x0 + 10, y0 + 40, SLATE)                   # a curtain
    r(x0 + 6, y0 + 50, x1, 73, WHITE)                             # the foot of the bed
    r(x0 + 12, y0 + 50, x0 + 17, 73, TEAL)
    r(x0, 71, x1, 73, CARPET)
    # The leaf, swung in: a narrow strip at the hinge, seen edge-on, darker toward the room.
    for y in range(y0, 74):
        r(x0, y, x0 + 4, y, WOOD_DARK)
        r(x0 + 1, y, x0 + 2, y, WOOD)
    # The light falling out of the room onto the frame's inner edge.
    r(x1, y0, x1, 73, "#fbff86")
    return door


if __name__ == "__main__":
    SOURCE.mkdir(parents=True, exist_ok=True)
    room, door = interior(), open_door()
    room.save(SOURCE / "interior.png")
    door.save(SOURCE / "door-open.png")
    room.save(GAME / "cabin-8206.png")
    door.save(GAME / "cabin-door-open.png")
    if "--preview" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--preview") + 1])
        sheet = Image.new("RGBA", (W + 50, H), "#2e222f")
        sheet.paste(room, (0, 0))
        sheet.paste(door, (W + 8, H - 74))
        sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(out)
    print("wrote", (GAME / "cabin-8206.png").relative_to(ROOT), (GAME / "cabin-door-open.png").relative_to(ROOT))
