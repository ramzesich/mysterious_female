"""The owner's toss (approved 2026-11-17) with the game's own tennis ball in her hand.

PixMiniMax drew a white ball in her fingers and a yellow one in the air; both are taken out, and
the game's ball (`tennis-ball` in assets/sprites/things.png, the one that flies) is put behind her
hand where she holds it: at her hip as it comes out of her pocket (raw frame 5), held out in her
cupped hand, her fingertips over its lower half (6). In 7 her hand opens: no ball of its own, the
game's flight starts there from where 6 holds it (`TOSS` in src/world/movers.js), so it never
hangs over her hand. Raw frame 0 is her standing picture (left out).

    python assets/source/people/dogowner-raw/clips/owner-toss/ball_in_hand.py
"""
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
OUT = ROOT / "assets" / "source" / "people" / "dogowner" / "toss"

# The ball's middle in the 64 px frames, and what the generator drew of its own ball there.
HELD = {5: (40, 32), 6: (45, 23)}
CLEAR = {5: [(37, 33)], 6: [(44, 23), (43, 24), (43, 25), (43, 26)],
         7: [(x, y) for x in range(41, 49) for y in range(15, 22)]}


def ball():
    f = json.loads((ROOT / "assets" / "sprites" / "things.json").read_text())["frames"]["tennis-ball"]["frame"]
    sheet = Image.open(ROOT / "assets" / "sprites" / "things.png").convert("RGBA")
    return sheet.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


def main():
    b = ball()
    OUT.mkdir(parents=True, exist_ok=True)
    for i in range(1, 9):
        im = Image.open(HERE / f"{i}.png").convert("RGBA")
        for xy in CLEAR.get(i, []):
            im.putpixel(xy, (0, 0, 0, 0))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if i in HELD:
            cx, cy = HELD[i]
            out.alpha_composite(b, (cx - b.width // 2, cy - b.height // 2))
        out.alpha_composite(im)
        out.save(OUT / f"{i - 1}.png")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
