# The shaft's art: sources and jobs

The ventilation shaft from the linen room to deck 8 forward (docs/shaft-remake-log.md). Built by
`python tools/build_shaft.py --mouth` into `assets/ship/shaft/`.

## How it was made

1. `python tools/build_shaft.py --roughs` draws the whole shaft flat (`rough/strip.png`) and cuts the pieces to
   redraw: `rough/run.png` (256 x 56, plain lengths), `grille.png` (96 x 56, a length with a floor grille),
   `end.png` (116 x 56, the dead end and the way out), `entry.png` (the mouth, the wall, the slope, the first
   length).
2. Each was redrawn by PixelLab's `edit_image_pro_flash` into `gen/` under the same name ("Redraw this same
   picture as detailed, polished pixel art, keeping every shape exactly where it is: the inside of a ...
   galvanized sheet-metal ventilation duct seen in cut-away from the side, flat with no perspective ...").
3. `python assets/source/shaft/mouth_inputs.py` draws the linen room's forward corner with the mouth in flat, in
   three states (`rough/mouth-*.png`); each redrawn the same way into `gen/mouth-*.png` ("Keep this whole picture
   exactly as it is ... redraw only the grey box on the left wall ...").
4. `python tools/build_shaft.py --mouth` lays the lengths along the run, lights them, and cuts the room's pieces
   (the duct's end from the open picture in every state, the cover from the shut one, the fallen cover from
   `mouth-down2.png`); the exit's grille is the cover's own pixels turned.

`gen/entry.png` is 168 px wide: it was made when the mouth stood 4 px further into the room (30 px, now 26, clear
of the rack's upright); the build cuts it at the mouth's end, so it was not made again.

## Jobs (PixelLab, 2026-11-23)

| Picture | Tool | Job | Generations |
|---|---|---|---|
| `gen/run-a.png` (seed 3) | edit_image_pro_flash | `cb0c5c75-f01b-4829-ad61-54f3278ff0ad` | 9 |
| `gen/run-b.png` (seed 21, "a small cobweb") | edit_image_pro_flash | `0f522866-cbe2-49dc-8dd2-e8de078571b8` | 9 |
| `gen/run-c.png` (seed 42, "a rust streak", "paw prints in the dust") | edit_image_pro_flash | `3c686fdb-1a76-4045-910d-ae1552d6d49c` | 9 |
| `gen/grille-a.png` (seed 7) | edit_image_pro_flash | `60085bb9-5928-45ab-a331-c3cbeb511b4f` | 5 |
| `gen/grille-b.png` (seed 19) | edit_image_pro_flash | `f03232b4-cc69-4743-8e4b-7e6e430cc62b` | 5 |
| `gen/end.png` (seed 5) | edit_image_pro_flash | `5ec36a2c-707e-49a1-9cca-1144e845586c` | 6 |
| `gen/entry.png` (seed 9) | edit_image_pro_flash | `98ea1208-57f3-4e5c-b955-65a29ad1d1f2` | 6 |
| `gen/mouth-shut.png` (seed 4) | edit_image_pro_flash | `52c66b6e-4cfd-437a-b342-3f23f3aa16d2` | 5 |
| `gen/mouth-open.png` (seed 4) | edit_image_pro_flash | `d71ce4bd-6c20-46d3-95a0-6922b8b7fe4c` | 5 |
| `gen/mouth-down.png` (seed 4; its fallen cover came 22 px tall, too small: not used) | edit_image_pro_flash | `2e619eb8-ba87-426e-ae72-0a1e1e37292c` | 5 |
| `gen/mouth-down2.png` (seed 12, "exactly as tall as the duct's open end": used for the fallen cover) | edit_image_pro_flash | `719e43ca-1c4a-42b4-999a-95fae535aeb6` | 5 |

## Tries (`tries/`)

| Picture | What | Job | Generations |
|---|---|---|---|
| `run-rough-first.png` | the first flat drawing of a length | | |
| `run-pixflux-250.png`, `-120.png`, `-60.png` | `create_image_pixflux` from a flat drawing at three strengths: 250 and 120 gave the flat drawing back, 60 lost its shapes | `5bc9b867-18d3-4365-bbd4-2cff45584143`, `7edcb925-1f2f-41c3-8991-245aa58522c9`, `62b5ee71-900f-4bb8-948b-2ba13a4eec44` | 3 |
| `run-edit-seed3.png` | the first `edit_image_pro_flash` of the flat drawing: the look that was kept | `811adb95-17c7-4dfb-9f5d-28baa9acd285` | 9 |
| `run-text-seed5.png` | `create_image_pro_flash` from words alone: heavy outlines, a girder look, a hint of perspective: not used | `606b6996-591b-4cd7-b5db-9ed536b572f0` | 9 |

Her slide down the slope has its own folder: `assets/source/her/shaft-slide/` (2 generations).

**All of it: 92 generations.**
