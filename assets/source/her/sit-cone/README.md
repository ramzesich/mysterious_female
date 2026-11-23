# Her seat at her husband's table (§4 2.4, the user, 2026-11-23)

In the table scene (`tableScene` in `src/world/lido.js`) she sits down in the Great Outdoors' patio chair across from him,
facing him, with the cone she carried, licks it while he eats his, and gets up after his book. Her clips in her sheet
(`tools/build_sprites.py`): `sit-cone` (frames 0 to 9 of `cone/sit3/`), `lick-cone` (9 to 14, looped), `sat` (`faced/9`,
the cone eaten) and `sit-up` (`faced/` 9 to 0). They replace her old `sit-eat` (`../sit-eat-clean/`, empty hands at her
mouth: "what does Bumbusik do, while seated?"; made on another chair: "She's also not seating properly in the chair").

Placed at the table's middle plus 12 px, which lands her back on the chair's backrest 7 px further back than first
composed (the user chose 7 of 2 to 8 shown); the chair's near arm drawn again over her lap, as over his.

| Folder / file | What | PixelLab | Generations |
|---|---|---|---|
| `raw/` | First seated clip: her character, the `sit_seat` move, her near hand held at her chest; a mauve chair drawn under her (`unchair.py`). Not used: its eating loops leaned her face into the cone | skeleton-v3, group `f527ed24-96f8-43dd-98e3-22e2a23f1d35` | 3 |
| `eat-raw/` | PixMiniMax from `raw/7`: her fist up to her mouth. Not used (the cone over her face) | `bd057c8a-833b-4fb6-9b90-5d00c3ab3893` | 1 |
| `lick-raw/` | PixMiniMax: her head dipping to lick. Not used (a 7 px lean, her face into the cone) | `57d29a35-d9de-4b09-a7c0-513f071a231a` | 1 |
| `raw2/` | **Used**: one 15-frame clip, `sit_seat` with her near hand at her chest, then seated with her head dipping 14° (frames 11, 13, 15); a dark brown chair drawn under her | skeleton-v3, group `8e4c4028-1732-44f6-9074-1fe418230853` | 4 |
| `clean2/` | `unchair2.py`: that chair taken out by its shape (its darks are her hair's): its own mauves below her shoulders, the darks beside them, the seat's rows; loose specks dropped | | |
| `faced/` | `face.py`: her standing sprite's head (`../rotations/east.png`) in every frame where its own head best matches (the user: "Her face is distorted while she's eating": puffed red lips, closed eyes, a swollen chin) | | |
| `cone/sit3/` | `bake.py`: her husband's own cone, its pixels cut from his still (`../../people/husband-raw/eat-cone/still-s1.png`; the user: "Her ice cream is too big, let it match his"), set in her fist as his sits in his, her fingers drawn over it and her head over it (as she licks) | | |
| `load-cone.png` | The game's carried cone (`load-cone` in `src/world/carry.js`), read from the running game: in her fist at first, too big beside his. The carried cone itself stays as it is (the user: only at the table) | | |

Her fist in each frame: her near hand's skin under her chin (`fist()` in `bake.py`); first found from PixelLab's skeleton
estimates of her wrist (17 frames, 1.7 generations). Her heads for the popups: 17 more estimates
(`tools/build_heads.py --missing`, 1.7). About 15 generations in all.
