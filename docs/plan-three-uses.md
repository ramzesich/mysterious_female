# Plan: three uses for a tangerine, and decks worth walking

**Settled with the user on 2026-11-15: every design question below is answered (§8 has their
words). Nothing of it is built. The build starts at step 1 (§5).**

It follows `docs/brainstorm/dash-rework.md` (the "shout, throw, pocket" proposal) and
`docs/audit-2026-11-15.md` (findings C1 to C10; its visual faults were fixed separately,
`docs/plan-visual-fixes.md`).

## Start here (for whichever session builds it)

1. Read `CLAUDE.md` (the rules that are easy to break, "Looking closely", "Working with the
   user"), then this file. §1 to §4 say what is built, §5 how, step by step.
2. Make a branch off `main` (say `three-uses`). If another session is at work in the same
   folder, build in a git worktree of your own (`git worktree add <folder> -b three-uses main`)
   and never `git add -u` over files that are not yours.
3. Build one step at a time, in order. **After each step: pictures in the chat, the link
   (always with `&tangerines=infinite`, and `&pocket=off` when a fright is to be seen), the
   playtest scenarios that were run named and the rest said not to have been run, then stop for
   the user's review.** Commit once a step is approved; merge to `main` and push only on the
   user's word.
4. Standing rules that matter here: never the whole playtest suite unasked; every test browser
   muted (`tools/playtest.py`'s `Browser`); every generation's price stated and approved before
   it is spent; every picture shown to the user, enlarged, before it is placed; no hint popups
   and nothing that points to where something is; no person, hazard, errand or reward used
   twice; nothing floats; failures are "scares"; every text in `src/lang.js` in both languages;
   record each change of plan with its reason in `docs/progress-decisions.md`.
5. Everything placed is a line of data in `tools/population.py`. **The user will move things
   while play testing** ("I will fine tune it while play testing"): keep each placement one
   line, easy to move.
6. Numbers (speeds, reaches, times) are first guesses to be tuned by play, all in
   `src/config.js`.

Read from the code for this plan, so that the steps name real places:

- Every fright by contact goes through one function, `scareContact(fromX, kind)` in
  `src/scenes/ShipScene.js` (18 callers), and every spilled tray through `Carry.spill(fromX)` in
  `src/world/carry.js`. Falls and overboard have their own (`scareFall`, `scareOverboard`).
- The dash is `tryDash` / `isDashing` / `updateDash` in the ship scene, `DASH` in `src/config.js`;
  five places ask `isDashing()` (the breakables' collider in `world.js`, deck 4's vacuum in the
  ship scene, the darting vacuum and the towel stack in `movers.js`, the kid in `lido.js`).
- It is learned at near-catch 1 (`FLAG_GIVES = {"bb1": ["verb:dash"]}` in `tools/population.py`).
- People who walk already have "turned aside, she can slip past" (`aside` in
  `src/world/people.js`, the waiter at his tables).
- A fire door she has come through from its free side is open both ways for good (`passes()` in
  `src/progression.js`, `save.opened`).
- Her husband sits at the first table of the Great Outdoors (deck 11, about 220 m) from region
  6; the table scene is `tableScene` in `src/world/lido.js` and sets the flag `table`.
- PixelLab: 540 generations were left on 2026-11-15, until 2026-11-30.

---

## 1. The three uses

A tangerine can do three things, and one used well can come back.

### 1.1 D: the cry with the lunge, one tangerine (B on the controller)

- **Every D costs one tangerine**, whatever it does. With none on her: nothing happens, and the
  HUD's count blinks once.
- **The cry is to startle what is in her way.** "Кісюнічка!!!" in her bubble, her sound, and
  the people and animals within 4.5 m on her deck are startled for three seconds (§2, §3).
- **With it, once she has learned it (§1.4), the lunge:** one second at twice her speed (280 px a
  second, about six metres) the way she faces, the trail behind her. During it:
  - what the dash broke breaks (the five breakables), the vacuums spin, the towels topple;
  - **nothing can frighten her by contact**: a swinging door, a sprinkler, a basketball, the
    porter's cart: she is through. Each gives way in its own manner (§2);
  - **in the air it is a leap**: a jump taken in a lunge carries about 4.5 m against 2.3 m;
  - falls and the sea are what they are. Solid things stay solid (carts, the queue, walls, ropes).
- **With a tray in her hands, and before the lunge is learned: the cry alone, still one
  tangerine.** One rule, no exceptions.
- Not while she crawls, climbs, swims, or holds Bumbot.

`CRY = { reach: 4.5 m, startleMs: 3000, deafMs: 8000 }`, `LUNGE = { ms: 1000, speed: 2,
safeTailMs: 300 }`. The speed stays under Bumbot's 300 px a second.

### 1.2 F: the throw (Y on the controller), one tangerine

- **F: a roll.** Underarm, low; it bounces once and rolls about six metres, off steps and edges,
  and stops against anything solid.
- **↑ with F: a lob.** High and short (it tops out just under the ceiling, about 2.3 m ahead):
  for what is up on shelves, ledges, lamps and strings.
- **It is a real thing on the floor.** Whatever wants it takes it (§2). If nothing does, it lies
  where it stopped and is picked up by walking over it, today or next week (it is saved). Over
  the side it is gone, with a small splash. In a pool it floats.
- Not with a tray, crawling, climbing, swimming or holding Bumbot. No cursor: she aims by where
  she stands.

### 1.3 The pocket (automatic, on every hit), one tangerine

- A hit that would be a fright or a spilled tray, with a tangerine on her: she flinches (the
  `her-hit` clip, a third of a second), is pushed a step back, blinks for a second and a half
  during which nothing can touch her, **and keeps her place and her tray.**
- **The tangerine is knocked out of her pocket and rolls away fast**, the way she was pushed. It
  is the same real thing as a thrown one: she can run after it, and whatever wants it may get
  there first.
- With none on her, a hit is what it is today. Falls, the sea and a cake that wobbles over by her
  own feet are never forgiven.
- **Testing:** with `?tangerines=infinite` the pocket would forgive everything. `&pocket=off`
  switches it off; the playtests that check frights start with no tangerines, as they do now.

### 1.4 When she has each

**The throw and the pocket from her first tangerine; the cry from the start; the lunge from the
Seven Seas** (near-catch 1, where "she lunges with the scream"). §6.1.2's "learned, not given"
now speaks of the lunge.

### 1.5 The tangerines: 56

The 53 on the ship are not moved and none is added on the decks. **One addition, the user's
own: the bowl on her desk in the crew cabin on deck 3**, whose three painted tangerines become
real ones (`tan_3_bowl`), each exactly where it is painted now (two in the bowl, one on top:
the data's "count" lays them side by side, so each needs its own place); the room's picture
keeps the bowl, empty once they are taken. The intro leaves her in the corridor outside her
door, so they are for whoever steps back in, and with them all but the lunge is hers from the
first minute.

---

## 2. What each thing does

`·` = nothing. Built today: the breakables, both vacuums' spin, the towels, the kid's flight, the
librarian's shush. The rest is new.

| Thing (where) | The cry | The lunge | A tangerine rolled or lobbed at it | A hit with one in her pocket |
|---|---|---|---|---|
| The porter and his cart (4) | Stops dead, pulls the cart to the wall for 3 s: she passes, tray and all | The cart is knocked rolling 2 m, he runs after it | He stops to pick it up, peels it by the wall (10 s clear). Spent | Forgiven |
| The waiter (5) | Freezes with his tray up: she passes with hers | · | Stops, pockets it. Spent | Her tray saved |
| The jogger (promenade) | Jogs on the spot, looking round, 3 s | Spun round like a top | Hops it without a look | Forgiven |
| The steward on his rounds (8) | Pulls his cart in at once, as at a knock | · (solid) | Stops and puts it on his cart, hers to take back with E. Not spent | · |
| The buffet queue (11) | They turn aside against the tables, as for a tray | · (solid) | · | · |
| The kid with the water pistol (11) | **Draws his fire**: he turns and squirts at once | Runs and hides (built) | Catches it, eats it, back turned 15 s. Spent | Forgiven |
| The dog on the lead (4, new) | Howls back and winds the lead round its owner's legs: the line lies flat 5 s | Jumps aside | **Fetches it and brings it back.** Not spent | · (the lead is no fright) |
| The paper round's steward (5, new) | Drops the bundle and stands aside | Through the papers | Catches it, stands aside to eat it. Spent | Forgiven |
| Anyone else (the ambient cast) | Turns to look; a `♥` over the few who like cats, a finger to the lips in quiet places | · | Looks at it | · |
| The librarian | The shush (built), and the "QUIET PLEASE" sign rattles | The same | · | · |
| "Do Not Disturb" doors (7) | **Within 3 m the door opens on someone not dressed for visitors: "Startled"** | · | · | Forgiven |
| Trays on the floor (10 places) | · | Scattered with a clatter; the door flies open after she has gone | Rolled into them: the clatter, the door opens on nobody, the trays safe to cross while the guest looks about | Forgiven |
| Swinging doors (6) | · | She is past before it swings | · | Forgiven |
| Sprinklers (5) | · | Through, with a few drops | · | Forgiven |
| The casino's chips, the wet patch | · | She skates across upright; or leaps the lot | · | Forgiven |
| Basketballs (12) | · | Headed back onto the court | A lob through a hoop scores (a cheer; it comes down again) | Forgiven |
| Teppanyaki's flares, the sauna's steam | The chef is startled: his next flare comes late | Through, a wisp of smoke on her hair | · | Forgiven |
| The boat drill (walkway) | The winchman looks round: the boat holds one beat longer | Out from under it | · | Forgiven |
| The stage's swinging light | · | Under it | · | Forgiven |
| The runaway suitcase (4, new) | · | Sent to the corridor's end, where it stays | · | Forgiven |
| Robot vacuums (4, 9) | · (machines do not hear) | Sent spinning (built) | **Swallowed: it chokes, smokes and stands dead until she has left the deck.** Spent | Forgiven, and it usually eats what she dropped |
| The delivery robot (6) | · | · | Lands on its tray and rides with it; hers to take back | · |
| Shy gulls (promenade) | Up and away for 4 s | · | They come down to it and squabble: the rail is clear 8 s. Spent | · |
| The gull with the bell (promenade, new) | Flaps, keeps the bell | · | **A lob: it drops the bell for the fruit.** Spent | · |
| Gulls that dive at food (pool, Great Outdoors) | Scatter; a dive in its tell is called off | · | One takes it and leaves her cone alone 10 s. Spent | Her cone saved |
| Gulls on the balcony rails | Off the rail 6 s without swooping | Missed | Goes for it: that balcony is safe until she is past. Spent | Forgiven |
| The funnel's gulls; the bow's flocks | Break off; the flock lifts and settles | Missed | One goes after it: no swoop for 10 s. Spent | Forgiven |
| Gusts, laundry lines, partitions | · | · | · | · |
| Breakables: luggage, crates | · | Smashed (built) | Bounces off | · |
| The piñata | · | Smashed (built) | **A lob brings it down: three for one** | · |
| A thing on a shelf (the climb, deck 4) | · | · | A lob knocks it down | · |
| A pool; the sea | · | · | Floats and bobs, to swim to; in the sea, gone | · |
| The Spinnaker's piano | · | · | A note where it lands on the keys | · |
| **Bumbot at a near-catch** | Ears up, a look at her for half a second; the beat is what it was | · | **He bats it straight back to her**, sniffs his paw, pulls a face. Not spent | · |
| **Bumbot at the tip of the bow** | **He backs off**, as when she moves | · | He backs off | · |

## 3. Notes on the three uses

- **Where the cry reaches** (the user left it to my judgement: "The cry is to startle
  obstacles. Take your best judgment where crying in joy 'Кісюнічка' should affect things"). It
  costs a tangerine, so it is a tool, not a toy: no door answers it (the BOSUN's, PURSER's and
  DJ's included), and no venue has an answer of its own. People in her way step aside; animals
  react; four kinds of place are woken by it and cost her (a "Do Not Disturb" door, the kid,
  the librarian, Bumbot at the bow); bystanders only turn their heads; machines do not hear.
  Each person startled is deaf to the next cry for eight seconds.
- **The tangerine is a real thing.** One object (`Loose`) is what a throw and a knocked-out
  tangerine both are. From that alone: the vacuum that hits her and then chokes on her
  tangerine; the gull that steals what she dropped; a miss that costs a walk.
- **The lunge is a second she owns**, and it overlaps with the pocket on purpose: a tangerine
  spent with skill keeps her running; one lost to a hit costs a flinch and a chase.

| Spent on | What it buys | Comes back? |
|---|---|---|
| D | Those in her way startled three seconds; with the lunge, a second of speed and safety, a smash, a leap | No |
| A throw that is taken | A hazard out of play, a thing knocked down, a trade | No (the piñata pays three) |
| A throw that is not | Nothing | Yes, by walking to it |
| A hit | Her place and her tray | If she catches it before something else does |

---

## 4. The decks (the audit's C1 to C9)

No new tangerines on the decks, no trail, nothing twice. The decks are filled with things to do
with what she has, and with twenty things to find.

### 4.1 Twenty things to find, of four kinds

| Kind | How many | Where they end up |
|---|---|---|
| Things for Bumbot | 8 | With him in cabin 8206, the day after |
| Books | 4 more, 14 in all | The Library's shelf (fourteen gaps); the nook opens when all fourteen are home |
| Hers | 4 | **On the desk in cabin 8206, each from the moment it is picked up** |
| Her husband's | 4 | **On the same desk, beside hers, each from the moment it is picked up** |

- **The HUD** shows, for each kind, found of total (books 3/14). **A kind's count is not shown
  until its first thing is found**, the books' too. The books' number counts every book she has
  picked up, carried or shelved.
- **His four exist only after the table scene** (`after flag:table`): not lying there before it,
  not merely locked. His spoon lies a few steps from his table, so his count appears at once
  as 1 of 4.
- **Nothing makes her three uses stronger**, ever.
- **The four new titles come from the user later**, with the photos and the other missing
  things, once the game is tested: until then stand-in covers and plain pages (a picture, no
  hint).
- **Before the desk is built, the user sees a picture of it with all eight on it** (if it is
  too crowded, some of hers go by the bed).

**The first placement** (the user: "I will fine tune it while play testing"):

| # | Whose | Thing | Where | How it is got | From |
|---|---|---|---|---|---|
| 1 | Bumbot | An old tennis ball | Deck 4, the dog on the lead (about 86 m) | Three fetches; the owner hands it over | Region 1 |
| 2 | Bumbot | A ball of wool | Deck 5, forward end, the knitting lady's basket (about 22 m) | E | Region 1 |
| 3 | Bumbot | A feather on a stick | Deck 4, the shelf at the top of the climb (about 143 m) | Climb to it, or lob it down | Region 1 |
| 4 | Bumbot | A collar bell | The promenade, a gull on a lamp | A lob | Region 2 |
| 5 | Bumbot | A liquid snack in a single-use tube | Deck 4, the dry store, on a shelf | E (the room needs the green card) | Region 4 |
| 6 | Bumbot | A massage gun (a pistol shape with a round head; he enjoys it) | Deck 11, the gym, on the bench by the weights | E | Region 6 |
| 7 | Bumbot | A tin of sardines | The Sushi Bar | The chef's bubble shows a tangerine; he takes one for it | |
| 8 | Bumbot | A small remote-controlled car (his toy) | Deck 7, Entourage, past the ball pit | E | Region 9 |
| 9 | Hers | A small flag of Ukraine on a stand | Deck 5, Shore excursions, among the little flags at the desk's far end (about 146 m) | E | Region 1 |
| 10 | Hers | A bookmark with a cat on its top | Deck 6, the maid's cabin, in the book by the bed | E | Region 2 |
| 11 | Hers | A diary notepad | Deck 7, the Stardust balcony's far end, on a seat | E | Region 3 |
| 12 | Hers | A small plant in a pot | Deck 9, the cabin being cleaned, on its windowsill | E | Region 4 |
| 13 | His | His ice cream spoon | Deck 11, the Great Outdoors, the last table at the stern rail | E | After the table scene |
| 14 | His | His meditation and sleep mask | Deck 10, the far balcony, on a sunbed | E, after the vaults | Region 7 |
| 15 | His | His handheld (an Asus ROG Xbox Ally X: black, rounded grips, four coloured buttons; no logo) | Deck 12, Champs, on a sofa | E | Region 8 |
| 16 | His | A pick for his electric guitar | Deck 12, the Spinnaker, on the bandstand by the piano | E | Region 9 |
| 17 | Book | | The boat walkway, its end beyond the boat drill | E | Region 7 |
| 18 | Book | | Deck 8 midships | The thanks for the flowers | Region 7 |
| 19 | Book | | Deck 10 midships | The thanks for the tea | Region 7 |
| 20 | Book | | Deck 9 forward, the end of the officers' corridor | E | Region 9 |

Each place is set against what is built there before it is fixed (the lesson of 2026-11-14),
and each small picture is shown to the user first. The five breakables and the jackpot keep
their tangerines and get nothing more.

### 4.2 Region 1, the user's finding (C1): all seven kept

"I have just run through the deck 4, and it's almost completely empty." Metres are "about".

**Deck 4**

| m | What |
|---|---|
| 38 to 46 | **A runaway suitcase** on its wheels, rolling to and fro between two door frames with the ship's slow roll; a creak before it turns. Hop it |
| 53 to 64 | The porter (built), with his new answers (§2) |
| 86 | **A small dog on a long lead** across the corridor, its owner in the doorway (an existing figure). The lead is a line to hop. It fetches a rolled tangerine and brings it back; three fetches and the owner hands over the tennis ball. It barks at the vacuum when it comes near |
| 118 to 150 | The vacuum (built), with its new answer |
| 140 to 146 | **The climb:** a service cart, a linen cage and a shelf under the ceiling as three steps up, the feather on the shelf, the vacuum passing underneath |
| 250 | A look-out (§4.3) |

The laundry and the dry store stay behind the green card (the user: "No").

**Deck 5**

| m | What |
|---|---|
| 20 | A look-out (§4.3) |
| 22 | **A lady knitting in an open cabin**, her basket by the door with the ball of wool |
| 34 to 46 | **The paper round:** a steward skims folded newspapers along the carpet to each door; he licks a finger first. Hop them |
| 146 | Her flag at Shore excursions' desk |
| 170 to 192 | The waiter (built): on the lunch errand the cry is what gets her tray past him |

### 4.3 The look-outs (C3): five

At an end with a window or a rail, standing still two seconds eases the camera out from her to
the view; it holds while she is still and comes back when she moves (the intro's camera work).
Nothing is counted. **The Stardust's is built first and shown to the user running**, since a
camera move is judged in motion; the others after.

| Where | The view |
|---|---|
| Deck 7, the Stardust balcony's far end, the rail | The whole theatre from above |
| Deck 4, the stern end, a porthole | The wake from just above the waterline |
| Deck 5, the forward end, a porthole | The bow wave |
| Deck 9, the forward end of the officers' corridor, the front windows | Forward over the bow to the open sea |
| Deck 11, the Great Outdoors, the stern rail | Down and aft over the wake; at sunset the sun's path |

### 4.4 The deliveries (C4): three

Each hallway is entered the first time from the balconies and left by a fire door, which then
stays open both ways. After that a delivery waits at its pantry end: a tray with a cabin's
number on its tag (a label), carried to that cabin under tray rules (a low hop, no lunge, a hit
is a spill unless the pocket saves it, the cry alone for the steward, silence past the "Do Not
Disturb" doors). A hand takes it at the door, with a `♥`.

| Hallway | The load | Its own rule | Pays |
|---|---|---|---|
| Deck 8 midships | Flowers in a tall vase | It stands in front of her face: she sees the hallway through the stems | Book 18 |
| Deck 10 midships | A pot of tea | It cools (the HUD's meter, as the coffee) | Book 19 |
| Deck 9 aft | A stack of pillows | Light: a full jump allowed, but the top one slides off if she stops short | A thank-you only |

Deck 8 aft keeps its six trays and its tangerine and gets no delivery.

### 4.5 Each deck its own look (C2)

- **A coloured band on each deck's cabin number plaques:** deck 4 grey-blue, 5 warm yellow, 8
  blue, 9 green, 10 terracotta.
- **Each deck its own framed pictures between the doors, drawn in code:** deck 4 safety posters
  and rosters, 5 paintings of the ship, 6 (forward cabins) old port maps, 8 seascapes as built,
  9 botanical prints, 10 old liners' posters.
- **No tint on the wallpaper** for now. If a deck still looks like its neighbour, one deck is
  tried tinted and shown beside itself untinted.

### 4.6 Decided against

- **No new ladder.** The user's test was a smart way round a hard stretch, opened by doing it
  once; the fire doors and the balcony cabins' doors already do exactly that, and no place was
  found where a ladder would add to it.
- **No rounds** (the watchman's points at corridor ends): dropped for good.
- **No doors or venues that answer the cry; no free cry; no stronger uses; the laundry not
  opened early.**
- **Left empty by choice:** the aft ends of decks 9 and 10, Magnum's, the Spinnaker's balcony,
  behind Teppanyaki's flares. A thing from the table can be moved to one of them.

### 4.7 A check that stays

`tools/check_corridors.py`: the longest walk with nothing to do, per deck, from the data (the
audit's scratch script made permanent). Run at the end of steps 4 to 6 and its numbers given.

---

## 5. The build, step by step

Until a clip exists the plainest stand-in is used: the plain version that runs first, its art
after the user has seen it in motion.

### Step 1. D: the cry and the lunge; the cabin's bowl (no art)

| File | Change |
|---|---|
| `src/config.js` | `DASH` becomes `CRY` and `LUNGE` (§1.1) |
| `src/scenes/ShipScene.js` | `tryDash` → `tryCry(time)`: one tangerine, then `world.shout()`; with the lunge learned and her hands free, the lunge as well. `isDashing` → `isLunging` (the five callers follow). The HUD's ten-second bar goes; the count blinks when D is pressed with none. `scareContact`: nothing during a lunge and its short tail, after telling the thing that touched her (`world.lunged(kind, fromX)`). The longer leap needs nothing: the air already takes the lunge's speed |
| `src/world/world.js` | `shout(x, y, route)`: everyone and everything within reach on her deck and route gets `heard(dx)`; `lunged()` passes the word on. The breakables' collider asks `isLunging()` |
| `src/world/people.js` | `heard(p, dx)`: a walker with `touch` stops, turns aside (the built `aside`) for `startleMs`, a `!` over him, deaf for `deafMs`; anyone else turns to her (`hear="♥"` or `"shh"` in the data for the few with a mark). The porter's `lunged`: his cart rolls off and he after it |
| `src/world/movers.js`, `hazards.js`, `outside.js`, `topdeck.js`, `bow.js`, `lido.js`, `library.js`, `finale.js` | `heard()` on the gulls' four classes, `DndDoor`, `Flare`, `DrillBoat`, `Queue`, `Rounds`, the kid, the librarian, Bumbot's beats and the tip of the bow; `lunged()` where §2 says more than "through" |
| `tools/population.py` | `hear=` on the few people with a mark. `FLAG_GIVES` unchanged: the save's verb `dash` now means the lunge; the cry asks for nothing. `tan_3_bowl`: the crew cabin's three (§1.5) |
| `tools/draw_rooms.py`, `tools/build_ship_map.py` | The crew cabin's picture without the three tangerines (the bowl stays); the world's data rebuilt; the cabin looked at enlarged, full and emptied, against the picture as it is now |
| `src/sfx.js`, `src/rumble.js` | `dash` splits into `cry` and `lunge`; the rumble's "the dash starting" becomes the lunge |
| `tools/playtest.py` | `dash` rewritten (D spends one whatever it does; before the lunge is learned and with a tray, the cry alone; the porter steps aside and is deaf to a second cry; the lunge breaks the luggage, spins the vacuum, lasts a second; a fright refused during it, none after; D with none does nothing). Run: `dash`, `vacuum`, `gamepad`, `sound`, `lang`, `boot`, `deck3`, `intro` (the bowl: three taken, the count 3, the bowl empty), and `region1`, `region4`, `region6`, `region8` for the parts that used the dash |
| Docs | `GAME_DESIGN.md` §3.1, §3.2, §5.6, §6.1.2, §6.1.7, §6.3 (56) rewritten; `docs/population.md` §2.3; `docs/progress-decisions.md`; `CLAUDE.md`'s table |

Shown: the cry at the porter, the waiter and a gull; the lunge through the luggage and through
a swinging door; the cabin's bowl full and empty.

### Step 2. The real tangerine, and the pocket (no art)

| File | Change |
|---|---|
| `src/world/tangerine.js` (new) | `Loose`: an arcade body 8 px across, bounce 0.35, drag on a floor, colliding with the solid layer, the walks, the solids and the breakables; off the hull: a splash, gone; in a pool: it floats. At rest it becomes an ordinary tangerine on the floor, kept in the save (`save.loose`). Each frame it offers itself to what is near (`world.offered(t)`): the first to take it has it |
| `src/scenes/ShipScene.js` | `pocket(fromX, kind)`: with one on her and `?pocket=off` not set: one less, a `Loose` thrown the way she is pushed, the flinch (`flinchUntil`), `safeUntil`, the blink. Called at the top of `scareContact`; a hit inside `safeUntil` is ignored |
| `src/world/carry.js` | `spill(fromX, own)`: the pocket first, unless it is her own doing (`sway`, a melted cone) |
| `src/save.js` | `loose: []` in the empty save (old saves take the default; no new key) |
| `src/sfx.js`, `src/rumble.js` | `pocket`, `roll`, `plop`; the spill's light tick reused, no eleventh rumble |
| `tools/playtest.py` | A new scenario `pocket` (a hit with one: place and tray kept, the count down by one, the tangerine on the floor and picked up again; with none: the fright as before; a fall not forgiven). Run with it: `vacuum`, `falls`, `overboard`, `region1` |

Shown: the flinch frame by frame beside the porter; the tangerine rolling off.

### Step 3. The throw (art: one clip of hers, about 5 generations, asked first)

| File | Change |
|---|---|
| `src/controls.js` | `throw: 'F'`, Y on the controller; `GAME_DESIGN.md` §3.1's table |
| `src/scenes/ShipScene.js` | `tryThrow(input)`: the roll, or the lob with ↑; a stand-in pose until her clip is approved |
| `src/world/*.js` | `offered(t)` on the things of §2's fourth column |
| `assets/source/her/throw/`, `tools/build_sprites.py` | Her underarm throw, skeleton-v3 by poses (only the body described; her fist found in every frame and the tangerine put in it, behind her fingers) |
| `tools/playtest.py` | A new scenario `throw` (a roll nothing takes is picked up again; the vacuum chokes; a gull takes one; the piñata by a lob; Bumbot bats it back and the beat goes on). Run with it: `gamepad`, `region2`, `region6`, `region7`, `region8` |

Shown: her throw's frames for approval before anything else; then each target as a short strip.

### Step 4. Region 1's decks, and the first things to find (art: about 45, asked item by item)

- The dog (a character with a walk, a sit and a run: about 20), the knitting lady (a seated
  figure: about 10), the paper round's steward (about 13), the runaway suitcase (0 to 1), the
  climb (pieces the atlas has), four small pictures (the tennis ball, the wool, the feather,
  the flag: about 4).
- New classes in `src/world/movers.js`: `Roller` (the suitcase), `Fetcher` (the dog), `Skimmer`
  (the papers). Data: `ROLLERS`, `DOGS`, `SKIMMERS` in `tools/population.py`.
- **The machinery of the things to find, here in its smallest form:** `KEEPS` in
  `tools/population.py` (id: place, what, whose: `cat`, `her`, `him`, how it is got, `after`); a
  kind `keep` in `src/world/world.js` (taken with E, handed over, or knocked down); `save.keeps`;
  the HUD's counts in `Progression.buildHud`, each hidden until its first find.
- Each new thing looked at enlarged beside her (the nine questions of "Looking closely");
  `tools/check_overlaps.py` empty; `tools/check_corridors.py` (new) run.
- Playtests: a new scenario `deck4`; `region1`, `boot`, `deck3`, `trunk`, `ladder`.

### Step 5. The rest of the twenty (art: about 12 small pictures, shown first)

- The other placements of §4.1 (those not paid by a delivery).
- `src/world/library.js`, `tools/draw_pages.py`: fourteen wherever ten is written (the shelf's
  gaps, `books_all`, the colours, the pages); the count on the HUD as found of 14, hidden until
  the first.
- His four `after flag:table`. Cabin 8206 (the room `cabin`; `tools/draw_cabin.py` for where the
  desk's top is): his and hers on the desk, each a prop shown from its own flag on; the picture
  of the desk with all eight shown to the user first.
- `src/world/finale.js`: Bumbot's eight laid out with him the day after.
- Playtests: a new scenario `keeps` (each of his places empty before the table scene and
  holding its thing after; each thing on the cabin's desk once found; each count appearing with
  its first find); `region2`, `region6`, `region9`, `region5`, `cabin`, `finale`, and each
  region's scenario where something is placed.

### Step 6. The look-outs and the deliveries (art: about 5)

- `Lookout` in `src/world/movers.js`, `LOOKOUTS` in the data: the Stardust's first, shown to the
  user running, then the other four (a porthole piece and a window piece, 0 to 1 each).
- The three deliveries: `LOADS` in `src/world/carry.js` (the vase drawn in front of her, the
  tea's meter, the pillows' slide), a source at each pantry end `when` its fire door is opened,
  the door that takes it; books 18 and 19.
- Playtests: a new scenario `deliveries`; `region3`, `region5`, `region7`, `region4`, `region9`.

### Step 7. Each deck its own look (no art)

`tools/build_ship_map.py`: the plaques' bands, the pictures by deck, drawn in code. The whole
ship rendered and looked at; `boot`, `stairs`, `lift`, `tools/check_overlaps.py`.

### Cost

| | Generations |
|---|---|
| Steps 1 and 2 | 0 |
| Step 3 | about 5 |
| Step 4 | about 45 |
| Step 5 | about 12 |
| Step 6 | about 5 |
| Step 7 | 0 |
| **All** | **about 67 of the 540 left** |

Estimates: the real price is stated before each spend. Sounds are synthesised and cost nothing;
whoever builds cannot hear them: every new one is the user's to judge on the soundboard.

---

## 6. Risks

- **She may run dry.** 56, three uses, every cry one of them, and nothing grows back. Softened
  only by tangerines that roll being hers to pick up again; and the game is finishable with
  none (audit C10). If play shows her at zero for long, the levers are how easily a dropped one
  is caught again and what the pocket costs. To be watched from step 2 on.
- **The pocket may make frights rare.** How fast and how far the dropped one rolls decides how
  often it is lost: the first thing to tune.
- **A cry bought and wasted.** A tangerine spent where nothing hears it is a dear lesson with
  no word of warning. If the user finds that harsh in play, a cry that startles nobody could
  cost nothing.
- **Motion.** The lunge, the flinch, the roll and the look-outs' camera are judged in motion:
  each is shown plain first, and the user's eye is the test.
- **"Nothing twice."** The three deliveries are one kind of errand with three loads and three
  rules: the closest the plan comes to the line.

---

## 7. What is still the user's to give, later

- The fourteen books' titles, the photos for the photo slots, and "other missing things", once
  the game is tested and verified.
- The fine tuning of every placement, in play.

---

## 8. The user's answers (2026-11-15), in their words

**The order:** "I want to implement you earlier proposal regarding the dash mechanics, the
'three uses' one. I do want to still spend a tangerine instead of a 'breath' for the one-second
dash itself." Tangerines: "For now, I want to leave their number and their location unchanged."
"No path hint at this moment, I do not like those." "Think on how to make the corridors fun,
enriched and varied."

**From the audit, earlier the same day:** ends "can be both" (progress and pleasure); a ladder
only as "a smart shortcut that can be used to avoid difficult path with obstacles, and one
that's opened once that path is complete at least once"; the Spinnaker's balcony and the
promenade's enclosed ends: "Leave as they are for now."

**The first nine questions:**

| The question | The answer |
|---|---|
| The cry alone free, or every D costs one? | "Every D cost one" |
| The cry from the start, the lunge from the Seven Seas? | "As assumed" |
| The pocket on every hit? | "As assumed" |
| The second collection | "Take you best judgement here in order to make the game fun and varied" |
| The laundry open in region 1? | "No" |
| The BOSUN's, PURSER's and DJ's doors answering the cry? | "The cry is to startle obstacles. Take your best judgment where crying in joy 'Кісюнічка' should affect things." |
| F and Y for the throw? | "Yes" |
| No new ladder, the rounds later? | "Ok" |
| Anything to drop from the lists? | "Skip this for now" |

**On the collection and the tangerines:**

| The question | The answer |
|---|---|
| How do the things for Bumbot affect progress? (The user's own) | "I would reduce the number of collectibles for Bumbot and introduce instead a few more books, and some other items for her and her husband" |
| 8 for Bumbot, 4 more books, 4 for her, 4 for him? | "Ok" |
| The four titles | "I will provide all the titles later, when the game is fully tested and verified. Together with photos and other missing things" |
| Their things | "Bumbusik: A bookmark (cat-shaped on top of the bookmark), a small Ukraine flag (meant to stand on a writing desk), a diary notepad, a small plant in a pot. Husband: his handheld gaming device (Asus ROG Xbox Ally X), his ice-cream spoon, his mediation/sleep mask, a pick for his electric guitar" |
| What each kind pays | "Drop the stronger uses idea, I don't like it. Otherwise, as you suggested. Also, the HUD shows number of items found vs total per category" |
| (The user's own) | "In her initial crew cabin there's a bowl with three tangerines. Make the tangerines collectible (which increases the total number by 3)" |
| (The user's own) | "Also, the HUD only starts showing a collectible category when a first item is found. Place husband's collectibles in such a way, that they can only be found after she first meets him in cabin 8206" |
| Which meeting? (He is in cabin 8206 only at the ending) | "Yes, this is the meeting, at the table there. But his things, when picked up, are shown in the cabin 8206 on the desk" |

**The twelve asked one by one:**

| # | The question | The answer |
|---|---|---|
| 1 | D with a tray or before the lunge is learned: the cry alone for one tangerine, the cry free, or nothing? | 1: the cry alone, for one |
| 2 | The books' count: hidden until the first book, or shown from the start? | 1: hidden until the first, then found of 14 |
| 3 | Her things: cabin 8206's desk beside his, her crew cabin's desk, or only at the ending? | 1: cabin 8206's desk, from the moment each is picked up |
| 4 | His handheld: recognisable (black, grips, four coloured buttons), plain, or with something on its screen? | 1: recognisable, no logo |
| 5 | Region 1's seven new things (the suitcase, the dog, the climb, deck 4's look-out, the knitting lady, the paper round, a thing at Shore excursions) | "All" |
| 6 | Which eight for Bumbot? | The tennis ball, the wool and the bell as tied to what was kept; "5, 7" (the feather on a stick, the sardines), "a liquid snack (packed in a single use plastic tube), a massage device (for humans, but very much enjoys it)"; then "a small remotely-controlled car (his toy)"; the massage device: a handheld massage gun |
| 7 | Where each of the twenty lies (§4.1's table) | "I will fine tune it while play testing" |
| 8 | The deliveries: two, three with the mask as the pillows' pay, three with a thank-you, or none? | 3: all three, the pillows a thank-you only |
| 9 | The look-outs: four, three, all five, one first, or none? | 3: all five |
| 10 | Each deck's look: bands and pictures in code; by PixelLab; with a tint; bands only; none? | 1: bands and pictures drawn in code, no tint |
| 11 | The rounds: drop, later, build? | 1: dropped for good |
| 12 | Finish the plan, merge into `main`, push? | 1: yes |
