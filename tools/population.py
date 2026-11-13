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
    # A cabin being made up, its door held open (population: `amb_maid`): a peek.
    dict(id="maid6", deck=6, m=48, slot=True, width=240, look="cabin", door="open"),
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
    dict(id="balcabin8m", deck=8, m=159, slot=True, width=288, look="balcabin", door="cabin", lock=("oneway", 1),
         checkpoint="cp_hall_8m",
         doors=[dict(x=262, to="outside", deck=8, door="balcony")]),
    dict(id="balcabin8a", deck=8, m=230, slot=True, width=288, look="balcabin", door="cabin", lock=("oneway", 1),
         checkpoint="cp_hall_8a",
         doors=[dict(x=262, to="outside", deck=8, door="balcony")]),
    dict(id="balcabin9a", deck=9, m=225, slot=True, width=288, look="balcabin", door="cabin", lock=("oneway", 1),
         checkpoint="cp_hall_9a",
         doors=[dict(x=262, to="outside", deck=9, door="balcony")]),
    dict(id="balcabin10a", deck=10, m=215, slot=True, width=288, look="balcabin", door="cabin", lock=("oneway", 1),
         checkpoint="cp_hall_10a",
         doors=[dict(x=262, to="outside", deck=10, door="balcony")]),
    dict(id="guest10", deck=10, m=235, slot=True, width=288, look="balcabin", door="cabin", lock=("card", "hk", 0), checkpoint="cp_hall_guest",
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
    "cp_library": (6, 160.85, "inside", False),
    "cp_foyer": (6, 204.4, "inside", False),
    "cp_7_aft": (7, 191.6, "inside", False),
    "cp_station": (7, 128, "outside", False),
    "cp_9_arrive": (9, 119.6, "inside", True),
    "cp_9_mid": (9, 190, "inside", True),
    "cp_gym": (11, 84, "inside", False),
    # (The pool attendant's hut on pool 2's aft rim: the kid's and the wet patch's frights come back here.)
    "cp_pool": (11, 140.6, "inside", False),
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
    "tan_6_high": (6, 26.94, 1, 118, None),
    "tan_6_windjammer": (6, 142.2, 1, 32, None),
    "tan_7_jackpot": (7, 153.1, 2, 0, "jackpot"),
    "tan_7_tradewinds": (7, 182.21, 1, 20, None),
    "tan_8_8206": ("cabin", 104, 2, 33, None),
    "tan_8_fwd": (8, 49.3, 1, "table", None),
    "tan_8_aft": (8, 246, 1, "table", None),
    "tan_8_balc_fwd": (8, 100, 1, "out", None),
    "tan_8_balc_aft": (8, 245, 1, "out", None),
    "tan_5_pantry": ("pantry", 190, 1, 22, None),
    "tan_9_balcabin": ("balcabin9", 150, 1, 30, None),
    "tan_9_cart": (9, 172.6, 1, 28, None),
    "tan_9_luggage": (9, 181.5, 1, "table", None),
    "tan_9_fort": ("adjoin", 267, 2, 0, None),
    "tan_9_duct": ("duct", 540, 1, 0, None),
    "tan_9_balc": (9, 240, 1, "out", None),
    "tan_10_mid": (10, 182, 1, "table", None),
    "tan_11_spa": (11, 32, 1, "table", None),
    "tan_11_topsiders": (11, 156.35, 1, 30, None),
    "tan_11_fruit": (11, 176.8, 2, "table", None),
    "tan_11_crates": (11, 217.9, 2, 0, "broken:haz_crates_11"),
    # On the hot tub's canopy: up by a wall jump off one of its posts, from under it.
    "tan_11_canopy": (11, 132.5, 1, 90, None),
    "tan_10_tray": (10, 129.8, 1, 0, "flag:trays_10m"),
    # Region 7: in the ice bucket's tray on deck 8 (the steward's rounds go by it), on deck 9 aft's
    # cart, and on the balcony where Bumbot swiped at the gull.
    "tan_8_mid": (8, 178.32, 1, 3, None),
    "tan_9_aft": (9, 230, 1, 28, None),
    "tan_10_balc": (10, 160.6, 1, "out", None),
    "tan_12_spinnaker": (12, 54, 2, "table", None),
    "tan_12_lady": (12, 127.25, 2, 0, "lady"),
    "tan_12_cagneys": (12, 172.9, 1, 34, None),
    "tan_12_pinata": (12, 210.75, 3, 0, "broken:sec_pinata"),
    "tan_funnel": ("funnel", 189.2, 1, 13, None),
}

# --- Pickups ---------------------------------------------------------------------------------------
# id: (deck or room, m or x, what she gets, needs flag[, px up on a piece already there[, the atlas
# piece it is drawn as]]). `what`: "verb:<name>" a new way to move, "book:<n>", "item:<name>" a pocket
# item. All taken with E (population §2.1, §2.2).
ITEMS = {
    "item_socks": (11, 95.75, "verb:socks", None, 40),
    # Left at the old lady's sunbed when the horn sends her off: her parasol, leaning on it, and her book.
    "item_parasol": (12, 129.62, "verb:parasol", "horn", 0),
    "item_pills": ("smcabin", 172, "item:pills", "bb3", 50),
    "book_1": (5, 85.5, "book:1", None, 23),
    "book_2": ("lifeboat", 112, "book:2", None, 17),
    "book_3": ("dressing", 118, "book:3", None, 31),
    "book_5": ("cabin", 186, "book:5", None, 32),
    "book_8": (12, 128.2, "book:8", "horn", 13),
    "book_10": (10, 37.5, "book:10", None),
}

# --- Bumbot's beats (GAME_DESIGN.md §6.1.8) --------------------------------------------------------
# id: (deck or room, m or x, what he is doing, which way he bolts, where he is gone (m or x), needs).
# Each sets its own flag when he is away. Step 0: his built near-catch, no choreography yet.
BEATS = {
    "bb1": (5, 248.8, "eat", -1, 203, None),
    "bb2": (6, 181.0, "asleep", 1, 193.6, None),
    "bb3": (6, 248.75, "wash", 1, 250.6, None),
    "bb4": ("linen", 150, "asleep", 1, 226, None),
    "bb5": (11, 131.27, "bat", 1, 160, None),
    "bb6": (10, 31, "sit", -1, 29.2, None),
}
# What a flag gives besides itself: a verb learned at a beat.
FLAG_GIVES = {"bb1": ["verb:dash"], "bb4": ["verb:crawl"], "bb5": ["flag:drain"], "bb6": ["flag:alarm"]}
# He lies this many px up (on the towels, on a counter).
BEAT_LIFT = {"bb4": 6, "bb1": "service-station-bg", "bb2": "reading-table-bg"}      # px, or the piece he is on
# The linen room (tools/draw_linen.py): the vent high on its far wall (its middle, and its sill px
# up), the chute's hatch by the door, where the laundry's cart stands under the chute's mouth.
LINEN = dict(vent=220, sill=42, chute=24, cart_top=36, laundry_cart=200)

# --- Things she pushes (the push verb, region 4) ----------------------------------------------------
# id: (deck or room, m or x, how far it rolls (m or x), the atlas piece, flag set when it gets there,
# tall: it fills the doorway until then, the side she pushes from: -1 forward of it[, needs: the
# flag before which it is not hers to push]).
PUSHABLES = {
    "cart_steward": (9, 122.6, 130, "service-cart", "cart_free", True, -1),
    # The linen room's laundry cart: by the wall (she walks past it), pushed under the vent she
    # climbs onto it ("top": only its rim holds her).
    "cart_linen": ("linen", 108, 216, "@linen-cart", "cart_linen", "top", -1, "bb4"),
}

# The trap door in the stage and the tip of the bow (m), where the catch is.
TRAPDOOR_M = 246.3
TRAPDOOR_LANDS = ("galley", 86)     # on the flour sacks
# The stage as built (deck 6, 244-250.67 m): where the rival runs in, the cable he trips on, the fly
# rope Bumbot rides up. (The trap door is TRAPDOOR_M; the swinging light is in LIGHTS.)
STAGE = dict(deck=6, wing=244.3, cable=245.75, rope=249.7)
CATCH_M = 6

# --- Switches: E on a thing sets a flag (step 0's stand-ins for scenes) ----------------------------
# id: (deck or room, m or x, flag, needs, label).
SWITCHES = {
    "sw_cake": (12, 84, "wedding", None, "CAKE"),
}

# --- Wall jumps (GAME_DESIGN.md §6.1.3, region 6) --------------------------------------------------
# Grip surfaces besides the balconies' partitions (which the builder adds): (route, m, deck its foot
# stands on, px up to its foot, px up to its top, side she is on: -1 forward of it, 1 aft, 0 either).
GRIPS = [
    # The atrium's pillars, deck 5's floor to deck 10's walk.
    ("inside", 86, 5, 0, 5 * 144, 0), ("inside", 98, 5, 0, 5 * 144, 0),
    # (The boat walkway's ways up to deck 8's balconies, its end walls and the white columns the
    # boats hang between, are added by the builder from the promenade's layout.)
    # The Great Outdoors' sun cover: its aft post, the climb up to deck 12 (region 8's way in).
    ("inside", 233, 11, 0, 124, 1),
    # The hot tub canopy's two posts (the socks' first use: a tangerine on its roof).
    ("inside", 131.03, 11, 0, 84, 0), ("inside", 133.93, 11, 0, 84, 0),
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
#   behind her), default beside her; cover=[(atlas piece, m, px up)] built furniture drawn again in
#   front of them (a bar's counter, when its back bar must stay behind them); pose: "front" turned
#   to us (at a rail), "back" turned away (reading a wall).
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
    # Region 2, deck 6: the cabins, the Internet Cafe, the atrium walk, Bliss, the shops, the Windjammer.
    "amb_maid": dict(at=("maid6", 150), who="maid", face=1, idle="make"),
    "amb_surfer": dict(at=(6, 67.45), who="surfer", face=1, layer="back"),
    "amb_couple_6_her": dict(at=(6, 84.3), who="atriumwoman", pose="front", layer="back"),
    "amb_couple_6_him": dict(at=(6, 85.2), who="railman", pose="front", layer="back"),
    "amb_dj": dict(at=(6, 121.3), who="dj", face=-1, idle="bob", layer="behind"),
    "amb_photog_2": dict(at=(6, 135.45), who="studio", face=-1, idle="idle", layer="back"),
    "amb_barman_wj": dict(at=(6, 142.6), who="barmaid", face=-1, idle="idle", layer="back",
                          cover=[("bar-counter-bg", 142.6, 0), ("tan-bar-stool-bg", 142.6, 0)]),
    "amb_model_ship": dict(at=(6, 148.3), who="modelguest", face=1, idle="idle", layer="back"),
    # The Library: she stands behind her desk; her bubble while any book is in her pocket.
    "npc_librarian": dict(at=(6, 192.3), who="librarian", face=-1, idle="idle", layer="behind",
                          bubble=("book", "books:held", None, 4)),
    # The promenade: the jogger's loop on the JOGGING lane (she hops him or stands aside, ↑), the
    # rival peering under a boat (a glimpse: the story takes him away).
    "haz_jogger": dict(at=("prom", 150), who="jogger", face=1, walk=(116.5, 211.5, 2.2, "run"), end_ms=400,
                       touch=("scare", 14, 40, "bumped")),
    "riv_prom": dict(at=("prom", 190), who="rival", face=1, idle="idle", after="region:2", until="flag:riv_prom"),
    # Deck 7's lobbies and atrium walk: the carpet fitter on the 7-8 flight's foot, a couple at the plaques.
    "blk_fitter": dict(at=(7, 87.9), who="fitter", face=1, idle="work", until="region:4"),
    "amb_couple_7_her": dict(at=(7, 83.75), who="plaquewoman", pose="back", layer="back"),
    "amb_couple_7_him": dict(at=(7, 84.6), who="plaqueman", pose="back", layer="back"),
    # Region 3, the theatre (deck 6). The stage manager at the curtain; two dancers rehearsing on
    # the stage until Bumbot's beat, sat on the floor in front of it after; the rival where the trap
    # door dropped him, on the galley's flour sacks; three in the stalls.
    "npc_stagemanager": dict(at=(6, 245.0), who="stagemanager", face=1, idle="idle",
                             bubble=("pills", "flag:bb3", "card:ent", 4)),
    "amb_dancer_her": dict(at=(6, 245.9), who="dancer_her", face=1, idle="dance", until="flag:bb3"),
    "amb_dancer_him": dict(at=(6, 247.15), who="dancer_him", face=-1, idle="dance", until="flag:bb3"),
    "amb_dancer_her_sat": dict(at=(6, 241.05), who="dancer_her", face=1, still="sit", after="flag:bb3", layer="back"),
    "amb_dancer_him_sat": dict(at=(6, 241.75), who="dancer_him", face=-1, still="sit", after="flag:bb3", layer="back"),
    "riv_galley": dict(at=("galley", 62), who="rival", face=1, still="sit", after="flag:bb3", until="region:4"),
    "amb_audience_1": dict(at=(6, 212.29), who="aud_gent", face=1, layer="back"),
    # Region 4 (Housekeeping). The steward at his jammed cart (the story moves him with it), the
    # honeymooners at their door, the bedmaker in the cabin being cleaned; strollers on the atrium's
    # walks; the security officer in the laundry, waiting for his uniform.
    "npc_steward": dict(at=(9, 123.4), who="steward", face=-1, idle="tug",
                        bubble=("cart", "!flag:cart_free", None, 4)),
    "npc_bride": dict(at=(9, 135.0), who="bride", face=-1, idle="idle", until="flag:photo",
                      bubble=("camera", None, "flag:photo", 3)),
    "npc_groom": dict(at=(9, 135.75), who="groom", face=-1, idle="idle", until="flag:photo"),
    "amb_bedmaker": dict(at=("cleanup", 166), who="bedmaker", face=1, idle="make"),
    "amb_planman": dict(at=(9, 104.7), who="planman", face=-1, layer="back"),
    "amb_bagslady": dict(at=(8, 86), who="bagslady", face=1, walk=(84.2, 90.4, 0.7), end_ms=1800, layer="back"),
    "amb_domeman": dict(at=(10, 86.6), who="domeman", face=1, idle="idle", layer="back"),
    "riv_laundry": dict(at=("laundry", 124), who="rival_towel", face=1, after="region:4", until="region:6"),
    # Region 5 (deck 8 forward, "calm, hers"): the birthday girl at the door with the balloons.
    "amb_birthday": dict(at=(8, 71.95), who="partygirl", face=-1, idle="dance", layer="back"),
    # Region 6 (Lido, deck 11). The gym's two; the kid with the water pistol, in the hot tub until
    # Bumbot's beat and on the aft pool deck after (the story moves him: src/world/lido.js); the
    # security officer on his knees at a lounger; Topsiders' barman; the painter and the fans on the
    # flights up; her husband at the first table by the ice cream machine; guests at the far tables.
    "amb_treadmill": dict(at=(11, 86.6), who="runner", face=1, idle="run", layer="back", dy=7),
    "amb_weights": dict(at=(11, 99.95), who="lifter", face=-1, idle="curl", layer="back"),
    "npc_kid_tub": dict(at=(11, 132.5), who="kid", face=-1, layer="behind", until="flag:bb5"),
    "npc_kid": dict(at=(11, 146.0), who="kid", face=-1, idle="idle", after="flag:bb5",
                    bubble=("softserve", "!flag:kid_fed", None, 5)),
    "riv_loungers": dict(at=(11, 143.95), who="rival", face=1, idle="peek", layer="back", after="region:6", until="region:8"),
    "amb_barman_top": dict(at=(11, 155.65), who="barman_top", face=-1, idle="shake", layer="behind"),
    "blk_painter": dict(at=(11, 107.95), who="painter", face=-1, idle="paint", until="region:8"),
    "blk_fan_a": dict(at=(11, 199.75), who="fan_a", face=-1, idle="cheer", until="region:8"),
    "blk_fan_b": dict(at=(11, 200.55), who="fan_b", face=-1, idle="cheer", until="region:8"),
    "blk_fan_c": dict(at=(10, 196.45), who="fan_c", face=-1, idle="cheer", until="region:8"),
    "npc_husband": dict(at=(11, 219.52), who="husband", face=1, idle="idle",
                        bubble=("canister", "flag:kid_fed", "flag:table", 5)),
    "amb_go_reader": dict(at=(11, 236.52), who="go_reader", face=1, layer="back"),
    "amb_go_her": dict(at=(11, 240.52), who="go_her", face=1, layer="back"),
    "amb_go_him": dict(at=(11, 241.48), who="go_him", face=-1, layer="back"),
    "amb_audience_2": dict(at=(6, 213.25), who="aud_lady", face=1, layer="back"),
    "amb_audience_3": dict(at=(6, 226.54), who="aud_popcorn", face=1, layer="back"),
    # Region 3, deck 7: Magnum's, the casino, Tradewinds, the Arcade, the Stardust balcony.
    "amb_barman_mag": dict(at=(7, 113.6), who="barman", face=1, idle="idle", layer="back",
                           cover=[("bar-counter-bg", 113.6, 0), ("chrome-stool-bg", 113.6, 0)]),
    "amb_pianist": dict(at=(7, 115.55), who="pianist", face=1, idle="play", layer="back"),
    "amb_croupier": dict(at=(7, 158.0), who="croupier", pose="front", layer="behind"),
    "amb_player_lady": dict(at=(7, 157.29), who="casinolady", face=1, layer="back"),
    "amb_player_cowboy": dict(at=(7, 162.4), who="cowboy", pose="back", layer="back"),
    "amb_shopper": dict(at=(7, 177.4), who="shopper", face=1, idle="idle", layer="back"),
    "amb_teen": dict(at=(7, 188.29), who="teen", pose="back", layer="back"),
    "amb_balcony_1": dict(at=(7, 220.35), who="aud_girl", face=1, layer="back"),
    "amb_balcony_2": dict(at=(7, 232.71), who="aud_granny", face=1, layer="back"),
    # Region 7 (Outside). The guest locked out on his own balcony, deck 10 aft (in his cabin once
    # she has let him in: the story walks him in); the security officer looking into a tender on the
    # boat walkway (a glimpse: the story takes him away); the boat drill's two.
    "npc_balcony_guest": dict(at=("b10", 236.2), who="balcony_guest", face=-1, idle="idle", until="flag:guest",
                              bubble=("door", None, "flag:guest", 5)),
    "npc_guest_in": dict(at=("guest10", 196), who="balcony_guest", face=-1, idle="idle", after="flag:guest"),
    "riv_walkway": dict(at=("walkway", 207.6), who="rival", face=1, idle="peek", after="region:7", until="flag:riv_walkway"),
    "amb_drill_winch": dict(at=("walkway", 184.9), who="drill_winch", face=1, idle="crank", layer="back"),
    "amb_drill_officer": dict(at=("walkway", 192.6), who="drill_officer", face=-1, idle="idle", layer="back"),
    # Region 8 (deck 12 from Champs aft, the funnel). Champs' three at the TVs; the old lady on her
    # sunbed across the sun deck's walk (src/world/topdeck.js: she glares, dozes over her mojito,
    # bolts at the horn); the security officer on his knees at the loungers; the shuffleboard's two;
    # the engineer at the technical ladder's foot, and on the funnel's top once he has had his
    # coffee (by the cord until the horn, reading after); the restaurants' people; the fans in the
    # Sports Bar once they are off the stairs.
    "amb_champs_a": dict(at=(12, 90.3), who="champs_a", pose="back", layer="back"),
    "amb_champs_b": dict(at=(12, 95.1), who="champs_b", pose="back", layer="back"),
    "amb_champs_c": dict(at=(12, 97.88), who="champs_c", face=1, idle="cheer", layer="back"),
    "npc_oldlady": dict(at=(12, 128.5), who="oldlady", face=1, idle="read", until="flag:horn", dy=11,
                        bubble=("cocktail", "!flag:lady", None, 3.4)),
    "riv_sundeck": dict(at=(12, 134.75), who="rival", face=1, idle="peek", until="flag:horn"),
    "amb_shuffle_a": dict(at=(12, 156.05), who="shuffle_a", face=1, idle="push", layer="back"),
    "amb_shuffle_b": dict(at=(12, 159.25), who="shuffle_b", face=-1, idle="idle", layer="back"),
    "npc_engineer": dict(at=(12, 166.2), who="engineer", face=1, idle="idle", until="flag:engineer",
                         bubble=("coffee", None, "flag:engineer", 4)),
    "npc_engineer_cord": dict(at=("funnel", 187.25), who="engineer", face=-1, idle="idle", after="flag:engineer",
                              until="flag:horn", bubble=("horn", None, "flag:horn", 5)),
    "npc_engineer_read": dict(at=("funnel", 188.0), who="engineer", face=-1, idle="reading", after="flag:horn",
                              bubble=("book", "!flag:book9", None, 4)),
    "amb_cagneys_her": dict(at=(12, 169.4), who="cagneys_her", face=1, layer="back"),
    "amb_cagneys_him": dict(at=(12, 170.6), who="cagneys_him", face=-1, layer="back"),
    "amb_sushi_chef": dict(at=(12, 178.0), who="sushi_chef", face=-1, idle="slice", layer="behind"),
    "amb_sushi_a": dict(at=(12, 176.71), who="sushi_a", face=1, layer="back"),
    "amb_sushi_b": dict(at=(12, 179.29), who="sushi_b", face=-1, layer="back"),
    "amb_teppan_chef_a": dict(at=(12, 185.4), who="teppan_chef_a", face=1, idle="idle", layer="behind"),
    "amb_teppan_chef_b": dict(at=(12, 190.4), who="teppan_chef_b", face=-1, idle="idle", layer="behind"),
    "amb_teppan_1": dict(at=(12, 184.88 - 0.17), who="teppan_1", face=1, layer="back"),
    "amb_teppan_2": dict(at=(12, 185.92 + 0.17), who="teppan_2", face=-1, layer="back"),
    "amb_teppan_3": dict(at=(12, 189.88 - 0.17), who="teppan_3", face=1, layer="back"),
    "amb_teppan_4": dict(at=(12, 190.92 + 0.17), who="teppan_4", face=-1, layer="back"),
    "amb_bistro_her": dict(at=(12, 205.88 - 0.1), who="bistro_her", face=1, layer="back"),
    "amb_bistro_him": dict(at=(12, 206.71 + 0.1), who="bistro_him", face=-1, layer="back"),
    "amb_lobos_waiter": dict(at=(12, 209.55), who="lobos_waiter", face=-1, idle="shake", layer="back"),
    "amb_sportsbar_a": dict(at=(11, 205.9), who="fan_a", face=1, idle="cheer", after="region:8", layer="back"),
    "amb_sportsbar_b": dict(at=(11, 206.75), who="fan_b", face=1, idle="cheer", after="region:8", layer="back"),
    "amb_sportsbar_c": dict(at=(11, 208.5), who="fan_c", face=-1, idle="cheer", after="region:8", layer="back"),
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
    # Region 2. The fire-hose cabinet high on the wall (a tangerine on its top), the photo with a
    # black tail leaving the frame (`sec_cat_photo`), the rope stand Bumbot knocked over.
    "prop_hose": (6, 26.94, "hose-cabinet", 91, dict(back=True)),
    "sec_cat_photo": (6, 157.4, "@photo-cat", 72, dict(back=True)),
    "prop_rope_down": (6, 193.1, "@rope-down", 0, dict(after="flag:bb2")),
    # What stands in the way on deck 7's flights up: the carpet's roll, the florist's flowers for
    # the wedding, the auction's crates and a canvas.
    "prop_carpet": (7, 88.75, "carpet-end", 0, dict(until="region:4")),
    "prop_florist_1": (7, 78.4, "flower-vase", 0, dict(until="region:5")),
    "prop_florist_2": (7, 77.95, "rose-vase", 0, dict(until="region:5")),
    "prop_florist_3": (7, 77.45, "flower-vase", 0, dict(until="region:5", flip=True)),
    "prop_auction_1": (7, 106.25, "@crate-big", 0, dict(until="region:4")),
    "prop_auction_2": (7, 105.55, "@crate-big", 0, dict(until="region:4")),
    "prop_auction_3": (7, 104.6, "easel-painting", 0, dict(until="region:4")),
    # Region 3. The microphone's cable the rival trips on; Magnum's piano; the painting of a black
    # cat on an easel (`sec_cat_painting`); the theatre's scenery flats across the aft flight up.
    "prop_cable": (6, 245.75, "@cable", 0, {}),
    "prop_piano_mag": (7, 116.6, "grand-piano-bg", 0, dict(back=True)),
    "sec_cat_painting": (7, 140.0, "@easel-cat", 0, dict(back=True)),
    "prop_flat_1": (7, 198.15, "@flat-palm", 0, dict(until="region:4")),
    "prop_flat_2": (7, 197.3, "@flat-sun", 0, dict(until="region:4")),
    # Region 4. The wet-floor sign under the sprinkler; the "Do Not Disturb" card; the towel animals
    # on their table across the midship flight up from deck 10 (`blk_towels`).
    "prop_wet_9": (9, 146.2, "wet-floor-sign", 0, {}),
    "prop_towels_table": (10, 104.85, "towel-table", 0, dict(until="region:6")),
    "prop_towels_swan": (10, 104.85, "towel-swan", 25, dict(until="region:6")),
    "prop_towels_elephant": (10, 106.3, "thing:towel-elephant", 0, dict(until="region:6")),
    "prop_towels_monkey": (10, 105.6, "thing:towel-monkey", 0, dict(until="region:6")),
    # Region 5. A steward's cart with a towel swan on it; the duct's grille in the ceiling where she
    # drops out (shut until then, hanging open after), and his dusty paw prints from under it to the
    # lobby's door.
    "prop_swan_cart": (8, 29.3, "towel-trolley", 0, {}),
    "prop_swan_cart_swan": (8, 29.3, "towel-swan", 28, {}),
    "prop_grille_shut": (8, 66.1667, "@grille-shut", 120, dict(until="flag:duct", back=True)),
    "prop_grille_open": (8, 66.1667, "@grille-open", 98, dict(after="flag:duct", back=True)),
    "prop_paws_8": (8, 70.05, "@paws", 0, dict(after="flag:duct")),
    "prop_towels_rabbit": (10, 106.95, "thing:towel-rabbit", 0, dict(until="region:6", flip=True)),
    # Region 6. The rack with the yoga mats, the socks on its top; two sunbathers on the loungers by
    # the first pool; that pool's second ladder, at the end where Bumbot fishes; the attendant's hut
    # (a checkpoint); the wet-floor sign by the showers; the painter's bucket; deck 10's wet-floor sign.
    "prop_yoga_rack": (11, 95.75, "yoga-rack", 0, {}),
    "amb_sun_1": (11, 115.9, "thing:sunbather-1", 0, dict(back=True)),
    "amb_sun_2": (11, 117.6, "thing:sunbather-2", 0, dict(back=True)),
    "prop_ladder_aft": (11, 130.5, "pool-ladder-bg", -12, dict(back=True, flip=True)),
    "prop_pool_hut": (11, 140.6, "@pool-hut", 0, dict(back=True)),
    "sign_wet_11": (11, 150.55, "wet-floor-sign-bg", 0, dict(back=True)),
    "prop_paint_bucket": (11, 107.45, "@paint-bucket", 0, dict(until="region:8")),
    "sign_wet_10m": (10, 154.2, "wet-floor-sign", 0, {}),
    "prop_tray_10": (10, 182, "@tray", 12, {}),
    # Region 7's hallways: the wet-floor signs under the sprinklers; an ice bucket and glasses on a
    # tray outside a door (a tangerine in the tray).
    "sign_wet_8m": (8, 146.2, "wet-floor-sign", 0, {}),
    "sign_wet_9a": (9, 216.5, "wet-floor-sign", 0, {}),
    "amb_ice_tray": (8, 178.0, "@tray", 0, {}),
    "amb_ice": (8, 177.82, "ice-bucket", 3, {}),
    "amb_ice_glasses": (8, 178.02, "wine-glasses", 3, {}),
    # The drill's rope across the walkway's inboard side and its sign.
    "prop_drill_rope": ("walkway", 183.2, "rope-barrier", 0, dict(back=True)),
    # Bumbot's paw prints on the balcony where he swiped at the gull (a tangerine on its table).
    "prop_paws_10": ("b10", 161.6, "@paws", 0, {}),
    # Region 8. Two more sunbathers on the sun deck's loungers (the security officer looks under
    # them); the old lady's parasol leaning on her sunbed while she is there (hers to take after).
    "amb_sun_12a": (12, 136.7, "thing:sunbather-3", 0, dict(back=True)),
    "amb_sun_12b": (12, 138.8, "thing:sunbather-4", 0, dict(back=True, flip=True)),
    "prop_lady_parasol": (12, 129.62, "@icon-parasol", 0, dict(until="flag:horn")),
}
# Things standing in the way that she hops: id: (deck, m, atlas piece).
SOLIDS = {
    "haz_cart_4_90": (4, 90, "service-cart"),
    "haz_cart_4_182": (4, 182, "towel-trolley"),
    "haz_cart_4_220": (4, 220, "service-cart"),
    "haz_cart_5_30": (5, 30, "towel-trolley"),
    "haz_cart_9_172": (9, 172.6, "service-cart"),
    "haz_cart_10_118": (10, 118, "towel-trolley"),
    "haz_cart_8_186": (8, 186, "service-cart"),
    "haz_cart_9_230": (9, 230, "towel-trolley"),
    "haz_cart_10_237": (10, 237.7, "service-cart"),
}
# Things the dash goes through: id: (deck or room, m or x, [(atlas piece, dx, dy)]).
BREAKABLES = {
    "haz_luggage_4": (4, 30, [("suitcases", -13, 0), ("suitcases", 14, 0), ("beach-bag", 2, 25)]),
    "haz_crate_galley": ("galley", 36, [("@crate-big", 0, 0)]),
    # Delivered luggage, stacked to the ceiling outside a cabin: no hopping it.
    "haz_luggage_9": (9, 180, [("suitcases", 0, 0), ("suitcases", 3, 25), ("suitcases", -2, 50), ("suitcases", 2, 75),
                               ("suitcases", -1, 100)]),
    # Crates of cones and syrup behind the Great Outdoors' service station.
    "haz_crates_11": (11, 217.9, [("@crate-big", 0, 0), ("@crate-big", 1, 26)]),
    # Los Lobos' pinata (`sec_pinata`), hung on a string at head height across the way (`hang`: px
    # up to its foot): under it on hands and knees, or the dash through it: its tangerines.
    "sec_pinata": (12, 210.75, [("pinata", 0, 40)], dict(hang=40, string=True)),
}
# Quirks (§6.1.11): a moment with no reward. id: (deck or room, m or x, trigger: "E" or "still:<s>",
# her clip, ms it lasts, options: needs).
QUIRKS = {
    "sec_swan": (5, 177.6, "E", "shiver", 1700, {}),
    # (While she dances the disco ball over the floor throws its lights: `glitter` = m, px up.)
    "sec_dance": (6, 117.2, "still:3", "dance", 3200, dict(reach=36, glitter=(119.4, 113))),
    # Centre stage, between the open trap door and the swinging light: she bows to the house.
    "sec_spotlight": (6, 247.3, "still:3", "bow", 2000, dict(reach=14, needs="bb3", face=-1)),
    # The cat's portrait: a double-take.
    "sec_cat_look": (7, 140.0, "still:1.5", "idle-look", 1700, dict(reach=16)),
    # An open cabin, the sea in its window: she looks in.
    "sec_peek_sea": (8, 55.27, "still:2", "idle-look", 1700, dict(reach=14)),
}
# Trays to take: id: (deck or room, m or x, what, after, [(texture, dy)] shown there).
SOURCES = {
    "src_lunch": (5, 248.8, "lunch", "flag:bb1", [("tray", 24), ("load-cloche", 27)]),
    # Region 8's two errands: the engineer's coffee from the Great Outdoors' coffee station (hot for
    # 50 s), the old lady's mojito from Topsiders' bar.
    "src_coffee": (11, 212.42, "coffee", "region:8", [("coffee-cup", 22)], None, "flag:engineer"),
    "src_cocktail": (11, 155.38, "cocktail", "region:8", [("umbrella-cocktail", 30)], None, "flag:lady"),
    # The ice cream mix, on the cold room's shelf: taken once the machine has run empty.
    "item_canister": ("coldroom", 150, "canister", None, [("load-canister", 30)], "flag:kid_fed", "flag:refilled"),
}
# Signs: id: (deck, m, text, style: plate / poster / note, dy px up, options: size, wrap).
SIGNS = {
    "sign_lockdown_1": (4, 56, "SEARCH\nIN PROGRESS", "poster", 56, dict(size=5)),
    "sign_lostcat": (4, 190.6, "LOST:\nCAT", "note", 54, dict(size=4)),
    "sign_name_1": (4, 224.2, "BOSUN", "plate", 52, {}),
    "sign_name_2": (4, 228.2, "PURSER", "plate", 52, {}),
    "sign_name_3": (4, 236.1, "DJ", "plate", 52, {}),
    # The promenade's two lanes, painted on its wall: the track by the rail, the walk by the wall.
    "sign_lane_1": ("prom", 114.2, "JOGGING TRACK\nby the rail", "poster", 58, dict(size=4)),
    "sign_lane_2": ("prom", 119.4, "WALKERS:\nkeep to the wall  ↑", "note", 58, dict(size=4)),
    "sign_lane_3": ("prom", 213.6, "JOGGING TRACK\nby the rail", "poster", 58, dict(size=4)),
    # Region 4: the honeymooners' door.
    "sign_married": (9, 135.6, "JUST MARRIED", "note", 81, dict(size=4)),
    "sign_drill": ("walkway", 183.2, "BOAT DRILL", "poster", 40, dict(size=4)),
}

# --- Region 2's own things (docs/population.md, deck 6) ---------------------------------------------
# The library (GAME_DESIGN.md §6.1.2): the shelf with ten gaps on the wall over the librarian's desk
# (its forward end, m; px up to its board), the return trolley, the red reading chair.
LIBRARY = dict(deck=6, shelf=(190.1, 60), trolley=191.04, chair=166.75)
# The delivery robot (`haz_robot`): id: (deck, from m, to m, m/s). She rides on its top.
ROBOTS = {"haz_robot": (6, 24.6, 60, 0.8)}
# Gulls perched on a rail (`gull_prom`): id: (where, m, px up to the rail's top).
GULLS = {"gull_prom_1": ("prom", 150.5, 31), "gull_prom_2": ("prom", 175, 31), "gull_prom_3": ("prom", 200, 31)}
# Photo slots (population §2.4): id: (where, m or x, px up).
SLOTS = {"slot_lifeboat": ("lifeboat", 184, 85), "slot_lighting": ("lighting", 446, 62),
         "slot_table": (11, 220.0, 36, "flag:table"),
         # On the wall of deck 8's first balcony of all, at the forward end of the row (the plan's
         # `slot_stern`: the stern's terraces are out of sight behind its plating).
         "slot_balcony": ("b8", 74.9, 62)}
# The Photo Studio's flash (`haz_flash`): deck, from m, to m (between its softboxes), every s.
FLASH = (6, 132.45, 134.75, 6)
# The promenade's porthole where two black ears show once (`bb_glimpse_window`): m, px up.
GLIMPSE_WINDOW = (168.3, 72)

# --- Region 3's own things (docs/population.md, decks 6 and 7) --------------------------------------
# Stage lights that swing once their flag is set (`haz_lights`): id: (deck, m, flag, cable px while
# hauled up, cable px let down, swing in degrees, period s). From the ceiling.
LIGHTS = {"haz_light": (6, 249.1, "bb3", 30, 74, 55, 3.2)}
# Slot machines that pay out over the floor (`haz_chips`): id: (deck, m, half the spill's width m).
CHIPS = {"haz_chips_1": (7, 151.9, 0.9), "haz_chips_2": (7, 154.29, 0.9), "haz_chips_3": (7, 166.79, 0.9)}
# The machine with a glint (`sec_jackpot`): id: (deck, m, flag it sets, px up to its glint).
JACKPOTS = {"sec_jackpot": (7, 153.1, "jackpot", 44)}

# --- Region 4's own things (docs/population.md, deck 9: "housekeeping hour") ------------------------
# The robot vacuum that darts out of the cabin being cleaned (`haz_vacuum_9`): id: (deck, m of the
# doorway, how near she comes before it goes (m), how far it darts (m)).
DARTERS = {"haz_vacuum_9": (9, 139.6, 2.0, 2.0)}
# A stack of towels that topples (`haz_towels_9`): id: (deck, m). A jump landed beside it, or the
# dash, brings it down on her.
STACKS = {"haz_towels_9": (9, 141.3)}
# Sprinklers (`haz_sprinkler`): id: (deck, m, half its rain's width (m), every s, for s, offset s).
SPRINKLERS = {"haz_sprinkler_9": (9, 148.0, 1.0, 5, 2, 0), "haz_sprinkler_10m": (10, 156.0, 1.0, 5, 2, 1.5),
              # Region 7: deck 8 midships' one; deck 9 aft's two, out of phase: a rhythm to run.
              "haz_sprinkler_8m": (8, 148.0, 1.0, 5, 2, 0.7),
              "haz_sprinkler_9a": (9, 213.0, 1.0, 5, 2, 0), "haz_sprinkler_9b": (9, 220.0, 1.0, 5, 2, 2.5)}
# A cabin door that flies open (`haz_swing`): id: (deck, m of the door, how near (m), after s, who
# looks out). Takes a cabin door's place.
SWINGDOORS = {"haz_swing_9": (9, 159.6, 3.0, 0.6, "kid"), "haz_swing_10m": (10, 143.6, 3.0, 0.6, "hurry"),
              "haz_swing_8m": (8, 135.6, 3.0, 0.6, "swing_hawaiian"), "haz_swing_8a": (8, 239.6, 3.0, 0.6, "swing_sunhat"),
              "haz_swing_9a": (9, 207.6, 3.0, 0.6, "swing_ring"), "haz_swing_10a": (10, 223.6, 3.0, 0.6, "swing_suit")}
# "Do Not Disturb" doors (`haz_dnd`): id: (deck, m of the door, who is in). E at one: "Startled".
DND = {"haz_dnd_9": (9, 167.6, "spaguest"), "haz_dnd_10m": (10, 131.6, "sleeper"), "haz_dnd_10m2": (10, 171.6, "curlers"),
       "haz_dnd_8m": (8, 127.6, "dnd_shaver"), "haz_dnd_8a1": (8, 211.6, "dnd_facemask"),
       "haz_dnd_8a2": (8, 223.6, "dnd_boxers"), "haz_dnd_10a": (10, 207.6, "dnd_toothbrush")}
# Things she must crawl under or through: id: (deck or room, from, to (m or x), a picture drawn
# in front of her or None).
LOWS = {"haz_fort_9": ("adjoin", 236, 300, "@fort")}
# --- Region 5's own things (docs/population.md, deck 8 forward) --------------------------------------
# Cabin doors standing open, each in a cabin door's place: id: (deck, m, what shows: "party" the
# door with the balloons (`amb_party`), "sea" a made-up cabin with the sea in its window
# (`amb_peek_sea`)).
OPENDOORS = {"amb_party": (8, 72, "party"), "amb_peek_sea": (8, 56, "sea")}

# Where Bumbot shows from the balcony cabin's balcony (`bb_glimpse_balcony`): the deck her balcony
# is on, the cabin's door (m). He sits on the top of its aft partition, and is gone up to the next deck.
GLIMPSE_BALCONY = (9, 151.6)

# --- Region 6's own things (docs/population.md, deck 11 "Lido" and deck 10's hallway under it) -------
# Roofs she can stand on, landing from above: id: (deck, from m, to m, px up).
PLATFORMS = {"plat_canopy": (11, 130.92, 134.03, 90)}
# The pool's beat (`bb5`, src/world/lido.js): the drain lever's housing on the first pool's aft rim,
# the ladder Bumbot comes out by, the hot tub the kid squirts from, the kid's beat on the aft pool
# deck after (from m, to m), the lounger the security officer peers under, the chess set.
LIDO = dict(deck=11, lever=131.68, ladder=130.5, tub=132.5, kid=(142.6, 149.3), lounger=144.6, chess=112.4,
            machine=214.6, husband=219.52, table=220.0, paws=(141.2, 213.6))
# A wet patch she slides on without the socks, a deck chair that slides at her across it
# (`haz_wet`, `haz_deckchair`): id: (deck, from m, to m, where the chair stands (m)).
WETS = {"haz_wet": (11, 150.9, 152.9, 153.35)}
# Gulls that dive at food carried in the open (`gull_pool`, `gull_go`): id: (deck, from m, to m,
# how many, where they wait: "circle" overhead or a perch (m, px up), the flag that keeps them off).
FOODGULLS = {"gull_pool": (11, 140.9, 145.6, 2, "circle", "kid_fed"),
             "gull_go": (11, 210.6, 219.2, 1, (213.9, 46), None)}
# The buffet queue (`haz_queue`): id: (deck, from m, to m, m/s, who). They shuffle toward the
# counter (forward) in threes, solid bodies that shove her back; for crew with a tray they turn aside.
QUEUES = {"haz_queue": (11, 162.5, 181.5, 0.4, ["queue_a", "queue_b", "queue_c", "queue_d", "queue_e", "queue_f"])}
# Room-service trays left on a hallway's floor (`haz_trays`): id: (deck, from m, to m, the "Do Not
# Disturb" door their clatter opens, the flag set by the first clatter). Under two metres: a jump clears them.
TRAYS = {"haz_trays_10m": (10, 128.9, 130.7, "haz_dnd_10m", "trays_10m"),
         "haz_trays_8m": (8, 125.4, 126.8, "haz_dnd_8m", ""),
         # Deck 8 aft, "the breakfast rush": six lots along the hallway, two doors.
         "haz_trays_8a1": (8, 204.9, 206.3, "haz_dnd_8a1", ""), "haz_trays_8a2": (8, 209.4, 210.8, "haz_dnd_8a1", ""),
         "haz_trays_8a3": (8, 212.4, 213.8, "haz_dnd_8a1", ""), "haz_trays_8a4": (8, 216.9, 218.3, "haz_dnd_8a2", ""),
         "haz_trays_8a5": (8, 221.4, 222.8, "haz_dnd_8a2", ""), "haz_trays_8a6": (8, 224.4, 225.8, "haz_dnd_8a2", ""),
         "haz_trays_10a1": (10, 205.4, 206.8, "haz_dnd_10a", ""), "haz_trays_10a2": (10, 208.4, 209.8, "haz_dnd_10a", "")}

# --- Region 7's own things (docs/population.md: the outside; src/world/outside.js) ------------------
# Gusts along the ship's side, on the balconies: every s, for s, the tell before (s: the towels on
# the rails and the laundry flap), px/s aft while she is in the air.
GUSTS = dict(every=7.0, blow=1.5, tell=0.7, drift=60)
# Gulls perched on the balconies' rails (`gull_8`...): id: (deck, m). She lingers within three
# metres for two seconds: its shadow, then a swoop: "Swooped".
PERCH = {"gull_8_1": (8, 120), "gull_8_2": (8, 166), "gull_8_3": (8, 200), "gull_8_4": (8, 240),
         "gull_9_1": (9, 130), "gull_9_2": (9, 170), "gull_9_3": (9, 210),
         "gull_10_1": (10, 150), "gull_10_2": (10, 190), "gull_10_3": (10, 231)}
# Laundry lines (`haz_line`): id: (deck, m): the partition nearest is folded open (a family's two
# balconies made one) and a line of washing hangs across the gap: no vault there, she crawls under.
LINES = {"haz_line_8a": (8, 135), "haz_line_8b": (8, 215), "haz_line_9": (9, 195.7), "haz_line_10a": (10, 125.4),
         "haz_line_10b": (10, 224.4)}
# Balconies with someone on them behind a "Do Not Disturb" sign (`haz_sunbather`): id: (deck, m,
# the picture). Landing on one: "Startled". The way past is by another deck.
OCCUPIED = {"haz_sunbather": (8, 181.4, "thing:balc-sunbather"), "haz_breakfast": (10, 178.8, "thing:balc-breakfast")}
# Checkpoints on balconies, each at an ajar balcony door (a lamp over it): id: the room.
BALCONY_CPS = {"cp_balc_9": "balcabin9", "cp_balc_8m": "balcabin8m", "cp_balc_8a": "balcabin8a",
               "cp_balc_9a": "balcabin9a", "cp_balc_10a": "balcabin10a", "cp_balc_guest": "guest10"}
# The boat drill on the walkway (`haz_drill`): a rescue boat on its falls in the gap between the
# boats, its forward end (m); it hangs high (she walks under it), and every `period` s the crew
# lower it onto the walkway for `down` s: under it as it comes: "Bumped".
DRILL = dict(m=186.0, period=10.0, down=3.0, tell=1.0)
# The steward on his rounds (`haz_steward_rounds`): id: (deck, from m, to m, m/s, the doors he
# pulls his cart into (m), for s, who). Across the hallway he is a body that holds her back.
ROUNDS = {"haz_steward_rounds": (8, 162.0, 182.0, 0.9, [167.6, 175.6], 3.0, "steward_rounds")}

# --- Region 8's own things (docs/population.md: deck 12 from Champs aft, the roof, the funnel;
# src/world/topdeck.js) ------------------------------------------------------------------------------
# The old lady's sunbed across the sun deck's walk (`npc_oldlady`): deck, its middle (m), half its
# width and its height with her on it (px): too wide and high for a tray's hop, a jump clears it.
LADY = dict(deck=12, m=128.5, half=30, tall=36, rival=134.75, card=134.0)
# Basketballs out of the sports court (`haz_balls`): id: (deck, the hoop (m), the way the ball
# bounces: 1 aft, how far (m), every s, offset s). It comes off the rim (the tell), bounces twice
# along the walk and rolls back: "Bonked".
BALLS = {"haz_balls_a": (12, 146.9, 1, 2.2, 4.0, 0.0), "haz_balls_b": (12, 154.4, -1, 2.2, 4.0, 2.0)}
# The court's quirk (`sec_court`): a ball lying at the court's side (m); E: she shoots at the hoop (m).
COURT = dict(deck=12, ball=150.65, hoop=154.4)
# Teppanyaki's flares (`haz_flare`): id: (deck, the grill (m), half the flame's reach (m), every s,
# for s, offset s, the chef whose flourish is the tell). "Singed"; a tray is spilled.
FLARES = {"haz_flare_a": (12, 185.4, 1.25, 6.0, 1.0, 0.0, "amb_teppan_chef_a"),
          "haz_flare_b": (12, 190.4, 1.25, 6.0, 1.0, 3.0, "amb_teppan_chef_b")}
# The aft terrace (`gust_terrace`, `gull_terrace`): gusts over it and the sun cover below (every s,
# for s, the tell, px/s aft in the air), the span they blow over (m), towels on its rail (the tell),
# a gull on the rail.
TERRACE = dict(deck=12, gust=dict(every=7.0, blow=1.5, tell=0.7, drift=60), span=(214.5, 246),
               towels=[(215.85, 24), (217.65, 24)], gull=(220.0, 40))
# The funnel (`gust_funnel`, `gull_funnel`, `sec_horn`, `sec_telescope`): gusts on the roof and the
# stairway (climbing in one she slips back down the flight), two gulls circling (one comes down at
# her every `swoop` s, in a lull); on the top (m): the horn's post and cord, the engineer's toolbox
# with his lunch box, the telescope (it looks at the photo slot `look`).
FUNNEL_TOP = dict(gust=dict(every=5.0, blow=1.2, tell=0.7, drift=60), gulls=2, swoop=10.0,
                  horn=185.0, toolbox=189.2, telescope=192.3, look="slot_balcony")
# Flocks of gulls on the bow until the horn sends them off (`gull_bow_a`, `gull_bow_b`): id: (deck,
# from m, to m, how many, px up: the kids' pool's rims, the Spinnaker balcony's windscreen).
FLOCKS = {"gull_bow_a": (12, 57.75, 63.3, 6, 0), "gull_bow_b": (12, 33.0, 42.5, 6, 96)}
