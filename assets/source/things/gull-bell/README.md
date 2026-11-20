# The gull with Bumbot's collar bell (§4 2.1, thing 4)

The game's own gull (`../gull-perched.png`, `gull-up`, `gull-down`) holding Bumbot's collar bell in its beak,
on the promenade's round wall light at 140.6 m (`BellGull` in `src/world/movers.js`, `BELL_GULL` in
`tools/population.py`).

- `try-1.png`, `try-2.png`: `edit_image_pro_flash` of `../gull-perched.png`, "the same seagull ... holding in
  its beak a small red cat collar loop with a shiny round brass bell" (5 generations each). The generator
  nudged the whole gull's colours; `merged-*.png` keep only its new collar and bell pixels on the untouched
  original.
- Shrunk to the game's 20 px gull they read as nothing (the user: "unclear what it carries in its beak"), and
  the close-up shrunk was a scribble. **So the collar at game size is drawn by hand** in the close-up's own
  colours (its strap's reds, its gold bell, the slot), option 1 of two the user saw (`game-c1.png`; `game-c2`,
  a thicker U with a buckle, not taken): a thin red ring hanging from the beak's tip, a 3 x 2 bell under it.
- The same ring and bell on the three frames, each from its beak's tip: `../gull-bell-perched.png`,
  `../gull-bell-up.png`, `../gull-bell-down.png` (built as they are, no resize; the gull's own pixels
  unchanged, so it is the same bird once the bell drops).
- The bell glints a size smaller than the things to find, at its bottom right (`COLLAR_AT`; the user moved it
  there from the beak, 2026-11-20).
