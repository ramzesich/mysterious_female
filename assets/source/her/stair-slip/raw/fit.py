# Her steep-flight slip picture set on each flight's steps: how far each shoe is from the tread under it.
import numpy as np
from PIL import Image
D = "C:/Users/ramze/AppData/Local/Temp/bb/slip/"
her = np.array(Image.open(D + "steep-2-her.png").convert("RGBA"))
AX, AY = 48, 80
def treads(run, rise):
    t = {}
    for i in range(-10, 10):
        p0 = (round(AX + i * run), round(AY - i * rise)); p1 = (round(AX + (i + 1) * run), round(AY - (i + 1) * rise))
        for x in range(p0[0], max(p0[0] + 1, p1[0])): t[x] = p1[1]
    return t
ys, xs = np.nonzero(her[:, :, 3])
for name, run, rise in (("steep", 410 / 49, 8.0), ("gentle", 164 / 14, 108 / 14)):
    T = treads(run, rise)
    for dy in range(-6, 7):
        gaps = {}
        for x in np.unique(xs):
            col = ys[xs == x]; low = col.max() + dy
            if low > 60: gaps[x] = T[x] - 1 - low
        back = [gaps[x] for x in gaps if x < 47]; front = [gaps[x] for x in gaps if x >= 47]
        print(name, "lift", -dy, "back shoe", min(back), "front shoe", min(front))
