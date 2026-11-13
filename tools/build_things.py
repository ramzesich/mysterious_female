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
         "sunbather-1": 33, "sunbather-2": 20}


def piece(path):
    img = Image.open(path).convert("RGBA")
    img = img.crop(img.getbbox())
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
    return palettize(img)


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
