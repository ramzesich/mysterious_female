"""Packs the plan's own things (the delivery robot, the gulls, ... : PixelLab map objects, one
generation each, kept raw in assets/source/things/<name>.png) into an atlas, assets/sprites/things.png
+ things.json, each converted to Resurrect 64 and trimmed to what is drawn.

    python tools/build_things.py [--preview out.png]

`SCALE` shrinks a piece that came out too big next to her (box resampling, then the palette again),
as tools/build_ship_art.py's `height` does: name -> its height in the game, px.
"""

import json
import shutil
import sys
from pathlib import Path

from PIL import Image

from palettize import palettize

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "things"
OUT = ROOT / "assets" / "sprites"

# Heights in the game, px (she is 59): a herring gull stands about knee-high.
SCALE = {"gull-perched": 20, "gull-up": 22, "gull-down": 10, "robot": 52,
         # The towel animals on their table (deck 10's midship flight): a swan's size.
         "towel-elephant": 19, "towel-monkey": 27, "towel-rabbit": 27,
         # Two sunbathers, each on a lounger of their own (the pool deck, by the first pool).
         "sunbather-1": 33, "sunbather-2": 20,
         # Region 7's balconies with someone on them: a man asleep on a lounger, a couple at breakfast.
         "balc-sunbather": 32, "balc-breakfast": 46,
         # Region 8, deck 12's sun deck: two more, on loungers of their own.
         "sunbather-3": 27, "sunbather-4": 22,
         # Region 9: the wedding cake, carried at her hands: its top about level with her head.
         "wedding-cake": 25,
         # The things to find, region 1 (docs/plan-three-uses.md §4.1): Bumbot's tennis ball, wool and
         # feather on a stick, her little flag of Ukraine on its stand.
         # (The tennis ball 8 px and its outline, bigger than life so that it reads: the user chose it
         # from six, 2026-11-17, `SEAM`.)
         # (Since 2026-11-19 each made from its close-up, `FROM_CLOSEUP`, a little bigger than life: the
         # user, "A and C". The wool: a small picture of its own, its strand over the basket's rim.)
         "tennis-ball": 10, "wool": 10, "flag-ua": 16,
         # §4 2.1's things to find, each its close-up shrunk (the user approved each in place): Bumbot's
         # snack tube, massage gun and remote-controlled car; her diary. (Her bookmark in its book and
         # her plant are kept finished, mended by hand: the bookmark's cat head, the plant's stem.)
         "snack-tube": 6, "massage-gun": 16, "rc-car": 10, "diary": 13,
         # Her other pickups (2026-11-20, part of 2.1): the grip socks, the stage manager's pills.
         "grip-socks": 10, "pills-bottle": 12,
         # Bumbot's collar bell (4), lying on the promenade's deck once the gull has dropped it: its
         # close-up shrunk, 14 px wide (the user, 2026-11-20). (The gull holding it, `gull-bell-*`, is
         # the game's own gull frames with the collar drawn in by hand at this size: shrunk, the
         # generated collar read as nothing; `gull-bell/README.md`.)
         "collar-bell": 11,
         # The promenade's wall lights (deck 6, ten along it; the bell's gull on one): a round caged
         # bulkhead light and an oval one, a little bigger than life (the user chose 3 and 4, size B,
         # 2026-11-20; `lamps/README.md`).
         "lamp-round": 23, "lamp-oval": 17,
         # The breakfast round's tray, carried in both hands (the tray a hand's width).
         "breakfast-tray": 12,
         # Steps 1 to 4's pictures drawn in code, generated instead (the art rule looked back over,
         # the user, 2026-11-17; raw ids and the tries in `assets/source/things/tries/README.md`):
         # the four other desk flags, as tall as hers; the climb's shelf and its laundry cart (the
         # linen room's had stood in for it); the knitting lady's basket; the hand a cabin door puts
         # out; the heart her cry shows. (`icon-mute`, the quiet place's sign, is kept at its size.)
         "flag-se": 13, "flag-fi": 13, "flag-ee": 13, "flag-dk": 13,
         "wall-shelf": 5, "knit-basket": 9, "door-hand": 4, "icon-heart": 14,
         # (The laundry cart is kept at its size: its rows cut, not shrunk, and its rim mended. The
         # feather toy is its close-up shrunk since 2026-11-19; the purple-handled one before it is
         # `tries/feather-toy-purple.png`.)
         "feather-toy": 9}

# The things to find drawn in the world from their close-ups (assets/source/closeups/, the user's "A and
# C", 2026-11-19): the world's sprite is the close-up shrunk, so the two are one picture.
CLOSEUPS = SRC.parent / "closeups"
FROM_CLOSEUP = {"tennis-ball": "ball", "feather-toy": "feather", "flag-ua": "flag", "snack-tube": "snack",
                "massage-gun": "massage", "rc-car": "car", "diary": "diary", "grip-socks": "socks",
                "pills-bottle": "pills", "collar-bell": "bell"}
# A slight outline round a picture, in one of its own darker colours (the user, 2026-11-20: the socks
# and the pills, "give them a slight outline"): name -> its colour.
OUTLINE = {"grip-socks": "cf657f", "pills-bottle": "cd683d"}
# Pixels set by hand at the end (x, y in the finished sprite -> colour): the pills' label, a dark title
# and two lines of print, as on its close-up; its top row the cap's white ridges, as on the close-up, and
# its foot made even, a band of yellow and rounded corners (the user, 2026-11-20).
MEND = {"pills-bottle": {(1, 7): "3e3546", (2, 7): "3e3546", (3, 7): "3e3546", (4, 7): "3e3546", (1, 9): "9babb2", (2, 9): "9babb2", (3, 9): "9babb2", (4, 9): "9babb2", (1, 11): "9babb2", (2, 11): "9babb2", (3, 11): "9babb2", (1, 0): "c7dcd0", (2, 0): "ffffff", (3, 0): "c7dcd0", (4, 0): "ffffff", (5, 0): "c7dcd0", (0, 12): "cd683d", (1, 12): "f9c22b", (1, 13): "cd683d"}}

# Generated, paid for, and not used: the folded newspaper came drawn tilted, a smudge at the 3 px
# of a paper on the carpet; the paper round's papers are drawn in code (the user, 2026-11-16).
SKIP = {"newspaper",
        # (Butterflies made to circle over her head in code: the user would have them drawn with her,
        # and they are, in her dazed clips.)
        "butterfly-open", "butterfly-closed",
        # (A first armchair for the knitting lady, drawn turned three-quarters while she is in flat
        # profile: the user had it drawn again round her own seated pose, `knit-chair`.)
        "knit-chair-turned"}

# Colours changed after the palette: PixelLab drew the parasol's stripes maroon and pink; in the
# game they are the life rings' red and white. name -> {from: to}.
RECOLOUR = {
    "parasol-open": {"7a3045": "e83b3b", "9e4539": "e83b3b", "6e2727": "ae2334", "966c6c": "c7dcd0",
                     "9babb2": "ffffff"},
    "parasol-closed": {"c32454": "e83b3b", "7a3045": "ae2334", "831c5d": "ae2334", "966c6c": "c7dcd0",
                       "fdcbb0": "ffffff", "9babb2": "ffffff"},
    # Sweden's blue and yellow came out a dull violet and an olive on the palette.
    "flag-se": {"484a77": "4d65b4", "8fd3ff": "4d65b4", "d5e04b": "f9c22b", "a2a947": "f9c22b"},
    # The car's two rubbery wheels came a dull teal on the palette: its brightest cyans (the user: "cyan").
    "rc-car": {"0b8a8f": "0eaf9b", "0b5e65": "0b8a8f"},
}
# Rows taken out of a piece (its own rows, top to bottom, after trimming) rather than shrinking it,
# which would blur its stripes: the old lady's parasol came as long as she is tall, open and furled.
CUT_ROWS = {"parasol-open": [(30, 44)], "parasol-closed": [(16, 28), (45, 50)]}
# A piece leaning (nothing stands by itself on a crook handle): its rows pushed sideways, one px
# for every so many rows up from its foot, to the left. The furled parasol leans on the sunbed.
LEAN = {"parasol-closed": 3}
# A part of a piece cut off (its own px after trimming: left, top, right, bottom).
CROP = {}
# Shrunk by the colour that covers most of each new pixel, not by averaging: a little flag's cloth
# averaged with its dark outline came out dull (the Ukrainian flag had too, in the game since
# step 4): the four other desk flags and hers (the art rule looked back over, 2026-11-17).
BY_MAJORITY = {"flag-se", "flag-fi", "flag-ee", "flag-dk", "flag-ua", "feather-toy", "wool", "snack-tube",
               "massage-gun", "rc-car", "diary", "grip-socks", "pills-bottle", "collar-bell", "lamp-round", "lamp-oval"}
# Shrunk keeping a thin white line that reads it, then outlined: the tennis ball's seam (by majority
# it was lost, a plain yellow dot; the user: "has to look like a tennis ball", and chose an olive
# outline, 2026-11-17). name -> the outline's colour.
SEAM = {"tennis-ball": "a2a947"}
# Kept in their own colours, not put on the palette: the tin of sardines (7), drawn by hand at its size in its
# close-up's blue silver (shrunk, the close-up was a grey blob; on the palette its greys went purple).
# His folded t-shirt (13), on deck 12's lounger: PixelLab's small folded shirt (`tries/tshirt/3.png`, the user's
# choice), its purples set to the close-up's navies by lightness, 20 x 12 (the user, 2026-11-21: "Better"); not the
# close-up shrunk (that read as a dark bag), and no logo (folded, it would not show: the user).
# The life-jacket box at the boat walkway's aft end (book 11 on its lid; the user chose try 2 of two, 2026-11-21): white,
# which the palette turns pale green; kept so, and washed as the walkway's background is (`WASH`).
# The boat drill's warning light (the user, 2026-11-21: "a proper red warning light"; try 2 of two, a red lens in a cage
# hanging from a ceiling mount, `tries/warning-light/`): its reds kept, and a twin with the lens off (`DIM`).
# The console table at the end of deck 9's officers' corridor (book 14 on it; the user chose try 4 of four, a half-moon
# one, 2026-11-21, `tries/console-table/`): its honey teak kept (palettized, browns go mauve), washed as deck 9 inside.
# The lifeboat's roof hatch, its back and its lip (the user, 2026-11-21; `tools/build_hatch.py`): cut from the boat's own
# washed picture, kept so.
# (Delivery 1's vase of flowers and the low table it waits on, §5 3.2: in their own colours, as the user approved them;
# `delivery/`, its README.)
OWN_COLOURS = {"grip-socks", "canister", "delivery-vase", "delivery-teapot", "delivery-pillow-bottom", "delivery-pillow-mid", "delivery-pillow-top", "tray-stand", "sardine-tin", "tshirt-folded", "sleepmask", "guitar-pick", "lifejacket-box", "warning-light", "console-table",
               "lifeboat-hatch-back", "lifeboat-hatch-front"}
# A thing's twin with its light off: name -> (the lit thing, how far its reds are darkened toward a dull red).
DIM = {"warning-light-off": ("warning-light", 0.75)}
# Background things washed toward the wall behind them, as tools/wash_levels.py washes the ship's pieces: name ->
# (how far, the wall's colour). The walkway's recess wall is ShipScene's 0xc9ced3; decks 6 and 7 are at 20%.
WASH = {"lifejacket-box": (0.20, (0xc9, 0xce, 0xd3)),
        # (Deck 9 inside is at 35%, toward the corridor's wall, tools/build_ship_art.py's WALL.)
        "console-table": (0.35, (0xE9, 0xDF, 0xCC))}
# Pictures the user drew by hand in Paint, on a white ground (white is empty): name -> its file's stem. **Never written
# by a tool** (CLAUDE.md): his handheld (15), the user's own pixel edit of my 24 x 11, 2026-11-21.
BY_HAND = {"handheld": "handheld-by-hand"}


def by_hand(path):
    img = Image.open(path).convert("RGBA")
    img.putdata([(0, 0, 0, 0) if p[:3] == (255, 255, 255) else p for p in img.get_flattened_data()])
    return img.crop(img.getbbox())


def seam_shrink(img, n, outline):
    """The picture (square) n x n: a box with a fifth or so of the seam's whites in it is seam,
    otherwise the colour most of it has; clear where most of the box is clear. Then a one px
    outline round it, not on the corners."""
    import colorsys
    side = max(img.width, img.height)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(img, (0, 0))
    seam = lambda c: (lambda h, s, v: s < 0.25 and v > 0.55)(*colorsys.rgb_to_hsv(*[k / 255 for k in c[:3]]))
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    for oy in range(n):
        for ox in range(n):
            box = [sq.getpixel((x, y)) for y in range(int(oy * side / n), int((oy + 1) * side / n))
                   for x in range(int(ox * side / n), int((ox + 1) * side / n))]
            solid = [c for c in box if c[3] > 128]
            if len(solid) < len(box) / 2:
                continue
            white = [c for c in solid if seam(c)]
            if len(white) >= 0.12 * len(solid):
                out.putpixel((ox, oy), (244, 244, 232, 255))
            else:
                counts = {}
                for c in solid:
                    if not seam(c):
                        counts[c] = counts.get(c, 0) + 1
                out.putpixel((ox, oy), max(counts, key=counts.get))
    ring = Image.new("RGBA", (n + 2, n + 2), (0, 0, 0, 0))
    ring.alpha_composite(out, (1, 1))
    edge = tuple(bytes.fromhex(outline)) + (255,)
    done = ring.copy()
    for y in range(n + 2):
        for x in range(n + 2):
            if not ring.getpixel((x, y))[3] and any(0 <= x + dx < n + 2 and 0 <= y + dy < n + 2 and ring.getpixel((x + dx, y + dy))[3]
                                                  for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                done.putpixel((x, y), edge)
    return done


def majority_shrink(img, w, h):
    """Each pixel of the w x h picture takes the colour most of its box in `img` has, or stays
    clear when most of the box is clear."""
    px = img.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    sx, sy = img.width / w, img.height / h
    for y in range(h):
        for x in range(w):
            seen, total = {}, 0
            for yy in range(int(y * sy), max(int(y * sy) + 1, int((y + 1) * sy))):
                for xx in range(int(x * sx), max(int(x * sx) + 1, int((x + 1) * sx))):
                    r, g, b, a = px[xx, yy]
                    total += 1
                    if a >= 128:
                        seen[(r, g, b)] = seen.get((r, g, b), 0) + 1
            if seen and sum(seen.values()) * 2 >= total:
                op[x, y] = max(seen, key=seen.get) + (255,)
    return out


def piece(path, name=None):
    name = name or path.stem
    img = Image.open(path).convert("RGBA")
    img = img.crop(img.getbbox())
    path = Path(name + ".png")       # (the options below go by the thing's name, wherever its picture is)
    if path.stem in CROP:
        img = img.crop(CROP[path.stem])
        img = img.crop(img.getbbox())
    if path.stem in CUT_ROWS:
        for y0, y1 in reversed(CUT_ROWS[path.stem]):
            cut = Image.new("RGBA", (img.width, img.height - (y1 - y0)), (0, 0, 0, 0))
            cut.alpha_composite(img.crop((0, 0, img.width, y0)), (0, 0))
            cut.alpha_composite(img.crop((0, y1, img.width, img.height)), (0, y0))
            img = cut
    h = SCALE.get(path.stem)
    if path.stem in SEAM:
        img = seam_shrink(img, h, SEAM[path.stem])
    elif h and h != img.height:
        w = max(1, round(img.width * h / img.height))
        img = majority_shrink(img, w, h) if path.stem in BY_MAJORITY else img.resize((w, h), Image.BOX)
        # Box resampling leaves soft edges: alpha back to on or off.
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = px[x, y]
                px[x, y] = (r, g, b, 255 if a >= 128 else 0)
    # (The tennis ball keeps its own felt's colours, as the user chose it: on the palette its
    # fluorescent yellow went dull.)
    if path.stem not in SEAM and path.stem not in OWN_COLOURS:
        img = palettize(img)
    if path.stem in LEAN:
        every = LEAN[path.stem]
        reach = (img.height - 1) // every
        leant = Image.new("RGBA", (img.width + reach, img.height), (0, 0, 0, 0))
        for y in range(img.height):
            leant.alpha_composite(img.crop((0, y, img.width, y + 1)), (reach - (img.height - 1 - y) // every, y))
        img = leant
    swaps = {tuple(bytes.fromhex(k)): tuple(bytes.fromhex(v)) for k, v in RECOLOUR.get(path.stem, {}).items()}
    if swaps:
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = px[x, y]
                if a and (r, g, b) in swaps:
                    px[x, y] = swaps[(r, g, b)] + (a,)
    # (A shrunk close-up can leave an empty row or column at its edge: trimmed, or it would stand a px
    # off what holds it.)
    if name in FROM_CLOSEUP:
        img = img.crop(img.getbbox())
    if name in OUTLINE:
        img = outlined(img, OUTLINE[name])
    for (x, y), c in MEND.get(name, {}).items():
        img.putpixel((x, y), tuple(bytes.fromhex(c)) + (255,))
    if name in WASH:
        k, wall = WASH[name]
        img.putdata([(*(round(c + (w - c) * k) for c, w in zip(p[:3], wall)), p[3]) if p[3] else p
                     for p in img.get_flattened_data()])
    return img


def outlined(img, colour):
    """A one px ring round what is drawn, not on its corners."""
    w, h = img.size
    ring = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    ring.alpha_composite(img, (1, 1))
    out, c = ring.copy(), tuple(bytes.fromhex(colour)) + (255,)
    for y in range(h + 2):
        for x in range(w + 2):
            if not ring.getpixel((x, y))[3] and any(0 <= x + dx < w + 2 and 0 <= y + dy < h + 2 and ring.getpixel((x + dx, y + dy))[3]
                                                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out.putpixel((x, y), c)
    return out


def build():
    pieces = [(p.stem, piece(p)) for p in sorted(SRC.glob("*.png")) if p.stem not in SKIP and p.stem not in BY_HAND.values()]
    pieces += [(name, by_hand(SRC / f"{stem}.png")) for name, stem in BY_HAND.items()]
    pieces += [(name, piece(CLOSEUPS / f"{src}.png", name)) for name, src in FROM_CLOSEUP.items()]
    lit = dict(pieces)
    for name, (src, k) in DIM.items():
        off = lit[src].copy()
        off.putdata([(round(p[0] * (1 - k) + 0x5a * k), round(p[1] * (1 - k) + 0x1c * k), round(p[2] * (1 - k) + 0x22 * k), p[3])
                     if p[3] and p[0] > p[1] + 40 and p[0] > p[2] + 40 else p for p in off.get_flattened_data()])
        pieces.append((name, off))
    pieces.sort(key=lambda t: t[0])
    width = sum(im.width + 2 for _, im in pieces)
    height = max(im.height for _, im in pieces)
    sheet = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    frames, x = {}, 0
    for name, im in pieces:
        sheet.alpha_composite(im, (x, 0))
        frames[name] = {"frame": {"x": x, "y": 0, "w": im.width, "h": im.height}, "rotated": False, "trimmed": False,
                        "spriteSourceSize": {"x": 0, "y": 0, "w": im.width, "h": im.height},
                        "sourceSize": {"w": im.width, "h": im.height}}
        x += im.width + 2
    sheet.save(OUT / "things.png")
    (OUT / "things.json").write_text(json.dumps({"frames": frames, "meta": {"image": "things.png"}}, indent=1), encoding="utf-8")
    print("wrote assets/sprites/things.png:", ", ".join(f"{n} {im.width}x{im.height}" for n, im in pieces))
    # The flower frame round the screen while she carries the vase (delivery 1, the user's choice; `delivery/`): the
    # screen's own size, in its own colours, as it is.
    shutil.copyfile(SRC / "delivery" / "frame.png", OUT / "flower-frame.png")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        big = Image.new("RGBA", sheet.size, (150, 160, 175, 255))
        big.alpha_composite(sheet)
        big.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(out)


if __name__ == "__main__":
    build()
