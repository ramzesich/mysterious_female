"""The Art Gallery's painting and its two handlers (part 11's item 10, the user, 2026-11-28; sources in
`assets/source/people/handlers-raw/`, its README): into `assets/ship/`
- `painting.png`: the lighthouse painting (`assets/source/things/tries/painting/lighthouse.png`, the user's choice), the one
  picture of it the game draws whenever the two carry it, set it down, drop it or pick it up;
- `handlers.png` + `handlers.json`: their clips, 128 x 80 cells, their feet on row 75 (the floor at 76): `walkE`, `walkW`
  (loops), `downE`, `downW` (from the carry to the rest, facing us), `dropE`, `dropW` (startled, they lose their grip and
  it drops to the floor, then the rest: the user, 2026-11-28, when she bumps into them or lands on them), `wipe` (at
  rest), `upE`, `upW` (from the rest to the carry). Each frame's figures with the painting's place empty, and where the
  painting is in it (`panel`: its left column, its top row); it only goes straight up and down, its left column 41, and
  in a drop it falls by rule (`FALLS`: the generator tossed it up first). Specks the generator left in the air (pieces of
  fewer than `SPECK` px not joined to the two) are cleared.
Run `python tools/build_painting.py` after changing a source."""
import json
from collections import deque
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "assets/source/people/handlers-raw"
OUT = ROOT / "assets/ship"
HANDLERS = [("walkE", "walk", range(1, 9)), ("walkW", "walkW-s1", range(1, 9)),
            ("downE", "setdownE-s2", range(0, 13)), ("downW", "setdownW-s2", range(0, 13)),
            ("upE", "pickupE-s1", range(0, 13)), ("upW", "pickupW-p2", range(0, 13)),
            ("dropE", "dropE-s2", range(0, 9)), ("dropW", "dropW-s1", range(0, 9)),
            ("wipe", "wipe-s3", range(1, 9))]
PAINT_X = 41
# The painting's top row in a drop's frames: in their hands, then falling straight down onto the floor (row 36) as they
# let go (the right-facing one lets go a frame sooner).
FALLS = {"dropE": [22, 22, 28], "dropW": [22, 22, 22, 28]}
FLOOR_TOP = 36
SPECK = 8


def clear_specks(im):
    """Pieces of fewer than SPECK px, apart from the two, out."""
    px, seen = im.load(), set()
    for y in range(im.height):
        for x in range(im.width):
            if (x, y) in seen or not px[x, y][3]:
                continue
            piece, q = [], deque([(x, y)])
            seen.add((x, y))
            while q:
                a, c = q.popleft()
                piece.append((a, c))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        n = (a + dx, c + dy)
                        if 0 <= n[0] < im.width and 0 <= n[1] < im.height and n not in seen and px[n][3]:
                            seen.add(n)
                            q.append(n)
            if len(piece) < SPECK:
                for p in piece:
                    px[p] = (0, 0, 0, 0)
    return im


def sheet(frames, cw, ch, cols):
    rows = (len(frames) + cols - 1) // cols
    S = Image.new("RGBA", (cw * cols, ch * rows))
    for i, f in enumerate(frames):
        S.alpha_composite(f, ((i % cols) * cw, (i // cols) * ch))
    return S


def handlers():
    frames, clips, panels = [], {}, []
    for name, src, rng in HANDLERS:
        J = json.loads((RAW / "cut" / f"{src}.json").read_text())
        clips[name] = []
        for i in rng:
            k = len(clips[name])
            clips[name].append(len(frames))
            frames.append(clear_specks(Image.open(RAW / "cut" / src / f"{i}.png").convert("RGBA")))
            # (Its top row from its bottom: the painting is 40 rows; straight up and down, at one column.)
            top = J["panel"][i][3] - 39
            if name in FALLS:
                top = FALLS[name][k] if k < len(FALLS[name]) else FLOOR_TOP
            panels.append([PAINT_X, top])
    sheet(frames, 128, 80, 16).save(OUT / "handlers.png")
    meta = {"cell": [128, 80], "cols": 16, "floor": 76, "paintX": PAINT_X, "clips": clips, "panel": panels}
    (OUT / "handlers.json").write_text(json.dumps(meta) + "\n", encoding="utf8")
    print("handlers", len(frames), "frames")


if __name__ == "__main__":
    p = Image.open(ROOT / "assets/source/things/tries/painting/lighthouse.png").convert("RGBA")
    p.crop(p.getbbox()).save(OUT / "painting.png")
    handlers()
