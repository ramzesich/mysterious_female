# The Stardust's stage and near-catch 3's pieces (remade 2026-11-24)

The stage on deck 6 as one generated picture, and what near-catch 3 plays on it. `docs/near-catch-3-remake-log.md` has
the whole remake; `tools/build_stage.py` builds `assets/ship/stage/` from `gen/`.

| File | What |
|---|---|
| `scripts/rough_stage.py` | Draws the stage's left half flat by rule (160 x 128: curtain with a tie-back, swagged valance, lighting bar with two lanterns, a star cloth, boards), `gen/stage-rough-left.png`: what PixelLab redrew, every shape kept. The right half is its mirror |
| `gen/stage-left-s11.png` | **Used.** The redraw (`edit_image_pro_flash`, seed 11). `stage-left-s3.png`: the other try (a glossy floor, shadows on the cloth) |
| `scripts/props_src.py` | Lays the game's own drum kit (and, then, its grand piano) into the halves where the plan has them: `gen/src-left-drums.png` |
| `gen/redraw-left-drums.png` | **Used, by its box.** The drum kit redrawn in the stage's light. `redraw-right-piano.png`: the grand piano the same way, not used (the user: "remove the piano") |
| `gen/src-left-final.png`, `trap-open-s21.png` | The left half with the drum kit, and the open hatch inpainted into it (lid up on its hinge, a ladder's top in the opening; the mask x 90 to 132, y 92 to 128). **Used: what differs in that box.** `trap-open-s9.png`: the other try (no dark opening) |
| `gen/lamp-s4.png` | **Used.** The hanging lamp, 12 x 26 px of a 32 px canvas |
| `scripts/snag_src.py` | The rival's clip's two pictures, 128 x 128 from the stage's column 48: `gen/snag-start.png` (his run's frame 7, the lamp hauled up, the hatch shut) and `gen/snag-end.png` (the lamp low, the hatch open, he gone), the star cloth and the drum kit turned flat green: he is navy on a navy cloth |
| `gen/snag-s23/0..16.png` | **Used.** PixMiniMax from the one to the other, 16 frames: he runs two steps, leaps, his net's hoop goes over the lamp, he hangs and swings, the lamp comes down, he drops onto the hatch, it opens, he is gone, his net last. `snag-s7/`: the other try (its last frame kept a white blob) |
| `gen/puff-start.png`, `gen/puff/0..12.png` | The flour: PixMiniMax on the open hatch's own picture, pinned back to its start; frames 2 to 10 used |
| `dancers/` | The dancers' tries, east and south: her A (rehearsal clothes), **her B (show costume, the user's choice)**, him A, him B (the user: "looks like a waiter"), him C (blue waistcoat), **him D (silver shirt and blue sash, used)**, him E (blue tailcoat, top hat). The two used are the cast's `dancer_her` and `dancer_him` (`tools/cast.py`), their frames in `assets/source/people/` |
| `scripts/poses3.py` | Her two clips' poses (`assets/source/her/start-back/README.md`) |

Only pictures of the game's own stage, flat roughs of it and the game's own figures were sent.

## Generations (156)

| What | Tool | Job / id | Gens | Used |
|---|---|---|---|---|
| Stage, left half, seed 3 | edit_image_pro_flash | f4c4a65b-3f19-4ffd-9926-9bae28fdc14c | 6 | no (glossy floor, shadows) |
| Stage, left half, seed 11 | edit_image_pro_flash | 2e016007-fa0a-4ba7-b663-e1a23a4d484e | 6 | yes |
| Drum kit redrawn in the stage | edit_image_pro_flash | 165ac428-2d09-4a63-b773-4236dd582862 | 6 | yes |
| Grand piano redrawn in the stage | edit_image_pro_flash | 03909bc7-f276-42c5-9cbb-c7c76aa5c96c | 6 | yes |
| Dancer her A (rehearsal) | create_character pro | a1685c66-5c90-4c79-bfc5-8566bb0a8dba | 10 | candidate |
| Dancer him A (rehearsal) | create_character pro | 0ae9a34e-0f36-483a-bd99-3f3e19951d77 | 10 | candidate |
| Dancer her B (show costume) | create_character pro | 9baa6f8b-6aa3-40a8-907d-4d3daf0c6313 | 10 | candidate |
| Dancer him B (show costume) | create_character pro | 7d747a87-d714-4de8-b617-821d0b8100e3 | 10 | candidate |
| Her start-back | animate_character skeleton-v3 poses | group a61034fe-3664-47c6-b9e9-42033fde2d34, job 618f9469-1f70-4e2b-ab60-8df985e2c6c0 | 3 | |
| Her look-up | animate_character skeleton-v3 poses | group 44fd961d-0da4-4a82-abe6-77b41015aac7, job 8712bc31-9952-4a10-9950-0ed0e1a518ea | 3 | |
| Stage manager notice | animate_character skeleton-v3 poses | group 651c414a-48b9-4893-b975-3c66d083c112, job 53000cbc-5b49-4968-afd1-b98d59c3e14b | 3 | |
| Dancer her B dance (salsa move) | animate_character skeleton-v3 move | group 9948ed4a-8033-4e19-aa8c-592c99d6fb07, job a3d8944a-af9b-4357-9e7e-079e69c3af0a | 3 | |
| Dancer him B dance (salsa move) | animate_character skeleton-v3 move | group c06d1243-2573-4375-ae10-f7c79bf1f85e, job 45b48a8f-e806-45d9-bafa-f7f0c53c31ac | 3 | |
| Hanging lamp, seed 4 | create_image_pro_flash 32x32 | 091aaa51-f448-4842-a256-b3c4cbfd7c0e | 5 | yes |
| Open trap door, seed 9 | inpaint_image_pro_flash | 087d8a22-5c1c-462d-859c-f4981d1efb79 | 6 | |
| Open trap door, seed 21 | inpaint_image_pro_flash | 906cd4d9-53c4-4dca-a5be-2eb5f356a355 | 6 | |
| Rival run (run move) | animate_character skeleton-v3 move | group cb511bd8-5ab4-4c62-b01c-a3e76017603f, job 135291eb-f083-436c-ba9b-dd2468fe086e | 3 | |
| Rival's leap, snag and fall, seed 7 | animate_image_pixminimax 128x128, 16 frames, start and end pinned | 0788cf37-4fbe-4079-be51-c1541105c48c | 2 | |
| The same, seed 23 | animate_image_pixminimax | a3a4347a-de6e-4d26-ba75-f4f6573e4f23 | 2 | |
| Flour puff out of the open trap door | animate_image_pixminimax 64x64, 12 frames, pinned back to its start | 1cea73f5-8b13-49a2-b8da-56f6882242ec | 2 | |
| Dancer her B startle (hop_back move, hands up) | animate_character skeleton-v3 | group 6fd4d92d-4592-44ac-95f4-2d52cf39b369, job 120133d6-0ff4-4dea-b3ee-f6a6b732eb9d | 3 | |
| Dancer him B startle (hop_back move) | animate_character skeleton-v3 | group 5d64a547-dcb6-4b56-bf76-f35932a6642d, job 86bc7745-ef0f-43d6-864f-df4c7c7160c6 | 3 | |
| Dancer her B idle (idle move) | animate_character skeleton-v3 | group c0e4956a-f64a-4331-abff-133371115286, job 985c424e-1231-4b0d-a63e-13412fb1ffc6 | 3 | |
| Dancer him B idle (idle move) | animate_character skeleton-v3 | group 97a21b54-ef38-4cdd-971b-a3bb65d7d3d2, job 59cfc2a1-87d7-4bd0-a427-3576145b8543 | 3 | |
| Dancer him C (blue waistcoat) | create_character pro | 1ce60421-3c22-4d13-94f6-73b8015956a5 | 10 | candidate |
| Dancer him D (silver shirt, blue sash) | create_character pro | 319870d1-ce90-41d9-b074-5c8039a85f04 | 10 | yes (mine of three, after the user: B "looks like a waiter") |
| Dancer him E (blue tailcoat, top hat) | create_character pro | dea30412-7002-451b-a5e1-da4b556e7f3f | 10 | candidate |
| Dancer him D dance (salsa move) | animate_character skeleton-v3 | group 61801c0a-7530-4519-97a7-c578e599ed63, job 63cbb285-c254-4289-9292-0aba44a5e460 | 3 | |
| Dancer him D startle (hop_back move) | animate_character skeleton-v3 | group ff98e858-d5a8-4745-882d-b56c4285ee2c, job 9997bfb4-7bf1-420f-925a-47116e9aa347 | 3 | |
| Dancer him D idle (idle move) | animate_character skeleton-v3 | group 81a8c204-a775-4a09-a392-0ac7e1b357b2, job 1769bb6f-cdaa-4c7c-8751-e44df3e67787 | 3 | |
