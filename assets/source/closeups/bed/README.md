# Bumbot's bed seen close, the day after (§4 2.4, the user's, 2026-11-22)

On the day after, E by Bumbot asleep on cabin 8206's bed (from the floor) makes him purr and shows the bed over the whole
screen: him lying on it and round him his eight things (massage gun, car, collar bell, feather toy, snack tube, tennis
ball, wool, sardine tin), each from the moment it is found; a thing not found yet leaves bare bed (the user's choice:
"seen close, like the desk"; the room has no space for them at the game's size, the bed's reading spot kept free).
On the bed E is her reading, as before.

- **Him:** cut out of the user's photos (`reference/photos/Bumbot/`, git-ignored, never committed; only the cut-out was
  sent): first `2026-07-17 17.19.17.heic` (lying, a loaf) with his eyes shut (fur over them, a lid's curve), then, the
  user's choice, `2026-07-04 17.04.51.heic`, lying stretched out, his eyes open (the user: "why not leave them open?"),
  turned to face right as he lies on the bed in the game.
- **The bed:** drawn in code in the cabin's colours (the bed's top and front, the teal runner, the grey and teal
  cushions, the pillow, the window's lower part with its curtains and sill); his eight are their close-ups shrunk
  smoothly.
- **The layout is the user's**, step by step: him smaller; the ball and the wool in a row of their own right of his
  face, above the car; his tail over the runner's right part; the massage gun bigger, its handle on the runner's left
  edge; the car, the bell and the tin on the front row with the feather and the snack, 12 px apart.

PixelLab `image_to_pixelart`, 400 x 225, from each rough sent at 2x (1 generation each, 9 in all):

| Rough | Try | Settings | Job |
|---|---|---|---|
| `rough.png` (photo 1, eyes shut) | `try1.png` | default, seed 11 | `bf3a152c-8def-4360-b164-00792447ce50` |
| | `try2.png` | default, seed 22 | `7c260860-26fa-4cb2-be88-a890237922eb` |
| | `try3.png` | faithful 150, seed 33 (the user's pick of the three) | `22566c0d-6f22-4402-bcc0-cc2330009806` |
| `rough-photo2.png` (photo 2, eyes shut) | `try-photo2-shut.png` | faithful 150, seed 33 | `c0bfb52c-0be2-4ae5-9a7d-25b5a58911de` |
| `rough-photo1-open.png` | `try-photo1-open.png` | faithful 150, seed 33 | `48f34fc0-5308-4c44-8060-295d09de27e3` |
| `rough-photo2-open.png` | `try-photo2-open.png` | faithful 150, seed 33 (the user's: photo 2) | `0f33a5df-be43-49da-9a9a-7620a05fff14` |
| `rough-photo2-left.png` (his tail over the runner) | `try-photo2-left.png` | faithful 150, seed 33 | `586ca993-02f6-45d2-857e-9ba410c69862` |
| `rough-photo2-v2.png` (the gun bigger, the front row) | `try-photo2-v2.png` | faithful 150, seed 33 | `16e82e99-7cca-4392-9ff2-8a60a69aa9a4` |
| `rough-photo2-v3.png` (the gun's handle on the runner's edge) | `try-photo2-v3.png` | faithful 150, seed 33: **chosen** (asset `86c43549-b294-5cb4-96dc-5bc3b9a992ae`) | `99945179-5699-4425-b993-3e2752598899` |

`rough-photo2-v3-bare.png` is that rough with none of the things, kept for comparing.

- `full.png`: the chosen try, its empty last row filled from the row above.
- `bare.png`: him on the bed with none of his things, by rule (`bare_bed` in `tools/build_desk.py`): along the row as the
  desk's, but under the gun the runner from its own pattern 48 rows lower; above the bed's top the cushions and the
  pillow straight down; their bottom edge from the nearest open column of the same thing.
- `<thing>.png`: each thing alone on the whole canvas (its box 2 px wider all round, as its light rim shares the bed's
  colours; specks the redraw put round a thing kept with it). `layout.json`: each one's box.

All by `python tools/build_desk.py`; the bare bed with every piece over it is `full.png` exactly. The game's copies:
`assets/ship/bed/`.
