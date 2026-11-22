# Her husband's seated clips (§4 2.4, the user, 2026-11-22)

His approved character (`assets/source/hud/husband/`, PixelLab `a1ebd48e-3b9f-40fd-b2d8-e737d4981bba`) with one row of
his forehead taken out, as on his HUD icon (the user: "Remove one line from my forehead, like we did on the icon";
`assets/source/hud/husband/short/shorten.py`), imported as a character of its own so every clip keeps it:
**"Her husband (pyjamas, forehead shortened)"**, `5b85cf25-df58-47e2-b592-affd32aff145` (v3 import, 0.25 generations).

He sits in the Great Outdoors' patio chair (`assets/source/ship/patio-chair/`): its near arm drawn in front of him
(`patio-chair-arm`, the people's `cover`), his back on its backrest; "my far leg should be behind the table": his legs
apart, the far one reaching forward under the table, what shows of it a frame of its own (`far`) drawn behind the map's
furniture (the people's `under`). Kept in his own colours (`own_colours` in `tools/cast.py`: on the palette his hair went
olive, his skin pink, his eye red).

| Folder | What | PixelLab | Generations |
|---|---|---|---|
| `sit-idle/` | First try: seated, hands on his knees, his legs together; the generator drew a brown chair under him (`unchair.py` took it out, to `clean/`); its first frame's face "distorted"; the far leg could not be told apart. Not used ("not working") | skeleton-v3 poses, group `6272a497-0de1-4e70-a9ad-1e459c65370f` | 3 |
| `sit-idle-2/` | **Used**, `idle`: seated upright, breathing from the chest, the near leg bent, the far leg forward; no chair drawn. `make.py`: frame 2's head and legs in every frame (one face, the legs still), the far leg cut to `far` | skeleton-v3 poses, group `0c867a63-9341-42f6-8d40-1914c6ffa6e8` | 3 |
| `standin/` | The stand-in he replaces: the linen-shirted diner's character `89dfbeac-8d4c-4a89-a578-8dbc95ba16fc`, in his own chair | | |

`make.py` writes `out/`; the approved are copied to `assets/source/people/husband/` (`stand.png` the idle's first frame).
`tools/fetch_people.py` leaves him alone (`BY_HAND`).
