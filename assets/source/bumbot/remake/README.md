# Bumbot made again (plan-the-rest §7a, part 6; 2026-11-24)

The look is the user's choice and so are the clips ("I like all of them", 2026-11-24). `python
assets/source/bumbot/remake/cut.py` makes `clips/` from `raw/`; `tools/build_sprites.py` (`BUMBOT`) builds his sheet
from `still.png` and `clips/`, in his own colours. The old sources beside this folder (`rotations/`, `run/`, ...) are
kept for comparison and are no longer built.

## The look (`look/`, `still.png`)

Generated at the game's size (`create_image_pro_flash`, 48 x 32 and 52 x 36, his HUD face
`assets/source/hud/face-bumbot.png` as the style image, 5 generations each). Edits of the old sprite (`edit-*.png`)
came back blurred and in its lanky shape. **The user chose `real-1`** ("1", of seven shown) and its coat as it is
("Leave as it is"): `still.png`, the same pixels on a 64 x 64 canvas, his feet on row 56. He stands 26 px tall and 36
long. **His colours are his own, not the palette's:** palettized he becomes a flat purple silhouette.

| File | Job |
|---|---|
| `real-1.png` (chosen) | `6a2a287f-0430-4b7f-92d8-077879e098c1` |
| `real-2.png` | `f462a72c-16a1-4541-b14e-90ee6c825d62` |
| `cute-1.png`, `cute-2.png` | `869a775f-532e-4ed9-a650-3b41cf9d1ac8`, `4927b696-6441-4992-be5f-78a979038ad7` |
| `edit-real.png`, `edit-cute.png`, `edit-photo.png` | `e24e77f2-7e86-4796-88a4-4537a5334609`, `90d847f4-86b2-4d39-922a-05319f382ae2`, `f407c136-c342-4e7a-9bc8-e82c935f50ba` |
| `real-3.png` to `real-5.png` | `c83de5fa-30d9-4226-97ea-e0fd05c55635`, `8401b4fc-c4e1-4e2f-b019-dc8f851d637f`, `e391fa46-0ef4-44d6-bc94-f663b2054489` |
| `mid-3.png` to `mid-5.png` | `9d76066c-cd47-4158-92fe-dd032c1748fb`, `d2ff7e4c-e0a6-4981-bf38-009d920afca2`, `f57c6b09-3e61-4c97-8fe7-b1b2dbf6af5b` |

65 generations. The photo cut-out sent with `edit-photo` was the cat alone on a flat ground.

## The clips (`raw/<name>/`, frame 0 the start picture)

All `animate_image_pixminimax` from `still.png` (or from a pose an earlier clip ended in), 64 x 64, on transparency
(one run on green, keyed out: `run-c`). A clip that returns to its start has the start as its last frame too.

| Clip | From, to | Frames | Job |
|---|---|---|---|
| `run-a` (a stride every four or five frames) | stand | 16 | `a1ce746d-8f87-4886-aae6-6172c2fa111a` |
| `run-green` (`run-c` keyed; its frames 2 to 9 are one stride, 10 to 15 the same again) | stand, on green | 16 | `bc652b6a-338e-4db6-911e-903eee99f614` |
| `run-b` (one stride over all sixteen: too slow) | stand | 16 | `fc62195a-e3eb-4295-97d2-8f27cb3ea34b` |
| `sit-a` (its frame 12 is the sitting pose the sitting clips start from) | stand | 12 | `f06728d2-80c4-4561-9440-57eca3ee5d51` |
| `sit-b` | stand to sitting | 8 | `07ec037e-5dd5-4214-a368-933cd584af15` |
| `idle-a` | stand to stand | 16 | `63e02e0e-3eb3-4f89-b1c5-f74908763827` |
| `walk-a` | stand | 16 | `ab06a20e-9608-4de0-a05d-4ef329f7bbc1` |
| `jump-a` | stand to stand | 16 | `5c30ded2-67c7-441a-869a-552e0e4b5aac` |
| `shake-a` | stand to stand | 12 | `24be09ef-2851-4901-a778-e378c866c148` |
| `eat-a` | stand | 16 | `f76cd987-f98c-4a68-9333-0f1caae33109` |
| `liedown-a` (its frame 16, set 1 px up onto the floor, is the sleeping pose) | stand | 16 | `1a299126-4e4c-4688-a4ba-2303ba0d6ee6` |
| `stretch-a` | stand to stand | 16 | `31000a54-99b3-4674-b75c-62de2581c3fc` |
| `loaf-a` (its frame 12 is the loaf) | stand | 12 | `004e70f9-45d7-488c-b57a-9d2fd70ca910` |
| `lookback-a` | stand to stand | 12 | `0deedc50-1850-48a5-966e-69b75231b7b2` |
| `turn-a` | stand to the stand mirrored | 12 | `3f93dc7f-3747-4b6e-ac29-2aad06f10d9b` |
| `crawl-a` | stand | 16 | `e1a81036-8ca4-4ca2-ad93-b8f5f8982ac2` |
| `sitidle-a` | sitting to sitting | 16 | `ec1e0cb3-00a0-46b7-8c38-6ecfdc60708c` |
| `wash-a` | sitting to sitting | 16 | `e8a229c5-027e-4127-af78-7591af3d4bac` |
| `bat-a` | sitting to sitting | 12 | `b3bd5a65-0921-49d9-81ee-1b1ea37b1233` |
| `standup-a` | sitting to stand | 8 | `50dd0ae4-e08f-4457-b0e0-3ac5508465d9` |
| `asleep-a` | asleep to asleep | 16 | `51bd4e66-1235-4793-8120-60850b19b8a3` |
| `wake-a` | asleep to stand | 12 | `c13685a4-1fab-41bf-a872-1b15b98f35da` |
| `loafidle-a` | loaf to loaf | 12 | `39d4100d-ee0b-421d-bb67-394bead3e0fa` |
| `loafup-a` | loaf to stand | 8 | `d2f2e133-002e-47fc-8f94-2f26f22881d5` |
| `rope-a` (from `rope-start.png`: `jump-a`'s frame 4 with the stage's rope drawn at his paws) | mid-leap | 12 | `dfc22fb3-ebd2-4ee4-8d9c-2d9a578f8c2a` |

| `fish-green` (from `fish-start.png`: the sitting pose at the edge of a tan floor over blue water, on green; the cat cut out by colour) | sitting to sitting | 16 | `9ce35f07-7fbb-48bd-bd5c-f09ad7847df8` |

49 generations. With the look: 114.

## The frames shown to the user (2026-11-24)

| Shown as | From | Frames |
|---|---|---|
| idle | `idle-a` | 0 to 15 |
| walk | `walk-a` | 1 to 16 |
| run | `run-c` | 2 to 9 |
| jump | `jump-a` | 0 to 16 |
| look-back, turn, stretch, shake, eat, crawl, rope | `lookback-a`, `turn-a`, `stretch-a`, `shake-a`, `eat-a`, `crawl-a`, `rope-a` | all |
| sit, sat, stand-up | `sit-b`, `sitidle-a` (0 to 15), `standup-a` | |
| wash, bat | `wash-a`, `bat-a` | all |
| loaf, loaf-rest, loaf-up | `loaf-a` (0 to 6), `loafidle-a` (0 to 11), `loafup-a` | |
| lie-down, asleep, wake | `liedown-a` (set on the floor), `asleep-a` (0 to 15), `wake-a` | |

Loose specks under 12 px off every frame but the shake's drops.
