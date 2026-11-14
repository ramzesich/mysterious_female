"""The welcome screen's menu art (the user, 2026-11-14: "The text looks too plain now", then chose
the brass plates from three mock-ups): its lettering and its plate, to `assets/sprites/menu.png`
and `menu.json` (an atlas the game loads; src/pixeltext.js sets words in it, src/intro.js lays the
menu out).

    python tools/build_menu.py

The sources, in `assets/source/menu/`, are PixelLab's:
- `font-title.png` (cells of 32) and `font-sign.png` (cells of 16): two generated pixel letterings
  (`create_font`, 15 generations each), each an atlas of 80 glyphs, eight to a row, in the order
  `ORDER`. Only the shapes are used: the game gives them their colours, outline and shadow.
- `plates.png`: a generated ship's name plate (`create_ui_asset`, 10 generations), a riveted brass
  frame round navy enamel; the upper of its two, made a little lower by taking rows out over and
  under its middle.

**The lettering is Latin only, and the game is in Ukrainian too:** the Ukrainian capitals the menu
needs are built here from the Latin ones, so both languages are in one hand. Thirteen are the same
shape (А В Е І К М Н О Р С Т У Х from A B E I K M H O P C T Y X); Г is L turned upside down, И is N
mirrored, Ь is P upside down, Б is that with E's top bar, Ї is I with two dots, З is 3, Я is R
mirrored. The menu is set in capitals for that reason. A word with a letter not here is left
without it, and the `lang` playtest says so.
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "menu"
OUT = ROOT / "assets" / "sprites"
ORDER = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?:;'\"-+()0123456789/%*=_$"
SAME = dict(zip("АВЕІКМНОРСТУХ", "ABEIKMHOPCTYX"))
# The plate: where it is in its sheet, and the rows taken out of it (it came 58 px high).
PLATE = {"box": (0, 0, 256, 128), "cut": [(14, 20), (38, 44)]}


def glyphs(path, cell):
    """Every glyph of a lettering as a mask a cell high, by its character: the atlas's own and
    the Ukrainian capitals made from them."""
    atlas = Image.open(path).convert("RGBA")
    g = {}
    for i, ch in enumerate(ORDER):
        box = ((i % 8) * cell, (i // 8) * cell, (i % 8 + 1) * cell, (i // 8 + 1) * cell)
        g[ch] = atlas.crop(box).getchannel("A").point(lambda v: 255 if v > 127 else 0)
    top, bottom = g["H"].getbbox()[1], g["H"].getbbox()[3]          # the capitals' rows
    stroke = max(2, round(cell / 7))

    def upside_down(m):
        out = Image.new("L", (cell, cell), 0)
        out.paste(m.crop((0, top, cell, bottom)).transpose(Image.FLIP_TOP_BOTTOM), (0, top))
        return out

    for cyr, lat in SAME.items():
        g[cyr] = g[lat]
    g["Г"] = upside_down(g["L"])
    g["И"] = g["N"].transpose(Image.FLIP_LEFT_RIGHT)
    g["Я"] = g["R"].transpose(Image.FLIP_LEFT_RIGHT)
    g["З"] = g["3"]
    g["Ь"] = upside_down(g["P"])
    be = g["Ь"].copy()                                             # Б: Ь under E's top bar
    be.paste(255, (0, top), g["E"].crop((0, top, cell, top + stroke + 1)))
    g["Б"] = be
    yi = g["I"].copy()                                             # Ї: I, shorter, two dots over it
    d = ImageDraw.Draw(yi)
    box = g["I"].getbbox()
    dot = max(2, cell // 8)
    d.rectangle([0, 0, cell, top + dot + max(1, dot // 2)], fill=0)
    mid = (box[0] + box[2]) / 2
    for side in (-1, 1):
        x0 = round(mid + side * (dot * 0.5 + 1) - dot / 2)
        d.rectangle([x0, top, x0 + dot - 1, top + dot - 1], fill=255)
    g["Ї"] = yi
    return {ch: m for ch, m in g.items() if m.getbbox()}


def plate():
    sheet = Image.open(SRC / "plates.png").convert("RGBA").crop(PLATE["box"])
    a = sheet.crop(sheet.getbbox())
    keep = [y for y in range(a.height) if not any(lo <= y < hi for lo, hi in PLATE["cut"])]
    out = Image.new("RGBA", (a.width, len(keep)), (0, 0, 0, 0))
    for i, y in enumerate(keep):
        out.paste(a.crop((0, y, a.width, y + 1)), (0, i))
    return out


def main():
    pieces = [("plate", plate())]
    for font, name, cell in (("T", "font-title.png", 32), ("S", "font-sign.png", 16)):
        for ch, mask in glyphs(SRC / name, cell).items():
            box = mask.getbbox()
            white = Image.new("RGBA", (box[2] - box[0], cell), (255, 255, 255, 0))
            white.putalpha(mask.crop((box[0], 0, box[2], cell)))
            pieces.append((f"{font}-{ord(ch):04x}", white))
    # Packed in rows, a pixel between pieces.
    W, x, y, row = 512, 0, 0, 0
    frames = {}
    placed = []
    for name, im in pieces:
        if x + im.width > W:
            x, y, row = 0, y + row + 1, 0
        placed.append((im, x, y))
        frames[name] = {"frame": {"x": x, "y": y, "w": im.width, "h": im.height}, "rotated": False, "trimmed": False,
                        "spriteSourceSize": {"x": 0, "y": 0, "w": im.width, "h": im.height},
                        "sourceSize": {"w": im.width, "h": im.height}}
        x += im.width + 1
        row = max(row, im.height)
    sheet = Image.new("RGBA", (W, y + row), (0, 0, 0, 0))
    for im, px, py in placed:
        sheet.paste(im, (px, py))
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT / "menu.png")
    (OUT / "menu.json").write_text(json.dumps({"frames": frames, "meta": {"image": "menu.png", "size": {"w": sheet.width, "h": sheet.height},
                                                                         "scale": "1"}}), encoding="utf-8")
    print(f"menu.png {sheet.size}: the plate and {len(pieces) - 1} glyphs")


if __name__ == "__main__":
    main()
