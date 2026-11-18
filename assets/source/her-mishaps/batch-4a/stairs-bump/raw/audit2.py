import json, math
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage
D = "C:/Users/ramze/AppData/Local/Temp/bb/g21/"
R = "C:/Users/ramze/Development/mysterious_female/"
def cut(path, stage):
    st = np.array(Image.open(D + stage).convert("RGBA")).astype(int)
    f = np.array(Image.open(path).convert("RGBA")).astype(int)
    d = np.abs(f - st).sum(2) > 0
    lab, n = ndimage.label(d, structure=np.ones((3, 3)))
    sizes = ndimage.sum(d, lab, range(1, n + 1))
    for k, sz in enumerate(sizes, 1):
        if sz < 6: d[lab == k] = False
    return np.fliplr(d)
sheet = Image.open(R + "assets/sprites/her.png").convert("RGBA")
m = json.load(open(R + "assets/sprites/her.json")); C = m["cell"]
stand = np.fliplr(np.array(sheet.crop((0, 0, C, C)))[:, :, 3] > 0)
fall = [cut(D + f"raw/sit1/{i:02d}.png", "stairs.png") for i in range(1, 9)]
bump = [cut(D + f"raw/bump2/{i:02d}.png", "stairs.png") for i in range(9)]
foot = [cut(D + f"raw/foot1/{i:02d}.png", "foot-stage.png") for i in range(1, 8)]
# The treads as the game draws them (drawStairs): step i from at(i/n) to at((i+1)/n), tread at p1.y.
def flight(b, t, n):
    out = []
    for i in range(n):
        p0 = (round(b[0] + (t[0] - b[0]) * i / n), round(b[1] + (t[1] - b[1]) * i / n))
        p1 = (round(b[0] + (t[0] - b[0]) * (i + 1) / n), round(b[1] + (t[1] - b[1]) * (i + 1) / n))
        out.append((min(p0[0], p1[0]), max(p0[0], p1[0]), p1[1]))
    return out
treads = flight((8694, 164), (9104, -228), 49) + flight((8530, 272), (8694, 164), 14)
def surface(x):
    ys = [y for a, b, y in treads if a <= x < b]
    return min(ys) if ys else 272      # (the roof's floor past the foot)
up = lambda i: (8694 + 410 * i / 49, 164 - 392 * i / 49)
lo = lambda i: (8530 + 164 * i / 14, 272 - 108 * i / 14)
corners = [up(i) for i in range(4, 0, -1)] + [lo(i) for i in range(14, 1, -1)]
seq = [(stand, corners[0], "stand")] * 2 + [(f, corners[0], f"fall{i+1}") for i, f in enumerate(fall)]
k = 0
plans = [[1,2,3,4,5,6,7,8], [2,4,5,7], [3,5,7], [3,5,7]] + [[4,7]] * 30
for p in plans:
    if k >= len(corners) - 1: break
    for f in p:
        if f == 5 or (len(p) == 2 and f == 7): k = min(k + 1, len(corners) - 1)
        seq.append((bump[f], corners[k], f"bump{f}@{k}"))
seq += [(f, "foot", f"foot{i+1}") for i, f in enumerate(foot)]
prev = None
for mask, at, name in seq:
    if at == "foot": X, Y = 8530 - 77, 272 - 100
    elif name == "stand": X, Y = round(at[0] - 42), round(at[1] - 84)
    else: X, Y = round(at[0] - 79), round(at[1] - 64)
    ys, xs = np.nonzero(mask)
    gaps = []
    for x in np.unique(xs):
        low = ys[xs == x].max() + Y          # her lowest px in this world column
        gaps.append(surface(x + X) - 1 - low)   # 0: on the tread; <0 into it; >0 above it
    g = np.array(gaps)
    box = (xs.min() + X, ys.min() + Y, xs.max() + X, ys.max() + Y)
    move = "" if prev is None else f"move {box[0]-prev[0]:+d},{box[3]-prev[3]:+d}"
    print(f"{name:12s} touch(min gap) {g.min():+3d}  into-tread px cols {int((g<0).sum()):2d} deepest {g.min():+d}  {move}")
    prev = box

# The composed frames themselves, around her, 3x: the look at contact and overlaps.
A = Image.open(D + "bgA3.png").convert("RGBA"); B = Image.open(D + "bgB3.png").convert("RGBA")
a_, b_ = np.array(A).astype(int), np.array(B).astype(int)
railc = np.array([[0xe8,0xea,0xec],[0xff,0xff,0xff],[0xe3,0xe7,0xea]])
near = np.min(np.abs(a_[:,:,None,:3]-railc[None,None]).sum(3),2) < 12
rm = (np.abs(a_-b_).sum(2) > 0) & ~(a_[:,:,2] > a_[:,:,0] + 40)
rail = np.zeros_like(a_); rail[rm] = a_[rm]; rail = Image.fromarray(rail.astype(np.uint8))
ox, oy = 8620 - 140, 160 - 160
def pic(path, stage):
    st = np.array(Image.open(D + stage).convert("RGBA")).astype(int)
    f = np.array(Image.open(path).convert("RGBA")).astype(int)
    d = cut(path, stage)
    o = np.zeros_like(f); o[np.fliplr(d)] = f[np.fliplr(d)]
    return ImageOps.mirror(Image.fromarray(o.astype(np.uint8)))
P = {"fall": [pic(D + f"raw/sit1/{i:02d}.png", "stairs.png") for i in range(1, 9)],
     "bump": [pic(D + f"raw/bump2/{i:02d}.png", "stairs.png") for i in range(9)],
     "foot": [pic(D + f"raw/foot1/{i:02d}.png", "foot-stage.png") for i in range(1, 8)]}
standp = ImageOps.mirror(sheet.crop((0, 0, C, C)))
want = ["stand"] + [f"fall{i}" for i in range(1, 9)] + [f"bump{i}@0" for i in range(1, 5)] + [f"bump{i}@1" for i in range(5, 9)] + ["bump4@5", "bump7@6", "bump4@12", "bump7@13", "bump4@15", "bump7@16"] + [f"foot{i}" for i in range(1, 8)]
tiles = []
for mask, at, name in seq:
    if name not in want: continue
    want.remove(name)
    im = B.copy()
    if at == "foot": img, X, Y = P["foot"][int(name[4:]) - 1], 8530 - 77, 272 - 100
    elif name == "stand": img, X, Y = standp, round(at[0] - 42), round(at[1] - 84)
    elif name.startswith("fall"): img, X, Y = P["fall"][int(name[4:]) - 1], round(at[0] - 79), round(at[1] - 64)
    else: img, X, Y = P["bump"][int(name[4])], round(at[0] - 79), round(at[1] - 64)
    im.alpha_composite(img, (X - ox, Y - oy)); im.alpha_composite(rail)
    ys, xs = np.nonzero(np.array(img)[:, :, 3])
    cx, cy = X - ox + (xs.min() + xs.max()) // 2, Y - oy + (ys.min() + ys.max()) // 2
    t = im.crop((cx - 40, cy - 36, cx + 40, cy + 36))
    tiles.append(t)
w, h = 80, 72
cols = 8
s = Image.new("RGBA", (w * cols, h * math.ceil(len(tiles) / cols)), (0, 0, 0, 255))
for i, t in enumerate(tiles): s.paste(t, ((i % cols) * w, (i // cols) * h))
s.resize((s.width * 3, s.height * 3), Image.NEAREST).save(D + "audit-contact.png")
print(len(tiles), "tiles")
