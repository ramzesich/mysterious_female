"""The ship's people (GAME_DESIGN.md §6.1.6, docs/population.md §7): each one's PixelLab character
and the clips the game uses. `python tools/fetch_people.py` downloads their frames into
assets/source/people/<name>/ (the standing pose `stand.png`, the figure turned to us `front.png` and away `back.png`, each animation's east frames
`<animation>/<i>.png`); `python tools/build_people.py` packs them into assets/sprites/people.png.

All are PixelLab v3 characters at 64 px, side view (two generations each): that came out at her
height and nearest her look (2026-11-13; a "standard" one was 71 px tall and realistic). Clips are
made with animate_character, east only: a template clip, or skeleton-v3 with one of its moves
(walk, eat, talk, sit_seat...) and poses on top.

name: (character id, {clip: frames per second}, options). A clip is an animation of that name on
the character; "stand" is its standing pose. Options: "flip": the sprite was drawn facing west;
"scale": shrunk by that much (a seated figure that came out as tall as the standing ones); "cut":
{name: (clip, [frames])} a loop made of some of a clip's frames.
"""

CAST = {
    # Region 1.
    "officer": ("4d3e6422-a934-40e0-a47d-e841378610ae", {}, {}),
    "rival": ("68ef5f08-d2be-4f41-ad76-5831039110c3", {"trip": 12, "peek": 5}, {}),
    "porter": ("3ad54560-70f4-4b3c-8ab0-60b0be9ca97e", {}, {}),
    "waiter": ("3423e6b8-f2d5-423f-86ee-b9c77809194c", {}, {}),
    "tourist": ("5d966249-7a4c-42ab-9ba8-d1384fae259a", {}, {}),
    "robe": ("9d68ff5f-80b7-4187-86a9-7cd9eff01bed", {}, {}),
    "stewardess": ("29866bd3-ce11-4319-8e99-7d6de7ffaef8", {}, {}),
    "receptionist": ("b0851098-7398-456a-a950-c1b5367d4d53", {}, {}),
    "photographer": ("89836c72-c724-4013-a128-46519a7a8976", {}, {}),
    "gentleman": ("4a0085ce-78f1-476c-8863-3f3fc461190f", {}, {}),
    "lady": ("45a8f48c-7fd9-4067-9173-7cb7d82c21d7", {}, {}),
    "cleaner": ("47c5aa91-e4f6-471b-bc77-280aeba5feb8", {}, {}),
    "agent": ("4f239177-54ca-4b07-b1e6-7d9475c8d35b", {}, {}),
    "maitre": ("8336eefc-5d4f-452c-b70d-d3ca545505c8", {}, {}),
    "chef": ("6ca50f05-0ef1-4094-af3c-9ec00846cd36", {}, {}),
    "folder": ("fe49270a-7cd3-4f5d-84ee-3e47316bc16f", {}, {}),
    # Diners, drawn seated on their own dining chairs (they stand in a chair's place at a table).
    "diner_red": ("6dc96ff4-58fc-4a8d-b5c7-1bb111a772fc", {}, {}),
    "diner_suit": ("126b575d-bac9-4369-a721-7aa957e0bb5f", {}, {}),
    "diner_teal": ("f2700aec-2d7f-48b8-8025-4313be63f2ce", {}, {}),
    "diner_linen": ("89dfbeac-8d4c-4a89-a578-8dbc95ba16fc", {}, {}),
    # Region 2.
    "librarian": ("10f3bef9-74d9-47f9-af84-f36ec73cb625", {"shelve": 7, "idle": 4, "shush": 6}, {}),
    "jogger": ("26773aee-c797-4c20-950d-47db78465fda", {"run": 12}, {}),
    "fitter": ("e0de11f2-246a-40cc-b9e6-3f374eb03d66", {"work": 6}, {}),
    "dj": ("d1ef2972-5ac8-41fe-9a95-09bc4c9a7bc3", {"bob": 9}, {}),
    "barmaid": ("a0121f2c-c4ee-4b9f-a230-c20e513d118f", {}, {}),
    "studio": ("c8b8807b-8583-4513-9db2-c3066f6d172e", {}, {}),
    # (Drawn leaning back on a rail of her own, a life ring behind her: for an open deck, where the
    # rail is behind the people. Not placed yet.)
    "railwoman": ("123c4f2e-bcb8-4651-a3b7-0c4910048c62", {}, {}),
    # Seated on his own office chair, at one of the Internet Cafe's terminals. (A first one,
    # 2c479d41-d01d-46ea-90c3-36cb855461c8, came out a grey figure with a monitor in the air.)
    "surfer": ("33bd2921-f3b1-4b59-b2ce-1f8892bd9eee", {}, {"scale": 0.8}),
    "atriumwoman": ("7a2ebdab-d174-463f-8636-6f915cfe60e8", {}, {}),
    "railman": ("0c8faf8c-a4f6-4920-8785-658c177af315", {}, {}),
    "maid": ("4677d8f1-5586-41e1-b13e-53d9bdd49ffc", {"make": 6}, {}),
    "modelguest": ("d15bae3f-7372-455a-82fc-f4ce9bab224e", {}, {}),
    # A couple reading the ports' plaques on deck 7, their backs to us.
    "plaquewoman": ("da2e0888-a560-4557-9f72-ad92e4f5e772", {}, {}),
    "plaqueman": ("e41a23e9-edd4-4784-8de8-33b29d2de61e", {}, {}),
    # Region 3.
    "stagemanager": ("0c00142e-0038-4dcc-8c93-7c0741317385", {"sneeze": 9, "flap": 10, "idle": 4}, {}),
    "dancer_her": ("24692747-5dde-4578-9a6e-c3ac1adc9df8", {"dance": 9}, {}),
    "dancer_him": ("b14c307c-c551-4381-85e9-74b5610b95cd", {"dance": 9}, {}),
    "croupier": ("935328d2-d98f-44de-889a-bf04e9e86b6d", {}, {}),
    "cowboy": ("9aa4a55c-aea0-46aa-80fb-8642f6d13c99", {}, {}),
    "barman": ("ac5b9c77-3083-4b2b-9615-e7a3a98dc860", {"idle": 4}, {}),
    "shopper": ("21e8d182-fdfa-41ac-ba94-f7f0ef3df251", {"idle": 4}, {}),
    "teen": ("f761c927-d14c-4e1a-b0a8-ed090f28ae99", {}, {}),
    # Seated, each on a seat of their own (they take a built seat's place), shrunk to the others' size.
    "pianist": ("f3cc44c3-8f12-4e1f-95af-3e95eb44c59f", {"play": 8}, {"scale": 0.8}),
    "casinolady": ("1e62b76d-ee89-41aa-adba-a443c7b5d23f", {}, {"scale": 0.8}),
    "aud_gent": ("7a1005bb-985f-4463-87e0-a07a75b1da48", {}, {"scale": 0.8}),
    "aud_lady": ("5b1a8280-b981-4f70-9520-fece33d9532b", {}, {"scale": 0.8}),
    "aud_popcorn": ("5839b55a-2580-4cfc-866c-da9207cb2a8e", {}, {"scale": 0.8}),
    "aud_girl": ("f88758dd-1a25-4b42-91db-96898f49701e", {}, {"scale": 0.8}),
    "aud_granny": ("93caa538-db58-45db-98df-eb42a7277afa", {}, {"scale": 0.8}),
    # Region 4 (Housekeeping): deck 9's corridor, the atrium walks, the laundry.
    "steward": ("f2cc7401-693f-4f93-8915-f3f040c2658c", {"idle": 4, "tug": 8, "walk": 9, "thanks": 8}, {}),
    "bride": ("70b0bc20-aef9-46aa-bd9d-35f56c4c0008", {"idle": 4, "kiss": 7}, {}),
    "groom": ("0c16e385-6331-4d44-87dc-060e70835055", {"idle": 4, "kiss": 7}, {}),
    "spaguest": ("d816e0d8-b223-4288-9a66-257d4cc2466b", {"shriek": 10}, {}),
    # The kid with the water pistol (the pool's, region 6): first seen at his cabin's door.
    "kid": ("59b5cce6-5f2e-45c3-8334-7b2f1eec96c4", {"idle": 4, "walk": 8, "squirt": 11, "eat": 6}, {"scale": 0.72}),
    "bedmaker": ("76a0ee8f-2daf-428c-8a0f-c83445dfbd73", {"make": 8}, {}),
    "domeman": ("7a956cd3-6357-4fa6-a319-020144870524", {"idle": 4}, {}),
    "bagslady": ("1528b5cf-4225-4d4b-85f8-e6f67ed664df", {"walk": 8}, {}),
    "planman": ("3bccf530-3e86-4a11-b6de-c7a049b9572c", {}, {}),
    # The security officer waiting for his uniform in the laundry (after the stage's flour).
    "rival_towel": ("1f2d9528-cb0b-4cd0-9fdd-ae8665ef179e", {}, {"scale": 0.8}),
    # Region 5 (deck 8 forward): the party at the cabin with the balloons.
    "partygirl": ("805b5b9e-f9ba-4091-be45-4b4fb9619843", {"dance": 9}, {"scale": 0.75}),
    # Region 6 (Lido, deck 11). The buffet queue's six, each carrying a tray of their own; the fans
    # on the aft stairs.
    "queue_a": ("7f5590e5-ce63-4740-a8fa-b5b0ddb79795", {"walk": 6}, {}),
    "queue_b": ("ec3c837c-dde4-4147-a113-5ff683c14c9e", {"walk": 6}, {}),
    "queue_c": ("25221bc8-5291-46c9-b1fe-a3ef2dfd5ba9", {"walk": 6}, {}),
    "queue_d": ("4ae6c188-d115-4acb-9ca0-e2cc294966cf", {"walk": 6}, {}),
    "queue_e": ("7d1f88c4-005b-4752-aad5-c86958b996bb", {"walk": 6}, {}),
    "queue_f": ("096244bc-9c59-49bc-8d8d-e0d0483d5c60", {"walk": 6}, {}),
    # Her husband, at the first table of the Great Outdoors. A STAND-IN until the user's photo comes:
    # the linen-shirted diner's character. Replace this id with his own character's.
    "husband": ("89dfbeac-8d4c-4a89-a578-8dbc95ba16fc", {}, {}),
    "fan_a": ("91c28911-98b0-4167-8ca7-06edc793b5a8", {"cheer": 9}, {}),
    "fan_b": ("23af878f-1c70-4d98-bf25-43f971781103", {"cheer": 9}, {}),
    "fan_c": ("25aa68a6-c806-4f18-a5c4-cfc4a8fb5983", {"cheer": 7}, {}),
    # The painter on the midship flight up; the gym's two; Topsiders' barman; guests at the Great
    # Outdoors' far tables, each seated on a wicker chair of their own.
    "painter": ("65140f65-b4ef-4826-9b38-f214bafbcbf6", {"paint": 7}, {}),
    "runner": ("c63d9718-4141-45bd-a4f7-c2e637f8edfe", {"run": 12}, {}),
    "lifter": ("f0fd3504-2ccd-4982-91a9-55e0f6ba4863", {"curl": 7}, {}),
    "barman_top": ("9dca3658-e553-4840-8dc1-16f2be45f8e6", {"shake": 8}, {}),
    "go_reader": ("5f4c8274-b10f-4549-9073-245277a981a5", {}, {"scale": 0.8}),
    "go_her": ("33919b16-1c1c-42a3-a788-b3f0cc837078", {}, {"scale": 0.8}),
    "go_him": ("cc92f5ad-c324-47c6-84da-97466fcd2f18", {}, {"scale": 0.8}),
    # Deck 10's hallway under the pool: who is behind its two "Do Not Disturb" doors, and who throws
    # the swinging one open.
    # (First tries of the two behind the doors, 977c3e8e-4a5b-4e97-b41b-3b09a4917960 and
    # 0be059cb-aed5-4750-aa55-acc699881d77, came with a doorway drawn into the sprite: their
    # descriptions said "in the cabin doorway".)
    "sleeper": ("071b5059-4fef-4ea8-abfd-0b6784aec60d", {"shriek": 10}, {}),
    "curlers": ("2ad7be74-3c6d-4947-a58c-aafc96d29f82", {"shriek": 10}, {}),
    "hurry": ("c17f28af-31b2-4a7b-8094-b0dfde83b7ff", {"idle": 4}, {}),
    # Region 7 (Outside). Behind the hallways' "Do Not Disturb" doors (decks 8 and 10), none dressed
    # for visitors; behind the doors that fly open; the steward on his rounds on deck 8; the guest
    # locked out on his balcony on deck 10; the boat drill's two on the walkway.
    "dnd_shaver": ("7f18618a-5d9e-461e-92fd-8062aa687486", {"shriek": 10}, {}),
    "dnd_facemask": ("396c998d-0109-453e-81fe-b7b5a8f438c6", {"shriek": 10}, {}),
    "dnd_boxers": ("d20a96a6-3001-461c-bf8c-b15a994e4480", {"shriek": 10}, {}),
    "dnd_toothbrush": ("6f8bcf6b-b35d-4157-a071-c10ce0985344", {"shriek": 10}, {}),
    "swing_hawaiian": ("528d7ec8-5ea6-4b74-955c-28036873ee2c", {"idle": 4}, {}),
    "swing_sunhat": ("657f90b7-b6f6-4409-aaf9-2793bedcfd9f", {"idle": 4}, {}),
    "swing_ring": ("659ad453-9baa-4b17-9fd1-6e9fbbfad3f8", {"idle": 4}, {"scale": 0.8}),
    "swing_suit": ("c7651c6c-5c1d-46ed-9efa-74678b21a45b", {"idle": 4}, {}),
    "steward_rounds": ("a36e1cc2-cfb0-4200-abee-a448648fd052", {"push": 8}, {}),
    "balcony_guest": ("6771ef05-487c-4392-bafa-95fa964dc005", {"idle": 4, "wave": 8, "walk": 8, "thanks": 7}, {}),
    "drill_winch": ("a9ac5ab7-cc28-4b90-94c8-a922be66a20d", {"crank": 8}, {}),
    "drill_officer": ("3ed991ae-cf74-4ce1-a636-8549344290a6", {"idle": 4}, {}),
    # Region 8 (deck 12 from Champs aft, the funnel). The old lady sits with her knees drawn up (the
    # game draws her sunbed under her); the diners are drawn seated on chairs of their own.
    "oldlady": ("78fa84ea-9f20-4f85-81f5-5043cd294920", {"read": 4, "glare": 9, "doze": 4, "bolt": 11, "dozing": 2, "fleeing": 9},
                {"scale": 0.8, "cut": {"dozing": ("doze", [6, 7, 8, 7]), "fleeing": ("bolt", [7, 8])}}),
    "engineer": ("819d8399-a91f-48d5-a2b1-47dfd0691eff", {"idle": 4, "walk": 8, "drink": 6, "wave": 8, "climb": 9, "read": 4, "reading": 3},
                 {"cut": {"reading": ("read", [4, 5, 6, 7, 8, 7, 6, 5])}}),
    "teppan_chef_a": ("9190cb8c-6aae-4d16-8a38-a2a81f8973ec", {"flourish": 10}, {}),
    "teppan_chef_b": ("0ed63716-52c2-41e8-af6c-92b069690a24", {"flourish": 10}, {}),
    "sushi_chef": ("1114fd50-c3d7-43f8-9641-0aa91b6f4e49", {"slice": 10}, {}),
    "lobos_waiter": ("64db2435-6028-4c5e-9acb-872151602a96", {"shake": 9}, {}),
    "shuffle_a": ("6f8f13f9-7b6d-41de-950f-a548cd4f1449", {"push": 6}, {}),
    "shuffle_b": ("a52e43f1-5bb8-437c-856e-c650ccfc8a5b", {"idle": 4}, {}),
    "champs_a": ("5f10becb-41fb-4efc-a5e3-9a7c88563c9b", {}, {}),
    "champs_b": ("81fa22b4-2fcc-4f67-b30f-9163f4e7cd66", {}, {}),
    "champs_c": ("65193a43-d567-4270-85ef-74b2632f7861", {"cheer": 8}, {"scale": 0.8}),
    "cagneys_her": ("c3fb03be-54f7-4b0e-aade-1d7134d3b66f", {}, {"scale": 0.8}),
    "cagneys_him": ("cbf3d679-01a3-4ab8-9be2-b4c56be18426", {}, {"scale": 0.8}),
    "sushi_a": ("ab3f381b-f5ba-4c2b-8568-a20a81ed36f3", {}, {"scale": 0.8}),
    "sushi_b": ("e0b56bbe-4964-45bf-94ef-8c8d36c2fd2e", {}, {"scale": 0.8}),
    "bistro_her": ("566ef581-e206-4bc1-a9e5-918e67ac899d", {}, {"scale": 0.8}),
    "bistro_him": ("5c3df12a-4623-482f-adeb-053a4ba12f6c", {}, {"scale": 0.8}),
    "teppan_1": ("5b40cf7b-a23f-41f6-b508-0c35c43fcf42", {}, {"scale": 0.72}),
    "teppan_2": ("d53dac58-6a4f-4439-8030-3226887dba5c", {}, {"scale": 0.8}),
    "teppan_3": ("4e0eae20-2959-4b1b-abeb-a9f188b22326", {}, {"scale": 0.8}),
    "teppan_4": ("42920244-2e84-460a-ab33-36635732b3b1", {}, {"scale": 0.8}),
}
