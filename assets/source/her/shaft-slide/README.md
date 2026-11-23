# Her slide down the shaft's slope

Behind the linen room's forward wall the shaft slopes down into the slab between decks 9 and 8
(docs/shaft-remake-log.md). She tips over its lip, slides down it on her front, arms out, and is on her hands and
knees again at its foot: one clip of nine pictures, played by `shaftSlide` in `src/world/world.js` where it was
made.

- `inputs.py` makes the two pictures the clip runs between, on the game's own shaft: `start.png` (her crawl frame
  0 at the lip) and `end.png` (her crawl frame 4 at the foot), and the same on the shaft turned green
  (`green-start.png`, `green-end.png`), with `place.json` (where the picture stands in the world).
- `green-raw-0.png` to `green-raw-8.png`: PixelLab's `animate_image_pixminimax`, 8 frames, first and last frame
  pinned, seed 3, job `c644109e-12e5-4171-9d8e-632eb3d6abc3` (1 generation). "She crawls forward over the edge,
  her hands slip and she slides down the slope head first on her front, arms stretched out ahead of her, legs
  trailing behind, hair streaming back, staying inside the green duct along its sloping floor; at the bottom she
  comes to rest on her hands and knees. The green duct does not move or change."
- `raw-0.png` to `raw-8.png`: the same asked on the shaft in its own dark steel, job
  `3ce197d2-564b-4ca1-8682-c1a28bc0e732` (1 generation). The motion is the same, but cut out of the dark she lost
  her navy skirt and dark hair in two frames: not used.
- `tools/build_shaft.py` takes the green shaft out of every frame (a pixel is the shaft's when green leads its red
  and its blue by 18), drops loose specks, puts her on the palette (her blouse's shade as in her sheets) and writes
  `assets/ship/shaft/slide.png` and `slide.json`.

Checked frame by frame, enlarged: she is whole in every frame, no green fringe, her size as in her sheet; she stays
inside the slope's own lines; frame 0 is her crawl frame as the game shows it at the lip, frame 8 her crawl frame 4
at the foot, where the game sets her down in that frame.
