# The spa's massage guest (deck 11, the massage scene; the user, 2026-11-22)

A woman in a towel wrap and a towel turban (the user's choice of three), lying face down on the second massage table
while the masseur works on her; on E she goes to the sauna's bench and back (src/world/spa.js).

**The character:** PixelLab pro, size 64, side view, in the cabin maid's style (`style_character_id`
4677d8f1-5586-41e1-b13e-53d9bdd49ffc, the women's proportions): **26e8b77a-c87c-4c84-904c-9e7d9765fe42**, "Spa guest
(towel)", 10 generations. 61 px tall. (`spaguest` is another figure, deck 9's "Do Not Disturb" guest: not hers.)

| Folder / file | What | How | Job | Gen. |
|---|---|---|---|---|
| `walk/` | **used**, back outline thinned (`walk-clean/`, `thin_back.py`), at 12 frames a second | skeleton-v3, template `walking` | 070d138d-4eec-4681-adc1-b414c491f6cb (group e8cdac6d-441a-4144-891b-da9363a789b3) | 3 |
| `lie/s11.png`, `lie/s5.png` | not used: her back bare, the towel round her hips | `edit_image_pro_flash` of `lie/input.png` (her standing picture laid flat on the table, 96 x 48) | 83ab7aea-88f8-441f-b790-fd6d0a1a5511, 733075f4-0f5b-4b72-ad3f-56cacb7b59ab | 10 |
| `lie/s5-wrapped.png` | **used**: lying face down, the towel wrapped as when she stands, her turban on the pillow; cut out by its difference from the table (`lie/guest-lie.png`) | the same, seed 5 | 4709da1d-bb72-44db-951c-9c114f5b637d | 5 |
| `up/raw/` | **used**: pushing herself up, kneeling, sitting on the edge, standing at the table's right end; made with the game's table (`up/start.png`, `up/end.png`, `layout.json`), the table taken out and her 3 px lower on it (2, 1 as she sits up), the pad's leftovers under her cut off (`tools/untable.py` to `up/clean/`); backwards she lies down (`lie` in the cast) | `animate_image_pixminimax`, 16 frames | 9681c659-ac98-4496-9a91-a381f451a2cd | 2 |
| `sit/south/` | **used**: sitting down facing us on a high seat (the sauna's bench, 16 to 18 px), the move `sit_seat` with the pelvis held at the seat; the generator drew a grey bench under her, taken out by its own colours (`unbench.py` to `sit-clean/`); backwards she stands up (`sit-up`) | skeleton-v3, south | 1bc5e45f-c75e-41a2-9827-c487584d6c80 (group a9df5da8-6fac-4de0-acfa-539580484772) | 3 |

33 generations in all. The game's folder is `../massage_guest/` (`stand.png` east, `front.png` south, `back.png`
north, `walk/`, `up/`, `sit/`); `tools/fetch_people.py` leaves her alone (`BY_HAND`).
