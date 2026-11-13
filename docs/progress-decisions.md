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
