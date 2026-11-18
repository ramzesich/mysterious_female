"""The towel stack's start pictures (2026-11-18): the stack and its stool exactly as the game draws them
(`TowelStack.textures` in src/world/movers.js, its rectangles copied here), alone and with her own
standing sprite passing it, in a 128 x 128 frame, the floor on row 120, the stool's middle at x 36."""
import os
from PIL import Image, ImageDraw
R = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
here = os.path.dirname(os.path.abspath(__file__))
def c(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
def stack():
    im = Image.new("RGBA", (28, 70)); d = ImageDraw.Draw(im)
    offs = [0, 1, -1, 1, 0, -1, 0, 2, -1, 0, 1, -1, 0, 1]
    for i in range(14):
        y, off = 70 - (i + 1) * 5, offs[i]
        d.rectangle((2 + off, y, 2 + off + 21, y + 4), fill=c("9babb2"))
        d.rectangle((3 + off, y, 3 + off + 19, y + 3), fill=c("8fd3ff" if i % 4 == 2 else "ffffff"))
        d.rectangle((3 + off, y + 3, 3 + off + 19, y + 3), fill=c("4d9be6" if i % 4 == 2 else "c7dcd0"))
    return im
def stool():
    im = Image.new("RGBA", (26, 12)); d = ImageDraw.Draw(im)
    for r in ((1, 0, 24, 3), (3, 3, 2, 9), (21, 3, 2, 9)):
        d.rectangle((r[0], r[1], r[0] + r[2] - 1, r[1] + r[3] - 1), fill=c("7a4528"))
    d.rectangle((2, 0, 23, 1), fill=c("cd683d"))
    return im
W = H = 128; FLOOR = 120; X = 36
def base():
    img = Image.new("RGBA", (W, H))
    img.alpha_composite(stool(), (X - 13, FLOOR - 12))
    img.alpha_composite(stack(), (X - 14, FLOOR - 12 - 70))
    return img
her = lambda: Image.open(os.path.join(R, "assets/source/her-mishaps/paper-start/start-4a.png")).convert("RGBA")  # 80x80, feet row 73
if __name__ == "__main__":
  alone = base(); alone.save(os.path.join(here, "start-alone.png"))
  withher = base(); withher.alpha_composite(her(), (X + 36 - 40, FLOOR - 73)); withher.save(os.path.join(here, "start-her.png"))
