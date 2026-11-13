"""Takes out the chair PixelLab drew under her in a seated clip (skeleton-v3 adds things: CLAUDE.md),
so that she can sit on the game's own chairs: the wood's colours go, then the thin dark lines of its
outline left standing alone.

    python tools/unchair.py <clip> [<clip> ...]      assets/source/her/<clip>/ -> <clip>-clean/

The wood is told from her hair by its lightness (her hair is the darker brown), and only looked for
below her chin, behind and under her (the food in her hand, in front of her face, stays).
"""

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "her"


def is_wood(p):
    r, g, b, a = p
    return a > 0 and 0x3c <= r <= 0x80 and r - b >= 0x14 and g < r and 0x26 <= g <= 0x60 and b <= 0x4c


def is_dark(p):
    r, g, b, a = p
    return a > 0 and r < 0x48 and g < 0x38 and b < 0x38


def clean(im):
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    box = im.getbbox()
    if not box:
        return im
    # Her chin: a third of the way down her figure; her front: the right half of her (she faces east).
    chin = box[1] + (box[3] - box[1]) // 3
    gone = 0
    for y in range(chin, h):
        for x in range(w):
            if is_wood(px[x, y]):
                px[x, y] = (0, 0, 0, 0)
                gone += 1
    if gone < 12:
        return im           # no chair in this frame
    # The chair's outline, left standing alone: thin dark lines. A dark pixel with at most two
    # neighbours is part of a line (her own outline has her colours beside it); they go, pass by pass.
    for _ in range(6):
        drop = []
        for y in range(chin, h):
            for x in range(w):
                if not is_dark(px[x, y]):
                    continue
                near = [px[x + dx, y + dy] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                        if (dx or dy) and 0 <= x + dx < w and 0 <= y + dy < h]
                if sum(1 for n in near if n[3] > 0) <= 2:
                    drop.append((x, y))
        for x, y in drop:
            px[x, y] = (0, 0, 0, 0)
        if not drop:
            break
    # What is left of it in bits: everything not joined to her goes.
    seen, best = set(), []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0 or (x, y) in seen:
                continue
            part, todo = [], [(x, y)]
            seen.add((x, y))
            while todo:
                cx, cy = todo.pop()
                part.append((cx, cy))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        n = (cx + dx, cy + dy)
                        if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and px[n][3] > 0:
                            seen.add(n)
                            todo.append(n)
            if len(part) > len(best):
                best = part
    keep = set(best)
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > 0 and (x, y) not in keep:
                px[x, y] = (0, 0, 0, 0)
    return im


def main():
    for clip in sys.argv[1:]:
        out = SRC / f"{clip}-clean"
        out.mkdir(exist_ok=True)
        for f in sorted((SRC / clip).glob("*.png")):
            clean(Image.open(f)).save(out / f.name)
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
