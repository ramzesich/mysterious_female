"""Gag 22's start picture, `raw/start.png`: her glide frame from her built sheet with the open parasol where
the game draws it (origin bottom middle at her x + 8, 41 px over her feet, behind her), on a 128 px canvas,
her feet at (56, 112)."""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
her = Image.open(ROOT / "assets/sprites/her.png").convert("RGBA")
th = Image.open(ROOT / "assets/sprites/things.png").convert("RGBA")
C = 84
def cell(i):
    return her.crop(((i % 48) * C, (i // 48) * C, (i % 48) * C + C, (i // 48) * C + C))
par = th.crop((631, 0, 631 + 58, 46))
FX, FY = 56, 112
for i in (322, 323):
    out = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    out.alpha_composite(par, (FX + 8 - 29, FY - 59 + 18 - 46))
    out.alpha_composite(cell(i), (FX - 42, FY - 84))
    out.save(HERE / f"start-{i}.png")
