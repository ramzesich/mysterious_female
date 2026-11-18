# The one-way doors' push bar (2026-11-18)

The design's "fire-exit doors with a push bar on one side only are the one-way doors" (GAME_DESIGN.md
§6.1.2), built (docs/plan-three-uses.md, step 4a's second revision). All `inpaint_image_pro_flash`
(5 generations each, 20 in all): only a band of the game's own picture redrawn, every other pixel
returned as it was, so the one-way and the free doors stay one pair.

| File | What | PixelLab |
|---|---|---|
| `leaf.py` | The open glass leaf exactly as `buildBulkhead` draws it (`leaf-free.png`), and without its handle (`leaf-plain.png`, the source) | made here |
| `raw/steel.png` | **Chosen:** a plain steel push bar across the leaf at her hip (rows 38 to 45: 32 to 39 px over the floor) | `81d85279-7925-4392-8466-6d9af90f5785` |
| `raw/red.png` | Not used: steel with a red band | `ae9ceab3-7ed9-4e6c-9ded-31d3aa460746` |
| `edge.py` | The shut door seen edge on as the game draws it (`edge-plain.png`, the source; `edge-twoway.png` with the free door's handle) and the masks on its free side | made here |
| `raw/edge-closer.png` | **Chosen** (the user: "the door profile should also differ from a two-way glass door"): the bar's end and a door closer at the top on the free side | `c8215f81-0942-4483-9368-2f8681477177` |
| `raw/edge-bar.png` | Not used: the bar's end only | `a7bf32af-5230-4d37-bdac-3d35e53eb36c` |
| `snap.py` | What each inpainting changed, snapped to the palette (`leaf-*.png`, `edge-*.png`) | |
| `build.py` | To the game: `assets/ship/door-glass-pushbar.png` (the open leaf, 28 x 74, its glass see-through as the game draws a free door's) and `assets/ship/door-glass-oneway-edge.png` (shut, 12 x 74, the slab in columns 8 to 11; mirrored by the game for a door free from the stern) | |
