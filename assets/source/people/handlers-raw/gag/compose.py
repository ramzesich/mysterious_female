"""Item 10's hit: the start pictures of its clips (the game's own frames at the moment of the hit, at exact game px: the
handlers' walk frame with the painting where its panel is, and her run or fall frame against them), and the rough ends
the edits finish (her framed, facing us; the handlers empty-handed, facing each other). One green canvas for all:
W x H, the floor at row FLOOR, the handlers' 128 x 80 frames at (GX, GY)."""
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
RAW = HERE.parent
ROOT = RAW.parent.parent.parent.parent
W, H, FLOOR = 208, 128, 124
GX, GY = 40, FLOOR - 76
GREEN = (0, 200, 0, 255)
PAINT = Image.open(ROOT / "assets/source/things/tries/painting/lighthouse.png").convert("RGBA")
PAINT = PAINT.crop(PAINT.getbbox())
HER = Image.open(ROOT / "assets/sprites/her.png").convert("RGBA")
HJ = json.loads((ROOT / "assets/sprites/her.json").read_text())


def her(clip, k=0, flip=False):
    c, n = HJ["cell"], HJ["cols"]
    a = HJ["anims"][clip]
    i = a[k] if isinstance(a, list) else a
    f = HER.crop(((i % n) * c, (i // n) * c, (i % n + 1) * c, (i // n + 1) * c))
    return f.transpose(Image.FLIP_LEFT_RIGHT) if flip else f


def handlers(clip, i):
    J = json.loads((RAW / "cut" / f"{clip}.json").read_text())
    f = Image.open(RAW / "cut" / clip / f"{i}.png").convert("RGBA")
    box = J["panel"][i]
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c.alpha_composite(PAINT, (GX + 41, GY + box[3] - PAINT.height + 1))
    c.alpha_composite(f, (GX, GY))
    return c


def cols(im):
    xs = [x for x in range(im.width) if any(im.getpixel((x, y))[3] for y in range(im.height))]
    return min(xs), max(xs)


def start(clip, i, side):
    """She runs into the handler on `side` (-1: from the left, running right; 1: from the right, running left)."""
    c = Image.new("RGBA", (W, H), GREEN)
    h = handlers(clip, i)
    c.alpha_composite(h)
    x0, x1 = cols(h)
    f = her("run", 2, flip=side > 0)
    fx0, fx1 = cols(f)
    # (Her front 1 px into the handler's back or front: the moment they touch.)
    left = x0 - fx1 + 1 if side < 0 else x1 - fx0 - 1
    c.alpha_composite(f, (left, FLOOR - 84))
    return c


def hop(clip, i, flip):
    c = Image.new("RGBA", (W, H), GREEN)
    c.alpha_composite(handlers(clip, i))
    f = her("fall", 0, flip=flip)
    fx0, fx1 = cols(f)
    top = GY + 22                      # the painting's top
    c.alpha_composite(f, (GX + 63 - (fx0 + fx1) // 2, top - 84 + 1))
    return c


if __name__ == "__main__":
    out = HERE / "starts"
    out.mkdir(exist_ok=True)
    for clip, i, name in (("walk", 1, "E"), ("walkW-s1", 1, "W")):
        start(clip, i, -1).save(out / f"run-{name}-left.png")
        start(clip, i, 1).save(out / f"run-{name}-right.png")
        hop(clip, i, False).save(out / f"hop-{name}-r.png")
        hop(clip, i, True).save(out / f"hop-{name}-l.png")
    print(sorted(p.name for p in out.glob("*.png")))
