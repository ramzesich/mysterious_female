"""The rope stand's fall: its start and end pictures in the game's own picture of the place (96 x 64, world x 9736..9832).
Finds where the game draws the stand (difference of two snapshots), then: gen/stand-start.png (the stand as it stands,
without its card, the door open behind), gen/stand-end-rough.png (both posts lying aft, quarter turns of their own pixels,
the rope slack over them), gen/stand-bare.png (the place with the door open and no stand). x4 copies beside them."""
from pathlib import Path
import json
from PIL import Image
R = Path(r"C:\Users\ramze\Development\mysterious_female-catch2")
T = Path(__file__).resolve().parent.parent
OUT, GEN = T / "out", T / "gen"; GEN.mkdir(exist_ok=True)
VX = 9400
bare, norope, opened = (Image.open(OUT / f"place-{n}.png").convert("RGB") for n in ("bare", "norope", "open"))
# where the stand and its card are drawn
xs, ys = [], []
for y in range(270):
    for x in range(480):
        if bare.getpixel((x, y)) != norope.getpixel((x, y)):
            xs.append(x); ys.append(y)
print("stand + card on screen:", min(xs), max(xs), min(ys), max(ys), "-> world x", min(xs) + VX, max(xs) + VX)
FLOOR = max(ys) + 1            # the screen row under the stand's lowest
print("floor row (first row under the stand):", FLOOR)
a = json.load(open(R / "assets/ship/ship.json"))
fr = a["frames"] if isinstance(a["frames"], dict) else {f["filename"]: f for f in a["frames"]}
f = fr["rope-barrier"]["frame"]
stand = Image.open(R / "assets/ship/ship.png").convert("RGBA").crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
SX = 9766 - 15 - VX            # its left column on the screen
X0, Y0 = 9736 - VX, FLOOR - 52
box = (X0, Y0, X0 + 96, Y0 + 64)
base = opened.crop(box).convert("RGBA")
base.save(GEN / "stand-bare.png")
start = base.copy(); start.alpha_composite(stand, (SX - X0, 52 - 23))
start.save(GEN / "stand-start.png")
# the end: each post a quarter turn clockwise (its top aft), lying on the floor; the rope slack over the aft one
post1, post2 = stand.crop((0, 0, 7, 23)), stand.crop((23, 0, 30, 23))
lie1, lie2 = post1.transpose(Image.ROTATE_270), post2.transpose(Image.ROTATE_270)   # 23 x 7, base at the left
end = base.copy()
x1, x2 = SX - X0 + 2, SX - X0 + 27          # the lying posts' left ends
end.alpha_composite(lie2, (x2, 52 - 7))
end.alpha_composite(lie1, (x1, 52 - 7))
end.save(GEN / "stand-end-posts.png")
rope, dark = (0x7a, 0x30, 0x45, 255), (0x6e, 0x27, 0x27, 255)
# the rope: from the forward post's ring (5 px from its top) in a slack curve on the floor to the aft post's ring
pts = [(x1 + 17, 45), (x1 + 18, 44), (x1 + 19, 44), (x1 + 20, 45), (x1 + 21, 46), (x1 + 22, 47), (x1 + 23, 48), (x1 + 24, 49), (x1 + 25, 50), (x1 + 26, 50),
       (x1 + 27, 50), (x1 + 28, 49), (x1 + 29, 48), (x1 + 30, 47), (x1 + 31, 46), (x1 + 32, 45), (x1 + 33, 44), (x1 + 34, 44), (x1 + 35, 44), (x1 + 36, 44),
       (x1 + 37, 44), (x1 + 38, 44), (x1 + 39, 44), (x1 + 40, 44), (x1 + 41, 44), (x1 + 42, 45)]
for (x, y) in pts:
    end.putpixel((x, y), rope); end.putpixel((x, y + 1), dark)
end.save(GEN / "stand-end-rough.png")
for n in ("stand-bare", "stand-start", "stand-end-rough"):
    im = Image.open(GEN / f"{n}.png"); im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(GEN / f"{n}-x4.png")
json.dump(dict(VX=VX, FLOOR=FLOOR, X0=X0 + VX, Y0=Y0, SX=SX + VX), open(GEN / "stand.json", "w"))
print("box", box, "stand left", SX + VX)
