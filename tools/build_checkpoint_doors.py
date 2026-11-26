"""The checkpoints' own doors (plan-the-rest §7e, the user, 2026-11-26: "I like all of them, let's use all"): four
generated leaves (`assets/source/ship/checkpoint-doors/tries/`, its README has the jobs), each set into a doorcase on the
crew door's frame (29 x 74: the dark outline, the leaf where the crew door's leaf is, a flat band of dark wood round it
drawn by rule), and its lit twin made from it by the crew door's ajar geometry (`door-crew-ajar`: 29 x 79, the leaf swung
toward us on its right-hand hinges, 18 px wide, its free edge 2 px over the frame's top and 3 under its foot, the warm
light in the gap). Writes `assets/source/ship/<name>/frame_0.png` for both; `tools/build_ship_art.py` takes them in their
own colours (`OWN`) and records the ajar ones' foot.

    python tools/build_checkpoint_doors.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TRIES = ROOT / "assets/source/ship/checkpoint-doors/tries"
SHIP = ROOT / "assets/source/ship"

# name: the try it is made from (B: padded theatre doors; C: dark wood service doors)
DOORS = {"door-theatre-red": "B1", "door-theatre-navy": "B2", "door-walnut": "C1", "door-mahogany": "C2"}
FOOT = 3                                         # the ajar twin's px under the floor line (as `door-crew-ajar`)

OUTL = (46, 34, 47)
FACE, LIT, SHADE = (70, 44, 22), (101, 63, 28), (54, 34, 15)      # the doorcase's dark wood
LIGHT, WARM = (251, 255, 134), (251, 185, 84)                   # the room's light in the gap, as the crew door's


def _grey(p):
    r, g, b, a = (int(v) for v in p)
    return a and abs(r - 147) < 14 and abs(g - 164) < 14 and abs(b - 172) < 14


def leaf(name):
    """The try's leaf, its generated grey rim taken off, set in a 21 x 70 box (the crew door's leaf, outline and all,
    with the frame's bottom row)."""
    im = Image.open(TRIES / f"{name}.png").convert("RGBA")
    a = np.array(im.crop(im.getbbox()))
    while all(_grey(p) for p in a[0] if p[3]): a = a[1:]
    while all(_grey(p) for p in a[:, 0] if p[3]): a = a[:, 1:]
    while all(_grey(p) for p in a[:, -1] if p[3]): a = a[:, :-1]
    while all(_grey(p) for p in a[-1] if p[3]): a = a[:-1]
    lf = Image.fromarray(a)
    w, h = lf.size
    box = Image.new("RGBA", (21, 70), OUTL + (255,))
    box.alpha_composite(lf.crop((0, max(0, h - 69), min(w, 21), h)), ((21 - min(w, 21)) // 2, 69 - min(h, 69)))
    return box


def case(height, top):
    """The doorcase, 29 wide, its top outline at row `top`, its bottom outline at row `top + 73`."""
    c = Image.new("RGBA", (29, height), (0, 0, 0, 0))
    px = c.load()
    for y in range(top, top + 74):
        for x in range(29):
            edge = y in (top, top + 73) or x in (0, 28)
            px[x, y] = (OUTL if edge else LIT if x == 1 or y == top + 1 else SHADE if x == 27 else FACE) + (255,)
    return c


def shut(name):
    c = case(74, 0)
    c.paste(leaf(DOORS[name]), (4, 4))
    return c


def ajar(name):
    """The crew door's ajar geometry: the frame 2 rows lower on a canvas 79 tall; the opening (cols 3 to 24) the
    room's light with the frame's inner edge, the leaf from col 6 to 23, its top from row 0 at the free edge to row 3
    at the hinge, its foot from row 78 to 75; horizontal lines on it slant by the same rule (nearest row)."""
    c = case(79, 2)
    px = c.load()
    for y in range(5, 75):                                   # the opening, behind the leaf
        for x in range(3, 25):
            px[x, y] = OUTL + (255,)
        px[3, y] = LIGHT + (255,)
        px[5, y] = (WARM if y >= 68 else LIGHT) + (255,)
    for x in (4, 5):
        px[x, 5] = LIGHT + (255,)
    src = leaf(DOORS[name])
    sp = src.load()
    for j in range(18):                                      # col 6 + j; j 0 at the free edge
        k = j / 17
        top, bot = round(3 * k), round(78 - 3 * k)
        sx = round(j * 20 / 17)
        for y in range(top, bot + 1):
            sy = min(69, round((y - top) * 69 / (bot - top)))
            px[6 + j, y] = sp[sx, sy]
    for y in range(75, 79):                                  # under the floor: only the leaf
        for x in list(range(0, 6)) + list(range(24, 29)):
            if y > 75:
                px[x, y] = (0, 0, 0, 0)
    if DOORS[name] in PORTHOLES:
        porthole(px, sp, *PORTHOLES[DOORS[name]])
    return c


# A theatre door's round window (the user, 2026-11-26: warped with the leaf it was "distorted"): its middle and radii
# in the leaf's box, outline and all.
PORTHOLES = {"B1": (10, 15.5, 6.5, 6.0), "B2": (9.5, 15, 5.4, 4.9)}


def _warp(j, y):
    """The leaf's (x, y) that the ajar's col 6 + j, row y shows, or None off the leaf."""
    k = j / 17
    top, bot = round(3 * k), round(78 - 3 * k)
    if not top <= y <= bot:
        return None
    return round(j * 20 / 17), min(69, round((y - top) * 69 / (bot - top)))


def porthole(px, sp, cx, cy, rx, ry):
    """The window drawn whole: its warped pixels filled with the leaf beside them, then its own pixels laid over where
    the leaf's middle carries it, neither narrowed nor stretched (narrowed by its middle columns, at 13 px its rim came
    out lumpy)."""
    inside = lambda x, y, m=0.5: ((x - cx) / (rx + m)) ** 2 + ((y - cy) / (ry + m)) ** 2 <= 1
    hit = {}
    for j in range(18):
        for y in range(79):
            s = _warp(j, y)
            if s and inside(*s, 1.2):
                hit.setdefault(y, []).append(6 + j)
    for y, xs in hit.items():                                # the warped window, filled with the leaf beside it
        x0, x1 = min(xs), max(xs)
        for x in xs:
            px[x, y] = px[x0 - 1, y] if x - x0 < x1 - x else px[x1 + 1, y]
    x0, x1 = int(cx - rx - 0.5), int(cx + rx + 0.5)
    y0, y1 = int(cy - ry - 0.5), int(cy + ry + 0.5)
    jc = cx * 17 / 20                                        # where its middle lands
    k = jc / 17
    top, bot = 3 * k, 78 - 3 * k
    dy = round(top + cy * (bot - top) / 69 - cy)
    # (Narrowed into an oval by the swing, its height kept (the user, 2026-11-26): columns either side of its middle
    # left out, the same number each side, so its middle stays where it was.)
    mid = (x0 + x1) / 2
    drop = {round(mid - 1), round(mid + 1)} if (x1 - x0) % 2 == 0 else {int(mid), int(mid) + 1}
    keep = [x for x in range(x0, x1 + 1) if x not in drop]
    left = round(6 + jc - (len(keep) - 1) / 2)
    for i, sx in enumerate(keep):
        for sy in range(y0, y1 + 1):
            if inside(sx, sy):
                px[left + i, sy + dy] = sp[sx, sy]


def main():
    for name in DOORS:
        for n, img in ((name, shut(name)), (f"{name}-ajar", ajar(name))):
            d = SHIP / n
            d.mkdir(parents=True, exist_ok=True)
            img.save(d / "frame_0.png")
            print("wrote", (d / "frame_0.png").relative_to(ROOT), img.size)


if __name__ == "__main__":
    main()
