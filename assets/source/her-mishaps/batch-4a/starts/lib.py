import json
from PIL import Image
R = "C:/Users/ramze/Development/mysterious_female/"
B = "C:/Users/ramze/AppData/Local/Temp/dt/b1/"
A = Image.open(R + "assets/ship/ship.png").convert("RGBA"); F = json.load(open(R + "assets/ship/ship.json"))["frames"]
T = Image.open(R + "assets/sprites/things.png").convert("RGBA"); TF = json.load(open(R + "assets/sprites/things.json")); TF = TF.get("frames", TF)
def cut(img, fr): f = fr["frame"]; return img.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
def ship(k): return cut(A, F[k])
def thing(k): return cut(T, TF[k])
def her(p): return Image.open(R + "assets/source/her/" + p).convert("RGBA")
def row(pics, path, k=3, bg=(70, 70, 80, 255), h=None):
    h = h or max(p.height for p in pics)
    S = Image.new("RGBA", (sum(p.width for p in pics) + 8 * len(pics), h), bg); x = 0
    for p in pics: S.alpha_composite(p.convert("RGBA"), (x, h - p.height)); x += p.width + 8
    S.resize((S.width * k, S.height * k), Image.NEAREST).save(path); return S.size
