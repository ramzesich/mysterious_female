# Her creep: on tiptoe, and her reach at chest height (near-catch 2, remade 2026-11-24)

In the Library she creeps up on Bumbot asleep on the return trolley and reaches for him at his height (the user's
choice of three ways she could go for him; `docs/near-catch-2-remake-log.md`). Both clips are her own character's
("Bumbusik (final)", `ebd5dadc-1318-4717-b0c0-6f429a7a58f0`), east, skeleton-v3 with poses written for it, as her
shrug was: her look holds, and the pose is what was asked.

| Folder | What | PixelLab |
|---|---|---|
| `creep-tiptoe/0..7.png` | A loop of 8: two small steps on her toes (each foot 0.10 of the figure's box from front to back while planted, lifted 0.03 coming forward, feet and pelvis 0.012 up), her hands held up in front, elbows down, a lean of 9 degrees. Her planted toes slide back 1.6 px a frame: at 18 frames a second she moves 29 px/s (`QUIET.tipFps`, `tipPx`) | animate_character, mode skeleton-v3, group `d327f239-a1ed-4f5e-b898-2e2b48927a0a`, 3 generations |
| `../creep-reach/0..7.png` | 8, one way: from the creep's hands out to arm's length at chest height (wrists 0.235 forward, 0.19 up from the pelvis), leaning in 18 degrees on her toes, held. Her hands end 24 px ahead of her middle, 38 to 44 px over the floor. Played back from its fifth frame to straighten (`her-creep-back`) | the same, group `83b7dde0-282d-48c0-a124-0c8362a689e8`, 3 generations |

Checked frame by frame beside her standing sprite: her height (59 px), her hair and face, both feet in every frame,
her hands; the scarf is behind her forearms in the creep. Built by `tools/build_sprites.py` (`creep-tiptoe`,
`creep-reach`, each frame on its lowest pixel); upright frames, so `tools/build_heads.py` finds her head by rule.
