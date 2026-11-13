"""Everything the plan puts on the ship (docs/population.md), as data: the rooms behind doors, the
checkpoints, the tangerines, the books, the pickups, Bumbot's beats, the grips for wall jumps, the
ladders between routes, the things outside. Positions are metres from the bow on the deck named
(the builder's `x_of`), or pixels from a room's left edge for things inside a room.

The map builder (tools/build_ship_map.py) turns this into maps/world.json, which the game's world
(src/world/) reads. Built step by step (docs/build-plan.md); what a step changed against the spec is
recorded in docs/progress-decisions.md.
"""

# --- Rooms behind doors ----------------------------------------------------------------------------
# A room she enters with E at its door; it shows in the corridor's place, the deck dimmed round it
# (the user's rule, CLAUDE.md). `m`: its door on the deck; on a cabin corridor it takes the nearest
# cabin door's place (`slot`). `width`: the drawing's (tools/draw_rooms.py), its door `door_x` in
# from its left edge. `lock`: as ship_layout's DOOR_LOCKS. `door`: how the door looks from the
# corridor ("crew", "cabin", "open": held open, "hatch", "bookcase"). `doors`: more ways out, each
# (x in the room, where it leads: route, deck, m, lock). `checkpoint`: she comes back at its door.
ROOMS = [
    dict(id="laundry", deck=4, m=112, slot=True, width=336, look="laundry", door="crew", plate="LAUNDRY",
         lock=("card", "hk", 0), checkpoint="cp_laundry"),
    dict(id="store", deck=4, m=165, slot=True, width=240, look="store", door="crew", plate="DRY STORE",
         lock=("card", "hk", 0)),
    dict(id="smcabin", deck=4, m=232, slot=True, width=240, look="crewcabin", door="cabin", plate="STAGE MGR"),
    dict(id="pantry", deck=5, m=166, width=288, look="pantry", door="crew", plate="PANTRY", lock=("card", "hk", 0),
         doors=[dict(x=236, to="inside", deck=5, m=191.5, door="crew", plate="PANTRY", lock=("card", "hk", 0))]),
    dict(id="galley", deck=5, m=250.1, width=336, look="galley", door="crew", plate="GALLEY"),
    dict(id="nook", deck=6, m=189, width=240, look="nook", door="bookcase", needs="nook"),
    dict(id="dressing", deck=6, m=242.5, width=240, look="dressing", door="crew", plate="STAGE DOOR",
         lock=("card", "ent", 0)),
    dict(id="lighting", deck=7, m=206, width=480, look="lighting", door="crew", plate="LIGHTING",
         lock=("card", "ent", 0)),
    dict(id="lifeboat", deck=7, m=147.5, route="outside", width=240, look="lifeboat", door="hatch"),
    dict(id="cleanup", deck=9, m=140, slot=True, width=240, look="cabin", door="open"),
    dict(id="balcabin9", deck=9, m=150, slot=True, width=288, look="balcabin", door="cabin",
         lock=("card", "hk", 0), checkpoint="cp_balcabin",
         doors=[dict(x=262, to="outside", deck=9, door="balcony")]),
    dict(id="adjoin", deck=9, m=176, slot=True, width=432, look="adjoin", door="cabin",
         doors=[dict(x=432 - 59, to="inside", deck=9, m=184, slot=True, door="cabin")]),
    dict(id="balcabin8m", deck=8, m=150, slot=True, width=288, look="balcabin", door="cabin", lock=("oneway", 1),
         doors=[dict(x=262, to="outside", deck=8, door="balcony")]),
    dict(id="balcabin8a", deck=8, m=230, slot=True, width=288, look="balcabin", door="cabin", lock=("oneway", 1),
         doors=[dict(x=262, to="outside", deck=8, door="balcony")]),
    dict(id="balcabin9a", deck=9, m=225, slot=True, width=288, look="balcabin", door="cabin", lock=("oneway", 1),
         doors=[dict(x=262, to="outside", deck=9, door="balcony")]),
    dict(id="balcabin10a", deck=10, m=215, slot=True, width=288, look="balcabin", door="cabin", lock=("oneway", 1),
         doors=[dict(x=262, to="outside", deck=10, door="balcony")]),
    dict(id="guest10", deck=10, m=235, slot=True, width=288, look="balcabin", door="cabin", lock=("card", "hk", 0),
         doors=[dict(x=262, to="outside", deck=10, door="balcony", lock=("flag", "guest"))]),
    dict(id="coldroom", deck=11, m=185, width=240, look="coldroom", door="crew", plate="COLD ROOM",
         lock=("card", "hk", 0)),
]

# The duct (population §6.5): a crawl space at deck 9's floor level, from the linen room's vent
# forward to a grille over deck 8's forward corridor, where she drops out. Grilles on the way show
# what is below (m, what).
DUCT = dict(deck=9, m_in=112, m_out=66, drop_deck=8, length=1300,
            grilles=["lobby", "dome", "balloons", "snore"])

# --- Checkpoints (population §2.5) -----------------------------------------------------------------
# id: (deck, m, route, slot). Crew doors; `slot` takes a cabin door's place. The rooms' own doors
# (`checkpoint` above), cabin 8206's and the funnel's locker are made by the game. Moved against the
# spec where a lobby has no wall free between its stairs and its elevator (progress-decisions).
CHECKPOINTS = {
    "cp_gangway": (4, 72, "inside", False),
    "cp_4_aft": (4, 212, "inside", True),
    "cp_6_fwd": (6, 40, "inside", True),
    "cp_library": (6, 192.4, "inside", False),
    "cp_foyer": (6, 204.4, "inside", False),
    "cp_7_aft": (7, 191.6, "inside", False),
    "cp_station": (7, 128, "outside", False),
    "cp_9_mid": (9, 190, "inside", True),
    "cp_gym": (11, 84, "inside", False),
    "cp_garden": (11, 192, "inside", False),
    "cp_technical": (12, 165, "inside", False),
    "cp_officer": (10, 60, "inside", True),
    "cp_chapel": (12, 70.7, "inside", False),
    "cp_bridge": (10, 43, "inside", True),
}

# --- Tangerines (population §2.3) ------------------------------------------------------------------
# id: (deck or room id, m or x in the room, count, what it rests on, needs). "table": a small side
# table of its own; a number: that many px up, on a piece already there. `needs`: a flag (the bowl
# Bumbot knocks over) or "break:<id>" (behind a breakable).
TANGERINES = {
    "tan_4_30": (4, 31.2, 1, "table", None),
    "tan_4_laundry": ("laundry", 250, 1, 46, None),
    "tan_4_store": ("store", 150, 2, 40, None),
    "tan_5_cafe": (5, 90, 1, "table", None),
    "tan_5_dessert": (5, 190, 1, "table", None),
    "tan_5_bowl": (5, 245, 3, 0, "bb1"),
    "tan_5_galley": ("galley", 250, 2, 0, None),
    "tan_6_high": (6, 26, 1, 106, None),
    "tan_6_windjammer": (6, 142, 1, "table", None),
    "tan_7_jackpot": (7, 160, 2, 0, "jackpot"),
    "tan_7_tradewinds": (7, 180, 1, "table", None),
    "tan_8_8206": ("cabin", 104, 2, 33, None),
    "tan_8_aft": (8, 246, 1, "table", None),
    "tan_8_balc_fwd": (8, 100, 1, "out", None),
    "tan_8_balc_aft": (8, 245, 1, "out", None),
    "tan_9_balcabin": ("balcabin9", 150, 1, 30, None),
    "tan_9_cart": (9, 172, 1, "table", None),
    "tan_9_luggage": (9, 181.5, 1, "table", None),
    "tan_9_balc": (9, 240, 1, "out", None),
    "tan_10_mid": (10, 182, 1, "table", None),
    "tan_11_spa": (11, 32, 1, "table", None),
    "tan_11_topsiders": (11, 145, 1, "table", None),
    "tan_11_fruit": (11, 176, 2, "table", None),
    "tan_11_crates": (11, 208.2, 2, 0, None),
    "tan_12_spinnaker": (12, 54, 2, "table", None),
    "tan_12_lady": (12, 128, 2, 0, "lady"),
    "tan_12_cagneys": (12, 167, 1, "table", None),
    "tan_12_pinata": (12, 211, 2, 0, "pinata"),
    "tan_funnel": ("funnel", 188, 1, 0, None),
}

# --- Pickups ---------------------------------------------------------------------------------------
# id: (deck or room, m or x, what she gets, needs flag). `what`: "verb:<name>" a new way to move,
# "book:<n>", "item:<name>" a pocket item. All taken with E (population §2.1, §2.2).
ITEMS = {
    "item_socks": (11, 96, "verb:socks", None),
    "item_parasol": (12, 130, "verb:parasol", "horn"),
    "item_pills": ("smcabin", 170, "item:pills", "bb3"),
    "book_1": (5, 96, "book:1", None),
    "book_2": ("lifeboat", 150, "book:2", None),
    "book_3": ("dressing", 150, "book:3", None),
    "book_4": (9, 134, "book:4", None),
    "book_5": ("cabin", 190, "book:5", None),
    "book_6": (11, 216, "book:6", None),
    "book_7": ("guest10", 150, "book:7", None),
    "book_8": (12, 128.6, "book:8", "horn"),
    "book_9": ("funnel", 184, "book:9", "horn"),
    "book_10": (10, 37.5, "book:10", None),
}

# --- Bumbot's beats (GAME_DESIGN.md §6.1.8) --------------------------------------------------------
# id: (deck or room, m or x, what he is doing, which way he bolts, where he is gone (m or x), needs).
# Each sets its own flag when he is away. Step 0: his built near-catch, no choreography yet.
BEATS = {
    "bb1": (5, 248.8, "eat", -1, 203, None),
    "bb2": (6, 178, "asleep", 1, 193.6, None),
    "bb3": (6, 249, "wash", 1, 250.6, None),
    "bb4": ("linen", 150, "asleep", 1, 226, None),
    "bb5": (11, 131.8, "bat", 1, 160, None),
    "bb6": (10, 31, "sit", -1, 29.2, None),
}
# What a flag gives besides itself: a verb learned at a beat.
FLAG_GIVES = {"bb1": ["verb:dash"], "bb4": ["verb:crawl"], "bb5": ["flag:drain"], "bb6": ["flag:alarm"]}
# He lies this many px up (on the towels, on a counter).
BEAT_LIFT = {"bb4": 6, "bb1": "service-station-bg"}      # px, or the piece he is on

# --- Things she pushes (the push verb, region 4) ----------------------------------------------------
# id: (deck or room, m or x, how far it rolls (m or x), the atlas piece, flag set when it gets there,
# tall: it fills the doorway until then, the side she pushes from: -1 forward of it).
PUSHABLES = {
    "cart_steward": (9, 122.6, 130, "service-cart", "cart_free", True, -1),
}

# The trap door in the stage and the tip of the bow (m), where the catch is.
TRAPDOOR_M = 250
CATCH_M = 6

# --- Switches: E on a thing sets a flag (step 0's stand-ins for scenes) ----------------------------
# id: (deck or room, m or x, flag, needs, label).
SWITCHES = {
    "sw_horn": ("funnel", 186, "horn", None, "HORN"),
    "sw_cake": (12, 84, "wedding", None, "CAKE"),
}

# --- Wall jumps (GAME_DESIGN.md §6.1.3, region 6) --------------------------------------------------
# Grip surfaces besides the balconies' partitions (which the builder adds): (route, m, deck its foot
# stands on, px up to its foot, px up to its top, side she is on: -1 forward of it, 1 aft, 0 either).
GRIPS = [
    # The atrium's pillars, deck 5's floor to deck 10's walk.
    ("inside", 86, 5, 0, 5 * 144, 0), ("inside", 98, 5, 0, 5 * 144, 0),
    # The boat walkway's recess, its end walls up to deck 8's balconies.
    ("outside", 100.6, 7, 0, 150, 1), ("outside", 230.4, 7, 0, 150, -1),
    # The Great Outdoors' sun cover: its aft post, the climb up to deck 12 (region 8's way in).
    ("inside", 233, 11, 0, 124, 1),
]
