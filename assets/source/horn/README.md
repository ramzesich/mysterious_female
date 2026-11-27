# The horn's scene: its own art (2026-11-27)

The clips of the horn's scene as remade (`docs/horn-remake-log.md`). Cut and built by `tools/build_horn.py`
(run `tools/build_sprites.py`, `tools/build_balconies.py` and `tools/build_heads.py` after it: hers and Bumbot's go
into their sheets).

| Folder | What |
|---|---|
| `starts/` | The built sheets' own frames each clip starts from, on a plain green (Bumbot's on transparency, 64 x 64) |
| `tries/<name>/` | Everything PixelLab returned, frame by frame (`NN.png`), and each frame cut out of its green (`cut-NN.png`) |

## The jobs

All `animate_image_pixminimax`, 8 frames, 1 generation each; 128 x 128 on green but Bumbot's.

| Try | What | Job |
|---|---|---|
| `ears-s17` | from her stand: her hands over her ears, hunched, her knees bent. **Used** (`her-ears`; played back for her hands coming down) | `69567561-d8cd-490f-a5ac-8b6e386bfea7` |
| `ears-s3` | the same, another seed: her hands over her face; not used | `211b4582-3265-48f0-b8fe-d23076b728bd` |
| `start-s4` | the officer from his kneeling frame (`peek`) to his stand, pinned: off his knees into the air, arms out, down onto his feet. **Used** (`start`; the dust strokes under him cut off) | `b29f7ba5-3a9b-4833-8cb6-e84222aebbb9` |
| `hurdle-s4` | the officer from his run's frame (`charge`) back to it, pinned: a leap with his knees tucked. **Used** (`hurdle`; the generator drew a hurdle under him, apart from him: cut off) | `57523f2e-ebc4-42fc-96fc-8cd674dbbc6d` |
| `ladywalk-s5` | the old lady from her `bolt`'s last frame back to it, pinned: quick short steps, her book in her hand. **Used** (`hurry`, a loop of eight, each frame set on its lowest pixel) | `cd691483-13fc-44b5-94f0-81944bc2bb3a` |
| `fright-s3` | Bumbot from his sitting pose: straight up, back arched, tail puffed. **Used** (`bumbot-fright`, each frame on its lowest pixel: the game moves him) | `af8eb8ba-42b6-4a15-8759-d7a609d9017e` |
| `fright-s17` | the same, another seed: he flattens into a blob in the air; not used | `dccab96f-8e83-49a0-8813-a453c9f5c72d` |

7 generations.

## The old lady's bags and towel (`bags/`)

`create_map_object`, 32 x 32 (the duffel 40 x 32), side view, 1 generation each; `<name>.png` as returned,
`<name>-small.png` at the game's size (the scratch try; the game's are built by `tools/build_horn.py`, `BAGS`, into
`assets/ship/horn/lady-*.png`). The user chose set 2 of three sets shown in the running game.

| Candidate | Job | |
|---|---|---|
| `bag-floral` (a canvas bag with a pink flower, a towel in it) | `6b7ff314-43d5-4890-bafd-d088dd94b0b5` | **Used** (`lady-bag`) |
| `handbag-burgundy` | `f3866b2b-ac85-4645-8c61-356b3006496e` | **Used** (`lady-handbag`) |
| `duffel-teal` | `84bac22e-549b-45e9-a7f2-4187c0285e67` | **Used** (`lady-duffel`) |
| `towel-draped` (striped, hung over a rail: the rail cut off) | `0cb82ebc-807e-4fe7-9c52-81d2191ce332` | **Used** (`lady-towel`, over the sunbed's foot) |
| `tote-straw` | `ad4afb18-7561-4673-97fa-70099f49ad07` | not used |
| `towels-stack` (came seen from above) | `0175ec0a-ced3-4bbb-9dad-1fc9116e7deb` | not used |

6 generations; 13 with the clips.
