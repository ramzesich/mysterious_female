"""Her reading clips (the user, 2026-11-21): seated facing us in the Library's armchairs (the red reading chair and the
six at the reading tables, all the same chair) and sitting up against the pillows on her bed in cabin 8206, each one
PixMiniMax clip from a start picture with the game's own chair or bed in it (`assets/source/her/reading/raw-*`, the
README there has the jobs), then cut out of it by what differs from the start without her (holes she encloses
filled, her figure alone; the wall picture's wisps over her hair dropped), so the game's chair and bed stay as they
are and she is drawn over them.

    python tools/build_reading.py

Writes assets/sprites/reading.png + reading.json: frames `chair-<i>` (68 x 68: the chair's foot on the bottom row,
its middle at column 34) and `bed-<i>` (132 x 100: the cabin picture's columns 108 to 239, rows 28 to 127), each the
whole frame, so the game sets it by its corner; and `heads`, her head in each (for the popups). Her own colours, as
in her sheet.
"""

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "her" / "reading"
OUT = ROOT / "assets" / "sprites"
# (`bed-towel`: the bed's with her towel turban on, after the shower, the frames the game plays; cut by
# `tools/cut_reading.py`, the user, 2026-11-23: the towel went from her hair when she sat to read.)
CLIPS = {"chair": (range(0, 17), (68, 68)), "bed": (range(0, 17), (132, 100)), "bed-towel": (range(0, 10), (132, 100))}
ROW = 2048


def head(im):
    """Her head in a frame, as `tools/build_heads.py` keeps it ([x, y, top]: its middle and its top row), so a popup
    over her while she reads stands over her seated head: the top is her topmost row, the middle the middle of
    her hair's columns in the top five rows, eight rows under the top."""
    a = im.getchannel("A")
    top = next(y for y in range(im.height) if any(a.getpixel((x, y)) for x in range(im.width)))
    cols = [x for y in range(top, top + 5) for x in range(im.width) if a.getpixel((x, y))]
    return [round(sum(cols) / len(cols)), top + 8, top]


def main():
    frames, heads, x, y, row_h = {}, {}, 0, 0, 0
    pieces = []
    for name, (idx, (w, h)) in CLIPS.items():
        for i in idx:
            im = Image.open(SRC / name / f"{i}.png").convert("RGBA")
            assert im.size == (w, h), (name, i, im.size)
            if x + w > ROW:
                x, y, row_h = 0, y + row_h, 0
            pieces.append((im, x, y))
            frames[f"{name}-{i}"] = {"frame": {"x": x, "y": y, "w": w, "h": h}, "sourceSize": {"w": w, "h": h},
                                     "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h}, "rotated": False, "trimmed": False}
            heads[f"{name}-{i}"] = head(im)
            x += w
            row_h = max(row_h, h)
    sheet = Image.new("RGBA", (ROW, y + row_h), (0, 0, 0, 0))
    for im, px, py in pieces:
        sheet.alpha_composite(im, (px, py))
    sheet.save(OUT / "reading.png")
    (OUT / "reading.json").write_text(json.dumps({"frames": frames, "heads": heads, "meta": {"image": "reading.png", "size": {"w": ROW, "h": sheet.height}}},
                                                 indent=1), encoding="utf-8")
    print("wrote", len(frames), "frames to", (OUT / "reading.png").relative_to(ROOT), sheet.size)


if __name__ == "__main__":
    main()
