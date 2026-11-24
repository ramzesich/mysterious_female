# Her reach up out of the water (2026-11-24)

Near-catch 5, at the pool's rim under Bumbot (docs/pool-remake-log.md, decision 29; the user: "she has to look up from
the water and try and reach him, while in the swimming pose. That has to be generated"). Her clip `swim-reach` (nine
frames; the game plays the first five once, `her-swim-reach`, then loops the last five, `her-swim-strain`).

| File | What | Job | Generations |
|---|---|---|---|
| `start.png` | her swim's first frame from her built sheet (`her.png`), on a green none of her colours is near, 96 x 96, her cell at (6, 8) (`place.json`) | made here | |
| `tries/seed4-0..8.png` | `animate_image_pixminimax`, 8 frames, the ground kept: "She stops swimming, lifts her head and looks up, and stretches one arm straight up and forward, high above her head, reaching with an open hand, straining; her other arm stays stretched in front of her on the water; her body and legs stay flat and level, floating in place, seen from the side the whole time." **Used.** | `b5cf9142-0fa2-40f1-b284-da104a087179` | 1 |
| `tries/seed19-0..8.png` | the same, another seed: her arm lower (about 45 degrees), a grey stray shape at the picture's foot from frame 5; not used | `ddff6e92-d998-4828-aea4-e9a6e1e50d24` | 1 |
| `cut.py` | the ground taken out by colour, the spray's flecks dropped, each frame set on her sources' canvas where her swim's frames are | | |
| `0.png` .. `8.png` | the clip's sources, as `tools/build_sprites.py` takes them (set by row 65, her swim's own row) | | |

Checked frame by frame: her first frame is her swim's first to the pixel in the built sheet; her size and colours hold;
one arm up from the shoulder with an open hand, the other on the water, her body flat; 31 and 27 px of spray flecks
dropped from frames 2 and 3. Her head in each frame for the popups: `BY_HAND` in `tools/build_heads.py`.

2 generations.
