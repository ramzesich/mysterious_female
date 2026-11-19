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
| 1 (§3) | The mishaps' gags to their end, their playtest, two leftovers | `docs/plan-three-uses.md` step 4a | Large | About 80 generations |
| 2 (§4) | The rest of the twenty things to find; fourteen books with their covers; cabin 8206's desk | Step 5 and its revisions | Large | About 45, and the nook's photo |
| 3 (§5) | The look-outs; the deliveries | Step 6 | Large | About 15 |
| 4 (§6) | Each deck its own look | Step 7 | Medium | About 20 |
| 5 (§7) | Small faults and leftovers | The log, the audit | Small each | None |
| 6 (§7a) | Bumbot made again: his look, then every clip of his, richer and tuned (added 2026-11-19) | The user's word; `GAME_DESIGN.md` §4 | Large | About 90 (the design session's guess) |
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
  butterflies (the user's additions); `?at=stairway`. On the way, the funnel's
  stairway gone over (`docs/progress-decisions.md`): moved 12 px out, boarded by walking into it, a hold on
  the rail in a gust, gulls that dive straight from their flight, a tangerine carried in the beak.

### 1.2 The third batch: nine gags and two clips of others (large; about 55 generations)

| # | What hits her | The gag with no tangerine on her | Its code | Before any art |
|---|---|---|---|---|
| 7a | The deck chair, head on | "Face first onto it; it folds flat and she sledges on it across the tiles" | `WetPatch`, `hazards.js` | **Walk at it with real keys: can it still happen?** Since 7b the chair hardly rocks as she slides in past it. If it cannot, say so to the user and drop it |
| 9a | The jogger, head on, both running | "Twirled like a top, spirals over her head, she sits" | `haz_jogger`, `world.touched()` | |
| 9b | He runs into her, she standing | "Bowled back onto her bottom; he jogs on the spot, sorry" | The same | **His sorry on the spot** is a clip of his (where the two meet they are generated together) |
| 9c | He runs into her back | "Shoved into three flailing steps and a belly-flop" | The same | |
| 9d | She runs into his back | "She bounces off and sits (8d's clip); he never notices" | The same | No art: the built bounce is wired in |
| 11a | The kid's jet in her face | "Sat back, spluttering, wringing her hair; he points and laughs" | `src/world/lido.js` | **The kid's laugh** is a clip of his (his pistol is drawn into both hands in every pose) |
| 11b | The jet in her back | "As 10b: she arches, dances, squelches off" | The same | **A question for the user:** 10b's squirm was dropped ("looked weird, and the case is rare"), so 11b points at a clip that is gone. Propose: her arch as built and the run-off, no new clip |
| 12a | The stage's light, from the front | "Her head back, two spins on the spot, stars circling, she sits" | `SwingLight`, `movers.js` | |
| 12b | The same, from behind | "Three stumbling steps, down on her hands and knees, stars" | The same | |
| 14a | A basketball in her face | "She tips over backward, stiff as a skittle" | `Balls`, `topdeck.js` | |
| 14b | A basketball on the back of her head | "She topples forward, stiff as a plank" | The same | |
| 15 | The drill's boat, from above | "Pressed down to half her height, a waddle, she springs back up and sits" | `DrillBoat`, `outside.js` | |

- Shown to the user in batches, enlarged and numbered, each checked frame by frame first; one
  that will not read after two tries is shown with what could take its place.
- Without a gag by design, not to be made: 1 (the chips), 2 (the dog's lead), 10e (her own
  trip). 13b is not made (no swing door hits her from that side); `src/world/mishaps.js` still
  names it for a door hit from behind: check whether that can still be reached, and take the
  line out of `MISHAP_SCENES` only if it cannot.
- **Proposed, the user's word first:** her "bats the towels off" (18 with a tangerine on her;
  the reel stands in). 16's two small flaws were noted and left (her blouse greys one frame in
  two run-stops; her hair streams back at the sneeze's peak).

### 1.3 The `mishaps` playtest, the sounds, the start places (medium; no art)

- `mishaps`: a new scenario, a case for each scenario of §1.6 outside region 1 (the gag it asks
  for, her checkpoint after, the thing back in its place; with a tangerine the reaction and
  where the tangerine goes; the side told right). The gags built so far are checked inside
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

- **The four end walls with a one-way doorway** (decks 8, 9 and 10 aft, deck 11 forward): not
  looked at yet. Look, and propose to the user whether and how they show their free side
  (`end_walls()` in `tools/build_ship_map.py`, `buildBulkhead`, `assets/source/ship/pushbar/`).
- **A crew-door checkpoint just past deck 9's sprinkler:** proposed, "only if the stretch from
  `cp_9_arrive` to the steward with no tangerine proves harsh". The user judges it in play; if
  yes, one line of data.

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
| 5 | Bumbot's | Liquid snack in a tube | Deck 4, the dry store, on a shelf | E (green card) |
| 6 | Bumbot's | Massage gun | Deck 11, the gym, the bench by the weights | E |
| 7 | Bumbot's | Tin of sardines | The Sushi Bar | The chef's bubble shows a tangerine; he takes one for it (the apology's hand-over) |
| 8 | Bumbot's | Remote-controlled car | Deck 7, Entourage, past the ball pit | E |
| 10 | Hers | Bookmark with a cat on top | Deck 6, the maid's cabin, in the book by the bed | E |
| 11 | Hers | Diary notepad | Deck 7, the Stardust balcony's far end, on a seat | E (look-out 1 will be at the same end) |
| 12 | Hers | Small plant in a pot | Deck 9, the cabin being cleaned, its windowsill | E |
| 13 | His | Ice cream spoon | Deck 11, the Great Outdoors, the last table at the stern rail | E, after the table scene (look-out 5 will be at the same rail) |
| 14 | His | Sleep mask | Deck 10, the far balcony, on a sunbed | E, after the vaults |
| 15 | His | Handheld (black, four coloured buttons, no logo) | Deck 12, Champs, on a sofa | E |
| 16 | His | Guitar pick | Deck 12, the Spinnaker, the bandstand by the piano | E |
| 17 | Book 11 | נערה במעיל כחול | The boat walkway's end, beyond the boat drill | E |
| 20 | Book 14 | Pachinko | Deck 9 forward, the officers' corridor's end | E (look-out 4 will be at the same end) |

- His four are not there before the table scene ("not lying there before it, not merely
  locked"). Nothing of the twenty flies to its count. Books 12 and 13 (rows 18 and 19) are paid
  by part 3's deliveries.
- `tools/check_overlaps.py` must list nothing; `tools/check_corridors.py`'s numbers given at
  the end (the audit's C9: a reward every 25 to 30 m is measured only now).

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
  door that takes it. With a delivery in her hands a hit is a spill, as with any tray; with a
  tangerine on her the reaction follows §1.6.
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
| U16 | Fine placement of everything, and the numbers, in play: the cry and the lunge, the pocket's roll, how often she runs dry, each gag's length, the glide, the checkpoints' spacing | Her playtest and the user's |

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
  11a, 11b, 12a, 12b, 13b, 14a, 14b, 15, 21 to 24 (21 built since: `gag: 'stairs'`). `src/world/mishaps.js` still returns `13b`.
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
  of small pickups: decided against.
- The audit's I1, I5, I8, I11; V9 and V11 (choices, not faults); V1, V2, V3, V6, V7 (fixed).
- 13b, 4c, 10b's squirm, 7b's fold "shut on her" (the collapse was taken).
- The controller's mute (keyboard only). A whole suite before each merge ("The old rule").
- A gust carries her twice what its data says: known since region 7, every gust is tuned to it.
- After the sunset, the stairs to deck 8's forward terrace are a way round the glide: left in,
  "a crew member's shortcut".
- Two sessions building in workspaces of their own, each with half of this plan: set up on
  2026-11-18 and taken down the same day on the user's word ("too convoluted and hard to
  track"). One session builds; one designs.
