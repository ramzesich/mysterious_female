"""The sky's art (plan-the-rest §7b, the user, 2026-11-20: "more realistically-looking sun and
reflections, more varied and volumetric clouds"; then mock-up B3 chosen: the sun just over a cloud's
top, the clouds soft with no dark base, god rays through them). Builds:

- `assets/sprites/sky.png` + `sky.json`: an atlas of the intro's clouds (`cloud-<i>`, each with its
  edge toward the sun lit, baked for where it stands) and the sun's disc (`sun`);
- `assets/sprites/sky-layout.json`: where each cloud stands, in screen px of the intro's wide view
  from the sun (a cloud's texel is two screen px), and where the rays' picture starts;
- `assets/sprites/sky-rays.png`: the god rays, worked out from the clouds where they stand (a pixel of
  air is lit by how much of the sun it sees past them, so each cloud casts a shadow lane away from
  the sun and beams show only where clouds break the light); smooth, one texel a screen px;
- `assets/sprites/sky-glow.png`: the sun's bloom, smooth, one texel a screen px;
- `assets/sprites/sky-strip.png`: the far clouds' strip (the game's far background, in play and from
  outside, and the intro's far rows), small clouds hazed toward the horizon's colour.

    python tools/build_sky.py

The clouds are PixelLab's (`create_image_pro`), raw in `assets/source/sky/tries/` (its README has
the jobs); the user chose the soft sets (`big-soft`, `mid-soft`, `small-soft`) over the first ones,
"too heavy", with dark bases. Their colours are their own, not the palette's (the user chose them
over the palette's mint and purple, 2026-11-20). The sun and its light are drawn here: light is flat
by nature (and smooth, the user's choice: "pixel-art shapes, the bloom and the haze smooth").
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TRIES = ROOT / "assets" / "source" / "sky" / "tries"
OUT = ROOT / "assets" / "sprites"
HAZE = np.array([0xcd, 0xee, 0xff], float)          # the sky at the horizon (src/background.js)

# The intro's clouds round the sun: [source, px right of the sun, px under it, mirrored]. Nothing under
# the sun: its path on the water is below it, and a cloud between them "looks off" (the user, 2026-11-20,
# of B3's cloud under it); a smaller one hides its right side instead (the last).
CLOUDS = [
    ("big-soft/2.png", -215, 72, False), ("big-soft/0.png", -340, -120, False), ("mid-soft/4.png", 330, -110, True),
    ("between-soft/2.png", 390, 150, False), ("mid-soft/0.png", -440, 205, False), ("mid-soft/8.png", -110, -230, True),
    ("small-soft/20.png", 200, -230, False), ("small-soft/12.png", -200, 230, False),
    ("mid-soft/7.png", 55, -6, False),
    # Over the ship, as the camera comes to it (the user: "a few more variously sized clouds here, but
    # not big"); clear of the funnel and its smoke.
    ("wide-soft/0.png", 640, 18, False), ("mid-soft/3.png", 820, 92, True), ("between-soft/0.png", 1010, 30, False),
    ("small-soft/5.png", 1080, 122, False), ("wide-soft/3.png", 1300, 4, True), ("small-soft/9.png", 560, 128, True),
    ("mid-soft/5.png", 1420, 112, False),
]
BLOOM = 0.85                    # the light round the sun ("turn the light down slightly", the user)
LINING = 0.9                    # how bright a cloud's edge toward the sun goes (near it)
RAYS = {"box": (-960, -330, 960, 540), "strength": 0.7, "reach": 420}   # (wide: the camera pans right past it)
STRIP = {"names": [f"small-soft/{i}.png" for i in (0, 1, 2, 4, 5, 8, 9, 11, 12, 14, 18, 20, 23, 24)],
         "w": 2048, "h": 60, "haze": 0.3, "seed": 21}


def load(name):
    return np.asarray(Image.open(TRIES / name).convert("RGBA"), float)


def save(a, path):
    Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), "RGBA").save(path, optimize=True)


def edges(al):
    return al & ~(np.roll(al, 1, 0) & np.roll(al, -1, 0) & np.roll(al, 1, 1) & np.roll(al, -1, 1))


def lining(a, cx, cy, strength, reach=70):
    """A cloud's edge toward the sun lit (cx, cy: the sun in the cloud's texels), fading with distance."""
    al = a[..., 3] > 0
    edge = edges(al)
    edge2 = al & ~edge & (np.roll(edge, 1, 0) | np.roll(edge, -1, 0) | np.roll(edge, 1, 1) | np.roll(edge, -1, 1))
    yy, xx = np.mgrid[:a.shape[0], :a.shape[1]]
    k = strength * np.exp(-np.hypot(xx - cx, yy - cy) / reach)
    out = a.copy()
    for m, f in ((edge, 1.0), (edge2, 0.5)):
        w = (k * f)[m][:, None]
        out[..., :3][m] = out[..., :3][m] * (1 - w) + np.array([255, 252, 236]) * w
    return out


def sun_disc(r=13):
    """The disc, pixel art: a pale core, a warmer rim, a half-clear ring outside it."""
    d = 2 * r + 5
    c = d // 2
    a = np.zeros((d, d, 4))
    dist = np.hypot(*(np.mgrid[:d, :d] - c))
    a[dist <= r + 1.6] = [255, 236, 170, 110]
    a[dist <= r + 0.5] = [255, 240, 186, 255]
    a[dist <= r - 0.8] = [255, 250, 222, 255]
    a[dist <= r - 3.5] = [255, 254, 246, 255]
    return a


def border(h, w, margin):
    """1 inside, falling smoothly to 0 at a picture's edges: none of its light ends in a line."""
    fy = np.minimum(np.arange(h), np.arange(h)[::-1]) / margin
    fx = np.minimum(np.arange(w), np.arange(w)[::-1]) / margin
    k = np.minimum.outer(fy.clip(0, 1), fx.clip(0, 1))
    return k * k * (3 - 2 * k)


def bloom(size=700, core=34):
    c = size / 2
    r = np.hypot(*(np.mgrid[:size, :size] - c))
    v = 0.85 * np.exp(-((r - core).clip(0) / 26) ** 1.2) + 0.32 * np.exp(-(r / 150) ** 1.4) + 0.12 * np.exp(-r / 320)
    v *= (1 - (r / c).clip(0, 1)) ** 0.5 * BLOOM                    # to nothing at its rim
    a = np.zeros((size, size, 4))
    a[..., :3] = (255, 248, 220)
    a[..., 3] = v.clip(0, 1) * 255
    return a


def god_rays(clouds, box, strength, reach):
    """The light in the air round the sun with the clouds' shadows in it (screen px, the sun at 0, 0)."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    occ = np.zeros((H, W))
    for px, x, y in clouds:
        al = np.kron(px[..., 3] / 255, np.ones((2, 2)))
        h, w = al.shape
        left, top = int(round(x - w / 2)) - x0, int(round(y - h / 2)) - y0
        ys, xs = slice(max(0, top), min(H, top + h)), slice(max(0, left), min(W, left + w))
        if ys.stop <= ys.start or xs.stop <= xs.start:
            continue                                                # (out past the rays' picture)
        occ[ys, xs] = np.maximum(occ[ys, xs], al[ys.start - top:ys.stop - top, xs.start - left:xs.stop - left])
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(float)
    lit = np.zeros((H, W))
    taps = [(0, 0), (-14, 0), (14, 0), (0, -14), (0, 14)]          # across the sun's disc
    steps = 96
    for sx, sy in taps:
        vis = np.ones((H, W))
        for i in range(1, steps):
            t = i / steps
            px = (xx + (sx - xx) * t).round().astype(int) - x0
            py = (yy + (sy - yy) * t).round().astype(int) - y0
            ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
            o = np.zeros((H, W))
            o[ok] = occ[py[ok], px[ok]]
            vis *= 1 - o * 0.35
        lit += vis.clip(0, 1)
    lit /= len(taps)
    r = np.hypot(xx, yy)
    v = lit * np.exp(-r / reach) * (r > 20) * strength * (1 - occ)  # not over the clouds' bodies
    v *= border(H, W, 220)
    a = np.zeros((H, W, 4))
    a[..., :3] = (255, 246, 214)
    a[..., 3] = (v * 255).clip(0, 255)
    return a


def strip():
    s = STRIP
    a = np.zeros((s["h"], s["w"], 4))
    rng = np.random.default_rng(s["seed"])
    x = 30
    while x < s["w"] - 120:
        c = load(s["names"][rng.integers(len(s["names"]))])
        if rng.random() < 0.5:
            c = c[:, ::-1]
        c = c.copy()
        c[..., :3] = c[..., :3] * (1 - s["haze"]) + HAZE * s["haze"]
        ch, cw = c.shape[:2]
        top = s["h"] - ch - int(rng.integers(0, max(1, s["h"] - ch)))
        if x + cw >= s["w"]:
            break
        m = c[..., 3] > 0
        a[top:top + ch, x:x + cw][m] = c[m]
        x += cw + 70 + int(rng.integers(0, 260))
    return a


def pack(frames):
    """One row, a px apart; Phaser's hash atlas."""
    w = sum(f.shape[1] + 1 for f in frames.values())
    h = max(f.shape[0] for f in frames.values())
    sheet = np.zeros((h, w, 4))
    meta, x = {}, 0
    for name, f in frames.items():
        fh, fw = f.shape[:2]
        sheet[:fh, x:x + fw] = f
        meta[name] = {"frame": {"x": x, "y": 0, "w": fw, "h": fh}, "rotated": False, "trimmed": False,
                      "spriteSourceSize": {"x": 0, "y": 0, "w": fw, "h": fh}, "sourceSize": {"w": fw, "h": fh}}
        x += fw + 1
    return sheet, {"frames": meta, "meta": {"image": "sky.png", "size": {"w": w, "h": h}, "scale": "1"}}


def main():
    frames, placed, layout = {}, [], {"clouds": []}
    for i, (name, x, y, mirror) in enumerate(CLOUDS):
        px = load(name)
        if mirror:
            px = px[:, ::-1].copy()
        h, w = px.shape[:2]
        px = lining(px, (w - x) / 2, (h - y) / 2, LINING)       # the sun in its texels
        frames[f"cloud-{i}"] = px
        placed.append((px, x, y))
        layout["clouds"].append({"frame": f"cloud-{i}", "x": x, "y": y})
    frames["sun"] = sun_disc()
    sheet, atlas = pack(frames)
    save(sheet, OUT / "sky.png")
    (OUT / "sky.json").write_text(json.dumps(atlas, indent=1))
    layout["rays"] = {"x": RAYS["box"][0], "y": RAYS["box"][1]}
    (OUT / "sky-layout.json").write_text(json.dumps(layout, indent=1))
    save(god_rays(placed, RAYS["box"], RAYS["strength"], RAYS["reach"]), OUT / "sky-rays.png")
    save(bloom(), OUT / "sky-glow.png")
    save(strip(), OUT / "sky-strip.png")
    for f in ("sky.png", "sky-rays.png", "sky-glow.png", "sky-strip.png"):
        print(f, (OUT / f).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
