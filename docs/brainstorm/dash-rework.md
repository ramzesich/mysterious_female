# The dash, the tangerines and the rewards: a brainstorm in progress

Started 2026-11-14 on the user's word: "I want an analysis of the dashing mechanic in the game.
Right now, I'm not sure if it makes sense." **Nothing here is decided and nothing is built.** The
game still has the dash of `GAME_DESIGN.md` §3.2. Continue from "Where we stopped" at the end.

Everything below is read from the code and the world's data (`src/`, `maps/world.json`), not from
play; the timings are arithmetic, not measured in the browser.

## 1. What the dash is today

D, one tangerine, ten seconds at twice her run speed (280 px/s; `DASH` in `src/config.js`). It
cannot be stopped, a scare ends it, and it is off while she carries a tray, crawls or holds Bumbot.

| Obstacle | Placed | What the dash does |
|---|---|---|
| Breakables | 5: luggage on decks 4 and 9, the galley's crate, the crates on deck 11, the piñata | Smashed for good |
| Robot vacuums | 2: decks 4 and 9 | Sent spinning 4 to 6 s |
| The kid with the water pistol | 1 | Runs off and hides 10 s |
| The towel stack | 1 | Topples; at dash speed it lands behind her (not tested) |
| The librarian | 1 | Shushes her |
| Swinging doors, sprinklers, room-service trays, "Do Not Disturb" doors | 6, 5, 10, 7 | Nothing; she meets them at double speed |
| Porter's cart, jogger, buffet queue, chip spills, wet patch, gulls, stage light, gusts, boat drill, basketballs, flares, steam | about 20 | Nothing |
| Standing service carts | 9 | Nothing; solid |
| Stair blocks, ropes, card locks | all | Nothing |
| Bumbot | 6 beats | Nothing; he escapes at 300 px/s |

Why it does not hold together:

- Nine things of about eighty react; in the hallways of decks 8 to 10 it makes things harder.
- **The rewards are circular:** three breakables hide tangerines (7), the other two are shortcuts
  with a way round. Fuel is spent to get fuel.
- It is off where speed would matter: the errands are tray carries, two of them on a clock.
- It is learned at the Seven Seas, and the next job is a tray carry with it switched off; deck 4's
  luggage and vacuum are behind her by then.
- "Кісюнічка!!!" is her cry at cats, and Bumbot ignores it.
- The design doc promises more than is built: the porter's cart toppled, the sprinkler passed,
  "enemies" and room-service carts broken. None of that exists.

**The tangerines:** 53 on the ship (the doc says "about 30" and "about 40"), 46 of them reachable
without the dash; about eight places are worth a dash. They do not make the game easy, they mean
nothing: "scarce, each one counts" is not true as built.

## 2. The options first listed

1. **The shout becomes the power:** everyone and everything near her reacts for a few seconds.
2. Keep the dash and give it teeth (hazards bounce off her, a shorter burst, fewer tangerines).
3. **A tangerine forgives a scare.**
4. **Throw a tangerine:** it rolls; gulls chase it, the vacuum chokes on it, Bumbot bats at it.
5. Drop the fuel: a free sprint, tangerines as collectibles.

The user took 1 with 3, then asked about checkpoints, then asked for **1, 3 and 4 together, the 53
tangerines kept where they are, and the rewards rethought** ("Perhaps, the quest items should
become rewards, and we can add more of those").

## 3. What a scare costs today (the checkpoints)

- **Kept:** tangerines, cards, books, flags, broken things, lit checkpoints. Nothing is counted;
  hazards do not reset.
- **Lost:** her place, a dash in progress, a tray in her hands.
- **Time:** 2 to 3 s of fright and fade (by the code's timings), then the walk back from the
  nearest lit checkpoint: same deck first, then by distance, **in either direction**
  (`closestCheckpoint()` in `src/scenes/ShipScene.js`). 31 checkpoints.

| Deck | Hazards | Walk back, every checkpoint on the deck lit |
|---|---|---|
| 4 | porter's cart, vacuum | about 5 s |
| 6 promenade | jogger, three gulls | no checkpoint on the promenade itself |
| 7 | the casino's chip spills | 8 to 13 s |
| 8 hallways | trays, doors, a sprinkler | 2 to 11 s |
| 9 hallway | vacuum, towels, sprinklers, doors | 1 to 5 s |
| 10 midship hallway | trays, doors, a sprinkler | 15 to 25 s |
| 10 aft | trays, doors | 2 to 3 s |
| 11 | gulls, the wet patch, steam | 1 to 10 s |
| 12 | basketballs, flares | 4 to 9 s |

Three things the rule does:

1. **A scare can move her forward:** deck 9's sprinkler stands 173 px before a checkpoint door;
   with that door lit, being drenched puts her past the sprinkler.
2. **Only the first pass through a gauntlet bites** (the checkpoint ahead is not lit yet): deck 10
   midship up to about 40 s back, deck 8 aft about 20 s with four trays again.
3. A bump on the promenade puts her at the boat walkway's station on deck 7 once it is lit, at an
   inside checkpoint on deck 6 before that.

**The real setback is the spill.** With a tray a hit is a spill, and she walks to the source for
another: the lunch (the first carry) is about 60 s from the officer; a cone melts in 45 s; the
cake, the coffee and the cocktail are 15 to 30 s each way. A spill costs one to two minutes, a
scare a tenth of that. So a tangerine that forgives only a scare buys little: **it should save
her place and her tray on any hit.** A separate choice, not pressed: respawn at the checkpoint
last passed and not the nearest one (ends the forward skip; makes a scare dearer on return trips).

## 4. The proposal on the table: shout, throw, pocket

Each use has its own job: the shout for living things, a thrown tangerine for things out of
reach, a tangerine in her pocket for mistakes.

- **The shout (D, free, a few seconds of breath between cries).** "Кісюнічка!!!" with a
  one-second lunge, as in the design's first near-catch ("she lunges with the scream"). People
  and animals near her react for about three seconds; the lunge smashes what the dash smashed.
  With a tray: the cry without the lunge. Free, because with three uses 53 tangerines only hold
  out if the cry costs breath and not fruit, and because her own cry should be used gladly.
- **The throw (a new key, one tangerine).** It rolls a few metres. If nothing takes it she can
  pick it up again: a miss costs nothing.
- **The pocket (automatic, one tangerine).** On a hit she flinches, one rolls away and is gone,
  and she keeps her place and her tray, with a second of safety. With none left a hit is the
  scare or the spill it is today.

| Obstacle | Shout | Thrown tangerine | Pocket |
|---|---|---|---|
| Porter, jogger, buffet queue, waiter | Stop or step aside | | Saves the bump or the tray |
| The kid | Runs and hides, as now | | Saves the splash |
| Gulls | Scatter for a moment | Chase it: bait that lasts, and saves a cone | Saves the swoop |
| Vacuums | The lunge sends them spinning | Swallow it and jam until she has gone | Saves the fright |
| Crates, luggage, the piñata | The lunge smashes them | Knocks the piñata down from a distance | |
| "Do Not Disturb" doors, the Library | The cry wakes the guest or earns a shush: here it costs her | | Saves the startle |
| Sprinklers, swinging doors, flares, steam, basketballs, the boat drill, gusts, the wet patch, chips | | | The only answer besides timing |
| Bumbot | Freezes, ears up, for a beat | Bats it once, sniffs, pulls a face (cats dislike citrus) | |
| Long falls, overboard | | | Not forgiven |

About thirty timing hazards stay untamed, so the platforming stays; the pocket makes them gentle.

## 5. The rewards

A free lunge ends the circle by itself: nothing costs a tangerine to open, so **all 53 stay where
they are**, the seven behind crates and in the piñata too. A tangerine thrown at the piñata pays
three for one, which suits a piñata.

Still missing: a prize for effort that is not supply. "Quest items" read as things that belong to
a quest of their own, like the ten books (whose titles are the user's, so they cannot simply be
multiplied). A second collection, three candidates:

- **Things for Bumbot (recommended):** about ten small things at the effort spots (a toy mouse,
  a collar bell, a tin of sardines, a ball of wool, a cushion, a cardboard box). The HUD counts
  them like the books; in the day-after scene in cabin 8206 each one she found is there with him.
- **His loot, returned:** things he stole, handed in at a lost-and-found that fills like the
  library's shelf. Fits the chase; a second return quest of the books' shape.
- **More books**, if the user gives more titles.

Where they would go: where effort pays in tangerines or nothing today (the three crates and
luggage stacks, the piñata, the casino's jackpot) and three or four new throw targets (a gull that
drops what it holds for a thrown tangerine; a thing on a ledge too high to reach). Each tangerine
already there stays beside it.

**Cost, roughly:** 20 to 25 generations (a throw clip of hers, about ten small objects, each
shown to the user before it is placed); the shout's reactions mostly reuse clips. Code in four
steps, each shown before the next: the shout in place of the dash, the pocket, the throw, the
collection.

## Where we stopped (2026-11-14)

The user: "Save our brainstorming progress, we'll continue tomorrow." Asked and not yet answered:

1. The shout: free on a breath (recommended), or one tangerine each?
2. D keeps the one-second lunge with the cry (recommended), or the cry alone, with crates opened
   some other way?
3. The second collection: things for Bumbot (recommended), his loot returned, or more books with
   the user's titles?
4. Should a far meow answer the shout from the direction of his next appearance? Not a popup, but
   it softens "figuring things out": the user's to allow.

Also open, not yet asked as questions: the throw's key; whether the respawn rule changes (§3);
the full list of collection things and their places (to be shown with pictures first).

When it is decided: `GAME_DESIGN.md` §3.2, §6.1.2, §6.1.7 and §6.3 are rewritten, the decision and
its reasons go into `docs/progress-decisions.md`, and this file stays as the record of how it was
reached.
