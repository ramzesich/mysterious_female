# Her start back, and her look up (near-catch 3, remade 2026-11-24)

On the Stardust's stage she starts toward Bumbot on tiptoe (near-catch 2's `creep-tiptoe`); as the rival bursts out
of the wing ahead of her she starts back, and when Bumbot is gone up the fly rope she straightens and looks up after
him (`docs/near-catch-3-remake-log.md`). Both clips are her own character's ("Bumbusik (final)",
`ebd5dadc-1318-4717-b0c0-6f429a7a58f0`), east, skeleton-v3 with poses written for it (`assets/source/stage/scripts/
poses3.py`), as her tiptoe and her shrug were.

| Folder | What | PixelLab |
|---|---|---|
| `start-back/0..7.png` | 8, one way, held: from the tiptoe's pose (hands in front, a lean of 9 degrees) back onto her heels, a step back, her hands up by her face, leaning back 13 degrees, then settling | animate_character, mode skeleton-v3, group `a61034fe-3664-47c6-b9e9-42033fde2d34`, 3 generations |
| `../look-up/0..7.png` | 8, one way, held: from that pose she straightens, her hands down, her head back (the engine kept it to its limit) | the same, group `44fd961d-0da4-4a82-abe6-77b41015aac7`, 3 generations |

Checked frame by frame beside her standing sprite: her height (57 to 59 px), her hair and face, both feet in every
frame. Built by `tools/build_sprites.py` (`start-back`, `look-up`, each frame on its lowest pixel); upright frames, so
`tools/build_heads.py` finds her head by rule.
