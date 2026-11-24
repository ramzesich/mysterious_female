# The Library's rope stand going over (near-catch 2, remade 2026-11-24)

The "QUIET PLEASE" rope stand before the Library's aft door (deck 6), knocked over into the door by Bumbot.
`docs/near-catch-2-remake-log.md` has the whole remake; `tools/build_quiet.py` builds `assets/ship/quiet/` from here.

| File | What | PixelLab |
|---|---|---|
| `roughs.py` | Makes the fall's two pictures in the game's own picture of the place (a snapshot at game px, the door open, 96 x 64 from world x 9736): `gen/stand-start.png` (the game's own stand, without its card), `gen/stand-end-posts.png` (each post a quarter turn of its own pixels, lying aft), `gen/stand-end-rough.png` (the same with a rope drawn over them: the end frame given to the generator), `gen/stand-bare.png` (the place alone). It reads the snapshots from the scratch folder it was run in: kept as the record of how they were made | |
| `gen/fall1/0..8.png` | **Used (frames 2 to 6).** The fall, from `stand-start.png` to `stand-end-rough.png`, 8 frames, on the place's picture (`no_background: false`), seed 7. Frame 1 smeared the rope; the generator left dark smears on the wall where the posts had stood, and broke the rope into pieces: the build cuts the posts out along their own axes and draws the rope by rule | animate_image_pixminimax, job `f90b9b1a-e889-4320-ba12-3c0a87acd2c2`, 1 generation |
| `gen/stand-end-redraw.png` | Not used: PixelLab's redraw of the end picture ("two brass posts lying flat, the rope slack between and over them"): it merged the two posts into one long bar | edit_image_pro_flash, job `1898f3ac-217d-42b0-b727-d5964f5231e4`, 5 generations |

Only cut-outs of the game's own picture were sent.
