# The man with the popcorn tub tips it (part 11's item 12, 2026-11-27)

The theatre's popcorn (`haz_popcorn`, deck 6, 226.54 m): the man with the tub (`amb_audience_3`, `aud_popcorn`) tips it
now and then and it lies on the aisle's floor ahead of him; running onto it is the chips' slip (scenario 1). The user
approved the clip composed over his seat, then the game ("Approved").

| File | What | PixelLab |
|---|---|---|
| `start.png` | His game picture (`../../aud_popcorn/stand.png`, him in the theatre's one seat) at (4, 8) on a 128 x 96 green ground over a floor strip from row 88 | |
| `s1/f00.png` to `f16.png` | PixMiniMax, 16 frames, seed 1: the tub tips over his knees, the popcorn pours onto the floor ahead of him, he rights it: **used** | `b4b80c22-7cc5-40ba-bc7f-9a0ebd62a2ac` (2) |
| `s7/` | The same, seed 7: the ground's green shifts and the floor strip gets marks (unused) | `4b98a7c3-5a6e-4dc0-beee-75c4b182efd8` (2) |
| `cut.py` | Each frame off the green, the generator's seat out and the game's own put back split round him (as `../../audience-seated/compose.py`), the lying kernels a layer of their own; 13 and 14 left out (he lurches and the generator's seat moves with him), a speck and the kernels left hanging in the air taken out, the lying ones settled onto the floor | |
| `cut/<i>.png`, `cut/floor-<i>.png` | Its output | |

`tools/build_popcorn.py` then writes his clip `tip` (`../../aud_popcorn/tip/`, frames 3 to 12, 15, 16 in his 80 px cell)
and the lying popcorn's strip `assets/ship/popcorn.png` + `.json`; run `tools/build_people.py` and
`tools/build_heads.py` after. 4 generations.
