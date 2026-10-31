"""Generates the first-slice map (maps/ship.json, Tiled JSON format) and the placeholder tileset
(assets/tiles/placeholder.png).

The slice is the stern end of decks 3-5 around the deck 4 gangway lobby (GAME_DESIGN.md §7.3). It is
generated rather than hand-drawn so the layout is easy to read and change while the mechanics are
being tuned. Once the ship is laid out for real, the map is edited in Tiled and this script retires.

Run from the repo root:  python tools/build_slice_map.py
"""

import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TILE = 16
COLS, ROWS = 100, 40

# Tile ids (1-based, as stored in Tiled layer data; 0 = empty).
STEEL, FLOOR, LADDER_TOP, RAILING, LADDER, BACKWALL, TEAK, NAVY, WAINSCOT = range(1, 10)
TILE_COUNT = 9

# Deck layout: each deck is 7 rows of air over a 1-row floor slab, so one deck = 8 rows = 128px.
DECK_PITCH = 8 * TILE
FLOOR_ROW = {6: 7, 5: 15, 4: 23, 3: 31}  # row index of each deck's floor slab
STERN = 10                               # hull column at the stern; everything left of it is sea and sky
WATER_ROW = 30                           # sea surface (deck 3 sits below the waterline, as on a real ship)


def floor_y(deck):
    """Pixel y of the walkable top of a deck's floor."""
    return FLOOR_ROW[deck] * TILE


def build_layers():
    solid = [[0] * COLS for _ in range(ROWS)]
    ladders = [[0] * COLS for _ in range(ROWS)]
    back = [[0] * COLS for _ in range(ROWS)]

    def fill(layer, c0, c1, r0, r1, tile):
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                layer[r][c] = tile

    # Interior back wall behind every deck, except the open aft deck on deck 5.
    fill(back, STERN + 1, COLS - 2, 0, 30, BACKWALL)
    for row in FLOOR_ROW.values():
        fill(back, STERN + 1, COLS - 2, row - 1, row - 1, WAINSCOT)
    fill(back, STERN + 1, 23, 8, 14, 0)

    # Deck floors, stern to the slice's forward end.
    for deck, row in FLOOR_ROW.items():
        fill(solid, STERN, COLS - 1, row, row, FLOOR)
    fill(solid, STERN, 23, FLOOR_ROW[5], FLOOR_ROW[5], TEAK)  # open aft deck

    # Stern: deck 6 is closed off (scenery only); deck 5 ends in an open railing; decks 4 and 3 sit
    # inside the hull, which runs down into the sea.
    fill(solid, STERN, STERN, 0, 6, STEEL)
    fill(solid, STERN, STERN, 13, 14, RAILING)
    fill(solid, STERN, STERN, 16, WATER_ROW - 1, STEEL)
    fill(solid, STERN, STERN, WATER_ROW, ROWS - 1, NAVY)
    fill(solid, STERN + 1, COLS - 1, 32, ROWS - 1, STEEL)  # tanks and machinery below deck 3

    # Wall between the open aft deck and the deck 5 interior, with a 64px doorway at floor level.
    fill(solid, 24, 24, 8, 10, STEEL)

    # Forward end of the slice.
    fill(solid, COLS - 1, COLS - 1, 0, 31, STEEL)

    # Atrium: a well through deck 5, and a narrower one through deck 4 underneath. The outer edges
    # are a one-deck drop; the middle drops two decks, which is a scare.
    fill(solid, 80, 86, FLOOR_ROW[5], FLOOR_ROW[5], 0)
    fill(solid, 82, 84, FLOOR_ROW[4], FLOOR_ROW[4], 0)

    # Crew ladder, deck 4 down to deck 3. The cell in the floor is a one-way ladder top.
    solid[FLOOR_ROW[4]][30] = LADDER_TOP
    fill(ladders, 30, 30, FLOOR_ROW[4], FLOOR_ROW[3] - 1, LADDER)

    return back, solid, ladders


def point(obj_id, name, obj_type, x, y, props=None):
    obj = {"id": obj_id, "name": name, "type": obj_type, "x": x, "y": y, "width": 0, "height": 0,
           "rotation": 0, "visible": True, "point": True}
    if props:
        obj["properties"] = props
    return obj


def build_objects():
    objs = []
    next_id = 1

    def add(obj):
        nonlocal next_id
        obj["id"] = next_id
        next_id += 1
        objs.append(obj)

    def col_x(col):
        return col * TILE + TILE // 2

    add(point(0, "gangway", "spawn", col_x(44), floor_y(4)))

    # Checkpoints: crew cabin doors.
    add(point(0, "cp-d4-gangway", "checkpoint", col_x(50), floor_y(4)))
    add(point(0, "cp-d3-crew", "checkpoint", col_x(40), floor_y(3)))
    add(point(0, "cp-d5-aft", "checkpoint", col_x(40), floor_y(5)))

    # Stairwell: from one landing on deck 4, one flight goes up to deck 5 and one goes down to
    # deck 3. Each flight is a two-point polyline from its lower end to its upper end.
    def stairs(name, x0, y0, x1, y1):
        add({"id": 0, "name": name, "type": "stairs", "x": x0, "y": y0, "width": 0, "height": 0,
             "rotation": 0, "visible": True, "polyline": [{"x": 0, "y": 0}, {"x": x1 - x0, "y": y1 - y0}]})

    stairs("stairs-4-5", 60 * TILE, floor_y(4), 70 * TILE, floor_y(5))
    stairs("stairs-3-4", 70 * TILE, floor_y(3), 60 * TILE, floor_y(4))

    # Tangerines. One sits behind a crate stack that only the dash can break.
    add(point(0, "t-aft-deck", "tangerine", col_x(30), floor_y(5)))
    add(point(0, "t-crew-far", "tangerine", col_x(92), floor_y(3)))
    add(point(0, "t-crew-nook", "tangerine", col_x(14), floor_y(3)))

    for i, col in enumerate((20, 21)):
        for j in range(2):
            add({"id": 0, "name": f"crate-{i}-{j}", "type": "breakable", "x": col * TILE,
                 "y": floor_y(3) - (j + 1) * TILE, "width": TILE, "height": TILE, "rotation": 0,
                 "visible": True})

    # Background signs and decor: muted, never interactive (GAME_DESIGN.md §2.1).
    def sign(text, col, deck, rise=44):
        add(point(0, f"sign-{text.lower().replace(' ', '-')}-{col}", "sign", col_x(col), floor_y(deck) - rise,
                  [{"name": "text", "type": "string", "value": text}]))

    sign("GANGWAY", 44, 4, rise=74)
    sign("DECK 4", 57, 4)
    sign("DECK 5", 73, 5)
    sign("DECK 3", 73, 3)
    sign("CREW ONLY", 30, 4)
    # Sized to her, like every human-scale thing (GAME_DESIGN.md §2.1): a double door ~1.3x her height.
    add({"id": 0, "name": "shell-door", "type": "decor", "x": 42 * TILE + 8, "y": floor_y(4) - 64,
         "width": 3 * TILE, "height": 64, "rotation": 0, "visible": True,
         "properties": [{"name": "kind", "type": "string", "value": "shelldoor"}]})

    # A robot vacuum patrolling the deck 3 crew corridor.
    add(point(0, "vacuum-1", "vacuum", col_x(54), floor_y(3), [
        {"name": "minX", "type": "float", "value": 44 * TILE},
        {"name": "maxX", "type": "float", "value": 64 * TILE},
        {"name": "speed", "type": "float", "value": 40},
    ]))

    return objs, next_id


def tile_layer(layer_id, name, grid):
    return {"id": layer_id, "name": name, "type": "tilelayer", "x": 0, "y": 0, "width": COLS,
            "height": ROWS, "opacity": 1, "visible": True,
            "data": [t for row in grid for t in row]}


def build_map():
    back, solid, ladders = build_layers()
    objs, next_obj = build_objects()
    return {
        "type": "map", "version": "1.10", "tiledversion": "1.11.0", "orientation": "orthogonal",
        "renderorder": "right-down", "infinite": False, "width": COLS, "height": ROWS,
        "tilewidth": TILE, "tileheight": TILE, "nextlayerid": 5, "nextobjectid": next_obj,
        "properties": [
            {"name": "deckPitch", "type": "int", "value": DECK_PITCH},
            {"name": "hullMinX", "type": "int", "value": STERN * TILE},
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
        rect(0, 2, 15, 3, hex_rgba("#ffffff"))
        rect(0, 9, 15, 9, hex_rgba("#e8e8e8"))
        for x in (1, 7, 13):
            rect(x, 2, x + 1, 15, hex_rgba("#f4f4f4"))
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
    map_path.write_text(json.dumps(build_map(), indent=1), encoding="utf-8")
    print("wrote", map_path.relative_to(ROOT))
    print("wrote", build_tileset().relative_to(ROOT))
