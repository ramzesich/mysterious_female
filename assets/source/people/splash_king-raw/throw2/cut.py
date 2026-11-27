"""Splash Academy's pillow siege: the king's and the knight's throw (PixMiniMax from their stand with the pillow lying at
their toes to their stand: de5aee3d, caf6d4f4, 1 generation each), cut into `../../<name>/throw/`.

Before the hands reach it the pillow is the start picture's to the px (the world's lies there); from the first frame it
is clear of the hands (`RELEASE`) every piece of the picture but the figure's is taken out (the game's pillow flies on
from where the clip's was). Prints, per kid: the pillow's box in the start picture, the frame the hands take it
(`grab`: the first in which it differs from the start), and the pillow's middle in the release frame.
    python assets/source/people/splash_king-raw/throw2/cut.py
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
PEOPLE = HERE.parent.parent


def components(im):
    px = im.load(); w, h = im.size; seen = set(); out = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] and (x, y) not in seen:
                st = [(x, y)]; seen.add((x, y)); comp = []
                while st:
                    a, b = st.pop(); comp.append((a, b))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            q = (a + dx, b + dy)
                            if 0 <= q[0] < w and 0 <= q[1] < h and q not in seen and px[q][3]:
                                seen.add(q); st.append(q)
                out.append(comp)
    return sorted(out, key=len, reverse=True)


# The frame each one's hands take the pillow (seen: before it the generator slid its own copy against the toes).
GRAB = {"splash_king": 3, "splash_knight": 5}

for name in ("splash_king", "splash_knight"):
    raw = PEOPLE / f"{name}-raw/throw2"
    frames = [Image.open(raw / f"raw/{i}.png").convert("RGBA") for i in range(17)]
    start = Image.open(raw / "start.png").convert("RGBA")
    stand = Image.open(raw / "end.png").convert("RGBA")
    # The pillow in the start picture: what it has that the stand has not.
    sp, ep = start.load(), stand.load()
    pil = [(x, y) for y in range(88) for x in range(88) if sp[x, y][3] and not ep[x, y][3]]
    box = (min(p[0] for p in pil), min(p[1] for p in pil), max(p[0] for p in pil) + 1, max(p[1] for p in pil) + 1)
    out = PEOPLE / name / "throw"
    out.mkdir(exist_ok=True)
    grab = release = None
    mid = None
    pillow = start.crop(box)
    for i, f in enumerate(frames):
        f = f.copy()
        fp = f.load()
        comps = components(f)
        loose = [c for c in comps[1:] if len(c) > 20]
        if i == GRAB[name]:
            grab = i
        if grab is None:
            # Lying: the world's pillow, to the px (the generator's copy taken out: all in its box and to its right
            # under its top, where no part of the figure is before the hands come down to it).
            for y in range(box[1], 88):
                for x in range(box[0], 88):
                    fp[x, y] = (0, 0, 0, 0)
            for c in comps[1:]:
                for q in c:
                    fp[q] = (0, 0, 0, 0)
            f.alpha_composite(pillow, box[:2])
        elif release is None and loose:
            release = i
            c = loose[0]
            mid = (sum(q[0] for q in c) / len(c), sum(q[1] for q in c) / len(c))
        if release is not None:
            for c in comps[1:]:
                for q in c:
                    fp[q] = (0, 0, 0, 0)
        if i == 16:
            f = stand.copy()
        f.save(out / f"{i}.png")
    print(name, "pillow box", box, "grab", grab, "release", release, "middle", mid)
