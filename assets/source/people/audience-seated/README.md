# The theatre's audience, all in the one seat (2026-11-19)

The user: the theatre's props "washed out too much", the half-turned seats out for "empty chairs like the one that the
guy sits on"; then "Make all of the people in the theatre sit on the same exact chair ... Fill much more chairs with
people, randomly. Make them slightly washed"; and "behind the right (closest to the screen) chair arm, but obscure the
left (far) part of the chair". All `edit_image_pro_flash`, 80 x 80 (the people sheet's cell, the game's size).

| File | What | PixelLab |
|---|---|---|
| `../../ship/theatre-seat-side/frame_0.png` (`edit-s4.png`) | The empty seat: aud_popcorn's game picture, him taken out | `7b4bf611-153f-4bef-ac24-635016b452a3` (5) |
| `cell-<name>.png` | The five named as the people sheet had them, each in his or her own chair | the sheet |
| `nochair-aud_popcorn.png` | Him without his chair, the same pose | `2f1a313c-4b2e-4916-84fb-5688d5533ba8` (5) |
| `nochair-aud_gent.png` | | `5f2a1141-db6f-41bd-924f-4c44ef17aceb` (5) |
| `nochair-aud_lady.png` | | `2b38b615-4bd3-46d4-bbd7-9ac27409668c` (5) |
| `nochair-aud_girl.png` | | `6cf5eeb3-0a25-415d-a5fe-c48088718d5e` (5) |
| `nochair-aud_granny.png` | | `5946211f-1702-4969-83ea-e827a7a3dbd4` (5) |
| `new-1.png` to `new-10.png` | Ten others from them, two each, the same pose: a girl with a soda, a bearded man, a man in a blazer, an older man in a cardigan, a blonde in red, a woman in purple, a boy with a toy car, a girl with a doll, an old man with a moustache, a woman in teal | `3bc140e3-b79c-4218-8453-8e379ad2c4c4`, `32ecffec-e937-4375-9aac-5ed2d62529a8`, `9618ded6-3ba5-431c-b244-cd20ce5d6bc6`, `6ef0e118-c00c-40e1-bf4c-1db9b38a035e`, `fc7fb1be-3b69-4c9c-9d1b-9a4a1e1a25ac`, `9841d601-637c-4908-924c-6a8c6f607127`, `931c7b95-456a-4bd0-8f07-de14f0ff98f3`, `b473b1d6-816a-420c-a8d0-791bf6affae6`, `be94e344-3a7c-4571-ab1a-906108f55aa3`, `e83ebd28-56c4-44d5-a81d-0f4254defc90` (5 each) |
| `compose.py` | The seat split at row 60 (the backrest and far arm behind, the near arm's pad, the seat's front and legs in front), each sitter between | |

The five named stay people (`tools/cast.py`, `wash` 0.12; their PixelLab pictures kept as `stand-own-chair.png`, and kept
from `tools/fetch_people.py`); the ten are ship pieces `audience-0` to `audience-9` (`assets/source/ship/audience/`),
with the empty seat, each with a lightly washed `-lt` twin; `tools/build_ship_map.py` fills about half the empty seats,
the same each build, none beside the balcony's lighting booth door. 80 generations.
