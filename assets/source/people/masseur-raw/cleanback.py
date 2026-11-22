"""His back in the massage's back view, cleaned after the hands were painted out (unhands.py): in every frame the middle
of each shirt row one even white, holes at his sides filled, the hem's broken row mended; sleeves and side shading as
drawn. In place, massage-back/<i>.png."""
import numpy as np
from PIL import Image
R = r"C:\Users\ramze\Development\mysterious_female\assets\source\people\masseur-raw\massage-back"
WHITE = (0xee, 0xf8, 0xfb, 255)
for i in range(7):
    p = R + "\\" + f"{i}.png"
    a = np.array(Image.open(p).convert("RGBA")).astype(int)
    op = a[..., 3] > 0
    light = op & (a[..., :3].min(2) > 140)
    collar = np.where((light & (a[..., :3].min(2) > 200)).any(1))[0][0]
    rows = [y for y in range(collar + 3, a.shape[0]) if light[y].any()]
    last = rows[-1]
    # (the trousers start where the light rows end; their own light greys are under 140 at the waist, but the shoes are
    # light: stop at the first row after the shirt with no light pixel)
    shirt = []
    for y in range(collar + 3, a.shape[0]):
        if not light[y].any():
            break
        shirt.append(y)
    for y in shirt:
        xs = np.where(light[y])[0]; L, R_ = xs[0], xs[-1]
        # (over a hole of 1 or 2 px to his outline, never out into the air)
        for k in (1, 2):
            if L - k - 1 >= 0 and not op[y, L - k:L].any() and op[y, L - k - 1]:
                L -= k; break
        for k in (1, 2):
            if R_ + k + 1 < a.shape[1] and not op[y, R_ + 1:R_ + k + 1].any() and op[y, R_ + k + 1]:
                R_ += k; break
        span = R_ - L + 1
        ragged = y > (shirt[0] + shirt[-1]) / 2 and light[y, L:R_ + 1].sum() < 0.6 * span   # (the hem only)
        for x in range(L, R_ + 1):
            if not op[y, x]:
                a[y, x] = WHITE                       # a hole inside his outline
            elif L + 3 <= x <= R_ - 3 and not ragged:
                a[y, x] = WHITE                       # the middle of the back
        if ragged:
            # the hem's broken row: its light pixels dark, as the hem line under them
            for x in range(L, R_ + 1):
                if light[y, x]:
                    a[y, x] = (1, 2, 5, 255)
    # Specks apart from him (a few px off his trousers in frame 2): gone.
    import cv2
    m = (a[..., 3] > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    for k in range(1, n):
        if k != big:
            a[lab == k] = 0
    Image.fromarray(a.astype(np.uint8)).save(p)
    print(i, "shirt rows", shirt[0], shirt[-1])
# (Then by hand: frame 2's right trouser leg, its outline broken at rows 63-66 and 70: (56, 63-65) and (50, 70) dark,
# its 1 px nubs at (57, 64) and (57, 66) taken off.)
