"""His sleep mask's close-up from try 1: python smooth.py OUT 1.4 2 mirror (the user's choice, 2026-11-21)."""
import sys
from collections import Counter
from PIL import Image, ImageFilter
from pathlib import Path
SRC = Path(__file__).parent / "1.png"   # try 1; OUT is the close-up (../../sleepmask.png)
OUT, SIG, BAND = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
OUTLINE = (176, 127, 127, 255)
im = Image.open(SRC).convert("RGBA")
W, H = im.size
a = im.getchannel("A")
TABS = [(12, 17), (110, 116)]          # the strap's ends, by columns
body = a.copy()
for x0, x1 in TABS:
    for x in range(x0, x1 + 1):
        for y in range(H): body.putpixel((x, y), 0)
m = body.filter(ImageFilter.GaussianBlur(SIG)).point(lambda v: 255 if v >= 128 else 0)
inside = lambda x, y: 0 <= x < W and 0 <= y < H and m.getpixel((x, y)) > 0
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
dist = {}
front = [(x, y) for y in range(H) for x in range(W) if inside(x, y) and any(not inside(x + dx, y + dy) for dx, dy in N4)]
for p in front: dist[p] = 0
d = 0
while front:
    d += 1; nxt = []
    for x, y in front:
        for dx, dy in N4:
            q = (x + dx, y + dy)
            if inside(*q) and q not in dist: dist[q] = d; nxt.append(q)
    front = nxt
src_in = [p for p, dd in dist.items() if dd == BAND + 1 and im.getpixel(p)[3]]
near = lambda x, y: im.getpixel(min(src_in, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2))
out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for (x, y), dd in dist.items():
    c = OUTLINE if dd == 0 else near(x, y) if dd <= BAND or im.getpixel((x, y))[3] == 0 else im.getpixel((x, y))
    out.putpixel((x, y), c)
MIRROR = len(sys.argv) > 4
# The strap's ends: square tabs, their fill the original's commonest, outlined; tucked under the body.
for x0, x1 in TABS:
    ys = [y for x in range(x0, x1 + 1) for y in range(H) if a.getpixel((x, y))]
    y0, y1 = min(ys), max(ys)
    if MIRROR:
        rx0, rx1 = TABS[1]
        rys = [y for x in range(rx0, rx1 + 1) for y in range(H) if a.getpixel((x, y))]
        y0, y1 = min(rys), max(rys)
        mid = (y0 + y1) // 2
        redge = max(x for x in range(W) if (x, mid) in dist)
        ledge = min(x for x in range(W) if (x, mid) in dist)
        if x0 < 50:
            x1 = ledge - 1 + 3 - 3
            x0 = ledge - (rx1 - redge)
        print('tab', x0, x1, y0, y1, 'right visible', rx1 - redge, 'left edge', ledge)
    fill = Counter(im.getpixel((x, y)) for x in range(x0 + 1, x1) for y in range(y0 + 1, y1) if a.getpixel((x, y))).most_common(1)[0][0]
    rng = range(x0, x1 + 4) if x0 < 50 else range(x0 - 3, x1 + 1)
    for x in rng:
        for y in range(y0, y1 + 1):
            if out.getpixel((x, y))[3]: continue
            edge = x in (x0, x1) or y in (y0, y1)
            out.putpixel((x, y), OUTLINE if edge else fill)
out.save(OUT)
