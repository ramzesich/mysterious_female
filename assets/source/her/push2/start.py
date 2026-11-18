"""The push clip's start picture (the user, 2026-11-18: "her legs do not move properly when she's
pushing"): her built push frame 0 (assets/sprites/her.png, cell 84) against the steward's trolley as
the game sets them (her middle 29.5 px from its middle: the push's gap, one px more than before), feet
on row 120 of a 128 px canvas. The trolley is taken out of the frames afterwards (`clean.py`).

python assets/source/her/push2/start.py"""
import json
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sheet = Image.open(ROOT / "assets/sprites/her.png").convert("RGBA")
meta = json.load(open(ROOT / "assets/sprites/her.json"))
n = meta["anims"]["push"][0]
C, cols = 84, 48
her = sheet.crop(((n % cols) * C, (n // cols) * C, (n % cols) * C + C, (n // cols) * C + C))
things = Image.open(ROOT / "assets/sprites/things.png").convert("RGBA")
tf = json.load(open(ROOT / "assets/sprites/things.json")); tf = tf.get("frames", tf)
f = tf["steward-trolley"]["frame"]
cart = things.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
PX = 40                                 # her middle on the canvas
cx = PX + 29.5                          # the trolley's middle
im = Image.new("RGBA", (128, 128))
left = round(cx - cart.width / 2)
im.alpha_composite(cart, (left, 121 - cart.height))
im.alpha_composite(her, (PX - 42, 121 - C))
im.save(HERE / "start.png")
json.dump({"px": PX, "cart_left": left, "cart_w": cart.width, "cart_h": cart.height}, open(HERE / "start.json", "w"))
big = Image.new("RGBA", im.size, (233, 223, 204, 255)); big.alpha_composite(im)
big.resize((512, 512), Image.NEAREST).save(HERE / "start-x4.png")
print(left)
