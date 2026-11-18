import json, os
from PIL import Image, ImageDraw
R = "C:/Users/ramze/Development/mysterious_female/"
W, H, FL = 210, 112, 104          # scene, floor row
BG = (226, 214, 192, 255)
atlas = Image.open(R + "assets/ship/ship.png").convert("RGBA")
fr = json.load(open(R + "assets/ship/ship.json"))["frames"]
def piece(n):
    f = fr[n]["frame"]; return atlas.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
TROL, BAGS = piece("luggage-trolley"), piece("suitcases")
def load(p): return Image.open(p).convert("RGBA")
RUN = [load(R + f"assets/source/her/run/{i}.png") for i in range(8)]
PCART = [load(R + f"assets/source/people/porter/cart/{i}.png") for i in range(8)]
PFRONT = load(R + "assets/source/people/porter/stand.png")
TIP = [load(f"tip-cap/{i}.png") for i in range(9)]
def clip(name): return [load(f"{name}/{i}.png") for i in range(9)]
def floor_of(frames): return frames[0].getbbox()[3] - 1
def put(sc, img, cx, feet, flip=False, cxin=None):
    """img's column cxin (default its middle) at scene x cx, its row `feet` on the floor."""
    if flip: img = img.transpose(Image.FLIP_LEFT_RIGHT)
    c = img.width // 2 if cxin is None else (img.width - 1 - cxin if flip else cxin)
    sc.alpha_composite(img, (int(cx - c), FL - feet))
def cart(sc, cx, flip):
    for p, dy in ((TROL, 0), (BAGS, 29)):
        q = p.transpose(Image.FLIP_LEFT_RIGHT) if flip else p
        sc.alpha_composite(q, (int(cx - q.width // 2), FL + 1 - dy - q.height))
def porter(sc, x, d, i=0, img=None):
    put(sc, img or PCART[i % 8], x, 78, d < 0)
def blank():
    sc = Image.new("RGBA", (W, H), BG); ImageDraw.Draw(sc).rectangle((0, FL + 1, W, H), fill=(70, 76, 110, 255)); return sc
def clipat(sc, frames, k, x0):
    f = frames[k]; sc.alpha_composite(f, (x0, FL - floor_of(frames)))
def herx(frames, k, x0):
    b = frames[k].getbbox(); return x0 + b[0], x0 + b[2]
out = {}
# 8a: she runs into the cart's front; he has stopped behind it.
A = clip("cart-8a-draped"); x0 = 30; seq = []
cartx = 70 + x0; px = cartx + 24
for k in range(4):
    s = blank(); cart(s, cartx + (3 - k) * 5, True); porter(s, px + (3 - k) * 5, -1, k)
    put(s, RUN[(k * 2) % 8], 40 + 14 + x0 - (4 - k) * 14, 61); seq.append(s)
for k in range(3, 9):
    s = blank(); porter(s, px, -1); clipat(s, A, k, x0); seq.append(s)
out["8a"] = seq
# 8b: the cart pushes into her as she stands facing it; it follows her front till she sits.
B = clip("cart-8b-backpedal-2"); x0 = 10; seq = []
front = herx(B, 0, x0)[1] + 1
for k in range(4):
    s = blank(); cl = front + (4 - k) * 5; cart(s, cl + 14, True); porter(s, cl + 14 + 24, -1, k); clipat(s, B, 0, x0); seq.append(s)
cl = front
for k in range(1, 9):
    if k <= 6: cl = min(cl, herx(B, k, x0)[1] + 1)
    s = blank(); cart(s, cl + 14, True); porter(s, cl + 38, -1, k if k <= 6 else 0); clipat(s, B, k, x0); seq.append(s)
out["8b"] = seq
# 8c: the cart reaches her back; she sits into the bags; he wheels her on, sees her, tips his cap.
C = clip("cart-8c-fixed"); x0 = 20; seq = []
cartx = 52 + x0
for k in range(4):
    s = blank(); cart(s, cartx - (4 - k) * 5, False); porter(s, cartx - 24 - (4 - k) * 5, 1, k)
    f = C[0].copy(); f.paste((0, 0, 0, 0), (0, 0, 70, f.height)); clipat(s, [f] + C[1:], 0, x0); seq.append(s)
for k in range(1, 9):
    s = blank(); porter(s, cartx - 24, 1, 0); clipat(s, C, k, x0); seq.append(s)
for k in range(1, 7):
    s = blank(); porter(s, cartx - 24 + k * 5, 1, k); clipat(s, C, 8, x0 + k * 5); seq.append(s)
for k in range(1, 9):
    s = blank(); porter(s, cartx - 24 + 30, 1, img=TIP[k]); clipat(s, C, 8, x0 + 30); seq.append(s)
out["8c"] = seq
# 8d: she runs into his back as he pushes the cart away; she bounces off and sits; he turns round.
D = clip("cart-8d-bounce-2"); x0 = 0; seq = []
hb = herx(D, 0, x0)[1]; px = hb + 9
for k in range(4):
    s = blank(); cart(s, px + 24 - (3 - k) * 5, False); porter(s, px - (3 - k) * 5, 1, k)
    put(s, RUN[(k * 2) % 8], 96 + x0 - (4 - k) * 14, 61); seq.append(s)
for k in range(3, 9):
    q = px + 5 * min(k - 2, 4)          # he walks on a few steps before he notices
    s = blank(); cart(s, q + 24, False)
    (put(s, PFRONT, q, 62, True) if k >= 7 else porter(s, q, 1, k))
    clipat(s, D, k, x0); seq.append(s)
out["8d"] = seq
for name, seq in out.items():
    hold = seq + [seq[-1]] * 6
    big = [f.resize((W * 3, H * 3), Image.NEAREST).convert("P", palette=Image.ADAPTIVE) for f in hold]
    big[0].save(f"porter-{name}.gif", save_all=True, append_images=big[1:], duration=100, loop=0, disposal=2)
    n = len(seq); cols = 6; rows = (n + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * W, rows * H), BG)
    for i, f in enumerate(seq): sheet.alpha_composite(f, ((i % cols) * W, (i // cols) * H))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(f"porter-{name}-sheet.png")
    print(name, n)
