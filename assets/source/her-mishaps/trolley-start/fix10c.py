"""10c's clip without the generator's trolley (2026-11-17): in the game the world's own trolley stays
and is drawn over her while the clip plays, so the trolley the clip was drawn with is taken out of
each frame inside its box (and a pixel round it, for drift): a pixel there goes if its colour is
nearer the trolley's than hers; then any loose speck (under 12 px, apart from her) goes. Raw frames: `trolley-tries/trolley-10c-trip-raw/`; out:
`trolley-trip/`. The trolley sits at (62, 91) of the 192 x 140 frames, the floor on row 118. Its
last frame, her lying where the end picture had her, is her mended lying pose (`her/lie-fix/`:
legs flat, not one raised; the user, 2026-11-17), set where the end picture set hers."""
import json, os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(here, "..", "..", "..", "..")
atlas = Image.open(os.path.join(R, "assets/ship/ship.png")).convert("RGBA")
fr = json.load(open(os.path.join(R, "assets/ship/ship.json")))["frames"]["service-cart"]["frame"]
cart = atlas.crop((fr["x"], fr["y"], fr["x"] + fr["w"], fr["y"] + fr["h"]))
her = Image.open(os.path.join(R, "assets/source/her-mishaps/paper-start/start-4a.png")).convert("RGBA")
cols = lambda im: {c[1][:3] for c in im.getcolors(65536) if c[1][3] > 128}
tc, hc = cols(cart), cols(her)
d2 = lambda a, b: sum((x - y) ** 2 for x, y in zip(a, b))
X0, Y0 = 62, 91
src = os.path.join(here, "..", "trolley-tries", "trolley-10c-trip-raw")
out = os.path.join(here, "..", "trolley-trip"); os.makedirs(out, exist_ok=True)
for i in range(9):
    im = Image.open(os.path.join(src, f"{i}.png")).convert("RGBA"); px = im.load(); n = 0
    for y in range(Y0 - 2, min(im.height, Y0 + cart.height + 1)):
        for x in range(X0 - 2, X0 + cart.width + 2):
            c = px[x, y]
            if c[3] and min(d2(c[:3], t) for t in tc) <= min(d2(c[:3], h) for h in hc):
                px[x, y] = (0, 0, 0, 0); n += 1
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
    if i == 8:
        im = Image.new("RGBA", im.size)
        im.alpha_composite(Image.open(os.path.join(R, "assets/source/her/lie-fix/lying.png")).convert("RGBA"), (65, 44))
    im.save(os.path.join(out, f"{i}.png")); print(i, n, im.getbbox())
