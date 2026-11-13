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

## Step 2: Atrium + promenade, region 2 (2026-11-13)

Done: deck 6 from the bow to the Library, the promenade, the boat walkway's foothold and deck 7's
lobbies populated and playable from the crew trunk to the door into region 3. The delivery robot
she rides; a cabin being made up; the Internet Café's surfer; the couple at the atrium's rail and
the glass elevator's glimpse; Bliss's DJ and the dance floor; the Photo Studio's flash; the
Windjammer's barmaid and the guest at the model ship; the cat's tail in the Photo Gallery; the
Library (the librarian, the shelf with ten gaps, the return trolley, the red reading chair, ten
pages, near-catch 2 on the reading table and the door it leaves ajar); the jogger, the gulls, the
rival's glimpse and the porthole's on the promenade; the gate's ladder, the lifeboat's inside with
the second book and the first photo slot; the fitter, the florist's flowers and the auction's
crates on deck 7's ways up. Playtest `region2` (it starts from a save at region 2's door:
`enter_region2`); `golden` still walks the whole route.

**New systems:** the books (`src/world/library.js`: trolley, shelf, chair, a full-screen panel for
a page or a photo); things that move by themselves (`src/world/movers.js`: the robot as a platform,
gulls that are shy of her); photo slots; glimpses and the region's scenes in `src/world/story.js`;
standing aside (`verbs.updateAside`); quirks set off by standing still; scenery people turned to
us or away (`pose`), and built furniture drawn again in front of someone (`cover`).
`tools/build_things.py` packs PixelLab map objects (the robot, the gulls) into
`assets/sprites/things.png`; `tools/draw_pages.py` draws the ten pages.

**Changes and additions to the plan, and why:**

1. **The Library is laid out on what is built.** Its desk stands at the aft door (191.9 m; the spec
   put the librarian at 164), so: the librarian behind that desk, the shelf with ten gaps on the
   wall beside her over the bookcase (190-192 m), the return trolley by her desk (191 m), the red
   chair and its lamp at 166.75 m, Bumbot asleep on the reading table at 181 m (spec: 178, between
   tables), and `cp_library` by the forward door at 160.85 m (the spec's 193 m is the desk). The
   basic layout is not to change, and this way a book's return ends beside the door Bumbot opens.
2. **A book always stands in its own gap** (book n in gap n), so the shelf shows which are missing,
   not only how many. The librarian shelves them one at a time (her `shelve` clip).
3. **The chair reads the lowest-numbered book she has found and not yet read**, whether it is still
   in her pocket or back on the shelf: finding a book is enough to read its hint. The ten pages are
   drawn in code, each a picture of one hidden thing (no words).
4. **The door Bumbot knocks open stays open for good** (`ajar`), with the rope stand lying where it
   fell (a drawing of its own, `rope-down`): the way into region 3 can be seen from across the room.
5. **The robot makes the high tangerine easy, it is not the only way to it.** Her jump (68 px) plus
   her height reaches 127 px and a deck's ceiling is at 128: nothing under a ceiling is out of a
   full jump's reach. The tangerine sits on the fire-hose cabinet at 118 px: a small hop from the
   robot's top takes it, and so does a full jump from exactly under it.
6. **Standing aside is ↑ on the promenade's deck** (she turns her back to us against the wall, the
   jogger runs by). The view is side-on, so the two lanes cannot be painted as lanes: signs on the
   wall say it ("JOGGING TRACK by the rail", "WALKERS: keep to the wall ↑"). Hopping him works too:
   standing still it wants timing, running at him it is easy. His touch is 14 x 40 px.
7. **The rival's glimpse is tuned to the view's width** (about 12.5 m): he peers under a boat at
   190 m as the spec says, notices her at 4.2 m (at 5.5 m he was still off screen and left unseen),
   and hurries off away from her faster than she runs: in at a promenade door if one is on his way
   (the door at 186 m when she comes from aft), otherwise out of sight along the deck.
8. **The porthole glimpse is at 168.3 m** (the spec's 150 m has no porthole): two black ears and
   green eyes rise behind the glass and duck.
9. **The flash is between the studio's softboxes** (132.45-134.75 m), every six seconds, the lamps
   warming for 0.7 s as its tell; caught, she turns to the camera with a thumbs-up for a second.
   Not with a tray in her hands.
10. **The cabin being made up is a room she can step into** (`maid6`, drawn: the stewardess
    smoothing the bed, a towel swan, a suitcase on the rack), not only a peek through a door.
11. **The open lifeboat is at 147.5 m** (spec: 140 m), where a tender hangs with a door at the
    walkway's height. Inside: the second book on the bench, the first photo slot between the
    portholes. **Photo slots show a placeholder (a heart in a frame) until the user's pictures are
    in:** a texture named `photo-<slot id>` replaces it.
12. **The dance floor's spot is 117.2 m** (spec: 117; kept clear of the crew trunk's door at
    118.2 m), **and the disco ball throws its lights while she dances** (an addition).
13. **A stand-still quirk counts from when she stopped at the spot.** It used to count her stillness
    from wherever it began, so arriving by a door or a lift could set it off at once (the playtest
    found it: the dance swallowed the E meant for the trunk).
14. **Scenery people can face us or away** (`pose`): the couple at the atrium's balustrade look down
    into it, toward us; the couple at the ports' plaques on deck 7 have their backs to us.
    **Furniture can be drawn again in front of someone** (`cover`): the Windjammer's barmaid stands
    between the back bar and the counter. (The tangerine on her counter reads as hers to offer.)
15. **Two characters were replaced.** The first surfer came out a grey figure with a monitor in the
    air; the second is seated on his own chair and shrunk to 0.8 (PixelLab draws seated figures as
    tall as standing ones: `tools/cast.py` has a `scale` option now). The "woman at the rail" came
    with a rail and a life ring drawn into her: she is kept for an open deck, where the rail is
    behind the people, and the atrium has another woman.
16. **The Windjammer's barman is a barmaid; the guest "with the model ship" is an old gentleman in a
    captain's cap** admiring the ship in its cabinet (the cabinet is built).
17. **`sec_cat_photo` is drawn by the game** (an empty deck, a black tail leaving the frame) and
    hangs in the gallery's upper row at 157.4 m.
18. **What stands on deck 7's ways up:** the florist's vases stand in front of the forward flight
    (the elevator's door is right behind its foot: no floor there); the fitter kneels at his roll
    by the atrium flight; the auction's crates and a canvas on an easel stand under the midship
    flight.
19. **The gulls** are three PixelLab map objects (perched, wings up, wings level) on the rail's top
    at 150.5, 175 and 200 m; one flies up when she is within 3 m and settles when she has gone.
20. **The librarian's finger goes to her lips whenever she passes the desk at speed** (she has no
    walk, so: any run within 3 m), at most every six seconds.
21. **Left to later steps:** the Library's rolling ladder and the odd book (the push verb is region
    4's; the nook is step 9's), the theatre's audience (step 3), the boat drill and the rival on
    the walkway (region 7). The librarian's bubble shows a book, not "a book and the gapped shelf":
    the shelf is right beside her.

**PixelLab spent on this step:** about 55 generations (13 characters and their clips, her dance,
pose and reading clips, the robot and the gulls). 1,509 of 2,000 left (renews 2026-11-30).

## Step 3: Showtime, region 3 (2026-11-13)

Done: the theatre (deck 6) and deck 7 from Magnum's to the Stardust balcony populated and playable
from the Library's door to the red trunk up to deck 9. Near-catch 3 with its own staging (the rival
runs in, trips and goes down the trap door; Bumbot rides the fly rope up); the stage manager's
errand (his pills from his cabin on deck 4, his sneezes, the Entertainment card handed over); the
swinging stage light ("Bonked"); the open trap door down to the galley, where the rival sits in
the flour; the dancers; the bow at centre stage; the casino's chip spills ("Slipped") and the
jackpot; the cat's portrait and her double-take; the dressing room with the third book; the
lighting booth and its catwalk with the second photo slot; Magnum's barman and pianist, the
croupier and players, the shopper, the teen at the arcade, five in the audience; the theatre's
scenery flats on the aft flight up. Playtest `region3` (from `enter_region3`); `golden` now does
the pills errand for real.

**New systems:** a near-catch can have something happen first and its own way out (`cat.before`,
`cat.flee`: `nearCatch` in the ship scene); hazards that keep their own time
(`src/world/movers.js`: `SwingLight`, a pendulum; `Spill`, a tell then a spill); a thing that pays
out once (`jackpot`); people held in a clip's last frame (`still`: sat on the floor).

**Changes and additions to the plan, and why:**

1. **The stage as built is 6.7 m wide (244-250.67 m), not the spec's 244-254:** the deck's last
   metres are structure. Everything on it is laid out again in that width, from the curtain aft:
   the stage manager (245.0), the trap door (246.3), centre stage (247.3), Bumbot in the spotlight
   in front of the piano (248.75), the light (249.1), the fly rope (249.7).
2. **The rival goes down the trap door, not into an orchestra pit.** A pit would need a hole in
   deck 6 showing in the Seven Seas below; the trap door is already a one-deck drop onto the
   galley's flour sacks. He bursts in through the curtain behind her, trips on the microphone's
   cable, lands on the trap door, it gives way, flour puffs up out of the hole. The gag shows what
   the seam in the boards is, and **the trap door stays open after**: a visible hole she hops or
   uses (a quick way down toward deck 4). **He sits in the galley's flour until region 4.**
3. **One swinging light, not two.** Two alternating arcs do not fit a 6.7 m stage with a hole in
   it and leave anywhere to stand. The one light is a real pendulum from the ceiling (period
   3.2 s): at the bottom of its arc it is at her head's height, at the ends it is over it. Before
   the beat it is hauled up short and is Bumbot's spotlight; the rival's crash lets it down, and it
   swings out away from her first. Where the scene leaves her standing it does not reach her
   (the playtest checks it).
4. **Centre stage is the safe spot between the open trap door and the light,** and standing still
   there for three seconds is the bow (`sec_spotlight`, her own clip, to the house).
5. **The stage door is by the curtain at 242.5 m** (spec: 254, in structure; decided in step 0); the
   dressing room behind it is drawn (the mirror ringed with bulbs, the third book on the make-up
   table).
6. **The dancers rehearse on the stage until the beat, then sit on the floor in front of it** (the
   flat stage has no edge to sit on): two people each, one until `bb3`, one after.
7. **The stage manager's allergy is the story:** he sneezes every five seconds from the start
   (the cat is on his stage), flaps when the rival appears, wants his pills after, sneezes once
   more with the bottle in his hand, and stops for good. The Entertainment card is his to hand
   over (its stand-in pickup on the stage is gone).
8. **The pills can be fetched two ways:** down the theatre's one-way trunk (which then opens from
   deck 4 too), or down the trap door and back up the aft stairs, whose rehearsal rope has lifted.
9. **The chip spills are 1.8 m wide on three machines** (151.9, 154.3 and 166.8 m), and **a slip
   needs her to be running on them**: standing still is safe, and a running jump clears them.
   The jackpot machine (the one under the JACKPOT sign, 153.1 m) stands between two of them.
10. **The cat's portrait replaces the easel at 140 m** (drawn by the game), and the double-take is
    her own idle look, set off by a second and a half of standing still.
11. **Magnum's had no piano:** one is added by the bar (116.6 m) with the pianist at it. **The
    casino's seated player and the audience are drawn on seats of their own** and shrunk to 0.8,
    like the surfer; the croupier faces us from behind her table, the cowboy and the teen have
    their backs to us.
12. **The lighting booth and the catwalk are one room** (480 px): the console under a window on
    the stage, then the catwalk in the flies with the hatch Bumbot went through and the photo slot
    at its end.
13. **The scenery flats on the aft flight 7-8** (a palm, a setting sun) are drawn by the game.
14. **Left for later:** the rival's lunge (he runs in and trips: no lunge needed), the stage
    manager's talk clip, a fright clip per hazard.

**PixelLab spent on this step:** about 61 generations (15 characters and their clips, the rival's
trip and sit, her bow). 1,448 of 2,000 left.
