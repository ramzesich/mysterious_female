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

## Step 4: Housekeeping, region 4 (2026-11-13)

Done: deck 9's midships corridor ("housekeeping hour") populated and playable from the red trunk's
door to the duct's drop into deck 8, with decks 8-10's lobbies and atrium walks. The steward and
his jammed cart (he pulls, she pushes, his thanks and the Housekeeping card); the honeymooners'
picture (her camera clip, the flash, their kiss, the fourth book); the cabin being cleaned with the
vacuum that darts out of its doorway and the towel stack beside it ("Buried"); the sprinkler
("Drenched"); the balcony cabin (drawn; a checkpoint, a tangerine, Bumbot's glimpse from its
balcony); the door that flies open ("Bonked") with the kid behind it; the "Do Not Disturb" door
("Startled"); the standing cart, the luggage stacked to the ceiling, the adjoining cabins round it
with a blanket fort; near-catch 4 in the linen room with its own way out (he leaps into the vent),
the laundry cart pushed under the vent, the duct with its grilles and what is under them, the
chute down to the laundry; the towel animals on the flight up from deck 10. Her crawl, push and
camera clips. Playtest `region4` (from `enter_region4`); `golden` does the new flow for real.

**New systems:** hazards that react to her coming (`src/world/movers.js`: `Darter`, `SwingDoor`,
each armed again only once she has gone away), a trap with a tell (`TowelStack`), a timed one
(`Sprinkler`), a door that answers E with a fright (`DndDoor`); things she must crawl under or
through (`LOWS`, kind `low`: solid above her on hands and knees, its picture in front of her); a
pushable that stands by the wall and is a step up (`"top"`); key caps that bob over a spot
(`world.glyph`); looks down through the duct's grilles (`peeks`); a book handed over
(`world.giveBook`); a fright's own clip (drenched: she shivers).

**Changes and additions to the plan, and why:**

1. **A checkpoint where she arrives** (`cp_9_arrive`, the crew door by the trunk, 119.6 m). A
   fright sends her to the nearest lit checkpoint, and deck 9 had none before 150 m: the first
   fright of the gauntlet would have sent her back down to deck 7.
2. **The Housekeeping card is the steward's to hand over** (its stand-in pickup at 132.5 m is
   gone). He stands at his cart's far end and pulls while she pushes, so the cart never runs over
   him and the push reads as help; at 130 m he mops his brow, bows, and passes the card across the
   cart. (The spec had him walk to her: the cart is between them.)
3. **The linen room's vent is high on the wall** (the room's drawing changed: it was low, from
   before the plan). The laundry cart, now a thing of its own, stands by the wall: she walks past
   it to Bumbot; he leaps from the towels up into the vent; an E key shows at the cart's end, she
   pushes it under the vent, jumps onto it, and ↓ there takes her in. This is the spec's scene; the
   cart is not in her way because only its rim holds her (a step up, not a wall).
4. **The chute's hatch is drawn in the linen room's wall by the door** (a steel flap, the green
   card's colour), and **she lands in the laundry's cart of towels with a towel on her head**; she
   climbs out, and the towel stays on her head a few steps before it slides off.
5. **The security officer waits in the laundry in a towel** (a new sprite of him), his uniform
   going round in the third washer, from region 4 until region 6. Region 4 had no appearance of
   his; this follows the stage's flour (he sat in the galley until now) and is what she finds at
   the bottom of the chute.
6. **The duct is a place, not a tunnel:** steel with flanges, rivets and hangers, cobwebs, a fan in
   a branch, Bumbot's paw prints in the dust, and his eyes in the dark ahead of her the first time
   through (they keep their distance and are gone at the far grille). Over each grille a framed
   look down fades in under it (the lobby's chandelier, the atrium's dome, a cabin full of
   balloons, a passenger snoring), drawn by hand. A tangerine lies half way. The far grille shows
   its key (↓) and answers from the duct's end wall too.
7. **The vacuum's rule:** its red eye blinks while she is coming (within 4.6 m); as she comes
   within 2 m it rattles for 0.3 s and darts 2 m along the corridor at her. A jump as it rattles
   clears it; the dash sends it spinning. On its way back in it is harmless, and it stays in until
   she has gone away and come again: so she can stand at the door and go into the cabin.
8. **The towel stack falls when the floor is shaken, not at "running speed":** the game has one
   speed on foot. It sways as its tell (harder when she is near); a jump landed within a metre of
   it, or the dash, brings it down on her side: "Buried" if she is still under it a third of a
   second later (the dash is through by then). It stands by the vacuum's doorway on purpose: a late
   jump over the vacuum lands beside it.
9. **The door that flies open has the pool's kid behind it** (his character, made now, shrunk to a
   child's height): he looks out with his water pistol and shuts it again. Stopping when the
   handle rattles is safe; the door only hurts as it swings.
10. **"Do Not Disturb": a guest in a bathrobe, a towel turban and a face mask** shrieks in the
    doorway; her fright is the apology ("Ой, вибачте!").
11. **The adjoining cabins are a family's, and the children have built a blanket fort across the
    way through:** the loop round the luggage needs the crawl (learned at the linen room); the dash
    goes through the luggage without it. Two tangerines are hidden inside the fort. The cabins are
    drawn (cabin 8206's colours), as are the cabin being cleaned and the balcony cabin.
12. **Bumbot's glimpse from the balcony is on the partition's top at the balcony's aft end**, not
    on deck 10's rail at 160 m: a deck up and eight metres aft is outside her view (about 12 m wide,
    7 m tall). He sits there washing, looks at her, and jumps up to the balcony above.
13. **The honeymooners stand at their own door** (135.6 m, a "JUST MARRIED" note over it), turn to
    each other for the picture, and go in after. Their camera is the bubble's pictogram and crosses
    to her hands; her clip raises her hands to her eye and the game draws the camera there.
14. **The standing cart is at 172.6 m** (an extinguisher hangs on the wall at 173.6), its tangerine
    on its cloche: she hops onto the cart for it. **The luggage is five suitcases high**, to the
    ceiling.
15. **The towel animals** on deck 10's midship flight: the atlas's swan on a table of towels, and
    three new ones (an elephant in sunglasses, a monkey, a rabbit).
16. **Strollers:** a man frowning at a deck plan by deck 9's directory, a lady with shopping bags
    walking deck 8's atrium walk, an old man photographing the dome from deck 10's; a bedmaker
    shaking out a sheet in the cabin being cleaned. A tangerine in the pantry (on a crate): the
    green card opens it now.
17. **Left for later:** the two officers (step 9 draws them where they stand); a fright clip of
    her own for "Buried" and "Startled" (the towels over her and her start do it); deck 9's aft
    hallway and the other balcony cabins (regions 7 and on).

**PixelLab spent on this step:** 45 generations (ten characters and their clips, her crawl, push
and camera clips, three towel animals). 1,403 of 2,000 left.

## Step 5: Deck 8 forward, region 5 (2026-11-13)

Done: the breather between the duct and the pool deck. She drops out of the duct's grille into
deck 8's forward corridor (the grille hangs open in the ceiling after, dust comes down with her);
the party behind the door with the balloons; an open cabin with the sea in its window; her own
cabin 8206 (a checkpoint at its door, the welcome basket's tangerines, the fifth book on the bed,
read there); a steward's cart with a towel swan; the lobby's door, which opens from the corridor;
the forward stairs on up past the officers' lobbies to deck 11. Playtest `region5` (from
`enter_region5`).

**New in the code:** cabin doors that stand open (`OPENDOORS`, kind `opendoor`: "party", "sea");
a thing can be taken from where it lies as well as from the floor under it (a book on a bed).

**Changes and additions to the plan, and why:**

1. **Paw prints in the dust** run from under the grille to the lobby's door (once she is out of the
   duct): the plan's paw prints start on deck 11; here they say which way he went, in a corridor
   with nothing else to say it.
2. **The party is a child's birthday:** the girl whose birthday it is (a new character: a party
   hat, a paper horn) dances at the door; balloons are tied to its handle, lie on the floor and sit
   against the ceiling; notes come out into the corridor while she is near. The balloons are drawn
   by the game, as they are in the duct's look down at this cabin.
3. **The cabin with the sea in its window is a doorway to look into, not a room:** an open door in
   a cabin door's place, the window and the made bed drawn in it; standing still there two seconds
   she looks in (a quirk).
4. **The fifth book lies on her bed, and standing still on the bed with it she sits down on the
   bed's edge and reads it**: its page shows as in the Library's chair, and it counts as read. After
   that the bed is for bouncing again. (The spec: "she reads there instead of the bounce".)
5. **Cabin 8206's door is a checkpoint** (`cp_8206`, the spec's exception to crew doors), lit by
   walking past it.
6. **One more tangerine** on a side table at 49.3 m: the region had only the basket's two.
7. **The duct's grille is a thing in deck 8's ceiling** at 66 m: shut until she has come out of it,
   hanging open after.

**PixelLab spent on this step:** 5 generations (the birthday girl and her dance). 1,398 of 2,000
left.

## Step 6: Lido, region 6 (2026-11-13)

Done: deck 11 from the forward lobby aft, and deck 10's hallway under the pool. The gym (a runner
on a treadmill, a man with dumbbells, the grip socks on the yoga rack); the chess set; two
sunbathers; near-catch 5 at the first pool and the pool draining; the hatch into deck 10's hallway
(trays outside a "Do Not Disturb" door, a swinging door, a sprinkler, a second door not to knock
at); the hot tub and the tangerine on its canopy; the kid with the water pistol on the aft pool
deck, the security officer on his knees at a lounger, the wet patch and its deck chair, Topsiders'
barman; the Garden Cafe's queue and its cold room; the painter and the fans on the flights up; the
Great Outdoors: the soft serve machine and its swirl, the gulls, her husband at the first table,
the canister, the table scene with the sixth book and the framed picture, a cone for herself; the
crates. Playtest `region6` (from `enter_region6`).

**New in the code:** `src/world/lido.js` (region 6's part of the story, mixed into the Story:
the pool's scene, the kid, the machine, the table, the chess set, the hot tub, the paw prints) and
`src/world/hazards.js` (`WetPatch`, `FoodGulls`, `Queue`, `Trays`); in the data `PLATFORMS` (a
roof to stand on), `LIDO`, `WETS`, `FOODGULLS`, `QUEUES`, `TRAYS`; sources that are there to see
but hers to take only `when` a condition holds; photo slots that come `after` a flag; a beat with a
whole scene of its own (`cat.custom`); the pool drains over five seconds with her in it;
`tools/unchair.py` (takes out a chair PixelLab drew under her in a seated clip).

**Changes and additions to the plan, and why:**

1. **The spec's metres follow the deck as built.** The pool deck and the Great Outdoors were built
   before the plan (the user's photos): the hot tub stands between the two pools, the first pool's
   ladder is at its forward end, the service station runs 211-217 m and the first table is at 220.
   So: the machine is at 214.6 m, her husband at the first table's forward chair (219.5), the
   crates at 217.9 (behind his chair, by the station), the kid's beat is 142.6-149.3 (aft of the
   second pool), the wet patch 150.9-152.9 by the shower, Topsiders' tangerine on the bar (156.3).
2. **Near-catch 5 comes to her in the water.** The first pool fills the deck from side to side, so
   she can only come to Bumbot swimming: the scene starts when she is within about two metres of
   the aft rim. He fishes on the rim; **the kid squirts from the hot tub** behind him (his cap
   shows over its rim before; the plan had him 5 m off, on the far side of a pool); Bumbot goes up,
   comes down in the pool, climbs out by a second ladder (added at the aft end) onto the drain
   lever's housing on the rim, shakes himself dry (his new clip), throws the lever jumping off and
   runs aft along the pools' far side. "She topples in too" happens only if she came along the rim.
3. **The pool drains with her in it:** the surface sinks to the tank's floor over five seconds and
   she sinks with it, to stand in the empty tank by the hatch. (Before: the water faded and she
   was put on the deck.)
4. **A checkpoint on the aft pool deck: the pool attendant's hut** (`cp_pool`, a striped white hut
   on the second pool's aft rim). Without it the kid's and the deck chair's frights sent her back
   to the gym, two pools away.
5. **A tangerine on the hot tub's canopy** (`tan_11_canopy`), reached by a wall jump off one of its
   posts from under it: the socks' first use, a few steps from where she gets them, long before
   the climb to deck 12 that needs them.
6. **The socks' hint says how:** "In the air at a post or a wall, jump again: kick off it" (the
   posts and pillars are not walls she can press against).
7. **The kid:** his jet is one shot after a tell (he brings the pistol up, about half a second),
   three metres long at the height of his hands: a jump as he fires clears it; behind him she is
   safe. The dash sends him to his beat's aft end, his back turned for ten seconds. With a cone in
   her hands he stands and waits. A stub he drops on the deck (a gull comes for it) and he is
   himself again in three seconds; a proper cone he eats, and from then on he squirts the gulls
   over the pool deck (they wheel higher and never dive) and never her.
8. **The buffet queue** is six passengers with full trays coming from the buffet along the aisle in
   two threes, round and round (out from behind the buffet, in behind the ice cream counter). Each
   is a body she can't walk through (no fright: she is held back) and hops one at a time. **For a
   crew member with a tray they turn aside**: with a tray she can only hop 26 px, so the plan's
   "hop it at a gap" would have made the cone's run impossible; and it is what passengers do.
9. **Trays never cross a pool** (swimming spills one, and the tank is deeper than a tray's hop), so
   nothing she must carry goes that way: the kid's cone goes from the machine through the cafe to
   the aft pool deck, the canister from the cold room straight aft.
10. **The gulls dive at where she will be:** while she carries food in the open, a gull's shadow
    shows on the deck where she will be in a second if she keeps on as she goes, then it comes
    down on that spot. In it, she loses the cone (never a fright). So the way past is to break her
    stride, not to stand still (standing still, it has her). Two stretches: the aft pool deck's
    open part (141-145.6 m, two gulls wheeling; off for good once the kid is fed) and the Great
    Outdoors from its door to the first table (one gull on the rail). The plan's gulls over the
    first pool had no food to dive at (see 9).
11. **The machine:** hold E and the swirl grows on a meter; let go in the green for a proper cone,
    early for a stub, late and it goes over onto the deck (the gull is on it at once). It works
    until the kid is fed, then is empty (a red light, a cough) until the canister is poured in.
    The canister is on the cold room's shelf from the start, but hers to take only once the
    machine is empty.
12. **The table scene:** his bubble (a soft serve, once the machine is refilled) asks her to make
    one **for herself** and sit down: she keeps the cone, they eat together (the plan had her hand
    it to him, and him already holding one). Then their framed picture stands on the table (the
    photo slot) and he gives her the sixth book.
13. **The wet patch is two metres long** (a jump clears it), and the palm that stood at its end
    moved a metre aft, out of the deck chair's way. The chair rocks, slides the patch's length at
    her, waits, and slides home.
14. **The hot tub** takes her standing in it up to her shoulders (no new clip was needed).
15. **Deck 10's hallway:** the trays' zone is under two metres so a jump clears it; their clatter
    opens the door at 131.6 m; a tangerine rolls out from among them (one more, `tan_10_tray`).
    New people behind the doors (no person is used twice): a man in pyjamas, a woman in curlers,
    a man half-dressed for dinner at the swinging door.
16. **The paw prints** run from the second pool to the machine and dry over a minute and a half.
17. **Ambient people, each new:** the gym's runner and lifter, two sunbathers on loungers of their
    own (PixelLab map objects; the two empty loungers there were taken out), Topsiders' barman,
    the painter (with his bucket), three fans (two on deck 11's aft flight, one on deck 10's),
    three guests at the Great Outdoors' far tables.
18. **Her husband is a stand-in for now.** The plan draws him from the user's photo, and there is
    none in `reference/` yet (asked for on 2026-11-13). Until it comes, `husband` in
    `tools/cast.py` points at a seated guest's character; his own needs: seated on a dark wicker
    armchair, and the clips `eat`, `wave`, `laugh`, `give`.
19. **Left for later:** the coffee machines' source and the mojito at Topsiders (step 8, with the
    engineer's and the old lady's errands); the Sports Bar's three at the TV (they are the fans,
    until region 8); the wedding party itself (step 9; its rope and sign stand); a swoop at her
    when she lingers on an open deck (step 7's rule).

**PixelLab spent on this step:** 97 generations (twenty characters, their clips, her five
clips, Bumbot's shake, two sunbathers). 1,301 of 2,000 left.

## Step 7: Outside, region 7 (2026-11-13)

Done: the balconies of decks 8-10 (the vault over a partition, the climb up its pole, gusts, ten
perched gulls, five laundry lines, two balconies with someone on them, towels on the rails, the
balconies' furniture, six ajar balcony doors, each a checkpoint); the five balcony cabins drawn;
the four hallways behind them (deck 8 midships: trays and a "Do Not Disturb" door, a door that
flies open, a sprinkler, the steward on his rounds, an ice bucket's tray; deck 8 aft: six lots of
trays and two doors; deck 9 aft: a door, two sprinklers out of phase, a cart; deck 10 aft: trays
and a door, a door that flies open, the guest's cabin, a cart); the guest locked out on his balcony
and his book, the seventh; the boat walkway: the columns and end walls as ways up to deck 8, the
boat drill and its two crew, the security officer at a tender; a photo slot on deck 8's first
balcony. Playtest `region7` (from `enter_region7`); `?at=balcony` and `?at=walkway` start there.

**New in the code:** `src/world/outside.js`: `Gusts`, `PerchGull`, `Laundry`, `Occupied`,
`DrillBoat`, `Rounds`, and region 7's part of the story (the ajar doors, the guest's scene, the
security officer on the walkway, the hint); in the data `GUSTS`, `PERCH`, `LINES`, `OCCUPIED`,
`BALCONY_CPS`, `DRILL`, `ROUNDS`, and places "b8"/"b9"/"b10" (on a balcony of that deck); the
builder's `balcony` and `drill` in `maps/world.json`; checkpoints that are only a lamp (`bare`).

**Changes and additions to the plan, and why:**

1. **How the partitions are crossed.** The plan's wall jump kicked her away from the wall, so a
   partition took a kick back and a steer round: awkward 66 times a deck, and the balcony above was
   2 px out of reach. Now: at a partition, **jump and jump again vaults it** the way she is going
   (the kick is as strong as the panel's top still needs); **with ↑ held, each jump is a kick
   straight up**, and the partition has a pole on its top up to the balcony above, a grip all the
   way, so three or four kicks climb a deck. ↑ works on every grip (pillars, the sun cover's post).
   Letting go of jump no longer cuts a kick short. A hint says so the first time she is out on a
   balcony in the socks. Down is ↓ and jump, as before.
2. **A partition is a wall, never a ledge:** coming down on its 6 px top she slips off it, the way
   she is going (the playtest found her standing on one, her head in the balcony above).
3. **Ways up from the boat walkway:** the plan had "the recess's wall" (it is behind her, nothing
   to kick). Now the recess's two end walls and **the ten white columns** the boats hang between
   are grips: kicks with ↑ held climb any of them onto deck 8's balconies. (The end walls' grips
   stood 20 px off the walls and never worked.)
4. **Gusts:** every 7 s, for 1.5 s, after 0.7 s of the towels on the rails, the laundry and the
   curtains flapping; streaks of spray cross the view; in the air she is carried aft at 60 px/s.
   A vault aft goes further; a vault forward or a climb falls short: wait for the lull.
5. **Gulls:** ten, on the rails. Lingering 2 s within 2.6 m: it goes up, its shadow shows where
   she stands, a second later it comes down there: "Swooped". A step aside and it misses. If she
   carries food it takes that, no fright.
6. **Laundry lines are folded partitions.** A line across a balcony runs along her way in a side
   view, and a vault would land her in it. So at a line the partition is folded back (a family's
   two balconies made one: ships do that) and the washing hangs across the gap from the ceiling's
   edge: nothing to kick off, so no vault there: under it on hands and knees.
7. **A second balcony with someone on it** (a couple at breakfast, deck 10, next to the
   sunbather's column on deck 8), so that the way aft has to change decks: over, under, round.
   Each has "Do Not Disturb" cards on both its partitions.
8. **Every ajar balcony door is a checkpoint** (a lamp over it; hers on deck 9, the four aired
   cabins', the guest's), and each of those cabins' corridor doors is one too: a fright on the
   balconies or in a hallway costs a few balconies or metres, not a deck. A fright now brings her
   back on the route she is on (a hallway's checkpoint in a hallway, a balcony's on the balconies)
   before the nearest by distance.
9. **Deck 8 midships' aired cabin is three balconies aft of the plan's place** (cabin door 159.6):
   at 150 it was straight under region 4's balcony cabin, and a drop from there (no socks) would
   have let her into region 7's hallway. And **the balconies count as region 7 only in the socks**:
   stepping out of the balcony cabin in region 4 opened it.
10. **The steward on his rounds** has the stretch between the aired cabin's door and the standing
    cart (162-182 m, two doors where he pulls in for 3 s), not the whole hallway: the trays, the
    sprinkler and the carts were in his way. He and his cart hold her back and carry her along,
    never a fright.
11. **The trays' clatter frightens only by the door:** it opens the nearest "Do Not Disturb" door,
    and she is startled if she is within 3 m of it; further off, whoever it is only looks out.
    Deck 8 aft has six lots (1.4 m each, a jump clears one), four of them in pairs round its two
    doors: jump, land between, jump.
12. **The boat drill is a rescue boat lowered onto the walkway** (the plan: a boat swinging out
    across it, which in a side view is toward us). It hangs in the gap between the boats at
    186-191 m, hoisted high enough to walk under; every 10 s, after a second of its lamp and a
    jolt, the crew lower it for 3 s. Under it as it comes: "Bumped"; down, it is in the way.
13. **The guest:** in a bathrobe, his book in his hand; he waves when she is in sight; his door
    won't open from outside (his bubble: a door). Inside, E at his balcony door: he comes in, bows,
    hands her the book, goes to his bed's side. The item `book_7` on his table is gone.
14. **The stern: left as the user settled it.** On the aft terraces and deck 7's stern strip she is
    out of sight behind the stern's plating (the user, 2026-11-06), so the plan's climb up the
    stern's tiers can't be played and is left out (a try with grips there didn't work either), and
    **the photo slot `slot_stern` is now `slot_balcony`: on the wall of deck 8's first balcony of
    all** (73 m, the forward end of the row, over the sea: thirty-odd vaults forward of the aired
    cabin, or ten from the walkway's first column). Step 8's telescope will point there.
15. **Three more tangerines:** in the ice bucket's tray on deck 8 (inside the steward's beat), on
    deck 9 aft's cart, and on the balcony where Bumbot swiped at the gull (his paw prints there).
16. **Twelve new people, none used twice:** four behind "Do Not Disturb" doors (shaving, a face
    mask, in his underwear, brushing her teeth), four behind the doors that fly open (a tourist
    with a camera, a lady in a sun hat, a boy in a swim ring, a businessman on the phone), the
    steward, the guest, the drill's deckhand and safety officer; two pictures for the balconies
    with someone on them.
17. **A step added by the user:** "Step 11: The ship's side" in `docs/build-plan.md` (a texture for
    the ship's outer body), after the last region.
18. **Left for later:** the per-deck pictures and plaque bands in the hallways; a second look for
    the sunbather when startled; with the parasol, the glide from a balcony (step 8).

**PixelLab spent on this step:** 42 generations (twelve characters, their clips, two map
objects). 1,259 of 2,000 left.

## Step 8: Top deck + funnel, region 8 (2026-11-13)

Done: deck 12 from Champs aft (Champs' three at the TVs; the old lady on her sunbed across the sun
deck's walk, her mojito from Topsiders, the security officer at the loungers, two sunbathers; the
court's basketballs and its quirk, the shuffleboard's two; the engineer at the technical ladder and
his coffee from the Great Outdoors; Cagney's diners; the sushi chef and two diners; Teppanyaki's
two chefs, four diners and their flares; Le Bistro's couple; Los Lobos' waiter and pinata; the aft
terrace's gusts and gull), the roof, the funnel's stairway (gusts, two circling gulls) and its top
(the horn, the engineer's toolbox and lunch box, the telescope, his locker), the horn's scene and
what it sets off, books 8 and 9, the Officer's card, the parasol and the glide, the blocks lifted
(the painter gone, the fans in the Sports Bar), the gulls on the bow that the horn sends off.
Playtest `region8` (from `enter_region8`); `?at=terrace`, `sundeck`, `technical`, `teppanyaki`,
`funnel` start there. The golden path now carries the coffee and climbs in the lulls.

**New in the code:** `src/world/topdeck.js`: `OldLady`, `Balls`, `Flare`, `FunnelWind`, `Flock`, and
region 8's part of the story (the mojito, the coffee, the horn and its cascade, the engineer's
book, the telescope, the court's shot); in the data `LADY`, `BALLS`, `COURT`, `FLARES`, `TERRACE`,
`FUNNEL_TOP`, `FLOCKS`, the builder's `topdeck` in `maps/world.json`; `Gusts` and `PerchGull` take a
place of their own (`world.winds`); a ladder gate in plain sight (a chain and a sign); a breakable
that hangs (`hang`); an item drawn as an atlas piece; `"cut"` in `tools/cast.py` (a loop made of
some of a clip's frames); the scene's `viewOverride` (the cut-away while the camera is away from
her), `stairSlip`, `overRail`.

**Changes and additions to the plan, and why:**

1. **The old lady's sunbed is a block 60 px wide and 36 high.** A jump clears it; landing on it she
   slides on over, the way she was going (nobody stands on the old lady), and the old lady glares.
   A tray's hop (26 px) does not, and ↓ drops through the walk into the pool below, as planned. A
   hint says so the first time the sunbed stops her. The sunbed is drawn in code and stays when she
   has gone; she sits on it with her knees drawn up (PixelLab drew her so, without furniture).
2. **Her mojito:** two sips, a heart, and she dozes (a loop of the doze clip's last frames, "z"s);
   two tangerines by her tipped bag. She stays a block until the horn.
3. **The security officer stands 6 m aft of her, not 10,** and his card falls 0.75 m forward of
   him: the view is 10 m wide, and the horn's scene has to show both at once. The two sunbathers
   he looks under are new pictures, just aft of him.
4. **Two teppanyaki chefs at the two grills as built, flaring in turn** (every 6 s each, 3 s
   apart, a flourish and sparks 0.9 s before): the plan had one flare 4 m wide; two of 2.5 m with
   the screen between them is a rhythm, like deck 9 aft's sprinklers. With a tray a flare spills
   it and does not frighten.
5. **The pinata hangs in the way,** on a string at head height in Los Lobos (the plan: under the
   ceiling, "the dash breaks it", where the dash could not reach it). Walking, it stops her; on
   hands and knees she goes under; the dash goes through it: paper, sweets, three tangerines
   (`GAME_DESIGN.md` says three, the spec's table two). It is the first thing after the climb.
6. **The basketballs come off the two hoops as built** (146.9 and 154.4 m), in turn every 4 s: a
   rattle on the rim, the drop, two bounces 2.2 m along the walk, a roll back under the net. The
   court's own ball lies between their reaches (150.65 m): E, and she shoots (a new clip of hers)
   and scores.
7. **The engineer's ladder has a chain across its foot and a sign, "TECHNICAL / CREW ONLY",** in
   plain sight (the bridge's hatch was the only gated ladder, hidden). ↑ at it shows the sign and
   his bubble hops. His scene lights the technical door's checkpoint: she stands by it, 1.2 m aft
   of where walking past would have lit it.
8. **The coffee is taken from the coffee station itself** (a steaming cup on its counter, no
   table), the mojito from Topsiders' bar top. The cup steams less as it cools; its meter on the
   HUD is orange and turns blue for its last third. Gone cold, she puts it down.
9. **Gusts on the funnel's stairway: no climbing in one.** On stairs she cannot be pushed aside, so
   the wind (every 5 s for 1.2 s, three windsocks lifting 0.7 s before) takes her feet if she is
   moving in it: she slides back down the flight she is on. Standing still she holds on. On the
   roof and the top the gusts carry a jump aft, as on the balconies. **The aft terrace's gusts**
   (every 7 s; towels on its two deck chairs flap first) blow over the terrace and the sun cover's
   upper end only, where the towels are in sight: the jump from the cover over the rail waits for
   a lull; the kick up the cover's post, a deck down and 13 m aft, is out of them (the whole
   suite found the golden path failing there when they reached it).
10. **The funnel's gulls come down only in a lull, every other one** (10 s; the plan: every 6 s):
    one marks where she stands on the stairway and dives a second later: moving on is the way,
    and a gust (stand still) never asks the opposite at the same moment.
11. **Bumbot sits on the horn's bracket, not on the lattice:** a black cat on the navy lattice does
    not show. Up there he is against the sky, out of reach, seen from the last metres of the
    climb; the horn goes off under him.
12. **The horn's scene:** the pull (a new clip), the shake, rings of sound, smoke; Bumbot straight
    up, down the stairway and forward along the roof; the camera to the sun deck (he streaks
    through, the officer jumps, his card flies out, he runs forward and hurdles the sunbed; the
    old lady is up and away with her bags), then to the bow (he streaks past, the twelve gulls go
    up in a cloud), and back: about 12 s. Its flag is set at the end, so a scene cut short can be
    pulled again. **After that the cord gives a toot** (a short shake and smoke): a quirk.
13. **The gulls on the bow are placed now** (the kids' pool's rims, the Spinnaker balcony's
    windscreen), since the scene shows them leaving; that they bar the way before the horn is
    region 9's (step 9).
14. **The telescope shows a round view** of deck 8's first balcony and the frame on its wall (the
    new place of the plan's stern slot): the view swings along the balconies to it, a glint on the
    frame, and back.
15. **The glide:** hold jump in the air, as planned; the open parasol keeps perched gulls, food
    gulls and sprinklers off her. **New: ↓ and jump takes her over a railing.** The atrium's walks
    are floors from side to side, so "a glide down the atrium" had no way in: with the parasol,
    ↓ + jump on an atrium walk hops its glass railing, and under the open parasol she floats down
    in front of the walks below to the atrium's floor; closing it, she comes down on the next
    walk. Outside the same keys (they already drop her a balcony) let her float on past the
    balconies below while the parasol is open. A plain jump with the key held never falls through.
    Her gliding pose is the first frames of the pull clip (both hands up on the handle).
16. **The Officer's card lies on the deck with a glint,** not on a table.
17. **The Sports Bar has its three fans** once they are off the stairs (the same three).
18. **Places moved to what is built:** the top's things (the top runs 179.7-193.2 m: locker 180.9,
    horn 185, engineer 187-188, toolbox 189.2, telescope 192.3); Cagney's tangerine on the carving
    trolley (the ladder comes down at 167.2); Los Lobos' waiter in front of his bar.
19. **Left for later:** the pastry chef and the cake (step 9: `sw_cake` still stands in); the
    restaurants' people are still (one clip each for the chefs, the waiter, a shuffleboard player
    and one of Champs' three).

**PixelLab spent on this step:** 74 generations (21 characters, 16 clips of theirs, two map
objects, three clips of hers of which the "hover" one was not used). 1,185 of 2,000 left.

## Between steps 8 and 9: the people's proportions, the parasol (the user's review, 2026-11-13)

The user, looking at step 8's screenshots: the people are not drawn to one set of proportions
(the security officer against the others on decks 11 and 12), and the parasol does not read as a
parasol. "Do a visual inspection and fix any weird-looking characters by aligning them to a same
proportional standard... You are free to use as many generations as needed."

**What the inspection found** (all 113 side by side with her, `python tools/check_people.py`):

- **The standard is hers:** a head of 17 px (hair in) on a figure 59 px tall, about three and a
  half heads. Most of the cast is within 14 to 20 px. **Twenty-four were not:** heads of 21 to
  25 px on a squat body (the security officer the worst: 22 px tall and 26 wide), or a figure
  bigger all over (the photographer).
- **The four diners of Seven Seas and La Cucina, and her husband's stand-in, sat as tall as the
  others stand:** PixelLab draws a seated figure to the same height as a standing one, and these
  five had been left out of the 0.8 that every other seated figure has.
- A template clip (breathing-idle) had shrunk the photographer by half a head against his
  standing pose.

**What was done:**

1. **Twenty-four people redrawn** from their own descriptions: the security officer (still stout,
   with his net in his hand), the porter, the lady posing for the photographer, the photographer,
   the cleaner, the receptionist, the librarian, the DJ, the stage manager, deck 9's steward, the
   groom, two of the buffet queue (the polka dots, the kaftan), the three fans, the gym's runner,
   the two behind deck 10's "Do Not Disturb" doors, both teppanyaki chefs, Los Lobos' waiter, two
   of Champs' three. All the clips the game plays of them were made again with the same motions (38 clips).
2. **How: PixelLab's "pro" mode with a style character** (`style_character_id`): the new figure
   takes its proportions and strict side view from one that has them (the boat drill's officer
   for men, the cabin maid for women). Ten generations a figure against two, but it holds: a
   plain v3 figure asked in words for "realistic adult proportions, small head, about four heads
   tall" still came out with a 24 px head. The rule and the two style ids are in `tools/cast.py`.
3. **The five seated ones shrunk to 0.8** like the rest (`"scale"` in the cast).
4. **The photographer's idle made again on his own skeleton** (skeleton-v3 with the template),
   which keeps his size; the same for the librarian's and the receptionist's.
5. Two clips made twice: the stage manager's flap (from poses, his arms hardly left the clipboard:
   now a panicked jog on the spot) and the first chef's flourish (he turned to face us and sparks
   were drawn into the frames).
6. **`tools/check_people.py`** is the inspection as a tool: everyone next to her, heads against a
   ruler, every clip of a figure frame by frame.
7. **For steps 9 and 10:** a new figure is made in v3 first (two generations), checked with the
   tool before any clip is made, and made again in pro (ten) only if its head is over 20 px.

**The parasol.** Drawn in code it was a flat red disc with white ovals, and furled a red bar on a
stick. Both are now PixelLab's (two map objects): an open parasol with gores, a scalloped edge, a
shaft and a crook handle, and the same one furled; their maroon and pink turned to the life
rings' red and white in `tools/build_things.py` (`RECOLOUR`), their length cut by taking rows out
(`CUT_ROWS`) rather than shrinking, which blurs stripes. She holds it by the shaft just above the
crook, and it turns with her.

**Two more from the same review** (the user: "check her hand placement when she's holding the
parasol"; "check the woman running on a treadmill... visual overlaps, and the direction she
faces"):

- **Her hand on the parasol.** It was drawn over her, its shaft across her hair and its crook
  beside her fist. Her fist was found in the glide's two frames (6 to 9 px in front of her
  middle, 49 to 53 px over her feet); the shaft now comes up out of it, the crook hangs under
  it, and the parasol is drawn behind her so the hand is on the shaft. Furled, it leans on the
  sunbed's foot (it stood by itself once the old lady's bags had gone).
- **The gym's runner** faced aft, her back to her treadmill's console, and covered its handrail.
  She faces the console now, stands on the belt behind it, and the machine is drawn again in
  front of her (`cover`), its handrail across her.

**A change to the plan's method, so that this is found by the build and not by the user** (the
user: "I want us to learn from the recent corrections"): the faults above passed every check
the steps had, because those were wide screenshots and tests of behaviour. `docs/build-plan.md`
"The shape of every step" has a new step 5, **Looking closely**: every person and thing a step
places is shot enlarged beside her and asked seven things (proportions, does it read, which way
it faces, what it overlaps, how it is held, what holds it up, each state of the spot). The list
is in `CLAUDE.md`; the tools are `tools/shoot_people.py`, `tools/check_people.py` and
`Browser.close_up()` in `tools/playtest.py`. Steps 9 to 11 follow it, and step 8's and earlier
steps' people are covered by this review's sweep.

**PixelLab spent:** 332 generations (26 figures in pro mode, two of them tries that were not
used, 260; one v3 try, 2; 38 clips, 68; two map objects, 2). 853 of 2,000 left.

**Where this review stopped (2026-11-13, the day's end, at the user's word):** the whole suite
passed (582 checks) with the redrawn people, the new parasol and the shrunk diners in. After it
came three small changes (the furled parasol leaning on the sunbed's foot at 129.12 m, the
runner's place, her grip on the open parasol), and after those only `region8` was run: it failed once at the gust-timed climb onto the aft terrace at its start (a known flaky jump, not near these changes) and passed on the second run (55 checks).
What is left of the review is listed in `GAME_DESIGN.md` §8 ("First next time"): the golden path
and `region6` again, the grip and the leaning parasol seen in the game, the porter and the stage
manager seen in place, and the sweep of everyone with `tools/shoot_people.py`.

**The review finished (2026-11-14).** What the last looks and two more of the user's corrections
changed:

1. **Seen in the game, enlarged:** her fist on the open parasol in the glide, facing each way
   (right); the furled parasol at the sunbed with the old lady there, after the horn and taken
   (right); the porter with his cart (right).
2. **The stage manager stood in the drum kit, black on the dark stage.** He is in front of the
   red curtain's leg at the stage's forward edge now (244.42 m).
3. **The user, from that picture: "the door is on top of the speakers, the sign is on top of the
   speakers."** The stage door moved forward to 241.3 m, clear of the speaker stack with its
   plate. I had looked at that picture for the stage manager only.
4. **So overlaps are checked by rule now:** `tools/check_overlaps.py` reads every picture's and
   text's real bounds in the running game, in two states of the story, and lists doors, plates,
   signs and wall pictures that cross furniture or each other. Its first run found six more of
   the plan's doors on built things, all from step 0's "nearest free metre": the pantry's door on
   the wine trolley (the trolley moved 0.3 m), the aft checkpoint on deck 7 on the pinball table
   (now at 189.15 m, between the cabinets and the claw machine, which moved 0.2 m), the lighting
   booth's door on a balcony seat (that seat left out, the door at 206.1 m), the gym's checkpoint
   on a treadmill and in the window wall (now on the strip of wall at 82.72 m), the chapel
   lobby's checkpoint on the side table (the table moved to 69.75 m). The list is empty but for
   the cake's stand-in switch, which step 9 removes.
5. **The sweep of every person in place** (`tools/shoot_people.py`, eight sheets) found one
   fault of the runner's kind: the boat drill's crewman cranked the air. A winch stands at his
   hands now (a PixelLab map object). On the way: the drill's rope had `back`, a depth that is
   behind the ship's side outside, and had never been seen; it shows now.
6. **The user: "What are they doing? They look weird and out of place"** (the two dancers sat on
   the floor by the stalls after the stage's beat, my addition in step 3). They stand by the
   front row now, facing each other, with a breathing idle each (6 generations). The check has
   a new question for this: what is this person doing, and would the user know why here?
7. **`region8`'s flaky first climb was the test's:** it walked along the sun cover for a fixed
   3.2 s and sometimes jumped a few steps short of the rail, into its side. It walks until she
   is at the rail now (the golden path too). A jump from the rail's foot clears it every time.

PixelLab for this: the winch (1), the dancers' idles (6).

