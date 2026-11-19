"""The close-ups (the user, 2026-11-19, "A and C"): each thing to find and each key card seen close,
shown in the middle of the screen when she gets it (`world.closeup()` in src/world/world.js). From the
PixelLab pictures in assets/source/closeups/ (its README has their ids) to the atlas
assets/sprites/closeups.png + closeups.json, each on the palette and trimmed; shown at 2x, the world's
own pixel size.

    python tools/build_closeups.py [--preview out.png]

A frame is named for what she gets: a thing to find by its keep name ("keep:cat:wool" -> `wool`),
a card `card-<card>`. The world's sprites of most of these things are their close-ups shrunk
(tools/build_things.py, `FROM_CLOSEUP`).
"""

import json
import sys
from pathlib import Path

from PIL import Image

from palettize import palettize

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "closeups"
OUT = ROOT / "assets" / "sprites"

# Kept in their own colours: the tennis ball's fluorescent felt went olive on the palette (as in the
# world, where the user chose it so).
OWN_COLOURS = {"ball"}
# Colours changed after the palette, as in tools/build_things.py: the car's rubbery wheels to the
# palette's brightest cyans (the user: "two big rubbery cyan wheels").
RECOLOUR = {"car": {"0b8a8f": "0eaf9b", "0b5e65": "0b8a8f"}}
# The four cards: one picture, its stripe (the generated blue, on the palette) in each card's colour,
# the colours of `CARD_COLOURS` in src/progression.js.
CARD_STRIPE = "4d65b4"
CARDS = {"deck": "4d9be6", "ent": "e83b3b", "hk": "1ebc73", "off": "f9c22b"}


def recolour(img, swaps):
    swaps = {tuple(bytes.fromhex(k)): tuple(bytes.fromhex(v)) for k, v in swaps.items()}
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in swaps:
                px[x, y] = swaps[(r, g, b)] + (a,)
    return img


def picture(path):
    img = Image.open(path).convert("RGBA")
    img = img.crop(img.getbbox())
    if path.stem not in OWN_COLOURS:
        img = palettize(img)
    return recolour(img, RECOLOUR.get(path.stem, {}))


def build():
    pieces = []
    for p in sorted(SRC.glob("*.png")):
        img = picture(p)
        if p.stem == "key-card":
            pieces += [(f"card-{card}", recolour(img.copy(), {CARD_STRIPE: c})) for card, c in CARDS.items()]
        else:
            pieces.append((p.stem, img))
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
    sheet.save(OUT / "closeups.png")
    (OUT / "closeups.json").write_text(json.dumps({"frames": frames, "meta": {"image": "closeups.png"}}, indent=1), encoding="utf-8")
    print("wrote assets/sprites/closeups.png:", ", ".join(f"{n} {im.width}x{im.height}" for n, im in pieces))
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        big = Image.new("RGBA", sheet.size, (40, 40, 52, 255))
        big.alpha_composite(sheet)
        big.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(out)


if __name__ == "__main__":
    build()
