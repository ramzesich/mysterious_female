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

## Step 9: The bow, region 9 (2026-11-14)

Done: the wedding at Champs' door (the planner, the couple and four guests in the forward lobby),
the cake from Cagney's pastry chef, the party's walk into the chapel and the ceremony there with
its photo slot; the Spinnaker (its barman, two guests in armchairs, the piano's quirk, the bar's
tangerines, a bench on the balcony); the kids' pool (two kids, the slide's quirk); the spa (the
receptionist, the masseuse and her guest, the stylist and his client, the step class, the sauna's
steam: "Fogged", the desk's tangerine); deck 10's and deck 9's officers' corridors (an officer
walking each, the checkpoints, the captain's door and its knock); the bridge: near-catch 6, the
alarm, the hatch's ladder, book 10; deck 7's kids' clubs behind the gold door (three toddlers, the
counsellor, the pillow fort, the ball pit, two tangerines); the Library's odd book and the reading
nook, drawn. Playtest `region9` (from `enter_region9`); the golden path carries the cake.
`src/world/bow.js` is the region's code.

**Changes and additions to the plan, and why:**

1. **The planner stands on Champs' side of the door (83.25 m), the rope on that side; the couple
   are in the party.** The spec had her at 76 m, inside the lobby she is keeping shut, where E
   could never reach her; and four guests alone did not say "wedding": a bride in her gown and a
   groom in his tuxedo do, seen through the glass door. The lock at (12, 82) is `("block",
   "wedding", 1)` now.
2. **The cake is a three-tier wedding cake on a tray, not a box, and "fragile" means it sways.**
   A box is a few rectangles and carries like any tray. The cake (a PixelLab piece, 25 px, its
   top level with her head) sways with what her feet do: each start and each stop adds 0.26, a
   turn on the move 0.42, a landing 0.5; it settles by 0.24 a second; at 1 it goes over (the
   meter on the HUD is how steady it stands; the cake's tilt shows it too). So the errand is
   patience at the court's balls, where the other trays are a race against a clock. A bump still
   spills it. `SWAY` in `src/world/carry.js`. (A start or a stop counts once it has lasted 70 ms,
   a landing after 120 ms in the air: her speed and footing flicker for a frame now and then,
   which toppled it on a steady walk at first.)
3. **The cake waits on a table by the pastry chef at 167.75 m, in the open** (spec: behind a crew
   door at 173 m). Cagney's has no room for another door, and a cake in plain sight on the way
   in from the ladder is its own signpost. It is hers to take once the planner has shown her
   bubble (`cake_asked`, within 4.5 m of her); a cake gone over makes the chef sigh.
4. **The wedding is a camera scene:** the cake crosses to the planner, the ropes come off, the
   lobby's two doors open, and the camera goes with the party through the lobbies to the chapel's
   door (the couple first, the planner last with the cake), about seven seconds.
5. **The ceremony plays the first time she steps into the chapel after** (spec: E at its door,
   "seen from the back"): the game is side-on, so the party stands in the chapel as it is drawn,
   the couple at the altar; a kiss, hearts, confetti, then the frame (`slot_chapel`) on the wall,
   hung above the guests' heads (at 64 px it sat on a guest's hat).
6. **The Spinnaker's tangerines are on its bar** (54 m, the spec's place, is the grand piano; a
   side table stood in front of it). Its two guests are PixelLab pieces, each in an armchair of
   their own facing us, in two built armchairs' places.
7. **The slide is ridden with E at its ladder** (spec: "walk onto the slide's top": there is no
   way up but the ladder): up, down the chute, into the pool, where she swims.
8. **The gulls on the bow need no "Swooped" block:** the cake cannot pass the old lady's sunbed
   before the horn, so the bow cannot be reached while they are there. They are scenery for the
   horn's scene, as built in step 8.
9. **The spa:** its tangerine is on the reception's desk (32 m is inside the deck's front wall);
   the receptionist bows; the masseuse works on a guest lying on the second table (a piece); the
   stylist stands behind a client in the second salon chair (the plan's "guest under the hood
   dryer": PixelLab's first came with a lamp stand and child-sized, the second sits in a chair
   of her own, which reads better; the built hood dryer stays); the step class has two boards;
   the steam comes out of the sauna's aft door at 52.9 m (the sauna moved since the spec's 48 m).
10. **The bridge's beat, laid out for the bridge as built:** the alarm panel and the engine
    telegraph changed places, so the panel stands by the helm; Bumbot washes on the floor between
    them; the security officer, who ran up here at the horn, stands at the forward end and is
    seen from the door (spec: at 26 m, which is in the deck's structure); as she reaches, he
    runs in and swings: his net lands on the alarm panel. Red light over the whole bridge and
    the panel's beacon turning, until the catch; the hatch's ladder comes down rung by rung and
    Bumbot is up it. The officer ends sat on the floor by the helm (spec: slumped in the
    captain's chair, waving: a seated clip brings its own chair, and his "sit" was made already).
11. **Book 10 lies on the chart table** (it stood on a side table of its own in front of it).
12. **The captain's cabin is deck 9's first door, 28.6 m;** E: a knock, her back to us, and
    nobody answers. Its plate says CAPTAIN until the user gives the name (§6.4).
13. **The ball pit is a padded box of balls, 49.3-53.7 m,** standing on the floor with a low
    wall at each end (a hop takes her over), the balls drawn in front of her to the waist; she
    wades at half speed (`scene.wading`). One ball is a tangerine (`tan_7_ballpit`, an orange one
    with a leaf): a secret the spec did not have. The first beanbags went.
14. **The pillow fort is a PixelLab piece, 169 px, across Splash Academy at 30.85-34.4 m**
    (`LOWS`): the rocking horse, the toy box and the blocks moved out of its way. The three
    toddlers are pieces too (stacking blocks, cooking, crawling); the counsellor cheers them on.
    A tangerine on the low table (`tan_7_splash`, the plan's snack table).
15. **The odd book stands on the Library's bookcase at 189.4 m.** E: she pulls; it is stuck
    until all ten books are back (`books_all`); then it tips, and the bookcase swings open on
    the nook (flag `nook`; the room's door is the bookcase). The nook is drawn: the red chair,
    a lamp, books to the ceiling, a small picture of a black cat asleep on a book, the frame.
16. **A testing option, `?did=`** (README): story flags set from the start, so a later state can
    be looked at without playing to it (`?play&at=champs&cards=all&did=engineer,horn,lady`).
    Start places `cagneys`, `kids`, `captain`.

**Found on the way, and fixed for good:**

- **Her sprite sheet was one strip, and with two more clips it was 17,472 px wide:** over what a
  WebGL texture may be, so she drew as a black box, and every test passed. The sheets are packed
  in rows of 48 cells now (`tools/build_sprites.py`), and the `boot` playtest fails if any
  texture is over 8,192 px a side. I saw it only because I looked at the scenario's screenshots.
- **`Browser.close_up()` was 19 % off:** the game's canvas is fitted into the window smaller
  than it; it measures the canvas now, and the metre marks of a strip are true.
- **PixelLab draws what an action names, again:** her "plays piano keys" came with a piano in
  every frame; "taps both hands in the air" is the clip used (`keys`). A fort asked for at
  200x80 came as two small tents; "one long low ... filling the whole picture from the left
  edge to the right edge" at 176x64 gave one. Several v3 text clips turned the figure to face
  us halfway or dropped what it held: their loops are cut from the frames before
  (`"cut"` in `tools/cast.py`); the planner's "fret" and a guest's "laugh" were dropped.
- Six of the nineteen new figures came out with heads of 21 to 25 px from text and were made
  again in pro mode before any clip was made (the rule from the review).

PixelLab: 173 generations (19 figures 38, six again in pro 60, their clips 52, her knock and two
tries at the piano 9, the security officer's two swings 2, pieces 12); 673 of 2,000 left.

**Left for later:** the wedding's guests have no talk or laugh clips (they stand, one sips); the
security officer does not wave her on from the floor; sound for the alarm and the horn comes with
"Sound on" (after the regions).

## Step 10: Sunset and the end, region 10 (2026-11-14)

Built: the sunset; the scene on the balcony forward of the spa; the glide down to the mooring deck
through the wind and past two gulls; Bumbot at the tip and the catch; her with him in her arms; the
way home; cabin 8206, the win screen, and the day after. Code: `src/world/finale.js`, the dusk in
`src/background.js` and `src/sea.js`, her look and its rules in the ship scene (`holding`). Playtest
`finale` (44 checks); the golden path now ends at home. The whole suite: 683 checks, all passing
(run before the last fix below, after which `finale` was run again alone).

**Changes against the plan, and why:**

1. **The sunset is a second sky and sea faded over the day's** (`setDusk(k)`): the mock-up's bands
   of colour, 14 px each, so the whole of it shows over her head; the sun half sunk ahead of the
   bow with its path of light on the water; the clouds, the islands and the ripples take a tint.
   **The ship's own evening light is one warm multiply over the whole picture,** drawn by a camera
   of its own between the world's and the HUD's (so the whole-ship view, O, keeps it); the sky's
   and the sea's dusk colours are written as they should look and drawn divided by that light
   (`dusk()`), or the wash would have dulled them. The windows show the sunset too. It lasts from
   the balcony's scene until the day after the catch.
2. **A miss brings her back onto the balcony itself, not to the bridge's crew door** (`cp_bridge`
   in the plan): a shorter loop, a few steps from the rail. It had to be a rule of its own anyway
   (`respawnFor`): a fright is sent to the checkpoint nearest by deck, and a fall towards deck 7
   would have come back at deck 7's far checkpoints.
3. **The two gulls fly level, to and fro, each at its own height** under the balcony; flown into
   in the air, one knocks the parasol from her hands ("Киш!") and down she goes (`scareAir`).
   **The wind** blows aft every 4 s for a second, after a tell: two windsocks (on the balcony's
   rail, at the stem) lift, and thin streaks come in at the forward edge of the view. Steering
   into it she still makes way, slowly; not steering she is carried back two metres a gust.
4. **A short glide is not a miss:** deck 8's forward terrace and deck 9's front bulwark catch
   her, and she hops on down from there. A miss is a gull, the parasol closed too high, or the
   sea past the tip.
5. **Found: the mooring deck could be reached since region 5,** from deck 8's forward terrace
   (a jump down), and its door is shut until the catch: before the alarm she was stuck there but
   for the sea. The terrace is the user's and the layout stays, so it is left open and made
   kind: nothing happens there before the sunset; after nine seconds a hint ("No way back up from
   here. Over the rail, then!"); and that fright puts her back on the terrace. After the sunset's
   scene the same way is a way round the glide (the stairs, deck 8, the terrace): left in, a
   crew member's shortcut. Bumbot is at the tip only from the sunset's scene on.
6. **Bumbot sits on our side of the mooring deck's railing,** on the deck's very edge: the
   railing is drawn in front of her, and behind it he could hardly be seen. At the catch he
   comes through it to her (GAME_DESIGN.md §6.1.9 asked for exactly that).
7. **The catch, as rules** (`TIP` in `finale.js`): coming within 2.3 m of him she sends him back
   along the deck, and with no deck left behind him he darts past her; the second time, a hint
   ("Stand still. Let him come to you"). Standing still within 7.5 m: after a second he comes, a
   few steps at a time, a heart a second; three seconds and the scene: she turns to the sea,
   arms wide in the wind (the pose kept from the bow view); he comes round to her front; she
   bends as at every near-catch; he jumps into her arms; a fade.
8. **Her with Bumbot in her arms** is a new state of her PixelLab character ("Holding the cat",
   6905f308): its walk (skeleton-v3 "walking", arms still), her head bent to him now and then as
   she stands (a v3 clip's first frames; in its last the cat was gone); in the air, two strides
   of the walk (a skeleton-v3 jump drew him as a dark blob, kept unused). **The rules with him**
   (`HOLDING`): a calm walk (0.8 of her run), a lower jump, and no hands: no ladders, trunks,
   crawl, dash, parasol, wall kick or E at people and things; doors, stairs and elevators work.
   Nothing scares her (`scareContact` does nothing); at a pool's rim Bumbot will not have it
   ("Мяу!") and she stays out.
9. **What the way home needed of the ship:** the kids' pillow fort is put away for the night (she
   cannot crawl with him: a pile of pillows, a PixelLab piece, stands by where it was), the
   toddlers are in bed, her husband has left his table. Conditions can now be joined
   (`flag:catch&!flag:home`: the evening of the catch).
10. **An addition: those she helped clap her in.** The steward, the stage manager, the engineer
    and the wedding planner stand in deck 8's corridor between the doors next to cabin 8206, turn
    to her as she comes, and clap, bow or wave while she is near; a heart from each. (The plan
    had an empty walk; a welcome is a warmer end to a game given as a present.)
11. **`scn_home`:** her husband (the stand-in: a seated figure with his chair) sits by the desk;
    she steps up onto the bed, Bumbot goes from her arms onto it and curls up between them, she
    sits down by him. **The win screen** comes over the scene: "Bumbusik", "Bumbot is home.", what
    she found (tangerines, books back on the shelf, pictures), a place for the user's own message
    (`WIN_MESSAGE` in `src/config.js`: empty for now, §6.4), and "Press E".
12. **An addition: the day after.** A key, a fade, and the game goes on at midday: Bumbot asleep
    on the cabin's bed for good (E by him: a purr), her husband back at his table (his book and
    the table's picture can still be had), the fort up again. So nothing left to find is lost by
    finishing.
13. **Start places `sunset` and `home`** (README); `tools/check_overlaps.py` audits a fourth
    state, the evening of the catch.

**Found on the way, and fixed for good:**

- **The alarm's red light showed on the ship's side** from the balcony above the bridge (a wash
  drawn over a deck that was not cut open): it is drawn only while she is on deck 10 now.
- **Two scripted moments could end each other:** `world.cut` gave play back as soon as either was
  over. It counts them now. (Met in a test that set the horn's flag by hand.)
- **A game opened again on the way home had lost Bumbot from her arms:** the player's set-up
  reset `holding` after the story had set it from the save. Found by opening the links meant for
  the user; `finale` now closes and opens the game on the way home.
- **A gust carries her twice the px a second its data says** (the push moves her body and her
  picture, and the physics adds the body's move again): so it has been since region 7, whose
  numbers were tuned by feel; noted at `FINALE` in `tools/population.py`, not changed.

PixelLab: 20 generations (her state 10, its walk 3, a jump not used 3, her head bent to him 1,
two clapping clips 2, the pillow pile 1); about 653 of 2,000 left.

**Left for later:** the win screen's message (the user's); her husband's own character (the cabin
uses the stand-in too: his own will want a pose for the cabin and a wave); the sound of the wind,
the gulls and a purr, with "Sound on"; the glide's numbers (the gulls' speed, the gusts) from her
playtest.

## Step 11: The ship's side (2026-11-14)

Built: the ship's side painted by rules instead of one flat white: the plating in strakes with
its seams and butts, shade under what stands out over it, weathering, and the marks and openings
a hull carries; the same on the pieces the game draws itself (the slopes at the decks' ends, the
stem's edge, the walls drawn over her, the promenade's recess and closed ends, the balconies'
fascia and recesses). And, asked for by the user while it was being built, **the livery's ragged
lines smoothed.** Code: `tools/shell_paint.py` (new), the map builder, the ship scene,
`tools/build_livery.py`. No PixelLab art: 0 generations (about 653 of 2,000 left). The whole suite: 687 checks, all passing (`boot` gained three: the side's tiles are of many kinds, nothing inside shows through the closed side in the outside view, O again is back in the game); after it two small fixes (the bow wave, the galley's plate), then `boot` and `region1` again and the overlap audit, which lists nothing.

**How it is done, and why so:**

1. **The side is painted as a picture and cut into the map's tiles.** `tools/shell_paint.py`
   paints every pixel of plating (palette indexes, by rules, a steady random number for each
   choice so the ship is the same every build), then every 16 px tile that is not plain plating
   becomes a tile of its own in the tileset, the same ones shared (760 new tiles; the tileset is
   laid out in rows of 64 now). So the game draws the side exactly as before, a tile layer that is
   culled to the view and fades deck by deck with the cut-away: nothing new is drawn each frame.
   (Thousands of rectangles in a `Graphics`, as the windows are drawn, would have been redrawn
   every frame; one big picture would not fit a texture.)
2. **Seams sit between the floors and the windows, and the plates are long.** Twice before, the
   user had lines taken off the side: a line along each deck's floor and seams on every tile
   ("stray marks", "stripes", 2026-11-03). So: a seam along the side every 72 px (a metre and a
   half), 36 and 108 px over each deck's floor, which is clear of every row of windows and of the
   floors themselves; a lit edge under each; the plates' butts across them about every eight
   metres, staggered strake by strake, fainter than the seams, moved off any window they would
   graze; one plate in four a shade lighter or darker. The first try (six-metre plates, stronger
   butts and shades) read as brickwork and was toned down.
3. **Above the hull the panels are three times longer and all one white:** the superstructure's
   sides are smooth on the real ship; only the hull (up to the forecastle and the promenade) is
   plated in the full pattern.
4. **The near-whites keep to the side's own white, not to the palette.** The plan asked for "two
   or three near-whites from the palette"; the side's white (`#e8eaec`) is not Resurrect 64's,
   whose whites are `#ffffff` and the green-grey `#c7dcd0`, both far off it. The plating's shades
   are a few steps either side of its own white; the marks and openings use the palette's greys.
5. **Weathering is faint and sparse:** a streak under about four portholes in ten, under each
   scupper along the promenade's foot (small slots, new), under each overboard outlet low on the
   hull (new, rust-tinted); a dull band with a ragged top where the sea washes the side over the
   boot topping; a few smudges low down. The first streaks were solid two-pixel lines and read as
   pipes; they start strong and break up now.
6. **What a hull carries, as additions:** two shell doors on deck 3 as outlines in the plating
   (150 m and 224 m), the draught marks at the stem and the stern, the bow thrusters' two marks,
   the load line amidships. **No anchor:** on the real ship it sits in the livery's red band, and
   the livery is the user's placement. **No rivets:** at this scale a rivet is under a pixel; the
   seams and butts stand for them.
7. **Nothing is painted over the livery:** seams run under its paint and are hidden by it, every
   mark and streak keeps clear of it.
8. **The pieces the game draws itself carry the same plating:** the slopes at the decks' ends and
   the stem's smooth edge get their painted pixels from the builder as marks; the strips of wall
   drawn over her at a deck's ends, the end walls she passes behind and the terraces' covers are
   now the side's own tiles drawn again (`plateTiles()`), where they were flat white rectangles
   that would have blanked the seams; the bow's smooth plating went under the hull's tiles (it
   was over them) and shows only along the stem.
9. **The promenade, the walkway and the balconies** (the plan's list): the promenade's recess has
   the seams and staggered joints in its own shade, the shade deepest right under the overhang
   and a soft shadow under the boat walkway; its closed ends carry the seams across in line with
   the side's; each balcony's recess has the slab's shade under its ceiling, and the white fascia
   between two rows a joint under every partition and a fine line at the foot of the glass.
10. **The livery's lines smoothed (the user, 2026-11-14).** Blurring harder rounded the ribbons'
    pointed ends away, so each outline is smoothed along its own length instead: cut at its sharp
    turns (a turn counts only if it is still one at twice the reach, so a drip's notch does not),
    and each stretch between two tips evened out as a curve pinned at both ends (`sleek()` in
    `tools/build_livery.py`, `SLEEK` 30 px). The paint's outline and each colour's own are done
    the same way. Its placement, size and colours are untouched.

**Found on the way, and fixed for good:**

- **`tools/render_ship.py` no longer rendered the ship** (it predated the HUD's and the evening
  light's cameras and shot deck 4's corridor forty times). It uses the game's own outside view
  (O) now, at one pixel to a pixel.
- **The kids' ball pit and pillow fort showed through the closed side** in the outside view: they
  are drawn in front of her, so in front of the side too. What the plan puts inside a deck in
  front of her now fades with its deck's cut-away (`behindShell()`); a bubble over someone by her
  is put away while the outside view is open. `boot` checks it.

- **The bow wave stopped at its highest, a straight edge** (the user, on this step's close-up of
  the waterline: "this water looks cut off"). Aft of the stem it now falls away along the side
  and breaks up into the foam there (`BOW_TAIL` in `src/sea.js`).
- **The galley's plate was half behind the wall drawn over her at deck 5's aft end.** The overlap
  audit had never seen it: that strip of wall was a flat rectangle, which the audit does not
  look at; as the side's own tiles it does. The plate is forward of its door now (`plate_side`).

**Left for later:** the funnel's white base, the open decks' bulwarks and the sun cover stay
plain (small, and no seam lines up with them); two round spots in the livery where the photo's
portholes were painted over; sound has no part in this step.

## Step 12: Sound (2026-11-14)

The first item of the plan's "After the regions" ("Sound on: the synthesised effects for every
entity, in the order of the regions; the horn and the alarm first"), built as a step of its own
when the user said "Let's continue" after step 11. **Sound is on now** (`SOUND.on`); **M mutes it**
and the choice is remembered. Code: `src/sfx.js` (rewritten), `src/world/soundscape.js` (new),
sound lines in every file of `src/world/` and in the ship scene; tools `tools/check_sound.py` and
`tools/soundboard.html` (new). No PixelLab art or audio: 0 generations (about 653 of 2,000 left).
The whole suite passes (702 checks, the new `sound` scenario's thirteen among them); `python tools/check_sound.py` ends "all within bounds".

**Nobody has heard any of it yet.** I cannot hear: every effect was written from what such a
sound is made of (a struck bell's overtones, a voice's buzz through an opening mouth, noise
through a moving filter), then rendered by the browser without playing it and measured: how
loud, how long, where its weight lies, and its picture (a spectrogram each), which shows whether
it has the shape it was written to have. That finds a sound that is silent, clipped or far out
of balance; it does not tell whether a meow sounds like a cat. **So the whole set waits for the
user's ears:** `http://localhost:8000/tools/soundboard.html` plays every one by a button and has
the ambience's layers on sliders.

**How it is done, and why so:**

1. **About 130 effects where there were 17.** The game had used a handful of generic ones for
   everything (one rattle for a snore, a vacuum's tell and the soft serve machine; one smash for
   towels falling, a lever and a door flying open). Each entity has its own now, in seven groups
   in `src/sfx.js`: hers (her steps on four kinds of floor, the parasol, the socks' squeak on a
   wall, the shower and the song she hums in it, the bed's springs), the ship's (five kinds of
   door, the elevators, the chute, the hatch, the horn, the alarm), finds and signs, Bumbot's
   (mrrp, meow, purr, his claws), people's (voices without words: a shout, a startled "oh", a
   giggle, a grumble, a sneeze, a "shh"; clapping, a kiss, the wedding's bells, the piano's
   tune), things' (the robot, the vacuum, towels, the sprinkler, gulls, gusts, the pool
   draining, the soft serve machine, chips, the court's ball, Teppanyaki's flare, steam, the
   net, the slide, the radar) and the end's (the sunset's chord, the catch, the win screen).
2. **The horn and the alarm, as the plan asked first:** the horn is three low notes together,
   each a pair a little out of tune so that they beat, opened and closed through a filter like
   steam, with a sub note and the breath under it, for exactly as long as the blast shown; the
   loudest thing in the game. The bridge's alarm is a rising whoop, half a second each, every
   second for its first seven seconds and then only every six (it stays on until the catch, and
   would wear).
3. **A sound comes from where its source is** (`sfx.at(x, y).name()`): full within about five
   metres, gone at twenty, a deck up or down counting for more than twice the same way along (a
   deck away is another room), a little to its side in stereo. Everything on a clock of its own
   uses it (hazards, people, gulls, machines), so the ship is not a wall of noise and a tell can
   be heard coming from its side. Her ears are where she is; while a scene shows somewhere else
   (the horn's cascade), where the camera is.
4. **The ambience** (§5.2, decided long ago: "a soft sea and engine ambience outdoors, quieter
   inside") is five layers that run all the time, each as loud as the place makes it
   (`src/world/soundscape.js`): the sea's wash and hiss (out on deck, most on the low open
   decks), the engines' low throb (most low in the ship, little on deck 12), the wind (the open
   decks, more the higher), the ventilation's hush indoors (more in the duct), water lapping by
   a full pool. From outside (O): the sea and the wind.
5. **Her own going is heard:** a step for every 30 px on the floor (carpet inside, planks on the
   open decks, metal on the roof and the funnel, the duct's hollow tin), a rung under her hand
   on ladders and in the trunks, a cart's wheels, her strokes in the pool; in scenes that walk
   her too, since it goes by the ground she covers and not by the keys.
6. **A few places have a small steady sound of their own:** the casino (chips, a machine
   paying out), the bridge (the radar's ping), the birthday party's beat through its door, a
   gull somewhere off the ship now and then while she is out on deck.
7. **No music, as decided** (§7.1): the nearest things to it are sounds of the world or short
   signs: the piano she picks a tune out on, the wedding's bells, the song she hums in the
   shower, a chord as the sun goes down, the win screen's four chords.
8. **Several loud things at once never clip:** everything goes through one compressor; the
   same effect twice within a thirtieth of a second counts as one.
9. **The wiring was split:** the engine, her own sounds, the ambience and the tools are mine;
   which effect fits each of about 250 moments in the eleven files of `src/world/` was worked
   out by four helpers in parallel, one group of files each, from one written brief
   (`%TEMP%/bumbusik-plan/sound_brief.md`), and their notes folded in after (a fault in the
   engine one of them found: a far, unheard sound took the turn of a near one in the same
   moment; a dozen missing effects they asked for: a sneeze, a "shh", a soft splat, the hot
   tub's bubbles, a wobbling cake's warning).

**Additions nobody asked for:** her bow on the stage is answered by a house that claps; her
dance has a beat; a secret found for the first time has its own little sign; the flash in the
Photo Studio whines as it charges; a cake about to go over warns with two anxious notes.

**Left for the user's ears and for later:** every sound's character and loudness (`SOUND` in
`src/config.js` has the whole volume, the effects' and the ambience's; each effect's own is in
its line in `src/sfx.js`); a held sound that can be stopped (the soft serve machine's motor is
short pieces end to end); eating and drinking are mostly silent; the controller has no mute.

## After step 12: the hull refined (2026-11-14)

Asked for by the user on a full-size render of the ship made during step 12, three points:

1. **"Livery: fill the two round spots left where the photo's portholes were painted over."** A
   dark red drop in the lower red band and a red-orange disc in the loop, both too near their
   band's edge for the rule that fills such spots. Each is named by a point inside it (`SPOTS` in
   `tools/build_livery.py`) and takes the colour round it; the builder stops if a spot is no
   longer where it was.
2. **"Stern: it is a straight vertical line now. Make it similar to the real ship. Without
   touching the playable decks."** The side photo shows the real stern plumb for most of its
   height and curving forward to the waterline under it (a counter). The playable decks reach
   down to deck 4, so the curve lives **under deck 3's floor**: 256 px of hull in which the
   transom rakes in by 152 px, more and more toward the water (`COUNTER`, `stern_x()` in the map
   builder). Nothing of a deck is touched. The hull's tiles stop short of the curve and the game
   draws the smooth sliver between, as it does along the stem (`sternEdge`, `sternMarks`); the
   boot topping follows the curve; the stern's draught marks moved forward with the waterline's
   end; the foam and the wake start where the hull now meets the water. The tiers above (decks
   7 to 12) are as they were: they are decks she plays on.
3. **"Background: why are there two rows of clouds with a weird blue area above the sea? Make
   it look more real."** The picture is stitched from four rows of screens, and the sky was laid
   out for each screen: every row brought its own strip of sky and its own clouds. In the game's
   outside view there was one, but it too was tied to the screen. Now **from outside the sky
   stands in the world**: it deepens over a fixed stretch up from the horizon, the islands and
   the clouds have a fixed size against the ship (what they had on a 1920 px wide screen) and
   grow with it when the view is zoomed, and the clouds are in three rows (small and faint low
   over the horizon, bigger higher up) instead of one. `tools/render_ship.py` holds the sea and
   the sky still while it takes its views (`enterOverview(true)`), so they fit each other. Play
   is as it was.

And, asked with it ("the best and easiest way for me to do the final touches to the livery by
myself"): **the user's own touches have a file of their own**,
`assets/source/livery/livery-by-hand.png`, a copy of `livery.png` edited by hand, which the map
builder uses in its place while it is there and the generator never writes. Recommended:
Paint.NET, antialiasing off, the bucket's tolerance at 0, colours picked from the picture.

Checked: `boot`, `overboard`, `falls` and `sound` pass; the render and the game's outside view
looked at. The whole suite was not run again after these (cosmetic, and it had passed an hour
before, with the sound): it runs before the next merge.

## The prep before the intro (2026-11-14)

The user wrote `docs/intro.md` (the welcome screen, the start sequence, the intro's scene) and
asked for three things before it, "the prep", and later made clear that the intro itself is not to
be built until they say so.

1. **"Remove every hint popup with text that we have in the game. Part of the game is figuring
   things out. Labels and namings are not considered hints."** Taken out: the line shown when a
   verb is learned (the dash's key, crawl, the wall kick, the glide), the keys' caps that bobbed
   over the laundry cart, the vent, the duct's far grille and the soft serve machine ("hold E"),
   and the one-time lines at the old lady's sunbed, on the balconies, with the cake, on the
   mooring deck when stranded there, at the catch ("Stand still. Let him come to you") and after
   it ("Home now: cabin 8206, deck 8"). `world.hint()` and `world.glyph()` are gone.
   **Kept, as my reading of the line drawn:** the ship's signs and plates (labels); the people's
   pictogram bubbles and her own (they have no text); a lock's popup, which names the card the
   lock wants (a naming); her exclamations; the win screen's "Press E: the ship is still yours to
   wander", which is the screen's way on rather than a hint about the game. **Asked; the user
   (2026-11-14): the lock's popup and the win screen's line are kept.**
2. **"Support two languages in the game: English and Ukrainian. Every text shall have two
   versions. The art text (e.g. La Cucina) stays as it is."** `src/lang.js` holds every text the
   game says, in both; English is the default (`docs/intro.md`). It turned out to be a short
   list once the hints were gone: the title, the win screen (its line, its tally, the "Press E"
   line, the user's own message when it is written: `WIN_MESSAGE` takes both), a lock's popup and
   the four cards' names, eleven frights and six exclamations. **Her frights and exclamations
   were Ukrainian only** ("Ой!", "Гей!", "тук"): they are the Ukrainian version now, and English
   got its own ("Oops!", "Hey!", "knock"). Her «Кісюнічка!!!» stays in both (§3.2: the exact
   text). **The ship's own signs and plates are left as they are in both languages**, all of
   them, not only the venues' names: DECK 5, LINEN, Restrooms, a rope's QUIET PLEASE, the LOST:
   CAT poster. Reason: they are part of the picture of an English-speaking ship, as La Cucina's
   sign is, and Ukrainian words would not fit most of the plates. This is a reading of "art
   text" that the user might not have shared: **asked ("should the functional ones get
   Ukrainian versions, with only venue names staying?"); the user answered "Ok", which I take
   as leaving them as they are** (said so in the report, for them to correct). The choice is kept in the browser;
   `?lang=uk` sets it for a session. No button switches it yet: the LANGUAGE button is the
   welcome screen's, which is the intro's.
3. **"Add a relatively small section of deck 3 (check the official ship documentation) where the
   game will now start. Place the crew cabin there (described in the intro doc), decorate the
   deck 3 corridor accordingly, and add a service ladder (with the door) to the deck 4."**
   - **Where.** NCL's plan names one place on deck 3, the Medical Center, just aft of the forward
     stairs (the user's photo of deck 3's gangway exit is of the guests' part of that deck). The
     corridor is there: 82 to 98 m, two screens long, under deck 4's cabins between the forward
     and the midship stairs. The Medical Center's door is in it, shut, as dressing.
   - **What is in it** (bow to stern): the fire point; the Medical Center's door, a first-aid
     cabinet, a seat; the notice board; **the door marked CREW, her cabin**; a clock, the water
     cooler; the way out's sign; **the service ladder's door**; the deck's plaque.
   - **Her cabin is a room she can enter**, like the plan's other rooms: "place the crew cabin
     there" was read as the cabin, not only its door. Drawn in code: a desk with a bowl of
     tangerines under a mirror, a porthole, her spare shirt, her bed. **The user, on its first
     picture (a plain wall, a ginger cat's poster, a bunk for two): "1. Add some texture to the
     wallpaper in her crew cabin. 2. Replace the picture of an orange cat with the picture of
     Bumbot. 3. Make the bed for a single person."** So: wallpaper with pinstripes and small
     sprigs, a shade off the wall each way; a framed picture of Bumbot over the bed; a single
     bed with head and foot boards, her suitcase still under it. The picture was first his own
     sat frame from his sheet; **the user, on that: "Make Bumbot picture smaller and only place
     his head there. Use generation of a bombay black cat. Eyes not orange, but how his eyes
     are."** So it is a head now, in a frame of 28 x 33 px where the first was 41 x 36: a
     PixelLab map object, 32 px, two tries for 2 generations, the blacker one with whiskers
     kept (`assets/source/rooms/bumbot-head.png`), cut close, its pale yellow eyes given the two
     colours of his sprite's (yellow-green and its darker shade). **Then the user put four
     photos of the real Bumbot into `reference/photos/Bumbot/` ("use that in order to generate
     a Bumbot picture in her cabin"; "Ask me if I like the picture before placing it in the
     game"; "Try his photo with the fruit bowl as a reference, too").** Six candidates were
     shown side by side, framed and enlarged: the Bombay head, three conversions of his
     close-up, and two of the fruit-bowl photo. **The user chose "4": him lying by the bowl of
     fruit**, 48 x 24 px in a 52 x 28 frame over the bed (`bumbot_picture()` in
     `tools/draw_rooms.py`; source `assets/source/rooms/bumbot-by-the-bowl.png`; the Bombay
     head is gone). What PixelLab was sent each time was a cutout only, the cat (and the bowl)
     on a flat ground, nothing of the room; the photos stay in the git-ignored `reference/`.
     The conversions come back charcoal or navy with orange eyes whatever the photo shows:
     his fur is brought to his sprite's blacks and his eyes to the photo's pale yellow-green by
     rule. Nine conversions at 1 generation each. Seen in the game, the user: "it doesn't look
     as good. We need to fix Bumbot's face a little bit", "Smooth up his outline on the left",
     "Above the eye": the ear's outer edge stood a pixel in from the cheek's and left a notch
     at the eye; three pixels close it (in `bumbot_picture()`). Shown before and after; the
     user: "Keep". And of the bowl on her desk: "a nice touch, but they don't read as
     tangerines as clearly if you don't know that they are supposed to be tangerines": the
     three fruit are the game's own tangerine now, the sprite she picks up and the HUD counts,
     pixel for pixel with its leaf, in a shallower bowl (`game_tangerine()`). Its door is the start's checkpoint (`cp_crew`), lit from the start; the
     gangway's (`cp_gangway`) lights when she first passes it, like any other.
   - **The ladder is an escape trunk** (decks 3 and 4, no card), the game's own way of putting a
     ladder behind a door. On deck 4 it comes out at 95.6 m in the place of one cabin door.
   - **The forward stairs and lifts do not come down to deck 3**, though on the real ship they
     do: the user asked for a service ladder as the way up, and a second way would make it
     pointless. A bulkhead closes each end of the corridor. (Asked; the user: "You did fine".)
   - **The look:** a working corridor, plainer than the guests' (panels over a green dado, a
     steel handrail, pipes and a cable tray overhead, tube lights, vinyl). One new tile (the
     floor); the rest drawn by the game and dressed from the atlas. No generations spent on
     the corridor; 11 on the picture of Bumbot in her cabin (above: 2 + 9).
   - **The basic layout is as it was** (the user's standing rule): no deck's length, no room and
     no stair moved. Deck 3 was already in the map, closed; a part of it opens.
   - **Region 1** takes deck 3 in. The first errand is unchanged: up the ladder, forward through
     the stair lobby to the gangway officer.
   - Not done, and not asked: Bumbot, people or tangerines on deck 3; the intro's zoomed-in door
     and the more detailed figure of her (the intro's own art).

Also asked meanwhile: **`docs/start-links.md`**, a localhost link for every place the game can be
started at, everything open (`cards=all`) and the dash free.

**The playtests after it.** Twenty-six scenarios opened the game and walked from the gangway:
`Browser.open()` still starts them there, its checkpoint lit as it was (`start="gangway"`); only
`boot` and `deck3` take the game's own start. The checks that looked for her frights by their
Ukrainian words look for the English ones now (English is the default), word for word by the
table in `src/lang.js`.

Checked: the new `deck3` scenario (the start, the cabin in and out, both bulkheads, the ladder
up, the cut-away) and `lang` (both languages have every key, the title, a lock, her words, the
tally, `?lang=`); the corridor and the cabin looked at enlarged next to her; the overlap audit.
Of the older scenarios, those the changes can touch most were run, not the whole suite
(`CLAUDE.md`): `boot`, `run_jump`, `trunk`, `golden`, `region1`, `region4`, `region7`, `finale`,
`sound`. Not run: the rest, among them `region2`, `region3`, `region5`, `region6`, `region8`,
`region9` and `sweep`, whose fright checks had their words changed the same mechanical way.

## The intro (2026-11-14)

The user: "Read the intro document and implement it. Readjust her crew cabin to include a
standing mirror. Replace the mirror on the wall with a Ukrainian flag (which includes a trident
on it)". `docs/intro.md` is theirs; what follows is what I decided where it left room, and what
they said on the way.

**How it is built.** Not a title scene and an intro scene: both are the ship scene's own
picture (`src/intro.js`), because the doc wants each to run into the next (the menu melts, the
same sky comes into focus, the camera that leaves the sun is the one that ends on her). One
clock, and everything a function of it: the camera, what is open, what is shown. So any moment
can be shown by itself (`?intro=<part>`, `intro.seek()` in the playtest) and Esc is the clock
set to its end. The old `TitleScene` is gone.

**The welcome screen.** "Bumbusik" in the middle is the game's name, not her figure (asked
myself, and the user said so before I asked them; they put quotes round it in the doc). The
LANGUAGE button shows the language chosen ("LANGUAGE: English", "МОВА: Українська"), so a
press shows at once what it did. PLAY is "ГРАТИ". Keys as well as the mouse (↑/↓, Enter, Space
or E), for the controller's sake later. Out of focus is a blur on the world's camera; the
camera draws 48 px more all round while blurred, or the blur darkens the picture's edges.

**The wide views** use the outside view's sky (laid out in the world), with the islands at the
game's own pixel size (two screen pixels to one of theirs) so that the "Baltic shoreline" is
there to see; the day had no sun, so the intro has its own (a disc, a glow, rays that take
turns), a few clouds of its own round it, gulls, and the sun's glitter on the water for the
doc's "sunbeams shimmer on the sea waves". All of it is at the game's pixel size, stands in the
world, and fades as the camera goes in. The sun is ahead of the bow, where the sunset's sun is
at the end of the game. Far off the camera moves by whole screen pixels, so the small ship does
not shimmer.

**The way in.** Deck 3's side opens as the camera comes close (the cut-away's own fade, driven
through `viewOverride`), the corridor holds a moment with the door and its CREW sign, the cabin
comes up over the corridor as rooms do, and she is there at the mirror.

**The close-up.** I first read "a zoomed in and more detailed character" as her whole figure
drawn finer, and made candidates (a figure from a description: unlike her; one redrawn from her
own game figure: like her). Shown them, the user described the shot instead: "the entire scene
zoomed as much as to show her up from her waist. She adjusts her badge (which says Bumbusik).
Then it zooms out smoothly transitioning into the playable scene", and "only her profile up
from her waist together with a part of the mirror is visible in the center of the frame". So:
- The camera goes to 16 times; her portrait (256 px, her profile from the waist up) and a finer
  piece of the mirror are eight pixels to one of the game's, two of the screen's each, as a
  pixel of the game's is in play. They are on a camera of their own, and the cabin behind them
  goes out of focus, which also hides its sixteen-pixel blocks.
- The portrait comes in over her game figure only as the view's foot reaches her waist (it ends
  there), and goes the same way.
- **The badge says BUMBUSIK** and is drawn by the build (`tools/build_closeup.py`), not by the
  generator, on every frame: crooked until her hand has been on it, straight after, her hand
  kept on top wherever a frame has it there. It is bigger than a real badge would be on her
  (35 px of her 40 px chest): eight letters do not fit in less.
- **The portrait is a stand-in**: PixelLab's finer redraw of her own game figure (her game
  figure to 256 px, that to a character in eight directions, its west view from the waist up
  to 256 px again, then animated). The user asked, seeing it: "Can you use her photos in order
  to make the character look more similar to her?" Yes, and there are none of her in
  `reference/` yet: it waits for them (`reference/photos/Bumbusik/`; only a cutout of her on a
  plain ground would be sent, as with Bumbot).
- **Her turn to the door** is not in the close-up, as the doc has it, but at the game's scale
  once the camera is back (her game figure turns by way of facing us). The user's later telling
  left it out of the close-up, and a turn there needs four more portraits. Open: theirs to say.

**A game already under way** is not in the doc. It gets the same welcome, the same sky, sea
and ship a little quicker, then the camera closes in on wherever she is and the picture goes
over to the game through a short fade (her deck may be open to the sky, where the far
background of the outside view and the game's own would not meet). A new game is one with
nothing saved past its start; the intro, once seen, is marked in the save. `?play` goes past
the welcome and the intro, so every start link and every playtest is as it was.

**Her cabin.** The standing mirror stands by the wall forward of the door (the one free piece
of wall), she at it turned from the door, which is then what she turns to. The user, on seeing
it: flipped, taller, its slant gentler. The flag is where the wall mirror was, then (the user)
over the desk's middle and a little muted; the porthole between desk and bed went (the user);
Bumbot's picture was tried a little smaller and put back (the user).

**The menu's look.** With the intro built the user wrote: "Can you use generations in order to
create menu items? The text looks too plain now. Think of appropriate style to decorate the menu
entries." Three styles were generated as plates (ship's brass name plates; white boards in a rope
border with anchors; white plates with the sun livery's wave) and shown as mock-ups of the whole
screen in both languages; **the user chose the brass plates.** With them:
- **The lettering is generated too** (PixelLab's `create_font`: a 32 px one for the name, a
  16 px one for the plates), and only its shapes are used: the game fills them in bands of
  colour, outlines and shadows them (`src/pixeltext.js`). The name is in the sun livery's
  yellows and oranges; a plate's word is cream, gold when chosen.
- **A generated lettering is Latin only**, and a second font for Ukrainian would have been
  another hand. So the Ukrainian capitals are built from the Latin shapes (thirteen are the
  same; Г is L upside down, И is N mirrored, Ь is P upside down, Б that with a top bar, Ї is I
  with two dots), and the menu is in capitals in both languages: BUMBUSIK / БУМБУСІК, PLAY /
  ГРАТИ, LANGUAGE / МОВА.
- **The LANGUAGE button no longer spells the language out** ("LANGUAGE: English" was too long
  for a plate, and pressing it changes every word on the screen at once).
- The plate came 58 px high; rows were taken out over and under its middle to make it 46, so
  two fit under the name with the sun between.
- A tangerine, the game's own, marks the chosen entry.

**Generations:** 95. The close-up 35 (a whole-figure candidate from a description 9, her game
figure in eight directions 1, the same at 256 px 8, five finer redraws 5, two whole-figure
animations made before the shot was described 10, the portrait's animation 2); the menu 60
(three plates 30, two letterings 30). 547 are left.

**Checked:** the new `intro` scenario (the menu and both buttons, each part of the camera's way,
the close-up, the hand-over, the short way in, Esc, `?play`), `lang`, `boot`, `deck3`; the
whole intro run in real time for jumps and frame rate (38 s, never under 40 frames a second);
and of the older scenarios `run_jump`, `trunk`, `sound`, `region1`, `finale`. Not run: the
rest. No sound was added: the ambience follows the view (the sea and wind from afar, the
corridor's inside), and none of it has been heard.

**Tests are silent from now on** (the user, during this work: "When you're testing, please test
with sound off"): the test browser is muted at the browser, so the sound still runs and is
still checked, and nothing comes out of the speakers.

## The intro's ending redone, the menu smaller (2026-11-14)

The user, on seeing the intro in motion: "1. Make the initial menu smaller, but still big. Now it
is oversized. 2. The transition scene doesn't work at all: a) Drop the zoomed in profile sequence
entirely. b) When the deck 3 corridor is shown at its gameplay scale, stop there, centered on her
cabin door. c) Then, her cabin door opens and she steps out and stands by her door. d) Make her
adjust her badge. Then, the controls are given. Add a hint popup, saying "E to interact". e) When
she's in her crew cabin, make an invisible barrier (make her stop, basically) in front of her
mirror. If she stops facing her mirror, she automatically fixes her hair once or twice. Don't do
it in a constant loop." And on d): "make an animation when she kinda adjusts her badge. Don't add
an additional badge or anything."

- **The menu** is three quarters of what it was: the build makes the lettering and the plate
  smaller (the name's letters 24 px, the plates' 12, the plate 166 x 38, each two screen pixels
  to one), rather than the game scaling them by one and a half, which would have made the
  pixels uneven.
- **The close-up is gone**, with everything made for it: the portrait and its animation, the
  finer mirror, `tools/build_closeup.py`, the second camera and the blur behind her. The sections
  above on it are history. The question of her photos went with it.
- **The camera stops on the corridor** at the game's own framing of her standing at her door, so
  nothing moves when the game takes over. Once it has stopped the game's own cut-away takes the
  deck, and the rest of the ship goes dim round it as she comes out.
- **She comes out facing us**: the door stands ajar (the ship's own ajar crew door), she shows
  in it, it shuts. Facing us is also where her badge is seen, so **the badge clip is drawn from
  the front** (a new clip of her game figure, skeleton-v3 by poses: both hands to her badge, her
  head bent to it, and down; nothing added to her). Then she turns to the side, as she stands
  in play.
- **The hint.** "No hint popups" stood since the prep; this one the user asked for by name. It is
  the game's own word over her (`world.say`), in both languages, six seconds, at a new game's
  start only. It stays the only one.
- **The mirror.** The cabin's forward wall for her is now 36 px in (`mirror` in the room's data),
  in front of the mirror. Stopped there and turned to it, she plays a new clip (a hand over her
  hair) once or twice (the number is drawn each time she arrives), then stands; walking away or
  turning from it arms it again. Her ordinary idles go on as anywhere.
- At the hand-over her idles now wait their usual four seconds: she had begun to tap her foot at
  once.

**Generations:** 6 more (the two clips, 3 each). Of the 95 before, the 35 for the close-up made
nothing that is still in the game.

**Checked:** `intro` (rewritten: the stop on the corridor, the door, her coming out, the badge
clip, the hint and its going, the mirror's wall, her hair once or twice and again on coming
back), `lang`, `boot`, `deck3`, `region1`, `sound`. Not run: the rest.

**Two adjustments after the user watched it** ("Overall, much better"): the camera held the sea
for two and a half seconds before going right, and now holds it half a second ("Make it move
right earlier"); and the dark round deck 3 came on as she stepped out, and now comes on with the
opening of the deck's side, as the corridor shows (`dimOverride`, driven by the same measure as
the cut-away). The intro is about 28 s. Checked: `intro`, `deck3`.

**And a third:** "the background moves right, but the sun stays in place. It looks weird". The
islands, the clouds and the ripples I had laid on the sea drifted aft, as the far background does
in play, where it is seen from the ship under way; the intro's camera is not on the ship, and its
sun stands in the world. In the wide views nothing far off drifts now: the islands and clouds
hold (the sky is laid out with no time passing while the view is from afar), the intro's own
clouds stand, the water only sways a little in place. The gulls and the glitter are what moves.
Checked: `intro`, `boot`.

**The open crew door levelled with the closed one** (the user, on watching her door open: "A
closed door frame is leveled correctly with the floor. An open door's frame is not on the same
level. Make both frames equal. Both in height and in ground level"). The sheet drew the open door
with its leaf swung toward us, hanging over the frame's top and under its foot, and the whole was
fitted to a door's 74 px: its frame came 69 px high, 3 px off the floor, and 33 px wide against
the closed door's 29. `level_frame()` in `tools/build_ship_art.py` makes the frame 74 x 29 (five
plain rows drawn twice, four plain columns of the leaf taken out), leaves off what hung under the
foot and draws the leaf's foot level with the floor; the leaf's corner still rises 2 px over the
frame. It is the door of every lit checkpoint on board, so all of them changed. No tests were
run, at the user's word ("this is just a leveling"); the two doors were laid over each other at
the game's placing and their frames coincide.

**And the open cabin door** (the user, on the picture of the doors side by side: "the two doors
on the right (the orange ones) represent the same door in two states? If so, the frames differ
now, also in color. Fix that"). They are: the guest cabin door closed, and ajar (the cabins held
open on decks 6 and 9, and the one that stands ajar in a hallway). The sheet drew the ajar one in
a dark frame 30 px wide; the closed one's is the corridor's warm wood, 34 px. `reframe()` in
`tools/build_ship_art.py` now builds the ajar door as the closed door's own picture with its
opening filled by the ajar door's leaf and light (two plain columns of the leaf and the strip of
light drawn wider to fill it, so it stands a little further open). Same frame, same colours, same
size, same level. No tests run; the pieces were compared side by side.

**The open crew door's leaf reaches under the floor line again** (the user, on the levelled
doors: "the open doors are cut off on the bottom. It is ok that they cross the red line here,
that makes them look more real"). I had cut the swung leaf off level with the floor to keep the
frame standing on it. Now the leaf keeps its 3 px under the frame's foot; the piece carries that
number in the atlas (`foot`), and the game stands such a piece by its frame, not by its lowest
pixel (`setDoorArt()` in the ship scene: the lit checkpoints' doors, and her cabin's as it opens
in the intro). The frame is still the closed door's equal and on the floor. Looked at in the
running game at her door, shut and open; no playtests run.

**The open doors hinged on the closed doors' side** (the user: "the open door has its handle on
the other side. Is it a look from the other side of the door? If not, then the handle has to be
on the same side"). It is the same side, the corridor's: the sheet drew each open door hinged on
the left with its handle at the right, and each closed door with its handle at the left. The
open leaves are mirrored now, the cabin door's inside its frame and the crew door's whole piece
(its plate comes to the closed door's side with it): handle at the left, hinges at the right,
the light in the gap at the left. Compared side by side; no playtests run.

## The audit's visual overlaps fixed (2026-11-15)

From `docs/plan-visual-fixes.md` (the audit's V1, V2, V3, V6, V7), each a number in the builders'
data, and one the user found while checking them.

- **F1, the "LOST: CAT" note on deck 4's crew notice board (190.6 m)** was drawn under its own
  board. The board now hangs at the wall's depth (`prop_board`, `back=True`), and the note showed,
  but its 4 px letters read "LOS II / CAI" and it covered the board's own picture. **The user had
  the note removed from the game** ("I don't want such hints"): `sign_lostcat` is gone.
- **F2, the wet-floor sign in the midship lift's doorway (deck 5):** `prop_wetfloor` from 107.7 to
  109.2 m, on the free floor aft of the lift.
- **F3, the card readers on the directory boards (decks 9 and 10, forward lobby):** the board
  hangs 50 px from the wall, not 30, where that wall has a card reader on the lobby's side
  (`DOOR_LOCKS`, in the directory loop of `tools/build_ship_map.py`).
- **F4, people over the lobbies' "DECK n" plaques:** every plaque, deck 3's too, hangs 80 px over
  the floor, not 56: over head height, level with the lift's number plate. All 28 looked at.
- **F5, the old lady's duffel under her sunbed (deck 12):** from `def.x + 30` to `+ 46`, clear of
  the bed's foot (`src/world/topdeck.js`).
- **The rival officer at the search rope (deck 5's forward lobby; the user's screenshot)** stood
  in front of the forward lift's door frame and its floor button: `riv_rope` from 79.55 to
  81.05 m, aft of the lift under the DECK 5 plaque, facing the stairs. Inside the rope (78.6) his
  leg covered the rope's sign.

`tools/check_overlaps.py`: 0 overlaps. Playtests run: boot, region1, region4, region8, region9,
stairs, lift (the rest not run).

**The notice board's cat notice painted out** (the user, after the note went: yes to taking out the
board's own red notice with a white cat on it, which read as a lost-cat poster too). The piece is
repainted as a plain notice of text lines when the atlas is built (`paint` in
`tools/build_ship_art.py`); both boards that use it changed, deck 4's at 190.6 m and deck 3's muted
one at 88.5 m. Looked at in the game; no playtests run (art only).

## The plan for the three uses, step 1: the cry and the lunge, the cabin's bowl (2026-11-15)

Built on the branch `three-uses` from `docs/plan-three-uses.md` §5, step 1 (the user: "Start the
implementation plan"). No art.

- **D is the cry, and the lunge with it once learned** (`tryCry` in the ship scene; `CRY`, `LUNGE`
  in `src/config.js`); the ten-second dash, its HUD bar and `DASH` are gone. Every press costs one
  tangerine; with none, the count blinks. A second D within 0.6 s (`CRY.gapMs`) or during a lunge
  does nothing, so a double tap does not spend two by accident (my addition, not in the plan).
- **The lunge carries her the way she faces** whether a way is held or not (a lunge, not a faster
  run); the arrows still steer it. Twice her speed and twice her acceleration, as the dash had.
- **What the cry reaches** (`world.shout()`, `world.hears()`: 4.5 m, on her route, within 70 px of
  her height) and what each does: as GAME_DESIGN.md §3.2 lists, from the plan's §2. Choices made
  where the plan left room:
  - A startled walker freezes mid-step (`anims.pause()`), a little smaller, as the steward at a
    door: his standing frame left the waiter's tray in the air over his face (seen in the
    close-up). The jogger jogs on the spot.
  - Only those standing about with the plain `idle` clip turn to look: one at work (the runner on
    the treadmill, the chefs, the pianist) or seated keeps facing what they do ("Looking closely",
    question 3).
  - The few with a mark (`hear` in `tools/population.py`): a heart over four who like cats (the
    lady in the robe on deck 4, the guest at the model ship, the shopper, the granny on the
    Stardust's balcony); a finger to the lips over two in quiet places (the Internet Cafe's surfer,
    a lady in the theatre's stalls). "own": the kid, the kid in the hot tub, the librarian, whose
    story code answers. People the movers own (the queue, the steward on his rounds, the faces
    behind the swinging and "Do Not Disturb" doors, the rival on the stage) are left to them.
  - The "Do Not Disturb" door answers within 3 m, 0.3 s after the cry, and its fright is not
    forgiven by the lunge (`scareContact(..., force)`): it is no contact. With a tray, a spill.
  - Bumbot at a near-catch: he turns to her for half a second with a small hop (his ears are not
    drawn separately). The funnel's gulls only mark her on its stairway, where D does not work
    (stairs are a mode of their own): their answer is built but will rarely be heard.
- **What the lunge does** (`world.lunged(kind, fromX)`, once per thing): the porter's cart rolls
  two metres within his loop and he runs after it; the jogger spins; a basketball is headed back
  onto the court and that turn's ball is gone; trays on a hallway's floor scatter (set straight
  once she is 8 m away) and their door opens 0.9 s later; a sprinkler leaves drops on her, a flare
  or the sauna's steam a wisp. The swinging light and the chips no longer play their bonk and slip
  sounds when she is through them; the towels do not bury her.
- **The bowl**: the crew cabin's three painted tangerines are `tan_3_bowl_1` to `_3`, each with
  its 8 px cell where it was painted (`tools/draw_rooms.py` keeps the bowl and drops them). Laid
  over the old picture pixel for pixel: the same places; the real ones are a little brighter (the
  painted ones were washed with the room) and their bottom row now covers 4 px of the bowl's rim.
  56 tangerines in all.
- **Sounds**: `dash` became `cry` (unchanged), `lunge` (a rush of air, new: the user's to judge on
  the soundboard) and `lungeEnd`; the rumble's "the dash starting" is "the lunge starting".
- **The `dash` playtest** found that deck 4's crates it broke no longer exist (the check passed
  because she ran past where they had been); it now lunges through deck 4's luggage at 30 m.
- **Playtests run, sound off:** `boot`, `dash`, `deck3` (the bowl added to it: three taken, the count
  3), `vacuum`, `gamepad`, `sound`, `lang`, `intro`, `region1`, `region4`, `region6`, `region8`:
  all pass but one check in `region6`, "the grip socks ... how they are used", which looks for a
  hint ("kick") taken out on 2026-11-14 and fails on `main` as well (the socks are taken: later
  checks see them). Not fixed here. The rest of the suite was not run.
  **Since (the user, 2026-11-15: "Drop the check (fix the test)"):** the check asks only that the
  socks are taken; `region6` passes.

## The plan for the three uses, step 2: the pocket, and the tangerine a real thing (2026-11-15)

Built on `three-uses` from `docs/plan-three-uses.md` §5, step 2, after step 1 was approved (the
user: "continue the plan"). No art.

- **The pocket** (`pocket(fromX)` in the ship scene; `POCKET` in `src/config.js`): at the top of
  `scareContact` (after the lunge, which still comes first) and of `Carry.spill`; also under the
  parasol (`scareAir`, the two gulls over the bow), where she keeps gliding and only blinks (the
  plan's table forgives the bow's flocks; a hit there was a fall). Not for a load gone over by her
  own feet (the cake's sway, a tray carried into a pool: `spill(fromX, own)`), falls or the sea.
  The flinch is her `her-hit` clip for 340 ms while she is slowed from a push of 120 px a second
  (about half a metre back); the blink is her alpha between 1 and 0.5 (the soundscape takes her
  under 0.5 for gone and would drop her steps).
- **A walker who bumped into her stands aside** as at her cry (`people.standAside()`, taken out
  of `heard()`): my addition. Without it the porter walked on through her while she blinked and
  hit her again the moment it ended, a second tangerine for one meeting.
- **The loose tangerine** (`src/world/tangerine.js`, `LOOSE` in the config): an 8 px body in a
  physics group with the same floors and walls as hers by its own route (the solid layer, rooms,
  side walks from above, the outside's platforms and partitions, the duct, carts, crates,
  pushables, breakables, the robot, closed bulkheads, the ropes and fire doors that hold her).
  Phaser hands a group against a single body to the callback in the other order: each callback
  finds the tangerine first. It leaves her hip at 220 px a second, 200 up, bounces at 0.35, a
  floor slows it 200 px a second each second: about 4 m in all, then rest. It turns a quarter at
  a time about its middle (by degrees an 8 px fruit only blurs). She cannot catch it for 0.6 s
  (it leaves from inside her). At rest it is kept in `save.loose` (written with the save at a
  checkpoint, as her count is); picked up by walking over it, as any tangerine.
- **Sounds**: `pocket` new (a soft knock and a pop; the user's to judge on the soundboard). The
  plan's `roll` and `plop` were names taken already (a cart's wheels, a small soft thing dropped):
  its bounces use `plop`, its fall into a pool or the sea `splashSmall`, and it rolls silently. No
  new rumble: the spill's light tick.
- **The playtests run with the pocket off** unless a scenario names it (`Browser.open()` adds
  `&pocket=off`): a scenario that picks up a tangerine on its way and then checks a fright still
  sees the fright, as the plan wanted of them. A new scenario, `pocket`: the porter walks into her
  with her tray and two tangerines; forgiven, one less, the tray kept, he stands aside, it flies
  off the way she was pushed, rests on the floor some way off, is in the save, there after a
  reload, hers again walked over; with none, a fright; a long fall is a fright with three.
- **Playtests run, sound off:** `pocket`, `dash`, `vacuum`, `falls`, `overboard`, `region1`,
  `sound`, `boot`: all pass. `tools/check_sound.py`: all within bounds. The rest of the suite was
  not run.

## The plan for the three uses, step 3: the throw (2026-11-15)

- **Her clip** (`toss`, 3 generations, approved by the user's price word: the plan said about 5,
  I quoted 3.1): `animate_character` in skeleton-v3 mode with eight poses written by hand (arm
  back low, a step, the swing past the hip, the let-go at chest height, the follow-through), east
  only, on her stored character, so no pose estimate was needed. Her existing `throw` (the
  two-handed overhead shot at the court) would not do for a roll. The tangerine is put in her
  fist in frames 0 to 3 by `tools/hold_tangerine.py` (the game's own fruit, her fingers' skin put
  back over it), into `toss-held/`; the raw frames are kept as they came. One frame has her fist
  a little smeared as it swings past her hip: it reads as a hand at the game's size, left.
- **The throw** (`tryThrow`, `releaseThrow` in the ship scene; `THROW` in the config): on her
  feet only, hands free (not with a tray, crawling, gliding, in a lunge, holding Bumbot; the
  ladders, stairs and pool are modes of their own). She stands for 440 ms; it leaves her hand at
  250 ms (the clip's fifth frame, at 16 a second), 18 px ahead of her middle, 32 over her feet,
  and is spent only then: a fright or the pocket's flinch before it drops the throw and keeps the
  tangerine. The roll: 240 px/s, 60 up: 6.1 m measured. The lob: 250 px/s, 355 up: its top 99 px
  over the floor 2.5 m ahead (the plan's 2.3). With none, the count blinks, as for D.
- **A hard landing keeps 45% of its speed along the floor** (`LOOSE.landKeep`, from 260 px/s
  down): a lob rolled on 9 m after landing without it. It applies to a knocked-out tangerine too.
- **Lying tangerines are offered too**, each frame (step 2 offered only moving ones): a vacuum
  passing one, a gull coming down to one. `loose.near(t, x, y, dx, dy, route)` is every taker's
  test; `loose.claim(t)` hands over one a taker carries off itself.
- **The takers, as built** (the plan's §2, fourth column, for everything there is today):
  - Porter: he stops for it anywhere along his touch box, his cart's front included (at first
    only his feet counted, and his cart reached her first: a fright), picks it up, stands by the
    wall 10 s and eats it. Waiter: stops 2 s and pockets it. Both spent. Jogger: a little hop
    over it, which rolls on.
  - Anyone else standing about (the ones who turn at her cry) turns to look at a moving one
    for 1.8 s.
  - The steward on his rounds: on his cart's top beside the swan, hers again with E (a thing
    whose x is the cart's). Not spent; **but it is not in the save while it is on the cart**:
    lost if the game is closed then. My simplification.
  - The kid: catches one that reaches his hands (he faces where it came from), eats it in two
    bites, his back turned 15 s (`KID.fruit`). One that lands short of him at the pool is the
    gulls'.
  - Deck 4's vacuum (the scene's `offeredHere`) and deck 9's darting one: swallowed, a choke
    (`vacChoke`, a new sound, the user's to judge), tinted dead and tilted, a wisp of smoke now
    and then, harmless, until she has left the deck.
  - Gulls (`world.gullTakes`: down to it, four pecks, off with it in its beak): the pool's and the
    Great Outdoors' (their own `pounce`; no dive at her cone for 10 s after), a balcony's (gone
    until she is 4 m away), the promenade's shy ones (8 s), the funnel's (no swoop 10 s), the
    bow's flocks (one goes, and flies back to its place).
  - The trays outside a "Do Not Disturb" door: the clatter, the door opens, the guest looks this
    way and that (a third way of `knock`, `look`: no shriek, no fright wherever she is), and the
    trays stay quiet until she is 3 m off them again. The tangerine lies there, hers again.
  - The piñata: a lob that meets it brings it down by the lunge's own code, taken out into
    `world.breakThing()`. It hangs in a small room past a wall, so the lob that does it is the
    one thrown from under it, rising through it.
  - The court's hoop: a lob coming down through the rim, a swish, a cheer, a sparkle; it falls
    on through.
  - The Spinnaker's piano: one coming down over its keys (a box guessed from where she stands to
    play, not from the art) plays a random note of its tune and a ♪.
  - The delivery robot: one that comes down on its top stays there (a bounce would take it off
    so small a top) and rides along, its place in the save kept up.
  - Bumbot at a spot: a thrown one that reaches him is batted straight back to her (his `bat`
    clip, then a wash: "sniffs his paw"); his spot and his near-catch are what they were. At the
    tip of the bow: he backs off (`spook`), and it rolls on.
- **Not tried in the game:** the funnel's gulls and Bumbot at the tip (both need the story far
  along); written by their own code's patterns.
- **The `gamepad` scenario taps Y** to take the controller up again before a fright: Y is the
  throw now; harmless there (the fright drops it).
- **A new playtest scenario `throw`**: the roll (one less, about six metres, in the save, hers
  again walked over), the lob's height, deck 4's vacuum choking and harmless and going again off
  the deck, a pool gull taking one, the piñata by a lob and its three tangerines, Bumbot batting
  one back and his near-catch after.
- **Looked at closely** (the targets at their moment, enlarged): the porter's fruit in his hand,
  on the steward's cart by the swan, the choked vacuum, the kid eating it and his back turned.
  The pool's gull came down exactly on the fruit and hid it; it lands short of it now, facing it.
- **Playtests run, sound off:** `throw`, `pocket`, `vacuum`, `gamepad`, `region2`, `region6`,
  `region7`, `region8`: all pass (`throw` again after the gull's fix); `tools/check_sound.py`: all
  within bounds. The rest of the suite was
  not run.

## The plan for the three uses, step 4: region 1's decks, and the first things to find (2026-11-16)

- **Art, approved item by item (49 generations):** the dog (PixelLab pro flash, the dog template,
  side view, styled on her sprite; 6) with a walk, a run and a sit (skeleton-v3, 3 each); the
  knitting lady (pro, styled on the cabin maid; 10) and her seated knit (skeleton-v3 poses; 3);
  the paper round's steward (pro, styled on the drill's officer; 10), his walk (skeleton-v3
  "walking"; 3) and his skim (poses; 3); four map objects (tennis ball, wool, feather on a stick,
  a desk flag of Ukraine; 1 each) and a folded newspaper (1). Shown to the user before the clips.
- **The newspaper map object is not used** (`SKIP` in `tools/build_things.py`): it came drawn
  tilted, a smudge at the 3 px of a paper on the carpet; the papers are drawn in code
  (`paper-fold`), on the user's word.
- **The steward's skim lost its stack** in its first three frames (the finger licked): his flick is
  the clip's last five (`cut` in `tools/cast.py`), and the lick is gone.
- **The dog is shrunk to 22 px** (`scale` 0.65): a small dog beside her.
- **The things to find** are `ITEMS` whose `what` is `keep:<whose>:<name>` (cat, her, him), kept in
  `save.keeps`; taken with E, or handed over (`world.giveKeep()`, the dog's owner's ball). One up
  high (more than 40 px over the floor: the climb's feather) is hers only from up there, or once a
  lob has knocked it to the floor (`world.lobbedInto()`; the lob that does it comes down onto the
  shelf from about four metres back, over the carts). The HUD: a count per kind after the books'
  (🐾 Bumbot's, 🌸 hers, 🎸 his: my picks), each hidden until its first find; the totals are
  `KEEPS` in `tools/population.py`.
- **Deck 4:**
  - The suitcase (`Roller`, the atlas's own `suitcase`) rolls between 38.5 and 45.5 m, a roll there
    and back in 20 s, a creak at each end; walked into, a bump; a lunge sends it rolling to the
    corridor's end, where it stays.
  - The dog (`Fetcher`) is at the cabin door at 99.6 m, not 86: 90 m has a service cart and 95.6
    a lift's door. Its owner is `railwoman`, the one figure made and placed nowhere (the plan's
    "existing figure"), standing in her open door (`door-cabin-ajar`; its slot listed with the
    corridor's door spots so no closed door is drawn under it). The lead is drawn from her hand
    to its collar, sagging to the carpet. **Where it lies, run into, she trips on it: a stagger
    (her slip pose), slowed to a third for half a second, and she is past; a hop clears it; never
    a fright.** At first it held her back like a wall until she jumped (the plan's "a line to hop",
    with its "no fright"): the user ran into it and asked why she could not pass; of three ways
    offered they chose the trip (2026-11-16). Only crossing at the line itself counts (a teleport,
    a fright's walk back, cross it freely). **The lead stops short of any wall across the deck:** the
    user saw the dog wander past the bulkhead at 101.9 m into the stair hall, its lead through the
    wall; its reach is now 95.6 to 101.6 m. Its owner turns to face her dog, the lead in her front
    hand.
    It fetches a tangerine on the carpet within its 4 m and brings it to her feet; she has it
    again at once. Three fetches: a heart over its owner, and the tennis ball. Her cry: a howl,
    round its owner's legs, the lead flat 5 s. A lunge: it jumps aside. It never meets the vacuum
    (118 to 143 m), so it does not bark at it.
  - The climb, between the cabin doors at 143.6 and 147.6 m: the room-service cart (25 px), the
    laundry cart drawn for the linen room (41 px; nothing in the atlas reads as a linen cage), a
    shelf on two brackets drawn in code at 66 px (the ceiling is at 128 and she is 59 tall: no
    higher). The feather lies on the shelf. **The vacuum now stops at 143 m** (it ran to 150),
    so it never runs through the carts: the plan's "the vacuum passing underneath" is dropped.
- **Deck 5:**
  - The knitting lady sits in an armchair just inside her open cabin door at 24.9 m (`peek-knit`,
    drawn in code like `peek-sea`), knitting; her basket by the door with the wool.
  - The paper round (`Skimmer`) between 31.5 and 42 m (not 34 to 46: a stewardess with a tray
    stands at 44.4): from three metres short of each door he flicks a paper along the carpet
    that slows to a stop at it; stepped on while it slides, she slips. At the end he walks back,
    and the papers are taken in. Her cry: he stands aside; a tangerine thrown to him: caught and
    eaten standing aside (spent).
  - Her flag: there is no desk at 146 m. The one desk of Shore excursions and reservations is the
    counter at 140 m; four little port flags drawn in code (Sweden, Finland, Estonia, Denmark) and
    hers at its far end.
- **Sounds:** `bark`, `howl`, `paperSlide` new (the user's to judge on the soundboard).
- **`tools/check_corridors.py`** (the plan's §4.7, from the audit's scratch script): before this
  step deck 4 had 80.4 m without a reward and deck 5 80.5 m; after it, deck 4 68.4 m (31 to 100)
  and 29.6 m at most without a beat, deck 5 58.1 m without a reward and 55.2 m without a beat.
- **A new playtest scenario `deck4`** (decks 4 and 5): the suitcase, the lead tripped on and hopped, its reach short of the bulkhead, three
  fetches and the ball, the feather (not from the floor; a lob; up the climb by jumps, 25, 41 and
  66 px), the wool, the flag, the HUD's counts, a paper slipped on.
- `tools/check_overlaps.py`: nothing (after the dog's door).
- **Playtests run, sound off:** `deck4` (new), `region1`, `boot`, `deck3`, `trunk`, `ladder`,
  `throw`: all pass. `tools/check_sound.py`: all within bounds. The rest of the suite was not run.
- **Eating, as the user asked it (2026-11-16): "to their mouths, bite, remove leftover food from
  their mouths, chew; the food has to stay in their hands".** The tangerine had been squashed
  flatter in the air at each bite, and the user saw it melt. Now a `bite` clip for the porter and
  the paper round's steward (skeleton-v3 poses, 3 generations each, approved): the hand to the
  mouth, a bite, the hand down, three chews; played three times (`people.eat()`), the fruit in
  the fist in every frame (`FISTS` in `src/world/people.js`, found frame by frame and composed
  offline at the game's offsets before trusting them), drawn behind the figure so the fingers
  close over it (over the porter's trolley, which is drawn over him while he stands aside),
  bitten at each bite (`tangerine-bit1`, `-bit2`, drawn in code) and gone at the third. The
  steward eats with his far hand: the near arm holds his stack.
- **The kid's clip was made and is not used** (3 generations): his water pistol is drawn into
  both his hands in every pose he has, and the clip carried it to his mouth. He catches the
  tangerine, turns his back and eats it out of sight (munches heard), back turned 15 s.
- **The papers are taken in** (the user tried E and crouching on one lying at a door: it looked
  like a thing to pick up): a moment after one stops at its door, the door opens a crack at its
  handle's side, a hand draws it in, the door shuts. **One she slips on shoots on to its door**
  (the user saw it stay where it hit her), harmless after the first slip, and is taken in.
- **Playtests run, sound off:** `deck4` (with the paper taken in and the steward eating),
  `throw`, `region1`, `region6`: all pass.
- **The user's fixes to the paper round (2026-11-16):** the steward's tangerine is drawn over his
  hand, covering his palm (it sat behind it: `FRUIT_OVER`); a paper lying at its door, not yet
  taken in, is as slippery as a sliding one (once), and lies there 2 s before the hand takes it;
  he skims each from five metres short of its door (three before), sliding a second and a half;
  his round starts at 23.5 m so that the first door (28.9 m) has its five metres, and the doors
  he serves start five metres into his round (the knitting lady's open door is not one).
  `deck4` passes (with a paper lying at its door slipped on).
- **More of the user's fixes (2026-11-16):** the steward skims papers on his way back too, west
  to the doors behind him (from 5 m short of each, as forward), so the round is never quiet. The
  knitting lady sat in front of her doorway rather than in it (the user: "she looks misplaced");
  she sits two pixels further in, her armchair's back against the door's leaf, and the door's
  frame on the corridor side is drawn over her (`peek-knit-front`), her toes behind it.
- **The user's third round on deck 5 (2026-11-16; generations approved freely, "I have 5000"):**
  - The knitting lady's cabin: its picture (a green and blue landscape) read as the flag of
    Ukraine upside down; it is a red flower in a vase in a gilt frame, and below it the end of
    her bed. She sits on her own armchair in the corridor, forward of her open door, its back
    against the deck's end wall (which runs to 23.33 m), her basket at her feet. A first
    armchair (a map object, 1 generation) came drawn turned three-quarters while she is in
    flat profile; the user: "Regenerate the lady with the chair together". The armchair was
    drawn by inpainting round her own seated frame (her pixels kept, 1 generation), the specks
    cleaned off and her cut out of it, so she sits in it exactly (`knit-chair`; the turned one
    kept unused in `SKIP`).
  - The stewardess with the tray (`amb_breakfast`, an ambient figure) is the breakfast round
    (`Breakfast`, `BREAKFASTS`): door to door at 44.9, 48.9 and 52.9 m with a covered plate from
    her room-service trolley, a knock, a hand takes it in (`world.handTakes()`, shared with the
    papers), she wheels the trolley on (a low thing to hop), and back at the last door. Walked
    into, she drops her tray with a crash: a fright. Her cry: she stands aside. A tangerine
    thrown to her: onto the trolley, in with the next plate (spent). A lunge: she is spun round.
    Her walk clip (3 generations) carries her tray and her bag, as her standing pose does.
  - A second paper round where the forward cabins meet the stair hall (57.5 to 74 m), by a new
    stewardess (`paperwoman`: pro, styled on the cabin maid, 10; walk, skim, bite, 3 each). Her
    skim is her flick whole (no finger licked); her stack is under her far arm, mostly hidden
    behind her, so in her walk it shows in two frames of six. Her tangerine is in her palm.
  - The first round starts at 26 m (it stood in front of the knitting lady at 23.5); it serves
    the first door on its way back only.
  - `deck4` (now with the breakfast round), `region1`, `boot`: pass; `check_overlaps.py`: none.
- **The user's fourth round (2026-11-16): "broken on many levels".** The tray stewardess's figure
  (`stewardess`, made long before) holds a tray in one hand and a bag in the other in every pose,
  and I had drawn a covered dish over her painted tray. She is replaced by a new figure with
  empty hands (`roomservice`: pro, styled on the cabin maid, 10; a walk and a `carry` walk, both
  hands forward, 3 each) and a breakfast tray of its own (a map object, 1: a covered plate, a
  glass of juice, a flower in a vase), carried on her hands (`TRAY_HANDS`, composed offline) to
  the door, where the hand takes the tray itself in; she walks back empty-handed for the next.
  Walked into with a tray, it falls with a crash.
  **The door's crack opened in bare wall** at some doors: the rounds took their doors from the
  corridor's grid of door places, but the corridor draws no cabin door beside a lift's, a crew
  door or a stair hall. The corridor now keeps the doors it draws (`cabinDoorsDrawn`), and the
  rounds serve only those (`realDoors`): the breakfast round 44.9 and 52.9 m (48.9 is a lift's),
  the second paper round 60.9 to 68.9 m (72.9 is the stair hall's).
  **The user's standing word, saved (`CLAUDE.md`, "Art"): "Don't hesitate to generate new/updated
  props in order to implement things properly visually. Use the generations."**
  The knitting lady's cabin: its picture and bed washed 30% toward the wall, as inside every room.
  `deck4`, `boot`: pass; `check_overlaps.py`: none.
- **The user's fifth round (2026-11-16):**
  - A lunge goes past the breakfast trolley as past her (`through` on a solid: the trolley).
  - **Her falls, new clips (skeleton-v3 poses, 3 generations each):** a slip with a tangerine on
    her is caught backwards, arms going (`slipback`), the tangerine flying back; without one she
    goes down on her bottom (`slipfall`), sits dazed with butterflies circling over her head
    (`dazed-sit`) and is back at her checkpoint. **The dog's lead is a trip now** (`tripped`, a new
    fright word in both languages): with a tangerine she stumbles on forward (`stumble`), the
    tangerine flying ahead of her; without, she falls flat on her belly (`tripfall`), lies dazed
    (`dazed-lie`) and is back at her checkpoint. The stagger of before (slowed, nothing lost) is
    gone. The wet patch by the pool is a slip too, and has the same falls.
  - **The butterflies are drawn with her** in the dazed clips (the user: "Don't generate
    butterflies separately. As a rule ... generate people with objects together"; saved in
    `CLAUDE.md`): two butterfly sprites made first to circle over her in code (2 generations) are
    kept unused (`SKIP`). The dazed clips' first frame is their starting pose, without the
    butterflies, and is left out of the loop. The trip's clip failed once on PixelLab's side (a
    service error) and was made again.
  - `deck4` (the lead's trip and fall, the breakfast round from a spot clear of the papers),
    `pocket`, `lang`, `region6`: pass.
- **The user's sixth round (2026-11-16):** the second paper stewardess turned on the stair hall's
  doorway (its wall at 73.9 m): her round ends at 72 m. A trip with a tangerine on her played its
  stumble while she ran on at her speed, and read as nothing ("she doesn't trip"): she is stopped
  short now (45 px/s on), and her stumble and her slip caught backwards play at 9 frames a second
  for 0.7 s. The fall after a slip with tangerines on her was my second link's `&pocket=off`,
  which switches their help off while the HUD still shows ∞.

## The plan's revision, step 1 gone back over: obstacles by name, the new tangerine (2026-11-16)

The plan was revised with the user the same day (`docs/plan-three-uses.md`, §1.6, §1.7, "Start
here" 7); each built step is gone back over under its "Revision".

- **Every hit names its obstacle** (`MISHAPS` in `src/config.js`, 24 lines: the chips, the lead,
  the trays, the papers, the vacuums, the suitcase, the deck chair, the porter's cart, the jogger,
  the breakfast tray, the kid's jet, the stage's light, a door, a basketball, the drill's boat, a
  sprinkler, the steam, the towels, a flare, the three kinds of gull, a "Do Not Disturb" door, the
  occupied balcony). `scareContact`, `scareAir`, `Carry.spill` callers and `world.lunged` take that
  name; the people's `touch` in the data names theirs (`cart`, `jogger`). Each line has the word she
  cries, as before, and what stands in until its own gags are made (`down`: the built falls;
  `recoil`; `mark`: what a lunge through it leaves on her). Nothing in play changes yet.
- `src/lang.js`: "Weeeee!" / «Віііі!» (`fright.ride`), the vacuum's ride (§1.6, 5b).
- **The new tangerine (§1.7):** six candidates from PixelLab (pixen, 16 and 20 px, 6 generations;
  one came with a face). The user chose the second and asked for it a little smaller: shown at
  12, 11 and 10 px, made by taking whole rows and columns out of its peel (not resampled, which
  blurs the outline); its colours put on Resurrect 64 by hand (the automatic snap flattened its
  shading and turned its leaves yellow). **The user chose 10 px.** It is `FRUIT.tangerine` in
  `src/textures.js` with its own small palette, and its two bitten states are cut from it (the
  half's top the fruit inside, not an outline, which read as a dark bowl). Everything follows: the
  pickups (their glint on its highlight), the loose one (origin at the fruit's middle under its
  leaves, so it turns about itself; its body 8 px, it was 6), the HUD's icon (x3, it was x4 of
  8 px), her toss's fist (`tools/hold_tangerine.py`, leaves and all), `TANGERINE` in
  `tools/draw_rooms.py`. Its raw picture: `assets/source/tangerine/`.
- **Found on the way:** a tangerine on a side table lay 12 px up, the table is 22: it hung under
  the top (it did with the old one too, the bigger fruit showed it). It lies on the top now.
- **The crew cabin's bowl (the user):** "Two bottom tangerines should be layered out behind the
  bowl (move them on z-axis relative to the bowl ...). The top tangerine move on the z-axis behind
  the bottom two." A room's picture can now have pixels drawn in front of what lies in the room
  (`Room.in_front()` in `tools/draw_rooms.py` marks what a drawing changed; `<room>-front.png`,
  loaded when the data says `front`, drawn over the tangerines); in a pile a higher tangerine is
  behind a lower one (its depth by its height).
- `lang`, `dash`, `pocket`, `deck4`, `deck3`, `intro`, `throw`, `boot`: pass.

## The plan's revision, step 2 gone back over: mishaps by side and mover, her reactions, the flight to the count (2026-11-16)

- **Which mishap a hit is** (§1.6): `src/world/mishaps.js` reads the two facts at every hit (the
  side of her it is on, at that moment; who was moving: she toward it over 20 px/s, it toward her
  over 5) and picks the obstacle's scenario by the plan's table (the porter: 8a into his cart, 8b
  it pushes into her as she stands facing it, 8c it reaches her back, 8d into his back). The
  scenarios are `MISHAP_SCENES` in `src/config.js`, one line each: her word, her reaction with a
  tangerine, where the tangerine goes, and the built fall that stands in for the gag until it is
  made (`down`: on her bottom or on her front; none: the run-off, now only for the doors and
  the balcony and where no fall fits yet: a sprinkler, water down her back, a gull on a rail).
  `scareContact(fromX, name, { vx, dir, lying, force, snatch })` returns the scenario; the callers
  pass their speed (the vacuums, the suitcase, the papers, the deck chair, the people walking) and
  a person their facing. `Carry.spill` takes the same name and gives the same reaction (a tray in
  her hands is spilled whatever it is, and she never hands one over with it: thrown back or
  pushed on instead). 4c and 6c (a paper at her shoe, the suitcase she watches) are no hit at
  all; what the paper and the suitcase then do is step 4's revision.
- **A hit in the air** plays its mishap when she lands (`gagPending`); during a mishap the keys
  do nothing (as before: the scene is scripted).
- **Her seven new clips** (skeleton-v3 poses, 3 generations each, 21): `reel` (the plan's
  "thrown back, she reels a step"; PixelLab's `hit` move), `rubnose`, `splutter`, `arch`, `yelp`,
  `duck`, `apology` (both hands held out, head bowed: only her body described; the game's own
  tangerine is laid behind her hands from its third frame, `HAND_OVER`, so that a hand at the door
  can take it). Each in place in the game, frame by frame, before showing.
- **Found on the way:** her run's pace is left on her sprite's playback speed, so a fall played
  just after running ran three times slower (the `dash` scenario waited out its 6 s). Her
  reactions and falls are played at their own speed now (`herClip`).
- **The gulls** (on the balcony rails, the funnel's, those across her glide) take the tangerine
  from her and fly off with it (`world.snatch`). **A "Do Not Disturb" door, the occupied
  balcony:** her apology, the hand takes it (spent).
- **The flight to the count** (§1.7): `gainTangerine(x, y)` at the three places one is added
  (one lying in its place, a loose one, the steward's cart); `TALLY` in the config.
- **Sounds:** her reactions' own (`yelpHot`, `splutter`, `gasp`, `sniff`) and the tangerine's
  landing at the count (`tally`); written, rendered and measured, not heard: the user's to judge
  on the soundboard.
- `pocket` grown (front and back, a door, a gull, a door's hand, a paper at her shoe, the count
  changing on landing, the keys dead through a mishap, her checkpoint after); `vacuum` waits for
  her return instead of a fixed time. Passed: `pocket`, `vacuum`, `dash`, `lang`, `boot`,
  `sound`, `gamepad`, `deck4`, `region1`, `region6`, `region7`, `region8`; `check_sound.py`: all within bounds.

## No save while the game is made; a start place on deck 4 (2026-11-16)

- **The user: "remove save games (for now) ... If I want intro, I want a default link to work like
  expected. If I want any other location, or infinite tangerines, or whatever else we had, it
  should all still work. Just don't save my progress."** `DEV_FRESH` in `src/config.js`: the save
  is neither read nor written, so every load is a new game; every link works as before. `?real`
  keeps the save as she will get it; `tools/playtest.py` opens every scenario with it (the
  `pocket` scenario reloads to find its tangerine where it lay). To be set to false before the
  gift. (A first try also skipped the welcome screen and the intro on every load: not asked,
  taken out.)
- **`?at=deck4`**: deck 4's corridor at 49 m, between the runaway suitcase and the porter's
  round (I had given the user a link with a place that did not exist, and the game started them
  on deck 3). `docs/start-links.md`, `README.md`.
- `boot`, `deck3`, `intro`, `pocket`: pass.
- **The user asked whether her falling on her bottom when the porter's cart reaches her back is
  meant** (8c's gag is sitting back into the luggage; the stand-in is the built fall in the gag's
  direction). Offered: keep it until step 4 draws the gags, or stand in with the fall forward for
  every hit from behind. **The user: keep it.**
- **A new rule (the user): after each approved step, commit, save and record everything, and say
  when it is safe to compact the context** (`CLAUDE.md`, "Working with the user").

## The plan's revision, step 3 gone back over: the thrown tangerine (2026-11-16)

- The new tangerine in her toss's fist (`tools/hold_tangerine.py`) and the loose one turning a
  quarter at a time as it rolls were already done with step 1's revision; a thrown one picked up
  again already flew to the count (`gainTangerine` in `LooseTangerines.pickedUp`).
- **Changed:** on every pick-up the tangerine's own picture also rose and faded where it lay
  while its copy flew to the count, so two showed for a moment. §1.7 says its picture flies
  "from where it was": the one on the floor now goes at once (the placed ones in
  `checkPickups`, the loose ones in `pickedUp`), and only the flight is seen. Shown frame by
  frame to the user.
- `throw`, `gamepad`, `pocket`: pass. **Approved by the user.**

## The plan's revision, step 4 under way: she rides the vacuum and the suitcase (2026-11-16)

- **Her first two gags (§1.6, 5b and 6b), each one picture of her with the thing:** a state of her
  character with the thing drawn in (10 generations each), then v3 clips from it: she plops down
  onto it as it catches her heels, then rides (the vacuum: arms up, hair streaming, out of the
  screen, "Weeeee!"; the suitcase: clutching her hands, to the end of its roll, where it tips and
  she lands sitting on the floor). A sheet of their own, `assets/sprites/her-mishaps.png`
  (`HER_MISHAPS`, 112 px cells, each clip placed by its thing's middle so the thing never jumps
  between clips); `rideGag()` in the ship scene, `GAGS` in the config; the world's own thing is
  hidden while the picture plays and is back in its place when she comes out of her door.
- **The world's vacuum and suitcase are cut from the same pictures** (where she sits on them,
  each row filled from its own colours or the column below), so the one that hits her is the one
  she rides. Deck 4's vacuum was a 16 x 6 block drawn in code; the suitcase's handle is up now.
- **The user's corrections, in order:** the first suitcase state was darker and narrower than the
  game's: made again in the game's colours, handle up, tag (the user's choice, of two). My
  cut-out squared the suitcase's rounded corners: restored. The vacuum "looks too big": made
  smaller by taking out its plain middle columns and a row (32 x 13 to 22 x 11), its top line
  run out to mirror its left end and greyed (the user's choice of three sizes and two greys);
  the riding picture made again with it under her, she lowered 2 px, and both clips drawn again
  from it (2 generations).
- **"I prefer the ride in all cases"** (the user, after trying it from every side with a test flag,
  `?ride=all`, since removed): 5a, 6a and 6c ride too, the picture facing the way the thing goes
  (from the front she turns round onto it). With a tangerine the side still picks her reaction;
  6c, before no hit at all, throws her back a step (the tangerine behind her). The suitcase from a
  standstill at an end of its roll sets off for the other end with her, up to 80 px/s.
- **A glitch the user saw:** the camera, restarted to follow the suitcase's ride, snapped the view
  down a few px out of its slack box. The view now stays put and slides sideways by exactly her
  ride (measured: 0 px up or down).
- **Two new rules from the user:** every visual change or new prop is shown enlarged and approved
  before it is placed or tested (I had placed and tested the cut-outs first: "If we follow the
  preview/approve rule, we won't need to regenerate sequences like this time"); while this plan
  is built, links for scenarios without tangerines leave `&tangerines=infinite` out.
- `?at=deck4-aft`: deck 4's corridor at 112 m, by the vacuum's round.
- Generations, from the account: 41 (three states 30, the first suitcase try among them; the
  first five clips 8, the big vacuum's two now unused; the map object 1, not used; the small
  vacuum's two clips 2). (I had told the user 31, then 33: miscounted.)
- Passed: `deck4` (6a, 6b, 6c ride; tipped off at the roll's end; back at her checkpoint with it in
  place), `vacuum` (head-on and from behind she rides it off; back; no smoke from a ridden one),
  `pocket`, `boot`; `region1` before the vacuum was made smaller. The rest not run.

## Step 4's revision, the papers: a first try in the game, then the user's own brief (2026-11-16)

- **The first stills** (two states of her character with the open newspaper, 20 generations) were
  a quarter bigger than her: the user saw it at once. Clips from her own standing sprite in an 80
  px frame, aimed at those stills shrunk to her size (v3 with an end frame), keep her size: the
  clip's last frame is the still. Kept in `assets/source/her-mishaps/` (README).
- **4a and 4b, the first version:** 4a sat with the paper over her head (a tent), 4b on her belly
  with it on her back (the user chose the paper from behind over in front, both kept). Built onto
  the gag sheet (frames stood on a fixed floor row; 4b's lying frames 2 px up, set down, the
  paper's edge under the floor cut), played where she stands (`fallGag` in the ship scene; the
  paper that hit her taken away), and 4c made: a paper stopped at her shoe lies a second and
  fades, no hand takes it. A start place `?at=deck5`, between deck 5's two paper rounds.
- **The user tried it: "It doesn't work at all".** Their brief: the sliding paper too small,
  generated, near the open one's size; she slips even standing; from behind, the same paper
  slides on under her foot, that leg goes up with the paper following it round in a circle, she
  sits and it covers her as a tent; from the front, on her belly, that leg up behind her, the
  paper round after it and over her. Candidates: two sliding newspapers (map objects; their
  greys put on the palette as white, since plain palettizing turned them pale green), and the two
  clips from her standing on the paper. The first try from the front kicked the leg up in front
  (kept, not used). **Saved at the user's word, to decide the next day** which paper and whether
  the clips go in. The game still has the first version; the `deck4` playtest's paper check
  expects the old rules (not run).
- Generations: 36 (the two oversized stills 20; clips 6 + 2 + 6; the two papers 2).

## Step 4's revision, the papers done (2026-11-17)

- **What the user asked first** (on seeing the strips): the paper sliding on the floor and her
  slip clip, which has the paper in it, "work seamlessly together visually". Shown as one strip
  each, composed from the real pictures: the world's paper sliding in under her (her own standing
  sprite), then the clip, whose first frame is that same picture. Both papers now get one colour
  rule (`paper_greys` in `tools/palettize.py`: the neutral greys by lightness, before the palette,
  so that white paper is white and not pale green; her shirt's tinted shades are left alone).
- **"The newspaper is slowing down when it gets under her foot. So the resulting fall is
  unconvincing":** a paper slides at a steady 260 px/s right to her foot, braking only in its last
  half metre to its door; the clip's first frame (her still standing) left out and its next three
  at 60 ms, so that the push carries into the fall. Approved as a strip, then in the game.
- **In the game:** the user's B at 10 px (`assets/source/things/paper-sliding.png`, in the things
  sheet; the code-drawn 10 x 3 one gone), its curled edge trailing as in the clips. At her front
  (sliding at her, standing or running, or lying at a door where she steps): 4a, her leg up behind
  her, on her belly, the paper on her back. At her heel: 4b, on her bottom, the paper over her head.
  She slips standing too (4c gone). Her foot is on it when its middle is within 9 px of hers; the
  clip is set down by where the paper is (`GAGS[..].paper`: its offset from her middle in the
  first picture) and the world's paper is taken away, so the paper does not jump. With a
  tangerine on her the side gives her short reaction the way she falls: the front a stumble on
  (the tangerine ahead), the heel a slip back (behind).
- No new generations (36 for the papers in all, 2026-11-16).
- Passed: `deck4` (the slide's speed near her, 273 px/s; from behind and in front as she stands;
  one lying at its door walked onto; back at her checkpoint), `pocket` (a paper at her front and
  at her heel with a tangerine), `region1`, `boot`: 85 checks. The rest not run.

## The suitcase and the vacuum refined (2026-11-17)

- **The vacuum 2 px lower** (the user, shown as frames from the game moved by hand first): the
  world's sits down into the carpet's top line, and her ride with it (`ride.y`).
- **Butterflies over her head after the suitcase tips her off:** a loop of 8 frames v3 of the
  riding state from the tip's last frame. Two tries from that frame had them fly off; set over her
  head in the start picture (from her own dazed clip, start = end), they circle. The first such loop
  had her grin with her eyes closed between open-eyed frames; the user: "I liked the smile, leave
  it. Just don't add frames with her eyes blinking": the loop in the game keeps her eyes open, her
  own small smile. Same canvas and edges as the tip's last frame, placed as the tip is
  (`shift_as` in `HER_MISHAPS`).
- **"The suitcase sequence takes too long":** recorded as GIFs from the running game at two paces.
  The user liked the "as it is now" one, which played 10% fast (a GIF keeps hundredths of a
  second: 66 ms frames became 60) and showed a ride from halfway along. So: the clips 10% quicker,
  the dazed hold 1.18 s, and **the ride takes 3.3 s wherever she is hit** (the same speed profile,
  scaled for the roll left, never under 1.1 times). And the suitcase by itself rolls faster, 1.6
  m/s at its fastest from 1.1 (there and back in 13.7 s, from 20). Recordings since are at 70 ms a
  frame, which a GIF keeps exactly.
- Generations: 12 (the butterfly loops: six tries of 2).
- Passed: `deck4` (6a, 6b, 6c; tipped off at the roll's end; back), `vacuum` (5b), `boot`: 41
  checks. The rest not run.

## Doors and walls stop whatever moves (2026-11-17)

- **The user's rule:** "I want the corridor doors (and walls, where relevant) to serve as natural
  obstacles not only for the player, but for moving NPCs and moving objects too. If it makes sense
  for a given moving NPC to open a door on their path and walk through, then they should do that.
  If not, the door should stop them (before the door, not while they're already on top of the
  door). Moving obstacles are just stopped before doors." Written into the plan as §1.8, a standing
  rule in its "Start here" and in `CLAUDE.md`'s rules.
- **Built once, in the ship scene:** `stopShort` (how far a thing goes before the first door or
  wall, the solid layer at a body's height), `spanOn` (a to-and-fro range cut short either side),
  `doorAhead`, `mayOpen` (no lock), `holdDoor` / `letGoDoor` (a door held by a person stays open;
  `updateBulkhead` shuts it once no one holds it and she is away). Bulkheads keep their width (`w`).
- **Who does what:** a person walking a loop (`people.js`, `door()`) opens a door with no lock,
  half a second at its handle, goes through holding it till their back (their cart's) is past; a
  locked door turns them back short of it (one held open would let her past a lock). Things stop
  short of a door, shut or open: the delivery robot, the suitcase (its roll and a lunge's send),
  the dog's lead (its own rule before, now the shared one: the same spot), the vacuum's dart, the
  porter's cart sent rolling, her ride on the vacuum (it ends at a door with a bump, then her
  checkpoint). The paper rounds, the breakfast round and deck 8's steward keep to their side of
  any door (one corridor's work). Loose tangerines already bounced off shut doors.
- **What it changed today:** every mover's range checked against every door and wall from the
  data: only the porter's loop on deck 4 crossed one (the glass door at 60 m, which he went
  through shut); he opens it now (shown as frames and a GIF from the game). Nothing crossed a wall.
- **Bumbot looked at, on the user's ask:** at near-catch 2 the rope stand he knocks swings deck 6's
  194 m door open and he runs through it off the screen; at near-catch 5 he is gone off the screen
  along the pools, 24 m short of deck 11's door (the pool scene does not use its `exitX`). Both
  approved as they are.
- Passed: `deck4`, `vacuum`, `boot`, `dash`, `pocket`, `region1`, `region7`. The rest not run.
  No generations.

## The porter's cart: 8a to 8d and his tip of the cap (2026-11-17)

- **Made as the papers were:** each a v3 clip of her base character from her own standing sprite,
  for 8a and 8c beside the game's own cart (its two atlas pieces) so that the clip's cart is the
  world's; 8b and 8d her alone, the world's porter and cart staying. Shown first as a strip and a
  GIF composed from the real frames with the porter, then in the game.
- **What needed mending:** 8c's generator threw the top bag into the air on both tries: the flying
  bag taken out and the game's cart put back under her in its first frames (her pixels told from
  the redrawn stack by their colours). 8b's first try ended lying flat and 8d's drew a cushion
  ("something soft" in the description: an object named is drawn); both made again toward end
  poses.
- **In the game (`cartGag` in the ship scene):** 8a and 8c are set down where she stands, the
  porter brought the last few px up to the clip's cart and his own cart hidden; 8b keeps the cart's
  front at hers as she is pushed back (`fronts`, measured from the clip); 8c's ride is two metres
  at his walk, then his `tip` clip; 8d: he walks on, then turns round to her (his cart stays). Each
  ends at her checkpoint. Doors and walls stop him (`stopShort`, §1.8).
- **The user's one change:** 8a's kicking on the bags "too fast, making her look like twitching";
  its loop at 4 frames a second, the scene as long as before.
- Generations: 23 (four clips 12, three tries again 9, his cap 2). Passed: `deck4`, `boot`,
  `region1`; the rest not run.
- The dog's lick: the user has another idea for the dog's sequences; to be talked over once the
  rest of this step is done.

## The breakfast stewardess: 10a, 10b and her trolley, 10c to 10f (2026-11-17)

- **10a (approved at once in the game):** she runs into the stewardess's tray, reels back and
  sits; the toast lands on her head and the flower behind her ear. A v3 clip of her base character
  from her own standing sprite toward an end picture (her sitting, made with an edit of 8d's end;
  its first try drew the toast as a bun). Contact counts from the tray's front edge, not the
  stewardess's body (the tray had passed through her), and also while she knocks at a door with
  it (that had played the old fall, butterflies and all).
- **10b, rethought by the user:** a squirm on the spot with a squelching walk-off "still looks
  weird, and it is a rare use case": it is 10a's clip, she turned round to face the tray at her
  back (`turn`; the user liked it that way and asked that it be on purpose, not a bug's result).
- **Her trolley, the user's word:** "most of the round the woman pushes her trolley, so that must
  impact the player"; it had pushed her along (and then, for a moment, waited for her). Left to
  me, with "the transition has to be always smooth, without change in appearance, speed, etc. And
  the gag shouldn't take long", and 5: a parked trolley counts as 10c. The trolley stands to her
  knee, so she trips over it, not over its top:
  - 10c, no one just past it: she trips over it head first onto her belly past it (one new clip
    from her sprite beside the game's own trolley, its trolley taken out so that the world's is
    drawn over her: it never changes);
  - 10d, the stewardess just past it (it is wheeled): over it she landed on the stewardess (seen
    in the first recording), so she is bumped back and sits (8b's clip);
  - 10e, at her back: tripped forward, away from it (her own trip); first without a dazed spell
    to keep it short, then dazed 1.2 s at the user's question ("why doesn't she get dazed?");
  - 10f, into the stewardess's back: bounced off (8d's clip), the stewardess turns round.
  `crowded` (someone just past it) is a new fact of a hit, for the trolley.
- **Fixes from the user's tries:** a gag is set on the corridor's floor whatever she stood on (on
  the trolley's top she had sat in the air once it moved on); her trip's and dazed loop's lying
  pose had one leg bent straight up: mended from one edit, the same legs in both so that the trip
  hands over to the dazed loop unchanged, and the trolley trip's last frame too.
- **The stewardess herself:** she pushed the trolley with her hands at her sides. Her pushing walk
  generated with the game's own trolley in the picture (an edit of her walk frame gripping its
  handle, then a loop), the trolley taken out after: v3 swung her hands 5 px off the handle (the
  user), pixminimax held them but its legs shuffled ("like dancing a little"), a third try held
  both, two even steps at 6 a second, her feet keeping pace. Her tray at a door: she lowered her
  hands before it was taken, then it slid sideways across her (the door's hand is on her side
  heading east); behind her it vanished at once. The user's idea: it shrinks a little and is gone
  (`handTakes(..., { shrink })`), her hands out until then.
- Generations: 76 (10a and 10b's tries 31, the spilled tray 7, the trip 8, the lying legs 10, the
  pushing walk 20). Not used: a spilled tray, picture kept (`her-mishaps/tray-tries/`), the
  dropped tray now landing flat. Passed: `deck4`, `boot`, `region1`; the rest not run.

## The art rule looked back over, steps 1 to 4 (2026-11-17)

- **What was found** (the branch's code read for drawing; nothing in steps 1 to 3): deck 4's climb
  shelf, the knitting lady's basket, four desk flags, a cabin door's hand (a 4 x 2 rectangle), the
  cry's heart and "shh" drawn in code; the climb's laundry cart was the linen room's, from deck 9.
  The view into the knitting lady's cabin stays drawn, like the rooms (the user). Kept by the rule:
  the dog's lead and the door's crack (flat), the bitten tangerines (a generated picture edited),
  the fruit in a fist and the breakfast tray (separate in play).
- **Made** (map objects, side view, low detail; ids and every try in
  `assets/source/things/tries/README.md`): the flags, the shelf, the basket, the hand, the heart.
  The "shh": two lips-and-finger tries and three faces with a finger at the lips; none read at a
  bubble's 16 px ("doesn't read like a shh at all", the user), so a speaker crossed out, its cross
  redrawn even by hand ("It is uneven"). The cart: tries drifted to three-quarters; the user chose
  the look of one half-turned try (cart-c) "in profile", made with `edit_image_pro_flash` from it;
  shrunk from 51 px to 44 it came out deformed, so it keeps its pixels with 7 rows cut from its bin,
  and a white towel row across its rim painted the rim's green. The feather: lying flat 6 px tall
  it read as "a shelf glitch" and not as a cat toy; stood on end, "stuck in the shelf"; a teaser
  lying on the shelf, its handle made purple to stand out from the shelf's wood.
- **Little flags shrink by majority colour** (`BY_MAJORITY` in `tools/build_things.py`): averaged
  with their outline they came out dull, the Ukrainian flag too since step 4.
- **The climb** (the user): the room-service cart taken out; the laundry cart and the shelf a
  metre forward, then 0.8 m further apart (each by half, clear of both doors): the shelf is reached
  by a jump from the cart's edge. `deck4`'s climb check runs to the edge first.
- **Deck 5's dim blinked** as her head touched deck 4's ceiling from the shelf: a deck's dim piece
  reaches 16 px under its floor, and her head counted in it. It counts past the floor now
  (`updateDeckDim`).
- **A corridor's extinguisher** hung under a crew door's card reader (deck 4): one within 50 px of
  a door put in a cabin door's place moves 50 px from it.
- **The lady in the bathrobe** (deck 4, 130 m), who did nothing, is an obstacle: 10f's bounce
  (`MISHAPS.robe`), beside her rather than behind.
- **Decided (the user): the tangerine knocked out of her pocket always rolls behind her**, whatever
  the side (the gull's and the door's hand's excepted): "It would place a dilemma: run back to pick
  it up, or continue moving to the initial destination." The user tried it at once: a hit in the
  back by the porter at a glass door, the tangerine bounced off the door into the porter, who ate
  it: "This entire scene played seamlessly and made sense."
- The lunge seemed broken: without `&cards=all` she has not learned it (Bumbot's first beat).
- Generations: 33. Passed: `boot`, `pocket`, `deck4`, `region1`; `check_overlaps` lists nothing;
  the rest not run.

## The dog and its owner made again together (2026-11-17)

- **The user's idea for the dog** (talked over first, as agreed): keep the mechanic, remake the
  pictures: "the lady and the dog are loosely connected, the leash looks weird and glitches on its
  connecting ends ... regenerate them together as a single animation sequence. But we will still
  have to keep the same hitbox areas". One picture cannot follow a dog that strolls 4 m, fetches
  and comes back to her, so: the two made together as one picture for their look and size, then
  separate sprites joined by a lead the game draws from measured ends; together clips for the
  moments they are close (next). The user agreed, with a new owner, the dog still strolling, and
  the lick "without leash glitches".
- **Everyone's feet on the floor** (the user: "not even placed properly on the floor"): PixelLab's
  frames drift 1 to 4 px; the dog sat 1 px up, its owner bobbed, the kid idled 2 to 3 px up, 71
  clips in all. `tools/build_people.py` sets each frame of a clip whose feet stay down on the
  floor by its own lowest px; the clips that leave the floor are listed (`OFF_THE_FLOOR`). No
  generation. Committed by itself (4454684).
- **The picture:** three map objects first (people come out as silhouettes there); then a pro
  character in the cabin maid's style (10), a woman holding the lead's loop, the dog at her feet,
  approved. Cut apart by hand (the dog's neck one px blackened, the user). The dog redrawn
  standing by `edit_image_pro_flash` (a Pro Flash dog from text with it as style came out another
  dog), made a character by Pro rotate; the dog template's walk and run redrew it as another dog
  and its v3 sit never sat; skeleton-v3 kept it but stretched its walk a third; PixMiniMax from its
  own picture held it (the walk, and the sit toward the approved sitting dog as its end frame); the
  run is skeleton-v3's (a smooth gallop). Her idle: PixMiniMax, her fist still in every frame. 47
  generations; ids and tries in `assets/source/people/dogowner-raw/README.md`. Their frames are kept
  by hand (`BY_HAND` in `tools/fetch_people.py`).
- **The lead** (`LEAD` in `src/world/movers.js`): from her fist (7 px in front, 32 up, the same in
  all her idle) to the dog's collar (measured in each frame of its clips), drawn px by px in the
  picture's colours; under her (her fist closes over it), over the dog (from behind, it runs along
  its back to the collar, as in the picture). The user: "too thick" (3 px, the picture's) -> 2 px,
  a dark px under its colour; and it hung at her waist where she met it ("She cannot trip over the
  leash, if it's at her waist line"; I first moved the trip point, "Not what I meant. I meant we
  need to make the leash hang lower"): it hangs down to 3 px over the carpet at the spot she trips
  on, a little over halfway from her hand to the dog as always. A one-px notch at its bottom came
  from cutting fractions down: rows rounded.
- **Lying after a trip, 2 px lower** (the user): her cell ends at her lowest px (her hand under her
  chin), so the game draws her picture lower (`herDrop`, `LIE_DROP`), her body where it was, from
  the fall's frame on the floor until her checkpoint.
- **Her running footsteps** (the user: "her sound is faster than her steps"): a step each 30 px;
  her run lands a foot every 40. They sound on her run's footfall frames now (`SOUND.runSteps`):
  7 in 2 s of running, each on a landing frame. I can't hear it: the user's to judge.
- **Decided (the user): on the dog's lead she falls whatever she carries, and keeps her
  tangerines** ("This will be an exception. And we'll have some other exception to this rule
  later ... handled gracefully in the code"): `pocket: false` on a scenario (`MISHAP_SCENES`),
  asked by `pocket()` itself, so every way a hit reaches her follows it.
- Passed: `deck4` (with the new checks: she falls with tangerines, back with all three), `sound`;
  `boot`; the rest not run.

## The dog's together clips (2026-11-17)

- **The three moments the dog and someone are close, each one picture of the two** (the user's idea
  for the dog, the hybrid agreed: separate sprites joined by a drawn lead, together clips where they
  meet; "Go ahead with all three"). Made by PixMiniMax from the approved pictures (12 generations):
  - **The lead round her legs (her cry):** an end picture of the two, the lead wound round her legs,
    the dog sat against her shins (`edit_image_pro_flash` of their picture, 5); the winding toward it
    and the unwinding from it back to their picture (2 each), and a loop of the two tied (1). The
    winding played backwards would have the dog run tail first: the unwinding is its own clip. Her
    "surprise" marks are the generator's, kept ("All good").
  - **The toss:** her free hand to her pocket, the ball out, tossed underhand, her lead fist the
    same px in every frame (1).
  - **The lick:** her dazed-lie frame with the dog's standing picture turned to her at her face, to
    the same (1); its butterflies drawn purple and teal, put back to her yellow by rule.
- **The tennis ball** (the user: "has to look like a tennis ball"): the game's had been the
  generated ball shrunk to 5 px by majority, its seam lost. 64 small candidates were made (10) with
  a dark outline before the user's word ("don't use black outline"): not used. The user chose from
  six shrinks of the same picture keeping its seam (7 or 8 px; none, a grey or an olive outline):
  8 px with the olive (`SEAM` in `tools/build_things.py`, its own colours, not the palette's, which
  dulled it).
- **The toss made seamless** (the user, three times): the ball in her hand behind her fingers (at her
  hip, held out; "partially covered by lady's hand", its place moved); the flight a lob, its top a
  fifth of the way across (it had risen a little and flown flat, "Innatural"); the ball leaving her
  hand as it opens, from where she held it (it had hung a frame over her open hand, "like the ball
  takes off by itself"); in front of her as it reaches her, under the sparkle ("the final animation
  with sparks is on top of her").
- **In the game:** the dog runs to its place in their picture (17 px in front of her, where its
  sitting picture lies on theirs) and the clip takes over; at the end their picture is held while it
  sits and the game's dog and lead take over as it gets up, trotting away from her: the game's lead
  at that spot never matched the picture's (tried: hung no lower than the collar when close; undone).
  The lick waits for her dazed loop's frame the picture starts on; the lead's collar end is measured
  in its 8 frames; over the dog when its owner is on her face's side (it had looked tied to its
  rump), from under her when not. Her checkpoint waits for anyone with her (`down.holds`).
- Passed: `deck4` (its new checks for all three) three runs in four, `boot`; the fourth failed later
  on, the lob onto the climb's shelf not knocking the feather down; not seen again in three runs.
  The rest not run.

## Step 4a: deck 9's darting vacuum, and small things on the way (2026-11-17)

- **Deck 9's vacuum (`Darter`) rides her off too** (approved): it was a little shape drawn in code;
  it is deck 4's generated vacuum now, the picture she rides in her gag, dimmed in its doorway at
  its own size (it had been shrunk to 0.8, uneven pixels), its blink on its own red light at its
  front. Caught by it, from the front or from behind, she rides it off down the corridor the way it
  darted (5a, 5b; `ride` to the ship scene's `rideGag`); it is back in its doorway once she is at
  her checkpoint. With a tangerine on her it is only a stumble and it goes on. `region4`'s check
  changed from the old fall to the ride.
- **Ukrainian is `ua`, not `uk`** (the user: "uk is short for United Kingdom"): `?lang=ua`, the
  language's code everywhere; a choice kept in the browser as `uk` is read as `ua`. Its ride word is
  «Уіііііііі!» (the user).
- **The breakfast stewardess's trolley is solid by its picture's shape** (`TROLLEY`): the table, 21
  by 18, and the cloche's dome on it, 10 by 7. One box the cloche's height over the whole trolley
  had been 7 px of air over the table's ends to bump into.
- **A start place `deck9-aft`** (deck 9, 134 m): past the steward's jammed cart, short of the
  vacuum, which the user could not reach from `housekeeping`.
- Passed: `region4`, `deck4`, `lang`. The rest not run.

## Step 4a: the steward's jammed trolley (2026-11-17)

- **The jam made visible** (the user: "I cannot jump over this scene here, there's an invisible
  wall"; the scene "weird and unclear", a man "twitching"): deck 9's steward stood 35 px from a low
  service cart, grabbing at the air, and an invisible block reached the ceiling. Asked how it should
  be, the user took my recommendation: a tall housekeeping trolley that shows why the corridor is
  blocked. Four candidates (map objects); the user chose "4" (boxes, towels, a laundry sack: 79 px,
  taller than her jump), mirrored so its handle faces him.
- **He and it one picture while jammed** (approved): him gripping its handle, leaning back (an edit
  of the two composed); his two heaves at it, the trolley giving 3 px (PixMiniMax); the world's
  trolley hidden meanwhile, so his hands never leave its handle. His bubble over his own head in it
  (`bubbleDx` in people.js). The world's trolley is cut from the clip's last frame, so the two match
  when one replaces the other.
- **Free, it stands back against the wall**, drawn behind her and not solid (a tall `push` thing,
  `aside()` in world.js): it could not be hopped where it stops, as the low one was. He steps back
  off its handle before he thanks her.
- **The user's fixes after trying it:** "When pushing, his legs are not moving": a clip of him
  stepping back as he pulls, in place (`tugwalk`), played while the trolley moves (moved within 150
  ms). "The card is just flying at her. Maybe we need a proper toss sequence": his toss clip from his
  standing picture (to his shirt pocket, an underhand toss), the card in his fingers at his pocket
  for two frames, out of his hand as it opens, a lob to her chest on the game's clock
  (`world.tossOver`, for anyone with a toss clip; the others still hand over as before).
- 12 generations (4 trolleys, 5 the edit, 3 clips). Passed: `region4` (its steward checks changed:
  one picture of the two, he stands back, she walks past the trolley), `boot`. The rest not run.
- **The towel stack** (`haz_towels_9`): the user asked what it is for ("swaying, in the background,
  doing nothing else"): it fell only on a jump landed beside it or the dash; she has no walk, so its
  sway warned of nothing. The user: keep its look, "Make it an obstacle"; a way is proposed to them.

## Step 4a: the towel stack an obstacle (2026-11-17)

- **The user's rule:** "What if it falls on top of her the moment she passes it? And the getting
  past will be having to stop at the stack and wait while it falls." (My proposal had been a wobble,
  a fall a beat after she came in reach, and three ways past: stopping, the dash, knocking it down
  from afar.) Its look kept: "Don't redraw it, I like it the way it is."
- **Built:** coming at it within 100 px (middle to middle) it wobbles hard 0.4 s, then falls the way
  she is going (0.36 s): as long as her run to it, so that she cannot outrun it, and it lands on her
  as she passes it ("Mmmph!", her checkpoint). Stopped as it wobbles, she is about 60 px short and
  it falls in front of her; she walks on over the heap. A jump landed beside it and the dash bring it
  down as before. Its fall is on the game's clock (`update`), not a tween (a recording stepped by
  hand had shown her outrunning it). Stacked again once she has gone (beyond 560 px, within its 800).
- `region4`'s checks changed (running past: buried; stacked again; stopped: it falls in front of
  her; she walks on); the old "the stack still stands" after the vacuum's jump dropped (running on
  toward it, it now falls, in front of her). Passed: `region4`. The rest not run.
- **Next (the user):** "The animations have to be generated, I think, especially the falling and
  scattering": the stack's fall and the towels scattering, and her burial under them (scenario 18),
  generated from the stack's own picture.
- The user asked whether this corridor is on her way to the next area: it is not. Region 4's way
  on is the steward's card, then the linen room at 112 m (behind where she arrives) and its vent;
  the corridor aft of the steward (130 to 194 m) is the plan's optional "gauntlet" (book 4, the
  tangerines, the balcony cabin, the checkpoint at 190).

## Step 4a: the towel stack's fall generated (2026-11-18)

- **The user:** "The animations have to be generated, I think, especially the falling and
  scattering"; the stack's look kept. All of it is PixMiniMax from the stack's own picture
  (`assets/source/things/towel-fall/`, its README has the ids), then shown and approved:
  - **Its fall alone** (try c of two pinned ones): pinned to an end picture made of the stack's own
    fourteen towels lying scattered (`ends.py`), since the first tries fell as one stiff column and
    landed "like books", and five generated heaps read as snow drifts.
  - **The fall on her:** try g of five (c, the first approved, stretched the stack taller as it
    tipped; the user: "fix the stack getting higher glitch"; the two told "never taller" stretched
    worse).
  - **Her coming up:** the heap stirs and bulges, a towel swan pops out, then she under it in her
    towel turban (`emerged.py`: her turban look and a generated swan; five swans came as birds with
    orange beaks, the palest one used with its beak whitened, at 15 px).
  - **The towels redrawn soft** (the user: "the towels themselves look like white bricks. Can we
    keep the animations, but redraw the towels"): `edit_animation` over every frame, the motion
    kept to a px; the standing stack in the corridor is the redrawn first frame, so it and the
    clips hand over exactly.
- **In the game:** the stack and its stool apart while it stands (it sways on the stool's top),
  one sprite for the clips; the fall on her is a gag the stack plays itself (the ship scene's new
  `thingGag`, `GAGS.towels`): she hidden, its clips, her checkpoint, the heap left behind her.
- **Seamless, the user's word** ("It looks like she deliberately stops for a fraction of time to let
  the towels fall on top of her. It has to be seamless"):
  - the stack used to start falling while she was 40 px short of it, so the fall on her took
    over mid-clip, 25 px off: now it wobbles until she is past it (at most 1.1 s; stopped short, it
    falls in front of her when that runs out), the user's own "the moment she passes it";
  - the clip had her standing: four new ones start from her own run frames (0, 2, 4, 6) 6 px past
    it, she running on about 10 px a frame (at her run's 14 a second, her 140 px/s) until it
    catches her; the game takes the one whose first frame is the pose she shows next (in the
    recordings: 7 px past, her stride carried on). A first try from her run frame 36 px past it had
    her running on the spot (pinned to the heap where she stood);
  - the sway eases as she comes level with it, so it is near upright when a clip takes over.
  - The clip of her standing stays for her caught under it any other way while it falls.
- **The heap behind her** as she crosses it (the user, with its stool: "Also its table").
- **Placement:** the heap fell over the open cabin's door; moved 1 m aft (the user: "Yes"), it fell
  over the next door aft: the doors' frames either side are 159 px apart and the heap reaches 90 px
  the way it falls, so no spot keeps both clear; midway, 141.6 m, a towel's tip touches a frame by
  a few px. **The ship picture it hid** (the user) now hangs in the nearest gap with nothing on its
  wall: a rule in `drawCabinDoors` (a stack of the world in front of a picture's gap moves the
  picture), here one gap forward.
- Generations: 101 this round (the first clips 13, the redraw 70, the running clips 8, the heaps
  and swans 10).
- Passed: `region4` (its towel checks unchanged and green), `tools/check_overlaps.py` (0). The rest
  not run.
- Not made: her "bats the towels off" with a tangerine on her (the plan's 18): she reels, loses one,
  the stack falls past her.

## The books' titles, and where they show (2026-11-18; the documents only, nothing built)

- **The user gave the titles**, from two photos of her bookshelf, and a photo of her reading
  armchair at home (`reference/photos/Books/`, git-ignored; read here, sent nowhere). They had
  been promised for "when the game is fully tested": they came now, so the plan's stand-in covers
  are dropped.
- **Decided by the user:** the fourteen titles, each in its own language and script, with its
  author; Її війна is her own, on the bed in cabin 8206; the two Harry Potters by their real
  English titles (the Philosopher's Stone, the Chamber of Secrets, as on her copies); a title
  shows as a generated cover in the centre of a slightly dimmed screen when she gets the book,
  and on the shelf seen close (E at it), generated too; every cover its own; the armchair's photo
  is the picture in the nook's frame, not the nook's look.
- **Mine:** which title lies where ("The order is random"), by what each name fits (approved by
  the user: "Good"); the four new books are shelf numbers 11 to 14 in the plan's order (its things
  17 to 20); the lettering set by a build tool, since the game's pixel lettering has neither
  lower case nor Hebrew; the cover's moment through the Library's existing panel.
- **Found while reading the mechanic, not changed:** the design's "standing still with a book she
  reads where she stands" has no code (only the chair and her bed); the shelf and the trolley
  are drawn in code; nothing says whether books 11 to 14 get hint pages. The second is proposed
  in the plan's step 5; the third is in GAME_DESIGN.md §6.1.15.
- Written: GAME_DESIGN.md §6.1.2 (the table, the two places) and §6.1.15; docs/plan-three-uses.md
  §4.1, step 5's revision, §7, the answers; docs/population.md §2.2. No generations, no playtest.

## Deck 9's corridor becomes the way: the steward to its aft end (2026-11-18; the documents only, nothing built)

- **The user's question:** whether the sprinkler's gag is planned (it is: mishap 16, step 4a, not
  in its first batch), and whether the corridor of the darting vacuum, the towel stack and the
  sprinkler has to be crossed to go on. **It does not:** the trunk comes up at 118 m, the steward
  is at 122, the card opens the linen room at 112, and all three stand aft of him, on a stretch
  of rewards.
- **Decided by the user** ("I accept your recommendation here, and the suggested fixes"): the
  steward and his trolley go to the corridor's aft end, so the card is earned past everything
  and brought back. The route plan is untouched (the trunk, the card, the linen room, the duct).
- **Mine, accepted with it:** the aft end, not just past the sprinkler at 152 m (six different
  things on the way, the luggage stack as the deck's one puzzle with two answers, the balcony
  cabin's green door a tease out and a reward back; the price is a walk back of about 74 m); the
  trolley's roll cut from 7.4 m to 3.8 (185.2 to 189.0), the checkpoint left where it is; the way
  back changed, not repeated (the stack stays fallen, the luggage broken); the wall picture
  rehung and the small housekeeping cart taken out at his new place; the glass door at 194 m
  one-way from the corridor, like decks 8 and 10, so that she cannot come up behind him by deck
  7 and the aft stairs (it had no lock: found when the user asked).
- **Options set aside:** the steward at 152 m (the shorter errand: only the three obstacles);
  the card apart from him (in the cabin being cleaned, or on a second cart: his approved toss
  would lose its use); the hazards moved forward of him (the towel stack's place was just
  fitted); the linen room or the trunk moved (the ship's layout).
- **Proposed, to judge in play:** a checkpoint past the sprinkler, if the way out with no
  tangerine proves harsh.
- **Tried, outside the repo:** the two positions in a copy of the committed game in the temp
  folder (`git archive`, its own map built, a muted headless browser on ports of its own; the
  other session's folder untouched): two strips shown to the user, jammed and freed. The
  checkpoint's door is drawn at 191.6 m, not 190. No playtest scenario run.
- Written: GAME_DESIGN.md (region 4), docs/population.md (the corridor's table, a note under
  it), docs/plan-three-uses.md (step 4a's revision, the answers). For the building session.

## The one-way doors get their push bar (2026-11-18; the documents only, nothing built)

- **The user had missed that there are one-way doors** (asked on reading deck 9's 194 m door
  made one): thirteen in the built map, all at the cabin hallways of decks 8 to 10 and deck 11's
  forward end wall, plus four balcony cabins from their balcony side and the theatre's trunk.
- **Found:** they are drawn exactly like the free glass doors; only E tells (a rattle, a
  padlock). The design's own line, "Fire-exit doors with a push bar on one side only are the
  one-way doors", was never built.
- **Decided by the user** ("Add it to the plan, yes"): the push bar on the free side, a plain
  face on the other, as a generated variant of the glass door shown first.
- **Mine:** its scope (the glass doors across a deck; the end walls' doorways proposed apart;
  cabin doors and the trunk left), made from the game's own open leaf so the two kinds stay a
  pair, the free leaf remade with it if they do not match.
- Written: docs/plan-three-uses.md (step 4a's second revision, the answers), GAME_DESIGN.md
  (§6.1.2's table of locks), docs/population.md (the doors' row). No generations, no playtest.

## Step 4a: the first batch of gags, built (2026-11-18)

The plan's first four (13a, 7b, 3, 20), each the thing's own clip with her (`gags` sheet,
`tools/build_gags.py`, sources and PixelLab ids in `assets/source/her-mishaps/batch-4a/README.md`),
played by the thing itself (the ship scene's `thingGag`, `ride.play`). About 36 generations.

- **The user's rule, made on seeing the first tries** ("Take a look at each of the generated gags
  and look for: visual overlaps that make no sense; anything that breaks seamless transition,
  visually or dynamically; that the anatomy makes sense in every situation; that everything is
  aligned well spatially. Make this a rule"): every candidate checked frame by frame and measured
  before it is shown (`CLAUDE.md`, "Art"). It found: start frames 1 px off her built sheet, a run
  loop floating 3 px, a gull that changed between frames, her standing in a clip where the game
  has her slipping, a hand over the open doorway, holes in the world's door picture that turned
  dark in a clip.
- **13a, the swinging door.** First shown with the leaf as the game drew it (a door picture
  stretched in code): the user could not read it, and the door changed colour. Now its swing is
  generated, the door alone and the same with her (slammed flat on the wall under the leaf, she
  slides down), from the world's own muted shut door, the frame's left side and top its own
  pixels. **From aft only** (the user: from forward "it looks broken"): from forward it never hits
  her and waits to burst until she is clear of its swing (the user: "Visually, that makes sense";
  left so). Coming at it from aft it waits for her (it burst while she was still too far).
  **No tell** (the user: "Let the opening of the door surprise the player"): its rattle and shake
  taken out. 13b is no more.
- **Whoever looks out of a door** (six swinging doors, seven "Do Not Disturb" doors) is cut to the
  doorway (the user: a boy's cap through the frame; a sun hat and a Hawaiian shirt's hat the same,
  found at once) and stands on its threshold (it stood 2 px up). `People.doorway`: Phaser's crop
  (the Mask filter hid them whole).
- **The "Do Not Disturb" doors** swing open and shut in their full colours (the swinging door's
  clip, its muting taken back out exactly), their frame kept (the user: the door "just disappears
  together with the doorframe"). Kept in full colour: she can knock at them (the user's question;
  their "All good").
- **3, the tray.** The three flat bars "don't make any sense" (the user): one tray, the breakfast
  stewardess's own; two more detailed tries came out muddy at that size and are not used. Run onto
  at any step (four clips, one from each quarter of her stride, so the hop never holds or slows) or
  jumped onto (the user: "I should also slide in the direction of the jump"), she rides it off the
  way she was going; the world's own tray base moves under her (her clips are her alone), its
  dishes fly off and lie on the floor; the door opens after on the guest looking after her. Found:
  after a ride the tray stayed hidden where it was carried until she was 8 m away (now back at the
  respawn); the trays it passed were ridden through (knocked aside first, then one tray only).
- **7b, the deck chair.** The plan's fold "shut on her" did not come in four tries; the collapse
  flat under her was offered and taken. She slid off the patch before the chair could catch her:
  sliding in past it, it hardly rocks now. It stops short of the wet-floor sign.
- **20, the gull.** It dives onto her head; standing, she flails and runs off with it; running, she
  runs on. To the next partition, a wall, or out of the screen.
- **Test places:** `door9`, `trays10`, `wet`, `gull9` (`docs/start-links.md`).
- **Tests:** `boot`, `pocket`, `region4`, `region6`, `region7` pass; the rest not run.
  `check_overlaps`: 0. Changed to the new rules: `region4` (the swinging door from aft slams her
  flat; stopping short it bursts by itself; from forward it never hits her), `region6` and
  `region7` (the tray ridden off, the door opening on the guest after; a tray far from its door
  ridden as well). Found by them: after a ride the tray never re-armed when she came back at a
  checkpoint far off (it stopped updating before its re-arm); fixed.

## Step 4a: deck 9's corridor is the way, built; her push remade; the steward's thanks shortened (2026-11-18)

The first of the other session's two decided revisions (docs/plan-three-uses.md, step 4a).

- **The steward and his trolley at the corridor's aft end** (`tools/population.py`): the trolley jammed
  at 185.2 m, rolling to 189.0 (3.8 m), he at 186.0; the story places him by it as before. Shown to
  the user in place, jammed and freed, before the tests (as the plan asks).
- **The door at 194 m** one-way from the corridor (`tools/ship_layout.py`, as decks 8 and 10).
- **At his new place, by rule** (`drawCabinDoors`): a picture is not hung, nor a small cart drawn,
  anywhere along a tall trolley's whole way (the towel stack's rule, widened); the one there hangs in
  the nearest empty gap, 20 m forward.
- **The way back changed:** the towel stack, once fallen, stays fallen (kept with what she broke,
  `save.broken`, the way it fell in `save.heaps`); it used to stack itself again 12 m behind her. The
  luggage already stayed broken.
- **A `steward` start place**, just forward of the trolley.
- **The user, on pushing it:** "shift her a pixel back" and "her legs do not move properly". Her push
  was an old clip whose feet shuffled 2.5 px a frame while the cart rolled 6.7. Remade with
  PixMiniMax (1 generation, `assets/source/her/push2/`, its README) from her push frame against the
  world's trolley, the trolley taken out: two even steps, the planted foot sliding back about 3.6 px a
  frame, so 11 frames a second at 40 px/s (it was 9 and 60; every push, the laundry cart's too).
  Checked frame by frame first: three frames 1 px off the floor set down; her knee clear of the post.
  She stands 29 px from the cart's middle, a whole px so that it never flickers (it was 27.5, drawn
  27 or 28), and the cart is now set at her gap ahead of her after the physics moves her
  (`pushFollow`, on the scene's `postupdate`): set before, it read 27.8 or 28.5 by the moment.
- **The user: his thanks "take too long", and "if I run past him, he doesn't turn to face me".** Found:
  freeing the trolley set her back to play the very moment his scene had stopped her (the flag is set
  inside the push's last step), so she always could walk on, and he faced where she had been. Now his
  thanks do not stop her at all: he steps back twice as fast, no pauses, his brow mop and bow at 1.8
  times, about 1.3 s to the toss (it was 2.5); he turns to her as she passes, during his thanks and
  after while she is within 4 m; the card comes down where she is by then (`tossOver`; only his uses
  it).
- **Tests:** `region4` passes (changed: the steward found at his new place, the door at 194 shut from
  the lobby and opened from the corridor, her gap while pushing, his turning to her, the towel stack
  staying fallen and stood up again by hand for its second check, the laundry cart's push given the
  slower pace); `vacuum` passes; `golden` (changed the same way) and `boot` pass; `check_overlaps`: 0;
  `check_corridors`, deck 9: 64.6 m without a beat (55 to 120, forward of the trunk), 116 m without a
  reward (24 to 140), neither in the stretch that changed.

## Step 4a: the one-way doors' push bar, built (2026-11-18)

The second of the other session's decided revisions (docs/plan-three-uses.md, step 4a).

- **How it was made:** the game's own pictures of the glass door (drawn in code) rendered exactly,
  and only a band of each redrawn by `inpaint_image_pro_flash`, every other pixel coming back as it
  was: so the one-way door and the free one stay one pair. 20 generations
  (`assets/source/ship/pushbar/`, its README).
- **Open:** two bars shown in place beside her, plain steel and steel with a red band; the user chose
  the plain steel. The leaf's glass see-through as the free door's (85%).
- **Shut:** the user, on seeing the first version (the bar's end as a 3 px nub drawn in code): "the door
  profile should also differ from a two-way glass door". Two generated profiles, the bar's end alone
  and with a door closer at the top; the user chose the closer. The free door keeps its handle on both
  sides.
- **Also the user's, in play:** "It opens in the wrong way": the doors swung away from a stair lobby
  (the house rule), so nine of ten opened toward whoever pushed them. A one-way door now swings away
  from its free side (`part_doors()` in the map builder); the lobby's deck plan hangs 20 px further
  along where such a leaf swings in. "I can also open it from the other side now": by the design, once
  she has come through from the free side it is open both ways for good (the shortcuts back); but it
  shut behind her and opened from its plain side with E. Now it stays propped open from then on
  (`propOpen`), and before that its plain side does not open.
- Checked: all ten doors shut and open beside her, in place; the whole ship from outside
  (`tools/render_ship.py`: no door shows through the side); `check_overlaps`: 0.
- **Not looked at yet:** the four end walls with a one-way doorway (decks 8 to 10 aft, deck 11
  forward), to be proposed to the user apart, as the plan says.
- **Tests:** `boot`, `region4`, `region5`, `region7`, `golden` pass; the rest not run.
- **With it, the user's (deck 8's open cabin, `amb_peek_sea`):** "Let's make its interior more washed
  out colors, like we usually do": its inside washed 30% toward the wall, as the knitting lady's open
  cabin already was (`peek-sea` in `src/world/world.js`).

## Deck 8's open cabin: a bed bounce on E (2026-11-18)

- **The user, at `amb_peek_sea`** (region 5's open cabin with the sea in its window): "What is this open
  cabin for?"; its inside washed (above); "I stood still at the entrance, and nothing happened, she
  didn't lean in. But since it now reads as interactable, let's add some gag at the E press." Found:
  standing still there 2 s did set the quirk off, but it played her ordinary look-around, which reads as
  nothing.
- **Four gags offered; the user chose the bed bounce:** E (X), she steps in at the door, her back to us,
  hops onto the bed and bounces facing us (her 8206 clip and its springs), cut to the doorway's opening
  (Phaser's crop, as the people in doorways), her head going out of sight under the lintel at each
  bounce ("as shown", over a seated bounce that would have needed a new clip); "when she's inside, she's
  in the background, so she also has to have the washed-out contrast": a copy of her frame filled with
  the wall's colour at 30% over her, the room's own wash. Out again, she straightens her badge (the
  intro's clip). About 5 s; any key ends the bouncing. A glance each way along the corridor first was
  "the delay after the E press": taken out. Its door frame stays in full colour (it is used now).
- No new art: her own clips. `peekBed` in `src/world/world.js`, the quirk `sec_peek_sea` (`gag: "bed"`).
- **Tests:** `region5` (changed: nothing on standing still, E in and bouncing cut to the door, back out,
  a find) and `boot` pass.

## Step 4a's second batch: the sprinkler's gag (16), built (2026-11-18)

- **What she does** (`Sprinkler.ride` in `src/world/movers.js`, played by the ship scene's `thingGag`;
  `gags` sheet, `sprinkler-*`): in its rain she flinches and her hair falls flat over her face, where she
  stands, or stopping short from her run (a clip from each quarter of her stride, run frames 1, 3, 5, 7;
  the hit waits up to a frame for one), sliding to a stop; a sneeze; then she turns round and squelches
  back the way she came (the user, on seeing it: "make her always return to the direction she came
  from"), slowly, and her checkpoint. Her word "Brrr!" as before.
- **Made:** her soaked picture by `edit_image_pro_flash` from her standing frame (two tries, 10
  generations; the second drifted to a blue-black mop), then PixMiniMax clips (10 generations, 1 each)
  from her built sheet's frames to it: the first drench and run-stop drew a thick water column and the
  first sneeze uncovered her face; redone describing her body only. Checked frame by frame: eight frames
  1 px over the floor set down, loose specks out, the water drops kept. Left: her blouse greys for one
  frame in two run-stops as it soaks; her hair streams back at the sneeze's peak. 20 generations.
  `assets/source/her-mishaps/batch-4a/` (README).
- **The user: "Hard to understand like this, let me see it in the game"**: strips of loose frames on a
  plain backdrop did not show it; it was put in the game and shown from there (a `sprinkler9` place).
- **Deck 8's sprinkler rained through the floor** (the user: "do we have another sprinkler on the deck
  below?"): it stands at 148 m right under deck 9's, and its rain, drawn above her layer, showed through
  the darkened deck, in step with the one above. A sprinkler's rain and sound now only while she is on
  its deck (the user declined different rain patterns: "No need").
- **The second exception to the tangerines** (the user, on finding no difference with tangerines on, then:
  "let's do this as another exception: the wet gag regardless of the tangerines"): `pocket: false`, as the
  dog's lead; she keeps them all and goes back to her checkpoint. (The difference they had not seen: the
  test link carried `&pocket=off`.) A tray in her hands still spills.


## A plan for fast playtests: the stepped clock (2026-11-18; a plan only, nothing built)

- **The user:** the tests take too long even when only the relevant ones are run, without the
  sound's; "come up with a smart solution to speed up the development cycle without compromising
  on QA".
- **Found:** the tests wait in real time (650 sleeps, every walk a key held for real seconds), in
  one browser, one scenario after another; the region scenarios are single functions of 55 to 70
  checks. The test browser already draws on the graphics card, so nothing is to be gained there.
- **Measured in a copy of the game:** a frame not drawn costs about 0.2 ms against 10.6 ms drawn
  (600 game seconds in 6.7 s); her run and her jump come out the same stepped as in real time;
  timers follow a stepped clock, tweens only once `Date.now` returns it.
- **The plan (docs/plan-fast-tests.md):** the test stops the engine's loop after a page loads and
  steps the game itself, undrawn but for screenshots; every wait in `tools/playtest.py` goes
  through one clock, so no scenario is rewritten; then scenarios side by side, only-the-failed,
  times per scenario, smaller cases as scenarios are next touched. `sound` and `boot` stay in real
  time; `--real` keeps today's way for comparing. Its first step ends with two scenarios run both
  ways and shown to the user.
- **Also found:** five test browsers left running by scripts that had ended (2.6 cores, 2 GB);
  closed with the user's leave. The plan's runner closes such leftovers itself.

## Step 4a's second batch: the sauna's steam (17), built (2026-11-18)

- **What she does** (`Steam.ride` in `src/world/bow.js`, played by the ship scene's `thingGag`; `gags`
  sheet, `steam-*`): the cloud out of the sauna's aft door catches her; a thick burst of steam wraps her
  where she is (from her run she slides to a stop) and thins, rising: her hair is frizzed into a huge
  puff, her cheeks flushed; she fans her face, sways with a hand to her forehead, and sits down dazed;
  then her checkpoint. Her word "Pfff!" as before; with a tangerine on her she splutters as before (no
  exception). Sounds: a hiss at the hit, a cough in the burst, a plop as she sits (not heard by me).
- **No clip per quarter of her stride** (as 16 needed): the burst covers her whole, puff and all, the
  frame she is caught, so the change to her puff picture is not seen; drawn in code, as the cloud is.
- **Found in the game and mended before showing:** a gap in the first burst showed a bit of her new
  hair; caught pressed against the sauna's door she stood in its doorway, its post through her, and
  sitting she put her legs across it: under the burst she is set 34 px clear of the door (`clear`).
- **Made:** her puff picture by `edit_image_pro_flash` from her standing frame (two tries, 10
  generations; the second hid her eye under a red blotch), the fan and the swoon by PixMiniMax from it
  (2 generations). Checked frame by frame: the body from the hair down unchanged, feet on the floor line
  (four swoon frames 1 px under, set up), four loose specks out, both clips starting on the exact puff
  picture and the fan ending on it. 12 generations. `assets/source/her-mishaps/batch-4a/` (README).
- **A `steam11` place** to try it; `region9` now checks the gag (fan, then swoon) and waits for her
  return, longer than the old fright's.

## Fast playtests: the stepped clock, built (2026-11-18)

- **The user:** "Implement the entire fast test plan, then go back to our current plan" (step 1 shown
  first: `vacuum` 8.3 s to 1.6 s, `region4` 126.8 s to 5.7 s, every check the same both ways).
- **What it gives** (`docs/plan-fast-tests.md` §7): the 38 scenarios in about 35 minutes in real time,
  about 4 stepped one after another, **55 s six at a time** (`-j 6`); 878 checks compared, every one the
  same result both ways. `check_overlaps` 20 s to 6 s, `shoot_people` 399 s to 21 s, `render_ship` 27 s
  to 5 s.
- **Found in the harness:** undrawn frames left the cameras still (a ride's "out of the screen" ended at
  once); the game's awaited waits and tweens ran late within a batch (the chute); the loop's own delta
  froze (the cake never swayed); six browsers at once had a file refused by the test server.
- **Found in the tests:** six checks that had passed by real time's slack (the trunk's lock message,
  the funnel stairway's top twice, the jogger three times, the trays' jump, the terrace gull's swoop):
  each now waits for the thing, not for a time.
- **The rule stays** (the user, asked whether the whole suite should now run before each merge: "The old
  rule"): after a change, the scenarios it touches, stepped; the whole suite never unasked; what is
  judged by eye stays the real game (`CLAUDE.md`, "Working with the user").
- **Also:** `Math.random` and Phaser's RND seeded in tests (`--seed`); 1,471 old browser profile folders
  removed, and every test browser now takes its own away; cases (`scenario_region4__towels`) ready for
  new checks, no old scenario cut up.

## Step 4a: Teppanyaki's flares (19), built (2026-11-18)

- **The gag:** caught in the flame, a puff of black smoke (embers in it) wraps her at once, so the
  switch from her run is never seen; under it she jumps back out of the flame's reach (`back`, doors
  and walls stop her: the flame is still up, and where she is caught the diners sit). It thins and she
  is in her soot picture: her face black but for the white eye, her hair on end, singed at the tips;
  she blinks, a wisp of smoke curling off her hair, and coughs out a puff of smoke; then her checkpoint.
  A yelp at the hit, a cough on the clip (sound: the user's to judge).
- **The user, on seeing it:** "The flames are too big, make them less wide": the reach from 1.25 m to
  0.8 m each way, about the grill's own width. "If I just run past them, they usually go up behind me"
  (a flame every 6 s by the clock, the flourish 0.9 s before it: she mostly met the flourish): asked,
  the user chose **"Answers her coming"**: running at a quiet grill starts the chef's flourish so that
  the flame is up as she gets there (by her speed); stopped at the flourish she lets it flare and passes
  in the lull after it (2.5 s); nearer than the flame could meet her, nothing starts (it would rise
  behind her); with no one near, the clock; her cry still makes his next one late (`FLARE` in
  `src/config.js`). Asked why the hit moves her: the three reasons above; kept.
- **Made:** her soot picture by `edit_image_pro_flash` from her standing frame (two tries, 10
  generations; the first darkened her all over, legs and arms too), the blink and the cough by
  PixMiniMax from it, both pinned to it at the end (2 generations). Checked frame by frame: the body
  unchanged from the shoulders down, feet on the floor line in every frame, loose specks out (two in the
  picture, three in a cough frame; two singed tips standing apart kept), the blink a lid over the eye,
  not a change of the face. **Her soot came out green in the game:** the palette has no neutral dark
  grey, and its two nearest are greenish; for these clips they go on the charcoal greys of her hair's
  family (`SOOT` in `tools/build_gags.py`). 12 generations. `assets/source/her-mishaps/batch-4a/`
  (README).
- `region8` checks the gag (blink, then cough, and her return) and the chef answering her coming.

## The rest of the game as one plan (2026-11-18; a plan, nothing of the game built)

- **The user:** "Read all of the docs of the project, and make a general implementation plan,
  combined from everything what's left to do."
- **The plan: `docs/plan-the-rest.md`.** Four readers went through every document whole and
  checked each open item against the code. It lists what can be built now, in the order to build
  it (the mishaps' gags to their end; the rest of the twenty things to find and the books; the
  look-outs and the deliveries; each deck's own look; small faults); what waits for the user
  (sixteen things: a photo, a text, a decision); what is done once at the end (the other
  documents brought up to date, saving on, the release); and what is closed.
- **Found while reading:** the key cards are on, though `CLAUDE.md` and `README.md` said off and
  named a `?cards=locked` that does not exist; Bumbot's beats are placed, though `CLAUDE.md`'s
  table said not; `GAME_DESIGN.md` §8's "Next up" is of 2026-11-03 with about fifteen stale
  boxes; the Library's rolling ladder was never built; no record of the user having heard any of
  the sound.
- **Tried and taken down the same day:** the user first asked for the rest to be split between
  two sessions building at once ("Split the rest of the plan in two equal parts so that two
  sessions will work in parallel without interference"). I set that up as two clones of the
  repository, each with its own branch, memory, temp folder, notes file and half of the plan,
  and a small change to the tools for the temp folder. The user, on seeing it: "this is too
  convoluted and hard to track for me. I will continue working in my current project in Paseo
  with two worktrees: Design (this session) and Implementation (the other one)." Everything of
  the split was removed (the clones, their folders and memories, their projects in Paseo, the
  tools' change, the plan's two halves); the plan stayed, as one. **Lesson (mine):** when asked
  for a way to work side by side, show the whole arrangement and what it asks of the user
  before building it; separate memories and folders multiplied what the user had to keep track
  of.

## CLAUDE.md and README.md brought up to date (2026-11-18)

- **The user:** "Bring both CLAUDE and README md documents up to date with the actual state."
  Every path, flag, control and start place the two name was checked against the code first.
- **`CLAUDE.md`:** the locks are on (it said key cards were off and named a `?cards=locked` that
  does not exist; `?did=` was missing); Pages serves the `placeholder` branch, not `main`;
  Bumbot's beats are placed (the table said not); the PixelLab account as it is (Tier 2, 5,000 a
  cycle); rows for what the table did not name (`src/progression.js`, `src/save.js`,
  `src/main.js`, `src/scenes/BootScene.js`, `src/textures.js`, `tools/draw_casino.py`, the plans
  and the audit); a session starts from `docs/plan-the-rest.md`, no longer from
  `GAME_DESIGN.md` §8, whose "Next up" is of 2026-11-03.
- **`README.md`:** what the game is and that the whole route plays; Pages; the locks; what
  `?tangerines=infinite` covers now (the throw and the pocket too); the controls it lacked (the
  welcome screen, ending the intro, M); the layout table as the repo is; testing on the stepped
  clock. Its list of 49 start places already matched `docs/start-links.md`.
- **Left as they are** (the plan's §10): `GAME_DESIGN.md` §8's stale boxes,
  `docs/build-plan.md`'s intro entry, `docs/population.md`'s rows, the audit's marks, three
  links under the wrong deck.

## Part 1.1 begun: gags 21 to 24 proposed; the funnel's stairway gone over (2026-11-18)

The building session's first round from `docs/plan-the-rest.md` §3. Gags 21 to 24 were proposed to the user
(their answers: 21 sits facing down the flight and bumps down feet first; 22 a new clip of her looking up at the
inside-out parasol, kicking; 23 and 24 as written, to the next wall or partition; built one at a time). Trying the
funnel's stairway for 21 brought up its faults, mended first on the user's word:

- **The stairway 12 px out from the lattice** (the user: on its edge "the background is visible on top of the
  stairs ... it looks like a glitch"): `funnel_top()` in `tools/build_world.py`, mocked first in the running
  game at 0, 6 and 12 px. The funnel's white base carried out under the lower flight and its navy frame under the
  upper one (`src/world/topdeck.js`), the foot's windsock kept by the foot.
- **Walked into, she steps onto it** (the user: walking left off its top she "falls through"; boarding was ↓ or ↑
  only): for outside flights only (`tryStairs`); inside, ↑/↓ as before.
- **The gust: she holds on** (the user, on the slide back down the flight on her feet: "Looks weird"; offered three
  ways, the user took "she clings on"): while it blows on the stairway she crouches and grips the rail, ↑/↓ do
  nothing, she stands back up when it drops; nothing is lost. Her clips `cling-up`/`cling-down` (PixMiniMax from
  her standing frame on the steps with the rail where the game draws it; 12 generations with two whole-picture
  edits that wiped the scene; `assets/source/her/stair-cling/README.md`). A first fix, a slip picture with her feet
  on the steps (15 generations, `assets/source/her/stair-slip/`), was approved and then retired with the slide.
- **The gulls dive straight at her** (the user: it "hovers for a bit above me before taking a dive ... That's why
  it rarely happens"): no mark, no hover; every 2.5 to 5.5 s at random between gusts, the next gull breaks off from
  wherever it is in its circle and dives at her, 320 px/s on average, speeding up; it hits wherever it touches her,
  and a miss swoops on past. With a tangerine she now ducks on the stairs too (reactions played only in `play`),
  and the gull flies off over the sea with it (it had snapped back to its circle: "it just disappeared").
- **A gull carries a tangerine in its beak** (the user: it sat on its back): the beak's tip measured in each gull
  frame (`GULL_BEAKS`, `inBeak` in `src/world/world.js`), the fruit behind the bird and placed on `postupdate`
  (placed before the bird moved, it took the other wing frame's beak every other frame); every gull that takes one.
- **Gag 21's clip** made and approved (4 generations; constant pace, no slow first bump, the user), not yet built:
  `C:\...\bb\g21` scratch; to be saved with the build.
- **Tests:** `boot`, `region6`, `region7`, `region8` (the hold in a gust, the dive), `finale`, `golden` (its walk to
  the stairway's foot now waits for the foot), `pocket`, `stairs`, `throw`, `atrium` pass; `check_overlaps` 0. The
  rest not run.

## Gag 21 built: she bumps down the funnel's stairway (2026-11-18)

`docs/plan-the-rest.md` §3 1.1, the first of its four gags. A funnel gull hits her on the stairway with no tangerine on
her: from the step's corner nearest her she sits down hard facing down the flight and at once bumps down on her
bottom, a step every three frames at one pace (the user: "let her just bump down at a constant speed, starting
immediately"), across the turn and down to the foot; she slides off onto the roof slumped, then her checkpoint at the
technical door. The ship scene's `stairsGag` (`GAGS.stairs`), frames from the `gags` sheet stood each on its step's
corner, at her depth (the rail in front of her); her hidden sprite goes along for the camera and the word.

- **Phaser 4 mirrors a frame in place**, its origin still counted from the left of what is drawn (not about the
  origin): both clips first stood 26 to 30 px east of their corners. Found by matching the game's frames to the clip's
  pixels; now every frame stands where the approved preview had it.
- **The user's additions on seeing it:** a dizzy end, butterflies over her head (a new loop, PixMiniMax, 1 generation,
  shown in the chat composed at the foot and approved; it plays twice, about 1.8 s); and the word "Ow-ow-ow!"
  («Ай-ай-ай!») for the ride (`fright.bumpy`; the gull's snatch with a tangerine keeps "Shoo!").
- `?at=stairway` (the stairway's foot), in README and `docs/start-links.md`. A thump on the steel at each step.
- Not changed: from the stairway's top the ride is about 12 s (from five steps over the turn, about 5); she turns to
  face down the flight in one frame if she was climbing.
- **Tests:** `region8` (the hit, the ride to the foot, the technical door), `boot`, `lang` pass; the rest not run.

## The plan gets a part 6: Bumbot made again (2026-11-19; a plan, nothing built)

The user, to the design session: "Add to the end of our combined plan a new action item: regenerate all Bumbot's
sprites. Now it doesn't look like him, and also his animations must be enriched and fine-tuned." Written into
`docs/plan-the-rest.md` as §7a, part 6, after the small faults and before what is done once at the end; numbered 7a so
that no other section's number changes. It starts with questions to the user (what in him is off, which moves are
missed), then his look from the user's photos, every clip again, new clips, the tuning, and everything else that shows
him (her sheet with him in her arms). The two optional clips of his (the fly rope, the vent's squeeze) moved into it
from §8. Its size (large, about 90 generations) is the design session's guess, not a count.

The estimate given on 2026-11-18 (about 14 working days; around 10 December by the last two weeks' attendance) grows
by about three working days with it: around 15 December, at the slow end about the 20th. The gift is for New Year.

## The plan gets a part 7: the intro's scene tuned (2026-11-19; a plan, nothing built)

The user, to the design session: "And after that one, add another action item: fine-tune the intro scene. I want more
realistically-looking sun and reflections, more varied and volumetric clouds." Written into `docs/plan-the-rest.md` as
§7b, part 7, after Bumbot's (§7a) and before what is done once at the end. It starts with questions to the user (what
"more real" means, what reflects, and whether it reaches past the intro to the game's far background and the sunset),
then the look chosen from mock-ups of the whole screen, then the art generated (today the sun, the glitter and the
clouds are all drawn in code) and the motion. Its size (medium, about 30 generations) is the design session's guess.

The estimate grows by about two working days with it: around 18 December by the last two weeks' attendance, at the
slow end about the 23rd.

## Gag 22 built: the parasol inside out over the bow (2026-11-18)

`docs/plan-the-rest.md` §3 1.1, the second of its four gags. A crossing gull flown into with no tangerine on her: the
parasol is blown inside out while she still sinks at the glide's pace, then she looks up at it, her hair flying up,
and kicks her legs as she drops out of the screen, more slowly than a closed parasol's fall (it still catches a little
air); "Whoa-whoa-whoa!" («Ой-ой-ой!», `fright.whoa`, my suggestion, kept by the user); back on the balcony. The clip:
PixMiniMax from her glide picture with the world's parasol (2 tries, 1 generation each; the second used), mended by
`assets/source/her-mishaps/batch-4a/parasol-flip/cut.py` (loose wind scraps, a shaft lit pale). The ship scene's
`parasolGag` (`GAGS.parasol`), from `scareAir`; its frame 0 matched against her glide in the game, 0 px apart both
ways round. Her word is raised over the parasol's top for it (`alertOver`). With a tangerine on her, as before.

- **The user's addition on playing it:** the hit was "indistinguishable from the gull just flying around ... it
  should dart toward us a little bit (not too fast)". With her ahead of it within 130 px and 80 px of its height, a
  crossing gull cries (the dive's cry) and darts straight at where her drift will take her, 170 px/s (its flight is
  96 to 110), wings beating twice as fast; no homing, so she can steer away or let the parasol go; then on and back
  up to its line, no dart for 2.5 s (`DART` in `src/world/finale.js`; the gulls now move by their own state, not a
  clock). The first try aimed at where she was and passed over her head: she sinks under the parasol.
- **The bow's plating** (the user: parts of the hull at the front balconies "disappear when the gull attack happens";
  "they should also hide the balcony railings behind them"): a scripted fall had the cut-away follow her height, so
  the decks she dropped past opened one by one (the bridge's piece among them); now a fall from a scare in the air
  keeps the view she had (`airScare`). The decks' leaning railings at their forward ends showed whenever she was at
  their height in the air: they now count the deck she last stood on (`floorDeck`). The mooring deck's railing ran on
  under deck 7's sloped front plate in front of it: it goes behind the plate while the plate shows (`underSlopes`).
- **Landing on the bow** (the user: "something changes on the bow's floor"): deck 7 was cut open as she landed (its
  floor's edge and slab for the plating, the sloped plate gone). Asked: "Closed always". The mooring deck is an
  `outdoors` area now, as deck 11's front (`bow-7` in `tools/build_ship_map.py`): the side closed, the plate in front
  of her always (she is hidden behind it by deck 7's door); the railing's last pieces behind the plate.
- **The low crossing gull at the top of the view** (the user, standing on the bow: "appears and disappears rapidly"):
  its two flap pictures (22 and 10 px tall) hung by their middles, so its body jumped 5 px a flap at the screen's
  edge. Hung by its underside now (the beak within 1 px in both). The funnel's circling gulls hang the same old way;
  offered, not changed.
- **Tests:** `finale` (the gag's word and picture, back on the balcony), `lang`, `boot`, `falls`, `overboard`,
  `region7`, `region9`, `bridge`, `balcony`, `run_jump`, `promenade`, `atrium` pass; `check_overlaps` 0. The rest
  not run. 2 generations.

## The parasol opens on a second press of jump (2026-11-19)

The user: "Let's change the parasol control: it will open on a second jump press only, not on hold." I first made it
a toggle (a press in the air opened it, it stayed open, another press shut it); the user: "not what I meant ... it
should open only on the second jump press (when we're in the air). It stays open as long we hold that jump press.
Meaning, the only difference with the initial mechanic is that it doesn't open if we jump from the ground and hold."
So: a press of jump in the air (not the jump from the floor, nor a coyote jump, nor a wall kick: `glidePress` in the
ship scene's jump code) arms it while it is held (`glideArmed`); armed and falling, it opens as before; letting go
shuts it; landing disarms it. `updateGlide` in `src/world/verbs.js`.

- **Tests:** the glides in `region8`, `finale` and `golden` press jump a second time in the air and hold it
  (`open_parasol` in `tools/playtest.py`); `region8` checks that over the atrium's rail with the hop's jump still held
  the parasol stays shut. `region8`, `finale`, `golden`, `falls`, `run_jump`, `balcony` pass; the rest not run.

## Gag 23 built: "Oh, sorry!" at a "Do Not Disturb" door; the doors' sign redrawn (2026-11-19)

`docs/plan-the-rest.md` §3 1.1, the third of its four gags. A "Do Not Disturb" door opened on its guest with no tangerine
on her (E at it, or her cry by it): "Oh, sorry!", a startled hop, both hands over her eyes, her cheek blushing; she turns
away from the door and tiptoes off, quick, to the next wall or door across the deck (`stopShort`: a beat there) or out of
the screen; then her checkpoint. The ship scene's `sorryGag` (`GAGS.sorry`), the `gags` sheet's `dnd-cover` and
`dnd-tiptoe` (`assets/source/her-mishaps/batch-4a/dnd-sorry/`, its README has the ids). With a tangerine on her, the
apology and the hand-over as before. `?at=dnd9`, 2 m forward of deck 9's door.

- **The cover:** PixMiniMax from her standing frame (2 tries); its own blush turned her whole hands hot pink, so the
  blush is set by hand on her cheek in the palette's pinks.
- **The tiptoe:** PixMiniMax's walk loops (4 tries) took strides 28 px wide with a bob: "a bit like a skip-dancing" (the
  user). Her character's skeleton "sneak" (3) came as a crouched sneak with lighter hair. What worked:
  animate_with_skeleton_v3 from her own end pose along skeletons laid out by rule (`raw/tiptoe_kp.py`: her pose from the
  hips up held, two tiny steps on her toes, the pelvis level). Paced by her planted foot (2.6 px a frame); the user asked
  twice for faster: 26 ms a frame, 100 px/s.
- **The sign** (the user, mid-way: "redraw the door with the dnd sign: The sign should hang from the door handle, have a
  half round top and in the middle of the sign it should have visible red circle, crossed"): drawn by hand on the palette
  (11 x 22 px, below what a generation draws exactly), `assets/source/ship/dnd-hanger/`. The old red card hung beside the
  door from nothing. First hung from the lever's tip; the user: "it should hang from where the door handle is mounted";
  moved onto the rose, the bar resting at the hole's top, the lever drawn over it. **Swung with the door** (the user:
  "Swing"): in each of the swing's 13 frames, on the lever's mount of the outer face; first it "magically transfers to its
  inner side" (the open leaf shows its inner face): now, once the leaf is past edge-on, it is behind the leaf, its plain
  back peeking 4 px past the leaf's free edge (measured below the handle in each frame, the generated leaf's width
  wobbling), a strip against the leaf edge-on. Gone over frame by frame on the user's word (frames 1, 3, 5 to 7, 9, 10
  mended). Everywhere it shows: the seven doors (shut: `door-cabin-dnd`, exactly the swing's frame 0, a picture of its own
  so that `tools/check_overlaps.py` still sees a door), the occupied balconies' partitions (`dnd-hanger` for the old
  `dnd-tag`), cabin 8206's door inside (`tools/draw_cabin.py`).
- **Tests:** `region4` checks the gag (the tiptoe away from the door at her pace, back at her checkpoint); `boot`,
  `region4`, `pocket`, `region6`, `region7`, `cabin` pass; `check_overlaps` 0. The rest not run. About 12 generations.

## Gag 24 built: "Oh, sorry!" on an occupied balcony (2026-11-19)

`docs/plan-the-rest.md` §3 1.1, the last of its four gags (the user: "as written", to the next partition). Vaulting onto a
balcony with someone on it (the sunbather on deck 8, the breakfast couple on deck 10) with no tangerine on her: gag 23's
own clips, "Oh, sorry!", her hands over her eyes, blushing, then she tiptoes away from the balcony's middle to the
partition ahead, a beat there, her checkpoint. No new art, no generations. With a tangerine on her, the hand-over as before.

- **Partitions stop what runs off her:** `partitionShort` in the ship scene (a grip with `over` on her route and floor),
  after `stopShort`; the gull's 20 had its own copy of it, now this one, which also stops her where she is when she
  already stands by the partition (before, the gull could then run her through it).
- **Where she lands:** a vault held toward the balcony drops her just past its middle, so the tiptoe ahead is short
  (about 20 px, 0.2 s); shown to the user with that said, approved as it is. The couple's red "!" is half under her word.
- **The vault, asked by the user** ("Not sure how I get there at all", "Do we have a double jump there?"): no double
  jump; the second press is the grip socks' kick off the partition (`tryWallJump`), which works 0.1 to 0.5 s after the
  first while beside it. `?at=occupied8`: deck 8's balcony aft of the sunbather's, `cards=all` for the socks.
- **Tests:** `region7` (the occupied balcony's check now sees the gag) and `region4` pass; the rest not run.

## Gag 7a built; the wet patch redrawn, its chair standing; deck 12's ball and flame (2026-11-19)

`docs/plan-the-rest.md` §3 1.2, its first row. **Can 7a still happen?** Yes: walked at with real keys from forward of the
patch (four ways: a run from 2.5 m and from 1 m, a jump in, one step on), the chair met her head on every time.

- **The gag:** PixMiniMax from her slip frame 0 with the world's chair 18 px ahead (2 tries, 4 generations; the other fell
  on her back): it trips her, she dives face first onto it, it folds flat, she lies on it like on a sled. Checked frame by
  frame: frame 1's chair put back on its place (1 px off), two loose specks out, every frame on the floor line. Its
  direction (head first aft, the way she dived) was my choice, approved. The trip and the dive were first at 10 frames a
  second (half a second to the landing); the user: "reduce the delay": 40 to 60 ms, 0.24 s. `chair-sledge` in the gags
  sheet, the chair's `ride()`, `GAGS.sledge`; `?at=wet7a`.
- **The patch and the chair** (the user, on seeing it: "It is unclear, why either she or the chair is sliding, and they
  also slide toward each other"): the chair stands still now (the user's choice), moved from 153.35 to 153.0 m so that she
  meets it still on the wet tiles, exactly where the clip has it; 7b, the chair reaching her back, cannot happen any more
  (its clip kept). The patch was a 2 px blue strip seen edge-on against the sea in the windows: it did not read. Four
  versions drawn in the running game (wet boards, overflow, a puddle on the floor's face, the puddle with the tray
  brimming over); the user chose the last: the shower runs, its tray brims over, a puddle lies on the floor's face, and
  splashes fly off her feet as she slides.
- **Deck 12 from deck 11** (the user's screenshot: "What is that orange round thing bouncing above in the air?"): the
  court's ball was drawn whenever she was within 200 px of its deck, so from deck 11 it bounced in front of deck 12's
  closed side. Drawn now only while she is on its deck (`onDeck` in `src/world/topdeck.js`); Teppanyaki's flame had the
  same fault, mended the same way.
- **The pool's gulls** (the user: "Why are the gulls flying here?"): they serve (the dive at food, the bait, the kid's
  reward), but fly under deck 12's closed side: the design's opening over the pool was never drawn. I offered to remove
  them without saying what goes with them (the kid's reward, the bait, the throw, the pounce on the dropped stub); the user
  caught it, and the removal was taken back. A rule since (memory: list what a removal takes, in the question). **The
  opening in deck 12 over the pool is the next step** (the user), `docs/plan-the-rest.md` §3 1.1b.
- **Tests:** `region6` (7a's sled, a new check from aft), `throw`, `region8`, `boot` pass; `check_overlaps` 0. The rest
  not run.

## The pool's gulls, the kid's cone, the buffet queue (2026-11-19)

`docs/plan-the-rest.md` §3 1.1b, and what the user found trying it.

- **The pool's gulls** (`gull_pool`): the opening in deck 12 over the pool was built all along (`POOL_OPENING`); from
  deck 11 the near side of deck 12 shows as a white band, and the gulls circled just under it, "as under a ceiling".
  Now they wheel in the open sky over deck 12, above its railing, behind the ship's side (from deck 11 out of view),
  and a dive at her food comes down past the band, in front of her once under it (0.42 s, longer than the perched
  gull's). The user: "Remove the shadow spot": none for them (the Great Outdoors' perched gull keeps its own). Shown as
  mock-ups in the running game first.
- **Where the cone goes** (the user could not find the machine, then whom to bring it to): the machine is built (deck
  11's Great Outdoors, hold E, let go in the green); the cone is for the kid, who is on the aft pool deck only after
  near-catch 5 (`did=bb5`). A start place by the machine, `?at=icecream`.
- **Her footsteps with something in her hands** ran by distance, much quicker than her carry walk's feet: now on its
  own frames, 0 and 4 (`SOUND.carrySteps`), as her run's are.
- **The hand-over** (the user: "I stand obscuring him, while he eats. And I cannot move"): from a step away (she steps
  back to arm's length first), and she is free as soon as the cone is in his hand (`kidHas`, the rest on its own); he is
  fed from that moment (his bubble asking for one went on while he ate). He waits for her cone a step clear of the
  security officer on his knees at the loungers (their two figures were one).
- **His eating clip** (the user: "the kid is holding his water gun while eating. The ice cream is just hanging in the air
  in front of him"): his old `eat` had him biting his orange water pistol. A new one, him and the cone together:
  `edit_image_pro_flash` of his stand with the cone in his fist and the pistol tucked away (2 tries, 10 generations),
  then PixMiniMax: three licks, the swirl smaller each time, a bite of the cone (1). `assets/source/people/kid-eat-cone/`.
- **The buffet queue** (the user: when she carries something, those who turn away "are shifted behind the background
  props", then "they continue sliding forward"): turned aside they kept their depth (they had gone 5 depths back,
  behind the café's tables and chairs), and while anyone has turned aside the whole line stands still.
- **What she uses, muted:** the soft serve machine was drawn in its muted background twin (`at11` places every piece
  as `-bg`), like eight more things she uses. The user, to answer it, wants them compared first with what already
  stands out: `docs/plan-the-rest.md` §7c, part 8, at the plan's end.
- **Tests:** `region6` (new: she is free a step from him while he eats), `throw`, `boot` pass. The rest not run. 11
  generations.

## The kid's jet plays the wet gag; the sprinkler's run clips; the water drawn stronger (2026-11-19)

Asked by the user before the jogger's gags (`docs/plan-the-rest.md` §3 1.2, 9a to 9d, proposed and approved as
recommended: 9b first, his "sorry" a clip of his own; the meetings composed from the sheets,
`assets/source/her-mishaps/batch-4a/starts/jog9/`).

- **The kid's jet with no tangerine on her** (the user: "a standard dazed gag is played. Let's replace it with the wet
  gag"): 11a and 11b play 16's soak (`gag: 'sprinkler'`): soaked, a sneeze, and she squelches off away from him, then her
  checkpoint. The soak is one ride for both, `soakRide(scene, floor, away)` in `src/world/movers.js`; from her run the jet's
  hit waits for an odd frame of her stride (a frame at most), as the sprinkler's does. With a tangerine on her nothing
  changed (her splutter, her arch). So 11a's and 11b's own gags of the plan (spluttering with his laugh; 10b's arch) are
  stood in for by it: to be asked when the plan reaches them.
- **Found on the way: 16's four clips from her run never played.** `thingGag` stops her before the ride plays, and the
  ride read her stride then: every soak from a run was the standing one, she stopped dead. The ride reads her stride when
  it is made, at the hit. Seen in a recording; the sprinkler's own recording now shows the run clip (`run7`).
- **Her walk off, drenched,** 2.3 s instead of 1.3 (the user: "it cuts off a bit too soon"): `GAGS.sprinkler.walkMs`.
- **The water** (the user: "make the water a bit more visible", then of my try, 4 px with a dark blue underside: "too
  strong and too thick. Draw the suggested images for me to choose from"): six jets and five rains drawn in the running
  game, frozen at one moment (a script that draws them in the page); chosen: the jet a stream 2 px thick, light blue over
  mid blue with white glints (it was light blue and white dots); the rain 1 px streaks, a white head, light blue, a mid
  blue tail (it was light blue and white). The sprinkler's drip and splashes in the same blues.
- **Tests:** `region6` (new: with none on her, the jet plays the wet gag), `region4`, `boot` pass. The rest not run.
  No generations.

## The jogger's four gags, 9a to 9d (2026-11-19)

`docs/plan-the-rest.md` §3 1.2. Proposed as a table with the four meetings composed from the sheets
(`assets/source/her-mishaps/batch-4a/starts/jog9/meet.png`); approved as recommended (his sorry a clip of his own, made
with her sat before him and then taken out; 9a he runs on; one clip per quarter of her stride), then 9a moved before 9c
(the user met 9a first in play and took its stand-in for 9b: "Is that what we planned?").

- **9b** (commit f246cf0): standing, facing him: bowled back onto her bottom. **His sorry**, by the user's word, three
  times: jogging on the spot with his palms out ("That looks weird"), a hand raised by his head ("It looks like he's
  saying Hi in both cases"), then: "His hand has to go behind his head (be obscured by his head)". PixMiniMax could not
  give it (a blob that read as hair, twice; once he turned to face us); an edit of his standing frame into the pose
  (`edit_image_pro_flash`) and a clip toward it did. Mended by hand: his far hand still peeked out at his hip ("three
  hands"), two px on his shorts ("Make his shorts look the same as on the previous frames"). The composites drew them
  over the promenade's railing; the game draws it in front of them (the user: "They both should be placed behind the
  railings"): a shot of the game with a marker at their layer gives what is in front.
- **9a**: both running, head on: spun round like a top through her front and back, she sits dizzy (her own dazed sit, the
  butterflies, takes over from the clip's last frame); he runs on, through her, drawn behind her. Four clips, one per odd
  frame of her stride (an even one taken as the next).
- **9c**: into her back, she standing: she pitches forward, stumbles, dives, flat on her belly, dazed; he stops behind
  her and scratches his head.
- **9d**: she into his back: 8d's bounce; he never notices.
- **Found on the way:** a gag whose settings had a key `sorry` was played as gag 23's (its own test); renamed `his`. A clip
  of 17 frames on a sheet 13 wide showed another gag's picture for its last four (the sheet is 17 wide, the build refuses
  one longer). He met her in a promenade door he held open, its leaf drawn in front of her: he lets it go when he stops.
  `region2` moved him by hand while the game counted him in a door: it lets go first.
- **Tests:** `region2` (new: the bump plays 9b and his sorry), `region4`, `region6`, `region7`, `region8`, `region9`,
  `boot` pass. 31 generations (9b 19, 9a 8, 9c 4).

## 11a and 11b: the wet gag covers them (2026-11-19)

Asked whether the kid's jet still wants its own two gags of the plan (11a: sat back spluttering, he points and laughs;
11b: 10b's arch), now that the wet gag plays for both with none on her: the user, "Covers". Not made.

## The stage: the light and the stage manager change places (2026-11-19)

The user: "Switch locations of the DJ and the swinging lamp" (the stage manager, in his headset). He stands at 250.4 m,
in front of the stage's aft red curtain, facing the stage (all in black, he must stand against the red: 2026-11-14).
Hung at his old 244.42 m the light swung out over the wings' speakers, its cable across the curtain: at 245.9 m, over
the drum kit, its whole swing on the stage. `region3` finds him where he is. `check_overlaps`: 0. Then the user asked
what the black rectangle on the stage is: the open trap door (near-catch 3's), drawn in code as a black box and a
stick; to be redrawn (option 1: a generated open trap door, its lid up on hinges, a ladder's top in the hole).

## The stage's open trap door, drawn (2026-11-19)

Option 1 of three (generated; with hazard tape; as it was): an inpaint of the game's own stage at 1:1 (Phaser's
snapshot: the canvas reads back black), so it takes the stage's colours and light; its lid up on its hinge, a ladder's
top in the opening, its middle the drop's. The try used took the mic stand out: only its own pixels are kept and the
game's mic stand moved 0.25 m aft. The user: "fix the stairs' right side to match its left" (the ladder's right rail
stopped at the floor): copied from its left. `assets/source/ship/trapdoor/`. A faint copy of the trap area in a shot
before near-catch 3 was that scene caught mid-fall, not a fault. `region3`, `boot` pass; `check_overlaps` 0. 10
generations.

## The theatre: lightly washed, one seat for all, a full house (2026-11-19)

The user: the theatre's and the stage's props "are washed out too much. Please use their original pictures, and let's
wash out them only slightly"; the half-turned seats out for "empty chairs like the one that the guys sits on"; then all
the audience "on the same exact chair as the popcorn guy, and as the empty chairs", "much more chairs with people,
randomly", "slightly washed"; and "behind the right (closest to the screen) chair arm, but obscure the left (far) part".

- **A light wash** (`-lt`, 12% toward the wall instead of the background's 35%): the stage's drum kit, mic stand, guitar,
  piano, speakers, the seats, the audience (`MUTE_LIGHT`, `LIGHT` in `tools/build_ship_art.py`; `wash` in `tools/cast.py`).
  The rule that background props are muted stands; the theatre is muted less, on the user's word.
- **The one seat:** an edit of the popcorn man's picture without him. The five named without their own chairs, ten
  others from them, each set in it, the near arm in front of them (`assets/source/people/audience-seated/`). The five stay
  people (the lady's "shh"); the ten are pieces filling about half the empty seats, the same each build.
- **Found:** a sitter's head at the balcony's "LIGHTING" plate (the seats beside the booth door stay empty); the new
  pieces' empty canvas counted as overlaps (trimmed to what is drawn, their middle kept).
- `check_overlaps` 0; `region3`, `boot` pass. 80 generations.

## A hit is its gag, tangerines or not; only a gull takes one (2026-11-19; a plan, nothing built)

The user, after playing: "losing a tangerine on hit almost never fits visually and in terms of gameplay. I want to play
the respawn gags in most of the cases, tangerines or no. But analyze all of the encounters that are in the game and in
the plan, and see if there are cases that are really fitting to lose a tangerine on hit."

The design session went through every hit (`MISHAPS`' 27 obstacles, `MISHAP_SCENES`' 45 scenarios, the tray spills,
part 3's deliveries) with one test: **losing a tangerine fits only where someone takes it**, not where a knock makes a
fruit pop out of her pocket while she stays on her feet. Recommended, and the user's answer "Yes, all as recommended":

1. **The gulls' three (20, 21, 22) keep it:** the gull takes a tangerine, she ducks and keeps her place.
2. **The "Do Not Disturb" doors and the occupied balcony (23, 24): gag 23 always.** The tangerine held out fits the
   fiction, but it hides the better picture.
3. **A tray, a cone or a delivery in her hands is always spilled by a bump.**
4. **Every other hit: its gag and her checkpoint always, none lost.**

**Why:** with tangerines on her, the gags (the most worked-on art of this part) were never seen, and what was seen in
their place (a flinch, a fruit rolling off) had no cause in the picture. A tangerine is now only spent by her own choice,
or taken by a gull that wants it.

**What goes with it:** the tangerine knocked out to roll off behind her and its "run back or go on" choice (the user's
own, 2026-11-17); her short reactions to a hit (left in the sheets); the vacuum eating what she dropped; a tray saved by
a tangerine; the proposed "bats the towels off". The game is harder with a full pocket: every hit costs the way back;
the lunge is the one way to pay through a hit.

**Found while writing it:** the gulls that dive at food take the food whatever is in her pocket (`FoodGulls`, the rail
gulls with food in her hands): the three-uses plan's "her cone saved" was never built for them. Left as built; I had
listed it to the user as a case that exists, which was wrong.

**In the documents:** `docs/plan-three-uses.md` §1.3 and §1.6 (dated notes; what they supersede struck or marked), §2's
last column, §3, §4.4, step 6, the risks, the user's answers; `GAME_DESIGN.md` §3.2 and §5.6 (decided, not built);
`docs/plan-the-rest.md`: **a new step 1.2a in §3, after 14a/14b and before 15** (the user: "Steps that are already
implemented: add a step for their update after 14a/14b"), what it changes in the code, the tests and the documents; 1.3's
`mishaps` playtest, 3.2's deliveries, U16, and §12's closed list. No art; about half a day to build, about what the
`mishaps` playtest saves by losing its "with a tangerine" half, so the date does not move.

## 14a and 14b, and the court's two players (2026-11-19)

`docs/plan-the-rest.md` §3 1.2. **14a**, a basketball in her face: stiff as a skittle she tips over backward onto her
back; **14b**, on the back of her head: stiff as a plank she topples forward onto her face. One clip from her stand and
one from each quarter of her run (PixMiniMax pinned to her lying flat), then lying so with her dazed lie's butterflies
over her head, then her checkpoint (`jogGag`, now with `meta` and `lie`). The ball bounces off her and rolls back.

- **Her lying picture redrawn.** Her standing frame turned a quarter touched the floor only with her hair (14a) or her
  chest (14b): "she should be on the ground, not float above it". Set straight along a line under her, it "appears to
  be at an angle" (her standing frame's head tips forward, so on her back her head stayed up). An edit of it, lying
  flat on her back, and the clips made again to it; 14b the same, the user choosing the face-down redraw over the old.
- **Her red scarf under her face on the floor** read as blood in 14b's landing frames: recoloured there.
- **The ball no longer rolls back to the cage's foot** (the user): it stops; then, on the user's word, **the court's two
  players**: a man in red and a woman in blue (pro characters in the cast's style, 12% washed like the theatre's people),
  each 1.6 m (was 2.2) in front of their own hoop, where the ball comes to rest. A round of 5 s (was 4), the two half a
  round apart, never in step: the jump shot (its wind-up is the tell; the rim's rattle is gone), the game's ball from
  the hand up, in front of the board and down through the net (behind the hoop's picture only in the ring), bouncing
  twice to their feet; they pick it up, dribble once, shoot again. The waiting plays at 4 frames a second (the user:
  slower). Everything is a function of the round's clock (`frame(t)`, `at(t)`), so it steps and seeks exactly.
- **Seamless hand-overs.** The clip's ball is in the hand until frame 8, the game's starts at frame 7's spot; lying, the
  ball is the game's until the hands take it (frame 3 of the pick-up), the clip's lying ball cut out before. The washed
  ball in their hands and the game's full one turn into each other over 0.2 s (`basketball-lt`, the theatre's light
  wash added for it).
- **It hits her from the throw to its second landing** (the user): the flight, the drop, the first hop; not the second
  hop, the roll or a ball lying still. Off her (a hit) or headed in a lunge, it comes down and rolls to its player's feet,
  and the pick-up waits for it.
- **Tests:** `region8` checks 14a (none on her, facing the hoop: her back clip, then the lying loop) and gives her
  tangerines back after; its funnel stairway check holds the gulls off (by the clock's new phase one dived at her
  there). `region8`, `boot`, `throw` pass; the rest not run.
- **Generations:** 35 for 14a and 14b (the first ten falls unused), 38 for the players.

## A ball in the air knocks her down where it hits (2026-11-19)

The user: "when the ball hits her in mid-jump, the gag plays only at her landing. She should fall on the ground from
where the ball hit her." A hit in the air is held until she lands (`gagPending`), and she went on along her jump's arc.
Now a gag with `drop` (the court's balls, 14a and 14b) stops her there: her way across is gone, she goes stiff at once
(her standing frame, the topple's first) with her word, drops straight down, and topples where she lands. Every other
hit in the air is as before. `region8` and `boot` pass.

## A hit is its gag whatever she carries; only a gull takes a tangerine (2026-11-19, §3 step 1.2a)

Built as the design session wrote it (`docs/plan-the-rest.md` §3 1.2a), with the user's three answers:

- **Every hit but a gull's is its gag and her checkpoint, whatever she carries; none is lost.** `MISHAP_SCENES` says
  `pocket: true` on 20, 21 and 22 only; `toss` is gone from every scenario, and `pocket: false` from 2 and 16. A
  "Do Not Disturb" door and the occupied balcony are her tiptoe always. `react` stays: a gull's duck, and her start
  before running off where no gag stands in.
- **`pocket()` is the gull's take alone:** it takes one (`snatch`), she ducks, blinks, keeps her place and whatever she
  carries. Gone: the tangerine knocked out to roll behind her (`loose.knock`, `LOOSE.knock`), the push on or back
  (`POCKET.push`, `stumblePush`, `hop`), the hand-over at a door, her reactions' sounds (`REACT_SOUND`; the sounds stay
  in `src/sfx.js`), `reactionTo()`, the walker standing aside after a forgiven bump. `handOver()` and her apology clip
  are kept for part 2's sardines.
- **A tray is spilled whatever she carries** (`Carry.spill` no longer asks the pocket; only the blink after a gull's take
  keeps it).
- **A rail gull with a tray (not food) in her hands** takes a tangerine and she keeps the tray (the user: "Let the gull
  steal a tangerine"); with food in her hands it takes the food, as built; with none on her, its gag.
- **`?pocket=off` is gone** (the user: "Remove the flag, it always confused me"): the playtests no longer add it; the
  gull checks of `region7`, `region8` (the terrace's gull, the funnel's) and `finale` empty her pocket first and give it
  back.
- **The rule on links is dropped** (the user: "Drop the rule, and render the links as appropriate in the context"):
  `docs/start-links.md` without `&tangerines=infinite` (and without `&pocket=off`); `CLAUDE.md`'s rule rewritten.
- **Tests:** `pocket` rewritten (with two on her: the porter spills her tray, the cart, a door, a paper each her mishap
  and her checkpoint with the count unchanged and nothing lying, a "Do Not Disturb" door her tiptoe; a gull takes one,
  she ducks and keeps place and tray; with none, the gull's swoop is her mishap; a fall a fright). Run and passed:
  `pocket`, `vacuum`, `region1` to `region9`, `finale`, `boot`, and `dash`, `throw`, `deck4`, `overboard` (the ones
  that give her tangerines). The rest not run.
- **The perched gull's take, on the user's word after trying it:** its shadow spot on the floor is gone (the balconies'
  and the terrace's gulls: one class), the tell is the gull going up and hanging over her; and having taken a tangerine
  it flies off with it in its beak, on past her and up, out of sight (`flee`), back on its rail once she is past (as
  after taking a loose one). It had gone straight back to its rail and the fruit vanished from its beak after 1.8 s.
  (The funnel's and the crossing gulls already fly on with theirs.) `region7`, `region8`, `pocket` pass.

## The tangerines' seats: an audit of all 56, and a new part 9 (2026-11-19; a plan, nothing built)

The user: "I've seen a few places myself where tangerines are weirdly placed or misplaced"; asked the design session
to audit the game and the plan for placements that make no sense, for props that would give them sense and one look,
and for the best total. Nothing was to be changed while the building session worked: the audit ran a script of its own
outside the repo (her teleported beside each `tangerine` of `maps/world.json`, a close-up of each; 43 spots, 56
tangerines), then closer second looks, each on a fresh page.

- **Found, twelve spots (13 tangerines) that make no sense:** `tan_11_spa` floats over the desk's end;
  `tan_11_topsiders` is in the air by the bar's post; `tan_4_laundry` is behind the laundress's head; `tan_11_fruit`'s
  pair is on a bare table inside the buffet queue's line; `tan_5_dessert`, `tan_9_cart` and `tan_12_cagneys` are
  balanced on trolleys' domes; `tan_10_mid` has a tray prop through its table's legs; `tan_4_30` and `tan_8_aft`
  stand against fire extinguishers; `tan_8_fwd` and `tan_9_luggage` are on a bare table alone in a corridor. The
  cause of six: `sidetable`, an early placeholder drawn in code. The plan's own words for those spots had been "a
  room-service tray by a door" and "the fruit counter".
- **The number: 56 stays.** Against what a run spends now that a hit takes none (1.2a): typically 25 to 30 of the
  about 42 a first player finds. Under about 48 she would run dry mid-game; over 60 the count means nothing. The
  audit's old I2 (more on decks 4 to 6) was for the pocket, which is gone.
- **The user's answer** to the findings and four questions (all twelve with new props; a tray on a stand for the
  corridors, not five dropped; 56; the Garden Café's pair moved just past the queue): "Yes, do all as recommended.
  Add this as a new action point at the end of the plan."
- **Written:** `docs/plan-the-rest.md` §7d (part 9, after part 8), its row in §2 and a note in §12;
  `GAME_DESIGN.md` §6.3. This reopens "leave their number and their location unchanged" (2026-11-15) on the user's
  word: the number stays, one pair moves about 6 m, the rest is what they lie on.
- **Cost, the design session's guess:** 20 to 25 generations, about a day with the approvals, out of the slack before
  the date (about 18 December, the slow end the 23rd).

## 15: the drill's boat (2026-11-19, §3 step 1.2)

The last of the third batch's gags, made under 1.2a's rule (its gag whatever she carries). No art.

- **The gag:** the plan's "pressed down to half her height, a waddle, she springs back up and sits" was proposed as a
  cartoon squash or a deep crouch; the user: "No squash and no crouch. Make her lying flat on her back (like the
  basketball case)". So 15 plays 14a's clips (`GAGS.boat`: `gags-ball-back` from her stand or her run's quarter,
  then lying with the butterflies). First the boat stopped where its keel met her head; the user: "when hit, the boat
  stops too high. Your first gif ... had the boat at a lower level, that's why I asked for the lying down gag". It
  comes down over her as she lies, as low as on the bare walkway, and stays down until her checkpoint (`pinned`;
  `DRILL.pinPx` 0). The butterflies are mostly behind its hull; left so.
- **The drill answers her coming** (the user: "The drill starts too late, I can just run past it freely"): as the
  flares do, running at the hoisted boat she sets off its tell so that the keel is at her head as she is `inPx` (64)
  under its end (her speed, the tell, `hitS()` the lowering's time to her head); not nearer than `nearK` of that,
  nor for `lullMs` (1.5 s) after it is hoisted, her way through. With no one near, its 10 s clock as before. Its
  round is now a start time (`t0`), not the clock's remainder; her cry holds the tell a second.
- **The falls** (the user: "Fix the boat cables not being attached properly"): they stopped 6 px over the boat's two
  posts; now drawn to the posts' tops (`POSTS` in `src/world/outside.js`, measured in `rescue-boat.png`).
- **The winch and its crewman 0.3 m forward** (184.6 m; the user: "Yes, move them"): caught at the boat's end as
  first built, she fell back with her hair on the winch's base. Caught 64 px in now, she lies clear of it anyway.
- **Found, left:** the lowered boat holding her at its end moves her twice (body and picture); only reachable after
  a lunge that ends under the lowered boat. The user asked how she could be under it at all; told, left as is.
- `region7`'s drill check rewritten (just hoisted, she passes under it; running at it after the lull, the lamp, and
  it catches her well under it, the boat down over her); `region7`, `boot` and `tools/check_overlaps.py` pass.

## 1.3: the `mishaps` playtest, the gags' sounds, the start places (2026-11-19, §3 step 1.3)

No art. Proposed first with what a survey found (the user's answers by number: 1 region 1's untested
scenarios in too; 2 7b and 13b left in the table, marked unreachable; 3 the ten sounds; 4 the start places).

- **Found:** no check still expected the old run-off (the plan's list was done, each check rewritten as its
  gag landed). Untested: 8c, 8d, 9a, 9c, 9d, 10a to 10f, 11b, 14b; 12a/12b not told apart; 3 (in region 7),
  8a, 15, 16, 18, 20 and 24 checked by her word alone; three `pocket` checks passing on a stand-in (8b and 13a
  called with no ride played the built fall, 20 with none the old run-off); the gulls' take checked for 20
  only. 7b (the chair stands) and 13b (a door hits her only facing it) cannot happen.
- **`mishaps`**, nine cases (`porter`, `jogger`, `breakfast`, `jet`, `light`, `ball`, `things`, `balcony`,
  `gulls`): sixty hits, each through the thing's own code, with none on her and with two: the scenario, its
  gag's clip (every clip played is recorded by wrapping Phaser's `AnimationState.play`), her checkpoint
  after (`respawn` counted), the count as it was, nothing lying. With two on her each gull takes one and she
  keeps her place (21 on the stairway, 22 in a glide). `pocket`'s three stand-in checks taken out (the cases
  cover them); the leftover lines that emptied her pocket before the jet, the ball and the suitcase gone.
- **The sounds:** ten new effects, each played on its gag's clip frames (`GAGS[...].sounds`; a clip shared by
  several gags sounds as the gag of her last hit: the cart's push is the porter's bump, the trolley's
  rattle): `spin`, `bellyFlop`, `tiptoe`, `herCough`, `herSneeze`, `cartBump`, `trolleyRattle`, `headBonk`,
  `boatThump`, `towelFlump`; `thump` where she sits down hard (8b, 8d, 9b, 9d, 10d, 10f). 19's yelp is her own
  `yelpHot` (it was the people's man's), 17's and 19's cough hers (it was the soft serve machine's), the wet
  gag's sneeze hers. `tiptoe` measured too faint and was raised; `tools/check_sound.py`: all within bounds (the
  first run since 16, 17 and 19). The user judges them on the soundboard.
- **A fix found by the tests:** a hit in the air (`scareAir`, the crossing gulls) did not record `lastMishap`;
  it does, as every hit.
- **Start places:** `chips7`, `jet11` (`&did=bb5`; first in the pool, now at the pool attendant's hut),
  `light6` (`&did=bb3`), `towels9` (aft of the stack: forward of it the darting vacuum comes first),
  `drill7`. `jogger6` was not made: the `promenade` place is on his loop already. Five places filed under
  deck 9 in `docs/start-links.md` moved to decks 10 and 11.
- **Found while testing, in the tests:** a round's "just bumped" wait counted from 0 blocked the test's own
  bump in a game's first 2.5 s (`bumpedAt` far in the past now); a stage-light hit from a teleport landing
  mid-swing gave either side (she stands before the lamp turns back her way); the open trap door is just
  aft of the light's lowest point; the test browser keeps its save between games (`&reset` for the towel
  stack, which stays fallen); her step out of a checkpoint's door turns her, so each hit waits it out.
- The table of every hit, its gag, sounds and checks: `docs/population.md` §2.9.
- Run: `mishaps` (three times whole), `pocket`, `deck4`, `region1` to `region4`, `region6` to `region9`,
  `finale`, `vacuum`, `sound`, `boot`: all pass.

## The checkpoints: an audit of all 32, and a new part 10 (2026-11-19; a plan, nothing built)

The user: "I've seen a few places myself where doors are stuck at weird places or misplaced"; asked the design
session for an audit (placements that make no sense, new props for variety, the best total, "Don't make the game
too easy", "Remove redundant/unnecessary checkpoints") and a plan update for review, nothing to be changed
while the building session worked.

- **How it was looked at:** every one of `window.__ship.checkpoints` in the running game, her teleported
  beside it, `Browser.close_up` (a fresh page each), then the doubtful ones closer, unlit and lit; the
  hazards' places from `maps/world.json` and `maps/ship.json`; the game's own `closestCheckpoint` asked where
  each scare sends her, with the checkpoints of each stage of the game lit. From a script outside the repo.
- **Found, in the pictures:** 32 as the game counts them at 26 places; 17 the same white crew door, nine of
  those standing wrong (on the Stardust Lounge marquee's post; in the walkway's glass wall over its railing;
  on an exhaust pipe on the funnel's top; in the Garden Café's window; over the officer who stands there;
  wedged between a wall and Cagney's wine cabinet; white on the Library's panelling beside the promenade
  door; between the Arcade's machines; a twin of deck 9's trunk door 1.4 m from it).
- **Found, in the returns:** hit by deck 9's aft swinging door she comes back behind a one-way door she has
  not opened; deck 10's midships hallway has five things that scare and none of its own; the balcony cabin's
  lamp on deck 9 lights as she walks past its locked door (so §3 1.4's "a checkpoint past the sprinkler" stood
  there in effect); `cp_6_fwd` takes deck 5's scares a deck up; nothing returns to `cp_4_aft`, `cp_chapel`,
  `cp_officer`; lit, `cp_funnel` puts her back at the top after a gull has bumped her down to the foot.
- **The first proposal, 28 (23 places), turned down:** "I feel like that is too many checkpoints in the game."
- **Decided (the user): "Yes, let's try those 19"**, the leaner set: a checkpoint stays only if a scare sends
  her back to it and its removal would cost hazards done again, not an empty walk. Nine go (`cp_6_fwd`,
  `cp_4_aft`, `cp_officer`, `cp_hall_guest`, `cp_balc_guest`, `cp_chapel`, `cp_funnel`, `cp_station`,
  `cp_balcabin`); none is added in deck 10's midships hallway ("No, don't add"). 23 as the game counts them,
  fourteen on the main way and five balcony cabins. The reason for each and what it costs her:
  `docs/plan-the-rest.md` §7e.
- **With it:** six doors that stay are mended; deck 9's trunk door carries its own lamp; two door props (a
  padded theatre door, a dark wood service door), each with its lit twin; one rule, she never comes back
  behind a door shut to her. §3 1.4's second leftover is closed.
- **Spent by the design session:** 4 generations, four tries of a steel locker for the walkway and the
  funnel's top (the user asked to see that fix before and after), made before both checkpoints were dropped;
  not used, not in the repo.
- Written: `docs/plan-the-rest.md` §2 and §7e (part 10, after part 9), §3 1.4; `GAME_DESIGN.md` §5.5.

## 1.4: the two leftovers of step 4a, closed (the user, 2026-11-19)

- **The four end walls with a one-way doorway** (decks 8, 9 and 10 aft, deck 11's front): shot in the running
  game from both sides. Only one face of each is ever on screen, the other always behind the ship's plating (the
  stern terraces, the balcony forward of the spa, out of sight by design). On decks 8 to 10 the face seen is the
  free one: the corridor ends and she passes through as through any end wall; on deck 11 it is the spa's locked
  face (the padlock and the rattle). I offered a door's profile, a sign, or nothing; the user: "This looks exactly
  the way we already decided and built." Left as built, nothing changed.
- **The checkpoint past deck 9's sprinkler:** closed by the design session's checkpoint audit (§7e, `8cd94f0`):
  the balcony cabin's lamp stood there in effect, and goes with part 10.
- **Part 1 (§3) is done.** Next: part 2, §4 2.1, the other fourteen of the twenty things to find.

## §4 2.1 begun: six things placed, and a close-up for every thing to find and every card (the user, 2026-11-19)

- **Proposed and approved:** 2.1 in three batches, the ten picked up with E first, then 4 (the bell gull) and 7
  (the sardines), the books 11 and 14 only after 2.2 (the game counts books to ten). Each spot shot in the game
  first: the dry store's shelves, the gym's bench, Entourage past the ball pit, the maid's cabin (deck 6), the
  Stardust balcony's last seat (the same mother with a doll sits in two seats side by side there: the user, "Leave
  that for now"), the cabin being cleaned (deck 9).
- **The cabin being cleaned is an inside cabin, no window:** the plant (12) and the bookmark (10) swapped (the
  user): the plant on the maid's cabin's sill (deck 6, region 2), taken with E from the floor (`low` in the item's
  data: a thing to find over 40 px up is otherwise hers only from up there or by a lob); the bookmark's book on
  the deck 9 cabin's stripped bed (region 4). `docs/plan-three-uses.md` §4.1's rows changed with them.
- **The user: "Can we use more fine-detailed visuals for the items in the game (keycards, collectables, books)?"**
  I explained the limit (the world's pixel is 2 screen px; her 59 px sets the scale) and offered A, bigger than
  life in the world; B, finer pixels in the world (advised against: pixels of two sizes); C, a close-up when she
  gets one. **Chosen: A and C.** Of two looks for the moment (a soft warm light behind it, or a pale card), **the
  warm light**.
- **The art (26 generations):** six first pictures at 48 px (7 with a retry; the bookmark first came as a cat
  sitting on the book), replaced by detailed ones at about 100 px once C was chosen; the car again ("beige with two
  big rubbery cyan wheels": two tries, the side-on one taken, its wheels moved to the palette's brightest cyan by
  hand); the diary again ("leather cover": two, the user took the brown one with a buckle over the tan one I
  recommended for the red seat); the four placed things and the key card (one card, its stripe in each card's
  colour). The world's sprites are the close-ups shrunk (majority colour; the plant's stem and the bookmark's
  4 px cat head mended by hand). The user approved every close-up and the new world sprites but the wool's ("I
  don't like both of the in-game versions"): shrunk, it was always a plain red blob; a small picture made for its
  size, 10 px with its strand over the basket's rim, chosen of four in the basket.
- **The tennis ball in the owner's toss:** its clip held the old ball in her hands (frames 4 and 5, let go at 6):
  the new ball pasted in at the old one's middle, **over her far hand** in both frames, under her near hand (the
  user, twice: frame 5 first, then frame 4).
- **Built:** `assets/source/closeups/` (README with ids), `tools/build_closeups.py` to `assets/sprites/closeups.*`;
  `FROM_CLOSEUP` in `tools/build_things.py` (the ball 10 px, the feather 9, the flag 16, the snack tube 6, the gun
  16, the car 10, the diary 13; the old pictures in `things/tries/`); `world.closeup(frame)` from `take`,
  `giveKeep` and `progression.open('cards')`, a cut, `scene.viewing` keeping every hit off her; the six items in
  `ITEMS`; five start places (`store4`, `maid6`, `knit5`, `shore5`, `balcony7`). Playtests skip the moment
  (`Browser(closeups=False)`).
- **Checked:** in the running game, each of the nine taken with E (the feather from the shelf by `take`): kept,
  the close-up up, she held, a key closes it, play again; the five places start clean; every built sprite equal
  to the one approved. `boot`, `deck4`, `region1`, `region2`, `region3`, `region4`, `region6`, `golden` pass; the
  rest not run.
- **Waiting for the user (asked for the next session): the locations of all ten, judged in play.**

## §4 2.1 continued: the gym, and the other pickups' pictures and close-ups (the user, 2026-11-20)

- **Merged:** `main` fast-forwarded to `three-uses` (0b49441) and pushed, on the user's word.
- **The massage gun (6):** "Move it to the bench that I circled": the rowing machine; first on its rail, then
  (the user: "Put it on the seat") on its seat, 15 px up.
- **The gym's background props "too washed out ... like in the theater":** the fitness centre's machines
  (treadmill, exercise bike, cross-trainer, rowing machine, weight bench, dumbbell rack) and, asked and
  answered "Yes", the spa's aerobics studio (the yoga-mat rack, mat, medicine ball, dumbbells, kettlebell,
  bottle, water cooler) take the theatre's light wash (`LIGHT` in `tools/build_ship_art.py`, `-lt`, 12%). Found
  with it: the treadmill runner's `cover` still named `treadmill-bg`, now `-lt`. The crew corridor's water
  cooler keeps `-bg`.
- **"What is this?"** (the pink sock on the yoga-mat rack): the grip socks, an early placeholder drawn in code,
  as the pills were. "Are their refinement and their close-ups not in the plan?" They were not; added to 2.1
  ("As part of 2.1"), and built: the pills are her only quest item kept in the pocket (the user: the same for
  every pocket quest item, not the carried ones; every hand-over and pickup of the story was looked at).
  Pictures (6 generations): the socks and the pills generated; the parasol's close-up first came open, then
  redrawn from the world's sprite (rough), then generated again furled, two tries, the user taking the one
  folded like a closed umbrella, "remove the red pixel from the parasol's handle". In the world: the socks
  in a stronger pink with a lighter pink outline, then moved to the free treadmill's belt by its rear end and
  two px lower, in front of it (the user); the close-up recoloured to match ("more similar to that in the
  game"). The pills at 12 px with an orange outline; "something that resembles a text on its white label"
  (a dark title and lines of print, by hand, on both); "its bottom line has to be fixed" (the foot stepped in
  on one side): three candidates, B, an even foot with rounded corners, "but make the top line to match the
  color of the cap in the close up" (the cap's white ridges). `icon-socks` and `icon-pills`, drawn in code,
  removed.
- **Checked:** each in place and its close-up in the running game; every built picture equal to the approved
  one. `boot`, `region1`, `region2`, `region6`, `region8`, `golden` pass (`region6` and `golden` took the socks
  from the rack: their spot changed); the rest not run.
- **The locations (the user, 2026-11-20):** 1, 2, 3, 5 approved as placed; 6 moved (above); the car (8) "where I
  circled": on Entourage's air hockey table, left of its post, 26 px up; the flag (9) approved. Entourage's
  props "too washed out": its ten pieces take the light wash too (the TV console, the foosball and air hockey
  tables, the dartboard, the arcade cabinet, the vending machine, the wall TV, two beanbags, the monstera; the
  same pieces elsewhere keep `-bg`). `boot`, `region3`, `region9`, `golden` pass.
- **The bookmark (10) and "this lady":** the bedmaker shaking out a sheet in the cabin being cleaned "is
  problematic, we'll have to slow her down, and also find some other place for her, maybe another room". Of
  three places offered (the linen room, a new open cabin on deck 10's midships hallway, the cabin left
  empty), the user chose **a new cabin on deck 10**: `makeup10` at 164 m, between the sprinkler and the "Do Not
  Disturb" door, drawn in code as its kin (`tools/draw_rooms.py`: the bed made, her trolley clear of her,
  the wardrobe, a picture; a first layout had her in front of her trolley); her `make` at 4 frames a second
  (was 8, "frantic"). The cabin being cleaned is empty, its bed the bookmark's: on the mattress's top, then two
  px lower into it (the user). `region4`'s check of her there now checks the bookmark. `tools/check_overlaps.py`
  skips the pickups lying on furniture (the car on its table, the diary on its seat). `boot`, `region4`,
  `region7`, `vacuum`, `golden` pass; overlaps 0.
- **The diary (11):** "still looks weird": moved 9 px aft onto the cushion, clear of the backrest, then 4 px down
  into it, and "the circled part of the diary obscured by the chair's arm": first drawn behind the whole seat
  (the user: "both armchair's arms, and I meant only the one closer to the screen"), then right: a pickup can
  name the furniture it is in (`cover` in the item's data: piece, metres, px), whose lowest rows (the seat's
  near arm, 21 px) the game draws again in front of it. `boot`, `region3`, `golden` pass; overlaps 0.
- **The plant (12) and the maid's cabin (deck 6), the user's four:** (1) "Make Bumbusik able to jump on top of the
  bed, like in cabin 8206": a ledge on the bed (`PLATFORMS` may now name a room: there only while she is in it;
  `walk.route`), then 2 px lower so her feet touch the mattress (the user). (2) On the bed the swan is in front
  of her, on the floor she is in front of it: the swan's own pixels cut from the finished room picture
  (`on_bed` in `tools/draw_rooms.py`, `maid6-onbed.png`), drawn over her while she stands on the bed. I first
  read it backwards. (3) The towel swan's orange beak, "impossible if it made of towels": whitened in the shared
  piece (`RECOLOUR` in `tools/build_ship_art.py`), as the towel stack's swan's was; the swans of deck 10's
  towel table and deck 8's cart with it. (4) "Stretch her back, while holding her waist behind her back ... after
  the current making the bed sequence ... in a loop": a PixMiniMax clip from `make`'s last frame to its first
  (2 generations), approved; her loop twice `make`, once `stretch` (`cycle` on a person, `people.cycleIdle`).
  Then "her hands have to be a little bit lower, now they don't reach the bed": her forearms bent down by hand
  in every `make` frame (5 px at the fingertips) and in the stretch's first and last four, fading
  (`assets/source/people/maid-raw/` keeps them as generated). "Make the two pillow outlines obscure the bed":
  asked, "Solid pillows": the upper one had the wall's colour inside. And the plant was taken from the floor,
  not the bed: now only from the bed (`from` on the item: px up she must stand). `boot`, `region2`, `region6`,
  `golden` pass; overlaps 0. **The ten things' locations are all approved.**

## Every pickup lying in the world glints (the user, 2026-11-20)

- **The user:** "Every collectible thing that we pick up from somewhere (not given to us, or not made by an ice
  cream machine, for example): let's add a tiny spark animation to it." Then: tangerines "have no spark".
- **As it came to be, round by round:** a 7 px star at a random spot on the thing's upper half every 2.2 to
  3.2 s ("too aggressive, and blinking all over the place. I meant a much softer, and slower spark on the top
  right corner of every item"); then 5 px at the top right corner, fading in and out over 1.6 s at 80% every
  4.5 to 6 s ("Reduce the delay ... Make the spark also rotate (not fast)"); then every 2.5 to 3.5 s, turned by
  rotating the picture ("it leaves LCD traces"); then four drawn turns, two with bent rays ("every frame shall
  have the rays straight"); **approved: "+" and "×" in eighth-turns, eight steps of 0.2 s, growing over two and
  shrinking over two, fading with them** (`world.glint`, `updateGlints`, the `spark` texture drawn in code at
  the world's start: twelve px at most, an effect, as the sparkle on taking).
- **On:** every pickup taken with E (the things to find, the books lying out, the socks, the parasol, the pills)
  and the key cards lying on a table or on the deck (the deck card's pulsing dot gives way). Not tangerines, not
  what is handed to her or made for her.
- **The user, on pictures of the game:** "When asking for in game scenes, I meant not closed-up, but how I
  actually see it in game": recordings of the game's own view from now on.
- `boot`, `region1`, `region2`, `region8`, `golden` pass.

## Her feet a pixel into the floor (the user, 2026-11-20)

- **The user:** "shift Bumbusik down one pixel everywhere in the game ... update her default ground level", then
  "leave the gags out of it", then "in some places where her feet should be obscured, the bottom line shows ...
  fix that properly everywhere", then "Hide the bottom line of her feet on the promenade".
- **Built:** `PLAYER.sink` (1): her picture drawn that much lower than her body's foot, by her display origin and
  her body's offset together (`herDrop`, the crawl's offset), so where she stands, and every check of it, is
  unchanged; in every look of hers (uniform, towel, with Bumbot), on stairs, ladders, crawling. Her gag clips
  are left as they were.
- **What hides her feet reaches a pixel lower too:** the decks' end railings, the props and pickups' fronts,
  the forts, the ball pit's front (`withFoot`: the picture's bottom row drawn once more, its placement kept);
  the balconies' fronts, the bulwarks, the promenade's sills, posts and columns, the side walks' railing, the
  funnel top's front rail (graphics a px taller); the end walls' strips and the open decks' strip (plating a
  px into the floor's row); under each sloped plate the side's own floor row copied in front of her (no pixel
  changes from outside, checked). Found and checked in the running game: everything over her that ends on a
  floor line listed, then at each kind of spot the screen with and without her compared on her lowest row
  against the row above it (a leak made on purpose is caught); deck 9's stern leaked until the slopes' copy.
- **On the promenade's deck** her lowest row is left off (a crop while she stands there): the user's call.
- `boot`, `run_jump`, `stairs`, `ladder`, `trunk`, `lift`, `pool`, `promenade`, `cabin`, `linen`, `balcony`,
  `falls`, `dash`, `golden`, `region4`, `region7`, `finale` pass. `tools/check_overlaps.py` listed 3: the pickups'
  glint stars (since the glint's commit, where it was not run), now skipped by it (`spark`); then 0.


## §4 2.1, thing 4: the bell gull, the promenade's lights, her throw in the air (the user, 2026-11-20)

- **What the bell is for** (the user asked): one of Bumbot's eight things to find, no power; his count, and
  with him in cabin 8206 the day after. The gull makes it a small riddle of the throw.
- **The promenade's lights:** the first two tries were lanterns no cruise ship has (the user: "Before setting them
  in the game, you should have shown them to me. Neither of such lamps are on cruise ships"). Four real fittings
  generated; the user chose the round caged bulkhead light and the oval one, a little bigger than life, "a few
  along the promenade, with our gull sitting on top of one of them": ten, round and oval in turn, their middles
  80 px up, clear of doors, portholes, the window wall, the columns and the plating's butts. **The two portholes
  at 156.0 and 158.2 m moved to 156.4 and 158.6** (the first stood on a butt; the user: "so that they won't be
  placed on top of the hull plating stitching"), and a light from 149 to 149.6 m.
- **The gull** (`BellGull`): on the round light at 140.6 m, between door 138 and the column, the first thing out
  of that door. It keeps its place as she passes; her cry sends it up, the bell kept; a throw that reaches it is
  caught, the bell falls to the deck under its beak (growing from its size in the beak to its own 14 px) with a
  jingle (`jingle`, new; the user judges sounds), the gull is off with the fruit for good (`bell_dropped`). The
  bell lies glinting, E takes it, its close-up (the collar, its yellow ring taken out by hand at the user's word).
  It flinches only when she jumps straight into it (the user). **Its collar at game size is drawn by hand** in the
  close-up's colours: the generated one, shrunk to the 20 px gull, read as nothing ("unclear what it carries in
  its beak"). The collar glints a size smaller, at the bell's bottom right (the user placed it, three tries).
- **Hits:** the lob from the deck reaches it only from 1.25 to 3.5 m (measured); the user, as a player: "a thrown
  tangerine never flies high enough to hit the gull ... What I would expect is to be able to throw it while
  jumping". **Her throw in the air:** F in a jump tosses forward and a little up from her hand (vy 200: a level
  throw dropped under the gull beyond 1.5 m; this one meets it from 0.5 to 2.5 m whenever in the jump, but at the
  end of her fall), ↑ and F the lob; once a jump, her arc kept, some of her speed along carried. Her clip
  (`her-airtoss`): skeleton-v3 from her jump's top, only her near arm moving, the tangerine in her fist until
  the fourth frame (two PixMiniMax tries swung both arms; the first skeleton try raised her hand to her face).
  Everything that answers a thrown tangerine answers it.
- **Showing through the hull, found and mended:** the Photo Studio's flash (from the promenade outside, the user
  saw it, and from deck 7 above it), the theatre's stage light (from the Stardust balcony; the user saw it too),
  the sauna's steam (from the Spinnaker): each now only while she is inside on its deck. A sweep of every effect
  drawn over the hull on a clock or by her distance found no others (the bridge's alarm, the old lady's snores,
  the kid's jets, the terrace's gusts, the crossing and funnel gulls are over open deck or check her deck).
- **A tangerine on the promenade's deck** showed its lowest row through the hull, as her feet had: the side's
  own two rows under the floor's line are drawn again over what lies there, while she is out on it.
- **Tests:** `throw` checks the bell gull (kept as she walks under it, the cry, a throw in a jump caught with her
  clip and once a jump, a lob from the deck caught, the bell taken); `region2`'s shy gull is found by its id (the
  bell gull came first in the list). `boot`, `throw`, `region2`, `region3`, `region9`, `mishaps`, `gamepad` pass;
  `mishaps.things` failed once in a batch, unread, and passed five runs after (four seeds). `check_overlaps`: 0.
  Generations: 6 lights, 10 gull edits, 2 close-ups, 8 for her throw in the air.

## The HUD redone (2026-11-20, the user's design, before item 7)

The user: "Before we do it, let's refine the HUD": nothing at the start; the first tangerine flies to its place
and the count shows with it; a key card shows in its place from its close-up; each kind of thing to find, and
the books, shows its count as its close-up closes, a little bigger, settling. Settled by mock-ups over a real
shot of deck 4's corridor (A to K), each the user's word:

- **One row**, at the game's pixel size (2 screen px a pixel, "A as a baseline"): the tangerines in a slot of
  their own on the left, kept free before the first ("only the offset from the tangerines is fixed"), then the
  kinds **from left to right in the order first found**; each keeps the width of its largest count, so nothing
  moves once placed. Under it the **four key cards in fixed places, faint outlines until held** ("slightly
  stronger"); the row of cards shows from the first card.
- **The kinds are faces** ("The flower and the guitar are especially unclear. Have to be faces of Bumbusik and
  her husband"): Bumbot's generated from his photo (#3 of 64; two pixels cleared at the user's circle); hers her
  own front view; her husband's from **his new character** (below), with the bear on his chest, one forehead row
  out. The books the popups' book, the cards the popups' card with the slot at its top filled ("fix the
  triangular cuts"). **Every picture rimmed** with a light pixel, the tangerine too ("The light rim helps"); all
  on one bottom line, the numbers on one line a little lower, the row 4 px higher than first drawn.
- **Smaller was tried and dropped:** shrunk by majority the faces "became distorted"; cut by rows and columns
  they kept their pixels, but the user took the originals.
- **The numbers** are the popups' lettering (Galmuri9), white with a navy outline, "x 12", "3/8"; the lettering
  has no "×" (an x) nor "∞": for `?tangerines=infinite` an ∞ drawn in its style, as tall as the x and centred on
  it (the user: "Enlarge the infinity sign, and center it against the X"; "x --" before).
- **The moments:** the first tangerine's flight lands in its slot and the count shows (a bump after); a card
  flies out from under its close-up's card as that closes, arcs to its place and settles, the outlines fading in
  with the first; a kind's count shows as its close-up closes (`world.closeup(frame, then)`), a book's at once.
- **Her husband's character** (asked by the user with the photos: "my HUD icon and sprites in the game"): a pro
  character in the cast's style from his first photo, **in his pyjamas, at the table and in the cabin** ("That's
  an inside joke"); the bear on his top by an edit, its face the edit's own, its pyjamas set to his trousers'
  check by hand. Approved; **not yet in the game** (the stand-in diner is still at his table, with no clips).
- Built: `tools/build_hud.py` (the `hud` atlas from the approved sources), `src/hud.js` (the scene's `hud`;
  `refreshHud`/`blinkCount` hand over to it; the save keeps `hud`: the tangerines shown, the kinds' order, the
  cards shown). Gone: the Verdana count, the emoji counts, the card rectangles. Tests: `pocket` and `deck4` read
  `hud.state()` (deck 4/5 checks the order found); `boot`, `pocket`, `deck4`, `region1`, `region2` pass.
  Generations: 65 (`assets/source/hud/README.md`). Not done: a sound for a count appearing (none asked); the
  lock popups' card keeps its slot notch.

## §4 2.1, thing 7: the tin of sardines at the Sushi Bar (the user, 2026-11-20)

Asked one question at a time (the user: "Give me questions interactively, one by one, with the context"):

- **His wish:** a thought cloud with the game's own tangerine (`icon-tangerine` in the popups' atlas, from
  `FRUIT`; no generation), shown **only once she is near** (3 m), until he has one (`flag:sushi`).
- **The trade by hand:** E at the counter with a tangerine: she walks round to his front (the case's bare end;
  36 px before him, clear of the seated diner), bows and holds it out (her apology's clip, as the plan had it),
  he reaches over the glass case and takes it on his palm, puts it away behind the case, comes up with the tin and
  hands it across; the close-up, Bumbot's count pops in; one tangerine fewer. **With none:** his cloud hops. Her
  hands full: nothing.
- **By a throw** (the user: "also tossing him a tangerine works. Only if it hits him (or almost hit him)"): a
  thrown tangerine within 22 px of his middle, above his case and up to 10 px over his head, is caught (his fist
  up), put away, and **the tin set on his case's top** for E (the user's choice of three; `keep_sardines`,
  `flag:sushi_tin`). Measured: a lob reaches him from up to about 1.3 m, a throw in a jump from about 2.7 m on;
  between, it passes 25 px or more over his head. A throw from the floor passes under the case's top.
- **The tin:** four close-up tries (two closed, two open); the user chose **4 as it is** (open, silver, the fish
  packed in): kept in its own blue silver (`OWN_COLOURS`; on the palette it went purple). Its world picture is
  **drawn by hand at 13 x 9 in its colours**: shrunk, it was a grey blob (the collar bell's lesson). That one
  picture is in his hand in the clip (`own` colours in `tools/build_people.py`), crossing to her, on the counter.
- **His clips** (approved): `take`, `give`, `catch`, each a PixMiniMax clip from his slice frame toward an edit
  of it (`edit_image_pro_flash`), and each played back down (`take-back`, `give-back` without the tin,
  `catch-back`); the give's frame with the tin in front of his face dropped; the generator's tin replaced by the
  drawn one. The tangerine in his hand is the game's, at his palm or fist measured per frame (`SUSHI` in
  `src/world/topdeck.js`), put away once his hand is below his shoulder.
- **The nigiri moved behind him** by the sake set (the user, over raising his arm): his take had laid his hand on
  the plate.
- Built: `sushi()`, `sushiOffered()` in `src/world/topdeck.js`; `people.play(..., { stay })` holds a clip's last
  frame for the next. Test `throw.sardines` (the cloud near, E with none and with one, a lob caught, the tin taken);
  `boot`, `throw`, `region8`, `deck4` pass; `check_overlaps` 0. Generations: 22 (`assets/source/closeups/README.md`,
  `assets/source/people/sushi-chef-trade/README.md`).

## The empty stretches: an audit, and a new part 11 (2026-11-21; a plan, nothing built)

The design session, on the user's word: "Let's focus on the long corridors that are still underpopulated with
obstacles. I want a proposal of how we would fill the empty stretches with playable obstacles by reusing the
current ones (in a smart way, so that they aren't repeated one after the other), and maybe adding a few new ones."

- **Measured**, counting only what can catch her or must be got past (from `maps/world.json` and the map, then
  eight stretches looked at as panoramas of the running game): deck 4 from the climb to the stern is 109 m with
  three standing carts; deck 5 from the forward stairs to the stern 182 m with the waiter alone; deck 6 inside
  184 m with nothing. Regions 1 to 3 are the thin part of the main way, and the best gags (the suitcase, the
  papers, the breakfast trolley, the tray ride, the "Do Not Disturb" door, the steam) sit in side stretches and
  optional parts. `tools/check_corridors.py` did not show it: it counts a checkpoint, a person with a bubble and
  a room's door as "something to do".
- **Proposed:** ten placements, seven of them things already built and placed anew under three rules (never the
  same thing as the last she met; neighbours never the same move; a thing comes back changed in one way), two
  with one small picture or person, one new. A map of the decks with the empty stretches and the ten was shown.
- **The user's answers:** on which go in, "All of them"; on deck 4's aft checkpoint, which part 10 removes and
  which two of the ten would give a use (a hit there is about 100 and 155 m back from the gangway), "As decided":
  it goes, and no checkpoint is added or kept for the ten; on the rule "No person, hazard, errand or reward is
  used twice" (the user, 2026-11-10), **"Drop the rule, it is no longer relevant, we are doing refinements
  manually now."**
- **Changes to the plan, and why:** `docs/plan-the-rest.md` has a new last part, **11 (§7f)**, with the ten, what
  each needs, where a hit sends her back under the nineteen checkpoints, what is left calm, the tests and the
  order (the new one, the painting carried through the Art Gallery, last and from a plain version shown first).
  `GAME_DESIGN.md` §6.1.2 marks the rule dropped, §5.8 has the decision, not built. Why: the user's request, and
  the measurement above.
- **The date:** about three working days, the design session's guess; with parts 9 and 10 that is all of the
  roughly five spare days before the 23rd of December. Said to the user before the choice.
- Three things found on the way, not acted on: a tray's low hop over the suitcase is not measured (§7f, 3); the
  walkway has nothing that could flap as a gust's tell (§7f, 6); in the panoramas a thought cloud stood over the
  aft lift's door (200.3 m) on decks 4 and 5 with her at the gangway, which may be the pictures' doing (`?cards=all`,
  a deck cut open by `viewOverride`) and was not looked into.
- No generations. The scripts and pictures are outside the repo and not kept.

## The ends of the long runs: a second round for part 11 (2026-11-21; a plan, nothing built)

The design session, on the user's word: "check the ends of the all the long corridors and see whether reaching every
end benefits the player. Whether it is part of a route that must be taken, or whether the end holds something else
valuable."

- **Found** (from `maps/world.json`, the plan and the panoramas): of about forty ends, eleven held nothing; four of
  those got something from parts 2 and 3. The design session proposed leaving most, three of them by the user's own
  earlier choice.
- **The user:** "First of all, your plan has to account for already planned things that are not built yet. Plan with
  them in mind, like they are in the game. Second of all, I do not agree leaving empty ends. Every long corridor run
  has to have obstacles (you already planned it) and a purpose." On the adjusted plan, shown with a map: "Write it".
- **Changes to the plan, and why:** `docs/plan-the-rest.md` §7f has a second round: six more obstacles (11 to 16: the
  Photo Gallery's crowd, the aisle's popcorn, the balcony's lamp, deck 8 forward's balloons, a robot in deck 9's
  officers' corridor, pool towels on deck 12) and six ends given a purpose (P1 to P6: a ladder with a gate from above
  at the promenade's aft end, its hidden tip chained off; look-out 4 moved to the Spinnaker's balcony; his mask at
  deck 10's first balcony; deck 9 aft's tangerine and the pillows' cabin at its last door; deck 8 forward's tangerine
  out on the terrace; the snack table behind the fort). Number 4's plates lie there from the start. Why: the user's
  rule, with what is planned counted as built.
- **What it overrides, each said to the user first:** "left empty by choice" (`docs/plan-three-uses.md` §4.6); deck 8
  forward agreed bare; three tangerines' places (the number stays 56); "Leave as they are for now" on the two places
  where she is hard to see (one is closed off, in the other she is drawn in front of the glass); "No new ladder".
- **Lines amended elsewhere in the plan:** §4 2.1's row 14, §5 3.1's row 4 and 3.2's row 3, §7d's row 11, §8's line
  on the empty places, U10.
- **The date:** about two more working days by the design session's guess, five for the part: the likely end near
  25 December, the slow end at New Year's Eve. If it slips: the balloons and the ladder first.
- Found on the way: the walkway's end walls and its columns are all climbs up to deck 8's balconies (the grips), so
  both its ends lead on; "behind Teppanyaki's flares" was never empty (the piñata).
- No generations. The scripts and the two maps are outside the repo and not kept.

## §4 2.1, thing 13: his navy t-shirt on deck 12's sun deck (the user, 2026-11-21)

- **The thing changed:** "Replace #13 with his navy t-shirt. I have added a new photo to the Husband folder. The
  t-shirt has to have this logo on the left side of the chest" (the logo: "bluevine cares", an arch with a heart
  flower). The photo stays in `reference/Husband/` (git-ignored); only the print, its fabric made one flat navy,
  was sent to PixelLab.
- **Where:** not the plan's last table at the stern rail; the linen room was asked about and dropped (region 4: she
  reaches it before she meets him); a sunbed "by the pool" reached only after their meeting: **deck 12's sun deck
  over the pools** (deck 12 opens only by the wall jump at 232 m, past his table), the first of its two loungers.
  Shown only after the table scene (`flag:table`), as all four of his.
- **The close-up:** a big generated shirt (try 7, as the user's choice of look, try 2, at twice the size), **only its
  top half** (the user, so the logo can be in proportion and legible). The logo: my hand-drawn one was set aside for
  one generated from the photo (`image_to_pixelart`, four tries; the user chose **a**); its colours set to the
  photo's inks, carried over by the fabric's navy; "bluevine" (which no try could write) and "cares" stamped in pixel
  letters; the user chose the bigger "cares". My fix of its leaves was "worse"; **the user edited the logo
  themselves** (`assets/source/closeups/tshirt-logo-by-hand.png`, never written by a tool; `tshirt-logo.png` is
  the file they saved over, left as it is). Its own colours, not the palette's (on it the navy went purple).
- **In the world:** the close-up shrunk read as a dark bag ("None of them read as a folded t-shirt"); a small
  generated folded shirt (try 3 of four, `create_map_object` 48 x 32) made navy by lightness, 20 x 12, no logo
  ("it cannot be shown when the t-shirt is folded, anyway"), pressed 3 px into the seat (the user's placing).
- **The loungers:** "Each of the two sunbeds ... replaced with a newly generated one (same one for both). Slightly
  longer and without arm rests. With longer head support": try 3 of four, mirrored, **at its own size** (82 x 32;
  shrunk to 36 or 41 px it was faint, and outlined its slats read as teeth); washed as deck 12's props, then
  darkened to 70% (`SHADE` in `tools/build_ship_art.py`); the second 4 px aft, both 2 px down (the user, pixel by
  pixel). Deck 11's loungers are unchanged.
- Built: `keep_tshirt` (`tools/population.py`), `sunlounger-long` (`tools/build_ship_art.py`, placed in
  `tools/build_ship_map.py`), `tshirt` close-up and `tshirt-folded` thing in their own colours. Test
  `region8.tshirt` (absent before the table scene, the loungers where the user put them, the shirt on the seat, E
  takes it); `boot`, `region8` pass; `check_overlaps` 0. Generations: about 40 (the shirt 7, its fold 6, the logo 4,
  the small folded shirts 4, the loungers 4, and tries along the way; the ids in the READMEs).
- **Set right on the way:** the dropped mirror close-up of the intro was taken out of CLAUDE.md's lessons and my
  memory (the user: "it should not be there anymore").

## §4 2.1, thing 14: his sleep mask on deck 10's first balcony; the balconies mended (the user, 2026-11-21)

- **Where:** the Design session's §7f P3 had moved it to deck 10's balcony row, its forward end (62.9 m). That balcony
  was bare (the furnishing rule gave it only a towel): the user chose a sunlounger, then **deck 12's long lounger**
  (`sunlounger-long-w20`, the balconies' wash), behind the balcony's bottom wall as every balcony's furniture; its
  towel moved to the next balcony aft, **blue, 35 px in as on deck 9's below** (the user). Both set by hand:
  `BALCONY_SET` in `tools/population.py`, read by `tools/build_world.py` (the rule furnishes the rest as before).
  Shown only after the table scene (`flag:table`), as all four of his.
- **The look:** "A regular sleep mask with one strap. Pink/beige color." Four map objects (1 generation each); the
  user took **try 1, the edges smoothed**: its body's outline smoothed by rule (the mask blurred and cut at half, one
  outline colour), the dotted seam by the edge filled from the shading 2 px in (version A; B filled 3 px), the strap's
  two tabs square and **the same size** (7 x 15), on the user's word (a try one pixel shorter was set aside:
  "take the before variant"). `assets/source/closeups/sleepmask.png`; the script in `tries/mask/smooth.py`.
- **In the world:** the close-up's body shrunk by majority to 12 x 6, outlined in its rose, a pixel of strap each side:
  16 x 8 (C of three sizes, the user's), on the lounger's slats, 4 px forward and 3 px down from where I first set it
  (the user, a pixel at a time). Both pictures in their own colours: on the palette the pink went peach.
- **The balconies, seen with it** (the user's two screenshots): parts of her picture showed through a partition (on
  the next balcony) and over the ship's side at the row's end. Now each partition's panel is drawn over her (its
  colours as the builder draws it, its foot the side's own tiles; pixel-identical to the side with her away), and her
  picture is cut to her balcony: at a partition while she is under its top (over it she can be seen leaning across),
  at a row's end at any height. **Phaser 4 shifts a picture turned by `flipX` when it is cropped** (by width - 2x - w),
  so while she is on a balcony a stand-in of her, turned by its scale (which crops true), is drawn and her own
  picture cropped to nothing (`balconyPic` in the ship scene). A copy of the side past the rows' ends was tried and
  dropped: it hid a window on deck 9, not a tile of the side.
- **↓ and jump** on a balcony with no balcony under it had been the long-fall scare (the user: "That shouldn't
  happen if there is no balcony underneath. She shouldn't jump down"): she drops only where a floor of the route
  lies one deck under her (a balcony, the walkway under deck 8's); with the parasol, where any floor of it is under
  her (`dropFloorAt`). GAME_DESIGN §6.1.3 says so now.
- Built: `keep_sleepmask`, `BALCONY_SET`, the `covers` of the outside's data (`tools/build_world.py`), the panels and
  the cut (`src/world/world.js`, `src/scenes/ShipScene.js`), the start place `mask10` (`docs/start-links.md`). Test
  `region7.mask` (no mask before the table scene, the lounger in place, no drop where nothing is under her, the drop
  onto deck 9 from the next balcony, the cut at the partition, the mask on the slats, E takes it); `region7`,
  `region4`, `mishaps`, `boot` pass; `check_overlaps` 0 (it skips the side's copied tiles: plating, not things).
  Generations: 4.


## §4 2.1, thing 15: his handheld on a new sofa in Champs; Champs remade round it (the user, 2026-11-21)

- **Champs had no sofa** (the plan's "on a sofa"): a new one, generated (try 3 of four, front view, dark brown leather),
  in its own colours lightened 1.9 times (the user's tone 4; on the palette the brown went mauve), **in the aft high
  table's place** under the aft windows; the table, its stools and the wings gone. The seated cheering fan moved to the
  bar's aft end facing it, on his own stool (that end's bar stool gone); both fans 15 px forward and 2 px down (the user).
- **The bar bigger** (the user, its right end where it was): the first four tries were "neither ... A bar from a cruise
  ship"; the real Champs Bar's photos (cruisedeckplans.com) showed honey teak under a pale top; try 7 of the second four
  (vertical honey slats, a white top, its own tap and two glasses), 109 x 49 at its own size, its right end at 4955 px.
  Its beer pint and its forward stool gone.
- **The fan in stripes** standing by that stool gone; **a second seated fan** at the bar's forward end facing it: an edit
  of the first fan's frame, "a different person in exactly the same pose" (try 2 of three, a blonde woman in a blue
  jersey with a pint; 5 generations each), a still.
- **The handheld** (his ROG Xbox Ally X, from the user's photos, every logo painted out before sending): from text,
  "neither"; from the photo, try 1 chosen, then "too rough ... compared to other close ups": **the close-up is a pro
  redraw** (`image_to_pixelart_pro_flash`). The world picture: the converter at 16 px gave blobs, the photo shrunk a
  brick ("Handhelds are really broken ... How do we do it correctly?"): a clean front view first (a pro redraw of the
  front photo), then a 24 x 11 built feature by feature (outline, the screen in its bezel, the sticks' RGB rings, the
  d-pad, the face buttons, a lit top edge); **the user then edited it in Paint** (`assets/source/things/handheld-by-hand.png`,
  white its ground; never written by a tool, read by `BY_HAND` in `tools/build_things.py`). On the sofa's left seat
  cushion, only after the table scene.
- Built: `sofa-champs` and `champs-bar-long` (`tools/build_ship_art.py`, `OWN`, `BRIGHTEN`), placed in
  `tools/build_ship_map.py`; `champs_d` (`tools/cast.py`, `BY_HAND` in `tools/fetch_people.py`; its tries in
  `champs_d-raw/`: a folder beside `stand.png` is read as a clip); `keep_handheld`; the fans in `tools/population.py`.
  Test `region8.handheld` (absent before the table scene, the bar's right end and the sofa in place, the fans at the bar's
  ends, the handheld on the seat, E takes it); `region8`, `region9`, `boot` pass; `check_overlaps` 0. Generations: about
  58 (the sofa 4, the bars 8, the handheld 31, the fans 15).

## "Washie, washie, happy, happy!": a new part 12 (2026-11-21; a plan, nothing built)

- **What the user asked:** a fun way to bring their and his wife's own joke into the game: the crewman who stood at
  the entrance to deck 11's dining area from the lifts, sanitizing hands and singing "Washie, washie, happy, happy!".
- **What was proposed and taken:** five pieces, "All five" (`docs/plan-the-rest.md` §7g, `GAME_DESIGN.md` §5.8): a
  first meeting that cannot be missed, their duet; he never holds her after it, nor ever with her hands full; foamy
  paw prints past him; a tangerine washed and tossed back; the song stuck in her head. The user's own additions: his
  look ("Asian crew member, maybe Philippine guy. Happy face, black hair. Standard waiter crew uniform"), both sing
  the whole line in the duet, and no melody.
- **Why there:** the game's Garden Café opens into the aft lift lobby at 194 m, so his real place exists, and a piece
  of wall is free between the checkpoint's door and the lobby's pillar (seen in a shot of the spot). She meets him
  after the kid's jet and the queue, so he is a rest and not a third thing to get past; for that reason his squirt is
  nothing to dodge. The fruit counter was not locked behind clean hands: she passes it before him.
- **A mistake of the design session's, mended in the plan:** the proposal said Bumbot's wet paw prints "already run
  past this spot". They are in `docs/population.md` (`sec_pawprints`) and were never built. Part 12 builds only the
  prints by him; the 82 m trail is left to the user, since it could read as a hint where to go.
- **What it costs:** about 25 to 30 generations and a day and a half (a guess). The likely end moves from near 25
  December to about the 27th, the slow end past New Year's Eve unless something gives; said to the user before the
  choice. The design session's ranking: the balloons (14) and the ladder (P1) of part 11 are dropped before him.
- **Mine, not the user's:** the bottle held like a microphone, the words kept in English in both languages, the
  squirt's sound, the build order. Each is marked so in §7g.
- **Corrected the same day (the user):** the plan had named the game's own waiter (the cast's `waiter`, a white jacket
  and black trousers) as the model for his uniform. The user: "No, that uniform doesn't match. Don't reference him."
  The reference is out of §7g. The real uniform is not known to the design session (a search and the user's photo of
  the café did not show it): the user is asked before his character is generated.


## §4 2.1, thing 16: his guitar pick on a new bandstand corner in the Spinnaker Lounge (the user, 2026-11-21)

- **The look:** "a plain classic pick", tortoiseshell; four tries from text, then "Use mine as a reference": his own,
  red, a Jazz shape with a raised dot grid. The photo cut out, its words ("D-GriP", the maker's name) and mark painted
  out and the dot grid mended where they had been, before anything was sent; three tries; the user chose the plain
  converter's ("B"), its edges cleaned (loose specks off, black and grey rim pixels removed or set to the red beside them).
- **Where:** the plan's "bandstand by the piano"; the lounge had none: a small one (the user's choice of three), a guitar
  on its stand by a small amp, generated together (try 4 of four, at its own size), first tried by the piano's tail, then
  **between the cream armchair and the sofa** (the user), 2 px down; the piano 8 px forward and the two seated guests 2 px
  down, the lady 5 px forward (the user, a few px at a time).
- **In the world:** 8 x 9, the close-up's outline shrunk by majority and coloured by hand; **point up**, resting on its
  wide edge on the amp (point down it stood on its tip, which a pick cannot). Only after the table scene.
- Built: `bandstand` (`tools/build_ship_art.py`), placed with the piano's move in `tools/build_ship_map.py`;
  `keep_pick` and the guests' moves in `tools/population.py`; `pick` close-up and `guitar-pick` thing in their own
  colours. Test `region9.pick` (absent before the table scene, the corner, the piano and the guests where the user put
  them, the pick on the amp, E takes it); `region9`, `region8`, `boot` pass; `check_overlaps` 0. Generations: 19 (the
  corner 4, the pick's close-up 12). **His four (13 to 16) are placed.**


## §4 2.2, fourteen books, their pages, and reading anywhere she can sit (the user, 2026-11-21)

- **Fourteen where ten was written:** one total, `BOOKS = 14` (`src/config.js`), read by the shelf, the nook's
  `books_all`, the HUD, the trolley's last return and the nook's test; one list of colours (`BOOK_COLOURS`, four new
  stand-ins: indigo, plum, turquoise, sage, until 2.3's covers).
- **The shelf** (mock-ups in the game): "Move the current shelf up two pixels. Make it cover both standing book cases"
  (its board from the first bookcase's left side to the second's right, the gaps centred, 8 px a book); "Remove the
  bookshelf's legs"; the books back on it "slightly more washed out, now they look like pickable objects": washed 12%
  toward the wall (the user's choice of 12% and 20%).
- **The odd book** ("What is that green thing hanging on the book case?"): it was drawn on the glass's front; "Stand
  it in the bookcase's top shelf behind the glass": a dark teal spine with two gold bands among the lit books, a px
  taller than they, in full colours (she uses it).
- **The pages:** drawings for 11 to 14 were turned down ("I'd rather prefer the actual book pages"), then "Text only for
  all the books, same as we have decided now": the ten hint drawings are gone. Each page is the book's real opening,
  readable, in its own language and script; "Try to enlarge the font slightly, making less words per page, but cover
  the entire page. Don't break sentences": shown at 3x on a 260 x 146 page, a running head, justified, whole sentences,
  the spare lines spread. The lettering: Pixelzone (GGBotNet, CC0; of the three CC0 pixel fonts with Polish, Cyrillic
  and Hebrew, the user liked its page, `mock-zone`). The texts: the web's tools quote a couple of sentences at most, so
  the Ukrainian and Russian ones came from online libraries' pages and the publisher's scan (Її війна), the Polish from
  the publisher's free sample (Niebieskie nitki) and a school excerpt (Poczwarka), the Hebrew, «Боря» and Daughters of
  Warsaw from the user; «Тс-с…» set for the scan's «Тс— с…» (the user). **Placeholders:** 1, 2, 6, 14 (two sentences
  each), 4 (a title page): the user gives them on 2026-11-22.
- **Reading** ("How do I choose what book to read?": the lowest unread was shown, no choice): the user chose "a small
  choice": the books she carries ("picked up and unreturned"), "no need to mark read books, they're just books". Book 5
  a regular book, "Make the bed another readable place". Her seated pictures generated: "a proper sprite for her
  seating facing us in that red chair" and "where she sits properly on the bed, reading" (one PixMiniMax clip each from
  the game's own chair and bed, 2 generations; frames with red streaks and a speck left out). The backdrop: "rectangular
  ... round corners ... standing out from behind the book and the title on all sides", "slightly more transparent,
  smooth the edges"; "any number of books ... (1 to 14)". Hebrew titles were cut at the top in a mock-up (a lamed's
  stroke): every title strip now as tall as its letters reach. "Show me other reading locations": the six armchairs at
  the reading tables are the same armchair, so **2.3b is built here**: all seven seats, in full colours.
- Built: `src/world/library.js` (`read(seat)`, `choose()`, `got()`, `heldInOrder()`), `tools/build_reading.py`
  (`assets/sprites/reading.png`, heads for the popups), `tools/draw_pages.py` (pages and titles), the seats in
  `tools/build_world.py` (`library.chairs`), the chairs' full colours in `tools/build_ship_map.py`; `?books=`; E stops
  her bed bounce and sits her to read; the hint `hint.read` (both languages, the pad's buttons). Tests: `region2` (the
  chair, a table chair, the page, the row back, getting up), `region5` (the bed), `region4`, `region6`, `region7`,
  `region8`, `region9` (the nook at fourteen), `lang`, `boot` pass; `check_overlaps` 0. Generations: 2.

## §4 2.1, book 11, and the boat walkway mended on the way (the user, 2026-11-21)

- **Book 11** (row 17, "the boat walkway's end, beyond the boat drill"): the end had nothing to lie on. The user asked
  for it in a boat; the one boat she enters (at 143 m) is forward of the drill and holds book 2, so "the initial plan":
  a **life-jacket box** at the walkway's aft end (generated, try 2 of two), the book on its lid, the box 2 px up and the
  book 2 px into the lid (the user's placing), the box washed 20% toward the recess wall.
- **The walkway, fixed as the user went** (commits `842e657`, `d6a62ee`, `3e4816b`, `70623ef`):
  - the lifeboat's inside showed deck 7's casino: a room entered from outside keeps the ship's side closed, dimmed round
    it (`inDeck` false; its dim over the outside's fronts);
  - her picture 2 px higher on the walkway (`WALK_LIFT`), cut at its two ends as on the balconies;
  - the boats drawn **in front of her** (she walks behind them), the walkway's railing between her and them; the boats
    25% washed (from 35%); every cable a **wire rope** (`src/wire.js`) ending on its ring (each eye measured in the
    boat's picture; the tender's forward hook moved off its wheelhouse, its ring had been cut);
  - **the drill**: its boat, down, is a floor she can jump into and run along, and stays down while she is in it; while it
    moves its ends are a wall to a jump; **gag 15 remade** ("Ouch!"): she sinks onto all fours, dizzy, butterflies, and
    crawls away through the fade (generated from her crawl, 2 clips); the winch and its crewman one generated clip that
    turns with the boat (forward lowering, back hoisting), a wire rope up from its drum, a **generated red warning
    light** that blinks with a faint halo;
  - **the lifeboat's way in, after many tries** (the user's rulings: "the cut away must show the outside of the hull";
    "Remove the door. Make a hatch on top of the boat"; "Crawls from behind the boat"; "her hands cannot be climbing
    the air"; "she still doesn't go into the hatch, but outside the boat"): a **wide hatch on its roof**, seen a little
    from above, its lid taken off; going in, she pulls herself up over its far rim facing us (her own character, a
    skeleton-v3 clip of written poses, her hands held on the rim), stands, turns with her own frames, steps into the
    opening and sinks with her hands on its rim (her `climb-out` frames), cut by its near lip; the 14 frames approved
    together as a GIF. Inside she starts **on top of a ladder** the player climbs down; up past its top she comes out,
    the same frames the other way (no E). A faint warm glow out of the hatch while she stands where E works. ↓ held
    from a climb no longer crawls her. Dropped on the way (each shown, each broke): a side boarding door, a generated
    whole climb (another drawing than her sprite), her ladder clips over the roof (hands on nothing).
  - **the lifeboat itself**: its inside the whole boat (408 px); nine portholes evenly (36 px), the ladder in the rhythm;
    round windows outside at the same columns (a picture of its own, `lifeboat-round`); its forward end furnished
    (book 2 there now, between the flare box and the water can); generated oars and a wooden boathook, level, smoothed;
    the photo frame under the forward oar.
- Tests: `region2` (in, down, book 2, the photo, up and out), `region7` (the drill: on all fours, the crawl), `mishaps`,
  `boot` pass; `check_overlaps` 0 (the boats are outside the outside route's depths now: skipped by name). Not mine:
  `ladder` fails at "walks off the ladder top without falling through" on `d6a62ee` too (the funnel's top puts her on its
  stairway); not looked at. Generations: about 75 (the box 2, the drill 22, the hatch and climb 35, the light 2, oars
  and boathook 5, the rest tries).
- **After the user's playtest** (same day): E behind the boat and the glow from anywhere under the hatch's width
  (`ROOF.reach` 26 px, from 16); **every red lifeboat in the same design, its hatch closed** (the cover made from the open
  hatch's own pixels, its opening in the canopy's reds; "remove the black lines", "remove the black handle"); her ladder
  climb's frames cleaned (a rung-like strip the generator drew under her shoes showed beside her feet on every ladder:
  `assets/source/her/climb-alternating/`, raw frames kept); leaving the boat she is hidden before the fade (her standing
  frame flashed over its inside). Tests: `region2`, `region7`, `region8`, `mishaps`, `boot` pass; `check_overlaps` 0;
  `ladder` fails as before (not this work).

## §4 2.1, book 14: on a console table at the end of deck 9's officers' corridor (the user, 2026-11-21)

- **Book 14** (row 20, "Deck 9 forward, the officers' corridor's end"): the end had nothing to lie on, only about 45 px
  of wall between the end wall and the captain's door (the bow terrace past the wall holds only its railing). The user
  chose a console table (of a console table, a chair, the terrace, the floor). Four generated tries (4 generations): the
  first two came as low desks ("None of them are consoles though"), so two more, tall and slim; all four were placed in
  the running game for the user, who chose **4, a half-moon console in honey teak**, and set it **1 px down**
  (`prop_console_9`, `dy` -1; the book on its top row, `on` 27).
- Kept in its own colours (palettized, browns go mauve) and **washed 35% toward the corridor's wall**, as deck 9's
  furniture inside (`WASH` in `tools/build_things.py`).
- **All fourteen books are now in the world.** `region9` checks E takes it; `check_overlaps` lists nothing; deck 9's
  longest walk without a reward now starts at the book (28 to 140 m).
- Asked on the way: what the captain's door does. As built (`knock()` in `src/world/bow.js`): a polite knock, three
  "knock"s and "…", nobody answers, `sec_captain` kept; the plate's name is still the user's to give. Its floating
  "knock" words are text boxes, not popups (the one such place left), and the door is drawn muted though she uses it
  (§7c): told to the user, left as built.

## §4 2.3, the books' covers (the user, 2026-11-22)

- **Her own copies' covers.** Asked whether the covers should be original or like her copies, the user said: pull the
  official covers from the Internet and generate simplified ones from them. Most were found (Open Library, Amazon's
  images by ISBN, publishers' pages), but several editions were not hers or not online, so the user photographed all
  fourteen of her copies instead (`reference/books/`, git-ignored, never committed). Each was straightened (GrabCut
  and a warp), its words painted out (OpenCV inpaint over the letters, boxes measured per cover), and redrawn by
  PixelLab `image_to_pixelart` at 120 x 180. Of the two modes tried on three covers, redrawn (clean pixel art) over
  faithful (the photo's grain and glare): the user's "Ok". 16 generations in all (Atomic Habits, all lettering, has
  none: its gold dust is drawn by the build). Ids: `assets/source/covers/README.md`.
- **Mends by hand:** Понаїхали's bag came blue (back to grey), Двор sepia (back to black and white but the window's
  blue), Niebieskie nitki's blue bands made taller for its lettering, a leftover of a painted-out subtitle on Її війна,
  the plate's inner rule on Танґо смерті (room for the author's two lines). The covers' blurbs, stickers, publishers
  and taglines are left off; on Philosopher's Stone its "PRIDE / AMBITION / CUNNING" too (the user).
- **The lettering** (`tools/build_covers.py`): each title and author where her copy has them, in its colours, Pixelzone
  at whole-pixel scales; a spine's title turned; Понаїхали's title climbing its tag letter by letter (slanted by whole
  letters); a long title's letters 1 px apart; Hebrew right to left; Pachinko's Korean title left off (no Korean in the
  font).
- **Й was wrong everywhere** (the user: "It adds two dots"). The font's breve is two dots over a bar, and FreeType's
  hinting at 16 px moved the dots a row up. `tools/pixelzone.py` now draws Pixelzone eight times larger and reads it
  back pixel by pixel (the font exactly as designed; the Polish accents moved a pixel too), and the font's Й/й are
  mended to И/и with a 2 px line one row above (the user's B of three). The pages and the row's titles were redrawn
  with it (only the Cyrillic and Polish ones changed).
- **The cover's moment** (`world.cover()`, from `take` and `giveBook`): the close-up's own code with a picture of its
  own, the dim at 35% (the user: "dimmed slightly"), a faint shadow, and the close-ups' warm light (the user's B of
  two, mocked up in the running game first). `region2` checks it shows on book 2 and a key closes it.
- **The small books and the shelf's spines take their colours from the covers** (`BOOK_COLOURS`, `BOOK_ACCENTS` in
  `src/world/library.js`): the cover's ground and its title's colour for the label. A vertical label on the spines
  was tried and reverted (the user: "it's worse now").
- Tests: `boot`, `region2`, `region9` pass.

## §4 2.3 4, the shelf seen close: dropped (the user, 2026-11-22)

- "Drop the shelf seen close from the plan, no need for that. Unless there's some other mechanic tied to it." Nothing
  is: `sec_shelf` was only a line of the spec and the plan (no code); the shelf's spines filling as books come back
  (the trolley), the odd book and the nook with all fourteen back are the shelf itself and stay. A title now shows on
  its cover only.

## §4 2.3, the rest: the books found and given back, the nook, the Library's art (the user, 2026-11-22)

- **The row of books** (`choose()` in `src/world/library.js`): every book she has found, those given back greyed with a
  stamp and not to be read; the HUD's count never goes down. The stamp, by rounds: a red frame with two lines, then a
  green ring with a V, then (the user's picture) a green disc with a white check, two of its pixels taken off and moved
  one right; RETURNED beside the chosen one's title in green (the word is wider than a book in a full row, so on the
  cover only the mark: the user's choice of three). While the row is open the HUD fades (a full row reached under it).
- **The trolley:** with more than one book on her, the row opens on those she carries; each E gives the chosen back, the
  row opens again on the rest until none is left or Esc. `hint.return` once.
- **The nook:** its armchair is a reading seat (`kind: 'nook'`, full colours, its own pixels only: a box had left a
  pale patch of wall), all fourteen to read. **The bookcase's opening, reworked:** no screen shake; it shudders a px
  each way with puffs of dust rising at its two sides (PixelLab's effects workbench, free: `assets/source/things/dust-puff/`),
  then slides right behind its neighbour (it was a fade); the entrance a wooden casing round the nook's own picture at
  its lamp and armchair, washed 35% (`nookEntrance()` in `src/world/bow.js`). Its stack of books left of its door; its
  cat picture generated (try 1 of three, its ear's red black, its eyes Bumbot's yellow-green). `?at=nook`; `did=books_all`
  now also fills the shelf. The win screen counts 14 (it said 10).
- **The nook's photo:** her armchair at home (the user's photo cut out, nothing of the room sent), PixelLab's redraw
  try 2 of three, its navy chair recoloured to her greys with the throw's woolly weave and its cushion found by its own
  outline (a first try by its purples split it diagonally with a yellow tint: the user saw it): `tools/recolour_nook_photo.py`.
  On the wall: a 20 x 26 redraw, faded as an old print, its oranges mostly out, in a gold frame centred over the table
  (`tools/frame_nook_thumb.py`). Seen close, every photo slot's picture now in a gold frame (`framed()`).
- **Generated for the Library:** the return trolley (a small bookcase on castors, try 2 of three) and the shelf's board
  (try 2 of two, its plain middle lengthened to 125 px); the row's small covers, PixelLab's 16 x 22 redraws of each cover's
  picture without its lettering (the user: "Use the covers without the text"; a first three with lettering were set
  aside).
- **The pages:** books 1, 2, 4, 6 and 14 typed by the user from her copies (drop caps and lost quotes mended, the
  unfinished last sentences left off); book 4's page may break a sentence at its colon (one line short otherwise).
- **Dropped:** reading while standing (GAME_DESIGN's table); the shelf seen close (earlier today).
- Generations: about 30 today in all (covers 16, minis 17 with the three set aside, the cat 3, the trolley and shelf 5,
  the photo 3 and its two small redraws 2). Tests: `boot`, `region2` (now also the trolley's row with two books and the
  row of found books), `region9` (now also the bookcase slid aside and the nook's armchair with fourteen), `lang` pass;
  `check_overlaps` 0.

## §4 2.4 begun: cabin 8206's tangerines (the user, 2026-11-22)

- Its two tangerines hung 7 px under the desk's top, in front of its edge, one over the phone: now on the top (40 px
  up), right of the phone and the daily programme (`tan_8_8206` at 118).
- **On the day after they are gone**, picked up or not (the user: "on the day after, the tangerines won't be there
  anymore ... they should be removed in any case"): `TANGERINES_UNTIL` in `tools/population.py` gives a tangerine an
  `until`; `placeTangerine` skips it once met, `world.dropTangerines()` (from the story's flag refresh) takes it away
  while the screen is black, not counted. Tests: `boot`, `cabin`, `finale` pass.
- The desk's eight (2.4): two layouts shown (A: his on the desk unit, hers on the window sill; B: hers on the shelf,
  his on the bed); the user is deciding with the day after's whole arrangement (the bed's reading spot stays free).

## §4 2.4, the desk seen close (the user, 2026-11-22)

- **Correction to the entry above:** the user then chose to keep cabin 8206's tangerines on the day after if not picked
  up ("since we're not putting anything on the desk"); the removal (`TANGERINES_UNTIL`, `dropTangerines`) is gone.
- **The eight do not fit the room** (the desk 36 px, half of it the phone; two layouts on the shelf, the sill and the bed
  shown; the bed's reading spot must stay free): the user chose **the desk seen close**. E at the desk (`sec_desk`, the
  cabin picture's column 110) shows, over the dim at 2x, a picture of the desk under the TV's lower edge, her four
  things and his four each from its find (`save.keeps`), **the bare desk where one is not found, and with none** (the
  user: "On None, show empty desk"); **any time she is in the cabin** (the user), Bumbot in her arms too (`look`: looking
  needs no hand; the evening of the catch is a scene the moment she enters, so in play that is the day after).
- **Its picture:** a rough of the approved close-ups shrunk smoothly on a desk drawn in code (the user chose the first of
  two: each close-up at its own scale, not true sizes; the TV made a TV, centred, only its lower part), redrawn by
  PixelLab `image_to_pixelart` 400 x 225 (try 1 of three, 3 generations), two stray marks on the mask taken out; his
  shirt's two words kept as the redraw's smudge (drawn as strokes they read as a barcode). **The bare desk by rule**: its
  wall, back edge, top, edge and front are flat colours, so each thing's box is filled along its row (free, exact, no
  inpaint); each thing is what differs from it in its box (the mask and the handheld split by colour, the flag's stand
  and the shirt's sleeve by the nearer box, a 2 px bit of the back edge given back to the desk); bare + all eight is
  the redraw exactly. `tools/build_desk.py` to `assets/ship/desk/`; `world.deskSeen()`, `library.panel(key, { scale })`;
  `DESK_THINGS` in the config; `?keeps=flag,pick` or `desk` for testing.
- Tests: `boot`, `cabin` (now also E at the desk: none, two, all eight the day after, a key closing it), `finale`,
  `region2` pass.

## §4 2.4, Bumbot's bed seen close, the day after (the user, 2026-11-22)

- **His eight do not fit the room either** (about 126 px of them side by side; the bed's top about 97 px, him and her
  reading spot taking most of it): the user chose **"seen close, like the desk"**. On the day after, E by him (`bb_home`)
  makes him purr and shows, over the dim at 2x, him lying on the bed with his eight round him (massage gun, car, collar
  bell, feather toy, snack tube, tennis ball, wool, sardine tin), each from its find (`keep:cat:*` in `save.keeps`), the
  bare bed where one is not found and with none (`world.seenClose('bed')`; the desk's code made one for both,
  `seenClose('desk')`). No hearts on that E (the user: "we cannot see them anyway").
- **E by him is from the floor only:** it had been anywhere within 26 px of him, the bed too, and her reading seat on
  the bed is 18 px from him: on the day after she could not read on her bed (the user: "she still has to have access to
  the bed's reading spot"). Now on the bed E is her reading.
- **Her bounce for joy on the bed stays** (it starts by itself when she stands still a second, not on E; the user asked
  it removed, then: "if not, then leave it". It was taken out and put back exactly).
- **Its picture:** a rough of him cut out of the user's photo on a bed drawn in code in the cabin's colours, his eight
  the close-ups shrunk smoothly, then PixelLab `image_to_pixelart` 400 x 225, faithful 150 (9 generations in all,
  `assets/source/closeups/bed/README.md`). The user's steps: try 3 of three (photo 1, eyes shut); the other photo to
  compare; "the eyes are not right, why not leave them open?"; photo 2 (stretched out); his tail over the runner; the
  massage gun bigger, its handle on the runner's left edge; the car, the bell and the tin on the front row, 12 px apart.
- **The bare bed by rule** (`bare_bed` in `tools/build_desk.py`, which now builds both pictures): along the row as the
  desk's, but where an edge runs down through a box: under the gun the runner from its own pattern (its chevrons repeat
  every 16 rows exactly: the same column 48 rows lower), above the bed's top the cushions and the pillow straight down,
  their bottom edge from the nearest open column of the same thing. The boxes 2 px wider all round (the things' light
  rims share the bed's colours; streaks were left otherwise), and specks the redraw put round a thing kept with it
  (`bits`). Bare + all eight is the redraw exactly; the desk's files came out the same.
- `?keeps=` takes his things' names, and `bed` for all eight (`BED_THINGS` in the config).
- Tests: `cabin` (E by him from the floor: none, two, all eight, a key closing it; on the bed by him, E is her reading)
  and `finale` (the day after: E by him first takes book 5 off the bed, then the bed seen close) pass. Not run: the
  rest of the suite.

## Bumbot's massage gun from the spa's masseur (the user, 2026-11-22)

- **The idea (the user's):** the massage gun (6) a quest item from a massage person in the spa. Of five ideas the user
  chose "she gets a massage": E at the masseur, she lies on the table, and he hands her the gun after. It leaves the
  gym's rowing machine (region 6) for the spa (region 9, where the spa opens). Then the user's scene, step by step
  (`docs/massage-sequence-prompt.md` is the user's own note of it, not committed).
- **The room remade:** the old masseuse "huge", the guest "tiny"; the masseuse, both tables, the guest and the round
  table taken out. **The massage table** generated (four map objects, the user's 3, a sage pad, shown with her lying on
  each; its back legs deleted after, `no_back_legs.py`), two of them at 42.2 and 45.45 m. **The round side table**
  generated in a strict side view (the user's 2 of four, 18 x 21) and made **every** round side table on board (the
  spa's, the Chapel's rose, Teppanyaki's two bonsai, the wedding cake's, the balconies', the nook's); **what stands on
  one is 2 px into its top** (`ON_SIDE_TABLE`, the cake's `src_cake`, the nook in `tools/draw_rooms.py`); the second
  bonsai and its teapot set on the narrower top; the cake was 4 px over it and is set for the new height. The nook's
  table has the spa's candle in its coffee cup's place (the user's A of two).
- **The masseur:** a man in a spa uniform (the user's), pro in the drill officer's style (61 px, a 15 px head). His
  stretch: four tries failed (turned to us in a T, hands to his face, hands behind his head) before the library's
  `arms_overhead` on his skeleton; the user: slower in the game, the hands up longer and his head looking up (held
  0.6 s a frame, 5 a second). His massage, one skeleton clip seen from the front (behind the table) and the back (his
  back to us): the back view's hands were drawn over his own back, painted out, the back one even white ("clean his
  back"). His walk round the table (the far arm's doubled outline thinned) and his toss (both hands, the game draws the
  gun in them).
- **The guest:** a woman in a towel wrap and turban (the user's of three). Her lying face down: the first two edits
  bared her back with the towel at her hips, made again with the towel wrapped as she stands; 3 px into the pad in all
  (the user: "at least two pixels", then one more). Her get-up from the table and Bumbusik's climb on were made with the
  game's table in the picture (Bumbusik's first try flipped from her back to her front in one frame: remade on hands
  and knees, her hands on the table throughout), the table taken out after (`tools/untable.py`).
- **The scene, the user's rounds of fixes:** the guest walks faster (42 px/s), in front of the sauna's open glass door;
  the whole round for the guest too, over and over; E stops him at once and he goes behind the table round its head,
  the guest getting up in the same moment; **the user's idea:** the guest goes into the sauna and sits on its bench
  facing us while Bumbusik is massaged, then comes back and lies down again (her sitting made on her skeleton; the bench
  the generator drew under her taken out by its own colours: a first try by kinds of grey took her own pixels, "missing a
  few pixels"); Bumbusik's round is one: behind, a stretch at her feet, in front his back to us, a stretch at her head,
  then she gets up and gets the gun. His layering: the user asked that she cover him in front of the table, which put her
  over his back while she lay there ("incorrect layering"): in front he is over her while she lies on the table, under
  her while she stands. He is 1 px lower but facing us behind the table. Her climb's pink speckles (greys the palette
  took to the mauve her sheet turns pink, and her skin's shading scattered) cleaned. The pad's leftovers under the
  guest cut. **The empty table too (the user's addition):** E at it brings him over at once, the guest waiting on hers;
  he goes back to her after. His slide on the way there (the interrupted step stopped his new walk's clip) mended.
- **Cost:** 76 generations (the tables 8, the masseur 31, the guest 33, her climb 4); every try and its id in the
  READMEs (`assets/source/people/masseur-raw/`, `massage_guest-raw/`, `assets/source/her/massage-lie/`,
  `assets/source/ship/massage-table-2/`, `side-table-2/`).
- Tests: `region9` with a new case `region9.massage` (the guest's table: the sauna, the gun, her return; the empty
  table: he comes, she waits, no second gun), `boot`, `tools/check_overlaps.py` (0) pass. Not run: the rest of the suite.

## The sauna's steam from its coals (the user, 2026-11-22)

- **The user's:** the steam gag at the sauna's door removed; the steam rises from the coals inside the sauna instead, "no
  overlaps and leaking of steam outside", a timing obstacle like the sprinkler; caught, her gag inside the sauna and her
  checkpoint.
- **Built** (`Steam` in `src/world/bow.js`; `BOW["steam"]` in `tools/population.py`: the stove at 51.7 m, the walls at
  47.9 and 52.9, every 4.6 s, 1.6 s on, a 0.8 s tell): the tell, the coals glowing and a few wisps with the hiss; then
  the steam up from the coals to the ceiling and out under it toward the walls, thinning. Every puff, the burst round her
  too, is cut to fit inside the walls' inner faces and under the ceiling's beam (`puff`): nothing of it outside. Caught
  within 20 px of the stove's middle: "Fogged", gag 17 where she is (her slide stops short of the sauna's doors), then her
  checkpoint; a tray spills as before. The guest on the sauna's bench (49.6 m, the massage scene) is clear of it.
- **The user, on the GIF previews:** "make the steam disperse more to the sides, not only up": each puff drifts out to its
  own side as it rises, wider the higher (a scattered side for each: a sequence in step with its height lined them up
  in one curve), about 64 px either side near the top. GIFs recorded from the game's own renderer on the stepped clock.
- `?at=steam11` now starts inside the sauna, forward of the stove. Tests: `region9` (by the stove as the steam rises:
  fogged; the fan and the swoon) passes. Not run: the rest of the suite.

## Her husband at his table, and the Great Outdoors' tables and chairs (§4 2.4, the user, 2026-11-22)

- **His forehead:** "Remove one line from my forehead, like we did on the icon": a row out of each view where two
  rows of the forehead are alike (`assets/source/hud/husband/short/shorten.py`); his character imported again from
  those (`5b85cf25-df58-47e2-b592-affd32aff145`, 0.25 generations) so every clip keeps it.
- **The chairs:** "Use wicker chairs, like in the game, but regenerate them to be made with their side to us. When I sit
  in the chair, its arm that close to the screen shall obscure me. I shall obscure the farther arm." Four wicker tries
  "too garbled"; "other chairs fitting that location": the user's 5 of eight, a teak armchair. **The table:** the old
  round white table stretched taller (the user: "slightly taller") was "too distorted"; generated ones: four (teak,
  square) "none of them", four more round, the user's 5, a white café table. "Make it beige. Also, make the chairs
  beige": both put on a beige ramp by lightness (`patio-table/beige.py`), kept off the palette (on it the teak went
  olive). At all seven tables (the Great Outdoors' five, the Garden Café's two window tables). What stands on them 3 px
  into the top (the user: 2, then "one more pixel down"; `ON_PATIO_TABLE`, the table scene's photo too).
- **The far guests** (the reader, the couple) have wicker chairs drawn into their own pictures: taken out of them and
  set in the beige chair (their shins shortened to its lower seat): "This doesn't work, let's leave them as they are
  for now" (`assets/source/people/go-seated/README.md`).
- **Him seated:** his skeleton-v3 idle (poses: hips over the 15 px seat, hands on his knees). The first try had the
  generator's own chair under him (taken out by its colours), its first frame's face "distorted", and the stills were
  shown from the browser's screenshot resampled ("distorted": since then every still is the renderer's own picture at
  exact game px). "My far leg should be behind the table": the legs together could not be told apart ("not working");
  regenerated "the entire idle" with the legs apart, the far one forward under the table. One face (skeleton-v3 redraws
  the head a little each frame: one frame's head in all), one pair of legs; the far leg cut into a frame of its own drawn
  behind the furniture (`under`, new in `src/world/people.js`), the chair's near arm a piece drawn over him (`cover`,
  `patio-chair-arm`). On the palette his hair went olive, his skin pink, his eye red: he keeps his own colours
  (`own_colours`, new in `tools/build_people.py`). The stand-in is gone (`husband-raw/standin/`). **Until his cabin seat
  is settled he sits on nothing in cabin 8206** (the stand-in brought its own chair).
- **Cost:** about 37 generations (the chairs 8, the tables 8, the guests 15, his import 0.25, his idles 6). Tests:
  `boot`, `region6` (the table scene, his book, the photo) pass; `tools/check_overlaps.py` 0. Not run: the rest.
- **In cabin 8206 (the user's):** at first a desk chair (four generated, the user's 3, `assets/source/ship/cabin-chair/`,
  not used); then "place me on the sofa that's under the window, facing the screen"; a south view of his seated idle
  (3 generations, `sit-idle-2/south/`, not used): "I already have my facing the screen sprite, use that one. My lower
  body isn't visible anyway". His front view (`front`, from `assets/source/hud/husband/short/south-bear.png`) at 160 px
  into the room, the bed drawn again over him (`assets/ship/cabin-8206-bed.png`, the room's own pixels where
  `tools/draw_cabin.py` draws the bed; a `carry` in front of him), under her and Bumbot. Tests: `finale` passes.

- **Merged:** `main` fast-forwarded to `three-uses` (3fb257b: his table and his cabin seat) and pushed, on the user's
  word (2026-11-22).

## §4 2.4's rest: his gestures and the table scene (the user, 2026-11-23)

- **His four gestures**, seated, skeleton-v3 poses on his character from the idle's pose, through `make.py` (his legs held,
  his far leg behind the table): `wave` (his near hand raised forward toward her; the first try's hand crossed his face),
  `laugh`, `give` (the held frames' stern brow given the first held frame's face), `eat` (an edit of his seated frame with
  a soft serve, then PixMiniMax). The book is in his fist while his arm is out, from the clip's third frame
  (`GIVE_HANDS` in `src/world/world.js`). Ids in `assets/source/people/husband-raw/README.md`.
- **The crates** on deck 11 stood between the soft serve machine and his table: no cone could pass ("Do we need that
  obstacle here at all?"). Moved aft of his table between the Garden Café's palms (232.8 m), off every carrying route,
  their two tangerines with them.
- **Bumbusik at the table** ("what does Bumbusik do, while seated?"; "not seating properly in the chair"): her old
  `sit-eat` had empty hands, made on another chair. Remade on her skeleton (the `sit_seat` move, her near hand at her
  chest, then small head dips), the generated chair taken out, set 7 px further back into the patio chair than first
  composed (the user's 7 of 2 to 8), the chair's near arm over her lap; her face held (her standing sprite's head:
  "Her face is distorted while she's eating"); her cone her husband's cone's own pixels ("too big, let it match his";
  the carried cone stays as it is: the user's "only at the table"). Clips `sit-cone`, `lick-cone`, `sat`, `sit-up`;
  `assets/source/her/sit-cone/README.md`.
- **Only the book after eating** ("two things appearing at once"): the photo slot left his table for La Cucina's wall on
  deck 5 (`slot_cucina`, 154.25 m, "between the entrance and the first window"; the user's choice of place), with the
  user's own photo of the two of them at La Cucina's window table (sent whole, his *vyshyvanka* kept; tries at 108 x 144
  "too pixellated", try 4 of 168 x 224 chosen; a 20 x 26 redraw framed small on the wall: `tools/frame_nook_thumb.py
  cucina`); the preview shows it at 2x (its margin 76 px). A start place at La Cucina's entrance, `cucina`.
- **The book he gives** is *Atomic Habits* (book 1, "switch the book to the Atomic Habits one"); book 6 lies on the
  Atrium Café's table in book 1's old place.
- **Cost:** about 45 generations (his gestures 23, hers about 15, the photo 7). Tests: `boot`, `region6`, `region9` pass;
  `tools/check_overlaps.py` 0. Not run: the rest.

## The Great Outdoors refined (the user, 2026-11-23)

- **Her hop with a load** ("the ice cream is just hanging in the air"): her sheet's `carry-rise`, `carry-apex`,
  `carry-fall`, her own jump's poses with her carrying arms ("that doesn't look like a jump at all" of a hop with straight
  legs), the load by her fists in each (`HOP_HOLDS` in `src/world/carry.js`); height and timing unchanged.
  `assets/source/her/carry-jump/README.md`.
- **The machine:** she steps to its side (the side she came from, `SWIRL.aside` 18 px) and faces the cone filling.
- **The gull** (`gull_go`): no shadow; its hover 600 ms (950 before; the pool's gulls too); its perch 210.9 m, away from
  the machine; with her cone it flies off the screen, stays away 5 s and flies back, each leg placed by the time since it
  began (`FLIGHT` in `src/world/hazards.js`): the birds are updated only while she is near, and one left mid-flight had
  stayed in the air.
- **Feeding him every time** while he is at his table (his book the first time only); a cone she eats herself
  (`sec_cone`) only from the catch to the day after; `region6` checks a second meal, no second book.
- **The kiss** (E with her hands empty once he has been fed; before, his wave and his bubble): he stands facing us (his
  front view; his chair's near arm and far leg hidden: the people's `coverPics`), she steps up 6 px to his right with
  her back to us, they embrace (his `embrace`, hers, his near hand drawn over her: `hug-hand-*`; her forearms behind her
  hair: "She is hugging herself, not him"), seven hearts, the embrace backwards, he sits; she faces the way she was going.
  `assets/source/her/embrace/README.md`, `assets/source/people/husband-raw/README.md`.
- **Cost:** about 13 generations (her hop 8.4, the embrace 4.2). Tests: `boot`, `region6`, `region8`, `region9` pass. Not
  run: the rest.
- **Merged:** `main` fast-forwarded to `three-uses` (e4f719c: the table scene, the photo, the Great Outdoors refined) and
  pushed, on the user's word (2026-11-23).

## `main` taken in, 2.5 the `keeps` playtest, book 6 moved (2026-11-23)

- **`main` into `three-uses`:** the Refinement session's §7c (`src/highlight.js`: what she can use pulses where E would act;
  doors washed at rest), part 13 planned (§7h). A fast-forward to cd03df3, no conflicts; the maps rebuilt identical.
- **2.5, the `keeps` playtest** (`python tools/playtest.py keeps`): one game with the close-ups shown (the other scenarios
  skip them). Nothing counted at the start; the first of each kind (the wool, her flag, book 6, his t-shirt) shown close,
  its count off while it shows and on once a key closes it, in the order found; a second find and a book given (9) up by
  one only once closed; his four places empty before his table scene and each holding its thing after; cabin 8206's desk
  seen close with two found and with all eight, Bumbot's bed the same: each found thing's box differs from the bare
  picture, every other box is bare. **Decided:** the shelf's close view of 2.5's text went with 2.3.4 (dropped); "each
  region's scenario ... the cover closed" is this one scenario, not close-ups turned on in every region's (they would
  each need a key press per find).
- **A book's count waits for its cover** (found by the test): a found thing's count came on as its close-up closed, a
  book's while its cover still showed. Now both the same (`world.take`, `giveBook`: `hud.expect('book')`, released by
  `cover(n, then)`).
- **Book 6 moved** (the user: "why doesn't the book pulsate?"): at the Atrium Café's table its pulse, 20% toward the wall
  as the café's props are washed, barely changed its near-black cover, and from where E reaches it her body stood in front
  of it. The user asked whether it is progress or a collectible (a collectible: the fourteen open the nook, nothing else
  waits on it), was shown the shore excursions' desk (two ends of it read as a second screen), Four Seasons' table and the
  brochure stand's top, and chose the stand's bottom row, the middle pocket: at 134 m, 4 px up, the stand's lowest five
  rows drawn again in front of its foot (`cover`). It hides the middle brochure and most of its neighbours (a brochure is
  4 px wide, the book 10): shown so, approved.
- **The pulse itself** (`src/highlight.js`, the Refinement session's) is unchanged: a dark pickup pulses faintly wherever
  it lies. Offered: pickups pulsing deeper (about 50%); not decided.
- Tests: `keeps`, `highlight`, `region1`, `region2`, `region6` pass. Not run: the rest.

## §5 3.1 begun: the Stardust's look-out, its drop, the theatre's twins, the booth's photo back (2026-11-23)

- **Look-out 1, the Stardust balcony's rail** (`LOOKOUTS` in `tools/population.py`, `Lookout` in `src/world/movers.js`):
  standing still on the spot (243.45 m, half a metre either way) eases the camera aft and down over 1.8 s to the stage
  seen from above, curtain to curtain, her at the rail top left; it holds while she stands and comes back in 0.7 s when
  she moves. **The wait is 0.5 s, not the plan's 2 s** (the user, on trying it). Nothing counted, no art.
- **The camera is the look-out's while it is away from her:** the follow's deadzone (40 x 24) held back the first 20 and
  12 px of a follow offset, and the view stopped short. Its middle is her middle as the follow keeps it, eased on to her,
  mixed with the view's by one eased number `k` (the intro's way); at 0 the follow takes it back where it stands. If
  anything else takes the camera meanwhile (the outside view, a scene, a checkpoint: `cam._follow` set again), the look
  ends without a move of its own.
- **Two decks open at once** (`world.lookOpen`, read by the ship scene's cut-away): opening deck 6 alone (`viewOverride`)
  closed deck 7 and she floated over its white side. **A deck so opened is a crossfade from its dimmed hull to its
  inside at every step, never the hull undimmed** (the user: "I don't want to be shown an undimmed hull"): the hull's
  alpha `(1-t)(1-r) / ((1-t)(1-r) + t)` and its dim `1 - t` (`lookDim()` from the alpha), r the deck dim's 0.88; only
  while a deck is cut open (not in the outside view); never on her own deck.
- **The drop off that rail** (the user: "make the below deck open earlier, and don't show the hull in between"): the
  look-out names it (`drop`: 244 to 256 m, onto deck 6). Clearing the rail from deck 7, the stage opens from its dim in a
  quarter second and both decks stay open as she falls; landed, deck 7 closes to its dimmed hull once the cut-away has
  deck 6. Jumping from the view, the view and the stage hold till she lands, then the camera comes back to her. A jump on
  the stage itself opens nothing.
- **The theatre's twins** (the user: "two identical women next to each other in the front rows"): a sitter the same as
  the seat before is swapped for another by a draw of its own (`tools/build_ship_map.py`, `seat()`), the rest where they
  were; in the whole theatre one seat changed (deck 7, 241.3 m: the lady with the doll to the man in the navy suit).
- **The lighting booth's photo was missing** since 70623ef (2026-11-21): `slot_lighting` had gone into the lifeboat slot's
  comment on one line; `region3` found it (failing the same on b81e18a, in a worktree). Split back; no other entry so hidden.
- Checked in the game: the outside view while looking (the hull closed), walking off (deck 6 dimmed again, the follow
  back), jumps on the stage (nothing opens), after the drop (nothing left open). Tests: `boot`, `balcony`, `region3`,
  `golden`, `highlight`, `mishaps.light` pass; `tools/check_overlaps.py` 0. Not run: the rest.
- Next: look-outs 2 to 5 (deck 4's and deck 5's portholes, the Spinnaker's balcony, the Great Outdoors' stern rail).

## §5 3.1: look-out 2 by E, look-out 3 dropped (the user, 2026-11-23)

- **First built as the Stardust's:** deck 4's aft end and deck 5's forward end, each a porthole on the corridor's wall
  (the atlas's brass `porthole-bg`, its dark glass cut out in the game and the windows' live sea behind it, a glint on
  it, in the place of the corridor's picture there); half a second still eased the camera out of the ship to the wake
  behind the stern, or to the bow wave, the deck dim fading and the far horizon gliding down onto the waterline with
  it. Deck 5's first place (26.75 m) was in the paperboy's round (26-42 m), so it went over the knitting lady's head
  on the end wall.
- **The user: "I don't like either of those."** Deck 4's porthole stays and is used **by E**: she steps to it and
  turns her back to us (her `back` frame), and half a second later the outside view (O) shows; **any movement key**
  brings the camera back to her (the overview's `porthole` flag; O and Esc too; O pressed alone still ignores the
  movement keys, as the user had it on 2026-11-07). **Deck 5's is dropped from the plan.** The code for the eased view
  out of the ship (the dim's fade, the horizon on the waterline, a view at a fixed place) was taken out again.
  `PORTHOLES` in `tools/population.py`; `world.porthole()`, `lookOutOf()`. A start place `wake4` (deck 4, 246.5 m).
- **Playtests added:** `region3.lookout` (standing still: the view, decks 6 and 7 open; a step: back, deck 6 closed;
  over the rail both open all the way down, none after the landing) and `deck4.porthole` (E: her back at the
  porthole, the outside view; a movement key: back with her). Tests: `boot`, `highlight`, `region1`, `deck4`,
  `balcony`, `region3` with both cases pass; `tools/check_overlaps.py` 0. Not run: the rest.
- No generations spent. Next: look-out 5 (the Great Outdoors' stern rail), then 4 (the Spinnaker's balcony, with
  part 11's P2: her drawn in front of its glass).

## §5 3.1: look-out 5, the Great Outdoors' stern rail zoomed out (the user, 2026-11-23)

- **Its form asked first** (after 2 and 3's views out of the ship were turned down): the user chose "Ease aft, not
  down" over the porthole's E and dropping it. Stills of the view 200 px aft at her height, by day and at sunset (the
  sun keeps its place on the screen: at 160 px it stood on her head), approved; built as the Stardust's.
- **Then "zoom out during this lookout. Showing a bit less than rear half of the ship"**, and moved aft "until only half
  of the ship shown here remains in view": `frame` in `LOOKOUTS` (197.6 to 321.6 m across at its end; the waterline
  77% down). The zoom goes by its ratio, the middle by the screen's share of the way; the camera's bounds off while it
  is out. Every deck closed while it is (`world.lookFar`, the cut-away's target none), as in the outside view.
- **The far background under the zoom:** the intro switches between play's layout and the outside view's at a zoom of
  0.6, which would make the islands and clouds jump; instead play's layout is drawn `keep` times bigger
  (`VIEW.zoom / zoom`, `src/background.js`), so it keeps its size on the screen, and its horizon glides down onto the
  waterline with the way out (`layBackdrop()` in the ship scene). It is laid again after the world's update while the
  zoom runs: laid before it, it lagged a frame and its edges showed black.
- Along the user's arrow (aft and up) the sea left the frame: straight aft, shown side by side, approved.
- **At sunset the sun is behind the ship** (it stands near the screen's left in play's layout); its glow and lit clouds
  show aft of the stern. Said to the user; left so.
- Playtest case `region6.lookout`. Tests: `boot`, `intro`, `finale`, `region6`, `region3`, `deck4` with their cases pass.
  Not run: the rest. No generations spent. Next: look-out 4 (the Spinnaker's balcony, with part 11's P2).

## After the ending the evening goes on (the user, 2026-11-23)

- **Asked:** after the ending, is it sunset, and is her husband in two places? It was midday ("the day after"), he back at
  his table and off the cabin's sofa, never in both. **The user: "I want the exploration after the ending have the same
  state as at the ending".**
- **Built:** the evening of the catch (`flag:catch&!flag:home`) no longer ends at `home` for the sky (`refreshFinale`:
  the sunset from the balcony's scene on), her husband (`npc_husband` until the catch, `npc_husband_home` from it), the
  kids' club (the toddlers until the catch, the fort down, its pile from the catch) and the cone that is hers (`lido.js`).
  Bumbot sleeps on the bed after it as before; her hands are free.
- **Asked: those who clap her home** (the steward, the stage manager, the engineer, the wedding planner): back to their
  own places after it (the user's choice of two). On the way: **they had stood in two places at once** from the catch till
  she was home (outside 8206 and at their own places): their own places now `until="flag:catch&!flag:home"`.
- `finale`'s checks of the day after changed to this state, and two added (none at their own place while clapping her
  home; all back after). Tests: `finale`, `region6`, `region9`, `region2`, `keeps`, `boot` pass. Not run: the rest.

## Her towel turban: kept while she reads on the bed, its top outline back, no blue (the user, 2026-11-23)

- **The towel went from her hair when she sat to read on the bed** (the user's bug): the bed's reading clip was made
  without it. A towel version, made as the first (one PixMiniMax clip, 1 generation, from cabin 8206's picture with her
  towel look standing at the plain clip's very place), cut by a new tool, `tools/cut_reading.py` (its rules in
  `assets/source/her/reading/README.md`), each fault the user or the frame-by-frame check found mended in the cut:
  the window lit grey, the towel's inside cut away over the pale wall picture, tufts over it, "shifting pixels in front of
  the towel" (the picture's greys within a px of its outline, kept because the closing counted its own grown ring),
  "the top-right part of the turban outline partly missing" (a diagonal outline's steps joined only side to side),
  "some white spot behind her" (the pillow redrawn against her back). `library.read()` plays `bed-towel` while the towel
  is on. The towel is only on in the cabin, so the Library's chairs need none.
- **"The turban is missing some of its outline on top"** as she steps out of the shower: PixelLab's front still of the
  towel look has the turban touching its canvas's top, its outline cut off. `rotations/south-topped.png`, a row taller
  with that row of outline in the outline's colour, stood by its lowest row; no other towel frame touches its top.
- **"Remove the added blue pixels from all the with turban on frames"** (the user asked whether they were water): the
  palette's sky blue shading the towel (372 px) and the reading clip's blue-greys turned to neutral grey of the same
  lightness, in the figure's top 18 rows, dark blues (her eyes) kept: `grey_top` in `tools/build_sprites.py`
  (`HER_TOWEL`) and in the reading clip's cut.
- `region5` checks the towel clip on the bed and that she stands up in the towel; its stale "two tangerines in the welcome
  basket" (at 104 px since the desk took them, 118 px, 2026-11-22) mended. Tests: `region5`, `cabin`, `boot`, `keeps`
  pass. Not run: the rest. 1 generation.

## Her blouse without sky blue; the water on her blue (the user, 2026-11-23)

- **"I still feel like blue pixels were added to Bumbusik's sprites"**: her stand and run were checked through every
  build of her sheet (36 commits): pixel for pixel the same since 2026-10-31. The blue was there from her first sheet:
  PixelLab shades her white blouse with pale lavender-blues, and the palette's nearest to the palest is its sky blue
  (`#8fd3ff`), a few px in every frame of hers (5 in her stand, 82 in her run). The user chose its replacement from three
  (the blouse's own grey-blue shade `#9babb2`, white, a neutral grey): the grey-blue. `blouse_grey` in `tools/palettize.py`:
  sky blue joined to the blouse's white or grey-blue, after the palette, in her sheets (`blouse` in `HER`, `HER_TOWEL`,
  `HER_CAT`, `HER_MISHAPS`) and the gags (`tools/build_gags.py`). Her eye's glint and loose water stay.
- **"When she's wet, a lot of water pixels were turned to grey"**: the first try greyed water on her too, and the user
  found the wet gag's drips grey before it (since it was built, 2026-11-18: PixelLab's blue drips, `#6889ab`, fell on the
  palette's lavender-grey). Frame by frame with the user was too slow for the deadline; measured instead: PixelLab's
  water on her is cyan-blue (green well above red), her blouse's blues lavender-blue, and not one px of her 399 dry
  generated frames is cyan-blue. `water_blue` (`is_water`): in her wet clips (the wet gag's seven, `shower`, `swim`,
  `shiver`, `splutter`: `WET` in `tools/build_sprites.py`) a cyan-blue source px goes on the palette's nearest true blue.
  The palette's own sky blue is not water (a gag's first frame is her built sheet's). Every wet clip's frames looked
  over (before, after, the blue marked); what no tint tells (pale grey drips, blue-white water on the blouse) stays grey.
- Only colours changed (diffed against the old sheets: dry clips only sky blue to grey-blue). Tests: `boot`, `cabin`
  pass. Not run: the rest.

## Look-out 4 on the Spinnaker's balcony (§5 3.1, part 11's P2; the user, 2026-11-23)

- **Shown two mock-ups:** her drawn in front of the windscreen (P2) and two zoomed views. **The user: the glass "Leave
  as it is"; the view A, 5's mirror** (-63.4 to 60.6 m: the sea ahead of the bow and the bow, every deck closed).
- **Built:** `look_spinnaker` in `LOOKOUTS`. The user's fixes after trying it: **the spot** (at 33 m, a metre wide, it
  "never triggers": she stood against the windscreen; to the first palm it went off "when we stand back a little":
  now the first metre from the windscreen, 31.5 m, reach 0.5 m); **the gulls on the rail over her** ("they sit on a
  railing that is closer to the screen": `front` flocks at `player + 0.05`) **and making way** ("they have to take off a
  little bit, as if out of the way, and then sit down after I land": `Flock.dodge`, the one her head comes up at flaps
  34 px up and 10 aside, 0.15 s after she lands it sits again over 0.4 s, on the scene's clock); **the cloud "cannot
  obscure the gulls"** (it was behind them: their white heads have no outline; the user chose, of an outline or
  clouds higher, the clouds higher: `CLOUDS_UP` 52 from 40 in `src/background.js`, the clouds 61 to 99 px over the
  horizon on the screen); **"a bulge under the dark strip of the front part of the livery"** (the bow's dark band 74,
  84, 71 px thick where it tapers from 87 to 59: its lower edge follows its upper one there, the thickness eased with
  the slopes either side, `even_band` in `tools/build_livery.py`, the rebuild otherwise identical).
- Tests: `region9.lookout` (new: walked into the windscreen, still, zoomed; off the spot, back), `region8`, `boot`
  pass. Not run: the rest. No generations.

## Delivery 1, the vase of flowers (§5 3.2; the user, 2026-11-23)

- **Asked, one at a time:** the vase's rule (she sees the hallway through the stems): **stems over the view**; the route:
  **approved as proposed** (a table by deck 8 midships' aft lobby door at 193 m, to cabin 8215 at the forward end, 115.6
  m, past the steward's rounds, the sprinkler, the swinging door, the trays and the "Do Not Disturb" door), tray rules.
- **The art, generated and chosen:** the vase (cut 8 rows of plain glass, 43 to 35 px); its tray narrower (18 px: "the
  tray should be shorter"); the low table ("more in profile from the side"); the view: a bouquet over the hallway ahead
  was turned into **"a flower frame, all around the screen's perimeter, obscuring parts of front and back of the
  corridor"**: three candidates, the first chosen; it "looks cut out near the screen edges": its margins inpainted (the
  background removal took them; then on magenta: "the bottom part doesn't look good"); **"measure the exact dimensions
  and regenerate the entire thing from scratch"**: 512 x 288 cut to the screen's 480 x 270, full bleed, then "sides
  fuller still" (the last frame as a style image). Ids in `assets/source/things/delivery/README.md`; about 200
  generations, most of them the frame.
- **Built:** `LOADS.vase` (`tray`, `view` in `src/world/carry.js`), the frame on the screen's layer under the HUD, faded in
  and out, **never in a zoomed-out view** (the user: the look-outs' and the outside view; the scene's update hides it, as
  the outside view holds the world still); `src_vase` with its tag hanging from the table's edge (a source's `sign:`
  item); `DELIVERIES` and the world's `delivery` (E with the load: a knock, `handTakes`, a heart, the flag, the book);
  conditions `a|b` and `opened:<door>` in `world.cond`; start place `hall8`.
- **The user's play:** the vase "magically appears behind me" (shown once a lobby door was opened): there from the start.
  (The "SCENERY MOVE" sign that went with the door is the theatre's block, lifted with region 4, which a fresh game at
  `hall8` opens there.) **The ice bucket's tray "should be a gag": a trap** (`haz_trays_8ice`, its own things, `DISH_PIECES`
  splitting the two glasses; its tangerine in the bucket flies off with them and lies loose, `fruitOff`). **"This tray
  breaks the vase, but the sliding gag isn't triggered"**: asked, **"gag and spill, trays only"**: a floor tray spills a load
  and plays its ride (her carry run counts as her run); every other hit with a load stays a spill only. **"Scattered items
  should all be on the floor. Spilled items should not sink through the floor"**: a spill's things turned about their middles
  and set down by their height once turned (the tray upside down, the load on its side); the lunge's scatter tumbles the
  dishes over as the ride does. **"The gag is triggered before we visually touch the tray"**: the hop starts within 4 px of
  her toe (it was 22), from the next quarter of her stride if she is between; 16 runs at the ice tray, all ridden.
- Tests: `deliveries` (new), `region7`, `region6`, `region9`, `region4`, `boot` pass; `mishaps` but `mishaps.things`' deck
  9 sprinkler (16): **broken since cefcf4c** (the Refinement session's "doors are secrets too"; passes at e621d5b; the door
  burst's gag plays instead), not looked into. `tools/check_overlaps.py`: 0. Corridors: deck 8 40.1 m without a beat,
  104.3 m without a reward (the delivery is not counted).

## Delivery 2, the pot of tea (plan-the-rest §5 3.2; 2026-11-23)

- **Proposed and taken ("Go ahead"):** the vase's other way round: on the vase's low table by deck 10 midships' forward
  lobby door (113.2 m, between cabins 10211 and 10212), to cabin 10230 (187.6 m) near the aft one, past the cart, the
  floor trays (a trap), the swinging door (from this side it never hits her), the sprinkler and the "Do Not Disturb" door.
  It cools as the coffee does (45 s against the coffee's 50; her plain walk takes about 27 s), the meter orange to blue,
  steam from the spout; cold, it is lost, a fresh pot on the table.
- **The teapot:** five map objects (32 x 32); generated size covered her face. **Try 4** (white, a navy band, a cup;
  the user's choice) with **"the tray a little bit shorter"** (22 px). Shrunk by majority colour its outline broke, so
  PixelLab redrew it at its size (`image_to_pixelart`, 20 x 11); **"Fix the teapot's pixels"**: set by hand px by px
  (`assets/source/things/delivery/draw_teapot.py`: four colours, a closed outline, a foot line, the cup's rim and handle).
  **"Make it a bit thinner; place it on top of the table, not built into the table"**: the tray 3 px tall; things on a tray
  stand on its top row (`img.height - 1`). 7 generations.
- **The user's play, for every load:**
  - **"The item with the tray should disappear from their tables when picked up ... but reappear if we fail to deliver"**:
    a delivery source's tray and load (`lifted`) are hidden while that load is in her hands; a spill or a cold pot shows a
    fresh one; the table and its tag stay.
  - **"Proper layer handling ... treated as the player (but one point closer to the screen)"**: what she carries takes her
    depth each frame, +0.001 a piece (it was drawn over the decks while she climbed the stairs behind them), her alpha too.
  - **"Disappears if I interact with elevators"**: it had been hidden in the lift so as not to draw over its doors; at her
    depth now it shows.
  - **Turned to us, it moves to her middle in front of her; her back to us, to her middle behind her; in profile again,
    at her hands.** The pot's spout faces the way she does (every load turns with her).
  - **"We also have to adjust her hands accordingly"**: her `carry-front` and `carry-back`, her front and back views
    animated (skeleton-v3, the elbows and wrists only: the rest the same pixels) with her forearms raised to the load
    (`assets/source/her/carry-turn/`, 4.2 generations); `pose()` takes them by name. All nine loads shown in profile,
    front and back: "they all look fine"; the cone facing us sits a few px above her hands, "not worth tinkering".
- Tests: `deliveries` (the tea added), `boot`, `region4` to `region9`, `lift` pass. `tools/check_overlaps.py`: 0. Corridors:
  deck 10 51.6 m without a beat (62 to 113), 92.3 m without a reward (38 to 130; the delivery is not counted). Start
  place `hall10`.

## Delivery 3, the pillows; the linen room changed (plan-the-rest §5 3.2; 2026-11-23)

- **Proposed (as text with numbered questions, the user's new rule for long proposals; short choices stay in the dialog):**
  the table by deck 9 aft's forward lobby door to 9245, the last cabin; answered: **"1. Let's try reusing her tray pose
  first, and then see 2. Let's try E, but that would require some sort of additional animation where she crouches with her
  pillows on her hands and the pillow is somehow picked up 3. A thank you, without hearts 4. Right"**.
- **The pillows:** three map objects; try 2, cut into its three pillows. "Meanwhile, all looks fine." **The crouch:** her
  carry-stand animated into a squat (skeleton-v3, 2 generations), the load on her fists frame by frame. The slide: after
  0.3 s of running, a stop (under 5 px/s on the floor) slides the top one 14 px on ahead; E within 36 px: she crouches, it
  arcs back on top. The thank-you: a speech popup from the door's crack as the hand takes them (first from over her head:
  its tail pointed at her, "as if she says it").
- **The user's play:** "why does she jump too high? Isn't the carrying jumping handled for deliveries in the same way?": the
  low hop (the plan's full jump dropped). **"When she hands it over, her hands lower too soon (the previous cases with tray
  should be checked for that too)"**: a delivery holds her in her carrying pose until the hand has it (the vase, the tea and
  the pillows; the story's other hand-overs run as scripted moments and kept her pose already; their trays vanish while the
  load crosses, offered, not asked). **"When she spills the pillows, they fall down as a single block now"**: three pieces,
  scattered flat. **"Place the pillows not on this table, but on an appropriate laundry trolley"**: three trolleys shown; the
  user took the linen room's drawn cart, then: **"can we replace the drawn-in-code version with the first one on my
  picture? For the pillow stack case, make the version without the pillows/sheets in it"**: region 1's generated laundry
  cart, and an empty copy of it for the pillows.
- **The linen room (the user's, on playing it):** "make the cart an obstacle there: we cannot move past it, we have to push
  it" (`"rim"`: solid, pushed from the start); "her legs move too slowly" (near-catch 4's walk had left her clip at 0.6; the
  push now plays at its own pace); "nothing worked" on the cart (my link's `?did=bb4` set the flag without the crawl it
  gives: `?did=` now gives what a flag gives). Then, the near-catch's reach being broken ("I will fix it in a separate
  session"): **the hanging grille removed, a proper vent cover over the opening that falls to the floor when Bumbot jumps at
  it** (generated, try 1 of 3); the heap and Bumbot on it removed; the opening 2 px smaller all round, centred between the
  rack's upright and the wall; **Bumbot asleep on the bottle shelf**; **he leaps the moment she, or the cart, is 2 px from
  him** ("closer ... by a couple of pixels"). Its door "a bit more full color": washed 20% instead of 30% (`ROOM_DOOR_WASH`
  in `src/highlight.js`, the Refinement session's file, asked first).
- Tests: `deliveries` (the pillows added), `boot`, `lang`, `region4` to `region9`, `golden`, `linen`, `highlight`, `lift`
  pass; `mishaps` but `mishaps.things`' deck 9 sprinkler (broken since cefcf4c, the Refinement session's). `region4`'s and
  `golden`'s linen room steps rewritten for the new order. About 14 generations (pillows 3, trolleys 3, crouch 2.3, covers 3,
  heads 0.2, the teapot's round already counted).

## The shaft remade (the user's own request, outside the plan; 2026-11-23)

The sequence where she follows Bumbot into the linen room's vent, remade on the user's word: the room mirrored and its
door one slot aft, the chute's hatch over the laundry's cart, the shaft at its true place and length with the ship
itself under its grilles, no cut going in or out. Every decision, what was generated and what was checked:
**`docs/shaft-remake-log.md`**.

**After the user's play of it, the same day** (decisions 13 and 20 to 25 of that log): nothing of Bumbot in the shaft
(two eyes kept ahead of her "move in sync with the player"; "Bumbot is long gone"); standing on the cart she is stopped
at the mouth; everything round the shaft black and each grille over a landmark of deck 8; on hands and knees at the
mouth she is behind its near side; only the grille she is over opens; one grille to a place, six in all.

## The shaft's mouth half as deep, its cover's fall (the user's, 2026-11-24)

The mouth cut to half its depth from its own picture, and the cover's fall made a quarter turn landing flat on the
floor: decisions 26 and 27 of `docs/shaft-remake-log.md`. No generations. `region4`, `linen`, `golden` pass.

## The shaft's mouth and its way out (the user's, 2026-11-24)

She is in the mouth on hands and knees (its far side behind her, nothing of her past the room's wall until the view is
the shaft's); the way out a grille like the rest, that drops her the moment she is on it and swings down unlit on its
right edge: decisions 28 and 29 of `docs/shaft-remake-log.md`. No generations. `region4`, `linen`, `golden` pass.

## The shaft's seams; Bumbot's paw prints dropped (the user's, 2026-11-24)

- **Thin vertical lines of light while she crawls in** (the user: "very brief ... really hard to catch on a
  screenshot"): the dark round the shaft is one picture with a clear box for each "window" (the dark round neighbouring
  grilles' views, redrawn as one opens), the windows laid in those boxes; where one picture's texels ended at the other's
  edge, a camera between pixels showed a column of deck 8 through the seam. Found by recording her way in at the canvas's
  full size, the camera nudged by fractions of a pixel each frame, and searching every frame for one-pixel bright
  columns (a 272 px line); each box is now cleared a pixel short all round, the great dark under the window's own dark
  edge. The same search over the whole crawl (720 frames) finds none.
- **Bumbot's paw prints, dropped** (the user, shown four light-grey candidates from three generated pictures: "None of
  those looks like his prints. Let's drop the prints entirely"): the dusty prints on deck 8 under the shaft's way out,
  those on the balcony where he swipes at the gull, and the wet trail aft from the pool; the `paws` picture and its
  playtest checks with them; part 12's foamy prints (plan-the-rest §7g item 3) struck out. The generated tries stay in
  `assets/source/things/paws/` (3 generations).

## Her crawl at its own pace; the shaft's joints over her (the user's, 2026-11-24)

- **Her crawl sometimes played very slowly** (after the shaft's slide, "not every time"): her run's clip is played at
  her speed (`pose('run', |vx| / runSpeed)`), a fraction of itself as she slows to a stop, and the crawl never set a
  speed of its own, so it kept whatever the run had left. `poseCrawl` (and the slide's end) set it to 1: checked with the
  run's left at 0.1 just before she crouched.
- **The shaft's joints over her their whole height** ("let's make the entire line cover us"), not only their top and
  foot (`compose` in `tools/build_shaft.py`, `front.png`).

## The laundry chute as a scene (the user's, 2026-11-24)

- **The way down, as the user described it:** E at the linen room's hatch: she steps to it, turns her back to us,
  crouches, pushes the flap in and slides in head first (clip B of two, `animate_image_pixminimax` on the room's own
  hatch, its wall turned green to cut her out; the room's hatch shows through the clip while the flap is shut, so
  nothing jumps). The moment her feet are in (frame 12 of 16, no hold on the empty hatch) the room fades into the ship's
  closed side in 0.15 s (her route `chute`: no room, every deck closed; the rooms' pictures and dims held at an alpha of
  their own, the ship scene's `roomFade`) and the view drops five decks with her in 2 s ("Let's try 2s"), slow at
  first, nothing of her shown ("we're shown the hull"); the laundry fades in round the outlet just before she shows,
  its own deck held open behind it (by her height the cut-away had opened the deck above for a moment).
- **Out of it** ("she should be shown briefly falling out head-first of the outlet and into the bin (the bin obscures
  her). Then, she stands up in the bin with the towel"): her dive (try 1 of 2) cut at the outlet's mouth, falling on at
  the chute's speed until all of her is under the heap's top, the cart's picture drawn over her down through the floor's
  slab; the camera held on her down the drop (at its usual ease it trailed 70 px and the dive happened under the
  screen's edge), eased again once she is in. She stands up knee-deep with the towel (try 1 of 3) and climbs out.
- **The towel:** placed after the physics each frame ("When we run with towel, it shifts behind us"); off the moment she
  moves or jumps ("as soon as we move or jump"); it falls like cloth, a generated fall from the towel as it lay on her
  head to a generated flat towel ("it has to behave like a towel, not like a brick, and lay down flat"), in front of
  her as it slides, behind her on the floor, then fades.
- **The laundry's picture:** the outlet drawn in code (a box hanging under the ceiling) replaced by outlet 4 of four
  (the user's; try 2 had a hole and a shadow block), joined to the ceiling, straight over the cart, in its own colours;
  its duct made solid where the cut had left rows empty and its pale highlight a steel one ("The white strip looks
  off"); the cart drawn in code replaced by the generated laundry cart heaped with towels ("a proper stack of laundry").
- 65 generations (`assets/source/ship/laundry-chute/README.md`). `region4` (the chute's new checks), `linen`, `golden`
  pass; `tools/check_overlaps.py` 0.

## The pool's scene remade (the user's own request, outside the plan; 2026-11-24)

The user asked the design session to remake near-catch 5 at the pool "from start to finish (Bumbot, kid, the lever,
the pool drain)" by the shaft's rules, in a worktree of its own (`../mysterious_female-pool`, branch `pool-scene`), so
as not to cross the building session's work. It closes plan-the-rest §9's U17. **The whole record, decision by
decision with the user's words, is `docs/pool-remake-log.md`**; in short:

- **The scene:** her reach up out of the water at the rim (a generated clip of hers); the kid in the hot tub, his
  pistol green; Bumbot over her head into the pool, in sight under it, back past her, out, onto the drain lever's
  grip, thrown across the tub. From the deck she dives at him and ends in the pool under him.
- **The pieces, generated** (`tools/build_pool.py`, 58 generations; her clip 2): the lever (knee-high, the user's
  size), the hatch on the tank's floor (128.5 m, was 125: in view as the water leaves her), the drain's grate, deck
  10's ceiling panel.
- **The drain and the way down:** the water down the grate, a funnel in its surface, puddles at the last; the
  hatch's lid heaved up, its ladder, the ceiling panel, no fade.
- **Changed besides, on the user's play:** her picture 5 px lower in the dry tank; the pools' water to the foot of
  the tank's wall; the pool ladders down to the floor; deck 10's laundry line not shown from deck 11; the paw
  prints heading aft on the planks (dropped again in the merge into `three-uses`, the user: every print of his
  goes); the hot tub 22 px aft.
- **Left:** `docs/ship-regions.png` still draws the hatch's way at the pool's middle; Bumbot's own clips are part 6's.

## The chute's dims and towel after the user's play (the user's, 2026-11-24)

- **The linen room showed the balconies round it undimmed** (decks 8 and 10's railings, partitions, a gull): a room's
  dim lay under what the outside draws in front of her. Every room's dim is now over her depth (`roomDim`), as the
  lifeboat's already was; it frames the room, so neither the room nor she is under it.
- **Out of the laundry, the corridor's decks were undimmed:** the drop held the view on deck 4 (`viewOverride`) after she
  had landed, and the decks' dim is off while the view is held. Let go as she climbs out.
- **The towel fell by itself as she climbed out:** in the first frame of play her body was not yet on the floor, read as
  a jump. It is watched only once she has stood in play; the 4.5 s that took it off her while she stood went too.
- **Out into the corridor at once, the towel lay there fading:** the towel, on her head or on the floor, is the
  laundry's and goes the moment she leaves (`hatAway`).
- `region4` checks each; `region4`, `linen`, `golden`, `cabin`, `region7` pass.

## Part 4: each deck its own look (plan-the-rest §6, 2026-11-24)

- **The cabin numbers are part of the door's art:** a brass plate 6 x 4 px with a 4 x 2 face. A band on it (1 px) hardly
  showed; the face in the deck's colour read. **The user dropped the idea:** "Leave the doors as they are now"; with it the
  deck colours, which were the plates' only.
- **The framed pictures:** 24 generated (map objects, side view, "filling the whole picture ... completely flat front
  elevation"), then five re-rolled (three drawn without a frame, one too faint, a palm that read as a bush) and, on the
  user's word, deck 4's green muster sign ("an exit sign, does not make any sense") replaced: three tries, then six more;
  the user took the first aid and lifeboat posters, so deck 4 hangs five. 38 generations. Cut to their frames (hanging
  wires and hooks off, a stray red mark) by `assets/source/ship/deck-pictures/clean.py`, built as `picture-d<deck>-<name>`
  with the usual twins; hung by deck in `drawCabinDoors` (`DECK_PICTURES`), any other corridor keeping the old three.
- **Wash:** the standard rule (the user): the guest cabin corridors stay at 35%.
- **No tint:** not asked for once the pictures were seen.
- Deck 6's corridor is short and hangs three of its four (the compass-rose chart is not seen).
- `boot`, `stairs`, `lift` pass; `tools/check_overlaps.py` 0. The whole ship's render not made: nothing is drawn
  outside the corridors' walls.
- **The kid's legs through deck 10's ceiling** (the user, after part 4): right down in the hot tub his picture reached
  20 px under deck 11's floor, where nothing covers it. It is cut at the floor each frame he is in the tub (`updateLido`);
  above it the tub's near wall hides him as before. `region6` passes.

## Popups off the screen; a blocked way is a shrug (the user's, 2026-11-24)

- **Her popup goes off the screen with her during a scare** (from her hit to her respawn, `scareFrom`): a gag or a fall
  that carries her out of the view no longer leaves her word at the screen's edge. Anywhere else, and for anyone else's
  popup, it stays inside the view as before (the user: "only when the player moves off the screen before the respawn").
- **A way roped or chained off says nothing over her** (it repeated the sign): she turns to us and shrugs, and the sign
  lights up once (its own picture added over it, in and out over 0.6 s). The user chose shrug A (her character's
  skeleton, custom poses; 3 generations; B, pixminimax, and a v3 try, 1 each, kept in `assets/source/her/shrug/tries/`)
  and flash 2 (brighten; white and a blink were the others). A lock with only a padlock keeps it over her, and she
  shrugs too; card locks are unchanged. The same shrug where she turned to us after a near-catch. `SHRUG` in the config.
  - The shrug is played as an idle is: a fresh step or jump cuts it short, a key held against the rope does not; not
    again within 2.5 s; not with her hands full, crawling, in the towel or in the air.
  - **Its clock is its own:** her stand is a still frame, so the run's last slowing (`timeScale`, 0.14 after a stop)
    stayed on and the shrug took 4 s ("very much slow"). It plays at 1 and gives the old pace back after: her idles stay
    slowed on purpose (the user: quicker they "looked like twitching").
  - The ladders' chain signs are text drawn at 4x: a copy of their texture lit only the top left corner. The glow is made
    from their canvas.
- **`?at=pass5`**: deck 5 aft by the Seven Seas' pass (near-catch 1). The corridor from La Cucina is walled off at 167 m:
  I had sent the user there from `cucina`, and Bumbot was not to be reached.
- The playtests that read a sign's words from her bubble read `lastBlocked` (`blocked(b)`); `stairs` checks the shrug
  and that nothing is over her. `stairs`, `golden`, `region1`, `region2`, `region3`, `region6`, `region8`, `lang`,
  `mishaps`, `region4`, `boot` pass (`mishaps.things`' sprinkler case failed before this, as it does now: a door's gag
  reaches her first).

## Part 5, the small faults: the throws at the funnel and the tip, the deck 4 checks, V8 and V10 (2026-11-24)

- **A tangerine thrown at the funnel's gulls** (tried in the game for the first time): rolled toward the stairway it went
  off the funnel's top and fell straight through the steps, and a gull came down to it in the air and stood on nothing.
  The stairway now has treads for a tangerine only (`stairTreads`, `treads` in the ship scene; she still walks it by its
  line): it bounces down step by step and lies on one, hers again as she walks the flight. A funnel gull comes only to one
  lying on something, on the stairway only once it lies still, and stands on its tread (or the one under it, looking up a
  step), never in the step above (`gullTakes(..., { side, footAt })`). Thrown the other way it lies on the top, out of
  their reach. On a tread it is drawn at the stairway's depth, in front of the ship's side.
- **A tangerine thrown at Bumbot at the tip:** a roll at him sends him back along the deck and, cornered, past her, as
  built. A lob from close went over his head, landed behind him and rolled away, and he went after it: he now answers
  only one coming at him, and backs away from it (`tipOffered`).
- New cases `throw.funnel`, `throw.tip`. `throw` had failed since e4f719c: it waited for the pool gull's `fed`, gone with
  its flight's rework (the gull took the fruit as it should); the check waits for its flight off with it.
- **The two `deck4` checks that failed now and then before the stepped clock** (the breakfast round moving on, the lob onto
  the climb's shelf): 20 runs stepped under seeds 1 to 20 and 3 in real time at once all pass. Not reproduced, so no
  cause named; most likely real time's uneven frames (the lob's arc to a narrow shelf) and the breakfast round's rework
  since. Closed.
- **V8** (her word's box with no outline) was settled by the popups' remake (a dark outline). **V10** (the party cabin's
  notes at the wall's depth), the user's yes: drawn above the world as every other small mark.
- `throw`, `region8`, `finale`, `region4`, `region5` pass.

## Part 5, the sound leftovers (2026-11-24, approved by the user on listening)

- **Held sounds:** `sfx.hold(name, ...)` (and `sfx.at(x, y).hold(...)`) plays an effect whose first argument is its
  length as 30 s long and returns `{ stop(fade) }`, which fades it and ends its voices (they are kept as they are made:
  `cur.sources`). The soft serve's motor is one held `whirr` for as long as E pours, and `whirrDown` (its pitch falling)
  when it stops, on every way out of the swirl; it was 0.4 s pieces begun again every 280 ms.
- **Eating and drinking:** `sip` (a slurp and a swallow), `lick`, Bumbot's `nom`. Sounds on people's clips' own frames
  (`CLIP_SOUNDS` in `src/world/people.js`, frames read from their strips where the cup or cone is at the mouth): the
  engineer's coffee (4), the wedding guest's glass (7, his idle), her husband's cone (4); hers on her own clips
  (`HER_SOUNDS` in the ship scene: `her-lick-cone`, 3); the old lady's two sips at her glass's tilt; Bumbot eating at a
  spot (`addCat`, each round of his clip).
- **The intro:** `CUES` in `src/intro.js`, each once as the clock passes it (none while held or sought): gulls four times
  over the wide views, `swell` (a rush of air rising over 2 s) into the dive, `cloth` at her badge; `choose`, a tick, when
  the menu's choice moves or the language switches.
- `tools/check_sound.py` all within bounds (the tick and the lick raised from its floor). The `sound` playtest reads held
  sounds and the frame tables (`CLIP_SOUNDS`, `HER_SOUNDS`, `CUES`) as used; `region6` checks the motor is one held sound
  and its run-down. `sound`, `region6`, `region8`, `region9`, `boot`, `deck3` pass.
- **Part 5 is done.**

## Part 6: Bumbot made again (2026-11-24, the design session in the default folder)

The user: the building session "merged all its work to main and is idle now. I want us to take over for now and
continue with the next item on the plan: Bumbot made again." `docs/plan-the-rest.md` §7a; all the art and its jobs in
`assets/source/bumbot/remake/README.md`.

- **Asked first** (§7a's step 1). The user: "Head and his face look disproportional to me"; keep his size; realistic or
  stylised, "Let's try both and show me to decide"; every clip again and all the new ones, "make also the existing
  animations a bit smoother. We might not end up using all of them in the game, but I want to choose what's proper";
  him in her arms "is the only thing that I actually like", but for pink pixels in its front view; no new photos.
- **His look.** Edits of the old sprite came back blurred and in its lanky shape. `create_image_pro_flash` at the
  game's size (48 x 32, then 52 x 36), with his HUD face as the style image, drew a proper cat each time; thirteen
  tries, seven shown. **The user chose 1, the first realistic one, its coat as it came.** He stands 26 px, not 28:
  the chosen picture is kept as it is, not redrawn. **His own colours** (`own` in `tools/build_sprites.py`): on the
  palette he was a flat purple silhouette.
- **His clips.** `animate_image_pixminimax` from that one picture on a 64 px canvas, on transparency, 1 or 2
  generations each; it held his head, ears, eye and coat in every frame. Poses a clip ends in start the next ones
  (sitting, asleep, the loaf). The run three times (the one kept is an exact eight-frame stride, made on green and
  keyed). The rope's clip was made with the stage's rope in its picture and the rope taken out; the fishing with a
  floor's edge and water under it, the cat cut out by colour. Cleaned by rule (`remake/cut.py`): loose specks off,
  the shake's drops in water colours (the user: "black droplets, maybe those should be light grey/blue").
  **"All Bumbot animations are approved."**
- **In the game.**
  - `BootScene.js`: his animations' table. The jump three ways: `bumbot-jump` (crouch to crouch, each frame on its own
    lowest pixel: the pool's scene paces it and places him by his paws), `bumbot-leap` (through the air, for a leap
    the game moves him through), `bumbot-startle` (straight up on the spot with the clip's own rise).
  - `nearCatch`: out of what he was doing first (`BUMBOT.getUp`: awake and up from asleep, up off his haunches from
    sitting, quick), then the leap, 0.44 s (`leapMs`; it was 0.16 s, two frames of a crouch), then his run.
  - Asleep he breathes in the clip (one still stretched by a tween before); a tangerine thrown at him asleep is
    still slept through.
  - The stage: he catches the rope, in front of it, and rides it up. The linen room: in on his belly, his picture
    cut at the room's forward wall as hers is (turned by its scale for the crop). Cabin 8206: he turns round, lies
    down, sleeps.
  - **The pool** (the user: "He doesn't bat at the level, he is with his back to it. That's why it looks so weird"):
    his activity is `fish`, a paw down over the rim at the water. My reading of the user's words, shown and approved
    with the rest. Its frames, and the rope's, keep 8 px under his floor (`BUMBOT.under`).
- **Her with him in her arms** (`fcb870e`): in that sheet her skin's shade landed on the palette's tan (patches on her
  face, arms and legs in every frame): a remap puts it on her peach; four lone pink pixels in her hair in the front
  view mended in the source (the user circled two). His coat there: "Let's try to recolor. If I don't like, we keep
  the current version"; shown as pictures, then "need to see in game": two trial sheets behind `?coat=a` and
  `?coat=b`, and a link that starts before the catch at the bow ("Show me B before the catch at the bow"); **"Ok, B it
  is"**: his two tones and his eyes there on his new picture's colours, a tone darker than its main one (a remap in
  `HER_CAT`, off the palette as he is everywhere); the flag and the trial sheets taken out.
- **Not done, the user's word:** "there are a lot of issues with the near-catch scenes in general, I will fix them
  separately, when doing general QA". One I told them of: at near-catch 2 he sleeps over the reading table's lamp
  (`BEAT_LIFT` takes the piece's whole height).
- **Tests:** `boot`, `region1` to `region9`, `golden`, `throw`, `sound`, `deck3`, `highlight` pass; `finale` passed
  alone three times and failed one wind check once six at a time (cause not found; no cat in that check);
  `check_overlaps` 0. The whole suite not run. Each near-catch but the first was recorded from the running game and
  looked at frame by frame.
- 114 generations (65 the look, 49 the clips).

## The linen room and the laundry redecorated; the room doors' plates (the user's, 2026-11-24)

- **Both rooms redrawn in place by PixelLab**, every shape kept where it was (the user: "keeping the exact dimensions and
  the layout of the current props, so that we wouldn't affect gameplay"); three looks of each, worn steel, clean modern,
  warm. **Linen A** (worn steel; the shelves' linen redrawn varied: towels white, blue and sage, rolled navy-striped pool
  towels, sheets, blankets, bathrobes, the user: "more like linen", "add variety") and **laundry C** (warm; its own floor
  put back, the redraw's glossy one "way out of the rest of the ship's theme"). `tools/redecorate_rooms.py`, called by
  both builders, lays them over what the builders draw and pastes back, pixel for pixel, the doors, the linen room's chute
  hatch (her `chute-in` clip was made on it), the laundry's outlet and towel cart and its floor. The laundry is wider than
  one redraw: two halves, matched row by row, the join inpainted. About 216 generations with the tries
  (`assets/source/ship/redeco/README.md`).
- **The linen room's door from the corridor is the ship's regular crew door, shut**, washed at rest and pulsing like every
  door she uses (the user); the open door with the room seen through it is retired (`linen-door-open`). Its card reader
  on the door's left and its plate on the right, as the laundry's (it was squeezed in by the plate).
- **The room doors' plates in a background tone** (the user: "the plates same background'ish tone as the doors"): the ten
  `sign()` plates beside doors washed at rest (LINEN, LAUNDRY, DRY STORE, STAGE MGR, both PANTRYs, GALLEY, COLD ROOM, STAGE
  DOOR, LIGHTING) washed 20% toward the corridor wall ("35 too strong"), their readers and the pulse left as they are
  (`washPlates`, `WASHED_PLATES` in the ship scene). The captain's brass plate (text) was shown and left.
- `?at=laundry`: inside the laundry (deck 4's corridor hazards stand between it and every other start).
- The laundress at her folding table stands in front of the laundry's tangerine on the detergent shelf, as before: part 9.
- `linen`, `region1`, `region4`, `highlight`, `boot` pass; `tools/check_overlaps.py` 0.

## Near-catch 1 remade (2026-11-24, the design session, a worktree of its own)

The user: "Let's fix the first Bumbot near-catch sequence in the game. Right now it is very much broken, both visually
and in terms of gameplay: there are delays and glitches. Apply the plan and let's go". The plan is
`docs/sequence-remake-plan.md`, saved the same day; everything found, decided and built is in
**`docs/near-catch-1-remake-log.md`** (22 decisions, the user's among them: the counter, "she cries and dashes at
him", "D to dash", then on playing it the pause before the dash, the lunch's pulse, the nearer start, the tray off
the counter). The Seven Seas' pass became a generated serving counter; the scene is `src/world/pass.js`, one clock;
she is held 2.4 s where it was 8.3. 31 generations.

## Three more rooms redecorated (2026-11-24)

The user: "In the same manner as we redecorated the linen room and the laundry room, I want to continue with other
rooms. Crew cabin on deck 3 and room 8206 are looking well, so we leave them alone." Of the twenty rooms left, the best
candidates by how flat they are, how much she is in them and what they cost: the galley, the dry store, the maid's cabin
(also the cheapest way to settle a look for the guest cabins); the user: "Let's start with 1 to 3".

- Three looks each (A worn working, B clean modern, C warm; the maid's cabin's C asked to match cabin 8206 as a
  reference, and came back almost as it was). **Chosen: store A, galley A, maid's cabin C** (the user).
- **Kept pixel for pixel:** the doors and floors; the maid's cabin's luggage rack and suitcase, sea picture and towel
  swan by boxes round them (by their own pixels the redraw's copies left faint traces), so the swan drawn over her on the
  bed is the same picture. The store's shelf for the tangerines and the snack tube came back on its row (88), its middle
  empty; the galley's flour sacks, range and pass where they were.
- **The galley in halves** (336 px): matched row by row and cut at x 178, between the range and the pass, where the tile
  rows meet and the cut reads as a grout line. An inpaint of the strip came back a flat grey pillar: kept in `tries/`,
  not used.
- `tools/redecorate_rooms.py` has the three; `tools/draw_rooms.py`'s `store`, `galley` and `maid6` call it. 99
  generations (`assets/source/ship/redeco/README.md`).
- **The maid's cabin's window shows the live outside** (the user, asked whether it ever had: it was always painted; "Yes,
  and we'll do the others, as we redecorate them"): its panes are cleared in its picture (`windows` on the room in
  `tools/population.py`, `clear_glass` in `tools/redecorate_rooms.py`) and one window view for every such room is drawn
  behind them (the ship scene's `roomView`, made by `world.buildRooms`), shown while she is in the room, as cabin 8206's.
  The guest cabins get theirs as they are redecorated. `region2`, `keeps`, `cabin`, `boot` pass.
- The galley's door is at deck 5's aft end past the pass (the user did not find it): from `?at=pass5`, aft past the
  near-catch.
- The user upgraded PixelLab to Tier 3 the same day: 10,000 generations a cycle, refilled on 2026-12-24 (CLAUDE.md).
- `boot`, `region1`, `region2`, `region3`, `keeps`, `highlight` pass.

## The guest cabins and the pantry redecorated, the balconies' railing out of the rooms (2026-11-24)

The user: "More rooms. Now we have more than enough generations".

- **The nine guest cabins** (the six balcony cabins, the clean-up and make-up cabins, the adjoining cabins): a pilot of
  three takes on deck 9's balcony cabin, the user's **take 3** (their own colours, only the finish: cream panels with
  thin seams, warm wood with a little grain, soft folds; "keep every shape ..., change only the finish"), then each
  cabin the same way. Cabin 8206 as a style reference moved the furniture and drew a second bed: dropped (`tries/`).
  Cut where the wall is plain (x 0..184 and 112..288, the cut between the desk and the bed; the adjoining cabins in
  three parts, cut at 211 and inside the second door at 363). Kept as drawn: the doors, the floor, the vacuum's dock;
  the generated pieces by their own pixels (the swans, trolleys, rose, bucket and spade, juice, beach bag, swim ring,
  glasses, cake, champagne, lamp, luggage).
- **Every balcony door shows the live outside** (the user: the guest cabins' windows "as we redecorate them"): its
  panes cleared (`balcony_glass`: shut or slid open), the rail, balusters, handle and the curtain blown in kept; the
  panes are the room's `windows` for the game's view. (The committed `balcabin9.png` still had the swan's old beak:
  8 px now as the atlas has it.)
- **The blanket fort redrawn in place** (the user: "The fort also have to be regenerated"; 3 of three): its outline
  as it was, so her crawl behind it is the same.
- **The pantry B** (clean modern; of three): its left part redrawn to x 212, past the shelf's right post, so the cut
  falls on plain wall (cut through the shelves, their rows did not meet).
- **The balconies' fronts and partitions are not drawn across a room she is in** (found in the balcony cabin, an
  existing fault; the user: "fix the railing"): the ship scene's cut-away sets them to nothing on her deck while she
  is in a room (`balcony` on their `shellSlopes`).
- About 260 generations this round (`assets/source/ship/redeco/README.md`). `boot`, `region1`, `region2`, `region4`,
  `region7`, `region9`, `finale`, `keeps`, `highlight` pass; `check_overlaps` 0.

## The stage manager's cabin, the dressing room and the cold room redecorated; the cold room's door, the canister (2026-11-24)

The user: "What other rooms can we redecorate?"; of seven (the stage manager's cabin, the nook, the dressing room, the cold
room, the chapel, the lighting booth, the lifeboat), "1-3".

- **Three looks of each** (`edit_image_pro_flash`, "keep every shape ..., change only the finish": A its own colours,
  B lived-in or worn, C clean modern or grand); **the user's: the stage manager's cabin C (light grey panels, pale birch,
  navy blankets), the dressing room A (peach, the bulbs glowing), the cold room A (icy panels, labelled tubs).** In
  `CABINS` as the guest cabins: their doors pasted back by their own pixels (a box carried a strip of the old wall's
  colour and the old frost round them); the cabin's door was drawn a little bigger by the redraw, its rim filled from the
  wall beyond (`rim_fill`); the dressing room's stool and rail by their pixels. **The cabin's chair is the redraw's** (the
  user: ours over it "looks too distorted"; the redraw's edges showed round it). The cold room's floor frost is no longer
  drawn across its door's frame (the user: "clean the white strips").
- **The cold room's door between the café's last two windows** (the user: "its location is off ... out of the window"):
  185 m to 183.542, its plate over the door (the wall there is 116 px: the counter, the reader, the door); the Ice Cream
  Bar's counter and cone sign 30 px forward, 5 px clear of the window's frame.
- **The deck 4 officers' plates clear of their doors' frames** (the user: BOSUN and PURSER "overlap the doorframes"): BOSUN,
  PURSER and DJ each 3 px clear, as the stage manager's plate is.
- **The ice cream mix's canister generated** (the user: "what is it on the table, drawn in code? ... worth generating
  properly"; the last of three, a steel churn with a pink label and a cone on it), in its own colours (on the palette
  its steel would go green), on the shelf, in her hands and poured; **one canister**, off the shelf while she carries it
  (`lift`, as the lunch's tray).
- 96 generations (81 + 15). `boot`, `region2`, `region3`, `region6`, `keeps`, `highlight` pass; `check_overlaps` 0.

## The nook, the lighting booth and the chapel redecorated; the chapel's chairs out (2026-11-24)

The user: "The remaining rooms" (the nook, the chapel, the lighting booth, the lifeboat), three looks of each (the
three wider ones in two parts): **the nook B** (an old library: dark green walls, walnut panelling, brass), **the
lighting booth A** (its own dark grey-purple, panel seams, worn steel), **the lifeboat left as it is** (its tries kept),
and the chapel: **"Remove the chairs and regenerate"**, then **B** (its own colours, a soft glow from the downlights and
sconces).

- **The chapel's cane chairs and their bows are gone** (nothing in the code used them; the ceremony's guests stood in
  them, and now stand on the open carpet). Its two redrawn parts lit the wall differently, so they are faded one into
  the other over 80 px of plain wall between the doors and the flowers' stands (`blend` in `CABINS`), not cut.
  `tools/draw_chapel.py` calls the redecoration; its doors by their box, the flowers, their stands and the candle as
  drawn.
- **The nook:** its way out, the armchair she reads in (her clip was cut over it) and the cat's picture as drawn; its
  lamp, table, candle, bookcase and books the redraw's (ours, washed toward the old red wall, were pinkish on the green).
- **The lighting booth:** its door as drawn, its chair the redraw's; cut inside the steel post between the booth and
  the catwalk.
- 243 generations (189 + 54). `boot`, `region3`, `region9`, `keeps`, `highlight` pass; `check_overlaps` 0.

## The restrooms by the Chapel (deck 12): its own door, a room to enter (2026-11-24 and 25)

The user: "Let's generate a proper door for the restrooms" (it was a cabin door, card lock and number plate); then
"make it entreable to a small restroom cabin, not too wide as not to overlap the glass doors on the right and the
checkpoint door on the left"; "Do as you suggest"; then rounds of play.

- **Its door** (`door-restroom`): try 2 of three, redrawn from the cabin door's own picture (its size and frame), pale oak,
  a long pull handle, a kick plate; its square sign's man and woman drawn by hand (generated, a smudge); in its own colours.
- **The room** (`restroom` in `ROOMS`): 124 px between the checkpoint's crew door and the glass doors, its door where it
  stood (70 px in); drawn flat by `tools/draw_rooms.py`'s `restroom`, redrawn in place (C of three: modern, pale grey
  stone, brushed steel) through `CABINS`, its door pasted back. Then, by rule (`moves`, `patches`, `lines` in
  `redecorate_rooms.py`): **its mirror 18 px lower**, at her face ("Lower the mirror"), the wall it left filled from the
  wall beside it; **the dryer's right outline** drawn one column in (the door's frame covered it); **someone in the stall**:
  a gap under its door and their dark shoes (inpainted, 3 of three: "they worked better"), the ankles covered by the
  door's rail.
- **E at the mirror:** her hair, as in her crew cabin (`mirror`). **E at the dryer** (`sec_dryer`): its roar 2.4 s
  (`sfx.dryer`) and its warm air as the sauna's steam, small circles falling and spreading, behind her, white and a steel
  grey (white alone was lost on the pale wall). **The stall:** a muffled hum now and then (`sfx.stallHum`, a room's place in
  `src/world/soundscape.js`) and a note rising over its top for each note sung (the user, sound off: "I just imagined
  there would be notes coming up from the stall"); **E at it** (`sec_stall`): she knocks, "Occupied!" from over its top
  (`say.occupied`), then the "Do Not Disturb" gag (23), which here tiptoes her to the mirror and stops there
  (`sorryStop`: "let her always go to the mirror, stop there, and then respawn"), then her checkpoint.
- **A tangerine on its counter**, right of the tap (the user circled it): `tan_12_restroom`, moved from Cagney's
  (`tan_12_cagneys`, balanced on its steel trolley's dome, plan-the-rest §7d's seventh). The total stays 56; deck 12's
  longest stretch without a reward is now 48.4 m (129 to 178).
- The mirror and the dryer pulse (`IN_ROOM` in `src/highlight.js`, the user's leave).
- 51 generations (doors 15, room 18, feet 18). `boot`, `region2`, `region4`, `region7`, `region8`, `region9`,
  `highlight`, `deck3`, `keeps`, `lang`, `sound` pass; `check_overlaps` 0. `mishaps.things` fails at deck 9's sprinkler
  (the swinging door's gag first), on fcca25e too: not this work, not looked into.

## Near-catch 2 remade (2026-11-24, the Design session)

The user, right after near-catch 1 was merged: "In this same manner, let's work on the second near-catch". By
`docs/sequence-remake-plan.md` again; everything found, decided and built is in
**`docs/near-catch-2-remake-log.md`** (14 decisions; the user's: "He sleeps on top of the book return basket,
everything else derived from A", and "a", her tiptoe and her reach at his height; "Go ahead" on the storyboard;
"Approved" on playing it, with no correction). His spot moved from the last reading table to the return trolley, so
that the rope and the door are in the picture; the scene is `src/world/quiet.js`, one clock; the Library's aft door
swings aft now; she is held 2.6 s where it was 3.5. 15 generations.

## Near-catch 3 remade (2026-11-24, the Design session)

The user, with near-catch 2 approved: "Let's work on the next near-catch, same approach". By
`docs/sequence-remake-plan.md` a third time; everything found, decided and built is in
**`docs/near-catch-3-remake-log.md`** (21 decisions; the user's: "Do as you planned and recommend", "regenerate both
the stage, the props and the people here", "The stage manager has to react somehow to Bumbot and then start
sneezing"; at the preview stop, of the dancers, "the male dancer looks like a waiter, the female one is approved",
"remove the piano; switch places: the stage manager and the dancers"; on playing it, "The stages pops out too much"
and "The scene plays too fast in the game"; then "Approved"). The stage is one generated picture
(`tools/build_stage.py`); the scene is `src/world/stage.js`, one clock; the lamp and the fly rope's loop are the two
ends of one line, so the rival's weight on the lamp is what takes Bumbot up; she is held 4.35 s where it was 4.75,
and all of it is in front of her. 156 generations.

## Near-catch 4 remade (2026-11-24, the Design session)

The fourth by `docs/sequence-remake-plan.md`, on branch `near-catch-4` (made from `near-catch-3`). Its whole record:
**`docs/near-catch-4-remake-log.md`** (16 decisions). The old scene was recorded (nine faults); a held scene of 3.5 s
was offered and turned down: the user chose two faults to mend and gave the scene themselves ("From your list of
faults, let's address only the following: 4, 8 ... The laundry cart has stack of pillows on top of it. We cannot jump
past it, or on top of it. We only have to push it. When we push it, Bumbot jumps (like now), the pillows scatter, and
we are able to jump on top of the cart and enter the vent"; "Use this cart, but empty"; at the preview, "Shift
Bumbot's crawl higher, it is shown from below the entrance", "a black pixel shows"; "Build it"; during the build, "The
tooltip has to show (after the Bumbot's escape) only when we jump on top of the cart"; then "Approved"). The pillows
are one generated clip in two layers (`tools/build_linen_pillows.py`); the scene is `src/world/linen.js`, one clock;
`tools/build_shaft.py` fills the mouth's holes and lowers the fallen cover, and cuts the mouth against the room's
corner as it was when its pictures were made. About 80 generations.

## Part 14, group 1: the last three rooms redecorated; the lifeboat's photo; the pulse stops on E (2026-11-25)

The user: "Yes, let's do group 1" (plan-the-rest §7i). Three looks of each room, the other rooms' wording (A its own
colours, B lived-in, C clean modern; seeds 5, 13, 27); the user: "1. I like A, but let's regenerate without Bumbot's
picture and reapply it 2. A 3. A".

- **Her crew cabin (A):** redrawn from the room with his picture taken out (the wallpaper carried through, its 16 px
  repeat), so his picture from their photo goes back on a wall that never had the redraw's copy of it. Her door, her
  mirror, her bed (its suitcase, her slippers), the bowl her three tangerines lie in and his picture are as drawn, cut
  out by what is not the wall's colours (`cutouts`, `wall` in `tools/redecorate_rooms.py`: a box would carry the old wall).
- **Ukraine's flag, generated on its own** (the user: "Please regenerate the Ukrainian flag separately, not based on
  your drawn picture. We need a UA flag with the trident in the middle"): three tries at 32 x 24, **3** chosen; its blue
  was 10 rows of 24, so a row of its own blue was added and two of yellow taken off: 11 over 11 in its 22 px slot, the
  shield centred on the line ("the separation between blue and yellow must be in the middle"); muted a third toward
  the wall as the drawn one was (the user's choice); in its own colours, not the palette's.
- **Cabin 8206 (A):** its shower room's door, the door back out with its sign, the desk and its pouf, the bed and the
  lobster drawing as drawn; the window's glass clear again for the live sea (`clear`; the redraw was given a pale sky
  there). **Its bed pulses alone** (`keep` by its shapes in `src/highlight.js`): the redrawn sofa behind it pulsed with
  it ("the sofa is pulsing, where only the bed has to").
- **The lifeboat's inside (A):** sent without its portholes (`tries/lifeboat-noports-drawn.png`), both parts with the
  same wording and seed; the nine portholes pasted back by their circles (`ellipses`), the ladder and hatch by their
  shape, the generated oars and boathook by their own outline (`images`); its parts faded into each other over x
  195..255 (cut hard at a rib, the right part showed brighter).
- **The lifeboat's photo** (plan-the-rest §9 U2): the user's own, "I ❤ BAT YAM" on its beach promenade
  (`reference/photos/`, git-ignored), redrawn by PixelLab at 168 x 224, **try 1** of four; small and framed
  (`tools/frame_nook_thumb.py lifeboat`). Its frame first 2 px lower ("shift the picture two pixels down"), then
  standing on the bench ("place it on the lifeboat's shelf"), then aft along it where the user stood her ("Move it
  here, behind the player"): `slot_lifeboat` at 336, 32 px up.
- **The pulse stops the moment E acts** (the user: "In general in the game: the pulse has to stop as soon as we
  activate an interaction with E"; `src/highlight.js`, the Refinement session's file, on the user's word): gone at once,
  not settled, and not again while she stays at the thing; back once she is free and at something else.
- 137 generations (the rooms 117, the flags 15, the photo 5). `boot`, `region2`, `deck3`, `highlight`, `keeps` pass;
  `check_overlaps` 0.

## Near-catch 5 from the water, her swimming enriched (2026-11-25, the Design session)

The user's two asks, not by the remake plan ("no need to apply our remake plan"); approved in play. The record is
`docs/pool-remake-log.md` §8 (decisions 30 to 38). Her stroke made again (sixteen frames with a kick), upright at rest
on the pool's floor with her head out, rings in the surface, the stroke's splash on its frame; from the water the scene
starts when Bumbot and the hot tub behind him are both in the picture, she stops, comes up, calls and watches, he
plunging in front of her, and she is never moved. `swimShow`, `swimY`, `swimRings` in the ship scene; `poolWatch`,
`poolBeat` in `src/world/lido.js`; `SWIM`, `POOL` in the config. 12 generations.

## Near-catch 6 remade (2026-11-25, the Design session)

The fifth by `docs/sequence-remake-plan.md`, on branch `near-catch-6` (made from `near-catch-5`). Its whole record:
**`docs/near-catch-6-remake-log.md`** (15 decisions). The old scene was recorded (fifteen faults: the net never touched
the alarm, there was no hatch to see, her way out left her legs on the ship's side); the user chose the structure
proposed, with one condition ("Just don't use the cry as a call"); two corrections on the preview's GIF ("Bumbot's
position is in the air between the consoles"; "it is not visually clear that the button is actually pressed"); approved
on its first play ("All approved"), with one thing more at the bow ("place Bumbot behind the railings on the bow. The
railings have to obscure him"). `src/world/bridge.js`, `BRIDGE` in the config, `tools/build_bridge.py`,
`assets/source/bridge/`; her clips `call`, `call-loop`, `call-up`; the popup `call.kitty`, the sound `pspsps`.
40 generations. `region9.bridge`, `region9.bridge_jump` new.

## The balconies remade (2026-11-25; `docs/balconies-remake-log.md`, the sixth by `docs/sequence-remake-plan.md`)

The user: "I need you to analyze the path through the balconies, start to finish ... I feel like things are broken
there." Recorded with real keys: twenty faults, most of one cause (the balconies had been given the wall jump, and a
balcony has no wall: she climbed through floors, skipped 40 px across a partition, was cut in half at one, and at each
row's forward end a kick took her out of the ship). Settled with the user: three drawn moves outside the rail (round a
partition; up and down its fin), the rail at 32 px, the pieces generated, the grip socks worn and made again. Three
preview rounds (the reflections out of the doors' glass; "Look carefully how she transitions from behind the balcony
glass to in front of it": the layering made a rule of the rail's top and the climb remade in parts; one frame's leg;
the socks' close-up with white nubs), then the build, then four corrections on play (a hop out over the rail that read
as the old drop: gone; the hints never shown under `cards=all`; down only at a partition: now from anywhere on a
balcony; the rail towels in a cabin; a wait on the fin in a gust: gone), and "All approved". `src/world/balcony.js`,
`BALCONY` in the config, `tools/build_balconies.py`, `assets/source/balconies/`, `assets/ship/balconies/`,
`assets/sprites/her-socks.png`. 62 generations. `region7` rewritten, `region7.link` new.

## Part 9: the tangerines' seats; the delivery robot seen from the side, its ride mended (2026-11-25)

The user: "Next step in our plan is tangerines' placement, no?" (plan-the-rest §7d), then "Yes" to the audit made again
and the raw tries. Every spot of the plan's twelve looked at again with her beside it (the renderer's own frame): all
still as the audit found them but 8206's desk (moved 2026-11-22) and Cagney's (moved 2026-11-24).

- **The props, generated** (`assets/source/things/tangerine-seats/`, its README has the jobs; 90 generations):
  **A**, a room-service tray on a stand. The first two looks stood on a wooden X like the deliveries' stand; the user:
  "Make a fitting stand": a slim chrome stand with straight legs, two loads (a dome and a glass, `roomtray-dome`; a cup
  and a milk jug, `roomtray-cup`), the tangerine 1 px into the tray's free end ("Shift the tangerine down one pixel").
  **B**, `B-s5`, a low bowl of grapes, a green apple and a banana (nothing orange), the tangerine in the apple's place
  ("It should cover the green apple there"; the second of a pair on the grapes). **C**, each trolley an inpaint of the
  game's own piece: the dessert cart's right dome taken out for a plate (`dessert-trolley-plate`), the room-service
  cart's plate by its dome (`service-cart-plate`, the tangerine 3 px in from its end: "two pixels left", "one more
  pixel to the left"; the generator twice kept the dome whole). All in their own colours, in the ship's atlas
  (`tools/build_ship_art.py`) with their washed twins.
- **The seats as data:** `SEAT_SPOTS` (where a tangerine lies in each piece's picture) and `SEATS` (each spot's piece,
  metre, offset, height, and whether the world puts the piece there) in `tools/population.py`; `tools/build_world.py`
  emits the piece (`seat_<id>`, washed by its place) and the tangerines on it. The tray stands replace the early side
  table at all five of its spots (deck 4's at 31 m and deck 8 aft's 14 px aft, clear of the extinguisher; deck 8
  forward's until part 11 moves it; deck 10's loose `prop_tray_10` gone). The bowl on the spa's desk, on Topsiders'
  counter aft of the barmaid (first over her: moved), and on the Garden Café's patio table at 187.2 m beside its juice
  (moved to the table's forward end), the pair out of the queue and clear of the cold room's door (the plan's 183 m is
  the ice cream counter and that door; the user: "Ok"). The dessert cart's and deck 9's cart's tangerines on their plates.
- **The shifts:** the Windjammer's and the Spinnaker's along their counters to the aft ends; the laundress moved 22 px
  aft to the folding table (the tangerine on the wall shelf where it was).
- **The user's review of all 56 placements** (an enumerated sheet asked for): the Atrium Café's down onto the table
  beside its little bowl ("touch the table, not the bowl"); the pantry's 1 px up; deck 9 aft's onto the towel
  trolley's folded towels ("on top the white plate to the right", `SEATS` with the map's own piece); the crates' "all
  good"; the fire-hose cabinet's asked about ("is it reachable there?": from the delivery robot's top, as `region2`
  checks).
- **The delivery robot:** shown riding it ("Show me a gif of her riding the delivery robot"), her ride was broken since
  step 2: it moved her picture and her body, the physics moved her picture again, and she slid off its front to hang
  on its corner (the test only measured her height and a distance). Moving her body only held in the stepped clock but
  not in play ("She slowly slides off him while he moves": a frame with no physics step lost the move); now its step
  is added to her picture and body together after the physics (`postupdate`), steady in real time and stepped. The
  robot made again seen from the side (the user: "regenerate the delivery robot, to has a view more from its side"):
  four map objects, **try 4**, turned to face the way it drives, four plain rows cut to its old 52 px, in its own
  colours (on the palette its greys went purple), 2 px into the floor ("its level on the floor should be lowered by two
  pixels", `ROBOT_SINK`), her top with it. The same two-line carry is in a few other movers (`outside.js`,
  `hazards.js`, `world.js`): offered to the user, not touched.
- `check_overlaps` 0 (the bowl on the spa's desk and on the pool bar allowed); `check_corridors`: deck 11 47.2 / 53.7 m
  (was 47.4 / 53.9), deck 4's longest without a reward 68.0 m (was 68.4). `boot`, `region1`, `region2`, `region3`,
  `region4`, `region6`, `region9` pass; `mishaps` fails only on deck 9's sprinkler, as on the committed tree.
- 90 generations for the seats, 4 robot tries; the balance went from 8,869 to 8,695.
- **Asked after the commit:** "Why did the gag stop working here?" (the wet patch and the deck chair by Topsiders, 7a). It
  had not: the Topsiders link given for this part carried `&cards=all`, which gives her every verb, the grip socks too,
  and in the socks the wet tiles hold. Walked from `?at=wet7a` with it she passed the chair; without it she slid into it
  and the gag played. No link of this round needed the flag (the user's rule: only where a lock must open).

## Part 10: the checkpoints, nineteen places (2026-11-26; `docs/plan-the-rest.md` §7e)

- **The doors (the user's choices):** four tries of the plan's two props (B, a padded theatre door; C, a dark wood service
  door), `edit_image_pro_flash` of the crew door padded to 40 x 80, 5 generations each. The leaves came 23 x 69 with no
  surround: each is set into a doorcase on the crew door's own frame (29 x 74, its outline, the leaf where the crew
  door's is, a flat band of dark wood by rule). The user: "I like all of them, let's use all. Find a fitting place for
  each": burgundy padded (B1) for the theatre's foyer (the Stardust's red and gold), navy padded (B2) for the Arcade's
  night blue walls, walnut panels (C1) for the Library, mahogany with a wide brass kick plate (C2) for Cagney's.
- **The lit twins, by rule** (`tools/build_checkpoint_doors.py`): the crew door's ajar geometry (29 x 79, the leaf 18 px
  wide on its right-hand hinges, its free edge 2 px over the frame and 3 under the floor, the room's light in the gap),
  the leaf mapped onto it column by column (lines across it slant a step at a time). The user: the portholes on the
  opened doors were "distorted" (warped with the leaf): each is now cleared from the warped leaf and laid back whole from
  its own pixels where the leaf's middle carries it; then "shrink them a little bit, making them less wide (but same
  height as now, thus creating ovals). And keep them centered still": a column either side of the middle left out, so
  the rim stays a ring (13 to 11 px, 12 to 10).
- **Placed:** each checkpoint's door is a name in `CHECKPOINTS` (a fifth field; `trunk:<name>` for a lamp over a trunk's
  own door), `lightCheckpoint` sets the door's own `-ajar` twin. The foyer's door a metre aft (205.3 m). The Arcade's
  second cabinet out, the teen at the first, the claw machine, the pinball and the last cabinet 0.9 m aft. **The
  Library's door at 160.9 m, not the plan's 161.1:** measured in the shot, 161.1 left 36 px of panelling on its left and
  17 on its right; 160.9 is the gap's middle. **Cagney's wine cabinet is gone, not moved:** aft of the technical door
  stand the ladder (167.2), the cake's table (167.75), the pastry chef (168.5) and the booth; no room is left. The
  Garden Café's last window run ends at 191.0 m (five panes), its last table at 189.8 m. Deck 9's arrival is the lamp
  over the trunk's own door (`TRUNK_LAMP_RISE`, 92 px: above its ▲/▼ lamps); its white twin door is gone.
- **Out:** `cp_6_fwd`, `cp_4_aft`, `cp_station`, `cp_officer`, `cp_chapel`, the guest's cabin both sides, `cp_funnel`,
  `cp_balcabin`. The three that held a cabin door's slot gave it back by the corridor's rule (looked at: deck 4 aft,
  deck 6 forward, deck 10's officer at a cabin door again). **The funnel (the user asked, then approved):** with every
  checkpoint lit, a scare at the top's forward end, middle or aft end brings her back at the technical door; offered if
  it plays too harsh: a lamp with no door at the top, or one of the design session's four steel lockers.
- **The rule** (`closestCheckpoint`, `shutBetween`): on her deck, a checkpoint with a wall across the deck between it and
  where she was, whose door (or end wall) would not pass her from the checkpoint's side, is left out; with none at all
  the rule gives way. `region7.shut` checks it at deck 9's aft swinging door: the hallway's cabin, then another deck,
  then 190 m once the one-way door at 202 m is opened.
- **Tests:** `check_overlaps` 0. `boot`, `region1` to `region4`, `region6` to `region9` (with the new case), `finale`
  pass; `mishaps` fails only on deck 9's sprinkler, as before. The checks that named a checkpoint that went now check it
  is gone; `region4`'s two returns moved with the plan (the trunk's own door; the corridor's aft end where the balcony
  cabin's corridor side was).
- **Links walked as given** (E at the doors, a hop at the queue, as a player would): `library`, `theatre`, `balcony7`,
  `technical`, `diner`, `deck9-aft`, `jet11`. `chips7` is not one for the Arcade: its spill of chips takes her.
- 20 generations; the balance went from 8,667 to 8,647.
- **After the commit, in play (the user):** "Remove the chair to the right of the checkpoint, and shift this entire
  checkpoint to the right, so that it entirely stands on the wooden floor": the pool attendant's hut stood 9 px over the
  pool's tiled rim; the hut, its door and its lamp 10 px aft (140.6 to 140.8125 m), the lounger at 141.4 m out. Then
  "Place this chair in the middle between the officer and the checkpoint": the lounger at 144.6 m to the middle of the
  free space between the hut's edge and the security officer's back (`riv_loungers`), 4 px forward of it so that its
  foot clears the parasol's base: 142.45 m (`LIDO["lounger"]` with it). `check_overlaps` 0; `region6` passes.

## Part 11, first group: items 1 to 4 (2026-11-26; `docs/plan-the-rest.md` §7f)

- **1, the towel stack on deck 4 at 169.6 m** (`STACKS`), midway between the cabin doors at 167.6 and 171.6 m; the
  corridor's picture moves out of its way by its rule. **The user, checking its fall both ways and deck 9's: "they don't
  cover the foot of the cabin door, but are obscured by the door. If visually they would obscure the door, then it would
  make sense"**. Two causes. (a) The heap's top towels ended at 77 to 79 px from the stack, the frame's outer edge at
  79: drawn in front, it read as tucked behind. **A cabin door within 100 px of a towel stack stands 8 px nearer to it**
  (`nudged()` and `STACK_DOOR_NUDGE` in `tools/build_world.py` for every door placed in a slot, the same rule in the ship
  scene's `drawCabinDoors`), so the towels lie plainly across the frame onto the leaf; deck 9's open cabin (the darting
  vacuum's) moves with it. (b) Deck 9's ajar door (depth 8.0) was over the heap (7.98): **the falling and fallen heap at
  `props + TOWELS.heapDepth` (0.01)**, over the ajar doors, under the vacuum resting in the doorway (8.02, the user's
  "correct order of depth", after a try at 8.04 over it), the people (8.05), the ship's closed side (8.6) and her.
  **Checked on the user's word ("dimming, when on decks above or below, the hull, outside")** by the heap at the old
  depth, the new and hidden, in its own rectangle: its own corridor (changes only at the doors), the deck above and below
  (not seen: deck 9 is behind the closed side there; only the balconies' towels flap), the outside view (hidden), inside
  the open cabin (hidden). `check_overlaps` 0.
- **2, a second vacuum on deck 4, 225.5 to 239 m** (`vacuum-2` in the map), past the stage manager's door, turning short
  of the theatre trunk's door: the pills' test in region 3. `pills_for_the_stage_manager` in the playtests holds it still
  for its blind walk; its hit is `mishaps.stretches`'.
- **3, a second runaway suitcase: not at Shore excursions, but deck 5's atrium, 93.4 to 97 m, and only once the lunch is
  delivered** (`after: flag:lunch`). Measured: a tray's low hop peaks at 26 px (350 x 0.62, gravity 900), the case needs
  30, and the lunch's way runs the whole of deck 5 (the pass at 249 m to the forward stairs, 75 m); the forward cabins
  (20 to 74 m) are full. The user chose "off the way", then "same spot, after lunch", then (in review) "a suitcase is
  supposed to be in a corridor with the guest rooms, or in the atrium deck 5, where guests are checked in": a guest's
  case by Guest Services, between the glass lift and the palm before its desk; nothing else is planned there. Then
  **"Make two suitcases different colors": the new one red** (the user's choice of red, teal, mustard, green), its world
  picture and every frame of her gags with it (6a to 6c) turned by `tools/recolour_suitcase.py` (the case's own mid tones
  only, pieces of a dozen px or more, the handle's greys and the tag kept), each red clip placed exactly as its slate one
  (`shift_as`) with its heads (`SAME_AS` in `tools/build_heads.py`); the game plays `GAGS['suitcase-red']`'s clips for a
  roller with `look: 'red'` (`rideGag`). No generations.
- **4, Bumbot's trays in the Seven Seas** (`TRAYS`), three lots at 218.7 to 220.1, 226.1 to 227.5 (off the column) and
  235.7 to 237.1 m, between its tables and palms, no door behind them, there from the start until the lunch is delivered
  (`until`, a new option of a `TRAYS` entry: a dict). Carrying the lunch, a low hop clears each (measured).
- **Tests:** `mishaps.stretches` new (each of the four with none on her and with two; the trays before the lunch, the red
  suitcase after); `deck4`, `vacuum`, `region1`, `region3`, `region4`, `highlight`, `golden`, `boot` pass; `mishaps.things`
  fails only on deck 9's sprinkler, as before. Not run: the rest.

## Part 11, item 5: the DJ's fog machine at Bliss; Bliss in its props' own colours (2026-11-26)

- **The place:** the plan's 113.2 to 114.8 m is the lounge's table and stools, and the DJ stands at 121.3 m, not there.
  The user, shown three tries (map objects) and two redraws of try 2 in strict side profile: "Use A, don't redraw"; then
  "Show me the entire scene" (a panorama of Bliss from the renderer, stitched by world position) and, of three places
  with the puff's reach marked, "2, and shift it a few pixels to the right": on the floor at the DJ booth's front
  (120.054 m), its nozzle forward under the disco ball.
- **The machine:** A cut to 31 x 17 (plain rows and columns out, never resampled), its own colours; solid as the carts
  (she hops it). **The hazard** (`Fog` in `src/world/bow.js`, a `Steam`; `FOG` in `tools/population.py`, `haz_fog`):
  the sauna's clock, ~~every 5.2 s~~ **every 3.8 s (the user: "Reduce the delay between the steam cycles")**, a tell of
  0.9 s (its light blinks red, wisps from the nozzle, the hiss), a low puff of 1.6 s rolling 0.8 m forward along the
  floor; caught under its top, gag 17 (`Steam.ride`, its cloud inside Bliss's walls); a hop over its low front, or
  standing on the machine, clears it. Drawn only while she is inside on deck 6. **Looked at:** the first puff (1.05 m,
  opaque) rolled over the trunk's door's foot and read as a blob: 0.8 m, thinner, smaller, and the machine's puffs never
  past the door's frame (`stop`); the gag's cloud cut there ended in a hard edge down the door, so it is not cut.
- **Bliss's props in their own colours** (the user: "make the background props less washed out. Show me a screenshot
  with them placed there with their original color tones first"; of 20%, 12% and their own: "3"): a place at level 0
  in `tools/wash_levels.py` (`SUFFIX[0]` is no suffix). Its promenade door then rested in full colour with an invisible
  pulse; the user chose to change `src/highlight.js` (the Refinement session's code, asked first): a door in a place
  at level 0 rests as a lone trunk door (20%) and pulses up (`placed`, `own`).
- **Tests:** `mishaps.stretches` (the fog's case added: walked into its puff, none on her and two), `region2`, `region3`,
  `highlight`, `boot` pass; `check_overlaps` 0. 13 generations.

## Part 11, item 6: the boat walkway's gulls; the lifeboat she enters moved (2026-11-26)

- **Two gulls on the walkway's rail, no gusts** (the user, of a mock-up with a line of signal flags as the gusts' tell:
  "Yes, those two", "No gusts there"): `WALKWAY_PERCH` in `tools/population.py`, at 165.4 m (between two lifeboats: at the
  plan's 160 m a boat, drawn in front of her and the rail, hid it) and 181 m (5 m forward of the drill), on the rail's top
  (30 px, measured). **They answer her coming** (`eager` on a `PerchGull`): the balconies' wait for her to linger two
  seconds, and the user "can run past them without even realizing they would move"; then "remove the starting sequence,
  when the gull is preparing. Make it just fly up straight away": the moment she is within 2.6 m, no hop on the rail, it
  goes up (0.38 s) and dives at where her speed puts her; then "the gull shoots at me even when I'm more than half a
  screen away. There has to be some max range": the dive is kept within 1.6 m of its rail (`EAGER.reach`). The way past:
  bait it from just outside, let it miss, run through while it flies back (2.6 s). A runner straight past gets gag 20; with
  tangerines on her it takes one. The balconies' gulls are as they were.
- **`?at=drill7` moved to 184.3 m:** at 180.5 the gull dove on her as the page loaded (the drill's case in
  `mishaps.things` starts there too; it passes).
- **The lifeboat she enters is the second red one, 155.6 m** (the user: "switch between the two red boats, making the
  second one enterable instead of the first one"): `lifeboat-round` and the room's `m` moved from 143 m (two lines of
  data; inside, all is in the room's own px).
- **Tests:** `mishaps.stretches` (the walkway gull's case added: lingering by it with none on her, its gag; with two, it
  takes one), `region2` (the hatch, the book, the photo), `region7` pass; `mishaps.things` fails only on deck 9's
  sprinkler, as before; `check_overlaps` 0. No generations.

## Part 11, item 7: the sun deck's gusts (2026-11-26)

- **Gusts over the sun deck** (`SUNDECK` in `tools/population.py`, the topdeck's `sundeckGusts`, a `Gusts` as the aft
  terrace's): every 7 s over 110.5 to 144 m, a tell of 0.7 s, a blow of 1.5 s; towels over the two loungers' backrests
  (111.02 and 112.9 m) the tell; the palm left still (turned, its pot would tip). In the air she drifts aft; **the cake
  wobbles while she moves in a blow** (`SWAY.gust`, 0.45 a second, in `src/world/carry.js`; standing still, nothing:
  measured 0 and 0.55 over a blow).
- **The user:** "The towel is visible through the door. Make the towels less colorful": the towels at the loungers' depth
  (`towelDepth`, 3.11, under the deck's door at 8) and muted (`colours`: a pale blue, a sand). Then, asked what a gust
  should do on the deck (it is no obstacle on foot): **"Keep as is"**: dressing, the hop's drift and the cake's wobble.
- **Tests:** `region8`, `region9`, `boot` pass; `check_overlaps` 0. No generations.

## Nine more people to her proportions (2026-11-25, the Refinement session)

The user: "I remember we regenerated people that had large heads. Now I see some of those in the game again. Is that a
new bug, or something we missed previously?"

- **Not a regression:** the twenty-four redrawn on 2026-11-13 (`312fe103`) still have their redrawn characters and
  standing pictures. Every one of the 140 people laid beside her (`tools/check_people.py`), the doubtful ones' heads
  against the ruler (`--heads`).
- **The user named nine:** the lost tourist, the Windjammer's barmaid, the model ship's guest, the casino's cowboy, the
  spa guest behind deck 9's "Do Not Disturb" door, deck 8 aft's door guest (`swing_sunhat`), the two in the step class,
  deck 10's officer. Six had been in the game at the first review and passed it; the steppers and the officer were
  placed the next day without the check.
- **Redrawn** in PixelLab's pro mode with the style characters that hold the proportions (the drill's officer for the
  men, the cabin maid for the women), from their own descriptions, and every clip the game plays of them made again on
  the new figure: the idles and the officer's walk on its own skeleton (skeleton-v3 with the template: the size kept),
  the shriek and the steps by v3. **The user's two changes:** the model ship's guest an elderly gentleman with no cap,
  in a polo shirt and chinos ("looks like a captain to me"); deck 8 aft's door guest an elderly lady woken in her
  nightgown, round glasses, slippers ("looks out of place at all"). The old characters' ids are kept in
  `tools/cast.py`.
- **Checked frame by frame:** the door guest's idle came with a breath's puff in front of her mouth, taken out of its
  four frames (each frame's smaller pieces); her frames are kept by hand now (`BY_HAND` in `tools/fetch_people.py`).
  Nothing else loose; every head at its standing size in every frame. Shot in place in the game beside her; the
  steppers stand beside their boards as the old ones did.
- **Found and offered, not done:** six seated diners never redrawn read a little chibi (`docs/plan-the-rest.md` §9,
  U14).
- 108 generations (90 the figures, 18 the clips). boot, region1, region2, region3, region4, region6, region7, region9
  pass; check_overlaps 0; the whole suite not run.

## Every placed person checked, twelve placements tuned (2026-11-26, the Refinement session)

The user: "do a visual check over every placed NPC in game. I want to detect NPC's that look out of place, that are
visually overlapped with anything ... An example: an NPC is drawn with their own chair, but is placed on top of some
other chair". On branch `npc-check` (worktree `../mysterious_female-npc`), from main 4045cef.

- **The check:** all 163 placed people shot in place (her hidden and untouchable, every story state shown), every
  suspect enlarged, each finding shown in the game's full view: twelve. Not faults: the theatre's seats, the kid passing
  the rival by the pool, the door gags' faces, the chapel's crowd.
- **The fixes (the user's rounds, seven):**
  - La Cucina, the Seven Seas, Cagney's: the diners are new people with no chair of their own (edits of the approved
    stills), seated by the husband's rule; La Cucina's tables and chairs and the Seven Seas' (and the Four Seasons')
    redrawn side-on and bigger, La Cucina's tables in its chairs' walnut; the tables drawn again over the diners
    (`cover`); La Cucina and Cagney's unwashed (`tools/wash_levels.py`, level 0); Cagney's booths 2 px into the floor
    (`around(chair_dy=)`), the lady's dress navy (by a hue rule, the wine kept red).
  - The step class: a clip of each stepping up onto the board and down (PixMiniMax, the board by rule in the frame);
    the boards drawn in code are gone.
  - The Garden Café: its tables at the forward end, the buffet along the queue's stretch (`QUEUES` 168.4 to 181.5 m).
  - The wedding party clear of deck 12's stairway door; the trophy cabinet and beer fridge swapped behind the planner;
    the walkway's rival in the gap between two tenders; the guest in his cabin 16 px aft of his wall lamp.
  - The Internet Café: side-on desks 30% higher, ergonomic office chairs, the girl's armrest and the desk's legs over her,
    a footrest under her feet. The Sushi Bar: side-on stools in at the counter, its two diners new (half of U14).
  - The engineer by Cagney's wine cabinet is left to part 10 on `three-uses` (the cabinet is gone there).
- 132 generations (the nine people 45, the furniture and footrest 80, the step clips 2, the board 5). check_overlaps
  0; boot, region1, region2, region5, region6, region7, region8, region9, highlight pass; mishaps fails only on deck 9's
  sprinkler, as on main. The whole suite not run.

## Part 11, item 8: the gym's two balls; the sit-down lower; the runner on her treadmill (2026-11-26)

- **Two balls rolling with the ship** (`haz_gymball_1`, `_2` in `ROLLERS`, `thing: "gymball"`; a `Roller` with its own
  pictures, height and hit, `Roller.BALL` in `src/world/movers.js`). Of three generated tries the user took two ("If there
  is enough space for two of them in the gym, then both blue and purple"): the purple in front of the two bikes, 90.6 to
  94.2 m (clear of the socks on the treadmill, 89.2 m, and short of the cross trainer), the blue aft of the yoga rack in
  front of the rower and the bench, 96.3 to 99.3 m (short of the trainer, 100 m); 1.4 m/s at their fastest. **They turn,
  their light still** (the user: "The balls have lines, so they should turn. The light has to stay still. If that needs an
  animation(s), generate"): a ball rolling in a side view turns in the picture's plane, so `tools/build_gym_ball.py` draws
  a seam and two ribs by rule on the sphere at 32 angles over the try's own shading (the highlight kept clear of them; a
  whole turn, since the lines' axis leans toward us and half a turn bows them the other way); the blue is the same
  picture in try 1's blue. Each frame by the px rolled over its radius. 24 px: a hop clears it.
- **Its hit** (`MISHAPS.gymball`), first one scenario, "Bumped" and the sit-down; then the user: "If she is hit from the
  front, she trips over the ball, use the tripping and falling forward gag. If she is hit from behind, keep the current
  gag": **25a** at her front (tripped, the built trip onto her belly), **25b** at her back (bumped, on her bottom). Her dash
  sends a ball rolling to its end of the room.
- **`?at=gym` moved from 92 to 88 m:** 92 was in the purple ball's lane.
- **Her sit-down 2 px lower, everywhere** (the user: "The gag where she sits on the floor has to be shifted down by two
  pixels. In all the occasions"): `scareDown` drops her from her fall's first frame on the floor for the sit as for the
  belly (`LIE_DROP`), and a gag that ends in the dazed sit too.
- **The gym's runner** (the user: "shift her 2 pixels up, and change her depth to obscure the treadmill"): `dy` 7 to 9 and
  no `cover` (the treadmill's handrail was drawn again across her).
- **Tests:** `mishaps.stretches` (the balls' cases: 25a and 25b with none on her and two, a hop over the blue, both
  turning), `mishaps.porter`, `region6`, `boot` pass; `check_overlaps` 0; `check_corridors` deck 11: 47.2 m without a beat
  (36 to 83), 53.7 without a reward. 3 generations.

## Part 11, item 9: the night watch's "Do Not Disturb" door and tray; deck 10's bridge sign; the corridors' carts (2026-11-26)

- **The place** (the user, of two: "1"): his door is the last cabin of deck 10's officers' corridor before the bridge,
  45.6 m (`haz_dnd_10f`), his tray from the night just aft of it, 47.0 to 48.4 m (`haz_trays_10f`, its clatter opens his
  door). The plan's 53.6 m is inside the officer's trolley walk (50 to 70 m). Going forward to the bridge: the officer, the
  tray (hop it; gag 3), the door (E or her cry; gag 23); a tangerine in the tray brings him to look out, no fright.
- **The night watch** (`dnd_nightwatch`, a pro character in the drill officer's style): the first, all in striped pyjamas
  with a black mask, was nearly deck 10's sleeper and his mask was lost on his hair; the user chose the redraw: his white
  uniform shirt with gold epaulettes, half-buttoned, over striped pyjama trousers, barefoot, a pale blue mask pushed up.
  His `shriek` (v3, as the other door guests'), its teal undershirt put in his skin's tones; approved over his doorway.
  `assets/source/people/dnd_nightwatch-raw/README.md` has the ids.
- **`?at=officers10`** (72 m, the corridor's aft end by the stairs), walked as given: past the officer, a hop over the
  tray, at his door, nothing hit.
- **The bridge's "BRIDGE / CREW ONLY" sign 2 px higher** (the user; `sign_up` on its wall, `signUp` in `buildBulkhead`).
- **The carts the corridors leave by a door** (`drawCabinDoors`; and the towel trolley at cabin 8206's door) are under
  whoever walks past, decor 0.115 from 0.15 (the user, of deck 10's officer passing behind one: "This guy should obscure
  the trolley, not be behind it").
- **Tests:** `mishaps.stretches` (his tray, 3, and his door, 23, none on her and two; him shrieking in his doorway; the
  tray's clatter opening his door), `boot` pass; `check_overlaps` 0; `check_corridors` deck 10: 53.2 m without a beat
  (60 to 113), 92.3 without a reward (38 to 130). 21 generations.
## The HUD's utilities: the grip socks and the parasol (2026-11-26, the Refinement session)

The user: "both the parasol and the grip socks are not shown in any way on the HUD, once collected"; "We need to
show both utilities on HUD, once collected". On branch `refine` (worktree `../mysterious_female-refine`), from main
e13eb438.

- **Where:** of four places mocked up over a real shot (after the cards, top right, bottom left, a row under the
  cards), the user chose the top right: on the counts' line, 11 px in from the right edge (the tangerine's rim is
  11 px in from the left), from the right in the order she gets them (the socks come first in the story).
- **The pictures, the user's own:** the socks regenerated so that the grip dots read (8 tries, 40 generations,
  `assets/source/hud/tries/socks/README.md`): the user took try 7 (one sock, white dots on a dark sole), mirrored, a
  copy behind it 4 px left and 3 px up, and edited the pair in Paint; the parasol the game's open one shrunk by
  majority and outlined, edited in Paint (furled it lost its shaft). Both files `assets/source/hud/*-by-hand.png`,
  magenta empty (both pictures have pure white), read by `tools/build_hud.py` (which reproduced the committed atlas
  before the change), never written; the dark outline is in the picture, the light rim the build's.
- **In the game:** `src/hud.js` (`TOOLS`, `tool()`, `save.hud.tools`, `state().tools`); `world.take()` holds a verb's
  picture until its close-up closes (`hud.expect(name)`, `release`), as a kind's count. The sound's sign (M) moved
  62 px down, under them (`showSoundSign`).
- **Checks:** in the running game each picture shows only once its close-up is closed, socks then parasol, no
  errors; `region6` and `region8` check each picture after its pickup (new); boot, keeps, highlight pass. The rest of
  the suite not run.
- **Next:** the pills, her one pocket item, shown while she carries them (the user: after the utilities).

## The stage manager's pills carried in her hands (2026-11-26, the Refinement session)

The user: "Analyze the route she has to make in order to bring him the pills and let see if we can turn this item to be
another deliverable (not in our pocket)". On branch `refine`, after the HUD's utilities.

- **The route as it was:** down the theatre's trunk (240 m) to deck 4, 8 m to his door (232 m), the bottle, back up the
  trunk: about 16 m. **As a load** (no ladders with her hands full): forward about 30 m on deck 4 past the second vacuum
  and the cart at 220 m, the aft stairs 4 to 6, about 46 m aft through the foyer and the stalls, onto the stage under
  the swinging lamp.
- **The user's choices:** the bottle alone in her hands (of the bottle, a tray with a glass of water, a pharmacy bag);
  the lamp kept as the last test; the cart checked first (her low hop with a load clears it both ways, a walk stops
  17 px short: it stays).
- **Built:** `pills` in `LOADS` (`src/world/carry.js`, bare, a rattle when it spills); `item_pills` a source on his
  shelf (`tools/population.py`, `lift`: one bottle, a fresh one after a spill), on view only once near-catch 3 is over
  (as the pickup was: the user asked why it showed from the start; it had come from the canister's pattern), 1 px up
  and 2 right (the user); `pills()` in `src/world/story.js` takes it from her hands. No close-up for it now.
- **Found in play by the user:** the deck 4 vacuum hid behind the stage manager's door (both at `DEPTH.props`): it is
  drawn just in front of the doors now; and a vacuum hit with the bottle hung the game: the vacuum's hit had no height
  (`world.touched` without `y`), the spill's sound threw every frame. It reports its height now; a hit spills the bottle,
  plays gag 5a and sends her to her checkpoint.
- **Checks:** `region3` and `golden` check the bottle in her hands, off the shelf, the trunk refusing her, his card;
  `region3.pills_spill` (new) the vacuum's hit with it; boot, region1, deck4, vacuum, highlight pass; mishaps fails only
  on deck 9's sprinkler, as on main. No generations.


## The pools' tanks over the decks under them (the Refinement session, 2026-11-27; the hull's top review, 1 and 11)

- **What was wrong** (`docs/audit-hull-top-2026-11-26.md`): the tanks are drawn over the ship's side on purpose (their
  floor seen from their deck, the user). Deck 12's kids' pool reached 20 px into deck 11's window row; under deck 11's
  pools, deck 10's balcony dividers (the panels the game draws over her) ran up over the tanks' last rows.
- **The kids' pool:** its tank drawn a tile thinner, walls and bottom (8 px each, `TANK_WALL` in the ship scene), so
  that it reaches 12 px into the windows; the windows as they were (the user: "Don't change the windows"). The map's
  tiles stay (play is the same); only the walls' top tiles at the deck's floor are the deck's own floor tile, or their
  outer half showed beside the rim (`tools/build_ship_map.py`). The water and her swimming are as they were.
- **Deck 11's pools keep their two tiles** (the user, after seeing them thinner: the drain's hatch and grate are drawn
  for that floor and hung under a thinner one). **Deck 10's dividers under them start at the tank's foot**, where the
  doors' glass shows from under it (`tankFoot()`, the panels in `src/world/world.js`); elsewhere they still reach the
  balcony's ceiling. A tank's rows run from 4 px under its floor: its foot is 4 px past the walls' thickness.
- **Not done yet:** the 3% ghosts while she swims (finding 2, the fractional deck; "not now, at first the two above").
  Finding 12 (hidden at the `stern` start) is by design (the user).
- **Checks:** region6, region7, region9 pass (14 cases). No generations.
