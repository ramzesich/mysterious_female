"""The funnel's top: the ship's horn on its post, its cord and the engineer's toolbox (the hull's top review, the user,
2026-11-27: "generate proper horns and the horn cable. Also, generate the boxes there, that the tangerine is placed on";
the user chose horn B and toolbox A). Generated tries in `assets/source/funnel-top/tries/` (its README has the jobs), in
their own colours (on the palette the pole went green and the lunch box purple), alpha snapped; into
`assets/ship/funnel-top/` with `funnel-top.json`, the places the game needs:

- `horn.png`: the post's foot on the picture's bottom row; `pole` its middle column, `seat` the row of the top bar's top
  (Bumbot sits there), `hang` [x, y] where the cord hangs from (under the bar's aft end).
- `cord-rope.png`: the rope, one column strip repeating every two rows, long enough for any pull; the game crops it.
- `cord-handle.png`: the knot and the red pull handle; `knot` the rows of it over the handle's wood.
- `toolbox.png`: the box on its bottom row; `lid` its lid's top row, `spot` the middle of its free lid between the
  carry handle and the lunch box (where the tangerine lies).

    python tools/build_funnel_top.py
"""

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "funnel-top" / "tries"
OUT = ROOT / "assets" / "ship" / "funnel-top"


def opaque(im):
    """Alpha snapped to fully opaque or fully empty."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 128 else (0, 0, 0, 0)
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {}

    horn = opaque(Image.open(SRC / "horn-b.png"))
    x0, y0, x1, y1 = horn.getbbox()
    horn = horn.crop((x0, y0, x1, y1))
    horn.save(OUT / "horn.png")
    # (In the try: the pole's columns 37 to 41 at its foot, the top bar's top at row 17, its aft end at column 44, its
    # underside at row 22.)
    data["horn"] = {"w": horn.width, "h": horn.height, "pole": 39 - x0, "seat": 18 - y0, "hang": [43 - x0, 22 - y0]}

    cord = opaque(Image.open(SRC / "cord-a.png"))
    rope = cord.crop((15, 0, 18, 2))
    strip = Image.new("RGBA", (3, 96))
    for y in range(0, 96, 2):
        strip.paste(rope, (0, y))
    strip.save(OUT / "cord-rope.png")
    handle = cord.crop((14, 37, 19, 51))
    handle.save(OUT / "cord-handle.png")
    data["cord"] = {"rope": 3, "handle": [handle.width, handle.height], "knot": 4}

    box = opaque(Image.open(SRC / "box-a.png"))
    x0, y0, x1, y1 = box.getbbox()
    box = box.crop((x0, y0, x1, y1))
    box.save(OUT / "toolbox.png")
    # (In the try: the lid's top at row 15, free from column 24 to 29 between the handle and the lunch box; the
    # tangerine 2 px left of their middle, clear of the lunch box's open lid.)
    data["toolbox"] = {"w": box.width, "h": box.height, "lid": 15 - y0, "spot": 25 - x0}

    (OUT / "funnel-top.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf8")
    print(json.dumps(data))


if __name__ == "__main__":
    main()
