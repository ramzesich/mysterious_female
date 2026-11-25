# The delivery robot seen from the side (2026-11-25)

The user: "We also need to regenerate the delivery robot, to has a view more from its side". Four `create_map_object`
tries, 64 x 64, `view: side` ("completely flat side elevation, no depth, facing right"):

| Try | Job (object id) | |
|---|---|---|
| `try1.png` | dec6f2af-13a2-4e52-aaa4-ca65a8d9f730 | its screen face turned to us |
| `try2.png` | 26d5401d-3d2c-4a9a-8408-8c6f576dcc9d | a boxy cabinet, side-on |
| `try3.png` | 2c5fe2f1-1b87-43ac-b2cc-24a015ab3f7c | its screen turned to us |
| **`try4.png`** | fea5ec92-6127-4aad-891f-c72aa45c9731 | **Used** (the user's choice) |

Try 4 looked left: mirrored into `assets/source/things/robot.png` to face right as the game expects (it turns it as it
drives); 56 px, four plain rows of its body cut (`CUT_ROWS` in `tools/build_things.py`) to the old robot's 52; its own
colours (`OWN_COLOURS`: on the palette its greys went purple). In the game 2 px into the floor (`ROBOT_SINK` in
`src/world/movers.js`, the user). The old robot's picture: `../robot-front-old.png`.
