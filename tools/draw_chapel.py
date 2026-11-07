"""Draws the Chapel on deck 12 by hand (GAME_DESIGN.md §5.3), from the user's photo: off the forward
lobby, behind its door. Inside, it shows in the deck's place, the deck around it dimmed, as the linen
room does. Cream wallpaper under a light wood ceiling with downlights, a red carpet with a cream
lattice, cane-back chairs in rows facing the round altar table, white flowers on tall stands either
side of it and a painting over it, the amber glass doors back out to the lobby.

Also the open door seen from the lobby: a wood frame, an amber glass leaf swung in, the red carpet
and the cream wall beyond.

Writes assets/source/ship/chapel/interior.png and door-open.png and the game's copies,
assets/ship/chapel-room.png and assets/ship/chapel-door-open.png. Run from the repo root, after
tools/build_ship_art.py (the chairs and flowers come from the atlas):
    python tools/draw_chapel.py [--preview out.png]
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source" / "ship" / "chapel"
GAME = ROOT / "assets" / "ship"
W, H = 312, 144          # 6.5 m of room (wider, the user: it looked cramped); its wall up to the
                         # ceiling (128 px) and the floor's slab
FLOOR = 128              # her feet: the top of the slab

INK = "#2e222f"
WALL, WALL_DOT, WALL_SHADE = "#efe6d2", "#e4d8bf", "#d8caae"
WOOD, WOOD_DARK, WOOD_LIGHT = "#c28d5a", "#9e6a3f", "#dcae78"
CARPET, CARPET_DARK, CARPET_LINE = "#ae2334", "#7a3045", "#f2d6b0"
AMBER, AMBER_LIGHT, AMBER_DARK = "#f79617", "#fbb954", "#cd683d"
CREAM, STONE, STONE_DARK = "#f4ead8", "#e6d6b8", "#c8b38e"
WHITE, GREY, SLATE, SLAB = "#ffffff", "#9babb2", "#625565", "#8e98a3"
LIGHT = "#fbff86"

# Where things are, from the room's left edge (ShipScene's CHAPEL must agree): the door back out.
DOOR_X = 59
WASH = 0.18              # how far the background fades toward the wall


def piece(name):
    """A piece of the ship's atlas, as an image."""
    atlas = Image.open(GAME / "ship.png").convert("RGBA")
    f = json.loads((GAME / "ship.json").read_text(encoding="utf-8"))["frames"][name]["frame"]
    return atlas.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


def wash(im, y0, y1):
    """Fades a band of the picture toward the wall colour."""
    px = im.load()
    w = tuple(int(WALL[i:i + 2], 16) for i in (1, 3, 5))
    for y in range(y0, y1):
        for x in range(im.width):
            c = px[x, y]
            px[x, y] = (*(round(v + (t - v) * WASH) for v, t in zip(c[:3], w)), c[3])


def glass_door(d, x0, top, bottom):
    """An amber glass door in a wood frame, seen face on: small panes in a wood grid."""
    r = lambda a, b, c, e, col: d.rectangle([a, b, c, e], fill=col)
    r(x0, top, x0 + 28, bottom, WOOD_DARK)
    r(x0 + 3, top + 3, x0 + 25, bottom - 3, AMBER)
    for y in range(top + 3, bottom - 3, 9):
        r(x0 + 3, y, x0 + 25, y, WOOD)
    r(x0 + 14, top + 3, x0 + 14, bottom - 3, WOOD)
    for y in range(top + 5, bottom - 6, 9):
        r(x0 + 5, y, x0 + 6, y + 2, AMBER_LIGHT)
        r(x0 + 16, y, x0 + 17, y + 2, AMBER_LIGHT)
    r(x0 + 20, top + 40, x0 + 24, top + 41, "#f9c22b")              # the brass handle


def interior():
    im = Image.new("RGBA", (W, H), WALL)
    d = ImageDraw.Draw(im)
    r = lambda x0, y0, x1, y1, c: d.rectangle([x0, y0, x1, y1], fill=c)

    # The ceiling: light wood slats, a cream cove under them, round downlights.
    r(0, 0, W - 1, 9, WOOD)
    for x in range(0, W, 6):
        r(x, 0, x, 9, WOOD_DARK)
    r(0, 10, W - 1, 13, CREAM)
    r(0, 14, W - 1, 14, WALL_SHADE)
    for x in range(30, W, 50):
        r(x - 3, 12, x + 3, 13, LIGHT)
    # The wall: cream wallpaper with a faint dotted pattern; a wood dado rail; the skirting.
    for y in range(20, FLOOR - 30, 8):
        for x in range((y // 8 % 2) * 4, W, 8):
            d.point((x, y), fill=WALL_DOT)
    r(0, FLOOR - 34, W - 1, FLOOR - 33, WOOD)
    r(0, FLOOR - 4, W - 1, FLOOR - 1, WOOD_DARK)
    # The floor: the red carpet with its cream lattice, over the deck's slab.
    r(0, FLOOR, W - 1, FLOOR + 3, CARPET)
    for x in range(0, W, 6):
        d.point((x, FLOOR + 1), fill=CARPET_LINE)
        d.point((x + 3, FLOOR + 2), fill=CARPET_DARK)
    r(0, FLOOR + 4, W - 1, H - 2, SLAB)
    r(0, H - 1, W - 1, H - 1, "#6f7882")

    # The amber glass doors back out to the lobby.
    glass_door(d, DOOR_X - 14, FLOOR - 80, FLOOR - 5)
    # Sconces either side of the altar; the painting over it: soft pastel strokes in a white frame.
    cx = 204
    r(cx - 22, 30, cx + 22, 62, WHITE)
    r(cx - 20, 32, cx + 20, 60, "#f2f6f6")
    for i, col in enumerate(("#a884f3", "#8fd3ff", "#fca790", "#cddf6c", "#4d65b4")):
        d.line([(cx - 16 + i * 7, 56), (cx - 8 + i * 7, 36)], fill=col, width=2)
    for x in (cx - 44, cx + 44):
        r(x - 2, 46, x + 2, 52, "#f9c22b")
        r(x - 3, 40, x + 3, 45, CREAM)
        r(x - 6, 36, x + 6, 39, (0xfb, 0xff, 0x86))
    # A wood side table with a white candle by the far wall, and a window-like light panel.
    r(W - 28, FLOOR - 26, W - 8, FLOOR - 24, WOOD_DARK)
    r(W - 26, FLOOR - 24, W - 25, FLOOR - 5, WOOD_DARK)
    r(W - 11, FLOOR - 24, W - 10, FLOOR - 5, WOOD_DARK)
    r(W - 20, FLOOR - 38, W - 17, FLOOR - 27, WHITE)
    r(W - 19, FLOOR - 41, W - 18, FLOOR - 39, "#f79617")
    wash(im, 0, FLOOR)

    # The altar: a round table on a fluted cream pedestal (the photo's), flowers on stands either side.
    d = ImageDraw.Draw(im)
    r(cx - 20, FLOOR - 30, cx + 20, FLOOR - 26, STONE)
    r(cx - 20, FLOOR - 26, cx + 20, FLOOR - 25, STONE_DARK)
    r(cx - 15, FLOOR - 25, cx + 15, FLOOR - 1, STONE)
    for x in range(cx - 13, cx + 14, 4):
        r(x, FLOOR - 24, x, FLOOR - 2, STONE_DARK)
    r(cx - 17, FLOOR - 2, cx + 17, FLOOR - 1, STONE_DARK)
    bouquet = piece("bouquet")
    im.alpha_composite(bouquet, (cx - bouquet.width // 2 - 8, FLOOR - 30 - bouquet.height))
    candle = piece("pillar-candle")
    im.alpha_composite(candle, (cx + 8, FLOOR - 30 - candle.height))
    stand = piece("flower-pedestal")
    for x in (cx - 34, cx + 34):
        im.alpha_composite(stand, (x - stand.width // 2, FLOOR - stand.height))
    # The cane-back chairs in rows facing the altar: two on the door's side, one on the far side.
    chair = piece("cane-chair")                          # drawn facing right (east)
    left = chair.transpose(Image.FLIP_LEFT_RIGHT)
    bow = piece("pew-bow")
    for x in (106, 152):
        im.alpha_composite(chair, (x - chair.width // 2, FLOOR - chair.height))
        im.alpha_composite(bow, (x - chair.width // 2 - 2, FLOOR - chair.height + 2))
    for x in (262,):
        im.alpha_composite(left, (x - chair.width // 2, FLOOR - chair.height))

    # The room opens where the deck was, the deck around it dimmed by the game: the ceiling's shadow,
    # and its two end walls, cream.
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for i in range(8):
        a_ = int(0.35 * 255 * (1 - i / 8) ** 1.6)
        sd.rectangle([0, i * 2, W - 1, i * 2 + 1], fill=(0x2e, 0x22, 0x2f, a_))
    im = Image.alpha_composite(im, shade)
    d = ImageDraw.Draw(im)
    for x0, x1 in ((0, 3), (W - 4, W - 1)):
        d.rectangle([x0, 0, x1, H - 1], fill=WOOD_DARK)
        d.rectangle([x0 + 1, 0, x1 - 1, H - 1], fill=WOOD)
    return im


def open_door():
    """The chapel's door, held open, from the lobby: a wood frame, the amber glass leaf swung in at
    the left, the room beyond: the cream wall, a downlight, a chair's cane back, the red carpet."""
    w, h = 30, 76
    door = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(door)
    r = lambda a, b, c, e, col: d.rectangle([a, b, c, e], fill=col)
    r(0, 0, w - 1, h - 1, WOOD_DARK)
    r(1, 1, w - 2, 1, WOOD)
    r(3, 3, w - 4, h - 1, WALL)
    r(3, 3, w - 4, 5, WOOD)
    r(12, 6, 18, 7, LIGHT)
    r(14, 40, 25, 41, "#ab947a")                                  # a cane chair's back beyond
    r(15, 42, 24, 56, "#e6c98c")
    for y in range(43, 56, 3):
        r(15, y, 24, y, "#cfae6a")
    r(14, 57, 25, 62, "#9babb2")
    r(15, 63, 16, h - 4, WOOD_DARK)
    r(23, 63, 24, h - 4, WOOD_DARK)
    r(3, h - 3, w - 4, h - 1, CARPET)
    # The leaf, swung in: a narrow strip at the hinge, amber glass in its wood edge.
    for y in range(3, h):
        r(3, y, 7, y, WOOD)
        r(4, y, 6, y, AMBER if y % 9 else WOOD)
    r(w - 4, 3, w - 4, h - 1, LIGHT)                              # the light falling out of the room
    return door


if __name__ == "__main__":
    SOURCE.mkdir(parents=True, exist_ok=True)
    room, door = interior(), open_door()
    room.save(SOURCE / "interior.png")
    door.save(SOURCE / "door-open.png")
    room.save(GAME / "chapel-room.png")
    door.save(GAME / "chapel-door-open.png")
    if "--preview" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--preview") + 1])
        sheet = Image.new("RGBA", (W + 50, H), "#2e222f")
        sheet.paste(room, (0, 0))
        sheet.paste(door, (W + 8, H - door.height))
        sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(out)
    print("wrote", (GAME / "chapel-room.png").relative_to(ROOT), (GAME / "chapel-door-open.png").relative_to(ROOT))
