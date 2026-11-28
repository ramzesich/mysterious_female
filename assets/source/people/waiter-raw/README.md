# The Seven Seas' waiter at his tables (the user, 2026-11-28)

He serves the diners of tables 2 and 4 of the Seven Seas' forward part, clears them on his next visit, and is bumped
into as the lady in her bathrobe is (10f). Built by `serve/cut.py` into `assets/ship/waiter/`.

## The diners (`diners/`)

`edit_image_pro_flash` of the approved Seven Seas pair, "a different person in exactly the same sitting pose and size ...
no chair" (5 generations each); the image ids stand for the characters in `tools/cast.py`:

- `woman-try1.png` (`seas_green`, table 2): a grey-haired lady in emerald with pearls, from `seas_navy`; `4496ae8c-ef80-5615-8418-356d27424f79`
- `man-try1.png` (`seas_burgundy`, table 4): a bearded man in a burgundy dinner jacket, from `seas_white`; `bdec6854-b10d-5e87-ac2d-741e228afe88`

## The serve (`serve/`)

- `game-A.png`, `game-B.png`, `game-C.png`: the game's own picture of table 2 with him and his tray, without him, without
  the table (renderer snapshots, the window's view hidden); `waiter-tray.png`, `table.png` by difference; `start-green.png`
  him on a green copy of the table.
- `mid-try1.png`: the cloche lifted off a plate of food, `edit_image_pro_flash` of the start (6 generations), job
  `72683395-bbce-4d33-aa26-dc8e94cd3a23`; `plate.png` cut from it.
- `end-green.png`: the start with the plate on the cloth, its foot on the row the vase's glass stands on (the user:
  "same level as the flower").
- `raw1/`: PixMiniMax start to mid, 8 frames, `ca24dc41-79e4-4321-8b9e-32c02ebb936c` (1 generation); `raw2/`: mid to an end
  with the plate 2 px higher, unused, `282b2999-ff38-497f-8ab0-cb863364d232`; `raw3/`: mid to `end-green.png`,
  `80f215e3-2ff0-4477-a686-5d3e3692b37c` (1 generation each).
- `clip/`: the frames used (`SEQ`), cut by what differs from the set, streaks and specks out; its first frame the game's
  own picture exactly, its last the start with the plate.

In all 19 generations.
