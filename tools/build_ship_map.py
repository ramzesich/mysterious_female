"""Generates the whole ship's map (maps/ship.json, Tiled JSON format) and the placeholder tileset
(assets/tiles/placeholder.png) from tools/ship_layout.py: every deck at its real length and
position, the bow on the left (GAME_DESIGN.md §5.3).

The art is placeholder: walls are tinted by what is there (venues, cabins, crew, the atrium) and
venues carry a sign. Positions come from the layout list in metres from the bow; edit that list,
not this file, to move things.

Run from the repo root:  python tools/build_ship_map.py
"""

import json
import math
import struct
import zlib
from pathlib import Path

from ship_layout import (ATRIUM, BOW, CORES, DECKS, EXTENT, FRONT_WALL, FUNNEL, HULL_PLAIN_TO, LENGTH, MAST, PLAYABLE,
                         OUR_CABIN, LINEN_ROOM, BRIDGE_WALL_M, SPA_WALL_M, PROMENADE, STAGE, TRUNKS, VENUES)

ROOT = Path(__file__).resolve().parent.parent
TILE = 16
PER_M = 3                                  # tiles per metre: 48px, so the ship is real length (§5.4)
SEA = 30                                   # columns of open sea beyond the bow and the stern
COLS = SEA + LENGTH * PER_M + SEA

# Tile ids (1-based, as stored in Tiled layer data; 0 = empty).
(STEEL, FLOOR, LADDER_TOP, RAILING, LADDER, BACKWALL, TEAK, NAVY, WAINSCOT,
 VENUEWALL, CREWWALL, ATRIUMWALL, DIMWALL, CABIN_CARPET, DECK_PAINT, GLASS_RAIL, POOL_TILE, HULL,
 LOBBY_CARPET, MAHOGANY, CABIN_WALL, FRAMES, END_WALL_L, END_WALL_R, FRAMES_RIB, SLAB,
 EXT, EXT_SLAB, EXT_FIXED, EXT_FIXED_SLAB, EXT_EDGE_L, EXT_EDGE_R, EXT_CORNER_L, EXT_CORNER_R, HIDDEN,
 WALNUT, CUCINA_WALL, DINING_WALL, DINING_CARPET, DIAMOND_CARPET, ATRIUM_CARPET,
 BLISS_WALL, WINDJAMMER_WALL, GALLERY_WALL, THEATRE_WALL, BURL_WALL, WOOD_FLOOR, BLISS_CARPET,
 LIBRARY_CARPET, THEATRE_CARPET, LOBBY6_CARPET,
 KIDS_WALL, TEEN_WALL, CASINO_WALL, ARCADE_WALL, KIDS_CARPET, CASINO_CARPET, ARCADE_CARPET,
 BALCONY_RAIL, BRIDGE_WALL, BRIDGE_FLOOR, SPA_WALL, SAUNA_WALL, GYM_FLOOR, CAFE_WALL, CAFE_CARPET) = range(1, 67)
TILE_COUNT = 66

# The furnished rooms' own walls and carpets (the user's photos, §5.3): the wall, and the carpet.
# La Cucina's first metres are the grey-blue wall its marble portico stands on.
ROOM_LOOK = {
    "La Cucina": (WALNUT, DIAMOND_CARPET),
    "Four Seasons": (DINING_WALL, DINING_CARPET),
    "Seven Seas": (DINING_WALL, DINING_CARPET),
    "Shore excursions, reservations": (VENUEWALL, LOBBY_CARPET),
    "Internet Café": (VENUEWALL, CABIN_CARPET),
    "Bliss Ultra Lounge": (BLISS_WALL, BLISS_CARPET),
    "Gift Shops, Perspectives Photo Studio": (DINING_WALL, WOOD_FLOOR),
    "Windjammer Bar": (WINDJAMMER_WALL, WOOD_FLOOR),
    "Photo Gallery": (GALLERY_WALL, WOOD_FLOOR),
    "Library": (WALNUT, LIBRARY_CARPET),
    "Stardust Lounge theatre (Bumbot: washing)": (THEATRE_WALL, THEATRE_CARPET),
    "Splash Academy": (KIDS_WALL, KIDS_CARPET),
    "Entourage": (TEEN_WALL, ARCADE_CARPET),
    "Magnum's": (WALNUT, DINING_CARPET),
    "Art Gallery": (GALLERY_WALL, WOOD_FLOOR),
    "Sun Club Casino": (CASINO_WALL, CASINO_CARPET),
    "Tradewinds": (DINING_WALL, WOOD_FLOOR),
    "Arcade": (ARCADE_WALL, ARCADE_CARPET),
    "Stardust Lounge balcony": (THEATRE_WALL, THEATRE_CARPET),
    "Bridge (Bumbot: controls)": (BRIDGE_WALL, BRIDGE_FLOOR),
    # Deck 11 (NCL's plan, the user's photos, 2026-11-06).
    "Spa reception": (SPA_WALL, WOOD_FLOOR),
    "Massage and sauna": (SAUNA_WALL, WOOD_FLOOR),
    "Salon": (SPA_WALL, WOOD_FLOOR),
    "Aerobics": (VENUEWALL, WOOD_FLOOR),
    "Fitness": (VENUEWALL, GYM_FLOOR),
    "Garden Café buffet, Ice Cream Bar (Bumbot: fish)": (CAFE_WALL, CAFE_CARPET),
    "Sports Bar": (WINDJAMMER_WALL, WOOD_FLOOR),
}
# A span within a room with its own wall: the burl wood behind deck 5's Restaurant Reservations desk
# (the user's photo). (Bliss's wooden dance floor was tried: one carpet reads better, the user.)
RESERVATIONS = (5, 137.6, 143.0)
CUCINA_FRONT = (150, 153.5)     # the portico stands on the grey-blue wall (tried in its middle: the user preferred this)
FURNISHED = {4, 5, 6, 7, 8, 9, 10, 11}     # decks furnished from the photos: no placeholder venue signs on them

# The outer shell (§5.3): the off-white plating seen from outside, and its colour.
# Where a deck steps back from the one below by less than SLOPE_MAX metres, the
# shell slopes across the step, so the outline runs smoothly like the real ship's; bigger steps
# (the mooring deck, the aft diner terrace) keep their open shape. EXT tiles are cut away while
# she is on their deck; EXT_FIXED ones never are.
SLOPE_MAX = 8
PLATING = "#e8eaec"
EXT_CUT = (EXT, EXT_SLAB)

# A cabin corridor stops short of the outer plating (the user, 2026-11-03): this many columns of the
# ship's structure (steel frames) lie between, then the corridor's end wall.
STRUCTURE_COLS = 8

# Each deck is 8 rows of air over a 1-row floor slab: 144px, a ceiling at ~2.2x her height (§5.4).
DECK_ROWS = 9
DECK_PITCH = DECK_ROWS * TILE
TOP_FLOOR_ROW = 3 * DECK_ROWS - 1          # deck 12's floor; above it, the roof, funnel and mast
FLOOR_ROW = {d: TOP_FLOOR_ROW + (12 - d) * DECK_ROWS for d in DECKS}
ROOF_ROW = FLOOR_ROW[12] - DECK_ROWS       # the roof over deck 12's indoor rooms
# The sea surface: two decks of hull (crew decks 1 and 2) show above it below deck 3, as in the
# user's photo of the whole ship, where the hull below the promenade is nearly five decks tall.
HULL_DECKS_BELOW = 2
WATER_ROW = FLOOR_ROW[3] + HULL_DECKS_BELOW * DECK_ROWS - 1
ROWS = WATER_ROW + 11                      # the hull below the waterline, down past the keel

# The card each flight of stairs needs, by the deck it climbs to: her own crew card covers decks
# 4-6, the Hotel card everything above (§6.2).
FLIGHT_CARD = {d: ("crew" if d <= 6 else "hotel") for d in PLAYABLE}

# Deck 12's open stretch over deck 11's pool area, crossed by a side walk (§5.3), and deck 11's
# pools under it, metres from the bow. A pool is sunk two tiles into the deck.
POOL_OPENING = (115, 145)
POOLS = [(119, 131), (134, 140)]
POOL_DEPTH = 2 * TILE


WALL_FOR = {"venue": VENUEWALL, "cabins": CABIN_WALL, "crew": CREWWALL, "start": BACKWALL}


def col(m):
    """The column at `m` metres from the bow."""
    return SEA + round(m * PER_M)


def metres(c):
    """Metres from the bow at the middle of column `c`."""
    return (c - SEA + 0.5) / PER_M


def exact_x(m):
    """Pixel x at exactly `m` metres from the bow (not snapped to a column)."""
    return SEA * TILE + round(m * PER_M * TILE)


def x_of(m):
    """Pixel x at `m` metres from the bow (the middle of its column)."""
    return col(m) * TILE + TILE // 2


def floor_y(deck):
    """Pixel y of the walkable top of a deck's floor."""
    return FLOOR_ROW[deck] * TILE


def walk_y(deck):
    """Where she stands on `deck` in the atrium: its side walks are level with the deck's floor."""
    return floor_y(deck)


def funnel_ladder_col():
    """The technical ladder beside the funnel housing, deck 12 up to the roof (§5.1)."""
    return col(FUNNEL[0]) - 3


def clear_of_ladders(deck, m):
    """Is a door at `m` on `deck` clear of every ladder (doors and ladders must not overlap)?"""
    return deck != 12 or abs(m - metres(funnel_ladder_col())) > 1.5


def stem_x(row):
    """The stem's exact x in pixels at a (fractional) tile row: the smooth line the game draws."""
    return (SEA + stem_m(row) * PER_M) * TILE


def stem_m(row):
    """Where the raked stem is, in metres from the bow, at tile row `row` (§5.3): the curve measured
    off the user's photo (`BOW["rake"]`), in deck heights below deck 7's floor."""
    a, b = BOW["rake"]
    # From the underside of deck 7's floor, where the forecastle's deck edge meets the stem.
    d = min(max(0.0, (row - FLOOR_ROW[7] - 1) / DECK_ROWS), a / (2 * b))   # no further aft than its turn
    return BOW["stem"][7] + (a * d - b * d * d) * DECK_PITCH / (PER_M * TILE)


def corridor_ends(deck):
    """The deck's indoor ends at the outer plating: (plating column, inward). The playable space
    stops short of them, so the ship's ends always show its outer wall (the user, 2026-11-03)."""
    fwd, aft = EXTENT[deck]
    for c, inward in ((col(fwd), 1), (col(aft) - 1, -1)):
        if covered(deck, metres(c + inward)) and indoor(deck, metres(c + inward * (STRUCTURE_COLS + 2))):
            yield c, inward


def in_structure(deck, c):
    """Is column `c` on `deck` the structure or end wall at a corridor's end, not corridor?"""
    return any(0 < (c - pc) * inward <= STRUCTURE_COLS + 1 for pc, inward in corridor_ends(deck))


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
            name, kind = venue_at(deck, m)
            look = ROOM_LOOK.get(name)
            if deck == 3:
                tile = DIMWALL
            elif in_atrium(deck, m):
                tile = ATRIUMWALL
            elif in_core(m):
                tile = MAHOGANY  # the stair and elevator lobbies' panelling (the user's photos)
            elif not covered(deck, m) or kind in ("outdoor", "finale"):
                tile = 0
            elif look and name == "La Cucina" and CUCINA_FRONT[0] <= m < CUCINA_FRONT[1]:
                tile = CUCINA_WALL
            elif deck == RESERVATIONS[0] and RESERVATIONS[1] <= m < RESERVATIONS[2]:
                tile = BURL_WALL
            elif look:
                tile = look[0]
            else:
                tile = WALL_FOR.get(kind, BACKWALL)
            if tile:
                fill(back, c, c, floor - DECK_ROWS + 1, floor - 1, tile)
                if tile in (BACKWALL, VENUEWALL, CREWWALL, CABIN_WALL) and not look:
                    back[floor - 1][c] = WAINSCOT
            if deck == 12 and covered(12, m):
                solid[ROOF_ROW][c] = STEEL

            # The floor's surface, from the user's photos (§5.3): the cabin corridors' blue-grey
            # wave carpet, the open decks' tan non-skid paint.
            # Open to the sky wins: a corridor's carpet stops where the deck above it ends.
            if deck == 6 and in_core(m):
                solid[floor][c] = LOBBY6_CARPET  # deck 6's lobbies: purple-navy with gold (her photo)
            elif deck > 3 and (in_core(m) or kind == "start"):
                solid[floor][c] = LOBBY_CARPET  # the lobbies' and the gangway's blue mosaic carpet
            elif deck > 3:
                if not covered(deck, m) or kind in ("outdoor", "finale"):
                    solid[floor][c] = TEAK if deck == 11 else DECK_PAINT  # deck 11: teak (her photos)
                elif kind == "cabins":
                    solid[floor][c] = CABIN_CARPET
                elif look:
                    solid[floor][c] = look[1]
                elif deck == ATRIUM["decks"][0] and in_atrium(deck, m):
                    solid[floor][c] = ATRIUM_CARPET  # the atrium's floor: a blue-green patterned carpet

        # The deck's ends: the ship's outer shell indoors, riveted grey steel through the floor slab
        # too (the user's choice, 2026-11-03), a railing on an open terrace; decks 11 and 12 have
        # glass side walls instead (§5.3).
        for c, inward in ((c0, 1), (c1, -1)):
            if covered(deck, metres(c + inward)):
                fill(solid, c, c, floor - DECK_ROWS + 1, floor, STEEL)
            elif deck == 11 and inward == 1:
                # Deck 11's front: its bulwark, drawn by the game, ends the deck (the user: no glass
                # rail stub there); the rail stays, solid and unseen.
                fill(solid, c, c, floor - 2, floor - 1, BALCONY_RAIL)
            else:
                fill(solid, c, c, floor - 2, floor - 1, GLASS_RAIL if deck >= 11 else RAILING)

        # A cabin corridor ends short of the plating: the ship's structure, steel frames, fills the
        # gap, and the corridor's end wall turns away from us at its edge.
        for c, inward in corridor_ends(deck):
            for k in range(1, STRUCTURE_COLS + 1):
                tile = FRAMES_RIB if k % 2 == 0 else FRAMES  # a frame rib every second column
                fill(solid, c + inward * k, c + inward * k, floor - DECK_ROWS + 1, floor - 1, tile)
                solid[floor][c + inward * k] = SLAB  # the deck's slab, no carpet
            end = c + inward * (STRUCTURE_COLS + 1)
            fill(solid, end, end, floor - DECK_ROWS + 1, floor - 1, END_WALL_L if inward == 1 else END_WALL_R)

        # Where an open deck meets the indoors, an outer wall with a doorway 5 tiles (80px) high.
        if 3 < deck < 12:
            for c in range(c0 + 1, c1):
                if indoor(deck, metres(c - 1)) != indoor(deck, metres(c)):
                    wall = c if indoor(deck, metres(c)) else c - 1
                    fill(solid, wall, wall, floor - DECK_ROWS + 1, floor - 6, STEEL)

    # The bow's hull, seen from outside (§5.3): from the raked stem back to the block's end, from
    # under the forecastle down to the waterline, white plating (the game paints the ship's sun on
    # it). Below deck 3 the hull runs on aft, narrowing into the sea, navy under the waterline.
    fwd3, aft3 = EXTENT[3]
    # Tiles only where the stem has passed by the row's foot, so none sticks out past the smooth
    # line the game draws over the stem's edge.
    for r in range(FLOOR_ROW[7] + 1, ROWS):
        below = r - FLOOR_ROW[3]
        # The stern goes straight down to the waterline, as the real transom does, and only rounds
        # away under the water.
        end = col(BOW["block"]) - 1 if below <= 0 else col(aft3) - 1 - max(0, r - WATER_ROW)
        fill(solid, math.ceil(stem_x(r + 1) / TILE), end, r, r, HULL if r <= WATER_ROW + 2 else NAVY)

    # The atrium is open from its floor on deck 5 up through deck 10, and deck 12 over deck 11's pool
    # area (§5.3): their decks cross on side walks, built in the game, not floor tiles.
    lo, hi = ATRIUM["decks"]
    for deck in range(lo + 1, hi + 1):
        fill(solid, col(ATRIUM["span"][0]), col(ATRIUM["span"][1]) - 1, FLOOR_ROW[deck], FLOOR_ROW[deck], 0)
    a, b = POOL_OPENING
    fill(solid, col(a), col(b) - 1, FLOOR_ROW[12], FLOOR_ROW[12], 0)
    # The theatre's balcony, deck 7, ends in a railing over the stage; beyond it the stage's fly
    # space is open down to deck 6 (§5.3).
    fill(solid, col(STAGE), stage_end_col() - 1, FLOOR_ROW[7], FLOOR_ROW[7], 0)
    fill(back, col(STAGE), stage_end_col() - 1, FLOOR_ROW[7], FLOOR_ROW[7], THEATRE_WALL)
    fill(solid, col(STAGE) - 1, col(STAGE) - 1, FLOOR_ROW[7] - 2, FLOOR_ROW[7] - 1, BALCONY_RAIL)
    # Deck 7's stern: the open strip past deck 8's end, on the stern structure, stays (she can drop
    # onto it from deck 8's terrace), but it has no way in to the theatre's balcony: the wall there
    # is solid, no doorway (the user, 2026-11-06: maybe a secret place later, GAME_DESIGN.md §8).
    wall = next(c - 1 for c in range(col(STAGE), col(EXTENT[7][1]))
                if indoor(7, metres(c - 1)) and not indoor(7, metres(c)))
    fill(solid, wall, wall, FLOOR_ROW[7] - DECK_ROWS + 1, FLOOR_ROW[7] - 1, STEEL)
    STERN_STRIP_7[:] = [(wall + 1) * TILE, col(EXTENT[7][1]) * TILE]

    # Deck 11's pools, sunk into the deck: tiled sides and bottom, the water filled in by the game.
    for a, b in POOLS:
        top, bottom = FLOOR_ROW[11], FLOOR_ROW[11] + POOL_DEPTH // TILE
        fill(solid, col(a), col(b) - 1, top, bottom - 1, 0)
        fill(solid, col(a) - 1, col(a) - 1, top, bottom, POOL_TILE)
        fill(solid, col(b), col(b), top, bottom, POOL_TILE)
        fill(solid, col(a), col(b) - 1, bottom, bottom, POOL_TILE)

    # Funnel and mast, standing on the roof.
    # (Solid but drawn by the game's shell: the navy funnel and the white mast, §5.3.)
    fill(solid, col(FUNNEL[0]), col(FUNNEL[1]) - 1, ROOF_ROW - 12, ROOF_ROW - 1, HIDDEN)
    fill(solid, col(MAST[0]) + 6, col(MAST[1]) - 7, ROOF_ROW - 14, ROOF_ROW - 1, HIDDEN)

    # A technical ladder beside the funnel housing, deck 12 up to the roof (§5.1).
    lc = funnel_ladder_col()
    solid[ROOF_ROW][lc] = LADDER_TOP
    fill(ladders, lc, lc, ROOF_ROW, FLOOR_ROW[12] - 1, LADDER)

    return back, solid, ladders, build_exterior()


# The ship's white wall where a deck's indoors end at an open stretch of deck, as at every deck's
# end, END_WALL_M thick, a deck door through it implied: she passes behind it (the user,
# 2026-11-03, deck 7's front to the mooring deck; 2026-11-06, deck 8's small terraces at its ends,
# past the deck above; decks 9 and 10, the same). Deck 11's open ends are the pool deck's own.
# Behind the aft ones the deck's own small terrace is outdoors with no way in but the wall's: the
# ship's side stays closed while she is on it, as on deck 7's stern strip (the user, 2026-11-06).
END_WALL_M = 2.0
END_WALL_DECKS = (8, 9, 10)
END_WALL_FORE_ONLY = (11,)     # deck 11's open front meets the spa (its open stern is the Great Outdoors)
TERRACE_MIN_M = 1.0            # an open strip shorter than this is no terrace (the extents' rounding)


def end_walls():
    """(deck, first column, last column + 1) of each end wall, on the indoor side of the edge."""
    w = round(END_WALL_M * PER_M)
    a7 = col(EXTENT[8][0])
    walls = [(7, a7, a7 + w)]
    for deck in END_WALL_DECKS + END_WALL_FORE_ONLY:
        fwd, aft = EXTENT[deck]
        under = [c for c in range(col(fwd), col(aft)) if covered(deck, metres(c))]
        a, b = under[0], under[-1] + 1
        if metres(a) - fwd >= TERRACE_MIN_M:
            walls.append((deck, a, a + w))
        if aft - metres(b) >= TERRACE_MIN_M and deck not in END_WALL_FORE_ONLY:
            walls.append((deck, b - w, b))
    return walls


def in_end_wall(deck, c):
    return any(d == deck and a <= c < b for d, a, b in end_walls())


def on_stern_terrace(deck, c):
    """Past an aft end wall (decks 8-10), on deck 7's stern strip, or on deck 11's open front: out
    of sight behind the sloped plating at all times, its floor's edge too (the user, 2026-11-06)."""
    if deck == 7:
        return bool(STERN_STRIP_7) and c * TILE >= STERN_STRIP_7[0]
    if deck == 11:
        fa, fb = front_bulwark_11()
        return fa <= c * TILE < fb
    return any(d == deck and d != 7 and metres(b) > sum(EXTENT[d]) / 2 and c >= b for d, a, b in end_walls())


# Deck 7's stern strip, outside its solid wall (x from, x to): set as the solid layer is built; the
# game keeps the ship's side closed while she is on it, the deck's inside out of sight.
STERN_STRIP_7 = []


def stage_end_col():
    """Where the theatre's inside ends at the stern wall (the cut-away's last column + 1)."""
    return col(EXTENT[6][1]) - STRUCTURE_COLS - 2


def build_exterior():
    """The outer shell, a layer over everything (§5.3): every deck's indoor part and its floor's
    edge, in off-white plating. The game cuts away the deck she is on (EXT tiles); the ship's ends,
    deck 3 and the structure stay (EXT_FIXED), their edge at the cut a little shaded, their top
    outer corners rounded."""
    ext = [[0] * COLS for _ in range(ROWS)]
    for deck in DECKS:
        fwd, aft = EXTENT[deck]
        c0, c1 = col(fwd), col(aft) - 1
        floor = FLOOR_ROW[deck]
        for c in range(c0, c1 + 1):
            m = metres(c)
            shell = c in (c0, c1) and covered(deck, metres(c + (1 if c == c0 else -1)))
            fixed = deck == 3 or shell or in_structure(deck, c) or in_end_wall(deck, c)
            if indoor(deck, m) or fixed:
                for r in range(floor - DECK_ROWS + 1, floor):
                    ext[r][c] = EXT_FIXED if fixed else EXT
            ext[floor][c] = EXT_FIXED_SLAB if fixed or on_stern_terrace(deck, c) else EXT_SLAB
        # (The cut's edges are shaded by the game now, a soft shadow inside the opening.)
        # (No rounded corner tiles, nor a line along each deck's floor: the user, 2026-11-03; they
        # read as stray marks on the plating.)
    return ext


# --- The outer shell's details (§5.3, the user's photo of the whole ship) ---------------------------

GLASS_DARK = "#323353"
GLASS = "#484a77"
FRAME = "#9babb2"


PORTHOLE_PITCH = 160
PORTHOLE_R = 12      # the round windows: 24 px across (the user, 2026-11-03)
END_COVER = 32       # px of wall the game draws over her at each end of a cut-away deck


def shell_rooms():
    """Stretches of a deck's outer shell cut away on their own (the user, 2026-11-06): the bridge on
    deck 10, out of sight from the corridor, and cut open, the rest of the deck closed, while she is
    on it."""
    return [{"key": "10:bridge", "deck": 10, "x0": col(EXTENT[10][0]) * TILE, "x1": col(BRIDGE_WALL_M) * TILE},
            {"key": "11:spa", "deck": 11, "x0": front_bulwark_11()[1], "x1": col(SPA_WALL_M) * TILE}]


def front_bulwark_11():
    """Deck 11's open front, (x from, x to): up to the ship's wall before the spa."""
    a = next(wa for d, wa, wb in end_walls() if d == 11)
    return col(EXTENT[11][0]) * TILE, a * TILE


def shell_owner(deck, c):
    """Whose cut-away a shell tile of `deck` at column `c` follows: its deck's, or a room's."""
    return next((r["key"] for r in shell_rooms() if r["deck"] == deck and r["x0"] <= c * TILE < r["x1"]), deck)


def shell_details(ext, solid):
    """What is on the outside of the shell, as shapes for the game to draw over it: each listed
    under the deck whose wall it is on (it fades with that deck's cut-away) or under "fixed".
    Portholes along the lower hull, square windows on the cabin decks, balconies higher up, big
    windows on the public rooms, the bridge's window band, the open decks' bulwark and windscreen,
    and on top the roof's edge, the funnel, the mast and the radar domes."""
    out = {}

    def put(owner, shape):
        out.setdefault(str(owner), []).append(shape)

    def owner_at(c, r, deck):
        t = ext[r][c] if 0 <= r < ROWS and 0 <= c < COLS else 0
        if t in EXT_CUT:
            return shell_owner(deck, c)
        return "fixed" if t else None

    def rect(owner, x, y, w, h, colour):
        put(owner, ["r", round(x), round(y), round(w), round(h), colour])

    def span_owner(x0, x1, r, deck):
        """Whose wall a detail from x0 to x1 is on, or None if it would straddle the edge of the cut
        or sit within END_COVER of it, where the game draws the wall over her as she reaches it."""
        owners = {owner_at(c, r, deck) for c in range((x0 - END_COVER) // TILE, (x1 + END_COVER) // TILE + 1)}
        return owners.pop() if len(owners) == 1 else None

    def plain(x, y):
        """The forward hull, below deck 7, is plain plating with the livery: no windows."""
        return x < x_of(HULL_PLAIN_TO) and y > FLOOR_ROW[7] * TILE

    def window(deck, x, y, w, h):
        owner = span_owner(x - 1, x + w + 1, y // TILE, deck)
        if owner is None or plain(x, y):
            return
        rect(owner, x - 1, y - 1, w + 2, h + 2, FRAME)
        rect(owner, x, y, w, h, GLASS_DARK)
        rect(owner, x + 1, y + 1, max(1, w // 3), 1, "#8fd3ff")

    # The lower hull, crew decks 1-3: a row of round portholes along each deck, as big as deck 5's
    # and in line under them (the user, 2026-11-03: small ones made no sense).
    for k in range(HULL_DECKS_BELOW + 1):
        y = (FLOOR_ROW[3] - DECK_ROWS // 2 + k * DECK_ROWS) * TILE
        a = col(EXTENT[3][0]) * TILE + 40
        for x in range(a - a % PORTHOLE_PITCH + PORTHOLE_PITCH // 2, col(EXTENT[3][1]) * TILE - 40, PORTHOLE_PITCH):
            if x >= a and not plain(x, y) and (solid[y // TILE][x // TILE] or ext[y // TILE][x // TILE]):
                put("fixed", ["c", x, y, PORTHOLE_R, FRAME])
                put("fixed", ["c", x, y, PORTHOLE_R - 2, GLASS_DARK])
                rect("fixed", x - 5, y - 6, 3, 1, "#8fd3ff")
    # The dark navy band along the waterline.
    w0 = round(stem_x(WATER_ROW))
    rect("fixed", w0, WATER_ROW * TILE - 14, col(EXTENT[3][1]) * TILE - w0, 14, "#1d2b53")

    for deck in PLAYABLE:
        fwd, aft = EXTENT[deck]
        floor = FLOOR_ROW[deck] * TILE
        mid_row = FLOOR_ROW[deck] - 4
        x0, x1 = col(fwd) * TILE, col(aft) * TILE
        # Square windows, balconies and big windows, laid out on fixed spacings from the bow so the
        # rows line up deck over deck.
        # Deck 5's windows are round, fewer and bigger (the user, 2026-11-03).
        if deck == 5:
            for x in range(x0 - x0 % PORTHOLE_PITCH + PORTHOLE_PITCH // 2, x1 - 20, PORTHOLE_PITCH):
                own = span_owner(x - PORTHOLE_R, x + PORTHOLE_R, mid_row, deck)
                if own is None or x < x0 + 20 or plain(x, floor - 72):
                    continue
                put(own, ["c", x, floor - 72, PORTHOLE_R, FRAME])
                put(own, ["c", x, floor - 72, PORTHOLE_R - 2, GLASS_DARK])
                rect(own, x - 5, floor - 78, 3, 1, "#8fd3ff")
        prom_a, prom_b = PROMENADE["span"]
        open_a, open_b = PROMENADE["enclosed"][0][1], PROMENADE["enclosed"][-1][0]
        doors = [x_of(m) for m in PROMENADE["doors"]]
        for unit, style in ((96, "square"), (144, "balcony"), (64, "venue"), (48, "bridge"), (192, "promenade")):
            for x in range(x0 - x0 % unit, x1, unit):
                c = (x + unit // 2) // TILE
                if not (x0 <= x and x + unit <= x1):
                    continue
                own = owner_at(c, mid_row, deck)
                if own is None:
                    continue
                _, kind = venue_at(deck, metres(c))
                # From outside the hull's side has windows all along, whatever lies behind it: by
                # the stair cores and the atrium, the deck's usual ones.
                if in_core(metres(c)) or in_atrium(deck, metres(c)) or kind is None:
                    kind = "cabins" if deck in (4, 5, 8, 9, 10) else "venue"
                balcony = kind == "cabins" and deck >= 8 and metres(c) >= 82
                want = ("balcony" if balcony else "square") if kind == "cabins" else \
                       "bridge" if kind == "crew" and deck == 10 else "venue" if kind == "venue" else None
                # Along the promenade (the user, 2026-11-03): its wall has only a few windows, clear
                # of the doors, and deck 7 has none where the boats hang in front of it.
                if deck == PROMENADE["deck"] + 1 and open_a <= metres(c) < open_b:
                    continue
                if deck == PROMENADE["deck"] and prom_a <= metres(c) < prom_b:
                    mid = x + unit // 2
                    clear = all(abs(mid - d) > 70 for d in doors) and x_of(open_a) + 28 <= mid <= x_of(open_b) - 28
                    want = "promenade" if clear else None
                if want != style:
                    continue
                if deck == 5:
                    continue
                if style == "square":
                    # A cabin's pair of windows, both or neither.
                    if span_owner(x + 29, x + 68, (floor - 76) // TILE, deck) is not None:
                        window(deck, x + 30, floor - 76, 11, 9)
                        window(deck, x + 56, floor - 76, 11, 9)
                elif style in ("venue", "promenade"):
                    window(deck, x + unit // 2 - 20, floor - 94, 40, 30)
                elif span_owner(x, x + unit, mid_row, deck) is None:
                    continue
                elif style == "bridge":
                    rect(own, x, floor - 104, unit, 22, GLASS_DARK)
                    rect(own, x, floor - 103, unit, 1, "#4d65b4")
                else:
                    # A balcony: the cabin's dark glass door, a white partition, a glass railing.
                    rect(own, x, floor - 112, unit, 104, GLASS)
                    rect(own, x + 18, floor - 100, unit - 36, 60, GLASS_DARK)
                    rect(own, x, floor - 112, 6, 104, "#e8eaec")
                    rect(own, x + 6, floor - 40, unit - 6, 32, "#7f9aa8")
                    rect(own, x + 6, floor - 42, unit - 6, 2, "#e8eaec")
        # The open decks up top: a white bulwark with a glass windscreen above it, all along.
        if deck >= 11:
            fa, fb = front_bulwark_11()
            for x in range(x0, x1, TILE):
                m = metres(x // TILE)
                _, kind = venue_at(deck, m)
                if indoor(deck, m) or in_core(m) or (deck == 11 and fa <= x < fb):
                    continue
                rect(deck, x, floor - 24, TILE, 24, "#e8eaec")
                rect(deck, x, floor - 48, TILE, 24, "#bfe6f5")
                rect(deck, x, floor - 50, TILE, 2, "#cd683d")
            for x in range(x0, x1, 48):
                if not indoor(deck, metres(x // TILE)) and not in_core(metres(x // TILE)) and not (deck == 11 and fa <= x < fb):
                    rect(deck, x, floor - 50, 2, 26, "#e8eaec")

    # On top: the roof's white edge, the navy funnel with its dark grille, the white mast, the domes.
    roof = ROOF_ROW * TILE
    for c in range(COLS):
        if solid[ROOF_ROW][c] == STEEL:
            rect("fixed", c * TILE, roof, TILE, TILE, "#e8eaec")
    fa, fb = x_of(FUNNEL[0]) - 8, x_of(FUNNEL[1]) + 8
    put("fixed", ["p", [[fa, roof], [fb, roof], [fb - 30, roof - 12 * TILE], [fa + 50, roof - 12 * TILE]], GLASS_DARK])
    put("fixed", ["p", [[fa + 46, roof - 12 * TILE + 14], [fb - 32, roof - 12 * TILE + 14], [fb - 30, roof - 12 * TILE], [fa + 50, roof - 12 * TILE]], "#2e222f"])
    put("fixed", ["p", [[fa, roof], [fb, roof], [fb - 4, roof - 22], [fa + 6, roof - 22]], "#e8eaec"])
    ma, mb = x_of(MAST[0]), x_of(MAST[1])
    mc = (ma + mb) / 2
    put("fixed", ["p", [[mc - 22, roof], [mc + 22, roof], [mc + 5, roof - 14 * TILE], [mc - 5, roof - 14 * TILE]], "#e8eaec"])
    rect("fixed", mc - 34, roof - 10 * TILE, 68, 6, "#e8eaec")
    for m in (118, 124, 146):
        rect("fixed", x_of(m) - 4, roof - 26, 8, 26, "#c7dcd0")
        put("fixed", ["c", x_of(m), roof - 40, 18, "#e8eaec"])
        put("fixed", ["c", x_of(m) + 5, roof - 45, 6, "#ffffff"])
    return out


def shell_slopes():
    """Where the shell slopes across a deck's step back (§5.3): from the deck's own end at its floor
    to where the deck above ends, at the top of its band. The game draws these, fading with the
    deck."""
    slopes = []
    for deck in DECKS[:-1]:
        floor_end, top_end = EXTENT[deck], EXTENT[deck + 1]
        for end, i, sign in (("fwd", 0, 1), ("aft", 1, -1)):
            foot = FRONT_WALL.get(deck, floor_end[i]) if end == "fwd" else floor_end[i]
            step = (top_end[i] - foot) * sign
            if 0 < step <= SLOPE_MAX:
                slopes.append({"deck": deck, "end": end, "x0": col(foot) * TILE, "x1": col(top_end[i]) * TILE,
                               "yTop": (FLOOR_ROW[deck] - DECK_ROWS + 1) * TILE, "yFloor": FLOOR_ROW[deck] * TILE})
    return slopes


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
    for name, deck, m in [("gangway", 4, 67), ("pool", 11, 116), ("deck12", 12, 113), ("atrium", 7, 80), ("atrium-floor", 5, 84),
                          ("library", 6, 160), ("bar", 6, 112), ("theatre", 6, 215), ("bridge", 10, 37),
                          ("buffet", 11, 170), ("diner", 11, 220), ("spa", 11, 34), ("gym", 11, 92), ("bow", 7, 12), ("stern", 9, 247)]:
        add(point(name, "place", x_of(m), floor_y(deck)))
    add(point("promenade", "place", x_of(160), floor_y(6), [prop("route", "promenade")]))
    # Deck 7's stern strip is outdoors with no way in: the deck is not cut away while she is on it.
    # Nor are the aft terraces behind the end walls (decks 8-10): she is hidden behind the ship's side.
    x0, x1 = STERN_STRIP_7
    add(area("stern-strip-7", "outdoors", x0, floor_y(7), x1 - x0, 0, [prop("deck", 7, "int")]))
    # Deck 11's open front, the same (the user): the ship's side closed, the plating sloping up to deck
    # 12 over it, and its floor's edge, there whether she is out on it or not.
    fa, fb = front_bulwark_11()
    add(area("front-11", "outdoors", fa, floor_y(11), fb - fa, 0, [prop("deck", 11, "int"), prop("end", "fwd")]))
    for deck, wa, wb in end_walls():
        if deck != 7 and metres(wb) > (EXTENT[deck][0] + EXTENT[deck][1]) / 2:
            x1 = col(EXTENT[deck][1]) * TILE
            add(area(f"stern-terrace-{deck}", "outdoors", wb * TILE, floor_y(deck), x1 - wb * TILE, 0,
                     [prop("deck", deck, "int")]))
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
                      [prop("text", f"DECK {deck}"), prop("style", "plaque")]))

    # Side walks (§5.3), level with their deck's floor so she simply runs along them (the user,
    # 2026-11-02): each deck from 6 to 10 across the atrium, and deck 12 over deck 11's pool area,
    # which she can drop through into a pool. The atrium's dressing (pillars, skylight) is its own.
    lo, hi = ATRIUM["decks"]
    ax0, ax1 = col(ATRIUM["span"][0]) * TILE, col(ATRIUM["span"][1]) * TILE
    for d in range(lo + 1, hi + 1):
        add(area(f"sidewalk-atrium-{d}", "sidewalk", ax0, walk_y(d), ax1 - ax0, 0, [prop("style", "atrium")]))
    pa, pb = (col(m) * TILE for m in POOL_OPENING)
    add(area("sidewalk-pool", "sidewalk", pa, floor_y(12), pb - pa, 0, [
        prop("style", "deck"), prop("dropThrough", True, "bool")]))
    add(area("atrium", "atrium", ax0, floor_y(hi + 1) + TILE, ax1 - ax0, floor_y(lo) - floor_y(hi + 1) - TILE, [
        prop("levels", ",".join(str(walk_y(d)) for d in range(lo + 1, hi + 1)))]))
    for a, b in POOLS:
        add(area(f"pool-{a}", "pool", col(a) * TILE, floor_y(11) + 4, (col(b) - col(a)) * TILE, POOL_DEPTH - 4))
    walks = [{"deck": str(d), "y": walk_y(d)} for d in range(lo + 1, hi + 1)]
    levels = [("5", floor_y(lo))] + [(w["deck"], w["y"]) for w in walks if int(w["deck"]) <= ATRIUM["stairs"][1]]
    # The curving staircase winds round the glass elevator (the user's photos): each flight sweeps
    # from one side of it to the other, alternately behind it and in front of it, decks 5 to 9.
    lift_x = x_of(sum(ATRIUM["span"]) / 2)
    left, right = lift_x - 8 * TILE, lift_x + 8 * TILE
    for i, ((a, y0), (b, y1)) in enumerate(zip(levels, levels[1:])):
        x0, x1 = (left, right) if i % 2 == 0 else (right, left)
        card = FLIGHT_CARD[int(b)]
        add({"id": 0, "name": f"stairs-atrium-{a}-{b}", "type": "stairs", "x": x0, "y": y0,
             "width": 0, "height": 0, "rotation": 0, "visible": True,
             "polyline": [{"x": 0, "y": 0}, {"x": x1 - x0, "y": y1 - y0}],
             "properties": [prop("card", card), prop("curve", True, "bool"), prop("front", i % 2 == 1, "bool")]})

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
    lift("atrium", x_of(sum(ATRIUM["span"]) / 2), range(ATRIUM["lift"][0], ATRIUM["lift"][1] + 1), glass=True)

    # Venue signs; cabin doors along the corridors (background, muted), numbered from the bow. The
    # corridor's back wall is the starboard side's cabins (the game looks from port), numbered as on
    # the real ship: deck, then 2xx, one by one, so cabin 8206 lands where it is on deck 8.
    cabins_before = {}
    for deck, a, b, name, kind in VENUES:
        if kind == "cabins":
            # Only under a ceiling: where the deck above ends, the corridor is an open terrace.
            cols = [c for c in range(col(a), col(b))
                    if covered(deck, metres(c)) and not in_structure(deck, c) and not in_end_wall(deck, c)]
            runs = []
            for c in cols:
                if runs and runs[-1][1] == c:
                    runs[-1][1] = c + 1
                else:
                    runs.append([c, c + 1])
            for c0, c1 in runs:
                xs = list(range(c0 * TILE + 60, c1 * TILE - 30, 192))
                first = deck * 1000 + 202 + cabins_before.get(deck, 0)
                cabins_before[deck] = cabins_before.get(deck, 0) + len(xs)
                if deck == OUR_CABIN["deck"] and c0 * TILE < x_of(OUR_CABIN["m"]) < c1 * TILE:
                    i = min(range(len(xs)), key=lambda i: abs(xs[i] + 17 - x_of(OUR_CABIN["m"])))
                    assert first + i == OUR_CABIN["number"], (first + i, OUR_CABIN)
                    add(point(f"cabin-{OUR_CABIN['number']}", "cabin", xs[i] + 17, floor_y(deck),
                              [prop("number", OUR_CABIN["number"], "int")]))
                    # ?at=cabin: inside, where she comes in through its door.
                    add(point("cabin", "place", xs[i] + 17, floor_y(deck), [prop("route", "cabin")]))
                # The linen room's crew door, held open, in a cabin door's place (LINEN_ROOM).
                if deck == LINEN_ROOM["deck"] and c0 * TILE < x_of(LINEN_ROOM["m"]) < c1 * TILE:
                    i = min(range(len(xs)), key=lambda i: abs(xs[i] + 17 - x_of(LINEN_ROOM["m"])))
                    add(point("linen-room", "linen", xs[i] + 17, floor_y(deck)))
                    add(point("linen", "place", xs[i] + 17, floor_y(deck), [prop("route", "linen")]))
                add(area(f"cabins-{deck}-{c0}", "decor", c0 * TILE, floor_y(deck), (c1 - c0) * TILE, 0, [
                    prop("kind", "cabindoors"), prop("first", first, "int"), prop("last", first + len(xs) - 1, "int"),
                    prop("coreBefore", in_core(metres(c0 - 1)), "bool"), prop("coreAfter", in_core(metres(c1)), "bool")]))
        elif indoor(deck, (a + b) / 2) and kind != "start" and deck not in FURNISHED:  # a wall to hang on
            add(point(f"sign-{deck}-{a}", "sign", (x_of(a) + x_of(b)) / 2, floor_y(deck) - 100,
                      [prop("text", name.split(" (")[0].upper())]))

    # Checkpoints (crew cabin doors, §5.5): none for now (the user, 2026-11-03): they come back
    # when the ship is split into unlockable areas. Until then she always starts again at the
    # gangway. The last placements are in GAME_DESIGN.md §8.

    # Bumbot at his five spots (§4): what he is doing, and which way he runs. The fifth, asleep in
    # the linen room on deck 9, is placed by the game with the room.
    for name, deck, m, activity, escape in [("theatre", 6, 226, "wash", 1), ("buffet", 11, 178, "sit", 1),
                                            ("pool", 11, 146, "fly", 1), ("bridge", 10, 31.75, "bat", -1)]:
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
        # At the exact spot, not snapped to a tile's middle: pieces set round each other stay even.
        props = [prop("frame", frame), prop("dy", dy, "int")]
        if flip:
            props.append(prop("flip", True, "bool"))
        add(point(f"prop-{len(objs)}", "prop", x if x is not None else exact_x(m), floor_y(deck), props))

    def around(deck, m, middle, chair, on_top=None, gap=None, faces_left=False, sides=(True, True)):
        """A table (or anything) with a chair at each side, facing it, the same distance away (the
        user, 2026-11-03): by default each chair's seat tucked a little under the table's edge.
        `faces_left`: the chair was drawn facing left; `sides`: which of the two chairs to put."""
        cx = exact_x(m)
        off = gap if gap is not None else (width(middle) + width(chair)) // 2 - 5
        if sides[0]:
            put(deck, 0, chair, flip=faces_left, x=cx - off)
        if sides[1]:
            put(deck, 0, chair, flip=not faces_left, x=cx + off)
        put(deck, 0, middle, x=cx)
        if on_top:
            put(deck, 0, on_top, height(middle), x=cx)

    # The bow (§5.3): the sun painted on its hull, and the mooring deck's bollards and cleats.
    lx0, ly0, lx1, ly1 = livery_box()
    stem = [(round(stem_x(r / 4)), r * TILE // 4) for r in range(4 * (FLOOR_ROW[7] + 1), 4 * (WATER_ROW + 3) + 1)]
    add(area("livery", "livery", lx0, ly0, lx1 - lx0, ly1 - ly0, [
        prop("stem", ",".join(f"{x}:{y}" for x, y in stem))]))
    add(promenade())
    # Inside, each promenade door on the rooms' wall, where E uses it (no sign: the door says it,
    # the user, 2026-11-03).
    for m in PROMENADE["doors"]:
        put(PROMENADE["deck"], m, "door-deck", x=x_of(m))
    # The mooring deck: bollards and a cleat, the side railing in front of them (the user), from the
    # tip all the way back to deck 7's front wall (its last piece runs on under the wall).
    put(7, 6, "bollard-bg")
    put(7, 10.5, "cleat-bg")
    put(7, 15, "bollard-bg")
    rail_w = width("railing-bg")
    for x in range(col(BOW["stem"][7]) * TILE + 30, end_walls()[0][1] * TILE + rail_w // 2, rail_w):
        put(7, 0, "railing-bg", x=x)
    # The bow view (§5.3): standing still on the mooring deck, she goes to the tip and spreads her
    # arms, and the camera draws back to frame the whole bow, from above the forecastle down to
    # the sea. `x0`-`x1` is where on deck 7 it can start.
    add(area("bow-view", "bowview", x_of(-1), floor_y(7) - 90, x_of(23) - x_of(-1), (WATER_ROW + 2) * TILE - floor_y(7) + 90, [
        prop("x0", x_of(BOW["stem"][7]), "int"), prop("x1", x_of(EXTENT[8][0]), "int"),
        prop("tipX", (col(BOW["stem"][7]) + 1) * TILE + 9, "int"), prop("deckY", floor_y(7), "int")]))
    # The bridge's windows on deck 10, looking out to sea.
    # Big panes in two runs, the sky and the sea in them, a stretch of wall between them and after
    # them for the clock and the screens (the user, 2026-11-06).
    for a, b in ((28.7, 33.0), (34.4, 37.6)):
        add(area(f"bridge-windows-{a}", "decor", exact_x(a), floor_y(10) - 104, exact_x(b) - exact_x(a), 56,
                 [prop("kind", "bridgewindows")]))

    # The gangway lobby, deck 4 (the user's photo): cream panelling, a fire door held open at each
    # end (folded flat against the wall), an exit sign over the shell door, fire equipment. (The
    # photo's runner mat is left out: from the side a floor mat is only a sliver.)
    add(area("gangway-lobby", "decor", x_of(60), floor_y(4), x_of(74) - x_of(60), 0, [prop("kind", "gangway")]))
    put(4, 62.85, "exit-sign-bg", 92)
    put(4, 65.3, "picture-ship-bg", 44)
    put(4, 66.6, "hose-cabinet-bg", 18)
    put(4, 68.7, "plant-bg")
    put(4, 70.1, "extinguisher-bg", 14)
    # A framed picture in each stair and elevator lobby, left of its stairs; on decks 8-10 the deck's
    # directory board hangs there instead (the user's photo of deck 8; decks 9 and 10 are like it).
    for core, (a, _) in CORES.items():
        for deck in PLAYABLE:
            if deck not in (8, 9, 10):
                put(deck, 0, ("picture-art-bg", "picture-sea-bg")[deck % 2], 46, x=col(a) * TILE + 30)

    # Deck 5, furnished from the user's photos (§5.3): the atrium café and Guest Services, the shore
    # excursions and reservations desks, La Cucina, the Four Seasons and the Seven Seas.
    def decor(name, kind, x0, x1, deck=5, **props):
        add(area(name, "decor", x0, floor_y(deck), x1 - x0, 0,
                 [prop("kind", kind)] + [prop(k, v) for k, v in props.items()]))

    def dinner(m, table, chair, lamp=None):
        around(5, m, table, chair, lamp)

    # The atrium's floor: the café on the forward side, Guest Services aft (the user's photos).
    for m in (83.6, 85.6):
        around(5, m, "cafe-table-bg", "cafe-chair-bg")
    put(5, 86.4, "pastry-case-bg")
    put(5, 98.3, "palm-bg")
    put(5, 99.2, "counter-bg")
    put(5, 99.85, "desk-screen-bg")
    add(point("sign-guest-services", "sign", x_of(99.5), floor_y(5) - 62,
              [prop("text", "Guest Services"), prop("style", "plaque")]))
    # Shore excursions and reservations: desks, brochures, travel posters (not in the photos).
    put(5, 112.6, "brochure-stand-bg")
    put(5, 114.0, "desk-screen-bg")
    put(5, 114.0, "poster-beach-bg", 46, x=x_of(114.0) - 30)
    put(5, 116.4, "poster-fjord-bg", 46)
    put(5, 118.4, "poster-city-bg", 46)
    put(5, 121.0, "orchid-bg")
    put(5, 130.5, "world-map-bg", 48)
    put(5, 132.6, "desk-screen-bg")
    put(5, 134.0, "brochure-stand-bg")
    # Restaurant Reservations (NCL's plan puts it here; the user's photo): burl-wood walls, a curved
    # grey counter with a black top, brass lettering over it.
    decor("reservations-desk", "resdesk", exact_x(140.3), exact_x(140.3), text="Restaurant Reservations")
    put(5, 143.6, "easel-sign-bg")
    put(5, 146.5, "palm-bg")
    # La Cucina: the marble portico on its grey-blue wall, then dark wood, dark tables with lamps,
    # windows with beige drapes (the user's photos).
    decor("cucina-portico", "portico", x_of(151.8), x_of(151.8), text="La Cucina")
    put(5, 150.5, "menu-lectern-bg")
    cucina = [155.5, 159.8, 164.1]
    decor("cucina-windows", "dinewindows", x_of(150), x_of(168), xs=",".join(str(x_of(m)) for m in cucina), style="drapes")
    for m in cucina:
        dinner(m, "dark-table-lamp-bg", "dark-chair-bg")
    put(5, 157.65, "wine-barrel-bg")
    put(5, 161.95, "olive-tree-bg")
    put(5, 166.4, "wine-trolley-bg")
    # The Four Seasons: cream, burl-wood pillars, white-cloth tables, beige chairs, sheer curtains,
    # chandeliers.
    seasons = [171.0, 175.4, 179.8, 184.2, 188.6]
    decor("seasons-windows", "dinewindows", x_of(168), x_of(194), xs=",".join(str(x_of(m)) for m in seasons), style="sheers")
    decor("seasons-pillars", "pillars", x_of(168), x_of(194), xs=",".join(str(x_of(m)) for m in (173.2, 182.0, 190.8)), style="burl")
    for i, m in enumerate(seasons):
        dinner(m, ("table-dinner-bg", "table-flowers-bg")[i % 2], "dining-chair-bg")
        put(5, m, "chandelier-bg", DECK_PITCH - TILE - height("chandelier-bg"))
    put(5, 168.9, "sideboard-bg")
    put(5, 177.6, "ice-swan-bg")
    put(5, 186.4, "dessert-trolley-bg")
    put(5, 192.6, "service-station-bg")
    # The Seven Seas: its backlit wave panel between white columns (the user's photo from the inner
    # balcony), white-cloth tables either side under sheer curtains.
    # Its entrance, straight off the aft lobby (the user, 2026-11-03: make it clear): a welcome
    # station, the host's counter and the menu lectern, a brass plaque with the name over them.
    put(5, 203.3, "counter-bg")
    put(5, 204.3, "menu-lectern-bg")
    add(point("sign-seven-seas", "sign", exact_x(203.6), floor_y(5) - 62,
              [prop("text", "Seven Seas"), prop("style", "plaque")]))
    seas = [208.6, 213.0, 217.4, 221.8, 238.2, 242.6, 247.0]
    decor("seas-windows", "dinewindows", x_of(205), x_of(252), xs=",".join(str(x_of(m)) for m in seas), style="sheers")
    decor("seas-panel", "wavepanel", x_of(230) - 80, x_of(230) + 80)
    decor("seas-columns", "pillars", x_of(205), x_of(252), xs=",".join(str(x_of(m)) for m in (227.6, 232.4)), style="white")
    for i, m in enumerate(seas):
        dinner(m, ("table-flowers-bg", "table-dinner-bg")[i % 2], "dining-chair-bg")
    put(5, 225.2, "palm-bg")
    put(5, 234.8, "palm-bg")
    put(5, 248.8, "service-station-bg")
    # Warm downlights along the public rooms' ceilings.
    for a, b in ((110, 150), (150, 194), (202, 252)):
        decor(f"downlights-5-{a}", "downlights", x_of(a), x_of(b))

    # Deck 6, after NCL's plan and the user's photos (§5.3). Clear of its trunk doors (118, 125, 240),
    # and the promenade doors (111, 138, 162, 186).
    # The Internet Café, at the end of the cabin corridor by the forward lobby.
    decor("cafe-doorway", "doorway", x_of(64) - 8, x_of(64) - 8, deck=6, text="Internet Café")
    for m in (65.6, 67.6, 69.6):
        put(6, m, "office-chair-bg")
        put(6, m + 0.55, "computer-desk-bg")
    put(6, 71.6, "printer-bg")
    put(6, 72.8, "fern-bg")
    # The Bliss Ultra Lounge: near-black walls, a dotted carpet, a wooden dance floor under a disco
    # ball, the DJ booth, purple velvet seats round cocktail tables, a bar with a neon sign.
    put(6, 112.4, "velvet-sofa-bg")
    around(6, 114.6, "cocktail-table-bg", "velvet-stool-bg")
    put(6, 116.2, "speaker-stand-bg")
    put(6, 119.4, "disco-ball-bg", DECK_PITCH - TILE - height("disco-ball-bg"))
    put(6, 121.3, "dj-booth-bg")
    put(6, 122.9, "neon-bar-bg", 62)
    put(6, 122.9, "bar-counter-bg")
    for m in (122.4, 123.4):
        put(6, m, "velvet-stool-bg")
    # The Gift Shops and the Perspectives Photo Studio.
    put(6, 126.6, "shop-shelves-bg")
    put(6, 127.8, "mannequin-bg")
    put(6, 129.0, "jewellery-counter-bg")
    put(6, 130.0, "till-bg")
    put(6, 131.2, "dress-rack-bg")
    put(6, 133.6, "photo-backdrop-bg")
    put(6, 132.2, "softbox-bg")
    put(6, 135.0, "softbox-bg", flip=True)
    put(6, 134.3, "camera-tripod-bg", flip=True)
    # The Windjammer Bar (the user's photos): dark green walls, a coffered mahogany ceiling with
    # brass lamps, a plank floor; the ship's wheel and the captain on the walls; teal club chairs
    # round a bar table; the back bar and its counter with tan stools; the chesterfield sofa under
    # a green lamp; the lit cabinet with a model ship, by the gallery as in her photo.
    decor("windjammer-ceiling", "coffers", exact_x(136), exact_x(150), deck=6)
    add(point("sign-windjammer", "sign", exact_x(137.4), floor_y(6) - 100,
              [prop("text", "Windjammer Bar"), prop("style", "plaque")]))
    put(6, 136.8, "ships-wheel-bg", 50)
    around(6, 139.6, "bar-table-bg", "club-chair-side-bg")
    put(6, 139.6, "green-lamp-bg", height("bar-table-bg"))
    put(6, 142.6, "back-bar-bg")
    put(6, 142.6, "bar-counter-bg")
    for m in (141.6, 142.6, 143.6):
        put(6, m, "tan-bar-stool-bg")
    put(6, 146.0, "chesterfield-sofa-bg")
    put(6, 146.0, "captain-portrait-bg", 50)
    put(6, 147.6, "bar-table-bg")
    put(6, 147.6, "green-lamp-bg", height("bar-table-bg"))
    put(6, 149.1, "ship-cabinet-bg")
    for m in (139.6, 146.0):
        put(6, m, "brass-ceiling-lamp-bg", DECK_PITCH - TILE - height("brass-ceiling-lamp-bg"))
    # The Photo Gallery: white walls, its name in big grey letters, the ship's photographers'
    # pictures in two rows.
    decor("gallery-name", "lettering", exact_x(155), exact_x(155), deck=6, text="PHOTO GALLERY")
    for i, m in enumerate((151.2, 152.6, 154.0, 156.0, 157.4, 158.8)):
        put(6, m, ("photo-couple-bg", "photo-sunset-bg", "photo-family-bg")[i % 3], 44)
        put(6, m, ("photo-family-bg", "photo-couple-bg", "photo-sunset-bg")[i % 3], 72)
    put(6, 155.0, "leaflet-stand-bg")
    # The Library (the user's photos): lit dark-wood bookcases with glass doors, the red-and-white
    # striped carpet, red reading chairs round lamp tables, a chess table, a writing desk.
    for m in (164.2, 165.5, 170.6, 171.9, 177.2, 178.5, 183.4, 189.4, 190.7):
        put(6, m, "bookcase-bg")
    for m in (168.0, 174.9, 181.0):
        around(6, m, "reading-table-bg", "reading-chair-bg")
    around(6, 187.9, "chess-table-bg", "chair-bg")
    put(6, 191.9, "desk-bg")
    put(6, 191.9, "bankers-lamp-bg", height("desk-bg"))
    put(6, 192.55, "chair-bg", flip=True)
    put(6, 184.6, "globe-bg")
    # The Stardust Lounge: deep navy, a red carpet, rows of red velvet seats facing the stage aft,
    # the stage with its red curtains, spotlights and the band's instruments.
    decor("stardust-entrance", "marquee", exact_x(203.4), exact_x(203.4), deck=6, text="STARDUST LOUNGE")
    decor("stardust-stage", "stage", col(STAGE) * TILE, stage_end_col() * TILE, deck=6)
    for k in range(int((238.4 - 206.6) / 0.95) + 1):
        m = 206.6 + k * 0.95
        put(6, m, "theatre-seat-bg")
    put(6, 245.2, "drum-kit-bg")
    put(6, 246.7, "mic-stand-bg")
    put(6, 247.6, "guitar-bg")
    put(6, 249.0, "grand-piano-bg", flip=True)
    put(6, 243.2, "speaker-stack-bg")

    # Deck 7, after NCL's plan and the user's photos (§5.3). Clear of the Hotel trunk's door (118).
    def plaque(name, m, text):
        add(point(name, "sign", exact_x(m), floor_y(7) - 100, [prop("text", text), prop("style", "plaque")]))

    # Deck 11's open front: its white bulwark and glass windscreen in front of her (the user): she
    # is hidden behind the white, seen through the glass.
    fa, fb = front_bulwark_11()
    add(area("bulwark-11", "bulwark", fa, floor_y(11), fb - fa, 0))
    # The end walls she passes behind: deck 7's front, to the mooring deck; deck 8's two ends.
    for deck, wa, wb in end_walls():
        add(area(f"end-wall-{deck}-{wa}", "endwall", wa * TILE, floor_y(deck), (wb - wa) * TILE, 0))
    # Splash Academy: sunny walls, a blue carpet with coloured dots, toys, a play kitchen, low tables.
    plaque("sign-splash", 24.6, "Splash Academy")
    put(7, 24.0, "kids-bookshelf-bg")
    put(7, 26.4, "play-kitchen-bg")
    for m in (29.0, 41.2):
        around(7, m, "kids-table-bg", "kids-chair-bg")
        put(7, m, "kids-drawing-bg", 52)
    put(7, 31.4, "rocking-horse-bg")
    put(7, 33.0, "toy-box-bg")
    put(7, 34.0, "toy-blocks-bg")
    put(7, 36.0, "beanbags-bg")
    put(7, 36.0, "pin-map-bg", 54)
    put(7, 38.0, "teddy-bg")
    put(7, 39.2, "toy-train-bg")
    put(7, 43.6, "cactus-bg")
    # Entourage, the teen club: deep teal, a dark carpet with neon specks, games.
    decor("entourage-doorway", "doorway", exact_x(45), exact_x(45), deck=7, text="Entourage")
    put(7, 48.4, "tv-console-bg")
    put(7, 51.0, "beanbags-bg")
    put(7, 54.6, "foosball-bg")
    put(7, 58.2, "air-hockey-bg")
    put(7, 61.4, "dartboard-2-bg", 54)
    put(7, 63.2, "arcade-cabinet-bg")
    put(7, 65.0, "vending-machine-bg")
    put(7, 67.8, "wall-tv-bg", 62)
    put(7, 67.2, "beanbag-orange-bg")
    put(7, 68.4, "beanbag-blue-bg")
    put(7, 71.6, "monstera-bg")
    # The atrium on deck 7 (the user's photos): burl-wood panels behind the side walk, covered in
    # the ports' plaques, a ship's wheel and paintings among them.
    plaques = ["plaque-shield", "plaque-medallion", "certificate", "plaque-lighthouse", "plaque-crown",
               "plaque-red", "welcome-card", "painting-harbour", "ships-wheel"]
    k = 0
    for a, b in ((82.9, 86.5), (97.3, 101.0)):
        decor(f"plaque-wall-{a}", "burlpanel", exact_x(a), exact_x(b), deck=7)
        for m in [a + 0.45 + i * 0.68 for i in range(int((b - a - 0.4) / 0.68))]:
            for dy in (44, 80):
                put(7, m, plaques[k % len(plaques)] + "-bg", dy)
                k += 1
    # Magnum's Champagne & Whiskey Bar: dark wood, the back bar and chrome stools, leather club
    # chairs round marble tables, art-deco lamps.
    plaque("sign-magnums", 111.4, "Magnum's")
    put(7, 113.6, "back-bar-bg")
    put(7, 113.6, "bar-counter-bg")
    for m in (112.6, 113.6, 114.6):
        put(7, m, "chrome-stool-bg")
    for m, painting in ((121.2, "painting-sea-bg"), (125.6, "painting-flowers-bg")):
        around(7, m, "marble-table-bg", "leather-club-chair-bg", "deco-lamp-bg")
        put(7, m, painting, 52)
        put(7, m, "brass-ceiling-lamp-bg", DECK_PITCH - TILE - height("brass-ceiling-lamp-bg"))
    put(7, 128.6, "decanter-bg")
    # The Art Gallery: white, paintings on the walls and on easels, benches, a dancer in marble,
    # spotlights on a track.
    decor("gallery-doorway", "doorway", exact_x(130), exact_x(130), deck=7, text="Art Gallery")
    for m in (132.4, 140.0, 147.4):
        put(7, m, "easel-painting-bg")
    for i, m in enumerate((134.2, 135.9, 137.6, 142.0, 143.7, 145.4)):
        put(7, m, ("painting-abstract-bg", "painting-blue-bg", "painting-harbour-bg", "painting-sea-bg",
                   "painting-flowers-bg", "painting-ship-bg")[i], 50)
    for m in (135.9, 143.7):
        put(7, m, "gallery-bench-bg")
    put(7, 138.8, "dancer-statue-bg")
    put(7, 149.2, "bronze-sculpture-bg")
    for m in (134.2, 137.6, 142.0, 145.4):
        put(7, m, "track-spot-bg", DECK_PITCH - TILE - height("track-spot-bg"))
    # The Sun Club Casino: deep red and gold, rows of slot machines, the roulette and blackjack
    # tables with stools, a jackpot sign, the ATM.
    decor("casino-doorway", "doorway", exact_x(150), exact_x(150), deck=7, text="Sun Club Casino")
    for m in (151.9, 153.1, 154.3, 165.6, 166.8, 168.0):
        put(7, m, "slot-pair-bg")
    put(7, 153.1, "jackpot-sign-bg", 72)
    around(7, 158.0, "roulette-bg", "casino-stool-bg")
    around(7, 162.4, "blackjack-bg", "casino-stool-bg")
    put(7, 170.6, "atm-bg")
    # Tradewinds duty-free: shelves of liquor and perfume, watches, chocolates, sunglasses, the till.
    decor("tradewinds-doorway", "doorway", exact_x(172), exact_x(172), deck=7, text="Tradewinds")
    put(7, 173.6, "shop-shelves-bg")
    put(7, 175.4, "liquor-shelf-bg")
    put(7, 176.6, "perfume-display-bg")
    put(7, 178.2, "jewellery-counter-bg")
    put(7, 179.6, "till-bg")
    put(7, 181.0, "sunglasses-stand-bg")
    put(7, 182.2, "shop-basket-bg")
    put(7, 183.6, "handbag-shelf-bg")
    put(7, 185.0, "chocolates-bg")
    # The Arcade: night blue, cabinets, a claw machine, pinball.
    decor("arcade-doorway", "doorway", exact_x(186), exact_x(186), deck=7, text="Arcade")
    put(7, 187.4, "arcade-cabinet-bg")
    put(7, 188.3, "arcade-cabinet-bg")
    put(7, 189.8, "claw-machine-bg")
    put(7, 191.4, "pinball-bg")
    put(7, 192.9, "arcade-cabinet-bg")
    # The Stardust Lounge's balcony: rows of red seats down to the railing over the stage.
    decor("balcony-doorway", "doorway", exact_x(202), exact_x(202), deck=7, text="Stardust Lounge Balcony")
    for k in range(int((STAGE - 1.6 - 204.2) / 0.95) + 1):
        put(7, 204.2 + k * 0.95, "theatre-seat-bg")
    # Its front over the stage, seen end-on: a velvet-padded parapet with a brass rail, as tall as
    # the solid railing she hops (the tile itself is invisible).
    put(7, 0, "balcony-front", x=(col(STAGE) - 1) * TILE + TILE // 2)
    for a, b in ((110, 150), (150, 194)):
        decor(f"downlights-7-{a}", "downlights", x_of(a), x_of(b), deck=7)

    # Decks 8-10, cabins fore and aft and the atrium between (NCL's plan; the user's photos of deck 8,
    # 2026-11-06; decks 9 and 10 are like it, the user remembers).
    # The lobbies: the deck's directory board, blue in a brass frame, and an exit sign over the stairs.
    for deck in (8, 9, 10):
        for core, (a, _) in CORES.items():
            x = col(a) * TILE + 30
            add(area(f"directory-{deck}-{core}", "decor", x - 13, floor_y(deck), 26, 0, [prop("kind", "directory")]))
            put(deck, 0, "exit-sign-bg", 112, x=col(a) * TILE + 5 * TILE)
        # The atrium's walk: downlights and a warm cove along its ceiling (deck 10's is the dome:
        # the cove only), and paintings on its cream walls, clear of the pillars, the staircase and
        # the glass elevator.
        if deck != 10:
            decor(f"downlights-{deck}-atrium", "downlights", x_of(ATRIUM["span"][0]), x_of(ATRIUM["span"][1]), deck=deck)
        decor(f"cove-{deck}-atrium", "cove", x_of(ATRIUM["span"][0]), x_of(ATRIUM["span"][1]), deck=deck)
    for m, painting in ((83.6, "painting-harbour-bg"), (99.0, "painting-sea-bg"), (100.6, "painting-blue-bg")):
        put(8, m, painting, 50)
    for m, painting in ((83.6, "painting-ship-bg"), (99.0, "painting-flowers-bg"), (100.6, "painting-abstract-bg")):
        put(9, m, painting, 50)
    for m, painting in ((83.6, "painting-sea-bg"), (100.6, "painting-harbour-bg")):
        put(10, m, painting, 50)
    # Cabin 8206, the user's own (OUR_CABIN): its open door is placed with the corridor's doors.

    # Deck 10's bridge (§5.3; a PixelLab sheet, bridge-1, 2026-11-06): the consoles, the helm and the
    # engine telegraph forward (Bumbot bats at the telegraph's levers), the captain's and an
    # officer's chair, the compass binnacle, the radar and the chart display, the chart table and
    # the alarm panel; screens and the clock with its barometer on the wall under the side windows.
    # (Its inside starts about 28.5 m: the deck's front 3 m are the ship's structure.)
    for m, frame in ((29.3, "bridge-console"), (30.55, "helm-console"), (32.1, "engine-telegraph"),
                     (33.4, "captain-chair"), (34.5, "binnacle"), (35.5, "radar-pedestal"),
                     (36.5, "ecdis-stand"), (37.8, "chart-table"), (38.9, "alarm-panel")):
        put(10, m, frame + "-bg")
    put(10, 33.7, "clock-barometer-bg", 62)
    put(10, 38.6, "bridge-monitors-bg", 74)
    # Its back wall, across the deck, with the crew door: the game draws it and opens it with E.
    add(point("spa-door", "bulkhead", exact_x(SPA_WALL_M), floor_y(11), [
        prop("x0", col(EXTENT[11][0]) * TILE, "int"), prop("key", "11:spa"), prop("text", "SPA & SALON"),
        prop("leaf", "door-deck"), prop("colour", "#0b5e65")]))
    add(point("bridge-door", "bulkhead", exact_x(BRIDGE_WALL_M), floor_y(10), [
        prop("x0", col(EXTENT[10][0]) * TILE, "int"), prop("key", "10:bridge"), prop("text", "BRIDGE"),
        prop("sub", "CREW ONLY")]))

    # Deck 11, after NCL's plan and the user's photos (2026-11-06; three PixelLab sheets, tall-3,
    # tall-4 and props-6, 30 generations). Bow to stern.
    def at11(m, frame, dy=0, flip=False):
        put(11, m, frame + "-bg", dy, flip)

    # The spa: its reception, the massage and sauna rooms, the salon, the aerobics studio, opening one
    # into the next at wood posts with brass plaques; she comes in from the forward lobby.
    # (Each plaque names the room aft of its post, as on deck 7; the reception's is on its wall.)
    for m, text in ((40, "Massage & Sauna"), (55, "Salon"), (65, "Aerobics")):
        decor(f"spa-doorway-{m}", "doorway", exact_x(m), exact_x(m), deck=11, text=text)
    add(point("sign-spa", "sign", exact_x(35.2), floor_y(11) - 100, [prop("text", "Spa & Salon"), prop("style", "plaque")]))
    at11(33.8, "bamboo")
    at11(35.6, "spa-desk")
    at11(37.4, "towel-shelf")
    at11(37.4, "spa-towels", height("towel-shelf-bg"))
    at11(37.4, "painting-flowers", 56)
    at11(38.9, "cucumber-water")
    at11(42.2, "massage-table")
    at11(43.8, "side-table")
    at11(43.8, "spa-candle", height("side-table-bg"))
    at11(45.4, "massage-table")
    at11(47.2, "bathrobe", 34)
    at11(47.2, "spa-slippers")
    at11(53.6, "bathrobe", 34)          # and one by the sauna's far door (the user)
    at11(53.6, "spa-slippers")
    decor("sauna-11", "sauna", exact_x(47.9), exact_x(52.9), deck=11)
    at11(49.6, "sauna-bench")
    at11(50.7, "sauna-bench")
    at11(51.7, "sauna-stove")
    # Its ends: cedar walls across the deck, a glass door in each opening into it with E.
    for m, swing in ((47.9, 1), (52.9, -1)):
        add(point(f"sauna-door-{m}", "bulkhead", exact_x(m) + swing * 3, floor_y(11), [
            prop("leaf", "glass"), prop("width", 6, "int"), prop("swing", swing, "int"), prop("wall", "#6e3a22")]))
    for m in (57.0, 59.8):
        at11(m, "salon-mirror", 44)
        at11(m, "salon-chair")
    at11(62.3, "hood-dryer")
    at11(63.8, "manicure-table")
    at11(66.6, "yoga-rack")
    at11(68.0, "kettlebell")
    at11(68.8, "medicine-ball")
    at11(69.6, "gym-bottle")
    at11(70.6, "yoga-mat")
    at11(71.6, "dumbbells")
    at11(73.0, "water-dispenser")
    # The fitness centre over the atrium's dome: machines in a row before big windows.
    add(area("fitness-windows", "decor", exact_x(83.2), floor_y(11) - 104, exact_x(100.8) - exact_x(83.2), 56,
             [prop("kind", "bridgewindows")]))
    for m, frame in ((84.4, "treadmill"), (86.6, "treadmill"), (88.8, "treadmill"), (90.8, "exercise-bike"),
                     (92.6, "exercise-bike"), (94.6, "cross-trainer"), (96.8, "rowing-machine"),
                     (99.0, "weight-bench"), (101.0, "dumbbell-rack")):
        at11(m, frame)
    # The pool deck (the user's photos): the giant chess set, sun loungers and parasols, the hot tub
    # between the two pools, ladders into them, the towel cart and a shower, Topsiders' bar.
    decor("chess-11", "chess", exact_x(110.4), exact_x(114.4), deck=11)
    for m in (115.9, 117.6, 141.4, 144.6, 147.8):
        at11(m, "sunlounger")
    at11(143.0, "parasol")
    at11(132.5, "hot-tub")
    decor("hot-tub-canopy", "canopy", exact_x(131.1), exact_x(133.9), deck=11)
    for m, flip in ((119.5, False), (139.5, True)):
        at11(m, "pool-ladder", -12, flip=flip)   # feet in the water, within deck 11's slab (not into deck 10)
    at11(150.0, "towel-cart")
    at11(151.8, "pool-shower")
    decor("shower-box", "showerbox", exact_x(151.1), exact_x(152.5), deck=11)
    at11(153.4, "planter-palm")
    at11(155.8, "pool-bar")
    at11(157.6, "chalkboard")
    at11(158.8, "planter-palm")
    # The Garden Café (the user's photos): the buffet counters, light wood tables with light blue
    # chairs, a painting between the windows, the Ice Cream Bar, window seats at round white tables
    # in wicker chairs. Bumbot sits by a table with a fish on it (§4).
    decor("cafe-doorway", "doorway", exact_x(160), exact_x(160), deck=11, text="Garden Café")
    for a, b in ((160.8, 170.2), (172.8, 181.8), (184.2, 193.4)):
        add(area(f"cafe-windows-{a}", "decor", exact_x(a), floor_y(11) - 104, exact_x(b) - exact_x(a), 56,
                 [prop("kind", "bridgewindows")]))
    at11(171.5, "painting-abstract", 66)
    at11(162.0, "buffet-hot")
    at11(164.1, "buffet-salad")
    at11(166.2, "juice-station")
    for m in (170.0, 174.2):
        around(11, m, "cafe-wood-table-bg", "cafe-blue-chair-bg")
        put(11, m, "coffee-cup-bg", height("cafe-wood-table-bg"))
    around(11, 179.4, "cafe-wood-table-bg", "cafe-blue-chair-bg", sides=(False, True))
    put(11, 179.4, "fish-lemon-bg", height("cafe-wood-table-bg"))
    at11(183.0, "ice-cream-counter")
    at11(183.0, "ice-cream-sign", 56)
    for m in (187.2, 190.8):
        around(11, m, "round-white-table-bg", "wicker-chair-bg")
        put(11, m, "orange-juice-bg", height("round-white-table-bg"))
    decor("downlights-11-cafe", "downlights", x_of(160), x_of(194), deck=11)
    decor("downlights-11-gym", "downlights", x_of(82), x_of(102), deck=11)
    # The Sports Bar, inside by the aft lobby: the back bar and its counter, stools, a TV, darts.
    decor("sports-doorway", "doorway", exact_x(202), exact_x(202), deck=11, text="Sports Bar")
    at11(204.6, "back-bar")
    at11(204.6, "bar-counter")
    for m in (203.6, 204.6, 205.6):
        at11(m, "bar-stool")
    at11(207.6, "wall-tv", 62)
    at11(209.0, "dartboard", 54)
    # The Great Outdoors, open aft (§4, the finale's place): the self-service station first, the
    # coffee machines and the soft serve ice cream machine where she catches Bumbot at last; then
    # round white tables and wicker chairs, parasols where the sky is open, palms.
    decor("outdoors-doorway", "doorway", exact_x(210), exact_x(210), deck=11, text="The Great Outdoors")
    at11(211.4, "chalkboard")
    at11(212.8, "coffee-station")
    at11(214.6, "ice-cream-machine")
    at11(216.4, "juice-station")
    for m in (220.0, 224.0, 228.0, 237.0, 241.0):
        around(11, m, "round-white-table-bg", "wicker-chair-bg")
        put(11, m, ("iced-coffee-bg", "sundae-bg", "lemonade-bg")[int(m) % 3], height("round-white-table-bg"))
    for m in (237.0, 241.0):
        at11(m, "parasol")
    at11(231.4, "planter-palm")
    at11(234.2, "planter-palm")

    # A robot vacuum patrolling the deck 4 cabin corridor.
    add(point("vacuum-1", "vacuum", x_of(130), floor_y(4), [
        prop("minX", x_of(113), "float"), prop("maxX", x_of(186), "float"), prop("speed", 40, "float")]))

    return objs


BOAT_W, BOAT_PITCH = 300, 9      # the lifeboat's drawn length (px) and their spacing (m)


def promenade():
    """Deck 6's promenade (§5.3), as one object for the game to draw and use: its span, the doors,
    the enclosed ends, and the lifeboats hanging in pairs of davits over the open middle, a white
    column between each two boats."""
    deck, (a, b) = PROMENADE["deck"], PROMENADE["span"]
    open_a, open_b = PROMENADE["enclosed"][0][1], PROMENADE["enclosed"][-1][0]
    span = x_of(open_b) - x_of(open_a)
    pitch = BOAT_PITCH * PER_M * TILE
    n = (span - BOAT_W) // pitch + 1
    first = x_of(open_a) + (span - (n - 1) * pitch - BOAT_W) // 2
    boats = [first + k * pitch for k in range(n)]
    gap = (pitch - BOAT_W) // 2
    columns = [x - gap for x in boats] + [boats[-1] + BOAT_W + gap]
    doors = [x_of(m) for m in PROMENADE["doors"]]
    for d in doors:
        assert all(abs(d - c) > 30 for c in columns), ("a promenade door behind a column", metres(d // TILE))
    return area("promenade", "promenade", x_of(a), floor_y(deck) - 2 * DECK_PITCH, x_of(b) - x_of(a), 2 * DECK_PITCH, [
        prop("floor", floor_y(deck), "int"),
        prop("doors", ",".join(map(str, doors))),
        prop("enclosed", ",".join(f"{x_of(p)}:{x_of(q)}" for p, q in PROMENADE["enclosed"])),
        prop("boats", ",".join(map(str, boats))),
        prop("columns", ",".join(map(str, columns))),
    ])


def tile_layer(layer_id, name, grid):
    return {"id": layer_id, "name": name, "type": "tilelayer", "x": 0, "y": 0, "width": COLS,
            "height": ROWS, "opacity": 1, "visible": True,
            "data": [t for row in grid for t in row]}


def build_map():
    back, solid, ladders, exterior = build_layers()
    objs = build_objects()
    return {
        "type": "map", "version": "1.10", "tiledversion": "1.11.0", "orientation": "orthogonal",
        "renderorder": "right-down", "infinite": False, "width": COLS, "height": ROWS,
        "tilewidth": TILE, "tileheight": TILE, "nextlayerid": 6, "nextobjectid": len(objs) + 1,
        "properties": [
            {"name": "deckPitch", "type": "int", "value": DECK_PITCH},
            {"name": "hullMinX", "type": "int", "value": col(EXTENT[4][0]) * TILE},
            {"name": "hullMaxX", "type": "int", "value": col(EXTENT[4][1]) * TILE},
            {"name": "waterY", "type": "int", "value": WATER_ROW * TILE},
            {"name": "deckFloors", "type": "string", "value": json.dumps({d: FLOOR_ROW[d] for d in DECKS})},
            {"name": "exteriorCut", "type": "string", "value": ",".join(str(t) for t in EXT_CUT)},
            {"name": "shellSlopes", "type": "string", "value": json.dumps(shell_slopes())},
            {"name": "endCover", "type": "int", "value": END_COVER},
            {"name": "shellRooms", "type": "string", "value": json.dumps(shell_rooms())},
            {"name": "poolTile", "type": "int", "value": POOL_TILE},
            {"name": "poolSpans", "type": "string", "value": json.dumps([[(col(a) - 1) * TILE, (col(b) + 1) * TILE] for a, b in POOLS])},
            {"name": "shellDetails", "type": "string", "value": json.dumps(shell_details(exterior, solid))},
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
            tile_layer(5, "exterior", exterior),
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
    elif tile_id == LOBBY_CARPET:
        # The lobbies' carpet: deep blue with a mosaic of lighter triangles (the user's photos).
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        rect(0, 0, 15, 3, hex_rgba("#323353"))
        for x in (1, 6, 11):
            px[2][x] = px[2][x + 1] = px[2][x + 2] = hex_rgba("#4d9be6")
            px[1][x + 1] = hex_rgba("#4d9be6")
        for x in (4, 9, 14):
            px[0][x] = hex_rgba("#0b8a8f")
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id == WALNUT:
        # La Cucina's dark wood panelling (the user's photos): tall panels, a lighter edge.
        rect(0, 0, 15, 15, hex_rgba("#5e3d2c"))
        rect(0, 0, 0, 15, hex_rgba("#46291f"))
        rect(1, 0, 1, 15, hex_rgba("#74503a"))
        rect(8, 0, 8, 15, hex_rgba("#46291f"))
        rect(9, 0, 9, 15, hex_rgba("#74503a"))
    elif tile_id == CUCINA_WALL:
        # The grey-blue wall by La Cucina's entrance, a faint diamond lattice on it.
        rect(0, 0, 15, 15, hex_rgba("#66728c"))
        for i in range(16):
            px[i][i] = px[i][15 - i] = hex_rgba("#717d97")
    elif tile_id == DINING_WALL:
        # The dining rooms' cream walls.
        rect(0, 0, 15, 15, hex_rgba("#efe6d2"))
        rect(0, 0, 0, 15, hex_rgba("#e7dcc4"))
    elif tile_id in (DINING_CARPET, DIAMOND_CARPET, ATRIUM_CARPET):
        # Carpets on the steel deck: the dining rooms' dark floral, La Cucina's dark diamonds, the
        # atrium's blue-green.
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        base, dots = {DINING_CARPET: ("#45293f", ("#cd683d", "#fbb954", "#4d65b4")),
                      DIAMOND_CARPET: ("#2e222f", ("#9babb2",)),
                      ATRIUM_CARPET: ("#0b5e65", ("#8fd3ff", "#0eaf9b"))}[tile_id]
        rect(0, 0, 15, 3, hex_rgba(base))
        if tile_id == DIAMOND_CARPET:
            for x in (2, 10):
                px[1][x] = px[0][x + 1] = px[1][x + 2] = px[2][x + 1] = hex_rgba(dots[0])
        else:
            for i, (x, y) in enumerate(((1, 1), (5, 2), (8, 0), (12, 1), (14, 3), (3, 3))):
                px[y][x] = hex_rgba(dots[i % len(dots)])
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id in (BLISS_WALL, WINDJAMMER_WALL, GALLERY_WALL, THEATRE_WALL):
        # Bliss: near-black plum; the Windjammer: dark green; the gallery: white; the theatre: deep
        # navy (the user's photos), each with a faint seam.
        base, seam = {BLISS_WALL: ("#2b2433", "#342c3e"), WINDJAMMER_WALL: ("#1f3b35", "#25453e"),
                      GALLERY_WALL: ("#f2f2f0", "#e8e8e5"), THEATRE_WALL: ("#262440", "#2e2c4c")}[tile_id]
        rect(0, 0, 15, 15, hex_rgba(base))
        rect(0, 0, 0, 15, hex_rgba(seam))
    elif tile_id == BURL_WALL:
        # Burl wood, orange-brown and mottled (the Restaurant Reservations desk, the user's photo).
        rect(0, 0, 15, 15, hex_rgba("#b5653a"))
        for x, y in ((2, 3), (3, 3), (9, 1), (12, 6), (13, 6), (5, 9), (6, 10), (10, 12), (1, 13), (14, 14)):
            px[y][x] = hex_rgba("#9e4539")
        for x, y in ((7, 4), (11, 9), (3, 12), (14, 2)):
            px[y][x] = hex_rgba("#cd683d")
    elif tile_id == WOOD_FLOOR:
        # Warm wooden planks on the steel deck.
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        rect(0, 0, 15, 3, hex_rgba("#9e4539"))
        rect(0, 0, 15, 0, hex_rgba("#cd683d"))
        px[1][5] = px[2][5] = px[1][13] = px[2][13] = hex_rgba("#6e2727")
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id in (BLISS_CARPET, LIBRARY_CARPET, THEATRE_CARPET, LOBBY6_CARPET):
        # Bliss: dark with grey and white dots; the library: cream with red diagonal strokes; the
        # theatre: deep red; deck 6's lobbies: purple-navy with gold.
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        base, marks = {BLISS_CARPET: ("#2e222f", ("#9babb2", "#ffffff")),
                       LIBRARY_CARPET: ("#e9e1d6", ("#9e4539", "#b33831")),
                       THEATRE_CARPET: ("#6e2727", ("#7a3045",)),
                       LOBBY6_CARPET: ("#323353", ("#f9c22b",))}[tile_id]
        rect(0, 0, 15, 3, hex_rgba(base))
        if tile_id == LIBRARY_CARPET:
            for x in (0, 4, 8, 12):
                px[0][x + 3] = px[1][x + 2] = px[2][x + 1] = px[3][x] = hex_rgba(marks[x // 4 % 2])
        else:
            for i, (x, y) in enumerate(((1, 1), (5, 2), (8, 0), (12, 1), (14, 3), (3, 3))):
                px[y][x] = hex_rgba(marks[i % len(marks)])
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id in (KIDS_WALL, TEEN_WALL, CASINO_WALL, ARCADE_WALL):
        # Splash Academy: sunny yellow; Entourage: deep teal; the casino: deep red; the arcade: night
        # blue; each with a faint seam.
        base, line = {KIDS_WALL: ("#fbe9a6", "#f4dd92"), TEEN_WALL: ("#0b4a50", "#0b5e65"),
                      CASINO_WALL: ("#5a1d2a", "#652333"), ARCADE_WALL: ("#1d1f3a", "#262a4a")}[tile_id]
        rect(0, 0, 15, 15, hex_rgba(base))
        rect(0, 0, 0, 15, hex_rgba(line))
    elif tile_id in (KIDS_CARPET, CASINO_CARPET, ARCADE_CARPET):
        # Splash Academy: bright blue with coloured dots; the casino: red and gold; the arcade and
        # Entourage: dark with neon specks.
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        base, marks = {KIDS_CARPET: ("#4d9be6", ("#f9c22b", "#e83b3b", "#1ebc73")),
                       CASINO_CARPET: ("#7a3045", ("#f9c22b", "#e83b3b")),
                       ARCADE_CARPET: ("#2e222f", ("#30e1b9", "#f04f78", "#a884f3"))}[tile_id]
        rect(0, 0, 15, 3, hex_rgba(base))
        for i, (x, y) in enumerate(((1, 1), (5, 2), (8, 0), (12, 1), (14, 3), (3, 3))):
            px[y][x] = hex_rgba(marks[i % len(marks)])
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id == BALCONY_RAIL:
        pass    # solid but unseen: the game draws the balcony's front over it
    elif tile_id in (SPA_WALL, CAFE_WALL):
        # The spa: a soft sage; the Garden Café: pale grey-white panels (the user's photo).
        base, seam = {SPA_WALL: ("#dfe6d6", "#d2dbc7"), CAFE_WALL: ("#eef0ee", "#e0e4e2")}[tile_id]
        rect(0, 0, 15, 15, hex_rgba(base))
        rect(0, 0, 0, 15, hex_rgba(seam))
    elif tile_id == SAUNA_WALL:
        # The sauna and massage rooms: pale pine boards (a first, brighter orange stood out).
        rect(0, 0, 15, 15, hex_rgba("#ead2ae"))
        for y in (3, 7, 11, 15):
            rect(0, y, 15, y, hex_rgba("#dcbf96"))
        px[1][6] = px[9][13] = hex_rgba("#cfae82")
    elif tile_id == GYM_FLOOR:
        # The gym: black rubber flooring, flecked.
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        rect(0, 0, 15, 3, hex_rgba("#313638"))
        for x, y in ((1, 1), (5, 2), (9, 1), (13, 2)):
            px[y][x] = hex_rgba("#625565")
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id == CAFE_CARPET:
        # The Garden Café: a dark blue carpet with a small grey pattern (the user's photo).
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        rect(0, 0, 15, 3, hex_rgba("#323353"))
        for x, y in ((2, 1), (6, 2), (10, 1), (14, 2)):
            px[y][x] = hex_rgba("#7f708a")
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id == BRIDGE_WALL:
        # The bridge: pale grey-blue steel panels, a seam on each.
        rect(0, 0, 15, 15, hex_rgba("#d3dde0"))
        rect(0, 0, 0, 15, hex_rgba("#bfcbd0"))
    elif tile_id == BRIDGE_FLOOR:
        # The bridge's floor: dark grey non-slip vinyl, flecked.
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        rect(0, 0, 15, 3, hex_rgba("#3e3546"))
        for x, y in ((2, 1), (7, 2), (11, 1), (14, 2)):
            px[y][x] = hex_rgba("#625565")
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id == MAHOGANY:
        # The lobbies' panelling: a warm terracotta wood with a faint lighter grain, as in the user's
        # deck 8 photo (2026-11-06: lighter than the dark maroon first drawn).
        rect(0, 0, 15, 15, hex_rgba("#b5604a"))
        for x, y in ((3, 2), (3, 3), (3, 4), (9, 8), (9, 9), (12, 12), (12, 13), (6, 14)):
            px[y][x] = hex_rgba("#c4735a")
        for x, y in ((7, 4), (13, 6), (1, 10)):
            px[y][x] = hex_rgba("#a5543f")
        rect(0, 0, 0, 15, hex_rgba("#9e4539"))
    elif tile_id in (HULL, EXT, EXT_FIXED):
        # The ship's off-white outer plating, clean (seams on every tile read as stripes).
        rect(0, 0, 15, 15, hex_rgba(PLATING))
    elif tile_id in (EXT_SLAB, EXT_FIXED_SLAB):
        # The plating along a deck's floor, plain like the rest.
        rect(0, 0, 15, 15, hex_rgba(PLATING))
    elif tile_id in (EXT_EDGE_L, EXT_EDGE_R):
        # The wall at the edge of the cut-away stretch, shaded toward the cut to show its thickness.
        rect(0, 0, 15, 15, hex_rgba(PLATING))
        for i, colour in enumerate(("#bfc5ca", "#c9ced3", "#d8dcdf")):
            x = i if tile_id == EXT_EDGE_L else 15 - i
            rect(x, 0, x, 15, hex_rgba(colour))
    elif tile_id in (EXT_CORNER_L, EXT_CORNER_R):
        # A rounded outer corner: plating inside a quarter circle.
        for y in range(16):
            for x in range(16):
                dx = 15 - x if tile_id == EXT_CORNER_L else x
                if dx * dx + (15 - y) * (15 - y) <= 16 * 16:
                    px[y][x] = hex_rgba(PLATING)
    elif tile_id == SLAB:
        # The deck's steel slab with nothing laid on it: under the ship's structure.
        rect(0, 0, 15, 15, hex_rgba("#8e98a3"))
        rect(0, 15, 15, 15, hex_rgba("#6f7882"))
    elif tile_id in (FRAMES, FRAMES_RIB):
        # The ship's structure between a corridor's end and the plating: plain grey steel, and on
        # every second column a frame rib with its lit edge.
        rect(0, 0, 15, 15, hex_rgba("#9babb2"))
        if tile_id == FRAMES_RIB:
            rect(6, 0, 7, 15, hex_rgba("#7f708a"))
            rect(8, 0, 8, 15, hex_rgba("#b2ba90"))
    elif tile_id in (END_WALL_L, END_WALL_R):
        # A corridor's end wall, turning away from us: the cream wall in three darkening steps
        # toward the structure behind it.
        steps = ("#cdbfa6", "#d9cdb6", "#e2d7c2")
        for i, colour in enumerate(steps):
            x0, x1 = i * 5, i * 5 + 4 if i < 2 else 15
            if tile_id == END_WALL_R:
                x0, x1 = 15 - x1, 15 - x0
            rect(x0, 0, x1, 15, hex_rgba(colour))
    elif tile_id == CABIN_WALL:
        # The cabin corridors' wallpaper: the cream wall with a faint diamond lattice, a shade off it.
        rect(0, 0, 15, 15, hex_rgba("#e9dfcc"))
        for i in range(8):
            for x, y in ((i, 7 - i), (8 + i, i), (i, 8 + i), (8 + i, 15 - i)):
                px[y][x] = hex_rgba("#e4d9c4")
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


# --- The ship's sun on the bow ---------------------------------------------------------------------

# The livery's bands run on past the bow's block onto the decks' fixed ends, tapering to a tip
# before the cut-away corridors (and the wall drawn over her there) begin (the user, 2026-11-03).
LIVERY_END = BOW["block"] + 1.8


def livery_box():
    """The bow's hull block, in pixels: from the stem's tip back to the block's end, from under the
    forecastle down to the waterline."""
    x0, x1 = col(BOW["stem"][7]) * TILE, col(LIVERY_END) * TILE
    y0, y1 = (FLOOR_ROW[7] + 1) * TILE, (WATER_ROW + 1) * TILE
    return x0, y0, x1, y1


def build_livery():
    """The ship's sun, as painted on the real bow (the user's photos, §5.3), scaled to cover most of
    the bow's side: concentric rings of deep red, red, orange and yellow round a white centre;
    curved flame-like rays swirling round it, each red with orange and yellow inside and a grey
    shadow on its trailing edge; and red, orange and yellow bands with a grey line sweeping aft
    below it. Cut to the stem's line, as if wrapping round the bow. No lettering (§5.1)."""
    import math
    from PIL import Image, ImageDraw
    from palettize import palettize

    x0, y0, x1, y1 = livery_box()
    w, h = x1 - x0, y1 - y0
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    # Laid out as on the real bow (the user's side-view photo), compressed into the bow's hull
    # block: the sun high on the bow; forward of it a red band above and a red, orange and yellow
    # band below running in from the stem; aft of it a big red arc looping up and over, a yellow
    # swoop under it, and thin red pinstripes on aft. The bands stop short of the sun's rim.
    cx, cy = x_of(14.5) - x0, round((FLOOR_ROW[3] - FLOOR_ROW[7] - 1) * TILE * 0.3)  # high on the bow, clear of the stem
    r = 72

    def ray(angle, base, tip, width, colour):
        """A curved flame: from `base` out to `tip` radii, `width` degrees wide at its base, its tip
        swept round clockwise."""
        left, right = [], []
        for i in range(13):
            t = i / 12
            rad = base + (tip - base) * t
            sweep = 20 * t ** 1.4
            half = width * (1 - t) ** 0.8
            for side, a in ((left, angle - half + sweep), (right, angle + half * 0.6 + sweep)):
                side.append((cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a))))
        d.polygon(left + right[::-1], fill=colour)
        return right

    def band(points, colours, width=8, shadow=True, taper=0.12):
        """Stripes stacked under the line through `points`, the whole band narrowing to a point over
        its last `taper` of the way (the stripes drawn as polygons, so they can narrow)."""
        n = len(points)
        mid = len(colours) * width / 2

        def squeeze(i):
            t = i / (n - 1)
            return 1 if t < 1 - taper else max(0.0, (1 - t) / taper) ** 0.8

        stripes = [(colour, k * width - width / 2, k * width + width / 2) for k, colour in enumerate(colours)]
        if shadow:
            top = len(colours) * width - width / 2 + 1
            stripes.append(("#9babb2", top - 1, top + 2))
        for colour, a, b in stripes:
            upper = [(x, y + mid + (a - mid) * squeeze(i)) for i, (x, y) in enumerate(points)]
            lower = [(x, y + mid + (b - mid) * squeeze(i)) for i, (x, y) in enumerate(points)]
            d.polygon(upper + lower[::-1], fill=colour)

    def curve(f, n=80):
        return [f(i / n) for i in range(n + 1)]

    # Two bands, in the bow's wide upper part (the stem rakes back below): a red one sweeping down
    # from the bow's top into the sun, and a red, orange and yellow one coming in level from the
    # stem. Both run on behind the sun and, past it, part: the upper curving up, the lower down.
    def upper(t):
        if t <= 0.6:
            u = t / 0.6
            return cx * u, 24 + (cy - 64) * u ** 1.5
        u = (t - 0.6) / 0.4
        return cx + (w - cx) * u, cy - 40 + 40 * u - 110 * u * u

    def lower(t):
        if t <= 0.6:
            u = t / 0.6
            return cx * u, cy + 6 + 14 * math.sin(math.pi * u)
        u = (t - 0.6) / 0.4
        return cx + (w - cx) * u, cy + 6 - 10 * u + 90 * u * u

    band(curve(upper, 160), ("#e83b3b",), 10)
    band(curve(lower, 160), ("#e83b3b", "#fb6b1d", "#f9c22b"), 7)
    # A clear gap round the sun's rim, then the sun over it.
    gap = r * 1.12
    d.ellipse((cx - gap, cy - gap, cx + gap, cy + gap), fill=(0, 0, 0, 0))
    for i in range(12):
        a = i * 30 - 75
        edge = ray(a, r * 0.95, r * 1.9, 19, "#e83b3b")
        d.line([(x + 3, y + 3) for x, y in edge], fill="#9babb2", width=5)
        ray(a + 2, r * 1.05, r * 1.72, 12, "#fb6b1d")
        ray(a + 3, r * 1.15, r * 1.5, 6, "#f9c22b")
    for frac, colour in ((1.0, "#ae2334"), (0.84, "#e83b3b"), (0.66, "#fb6b1d"), (0.5, "#f9c22b"),
                         (0.34, "#ffffff")):
        rr = r * frac
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=colour)

    # Cut to the stem: nothing forward of the hull's smooth edge.
    px = img.load()
    for y in range(h):
        edge = round(stem_x((y + y0) / TILE)) + 2 - x0
        for x in range(min(max(edge, 0), w)):
            px[x, y] = (0, 0, 0, 0)
    out = ROOT / "assets" / "ship" / "livery.png"
    palettize(img).save(out)
    return out


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
    print("wrote", build_livery().relative_to(ROOT))
