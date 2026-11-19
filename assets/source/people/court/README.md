# The court's two players (deck 12, 2026-11-19)

The user: "Instead of balls just spawning above the ring, place two different basketball players on either side
(slightly backgrounded in terms of colors) and make them throw the balls through their respective rings. Make the ball
transition seamless." Each shoots at their own hoop, the ball comes back to their feet, they pick it up, dribble and
shoot again (`Balls` in `src/world/topdeck.js`). Built by `python tools/build_court.py` into `assets/sprites/court.png`.

| What | Where | PixelLab |
|---|---|---|
| The man in red (hoop A, 146.9 m): pro character, size 64, side view, style of the drill's officer | `man/stand.png` (its east view) | character `cb8eb7a0-deda-41ed-9797-6ea2bb7d09d5` (10) |
| The woman in blue (hoop B, 154.4 m): pro, style of the cabin maid | `woman/stand.png` | character `e01b4efd-0761-4f95-8be6-037658b75fed` (10) |
| Holding the ball at the chest: `edit_image_pro_flash` of the stand with the game's own ball pasted there, seed 5 | `man/hold.png`, `woman/hold.png` | `f9d6f9f7-da2a-4b3e-b905-6b1ea3650da7`, `8b896ef6-b55e-46a8-8940-67af6375f317` (5 each) |

The clips, PixMiniMax on a 96 px canvas (the 64 px pictures at (16, 32): feet on row 93), seed 23, index 0 the input:

| Clip | From, to | Man | Woman |
|---|---|---|---|
| `shoot` (12 frames) | hold, to the stand: a jump shot, the ball off the hand in frame 8 (cut out there: the game's takes over) | `64ee4790-015f-437a-863e-5f5d9057210e` | `b1f61387-e1b8-429d-99de-99aea5264853` |
| `idle` (4) | the stand to itself, breathing | `3f8d162a-261c-484c-b88b-5a468b3505e0` | `cca2d9ae-1244-4983-a680-10f555e975bc` |
| `pick` (8) | the stand with the game's ball at the toes (`pick-start.png`), to hold | `7e6f0276-c2ac-45b1-9fdf-90573598d919` | `e013936e-8b98-470e-831e-3f906925050b` |
| `dribble` (8) | hold to hold, one bounce | `99c2a812-0a76-4c28-a3a9-f745813a7f82` | `ce98d9ba-4759-459f-9d4d-22142be8aa43` |

38 generations in all. Checked frame by frame on the court (proportions against hers: 61 and 59 px to her 59; the floor
line; the release and the pick-up against the game's ball at 60 frames a second). Washed 12% toward the wall as the
theatre's people (the user: "slightly backgrounded"); the ball in their hands too, the game's ball turning to and from
`basketball-lt` at the hand-overs. Waiting plays at 4 frames a second (the user: slower than the first GIF).
