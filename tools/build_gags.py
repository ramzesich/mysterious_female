"""Step 4a's first batch of gags (2026-11-18): `assets/sprites/gags.png`, cells of 128 px, one row per
clip, and `gags.json` (each clip's cells, and where the game stands each one). From
`assets/source/her-mishaps/batch-4a/` (its README has the PixelLab ids and what was fixed by hand).
Every frame: the floor under row 120 (the world's `y` is the canvas row 121).

  door-burst    13a's door alone: shut, bursting open toward us, flat against the wall, slammed
                shut (frame 0 and 12: the world's shut door itself). The door's middle at x 40
  door-squash   13a: the same with her standing 30 px past it, slammed flat against the wall under
                the leaf, then left flat on the wall facing us; the door's middle at x 40
  door-slide    13a's end: she slides down the wall and sits (her alone; the world's shut door)
  tray-ride     3: from her run frame 7 she hops onto the tray and rides it, arms wheeling; her
                middle at x 52 in frame 0. Under her the breakfast stewardess tray's own base
                (`starts/retray.py`), none in frames 0 and 1 (the world's tray lies where it is until
                she lands); `trayAt`: the base's left column in each frame
  tray-ride3, tray-ride1, tray-ride5   3: the same from her run frames 3, 1 and 5: one start each
                quarter of her stride, so that the tray is always within a short hop
  chair-collapse 7b: from her slip frame 0 the deck chair takes her behind the knees, she sits,
                it collapses flat under her; her middle at x 64, the chair's at 46
  gull-flail    20: the world's gull landed on her head; she flails, breaks into a run; her middle
                at x 54
  gull-run      20: running off flailing, the gull on her head (a loop; frame 0 = flail's 8)
  door-burst-full  the same swing as door-burst in the full-colour door's own colours (the muting taken
                back out, exactly: `starts/fullcolour.py`): a "Do Not Disturb" door opening on the
                guest and shutting (the user, 2026-11-18: it vanished with its frame)
  sprinkler-stand  16: from her standing frame, drenched: she flinches, her hair falls flat over her
                face (frame 8: her soaked picture, `starts/sprinkler/wet-9b13cff9-...png`); her middle
                at x 64
  sprinkler-run1, -run3, -run5, -run7  16: the same from her run frames 1, 3, 5 and 7 (her middle at
                x 54 in frame 0): she stops short in two steps, ending on the soaked picture at x 64
  sprinkler-sneeze  16: soaked, a sneeze (from and back to the soaked picture)
  sprinkler-walk  16: soaked, squelching off, a walk loop on the spot (the game moves her)

The door's clips keep their colours (the world's muted shut door is not on the palette, and the
leaf is drawn in its colours): only her pixels are put on the palette there.

python tools/build_gags.py"""
import json
from pathlib import Path
from PIL import Image
from palettize import palettize

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "her-mishaps" / "batch-4a"
CELL, COLS = 128, 13
CLIPS = [("door-burst", 13), ("door-squash", 13), ("door-slide", 9), ("tray-ride", 9), ("tray-ride3", 9), ("tray-ride1", 9), ("tray-ride5", 9),
         ("chair-collapse", 9), ("gull-flail", 9), ("gull-run", 9), ("door-burst-full", 13),
         ("sprinkler-stand", 9), ("sprinkler-run1", 9), ("sprinkler-run3", 9), ("sprinkler-run5", 9), ("sprinkler-run7", 9),
         ("sprinkler-sneeze", 9), ("sprinkler-walk", 9)]
DOOR = {"door-burst", "door-squash", "door-burst-full"}


def frame(clip, i):
    im = Image.open(SRC / clip / f"{i}.png").convert("RGBA")
    if clip == "door-slide":
        # (Her flattened picture's canvas is 96 px: set beside the door as the squash's last frame.)
        c = Image.new("RGBA", (CELL, CELL))
        c.alpha_composite(im, (33, 40))
        im = c
    if clip == "door-squash" and i == 1:
        # (Her own sprite is shown until the leaf covers her, frame 2: she is taken out of frame 1, the
        # leaf ending at column 56 and she starting at 59.)
        px = im.load()
        for y in range(CELL):
            for x in range(57, CELL):
                px[x, y] = (0, 0, 0, 0)
    if clip in DOOR:
        shut = Image.open(SRC / ("door-burst-full" if clip == "door-burst-full" else "door-burst") / "0.png").convert("RGBA")
        keep = set(p[:3] for p in shut.getdata() if p[3]) | {(233, 223, 204)}
        pal = palettize(im)
        a, b = im.load(), pal.load()
        for y in range(CELL):
            for x in range(CELL):
                if a[x, y][3] and a[x, y][:3] not in keep:
                    a[x, y] = b[x, y]
        return im
    return palettize(im)


def main():
    sheet = Image.new("RGBA", (CELL * COLS, CELL * len(CLIPS)))
    anims = {}
    for r, (clip, n) in enumerate(CLIPS):
        anims[clip] = []
        for i in range(n):
            sheet.alpha_composite(frame(clip, i), (i * CELL, r * CELL))
            anims[clip].append(r * COLS + i)
    out = ROOT / "assets" / "sprites" / "gags.png"
    sheet.save(out)
    meta = {"cell": CELL, "floor": 121, "anims": anims,
            "door": {"x": 40, "her": 30, "zone": [22, 38]},
            "tray": {"x": 52, "clips": {"7": {"key": "tray-ride", "toe": 8, "trayAt": [62, 62, 64, 60, 57, 55, 53, 51, 49]},
                                        "3": {"key": "tray-ride3", "toe": 6, "trayAt": [60, 60, 62, 60, 59, 58, 57, 56, 55]},
                                        "1": {"key": "tray-ride1", "toe": 12, "trayAt": [66, 64, 63, 61, 59, 58, 56, 54, 53]},
                                        "5": {"key": "tray-ride5", "toe": 13, "trayAt": [67, 67, 67, 67, 66, 64, 62, 59, 57]}}},
            "chair": {"x": 64, "chair": 46},
            "gull": {"x": 54},
            "sprinkler": {"x": 64, "run": 54}}
    (ROOT / "assets" / "sprites" / "gags.json").write_text(json.dumps(meta))
    print(out, sheet.size)


if __name__ == "__main__":
    main()
