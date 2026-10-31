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
EXTENT = {
    3: (4, 256), 4: (2, 257), 5: (2, 257), 6: (3, 257), 7: (5, 251),
    8: (10, 247), 9: (14, 245), 10: (17, 242), 11: (29, 235), 12: (29, 235),
}

# Stair-and-elevator cores, (forward edge, aft edge), on every deck from 3 to 12.
CORES = {"forward": (74, 82), "midship": (92, 100), "aft": (194, 202)}

# The atrium: open from deck 5 up to deck 9, between the forward and midship cores.
ATRIUM = {"span": (82, 92), "decks": (5, 9)}

# Above the top deck.
FUNNEL = (168, 196)
MAST = (54, 62)

# Kinds: "venue" (an indoor public room), "outdoor", "cabins", "crew", "start" (the gangway),
# "finale". A name with "Bumbot:" is one of his near-catch spots (§4).
VENUES = [
    # deck, from, to, name, kind
    (12, 29, 68, "Chapel, kids' pool, Spinnaker Lounge", "venue"),
    (12, 100, 165, "Sports court, shuffleboard, Champs Bar", "outdoor"),
    (12, 165, 194, "Speciality dining, golf nets", "venue"),
    (12, 202, 235, "Le Bistro, Los Lobos", "venue"),

    (11, 29, 74, "Spa and salon", "venue"),
    (11, 82, 92, "Fitness", "venue"),
    (11, 100, 160, "Oasis Pool, Topsiders, hot tubs (Bumbot: fly)", "outdoor"),
    (11, 160, 194, "Garden Café buffet, Ice Cream Bar (Bumbot: fish)", "venue"),
    (11, 202, 235, "Great Outdoors diner (finale)", "finale"),

    (10, 17, 40, "Bridge (Bumbot: controls)", "crew"),
    (10, 40, 74, "Cabins", "cabins"),
    (10, 82, 92, "Cabins", "cabins"),
    (10, 100, 194, "Cabins", "cabins"),
    (10, 202, 242, "Cabins", "cabins"),

    (9, 14, 74, "Cabins", "cabins"),
    (9, 100, 194, "Cabins", "cabins"),
    (9, 202, 245, "Cabins", "cabins"),

    (8, 10, 74, "Cabins", "cabins"),
    (8, 100, 194, "Cabins", "cabins"),
    (8, 202, 247, "Cabins", "cabins"),

    (7, 8, 60, "Kids' and teen clubs", "venue"),
    (7, 100, 150, "Magnum's bar, art gallery", "venue"),
    (7, 150, 194, "Casino, duty-free shops", "venue"),
    (7, 222, 251, "Theatre balcony", "venue"),

    (6, 8, 68, "Cabins, internet café", "cabins"),
    (6, 100, 150, "Bars, shops, photo studio", "venue"),
    (6, 150, 194, "Library, photo gallery; promenade, lifeboats", "outdoor"),
    (6, 206, 256, "Stardust Lounge theatre (Bumbot: washing)", "venue"),

    (5, 4, 74, "Cabins", "cabins"),
    (5, 100, 150, "Shore excursions, reservations", "venue"),
    (5, 150, 194, "La Cucina, Four Seasons, Guest Services", "venue"),
    (5, 205, 256, "Seven Seas dining", "venue"),

    (4, 3, 60, "Cabins", "cabins"),
    (4, 60, 74, "Gangway (start)", "start"),
    (4, 82, 92, "Cabins", "cabins"),
    (4, 100, 194, "Cabins", "cabins"),
    (4, 202, 256, "Cabins", "cabins"),
]
