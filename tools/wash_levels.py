"""How far each background prop is washed toward the corridor wall, place by place (the user, 2026-11-20,
an audit of the background props deck by deck, each place shown in the game at 35%, 20% and 12%).

Every prop of the background has three twins in the ship's atlas (`tools/build_ship_art.py`): `-bg` (35%,
the old level), `-w20` (20%) and `-lt` (12%, the gym's and the theatre's). The map and the world are written
with `-bg`, and `frame()` turns each into the twin of its place: `tools/build_ship_map.py`'s `put()` and
`tools/build_world.py`'s last pass over its things.

**The guest cabin corridors stay at 35%**, as they were ("Those guest cabin corridors remain as they were
before this entire update"): their pictures, extinguishers, exit signs and carts are laid by the game itself
(the ship scene's corridor decoration, `-bg`), never through here. Doors she cannot use and railings keep
35% too (not part of the audit), and the rooms she enters keep their own wash.
"""

# A deck's level, where no place below says otherwise.
DECKS = {3: 20, 4: 20, 5: 20, 6: 20, 7: 20, 8: 35, 9: 35, 10: 20, 11: 20, 12: 20}
# Places with their own level: (deck, from m, to m, level), as tools/ship_layout.py's VENUES has them.
PLACES = [
    (6, 160, 194, 12),      # the Library
    (7, 110, 130, 12),      # Magnum's, the dark wood bar
    (11, 202, 210, 12),     # the Sports Bar, its dark green wall
    (6, 110, 124, 0),       # Bliss, the dark lounge with the DJ: its props in their own colours (the user, 2026-11-26, of 20%, 12%
                            # and their own colours shown in place: "3")
    (5, 150, 168, 0),       # La Cucina in its own colours (the user, 2026-11-26)
    # Cagney's in its own colours (the user, 2026-11-26: "Make all background props in Cagney's their original color
    # tone"), aft of the door at its forward end (164.8 to 165.2 m), which keeps the wash of the props forward of it.
    (12, 165.3, 174, 0),
]
# The balconies outside decks 8 to 10 (the outside route).
BALCONIES = 20
# Pieces with a level of their own wherever they stand: the casino's slot machines, washed less than the casino
# round them (the user, 2026-11-23, with the highlight of what she can use: "too washed out").
PIECES = {"slot-pair": 12}
SUFFIX = {35: "-bg", 20: "-w20", 12: "-lt", 0: ""}
KEEP = ("door", "railing")


def level(deck, m=None, balcony=False):
    if balcony:
        return BALCONIES
    for d, a, b, lv in PLACES:
        if d == deck and m is not None and a <= m < b:
            return lv
    return DECKS.get(deck, 35)


def frame(name, deck, m=None, balcony=False):
    """The twin of a `-bg` piece for its place; anything else as it is."""
    if not isinstance(name, str) or not name.endswith("-bg") or name.startswith(KEEP):
        return name
    base = name[:-3]
    return base + SUFFIX[PIECES.get(base) or level(deck, m, balcony)]


def table(to_x):
    """The levels for the game (the map's `washLevels`; src/highlight.js): what a thing she can use in full colour
    pulses down to, as the props round it are washed. `to_x`: metres to px."""
    return {"decks": DECKS, "places": [[d, to_x(a), to_x(b), lv] for d, a, b, lv in PLACES], "balconies": BALCONIES,
            "default": 35}
