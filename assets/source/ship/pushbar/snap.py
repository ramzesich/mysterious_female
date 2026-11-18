"""The push bar's pixels (what the inpainting changed in `leaf-plain.png`, or in `edge-plain.png` for the
shut door's profiles) snapped to the Resurrect 64
palette; the leaf's own pixels kept as the game draws them. Writes `leaf-<name>.png` for each try in
`raw/`.

python assets/source/ship/pushbar/snap.py"""
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
PAL = [tuple(int(l[i:i + 2], 16) for i in (0, 2, 4)) for l in (HERE.parents[2] / "palette/resurrect-64.hex").read_text(encoding="utf-8").splitlines() if len(l.strip()) == 6 and not l.startswith(";")]


def near(c):
    return min(PAL, key=lambda p: sum((p[k] - c[k]) ** 2 for k in range(3)))


for raw in sorted((HERE / "raw").glob("*.png")):
    # (Its source: the edge-on door for the profiles, the open leaf for the bars.)
    src = Image.open(HERE / ("edge-plain.png" if raw.stem.startswith("edge") else "leaf-plain.png")).convert("RGBA")
    im = Image.open(raw).convert("RGBA")
    px, sp = im.load(), src.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] != sp[x, y] and px[x, y][3]:
                px[x, y] = near(px[x, y][:3]) + (255,)
    im.save(HERE / (f"{raw.stem}.png" if raw.stem.startswith("edge") else f"leaf-{raw.stem}.png"))
    print(raw.stem, sorted({px[x, y][:3] for y in range(35, 48) for x in range(2, 30)}))
