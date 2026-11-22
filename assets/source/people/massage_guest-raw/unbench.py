"""Her sitting down facing us (skeleton-v3, `sit`): the generator drew a grey bench under her in frames 1 to 7; taken
out by its own colours, exactly. The bench's colours are those of its ends, which stick out past her on both sides (columns
under 33 or over 62); hers are her standing frame's (frame 0, no bench). A px in a colour of the bench's alone goes; one in
a colour both have goes only with nothing of hers beside it. (A first try took greys by kind, and took hers with them: her
legs', her turban's, her outline's: the user, 2026-11-22.) The game's own sauna bench is behind her.
sit/south/<i>.png to sit-clean/<i>.png."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sit", "south")
OUT = os.path.join(HERE, "sit-clean")
os.makedirs(OUT, exist_ok=True)

frames = [np.array(Image.open(os.path.join(SRC, f"{i}.png")).convert("RGBA")) for i in range(8)]
hers = {tuple(p[:3]) for p in frames[0].reshape(-1, 4) if p[3]}
bench = set()
for a in frames[1:]:
    ys, xs = np.where(a[..., 3] > 0)
    bench |= {tuple(a[y, x, :3]) for y, x in zip(ys, xs) if x < 33 or x > 62}
only_bench, shared = bench - hers, bench & hers
print("the bench's own colours:", len(only_bench), "shared:", len(shared))

for i, a in enumerate(frames):
    out = a.copy()
    h, w = a.shape[:2]
    col = [[tuple(a[y, x, :3]) if a[y, x, 3] else None for x in range(w)] for y in range(h)]
    gone = 0
    for y in range(h):
        for x in range(w):
            c = col[y][x]
            if c is None:
                continue
            if c in only_bench:
                out[y, x] = 0
                gone += 1
            elif c in shared:
                near = [col[v][u] for v in range(max(0, y - 1), min(h, y + 2)) for u in range(max(0, x - 1), min(w, x + 2))
                        if (v, u) != (y, x)]
                if not any(n is not None and n in hers and n not in bench for n in near):
                    out[y, x] = 0
                    gone += 1
    Image.fromarray(out).save(os.path.join(OUT, f"{i}.png"))
    print(i, gone, "px of bench")
