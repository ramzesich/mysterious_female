"""The grip socks' close-up: S3 (try3.png) with white rubber nubs under the whole sole of both socks, by rule (the user,
2026-11-25: "Make the barbs white on the close up, make less of them (more distance between each other), and cover the
entire sole with them in this way on both socks"). python assets/source/closeups/tries/socks/nubs.py -> socks-nubs.png

A sock here is seen from the side, standing: its sole is its lower outline from toe to heel. A nub is 2 x 2 px of white
with a grey foot, hung under that outline every STEP px of its length."""
from collections import deque
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
STEP = 7
WHITE, SHADE = (255, 255, 255, 255), (199, 207, 221, 255)


def main():
    im = Image.open(HERE / "try3.png").convert("RGBA")
    px = im.load(); w, h = im.size
    # The two socks: the two largest pieces.
    seen, comps = set(), []
    for y in range(h):
        for x in range(w):
            if (x, y) in seen or px[x, y][3] < 128: continue
            comp, q = [], deque([(x, y)]); seen.add((x, y))
            while q:
                a, b = q.popleft(); comp.append((a, b))
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    c = (a + da, b + db)
                    if 0 <= c[0] < w and 0 <= c[1] < h and c not in seen and px[c][3] >= 128:
                        seen.add(c); q.append(c)
            comps.append(comp)
    comps.sort(key=len, reverse=True)
    out = im.copy(); o = out.load()
    for comp in comps[:2]:
        low = {}
        for x, y in comp: low[x] = max(low.get(x, -1), y)
        xs = sorted(low)
        # (The sole runs from the toe's tip to the heel's back: every column of the sock. The nubs are set along that
        # outline by its own length, so that they stand as far apart on its slope up to the heel as under the toes.)
        run = STEP / 2
        for i in range(3, len(xs) - 3):
            x = xs[i]
            dy = low[x] - low[xs[i - 1]]
            run += (1 + dy * dy) ** 0.5
            if run < STEP: continue
            run = 0
            y = low[x] + 1
            for dx in (0, 1):
                for dy2 in (0, 1):
                    xx, yy = x + dx, max(y, low.get(x + dx, y - 1) + 1) + dy2
                    if 0 <= xx < w and 0 <= yy < h and o[xx, yy][3] < 128:
                        o[xx, yy] = WHITE if dy2 == 0 else SHADE
    out.save(HERE / "socks-nubs.png")
    print("wrote", HERE / "socks-nubs.png")


if __name__ == "__main__":
    main()
