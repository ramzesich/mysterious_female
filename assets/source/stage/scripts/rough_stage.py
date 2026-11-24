"""The stage's left half drawn flat by rule (160 x 128, the stage's forward end at column 0, its floor line under the
last row), for PixelLab to redraw; the right half is its mirror."""
from pathlib import Path
from PIL import Image, ImageDraw
import random
SRC = Path(r"C:\Users\ramze\Development\mysterious_female-catch3\assets\source\stage\gen")
W, H = 160, 128
C = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
im = Image.new("RGB", (W, H), C("#1b1828"))
d = ImageDraw.Draw(im)
# the star cloth: a few faint points
rnd = random.Random(7)
for _ in range(46):
    x, y = rnd.randrange(38, W), rnd.randrange(26, 108)
    d.point((x, y), fill=C(rnd.choice(["#3e3546", "#3e3546", "#625565", "#7f708a"])))
# faint folds of the backdrop
for x in range(44, W, 16):
    d.line((x, 22, x, 119), fill=C("#211d30"))
# the boards, seen a little from above
d.rectangle((0, 120, W - 1, 127), fill=C("#5e3d2c"))
d.line((0, 120, W - 1, 120), fill=C("#74503a"))
d.line((0, 127, W - 1, 127), fill=C("#45293f"))
for x in range(10, W, 22):
    d.line((x, 121, x - 3, 127), fill=C("#45293f"))
# the proscenium's curtain, gathered by a gold tie-back
d.rectangle((0, 8, 33, 119), fill=C("#ae2334"))
for k in range(4, 34, 7):
    d.rectangle((k, 8, k + 1, 119), fill=C("#831c5d"))
    d.line((k + 3, 8, k + 3, 119), fill=C("#c32454"))
d.polygon([(34, 40), (27, 62), (34, 84)], fill=C("#1b1828"))        # the drape drawn in at its tie-back
d.rectangle((0, 61, 28, 64), fill=C("#d9a43b"))
d.line((0, 65, 28, 65), fill=C("#9e4539"))
d.rectangle((0, 116, 33, 119), fill=C("#831c5d"))
for x in range(1, 34, 3):
    d.point((x, 119), fill=C("#d9a43b"))
# the valance: a band, swags, a gold fringe
d.rectangle((0, 0, W - 1, 11), fill=C("#c32454"))
d.line((0, 0, W - 1, 0), fill=C("#831c5d"))
for x in range(0, W, 16):
    d.polygon([(x, 12), (x + 16, 12), (x + 8, 19)], fill=C("#ae2334"))
    d.line((x, 12, x + 8, 19), fill=C("#d9a43b")); d.line((x + 16, 12, x + 8, 19), fill=C("#d9a43b"))
d.line((0, 11, W - 1, 11), fill=C("#d9a43b"))
# the lighting bar and its lanterns
d.rectangle((36, 21, W - 1, 22), fill=C("#3e3546"))
for x in (48, 139):
    d.rectangle((x - 1, 22, x, 24), fill=C("#3e3546"))
    d.rectangle((x - 4, 24, x + 3, 30), fill=C("#3e3546"))
    d.line((x - 4, 24, x + 3, 24), fill=C("#625565"))
    d.rectangle((x - 2, 31, x + 1, 31), fill=C("#fbff86"))
im.save(SRC / "stage-rough-left.png")
full = Image.new("RGB", (320, H)); full.paste(im, (0, 0)); full.paste(im.transpose(Image.FLIP_LEFT_RIGHT), (160, 0))
full.resize((960, 384), Image.NEAREST).save(Path(__file__).resolve().parent.parent / "out" / "stage-rough-3x.png")
print("ok")
