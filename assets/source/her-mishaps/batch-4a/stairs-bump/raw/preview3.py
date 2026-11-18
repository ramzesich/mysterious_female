import json
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage
D = "C:/Users/ramze/AppData/Local/Temp/bb/g21/"
R = "C:/Users/ramze/Development/mysterious_female/"
A = Image.open(D + "bgA3.png").convert("RGBA"); B = Image.open(D + "bgB3.png").convert("RGBA")
a, bb = np.array(A).astype(int), np.array(B).astype(int)
railc = np.array([[0xe8,0xea,0xec],[0xff,0xff,0xff],[0xe3,0xe7,0xea]])
near = np.min(np.abs(a[:,:,None,:3]-railc[None,None]).sum(3),2) < 12
mask = (np.abs(a-bb).sum(2) > 0) & ~(a[:,:,2] > a[:,:,0] + 40)
rail = np.zeros_like(a); rail[mask] = a[mask]; rail = Image.fromarray(rail.astype(np.uint8))
ox, oy = 8620 - 140, 160 - 160
def cut(path, stage, specks=True):
    st = np.array(Image.open(D + stage).convert("RGBA")).astype(int)
    f = np.array(Image.open(path).convert("RGBA")).astype(int)
    d = np.abs(f - st).sum(2) > 0
    if specks:
        lab, n = ndimage.label(d, structure=np.ones((3, 3)))
        sizes = ndimage.sum(d, lab, range(1, n + 1))
        for k, sz in enumerate(sizes, 1):
            if sz < 6: d[lab == k] = False
    o = np.zeros_like(f); o[d] = f[d]
    return ImageOps.mirror(Image.fromarray(o.astype(np.uint8)))
sheet = Image.open(R + "assets/sprites/her.png").convert("RGBA")
m = json.load(open(R + "assets/sprites/her.json")); C = m["cell"]
stand = ImageOps.mirror(sheet.crop((0, 0, C, C)))
fall = [cut(D + f"raw/sit1/{i:02d}.png", "stairs.png") for i in range(1, 9)]
bump = [cut(D + f"raw/bump2/{i:02d}.png", "stairs.png") for i in range(9)]
foot = [cut(D + f"raw/foot1/{i:02d}.png", "foot-stage.png") for i in range(1, 8)]
# The anchor's corners from where she stood down to the lower flight's corner 2.
up = lambda i: (8694 + 410 * i / 49, 164 - 392 * i / 49)
lo = lambda i: (8530 + 164 * i / 14, 272 - 108 * i / 14)
corners = [up(i) for i in range(4, 0, -1)] + [lo(i) for i in range(14, 1, -1)]
seq = [("stand", corners[0])] * 4 + [(f, corners[0]) for f in fall[:6]]
k = 0
plans = [[3,5,7]] * 40
for p in plans:
    if k >= len(corners) - 1: break
    for f in p:
        if f == 5: k = min(k + 1, len(corners) - 1)
        seq.append((bump[f], corners[k]))
seq += [(f, "foot") for f in foot] + [(foot[-1], "foot")] * 12
frames = []
for img, at in seq:
    im = B.copy()
    if at == "foot":
        im.alpha_composite(img, (int(round(8530 - (127 - 50) - ox)), int(round(272 - 100 - oy))))
    elif img == "stand":
        im.alpha_composite(stand, (int(round(at[0] - 42 - ox)), int(round(at[1] - 84 - oy))))
    else:
        im.alpha_composite(img, (int(round(at[0] - 79 - ox)), int(round(at[1] - 64 - oy))))
    im.alpha_composite(rail)
    frames.append(im.crop((0, 40, 280, 320)))
big = [f.resize((f.width * 3, f.height * 3), Image.NEAREST).convert("RGB") for f in frames]
big[0].save(D + "g21-preview3.gif", save_all=True, append_images=big[1:], duration=60, loop=0)
n = len(frames)
pick = [3, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, n - 16, n - 13, n - 11, n - 9, n - 7, n - 1]
pick = sorted(set(p for p in pick if 0 <= p < n))[:16]
w, h = frames[0].size
s = Image.new("RGB", (w * 4, h * 4))
for j, q in enumerate(pick): s.paste(frames[q].convert("RGB"), ((j % 4) * w, (j // 4) * h))
s.resize((s.width * 2, s.height * 2), Image.NEAREST).save(D + "g21-strip3.png")
print(n, "frames,", round(n * 0.07, 2), "s", pick)
