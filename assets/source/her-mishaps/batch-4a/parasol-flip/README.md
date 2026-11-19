# Gag 22: a gull across her glide turns the parasol inside out (2026-11-18; built)

PixMiniMax, 8 frames, 128 px, 1 generation each; index 0 is the input. The start picture (`raw/start-322.png`, made by
`raw/start.py`) is her glide frame from her built sheet (cell 322) with the world's open parasol where the game draws
it, behind her, on a 128 px canvas, her feet at (56, 112); facing east (the game flips her: she glides west, to the bow).

| Folder | What | PixelLab |
|---|---|---|
| `raw/flip2/` | **Used.** The parasol is blown inside out (cup up, the ribs showing); she keeps hold of the shaft, looks up at it with her mouth open, her hair flies up, she kicks her legs (seed 7) | `bfadd424-ec3a-443d-8ade-a67ad953a9d5` |
| `raw/flip1/` | Not used: the same words, seed 22; her legs only start to move at the end, a run in the air | `b6c32db6-caf4-4159-bc34-c8de986dbe9b` |

Checked frame by frame (the user's rule) and mended by `cut.py` into `flip/0.png` .. `flip/8.png`: the loose wind
dashes and red scraps under the canopy in frames 1 to 3 taken out (only the largest piece kept); the shaft's left
column, lit pale grey from frame 2 on, put back in its olive over the rows where it is alone. Every colour in the clip is
one of the start picture's; her blouse, the shaft and her hand stay on the same px in every frame.

Shown to the user in the chat over a real screenshot of the air over the bow at dusk, with the game's evening light
(`raw/preview.py`, `raw/g22-preview.gif`, `raw/g22-strip.png`; the clip alone `raw/g22-clip.gif`) and approved. Then,
on the user's word, the crossing gull darts at her before it hits (recorded in the game: `raw/g22-dart.gif`).

**Built:** `tools/build_gags.py` puts `flip/` in `assets/sprites/gags.png` as `parasol-flip` (`parasol.feet` in
`gags.json`); the ship scene's `parasolGag` plays frames 1 to 3 (`GAGS.parasol.flipMs`) while she still sinks at the
glide's pace, then 4 to 8 in a loop (`kickMs`) as she drops, softer than a closed parasol's fall, out of the screen.
Its frame 0 matched in the game against her glide with the world's parasol: 0 px apart, both ways round.
2 generations.
