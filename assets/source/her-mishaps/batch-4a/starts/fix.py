from lib import *
from analyze import comps
RAW, OUT = B + "raw/", B + "fixed/"
FLOOR = 120
def load(k, i): return Image.open(RAW + f"{k}-{i}.png").convert("RGBA")
def despeck(im, keep=40):
    cs = comps(im); px = im.load()
    for c in cs:
        if len(c) < keep:
            for p in c: px[p] = (0, 0, 0, 0)
    return im
def shift(im, dy):
    out = Image.new("RGBA", im.size); out.alpha_composite(im, (0, dy)); return out
def lowest(im): return im.getbbox()[3] - 1
LEGS = {(105, 79, 98), (127, 112, 138), (123, 129, 161)}
gull = thing("gull-perched")
def regull(im):
    px = im.load(); w, h = im.size
    head = next(y for y in range(30, 100) if sum(1 for x in range(w) if px[x, y][3] and sum(px[x, y][:3]) < 150) >= 3)
    legx = [x for y in range(head - 5, head + 2) for x in range(w) if px[x, y][3] and px[x, y][:3] in LEGS]
    lx = round(sum(legx) / len(legx))
    for y in range(h):
        for x in range(w):
            if y < head or (y < head + 2 and px[x, y][:3] in LEGS): px[x, y] = (0, 0, 0, 0)
    im.alpha_composite(gull, (lx - 11, head + 1 - 19))
    return im, head, lx
log = []
for k, perched in (("g20a", (1, 2, 5, 8)), ("g20b", (0, 1, 7, 8))):
    for i in range(9):
        im = despeck(load(k, i))
        if i in perched and not (k == "g20a" and i == 0): im, hd, lx = regull(im); log.append((k, i, hd, lx))
        if not (k == "g20a" and i == 0): im = shift(im, FLOOR - lowest(im))
        im.save(OUT + f"{k}-{i}.png")
for i, t in enumerate([78, 78, 78, 79, 79, 79, 80, 80, 80]):
    im = despeck(load("d13f", i)); im = shift(im, t - lowest(im)); im.save(OUT + f"d13f-{i}.png")
for k in ("t3e", "c7d"):
    for i in range(9): despeck(load(k, i)).save(OUT + f"{k}-{i}.png")
print(log)
for k in ("g20a", "g20b", "d13f", "t3e", "c7d"):
    print(k, [lowest(Image.open(OUT + f"{k}-{i}.png")) for i in range(9)])
