from PIL import Image
from collections import deque
B = "C:/Users/ramze/AppData/Local/Temp/dt/b1/"
WALL = (233, 223, 204, 255)
shut = Image.open(B + "door-shut.png").convert("RGBA"); sp = shut.load()
endB = Image.open(B + "door-her-flat.png").convert("RGBA")
DARK = {"dA": (22, 20, 34), "dB": (46, 34, 47)}
def fill_holes(im, dark):
    p = im.load(); w, h = im.size; outside = set(); q = deque()
    for x in range(w):
        for y in (0, h - 1): q.append((x, y))
    for y in range(h):
        for x in (0, w - 1): q.append((x, y))
    while q:
        x, y = q.popleft()
        if (x, y) in outside or not (0 <= x < w and 0 <= y < h) or p[x, y][3]: continue
        outside.add((x, y)); q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    seen = set(); n = kept = 0
    for y0 in range(h):
        for x0 in range(w):
            if p[x0, y0][3] or (x0, y0) in outside or (x0, y0) in seen: continue
            comp = []; q = deque([(x0, y0)]); seen.add((x0, y0))
            while q:
                x, y = q.popleft(); comp.append((x, y))
                for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= a < w and 0 <= b < h and not p[a, b][3] and (a, b) not in seen: seen.add((a, b)); q.append((a, b))
            touches = any(p[a, b][3] and p[a, b][:3] == dark for x, y in comp for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if 0 <= a < w and 0 <= b < h)
            if touches: kept += len(comp); continue
            for c in comp: p[c] = WALL
            n += len(comp)
    return n, kept
for k in ("dA", "dB"):
    holes = []
    for i in range(13):
        if i == 0: im = Image.open(B + f"raw/{k}-0.png").convert("RGBA")
        elif i == 12: im = (shut if k == "dA" else endB).copy()
        else:
            im = Image.open(B + f"raw/{k}-{i}.png").convert("RGBA"); p = im.load()
            for y in range(47, 121):
                for x in range(23, 28): p[x, y] = sp[x, y]
            for y in range(47, 51):
                for x in range(23, 51): p[x, y] = sp[x, y]
            holes.append(fill_holes(im, DARK[k]))
            for y in range(49, 119):
                for x in range(26, 54):
                    if p[x, y][3] and p[x, y][:3] == DARK[k]: p[x, y] = (0, 0, 0, 0)
        im.save(B + f"fixed/{k}-{i}.png")
    print(k, "holes filled per frame", holes)
