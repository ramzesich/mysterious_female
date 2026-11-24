"""A flat rough of the pillow stack on the laundry cart, in the room's own picture, for PixelLab to redraw.
Canvas 128 x 128: world x 5916..6044, y 738..866 (the floor line at row 110). -> out/gen/stack-rough.png, stack-base.png"""
from pathlib import Path
from PIL import Image, ImageDraw
O = Path(__file__).resolve().parent.parent / "out"
(O / "gen").mkdir(exist_ok=True)
X0, Y0 = 5916 - 5849, 738 - 716
base = Image.open(O / "base-cart.png").convert("RGB").crop((X0, Y0, X0 + 128, Y0 + 128))
base.save(O / "gen/stack-base.png")
im = base.copy(); d = ImageDraw.Draw(im)
CX = 5980 - 5916                    # the cart's middle on the canvas
TOP = 110 - 44                      # the towels' top row
WHITE, SHADE, LINE = (246, 246, 250), (206, 213, 226), (118, 128, 150)
N, H, W = 5, 9, 36
for i in range(N):
    y1 = TOP - i * H + 1; y0 = y1 - H
    off = (1, -1, 0, 1, -1)[i]
    x0 = CX - W // 2 + off; x1 = x0 + W
    d.rounded_rectangle((x0, y0, x1, y1), radius=4, fill=WHITE, outline=LINE)
    d.line((x0 + 4, y1 - 2, x1 - 4, y1 - 2), fill=SHADE)
    d.line((x0 + 3, y1 - 3, x0 + 3, y0 + 3), fill=SHADE)
im.save(O / "gen/stack-rough.png")
both = Image.new("RGB", (128 * 4 * 2 + 8, 128 * 4), (30, 30, 40))
both.paste(base.resize((512, 512), Image.NEAREST), (0, 0)); both.paste(im.resize((512, 512), Image.NEAREST), (520, 0))
both.save(O / "gen/stack-rough-4x.png")
print("top row", TOP - N * H + 1, "=", 110 - (TOP - N * H + 1), "px over the floor")
