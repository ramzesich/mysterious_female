"""The Library's "QUIET PLEASE" rope stand going over (deck 6, near-catch 2; remade 2026-11-24,
docs/near-catch-2-remake-log.md): its fall's frames, from assets/source/quiet/gen/ (its README has the jobs) into
assets/ship/quiet/.

    python tools/build_quiet.py

- `stand-fall.png`: a row of frames of the picture the fall was made in (96 x 64, the stand's left column at 15, the
  floor's line at row 52). The clip's frame 0 is the game's own stand standing, so it is not in the sheet; its last
  frame is what lies in the doorway afterwards, each post a quarter turn of its own pixels.
  **The posts** are cut out of PixMiniMax's frames (from the game's stand to that end picture, in the game's own
  picture of the place): what differs from the bare place and is nearer one of the posts' own six colours than the
  place's pixel there, set to that colour, and kept only along each post's own axis (its brass pixels' two ends),
  which drops the smears the generator left on the wall where the posts had stood.
  **The rope** is drawn by rule in its own two colours from ring to ring (a ring is 5 px down a post from its top),
  hanging as it hung and onto the floor at the end: a line whose ends move is not left to the generator (it came in
  pieces).
- `quiet.json`: where a frame stands, how many there are, the frame at which the aft post is into the door.

The stand's card is the game's own (src/signs.js), moved by the scene.
"""
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "quiet" / "gen"
OUT = ROOT / "assets" / "ship" / "quiet"

STAND_X, FLOOR = 15, 52             # in the fall's picture: the stand's left column, the first row under it
USE = [(2, 5), (3, 5), (4, 6), (5, 7), (6, 9)]      # (generated frame, the rope's sag there); frame 1 smeared its rope
END_SAG = 9
DOOR_FRAME = 3                      # of the sheet's frames, from 0: the aft post's top is past the door's face (column 54)
OUTL, DARK = (0x4c, 0x3e, 0x24), (0x2e, 0x22, 0x2f)
BRASS = [(0xfb, 0xb9, 0x54), (0xe6, 0x90, 0x4e), (0xfd, 0xcb, 0xb0), (0xcd, 0x68, 0x3d)]
ROPE, ROPE_D = (0x7a, 0x30, 0x45), (0x6e, 0x27, 0x27)
COLS = [OUTL, DARK] + BRASS


def d2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def seg_dist(p, a, b):
    (ax, ay), (bx, by), (px, py) = a, b, p
    L = (bx - ax) ** 2 + (by - ay) ** 2
    t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / L)) if L else 0
    return math.hypot(px - (ax + t * (bx - ax)), py - (ay + t * (by - ay))), t


def posts(im, bare):
    """The two posts' pixels {(x, y): colour}, and each one's base and top."""
    im = im.convert("RGB")
    cand = {}
    for y in range(im.height):
        for x in range(im.width):
            p, q = im.getpixel((x, y)), bare.getpixel((x, y))
            if d2(p, q) < 500:
                continue
            c = min(COLS, key=lambda c: d2(p, c))
            if d2(p, c) < d2(p, q) and d2(p, c) < 3000:
                cand[(x, y)] = c
    brass = [k for k, c in cand.items() if c in BRASS]

    def spread(g):
        mx, my = sum(p[0] for p in g) / len(g), sum(p[1] for p in g) / len(g)
        return sum((p[0] - mx) ** 2 + (p[1] - my) ** 2 for p in g)

    best = None                     # (the posts never cross: the split of the brass at a column that leaves two tight groups)
    for split in range(min(x for x, _ in brass) + 1, max(x for x, _ in brass)):
        a, b = [p for p in brass if p[0] < split], [p for p in brass if p[0] >= split]
        if len(a) >= 8 and len(b) >= 8 and (best is None or spread(a) + spread(b) < best[0]):
            best = (spread(a) + spread(b), a, b)
    out, ends = {}, []
    for g in best[1:]:
        base = max(g, key=lambda p: (p[1], -p[0]))
        top = max(g, key=lambda p: (p[0] - base[0]) ** 2 + (p[1] - base[1]) ** 2)
        ends.append((base, top))
        for k, c in cand.items():
            dist, t = seg_dist(k, base, top)
            if dist <= (3.6 if t < 0.12 or t > 0.9 else 1.9):
                out[k] = c
    return out, ends


def rope(ends, sag):
    """The rope's pixels from ring to ring, hanging `sag` px at its middle, never under the floor."""
    rings = []
    for base, top in ends:
        L = math.hypot(top[0] - base[0], top[1] - base[1])
        rings.append((top[0] + (base[0] - top[0]) * 5 / L, top[1] + (base[1] - top[1]) * 5 / L))
    (x0, y0), (x1, y1) = rings
    px, n = {}, int(abs(x1 - x0)) * 3 + 1
    for i in range(n + 1):
        t = i / n
        x, y = round(x0 + (x1 - x0) * t), min(round(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)), FLOOR - 2)
        px[(x, y)] = ROPE
        px.setdefault((x, y + 1), ROPE_D)
    return px


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bare = Image.open(SRC / "stand-bare.png").convert("RGB")
    frames = []
    for i, sag in USE:
        p, ends = posts(Image.open(SRC / "fall1" / f"{i}.png"), bare)
        f = Image.new("RGBA", bare.size)
        for k, c in rope(ends, sag).items():
            f.putpixel(k, c + (255,))
        for k, c in p.items():
            f.putpixel(k, c + (255,))
        frames.append(f)
    # The end: the posts' own pixels lying (assets/source/quiet/roughs.py), the rope on the floor between their rings.
    endp = Image.open(SRC / "stand-end-posts.png").convert("RGB")
    diff = [(x, y) for y in range(endp.height) for x in range(endp.width) if endp.getpixel((x, y)) != bare.getpixel((x, y))]
    x1 = min(x for x, _ in diff)
    x2 = x1 + 25
    last = Image.new("RGBA", bare.size)
    for k, c in rope([((x1, 48), (x1 + 22, 48)), ((x2, 48), (x2 + 22, 48))], END_SAG).items():
        last.putpixel(k, c + (255,))
    for k in diff:
        last.putpixel(k, endp.getpixel(k) + (255,))
    frames.append(last)
    sheet = Image.new("RGBA", (96 * len(frames), 64))
    for k, f in enumerate(frames):
        assert f.getbbox()[3] <= FLOOR, (k, f.getbbox())
        sheet.paste(f, (96 * k, 0))
    sheet.save(OUT / "stand-fall.png")
    layout = {"fall": {"w": 96, "h": 64, "frames": len(frames), "x": STAND_X, "y": FLOOR, "door": DOOR_FRAME,
                       # (How far the fallen stand reaches from the standing one's left, for what must clear it.)
                       "reach": last.getbbox()[2] - STAND_X}}
    (OUT / "quiet.json").write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("stand's fall:", len(frames), "frames; the last reaches", layout["fall"]["reach"], "px from the stand's left")


if __name__ == "__main__":
    main()
