"""Her coming up out of the heap (18's end, 2026-11-18): her towel-turban look (`her-towel/rotations/east.png`)
from the head to the waist, standing up out of the middle of the buried heap (`ends.buried()`, its towels
drawn over her below the waist), a towel swan sitting on the turban: a generated swan (`tries/swan-*.png`)
shrunk by majority colour to `SW` px wide, its beak whitened. The emerge clip is drawn toward it."""
import os, sys
from collections import Counter
from PIL import Image
from ends import buried, towel, PILE, X, FLOOR, W, H
here = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(here, "..", "..", "..", "..")
SW = 15
def shrink(im, w):
    s = im.width / w; h = round(im.height / s); out = Image.new("RGBA", (w, h)); src = im.load()
    for y in range(h):
        for x in range(w):
            cell = [src[i, j] for i in range(int(x * s), int((x + 1) * s)) for j in range(int(y * s), int((y + 1) * s))]
            op = [p for p in cell if p[3] > 128]
            if len(op) * 2 >= len(cell): out.putpixel((x, y), Counter(op).most_common(1)[0][0])
    return out
def swan(name):
    im = Image.open(os.path.join(here, "tries", f"{name}.png")).convert("RGBA")
    im = im.crop(im.getbbox()); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and r > 150 and r - b > 60: px[x, y] = (255, 255, 255, a) if r > 200 else (199, 220, 208, a)  # the beak
    return shrink(im, SW)
def emerged(name):
    img = buried()
    her = Image.open(os.path.join(R, "assets/source/her-towel/rotations/east.png")).convert("RGBA").crop((16, 0, 52, 34))
    top = FLOOR - 50                                     # her turban's top, sitting up in the heap
    img.alpha_composite(her, (X + 36 - 18, top))
    for x, y, a, b in PILE:                             # the heap's towels over her below the waist
        if y >= 105:
            t = towel(b)
            if a: t = t.rotate(a, resample=Image.NEAREST, expand=True)
            img.alpha_composite(t, (x, y - (t.height - 5) // 2))
    sw = swan(name)
    img.alpha_composite(sw, (X + 36 - SW // 2 - 1, top - sw.height + 3))
    return img
if __name__ == "__main__":
    for n in sys.argv[1:]: emerged(n).save(os.path.join(here, f"end-emerged-{n}.png"))
