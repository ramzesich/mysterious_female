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
        "idle": [(f"idle/{i}.png", "keep") for i in range(4)],
        "run": [(f"run/{i}.png", "keep") for i in range(8)],
        "rise": [("jump/3.png", "feet")],
        "apex": [("jump/4.png", "feet")],
        "fall": [("jump/5.png", "feet")],
        "climb": [(f"climb/{i}.png", "keep") for i in range(1, 9)],
        "front": [("rotations/south.png", "keep")],
        "back": [("rotations/north.png", "keep")],
    },
    # The standing baseline: this frame's lowest pixel row is where the feet are in "keep" frames.
    "baseline": "idle/0.png",
}


def lowest_row(img):
    return img.getbbox()[3] - 1


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
        for path, anchor in sources:
            img = palettize(Image.open(src_dir / path), remap)
            feet = standing_feet(img.size) if anchor == "keep" else None
            if feet is None:
                feet = lowest_row(img)
            x = (cell - img.width) // 2
            y = cell - 1 - feet
            frame = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
            frame.alpha_composite(img, (x, y)) if y >= 0 else frame.alpha_composite(img.crop((0, -y, img.width, img.height)), (x, 0))
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
