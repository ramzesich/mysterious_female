"""Draws the plan's rooms by hand (GAME_DESIGN.md §6.1.12; docs/population.md): the small rooms
behind doors, each shown in the corridor's place with the deck dimmed round it (the user's rule for
rooms, CLAUDE.md). One picture per room, assets/ship/rooms/<id>.png, as wide as tools/population.py's
ROOMS says and 144 px tall (128 of wall, 16 of floor slab); each door back out is where the room's
`doors` put it (the first at 59 px), cut from the ship's atlas.

    python tools/draw_rooms.py [id ...] [--preview out.png]

Run after tools/build_ship_art.py (it uses the atlas). A room with no drawing here stays bare in
the game (src/world/world.js draws walls and doors).
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from palettize import palettize
from population import ROOMS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "ship" / "rooms"
H, FLOOR = 144, 128
DOOR_X = 59

INK = "#2e222f"
WHITE, PALE, GREY, SLATE, DARK = "#ffffff", "#c7dcd0", "#9babb2", "#625565", "#3e3546"
STEEL, STEEL_SEAM, STEEL_SHADE = "#dfe8e2", "#c7dcd0", "#b8c9bf"
TUBE = "#fbff86"
WOOD, WOOD_DARK, WOOD_LIGHT = "#ab947a", "#7a4528", "#d8b29a"
CREAM, CREAM_SHADE = "#f3ecdd", "#d8cdb8"
BLUE, BLUE_LIGHT, NAVY = "#4d9be6", "#8fd3ff", "#323353"
RED, ORANGE, YELLOW, GREEN, TEAL = "#ae2334", "#f28c28", "#f9c22b", "#1ebc73", "#0b5e65"
PINK, MAUVE = "#f68181", "#905ea9"
SLAB = "#8e98a3"

_atlas = None


def atlas(frame):
    """A piece of the ship's atlas (tools/build_ship_art.py)."""
    global _atlas
    if _atlas is None:
        _atlas = (Image.open(ROOT / "assets" / "ship" / "ship.png").convert("RGBA"),
                  json.loads((ROOT / "assets" / "ship" / "ship.json").read_text(encoding="utf-8"))["frames"])
    img, frames = _atlas
    f = frames[frame]["frame"]
    return img.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


def stand(im, frame, x, dy=0, flip=False):
    """A piece standing at x (its middle), its foot `dy` px over the floor."""
    piece = atlas(frame)
    if flip:
        piece = piece.transpose(Image.FLIP_LEFT_RIGHT)
    im.alpha_composite(piece, (x - piece.width // 2, FLOOR - dy - piece.height))
    return piece.size


class Room:
    def __init__(self, width, wall, seam, ceiling=WHITE, skirting=GREY, floor=GREY, fleck=SLATE, pitch=48):
        self.w = width
        self.im = Image.new("RGBA", (width, H), wall)
        self.d = ImageDraw.Draw(self.im)
        r = self.r
        r(0, 0, width - 1, 7, ceiling)
        r(0, 8, width - 1, 8, seam)
        for x in range(0, width, pitch):
            r(x, 9, x, FLOOR - 5, seam)
        r(0, FLOOR - 4, width - 1, FLOOR - 1, skirting)
        r(0, FLOOR, width - 1, FLOOR + 3, floor)
        for x in range(2, width, 7):
            self.d.point((x, FLOOR + 1 + (x * 5) % 3), fill=fleck)
        r(0, FLOOR + 4, width - 1, H - 2, SLAB)
        r(0, H - 1, width - 1, H - 1, "#6f7882")

    def r(self, x0, y0, x1, y1, c):
        self.d.rectangle([x0, y0, x1, y1], fill=c)

    def box(self, x0, y0, x1, y1, fill, edge=INK):
        self.d.rectangle([x0, y0, x1, y1], fill=fill, outline=edge)

    def tube(self, x, w=40):
        """A fluorescent tube in its fitting on the ceiling."""
        self.r(x, 5, x + w, 7, GREY)
        self.r(x + 2, 7, x + w - 2, 8, TUBE)

    def pipe(self, y=11, c=GREY):
        self.r(0, y, self.w - 1, y + 1, c)
        self.r(0, y, self.w - 1, y, PALE)

    def door(self, x=DOOR_X, frame="door-crew"):
        stand(self.im, frame, x)

    def shelves(self, x0, x1, ys, post=SLATE, board=GREY):
        """An open shelf unit: two uprights, a board at each y (its top)."""
        for x in (x0, x1):
            self.r(x, ys[0] - 14, x + 1, FLOOR - 1, post)
        for y in ys:
            self.r(x0, y, x1 + 1, y + 2, board)
            self.r(x0, y + 2, x1 + 1, y + 2, post)

    def crate(self, x, bottom, w=22, h=16, fill=WOOD, slat=WOOD_DARK):
        self.box(x, bottom - h, x + w, bottom, fill, INK)
        self.r(x + 1, bottom - h + 4, x + w - 1, bottom - h + 4, slat)
        self.r(x + 1, bottom - 5, x + w - 1, bottom - 5, slat)
        self.r(x + w // 2, bottom - h + 1, x + w // 2, bottom - 1, slat)

    def sack(self, x, bottom, w=16, h=14, fill=CREAM_SHADE):
        self.d.rounded_rectangle([x, bottom - h, x + w, bottom], radius=4, fill=fill, outline=INK)
        self.r(x + w // 2 - 2, bottom - h - 2, x + w // 2 + 2, bottom - h + 1, WOOD)

    def jars(self, x0, x1, bottom, colours, step=7):
        for i, x in enumerate(range(x0, x1 - 4, step)):
            c = colours[i % len(colours)]
            self.r(x, bottom - 8, x + 4, bottom, c)
            self.r(x, bottom - 9, x + 4, bottom - 8, WHITE)
            self.d.point((x + 1, bottom - 6), fill=WHITE)

    def boxes(self, x0, x1, bottom, colours, w=12, h=10):
        for i, x in enumerate(range(x0, x1 - w, w + 2)):
            c = colours[i % len(colours)]
            hh = h + (i * 3) % 4
            self.box(x, bottom - hh, x + w, bottom, c, INK)
            self.r(x + 2, bottom - hh + 3, x + w - 2, bottom - hh + 4, WHITE)

    def poster(self, x, y, w, h, colours):
        self.box(x, y, x + w, y + h, colours[0], INK)
        self.r(x + 2, y + 2, x + w - 2, y + h // 2, colours[1])
        self.r(x + 3, y + h - 6, x + w - 3, y + h - 5, colours[2])
        self.r(x + 3, y + h - 3, x + w - 6, y + h - 3, colours[2])

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        palettize(self.im).save(OUT / f"{name}.png")
        return self.im


# --- Region 1's rooms (decks 4 and 5) --------------------------------------------------------------

def laundry(width):
    """The laundry, deck 4 (population: `room_laundry`): washers and dryers, the chute's mouth in the
    ceiling over a cart of towels (she lands in it), a folding table, a shelf with a tangerine."""
    R = Room(width, STEEL, STEEL_SEAM, floor="#92a984", fleck="#547e64", pitch=40)
    r, box, d = R.r, R.box, R.d
    R.pipe()
    R.pipe(15, PALE)
    for x in (30, 150, 262):
        R.tube(x)
    R.door()
    # Three washers, round glass doors with blue water behind; a dryer stacked on the last two.
    for i, x in enumerate((84, 112, 140)):
        box(x, FLOOR - 34, x + 26, FLOOR - 5, WHITE)
        r(x + 2, FLOOR - 32, x + 24, FLOOR - 28, PALE)
        r(x + 19, FLOOR - 31, x + 22, FLOOR - 29, (GREEN, YELLOW, RED)[i])
        d.ellipse([x + 5, FLOOR - 25, x + 21, FLOOR - 9], fill=SLATE, outline=INK)
        d.ellipse([x + 7, FLOOR - 23, x + 19, FLOOR - 11], fill=BLUE)
        d.arc([x + 8, FLOOR - 22, x + 18, FLOOR - 12], 200, 300, fill=BLUE_LIGHT)
        r(x, FLOOR - 5, x + 26, FLOOR - 5, GREY)
    for x in (112, 140):
        box(x, FLOOR - 64, x + 26, FLOOR - 35, PALE)
        d.ellipse([x + 5, FLOOR - 59, x + 21, FLOOR - 43], fill=DARK, outline=INK)
        d.ellipse([x + 8, FLOOR - 56, x + 18, FLOOR - 46], fill=SLATE)
        r(x + 2, FLOOR - 63, x + 24, FLOOR - 61, GREY)
    # Steam from a pipe joint over them.
    for x, y in ((120, 22), (124, 18), (130, 21), (152, 20), (156, 17)):
        d.ellipse([x, y, x + 5, y + 4], fill=WHITE)
    # The chute's mouth in the ceiling, a square steel hood, and under it a canvas cart heaped with towels.
    box(184, 8, 216, 22, GREY)
    r(187, 20, 213, 22, DARK)
    for k in range(4):
        r(188 + k * 7, 10, 190 + k * 7, 18, STEEL_SHADE)
    box(178, FLOOR - 26, 222, FLOOR - 6, "#b2ba90")
    for x in range(184, 222, 8):
        r(x, FLOOR - 24, x, FLOOR - 8, "#92a984")
    for x in (182, 214):
        d.ellipse([x, FLOOR - 6, x + 5, FLOOR - 1], fill=DARK)
    for x, y, c in ((180, 33, WHITE), (192, 37, BLUE_LIGHT), (203, 34, WHITE), (211, 31, PALE), (186, 30, PALE)):
        d.rounded_rectangle([x, FLOOR - y, x + 12, FLOOR - y + 8], radius=2, fill=c, outline=GREY)
    # A shelf of detergent on the wall (the tangerine sits on it, 46 px up), and the folding table.
    r(236, FLOOR - 46, 268, FLOOR - 44, GREY)
    r(236, FLOOR - 44, 268, FLOOR - 44, SLATE)
    for x, c in ((238, BLUE), (258, ORANGE)):
        r(x, FLOOR - 56, x + 6, FLOOR - 47, c)
        r(x + 1, FLOOR - 58, x + 4, FLOOR - 56, WHITE)
    box(270, FLOOR - 30, 326, FLOOR - 27, WHITE)
    for x in (273, 322):
        r(x, FLOOR - 27, x + 1, FLOOR - 1, GREY)
    for x, n in ((276, 4), (290, 3), (306, 5)):
        for k in range(n):
            d.rounded_rectangle([x, FLOOR - 35 - k * 4, x + 11, FLOOR - 31 - k * 4], radius=1,
                                fill=(WHITE, BLUE_LIGHT)[(x + k) % 2], outline=GREY)
    return R.save("laundry")


def store(width):
    """The dry store, deck 4 (`room_store`): shelves of boxes, jars and sacks, crates of tangerines."""
    R = Room(width, "#c9c2b0", "#b3a995", ceiling=CREAM, skirting=WOOD_DARK, floor=SLAB, fleck=SLATE, pitch=60)
    R.tube(60)
    R.tube(160)
    R.door()
    R.shelves(84, 232, [FLOOR - 96, FLOOR - 68, FLOOR - 40], post=WOOD_DARK, board=WOOD)
    R.boxes(88, 150, FLOOR - 96, [ORANGE, BLUE, CREAM])
    R.jars(156, 230, FLOOR - 96, [RED, YELLOW, GREEN])
    R.jars(88, 130, FLOOR - 68, [YELLOW, ORANGE])
    R.boxes(136, 230, FLOOR - 68, [CREAM, TEAL, PINK])
    # The shelf at 40 px: sacks, and the two crates the tangerines lie on (at 150 and 159).
    R.sack(90, FLOOR - 40)
    R.sack(108, FLOOR - 40, fill=CREAM)
    R.crate(194, FLOOR - 40, w=30, h=14)
    # On the floor under the shelves: big crates and a sack trolley's load.
    R.crate(90, FLOOR - 1, w=28, h=22)
    R.crate(122, FLOOR - 1, w=24, h=18)
    R.sack(184, FLOOR - 1, w=20, h=18)
    R.sack(206, FLOOR - 1, w=20, h=16, fill=CREAM)
    # A low crate standing out from the shelves, its top 40 px up... no: the tangerines rest on the
    # 40 px shelf between the sacks and the crate.
    R.poster(20, 40, 22, 28, [WHITE, "#f3ecdd", SLATE])
    return R.save("store")


def smcabin(width):
    """The stage manager's cabin, deck 4 (`room_sm_cabin`): a bunk, show posters, a desk with his
    headset's charger, a shelf (50 px up) where his pills stand."""
    R = Room(width, "#e6dcc8", "#d8cdb8", ceiling=CREAM, skirting=WOOD, floor="#4d65b4", fleck=NAVY, pitch=240)
    r, box, d = R.r, R.box, R.d
    r(98, 5, 126, 8, CREAM_SHADE)
    r(102, 8, 122, 9, TUBE)
    R.door(frame="door-cabin")
    # Show posters over the desk.
    R.poster(84, 30, 24, 32, [RED, YELLOW, WHITE])
    R.poster(112, 26, 24, 32, [NAVY, PINK, WHITE])
    R.poster(140, 34, 20, 26, [TEAL, ORANGE, WHITE])
    # The desk: a lamp, papers, a mug.
    box(86, FLOOR - 30, 134, FLOOR - 27, WOOD)
    for x in (88, 131):
        r(x, FLOOR - 27, x + 1, FLOOR - 1, WOOD_DARK)
    r(92, FLOOR - 32, 106, FLOOR - 31, WHITE)
    r(118, FLOOR - 36, 122, FLOOR - 31, RED)
    r(110, FLOOR - 40, 111, FLOOR - 31, DARK)
    r(106, FLOOR - 43, 114, FLOOR - 40, YELLOW)
    stand(R.im, "office-chair", 112)
    # The shelf, 50 px up, books on it; the pills stand at 170.
    r(150, FLOOR - 50, 196, FLOOR - 48, WOOD)
    r(150, FLOOR - 48, 196, FLOOR - 48, WOOD_DARK)
    for x, c, hh in ((152, RED, 12), (156, BLUE, 10), (160, GREEN, 13), (182, MAUVE, 11), (186, ORANGE, 12), (190, NAVY, 9)):
        r(x, FLOOR - 50 - hh, x + 3, FLOOR - 51, c)
    # The bunk: two berths, curtains drawn back, a ladder.
    box(162, FLOOR - 44, 232, FLOOR - 1, WOOD_DARK)
    r(164, FLOOR - 42, 230, FLOOR - 24, "#e6dcc8")
    r(164, FLOOR - 21, 230, FLOOR - 3, "#e6dcc8")
    for y in (FLOOR - 28, FLOOR - 8):
        r(166, y, 228, y + 4, BLUE)
        r(166, y - 5, 182, y - 1, WHITE)
    r(164, FLOOR - 24, 230, FLOOR - 22, WOOD)
    r(214, FLOOR - 42, 215, FLOOR - 3, GREY)
    r(220, FLOOR - 42, 221, FLOOR - 3, GREY)
    for y in range(FLOOR - 38, FLOOR - 4, 8):
        r(214, y, 221, y, GREY)
    return R.save("smcabin")


def pantry(width):
    """The pantry between the kitchens, deck 5 (`room_pantry`): a passage of shelves, jars and crates,
    a crew door at each end."""
    R = Room(width, "#d9dee0", "#c0c8cc", floor=SLAB, fleck=SLATE, pitch=36)
    R.pipe()
    R.tube(100)
    R.tube(190)
    R.door(DOOR_X)
    R.door(236)
    R.shelves(84, 210, [FLOOR - 100, FLOOR - 74, FLOOR - 48], post=SLATE, board=GREY)
    R.jars(88, 140, FLOOR - 100, [RED, YELLOW, GREEN, ORANGE])
    R.boxes(146, 208, FLOOR - 100, [CREAM, BLUE])
    R.boxes(88, 130, FLOOR - 74, [ORANGE, CREAM, TEAL])
    R.jars(136, 208, FLOOR - 74, [YELLOW, MAUVE, RED])
    R.sack(90, FLOOR - 48)
    R.jars(112, 150, FLOOR - 48, [GREEN, ORANGE])
    R.crate(160, FLOOR - 48, w=26, h=14)
    R.crate(88, FLOOR - 1, w=26, h=20)
    R.crate(118, FLOOR - 1, w=22, h=16)
    R.sack(150, FLOOR - 1, w=20, h=18)
    R.crate(176, FLOOR - 1, w=28, h=22)
    # Strings of onions and peppers hung from the pipe.
    for x, c in ((30, ORANGE), (36, RED), (260, RED), (268, YELLOW)):
        R.r(x, 13, x, 20, WOOD)
        for k in range(4):
            R.d.ellipse([x - 2, 20 + k * 5, x + 2, 24 + k * 5], fill=c)
    return R.save("pantry")


def galley(width):
    """The Seven Seas' galley, deck 5 (`room_galley`): white tiles, the pass's counter, a range with
    pans hung over it, sacks of flour where the stage's trap door drops her."""
    R = Room(width, "#eef2f2", "#d9dee0", floor="#c7dcd0", fleck=GREY, pitch=16)
    r, box, d = R.r, R.box, R.d
    for y in range(24, FLOOR - 8, 16):
        r(0, y, width - 1, y, "#d9dee0")
    R.pipe()
    for x in (70, 170, 270):
        R.tube(x)
    R.door()
    # The pass: a steel counter with a heat lamp and plates under cloches.
    box(84, FLOOR - 32, 150, FLOOR - 28, GREY)
    box(86, FLOOR - 28, 148, FLOOR - 1, PALE)
    r(86, FLOOR - 16, 148, FLOOR - 15, GREY)
    for x in (92, 112, 132):
        d.pieslice([x, FLOOR - 42, x + 12, FLOOR - 24], 180, 360, fill=PALE, outline=INK)
        r(x - 1, FLOOR - 33, x + 13, FLOOR - 32, WHITE)
    r(84, 30, 150, 33, GREY)
    for x in (96, 116, 136):
        r(x, 33, x + 6, 36, ORANGE)
    # The range: burners, a stock pot, a hood, pans hung on a rail.
    box(160, FLOOR - 34, 226, FLOOR - 1, SLATE)
    r(162, FLOOR - 36, 224, FLOOR - 34, DARK)
    for x in (166, 186, 206):
        r(x, FLOOR - 26, x + 12, FLOOR - 20, DARK)
        d.ellipse([x + 3, FLOOR - 25, x + 9, FLOOR - 21], fill=ORANGE)
    box(170, FLOOR - 52, 188, FLOOR - 37, GREY)
    r(168, FLOOR - 53, 190, FLOOR - 51, PALE)
    for x, y in ((174, 62), (180, 66), (177, 71)):
        d.ellipse([x, FLOOR - y, x + 4, FLOOR - y + 3], fill=WHITE)
    d.polygon([(156, 22), (230, 22), (220, 36), (166, 36)], fill=GREY, outline=INK)
    r(160, 44, 226, 45, DARK)
    for x, w in ((196, 10), (210, 12)):
        r(x + w // 2, 45, x + w // 2, 50, DARK)
        d.ellipse([x, 50, x + w, 50 + w], fill=WOOD_DARK, outline=INK)
    # Flour sacks heaped by the wall (her soft landing from the trap door, at 200... the heap is at 240).
    R.sack(232, FLOOR - 1, w=22, h=16, fill=CREAM)
    R.sack(250, FLOOR - 1, w=22, h=16)
    R.sack(240, FLOOR - 15, w=22, h=14, fill=CREAM)
    # The trap door's shaft in the ceiling over them.
    box(232, 8, 268, 16, DARK)
    r(234, 14, 266, 16, INK)
    # A rack of ladles and a clock at the far end.
    r(290, 40, 326, 41, DARK)
    for x in range(294, 326, 8):
        r(x, 41, x, 54, GREY)
        d.ellipse([x - 2, 54, x + 2, 58], fill=GREY)
    d.ellipse([300, 20, 314, 34], fill=WHITE, outline=INK)
    r(307, 24, 307, 27, INK)
    r(307, 27, 310, 27, INK)
    # Its door is at its aft end (the deck's last metres are structure): the whole room is mirrored.
    R.im = R.im.transpose(Image.FLIP_LEFT_RIGHT)
    return R.save("galley")


# --- Region 2's rooms (deck 6, the boat walkway) ----------------------------------------------------

def maid6(width):
    """A cabin being made up, deck 6 (population: `amb_maid`): the bed half made, a towel swan on it,
    the curtains open on the sea, a guest's suitcase on the rack. The stewardess stands at the bed's
    foot (150)."""
    R = Room(width, "#e6dcc8", "#d8cdb8", ceiling=CREAM, skirting=WOOD, floor="#0b8a8f", fleck=TEAL, pitch=240)
    r, box, d = R.r, R.box, R.d
    r(100, 5, 128, 8, CREAM_SHADE)
    r(104, 8, 124, 9, TUBE)
    R.door(frame="door-cabin-ajar")
    # The window on the sea, its curtains drawn back.
    box(176, 34, 226, 72, BLUE_LIGHT)
    r(177, 56, 225, 71, BLUE)
    r(177, 55, 225, 55, WHITE)
    for x in (184, 204, 215):
        r(x, 61 + x % 5, x + 5, 61 + x % 5, BLUE_LIGHT)
    r(200, 35, 201, 71, CREAM)
    for x0, x1 in ((168, 180), (222, 234)):
        box(x0, 30, x1, 78, MAUVE)
        r(x0 + 3, 32, x0 + 3, 76, PINK)
        r(x0 + 8, 32, x0 + 8, 76, "#6b3e75")
    r(164, 28, 238, 30, WOOD_DARK)
    # The luggage rack by the door, a suitcase on it; a picture over it.
    stand(R.im, "luggage-rack", 104)
    stand(R.im, "suitcase", 104, dy=20)
    stand(R.im, "picture-sea", 110, dy=74)
    # The bed, its foot toward the door: the duvet folded back half way, pillows, the towel swan.
    box(160, FLOOR - 13, 236, FLOOR - 1, WOOD_DARK)
    box(228, FLOOR - 40, 236, FLOOR - 1, WOOD)
    box(160, FLOOR - 21, 229, FLOOR - 13, WHITE)
    r(161, FLOOR - 14, 228, FLOOR - 14, PALE)
    box(160, FLOOR - 24, 196, FLOOR - 19, BLUE_LIGHT)
    r(161, FLOOR - 20, 195, FLOOR - 20, BLUE)
    d.rounded_rectangle([211, FLOOR - 28, 228, FLOOR - 21], radius=3, fill=WHITE, outline=GREY)
    d.rounded_rectangle([214, FLOOR - 33, 228, FLOOR - 27], radius=3, fill=PALE, outline=GREY)
    stand(R.im, "towel-swan", 190, dy=21)
    # A bedside lamp on the wall over the pillows; fresh towels folded on a stool by the bed's foot.
    r(224, FLOOR - 62, 232, FLOOR - 55, YELLOW)
    r(227, FLOOR - 55, 229, FLOOR - 50, WOOD_DARK)
    box(126, FLOOR - 16, 142, FLOOR - 13, WOOD)
    for x in (128, 139):
        r(x, FLOOR - 13, x + 1, FLOOR - 1, WOOD_DARK)
    for k in range(3):
        d.rounded_rectangle([128, FLOOR - 21 - k * 4, 140, FLOOR - 17 - k * 4], radius=1, fill=(WHITE, BLUE_LIGHT, WHITE)[k], outline=GREY)
    return R.save("maid6")


def lifeboat(width):
    """Inside the one lifeboat whose hatch is open, on the boat walkway (population: `room_lifeboat`):
    the orange hull's ribs, a bench with harnesses along its side, an oar in its brackets, portholes
    on the sea, life jackets, a ration box; the second book lies on the bench (112, 17 px up), the
    photo slot hangs between the portholes (184)."""
    R = Room(width, "#f79617", "#cd683d", ceiling="#fbb954", skirting="#cd683d", floor=GREY, fleck=SLATE, pitch=30)
    r, box, d = R.r, R.box, R.d
    # The hull closes in at both ends: dark rounded corners under the canopy.
    for x0, x1, a0, a1 in ((-40, 40, 180, 270), (width - 41, width + 39, 270, 360)):
        d.pieslice([x0, 8, x1, 88], a0, a1, fill="#fbb954")
    r(0, 9, 3, FLOOR - 5, "#cd683d")
    r(width - 4, 9, width - 1, FLOOR - 5, "#cd683d")
    # A grab line along the canopy, a lamp in its cage.
    r(20, 14, width - 21, 14, WHITE)
    for x in range(24, width - 20, 30):
        r(x, 12, x, 16, GREY)
    box(114, 9, 126, 15, DARK)
    r(116, 11, 124, 13, TUBE)
    R.door(frame="door-watertight")
    # Portholes on the sea.
    for x in (96, 150, 218):
        d.ellipse([x - 9, 34, x + 9, 52], fill=DARK, outline=INK)
        d.ellipse([x - 7, 36, x + 7, 50], fill=BLUE_LIGHT)
        d.chord([x - 7, 36, x + 7, 50], 10, 170, fill=BLUE)
        r(x - 5, 41, x - 2, 41, WHITE)
    # The oar in its brackets over the bench: the shaft, a red-tipped blade.
    r(88, 66, 176, 68, WOOD)
    r(88, 68, 176, 68, WOOD_DARK)
    box(176, 62, 204, 72, WOOD_LIGHT)
    r(198, 63, 203, 71, RED)
    for x in (104, 160):
        r(x, 63, x + 2, 72, DARK)
    # The bench along the side, 17 px up, harness straps hung over it.
    box(84, FLOOR - 17, 236, FLOOR - 13, PALE)
    box(86, FLOOR - 13, 234, FLOOR - 1, STEEL_SHADE)
    for x in range(100, 232, 28):
        r(x, FLOOR - 12, x, FLOOR - 2, GREY)
    for x in (100, 156, 212):
        r(x, FLOOR - 44, x + 1, FLOOR - 18, SLATE)
        r(x + 7, FLOOR - 44, x + 8, FLOOR - 18, SLATE)
        r(x, FLOOR - 32, x + 8, FLOOR - 30, SLATE)
        r(x + 3, FLOOR - 33, x + 5, FLOOR - 29, YELLOW)
    # A life jacket on its hook, the ration box and a water can on the bench's end.
    stand(R.im, "life-jacket", 72 + 104, dy=17)
    box(214, FLOOR - 29, 232, FLOOR - 17, WHITE)
    r(221, FLOOR - 26, 225, FLOOR - 20, RED)
    r(219, FLOOR - 24, 227, FLOOR - 22, RED)
    box(140, FLOOR - 27, 150, FLOOR - 17, BLUE)
    r(143, FLOOR - 30, 147, FLOOR - 27, WHITE)
    return R.save("lifeboat")


# --- Region 3's rooms (the theatre) ------------------------------------------------------------------

def dressing(width):
    """The dressing room behind the stage door, deck 6 (population: `room_dressing`): a make-up table
    under a mirror ringed with bulbs (the third book lies on it, 118, 31 px up), a stool, costumes on
    a rail, hat boxes, wig stands on a shelf, a star on the wall."""
    R = Room(width, "#f6c0a0", "#e9a58c", ceiling=CREAM, skirting=WOOD_DARK, floor="#905ea9", fleck="#6b3e75", pitch=240)
    r, box, d = R.r, R.box, R.d
    r(100, 5, 128, 8, CREAM_SHADE)
    r(104, 8, 124, 9, TUBE)
    R.door()
    # The mirror, bulbs all round it.
    box(92, 30, 146, 78, WOOD_DARK)
    box(98, 36, 140, 72, BLUE_LIGHT)
    r(100, 38, 112, 70, WHITE)
    d.line([(116, 70), (132, 38)], fill=WHITE)
    for x in range(95, 146, 8):
        for y in (33, 75):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=TUBE, outline=ORANGE)
    for y in range(41, 72, 8):
        for x in (95, 143):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=TUBE, outline=ORANGE)
    # The table under it, 30 px up: brushes in a pot, powder, a lipstick; a stool.
    box(90, FLOOR - 30, 148, FLOOR - 27, WOOD)
    for x in (92, 145):
        r(x, FLOOR - 27, x + 1, FLOOR - 1, WOOD_DARK)
    box(94, FLOOR - 26, 112, FLOOR - 16, WOOD_LIGHT)
    r(102, FLOOR - 22, 104, FLOOR - 21, WOOD_DARK)
    box(94, FLOOR - 37, 100, FLOOR - 31, PINK)
    for x, c in ((95, WOOD_DARK), (97, DARK), (99, WOOD)):
        r(x, FLOOR - 43, x, FLOOR - 37, c)
    d.ellipse([132, FLOOR - 35, 142, FLOOR - 30], fill=WHITE, outline=GREY)
    r(127, FLOOR - 36, 128, FLOOR - 31, RED)
    stand(R.im, "velvet-stool", 164)
    # Costumes on a rail, hat boxes under them, a feather boa over the rail's end.
    stand(R.im, "dress-rack", 206)
    for x, c, w in ((186, MAUVE, 16), (204, YELLOW, 14)):
        d.rounded_rectangle([x, FLOOR - 12, x + w, FLOOR - 1], radius=2, fill=c, outline=INK)
        r(x, FLOOR - 9, x + w, FLOOR - 8, WHITE)
    for k in range(7):
        d.ellipse([228 + (k % 2) * 3, FLOOR - 50 + k * 5, 233 + (k % 2) * 3, FLOOR - 45 + k * 5], fill=PINK)
    # A shelf of wig stands, and a gold star on the wall.
    r(160, 44, 196, 46, WOOD)
    r(160, 46, 196, 46, WOOD_DARK)
    for x, c in ((164, ORANGE), (176, YELLOW), (188, NAVY)):
        d.ellipse([x - 4, 30, x + 4, 40], fill=c, outline=INK)
        d.ellipse([x - 3, 34, x + 3, 42], fill=WOOD_LIGHT)
        r(x - 1, 42, x + 1, 44, WOOD_LIGHT)
    d.polygon([(214, 22), (217, 29), (224, 29), (219, 34), (221, 41), (214, 37), (207, 41), (209, 34), (204, 29), (211, 29)], fill=YELLOW, outline=ORANGE)
    R.poster(20, 34, 22, 30, [RED, YELLOW, WHITE])
    return R.save("dressing")


def lighting(width):
    """The lighting booth and the catwalk over the stage, deck 7 (population: `room_lighting`): the
    console under a window on the stage, then out through a frame onto the catwalk in the flies:
    lamps on a bar, ropes and sandbags, the hatch in the ceiling Bumbot went through, and a photo
    slot at its far end (446)."""
    R = Room(width, "#3e3546", "#2e222f", ceiling=DARK, skirting=SLATE, floor=SLATE, fleck=DARK, pitch=48)
    r, box, d = R.r, R.box, R.d
    r(96, 5, 124, 8, SLATE)
    r(100, 8, 120, 9, "#f9c22b")
    R.door()
    # The window on the stage: far below, the boards lit, the red curtains.
    box(88, 28, 200, 70, INK)
    r(90, 30, 198, 68, "#1b1828")
    r(90, 58, 198, 68, WOOD_DARK)
    r(90, 58, 198, 59, WOOD)
    r(90, 30, 100, 68, RED)
    r(188, 30, 198, 68, RED)
    d.polygon([(150, 30), (136, 58), (164, 58)], fill="#4a4460")
    d.ellipse([138, 56, 162, 62], fill=TUBE)
    r(144, 30, 144, 68, INK)
    # The console: faders, lit keys, two screens; the operator's chair.
    box(86, FLOOR - 34, 202, FLOOR - 28, GREY)
    box(90, FLOOR - 28, 198, FLOOR - 1, SLATE)
    for x in range(94, 160, 6):
        r(x, FLOOR - 33, x + 1, FLOOR - 30, INK)
        r(x - 1, FLOOR - 33 + (x * 7) % 3, x + 2, FLOOR - 32 + (x * 7) % 3, (RED, YELLOW, GREEN, BLUE_LIGHT)[(x // 6) % 4])
    for x, c in ((166, GREEN), (172, RED), (178, YELLOW), (184, BLUE)):
        r(x, FLOOR - 32, x + 3, FLOOR - 30, c)
    for x in (100, 128):
        box(x, FLOOR - 52, x + 22, FLOOR - 36, INK)
        r(x + 2, FLOOR - 50, x + 20, FLOOR - 38, TEAL)
        r(x + 4, FLOOR - 47, x + 14, FLOOR - 46, GREEN)
        r(x + 4, FLOOR - 43, x + 17, FLOOR - 42, GREEN)
        r(x + 10, FLOOR - 36, x + 12, FLOOR - 34, INK)
    stand(R.im, "office-chair", 176)
    # Out onto the catwalk: a frame, and beyond it the dark of the flies.
    r(232, 9, width - 1, FLOOR - 1, "#1b1828")
    box(228, 9, 236, FLOOR - 1, SLATE)
    r(230, 9, 233, FLOOR - 1, GREY)
    # The catwalk: a grating to walk on, a handrail on posts.
    r(236, FLOOR, width - 1, FLOOR + 3, GREY)
    for x in range(238, width, 4):
        r(x, FLOOR, x, FLOOR + 3, DARK)
    r(236, FLOOR + 4, width - 1, H - 1, "#1b1828")
    for x in range(240, width, 40):
        r(x, FLOOR + 4, x + 1, H - 1, SLATE)
    r(236, FLOOR - 34, width - 1, FLOOR - 33, GREY)
    r(236, FLOOR - 18, width - 1, FLOOR - 18, SLATE)
    for x in range(250, width, 36):
        r(x, FLOOR - 34, x + 1, FLOOR - 1, GREY)
    # A bar of lamps overhead, their beams falling to the stage.
    r(244, 16, width - 12, 17, GREY)
    for x, c in ((262, YELLOW), (300, PINK), (338, BLUE_LIGHT)):
        r(x + 3, 17, x + 4, 22, GREY)
        box(x, 22, x + 9, 31, INK)
        r(x + 2, 31, x + 7, 32, c)
        d.polygon([(x + 2, 33), (x + 7, 33), (x + 16, FLOOR - 35), (x - 7, FLOOR - 35)], fill="#2c2840")
    # Ropes and sandbags.
    for x, y in ((372, 70), (384, 54)):
        r(x, 9, x, y, WOOD)
        d.rounded_rectangle([x - 4, y, x + 4, y + 12], radius=3, fill=WOOD_LIGHT, outline=INK)
    # The hatch in the ceiling he went through: open, its lid hanging, a rope up into it.
    box(404, 8, 430, 14, INK)
    r(406, 9, 428, 13, "#0d0b14")
    r(430, 9, 432, 30, SLATE)
    r(416, 13, 416, 46, WOOD)
    d.ellipse([413, 46, 419, 54], outline=WOOD)
    return R.save("lighting")


DRAW = {"laundry": laundry, "store": store, "smcabin": smcabin, "pantry": pantry, "galley": galley,
        "maid6": maid6, "lifeboat": lifeboat, "dressing": dressing, "lighting": lighting}


def main():
    argv = sys.argv[1:]
    preview = argv[argv.index("--preview") + 1] if "--preview" in argv else None
    args = [a for a in argv if not a.startswith("--") and a != preview]
    widths = {r["id"]: r["width"] for r in ROOMS}
    done = []
    for name, fn in DRAW.items():
        if args and name not in args:
            continue
        done.append((name, fn(widths[name])))
        print("wrote", (OUT / f"{name}.png").relative_to(ROOT))
    if preview:
        out = preview
        sheet = Image.new("RGBA", (max(im.width for _, im in done), H * len(done) + 4 * len(done)), "#1a141c")
        for i, (_, im) in enumerate(done):
            sheet.alpha_composite(im, (0, i * (H + 4)))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(out)


if __name__ == "__main__":
    main()
