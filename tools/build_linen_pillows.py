"""The linen room's pillows (near-catch 4, the user, 2026-11-24: "The laundry cart has stack of pillows on top of it ...
When we push it, Bumbot jumps (like now), the pillows scatter"): PixelLab's clip of the stack going over
(assets/source/linen-pillows/clip/, 17 pictures of 208 x 128 on a flat green set, the cart a flat blue shape; its README
has the jobs) cut into the game's pieces, in assets/ship/linen-pillows/:

- `ride.png`: the pillows still in the cart, frame by frame, in the cart's own px (the game moves them with its cart);
- `free.png`: those in the air and on the floor, in the room's px (they stay where the room has them);
- `near.png`, `far.png`: the four as they lie at the end, the two behind the cart and the two at the aft rack;
- `pillows.json`: the frames' cells and where each stands.

A pixel is a pillow's when it is neither the set's green nor the cart's blue. The clip's frame 1, a smear of the whole
stack, is left out. A piece is in the cart while its foot is at the rim and its middle over the cart, until the first
frame in which none is. Nothing of them is kept past the room's aft wall. The pillows keep their own colours.

    python tools/build_linen_pillows.py [--sheet out.png]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source" / "linen-pillows"
GAME = ROOT / "assets" / "ship" / "linen-pillows"

SEQ = [0] + list(range(2, 17))      # the clip's pictures used, in order (1 is a smear)
FLOOR, RIM = 116, 32                # the set's floor row; the cart's rim over it
START = 35                          # the cart picture's left edge on the set in the first frame (45 px wide, as the game's)
WALL = 199                          # the room's aft wall on the set: the set's left edge is 5887 in the world as the game
                                    # places it, the wall's face 6086
SPLIT = 140                         # lying at the end: left of this the two behind the cart, right of it the two aft
SPECK = 120                         # a piece smaller than this is no pillow (specks; the streak the knock drew)


def kind(c):
    r, g, b = c
    if g > r + 25 and g > b + 15:
        return "green"
    if b > r + 40 and b > g + 25:
        return "blue"
    return "other"


def layers():
    """Each used frame as (ride, free, the cart's left edge): RGBA pictures the set's size."""
    out, released = [], None
    for n, i in enumerate(SEQ):
        im = Image.open(SOURCE / "clip" / f"{i}.png").convert("RGB")
        W = im.width
        px = im.load()
        # (The cart: its blue columns at the tub's rows; a px in from its picture's edge.)
        cols = [x for x in range(W) if sum(1 for y in range(FLOOR - 30, FLOOR - 3) if kind(px[x, y]) == "blue") >= 4]
        left = min(cols) - 1
        keep = {}
        for y in range(FLOOR):
            for x in range(W):
                k = kind(px[x, y])
                if k == "green":
                    continue
                in_cart = left <= x <= left + 47 and y >= FLOOR - 41
                r, g, b = px[x, y]
                if in_cart and (k == "blue" or max(r, g, b) < 120):
                    continue
                if k == "blue" and max(r, g, b) > 150 and r < 90:
                    continue
                keep[(x, y)] = (r, g, b, 255)
        seen, comps = set(), []
        for p in list(keep):
            if p in seen:
                continue
            comp, todo = [p], [p]
            seen.add(p)
            while todo:
                cx, cy = todo.pop()
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        t = (cx + dx, cy + dy)
                        if t in keep and t not in seen:
                            seen.add(t)
                            comp.append(t)
                            todo.append(t)
            comps.append(comp)
        ride = Image.new("RGBA", (W, 128), (0, 0, 0, 0))
        free = Image.new("RGBA", (W, 128), (0, 0, 0, 0))
        riding = 0
        for comp in comps:
            if len(comp) < SPECK:
                continue
            xs, ys = [p[0] for p in comp], [p[1] for p in comp]
            mid = (min(xs) + max(xs)) / 2
            on = released is None and FLOOR - RIM - 8 <= max(ys) <= FLOOR - RIM + 8 and left + 1 <= mid <= left + 46
            riding += on
            for p in comp:
                if on:
                    ride.putpixel(p, keep[p])
                elif p[0] <= WALL:
                    free.putpixel(p, keep[p])
        if n and not riding and released is None:
            released = n
        out.append((ride, free, left))
    return out, released


def sheet(frames, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    s = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        s.paste(f.crop(box), (i * w, 0))
    return s


def union(frames):
    boxes = [f.getbbox() for f in frames if f.getbbox()]
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def main():
    GAME.mkdir(parents=True, exist_ok=True)
    frames, released = layers()
    lefts = [f[2] for f in frames]
    assert lefts[0] == START, lefts
    # The riding pieces in the cart's own px: each frame moved so that the cart's left edge is at the first frame's.
    rides = []
    for ride, _, left in frames:
        r = Image.new("RGBA", ride.size, (0, 0, 0, 0))
        r.paste(ride, (START - left, 0))
        rides.append(r)
    frees = [f[1] for f in frames]
    rb, fb = union(rides[:released]), union(frees)
    sheet(rides[:released], rb).save(GAME / "ride.png")
    sheet(frees, fb).save(GAME / "free.png")
    last = frees[-1]
    near = last.crop((0, 0, SPLIT, 128))
    far = last.crop((SPLIT, 0, last.width, 128))
    nb, fbb = near.getbbox(), far.getbbox()
    near.crop(nb).save(GAME / "near.png")
    far.crop(fbb).save(GAME / "far.png")
    # Every x is from the cart picture's left edge as he goes (the set's column START), every y from the floor (up is minus).
    layout = dict(
        frames=len(frames), release=released, cartLeft=[l - START for l in lefts],
        ride=dict(cell=[rb[2] - rb[0], rb[3] - rb[1]], x=rb[0] - START, y=rb[1] - FLOOR),
        free=dict(cell=[fb[2] - fb[0], fb[3] - fb[1]], x=fb[0] - START, y=fb[1] - FLOOR),
        near=dict(x=nb[0] - START, y=nb[1] - FLOOR, w=nb[2] - nb[0], h=nb[3] - nb[1]),
        far=dict(x=SPLIT + fbb[0] - START, y=fbb[1] - FLOOR, w=fbb[2] - fbb[0], h=fbb[3] - fbb[1]),
        top=FLOOR - rb[1])
    (GAME / "pillows.json").write_text(json.dumps(layout), encoding="utf-8")
    print("pillows:", len(frames), "frames; the last leave the cart at frame", released, "; ride", layout["ride"], "free", layout["free"])
    print("near", layout["near"], "far", layout["far"], "; the stack's top", layout["top"], "px over the floor")
    if "--sheet" in sys.argv:
        W = frames[0][0].width
        out = Image.new("RGB", (4 * (W * 2 + 4), 4 * 260), (30, 30, 40))
        for n in range(len(frames)):
            t = Image.new("RGB", (W, 128), (200, 208, 200))
            t.paste(frees[n], (0, 0), frees[n])
            t.paste(frames[n][0], (0, 0), frames[n][0])
            t = t.resize((W * 2, 256), Image.NEAREST)
            ImageDraw.Draw(t).text((3, 2), f"{n} (clip {SEQ[n]}) cart {lefts[n]}", fill=(200, 0, 0))
            out.paste(t, ((n % 4) * (W * 2 + 4), (n // 4) * 260))
        out.save(sys.argv[sys.argv.index("--sheet") + 1])


if __name__ == "__main__":
    main()
