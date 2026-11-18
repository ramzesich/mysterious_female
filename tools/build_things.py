"""Packs the plan's own things (the delivery robot, the gulls, ... : PixelLab map objects, one
generation each, kept raw in assets/source/things/<name>.png) into an atlas, assets/sprites/things.png
+ things.json, each converted to Resurrect 64 and trimmed to what is drawn.

    python tools/build_things.py [--preview out.png]

`SCALE` shrinks a piece that came out too big next to her (box resampling, then the palette again),
as tools/build_ship_art.py's `height` does: name -> its height in the game, px.
"""

import json
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
         "tennis-ball": 8, "wool": 6, "flag-ua": 13,
         # The breakfast round's tray, carried in both hands (the tray a hand's width).
         "breakfast-tray": 12,
         # Steps 1 to 4's pictures drawn in code, generated instead (the art rule looked back over,
         # the user, 2026-11-17; raw ids and the tries in `assets/source/things/tries/README.md`):
         # the four other desk flags, as tall as hers; the climb's shelf and its laundry cart (the
         # linen room's had stood in for it); the knitting lady's basket; the hand a cabin door puts
         # out; the heart her cry shows. (`icon-mute`, the quiet place's sign, is kept at its size.)
         "flag-se": 13, "flag-fi": 13, "flag-ee": 13, "flag-dk": 13,
         "wall-shelf": 5, "knit-basket": 9, "door-hand": 4, "icon-heart": 14,
         # (The laundry cart is kept at its size: its rows cut, not shrunk, and its rim mended; the
         # feather toy is a teaser lying on the shelf now, its handle made purple to stand out from the
         # shelf's wood: `assets/source/things/tries/README.md`.)
         "feather-toy": 12}

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
BY_MAJORITY = {"flag-se", "flag-fi", "flag-ee", "flag-dk", "flag-ua", "feather-toy"}
# Shrunk keeping a thin white line that reads it, then outlined: the tennis ball's seam (by majority
# it was lost, a plain yellow dot; the user: "has to look like a tennis ball", and chose an olive
# outline, 2026-11-17). name -> the outline's colour.
SEAM = {"tennis-ball": "a2a947"}


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


def piece(path):
    img = Image.open(path).convert("RGBA")
    img = img.crop(img.getbbox())
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
    if path.stem not in SEAM:
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
    return img


def build():
    pieces = [(p.stem, piece(p)) for p in sorted(SRC.glob("*.png")) if p.stem not in SKIP]
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
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        big = Image.new("RGBA", sheet.size, (150, 160, 175, 255))
        big.alpha_composite(sheet)
        big.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(out)


if __name__ == "__main__":
    build()
