"""Generates the whole ship's map (maps/ship.json, Tiled JSON format) and the placeholder tileset
(assets/tiles/placeholder.png) from tools/ship_layout.py: every deck at its real length and
position, the bow on the left (GAME_DESIGN.md §5.3).

The art is placeholder: walls are tinted by what is there (venues, cabins, crew, the atrium) and
venues carry a sign. Positions come from the layout list in metres from the bow; edit that list,
not this file, to move things.

Run from the repo root:  python tools/build_ship_map.py
"""

import json
import struct
import zlib
from pathlib import Path

from ship_layout import ATRIUM, CORES, DECKS, EXTENT, FUNNEL, LENGTH, MAST, PLAYABLE, TRUNKS, VENUES

ROOT = Path(__file__).resolve().parent.parent
TILE = 16
PER_M = 3                                  # tiles per metre: 48px, so the ship is real length (§5.4)
SEA = 30                                   # columns of open sea beyond the bow and the stern
COLS = SEA + LENGTH * PER_M + SEA

# Tile ids (1-based, as stored in Tiled layer data; 0 = empty).
(STEEL, FLOOR, LADDER_TOP, RAILING, LADDER, BACKWALL, TEAK, NAVY, WAINSCOT,
 VENUEWALL, CREWWALL, ATRIUMWALL, DIMWALL, CABIN_CARPET, DECK_PAINT, GLASS_RAIL, POOL_TILE) = range(1, 18)
TILE_COUNT = 17

# Each deck is 8 rows of air over a 1-row floor slab: 144px, a ceiling at ~2.2x her height (§5.4).
DECK_ROWS = 9
DECK_PITCH = DECK_ROWS * TILE
TOP_FLOOR_ROW = 3 * DECK_ROWS - 1          # deck 12's floor; above it, the roof, funnel and mast
FLOOR_ROW = {d: TOP_FLOOR_ROW + (12 - d) * DECK_ROWS for d in DECKS}
ROOF_ROW = FLOOR_ROW[12] - DECK_ROWS       # the roof over deck 12's indoor rooms
WATER_ROW = FLOOR_ROW[3] - 1               # the sea surface: deck 3 sits at the waterline
ROWS = FLOOR_ROW[3] + 10                   # the hull below deck 3, down past the keel

# The card each flight of stairs needs, by the deck it climbs to: her own crew card covers decks
# 4-6, the Hotel card everything above (§6.2).
FLIGHT_CARD = {d: ("crew" if d <= 6 else "hotel") for d in PLAYABLE}

# Deck 12's open stretch over deck 11's pool area, crossed by a side walk (§5.3), and deck 11's
# pools under it, metres from the bow. A pool is sunk two tiles into the deck.
POOL_OPENING = (115, 145)
POOLS = [(119, 131), (134, 140)]
POOL_DEPTH = 2 * TILE

# The atrium's side walks (§5.3) stand a visible step above their deck's floor: she steps up onto
# them.
SIDEWALK_RISE = 8

WALL_FOR = {"venue": VENUEWALL, "cabins": BACKWALL, "crew": CREWWALL, "start": BACKWALL}


def col(m):
    """The column at `m` metres from the bow."""
    return SEA + round(m * PER_M)


def metres(c):
    """Metres from the bow at the middle of column `c`."""
    return (c - SEA + 0.5) / PER_M


def x_of(m):
    """Pixel x at `m` metres from the bow (the middle of its column)."""
    return col(m) * TILE + TILE // 2


def floor_y(deck):
    """Pixel y of the walkable top of a deck's floor."""
    return FLOOR_ROW[deck] * TILE


def walk_y(deck):
    """Where she stands on `deck` in the atrium: on its side walk above deck 5, the atrium floor."""
    lo, hi = ATRIUM["decks"]
    return floor_y(deck) - (SIDEWALK_RISE if lo < deck <= hi else 0)


def funnel_ladder_col():
    """The technical ladder beside the funnel housing, deck 12 up to the roof (§5.1)."""
    return col(FUNNEL[0]) - 3


def clear_of_ladders(deck, m):
    """Is a door at `m` on `deck` clear of every ladder (doors and ladders must not overlap)?"""
    return deck != 12 or abs(m - metres(funnel_ladder_col())) > 1.5


def in_core(m):
    return any(a <= m < b for a, b in CORES.values())


def in_atrium(deck, m):
    (a, b), (lo, hi) = ATRIUM["span"], ATRIUM["decks"]
    return a <= m < b and lo <= deck <= hi


def venue_at(deck, m):
    for d, a, b, name, kind in VENUES:
        if d == deck and a <= m < b:
            return name, kind
    return None, None


def covered(deck, m):
    """Is this spot on `deck` indoors (under a ceiling), rather than an open terrace?"""
    if deck == 12:
        _, kind = venue_at(12, m)
        return in_core(m) or kind in ("venue", "crew", "cabins")
    above = EXTENT[deck + 1]
    return above[0] <= m < above[1]


def indoor(deck, m):
    """Is there a wall behind this spot (a room, a corridor, a core), rather than open air? An
    open deck under the deck above, like the promenade, is covered but not indoors."""
    if in_atrium(deck, m) or in_core(m):
        return True
    _, kind = venue_at(deck, m)
    return covered(deck, m) and kind not in ("outdoor", "finale")


def build_layers():
    solid = [[0] * COLS for _ in range(ROWS)]
    ladders = [[0] * COLS for _ in range(ROWS)]
    back = [[0] * COLS for _ in range(ROWS)]

    def fill(layer, c0, c1, r0, r1, tile):
        for r in range(max(0, r0), min(ROWS - 1, r1) + 1):
            for c in range(max(0, c0), min(COLS - 1, c1) + 1):
                layer[r][c] = tile

    for deck in DECKS:
        fwd, aft = EXTENT[deck]
        floor = FLOOR_ROW[deck]
        c0, c1 = col(fwd), col(aft) - 1
        fill(solid, c0, c1, floor, floor, FLOOR)

        # The back wall, tinted by what is there; open sky on outdoor terraces.
        for c in range(c0, c1 + 1):
            m = metres(c)
            _, kind = venue_at(deck, m)
            if deck == 3:
                tile = DIMWALL
            elif in_atrium(deck, m):
                tile = ATRIUMWALL
            elif in_core(m):
                tile = BACKWALL
            elif not covered(deck, m) or kind in ("outdoor", "finale"):
                tile = 0
            else:
                tile = WALL_FOR.get(kind, BACKWALL)
            if tile:
                fill(back, c, c, floor - DECK_ROWS + 1, floor - 1, tile)
                if tile in (BACKWALL, VENUEWALL, CREWWALL):
                    back[floor - 1][c] = WAINSCOT
            if deck == 12 and covered(12, m):
                solid[ROOF_ROW][c] = STEEL

            # The floor's surface, from the user's photos (§5.3): the cabin corridors' blue-grey
            # wave carpet, the open decks' tan non-skid paint.
            # Open to the sky wins: a corridor's carpet stops where the deck above it ends.
            if deck > 3 and not in_core(m):
                if not covered(deck, m) or kind in ("outdoor", "finale"):
                    solid[floor][c] = DECK_PAINT
                elif kind == "cabins":
                    solid[floor][c] = CABIN_CARPET

        # The deck's ends: a steel wall indoors, a railing on an open terrace; decks 11 and 12 have
        # glass side walls instead (§5.3).
        for c, inward in ((c0, 1), (c1, -1)):
            if covered(deck, metres(c + inward)):
                fill(solid, c, c, floor - DECK_ROWS + 1, floor - 1, STEEL)
            else:
                fill(solid, c, c, floor - 2, floor - 1, GLASS_RAIL if deck >= 11 else RAILING)

        # Where an open deck meets the indoors, an outer wall with a doorway 5 tiles (80px) high.
        if 3 < deck < 12:
            for c in range(c0 + 1, c1):
                if indoor(deck, metres(c - 1)) != indoor(deck, metres(c)):
                    wall = c if indoor(deck, metres(c)) else c - 1
                    fill(solid, wall, wall, floor - DECK_ROWS + 1, floor - 6, STEEL)

    # The hull below deck 3, narrowing down into the sea.
    fwd3, aft3 = EXTENT[3]
    for r in range(FLOOR_ROW[3] + 1, ROWS):
        k = r - FLOOR_ROW[3]
        fill(solid, col(fwd3) + 4 * k, col(aft3) - 1 - k, r, r, STEEL if r <= WATER_ROW + 2 else NAVY)

    # The atrium is open from its floor on deck 5 up through deck 9, and deck 12 over deck 11's pool
    # area (§5.3): their decks cross on side walks, built in the game, not floor tiles.
    lo, hi = ATRIUM["decks"]
    for deck in range(lo + 1, hi + 1):
        fill(solid, col(ATRIUM["span"][0]), col(ATRIUM["span"][1]) - 1, FLOOR_ROW[deck], FLOOR_ROW[deck], 0)
    a, b = POOL_OPENING
    fill(solid, col(a), col(b) - 1, FLOOR_ROW[12], FLOOR_ROW[12], 0)

    # Deck 11's pools, sunk into the deck: tiled sides and bottom, the water filled in by the game.
    for a, b in POOLS:
        top, bottom = FLOOR_ROW[11], FLOOR_ROW[11] + POOL_DEPTH // TILE
        fill(solid, col(a), col(b) - 1, top, bottom - 1, 0)
        fill(solid, col(a) - 1, col(a) - 1, top, bottom, POOL_TILE)
        fill(solid, col(b), col(b), top, bottom, POOL_TILE)
        fill(solid, col(a), col(b) - 1, bottom, bottom, POOL_TILE)

    # Funnel and mast, standing on the roof.
    fill(solid, col(FUNNEL[0]), col(FUNNEL[1]) - 1, ROOF_ROW - 12, ROOF_ROW - 1, STEEL)
    fill(solid, col(MAST[0]) + 6, col(MAST[1]) - 7, ROOF_ROW - 14, ROOF_ROW - 1, STEEL)

    # A technical ladder beside the funnel housing, deck 12 up to the roof (§5.1).
    lc = funnel_ladder_col()
    solid[ROOF_ROW][lc] = LADDER_TOP
    fill(ladders, lc, lc, ROOF_ROW, FLOOR_ROW[12] - 1, LADDER)

    return back, solid, ladders


def point(name, obj_type, x, y, props=None):
    obj = {"id": 0, "name": name, "type": obj_type, "x": x, "y": y, "width": 0, "height": 0,
           "rotation": 0, "visible": True, "point": True}
    if props:
        obj["properties"] = props
    return obj


def prop(name, value, kind="string"):
    return {"name": name, "type": kind, "value": value}


def area(name, obj_type, x, y, width, height, props=None):
    obj = {"id": 0, "name": name, "type": obj_type, "x": x, "y": y, "width": width, "height": height,
           "rotation": 0, "visible": True}
    if props:
        obj["properties"] = props
    return obj


def build_objects():
    objs = []

    def add(obj):
        obj["id"] = len(objs) + 1
        objs.append(obj)

    # The start: the gangway lobby on deck 4, forward, by the forward stairs (§5.3).
    add(point("gangway", "spawn", x_of(67), floor_y(4)))

    # Named places to start at, for testing: ?at=<name> (README).
    for name, deck, m in [("pool", 11, 116), ("deck12", 12, 113), ("atrium", 7, 80), ("atrium-floor", 5, 84),
                          ("promenade", 6, 160), ("bar", 6, 112), ("theatre", 6, 215), ("bridge", 10, 30),
                          ("buffet", 11, 170), ("diner", 11, 205)]:
        add(point(name, "place", x_of(m), floor_y(deck)))
    add(area("shell-door", "decor", x_of(62), floor_y(4) - 80, 3 * TILE + 8, 80, [prop("kind", "shelldoor")]))

    # Stairs: in each core, flights zigzag from deck 4 up to deck 12. Each is a two-point polyline
    # from its lower end to its upper end; holding the key carries her on through a landing.
    for core, (a, b) in CORES.items():
        left, right = col(a) * TILE + 4 * TILE, col(a) * TILE + 15 * TILE
        for deck in PLAYABLE[:-1]:
            x0, x1 = (left, right) if deck % 2 == 0 else (right, left)
            y0, y1 = floor_y(deck), floor_y(deck + 1)
            add({"id": 0, "name": f"stairs-{core}-{deck}-{deck + 1}", "type": "stairs", "x": x0, "y": y0,
                 "width": 0, "height": 0, "rotation": 0, "visible": True,
                 "polyline": [{"x": 0, "y": 0}, {"x": x1 - x0, "y": y1 - y0}],
                 "properties": [prop("card", FLIGHT_CARD[deck + 1])]})
        for deck in PLAYABLE:
            add(point(f"sign-deck-{deck}-{core}", "sign", col(b) * TILE - 3 * TILE, floor_y(deck) - 56,
                      [prop("text", f"DECK {deck}")]))

    # Side walks (§5.3), with a step up at both ends: each deck from 6 to 9 across the atrium, and
    # deck 12 over deck 11's pool area. The atrium's dressing (pillars, the skylight) is its own.
    lo, hi = ATRIUM["decks"]
    ax0, ax1 = col(ATRIUM["span"][0]) * TILE, col(ATRIUM["span"][1]) * TILE
    for d in range(lo + 1, hi + 1):
        add(area(f"sidewalk-atrium-{d}", "sidewalk", ax0, walk_y(d), ax1 - ax0, 0, [
            prop("rise", SIDEWALK_RISE, "int"), prop("style", "atrium")]))
    pa, pb = (col(m) * TILE for m in POOL_OPENING)
    add(area("sidewalk-pool", "sidewalk", pa, floor_y(12) - SIDEWALK_RISE, pb - pa, 0, [
        prop("rise", SIDEWALK_RISE, "int"), prop("style", "deck")]))
    add(area("atrium", "atrium", ax0, floor_y(hi + 1) + TILE, ax1 - ax0, floor_y(lo) - floor_y(hi + 1) - TILE, [
        prop("levels", ",".join(str(walk_y(d)) for d in range(lo + 1, hi + 1)))]))
    for a, b in POOLS:
        add(area(f"pool-{a}", "pool", col(a) * TILE, floor_y(11) + 4, (col(b) - col(a)) * TILE, POOL_DEPTH - 4))
    walks = [{"deck": str(d), "y": walk_y(d)} for d in range(lo + 1, hi + 1)]
    levels = [("5", floor_y(lo))] + [(w["deck"], w["y"]) for w in walks]
    left, right = ax0 + 2 * TILE, ax0 + 12 * TILE
    for i, ((a, y0), (b, y1)) in enumerate(zip(levels, levels[1:])):
        x0, x1 = (left, right) if i % 2 == 0 else (right, left)
        card = FLIGHT_CARD[int(b)]
        add({"id": 0, "name": f"stairs-atrium-{a}-{b}", "type": "stairs", "x": x0, "y": y0,
             "width": 0, "height": 0, "rotation": 0, "visible": True,
             "polyline": [{"x": 0, "y": 0}, {"x": x1 - x0, "y": y1 - y0}],
             "properties": [prop("card", card), prop("curve", True, "bool")]})

    # Elevators (§5.1): one in each core, aft of the stairs, decks 4-12, and the atrium's glass one,
    # decks 5-9, opening onto the side walks. Floors are listed top to bottom with each deck's
    # number and the card it needs.
    def lift(name, x, decks, glass=False):
        decks = sorted(decks, reverse=True)
        stand = walk_y if glass else floor_y
        props = [prop("floors", ",".join(str(stand(d)) for d in decks)),
                 prop("decks", ",".join(str(d) for d in decks)),
                 prop("cards", ",".join(FLIGHT_CARD[d] for d in decks))]
        if glass:
            props.append(prop("glass", True, "bool"))
        add(point(f"lift-{name}", "lift", x, floor_y(decks[0]), props))

    for core, (a, b) in CORES.items():
        lift(core, col(a) * TILE + 18 * TILE, PLAYABLE)
    lift("atrium", x_of(sum(ATRIUM["span"]) / 2), range(ATRIUM["decks"][0], ATRIUM["decks"][1] + 1), glass=True)

    # Venue signs; cabin doors along the corridors (background, muted).
    for deck, a, b, name, kind in VENUES:
        if kind == "cabins":
            # Only under a ceiling: where the deck above ends, the corridor is an open terrace.
            cols = [c for c in range(col(a), col(b)) if covered(deck, metres(c))]
            runs = []
            for c in cols:
                if runs and runs[-1][1] == c:
                    runs[-1][1] = c + 1
                else:
                    runs.append([c, c + 1])
            for c0, c1 in runs:
                add(area(f"cabins-{deck}-{c0}", "decor", c0 * TILE, floor_y(deck), (c1 - c0) * TILE, 0,
                         [prop("kind", "cabindoors")]))
        else:
            add(point(f"sign-{deck}-{a}", "sign", (x_of(a) + x_of(b)) / 2, floor_y(deck) - 100,
                      [prop("text", name.split(" (")[0].upper())]))

    # Checkpoints: crew cabin doors, one at each near-catch spot and a few between (§5.5).
    # A door needs a wall: the ones by the open decks stand just inside.
    for name, deck, m in [("gangway", 4, 71), ("d5-aft", 5, 204), ("d6-promenade", 6, 148),
                          ("d6-theatre", 6, 209), ("d7-casino", 7, 152), ("d9-linen", 9, 115),
                          ("d10-bridge", 10, 44), ("d11-pool", 11, 162), ("d11-buffet", 11, 191),
                          ("d12-sports", 12, 175)]:
        assert indoor(deck, m) and not in_core(m), f"checkpoint {name}: no wall for its door"
        assert clear_of_ladders(deck, m), f"checkpoint {name}: its door stands on a ladder"
        add(point(f"cp-{name}", "checkpoint", x_of(m), floor_y(deck)))

    # Bumbot at his five spots (§4): what he is doing, and which way he runs.
    for name, deck, m, activity, escape in [("theatre", 6, 226, "wash", 1), ("buffet", 11, 178, "sit", 1),
                                            ("pool", 11, 146, "fly", 1), ("bridge", 10, 24, "bat", -1),
                                            ("linen", 9, 112, "asleep", 1)]:
        add(point(f"bumbot-{name}", "bumbot", x_of(m), floor_y(deck),
                  [prop("activity", activity), prop("escape", escape, "int")]))

    # Tangerines (§6.3): ten, each on a side table. One sits behind crates only the dash breaks.
    for i, (deck, m) in enumerate([(4, 30), (4, 150), (4, 236), (5, 60), (5, 170), (6, 120), (6, 245),
                                   (7, 30), (11, 215), (12, 113)]):
        add(point(f"t-{i + 1}", "tangerine", x_of(m), floor_y(deck)))
    for i in range(2):
        for j in range(2):
            add(area(f"crate-{i}-{j}", "breakable", (col(232) + i) * TILE, floor_y(4) - (j + 1) * TILE, TILE, TILE))

    # Escape trunks (§5.1): a door on each deck listed, top to bottom, all at the same x. Each door
    # sits on an indoor wall, clear of the stair cores and the atrium.
    for name, m, decks, opts in TRUNKS:
        for deck in decks:
            assert deck in PLAYABLE and indoor(deck, m) and not in_core(m) and not in_atrium(deck, m) \
                and clear_of_ladders(deck, m), \
                f"trunk {name}: no wall for a door on deck {deck} at {m} m"
        props = [prop("floors", ",".join(str(floor_y(d)) for d in sorted(decks, reverse=True)))]
        if opts.get("one_way"):
            props.append(prop("oneWay", True, "bool"))
        if opts.get("card"):
            props.append(prop("card", opts["card"]))
        add(point(f"trunk-{name}", "trunk", x_of(m), floor_y(max(decks)), props))

    # Furnishing, a first test from the art style test (§8): muted, so it never reads as
    # interactive. Each piece stands on the floor, on another piece, or hangs on the wall `dy`
    # pixels up. Sizes come from the art atlas (tools/build_ship_art.py).
    art = json.loads((ROOT / "assets" / "ship" / "ship.json").read_text(encoding="utf-8"))["frames"]
    height = lambda frame: art[frame]["frame"]["h"]
    width = lambda frame: art[frame]["frame"]["w"]

    def put(deck, m, frame, dy=0, flip=False, x=None):
        props = [prop("frame", frame), prop("dy", dy, "int")]
        if flip:
            props.append(prop("flip", True, "bool"))
        add(point(f"prop-{len(objs)}", "prop", x if x is not None else x_of(m), floor_y(deck), props))

    # The gangway lobby, deck 4.
    put(4, 61.5, "plant-bg")
    put(4, 65, "picture-ship-bg", 44)
    put(4, 69.4, "extinguisher-bg", 14)
    # A Windjammer Bar corner in the deck 6 bars: club chairs round a table, a ship model on a
    # dresser, bar stools along the bar.
    put(6, 112, "club-chair-side-bg")
    put(6, 113.2, "side-table-bg")
    put(6, 114.4, "club-chair-side-bg", flip=True)
    put(6, 116.5, "dresser-bg")
    put(6, 116.5, "ship-model-bg", height("dresser-bg"))
    put(6, 116.5, "sconce-round-bg", 52)
    for i in range(4):
        put(6, 120 + i * 1.1, "bar-stool-bg")
    # The promenade's outer railing along deck 6, with a life ring every 12 m.
    a, b = 150, 194
    for x in range(x_of(a) + 16, x_of(b) - 16, width("railing-bg")):
        put(6, 0, "railing-bg", x=x)
    for m in range(a + 6, b - 3, 12):
        put(6, m, "life-ring-rail-bg")

    # A robot vacuum patrolling the deck 4 cabin corridor.
    add(point("vacuum-1", "vacuum", x_of(130), floor_y(4), [
        prop("minX", x_of(113), "float"), prop("maxX", x_of(186), "float"), prop("speed", 40, "float")]))

    return objs


def tile_layer(layer_id, name, grid):
    return {"id": layer_id, "name": name, "type": "tilelayer", "x": 0, "y": 0, "width": COLS,
            "height": ROWS, "opacity": 1, "visible": True,
            "data": [t for row in grid for t in row]}


def build_map():
    back, solid, ladders = build_layers()
    objs = build_objects()
    return {
        "type": "map", "version": "1.10", "tiledversion": "1.11.0", "orientation": "orthogonal",
        "renderorder": "right-down", "infinite": False, "width": COLS, "height": ROWS,
        "tilewidth": TILE, "tileheight": TILE, "nextlayerid": 5, "nextobjectid": len(objs) + 1,
        "properties": [
            {"name": "deckPitch", "type": "int", "value": DECK_PITCH},
            {"name": "hullMinX", "type": "int", "value": col(EXTENT[4][0]) * TILE},
            {"name": "hullMaxX", "type": "int", "value": col(EXTENT[4][1]) * TILE},
            {"name": "waterY", "type": "int", "value": WATER_ROW * TILE},
        ],
        "tilesets": [{
            "firstgid": 1, "name": "placeholder", "image": "../assets/tiles/placeholder.png",
            "imagewidth": TILE_COUNT * TILE, "imageheight": TILE, "tilewidth": TILE, "tileheight": TILE,
            "tilecount": TILE_COUNT, "columns": TILE_COUNT, "margin": 0, "spacing": 0,
        }],
        "layers": [
            tile_layer(1, "background", back),
            tile_layer(2, "solid", solid),
            tile_layer(3, "ladders", ladders),
            {"id": 4, "name": "objects", "type": "objectgroup", "x": 0, "y": 0, "opacity": 1,
             "visible": True, "draworder": "topdown", "objects": objs},
        ],
    }


# --- Placeholder tileset ------------------------------------------------------------------------

def hex_rgba(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


CLEAR = (0, 0, 0, 0)


def draw_tile(tile_id):
    """Returns a 16x16 grid of RGBA tuples for one placeholder tile."""
    px = [[CLEAR] * TILE for _ in range(TILE)]

    def rect(x0, y0, x1, y1, color):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                px[y][x] = color

    if tile_id == STEEL:
        rect(0, 0, 15, 15, hex_rgba("#c9ced3"))
        rect(0, 0, 15, 0, hex_rgba("#e3e7ea"))
        rect(0, 15, 15, 15, hex_rgba("#a9b0b7"))
        px[3][3] = px[3][12] = px[12][3] = px[12][12] = hex_rgba("#a9b0b7")  # rivets
    elif tile_id in (FLOOR, LADDER_TOP):
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))     # steel slab
        rect(0, 0, 15, 3, hex_rgba("#b8434e"))      # carpet
        rect(0, 0, 15, 0, hex_rgba("#d4626c"))
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
        if tile_id == LADDER_TOP:
            rect(4, 0, 11, 15, hex_rgba("#3a3f47"))  # the hatch the ladder goes through
            rect(3, 0, 3, 15, hex_rgba("#e0e0e0"))
            rect(12, 0, 12, 15, hex_rgba("#e0e0e0"))
            rect(3, 0, 12, 0, hex_rgba("#f2c14e"))   # yellow safety edge
    elif tile_id == RAILING:
        # White rails and posts under a varnished wooden handrail, as on the promenade (§5.3).
        for x in (1, 9):
            rect(x, 3, x + 1, 15, hex_rgba("#ffffff"))
            rect(x + 1, 4, x + 1, 15, hex_rgba("#c7dcd0"))
        rect(0, 8, 15, 8, hex_rgba("#ffffff"))
        rect(0, 12, 15, 12, hex_rgba("#ffffff"))
        rect(0, 0, 15, 2, hex_rgba("#cd683d"))
        rect(0, 0, 15, 0, hex_rgba("#e6904e"))
        rect(0, 2, 15, 2, hex_rgba("#9e4539"))
    elif tile_id == GLASS_RAIL:
        # Decks 11 and 12: glass windbreak panels in white frames, a wooden handrail on top (§5.3).
        rect(0, 3, 15, 15, hex_rgba("#bfe6f5", 150))
        for x, y in ((4, 12), (5, 11), (6, 10), (10, 13), (11, 12)):
            px[y][x] = hex_rgba("#ffffff", 200)          # a glint on the glass
        rect(0, 3, 0, 15, hex_rgba("#ffffff"))
        rect(15, 3, 15, 15, hex_rgba("#e3e7ea"))
        rect(0, 0, 15, 2, hex_rgba("#cd683d"))
        rect(0, 0, 15, 0, hex_rgba("#e6904e"))
        rect(0, 2, 15, 2, hex_rgba("#9e4539"))
    elif tile_id == POOL_TILE:
        # A pool's tiled side and bottom: pale blue tiles with white grout.
        rect(0, 0, 15, 15, hex_rgba("#8fd3ff"))
        for g in (0, 8):
            rect(0, g, 15, g, hex_rgba("#e3f4fb"))
            rect(g, 0, g, 15, hex_rgba("#e3f4fb"))
    elif tile_id == CABIN_CARPET:
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))      # steel slab
        rect(0, 0, 15, 3, hex_rgba("#484a77"))       # blue-grey carpet
        for x, y in ((1, 1), (2, 0), (3, 0), (4, 1), (5, 2), (6, 2), (7, 1),
                     (9, 1), (10, 0), (11, 0), (12, 1), (13, 2), (14, 2), (15, 1)):
            px[y][x] = hex_rgba("#c7dcd0")           # its thin white wave
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id == DECK_PAINT:
        rect(0, 0, 15, 15, hex_rgba("#c7cdd2"))      # white-painted steel slab
        rect(0, 0, 15, 3, hex_rgba("#ab947a"))       # tan non-skid deck paint
        rect(0, 0, 15, 0, hex_rgba("#c2ad92"))
        px[2][4] = px[1][11] = px[3][14] = hex_rgba("#9a8469")  # the non-skid grit
        rect(0, 15, 15, 15, hex_rgba("#a9b0b7"))
    elif tile_id == LADDER:
        rect(3, 0, 3, 15, hex_rgba("#d8dde2"))
        rect(12, 0, 12, 15, hex_rgba("#d8dde2"))
        for y in (2, 7, 12):
            rect(4, y, 11, y, hex_rgba("#b8bec5"))
    elif tile_id == BACKWALL:
        rect(0, 0, 15, 15, hex_rgba("#e9dfcc"))
    elif tile_id == WAINSCOT:
        rect(0, 0, 15, 15, hex_rgba("#e9dfcc"))
        rect(0, 6, 15, 15, hex_rgba("#dccfb8"))      # muted wainscot along the floor
        rect(0, 6, 15, 6, hex_rgba("#cfc1a8"))
    elif tile_id == TEAK:
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        rect(0, 0, 15, 3, hex_rgba("#b07a45"))
        rect(0, 0, 15, 0, hex_rgba("#c8925c"))
        rect(7, 0, 7, 3, hex_rgba("#7d5530"))
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id in (VENUEWALL, CREWWALL, ATRIUMWALL, DIMWALL):
        rect(0, 0, 15, 15, hex_rgba({VENUEWALL: "#dfe6e8", CREWWALL: "#e8dccd",
                                     ATRIUMWALL: "#f1e8cf", DIMWALL: "#b9b4aa"}[tile_id]))
    elif tile_id == NAVY:
        rect(0, 0, 15, 15, hex_rgba("#1d2b53"))
        rect(0, 0, 15, 0, hex_rgba("#2b3d6e"))
    return px


def write_png(path, width, height, pixels):
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in pixels)

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    path.write_bytes(png)


def build_tileset():
    tiles = [draw_tile(i) for i in range(1, TILE_COUNT + 1)]
    rows = [[p for t in tiles for p in t[y]] for y in range(TILE)]
    out = ROOT / "assets" / "tiles" / "placeholder.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    write_png(out, TILE_COUNT * TILE, TILE, rows)
    return out


if __name__ == "__main__":
    map_path = ROOT / "maps" / "ship.json"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(json.dumps(build_map(), separators=(",", ":")), encoding="utf-8")
    print("wrote", map_path.relative_to(ROOT))
    print("wrote", build_tileset().relative_to(ROOT))
