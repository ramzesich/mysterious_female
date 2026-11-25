"""Her richer swimming (the user, 2026-11-25: "I want her swimming animation enriched"; near-catch 5: "She stops,
peeks out of the water, cries"): PixMiniMax's clips from her swim's first frame on a green ground (start.png: her cell
at (22, 14) of a 128 px picture), the ground taken out of every frame: a pixel is the ground's when green leads its
red and its blue by 60. Loose specks go (anything not joined to her). Each frame is set on her sources' 96 px canvas
where her swim's frames are (16 columns and 32 rows off the picture's), so that a clip's first frame is the frame it
was made from, to the pixel.

    python assets/source/her/swim-rich/cut.py
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
DX, DY, SIZE = 16, 32, 96
# clip -> (the try's name, its pictures in the order played)
CLIPS = {
    "swim-stroke": ("stroke-s11", list(range(16))),      # (16 is 0 again: the loop's end was pinned to its start)
    "swim-peek": ("peek-s19", list(range(9))),
    "swim-tread": ("tread-s7", list(range(8))),
    "swim-cry": ("cry1-s3", list(range(9))),
}


def parts(cells):
    seen, out = set(), []
    for s in cells:
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
                    if q in cells and q not in seen:
                        seen.add(q)
                        todo.append(q)
        out.append(comp)
    return sorted(out, key=len, reverse=True)


def cut(im):
    im = im.convert("RGB")
    w, h = im.size
    p = im.load()
    body = {(x, y) for y in range(h) for x in range(w) if not (p[x, y][1] > p[x, y][0] + 60 and p[x, y][1] > p[x, y][2] + 60)}
    best = set(parts(body)[0])
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    op = out.load()
    lost = 0
    for x, y in best:
        if 0 <= x - DX < SIZE and 0 <= y - DY < SIZE:
            op[x - DX, y - DY] = p[x, y] + (255,)
        else:
            lost += 1
    return out, len(body) - len(best), lost


if __name__ == "__main__":
    for clip, (name, order) in CLIPS.items():
        if not (HERE / "tries" / f"{name}-0.png").exists():
            print(clip, "no try", name)
            continue
        d = HERE / clip
        d.mkdir(exist_ok=True)
        for k, i in enumerate(order):
            out, specks, lost = cut(Image.open(HERE / "tries" / f"{name}-{i}.png"))
            out.save(d / f"{k}.png")
            print(clip, k, out.getbbox(), "specks dropped:", specks, "off the canvas:", lost)
