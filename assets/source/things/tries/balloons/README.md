# The party's balloons on deck 8 (part 11's item 14, 2026-11-28)

The birthday party's balloons drifted across deck 8's corridor by its door, and every other balloon of the party in the
same art (the user: "all of the balloons should match"). `tools/build_balloons.py` builds them into `assets/ship/`.

| File | What | PixelLab |
|---|---|---|
| `s1.png` | Five balloons (red, yellow, blue, green, pink), 128 x 32, the game's gym ball as the style: **the user's choice** of two, the look | `create_image_pro_flash` `52ffe685-6049-4573-9634-ea159659298e` (6) |
| `s7.png` | The same, seed 7: rounder, darker outlines (unused) | `dac7ece4-31d2-4b21-adc8-b970ad30a22a` (6) |
| `style-red.png` | `s1.png`'s red balloon, the style of the next two | |
| `small-s1.png` | The five at the game's size (about 15 x 22), `s1.png`'s red as the style: **used** (the user's choice of two) | `0140d595-4cf2-414e-b9e0-eb98f668b449` (5) |
| `small-s5.png` | The same, seed 5: rounder (unused) | `0410e7d4-af35-4e03-8384-4a1102b8d21a` (5) |
| `cut.py`, `cut/<colour>.png` | `small-s1.png` cut into its five balloons | |
| `tries-x8.png`, `small-beside-her-x6.png` | The tries as shown to the user | |

`s1.png` was 19 x 27 a balloon; taking whole rows and columns out of their middles to bring it to 14 x 18 (a third of its
rows) turned them into pointed diamonds, so they were generated again at their size with its red balloon as the style.
22 generations.
