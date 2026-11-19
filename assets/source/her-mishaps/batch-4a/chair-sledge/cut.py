"""Gag 7a's frames (2026-11-19) from the generator's (`raw/a1`, README): 0..12.
  0      the start picture: her slip frame 0 sliding east, the world's deck chair (flipped, as the game stands it)
         18 px ahead of her middle (x 52), sliding at her (`starts/chair7a/c7a-slip0.png`)
  1..12  she is tripped by it, dives face first onto it, it folds flat under her, she lies on it on her belly like
         on a sled, arms ahead, legs up. Mended: frame 1's chair, drawn 1 px back toward her, put back on the world's
         own place; loose specks (under 8 px, apart from everything: a droplet, a chip) taken out"""
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np, sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "starts"))
from lib import ship
from scipy import ndimage

CHAIR = ImageOps.mirror(ship("deck-chair"))
CX, CY = round(70 - CHAIR.width / 2), 121 - CHAIR.height      # where the start picture has it


def unspeck(a):
    m = a[:, :, 3] > 0
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    for k, s in enumerate(sizes, 1):
        if s < 8:
            a[lab == k] = 0
    return a


def rechair(a, dx):
    """The generator's chair at dx from the world's place taken out, the world's own put in."""
    ch = np.array(CHAIR).astype(int)
    cm = ch[:, :, 3] > 0
    for y, x in zip(*np.nonzero(cm)):
        X, Y = CX + dx + x, CY + y
        if a[Y, X, 3] and np.abs(a[Y, X, :3].astype(int) - ch[y, x, :3]).sum() < 40:
            a[Y, X] = 0
    im = Image.fromarray(a)
    im.alpha_composite(CHAIR, (CX, CY))
    return np.array(im)


for i in range(13):
    a = np.array(Image.open(HERE / f"raw/a1/{i:02d}.png").convert("RGBA"))
    if i == 1:
        a = rechair(a, -1)
    if i:
        a = unspeck(a)
    Image.fromarray(a).save(HERE / f"{i}.png")
print("ok")
