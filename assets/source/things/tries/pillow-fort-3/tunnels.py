"""Splash Academy's pillow castle (the user's choice of four, 2026-11-27, `castle.png`) with a crawl tunnel at each
tower's foot, its mouth in profile as the shaft's and the first fort's were (the user: "take what we learned about the
openings"): the tunnel's near side and rim in front of her (`pillow-fort.png`), its dark slot behind her
(`pillow-fort-back.png`).

    python tunnels.py rough            the castle cropped to its floor row, a tunnel drawn flat at each tower's foot
    python tunnels.py split <redraw>   the redraw cut in two: the dark at each outer end behind her
"""
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
OUT_DIR = HERE.parent.parent
FLOOR = 100                                # the castle's floor row in castle.png
TOP = 3                                    # rows added over it: the canvas a multiple of 4 high (104)
PAD = 12                                   # px added each side (232 wide)
TUBE_H, OUT = 30, 6                        # a mouth's height, and how far it stands out of its wall
# Each tower's two faces at its foot, in the castle's own px, and which way its mouth faces (-1 left, +1 right):
# the outer faces, and the inner ones facing the middle under the quilt (the user, 2026-11-27: "The outside protrusions
# have to be much narrower ... The inside walls of the fort, on the opposite sides of the protrusions, don't look like
# they're passable. So we have to deal with both sides of each wall").
FACES = ((9, -1), (41, +1), (161, -1), (192, +1))
# The cushions leaning at the towers' inner feet, under the quilt's corners, cleared so the inner mouths are the towers'
# own faces: (x from, x to, from row) in the castle's px.
LEANING = ((42, 66, 70), (134, 160, 70), (67, 133, 95))   # (and the floor line under the open middle)
STRIPES = [(232, 59, 59), (249, 194, 43), (77, 155, 230), (249, 194, 43)]
OUTL, RIM, DARK = (46, 34, 47), (150, 40, 50), (50, 44, 60)


def mouth_cols(face, way):
    """A mouth's columns in the canvas, from its wall outward: fabric 2, rim 2, the dark slot 2."""
    x = face + PAD
    return [x + way * k for k in range(1, OUT + 1)]


def rough():
    castle = Image.open(HERE / "castle.png").convert("RGBA").crop((0, 0, 208, FLOOR + 1))
    for a, b, row in LEANING:
        for x in range(a, b + 1):
            for y in range(row, FLOOR + 1):
                castle.putpixel((x, y), (0, 0, 0, 0))
    W, H = 208 + 2 * PAD, FLOOR + 1 + TOP
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.alpha_composite(castle, (PAD, TOP))
    for face, way in FACES:
        for k, x in enumerate(mouth_cols(face, way)):
            for y in range(H - TUBE_H, H):
                edge = y in (H - TUBE_H, H - 1)
                if k < 2:
                    c = OUTL if edge else STRIPES[((y + k) // 4) % 4]
                elif k < 4:
                    c = OUTL if edge else RIM
                else:
                    c = OUTL if edge or k == OUT - 1 and y < H - TUBE_H + 2 else DARK
                im.putpixel((x, y), c + (255,))
    im.save(HERE / "rough-tunnels.png")
    print("rough", im.size)


def split(path):
    """The redraw as the fort's one picture, in front of her, cut to its own box. (A first cut moved the openings' dark
    behind her and left holes in the tubes' rims: she showed patched through them at every opening, the user, 2026-11-27:
    "The cuts are very bad, on all sides". In the tubes' rows the fort stops at the tubes' ends, 15 to 61 and 166 to 212,
    so wholly in front of her it hides her inside a tube, ends straight at each opening, and is in front of nothing of
    her between the towers or outside them.)"""
    red = Image.open(path).convert("RGBA")
    box = red.getbbox()
    red.crop(box).save(OUT_DIR / "pillow-fort.png")
    gone = OUT_DIR / "pillow-fort-back.png"
    if gone.exists():
        gone.unlink()
    print("fort", box, "->", (box[2] - box[0], box[3] - box[1]))


def cutaway(path):
    """The tubes cut open (seed 7 of the cutaway edit, `cutaway-s7.png`; the user, 2026-11-27, of the tubes drawn whole in
    front of her: "Now she is not inside them, but just behind them"): as the shaft's run, the tube's inside behind her
    and its two rims in front, so that she is seen crawling through. The edit left each tower's bottom cushion over the
    tube's top (rows 68 to 83 between the rims), so everything over row SEAM but the rims is lifted LIFT rows (the
    cushions then rest on the tube's top, row 72), the inside carried up into the rows freed (its own rows under, without
    the cushion's seam), the canvas LIFT rows taller. The inside's pixels go behind her (`pillow-fort-back.png`), the rest
    in front (`pillow-fort.png`), both cut to one box."""
    src = Image.open(path).convert("RGBA")
    W, H = src.size
    SEAM, TUBE_TOP, LIFT = 84, 72, 12
    # The tubes' columns at a row of their inside: the inside a run of dark (or dark red) px, the rims either side.
    lum = lambda p: 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]
    dark = lambda p: p[3] and lum(p) < 70
    inside = []
    for a, b in ((8, 70), (160, 220)):
        runs, x = [], a
        while x < b:
            if dark(src.getpixel((x, 90))):
                x0 = x
                while x < b and dark(src.getpixel((x, 90))):
                    x += 1
                runs.append((x0, x - 1))
            x += 1
        lo, hi = max(runs, key=lambda r: r[1] - r[0])
        inside.append((lo, hi))
    tube = [(lo - 8, hi + 8) for lo, hi in inside]            # the rims: 8 px either side of the inside
    in_rim = lambda x, y: y >= TUBE_TOP and any(a <= x <= b and not (lo <= x <= hi) for (a, b), (lo, hi) in zip(tube, inside))
    in_inside = lambda x: any(lo <= x <= hi for lo, hi in inside)
    out = Image.new("RGBA", (W, H + LIFT), (0, 0, 0, 0))
    o, sp = out.load(), src.load()
    for y in range(H):
        for x in range(W):
            p = sp[x, y]
            if not p[3]:
                continue
            if y < SEAM and not in_rim(x, y):
                o[x, y] = p                                    # lifted (the canvas grew under it)
            elif y >= SEAM or in_rim(x, y):
                o[x, y + LIFT] = p
    # The inside carried up into the freed rows, from its own rows under the seam; the seam itself the same way.
    for lo, hi in inside:
        for x in range(lo, hi + 1):
            for k in range(LIFT + 1):
                o[x, TUBE_TOP + LIFT + k] = sp[x, SEAM + 1 + k]
    front, back = out.copy(), Image.new("RGBA", out.size, (0, 0, 0, 0))
    f, bk = front.load(), back.load()
    for lo, hi in inside:
        for x in range(lo, hi + 1):
            for y in range(TUBE_TOP + LIFT, H + LIFT):
                if dark(o[x, y]) or (o[x, y][3] and lum(o[x, y]) < 110 and y < H + LIFT - 4):
                    bk[x, y] = o[x, y]
                    f[x, y] = (0, 0, 0, 0)
    box = out.getbbox()
    front.crop(box).save(OUT_DIR / "pillow-fort.png")
    back.crop(box).save(OUT_DIR / "pillow-fort-back.png")
    out.save(HERE / "cutaway-lifted.png")
    print("inside", inside, "fort", box, "->", (box[2] - box[0], box[3] - box[1]))


def holes(path):
    """The user's way, 2026-11-27 (after the tubes drawn whole in front of her read as "not inside them, but just behind
    them", and a cut-open tube as "worse"): seed 44 as it was, and only each opening itself behind her, as at the linen
    room's shaft: she goes into the dark opening, seen in it, and is hidden once past the near wall. Each opening is the
    narrow dark ellipse inset in a tube's end, in dark purples; its rim's red, the near-black outlines and the cushions'
    blues are the wall and stay in front, whole (the first cut took every dark px near an opening, outlines and shading
    too, and she showed through the holes it left: "The cuts are very bad, on all sides")."""
    src = Image.open(path).convert("RGBA")
    W, H = src.size
    sp = src.load()
    hole = lambda p: p[3] and 60 < sum(p[:3]) < 190 and abs(p[0] - p[2]) < 26 and p[1] <= p[0] + 4
    picked = set()
    for a, b in ((10, 30), (40, 66), (160, 180), (196, 218)):
        seen, comps = set(), []
        for x in range(a, b):
            for y in range(72, 102):
                if (x, y) in seen or not hole(sp[x, y]):
                    continue
                comp, stack = [], [(x, y)]
                seen.add((x, y))
                while stack:
                    cx, cy = stack.pop()
                    comp.append((cx, cy))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if a <= nx < b and 72 <= ny < 102 and (nx, ny) not in seen and hole(sp[nx, ny]):
                            seen.add((nx, ny))
                            stack.append((nx, ny))
                comps.append(comp)
        best = max(comps, key=len)
        picked |= set(best)
        xs, ys = [c[0] for c in best], [c[1] for c in best]
        print("opening", (a, b), "->", len(best), "px, x", min(xs), max(xs), "y", min(ys), max(ys))
    front, back = src.copy(), Image.new("RGBA", src.size, (0, 0, 0, 0))
    for x, y in picked:
        back.putpixel((x, y), sp[x, y])
        front.putpixel((x, y), (0, 0, 0, 0))
    box = src.getbbox()
    front.crop(box).save(OUT_DIR / "pillow-fort.png")
    back.crop(box).save(OUT_DIR / "pillow-fort-back.png")
    print("fort", box)


def rings(path):
    """The user's correction of `holes` (2026-11-27: "On all four sides of the openings: the far wall of the tube (and
    the ring on the opening) should be obscured by her. That's what gives the visual look of her getting inside the
    tube"): at each opening, everything from the opening's inner edge outward, in the tube's rows (the dark, the ring
    round it, its outline), goes behind her as one band; the tube's body inward of it stays in front. The inner edge is
    the dark ellipse's innermost column (measured by `holes`' colour rule)."""
    src = Image.open(path).convert("RGBA")
    sp = src.load()
    # (The left tube's bottom outline missing a px, x 53 of row 102: the user, 2026-11-27, "Fill this missing black pixel".)
    sp[53, 102] = sp[52, 102]
    hole = lambda p: p[3] and 60 < sum(p[:3]) < 190 and abs(p[0] - p[2]) < 26 and p[1] <= p[0] + 4
    # (window, which way is outward: -1 left, +1 right)
    ends = (((10, 30), -1), ((40, 66), +1), ((160, 180), -1), ((196, 218), +1))
    ROWS = (70, 104)
    # The dark ellipses' inner edges, as `holes` measured them (each ellipse the connected piece of its colours:
    # x 17-19, 57-58, 169-170, 207-209).
    PLANES = {(10, 30): 19, (40, 66): 57, (160, 180): 170, (196, 218): 207}
    front, back = src.copy(), Image.new("RGBA", src.size, (0, 0, 0, 0))
    for (a, b), way in ends:
        plane = PLANES[(a, b)]                                  # the opening's inner edge
        xs = range(0, plane + 1) if way < 0 else range(plane, src.width)
        xs = [x for x in xs if a - 12 <= x < b + 12]           # only this end of this tube
        for x in xs:
            for y in range(*ROWS):
                if sp[x, y][3]:
                    back.putpixel((x, y), sp[x, y])
                    front.putpixel((x, y), (0, 0, 0, 0))
        print("end", (a, b), "outward", way, "plane", plane)
    box = src.getbbox()
    front.crop(box).save(OUT_DIR / "pillow-fort.png")
    back.crop(box).save(OUT_DIR / "pillow-fort-back.png")
    print("fort", box)


if __name__ == "__main__":
    {"rough": lambda: rough(), "split": lambda: split(sys.argv[2]), "cutaway": lambda: cutaway(sys.argv[2]), "holes": lambda: holes(sys.argv[2]), "rings": lambda: rings(sys.argv[2])}[sys.argv[1]]()
