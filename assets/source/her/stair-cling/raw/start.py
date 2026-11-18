import json
from PIL import Image, ImageDraw, ImageOps
D = "C:/Users/ramze/AppData/Local/Temp/bb/cling/"
R = "C:/Users/ramze/Development/mysterious_female/"
sheet = Image.open(R + "assets/sprites/her.png").convert("RGBA")
m = json.load(open(R + "assets/sprites/her.json")); C, cols = m["cell"], m["cols"]
def cell(i): return sheet.crop(((i % cols) * C, (i // cols) * C, (i % cols + 1) * C, (i // cols + 1) * C))
hx = lambda c: tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) + (255,)
look = dict(carpet=hx("#9babb2"), fleck=hx("#625565"), nosing=hx("#3e3546"), side=hx("#7f708a"), rail=hx("#e8eaec"), light=hx("#ffffff"))
S, AX, AY = 96, 48, 80
run, rise = 410 / 49, 8.0
def stairs(with_rail):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    for i in range(-10, 10):
        p0 = (round(AX + i * run), round(AY - i * rise)); p1 = (round(AX + (i + 1) * run), round(AY - (i + 1) * rise))
        x, w = p0[0], max(1, p1[0] - p0[0])
        g.rectangle([x, p1[1], x + w - 1, p0[1] + 5 - 1], fill=look["side"])
        g.rectangle([x, p1[1], x + w - 1, p1[1] + 2], fill=look["carpet"])
        g.point((x + w // 2, p1[1] + 1), fill=look["fleck"])
        g.rectangle([x + w - 1, p1[1], x + w - 1, p1[1] + 3], fill=look["nosing"])
    if with_rail:
        # The handrail as drawStairs draws it: a rail height (22) over the flight's line, 2 px, its light over it.
        a = (AX - 10 * run, AY + 10 * rise - 22); b = (AX + 10 * run, AY - 10 * rise - 22)
        g.line([a, b], fill=look["rail"], width=2)
        g.line([(a[0], a[1] - 1), (b[0], b[1] - 1)], fill=look["light"], width=1)
    return im
st = stairs(False); st.save(D + "stairs.png")
rail = stairs(True); rail.save(D + "stairs-rail.png")
stand = cell(m["frames"]["stand"])
for name, fr in (("up", stand), ("down", ImageOps.mirror(stand))):
    im = st.copy(); im.alpha_composite(fr, (AX - C // 2, AY - C))
    r = rail.copy(); r.alpha_composite(fr, (AX - C // 2, AY - C))
    # The rail in front of her, as in the game.
    rr = rail.copy(); rr.alpha_composite(fr, (AX - C // 2, AY - C))
    front = Image.new("RGBA", (S, S)); 
    import numpy as np
    a_ = np.array(rail); b_ = np.array(st)
    mask = (np.abs(a_.astype(int) - b_.astype(int)).sum(2) > 0)
    out = np.array(rr); out[mask] = a_[mask]
    Image.fromarray(out).save(D + f"start-{name}.png")
s = Image.new("RGBA", (S * 2, S), (225, 232, 238, 255))
s.alpha_composite(Image.open(D + "start-up.png")); s.alpha_composite(Image.open(D + "start-down.png"), (S, 0))
s.resize((S * 8, S * 4), Image.NEAREST).save(D + "starts.png")
