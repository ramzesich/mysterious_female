# Splash Academy's pillow castle (plan-the-rest §7f, P6; 2026-11-27) — APPROVED

The user, of the first new fort (`../pillow-fort-2/`): "I don't like how the entire fort looks like. Let's take what we
learned about the openings, and generate different forts. They also have to be higher, because right now, visually, it
doesn't make sense that cannot jump on top of it" (her jump's feet rise 65 px).

| File | Job | What |
|---|---|---|
| `castle.png` | `create_image_pro_flash` `dcd91d90-0fcf-46ab-95a9-158ae97cfc46` (seed 3, 6) | a pillow castle: **the user's choice ("1")** |
| `bunk.png`, `boxes.png`, `tent.png` | `33d44e98-9454-4ef2-b8da-aa5669104835`, `bb5f2ff6-8841-4b53-933c-d45c2ba1f6a4`, `f31a0d9e-1e2c-4cd0-a468-c8e684ba6940` | a bunk-bed fort, a cardboard castle, a play tent (6 each) |
| `rough-tunnels.png` (`tunnels.py rough`) | by rule | the castle, the cushions leaning at the towers' inner feet and a floor line cleared, a mouth 6 px out from each tower's two faces (the user: "much narrower ... deal with both sides of each wall") |
| `tunnels-s12.png`, `tunnels-s44.png` | `edit_image_pro_flash` `a5343666-032e-4fe9-82b0-5ac8fddc65ef`, `b0bfd0ea-3178-4fc4-b1cc-304ed1605133` (9 each) | s44, **the user's choice ("2")**: each tower's bottom cushion a red crawl tube with a dark opening at both ends |
| `cutaway-s7.png`, `cutaway-s21.png`, `cutaway-lifted.png` | `3b1e88b5-3c5c-43e1-8999-27233f3549ed`, `52a2ffbd-602c-415e-a868-b4ce34e5e334` (9 each) | the tubes cut open (unused: "No, it's worse") |

**In the game:** `tunnels.py rings tunnels-s44.png` (one px of the left tube's bottom outline filled, x 53 of row 102):
at each opening, everything from the dark ellipse's inner edge outward in the tubes' rows (the dark, its ring, its
outline) is `../../pillow-fort-back.png`, drawn behind her; the rest `../../pillow-fort.png`, in front (the user: "the far
wall of the tube (and the ring on the opening) should be obscured by her"; the linen room's shaft's way). Both on one
canvas (`KEEP_CANVAS` in `tools/build_things.py`); the low's `dy` 1 (the user). The ways that failed, in the order tried:
only the dark taken out of the picture in front (holes in the near wall she showed through), the whole tube in front
(she was "not inside them, but just behind them"), the tubes cut open ("worse"), only the ellipse behind her (the ring in
front of her). 60 generations for the castle.
