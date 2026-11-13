"""Packs the ship's people (tools/cast.py) into one sheet, assets/sprites/people.png, a grid of
equal cells with each figure's feet on its cell's bottom row, and assets/sprites/people.json naming
each one's standing frame and clips. Sources: assets/source/people/<name>/ (tools/fetch_people.py).
Every frame is converted to Resurrect 64 (tools/palettize.py).

    python tools/build_people.py
"""

import json
from pathlib import Path

from PIL import Image

from cast import CAST
from palettize import palettize

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "people"
CELL = 80
COLS = 24
DEFAULT_FPS = 8


def lowest_row(img):
    box = img.getbbox()
    return (box[3] - 1) if box else img.height - 1


def shrunk(img, scale):
    """A figure drawn too big next to the others, smaller: box-resampled, hard-edged, on the palette again."""
    box = img.getbbox()
    if not box:
        return img
    part = img.crop(box)
    small = part.resize((max(1, round(part.width * scale)), max(1, round(part.height * scale))), Image.BOX)
    px = small.load()
    for y in range(small.height):
        for x in range(small.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255 if a >= 128 else 0)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    # Its feet stay on the row they stood on, its middle where it was.
    out.alpha_composite(palettize(small), ((box[0] + box[2] - small.width) // 2, box[3] - small.height))
    return out


def cell_of(img, feet, flip):
    """The frame in a cell: centred as its canvas is, the row `feet` on the cell's bottom row."""
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    frame = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    x, y = (CELL - img.width) // 2, CELL - 1 - feet
    left, top = max(0, -x), max(0, -y)
    right, bottom = min(img.width, CELL - x), min(img.height, CELL - y)
    if right > left and bottom > top:
        frame.alpha_composite(img.crop((left, top, right, bottom)), (x + left, y + top))
    return frame


def build():
    cells, meta = [], {"cell": CELL, "cols": COLS, "people": {}}
    for name, (_cid, clips, opts) in CAST.items():
        src = SRC / name
        if not (src / "stand.png").exists():
            print("  (not fetched yet:", name + ")")
            continue
        flip = opts.get("flip", False)
        scale = opts.get("scale")
        load = (lambda path: shrunk(palettize(Image.open(path).convert("RGBA")), scale)) if scale else (lambda path: palettize(Image.open(path)))
        stand = load(src / "stand.png")
        feet = lowest_row(stand)
        entry = {"stand": len(cells), "anims": {}, "fps": {}}
        cells.append(cell_of(stand, feet, flip))
        for turned in ("front", "back"):
            if (src / f"{turned}.png").exists():
                pic = load(src / f"{turned}.png")
                entry[turned] = len(cells)
                cells.append(cell_of(pic, lowest_row(pic), False))
        for clip_dir in sorted(p for p in src.iterdir() if p.is_dir()):
            n = len(list(clip_dir.glob("*.png")))
            frames = [load(clip_dir / f"{i}.png") for i in range(n)]
            if not frames:
                continue
            # On the standing pose's canvas the feet stay where they stand; on another canvas the
            # clip's own lowest row is the floor.
            base = feet if frames[0].size == stand.size else max(lowest_row(f) for f in frames)
            entry["anims"][clip_dir.name] = list(range(len(cells), len(cells) + n))
            entry["fps"][clip_dir.name] = clips.get(clip_dir.name, DEFAULT_FPS)
            cells += [cell_of(f, base, flip) for f in frames]
        meta["people"][name] = entry
    rows = (len(cells) + COLS - 1) // COLS
    sheet = Image.new("RGBA", (COLS * CELL, rows * CELL), (0, 0, 0, 0))
    for i, frame in enumerate(cells):
        sheet.alpha_composite(frame, ((i % COLS) * CELL, (i // COLS) * CELL))
    out = ROOT / "assets" / "sprites"
    sheet.save(out / "people.png")
    (out / "people.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"wrote assets/sprites/people.png  ({len(cells)} frames of {CELL}x{CELL}, {len(meta['people'])} people)")


if __name__ == "__main__":
    build()
