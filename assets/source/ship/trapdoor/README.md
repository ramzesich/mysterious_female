# The stage's open trap door (2026-11-19)

The user asked what "that black rectangle in the middle" of the stage was (the trap door near-catch 3 leaves open, drawn
in code as a black box and a stick) and chose a generated open trap door.

| File | What | PixelLab |
|---|---|---|
| `src-stage.png` | The game's stage at 1:1 around the trap door (Phaser's snapshot, halved; the trap door's drawing, her and the light hidden), the drop at column 48 | made here |
| `src-context.png` | The stage around it, for the inpaint's context | made here |
| `inpaint-s9.png` (used) | `inpaint_image_pro_flash`, the area x 26-72, y 14-57: the lid up on its hinge, a ladder's top in the opening; it took the mic stand out | `192bf5f3-1097-454d-a05d-2c83e193ac5f` (seed 9, 5 generations) |
| `inpaint-s3-unused.png` | The other try: it redrew the mic stand elsewhere | `72561e2c-f9fe-4ef0-8288-5e50dc95066f` (seed 3, 5) |
| `cut.py` | Its own pixels only (not where the mic stand was taken out), 7 px left onto the drop, the ladder's right rail made its left's (the user); to `assets/ship/trapdoor-open.png`, its column 15 the drop, its last row the stage floor's | |

The game's mic stand moved 0.25 m aft (246.95 m, `tools/build_ship_map.py`), clear of the opening. 10 generations.
