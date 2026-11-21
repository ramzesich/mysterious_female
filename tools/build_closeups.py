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
# (The sardines keep their own blue silver too, the user's "as it is", 2026-11-20: on the palette they went purple.)
# (His navy t-shirt (13) and its logo too, the photo's own inks (the user, 2026-11-21): on the palette the navy went
# purple and the lilac a grey green.)
OWN_COLOURS = {"ball", "sardines", "tshirt", "sleepmask", "handheld"}
# Not close-ups: the t-shirt's logo alone, built and the user's own edit of it (`tools/draw_tshirt_logo.py`).
NOT_CLOSEUPS = {"tshirt-logo", "tshirt-logo-by-hand"}
# Colours changed after the palette, as in tools/build_things.py: the car's rubbery wheels to the
# palette's brightest cyans (the user: "two big rubbery cyan wheels").
RECOLOUR = {"car": {"0b8a8f": "0eaf9b", "0b5e65": "0b8a8f"},
            # The parasol came maroon: the world parasol's red and white (`parasol-closed`).
            "parasol": {"ae2334": "e83b3b", "6e2727": "ae2334", "966c6c": "c7dcd0", "fdcbb0": "ffffff",
                        "f68181": "ffffff"},
            # The socks in the world's stronger pink, their shading a shade deeper (the user, 2026-11-20:
            # "more similar to that in the game").
            "socks": {"eaaded": "ed8099", "ed8099": "cf657f", "cf657f": "a24b6f"}}
# Pixels set by hand after the palette (x, y in the trimmed picture -> colour): the parasol's handle had a
# band of the cloth's red across it (the user, 2026-11-20: "remove the red pixel from the parasol's
# handle"), now the pole's own two colours.
MEND = {"parasol": {(9, 98): "cd683d", (10, 98): "4c3e24", (9, 99): "cd683d", (10, 99): "4c3e24"},
        # The pills' white label: a dark title, lines of print, a dark mark (the user, 2026-11-20:
        # "something that resembles a text on its white label"; text in art is ours to draw).
        "pills": {(3, 30): "3e3546", (4, 30): "3e3546", (5, 30): "3e3546", (6, 30): "3e3546", (7, 30): "3e3546", (8, 30): "3e3546", (9, 30): "3e3546", (10, 30): "3e3546", (11, 30): "3e3546", (12, 30): "3e3546", (13, 30): "3e3546", (14, 30): "3e3546", (15, 30): "3e3546", (3, 31): "3e3546", (4, 31): "3e3546", (5, 31): "3e3546", (6, 31): "3e3546", (7, 31): "3e3546", (8, 31): "3e3546", (9, 31): "3e3546", (10, 31): "3e3546", (11, 31): "3e3546", (12, 31): "3e3546", (13, 31): "3e3546", (14, 31): "3e3546", (15, 31): "3e3546", (3, 35): "9babb2", (4, 35): "9babb2", (5, 35): "9babb2", (6, 35): "9babb2", (7, 35): "9babb2", (8, 35): "9babb2", (9, 35): "9babb2", (10, 35): "9babb2", (11, 35): "9babb2", (12, 35): "9babb2", (13, 35): "9babb2", (14, 35): "9babb2", (15, 35): "9babb2", (16, 35): "9babb2", (17, 35): "9babb2", (18, 35): "9babb2", (19, 35): "9babb2", (3, 38): "9babb2", (4, 38): "9babb2", (5, 38): "9babb2", (6, 38): "9babb2", (7, 38): "9babb2", (8, 38): "9babb2", (9, 38): "9babb2", (10, 38): "9babb2", (11, 38): "9babb2", (12, 38): "9babb2", (13, 38): "9babb2", (14, 38): "9babb2", (15, 38): "9babb2", (16, 38): "9babb2", (17, 38): "9babb2", (3, 41): "9babb2", (4, 41): "9babb2", (5, 41): "9babb2", (6, 41): "9babb2", (7, 41): "9babb2", (8, 41): "9babb2", (9, 41): "9babb2", (10, 41): "9babb2", (11, 41): "9babb2", (12, 41): "9babb2", (13, 41): "9babb2", (14, 41): "9babb2", (15, 41): "9babb2", (16, 41): "9babb2", (17, 41): "9babb2", (18, 41): "9babb2", (19, 41): "9babb2", (3, 44): "9babb2", (4, 44): "9babb2", (5, 44): "9babb2", (6, 44): "9babb2", (7, 44): "9babb2", (8, 44): "9babb2", (9, 44): "9babb2", (10, 44): "9babb2", (11, 44): "9babb2", (12, 44): "9babb2", (3, 48): "3e3546", (4, 48): "3e3546", (5, 48): "3e3546", (6, 48): "3e3546", (3, 49): "3e3546", (4, 49): "3e3546", (5, 49): "3e3546", (6, 49): "3e3546", (9, 49): "9babb2", (10, 49): "9babb2", (11, 49): "9babb2", (12, 49): "9babb2", (13, 49): "9babb2", (14, 49): "9babb2", (15, 49): "9babb2", (16, 49): "9babb2", (17, 49): "9babb2", (18, 49): "9babb2", (19, 49): "9babb2"}}
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
    img = recolour(img, RECOLOUR.get(path.stem, {}))
    for (x, y), c in MEND.get(path.stem, {}).items():
        img.putpixel((x, y), tuple(bytes.fromhex(c)) + (255,))
    return img


def build():
    pieces = []
    for p in sorted(SRC.glob("*.png")):
        if p.stem in NOT_CLOSEUPS:
            continue
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
