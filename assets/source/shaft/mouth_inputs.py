"""The pictures the shaft's mouth was generated from (run from the repo root: python assets/source/shaft/mouth_inputs.py).

The linen room's forward corner (assets/ship/linen-room.png, its box `MOUTH_CORNER` of tools/build_shaft.py) with the
mouth drawn in flat, in three states: `rough/mouth-shut.png` (its louvred cover on its end), `mouth-open.png` (the end
open), `mouth-down.png` (the cover off, by the wall under it); `mouth-bare.png` is the corner alone. PixelLab redrew
each (`gen/mouth-*.png`); tools/build_shaft.py `--mouth` cuts the pieces from those.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from build_shaft import MOUTH_CORNER as BOX                 # noqa: E402

OUT = Path(__file__).resolve().parent / "rough"
room = Image.open(ROOT / "assets/ship/linen-room.png").convert("RGB")
PALE, GREY, SLATE, DARK, INK, WHITE = "#c7dcd0", "#9babb2", "#625565", "#3e3546", "#2e222f", "#f2f6f6"


def corner(state):
    im = room.crop(BOX)
    d = ImageDraw.Draw(im)
    top, bot = 128 - 68 - 2 - BOX[1], 128 - 32 + 2 - BOX[1]      # the duct's outside: its floor 32 px up, 36 px inside
    # The duct's end standing out of the wall: its near side, a seam, the flange at its end, a bracket under it.
    d.rectangle([4, top, 25, bot - 1], fill=GREY, outline=SLATE)
    d.rectangle([5, top + 1, 24, top + 2], fill=PALE)
    d.rectangle([5, bot - 5, 24, bot - 2], fill="#8a98a0")
    d.line([(14, top + 1), (14, bot - 2)], fill=SLATE)
    for y in (top + 6, top + 20, top + 33):
        d.point((7, y), fill=WHITE)
        d.point((21, y), fill=WHITE)
    d.rectangle([23, top - 2, 27, bot + 1], fill=PALE, outline=SLATE)
    for y in (top + 2, top + 13, top + 25, top + 36):
        d.point((25, y), fill=INK)
    d.line([(5, bot), (5, bot + 6)], fill=SLATE)
    d.line([(5, bot + 6), (12, bot)], fill=SLATE)
    if state == "shut":
        d.rectangle([28, top, 31, bot - 1], fill=GREY, outline=SLATE)       # the cover on its end: a louvred plate, edge on
        for y in range(top + 3, bot - 2, 4):
            d.line([(29, y), (32, y + 1)], fill=PALE)
    else:
        d.rectangle([28, top + 1, 29, bot - 2], fill=INK)                   # the open end, a dark lip
    if state == "down":
        f = BOX[3] - BOX[1]
        d.polygon([(5, f - 36), (16, f - 33), (20, f), (9, f)], fill=GREY, outline=SLATE)
        for k in range(5):
            y = f - 30 + k * 6
            d.line([(8 + k * 0.6, y), (16 + k * 0.6, y + 2)], fill=DARK)
            d.line([(8 + k * 0.6, y - 1), (16 + k * 0.6, y + 1)], fill=PALE)
    return im


OUT.mkdir(parents=True, exist_ok=True)
room.crop(BOX).save(OUT / "mouth-bare.png")
for s in ("shut", "open", "down"):
    corner(s).save(OUT / f"mouth-{s}.png")
print("wrote", OUT)
