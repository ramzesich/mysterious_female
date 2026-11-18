# The towel stack's clips (deck 9, `haz_towels_9`; 2026-11-18)

Built into `assets/sprites/towels.png` by `python tools/build_towels.py` from `soft/`. Played by
`TowelStack` in `src/world/movers.js`. Every frame is 128 x 128: the stool's middle at x 36, the
floor under row 119, the stack standing on the stool's top (row 108). Each is drawn falling east.

| In the game (`soft/`) | What | PixelLab |
|---|---|---|
| `fall/` | The stack falls alone and scatters (frame 0 is also the standing stack and its stool) | PixMiniMax `65e9763a-3265-4536-8049-7dc147e9ec1b` (`raw/fall-c`), from `start-alone.png` to `end-alone.png`; its towels redrawn soft |
| `bury/` | It falls on her standing 36 px past it (kept for her caught under it standing) | PixMiniMax `6fd90930-2453-4b9b-bc95-d53809bd11bd` (`raw/bury-g`), from `start-her.png` to `end-her.png`; redrawn soft |
| `run0/` `run2/` `run4/` `run6/` | It falls on her as she runs past it: each from her own run frame n (`her/run-steady/n.png`) 6 px past it (`start-run-n-6.png`) to the buried heap (`soft/bury/8.png`); she runs on about 10 px a frame, then is buried | PixMiniMax `178505cf-3b2a-4393-b662-8cf6435a2d9c` (0), `2dde61e9-1eb9-4ecb-b8d9-e211c72f4ba8` (2), `d4e88e45-a860-469f-a775-aff4070db7a8` (4), `70f5f1cc-a760-4caa-bf5b-6b2e90910036` (6); drawn from the soft pictures, so not redrawn |
| `emerge/` | The heap stirs, a towel swan pops out, her head comes up under it in her towel turban (frame 0 is `bury/8`) | PixMiniMax `91675bad-fa18-486b-bec3-18bcbd79d561` (`raw/emerge-e`), from `raw/bury-g/8.png` to `end-emerged-swan-e.png`; redrawn soft |

**The soft towels** (the user: "the towels themselves look like white bricks"): `edit_animation`
of every frame of `fall`, `bury` and `emerge`, "redraw every white and pale blue block as a real
folded bath towel ...", seed 7, four frames a call (`ef9874b6-19bf-47a2-a0ee-68cff889ec00` frames
0, 2, 5, 8 of the fall; `01aba3c5-...`, `803606b9-...`, `804bccdf-...`, `a076ed8e-...`,
`ea6153fe-...`, `eba48303-...` the rest, in `raw/soft-test` and `soft/`). The motion is kept to a px.

The scripts: `starts.py` (the stack and stool exactly as the game drew them before, and her standing
sprite beside it), `ends.py` (its own fourteen towels lying scattered; piled where she stood),
`emerged.py` (her turban look from `her-towel/rotations/east.png` sitting up in the heap, a
generated swan shrunk by majority colour to 15 px, its beak whitened), `starts_run.py` (her run
frames beside the soft stack; `AT=6`).

Not used (`raw/`, `tries/`): the first unpinned falls (a, b: a stiff column landing "like books"),
d (the second pinned fall), burials a to f (b arched over her, c stretched the stack taller as it
tipped, e and f stretched worse), the running tries 36 px past it (`runbury-*`: she ran on the
spot), `runb-2b`, `emerge-a` (the darker swan), heaps generated as map objects (`h1`-`h3`,
`heap-b`: snow drifts; `11daaf82-...`, `b90af24e-...`, `bd816188-...`, `761c1f3b-...`,
`206a246a-...`), swans (`swan-a`-`e`: all came as birds; `swan-e` is `51c3cfb2-15b8-4fb4-bb2b-c9b753847d2e`).
