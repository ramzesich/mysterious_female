"""Lying flat, she lies on the floor (the user, 2026-11-19: "when lying down she should be on the ground, not float
above it"): her stand turned flat touched the floor only with her hair's tuft (14a) or her chest (14b), the rest of her
4 to 7 px over it, since her standing frame is not quite straight. Each column of a flat frame (under 23 px tall) is set
down by a straight line under her: the line that touches her lowest points along her length, a tuft a few columns wide
that hangs lower left out (it spreads on the floor: what falls under the floor row is cut)."""
from PIL import Image
FLOOR = 120


def lows(im):
    a = im.getchannel("A"); b = im.getbbox()
    return {x: max(y for y in range(b[1], b[3]) if a.getpixel((x, y))) for x in range(b[0], b[2])
            if any(a.getpixel((x, y)) for y in range(b[1], b[3]))}


def settle(im):
    b = im.getbbox()
    if not b or b[3] - b[1] > 22:
        return im, None
    lo = lows(im); xs = sorted(lo)
    # (A tuft: a column lower by 3 or more than the median of the columns about it.)
    def tuft(x):
        near = sorted(lo[q] for q in range(x - 6, x + 7) if q in lo)
        return lo[x] - near[len(near) // 2] >= 3
    pts = [(x, lo[x]) for x in xs if not tuft(x)]
    # The line under her: of all lines through two of her points with every other point on or above it, the one
    # that lies lowest in the middle (her points' lower hull, its edge under her middle).
    best = None; mid = (xs[0] + xs[-1]) / 2
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            (x0, y0), (x1, y1) = pts[i], pts[j]
            if not x0 <= mid <= x1 and best:
                continue
            k = (y1 - y0) / (x1 - x0)
            if all(y <= y0 + k * (x - x0) + 1e-9 for x, y in pts):
                if x0 <= mid <= x1:
                    best = (x0, y0, k); break
                best = best or (x0, y0, k)
        else:
            continue
        break
    x0, y0, k = best
    out = Image.new("RGBA", im.size); src = im.load(); o = out.load()
    for x in xs:
        s = FLOOR - round(y0 + k * (x - x0))
        for y in range(im.height):
            if src[x, y][3] and 0 <= y + s <= FLOOR:
                o[x, y + s] = src[x, y]
    return out, (round(FLOOR - y0 - k * (x0 - xs[0])), round(FLOOR - y0 - k * (xs[-1] - x0)))


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        im, s = settle(Image.open(p).convert("RGBA")); print(p, s)
