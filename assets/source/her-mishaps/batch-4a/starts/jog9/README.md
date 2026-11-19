# The jogger's gags, 9a to 9d (2026-11-19)

`docs/plan-the-rest.md` §3 1.2. The meetings as the game draws them: `starts9.py` (`meet.png`, 9a to 9d left to right).
All PixMiniMax (`animate_image_pixminimax`) unless said; index 0 of each job is its input.

## 9b: he runs into her, she standing facing him

| What | Where | PixelLab |
|---|---|---|
| Her start (her standing frame at x 84) and end (her dazed sit's first frame, 22 px back) | `b/start.png`, `b/end.png` (`../jog9b.py`) | made here |
| **Her fall (used):** knocked off her feet, back and down on her bottom, a little bounce; the generator's speed lines (frame 1) and specks taken out by `clean.py`; built from `../../jog-bowled/` | `b/raw/s23/`, `b/clean/` | `a2f2b5c9-3bc6-450b-a850-d972aa4d8261` (seed 23, 12 frames, 2) |
| Her fall, not used (a held first frame, big speed lines) | `b/raw/s11/` | `92859e48-ec2f-433f-a5ac-03290247ca48` (2) |
| His start: his run frame 3, she sat 40 px before him (taken out of every frame after); and from his standing frame | `sorry/start.png`, `sorry/start-stand.png` (`../jog9sorry.py`) | made here |
| Jogging on the spot, palms out (the user: "What is he doing after he hits us? That looks weird"): not used | `sorry/raw/s11`, `s23`, `r2`, `st2` | `05bf1b65-929e-40a9-b8bd-7ecda7b3ea65`, `61a4fac4-7f09-4bf7-8610-820bbfdbbabf`, `8cdd8794-8a96-49f8-9c5f-58005d4ec156`, `9af2178c-83d2-466e-ace2-1edc93324761` (1 each) |
| A hand raised by his head (the user: "It looks like he's saying Hi in both cases"): not used | `sorry/raw/w23`, `w7` | `b5d631b3-b0bf-4ce4-b7cf-cffac67c6ad3`, `b195b94e-3788-4b6a-af4c-e9dbc0456503` (1 each) |
| The hand behind his head (the user: "His hand has to go behind his head"), two tries read as hair, one turned to face us: not used | `sorry/raw/h23`, `h7`, `e31` | `505ce39e-4293-4b95-859d-048aeaa9bb67`, `abd4eb69-e3b5-471d-8965-5fed3628ab2a`, `5a765770-eb85-4551-b38b-27dce15154ba` (1 each) |
| His end pose: `edit_image_pro_flash` of his standing frame, the far elbow up before his face, the hand hidden behind his head | `sorry/raw/edit5/0.png`, `sorry/end-scratch.png` | `e37f6351-b01c-46b0-a764-8b65f7fdfe35` (seed 5, 5) |
| **His sorry (used):** from his standing frame to that pose; frames 2 and 3 (his fist swung forward) left out; her taken out (`clean.py`); mended by hand (`sorry/fix_sc23.py`: his far hand still peeking out at his hip in frames 6-8, skin at the back of his head, a bump on his shorts); on his own 64 px canvas in `assets/source/people/jogger/sorry/` (0, 1, 4, 5, 6, 7, 8 as 0 to 6); `scratch` is 4-5-6-5 of it (`tools/cast.py`) | `sorry/raw/sc23/`, `sorry/clean-sc23/` | `1d02cc23-1110-4a4a-a999-d079838dc712` (seed 23, 8 frames, 1) |

Composed over the promenade for the user (`compose9b.py`; the railing in front of them from a shot of the game with a
marker at their layer). 19 generations for 9b.
