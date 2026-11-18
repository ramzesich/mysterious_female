import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, r"C:/Users/ramze/Development/mysterious_female/tools")
from palettize import load_palette
D = "C:/Users/ramze/AppData/Local/Temp/bb/cling/"
pal = np.array(load_palette(), dtype=int)
st = np.array(Image.open(D + "stairs.png").convert("RGBA")).astype(int)
stair_geo = st[:, :, 3] > 0
K = 8.0 / (410 / 49)              # the flight's slope: y falls K px per px to the east
H, W = st.shape[:2]
Y, X = np.mgrid[0:H, 0:W]
band_of = np.round(Y + K * X).astype(int)
def cut(path):
    f = np.array(Image.open(path).convert("RGBA")).astype(int)
    op = f[:, :, 3] > 0
    whiteish = op & (f[:, :, :3].min(2) > 215)
    # The rail in this frame: the bands of y + K x where white runs the whole picture's width.
    counts = np.bincount(band_of[whiteish].ravel(), minlength=band_of.max() + 1)
    rail_bands = [b for b in range(len(counts)) if counts[b] >= 25]
    # The rail's band (its bands and one either side): whatever the generator drew there (white, grey,
    # dashed) is taken out; the game's own rail is drawn in front of her along it.
    band = np.isin(band_of, rail_bands + [min(rail_bands) - 1, max(rail_bands) + 1])
    # The stairs: as drawn, or a stair pixel the generator moved on the stairs' own place.
    same = (np.abs(f - st).sum(2) == 0) & stair_geo
    STAIRC = np.array([[0x9b, 0xab, 0xb2], [0x62, 0x55, 0x65], [0x3e, 0x35, 0x46], [0x7f, 0x70, 0x8a]])
    stairc = (np.abs(f[:, :, None, :3] - STAIRC[None, None]).sum(3) == 0).any(2)
    stairs = same | (stairc & stair_geo)
    cand = op & ~band & ~stairs
    # Her: the biggest piece, joined across the band.
    joined = cand | (band & ndimage.binary_dilation(cand, iterations=3))
    lab, n = ndimage.label(joined, structure=np.ones((3, 3)))
    sizes = ndimage.sum(cand, lab, range(1, n + 1))
    body = lab == 1 + int(np.argmax(sizes))
    her = cand & body
    loose = int(cand.sum() - her.sum())
    # Across the band, where she is both above and below within 5 px: the nearer of the two.
    out = np.zeros_like(f); out[her] = f[her]
    holes = 0
    for y, x in zip(*np.nonzero(band)):
        up = next((d for d in range(1, 6) if y - d >= 0 and her[y - d, x]), None)
        dn = next((d for d in range(1, 6) if y + d < H and her[y + d, x]), None)
        if up and dn:
            yy = y - up if up <= dn else y + dn
            out[y, x] = f[yy, x]; holes += 1
    m = out[:, :, 3] > 0
    for y, x in zip(*np.nonzero(m)):
        out[y, x, :3] = pal[np.argmin(((pal - out[y, x, :3]) ** 2).sum(1))]
    out[m, 3] = 255
    return out.astype(np.uint8), loose, holes, rail_bands
if __name__ == "__main__":
    for name in ("up", "down"):
        os.makedirs(D + f"cut/{name}", exist_ok=True)
        for i in range(9):
            o, loose, h, bands = cut(D + f"raw/{name}/{i:02d}.png")
            Image.fromarray(o).save(D + f"cut/{name}/{i:02d}.png")
            ys, xs = np.nonzero(o[:, :, 3])
            print(name, i, "rail bands", bands, "loose out", loose, "filled", h, "rows", ys.min(), ys.max())
