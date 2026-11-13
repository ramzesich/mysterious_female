"""Pictures for checking the people against her (the user, 2026-11-13: everyone to one standard of
proportions, see tools/cast.py), from the built sheet assets/sprites/people.png. They are written to
%TEMP%/bumbusik-playtest/.

    python tools/check_people.py [name ...]           everyone (or those named) standing next to her, x3
    python tools/check_people.py --heads name ...     heads x6 against a ruler: a line every 4 px, the bold one at 16
    python tools/check_people.py --clips name ...     every clip of each, its frames in a row, x3

What to look for: a head (hair in, hats and buns out) of 14 to 20 px on a standing figure about
60 px tall (hers: 17 of 59); a seated figure's head at about her shoulder (seated ones are shrunk
with "scale": 0.8 in the cast); in the clips, a head that swells or a body that changes build.
"""

import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("TEMP", "/tmp")) / "bumbusik-playtest"
SKY = (150, 190, 220)
LINE = (120, 160, 190)


def load():
    meta = json.loads((ROOT / "assets" / "sprites" / "people.json").read_text(encoding="utf-8"))
    sheet = Image.open(ROOT / "assets" / "sprites" / "people.png").convert("RGBA")
    hers = json.loads((ROOT / "assets" / "sprites" / "her.json").read_text(encoding="utf-8"))
    her_sheet = Image.open(ROOT / "assets" / "sprites" / "her.png").convert("RGBA")
    f = hers["frames"]["stand"]
    f = f[0] if isinstance(f, list) else f
    c = hers["cell"]
    n = her_sheet.width // c
    her = her_sheet.crop(((f % n) * c, (f // n) * c, (f % n) * c + c, (f // n) * c + c))
    # (On a cell as big as the people's, her feet on its bottom row.)
    cell = Image.new("RGBA", (meta["cell"], meta["cell"]), (0, 0, 0, 0))
    cell.alpha_composite(her.crop((c // 2 - 40, c - 80, c // 2 + 40, c)))
    return meta, sheet, cell


def frame(meta, sheet, i):
    c, cols = meta["cell"], meta["cols"]
    return sheet.crop(((i % cols) * c, (i // cols) * c, (i % cols) * c + c, (i // cols) * c + c))


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name)
    print(OUT / name, img.size)


def standing(names):
    meta, sheet, her = load()
    zoom, w, h, per, rows = 3, 46, 66, 14, 4
    c = meta["cell"]

    def cut(img):
        box = img.getbbox()
        mid = (box[0] + box[2]) // 2
        return img.crop((mid - w // 2, c - h, mid + w // 2, c))

    lines = [["HER"] + names[k:k + per - 1] for k in range(0, len(names), per - 1)]
    for page in range(0, len(lines), rows):
        part = lines[page:page + rows]
        out = Image.new("RGB", (per * w * zoom, len(part) * (h * zoom + 12)), SKY)
        d = ImageDraw.Draw(out)
        for r, line in enumerate(part):
            y0 = r * (h * zoom + 12)
            # Her top, her chin (17 px down), her middle.
            for y in (h - 59, h - 59 + 17, h - 30):
                d.line([(0, y0 + y * zoom), (out.width, y0 + y * zoom)], fill=LINE)
            for k, name in enumerate(line):
                img = cut(her if name == "HER" else frame(meta, sheet, meta["people"][name]["stand"]))
                img = img.resize((img.width * zoom, img.height * zoom), Image.NEAREST)
                out.paste(img, (k * w * zoom, y0), img)
                d.text((k * w * zoom + 2, y0 + h * zoom), name[:20], fill=(0, 0, 0))
        save(out, f"cast-{page // rows}.png")


def heads(names):
    meta, sheet, her = load()
    zoom, w, h, per = 6, 40, 34, 8
    names = ["HER"] + names
    lines = [names[k:k + per] for k in range(0, len(names), per)]
    out = Image.new("RGB", (per * w * zoom, len(lines) * (h * zoom + 14)), SKY)
    d = ImageDraw.Draw(out)
    for r, line in enumerate(lines):
        y0 = r * (h * zoom + 14)
        for k, name in enumerate(line):
            img = her if name == "HER" else frame(meta, sheet, meta["people"][name]["stand"])
            box = img.getbbox()
            mid = (box[0] + box[2]) // 2
            img = img.crop((mid - w // 2, box[1], mid + w // 2, box[1] + h))
            img = img.resize((img.width * zoom, img.height * zoom), Image.NEAREST)
            out.paste(img, (k * w * zoom, y0), img)
            d.text((k * w * zoom + 2, y0 + h * zoom + 1), f"{name}  {box[3] - box[1]} tall", fill=(0, 0, 0))
        for k in range(0, h, 4):
            d.line([(0, y0 + k * zoom), (out.width, y0 + k * zoom)], fill=(255, 255, 0) if k == 16 else LINE,
                   width=2 if k == 16 else 1)
    save(out, "cast-heads.png")


def clips(names):
    meta, sheet, her = load()
    zoom, c = 3, meta["cell"]
    for name in names:
        entry = meta["people"][name]
        rows = [("stand", [entry["stand"]])] + sorted(entry["anims"].items())
        width = 1 + max(len(f) for _, f in rows)
        out = Image.new("RGB", (width * c * zoom, len(rows) * (c * zoom + 12)), SKY)
        d = ImageDraw.Draw(out)
        for r, (clip, frames) in enumerate(rows):
            y0 = r * (c * zoom + 12)
            for y in (c - 59, c - 59 + 17):
                d.line([(0, y0 + y * zoom), (out.width, y0 + y * zoom)], fill=LINE)
            for k, img in enumerate([her] + [frame(meta, sheet, i) for i in frames]):
                img = img.resize((c * zoom, c * zoom), Image.NEAREST)
                out.paste(img, (k * c * zoom, y0), img)
            d.text((2, y0 + c * zoom), f"{name}: {clip}", fill=(0, 0, 0))
        save(out, f"cast-clips-{name}.png")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--heads" in sys.argv:
        heads(args)
    elif "--clips" in sys.argv:
        clips(args)
    else:
        standing(args or list(load()[0]["people"]))
