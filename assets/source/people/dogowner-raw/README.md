# The dog on a lead and its owner, made together (deck 4, 2026-11-17)

The user: "the lady and the dog are loosely connected, the leash looks weird and glitches on its
connecting ends ... regenerate them together". The mechanic is kept (the dog strolls, fetches a
tangerine, trips her); the pictures are new. 47 generations.

**The frames the game uses are in `../dog/` and `../dogowner/`, kept by hand** (`BY_HAND` in
`tools/fetch_people.py`: a fetch would put the characters' own clips over them).

## Used

| File | What | PixelLab |
|---|---|---|
| `east.png`, `south.png`, `west.png` | The two together: the owner holding the lead's loop, the dog sitting at her feet (approved) | pro character in the cabin maid's style, `dddf2b55-1eaa-44ca-a309-48a637f7ecf6` (10) |
| `owner-cut.png` | The owner alone, the dog and the lead below her fist taken out by hand: `../dogowner/stand.png` | |
| `dog-sitting-cut.png` | The dog alone, the lead across its neck taken out by hand, one px of its neck blackened (the user) | |
| `dog-standing-raw.png` | The approved dog redrawn standing on all four legs | `edit_image_pro_flash`, job `2079a706-6476-427a-b1b9-a1ee0b72b5ea` (5) |
| `dog-character-east.png` | The dog made a character from it (Pro rotate, quadruped, the dog template): `../dog/stand.png` | `be63988d-bf91-4122-a1da-eecd4fa4b65b` (10) |
| `clips/owner-idle/` | Her breathing, her fist still on the lead in every frame (0 is the start picture; 1 to 8 are `../dogowner/idle/`) | PixMiniMax, `2a790a39-a5d8-40fb-b6f1-824123bf97e8` (1) |
| `clips/dog-walk/` | The dog walking, from its standing picture (1 to 8 are `../dog/walk/`) | PixMiniMax, `3e17e35e-a00e-4c2c-9631-07f317d3a00f` (1) |
| `clips/dog-run/` | The dog running: `../dog/run/` | the dog template `running-6-frames` in skeleton-v3 on `be63988d`, group `d2e58583-cbbe-4c1d-af27-810f0860003f` (3) |
| `clips/dog-sit/` | Sitting down, from standing to the approved sitting dog as the end frame: `../dog/sit/` | PixMiniMax, `7a5fbe32-2dd8-4a73-8622-ba82c00b5847` (1) |

## Tries not used

| File | PixelLab | Why not |
|---|---|---|
| `tries/map-object-a.png`, `-b`, `-c` | map objects `7f94e2ff-5c55-4004-a82c-09cee9c7f9ab`, `2ae106ff-52f7-4133-a1fc-2ca60f7707e0`, `6085a9cb-0cd2-44a0-90f2-6bbe5ea06002` (3) | a grey and a white silhouette, no face; a third half her height: map objects don't draw people |
| `tries/dog-proflash-try-east.png` | `create_character_pro_flash`, dog template, the approved dog as its style image, `c207c3c9-8691-41e3-8b0c-47b7dc73beba` (6) | long and thin, stretching, its white grey-green |
| `tries/dog-template-walk/`, `-run/`, `dog-v3-sit/` | template clips and a v3 sit on `be63988d` (3, deleted on PixelLab) | the template redrew it as another dog (no patches, grey ears); the "sit" never sat |
| `tries/dog-skeleton-walk/` | skeleton-v3 `walk-6-frames` on `be63988d`, group `9073ad48-106e-4ec7-957a-71790a1618df` (3) | its body a third longer than the standing dog |
| `tries/dog-pixminimax-run/` | PixMiniMax, `3fd1957a-c231-4108-a50c-dbd81879489a` (1) | three of its frames near standing: it would stutter |

The first dog (step 4), kept on PixelLab: `0e7afef8-f85d-44da-913d-16d81826d998`; its owner was the
`railwoman` figure, who stays in the cast.
