# Progress and decisions of the autonomous build

The user's order of 2026-11-13: build the whole plan (`docs/build-plan.md`) autonomously on branch
`the-build`, deciding alone for fun, variety and richness, and **record here every change or
addition made to the plan, with its reason**. One section per step, saved with the step's commit.
`GAME_DESIGN.md` §8 says where work stands; this file says what was decided on the way and why.

How the build is put together (for whoever picks it up):

- **`tools/population.py`** is the plan's world as data (rooms, checkpoints, tangerines, pickups,
  Bumbot's beats, switches, pushables, grips). **`tools/build_world.py`** turns it into
  **`maps/world.json`** with the map builder's positions (`python tools/build_ship_map.py` writes
  both maps). **`src/world/world.js`** reads it and builds everything; **`src/world/verbs.js`** holds
  crawling, the wall jump, the glide and pushing, mixed into the ship scene.
- A thing is placed on a deck in metres from the bow, or in a room in pixels from the room's left
  edge. A room is a route of its own (`route === room id`), shown in the corridor's place.
- **`python tools/playtest.py golden`** walks the whole route with real keys; **`sweep`** tries
  every lock from the wrong side. Both must pass at the end of every step.

## Step 0: the skeleton (2026-11-13)

Done: the locks (round 1, before this run), the new vertical ways, bare rooms, the verbs, the flags,
checkpoints, tangerines, books as pickups, the golden path from the gangway to the catch.

**What was built as planned:** eighteen rooms behind doors (bare: wall, floor, their doors); the
trunk from Bliss to deck 9; the duct; the chute to the laundry; the pool's drain and hatch; the
bridge's hatch and ladder; the funnel's stairway and top; the boat walkway's gated ladder; the
balconies as floors and their partitions as walls; fourteen checkpoints plus the rooms', cabin
8206's (step 5) and the funnel's; the tangerines; ten books; the socks and the parasol as pickups;
Bumbot's six beats with his built near-catch, each setting its flag; the horn and the cake as
switches (yellow boxes) until their scenes exist.

**Changes and additions to the plan, and why:**

1. **One outside route for the promenade, the boat walkway and the balconies** (the game's route
   `promenade`). The spec treated them as separate places; as one route a drop from a balcony lands
   on the walkway or the promenade by plain physics, and a glide from a balcony to the promenade
   needs no special case. Outside, only the outside's own floors and walls hold her.
2. **The wall jump is a kick off one wall, repeatable** (jump at a grip, jump again: up and away;
   steer back, kick again). The spec's "wall jump off the partition" could not get her over a
   partition taller than her jump with a single kick. Grips are data (`GRIPS`, plus every balcony
   partition), so nothing else on the ship is climbable by accident. Pressed to a grip she slides
   slowly.
3. **The balcony partitions are 88 px tall on the ship's side** (they were drawn to the ceiling):
   taller than her jump (68), short of the ceiling, so going over one reads. A balcony's floor is
   one-way: up through it from below, **down through it with ↓ and jump** (↓ alone crawls, which the
   laundry lines will need).
4. **The balconies' glass fronts are drawn thin over her** (alpha 0.28): they are at the ship's
   scale and come up to her eyes, so at full strength she was a ghost.
5. **The duct is 1300 px long, about a quarter of a minute's crawl** (88 px/s), not the true 46 m:
   twenty seconds of holding one key was already long, forty would have been a chore. It runs at
   deck 9's floor level (the void over deck 8's ceiling), so its grilles look down into deck 8, and
   its far grille drops her into deck 8 at 66 m. → must be let go once in the vent, or holding it
   would carry her straight back out.
6. **The linen room's vent stays low for now** (as drawn): she crawls straight in. The plan's
   puzzle (push the laundry cart under a high vent, climb on it) comes with region 4's step, when
   the room is redrawn.
7. **Crawling is learned at the linen room's beat; pushing needs no lesson** (E at a cart's end is
   its own glyph). The steward's cart is in already: it fills the corridor at 122.6 m and rolls to
   130 m, where it can be hopped. The Housekeeping card's stand-in moved to 132.5 m, past the cart,
   so the cart is the gate as in the final design.
8. **Doors that could not stand where the spec put them** (a deck's last 3 m are structure; a stair
   lobby has no free wall between its stairs and its elevator; something was already drawn there):
   the gangway's checkpoint 62 → 72 m (the shell door is at 62) and it is lit from the start; the
   gym's 80 → 84 m; the foyer's 200 → 204.4 m; deck 7 aft's 196 → 191.6 m; the bridge's 40 → 43 m (a
   crew door face-on in the officers' corridor; the bridge's own door is seen from the side); the
   chapel lobby's 72 → 70.7 m; the galley's door 253 → 250.1 m; the stage door 254 → 242.5 m (beside
   the proscenium); the trap door 248 → 250 m; the bridge's hatch 27 → 28.8 m.
9. **The pantry's second door is at the Four Seasons' aft end (191.5 m), not 169 m:** the spec's
   two doors were 2 m apart and passed nothing; now the pantry really is a way past the waiter.
10. **The lifeboat she can enter is the one at 143 m** (its hatch at 147.5 m): the spec's 140 m has
    no boat (the user's photo set the boats).
11. **The funnel's stairway is two flights** (the roof to the casing's shoulder, then up the
    lattice's raked front) and its top runs 179.7-193 m, so the top's things moved: the locker 181,
    the horn 186, the lunch box 188, the telescope 191.
12. **The climb to deck 12 starts at the sun cover's aft post** (233 m): a grip on the post, a
    jump and a kick, onto the cover, up its curve, over deck 12's rail. The plan's station roof and
    parasol top as stepping stones come with region 6's step if they add anything.
13. **Deck 12's front windscreen is 96 px tall** (was a 32 px rail): it bars the jump down to the
    balcony forward of the spa, as §6.1.9 needs.
14. **The trap door works only after the stage's beat** (near-catch 3), or she would fall through
    it on her way to him.
15. **`?cards=all` also gives every verb**, for testing round the ship; what has happened (the
    flags) is never faked by it.
16. **The save is v3** (`verbs`, `books`, `read`, `items`, `seen` added); older saves start again.

**Left for the steps:** every person and scene, all art, hazards, carrying, the HUD's carried
thing, the glimpses, the elevators' panels beyond the regions' rule, `LOCKED_PARTS`, cabin 8206's
checkpoint, sound.

## Step 1: Lower ship, region 1 (2026-11-13)

Done: decks 4 and 5 populated and playable from the start to the way into region 2. The first
errand end to end (near-catch 1 at the Seven Seas' pass, the scream, the fruit bowl, a tray of
lunch carried past the waiter and down the stairs, the officer eats and hands over the Deck card),
the rival at his search rope, the glimpse up the forward stairs, the porter and his cart, the
luggage stack, the standing carts, the vacuum, the blocks on the 5-6 flights with their people,
five rooms drawn, twenty-one people drawn, the first quirk (the ice swan), the first book and the
tangerines. Playtest `region1`; `golden` now does the errand for real.

**New systems** (all data-driven from `tools/population.py`): people (`src/world/people.js`:
standing, walking loops with stops, things carried along, pictogram bubbles, what touching them
does); carrying (`src/world/carry.js`: the tray rules, the spill, loads that melt or cool with a
HUD meter); the story's own moments (`src/world/story.js`: one part per region); props, things to
hop, things the dash breaks, tray sources, signs, quirks; scripted moments written as plain async
functions (`world.cut`, `wait`, `tween`, `handOver`).

**The art pipeline for people:** `tools/cast.py` lists each person's PixelLab character;
`python tools/fetch_people.py` downloads their frames (PixelLab's ZIP of a character needs no key);
`python tools/build_people.py` packs `assets/sprites/people.png`. Her own new clips:
`python tools/fetch_her.py <animation>` then `tools/build_sprites.py`. Rooms:
`python tools/draw_rooms.py` (drawn by hand in code, `assets/ship/rooms/`).

**Changes and additions to the plan, and why:**

1. **People are PixelLab v3 characters at 64 px, side view** (2 generations each; clips east only:
   a template clip 1 generation, a skeleton-v3 move with poses on top 3). A calibration pair showed
   v3 comes out at her height (61 px) and nearest her look; "standard" came out 71 px tall and
   realistic. skeleton-v3's library moves (walk, eat, hit, sit...) with a few hand poses on top give
   the special clips: her walk with a tray is its `walk` with both forearms held out.
2. **The porter works forward of the officer** (53.5-64 m, was 62-72): his loop had the officer
   inside it, so the errand's last metres, with a tray that cannot hop a cart, came after a 180 m
   walk from the only place trays come from. Now the tray's test is the waiter, 20 m from the pass,
   where a spill costs seconds; the porter guards the forward cabins' luggage and tangerine instead.
3. **The waiter serves his tables:** twice on his loop he turns to a table for 2.4 s, and is out of
   the aisle while he does. A tray's low hop cannot clear him and a corridor has no way round, so
   this is how she passes: wait for him to serve, slip behind him. His tell is the turn.
4. **Deck 4 is not a tray route:** its standing carts cannot be hopped with a tray. The lunch goes
   along deck 5 and down the forward stairs. (The spec offered either deck.)
5. **The glimpse of Bumbot's tail is at the forward stairs the first time she comes by after the
   Seven Seas**, not "as she reaches the crew trunk" (45 m away: nobody would have seen it). She
   passes there with the tray, the rival at his rope beside it.
6. **The rival shakes his head** when she tries his flight (his own clip); he is gone once she has
   been in region 2.
7. **Diners are drawn seated on chairs of their own** (the seated test came out with its chair) and
   take a dining chair's place, **one to a table**: two facing each other overlapped across the
   small tables.
8. **`amb_lost` is a tourist in a Hawaiian shirt with a map**, not a second passenger in a bathrobe
   (the spec had two robes on deck 4: variety).
9. **Left out for now:** the string trio on the atrium floor (the spec's own doubt), the open cabin
   with a guest at its window on deck 5 (`amb_robe_5`; needs an open cabin drawing). Both can come
   back in a polish pass.
10. **The waiter's sprite came without a tray**, so the game draws the tray and cloche in his raised
    hand (the same pictures as hers).
11. **Her frights are her own words** («Ой!», «Ай!», «Бррр!»...) over one recoil clip (skeleton-v3's
    `hit`) for now; the vacuum keeps its jump and «Іііі!». A clip per fright is art for later.
12. **A tray is lost in a scare** (a fall, overboard): it is not hers to keep. People and hazards
    never scare her while she carries one, they spill it.
13. **The dash shoves the vacuum aside for six seconds** (it used to destroy it), as the spec says.
14. **The galley lies forward of its door** (the door is at the room's aft end): a deck's last
    metres are structure, and a room there would reach past the hull. In the plan's rooms only the
    deck's floor holds her, so a room can lie over structure.
15. **Crew name plates are placeholders** (BOSUN, PURSER, DJ; STAGE MGR on his door) until the
    user's in-jokes (§6.1.15).
16. **The notice board is at 190.6 m** (188 m is a cabin door); the galley's tangerines are in a
    crate that the dash breaks (they appear when it is broken).
17. **The Deck card's stand-in pickup is gone**: the officer hands the card over in his scene.

**PixelLab spent on this step:** about 90 generations (22 characters, their clips, three of hers).
