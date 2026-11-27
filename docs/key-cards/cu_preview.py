import sys, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import numpy as np
from PIL import Image, ImageDraw
import build_popups as BP
from build_hud import SLOT
from versions import card as world_card, lying as world_lying
ROOT = r"C:\Users\ramze\Development\mysterious_female-refine"
CARDS = {"deck": "4d9be6", "ent": "e83b3b", "hk": "1ebc73", "off": "f9c22b"}
H = lambda s: np.array(list(bytes.fromhex(s)) + [255], np.uint8)
fr = json.load(open(ROOT + "/assets/sprites/closeups.json"))["frames"]
sheet = np.array(Image.open(ROOT + "/assets/sprites/closeups.png").convert("RGBA"))

def recoloured(c):
    d = fr[f"card-{c}"]["frame"]
    im = sheet[d["y"]:d["y"] + d["h"], d["x"]:d["x"] + d["w"]].copy()
    w = (im[:, :, 3] > 0).sum(axis=1)
    top = next(r for r in range(len(w)) if w[r] >= 0.9 * w.max())
    body = im[top:]
    white = (body[:, :, :3] == 255).all(axis=2) & (body[:, :, 3] > 0)
    stripe = (body[:, :, :3] == H(CARDS[c])[:3]).all(axis=2) & (body[:, :, 3] > 0)
    body[white] = H(CARDS[c]); body[stripe] = H("ffffff")
    return im

def shrunk(im):
    w = (im[:, :, 3] > 0).sum(axis=1)
    top = next(r for r in range(len(w)) if w[r] >= 0.9 * w.max())
    cc = BP.crop(im[top:].copy())
    ink = tuple(int(v) for v in cc[cc.shape[0] // 2, 0])
    W, Hh = BP.CARD_SIZE
    out = np.zeros((Hh, W, 4), np.uint8)
    out[1:-1, 1:-1] = BP.majority(cc[2:-2, 2:-2], W - 2, Hh - 2)
    out[0, 1:-1] = out[-1, 1:-1] = out[1:-1, 0] = out[1:-1, -1] = ink
    return out

def old(c):
    d = fr[f"card-{c}"]["frame"]; return sheet[d["y"]:d["y"] + d["h"], d["x"]:d["x"] + d["w"]].copy()

def hud(a, fill):
    a = a.copy()
    for x, y in SLOT: a[y, x] = fill
    return a

rows = []
for label, get in (("now", old), ("new", recoloured)):
    for c in CARDS:
        cu = get(c); ic = shrunk(cu)
        fill = H("ffffff") if label == "now" else H(CARDS[c])
        rows.append((label, c, cu, hud(ic, H("ffffff")), hud(ic, fill), ic))
# Sheet: per card, now and new: close-up x2, HUD x6 (slot white and slot in the colour), popup icon x6, world v5 x6.
K = 6
S = Image.new("RGBA", (1500, 620), (88, 96, 112, 255)); dr = ImageDraw.Draw(S)
x = 10
for i, c in enumerate(CARDS):
    for j, label in enumerate(("now", "new")):
        _, _, cu, hw, hc, ic = rows[j * 4 + i]
        y = 20 + j * 300
        dr.text((x, y - 16), f"{c} {label}", fill=(255, 255, 255))
        a = Image.fromarray(cu); S.alpha_composite(a.resize((a.width * 2, a.height * 2), Image.NEAREST), (x, y))
        b = Image.fromarray(hc if label == "new" else hw); S.alpha_composite(b.resize((b.width * K, b.height * K), Image.NEAREST), (x + 74, y + 110))
        if label == "new":
            wv = world_card(c, whole=True, lanyard="navy"); S.alpha_composite(wv.resize((wv.width * K, wv.height * K), Image.NEAREST), (x + 160 - 70 + 70, y + 60))
    x += 370
S.save("cu-preview.png")
# The HUD's slot: a white slot (as now) and the slot in the card's colour, side by side, x8.
T = Image.new("RGBA", (8 * 16 * 8 + 20, 18 * 8 + 20), (30, 34, 48, 255))
for i, c in enumerate(CARDS):
    _, _, _, hw, hc, _ = rows[4 + i]
    for k, a in enumerate((hw, hc)):
        im = Image.fromarray(a); T.alpha_composite(im.resize((im.width * 8, im.height * 8), Image.NEAREST), (10 + (i * 2 + k) * 128, 10))
T.save("hud-slot.png")
print(BP.CARD_SIZE)
