# The popups' sources (the Refinement session, 2026-11-20)

The user: "we're refining the looks of every popup in the game ... a nice framing, and differentiate
between [speech] bubbles and thought clouds". Built by `tools/build_popups.py` into
`assets/sprites/popups.png` + `.json` and `popup-layout.json`; where each picture's head is, by
`tools/build_heads.py` into `assets/sprites/heads.json`; shown by `src/popup.js`.

## `tries/`: every generated candidate (PixelLab, Resurrect 64)

| Folder | What | Job | Cost | Kept (index) |
|---|---|---|---|---|
| `speech/` | Speech bubbles, 64x48, 16 tries (`create_image_pro`) | `d898907d-69dd-4d5c-aa3a-6f9b75280ff6` | 10 | 8 (the sheet's 9), its tail taken off |
| `thought/` | Thought clouds | `9f5ea1b3-36f0-4217-8b8e-55d300b4f675` | 10 | 9 (the sheet's 10), its two circles apart |
| `shout/` | Shout bursts | `61c638ad-f8f1-4d15-a868-2a75bc715c76` | 10 | 1 (the sheet's 2: 15 was picked, but its tail had to go, the user: "Remove the tip from her cry") |
| `plate/` | Navy and brass hint plates | `cfc02420-9cef-4362-a298-e9016b02a4bf` | 10 | 0 (the sheet's 1) |
| `icons/` | 20 icons x 3 tries, 18x18 (`create_1_direction_object`, object `ef49adfc-3bbf-435b-971c-1baa19c1dbaf`) | | 10 | `ICONS` in `tools/build_popups.py` |
| `space/` | A space bar key cap, 32x16, 64 tries | `afd46f9e-0a5b-459e-a3bd-2a797292b74c` | 10 | none: the keys are all stretched from the square key cap, so they match |

`*-sheet.png` show each folder's tries numbered from 1.

## `font/`

Galmuri9 by Lee Minseo (quiple), version 2.40.3 from npm `galmuri`, SIL Open Font License 1.1
(`OFL.md`, no reserved font name): a subset (Latin, Cyrillic, punctuation, arrows) made with
`pyftsubset`. Set at its own pixel size, 10; the game ships only the glyphs drawn from it.

## `heads/estimates.json`

PixelLab's skeleton estimates (`tools/estimate_skeleton.py`, 0.1 generations a frame) of every frame
of hers (her sheet, the towel turban's, with Bumbot, her mishaps, the gags, the towels') and of the
people with a wish: only the head's points (eyes, ears, nose), as fractions of the frame. Kept so
that nothing is estimated twice; `python tools/build_heads.py --from <folder>` adds a new run.
