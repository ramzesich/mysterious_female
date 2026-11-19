"""The "Do Not Disturb" hanger on a cabin door's lever (the user, 2026-11-19: "The sign should hang from the door
handle, have a half round top and in the middle of the sign it should have visible red circle, crossed"). Drawn by
hand pixel by pixel (a pictogram of 11 x 22 px, below what a generation draws exactly), on the palette.
`hanger.png`: the sign alone; `door-cabin-dnd.png`: the cabin door with it, the lever seen through its hole; both
copied to `assets/ship/` (`dnd-hanger.png`, `door-cabin-dnd.png`), which the game loads (the "Do Not Disturb"
doors, `DndDoor`; the occupied balconies' partitions, `Occupied`). Then `swing.py`, and `tools/build_gags.py`.
Its hole hangs on the lever where it is mounted (the user, 2026-11-19: "It cannot hang from the tip of the door
handle"): the rose, the door's columns 7 to 9, the bar on row 39 resting at the hole's top; the lever is drawn in
front of the sign."""
import sys
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
O, W, R, T, G = (46, 34, 47), (255, 255, 255), (232, 59, 59), (98, 85, 101), (199, 220, 208)
SLASH = sys.argv[1] if len(sys.argv) > 1 else "2"
ROWS = [
    "...OOOOO...",
    ".OOWWWWWOO.",
    ".OWWOOOWWO.",
    "OWWO...OWWO",
    "OWWO...OWWO",
    "OWWO...OWWO",
    "OWWWOOOWWWO",
    "OWWWWWWWWWO",
    "OWW..R..WWO",   # (the circle's rows are filled below)
    "OW.......WO",
    "OW.......WO",
    "OW.......WO",
    "OW.......WO",
    "OW.......WO",
    "OW.......WO",
    "OWWWWWWWWWO",
    "OWWWWWWWWWO",
    "OWTTTTTTTWO",
    "OWWWWWWWWWO",
    "OWWTTTTTWWO",
    "OWWWWWWWWWO",
    ".OOOOOOOOO.",
]
CIRCLE = ["..RRR..",
          ".R...R.",
          "R.....R",
          "R.....R",
          "R.....R",
          ".R...R.",
          "..RRR.."]
TOP, LEFT = 36, 4          # the door's row and column of the sign's top left
# (The lever, the door's own pixels: its rose where it is mounted, columns 7 to 9, and its bar to column 14.)
LEVER = [(x, 38) for x in range(8, 14)] + [(x, 39) for x in range(7, 15)] + [(x, 40) for x in range(8, 14)] + [(8, 41), (9, 41)]
HOLE = [(c, r) for r, row in enumerate(ROWS) for c, ch in enumerate(row) if ch == "." and 2 <= r <= 5 and 3 < c < 7]

def hanger():
    im = Image.new("RGBA", (11, len(ROWS)))
    px = im.load()
    for r, row in enumerate(ROWS):
        for c, ch in enumerate(row):
            if ch in "OWTG": px[c, r] = (*{"O": O, "W": W, "T": T, "G": G}[ch], 255)
    for r in range(7):
        for c in range(7):
            x, y = 2 + c, 8 + r
            px[x, y] = (*W, 255)
            if CIRCLE[r][c] == "R" or (1 <= c <= 5 and c == r) or (SLASH == "2" and 1 <= c <= 5 and c == r + 1):
                px[x, y] = (*R, 255)
    return im

if __name__ == "__main__":
    h = hanger()
    h.save(HERE / "hanger.png")
    door = Image.open(HERE / "door-cabin.png").convert("RGBA")
    out = door.copy()
    out.alpha_composite(h, (LEFT, TOP))
    # (The lever through the hole: the door's own pixels there.)
    for c, r in HOLE:
        out.putpixel((LEFT + c, TOP + r), door.getpixel((LEFT + c, TOP + r)))
    # (The lever in front of the sign, through its hole.)
    for x, y in LEVER:
        c = door.getpixel((x, y))
        if c[3]:
            out.putpixel((x, y), c)
    out.save(HERE / "door-cabin-dnd.png")
    out.save(ROOT / "assets" / "ship" / "door-cabin-dnd.png")
    h.save(ROOT / "assets" / "ship" / "dnd-hanger.png")
