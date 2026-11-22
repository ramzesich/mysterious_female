"""The reading nook's photo (`slot_nook`): PixelLab's try 2 of her armchair (`assets/source/photos/nook/try2.png`) put
back to her own colours (the user, 2026-11-22): the chair's navy to the grey of her throw by its lightness, with the
throw's woolly weave as light and dark flecks that follow the shading (not on the outlines); the patterned cushion,
found by its own outline, a lighter mauve grey with a white pattern; the lion as it came.

    python tools/recolour_nook_photo.py   ->  assets/source/photos/nook/try2-grey.png, assets/ship/photos/slot_nook.png
"""
import random
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "photos" / "nook"


def main():
    im = Image.open(SRC / "try2.png").convert("RGBA")
    a = np.array(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    # The patterned cushion: everything inside its dark outline, filled from its middle (its top right half is a bluer
    # grey than the rest: found by its purples alone, that half went to the chair, a diagonal with a yellow tint).
    dark = (lum < 40).astype(np.uint8)
    fill = np.zeros((a.shape[0] + 2, a.shape[1] + 2), np.uint8)
    canvas = dark.copy() * 255
    cv2.floodFill(canvas, fill, (64, 50), 128, flags=4)
    cushion = (canvas == 128)
    cushion[:, :45] = False
    cushion[:, 83:] = False
    cushion = cv2.dilate(cushion.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (dark == 0) | cushion
    out = a.copy()
    chair = (b > r + 6) & (g >= r - 1) & ~cushion
    v = np.where(lum < 15, 22 + lum, np.minimum(200, 30 + lum * 1.32)).astype(int)
    # The weave: flecks a little lighter and a little darker, scattered, more of them where the throw is lit.
    rnd = random.Random(5)
    weave = np.zeros_like(v)
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if chair[y, x] and lum[y, x] >= 15:
                k = rnd.random()
                if k < 0.16:
                    weave[y, x] = 22
                elif k < 0.30:
                    weave[y, x] = -16
                elif k < 0.34:
                    weave[y, x] = 40
    v = np.clip(v + weave, 0, 230)
    for c, add in ((0, 0), (1, 0), (2, 3)):
        out[..., c] = np.where(chair, np.minimum(255, v + add), out[..., c])
    pattern = cushion & (r > 180) & (g > 150) & (r - b > 20)       # its pattern: the light yellows, made white
    cush = cushion & ~pattern
    v2 = np.where(lum < 15, 22 + lum, np.minimum(210, 40 + lum * 1.35)).astype(int)
    for c, add in ((0, 6), (1, 2), (2, 12)):
        out[..., c] = np.where(cush, np.minimum(255, v2 + add), out[..., c])
    for c, val in ((0, 232), (1, 232), (2, 236)):
        out[..., c] = np.where(pattern, val, out[..., c])
    pic = Image.fromarray(out.astype(np.uint8))
    pic.save(SRC / "try2-grey.png")
    (ROOT / "assets" / "ship" / "photos").mkdir(parents=True, exist_ok=True)
    pic.save(ROOT / "assets" / "ship" / "photos" / "slot_nook.png")
    print("wrote try2-grey.png and assets/ship/photos/slot_nook.png")


if __name__ == "__main__":
    main()
