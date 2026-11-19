"""Gag 23's start picture, `raw/start.png`: her standing frame from her built sheet (cell 0), on a 128 px
canvas, her middle at x 64, her feet on row 120 (the world's y is row 121); facing east."""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
her = Image.open(ROOT / "assets/sprites/her.png").convert("RGBA")
C = 84
out = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
out.alpha_composite(her.crop((0, 0, C, C)), (64 - 42, 121 - C))
out.save(HERE / "start.png")
