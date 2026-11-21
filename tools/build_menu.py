"""The welcome screen's menu art (the user, 2026-11-14: "The text looks too plain now", then chose
the brass plates from three mock-ups): its lettering and its plate, to `assets/sprites/menu.png`
and `menu.json` (an atlas the game loads; src/pixeltext.js sets words in it, src/intro.js lays the
menu out).

    python tools/build_menu.py

The sources, in `assets/source/menu/`:
- `PressStart2P-Regular.ttf`, the menu's lettering (the user chose it from five fonts set over the
  menu, 2026-11-21; SIL Open Font License, `OFL.txt` beside it): a pixel font on an 8 px grid with
  its own Ukrainian capitals. It is set here at the sizes where its pixels are the game's: the name
  (`T`) at 16, two art px to one of the font's; the plates' words (`S`) at 8. Only the shapes are
  used: the game gives them their colours, outline and shadow. Every letter is its own frame,
  trimmed to what it draws, its place in the font's cell kept as the frame's trim (src/pixeltext.js
  steps by the cell, as the font does).
- `plates.png`: a generated ship's name plate (`create_ui_asset`, 10 generations), a riveted brass
  frame round navy enamel; the upper of its two, made a little lower by taking rows out over and
  under its middle.

The menu is set in capitals. `font-title.png` and `font-sign.png`, the two generated letterings it
had before (Latin only, the Ukrainian capitals built from their shapes), are kept there but no
longer used.
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from palettize import palettize

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "menu"
OUT = ROOT / "assets" / "sprites"
FONT = SRC / "PressStart2P-Regular.ttf"
# The letters in the atlas: the Latin and Ukrainian capitals, the digits and a few signs.
LETTERS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ" "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ" "0123456789" ".,!?:;'\"-+()/%*=_$’")
# Each lettering: its size (a multiple of the font's 8 px grid) and its frames' names.
SIZES = {"T": 16, "S": 8}
# The plate: where it is in its sheet, and the rows taken out of it (it came 62 px high).
PLATE = {"box": (0, 0, 256, 128), "cut": [(14, 20), (38, 44)]}
# The plate is made three quarters of the size it was drawn at (the user, on seeing the menu in the
# game: "Make the initial menu smaller, but still big. Now it is oversized"): 166 x 38, two screen
# pixels to one in the game.
SCALE = 0.75


def glyphs(size):
    """Every letter at `size`, by its character: its mask trimmed to what it draws, where that is in
    the font's cell (the advance wide, from the top of the capitals to the foot of Д's tail), and the
    cell's size."""
    font = ImageFont.truetype(str(FONT), size)
    cell = (round(font.getlength("H")), size)
    out = {}
    for ch in LETTERS:
        im = Image.new("L", (cell[0] * 2, cell[1] * 2), 0)
        d = ImageDraw.Draw(im)
        d.fontmode = "1"                                           # (no antialiasing: the font's own pixels)
        d.text((0, 0), ch, font=font, fill=255)
        box = im.getbbox()
        assert round(font.getlength(ch)) == cell[0], ch            # (one cell for every letter)
        assert box[2] <= cell[0] + 1 and box[3] <= cell[1], (ch, box)
        out[ch] = (im.crop(box), box[0], box[1], cell)
    return out


def plate():
    sheet = Image.open(SRC / "plates.png").convert("RGBA").crop(PLATE["box"])
    a = sheet.crop(sheet.getbbox())
    keep = [y for y in range(a.height) if not any(lo <= y < hi for lo, hi in PLATE["cut"])]
    out = Image.new("RGBA", (a.width, len(keep)), (0, 0, 0, 0))
    for i, y in enumerate(keep):
        out.paste(a.crop((0, y, a.width, y + 1)), (0, i))
    # Smaller, and back to the game's palette and a hard edge.
    size = (round(out.width * SCALE), round(out.height * SCALE))
    small = palettize(out.resize(size, Image.LANCZOS))
    small.putalpha(out.getchannel("A").resize(size, Image.LANCZOS).point(lambda v: 255 if v > 127 else 0))
    return small


def main():
    pieces = [("plate", plate())]
    trims = {}
    for font, size in SIZES.items():
        for ch, (mask, x, y, cell) in glyphs(size).items():
            white = Image.new("RGBA", mask.size, (255, 255, 255, 0))
            white.putalpha(mask)
            name = f"{font}-{ord(ch):04x}"
            pieces.append((name, white))
            trims[name] = (x, y, cell)
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
        if name in trims:                                       # (a letter: its place in the font's cell)
            tx, ty, (cw, ch) = trims[name]
            frames[name].update(trimmed=True, spriteSourceSize={"x": tx, "y": ty, "w": im.width, "h": im.height},
                                sourceSize={"w": cw, "h": ch})
        x += im.width + 1
        row = max(row, im.height)
    sheet = Image.new("RGBA", (W, y + row), (0, 0, 0, 0))
    for im, px, py in placed:
        sheet.paste(im, (px, py))
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT / "menu.png")
    (OUT / "menu.json").write_text(json.dumps({"frames": frames, "meta": {"image": "menu.png", "size": {"w": sheet.width, "h": sheet.height},
                                                                         "scale": "1"}}), encoding="utf-8")
    print(f"menu.png {sheet.size}: the plate and {len(pieces) - 1} letters")


if __name__ == "__main__":
    main()
