"""The windsocks (the hull's top review, finding 9; the user, 2026-11-27: generated, try B, "It has to be connected to
the pole with its ring in all positions"): one generated try with the same sock in three states side by side (limp,
half filled, full; `assets/source/windsock/tries/sheet-b.png`, its README has the job), in its own colours, alpha
snapped, each state cut to what it draws, into `assets/ship/windsock/` (`limp.png`, `half.png`, `full.png`) with
`windsock.json`: each state's `eye`, the middle of its swivel's eye (measured by hand: the same spot in all three), which
the game puts on its pole's top and turns the sock round.

    python tools/build_windsock.py
"""

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "windsock" / "tries" / "sheet-b.png"
OUT = ROOT / "assets" / "ship" / "windsock"
# Each state: its columns in the try, and its eye's middle from the state's own top left (px, a pixel's middle at .5).
STATES = {"limp": ((2, 19), (3.5, 3.0)), "half": ((28, 55), (3.5, 3.5)), "full": ((59, 94), (3.5, 3.5))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 128 else (0, 0, 0, 0)
    data = {}
    for name, ((x0, x1), eye) in STATES.items():
        part = im.crop((x0, 0, x1, im.height))
        bx0, by0, bx1, by1 = part.getbbox()
        assert bx0 == 0, (name, bx0)       # (the eye is the state's leftmost column)
        part = part.crop((0, by0, bx1, by1))
        part.save(OUT / f"{name}.png")
        data[name] = {"w": part.width, "h": part.height, "eye": list(eye)}
    (OUT / "windsock.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf8")
    print(json.dumps(data))


if __name__ == "__main__":
    main()
