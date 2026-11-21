"""The lifeboat's roof hatch (the boat walkway, deck 7; the user, 2026-11-21: "Remove the door. Make a hatch on top of the
boat, front end. Make a new animation where she crawls up the boat into the hatch", "from behind the boat"; the frames
approved together as one GIF):

- the hatch, inpainted into the game's own picture of the lifeboat just aft of its forward hook (a wide one seen a little
  from above, try 2 of two), its lid taken off ("Remove the lid from the hatch": its rows the boat's own again, a far rim
  mended in the hatch's own colours), cut by what changed into its back (the far rim and the dark opening, behind her)
  and its front (the near lip, over her): `assets/source/things/lifeboat-hatch-back.png`, `-front.png` (the things
  atlas, `tools/build_things.py`), from `assets/source/ship/lifeboat-door/nolid*.png`;
- her pull-up over the hatch's far rim, facing us (the walkway is behind the boat: she climbs its far side), a clip of
  her own character (skeleton-v3, poses written for it: `assets/source/her/mantle-front/`, PixelLab animation
  "mantle-front"), to `assets/sprites/mantle-front.png` + `.json` (96 px cells); `hands`: each frame's lowest row of her
  hands, which the game holds on the far rim. The rest of the climb is her own sheet's frames: front, side, back on the
  roof, her back frame in the opening, `climb-out` 74, 73, 72 sinking in (the ship scene's `roofClimb`, `ROOF`).
  (A generated clip of the whole climb, and her ladder clips, tried first, broke at every joint or held the air:
  `assets/source/ship/lifeboat-door/raw-*`, dropped.)
    python tools/build_hatch.py
"""
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "her" / "mantle-front"
OUT = ROOT / "assets" / "sprites"
CELL = 96
X = 48                       # her middle column in the clip's cells
HANDS = [34, 34, 38, 46, 54, 55]   # each frame's lowest row of her hands (measured: her skin's outermost pixels)


def build():
    frames = [Image.open(SRC / f"{i}.png").convert("RGBA") for i in range(len(HANDS))]
    sheet = Image.new("RGBA", (CELL * len(frames), CELL), (0, 0, 0, 0))
    for n, img in enumerate(frames):
        assert img.size == (CELL, CELL), (n, img.size)
        sheet.alpha_composite(img, (n * CELL, 0))
    sheet.save(OUT / "mantle-front.png")
    meta = {"cell": CELL, "x": X, "hands": HANDS}
    (OUT / "mantle-front.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"wrote assets/sprites/mantle-front.png ({sheet.width} x {sheet.height}, {len(frames)} frames) and mantle-front.json")


if __name__ == "__main__":
    build()
