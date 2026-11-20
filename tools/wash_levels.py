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
]
# The balconies outside decks 8 to 10 (the outside route).
BALCONIES = 20
SUFFIX = {35: "-bg", 20: "-w20", 12: "-lt"}
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
    return name[:-3] + SUFFIX[level(deck, m, balcony)]
