# Her climb onto the spa's massage table (the massage scene; the user, 2026-11-22)

From her standing frame (her built sheet's) in front of the game's massage table to her lying face down on it (the 14b
gag's lying picture, `b-end2-st.png`, mirrored, 2 px into the pad: the user's), `start.png` and `end.png` on a 128 x 96
canvas (`layout.json`: the table's place, her floor row 92). PixelLab `animate_image_pixminimax`, 16 frames:

| Raw | What | Job | Gen. |
|---|---|---|---|
| `raw/` | not used: she sat on the edge, lay back on her back, and flipped face down in one frame | 523f0ba0-5e99-4bfd-a693-866ddcb2ff09 | 2 |
| `raw2/` | **used**: hands on the table, up on her knees (from behind two frames), along on all fours, down face down; her hands on the table in every frame of the climb | b807eec0-b9a4-4678-aef6-7d03cfbb56d8 | 2 |

`tools/untable.py` takes the table out of every frame (the game draws its own) and keeps her greys off the palette's
mauve her sheet turns pink, and her skin's scattered pink shading to her skin's middle tone (the user: "too many pink
pixels over her"), into `clean/`; `massage-lie` in her sheet (`tools/build_sprites.py`), backwards to get up.
