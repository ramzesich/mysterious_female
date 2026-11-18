import json
from PIL import Image
R = r"C:/Users/ramze/Development/mysterious_female/"
atlas = Image.open(R + "assets/ship/ship.png").convert("RGBA")
fr = json.load(open(R + "assets/ship/ship.json"))["frames"]
def piece(n):
    f = fr[n]["frame"]; return atlas.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
trolley, bags = piece("luggage-trolley"), piece("suitcases")
her = Image.open(R + "assets/source/her-mishaps/paper-start/start-4a.png").convert("RGBA")  # 80x80, feet row 74
W, H, FLOOR = 128, 112, 104
def cart(img, cx, flip):
    for p, dy in ((trolley, 0), (bags, 29)):
        q = p.transpose(Image.FLIP_LEFT_RIGHT) if flip else p
        img.alpha_composite(q, (cx - q.width // 2, FLOOR - dy - q.height))
def herat(img, x0, flip=False):
    q = her.transpose(Image.FLIP_LEFT_RIGHT) if flip else her
    img.alpha_composite(q, (x0, FLOOR - 74))
out = {}
# 8a: she faces east, the cart's front just ahead of her; 8c: her back to the cart (she faces east, cart behind)
a = Image.new("RGBA", (W, H)); herat(a, 14); cart(a, 14 + 40 + 2 + 14, True); out["start-8a"] = a
c = Image.new("RGBA", (W, H)); herat(c, 48); cart(c, 48 + 20 - 2 - 14, False); out["start-8c"] = c
for k, v in out.items():
    v.save(rf"{__import__('os').environ['TEMP']}/cartgag/{k}.png")
    print(k, v.getbbox())
sheet = Image.new("RGBA", (W * 2 + 8, H), (230, 220, 200, 255))
sheet.alpha_composite(out["start-8a"], (0, 0)); sheet.alpha_composite(out["start-8c"], (W + 8, 0))
sheet.resize((sheet.width * 4, H * 4), Image.NEAREST).save(rf"{__import__('os').environ['TEMP']}/cartgag/starts-x4.png")
