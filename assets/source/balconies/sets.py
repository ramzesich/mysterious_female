"""The sets her balcony clips are made on: the game's own picture of two balconies (the lower rail, the partition to the
ceiling, its fin up the slab), turned green so that she can be cut out by colour, with her own frame (in the grip
socks) where each move starts and ends. python assets/source/balconies/sets.py <base.png> <vx> <vy> <her-socks.png>

  sets/along-start.png, along-end.png   128 x 128: a jump at the partition; a landing on its other side
  sets/up-start.png, up-end.png         128 x 256: stood at the partition on deck 9; stood at it on deck 10
  (down is up's two pictures the other way round)
"""
import json, sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PART = 8003                 # the partition's middle (world px); its panel 8000..8006
F9, F10 = 848, 704
CELL = 84


def green(im):
    im = im.convert("RGB"); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            l = (r * 3 + g * 6 + b) // 10
            px[x, y] = (l // 5, 70 + l * 150 // 255, l // 5)
    return im


def main():
    base, vx, vy, sheet = Image.open(sys.argv[1]).convert("RGB"), int(sys.argv[2]), int(sys.argv[3]), Image.open(sys.argv[4]).convert("RGBA")
    meta = json.loads((ROOT / "assets/sprites/her.json").read_text(encoding="utf8"))
    A, cols = meta["anims"], meta["cols"]
    fr = lambda n: sheet.crop(((n % cols) * CELL, (n // cols) * CELL, (n % cols + 1) * CELL, (n // cols + 1) * CELL))
    out = HERE / "sets"; out.mkdir(exist_ok=True)

    def make(name, x0, y0, w, h, her):
        """The set's box in world px; `her`: (frame, world x of her middle, world y of her feet)."""
        im = green(base.crop((x0 - vx, y0 - vy, x0 - vx + w, y0 - vy + h))).convert("RGBA")
        n, hx, hy = her
        im.alpha_composite(fr(n), (round(hx - x0 - CELL / 2), round(hy - y0 - CELL + 1)))
        im.convert("RGB").save(out / f"{name}.png")

    ax, ay = PART - 64, F9 - 112
    make("along-start", ax, ay, 128, 128, (A["rise"][0], PART - 11, F9 - 6))
    make("along-end", ax, ay, 128, 128, (A["fall"][0], PART + 11, F9 - 6))
    bx, by = PART - 72, 606
    make("up-start", bx, by, 128, 256, (A["stand"][0], PART - 11, F9))
    make("up-end", bx, by, 128, 256, (A["stand"][0], PART - 11, F10))
    (out / "boxes.json").write_text(json.dumps(dict(along=[ax, ay, 128, 128], up=[bx, by, 128, 256], part=PART, f9=F9, f10=F10)))
    print("wrote", out)


if __name__ == "__main__":
    main()
