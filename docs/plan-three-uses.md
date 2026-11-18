# Plan: three uses for a tangerine, and decks worth walking

**Settled with the user on 2026-11-15: every design question below is answered (§8 has their
words).**

**Revised with the user on 2026-11-16:** how she takes a hit (§1.6, "mishaps": each obstacle its
own, by the side it comes from and by who was moving), the tangerine's own picture and its
flight to the count (§1.7), and a general rule on art (Start here, 7). **Each step of §5 has
what the revision adds to it under "Revision (2026-11-16)", the built steps too: whoever builds
goes back over what is built, revises it and completes it** (the user: "You update each step
with their relevant additions. Even the built steps. The other session should revise what it
already built and complete it").

**Where the build stood when this was written (2026-11-16, branch `three-uses`):** steps 1 to 4
committed (the last `2ee244b`). **Next: the revisions of steps 1 to 4, then step 4a, then step
5.** `GAME_DESIGN.md` §8 has the latest.

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
   muted (`tools/playtest.py`'s `Browser`); what the generations cost said in each report (no
   asking first for pictures: `CLAUDE.md`, "Art"); every picture shown to the user, enlarged,
   before it is placed; no hint popups
   and nothing that points to where something is; no person, hazard, errand or reward used
   twice; nothing floats; doors and walls stop whatever moves, or a person opens the door
   (§1.8); failures are "scares"; every text in `src/lang.js` in both languages;
   record each change of plan with its reason in `docs/progress-decisions.md`.
5. Everything placed is a line of data in `tools/population.py`. **The user will move things
   while play testing** ("I will fine tune it while play testing"): keep each placement one
   line, easy to move.
6. Numbers (speeds, reaches, times) are first guesses to be tuned by play, all in
   `src/config.js`.
7. **Art is generated (the user, 2026-11-16): "use generations instead of attempting to draw by
   itself, or reuse part of props from other scenarios."** A new thing, figure, pose or gag is
   made with PixelLab: not drawn in code, and not put together from pieces of props that were
   made for another scene. A person with a thing is one generated clip or picture (`CLAUDE.md`,
   "Art"). Drawing in code stays for what is flat by nature (a coloured band, a wash, a rope's
   line, a jet of water) and for the rooms already drawn that way. Add the rule to `CLAUDE.md`'s
   "Art". What steps 1 to 4 drew in code or put together from other props is listed, shown to
   the user and made again (step 4's revision).

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
- PixelLab: 4,939 generations left on 2026-11-16 (the user upgraded the subscription; the
  allowance refills on 2026-12-16). There were 540 on 2026-11-15.

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

- A hit that would send her back or spill her tray, with a tangerine on her: she takes it with
  a short reaction that fits the hit and the side it came from (§1.6; about half a second),
  blinks for a second and a half during which nothing can touch her, **and keeps her place and
  her tray.**
- **The tangerine is knocked out of her pocket and rolls away fast, ~~the way she is thrown~~
  (§1.6): ~~on ahead of her after a hit from behind, back the way she came after a hit from the
  front~~ always behind her, back the way she came, whichever way the hit throws her** (the user,
  2026-11-17: "It would place a dilemma: run back to pick it up, or continue moving to the initial
  destination"). It is the same real thing as a thrown one: she can run after it, and whatever wants it
  may get there first. Two hits take it for good: a gull that comes down on her flies off with
  it, and at a "Do Not Disturb" door she holds it out as an apology and a hand takes it.
- With none on her, a hit is a mishap with a gag of its own, and then her checkpoint (§1.6).
  Falls, the sea and a cake that wobbles over by her own feet are never forgiven.
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

### 1.6 Mishaps: how she takes a hit (the user, 2026-11-16)

The user, while step 4 was being built: "replace some frights with slips, trips, and falls";
then "replace frights with more proper mechanics leading to either a respawn or to a tangerine
loss"; on a first proposal, "You're reusing the slips too much. We have a lot of PixelLab
generations ... and I want us to use them. Add more variety"; and on the second, "What happens
when she is facing a moving object, versus when she is hit with it from behind (like: fall
forward vs fall backwards on her bottom). What happens when she stumbles on an object while
moving, versus when an object hits her while she's standing".

**The outcome does not change:** with a tangerine on her, one is lost and she keeps her place
(§1.3); with none, she goes back to her checkpoint. **What changes is what is seen.** "A fright,
then she runs off the screen" stays only where she is truly embarrassed (the "Do Not Disturb"
doors, the occupied balcony). Everywhere else:

- **with a tangerine on her: a short reaction** (about half a second) by the kind of hit and
  its side;
- **with none: the obstacle's own gag** (about two seconds), then the fade and her checkpoint.
  **During a gag the keys do nothing and it cannot be cut short** (the user: "No, during the gag
  the movement keys have no effect").

**What decides how she goes down.** Two facts are read at every hit: **which side of her it is
on** (front is the way she faces) and **who was moving** (she ran into it, it came at her, or
both).

| The hit | She goes |
|---|---|
| She runs into a low thing that holds | Forward, over it |
| She steps on a thing that slides her way | Backward: her foot goes on ahead |
| A thing slides against her foot | Forward: her foot is taken back |
| A waist-high thing, and she runs into it | Forward, onto it: the momentum is hers |
| A waist-high thing hits her as she stands facing it | Backward, on her bottom: the momentum is its |
| A seat-high thing reaches her from behind | She sits down onto it, and it carries her |
| A head-high thing from the front | Backward |
| A head-high thing from behind | Forward |
| From above, a cloud, or an embarrassment | No side: one gag |

She runs at 140 px a second or stands. Slow things (the porter's cart 48, the jogger 106, the
suitcase 53 at its fastest) reach her back only while she stands; fast ones (the deck chair
235, the vacuum's dart, the light, the door, the balls, the jet) can catch her running.

**Each obstacle with a side, by scenario** (the gag is what plays with none on her):

| # | Obstacle | Scenario | The gag |
|---|---|---|---|
| 1 | Casino chips (3) | She runs onto them | On her bottom, butterflies (built). Standing on them: nothing (built) |
| 2 | The dog's lead | She runs into it | On her belly, butterflies (built); **the dog comes and licks her face**. **With tangerines on her too: down, back to her checkpoint, none lost** (`pocket: false`, the user, 2026-11-17: "She has to fall here anyway, tangerines or no") |
| 3 | Trays on the floor (10) | She runs onto them | **A tray shoots on ahead with her on it**, arms wheeling, out of the screen; a crash; the door opens on the guest looking after her |
| 4a | A sliding paper | ~~It slides her way~~ **At her front: sliding at her, standing or running, or lying where she steps** | ~~She sits down; the paper flutters open over her head like a tent~~ **Her leg flies up behind her with the paper on its sole, she lands on her belly, the paper comes round and down onto her back** (the user, 2026-11-16; built 2026-11-17) |
| 4b | | ~~It slides against her~~ **At her heel, from behind** | ~~Down on her belly, chin on her hands; the paper settles on her back like a blanket~~ **Her heel is taken forward and up with the paper, she sits down hard, the paper comes round over her and lands on her head as a tent** |
| ~~4c~~ | | ~~She stands still~~ | ~~Nothing: it stops against her shoe.~~ **Gone (the user, 2026-11-16): she slips on a paper standing too** |
| | | **The user's revision (2026-11-16, after trying the first 4a and 4b in the game: "It doesn't work at all")** | **From behind: the paper slides on under her foot, that leg goes up with the paper following it round in a circle, she falls on her bottom and it covers her as a tent. From the front: she falls on her belly, that leg up behind her, the paper following it round and covering her from above. She slips on a paper even standing (no more 4c). The sliding paper is generated, near the size of the open one.** Built 2026-11-17 (the rows above), the paper sliding at a steady speed right to her foot |
| 5a | Robot vacuums (decks 4 and 9) | It comes at her front, or she runs into it | ~~Forward over it, on her belly across it; it bumps her side twice and trundles home. "Eeek!"~~ **As 5b: she rides it off** (the user, 2026-11-16: "I prefer the ride in all cases"), turned round onto it, the way it was going |
| 5b | | It catches her from behind | **She sits down on it and it carries her off down the corridor**, like a cat on one. **"Weeeee!"** (see the words, below) |
| 6a | The runaway suitcase | She runs into it | ~~Over it; it pops open; she sits up in someone's sun hat~~ **As 6b: she rides it** (the user, 2026-11-16); standing at an end of its roll, it sets off for the other end with her |
| 6b | | It rolls into her back as she stands | She sits on it and rides to the end of its roll, where it creaks and tips her off |
| 6c | | She stands facing it | ~~Nothing: she stops it with her hands and it rolls back~~ **As 6b: she rides it** (the user, 2026-11-16), turned round onto it; with a tangerine on her, thrown back (her reel) |
| 7a | The deck chair on the wet patch | Head-on (she slid in from the forward end) | Face first onto it; it folds flat and she sledges on it across the tiles |
| 7b | | From behind (she slid in from the aft end) | Scooped up seated; it folds shut on her, her feet out |
| 8a | The porter's cart | She runs into the cart | Folded over its bar, draped on the bags, legs kicking |
| 8b | | It pushes into her as she stands facing it (he cannot see over the bags) | She back-pedals before it and sits down |
| 8c | | It reaches her back as she stands | She sits into the luggage with a bag on her lap; he wheels her two metres, sees her, tips his cap |
| 8d | | She runs into his back | She bounces off him and sits; he turns round |
| 9a | The jogger | Head-on, both running | Twirled like a top, spirals over her head, she sits |
| 9b | | He runs into her as she stands facing him | Bowled back onto her bottom; he jogs on the spot, sorry |
| 9c | | He runs into her back | Shoved into three flailing steps and a belly-flop |
| 9d | | She runs into his back | She bounces off and sits (8d's clip); he never notices |
| 10a | The breakfast stewardess with a tray | She runs into the tray | She sits back with the breakfast on her: toast on her head, the flower behind her ear |
| 10b | | The tray meets her back as she stands | ~~Juice down her collar: she arches and dances on the spot, pulling her shirt off her back, and squelches off~~ **As 10a, turned round to face the tray** (the user, 2026-11-17: the squirm looked weird, and the case is rare) |
| 10c | Her trolley (the user, 2026-11-17: most of her round she wheels it) | Into it with no one just past it (parked at a door) | She trips over it head first and lands on her belly past it |
| 10d | | Into it, or it wheeled into her front, the stewardess just behind it | Bumped back off it, she sits (8b's clip): over it she would land on the stewardess |
| 10e | | It reaches her back | She trips forward, away from it, dazed a moment (her own trip) |
| 10f | | She runs into the stewardess's back, her hands empty | She bounces off and sits (8d's clip); the stewardess turns round |
| 11a | The kid's water jet | In her face | Sat back, spluttering, wringing her hair; he points and laughs |
| 11b | | In her back | As 10b: she arches, dances, squelches off |
| 12a | The stage's swinging light | From the front | Her head back, two spins on the spot, stars circling, she sits |
| 12b | | From behind | Three stumbling steps, down on her hands and knees, stars |
| 13a | A swinging door (6) | It opens in her face (she faces the door) | **Flattened against the wall behind it;** it swings shut, she peels off and flutters down |
| 13b | | It catches her just past it (her back to it) | Swatted forward: a belly-slide along the carpet, chin first |
| 14a | A basketball | In her face | She tips over backward, stiff as a skittle |
| 14b | | On the back of her head | She topples forward, stiff as a plank |
| 15 | The boat drill's boat | From above | Pressed down to half her height, a waddle, she springs back up and sits |

**Those with no side, one gag each:**

| # | Obstacle | With a tangerine | The gag |
|---|---|---|---|
| 16 | Sprinklers (5) | She shivers (built); it slips from her wet fingers | Her hair plastered over her face, a sneeze, she squelches off to change |
| 17 | The sauna's steam | She coughs and fans it away | Out of the cloud with her hair frizzed into a huge puff; she fans herself and swoons |
| 18 | The towel stack | She bats the towels off | Buried; her head comes up in a towel turban, a towel swan sitting on top |
| 19 | Teppanyaki's flares | She yelps and pats out a smoking sleeve | A sooty face, her hair on end and smoking, two white eyes blink, a puff of smoke coughed |
| 20 | The gulls on the balcony rails | She ducks; **the gull takes the tangerine and is gone** | The gull lands on her head and stays; she runs off flailing with it sitting there |
| 21 | The funnel's gulls, on the stairway | She ducks; the gull takes it | She bumps down the flight on her bottom, step by step, to its foot |
| 22 | The gulls across her glide | She ducks; the gull takes it | The parasol turns inside out, and she falls (the fall as built) |
| 23 | "Do Not Disturb" doors (7) | **She holds a tangerine out in both hands, her head bowed; a hand takes it and the door shuts** (spent, not rolling) | "Oh, sorry!": both hands over her eyes, blushing, she tiptoes off fast, out of the screen |
| 24 | The occupied balcony | As 23: whoever is on it takes the tangerine | As 23 |

**Unchanged:** a fall of more than a deck, the sea and its life ring, a tray spilled (it flies,
she fetches another; the pocket saves it), and everything that never sent her back (the
delivery robot, the steward on his rounds, the buffet queue, the old lady, the ball pit, the
gusts, the laundry lines, the gulls that take food, the waiter).

**The rules that go with the tables:**

- **With a tangerine on her, the same side picks her short reaction:** thrown back, she reels a
  step (a slip: her caught-backwards, built); pushed on, she stumbles a step (built). A door in
  her face: she rubs her nose. Water in her face: a splutter; on her back: she arches. Heat: a
  yelp. From above: she ducks. ~~**The tangerine flies the way she is thrown.**~~ **The tangerine
  rolls off behind her whatever the side (§1.3; the user, 2026-11-17).**
- **With a tangerine on her she is never sat onto a thing or carried by it:** a ride is only
  for the gag with none.
- **A hit while she is in the air** uses the same rule; the gag starts when she lands.
- **With a tray in her hands** nothing changes (the tray flies, no checkpoint); with a
  tangerine on her the reaction follows the same rule.
- **In a lunge** nothing changes (§1.1, §2): she is through, and there is no mishap.
- **The four gags that carry her off** (3, 5b, 6b, 20) are each one picture of her with the
  thing: the world's own tray, vacuum, suitcase or gull is hidden while the clip moves, and is
  back in its place when she steps out of her door.
- ~~**4c makes the papers gentler on purpose:** a slow thing she is looking at does not knock her
  over. She still has to hop them to get past.~~ (The user, 2026-11-16: she slips on a paper
  standing too; the papers slide fast and steady, so a slip convinces.) (6c did the same for the suitcase until the user
  tried the ride from every side, 2026-11-16: "I prefer the ride in all cases": the vacuum and the
  suitcase carry her off whichever side they reach, the gag's picture facing the way it goes.)
- **The words over her head** stay as they are for each kind of hit, in both languages. One
  changes, the user's: "Update the wording with fright/excitement, like 'Weeeee!' or
  something": the vacuum's ride (5b) is **"Weeeee!"** («Уіііііііі!», the user, 2026-11-17); over it on her belly (5a) she
  keeps "Eeek!". A gag that needs a word of its own gets one in `src/lang.js`, in both.

**In the code** (names are suggestions):

- `scareContact(fromX, what, { vx = 0, force = false })`: `what` is the obstacle's own name (a
  key of `MISHAPS`), no longer a word shared by several; `vx` its speed along the deck, so that
  who was moving can be told. `Carry.spill` passes both on.
- One helper for the two facts: the side from her facing and `fromX`; she is moving when her own
  speed toward it is over 20 px a second, it is when `vx` toward her is over 5.
- `MISHAPS` in `src/config.js`: per obstacle, which scenario each side and mover gives; per
  scenario its word, her reaction's clip, her gag's clip, how the gag ends (a fade where she
  is; out of the screen; a fall) and what the other party does (the dog's lick, the porter's
  cap). One line each, as everything in this plan.
- One function plays a gag in place of the run-off and of `scareDown`; `pocket()` takes the
  reaction from the same table.
- `world.lunged()` gets the same names.

### 1.7 The tangerine itself (the user's own two, 2026-11-16)

- **"Rework the tangerine sprite to make it a bit more detailed and look like a tangerine."**
  It is 8 px today, drawn from rows of letters (`tangerine` and its two bitten states in
  `src/textures.js`; a copy in `tools/draw_rooms.py`, `TANGERINE`). A new one is generated
  (Start here, 7): a fruit a little flatter than round, the dimple and a small green leaf at
  its stalk, a highlight, a speck or two of the peel's pores; about 10 to 12 px, so that it
  still sits in her fist. **The user chooses from candidates shown enlarged and numbered:** on
  a floor beside her, in her fist, in the HUD. Everything that shows a tangerine then follows
  the chosen one: the pickups, the loose one (it turns as it rolls), the HUD's icon, her toss's
  fist (`tools/hold_tangerine.py`), the two bitten states, the ones painted into rooms
  (`game_tangerine()`), the people's bubbles that show one, the ball pit's and the piñata's.
- **"Collected tangerines should fly into her tangerine meter above."** On every pick-up (one
  in its place, a loose one, one handed back, the piñata's three, the bowl's): its picture
  flies from where it was to the HUD's tangerine in about 0.4 s, along a small arc, coming down
  to the icon's size; **the number changes when it lands** (the save changes at once: only what
  is shown waits), and the icon gives a small bump. It flies on the HUD's own layer, fixed to
  the screen, from the screen's point where it lay. Several at once follow each other 80 ms
  apart. With `?tangerines=infinite` it flies all the same. A tangerine spent does nothing new.

### 1.8 Doors and walls stop everything that moves (the user, 2026-11-17)

"I want the corridor doors (and walls, where relevant) to serve as natural obstacles not only for
the player, but for moving NPCs and moving objects too. If it makes sense for a given moving NPC
to open a door on their path and walk through, then they should do that. If not, the door should
stop them (before the door, not while they're already on top of the door). Moving obstacles are
just stopped before doors."

A door across a deck is a bulkhead's (the glass doors between the ship's parts, the deck doors,
the spa's, the bridge's, the sauna's); a wall is the solid layer at a body's height. Built into
the ship scene (`stopShort`, `spanOn`, `doorAhead`, `mayOpen`, `holdDoor`, `letGoDoor`) and used
by everything that moves, so that a later step only has to call them:

- **A thing that moves by itself stops short of the door's face, shut or open** (one she holds
  open would shut on it), never on top of it: a span (`spanOn`) for a thing that goes to and fro
  (the robot, the suitcase, the dog's lead), `stopShort` for a single move (the vacuum's dart, a
  lunge sending the suitcase or the porter's cart rolling, her ride on the vacuum, which ends at
  the door with a bump and her checkpoint). Loose tangerines already bounce off a shut door
  (`src/world/tangerine.js`).
- **A person walking a loop opens a door with no lock** (`people.js`, `door()`): half a second at
  its handle, the door opens (its sound), they go through holding it, and it shuts once their
  back (and their cart's) is past and she is away. The porter on deck 4 does it at 60 m.
- **A locked door turns a person back short of it** as at an end of their walk (a card, one way,
  a rope, the story's block): one held open would let her past a lock.
- **A round that is one corridor's work** (the paper rounds, the breakfast round, the steward on
  deck 8) is kept to its side of any door: their cabins are all on one side.
- **A scripted scene that walks people through a door opens it** (`setBulkheadOpen`, `ajar` while
  they pass: the wedding party into the chapel).
- **Placing a mover** (§5's steps): give it a span on one side of a door, or a walking person
  whose door has no lock; never a thing set to cross a door.
- Bumbot's ways out already keep it (looked at 2026-11-17): at near-catch 2 the rope stand he
  knocks swings deck 6's 194 m door open and he runs through it, off the screen; at near-catch 5
  he runs off the screen along the pools and is gone there, some 24 m short of deck 11's door
  (its data's `exitX`, 170 m, is not used by the pool's own scene).

---

## 2. What each thing does

`·` = nothing. Built today: the breakables, both vacuums' spin, the towels, the kid's flight, the
librarian's shush. The rest is new.

**The last column** says whether the pocket forgives the hit. How she takes it, with one on her
and with none, by its side and by who was moving, is §1.6 (2026-11-16).

| Thing (where) | The cry | The lunge | A tangerine rolled or lobbed at it | A hit with one in her pocket |
|---|---|---|---|---|
| The porter and his cart (4) | Stops dead, pulls the cart to the wall for 3 s: she passes, tray and all | The cart is knocked rolling 2 m, he runs after it | He stops to pick it up, peels it by the wall (10 s clear). Spent | Forgiven |
| The waiter (5) | Freezes with his tray up: she passes with hers | · | Stops, pockets it. Spent | Her tray saved |
| The jogger (promenade) | Jogs on the spot, looking round, 3 s | Spun round like a top | Hops it without a look | Forgiven |
| The steward on his rounds (8) | Pulls his cart in at once, as at a knock | · (solid) | Stops and puts it on his cart, hers to take back with E. Not spent | · |
| The buffet queue (11) | They turn aside against the tables, as for a tray | · (solid) | · | · |
| The kid with the water pistol (11) | **Draws his fire**: he turns and squirts at once | Runs and hides (built) | Catches it, eats it, back turned 15 s. Spent | Forgiven |
| The dog on the lead (4, new) | Howls back, runs to its owner and winds the lead round her legs (their picture): nothing to trip on until 5 s after the cry, and it unwinds | Jumps aside | **Fetches it and brings it back.** Not spent | Forgiven: a stumble, and the dog fetches the tangerine back (§1.6, 2) |
| The paper round's steward (5, new) | Drops the bundle and stands aside | Through the papers | Catches it, stands aside to eat it. Spent | Forgiven |
| Anyone else (the ambient cast) | Turns to look; a `♥` over the few who like cats, a finger to the lips in quiet places | · | Looks at it | · |
| The librarian | The shush (built), and the "QUIET PLEASE" sign rattles | The same | · | · |
| "Do Not Disturb" doors (7) | **Within 3 m the door opens on someone not dressed for visitors: "Startled"** | · | · | Forgiven: she holds it out as an apology and a hand takes it (§1.6, 23). Spent |
| Trays on the floor (10 places) | · | Scattered with a clatter; the door flies open after she has gone | Rolled into them: the clatter, the door opens on nobody, the trays safe to cross while the guest looks about | Forgiven: a stumble with a clatter. The door is no longer the fright (§1.6, 3) |
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
| Gulls on the balcony rails | Off the rail 6 s without swooping | Missed | Goes for it: that balcony is safe until she is past. Spent | Forgiven: the gull takes it (§1.6, 20). Spent |
| The funnel's gulls; the bow's flocks | Break off; the flock lifts and settles | Missed | One goes after it: no swoop for 10 s. Spent | Forgiven: the gull takes it (§1.6, 21, 22). Spent |
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
- **The fourteen titles are given (the user, 2026-11-18)**, earlier than "once the game is
  tested": GAME_DESIGN.md §6.1.2 has them, each in its own language and script, with its author.
  **A title shows in two places:** the book's cover over a slightly dimmed screen, in its centre,
  when she gets the book; and the shelf seen close (E at it), over the whole screen. **Every
  cover is generated and different from the others; the shelf's close view is generated too.**
  The lettering is drawn in by the build (Latin with Polish letters, Cyrillic, Hebrew). The four
  new books' pages stay plain (a picture, no hint) until the user says otherwise.
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
| 17 | Book | נערה במעיל כחול (book 11) | The boat walkway, its end beyond the boat drill | E | Region 7 |
| 18 | Book | Poczwarka (book 12) | Deck 8 midships | The thanks for the flowers | Region 7 |
| 19 | Book | Daughters of Warsaw (book 13) | Deck 10 midships | The thanks for the tea | Region 7 |
| 20 | Book | Pachinko (book 14) | Deck 9 forward, the end of the officers' corridor | E | Region 9 |

Each place is set against what is built there before it is fixed (the lesson of 2026-11-14),
and each small picture is shown to the user first. The five breakables and the jackpot keep
their tangerines and get nothing more.

### 4.2 Region 1, the user's finding (C1): all seven kept

"I have just run through the deck 4, and it's almost completely empty." Metres are "about".

**Deck 4**

| m | What |
|---|---|
| 38 to 46 | **A runaway suitcase** on its wheels, rolling to and fro between two door frames with the ship's slow roll; a creak before it turns. Hop it (§1.6, 6) |
| 53 to 64 | The porter (built), with his new answers (§2) |
| 86 | **A small dog on a long lead** across the corridor, its owner in the doorway (an existing figure). The lead is a line to hop: run into, a trip (§1.6, 2). It fetches a rolled tangerine and brings it back; three fetches and the owner hands over the tennis ball. It barks at the vacuum when it comes near |
| 118 to 150 | The vacuum (built), with its new answer |
| 140 to 146 | **The climb:** a service cart, a linen cage and a shelf under the ceiling as three steps up, the feather on the shelf, the vacuum passing underneath |
| 250 | A look-out (§4.3) |

The laundry and the dry store stay behind the green card (the user: "No").

**Deck 5**

| m | What |
|---|---|
| 20 | A look-out (§4.3) |
| 22 | **A lady knitting in an open cabin**, her basket by the door with the ball of wool |
| 34 to 46 | **The paper round:** a steward skims folded newspapers along the carpet to each door; he licks a finger first. Hop them (§1.6, 4) |
| 146 | Her flag at Shore excursions' desk |
| 170 to 192 | The waiter (built): on the lunch errand the cry is what gets her tray past him |

Built in step 4 beyond these tables, on the user's rounds of review (`docs/progress-decisions.md`
has each): a second paper round where deck 5's forward cabins meet the stair hall (57.5 to
72 m), and the breakfast round (deck 5, 44.9 to 52.9 m: a room-service stewardess with a
trolley, carrying a tray to each door). Their mishaps: §1.6, 4 and 10.

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
- **Each deck its own framed pictures between the doors, generated** (revised 2026-11-16: they were to be drawn in code; step 7's revision)**:** deck 4 safety posters
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

**Revision (2026-11-16); step 1 is built, so this is gone back over:**

- `world.lunged(kind, fromX)` and every `lunged()` take the obstacle's own name (§1.6's
  `MISHAPS` keys) where they took the shared word. The lunge's rule is what it was: she is
  through, no mishap.
- The cabin's bowl: its three follow the new tangerine (§1.7), and so does every tangerine
  painted into a room (`game_tangerine()` in `tools/draw_rooms.py`); the rooms' pictures built
  again and the crew cabin looked at enlarged, full and emptied.
- `src/lang.js`: the vacuum's ride, "Weeeee!" / «Уіііііііі!» (§1.6).
- Run again: `dash`, `deck3`, `intro`, `lang`.

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

**Revision (2026-11-16); step 2 is built, so this is gone back over:**

| File | Change |
|---|---|
| `src/config.js` | `MISHAPS` (§1.6): one line per scenario. The dazed wait and each gag's length with it |
| `src/scenes/ShipScene.js` | `scareContact(fromX, what, { vx, force })`; the helper for side and mover; `pocket()` takes her reaction from the table and throws the tangerine the way she is thrown; one function plays a gag (it takes the place of the run-off and of `scareDown`), ends it as its line says, and keeps the keys dead until the fade. The run-off stays for 23 and 24 only |
| Every caller of `scareContact` and `Carry.spill` (28 places in `movers.js`, `hazards.js`, `outside.js`, `topdeck.js`, `bow.js`, `lido.js`, `world.js`, the ship scene) | Its own name and its speed passed. Their gags come with steps 4 and 4a: until a gag's clip is approved the built fall on that side stands in (on her bottom, on her belly) |
| The gulls' classes, `DndDoor`, `Occupied` | With a tangerine on her the gull takes it (`world.gullTakes()`), and at a door or the balcony it is handed over: spent, never loose |
| `assets/source/her/`, `tools/build_sprites.py` | **Her six new reactions** (reel, rub her nose, splutter, arch, yelp, duck) **and the apology** (a tangerine held out in both hands, head bowed): seven clips, about 25 generations; each shown enlarged first |
| `src/textures.js`, `tools/draw_rooms.py`, `tools/hold_tangerine.py`, `tools/build_things.py` | **The new tangerine** (§1.7): candidates to the user (about 5 generations), then everything that shows one follows |
| `src/scenes/ShipScene.js` (the HUD), `src/world/tangerine.js`, `src/world/outside.js` | **The flight to the count** (§1.7) at the three places a tangerine is added to her (`save.tangerines += 1`) and wherever else one is given |
| `src/sfx.js` | A reaction's and a landing tangerine's sounds, each in its group with its line; the user judges them on the soundboard |
| `tools/playtest.py` | `pocket` grown: a hit from the front and one from behind give the reaction and the tangerine's way of §1.6; a gull takes it; at a "Do Not Disturb" door it is handed over and not on the floor; with none a gag plays, the keys do nothing during it, and she is at her checkpoint after; the number changes when the flying tangerine lands. Run with it: `vacuum`, `dash`, `lang`, `boot`, `sound`, `gamepad` |
| Docs | `GAME_DESIGN.md` §5.6 written again (mishaps in place of "a fright, then she runs off"), §3.2; `CLAUDE.md`'s table and its "Art" (Start here, 7); `docs/progress-decisions.md` |

### Step 3. The throw (art: one clip of hers, about 5 generations, asked first)

| File | Change |
|---|---|
| `src/controls.js` | `throw: 'F'`, Y on the controller; `GAME_DESIGN.md` §3.1's table |
| `src/scenes/ShipScene.js` | `tryThrow(input)`: the roll, or the lob with ↑; a stand-in pose until her clip is approved |
| `src/world/*.js` | `offered(t)` on the things of §2's fourth column |
| `assets/source/her/throw/`, `tools/build_sprites.py` | Her underarm throw, skeleton-v3 by poses (only the body described; her fist found in every frame and the tangerine put in it, behind her fingers) |
| `tools/playtest.py` | A new scenario `throw` (a roll nothing takes is picked up again; the vacuum chokes; a gull takes one; the piñata by a lob; Bumbot bats it back and the beat goes on). Run with it: `gamepad`, `region2`, `region6`, `region7`, `region8` |

Shown: her throw's frames for approval before anything else; then each target as a short strip.

**Revision (2026-11-16); step 3 is built, so this is gone back over:**

- The new tangerine (§1.7) in her fist in the toss's frames (`tools/hold_tangerine.py` run
  again; her clip itself stays) and as the thrown one, turning as it rolls.
- A thrown tangerine picked up again flies to the count like any other (§1.7).
- Where §2's fourth column has someone catch or take it, nothing changes.
- Run again: `throw`, `gamepad`.

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

**Revision (2026-11-16); step 4 is built, so this is gone back over:**

- **Region 1's mishaps, each by its scenarios (§1.6):** the dog's lead (2, and the dog's lick),
  the papers of both rounds (4a, 4b, 4c: a paper stopped by her shoe short of its door fades
  away, no hand takes it), deck 4's vacuum (5a, 5b), the suitcase (6a, 6b, 6c), the porter and
  his cart (8a to 8d, and his tip of the cap), the breakfast stewardess (10a, 10b).
- **Art, each shown enlarged before it is placed:** twelve gags of hers (4a, 4b, 5a, 5b, 6a,
  6b, 8a, 8b, 8c, 8d, 10a, 10b), the dog's lick, the porter's cap: about 70 generations.
  **Done (2026-11-16): 5b and 6b, and with them 5a, 6a and 6c, which ride too** (the user's
  word after trying it); the vacuum, made smaller, and the suitcase are cut from the same pictures.
  Left: the dog's lick (4a, 4b done, below; it waits for an idea of the user's, to be talked
  over at the end of this step, 2026-11-17). **The breakfast stewardess done (2026-11-17):** 10a
  and 10b, and her trolley's 10c to 10f added at the user's word (the table above): `fallGag`
  (`GAGS` trayFront, trayBack, trolleyTrip, trolleyPush, trolleyBounce; 10e her own trip, dazed
  1.2 s), always on the corridor's floor; the trolley a hit, not a thing that waits for her; she
  wheels it by its handle, and a tray she hands in shrinks a little and is gone
  (`assets/source/her-mishaps/README.md`). **The porter's cart done
  (2026-11-17):** 8a to 8d and his tip of the cap, clips of her from her own sprite beside the
  game's own cart (`assets/source/her-mishaps/README.md`), played by the ship scene's `cartGag`
  (`GAGS` cartDrape, cartPush, cartSit, cartBounce): the cart's clips set down where she stands
  and the world's cart hidden; her alone for 8b (the porter pushes on, his cart's front at hers)
  and 8d (he walks on a step or two, then turns round); 8c's ride two metres and his cap;
  doors and walls stop him (§1.8). **The papers (2026-11-16,
  under way):** a first 4a (sat, a tent) and 4b (on her belly, a blanket, the paper from behind)
  were approved as clips and put in the game (`fallGag` in the ship scene, a stopped paper fading
  for 4c, the start place `deck5`); the user tried them and asked for them again by the paper's
  side (the revision under the table above). **Done 2026-11-17:** the sliding newspaper
  generated (`things/paper-sliding.png`, the user's B at 10 px), the two clips made from her
  standing on it, its slide steady to her foot (approved in the game).
  The
  first to be made and shown are 5b and 6b (her on the vacuum, her on the suitcase): they tell
  whether a picture of her riding a thing holds up.
- Her gags go on a sheet of their own (`assets/sprites/her-mishaps.png`, its own cell, her
  feet at its bottom row as on her sheet), so that her main sheet stays within a texture's
  size (`boot` checks it).
- **The art rule looked back over (Start here, 7):** list what steps 1 to 4 drew in code or put
  together from parts of other props (the things on the climb, the knitting lady's basket, the
  breakfast trolley and its tray, the papers, anything else found), show the list to the user
  with a close-up of each, and make again with PixelLab what they point at.
- `deck4` grown: each scenario above set up by where she stands, which way she faces and
  whether she moves, the right gag asked for, her checkpoint after; 4c costs nothing; with
  a tangerine the reaction and the tangerine's way. Run with it: `region1`, `pocket`, `boot`.
  **The art rule looked back over (2026-11-17):** steps 1 to 4's pictures drawn in code made
  PixelLab's (`assets/source/things/`, its `tries/README.md`): the four other desk flags, the
  climb's shelf and its laundry cart (the linen room's had stood in), the knitting lady's
  basket, the hand a cabin door puts out, the cry's heart; the cry's "shh" a speaker crossed
  out (a finger to the lips never read at a bubble's size); the feather a cat teaser lying on
  the shelf, its handle purple. The view into her cabin stays drawn, like the rooms (the
  user). With it, at the user's word: the climb a laundry cart and a shelf, the gap between
  them a jump from the cart's edge; the lady in the bathrobe an obstacle (10f's bounce,
  `robe`); and the tangerine knocked out of her pocket always rolls behind her (§1.3).
  **The dog and its owner made again together (2026-11-17)**, the user's idea for the dog: the
  mechanic kept, the pictures new ("the lady and the dog are loosely connected, the leash looks
  weird and glitches on its connecting ends"). One picture of the two (a new owner, `dogowner`,
  in her doorway holding the lead's loop, the dog at her feet), cut apart by hand; the dog made
  a character from it standing, its walk and sit animated from its own picture, its run the dog
  template in skeleton-v3; her idle her fist still on the lead
  (`assets/source/people/dogowner-raw/README.md`). The lead drawn by the game in the picture's
  own colours, 2 px (the picture's 3 "too thick"), from her fist to the collar as measured in
  every frame, under her fist and over the dog's back, hanging down to 3 px over the carpet at
  the spot she trips on (a little over halfway from her hand to the dog, as always: at her
  waist it "cannot trip her"). With it: lying flat after a trip she is drawn 2 px lower; her
  running footsteps on the frames her feet land on; everyone's clips set on the floor frame by
  frame. **Then their together clips (2026-11-17)**, the moments the two are close, each one
  picture of them (the dog sprite and the drawn lead hidden while it plays; `WIND`, `TOSS`, `LICK`
  in `src/world/movers.js`): her cry, and the dog runs to its place at her feet in their picture,
  winds the lead round her legs, they stand tied until 5 s after the cry, it unwinds it, their
  picture held while it sits, and it trots off away from her (nothing to trip on all the while);
  three fetches, and she takes the tennis ball out of her pocket and tosses it, her lead fist still,
  the ball the clip's while she holds it and the game's from the frame her hand opens, a lob to her
  chest, in front of her as it reaches her (the user); a trip on its lead, and it runs to her face
  and licks it, one picture of her lying dazed and the dog, the lead to its collar there, over the
  dog when its owner is on that side and from under her when not; her checkpoint waits for it.

### Step 4a. The mishaps on the rest of the ship (art: about 125, in three batches)

Everything of §1.6 that step 4 does not reach. No new obstacle, no placement moved: only what
is seen when she is hit.

| Obstacle | Where its code is | Scenarios |
|---|---|---|
| The casino's chips | `Spill` in `movers.js` | 1: as built |
| The trays on the floor | `Trays` in `hazards.js` | 3: the trip and the ride are the fright now; the door opens after, on the guest looking after her. **Built (2026-11-18):** one tray, the breakfast stewardess's own (the user: the three flat bars "don't make any sense"); run onto at any step of her stride (four clips, one each quarter) or jumped onto, she rides it off the way she was going, its dishes flying off behind her; the "Do Not Disturb" door swings open on the guest after |
| Deck 9's vacuum | `Darter` in `movers.js` | 5a, 5b (step 4's clips). **Done (2026-11-17):** deck 4's picture, the ride the way it darted, back in its doorway after |
| The towel stack | `TowelStack` in `movers.js` | 18. **Its rule (the user, 2026-11-17):** it falls on her the moment she passes it; she stops at it and waits while it falls. **Built, its pictures generated (2026-11-18):** its own clips (`towels` sheet, `tools/build_towels.py`): its fall and scatter alone; running past, the fall on her from her own run's phase, she running on into it; buried, then her head up in a towel turban with a towel swan on it. With a tangerine on her: the reel and a tangerine lost, the stack falling past her (her "bats the towels off" not made) |
| (Not a mishap) the steward's jammed cart | `cart_steward`, `updateHousekeeping` in `story.js` | **Done (2026-11-17), the user's:** a tall trolley that shows the block, he and it one picture, his card tossed (`docs/progress-decisions.md`) |
| The wet patch's deck chair | `WetPatch` in `hazards.js` | 7a, 7b, by the end she slid in from. **7b built (2026-11-18):** from her slip frame the chair takes her behind the knees, carries her on, and collapses flat under her (the fold "shut on her" did not come in four tries; the user took the collapse); sliding in past it, it hardly rocks, so that it can catch her on so short a patch |
| The jogger | `haz_jogger`, `world.touched()` | 9a to 9d; his sorry on the spot |
| The kid's jet | `lido.js` | 11a, 11b; his laugh |
| The stage's light | `SwingLight` in `movers.js` | 12a, 12b, by the way it swings |
| The swinging doors | `SwingDoor` in `movers.js` | 13a, 13b, by her facing. **13a built (2026-11-18):** the door's swing generated with her (the user: the leaf drawn in code was a picture stretched, and changed colour), slammed flat on the wall under the leaf, she slides down; the door alone the same swing. Only from aft, past its hinge (the user: from forward it never hits her); **no tell** (the user: "Let the opening of the door surprise the player"). 13b not made: no swing door hits her from the other side now |
| The basketballs | `Balls` in `topdeck.js` | 14a, 14b |
| The boat drill | `DrillBoat` in `outside.js` | 15 |
| Sprinklers, the steam, the towels, the flares | `Sprinkler`, `Steam`, `TowelStack`, `Flare` | 16 to 19 |
| The gulls | `PerchGull` in `outside.js`, `FunnelWind` in `topdeck.js`, `Crossers` in `finale.js` | 20, 21, 22. **20 built (2026-11-18):** the gull dives onto her head; standing, she flails and runs off with it, running she runs on, out of the screen or to the next partition |
| "Do Not Disturb" doors, the occupied balcony | `DndDoor` in `movers.js`, `Occupied` in `outside.js` | 23, 24. **(2026-11-18)** the door swings open and shut (the swinging door's clip in its full colours; it had vanished with its frame); anyone in a doorway is cut to its opening and stands on its threshold (`People.doorway`) |

- **Art:** twenty-two gags of hers (3, 7a, 7b, 9a, 9b, 9c, 11a, 12a, 12b, 13a, 13b, 14a, 14b,
  15 to 23), the kid's laugh, the jogger's sorry. **Three batches of about eight, each shown to
  the user enlarged and numbered before anything of it is placed.** The first: 13a (flat behind
  the door), 7b (folded in the chair), 3 (on the tray), 20 (the gull on her head): the hardest
  to get right. **The first batch done (2026-11-18)**, approved in the game (`gags` sheet,
  `tools/build_gags.py`; `docs/progress-decisions.md`). Each candidate is checked frame by frame
  before it is shown (the user's rule of the same day, `CLAUDE.md`, "Art"). One that will not read after two tries is shown to the user with what could
  take its place, not re-rolled on and on.
- **Each gag looked at as "Looking closely" asks:** her proportions held in every frame, the
  thing the size it is in the world, what holds it up, the same spot before and after (the
  thing back in its place when she returns).
- **Sounds:** each gag its own few, in `src/sfx.js` with their lines; `tools/check_sound.py`
  must end "all within bounds"; the user judges them on the soundboard.
- **Playtests:** a new scenario `mishaps` (every scenario of §1.6 outside region 1 set up and
  the gag it asks for checked, her checkpoint after, the thing back in its place; with a
  tangerine the reaction and where the tangerine goes); the checks that expect the run-off
  changed in `vacuum`, `pocket`, `dash`, `region2`, `region4`, `region6`, `region7`, `region8`,
  `region9`, `finale`; `lang`, `sound`, `boot`.
- **Docs:** `docs/population.md`'s hazards, each with its scenarios; `GAME_DESIGN.md` §5.6 and
  §5.8; `docs/progress-decisions.md`; `CLAUDE.md`'s table (the new sheet).

Shown: each gag as a strip of its frames in place, and the link to its spot with
`&tangerines=infinite&pocket=off`.

**Revision (2026-11-18): deck 9's midships corridor is the way (GAME_DESIGN.md, region 4;
docs/population.md's table; decided by the user, nothing of it built).** The one placement this
step moves, on the user's word: the vacuum, the towel stack and the sprinkler stood on an
optional stretch, since the steward gave the card at 122 m.

- **Data (`tools/population.py`):** `PUSHABLES["cart_steward"]` to `(9, 185.2, 189.0, ...)`;
  `npc_steward` to `at=(9, 186.0)`. The story's part (`updateHousekeeping`, `stewardThanks` in
  `story.js`) places him by the cart and needs no change: tried in a copy, both states stand
  right.
- **The map (`tools/build_ship_map.py`):** `part-door-9-194`'s lock from none to `oneway:-1`, as
  decks 8 and 10 have it. Check what else leans on that door being free (the `region4` scenario,
  anyone's loop through it).
- **The corridor's own things at his new place:** the wall picture near 189.7 m moves out of the
  freed trolley's way by rule (as the towel stack's did, `drawCabinDoors`' kind of rule, not by
  hand); the small housekeeping cart by the cabin door at 188 m is left out there.
- **What stays as she left it:** the towel stack fallen (its heap, crossed on the way back), the
  luggage stack broken. See what the save and the movers keep today; add what is missing.
- **Nothing new is drawn:** the trolley, his tug, his steps and his toss as approved
  (2026-11-17). Shown to the user in place all the same, jammed and freed, before the playtests.
- **Proposed, to judge in play:** a crew-door checkpoint just past the sprinkler, only if the
  stretch from `cp_9_arrive` to the steward with no tangerine proves harsh.
- **Playtests:** `region4` (its order changes: the corridor first, then the trolley, the card,
  the way back, the linen room; the door at 194 shut from the lobby, open after), `vacuum`,
  `mishaps` when it exists; `tools/check_overlaps.py` (must list nothing), `tools/check_corridors.py`
  (its numbers for deck 9 given).
- **Docs when built:** the rows of docs/population.md's table themselves, GAME_DESIGN.md's
  region 4 (its "corridor's life" and "Blocks"), `docs/progress-decisions.md`.

**Second revision (2026-11-18): the one-way doors get their push bar (decided by the user,
nothing of it built).** The design has had the line since the cards were settled ("Fire-exit
doors with a push bar on one side only are the one-way doors", GAME_DESIGN.md §6.1.2's table of locks);
as built, a one-way glass door is drawn exactly like a free one, and she learns which it is only
by E (a rattle, a padlock over her). A naming of the door, not a hint.

- **Which doors:** every glass door across a deck whose lock is `oneway` in `maps/ship.json`:
  deck 8 at 74, 82, 110, 194 and 202 m; deck 9 at 202 m, and at 194 m once the revision above
  makes it one; deck 10 at 110, 194 and 202 m. The four end walls with a one-way doorway (decks
  8, 9 and 10 aft, deck 11 forward) are looked at and proposed to the user separately: they are
  not this door. The balcony cabins' corridor doors are cabin doors and stay as they are. The
  theatre's trunk has its unlit arrows already.
- **What is seen:** shut, the door is edge on (`buildBulkhead` in the ship scene: a 4 px slab,
  its handle sticking out on both sides): **a one-way door has the bar's end on its free side
  only, and nothing on the other.** Open, swung against the wall and seen face on: the leaf with
  the bar across it. The same after it has been opened for good: it is the same door.
- **Art, generated (Start here, 7), shown first:** the open leaf with its push bar, made from
  the game's own picture of the open glass leaf (28 px wide, a door's height) so that the two
  kinds stay one family and share one frame; if the generated leaf makes the code-drawn free
  door look poor beside it, the free leaf is made with it as a pair. The user sees, enlarged and
  at the game's size, in place beside her: a one-way door shut from each side, open, and a free
  door next to it. Two or three candidates for the bar (steel, or steel with a red or green
  band); it must read at 1:1. About 5 to 10 generations.
- **In the code:** the leaf and the handle by the lock's free side in `buildBulkhead` (the lock
  is already passed to it); nothing in `src/progression.js` changes.
- **Playtests:** `region4`, `region7` (the hallways' doors), `boot`;
  `tools/check_overlaps.py` (must list nothing); `tools/render_ship.py` looked at whole (a door
  drawn over the ship's side must not show from outside).

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

**Revision (2026-11-16):**

- The small pictures are generated, none drawn in code (Start here, 7); the four new books'
  stand-in covers too.

**Revision (2026-11-18), the titles (GAME_DESIGN.md §6.1.2; nothing of it built):**

- **Fourteen covers, generated, each its own** (no stand-ins any more): shown to the user
  enlarged, numbered, with title and author drawn in, before any is placed. The small book lying
  in the world and its spine on the shelf take their colours from its cover.
- **The cover's moment:** in `world.take` and `world.giveBook`, after the pick-up's sparkle or the
  hand-over's clip: the Library's `panel()` with a lighter dim (the user: "dimmed slightly"), the
  cover in the centre, any key closes it. Each of the fourteen, once.
- **The shelf seen close:** `sec_shelf` answers E: a generated picture of the shelf over the
  screen, the returned books' spines with their titles laid in by the game from the save, gaps
  for the rest. The spines are cut to one height and width so that any fourteen stand together.
- **The lettering:** a build tool sets each title and author on its cover and spine from a font
  with every script needed, at whole pixels; Hebrew from right to left. Texts of the ship's own
  kind, the same in both languages: they do not go through `src/lang.js`.
- **The reading nook's photo** (the user's, of her armchair at home): pixel art from a cutout on
  a flat ground (`image_to_pixelart`), candidates shown first; in the nook's frame (`slot_nook`).
- **Proposed with it, for the user's word:** the small shelf and the return trolley in the
  Library, drawn in code since step 2, generated as well (the art rule of 2026-11-16).
- Art: about 30 generations more than this step's estimate (the covers, the shelf, the photo),
  the exact cost said before each batch.
- Playtests: `region2` (the cover on the first pick-up, closed by a key; the shelf's close view
  with one book back and thirteen gaps), `keeps`, and each region's scenario that takes a book
  (the cover closed before it goes on).
- At the Sushi Bar the tangerine is handed over with the apology's clip (step 2's revision): it
  is the same act.
- Nothing of the twenty flies to its count: only tangerines fly (§1.7).

### Step 6. The look-outs and the deliveries (art: about 5)

- `Lookout` in `src/world/movers.js`, `LOOKOUTS` in the data: the Stardust's first, shown to the
  user running, then the other four (a porthole piece and a window piece, 0 to 1 each).
- The three deliveries: `LOADS` in `src/world/carry.js` (the vase drawn in front of her, the
  tea's meter, the pillows' slide), a source at each pantry end `when` its fire door is opened,
  the door that takes it; books 18 and 19.
- Playtests: a new scenario `deliveries`; `region3`, `region5`, `region7`, `region4`, `region9`.

**Revision (2026-11-16):**

- With a delivery in her hands a hit is a spill, as with any tray; with a tangerine on her the
  reaction follows §1.6.
- The loads (the vase of flowers, the teapot, the pillows) and the look-outs' porthole and
  window are generated (Start here, 7). Where a load hides her or changes how she stands (the
  vase before her face, the pillows in both arms), her with it is one generated clip.

### Step 7. Each deck its own look (no art)

`tools/build_ship_map.py`: the plaques' bands, the pictures by deck, drawn in code. The whole
ship rendered and looked at; `boot`, `stairs`, `lift`, `tools/check_overlaps.py`.

**Revision (2026-11-16):** the framed pictures of each deck are generated, not drawn in code
(Start here, 7, which is newer than answer 10 of §8; the plaques' bands, a flat colour, stay in
code): six sets of three or four, about 20 generations, each set shown to the user first.

### Cost

| | As planned on 2026-11-15 | Added on 2026-11-16 |
|---|---|---|
| Step 1 | 0 | 0 |
| Step 2 | 0 | about 30 (the tangerine, her seven reactions) |
| Step 3 | about 5 | 0 |
| Step 4 | about 45 (more was spent on the user's rounds of review) | about 70 (twelve gags, two clips of others) and what the look back over the art rule asks |
| Step 4a | | about 125 (twenty-two gags, two clips of others) |
| Step 5 | about 12 | a few (stand-in covers) |
| Step 6 | about 5 | about 10 (the loads, her with two of them) |
| Step 7 | 0 | about 20 |
| **All** | **about 67** | **about 260, of 4,939 left on 2026-11-16** |

Estimates, re-rolls counted in: what was spent is said in each report. Sounds are synthesised and cost nothing;
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
- **A gag is longer than a run-off** (about two seconds against one) **and cannot be cut
  short** (the user's choice). If going back feels slow in play, the lever is each gag's length
  in `MISHAPS`, not a key.
- **Her drawn with a thing** (riding the vacuum, flat behind a door, folded in a deck chair) is
  the hardest art in the plan: those are made first, and one that will not read is shown to the
  user with a replacement, not re-rolled on and on.
- **Sides must be told right.** A hit read as from the front when she had just turned gives the
  wrong fall, and the user will see it at once: the side is taken from her facing at the moment
  of the hit, and each scenario has its own check in the playtests.
- **"Nothing twice."** The three deliveries are one kind of errand with three loads and three
  rules: the closest the plan comes to the line.

---

## 7. What is still the user's to give, later

- ~~The fourteen books' titles~~ (given 2026-11-18, §4.1) and the reading nook's photo (given
  the same day). The other five photo slots' photos and "other missing things", once the game is
  tested and verified.
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
| (2026-11-18, from two photos of her bookshelf) Which fourteen, and in what order? | Fourteen picked by number, the two Harry Potters "two first harry potter books in the series"; "The order is random" |
| Her own book on the bed in cabin 8206? | Її війна |
| The nook's photo: the picture in its frame, or the model for the nook? | "The picture. The nook is at home, and cabin 8206 is not home in that sense." |
| Titles in their own language, or in the game's? | "In their own language and script." |
| Where do titles show: A the cover when she gets a book, B the cover before the page in the chair, C the shelf seen close, D the nook's bookcase? | "A and C. On A, the screen is dimmed slightly, a generated book cover is shown in the center of the screen with the title and author. Covers have to be generated for every book, to look differently. For C, it also has to be generated." |
| Harry Potter: which edition? | "English. But put the real titles there, not the first/second book." (Harry Potter and the Philosopher's Stone; Harry Potter and the Chamber of Secrets) |
| The author on the cover? | "Yes" |
| Which title lies where (GAME_DESIGN.md §6.1.2's table)? | "Good" |
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

**The revision of 2026-11-16 (mishaps, the tangerine, the art rule):**

| The question | The answer |
|---|---|
| (The user's own, opening it) | "While implementing the three-uses plan (in another session), I came up with an idea to replace some frights with slips, trips, and falls ... propose an update to the plan, to replace frights with more proper mechanics leading to either a respawn or to a tangerine loss" |
| The first proposal (most hits a slip, a trip or a knock) | "You're reusing the slips too much. We have a lot of PixelLab generations (I upgraded my subscription), and I want us to use them. Add more variety to the current frights" |
| The second (a gag per obstacle) | "Better ... think about specific scenarios from it where she interacts with moving objects. What happens when she is facing a moving object, versus when she is hit with it from behind (like: fall forward vs fall backwards on her bottom). What happens when she stumbles on an object while moving, versus when an object hits her while she's standing" |
| 4c and 6c (standing still and watching, nothing happens): keep both, one, neither? | "Your suggestions accepted, although, a stopped [paper] would not be collected, if it stops not by the door. It just disappears shortly after" |
| Four gags have her sit onto the thing: a family, or too alike? | "Accepted" |
| Any rows to change or drop? | "All accepted" |
| The vacuum's ride in place of her squeal and run-off, the "Eeek!" kept? | "Update the wording with fright/excitement, like 'Weeeee!' or something" |
| "Do Not Disturb" doors with a tangerine on her: (a) held out as an apology, (b) knocked out? | "a" |
| Any key cuts a gag short? | "No, during the gag the movement keys have no effect" |
| Who builds it? | "You update the plan with this update in detail, and my other session implements it. You update each step with their relevant additions. Even the built steps. The other session should revise what it already built and complete it" |
| (The user's own) | "Also, add a general rule: use generations instead of attempting to draw by itself, or reuse part of props from other scenarios" |
| (The user's own) | "Rework the tangerine sprite to make it a bit more detailed and look like a tangerine" |
| (The user's own) | "Collected tangerines should fly into her tangerine meter above" |
| (2026-11-18) Deck 9's vacuum, towel stack and sprinkler are on an optional stretch: make that part of the corridor required? Where does the steward go: just past the sprinkler (152 m) or the corridor's aft end? | "What would you recommend here for the most fun and varied gameplay?"; on the recommendation (the aft end; the luggage stack kept; the roll cut to about 4 m; the way back changed, not repeated; the picture rehung, the small cart out; the glass door at 194 one-way from the corridor): "Ok, I accept your recommendation here, and the suggested fixes" |
| (2026-11-18) The one-way doors look like any glass door; the design's push bar on the free side was never drawn. Build it, as a generated variant shown first? | "Add it to the plan, yes" |
