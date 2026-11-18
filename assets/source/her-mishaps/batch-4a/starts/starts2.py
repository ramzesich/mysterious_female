"""Start pictures from her built sheet (what the game draws): 128 canvas, her sole's last row 120 (= the
floor line, as the world's things' last rows), p.x at canvas MX (her cell's x 42)."""
from lib import *
from PIL import ImageDraw
import json
M = json.load(open(R + "assets/sprites/her.json")); SH = Image.open(R + "assets/sprites/her.png").convert("RGBA"); C, COLS = M["cell"], M["cols"]
def herf(anim, n=0):
    i = M["anims"][anim][n]; return SH.crop(((i % COLS) * C, (i // COLS) * C, (i % COLS) * C + C, (i // COLS) * C + C))
FLOOR = 120
def put(im, pic, px): im.alpha_composite(pic, (px - 42, FLOOR + 1 - 84))
def tray():
    im = Image.new("RGBA", (26, 4)); d = ImageDraw.Draw(im)
    d.rectangle((1, 0, 24, 3), fill=(0x2e, 0x22, 0x2f, 255)); d.rectangle((2, 1, 23, 2), fill=(0xc7, 0xdc, 0xd0, 255)); d.rectangle((3, 1, 10, 1), fill=(255, 255, 255, 255))
    return im
def at(im, pic, cx):   # a world thing, origin (0.5, 1), at canvas x cx on the floor
    im.alpha_composite(pic, (round(cx - pic.width / 2), FLOOR + 1 - pic.height))
if __name__ == "__main__":
    import sys
    out = {}
    # 7b: sliding east (her slip clip), the deck chair (unflipped: drawn east) hitting her back, middles 18 apart
    for n in range(4):
        im = Image.new("RGBA", (128, 128)); at(im, ship("deck-chair"), 64 - 18); put(im, herf("slip", n), 64); out[f"c7b2-slip{n}"] = im
    # 3: her run frames on the floor; the tray just ahead of her front foot where it lands next
    for n in range(8):
        im = Image.new("RGBA", (128, 128)); put(im, herf("run", n), 56); out[f"t3-run{n}"] = im
    for k, v in out.items(): v.save(B + k + ".png")
    row([out[f"c7b2-slip{n}"] for n in range(4)] + [out[f"t3-run{n}"] for n in range(8)], B + "starts2.png", k=2, bg=(200, 200, 205, 255))
