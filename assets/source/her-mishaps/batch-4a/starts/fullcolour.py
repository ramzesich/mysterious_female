from lib import *
SRC = R + "assets/source/her-mishaps/batch-4a/door-burst/"
WALL, MUTE = (0xE9, 0xDF, 0xCC), 0.35
full, mut = ship("door-cabin"), ship("door-cabin-bg")
# the exact pairs: each muted colour of the shut door -> its full colour
pairs = {}
for a, b in zip(mut.getdata(), full.getdata()):
    if a[3] and b[3]: pairs.setdefault(a[:3], set()).add(b[:3])
amb = {k: v for k, v in pairs.items() if len(v) > 1}
print("colours", len(pairs), "ambiguous", amb)
fullcols = set(p[:3] for p in full.getdata() if p[3])
def unmute(c):
    if c in pairs: return next(iter(pairs[c]))
    if c == (233, 223, 204): return c
    raw = tuple(max(0, min(255, round((m - MUTE * w) / (1 - MUTE)))) for m, w in zip(c, WALL))
    return min(fullcols, key=lambda f: sum((x - y) ** 2 for x, y in zip(f, raw)))
out = []
for i in range(13):
    im = Image.open(SRC + f"{i}.png").convert("RGBA"); px = im.load()
    for y in range(128):
        for x in range(128):
            if px[x, y][3]: px[x, y] = (*unmute(px[x, y][:3]), 255)
    out.append(im)
    im.save(B + f"fullburst-{i}.png")
d0 = out[0].crop((23, 47, 57, 121))
print("frame 0 vs the world's full door:", sum(1 for a, b in zip(d0.getdata(), full.getdata()) if a != b))
row([o.crop((10, 40, 100, 124)) for o in out], B + "fullburst.png", k=2, bg=(232, 220, 203, 255))
