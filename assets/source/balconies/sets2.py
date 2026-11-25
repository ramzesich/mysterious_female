"""The sets of the climb's two parts (the user, 2026-11-25, of the first clips: "Look carefully how she transitions from
behind the balcony glass to in front of it": she was on the partition's line with her feet still on the balcony's floor,
and came in at the floor's height at the top). She first gets up onto the rail, a foot each side of the fin (the perch);
she climbs from perch to perch; she comes in off the rail.  python assets/source/balconies/sets2.py <base.png> <vx> <vy>

  sets/mount-start.png   = sets/up-start.png (stood inside, at the partition, deck 9)
  sets/perch-low.png     the perch on deck 9's rail: a frame of the first climb (tries/up-2, frame 9), her lowest row
                         1 px over the rail's cap
  sets/perch-high.png    the same on deck 10's rail
"""
import json, sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sets import green, PART, F9, F10

RAIL = 32
PERCH = ("up-2", 9)


def main():
    base, vx, vy = Image.open(sys.argv[1]).convert("RGB"), int(sys.argv[2]), int(sys.argv[3])
    box = json.loads((HERE / "sets/boxes.json").read_text())
    bx, by, w, h = box["up"]
    her = Image.open(HERE / "tries" / PERCH[0] / f"cut-{PERCH[1]:02d}.png").convert("RGBA")
    bb = her.getbbox()
    fig = her.crop(bb)
    cx = round(PART - (bb[2] - bb[0]) / 2)          # her middle on the partition's
    for name, floor in (("perch-low", F9), ("perch-high", F10)):
        im = green(base.crop((bx - vx, by - vy, bx - vx + w, by - vy + h))).convert("RGBA")
        top = floor - RAIL - 1 - (bb[3] - bb[1]) + 1                 # her lowest row at floor - 33
        im.alpha_composite(fig, (cx - bx, top - by))
        im.convert("RGB").save(HERE / "sets" / f"{name}.png")
    fig.save(HERE / "sets/perch.png")
    json.dump(dict(w=bb[2] - bb[0], h=bb[3] - bb[1], x=cx - PART), open(HERE / "sets/perch.json", "w"))
    print("wrote the perch's sets", fig.size)


if __name__ == "__main__":
    main()


def stood():
    """sets/stood-low.png: stood on deck 9's rail on her own side of the partition, a hand on it (her wall slide's frame):
    the mount in two parts, so that she is not on the partition's line before her feet are on the rail."""
    base, vx, vy, sheet = Image.open(sys.argv[1]).convert("RGB"), int(sys.argv[2]), int(sys.argv[3]), Image.open(sys.argv[4]).convert("RGBA")
    meta = json.loads((HERE.parents[2] / "assets/sprites/her.json").read_text(encoding="utf8"))
    n, cols = meta["anims"]["wallslide"][1], meta["cols"]
    fig = sheet.crop(((n % cols) * 84, (n // cols) * 84, (n % cols + 1) * 84, (n // cols + 1) * 84))
    box = json.loads((HERE / "sets/boxes.json").read_text())
    bx, by, w, h = box["up"]
    im = green(base.crop((bx - vx, by - vy, bx - vx + w, by - vy + h))).convert("RGBA")
    im.alpha_composite(fig, (PART - 12 - 42 - bx, F9 - RAIL - 1 - 84 + 1 - by))
    im.convert("RGB").save(HERE / "sets/stood-low.png")
    print("wrote stood-low")


if __name__ == "__main__" and len(sys.argv) > 4:
    stood()
