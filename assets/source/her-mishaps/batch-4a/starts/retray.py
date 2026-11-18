"""The tray ride's frames with the breakfast stewardess's tray (the user, 2026-11-18: the flat bars "don't
make any sense"; "a normal-looking tray, like the one that the breakfast lady hangs out to the doors").
The clips were generated on the old flat tray, 24 x 4, its last row on the floor line (row 120): in every
frame where she stands on it, that tray is taken out and she is lowered by the 2 px the stewardess tray's
own base is thinner (`breakfast-tray`'s rows 10 and 11, 24 x 2, things atlas): the world's own base is
moved under her by the game, its left column at `trayAt` (the user, 2026-11-18: landing on it from a
jump she slides too, so the tray is not part of her picture).
Frames where she has not landed yet keep no tray (the world's own lies where it is). Writes
`tray-ride/`, `tray-ride3/`, `tray-ride1/`, `tray-ride5/` (from her run frames 7, 3, 1, 5; the clips on the
old tray are each one's `-flat/`) and prints the base's left
column in each frame (`trayAt` in tools/build_gags.py).

python assets/source/her-mishaps/batch-4a/starts/retray.py"""
import json, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent.parent
OLD = {(0x2e, 0x22, 0x2f), (0xc7, 0xdc, 0xd0), (0xff, 0xff, 0xff)}


def base():
    atlas = Image.open(ROOT / "assets/sprites/things.png").convert("RGBA")
    meta = json.load(open(ROOT / "assets/sprites/things.json"))
    f = meta.get("frames", meta)["breakfast-tray"]["frame"]
    return atlas.crop((f["x"], f["y"] + 10, f["x"] + 24, f["y"] + 12))


def old_tray(im):
    """The old tray's left column, if she stands on it: a run of 20 or more of its dark outline on its
    bottom row, 120 (her shoes on it may cover its top rows); else of its colours on row 119 (one clip
    drew its bottom row otherwise)."""
    px = im.load()
    for row, ok in ((120, lambda c: c == (0x2e, 0x22, 0x2f)), (119, lambda c: c in OLD)):
        run = 0
        for x in range(im.width):
            if px[x, row][3] and ok(px[x, row][:3]):
                run += 1
                if run >= 20:
                    return x - run + 1
            else:
                run = 0
    return None


def retray(src, out, n=9):
    b = base()
    out.mkdir(exist_ok=True)
    at = []
    for i in range(n):
        im = Image.open(src / f"{i}.png").convert("RGBA")
        left = old_tray(im)
        if left is None or i < 2:
            # (Not landed yet: no tray in the frame at all.)
            px = im.load()
            for y in range(116, 121):
                for x in range(im.width):
                    if px[x, y][3] and px[x, y][:3] in OLD and (left is None or left - 1 <= x <= left + 25):
                        px[x, y] = (0, 0, 0, 0)
            im.save(out / f"{i}.png")
            at.append(left)
            continue
        her = im.copy()
        hp = her.load()
        for y in range(117, 121):
            for x in range(left - 1, min(im.width, left + 26)):
                hp[x, y] = (0, 0, 0, 0)
        new = Image.new("RGBA", im.size)
        new.alpha_composite(her.crop((0, 0, im.width, 117)), (0, 2))
        new.alpha_composite(her.crop((0, 117, im.width, im.height)), (0, 117))
        # (The base itself is the world's, moved under her by the game: `trayAt`.)
        new.save(out / f"{i}.png")
        at.append(left)
    print(out.name, at)


if __name__ == "__main__":
    # (From her run frames 7, 3, 1 and 5: `tray-ride` is frame 7's.)
    for n in (7, 3, 1, 5):
        name = "tray-ride" if n == 7 else f"tray-ride{n}"
        retray(HERE / f"{name}-flat", HERE / name)
