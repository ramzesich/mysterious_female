"""Flat roughs of the scene's new pieces, drawn into the game's own pictures of their places (for PixelLab to redraw).
Writes OUT/rough/<name>.png and <name>-base.png (the place without the piece), each with its world origin in rough.json."""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
SRC, RO = HERE / "src", HERE / "rough"       # (`src/`: the game's own pictures of the places, Phaser's snapshot halved, what the scene moves hidden)
RO.mkdir(exist_ok=True)
D11, D10 = 560, 704
RIM, LEVER, TUB, HATCH, DRAIN, LADDER = 6768, 6803, 6862, 6648, 6739, 6744
STEEL, STEEL_D, STEEL_L, DARK = (155, 171, 178), (98, 85, 101), (199, 220, 208), (46, 34, 47)
RED, YEL = (232, 59, 59), (249, 194, 43)
meta = {}


def crop(src, x0, y0, x1, y1):
    v = json.load(open(SRC / f"{src}.json"))
    im = Image.open(SRC / f"{src}.png").convert("RGB")
    return im.crop((int(x0 - v["vx"]), int(y0 - v["vy"]), int(x1 - v["vx"]), int(y1 - v["vy"])))


def save(name, im, x0, y0):
    im.save(RO / f"{name}.png")
    im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(RO / f"{name}-x4.png")
    meta[name] = [x0, y0, im.width, im.height]


def thick_line(d, a, b, w, fill):
    d.line([a, b], fill=fill, width=w)


# --- 1. The drain's lever on its stand, armed (leaning toward the pool) and thrown (over toward the hot tub) -------
X0, Y0 = 6752, 464
base = crop("gap-full", X0, Y0, X0 + 128, Y0 + 112)
save("lever-base", base, X0, Y0)
PIV = (LEVER - X0, D11 - 10 - Y0)


def lever(angle):
    """Knee-high (the user, 2026-11-24: the first, 46 px to its grip, was "way too big. It should be at least half a
    height"): its stand 15 px, its grip 21 px over the deck when armed."""
    im = base.copy()
    d = ImageDraw.Draw(im)
    cx, fy = LEVER - X0, D11 - Y0
    d.rectangle([cx - 7, fy - 2, cx + 7, fy - 1], fill=STEEL_D, outline=DARK)
    d.rectangle([cx - 4, fy - 10, cx + 4, fy - 2], fill=STEEL, outline=DARK)
    for i in range(-3, 4, 2):
        d.point([(cx + i, fy - 5), (cx + i, fy - 4)], fill=YEL if (i // 2) % 2 == 0 else DARK)
    d.pieslice([cx - 5, fy - 15, cx + 5, fy - 5], 180, 360, fill=STEEL_L, outline=DARK)
    a = math.radians(angle)
    tip = (PIV[0] + math.sin(a) * 13, PIV[1] - math.cos(a) * 13)
    g0 = (PIV[0] + math.sin(a) * 8, PIV[1] - math.cos(a) * 8)
    thick_line(d, PIV, tip, 3, DARK)
    thick_line(d, PIV, g0, 1, STEEL_L)
    thick_line(d, g0, tip, 3, RED)
    return im, tip


for name, ang in (("lever-up", -33), ("lever-down", 75)):
    im, tip = lever(ang)
    save(name, im, X0, Y0)
    print(name, "tip world", round(tip[0] + X0), round(tip[1] + Y0), "px over the deck", round(D11 - Y0 - tip[1]))

# --- 2. The hatch in the tank's floor, shut and open ---------------------------------------------------------
X0, Y0 = 6592, 528
base = crop("tank-drained", X0, Y0, X0 + 112, Y0 + 96)
save("hatch-base", base, X0, Y0)
hx, fy = HATCH - X0, 592 - Y0


def hatch(open_):
    im = base.copy()
    d = ImageDraw.Draw(im)
    far, near = fy + 1, fy + 14
    quad = [(hx - 17, far), (hx + 17, far), (hx + 21, near), (hx - 21, near)]
    # its frame, set in the tiles
    d.polygon([(hx - 19, far - 1), (hx + 19, far - 1), (hx + 23, near + 1), (hx - 23, near + 1)], fill=YEL, outline=DARK)
    if not open_:
        d.polygon(quad, fill=STEEL, outline=DARK)
        d.line([(hx - 15, far + 2), (hx + 15, far + 2)], fill=STEEL_L)
        d.ellipse([hx - 5, far + 4, hx + 5, far + 9], outline=DARK)        # a ring handle, lying flat
        d.rectangle([hx - 12, far - 1, hx - 8, far], fill=DARK)
        d.rectangle([hx + 8, far - 1, hx + 12, far], fill=DARK)
    else:
        d.polygon(quad, fill=(20, 16, 26), outline=DARK)
        # the top of a ladder inside, against the far side
        for x in (hx - 7, hx + 7):
            d.line([(x, far + 1), (x, near - 2)], fill=STEEL_L)
        d.line([(hx - 7, far + 6), (hx + 7, far + 6)], fill=STEEL)
        # the lid swung up on its far hinges, standing behind the opening, its underside to us
        d.polygon([(hx - 17, far - 1), (hx + 17, far - 1), (hx + 16, far - 31), (hx - 16, far - 31)], fill=STEEL_D, outline=DARK)
        d.rectangle([hx - 12, far - 27, hx + 12, far - 5], outline=STEEL)
        d.line([(hx - 12, far - 16), (hx + 12, far - 16)], fill=STEEL)
        d.ellipse([hx - 3, far - 19, hx + 3, far - 13], fill=STEEL, outline=DARK)
    return im


save("hatch-shut", hatch(False), X0, Y0)
save("hatch-open", hatch(True), X0, Y0)

# --- 3. The tank's aft end: the ladder down to the floor, the drain's grate ------------------------------------
X0, Y0 = 6672, 528
base = crop("tank-drained", X0, Y0, X0 + 112, Y0 + 96)
save("aft-base", base, X0, Y0)
im = base.copy()
d = ImageDraw.Draw(im)
fy = 592 - Y0
# the drain: a grate in the floor, seen a little from above
gx = DRAIN - 28 - X0
d.polygon([(gx - 9, fy + 3), (gx + 9, fy + 3), (gx + 11, fy + 11), (gx - 11, fy + 11)], fill=STEEL_D, outline=DARK)
for i in range(-7, 8, 3):
    d.line([(gx + i, fy + 4), (gx + i * 1.2, fy + 10)], fill=DARK)
save("aft", im, X0, Y0)

# --- 4. The ceiling panel in deck 10's hallway, shut and hanging open ------------------------------------------
X0, Y0 = 6592, 560
base = crop("hall", X0 + 8, Y0, X0 + 104, Y0 + 56)
X0 += 8
save("ceiling-base", base, X0, Y0)
cx, cy = HATCH - X0, 575 - Y0
for name in ("ceiling-shut", "ceiling-open"):
    im = base.copy()
    d = ImageDraw.Draw(im)
    d.rectangle([cx - 20, cy - 1, cx + 20, cy + 3], fill=(230, 230, 230), outline=DARK)
    if name.endswith("shut"):
        d.rectangle([cx - 17, cy + 1, cx + 17, cy + 2], fill=(200, 200, 205))
        d.rectangle([cx + 12, cy + 1, cx + 14, cy + 3], fill=STEEL_D)
    else:
        d.rectangle([cx - 17, cy, cx + 17, cy + 2], fill=(20, 16, 26))
        d.rectangle([cx - 19, cy + 2, cx - 16, cy + 36], fill=(230, 230, 230), outline=DARK)
    save(name, im, X0, Y0)

json.dump(meta, open(RO / "rough.json", "w"), indent=1)
