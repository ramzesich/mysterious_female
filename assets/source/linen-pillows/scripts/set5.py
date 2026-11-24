"""The pillows' pieces and the scatter clip's two pinned pictures.
1. The stack, cut from its redraw (rows filled across) -> gen/stack.png (its bottom row sits on the cart's towels).
2. The clip's set, 128 x 128: flat green, a darker floor from row 116, the cart as a flat blue shape with its towels
   magenta (so that every pale pixel of a frame is a pillow's): the start (the cart at 34, the stack on it) and the
   end's rough (the cart 28 px on, four flat shapes lying where the pillows should) -> gen/scatter-start.png, scatter-end-rough.png"""
from pathlib import Path
from PIL import Image, ImageDraw
O = Path(__file__).resolve().parent.parent / "out"; G = O / "gen"
base = Image.open(G / "stack-base.png").convert("RGB"); g = Image.open(G / "stack-s11.png").convert("RGB")
ROWS = (19, 65); X = (40, 88)
st = Image.new("RGBA", (X[1] - X[0], ROWS[1] - ROWS[0] + 1), (0, 0, 0, 0))
for y in range(ROWS[0], ROWS[1] + 1):
    xs = [x for x in range(X[0], X[1]) if sum(abs(a - b) for a, b in zip(base.getpixel((x, y)), g.getpixel((x, y)))) > 30]
    if not xs: continue
    for x in range(min(xs), max(xs) + 1):
        st.putpixel((x - X[0], y - ROWS[0]), g.getpixel((x, y)) + (255,))
bb = st.getbbox(); st = st.crop(bb)
DX = X[0] + bb[0] - 64          # the stack's left edge from the cart's middle
print("stack", st.size, "left edge", DX, "from the cart's middle; top", 110 - (ROWS[0] + bb[1]), "px over the floor; bottom row", ROWS[0] + bb[3] - 1, "(towels' top row 66)")
st.save(G / "stack.png")
(G / "stack.txt").write_text(f"{DX} {110 - (ROWS[0] + bb[3])}")     # dx from the cart's middle, px over the floor of its bottom edge

BG, FLOOR, BLUE, DARK, PINK = (40, 150, 70), (25, 105, 50), (40, 60, 200), (20, 30, 120), (200, 60, 180)
cart = Image.open(O / "thing-laundry-cart-empty.png").convert("RGBA")     # (the user: "Use this cart, but empty")
RIM, SINK = 32, 3      # the rim over the floor; the bottom pillow sits this far into the tub, behind the rim
flat = Image.new("RGBA", cart.size, (0, 0, 0, 0))
for y in range(cart.height):
    for x in range(cart.width):
        r, gg, b, a = cart.getpixel((x, y))
        if not a: continue
        l = (r + gg + b) / 3
        flat.putpixel((x, y), (DARK if l < 110 else BLUE) + (255,))
FL = 116
CW = 208                # the canvas: from 35 px forward of the cart to the room's aft wall (world 5887..6095)
def stage(cart_left, stack=False):
    im = Image.new("RGB", (CW, 128), BG)
    ImageDraw.Draw(im).rectangle((0, FL, CW - 1, 127), fill=FLOOR)
    if stack:
        im.paste(st, (cart_left + 23 + DX, FL - RIM + SINK - st.height), st)
    im.paste(flat, (cart_left, FL - flat.height), flat)
    return im
START, END = 35, 7
a = stage(START, True)
a.save(G / "scatter5-start.png")
z = stage(END); d = ImageDraw.Draw(z)
WHITE, SHADE, LINE = (246, 246, 250), (206, 213, 226), (118, 128, 150)
def pillow(cx, cy, w, h, ang):
    p = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0)); q = ImageDraw.Draw(p)
    q.rounded_rectangle((4, 4, w + 3, h + 3), radius=4, fill=WHITE, outline=LINE)
    q.line((8, h + 1, w - 1, h + 1), fill=SHADE)
    p = p.rotate(ang, expand=True, resample=Image.NEAREST)
    z.paste(p, (cx - p.width // 2, cy - p.height // 2), p)
# The pillows scattered (canvas x = world - 5887): two low ones on the floor under the chute's hatch (the hatch 75..107,
# its foot 11 px up: nothing of them over 15), the door kept clear (121..159), two at the room's aft end in front of
# the aft rack (161..201).
pillow(73, FL - 6, 40, 11, 0)
pillow(98, FL - 8, 38, 11, -7)
pillow(181, FL - 6, 40, 11, 0)
pillow(183, FL - 16, 36, 11, 10)
pale = [(x, y) for y in range(128) for x in range(53, CW) if min(z.getpixel((x, y))) > 190]
near = [q for q in pale if q[0] < 140]; far = [q for q in pale if q[0] >= 140]
print("near", min(q[0] for q in near), max(q[0] for q in near), "top", FL - min(q[1] for q in near), "px; far", min(q[0] for q in far), max(q[0] for q in far), "top", FL - min(q[1] for q in far))
z.save(G / "scatter5-end-rough.png")
both = Image.new("RGB", (CW * 3, 128 * 3 * 2 + 4), (30, 30, 40))
both.paste(a.resize((CW * 3, 384), Image.NEAREST), (0, 0)); both.paste(z.resize((CW * 3, 384), Image.NEAREST), (0, 388))
both.save(G / "scatter5-set-3x.png")
