# Her reading clips (2026-11-21)

Every place she reads (the user, 2026-11-21: "Generate a proper sprite for her seating facing us in that red chair";
"Generate the sprites where she sits properly on the bed, reading"): the Library's seven armchairs (all the same
chair) and her bed in cabin 8206. Each is one PixMiniMax clip (`animate_image_pixminimax`, 16 frames, 1 generation)
from a start picture holding the game's own chair or bed, so its pixels stay the world's; then cut out of each frame
by what differs from the start without her (`tools/build_reading.py` reads `chair/`, `bed/`).

| Folder | What | PixelLab job |
|---|---|---|
| `raw-chair/` | Facing us, she sits down into the red armchair, takes a book, opens it in her lap and reads. `start.png`: a flat wall, the game's `reading-chair` on the floor line (68 x 68, its foot on the bottom row, its middle at column 34), her front view standing in front of it | 22a754c9-533f-49c2-965e-ea9709579db2 |
| `raw-bed/` | Side-on, facing left, she sits down on her bed up against the pillows, legs along the mattress, and reads a book on her knees. `start.png`: cabin 8206's own picture, columns 108 to 239, rows 28 to 127, her side view standing on the mattress at column 196 | 4f977da1-b14c-4556-a322-295d95b166ee |
| `raw-bed-towel/` | The bed's clip with her towel turban on (after the shower; the user, 2026-11-23: the towel went from her hair when she sat to read). `start.png`: the same picture with her towel look's side view (`assets/source/her-towel/rotations/east.png`, turned) at the very place of `raw-bed/start.png`'s, 0 px apart. Description as `raw-bed`'s, "The towel wrapped round her hair stays on her head the whole time. The room does not move." 1 generation | 1b6edb0b-80c8-4195-a979-bf21784a62d0 |
| `chair/`, `bed/` | The cut frames (her alone): what differs from the start without her, the holes her outline encloses filled, her figure only; on the bed the wall picture's redrawn wisps over her hair dropped | |

Used by `Library.read()` (`src/world/library.js`): the chair's frames 0 to 4 she sits down (4 held while she
chooses), 7 to 13 she opens the book (5 and 6 left out: red streaks down her front as the book took shape; a stray
speck over her head is not in the cut); the bed's 0 to 3 she sits down, 4 to 9 she opens the book. Both 2 generations.

`bed-towel/` is cut by `tools/cut_reading.py bed-towel` (the first two were cut by hand the same way): what differs from
cabin 8206's own picture; the window left out (the generator lit it grey); her pieces joined at corners too (a diagonal
outline is a staircase); over the wall picture her outline closed so the towel's pale inside, matching the picture's
pale ground, stays; grey and near-white px outside her dark outline (closed by 1, or 2 where 1 leaves the towel open,
and shrunk back) dropped: the tufts over the towel as she sits down, the picture's greys flickering in front of it as
she reads, the pillow's white lifted against her back; lone specks over her head; the towel's light blues grey
(`grey_top`). The game plays its frames 0 to 9 as the bed's (frame 10 has a broken turban; not built).
