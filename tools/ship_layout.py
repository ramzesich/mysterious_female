"""The Norwegian Sun's layout, as the game uses it: where each deck, stair core and venue sits along
the ship, in metres from the bow. The bow is on the left (GAME_DESIGN.md §5.3).

Positions are read off NCL's side profile of the ship (the ship map PDF linked in §5.3): its venue
labels sit in the stretch the venue occupies, so the spans here are approximate, true to the order
and rough size of things rather than to the metre. Edit this list to move things; the schematic
(tools/draw_ship_profile.py) and the map builder read it.
"""

LENGTH = 258  # metres, bow to stern

# Decks from the bottom up. Deck 3 shows below deck 4 but is not playable.
DECKS = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
PLAYABLE = [4, 5, 6, 7, 8, 9, 10, 11, 12]

# How far each deck reaches, (forward end, aft end): the superstructure steps back from the bow,
# and the upper decks end short of the stern in terraces.
# Measured off NCL's profile at each deck's floor (2026-11-03). Decks 3-6 start at the bow's hull
# block (BOW below); deck 7's floor runs out to the stem's tip as the open forecastle.
EXTENT = {
    3: (21.5, 254), 4: (20, 254), 5: (20, 254), 6: (20, 254), 7: (0.5, 254),  # the stern: one straight wall
    8: (21.4, 251.5), 9: (23.6, 249.5), 10: (25, 247), 11: (24, 244), 12: (31, 220),
}
# (Deck 12 ends at 220 m, as on NCL's plan: its restaurants, then a small open terrace looking down
# on the Great Outdoors, open to the sky aft of it (the user, 2026-11-07).)

# The superstructure's front, measured row by row off the profile (2026-11-03): one steady slope
# from deck 7's floor up to the bridge, which stands near-upright on deck 10. Where a deck's own
# floor runs further forward than its front wall (deck 7's forecastle, deck 11's open roof over the
# bridge), the wall's foot is given here; the shell slopes from it up to the deck above.
FRONT_WALL = {7: 18.7, 11: 29.5}

# The bow (§5.3): the raked stem, from its tip at deck 7's floor down past the waterline: one smooth
# convex curve, measured in deck heights off the user's side-view photo (2026-11-03; NCL's diagram
# draws it shorter): `d` decks below deck 7's floor it is `tip + a*d - b*d*d` deck heights aft of
# the tip, shallow under the forecastle (about 30 degrees below level), steepening to about 60 at
# the waterline, 6 decks down and 7.3 back. Between it and `block` the hull is drawn from outside:
# white plating, painted with the ship's sun.
BOW = {"stem": {7: 0.5}, "rake": (2.15, 0.115), "block": 20}   # longer still (the user, 2026-11-03)
# The hull forward of this is plain white plating, the livery on it, no windows (the user's photos).
HULL_PLAIN_TO = 30

# Stair-and-elevator cores, (forward edge, aft edge), on every deck from 3 to 12. The midship core
# stands 10 m further aft than on the profile, to give the atrium room (below).
CORES = {"forward": (74, 82), "midship": (102, 110), "aft": (194, 202)}

# The atrium, open from its floor on deck 5 up through deck 10, between the forward and midship
# cores, crossed by side walks (§5.3). The profile draws it about 10 m long; the game makes it 20 m,
# two screens wide, the user's choice (2026-11-02): at 10 m it looked narrow next to its height.
# Deck 10 is open over it as on the real ship (the user, 2026-11-06; it had cabins over a dome under
# deck 10). The glass elevator's column runs up to deck 10 with it (the user); the curving staircase
# still runs from deck 5 to deck 9.
ATRIUM = {"span": (82, 102), "decks": (5, 10), "lift": (5, 10), "stairs": (5, 9)}

# Deck 6's promenade (§5.3, decided 2026-11-03): outside the rooms, along the ship's side, two
# decks tall with the lifeboats hanging high over it. Its fore and aft ends are enclosed by a wall
# with large glassless openings; the open middle has a railing and the boats. She switches between
# the rooms and the promenade through the doors (metres from the bow, each on both sides).
PROMENADE = {"deck": 6, "span": (100, 231), "enclosed": [(100, 116), (212, 231)],
             "doors": [111, 138, 162, 186],    # none from the theatre (the user, 2026-11-03)
             # Its boats and white columns as in the user's side photo (2026-11-07): where each boat's
             # bow is (m) and what it is (clear of the recess's ends); the columns between them. Its
             # opening, 100-231 m, too.
             "boats": [(100.8, "lifeboat"), (113.0, "rescue-boat"), (143.0, "lifeboat"), (155.6, "lifeboat"),
                       (166.6, "lifeboat"), (199.3, "tender"), (209.9, "tender"), (220.4, "lifeboat")],
             "columns": [112.2, 122.8, 131.4, 142.3, 155.1, 178.9, 183.9, 196.0, 209.5, 220.1],
             # Its back wall (the photo): round portholes on deck 6, a glazed bay two decks tall.
             "portholes": [105.5, 156.0, 158.2, 168.3, 193.6, 200.9, 203.3],
             "glazed": [(123.4, 131.0)]}

# Cabin 8206, the user's own cabin on the cruise (2026-11-06): an oceanview with a picture window on
# the starboard side, forward on deck 8, the fourth cabin aft of the Sky Suite (cruisedeckplans.com's
# deck 8 plan, kept in reference/web/deck8/). Its door stands open and she can go in (§5.3).
OUR_CABIN = {"deck": 8, "number": 8206, "m": 41.4}

# The housekeeping linen room on deck 9 (towels heaped on its floor, §5.3): a crew door off the cabin
# corridor, in a cabin door's place, that she can go through (the user, 2026-11-06); the Housekeeping
# card opens it (§6.1.5).
LINEN_ROOM = {"deck": 9, "m": 112, "lock": ("card", "hk", 0)}

# The Chapel on deck 12 (the user's photo, 2026-11-07): off the forward lobby, behind its door, shown
# in the deck's place like the linen room; the door at `m`.
CHAPEL = {"deck": 12, "m": 68.6}

# The bridge's back wall on deck 10, across the deck where the bridge ends and the cabins begin, a
# crew door in it (the user, 2026-11-06); the Captain's card is to lock it later (§6.2).
BRIDGE_WALL_M = 40

# The spa's wall on deck 11, between it and the forward lobby, a door in it, as the bridge's (the
# user, 2026-11-06).
SPA_WALL_M = 74

# The Stardust Lounge's stage, deck 6, from here to the stern wall; over it deck 7's balcony ends in a
# railing, the stage's fly space open below (the user: she can hop over and drop onto the stage).
STAGE = 244

# Above the top deck.
FUNNEL = (168, 196)
# The antenna mast stands on the roof over the forward lobby (the user, 2026-11-07; it stood on the
# Spinnaker Lounge's roof, where the real ship's angled radar mast is now drawn).
MAST = (71, 79)
RADAR_MAST = 46.5     # the angled radar mast's foot, forward end (m), on the Spinnaker Lounge's roof

# Kinds: "venue" (an indoor public room), "outdoor", "cabins", "crew", "start" (the gangway),
# "terrace" (an open deck that is a place of its own: the Great Outdoors' tables). (Bumbot's spots were
# marked in the names; all taken out on 2026-11-07, to be mapped in again later: §4.)
VENUES = [
    # deck, from, to, name, kind
    # Deck 12, after NCL's plan and cruisedeckplans.com's (2026-11-07): the Spinnaker Lounge forward,
    # the kids' pool outside it, the Chapel off the forward lobby, Champs Bar, the open deck over the
    # pools, the sports court, shuffleboard and golf nets, the speciality restaurants, Le Bistro and
    # Los Lobos, and a terrace over the Great Outdoors.
    # The Spinnaker's balcony: the curved open deck in front of the lounge, out to deck 12's front,
    # through doors at the lounge's front corners (NCL's plan; the user, 2026-11-07).
    # (The kids' pool and the Chapel's lobby made wider, the lounge a little shorter: the user,
    # 2026-11-07, they looked cramped.)
    (12, 31, 44, "Spinnaker balcony", "outdoor"),
    (12, 44, 57.5, "Spinnaker Lounge", "venue"),
    (12, 57.5, 67, "Kids' pool", "outdoor"),
    (12, 67, 74, "Chapel lobby", "venue"),
    (12, 82, 102, "Champs Bar", "venue"),
    (12, 110, 146, "Sun deck", "outdoor"),
    (12, 146, 164, "Sports court, shuffleboard, golf nets", "outdoor"),
    (12, 164, 174, "Cagney's Steakhouse", "venue"),
    (12, 174, 182, "Sushi Bar", "venue"),
    (12, 182, 194, "Teppanyaki", "venue"),
    (12, 202, 208, "Le Bistro", "venue"),
    (12, 208, 214, "Los Lobos Cantina", "venue"),
    (12, 214, 220, "Aft terrace", "outdoor"),

    # The spa, after NCL's plan (2026-11-06): its reception, the massage and sauna rooms, the salon,
    # the aerobics studio, opening one into the next.
    (11, 29, 40, "Spa reception", "venue"),
    (11, 40, 55, "Massage and sauna", "venue"),
    (11, 55, 65, "Salon", "venue"),
    (11, 65, 74, "Aerobics", "venue"),
    (11, 82, 102, "Fitness", "venue"),
    (11, 110, 160, "Oasis Pool, Topsiders, hot tubs", "outdoor"),
    (11, 160, 194, "Garden Café buffet, Ice Cream Bar", "venue"),
    (11, 202, 210, "Sports Bar", "venue"),
    (11, 210, 244, "Great Outdoors", "terrace"),

    (10, 25, 40, "Bridge", "crew"),
    (10, 40, 74, "Cabins", "cabins"),
    (10, 110, 194, "Cabins", "cabins"),
    (10, 202, 247, "Cabins", "cabins"),

    (9, 23.6, 74, "Cabins", "cabins"),
    (9, 110, 194, "Cabins", "cabins"),
    (9, 202, 249.5, "Cabins", "cabins"),

    (8, 21.4, 74, "Cabins", "cabins"),
    (8, 110, 194, "Cabins", "cabins"),
    (8, 202, 251.5, "Cabins", "cabins"),

    (7, 0.5, 21.4, "Mooring deck", "outdoor"),
    # Deck 7 as on NCL's plan (2026-11-03): the youth and teen clubs forward, Magnum's and the Art
    # Gallery amidships, the casino, duty-free and arcade aft, the theatre's balcony at the stern.
    (7, 21.4, 45, "Splash Academy", "venue"),
    (7, 45, 74, "Entourage", "venue"),
    (7, 110, 130, "Magnum's", "venue"),
    (7, 130, 150, "Art Gallery", "venue"),
    (7, 150, 172, "Sun Club Casino", "venue"),
    (7, 172, 186, "Tradewinds", "venue"),
    (7, 186, 194, "Arcade", "venue"),
    (7, 202, 254, "Stardust Lounge balcony", "venue"),

    (6, 20, 64, "Cabins", "cabins"),
    (6, 64, 74, "Internet Café", "venue"),
    # Midships and aft as on NCL's plan (2026-11-03): Bliss, the shops and photo studio, the
    # Windjammer; then the Photo Gallery beside it (the user's photo) and the Library.
    (6, 110, 124, "Bliss Ultra Lounge", "venue"),
    (6, 124, 136, "Gift Shops, Perspectives Photo Studio", "venue"),
    (6, 136, 150, "Windjammer Bar", "venue"),
    (6, 150, 160, "Photo Gallery", "venue"),
    (6, 160, 194, "Library", "venue"),
    (6, 202, 255, "Stardust Lounge theatre", "venue"),

    (5, 20, 74, "Cabins", "cabins"),
    (5, 110, 150, "Shore excursions, reservations", "venue"),
    (5, 150, 168, "La Cucina", "venue"),
    (5, 168, 194, "Four Seasons", "venue"),
    (5, 202, 255, "Seven Seas", "venue"),

    (4, 20, 60, "Cabins", "cabins"),
    (4, 60, 74, "Gangway (start)", "start"),
    (4, 82, 102, "Cabins", "cabins"),
    (4, 110, 194, "Cabins", "cabins"),
    (4, 202, 255, "Cabins", "cabins"),
]

# Escape trunks (§5.1): crew doors onto a vertical ladder shaft. Each is (name, metres from the
# bow, the decks with a door, options): "one_way" opens from the top door only until she has come
# down through it once; "card" is the key card the doors need. For now, test trunks for the
# blockout; the real ones are placed when the interiors are filled.
TRUNKS = [
    ("fwd-cabins", 50, [4, 5], {}),
    ("midships", 125, [4, 5, 6], {"card": "deck"}),      # the crew way up into region 2 (§6.1.4)
    ("theatre", 240, [4, 6], {"one_way": True}),
    # The Bliss/Magnum's trunk, up to deck 9 beside the linen room (no door on deck 8): the way into
    # region 4 (§6.1.3).
    ("magnums", 118, [6, 7, 9], {"card": "ent"}),
]

# --- Progression (GAME_DESIGN.md §6.1; every lock in docs/population.md §2.6) -------------------
# Built step by step (docs/build-plan.md); step 0 is the skeleton: the locks, with plain pickups and
# triggers standing in for the people and scenes that will open them.

# The four department cards: id, colour on the readers and the HUD (§6.1.5).
CARDS = {"deck": "blue", "ent": "red", "hk": "green", "off": "gold"}

# The regions (§6.1.3), each as boxes (deck, from m, to m, route): she opens a region the first time
# she stands in one of its boxes. Blocks lift and elevators light their landings by these; the route
# is the game's ("inside", or "promenade" for deck 6's outside). Region 7's outside and the roof come
# with their ways (step 0's second round).
REGIONS = {
    1: [(4, 0, 258, "inside"), (5, 0, 258, "inside")],
    2: [(6, 0, 194, "inside"), (6, 100, 231, "promenade"), (7, 74, 110, "inside"),
        (7, 100, 231, "promenade")],                      # the boat walkway, up the lifeboat station's ladder
    3: [(6, 194, 258, "inside"), (7, 110, 258, "inside")],
    4: [(8, 82, 110, "inside"), (9, 82, 194, "inside"), (10, 82, 110, "inside"),
        (8, 194, 202, "inside"), (9, 194, 202, "inside"), (10, 194, 202, "inside")],
    5: [(8, 0, 82, "inside"), (9, 74, 82, "inside"), (10, 74, 82, "inside")],
    6: [(11, 74, 258, "inside"), (10, 110, 194, "inside")],
    7: [(8, 110, 194, "inside"), (8, 202, 258, "inside"), (9, 202, 258, "inside"), (10, 202, 258, "inside"),
        (8, 0, 258, "promenade"), (9, 0, 258, "promenade"), (10, 0, 258, "promenade")],   # the balconies
    8: [(12, 82, 258, "inside")],
    9: [(12, 0, 82, "inside"), (11, 29, 74, "inside"), (10, 25, 74, "inside"), (9, 0, 74, "inside"),
        (7, 21.4, 74, "inside")],
    10: [(11, 0, 29, "inside"), (7, 0, 21.4, "inside")],
}

# The stair cores' flights (§6.1.4), by core and the deck each climbs to: ("block", id) a person or
# thing across the flight with a rope and a sign, both ways, until BLOCKS lifts it. Flights not listed
# are open. Public stairs are never locked with a card (the user, 2026-11-11: a fire door can't appear
# on a public staircase, and an escape route never locks); cards open crew ways only.
FLIGHT_LOCKS = {
    ("forward", 6): ("block", "search"), ("forward", 8): ("block", "florist"), ("forward", 12): ("block", "wedding"),
    ("midship", 6): ("block", "cleaner"), ("midship", 8): ("block", "auction"),
    ("midship", 11): ("block", "towels"), ("midship", 12): ("block", "paint"),
    ("aft", 6): ("block", "rehearsal"), ("aft", 8): ("block", "scenery"),
    ("aft", 11): ("block", "fans"), ("aft", 12): ("block", "fans"),
    ("atrium", 6): ("block", "photographer"), ("atrium", 8): ("block", "carpet"),
}

# The blocks (population §2.6): what stands there, its sign, and what lifts it for good: ("region", n)
# once region n opens, or ("flag", name) once that has happened.
BLOCKS = {
    "search": ("The security officer's rope", "SEARCH IN PROGRESS", ("region", 2)),
    "florist": ("The florist's buckets of flowers for the wedding", "DELIVERY", ("region", 5)),
    "auction": ("The Art Gallery's auction crates", "ART AUCTION", ("region", 4)),
    "scenery": ("The theatre's scenery flats", "SCENERY MOVE", ("region", 4)),
    "magnums": ("A rope at Magnum's door", "CLOSED", ("region", 3)),
    "spa": ("A rope at the spa's door", "CLOSED", ("region", 9)),
    "cleaner": ("The cleaner mopping", "WET FLOOR", ("region", 3)),
    "rehearsal": ("A rope", "REHEARSAL IN PROGRESS", ("region", 3)),
    "photographer": ("The photographer's backdrop", "PHOTO SESSION", ("region", 3)),
    "carpet": ("A roll of carpet, the fitter", "CARPET WORKS", ("region", 4)),
    "towels": ("A table of towel animals", "PLEASE DO NOT TOUCH", ("region", 6)),
    "paint": ("The painter, cones", "WET PAINT", ("region", 8)),
    "fans": ("Three fans with drinks", "BIG GAME", ("region", 8)),
    "wedding": ("The wedding party", "PRIVATE EVENT", ("flag", "wedding")),
}

# The doors that lock, by (deck, metres) of their wall: ("card", id, free side) a reader on a crew
# door, the free side -1 (bow) or 1 (stern) opening without the card, 0 none; ("oneway", free side) a
# fire-exit door, its push bar on one side only, shut from the other until she has come through;
# ("flag", name) shut until that has happened; ("block", id, side) a rope across the doorway on that
# side. The spa's and the bridge's doors are keyed by their walls.
DOOR_LOCKS = {
    (6, 194): ("flag", "bb2"),                       # the Library's aft door, the rope until Bumbot
    (7, 110): ("block", "magnums", -1),              # Magnum's, closed until region 3
    (7, 74): ("card", "off", -1),                    # the kids' club's staff door from the forward lobby
    (8, 74): ("oneway", -1),                         # deck 8's forward corridor into its lobby
    # Open from the lobby only, or region 4's atrium walk on deck 8 would lead to the forward stairs and
    # up to deck 11, past region 5 (approved by the user, 2026-11-11).
    (8, 82): ("oneway", -1),
    (9, 74): ("card", "off", -1), (9, 82): ("card", "off", 0),      # the officers' lobbies
    (10, 74): ("card", "off", -1), (10, 82): ("card", "off", 0),
    (11, 74): ("block", "spa", 1),                   # the spa, closed until region 9
    (10, 40): ("card", "off", -1),                   # the bridge
    (8, 110): ("oneway", 1), (8, 194): ("oneway", -1), (8, 202): ("oneway", 1),
    (9, 202): ("oneway", 1),
    (10, 110): ("oneway", 1), (10, 194): ("oneway", -1), (10, 202): ("oneway", 1),
    (12, 82): ("block", "wedding", 1),               # Champs into the forward lobby (the rope on Champs' side)
}
# The walls she passes straight through at a deck's end (no door drawn, §5.3), by deck and end, locked
# the same way: the aft terraces' (region 7's hallways open from inside), deck 7's front onto the
# mooring deck (opened after the catch), and deck 11's front, the spa's onto the balcony forward of
# it (§6.1.9: the bridge's hatch is the only way out there; back in from the balcony only).
END_WALL_LOCKS = {
    (8, "aft"): ("oneway", -1), (9, "aft"): ("oneway", -1), (10, "aft"): ("oneway", -1),
    (7, "fore"): ("flag", "catch"), (11, "fore"): ("oneway", -1),
}

# Step 0's stand-ins (docs/build-plan.md): the cards lie where their givers will be; standing in a
# trigger sets its flag where a scene will. (deck, m, needs flag or None).
# (The Officer's card lies on the sun deck where the security officer dropped it at the horn.)
CARD_SPOTS = {"off": (12, 134, "horn")}
TRIGGERS = []       # (flag, deck, m, needs): none left; Bumbot's beats are in tools/population.py
