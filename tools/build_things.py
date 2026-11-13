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
         "sunbather-3": 27, "sunbather-4": 22}

# Colours changed after the palette: PixelLab drew the parasol's stripes maroon and pink; in the
# game they are the life rings' red and white. name -> {from: to}.
RECOLOUR = {
    "parasol-open": {"7a3045": "e83b3b", "9e4539": "e83b3b", "6e2727": "ae2334", "966c6c": "c7dcd0",
                     "9babb2": "ffffff"},
    "parasol-closed": {"c32454": "e83b3b", "7a3045": "ae2334", "831c5d": "ae2334", "966c6c": "c7dcd0",
                       "fdcbb0": "ffffff", "9babb2": "ffffff"},
}
# Rows taken out of a piece (its own rows, top to bottom, after trimming) rather than shrinking it,
# which would blur its stripes: the old lady's parasol came as long as she is tall, open and furled.
CUT_ROWS = {"parasol-open": [(30, 44)], "parasol-closed": [(16, 28), (45, 50)]}
# A piece leaning (nothing stands by itself on a crook handle): its rows pushed sideways, one px
# for every so many rows up from its foot, to the left. The furled parasol leans on the sunbed.
LEAN = {"parasol-closed": 3}


def piece(path):
    img = Image.open(path).convert("RGBA")
    img = img.crop(img.getbbox())
    if path.stem in CUT_ROWS:
        for y0, y1 in reversed(CUT_ROWS[path.stem]):
            cut = Image.new("RGBA", (img.width, img.height - (y1 - y0)), (0, 0, 0, 0))
            cut.alpha_composite(img.crop((0, 0, img.width, y0)), (0, 0))
            cut.alpha_composite(img.crop((0, y1, img.width, img.height)), (0, y0))
            img = cut
    h = SCALE.get(path.stem)
    if h and h != img.height:
        w = max(1, round(img.width * h / img.height))
        img = img.resize((w, h), Image.BOX)
        # Box resampling leaves soft edges: alpha back to on or off.
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = px[x, y]
                px[x, y] = (r, g, b, 255 if a >= 128 else 0)
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
    pieces = [(p.stem, piece(p)) for p in sorted(SRC.glob("*.png"))]
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
