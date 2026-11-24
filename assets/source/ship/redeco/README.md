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

# Three more (2026-11-24): the dry store, the galley, the maid's cabin

The user: "In the same manner as we redecorated the linen room and the laundry room, I want to continue with other
rooms" (the crew cabin on deck 3 and cabin 8206 left as they are). Three looks of each, the same wording as above (A worn,
B clean modern, C warm; the maid's cabin's A a classic cruise cabin, B Scandinavian, C cabin 8206 as a reference).
**Chosen: store A, galley A, maid's cabin C.** The galley's halves are cut at x 178 with no inpaint.

## Used

| Picture | What | Job | Generations |
|---|---|---|---|
| `store-A.png` | the dry store, worn painted steel, its goods redrawn as a food store (seed 3) | `46d007ab-3b23-49d6-8499-94df66e2a9c8` | 9 |
| `galley-left-A.png` | the galley's x 0..188, a worn working stainless galley (seed 3) | `2f0c5b21-0f70-4d65-aedd-53816fb643ee` | 6 |
| `galley-right-A.png` | the galley's x 148..336 (seed 3) | `da53a7ad-84d5-4c5e-97db-72df78aba0d2` | 6 |
| `maid6-C.png` | the maid's cabin, `method: reference` with cabin 8206's picture (seed 27) | `4cac2596-ab5f-41f7-a910-d5e0a54a7bd3` | 9 |

## Tries (`tries/`)

| Picture | What | Job | Generations |
|---|---|---|---|
| `store-B/C.png` | clean modern; warm | `0e8f6a5e…`, `a4354147…` | 18 |
| `maid6-A/B.png` | classic cruise cabin (cherry, brass); bright Scandinavian | `33336b18…`, `6d519ee5…` | 18 |
| `galley-left-B/C.png`, `galley-right-B/C.png` | gleaming new (bare panels on the right); warm (a tall cabinet by the door read as a second door) | `cd738bc2…`, `f58ac2d9…`, `b3a8a9c1…`, `04b42247…` | 24 |
| `galley-heal-A.png` | `inpaint_image_pro_flash` of the strip over a join at x 181: a flat grey pillar, not used | `5a80da0e…` | 9 |

**These three: 99 generations.**

# The guest cabins, the pantry and the blanket fort (2026-11-24)

The user: "More rooms". A pilot on deck 9's balcony cabin: C1 to C3 with cabin 8206 (or the maid's cabin) as the style
reference (they moved the furniture and drew a second bed: `tries/balcabin9-left/right-C*`), then T1 to T3 described in
words, parts cut at plain wall; **take 3 chosen**: "Keep every shape in this picture exactly where it is and the same
size, nothing added or moved: part of a passenger cabin on a cruise ship [with a glass door onto the balcony], flat side
view. Change only the finish, as detailed polished pixel art: cream wall panels with thin seams, warm orange-brown wood
with a little grain, [soft folds in the bedding and curtains,] soft gentle shading, the same colours." (seed 5), then
the same for each cabin. The pantry: three looks (A worn, B clean modern, C warm, the store's wording), **B chosen**,
its left part redrawn to x 212. The fort: three, **3 chosen**.

## Used

| Picture | What | Job | Generations |
|---|---|---|---|
| `balcabin9-l2-T3.png`, `-r2-T3.png` | deck 9's balcony cabin, x 0..180 and 112..288 | `8302e910…`, `3a3bfb45…` | 12 |
| `balcabin8m-l/r.png` | deck 8 midships' (x 0..184, 112..288) | `822489ae…`, `28edd55c…` | 12 |
| `balcabin8a-l/r.png` | deck 8 aft's | `9f8d3538…`, `5a38995c…` | 12 |
| `balcabin9a-l/r.png` | deck 9 aft's | `91317524…`, `28e405ac…` | 12 |
| `balcabin10a-l/r.png` | deck 10 aft's | `f6c9fd30…`, `e33b2513…` | 12 |
| `guest10-l/r.png` | the balcony guest's, deck 10 | `d08458df…`, `cd8afa8c…` | 12 |
| `cleanup-w.png` | the cabin mid-cleanup, deck 9 | `5b77ee46-5431-4e7a-8615-fe41ad78854e` | 9 |
| `makeup10-w.png` | the cabin being made up, deck 10 | `9143ce18-4b77-4502-9524-c423cd3b9bef` | 9 |
| `adjoin-p1/p2/p3.png` | the adjoining cabins, x 0..212, 200..388, 244..432 | `093e5302…`, `d55b7c7a…`, `2a3fe6ff…` | 21 |
| `pantry-L212-B.png`, `pantry-right-B.png` | the pantry B, x 0..212 and 100..288 | `ca8afcda…`, `8458fe00…` | 15 |
| `fort-3.png` | the blanket fort, its outline kept ("change only the finish") | `25522bff-df2e-4d9a-9eb8-10f9796ae370` | 5 |

## Tries (`tries/`)

| Picture | What | Job | Generations |
|---|---|---|---|
| `balcabin9-left/right-C1..C3.png` | cabin 8206 / the maid's cabin as the style reference: furniture moved, a second bed | `846cd1ab…`, `0d1018bc…`, `59196549…`, `d454c92a…`, `76da5117…`, `ca391b31…` | 36 |
| `balcabin9-l2/r2-T1, T2.png` | richer wood; warm glow | `c6f68965…`, `78955e4a…`, `a161f40c…`, `8aadc357…` | 24 |
| `pantry-left/right-A, C.png`, `pantry-left-B.png` | worn; warm; B's first left half (cut through the shelves) | `30a6addf…`, `fb802b12…`, `16b9d9b4…`, `6c0a6f8a…`, `8545ee0d…` | 30 |
| `fort-1.png`, `fort-2.png` | the fort described in words | `76e04480…`, `c93e4aa8…` | 10 |

**This round: about 260 generations.**
