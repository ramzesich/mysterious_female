"""The balconies' art (decks 8 to 10, region 7; the remake of 2026-11-25, docs/balconies-remake-log.md), from
assets/source/balconies/ and assets/sprites/her.png into assets/ship/balconies/ and assets/sprites/:

  assets/ship/balconies/unit.png       a balcony's recess over its rail: the back wall, the cabin's sliding glass door shut
  assets/ship/balconies/unit-ajar.png  the same with the door slid open on the lit cabin, a sheer curtain in the doorway
  assets/ship/balconies/washing.png    a clothes line between two poles that stand on the floor
  assets/ship/balconies/moves.png      her three moves' frames (the mount onto the rail, the swing onto the partition's
                                       fin, the climb from perch to perch, the crossing round a partition), one cell each
  assets/ship/balconies/balconies.json the cells, each frame's place from the partition's middle and the balcony's floor
  assets/sprites/her-socks.png         her whole sheet in the grip socks, by rule: the same cells as her.png

python tools/build_balconies.py        (after tools/build_sprites.py whenever her sheet changes)
"""
import json
import sys
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import palettize as PZ

SRC = ROOT / "assets/source/balconies"
OUT = ROOT / "assets/ship/balconies"
RAIL = 32                      # the rail's top over a balcony's floor (BALCONY_RAIL_H in tools/build_ship_map.py)
UNIT_X, UNIT_W, UNIT_H = 6, 119, 116 - RAIL      # the recess beside its partition, from the ceiling's edge to the rail
# The clips, in the order they are packed: (name, the try's folder, its frames).
CLIPS = [("mount", "mount-2m", range(0, 9)), ("swing", "swing-1", range(1, 5)), ("climb", "climb-1", range(0, 25)),
         ("along", "along-4", range(0, 13))]
ROW = 16                       # cells in a row of the sheet

# --- The grip socks on her feet, by rule ------------------------------------------------------------------------------
NAVY = {(0x32, 0x33, 0x53), (0x62, 0x55, 0x65)}
SHOE = (0x32, 0x33, 0x53)
DARK = (0x2e, 0x22, 0x2f)
SKIN = {(0xfd, 0xcb, 0xb0), (0xfc, 0xa7, 0x90), (0xf6, 0x81, 0x81), (0xe8, 0x3b, 0x3b)}
PINK, SHADE, RIM, CUFF, DOT = (0xed, 0x80, 0x99), (0xcf, 0x65, 0x7f), (0xa2, 0x4b, 0x6f), (0xf9, 0xb4, 0xc4), (0xf4, 0xf4, 0xf4)


def socked(cell):
    """One picture of her in her shoes, in the grip socks instead. Her shoes are the small navy pieces at a leg's end:
    with the shoe's own navy in them (the specks in her hair and by her eye are only its lighter grey), skin within 3 px,
    and no more than 30 px (her skirt is one big navy piece). Pink, their dark outline a deeper pink, the outline under
    them dotted white (the nubs), the ankle over them a lighter cuff."""
    px = cell.load()
    w, h = cell.size
    seen, shoes = set(), []
    for y in range(h):
        for x in range(w):
            if (x, y) in seen or px[x, y][3] == 0 or px[x, y][:3] not in NAVY:
                continue
            comp, q = [], deque([(x, y)])
            seen.add((x, y))
            while q:
                a, b = q.popleft()
                comp.append((a, b))
                for da in (-1, 0, 1):
                    for db in (-1, 0, 1):
                        c = (a + da, b + db)
                        if 0 <= c[0] < w and 0 <= c[1] < h and c not in seen and px[c][3] and px[c][:3] in NAVY:
                            seen.add(c)
                            q.append(c)
            if len(comp) <= 30:
                shoes.append(comp)
    out = cell.copy()
    o = out.load()

    def has(p, cols, r):
        return any(0 <= p[0] + da < w and 0 <= p[1] + db < h and px[p[0] + da, p[1] + db][3] and px[p[0] + da, p[1] + db][:3] in cols
                   for da in range(-r, r + 1) for db in range(-r, r + 1))

    for comp in shoes:
        S = set(comp)
        if not any(px[p][:3] == SHOE for p in comp) or not any(has(p, SKIN, 3) for p in comp):
            continue
        for (a, b) in comp:
            o[a, b] = (PINK if px[a, b][:3] != SHOE else SHADE) + (255,)
        rim = set()
        for (a, b) in comp:
            for da in (-1, 0, 1):
                for db in (-1, 0, 1):
                    c = (a + da, b + db)
                    if 0 <= c[0] < w and 0 <= c[1] < h and c not in S and px[c][3] and px[c][:3] == DARK:
                        rim.add(c)
        for (a, b) in rim:
            o[a, b] = ((DOT if a % 2 == 0 else RIM) if (a, b - 1) in S else RIM) + (255,)
        for (a, b) in comp:
            for da in range(-2, 3):
                for db in range(-2, 3):
                    c = (a + da, b + db)
                    if 0 <= c[0] < w and 0 <= c[1] < h and px[c][3] and px[c][:3] in SKIN and abs(da) + abs(db) <= 2:
                        o[c] = CUFF + (255,)
    return out


def feet_band(im, rows=6):
    """A generated frame whose socks came out dark (the crossing's clip): her feet are the lowest `rows` rows of her;
    what is not skin there is the sock, pink by its lightness, its lowest pixels dotted white."""
    bb = im.getbbox()
    if not bb:
        return im
    out = im.copy()
    px, o = im.load(), out.load()
    for y in range(bb[3] - rows, bb[3]):
        for x in range(bb[0], bb[2]):
            r, g, b, a = px[x, y]
            if not a or (r, g, b) in SKIN:
                continue
            lum = (r * 3 + g * 6 + b) // 10
            under = y + 1 >= im.height or px[x, y + 1][3] == 0
            o[x, y] = ((DOT if x % 2 == 0 else RIM) if under else SHADE if lum < 70 else PINK) + (255,)
    return out


def her_socks():
    cell = 84
    sh = Image.open(ROOT / "assets/sprites/her.png").convert("RGBA")
    out = sh.copy()
    n = 0
    for cy in range(0, sh.height, cell):
        for cx in range(0, sh.width, cell):
            c = sh.crop((cx, cy, cx + cell, cy + cell))
            if c.getbbox():
                s = socked(c)
                if s.tobytes() != c.tobytes():
                    n += 1
                out.paste(s, (cx, cy))
    out.save(ROOT / "assets/sprites/her-socks.png")
    return n


# --- The pieces -------------------------------------------------------------------------------------------------------
def crisp(im, n):
    return im.convert("RGB").quantize(n, dither=Image.Dither.NONE).convert("RGBA")


def pieces():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, src, n in (("unit", "unit-2", 20), ("unit-ajar", "unit-ajar-1", 28)):
        im = crisp(Image.open(SRC / "tries" / f"{src}.png"), n)
        im.crop((UNIT_X, 0, UNIT_X + UNIT_W, UNIT_H)).save(OUT / f"{name}.png")
    w = Image.open(SRC / "tries/washing-1.png").convert("RGBA")
    bb = w.getbbox()
    w.crop(bb).save(OUT / "washing.png")
    return dict(x=UNIT_X, w=UNIT_W, h=UNIT_H, washing=[bb[2] - bb[0], bb[3] - bb[1]])


# --- Her moves --------------------------------------------------------------------------------------------------------
def moves():
    box = json.loads((SRC / "sets/boxes.json").read_text())
    part, floor = box["part"], box["f9"]
    frames = []
    for name, folder, ids in CLIPS:
        x0, y0 = box["along" if name == "along" else "up"][:2]
        for k, i in enumerate(ids):
            c = Image.open(SRC / "tries" / folder / f"cut-{i:02d}.png").convert("RGBA")
            c = PZ.blouse_grey(PZ.palettize(c)).convert("RGBA")
            if name == "along":
                c = feet_band(c)
            bb = c.getbbox()
            frames.append((name, c.crop(bb), bb[0] + x0 - part, bb[1] + y0 - floor))
    cw, ch = max(f[1].width for f in frames) + 2, max(f[1].height for f in frames) + 2
    rows = (len(frames) + ROW - 1) // ROW
    sheet = Image.new("RGBA", (ROW * cw, rows * ch), (0, 0, 0, 0))
    clips = {}
    for n, (name, im, ox, oy) in enumerate(frames):
        sheet.paste(im, ((n % ROW) * cw + 1, (n // ROW) * ch + 1))
        c = clips.setdefault(name, dict(first=n, at=[]))
        # (where the cell's corner stands: px aft of the partition's middle, px down from the balcony's floor; and how
        # far her lowest row is over that floor, for the layering's rule)
        c["at"].append([ox - 1, oy - 1, -(oy + im.height)])
    sheet.save(OUT / "moves.png")
    return dict(cell=[cw, ch], row=ROW, count=len(frames), clips=clips)


def main():
    meta = dict(rail=RAIL, unit=pieces(), moves=moves())
    (OUT / "balconies.json").write_text(json.dumps(meta, separators=(",", ":")))
    n = her_socks()
    print("wrote", OUT, "cell", meta["moves"]["cell"], {k: len(v["at"]) for k, v in meta["moves"]["clips"].items()}, "; her socks on", n, "frames")


if __name__ == "__main__":
    main()
