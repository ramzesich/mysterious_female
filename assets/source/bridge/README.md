# The bridge's forward end: near-catch 6's own art (2026-11-25)

The pieces and the clips of near-catch 6 as remade (`docs/near-catch-6-remake-log.md`). Built by
`tools/build_bridge.py` (the pieces) and cut by `cut.py` (the clips).

| File | What |
|---|---|
| `src/forward.png`, `.json` | The game's own picture of the place (Phaser's snapshot halved; the console, the helm and the alarm panel hidden, no figures, the decks' dim off), its world origin |
| `roughs.py`, `rough/` | The pieces drawn flat into that picture (`hatch-open`, `station`), each with its `-base` (the place without it), `rough.json` their world origins; `place.png` the place with the cut-away's soft edge taken off |
| `sets.py`, `sets/` | Green copies of the place for the clips made on it: its shapes kept, every colour a green by its lightness |
| `starts/` | The sheets' frames the first clips start from, on a plain green |
| `tries/` | Everything PixelLab returned, frame by frame |
| `cut.py`, `clips/` | The clips cut out of their grounds, each frame on its own canvas; `clips.json` says how a canvas lies in the world |
| `storyboard.py` | The storyboard on its clock: every moment a function of T, composed from the pieces as built and the clips as cut |

## The jobs

| Try | What | Job | Generations |
|---|---|---|---|
| `hatch-s1.png` | `edit_image_pro_flash` of `rough/hatch-open.png`: the escape hatch's collar, its lid hung down, its ladder. **Used** (the collar whole; the ladder one clean period repeated; the lid drawn by rule in its tones) | `43896948-013c-4160-82c9-fd4a3c22581f` | 6 |
| `station-s1.png` | `edit_image_pro_flash` of `rough/station.png`: the alarm station. **Used** | `4ff1704a-d120-4820-a499-a3518dba93d5` | 5 |
| `call-s3-*` | PixMiniMax, 8 frames from her stand: down onto her heels, a hand held out palm up. **Used** (`her-call`) | `2ad96030-bbf4-442c-ba1d-6d3dc9f82518` | 1 |
| `call-s17-*` | the same, another seed: her hand lower, less of an offer; not used | `20cd7a0d-680d-439c-bc93-9b5ea7851b56` | 1 |
| `callloop-s5-*` | 8 frames from the call's last frame, pinned to it: beckoning, her fingers rubbing. **Used** (`her-call-loop`) | `b58089f1-e619-4ebf-aff8-be77aa54d814` | 1 |
| `callup-s5-*` | 8 frames from the call's last frame to her stand: startled, up onto her feet. **Used** (`her-call-up`) | `1e93b69c-b527-4682-bf9e-a2353d73f2f8` | 1 |
| `stalk-s3-*` | 8 frames from the officer's stand: onto tiptoe, the net raised, frozen mid-step. **Used** for its last frame, the pose the rest start from | `ebe45f34-a4e8-44cf-8236-2e3ef4bc91cd` | 1 |
| `stalk-s17-*` | the same, another seed: the net straight up; not used | `a14cda63-bfce-4351-b74b-fa90b24d7e50` | 1 |
| `stalkloop-s5-*` | 8 frames from that pose, pinned to it: frozen, wobbling. **Used** (`rival-stalk`) | `91da1751-28d0-45ee-98aa-b0e002b42e46` | 1 |
| `creep-s5-*` | 8 frames from that pose, pinned to it: two tiptoe steps; his planted foot slides back 5.3 px a frame (42 px a loop). **Used** (`rival-creep`) | `0c144e6c-ff8e-4558-8b0a-6b79d08400e3` | 1 |
| `netted-s2.png` | `edit_image_pro_flash` of his seated frame: his own net over his head. **Used** as the end the main clip is pinned to | `ec220fd1-c68a-4e4f-93b6-68fef3bcffb9` | 6 |
| `netted-s9.png` | the same, another seed; not used | `503f1b39-aa31-4640-ac00-9da0b194b73a` | 6 |
| `swing-s4-*` | 24 frames on the green set, from the pose at 1945 to that end: the swing onto the station's button, the net stuck, the tugs, free, the fall, his net over his head. **Used** (`rival-net`) | `08425d5c-d04f-41e5-a547-983515625833` | 3 |
| `swing-s21-*` | the same, another seed: the net jumps from the station to his head in one frame; not used | `772150cd-05e3-414a-a9cf-4db7d27c45a5` | 3 |
| `climb-s4-*` | 16 frames on the green set (mirrored), from Bumbot's run on the console: onto the ladder, up it paw over paw seen from behind, into the hatch. **Used** (`bumbot-climb`) | `cfe0afbe-5df9-42ce-bd54-8a6a916ae585` | 1 |
| `climb-s21-*` | the same, another seed: red specks in five frames; not used | `45fb4bce-db36-4e6c-9749-591921719ccf` | 1 |
| `netted-loop-s6-*` | 8 frames from the main clip's last frame, pinned to it: one long sigh. **Used** (`rival-netted`) | `82519eed-aab3-4cc4-8f3e-19f8d641f511` | 1 |

40 generations.
