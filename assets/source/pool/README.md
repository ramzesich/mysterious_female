# The pool's scene: sources and jobs

Deck 11's first pool: near-catch 5, the drain, the hatch (docs/pool-remake-log.md). Built by
`python tools/build_pool.py` into `assets/ship/pool/`.

## How it was made

1. `src/`: the game's own pictures of the three places at 1:1 (Phaser's snapshot, halved), with what the scene
   moves hidden (Bumbot, the old lever, her, the kid): the deck between the two pools (`gap-full.png`), the first
   pool's tank dry (`tank-drained.png`), deck 10's hallway under it (`hall.png`); each with its view's corner in
   world px (`.json`).
2. `python assets/source/pool/roughs.py` draws each new piece flat, by rule, into a crop of its place (`rough/`,
   each with its `-base.png`, the place without the piece; `rough.json`, each crop's corner in the world).
3. Each rough was redrawn by PixelLab's `edit_image_pro_flash` into `gen/` under the same name ("Keep this whole
   picture exactly as it is ... Redraw only the rough ... as detailed, polished pixel art ... exactly where the
   rough one is and the same size").
4. `python tools/build_pool.py` cuts each piece by what differs from its base inside its box, drops what is not
   joined to it and what is the sea's colour, fills its holes, and writes the pieces with where each stands.

The lever's arm is not the generated one: at knee height that is a hair's width. The build takes the stand without
it and draws the arm by rule in the picture's own tones, at each frame's angle.

The kid's water pistol (light green with blue lines, the user) is not in this folder: it is repainted in his own
source frames as they are built (`tools/build_people.py`, `"repaint": "pistol"` in `tools/cast.py`), no generation.

## Jobs (PixelLab, 2026-11-24)

| Picture | Tool | Job | Generations |
|---|---|---|---|
| `gen/lever-up.png` (seed 3; the knee-high lever, the user's size) | edit_image_pro_flash | `0c7304d8-fd33-4346-8402-79cf1cfd2e33` | 6 |
| `gen/hatch-shut.png` (seed 5) | edit_image_pro_flash | `d525bcf6-0650-4f97-92b1-36d01066c53f` | 6 |
| `gen/hatch-open.png` (seed 5) | edit_image_pro_flash | `c5b6968d-37fb-4a5f-ad5d-450c690afec9` | 6 |
| `gen/aft.png` (seed 5: the drain's grate) | edit_image_pro_flash | `e90b2a5e-44bc-4e4b-8096-7c9a002f0fe8` | 6 |
| `gen/ceiling-shut.png` (seed 5) | edit_image_pro_flash | `d40a9c90-6cac-4595-b3b7-24997e8f73ef` | 5 |
| `gen/ceiling-open.png` (seed 5) | edit_image_pro_flash | `e87b76a9-0324-4a8c-bf50-abab5c0cfad9` | 5 |

## Tries (`tries/`)

| Picture | What | Job | Generations |
|---|---|---|---|
| `lever-up-big.png` | the first lever, its grip 46 px over the deck: "way too big. It should be at least half a height" (the user) | `93a1d22a-f953-4886-be2c-dccdf82ed025` | 6 |
| `lever-down-big.png` | the same thrown: the generator drew another stand, so a state is one picture plus the part that changes | `723d777d-49b9-4228-984f-66f234567095` | 6 |
| `lever-stand-big.png` | the first lever with its arm taken out by a second edit | `e8905131-c1ad-4b7c-a8a5-a5821187c88d` | 6 |
| `lever-up-seed11.png` | the knee-high lever, another seed: a wider cap, not used | `85fb266b-3987-4269-add3-d0d3d74ea63e` | 6 |

**All of it: 58 generations.**
