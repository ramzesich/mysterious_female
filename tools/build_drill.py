"""The boat drill's own clips (the walkway, deck 7; the user, 2026-11-21) to `assets/sprites/drill.png` + `drill.json`:

- the winch's crewman at his winch, one picture of the two (`assets/source/people/drill_winch-raw/`: try 2 of an edit of his
  standing frame, then PixMiniMax's clip B of him turning its handwheel, 8 frames, its ninth the first again), played
  forward while the boat is lowered, backward while it is hoisted, its first frame held otherwise (`DrillBoat`);
- her gag under the boat (15, `GAGS.boat`, the ship scene's `crawlGag`): bumped on the head as she runs, she sinks onto
  all fours, dizzy, the butterflies over her head (`drop`, try 3; its frame 0 is her own run frame), then crawls on
  all fours, the butterflies circling (`crawl`, a loop) out from under it (`assets/source/her-mishaps/boat-crawl/`).

Every frame in its own colours, as generated (as her reading clips, tools/build_reading.py): on the palette her hair went
black, her blouse took cyan spots and her far limbs went brown. In 96 px cells, one row. `heads`: her head in each of her frames ([x, y, top], as
`tools/build_heads.py` keeps them), the butterflies left out, for her popup ("Bumped!") over it.
    python tools/build_drill.py
"""
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "sprites"
CELL = 96
CLIPS = {
    "winch": (ROOT / "assets" / "source" / "people" / "drill_winch-raw" / "turn-b", range(8)),
    "drop": (ROOT / "assets" / "source" / "her-mishaps" / "boat-crawl" / "raw-drop3", range(9)),
    "crawl": (ROOT / "assets" / "source" / "her-mishaps" / "boat-crawl" / "raw-crawl", range(8)),
}
HER = ("drop", "crawl")
# Her middle column and her floor row in her cells (her run frame was set at (22, 16) of the cell, its 64 px frame's
# middle at 32 and its feet on row 61); the crewman's middle column and his floor row in his.
HER_X, HER_FLOOR = 54, 77
WINCH_X, WINCH_FLOOR = 26, 95
# Where the wire rope leaves the drum's top for the ceiling (src/wire.js; the user, 2026-11-21): column, row.
ROPE_X, ROPE_Y = 66, 56


def butterfly(p):
    r, g, b, a = p
    return a and r > 100 and b < 70 and g > 80


def head(img):
    """Her head's middle and its top, from her own pixels (not the butterflies')."""
    px = img.load()
    rows = [(x, y) for y in range(img.height) for x in range(img.width) if px[x, y][3] and not butterfly(px[x, y])]
    top = min(y for _, y in rows)
    near = [x for x, y in rows if y <= top + 6]
    return [round(sum(near) / len(near)), top + 7, top]


def build():
    frames, meta = [], {"cell": CELL, "herX": HER_X, "herFloor": HER_FLOOR, "winchX": WINCH_X, "winchFloor": WINCH_FLOOR,
                        "ropeX": ROPE_X, "ropeY": ROPE_Y,
                        "heads": {}}
    for name, (folder, idx) in CLIPS.items():
        meta[name] = []
        for i in idx:
            img = Image.open(folder / f"{i}.png").convert("RGBA")
            assert img.size == (CELL, CELL), (name, i, img.size)
            n = len(frames)
            meta[name].append(n)
            if name in HER:
                meta["heads"][str(n)] = head(img)
            frames.append(img)
    sheet = Image.new("RGBA", (CELL * len(frames), CELL), (0, 0, 0, 0))
    for n, img in enumerate(frames):
        sheet.alpha_composite(img, (n * CELL, 0))
    OUT.mkdir(exist_ok=True)
    sheet.save(OUT / "drill.png")
    (OUT / "drill.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"wrote assets/sprites/drill.png ({sheet.width} x {sheet.height}, {len(frames)} frames) and drill.json")


if __name__ == "__main__":
    build()
