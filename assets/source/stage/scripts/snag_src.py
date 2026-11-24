"""The rival's key clip: its start and end pictures, 128 x 128 from world x 12240, the stage's top to its floor.
The star cloth and the drum kit turned flat green (he is navy on navy); the boards, the lamp and the trap door kept."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops
R = Path(r"C:\Users\ramze\Development\mysterious_female-catch3")
G = R / "assets/source/stage/gen"
O = Path(__file__).resolve().parent.parent / "out"
X0 = 12240 - 12192                      # the canvas's left column in the stage's picture
GREEN = (0, 177, 64)
left = Image.open(G / "src-left-final.png").convert("RGB")
opened = Image.open(G / "trap-open-s21.png").convert("RGB")
lamp = Image.open(G / "lamp-s4.png").convert("RGBA"); lamp = lamp.crop(lamp.getbbox())      # 12 x 26
run = Image.open(R / "assets/source/stage/rival-raw/run/7.png").convert("RGBA"); run = run.crop(run.getbbox())

def base(open_):
    src = opened if open_ else left
    c = src.crop((X0, 0, X0 + 128, 128)).copy()         # (the left half is 160 wide: 48..176 runs 16 px past it)
    full = Image.new("RGB", (320, 128)); full.paste(src, (0, 0)); full.paste(left.transpose(Image.FLIP_LEFT_RIGHT), (160, 0))
    c = full.crop((X0, 0, X0 + 128, 128)).copy()
    px = c.load(); bare = left.load()
    for y in range(0, 118):
        for x in range(128):
            keep = False
            if open_:
                sx = x + X0
                if sx < 160:
                    a, b = opened.getpixel((sx, y)), left.getpixel((sx, y))
                    keep = sum(abs(a[i] - b[i]) for i in range(3)) > 30 and a[0] > a[2] + 20 and 90 <= sx <= 132 and y >= 90   # the lid, the ladder (brown): what the inpaint drew
            if not keep:
                px[x, y] = GREEN
    return c.convert("RGBA")

def hang(c, length):
    """The lamp on its cable: its lens's middle `length` px under the stage's top."""
    x = 12283 - 12240
    top = length + 7 - lamp.height
    ImageDraw.Draw(c).line((x, 0, x, top), fill=(46, 34, 47, 255))
    c.alpha_composite(lamp, (x - lamp.width // 2, top))

a = base(False)
d = ImageDraw.Draw(a)
# the trap door shut: a seam in the boards and a brass ring (where the open one's hole is)
hx0, hx1 = 12305 - 12240, 12326 - 12240
d.line((hx0, 120, hx1, 120), fill=(40, 16, 20, 255)); d.line((hx0, 126, hx1, 126), fill=(40, 16, 20, 255))
d.line((hx0, 120, hx0 - 2, 126), fill=(40, 16, 20, 255)); d.line((hx1, 120, hx1 - 2, 126), fill=(40, 16, 20, 255))
d.rectangle(((hx0 + hx1) // 2 - 1, 122, (hx0 + hx1) // 2, 123), fill=(217, 164, 59, 255))
hang(a, 30)
a.alpha_composite(run, (22 - run.width // 2, 128 - run.height))
b = base(True); hang(b, 74)
a.convert("RGB").save(G / "snag-start.png"); b.convert("RGB").save(G / "snag-end.png")
sh = Image.new("RGB", (128 * 2 + 4, 128)); sh.paste(a.convert("RGB"), (0, 0)); sh.paste(b.convert("RGB"), (132, 0))
sh.resize((sh.width * 4, sh.height * 4), Image.NEAREST).save(O / "snag-src.png")
print("rival", run.size)
