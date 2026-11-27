"""The siege's numbers from the built people sheet (run after tools/build_people.py): the lying pillow's picture (what
the throw's first frame has that its last has not) into `assets/source/things/splash-pillow.png`, where it lies from
each kid's feet (their sprite's origin, facing east), and where the pillow is at the release (the raw frame's loose
pillow, mapped as the build maps a frame: the canvas shrunk whole, set on the cell by its lowest row)."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[5]
m = json.loads((ROOT / "assets/sprites/people.json").read_text())
sh = Image.open(ROOT / "assets/sprites/people.png").convert("RGBA")
C, cols = m["cell"], m["cols"]
cell = lambda i: sh.crop(((i % cols) * C, (i // cols) * C, (i % cols + 1) * C, (i // cols + 1) * C))
RELEASE = {"splash_king": (12, (78.97, 17.24)), "splash_knight": (13, (68.59, 18.55))}
SCALE = 0.68
for n, (rel, (rx, ry)) in RELEASE.items():
    A = m["people"][n]["anims"]["throw"]
    t0, t16 = cell(A[0]), cell(A[16])
    a, b = t16.load(), t0.load()
    pts = [(x, y) for y in range(C) for x in range(C) if b[x, y][3] and b[x, y] != a[x, y]]
    box = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts) + 1, max(p[1] for p in pts) + 1)
    pil = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]))
    for x, y in pts:
        pil.putpixel((x - box[0], y - box[1]), b[x, y])
    if n == "splash_king":
        pil.save(ROOT / "assets/source/things/splash-pillow.png")
    # The release frame's lowest row in the sheet's cell is its bottom row; in the shrunk canvas it was `feet`.
    fr = cell(A[rel])
    small = Image.open(ROOT / f"assets/source/people/{n}/throw/{rel}.png").convert("RGBA")
    sw = round(88 * SCALE)
    feet_raw = small.getbbox()[3] - 1
    feet = 88 - sw + feet_raw * SCALE
    print(n, "pillow", pil.size, "lies from her feet: x", (box[0] + box[2]) / 2 - C / 2, "bottom", box[3] - C,
          "| release frame", rel, "at", round(SCALE * rx - (sw / 2 + 0 - 0) + (88 - sw) / 2 - 44 + 0, 1) if False else
          round(SCALE * rx + (88 - sw) // 2 + (C - 88) // 2 - C / 2, 1), round(SCALE * ry + 88 - sw - feet, 1))
