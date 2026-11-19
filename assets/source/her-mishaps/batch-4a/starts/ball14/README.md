# The court's basketballs, 14a and 14b (2026-11-19)

`docs/plan-the-rest.md` §3 1.2: a ball in her face, "she tips over backward, stiff as a skittle" (14a, `ball-back*`); on
the back of her head, "she topples forward, stiff as a plank" (14b, `ball-front*`). Built into the gags sheet from
`../../ball-back*/`, `../../ball-front*/` (`tools/build_gags.py`).

All PixMiniMax (`animate_image_pixminimax`, 8 frames, 1 generation each, seed 23) unless said; index 0 of each job is
its input. Starts: her built sheet's standing frame or run frame 1, 3, 5 or 7 (`ball14.py`: `<a|b>-start-<st|r1..r7>.png`),
her middle at x 92 (14a) or 36 (14b) on the 128 px canvas; a run's end a little further on (her momentum).

## The end pictures

Her standing frame turned a quarter (`<a|b>-end-*.png`, `ball14.py`) was the first end; turned flat it touched the floor
only with her hair or her chest (her standing frame is not straight), and set straight along a line under her
(`settle.py`) it "appears to be at an angle" (the user). Redrawn lying flat by `edit_image_pro_flash` (5 generations
each) of that picture on a 96 x 40 canvas (`a-flat-96.png`, `b-flat-96.png`):

| What | Where | PixelLab |
|---|---|---|
| **14a, on her back (used)**, seed 11 | `raw/flat/s11.png`, placed as `a-end2-*.png` | `e7a9b044-732c-4212-a086-fd876c129de9` |
| 14a, seed 5: not used | `raw/flat/s5.png` | `43d31c6c-7efc-484b-bb86-6ede2ffa83b1` |
| **14b, face down (used; the user chose it)**, seed 11 | `raw/flat/b-s11.png`, placed as `b-end2-*.png` | `ceccd9af-6292-415f-91c5-2bcccc513875` |

## The falls (used: pinned to the redrawn ends, `raw/<a|b>-<tag>-e2/`)

| From | 14a | 14b |
|---|---|---|
| standing | `3868ea3f-9cc4-4f89-a16a-f3352be00953` | `c6b42544-df8f-4c18-b2e6-9e6329b29d78` |
| run frame 1 | `bd8c6eff-4277-4466-89d2-cc646c87d02c` | `078f6ef6-1b43-400f-8bbb-239a5dc2395f` |
| run frame 3 | `515b8999-85be-4062-827f-d950dbdc33bf` | `0189480f-d929-488c-919c-daac06cc95b8` |
| run frame 5 | `9dd2fdc1-a1c6-4abc-b75e-df9f575255e5` | `c53fac5f-47db-46b7-a6f2-22d6a4d3257f` |
| run frame 7 | `07c8b061-8a21-4157-933e-fedab18cb973` | `015eb928-3ed0-4054-916c-0ef4c30277c9` |

Cleaned by `clean.py`: the generator's specks out; from frame 1 her lowest pixel on the floor row (120); the last frame
the end picture itself; 14b's red scarf under her face on the floor in the landing frames (it read as blood) recoloured
from her nearest pixels. The lying beat (`clean/<a|b>-lie/`, `ball-*-lie`): the end picture with the butterflies of
her dazed lie (`assets/source/her/dazed-lie/1-5`) copied over her head (no generation: a generated loop would bend
her); a run's clip ends further on, the game sets the loop `ball.dx` on (the gags sheet's meta).

## Not used: the falls to her stand turned flat (`raw/<a|b>-<tag>-s23/`)

| From | 14a | 14b |
|---|---|---|
| standing | `06717b9c-298b-4ca2-9b98-ddd25e9347c0` | `098a0ffc-1564-4b0f-b0fb-bda46a04cdea` |
| run frame 1 | `2219dde4-0b98-4f16-ae1c-433a5454569a` | `da1d31e7-1244-4a5a-ac13-79104ddcc759` |
| run frame 3 | `2b1dff57-62c7-4f56-a6e7-f7f481806815` | `ca6bfe2f-465e-4c02-a7d8-77e91ba91536` |
| run frame 5 | `7295cdb8-d38b-4aee-9e8f-473a61d44749` | `b45c328b-0294-42de-90d8-2cf92c2ef8b1` |
| run frame 7 | `04611322-67cc-4468-9dc2-3f138d1e4469` | `c5fa82a0-e11a-467f-a4ab-7598628a28e1` |

35 generations for 14a and 14b in all.
