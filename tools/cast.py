"""The ship's people (GAME_DESIGN.md §6.1.6, docs/population.md §7): each one's PixelLab character
and the clips the game uses. `python tools/fetch_people.py` downloads their frames into
assets/source/people/<name>/ (the standing pose `stand.png`, the figure turned to us `front.png` and away `back.png`, each animation's east frames
`<animation>/<i>.png`); `python tools/build_people.py` packs them into assets/sprites/people.png.

All are PixelLab v3 characters at 64 px, side view (two generations each): that came out at her
height and nearest her look (2026-11-13; a "standard" one was 71 px tall and realistic). Clips are
made with animate_character, east only: a template clip, or skeleton-v3 with one of its moves
(walk, eat, talk, sit_seat...) and poses on top.

**Proportions (the user, 2026-11-13): everyone is drawn to her standard,** a head (hair in, hats
and buns out) of 14 to 20 px on a figure about 60 px tall: hers is 17 of 59. v3 from text does not
keep to it whatever the description says ("realistic proportions, small head" still came out with
a 24 px head): twenty-four of the first hundred came out chibi or near it and were redrawn. **What keeps it:
mode="pro" with style_character_id** = a figure that has it (the drill's officer
3ed991ae-cf74-4ce1-a636-8549344290a6 for men, the cabin maid 4677d8f1-5586-41e1-b13e-53d9bdd49ffc
for women), size 64, view "side": ten generations each, a strict side view. Check a new figure
with `python tools/check_people.py` before placing it. The first characters of those, kept on
PixelLab: rival 68ef5f08, porter 3ad54560, lady 45a8f48c, stagemanager 0c00142e, steward f2cc7401, groom 0c16e385, queue_d 4ae6c188, sleeper 071b5059, curlers 2ad7be74, teppan_chef_b 0ed63716, champs_b 81fa22b4, photographer 89836c72, fan_a 91c28911, fan_b 23af878f, runner c63d9718, cleaner 47c5aa91, dj d1ef2972, fan_c 25aa68a6, receptionist b0851098, librarian 10f3bef9, queue_b ec3c837c, teppan_chef_a 9190cb8c, lobos_waiter 64db2435, champs_a 5f10becb.

A template clip (breathing-idle, walking) redraws the figure and can shrink it by half a head: for a
figure that is seen both standing and in the clip, make it with mode="skeleton-v3" and the same
template_animation_id (three generations), which keeps its size (the photographer's "idle2").

name: (character id, {clip: frames per second}, options). A clip is an animation of that name on
the character; "stand" is its standing pose. Options: "flip": the sprite was drawn facing west;
"scale": shrunk by that much (a seated figure that came out as tall as the standing ones); "cut":
{name: (clip, [frames])} a loop made of some of a clip's frames.
"""

CAST = {
    # Region 1.
    "officer": ("4d3e6422-a934-40e0-a47d-e841378610ae", {}, {}),
    # (On the bridge, region 9: "swing" is the net brought down, cut from "swat"; a first try,
    # "lunge", ran with the net over his shoulder.)
    "rival": ("c76f8ffa-277f-405f-ae3b-0268a53e2fb4", {"trip": 12, "peek": 5, "swing": 10},
              {"cut": {"swing": ("swat", [2, 3, 4, 5, 7, 8])}}),
    "porter": ("00c30095-76c1-4898-a423-34f740532970", {}, {}),
    "waiter": ("3423e6b8-f2d5-423f-86ee-b9c77809194c", {}, {}),
    "tourist": ("5d966249-7a4c-42ab-9ba8-d1384fae259a", {}, {}),
    "robe": ("9d68ff5f-80b7-4187-86a9-7cd9eff01bed", {}, {}),
    "stewardess": ("29866bd3-ce11-4319-8e99-7d6de7ffaef8", {}, {}),
    "receptionist": ("8adf75c5-2558-4a05-aa70-b0f9749f1348", {}, {}),
    "photographer": ("5e90962a-b76e-453f-a096-265ee177de4f", {"idle": 4}, {"cut": {"idle": ("idle2", [0, 1, 2, 3])}}),
    "gentleman": ("4a0085ce-78f1-476c-8863-3f3fc461190f", {}, {}),
    "lady": ("e321871f-7108-427e-bd99-c4e260ed9428", {}, {}),
    "cleaner": ("efe40b7d-0352-4356-bf82-dc77f19def4d", {}, {}),
    "agent": ("4f239177-54ca-4b07-b1e6-7d9475c8d35b", {}, {}),
    "maitre": ("8336eefc-5d4f-452c-b70d-d3ca545505c8", {}, {}),
    "chef": ("6ca50f05-0ef1-4094-af3c-9ec00846cd36", {}, {}),
    "folder": ("fe49270a-7cd3-4f5d-84ee-3e47316bc16f", {}, {}),
    # Diners, drawn seated on their own dining chairs (they stand in a chair's place at a table),
    # shrunk like every seated figure: PixelLab draws a seated one as tall as a standing one.
    "diner_red": ("6dc96ff4-58fc-4a8d-b5c7-1bb111a772fc", {}, {"scale": 0.8}),
    "diner_suit": ("126b575d-bac9-4369-a721-7aa957e0bb5f", {}, {"scale": 0.8}),
    "diner_teal": ("f2700aec-2d7f-48b8-8025-4313be63f2ce", {}, {"scale": 0.8}),
    "diner_linen": ("89dfbeac-8d4c-4a89-a578-8dbc95ba16fc", {}, {"scale": 0.8}),
    # Region 2.
    "librarian": ("c7f368e7-11e5-4d3b-b5dd-112c8f71a53a", {"shelve": 7, "idle": 4, "shush": 6}, {}),
    "jogger": ("26773aee-c797-4c20-950d-47db78465fda", {"run": 12}, {}),
    "fitter": ("e0de11f2-246a-40cc-b9e6-3f374eb03d66", {"work": 6}, {}),
    "dj": ("68e66eb2-4d14-48c8-9acc-37bb6d1001aa", {"bob": 9}, {}),
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
    # (The stage manager's "flap" is his second, "flap2": the first, from poses, hardly moved the arms
    # that hold his clipboard.)
    # ("applaud", cut from "clap": he and the planner clap her home, step 10: src/world/finale.js.
    # Each claps against the clipboard in the other hand.)
    "stagemanager": ("e6153c00-599b-41a5-8c3a-4d3f562b1ad1", {"sneeze": 9, "flap": 10, "idle": 4, "applaud": 9},
                     {"cut": {"flap": ("flap2", [1, 2, 3, 4, 5, 6]), "applaud": ("clap", [3, 4, 5, 6, 7, 6, 5, 4])}}),
    "dancer_her": ("24692747-5dde-4578-9a6e-c3ac1adc9df8", {"dance": 9, "idle": 4}, {}),
    "dancer_him": ("b14c307c-c551-4381-85e9-74b5610b95cd", {"dance": 9, "idle": 4}, {}),
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
    "steward": ("88741662-8a90-437a-bca4-c996663761ff", {"idle": 4, "tug": 8, "walk": 9, "thanks": 8}, {}),
    "bride": ("70b0bc20-aef9-46aa-bd9d-35f56c4c0008", {"idle": 4, "kiss": 7}, {}),
    "groom": ("146b63d6-6f03-4675-9b0a-5d79914315ba", {"idle": 4, "kiss": 7}, {}),
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
    "queue_b": ("84bf7071-becd-4d3a-8f93-686affe25c02", {"walk": 6}, {}),
    "queue_c": ("25221bc8-5291-46c9-b1fe-a3ef2dfd5ba9", {"walk": 6}, {}),
    "queue_d": ("709fc84f-77bc-4693-bb48-4a1de35ba6e5", {"walk": 6}, {}),
    "queue_e": ("7d1f88c4-005b-4752-aad5-c86958b996bb", {"walk": 6}, {}),
    "queue_f": ("096244bc-9c59-49bc-8d8d-e0d0483d5c60", {"walk": 6}, {}),
    # Her husband, at the first table of the Great Outdoors. A STAND-IN until the user's photo comes:
    # the linen-shirted diner's character. Replace this id with his own character's.
    "husband": ("89dfbeac-8d4c-4a89-a578-8dbc95ba16fc", {}, {"scale": 0.8}),
    "fan_a": ("dc207d50-0515-4a17-b85e-03130517536d", {"cheer": 9}, {}),
    "fan_b": ("76e60a27-a813-4456-8d85-e7830eb21730", {"cheer": 9}, {}),
    "fan_c": ("beeb5d2c-2cc0-4145-98d0-b570504269aa", {"cheer": 7}, {}),
    # The painter on the midship flight up; the gym's two; Topsiders' barman; guests at the Great
    # Outdoors' far tables, each seated on a wicker chair of their own.
    "painter": ("65140f65-b4ef-4826-9b38-f214bafbcbf6", {"paint": 7}, {}),
    "runner": ("134f92ce-a8aa-42a8-9a03-ec6539e27d08", {"run": 12}, {}),
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
    "sleeper": ("99d9d8bf-34fc-4265-86b5-1f5f6a176657", {"shriek": 10}, {}),
    "curlers": ("08f18b17-7aeb-4779-b22f-038849dff7d3", {"shriek": 10}, {}),
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
    # (The first chef's "flourish" is his second, "flourish2": in the first he turned to face us and
    # sparks were drawn into the frames.)
    "teppan_chef_a": ("64b21a54-a081-444c-8ab3-c911eb069453", {"flourish": 10},
                      {"cut": {"flourish": ("flourish2", [1, 2, 3, 4, 5, 6, 7, 8])}}),
    "teppan_chef_b": ("2598efbb-c8a0-4125-a731-7c43ec6f8a26", {"flourish": 10}, {}),
    "sushi_chef": ("1114fd50-c3d7-43f8-9641-0aa91b6f4e49", {"slice": 10}, {}),
    "lobos_waiter": ("0d3e8eeb-65c4-42e6-8367-ee902890f063", {"shake": 9}, {}),
    "shuffle_a": ("6f8f13f9-7b6d-41de-950f-a548cd4f1449", {"push": 6}, {}),
    "shuffle_b": ("a52e43f1-5bb8-437c-856e-c650ccfc8a5b", {"idle": 4}, {}),
    "champs_a": ("0f1e2f4d-b920-48a0-af67-78c769d69054", {}, {}),
    "champs_b": ("3d41e4f4-0058-47d8-bf6a-03c3e82226b4", {}, {}),
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
    # Region 9 (The bow). The wedding party in deck 12's forward lobbies: the planner, the couple,
    # four guests; Cagney's pastry chef; the Spinnaker's barman; the kids' pool's two; the spa's
    # receptionist, masseuse, stylist and step class; the officers of decks 9 and 10; the kids'
    # club's counsellor. (Loops are cut from the frames before a clip turns the figure to face us
    # or drops what it holds; the planner's "fret" and a guest's "laugh" did both and were dropped.)
    # (Six came out with heads of 21 to 25 px from text and were made again
    # with mode="pro": the first ones, kept on PixelLab: wed_groom 8e25f1ec, wed_guest_a b5c89fa2, wed_guest_c 08532590, pastrychef 69bb0340, barman_sp e01475fd, counsellor b3ee4e51.)
    "planner": ("cc307b42-5ec9-4c95-a846-76882b67ab75", {"idle": 4, "walk": 8, "applaud": 9},
                {"cut": {"applaud": ("clap", [3, 4, 5, 6, 7, 6, 5, 4])}}),
    "wed_bride": ("ab0e8199-c60d-402d-a5d4-186f33bc3793", {"idle": 4, "walk": 7, "kiss": 7}, {}),
    "wed_groom": ("cd8f0a2b-e837-48aa-8c6a-f613ddc8befe", {"fuss": 7, "walk": 8, "kiss": 7}, {"cut": {"fuss": ("fidget", [0, 1, 2, 3, 2, 1])}}),
    "wed_guest_a": ("d311befd-5e0e-4d64-b63a-a9d8dd7c8ea0", {"sip": 6, "walk": 8}, {}),
    "wed_guest_b": ("7875101f-fbc8-4a40-8a53-b0987fc26e98", {"walk": 8}, {}),
    "wed_guest_c": ("3560d751-4dd5-441e-b6ac-fe17c9251393", {"walk": 8}, {}),
    "wed_guest_d": ("9d99e1c2-7611-4536-bb0b-0ea545ee1635", {"walk": 8}, {}),
    "pastrychef": ("4bdd435f-84cb-4f3a-bd36-2106d0b693be", {"idle": 4, "sigh": 7}, {}),
    "barman_sp": ("8a4fd600-d655-4810-bced-3fcc89f29d61", {"shine": 7}, {"cut": {"shine": ("polish", [0, 1, 2, 3, 4, 5, 6, 7, 8, 6, 4, 2])}}),
    "spa_reception": ("d45cc830-9766-4229-a74f-c950873b6e0f", {"bow": 8}, {}),
    "masseuse": ("2fefa59f-b6af-4f92-8133-41d5c5256da8", {"knead": 7}, {}),
    "stylist": ("42d60ae5-b735-40b6-b118-5cb62efa8577", {"work": 6}, {"cut": {"work": ("snip", [0, 1, 2, 3, 2, 1])}}),
    "stepper_a": ("b360c69a-412b-45aa-a318-38495b31dde9", {"steps": 9}, {"cut": {"steps": ("step", [2, 3, 4, 5, 6, 7, 8])}}),
    "stepper_b": ("6be4ce88-e432-45d4-9efe-84d79ad27e4e", {"steps": 8}, {"cut": {"steps": ("step", [2, 3, 4, 5, 6, 7, 8])}}),
    "officer_9": ("62e25632-167d-4c88-b585-04d3e606dd4e", {"walk": 8}, {}),
    "officer_10": ("3c827584-0209-4260-8e66-2982801bb0d9", {"walk": 8}, {}),
    "counsellor": ("2a5a0882-b53f-4069-af2a-92b877c3305a", {"cheer": 9}, {"cut": {"cheer": ("clap", [3, 4, 5, 6, 7, 8, 7, 6, 5, 4])}}),
    "poolkid_a": ("7638cecb-28a1-4d16-b1ca-f32388314e3b", {"hop": 9}, {"scale": 0.62, "cut": {"hop": ("jump", [3, 4, 5, 6, 7, 8])}}),
    "poolkid_b": ("8c73e72a-ca99-49ed-861f-12b4314638de", {"hop": 9}, {"scale": 0.66, "cut": {"hop": ("bounce", [3, 4, 5, 6, 7, 8])}}),
}
