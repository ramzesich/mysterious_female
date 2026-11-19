"""A try's nine frames side by side, cropped round her, enlarged 4x on a mid ground, with the floor row marked."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
name = sys.argv[1]
fr = [Image.open(HERE / name / f"{i}.png").convert("RGBA") for i in range(9)]
box = (24, 40, 104, 124)
W, H = box[2] - box[0], box[3] - box[1]
out = Image.new("RGBA", (W * 9 + 8 * 2, H), (90, 110, 130, 255))
for i, f in enumerate(fr):
    out.alpha_composite(f.crop(box), (i * (W + 2), 0))
d = ImageDraw.Draw(out)
d.line([(0, 121 - box[1]), (out.width, 121 - box[1])], fill=(255, 200, 0, 255))
out = out.resize((out.width * 4, out.height * 4), Image.NEAREST)
out.save(HERE / f"{name}-sheet.png")
for i, f in enumerate(fr):
    print(i, f.getbbox())
