"""His navy t-shirt's close-up (§4 2.1, thing 13, the user, 2026-11-21): the top half of a big generated shirt
(`assets/source/closeups/tries/tshirt/7.png`, the user's choice of look, try 2, at twice the size; "only the top
half of the t-shirt") with the logo from his photo on the wearer's left chest (the right as we look).

The logo is PixelLab's `image_to_pixelart` of the photo's print (`tries/tshirt/logo-a.png`, the user's choice of
four), then: its colours set to the photo's (each pixel to the nearest of its inks, the inks measured on the
photo and carried over by the fabric's own navy), its arch a pixel wider each side, and its words stamped in
pixel letters over the generator's scribble ("bluevine" and "cares" must be legible: the user).

    python tools/draw_tshirt_logo.py [--cares small|big] [--out PATH]

`--write-built` writes the built logo alone to `tshirt-logo.png` (on the shirt's navy, for editing); if
`tshirt-logo-by-hand.png` is there (the user's own edit of it, 2026-11-21: never written by a tool), that is put on
the shirt instead of the built one.
"""
import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TRIES = ROOT / "assets/source/closeups/tries/tshirt"
SHIRT = TRIES / "7.png"
LOGO = TRIES / "logo-a.png"
OUT = ROOT / "assets/source/closeups/tshirt.png"
# The built logo alone (candidate 2, the user's choice), written for the user to edit; and the user's own edit of it,
# which is used in its place while it is there (never written by a tool).
LOGO_BUILT = ROOT / "assets/source/closeups/tshirt-logo.png"
LOGO_BY_HAND = ROOT / "assets/source/closeups/tshirt-logo-by-hand.png"

# The photo's inks, carried from the photo's light (its fabric at 108,105,112, its arch at 248,246,231) to the
# shirt's (its navy 19,29,54, the arch a warm white): each channel mapped linearly between the two.
WHITE = (240, 238, 228, 255)
BLUE = (79, 112, 196, 255)          # the diamond and the left leaf (photo 146,161,209)
LILAC = (207, 190, 202, 255)        # the left lobe (photo 227,214,213)
LILAC_LEAF = (196, 176, 192, 255)   # the right leaf, a shade deeper (photo 220,204,206)
INK = (19, 29, 54, 255)             # "bluevine", printed in the shirt's navy

# The generator's colours sorted into the inks (its own centres); navy is the shirt (transparent here).
CENTRES = [((244, 239, 230), "white"), ((205, 203, 205), "white"), ((215, 175, 205), "lilac"),
           ((110, 120, 175), "blue"), ((20, 26, 48), "navy")]

# "bluevine": lowercase, x-height 4, ascenders to 6 rows, 3 px wide (l and i one).
SMALL = {
    "b": ["X..", "X..", "XXX", "X.X", "X.X", "XXX"],
    "l": ["X", "X", "X", "X", "X", "X"],
    "u": ["...", "...", "X.X", "X.X", "X.X", ".XX"],
    "e": ["...", "...", ".XX", "XXX", "X..", ".XX"],
    "v": ["...", "...", "X.X", "X.X", "X.X", ".X."],
    "i": ["X", ".", "X", "X", "X", "X"],
    "n": ["...", "...", "XX.", "X.X", "X.X", "X.X"],
}
# "cares", as on the shirt: bigger than "bluevine" (a two-storey a: a round one read as an o, "cores").
CARES = {
    "small": {
        "c": [".XXX", "X...", "X...", "X...", ".XXX"],
        "a": [".XX.", "...X", ".XXX", "X..X", ".XXX"],
        "r": ["X.XX", "XX..", "X...", "X...", "X..."],
        "e": [".XX.", "X..X", "XXXX", "X...", ".XXX"],
        "s": [".XXX", "X...", ".XX.", "...X", "XXX."],
    },
    "big": {
        "c": [".XXXX", "X....", "X....", "X....", ".XXXX"],
        "a": [".XXX.", "....X", ".XXXX", "X...X", ".XXXX"],
        "r": ["X.XX", "XX..", "X...", "X...", "X..."],
        "e": [".XXX.", "X...X", "XXXXX", "X....", ".XXXX"],
        "s": [".XXXX", "X....", ".XXX.", "....X", "XXXX."],
    },
}


def word(font, text, gap=1):
    px, x = set(), 0
    for c in text:
        g = font[c]
        for y, row in enumerate(g):
            for dx, ch in enumerate(row):
                if ch == "X":
                    px.add((x + dx, y))
        x += len(g[0]) + gap
    return px, x - gap, len(next(iter(font.values())))


def ink(p):
    if p[3] == 0:
        return "navy"
    return min(CENTRES, key=lambda c: sum((a - b) ** 2 for a, b in zip(p[:3], c[0])))[1]


def logo(cares="big"):
    src = Image.open(LOGO).convert("RGBA")
    w, h = src.size
    kinds = [[ink(src.getpixel((x, y))) for x in range(w)] for y in range(h)]
    # The arch a pixel wider each side: its column 2 and column 26 (white down the sides) said twice.
    cols = list(range(w))
    cols = cols[:3] + [2] + cols[3:27] + [26] + cols[27:]
    kinds = [[row[c] for c in cols] for row in kinds]
    w = len(cols)
    # The generator's blue edging where white meets navy (the dome's top, round the dark lobe) is no ink of the
    # print's: a blue pixel by the navy with fewer than three blue neighbours goes to the navy.
    def around(x, y):
        return [kinds[j][i] for j in range(y - 1, y + 2) for i in range(x - 1, x + 2)
                if (i, j) != (x, y) and 0 <= i < w and 0 <= j < h]
    for y in range(h):
        for x in range(w):
            if kinds[y][x] == "blue":
                n = around(x, y)
                if "navy" in n and n.count("blue") < 3:
                    kinds[y][x] = "navy"
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            k = kinds[y][x]
            if k == "navy":
                continue
            # (The right leaf a shade deeper than the lobe, as on the photo.)
            c = {"white": WHITE, "blue": BLUE, "lilac": LILAC if y < 14 else LILAC_LEAF}[k]
            out.putpixel((x, y), c)
    # The arch's foot: rows 21 to 27 white across the arch (the generator's word and the grey under it out).
    left = min(x for x in range(w) if kinds[25][x] != "navy")
    right = max(x for x in range(w) if kinds[25][x] != "navy")
    for y in range(21, 28):
        for x in range(left, right + 1):
            out.putpixel((x, y), WHITE)
    # Under the arch, the generator's "cares" out (the shirt shows).
    for y in range(28, h):
        for x in range(w):
            out.putpixel((x, y), (0, 0, 0, 0))
    px, ww, rows = word(SMALL, "bluevine")
    x0, y0 = left + (right - left + 1 - ww) // 2, 21
    for (x, y) in px:
        out.putpixel((x0 + x, y0 + y), INK)
    px, ww, rows = word(CARES[cares], "cares")
    x0, y0 = left + (right - left + 1 - ww + 1) // 2, 30
    for (x, y) in px:
        out.putpixel((x0 + x, y0 + y), WHITE)
    return out.crop(out.getchannel("A").getbbox())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cares", default="big", choices=CARES)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--logo-out", default=None, help="also write the logo alone")
    ap.add_argument("--write-built", action="store_true",
                    help="write the built logo to tshirt-logo.png, on navy (the user once edited that file itself)")
    ap.add_argument("--at", default="118,40", help="the logo's top left on the shirt")
    ap.add_argument("--cut", type=int, default=92, help="the row the top half ends at (0: whole)")
    a = ap.parse_args()
    lg = logo(a.cares)
    if a.logo_out:
        lg.save(a.logo_out)
    elif a.write_built:
        # On a flat ground of the shirt's navy, so any editor will do (Paint keeps no transparency).
        flat = Image.new("RGBA", lg.size, INK)
        flat.alpha_composite(lg)
        flat.convert("RGB").save(LOGO_BUILT)
    if LOGO_BY_HAND.exists():
        # The navy is the shirt: transparent, so the shirt's own fabric shows there ("bluevine" too, as on the
        # photo, where its letters are the shirt seen through the print).
        lg = Image.open(LOGO_BY_HAND).convert("RGBA")
        lg.putdata([(0, 0, 0, 0) if p[:3] == INK[:3] else p for p in lg.get_flattened_data()])
        print("using the hand-edited logo", LOGO_BY_HAND.name)
    im = Image.open(SHIRT).convert("RGBA")
    ox, oy = map(int, a.at.split(","))
    im.alpha_composite(lg, (ox, oy))
    if a.cut:
        im = im.crop((0, 0, im.width, a.cut))
    im = im.crop(im.getchannel("A").getbbox())
    im.save(a.out)
    print("wrote", a.out, im.size, "logo", lg.size)


if __name__ == "__main__":
    main()
