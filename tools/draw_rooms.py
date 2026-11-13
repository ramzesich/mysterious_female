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
        """Snapped to the palette, but for the colours in `keep` (a passenger cabin's cream wall, which
        is the corridors' and cabin 8206's, and is not in the palette)."""
        OUT.mkdir(parents=True, exist_ok=True)
        out = palettize(self.im)
        keep = {tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in getattr(self, "keep", ())}
        if keep:
            src, dst = self.im.load(), out.load()
            for y in range(out.height):
                for x in range(out.width):
                    if src[x, y][:3] in keep:
                        dst[x, y] = src[x, y]
        out.save(OUT / f"{name}.png")
        return out


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


# --- Region 4's rooms (deck 9's cabins) --------------------------------------------------------------
# Passenger cabins in cabin 8206's colours (tools/draw_cabin.py): cream panels under a wood cornice,
# grey carpet, wood furniture, teal runners.

CAB_WALL, CAB_SEAM = "#ece3cf", "#ddd2bb"
CAB_WOOD, CAB_WOOD_DARK, CAB_WOOD_LIGHT = "#cd683d", "#9e4539", "#e6904e"
CAB_TEAL, CAB_TEAL_LIGHT = "#0b5e65", "#0b8a8f"
BED_UP = 32                 # a made bed's top over the floor


def cabin_room(width, lights):
    R = Room(width, CAB_WALL, CAB_SEAM, ceiling="#f6f3ec", skirting=GREY, floor="#9babb2", fleck="#7f708a", pitch=48)
    R.r(0, 6, width - 1, 7, CAB_WOOD)
    R.r(0, 8, width - 1, 8, CAB_WOOD_DARK)
    R.r(0, FLOOR - 4, width - 1, FLOOR - 4, SLATE)
    for x in lights:
        R.r(x - 3, 5, x + 3, 5, TUBE)
    R.keep = (CAB_WALL, CAB_SEAM, "#f6f3ec")
    return R


def cabin_door(R, x):
    """A cabin door's inside face: wood, a lever, the escape plan."""
    r, x0, top = R.r, x - 14, FLOOR - 80
    r(x0, top, x0 + 28, FLOOR - 5, CAB_WOOD_DARK)
    r(x0 + 2, top + 2, x0 + 26, FLOOR - 5, CAB_WOOD)
    r(x0 + 3, top + 3, x0 + 3, FLOOR - 6, CAB_WOOD_LIGHT)
    r(x0 + 8, top + 12, x0 + 20, top + 28, WHITE)
    r(x0 + 9, top + 14, x0 + 19, top + 14, GREEN)
    R.d.line([(x0 + 10, top + 18), (x0 + 18, top + 24)], fill=GREEN)
    r(x0 + 21, top + 40, x0 + 25, top + 41, GREY)


def bed(R, x0, x1, head=1, made=True, runner=CAB_TEAL):
    """A bed side on, its headboard at the `head` end (1: aft, right): the base, the mattress, the
    duvet falling toward the floor, pillows, a runner across its foot. Unmade: the bare mattress."""
    r, d, box = R.r, R.d, R.box
    hx = x1 if head > 0 else x0
    box(min(hx, hx - head * 6), FLOOR - 50, max(hx, hx - head * 6), FLOOR - 1, CAB_WOOD, CAB_WOOD_DARK)
    a, b = (x0, x1 - 7) if head > 0 else (x0 + 7, x1)
    box(a, FLOOR - 12, b, FLOOR - 1, CAB_WOOD_DARK, INK)
    if made:
        d.rounded_rectangle([a - 1, FLOOR - BED_UP, b, FLOOR - 4], radius=3, fill=WHITE, outline=GREY)
        r(a, FLOOR - 24, b - 1, FLOOR - 24, PALE)
        fx = a + 8 if head > 0 else b - 22
        r(fx, FLOOR - BED_UP, fx + 14, FLOOR - 5, runner)
        for y in range(FLOOR - BED_UP + 3, FLOOR - 7, 5):
            d.line([(fx + 2, y + 2), (fx + 7, y), (fx + 12, y + 2)], fill=CAB_TEAL_LIGHT)
        px = b - 22 if head > 0 else a + 4
        d.rounded_rectangle([px, FLOOR - BED_UP - 7, px + 18, FLOOR - BED_UP], radius=3, fill=WHITE, outline=GREY)
    else:
        box(a, FLOOR - 26, b, FLOOR - 12, "#f2f6f6", GREY)
        for x in range(a + 4, b - 2, 6):
            r(x, FLOOR - 25, x, FLOOR - 13, BLUE_LIGHT)
        r(a + 1, FLOOR - 19, b - 1, FLOOR - 19, PALE)


def wall_lamp(R, x, y):
    R.r(x - 4, y, x + 4, y + 6, YELLOW)
    R.r(x - 3, y + 7, x + 3, y + 7, ORANGE)
    R.r(x - 1, y + 8, x + 1, y + 11, CAB_WOOD_DARK)


def picture(R, x, y, w, h, colours):
    R.box(x, y, x + w, y + h, CAB_WOOD_LIGHT, CAB_WOOD_DARK)
    R.r(x + 2, y + 2, x + w - 2, y + h - 2, colours[0])
    R.r(x + 2, y + h // 2, x + w - 2, y + h - 2, colours[1])
    R.d.ellipse([x + w - 9, y + 4, x + w - 5, y + 8], fill=colours[2])


def desk(R, x0, x1, up=26):
    """A wood desk with a drawer, and a stool pushed under it."""
    r, box = R.r, R.box
    box(x0, FLOOR - up, x1, FLOOR - up + 3, CAB_WOOD, CAB_WOOD_DARK)
    box(x0 + 2, FLOOR - up + 3, x0 + 18, FLOOR - 1, CAB_WOOD, CAB_WOOD_DARK)
    r(x0 + 8, FLOOR - up + 8, x0 + 12, FLOOR - up + 9, CAB_WOOD_LIGHT)
    r(x1 - 2, FLOOR - up + 3, x1 - 1, FLOOR - 1, CAB_WOOD_DARK)
    box(x0 + 24, FLOOR - 14, x1 - 6, FLOOR - 11, CAB_TEAL, INK)
    for x in (x0 + 26, x1 - 9):
        r(x, FLOOR - 11, x + 1, FLOOR - 1, CAB_WOOD_DARK)


def wardrobe(R, x0, x1, open_=False):
    r, box = R.r, R.box
    box(x0, FLOOR - 92, x1, FLOOR - 5, CAB_WOOD, CAB_WOOD_DARK)
    mid = (x0 + x1) // 2
    if open_:
        r(x0 + 2, FLOOR - 90, x1 - 2, FLOOR - 7, "#45293f")
        r(x0 + 2, FLOOR - 82, x1 - 2, FLOOR - 81, GREY)
        for x, c in ((x0 + 5, WHITE), (x0 + 10, BLUE_LIGHT), (x0 + 15, WHITE)):
            r(x, FLOOR - 80, x + 3, FLOOR - 52, c)
            r(x + 1, FLOOR - 84, x + 1, FLOOR - 81, GREY)
        box(x0 + 4, FLOOR - 22, x1 - 4, FLOOR - 8, ORANGE, INK)           # the life jackets' box
    else:
        r(mid, FLOOR - 90, mid, FLOOR - 7, CAB_WOOD_DARK)
        r(x0 + 3, FLOOR - 88, mid - 3, FLOOR - 9, "#d9e6e2")
        R.d.line([(x0 + 5, FLOOR - 60), (mid - 6, FLOOR - 84)], fill=WHITE)
        r(mid + 3, FLOOR - 50, mid + 4, FLOOR - 42, GREY)


def cleanup(width):
    """The cabin mid-cleanup, deck 9 (population: `room_cleanup`), an inside cabin with its door held
    open: the bed stripped to its mattress, the sheets in a heap, the pillows piled on the chair, the
    wardrobe open, the housekeeping trolley in the middle of the room, a spray bottle and a bucket.
    The bedmaker shakes out a sheet at the bed's foot (176); the robot vacuum's dock by the door."""
    R = cabin_room(width, (60, 130, 200))
    r, box, d = R.r, R.box, R.d
    cabin_door(R, DOOR_X)
    # The vacuum's dock by the door: a low grey wedge, a green light.
    box(22, FLOOR - 7, 38, FLOOR - 1, SLATE)
    r(24, FLOOR - 5, 26, FLOOR - 4, GREEN)
    wardrobe(R, 80, 108, open_=True)
    picture(R, 122, 36, 30, 22, (BLUE_LIGHT, BLUE, WHITE))
    stand(R.im, "towel-trolley", 132)
    # A bucket and a spray bottle.
    box(150, FLOOR - 11, 159, FLOOR - 1, BLUE, INK)
    r(151, FLOOR - 13, 158, FLOOR - 12, GREY)
    r(163, FLOOR - 9, 166, FLOOR - 1, PINK)
    r(163, FLOOR - 12, 167, FLOOR - 10, WHITE)
    # The stripped bed, the old sheets heaped at its foot on the floor; the wall lamp over its head.
    bed(R, 186, 236, made=False)
    d.rounded_rectangle([176, FLOOR - 9, 198, FLOOR], radius=4, fill=WHITE, outline=GREY)
    d.rounded_rectangle([170, FLOOR - 5, 186, FLOOR], radius=3, fill="#f2f6f6", outline=GREY)
    d.line([(180, FLOOR - 6), (192, FLOOR - 4)], fill=PALE)
    for k in range(3):                                                    # the pillows, piled on the bed's head
        d.rounded_rectangle([210 - k, FLOOR - 33 - k * 6, 228 - k, FLOOR - 27 - k * 6], radius=3, fill=WHITE, outline=GREY)
    wall_lamp(R, 222, FLOOR - 70)
    return R.save("cleanup")


def balcabin9(width):
    """The balcony cabin, deck 9 (population: `room_balcabin_9`): a mirrored wardrobe, the desk with
    the fruit basket (its tangerine at 150, 30 px up), the bed with a towel swan on it, and the glass
    door onto the balcony (262): sea and sky in it, the curtains drawn back."""
    R = cabin_room(width, (60, 150, 230))
    r, box, d = R.r, R.box, R.d
    cabin_door(R, DOOR_X)
    wardrobe(R, 82, 110)
    # The desk under a mirror, the fruit basket on it (the tangerine lies in the basket).
    box(128, 34, 172, 66, CAB_WOOD_LIGHT, CAB_WOOD_DARK)
    r(131, 37, 169, 63, "#d9e6e2")
    d.line([(134, 60), (150, 40)], fill=WHITE)
    desk(R, 126, 176)
    box(142, FLOOR - 31, 158, FLOOR - 26, WOOD, INK)
    for x in range(144, 158, 3):
        r(x, FLOOR - 30, x, FLOOR - 27, WOOD_DARK)
    d.ellipse([139, FLOOR - 33, 144, FLOOR - 28], fill=GREEN, outline=INK)
    d.ellipse([155, FLOOR - 34, 161, FLOOR - 28], fill=RED, outline=INK)
    r(164, FLOOR - 36, 166, FLOOR - 27, CAB_TEAL)                          # a bottle of water
    r(164, FLOOR - 38, 166, FLOOR - 37, WHITE)
    # The bed, its head forward so the pillows are away from the glass; a towel swan on the duvet.
    bed(R, 184, 236, head=-1)
    stand(R.im, "towel-swan", 220, dy=BED_UP)
    wall_lamp(R, 194, FLOOR - 70)
    picture(R, 204, 34, 26, 20, (YELLOW, ORANGE, WHITE))
    # The balcony door: floor-to-ceiling glass in a white frame, sky, sea, the rail outside.
    box(240, FLOOR - 86, 284, FLOOR - 1, WHITE, GREY)
    r(243, FLOOR - 83, 281, FLOOR - 2, BLUE_LIGHT)
    r(243, FLOOR - 40, 281, FLOOR - 2, BLUE)
    r(243, FLOOR - 41, 281, FLOOR - 41, WHITE)
    for x, y in ((250, FLOOR - 30), (266, FLOOR - 22), (274, FLOOR - 33)):
        r(x, y, x + 5, y, BLUE_LIGHT)
    d.ellipse([248, FLOOR - 76, 262, FLOOR - 70], fill=WHITE)
    d.ellipse([256, FLOOR - 79, 272, FLOOR - 71], fill=WHITE)
    r(243, FLOOR - 34, 281, FLOOR - 33, WHITE)                             # the balcony's rail
    for x in range(246, 282, 9):
        r(x, FLOOR - 33, x, FLOOR - 2, WHITE)
    r(261, FLOOR - 83, 262, FLOOR - 2, WHITE)
    r(258, FLOOR - 46, 259, FLOOR - 38, GREY)                              # the handle
    r(236, FLOOR - 90, 286, FLOOR - 88, GREY)                              # the curtain rail
    for x0 in (236, 281):
        box(x0, FLOOR - 88, x0 + 6, FLOOR - 3, "#7f708a", SLATE)
        r(x0 + 3, FLOOR - 86, x0 + 3, FLOOR - 5, SLATE)
    return R.save("balcabin9")


def adjoin(width):
    """Two adjoining inside cabins, deck 9 (population: `room_adjoin`): a family's. The parents' (in
    at 59): a made bed, a desk, suitcases. The connecting door in the wall between them stands open
    (216). The children's (out at 373): two beds end to end and, across the way through, a blanket
    fort (232-300, crawl): sheets pegged over two chairs, a torch glowing inside, a teddy on guard."""
    R = cabin_room(width, (60, 150, 280, 372))
    r, box, d = R.r, R.box, R.d
    cabin_door(R, DOOR_X)
    cabin_door(R, width - DOOR_X)
    # The parents' cabin.
    wardrobe(R, 82, 108)
    stand(R.im, "luggage-rack", 128)
    stand(R.im, "suitcases", 128, dy=20)
    picture(R, 118, 34, 26, 20, (BLUE_LIGHT, GREEN, WHITE))
    bed(R, 150, 204, runner=RED)
    wall_lamp(R, 192, FLOOR - 70)
    # The wall between the cabins, seen end on, its doorway open; the door's leaf swung back flat
    # against the children's wall.
    box(213, 9, 219, FLOOR - 80, CAB_WALL, CAB_SEAM)
    r(213, FLOOR - 81, 219, FLOOR - 80, CAB_WOOD_DARK)
    box(220, FLOOR - 79, 228, FLOOR - 5, CAB_WOOD, CAB_WOOD_DARK)
    r(226, FLOOR - 42, 227, FLOOR - 36, GREY)
    # The children's cabin: drawings taped to the wall, a bed, toys.
    for x, y, c in ((246, 30, PINK), (262, 36, YELLOW), (278, 28, BLUE_LIGHT)):
        box(x, y, x + 12, y + 14, WHITE, GREY)
        d.ellipse([x + 3, y + 3, x + 9, y + 9], fill=c)
        r(x + 5, y - 1, x + 7, y, RED)
    wall_lamp(R, 326, FLOOR - 70)
    bed(R, 306, 346, head=-1, runner=ORANGE)
    d.ellipse([350, FLOOR - 9, 358, FLOOR - 1], fill=RED, outline=INK)     # a ball
    r(351, FLOOR - 6, 357, FLOOR - 5, WHITE)
    box(392, FLOOR - 26, 414, FLOOR - 1, CAB_WOOD, CAB_WOOD_DARK)          # a toy chest
    r(393, FLOOR - 18, 413, FLOOR - 18, CAB_WOOD_DARK)
    d.ellipse([398, FLOOR - 34, 408, FLOOR - 26], fill=YELLOW, outline=INK)  # a rubber duck on it
    r(407, FLOOR - 31, 410, FLOOR - 30, ORANGE)
    # (The blanket fort across the way through is a picture of its own, in front of her: `fort()`.)
    fort()
    return R.save("adjoin")


def fort():
    """The children's blanket fort (the adjoining cabins, 232-302): sheets pegged over two chairs, down
    to the floor, a way in at each end; a torch glows through the cloth, a teddy keeps guard on top
    under a crayon notice. Drawn in front of her: she crawls through behind the sheet.
    assets/ship/rooms/adjoin-fort.png, 76 x 76, its foot on the floor."""
    W2, H2 = 76, 76
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    B2 = H2 - 1
    # The chairs' backs, standing up through the sheet at each end.
    for x in (6, 66):
        d.rectangle([x, B2 - 46, x + 3, B2], fill=CAB_WOOD, outline=CAB_WOOD_DARK)
    # The sheet: a white one and a blue one, sagging between the chairs, flaps held open at the ends.
    d.polygon([(2, B2), (6, B2 - 46), (38, B2 - 40), (38, B2)], fill="#f2f6f6", outline=GREY)
    d.polygon([(38, B2), (38, B2 - 40), (69, B2 - 46), (73, B2)], fill=BLUE_LIGHT, outline=GREY)
    for x in range(42, 70, 7):
        d.line([(x, B2 - 40 - (x - 38) // 6), (x + 1, B2 - 1)], fill=BLUE)
    for x in range(10, 36, 9):
        d.line([(x, B2 - 44 + (x - 6) // 6), (x - 1, B2 - 1)], fill=PALE)
    # The torch inside, glowing through the cloth.
    d.ellipse([26, B2 - 26, 50, B2 - 6], fill="#fbff86")
    d.ellipse([31, B2 - 22, 45, B2 - 10], fill=WHITE)
    # The ways in: dark flaps at the ends.
    d.polygon([(2, B2), (5, B2 - 24), (13, B2)], fill="#3e3546")
    d.polygon([(73, B2), (70, B2 - 24), (62, B2)], fill="#3e3546")
    # Clothes pegs along the ridge; the teddy; the notice.
    for x in (12, 62):
        d.rectangle([x, B2 - 49, x + 1, B2 - 44], fill=RED)
    d.ellipse([32, B2 - 54, 44, B2 - 40], fill=WOOD, outline=INK)
    d.ellipse([34, B2 - 63, 42, B2 - 53], fill=WOOD, outline=INK)
    for x in (34, 41):
        d.ellipse([x - 1, B2 - 65, x + 2, B2 - 62], fill=WOOD, outline=INK)
    d.point((36, B2 - 58), fill=INK)
    d.point((40, B2 - 58), fill=INK)
    d.rectangle([37, B2 - 56, 39, B2 - 55], fill=WOOD_LIGHT)
    d.rectangle([16, B2 - 36, 30, B2 - 28], fill=WHITE, outline=INK)
    d.line([(18, B2 - 34), (28, B2 - 34)], fill=RED)
    d.line([(18, B2 - 31), (25, B2 - 31)], fill=RED)
    palettize(im).save(OUT / "adjoin-fort.png")
    return im


def peeks():
    """What shows under the duct's grilles as she crawls over them (population: `scn_duct`): the
    midship lobby's chandelier, the atrium's glass dome, a cabin full of balloons, a passenger
    snoring. Small pictures, assets/ship/peeks/<what>.png, each as if looked down into."""
    out = ROOT / "assets" / "ship" / "peeks"
    out.mkdir(parents=True, exist_ok=True)
    W2, H2 = 64, 44

    def card(bg):
        im = Image.new("RGBA", (W2, H2), bg)
        return im, ImageDraw.Draw(im)

    # The lobby: warm light, the chandelier from above, the carpet's pattern, two heads going by.
    im, d = card("#7a3045")
    for x in range(-8, W2, 16):
        d.polygon([(x, 30), (x + 8, 22), (x + 16, 30), (x + 8, 38)], outline="#ae2334")
    d.ellipse([18, 4, 46, 26], fill="#f9c22b", outline=INK)
    d.ellipse([23, 8, 41, 22], fill=TUBE)
    for a in range(8):
        x, y = 32 + round(12 * __import__("math").cos(a * 0.785)), 15 + round(9 * __import__("math").sin(a * 0.785))
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=WHITE, outline="#d9a43b")
    for x, c in ((10, "#3e3546"), (52, "#cd683d")):
        d.ellipse([x - 4, 30, x + 4, 38], fill=c, outline=INK)
        d.ellipse([x - 6, 36, x + 6, 46], fill=WHITE if x < 30 else "#4d9be6", outline=INK)
    palettize(im).save(out / "lobby.png")

    # The dome: the atrium's skylight from above its rim: blue glass ribs, the sun in it.
    im, d = card("#323353")
    d.ellipse([4, -20, 60, 40], fill="#4d9be6", outline=INK)
    d.ellipse([10, -14, 54, 34], fill="#8fd3ff")
    for x in (20, 32, 44):
        d.line([(32, -14), (x - (32 - x) // 2, 36)], fill=WHITE)
    for y in (4, 16, 28):
        d.arc([10 - (y // 3), y - 14, 54 + (y // 3), y + 10], 20, 160, fill=WHITE)
    d.ellipse([38, 2, 48, 12], fill=TUBE)
    d.rectangle([0, 38, W2, H2], fill="#d9a43b")
    d.rectangle([0, 38, W2, 38], fill=INK)
    palettize(im).save(out / "dome.png")

    # The party: a cabin's ceiling full of balloons, streamers, a paper garland.
    im, d = card("#45293f")
    for x, y, c in ((10, 12, RED), (24, 8, YELLOW), (38, 14, BLUE), (52, 9, GREEN), (16, 26, PINK), (32, 28, ORANGE), (48, 27, MAUVE)):
        d.ellipse([x - 7, y - 8, x + 7, y + 8], fill=c, outline=INK)
        d.ellipse([x - 4, y - 5, x - 1, y - 2], fill=WHITE)
        d.line([(x, y + 8), (x + 1, y + 16)], fill=WHITE)
    for x in range(0, W2, 8):
        d.polygon([(x, 36), (x + 8, 36), (x + 4, 43)], fill=(YELLOW, RED, BLUE_LIGHT, GREEN)[(x // 8) % 4])
    palettize(im).save(out / "balloons.png")

    # The snorer: a bed from above the pillow: a round face, eyes shut, a big moustache, his mouth
    # open; a z or two.
    im, d = card("#323353")
    d.rounded_rectangle([4, 8, 56, 44], radius=4, fill=WHITE, outline=INK)
    d.rounded_rectangle([10, 3, 50, 20], radius=5, fill="#f2f6f6", outline=GREY)
    d.rectangle([4, 28, 56, 44], fill="#4d65b4")
    d.rectangle([4, 28, 56, 29], fill=WHITE)
    d.ellipse([20, 5, 40, 27], fill="#e6904e", outline=INK)
    d.line([(24, 13), (27, 13)], fill=INK)
    d.line([(33, 13), (36, 13)], fill=INK)
    d.rectangle([23, 18, 37, 19], fill="#7a4528")
    d.rectangle([23, 20, 25, 20], fill="#7a4528")
    d.rectangle([35, 20, 37, 20], fill="#7a4528")
    d.ellipse([28, 20, 32, 24], fill=INK)
    for x, y, k in ((44, 12, 3), (50, 6, 4), (57, 0, 5)):
        d.line([(x, y), (x + k, y), (x, y + k), (x + k, y + k)], fill=TUBE)
    palettize(im).save(out / "snore.png")
    return ["lobby", "dome", "balloons", "snore"]


DRAW = {"laundry": laundry, "store": store, "smcabin": smcabin, "pantry": pantry, "galley": galley,
        "maid6": maid6, "lifeboat": lifeboat, "dressing": dressing, "lighting": lighting,
        "cleanup": cleanup, "balcabin9": balcabin9, "adjoin": adjoin}


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
    if not args:
        print("wrote the duct's peeks:", ", ".join(peeks()))
    if preview:
        out = preview
        sheet = Image.new("RGBA", (max(im.width for _, im in done), H * len(done) + 4 * len(done)), "#1a141c")
        for i, (_, im) in enumerate(done):
            sheet.alpha_composite(im, (0, i * (H + 4)))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(out)


if __name__ == "__main__":
    main()
