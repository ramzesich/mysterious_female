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
