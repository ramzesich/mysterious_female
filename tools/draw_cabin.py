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
    x0, top = 45, FLOOR - 76
    r(x0, top, x0 + 28, FLOOR - 1, WOOD_DARK)
    r(x0 + 2, top + 2, x0 + 26, FLOOR - 1, WOOD)
    r(x0 + 3, top + 3, x0 + 3, FLOOR - 2, WOOD_LIGHT)
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
    r(110, 85, 122, 87, WHITE)                                    # papers, the daily programme
    r(93, 56, 95, 60, INK)                                        # the TV's arm, its screen
    r(96, 44, 124, 64, INK)
    r(98, 46, 122, 62, "#3e3546")
    d.line([(99, 47), (106, 47)], fill=SLATE)
    r(106, 106, 118, FLOOR - 5, WHITE)                            # the pouf: white, a teal band
    r(105, 104, 119, 107, TEAL)
    r(106, 104, 118, 104, TEAL_LIGHT)

    # The picture window in a wood surround: the sky, a far shore, the sea; grey curtains.
    r(136, 30, 184, 80, WOOD_DARK)
    r(138, 32, 182, 78, WOOD)
    d.rounded_rectangle([141, 35, 179, 75], radius=4, fill=WHITE)
    d.rounded_rectangle([143, 37, 177, 73], radius=3, fill=SKY)
    r(143, 37, 177, 46, "#c7f0ff")
    r(144, 55, 176, 56, SHORE)
    r(150, 54, 160, 54, SHORE)
    d.rounded_rectangle([143, 57, 177, 73], radius=3, fill=SEA)
    r(143, 57, 177, 57, "#8fd3ff")
    for y in (61, 66, 70):
        r(146 + y % 5, y, 156 + y % 5, y, SEA_DARK)
    r(159, 36, 161, 74, PALE)                                     # the window's middle bar
    r(130, 26, 190, 27, GREY)                                     # the curtain rail
    for x0, x1 in ((129, 141), (179, 191)):                       # the curtains, folded
        r(x0, 28, x1, 86, SLATE)
        for x in range(x0 + 2, x1, 3):
            r(x, 28, x, 86, "#7f708a" if (x - x0) % 6 else "#3e3546")
        r(x0, 86, x1, 86, "#3e3546")

    # The lobster drawing: blue lines on white in a white frame.
    r(196, 34, 230, 68, PALE)
    r(197, 35, 229, 67, WHITE)
    lob, lob2 = SEA, "#4d9be6"
    for i, (x, y) in enumerate(((203, 62), (206, 59), (209, 56), (212, 53))):   # the tail's segments
        d.ellipse([x - 2, y - 2, x + 2, y + 2], outline=lob, fill=WHITE if i else "#dbe9f2")
    d.polygon([(199, 66), (203, 61), (204, 66)], outline=lob)                   # the tail fan
    d.ellipse([212, 44, 221, 52], outline=lob)                                  # the shell
    d.line([(214, 48), (219, 46)], fill=lob2)
    d.line([(219, 45), (216, 40)], fill=lob)                                    # the claws
    d.ellipse([212, 36, 218, 41], outline=lob)
    d.line([(221, 48), (224, 46)], fill=lob)
    d.ellipse([223, 42, 228, 48], outline=lob)
    d.line([(221, 45), (227, 37)], fill=lob2)                                   # the feelers
    d.line([(220, 44), (223, 36)], fill=lob2)
    for i in range(3):                                                          # the legs
        d.line([(212 + i * 3, 51), (210 + i * 3, 55)], fill=lob2)

    # The sofa along the wall under the window, mostly behind the bed: its back and cushions.
    d.rounded_rectangle([144, 84, 210, 104], radius=3, fill="#576573")
    r(146, 86, 208, 87, "#6f7f8c")
    r(144, 94, 148, 104, "#4a5562")
    r(206, 94, 210, 104, "#4a5562")
    for x0 in (152, 174, 190):
        d.rounded_rectangle([x0, 86, x0 + 12, 98], radius=2, fill=TEAL)
        r(x0 + 2, 88, x0 + 6, 88, TEAL_LIGHT)

    # The bed, its head against the right wall: white sheets falling to the floor, pillows, and the
    # teal runner across its foot, patterned in grey.
    r(236, 72, 239, FLOOR - 1, WOOD_DARK)                         # the headboard panel
    d.rounded_rectangle([138, 96, 236, FLOOR - 1], radius=3, fill=WHITE)
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

    # The cut through the ship's side, its edges in shadow (as at every deck's cut, §5.3).
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for i in range(10):
        a = int(0.6 * 255 * (1 - i / 10) ** 1.6)
        sd.rectangle([0, i * 2, W - 1, i * 2 + 1], fill=(0x2e, 0x22, 0x2f, a))
    for i in range(9):
        a = int(0.6 * 255 * (1 - i / 9) ** 1.6)
        sd.rectangle([i * 2, 0, i * 2 + 1, FLOOR - 1], fill=(0x2e, 0x22, 0x2f, a))
        sd.rectangle([W - 2 - i * 2, 0, W - 1 - i * 2, FLOOR - 1], fill=(0x2e, 0x22, 0x2f, a))
    return Image.alpha_composite(im, shade)


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
