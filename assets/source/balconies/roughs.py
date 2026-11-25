"""The balconies' pieces drawn flat by rule, at the game's size, for PixelLab to redraw in place (the shaft's lesson:
"draw it flat by rule with the real thing's features, then have it redrawn"). python assets/source/balconies/roughs.py

  rough/unit.png      one balcony's recess, 128 x 112: the back wall, the cabin's sliding glass door shut, the ceiling's
                      edge, the partition's edge at its left (and the next one's at its right), no front
  rough/unit-ajar.png the same with the sliding pane open on the lit cabin
"""
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
UNIT, H = 125, 108                 # a balcony's width; its recess from the ceiling's edge down to the sill's top
WALL, GLASS, EDGE, LINE = "#5d6f86", "#323353", "#f4f4f4", "#c7dcd0"
FRAME, FRAME_LT, CURTAIN, GLINT = "#8fa0b4", "#c7cfdd", "#454a6e", "#4d65b4"


def unit(ajar=False):
    im = Image.new("RGB", (128, 112), WALL)
    d = ImageDraw.Draw(im)
    R = lambda x, y, w, h, c: d.rectangle((x, y, x + w - 1, y + h - 1), fill=c)
    # The ceiling's edge and its shade on the back wall (as the ship's side draws them).
    R(0, 0, 128, 5, EDGE); R(0, 5, 128, 1, LINE); R(0, 6, 128, 3, "#506178"); R(0, 9, 128, 2, "#566880")
    # The cabin's sliding glass door, floor to lintel: a frame, a fixed pane, a sliding pane, a handle.
    x0, x1, top = 14, 113, 12
    R(x0 - 2, top - 2, x1 - x0 + 4, H - top + 2, FRAME)
    R(x0, top, x1 - x0, H - top, GLASS)
    mid = 63
    R(mid - 1, top, 3, H - top, FRAME)
    # (drawn-back curtains inside, behind the glass)
    for x in (x0, x0 + 3, x0 + 7, x1 - 4, x1 - 8):
        R(x, top, 2, H - top, CURTAIN)
    R(x0 + 12, top + 2, 3, H - top - 6, GLINT)
    R(mid + 14, top + 2, 2, H - top - 6, GLINT)
    R(mid + 4, top + 44, 2, 10, FRAME_LT)                      # the handle
    R(x0 - 2, H - 3, x1 - x0 + 4, 3, FRAME_LT)                 # the threshold
    if ajar:
        # The sliding pane pushed aside over the fixed one: the doorway lit from the cabin, a sheer curtain in it.
        R(mid + 2, top, x1 - mid - 2, H - top, "#fdf0cf")
        R(mid + 2, top, x1 - mid - 2, 3, "#e6d3a3")
        for x in range(mid + 4, mid + 22, 4):
            R(x, top + 3, 2, H - top - 10, "#ffffff")
        R(mid - 30, top, 2, H - top, FRAME); R(mid - 26, top + 44, 2, 10, FRAME_LT)
    # The partitions' edges, floor to ceiling.
    for x in (0, UNIT):
        R(x, 0, 6, H, EDGE); R(x + 5, 6, 1, H - 6, LINE)
    R(0, H, 128, 4, EDGE)                                       # (the sill under it, for the redraw's sake)
    return im


if __name__ == "__main__":
    out = HERE / "rough"
    out.mkdir(exist_ok=True)
    unit().save(out / "unit.png")
    unit(True).save(out / "unit-ajar.png")
    both = Image.new("RGB", (128 * 2 * 4 + 12, 112 * 4), "#202028")
    both.paste(unit().resize((512, 448), Image.NEAREST), (0, 0)); both.paste(unit(True).resize((512, 448), Image.NEAREST), (524, 0))
    both.save(out / "units-4x.png")
    print("wrote", out)
