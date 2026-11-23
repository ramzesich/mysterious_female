# The deliveries' art (plan-the-rest §5 3.2)

## 1, the vase of flowers (deck 8 midships; the user, 2026-11-23)

| File | What | PixelLab |
|---|---|---|
| `../delivery-vase.png` | The vase, from `tries/vase-1.png` (`create_map_object`, side, 32 x 48) with 8 rows of its plain glass cut out (rows 27 to 34: 43 px tall was about 1.2 m beside her), 29 x 35; in its own colours (`OWN_COLOURS`) | `e503407a-c7bb-4fe9-aeee-f7db7ff8eab4` |
| `../tray-stand.png` | The low table it waits on, `tries/stand-2.png` (the user's choice of three: "more in profile from the side, not top-side"); its own colours | `ac6e805e-5389-4ccf-8414-9adbf2be78bb` |
| `tries/stand-1.png`, `stand-3.png` | The first try (its top seen from above), a folding stand in strict profile | `2c5a81f8-b3d1-47f6-bf59-21f33c15105f`, `98251b6d-66c2-44cf-94d0-c7e7a17dc1a5` |
| `frame.png` | The flower frame round the screen while she carries it (the user: "like a flower frame, all around the screen's perimeter, obscuring parts of front and back of the corridor"): `tries/frame-6-512.png` (`create_image_pro`, 512 x 288, the last frame as its style image, "the left and right sides each a thick column ...") cut to its middle 480 x 270, the screen's own size, so it runs off every edge. Copied to `assets/sprites/flower-frame.png` by `tools/build_things.py` | `4dfff9f1-f663-47a2-ba60-df70f67c91c0` |
| `tries/frame-1.png` | The first frame the user chose of three (480 x 270): it "looks cut out near the screen edges" (a margin of 10, 5, 6 px) | `b6386a4f-2b7e-4787-b6a2-994c9ebc40b8` |
| `tries/frame-2.png`, `frame-3.png` | The other two: light, a leafy wreath | `3c6ce45a-a139-4649-b4cd-19c7d5d7bf25`, `b059296e-8998-4322-b886-c329a3bd1c3c` |
| `tries/frame-4-512.png`, `frame-5-512.png` | Regenerated at 512 x 288 to be cut to the screen (full bleed; the user: "sides fuller still"), and a try whose sides came thinner | `505cce35-7b46-49e2-b5d6-2e0c7160d00d`, `81a4e78a-983f-49c0-a3b3-00032976ea4b` |
| (not kept) | frame-1's margins filled: inpainted tile by tile (the background removal took most of it, `c7d253c1-8dd9-4688-8e2a-7df6979b7bfe`), then on magenta (`401d4155-…`, `711ba6d3-…`, `0a96e21a-…`, `fca7c641-…`): "the bottom part doesn't look good"; regenerated whole instead | |
| `tries/stems-1.png`, `stems-2.png` | The bouquet seen close, a first idea for the view (over the hallway ahead only), before the frame | `ada24e67-5080-4c09-aedb-979bb2fcf7c3`, `57ad0d0d-3a03-4311-a6fc-35b2257863da` |

The tray is the game's own (`tray-18` in `src/world/carry.js`, narrower than the 26 px one: the user), the tag and the
door's plate are `src/signs.js` looks (`card`, `steel`). About 200 generations, most of them the frame.
