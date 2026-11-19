"""9b's two clips cleaned (2026-11-19): her fall (seed 23): loose specks and the generator's speed lines out (only
the biggest piece kept, and pieces over 25 px touching it within 2 px); his sorry (seed 23): her figure taken out
(her start pixels, grown 2 px), then his biggest piece kept."""
from PIL import Image, ImageFilter
import os
def pieces(im):
    a = im.load(); w, h = im.size; seen = {}; out = []
    for y in range(h):
        for x in range(w):
            if a[x, y][3] > 0 and (x, y) not in seen:
                st = [(x, y)]; seen[(x, y)] = 1; comp = []
                while st:
                    p = st.pop(); comp.append(p)
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            q = (p[0] + dx, p[1] + dy)
                            if 0 <= q[0] < w and 0 <= q[1] < h and q not in seen and a[q][3] > 0:
                                seen[q] = 1; st.append(q)
                out.append(comp)
    return sorted(out, key=len, reverse=True)
def keep_main(im):
    ps = pieces(im); keep = set(ps[0])
    out = Image.new("RGBA", im.size); a, o = im.load(), out.load()
    for p in keep: o[p] = a[p]
    return out, [len(p) for p in ps[1:]]
os.makedirs("b/clean", exist_ok=True); os.makedirs("sorry/clean", exist_ok=True)
for i in range(13):
    im = Image.open(f"b/raw/s23/{i}.png").convert("RGBA")
    out, lost = keep_main(im); out.save(f"b/clean/{i}.png")
    if lost: print("b", i, lost)
her = Image.open("sorry/her-alone.png").convert("RGBA").getchannel("A").point(lambda v: 255 if v else 0).filter(ImageFilter.MaxFilter(5))
for i in range(9):
    im = Image.open(f"sorry/raw/s23/{i}.png").convert("RGBA")
    im.putalpha(Image.composite(Image.new("L", im.size, 0), im.getchannel("A"), her))
    out, lost = keep_main(im); out.save(f"sorry/clean/{i}.png")
    print("sorry", i, out.getbbox(), lost)
