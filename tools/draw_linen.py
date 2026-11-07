"""Draws the housekeeping linen room by hand (GAME_DESIGN.md §5.3, deck 9), a room she can go into
(Bumbot slept in its towels until his spots were taken out, 2026-11-07; §4). Inside, it shows in the corridor's place, the deck around it dimmed
(not cut into the ship's side as cabin 8206 is). A crew room behind a crew door held open: pale
painted steel, a fluorescent tube, grey vinyl. A laundry cart by the door and the door back out,
chrome wire racks stacked with folded towels, sheets and pillows, a heap of fresh towels on the floor
(where Bumbot slept), and low on the far wall a vent with its grille hanging
open, where he gets away.

Also the open door seen from the corridor: a white crew door's frame, its leaf swung in, the racks
beyond it.

Writes assets/source/ship/linen/interior.png and door-open.png and the game's copies,
assets/ship/linen-room.png and assets/ship/linen-door-open.png. Run from the repo root:
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

# Where things are, from the room's left edge (ShipScene's LINEN must agree): the door back out,
# the heap of towels on the floor (its middle and its top over the floor), and the vent.
DOOR_X = 59
HEAP = (150, 6)
VENT = (222, 236)
WASH = 0.25              # how far the background fades toward the wall


def wash(im, y0, y1):
    """Fades a band of the picture toward the wall colour."""
    px = im.load()
    w = tuple(int(WALL[i:i + 2], 16) for i in (1, 3, 5))
    for y in range(y0, y1):
        for x in range(im.width):
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
    for x0 in (70, 160):
        r(x0, 5, x0 + 40, 7, GREY)
        r(x0 + 2, 7, x0 + 38, 8, TUBE)
    # The wall: steel panels with their seams and a few rivets; the skirting.
    for x in range(0, W, 40):
        r(x, 12, x, FLOOR - 5, WALL_SEAM)
        for y in range(18, FLOOR - 8, 24):
            d.point((x + 3, y), fill=WALL_SHADE)
    r(0, FLOOR - 4, W - 1, FLOOR - 1, GREY)
    r(0, FLOOR - 4, W - 1, FLOOR - 4, SLATE)
    # The floor: grey-green vinyl, flecked, over the deck's slab.
    r(0, FLOOR, W - 1, FLOOR + 3, VINYL)
    for x in range(2, W, 7):
        d.point((x, FLOOR + 1 + (x * 5) % 3), fill=VINYL_FLECK)
    r(0, FLOOR + 4, W - 1, H - 2, SLAB)
    r(0, H - 1, W - 1, H - 1, "#6f7882")

    # A laundry cart by the door: a canvas bin on a steel frame, crumpled sheets in it.
    r(8, 92, 40, FLOOR - 8, CANVAS)
    r(8, 92, 40, 93, CANVAS_DARK)
    for x in range(12, 40, 7):
        r(x, 96, x, FLOOR - 10, CANVAS_DARK)
    d.rounded_rectangle([10, 84, 26, 94], radius=4, fill=WHITE)
    d.rounded_rectangle([20, 86, 38, 95], radius=4, fill="#f2f6f6")
    d.line([(14, 88), (22, 90)], fill=PALE)
    r(6, 90, 42, 91, CHROME_DARK)
    r(8, FLOOR - 8, 40, FLOOR - 7, CHROME_DARK)
    for x in (10, 38):
        r(x - 2, FLOOR - 5, x + 2, FLOOR - 1, INK)
    # A clipboard on the wall over it: the steward's checklist.
    r(18, 40, 32, 58, "#ab947a")
    r(20, 43, 30, 57, WHITE)
    r(23, 39, 27, 41, GREY)
    for y in range(46, 56, 3):
        r(21, y, 29, y, GREY)

    # The door back out to the corridor (its inside face): a white steel crew door, its lever and
    # a sign; it stands on the skirting's line, as the cabin's does.
    x0, top = DOOR_X - 14, FLOOR - 80
    r(x0, top, x0 + 28, FLOOR - 5, GREY)
    r(x0 + 2, top + 2, x0 + 26, FLOOR - 5, WHITE)
    r(x0 + 3, top + 3, x0 + 3, FLOOR - 6, PALE)
    r(x0 + 7, top + 12, x0 + 21, top + 20, "#1ebc73")             # a green safety sign
    r(x0 + 9, top + 14, x0 + 19, top + 14, WHITE)
    r(x0 + 9, top + 17, x0 + 15, top + 17, WHITE)
    r(x0 + 20, top + 40, x0 + 25, top + 41, SLATE)                # the lever

    # The racks: folded white towels, hand towels, blue bath mats, sheets, pillows on top.
    rack(d, 80, 140, (34, 58, 82, 106))
    towels(d, 83, 140, 34, WHITE, PALE, h=6, n=2)
    towels(d, 83, 140, 58, WHITE, PALE)
    towels(d, 83, 140, 82, BLUE_LIGHT, BLUE, h=4, n=4)
    towels(d, 83, 140, 106, WHITE, PALE, h=4, n=4)
    for x in range(84, 136, 17):                                  # the pillows, on the top shelf
        d.rounded_rectangle([x, 26, x + 15, 33], radius=3, fill="#f2f6f6")
    rack(d, 146, 206, (40, 66, 92))
    for y in (40, 66):                                            # sheets, folded flat
        for k in range(5):
            r(149, y - 3 - k * 3, 172, y - 1 - k * 3, WHITE if k % 2 else "#f2f6f6")
            r(149, y - 1 - k * 3, 172, y - 1 - k * 3, PALE)
    towels(d, 176, 206, 40, WHITE, PALE, h=5, n=4)
    for x in range(177, 205, 6):                                  # toilet rolls
        r(x, 60, x + 4, 65, WHITE)
        r(x + 2, 62, x + 2, 63, GREY)
    for x in range(150, 205, 5):                                  # little toiletry bottles
        r(x, 86, x + 2, 91, BLUE if x % 10 else "#0eaf9b")
        r(x, 85, x + 2, 85, WHITE)

    # Low on the far wall, a vent: its dark duct, the grille hanging open on one screw.
    a, b = VENT
    r(a - 1, FLOOR - 22, b + 1, FLOOR - 5, SLATE)
    r(a, FLOOR - 21, b, FLOOR - 5, INK)
    r(a + 1, FLOOR - 20, b - 1, FLOOR - 19, DARK)
    for i in range(10):
        d.line([(a - 10 + i, FLOOR - 21 + i * 2), (a - 2 + i, FLOOR - 25 + i * 2)], fill=GREY)
    d.line([(a - 10, FLOOR - 21), (a - 1, FLOOR - 26)], fill=PALE)
    d.point((a, FLOOR - 21), fill=CHROME_DARK)

    # All of that is background, washed out a little toward the wall, as in the cabin; the floor
    # she stands on and the heap Bumbot sleeps on keep their colours.
    wash(im, 0, FLOOR)
    d = ImageDraw.Draw(im)

    # The heap of fresh towels on the floor, in front of the second rack: Bumbot sleeps on it.
    cx, top = HEAP[0], FLOOR - HEAP[1]
    d.rounded_rectangle([cx - 26, top, cx + 26, FLOOR + 1], radius=3, fill=WHITE)
    d.rounded_rectangle([cx - 30, top + 2, cx - 16, FLOOR + 1], radius=2, fill="#f2f6f6")
    d.rounded_rectangle([cx + 14, top + 1, cx + 30, FLOOR + 1], radius=2, fill=BLUE_LIGHT)
    d.line([(cx - 22, top + 3), (cx + 10, top + 3)], fill=PALE)
    d.line([(cx + 16, top + 4), (cx + 28, top + 4)], fill=BLUE)

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


def open_door():
    """The crew door, propped open, from the corridor: its frame from the atlas's crew door, the leaf
    swung in against the left, the room beyond: the wall, a rack of towels, the vinyl floor."""
    atlas = Image.open(GAME / "ship.png").convert("RGBA")
    frames = __import__("json").loads((GAME / "ship.json").read_text(encoding="utf-8"))["frames"]
    f = frames["door-crew"]["frame"]
    door = atlas.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
    w, h = door.size
    px = door.load()
    # The leaf: the door's white inside its frame (the frame's own white is at its edges).
    leaf = [(x, y) for y in range(h) for x in range(4, w - 4) if px[x, y][:3] == (0xff, 0xff, 0xff) and y > 4]
    x0 = min(x for x, _ in leaf); x1 = max(x for x, _ in leaf)
    y0 = min(y for _, y in leaf)
    d = ImageDraw.Draw(door)
    r = lambda a, b, c, e, col: d.rectangle([a, b, c, e], fill=col)
    r(x0, y0, x1, h - 1, WALL)
    r(x0, y0, x1, y0 + 2, CEILING)
    r(x0 + 3, y0 + 1, x1, y0 + 2, TUBE)                           # the tube's light
    r(x0 + 8, y0 + 10, x0 + 8, h - 4, CHROME_DARK)                # a rack's upright and shelves
    for y in range(y0 + 18, h - 6, 14):
        r(x0 + 8, y, x1, y, CHROME_DARK)
        for x in range(x0 + 9, x1 - 2, 6):
            r(x, y - 4, x + 4, y - 1, WHITE)
            r(x, y - 1, x + 4, y - 1, PALE)
    r(x0, h - 3, x1, h - 1, VINYL)
    # The leaf, swung in: a narrow strip at the hinge, seen edge-on, greyer toward the room.
    for y in range(y0, h):
        r(x0, y, x0 + 4, y, GREY)
        r(x0 + 1, y, x0 + 2, y, WHITE)
    # The light falling out of the room onto the frame's inner edge.
    r(x1, y0, x1, h - 1, TUBE)
    return door


if __name__ == "__main__":
    SOURCE.mkdir(parents=True, exist_ok=True)
    room, door = interior(), open_door()
    room.save(SOURCE / "interior.png")
    door.save(SOURCE / "door-open.png")
    room.save(GAME / "linen-room.png")
    door.save(GAME / "linen-door-open.png")
    if "--preview" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--preview") + 1])
        sheet = Image.new("RGBA", (W + 50, H), "#2e222f")
        sheet.paste(room, (0, 0))
        sheet.paste(door, (W + 8, H - door.height))
        sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(out)
    print("wrote", (GAME / "linen-room.png").relative_to(ROOT), (GAME / "linen-door-open.png").relative_to(ROOT))
