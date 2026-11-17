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
| `paper-tent/` | 4a, first version (approved as a clip, then dropped by the user once seen in the game, 2026-11-16): a paper slid her way, she sits down hard and it flutters over her head (a tent) | animation `paper-tent-end` of her base character, v3 from `paper-start/start-4a.png` (her own standing sprite) toward `end-4a.png` |
| `paper-blanket/` | 4b, first version: onto her belly, the paper floating down in front of her onto her back | `paper-blanket-end`, v3 from `start-4b.png` toward `end-4b.png` |
| `paper-blanket-behind/` | 4b, the same with the paper coming from behind her (the user's pick of the two; in the game in this commit, then dropped with 4a) | `paper-blanket-behind` |
| `paper-behind-sit/` | **4b in the game (approved 2026-11-17; frames 2 to 10, the first three quicker):** the paper slides in from behind under her heel, her leg kicks up forward with it on her sole, she sits down hard, it circles over and lands on her head as a tent (the user's brief: from behind, on her bottom) | `paper-behind-sit-1`, v3 from `start2-4a.png` (her standing on the sliding newspaper B at 10 px) toward `end-4a.png` |
| `paper-front-belly/` | **4a in the game (approved 2026-11-17; the same):** the paper under her front foot skids it back, that leg flies up behind her, she topples onto her belly, the paper carried up and dropped on her back (the user's brief: from the front, on her belly) | `paper-front-belly-3`, v3 from `start2-4b.png` toward `end-4b.png` |
| `paper-front-kick/` | Not used: the first try at the one above, the leg kicked up in front | `paper-front-belly-1` |
| `paper-start/` | The pictures the paper clips were made from: her own standing sprite in an 80 px frame (`start-*`; `start2-*` with the sliding newspaper under her foot), and the targets (`end-*`: the first stills shrunk to her size) | made here |

The first two stills of the paper gags (states `7902a37e-18bc-40f0-a669-a788ff8dadfd` "Paper tent" and
`71676d85-d4ae-466c-8b6e-d3cdbf5545ca` "Paper blanket") came out a quarter bigger than her (the user saw
it at once); they are only the targets, shrunk, for clips made from her own sprite, which keep her size.
The sliding newspaper's candidates are in `assets/source/things/newspaper-sliding/`.

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
