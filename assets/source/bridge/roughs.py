"""Flat roughs of near-catch 6's new pieces, drawn into the game's own picture of the bridge's forward end (for PixelLab
to redraw; docs/near-catch-6-remake-log.md). Writes rough/<name>.png, <name>-base.png (the place without the piece) and
rough.json (each picture's world origin).

`src/forward.png` is the game's own picture of the place (Phaser's snapshot halved; the console, the helm and the alarm
panel hidden, no figures, the decks' dim off), its world origin in `src/forward.json`. The cut-away's soft edge is
still in it along the room's forward end and under its ceiling: `flat()` lays the wall's own panels over that."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC, RO = HERE / "src", HERE / "rough"
RO.mkdir(exist_ok=True)
D10, CEIL, WALL = 704, 576, 1843            # the bridge's floor, its ceiling, its forward wall (world px)
LADDER = 1864                               # the hatch's column: it cannot move (deck 11's balcony over it ends at 1896)
CONSOLE, STATION = 1930, 1985               # the console's middle at its new place; the alarm station's
STEEL, STEEL_D, STEEL_L, DARK = (155, 171, 178), (98, 85, 101), (199, 220, 208), (46, 34, 47)
RED, RED_L, YEL = (232, 59, 59), (255, 143, 143), (249, 194, 43)
BODY, BODY_D = (127, 112, 138), (98, 85, 101)
meta = {}
V = json.load(open(SRC / "forward.json"))


def flat():
    """The place with its wall's panels carried into the shaded strips (the forward 20 px, the 25 rows under the
    ceiling), and the floor's rows into the forward 20 px."""
    im = Image.open(SRC / "forward.png").convert("RGB")
    px = im.load()
    x0, yc, yf = WALL - V["vx"], CEIL - V["vy"], D10 - V["vy"]
    win = (1856 - V["vx"], 596 - V["vy"])                # the window's frame starts here (left, top)
    for y in range(yc, yf):
        for x in range(x0, im.width):
            shaded = x < x0 + 24 or y < yc + 26
            if not shaded or (x >= win[0] and y >= win[1] and y < win[1] + 64):
                continue
            px[x, y] = px[x0 + 16 * 9 + (x - x0) % 16, yf - 34 + (y - yc) % 16]
    for y in range(yf, yf + 18):
        for x in range(x0, x0 + 24):
            px[x, y] = px[x + 48, y]
    # (Forward of the wall and over the ceiling: the hull's dark.)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, x0 - 1, im.height], fill=(37, 34, 46))
    d.rectangle([0, 0, im.width, yc - 1], fill=(37, 34, 46))
    return im


PLACE = flat()
PLACE.save(RO / "place.png")


def crop(x0, y0, x1, y1):
    return PLACE.crop((x0 - V["vx"], y0 - V["vy"], x1 - V["vx"], y1 - V["vy"]))


def save(name, im, x0, y0):
    im.save(RO / f"{name}.png")
    im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(RO / f"{name}-x4.png")
    meta[name] = [x0, y0, im.width, im.height]


def piece(name):
    a = json.load(open(ROOT / "assets/ship/ship.json"))["frames"][name]
    f = a.get("frame", a)
    return Image.open(ROOT / "assets/ship/ship.png").convert("RGBA").crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


# --- 1. The escape hatch under the ceiling, open: its collar, its lid hanging down the wall, its ladder let down --------
X0, Y0 = 1836, 560
base = crop(X0, Y0, X0 + 96, Y0 + 144)
save("hatch-base", base, X0, Y0)
im = base.copy()
d = ImageDraw.Draw(im)
L, T = LADDER - 15 - X0, CEIL - Y0          # the collar: 30 px wide, 14 tall
d.rectangle([L, T, L + 29, T + 13], fill=STEEL, outline=DARK)
d.line([L + 1, T + 1, L + 28, T + 1], fill=STEEL_L)
for i in range(7):
    d.rectangle([L + 1 + i * 4, T + 8, L + 4 + i * 4, T + 11], fill=YEL if i % 2 == 0 else DARK)
d.rectangle([L + 2, T + 12, L + 27, T + 13], fill=(27, 27, 38))
# the lid, hinged on the collar's forward edge and hung straight down, seen edge on: a plate 28 px long, 4 thick
d.rectangle([L, T + 14, L + 3, T + 42], fill=STEEL, outline=DARK)
d.line([L + 1, T + 16, L + 1, T + 40], fill=STEEL_L)
d.rectangle([L, T + 12, L + 4, T + 15], fill=DARK)
# the ladder: two rails, a rung every 8 px, down to the floor
RX0, RX1 = LADDER - 7 - X0, LADDER + 6 - X0
for x in (RX0, RX1):
    d.rectangle([x - 1, T + 11, x + 1, D10 - Y0 - 1], fill=STEEL_L, outline=DARK)
for y in range(T + 18, D10 - Y0 - 2, 8):
    d.rectangle([RX0 + 2, y, RX1 - 2, y + 1], fill=STEEL_L)
    d.line([RX0 + 2, y + 2, RX1 - 2, y + 2], fill=DARK)
save("hatch-open", im, X0, Y0)

# --- 2. The alarm station at the console's aft end: a pedestal with a slanted top, one big red button, a beacon -------
X0, Y0 = 1940, 624
base = crop(X0, Y0, X0 + 96, Y0 + 96)
con = piece("bridge-console")
base.paste(con, (CONSOLE - con.width // 2 - X0, D10 - Y0 - con.height), con)
save("station-base", base, X0, Y0)
im = base.copy()
d = ImageDraw.Draw(im)
cx, fy = STATION - X0, D10 - Y0
d.rectangle([cx - 17, fy - 2, cx + 17, fy - 1], fill=BODY_D, outline=DARK)                     # its plinth
d.rectangle([cx - 15, fy - 38, cx + 15, fy - 3], fill=BODY, outline=DARK)                      # its body
d.rectangle([cx - 11, fy - 20, cx + 11, fy - 7], outline=BODY_D)
d.polygon([(cx - 17, fy - 46), (cx + 17, fy - 40), (cx + 17, fy - 37), (cx - 17, fy - 37)], fill=STEEL, outline=DARK)   # its slanted top
for i in range(5):                                                                          # the button's striped plate
    d.rectangle([cx - 10 + i * 4, fy - 44 + i // 2, cx - 7 + i * 4, fy - 42 + i // 2], fill=YEL if i % 2 == 0 else DARK)
d.rectangle([cx - 3, fy - 47, cx + 2, fy - 44], fill=DARK)                                      # the button: its stem, its dome
d.ellipse([cx - 6, fy - 53, cx + 5, fy - 46], fill=RED, outline=DARK)
d.line([cx - 3, fy - 51, cx, fy - 52], fill=RED_L)
d.rectangle([cx + 12, fy - 52, cx + 13, fy - 41], fill=DARK)                                    # the beacon on its stalk, aft
d.rectangle([cx + 9, fy - 55, cx + 16, fy - 53], fill=DARK)
d.rectangle([cx + 10, fy - 61, cx + 15, fy - 56], fill=(174, 35, 52), outline=DARK)
save("station", im, X0, Y0)

json.dump(meta, open(RO / "rough.json", "w"), indent=1)
print(meta)
