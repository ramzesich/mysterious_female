import json
from PIL import Image, ImageDraw
D = "C:/Users/ramze/AppData/Local/Temp/bb/slip/"
R = "C:/Users/ramze/Development/mysterious_female/"
sheet = Image.open(R + "assets/sprites/her.png").convert("RGBA")
m = json.load(open(R + "assets/sprites/her.json")); C, cols = m["cell"], m["cols"]
def cell(i): return sheet.crop(((i % cols) * C, (i // cols) * C, (i % cols + 1) * C, (i // cols + 1) * C))
hx = lambda c: tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) + (255,)
look = dict(carpet=hx("#9babb2"), fleck=hx("#625565"), nosing=hx("#3e3546"), side=hx("#7f708a"))
S = 96
AX, AY = 48, 80            # the stair point she stands on (her feet's middle)
def stairs(run, rise):
    # As drawStairs: a flight ascending east; step i from corner i to corner i+1, tread at the upper
    # corner's y across, its nosing at the step's east end, the side down to the underside.
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    for i in range(-10, 10):
        p0 = (round(AX + i * run), round(AY - i * rise)); p1 = (round(AX + (i + 1) * run), round(AY - (i + 1) * rise))
        x, w = p0[0], max(1, p1[0] - p0[0])
        g.rectangle([x, p1[1], x + w - 1, p0[1] + 5 - 1], fill=look["side"])
        g.rectangle([x, p1[1], x + w - 1, p1[1] + 2], fill=look["carpet"])
        g.point((x + w // 2, p1[1] + 1), fill=look["fleck"])
        g.rectangle([x + w - 1, p1[1], x + w - 1, p1[1] + 3], fill=look["nosing"])
    return im
for name, run, rise in (("steep", 410 / 49, 8.0), ("gentle", 164 / 14, 108 / 14)):
    st = stairs(run, rise); st.save(D + f"stairs-{name}.png")
    im = st.copy()
    # Her slip frame raised so that her front (uphill) toe is on its tread.
    lift = round(11 * rise / run)
    im.alpha_composite(cell(m["frames"]["slip"]), (AX - C // 2, AY - C - lift))
    im.save(D + f"start-{name}.png")
s = Image.new("RGBA", (S * 2, S), (225, 232, 238, 255))
s.alpha_composite(Image.open(D + "start-steep.png")); s.alpha_composite(Image.open(D + "start-gentle.png"), (S, 0))
s.resize((S * 8, S * 4), Image.NEAREST).save(D + "starts-4x.png")
