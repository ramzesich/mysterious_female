# The gym's balls (plan-the-rest §7f, 8; 2026-11-26)

| File | Map object | What |
|---|---|---|
| `1.png` | `2ebd1a59-9119-47ba-9cc7-f3748ef9b603` | a dusty blue gym ball with streaks: **its blue taken for the second ball** (the user: "both blue and purple") |
| `2.png` | `b259af02-ff4c-4e26-9860-7c42bb56c5c6` | a plain violet gym ball: **the ball, its shading in every frame of both** |
| `3.png` | `be367b94-f90b-4d39-84ff-504407771367` | a mottled silver grey one (read as a stone) |

All three `create_map_object`, side view, 32 x 32 (the ball 24 px across), 1 generation each: 3 in all. The frames
(`assets/source/things/gym-ball-<purple|blue>-<nn>.png`, 32 over a whole turn) are drawn from 2 by
`tools/build_gym_ball.py`: its light still in every frame, a seam and two ribs drawn by rule on the sphere at each angle
(the user: "The balls have lines, so they should turn. The light has to stay still"), the blue the same picture in 1's
hue. In their own colours (`OWN_COLOURS` in `tools/build_things.py`).
