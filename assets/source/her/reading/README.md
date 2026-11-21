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
| `chair/`, `bed/` | The cut frames (her alone): what differs from the start without her, the holes her outline encloses filled, her figure only; on the bed the wall picture's redrawn wisps over her hair dropped | |

Used by `Library.read()` (`src/world/library.js`): the chair's frames 0 to 4 she sits down (4 held while she
chooses), 7 to 13 she opens the book (5 and 6 left out: red streaks down her front as the book took shape; a stray
speck over her head is not in the cut); the bed's 0 to 3 she sits down, 4 to 9 she opens the book. Both 2 generations.
