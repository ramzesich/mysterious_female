import json
import numpy as np
from PIL import Image, ImageOps
R = "C:/Users/ramze/Development/mysterious_female/"
D = "C:/Users/ramze/AppData/Local/Temp/bb/g22/"
L = np.array([1, 0.84, 0.74, 1])
bg = Image.fromarray(np.array(Image.open(D + "bg.png").convert("RGBA"))[1::2, 1::2])
def wash(im):
    a = np.array(im).astype(float) * L
    return Image.fromarray(np.round(a).astype(np.uint8))
fl = lambda im: ImageOps.mirror(im)  # west, as she glides to the bow
clip = [wash(fl(Image.open(R + f"assets/source/her-mishaps/batch-4a/parasol-flip/flip/{i}.png").convert("RGBA"))) for i in range(9)]
glide = [wash(fl(Image.open(R + f"assets/source/her-mishaps/batch-4a/parasol-flip/raw/start-{i}.png").convert("RGBA"))) for i in (322, 323)]
FX = 127 - 56  # her feet's column, mirrored
X, Y = 240, 165.0
seq, dt = [], 1 / 60
# Gliding down at 55 px/s, her two glide frames.
t = 0
for k in range(36):
    seq.append((glide[(k // 8) % 2], X, Y)); Y += 55 * dt
# The flip: frames 1-3, still sinking at the glide's pace.
for i in (1, 2, 3):
    for _ in range(5): seq.append((clip[i], X, Y)); Y += 55 * dt
# The drop, kicking (4..8 looped), a softer fall than a closed parasol's.
vy, k = 55, 0
G, CAP = 500, 240
loop = [4, 5, 6, 7, 8]
while Y - 40 < 270 + 10:
    seq.append((clip[loop[(k // 6) % 5]], X, Y)); k += 1
    vy = min(vy + G * dt, CAP); Y += vy * dt
frames = []
for img, x, y in seq:
    im = bg.copy()
    im.alpha_composite(img, (int(round(x - FX)), int(round(y - 112))))
    frames.append(im)
print(len(seq), "frames", round(len(seq) / 60, 2), "s; after the hit", round((len(seq) - 36) / 60, 2))
big = [f.resize((960, 540), Image.NEAREST).convert("RGB") for f in frames[::2]]
big[0].save(D + "g22-preview.gif", save_all=True, append_images=big[1:], duration=33, loop=0)
pick = [34, 37, 42, 47, 55, 62, 70, 78]
pick = [p for p in pick if p < len(frames)]
s = Image.new("RGB", (240 * 4, 270 * 2))
for j, q in enumerate(pick):
    s.paste(frames[q].crop((120, 0, 360, 270)).convert("RGB"), ((j % 4) * 240, (j // 4) * 270))
s.resize((s.width * 2, s.height * 2), Image.NEAREST).save(D + "g22-strip.png")
