# The promenade's wall lights (deck 6; §4 2.1, thing 4's lamp)

The user, 2026-11-20: "a gull on a lamp" needed a lamp; the first two tries were lanterns no cruise ship has
("Neither of such lamps are on cruise ships"), then four real promenade fittings were generated and the user
chose **3 and 4**, at size **B** (a little bigger than life), "a few along the promenade, with our gull sitting
on top of one of them". Each a PixelLab map object, side view, 1 generation.

| File | What | PixelLab id | Kept? |
|---|---|---|---|
| `cand-3.png` | A round caged bulkhead light with a small rain hood | 5150f2b1-cc9d-46a5-aff8-8b1869ad46cf | **Yes**: `../lamp-round.png`, 20 x 23 in the game |
| `cand-4.png` | An oval ribbed bulkhead light with a visor | 28cedc08-1e81-4b81-a278-4523efbdc9f5 | **Yes**: `../lamp-oval.png`, 29 x 17 |
| `cand-1.png` | A floodlight on a wall frame | ada94010-d1db-4ddf-88d8-58db8abc629c | No |
| `cand-2.png` | A floodlight on an arm | 04c02b7b-5f53-4344-8f20-82a702f4b7b5 | No |
| `try-a.png` | A brass lantern on a stub | 54972a01-2693-4379-afb8-bd09769d041d | No (not a ship's) |
| `try-b.png` | A black lantern on a bracket | 9378ca0c-4d0b-4c5a-b5f2-12a354ab1763 | No (not a ship's) |

`game-3.png`, `game-4.png`: the approved game-size pictures (majority shrink); `tools/build_things.py` builds the
same from `../lamp-round.png`, `../lamp-oval.png` (`SCALE` 23 and 17, `BY_MAJORITY`), pixel for pixel. Ten along
the promenade (`prop_lamp_prom_*` in `tools/population.py`), round and oval in turn, their middles 80 px up,
clear of the doors, portholes, window wall, columns and the plating's butts (149.6, not 149: on a butt).
