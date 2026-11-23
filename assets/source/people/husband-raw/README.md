# Her husband's seated clips (§4 2.4, the user, 2026-11-22 and 23)

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
| `sit-idle-2/south/` | The same idle seen from the front, for the cabin's sofa; not used (the user: his own front view, `front.png`, his lower body behind the bed) | the same group, south | 3 |
| `sit-wave/` | First wave: his near hand swung up beside his head; it crossed his face on every up-swing. Not used | skeleton-v3 poses, group `00844706-f5d8-49a0-a19c-c70bd72a7081` | 3 |
| `sit-wave-2/` | **Used**, `wave` (E at him after the table scene): his near hand raised forward toward her, flapping up and down, twice; its 8th frame (thinner, upright) dropped | skeleton-v3 poses, group `42fe0ee9-4ef6-4b77-873a-9a0eb3747bd3` | 3 |
| `sit-laugh/` | **Used**, `laugh` (a stub once the machine is refilled): his head tips back three times, mouth open, hands in his lap; 8th frame dropped | skeleton-v3 poses, group `985466e9-26f0-403b-b669-ae91d7b558a9` | 3 |
| `sit-give/` | **Used**, `give` (his book to her): he leans in and reaches his near hand out across the table, holds, comes back; 8th frame dropped; the held frames' face the first held frame's (its brow came dark, stern: `FACE_FROM`). The book is in his fist from its third frame (`GIVE_HANDS` in `src/world/world.js`) | skeleton-v3 poses, group `65bf4fc4-608c-4df6-8593-9c85a3e65f2c` | 3 |
| `eat-cone/still-s1.png` | **Used**: `edit_image_pro_flash` of his seated frame (`sit-idle-2/east/2`): a soft serve in his near hand at his mouth. Its cone's pixels are hers too at the table (`assets/source/her/sit-cone/bake.py`) | `a92b3d81-8a2a-46b7-937e-a4861fbf64b8` (seed 1) | 5 |
| `eat-cone/still-s7.png` | The other seed: its orange top read as a torch. Not used | `e5d86be0-da35-4588-b28b-98e2231c3ba6` (seed 7) | 5 |
| `eat-cone/e1/` | **Used**, `eat` (the table scene, looped): PixMiniMax from `still-s1`, the cone to his mouth and a lick, his head dipping to meet it | `27f6965d-28ad-40b8-b80c-a01c7bc30ef2` | 1 |
| `embrace/` | **Used**, `embrace` (the kiss, once he has been fed): his front view with the bear (`../hud/husband/short/south-bear.png`, 96 px canvas) moved into his arms round her waist, played backwards to let go; `hand.py` cuts his near hand (skin and its outline at his waist) into `assets/sprites/hug-hand-1.png`, `-2.png`, laid out as the sheet places his frame, drawn over her | `animate_with_skeleton_v3`, job `0e950cd5-517b-4e87-a3f8-fe95dc14516b` | 2 |
| `standin/` | The stand-in he replaces: the linen-shirted diner's character `89dfbeac-8d4c-4a89-a578-8dbc95ba16fc`, in his own chair | | |

`make.py` writes `out/` (not kept in the repo): every clip gets the idle's legs and loses its far leg; the idle keeps one
face (frame 2's head), the gestures their own (his face acts); the approved are copied to `assets/source/people/husband/`
(`stand.png` the idle's first frame). Speeds in `tools/cast.py`: idle 4, wave 6, laugh 8, give 6, eat 5 a second.
`tools/fetch_people.py` leaves him alone (`BY_HAND`).
