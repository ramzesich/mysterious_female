"""The ship's side, painted by rules (docs/build-plan.md, step 11; GAME_DESIGN.md §5.3).

The side was one flat off-white. Here it is painted as a picture, one game pixel to a pixel, and
then cut into the map's 16 px tiles, so the game draws it as it drew the flat plating: the same
layers, each tile fading with its deck's cut-away, nothing new to draw each frame.

What is painted, after the user's side photo (reference/photos/side-full.jpg):
- the plating in strakes: faint seams along the side every metre and a half, clear of every row
  of windows, and the plates' butts across them, staggered strake by strake like brickwork; a
  plate here and there a shade lighter or darker than the rest;
- shade under what stands out over the side: the forecastle's deck edge at the bow, the roofs;
- weathering: faint streaks under some of the portholes and under the scuppers along the
  promenade's foot, under the overboard outlets low on the hull, and a dull band where the sea
  washes the side over the dark boot topping;
- what a hull carries: the scuppers and outlets themselves, two shell doors as outlines in the
  plating, the draught marks at the stem and the stern, the bow thrusters' marks, the load line.

Nothing is painted over the livery (the user's placement): seams run under it and are hidden by
it, and every mark keeps clear of its paint.

`paint()` gives the picture as palette indexes (0: the plating as it was) and what is plating;
`cut()` turns it into tiles; `marks()` gives the painted pixels of a part the game draws itself
(the slopes at the decks' ends, the stem's smooth edge) as rectangles.
"""

import zlib

import numpy as np

TILE = 16

# The plating's colours. The side's own white (#e8eaec) is not Resurrect 64's (its whites are
# #ffffff and the green-grey #c7dcd0, both far off it): the near-whites here keep to its family,
# and the marks use the palette's greys.
BASE, LIGHT, UP, DOWN, SEAM, SHADE, SHADE2, STAIN, STAIN2, RUST, SCUM, DARK, MARK, BUTT, TRACE = range(15)
PALETTE = [
    "#e8eaec",   # the plating
    "#f1f3f4",   # a lit edge
    "#ebedef",   # a plate a shade lighter
    "#e5e7ea",   # a plate a shade darker
    "#dbdfe3",   # a seam
    "#d5dade",   # shade
    "#c9ced3",   # deeper shade
    "#dddcd5",   # a streak of weathering, faint
    "#d1cfc5",   # and near its source
    "#d9cbbd",   # rust, faint
    "#d3dbd7",   # the dull band over the waterline
    "#9babb2",   # an opening
    "#7f708a",   # a painted mark
    "#e0e3e6",   # a butt between two plates: fainter than a seam along the side
    "#e3e3df",   # the faintest of a streak, where it thins out
]

STRAKE = 72          # px between seams along the side
SEAM_OVER_FLOOR = 36     # a seam this far over each deck's floor (and STRAKE further up): clear of the windows
PLATE = 384          # px between butts on the hull, give or take: plates of eight metres
LAP = PLATE // 2     # each strake's butts stand this far from the next strake's
HOUSE = 3            # the superstructure's panels are this many times longer, and all one white


def rgba(i):
    h = PALETTE[i].lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def rnd(*key):
    """A steady random number for a key: the same ship every build."""
    return zlib.crc32(":".join(map(str, key)).encode())


def seams(B):
    """The seams' lattice for the game, which draws a few white walls itself: the first seam's y,
    the pitch, the seam's colour and the lit edge's under it."""
    return {"first": (B.floor_y(3) - SEAM_OVER_FLOOR) % STRAKE, "pitch": STRAKE, "seam": PALETTE[SEAM], "lit": PALETTE[LIGHT]}


def paint(B, ext, solid, details, slopes):
    """Paints the side. `B` is the map builder's module, `ext` and `solid` its layers, `details`
    its shapes on the shell (windows, balconies: marks keep clear of them), `slopes` the sloped
    plating at the decks' ends. Returns (picture, tiles, extra): the picture as palette indexes;
    which tiles are plating; and, for the pixels of plating that are no tile's, the part they
    belong to (1: the stem's smooth edge, 2 + i: slope i)."""
    H, W = B.ROWS * TILE, B.COLS * TILE
    ext_a, solid_a = np.array(ext), np.array(solid)
    tiles = np.isin(ext_a, [B.EXT, B.EXT_SLAB, B.EXT_FIXED, B.EXT_FIXED_SLAB]) | ((solid_a == B.HULL) & (ext_a == 0))
    plating = np.repeat(np.repeat(tiles, TILE, axis=0), TILE, axis=1)

    # The parts the game draws itself, in the same flat white: the stem's smooth edge forward of the
    # hull's first tiles, and the slopes where a deck steps back from the one below.
    extra = np.zeros((H, W), np.uint8)
    for y in range((B.FLOOR_ROW[7] + 1) * TILE, (B.WATER_ROW + 1) * TILE):
        edge = int(np.ceil(max(B.stem_x(y / TILE), B.stem_x((y + 1) / TILE)))) + 2
        first = int(np.ceil(B.stem_x(y // TILE + 1) / TILE)) * TILE
        extra[y, edge:first] = 1
    for i, s in enumerate(slopes):
        for y in range(s["yTop"], s["yFloor"]):
            t = (y + 0.5 - s["yTop"]) / (s["yFloor"] - s["yTop"])
            xe = s["x1"] + (s["x0"] - s["x1"]) * t
            a, b = sorted((xe, s["x1"]))
            a, b = int(np.ceil(a)) + (2 if s["x0"] < s["x1"] else 0), int(b) - (0 if s["x0"] < s["x1"] else 2)
            extra[y, a:b] = 2 + i
    extra[plating] = 0
    region = plating | (extra > 0)

    # What stands on the side (a window, a balcony): seams' butts and marks keep clear of it.
    busy = np.zeros((H, W), bool)
    holes = []                                   # the round portholes: (x, y, r)
    for shapes in details.values():
        for s in shapes:
            if s[0] == "r":
                x, y, w, h = s[1:5]
                busy[max(0, y):y + h, max(0, x):x + w] = True
            elif s[0] == "c":
                x, y, r = s[1:4]
                busy[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1] = True
                if s[4] == B.FRAME and r in (6, B.PORTHOLE_R):
                    holes.append((x, y, r))
    painted = livery(B, H, W)

    img = np.zeros((H, W), np.uint8)
    water = B.WATER_ROW * TILE - 14              # the boot topping's top
    hull_top = (B.FLOOR_ROW[7] + 1) * TILE       # under the forecastle
    x_bow, x_stern = B.SEA * TILE, B.col(B.EXTENT[3][1]) * TILE

    def clear(x0, y0, x1, y1, margin=2):
        """Is this box plating all through, with no window on it and no paint of the livery?"""
        a, b, c, d = x0 - margin, y0 - margin, x1 + margin, y1 + margin
        if a < 0 or b < 0 or c > W or d > H:
            return False
        return bool(region[b:d, a:c].all()) and not busy[b:d, a:c].any() and not painted[b:d, a:c].any()

    # --- The strakes: seams along the side, the plates' butts across them, a plate's own shade ---
    seams = [y for y in range((B.floor_y(3) - SEAM_OVER_FLOOR) % STRAKE, water, STRAKE)]
    tone = np.zeros((H, W), np.uint8)
    butts = []
    for j, (y0, y1) in enumerate(zip([-1] + seams, seams + [water])):
        xs = []
        n = 0
        hull = y1 > B.floor_y(7)                 # the hull: up to the forecastle and the promenade
        pitch = PLATE if hull else PLATE * HOUSE
        while True:
            x = x_bow - pitch + n * pitch + (pitch // 2 if j % 2 else 0) + TILE * (rnd("butt", j, n) % 7 - 3)
            n += 1
            if x >= W:
                break
            if x < 8:
                continue
            for _ in range(10):
                # Not through a window, nor grazing one's side.
                col_busy = busy[y0 + 1:y1, x]
                grazing = (busy[y0 + 1:y1, x - 5:x + 6] != col_busy[:, None]).any()
                if not grazing:
                    break
                x += 8
            else:
                continue
            xs.append(x)
        for n, (a, b) in enumerate(zip([0] + xs, xs + [W])):
            r = rnd("tone", j, n) % 100
            if hull and r < 26:
                tone[y0 + 1:y1, a:b] = UP if r < 13 else DOWN
        butts += [(x, y0 + 1, y1) for x in xs]
    img[:] = tone
    for x, y0, y1 in butts:
        img[y0:y1, x] = BUTT
    for y in seams:
        img[y, :] = SEAM
        img[y + 1, :] = np.where(tone[y + 1, :] == DOWN, BASE, LIGHT)      # the lower plate's lit edge

    # --- Shade under what stands out over the side --------------------------------------------
    # The forecastle's deck edge over the bow's flare; the roof's edge over deck 12's walls.
    bow_end = B.col(B.BOW["block"]) * TILE
    for k, c in enumerate((SHADE2, SHADE, SHADE, SEAM, SEAM)):
        img[hull_top + k, :bow_end] = c
    roof = (B.ROOF_ROW + 1) * TILE
    for k, c in enumerate((SHADE, SEAM)):
        img[roof + k, :] = c

    # The balconies' fascia, the white band between two rows of them: a joint under each partition,
    # and a fine line at the foot of the glass.
    for deck, x in B.BALCONY_UNITS:
        floor = B.floor_y(deck)
        img[floor - 8, x:x + 125] = SEAM
        img[floor - 6:floor + 28, x + 2] = BUTT

    # --- Weathering ----------------------------------------------------------------------------
    def streak(x, y, length, width=2, strong=STAIN, faint=TRACE, key=0):
        """A streak running down from (x, y): a stain, not a line: strong only at its head, then
        faint, ragged along one side, breaking up and thinning out to nothing."""
        length = min(length, water - y)
        if length < 6 or not clear(x - 2, y, x + width + 2, y + length, 1):
            return False
        for k in range(length):
            t = k / length
            for i in range(width):
                r = rnd("streak", key, k, i) % 100
                if t < 0.3:
                    c = strong if i == 0 or (t < 0.12 and r < 60) else faint
                elif i == 0 and (t < 0.62 or r < 100 * (1 - t) * 1.8):
                    c = faint                    # its core: whole, then breaking up
                elif i > 0 and r < 100 * (0.8 - t):
                    c = faint                    # its side: ragged from the start
                else:
                    continue
                img[y + k, x + i] = c
        return True

    for x, y, r in holes:
        if rnd("hole", x, y) % 100 < (38 if r > 6 else 55):
            side = rnd("holeside", x) % 3 - 1
            streak(x + side * (r // 2) - 1, y + r + 2, 12 + rnd("holelen", x, y) % (34 if r > 6 else 20), key=x)

    # The scuppers along the promenade's foot (the hull's top edge, deck 6's floor): a small slot
    # every nine metres or so, the longest streaks on the side under them.
    pa, pb = B.PROMENADE["span"]
    y = B.floor_y(B.PROMENADE["deck"]) + TILE + 5
    m = pa + 3.0
    while m < pb - 2:
        x = B.exact_x(m) + rnd("scupper", int(m)) % 40
        if clear(x - 2, y - 2, x + 8, y + 6):
            img[y:y + 2, x:x + 4] = DARK
            img[y - 1, x:x + 4] = SHADE
            streak(x + 1 + rnd("scupperx", x) % 2, y + 2, 26 + rnd("scupperlen", x) % 50, key=x)
        m += 8.6 + (rnd("scuppergap", int(m)) % 20) / 10

    # The overboard outlets low on the hull: a round opening, rust under it down to the waterline.
    m = 34.0
    while m < 246:
        x = B.exact_x(m)
        y = water - 34 - rnd("outlety", x) % 22
        if clear(x - 4, y - 4, x + 5, water):
            img[y - 2:y + 3, x - 1:x + 2] = DARK
            img[y - 1:y + 2, x - 2:x + 3] = DARK
            img[y - 3, x - 1:x + 2] = SHADE
            streak(x - 1, y + 3, water - y - 3, strong=RUST, faint=STAIN, key=x)
        m += 17 + rnd("outletgap", int(m)) % 13

    # Where the sea washes the side, over the boot topping: a dull band with a ragged top.
    for x in range(0, W, 2):
        h = 3 + rnd("scum", x // 6) % 4 + (rnd("scum2", x) % 2)
        img[water - h:water, x:x + 2] = SCUM
    # And scuffs low on the side (fenders, tugs): a few faint smudges, thinning out to their edges.
    m = 24.0
    while m < 250:
        k = int(m)
        x, w, h = B.exact_x(m), 26 + rnd("scuffw", k) % 44, 8 + rnd("scuffh", k) % 12
        y = water - 14 - h - rnd("scuffy", k) % 46
        if clear(x, y, x + w, y + h):
            for yy in range(h):
                for xx in range(w):
                    # An ellipse with a wavering rim; fewer pixels the further out.
                    u, v = (xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)
                    d = (u * u + v * v) ** 0.5 + 0.18 * np.sin(xx * 0.7 + k) + 0.12 * np.sin(yy * 1.3 + k)
                    if d < 0.55 and (xx + yy) % 2 == 0 or d < 0.95 and rnd("scuff", k, xx, yy) % 4 == 0:
                        img[y + yy, x + xx] = STAIN
        m += 21 + rnd("scuffgap", k) % 17

    # --- What a hull carries ---------------------------------------------------------------------
    # Two shell doors on deck 3 (stores, bunkering): outlines in the plating, their hinges.
    for m in (150.5, 224.5):
        x0, y0, w, h = B.exact_x(m), B.floor_y(3) - 104, 92, 98
        if clear(x0 - 2, y0 - 2, x0 + w + 2, y0 + h + 2):
            img[y0:y0 + h, x0:x0 + w] = BASE
            img[y0, x0 + 2:x0 + w - 2] = img[y0 + h - 1, x0 + 2:x0 + w - 2] = SHADE
            img[y0 + 2:y0 + h - 2, x0] = img[y0 + 2:y0 + h - 2, x0 + w - 1] = SHADE
            img[y0 + 1, x0 + 1] = img[y0 + 1, x0 + w - 2] = img[y0 + h - 2, x0 + 1] = img[y0 + h - 2, x0 + w - 2] = SHADE
            img[y0 + 1, x0 + 2:x0 + w - 2] = LIGHT
            img[y0 + 2:y0 + h - 2, x0 + w // 2] = SEAM                       # its two leaves
            for yy in (y0 + 14, y0 + h - 20):
                img[yy:yy + 6, x0 - 2:x0 + 2] = DARK                         # hinges
                img[yy:yy + 6, x0 + w - 2:x0 + w + 2] = DARK
            streak(x0 + 6, y0 + h, 26, key=x0)
            streak(x0 + w - 9, y0 + h, 18, key=x0 + 1)

    # The draught marks at the stem and the stern: a ladder of ticks up from the waterline.
    def draught(x):
        if not clear(x - 2, water - 66, x + 9, water - 2):
            return
        for k in range(8):
            yy = water - 10 - k * 7
            img[yy:yy + 2, x:x + (7 if k % 2 == 0 else 4)] = MARK

    stem_at = int(B.stem_x((water - 30) / TILE))
    draught(stem_at + 40)
    draught(x_stern - 70)
    # The bow thrusters' marks: a ring with a cross, twice, over the waterline.
    def ring(cx, cy, r=6, cross=True):
        if not clear(cx - r - 1, cy - r - 1, cx + r + 2, cy + r + 2):
            return
        for yy in range(-r, r + 1):
            for xx in range(-r, r + 1):
                d = (xx * xx + yy * yy) ** 0.5
                if r - 1.1 <= d <= r + 0.3 or (cross and abs(abs(xx) - abs(yy)) == 0 and d < r - 1):
                    img[cy + yy, cx + xx] = MARK

    for k in range(2):
        ring(stem_at + 96 + k * 34, water - 22)
    # The load line amidships: a ring with a line through it, its little ladder beside it.
    lx = B.exact_x(131)
    if clear(lx - 10, water - 34, lx + 34, water - 6):
        ring(lx, water - 20, 6, cross=False)
        img[water - 21:water - 19, lx - 9:lx + 10] = MARK
        img[water - 30:water - 10, lx + 16] = MARK
        for k, w in enumerate((8, 6, 8, 6)):
            img[water - 30 + k * 6, lx + 16:lx + 16 + w] = MARK

    img[~region] = 0
    return img, tiles, extra


def livery(B, H, W):
    """Where the livery's paint is, as a picture of the whole map."""
    from PIL import Image
    from build_livery import ORIGIN

    painted = np.zeros((H, W), bool)
    src = B.ROOT / "assets" / "source" / "livery" / "livery.png"
    if src.exists():
        a = np.asarray(Image.open(src).convert("RGBA"))[..., 3] > 0
        ox, oy = ORIGIN
        painted[oy:oy + a.shape[0], ox:ox + a.shape[1]] = a[:H - oy, :W - ox]
    return painted


def cut(B, img, tiles, ext, solid, first_id):
    """The picture as tiles. Every tile of plating whose 16 x 16 pixels are not the plain plating
    gets a tile of its own kind (cut away with its deck or not) with those pixels, the same ones
    shared. Returns (ext, solid, pictures, kinds): the layers with the new ids in, each new
    tile's pixels as palette indexes (in id order from `first_id`), and each one's old id."""
    ext2, solid2 = [row[:] for row in ext], [row[:] for row in solid]
    ids, pictures, kinds = {}, [], []
    for r, c in zip(*np.nonzero(tiles)):
        block = img[r * TILE:(r + 1) * TILE, c * TILE:(c + 1) * TILE]
        if not block.any():
            continue
        layer = ext2 if ext[r][c] else solid2
        old = layer[r][c]
        key = (old, block.tobytes())
        if key not in ids:
            ids[key] = first_id + len(pictures)
            pictures.append(block.copy())
            kinds.append(old)
        layer[r][c] = ids[key]
    return ext2, solid2, pictures, kinds


def marks(img, where):
    """The painted pixels of one part the game draws itself, as [x, y, w, h, colour] runs."""
    out = []
    ys, xs = np.nonzero(where & (img > 0))
    if not len(ys):
        return out
    for y in np.unique(ys):
        row = np.sort(xs[ys == y])
        start = prev = int(row[0])
        for x in list(map(int, row[1:])) + [None]:
            if x is not None and x == prev + 1 and img[y, x] == img[y, start]:
                prev = x
                continue
            out.append([start, int(y), prev - start + 1, 1, PALETTE[img[y, start]]])
            if x is not None:
                start = prev = x
    return out
