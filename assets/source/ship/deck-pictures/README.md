# Each cabin deck's framed pictures (plan-the-rest §6, 2026-11-24)

PixelLab map objects (`create_map_object`, side view, 32 x 32 to 40 x 32, 1 generation each; 38 in all), the
description "one small framed ... hanging on a wall, filling the whole picture: ..., completely flat front elevation,
no depth". `clean.py` cuts the chosen ones to their frames (a hanging wire or hooks off, the escape plan's stray red
mark) into `frame_<n>.png`, which `tools/build_ship_art.py` reads (`DECK_PICTURES`, the same order); the corridors
hang them by deck (`DECK_PICTURES` in `src/scenes/ShipScene.js`), washed 35% as the cabin corridors' props are.
Deck 4: safety posters (the user chose the first aid and lifeboat posters among nine for its fifth); 5: paintings of
the ship; 6: old charts and port maps (its corridor hangs three); 8: seascapes; 9: botanical prints; 10: old liners'
posters.

| try | id | |
|---|---|---|
| `tries/d4-muster.png` | `a5980209-ca45-4f54-bea7-6270a6057c00` | turned down by the user: an exit sign, "does not make any sense" |
| `tries/d4-roster.png` | `01f18985-3e32-4706-a8c3-65dd7e92d17a` | no frame |
| `tries/d4-lifejacket.png` | `923c40fd-a081-43ce-b73b-9d24bcee1735` | **chosen** |
| `tries/d4-escape-plan.png` | `5f4208fc-8ace-4381-9bf5-ffeae52f0086` | too faint |
| `tries/d5-ship-sea.png` | `628c2e54-5f34-43ea-8123-65c65e7804cc` | **chosen** |
| `tries/d5-ship-harbour.png` | `7553bffd-dc40-48b8-80ff-a6d11654a79e` | **chosen** |
| `tries/d5-ship-islands.png` | `82fcad35-8395-49a8-823b-baabdce60a60` | no frame |
| `tries/d5-ship-bow.png` | `5318513d-2863-417d-9fc2-62110ccaf3a5` | **chosen** |
| `tries/d6-chart-harbour.png` | `29ae8e1e-5557-4a6c-be5f-a127299207c8` | **chosen** |
| `tries/d6-port-town.png` | `5d1c88c1-f92a-46dd-b384-9afa20a17025` | **chosen** |
| `tries/d6-islands.png` | `236700c8-e2ff-414c-b8e1-ee138efca845` | **chosen** |
| `tries/d6-chart-rose.png` | `4b4be0d9-6159-4a9f-9405-87ea92f88887` | **chosen** |
| `tries/d8-waves.png` | `86243af0-9244-4545-b599-db2bf1b5b900` | **chosen** |
| `tries/d8-lighthouse.png` | `25e2d4b6-2861-4f20-a5ac-5053af69eacc` | **chosen** |
| `tries/d8-sailboat.png` | `9e3866e6-7113-402b-a26c-6909ce980ed8` | **chosen** |
| `tries/d8-sunset.png` | `f59ea2ce-f2fe-4032-b7f9-265b5f07df64` | **chosen** |
| `tries/d9-fern.png` | `983ed91e-53d6-439e-826d-0294e1da26e6` | **chosen** |
| `tries/d9-flower.png` | `f35c99b7-1d90-4611-a897-9c0be9ffc920` | **chosen** |
| `tries/d9-lemon.png` | `fedb4f58-253d-4a51-8d9c-e7e4f24fd902` | **chosen** |
| `tries/d9-palm.png` | `361cbdf4-bafa-454c-9ec6-f45a16e582c5` | read as a bush |
| `tries/d10-liner.png` | `2fa81ff0-ab2f-44c1-8bb8-be9c49dc7439` | **chosen** |
| `tries/d10-bow.png` | `e6d976a2-171c-4245-980b-a4801256af3c` | **chosen** |
| `tries/d10-night.png` | `81375f1a-75f2-4e5e-a0cc-f8c27a83ca37` | **chosen** |
| `tries/d10-funnels.png` | `b7e06b2a-75df-4378-8ef1-d933d0c2e74b` | no frame |
| `tries/d4-roster-2.png` | `ef5fb725-774f-4f74-9b71-91d9f910fe3d` | **chosen** |
| `tries/d4-escape-plan-2.png` | `b9150310-6392-4fa6-956f-53cd5d7b4b27` | **chosen** |
| `tries/d5-ship-islands-2.png` | `13cb11b4-5e02-44b2-82f5-de730215948a` | **chosen** |
| `tries/d9-monstera.png` | `172e96dc-446b-4229-8cb4-55546dca1a22` | **chosen** |
| `tries/d10-funnels-2.png` | `ab4eaaa0-1d25-43d3-8efc-15441175be44` | **chosen** |
| `tries/d4-lifeboat.png` | `f5fb7ebe-bf51-449a-a0f9-571f35965802` | came as a life ring; not chosen |
| `tries/d4-muster-a.png` | `a8e3f872-6ebe-4242-9523-f22fa5acec36` | its letter garbled |
| `tries/d4-signal.png` | `09e0899b-478c-441b-9e91-6c61e6a05c38` | no horn; a plain notice |
| `tries/d4-lifeboat-2.png` | `292f5f27-20a3-4167-9740-ac78cc5ce05a` | **chosen** |
| `tries/d4-extinguisher.png` | `b8461203-d293-483f-b3f9-fcd375221969` | not chosen (a real one hangs beside) |
| `tries/d4-handwash.png` | `898d22d5-32d2-49ea-b966-fd9e2fe52af1` | not chosen |
| `tries/d4-hardhat.png` | `6df9a4a8-ab95-4a23-a786-4b5553c97064` | not chosen |
| `tries/d4-firstaid.png` | `abe68231-5d53-462b-aeab-7b25d3ae6ff8` | **chosen** |
| `tries/d4-blueprint.png` | `7e41f82d-e0e5-457e-a11f-0017d5e09056` | not chosen |
