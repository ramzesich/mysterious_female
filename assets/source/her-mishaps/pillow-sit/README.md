# Her gag under Splash Academy's pillow (26; 2026-11-27)

The pillow lobbed over the castle comes down on her head and she plops down; the user: "the same exact pose, as when is
hit by a running kid. Only with the pillow on her head".

- `start.png`: her built stand (`assets/sprites/her.png`) with the world's pillow (`assets/source/things/splash-pillow.png`)
  over her head; `end.png`: her dazed sit's first frame with the pillow where the game sets it on her head (her heads).
- `raw/`: PixMiniMax from `start.png` toward `end.png`, 12 frames, `26d245e4-9997-41e8-abb3-a0fe72150e4c`, 1 generation.
- `sit.png`: the frame a kid's hit shows, the swaying sit's first (`her-dazed-sit-plain`'s frame 1), with the pillow on
  her head: frames 10 and 11 of the gag (the user, frame by frame: "10 and 11 should be the frame from the kid hit";
  `end.png`, the sit the dazed clip starts from, was not it). Frame 8 two px higher than its lowest row on the floor, 9
  by its lowest row ("8 and 9 she should touch the green line with her bottom"); the generator's last frame left out.
  Built by `tools/build_sprites.py` (`HER_MISHAPS`), played by the ship scene's `fallGag`, then her own
  `her-dazed-sit-plain` with the pillow on her head (`GAGS.pillow`: `sit`, `hat`; `wearHat`).
- `first/`: the first try (`575424d5-832f-4d98-9b6f-2726581da581`, 1 generation), toward a sit of its own with a smaller
  pillow: her seat hovered over the floor; unused. Head estimates 2.4 generations.
