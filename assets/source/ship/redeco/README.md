# The linen room and the laundry redecorated (2026-11-24)

The user: "redecorate the laundry room and the linen room, keeping the exact dimensions and the layout of the current
props, so that we wouldn't affect gameplay. The props that are already generated with PixelLab there (like the openings)
are to be kept." The laundry's washers and dryers might change size; the linen room's racks and shelves stay exactly, what
lies on them may change ("they have to look more like linen", "and also add variety"). Three looks were made of each:
**A** worn working steel, **B** clean modern back-of-house, **C** warm and soft. **Chosen: linen A, laundry C** (the
laundry's glossy floor with reflections then taken out: "way out of the rest of the ship's theme"; its own floor back).

Every one is `edit_image_pro_flash` of the room's picture as its builder draws it (`assets/ship/linen-room.png`,
`assets/ship/rooms/laundry.png`), "keeping every shape exactly where it is". `tools/redecorate_rooms.py` lays the chosen
ones over the builders' pictures and pastes back what play and the clips rest on (both builders call it).

## Used

| Picture | What | Job | Generations |
|---|---|---|---|
| `linen-A.png` | the linen room, worn steel, the shelves' linen varied (seed 5) | `b63c3e2d-f72d-4116-9fba-5d9e53ca51bc` | 9 |
| `laundry-left-C.png` | the laundry's x 0..192, warm (seed 27) | `d076e809-c4a6-4d27-9229-7ecf6e35ca30` | 6 |
| `laundry-right-C.png` | the laundry's x 148..336, warm (seed 27) | `b49d6603-c2ec-46fb-93fb-a6a4697dd409` | 6 |
| `laundry-heal-C.png` | `inpaint_image_pro_flash` of a 256 px window from x 64, the strip over the join (x 184..200) blanked and inpainted from both sides | `12338fe2-d3af-4796-b119-a0ab533c14a0` | 9 |

## Tries (`tries/`)

| Picture | What | Job | Generations |
|---|---|---|---|
| `linen-A/B/C.png` | round 1, the shelves' contents kept as they were (white blocks) | `f79c9239…`, `e0da3d87…`, `3c9ab0e7…` | 27 |
| `linen2-A/B/C.png` | round 2, the contents free to read as linen (all white still) | `10f28f76…`, `5b583da5…`, `020aea95…` | 27 |
| `linen3-B/C.png` | round 3, varied linen: B widened the left rack, C added a shelf (not kept) | `7a279b35…`, `88e6a880…` | 18 |
| `linen4-B/C.png` | B and C restyled from linen A, racks and linen kept | `e6ea3967…`, `541c2c61…` | 18 |
| `laundry-left-A/B.png` | the laundry's left half, A and B | `d1247341…`, `b29c8ecf…` | 12 |
| `laundry-right1-A/B.png` | the right half, A and B | `e90a832f…`, `04182266…` | 12 |
| `laundry-right-A/B/C.png` | the right half with the left as a style reference: streaky, the join still showed | `c4aa812f…`, `139da9b5…`, `c28f0b66…` | 18 |
| `inp-A.png` | an inpaint of the right part next to the finished left: it kept the old picture | `2e4b510f…` | 9 |
| `win-A/B/C.png` | a redraw of the 256 px window with the left finished: the right came back almost unchanged | `62b1ce63…`, `296267de…`, `25037c83…` | 27 |
| `heal-A/B.png` | the join healed, A and B | `d4983869…`, `e96d3675…` | 18 |

**All of it: about 216 generations.**
