# The HUD's pictures (the user, 2026-11-20)

Built by `tools/build_hud.py` into `assets/sprites/hud.png` + `.json`; shown by `src/hud.js`. Each kind of
thing to find is counted by a face: Bumbot's, hers, her husband's ("The flower and the guitar are especially
unclear. Have to be faces of Bumbusik and her husband"); the books by the popups' book; the cards by the
popups' card. Every picture but the cards has a light rim (the user: it holds them on any background).

The photos they come from are the user's own (`reference/Bumbot/`, `reference/Husband/`, git-ignored, never
committed); each was cut out onto a flat ground before anything was sent (OpenCV's GrabCut, then by
darkness for Bumbot against the white wall, his ears filled by their hulls, the lit fur between them taken
back by its brightness).

| File / folder | What | PixelLab | Kept? |
|---|---|---|---|
| `tries/bumbot/` | 64 tries of Bumbot's face, 24 x 24 (`create_image_pro`), from his photo (the third, against the white wall) with her front face as the style | `4b998f2d-9679-4a66-96c4-88450317959a`, 10 generations | **#3** (`2.png`): `face-bumbot.png`; in the atlas cut to his outline, the two pixels under his left cheek cleared (the user circled them) |
| `tries/him-photo1/` | 64 tries of the husband's face from his first photo (smiling) | `d05c3313-26be-469a-82cb-c8899581f930`, 10 | none ("they are all bad") |
| `tries/him-photo2/` | 64 tries from his second photo | `637ad802-5903-4843-9895-dc2e5893746c`, 10 | none |
| `husband/` | **Her husband's character** "Her husband (pyjamas)", a pro character in the cast's style (`style_character_id` the drill's officer) designed from his first photo: his pyjamas, a navy top with a bear on it wearing the same checked pyjamas, checked trousers ("an inside joke": he wears them at the table and in the cabin). Rotations `south`, `east`, `west`, `north` | character `a1ebd48e-3b9f-40fd-b2d8-e737d4981bba`, 10 | **Approved** ("I like my sprites"); **not yet in the game** (the stand-in diner still sits at the table) |
| `husband/south-bear-raw.png` | The bear on his chest, `edit_image_pro_flash` of the front view | `6780d6a9-0234-404e-af0a-9dbdc39d08c7`, 5 | its bear only (the rest of the edit had changed 85 faint pixels of his face and hands) |
| `husband/short/` | His four views with one row of his forehead out, as on the icon (`shorten.py`; the user, 2026-11-22); imported as the character `5b85cf25-df58-47e2-b592-affd32aff145` his clips are made from (`assets/source/people/husband-raw/`) | 0.25 | **Approved** |
| `husband/south-bear.png` | His front view with the bear: the original everywhere, the edit's 13 x 17 px chest, the bear's pyjamas set to his trousers' even check (the user: "make it even, like on my trousers") | | **Approved**: his HUD face, cut from it (head, shoulders, the bear's head), one row of his forehead out (the user) |

Not kept: a first set of Bumbot's face from his game sprite (`bb7660d3-48e5-40e5-91f3-9bcca76269a6`, 10) and
one from a cut-out that was not clean (`213cce31-8ac8-4c5d-b09e-b34fcc8652d5`, 10): his sprites are to be made
again from the photos, and the cut had a notch in his head (the user saw it). Her face is her own front view
(`assets/source/her/rotations/south.png`), no generation. The ∞ for `?tangerines=infinite` is drawn in the
builder (the lettering has none). 65 generations in all.
