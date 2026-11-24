"""Her reach up out of the water (near-catch 5: at the pool's rim under Bumbot, the user, 2026-11-24): PixMiniMax's
clip (tries/seed4-*.png: nine pictures, from her swim's first frame to her head lifted and one arm stretched up) with
the green ground taken out of every frame: a pixel is the ground's when green leads its red and its blue by 60. Loose
specks go (the generator's flecks of spray: anything not joined to her, and small white bits on her outline). Each frame is set on her sources' 96 px canvas
where her swim's frames are (the picture's rows are 26 lower than the canvas's: place.json), so that the clip's first
frame is her swim's first frame to the pixel.

    python assets/source/her/swim-reach/cut.py
"""
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
SEED, N, DOWN = 4, 9, 26


def cut(im):
    im = im.convert("RGB")
    w, h = im.size
    p = im.load()
    body = {(x, y) for y in range(h) for x in range(w) if not (p[x, y][1] > p[x, y][0] + 60 and p[x, y][1] > p[x, y][2] + 60)}
    seen, best = set(), []
    for s in body:
        if s in seen:
            continue
        comp, todo = [], [s]
        seen.add(s)
        while todo:
            x, y = todo.pop()
            comp.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q in body and q not in seen:
                        seen.add(q)
                        todo.append(q)
        if len(comp) > len(best):
            best = comp
    # (And the flecks of spray that touch her: small white bits on her outline. The white of her eye is inside her.)
    best = set(best)
    white = {q for q in best if min(p[q]) > 200}
    done = set()
    for s in white:
        if s in done:
            continue
        comp, todo = [], [s]
        done.add(s)
        while todo:
            x, y = todo.pop()
            comp.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q in white and q not in done:
                        done.add(q)
                        todo.append(q)
        edge = any((x + dx, y + dy) not in best for x, y in comp for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if len(comp) < 8 and edge:
            best -= set(comp)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for x, y in best:
        if 0 <= y - DOWN < h:
            op[x, y - DOWN] = p[x, y] + (255,)
    return out, len(body) - len(best)


if __name__ == "__main__":
    for i in range(N):
        out, dropped = cut(Image.open(HERE / "tries" / f"seed{SEED}-{i}.png"))
        out.save(HERE / f"{i}.png")
        print(i, out.getbbox(), "specks dropped:", dropped)
