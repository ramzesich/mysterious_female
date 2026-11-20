# Her throw in the air (the user, 2026-11-20)

"From my perspective as a player: a thrown tangerine never flies high enough to hit the gull. What I would
expect is to be able to throw it while jumping." F in a jump: a toss forward and a little up from her hand
(↑ and F the lob), once a jump, her arc kept (`THROW.air*` in `src/config.js`, `tryThrow` in the ship scene).

- `raw/`: **the clip**, skeleton-v3 from her jump's top frame (`apex` of her built sheet), PixelLab job
  `79b77465-3120-4792-9669-e999281a9fad` (3 generations): only her near arm moves, back, down, forward at her
  chest (the release, frame 3) and back; her legs, skirt, hair and head hold. The skeletons were laid out by
  hand from PixelLab's estimate of that frame (`83bbd9ef-237f-4350-a0d1-1bf6c30840f5`).
- `held/`: the same with the game's tangerine in her fist in frames 0 to 2 (`tools/hold_tangerine.py`, `CLIPS`),
  built into her sheet as `airtoss` (`her-airtoss`, 20 fps, played over her jump for 0.4 s).
- `tries/`: `a` and `b`, PixMiniMax from the same frame (`0d72a59f-ab05-4d71-8a59-1504d00cc222`,
  `5edfe91a-1731-4201-9a7a-fedc32535594`, 1 generation each): both swung both arms and drew red bits flying off
  her; `c`, the first skeleton try (`89dc3c12-59ee-474e-88bb-9867d68524f2`): her hand rose in front of her face.
