"""The open glass leaf of a door across a deck, exactly as `buildBulkhead` draws it (steel frame,
swing 1: its handle on the right), on a 32 x 80 canvas (the leaf at (2, 3), 28 x 74, its bottom row
on the floor's last row, 76): the source the push bar is inpainted into (the user, 2026-11-18: the
one-way doors get their push bar). The glass, drawn at 85% over whatever is behind it, is set over
the corridor wall's colour, as it shows in the game.

python assets/source/ship/pushbar/leaf.py"""
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
WALL = (233, 223, 204)


def mix(c, a, under=WALL):
    return tuple(round(c[k] * a + under[k] * (1 - a)) for k in range(3)) + (255,)


def leaf(grip=True):
    im = Image.new("RGBA", (32, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    L, T, W, H = 2, 3, 28, 74
    rim, glass, white, handle = (0x9b, 0xab, 0xb2), (0xbf, 0xe6, 0xf5), (255, 255, 255), (0x62, 0x55, 0x65)
    d.rectangle((L, T, L + W - 1, T + H - 1), fill=rim + (255,))
    g = mix(glass, 0.85)
    d.rectangle((L + 3, T + 3, L + 3 + 22 - 1, T + 3 + H - 8 - 1), fill=g)
    hl = tuple(round(white[k] * 0.6 + g[k] * 0.4) for k in range(3)) + (255,)
    d.rectangle((L + 6, T + 6, L + 6 + 2 - 1, T + 6 + 30 - 1), fill=hl)
    if grip:
        # (floor - 40 to floor - 30: the leaf's rows 34 to 43)
        d.rectangle((L + 22, T + 34, L + 22 + 3 - 1, T + 34 + 10 - 1), fill=handle + (255,))
    return im


if __name__ == "__main__":
    leaf().save(HERE / "leaf-free.png")
    leaf(False).save(HERE / "leaf-plain.png")
    big = Image.new("RGBA", (32, 80), WALL + (255,)); big.alpha_composite(leaf())
    big.resize((256, 640), Image.NEAREST).save(HERE / "leaf-free-x8.png")
