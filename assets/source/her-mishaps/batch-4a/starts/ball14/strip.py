"""A clip's frames side by side, 3x, on a floor line; and a GIF: python strip.py <folder> <n> <name>."""
import sys
from PIL import Image, ImageDraw
d, n, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
fr = [Image.open(f"{d}/{i}.png").convert("RGBA") for i in range(n + 1)]
W = 128; S = Image.new("RGBA", (W * len(fr), 128), (200, 205, 212, 255)); g = ImageDraw.Draw(S)
for i, f in enumerate(fr):
    S.alpha_composite(f, (i * W, 0)); g.line((i * W, 120, i * W + W - 1, 120), fill=(240, 120, 120, 90))
    g.text((i * W + 3, 2), str(i), fill=(0, 0, 0, 255))
S.resize((S.width * 2, S.height * 2), Image.NEAREST).save(f"{name}.png")
gif = []
for f in fr:
    b = Image.new("RGBA", (128, 128), (200, 205, 212, 255)); b.alpha_composite(f); gif.append(b.resize((384, 384), Image.NEAREST).convert("P"))
gif[0].save(f"{name}.gif", save_all=True, append_images=gif[1:] + [gif[-1]] * 6, duration=70, loop=0)
