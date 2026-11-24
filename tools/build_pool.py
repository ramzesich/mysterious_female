"""The pool's scene, its own pieces (deck 11, near-catch 5; the user's remake, 2026-11-24; docs/pool-remake-log.md).

Each piece was drawn flat by rule into the game's own picture of its place (`assets/source/pool/rough/`, each with its
`-base.png`, the place without it), redrawn by PixelLab (`edit_image_pro_flash`: "Keep this whole picture exactly as it
is ... redraw only the rough ..."; `gen/`, the jobs in the folder's README), and is cut here by what differs from the
base inside its box:

- **the drain's lever on its stand** (`lever.png`, a strip of frames), knee-high: the stand is the generated one without
  its own hair-thin arm; the arm is drawn by rule in the picture's own tones (a steel bar outlined each side, a red
  grip) at each frame's angle, armed (leaning toward the pool) to thrown (over toward the hot tub). One stand in
  every frame: only the arm changes. (A generated arm turned pixel by pixel came out ragged where it rests.)
- **the maintenance hatch in the tank's floor**, seen a little from above (`hatch-shut.png`; open, `hatch-back.png`
  the opening and the lid stood up behind it, `hatch-lip.png` its near edge, drawn over her as she goes down);
- **the drain's grate** in the floor at the tank's aft end (`drain.png`);
- **the ceiling panel** in deck 10's hallway under the hatch (`ceiling-shut.png`, `ceiling-open.png`);
- **the pool ladder's lower part**, down the tank's wall to its floor (`ladder-low.png`: the ship atlas's own ladder,
  its rail-and-rung rows repeated; the atlas piece ends in the water).

`pool.json` says where each stands from its own anchor (the lever's stand on the deck, the hatch's and the grate's
middle on the tank's floor line, the ceiling panel's middle on the hallway's ceiling line), and the lever's grip in
every frame (where Bumbot rides it).

    python tools/build_pool.py
"""
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source" / "pool"
OUT = ROOT / "assets" / "ship" / "pool"
SEA = 50                  # a steel piece's pixel is not steel when its blue leads its red by more than this
DIFF = 24                 # a pixel is the piece's when it is this far (r + g + b) from the place's own
# Where each thing stands in the world its rough was drawn in (px; `LIDO` in tools/population.py gives the same):
# the lever's stand, the hatch's middle, deck 11's floor, the tank's floor, the hallway's ceiling line.
LEVER_X, HATCH_X, DECK_Y, TANK_Y, CEILING_Y = 6803, 6648, 560, 592, 575
# The user's own placing of them, seen in play (2026-11-24): the tank's floor reads as its strip of pale tiles, so
# the hatch lies 3 px lower than its rough was drawn, the grate 2, and the ladders stand 3 px lower (the atlas's
# ladder hangs LADDER_UNDER px under the deck's line: `at11` in tools/build_ship_map.py, `prop_ladder_aft`).
HATCH_DOWN, DRAIN_DOWN, FLOOR_DOWN, LADDER_UNDER = 3, 2, 3, 15
# Each piece: the generated picture, the base it is compared with, its box in that picture.
BOXES = {"lever": ("lever-up", "lever-base", (41, 72, 61, 96)), "hatch-shut": ("hatch-shut", "hatch-base", (30, 60, 84, 82)),
         "hatch-open": ("hatch-open", "hatch-base", (30, 26, 84, 82)), "drain": ("aft", "aft-base", (24, 62, 54, 80)),
         "ceiling-shut": ("ceiling-shut", "ceiling-base", (20, 10, 76, 22)), "ceiling-open": ("ceiling-open", "ceiling-base", (16, 10, 76, 56))}
# The lever (knee-high: the user, 2026-11-24, of the first, 46 px to its grip: "way too big. It should be at least half a
# height"; that one is kept in `tries/`): its pivot in its picture (px, the middle of its cap); the generated arm's own
# pixels there, taken off the stand (every row above ARM_ROW, and that row up to column ARM_COL); the arm drawn by rule:
# from the pivot (px), its grip's stretch along it; its angle from straight up when armed (degrees, toward the pool),
# and how far on from that it is frame by frame (clockwise, toward the hot tub): the swing, the thrown rest, its bounce.
PIVOT = (51, 83)
ARM_ROW, ARM_COL = 81, 48
ARM_FROM, GRIP = 2, (7, 12)
ARMED = -40
SWING = [0, 30, 62, 92, 114, 108, 112]
LID_CUT = (34, 40)        # rows of the open hatch's picture taken out of its lid's plain middle: the lid stood taller than the tank's wall
LIP_ROWS = 3              # the open hatch's near edge: its last rows, drawn over her


def origins():
    return json.loads((SOURCE / "rough" / "rough.json").read_text(encoding="utf-8"))


def differs(a, b, box, thr=DIFF):
    """What of picture `a` is not picture `b`, inside the box: an RGBA picture the box's size."""
    x0, y0, x1, y1 = box
    out = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    op, ap, bp = out.load(), a.load(), b.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            if sum(abs(u - v) for u, v in zip(ap[x, y], bp[x, y])) > thr:
                op[x - x0, y - y0] = ap[x, y] + (255,)
    return out


def components(mask, w, h, reach=1):
    """The mask's pieces, pixels joined within `reach` px."""
    seen, out = set(), []
    for start in mask:
        if start in seen:
            continue
        comp, todo = [], [start]
        seen.add(start)
        while todo:
            x, y = todo.pop()
            comp.append((x, y))
            for dx in range(-reach, reach + 1):
                for dy in range(-reach, reach + 1):
                    q = (x + dx, y + dy)
                    if q in mask and q not in seen:
                        seen.add(q)
                        todo.append(q)
        out.append(comp)
    return out


def clean(piece, source, box, steel=True):
    """A cut piece made whole: loose specks dropped (anything not joined to its largest part within 2 px), and
    the holes inside it filled from the generated picture (a pixel of the piece that happened to match the place behind
    it: the lever's grey on the sea's)."""
    w, h = piece.size
    p = piece.load()
    if steel:
        # (A steel piece has no sea in it: a pixel much bluer than it is red is the generator's own change to the sea
        # or the tiles beside the piece.)
        for y in range(h):
            for x in range(w):
                if p[x, y][3] and p[x, y][2] - p[x, y][0] > SEA:
                    p[x, y] = (0, 0, 0, 0)
    mask = {(x, y) for y in range(h) for x in range(w) if p[x, y][3]}
    comps = sorted(components(mask, w, h, 2), key=len, reverse=True)
    keep = set(comps[0])
    for x, y in mask - keep:
        p[x, y] = (0, 0, 0, 0)
    # holes: what the outside cannot reach
    outside, todo = set(), [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    todo = [q for q in todo if q not in keep]
    outside.update(todo)
    while todo:
        x, y = todo.pop()
        for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= q[0] < w and 0 <= q[1] < h and q not in keep and q not in outside:
                outside.add(q)
                todo.append(q)
    sp = source.load()
    for y in range(h):
        for x in range(w):
            if (x, y) not in keep and (x, y) not in outside:
                p[x, y] = sp[box[0] + x, box[1] + y] + (255,)
    return piece


def cut(name):
    gen, base, box = BOXES[name]
    a = Image.open(SOURCE / "gen" / f"{gen}.png").convert("RGB")
    b = Image.open(SOURCE / "rough" / f"{base}.png").convert("RGB")
    ox, oy = origins()[base][:2]
    return clean(differs(a, b, box), a, box, steel=not name.startswith("ceiling")), (ox + box[0], oy + box[1])


def trim(img, at):
    bb = img.getbbox()
    return img.crop(bb), (at[0] + bb[0], at[1] + bb[1])


def drawn(size, pivot, strip, degrees):
    """The straightened arm drawn at an angle from straight up (clockwise), as pixel art: stepped along whichever of x
    and y it runs further in, its width laid across the other, so that its outline and its width hold at every angle
    (turned pixel by pixel, an arm three px wide came out ragged where it rests)."""
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    op = out.load()
    r = math.radians(degrees)
    vx, vy = math.sin(r), -math.cos(r)
    flat = abs(vx) > abs(vy)
    n = len(strip) - 1
    steps = round(n * (abs(vx) if flat else abs(vy)))
    for i in range(steps + 1):
        t = i / (abs(vx) if flat else abs(vy))
        col = strip[min(n, round(t))]
        cx, cy = pivot[0] + vx * t, pivot[1] + vy * t
        for d, c in col.items():
            # (Across: to the right of its way when it stands, under it when it lies: as it turns.)
            x, y = (round(cx), round(cy) + (d if vx > 0 else -d)) if flat else (round(cx) + (d if vy < 0 else -d), round(cy))
            if 0 <= x < size[0] and 0 <= y < size[1]:
                op[x, y] = c
    return out


def lever():
    """The lever's frames, each the stand with the arm at its angle, on one canvas wide enough for the throw. The stand
    is the generated picture's without its own arm (a hair's width at this size: everything above the cap's top row,
    and the arm's foot on it); the arm is drawn by rule in the picture's own tones: a steel bar with an outline each
    side, so that it reads against the pale sky whichever way it lies, and a red grip a px wider."""
    gen, base, box = BOXES["lever"]
    up = Image.open(SOURCE / "gen" / "lever-up.png").convert("RGB")
    place = Image.open(SOURCE / "rough" / f"{base}.png").convert("RGB")
    ox, oy = origins()[base][:2]
    whole = clean(differs(up, place, box), up, box)
    stand = whole.copy()
    sp = stand.load()
    reds, steels = {}, {}
    for y in range(stand.height):
        for x in range(stand.width):
            c = sp[x, y]
            if not c[3]:
                continue
            if c[0] > 150 and c[1] < 110 and c[2] < 110:
                reds[c] = reds.get(c, 0) + 1
            else:
                steels[c] = steels.get(c, 0) + 1
            if box[1] + y < ARM_ROW or (box[1] + y == ARM_ROW and box[0] + x <= ARM_COL):
                sp[x, y] = (0, 0, 0, 0)
    fair = [c for c, k in steels.items() if k >= 0.04 * sum(steels.values())]
    dark, lit = min(steels, key=sum), max(fair, key=sum)
    red = max(reds, key=reds.get)
    red_lit = max(reds, key=sum)
    bar = {-1: dark, 0: lit, 1: dark}
    grip = {-2: dark, -1: red_lit, 0: red, 1: dark}
    strip_arm = [{} if t < ARM_FROM else bar if t < GRIP[0] else grip if t <= GRIP[1] else {d: dark for d in (-1, 0)} for t in range(GRIP[1] + 2)]
    px, py = PIVOT[0] - box[0], PIVOT[1] - box[1]
    reach = GRIP[1] + 4
    pad_l, pad_r, pad_t = int(max(0, reach - px)) + 1, int(max(0, reach - (whole.width - px))) + 1, int(max(0, reach - py)) + 1
    W, H = whole.width + pad_l + pad_r, whole.height + pad_t
    frames, grips = [], []
    mid = (GRIP[0] + GRIP[1]) / 2
    for deg in SWING:
        f = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        f.alpha_composite(drawn((W, H), (round(px + pad_l), round(py + pad_t)), strip_arm, ARMED + deg))
        f.alpha_composite(stand, (pad_l, pad_t))          # (the arm comes out from behind the cap)
        frames.append(f)
        r = math.radians(ARMED + deg)
        grips.append([round(px + pad_l + math.sin(r) * mid, 1), round(py + pad_t - math.cos(r) * mid, 1)])
    strip = Image.new("RGBA", (W * len(frames), H), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(f, (i * W, 0))
    # (Where the canvas stands from the stand's anchor: its middle on the deck.)
    left, top = ox + box[0] - pad_l, oy + box[1] - pad_t
    info = dict(w=W, h=H, frames=len(frames), dx=left - LEVER_X, dy=top - DECK_Y,
                grips=[[round(left + g[0] - LEVER_X, 1), round(top + g[1] - DECK_Y, 1)] for g in grips],
                pivot=[left + px + pad_l - LEVER_X, top + py + pad_t - DECK_Y])
    return strip, info


def hatch():
    shut, at_shut = trim(*cut("hatch-shut"))
    opened, at = cut("hatch-open")
    # the lid a few rows shorter, out of its plain ribbed middle, so that it tops out at the tank's rim
    a, b = LID_CUT[0] - BOXES["hatch-open"][2][1], LID_CUT[1] - BOXES["hatch-open"][2][1]
    short = Image.new("RGBA", (opened.width, opened.height - (b - a)), (0, 0, 0, 0))
    short.paste(opened.crop((0, 0, opened.width, a)), (0, 0))
    short.paste(opened.crop((0, b, opened.width, opened.height)), (0, a))
    opened, at = trim(short, (at[0], at[1] + (b - a)))
    lip = opened.crop((0, opened.height - LIP_ROWS, opened.width, opened.height))
    back = opened.crop((0, 0, opened.width, opened.height - LIP_ROWS))
    rel = lambda p: [p[0] - HATCH_X, p[1] - TANK_Y + HATCH_DOWN]
    return {"hatch-shut": (shut, rel(at_shut)), "hatch-back": (back, rel(at)), "hatch-lip": (lip, rel((at[0], at[1] + opened.height - LIP_ROWS)))}


def ladder_low():
    """The pool ladder on down the tank's wall: the atlas's ladder, a period of its rails with one rung repeated. Its
    rails are found by its own columns; it is placed under the atlas piece's last row above the water it is drawn in."""
    atlas = json.loads((ROOT / "assets" / "ship" / "ship.json").read_text(encoding="utf-8"))
    sheet = Image.open(ROOT / "assets" / "ship" / "ship.png").convert("RGBA")
    f = atlas["frames"]["pool-ladder-w20"]["frame"]
    piece = sheet.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
    p = piece.load()
    # rung rows: rows where the middle column between the rails is drawn; the period is the gap between two rungs
    mid = piece.width // 2 - 3
    rungs = [y for y in range(piece.height) if p[mid, y][3] and (y == 0 or not p[mid, y - 1][3])]
    rungs = [y for y in rungs if y > 8]
    period = rungs[1] - rungs[0]
    cell = piece.crop((0, rungs[0], piece.width, rungs[0] + period))
    return piece, cell, rungs, period


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    info = {}
    strip, info["lever"] = lever()
    strip.save(OUT / "lever.png")
    for name, (img, at) in hatch().items():
        img.save(OUT / f"{name}.png")
        info[name] = at
    img, at = trim(*cut("drain"))
    img.save(OUT / "drain.png")
    # (The grate's own anchor: its middle on the tank's floor line; `drain` in `LIDO` is that metre.)
    info["drain"] = dict(x=at[0] + img.width // 2, dx=-(img.width // 2), dy=at[1] - TANK_Y + DRAIN_DOWN)
    for name in ("ceiling-shut", "ceiling-open"):
        img, at = trim(*cut(name))
        img.save(OUT / f"{name}.png")
        info[name] = [at[0] - HATCH_X, at[1] - CEILING_Y]
    piece, cell, rungs, period = ladder_low()
    # from the tank's top edge (4 px under the deck) to its floor: the atlas piece hangs 12 px into the deck
    top_row = piece.height - LADDER_UNDER + 4      # the piece's row at the tank's top edge, 4 px under the deck's line
    rows = TANK_Y + FLOOR_DOWN - (DECK_Y + 4)
    low = Image.new("RGBA", (piece.width, rows), (0, 0, 0, 0))
    for y in range(rows):
        src_row = rungs[0] + ((top_row + y - rungs[0]) % period)
        low.paste(piece.crop((0, src_row, piece.width, src_row + 1)), (0, y))
    low.save(OUT / "ladder-low.png")
    info["ladder-low"] = dict(dy=4, rungs=rungs, period=period)
    (OUT / "pool.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(json.dumps(info))


if __name__ == "__main__":
    main()
