"""Her pushing walk without its trolley (2026-11-17: "her hands don't hold the trolley"): pixminimax
of her character ("push-pmm-3", 73e8022b: her hands on the same pixel in every frame, two even steps
of four frames, at 6 a second her feet keep pace with her 0.8 m/s) from `start.png`. Tries in
`tries/`: v3 swung her hands 5 px off the handle (the user), and 4 px again (`push-v3-2`); the
first pixminimax held them but its legs shuffled, "like dancing a little" (the user,
`push-pmm-legs-uneven`); `push-pmm-2` let them drift 3 px; `push-pmm-4`, 12 frames, as good, longer.
From `start.png`, her walk's first frame beside the game's own trolley
(`start-raw.png`, its middle 26 px ahead of hers), edited by PixelLab so that she leans in and grips
its handle (`start-b-unused.png` the other try), and back to the same. In the game the world's
own trolley stays, under her hands, so the trolley the clip was drawn with is taken out: inside its
box a pixel goes if its colour is nearer the trolley's than hers, then any loose speck. Each frame
is cut to a 96 px canvas with her middle on its middle, as her other clips are
(`../roomservice/push/`); the first (the start, the same as the last) left out, so the loop is 1 to 8."""
import json, os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(here, "..", "..", "..", "..")
mine = os.path.join(here, "..", "roomservice")
atlas = Image.open(os.path.join(R, "assets/ship/ship.png")).convert("RGBA")
fr = json.load(open(os.path.join(R, "assets/ship/ship.json")))["frames"]["service-cart"]["frame"]
cart = atlas.crop((fr["x"], fr["y"], fr["x"] + fr["w"], fr["y"] + fr["h"]))
cols = lambda im: {c[1][:3] for c in im.getcolors(65536) if c[1][3] > 128}
her = set()
for f in ("stand.png", "walk/0.png", "walk/2.png", "carry/0.png"):
    her |= cols(Image.open(os.path.join(mine, f)).convert("RGBA"))
tc = cols(cart)
d2 = lambda a, b: sum((x - y) ** 2 for x, y in zip(a, b))
X0, Y0 = 60, 49
out = os.path.join(mine, "push"); os.makedirs(out, exist_ok=True)
for i in range(1, 9):
    im = Image.open(os.path.join(here, "raw", f"{i}.png")).convert("RGBA"); px = im.load()
    for y in range(Y0 - 4, min(im.height, Y0 + cart.height + 2)):
        for x in range(X0 - 3, min(im.width, X0 + cart.width + 3)):
            c = px[x, y]
            if c[3] and min(d2(c[:3], t) for t in tc) <= min(d2(c[:3], h) for h in her):
                px[x, y] = (0, 0, 0, 0)
    seen = set()
    for y0 in range(im.height):
        for x0 in range(im.width):
            if px[x0, y0][3] == 0 or (x0, y0) in seen:
                continue
            part, todo = [], [(x0, y0)]
            seen.add((x0, y0))
            while todo:
                x, y = todo.pop(); part.append((x, y))
                for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)):
                    if 0 <= a < im.width and 0 <= b < im.height and (a, b) not in seen and px[a, b][3]:
                        seen.add((a, b)); todo.append((a, b))
            if len(part) < 12:
                for q in part: px[q] = (0, 0, 0, 0)
    im.crop((0, 0, 96, 96)).save(os.path.join(out, f"{i - 1}.png"))
    print(i, im.getbbox())
