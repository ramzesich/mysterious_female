# Plan: three uses for a tangerine, and decks worth walking (2026-11-15)

**A proposal for the user's review. Nothing here is built.** It follows
`docs/brainstorm/dash-rework.md` (the "shout, throw, pocket" proposal) and
`docs/audit-2026-11-15.md` (findings C1 to C10; the visual faults V1 to V7 are another session's,
`docs/plan-visual-fixes.md`).

The user's order (2026-11-15): "I want to implement your earlier proposal regarding the dash
mechanics, the 'three uses' one. I do want to still spend a tangerine instead of a 'breath' for
the one-second dash itself. Review the 'three uses' plan, think on how to enrich it and make it
more fun. Think on how to include the later audit findings... No path hint at this moment, I do
not like those. Think on how to make the corridors fun, enriched and varied. Propose a detailed
implementation plan, and I will review it."

## 0. What is fixed

| The user's word | What it means here |
|---|---|
| "For now, I want to leave their number and their location unchanged" | The 53 tangerines stay where they are. None added, none moved. Everything new on the decks is something else |
| "Spend a tangerine... for the one-second dash itself" | The lunge costs one tangerine |
| "No path hint" | No trail, no far meow answering the cry (the brainstorm's question 4 is dropped), nothing that points to where something is |
| Ends: "They can be both" | An end may pay in pleasure or in progress |
| A ladder only as "a smart shortcut... opened once that path is complete at least once" | See §4.7: the game has this rule already; no new ladder is proposed |
| V4, V5: "Leave as they are for now" | The Spinnaker's balcony and the promenade's enclosed ends get nothing new |
| Standing rules | No hint popups; no person, hazard, errand or reward twice; nothing floats; never the word; every picture shown before it is placed; every cost stated before it is spent |

Read from the code for this plan (so the steps below name real places):

- Every fright by contact goes through one function, `scareContact(fromX, kind)` in
  `src/scenes/ShipScene.js` (18 callers), and every spilled tray through `Carry.spill(fromX)` in
  `src/world/carry.js`. Falls and overboard have their own (`scareFall`, `scareOverboard`).
- The dash is `tryDash` / `isDashing` / `updateDash` in the ship scene, `DASH` in `src/config.js`;
  five places ask `isDashing()` (the breakables' collider in `world.js`, deck 4's vacuum, the
  darting vacuum and the towel stack in `movers.js`, the kid in `lido.js`).
- It is learned at near-catch 1 (`FLAG_GIVES = {"bb1": ["verb:dash"]}` in `tools/population.py`).
- People who walk already have "turned aside, she can slip past" (`aside` in
  `src/world/people.js`, the waiter at his tables).
- A fire door she has come through from its free side is open both ways for good (`passes()` in
  `src/progression.js`, `save.opened`).
- PixelLab: 540 generations left until 2026-11-30.

---

## 1. The three uses

A tangerine can do three things. Each has its own job, and **a tangerine used well can come
back**: that is what lets 53 serve three uses.

### 1.1 D: the cry, and the lunge (B on the controller)

- **Standing still, or with her hands full: the cry alone.** "Кісюнічка!!!" in her bubble, her
  sound, and everything alive within 4.5 m on her deck hears it (§2). **Free**, one cry every
  2.5 s (pressed sooner: nothing).
- **On the move (a direction held), one tangerine: the cry with the lunge.** One second at twice
  her speed (280 px a second, about six metres), the trail behind her. During it:
  - what the dash broke breaks (the five breakables), the vacuums spin, the towels topple;
  - **nothing can frighten her by contact**: the second is hers. A swinging door, a sprinkler,
    a basketball, the porter's cart: she is through. Each gives way in its own manner (§2);
  - **in the air it is a leap**: a jump taken in a lunge carries about 4.5 m against 2.3 m (the
    wet patch by the pool, the casino's chips, the trays on the floor are cleared in one);
  - falls and the sea are what they are. Solid things stay solid (carts, the queue, walls, ropes).
- No tangerine and on the move: the cry alone, and the HUD's count blinks once.
- Not while she crawls, climbs, swims, or holds Bumbot. With a tray: the cry only (as the
  design's tray rules say: no dash).

**Why the cry alone is free (question 1):** it is the toy. If every "Кісюнічка!!!" costs fruit
she will keep it for emergencies and the ship will never answer her (§3.1). The tangerine buys
the legs.

Numbers (all in `src/config.js`, to be tuned by play): `CRY = { reach: 4.5 m, breathMs: 2500,
startleMs: 3000, deafMs: 8000 }`, `LUNGE = { ms: 1000, speed: 2, safeTailMs: 300 }`. The speed
stays under Bumbot's 300, so "faster than she can ever run" stays true.

### 1.2 F: the throw (Y on the controller), one tangerine

- **F: a roll.** Underarm, low; it bounces once and rolls about six metres, off steps and edges,
  and stops against anything solid.
- **↑ with F: a lob.** High and short (it tops out just under the ceiling, about 2.3 m ahead):
  for things up on shelves, ledges, hoops and strings.
- **It is a real thing on the floor.** Whatever wants it takes it (§2). If nothing does, it lies
  where it stopped and is picked up by walking over it, today or next week (it is saved). Over
  the side it is gone, with a small splash. In a pool it floats.
- Not with a tray, crawling, climbing, swimming or holding Bumbot.

### 1.3 The pocket (automatic), one tangerine

- A hit that would be a fright or a spilled tray, with a tangerine on her: she flinches (the
  `her-hit` clip, a third of a second), is pushed a step back, blinks for a second and a half
  during which nothing can touch her, **and keeps her place and her tray.**
- **The tangerine is knocked out of her pocket and rolls away fast**, the way she was pushed. It
  is the same real thing as a thrown one: she can run after it, and whatever wants it may get
  there first (the vacuum that hit her swallows it and chokes; a gull has it).
- With none on her, a hit is what it is today. Falls, the sea and a cake that wobbles over by her
  own feet are never forgiven.
- **Testing:** with `?tangerines=infinite` (every link the user gets) the pocket would forgive
  everything and no fright would ever be seen. A flag `&pocket=off` switches it off; the
  playtests that check frights start with no tangerines, as they do now.

### 1.4 When she has each (question 2)

Proposed: **the throw and the pocket from the first tangerine** (deck 4's is at 31 m), **the cry
from the start** (she is looking for a cat: calling him is what one does), **the lunge from the
Seven Seas** (near-catch 1, where "she lunges with the scream", as the design says). That gives
region 1, the thinnest part of the game, two of the three uses and the free one. Today's rule
(§6.1.2: all of D learned at near-catch 1) is the alternative.

---

## 2. What each thing does

`·` = nothing. Built today: the breakables, both vacuums' spin, the towels, the kid's flight, the
librarian's shush. The rest is new.

| Thing (where) | The cry | The lunge | A tangerine rolled or lobbed at it | A hit with one in her pocket |
|---|---|---|---|---|
| The porter and his cart (4) | Stops dead, pulls the cart to the wall for 3 s: she passes, tray and all | The cart is knocked rolling 2 m, he runs after it | He stops to pick it up, peels it by the wall (10 s clear). Spent | Forgiven |
| The waiter (5) | Freezes with his tray up: she passes with hers | · (she has no tray then: he was never a fright) | Stops, pockets it. Spent | Her tray saved |
| The jogger (promenade) | Jogs on the spot, looking round, 3 s | Spun round like a top | Hops it without a look (not for him) | Forgiven |
| The steward on his rounds (8) | Pulls his cart in at once, as at a knock | · (solid) | Stops and puts it on his cart, to be taken back with E. Not spent | · |
| The buffet queue (11) | They turn aside against the tables, as for a tray | · (solid) | · | · |
| The kid with the water pistol (11) | **Draws his fire**: he turns and squirts at once | Runs and hides (built) | Catches it, eats it, back turned 15 s. Spent | Forgiven |
| The old lady on her sunbed (12) | Glares; her glasses slide down | · (solid) | · | · |
| Anyone else (the ambient cast) | Turns to look; one small mark over them, by the person: `!`, `?`, `♥` for those who like cats, a finger to the lips in quiet places | · | Looks at it | · |
| The librarian | The shush (built), and the "QUIET PLEASE" sign rattles | The same | · | · |
| "Do Not Disturb" doors (7) | **Within 3 m the door opens on someone not dressed for visitors: "Startled".** Hallways want her quiet | · | · | Forgiven |
| Trays on the floor (10 places) | · | Scattered with a clatter; the door flies open after she has gone | Rolled into them from a distance: the clatter, the door opens on nobody, and the trays are safe to cross while the guest looks about | Forgiven |
| Swinging doors (6) | The one inside looks out early: the door is spent for this pass | She is past before it swings | · | Forgiven |
| Sprinklers (5) | · | Through, with a few drops | · | Forgiven |
| The casino's chips, the wet patch | · | She skates across upright; or leaps the lot | · | Forgiven |
| Basketballs (12) | · | Headed back onto the court | A lob through a hoop scores (a cheer; it comes down again) | Forgiven |
| Teppanyaki's flares, the sauna's steam | The chef misses his beat: the next flare comes late | Through, a wisp of smoke on her hair | · | Forgiven |
| The boat drill (walkway) | The winchman looks round: the boat holds one beat longer | Out from under it | · | Forgiven |
| The stage's swinging light | · | Under it | · | Forgiven |
| Robot vacuums (4, 9) | · (machines do not hear) | Sent spinning (built) | **Swallowed: it chokes, smokes and stands dead until she has left the deck.** Spent | Forgiven, and it usually eats what she dropped |
| The delivery robot (6) | Beeps back | · | Lands on its tray and rides with it; hers to take back | · |
| Shy gulls (promenade) | Up and away for 4 s | · | They come down to it and squabble: the rail is clear for 8 s. Spent | · |
| Gulls that dive at food (pool, Great Outdoors) | Scatter; a dive in its tell is called off | · | One takes it and leaves her cone alone for 10 s. Spent | Her cone saved |
| Gulls on the balcony rails | Off the rail for 6 s without swooping | Missed | Goes for it: that balcony is safe until she is past. Spent | Forgiven |
| The funnel's gulls; the bow's flocks | Break off; the flock lifts and settles (a sight) | Missed | One goes after it: no swoop for 10 s. Spent | Forgiven |
| Gusts, laundry lines, partitions | · | · | · | · |
| Breakables: luggage, crates | · | Smashed (built) | Bounces off | · |
| The piñata | · | Smashed (built) | **A lob brings it down: three for one** | · |
| Things on a shelf or a ledge (new, §4.2) | · | · | A lob knocks them down | · |
| A pool; the sea | An echo over the water | · | Floats and bobs, to swim to; in the sea, gone | · |
| The Spinnaker's piano | · | · | A note where it lands on the keys | · |
| Empty halls (the Stardust, the atrium) | Her echo comes back | · | · | · |
| **Bumbot at a near-catch** | Ears up, a look at her for half a second; the beat is what it was | · | **He bats it straight back to her**, sniffs his paw, pulls a face (cats and citrus). Not spent | · |
| **Bumbot at the tip of the bow** | **He backs off**, as when she moves: the end asks her to be quiet and still | · (she holds no lunge there if she is still) | He backs off | · |

Thirty hazards are still answered only by timing. The platforming stays; what changes is that
every one of them now has at least one answer besides, and none of the answers is the same thing.

---

## 3. What makes it more than the brainstorm had

### 3.1 The ship answers her

The cry is free, so she will try it everywhere, and **somewhere new answers every time**. None
of it says where anything is; it is the ship being alive. About twenty answers, each used once:

- **Cabin doors that answer** (a sound from behind the door, a small mark, sometimes a head
  round it), each at one fixed door, ten in all: the BOSUN's parrot repeats her, badly; the
  PURSER's coins spill; a bass drop behind the DJ's door; a chain of three dogs barking one after
  another down deck 5; a baby cries, then a lullaby starts; a snore stops, and starts again; an
  opera singer answers a note higher; a newspaper is lowered and a "shh" comes over it; a child
  looks out and a paper plane follows; the honeymooners' door ("JUST MARRIED") throws a slipper.
  A few of these hand her something (§4.2). Those with a sound of their own are heard faintly
  through the door as she walks by (a snore, a whistle, a bass thump): a sound, not a sign.
- **Every venue's people have their own answer** (answers C8, the venues that are a walk past
  people), set against the cast that is built there. For example: a dealer drops his cards;
  Magnum's waiter pops a cork; the Spinnaker's pianist plays a sting; the gym's runner stumbles
  on her treadmill and waves; the chapel's guests all turn; the kids' club claps.
- **It costs her in places:** "Do Not Disturb" hallways, the Library, the kid, the tip of the
  bow. So it is a choice, not a button to hold.

### 3.2 The tangerine is a real thing

One object (`Loose`, §5 step 2) is what a throw and a knocked-out tangerine both are. It rolls,
bounces, falls off edges, floats, and gets taken. That one decision gives, without more rules:
the vacuum that hits her and then chokes on her tangerine; the gull that steals what she
dropped; a miss that costs a walk; the chase after her own fruit down a corridor of trays.

### 3.3 Two throws, and things to aim at

The roll is for the floor (vacuums, gulls, walkers, trays), the lob for what is up (the piñata, a
hoop, a thing on a ledge, a gull on a lamp). Aiming is by where she stands: no cursor.

### 3.4 The lunge is a second she owns

At one second it stops being a ten-second sprint that makes hallways harder, and becomes a
timed answer: through the door as it swings, under the boat as it drops, across the chips. It
overlaps with the pocket on purpose: **a tangerine spent with skill keeps her running; one lost
to a hit costs a flinch and a chase.**

### 3.5 What a tangerine is worth afterwards

| Spent on | What it buys | Comes back? |
|---|---|---|
| A lunge | A second of speed and safety, a smash, a leap | No |
| A throw that is taken | A hazard out of play, a thing knocked down, a trade | No (the piñata pays three) |
| A throw that is not | Nothing | Yes, by walking to it |
| A hit | Her place and her tray | If she catches it before something else does |

The seven tangerines behind crates and in the piñata now cost one to reach by lunge, or (the
piñata) one lob: still fruit for fruit, so the prize for effort becomes the keepsakes (§4.2).

---

## 4. The decks (the audit's C1 to C9)

No new tangerines, no trail, nothing twice. So the decks are filled with **things to do with what
she has** (jump, cry, roll, lob, lunge, carry) and with a second thing to find.

### 4.1 The kit

| Piece | What it is | Answers |
|---|---|---|
| **Keepsakes** (§4.2) | The second collection: about fourteen small things, each got a different way | C3, C5, C6, C7, C8, C9 |
| **Doors that answer** (§3.1) | Ten doors in the cabin corridors | C2, C9 |
| **A deck's own resident** | One new moving thing each on decks 4 and 5, found nowhere else | C1 |
| **Something to climb** | A parked cart, a linen cage and a shelf as three steps up: the jump gets a use in a corridor | C1 |
| **Look-outs** | At an end with a window or a rail, standing still eases the camera out to the view (the intro's own camera work). Pleasure only, no count | C3 |
| **Deliveries** | A tray with a cabin's number on its tag, to carry down a hallway she has already opened | C4 |
| **Each deck its own look** | The plan's own answer, never built: a coloured band on each deck's plaques, each deck its own framed pictures, a tint to the wallpaper | C2 |
| **A check that stays** | `tools/check_corridors.py`: the longest walk with nothing to do, per deck, from the data. The audit's scratch script made permanent; a step is not done while a stretch over 30 m is empty | C9 |

### 4.2 The keepsakes: things for Bumbot (question 4)

Proposed as the brainstorm recommended: small things a cat would want, the HUD counting them
beside the books, **each one lying about cabin 8206 with him in the day-after scene.** The list
is a proposal; each picture is shown first, and any of them can go.

| # | What | Where | How it is got | Audit |
|---|---|---|---|---|
| 1 | A toy mouse | Deck 4, the service deck, on the shelf above the linen cage | Climb to it, or lob it down | C1 |
| 2 | An old tennis ball | Deck 4, the dog on the lead (§4.3) | Three fetches, and its owner hands the dog's spare over | C1 |
| 3 | A ball of wool | Deck 5, the forward end: a lady knitting in an open cabin | The cry: she jumps, the ball rolls out into the corridor | C1, C3 |
| 4 | A paper boat | Deck 5, Shore excursions, the far end of its desk | E | C1, C9 |
| 5 | A feather duster | Deck 6, the maid's cabin | E | C7 |
| 6 | A collar bell | The promenade, in the beak of a gull on a lamp | A lob: it drops the bell for the fruit | C5 |
| 7 | A knotted rope's end | The boat walkway, the last bollard beyond the drill | E | C5 |
| 8 | A ping-pong ball | Deck 7, Entourage, past the ball pit | E | C3 |
| 9 | A feather on a stick | Deck 7, the Stardust balcony's far end, by the look-out over the stage | E | C3 |
| 10 | A paper plane | Deck 8 midships, the child's door | The cry | C4 |
| 11 | A slipper | Deck 9, the honeymooners' door | The cry | C4 |
| 12 | A cardboard box | Deck 9, the cabin being cleaned | E | C7 |
| 13 | A cushion | Deck 10, the far balcony | E, after the vaults | C6 |
| 14 | A sardine tin | Deck 9 forward, the end of the officers' corridor | E | C3 |
| 15 to 17 | A cork; a prize ball; a slice of tuna | Magnum's (the cry pops it); a hoop game at Champs, a new piece (a lob); the Sushi Bar (the chef takes a tangerine for it: his bubble shows one) | | C8 |
| 18 to 20 | One each from the three deliveries (§4.5) | Decks 8, 9, 10 | A thank-you from the door | C4 |

The five breakables and the jackpot keep their tangerines and get nothing more: they pay already.

### 4.3 Region 1, the user's finding (C1)

Today: from the ladder to the stern, 158 m with a vacuum and two carts. Proposed, bow to stern
(every place is "about": each is set against what is built there, by the lesson of 2026-11-14):

**Deck 4.**

| m | What | Kind |
|---|---|---|
| 24 to 31 | As built: the lost passenger, the luggage, the tangerine | |
| 38 to 46 | **A runaway suitcase**: on its wheels, rolling to and fro between two door frames with the ship's slow roll; a creak before it turns. Hop it. A lunge sends it to the corridor's end, where it stays | New hazard, deck 4's own |
| 53 to 64 | The porter, with his three new answers (§2) | Built, enriched |
| 86 | **A small dog on a long lead** across the corridor, its owner in the doorway. The lead is a line to hop. The cry: it howls back and winds the lead round the owner's legs (the line lies flat for 5 s). **A rolled tangerine: it fetches it and brings it back.** Three fetches: keepsake 2. It barks at the vacuum when it comes near | New resident. It teaches the throw for nothing |
| 112 | **The laundry opens without a card in region 1** (question 5): its steam, its folder, a first room. Its tangerine is where it was | A lock moved, nothing else |
| 118 to 150 | The vacuum, with its new answer (a rolled tangerine) | Built, enriched |
| 140 to 146 | **The climb**: a service cart, a linen cage, a shelf under the ceiling with keepsake 1, the vacuum passing underneath | New |
| 172 | A door that answers (the cook's radio turns up) | §3.1 |
| 224 to 236 | The BOSUN's parrot, the PURSER's coins, the DJ's beat (question 6: the plates are the user's in-jokes) | §3.1 |
| 250 | **A look-out**: a porthole at the corridor's end, the wake at the waterline | New |

**Deck 5.**

| m | What | Kind |
|---|---|---|
| 22 | The lady knitting in an open cabin (keepsake 3); the end of the corridor | New |
| 34 to 46 | **The paper round** (optional: it needs a new figure): a steward skims folded newspapers along the carpet to each door; he licks a finger first. Hop them. The cry: he drops the bundle | New hazard, deck 5's own |
| 56 to 70 | The chain of three barking doors | §3.1 |
| 110 to 150 | Shore excursions: the agent's brochures go flying at the cry; the paper boat at the desk's far end (keepsake 4) | Enriched |
| 170 to 192 | The waiter, with his answers: **on the lunch errand the cry is what gets her tray past him** | Built, enriched |

The lunch errand's walk back with the tray then has the cry to use on the porter and the waiter,
which is the first time it earns its keep.

### 4.4 The ends (C3, C5)

| End | What it gets |
|---|---|
| Deck 4 aft | The look-out at the waterline; the three doors that answer |
| Deck 5 forward | The knitting lady |
| Deck 7, the Stardust balcony | The look-out over the whole house; the feather; her echo |
| Deck 7, Entourage | The ping-pong ball |
| Deck 9 forward | The sardine tin; a look-out through the front windows over the bow |
| Deck 9 aft, deck 10 aft | A door that answers each (the opera singer; the snorer) |
| Deck 11, the Great Outdoors' stern half | The look-out over the wake from the rail |
| The walkway beyond the boat drill | The rope's end |
| The promenade | The gull with the bell |
| Teppanyaki's flares | Nothing behind them: they stay a thing on the way. The cry gives them a tell to play with |
| The Spinnaker's balcony | Nothing (the user: leave it) |

### 4.5 The optional hallways (C4): deliveries

Each of the four hallways is entered the first time from the balconies and left by a fire door,
which then stays open both ways. **After that a delivery waits at its pantry end**: a tray with a
cabin's number on its tag (a label), to carry to that cabin under tray rules. The hallway is the
same; the rules are new (a low hop, no lunge, a hit is a spill unless the pocket saves it, the
cry alone for the steward, and silence past the "Do Not Disturb" doors).

| Hallway | The load | Its own rule |
|---|---|---|
| Deck 8 midships | Flowers in a tall vase | It hides what is ahead of her: she sees the hallway through the stems |
| Deck 9 aft | A stack of pillows | Light: a full jump allowed, but the top one slides off if she stops short |
| Deck 10 midships | A pot of tea | It cools (the HUD's meter, as the coffee) |

A hand takes it at the door, a `♥`, and a keepsake. Three, not four: deck 8 aft keeps its
tangerine at the end and its six trays as they are.

### 4.6 Each deck its own look (C2)

As `docs/population.md` §4 had it: the plaques' band (8 blue, 9 green, 10 terracotta, and 4 and
5 their own), the framed pictures by deck (4 safety posters and rosters, 5 the ship, 6 port
maps, 8 seascapes as built, 9 botanical prints, 10 liners' posters), a faint tint to each
deck's wallpaper. It rebuilds the map, so it goes after the other session's visual fixes are in.

### 4.7 Earned shortcuts: no new ladder

The user's test for a ladder was that it be a smart way round a hard stretch, opened by doing
that stretch once. **The game does this already, with doors:** every fire door of decks 8, 9
and 10 and every balcony cabin's door is shut from one side until she has come through it, and
open both ways for good after. I looked for a place where a ladder would add to that and found
none that passes the test: every gauntlet already ends in such a door, and a ladder cannot be
used with a tray, which is when a way round is most wanted. So this plan adds none. If a stretch
felt like a slog to go back through, name it and I will look at that one.

**The rounds** (the audit's I8: a watchman's point at each corridor's end, counted on the HUD)
are left out of the first build, as a thing to decide after the steps below have been played:
with keepsakes, look-outs and doors at the ends, a box to press at each may be one thing too
many. If wanted, what they would pay is the three uses made stronger (a deeper breath: the cry
reaches further; a better arm: the roll goes further): progress that is hers.

---

## 5. The build, step by step

Each step ends with pictures in the chat, the link, the scenarios run named, and a stop for the
user's review. Art is asked for with its price before it is made, and shown before it is placed.
Until a clip exists the plainest stand-in is used (the lesson of the intro: the plain version
that runs first, its art after it has been seen in motion).

**Where it is built:** on a branch of its own off `main`, in a git worktree of its own (a second
folder), so that it never shares a folder with the other session again. Steps 4 and 7 rebuild
the map (`maps/ship.json`, `maps/world.json`): they wait until the visual fixes are merged.

### Step 1. D: the cry and the lunge (no art)

| File | Change |
|---|---|
| `src/config.js` | `DASH` becomes `CRY` and `LUNGE` (§1.1) |
| `src/scenes/ShipScene.js` | `tryDash` → `tryCry(time, input)`: the breath, then `world.shout()`; with a direction held, the lunge learned, a tangerine and free hands, the lunge as well. `isDashing` → `isLunging` (the five callers follow). The HUD's ten-second bar goes; the count blinks when a lunge is asked for with none. `scareContact`: `if (this.isLunging()) return` at its top, after telling the thing (`this.world.lunged(kind, fromX)`). The longer leap needs nothing: the air already takes the lunge's speed |
| `src/world/world.js` | `shout(x, y, route)`: everyone and everything within reach on her deck and route gets `heard(dx)`; `lunged()` passes the word to the thing that touched her. The breakables' collider asks `isLunging()` |
| `src/world/people.js` | `heard(p, dx)`: a walker with `touch` stops, turns aside (the built `aside`) for `startleMs`, a `!` over him, deaf to the next cry for `deafMs`; anyone else turns to her with their mark (`hear` in the data: `!`, `?`, `♥`, `shh`). The porter's `lunged`: his cart rolls off and he after it |
| `src/world/movers.js`, `hazards.js`, `outside.js`, `topdeck.js`, `bow.js`, `lido.js`, `library.js`, `finale.js` | `heard()` on the gulls' four classes, `DndDoor`, `SwingDoor`, `Flare`, `DrillBoat`, `Queue`, `Rounds`, `OldLady`, the kid, the librarian, Bumbot's beats and the tip of the bow; `lunged()` where §2 says more than "through" |
| `tools/population.py` | `hear=` on the people who get a mark of their own; `FLAG_GIVES` unchanged (the save's verb keeps the name `dash`; question 2 decides whether the cry asks for it) |
| `src/sfx.js`, `src/rumble.js` | `dash` splits into `cry` and `lunge`; the rumble's "the dash starting" becomes the lunge |
| `tools/playtest.py` | `dash` rewritten (the cry free and its breath; the lunge spends one, breaks the luggage, spins the vacuum, lasts a second; a fright refused during it; none after); `vacuum`, `gamepad`, `sound` and `lang` run; `region1` (near-catch 1), `region4` (the darting vacuum, the towels), `region6` (the kid, the crates), `region8` (the piñata) run for the parts that used the dash |
| Docs | `GAME_DESIGN.md` §3.1, §3.2, §5.6, §6.1.2, §6.1.7, §6.3 rewritten; `docs/progress-decisions.md`; `CLAUDE.md`'s table |

Shown: stills of the cry at the porter, the waiter and a gull; the lunge through the luggage and
through a swinging door; the link at the gangway.

### Step 2. The real tangerine, and the pocket (no art)

| File | Change |
|---|---|
| `src/world/tangerine.js` (new) | `Loose`: an arcade body 8 px across, bounce 0.35, drag on a floor, colliding with the solid layer, the walks, the solids and the breakables; off the hull: a splash, gone; in a pool: it floats. At rest it becomes an ordinary tangerine on the floor, kept in the save (`save.loose`). Each frame it offers itself to what is near (`world.offered(t)`): the first to take it has it |
| `src/scenes/ShipScene.js` | `pocket(fromX, kind)`: with one on her and `?pocket=off` not set: one less, a `Loose` thrown the way she is pushed, the flinch (`flinchUntil`, input held a third of a second), `safeUntil`, the blink. Called at the top of `scareContact`; a hit inside `safeUntil` is ignored |
| `src/world/carry.js` | `spill(fromX, own)`: the pocket first, unless it is her own doing (`sway`, a melted cone) |
| `src/save.js` | `loose: []` in the empty save (old saves take the default; no new key) |
| `src/sfx.js`, `src/rumble.js` | `pocket` (the flinch), `roll`, `plop`; the rumble: the spill's light tick is reused, no eleventh moment |
| `tools/playtest.py` | A new scenario `pocket` (a hit with one: place and tray kept, the count down by one, the tangerine on the floor and picked up again; a hit with none: the fright as before; a fall not forgiven); `vacuum`, `falls`, `overboard`, `region1` run |

Shown: the flinch frame by frame beside the porter; the tangerine rolling off; the link.

### Step 3. The throw (art: one clip of hers, about 5 generations, asked first)

| File | Change |
|---|---|
| `src/controls.js` | `throw: 'F'`, Y on the controller; §3.1's table |
| `src/scenes/ShipScene.js` | `tryThrow(input)`: the roll, or the lob with ↑; a stand-in pose until her clip is approved |
| `src/world/*.js` | `offered(t)` on the things of §2's third column: the gulls' four classes, both vacuums, walkers, the kid, the robot, the trays, the piñata and the shelf things (a hit, not an offer), the hoops, the piano, Bumbot's bat back |
| `assets/source/her/throw/`, `tools/build_sprites.py` | Her underarm throw, skeleton-v3 by poses (the body only described; her fist found in every frame and the tangerine put in it, behind her fingers) |
| `tools/playtest.py` | A new scenario `throw` (a roll that nothing takes is picked up again; the vacuum chokes; a gull takes one; the piñata by a lob; Bumbot bats it back and the beat goes on); `gamepad`, `region2` (the promenade's gulls), `region6`, `region7`, `region8` for their gulls |

Shown: her throw's frames for approval before anything else; then each target as a short strip.

### Step 4. Region 1's decks (art: asked item by item)

The runaway suitcase (1 generation, or the atlas's suitcase on wheels drawn in code), the dog
(a character with a walk, a sit and a run: about 20), the lady knitting (a seated figure: about
10), the paper round's steward (about 13, optional), the climb (atlas pieces), the laundry's lock
(question 5), the first six doors that answer (sounds and marks; heads from the people's sheet
where one fits), the look-out at deck 4's stern (a porthole piece and the camera).

New classes in `src/world/movers.js`: `Roller` (the suitcase), `Fetcher` (the dog), `Skimmer`
(the papers), `Answer` (a door that answers), `Lookout`. Data in `tools/population.py`
(`ROLLERS`, `DOGS`, `ANSWERS`, `LOOKOUTS`), built by `tools/build_world.py`. Each new thing looked
at enlarged beside her (the nine questions of "Looking closely"), `tools/check_overlaps.py`
empty, `tools/check_corridors.py` (new) run. Playtests: `region1`, `boot`, `deck3`, `trunk`,
`ladder`, and a new scenario `deck4`.

### Step 5. The keepsakes (art: about 16 small things, a generation each, shown first)

`KEEPS` in `tools/population.py`; a kind `keep` in `world.js` (taken with E, or handed over by
what §4.2 says); `save.keeps`; the HUD's count beside the books (`Progression.buildHud`); the
day-after scene in cabin 8206 lays out those she found (`src/world/finale.js`). Playtests: a new
scenario `keeps`, `finale`, and each region's scenario where one is placed.

### Step 6. The ends and the hallways (art: three loads, about 3; heads for doors as needed)

The other look-outs; the rest of the doors that answer; the venues' answers; the three
deliveries (`LOADS` in `src/world/carry.js`, a source at each pantry end with `when` the fire
door is opened, the door that takes it). Playtests: `region5`, `region7`, `region4`, `region9`,
`sound`, and a new scenario `deliveries`.

### Step 7. Each deck its own look (art: one sheet of pictures, about 10, or drawn in code)

`tools/build_ship_map.py` (the plaques' band, the pictures by deck), the wallpaper's tint. The
whole ship rendered and looked at; `boot`, `stairs`, `lift`, `tools/check_overlaps.py`.

### Later, to decide after playing: the rounds and what they pay (§4.7)

### Cost

| | Generations |
|---|---|
| Steps 1 and 2 | 0 |
| Step 3 | about 5 |
| Step 4 | about 31, or 44 with the paper round |
| Step 5 | about 16 |
| Step 6 | about 3 to 9 |
| Step 7 | 0 to 10 |
| **All** | **about 55 to 85 of the 540 left** |

Each is an estimate; the real price is stated before each spend. Sounds are synthesised and
cost nothing, and **I cannot hear them**: every new one (the cry, the lunge, the flinch, the
roll, each door's answer) is the user's to judge on the soundboard.

---

## 6. Risks

- **She may run dry.** 53, three uses, and nothing grows back. Softened by the cry being free
  and by tangerines that roll being hers to pick up again; and the game is finishable with none
  (audit C10). If play shows her at zero for long, the lever is the lunge's and the pocket's
  price, not more fruit (which the user has ruled out for now).
- **The pocket may make frights rare.** That is its purpose, but it is the first thing to tune:
  how fast and how far the dropped one rolls decides how often it is lost.
- **The cry may be held down.** Each listener is deaf for eight seconds after being startled,
  and it costs her in four kinds of place.
- **Motion.** I see stills. The lunge, the flinch, the roll and the camera at a look-out are all
  judged in motion: each is shown plain first, and the user's eye is the test.
- **The story's tests.** Several scenarios use the dash (`dash`, `region1`, `region4`, `region6`,
  `region8`); each step names the ones it touches. The
  whole suite is not run (the standing rule).
- **"Nothing twice."** Every new thing above was checked against what is built; the three
  deliveries are one kind of errand with three loads and three rules, which is the closest the
  plan comes to the line. Say if it is over it.

---

## 7. Questions for the user

1. **The cry alone: free** (D standing still, or with her hands full; a tangerine only for the
   lunge, D on the move), which is what the plan assumes; **or every D costs one?**
2. **The cry from the start of the game**, the lunge still learned at the Seven Seas (assumed);
   or all of D from the Seven Seas, as today?
3. **The pocket on every hit** (assumed), or only when it saves a tray?
4. **The second collection: things for Bumbot** (assumed, §4.2), his loot returned, or more
   books with your titles? And is that what you meant by "the quest items should become
   rewards"?
5. May **the laundry on deck 4 open without a card** in region 1 (its tangerine not moved, only
   reachable sooner)?
6. May **the BOSUN's, the PURSER's and the DJ's doors answer the cry** (a parrot, coins, a
   beat)? The plates are your in-jokes.
7. **The throw on F, and Y on the controller?**
8. **No new ladder, and the rounds left for later** (§4.7): agreed?
9. Anything in §4.2's list or §4.3's two decks to drop before pictures are made (the dog and the
   paper round are the dear ones)?
