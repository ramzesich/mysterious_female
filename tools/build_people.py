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
# Clips in which the figure leaves the floor (a jump, a hop, a leap, a run): kept where the
# generator drew each frame. Every other clip has its feet on the floor, and each of its frames is
# set on the floor by its own lowest row: PixelLab's frames drift 1 to 4 px up and down, and a
# dog sat, a lady stood, a kid idled in the air (the user, 2026-11-17: "not even placed properly on
# the floor"). By clip name, or (figure, clip).
OFF_THE_FLOOR = {"run", "jump", "shriek", "bounce", "step", "steps", "lunge", "kiss", "flap", "flap2",
                 "dance", "clap", "cheer", "bolt", "fleeing",
                 ("rival", "swat"), ("rival", "swing"),
                 # (The dog's owner with the dog running round her legs: her feet stay where she
                 # stands; the dog's paw a px lower in one frame is not the floor.)
                 ("dogowner", "wind"), ("dogowner", "unwind"),
                 # (The massage guest getting up off the table: lying on its top, then on the floor.)
                 ("massage_guest", "up"),
                 # (Her husband's far leg, alone: on his canvas, where his feet are.)
                 ("husband", "far")}


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


WALL = (0xE9, 0xDF, 0xCC)     # as tools/build_ship_art.py's


def washed(img, k):
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (*(round(c + (w - c) * k) for c, w in zip((r, g, b), WALL)), a)
    return out


def kept(done, raw, colours):
    """`done` (on the palette) with the pixels of `raw` whose colour is one of `colours` put back."""
    out, px, rp = done.copy(), None, raw.load()
    px = out.load()
    for y in range(raw.height):
        for x in range(raw.width):
            r, g, b, a = rp[x, y]
            if a and (r, g, b) in colours:
                px[x, y] = (r, g, b, a)
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
        if opts.get("own_colours"):
            # (All of a figure kept in its own colours: her husband, whose hair went olive, skin pink and eye red on
            # the palette, 2026-11-22.)
            load = lambda path: Image.open(path).convert("RGBA")
        if opts.get("wash"):
            # (Washed toward the corridor wall as the ship's background pieces are, `wash` of the way: the
            # theatre's audience, as lightly as the theatre's own pieces, `-lt`.)
            plain, k = load, opts["wash"]
            load = lambda path, plain=plain, k=k: washed(plain(path), k)
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
            # ("own": {clip: [colours]}: a thing in the clip kept in its own colours, not the palette's, as the
            # world's own picture of it is: the sushi chef's tin of sardines.)
            own = {tuple(bytes.fromhex(c)) for c in opts.get("own", {}).get(clip_dir.name, [])}
            if own:
                frames = [kept(f, Image.open(clip_dir / f"{i}.png").convert("RGBA"), own) for i, f in enumerate(frames)]
            if not frames:
                continue
            # On the standing pose's canvas the feet stay where they stand; on another canvas the
            # clip's own lowest row is the floor.
            base = feet if frames[0].size == stand.size else max(lowest_row(f) for f in frames)
            entry["anims"][clip_dir.name] = list(range(len(cells), len(cells) + n))
            entry["fps"][clip_dir.name] = clips.get(clip_dir.name, DEFAULT_FPS)
            down = clip_dir.name not in OFF_THE_FLOOR and (name, clip_dir.name) not in OFF_THE_FLOOR
            cells += [cell_of(f, lowest_row(f) if down else base, flip) for f in frames]
        # ("cut": {name: (clip, [frames])}: a loop made of some of a clip's frames, e.g. the frames
        # where a book is already in his hands.)
        for new, (clip, picks) in opts.get("cut", {}).items():
            entry["anims"][new] = [entry["anims"][clip][i] for i in picks]
            entry["fps"][new] = clips.get(new, DEFAULT_FPS)
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
