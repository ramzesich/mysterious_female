"""The gym's two balls, rolling (plan-the-rest §7f, 8; the user, 2026-11-26: "both blue and purple"; "The balls have
lines, so they should turn. The light has to stay still").

The ball is try 2 of `assets/source/things/tries/gym-ball/` (a map object, 24 px across), its shading kept as it is in
every frame: the light never turns. A ball rolling in a side view turns in the picture's own plane, so its lines are
drawn by rule on a sphere at each angle: the moulded seam (a great circle) and a rib either side, round an axis tilted
toward us, each line the edge of a band of latitude (one px wide, joined), in the ball's own colour a few steps darker
at that pixel; the outline is left as it is. FRAMES pictures over a whole turn.
The blue one is the same picture in try 1's blue (the user chose both colours).

Writes `assets/source/things/gym-ball-<colour>-<nn>.png` (the things build takes them as they are, `OWN_COLOURS`).
    python tools/build_gym_ball.py [--preview DIR]
"""
import colorsys
import math
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TRIES = ROOT / "assets/source/things/tries/gym-ball"
OUT = ROOT / "assets/source/things"
FRAMES = 32                    # pictures over a whole turn (the axis leans toward us: half a turn bows the rings the other way)
TILT = math.radians(28)        # the lines' axis leans toward us by this much
LINES = (0.0, -0.6, 0.6)       # latitudes of the seam and the two ribs, radians (parallels: they never cross)
DARKER = 0.72                  # a line's lightness, of the ball's at that pixel
SHINE = 0.8                   # the highlight (lighter than this) is on top: no line through it


def ball():
    im = Image.open(TRIES / "2.png").convert("RGBA")
    return im.crop(im.getbbox())


def ramp(img):
    """The ball's own colours, darkest first (a line takes one of them)."""
    cols = {p[:3] for p in img.get_flattened_data() if p[3]}
    return sorted(cols, key=lambda c: colorsys.rgb_to_hls(*(v / 255 for v in c))[1])


def nearest(cols, c):
    return min(cols, key=lambda k: sum((a - b) ** 2 for a, b in zip(k, c)))


def lat_at(x, y, cx, cy, r, theta):
    """Latitude of the sphere's point under pixel (x, y) (its middle), the axis turned by theta in the picture's plane."""
    dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
    d2 = dx * dx + dy * dy
    if d2 >= 1:
        dx, dy, d2 = dx / math.sqrt(d2) * 0.999, dy / math.sqrt(d2) * 0.999, 0.998
    dz = math.sqrt(1 - d2)                       # toward us
    # The axis: up the picture, leaning toward us, then turned by theta (clockwise on the screen, y down).
    ax, ay, az = 0.0, -math.cos(TILT), math.sin(TILT)
    c, s = math.cos(theta), math.sin(theta)
    ax, ay = ax * c - ay * s, ax * s + ay * c
    return math.asin(max(-1, min(1, dx * ax + dy * ay + dz * az)))


def frame(base, theta):
    w, h = base.size
    cx, cy, r = w / 2, h / 2, w / 2
    px = base.load()
    inside = lambda x, y: 0 <= x < w and 0 <= y < h and px[x, y][3] > 0
    rim = {(x, y) for y in range(h) for x in range(w) if inside(x, y)
           and not all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    lat = {(x, y): lat_at(x, y, cx, cy, r, theta) for y in range(h) for x in range(w) if inside(x, y)}
    cols = ramp(base)
    out = base.copy()
    o = out.load()
    for (x, y), a in lat.items():
        r0, g0, b0, al = px[x, y]
        if (x, y) in rim or colorsys.rgb_to_hls(r0 / 255, g0 / 255, b0 / 255)[1] > SHINE:
            continue
        for L in LINES:
            # The band's edge: this pixel over the line, a neighbour under it (one px, joined).
            if a > L and any(lat.get((x + dx, y + dy), 9) <= L for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                hh, ll, ss = colorsys.rgb_to_hls(r0 / 255, g0 / 255, b0 / 255)
                want = tuple(round(v * 255) for v in colorsys.hls_to_rgb(hh, ll * DARKER, ss))
                o[x, y] = nearest(cols, want) + (al,)
                break
    return out


def blue(img):
    """Try 1's blue on the purple's shading: its hue, and the purple's lightness and saturation bent to try 1's means
    (a power of each, so the shading stays as smooth as it was)."""
    hls = lambda c: colorsys.rgb_to_hls(*(v / 255 for v in c[:3]))
    one = Image.open(TRIES / "1.png").convert("RGBA")
    theirs = [hls(p) for p in one.get_flattened_data() if p[3]]
    ours = [hls(p) for p in img.get_flattened_data() if p[3]]
    mean = lambda xs: sum(xs) / len(xs)
    hue = math.atan2(mean([math.sin(2 * math.pi * h) for h, _, _ in theirs]), mean([math.cos(2 * math.pi * h) for h, _, _ in theirs])) / (2 * math.pi) % 1
    gl = math.log(mean([l for _, l, _ in theirs])) / math.log(mean([l for _, l, _ in ours]))
    gs = math.log(mean([s for _, _, s in theirs])) / math.log(mean([s for _, _, s in ours]))
    def to(p):
        h, l, s_ = hls(p)
        return tuple(round(v * 255) for v in colorsys.hls_to_rgb(hue, l ** gl, s_ ** gs)) + (p[3],)
    out = img.copy()
    out.putdata([to(p) if p[3] else p for p in img.get_flattened_data()])
    return out


def build():
    base = ball()
    made = {}
    for colour, picture in (("purple", base), ("blue", blue(base))):
        made[colour] = [frame(picture, 2 * math.pi * i / FRAMES) for i in range(FRAMES)]
        for i, im in enumerate(made[colour]):
            im.save(OUT / f"gym-ball-{colour}-{i:02d}.png")
    print("wrote", ", ".join(f"gym-ball-{c}-00..{FRAMES - 1:02d}" for c in made), "each", base.size)
    return made


if __name__ == "__main__":
    made = build()
    if "--preview" in sys.argv:
        d = Path(sys.argv[sys.argv.index("--preview") + 1])
        d.mkdir(parents=True, exist_ok=True)
        w, h = made["purple"][0].size
        strip = Image.new("RGBA", ((w + 2) * FRAMES, (h + 2) * 2), (225, 228, 232, 255))
        for row, c in enumerate(("purple", "blue")):
            for i, im in enumerate(made[c]):
                strip.alpha_composite(im, (i * (w + 2), row * (h + 2)))
        strip.resize((strip.width * 6, strip.height * 6), Image.NEAREST).save(d / "strip-6x.png")
        gif = []
        for i in range(FRAMES * 2):
            f = Image.new("RGBA", ((w + 4) * 2, h + 4), (225, 228, 232, 255))
            f.alpha_composite(made["purple"][i % FRAMES], (2, 2))
            f.alpha_composite(made["blue"][i % FRAMES], (w + 6, 2))
            gif.append(f.resize((f.width * 6, f.height * 6), Image.NEAREST).convert("RGB"))
        gif[0].save(d / "roll-6x.gif", save_all=True, append_images=gif[1:], duration=70, loop=0)
        print("preview", d)
