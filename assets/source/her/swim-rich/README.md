# Her richer swimming (2026-11-25)

The user: "I want her swimming animation enriched"; and near-catch 5 from the water: "She stops, peeks out of the
water, cries". Her first stroke (`../swim-breaststroke/`, seven frames) moved one arm and her legs never kicked.

Every clip is `animate_image_pixminimax` on a 128 px green picture, the ground kept (`no_background: false`), with the
captions given (a young woman ..., view side, direction east).

| File | What | Job | Generations |
|---|---|---|---|
| `start.png` | her swim's first frame from her built sheet, on a green none of her colours is near, her cell at (22, 14) (`place.json`) | made here | |
| `tries/stroke-s11-0..16.png` | 16 frames, pinned to end where it starts: a full breaststroke in place, the arms pulling in, the knees drawn up, the kick, the glide. **Used** (`swim-stroke/`, frames 0 to 15) | `3b6a907d-e13c-47fa-9ea2-b824a301ab0a` | 2 |
| `tries/stroke-s27-*.png` | the same, another seed: the ground's green changed part way; not used | `b478dbba-aaff-4e8f-a950-859389c9e3e9` | 2 |
| `tries/peek-s19-0..8.png` | 8 frames, not pinned: she comes upright, sitting back on her heels, her arms out to her sides, her chin lifted, looking ahead. **Used** (`swim-peek/`) | `5280a9ad-d362-4ed2-9bd4-ea3c57c5a221` | 1 |
| `tries/peek-s5-*.png` | the same, another seed: she turns to face us, arms straight out; not used | `ebe5e349-4b47-4ac8-835a-0db7a3365497` | 1 |
| `tries/tread-s7-0..8.png` | from the rise's last frame, pinned to it: a small bob, her arms sculling. **Used** (`swim-tread/`, frames 0 to 7) | `e438bedc-a35f-4749-8785-fe26af8a812c` | 1 |
| `tries/cry1-s3-0..8.png` | from the rise's last frame, pinned to it: one hand to the side of her mouth, leaning forward, calling, her face seen. **Used** (`swim-cry/`; the game plays frames 0 to 7) | `31a5a92e-1c71-4185-bec3-68725772351e` | 1 |
| `tries/cry1-s41-*.png` | the same, another seed: its frame 7 turns to us with her arms down; not used | `358d4dba-55d8-4ff2-be88-5a6a2ee93bc4` | 1 |
| `tries/cry-s7-*.png`, `cry-s23-*.png` | both hands cupped round her mouth: hands as big as her face, hiding it; not used | `2eb3b708-e65a-44f5-a4ec-49801f864297`, `13bb9cc4-71b8-446a-82ba-abe7475066c9` | 2 |
| `cut.py` | the ground taken out by colour, loose specks dropped, each frame set on her sources' 96 px canvas where her swim's frames are | | |

Checked frame by frame: each clip's first frame is the frame it was made from, to the pixel, in the built sheet (the
stroke's and the rise's are her old stroke's first; the bob's and the call's are the rise's last); her size and colours
hold; the skirt stays in place through the bob and the call (she leans, she does not slide); specks dropped from seven
frames (1 to 10 px each). Her head in each frame for the popups: `BY_HAND` in `tools/build_heads.py`, by her face's
own pixels.

12 generations.
