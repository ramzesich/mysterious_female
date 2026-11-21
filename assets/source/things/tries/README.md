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
