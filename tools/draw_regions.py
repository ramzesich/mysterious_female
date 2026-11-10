"""Draws the progression plan (GAME_DESIGN.md §6.1) on the real ship: the regions in colour over the
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
# the ship runs along a deck, its row is split: "outN" the outside half (deck 6's promenade, the boat
# walkway at deck 7's height, the balconies on decks 8-10), "inN" the inside half; "prom" and "rooms"
# are deck 6's two halves. The cabin decks' corridors are hallways, opened from the balconies outside
# (region 7) or by the pool's hatch; only deck 9 midships, round the linen room, is a region (4).
REGIONS = [
    (1, "Lower ship", (240, 190, 70), [
        (4, 20, 255), (5, 20, 255)]),
    (2, "Atrium + promenade", (90, 200, 120), [
        (6, 20, 100), ("rooms", 100, 194), ("prom", 100, 231), (7, 74, 110)]),
    (3, "Showtime", (235, 95, 130), [
        ("rooms", 194, 231), (6, 231, 255), ("in7", 110, 231), (7, 231, 254)]),
    (4, "Housekeeping", (95, 160, 240), [
        (8, 82, 110), (9, 82, 110), (10, 82, 110), ("in9", 110, 194)]),
    (5, "Deck 8 forward", (255, 90, 90), [
        (8, 21.4, 82)]),
    (6, "Lido", (60, 205, 210), [
        (11, 74, 244)]),
    (7, "Outside", (175, 225, 50), [
        ("out7", 100, 231), ("out8", 110, 251.5), ("out9", 110, 249.5), ("out10", 110, 247),
        ("in8", 110, 251.5), ("in9", 194, 249.5), ("in10", 110, 247)]),
    (8, "Top deck + funnel", (250, 140, 60), [
        (12, 82, 220), ("funnel", 179.5, 193)]),
    (9, "The bow", (170, 115, 225), [
        (12, 31, 82), (11, 29, 74), (10, 25, 82), (9, 23.6, 82), (7, 21.4, 74)]),
    (10, "Sunset", (250, 240, 120), [
        (11, 24, 29), (7, 0.5, 21.4)]),
]
COLOUR = {n: c for n, _, c, _ in REGIONS}
FUNNEL_REGION = 8

# Names on the big map: (deck, metre, text).
LABELS = [
    (4, 67, "Gangway (start)"), (4, 122, "Laundry"), (4, 165, "Crew corridors, cabins"),
    (4, 232, "Stage manager's cabin"),
    (5, 47, "Cabins"), (5, 92, "Atrium Café"), (5, 130, "Reception"), (5, 172, "Restaurants"),
    (5, 228, "Seven Seas: lunch, Bumbot"),
    (6, 47, "Cabins"), (6, 92, "Atrium"), ("prom", 170, "Promenade"), ("rooms", 130, "Bliss, shops"),
    ("rooms", 176, "Library: Bumbot"), (6, 243, "Theatre: stage"),
    (7, 9, "Mooring"), (7, 48, "Kids' clubs"), (7, 92, "Atrium"), ("out7", 165, "Boat walkway"),
    ("in7", 150, "Casino, gallery, arcade"), (7, 242, "Balcony"),
    (8, 50, "Cabin 8206"), ("out8", 175, "Balconies"), ("in8", 150, "Hallway"), ("in8", 228, "Hallway"),
    (9, 50, "Officers' cabins"), ("out9", 175, "Balconies"), ("in9", 121, "Linen room"),
    ("in9", 162, "Corridor: steward, carts"), ("in9", 225, "Hallway"),
    (10, 32, "Bridge"), (10, 58, "Officers' cabins"), ("out10", 175, "Balconies"),
    ("in10", 165, "Hallway (the pool's hatch)"), ("in10", 225, "Hallway"),
    (11, 26.5, "Balcony"), (11, 52, "Spa"), (11, 92, "Gym: socks"), (11, 135, "Pool: Bumbot"),
    (11, 177, "Garden Café"), (11, 226, "Great Outdoors"),
    (12, 50, "Spinnaker, Chapel"), (12, 92, "Champs"), (12, 128, "Sun deck: old lady"), (12, 155, "Sports"),
    (12, 190, "Restaurants"), ("funnel", 186, "Horn, engineer"),
]

# Where each region's number sits on the big map.
BADGES = {1: (4, 140), 2: (7, 104), 3: ("in7", 190), 4: (9, 106), 5: (8, 30), 6: (11, 113), 7: ("out10", 215),
          8: (12, 108), 9: (9, 30), 10: (7, 19)}

# The routes on the big map: (from (deck, m), to (deck, m), kind). "main": the way on into the next
# region; "short": a shortcut she opens; "glide": with the parasol.
ROUTES = [
    ((4, 76), (6, 78), "main"),                 # 2: the forward stairs' fire door, the Deck card
    (("rooms", 190), (7, 240), "main"),         # 3: the Library's door he left open, the theatre, up to its balcony
    (("rooms", 118), ("in9", 118), "main"),     # 4: the crew trunk from Bliss up to deck 9, the Entertainment card
    (("in9", 112), (8, 66), "main"),            # 5: the vent's duct, forward and down into deck 8
    ((8, 78), (11, 86), "main"),                # 6: the forward stairs on up to the gym
    (("in9", 150), ("out9", 150), "main"),      # 7: out through the balcony cabin, grip socks
    ((11, 232), (12, 217), "main"),             # 8: the wall jump up the sun cover to deck 12
    ((12, 96), (10, 34), "main"),               # 9: the cake, then the Officer's card forward and down to the bridge
    ((10, 29.2), (11, 27), "main"),             # 10: the hatch
    ((11, 25.5), (7, 4), "glide"),              #     and the glide to the bow
    ((6, 240), (4, 240), "short"),              # the theatre's one-way trunk
    (("in9", 113), (4, 113), "short"),          # the laundry chute
    ((11, 135), ("in10", 135), "short"),        # the drained pool's hatch
    (("out7", 125), ("prom", 125), "short"),    # the boat walkway's ladder, both ways once she has come down it
    (("out10", 205), ("in10", 205), "short"),   # a balcony door opened from outside: a hallway
    ((10, 92), (5, 92), "glide"),               # down the atrium
    (("out8", 128), ("prom", 124), "glide"),    # off a balcony to the promenade
]

# The order: what opens the region, and the arrows on that step's ship:
# (from (deck, m), to (deck, m), kind). "errand": hands full; "short": a shortcut; "back": a new
# way into a place she knows; "glide": with the parasol.
STEPS = [
    (1, "Start at the gangway. The officer there can't leave his post: his lunch, from the Seven Seas.",
     "Bumbot is eating it: the first near-catch, and the dash is born. A fresh tray carried back to him: the Deck card.",
     [((5, 228), (4, 67), "errand")]),
    (2, "The Deck card opens the forward stairs' fire door up to deck 6.",
     "The atrium, the bars and shops, the promenade, the boat walkway's gate. He rides the glass elevator up where she "
     "can't; in the Library he bolts through a roped-off door and leaves it open.",
     [((4, 76), (6, 78), "back"), ((6, 92), ("prom", 175), "back"), (("prom", 125), ("out7", 125), "back")]),
    (3, "The door he left open leads into the theatre: the rehearsal, Bumbot in the spotlight.",
     "The stage manager's pills from his cabin on deck 4, down the theatre's trunk. His Entertainment card opens "
     "the way up through deck 7 and, from Bliss, the crew trunk to deck 9.",
     [(("rooms", 190), (7, 240), "back"), ((4, 232), (6, 240), "errand"), ((6, 240), (4, 240), "short")]),
    (4, "The Entertainment card: the crew trunk from Bliss up to deck 9's corridor.",
     "The steward's cart (pushing: the Housekeeping card), a guest locked out, the balcony cabin. The linen room: "
     "Bumbot in the towels, into the vent; the laundry chute to deck 4; the pantries.",
     [(("rooms", 118), ("in9", 118), "back"), (("in9", 113), (4, 113), "short"), (("in9", 113), (5, 160), "back")]),
    (5, "The vent's duct: a crawl forward and down into deck 8 forward, past its shut door.",
     "Cabin 8206, the surprise, in calm. The only stairs that go on up to deck 11 start here.",
     [(("in9", 112), (8, 66), "back")]),
    (6, "The forward stairs on up: the gym's grip socks, wall jumps everywhere.",
     "Bumbot fishing at the pool: the kid squirts him, he falls in and drains it; the hatch into deck 10's hallway. "
     "Ice cream for the kid: an ally against the gulls.",
     [((8, 78), (11, 86), "back"), ((11, 135), ("in10", 135), "short"), ((11, 215), (11, 150), "errand")]),
    (7, "Grip socks: out through the balcony cabin, or up from the boat walkway (optional).",
     "Balcony to balcony outside the ship, between gusts and gulls; each balcony door left ajar opens a hallway: "
     "decks 8-10 become the fast way fore and aft. A guest locked out on his balcony.",
     [(("in9", 150), ("out9", 150), "back"), (("out7", 125), ("out8", 128), "back"),
      (("out9", 160), ("out10", 200), "back"), (("out10", 205), ("in10", 205), "short")]),
    (8, "Grip socks: a wall jump from the Great Outdoors onto the sun cover, up to deck 12.",
     "The engineer's lunch from Topsiders, past the old lady; up the funnel: the horn. The rival drops his card, "
     "the old lady leaves her parasol, the gulls lift off the bow.",
     [((11, 232), (12, 217), "back"), ((11, 140), (12, 190), "errand"), ((12, 190), ("funnel", 186), "back"),
      (("out8", 128), ("prom", 124), "glide")]),
    (9, "The wedding cake clears deck 12's forward lobby; the Officer's card opens the gold doors down the bow.",
     "The chapel, the Spinnaker, the spa's steam, the officers' cabins, the bridge: the rival's net hits the alarm, "
     "and the hatch in the ceiling opens.",
     [((12, 170), (12, 78), "errand"), ((12, 96), (10, 34), "back")]),
    (10, "The hatch: up from the bridge to the balcony forward of the spa, as the sun sets.",
     "She glides down on the parasol, through gusts and past two gulls, to the mooring deck. At the tip of the bow he "
     "finally comes to her; then the way home to cabin 8206.",
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
    d.text((pad + width / 2, 12), "The ship's regions, the plan of 2026-11-10; the numbers are the order they open in",
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
    d0.text((pad, 14), "The order the ship opens up (the plan)", font=font(26, True), fill=(30, 30, 60))
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
