"""The horn's scene remade (docs/horn-remake-log.md, the user, 2026-11-27): its clips, cut out of what PixelLab
returned (assets/source/horn/tries/, the jobs in its README).

    python tools/build_horn.py          then  python tools/build_sprites.py  (hers and Bumbot's go into their sheets)

- **Hers** (`ears`: her hands over her ears, hunched) into `assets/source/her/ears/`, her sources' 96 px canvas.
- **Bumbot's** (`fright`: off his seat, back arched, tail puffed) into `assets/source/bumbot/remake/clips/fright/`.
- **The officer's** (`start`: off his knees into the air and down onto his feet; `hurdle`: over the sunbed in his
  stride) and **the old lady's** (`hurry`: quick short steps, her book in her hand) into one strip of their own,
  `assets/ship/horn/clips.png` with `clips.json`: cells of 96 x 112, the figure's x at column 48, its floor under the
  bottom row, each figure in the colours of its own built sheet.
- **The old lady's bags and towel** (the user's choice of three sets, 2026-11-27): `assets/source/horn/bags/`, map
  objects of 32 px, brought to the game's size by each pixel's commonest colour (`BAGS`: the height each stands), in
  their own colours, into `assets/ship/horn/lady-<name>.png`. The towel's rail, which the generator drew, is cut off.
"""
import json
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/source/horn"
TRIES = SRC / "tries"
OUT = ROOT / "assets/ship/horn"
CELL = (96, 112)                # cut from the 128 px canvases at (16, 0): the figure's x at column 48
# clip -> (the try, its frames in the order played, whose sheet's colours, "largest": only the figure's own piece)
STRIP = {
    # (The generator drew dust strokes under his start, apart from him: only his own piece is kept, as of the hurdle.)
    "start": ("start-s4", list(range(9)), "rival", True),
    # (The generator drew a hurdle under him, apart from him: only his own piece is kept.)
    "hurdle": ("hurdle-s4", list(range(9)), "rival", True),
    # (8 is 0 again: a loop of eight.)
    "hurry": ("ladywalk-s5", list(range(8)), "oldlady", False),
}
HERS = {"ears": ("ears-s17", list(range(9)))}
CATS = {"fright": ("fright-s3", list(range(9)))}
PLANTED = {"hurry"}            # a walk: each frame set on its lowest pixel (the generator's frames drift 1 to 3 px)
# her things at the sunbed: name -> (the source, its height in the game)
BAGS = {"bag": ("bag-floral", 22), "handbag": ("handbag-burgundy", 17), "duffel": ("duffel-teal", 16), "towel": ("towel-draped", 19)}
LEAST = 10                      # a loose piece smaller than this is a speck (the start's dust strokes)


def pieces(im):
    px, (w, h) = im.load(), im.size
    seen, out = set(), []
    for y in range(h):
        for x in range(w):
            if (x, y) in seen or not px[x, y][3]:
                continue
            comp, todo = [], [(x, y)]
            seen.add((x, y))
            while todo:
                a, b = todo.pop()
                comp.append((a, b))
                for da in (-1, 0, 1):
                    for db in (-1, 0, 1):
                        c = (a + da, b + db)
                        if 0 <= c[0] < w and 0 <= c[1] < h and c not in seen and px[c][3]:
                            seen.add(c)
                            todo.append(c)
            out.append(comp)
    return sorted(out, key=len, reverse=True)


def clean(im, largest=False, least=LEAST):
    """A frame already cut out of its green (`cut-NN.png`): specks off; `largest`: only the biggest piece."""
    im = im.convert("RGBA")
    px = im.load()
    for k, comp in enumerate(pieces(im)):
        if (largest and k > 0) or len(comp) < least:
            for c in comp:
                px[c] = (0, 0, 0, 0)
    return im


def sheet_colours(who):
    """Every colour of a person's frames in the built people's sheet."""
    meta = json.loads((ROOT / "assets/sprites/people.json").read_text(encoding="utf8"))
    cell, cols, p = meta["cell"], meta["cols"], meta["people"][who]
    sheet = Image.open(ROOT / "assets/sprites/people.png").convert("RGBA")
    frames = {p["stand"], *[n for a in p["anims"].values() for n in a]}
    out = set()
    for n in frames:
        f = sheet.crop(((n % cols) * cell, (n // cols) * cell, (n % cols + 1) * cell, (n // cols + 1) * cell))
        out |= {c[:3] for _, c in f.getcolors(cell * cell) if c[3] == 255}
    return sorted(out)


def recolour(im, colours):
    px, cache = im.load(), {}
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            key = (r, g, b)
            if key not in cache:
                cache[key] = min(colours, key=lambda c: (c[0] - r) ** 2 + (c[1] - g) ** 2 + (c[2] - b) ** 2)
            px[x, y] = cache[key] + (255,)
    return im


def shrink(im, h):
    """A picture brought to `h` px high: each pixel the commonest colour of the source pixels it covers."""
    im = im.crop(im.getbbox())
    w = max(1, round(im.width * h / im.height))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    src, op = im.load(), out.load()
    for y in range(h):
        for x in range(w):
            x0, x1 = int(x * im.width / w), max(int(x * im.width / w) + 1, int((x + 1) * im.width / w))
            y0, y1 = int(y * im.height / h), max(int(y * im.height / h) + 1, int((y + 1) * im.height / h))
            px = [src[i, j] for j in range(y0, y1) for i in range(x0, x1)]
            solid = [q for q in px if q[3] > 127]
            if len(solid) * 2 >= len(px):
                op[x, y] = Counter(solid).most_common(1)[0][0][:3] + (255,)
    return out


def bags():
    for name, (source, h) in BAGS.items():
        im = Image.open(SRC / "bags" / f"{source}.png").convert("RGBA")
        if source == "towel-draped":
            # (The rail it was drawn hanging on: the dark pixels of its top rows.)
            px = im.load()
            for y in range(8):
                for x in range(im.width):
                    r, g, b, a = px[x, y]
                    if a and max(r, g, b) < 110:
                        px[x, y] = (0, 0, 0, 0)
        out = shrink(im, h)
        out.save(OUT / f"lady-{name}.png")
        print(f"lady-{name}: {out.size}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bags()
    meta = {"cell": list(CELL), "x": 48, "clips": {}}
    rows = []
    for clip, (name, frames, who, largest) in STRIP.items():
        colours = sheet_colours(who)
        row, feet = [], []
        for n in frames:
            f = clean(Image.open(TRIES / name / f"cut-{n:02d}.png"), largest).crop((16, 0, 16 + CELL[0], CELL[1]))
            f = recolour(f, colours)
            box = f.getbbox()
            up = CELL[1] - box[3]                   # how far its lowest pixel is over the floor line
            if clip in PLANTED and up:
                g = Image.new("RGBA", CELL, (0, 0, 0, 0))
                g.paste(f, (0, up))
                f, up = g, 0
            feet.append(up)
            row.append(f)
        meta["clips"][clip] = {"row": len(rows), "frames": len(row), "up": feet}
        rows.append(row)
        print(f"{clip}: {len(row)} frames, px over the floor {feet}")
    strip = Image.new("RGBA", (CELL[0] * max(len(r) for r in rows), CELL[1] * len(rows)), (0, 0, 0, 0))
    for j, row in enumerate(rows):
        for i, f in enumerate(row):
            strip.paste(f, (i * CELL[0], j * CELL[1]))
    strip.save(OUT / "clips.png")
    (OUT / "clips.json").write_text(json.dumps(meta, indent=1), encoding="utf8")
    for clip, (name, frames) in HERS.items():
        d = ROOT / "assets/source/her" / clip
        d.mkdir(parents=True, exist_ok=True)
        for i, n in enumerate(frames):
            # (Her sources' 96 px canvas, where her stand's frame is: her 84 px cell at (22, 14) of the 128 px picture.)
            clean(Image.open(TRIES / name / f"cut-{n:02d}.png"), least=6).crop((16, 32, 112, 128)).save(d / f"{i}.png")
        print(f"her {clip}: {len(frames)} frames")
    for clip, (name, frames) in CATS.items():
        d = ROOT / "assets/source/bumbot/remake/clips" / clip
        d.mkdir(parents=True, exist_ok=True)
        for i, n in enumerate(frames):
            clean(Image.open(TRIES / name / f"cut-{n:02d}.png"), least=4).save(d / f"{i}.png")
        print(f"bumbot {clip}: {len(frames)} frames")


if __name__ == "__main__":
    main()
