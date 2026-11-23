# Her crouch with a load on her forearms (delivery 3; the user, 2026-11-23)

"That would require some sort of additional animation where she crouches with her pillows on her hands and the pillow is
somehow picked up": her sheet's `carry-crouch`, played down and back up by `Carry.pickUp()` (`src/world/carry.js`); the
load follows her fists (`CROUCH_HOLDS`: 4, 8 and 13 px lower than standing, measured from the frames).

| File | What | PixelLab |
|---|---|---|
| `stand-96.png` (+ `.kp.json`) | Her carry-stand (`../carry-walk/2.png`), its skeleton estimated | 0.1 |
| `pose.json` | The poses sent: knees forward and down, hips back and down, back straight, forearms kept level, feet planted | |
| `raw/0-2.png` | **Used**: her carry-stand animated into a squat in three steps (`animate_with_skeleton_v3`) | job `38540a7f-128b-4807-8dfd-08e4c49e0939`, 2 |

Its heads for the popups are estimated (`tools/build_heads.py --missing`, `--from`; 0.2).
