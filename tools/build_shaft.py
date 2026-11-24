"""The ventilation shaft from the linen room to deck 8 forward (docs/shaft-remake-log.md; the user's remake,
2026-11-23), drawn at its true place and length on the ship by the numbers of tools/build_world.py's
`shaft_geometry()`: cut open along its near side, as the decks are.

Writes, into assets/ship/shaft/:
  strip.png    the shaft's inside, behind her: the mouth standing out of the linen room's forward wall, the slope down
               behind that wall, the long run in the slab between decks 9 and 8, its grilles, its dead end
  front.png    what is nearer than her: the near halves of the joints' flanges
  shaft.json   where the strip stands in the world, and the room's pieces (below)

The room's pieces (the mouth's near side as the linen room shows it, its cover on and knocked off) are cut by
`--mouth` from the generated pictures of the room's corner (assets/source/shaft/gen/mouth-*.png).

How the steel is made. The whole shaft is first drawn flat, by rule, with a real duct's features in their places (a
flanged joint every 2 m, two sheet-metal panels between joints, each with its cross-break crease, the sheet above and
below, the grilles' slots): `--roughs` writes that drawing's pieces into assets/source/shaft/rough/. Each piece was then
redrawn by PixelLab (`edit_image_pro_flash`, which keeps every shape where it is and gives it worn steel; the jobs are
in assets/source/shaft/README.md) into assets/source/shaft/gen/ under the same name. The build lays the redrawn pieces
back along the run: the plain lengths in a fixed shuffled order (each also mirrored: twice as many), a grille length
at each grille, the entry and the dead end at their own places; then the light, by rule: warm up through each grille,
the linen room's cool light a little way into the mouth. A piece that has no redrawn picture yet is laid from the flat
drawing, so the build always runs.

Run from the repo root:
    python tools/build_shaft.py [--roughs] [--mouth] [--preview out.png]
"""

import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ship_map as B                                  # noqa: E402
from build_world import shaft_geometry                      # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source" / "shaft"
GAME = ROOT / "assets" / "ship" / "shaft"

# Resurrect 64's purple greys (the palette's neutral greys go green: CLAUDE.md, the flare's soot); the redraw moves
# them toward a cooler steel of its own, kept (the user's word on generated art: its own colours where they are better).
VOID, INK, DARK, SLATE, STEEL, MID, LIT, PALE = "#1a141c", "#2e222f", "#3e3546", "#625565", "#4a4458", "#57506a", "#7f708a", "#9babb2"
SHEET = 2                 # the duct's sheet above and below its inside, px
JOINT = 96                # a flanged joint every 2 m; a length of duct is its flange (4 px) and two panels
FLANGE = 4
GRILLE = 30               # a floor grille's slot
PAD = 10                  # a piece's rows above and below the duct's inside
RUN_PIECES = ("run-a", "run-b", "run-c")     # plain lengths: each picture holds two
WARM, COOL = (0xff, 0xf1, 0xc9), (0xdf, 0xe8, 0xe2)


def rgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def geometry():
    g = shaft_geometry()
    H = g["height"]
    g["first"] = g["exitX"] - 50                         # the joint just forward of the way out; the rest every JOINT aft of it
    g["joints"] = list(range(g["first"], g["slopeFoot"] - 30, JOINT))
    g["entry"] = g["joints"][-1]                         # the entry piece: from the last joint to the mouth's end
    g["ox"] = g["x0"] - 8
    g["oy"] = g["upper"] - H - PAD
    g["w"] = g["mouthX"] + 4 - g["ox"]
    g["w"] += -(g["w"] - (g["entry"] - g["ox"])) % 4       # (the entry piece's width a multiple of 4: the generator's grid)
    g["h"] = g["lower"] + PAD - g["oy"]
    for gr in g["grilles"]:
        off = (gr["x"] - g["first"]) % JOINT
        assert GRILLE // 2 + FLANGE + 1 <= off <= JOINT - GRILLE // 2 - 1, f"the grille '{gr['what']}' is on a joint ({off} px past it)"
    return g


def floor_at(g, x):
    """The shaft's floor (world y) at world x: the run, the slope, the mouth."""
    if x <= g["slopeFoot"]:
        return g["lower"]
    if x >= g["slopeTop"]:
        return g["upper"]
    k = (x - g["slopeFoot"]) / (g["slopeTop"] - g["slopeFoot"])
    return round(g["lower"] + (g["upper"] - g["lower"]) * k)


def flat(g):
    """The whole shaft drawn flat on the void, every shape in its place: what the pieces are generated from."""
    im = Image.new("RGB", (g["w"], g["h"]), VOID)
    px = im.load()
    H = g["height"]
    for x in range(g["x0"], g["mouthX"]):
        f = floor_at(g, x) - g["oy"]
        c = f - H
        ix = x - g["ox"]
        for y in range(c - SHEET, f + SHEET):
            if y in (c - SHEET, f + SHEET - 1):
                col = INK
            elif y < c or y >= f:
                col = SLATE
            elif y - c < 2:
                col = LIT
            elif f - y <= 2:
                col = SLATE                      # dust
            elif f - y <= 6:
                col = DARK                       # the floor's shadow
            else:
                col = STEEL
            px[ix, y] = rgb(col)
    d = ImageDraw.Draw(im)
    top, bot = g["lower"] - H - g["oy"], g["lower"] - g["oy"]
    rnd = random.Random(5)
    # The run: at each joint a flange; between two, two panels, each with its cross-break crease.
    for n, j in enumerate(g["joints"]):
        ix = j - g["ox"]
        end = (g["joints"][n + 1] if n + 1 < len(g["joints"]) else g["slopeFoot"] - 2) - g["ox"]
        for k, p0 in enumerate((ix + FLANGE, ix + FLANGE + 46)):
            p1 = min(p0 + 45, end - 1)
            if p1 - p0 < 30:
                continue                         # (a short length by the slope's foot: plain)
            d.rectangle([p0, top + 2, p1, bot - 7], fill=MID if k else STEEL)
            d.line([(p0, top + 2), (p1, bot - 7)], fill=DARK)
            d.line([(p0, bot - 7), (p1, top + 2)], fill=LIT)
            if k == 0:
                d.line([(p1 + 1, top), (p1 + 1, bot - 1)], fill=DARK)
        d.rectangle([ix, top - SHEET - 1, ix + FLANGE - 1, bot + SHEET], fill=DARK)
        d.line([(ix + 1, top - SHEET - 1), (ix + 1, bot + SHEET)], fill=LIT)
        for y in (top + 5, top + 17, top + 29):
            d.point((ix + 2, y), fill=PALE)
        for x in range(ix + 8, end - 4, 9):
            if rnd.random() < 0.6:
                d.line([(x, bot - 2), (x + rnd.randint(1, 3), bot - 2)], fill=LIT)
    d.rectangle([g["x0"] - g["ox"], top, g["slopeFoot"] - g["ox"], top + 1], fill=LIT)
    # The dead end: a cap, a step past the way out.
    cap = g["x0"] - g["ox"]
    d.rectangle([cap - SHEET, top - SHEET, cap, bot + SHEET - 1], fill=INK)
    d.rectangle([cap + 1, top, cap + 2, bot - 1], fill=DARK)
    # The slope: a flanged joint at its foot and at its lip, where the elbows meet the straight lengths; a collar where
    # the mouth goes through the room's wall.
    H2 = g["upper"] - g["oy"]
    for x in (g["slopeFoot"] - 2, g["slopeTop"] - 2):
        f = floor_at(g, x + 1) - g["oy"]
        d.rectangle([x - g["ox"], f - H - SHEET - 1, x - g["ox"] + FLANGE - 1, f + SHEET], fill=DARK)
        d.line([(x - g["ox"] + 1, f - H - SHEET - 1), (x - g["ox"] + 1, f + SHEET)], fill=LIT)
    wall = g["roomX"] - g["ox"]
    d.rectangle([wall, H2 - H - SHEET - 2, wall + 3, H2 + SHEET + 1], fill=SLATE)
    d.line([(wall + 1, H2 - H - SHEET - 2), (wall + 1, H2 + SHEET + 1)], fill=PALE)
    # The grilles in the floor (slats across a slot through the sheet), and the way out (a clear opening: its grille
    # is the corridor's, hanging under it).
    for gr in g["grilles"] + [dict(x=g["exitX"], what="exit")]:
        ix = gr["x"] - g["ox"]
        a, b = ix - GRILLE // 2, ix + GRILLE // 2 - 1
        d.rectangle([a - 1, bot - 2, b + 1, bot + SHEET - 1], fill=INK)
        d.rectangle([a, bot - 1, b, bot + SHEET - 1], fill=VOID if gr["what"] == "exit" else WARM)
        if gr["what"] != "exit":
            for x in range(a + 2, b, 4):
                d.line([(x, bot - 1), (x, bot + SHEET - 1)], fill=INK)
    return im


# The way out's grille once it has given way (the user, 2026-11-24: "when it opens, it shouldn't be lit. Also, instead of
# falling down, make it hang by its right edge, as previously"; of three pictures, B): no longer lit from the shaft, it
# swings down on its right edge and hangs under the slot, its face seen a little, the same slats at the same pitch in
# unlit steel (`exit-hang.png`, 8 x 32, its top left at the hinge). The swing: the grille's own profile turned, unlit, a
# quarter about the hinge in frames (at eight times its size, read back at each 8 x 8's middle), then the hanging face.
SWING_CELL = (48, 40)                # each frame's box; the hinge at SWING_PIVOT in it
SWING_PIVOT = (36, 2)                # the grille's right end, a pixel under its top row: where the hanging face's top left is
SWING_ANGLES = (0, 18, 36, 54, 72)   # degrees turned, then the hanging face as the last frame


def exit_swing(grille):
    """`exit-hang.png` and `exit-swing.png` (a strip of SWING_CELL frames) from the way out's grille as the strip draws it."""
    p = grille.load()
    unlit = grille.copy()
    u = unlit.load()
    for y in range(grille.height):
        for x in range(grille.width):
            r, g_, b, a = p[x, y]
            if a and r + g_ + b > 300:
                u[x, y] = rgb(VOID) + (255,)
    hang = Image.new("RGBA", (8, GRILLE + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(hang)
    d.rectangle([0, 0, 7, GRILLE + 1], fill=VOID, outline=INK)
    for y in range(2, GRILLE + 1, 4):
        d.line([(1, y), (6, y)], fill=LIT)
        d.line([(1, y + 1), (6, y + 1)], fill=STEEL)
    d.line([(1, 1), (1, GRILLE)], fill=MID)
    hang.save(GAME / "exit-hang.png")
    W, H = SWING_CELL
    k = 8
    px, py = SWING_PIVOT
    at = (px - grille.width + 1, py - 2)          # the closed grille in its frame: its right end at the hinge
    big = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    big.paste(unlit.resize((unlit.width * k, unlit.height * k), Image.NEAREST), (at[0] * k, at[1] * k))
    strip = Image.new("RGBA", (W * (len(SWING_ANGLES) + 1), H), (0, 0, 0, 0))
    for i, ang in enumerate(SWING_ANGLES):
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if ang == 0:
            fr.paste(unlit, at)
        else:
            turned = big.rotate(ang, resample=Image.NEAREST, center=((px + 1) * k, py * k))
            tp, fp = turned.load(), fr.load()
            for y in range(H):
                for x in range(W):
                    fp[x, y] = tp[x * k + k // 2, y * k + k // 2]
        strip.paste(fr, (i * W, 0))
    last = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    last.paste(hang, SWING_PIVOT)
    strip.paste(last, (len(SWING_ANGLES) * W, 0))
    strip.save(GAME / "exit-swing.png")


def piece_boxes(g):
    """Each piece's box in the strip (x0, y0, x1, y1): the plain lengths' (two to a picture, and 32 px of the lengths
    either side so that the redraw sees what it runs on into), a grille's, the dead end's, the entry's."""
    top = g["lower"] - g["height"] - PAD - g["oy"]
    run = lambda j: (j - 32 - g["ox"], top, j - 32 - g["ox"] + 256, top + g["height"] + 2 * PAD)
    plain = [j for j in g["joints"][2:-3] if not any(j <= gr["x"] < j + 2 * JOINT for gr in g["grilles"])]
    boxes = {"run": run(plain[len(plain) // 2])}
    boxes["end"] = (g["x0"] - 6 - g["ox"], top, g["joints"][1] - g["ox"], top + g["height"] + 2 * PAD)
    w = g["w"] - (g["entry"] - g["ox"])
    boxes["entry"] = (g["entry"] - g["ox"], 0, g["entry"] - g["ox"] + w, g["h"])
    for k, (a, b, c, e) in boxes.items():
        assert (c - a) % 4 == 0 and (e - b) % 4 == 0 and c - a <= 256, (k, c - a, e - b)
    return boxes


def load(name):
    p = SOURCE / "gen" / f"{name}.png"
    return Image.open(p).convert("RGB") if p.exists() else None


def inside_mask(g):
    """Where the shaft is in the strip (its inside, its sheet, its joints' flanges standing a px proud), and where its
    inside alone is: the rest of the strip is clear."""
    whole = Image.new("L", (g["w"], g["h"]), 0)
    inner = Image.new("L", (g["w"], g["h"]), 0)
    wp, ip = whole.load(), inner.load()
    H = g["height"]
    for x in range(g["x0"] - SHEET, g["mouthX"]):
        f = floor_at(g, max(x, g["x0"])) - g["oy"]
        for y in range(f - H - SHEET, f + SHEET):
            wp[x - g["ox"], y] = 255
            if f - H <= y < f and x >= g["x0"]:
                ip[x - g["ox"], y] = 255
    d = ImageDraw.Draw(whole)
    top, bot = g["lower"] - H - g["oy"], g["lower"] - g["oy"]
    for j in g["joints"]:
        d.rectangle([j - g["ox"], top - SHEET - 1, j - g["ox"] + FLANGE - 1, bot + SHEET], fill=255)
    for x in (g["slopeFoot"] - 2, g["slopeTop"] - 2):
        f = floor_at(g, x + 1) - g["oy"]
        d.rectangle([x - g["ox"], f - H - SHEET - 1, x - g["ox"] + FLANGE - 1, f + SHEET], fill=255)
    wall, H2 = g["roomX"] - g["ox"], g["upper"] - g["oy"]
    d.rectangle([wall, H2 - H - SHEET - 2, wall + 3, H2 + SHEET + 1], fill=255)
    return whole, inner


def compose(g):
    """The strip laid from the redrawn pieces (the flat drawing where one is missing), cut to the shaft's own shape, the
    way out and the grilles' slots open, lit; and the joints' near halves, drawn over her."""
    base = flat(g)
    boxes = piece_boxes(g)
    out = base.copy()
    top = boxes["run"][1]
    row = lambda im, x0, x1: im.crop((x0, 0, x1, im.height))
    # The plain lengths: two to a picture, each also mirrored (its flange kept at its forward end).
    lengths = []
    for name in RUN_PIECES:
        im = load(name)
        if im is None:
            continue
        for a in (32, 32 + JOINT):
            seg = row(im, a, a + JOINT)
            lengths.append(seg)
            flip = seg.copy()
            flip.paste(row(seg, FLANGE, JOINT).transpose(Image.FLIP_LEFT_RIGHT), (FLANGE, 0))
            lengths.append(flip)
    # One steel all along: each redrawn piece came back in a tone of its own (bluer, greener, greyer), and laid side by
    # side the lengths read as patches. Each is moved most of the way to the mean of the plain lengths, measured on the
    # upper panel rows, where no grille's light reaches. (A little of its own tone is kept: sheets do differ.)
    def tone(im):
        px = im.load()
        n, acc = 0, [0, 0, 0]
        for y in range(PAD + 4, PAD + 18):
            for x in range(FLANGE + 2, min(im.width, JOINT) - 2):
                for i in range(3):
                    acc[i] += px[x, y][i]
                n += 1
        return [a / n for a in acc]

    def toward(im, target, share=0.8):
        d = [round((t - m) * share) for t, m in zip(target, tone(im))]
        return im.point(lambda v: v) if not any(d) else Image.merge("RGB", [ch.point(lambda v, k=k: max(0, min(255, v + k))) for ch, k in zip(im.split(), d)])

    if lengths:
        target = [sum(t[i] for t in map(tone, lengths)) / len(lengths) for i in range(3)]
        lengths = [toward(s, target) for s in lengths]
    rnd = random.Random(11)
    last = None
    for n, j in enumerate(g["joints"][1:-1], 1):          # (the first length is the dead end's, the last the entry's)
        if not lengths:
            break
        seg = rnd.choice([s for s in lengths if s is not last] or lengths)
        last = seg
        out.paste(seg, (j - g["ox"], top))
    for name in ("end", "entry"):
        im = load(name)
        if im is not None:
            if lengths:
                # (Measured on its own level length: the dead end's past its first joint, the entry's from its left.)
                part = im.crop((18, 0, 18 + JOINT, 2 * PAD + g["height"])) if name == "end" else im.crop((0, im.height - 2 * PAD - g["height"], JOINT, im.height))
                d = [round((t - m) * 0.8) for t, m in zip(target, tone(part))]
                im = Image.merge("RGB", [ch.point(lambda v, k=k: max(0, min(255, v + k))) for ch, k in zip(im.split(), d)])
            out.paste(im, boxes[name][:2])
    whole, inner = inside_mask(g)
    strip = out.convert("RGBA")
    strip.putalpha(whole)
    px, ip = strip.load(), inner.load()
    H = g["height"]
    bot = g["lower"] - g["oy"]
    # The grilles, by rule, wherever each stands along a length (since 2026-11-23 they are placed over what is worth
    # seeing below, not at a length's middle, and the two generated lengths with a grille in them are not used): a
    # slot through the floor's sheet in a dark frame, lit slats across it. The way out: a clear opening.
    # (The way out is a grille like the rest, the user, 2026-11-24: "It should look visually like any other peek cover
    # before it in the shaft"; it is cut out below, to give way under her.)
    for gr in g["grilles"] + [dict(x=g["exitX"])]:
        a, b = gr["x"] - GRILLE // 2 - g["ox"], gr["x"] + GRILLE // 2 - 1 - g["ox"]
        for x in range(a - 1, b + 2):
            for y in range(bot - 2, bot + SHEET):
                frame = x in (a - 1, b + 1) or y == bot - 2 or (x - a) % 4 == 3
                px[x, y] = rgb(INK) + (255,) if frame else WARM + (255,)
    # The light, by rule: warm up through each grille and the way out, strongest at the slot, gone 44 px off; the linen
    # room's cool light into the mouth, gone at the wall.
    def light(cx, cy, colour, reach, most):
        for x in range(max(cx - reach, 0), min(cx + reach + 1, g["w"])):
            for y in range(max(cy - reach, 0), min(cy + 2, g["h"])):
                if not ip[x, y]:
                    continue
                k = 1 - (((x - cx) ** 2 + ((y - cy) * 1.25) ** 2) ** 0.5) / reach
                if k <= 0:
                    continue
                k = most * k * k
                r, gr_, b, a = px[x, y]
                px[x, y] = (round(r + (colour[0] - r) * k), round(gr_ + (colour[1] - gr_) * k), round(b + (colour[2] - b) * k), a)
    for gr in g["grilles"] + [dict(x=g["exitX"])]:
        light(gr["x"] - g["ox"], bot, WARM, 46, 0.5)
    up = g["upper"] - g["oy"]
    for x in range(g["roomX"], g["mouthX"]):
        k = 0.3 * ((x - g["roomX"]) / (g["mouthX"] - g["roomX"])) ** 1.5
        for y in range(up - H, up):
            r, gr_, b, a = px[x - g["ox"], y]
            px[x - g["ox"], y] = (round(r + (COOL[0] - r) * k), round(gr_ + (COOL[1] - gr_) * k), round(b + (COOL[2] - b) * k), a)
    # The way out's grille, lit as the others are, cut out of the strip as a piece of its own (`exit-grille.png`, its top
    # left `EXIT_AT` px from the strip's): it gives way under her and falls with her (`shaftDrop` in src/world/world.js).
    # Under it the shaft's floor is open, and once it has fallen deck 8's ceiling shows the slot (`exit-hole.png`).
    ex = g["exitX"] - GRILLE // 2 - 1 - g["ox"]
    box = (ex, bot - 2, ex + GRILLE + 2, bot + SHEET)
    strip.crop(box).save(GAME / "exit-grille.png")
    for x in range(box[0], box[2]):
        for y in range(box[1], box[3]):
            px[x, y] = (0, 0, 0, 0)
    hole = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0))
    ImageDraw.Draw(hole).rectangle([0, 0, hole.width - 1, hole.height - 1], fill=VOID, outline=INK)
    hole.save(GAME / "exit-hole.png")
    g["exitAt"] = [box[0] + g["ox"], box[1] + g["oy"]]
    exit_swing(Image.open(GAME / "exit-grille.png").convert("RGBA"))      # (the grille as cut, before its place was cleared)
    # The joints' near halves: each flange again, over her, its whole height (the user, 2026-11-24: "let's make the
    # entire line cover us, that would look better"; only its top and foot had been, the foot over her shoes).
    front = Image.new("RGBA", strip.size, (0, 0, 0, 0))
    topy = g["lower"] - H - g["oy"]
    for j in g["joints"]:
        ix = j - g["ox"]
        box = (ix, topy - SHEET - 1, ix + FLANGE, bot + SHEET + 1)
        front.paste(strip.crop(box), box[:2])
    return strip, front


def mouth_pieces(g):
    """The mouth as the linen room shows it, cut from the generated pictures of the room's forward corner (the room's
    own picture with the mouth drawn in: gen/mouth-open.png its end open, mouth-shut.png its cover on, mouth-down.png
    the cover knocked off and leaning by the wall): each piece is what differs from the room's own picture inside its
    box. **The duct's end is one picture, the open one's, in every state**: the cover is cut from the shut picture by
    its own columns and laid over that end, so nothing of the duct changes as the cover comes off."""
    room = Image.open(ROOT / "assets" / "ship" / "linen-room.png").convert("RGB")
    bare = room.crop(MOUTH_CORNER)

    def cut(name, box):
        im = Image.open(SOURCE / "gen" / f"mouth-{name}.png").convert("RGB")
        x0, y0, x1, y1 = box
        out = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
        op, a, b = out.load(), im.load(), bare.load()
        for y in range(y0, y1):
            for x in range(x0, x1):
                if sum(abs(u - v) for u, v in zip(a[x, y], b[x, y])) > MOUTH_DIFF:
                    op[x - x0, y - y0] = a[x, y] + (255,)
        bb = out.getbbox()
        return out.crop(bb), (x0 + bb[0], y0 + bb[1])

    pieces = {name: cut(src, box) for name, (src, box) in MOUTH_CUTS.items()}
    # Half as deep as it was drawn (the user, 2026-11-24: "make the shaft entrance twice as short, now it's protruding too
    # much"): the columns of plain duct between the bolts by the wall and the end's flange cut out, the wall's strut under
    # it kept whole (its top pixel moved in to meet the duct), and the cover moved in with the end.
    (im, (x, y)), (a, b) = pieces["mouth"], MOUTH_SHORTEN
    short = Image.new("RGBA", (im.width - (b - a), im.height), (0, 0, 0, 0))
    short.paste(im.crop((0, 0, a, im.height)), (0, 0))
    short.paste(im.crop((b, 0, im.width, im.height)), (a, 0))
    sx, sy = MOUTH_STRUT
    short.putpixel((sx - 1, sy), im.getpixel((sx, sy)))
    pieces["mouth"] = (short, (x, y))
    cover, (cx, cy) = pieces["cover"]
    pieces["cover"] = (cover, (cx - (b - a), cy))
    return pieces


MOUTH_SHORTEN = (7, 20)              # the mouth's columns cut out (from, to): 13 of its 28
MOUTH_STRUT = (7, 39)
MOUTH_FAR = 12                       # the half-deep mouth's columns from this one on: its inside and its far rim                # the top of the strut under the mouth, in the uncut picture: moved a column in
# The cover's fall, knocked off by Bumbot from the room's side (the user, 2026-11-24: "let it fall flat on the ground,
# rotating while falling"): turned a quarter toward the wall as it drops, frame by frame at the game's pixels (each
# drawn from the cover enlarged eight times, turned, and read back a pixel at the middle of each 8 x 8; the first and
# the last are its own pixels, upright and turned exactly), and lying flat on the floor in front of the mouth.
FALL_FRAMES = 13                     # 0 to 90 degrees, 7.5 apart
FALL_CELL = 42                       # each frame's square, the cover's middle at its middle
FALL_OUT = 14                        # px its middle moves out from the wall as it falls (its foot kicked out)


def fall_frames(cover):
    """The cover's fall: a strip of FALL_FRAMES squares; and where the last one's picture (the cover lying flat, its own
    pixels turned) stands in its square."""
    C, k = FALL_CELL, 8
    ox, oy = (C - cover.width) // 2, (C - cover.height) // 2
    big = Image.new("RGBA", (C * k, C * k), (0, 0, 0, 0))
    big.paste(cover.resize((cover.width * k, cover.height * k), Image.NEAREST), (ox * k, oy * k))
    strip = Image.new("RGBA", (C * FALL_FRAMES, C), (0, 0, 0, 0))
    flat = cover.transpose(Image.ROTATE_90)
    for i in range(FALL_FRAMES):
        ang = 90 * i / (FALL_FRAMES - 1)
        if i == 0:
            fr = Image.new("RGBA", (C, C), (0, 0, 0, 0))
            fr.paste(cover, (ox, oy))
        else:
            turned = big.rotate(ang, resample=Image.NEAREST, center=(C * k / 2, C * k / 2))
            fr = Image.new("RGBA", (C, C), (0, 0, 0, 0))
            tp, fp = turned.load(), fr.load()
            for y in range(C):
                for x in range(C):
                    fp[x, y] = tp[x * k + k // 2, y * k + k // 2]
            if i == FALL_FRAMES - 1:
                bb = fr.getbbox()
                fr = Image.new("RGBA", (C, C), (0, 0, 0, 0))
                fr.paste(flat, (bb[0], bb[1]))
                flat_at = (bb[0], bb[1])
        strip.paste(fr, (i * C, 0))
    return strip, flat, flat_at


MOUTH_CORNER = (0, 32, 96, 128)      # the room's forward corner, in its picture: the box the mouth's pictures are made in
MOUTH_DIFF = 24                      # a pixel is the mouth's when it is this far (r + g + b) from the room's own
# Each piece: the picture it is cut from, and its box in the corner (measured on the pictures enlarged, 2026-11-23).
MOUTH_CUTS = {"mouth": ("open", (3, 22, 32, 69)), "cover": ("shut", (23, 24, 33, 66)), "cover-down": ("down2", (3, 67, 22, 96))}


SLIDE = ROOT / "assets" / "source" / "her" / "shaft-slide"
SLIDE_FPS = 12
SLIDE_ENDS_ON = 4          # the frame of her crawl the clip's last picture was made from (its `end.png`)


def slide_frames():
    """Her slide down the slope: PixMiniMax's clip (assets/source/her/shaft-slide/green-raw-*.png: nine pictures, from
    her crawl at the lip to her crawl at the foot, made on the shaft's own picture turned green so that none of her
    colours is near its) with the shaft taken out of every frame: a pixel is the shaft's when green leads its red and
    its blue by 18. Loose specks go (anything not joined to her within 3 px); her colours go on the palette, her
    blouse's shade as in her sheets. Returns the frames, each the whole picture's size, and the picture's place."""
    from palettize import palettize, blouse_grey
    place = json.loads((SLIDE / "place.json").read_text(encoding="utf-8"))
    frames = []
    for i in range(9):
        im = Image.open(SLIDE / f"green-raw-{i}.png").convert("RGB")
        W, H = im.size
        a = im.load()
        mask = [[not (a[x, y][1] > a[x, y][0] + 18 and a[x, y][1] > a[x, y][2] + 18) for x in range(W)] for y in range(H)]
        # Her: the largest piece, and whatever lies within 3 px of it (a shoe's sole, a strand of hair).
        seen, comps = [[False] * W for _ in range(H)], []
        for y in range(H):
            for x in range(W):
                if mask[y][x] and not seen[y][x]:
                    todo, c = [(x, y)], []
                    seen[y][x] = True
                    while todo:
                        cx, cy = todo.pop()
                        c.append((cx, cy))
                        for nx in range(cx - 3, cx + 4):
                            for ny in range(cy - 3, cy + 4):
                                if 0 <= nx < W and 0 <= ny < H and mask[ny][nx] and not seen[ny][nx]:
                                    seen[ny][nx] = True
                                    todo.append((nx, ny))
                    comps.append(c)
        her = max(comps, key=len)
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        op = out.load()
        for x, y in her:
            op[x, y] = a[x, y] + (255,)
        frames.append(blouse_grey(palettize(out)))
    return frames, place


def build_slide():
    """The slide's frames in a row, cut to the box they all fit in, as an atlas (`slide.png`, `slide.json`: frames "0"
    to "8"); returns where that box stands in the world."""
    frames, place = slide_frames()
    boxes = [f.getbbox() for f in frames]
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    w, h = x1 - x0, y1 - y0
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    atlas = {"frames": {}}
    for i, f in enumerate(frames):
        sheet.paste(f.crop((x0, y0, x1, y1)), (i * w, 0))
        atlas["frames"][str(i)] = {"frame": {"x": i * w, "y": 0, "w": w, "h": h}}
    sheet.save(GAME / "slide.png")
    (GAME / "slide.json").write_text(json.dumps(atlas), encoding="utf-8")
    print("slide", len(frames), "frames of", w, "x", h)
    return dict(x=place["x"] + x0, y=place["y"] + y0, n=len(frames), fps=SLIDE_FPS, endsOn=SLIDE_ENDS_ON)


def rough_mouth(g):
    """Flat stand-ins for the room's pieces, until the generated ones are cut: the mouth's near side, its cover on its
    end, the cover leaning by the wall."""
    H = g["height"]
    w = g["mouthX"] - g["wallX"]
    mouth = Image.new("RGBA", (w + 3, H + 2 * SHEET + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(mouth)
    d.rectangle([0, 1, w - 1, H + 2 * SHEET], fill=PALE, outline=SLATE)
    d.line([(1, 2), (w - 2, 2)], fill="#c7dcd0")
    d.rectangle([w - 3, 0, w + 2, H + 2 * SHEET + 1], fill=LIT, outline=SLATE)
    cover = Image.new("RGBA", (5, H + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(cover)
    d.rectangle([0, 0, 4, H + 1], fill=PALE, outline=SLATE)
    for y in range(3, H, 4):
        d.line([(1, y), (3, y)], fill=DARK)
    down = cover.rotate(-72, expand=True, resample=Image.NEAREST)
    return dict(mouth=mouth, cover=cover, **{"cover-down": down})


def main():
    g = geometry()
    GAME.mkdir(parents=True, exist_ok=True)
    if "--roughs" in sys.argv:
        (SOURCE / "rough").mkdir(parents=True, exist_ok=True)
        base = flat(g)
        base.save(SOURCE / "rough" / "strip.png")
        for name, box in piece_boxes(g).items():
            base.crop(box).save(SOURCE / "rough" / f"{name}.png")
            print("rough", name, box[2] - box[0], "x", box[3] - box[1])
        return
    if "--mouth" in sys.argv:
        # The room's pieces, and where each stands in the world (its top left corner).
        x0, y0 = g["roomX"] + MOUTH_CORNER[0], B.floor_y(g["deck"]) - 128 + MOUTH_CORNER[1]
        where = {}
        pieces = mouth_pieces(g)
        for name, (im, (x, y)) in pieces.items():
            if name == "cover-down":
                continue
            if name == "mouth":
                # Its near side and its far one (the user, 2026-11-24: on hands and knees at it she is "inside of it, not
                # behind it ... behind its wall that is closest to the screen, but obscuring its farther wall"): the
                # inside seen through its open end and the end's far rim (`MOUTH_FAR` on) are drawn behind her.
                far = Image.new("RGBA", im.size, (0, 0, 0, 0))
                far.paste(im.crop((MOUTH_FAR, 0, im.width, im.height)), (MOUTH_FAR, 0))
                far.save(GAME / "mouth-far.png")
                im = im.copy()
                im.paste(Image.new("RGBA", (im.width - MOUTH_FAR, im.height), (0, 0, 0, 0)), (MOUTH_FAR, 0))
            im.save(GAME / f"{name}.png")
            where[name] = [x0 + x, y0 + y]
            print("cut", name, im.size, "at", x, y)
        # The cover's fall, and the cover lying flat where it lands: its middle FALL_OUT px out from where it hung, on
        # the room's floor (the generated `mouth-down2` cover, leaning by the wall, retired 2026-11-24).
        cover, (cx, cy) = pieces["cover"]
        strip, flat, (fx, fy) = fall_frames(cover)
        strip.save(GAME / "cover-fall.png")
        flat.save(GAME / "cover-down.png")
        mid0 = (x0 + cx + cover.width / 2, y0 + cy + cover.height / 2)
        floor = B.floor_y(g["deck"])
        down = [round(mid0[0] + FALL_OUT - flat.width / 2), floor - flat.height]
        where["coverDown"] = down
        # (Where the falling frames' squares stand: first on the cover as it hangs, last on the cover lying flat.)
        where["fall"] = dict(cell=FALL_CELL, frames=FALL_FRAMES,
                             start=[x0 + cx - (FALL_CELL - cover.width) // 2, y0 + cy - (FALL_CELL - cover.height) // 2],
                             end=[down[0] - fx, down[1] - fy])
        print("fall", strip.size, "flat", flat.size, "at", down)
        (GAME / "mouth.json").write_text(json.dumps(where), encoding="utf-8")
        # (The grille at the shaft's other end was the mouth's cover turned, in deck 8's ceiling, until 2026-11-24: it is a
        # grille of the shaft's own now, cut from the strip, `compose`.)
    strip, front = compose(g)
    strip.save(GAME / "strip.png")
    front.save(GAME / "front.png")
    H = g["height"]
    layout = dict(strip=[g["ox"], g["oy"]], grille=GRILLE, exit=g["exitAt"],
                  swing=dict(cell=list(SWING_CELL), pivot=list(SWING_PIVOT), frames=len(SWING_ANGLES) + 1))
    cut = GAME / "mouth.json"
    if cut.exists():
        # (The room's pieces cut from the generated corner, `--mouth` below: where each stands.)
        layout.update(json.loads(cut.read_text(encoding="utf-8")))
    else:
        pieces = rough_mouth(g)
        for name, im in pieces.items():
            im.save(GAME / f"{name}.png")
        layout.update(mouth=[g["wallX"], g["upper"] - H - SHEET - 1], cover=[g["mouthX"], g["upper"] - H - 1],
                      coverDown=[g["wallX"] + 1, B.floor_y(g["deck"])])
    if (SLIDE / "green-raw-0.png").exists():
        layout["slide"] = build_slide()
    (GAME / "shaft.json").write_text(json.dumps(layout, indent=1), encoding="utf-8")
    print("wrote", (GAME / "strip.png").relative_to(ROOT), strip.size)
    if "--preview" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--preview") + 1])
        a = Image.new("RGBA", strip.size, VOID)
        a.alpha_composite(strip)
        a.alpha_composite(front)
        rows = [a.crop((x, 0, x + 480, a.height)) for x in range(a.width - 480, -1, -480)][:5]
        sheet = Image.new("RGBA", (480 * 3, (a.height * 3 + 6) * len(rows)), "#5a5a6e")
        for i, r_ in enumerate(rows):
            sheet.paste(r_.resize((480 * 3, a.height * 3), Image.NEAREST), (0, i * (a.height * 3 + 6)))
        sheet.save(out)


if __name__ == "__main__":
    main()
