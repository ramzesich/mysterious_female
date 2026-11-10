# Populating the ship: the spec

Every object, item, person, hazard, secret and scene the plan of `GAME_DESIGN.md` §6.1 puts on the
ship, in place, with its behaviour. A spec to build from (2026-11-10), not code: positions are metres
from the bow on the deck named (the builder's `x_of(m)`), and the build snaps them to the map's tiles
and to the rules of `CLAUDE.md` (a cabin door is never within 2 m of a crew door or a trunk; nothing
floats; human-sized things are sized to her). Where this spec and §6.1 differ, this spec is the later,
finer word, and §6.1 was patched to match (the funnel's door, the balcony partitions, the tangerines).

Each entity has an **id** for the layout file (`tools/ship_layout.py`) and the map builder:
`npc_` a person, `amb_` scenery people (no collision, no bubble), `haz_` a hazard or obstacle, `blk_`
a block on a flight, `rdr_` a card reader on a door or flight, `door_` a one-way or scripted door,
`tan_` a tangerine, `book_` a library book, `item_` another pickup, `src_` a tray source, `cp_` a
checkpoint, `sec_` a secret or quirk, `slot_` a photo slot, `room_` an enterable room, `bb_` a Bumbot
beat, `riv_` a rival appearance, `scn_` a scripted scene, `sign_` a sign, `gull_` and `gust_` the
weather.

## 1. The behaviour catalogue

Behaviours are named once here and referenced by the tables. Distances in metres, times in seconds,
speeds in m/s (her run is about 4 m/s; a cabin door every 4 m).

| Behaviour | Meaning |
|---|---|
| `static` | Stands or sits in place with an idle clip. A bubble shows its pictogram when she is within the range given and the errand is open |
| `loop(a, b, v)` | Walks between a and b at v, turning at the ends; a collision is the effect named (a bump, a spill, a block) |
| `patrol(a, b, v, act)` | Like loop, with an action `act` fired when she is in range in front of it |
| `platform(a, b, v)` | A moving thing she can stand on; it stops and beeps while she is within 2 m ahead of it on the floor |
| `timed(T, t, span)` | Every T seconds it is active for t seconds over the span named; contact while active is the scare named; the tell shows 0.7 s before |
| `random(T1-T2, t)` | As timed, with a random period between T1 and T2 |
| `reactive(r, d)` | Fires when she comes within r, after a tell lasting d; then rests 4 s |
| `trap(r)` | Hidden: fires on contact or on passing within r at running speed; its tell is a muted background prop |
| `block(lift)` | A thing or person across a flight with a rope and a sign; `lift` is the event that removes it for good |
| `oneway(from)` | A door shut from one side until she has come through it from `from`; then open both ways |
| `pickup` | E takes it (books, cards, the socks, the parasol); tangerines are taken by touch |
| `source(thing)` | E takes a tray of `thing`; it always has more |
| `machine` | The soft serve: hold E, release in the band (§6.1.2) |
| `room` | An enterable room shown in the corridor's place, the deck dimmed round it (`ROOM_DIM`); E at its door goes in and out |
| `quirk(trigger)` | A moment with no reward: `still(s)` after standing still s seconds on the spot; `E` on the thing |
| `scene` | Scripted, input locked, steps listed in §9 |
| `glimpse(when)` | Bumbot or the rival seen in the background once, unreachable, under the condition named |

Scares follow §5.6: contact with a hazard plays the fright named, she runs off the screen, and she
steps out of the closest activated checkpoint (§5.5), everything kept. A hazard that would get her
while she carries a tray spills the tray instead (never a scare) unless the table says otherwise.

## 2. The global tables

### 2.1 The cards and the verbs

| Id | What | Where | How | Opens |
|---|---|---|---|---|
| `item_card_deck` | Deck card, blue | Deck 4, 66, the gangway officer | Given for his lunch | §6.1.5 |
| `item_card_ent` | Entertainment card, red | Deck 6, 246, the stage manager | Given for his pills | §6.1.5 |
| `item_card_hk` | Housekeeping card, green | Deck 9, 126, the steward | Given for his cart | §6.1.5 |
| `item_card_off` | Officer's card, gold | Deck 12, 136, on the sun deck | Dropped by the rival at the horn; a glint; E | Every reader |
| `item_dash` | The dash | Deck 5, 247, the fruit bowl | The scream at near-catch 1, the D glyph as she takes the first tangerine | §3.2 |
| `item_push` | Pushing carts | Deck 9, 122, the steward's cart | The E glyph at the cart's end | Carts, the laundry cart, the library's ladder |
| `item_crawl` | Crawling | Deck 9, the linen room's vent | The ↓ glyph on the cart under the vent | The duct, laundry lines, the pillow fort |
| `item_socks` | Grip socks | Deck 11, 96, the gym's rack | E; the glyph: jump at a wall | Wall jumps |
| `item_parasol` | The parasol | Deck 12, 130, the old lady's sunbed, after the horn | E; the glyph: hold jump in the air | The glide |

### 2.2 The ten books

Pocket items; the HUD counts them. Returned at `src_trolley` (deck 6, 167); read at `sec_chair`
(deck 6, 172). The titles are the user's. Each book's page, read in the chair, hints at the hidden
thing named (drawn, no words).

| Id | Region | Where | How she gets it | Its page hints at |
|---|---|---|---|---|
| `book_1` | 1 | Deck 5, 96, a table at the Atrium Café, by a half-drunk coffee | Pickup, before she knows what it is for | The galley's crate behind the Seven Seas' crew door |
| `book_2` | 2 | The lifeboat at 140 on the boat walkway, on its bench | Pickup inside `room_lifeboat` | The trap door in the stage |
| `book_3` | 3 | Deck 6, 254, the dressing room's make-up table | Pickup inside `room_dressing` (the stage door, red) | The jackpot machine's glint |
| `book_4` | 4 | Deck 9, 134, the honeymoon couple | Their thanks for their picture | The pantry passage between the kitchens |
| `book_5` | 5 | Deck 8, cabin 8206, on the bed | Pickup; standing still on the bed with it, she reads there instead of the bounce | Deck 7's stern strip |
| `book_6` | 6 | Deck 11, 216, her husband | His thanks for a perfect cone | Los Lobos' piñata |
| `book_7` | 7 | Deck 10, 235, the balcony guest | His thanks for his door | The telescope on the funnel |
| `book_8` | 8 | Deck 12, 129, the old lady's sunbed, after the horn | Pickup | The lighting bridge over the stage |
| `book_9` | 8 | The funnel's top, 180, the engineer | He lends it after the horn | The chapel's moment |
| `book_10` | 9 | Deck 10, 38, the bridge's chart table | Pickup | The odd book on the library's top shelf |

### 2.3 The tangerines (41)

Placed where food is; by touch. Trim to taste; §6.1 says about 40.

| Deck | m | Id | On what | Count |
|---|---|---|---|---|
| 4 | 30 | `tan_4_30` | Behind the breakable luggage stack | 1 |
| 4 | 112 | `tan_4_laundry` | A shelf in the laundry (`room_laundry`) | 1 |
| 4 | 165 | `tan_4_store` | Crates in the dry store (`room_store`) | 2 |
| 5 | 90 | `tan_5_cafe` | The Atrium Café's fruit bowl | 1 |
| 5 | 190 | `tan_5_dessert` | The Four Seasons' dessert cart | 1 |
| 5 | 247 | `tan_5_bowl` | The Seven Seas' fruit bowl, knocked over by Bumbot | 3 |
| 5 | 253 | `tan_5_galley` | The crate in the galley (`room_galley`), breakable | 2 |
| 6 | 26 | `tan_6_high` | The fire-hose cabinet's top, reached from the delivery robot's roof | 1 |
| 6 | 142 | `tan_6_windjammer` | The Windjammer's bar | 1 |
| 7 | 160 | `tan_7_jackpot` | The jackpot machine (`sec_jackpot`) | 2 |
| 7 | 180 | `tan_7_tradewinds` | A gift basket in Tradewinds | 1 |
| 8 | 41.4 | `tan_8_8206` | The welcome basket in cabin 8206 | 2 |
| 8 | 246 | `tan_8_aft` | A room-service tray by a door, deck 8 aft | 1 |
| 8 (out) | 100 | `tan_8_balc_fwd` | A balcony table | 1 |
| 8 (out) | 245 | `tan_8_balc_aft` | A balcony table | 1 |
| 9 | 150 | `tan_9_balcabin` | The balcony cabin's basket | 1 |
| 9 | 172 | `tan_9_cart` | A standing cart | 1 |
| 9 | 180 | `tan_9_luggage` | Behind the luggage stack, breakable | 1 |
| 9 (out) | 240 | `tan_9_balc` | A balcony table | 1 |
| 10 | 182 | `tan_10_mid` | A room-service tray | 1 |
| 11 | 32 | `tan_11_spa` | The spa reception's fruit bowl | 1 |
| 11 | 145 | `tan_11_topsiders` | Topsiders' bar | 1 |
| 11 | 176 | `tan_11_fruit` | The Garden Café's fruit counter | 2 |
| 11 | 209 | `tan_11_crates` | Behind stacked crates at the service station, breakable | 2 |
| 12 | 54 | `tan_12_spinnaker` | The Spinnaker's bar | 2 |
| 12 | 128 | `tan_12_lady` | The old lady's thanks for her cocktail | 2 |
| 12 | 166 | `tan_12_cagneys` | Cagney's bread basket | 1 |
| 12 | 211 | `tan_12_pinata` | Los Lobos' piñata, broken by the dash | 2 |
| The funnel | 186 | `tan_funnel` | The engineer's lunch box | 1 |
| | | | **Total** | **41** |

### 2.4 The photo slots (6)

A framed picture; E opens it full screen; the picture is the user's (§6.4).

| Id | Where | Needs |
|---|---|---|
| `slot_lifeboat` | Inside the lifeboat at 140 | `room_lifeboat` |
| `slot_lighting` | The lighting bridge's end, over the stage | `room_lighting` (red) |
| `slot_stern` | Deck 7's stern strip, 253, on the stern structure | A drop from deck 8's stern terrace; the socks to climb back |
| `slot_chapel` | The chapel, on its wall | After the cake |
| `slot_nook` | The reading nook's wall | All ten books, the odd book |
| `slot_table` | The table with her husband, 216 | A perfect cone for him (the frame stands on the table after) |

### 2.5 The checkpoints (17)

Crew doors (§5.5), except the two cabins named. "Closest activated" per §5.5.

| Id | Deck | m | Door | Region |
|---|---|---|---|---|
| `cp_gangway` | 4 | 62 | The gangway lobby's crew door (the start) | 1 |
| `cp_4_aft` | 4 | 212 | A crew cabin door by the aft lobby | 1 |
| `cp_laundry` | 4 | 112 | The laundry's door | 4 |
| `cp_6_fwd` | 6 | 40 | A crew door among the forward cabins | 2 |
| `cp_library` | 6 | 193 | The Library's crew door (exists) | 2 |
| `cp_foyer` | 6 | 200 | The theatre foyer's crew door | 3 |
| `cp_7_aft` | 7 | 196 | The aft lobby's crew door | 3 |
| `cp_station` | Boat walkway | 128 | The station locker's steel door | 7 |
| `cp_9_mid` | 9 | 190 | A crew door at the corridor's aft end | 4 |
| `cp_balcabin` | 9 | 150 | The balcony cabin's door (a cabin, the exception) | 7 |
| `cp_8206` | 8 | 41.4 | Cabin 8206's door (the exception) | 5 |
| `cp_gym` | 11 | 80 | The forward lobby's crew door by the gym | 6 |
| `cp_garden` | 11 | 192 | The Garden Café's service door | 6 |
| `cp_technical` | 12 | 165 | The technical door, the roof ladder's foot | 8 |
| `cp_funnel` | The funnel's top | 178 | The engineer's locker | 8 |
| `cp_officer` | 10 | 60 | An officer's cabin door | 9 |
| `cp_chapel` | 12 | 72 | The chapel lobby's crew door by the restrooms | 9 |
| `cp_bridge` | 10 | 40 | The bridge's crew door (the finale's retry) | 10 |

### 2.6 The locks

Readers (`rdr_`) sit beside the door or at the flight's foot, lit in their colour; fire doors open
freely from above or from inside (§6.1.2). Blocks (`blk_`) stand across the flight with a rope and a
sign. Every stair core has its own: forward 74-82, midship 102-110, aft 194-202, the atrium 82-102.

| Id | Where | Kind | Opens or lifts |
|---|---|---|---|
| `rdr_fwd_5_6` | Forward core, flight 5-6 | Blue | The Deck card |
| `blk_cleaner` | Midship core, flight 5-6 | The cleaner mopping, a cone, "WET FLOOR" | Region 3 opens |
| `blk_rehearsal` | Aft core, flight 5-6 | A rope, "REHEARSAL IN PROGRESS" | Region 3 opens |
| `blk_photographer` | The atrium's stairs, 5-6, on deck 5 at 86 | The photographer, a backdrop across the stairs | Region 3 opens |
| `rdr_fwd_7_8`, `rdr_mid_7_8`, `rdr_aft_7_8` | Each core, flight 7-8 | Green | The Housekeeping card from below; free from above |
| `blk_carpet` | The atrium's stairs, 7-8, on deck 7 at 88 | A roll of carpet across the flight, the fitter kneeling | Region 4 opens |
| `rdr_mid_8_9`, `rdr_aft_8_9`, `rdr_mid_9_10`, `rdr_aft_9_10` | Midship and aft cores | Green | As above |
| `rdr_fwd_9_lobby`, `rdr_fwd_10_lobby` | The forward lobbies of decks 9 and 10: their doors at 74 and 82 | Gold | The Officer's card; the flights pass through untouched |
| `blk_towels` | Midship core, flight 10-11 | A table of towel animals across the landing, "PLEASE DO NOT TOUCH" | Region 6 opens |
| `blk_fans` | Aft core, flights 10-11 and 11-12 | Three fans with drinks, a rope, "BIG GAME" | Region 8 opens |
| `blk_paint` | Midship core, flight 11-12 | The painter, cones, "WET PAINT" | Region 8 opens |
| `blk_wedding` | Forward core, flight 11-12, and deck 12's lobbies 67-82 | The wedding party | The cake |
| `rdr_magnums` | Deck 7, 110, the midship lobby's door into Magnum's | Red | The Entertainment card; free from Magnum's side |
| `rdr_entourage` | Deck 7, 74, the forward lobby's door into Entourage | Gold | The Officer's card |
| `rdr_trunk_bliss` | Deck 6, 118 and deck 7, 118, the Bliss/Magnum's trunk's doors | Red | The Entertainment card |
| `rdr_stagedoor` | Deck 6, 254, the stage door | Red | `room_dressing` |
| `rdr_booth` | Deck 7, 206, the lighting booth | Red | `room_lighting` |
| `rdr_gate` | The promenade, 125, the lifeboat station's gate | Blue | The ladder to the boat walkway |
| `rdr_balcabin` | Deck 9, 150, the balcony cabin's door | Green | `room_balcabin_9` |
| `rdr_guest` | Deck 10, 235, the balcony guest's door | Green | `room_guest_10` |
| `rdr_pantry_5a`, `rdr_pantry_5b` | Deck 5, 167 and 169 | Green | `room_pantry` (both ends) |
| `rdr_store` | Deck 4, 165 | Green | `room_store` |
| `rdr_laundry` | Deck 4, 112 | Green | `room_laundry` |
| `rdr_chute` | Deck 9, the linen room's hatch | Green | The chute |
| `rdr_coldroom` | Deck 11, 185, the Garden Café's cold room | Green | `room_coldroom` |
| `rdr_spa` | Deck 11, 74, the spa's door | Gold | The spa |
| `rdr_bridge` | Deck 10, 40, the bridge's door | Gold | The bridge |
| `door_library_aft` | Deck 6, 194 | Shut by `blk_quiet` (a rope, "QUIET PLEASE") | Bumbot knocks the rope into it (`bb_2`) |
| `door_8_fwd_lobby` | Deck 8, 74 | `oneway(the corridor)` | The duct drops her inside |
| `door_8_mid_lobbies`, `door_8_aft_lobbies`, `door_9_aft_lobbies`, `door_10_mid_lobbies`, `door_10_aft_lobbies` | Each hallway's doors at its lobby ends | `oneway(the corridor)` | A balcony door, or the pool's hatch |
| `door_theatre_trunk` | Deck 4, 240 | `oneway(deck 6)` | The theatre's trunk, as built |
| `door_midships_trunk_6` | Deck 6, 125 | `oneway(deck 6)` | Opens from Bliss first |
| `door_mooring` | Deck 7, 21.4 | Shut; opens from the mooring deck after the catch | The way home |
| `door_hatch_bridge` | Deck 10, 27, the ceiling | Shut until the alarm (`scn_alarm`) | The ladder drops |
| `door_hatch_pool` | Deck 11, 125, the pool's floor | Hidden until the pool drains (`scn_drain`) | A drop into deck 10 |

### 2.7 The glass elevator's panel and the cores' panels

| After | The glass elevator lights | The cores' elevators light |
|---|---|---|
| The start | 5 | 4, 5 |
| Region 2 | 5, 6, 7 | 4-7 |
| Region 4 | 5-10 | 4-10 (8 and 10 at their midship lobbies) |
| Region 6 | 5-10 | 4-11 |
| Region 8 | 5-10 | 4-12 |

### 2.8 The HUD and the save

The HUD: four card slots (lit when held); the tangerine count; the dash's countdown; the books'
count; the carried thing with its meter (a melting cone, a cooling cup); a key glyph the first time a
verb is possible. The save keeps: the cards, the verbs, the regions opened, each block lifted, each
one-way door opened, each book (found, returned, read), each tangerine taken, each secret and quirk
seen, each errand's state, each Bumbot beat done, the machine refilled, the kid's ally state, the old
lady's doze, the wedding, the horn, the alarm, the catch, the way home; the towel's place (§8).

## 3. The decks, bow to stern

Columns: metres, id, what, behaviour, needs (art or a room). Ambient people (`amb_`) never block
or scare. Venues' spans are the layout's (`tools/ship_layout.py`).

### Deck 4 (region 1)

**Forward cabins 20-60, "arrivals".** Calm, one lesson, one breakable.

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 24 | `amb_lost` | A passenger in a bathrobe studying the deck plan upside down | `static`, scratches his head | A character |
| 30 | `haz_luggage_4` | A stack of delivered suitcases across the corridor, `tan_4_30` behind | Breakable (the dash); hoppable otherwise (it is low) | Suitcases (atlas has one) |
| 50 | trunk `fwd-cabins` | The trunk's door, decks 4-5, free | As built | |
| 56 | `sign_lockdown_1` | A "SEARCH IN PROGRESS" poster | Decor | A sign |

**The gangway lobby 60-74 (the start).**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 62 | `cp_gangway` | The crew door | Checkpoint, lit from the start | Built |
| 66 | `npc_officer` | The gangway security officer at his post by the shell door | `static`; bubble (a tray) within 4 m; E with the lunch tray: he eats (3 s), hands `item_card_deck` (`scn_card_deck`) | Idle, eat, hand over |
| 67 | spawn | Her start | As built | |
| 62-72 | `haz_porter` | The porter pushing a loaded luggage cart | `loop(62, 72, 1.0)`; a bump: "Bumped"; hop it (the cart is 1 m high) | The porter, the cart |

**Cabins 82-102, under the atrium.** Quiet; one cart to hop at 90 (`haz_cart_4_90`, standing).

**Cabins 110-194, "the service deck".**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 112 | `room_laundry` | The laundry behind a green crew door (`rdr_laundry`, `cp_laundry`): washers, dryers, carts, steam, the chute's mouth in the ceiling, `tan_4_laundry` on a shelf, `amb_folder` folding towels | `room`; she lands here from the chute (`scn_chute`) | Drawn by hand |
| 118-150 | `haz_vacuum_4` | The robot vacuum (built) | `loop(118, 150, 1.2)`; contact "Іііі!"; the dash shoves it spinning into a doorway for 6 s | Built |
| 130 | `amb_robe` | A passenger in a bathrobe looking for the spa | `static`, turns a map | A character |
| 156-162 | decor | Doors with vacation stickers (built) | | |
| 165 | `room_store` | The dry store (`rdr_store`): shelves, `tan_4_store` in crates | `room` | Drawn by hand |
| 182 | `haz_cart_4_182` | A standing room-service cart | Hop | Built |
| 188 | `sign_board` | The crew notice board: rosters, a lost-cat notice with no picture | Decor, a wink | A sign |

**Cabins 202-255, "crew quarters".**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 212 | `cp_4_aft` | A crew cabin door | Checkpoint | Built door |
| 220 | `haz_cart_4_220` | A standing cart | Hop | Built |
| 224-236 | `sign_names` | Crew cabin name plates (the user's in-jokes, §6.1.15) | Decor | Plates |
| 232 | `room_sm_cabin` | The stage manager's cabin: a bunk, show posters, a shelf; `item_pills` on the shelf once he has asked | `room`; E at the shelf takes the pills | Drawn by hand |
| 240 | trunk `theatre` | The trunk's lower door | `oneway(deck 6)`, as built | |

### Deck 5 (region 1)

**Cabins 20-74, "morning".** 30 a standing cart (`haz_cart_5_30`); 44 `amb_breakfast`, a steward
with a breakfast tray knocking at a door (ambient); 50 the trunk's upper door; 62 an open cabin door,
a guest in a bathrobe at the window (`amb_robe_5`, a peek, no room).

**The atrium floor 82-102.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 84 | `amb_reception` | Guest Services' receptionist | `static` | A character |
| 86 | `blk_photographer` | The photographer and his backdrop at the curving stairs' foot | `block(region 3)`; he poses passengers (`amb_posers`, a couple) | Three characters |
| 88-100 | `amb_trio` | A string trio on the atrium floor (optional) | `static`, a play loop | Three characters |
| 90 | `tan_5_cafe` | The café's fruit bowl | | |
| 96 | `book_1` | The book on a café table | `pickup` | A book |
| 92 | `sec_lift_glimpse` | The glass elevator at deck 5: the car's panel lights 5 only | | Built |

**Shore excursions, reservations 110-150.** Decor; `amb_agent` at the desk.

**La Cucina 150-168.** `amb_cucina_diners` (two at a table); `rdr_pantry_5a` at 167.

**The pantry 167-169 (`room_pantry`).** A passage with shelves, crates; doors at both ends (green);
a shortcut past the waiter; built as a short room. Drawn by hand.

**The Four Seasons 168-194.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 169 | `rdr_pantry_5b` | The pantry's other door | Green | |
| 170-192 | `haz_waiter` | The waiter with a tray, the only one in the game | `loop(170, 192, 1.5)`; a bump spills her tray; hop him otherwise | Walk with tray |
| 180 | `sec_swan` | The ice swan | `quirk(E)`: she shivers | A clip |
| 190 | `tan_5_dessert` | The dessert cart | | |

**The Seven Seas 202-255.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 203 | `amb_host` | The host at the welcome counter | `static` | A character |
| 210-240 | `amb_diners_7s` | Three tables of diners | `static` | Characters |
| 247 | `tan_5_bowl` | The fruit bowl, knocked over by Bumbot | Three tangerines roll to 244-246 after `bb_1` | |
| 250 | `src_lunch` | The pass by the crew door: the officer's lunch tray | `source(lunch)` after `bb_1` | A tray |
| 250 | `bb_1` | Bumbot eating the lunch on the counter | `scene` §9.1 | His `eating` |
| 253 | `room_galley` | The galley behind the crew door: the pass, a chef (`amb_chef_7s`), `tan_5_galley` in a breakable crate, the trap door's landing at 248 (`scn_trapdoor`) | `room` | Drawn by hand |

### Deck 6 (region 2; the theatre region 3)

**Cabins 20-64, "the robot".**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 24-60 | `haz_robot` | The delivery robot, a tall tray-carrying robot | `platform(24, 60, 0.8)`; its roof is 1.4 m up: a hop onto it; it carries her; it stops and beeps while she is within 2 m ahead on the floor | An object, two frames |
| 26 | `tan_6_high` | On the fire-hose cabinet's top, 2.2 m up | Reached from the robot's roof | |
| 40 | `cp_6_fwd` | A crew door | Checkpoint | |
| 48 | `amb_maid` | A cabin being made up, its door open, a stewardess inside | A peek | A character |

**The Internet Café 64-74.** `amb_surfer` at a terminal.

**The atrium walk 82-102.** `amb_couple_6` at the balcony rail; the glass elevator's car (`bb_lift`,
§9.2); the stairs up to 7 open.

**Bliss 110-124.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 114 | `amb_dj` | The DJ in his booth | `static`, bobs | A character |
| 117 | `sec_dance` | The dance floor | `quirk(still 3)`: she dances | A clip |
| 118 | `rdr_trunk_bliss` | The crew trunk's deck 6 door, red (the way to region 4) | As built, decks 6-7-9 | Trunk art built |

**The shops, Perspectives 124-136.** 125 the midships trunk's deck 6 door (`oneway(deck 6)`); 132
`haz_flash`: the studio's camera on its tripod, `timed(6, 1, 130-134)`: in its flash she stops and
poses for 1 s, the screen whites (no scare; `amb_photog_2` behind the camera).

**The Windjammer 136-150.** `amb_barman_wj`; `amb_model_ship` a guest with the model ship; `tan_6_windjammer` at 142.

**The Photo Gallery 150-160.** Decor; `sec_cat_photo`: one photo in the rows is a black cat's tail
leaving the frame (a wink, no trigger).

**The Library 160-194, her place.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 162-166 | `sec_shelf` | The shelf with ten gaps behind the desk | Fills as books come back | Drawn by hand |
| 164 | `npc_librarian` | The librarian at her desk | `static`; bubble (a book and the gapped shelf) within 4 m while any book is out; shelves each book (`scn_shelve`); a finger to her lips when she runs past | Shelve, idle, shush |
| 167 | `src_trolley` | The return trolley, "RETURN" | E with a book: returned | A trolley |
| 172 | `sec_chair` | The red reading chair by the window | `quirk(E)` with a book: she reads (an idle), the page shows (§2.2) | A clip, ten pages |
| 178 | `bb_2` | Bumbot asleep on the open book on the reading table | `scene` §9.3 | His `asleep` |
| 184-190 | `sec_ladder` | The rolling ladder on the bookcase | Pushed along 170-192 (the push verb); climbable (ladder) | Drawn |
| 186 | decor | The chess table, the globe | | Built |
| 188 | `sec_oddbook` | The odd book on the top shelf | E with all ten shelved: the bookcase swings (`scn_nook`) | |
| 186-192 | `room_nook` | The reading nook behind the bookcase: an armchair, a lamp, a porthole on the sea, `slot_nook`; the reading idle | `room` after `scn_nook` | Drawn by hand |
| 193 | `cp_library` | The crew door | Checkpoint | Built |
| 194 | `door_library_aft` + `blk_quiet` | The aft door and its rope stand | Shut until `bb_2` | A rope stand |

**The theatre 202-255 (region 3).**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 200 | `cp_foyer` | The foyer's crew door | Checkpoint | |
| 206-240 | decor | Rows of seats (built); `amb_audience` three seated | | |
| 242 | `haz_pit` | The orchestra pit in front of the stage | A one-deck drop for the rival only (she can hop it) | Drawn |
| 244-254 | `haz_lights` | The stage lights, swinging after `bb_3` | `timed(4, 1.2, 244-254)` over the stage, two lights alternating; contact "Bonked" | Drawn |
| 246 | `npc_stagemanager` | The stage manager | `static`; sneezes every 5 s; bubble (a pill bottle) after `bb_3`; E with the pills: `item_card_ent` (`scn_card_ent`) | Sneeze, flap, talk |
| 248 | `haz_trapdoor` | The trap door, a square seam | `trap`: standing on it drops her into `room_galley` (one deck, no scare) | Drawn |
| 249 | `sec_spotlight` | Centre stage | `quirk(still 3)`: she bows | A clip |
| 249 | `bb_3` | Bumbot washing in the spotlight | `scene` §9.4 | His `washing` |
| 250 | decor | The fly rope he rides | | Drawn |
| 251 | `amb_dancers` | Two dancers rehearsing | A loop until `bb_3`, then they sit on the edge | Two characters |
| 254 | `rdr_stagedoor` + `room_dressing` | The stage door (red) and the dressing room: a make-up table with bulbs, costumes on a rail, `book_3` | `room` | Drawn by hand |
| 240 | trunk `theatre` | The one-way trunk's upper door | As built | |

**The promenade 100-231 (outside deck 6).**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 111, 138, 162, 186 | doors | The promenade doors (built) | | |
| 116-212 | `haz_jogger` | The jogger on the JOGGING lane | `loop(116, 212, 2.2)`; a bump "Bumped"; hop him, or stand on the WALKING lane by the wall as he passes (a 1 m strip where he never runs) | Run clip |
| 125 | `rdr_gate` | The lifeboat station's gate in the railing and its ladder up the column to the boat walkway | Blue; the ladder free from above | A gate |
| 150, 175, 200 | `gull_prom` | Gulls perched on the railing | Flap up when she is within 3 m, settle again; harmless | Gulls |
| 190 | `riv_prom` | The rival peering up under a boat with his net | `glimpse(region 2, once)` | The rival |
| 150 | `bb_glimpse_window` | A black shape passing behind a promenade window | `glimpse(region 2, once)` | A silhouette |

### Deck 7 (regions 2, 3, 9, 10)

**The mooring deck 0.5-21.4 (region 10).** Bollards, cleats (built); `scn_catch` at the tip;
`door_mooring` at 21.4.

**Splash Academy 21.4-45 (region 9).**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 24-27 | `amb_toddlers` | Three toddlers at the play kitchen | `static` | Characters |
| 28-34 | `haz_fort` | A pillow fort across the room | Crawl through (the crawl verb) | Drawn |
| 38 | `amb_nanny` | The youth counsellor | `static` | A character |
| 60 (Entourage) | `haz_ballpit` | The ball pit, 50-58, across Entourage | She sinks to the waist and wades at half speed; no scare; a jump gets her out at its ends | Drawn |
| 70 | decor | The arcade cabinet, foosball (built) | | |
| 74 | `rdr_entourage` | The door to the forward lobby | Gold | |

**The forward lobby 74-82, the atrium walk 82-102 (region 2).** `blk_carpet` at 88 on the 7-8
flight; `amb_couple_7` reading the ports' plaques.

**Magnum's 110-130 (region 3).** `rdr_magnums` at 110 (red; free from inside); `rdr_trunk_bliss` at
118 (the trunk's deck 7 door); `amb_barman_mag`, `amb_pianist` at the bar's piano.

**The Art Gallery 130-150.** Decor; `sec_cat_painting` at 140: a painting of a black cat on an
easel, which she looks at twice if she stands still (a 1 s double-take; no reward).

**The casino 150-172.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 152, 156, 166 | `haz_chips` | Three slot machines that pay out | `random(8-14, 4)`: the lights race 1.5 s (the tell), then chips spill 2 m in front for 4 s: a slip ("Slipped") | Drawn |
| 160 | `sec_jackpot` | The machine with a glint | `quirk(E)` once: lights, a ding, `tan_7_jackpot` pour out | A glint |
| 166-171 | `amb_tables` | The croupier and two players at roulette and blackjack | `static` | Characters |

**Tradewinds 172-186.** `tan_7_tradewinds` at 180 in a gift basket; `amb_shopper`.

**The Arcade 186-194.** Decor (the claw machine); `amb_teen`.

**The aft lobby 194-202.** `cp_7_aft` at 196.

**The Stardust balcony 202-254.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 206 | `rdr_booth` + `room_lighting` | The lighting booth (red): the console, a window on the stage, a door onto the catwalk over the stage (244-254 at ceiling height), `slot_lighting` at its end, the hatch Bumbot vanished through (decor) | `room` | Drawn by hand |
| 210-240 | `amb_balcony_seats` | Two seated | | |
| 244-254 | the rail | The railing over the stage: hop it and drop onto the stage (built) | | |

**Deck 7's stern strip (behind deck 8's end, 252-254).** `slot_stern` at 253 on the stern structure.
In: a drop from deck 8's stern terrace. Out: a wall jump up the stern plating (the socks), or a scare.

**The boat walkway (outside, deck 7's height, 100-231).**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 125 | ladder top | From `rdr_gate` | | |
| 128 | `cp_station` | The station locker | Checkpoint | A locker |
| 104-230 every 9 | boats | The lifeboats, tenders, rescue boat (built) | | |
| 140 | `room_lifeboat` | The one lifeboat with its hatch open: inside, benches, an oar, `book_2`, `slot_lifeboat`, a porthole | `room`; E at the hatch | Drawn by hand |
| 185-194 | `haz_drill` | The boat drill: two crew at the davit winch, a rope and a "DRILL" sign | `timed(10, 3, 185-194)`: the boat swings out across the walkway and back; contact "Bumped" | Two characters, the boat's swing |
| 210 | `riv_walkway` | The rival looking into a boat | `glimpse(region 7, once)` | |
| 110-231 | the wall | The recess's wall: wall jumps up to deck 8's balconies (the socks) | | |

### Deck 8 (regions 5, 7)

**The forward corridor 21.4-74 (region 5), "calm, hers".**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 18.7-21.4 | the terrace | The forward terrace past the wall (built) | | |
| 30 | `amb_swan_cart` | A steward's cart with a towel swan on it | Decor | A towel animal |
| 41.4 | cabin 8206 | Her cabin (built): `tan_8_8206` in the welcome basket, `book_5` on the bed, the shower (§8) | `cp_8206` | Built |
| 56 | `amb_peek_sea` | An open cabin door, the sea in its window, nobody in | A peek | Built pieces |
| 66 | `door_duct_exit` | The duct's exit grille in the ceiling | She drops out of it (`scn_duct`) | Drawn |
| 72 | `amb_party` | A cabin's door with balloons spilling out, music | Decor; the duct's peek above it | Balloons |
| 74 | `door_8_fwd_lobby` | The lobby door | `oneway(the corridor)` | |

**The atrium walk 82-102, the midship lobby 102-110 (region 4).** Built; `rdr_fwd_7_8`, `rdr_mid_7_8`.

**The midships hallway 110-194 (region 7), "the hotel at full swing".** Entered from its balcony
cabin at 150 or from the lobbies once opened.

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 110, 194 | `door_8_mid_lobbies` | The lobby doors | `oneway(the corridor)` | |
| 114-190 | `haz_steward_rounds` | A steward pushing a cart on his rounds | `loop(114, 190, 0.9)`; every 8 m he pulls the cart into a doorway for 3 s: the gap to pass; otherwise a full-width block that pushes her back | A character, a cart |
| 124-128 | `haz_trays_8m` | Three room-service trays on the floor | `trap`: stepping on one clatters and opens `haz_dnd_8m` | Trays |
| 126 | `haz_dnd_8m` | A "Do Not Disturb" door | Opens on the clatter, or on E: a startled guest in a towel: "Startled" if she is within 2 m | A character |
| 136 | `haz_swing_8m` | A cabin door that swings open | `reactive(3, 0.6)`: the handle turns, the door swings out 1 m for 1.5 s; contact "Bonked" | Drawn |
| 146 | `sign_wet_8m` + `haz_sprinkler_8m` | A wet-floor sign (muted) and the sprinkler in the doorway at 148 | `timed(5, 2, 147-149)`; contact "Drenched"; the open parasol passes | Drawn |
| 150 | `room_balcabin_8m` | The balcony cabin whose balcony door stands ajar (housekeeping airing it): the way in from outside; its corridor door opens from inside | `room` | The generic balcony cabin, drawn by hand |
| 176 | `amb_ice` | An ice bucket and two glasses on a tray outside a door | Decor | |
| 184 | `haz_cart_8_184` | A standing cart | Hop | |

**The aft hallway 202-251.5 (region 7), "the breakfast rush".**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 202, 251.5 | `door_8_aft_lobbies` | The lobby door and the terrace wall's doorway | `oneway(the corridor)` | |
| 206-226 | `haz_trays_8a` | Six trays on the floor every 3-4 m | `trap` as above, each opening the nearest of two DND doors (210, 222) | |
| 230 | `room_balcabin_8a` | The ajar balcony cabin | `room` | |
| 238 | `haz_swing_8a` | A swinging door | `reactive(3, 0.6)` | |
| 246 | `tan_8_aft` | A tray with a tangerine | | |
| 251.5 | the terrace | The aft terrace (built); the drop to the stern strip; the stern tiers' wall jump up to deck 9's terrace | | |

**Deck 8's balconies (outside, 73-251).**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| all | partitions | Solid partitions, taller than a jump, running to the rail: going along a deck needs a wall jump off the partition (the socks); up a deck, a wall jump up it onto the balcony above; down, a drop onto the balcony below (one deck, fine) | | The partitions are drawn |
| all | `gust_balc` | Gusts along the ship's side | Every 7 s, 1.5 s, a push aft of 1 m while airborne; the towels on the rails flap 0.7 s before, then a line of spray | Code, a towel sprite |
| 100, 245 | `tan_8_balc_fwd`, `tan_8_balc_aft` | Balcony tables | | |
| 120, 160, 200, 240 | `gull_8` | Perched gulls | A swoop when she lingers more than 2 s within 3 m; the shadow 1 s before; contact "Swooped"; a cone held up takes it away | Gulls |
| 135, 215 | `haz_line_8` | Laundry lines across the balcony | Crawl under | Drawn |
| 150, 230 | balcony doors | The ajar doors of `room_balcabin_8m`, `room_balcabin_8a` | In | |
| 180 | `haz_sunbather` | A sunbather behind a "Do Not Disturb" sign on his balcony | Entering it: "Startled" (she backs out) | A character |

### Deck 9 (regions 4, 7, 9)

**The forward corridor 23.6-74 (region 9), "officers' country".** Calm. 30 `sign_captain`: the
captain's cabin door with its name plate (the user's in-joke; E: it is locked, a polite knock); 40-70
`amb_officer_9` an officer walking with a clipboard (`loop(40, 70, 1.0)`, friendly, she passes him);
the forward terrace past 23.6.

**The midship lobby and the atrium walk 82-110 (region 4).** Built; the trunk from Bliss comes up in
the corridor at 118, not here.

**The midships corridor 110-194 (region 4), "housekeeping hour": the designed gauntlet.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 112 | the linen room | Built (§8): `bb_4` asleep in the towel heap; the laundry cart (push); the vent (crawl, `scn_duct`); the chute hatch (`rdr_chute`, `scn_chute`) | `scene` §9.5 | The vent's inside |
| 118 | `rdr_trunk_bliss` | The trunk's deck 9 door, red, where she arrives | | |
| 122 | `haz_cart_steward` | The steward's cart jammed across the corridor in a cabin's doorway | The push glyph; E at its east end and walk east: it rolls to 130 and stands there (hop); it cannot be passed before | A cart |
| 126 | `npc_steward` | The steward | `static`; bubble (a cart) within 4 m until the cart is free; then `scn_card_hk`: `item_card_hk` | Idle, thanks |
| 134 | `npc_honeymooners` | The honeymoon couple at their door, a camera held out | `static`; bubble (a camera) within 3 m; E: she takes their picture (a clip, the flash, they kiss), `book_4`; then they go in | Two characters |
| 140 | `room_cleanup` | The cabin mid-cleanup, its door open: the bed stripped, a cart inside | `room` (nothing to find; the hazards are at its door) | The inside cabin, drawn by hand |
| 140 | `haz_vacuum_9` | The vacuum inside the cabin | `reactive(2, 0.3)`: it darts 2 m out of the doorway and back; contact "Іііі!" | Built |
| 141 | `haz_towels_9` | The towel stack in the doorway | `trap(1)` at running speed: it topples onto her: "Buried"; walking past is safe (it wobbles as the tell) | Drawn |
| 146 | `sign_wet_9` + `haz_sprinkler_9` | The wet-floor sign and the sprinkler at 148 | `timed(5, 2, 147-149)`; "Drenched" | |
| 150 | `rdr_balcabin` + `room_balcabin_9` | The balcony cabin (green, the card's first use): the generic balcony cabin; `tan_9_balcabin` in its basket; its balcony door out onto the balcony (a dead end until the socks: the partitions); `cp_balcabin` | `room` | Drawn by hand |
| 158 | `haz_swing_9` | A cabin door that swings open | `reactive(3, 0.6)`; "Bonked" | |
| 166 | `haz_dnd_9` | A "Do Not Disturb" door | E: "Startled"; otherwise nothing | |
| 172 | `haz_cart_9_172` + `tan_9_cart` | A standing cart with a tangerine | Hop | |
| 176, 184 | `room_adjoin_a`, `room_adjoin_b` | Two adjoining cabins with a connecting door between them | `room`: in at 176, through the connecting door, out at 184: the way past the stack | The inside cabin, with a connecting door |
| 180 | `haz_luggage_9` | A stack of delivered luggage, full height, `tan_9_luggage` behind | Breakable (the dash) or the adjoining loop; not hoppable | Suitcases |
| 190 | `cp_9_mid` | A crew door | Checkpoint | |
| 194 | the lobby door | Open (region 4 includes the aft lobby); deck 9 aft's corridor door shut from the lobby (`door_9_aft_lobbies`) | | |

**The aft hallway 202-249.5 (region 7), "the sprinkler test".** 206 `haz_swing_9a`; 214 and 222
`haz_sprinkler_9a`, `haz_sprinkler_9b`, two sprinklers 8 m apart out of phase (`timed(5, 2)` each,
offset 2.5 s): a rhythm to run; 225 `room_balcabin_9a` (the ajar door, the way in); 230
`haz_cart_9_230`; 240 the terrace wall's doorway; the aft terrace (built).

**Deck 9's balconies (outside).** As deck 8's: `gust_balc`; `gull_9` at 130, 170, 210; `haz_line_9`
at 195; `tan_9_balc` at 240; the ajar door at 225; the balcony cabin's own balcony at 150 (region 4's
view: from it, `bb_glimpse_balcony` on deck 10's rail at 160, a deck up).

### Deck 10 (regions 4, 6, 7, 9)

**The bridge 25-40 (region 9).**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 27 | `door_hatch_bridge` | The emergency hatch in the ceiling and its ladder (drops at the alarm) | `scn_alarm` | Drawn |
| 29 | `haz_alarm_panel` | The alarm panel on the wall (built piece, moved here) | Hit by the rival's net | Built |
| 30 | `bb_6` | Bumbot on the main console | `scene` §9.9 | |
| 26 | `riv_bridge` | The rival creeping with the net | Part of `bb_6` | |
| 33 | decor | The captain's chair (the rival slumps in it after) | | Built |
| 38 | `book_10` | On the chart table | `pickup` | |
| 40 | `rdr_bridge` + `cp_bridge` | The bridge's door (gold) and its crew door checkpoint | | Built door |

**The officers' corridor 40-74 (region 9).** 50-70 `amb_officer_10` (`loop`, friendly); 60
`cp_officer`; the lobby's gold doors at 74 and 82 (`rdr_fwd_10_lobby`).

**The midship lobby and the atrium walk 82-110 (region 4).** Open over the atrium (built).

**The midships hallway 110-194 (region 6), "the hallway from the hatch".**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 110, 194 | `door_10_mid_lobbies` | The lobby doors | `oneway(the corridor)` | |
| 118 | `haz_cart_10_118` | A standing cart | Hop | |
| 125 | landing | Where the pool's hatch drops her (`door_hatch_pool`) | | |
| 128-131 | `haz_trays_10m` | Trays on the floor | `trap`, opening `haz_dnd_10m` at 130 | |
| 130 | `haz_dnd_10m` | A "Do Not Disturb" door | As deck 8's | |
| 145 | `haz_swing_10m` | A swinging door | `reactive(3, 0.6)` | |
| 154 | `sign_wet_10m` + `haz_sprinkler_10m` | The sign and the sprinkler at 156 | `timed(5, 2)` | |
| 170 | `haz_dnd_10m2` | A second "Do Not Disturb" door | E only | |
| 182 | `tan_10_mid` | A tray | | |

**The aft hallway 202-247 (region 7), "the balcony guest's".**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 202, 247 | `door_10_aft_lobbies` | The lobby door and the terrace doorway | `oneway(the corridor)` | |
| 206-209 | `haz_trays_10a` | Trays | `trap`, opening `haz_dnd_10a` at 208 | |
| 215 | `room_balcabin_10a` | The ajar balcony cabin, the way in | `room` | |
| 224 | `haz_swing_10a` | A swinging door | | |
| 235 | `rdr_guest` + `room_guest_10` | The balcony guest's cabin (green): inside, his balcony door; E at it lets him in: `scn_guest` (thanks, `book_7`); his balcony door then an entry | `room` | The generic balcony cabin |
| 240 | `haz_cart_10_240` | A standing cart | Hop | |

**Deck 10's balconies (outside).** `gust_balc`; `gull_10` at 150, 190, 230; `haz_line_10` at 125,
245; `bb_glimpse_balcony` at 160 (Bumbot swiping at a gull on the rail: `batting`, the gull flaps
off; `glimpse(region 4, once)`, seen from deck 9's balcony cabin); the ajar door at 215;
`npc_balcony_guest` at 235 on his balcony (`static`, waves, a bubble with a door within 4 m, until
let in).

### Deck 11 (regions 6, 9, 10)

**The balcony forward of the spa 24-29.5 (region 10).** The hatch's top at 27; the glass windscreen
along the Spinnaker balcony's front above bars the jump down from deck 12 (§6.1.9); `scn_sunset`.

**The spa 29-74 (region 9).**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 32 | `tan_11_spa` + `amb_spa_reception` | The reception's fruit bowl, the receptionist | | |
| 42-48 | the sauna | Built; `haz_steam` at its aft door 48: `timed(5, 1.5, 48-49.5)`, a puff; contact "Fogged" | A puff sprite |
| 50 | `amb_masseuse` | At a massage table | | |
| 58 | `amb_salon` | A stylist and a guest under the hood dryer | | |
| 68 | `amb_aerobics` | Two in a step class | A loop | |
| 74 | `rdr_spa` | The spa's door, gold | | Built door |

**The forward lobby 74-82.** `cp_gym` at 80; `rdr_fwd_11` none (the flight from 10 is open; the
lobby doors on 9 and 10 are the gold ones).

**Fitness 82-102.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 86 | `amb_treadmill` | A runner on a treadmill | A loop | |
| 92 | `amb_weights` | A man with dumbbells | | |
| 96 | `item_socks` | The grip socks on the rack by the yoga mats | `pickup`; the glyph | An icon |

**The pool deck 110-160.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 112 | `sec_chess` | The giant chess set | `quirk(E)`: she moves a piece | |
| 119-131, 134-140 | the pools | Built; the first drains in `scn_drain` | | |
| 123-128 | `gull_pool` | Two gulls circling over the gap where deck 12 is open above the pool | Dive at food within 4 m (the shadow 1 s before); a cone held up takes one away 20 s; gone while the kid is an ally | Gulls |
| 125 | `door_hatch_pool` | The maintenance hatch in the drained tank's floor | E: a drop into deck 10 at 125 | Drawn |
| 128 | `haz_lever` | The drain lever on its housing | Thrown by Bumbot | Drawn |
| 130 | the pool ladder | Built | | |
| 131 | `bb_5` | Bumbot fishing at the first pool's aft rim | `scene` §9.7 | |
| 131-213 | `sec_pawprints` | Wet paw prints along the deck aft to the ice cream machine, fading over 60 s after `bb_5` | Decor | Drawn |
| 132 | `sec_hottub` | The hot tub | `quirk(E)`: she sits in it, steam | A clip |
| 136-160 | `npc_kid` | The kid with the water pistol | `patrol(136, 160, 1.0, squirt)`: squirts when she is within 4 m in front, every 2.5 s, the jet 3 m: "Splashed"; a jump clears him; the dash: he runs to 160 and hides 10 s; with a cone in her hand he waits, bubble (a soft serve); a stub: he takes it, frowns, resumes in 3 s; perfect: he eats, ally for good: `patrol(135, 160)` squirting gulls | Walk, squirt, run, eat |
| 142 | `riv_loungers` | The rival on his knees looking under a lounger; the kid squirts him now and then | `glimpse(region 6)`, a loop | |
| 145 | `src_cocktail` + `tan_11_topsiders` | Topsiders' bar: the mojito for the old lady (`source(cocktail)` once her errand is open), the barman (`amb_barman_top`), a tangerine | | |
| 149 | `sign_wet_11` | The wet-floor sign, muted, by the showers | | Built style |
| 150-153 | `haz_wet` | The wet patch | On it she slides at her speed until the patch ends: into the pool at 140 if she came from aft (a splash, fine) or into the deck chair; the socks: no slide; a jump clears it | Drawn |
| 155 | `haz_deckchair` | The sliding deck chair at the patch's aft edge | When she lands on the patch it rocks (the tell) and slides at her: "Bumped"; the socks: it stays | A chair |
| 110-146 | the walk above | Deck 12's side walk covers the pool deck except the gap over 123-128 | | Built |

**The Garden Café 160-194.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 162-180 | `haz_queue` | The buffet queue: six passengers with trays shuffling along the counter | `loop(162, 180, 0.4)` as a snake with a gap after every third; a full block that pushes her back; hop it at a gap | Shared bodies |
| 176 | `tan_11_fruit` | The fruit counter | | |
| 185 | `rdr_coldroom` + `room_coldroom` | The cold room (green): frost, shelves, `item_canister` (the ice cream mix, a heavy tray: no jumps at all) | `room`; E at the canister | Drawn by hand |
| 192 | `cp_garden` | The service door | Checkpoint | |

**The aft lobby 194-202.** `blk_fans` on the flights 10-11 and 11-12.

**The Sports Bar 202-210.** `amb_sportsbar` (three at the TV after region 8; empty before, the fans
are on the stairs).

**The Great Outdoors 210-244, his place.**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 209 | `haz_crates` | Stacked crates behind the service station, `tan_11_crates` behind | Breakable | Crates |
| 211 | `src_coffee` | The coffee machines | `source(coffee)`: a hot cup on a tray; a "keep it hot" meter, 50 s | A cup |
| 213 | `src_icecream` | The soft serve machine | `machine`: hold E; perfect, stub or toppled; empty after the first cone until `item_canister` is poured in (E); a cone melts in 45 s; a cone is gull bait | The meter, three cones |
| 213 | `sec_cone` | A cone for herself | `quirk(E)` with no errand open: she eats it where she stands | A clip |
| 216 | `npc_husband` | Her husband at the first table, a cone in hand, looking at the wake | `static`; bubble (the canister) once the machine is empty; bubble (a cone) once it is refilled and the kid is fed; E with a perfect cone: `scn_table` (they eat together, `slot_table` appears on the table, `book_6`) | From the user's photo; sit, eat, wave, the moment |
| 216 | `slot_table` | The framed picture on the table after `scn_table` | | |
| 210-222 | the climb | The service station's roof (2 m), the first table's parasol top (2.6 m), a wall jump off deck 12's end wall at 220 onto the sun cover's low end at 222, up the cover to the aft terrace | The socks | Built cover |
| 225, 235 | `gull_go` | Perched gulls | Dive at food within 4 m; a cone as bait; a swoop otherwise when she lingers | |
| 230-240 | `amb_tables_go` | Two tables of guests | | |

### Deck 12 (regions 8, 9)

**The Spinnaker balcony 31-44 (region 9).** The windscreen (built); `gull_bow_b` six gulls on the
windscreen until the horn; a bench.

**The Spinnaker Lounge 44-57.5.** 48 `sec_piano` (`quirk(E)`: a few notes); 54 `tan_12_spinnaker`
at the bar, `amb_barman_sp`; `amb_lounge` two in armchairs.

**The kids' pool 57.5-67.** 60 `sec_slide` (`quirk`: walk onto the slide's top: she rides it into
the pool); `gull_bow_a` six gulls on the rim until the horn (they flap in her face: "Swooped" if she
pushes through before the horn; the way through is then the pool itself, swimming under them);
`amb_kids_pool` two kids.

**The chapel lobby 67-74.** 68.6 the chapel (built): `scn_ceremony` after the cake, `slot_chapel`
inside; 72 `cp_chapel`; `blk_wedding`: the planner at 76, four guests at 70-80 across the lobbies.

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 76 | `npc_planner` | The wedding planner with a clipboard | `static`; bubble (a cake) within 4 m; E with the cake box: `scn_wedding` | Idle, clipboard |
| 70-80 | `amb_wedding_guests` | Four guests chatting across the lobby | A block until `scn_wedding` | Shared bodies |

**Champs Bar 82-102.** `amb_champs` three at the TVs; the midship lobby 102-110 with `blk_paint` on
the 11-12 flight (the painter, "WET PAINT").

**The sun deck 110-146 (the side walk over the pools).**

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 119-140 | the walk | ↓ drops her through into the pool below (built) | | |
| 126-131 | `npc_oldlady` | The old lady on her sunbed across the walk, bags and towels, a book in her hands | `static`; glares within 4 m; a full block (jump the sunbed from the rail side, or ↓ into the pool); bubble (a cocktail glass) within 3 m; E with the mojito: she dozes (`tan_12_lady` from her bag), still a block; at the horn (`scn_horn`) she bolts forward and is gone: `item_parasol` at 130, `book_8` at 129 | Sit, read, glare, doze, bolt |
| 138 | `riv_sundeck` | The rival searching under the loungers | `glimpse(region 8)` until the horn; at the horn he jumps, drops `item_card_off` at 136, runs forward | |
| 140 | `amb_sunbathers` | Two on loungers | | |

**Sports 146-164.** 148-160 the court's cage; `haz_balls` at 150 and 158: `timed(4, 2, 2 m out)`
alternating, a basketball bounces out, twice, and rolls back: "Bonked"; 161-164 shuffleboard,
`amb_shuffle` two players; `sec_court` (`quirk(E)` at the court's gate with a ball lying there: she
scores).

**Cagney's 164-174.** 165 `cp_technical`: the "TECHNICAL, CREW ONLY" door at the restaurants'
forward end, the ladder behind it up to the roof (the plan's "by Teppanyaki" moved here: the funnel's
base is solid and the stairway climbs its forward face, so the ladder must come up forward of it);
`npc_engineer` stands at it (below); 166 `tan_12_cagneys`; 173 `src_cake`: Cagney's pass behind a crew
door, `npc_pastrychef` (`static`, sighs when a cake is dropped), `source(cake)` once the planner has
asked; `amb_cagneys` diners.

| m | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| 165 | `npc_engineer` | The engineer at the technical door | `static`; bubble (a steaming cup) within 4 m; E with the hot coffee: he drinks, waves her up, climbs the ladder (`scn_engineer`); afterwards he is at the top | Idle, drink, climb, wave, read |

**The Sushi Bar 174-182.** `amb_sushi_chef` behind the counter; two diners. (No sign secret: dropped.)

**Teppanyaki 182-194.** 186-190 `haz_flare`: the chef (`amb_teppan_chef`) flares the grill
`timed(6, 1, 186-190)`: "Singed"; the flourish is the tell. `amb_teppan` four at the counter.

**The aft lobby 194-202.** `blk_fans` from below.

**Le Bistro 202-208.** `amb_bistro` diners. **Los Lobos 208-214.** 211 `sec_pinata`: the piñata hung
from the ceiling; the dash breaks it: `tan_12_pinata`; `amb_lobos` a waiter with maracas (ambient).

**The aft terrace 214-220.** `gust_terrace` (every 7 s); 220 the rail: hop onto the sun cover and
down to the Great Outdoors (built); `gull_terrace` at 218 perched.

### The roof, the funnel's stairway and its top (region 8)

| Where | Id | What | Behaviour | Needs |
|---|---|---|---|---|
| The roof, 166-169 | the ladder's top, a walk to the stairway's foot | Built ladder, moved to 166 | | |
| The stairway, 169 up to 177 | `gust_funnel` + `gull_funnel` | Gusts every 5 s; two gulls circling, a swoop every 6 s along the stairway: "Swooped"; a slip is a fall onto the roof (one storey, fine), from the top a long fall | | |
| The lattice, 175 | `bb_glimpse_funnel` | Bumbot sitting on the lattice as she climbs; at the horn he shoots down it and forward along the roof | `glimpse(region 8)` | |
| The top, 178 | `cp_funnel` | The engineer's locker | Checkpoint | |
| 180 | `npc_engineer` (after) | The engineer on his break, reading | After the horn: E, he lends `book_9` | |
| 184 | `sec_horn` | The horn's cord | E once he is up: `scn_horn` (the pull clip, the shake, the smoke, the cascade) | A cord, a clip |
| 186 | `tan_funnel` | His lunch box | | |
| 188 | `sec_telescope` | The lookout telescope | `quirk(E)`: the view swings to deck 7's stern strip for 3 s and back | A telescope |

### The stern tiers (outside, decks 7-11 at the stern)

The decks' aft terraces step back; with the socks, a wall jump up each step's plating climbs from
deck 7's stern strip to deck 8's terrace, 9's, 10's and deck 11's Great Outdoors: a secret route up
the stern and the way back from `slot_stern`. `gust_balc` applies.

## 4. The corridors: the rules that made them

- **A beat every 8-12 m, never two of the same kind in a row,** with 6 m of nothing between beats;
  one reward (a tangerine, a book, a peek) every 25-30 m; one enterable cabin per stretch; one gag
  or glimpse per stretch; a checkpoint at the stretch's end.
- **Every stretch has its own theme and one element found nowhere else:** deck 4 forward the
  arrivals' luggage, deck 4 midships the laundry and the dry store, deck 4 aft the crew's name plates
  and the stage manager's cabin, deck 5 forward the morning trays, deck 6 forward the delivery robot
  to ride, deck 8 forward the calm and the balloons, deck 8 midships the steward on his rounds, deck
  8 aft the breakfast rush of trays, deck 9 forward the captain's door, deck 9 midships the full
  gauntlet (the push lesson, the honeymooners, the mid-cleanup cabin, the adjoining cabins), deck 9
  aft the two sprinklers out of phase, deck 10 forward the officers, deck 10 midships the hatch's
  landing and the "Do Not Disturb" chain, deck 10 aft the balcony guest.
- **The hazards escalate by region:** region 1 one moving thing and one breakable per stretch;
  region 4 five beats with the first combinations (the vacuum and the towel stack at one door, the
  sprinkler before the balcony cabin); region 7's hallways are optional and dense; regions 5 and 9
  are calm on purpose.
- **Each deck looks its own without new corridor art:** the cabin numbers' plaques (built) take a
  coloured band per deck (8 blue, 9 green, 10 terracotta); the framed pictures differ per deck (deck
  4 safety posters and rosters, 5 paintings of the ship, 6 old port maps, 8 seascapes as built, 9
  botanical prints, 10 old liners' posters), one props sheet of pictures if PixelLab draws them (10
  generations) or cropped from the user's photos; the "Do Not Disturb" signs, trays, ice buckets and
  towel animals outside doors are the life.
- **Nothing hurts her while she carries a tray except a spill,** so a tray carried along a
  hallway is a route choice, not a trap.

## 5. The outside, summarised

The promenade (the jogger, the gate, the gulls), the boat walkway (the station locker, the lifeboat,
the drill), the balconies of decks 8-10 (partitions as walls, gusts, perched gulls, laundry lines,
the ajar doors, the sunbather, the balcony guest), the stern tiers, the terraces at the decks' ends
(built), deck 11's open decks (the pool gap's gulls, the Great Outdoors' gulls), deck 12's open decks
(the kids' pool's gulls until the horn, the sun deck, the court, the aft terrace's gusts), the roof
and the funnel (gusts, circling gulls), the balcony forward of the spa and the mooring deck (the
finale's gusts and two crossing gulls). Gulls are one creature with four states (perched, flap,
swoop, glide) and a per-instance rule from the tables.

## 6. Scenes

Input locked unless said; each sets its save flag.

1. **`bb_1` near-catch 1 (deck 5, 250):** she comes within 3 m of the pass; Bumbot eats on the
   counter; she walks up and bends, the scream bubble "Кісюнічка!!!"; he leaps west along the
   counter, the fruit bowl topples (three tangerines roll to 244-246), he runs out of the Seven Seas
   westward and is gone at the aft lobby; she straightens, turns to us; play resumes; the D glyph
   shows as she takes the first tangerine; `src_lunch` is now a source. Once, later, as she reaches
   the forward stairs' reader with the card: `bb_glimpse_stairs`, a tail up the flight.
2. **`bb_lift` the glass elevator (deck 6's atrium walk):** the first time she stands within 10 m of
   the glass elevator, the car waits at deck 6 with Bumbot sitting in it, doors open; when she is
   within 4 m the doors close and the car rises to deck 9, seen through the glass, and comes back
   empty. Input stays free.
3. **`bb_2` near-catch 2 (the library, 178):** he is asleep on the open book on the reading table;
   she bends; he leaps east, runs to 194, the rope stand topples into the door, which swings ajar and
   stays so (`door_library_aft` open); she turns to us.
4. **`bb_3` near-catch 3 (the stage, 249):** triggered when she first stands on the stage; he washes
   in the spotlight; the stage manager at 246 flaps; she bends; the rival runs in from the wing at
   254, trips on the cable at 251 and tumbles off the stage's front into the pit at 242; the lights
   start to swing (`haz_lights` on for good); Bumbot leaps onto the fly rope at 250 and rides up out
   of view; the stage manager's bubble turns to the pill bottle. Then `scn_card_ent` when she brings
   them: he takes them, sneezes once more, hands the card.
5. **`bb_4` near-catch 4 (the linen room):** he sleeps in the heap; she bends; he leaps to the vent
   and squeezes in; the push glyph shows on the laundry cart. **`scn_duct`:** with the cart under the
   vent and ↓ on it she crawls in; the duct room: she crawls west about twenty seconds with grilles
   at 100 (the lobby's light), 90 (the dome's glow), 72 (the balloons), 68 (a snoring passenger); at
   the end grille, ↓ kicks it out and she drops into deck 8 at 66. **`scn_chute`:** E at the hatch
   with the green card: a whoosh in the dark, and she lands in the laundry's cart of towels with a
   towel on her head (a gag frame), on deck 4.
6. **`scn_card_hk`:** the cart pushed to 130; the steward walks to her, thanks, the card.
   **`scn_photo`:** E at the honeymooners: she raises their camera, the flash, they kiss, the book.
7. **`bb_5` near-catch 5 (the pool, 131):** he bats at the water on the rim; within 3 m she bends;
   the kid at 136 squirts, the jet hits him; he leaps and falls in with a splash; she topples in too
   (play resumes in the water: she swims out); he scrambles up the ladder at 130 onto the lever's
   housing at 128, shakes (the wet shake) and bolts aft, wet paw prints after him; **`scn_drain`:**
   the lever drops, the water sinks over 5 s with a gurgle, the hatch at 125 shows in the tank's
   floor. **`scn_machine`:** the first cone at `src_icecream` empties it (a sad sputter); her
   husband's bubble shows the canister; `room_coldroom` has it; E at the machine with the canister:
   she pours, it hums, it never empties again; his bubble shows a cone once the kid is fed.
   **`scn_table`:** E at her husband with a perfect cone: they sit, eat, look at the wake for 4 s
   (input free to leave any time after); the framed picture appears on the table (`slot_table`);
   he hands her `book_6`.
8. **`scn_engineer`:** E at the technical door with the hot coffee: he drinks, waves her up, climbs
   the ladder out of sight; from then on he is at the top. **`scn_horn`:** E at the cord: the pull
   clip, the screen shakes, the smoke puffs; the camera pans to the sun deck: the rival jumps, the
   card drops at 136, he runs forward; the old lady bolts, the parasol and the book stay; then to the
   bow: the gulls lift off the kids' pool and the windscreen in a cloud; back to her. Flags: the
   card lies there, the sunbed is free, the gulls are gone, the engineer reads.
9. **`scn_wedding`:** E at the planner with the cake box: she takes it, the party walks into the
   chapel over 5 s, the lobbies clear, `blk_wedding` lifts; **`scn_ceremony`:** E at the chapel's
   door after: the ceremony seen from the back for 5 s, `slot_chapel` on the wall.
   **`scn_guest`:** E at the balcony guest's balcony door from inside: he comes in, thanks,
   `book_7`; his balcony door is an entry for good.
10. **`bb_6` near-catch 6 (the bridge):** she enters at 40; he sits on the console at 30; the rival
    at 26 creeps east with the net; when she is within 3 m she bends and the rival lunges; the cat
    leaps; the net hits the alarm panel at 29: the alarm sounds (lights, a klaxon once sound is on),
    the hatch at 27 releases and its ladder drops; Bumbot runs along the console and up it; the rival,
    tangled, slumps in the captain's chair and waves her on.
11. **`scn_sunset` and `scn_catch` (§6.1.9):** out of the hatch the sky turns; the camera slides to
    the tip of the bow and back; the glide with `gust_finale` (every 4 s) and two gulls crossing the
    path; a miss is the overboard scare and `cp_bridge`; at the tip, standing still 3 s: the
    arms-wide pose; he comes; she bends; he jumps into her arms. **`scn_home`:** a fade; she carries
    him through `door_mooring`, the kids' clubs, the forward core up to deck 8, into 8206, where her
    husband waits; Bumbot curls up on the bed between them; the win screen.
12. **`scn_nook`:** E at the odd book with all ten shelved: the bookcase swings open; `room_nook`.
    **`scn_shelve`:** each return: the librarian takes the book to its gap.

## 7. The ambient cast

Scenery people, drawn in full colour but behind the action, no collision, no bubble; one idle
each; most from two or three shared bodies recoloured (PixelLab's outfit transfer), the crew in
uniform. Decks 4-5: the lost passenger, the bathrobe guest, the steward with a breakfast tray, the
receptionist, the posers, the string trio (optional), the excursions agent, La Cucina's diners, the
host, the Seven Seas' diners, the galley chef, the laundry's folder. Deck 6: the stewardess making up
a cabin, the surfer, the couple at the rail, the DJ, the second photographer, the Windjammer's
barman and the guest with the model ship, the audience. Deck 7: the toddlers, the counsellor, the
couple at the plaques, Magnum's barman and pianist, the croupier and players, the shopper, the teen,
the balcony's seated pair. Decks 9-10: two officers. Deck 11: the spa's receptionist, masseuse,
stylist and client, the step class, the treadmill runner, the weights man, Topsiders' barman, two
sunbathers, the Sports Bar's three, two tables at the Great Outdoors. Deck 12: the Spinnaker's
barman and two guests, two kids at the kids' pool, Champs' three, two sunbathers, two shuffleboard
players, Cagney's diners, the sushi chef and two diners, the teppanyaki chef and four, Le Bistro's
diners, Los Lobos' waiter. About 60 figures from about 12 bodies.

## 8. The art this spec adds to §6.1.12

People: the librarian, the honeymooners, her husband, the jogger, the boat drill crew, the
teppanyaki chef, the carpet fitter, the steward on his rounds, the engineer's read, the kid's four
states, the old lady's five, the rival's six; the ambient bodies. Things: the delivery robot, the
luggage stacks, the towel animals, the carpet roll, the rope stands and signs, the readers in four
colours, the trays on the floor, the ice bucket, the laundry lines, the pillow fort, the ball pit,
the swinging lifeboat, the gate and ladder, the station locker, the sprinkler's burst, the towel
stack's fall, the chip spill, the stage lights' swing, the trap door, the pit, the fly rope, the
steam puff, the flare, the basketball, the wet patch, the deck chair, the drain lever, the hatch in
the tank, the bridge's hatch and ladder, the alarm's lights, the horn's cord, the telescope, the
canister, the coffee cup, the three cones, the swirl meter, the books and the shelf, the trolley,
the rolling ladder, the odd book and the swinging bookcase, the camera, the pill bottle, the cake
box, the parasol, the socks, the glyphs, the pictograms, the per-deck pictures and plaque bands.
Rooms: the laundry, the dry store, the pantry passage, the cold room, the galley, the stage
manager's cabin, the dressing room, the lighting booth and catwalk, the nook, the duct, the
lifeboat's inside, the generic inside cabin (with a connecting door) and balcony cabin, the
mid-cleanup cabin, the funnel's top. Clips of hers: §6.1.12, plus the camera, the pour, the wade,
the knock at the captain's door.

## 9. Open points for the build

1. Exact metres: this spec's positions are first placements; the builder snaps them and the user
   corrects from screenshots.
2. The delivery robot and the string trio are the two least "Norwegian Sun" things here; drop either
   on sight if they jar.
3. Whether the ambient cast is built early (the ship feels empty, §8) or after the interactive
   people.
4. The number of tangerines (41 placed) and whether the galley's and the service station's
   breakables should hide them or the dash should stay for shortcuts only.
