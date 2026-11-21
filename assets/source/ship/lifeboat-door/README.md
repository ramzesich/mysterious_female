# The lifeboat's way in (the boat walkway, deck 7; the user, 2026-11-21)

The lifeboat at 143 m is entered through a hatch on its roof: she pulls herself up over its far rim from behind the boat
(the walkway is on the boat's far side), turns on the roof and sinks into the opening; inside, a ladder. Built by
`tools/build_hatch.py`; played by the ship scene's `roofClimb` / `roofOut`.

| File | What | PixelLab job |
|---|---|---|
| `crop.png`, `mask.png` | The boat's left 128 px on the recess's grey, and a mask at its old side door: for a fitting door (dropped before it was tried: "Wait, I have another idea") | |
| `crop-top.png`, `mask-top.png` | The boat's columns 40 to 168, and a mask on the roof just aft of the forward hook | |
| `hatch1.png` | A low hatch, its red lid open at an angle (the user's first choice; then too narrow to read as a hole) | 09c2a840-4d5e-4d1b-b991-90a21df7ff9b |
| `hatch2.png` | A round hatch, its cover upright | 9e21d561-40b9-43a4-a7a9-9c202198e87b |
| `hatch-piece.png` | `hatch1.png` cut by what changed (dropped) | |
| `mask-top2.png`, `wide1.png` | A wider hatch seen a little from above, a plain lid | c962ce6a-7b20-4a04-bd56-f781d3421f0e |
| `wide2.png` | **Used**: the wide hatch seen a little from above, its framed lid upright behind the opening | 4d0f8921-7748-49b9-8b2f-61fa60fcf972 |
| `nolid.png`, `nolid-back.png`, `nolid-front.png` | **Used**: `wide2.png` with its lid taken off (the user: "Remove the lid from the hatch"), a far rim mended in its own colours, cut into what is behind her and its near lip (`assets/source/things/lifeboat-hatch-back.png`, `-front.png`) | |
| `climb-*.png`, `a-*.png` | Start and end pictures for the generated climbs below | |
| `raw-side/`, `raw-front/` | Dropped: generated climbs from behind the boat, side-on / facing us; her outfit wrong | 1acc597b-a0ed-495d-9280-88415cf2d8bb, d4a7ace9-a337-41d9-b3c7-13211b6680e2 |
| `raw-front2/`, `raw-front3/` | Dropped: the same with her outfit described; she came up aft of the hatch | 7cd44572-15d6-4260-99c7-65c98bc3bb29, 74555346-8985-4c13-bc60-54bbed52b0da |
| `raw-hatch1/`, `raw-hatch2/` | Dropped: up at the hatch and down into it; it read as going down behind the boat, her face grey | 022ce85f-66bb-4a66-a9c2-23bba99c9377, 143ff4b7-80ac-4c41-a0a7-3fcb6e2e0ba1 |
| `raw-a1/`, `raw-a2/` | Dropped: up facing us and turning her back (on green); another drawing than her sprite, every joint broke in the game | 6b60d1b1-cc4d-45d8-b739-e746c6571a8a, 7ab7e3cb-5cfa-4214-90a4-3440436c0dc3 |

Her own character's clips (`assets/source/her/`, PixelLab character "Bumbusik (final)"):

| Folder | What | PixelLab |
|---|---|---|
| `climb-front/` | Dropped: skeleton-v3's `climb` move facing us, in place: her hands climbed the air | group f9223ed7-5c88-4c43-8aa2-5cdb0d393ead, job 9d333d00-0bb8-4c9b-9d1e-6aebfc6bb1f3 |
| `mantle-front/` | **Used**: skeleton-v3 with written poses, facing us: her hands from by her face down to her hips, a knee up; the game holds her hands on the hatch's far rim and moves her body from them | group fa1f5c42-f019-42b6-a2bd-d73cbe07b3cd, job 07fa7583-24a3-42fb-8d87-8d3cd51fec8e |

The rest of the climb is her own sheet's frames (front, side, back; `climb-out` 74, 73, 72), approved together as one GIF.
35 generations in all.
