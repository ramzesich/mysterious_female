# Her slip on the funnel's stairway (2026-11-18)

`0.png`: one picture, 96 x 96, her feet's stair point at (48, 80): the frame `stair-slip` in her sheet
(`tools/build_sprites.py`, floor row 79), shown while a gust slides her back down the funnel's stairway
(`updateStairs` in the ship scene). Her floor slip frame, drawn for a flat floor, had one foot 11 px inside the
steps (the user: "Why is she falling through?").

Made from her built slip frame set on the steep flight's own steps (`raw/start-steep.png`, `raw/start.py`, the
steps as `drawStairs` draws them): her legs below the skirt inpainted onto the steps
(`inpaint_image_pro_flash` `40b53985-d815-4958-a218-c4257540f1f0`, mask x 24, y 55, 54 x 39, 5 generations),
everything above kept to the pixel. Then (`raw/clean.py`): her pixels only (the stair pixels it redrew dropped:
the game draws its own), 8 loose specks out, the new leg shades put on the palette; the back of the skirt, jutted
out at the mask's top edge, trimmed back to its own line (rows 55 to 59). One picture serves both flights: on the
gentle one her shoes are within 2 px of its steps too (`raw/fit.py`).

Not used: the whole figure redrawn (`edit_image_pro_flash` `45a754dc-81eb-4e99-89a3-2d86b36a5f72`, 5: her blouse
went grey, her far arm misshapen; `raw/redraw-not-used.png`); the gentle flight's own legs
(`2d43ab49-4e55-4344-91bf-8ec2763eb792`, 5: a half-sitting pose, a pale patch drawn behind her legs;
`raw/legs-gentle-not-used.png`). 15 generations in all.

**Retired the same day:** the user, trying it, found the gust's slide itself weird and chose that in a gust she holds on
to the rail instead (`assets/source/her/stair-cling/`). This picture is no longer in her sheet; kept here.
