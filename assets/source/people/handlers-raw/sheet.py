"""A cut clip's sheet and GIF with the real painting where its panel is. Usage: python sheet.py <cut name>"""
import json, sys
from pathlib import Path
from PIL import Image
HERE = Path(__file__).parent
name = sys.argv[1]
J = json.loads((HERE / "cut" / f"{name}.json").read_text())
p = Image.open(HERE.parent.parent / "things/tries/painting/lighthouse.png").convert("RGBA")
p = p.crop(p.getbbox())
fr = []
for i in range(J["frames"]):
    f = Image.open(HERE / "cut" / name / f"{i}.png")
    c = Image.new("RGBA", f.size, (246, 246, 244, 255))
    box = J["panel"][i]
    if box:
        c.alpha_composite(p, (box[0], box[3] - p.height + 1))
    c.alpha_composite(f)
    fr.append(c.convert("RGB"))
cols = 5
S = Image.new("RGB", (128 * cols, 80 * ((len(fr) + cols - 1) // cols)), (255, 255, 255))
for i, f in enumerate(fr):
    S.paste(f, ((i % cols) * 128, (i // cols) * 80))
S.resize((S.width * 3, S.height * 3), Image.NEAREST).save(HERE / f"{name}-x3.png")
big = [f.resize((512, 320), Image.NEAREST) for f in fr]
big[0].save(HERE / f"{name}.gif", save_all=True, append_images=big[1:], duration=110, loop=0)
