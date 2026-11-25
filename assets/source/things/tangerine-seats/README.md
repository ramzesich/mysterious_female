# The tangerines' seats (plan-the-rest §7d, 2026-11-25)

What a tangerine lies on, generated (the user's choices; 90 generations). The chosen ones are copied, trimmed, into
`assets/source/ship/<name>/frame_0.png` and built by `tools/build_ship_art.py` in their own colours with their washed
twins; where each tangerine lies in them: `SEAT_SPOTS` in `tools/population.py`.

| Try (`tries/`) | What | Tool, seed | Job | Gens |
|---|---|---|---|---|
| `A1-s5`, `A1-s13` | tray on a wooden X stand, used breakfast plates (the loads read as blobs) | `create_image_pro_flash` 48x32, style the deliveries' `tray-stand` | 80cb25c2-0761-4ca5-9f79-562b907125a9, fccd63ba-5973-4a4b-a8eb-e6e2bcf1fd24 | 10 |
| `A2-s5`, `A2-s13` | the same, a dome and a glass | the same | 98d2f123-757a-46b0-a3d5-f12d205db1b3, 74853210-6be6-4ad0-8cda-bad74d546a42 | 10 |
| `A3-dome-s5`, **`A3-dome-s13`** | "a fitting stand" (the user): slim chrome, straight legs; dome and glass. **Used: `roomtray-dome`** | pro flash 32x32, style A2-s13 cropped | 36dc98da-c04b-4612-b0da-ebe06627b0a5, 3cba3b04-9662-42ae-9068-0b10f0e42099 | 10 |
| `A3-cup-s5`, **`A3-cup-s13`** | the same, cup and milk jug. **Used: `roomtray-cup`** | the same | 39ca0d4a-42b4-4c0d-9bc1-670cdf6e3132, 84b5ca21-8819-4ca6-a33a-eea8de75a5ff | 10 |
| **`B-s5`**, `B-s13` | low bowl: grapes, a green apple, a banana, nothing orange. **Used: `fruit-bowl-green`** | pro flash 32x24, style the game's `fruit-bowl` | fdb2f232-2f91-41e3-8785-c79b8b3fb809, 288d9302-24e5-48e6-bc8c-1e281a47a1c0 | 10 |
| `C-dessert-s5`, `-s13` | a plate by the right dome (it kept the dome) | `inpaint_image_pro_flash` of the game's `dessert-trolley` | 1df6bd0b-70c7-4014-8849-6a0a7c7e129d, 2742db7d-0c5e-40c8-bbc4-b01585560a06 | 10 |
| **`C2-dessert-s7`**, `-s21` | the right dome taken out for a plate. **Used: `dessert-trolley-plate`** | the same | 4f4c64ab-4d60-4a9d-8991-044d59cf1680, 8f3a1ab1-05d2-4c1a-b4af-fa5f081ac4ff | 10 |
| `C-cart-s5`, `-s13` | a plate past the cart's end | inpaint of the game's `service-cart` | e00bc8b8-079c-42df-8275-f26491e2700f, bf86486a-1b41-4757-8a12-6db245245672 | 10 |
| `C2-cart-s7`, **`C2-cart-s21`** | the dome kept whole, the plate at its end. **Used: `service-cart-plate`** | the same | acad5e93-a147-4246-830e-0d625491a4ee, a9e959d7-ab66-4e01-9335-ce5525b0c7ac | 10 |

Seated as the user set them: the trays' tangerine 1 px into the tray's free end; the bowl's in the green apple's place
(a pair's second on the grapes); the dessert cart's on its plate; the room-service cart's 3 px in from its end.
