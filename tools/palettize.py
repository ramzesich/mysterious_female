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


def paper_greys(img, tol=14):
    """White paper's greys put on the palette by lightness, before `palettize` (which would turn them
    pale green: Resurrect 64 has no light neutral grey). Only the near-neutral greys (within `tol`):
    her shirt's shades are tinted and keep to the palette's own. The sliding newspaper and her paper
    gags (`assets/source/things/newspaper-sliding/README.md`)."""
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a < 100 or max(r, g, b) - min(r, g, b) >= tol:
                continue
            light = (r + g + b) / 3
            if light < 90:
                continue
            px[x, y] = ((255, 255, 255) if light >= 200 else (199, 220, 208) if light >= 170
                        else (155, 171, 178) if light >= 130 else (127, 112, 138)) + (255,)
    return img


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


SKY, BLOUSE_SHADE = (0x8f, 0xd3, 0xff), (0x9b, 0xab, 0xb2)


def blouse_grey(img):
    """Her blouse's sky blue to its own grey-blue shade, after `palettize` (the user, 2026-11-23: "I still feel like blue
    pixels were added to Bumbusik's sprites"): the generator shaded her white blouse with pale blue-greys, and the
    palette's nearest to the palest is its sky blue, a few px of it in every frame of hers since her first sheet.
    Only sky blue joined (at a side or a corner, through more of it) to the blouse's white or grey-blue: loose drops of
    water stay blue (her sneeze's spray)."""
    img = img.copy()
    px = img.load()
    w, h = img.size
    sky = {(x, y) for y in range(h) for x in range(w) if px[x, y][3] and px[x, y][:3] == SKY}
    seen = set()
    for start in sky:
        if start in seen:
            continue
        part, stack, touches = [], [start], False
        seen.add(start)
        while stack:
            x, y = stack.pop()
            part.append((x, y))
            for nx in (x - 1, x, x + 1):
                for ny in (y - 1, y, y + 1):
                    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in seen:
                        continue
                    q = px[nx, ny]
                    if (nx, ny) in sky:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
                    elif q[3] and q[:3] in ((255, 255, 255), BLOUSE_SHADE):
                        touches = True
        if touches:
            for x, y in part:
                px[x, y] = BLOUSE_SHADE + (255,)
    return img


WATER_BLUES = [(0x48, 0x4a, 0x77), (0x4d, 0x65, 0xb4), (0x4d, 0x9b, 0xe6), (0x8f, 0xd3, 0xff)]


def is_water(c):
    """Water as PixelLab draws it on her: cyan-blue, its green well above its red (drips #6889ab, #92c1d5, splashes
    #a1e4f1). Her blouse's pale blues are lavender-blue, green near red (#b6c9e6, #a1afce): not one px of her 399 dry
    generated frames is cyan-blue (measured 2026-11-23)."""
    r, g, b = c[:3]
    # (The palette's own sky blue is not water: a clip's first frame is her built sheet's, its blouse's sky blue in it.)
    return b - r >= 20 and b >= g and g - r >= 25 and (r, g, b) != SKY


def water_blue(src, pal):
    """Her wet clips (the user, 2026-11-23: the palette had turned the water on her grey): each px of `src` (the frame
    before `palettize`) that is water goes on the palette's nearest true blue in `pal` instead of its lavender-grey."""
    pal = pal.copy()
    s, p = src.convert("RGBA").load(), pal.load()
    for y in range(pal.height):
        for x in range(pal.width):
            c = s[x, y]
            if c[3] >= 128 and is_water(c):
                p[x, y] = min(WATER_BLUES, key=lambda w: sum((a - b) ** 2 for a, b in zip(w, c[:3]))) + (255,)
    return pal


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
