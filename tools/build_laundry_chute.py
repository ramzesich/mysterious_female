"""The laundry chute's pieces (the user, 2026-11-24; assets/source/ship/laundry-chute/, its README has the jobs).

From the generated tries the user chose:
  outlet.png    the laundry's chute outlet (try 4): the hood and its duct up into the ceiling, cut from the try by what
                differs from the room's own picture, row by row from its first changed pixel to its last (the try's
                own changes to the ceiling's light beside the duct left out); `tools/draw_rooms.py` lays it into the
                laundry's picture at OUTLET_AT
  cart.png      the laundry cart heaped with towels (the generated cart, edited); `draw_rooms.py` lays it on the floor
  -> assets/ship/chute/towel.png   the towel on her head (try 1), cut from her picture by what changed, its own whites
  -> assets/ship/chute/in.png      her going into the linen room's hatch (clip B), its 16 frames side by side, 128 px
                each, on the palette as her sheets are: what is not the green wall, not the floor, nor the room's own
                hatch (a pixel within HATCH_SAME of it) as long as the flap is shut; loose specks out
  -> assets/ship/chute/chute.json  where each is: the clip's frame over the room, the towel's place over her head

    python tools/build_laundry_chute.py
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from palettize import palettize, blouse_grey, hex_rgb  # noqa: E402

SRC = ROOT / "assets" / "source" / "ship" / "laundry-chute"
OUT = ROOT / "assets" / "ship" / "chute"

# The outlet: the try's box over the laundry's picture (x 152 to 248, rows 0 to 64; `ceiling-in.png`), and the rows it
# was generated in (the mask: x 26 to 70, rows 0 to 30).
OUTLET_FROM = (152, 0)
OUTLET_BOX = (26, 0, 70, 30)
OUTLET_SAME = 40                 # a pixel is the room's when it is this near it (r + g + b)
DUCT_PALE, DUCT_BODY, DUCT_SHINE = (0xce, 0xe0, 0xd5), (0xaf, 0xbd, 0xc0), (0xc2, 0xcd, 0xcf)    # the try's pale, its steel, a shine
# The clip: its 128 px frame's top left in the linen room's picture (the hatch's middle at x 129, 64 px in; row 16),
# the floor's first row in it (the room's FLOOR, 128, less 16), and the hatch's box in it.
CLIP_AT = (129 - 64, 16)
CLIP_FLOOR = 112
HATCH = (64 - 15, 128 - 44 - 16, 64 + 15, 128 - 12 - 16)
HATCH_SAME = 60
CLIP = "climb-b"
REMAP = {"3e3546": "45293f", "966c6c": "f68181"}       # her sheet's (tools/build_sprites.py `HER`)


def green(p):
    r, g, b = p[:3]
    return g > 130 and g > r + 50 and g > b + 40


def outlet():
    room = Image.open(SRC / "ceiling-in.png").convert("RGBA")
    gen = Image.open(SRC / "outlet-4.png").convert("RGBA")
    a, b = room.load(), gen.load()
    x0, y0, x1, y1 = OUTLET_BOX
    out = Image.new("RGBA", room.size, (0, 0, 0, 0))
    o = out.load()
    # (The duct's column: the try's changes that reach the top row; the light beside it is not the outlet's.)
    duct = [x for x in range(x0, x1) if sum(abs(u - v) for u, v in zip(a[x, 0][:3], b[x, 0][:3])) > OUTLET_SAME]
    lo, hi = min(duct), max(duct)
    for y in range(y0, y1):
        row = [x for x in range(x0, x1) if sum(abs(u - v) for u, v in zip(a[x, y][:3], b[x, y][:3])) > OUTLET_SAME]
        # (Only the run joined to the duct's or the hood's own width above: the strip of changed ceiling beside the
        # duct, rows 5 to 8, stands apart from it by a gap.)
        runs, run = [], []
        for x in row:
            if run and x != run[-1] + 1 and x - run[-1] > 2:
                runs.append(run)
                run = []
            run.append(x)
        if run:
            runs.append(run)
        keep = [r for r in runs if r[0] <= hi and r[-1] >= lo]
        if not keep:
            continue
        for x in range(min(r[0] for r in keep), max(r[-1] for r in keep) + 1):
            o[x, y] = b[x, y]
    # The duct up into the ceiling is solid all the way (the user, 2026-11-24: "The white strip looks off"): rows where
    # the try's duct matched the room's own pixels came out empty, the ceiling's light strip showing through it; each such
    # row is the nearest whole one above it. And its highlight, the wall's own pale green-white, read as a gap down it:
    # a steel highlight one column wide.
    whole = None
    for y in range(y0, y1):
        row = [o[x, y] for x in range(lo, hi + 1)]
        if all(c[3] for c in row) and (hi - lo + 1) == len(row):
            if any(o[x, y][3] for x in range(x0, lo)) or any(o[x, y][3] for x in range(hi + 1, x1)):
                break                               # (the hood: wider than the duct)
            whole = row
        elif whole and not any(o[x, y][3] for x in range(x0, lo)):
            for i, x in enumerate(range(lo, hi + 1)):
                o[x, y] = whole[i]
    for y in range(y0, y1):
        pale = [x for x in range(x0, x1) if o[x, y][3] and o[x, y][:3] == DUCT_PALE]
        for x in pale:
            o[x, y] = (DUCT_SHINE if x == pale[0] else DUCT_BODY) + (255,)
    # (Only the outlet itself: a loose dash beside the hood, apart from it, is the try's own leftover.)
    seen, best = set(), []
    for sy in range(out.height):
        for sx in range(out.width):
            if o[sx, sy][3] and (sx, sy) not in seen:
                part, todo = [], [(sx, sy)]
                seen.add((sx, sy))
                while todo:
                    x, y = todo.pop()
                    part.append((x, y))
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < out.width and 0 <= ny < out.height and o[nx, ny][3] and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            todo.append((nx, ny))
                if len(part) > len(best):
                    best = part
    keep = set(best)
    for y in range(out.height):
        for x in range(out.width):
            if o[x, y][3] and (x, y) not in keep:
                o[x, y] = (0, 0, 0, 0)
    # (And a row sticking out past both its neighbours by more than 2 px, the try's dash off the hood's top: cut back.)
    def edges(y):
        xs = [x for x in range(out.width) if o[x, y][3]]
        return (xs[0], xs[-1]) if xs else None
    for y in range(1, out.height - 1):
        e, up, dn = edges(y), edges(y - 1), edges(y + 1)
        if not (e and up and dn):
            continue
        if e[0] < min(up[0], dn[0]) - 2:
            for x in range(e[0], min(up[0], dn[0])):
                o[x, y] = (0, 0, 0, 0)
        if e[1] > max(up[1], dn[1]) + 2:
            for x in range(max(up[1], dn[1]) + 1, e[1] + 1):
                o[x, y] = (0, 0, 0, 0)
    bb = out.getbbox()
    piece = out.crop(bb)
    piece.save(SRC / "outlet.png")
    return {"x": OUTLET_FROM[0] + bb[0], "y": OUTLET_FROM[1] + bb[1], "w": piece.width, "h": piece.height}


def cart():
    im = Image.open(SRC / "cart-towels-1.png").convert("RGBA")
    bb = im.getbbox()
    piece = im.crop(bb)
    piece.save(SRC / "cart.png")
    return {"w": piece.width, "h": piece.height}


def towel():
    """The towel of try 1, by what changed from her own picture and is the towel's (light and unsaturated): the
    generator's few changed pixels of her face are not."""
    her = Image.open(SRC / "her-east.png").convert("RGBA")
    gen = Image.open(SRC / "her-towel-1.png").convert("RGBA")
    a, b = her.load(), gen.load()
    out = Image.new("RGBA", her.size, (0, 0, 0, 0))
    o = out.load()
    for y in range(her.height):
        for x in range(her.width):
            p, q = a[x, y], b[x, y]
            if q[3] < 128:
                continue
            changed = p[3] < 128 or sum(abs(u - v) for u, v in zip(p[:3], q[:3])) > 60
            light = sum(q[:3]) > 420 and max(q[:3]) - min(q[:3]) < 40
            if changed and light:
                o[x, y] = q
    bb = out.getbbox()
    piece = out.crop(bb)
    OUT.mkdir(parents=True, exist_ok=True)
    piece.save(OUT / "towel.png")
    # (Her feet are on her 64 px frame's bottom row; where the towel's top left is from her feet and her middle.)
    feet = her.getbbox()[3]
    return {"dx": bb[0] - 32, "dy": bb[1] - feet, "w": piece.width, "h": piece.height}


def clip():
    room = Image.open(ROOT / "assets" / "ship" / "linen-room.png").convert("RGBA")
    bg = room.crop((CLIP_AT[0], CLIP_AT[1], CLIP_AT[0] + 128, CLIP_AT[1] + 128))
    r = bg.load()
    frames = sorted((SRC / CLIP).glob("*.png"), key=lambda p: int(p.stem))[1:]    # (0 is the start picture as sent)
    strip = Image.new("RGBA", (128 * len(frames), 128), (0, 0, 0, 0))
    remap = {hex_rgb(k): hex_rgb(v) for k, v in REMAP.items()}
    for i, f in enumerate(frames):
        im = Image.open(f).convert("RGBA")
        p = im.load()
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        o = out.load()
        for y in range(CLIP_FLOOR):
            for x in range(128):
                q = p[x, y]
                if q[3] < 128 or green(q):
                    continue
                hx0, hy0, hx1, hy1 = HATCH
                if hx0 <= x <= hx1 and hy0 <= y <= hy1 and sum(abs(u - v) for u, v in zip(q[:3], r[x, y][:3])) < HATCH_SAME:
                    continue                    # the room's own hatch shows through
                o[x, y] = q[:3] + (255,)
        # Loose specks: a pixel with no neighbour kept.
        keep = out.copy()
        k = keep.load()
        for y in range(128):
            for x in range(128):
                if o[x, y][3] and not any(0 <= x + dx < 128 and 0 <= y + dy < 128 and o[x + dx, y + dy][3]
                                          for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))):
                    k[x, y] = (0, 0, 0, 0)
        frame = blouse_grey(palettize(keep, remap))
        strip.alpha_composite(frame, (i * 128, 0))
    OUT.mkdir(parents=True, exist_ok=True)
    strip.save(OUT / "in.png")
    return {"frames": len(frames), "cell": 128, "at": list(CLIP_AT)}


def dive():
    """Her falling head first out of the outlet (try 1, the user's): on the palette as her sheets are, cut to its own box."""
    im = Image.open(SRC / DIVE).convert("RGBA")
    remap = {hex_rgb(k): hex_rgb(v) for k, v in REMAP.items()}
    im = blouse_grey(palettize(im, remap))
    bb = im.getbbox()
    piece = im.crop(bb)
    OUT.mkdir(parents=True, exist_ok=True)
    piece.save(OUT / "dive.png")
    return {"w": piece.width, "h": piece.height}


def towel_fall():
    """The towel sliding off her head and falling like cloth to lie flat (generated from the towel as it lies on her head
    to the flat towel, the user's): its frames side by side, 64 px each, in their own whites; where the towel is in the
    first (the towel on her head) and how low the last one's foot is."""
    frames = sorted((SRC / "towel-fall").glob("*.png"), key=lambda p: int(p.stem))
    strip = Image.new("RGBA", (64 * len(frames), 64), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.alpha_composite(Image.open(f).convert("RGBA"), (i * 64, 0))
    strip.save(OUT / "towel-fall.png")
    first = Image.open(frames[0]).convert("RGBA").getbbox()
    last = Image.open(frames[-1]).convert("RGBA").getbbox()
    return {"frames": len(frames), "cell": 64, "towel": [first[0], first[1]], "foot": last[3]}


DIVE = "dive-1.png"


def main():
    place = {"outlet": outlet(), "cart": cart(), "towel": towel(), "in": clip(), "dive": dive(), "fall": towel_fall()}
    (OUT / "chute.json").write_text(json.dumps(place, indent=1), encoding="utf-8")
    print(json.dumps(place))


if __name__ == "__main__":
    main()
