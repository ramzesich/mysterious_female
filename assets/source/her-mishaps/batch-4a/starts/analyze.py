import sys
from PIL import Image
from collections import deque
B = "C:/Users/ramze/AppData/Local/Temp/dt/b1/raw/"
def comps(im):
    a = im.split()[3].load(); w, h = im.size; seen = set(); out = []
    for y in range(h):
        for x in range(w):
            if a[x, y] and (x, y) not in seen:
                q = deque([(x, y)]); seen.add((x, y)); px = []
                while q:
                    cx, cy = q.popleft(); px.append((cx, cy))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h and a[nx, ny] and (nx, ny) not in seen: seen.add((nx, ny)); q.append((nx, ny))
                out.append(px)
    return out
for k in sys.argv[1:]:
    print("==", k)
    for i in range(9):
        im = Image.open(B + f"{k}-{i}.png").convert("RGBA")
        cs = sorted(comps(im), key=len, reverse=True)
        main = cs[0]; ys = [p[1] for p in main]; xs = [p[0] for p in main]
        small = [(len(c), min(p[0] for p in c), min(p[1] for p in c)) for c in cs[1:]]
        semi = sum(1 for p in im.getdata() if 0 < p[3] < 255)
        print(i, "main bbox", (min(xs), min(ys), max(xs), max(ys)), "n", len(main), "others", small[:8], "semi", semi)
