import json
from PIL import Image, ImageDraw
D = r"C:/Users/ramze/AppData/Local/Temp/bb/g21/"
R = r"C:/Users/ramze/Development/mysterious_female/"
sheet = Image.open(R + "assets/sprites/her.png").convert("RGBA")
m = json.load(open(R + "assets/sprites/her.json"))
C, cols = m["cell"], m["cols"]
def cell(i):
    return sheet.crop(((i % cols) * C, (i // cols) * C, (i % cols + 1) * C, (i // cols + 1) * C))
hx = lambda c: tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) + (255,)
look = dict(carpet=hx("#9babb2"), fleck=hx("#625565"), nosing=hx("#3e3546"), side=hx("#7f708a"), edge=hx("#3e3546"))
S = 128
# The upper flight's slope, descending to the east (the game's, mirrored): 8 px rise per step, 410/49 run.
run, rise = 410 / 49, 8.0
# Her feet at (48, 64): the line through it.
fx, fy = 48, 64
def stairs():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    g = ImageDraw.Draw(im)
    for i in range(-10, 14):
        x0, y0 = fx + i * run, fy + i * rise          # top of step i (descending east)
        x1, y1 = fx + (i + 1) * run, fy + (i + 1) * rise
        x, w = int(round(x0)), max(1, int(round(x1)) - int(round(x0)))
        top = int(round(y0))
        # the step's tread at y0 from x0 to x1, its side down to the underside
        g.rectangle([x, top, x + w - 1, int(round(y1)) + 5 - 1], fill=look["side"])
        g.rectangle([x, top, x + w - 1, top + 2], fill=look["carpet"])
        g.point((x + w // 2, top + 1), fill=look["fleck"])
        g.rectangle([x + w - 1, top, x + w - 1, top + 3], fill=look["nosing"])
    return im
st = stairs()
st.save(D + "stairs.png")
her = cell(0)
im = st.copy()
im.alpha_composite(her, (fx - C // 2, fy - C))
im.save(D + "s21-start.png")
im.resize((S * 4, S * 4), Image.NEAREST).save(D + "s21-start-4x.png")
