# Step 4a's first gags (2026-11-18)

Built into `assets/sprites/gags.png` by `python tools/build_gags.py` (its docstring says what each row
is and where the game stands it). Every frame: 128 x 128, the floor under row 120. All PixMiniMax
(`animate_image_pixminimax`, 1 generation for 8 frames, 2 for 12) unless said; index 0 of each job is
its input. About 36 generations in all.

| Folder | What | PixelLab |
|---|---|---|
| `door-burst/` | 13a's door alone: the world's shut cabin door (muted, `door-cabin-bg`) bursts open toward us, flat against the wall past its hinge, slams shut. Frame 12 is the world's shut door itself; the door frame's left side and top are the world's own pixels in every frame; holes in the leaf filled with the wall's colour, holes by the doorway left clear (the world's dark shows); the doorway clear (`starts/dfix2.py`) | `9cf4df9a-885d-4e16-88f4-095b0aba2e3a` (12 frames, pinned to the shut door) |
| `door-squash/` | 13a: the same swing with her standing 30 px past the door facing it; it slams her flat under the leaf (her hand and foot out), swings back, she is left flat on the wall facing us. Frame 12 is `starts/door-her-flat.png` exactly; frame 1 without her (the game shows her own sprite until the leaf covers her) | `39779db6-5855-4d2d-8440-894fdbcb25c5` (12 frames, from `starts/door-her.png` to `door-her-flat.png`) |
| `door-slide/` | 13a's end: flat on the wall, she slides down and sits (96 px frames, set beside the door by the build); her feet sink steadily (frames shifted by hand, `starts/fix.py`) | `3c604adb-4888-42d8-9cb3-b49a47653761`, from her flattened picture `edit_image_pro_flash` `2260ccbb-393c-4e3d-bc47-2189e9aa67ce` (5 generations; her south view, "squashed flat against the wall, arms and legs spread wide") |
| `door-burst-full/` | The door burst's frames in the full-colour door's own colours (the muting taken back out exactly, `starts/fullcolour.py`): a "Do Not Disturb" door opening on its guest and shutting (the user: it had vanished with its frame) | made here |
| `tray-ride/`, `tray-ride3/`, `tray-ride1/`, `tray-ride5/` | 3: from her run frame 7, 3, 1, 5 (one each quarter of her stride) she hops onto a tray and rides it, arms wheeling. Generated on the old flat tray (`*-flat/`, specks removed); `starts/retray.py` takes that tray out and lowers her 2 px: the world's own tray, the breakfast stewardess's, has its base moved under her by the game (the user: "a normal-looking tray, like the one that the breakfast lady hangs out"; jumping onto it she slides too) | 7: `da038daf-7f28-4395-a429-821314323a6b`; 3: `9ae149b2-1808-49cf-93b3-ae3f9015eb05`; 1: `c8c45094-9636-4f26-b889-9494afec5736`; 5: `48ed4eb9-63e9-44ad-b039-4b1fc08e9324` |
| `chair-collapse/` | 7b: from her slip frame 0 with the world's deck chair at her heels: it takes her behind the knees, she sits, it collapses flat under her, her feet up. The plan's "folds shut on her" did not come in four tries; the user took the collapse | `3a71c18b-9cd2-470a-bc94-fa512c50e4a3` (start `starts/c7b2-slip0.png`) |
| `gull-flail/` | 20: the world's gull landed on her head, she flails at it and breaks into a run; the world's own gull pasted back where it only sits (frames 1, 2, 5, 8), specks removed, every frame on the floor line (`starts/fix.py`) | `179d3b76-b158-4896-9213-30b70952a586` (from `starts/g20-stand.png` to `g20-run.png`) |
| `gull-run/` | 20: running off flailing, the gull on her head (a loop); the same fixes | `1995dc00-cdd6-44c8-89e1-45f9b3d02810` (`g20-run.png` to itself) |
| `sprinkler-stand/` | 16 (2026-11-18): from her standing frame, soaked: she flinches, her hair falls flat over her face; frame 8 her soaked picture (`starts/sprinkler/wet-9b13cff9-....png`, `edit_image_pro_flash` `9b13cff9-439d-4cde-84b6-8403b239d72b`, 5 generations, of her standing frame on 96 px: `stand96.png`) | `bca6de50-f866-4500-8e1a-a020dcf0b1a8` |
| `sprinkler-run1/`, `-run3/`, `-run5/`, `-run7/` | 16: from her run frames 1, 3, 5, 7 (her middle at x 54) she stops short in two steps, to the soaked picture at x 64 | 1: `2664b9b8-b23d-4bcd-8a59-308e01e1bcbe`; 3: `3cdcece7-a9b7-435c-b56f-6ae82474992c`; 5: `843e3b98-33bd-4bef-bec3-3132b6bebd2d`; 7: `245e069b-b571-4c86-82ab-cfc587541e85` |
| `sprinkler-sneeze/` | 16: soaked, a sneeze, back to the soaked picture | `1c644093-c296-4505-a266-bdc922e341f6` |
| `sprinkler-walk/` | 16: soaked, a slow walk loop on the spot (the game moves her, 26 px/s) | `0a304ca6-c8b0-42f2-8714-1639c90d737c` |
| `steam-fan/` | 17 (2026-11-18): her puff picture (frame 0 and 8: `starts/steam/s17-puff.png`, `edit_image_pro_flash` `c129764a-032b-4db4-a560-d3fa2211533e`, 5 generations, of her standing frame on 96 px: `stand96.png`, three loose specks by her collar out), she fans her flushed face | `4a0142e9-a4ea-4105-b11f-04c5f10bce21` |
| `steam-swoon/` | 17: from the puff picture she sways, a hand to her forehead, and sits down dazed (frames 5 to 8 set up 1 px) | `5486e191-9384-47f1-b5a6-90b7b5bc5667` |
| `starts/steam/` | 17's start picture, the puff tries (`puff-*.png`, `puff-cmp.png`), the fixes (`fix.py`) | made here |
| `starts/sprinkler/` | 16's start pictures (`starts.py`), the fixes (`fix.py`: frames 1 px up set down, loose specks out unless water), the strips first shown (`present.py`, `show16-*.png`) | made here |
| `starts/` | The start and end pictures, the scripts that made them and mended the frames (`starts.py`, `starts2.py` from her built sheet, `door_starts.py`, `fix.py`, `dfix2.py`, `fullcolour.py`, `retray.py`, `analyze.py`: bounds, loose specks, colours per frame), and the review sheets shown to the user (`final-*.png`) | made here |
| `raw/` | Every job's frames as downloaded, used or not | |

Not used (in `raw/`): the tray turned into a skateboard (`8619edd9-a098-4a33-9a50-e3958501c478`), two tries on
the old tray from her source run frame lifted onto it (`33828451-13d9-4aa5-956b-19ab111b6ee3`,
`3f5c766b-2fe3-4f71-a69f-5519252f6819`, `109280d6-95a5-48dc-9db0-e3534d19a38d`); the chair from her standing
pose (`70a8095c-46e3-4275-80b2-aba40c85e684`) and three tries at the fold (`ad671d75-bd20-4f5a-8763-125f299742ae`,
`18cc7a9e-c5dc-4196-a691-a2df1477581e`, and two declined with no charge); the door with her, second seed
(`58996240-9113-48bc-863c-cba06ef7fa27`: its doorway turned brown); two more detailed trays from the stewardess's
(`edit_image_pro_flash` `88d1fd22-206e-4bd1-be0b-a817c7f50460`, `6f595933-63d7-4960-9d6e-508bc804397e`, 5 each: muddy
at that size, the user kept hers).

Not used for 16 (in `raw/sprinkler/`, by name): `drench-*` and `run7-*` drew a thick water column over her
(`cc834c57-76e0-45d7-b4fd-ad03ce81787a`, `e5d7e53f-b7f8-4f96-82b8-323163ba5939`), `sneeze-*` uncovered her face
(`3900bd96-da26-45bb-b075-e8028af76257`); the second soaked picture, a blue-black mop
(`edit_image_pro_flash` `889de6ce-800e-4496-a05b-558d888a0af9`). 20 generations for 16 in all.

Not used for 17: the second puff picture (`edit_image_pro_flash` `ab9de1fb-f67b-4a9d-a925-c941afa0b163`: a red blotch
hid her eye). 12 generations for 17 in all.
