"""The party's balloons drifted across deck 8's corridor (part 11's item 14, the user, 2026-11-28): the five generated
balloons (`assets/source/things/tries/balloons/cut/`, the user's choice; its README) in their own colours, each upright
(`u`, on its knot) and lying on its side with its knot to the left (`l`) or the right (`r`), a turn of a quarter by
whole pixels. One sheet of 22 x 22 cells, each picture set on the cell's bottom row and centred:
`assets/ship/balloons.png`, frame `colour index * 3 + pose index` (`COLOURS`, `POSES`, also in `balloons.json`).
Played by `Balloons` in `src/world/movers.js`.
And every other balloon of the party in the same art (the user: "all of the balloons should match"): the bunch tied to
its door, the five on strings drawn by rule to one tie point at its foot's middle (`balloon-bunch.png`, hung by that
point, as the drawn bunch it replaces was), and the two against the ceiling, each with a short string hanging
(`balloon-float-<colour>.png`, hung by its top)."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "things" / "tries" / "balloons" / "cut"
OUT = ROOT / "assets" / "ship"
COLOURS = ["red", "yellow", "blue", "green", "pink"]
POSES = ["u", "l", "r"]
CELL = 22
STRING = (155, 171, 178, 255)          # (the palette's light grey: the drawn strings' cream was lost on the corridor's wall)
# The bunch: each balloon's top left in a 50 x 64 picture, back ones first; their strings to (25, 63).
BUNCH = (50, 64, [("red", 2, 4), ("yellow", 17, 0), ("blue", 32, 4), ("pink", 9, 16), ("green", 25, 14)])
FLOAT = 16                             # the string under a balloon against the ceiling (px)
# The handle of the open cabin door (`door-cabin-ajar`, 34 x 74, stood by its foot's middle) the bunch is tied to (the user,
# 2026-11-28: "tied to the door handle. The handle should obscure the ropes"; "not the door handle mount"): the lever
# across its mount, its box in that picture (rows 37 to 39), and its pixels there that are not the leaf's face, drawn again
# over the strings (`balloon-handle.png`); the knot on its middle, (13, 38).
HANDLE = (10, 37, 16, 40)


def handle():
    meta = json.loads((OUT / "ship.json").read_text(encoding="utf8"))["frames"]["door-cabin-ajar"]["frame"]
    door = Image.open(OUT / "ship.png").convert("RGBA").crop((meta["x"], meta["y"], meta["x"] + meta["w"], meta["y"] + meta["h"]))
    leaf = {door.getpixel((16, 38))}                                    # (the leaf's face, beside the lever's end)
    out = door.crop(HANDLE)
    for y in range(out.height):
        for x in range(out.width):
            if out.getpixel((x, y)) in leaf:
                out.putpixel((x, y), (0, 0, 0, 0))
    return out


def knot(im, x, y):
    """The knot's lowest middle pixel of a balloon placed at (x, y)."""
    a = im.getchannel("A")
    row = max(j for j in range(im.height) if any(a.getpixel((i, j)) for i in range(im.width)))
    cols = [i for i in range(im.width) if a.getpixel((i, row))]
    return x + cols[len(cols) // 2], y + row


def bunch(pics):
    w, h, items = BUNCH
    out = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(out)
    for c, x, y in items:
        kx, ky = knot(pics[c], x, y)
        d.line([(kx, ky + 1), (w // 2, h - 1)], fill=STRING, width=1)
    for c, x, y in items:
        out.alpha_composite(pics[c], (x, y))
    return out


def floating(im):
    out = Image.new("RGBA", (im.width, im.height + FLOAT))
    out.alpha_composite(im, (0, 0))
    kx, ky = knot(im, 0, 0)
    ImageDraw.Draw(out).line([(kx, ky + 1), (kx, out.height - 1)], fill=STRING, width=1)
    return out


def main():
    sheet = Image.new("RGBA", (CELL * len(POSES) * len(COLOURS), CELL))
    for ci, c in enumerate(COLOURS):
        im = Image.open(SRC / f"{c}.png").convert("RGBA")
        for pi, t in enumerate((im, im.transpose(Image.ROTATE_90), im.transpose(Image.ROTATE_270))):
            assert t.width <= CELL and t.height <= CELL, (c, t.size)
            i = ci * len(POSES) + pi
            sheet.alpha_composite(t, (i * CELL + (CELL - t.width) // 2, CELL - t.height))
    sheet.save(OUT / "balloons.png")
    pics = {c: Image.open(SRC / f"{c}.png").convert("RGBA") for c in COLOURS}
    bunch(pics).save(OUT / "balloon-bunch.png")
    for c in ("yellow", "green"):
        floating(pics[c]).save(OUT / f"balloon-float-{c}.png")
    handle().save(OUT / "balloon-handle.png")
    (OUT / "balloons.json").write_text(json.dumps({"cell": CELL, "colours": COLOURS, "poses": POSES}) + "\n", encoding="utf8")
    print("wrote", OUT / "balloons.png", sheet.size)


if __name__ == "__main__":
    main()
