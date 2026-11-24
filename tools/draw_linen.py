"""Draws the housekeeping linen room by hand (GAME_DESIGN.md §5.3, deck 9), a room she can go into
(Bumbot slept in its towels until his spots were taken out, 2026-11-07; §4). Inside, it shows in the corridor's place, the deck around it dimmed
(not cut into the ship's side as cabin 8206 is). A crew room behind a crew door: pale
painted steel, a fluorescent tube, grey vinyl. The laundry chute's hatch low in the wall by the door,
the door back out, chrome wire racks stacked with folded towels, sheets and pillows (Bumbot asleep on the
toiletries' shelf, the game's), and on the forward wall the mouth of a ventilation shaft behind its cover (the game's,
tools/build_shaft.py), where he gets away: she pushes the laundry cart up to it and crawls in from the cart's rim
(docs/population.md `scn_duct`; docs/shaft-remake-log.md). The laundry cart she pushes is the generated one in the
things atlas (`laundry-cart`; the one drawn here until 2026-11-23 is retired, the user).

**Redecorated 2026-11-24** (the user's choice, linen A): what this draws is the plan the generated look is laid over,
`tools/redecorate_rooms.py`, which keeps its door and hatch. The door seen from the corridor is the ship's regular crew
door, shut (the user, 2026-11-24; the open door with the room seen through it, drawn here until then, is retired).

Writes assets/source/ship/linen/interior-plain.png (as drawn), interior.png and the game's copy,
assets/ship/linen-room.png (redecorated). Run from the repo root:
    python tools/draw_linen.py [--preview out.png]
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source" / "ship" / "linen"
GAME = ROOT / "assets" / "ship"
W, H = 240, 144          # 5 m of room; its wall up to the ceiling (128 px) and the floor's slab
FLOOR = 128              # her feet: the top of the slab

INK = "#2e222f"
WALL, WALL_SEAM, WALL_SHADE = "#dfe8e2", "#c7dcd0", "#b8c9bf"
CEILING = "#f4f6f3"
WHITE, PALE, GREY, SLATE, DARK = "#ffffff", "#c7dcd0", "#9babb2", "#625565", "#3e3546"
CHROME, CHROME_DARK = "#c7dcd0", "#7f708a"
VINYL, VINYL_FLECK, SLAB = "#92a984", "#547e64", "#8e98a3"
BLUE, BLUE_LIGHT = "#4d9be6", "#8fd3ff"
CANVAS, CANVAS_DARK = "#b2ba90", "#92a984"
TUBE = "#fbff86"

# Where things are, from the room's left edge (ShipScene's LINEN and tools/population.py's LINEN and SHAFT must agree):
# the door back out, the chute's hatch (its middle), the shaft's mouth on the forward wall.
# (Mirrored 2026-11-23, the user: the door at the room's aft end, on the right, the racks and Bumbot's bottle shelf
# forward of it, the shaft's mouth on the forward wall, so that she pushes the cart, climbs in and crawls on all one
# way, toward the bow, where the shaft leads. The chute's hatch between the racks and the door: straight over the
# laundry's cart on deck 4, five decks down. The mouth itself is the game's (tools/build_shaft.py): a duct's end
# standing out of the wall, its floor level with the laundry cart's rim; this picture leaves its wall bare.)
DOOR_X = 180
CHUTE_X = 129
WASH = 0.3               # how far the background fades toward the wall (cabin 8206's, the user, 2026-11-15)
# What she uses keeps its full colours: the door back out and the chute's hatch (x0, y0, x1, y1).


def wash(im, y0, y1, keep=()):
    """Fades a band of the picture toward the wall colour, but for the boxes in `keep`."""
    px = im.load()
    w = tuple(int(WALL[i:i + 2], 16) for i in (1, 3, 5))
    for y in range(y0, y1):
        for x in range(im.width):
            if any(a <= x <= b and c0 <= y <= c1 for a, c0, b, c1 in keep):
                continue
            c = px[x, y]
            px[x, y] = (*(round(v + (t - v) * WASH) for v, t in zip(c[:3], w)), c[3])


def towels(d, x0, x1, y, colour, edge, h=5, n=3):
    """Folded towels stacked on a shelf at y (their bottom), side by side: each stack `n` high."""
    for x in range(x0, x1 - 9, 12):
        for k in range(n):
            top = y - (k + 1) * h
            d.rounded_rectangle([x, top, x + 10, top + h - 1], radius=1, fill=colour)
            d.line([(x + 1, top + h - 1), (x + 9, top + h - 1)], fill=edge)
            d.point((x + 10, top + 2), fill=edge)


def rack(d, x0, x1, shelves):
    """A chrome wire rack: two uprights, wire shelves at each y."""
    r = lambda a, b, c, e, col: d.rectangle([a, b, c, e], fill=col)
    for x in (x0, x1):
        r(x, 14, x + 1, FLOOR - 1, CHROME_DARK)
        r(x, 14, x, FLOOR - 1, CHROME)
    for y in shelves:
        r(x0, y, x1 + 1, y + 1, CHROME_DARK)
        r(x0, y, x1 + 1, y, CHROME)
        for x in range(x0 + 3, x1, 4):
            d.point((x, y + 1), fill=CHROME)


def interior():
    im = Image.new("RGBA", (W, H), WALL)
    d = ImageDraw.Draw(im)
    r = lambda x0, y0, x1, y1, c: d.rectangle([x0, y0, x1, y1], fill=c)

    # The ceiling: painted steel, a fluorescent tube in its fitting, a pipe run along it.
    r(0, 0, W - 1, 7, CEILING)
    r(0, 8, W - 1, 8, WALL_SHADE)
    r(0, 10, W - 1, 11, GREY)
    r(0, 10, W - 1, 10, PALE)
    for x0 in (39, 129):
        r(x0, 5, x0 + 40, 7, GREY)
        r(x0 + 2, 7, x0 + 38, 8, TUBE)
    # The wall: steel panels with their seams and a few rivets; the skirting.
    for x in range(W - 1, 0, -40):
        r(x, 12, x, FLOOR - 5, WALL_SEAM)
        for y in range(18, FLOOR - 8, 24):
            d.point((x - 3, y), fill=WALL_SHADE)
    r(0, FLOOR - 4, W - 1, FLOOR - 1, GREY)
    r(0, FLOOR - 4, W - 1, FLOOR - 4, SLATE)
    # The floor: grey-green vinyl, flecked, over the deck's slab.
    r(0, FLOOR, W - 1, FLOOR + 3, VINYL)
    for x in range(2, W, 7):
        d.point((x, FLOOR + 1 + (x * 5) % 3), fill=VINYL_FLECK)
    r(0, FLOOR + 4, W - 1, H - 2, SLAB)
    r(0, H - 1, W - 1, H - 1, "#6f7882")

    # The laundry chute's hatch, low in the wall between the racks and the door: a steel flap on a hinge, a handle, a
    # green plate with an arrow down (the Housekeeping card's colour).
    cx = CHUTE_X
    r(cx - 15, FLOOR - 44, cx + 15, FLOOR - 12, CHROME_DARK)
    r(cx - 13, FLOOR - 42, cx + 13, FLOOR - 14, CHROME)
    r(cx - 13, FLOOR - 42, cx + 13, FLOOR - 41, WHITE)
    r(cx - 13, FLOOR - 15, cx + 13, FLOOR - 14, GREY)
    r(cx - 6, FLOOR - 20, cx + 6, FLOOR - 19, SLATE)                # the handle
    r(cx - 8, FLOOR - 38, cx + 8, FLOOR - 26, "#1ebc73")
    r(cx - 1, FLOOR - 36, cx, FLOOR - 31, WHITE)
    d.polygon([(cx - 4, FLOOR - 32), (cx + 3, FLOOR - 32), (cx, FLOOR - 28), (cx - 1, FLOOR - 28)], fill=WHITE)
    for x in (cx - 12, cx + 12):
        d.point((x, FLOOR - 43), fill=SLATE)
    # A clipboard on the wall over it: the steward's checklist.
    r(cx - 7, 44, cx + 7, 62, "#ab947a")
    r(cx - 5, 47, cx + 5, 61, WHITE)
    r(cx - 2, 43, cx + 2, 45, GREY)
    for y in range(50, 60, 3):
        r(cx - 4, y, cx + 4, y, GREY)

    # The door back out to the corridor (its inside face): a white steel crew door, its lever and
    # a sign; it stands on the skirting's line, as the cabin's does.
    x0, top = DOOR_X - 14, FLOOR - 80
    r(x0, top, x0 + 28, FLOOR - 5, GREY)
    r(x0 + 2, top + 2, x0 + 26, FLOOR - 5, WHITE)
    r(x0 + 25, top + 3, x0 + 25, FLOOR - 6, PALE)
    r(x0 + 7, top + 12, x0 + 21, top + 20, "#1ebc73")             # a green safety sign
    r(x0 + 9, top + 14, x0 + 19, top + 14, WHITE)
    r(x0 + 9, top + 17, x0 + 15, top + 17, WHITE)
    r(x0 + 3, top + 40, x0 + 8, top + 41, SLATE)                  # the lever

    # The racks. Forward of the hatch, the wide one: sheets, towels, toilet rolls, and the bottle shelf Bumbot sleeps
    # on (36 px up, his middle 63 px in: tools/population.py's `bb4`). Aft of the door, a narrow one: towels, bath
    # mats, pillows on top.
    rack(d, 33, 93, (40, 66, 92))
    for y in (40, 66):                                            # sheets, folded flat
        for k in range(5):
            r(67, y - 3 - k * 3, 90, y - 1 - k * 3, WHITE if k % 2 else "#f2f6f6")
            r(67, y - 1 - k * 3, 90, y - 1 - k * 3, PALE)
    towels(d, 36, 66, 40, WHITE, PALE, h=5, n=4)
    for x in range(36, 64, 6):                                    # toilet rolls
        r(x, 60, x + 4, 65, WHITE)
        r(x + 2, 62, x + 2, 63, GREY)
    for x in range(36, 91, 5):                                    # little toiletry bottles
        r(x, 86, x + 2, 91, BLUE if x % 10 else "#0eaf9b")
        r(x, 85, x + 2, 85, WHITE)
    rack(d, 199, 233, (34, 58, 82, 106))
    towels(d, 202, 233, 34, WHITE, PALE, h=6, n=2)
    towels(d, 202, 233, 58, WHITE, PALE)
    towels(d, 202, 233, 82, BLUE_LIGHT, BLUE, h=4, n=4)
    towels(d, 202, 233, 106, WHITE, PALE, h=4, n=4)
    for x in (202, 218):                                          # the pillows, on the top shelf
        d.rounded_rectangle([x, 26, x + 14, 33], radius=3, fill="#f2f6f6")

    # All of that is background, washed out a little toward the wall, as in the cabin; the floor she stands on, the
    # door and the hatch keep their colours.
    wash(im, 0, FLOOR, keep=((DOOR_X - 15, FLOOR - 81, DOOR_X + 15, FLOOR - 1),
                             (CHUTE_X - 16, FLOOR - 45, CHUTE_X + 16, FLOOR - 11)))
    d = ImageDraw.Draw(im)

    # The room opens where the corridor was (the user, 2026-11-06), the deck around it dimmed by the
    # game: the ceiling's shadow as along the corridor, and its two end bulkheads, plain steel.
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for i in range(8):
        a_ = int(0.45 * 255 * (1 - i / 8) ** 1.6)
        sd.rectangle([0, i * 2, W - 1, i * 2 + 1], fill=(0x2e, 0x22, 0x2f, a_))
    im = Image.alpha_composite(im, shade)
    d = ImageDraw.Draw(im)
    for x0, x1 in ((0, 3), (W - 4, W - 1)):
        d.rectangle([x0, 0, x1, H - 1], fill=GREY)
        d.rectangle([x0 + 1, 0, x1 - 1, H - 1], fill=PALE)
    return im


if __name__ == "__main__":
    SOURCE.mkdir(parents=True, exist_ok=True)
    room = interior()
    room.save(SOURCE / "interior-plain.png")
    # (Redecorated, the user's choice of 2026-11-24: tools/redecorate_rooms.py lays the generated look over it.)
    from redecorate_rooms import linen
    room = linen(room)
    room.save(SOURCE / "interior.png")
    room.save(GAME / "linen-room.png")
    if "--preview" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--preview") + 1])
        sheet = Image.new("RGBA", (W, H), "#2e222f")
        sheet.paste(room, (0, 0))
        sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(out)
    print("wrote", (GAME / "linen-room.png").relative_to(ROOT))
