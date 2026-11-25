"""Mends to the clips' frames, by their own pixels.  python assets/source/balconies/mend.py

mount-2, frame 3 (the user, 2026-11-25: "the leg that is behind and up: its placement is unnatural. Lower it behind the
level of the balcony's edge"): she still stands on the balcony's floor there, her rear leg bent up behind her so that
its foot shows over the rail's top. That leg is taken out and the frame before's rear leg put in its place (4 px
forward, as her skirt stands in this frame), under the rail's top, behind the glass. Written to tries/mount-2m/, the
other frames copied as they are.
"""
import shutil
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
SRC, OUT = HERE / "tries/mount-2", HERE / "tries/mount-2m"
DARK = (46, 34, 47, 255)


def main():
    OUT.mkdir(exist_ok=True)
    for f in SRC.glob("cut-*.png"):
        shutil.copy(f, OUT / f.name)
    a, b = Image.open(SRC / "cut-03.png").convert("RGBA"), Image.open(SRC / "cut-02.png").convert("RGBA")
    pa, pb = a.load(), b.load()
    # The raised leg: everything of her forward of her back's line in rows 204 to 213 (canvas px) ...
    for y in range(204, 214):
        for x in range(40, 53):
            pa[x, y] = (0, 0, 0, 0)
    # ... and where it lay across her back, her back's own dark line again.
    for y in range(208, 214):
        for x in range(53, 57):
            r, g, bl, al = pa[x, y]
            if al and r > 150 and r > bl + 20:      # skin or sock
                pa[x, y] = DARK
    # The frame before's rear leg, from its knee to its foot (rows 220 to 226, x 48 to 56), 4 px forward.
    for y in range(220, 227):
        for x in range(48, 57):
            if pb[x, y][3] and not pa[x - 4, y][3]:
                pa[x - 4, y] = pb[x, y]
    a.save(OUT / "cut-03.png")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
