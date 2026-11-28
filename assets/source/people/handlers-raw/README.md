# The Art Gallery's two art handlers and their painting (part 11's item 10, 2026-11-28)

Two handlers carry a large framed painting to and fro along deck 7's Art Gallery (134.2 to 145.5 m), set it down at each
end, wipe their brows and pick it up the other way; her cry sets it down; bumped into or landed on, they drop it and she
sits dizzy (the user's simplification after the framing gag below, "That doesn't work at all"). Built by
`tools/build_painting.py`; played by `GalleryPainting` in `src/world/movers.js`.

**The method.** Every clip of the two is generated with the painting replaced by a flat magenta panel of its exact shape
(`carry/masked.png`), so the generator moves only them; `cut.py` takes the green and the panel out and records where the
panel is in each frame; the game draws its one painting there. `fetch.py <job> <folder> <frames>` downloads, cuts and
sheets a clip; `sheet.py <cut name>` sheets a cut one with the real painting.

| What | Files | PixelLab |
|---|---|---|
| The older man (grey coat, moustache) | `../handler_coat-raw/` | `create_character` pro `53a2c062-e189-421b-b960-e01a4c3a975f` (10) |
| The younger man (navy apron) | `../handler_apron-raw/` | `create_character` pro `bbf65190-0a32-43ef-8bc2-8d45a396f422` (10) |
| The two carrying it: a rough on green, then an edit (left used; right: his head bigger) | `carry/rough.png`, `carry/e1.png`, `carry/e5.png` | `b857e761-3a28-4054-b36f-aa4be43506bc` used, `4a690cc4-a788-4ef8-8df1-52da344e5544` (6 each) |
| The carry with the panel (`e1.png`, the painting's own pixels magenta, their hands kept) | `carry/masked.png` | |
| Walk right with the painting in it (it was redrawn each frame: unused) | `walk/s1`, `walk/s2` | `d1d12d1c-82dc-470d-9fc3-3c950a94db4a`, `af3152c7-0ddc-449d-a570-e02e87cbf538` |
| **Walk right** (`walkE`) | `walk/m1` (used), `walk/m2` | `1adf18ab-a1e5-47be-a2a0-12c0d8347315`, `3b9c9aed-dbd4-40d0-b6c0-97fce63f58a3` |
| The rest: the panel on the floor, the two facing us from their own front views | `carry/rest.png` | |
| **Set down, right** (`downE`) | `setdownE/s2` (used), `s1` (drifted) | `7480535d-977f-4835-a56b-c79287f32a8d`, `2b91dc17-a0ed-4669-8c6b-c2dfd7e97efb` |
| **Pick up, right** (`upE`) | `pickupE/s1` | `ed91a77b-18e9-49ad-a195-8ce4f7b93635` |
| **Wipe their brows** (`wipe`) | `wipe/s3` (used); `s1` (a face smeared), `s2` | `9ac5d5bf-1d37-4f03-bac5-eff33be08737`; `2d8b68f2-22cc-42bd-b0b2-977610942ea2`, `4dd8cc2e-05db-4ba1-ad70-cb7d3a9999f0` |
| The carry to the left by edits (unused: the apron came out on his back, or the panel changed) | `carry/west-e1.png`, `west-e7.png`, `west2-s1.png`, `west2-s5.png`, `swap-s4.png` | `db325e2a-06c1-472e-b3da-aedd052317ab`, `fbf18a9e-fa08-414f-a5b5-0a56ca8245fb`, `77c27b59-8200-4995-8e08-259c3af39fdd`, `43b07e9e-4aac-4493-9245-a56313f16a7e`, `2876c656-755c-4885-8c4a-9ee4e4edcca1` |
| The carry mirrored, who is who swapped by an edit: the older man as the leader, used | `carry/masked-mirror.png`, `carry/swap-s1.png` | `933a4857-57dd-4dac-b806-4e782614991e` |
| The carry to the left composed: that leader, the younger man from his own left view, the exact panel; then his hands onto it | `carry/west.png`, `grip/g1` (used), `grip/g2` → `carry/westcarry.png` | `f6405fe2-c958-48db-94bf-c6aee3c1de68`, `757356b0-61c7-4688-b176-1b873824660f` |
| Pick ups to the left from the rest, unpinned (too low, walking backwards, too high) | `pickupW/s1` to `s4` | `d8a59412-275f-4d49-97bb-334fdf84adec`, `18fcc13b-6df0-447b-860a-45bb60cd7d7f`, `bbed69e0-f6db-41ec-98ca-dca5fd3fc865`, `bc710c1e-e3be-4ee1-b147-727159f4921d` |
| **Walk left** (`walkW`) | `walkW/s1` (used), `s2` | `7d02f86e-376c-4197-967d-3ac13aba6a1f`, `fc9e01bc-94e4-46f7-bf2e-f6b65ee6ba35` |
| **Set down, left** (`downW`) | `setdownW/s2` (used), `s1` | `15e7ba5e-89ae-4573-b28a-e121de1d4d94`, `7fc2fd61-90e3-403b-97ee-26dcf516d929` |
| **Pick up, left** (`upW`), pinned to the carry | `pickupW/p2` (used), `p1` | `2777974c-dfe8-40a4-8bac-7b5bb89e2542`, `b98443f5-0dbd-43cd-9e02-47ddcc82c333` |
| **They drop it** (`dropE`, `dropW`; its fall set by rule, the generator tossed it up first) | `dropE/s2`, `dropW/s1` (used); `dropE/s1`, `dropW/s2` | `5304ab0c-ee93-4424-b02c-ece48b847803`, `762b3604-5626-40cf-a589-210d0e65fedd`; `a63d5bcf-78b4-44b9-9740-877093122cbb`, `d3f76c04-ca4d-4939-8997-83750ffe12f9` |
| **The framing gag (unused: turned down in play)**: her through the canvas. Starts and rough ends composed (`gag/compose.py`, `gag/ends.py`), three end edits, eight clips, two rounds of her sitting in the frame (her clothes changed) | `gag/` | ends `6a4757b7-971a-426c-ba42-63fa13da7466` (chosen), `1e134e66-f1c6-4683-8bc9-56f4cd6d48d0`, `9d4a09c4-8dae-4a86-a876-8dfe20db29e6`, `067bed83-fac6-45b7-b43d-2952e0576279`; clips `620470e4-a8d1-4add-a8a9-91b8a2671e44`, `51b8b104-cee0-40b8-9369-6f47081c2e63`, `f0f73fad-6146-48e6-b407-1122f1c62c5b`, `78d39fd2-2572-44a7-9b67-a046c8d08d2d`, `571835ef-8f0f-4467-b8b7-0a7aebce2481`, `145fe79a-5036-4181-a6c1-2bfd913f9d33`, `a5b9ab0c-f2bf-4b12-8f23-7d23659fcba6`, `c4e17f01-18fd-4b03-a929-2b8fac424fdb`; sits `db3fefc2-be62-457d-8d58-bb538647bc61`, `e173953e-22a9-4cd4-adbe-ad2ddc7e6232`, `5f841cd7-d7e2-434a-9c92-d205e12805b5`, `1d2a2a71-cbd0-4429-9aef-28937f823b6e`, `5e84e498-fa78-4824-9339-c82e130553b7`, `2dc39727-42ef-480f-a6d5-beb669913d41` |

About 175 generations for the item (the painting's two tries in `../../things/tries/painting/`).
