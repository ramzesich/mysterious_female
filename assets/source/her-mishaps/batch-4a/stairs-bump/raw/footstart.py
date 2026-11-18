import json
import numpy as np
from PIL import Image, ImageDraw
D = "C:/Users/ramze/AppData/Local/Temp/bb/g21/"
R = "C:/Users/ramze/Development/mysterious_female/"
hx = lambda c: tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) + (255,)
look = dict(carpet=hx("#9babb2"), fleck=hx("#625565"), nosing=hx("#3e3546"), side=hx("#7f708a"))
S = 128
# The floor's own rows under the foot, from the game (the roof by the foot of the stairway).
B = Image.open(D + "bgB2.png").convert("RGBA")
fy_bg = 272 - (210 - 100)
floor_rows = B.crop((40, fy_bg, 41, fy_bg + 8))   # a column of the floor's rows
print([floor_rows.getpixel((0, k)) for k in range(8)])
FX, FY = 50, 100
run, rise = 164 / 14, 108 / 14
stage = Image.new("RGBA", (S, S), (0, 0, 0, 0))
g = ImageDraw.Draw(stage)
for k in range(8):
    g.line([(0, FY + k), (S - 1, FY + k)], fill=(232, 234, 236, 255))
for i in range(1, 12):   # step i: from corner i (upper) to corner i-1 (lower), descending east
    x0, y0 = FX - i * run, FY - i * rise
    x1, y1 = FX - (i - 1) * run, FY - (i - 1) * rise
    x, w = int(round(x0)), int(round(x1)) - int(round(x0))
    top = int(round(y0))
    g.rectangle([x, top, x + w - 1, FY - 1], fill=look["side"])
    g.rectangle([x, top, x + w - 1, top + 2], fill=look["carpet"])
    g.point((x + w // 2, top + 1), fill=look["fleck"])
    g.rectangle([x + w - 1, top, x + w - 1, top + 3], fill=look["nosing"])
stage.save(D + "foot-stage.png")
st = np.array(Image.open(D + "stairs.png").convert("RGBA")).astype(int)
f = np.array(Image.open(D + "raw/bump2/00.png").convert("RGBA")).astype(int)
d = np.abs(f - st).sum(2) > 0
her = np.zeros_like(f); her[d] = f[d]; her = Image.fromarray(her.astype(np.uint8))
a = stage.copy()
cx, cy = FX - 2 * run, FY - 2 * rise
a.alpha_composite(her, (int(round(cx - 48)), int(round(cy - 64))))
a.save(D + "foot-first.png")
sheet = Image.open(R + "assets/sprites/her.png").convert("RGBA")
m = json.load(open(R + "assets/sprites/her.json")); C, cols = m["cell"], m["cols"]
i = m["anims"]["dazed-sit"][0]
sit = sheet.crop(((i % cols) * C, (i // cols) * C, (i % cols + 1) * C, (i // cols + 1) * C))
b = stage.copy()
b.alpha_composite(sit, (FX + 14 - C // 2, FY - C))
b.save(D + "foot-last.png")
s = Image.new("RGBA", (256, 128), (230, 236, 240, 255)); s.alpha_composite(a); s.alpha_composite(b, (128, 0))
s.resize((1024, 512), Image.NEAREST).save(D + "foot-ends.png")
