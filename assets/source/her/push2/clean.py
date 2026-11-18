"""The push clip's frames with the trolley taken out (generated with the steward's trolley in its start
picture, `start.py`): a pixel the same as the trolley's own picture at that spot is the trolley's;
then loose specks; each frame stood on the floor line by its planted foot. Writes `push2/0.png` ...
`7.png` (frames 0 to 7 of the job; its frame 8 is frame 0 again) as 84 px cells, her middle at x 42,
her feet on row 83, as the sprite build takes them.

python assets/source/her/push2/clean.py"""
import json
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
S = json.load(open(HERE / "start.json"))
things = Image.open(ROOT / "assets/sprites/things.png").convert("RGBA")
tf = json.load(open(ROOT / "assets/sprites/things.json")); tf = tf.get("frames", tf)
f = tf["steward-trolley"]["frame"]
cart = Image.new("RGBA", (128, 128))
cart.alpha_composite(things.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"])), (S["cart_left"], 121 - S["cart_h"]))


def near(a, b, d=24):
    return sum(abs(a[k] - b[k]) for k in range(3)) <= d


def specks(im):
    px = im.load(); W, H = im.size
    seen = set()
    for y in range(H):
        for x in range(W):
            if px[x, y][3] and (x, y) not in seen:
                comp, st = [], [(x, y)]; seen.add((x, y))
                while st:
                    a, b = st.pop(); comp.append((a, b))
                    for c, d in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if 0 <= c < W and 0 <= d < H and (c, d) not in seen and px[c, d][3]:
                            seen.add((c, d)); st.append((c, d))
                if len(comp) < 12:
                    for a, b in comp: px[a, b] = (0, 0, 0, 0)


def her(i):
    im = Image.open(HERE / f"raw/a-{i}.png").convert("RGBA")
    px, cp = im.load(), cart.load()
    for y in range(128):
        for x in range(128):
            if px[x, y][3] and cp[x, y][3] and near(px[x, y], cp[x, y]):
                px[x, y] = (0, 0, 0, 0)
    specks(im)
    return im


if __name__ == "__main__":
    out = HERE
    for i in range(8):
        im = her(i)
        bb = im.getbbox()
        drop = 120 - (bb[3] - 1)
        cell = Image.new("RGBA", (84, 84))
        cell.alpha_composite(im.crop((S["px"] - 42, 121 - 84 - drop, S["px"] + 42, 121 - drop)), (0, 0))
        cell.save(out / f"{i}.png")
        print(i, "bbox", bb, "dropped", drop)
