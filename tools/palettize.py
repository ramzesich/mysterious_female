"""Converts pixel art to the game's one palette, Resurrect 64 (GAME_DESIGN.md §2.1).

Every opaque pixel is replaced with the perceptually nearest palette colour (CIELAB distance), and
alpha is snapped to fully opaque or fully transparent. Optional --remap rules override specific
results afterwards, e.g. to pick a fairer skin ramp than the nearest match would.

    python tools/palettize.py IN.png OUT.png [--remap FROM=TO ...] [--report]

FROM and TO are palette hex colours without '#'. Needs Pillow.
"""

import argparse
from pathlib import Path

from PIL import Image

PALETTE_FILE = Path(__file__).resolve().parent.parent / "assets" / "palette" / "resurrect-64.hex"


def load_palette():
    lines = PALETTE_FILE.read_text(encoding="utf-8").split("\n")
    return [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in (l.strip() for l in lines) if h and not h.startswith(";")]


def srgb_to_lab(rgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def nearest(rgb, palette_lab, cache):
    if rgb not in cache:
        lab = srgb_to_lab(rgb)
        cache[rgb] = min(palette_lab, key=lambda p: sum((a - b) ** 2 for a, b in zip(lab, p[1])))[0]
    return cache[rgb]


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def palettize(img, remap=None):
    palette = load_palette()
    palette_lab = [(c, srgb_to_lab(c)) for c in palette]
    remap = remap or {}
    cache = {}
    src = img.convert("RGBA")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    px, dst = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            c = nearest((r, g, b), palette_lab, cache)
            c = remap.get(c, c)
            dst[x, y] = (*c, 255)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--remap", nargs="*", default=[], metavar="FROM=TO")
    ap.add_argument("--report", action="store_true", help="print the palette colours used and their pixel counts")
    args = ap.parse_args()

    remap = {hex_rgb(a): hex_rgb(b) for a, b in (r.split("=") for r in args.remap)}
    out = palettize(Image.open(args.src), remap)
    out.save(args.dst)
    if args.report:
        counts = {}
        for r, g, b, a in out.get_flattened_data():
            if a:
                counts[(r, g, b)] = counts.get((r, g, b), 0) + 1
        for c, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"  {'%02x%02x%02x' % c}  {n}")


if __name__ == "__main__":
    main()
