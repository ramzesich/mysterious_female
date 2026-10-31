"""Builds the game's character sprite sheets from the raw PixelLab frames in assets/source/.

For each character: every frame is converted to Resurrect 64 (tools/palettize.py, plus that
character's colour swaps), placed in a fixed-size cell with the feet on the cell's bottom row, and
packed into one strip, assets/sprites/<name>.png, with assets/sprites/<name>.json naming the frames
and animations. Re-run after replacing any source frame.

    python tools/build_sprites.py
"""

import json
from pathlib import Path

from PIL import Image

from palettize import palettize, hex_rgb

ROOT = Path(__file__).resolve().parent.parent

# Bumbusik. Sources face east (the game mirrors her for west); the climb faces north.
HER = {
    "name": "her",
    "cell": 84,
    # Palette swaps after the nearest-colour match: warmer brown hair highlights, and pink-peach
    # shading on her fair skin instead of a dusky mauve.
    "remap": {"3e3546": "45293f", "966c6c": "f68181"},
    # name -> list of (source file, anchor). "keep" preserves the frame's own vertical motion (a
    # breathing bob, a running bounce) relative to the standing baseline; "feet" puts the frame's
    # lowest pixel on the bottom row, for airborne poses whose source includes the jump's height.
    "frames": {
        # Standing still: her plain side pose. Every so often one of her idles plays once
        # (GAME_DESIGN.md §3); both are skeleton-v3, starting and ending near "stand".
        "stand": [("rotations/east.png", "keep")],
        "idle-tap": [(f"idle-tap-2/{i}.png", "keep") for i in range(8)],
        "idle-look": [(f"idle-look/{i}.png", "keep") for i in range(8)],
        # skeleton-v3 run: moves her standing sprite instead of redrawing it, so her hair keeps its
        # standing length (the first, template run let it grow and puff up).
        "run": [(f"run-steady/{i}.png", "keep") for i in range(8)],
        "rise": [("jump/3.png", "feet")],
        "apex": [("jump/4.png", "feet")],
        "fall": [("jump/5.png", "feet")],
        # skeleton-v3 climb (PixelLab's built-in climb move): hands reach up in turn. The first,
        # text-described climb moved both hands together.
        "climb": [(f"climb-alternating/{i}.png", "keep") for i in range(8)],
        "front": [("rotations/south.png", "keep")],
        "back": [("rotations/north.png", "keep")],
        # Climbing out of a hatch, from behind: hands on the rim at head, shoulder, then waist
        # height, a knee coming up. The game picks the frame by how far she has risen.
        "climb-out": [(f"climb-out/{i}.png", "keep") for i in range(3)],
    },
    # The standing baseline: this frame's lowest pixel row is where the feet are in "keep" frames
    # of the same canvas size. Frames on another canvas use their own animation's lowest row.
    "baseline": "idle/0.png",
}


def lowest_row(img):
    return img.getbbox()[3] - 1


def paste(dst, src, x, y):
    """alpha_composite that clips a source larger than (or hanging off) the destination."""
    left, top = max(0, -x), max(0, -y)
    right, bottom = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if right > left and bottom > top:
        dst.alpha_composite(src.crop((left, top, right, bottom)), (x + left, y + top))


def build(spec):
    src_dir = ROOT / "assets" / "source" / spec["name"]
    cell = spec["cell"]
    remap = {hex_rgb(a): hex_rgb(b) for a, b in spec["remap"].items()}
    baseline = {}  # per source canvas size, the y of the standing feet

    def standing_feet(size):
        if size not in baseline:
            ref = Image.open(src_dir / spec["baseline"]).convert("RGBA")
            baseline[size] = lowest_row(ref) if ref.size == size else None
        return baseline[size]

    cells, meta = [], {"cell": cell, "frames": {}, "anims": {}}
    for anim, sources in spec["frames"].items():
        indices = []
        images = [(palettize(Image.open(src_dir / path), remap), anchor) for path, anchor in sources]
        anim_feet = max(lowest_row(img) for img, _ in images)
        for img, anchor in images:
            if anchor == "keep":
                feet = standing_feet(img.size)
                if feet is None:
                    feet = anim_feet
            else:
                feet = lowest_row(img)
            frame = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
            paste(frame, img, (cell - img.width) // 2, cell - 1 - feet)
            indices.append(len(cells))
            cells.append(frame)
        meta["anims"][anim] = indices
        meta["frames"][anim] = indices[0]

    sheet = Image.new("RGBA", (cell * len(cells), cell), (0, 0, 0, 0))
    for i, frame in enumerate(cells):
        sheet.alpha_composite(frame, (i * cell, 0))
    out = ROOT / "assets" / "sprites"
    out.mkdir(parents=True, exist_ok=True)
    sheet.save(out / f"{spec['name']}.png")
    (out / f"{spec['name']}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"wrote assets/sprites/{spec['name']}.png  ({len(cells)} frames of {cell}x{cell})")


if __name__ == "__main__":
    build(HER)
