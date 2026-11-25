"""The bridge's forward end, near-catch 6's own pieces (deck 10; the user's remake, 2026-11-25;
docs/near-catch-6-remake-log.md).

Each piece was drawn flat by rule into the game's own picture of its place (`assets/source/bridge/rough/`, each with its
`-base.png`, the place without it), redrawn by PixelLab (`edit_image_pro_flash`: "Keep every shape exactly where it is
... redraw only the flat shapes"; `tries/`, the jobs in the folder's README) and is cut here by what differs from the
base inside its box:

- **the alarm station** (`station.png`): a steel pedestal at the console's aft end, one big red button on a striped
  plate on its slanted top, a beacon on a stalk; washed as the bridge's other pieces are (20% toward the wall), its
  button and its beacon kept in their own red. `beacon.png`: the beacon's lamp lit, laid over it by the game.
- **the escape hatch under the ceiling** (`collar.png`), **its lid** (`lid.png`, a strip of frames: across the collar's
  mouth, then swung down on its hinge at the collar's forward edge to hang; drawn by rule at each angle in the
  generated lid's own tones, as the pool's lever is) and **its ladder** (`ladder.png`), let down out of the collar.

`bridge.json` says where each stands (px from its own anchor: the station's middle on the floor, the hatch's column
on the ceiling line) and the lid's hinge.

    python tools/build_bridge.py
"""
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source" / "bridge"
OUT = ROOT / "assets" / "ship" / "bridge"
DIFF = 30                 # a pixel is the piece's when it is this far (r + g + b) from the place's own
WASH, WALL = 0.2, (214, 222, 226)        # the bridge's pieces are washed 20% toward its wall (`-w20`)
D10, CEIL, LADDER_X, STATION_X = 704, 576, 1864, 1989
# The station as the hoop meets it (the user at the preview, 2026-11-25: "When the officer swings, it is not visually
# clear that the button is actually pressed": the hoop came down in front of the station, 8 px under its button and
# 5 px aft of it, the button untouched above it). So the station is 7 px shorter (rows cut out of its body's plain
# parts: the generated picture's rows, from its top) and stands 4 px further aft: the hoop's rim lies across the
# button's foot. And the button has two states: up, and down (its dome's box moved `BUTTON_DOWN` px down behind the
# rim, a little darker). The beacon's lamp lit, laid over the station by the game: its box.
STATION_CUT = [34, 35, 44, 45, 46, 47, 48]
BUTTON, BUTTON_DOWN, BUTTON_DARK = (11, 8, 23, 15), 4, 0.86
LAMP = (27, 0, 33, 6)
# Each piece: the generated picture, the base it is compared with, its box in that picture.
BOXES = {"station": ("station-s1", "station-base", (24, 14, 66, 80)),
         "hatch": ("hatch-s1", "hatch-base", None)}
# The hatch, in the world (px): its collar's box; the lid's hinge under the collar's forward end, its length, its tones
# across (its upper face first), its angle from shut frame by frame (its drop, its swing a little past, its rest); the
# ladder's columns, a clean period of its rows, the rows of its feet, how far up into the collar it reaches, and how
# pale a pixel may be and still be the ladder's (the generator left a light fringe along the rails).
COLLAR = (1846, 576, 1879, 590)
LID_HINGE, LID_LEN = (1853, 590), 26
LID_TONES = [(56, 59, 66), (122, 142, 149), (133, 154, 162), (122, 142, 149), (99, 117, 126), (64, 68, 75)]
LID_ANGLES = [0, 30, 64, 90]
LADDER_COLS, LADDER_PERIOD, LADDER_FEET, LADDER_IN, LADDER_PALE = (1854, 1873), (685, 693), 697, 4, 480


def origins():
    return json.loads((SOURCE / "rough" / "rough.json").read_text(encoding="utf-8"))


def differs(a, b, box, thr=DIFF):
    x0, y0, x1, y1 = box
    out = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    op, ap, bp = out.load(), a.load(), b.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            if sum(abs(u - v) for u, v in zip(ap[x, y], bp[x, y])) > thr:
                op[x - x0, y - y0] = ap[x, y] + (255,)
    return out


def components(im, reach=1):
    w, h = im.size
    p = im.load()
    mask = {(x, y) for y in range(h) for x in range(w) if p[x, y][3]}
    seen, out = set(), []
    for start in sorted(mask):
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
    return sorted(out, key=len, reverse=True)


def keep_big(im, least=12, reach=1):
    """Loose specks go: every piece under `least` px."""
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    op, p = out.load(), im.load()
    dropped = 0
    for comp in components(im, reach):
        if len(comp) < least:
            dropped += len(comp)
            continue
        for x, y in comp:
            op[x, y] = p[x, y]
    return out, dropped


def fill_enclosed(im, src, box):
    """What the piece's outline encloses is the piece's too (a pixel of the place's own colour inside it): empty pixels
    that cannot be reached from the picture's edge take the generated picture's pixel."""
    w, h = im.size
    p, sp = im.load(), src.load()
    outside, todo = set(), [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while todo:
        x, y = todo.pop()
        if (x, y) in outside or not (0 <= x < w and 0 <= y < h) or p[x, y][3]:
            continue
        outside.add((x, y))
        todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    n = 0
    for y in range(h):
        for x in range(w):
            if not p[x, y][3] and (x, y) not in outside:
                p[x, y] = sp[x + box[0], y + box[1]] + (255,)
                n += 1
    return n


def trim(im):
    b = im.getbbox()
    return im.crop(b), b


def wash(im, keep=lambda c: False):
    out = im.copy()
    p = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = p[x, y]
            if a and not keep((r, g, b)):
                p[x, y] = tuple(round(c + (w - c) * WASH) for c, w in zip((r, g, b), WALL)) + (a,)
    return out


def red(c):
    return c[0] > 120 and c[0] > c[1] * 1.8 and c[0] > c[2] * 1.8


def yellow(c):
    return c[0] > 180 and c[1] > 130 and c[2] < 110


def his_colours():
    """The colours of the officer's own frames in the people's sheet (on the palette): his clips are set to them, so that
    he is the same man here as everywhere else on the ship (as on the stage: tools/build_stage.py)."""
    m = json.loads((ROOT / "assets" / "sprites" / "people.json").read_text(encoding="utf8"))
    sheet = Image.open(ROOT / "assets" / "sprites" / "people.png").convert("RGBA")
    cell, cols, who = m["cell"], m["cols"], m["people"]["rival"]
    found = set()
    for clip in ("idle", "walk", "charge", "lunge", "trip", "sit", "swing"):
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


# The clips (assets/source/bridge/clips/, cut by its cut.py): the officer's four as strips of their whole canvases, in
# his sheet's colours; Bumbot's climb in his own colours, mirrored (it was made facing east, and he goes forward).
# A strip's frame lies in the world by `x`/`floor` (the column that is the figure's x, the row under which is the
# floor) or by `x0`/`y0` (its corner).
STRIPS = {"stalk": ("rival-stalk", True, False), "creep": ("rival-creep", True, False), "net": ("rival-net", True, False),
          "netted": ("rival-netted", True, False), "climb": ("bumbot-climb", False, True)}


def ungreen(im):
    """The net's mesh over the green ground came out greenish: such a pixel (its green leading its red and its blue)
    is the grey of its own lightness. Nothing of his is green."""
    out = im.copy()
    p = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = p[x, y]
            if a and g > r + 8 and g > b + 8:
                v = round((r + b) / 2 + (g - (r + b) / 2) * 0.35)
                p[x, y] = (v, v, min(255, v + 6), a)
    return out


def clips():
    src = json.loads((SOURCE / "clips" / "clips.json").read_text(encoding="utf8"))
    colours = his_colours()
    out = {}
    for name, (clip, his, mirror) in STRIPS.items():
        c = src[clip]
        w, h = c["size"]
        strip = Image.new("RGBA", (w * c["frames"], h), (0, 0, 0, 0))
        for i in range(c["frames"]):
            f = Image.open(SOURCE / "clips" / clip / f"{i}.png").convert("RGBA")
            if his:
                f = own(ungreen(f), colours)
            if mirror:
                f = f.transpose(Image.FLIP_LEFT_RIGHT)
            strip.paste(f, (i * w, 0))
        strip.save(OUT / f"{name}.png")
        lie = {"x": c["x"], "floor": c["floor"]} if "x" in c else {"x0": c["x0"] - (w - 1 if mirror else 0), "y0": c["y0"]}
        out[name] = {"frames": c["frames"], "w": w, "h": h, **lie}
        print(name, strip.size, lie)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    org = origins()
    meta = {}

    # --- the alarm station ---------------------------------------------------------------------------------------------
    gen, base, box = BOXES["station"]
    g = Image.open(SOURCE / "tries" / f"{gen}.png").convert("RGB")
    b = Image.open(SOURCE / "rough" / f"{base}.png").convert("RGB")
    st = differs(g, b, box)
    st, dropped = keep_big(st, 20)
    filled = fill_enclosed(st, g, box)
    st, bb = trim(st)
    x0, y0 = org["station"][0] + box[0] + bb[0], org["station"][1] + box[1] + bb[1]
    st.save(OUT / "station-full.png")                     # (as generated: the green sets were made with it)
    low = Image.new("RGBA", (st.width, st.height - len(STATION_CUT)), (0, 0, 0, 0))
    y = 0
    for row in range(st.height):
        if row not in STATION_CUT:
            low.paste(st.crop((0, row, st.width, row + 1)), (0, y))
            y += 1
    up = wash(low, red)
    up.save(OUT / "station.png")
    down = low.copy()
    bx0, by0, bx1, by1 = BUTTON
    dome = low.crop(BUTTON)
    dp = dome.load()
    for yy in range(dome.height):
        for xx in range(dome.width):
            r, g, b, a = dp[xx, yy]
            if a:
                dp[xx, yy] = (round(r * BUTTON_DARK), round(g * BUTTON_DARK), round(b * BUTTON_DARK), a)
    down.paste((0, 0, 0, 0), (bx0, by0, bx1, by0 + BUTTON_DOWN))
    down.alpha_composite(dome, (bx0, by0 + BUTTON_DOWN))
    wash(down, red).save(OUT / "station-down.png")
    lamp = Image.new("RGBA", (LAMP[2] - LAMP[0] + 4, LAMP[3] - LAMP[1] + 4), (0, 0, 0, 0))
    lp, sp = lamp.load(), low.load()
    for yy in range(LAMP[1], LAMP[3]):
        for xx in range(LAMP[0], LAMP[2]):
            if red(sp[xx, yy][:3]) and sp[xx, yy][3]:
                lp[xx - LAMP[0] + 2, yy - LAMP[1] + 2] = (255, 96, 80, 255)
    core = [(x, y) for y in range(lamp.height) for x in range(lamp.width) if lp[x, y][3]]
    cx, cy = sum(x for x, _ in core) / len(core), sum(y for _, y in core) / len(core)
    for x, y in core:
        if abs(x - cx) < 1.6 and abs(y - cy) < 1.6:
            lp[x, y] = (251, 255, 134, 255)
    lamp.save(OUT / "beacon.png")
    top = D10 - low.height
    meta["station"] = {"dx": x0 - 1985, "dy": top - D10, "w": low.width, "h": low.height,
                       "lamp": [LAMP[0] - 2, LAMP[1] - 2], "button": [(bx0 + bx1) // 2, by0]}
    print("station", st.size, "from", (x0, y0), "specks dropped", dropped, "enclosed filled", filled)

    # --- the hatch: its collar, its lid, its ladder -----------------------------------------------------------------------
    gen, base, box = BOXES["hatch"]
    g = Image.open(SOURCE / "tries" / f"{gen}.png").convert("RGB")
    b = Image.open(SOURCE / "rough" / f"{base}.png").convert("RGB")
    ox, oy = org["hatch-open"][0], org["hatch-open"][1]

    def part(x0, y0, x1, y1):
        """The generated picture's own pixels in a world box, where they differ from the place."""
        bx = (x0 - ox, y0 - oy, x1 - ox, y1 - oy)
        return differs(g, b, bx), bx

    # (The collar: the generated one, whole; its mouth's rows too, behind the lid.)
    col, bx = part(*COLLAR)
    col, dropped = keep_big(col, 6)
    fill_enclosed(col, g, bx)
    wash(col, yellow).save(OUT / "collar.png")
    meta["collar"] = {"dx": COLLAR[0] - LADDER_X, "dy": COLLAR[1] - CEIL, "w": col.width, "h": col.height}
    # (The ladder: one clean period of the generated one, its rails and a rung, taken where it stands against the plain
    # wall and repeated up its length; in front of the window the cut took the sea's changed pixels with it.)
    gp = g.load()
    x0, x1 = LADDER_COLS
    rows = list(range(LADDER_PERIOD[0], LADDER_PERIOD[1]))
    length = D10 - (COLLAR[3] - LADDER_IN)
    lad = Image.new("RGBA", (x1 - x0, length), (0, 0, 0, 0))
    lp, bp = lad.load(), b.load()
    for y in range(length):
        wy = D10 - length + y
        src = wy if wy >= LADDER_FEET else rows[(wy - rows[0]) % len(rows)]
        for x in range(x0, x1):
            c, c0 = gp[x - ox, src - oy], bp[x - ox, src - oy]
            if sum(abs(u - v) for u, v in zip(c, c0)) > DIFF and sum(c) < LADDER_PALE:
                lp[x - x0, y] = c + (255,)
    wash(lad).save(OUT / "ladder.png")
    meta["ladder"] = {"dx": x0 - LADDER_X, "top": COLLAR[3] - LADDER_IN - CEIL, "w": lad.width, "h": lad.height, "mouth": COLLAR[3] - CEIL - 2}
    # (The lid: a plate seen edge on, drawn at each angle in the generated lid's own tones, hinged under the collar's
    # forward end; frame 0 shut across the mouth.)
    hx, hy = LID_HINGE
    size, pad = LID_LEN + 16, 12
    strip = Image.new("RGBA", (size * len(LID_ANGLES), size), (0, 0, 0, 0))
    for i, deg in enumerate(LID_ANGLES):
        f = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        fp = f.load()
        a = math.radians(deg)
        al = (math.cos(a), math.sin(a))
        # (Stepped along its longer way, its width laid across in whole px: turned pixel by pixel it comes out ragged.)
        if abs(al[0]) >= abs(al[1]):
            n = round(LID_LEN * al[0])
            for t in range(n):
                y = round(t * al[1] / al[0])
                for c, tone in enumerate(LID_TONES):
                    fp[pad + t, pad + y + c] = (LID_TONES[0] if t in (0, n - 1) else tone) + (255,)
        else:
            n = round(LID_LEN * al[1])
            for t in range(n):
                x = round(t * al[0] / al[1])
                for c, tone in enumerate(LID_TONES):
                    fp[pad + x - 1 - c, pad + t] = (LID_TONES[0] if t in (0, n - 1) else tone) + (255,)
        strip.paste(f, (i * size, 0))
    wash(strip).save(OUT / "lid.png")
    meta["lid"] = {"frame": size, "hinge": [pad, pad], "dx": hx - LADDER_X, "dy": hy - CEIL, "frames": len(LID_ANGLES)}
    print("collar", col.size, "ladder", lad.size, "lid", strip.size)
    meta["clips"] = clips()
    (OUT / "bridge.json").write_text(json.dumps(meta, indent=1), encoding="utf8")


if __name__ == "__main__":
    main()
