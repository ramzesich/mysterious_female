"""The Stardust Lounge's stage and near-catch 3's own pieces (deck 6; remade 2026-11-24,
docs/near-catch-3-remake-log.md), from assets/source/stage/gen/ (its README has the jobs) into assets/ship/stage/.

    python tools/build_stage.py

- `stage.png` (320 x 128, its left column the stage's forward end, its last row the row over the floor's line): the
  stage's left half as PixelLab redrew it from a flat rough (curtain, valance, lighting bar, star cloth, boards), its
  right half that half mirrored, and the drum kit, redrawn in the stage's own light from the game's own piece where it
  stands, pasted in by its box.
- `valance.png`: the valance cut from it by its reds and golds, laid again over what goes up behind it (Bumbot on
  the rope).
- `lamp.png`: the hanging lamp (generated; hung by the game on a cable, turned as it swings).
- `trap-open.png`: the open hatch (lid up, a ladder's top in the opening), what the inpaint drew in its box of the
  stage's own picture; `trap-shut.png`: its seam and ring in the boards, drawn by rule (flat by nature).
- `snag.png`: the rival's leap, his net on the lamp, his swing and his drop through the hatch: seventeen frames of
  128 x 128 (the picture's left column is `SNAG_X` px into the stage's), made by PixMiniMax on a green copy of the
  stage (he is navy on a navy cloth) from his run's frame to the place with the hatch open, and cut here: what is not
  green and not the place's own picture (the start's until the hatch opens, the end's after), the generator's own lamp
  and cable taken out (the game hangs its own behind his net, where each frame's was measured: `LENS`), loose specks
  dropped; set to the colours his own frames have in the people's sheet (`his_colours`: run after the people's build).
- `puff.png`: the flour out of the hatch, nine frames of 64 x 64: what differs from the place and is light.
- `stage.json`: where each stands.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "stage" / "gen"
OUT = ROOT / "assets" / "ship" / "stage"

W, H = 320, 128
DRUMS = (22, 72, 100, 128)          # the drum kit's box in the left half
TRAP_BOX = (90, 92, 132, 128)       # the open hatch's box in the stage's picture (the inpaint's mask)
SEAM = (112, 134)                   # the shut hatch's seam, from and to (stage px): over the open one's hole
SNAG_X = 48                         # the rival's clip: its left column in the stage's picture
SNAG_TRY, OPEN_FRAME = "snag-s23", 13
# The lamp's lens in each frame of his clip (clip px), measured from its yellow in the generated frames.
LENS = [(42, 33.5)] * 5 + [(44, 33.5), (46, 33.5), (49.1, 33.5), (50, 34.5), (52, 37.5), (53, 41.5), (53, 50.5),
                           (54, 65.5), (50, 74.5), (47, 77.5), (44, 77.5), (42, 77.5)]
PUFF_BOX, PUFF_FRAMES = (92, 64), range(2, 11)
LANTERNS = [48, 139]                # the lighting bar's lanterns in the left half (their lenses at row 31)


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def red(c):
    return (c[0] > 90 and c[0] > c[2] * 1.5 and c[0] > c[1] * 1.5) or (c[0] > 150 and c[1] > 100 and c[2] < 110)


def green(c):
    return c[1] > 120 and c[1] > c[0] * 1.6 and c[1] > c[2] * 1.6


def stage():
    half = Image.open(SRC / "stage-left-s11.png").convert("RGB")
    drums = Image.open(SRC / "redraw-left-drums.png").convert("RGB")
    st = Image.new("RGB", (W, H))
    st.paste(half, (0, 0))
    st.paste(half.transpose(Image.FLIP_LEFT_RIGHT), (W // 2, 0))
    st.paste(drums.crop(DRUMS), DRUMS[:2])
    return st


def fronts(st):
    """The valance (the picture's top), by its reds and golds."""
    val = Image.new("RGBA", (W, 24), (0, 0, 0, 0))
    for x in range(W):
        rows = [y for y in range(24) if red(st.getpixel((x, y)))]
        for y in range(0, (max(rows) + 1) if rows else 0):          # (its dark folds too: all of it over its hem)
            val.putpixel((x, y), st.getpixel((x, y)) + (255,))
    return val


def trap(st):
    opened = Image.open(SRC / "trap-open-s21.png").convert("RGB")
    left = Image.open(SRC / "src-left-final.png").convert("RGB")
    x0, y0, x1, y1 = TRAP_BOX
    op = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    for y in range(y0, y1):
        for x in range(x0, x1):
            a = opened.getpixel((x, y))
            if dist(a, left.getpixel((x, y))) > 24:
                op.putpixel((x - x0, y - y0), a + (255,))
    # Shut: a seam in the boards, seen a little from above as they are, and a brass ring.
    a, b = SEAM
    shut = Image.new("RGBA", (b - a + 4, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(shut)
    dark, ring = (40, 16, 20, 255), (217, 164, 59, 255)
    d.line((2, 0, b - a + 2, 0), fill=dark)
    d.line((0, 6, b - a, 6), fill=dark)
    d.line((2, 0, 0, 6), fill=dark)
    d.line((b - a + 2, 0, b - a, 6), fill=dark)
    d.rectangle(((b - a) // 2, 2, (b - a) // 2 + 1, 3), fill=ring)
    return op, shut


def his_colours():
    """The colours of the rival's own frames in the people's sheet (on the palette): his clip is set to them, so that
    it is the same man as his run before it. (The palette's nearest to the generator's shades were darker ones.)"""
    meta = json.loads((ROOT / "assets" / "sprites" / "people.json").read_text(encoding="utf8"))
    sheet = Image.open(ROOT / "assets" / "sprites" / "people.png").convert("RGBA")
    cell, cols, who = meta["cell"], meta["cols"], meta["people"]["rival"]
    found = set()
    for clip in ("charge", "walk", "lunge", "trip"):
        for f in who["anims"].get(clip, []):
            box = ((f % cols) * cell, (f // cols) * cell, (f % cols) * cell + cell, (f // cols) * cell + cell)
            for c in sheet.crop(box).getdata():
                if c[3]:
                    found.add(c[:3])
    return sorted(found)


def own(im, colours):
    out = im.copy()
    px, memo = out.load(), {}
    for y in range(im.height):
        for x in range(im.width):
            c = px[x, y]
            if not c[3]:
                continue
            k = c[:3]
            if k not in memo:
                memo[k] = min(colours, key=lambda q: (q[0] - k[0]) ** 2 + (q[1] - k[1]) ** 2 + (q[2] - k[2]) ** 2)
            px[x, y] = memo[k] + (255,)
    return out


def snag(st):
    colours = his_colours()
    start = Image.open(SRC / "snag-start.png").convert("RGB")
    # (The start picture has him in it: under him the boards are the stage's own.)
    start.paste(st.crop((SNAG_X, 117, SNAG_X + 55, 128)), (0, 117))
    end = Image.open(SRC / "snag-end.png").convert("RGB")
    sheet = Image.new("RGBA", (17 * 128, 128), (0, 0, 0, 0))
    for i in range(17):
        f = Image.open(SRC / SNAG_TRY / f"{i}.png").convert("RGB")
        ref = end if i >= OPEN_FRAME else start
        out = Image.new("RGBA", f.size, (0, 0, 0, 0))
        fp, rp, op = f.load(), ref.load(), out.load()
        for y in range(128):
            for x in range(128):
                c = fp[x, y]
                if green(c):
                    continue
                if y >= 117 and dist(c, rp[x, y]) < 60:         # the boards, and the hatch as the world shows it
                    continue
                if i >= OPEN_FRAME and dist(c, rp[x, y]) < 45:    # the open hatch's lid and ladder, the lamp at rest
                    continue
                op[x, y] = c + (255,)
        if i == 0:
            # (Frame 0 is his run's frame as the game shows it, and the lamp where the game hangs it: only he is kept.)
            for y in range(60):
                for x in range(128):
                    op[x, y] = (0, 0, 0, 0)
        else:
            lx, ly = LENS[i]
            for y in range(0, int(ly) + 6):
                for x in range(34, int(lx) + 10):
                    c = op[x, y]
                    if not c[3]:
                        continue
                    inbox = abs(x - lx) <= 8 and y >= ly - 24
                    dark = c[0] + c[1] + c[2] < 230
                    grey = abs(c[0] - c[1]) < 22 and abs(c[1] - c[2]) < 30 and c[0] + c[1] + c[2] < 480
                    yellow = c[0] > 200 and c[1] > 160 and c[2] < 150
                    if (inbox and (dark or grey or yellow)) or (not inbox and y < ly - 20 and dark):
                        op[x, y] = (0, 0, 0, 0)
        if i >= OPEN_FRAME:
            # (The boards the generator broke up round the hatch: only what is under him and his net is kept.)
            cols = [x for x in range(128) if any(op[x, y][3] for y in range(0, 116))]
            lo, hi = (min(cols) - 2, max(cols) + 2) if cols else (0, -1)
            for y in range(116, 128):
                for x in range(128):
                    if not lo <= x <= hi:
                        op[x, y] = (0, 0, 0, 0)
        specks(out, 24)
        sheet.paste(own(out, colours), (i * 128, 0))
    return sheet


def specks(im, least):
    """Pieces of fewer than `least` px out."""
    px, seen = im.load(), set()
    for y0 in range(im.height):
        for x0 in range(im.width):
            if not px[x0, y0][3] or (x0, y0) in seen:
                continue
            comp, stack = [], [(x0, y0)]
            seen.add((x0, y0))
            while stack:
                x, y = stack.pop()
                comp.append((x, y))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        q = (x + dx, y + dy)
                        if 0 <= q[0] < im.width and 0 <= q[1] < im.height and q not in seen and px[q[0], q[1]][3]:
                            seen.add(q)
                            stack.append(q)
            if len(comp) < least:
                for x, y in comp:
                    px[x, y] = (0, 0, 0, 0)


def puff():
    first = Image.open(SRC / "puff" / "0.png").convert("RGB")
    sheet = Image.new("RGBA", (len(PUFF_FRAMES) * 64, 64), (0, 0, 0, 0))
    for n, i in enumerate(PUFF_FRAMES):
        f = Image.open(SRC / "puff" / f"{i}.png").convert("RGB")
        for y in range(64):
            for x in range(64):
                a = f.getpixel((x, y))
                if dist(a, first.getpixel((x, y))) > 60 and a[0] > 120:
                    sheet.putpixel((n * 64 + x, y), a + (255,))
    return sheet


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st = stage()
    st.save(OUT / "stage.png")
    fronts(st).save(OUT / "valance.png")
    lamp = Image.open(SRC / "lamp-s4.png").convert("RGBA")
    lamp = lamp.crop(lamp.getbbox())
    lamp.save(OUT / "lamp.png")
    op, shut = trap(st)
    op.save(OUT / "trap-open.png")
    shut.save(OUT / "trap-shut.png")
    sn = snag(st)
    sn.save(OUT / "snag.png")
    pf = puff()
    pf.save(OUT / "puff.png")
    run = Image.open(ROOT / "assets" / "source" / "people" / "rival" / "charge" / "7.png").convert("RGBA")
    box = run.getbbox()
    start = 22 - (box[2] - box[0]) // 2 + run.width // 2 - box[0]
    layout = {
        "stage": {"w": W, "h": H, "lanterns": LANTERNS + [W - 1 - x for x in reversed(LANTERNS)], "lens": 31},
        "lamp": {"w": lamp.width, "h": lamp.height},
        "trap": {"open": list(TRAP_BOX[:2]), "shut": [SEAM[0] - 2, 119], "x": (SEAM[0] + SEAM[1]) // 2},
        "snag": {"x": SNAG_X, "cell": 128, "frames": 17, "open": OPEN_FRAME, "lens": LENS, "start": start},
        "puff": {"x": PUFF_BOX[0], "y": PUFF_BOX[1], "cell": 64, "frames": len(PUFF_FRAMES)},
    }
    (OUT / "stage.json").write_text(json.dumps(layout, indent=1) + "\n", encoding="utf8")
    print("stage", st.size, "lamp", lamp.size, "trap", op.size, shut.size, "snag", sn.size, "puff", pf.size)


if __name__ == "__main__":
    main()
