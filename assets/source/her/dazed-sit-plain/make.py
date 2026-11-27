"""Her dazed sit without the butterflies (Splash Academy's kids, the user, 2026-11-27: "When she is hit by a running kid,
remove the butterflies"): each frame of `../dazed-sit/` with every piece not joined to her taken out (the two
butterflies circling over her head). Her sway is kept as it is.
    python assets/source/her/dazed-sit-plain/make.py"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent


def pieces(im):
    px = im.load(); w, h = im.size; seen = set(); out = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] and (x, y) not in seen:
                st, comp = [(x, y)], []
                seen.add((x, y))
                while st:
                    a, b = st.pop(); comp.append((a, b))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            q = (a + dx, b + dy)
                            if 0 <= q[0] < w and 0 <= q[1] < h and q not in seen and px[q][3]:
                                seen.add(q); st.append(q)
                out.append(comp)
    return sorted(out, key=len, reverse=True)


for i in range(6):
    im = Image.open(HERE.parent / "dazed-sit" / f"{i}.png").convert("RGBA")
    px = im.load()
    for comp in pieces(im)[1:]:
        for q in comp:
            px[q] = (0, 0, 0, 0)
    im.save(HERE / f"{i}.png")
print("wrote", HERE)
