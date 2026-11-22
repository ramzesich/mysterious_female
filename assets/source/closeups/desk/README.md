# Cabin 8206's desk seen close (§4 2.4, the user's, 2026-11-22)

E at the desk in cabin 8206 shows it over the whole screen: her four things (flag, plant, bookmark, diary) and his four
(t-shirt, sleep mask, handheld, pick), each from the moment it is found; a thing not found yet leaves bare desk (the
user's choice of three). The room could not hold the eight at the game's size (the user's choice: "seen close at the desk").

- `tries/rough.png`: the layout, made of the close-ups shrunk smoothly on a desk drawn in code, the TV's lower part
  centred over it (the user's: the first of two roughs, then "the TV ... more like a TV and centred", "only the bottom
  part of it"). Sent at 2x.
- `tries/try1.png` to `try3.png`: PixelLab `image_to_pixelart`, 400 x 225, from the rough (1 generation each):
  - try 1, default, seed 11: job `a94dfb99-a43a-4ea7-b908-701f711717ab` (asset `b9a718b1-69f5-5f99-bc41-7b773392d41a`): **chosen**
  - try 2, default, seed 22: job `7263c504-6dab-4390-b0cd-5172cdb59d91`
  - try 3, faithful 150, seed 33: job `7950a2e6-03c3-49cd-b2cd-59c2d8f006c5`
- `full.png`: try 1 mended (two stray marks on the mask); `bare.png`: the desk alone, by rule (its surfaces are flat
  colours); `<thing>.png`: each thing alone on the whole canvas; `layout.json`: each one's box. All by
  `python tools/build_desk.py`; the bare desk with every piece over it is `full.png` exactly.
