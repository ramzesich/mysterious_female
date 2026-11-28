"""The rough ends of the hit, for the edits: her framed, facing us (her front view, the painting round her middle, her head
and shoulders over it), where the hit left her; the two empty-handed, facing each other, the one she bumped a step back."""
from compose import *

ROT = RAW.parent


def rot(name, d):
    im = Image.open(ROT / f"{name}-raw/Idle/rotations/{d}.png").convert("RGBA")
    return im.crop(im.getbbox())


def framed(cx):
    """Her front view standing at middle cx, the painting round her middle."""
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = her("front")
    fx0, fx1 = cols(f)
    left = cx - (fx0 + fx1) // 2
    c.alpha_composite(f, (left, FLOOR - 84))
    top = FLOOR - 84 + f.getbbox()[1]          # her head's top row
    py = top + 19                               # the frame's top a little under her shoulders
    c.alpha_composite(PAINT, (cx - PAINT.width // 2, py))
    head = f.crop((0, 0, f.width, f.getbbox()[1] + 22))
    c.alpha_composite(head, (left, FLOOR - 84))
    return c


def end(her_x, coat_x, apron_x):
    c = Image.new("RGBA", (W, H), GREEN)
    a, b = rot("handler_coat", "east"), rot("handler_apron", "west")
    c.alpha_composite(a, (coat_x - a.width // 2, FLOOR - a.height))
    c.alpha_composite(b, (apron_x - b.width // 2, FLOOR - b.height))
    c.alpha_composite(framed(her_x))
    return c


if __name__ == "__main__":
    out = HERE / "ends"
    out.mkdir(exist_ok=True)
    # (Her middle where the run left her; the one she bumped a step back from her; the painting's middle at GX + 63.)
    end(GX + 63 - 52, GX + 50, GX + 100).save(out / "end-left.png")
    end(GX + 63 + 52, GX + 26, GX + 76).save(out / "end-right.png")
    end(GX + 63, GX + 30, GX + 96).save(out / "end-hop.png")
    S = Image.new("RGB", (W * 3, H))
    for i, n in enumerate(("end-left", "end-right", "end-hop")):
        S.paste(Image.open(out / f"{n}.png").convert("RGB"), (i * W, 0))
    S.resize((S.width * 2, S.height * 2), Image.NEAREST).save(r"C:\Users\ramze\AppData\Local\Temp\p11\p1\gag-ends-rough-x2.png")
