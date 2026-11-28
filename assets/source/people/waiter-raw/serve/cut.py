"""The waiter's serve at a table (the user, 2026-11-28): two PixMiniMax clips on a green copy of table 2 from the game's
own picture of him with his tray and cloche (`start-green.png`, from `game-A/B/C.png`), through the cloche lifted
(`mid-try1.png`, an edit) to the start with the plate of food set on the table (`end-green.png`, composed: `plate.png`
cut from the edit). Each frame cut out by what differs from the set (green and the table), specks cleared, into
`clip/NN.png` (128 x 96, the set's own frame: its column 64 the table's middle, row 88 the floor). `SEQ`: the frames
used, raw1's then raw3's (raw2, the first try toward the plate 2 px higher, unused). Then built into the game:
`assets/ship/waiter/serve.png` (8 frames a row) + `serve.json` (`stand`: his column and the floor's row in a frame; `plate`:
the plate's top left there), and `plate.png`, the plate he leaves on the table.
Run `python assets/source/people/waiter-raw/serve/cut.py`."""
import json
from collections import deque
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
SET = Image.open(HERE / "start-green.png").convert("RGB")
WAITER = Image.open(HERE / "waiter-tray.png").getchannel("A")
# The set: the start picture with the waiter taken out (green where he stood).
SETP = SET.copy()
SETP.paste((0, 200, 0), (0, 0, 128, 96), WAITER)
SEQ = [("raw1", i) for i in (0, 1, 3, 4, 5, 6, 7, 8)] + [("raw3", i) for i in range(1, 9)]
# (Only what is near him: the generator drew streaks by the far chair.)
KEEP = (40, 92)
PLATE_Y = 61        # (the plate's top row: its foot on row 66, as the vase's glass stands, the user, 2026-11-28)
SPECK = 30          # (the plate on the table is ~80 px; the streaks under 30)


def near(a, b, t):
    return abs(a[0] - b[0]) <= t and abs(a[1] - b[1]) <= t and abs(a[2] - b[2]) <= t


def green(c):
    return c[1] > 150 and c[0] < 70 and c[2] < 70


def cut(im):
    im = im.convert("RGB")
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    po, pi, ps = out.load(), im.load(), SETP.load()
    for y in range(im.height):
        for x in range(im.width):
            c = pi[x, y]
            if green(c) or near(c, ps[x, y], 24) or not KEEP[0] <= x <= KEEP[1]:
                continue
            po[x, y] = c + (255,)
    # Specks: pieces of fewer than SPECK px.
    seen = set()
    for y in range(out.height):
        for x in range(out.width):
            if (x, y) in seen or not po[x, y][3]:
                continue
            piece, q = [], deque([(x, y)])
            seen.add((x, y))
            while q:
                a, b = q.popleft()
                piece.append((a, b))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        n = (a + dx, b + dy)
                        if 0 <= n[0] < out.width and 0 <= n[1] < out.height and n not in seen and po[n][3]:
                            seen.add(n)
                            q.append(n)
            if len(piece) < SPECK:
                for p in piece:
                    po[p] = (0, 0, 0, 0)
    return out


if __name__ == "__main__":
    (HERE / "clip").mkdir(exist_ok=True)
    for k, (src, i) in enumerate(SEQ):
        cut(Image.open(HERE / src / f"{i}.png")).save(HERE / "clip" / f"{k:02d}.png")
    # (Its first frame is the game's own picture exactly, its last the start with the plate on the table.)
    first = Image.new("RGBA", (128, 96)); first.paste(Image.open(HERE / "waiter-tray.png"), (0, 0))
    first.save(HERE / "clip" / "00.png")
    last = Image.new("RGBA", (128, 96)); last.alpha_composite(Image.open(HERE / "plate.png"), (50, PLATE_Y))
    last.alpha_composite(Image.open(HERE / "waiter-tray.png"))
    last.save(HERE / "clip" / f"{len(SEQ) - 1:02d}.png")
    out = HERE.parents[4] / "assets" / "ship" / "waiter"
    out.mkdir(exist_ok=True)
    frames = [Image.open(HERE / "clip" / f"{k:02d}.png") for k in range(len(SEQ))]
    cols = 8
    sheet = Image.new("RGBA", (128 * cols, 96 * ((len(frames) + cols - 1) // cols)))
    for k, f in enumerate(frames):
        sheet.alpha_composite(f, ((k % cols) * 128, (k // cols) * 96))
    sheet.save(out / "serve.png")
    Image.open(HERE / "plate.png").save(out / "plate.png")
    (out / "serve.json").write_text(json.dumps({"cell": [128, 96], "frames": len(frames), "cols": cols, "stand": [70, 88],
                                                "plate": [50, PLATE_Y]}) + chr(10))
    print(len(SEQ), "frames")
