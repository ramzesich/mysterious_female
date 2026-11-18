"""The towel stack's end picture (2026-11-18): its own fourteen towels (as `starts.py` draws them) fallen to
its right and lying in a low scattered heap on the floor, the stool left standing; the last frame the
fall clip is drawn toward. Each towel: (x, y of its top, angle, blue?)."""
import os
from PIL import Image
from starts import stool, c, W, H, FLOOR, X
from PIL import ImageDraw
here = os.path.dirname(os.path.abspath(__file__))
def towel(blue):
    im = Image.new("RGBA", (22, 5)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 21, 4), fill=c("9babb2"))
    d.rectangle((1, 0, 20, 3), fill=c("8fd3ff" if blue else "ffffff"))
    d.rectangle((1, 3, 20, 3), fill=c("4d9be6" if blue else "c7dcd0"))
    return im
LIE = [  # bottom to top
    (44, 115, 0, 0), (64, 115, 0, 1), (85, 115, 0, 0), (104, 115, 0, 0),
    (54, 111, 0, 0), (75, 110, 4, 0), (96, 111, -3, 1),
    (63, 106, 0, 0), (85, 106, 6, 0),
    (37, 104, -38, 0), (72, 102, -5, 0), (103, 108, 12, 1),
    (50, 108, 0, 0), (94, 103, 0, 0),
]
def end():
    img = Image.new("RGBA", (W, H))
    img.alpha_composite(stool(), (X - 13, FLOOR - 12))
    for x, y, a, b in LIE:
        t = towel(b)
        if a: t = t.rotate(a, resample=Image.NEAREST, expand=True)
        img.alpha_composite(t, (x, y - (t.height - 5) // 2))
    return img
if __name__ == "__main__":
    end().save(os.path.join(here, "end-alone.png"))

# Her buried: the same fourteen towels piled over where she stood (her middle at X + 36), nothing of her
# showing; the burial clip is drawn toward it.
PILE = [
    (40, 115, 0, 0), (60, 115, 0, 1), (80, 115, 0, 0), (98, 115, 4, 0),
    (50, 110, 0, 0), (70, 110, -3, 0), (88, 110, 0, 1),
    (56, 105, 3, 0), (76, 105, 0, 0),
    (62, 100, 0, 1), (79, 100, -6, 0),
    (68, 95, 0, 0), (33, 106, -35, 0), (99, 108, 18, 0),
]
def buried():
    img = Image.new("RGBA", (W, H))
    img.alpha_composite(stool(), (X - 13, FLOOR - 12))
    for x, y, a, b in PILE:
        t = towel(b)
        if a: t = t.rotate(a, resample=Image.NEAREST, expand=True)
        img.alpha_composite(t, (x, y - (t.height - 5) // 2))
    return img
if __name__ == "__main__":
    buried().save(os.path.join(here, "end-her.png"))
