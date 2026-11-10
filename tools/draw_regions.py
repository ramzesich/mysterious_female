"""Draws the progression brainstorm (GAME_DESIGN.md §6.1, nothing decided) on the real ship: the regions in colour over the
game's own picture of the ship (`ship-full.png` from tools/render_ship.py), each deck stretched to
fit its labels, and the order they open in, one small ship a step. Re-run after editing the plan.

    python tools/render_ship.py
    python tools/draw_regions.py

Writes docs/ship-regions.png and docs/ship-unlock-order.png.
"""

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build_ship_map import floor_y, x_of
from ship_layout import EXTENT, LENGTH

ROOT = Path(__file__).resolve().parent.parent
FULL = Path(os.environ["TEMP"]) / "bumbusik-playtest" / "exterior" / "ship-full.png"
FONT = "C:/Windows/Fonts/arial.ttf"
FONT_B = "C:/Windows/Fonts/arialbd.ttf"

DECK_H = 144
TOP_WORLD = -335                           # over the funnel's pipes: above the map's top edge
BOTTOM_WORLD = floor_y(4) + 110            # a little hull and sea
FUNNEL_FA, FUNNEL_TOP = 8544, -228         # the funnel's fore edge and top, as buildFunnel() draws them


# Each region: its number, name, colour, and its pieces as (deck, from m, to m). Where the outside of
# the ship runs along a deck, its row is split: "outN" the outside half (deck 6's promenade, the
# balconies on decks 8-10), "inN" the inside half; "prom" and "rooms" are deck 6's two halves.
# (The user, 2026-11-10: the cabin decks were one long region of corridors. They are hallways
# now, opened from the balconies outside; only deck 9 midships, round the linen room, is a region.)
REGIONS = [
    (1, "Lower ship", (240, 190, 70), [
        (4, 20, 254), (5, 20, 254), (6, 20, 82)]),
    (2, "Atrium + promenade", (90, 200, 120), [
        (6, 82, 110), (7, 82, 110), ("prom", 110, 231)]),
    (3, "Showtime", (235, 95, 130), [
        ("rooms", 110, 231), (6, 231, 254), (7, 110, 254)]),
    (4, "Linen room", (95, 160, 240), [
        (8, 82, 110), (9, 82, 110), (10, 82, 110), ("in9", 110, 194)]),
    (5, "Deck 8 forward", (255, 90, 90), [
        (8, 21.4, 82)]),
    (6, "Lido", (60, 205, 210), [
        (11, 82, 244)]),
    (7, "Balconies + hallways", (175, 225, 50), [
        ("out8", 110, 251.5), ("out9", 110, 249.5), ("out10", 110, 247),
        ("in8", 110, 251.5), ("in9", 194, 249.5), ("in10", 110, 247)]),
    (8, "Top deck", (250, 140, 60), [
        (12, 82, 220), ("funnel", 179.5, 193)]),
    (9, "The bow", (170, 115, 225), [
        (7, 21.4, 82), (9, 23.6, 82), (10, 25, 82), (11, 29.5, 82), (12, 31, 82)]),
    (10, "Sunset", (250, 240, 120), [
        (7, 0.5, 21.4), (11, 24, 29.5)]),
]
COLOUR = {n: c for n, _, c, _ in REGIONS}
FUNNEL_REGION = 8

# Names on the big map: (deck, metre, text).
LABELS = [
    (4, 67, "Gangway (start)"), (4, 150, "Crew corridors, cabins"),
    (5, 47, "Cabins"), (5, 130, "Reception"), (5, 172, "Restaurants"), (5, 228, "Seven Seas"),
    (6, 47, "Cabins"), (6, 92, "Atrium"), ("prom", 170, "Promenade, lifeboats"),
    ("rooms", 170, "Bars, shops, Library"), (6, 243, "Theatre"),
    (7, 12, "Mooring"), (7, 48, "Kids' clubs"), (7, 92, "Atrium"), (7, 150, "Casino, gallery, arcade"),
    (7, 228, "Theatre balcony"),
    (8, 50, "Cabin 8206"), (9, 50, "Cabins"), (10, 32, "Bridge"), (10, 58, "Cabins"),
    ("out8", 175, "Balconies, outside the ship"), ("in8", 175, "Hallway"),
    ("out9", 175, "Balconies"), ("in9", 121, "Linen room"), ("in9", 167, "Corridor: carts, a guest locked out"),
    ("in9", 225, "Hallway"), ("out10", 175, "Balconies"), ("in10", 175, "Hallway"),
    (11, 52, "Spa"), (11, 92, "Gym"), (11, 135, "Pool"), (11, 177, "Garden Café"),
    (11, 226, "Great Outdoors"), (12, 50, "Spinnaker, Chapel"), (12, 128, "Sun deck"),
    (12, 155, "Sports"), (12, 190, "Restaurants"), ("funnel", 186, "Ship's horn"), (11, 26.8, "Balcony"),
]

# Where each region's number sits on the big map.
BADGES = {1: (4, 108), 2: (7, 104), 3: (7, 190), 4: (9, 106), 5: (8, 30), 6: (11, 113), 7: (10, 222),
          8: (12, 100), 9: (9, 30), 10: (7, 20.5)}

# The routes on the big map: (from (deck, m), to (deck, m), kind). "main": the way on into the next
# region; "short": a shortcut she opens; "glide": with the parasol.
ROUTES = [
    ((4, 76), (6, 90), "main"),                 # 2: up through the atrium, the Deck card
    (("prom", 140), (7, 140), "main"),          # 3: the door Bumbot left open
    ((7, 99), (9, 99), "main"),                 # 4: the glass elevator goes on up
    ((8, 84), (8, 57), "main"),                 # 5: the Housekeeping card's door, deck 8 forward
    ((8, 78), (11, 86), "main"),                # 6: the forward stairs on up to the pool deck
    (("in9", 145), ("out9", 145), "main"),      # 7: out through a balcony cabin, grip socks
    ((11, 232), (12, 217), "main"),             # 8: a wall jump up to deck 12's aft terrace
    ((12, 96), (10, 36), "main"),               # 9: the Officer's card, forward and down
    ((10, 29.2), (11, 29.2), "main"),               # 10: the hatch
    ((11, 25.5), (7, 4), "glide"),              #     and the glide to the bow
    ((9, 112), (4, 112), "short"),              # the laundry chute
    ((6, 247), (4, 247), "short"),              # the theatre's one-way trunk
    ((11, 135), (10, 135), "short"),            # the drained pool's hatch
    ((11, 89), (5, 89), "glide"),               # down the atrium
    (("out8", 128), ("prom", 124), "glide"),    # off a balcony to the promenade
    (("out10", 205), ("in10", 205), "short"),   # a balcony door opened from outside: a hallway
]

# The order: what opens the region, and the arrows on that step's ship:
# (from (deck, m), to (deck, m), kind). "errand": hands full; "short": a shortcut; "back": a new
# way into a place she knows; "glide": with the parasol.
STEPS = [
    (1, "Start at the gangway. Her colleague can't leave his post.",
     "Lunch waits on a tray in a restaurant: carry it to him. He gives her the Deck card.",
     [((5, 172), (4, 67), "errand")]),
    (2, "Deck card opens the way up and out to the promenade.",
     "Bumbot's first near-catch here: he bolts through a door and leaves it open.",
     [((4, 67), (6, 92), "back"), ((6, 92), ("prom", 175), "back")]),
    (3, "The door he left open leads into Showtime.",
     "The stage manager wants something from deck 4. Reward: the Entertainment card, and a one-way "
     "escape trunk down to deck 4.",
     [((4, 140), (6, 240), "errand"), ((6, 244), (4, 244), "short")]),
    (4, "Entertainment card: the glass elevator goes on up to decks 8-10.",
     "Only deck 9's midships corridor: carts, a door swinging open, a guest locked out, a balcony cabin. "
     "The linen room: the Housekeeping card, the laundry chute to deck 4, pantry doors on decks 4-5.",
     [((7, 96), (9, 96), "back"), ((9, 113), (4, 113), "short"), ((9, 113), (5, 135), "back")]),
    (5, "Housekeeping card opens the door at deck 8's forward end.",
     "Cabin 8206, the surprise, a bit past the middle of the game. Its door stands open on her way through.",
     [((8, 95), (8, 42), "back")]),
    (6, "Through deck 8 forward: the only stairs that go on up to the pool deck.",
     "Grip socks (wall jumps) and a parasol (long drops). Both change the old decks. "
     "Bumbot drains the pool: a hatch opens in its tank.",
     [((8, 78), (11, 90), "back"), ((11, 92), (5, 92), "glide"), ((11, 135), (10, 135), "short")]),
    (7, "Grip socks: out through the balcony cabin on deck 9, climbing balcony to balcony outside the ship.",
     "Each balcony door she opens from outside unlocks a hallway inside: decks 8-10 become the fast way "
     "fore and aft. A slip is the overboard scare; the parasol glides down to the promenade.",
     [(("in9", 145), ("out9", 150), "back"), (("out9", 160), ("out10", 200), "back"),
      (("out10", 205), ("in10", 205), "short"), (("out8", 128), ("prom", 124), "glide")]),
    (8, "Grip socks again: a wall jump from the Great Outdoors up to deck 12, then the funnel's stairway.",
     "An engineer up there needs something brought to him, then lets her pull the ship's horn. "
     "The officer runs for the bridge and drops his card; the old lady leaves her sunbed; the gulls lift.",
     [((11, 232), (12, 217), "back"), ((5, 172), ("funnel", 186), "errand"), (("funnel", 183), (12, 118), "back")]),
    (9, "Officer's card: forward along deck 12, then down through the bow.",
     "Spa, kids' clubs, and at last the bridge. Bumbot hits the alarm there, and the hatch in its ceiling opens.",
     [((12, 85), (11, 60), "back"), ((11, 60), (10, 34), "back")]),
    (10, "The hatch: up from the bridge to the balcony forward of the spa, as the sun sets.",
     "She glides down on the parasol to the mooring deck, shut until now. At the tip of the bow he finally comes to her.",
     [((10, 28), (11, 27), "back"), ((11, 26), (7, 5), "glide")]),
]


def with_funnel_top(full):
    """The picture with the funnel's top added: it rises past the map's top edge, where the render
    stops. Drawn from buildFunnel()'s measures in ShipScene.js (no smoke at this size)."""
    extra = -TOP_WORLD
    im = Image.new("RGB", (full.width, full.height + extra), full.getpixel((40, 2)))
    im.paste(full, (0, extra))
    d = ImageDraw.Draw(im)
    fb, c1 = FUNNEL_FA + 1360, 164
    fore, aft = FUNNEL_FA + 560, fb - 150
    t = c1 / (c1 - FUNNEL_TOP)
    x0 = FUNNEL_FA + 150 + (fore - FUNNEL_FA - 150) * t
    x1 = fb - 90 + (aft - fb + 90) * t
    top = FUNNEL_TOP + extra
    d.polygon([(x0, extra), (x1, extra), (aft, top), (fore, top)], fill=(0x1d, 0x20, 0x40))
    for a, b in (((x0, extra), (fore, top)), ((x1, extra), (aft, top)), ((fore, top), (aft, top))):
        d.line([a, b], fill=(0x32, 0x33, 0x53), width=10)
    lx = fb - 470
    d.rectangle([lx, FUNNEL_TOP + 110 + extra, lx + 170, extra + 2], fill=(0x8f, 0xb6, 0xdc))
    d.text((lx + 85, -46 + extra), "NCL", font=font(60, True), fill=(255, 255, 255), anchor="mm")
    for dx, h, w in ((30, 70, 34), (80, 90, 30), (126, 80, 36), (178, 96, 30), (300, 84, 34)):
        d.rectangle([fore + dx, top - h, fore + dx + w, top], fill=(0x7a, 0x6e, 0x66))
    return im


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


class Ship:
    """The ship's picture at a given width and deck height, and where things fall on it."""

    def __init__(self, full, width, row):
        self.row = row
        self.sx = width / full.width
        self.sy = row / DECK_H
        crop = full.crop((0, 0, full.width, BOTTOM_WORLD - TOP_WORLD))
        self.base = crop.resize((width, round(crop.height * self.sy)), Image.LANCZOS)

    def x(self, m):
        return (x_of(m) - 8) * self.sx

    def band(self, deck):
        """The top and bottom of a deck's row. A deck's row is split in two where the outside of the
        ship runs along it: "outN" its top half (deck 6's promenade, the balconies of decks 8-10),
        "inN" its bottom half (the rooms and corridors inside); "prom" and "rooms" are deck 6's.
        "funnel": on top of the funnel."""
        if deck == "funnel":
            return (FUNNEL_TOP - 58 - TOP_WORLD) * self.sy, (FUNNEL_TOP - TOP_WORLD) * self.sy
        deck = {"prom": "out6", "rooms": "in6"}.get(deck, deck)
        half = None
        if isinstance(deck, str):
            half, deck = deck[:-1] if deck[-2].isalpha() else deck[:-2], int(deck.lstrip("outin"))
        bottom = (floor_y(deck) - TOP_WORLD) * self.sy
        top = bottom - self.row
        if half == "out":
            return top, top + self.row / 2
        if half == "in":
            return top + self.row / 2, bottom
        return top, bottom

    def world(self, wx, wy):
        return wx * self.sx, (wy - TOP_WORLD) * self.sy

    def point(self, spot):
        deck, m = spot
        top, bottom = self.band(deck)
        return self.x(m), (top + bottom) / 2

    def rect(self, deck, a, b):
        top, bottom = self.band(deck)
        return [self.x(a), top + 1, self.x(b), bottom - 1]


def glide(d, a, b, colour, width):
    """A straight line from a to b, ending in a head."""
    d.line([a, b], fill=colour, width=width)
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = max(math.hypot(dx, dy), 1)
    ux, uy, head = dx / n, dy / n, width + 5
    base = (b[0] - ux * head * 1.5, b[1] - uy * head * 1.5)
    d.polygon([b, (base[0] - uy * head, base[1] + ux * head), (base[0] + uy * head, base[1] - ux * head)], fill=colour)


def arrow(d, a, b, colour, width):
    """A line from a to b, bent to run along then across, ending in a head."""
    mid = (b[0], a[1])
    d.line([a, mid, b], fill=colour, width=width, joint="curve")
    head = width + 5
    if abs(b[1] - mid[1]) >= 1:
        sign = 1 if b[1] > mid[1] else -1
        d.polygon([b, (b[0] - head, b[1] - sign * head * 1.5), (b[0] + head, b[1] - sign * head * 1.5)], fill=colour)
    else:
        sign = 1 if b[0] > a[0] else -1
        d.polygon([b, (b[0] - sign * head * 1.5, b[1] - head), (b[0] - sign * head * 1.5, b[1] + head)], fill=colour)


KIND = {"errand": (255, 255, 255), "short": (60, 255, 90), "back": (255, 240, 60), "glide": (255, 110, 200),
        "main": (255, 255, 255)}


def tint(ship, opened, new=None, dim=True, alpha=175):
    """The ship with `opened` regions in colour; the rest of it dark, if `dim`."""
    im = ship.base.copy().convert("RGBA")
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for n, _, colour, pieces in REGIONS:
        for piece in pieces:
            r = ship.rect(*piece)
            if n in opened:
                d.rectangle(r, fill=colour + (alpha if n == new or new is None else 95,))
                if n == new:
                    d.rectangle(r, outline=(255, 255, 255, 255), width=2)
            elif dim:
                d.rectangle(r, fill=(28, 26, 40, 225))
    if FUNNEL_REGION in opened:     # the stairway up the funnel's sloped front
        ImageDraw.Draw(layer).line([ship.world(FUNNEL_FA + 150, 164), ship.world(FUNNEL_FA + 560, FUNNEL_TOP)],
                                   fill=(255, 255, 255, 255), width=max(2, round(ship.row / 14)))
    im.alpha_composite(layer)
    return im


def big_map(full):
    width, row = 2000, 46
    ship = Ship(full, width, row)
    pad, title, legend = 56, 44, 104
    im = Image.new("RGB", (width + pad * 2, ship.base.height + title + legend), (250, 250, 247))
    ship_im = tint(ship, {n for n, *_ in REGIONS})
    d = ImageDraw.Draw(ship_im)
    for a, b, kind in ROUTES:
        pa, pb = ship.point(a), ship.point(b)
        draw = glide if kind == "glide" else arrow
        draw(d, pa, pb, (20, 20, 30), 8)
        draw(d, pa, pb, KIND[kind], 4)
    for deck, m, text in LABELS:
        x, y = ship.point((deck, m))
        size = 11 if isinstance(deck, str) or text == "Balcony" else 13
        d.text((x, y), text, font=font(size, True), fill=(20, 20, 40), anchor="mm",
               stroke_width=2, stroke_fill=(255, 255, 255))
    for n, spot in BADGES.items():
        x, y = ship.point(spot)
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(20, 20, 40), outline=(255, 255, 255), width=2)
        d.text((x, y), str(n), font=font(20, True), fill=(255, 255, 255), anchor="mm")
    im.paste(ship_im.convert("RGB"), (pad, title))

    d = ImageDraw.Draw(im)
    d.text((pad, 12), "Bow", font=font(20, True), fill=(30, 30, 60))
    d.text((pad + width, 12), "Stern", font=font(20, True), fill=(30, 30, 60), anchor="ra")
    d.text((pad + width / 2, 12), "The ship's regions, a brainstorm in progress; the numbers are the order they open in",
           font=font(22, True), fill=(30, 30, 60), anchor="ma")
    for deck in EXTENT:
        if deck == 3:
            continue
        _, y = ship.point((deck, 0))
        d.text((pad - 12, y + title), str(deck), font=font(18, True), fill=(30, 30, 60), anchor="rm")
    x = pad
    y = title + ship.base.height + 14
    for n, name, colour, _ in REGIONS:
        d.rectangle([x, y, x + 30, y + 30], fill=colour)
        d.text((x + 15, y + 15), str(n), font=font(18, True), fill=(20, 20, 40), anchor="mm")
        d.text((x + 38, y + 15), name, font=font(18, True), fill=(30, 30, 60), anchor="lm")
        x += 38 + d.textlength(name, font=font(18, True)) + 26
    x, y = pad, y + 48
    for kind, label in (("main", "the way on, step by step"), ("short", "shortcut"), ("glide", "parasol glide")):
        d.line([(x, y + 15), (x + 40, y + 15)], fill=(40, 40, 60), width=9)
        d.line([(x, y + 15), (x + 40, y + 15)], fill=KIND[kind], width=5)
        d.text((x + 50, y + 15), label, font=font(18, True), fill=(30, 30, 60), anchor="lm")
        x += 50 + d.textlength(label, font=font(18, True)) + 40
    im.save(ROOT / "docs" / "ship-regions.png")


def wrap(d, text, f, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if d.textlength(trial, font=f) > width and line:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


def strip(full):
    width, row, cols = 980, 24, 2
    ship = Ship(full, width, row)
    gap, pad, text_h = 26, 20, 118
    cell_h = ship.base.height + text_h
    rows = (len(STEPS) + 1) // cols
    im = Image.new("RGB", (pad * 2 + cols * width + gap * (cols - 1), 60 + rows * (cell_h + gap) + 34), (250, 250, 247))
    d0 = ImageDraw.Draw(im)
    d0.text((pad, 14), "The order the ship opens up (brainstorm)", font=font(26, True), fill=(30, 30, 60))
    lx = pad + 560
    for kind, label in (("errand", "carrying something"), ("short", "shortcut"), ("back", "new way in"), ("glide", "parasol glide")):
        d0.line([(lx, 30), (lx + 34, 30)], fill=(40, 40, 60), width=7)
        d0.line([(lx, 30), (lx + 34, 30)], fill=KIND[kind], width=4)
        d0.text((lx + 42, 30), label, font=font(18), fill=(30, 30, 60), anchor="lm")
        lx += 62 + d0.textlength(label, font=font(18)) + 20
    for i, (n, opens, there, arrows) in enumerate(STEPS):
        x = pad + (i % cols) * (width + gap)
        y = 60 + (i // cols) * (cell_h + gap)
        panel = tint(ship, set(range(1, n + 1)), new=n)
        d = ImageDraw.Draw(panel)
        for a, b, kind in arrows:
            pa, pb = ship.point(a), ship.point(b)
            draw = glide if kind == "glide" else arrow
            draw(d, pa, pb, (20, 20, 30), 6)
            draw(d, pa, pb, KIND[kind], 3)
        im.paste(panel.convert("RGB"), (x, y))
        d0.rectangle([x, y + ship.base.height + 6, x + 34, y + ship.base.height + 40], fill=COLOUR[n])
        d0.text((x + 17, y + ship.base.height + 23), str(n), font=font(22, True), fill=(20, 20, 40), anchor="mm")
        name = next(r[1] for r in REGIONS if r[0] == n)
        d0.text((x + 44, y + ship.base.height + 23), name, font=font(22, True), fill=(30, 30, 60), anchor="lm")
        ty = y + ship.base.height + 46
        for text, f, colour in ((opens, font(17, True), (30, 30, 60)), (there, font(17), (60, 60, 80))):
            for line in wrap(d0, text, f, width - 10):
                d0.text((x, ty), line, font=f, fill=colour)
                ty += 21
    im.save(ROOT / "docs" / "ship-unlock-order.png")


def main():
    Image.MAX_IMAGE_PIXELS = None
    full = with_funnel_top(Image.open(FULL).convert("RGB"))
    big_map(full)
    strip(full)
    print("wrote docs/ship-regions.png, docs/ship-unlock-order.png;", LENGTH, "m")


if __name__ == "__main__":
    main()
