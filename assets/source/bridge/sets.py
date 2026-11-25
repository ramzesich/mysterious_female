"""Green copies of the bridge's forward end for the clips made on it (docs/near-catch-6-remake-log.md): the place's
shapes kept (the console, the alarm station, the floor, the hatch and its ladder), every colour a green by its
lightness, so that a figure is cut out of each frame by colour whatever it crosses. Writes sets/<name>.png.

    python assets/source/bridge/sets.py
"""
import json
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "sets"
OUT.mkdir(exist_ok=True)
V = json.load(open(HERE / "src" / "forward.json"))
D10, CEIL, CONSOLE, STATION, LADDER = 704, 576, 1930, 1985, 1864
SHIP = json.load(open(ROOT / "assets/ship/ship.json"))["frames"]
ATLAS = Image.open(ROOT / "assets/ship/ship.png").convert("RGBA")
BR = json.load(open(ROOT / "assets/ship/bridge/bridge.json"))


def piece(name):
    f = SHIP[name].get("frame", SHIP[name])
    return ATLAS.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


def place(ladder=False):
    """The place as the game will show it: the console and the station at their new spots; the hatch open."""
    im = Image.open(HERE / "rough" / "place.png").convert("RGBA")
    con = piece("bridge-console")
    im.alpha_composite(con, (CONSOLE - con.width // 2 - V["vx"], D10 - con.height - V["vy"]))
    st = Image.open(ROOT / "assets/ship/bridge/station-full.png").convert("RGBA")
    im.alpha_composite(st, (STATION + BR["station"]["dx"] - V["vx"], D10 + BR["station"]["dy"] - V["vy"]))
    col = Image.open(ROOT / "assets/ship/bridge/collar.png").convert("RGBA")
    im.alpha_composite(col, (LADDER + BR["collar"]["dx"] - V["vx"], CEIL + BR["collar"]["dy"] - V["vy"]))
    if ladder:
        lad = Image.open(ROOT / "assets/ship/bridge/ladder.png").convert("RGBA")
        im.alpha_composite(lad, (LADDER + BR["ladder"]["dx"] - V["vx"], CEIL + BR["ladder"]["top"] - V["vy"]))
    return im.convert("RGB")


def green(im):
    """Every colour a green by its lightness (110 to 230): the shapes stay, nothing is a figure's colour."""
    out = im.copy()
    p = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b = p[x, y]
            lum = (r * 3 + g * 6 + b) / 10
            v = round(110 + lum * 120 / 255)
            p[x, y] = (0, v, round(v * 0.28))
    return out


def figure(path, at=None):
    """A figure off its green ground: (picture, bbox)."""
    im = Image.open(path).convert("RGBA")
    p = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = p[x, y]
            if g > r + 60 and g > b + 60:
                p[x, y] = (0, 0, 0, 0)
    return im, im.getbbox()


def crop(im, x0, y0, w, h):
    return im.crop((x0 - V["vx"], y0 - V["vy"], x0 - V["vx"] + w, y0 - V["vy"] + h))


if __name__ == "__main__":
    import sys
    tries = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "tries"
    meta = {}
    full = place()
    full.save(OUT / "place-full.png")
    # --- the officer's swing: he at 1945, the station ahead of him; ending sat in front of the console -----------------
    X0, Y0 = 1880, 592
    g = green(crop(full, X0, Y0, 128, 128))
    g.save(OUT / "swing-set.png")
    start = g.convert("RGBA")
    f, bb = figure(tries / "stalk-s3-8.png")
    start.alpha_composite(f, (1945 - X0 - 64, 0))
    start.convert("RGB").save(OUT / "swing-start.png")
    end = g.convert("RGBA")
    f, bb = figure(tries / "netted-s2.png")
    body = (bb[0] + bb[2]) // 2
    dx = (1934 - X0) - 76          # his seat: the picture's column 76 is under his hips
    end.alpha_composite(f, (dx, 0))
    end.convert("RGB").save(OUT / "swing-end.png")
    meta["swing"] = {"x0": X0, "y0": Y0, "start_dx": 1945 - X0 - 64, "end_dx": dx, "netted_bbox": bb}
    for n in ("swing-start", "swing-end"):
        im = Image.open(OUT / f"{n}.png")
        im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(OUT / f"{n}-x4.png")
    json.dump(meta, open(OUT / "sets.json", "w"), indent=1)
    print(meta)


def climb_set(tries):
    """Bumbot's climb: the hatch open, its ladder down, the console's forward end; mirrored, since his sheet faces east
    and he goes forward (the picture's column c is the world's x 1960 - c; its row r the world's y 560 + r)."""
    full = place(ladder=True)
    g = green(crop(full, 1833, 560, 128, 144).transpose(Image.FLIP_LEFT_RIGHT))
    g.save(OUT / "climb-set.png")
    cat = Image.open(ROOT / "assets/sprites/bumbot.png").convert("RGBA")
    n = 33                                         # his run's first frame
    f = cat.crop(((n % 48) * 64, (n // 48) * 64, (n % 48) * 64 + 64, (n // 48) * 64 + 64))
    start = g.convert("RGBA")
    # his paws on the console's top (46 px over the floor), his middle at the world's x 1920
    start.alpha_composite(f, (1960 - 1920 - 32, 144 - 46 - (64 - CAT_UNDER)))
    start.convert("RGB").save(OUT / "climb-start.png")
    start.convert("RGB").resize((128 * 4, 144 * 4), Image.NEAREST).save(OUT / "climb-start-x4.png")


CAT_UNDER = 8          # rows under his floor in his sheet's cells
if __name__ == "__main__":
    climb_set(HERE / "tries")
