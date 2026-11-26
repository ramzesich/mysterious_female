"""The new pillow fort's flat rough, strict side view (plan-the-rest §7f, P6; the user, 2026-11-26: the old one "is 3D,
while we just crawl in profile"): two cushion stacks at the ends, a striped blanket across them as a low roof, its hem at
30 px over the floor (the fort is solid from there up), its ends draped down the stacks' outer sides, the space under it
open, so that she shows crawling inside. 176 x 64, the floor the bottom row."""
from pathlib import Path
from PIL import Image, ImageDraw

W, H = 176, 64
FLOOR = H - 1
HEM = FLOOR - 30                      # the roof's lowest row (solid from 30 px up)
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
OUT = (46, 34, 47, 255)
CUSHIONS = [(232, 59, 59), (77, 155, 230), (249, 194, 43)]


def cushion(x0, y0, w, h, c):
    d.rounded_rectangle((x0, y0, x0 + w - 1, y0 + h - 1), radius=3, fill=c + (255,), outline=OUT)
    d.line((x0 + 3, y0 + 2, x0 + w - 4, y0 + 2), fill=tuple(min(255, v + 50) for v in c) + (255,))      # its lit top
    d.point((x0 + w // 2, y0 + h // 2), fill=OUT)                                                       # a button


# The two stacks, three cushions each, from the floor up to the roof.
for x0 in (4, W - 4 - 24):
    y = FLOOR + 1
    for k, c in enumerate(CUSHIONS if x0 < 50 else CUSHIONS[::-1]):
        h = 11
        y -= h
        cushion(x0 + (k % 2), y, 24, h, c)
top = FLOOR + 1 - 33                  # the stacks' top
# The blanket: a roof 7 rows thick lying on the stacks, sagging 2 px in the middle, striped, a fringed hem.
STRIPES = [(36, 159, 222), (255, 255, 255), (241, 108, 172), (255, 255, 255)]
for x in range(0, W):
    sag = round(2 * (1 - ((x - W / 2) / (W / 2)) ** 2))
    y0 = top - 7 + sag
    for y in range(y0, y0 + 7):
        c = STRIPES[(x // 6) % len(STRIPES)]
        im.putpixel((x, y), (c[0], c[1], c[2], 255) if y not in (y0, y0 + 6) else OUT)
    # (its fringe, every other column, down to the hem)
    if 28 < x < W - 29 and x % 2 == 0:
        for y in range(y0 + 7, min(HEM, y0 + 9) + 1):
            im.putpixel((x, y), (249, 194, 43, 255))
# Its ends draped down the stacks' outer sides, in folds.
for side in (0, 1):
    for x in range(0, 6):
        xx = x if side == 0 else W - 1 - x
        for y in range(top - 1, top + 22 - x * 2):
            c = STRIPES[(y // 4) % len(STRIPES)]
            im.putpixel((xx, y), OUT if x == 0 else (c[0], c[1], c[2], 255))
im.save(Path(__file__).with_name("rough.png"))
print("rough", im.size, "hem row", HEM, "stack top", top)
