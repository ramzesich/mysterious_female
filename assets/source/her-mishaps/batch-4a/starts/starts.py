from lib import *
from PIL import ImageDraw
W = 128; FLOOR = 120
def canvas(): return Image.new("RGBA", (W, W))
def tray():
    im = Image.new("RGBA", (26, 4)); d = ImageDraw.Draw(im)
    d.rectangle((1, 0, 24, 3), fill=(0x2e, 0x22, 0x2f, 255)); d.rectangle((2, 1, 23, 2), fill=(0xc7, 0xdc, 0xd0, 255)); d.rectangle((3, 1, 10, 1), fill=(255, 255, 255, 255))
    return im
stand = Image.open(R + "assets/source/her-mishaps/paper-start/start-4a.png").convert("RGBA")   # 80, feet row 73, head top x 31 row 15
gull = thing("gull-perched")                                                                    # 20, feet x 11 bottom row 19
out = {}
# 20: standing, the gull landed on her head
im = canvas(); hx, hy = 56, FLOOR - 73
im.alpha_composite(stand, (hx - 31, hy)); im.alpha_composite(gull, (hx - 11, hy + 15 + 2 - 20)); out["g20-stand"] = im
# 20: her run (frame 2) with the gull on her head
r = her("run-steady/2.png"); im = canvas(); ox, oy = 0, FLOOR - 79
im.alpha_composite(r, (ox, oy)); im.alpha_composite(gull, (ox + 57 - 11, oy + 23 + 2 - 20)); out["g20-run"] = im
# 3: her run (frame 7, front foot down) landing on a tray
r = her("run-steady/7.png"); im = canvas(); ox, oy = 10, FLOOR - 79 - 4
im.alpha_composite(tray(), (ox + 52 - 13, FLOOR - 4)); im.alpha_composite(r, (ox, oy)); out["t3-run"] = im
# 7b: standing (sliding east on the wet floor), the deck chair at the back of her legs
ch = ship("deck-chair"); im = canvas(); hx = 64
im.alpha_composite(ch, (hx - 6 - ch.width, FLOOR - ch.height)); im.alpha_composite(stand, (hx - 31, FLOOR - 73)); out["c7b"] = im
for k, v in out.items(): v.save(B + k + ".png")
row(list(out.values()), B + "starts.png", k=3)
# 13a: her south view in 96 px, feet on row 88
s = her("rotations/south.png"); im = Image.new("RGBA", (96, 96)); im.alpha_composite(s, (16, 88 - 62)); im.save(B + "d13a-south96.png")
