# The drill's winch and its crewman, one picture (the user, 2026-11-21)

"Replace him and the valve with a single generated animation of a worker turning the valve": the old crewman
(`assets/source/people/drill_winch/`, cast `drill_winch`, no longer placed) and the winch thing replaced by one picture
of the two, then a clip of him turning its handwheel. Built by `tools/build_drill.py` into `assets/sprites/drill.png`;
played by `DrillBoat` (`src/world/outside.js`): forward while the boat is lowered, backward while it is hoisted, still
otherwise. Its wire rope up to the ceiling leaves the drum at (66, 56) (`ROPE_X`, `ROPE_Y`).

| File / folder | What | PixelLab job |
|---|---|---|
| `start-edit.png` | His standing frame in a 96 px canvas, his feet on its bottom row, room for the winch ahead of him | |
| `try1.png` | `edit_image_pro_flash`: a red valve handwheel on a slim grey pedestal | 1186f129-65c9-4688-b115-737439a8d630 |
| `try2.png` | **Used** (the user's choice): a red handwheel on the side of a grey winch drum, its cable wound on it | 16e367d5-ad95-4775-82d7-8606b4151f72 |
| `turn-a/` | PixMiniMax from `try2.png` to itself, 8 frames: small hand moves | f6e2c58c-f843-41c3-9673-0aadee83a895 |
| `turn-b/` | **Used**: his near hand right round the rim, top to bottom, the spokes turning | 71680661-19f9-494c-bf0b-3c042dbe386f |

12 generations.
