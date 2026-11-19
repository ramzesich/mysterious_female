"""Lays a clip's frames side by side, enlarged 3x on a sky blue (its index 0 first): `python sheet.py flip1`."""
import sys
from pathlib import Path
from PIL import Image
d = Path(__file__).resolve().parent / sys.argv[1]
fr = [Image.open(p).convert("RGBA") for p in sorted(d.glob("0*.png"))]
S = 3
out = Image.new("RGBA", (len(fr) * 128 * S, 128 * S), (140, 190, 230, 255))
for i, f in enumerate(fr):
    out.alpha_composite(f.resize((128 * S, 128 * S), Image.NEAREST), (i * 128 * S, 0))
out.save(d.parent / f"{sys.argv[1]}-sheet.png")
print([f.size for f in fr][:2], len(fr))
