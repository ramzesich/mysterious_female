import sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, r"C:/Users/ramze/Development/mysterious_female/tools")
from palettize import load_palette
D = "C:/Users/ramze/AppData/Local/Temp/bb/slip/"
name, start, stairs, mask = sys.argv[1], sys.argv[2], sys.argv[3], [int(v) for v in sys.argv[4].split(",")]
pal = np.array(load_palette(), dtype=int)
b = np.array(Image.open(D + name).convert("RGBA")).astype(int)
a = np.array(Image.open(D + start).convert("RGBA")).astype(int)
st = np.array(Image.open(D + stairs).convert("RGBA")).astype(int)
sc = set(tuple(c) for c in st[st[:, :, 3] > 0][:, :3])
H, W = b.shape[:2]
inm = np.zeros((H, W), bool); x, y, w, h = mask; inm[y:y + h, x:x + w] = True
herA = np.abs(a - st).sum(2) > 0
stc = np.array([[tuple(b[yy, xx, :3]) in sc for xx in range(W)] for yy in range(H)])
her = np.where(inm, (np.abs(b - st).sum(2) > 0) & (b[:, :, 3] > 0) & ~stc, herA)
# Loose specks out; one-px holes inside her filled from the picture.
lab, n = ndimage.label(her, structure=np.ones((3, 3)))
sizes = ndimage.sum(her, lab, range(1, n + 1))
keep = np.isin(lab, [k + 1 for k, s in enumerate(sizes) if s >= 6])
holes = ndimage.binary_fill_holes(keep) & ~keep & inm
print("specks out", int(her.sum() - keep.sum()), "holes filled", int(holes.sum()))
her = keep | holes
out = np.zeros_like(b); out[her] = b[her]
# Every new colour onto the palette (her start's own colours kept).
own = set(tuple(c) for c in a[herA][:, :3])
for yy, xx in zip(*np.nonzero(her & inm)):
    c = tuple(out[yy, xx, :3])
    if c not in own:
        out[yy, xx, :3] = pal[np.argmin(((pal - np.array(c)) ** 2).sum(1))]
out[her, 3] = 255
Image.fromarray(out.astype(np.uint8)).save(D + name.replace(".png", "-her.png"))
