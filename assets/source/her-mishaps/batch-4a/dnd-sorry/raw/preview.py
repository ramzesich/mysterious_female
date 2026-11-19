import sys
sys.path.insert(0, "C:/Users/ramze/Development/mysterious_female/tools")
from palettize import palettize
from PIL import Image, ImageOps, ImageDraw
R = "C:/Users/ramze/Development/mysterious_female/assets/source/her-mishaps/batch-4a/dnd-sorry/"
D = "C:/Users/ramze/AppData/Local/Temp/bb/g23/"
cover = [palettize(Image.open(R + f"cover/{i}.png").convert("RGBA")) for i in range(9)]
tip = [palettize(Image.open(R + f"tiptoe/{i}.png").convert("RGBA")) for i in range(9)]
rec = [Image.open(D + f"rec/{i:03d}.png").convert("RGBA") for i in range(78)]
# The new door: its hanger swung with it (frames of `door-burst-dnd`, over the recording's own door).
DD = "C:/Users/ramze/Development/mysterious_female/assets/source/her-mishaps/batch-4a/"
new = [Image.open(DD + f"door-burst-dnd/{i}.png").convert("RGBA") for i in range(13)]
old = [Image.open(DD + f"door-burst-full/{i}.png").convert("RGBA") for i in range(13)]
import numpy as np
def only_hanger(i):
    a, b = np.array(new[i]), np.array(old[i]); m = (a != b).any(2); out = np.zeros_like(a); out[m] = a[m]
    return Image.fromarray(out)
hang = [only_hanger(i) for i in range(13)]
def door_at(t):
    if t < 0: return None
    if t < 1.7: return min(6, 1 + int(t * 13))
    k = 6 + int((t - 1.7) * 13)
    return k if k <= 12 else None
def match(bg):
    # (Which frame of the door's own clip the recording shows there: the nearest by its pixels.)
    a = np.array(bg.crop((240, 44, 368, 172)).convert("RGB")).astype(int)
    best, bi_ = None, 0
    for j in range(13):
        o = np.array(old[j]); m = o[:, :, 3] > 0
        d = np.abs(a[m] - o[:, :, :3][m].astype(int)).sum() / max(1, m.sum())
        if best is None or d < best: best, bi_ = d, j
    return bi_
def with_door(bg, t):
    i = None if t < 0 else match(bg)
    if i == 0 or i == 12: i = None
    if i is None:
        bg.alpha_composite(new[0], (240, 44))   # shut, the hanger on it
    else:
        bg.alpha_composite(hang[i], (240, 44))
    return bg
X, TOP = 240.0, 44          # her middle on the screen; the cell's top (her feet on row 120)
COVER_MS, TIP_MS, SPEED = int(sys.argv[1]) if len(sys.argv) > 1 else 90, 35, 74
seq = []  # (bg index, image, x, flip) at 60 a second
for _ in range(30): seq.append((-1, cover[0], X, False))
t = 0.0
for i in range(1, 9):
    for _ in range(round(COVER_MS / 1000 * 60)): seq.append((len(seq) - 30, cover[i], X, False))
k = 0
while X > -30:
    f = tip[1 + (k * 1000 // 60 // TIP_MS) % 8]
    seq.append((len(seq) - 30, f, X, True)); X -= SPEED / 60; k += 1
frames = []
for bi, img, x, flip in seq:
    bg = with_door((rec[-1] if bi < 0 else rec[min(int((bi + 1) / 60 / 0.05), len(rec) - 1)]).copy(), (bi + 1) / 60 if bi >= 0 else -1)
    im = ImageOps.mirror(img) if flip else img
    bg.alpha_composite(im, (int(round(x - 64)), TOP))
    frames.append(bg)
print(len(frames), "frames,", round((len(frames) - 30) / 60, 2), "s after the door")
big = [f.crop((100, 30, 380, 210)).resize((840, 540), Image.NEAREST).convert("RGB") for f in frames[::3]]
big[0].save(D + "g23-preview.gif", save_all=True, append_images=big[1:], duration=50, loop=0)
pick = [29, 34, 40, 48, 62, 78, 100, 130]
s = Image.new("RGB", (160 * 4, 110 * 2))
for j, q in enumerate(pick):
    s.paste(frames[q].crop((170, 70, 330, 180)).convert("RGB"), ((j % 4) * 160, (j // 4) * 110))
s.resize((s.width * 3, s.height * 3), Image.NEAREST).save(D + "g23-strip.png")
# The clip alone, enlarged
c = cover[1:] + tip[1:] + tip[1:]
strip = Image.new("RGBA", (40 * len(c), 64), (90, 110, 130, 255))
for j, f in enumerate(c): strip.alpha_composite(f.crop((44, 58, 84, 122)), (j * 40, 0))
gif = [Image.new("RGBA", (40, 64), (90, 110, 130, 255)) for _ in c]
for g, f in zip(gif, c): g.alpha_composite(f.crop((44, 58, 84, 122)))
gif = [g.resize((240, 384), Image.NEAREST).convert("RGB") for g in gif]
gif[0].save(D + "g23-clip.gif", save_all=True, append_images=gif[1:], duration=[COVER_MS] * 8 + [TIP_MS] * 16, loop=0)
