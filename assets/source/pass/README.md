# The Seven Seas' pass (near-catch 1 remade, 2026-11-24)

`python tools/build_pass.py` makes `assets/ship/pass/` from `gen/`. The whole record: `docs/near-catch-1-remake-log.md`.

| File in `gen/` | What | PixelLab job | Generations |
|---|---|---|---|
| `base-crop.png` | The place bare (its table, chairs and cabinet out of the picture), from the running game, 160 x 64 | (the game's) | |
| `rough-crop.png` | The same with the counter drawn flat by rule, at its size | (the game's) | |
| `counter-a.png` | The rough redrawn (`edit_image_pro_flash`): mahogany, panels with knobs | `7b19f09a-65ef-4252-933c-b984e689fbf0` | 6 |
| `counter-b.png` | The same: walnut, cupboard doors. **The user's choice** | `6ee8698c-f9a8-48a0-ad1f-c91a190b8281` | 6 |
| `bowl-bg.png`, `bowl-start.png` | The place with the chosen counter (the window painted out to plain wall), and with the game's own fruit bowl on the counter's forward end, 96 x 64 | (composed) | |
| `bowl-end-a.png` | The start picture edited: the bowl fallen, its fruit spilled, no oranges | `da0a9c8e-c2fb-432b-aefb-dbd618706d33` | 5 |
| `bowl-end-b.png` | The same, another try: the fall's end | `8a44a657-19e9-486a-a80b-40db5bae2944` | 5 |
| `fall-a/` | The fall, PixMiniMax from the start to that end, 12 frames, seed 5. Used: 3 to 9 and 12 (1 and 2 are smeared) | `c58229c5-2780-4001-ad18-442d374effb3` | 2 |
| `fall-b/` | The same, seed 21 (specks in its first frames) | `77b23cdc-b30c-4ccd-b997-47f3589dbad8` | 2 |
| `plate.png` | The lunch's plate, 24 x 16 (`create_image_pro_flash`) | `370b5991-6836-4e51-b865-2edcfabc2a14` | 5 |

31 generations.
