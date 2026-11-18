from lib import *
from starts2 import herf
FLOOR, X = 120, 40          # the door's middle; things' last row 120
def base():
    im = Image.new("RGBA", (128, 128)); d = ship("door-cabin-bg"); im.alpha_composite(d, (X - 17, FLOOR + 1 - 74)); return im
a = base(); a.save(B + "door-shut.png")
b = base(); b.alpha_composite(herf("stand").transpose(Image.FLIP_LEFT_RIGHT), (X + 30 - 42, FLOOR + 1 - 84)); b.save(B + "door-her.png")
e = base(); f = Image.open(B + "fixed/d13f-0.png").convert("RGBA"); e.alpha_composite(f, (X + 40 - 47, FLOOR - 2 - 78)); e.save(B + "door-her-flat.png")
row([a, b, e], B + "door-starts.png", k=3, bg=(232, 220, 203, 255))
