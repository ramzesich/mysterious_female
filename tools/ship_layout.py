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
PROMENADE = {"deck": 6, "span": (102, 226), "enclosed": [(102, 116), (212, 226)],
             "doors": [111, 138, 162, 186]}    # none from the theatre (the user, 2026-11-03)

# Cabin 8206, the user's own cabin on the cruise (2026-11-06): an oceanview with a picture window on
# the starboard side, forward on deck 8, the fourth cabin aft of the Sky Suite (cruisedeckplans.com's
# deck 8 plan, kept in reference/web/deck8/). Its door stands open and she can go in (§5.3).
OUR_CABIN = {"deck": 8, "number": 8206, "m": 41.4}

# The housekeeping linen room on deck 9 (towels heaped on its floor, §5.3): a crew door off the cabin
# corridor, in a cabin door's place, that she can go through (the user, 2026-11-06).
LINEN_ROOM = {"deck": 9, "m": 112}

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
# The mast stands on the Spinnaker Lounge's roof (moved forward from 54-62 m, 2026-11-07: with the kids'
# pool open to the sky there it stood on nothing, the user).
MAST = (46, 54)

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
    ("midships", 125, [4, 5, 6], {}),
    ("theatre", 240, [4, 6], {"one_way": True}),
    ("magnums", 118, [6, 7], {"card": "hotel"}),
]
