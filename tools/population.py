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
    # (Its door is at its aft end: the deck's last metres are structure, so the room lies forward of it.)
    dict(id="galley", deck=5, m=250.1, width=336, door_x=336 - 59, look="galley", door="crew", plate="GALLEY"),
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
    "tan_5_cafe": (5, 83.6, 1, 28, None),
    "tan_5_dessert": (5, 186.4, 1, 26, None),
    "tan_5_bowl": (5, 245, 3, 0, "bb1"),
    "tan_5_galley": ("galley", 36, 2, 0, "broken:haz_crate_galley"),
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
    "item_pills": ("smcabin", 172, "item:pills", "bb3", 50),
    "book_1": (5, 85.5, "book:1", None, 23),
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
TRAPDOOR_LANDS = ("galley", 86)     # on the flour sacks
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

# --- People (GAME_DESIGN.md §6.1.6, docs/population.md §3 and §7) ----------------------------------
# id: dict(at=(deck or room, m or x), who=<tools/cast.py name>, face=1 east / -1 west, ...):
#   idle: the clip she or he loops standing; walk=(from m, to m, m/s[, clip]) a loop, with
#   stops=[m...] where they turn aside for stop_ms (out of her way meanwhile), end_ms at each end;
#   touch=(kind, width px, height px[, fright, dx]) what running into them does: "scare" (a fright,
#   or a spill if she carries a tray), "spill" (only ever a spill); carry=[(atlas piece or "@" a
#   picture the game draws, dx, dy, front)] what goes along with them; bubble=(pictogram, when,
#   unless[, range m]) their request; until / after: a condition (src/world/world.js `cond`) that
#   takes them away / brings them; layer: "behind" furniture (a desk), "back" (scenery people,
#   behind her), default beside her.
PEOPLE = {
    # Region 1, deck 4.
    "amb_lost": dict(at=(4, 24), who="tourist", face=1, idle="idle", layer="back"),
    "haz_porter": dict(at=(4, 58), who="porter", face=1, walk=(53.5, 64, 1.0, "cart"), end_ms=1500,
                       touch=("scare", 46, 44, "bumped", 12),
                       carry=[("luggage-trolley", 24, 0, False), ("suitcases", 24, 29, False)]),
    "npc_officer": dict(at=(4, 65.6), who="officer", face=1, idle="idle",
                        bubble=("tray", "!card:deck", None, 4)),
    "amb_robe": dict(at=(4, 130), who="robe", face=-1, idle="idle", layer="back"),
    "amb_folder": dict(at=("laundry", 258), who="folder", face=1, idle="idle"),
    # Region 1, deck 5.
    "amb_breakfast": dict(at=(5, 44.4), who="stewardess", face=1, idle="idle", layer="back"),
    "riv_rope": dict(at=(5, 79.55), who="rival", face=-1, idle="idle", until="region:2"),
    "amb_reception": dict(at=(5, 99.55), who="receptionist", face=-1, idle="idle", layer="behind"),
    "blk_photographer": dict(at=(5, 87.9), who="photographer", face=1, idle="idle", until="region:3"),
    "amb_poser_him": dict(at=(5, 90.35), who="gentleman", face=-1, idle="idle", until="region:3"),
    "amb_poser_her": dict(at=(5, 91.25), who="lady", face=-1, idle="idle", until="region:3"),
    "blk_cleaner": dict(at=(5, 106.1), who="cleaner", face=1, idle="mop", until="region:3"),
    "amb_agent": dict(at=(5, 115.3), who="agent", face=-1, idle="idle", layer="back"),
    "haz_waiter": dict(at=(5, 172), who="waiter", face=1, walk=(170.2, 192.2, 1.5, "serve"), stops=[175.4, 184.2],
                       stop_ms=2400, end_ms=900, touch=("spill", 22, 56),
                       carry=[("@tray", 9, 42, True), ("@load-cloche", 9, 45, True)]),
    "amb_host": dict(at=(5, 205.3), who="maitre", face=-1, idle="idle", layer="back"),
    "amb_chef_7s": dict(at=("galley", 182), who="chef", face=-1, idle="idle"),
    # Diners (drawn seated, each on a chair of their own, in a dining chair's place at a table).
    "amb_cucina_her": dict(at=(5, 159.8 - 0.17), who="diner_teal", face=1, layer="back"),
    "amb_cucina_him": dict(at=(5, 164.1 + 0.17), who="diner_linen", face=-1, layer="back"),
    "amb_7s_her": dict(at=(5, 213.0 - 0.17), who="diner_red", face=1, layer="back"),
    "amb_7s_him": dict(at=(5, 221.8 + 0.17), who="diner_suit", face=-1, layer="back"),
}

# --- Things the plan adds to the decks -------------------------------------------------------------
# Props: id: (deck or room, m or x, atlas piece, dy px up, options: until/after a condition, front,
# back (behind furniture), flip).
PROPS = {
    "prop_backdrop": (5, 90.9, "photo-backdrop", 0, dict(until="region:3")),
    "prop_wetfloor": (5, 107.7, "wet-floor-sign", 0, dict(until="region:3")),
    "prop_coffee_cafe": (5, 85.72, "coffee-cup", 23, {}),
    "prop_bowl_cafe": (5, 83.6, "fruit-bowl-2", 23, {}),
    "prop_bowl_7s": (5, 247.0, "fruit-bowl", 27, {}),
    "prop_board": (4, 190.6, "notice-board", 40, {}),
}
# Things standing in the way that she hops: id: (deck, m, atlas piece).
SOLIDS = {
    "haz_cart_4_90": (4, 90, "service-cart"),
    "haz_cart_4_182": (4, 182, "towel-trolley"),
    "haz_cart_4_220": (4, 220, "service-cart"),
    "haz_cart_5_30": (5, 30, "towel-trolley"),
}
# Things the dash goes through: id: (deck or room, m or x, [(atlas piece, dx, dy)]).
BREAKABLES = {
    "haz_luggage_4": (4, 30, [("suitcases", -13, 0), ("suitcases", 14, 0), ("beach-bag", 2, 25)]),
    "haz_crate_galley": ("galley", 36, [("@crate-big", 0, 0)]),
}
# Quirks (§6.1.11): a moment with no reward. id: (deck or room, m or x, trigger: "E" or "still:<s>",
# her clip, ms it lasts, options: needs).
QUIRKS = {
    "sec_swan": (5, 177.6, "E", "shiver", 1700, {}),
}
# Trays to take: id: (deck or room, m or x, what, after, [(texture, dy)] shown there).
SOURCES = {
    "src_lunch": (5, 248.8, "lunch", "flag:bb1", [("tray", 24), ("load-cloche", 27)]),
}
# Signs: id: (deck, m, text, style: plate / poster / note, dy px up, options: size, wrap).
SIGNS = {
    "sign_lockdown_1": (4, 56, "SEARCH\nIN PROGRESS", "poster", 56, dict(size=5)),
    "sign_lostcat": (4, 190.6, "LOST:\nCAT", "note", 54, dict(size=4)),
    "sign_name_1": (4, 224.2, "BOSUN", "plate", 52, {}),
    "sign_name_2": (4, 228.2, "PURSER", "plate", 52, {}),
    "sign_name_3": (4, 236.1, "DJ", "plate", 52, {}),
}
