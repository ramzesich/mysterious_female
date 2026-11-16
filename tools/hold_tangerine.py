"""Puts a tangerine in her fist in her toss's frames (docs/plan-three-uses.md §1.2): from
assets/source/her/toss/ (PixelLab's raw frames, kept as they came) to toss-held/, which
tools/build_sprites.py builds into her sheet. In the frames before she lets go (0 to 3) the
fruit (the game's own, src/textures.js, its leaves too) is laid over her fist and her skin's
pixels around it are put back on top, so her fingers close over it; from frame 4 it is in the
air, a thing of the game's own (`THROW.hand`, `THROW.handY` in src/config.js).

    python tools/hold_tangerine.py

Her fist was found by eye on the frames enlarged with a grid (2026-11-15): `FIST` is the fruit's
middle in each frame's 96 px canvas.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "her" / "toss"
OUT = ROOT / "assets" / "source" / "her" / "toss-held"

# The game's tangerine (`FRUIT.tangerine` in src/textures.js, docs/plan-three-uses.md §1.7), its
# leaves too; `FIST` is its fruit's middle, the picture's (5, 6).
FRUIT = [
    "....K.KK..",
    "...KlKllK.",
    "..KollLK..",
    ".KoooooOK.",
    "KoohhooOOK",
    "KohoooooOK",
    "KOoOoooOOK",
    ".KOOOOOOK.",
    "..KOOOOK..",
    "...KKKK...",
]
COLOURS = {"K": (0x2E, 0x22, 0x2F, 255), "o": (0xFB, 0x6B, 0x1D, 255), "O": (0xEA, 0x4F, 0x36, 255),
           "h": (0xFD, 0xCB, 0xB0, 255), "l": (0x23, 0x90, 0x63, 255), "L": (0x16, 0x5A, 0x4C, 255)}
MIDDLE = (5, 6)
# Frame: the fruit's middle (x, y). Frame 0 her hand hangs by her skirt, 1 and 2 swung back,
# 3 swinging past her hip.
FIST = {0: (43, 56), 1: (36, 53), 2: (37, 54), 3: (58, 53)}
KEEP = 4            # px round the fist where her skin is put back over the fruit


def skin(c):
    r, g, b, a = c
    return a > 0 and r > 180 and g > 120 and b > 90 and r > b + 30


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in sorted(SRC.glob("*.png"), key=lambda p: int(p.stem)):
        i = int(f.stem)
        im = Image.open(f).convert("RGBA")
        if i in FIST:
            orig = im.copy()
            cx, cy = FIST[i]
            x0, y0 = cx - MIDDLE[0], cy - MIDDLE[1]
            for dy, row in enumerate(FRUIT):
                for dx, ch in enumerate(row):
                    if ch in COLOURS:
                        im.putpixel((x0 + dx, y0 + dy), COLOURS[ch])
            # Her fingers over it.
            for y in range(cy - KEEP, cy + KEEP + 1):
                for x in range(cx - KEEP, cx + KEEP + 1):
                    if skin(orig.getpixel((x, y))):
                        im.putpixel((x, y), orig.getpixel((x, y)))
        im.save(OUT / f.name)
    print("toss-held:", len(list(OUT.glob("*.png"))), "frames")


if __name__ == "__main__":
    main()
