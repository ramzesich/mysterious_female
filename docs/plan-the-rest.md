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
4. **Built outside this plan by the Refinement session (2026-11-20, the user's): every popup's look**
   (`src/popup.js`, `CLAUDE.md`'s table and its rule): speech bubbles, thought clouds, her cry's burst, the
   hints' plate, each tail from the speaker's head. A new word or wish over a head goes through it
   (`world.say`, a person's `bubble`), and a sheet of hers or the people's rebuilt is followed by
   `python tools/build_heads.py`. Not touched: the full-screen panels (the close-ups, the Library's,
   the covers' moment of §2.3) and the HUD (§2.4).

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
| 7 (§7b) | The intro's scene tuned: a more real sun and reflections, clouds more varied and with volume (added 2026-11-19). **Built 2026-11-20 by the Refinement session** (branch `refinement`, `4eb23d8`, `504be54`), the sunset's sky with it: not to be built again | The user's word; `docs/intro.md` | Medium | About 30 (the design session's guess); 160 spent |
| 8 (§7c) | What she can use: does it stand out? A comparison across the game, then the user's rule (added 2026-11-19). **Built 2026-11-23 by the Refinement session** (branch `refinement`, `e621d5b`, `cefcf4c`): the pulse where E would act, and doors washed like their neighbours: not to be built again | The user's word | Small to medium | None |
| 9 (§7d) | The tangerines' seats: twelve placements that make no sense mended, three props for them; the total stays 56 (added 2026-11-19) | The user's word; the design session's audit | Medium | About 20 to 25 (the design session's guess) |
| 10 (§7e) | The checkpoints: 19 places from 26 (23 from 32 as the game counts them), six doors that stand wrong mended, two door props, never back behind a shut door (added 2026-11-19) | The user's word; the design session's audit | Medium | About 20 (the design session's guess) |
| 11 (§7f) | The empty stretches: sixteen obstacles on the walks where nothing can catch her, twelve of them things already built, placed anew; six ends given a purpose, so that every long run has both; the rule "nothing is used twice" dropped (added 2026-11-21, two rounds) | The user's word; the design session's audits | Large | About 80 (the design session's guess) |
| 12 (§7g) | "Washie, washie, happy, happy!": the crewman with the sanitizer at the Garden Café's door by the aft lifts (deck 11), the user's and his wife's own joke: a first meeting that cannot be missed, their duet, foamy paw prints past him, a tangerine washed and tossed back, the song stuck in her head (added 2026-11-21) | The user's word | Medium | About 25 to 30 (the design session's guess) |
| 13 (§7h) | The balconies' doors: the five ajar balcony doors (decks 8 to 10, region 7) do not look like doors at all; made to read as doors (added 2026-11-23) | The user's word | Small to medium | A few (a picture of a balcony door) |
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
| 4 | Bumbot's | Collar bell | The promenade, a gull on a lamp | A lob: it drops the bell for the fruit. **A new mover** (her cry: it flaps and keeps the bell). **Placed 2026-11-20:** `BellGull` on the round wall light at 140.6 m (ten lights along the promenade, the user's), any throw that reaches it (a lob from the deck, or **her throw in the air**, new, the user's word), the bell's collar drawn in its beak, its close-up the collar |
| 5 | Bumbot's | Liquid snack in a tube | Deck 4, the dry store, on a shelf | E (green card). **Placed 2026-11-19** (the bottom shelf, by its tangerines) |
| 6 | Bumbot's | Massage gun | Deck 11, ~~the gym, the bench by the weights~~ ~~the rowing machine's seat~~ **the spa's masseur gives it, after her massage** (the user, 2026-11-22) | ~~E. Placed 2026-11-19, moved 2026-11-20~~ **Built 2026-11-22:** E at either massage table: the masseur's round of massage (behind the table, a stretch at her feet, in front his back to us, a stretch at her head), then his toss of the gun, the first time only; at his guest's table the guest goes to the sauna's bench meanwhile and comes back (`src/world/spa.js`, `MASSAGE` in the config). Region 9 (the spa opens then), no longer region 6 |
| 7 | Bumbot's | Tin of sardines | The Sushi Bar | The chef's bubble shows a tangerine; he takes one for it (the apology's hand-over). **Placed 2026-11-20:** his cloud once she is near; E with one: her bow, he takes it over his case and hands the tin across; a throw that reaches him (a lob close, a throw in a jump from further) is caught and the tin set on his case for E; the tin try 4 in its own colours, drawn by hand at game size; the nigiri moved behind him |
| 8 | Bumbot's | Remote-controlled car (beige, two big rubbery cyan wheels: the user) | Deck 7, Entourage, past the ball pit | E. **Placed 2026-11-19, moved 2026-11-20** (on the air hockey table, left of its post: the user) |
| 10 | Hers | Bookmark with a cat on top | ~~Deck 6, the maid's cabin, in the book by the bed~~ **Deck 9, the cabin being cleaned, in its book on the stripped bed** (swapped with 12, the user: that cabin has no window) | E. **Placed 2026-11-19; approved 2026-11-20**, the bed freed (its stewardess moved to a new cabin on deck 10, `makeup10`, her shake at half pace) |
| 11 | Hers | Diary notepad (brown leather, a strap with a brass buckle: the user) | Deck 7, the Stardust balcony's far end, on a seat | E (look-out 1 will be at the same end). **Placed 2026-11-19, approved 2026-11-20** (the last seat, by the railing: 9 px aft, 4 px down, the seat's near arm over its foot) |
| 12 | Hers | Small plant in a pot | ~~Deck 9, the cabin being cleaned, its windowsill~~ **Deck 6, the maid's cabin, its windowsill** (swapped with 10) | E from the maid's bed, not the floor (`from`). **Placed 2026-11-19, approved 2026-11-20** |
| 13 | His | ~~Ice cream spoon~~ **His navy t-shirt** (the user, 2026-11-21) | ~~Deck 11, the Great Outdoors, the last table at the stern rail~~ **Deck 12, the sun deck over the pools, folded on the first lounger (111.25 m)** | E, after the table scene. **Placed 2026-11-21:** its close-up the top half of the shirt with the logo from his photo ("bluevine cares", the user's own pixel edit); folded in the world, no logo; the sun deck's two loungers replaced by a new longer one, no armrests (the user's) |
| 14 | His | Sleep mask (pink-beige, one strap: the user) | Deck 10, ~~the far balcony~~ **the first balcony of the row, its forward end (62.9 m)** (§7f, P3), on a sunbed | E, after the table scene. **Placed 2026-11-21:** on deck 12's long lounger set on that balcony by hand (`BALCONY_SET`), its towel moved to the next one, blue; the close-up try 1 of four, smoothed by rule (the user's choice: the 2 px band, the strap's tabs the same size); in the world it shrunk, outlined, 16 x 8; with it the balconies mended (no drop where no floor is one deck under her; her picture cut at partitions and rows' ends) |
| 15 | His | Handheld (his ROG Xbox Ally X, black, RGB rings round its sticks, no logo) | Deck 12, Champs, on a sofa | E, after the table scene. **Placed 2026-11-21:** Champs had no sofa: a new one (try 3, its own brown lightened 1.9) in the aft high table's place, the fans moved to the bar's ends; the bar bigger, after the real Champs Bar's teak; the close-up a pro redraw of the user's photo of the model; the world picture 24 x 11, built feature by feature and then the user's own Paint edit (`handheld-by-hand.png`) |
| 16 | His | Guitar pick (his own: red, a Jazz shape, a dot grid; from the user's photo) | Deck 12, the Spinnaker, the bandstand by the piano | E, after the table scene. **Placed 2026-11-21:** the lounge had no bandstand: a guitar on its stand by a small amp, generated together, between the cream armchair and the sofa; the pick on the amp, point up (resting on its wide edge); the piano 8 px forward, the two seated guests 2 px down (the user's placing); the close-up from his photo, its edges cleaned |
| 17 | Book 11 | נערה במעיל כחול | The boat walkway's end, beyond the boat drill | E. **Placed 2026-11-21:** on the lid of a generated life-jacket box against the railing at the walkway's aft end (the user's placing); the walkway mended on the way (`docs/progress-decisions.md`) |
| 20 | Book 14 | Pachinko | Deck 9 forward, the officers' corridor's end | E (look-out 4 will be at the same end). **Placed 2026-11-21:** on a generated half-moon console table between the corridor's end wall and the captain's door (the user's choice of four, 1 px down) |

- **Built so far (2026-11-19): 5, 6, 8, 10, 11 and 12 placed; and the user's "A and C" for every thing
  to find and every key card:** (A) in the world a little bigger than life, each the shrink of (C) its
  **close-up**, a detailed generated picture (about 100 px) shown in the middle of the screen at 2x over a
  dim with a warm light behind it when she gets it, any key closes it (`world.closeup()`;
  `assets/source/closeups/`, `tools/build_closeups.py`). The four already placed got theirs too (the tennis
  ball, the feather and the flag a new world sprite from it; the wool a small picture of its own, its strand
  over the basket's rim); the dog's owner's toss holds the new ball over her far hand. 26 generations.
  **Waiting for the user: the locations of all ten, judged in play** (the links: `docs/start-links.md`, five
  new places `store4`, `maid6`, `knit5`, `shore5`, `balcony7`); noted for that: the flag now stands 16 px
  among four of 13, the brown diary on a red seat. Next after it: 4 (the bell gull, **placed 2026-11-20**) and 7 (the sardines),
  his four (13 to 16) after the table scene (**13 to 16, his t-shirt, sleep mask, handheld and guitar pick, all placed 2026-11-21**), then 2.2 before the two books (**2.2 built 2026-11-21**). **2026-11-20: all ten approved where
  they lie** (the user's review, in play). The close-ups also as the HUD's
  icons (2.4): superseded, the HUD's kinds are faces (built 2026-11-20).
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

**Built 2026-11-21** (with the user, step by step; `docs/progress-decisions.md`, "2.2"):
- **Fourteen everywhere:** one total, `BOOKS = 14` in `src/config.js` (the shelf's gaps, `books_all`, the HUD, the
  trolley's last return, the nook's test); one list of colours (`BOOK_COLOURS`, four new stand-ins until 2.3).
- **The shelf:** over the two bookcases by the librarian's desk, from the first's left side to the second's right,
  2 px higher, no brackets; the books back on it washed 12% toward the wall ("now they look like pickable objects").
- **The odd book** (the nook's): standing in the top shelf of its bookcase's third glass door, among the lit books, no
  longer hanging on the glass.
- **The pages are text, all fourteen** (the user: "Text only for all the books"; the ten drawn hint pages are gone):
  each book's real opening in its own language and script, readable, whole sentences, covering the page (Pixelzone,
  CC0; `tools/draw_pages.py`, `assets/source/pages/`, its README says where each text came from). **Books 1, 2, 4, 6
  and 14 typed by the user from her copies (2026-11-22)**; book 4's page may end a sentence at its colon (`COLON`).
- **Reading, anywhere she can sit** (the user's design, mock-ups approved round by round): E at any of the Library's
  seven armchairs (the red one and the six at the reading tables, now in full colours: **2.3b is built with it**) or on
  her bed in cabin 8206; she sits (two generated clips: facing us in the armchair, side-on against the pillows on the
  bed, `tools/build_reading.py`), the books she carries in a row over a soft rounded backdrop (1 to 14 fit), ← and →
  (d-pad or stick) choose, E reads, Esc/B/Space get up; any book, as often as she likes; a hint once. Book 5 is a
  regular book (no more reading it only on her bed). `?books=3,8,11` starts her carrying books.

### 2.3 The titles: covers, their moment, ~~the shelf seen close~~, the nook's photo (large; about 30 generations)

`docs/plan-three-uses.md`, step 5's revision of 2026-11-18. **1 to 3 built 2026-11-22** (16 generations): the
covers are her own copies' (the user's photos, `reference/books/`), `tools/build_covers.py`; 4 dropped 2026-11-22 (the user: "no need for that"; nothing else rides on it); **5 built 2026-11-22. 2.3 is done.**

1. **BUILT 2026-11-22: `tools/pixelzone.py`** (the pages' Pixelzone drawn exactly, Й/й mended). **The lettering tool first** (new): each title and author set on its cover and spine from a
   font with every script needed (lower case, Polish letters, Russian and Ukrainian Cyrillic,
   Hebrew from right to left), at whole pixels. The books' own texts do not go through
   `src/lang.js`. Each spelling checked against her copy (the photos: `reference/photos/Books`).
2. **BUILT 2026-11-22, the user's: her own copies' covers** (photographed, words painted out, `image_to_pixelart`,
   title and author set back in). **Fourteen covers, generated, each its own:** shown enlarged, numbered, title and author
   drawn in, before any is placed. The small book in the world and its spine take their colours
   from its cover.
3. **BUILT 2026-11-22** (`world.cover()`, a 35% dim with the close-ups' warm light, the user's B; `region2` checks
   it). **The cover's moment:** in `world.take` and `world.giveBook`, after the sparkle or the
   hand-over: the Library's `panel()` with a lighter dim, the cover in the centre, any key
   closes it. Each of the fourteen, once.
4. ~~**The shelf seen close:** `sec_shelf` answers E: a generated picture of the shelf over the
   screen, the returned books' spines with their titles laid in from the save, gaps for the rest.~~ **dropped 2026-11-22 (the user: "no need for that"; nothing else rides on it).**
   The shelf itself stays as built: the returned books' spines in their covers' colours, the odd book and the nook.
5. **BUILT 2026-11-22:** her armchair (the user's photo cut out, PixelLab's try 2 of three recoloured to her greys
   with the throw's weave: `tools/recolour_nook_photo.py`), small and faded in a gold frame over the nook's table
   (`tools/frame_nook_thumb.py`), framed when seen close. **The reading nook's photo** (given): pixel art from a cutout
   on a flat ground, candidates shown first; in `slot_nook`'s frame.
   **With it, the user's (2026-11-22):** the row of books shows every book found, the given-back greyed with a green
   check stamp and RETURNED by the title (E does nothing on them); the trolley's row to choose which goes back; the
   nook's armchair reads all fourteen; the bookcase slides aside behind its neighbour with puffs of dust, the screen
   still, the entrance a casing round the nook's washed view; the stack of books left of the nook's door, its cat
   picture generated; the return trolley and the shelf's board generated; the row's small covers PixelLab's redraws of
   the covers' pictures without their lettering; the win screen counts 14; `?at=nook`.
6. ~~**The user's to answer before they are built:** whether books 11 to 14 get hint pages~~ (answered 2026-11-21:
   every page is its book's opening, no hints, 2.2) ~~(plain
   until then); whether the Library's small shelf and return trolley, drawn in code, are
   generated too (proposed).~~ (answered 2026-11-22: generated, built.)

### 2.3b The Library's reading chairs, every one to sit in (small; no art; added 2026-11-20, the user) **BUILT 2026-11-21 with 2.2**

All seven armchairs are seats she reads in, in full colours; they turned out to be the same front-facing armchair, so
she sits in each facing us (her new clip), not side-on as below.

Asked in the Refinement session's audit of the background props' wash (the user: "Make all three chairs
interactable ... she can sit in either of them"). Today one red reading chair is hers (`sec_chair`,
`src/world/library.js`: the game's own `reading-chair` and `floor-lamp`, in full colours) and the four
beside the two reading tables are the map's background (`around(6, m, "reading-table-bg",
"reading-chair-bg")` in `tools/build_ship_map.py`), washed, so one chair of three read differently.

1. **All five in full colours:** the four by the tables become `reading-chair` (not `-bg`); the floor lamp
   stays as it is. The reading tables stay background (the Refinement session's wash, below).
2. **Each one a seat:** E at any of them is `read()` from that chair: she sits in it (facing the way it
   faces: the two round a table face each other, so `flipX` from the chair, not always false), the next
   book she has not read, its page. The chairs' places come from the map's data, as `data.chair` does now.
3. **Checked:** her seated clip (`her-read`) in each chair, enlarged, both ways she faces (the art rule's
   overlaps and floor line); `region2`'s reading check still passes; nothing else in the Library answers E
   from where a chair now does (the trolley, the shelf).

The background props' wash is the Refinement session's (the user's levels per deck, 2026-11-20; the Library
at 12%): not part of this item.

### 2.4 Cabin 8206's desk, the day after, the counts (medium; little art)

- ~~**The desk:** his four and her four, each a prop shown from its own find on. **First the
  picture of the desk with all eight, shown to the user**; if it is crowded, some of hers go by
  the bed (`tools/draw_cabin.py` for where the desk's top is).~~ **BUILT 2026-11-22, otherwise (the user's):** the room
  has no space for the eight at the game's size (two layouts in the room shown, "the things can't be arranged there
  properly"), so **the desk seen close**: E at the desk, any time she is in the cabin (Bumbot in her arms too), shows a
  generated picture of it (the TV's lower edge over it) over the whole screen, each of the eight from its find, bare
  desk where one is not yet found, and with none (`tools/build_desk.py`, `assets/source/closeups/desk/`, `world.seenClose('desk')`,
  `?keeps=`). The room's desk keeps its two tangerines, moved onto its top (they stay till picked up).
- ~~**The day after:** Bumbot's eight laid out with him (`src/world/finale.js`).~~ **BUILT 2026-11-22, otherwise (the
  user's):** the room has no space for them either (the bed's reading spot kept free), so **his bed seen close**: on the
  day after, E by him from the floor, he purrs and a generated picture shows him lying on the bed (from the user's photo,
  eyes open) with his eight round him, each from its find, bare bed where one is not found (`tools/build_desk.py`,
  `assets/source/closeups/bed/`, `world.seenClose('bed')`, `?keeps=bed`). On the bed E is her reading (it had been his purr
  within 26 px of him, and her seat is 18 px from him). No hearts on E (the picture covers him).
- **The HUD:** **BUILT 2026-11-20** (the user's design; `docs/progress-decisions.md`, "The HUD redone"):
  each count appears with its first find, the kinds as faces (Bumbot's, hers, her husband's) and the book, in
  the order found; the cards under them, faint until held; the first tangerine and each card fly to their
  places (`src/hud.js`, `tools/build_hud.py`). The books' total there is 10 until 2.2 (`BOOKS` in `src/hud.js`).
- **Her husband in the game (new, 2026-11-20):** his character from his photo is made and approved
  (`assets/source/hud/husband/`, PixelLab `a1ebd48e-3b9f-40fd-b2d8-e737d4981bba`: his pyjamas with the bear, at
  the table and in the cabin); still to do: his clips (seated at the table: `idle`, `wave`, `laugh`, `eat`;
  waiting in cabin 8206), shown to the user first, then he replaces the stand-in (`husband` in `tools/cast.py`).
  **Begun 2026-11-22:** one row of his forehead out (as his icon), his character imported so; **seated at his table
  (`idle`), in the stand-in's place**, in the Great Outdoors' new patio chair (its near arm in front of him, his far leg
  behind the table); the Great Outdoors' and the Garden Café's tables and chairs remade side-on and beige (what stands on
  them 3 px into the top). **In cabin 8206** (the user's): on the sofa under the window, behind the bed, facing us, in his
  own front view ("my lower body isn't visible anyway"), the bed drawn again over him. **Done 2026-11-23:** his `wave`,
  `laugh`, `give` (his book from his fist) and `eat` (a soft serve), seated; Bumbusik sits down across from him in the
  patio chair with her cone, eats it (his cone's look, her own face held) and gets up after the book; he gives
  *Atomic Habits* (book 1; book 6 to the Atrium Café's table, then the shore excursions' brochure stand); their photo from La Cucina (the user's) on La Cucina's
  wall (`slot_cucina`), no longer on his table; the crates moved off the cone's way (232.8 m).

### 2.5 The `keeps` playtest (medium; no art) — **done 2026-11-23**

New: each of his places empty before the table scene and holding its thing after; each thing on
the cabin's desk once found; each count appearing with its first find. With it `region2` (the
cover on the first pick-up, closed by a key; the shelf's close view with one book back and
thirteen gaps), and each region's scenario where something is placed or a book is taken (the
cover closed before it goes on).

**Built 2026-11-23:** `python tools/playtest.py keeps`, one game with the close-ups shown: nothing counted at the start;
the wool, her flag, book 6 and his t-shirt each shown close, its count off while it shows and on once a key closes it,
in the order found; a second find (the feather) and a book given (9) up by one only once closed; his four places empty
before the table scene and each holding its thing after (by the story: the sleep mask's balcony draws its things only
while she is out there); the desk seen close with two found and all eight, Bumbot's bed with two and all eight, each
found thing's box differing from the bare picture and the rest bare. The other scenarios keep skipping the close-ups
(`region2` shows book 2's cover); the shelf's close view went with 2.3.4. Found on the way: **a book's count went up
under its cover**; it now waits for the cover to close (`world.take`, `giveBook`, `cover(n, then)`). **Book 6 moved**
(the user: its pulse hardly showed at the Atrium Café's table, her body in front of it) into the shore excursions'
brochure stand at 134 m, the bottom row's middle pocket, its foot behind the pocket's lip (`cover`).

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
| 4 | ~~Deck 9, the officers' corridor's forward end, the front windows~~ **Deck 12, the Spinnaker's balcony** (§7f, P2: she drawn in front of its glass) | Forward over the bow, from the top of the ship |
| 5 | Deck 11, the Great Outdoors, the stern rail | Down and aft over the wake; at sunset the sun's path |

- **The Stardust's first, shown to the user running** (motion is judged by eye), then the other
  four. A porthole piece and a window piece, generated.
- `Lookout` in `src/world/movers.js`, `LOOKOUTS` in the data, the camera in the ship scene (the
  intro's camera work is the model); a case each in the regions' scenarios.
- Spot 1 is where the diary lies (2.1): look at it with both in place. (Spot 5 had his spoon until the t-shirt took
  thing 13 to deck 12, 2026-11-21.)
  (Spot 4 was book 14's end too until it moved to the Spinnaker's balcony, §7f.)

### 3.2 The deliveries (large; about 10 generations)

A delivery waits at a hallway's pantry end once its fire door has been opened; a tray with a
cabin's number on its tag, carried under tray rules; a hand takes it at the door, with a `♥`.

| # | Hallway | Load | Its rule | Pays |
|---|---|---|---|---|
| 1 | Deck 8 midships | Flowers in a tall vase | It stands in front of her face: she sees the hallway through the stems | Book 12 (Poczwarka) |
| 2 | Deck 10 midships | A pot of tea | It cools (the HUD's meter, as the coffee) | Book 13 (Daughters of Warsaw) |
| 3 | Deck 9 aft, **to the last cabin, about 246 m** (§7f, P4) | A stack of pillows | Light: a full jump allowed, but the top one slides off if she stops short | A thank-you only |

- `LOADS` in `src/world/carry.js`; a source at each pantry end `when` its door is opened; the
  door that takes it. With a delivery in her hands a hit is a spill, as with any tray,
  **tangerines on her or not** (1.2a, 2026-11-19: no tangerine saves a tray).
- The loads are generated; where a load hides her or changes how she stands (the vase before
  her face, the pillows in both arms), her with it is one generated clip.
- The plan's own warning: three deliveries are one kind of errand with three loads and three
  rules, "the closest the plan comes to the line" of nothing twice. Each must feel its own.
  (The rule itself was dropped by the user on 2026-11-21, §7f; that each load feels its own still holds.)
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
- ~~**"Standing still with a book she reads where she stands"** (`GAME_DESIGN.md` §6.1.2) has no
  code: she reads only in the chair and on her bed. Her reading clips exist.~~ **Dropped 2026-11-22** (the user).
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

**Built 2026-11-20 by the Refinement session, on branch `refinement` (`4eb23d8` the intro's sky,
`504be54` the sunset's); the building session skips this part** (the user's word, 2026-11-20). What
the user chose, and how, is in `docs/refinement-log.md`: mock-up B3 of the intro's sky (generated soft
clouds, a soft sun with god rays worked out from the clouds, nothing under the sun, the path of light
flickering glint by glint), and its reach to the game's far clouds and the sunset (S2: the sky blended,
clouds lit by the low sun, their edges smoothed). The art: `tools/build_sky.py`. The steps below are as
they were planned.

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

## 7c. Part 8: what she can use, does it stand out? (small to medium; added 2026-11-19) **BUILT 2026-11-23 by the Refinement session**

**Built** (`src/highlight.js`; `docs/refinement-log.md` on `refinement` has the steps): the user looked at every thing
she can use (213, on sheets) and chose a mechanic over a colour rule: while she stands where E would act, the thing
pulses between its own colours and the other state, full-colour things down to the props' wash, muted pieces up to
their full twin (the soft serve machine, the jackpot pair, the hot tub and the rest of the nine below, the massage
tables, the piano, the odd book's bookcase); people never. The casino's slot machines are washed 12%. Then **doors as
secrets**: every door she can use washed at rest like the background doors beside it, the pulse revealing it; the
lifts, the glass doors across the deck and the balconies' doors left as they are (the balconies' doors are the user's
next point: "they don't look like doors at all"). `CLAUDE.md`'s table and rules have it. Not done: the nook's armchair
and the funnel's horn, drawn inside larger pictures, do not pulse.

What follows is the plan as written before it was built.


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
| 11 | `tan_8_fwd` | A bare table alone in a cabin corridor, one tangerine on it | ~~Prop A~~ **It moves to a table on deck 8's forward terrace** (§7f, P5). (Also moved by §7f: `tan_9_aft` to about 246 m on prop A, P4; `tan_7_splash` with its snack table behind the pillow fort, P6) |
| 12 | `tan_9_luggage` | The same, behind the luggage stack | Prop A |

Small shifts, no art: `tan_6_windjammer` and `tan_12_spinnaker` lie on the barkeeper's hands and chest (along the
counter, clear of them); `tan_8_8206`'s two lie loose on the desk, one over a dark object (the plan's "welcome basket":
prop B there). (**2026-11-22, the user:** moved onto the desk's top, right of the phone; they stay on the day after if
not picked up; the bowl may still come with prop B.) Everything else was looked at and is right as it is.

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

## 7f. Part 11: the empty stretches: sixteen obstacles, and a purpose for every end (large; about 80 generations, a guess; added 2026-11-21)

The user, 2026-11-21: "Let's focus on the long corridors that are still underpopulated with obstacles. I want a
proposal of how we would fill the empty stretches with playable obstacles by reusing the current ones (in a smart way,
so that they aren't repeated one after the other), and maybe adding a few new ones." On the proposal of ten: "All of
them". On deck 4's aft checkpoint, which §7e removes and which two of the ten would give a use: "As decided" (it goes).
On the old rule "No person, hazard, errand or reward is used twice" (2026-11-10): **"Drop the rule, it is no longer
relevant, we are doing refinements manually now."**

**What was measured** (from `maps/world.json`, the map and the running game; only what can catch her or must be got
past was counted, not people to look at, checkpoints or things to find):

- **Regions 1 to 3 are the thin part of the main way.** Deck 4 from the climb (145 m) to the stern: 109 m with three
  standing carts. Deck 5 from the forward stairs to the stern: 182 m with the waiter alone, who matters only with a
  tray. Deck 6 inside from the forward cabins to the stage: 184 m with nothing that can catch her.
- **The best gags sit off the main way:** the suitcase, both paper rounds and the breakfast trolley in the forward
  cabins of decks 4 and 5, which the lunch errand never crosses; her tray ride and the "Do Not Disturb" gag in the
  optional hallways; the steam in the optional spa.
- **From region 4 on the game is dense enough**, but for the gym (49 m with the pool's start), the sun deck once the
  old lady has gone, the officers' corridors and the boat walkway (131 m with the drill alone).

**How the ten were chosen** (the design session's own three rules for bringing a thing back; they stand in place of
the dropped rule for this part, and later refinements are the user's, by hand):

1. Never the same thing as the last one she met, counted along her way, across the stairs too.
2. Neighbours never ask for the same move. The moves: hop a thing that stands, hop a thing that moves, time a pulse,
   stop for a tell, get past someone walking.
3. A thing comes back changed in one way: a new partner, a new state of hers (a tray, the cake), or a place that
   gives it a reason.

Every hazard is a class built from a line of data (`tools/population.py`, `src/world/*.js`), so a thing placed anew is
a line, a look and a test, unless said otherwise below. Metres are "about": **each is set against what is built there
first** (the lesson of 2026-11-14), looked at enlarged beside her, and shown to the user before it is tested.

| # | Where | What | From | What is changed, and what the build needs |
|---|---|---|---|---|
| 1 | Deck 4, about 169.6 m, midway between two cabin doors | **The towel stack** (`STACKS`, gag 18) | Deck 9 | Alone here, as the lesson (stop short, it falls in front of her); deck 9 keeps it with the darting vacuum. It stays fallen, as there. Look at the wall behind it (a picture was hidden on deck 9) and at the extinguisher at 173.5 m |
| 2 | Deck 4, 225.5 to 239 m | **A second vacuum** (the map's `vacuum`, gag 5) | Deck 4 midships | It patrols the pocket with the stage manager's door (232.5 m): "the vacuum on deck 4 is the test" for the pills (`GAME_DESIGN.md` §6.1.3, region 3), which the first one, at 118 to 143 m, never was. It turns short of the trunk's door (240.6 m), so that stepping out of the trunk is never a hit. The cart at 220 m and the prop cart at 224 m bound its forward end: see that it stops short of them |
| 3 | Deck 5, Shore excursions, 126.5 to 136.5 m | **A second runaway suitcase** (`ROLLERS`, gags 6a to 6c) | Deck 4 forward | Between the trunk's door (124.9 m) and the reservations desk (137.5 m, her flag at 140.7 m), clear of both. The first time it is met with the lunch in her hands. **Measure first whether a tray's low hop clears it:** if not, the lunch by deck 5 has no way past and the lane is cut so that it leaves her a gap, or the user is told |
| 4 | Deck 5, the Seven Seas, three lots between 214 and 240 m | **Plates and trays Bumbot knocked down** (`TRAYS`, gag 3: she rides one off) | Decks 8 and 10 | ~~There only from near-catch 1 (`flag:bb1`: his way forward out of the restaurant)~~ **There from the start** (the second round, below: her first walk in had nothing; his mess on his way in to the lunch) until the lunch is delivered. **The user was asked whether a trail of his mess reads as a hint to the cat** and let it stand ("Write it"); if in play it does read so, back to `flag:bb1`. No door behind them (`Trays.door()` may be nothing already). Each lot under two metres, between the tables, clear of the three tangerines that roll from the bowl. With the lunch in her hands a hop clears them; landed on, a spill and the pass again. Needs: `until` on a `TRAYS` entry |
| 5 | Deck 6, Bliss, about 113.2 to 114.8 m | **The DJ's fog machine: a puff every few seconds** (`Steam`, gag 17) | The sauna | Region 2's first timed obstacle, the DJ at his booth (`amb_dj`) its cause. Clear by a metre and a half of the promenade door (111 m), the dance floor's spot (117.2 m, where she stands still three seconds) and the trunk's door (118 m). Needs: a second steam in the data (`bow.steam` is one today); **a small fog machine on the floor, generated (1 or 2), as what it comes out of**, the sauna's hiss and wisps as its tell; drawn only while she is on deck 6 (the lesson of 2026-11-20 on effects seen through the hull) |
| 6 | The boat walkway, about 160 and 181 m | **Two gulls on its rail, and the balconies' gusts reaching down to it** (`PERCH`, gag 20; `GUSTS`) | The balconies | The second sits five metres from the boat drill (186 m): waiting out the boat is what a gull punishes. Needs: a perch at the walkway's rail (the data takes balcony decks today); the gusts' band down to the walkway's floor; **a tell that can be seen there** (the balconies' is their towels: the boats' covers or the drill's rope flapping, a line drawn in code) |
| 7 | Deck 12, the sun deck, 112 to 144 m | **Gusts** (`Gusts`, as `TERRACE`) | The aft terrace | The jump over the old lady's sunbed (128.5 m) must be timed; after the horn a gust rocks the cake unless she stands still. Two towels on the sunbeds and the palm (114 m) as the tell. Needs: `SWAY` in `src/world/carry.js` given a `gust` (moving in one adds to the wobble; standing still adds nothing), to be tuned in play; only while she is on deck 12 |
| 8 | Deck 11, the gym, 91 to 96 m | **A gym ball rolling with the ship** (`ROLLERS` with a picture of its own) | The suitcase's code | New picture: a gym ball about 30 px, generated (about 5 with tries), turned as it rolls. Between the socks' rack (89.2 m) and the bench (97.1 m). Its hit is a scenario of its own (`MISHAPS.gymball`): "Bumped", the built sit-down, no ride, until a gag is wanted |
| 9 | Deck 10, the officers' corridor, about 52 to 56 m, a cabin door's slot | **The night watch asleep: a "Do Not Disturb" door with his tray outside** (`DND`, `TRAYS`, gags 23 and 3) | Decks 8 to 10 | Both gags on the way to the bridge. Needs one person, an officer in pyjamas, a sleep mask pushed up (a pro character in the cast's style, the drill's officer; about 15 with what the other `dnd_*` people have). Clear of the officer's walk (`amb_officer_10`, about 60 m) and of the cabin door `cp_officer` gives back (§7e) |
| 10 | Deck 7, the Art Gallery, 132 to 148 m | **New: two handlers carrying a large framed painting to and fro** | None | Region 3's one walker. They carry it along her lane and set it against the wall at each end for a few seconds, wiping their brows: then the way is free. Her cry sets it down at once. Run into while they walk: **she goes through the canvas**, head and arms out of the picture, the frame round her; she staggers and sits; they look at each other. Then her checkpoint; they fetch another. About 50 generations, a guess (the two with the painting made together, their walk, setting down and picking up, their look; her gag). **Built last, a plain version first:** a rough of the shot over a real screenshot and the walk with stand-in art are shown to the user before any art is made (the intro's lesson) |

**The moves in the order she meets them, where two or more stand on one walk:** deck 4 going aft: the lead (hop), the
first vacuum (moving), the towels (stop), the cart (hop), the stairs, the second vacuum (moving). Deck 5 going aft:
the suitcase (moving), the waiter (walker), the plates (hop).

**Where a hit sends her back, with §7e's nineteen** (the user: "As decided"; no checkpoint is added or kept for these):

- 1 and 2: the gangway's door (72 m), about 100 and 155 m back, past the dog and the first vacuum; from region 4 the
  laundry's door (112 m). In region 3 a hit by the second vacuum is the long walk aft again with the pills. This is
  the cost the user took.
- 3: the gangway's door, a deck down and up the forward stairs, about 65 m; once it is lit, the Library's.
- 4: with the lunch in her hands, a spill and the pass, at most 35 m; without, the gangway.
- 5: the Library's door (45 m) once she has been there; before, the gangway, two decks down.
- 6: as the drill's hit today; with a tangerine on her the gull takes one and she keeps her place.
- 7: no hit; a cake gone over is fetched again at Cagney's.
- 8: the gym's door, ten metres.
- 9: the gym's door a deck up by the forward stairs; once lit, the bridge's.
- 10: the Arcade's door (189 m), which she has passed on her way from the balcony.

### The second round: every long run its obstacles, every end its purpose (the user, 2026-11-21)

Asked next to check the ends of all the long corridors ("whether reaching every end benefits the player. Whether it is
part of a route that must be taken, or whether the end holds something else valuable"), the design session found
eleven ends that held nothing and proposed leaving most. The user: **"First of all, your plan has to account for
already planned things that are not built yet. Plan with them in mind, like they are in the game. Second of all, I do
not agree leaving empty ends. Every long corridor run has to have obstacles (you already planned it) and a purpose."**
On the adjusted plan: "Write it".

**Counted as in the game:** the ten above, the five look-outs (§5 3.1), his four things and books 11 to 14 (§4 2.1),
the three deliveries (§5 3.2), the tangerines' seats (§7d), the nineteen checkpoints (§7e). A run is a walk of thirty
metres or more between stairs or to an end.

**Six runs still had no obstacle:**

| # | Where | What | From | What the build needs |
|---|---|---|---|---|
| 11 | Deck 6, the Photo Gallery, 150 to 159 m | **A crowd shuffling along the photo wall**, looking for their pictures: bodies to hop at the gaps (`QUEUES`) | The buffet queue | Three or four of the queue's own people (the same passengers, a day earlier; no art). No trays in their hands if their clips allow it: look. They hold her back and never hit; a hop at a gap |
| 12 | Deck 6, the theatre's aisle, about 224 to 229 m | **Popcorn spilled now and then by the man with the tub** (`amb_audience_3`, 226.5 m): a slip (`Spill`, scenario 1) | The casino's chips | `Spill` with the chips' colours changed and its tell from him, not a machine's lights (a rustle and his tub tipping: a clip of his, about 3 generations, shown first). Standing still or hopped, nothing, as the chips |
| 13 | Deck 7, the Stardust balcony, about 225 m | **A second lamp of the stage's rig, swinging over the aisle** after near-catch 3 (`LIGHTS`, gags 12a and 12b) | The stage's light | A line of data with `flag:bb3`; out of step with the stage's. Clear of the seats' people and of the diary's seat (242.2 m); what it hangs from looked at |
| 14 | Deck 8 forward, 70 to 73 m, by the party cabin's door (72 m) | **New, small: the birthday party's balloons drifted across the corridor.** She wades through them, slowed, they bob aside and one may pop; no fright | None | A few balloons, generated (about 3); a small class (they are pushed by her, bob back, slow her while she is among them, as the ball pit does). **Gone by the evening of the catch** (`until flag:catch`): the walk home with Bumbot is not slowed. Deck 8 forward was agreed calm ("no hazards, no people"): it has no fright still |
| 15 | Deck 9 forward, 30 to 70 m | **A second delivery robot, bringing the officers' coffee**: it stops and beeps in her way, she rides on its top (`ROBOTS`) | Deck 6 forward | A line of data. It turns short of the gold door (74 m) and of the corridor's end, where book 14 and the captain's door are; clear of the officer's walk (`amb_officer_9`) |
| 16 | Deck 12, the kids' pool, about 60 m | **A stack of pool towels** (`STACKS`, gag 18) | Decks 4 and 9 | A line of data; on the open deck, clear of the slide (62.3 m) and the pool's rims; it stays fallen. Drawn only while she is on deck 12 |

**Six ends still had no purpose:**

| # | The end | Its purpose now | What the build needs |
|---|---|---|---|
| P1 | The promenade aft of its last door (186 m): 45 m with the jogger's turn and a gull | **A ladder at about 210 m up to the boat walkway beyond the drill, its gate unlatched only from above:** once she has passed the drill, it is the way round it (the user's own test for a ladder, 2026-11-15: "a smart shortcut ... opened once that path is complete at least once"; `docs/plan-three-uses.md` §4.6 had found no place for one). **The last 19 m (212 to 231 m), where she is hidden behind the ship's side (the audit's V5), are chained off** | The gate's ladder again (`ladders`, a lock that opens from the top); a chain or rope across at 212 m, the jogger's turn and the lane's sign (213.6 m) kept clear. The forward enclosed end stays (11 m past its door) |
| P2 | Deck 12, the Spinnaker's balcony (31 to 44 m) | **Look-out 4 moves here from deck 9's corridor end:** forward over the bow from the top of the ship. Deck 9's end keeps book 14 and the captain's door | §5 3.1's row 4. **She must be seen there** (the audit's V4: she is a pale figure cut off at the thighs behind the windscreen's glass): she and the balcony's things drawn in front of the glass |
| P3 | Deck 10's balcony row, its forward end (62.9 m) | **His sleep mask** (§4 2.1, 14: "the far balcony") on the first balcony's sunbed. Deck 9's forward balconies are then the climb between deck 8's photo slot (74.9 m) and it | The place of a thing not yet placed. **Built 2026-11-21** (§4 2.1, 14) |
| P4 | Deck 9 aft, the last 19 m | **Its tangerine (`tan_9_aft`) moves from 230 m to the last cabin door, about 246 m**, on §7d's tray on a stand; **the pillow delivery (§5 3.2, 3) ends at that cabin** | Two lines of data; the cart at 230 m stays as an obstacle |
| P5 | Deck 8 forward, past her cabin (21 to 41 m, and the forward terrace) | **Its tangerine (`tan_8_fwd`, §7d's 11) moves from 49.3 m to a table on the forward terrace** | A table for it out there (a balcony table is a seat §7d allows); looked at with the terrace's stairs and U11 in mind |
| P6 | Deck 7, behind the pillow fort (21.4 to 31 m): a crawl to a shut door | **Splash Academy's snack table and its tangerine (`tan_7_splash`) move there from 41.2 m**, to about 27 m, by the counsellor | The table and the tangerine moved, clear of the counsellor (30.1 m) and of the mooring deck's door; the way home after the catch not blocked |

**Three tangerines move; the number stays 56** (§12 had "leave their number and their location unchanged": the user
saw the three moves and wrote "Write it").

**Ends that needed no change:** the walkway's forward end (its end wall, 100.2 m, is the climb straight up to deck 8's
balcony with the tangerine) and its aft end (book 11, and the climb to deck 8 aft's ajar door); deck 10 aft (the
guest's door is 11 m from the end); deck 4 aft, the Great Outdoors' stern, the Stardust balcony and deck 5 forward
(a look-out each, three with a thing to find); deck 8 aft (its tangerine 5 m from the end); Magnum's and the two
restaurants behind the flares (inside runs that have obstacles and lead on; the piñata is there).

**What this overrides:** the list "left empty by choice" (`docs/plan-three-uses.md` §4.6: the aft ends of decks 9 and
10, Magnum's, the Spinnaker's balcony, behind the flares) is gone, and §8's line on it with it; deck 8 forward is no
longer bare; U10 (V4 and V5, "Leave as they are for now") is answered for the Spinnaker's balcony (she is drawn in
front of the glass) and for the promenade's aft end (closed off); the first round's "left alone" below.

~~**Left alone:** by the user's earlier word Magnum's, the aft ends of decks 9 and 10, the Spinnaker's balcony, behind
the flares, and deck 8 forward (home); by the design session's judgment the Library, the theatre's aisle before the
stage's scene, deck 9's officers' corridor and deck 6's forward cabins, where the robot's ride is the play.~~ (The
first round's; the second round fills them, but for the Library, which lies inside deck 6's run with the fog and the
crowd, and deck 6's forward cabins, where the robot is the obstacle.) No more sprinklers, swinging doors or standing
carts: there are five, six and nine.

**The order:** 1 to 7, then 8, then 9; then 11 to 13, 15, 16 and P3 to P6 (lines of data); then P2, P1, 14; 10 last.
If the date presses, what is unbuilt is said to the user; the design session would drop the balloons (14) and the
ladder (P1) first.

**Tests:** a case in `mishaps` for each new thing that can hit her (the stack, the second vacuum, the second
suitcase, the plates, the fog, a walkway gull, the gym ball, the night watch's door and tray, the painting), each with
none on her and with two; `deck4`, `vacuum`, `region1` (the lunch carried by deck 4 and by deck 5 must still be
possible), `region2` (Bliss), `region3` (the pills, the gallery), `region6` (the gym), `region7` (the walkway),
`region8` and `region9` (the sun deck: the old lady's jump, the cake), `pocket`, `boot`; a start place for each new
spot (`docs/start-links.md`). `tools/check_overlaps.py` lists nothing; `tools/check_corridors.py`'s numbers given
(today, the longest walk with nothing to do: deck 4 29.6 m, 5 55.2, 6 68.3, 7 82.1, 8 40.1, 9 64.6, 10 56.4, 11
47.4, 12 44.0). **For the second round:** `mishaps` cases for the popcorn, the balcony's lamp and the pool's towel
stack; `region2` (the gallery's crowd; the ladder's gate from below and from above), `region3` (the aisle, the
balcony), `region5` (the balloons; the terrace's tangerine), `region7` (the mask; deck 9 aft's tangerine and the
pillows' cabin), `region9` (the robot, the towels, the look-out on the Spinnaker's balcony, the snack table behind the
fort), `finale` (the walk home: no balloons, the fort's place), the scenarios that pick the three tangerines up by id.

**The documents:** `GAME_DESIGN.md` §5.8, §6.1.2 (the rule is marked dropped there, 2026-11-21), §6.1.3's "Hazards"
lines and §6.1.7's table as each is built; `docs/population.md` §2.9, each deck's rows and §4's rules;
`CLAUDE.md`'s table for a new class or option.

**The date:** the design session's guess is about three working days for the first ten (1 to 7 about one, 8 a few
hours, 9 half a day, 10 one) and about two for the second round: five in all. Parts 9 and 10 had taken two of the
roughly five spare days before the 23rd of December; this takes the rest and about two more: the likely end near the
25th, the slow end at New Year's Eve. The user was told before each choice.

The audit's map and panoramas were made by scripts outside the repo (the obstacles' places from `maps/world.json` and
the map; each stretch shot tile by tile through `playtest.Browser`, a deck cut open by `viewOverride`); not kept.

## 7g. Part 12: "Washie, washie, happy, happy!" (medium; about 25 to 30 generations, a guess; added 2026-11-21)

The user, 2026-11-21: "In the dining area on deck 11, there was a crew member guy, who was standing at the entrance to
the dining area from the elevators and offering to sanitize the hands of the visitors. He was singing comedically:
'Washie, washie, happy, happy!' That's our inside meme. Suggest a fun way to add this meme into the game: placement,
looks, maybe some mechanics around him." On the design session's five pieces: **"All five."** On his look: "His was an
Asian crew member, maybe Philippine guy. Happy face, black hair. Standard waiter crew uniform." On the duet: "When they
both do the song, they should both do 'Washie, washie, happy, happy!'" On a melody: "No tune, he was just singing those
words."

**The idea:** he is the one person on the ship nobody gets past with dry hands, the cat included, and his song stays
in her head. He is not an obstacle: he never hits her, has no gag, and is not counted among part 11's.

**Where.** Deck 11, inside, where the Garden Café (160 to 194 m) opens into the aft lift lobby: his real place. About
193.2 m, on the free piece of white wall between the checkpoint's door (`cp_garden`, 192 m; §7e leaves the door
there) and the lobby's pillar (194 m), a sanitizer stand beside him on the pillar's side. He turns to whoever comes. If
he and the stand crowd the door (`tools/check_overlaps.py`), he goes to the lobby's side of the pillar, about 194.8 m,
and the painting there moves. She first reaches him from the pool side, after the kid's jet (a dodge) and the buffet
queue (a hop), 22 m before her husband's table, her hands free.

**His look.** The user's words above, and nothing from a photo. A pro character in the cast's style (the drill's
officer as the style reference, size 64, side view): short black hair, a wide happy smile, a small spray bottle held
up in one hand like a microphone. **His uniform is the real ship's waiters', not the game's waiter's.** The design
session first wrote the cast's `waiter` (a white jacket, black trousers) as the model; the user, 2026-11-21: "No, that
uniform doesn't match. Don't reference him." So the cast's `waiter` is not his model, in look or as a style reference.
What the real uniform is, is not settled: a web search and the user's photo of the café (no crew in it) did not show
it, and one careers site's line (a white long-sleeved shirt, black trousers, a yellow tie) is unconfirmed. **It is
decided with the user at the build** (the user, 2026-11-21: "We'll decide on the uniform look when building"): the
building session asks before his character is generated and shows the tries as always. `python tools/check_people.py --heads washie` before any clip. His clips: `sing` (his loop: he sways from
foot to foot and sings into the bottle), `squirt` (the arm out, two squeezes), `wiggle` (the duet's "happy, happy"),
`wash` (he catches a tangerine, squirts it, polishes it on his sleeve and tosses it: the fruit in his fist until the
frame the hand opens, then the game's). Hers: one clip, facing him: her hands held out, rubbed, then the same wiggle
(skeleton-v3 from her character; `tools/build_heads.py` after her sheet is rebuilt). The squirt itself is drawn by the
game, two fine puffs, as the kid's jet is.

**The five pieces.**

1. **The first meeting cannot be missed.** The first time she comes within about 1.5 m of him with free hands, he
   steps out with the bottle and she stops, for about three seconds and no longer: her hands out, his squirt, she rubs
   them, and both wiggle, **each with the whole line over the head: "Washie, washie, happy, happy!"** (the user). Her
   hands sparkle a moment (the pickups' glint). Flag `washie`, kept in the save. Before she is that near, and ever
   after, he sings alone as she comes within about 4 m: "Washie, washie!", then "Happy, happy!", on his clip's beats.
2. **After that he never holds her.** He sings as she passes, once a pass. Stopping beside him with free hands (or E)
   plays the duet again, and any move key ends it at once. **With her hands full** (a tray, the cone, the canister,
   the coffee, Bumbot in her arms) he sings and waves her through and no scene starts: the cone's 45 s and the
   coffee's 50 s are untouched.
3. **The cat paid too.** From near-catch 5 (`bb5`) until she has eaten with her husband (`table`): a few wet paw
   prints on the floor up to his spot from forward (about 3 m), and past him about 4 m of foamy ones, small heaps of
   suds that glint now and then. No words. **These prints are built here:** the population spec's `sec_pawprints`
   (wet prints from the pool at 131 m aft to the machine at 213 m) was never built and is in no part of this plan;
   the design session told the user they "already run past this spot", wrongly, from the spec. Only the stretch by
   him is built. The whole trail stays the user's to ask for: 82 m of prints leading aft could read as "go there".
4. **A tangerine thrown to him comes back washed.** Everyone else eats it. He takes one that reaches him (thrown, or
   lying within his reach: `people.offered`, `loose.claim`), plays `wash`, and tosses it back to her
   (`world.tossOver`), glinting as it flies; her count is as before. If she has left the café's end by then, it is
   set rolling on the floor toward where she went, a loose tangerine like any other. From how far a lob and a throw
   in a jump reach him is measured by a sweep and said to the user.
5. **The song stays in her head.** Once `washie` is set, about one of her idles in four anywhere on the ship comes
   with a small speech popup over her: "♪ washie, washie…". Never while she carries something, holds Bumbot, or in a
   scene (her idles do not play then anyway).

**Left out on purpose** (said to the user with the proposal): his squirt is nothing to dodge (the kid's jet 40 m
before is that already); the buffet's fruit is not locked behind clean hands (she passes the fruit before she meets
him).

**Texts** (`src/lang.js`, the same words in both languages, as her «Кісюнічка!!!»: it is their joke as it was sung;
the design session's proposal, the user did not object): `washie.a` "Washie, washie!", `washie.b` "Happy, happy!",
`washie.all` "Washie, washie, happy, happy!", `washie.hum` "♪ washie, washie…". If the popups' lettering has no ♪, it
is drawn in its stroke, as × and ∞ were for the HUD. **The duet's two popups stand 30 to 40 px apart and each line is
wider than that:** how they sit (the line broken in two, one higher than the other) is mocked up over a real shot of
the spot and shown to the user first.

**Sound.** No melody is made for the song (the user: "No tune"): the words are the popups. One new effect, the
squirt's two puffs (the design session's addition; the user hears it on the soundboard before it stays).

**Art, about 25 to 30 generations** (a guess): his character 10; `sing`, `squirt`, `wiggle` about 3 each; `wash`
about 5; her clip 2 to 4; the stand 1 or 2 (the atlas has a `sanitizer` of 12 x 26 px that was never placed: looked at
beside her first); the heads' estimates about 2. The prints are a few px each: made at their size by hand, wet and
foamy, and shown enlarged on the café's and the lobby's real floors (the lobby's is patterned blue). Everything shown
to the user in the chat before it is placed, the clips composed over a real shot of the spot.

**Open for the build:** his uniform (the user's description, above); where exactly he and the stand fit (above); whether the foamy prints read on the lobby's
floor; the duet's two popups; that the first meeting's stop does not start while she is in the air or sliding.

**Tests:** a case `region6.washie`: the first coming with free hands plays the scene, sets `washie`, and she can move
again within 3.5 s; the second coming does not hold her; with the cone in her hand no scene starts and her speed
across 190 to 196 m is unchanged; a tangerine thrown to him comes back and the count is the same; the prints are there
with `bb5` and gone with `table`; the hum shows only after `washie` (the idles' draw seeded). `region6` whole (the
cone's run to the kid, the canister), `lang`, `boot`; `python tools/shoot_people.py washie`;
`tools/check_overlaps.py` lists nothing. The start place `?at=buffet` is 23 m forward of him.

**The documents, as it is built:** `docs/population.md` (deck 11's rows; `sec_pawprints` marked as built only by
him), `GAME_DESIGN.md` §6.1's region 6, `CLAUDE.md`'s row for `src/world/lido.js`, `tools/cast.py`.

**When, and the date.** About a day and a half by the design session's guess (him and pieces 1 and 2 a day; 3 to 5
half a day). Part 11 had used the spare days, so this moves the likely end from near the 25th of December to about
the 27th, and the slow end past New Year's Eve unless something gives. The user was told before choosing. **He is
built before part 11's P2, P1, 14 and 10,** and if the date presses, the balloons (14) and the ladder (P1) are dropped
before any of his five pieces (the design session's ranking, said to the user with the proposal: their own joke is
worth more to the gift than either).

## 7h. Part 13: the balconies' doors (small to medium; added 2026-11-23)

The user, 2026-11-23, shown the balconies while every other door she can use was made a secret (washed like its
neighbours, revealed by the pulse, `src/highlight.js`): "Leave them as they are, but they don't look like doors at all.
When we're done with this update, remind me to work on the balcony doors."

- **What there is:** five balconies whose cabin she enters from outside (`balcabin8m`, `balcabin8a`, `balcabin9`,
  `balcabin9a`, `guest10`: rooms with a `balcony` door in `tools/population.py`). From the balcony the way in is
  `balcony-ajar`, drawn in code in `src/world/outside.js` (`make('balcony-ajar', 34, 98, ...)`: the glass slid aside on
  the lit cabin), with a curtain blowing out (`balcony-curtain`); the balconies round it show the ship's side, dark
  shut glass in its tiles, not doors. E there takes her in (the ship scene's `routeDoorAt`). Left out of the doors'
  wash at rest and still pulsing as a full-colour thing (`SKIP_DOORS` in `src/highlight.js`).
- **First, for the user:** the balcony and its neighbours as they are, and mock-ups of a balcony door that reads as one
  (by `CLAUDE.md`'s art rule a picture is generated, not drawn in code), composed over a real shot of the spot at the
  game's pixels; the user chooses. Then whether it is washed like what stands round it, as the other doors are.
- **Then:** the picture placed for all five (and its pairing with the cabin's own door picture inside, `Room.full`),
  `tools/check_overlaps.py`, the `highlight` playtest, and a look at each balcony in the running game.

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
  Bistro, four of the five balcony cabins. ~~Those left empty by choice stay so~~ (none is left empty: §7f's second round, 2026-11-21) (the aft ends of
  decks 9 and 10, Magnum's, the Spinnaker's balcony, behind the flares).

## 9. Waiting for the user

| # | What is owed | Then |
|---|---|---|
| U1 | A photo of her husband (or a description in words) | His own character and clips (sit with a cone, eat, wave, laugh, give, a pose for the cabin) in place of the stand-in |
| U2 | The pictures for five photo slots (the lifeboat, the lighting bridge, deck 8's first balcony, the chapel, ~~the table~~ La Cucina's wall: **done 2026-11-23**, the user's photo at La Cucina's window table, `assets/source/photos/cucina/`); "once the game is tested and verified" | Pixel art from a cutout, candidates shown; today a heart in a frame |
| U3 | The win screen's own message, in both languages | `WIN_MESSAGE` in `src/config.js` (empty) |
| U4 | The names on the crew doors (BOSUN, PURSER, DJ, STAGE MGR stand in) and on the captain's | Lines of data |
| U5 | Whether the chapel's wedding is anyone in particular; whether the rival has a name | As answered |
| U6 | **Their ears on the sound:** no record of any of it having been heard (about 130 effects, the ambience, and those added since: the lunge, the pocket, the dog, the papers, each gag's) | The soundboard, <http://localhost:8000/tools/soundboard.html>; changes as asked |
| U7 | Music, or none ("No music for now") | Only if wanted |
| U8 | The bridge and the spa hidden until she enters them (`LOCKED_PARTS`, off since 2026-11-08 "until we settle how the ship is split") | A switch and a look |
| U9 | Deck 7's stern strip: "maybe a secret place later"; today she can only leave it by jumping off | As decided |
| U10 | V4 and V5 of the audit: she is hard to see on the Spinnaker's balcony and at the promenade's enclosed ends ("Leave as they are for now") | Cut the side open there, or draw her in front of the glass |
| | **U10, 2026-11-21:** answered in part by §7f's second round: the Spinnaker's balcony gets look-out 4, she drawn in front of the glass; the promenade's aft enclosed end is chained off. The forward enclosed end stays as it is | |
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
