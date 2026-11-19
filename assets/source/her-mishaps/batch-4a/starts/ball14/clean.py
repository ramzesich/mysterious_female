"""14a's and 14b's topples cleaned (2026-11-19): the generator's specks out (her biggest piece, and pieces of 4 px or
more within 2 px of it); from frame 1 on, her lowest pixel set on the floor row (120: the generator floated some frames
2 to 3 px, or sank one 1 px); the last frame is the end picture it was pinned to, exactly (her stand turned flat), so
the lying beat after it hands over to the pixel. a-st: frame 1 (the same as 0 and 2) left out.
Then the lying beat (`<a|b>-lie/`): the flat picture with the butterflies of her dazed lie
(`assets/source/her/dazed-lie/1-5`) over her head, at the height over the floor they have there (14b's head ahead as
there; 14a's behind, their layer mirrored about her head)."""
import os
from PIL import Image
FLOOR = 120
H = "C:/Users/ramze/Development/mysterious_female/assets/source/her/dazed-lie/"


def pieces(im):
    a = im.load(); w, h = im.size; seen = set(); out = []
    for y in range(h):
        for x in range(w):
            if a[x, y][3] and (x, y) not in seen:
                st = [(x, y)]; seen.add((x, y)); comp = []
                while st:
                    p = st.pop(); comp.append(p)
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            q = (p[0] + dx, p[1] + dy)
                            if 0 <= q[0] < w and 0 <= q[1] < h and q not in seen and a[q][3]:
                                seen.add(q); st.append(q)
                out.append(comp)
    return sorted(out, key=len, reverse=True)


def clean(im):
    ps = pieces(im); main = set(ps[0]); keep = set(main)
    for p in ps[1:]:
        if len(p) >= 4 and any((x + dx, y + dy) in main for x, y in p for dx in (-2, 0, 2) for dy in (-2, 0, 2)):
            keep |= set(p)
    out = Image.new("RGBA", im.size); a, o = im.load(), out.load()
    for p in keep: o[p] = a[p]
    return out, sum(len(p) for p in ps) - len(keep)


def floored(im):
    b = im.getbbox(); out = Image.new("RGBA", im.size); out.alpha_composite(im, (0, FLOOR + 1 - b[3])); return out, FLOOR + 1 - b[3]


for k in "ab":
    for tag in ("st", "r1", "r3", "r5", "r7"):
        # (14a: its second round, pinned to her redrawn lying on her back, `a-end2-*`; the user, 2026-11-19: her stand
        # turned flat "appears to be at an angle", its head lifted. Not settled: it lies on the floor as drawn.)
        # (14b the same, face down, `b-end2-*`: the user chose it over its stand turned flat and set straight.)
        src, dst = f"raw/{k}-{tag}-e2", f"clean/{k}-{tag}"
        endp = f"{k}-end2-{tag}.png"
        os.makedirs(dst, exist_ok=True)
        idx = list(range(9))
        notes = []
        for j, i in enumerate(idx):
            im = Image.open(f"{src}/{i}.png").convert("RGBA")
            if i == 8:
                im = Image.open(endp).convert("RGBA"); notes.append("end")
            elif i > 0:
                im, lost = clean(im); im, dy = floored(im)
                if lost or dy: notes.append(f"{i}:-{lost}px,{dy:+d}")
            im.save(f"{dst}/{j}.png")
        print(k, tag, " ".join(notes))

# The lying beat with the butterflies.
lie = [Image.open(f"{H}{i}.png").convert("RGBA") for i in range(1, 6)]
for k in "ab":
    end = Image.open(f"{k}-end2-st.png").convert("RGBA")
    eb = end.getbbox(); head = eb[0] + 6 if k == "a" else eb[2] - 8
    os.makedirs(f"clean/{k}-lie", exist_ok=True)
    for j, f in enumerate(lie):
        ps = pieces(f); body = Image.new("RGBA", f.size); bf = Image.new("RGBA", f.size)
        a, o, q = f.load(), body.load(), bf.load()
        for p in ps[0]: o[p] = a[p]
        for pc in ps[1:]:
            for p in pc: q[p] = a[p]
        bb = body.getbbox(); fhead, ffloor = bb[2] - 8, bb[3] - 1
        out = end.copy()
        bfb = bf.getbbox()
        if k == "a":
            bf = bf.transpose(Image.FLIP_LEFT_RIGHT); fhead = f.width - 1 - fhead
        out.alpha_composite(bf, (head - fhead, FLOOR - ffloor))
        out.save(f"clean/{k}-lie/{j}.png")
    print(k, "lie", head)

# 14b: her red scarf showing under her face on the floor in the landing frames read as blood: those pixels (crimson,
# in the lowest 7 rows of a frame where she is down) take the colour of the nearest of her pixels that is not red.
def red(c): return c[3] and c[1] < 80 and c[0] - c[1] > 50 and c[2] > c[1]    # (crimson: her skin is never)
for tag in ("st", "r1", "r3", "r5", "r7"):
    d = f"clean/b-{tag}"
    for i in range(1, len(os.listdir(d))):
        im = Image.open(f"{d}/{i}.png").convert("RGBA"); px = im.load(); fixed = 0
        if im.getbbox()[3] - im.getbbox()[1] > 24:
            continue        # (only where she is down: standing, the lowest rows are her shoes)
        for _ in range(4):
            for y in range(FLOOR - 6, FLOOR + 1):
                for x in range(128):
                    if red(px[x, y]):
                        near = [px[x + dx, y + dy] for r in (1, 2) for dx in (-r, 0, r) for dy in (-r, 0, r)
                                if 0 <= x + dx < 128 and 0 <= y + dy < 128 and px[x + dx, y + dy][3] and not red(px[x + dx, y + dy])]
                        if near:
                            px[x, y] = near[0]; fixed += 1
        if fixed:
            im.save(f"{d}/{i}.png"); print("b", tag, i, "scarf px", fixed)
