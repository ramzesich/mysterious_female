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

# The stage manager's cabin, the dressing room and the cold room (2026-11-24)

The user: "1-3" of seven offered. Three looks of each, "Keep every shape in this picture exactly where it is and the same
size, nothing added or moved: [the room, its pieces named], flat side view. Change only the finish, as detailed polished
pixel art: [the look]" (seeds 5, 13, 27: A its own colours, B lived-in or worn, C clean modern or grand). **Chosen: the
stage manager's cabin C, the dressing room A, the cold room A.**

## Used

| Picture | What | Job | Generations |
|---|---|---|---|
| `smcabin-C.png` | the stage manager's cabin, clean modern: light grey panels, pale birch, navy blankets (seed 27) | `cb33b93e-7bb0-462f-a6a5-e04ad2b1e0da` | 9 |
| `dressing-A.png` | the dressing room, its own colours, the bulbs glowing (seed 5) | `454c0859-e409-499a-8135-2e12512df600` | 9 |
| `coldroom-A.png` | the cold room, icy panels with frost, labelled tubs (seed 5) | `bacb4349-1343-4a27-bf28-e3af225c0dc8` | 9 |

## Tries (`tries/`)

| Picture | What | Job | Generations |
|---|---|---|---|
| `smcabin-A.png`, `smcabin-B.png` | its own colours; lived-in steel | `692246d1…`, `356531a7…` | 18 |
| `dressing-B.png`, `dressing-C.png` | dusty rose, worn; plum and gold (both drew a glossy floor) | `b66fa118…`, `14342a97…` | 18 |
| `coldroom-B.png`, `coldroom-C.png` | a worn freezer; clean modern white | `b162d59f…`, `1eaf526f…` | 18 |

**These three: 81 generations** (and the canister, 15: `assets/source/things/tries/README.md`).

# The nook, the lighting booth, the chapel (and the lifeboat's tries), 2026-11-24

The user: "The remaining rooms". Three looks of each, the same wording (A its own colours, B and C others; seeds 5, 13,
27); the chapel, the lighting booth and the lifeboat in two parts (256 px each, from x 0 and from x 56, 224, 152). **Chosen:
the nook B, the lighting booth A; the lifeboat left as it is;** the chapel: "Remove the chairs and regenerate", then **B**.

## Used

| Picture | What | Job | Generations |
|---|---|---|---|
| `nook-B.png` | the nook, an old library: dark green, walnut, brass (seed 13) | `6bceacbd-b26f-45c7-8a0b-1da42577c797` | 9 |
| `lighting-p1-A.png`, `lighting-p2-A.png` | the booth (x 0..256) and the catwalk (x 224..480), its own colours (seed 5) | `9fac4fcc-fbd2-4a1f-8e2f-996800493cab`, `6bee7105-c7e4-4576-a811-fe987680199d` | 18 |
| `chapel-p1-B.png`, `chapel-p2-B.png` | the chapel without its chairs (x 0..256, 56..312), softly lit (seed 13) | `80ffed95-6dc0-4f5f-8530-3171982d2d8e`, `1beca215-c254-4e7b-810a-3f5d43da2173` | 18 |

## Tries (`tries/`)

| Picture | What | Job | Generations |
|---|---|---|---|
| `nook-A.png`, `nook-C.png` | its own red; honey oak and cream | `e99bbe35…`, `246623db…` | 18 |
| `lighting-p1/p2-B.png`, `-C.png` | black backstage with tape; deep navy with coloured haze | `7aa97c7f…`, `d9d25638…`, `f540a6b2…`, `ed580fda…` | 36 |
| `lifeboat-p1/p2-A/B/C.png` | its own orange; worn; new and glossy (their parts' portholes and benches did not agree) | `99a67ad1…`, `19118281…`, `a258fd22…`, `aa7af770…`, `c304c409…`, `ca3f9f39…` | 54 |
| `chapel-chairs-p1/p2-A/B/C.png` | the chapel with its chairs, A B C | `86e76afe…`, `f7ad3b43…`, `3c5b3c1f…`, `ce7b0b24…`, `9946649a…`, `0e0da83c…` | 54 |
| `chapel-p1/p2-A.png`, `-C.png` | without its chairs: its own colours; warmer, ivory damask | `88a15269…`, `fcb42e28…`, `c85954dc…`, `814c1521…` | 36 |

**These: 243 generations.**

# The restrooms by the Chapel (deck 12), 2026-11-24 and 25

The user: "make it entreable to a small restroom cabin". Drawn flat (`tries/restroom-drawn.png`), three looks with the
same wording as the other rooms ("Keep every shape ..., change only the finish"; seeds 5, 13, 27), **C chosen**. Then
someone in the stall: `inpaint_image_pro_flash` of the room's foot of the stall door (x 90..117, y 112..127), three
seeds, **3 chosen** ("they worked better"), its ankles covered by the rail by rule.

| Picture | What | Job | Generations |
|---|---|---|---|
| `restroom-C.png` | modern: pale grey stone, white counter, brushed steel, a sea blue band (seed 27) | `6cf9dffb-e593-418d-acb9-ae0a1013a0a9` | 6 |
| `restroom-feet.png` | the gap under the stall's door, dark shoes (seed 27) | `f9cf8c32-b7c9-490a-b45f-7c436ed2a335` | 6 |
| `tries/restroom-A.png`, `-B.png` | its own colours; elegant beige stone and brass | `d3c0b415…`, `116fa36c…` | 12 |
| `tries/restroom-feet-1.png`, `-2.png` | blue trainers with ankles; nothing drawn | `dd4e9fe1…`, `1ae4a38d…` | 12 |

**The room: 36 generations** (its door, 15: `assets/source/ship/door-restroom/README.md`).

# Part 14's first group: her crew cabin, cabin 8206, the lifeboat's inside (2026-11-25)

The user: "Yes, let's do group 1". Three looks of each, "Keep every shape in this picture exactly where it is and the same
size, nothing added or moved: [the room, its pieces named], flat side view. Change only the finish, as detailed polished
pixel art: [the look]" (seeds 5, 13, 27: A its own colours, B lived-in or worn, C clean modern). **Chosen: A, A, A**, the
crew cabin's "regenerate without Bumbot's picture and reapply it": redrawn from `tries/crewcabin-nocat-drawn.png`. The
lifeboat in two parts (x 0..256, 152..408) from `tries/lifeboat-noports-drawn.png`, the room without its portholes.

## Used

| Picture | What | Job | Generations |
|---|---|---|---|
| `crewcabin-A.png` | her crew cabin, its own mint, without his picture (seed 5) | `c5d8972a-e860-4fc7-a12c-c65d3256f6cc` | 9 |
| `cabin8206-A.png` | cabin 8206, its own colours (seed 5) | `502d246e-d1be-4912-bdfb-7f4e8bcceb87` | 9 |
| `lifeboat-p1-A.png`, `lifeboat-p2-A.png` | the lifeboat without portholes, its own orange (seed 5) | `a5603469-88eb-4b42-bc37-ab1a922b1efc`, `96e0be0f-e0fa-4407-9d2e-506a2eeb3896` | 18 |
| `flag-3-even.png` | Ukraine's flag, try 3 (`tries/flag/flag-3.png`, `create_image_pro_flash` 32 x 24, seed 27), a blue row added and two yellow taken off: the line at half height | `82a300fd-d203-4ac0-a461-7bc307721ac4` | 5 |

## Tries (`tries/`)

| Picture | What | Job | Generations |
|---|---|---|---|
| `g1-crewcabin-A/B/C.png` | with his picture: its own; lived-in (sunbeams in a cabin with no window); white panels | `4cbb53db…`, `4e5322ff…`, `ab6ffc95…` | 27 |
| `g1-cabin8206-B/C.png` (A is the one used) | warm, a plant and a lamp added; light oak | `1ef6b84a…`, `e843183f…` | 18 |
| `g1-lifeboat-p1/p2-B/C.png` (A used) | worn and grimy; clean, pale grey benches | `bcee1129…`, `f5258b03…`, `75997355…`, `512b0a08…` | 36 |
| `flag/flag-1.png`, `-2.png` | the flag, seeds 5 and 13 (2: green smears in its shield) | `7751e2fa…`, `801ab411…` | 10 |

**These: 132 generations** (the photo, 5: `assets/source/photos/lifeboat/README.md`).
