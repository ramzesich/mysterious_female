# Gag 23: "Oh, sorry!" at a "Do Not Disturb" door (2026-11-19; built)

With no tangerine on her, a "Do Not Disturb" door opened on its guest (E at it, or her cry by it): a startled hop, both
hands over her eyes, her cheek blushing; she turns away from the door and tiptoes off, quick, to the next wall or door
across the deck, or out of the screen. 128 px cells, her middle at x 64, her feet on row 120 (the world's y is row 121),
facing east (the game flips her). The start picture (`raw/start.png`, `raw/start.py`) is her standing frame from her
built sheet (cell 0).

| Folder | What | PixelLab |
|---|---|---|
| `raw/cover1/` | **Used.** PixMiniMax, seed 7: the hop, her hands over her eyes, her head ducked; its last two frames turned her whole hands hot pink (its "blush"), so frames 7 and 8 are frame 6 with the blush set by hand on her cheek (`raw/blush.py`, the palette's pinks; tries in `raw/blush-variants.png`) | `deed13d6-a2d4-4a9b-9630-73135cfb2e34` |
| `raw/cover2/` | Not used: the same words, seed 22; her blouse greyed, no blush | `22a27376-4160-49ef-96ce-6db96fa22849` |
| `raw/tip1/`, `raw/tip2/` | Not used: PixMiniMax walk loops from and to `raw/end-blush.png`, seeds 7 and 22; tip2 was shown, and its strides (feet 28 px apart, a 2 px bob) read "a bit like a skip-dancing" (the user) | `69b9de51-5092-42d4-bcfb-be9890fda98f`, `a7ab3070-73de-4b97-a5c2-a02843723212` |
| `raw/tip3/`, `raw/tip4/` | Not used: the same with "tiny steps" in the words; strides as wide | `96457fb2-a101-4ebd-83d4-f91c2497e8df`, `6cfa4561-0ec8-4120-81ae-bf7069e15f1b` |
| `raw/tip5/` | Not used: her character's "sneak" move, skeleton-v3, hands over her eyes: a crouched sneak, her hair lighter; it stays on her PixelLab character as "tiptoe-covered" | group `97961198-5844-4945-8edc-ccbf3ceec18a` |
| `raw/tip6/` | **Used.** animate_with_skeleton_v3 from `raw/end-blush.png` along skeletons laid out by rule (`raw/tiptoe_kp.py`: her estimated pose from the hips up in every frame, `end-blush.png.kp.json`; two tiny steps a round, each foot 10 px, lifted 3, on her toes, the pelvis level, knees forward) | `6ba32aeb-4fad-4432-b30e-f96813aa9cb9` |

Checked frame by frame and mended by `cut.py` into `cover/0..8` and `tiptoe/0..8`: the blush by hand; tiptoe frames 4 to 6
set down 1 px onto the floor; no new colour against the start picture, no half-transparent pixel; tiptoe/0 is cover/8
exactly, cover/0 her sheet's standing frame exactly. Her planted foot slides about 2.6 px a frame: the game moves her at
that pace (100 px/s at 26 ms a frame, the user's "make her move faster" twice: 50, then 35, then 26 ms).

Shown over a recording of deck 9's door and its guest (`raw/preview.py`: the door's frame matched to the recording's by its
pixels; `raw/g23-preview.gif`, `raw/g23-strip.png`, the clip alone `raw/g23-clip.gif`) and approved, with the door's new sign
(`assets/source/ship/dnd-hanger/`).

**Built:** `tools/build_gags.py` as `dnd-cover` and `dnd-tiptoe` (`dnd.x` in `gags.json`); the ship scene's `sorryGag`
(`GAGS.sorry` in `src/config.js`). About 12 generations (cover 2, PixMiniMax tiptoes 4, the sneak 3, the skeleton tiptoe 3,
two skeleton reads 0.2).
