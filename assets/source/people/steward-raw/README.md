# The steward and his jammed trolley (deck 9, region 4; 2026-11-17)

The user found the jammed cart "an invisible wall": a low service cart had stood for a block up to
the ceiling. It is a tall housekeeping trolley now, too tall to hop, and he is drawn with it.
12 generations.

| File | What | PixelLab |
|---|---|---|
| `../../things/tries/steward-cart-d.png` | The trolley the user chose ("4"), mirrored so that its handle faces him | `create_map_object`, e03df2fc-812c-46e1-b898-cbaa1c442dfc (1; the other three below) |
| `pair-start-rough.png` | The rough given to the edit: the trolley and his old `tug` frame side by side | (composed) |
| `pair-pull.png` | Him gripping its handle, leaning back, pulling (approved) | `edit_image_pro_flash`, job 2e5ab61b-4a84-47ab-830d-e4394e89c260 (5) |
| `pair-pull-128.png` | The same padded to 128 px for PixMiniMax | (padded) |
| `pair-tug/` | Two heaves at it, the trolley giving up to 3 px; 1 to 8 are `../steward/tug/` (cropped to 80 px at x 18, y 44, mirrored to face east) | PixMiniMax, a7e8928e-8044-4854-969a-ca0b9b670864 (1) |
| `pair-tugwalk/` | Stepping back as he pulls, in place; 1 to 8 are `../steward/tugwalk/`, cropped the same | PixMiniMax, 8bbc3664-26bf-43e7-9f03-63fa1c3daa39 (1) |
| `toss/` | From `../steward/stand.png`: his hand to his shirt pocket, an underhand toss; 1 to 8 are `../steward/toss/` with the generator's speck taken out (frames 5 and 6) | PixMiniMax, cc81a414-be1a-4997-aa2b-194055ff6590 (1) |
| `tug-before/` | His old `tug`, grabbing at the air 10 px short of the low cart ("twitching", the user) | (the cast's character) |

The world's trolley, `../../things/steward-trolley.png`, is cut from `pair-tug/8.png` on the palette
(the clip's own pixels, so that the hand-over matches), the handle's end under his hands from the
chosen picture. In the game (`STEWARD_TUG`, `STEWARD_HEAD`, `STEWARD_FREE`, `STEWARD_TOSS` in
src/world/story.js): jammed, he plays the picture of the two and the world's trolley is hidden; free,
it stands back against the wall, not solid, and he steps back off its handle, thanks her, and tosses
her his card (`world.tossOver`).
