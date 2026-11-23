"""Her cone in her fist, frame by frame (the user, 2026-11-23: she sits down at his table with the cone she carried and
eats it): the game's own cone (`load-cone.png`, the very picture `src/world/carry.js` draws while she carries it) set
upright with its tip a few px under her fist, then her fist's own pixels drawn again over it (held, not stuck on), and
her head's (the cone is in front of her body, behind her face, as she licks it).

(The game's own carried cone, `load-cone.png`, was in her fist at first: too big beside his.)

Her fist: her near hand's skin between her chin and her lap (rows from 13 under the top of her face to 59, in front of
her back), its front 2 px in. Out: `cone/sit/` (the sit-down, `clean/` with the cone) and `cone/lick/` (`lick-raw/`)."""
import os

import numpy as np
from scipy import ndimage
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
# Her husband's own cone (the user, 2026-11-23: "Her ice cream is too big, let it match his"), its pixels cut from his
# still (`assets/source/people/husband-raw/eat-cone/still-s1.png`): the swirl and its outline, the rim and the top of the
# waffle between his fingers; his fingers left out. Placed by her fist as it sits in his (his fist's middle `HIS_FIST`).
HIS = np.array(Image.open(os.path.join(HERE, "..", "..", "people", "husband-raw", "eat-cone", "still-s1.png")).convert("RGBA"))
CONE_PX = [(y, x) for y in range(36, 42) for x in range(51, 57) if HIS[y, x, 3]] +           [(42, 51), (42, 52), (42, 53), (42, 56), (43, 52), (43, 55), (44, 53), (44, 54)]
HIS_FIST = (53, 46)


def skin(a):
    r, g, b, al = [a[..., i].astype(int) for i in range(4)]
    return (al > 0) & (r >= 200) & (g >= 130) & (g <= 220) & (b >= 110) & (b <= 200) & (r - b >= 35)


def fist(a):
    m = skin(a)
    top = np.where(m.any(axis=1))[0].min()
    band = np.zeros_like(m)
    band[top + 13:60, 42:] = m[top + 13:60, 42:]
    ys, xs = np.where(band)
    front = xs.max()
    near = xs >= front - 3
    return front - 2, int(round(ys[near].mean())), band


def bake(a):
    fx, fy, hand = fist(a)
    out = a.copy()
    for y, x in CONE_PX:
        out[y - HIS_FIST[1] + fy, x - HIS_FIST[0] + fx] = HIS[y, x]
    # Her fingers over it: her hand's own pixels within 3 px of the fist's middle.
    for y in range(fy - 3, fy + 4):
        for x in range(fx - 3, fx + 4):
            if hand[y, x] or (a[y, x, 3] and a[y, x, :3].max() < 60 and hand[max(0, y - 1):y + 2, max(0, x - 1):x + 2].any()):
                out[y, x] = a[y, x]
    # Her head in front of it (the user saw the swirl over her face as she dipped to lick): her own pixels down to
    # her chin (the bottom of the topmost piece of her skin) drawn again over the cone.
    lab, n = ndimage.label(skin(a), structure=np.ones((3, 3)))
    tops = [(np.where(lab == k)[0].min(), k) for k in range(1, n + 1)]
    chin = np.where(lab == min(tops)[1])[0].max()
    head = (np.arange(a.shape[0])[:, None] <= chin) & (a[..., 3] > 0)
    out[head] = a[head]
    return out, (fx, fy)


for src, dst in (("faced", "sit3"),):
    os.makedirs(os.path.join(HERE, "cone", dst), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(HERE, src)), key=lambda s: int(s.split(".")[0])):
        a = np.array(Image.open(os.path.join(HERE, src, f)).convert("RGBA"))
        out, at = bake(a)
        Image.fromarray(out).save(os.path.join(HERE, "cone", dst, f))
        print(dst, f, "fist", at)
