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
  steam-fan     17: her hair frizzed by the sauna's steam into a huge puff (frame 0 and 8: her puff
                picture, `starts/steam/s17-puff.png`), she fans her face
  steam-swoon   17: from the puff picture she sways, a hand to her forehead, and sits down dazed
  flare-blink   19: singed by Teppanyaki's flare (frame 0 and 8: her soot picture,
                `starts/flare/s19-soot.png`): her face black, her hair on end, singed at the tips; a
                wisp of smoke curls up off her hair, her white eye blinks
  flare-cough   19: from and back to the soot picture, she bends and coughs out a puff of smoke
  stairs-sit    21: a funnel gull's swoop on the stairway: from her standing she sits down hard on the
                step, legs out down the flight (`stairs-bump/sit/`, cut by `stairs-bump/cut.py`)
  stairs-bump   21: one bump on her bottom in place (from and back to the sit's last picture); the
                game plays 3, 5, 7 a step, a step down at 5. Both stand on a step's corner at
                (48, 64): the left edge of column 48, row 64
  stairs-foot   21: the last two steps and off onto the roof's floor, slumped; it stands on the foot
                of the flight at (50, 100). All three face east and descend east (the game flips them)
  stairs-dazed  21's end: slumped at the foot, dizzy, her head wobbling, two butterflies circling over
                it (a loop; stood as the foot's)
  parasol-flip  22: a gull across her glide: frame 0 her glide picture with the open parasol as the game
                draws it, 1 to 3 the parasol blown inside out, 4 to 8 she looks up at it and kicks her
                legs (a loop as she drops); her feet at (56, 112), the left edge of column 56, as her
                own sprite's middle (`parasol-flip/flip/`, cut by `parasol-flip/cut.py`)

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
         ("sprinkler-sneeze", 9), ("sprinkler-walk", 9), ("steam-fan", 9), ("steam-swoon", 9),
         ("flare-blink", 9), ("flare-cough", 9), ("stairs-sit", 6), ("stairs-bump", 9), ("stairs-foot", 7), ("stairs-dazed", 8),
         ("parasol-flip", 9)]
# (Gags 21's and 22's frames are cut from the generator's in a folder of their own.)
PATH = {"stairs-sit": "stairs-bump/sit", "stairs-bump": "stairs-bump/bump", "stairs-foot": "stairs-bump/foot", "stairs-dazed": "stairs-bump/dazed",
        "parasol-flip": "parasol-flip/flip"}
DOOR = {"door-burst", "door-squash", "door-burst-full"}
# (19's soot: its greys fall on the palette's two cool, greenish greys, and her face read as green; they
# go on the charcoal greys of her hair's own family instead. No other colour of hers falls there.)
SOOT = {(49, 54, 56): (62, 53, 70), (55, 78, 74): (98, 85, 101)}


def frame(clip, i):
    im = Image.open(SRC / PATH.get(clip, clip) / f"{i}.png").convert("RGBA")
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
    return palettize(im, SOOT if clip.startswith("flare-") else None)


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
            "sprinkler": {"x": 64, "run": 54},
            "steam": {"x": 64},
            "flare": {"x": 64},
            "stairs": {"corner": [48, 64], "foot": [50, 100]},
            "parasol": {"feet": [56, 112]}}
    (ROOT / "assets" / "sprites" / "gags.json").write_text(json.dumps(meta))
    print(out, sheet.size)


if __name__ == "__main__":
    main()
