from lib import *
from starts2 import herf
from PIL import ImageDraw, ImageChops
WALL, CARPET = (232, 220, 203, 255), (70, 80, 110, 255)
def bg(w, h, floor, col=WALL, fl=CARPET):
    im = Image.new("RGBA", (w, h), col); ImageDraw.Draw(im).rectangle((0, floor + 1, w, h), fill=fl); return im
def fx(k, i): return Image.open(B + f"fixed/{k}-{i}.png").convert("RGBA")
def sheet(cells, path, K=2, per=9, gap=4):
    lines = [cells[i:i + per] for i in range(0, len(cells), per)]
    w = max(sum(c.width + gap for c in l) for l in lines) * K; h = sum(max(c.height for c in l) + gap for l in lines) * K
    S = Image.new("RGB", (w, h), (40, 40, 44)); y = 0
    for l in lines:
        x = 0
        for c in l: S.paste(c.resize((c.width * K, c.height * K), Image.NEAREST), (x, y)); x += (c.width + gap) * K
        y += (max(c.height for c in l) + gap) * K
    S.save(path); print(path, S.size)
# 1: 13a. Door middle X, floor row 100 (things' last row), she 30 px east of it facing west.
door = ship("door-cabin"); doorbg = ship("door-cabin-bg")
tint = ImageChops.multiply(door, Image.new("RGBA", door.size, (217, 196, 184, 255)))
X, FL = 40, 100
stand = herf("stand").transpose(Image.FLIP_LEFT_RIGHT)
def cell(leafk, who=None, flat=None):
    im = bg(120, 106, FL)
    if leafk: ImageDraw.Draw(im).rectangle((X - 14, FL - 71, X + 13, FL - 1), fill=(46, 34, 47, 255))
    else: im.alpha_composite(doorbg, (X - 17, FL + 1 - 74))
    if who == "stand": im.alpha_composite(stand, (X + 30 - 42, FL + 1 - 84))
    if flat is not None: f = fx("d13f", flat); im.alpha_composite(f, (X + 40 - 47, FL - 80))
    if leafk: im.alpha_composite(tint.resize((max(1, round(34 * leafk)), 74), Image.NEAREST), (X + 14, FL + 1 - 74))
    return im
sheet([cell(0.42, "stand"), cell(0.75, "stand"), cell(1.0, flat=0), cell(0.42, flat=0)] + [cell(0, flat=i) for i in (0, 2, 4, 6, 8)], B + "final1.png")
# 2: 7b (the pool deck), 3: the tray (corridor), 4: 20 (balcony)
def place(k, i, col, fl):
    im = bg(128, 92, 91 - 30 + 30 - 1, col, fl); im.alpha_composite(fx(k, i).crop((0, 30, 128, 128)), (0, 0)); return im
sheet([place("c7d", i, (190, 225, 245, 255), (176, 125, 80, 255)) for i in range(9)], B + "final2.png")
sheet([place("t3e", i, WALL, CARPET) for i in range(9)], B + "final3.png")
sheet([place("g20a", i, (165, 200, 215, 255), (235, 235, 238, 255)) for i in range(9)] + [place("g20b", i, (165, 200, 215, 255), (235, 235, 238, 255)) for i in range(1, 9)], B + "final4.png")
