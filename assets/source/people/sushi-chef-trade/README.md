# The sushi chef's trade (§4 2.1, thing 7; the user, 2026-11-20)

His clips for Bumbot's tin of sardines, built from `assets/source/people/sushi_chef/{take,give,catch}` and their
backward copies (`take-back`, `catch-back`, `give-back` without the tin), played by `sushi()` and `sushiOffered()`
in `src/world/topdeck.js`. Here, what they came from:

| File / folder | What | PixelLab | Generations |
|---|---|---|---|
| `start.png` | His `slice` frame 0 (88 px), the start of every clip | | |
| `end-take.png` | Edit: his near arm stretched forward at shoulder height, palm up (`edit_image_pro_flash`) | job `64f1c451-af66-4343-b95a-eb67ef6ba1c8` | 5 |
| `end-give.png` | Edit: holding out a small tin on his flat hand | job `94d19b4c-2b29-4b12-8b37-9338d5681515` | 5 |
| `end-give-tin.png` | The same with its tin replaced by the world's (`assets/source/things/sardine-tin.png`) | | |
| `end-catch.png` | Edit: his arm up over his head, the hand closed as on a catch | job `1cd847fa-baa2-411d-8558-4424127078f7` | 5 |
| `raw-take/` | PixMiniMax, start to `end-take` (frame 0 the start) | `65796bbc-95e2-4a72-b592-cdc1a7f25666` | 1 |
| `raw-give/` | PixMiniMax, start to `end-give-tin` | `ac8734ad-f599-4e3d-a327-ca72627e5fa1` | 1 |
| `raw-catch/` | PixMiniMax, start to `end-catch` | `d7827833-df5d-47f7-9668-890b3e23fc52` | 1 |

Mended for `give/`: frame 4 dropped (the tin came up in front of his face), and the generator's tin in frames 5 to
8 replaced by the drawn one, set on his hand where the generator had it. Its colours are kept off the palette in
the people sheet (`own` in `tools/cast.py`). `take/` and `catch/` are the raw frames. The approved composites
were shown over the Sushi Bar's counter at the game's offsets, with the nigiri moved behind him.
