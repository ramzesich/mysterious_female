"""The pictures her slide was generated from (run from the repo root: python assets/source/her/shaft-slide/inputs.py).

The game's own shaft (assets/ship/shaft/strip.png, on its dark) round the slope, with her crawl frame at the slope's lip
(`start.png`: her middle 22 px short of the lip, where the game starts the slide, her head at the lip) and at its foot
(`end.png`: 18 px past it, crawl frame 4). Then the same two with the shaft turned green, its shapes kept
(`green-start.png`, `green-end.png`): the clip is made on these, since none of her colours is near green and she can be
told from the shaft in every frame (on the dark steel her navy skirt and dark hair were lost in two frames of nine).
`place.json`: where the picture stands in the world.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import build_shaft as S                                     # noqa: E402

g = S.geometry()
strip = Image.open(ROOT / "assets/ship/shaft/strip.png").convert("RGBA")
her = Image.open(ROOT / "assets/sprites/her.png").convert("RGBA")
meta = json.loads((ROOT / "assets/sprites/her.json").read_text(encoding="utf-8"))
cell, cols = meta["cell"], meta["cols"]
frame = lambda i: her.crop(((i % cols) * cell, (i // cols) * cell, (i % cols) * cell + cell, (i // cols) * cell + cell))
crawl = [frame(i).transpose(Image.FLIP_LEFT_RIGHT) for i in meta["anims"]["crawl"]]      # facing forward, toward the bow
X0, Y0, W, H = g["slopeFoot"] - 56, g["oy"], 172, 104
bg = Image.new("RGBA", (W, H), S.VOID)
bg.alpha_composite(strip.crop((X0 - g["ox"], 0, X0 - g["ox"] + W, H)))


def with_her(x, y, k):
    im = bg.copy()
    im.alpha_composite(crawl[k], (x - cell // 2 - X0, y + 1 - cell - Y0))          # (her picture a px lower than her foot)
    return im.convert("RGB")


def green(im):
    out = Image.new("RGB", im.size)
    a, o = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, gr, b = a[x, y]
            lum = (r * 0.3 + gr * 0.59 + b * 0.11) / 255
            o[x, y] = (round(20 + 60 * lum), round(120 + 130 * lum), round(30 + 70 * lum))
    return out


plain = bg.convert("RGB")
plain.save(HERE / "background.png")
gbg = green(plain)
gbg.save(HERE / "green-background.png")
for name, im in (("start", with_her(g["slopeTop"] + 22, g["upper"], 0)), ("end", with_her(g["slopeFoot"] - 18, g["lower"], 4))):
    im.save(HERE / f"{name}.png")
    out = gbg.copy()
    a, b, o = im.load(), plain.load(), out.load()
    for y in range(H):
        for x in range(W):
            if a[x, y] != b[x, y]:
                o[x, y] = a[x, y]
    out.save(HERE / f"green-{name}.png")
(HERE / "place.json").write_text(json.dumps(dict(x=X0, y=Y0, w=W, h=H)), encoding="utf-8")
print("wrote start, end, green-start, green-end, backgrounds, place.json", (X0, Y0, W, H))
