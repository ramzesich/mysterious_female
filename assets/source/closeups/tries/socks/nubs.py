"""The grip socks' close-up: S3 (try3.png) with white rubber nubs under the whole sole of both socks, by rule (the user,
2026-11-25: "Make the barbs white on the close up, make less of them (more distance between each other), and cover the
entire sole with them in this way on both socks"). python assets/source/closeups/tries/socks/nubs.py -> socks-nubs.png

A sock here is seen from the side, standing: its sole is its lower outline from toe to heel. A nub is a round
stud about 5 px across, lit from the upper left, standing square out of that outline every STEP px of its length."""
from collections import deque
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
STEP = 9
RADIUS = 2.4
WHITE, SHADE, RIM = (255, 255, 255, 255), (213, 220, 230, 255), (155, 171, 190, 255)


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
            # A nub: a round stud of rubber standing out of the sole, square to it (down under the toes, down and aft
            # on the slope to the heel): a disc of RADIUS px, half sunk into the outline, lit from the upper left.
            j0, j1 = max(0, i - 3), min(len(xs) - 1, i + 3)
            tx, ty = xs[j1] - xs[j0], low[xs[j1]] - low[xs[j0]]
            n = (tx * tx + ty * ty) ** 0.5
            nx, ny = -ty / n, tx / n                      # the outline's normal, pointing out of the sock (downward)
            cx, cy = x + 0.5 + nx * (RADIUS - 0.6), low[x] + 0.5 + ny * (RADIUS - 0.6)
            for yy in range(int(cy - RADIUS - 1), int(cy + RADIUS + 2)):
                for xx in range(int(cx - RADIUS - 1), int(cx + RADIUS + 2)):
                    if not (0 <= xx < w and 0 <= yy < h) or px[xx, yy][3] >= 128: continue
                    dx, dy2 = xx + 0.5 - cx, yy + 0.5 - cy
                    d = (dx * dx + dy2 * dy2) ** 0.5
                    if d > RADIUS: continue
                    lit = (-dx - dy2) / (RADIUS * 1.42)        # 1 at the upper left, -1 at the lower right
                    o[xx, yy] = RIM if d > RADIUS - 0.75 and lit < -0.15 else SHADE if lit < 0.1 else WHITE
    out.save(HERE / "socks-nubs.png")
    print("wrote", HERE / "socks-nubs.png")


if __name__ == "__main__":
    main()
