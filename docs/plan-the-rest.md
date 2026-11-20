# Plan: the rest of the game

Written 2026-11-18 by the design session on the user's word: "Read all of the docs of the
project, and make a general implementation plan, combined from everything what's left to do."

**What this is:** everything the project's documents still call open, checked against the code
at `main` `0c99e7d` (2026-11-18), in one list and in the order to build it. It adds no design:
each item points to where its design is written, and that text holds. Where this plan and an
older document disagree on what is built, this plan was checked against the code and is the
newer.

**Read from:** `GAME_DESIGN.md`, `CLAUDE.md`, `README.md`, and in `docs/`: `build-plan.md`,
`population.md`, `plan-three-uses.md`, `plan-visual-fixes.md`, `plan-fast-tests.md`,
`audit-2026-11-15.md`, `progress-decisions.md`, `start-links.md`, `intro.md`. Four readers went
through them whole and checked each open item by search in `src/`, `tools/` and `maps/`; the
findings that decide something were checked again by hand (the list in §11).

## Start here (for the session that builds it)

1. `CLAUDE.md`, "Working with the user" and "Art": every picture approved before it is placed,
   each change shown and then a stop for the user's review, the whole suite never started
   unasked, after each approved step commit and record and say "safe to compact".
2. Build the parts of §2 in their order. Each part names where its design is; read that before
   its first change.
3. What a step records, as always: its entry in `docs/progress-decisions.md`, `GAME_DESIGN.md`,
   `docs/population.md`, `docs/start-links.md` for a new start place, `CLAUDE.md`'s table and
   lessons; and here, the item marked built.

## 1. Where the game stands

- **Built:** the whole of `docs/build-plan.md` (steps 0 to 12: the ship, ten regions, the
  finale, the hull, the sound, the intro, two languages, the controller);
  `docs/plan-three-uses.md` steps 1 to 4 with their revisions and step 4a's gags 3, 7b, 13a, 16
  to 20; `docs/plan-visual-fixes.md` (F1 to F5); `docs/plan-fast-tests.md` (all of it).
- **Left, in four kinds:**
  1. what can be built now (§3 to §8);
  2. what waits for something of the user's (§9): a photo, a text, a decision;
  3. what is done once, at the end (§10): the other documents brought up to date, saving
     switched on, the release;
  4. what was looked at and is closed (§12), listed so that nobody opens it again by mistake.

## 2. The order

| Part | What | From | Size | Art, by the plans' own estimates |
|---|---|---|---|---|
| 1 (§3) | The mishaps' gags to their end, their playtest, two leftovers; **and (1.2a, added 2026-11-19) a hit is its gag whatever she carries, only a gull takes a tangerine** | `docs/plan-three-uses.md` step 4a, §1.3 and §1.6 | Large | About 80 generations |
| 2 (§4) | The rest of the twenty things to find; fourteen books with their covers; cabin 8206's desk | Step 5 and its revisions | Large | About 45, and the nook's photo |
| 3 (§5) | The look-outs; the deliveries | Step 6 | Large | About 15 |
| 4 (§6) | Each deck its own look | Step 7 | Medium | About 20 |
| 5 (§7) | Small faults and leftovers | The log, the audit | Small each | None |
| 6 (§7a) | Bumbot made again: his look, then every clip of his, richer and tuned (added 2026-11-19) | The user's word; `GAME_DESIGN.md` §4 | Large | About 90 (the design session's guess) |
| 7 (§7b) | The intro's scene tuned: a more real sun and reflections, clouds more varied and with volume (added 2026-11-19) | The user's word; `docs/intro.md` | Medium | About 30 (the design session's guess) |
| 8 (§7c) | What she can use: does it stand out? A comparison across the game, then the user's rule (added 2026-11-19) | The user's word | Small to medium | None expected |
| 9 (§7d) | The tangerines' seats: twelve placements that make no sense mended, three props for them; the total stays 56 (added 2026-11-19) | The user's word; the design session's audit | Medium | About 20 to 25 (the design session's guess) |
| 10 (§7e) | The checkpoints: 19 places from 26 (23 from 32 as the game counts them), six doors that stand wrong mended, two door props, never back behind a shut door (added 2026-11-19) | The user's word; the design session's audit | Medium | About 20 (the design session's guess) |
| (§8) | Optional things | The log, the spec | Small each | A few each |

The order is the three-uses plan's own, and the one the building session had named ("21 ...
Then 22 ... and 23 ..., then step 5"). Part 3's deliveries pay books 12 and 13, so they need
part 2's fourteen-book shelf and covers first. Part 5's items can be taken whenever the work is
in their files anyway.

## 3. Part 1: the mishaps' gags to their end

Design: `docs/plan-three-uses.md` §1.6 (the mishaps' table) and step 4a;
`docs/progress-decisions.md` from "Step 4a: the first batch of gags" on.

### 1.1 The gulls and the doors: gags 21 to 24 (medium; about 25 generations)

| # | What hits her | The gag with no tangerine on her | Its code |
|---|---|---|---|
| 21 | A funnel gull on the stairway | "She bumps down the flight on her bottom, step by step, to its foot" | `FunnelWind`, `src/world/topdeck.js` |
| 22 | A gull across her glide | "The parasol turns inside out, and she falls (the fall as built)" | `Crossers`, `src/world/finale.js` (`scareAir`) |
| 23 | A "Do Not Disturb" door (seven) | "Oh, sorry!": both hands over her eyes, blushing, she tiptoes off fast, out of the screen | `DndDoor`, `src/world/movers.js` |
| 24 | The occupied balcony | As 23 | `Occupied`, `src/world/outside.js` |

- 21, 22 and 23 were the building session's proposals for its next batch ("21: she bumps down
  the funnel stairs on her bottom when a funnel gull swoops her. Then 22 (the parasol turns
  inside out) and 23 (the "Do Not Disturb" doors' "Oh, sorry!")"): each is shown to the user as
  a proposal first. 22 needs her with the parasol (a state of her character).
- With a tangerine on her these four are built already (the duck and the gull that takes it; the
  apology and the hand-over).
- **Under way (2026-11-18):** proposed and answered (21 facing down the flight, feet first, at a constant
  pace; 22 a new clip of her looking up at the inside-out parasol; 23 and 24 as written, to the next wall or
  partition; one at a time). **Gag 21 built (2026-11-18)**: `stairsGag` in the ship scene, "Ow-ow-ow!", a dizzy end with
  butterflies (the user's additions); `?at=stairway`. **Gag 22 built (2026-11-18)**: `parasolGag`, "Whoa-whoa-whoa!",
  the crossing gull's dart at her first (the user's addition), the bow's plating kept closed and its railings behind it
  (`docs/progress-decisions.md`). Then the parasol's control (the user, 2026-11-19): it opens only on a press
  of jump made in the air and held, not on the jump from the floor held on. **Gag 23 built (2026-11-19)**: `sorryGag`,
  "Oh, sorry!", her hands over her eyes, blushing, a quick tiptoe off to the next wall or door; and on the user's word
  the doors' sign redrawn (a hanger with a half-round top and a crossed red circle, on the lever's mount, swung with
  the door; the same on cabin 8206's door and the occupied balconies' partitions); `?at=dnd9`. **Gag 24 built (2026-11-19)**:
  the same gag on an occupied balcony, she tiptoes away from its guests to the partition ahead (`partitionShort` in the
  ship scene, which the gull's 20 uses too); `?at=occupied8`. **1.1 is done.** Then 1.2's 7a, then 1.1b (2026-11-19, built:
  the gulls' flight; the kid's cone, his eating clip, the queue on the way); **next: 1.2 from 9a.** On the way, the funnel's
  stairway gone over (`docs/progress-decisions.md`): moved 12 px out, boarded by walking into it, a hold on
  the rail in a gust, gulls that dive straight from their flight, a tangerine carried in the beak.

### 1.1b The pool's gulls and the opening in deck 12 over the pool (small; no art; added 2026-11-19; built)

The user, 2026-11-19, of the two gulls circling over deck 11's pool: "Why are the gulls flying here?" They have a
purpose (`gull_pool`, `FoodGulls` in `src/world/hazards.js`: one dives at food she carries there, a cone held up is
bait, a thrown tangerine is taken; once fed the kid squirts them away for her), and `docs/population.md` puts them
"circling over the gap where deck 12 is open above the pool"; but that gap was never drawn, so they fly under deck 12's
closed side. Removing them was asked and taken back (it would take the kid's reward with it). **To build, as the next
step:** the opening in deck 12 over the pool, as the design and the real ship have it.

**Found when it was started (2026-11-19): the opening is built** (`POOL_OPENING`, 115 to 145 m in
`tools/build_ship_map.py`: deck 12's floor open over the pools, crossed by a walk; she can drop through it into a pool).
From deck 11 the near side of deck 12 shows as a white band (its walk over the gap and its slab), and the gulls circled
just under it. **Built instead:** the pool's gulls wheel in the open sky over deck 12, above its railing, behind the
ship's side (from deck 11 out of view); a dive at her food comes down past the band, in front of her once under it,
and longer (0.42 s); and, the user's word, **no shadow** for them (the perched gull on the Great Outdoors' rail keeps
its own). The items below were the first plan, not needed:

- Where: over `gull_pool`'s stretch and the pool under it (deck 11, about 140.9 to 145.6 m in the code's metres; check
  the pools' own extent in `tools/ship_layout.py` and `docs/population.md`).
- What: deck 12's floor gone over it, the sky and the far background seen through, railings at deck 12's edges round
  it, deck 11's ceiling band gone there; the ship's side (shell tiles, livery, the cut-away) following it; the gulls
  circling in it, under the sky.
- First: list what stands on deck 12 there (the court's two hoops are at 146.9 and 154.4 m, the sun deck, the kids'
  pool) and what reaches over it; propose the opening's size and look to the user (a mock-up over a real screenshot)
  before building it.
- Tests: `region6` (the gulls, the kid), `region8` (deck 12 above), `throw`; `tools/check_overlaps.py`; the whole ship's
  render (`tools/render_ship.py`) for the side.

### 1.2 The third batch: nine gags and two clips of others (large; about 55 generations)

| # | What hits her | The gag with no tangerine on her | Its code | Before any art |
|---|---|---|---|---|
| 7a | The deck chair, head on | "Face first onto it; it folds flat and she sledges on it across the tiles" | `WetPatch`, `hazards.js` | **Built 2026-11-19** (it could still happen: from forward, every time; then the chair made to stand still, the patch redrawn). Was: **Walk at it with real keys: can it still happen?** Since 7b the chair hardly rocks as she slides in past it. If it cannot, say so to the user and drop it |
| 9a | The jogger, head on, both running | "Twirled like a top, spirals over her head, she sits" | `haz_jogger`, `world.touched()` | **Built 2026-11-19** (`jogGag`; her own dazed sit, the butterflies, for the spirals) |
| 9b | He runs into her, she standing | "Bowled back onto her bottom; he jogs on the spot, sorry" | The same | **His sorry on the spot** is a clip of his (where the two meet they are generated together). **Built 2026-11-19** (f246cf0; his sorry, on the user's word: he scratches the back of his head, the hand hidden). **Approved 2026-11-19, the proposal as recommended:** his own clip, made with her sitting before him and then taken out, played wherever he stops (9b and 9c); in 9a he runs on without a look; the order 9b, 9c, 9a, 9d; her clips from the frames the game shows (9a one per quarter of her stride); the meetings: `assets/source/her-mishaps/batch-4a/starts/jog9/` |
| 9c | He runs into her back | "Shoved into three flailing steps and a belly-flop" | The same | **Built 2026-11-19** (he scratches his head behind her) |
| 9d | She runs into his back | "She bounces off and sits (8d's clip); he never notices" | The same | **Built 2026-11-19** (no art) |
| 11a | The kid's jet in her face | "Sat back, spluttering, wringing her hair; he points and laughs" (**done 2026-11-19: the wet gag, 16's, plays for 11a and 11b; asked, the user: "Covers"; neither his laugh nor 11b's own is made**) | `src/world/lido.js` | **The kid's laugh** is a clip of his (his pistol is drawn into both hands in every pose) |
| 11b | The jet in her back | "As 10b: she arches, dances, squelches off" | The same | **A question for the user:** 10b's squirm was dropped ("looked weird, and the case is rare"), so 11b points at a clip that is gone. Propose: her arch as built and the run-off, no new clip |
| 12a | The stage's light, from the front | "Her head back, two spins on the spot, stars circling, she sits" | `SwingLight`, `movers.js` | **Built 2026-11-19** (the user: reuse 9a's spin, a new one from her standing frame; butterflies, not stars) |
| 12b | The same, from behind | "Three stumbling steps, down on her hands and knees, stars" | The same | **Built 2026-11-19** (9c's stumble and belly-flop, dazed). The light and the stage manager swapped places, the trap door drawn (the user) |
| 14a | A basketball in her face | "She tips over backward, stiff as a skittle" | `Balls`, `topdeck.js` | **Built 2026-11-19** (from her stand or a quarter of her run, onto her back, lying so with the butterflies; her lying redrawn, the user: her stand turned flat "appears to be at an angle"). With it, on the user's word: **the court's two players** (a man and a woman, lightly washed) shoot the balls through their rings, the ball comes back to their feet and they pick it up (`tools/build_court.py`); it hits her from the throw to its second landing |
| 14b | A basketball on the back of her head | "She topples forward, stiff as a plank" | The same | **Built 2026-11-19** (face down, redrawn lying flat: the user chose it) |
| 15 | The drill's boat, from above | ~~"Pressed down to half her height, a waddle, she springs back up and sits"~~ **14a's: stiff onto her back, the boat down over her** (the user, 2026-11-19: "no squash and no crouch") | `DrillBoat`, `outside.js` | **Built 2026-11-19**, no art; the drill answers her coming, the falls made fast to the posts, the winch 0.3 m forward |

- Shown to the user in batches, enlarged and numbered, each checked frame by frame first; one
  that will not read after two tries is shown with what could take its place.
- Without a gag by design, not to be made: 1 (the chips), 2 (the dog's lead), 10e (her own
  trip). 13b is not made (no swing door hits her from that side); `src/world/mishaps.js` still
  names it for a door hit from behind: check whether that can still be reached, and take the
  line out of `MISHAP_SCENES` only if it cannot.
- ~~**Proposed, the user's word first:** her "bats the towels off" (18 with a tangerine on her;
  the reel stands in).~~ **Dropped (2026-11-19, 1.2a):** with a tangerine on her the towels bury
  her all the same. 16's two small flaws were noted and left (her blouse greys one frame in
  two run-stops; her hair streams back at the sneeze's peak).
- **The order from here (2026-11-19):** 14a and 14b, then **1.2a** (below), then 15, made under
  1.2a's rule from the start (the boat's gag whatever she carries). **All built (2026-11-19); 1.2 is done.**

### 1.2a A hit is its gag, tangerines or not; only a gull takes one (medium; no art; added 2026-11-19)

**Built 2026-11-19.** As below, with the user's three answers: a rail gull that comes down on her while she
carries something that is not food takes a tangerine and she keeps it ("Let the gull steal a tangerine"); the
flag `?pocket=off` is gone ("it always confused me"); the rule on links is dropped (links as the context needs;
`docs/start-links.md` without `&tangerines=infinite`). The `pocket` playtest is rewritten; the gull checks of
`region7`, `region8` and `finale` empty her pocket first and give it back.

The user, 2026-11-19, after playing: "losing a tangerine on hit almost never fits visually and in
terms of gameplay. I want to play the respawn gags in most of the cases, tangerines or no." The
design session went through every hit in the game and in the plans (the 27 obstacles of
`MISHAPS`, the 45 scenarios of `MISHAP_SCENES`, the tray spills, part 3's deliveries) with one
test: **losing a tangerine fits only where someone takes it.** The user's answers: "Yes, all as
recommended"; and for what is built, "add a step for their update after 14a/14b". The design:
`docs/plan-three-uses.md` §1.3 and §1.6, revised the same day.

**The rule:**

| Hit | With tangerines on her |
|---|---|
| A gull that comes down on her: the balcony rails' (20), the funnel's on the stairway (21), one across her glide (22) | **As built: she ducks, the gull flies off with one, she keeps her place** (under the parasol she glides on). With none, the gull's gag |
| A "Do Not Disturb" door (23), the occupied balcony (24) | **Gag 23 always** ("Oh, sorry!", the tiptoe); no tangerine held out, none lost |
| Every other hit (1 to 19) | **Its gag and her checkpoint, always; none lost.** What 2 (the dog's lead) and 16 (the sprinklers) already do |
| A bump with a tray, a cone or a delivery in her hands | **Always a spill**, as before the pocket; no tangerine saves it, none is lost |

Not changed: a lunge still takes her through a hit; falls, the sea and a load that goes over by
her own feet; everything a tangerine is spent on by her own choice (the cry, the lunge, a
throw and whoever takes it). **Found while writing this:** the gulls that dive at food (the
pool's, the Great Outdoors', the rail gulls with food in her hands) take the food whatever is in
her pocket, in the code as built; `docs/plan-three-uses.md` §2's "her cone saved" was never
built for them. They stay as built: a tangerine thrown to them is what saves a cone.

**To build, after 14a and 14b:**

1. **`MISHAP_SCENES` (`src/config.js`):** the pocket is the exception now, not the rule: it
   holds for 20, 21 and 22 only (say `pocket: true` on those three and nothing on the rest;
   `pocket: false` on 2 and 16 goes). The scenarios built with a stand-in and no gag of their
   own (1, 10e, 13b if it can still be reached, 15 until it is made) give their stand-in.
2. **`pocket()` (the ship scene):** only the gull's take is left (`toss: 'gull'`, `snatch`),
   with its duck and the blink. Gone from it: the tangerine knocked out to roll off behind her
   (`loose.knock`), the push, the hand-over at a door. **Keep `handOver()` and her `apology`
   clip:** part 2's sardines (the Sushi Bar's chef takes a tangerine from her hands) uses them.
3. **`Carry.spill` (`src/world/carry.js`):** no pocket; `reactionTo()` in the ship scene goes
   with it. A gull's hit while she carries something that is not food: the spill, as any bump.
4. **`world.touched()`:** "the pocket took it: whoever walked into her stands aside" goes with
   the pocket (her gag holds them now, as built per gag).
5. **Left in the sheets, no longer played by a hit:** her short reactions (`reel`, `slipback`,
   `stumble`, `rubnose`, `splutter`, `arch`, `yelp`, `shiver`) and their sounds
   (`REACT_SOUND`). Search each before touching it (her own trip, the wet patch's slip and
   others play some of them); nothing is deleted from the art.
6. **Each gag looked at with tangerines on her**, since none has been played that way: the
   count on the HUD unchanged, nothing left lying, her checkpoint after. In the air a hit's gag
   still starts when she lands.
7. **`tools/playtest.py`:** `pocket` rewritten (a hit with tangerines on her: the gag, her
   checkpoint, the count as it was; a gull takes one and she keeps her place; a tray is spilled
   with tangerines on her; a fall as before); every `Browser.open()` adds `&pocket=off` today,
   so the regions' checks already see the gags: look for the few that ask for `pocket=on`. Run
   `pocket`, `vacuum`, `region1` to `region9`, `finale`, `boot` (each a few seconds, stepped).
8. **The documents:** `GAME_DESIGN.md` §3.2 and §5.6 (the design session has put the decision
   there; the "built" lines are this step's); `README.md`'s two flags; `docs/population.md`'s
   hazards; `CLAUDE.md`: `src/config.js`'s and `tangerine.js`'s rows, and the rule on links
   (a gag no longer needs a link without `&tangerines=infinite`; **the gulls' three do**,
   20 to 22: propose the new wording to the user, it is their rule).
9. **For the user in play, after it:** every hit now costs the way back. If a stretch proves
   harsh with it (1.4's checkpoint past deck 9's sprinkler is such a question; the tray errands,
   where a bump is now always a spill), it is answered with a checkpoint or a hazard's timing,
   one at a time, on the user's word.

### 1.3 The `mishaps` playtest, the sounds, the start places (medium; no art)

**Built 2026-11-19** (the user's answers: region 1's untested ones in too; 7b and 13b kept, marked
unreachable; the ten sounds; the five places): `mishaps` in nine cases, sixty hits through each thing's own
code, none on her and two; ten gag sounds on their clips' frames; `chips7`, `jet11`, `light6`, `towels9`,
`drill7`; `pocket`'s three stand-in checks and three leftover pocket-emptying lines gone; the table of hits
in `docs/population.md` §2.9. The old run-off checks listed below were already gone (each rewritten as its
gag landed). `docs/progress-decisions.md`, "1.3".

- `mishaps`: a new scenario, a case for each scenario of §1.6 outside region 1 (the gag it asks
  for, her checkpoint after, the thing back in its place; ~~with a tangerine the reaction and
  where the tangerine goes~~ **with tangerines on her the same gag and the count unchanged, and
  for 20 to 22 the gull's take (1.2a, 2026-11-19)**; the side told right). The gags built so far are checked inside
  `region4`, `region6`, `region7`, `region8`, `region9`: those stay, new ones go here.
- The checks that still expect the old run-off, as each gag lands: `region2` (the jogger),
  `region3` (the stage's light), `region6` (the jet, 7a), `region7` (the boat, the doors, the
  balcony), `region8` (the balls, the funnel's gulls), `finale` (the crossers).
- Sounds: each gag its own few in `src/sfx.js`; `tools/check_sound.py` must end "all within
  bounds" (not recorded as run for 16, 17 and 19: run it once for those too).
- A start place for each new gag (`?at=`), with its line in `docs/start-links.md`.
- The step's documents, not done for the gags built so far either: `docs/population.md`'s
  hazards, each with its scenarios; `GAME_DESIGN.md` §5.6 and §5.8.

### 1.4 Two leftovers of step 4a (small each; each the user's word first)

- ~~**The four end walls with a one-way doorway** (decks 8, 9 and 10 aft, deck 11 forward): not
  looked at yet. Look, and propose to the user whether and how they show their free side
  (`end_walls()` in `tools/build_ship_map.py`, `buildBulkhead`, `assets/source/ship/pushbar/`).~~
  **Looked at and left as built (the user, 2026-11-19):** only one face of each is ever on screen,
  the other always behind the ship's plating (the stern terraces, the balcony forward of the spa);
  on decks 8 to 10 that face is the free one, she passes through as through any end wall; on
  deck 11 it is the spa's, and she gets the padlock there. "This looks exactly the way we already
  decided and built." **Part 1 is done.**
- ~~**A crew-door checkpoint just past deck 9's sprinkler:** proposed, "only if the stretch from
  `cp_9_arrive` to the steward with no tangerine proves harsh". The user judges it in play; if
  yes, one line of data.~~ **Closed (the user, 2026-11-19, §7e):** none. One stood there in
  effect all along (the balcony cabin's lamp at 151.6 m lit as she walked past its locked door);
  it goes with part 10, and the corridor keeps its two ends.

## 4. Part 2: the rest of the twenty, and the books

Design: `docs/plan-three-uses.md` §4.1, §4.2 and step 5 with its revisions; `GAME_DESIGN.md`
§6.1.2 (the fourteen titles and where the books lie); `docs/progress-decisions.md`, "The books'
titles, and where they show".

### 2.1 The other fourteen placements (large; about 12 small pictures)

Four of the twenty are placed (the ball, the wool, the feather, the flag). To place, each a line
of data and a generated picture shown first, each set against what is built at its spot:

| # | Whose | Thing | Where | How |
|---|---|---|---|---|
| 4 | Bumbot's | Collar bell | The promenade, a gull on a lamp | A lob: it drops the bell for the fruit. **A new mover** (her cry: it flaps and keeps the bell) |
| 5 | Bumbot's | Liquid snack in a tube | Deck 4, the dry store, on a shelf | E (green card). **Placed 2026-11-19** (the bottom shelf, by its tangerines) |
| 6 | Bumbot's | Massage gun | Deck 11, the gym, ~~the bench by the weights~~ **the rowing machine's seat** (the user, 2026-11-20) | E. **Placed 2026-11-19, moved 2026-11-20** |
| 7 | Bumbot's | Tin of sardines | The Sushi Bar | The chef's bubble shows a tangerine; he takes one for it (the apology's hand-over) |
| 8 | Bumbot's | Remote-controlled car (beige, two big rubbery cyan wheels: the user) | Deck 7, Entourage, past the ball pit | E. **Placed 2026-11-19** (on the floor between the foosball and the pool tables) |
| 10 | Hers | Bookmark with a cat on top | ~~Deck 6, the maid's cabin, in the book by the bed~~ **Deck 9, the cabin being cleaned, in its book on the stripped bed** (swapped with 12, the user: that cabin has no window) | E. **Placed 2026-11-19** |
| 11 | Hers | Diary notepad (brown leather, a strap with a brass buckle: the user) | Deck 7, the Stardust balcony's far end, on a seat | E (look-out 1 will be at the same end). **Placed 2026-11-19** (the last seat, by the railing) |
| 12 | Hers | Small plant in a pot | ~~Deck 9, the cabin being cleaned, its windowsill~~ **Deck 6, the maid's cabin, its windowsill** (swapped with 10) | E from the floor (`low`). **Placed 2026-11-19** |
| 13 | His | Ice cream spoon | Deck 11, the Great Outdoors, the last table at the stern rail | E, after the table scene (look-out 5 will be at the same rail) |
| 14 | His | Sleep mask | Deck 10, the far balcony, on a sunbed | E, after the vaults |
| 15 | His | Handheld (black, four coloured buttons, no logo) | Deck 12, Champs, on a sofa | E |
| 16 | His | Guitar pick | Deck 12, the Spinnaker, the bandstand by the piano | E |
| 17 | Book 11 | נערה במעיל כחול | The boat walkway's end, beyond the boat drill | E |
| 20 | Book 14 | Pachinko | Deck 9 forward, the officers' corridor's end | E (look-out 4 will be at the same end) |

- **Built so far (2026-11-19): 5, 6, 8, 10, 11 and 12 placed; and the user's "A and C" for every thing
  to find and every key card:** (A) in the world a little bigger than life, each the shrink of (C) its
  **close-up**, a detailed generated picture (about 100 px) shown in the middle of the screen at 2x over a
  dim with a warm light behind it when she gets it, any key closes it (`world.closeup()`;
  `assets/source/closeups/`, `tools/build_closeups.py`). The four already placed got theirs too (the tennis
  ball, the feather and the flag a new world sprite from it; the wool a small picture of its own, its strand
  over the basket's rim); the dog's owner's toss holds the new ball over her far hand. 26 generations.
  **Waiting for the user: the locations of all ten, judged in play** (the links: `docs/start-links.md`, five
  new places `store4`, `maid6`, `knit5`, `shore5`, `balcony7`); noted for that: the flag now stands 16 px
  among four of 13, the brown diary on a red seat. Next after it: 4 (the bell gull) and 7 (the sardines),
  his four (13 to 16) after the table scene, then 2.2 before the two books. The close-ups also as the HUD's
  icons (2.4): to propose with it.
- His four are not there before the table scene ("not lying there before it, not merely
  locked"). Nothing of the twenty flies to its count. Books 12 and 13 (rows 18 and 19) are paid
  by part 3's deliveries.
- `tools/check_overlaps.py` must list nothing; `tools/check_corridors.py`'s numbers given at
  the end (the audit's C9: a reward every 25 to 30 m is measured only now).

**Also part of 2.1: the other pickups' pictures and close-ups** (small; about 3 to 6 generations; added 2026-11-20, the user: "As part of 2.1").

The user, 2026-11-20, of the pink sock on the gym's yoga-mat rack: "What is this?", then "Are their
refinement and their close-ups not in the plan?" They were not: "A and C" (2.1) covered the things to
find and the key cards, and the books' covers come in 2.3; the pickups that give her a way to move or a
pocket item were left out. "Yes, add those to the plan."

- **The grip socks** (`item_socks`, deck 11, 95.75 m, on the yoga-mat rack's top) and **her pills**
  (`item_pills`, the stage manager's cabin, deck 4): both still the early placeholders drawn in code at
  the game's start (`icon-socks`, `icon-pills` in `src/world/world.js`), never generated or approved; the
  sock floats over the rack's top rail. Each gets a detailed generated picture (assets/source/closeups/,
  `tools/build_closeups.py`), its world sprite made from it a little bigger than life (`FROM_CLOSEUP` in
  `tools/build_things.py`), standing on what holds it (the rack's top rail; the cabin's shelf or table).
- **The parasol** (`item_parasol`, deck 12, at the old lady's sunbed after the horn): its world picture
  is generated and approved (`parasol-closed`); only its close-up, made to match it.
- **The close-up on getting each**, as for the things to find (`world.closeup()`): from `take()` for a
  `verb:` and an `item:` pickup too (frames named for what she gets: `socks`, `pills`, `parasol`).
- Each picture shown to the user enlarged and in place before it goes in; then `region1` (the pills),
  `region6` (the socks), `region8` (the parasol), `boot`.
- **Built 2026-11-20:** the pills are her only quest item kept in her pocket (the user: "the same treatment
  to all the quest items that we put in our pocket, except those that we carry"; every hand-over and pickup
  of the story looked at: the rest she carries, or are cards and books). The socks: a pink pair, the world's
  in a stronger pink with a lighter pink outline, **moved to the free treadmill's belt by its rear end, 8 px
  up, sunk into it a little** (the user); the close-up in the same pink. The pills: a yellow bottle, 12 px with
  an orange outline, the cap's white ridges on top, an even foot with rounded corners, a dark title and two
  lines of print on its label (the close-up's label likewise, drawn by hand); the stage manager's hand-over
  carries it too. The parasol: a close-up only, generated furled (the second of two tries), set to the world
  parasol's red and white, the red band on its handle painted as the pole. The code-drawn `icon-socks` and
  `icon-pills` are gone. 6 generations.

### 2.2 Fourteen books where ten is written (medium; no art by itself)

`src/world/library.js` (the shelf's gaps, the colours, `books_all` at ten),
`src/world/world.js` (the second list of colours, the textures `book-1` to `book-10`, the HUD's
`/10`), `tools/draw_pages.py`, `tools/playtest.py` (`n <= 10`), the nook in `src/world/bow.js`.
The books' count on the HUD: found of 14, **hidden** until the first (today dimmed).

### 2.3 The titles: covers, their moment, the shelf seen close, the nook's photo (large; about 30 generations)

`docs/plan-three-uses.md`, step 5's revision of 2026-11-18. Nothing of it is built.

1. **The lettering tool first** (new): each title and author set on its cover and spine from a
   font with every script needed (lower case, Polish letters, Russian and Ukrainian Cyrillic,
   Hebrew from right to left), at whole pixels. The books' own texts do not go through
   `src/lang.js`. Each spelling checked against her copy (the photos: `reference/photos/Books`).
2. **Fourteen covers, generated, each its own:** shown enlarged, numbered, title and author
   drawn in, before any is placed. The small book in the world and its spine take their colours
   from its cover.
3. **The cover's moment:** in `world.take` and `world.giveBook`, after the sparkle or the
   hand-over: the Library's `panel()` with a lighter dim, the cover in the centre, any key
   closes it. Each of the fourteen, once.
4. **The shelf seen close:** `sec_shelf` answers E: a generated picture of the shelf over the
   screen, the returned books' spines with their titles laid in from the save, gaps for the rest.
5. **The reading nook's photo** (given): pixel art from a cutout on a flat ground, candidates
   shown first; in `slot_nook`'s frame.
6. **The user's to answer before they are built:** whether books 11 to 14 get hint pages (plain
   until then); whether the Library's small shelf and return trolley, drawn in code, are
   generated too (proposed).

### 2.4 Cabin 8206's desk, the day after, the counts (medium; little art)

- **The desk:** his four and her four, each a prop shown from its own find on. **First the
  picture of the desk with all eight, shown to the user**; if it is crowded, some of hers go by
  the bed (`tools/draw_cabin.py` for where the desk's top is).
- **The day after:** Bumbot's eight laid out with him (`src/world/finale.js`).
- **The HUD:** each kind's count appears with its first find. Its three icons are font emoji
  (🐾 🌸 🎸), never approved and not generated: propose small generated icons with the rest.

### 2.5 The `keeps` playtest (medium; no art)

New: each of his places empty before the table scene and holding its thing after; each thing on
the cabin's desk once found; each count appearing with its first find. With it `region2` (the
cover on the first pick-up, closed by a key; the shelf's close view with one book back and
thirteen gaps), and each region's scenario where something is placed or a book is taken (the
cover closed before it goes on).

## 5. Part 3: the look-outs and the deliveries

Design: `docs/plan-three-uses.md` §4.3, §4.4 and step 6 with its revision.

### 3.1 The look-outs (medium; about 5 generations)

Standing still two seconds eases the camera out from her to the view; it holds while she is
still and comes back when she moves. Nothing is counted.

| # | Where | The view |
|---|---|---|
| 1 | Deck 7, the Stardust balcony's far end, the rail | The whole theatre from above |
| 2 | Deck 4, the stern end, a porthole (250 m) | The wake from just above the waterline |
| 3 | Deck 5, the forward end, a porthole (20 m) | The bow wave |
| 4 | Deck 9, the officers' corridor's forward end, the front windows | Forward over the bow |
| 5 | Deck 11, the Great Outdoors, the stern rail | Down and aft over the wake; at sunset the sun's path |

- **The Stardust's first, shown to the user running** (motion is judged by eye), then the other
  four. A porthole piece and a window piece, generated.
- `Lookout` in `src/world/movers.js`, `LOOKOUTS` in the data, the camera in the ship scene (the
  intro's camera work is the model); a case each in the regions' scenarios.
- Spots 1, 4 and 5 are where the diary, book 14 and his spoon lie (2.1): look at each with both
  in place.

### 3.2 The deliveries (large; about 10 generations)

A delivery waits at a hallway's pantry end once its fire door has been opened; a tray with a
cabin's number on its tag, carried under tray rules; a hand takes it at the door, with a `♥`.

| # | Hallway | Load | Its rule | Pays |
|---|---|---|---|---|
| 1 | Deck 8 midships | Flowers in a tall vase | It stands in front of her face: she sees the hallway through the stems | Book 12 (Poczwarka) |
| 2 | Deck 10 midships | A pot of tea | It cools (the HUD's meter, as the coffee) | Book 13 (Daughters of Warsaw) |
| 3 | Deck 9 aft | A stack of pillows | Light: a full jump allowed, but the top one slides off if she stops short | A thank-you only |

- `LOADS` in `src/world/carry.js`; a source at each pantry end `when` its door is opened; the
  door that takes it. With a delivery in her hands a hit is a spill, as with any tray,
  **tangerines on her or not** (1.2a, 2026-11-19: no tangerine saves a tray).
- The loads are generated; where a load hides her or changes how she stands (the vase before
  her face, the pillows in both arms), her with it is one generated clip.
- The plan's own warning: three deliveries are one kind of errand with three loads and three
  rules, "the closest the plan comes to the line" of nothing twice. Each must feel its own.
- New scenario `deliveries`; `region3`, `region5`, `region7`, `region4`, `region9`;
  `tools/check_corridors.py`'s numbers again.

## 6. Part 4: each deck its own look (medium; about 20 generations)

Design: `docs/plan-three-uses.md` §4.5 and step 7.

- A coloured band on each deck's cabin number plaques (deck 4 grey-blue, 5 warm yellow, 8 blue,
  9 green, 10 terracotta), in code. **First find where the cabin numbers are drawn:** the reader
  found no number plaque in `drawCabinDoors`; if it is part of the door's art, the band is put
  there, and the user sees one deck before the rest.
- Framed pictures by deck, generated, six sets of three or four, each set shown first: deck 4
  safety posters and rosters, 5 paintings of the ship, 6 (the forward cabins) old port maps, 8
  seascapes as built, 9 botanical prints, 10 old liners' posters. Today every corridor hangs the
  same three (`pictures` in `drawCabinDoors`).
- A tint only if a deck still looks like its neighbour: one deck tried and shown beside itself.
- The whole ship rendered and looked at; `boot`, `stairs`, `lift`, `tools/check_overlaps.py`.

## 7. Part 5: small faults and leftovers (small each)

- **Never tried in the game:** a thrown tangerine at the funnel's gulls, and at Bumbot at the
  tip. Try both; a case each in `throw` or `finale`.
- **Two `deck4` checks failed now and then before the stepped clock:** the breakfast round
  moving on (once in three runs), and the lob onto the climb's shelf not knocking the feather
  down (once in four, cause not found). See whether they still do (`--seed`), and find the cause.
- **"Standing still with a book she reads where she stands"** (`GAME_DESIGN.md` §6.1.2) has no
  code: she reads only in the chair and on her bed. Her reading clips exist.
- **V8** (her word's white box has no outline) and **V10** (the party cabin's music notes drawn
  at the wall's depth): left out "unless the user asks". Ask once; a few lines each.
- **Sound, the engine's leftovers** (the user hears, the builder cannot): a held sound that can
  be stopped (the soft serve's motor is short pieces end to end); eating and drinking are mostly
  silent; the intro has a checkpoint's chime and a door and no more.

## 7a. Part 6: Bumbot made again (large; about 90 generations, a guess)

Added 2026-11-19 on the user's word: "regenerate all Bumbot's sprites. Now it doesn't look like
him, and also his animations must be enriched and fine-tuned." It is numbered 7a so that no
other section's number changes; it is built after part 5 and before §10.

Design: `GAME_DESIGN.md` §4 (who he is, his size, his clips as first decided); `CLAUDE.md`'s
lessons of 2026-10-31 (his character, shrinking a bigger design), 2026-11-17 (a quadruped's
clips) and 2026-11-14 (a photo to pixel art, step 10's her with him in her arms).

**What there is today** (`BUMBOT` in `tools/build_sprites.py`, `assets/source/bumbot/`): one
standing picture, our own two-thirds shrink of a 48 px PixelLab design, about 28 px tall; clips
`run`, `wash`, `jump`, `sit`, `eat`, `bat`, `shake`, and `asleep` as one still that breathes in
code. PixelLab character "Bumbot (final)", `81f4c718-6c1b-43aa-b3e0-da0cfdd7c855`.

1. **Ask first, by numbered questions:** what in him is not the real Bumbot (the head's shape,
   the ears, the eyes, the body's build, the tail, the coat's shine, his size next to her), and
   which moves the user misses or finds wrong. Nothing is generated before the answers.
2. **His look.** From the user's photos of him (`reference/photos/Bumbot/`, four; never
   committed; only a cutout on a flat pale ground is sent). Several candidates, each shown in
   the chat enlarged, at the game's size beside her, and beside the photo. He stays about 28 px
   standing unless the user says otherwise (everything he does is placed to that size). A black
   cat comes back charcoal or navy with orange eyes: recolour by rule. The user approves the
   still before any clip is made.
3. **Every clip again from the approved still,** each compared with the still on one floor line
   and shown in the chat on a real screenshot of a spot where it plays: `stand`, `run`, `wash`,
   `jump`, `sit`, `eat`, `bat`, `shake`, `asleep`. Template clips redraw a quadruped as another
   animal: PixMiniMax from his own picture holds him.
4. **Richer.** The list is the user's to settle in step 1; proposed: an idle that lives (a tail
   flick, an ear turn, a blink), a look back over his shoulder before he bolts, a stretch, a
   loaf, a turn round instead of a flip, lying down into `asleep` and getting up out of it, a
   landing after `jump`, and his own clips for the fly rope and the vent's squeeze (they were in
   §8; the scenes play with his other clips today).
5. **Tuned.** `run` paced by his planted paws against his 300 px a second; every clip set on the
   floor frame by frame; each hand-over between clips and with the scenes that move him (the six
   near-catches, his glimpses, the finale at the tip) looked at in time, not only in pictures.
6. **Everything else that shows him follows:** her sheet with him in her arms
   (`assets/sprites/her-cat.png`, PixelLab state `6905f308-15b1-4a44-ad97-a38a7ad17dff`; every
   pose the game asks of it), the catch, cabin 8206's scene and the day after, any gag or page
   that draws him. The picture over her crew cabin's bed is from a photo and stays.
7. Each near-catch and glimpse looked at enlarged in its place (he sits on our side of railings);
   the scenarios that have him (`finale`, the regions' near-catches, `deck3`), `boot`,
   `tools/check_overlaps.py`. The old sources are kept beside the new for comparison.

## 7b. Part 7: the intro's scene tuned (medium; about 30 generations, a guess)

Added 2026-11-19 on the user's word: "fine-tune the intro scene. I want more
realistically-looking sun and reflections, more varied and volumetric clouds." Built after
part 6 and before §10; numbered 7b so that no other section's number changes.

Design: `docs/intro.md` (the user's own document: read it, never edit it); `src/intro.js`'s
head comment; `CLAUDE.md`'s lessons of 2026-11-14 (the intro; the intro shown to the user) and
2026-11-07 (art far bigger than a generation).

**What there is today**, all drawn in code: the sun (`intro-sun` in `src/intro.js`: a disc, a
glow, two sets of rays that take turns); its glitter on the water (`intro-glitter-0` and `-1`:
short bright dashes in two frames, swapped 3.2 times a second); eight clouds round it (`CLOUDS`,
each from `cloudTexture()` in `src/background.js`: heaps of round puffs with a shaded lower rim,
the same recipe as the game's cloud strip, see-through).

1. **Ask first, by numbered questions,** with the three wide views as they are (`?intro=focus`,
   `sky`, `sea`) shown in the chat: what "more real" means for the sun (a soft disc with a
   bloom and no rays? a low warm sun? haze round it?); what reflects (a path of light on the
   water under the sun only, or also the clouds and the sky's colour in the sea, the ship's
   side in the water); how far from pixel art it may go; and **how far it reaches**: the intro's
   own sky only, or also the game's far background (the same clouds drift past in play) and the
   sunset's sun and path (`bg-sunpath`). This item is the intro's until the user says more.
2. **The look chosen from mock-ups of the whole screen,** two or three, composed offline over a
   real screenshot of the wide view with the menu on it, in both languages (the lesson of the
   menu's plates): the sun, its light on the water, the clouds together, not loose pieces.
3. **Then the art, generated** (the rule: art is generated, not drawn in code): clouds of
   several kinds and sizes with lit tops and shaded bellies, each its own picture, none
   repeated in a view; the sun and its bloom; the water's light. A cloud wider than a
   generation is made in tiles. The colours on the palette by rule, checked at the game's zoom
   and at 1:1.
4. **The motion, in code:** the path of light broken by the waves' own rows (`src/sea.js`), a
   shimmer that does not read as two frames swapping; nothing far off drifts in these views
   (the user's ruling, 2026-11-14: the camera stands still). It is judged in motion: the
   plainest version that runs is shown to the user before the rest is polished.
5. The welcome screen dims and blurs the sky: every new piece looked at there too, and through
   each part of the camera's way to the ship (`intro.seek`), where the sun, the clouds and the
   glitter fade as it goes in.
6. `intro`, `boot`, `lang`, `deck3`; if the user widens it to the game's background, `finale`
   and the whole ship rendered as well.

## 7c. Part 8: what she can use, does it stand out? (small to medium; added 2026-11-19)

The user, 2026-11-19, of the soft serve machine on deck 11: "Since the ice cream machine is interactable, it should have
a bit more contrast to it"; and, shown nine such things muted and in full colours: "In order to answer the contrast
question, I need to understand how that compared to other interactable things that already stand out in the game. Add
this to the end of the plan."

- **Found:** the map builder places most pieces as their muted background twins (`-bg`; `at11`, `at12` and others in
  `tools/build_ship_map.py`), and nine things she uses are among them: the soft serve machine, the coffee station (the
  engineer's coffee), the pool bar (the mojito), the lunch service station by the galley, the captain's door; and four
  secrets, the ice swan, the jackpot slot pair, the hot tub, the kids' slide. Each has a full-colour twin in the atlas.
  (Found by matching every world thing with an `interact` against the `-bg` pictures under it, in the running game.)
- **First, for the user:** one sheet of every thing she can use in the game as it is drawn now, side by side with what
  already stands out (the doors in full colours, the people, the pickups, the drawn rooms' things, the movers), each
  enlarged at its spot; so that the user can set the rule.
- **Then the user's rule** for what she uses and for the secrets (in full colour the jackpot pair stands out from the
  muted slots round it, which gives the secret away), and the rule applied everywhere it falls, by rule in the builder
  (a list of the pieces she uses, not by hand); `tools/check_overlaps.py` and a close look at each.

## 7d. Part 9: the tangerines' seats (medium; about 20 to 25 generations, a guess; added 2026-11-19)

The user, 2026-11-19: "I've seen a few places myself where tangerines are weirdly placed or misplaced"; asked for an
audit of every placement, of whether new props would give them sense and one look, and of the total. The design
session looked at all 56 in the running game, each enlarged with her beside it (43 spots). The user's answer to the
findings and the four questions: "Yes, do all as recommended. Add this as a new action point at the end of the plan."

**The rule from now on: a tangerine lies on food service or in a fruit bowl** (a tray, a trolley's plate, a bar, a
bowl, a crate in a store, a balcony table), or where the story put it (the hose cabinet, the canopy, the duct, the
fort, the ball pit, what an event pours out). **Never on bare furniture, never balanced on a thing, never in the air,
never behind someone.**

**The number stays 56** (41 lying, 15 from events; the win screen counts "found of 56"). Counted against what a run
spends since 1.2a: the five breakables, the bell and the sardines 7 (they pay back 9); the gulls' takes 3 to 6; a cry
or a throw to get a load through 4 to 8; lunges through hazards 0 to 20; typically 25 to 30. Someone who finds three
quarters has about 42, so D still costs and she rarely runs dry. Under about 48 she would run dry in the middle of the
game; over 60 the count means nothing. No tangerine is added or dropped; one pair moves about 6 m (4, below).

**The twelve** (`TANGERINES` in `tools/population.py`):

| # | Id | What is wrong | The fix |
|---|---|---|---|
| 1 | `tan_11_spa` | Floats about 15 px over the reception desk's end (`on` 40; the desk's top is lower) | The fruit bowl (prop B) on the desk, the tangerine in it |
| 2 | `tan_11_topsiders` | In the air beside the bar canopy's post, off the counter | Onto the counter, in prop B |
| 3 | `tan_4_laundry` | On its shelf, wholly behind the laundress's head (`amb_folder` at 258, the tangerine at 250) | One of the two moved clear; look at it with her in place |
| 4 | `tan_11_fruit` (two) | On a bare side table inside the buffet queue's line (`haz_queue`, 162.5 to 181.5 m; the pair at 176.8): the queue covers it, and standing there she is pushed onto it | A fruit stand (prop B on a counter piece) just aft of the queue's end, about 183 m, set against what is built there |
| 5 | `tan_5_dessert` | Balanced on the tips of the dessert cart's two glass domes | A plate on the cart with room for it (prop C) |
| 6 | `tan_9_cart` | Balanced on the dome's knob of the room-service trolley | A side plate by the dome (prop C) |
| 7 | `tan_12_cagneys` | The same, on Cagney's steel trolley | The same (prop C) |
| 8 | `tan_10_mid` | `prop_tray_10` (`@tray`) is drawn through the bare table's legs | One piece: the tray on its stand (prop A) |
| 9 | `tan_4_30` | The bare table stands against a fire extinguisher | Prop A, clear of it |
| 10 | `tan_8_aft` | The same | Prop A, clear of it |
| 11 | `tan_8_fwd` | A bare table alone in a cabin corridor, one tangerine on it | Prop A |
| 12 | `tan_9_luggage` | The same, behind the luggage stack | Prop A |

Small shifts, no art: `tan_6_windjammer` and `tan_12_spinnaker` lie on the barkeeper's hands and chest (along the
counter, clear of them); `tan_8_8206`'s two lie loose on the desk, one over a dark object (the plan's "welcome basket":
prop B there). Everything else was looked at and is right as it is.

**The cause of 4 and 8 to 12:** the `sidetable` picture (`src/textures.js`) is an early placeholder drawn in code, a top
and two thin legs. `placeTangerine` in `src/world/world.js` stands it under every `"table"` tangerine inside, the `item`
case under a pickup with no `on`, and the ship scene under the map's own `tangerine` objects: find what else stands
on it before it goes.

**The three props, each shown to the user enlarged beside her before anything is placed** (`CLAUDE.md`, "Art"):

- **A: a room-service tray on a folding stand**, two variants so that five corridors do not show the same one; in the
  `sidetable`'s place. Not a tray on the floor: those trip her (`trays`), and the two must not look alike.
- **B: a small fruit bowl** for a desk or a counter, the tangerine on top as in her crew cabin's bowl; and the piece it
  stands on at the Garden Café.
- **C: a side plate on each of the three trolleys** (the dessert cart, the cloth-covered one on deck 9, Cagney's steel
  one), each an inpaint of the game's own piece so that the rest of it stays to the pixel.

**Then:** the data (`on`, the metres, the holders), each of the twelve and the three shifts looked at enlarged with
the people of the spot in place and at the game's size; `tools/check_overlaps.py` lists nothing;
`tools/check_corridors.py`'s numbers given (the Garden Café's pair moves); the scenarios that pick these up by id,
and `boot`. `docs/population.md` §2.3's rows, `GAME_DESIGN.md` §6.3.

The audit's pictures were made by a script outside the repo (her teleported beside each `tangerine` of
`maps/world.json`, `Browser.close_up` on it); they are not kept. Make them again the same way before and after.

## 7e. Part 10: the checkpoints, nineteen places (medium; about 20 generations, a guess; added 2026-11-19)

The user, 2026-11-19: "I've seen a few places myself where doors are stuck at weird places or misplaced"; asked for an
audit of every checkpoint: placements that make no sense, new props for more variety of doors, the best total for the
progression, the routes and the map, "Don't make the game too easy", "Remove redundant/unnecessary checkpoints". The
design session looked at all 32 in the running game, each enlarged with her beside it, unlit and lit, and worked out
from the hazards' places and the game's own rule (`closestCheckpoint`) where every scare sends her back. On a first
proposal of 28: "I feel like that is too many checkpoints in the game". On the leaner one: "Yes, let's try those 19";
on a new one for deck 10's midships hallway: "No, don't add".

**The test for each: a checkpoint stays only if a scare sends her back to it, and taking it away would cost her hazards
to do again, not only an empty walk.** None stands inside a run of hazards; none on a calm stretch.

**Today 32 as the game counts them, at 26 places** (a balcony cabin has two, one at its corridor door and one at its
balcony door, the hallway and the balconies being two routes). **From now 23, at 19 places:**

| Where | Id | What it is | Changes |
|---|---|---|---|
| Deck 3, 90 m | `cp_crew` | Her crew cabin's door, lit from the start | None |
| Deck 4, 72 m | `cp_gangway` | The gangway lobby's crew door | None |
| Deck 4, 111.6 m | `cp_laundry` | The lamp over the laundry's door (the foot of the vacuum's corridor) | None |
| Deck 6, 160.9 m | `cp_library` | The Library, beside its promenade door: the promenade's scares come back here, two steps from the way out | Its place and its door, below |
| Deck 6, 204.4 m | `cp_foyer` | The theatre's foyer | Its place and its door |
| Deck 7, 189.2 m | `cp_7_aft` | The Arcade | Its neighbours and its door |
| Deck 8, 43.3 m | `cp_8206` | The lamp over cabin 8206's door | None |
| Deck 9, 118.2 m | `cp_9_arrive` | **The crew trunk's own door, the one she comes out of** | The twin door 1.4 m aft goes |
| Deck 9, 191.6 m | `cp_9_mid` | The crew door at the corridor's aft end | None |
| Deck 10, 41.6 m | `cp_bridge` | The crew door by the bridge | None |
| Deck 11, 82.7 m | `cp_gym` | The crew door between the lobby and the gym's windows | None |
| Deck 11, 140.6 m | `cp_pool` | The pool attendant's hut | None |
| Deck 11, 192 m | `cp_garden` | The Garden Café's service door | Out of the window, below |
| Deck 12, 165 m | `cp_technical` | The technical door at Cagney's forward end | Its neighbours and its door |
| Deck 9, 150 m | `cp_balc_9` | The balcony cabin, **its balcony side only** | The corridor side goes |
| Decks 8, 9, 10 | `cp_hall_8m`/`cp_balc_8m`, `cp_hall_8a`/`cp_balc_8a`, `cp_hall_9a`/`cp_balc_9a`, `cp_hall_10a`/`cp_balc_10a` | The four hallways' cabins with an ajar balcony door, both sides: each is its hallway's only way in | None |

Fourteen on the main way, five balcony cabins in the optional outside region.

**The nine that go, and what each costs her:**

| Id | Why | What changes in play |
|---|---|---|
| `cp_6_fwd` (deck 6, 40.9 m) | Nothing scares on deck 6 forward; it took deck 5's scares and put her a deck up, 38 m from the stairs | Deck 5 forward's scares (the papers, the breakfast round) come back at the gangway lobby, a flight below |
| `cp_4_aft` (deck 4, 211.6 m) | No scare returns to it | Nothing |
| `cp_officer` (deck 10, 61.6 m) | 20 m from `cp_bridge` in a calm corridor; its door was drawn over the officer who stands there (`amb_officer_10`, 60 m) | Nothing; he stands at a cabin door again |
| `cp_hall_guest`, `cp_balc_guest` (deck 10, 235.6 m) | 20 m from the other cabin of deck 10's aft hallway | A gull at 231 m on the balconies costs 16 m, not 5. The guest, his cabin, his balcony door as a way in and his book stay |
| `cp_chapel` (deck 12, 70.7 m) | No scare returns to it | Nothing |
| `cp_funnel` (the funnel's top) | A gull's hit bumped her down to the stairway's foot and she then came back at the top; a door on an exhaust pipe | Any hit on the stairway, and a fall from the top, come back at the technical door: the climb again |
| `cp_station` (the boat walkway, 128 m) | A crew door in the walkway's glass wall, drawn over the railing | The drill's boat costs about 100 m, not 58: back at the Library (or the Arcade), out to the promenade, up the ladder. Deck 8's balconies reached from the walkway, with no balcony cabin lit yet, come back inside the ship |
| `cp_balcabin` (deck 9's corridor, 151.6 m) | It lit as she walked past the cabin's locked door, in the middle of the corridor's hazards | On the way out every hit in deck 9's corridor comes back at the trunk (up to 48 m, the vacuum and the sprinkler again); on the way back, at one of the two ends |

**Not added (the user):** deck 10's midships hallway, under the pool's hatch, keeps none. She comes back at the pool
attendant's hut above the hatch for three of its four scares, and at deck 9's aft end for the "Do Not Disturb" door at
171.6 m.

**One rule in `closestCheckpoint` (the ship scene): she never comes back behind a door that is shut to her.** Among the
lit checkpoints on her deck and route, leave out any with a wall across the deck between it and where she was, whose
door would not open to her coming from the checkpoint's side (a one-way door not opened yet, a card or a flag she lacks:
`passes()` in `src/progression.js`); with none left on her deck, the nearest deck as now. Found in the running game: hit
by deck 9's aft swinging door (`haz_swing_9a`, 207.6 m) on her first way forward from the cabin, she comes back at
`cp_9_mid` (16.0 m against 16.0), outside the hallway, behind `part-door-9-202` (shut from the lobby's side), and the
only way in again is the balconies. Deck 10's midships scares, once `cp_hall_10a` or `cp_bridge` is lit, are the same
case. A check for it in `region7`.

**The six doors that stay and stand wrong** (nine did; `cp_officer`, `cp_station` and `cp_funnel` go):

| Id | What is wrong | The fix |
|---|---|---|
| `cp_foyer` | The door stands on the Stardust Lounge marquee's gold post (`stardust-entrance`, its post ends about 204.3 m) | About 1 m aft (about 205.3), clear of the post and of the first seat (206.6); prop B |
| `cp_7_aft` | Squeezed between an arcade cabinet (188.3, where `amb_teen` plays) and the claw machine (190.0), a third of a metre each side | One cabinet out or the row spread: a clear metre each side; prop B |
| `cp_library` | White on the dark panelling, a quarter of a metre from the wall's pillar and 0.85 m from the promenade door (`door-deck`, 162.2) | Centred in the gap (about 161.1); prop C. It stays beside the promenade door on purpose |
| `cp_technical` | Wedged between the wall across the deck (164.2) and the wine cabinet (`wine-cabinet-bg`, 165.9), its lit leaf over the cabinet | The cabinet moves aft of the kitchen or goes; half a metre clear each side; prop C |
| `cp_garden` | In the café's window (the run ends about 193.3 m), a wicker table and chairs at its edge (190.3 to 191.3) | The window run ends a pane short, as at `cp_gym`; the table a metre forward; the white crew door stays |
| `cp_9_arrive` | A second white door 1.4 m from the trunk's, the two alike | The trunk's own door carries the lamp (`addCheckpoint(..., { door: null })`), above its arrows' plate as her crew cabin's sign is above its lamp, whichever order reads; it lights as she steps out of the trunk |

`cp_gangway`, `cp_9_mid`, `cp_gym`, `cp_bridge` and the pool's hut were looked at and are right; so are the lamps over
doors drawn already.

**Two props, each with its lit twin, each shown to the user on a screenshot of its two places, shut and lit, before
anything is placed** (`CLAUDE.md`, "Art"). The green lamp over the door is what says checkpoint everywhere; the door is
its place's own:

- **B: a padded theatre door** (dark leather, brass studs, a small round window), for the foyer and the Arcade's night
  blue walls.
- **C: a dark wood service door** (a brass kick plate), for the Library's and Cagney's panelling.

Each on `door-crew`'s frame (29 x 74) so that its placing holds, in full colours as every door of hers; the ajar twin
built from the shut one's frame, the warm light in the gap as `door-crew-ajar` has it (`CLAUDE.md`, "Two states of one
thing share one frame"). `addCheckpoint` takes the door's name already; `lightCheckpoint` sets `door-crew-ajar` for all:
the door's own twin. `tools/check_overlaps.py` knows a door by its picture's name: the new names go in. The white crew
door stays in the corridors and lobbies. (The design session made four tries of a steel locker for the walkway and the
funnel, 4 generations, before those two were dropped: PixelLab map objects `3bfbdd69`, `24fa40fb`, `bfe5b772`,
`16aeb45b`, not used.)

**In the data and the code:** `CHECKPOINTS` in `tools/population.py` loses `cp_6_fwd`, `cp_4_aft`, `cp_station`,
`cp_officer`, `cp_chapel` and `cp_9_arrive`'s own door; `ROOMS` loses `checkpoint=` on `balcabin9` and `guest10`;
`BALCONY_CPS` loses `cp_balc_guest`; `cp_funnel` goes from `src/world/world.js`. The three that took a cabin door's
place (`slot`) give it back by the corridor's rule: look at each. A save that names a checkpoint that is gone starts her
at the start (`initialSpawn`): fine while nothing is saved (`DEV_FRESH`), one line to keep in mind for the release.

**Then:** each of the nineteen looked at enlarged, unlit and lit, with the people of the spot in place;
`tools/check_overlaps.py` lists nothing. The playtests that name what goes or moves: `region4` (`cp_balcabin` as the
card opens the cabin; `cp_9_arrive` by its id still), `region7` (`cp_balc_guest`; the new check), `region8`
(`cp_funnel`, and whatever expects her back at the top), `region9` (`cp_chapel`, `cp_officer`); run those,
`region1` to `region3`, `region6`, `mishaps`, `finale`, `boot`. The documents: `docs/population.md` §2.5 and each
deck's rows, `GAME_DESIGN.md` §5.5 and §6.1.3's "Checkpoints" lines.

**"Let's try" is the user's word: the number is judged in play.** If it is still too many, the next to go, each with
its cost: `cp_gym` (the sauna's steam then costs an 88 m empty walk from the pool's hut), `cp_laundry` (the first vacuum
sends her back to the gangway, past the dog again), `cp_7_aft` (the casino's chips wake her a deck down, in the
Library). Under about eleven on the main way, scares wake her on the wrong deck as a rule.

The audit's pictures and its model of the returns were made by scripts outside the repo (her teleported beside each of
`window.__ship.checkpoints`, `Browser.close_up`; `closestCheckpoint` asked with a given set lit); they are not kept.

## 8. Optional, each only on the user's word

- **The Library's rolling ladder** (`sec_ladder`, `docs/population.md`): pushed along the
  bookcase and climbed; never built, and the odd book it led to answers E from the floor. Ask
  whether it is still wanted (medium; one piece of art).
- People who stand still: the wedding's guests (talk, laugh), the security officer's wave from
  the bridge floor, the stage manager's talk, deck 12's chefs, waiter, shuffleboard player and
  one of Champs' three, a second look for the sunbather when startled.
- The string trio on the atrium floor; the Seven Seas' other two tables of diners
  (`docs/population.md` asks three, one is built); deck 5's open cabin with a guest at the
  window (`amb_robe_5`; the knitting lady's open cabin fills that stretch now).
- (Bumbot's own clips for the fly rope and the vent's squeeze: moved to §7a, 2026-11-19.)
- The Photo Studio's flash as a hazard "when paired with a cart" (a gag only, today).
- The ship's side: the funnel's white base, the open decks' bulwarks and the sun cover are
  still plain (`tools/shell_paint.py`).
- The places the audit found empty and no plan names: deck 4's last 14 m, the Internet Café, Le
  Bistro, four of the five balcony cabins. Those left empty by choice stay so (the aft ends of
  decks 9 and 10, Magnum's, the Spinnaker's balcony, behind the flares).

## 9. Waiting for the user

| # | What is owed | Then |
|---|---|---|
| U1 | A photo of her husband (or a description in words) | His own character and clips (sit with a cone, eat, wave, laugh, give, a pose for the cabin) in place of the stand-in |
| U2 | The pictures for five photo slots (the lifeboat, the lighting bridge, deck 8's first balcony, the chapel, the table); "once the game is tested and verified" | Pixel art from a cutout, candidates shown; today a heart in a frame |
| U3 | The win screen's own message, in both languages | `WIN_MESSAGE` in `src/config.js` (empty) |
| U4 | The names on the crew doors (BOSUN, PURSER, DJ, STAGE MGR stand in) and on the captain's | Lines of data |
| U5 | Whether the chapel's wedding is anyone in particular; whether the rival has a name | As answered |
| U6 | **Their ears on the sound:** no record of any of it having been heard (about 130 effects, the ambience, and those added since: the lunge, the pocket, the dog, the papers, each gag's) | The soundboard, <http://localhost:8000/tools/soundboard.html>; changes as asked |
| U7 | Music, or none ("No music for now") | Only if wanted |
| U8 | The bridge and the spa hidden until she enters them (`LOCKED_PARTS`, off since 2026-11-08 "until we settle how the ship is split") | A switch and a look |
| U9 | Deck 7's stern strip: "maybe a secret place later"; today she can only leave it by jumping off | As decided |
| U10 | V4 and V5 of the audit: she is hard to see on the Spinnaker's balcony and at the promenade's enclosed ends ("Leave as they are for now") | Cut the side open there, or draw her in front of the glass |
| U11 | The mooring deck can be reached from deck 8's forward terrace before the sunset, its door shut, and the hint that covered it went with every popup. Acceptable so? | As decided |
| U12 | Functional signs stay English in the Ukrainian version: the answer was "Ok", taken as yes | A confirmation |
| U13 | A pause, a map ("at least for now" neither); a controller button for the outside view (O) | Only if wanted |
| U14 | The real Xbox controller through the whole route (the mapping and rumble are built, the test drives a fake one); with the controller alone the game may stay silent until a key or click | The user's own run |
| U15 | The user's own touches to the livery (`assets/source/livery/livery-by-hand.png`) | The user's own |
| U16 | Fine placement of everything, and the numbers, in play: the cry and the lunge, ~~the pocket's roll~~ (gone with 1.2a: now how often a hit sends her back, and how far), how often she runs dry, each gag's length, the glide, the checkpoints' spacing | Her playtest and the user's |

## 10. Once, at the end (on the user's word)

1. **Documents out of step with the game, found while reading** (text only; `CLAUDE.md` and
   `README.md` were brought up to date on 2026-11-18):
   - `GAME_DESIGN.md` §8: "Next up" is dated 2026-11-03, and about fifteen boxes are open that
     are built or dropped (the locks "off for now", the checkpoints, the outside, the finale's
     art, the sun emblem, the glyphs, the gulls); §4 opens with "None of it is in the game yet"
     (Bumbot's six beats and his glimpses are all placed); §6.1.3 and §6.1.11 still describe the
     stern strip's slot (moved to deck 8's first balcony).
   - `docs/build-plan.md`: the intro's entry still ends at her mirror and waits for her
     photos (dropped); "the ten titles".
   - `docs/population.md`: no rows for region 1's new things; rows that no longer match
     (`slot_stern`, `sec_ladder`, `haz_pit`, the breakfast, the notice, the trolley at 130 m);
     glyphs named after the no-hints rule; the tangerine table "as first written".
   - `docs/audit-2026-11-15.md` was never marked with what was fixed (V1, V2, V3, V6, V7).
   - `docs/start-links.md`: three places under the wrong deck.
2. **Saving on:** `DEV_FRESH` to false ("Set to false before the gift"), and a pass over what
   the save must now hold (`save.loose`, `save.keeps`, `save.broken`, the heaps, a tangerine
   left on the steward's cart; the verb still named `dash` in the save).
3. **The whole route walked with the locks as they are** (step 0's exit, never recorded), and
   finished once without spending a tangerine (the audit's C10 was read from the data, not
   played). The whole suite, on the user's word.
4. **Her playtest**, and what it changes (U16).
5. **The release:** GitHub Pages back from the `placeholder` branch to `main`; the links
   without `&tangerines=infinite`.

## 11. Checked by hand (2026-11-18)

- `MISHAP_SCENES` in `src/config.js`: the scenarios with no `gag` are 1, 2, 7a, 9a to 9d, 10e,
  11a, 11b, 12a, 12b, 13b, 14a, 14b, 15, 21 to 24 (21 to 24 and 7a built since: `stairs`, `parasol`, `sorry`, `sledge`). `src/world/mishaps.js` still returns `13b`.
- `tools/playtest.py` has no `mishaps`, `keeps` or `deliveries`.
- `KEY_CARDS.required` is `true`; `src/progression.js` knows no `locked`.
- `DEV_FRESH` is `true`; `WIN_MESSAGE` is empty.
- `main` and `three-uses` hold the same files (`0c99e7d` is the merge).
- PixelLab: 4,388 generations left, Tier 2, the cycle ends 2026-12-16.

Not checked by hand, taken from the readers: each row of `docs/population.md` against the game
(363 ids by script, about sixty looked at); where the cabin numbers are drawn (§6 says to find
it first); whether the two `deck4` checks still fail on the stepped clock.

## 12. Looked at and closed (do not reopen without the user)

- The stern's tiers climb and deck 7's stern-strip slot: cannot be played, left out; the slot is
  on deck 8's first balcony. The orchestra pit: the rival goes down the trap door.
- The close-up at her mirror in the intro (`docs/intro.md`'s last part): built and dropped on
  the user's word; her portrait and her photos went with it.
- Every hint popup but "E to interact". The "LOST: CAT" note.
- More tangerines on decks 4 to 6: "leave their number and their location unchanged". A trail
  of small pickups: decided against. (2026-11-19: the number was looked at again and stays 56;
  what twelve of them lie on is mended in §7d, on the user's word.)
- The audit's I1, I5, I8, I11; V9 and V11 (choices, not faults); V1, V2, V3, V6, V7 (fixed).
- 13b, 4c, 10b's squirm, 7b's fold "shut on her" (the collapse was taken).
- **A tangerine lost to a hit, everywhere but the gulls' three (20 to 22)** (the user,
  2026-11-19; §3 1.2a): the tangerine knocked out of her pocket to roll off behind her, her
  short reactions to a hit, the tangerine held out at a "Do Not Disturb" door, a tray saved by
  a tangerine, her "bats the towels off".
- The controller's mute (keyboard only). A whole suite before each merge ("The old rule").
- A gust carries her twice what its data says: known since region 7, every gust is tuned to it.
- After the sunset, the stairs to deck 8's forward terrace are a way round the glide: left in,
  "a crew member's shortcut".
- Two sessions building in workspaces of their own, each with half of this plan: set up on
  2026-11-18 and taken down the same day on the user's word ("too convoluted and hard to
  track"). One session builds; one designs.
