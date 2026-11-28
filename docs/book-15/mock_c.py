"""Mock-ups of option C: the chosen book's cover shown with the row (over the real shot, canvas px)."""
import os
from PIL import Image, ImageDraw
OUT = os.path.dirname(os.path.abspath(__file__))
base = Image.open(os.path.join(OUT, "row-full.png")).convert("RGBA")
cov = Image.open(os.path.join(OUT, "..", "..", "assets", "ship", "covers", "cover-15.png")).convert("RGBA")
cov2 = cov.resize((cov.width * 2, cov.height * 2), Image.NEAREST)
def place(x, y, dim=0.0):
    im = base.copy()
    if dim:
        im.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, int(255 * dim))))
        im.alpha_composite(base.crop((0, 0, 960, 172)), (0, 0))      # the row stays undimmed
    sh = Image.new("RGBA", (cov2.width + 4, cov2.height + 4), (10, 6, 14, 110))
    im.alpha_composite(sh, (x + 6, y + 6))
    d = ImageDraw.Draw(im)
    d.rectangle([x - 2, y - 2, x + cov2.width + 1, y + cov2.height + 1], fill=(46, 34, 47, 255))
    im.alpha_composite(cov2, (x, y))
    return im.convert("RGB")
place(360, 174, 0.35).save(os.path.join(OUT, "mock-c1-under.png"))
place(700, 174).save(os.path.join(OUT, "mock-c2-beside.png"))
