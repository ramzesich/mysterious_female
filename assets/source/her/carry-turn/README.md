# Her front and back with a load in her hands (the user, 2026-11-23)

"If she has to turn and face the screen, the carried item should move horizontally to her center and obscure her. If she
has to turn away from the screen, ... be obscured by her", then "We also have to adjust her hands accordingly": her sheet's
`carry-front` and `carry-back` (the game's `pose('front')` / `pose('back')` take them by name while she carries), the
load at her middle in front of her or behind her (`src/world/carry.js`).

| File | What | PixelLab | Generations |
|---|---|---|---|
| `south-96.png`, `north-96.png` (+ `.kp.json`) | `../rotations/south.png`, `north.png` padded to 96 px, their skeletons estimated (`tools/estimate_skeleton.py`) | | 0.2 |
| `south-pose.json`, `north-pose.json` | The poses sent: only the elbows and wrists moved, in three steps; facing us the wrists in front of her at her waist (where the tray is, 31 px over her feet), her back to us in front of her body, out of sight | | |
| `front/0-2.png` | Her front view animated into it (`animate_with_skeleton_v3`) | job `1d0aad34-8e81-4e78-8e48-758ee6347795` | 2 |
| `back/0-2.png` | Her back view, the same | job `cfb03540-04fe-4529-ab3a-ebe934e177de` | 2 |
| `front.png`, `back.png` | **Used**: frame 2 of each, cropped to the rotations' 64 px framing. Only the arms differ from `rotations/`: rows 42 to 57 in front, 47 to 57 behind (her head, face and legs the same pixels) | | |
