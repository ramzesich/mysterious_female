"""9a to 9d (2026-11-19): the jogger meets her, as the game draws it (her built sheet, his built sheet), the moment of
the hit (middles 16 apart: his touch box 14 wide). Facing east is hers in every picture; he as the game flips him."""
from starts2 import *
from PIL import ImageOps
import os
O = R + "assets/source/her-mishaps/batch-4a/starts/jog9/"
os.makedirs(O, exist_ok=True)
PM = json.load(open(R + "assets/sprites/people.json")); PS = Image.open(R + "assets/sprites/people.png").convert("RGBA")
PC, PCOLS = PM["cell"], PM["cols"]; J = PM["people"]["jogger"]
def cell(i): return PS.crop(((i % PCOLS) * PC, (i // PCOLS) * PC, (i % PCOLS) * PC + PC, (i // PCOLS) * PC + PC))
def jog(n, west): f = cell(J["anims"]["run"][n]); return ImageOps.mirror(f) if west else f
def putj(im, pic, cx): im.alpha_composite(pic, (cx - PC // 2, FLOOR + 1 - PC))
D = 16
pics = {}
for n in (0, 2, 4, 6):
    im = Image.new("RGBA", (128, 128)); put(im, herf("run", n), 56); putj(im, jog(n, True), 56 + D); pics[f"9a-run{n}"] = im
im = Image.new("RGBA", (128, 128)); put(im, herf("stand"), 56); putj(im, jog(3, True), 56 + D); pics["9b-stand"] = im
im = Image.new("RGBA", (128, 128)); putj(im, jog(3, False), 72 - D); put(im, herf("stand"), 72); pics["9c-stand"] = im
im = Image.new("RGBA", (128, 128)); put(im, herf("run", 2), 56); putj(im, jog(5, False), 56 + D); pics["9d-run2"] = im
for k, v in pics.items(): v.save(O + k + ".png")
row([pics["9a-run2"], pics["9b-stand"], pics["9c-stand"], pics["9d-run2"]], O + "meet.png", k=3, bg=(200, 200, 205, 255))
print(J, PC)
