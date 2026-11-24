# Tries not used (the art rule looked back over, 2026-11-17)

PixelLab map objects (`create_map_object`, side view, low detail, 1 generation each), made when
step 1 to 4's pictures drawn in code were replaced by generated ones. The ones used are in
`assets/source/things/`; these are kept so nobody pays for them again.

| File | Map object | Why not |
|---|---|---|
| `flag-se-try1.png` | 8933a18f-df38-4407-b923-ef12bc0302f0 | a second flag drawn beside the first |
| `wall-shelf-try1.png` | 3a204258-a580-4ccf-8bbb-f18ae34c00e9 | its brackets above and below the plank |
| `laundry-cart-try1.png` | 42c482ce-055b-4ced-991a-71f80520ff9a | turned three-quarters |
| `door-hand-try1.png` | 1edf3ca7-196a-4f1a-8845-3df9a09c2817 | pointing, not taking |
| `shh-lips-try1.png` | 55668adf-258e-43e1-90bb-1fa721449917 | finger beside the lips |
| `shh-lips-try2.png` | 17bc8af0-4693-4899-ae60-3802ebccd704 | "doesn't read like a shh at all" (the user) |
| `shh-profile.png` | 7f4f71c8-5cf4-4b8c-bafd-bdd9459c9d59 | a finger to the lips is lost at a bubble's 16 px |
| `shh-emoji.png` | 85773165-0474-46b5-9c70-a9f07471c3f1 | the same |
| `shh-outline.png` | 81249e1c-63cd-421b-a3a0-6af9280d2dd1 | the same |
| `mute-plus.png` | 72212999-3e59-4912-abc0-0d146246c6fc | a plus, not a cross |
| `icon-mute-raw.png` | 0093936d-dc7c-45c4-9bfc-b1a3490107ab | **used**: the raw of `../icon-mute.png`, which is it shrunk to 18 px wide with its cross redrawn even by hand (the user: "It is uneven") |

| `laundry-cart-try2.png` | f4b52a29-421a-46d8-a18a-0ed98dc7bcf8 | still half-turned: "the half-turned profile doesn't fit here" (the user) |
| `cart-a.png`, `cart-b.png`, `cart-e.png` | 5387f495-469a-4936-b825-06ce436a1f45, ea9fabcb-06ca-4077-b158-46c62401478b, 38e2732d-e737-430d-b0ea-085b42bca938 | a, b: a strict side but not liked; e: grey and lopsided |
| `cart-c.png` | 5524b35b-85ca-497f-b683-ab590350f9bf | half-turned, but the look the user chose: "take cart-c as example, and generate it in profile" |
| `laundry-cart-raw.png` | `edit_image_pro_flash` of cart-c, job 739a55ea-f18e-4ade-ab75-3f8f968e4b5a (5 generations) | **used**: `../laundry-cart.png` is it at its own pixels (shrunk to 44 px it came out deformed, the user) with rows 31 to 37 of its bin cut out and the white towel row across its rim painted the rim's green (the user: "a white strip of laundry where it should be the cart's side") |
| `feather-lean.png`, `feather-mug.png` | 9ceca535-67c2-45e2-be8f-5d245a9fc2a1, aca6532e-4a61-4a9e-8f11-7136d027bcd9 | stood on its end it "looks like it is stuck in the shelf"; in a mug, a pen in a cup |
| `teaser-b.png` | 36372a6f-a9ac-4463-94d5-1d1c748068b3 | a rolling pin with a bag |
| `feather-toy-raw.png` | 91332653-c3a1-42cb-a52f-89a0055581df | **used**: `../feather-toy.png` is it with its wooden handle made purple, to stand out from the shelf (the user) |
| `feather-toy-step4.png` | (step 4's) | the feather toy lying flat, 6 px tall: on the shelf "it just looks like a shelf glitch", and not like a cat toy (the user) |

The ones used: `flag-se` 40e7f9a8-db21-49e5-951b-5b0567a4246a, `flag-fi`
1d020129-d8d1-4774-8827-5989875b6c64, `flag-ee` 5c2d413b-5d9b-48b1-8ead-4e4e952eca84, `flag-dk`
78ce4d53-a5de-4a36-affb-c0374d05f4e3, `wall-shelf` 67ddc1dd-9a54-4507-9777-8ce3902f4259,
`knit-basket`
a35c7de6-b5bf-46c2-82ce-36fbb1246894, `door-hand` 304312bc-1e2e-4f7c-b7dd-3c06a80ac3fe,
`icon-heart` f86250a0-3886-4984-a727-b06e35a23ca6.

The steward's tall trolley (2026-11-17; `create_map_object`, side view, low detail, 64 x 96, 1 each):
`steward-cart-a.png` ade11b6e-cf13-4701-94b5-7de02eaccb71 (wire trolley with towels), `-b`
df97f40e-8901-4593-855b-7ffce7f262da (blue cart, a tower of pillows), `-c`
9f4cea5e-ce98-480f-aafc-59b7ca4e4480 (wooden shelves, white and blue linen); **`-d`
e03df2fc-812c-46e1-b898-cbaa1c442dfc chosen** ("4": boxes, towels and a laundry sack; see
`../../people/steward-raw/README.md`).

## His folded t-shirt (13), 2026-11-21: `tshirt/`

Small folded shirts at their own size (the close-up shrunk read as a dark bag). **3 used** (`../tshirt-folded.png`:
its five purples set to the close-up's navies by lightness, 20 x 12 by majority).

| File | What | PixelLab id |
|---|---|---|
| `tshirt/1.png` | Laid flat, 32 x 32 | 17bfd147-58b4-4b65-b15c-aed71ebfbe61 |
| `tshirt/2.png` | Laid flat, lighter | 8f11cbf5-f9e8-4c75-b362-8cc4abe3ed6c |
| `tshirt/3.png` | **Used**: folded, lying, seen a little from above, 48 x 32 (came purple) | c55b5d17-bb51-4a94-b026-1e487cd5d59f |
| `tshirt/4.png` | Folded, standing, grey | e4e6a2ef-5c94-4997-a65a-463d3f59ff74 |

## The boat walkway's life-jacket box and the drill's warning light (2026-11-21)

| File | What | PixelLab object |
|---|---|---|
| `lifejacket-box/try1.png` | A white deck box: came tiny and broken | 7e81974d-e910-4778-a584-ba1d3503d099 |
| `lifejacket-box/try2.png` | **Used** (`../lifejacket-box.png`, the user's): a white deck box, two latches, a handle; book 11 on its lid | 5f1feb8b-79fd-4eab-abb6-73c467bea192 |
| `warning-light/try1.png` | A red beacon dome on a stand: stands up, does not hang | 0c8c773e-e9c3-4777-ba4b-8e0c773453ac |
| `warning-light/try2.png` | **Used** (`../warning-light.png`): a red lens in a cage hanging from a ceiling mount; its "off" twin built by `DIM` | 24f9e26e-ec4d-4b53-aafa-5a84fdfc7d27 |

## The lifeboat's oars (2026-11-21)

| File | What | PixelLab object |
|---|---|---|
| `oar/try1.png` | A dark varnished oar, a broad blade, a red tip | b1e62f2d-fc75-4293-8851-b89400c853b6 |
| `oar/try2.png` | **Used** (`../ship/lifeboat-oar.png`, cut to what is drawn; the user's): a light shaft, a narrower orange-red blade | e8317e60-187b-46c9-8f95-e7b6152977b3 |

## The lifeboat's boathook, left of the ladder (2026-11-21)

| File | What | PixelLab object |
|---|---|---|
| `left-rack/boathook-wood.png` | **Used** (`../ship/lifeboat-boathook.png`: cut to 82 px from its pole's middle, its pole thinned to the oars' two rows, the user's "slightly thinner, to match the oar handles") | 342946d5-cdfd-4b2e-8bdf-d0630c4ba211 |
| `left-rack/boathook-alu.png` | An aluminium boathook: read as a pipe | 7a657304-26e2-4d00-981d-0da3827a72b3 |
| `left-rack/reaching-pole.png` | A striped rescue reaching pole | b0d37384-70fb-4769-aa91-712180b05730 |

## Deck 9's console table, book 14 on it (2026-11-21)

The end of the officers' corridor, between its end wall and the captain's door (about 45 px of bare wall). Tries 1 and 2
came as low desks ("None of them are consoles though", the user); 3 and 4 asked for a tall slim one. All four were
placed in the game for the user, who chose 4 (its legs uneven at the floor at 8x, unseen at the game's size).

| File | What | PixelLab object |
|---|---|---|
| `console-table/try1.png` | A honey teak table with a drawer: a desk | a9b30900-8f0a-4585-9d61-ec0d9b9c0dc8 |
| `console-table/try2.png` | A dark mahogany table with a low shelf: a desk, ragged legs | 03ded0bb-488f-4ee5-bf43-0384d1f9342d |
| `console-table/try3.png` | A tall slim console, four thin legs with brass feet | f281640d-1621-4902-89b3-0fd7671e4cb2 |
| `console-table/try4.png` | **Used** (`../console-table.png`, trimmed, 32 x 28; the user's): a half-moon console in honey teak on curved legs | 284ced4a-0507-42e5-b810-4e3da6a2a945 |

## The reading nook's cat picture (2026-11-22)

A picture of a black cat asleep on a book for the nook's wall, over its stack of books (it replaced a few drawn shapes
that did not read). `create_map_object`, side view, 32 x 40, 1 generation each, in `cat-picture/`:

| Try | What | Object id |
|---|---|---|
| 1 | **Used**: dark wood frame, the cat curled on a red book (its ear's red made black and its eyes Bumbot's yellow-green #a2a947 by hand: `assets/source/things/cat-picture.png`) | 2a95c608-6027-434b-bbed-a0ce0b0aabc4 |
| 2 | gold frame, the cat sitting on two books | 0261b657-57ea-4ce3-9cec-bc766dd20e5c |
| 3 | the cat stretched on an open book | 5bfe38eb-d4aa-4071-9ae5-ebf9eca79c2b |

## The Library's return trolley and the shelf's board (2026-11-22)

In `library/`, `create_map_object`, side view, 1 generation each (the user chose "Both of them: 2"):

| Try | What | Object id |
|---|---|---|
| trolley1 | a low cart with a sign (its arrow read as a cross) | ce7c671a-7cef-4d1c-8231-337eaac84d15 |
| trolley2 | **Used**: a small bookcase on castors (`assets/sprites/book-trolley.png`, 29 x 34) | 4c9bda8e-5f10-4483-a1ab-4138233c46ff |
| trolley3 | a cart full of books, three-quarters (dropped) | 4a8d890d-58d3-460a-8afb-552c2a899101 |
| shelf1 | a dark board seen from above | 6eaa6034-2cac-406b-8c05-466917f30601 |
| shelf2 | **Used**: a thin warm plank, its middle lengthened to 125 px (`assets/sprites/book-shelf.png`) | 1f7439dd-79fc-436c-a588-2d1ba56d0364 |

## The ice cream mix's canister (2026-11-24)

The user: the canister drawn in code "worth generating properly". `create_image_pro_flash` at its size, 20 x 24, 5
generations each. **Used: 3** (`assets/source/things/canister.png`, its own colours: `OWN_COLOURS`).

| Try | What | Job |
|---|---|---|
| canister/canister-1 | a slim steel canister, a patterned pink band | c8298995-af5e-4b56-9ecd-699d3f6dffab |
| canister/canister-2 | the same, darker, a plain pink band | c5eca56a-6af9-4c99-9050-3716e51769fb |
| 3 | **Used**: a steel churn with side grips, a pink label with a cone on it | 123d6d8c-f619-4b15-a22f-5b1c247913c0 |
