"""The one-way doors' pictures. Shut, seen edge on: `edge-closer.png` (the user chose it, 2026-11-18:
the push bar's end and a door closer on its free side, nothing on the other), cut to 12 x 74, the
slab in its columns 8 to 11, written to `assets/ship/door-glass-oneway-edge.png` (drawn for a door
free from the bow; mirrored for one free from the stern). Open: its leaf with its push bar (the
user chose the plain steel bar, 2026-11-18):
`leaf-steel.png` cut to the leaf (28 x 74) and written to `assets/ship/door-glass-pushbar.png`, its
glass see-through as the game draws a free door's (85% glass; the highlight 60% white over it), so
the two kinds stay one pair whatever is behind them; the bar opaque.

python assets/source/ship/pushbar/build.py"""
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
WALL = (233, 223, 204)
GLASS, WHITE = (0xbf, 0xe6, 0xf5), (255, 255, 255)


def over(c, a):
    return tuple(round(c[k] * a + WALL[k] * (1 - a)) for k in range(3))


glass_on_wall = over(GLASS, 0.85)
hl_on_wall = tuple(round(WHITE[k] * 0.6 + glass_on_wall[k] * 0.4) for k in range(3))
# (The highlight as one colour at its own alpha: 0.6 white over 0.85 glass lets 0.4 x 0.15 through.)
a_hl = 1 - 0.4 * 0.15
hl = tuple(round((0.6 * WHITE[k] + 0.4 * 0.85 * GLASS[k]) / a_hl) for k in range(3))
im = Image.open(HERE / "leaf-steel.png").convert("RGBA").crop((2, 3, 30, 77))
px = im.load()
for y in range(im.height):
    for x in range(im.width):
        c = px[x, y][:3]
        if c == glass_on_wall:
            px[x, y] = GLASS + (round(0.85 * 255),)
        elif c == hl_on_wall:
            px[x, y] = hl + (round(a_hl * 255),)
im.save(ROOT / "assets/ship/door-glass-pushbar.png")
edge = Image.open(HERE / "edge-closer.png").convert("RGBA").crop((6, 3, 18, 77))
edge.save(ROOT / "assets/ship/door-glass-oneway-edge.png")
print(im.size, edge.size, edge.getbbox())
