"""7a's start picture (2026-11-19): she slides east (her slip frame 0, what the game shows), the world's deck chair
flipped as the game stands it (facing west, at her), sliding at her face; middles 18 apart (the hit's distance)."""
from starts2 import *
from PIL import ImageOps
import os
O = R + "assets/source/her-mishaps/batch-4a/starts/chair7a/"
os.makedirs(O, exist_ok=True)
for n in range(4):
    im = Image.new("RGBA", (128, 128)); put(im, herf("slip", n), 52); at(im, ImageOps.mirror(ship("deck-chair")), 52 + 18)
    im.save(O + f"c7a-slip{n}.png")
row([Image.open(O + f"c7a-slip{n}.png") for n in range(4)], O + "c7a-starts.png", k=3, bg=(200, 200, 205, 255))
