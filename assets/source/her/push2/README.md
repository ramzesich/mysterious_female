# Her push, remade (2026-11-18)

The user: "her legs do not move properly when she's pushing" (her first push, `../push/`, shuffled her
feet about 2.5 px a frame while the cart rolled 6.7: her shoes slid on the carpet).

- `start.py`: the start picture, her built push frame 0 against the steward's trolley as the game sets
  them (her middle 29.5 px from its middle), feet on row 120 of 128.
- PixMiniMax `animate_image_pixminimax`, job `64b519f5-ad1f-48f1-bcee-db00faf9ab91` (1 generation,
  8 frames, pinned back to the start picture so that it loops); its frames in `raw/` (`a-0` is the
  input, `a-8` the pinned end).
- `clean.py`: the trolley taken out of every frame by its own picture, loose specks, each frame on the
  floor line (frames 5 to 7 sat 1 px up), written as 84 px cells, `0.png` to `7.png`: what
  `tools/build_sprites.py` builds as `push`.
- Two even steps: the planted foot slides back about 3.6 px a frame, so the game plays it at 11
  frames a second with `VERBS.pushSpeed` 40 px/s (it was 9 and 60).
