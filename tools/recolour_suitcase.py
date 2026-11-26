"""The second runaway suitcase's own colour (plan-the-rest §7f, 3; the user, 2026-11-26: "Make two suitcases different
colors", red of four tries): deck 4's slate suitcase turned burgundy, its world picture and every frame of her gags with it
(6a to 6c: sitting onto it, the ride, the tip, dazed), so that the world's case and her gag's hand over in one colour.

What is turned is the case's own mid tones only: the colours of its world picture brighter than its outline (not its tag's
oranges, not the handle's pale greys, so the handle is grey on both), found in each frame within a few steps of them, and
of those only the pieces of a dozen px or more (the shell's two faces either side of its stripe, its band): the specks of
the same tones in her hair are smaller. Each is turned to the red's hue by its own offset from the slate's, half as far, its
saturation and value raised a little; the build puts it on the palette as the rest.

    python tools/recolour_suitcase.py     # then tools/build_things.py, tools/build_sprites.py, tools/build_heads.py

Writes `assets/source/things/suitcase-rolling-red.png` and `assets/source/her-mishaps/redcase-<clip>/<n>.png`.
"""
import colorsys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
THINGS = ROOT / "assets/source/things"
GAGS = ROOT / "assets/source/her-mishaps"
CLIPS = ("sit", "ride", "tip", "dazed")

# The case's tag (oranges) and the handle's pale greys, never turned.
KEEP = {(236, 137, 76), (236, 148, 90), (247, 135, 66), (129, 64, 41), (159, 80, 43),
        (125, 112, 139), (149, 133, 159), (159, 146, 168)}
TOL, PIECE = 12, 12
# The red (the user's choice of red, teal, mustard, green): its hue, saturation and value factors.
HUE, SAT, VAL = 0.99, 1.6, 1.05


def case_colours():
    case = Image.open(THINGS / "suitcase-rolling.png").convert("RGBA")
    return {p[:3] for p in case.getdata() if p[3] and sum(p[:3]) > 200 and p[:3] not in KEEP}


def mask(im, cols):
    px = im.load()
    w, h = im.size
    near = lambda p: any(abs(p[0] - c[0]) + abs(p[1] - c[1]) + abs(p[2] - c[2]) <= TOL for c in cols)
    m = {(x, y) for y in range(h) for x in range(w) if px[x, y][3] and near(px[x, y])}
    seen, keep = set(), set()
    for s in m:
        if s in seen:
            continue
        comp, st = [], [s]
        seen.add(s)
        while st:
            x, y = st.pop()
            comp.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q in m and q not in seen:
                        seen.add(q)
                        st.append(q)
        if len(comp) >= PIECE:
            keep.update(comp)
    return keep


def recolour(im, cols):
    im = im.convert("RGBA").copy()
    px = im.load()
    for x, y in mask(im, cols):
        r, g, b, a = px[x, y]
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        r2, g2, b2 = colorsys.hsv_to_rgb((HUE + (h - 0.66) * 0.5) % 1, min(1, s * SAT), min(1, v * VAL))
        px[x, y] = (round(r2 * 255), round(g2 * 255), round(b2 * 255), a)
    return im


def main():
    cols = case_colours()
    recolour(Image.open(THINGS / "suitcase-rolling.png"), cols).save(THINGS / "suitcase-rolling-red.png")
    print("wrote", (THINGS / "suitcase-rolling-red.png").relative_to(ROOT))
    for clip in CLIPS:
        src, out = GAGS / f"suitcase-{clip}", GAGS / f"redcase-{clip}"
        out.mkdir(exist_ok=True)
        frames = sorted((f for f in src.glob("*.png") if f.stem.isdigit()), key=lambda f: int(f.stem))
        for f in frames:
            recolour(Image.open(f), cols).save(out / f.name)
        print("wrote", out.relative_to(ROOT), len(frames))


if __name__ == "__main__":
    main()
