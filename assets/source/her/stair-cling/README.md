# Her hold on the funnel stairway's rail in a gust (2026-11-18)

The user, on the gust's old slide ("she slides on her feet backwards down fast. Looks weird"), chose: in a gust she
grabs the handrail and holds on; ↑ and ↓ do nothing until it drops; nothing is lost (GAME_DESIGN.md, region 8: "no
climbing in a gust"). The frames `cling-up` and `cling-down` in her sheet (`tools/build_sprites.py`, floor row 79 of a
96 px canvas, her stair point at x 48): crouching into the rail facing up the flight (the wind aft, at her back: her
hair blown forward over her head), and facing down it (the wind in her face: her hair streaming behind). `down/` is
stored mirrored, facing east as all her frames; the game flips it. Played by `updateStairs` in the ship scene: the
crouch, a hold on its last frames, the crouch backwards to stand.

Made: her standing frame on the steep flight's own steps with its handrail where the game draws it, 22 px over the
flight's line, in front of her (`raw/start-up.png`, `raw/start-down.png`, `raw/start.py`); PixMiniMax 8 frames each,
1 generation each: up `c895a565-3a10-4f1c-9d64-3d3fe192a2be`, down `ab0740f6-1d21-4f39-b3c3-ded8dba67c6b`
(`raw/up/`, `raw/down/`; index 0 the input). Cut out (`raw/cut2.py`): the rail found in each frame (the generator moved
it and redrew it white, grey or dashed: the bands of the flight's slope where white runs across the picture, and one
either side) and taken out, her body filled across it from her own pixels above and below (the game's rail is drawn
in front of her there); the steps it redrew, loose pieces, the wind streaks across her, and in down frame 2 a white
puff before her face (by hand, her face kept) taken out; every colour on the palette. Her feet on row 79 in every
frame.

Not used: two whole-picture edits (`edit_image_pro_flash`, 5 each): up `c638cd95-10d8-4dcc-bfcd-5801eeb6035c` wiped
the stairs and the rail and blew her hair the wrong way; down `db3731d5-3c2d-4b41-88b9-d0a828cb5a48` put her hands to
her face, not on the rail (`raw/edit-*-not-used.png`). 12 generations in all.
