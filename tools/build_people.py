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
        stand = palettize(Image.open(src / "stand.png"))
        feet = lowest_row(stand)
        entry = {"stand": len(cells), "anims": {}, "fps": {}}
        cells.append(cell_of(stand, feet, flip))
        if (src / "front.png").exists():
            front = palettize(Image.open(src / "front.png"))
            entry["front"] = len(cells)
            cells.append(cell_of(front, lowest_row(front), False))
        for clip_dir in sorted(p for p in src.iterdir() if p.is_dir()):
            n = len(list(clip_dir.glob("*.png")))
            frames = [palettize(Image.open(clip_dir / f"{i}.png")) for i in range(n)]
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
