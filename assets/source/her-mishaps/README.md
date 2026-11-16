# Her mishap gags (docs/plan-three-uses.md §1.6, step 4's revision)

Raw PixelLab output, kept so the sheet `assets/sprites/her-mishaps.png` can be rebuilt
(`python tools/build_sprites.py`, `HER_MISHAPS`). Each gag of her with a thing is one state of her
character "Bumbusik (final)" (`ebd5dadc-1318-4717-b0c0-6f429a7a58f0`) with the thing drawn in
(80 x 80 canvas, 10 generations), then animated v3, east, from that state:

| Folder | What | PixelLab |
|---|---|---|
| `ride-vacuum/` | 5b: her riding the robot vacuum, the state's rotations | state `454fc6c8-07dc-478d-a2e4-1692d7a0f5c0` |
| `ride-vacuum/east-small.png` | 5b: the riding picture with the vacuum made smaller (the user: "it looks too big"): the state's east picture, the big vacuum's pixels taken out, the approved small one set under her, she lowered 2 px (approved) | made here, the start of the two clips below |
| `vacuum-ride/` | 5b: the ride, arms up, hair streaming (frame 0 the start picture) | animation `ride-small-vacuum` of her base character, v3 from `east-small.png` |
| `vacuum-sit/` | 5b: caught at the heels, she plops down onto it | animation `sit-on-small-vacuum` of her base character, v3 from her standing with the small vacuum at her heels (frame 0, not used) to `east-small.png` |
| `ride-suitcase/` | 6b: her riding the runaway suitcase, handle up, the game's colours | state `fe79eecf-34e3-4ce8-b3f9-8419d001ba01` |
| `suitcase-sit/` | 6b: bumped at the knees, she sits back onto it | its animation `sit-on-suitcase`, as the vacuum's |
| `suitcase-ride/` | 6b: the ride, clutching her hands | its animation `ride` |
| `suitcase-tip/` | 6b: at the end of the roll it tips; she lands sitting on the floor | its animation `tip-off` |

The world's own vacuum and suitcase are cut from these same pictures (where she sits on them,
each row filled from its own colours, or the column below it), so that the one that hits her is
the one she rides: `assets/source/things/robot-vacuum.png`, `suitcase-rolling.png`. The vacuum was
then made smaller by taking out its plain middle columns and a plain row of its side (32 x 13 to
22 x 11, nothing resampled), its top line run out to mirror its left end and greyed to `#525460`;
the suitcase keeps the original's rounded corners (all approved by the user, 2026-11-16). The
state's own clips with the big vacuum (`ride`, `sit-on-vacuum`) are on PixelLab, not used.

Tried and not used: a first suitcase state (`56fd2d7c-b0b4-47f1-84ca-334628f115f1`: darker, no
handle, unlike the game's); a map object to complete the vacuum (`18c5fa65-...`: flatter and
lighter than the one she rides).
