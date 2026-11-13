# The build plan: step by step

How the plan of `GAME_DESIGN.md` §6.1 and the population spec `docs/population.md` get built
(Decided, 2026-11-11, the user's choice: the hybrid cut, the ambient cast built with each region).
**One short skeleton step, then one step per region in play order.** Each region step populates its
whole area from the spec, with the mechanics that first appear there, its art, its playtest and the
user's review. `GAME_DESIGN.md` §8 "Next up" names the current step; a new session starts there.

## The shape of every step

1. **Scope:** the region's areas and every entity the spec lists for them (by id), plus the systems
   that first appear in the step. Nothing from later regions.
2. **Layout first:** rooms, doors, trunks, hatches and platforms in `tools/ship_layout.py` and the map
   builder, before any art, so art is placed once.
3. **Art batch:** listed with its PixelLab cost, stated and approved before spending (`CLAUDE.md`);
   placeholders stand in until it lands. People: a character and its few clips each; the ambient
   figures from shared bodies recoloured.
4. **Playtest:** a headless scenario for the region (its route, its scares, its errand, its beat),
   added to `tools/playtest.py` and kept; the golden path re-run at the end of every step.
5. **Review:** screenshots in the chat and a link (`?play&at=<place>&tangerines=infinite`), one
   change at a time, the user's circled corrections fixed and shown again.
6. **Exit:** the region plays from its entrance to its exit with the real locks; every scare, errand,
   secret and beat in it works; its playtest and the golden path pass; a commit; §8 updated.

Rules that hold throughout: no death, nothing floats, human-sized things sized to her, sprites face
east, background props muted; a scare keeps everything collected; a tray never scares, only spills.

## Step 0: the skeleton

**Done (2026-11-13).** What changed against this list on the way: `docs/progress-decisions.md`.

The whole route proven before any polish. Everything that moves the layout goes in here.

- **Locks on:** `LOCKED_PARTS` and `KEY_CARDS.required`; every reader of the spec's §2.6 in its
  colour, on crew ways only (no card on a public stair or door, the user, 2026-11-11); the routine
  blocks as rope stands with their signs and no people yet; the one-way fire-exit doors; the gold
  lobby doors of decks 9 and 10; the bridge's gold door; the mooring deck's door. **Done (round 1,
  2026-11-11)**, except `LOCKED_PARTS` (the hidden parts).
- **The new vertical ways:** the Bliss/Magnum's trunk extended to deck 9 (red); the duct as a bare
  crawl passage from the linen room's vent to deck 8 at 66; the chute as a fade and a landing in a
  bare laundry; the pool's drained state and hatch into deck 10; the bridge's hatch and ladder; the
  technical door and ladder at 165 and the funnel's stairway and top platform; the sun cover climb
  from the service station; the balcony rails as platforms and the partitions as walls, the ajar
  balcony doors and their cabins as bare rooms; the boat walkway's gate and ladder; the stern tiers'
  climbable steps; the lifeboat, the dressing room, the lighting booth and catwalk, the nook, the
  pantries, the dry store, the cold room, the galley, the stage manager's cabin as bare rooms.
- **The verbs, bare:** push on marked carts and the library's ladder; the crawl state; the wall
  jump; the glide while jump is held; each with a stand-in clip (her run, climb or jump) and its glyph.
- **The flags:** the cards as plain pickups at their spots; Bumbot's six beats and three glimpses as
  triggers using his built near-catch with its escape direction, no choreography yet; the horn's
  cascade, the wedding, the alarm and the drain as flag flips with placeholder props; the glass
  elevator's and the cores' panels by region; the checkpoints placed; the tangerines placed; the
  books as plain pickups and a counter; the HUD's slots.
- **Playtests:** `golden` (the gangway to the catch, every lock opened the intended way) and `sweep`
  (every lock tried from the wrong side, every drop from a region into a later one). Both are kept
  for the rest of the build.
- **Art:** none. **Exit:** the golden path completes headless; the sweep finds no way round a lock;
  the user walks the route once with the real locks and approves the regions' edges.

## Step 1: Lower ship (region 1, decks 4 and 5)

**Done (2026-11-13).** What changed against this list: `docs/progress-decisions.md`.

- **Scope:** the spec's deck 4 and deck 5 tables; the gangway officer, the porter, the waiter, the
  lost passenger, the bathrobe guest; the rival security officer at his search rope (`riv_rope`); the luggage stack, the vacuum, the standing carts; the
  laundry, the dry store, the pantry passage and the galley as real rooms; the stage manager's
  cabin; the Seven Seas' pass; near-catch 1; the first book; the tangerines; the crew notice board
  and name plates; the ambient figures of decks 4 and 5.
- **Systems first seen here:** carrying and the tray rules, the spill, the tray source; pictogram
  bubbles; the scream that gives the dash and the D glyph; breakables; the scare framework with
  frights per hazard; `loop` and `trap` behaviours; the routine block with a person; the card
  hand-over scene; the room kind for crew rooms.
- **Art:** the officer (idle, eat, hand over), the rival security officer (his character; idle with
  the net, peer, shake his head; his other clips come in step 3), the porter and his cart, the waiter, two ambient
  passengers, the galley chef, the folder, the receptionist, diners; her tray walk, hop, hand-over
  and spill; the luggage stack; the frights "Bumped"; the rooms by hand. Priced before spending.
- **Playtest:** `region1`: the lunch fetched past the waiter and the vacuum, the card, the forward
  stairs open, the midship and aft flights blocked.
- **Exit:** region 1 plays as the spec says; the dash is learned; the user approves the look of a
  populated corridor, which sets the standard for the rest.

## Step 2: Atrium + promenade (region 2)

**Done (2026-11-13).** What changed against this list: `docs/progress-decisions.md`.

- **Scope:** deck 6 from the bow to the Library, the promenade, deck 7's lobbies and atrium walk,
  the boat walkway's gate and foothold, the lifeboat's inside; the librarian, the jogger, the
  delivery robot, the photographer, the carpet fitter, the DJ and the other ambient figures; the
  flash; near-catch 2 and the glass elevator glimpse; the rival's glimpse on the promenade; books 1 and 2
  returned and read; the gulls perched on the promenade.
- **Systems first seen here:** the books (trolley, shelf, chair, pages), the glimpse kind, the
  `platform` behaviour, the gate and ladder, `quirk(still)`, the photo slot kind, the first proper
  near-catch choreography (the rope stand knocked into the door).
- **Art:** the librarian, the jogger, the robot, the photographer and posers, the fitter and the
  carpet roll, the stewardess, the DJ, the barman, the audience; her reading idles and the dance;
  the lifeboat's inside, the shelf, the trolley, the ladder, the nook (bare until step 9's tenth
  book); the gulls' perched and flap states.
- **Playtest:** `region2`: up with the card, the promenade and the jogger, the library's beat, the
  door left open.

## Step 3: Showtime (region 3)

**Done (2026-11-13).** What changed against this list: `docs/progress-decisions.md`.

- **Scope:** the theatre, its balcony, deck 7 from Magnum's to the Arcade, the dressing room and the
  lighting bridge; the stage manager, the dancers, the rival on stage; the stage lights, the trap
  door, the pit, the chip spills, the jackpot; the pills' errand; the Entertainment card; book 3;
  the casino's and the bars' ambient figures; the one-way trunk; the midship lobby's red door; the
  trunk from Bliss to deck 9 as the exit.
- **Systems first seen here:** scripted scenes with two actors (the rival's trip into the pit),
  `timed` and `random` hazards, the trap door's one-deck drop into a room, pocket items.
- **Art:** the stage manager (sneeze, flap), the dancers, the rival (walk with net, lunge, trip,
  slump), the croupier and players, the barmen and pianist; the lights' swing, the trap door, the
  fly rope, the chip spill; "Bonked" and "Slipped"; the dressing room and the lighting bridge by hand.
- **Playtest:** `region3`: the drop onto the stage, the beat, the pills down the trunk and back,
  the card, the red door, the trunk to deck 9 opens.

## Step 4: Housekeeping (region 4)

**Done (2026-11-13).** What changed against this list: `docs/progress-decisions.md`.

- **Scope:** deck 9 midships, the linen room's beat, the duct as a real room with its grilles, the
  chute and the laundry finished, the pantries' tangerines; the steward and his cart, the
  honeymooners, the mid-cleanup cabin, the sprinkler, the swinging door, the towel stack, the
  "Do Not Disturb" door, the adjoining cabins, the luggage stack, the balcony cabin with its view of
  Bumbot a deck up; the Housekeeping card; book 4; the towel-animal block; the atrium walks of
  decks 8 and 10.
- **Systems first seen here:** push and crawl with real clips, `reactive` hazards, the hidden trap
  with a tell, the adjoining-cabin loop, the camera scene, the balcony cabin kind.
- **Art:** the steward, the honeymooners, the startled guest, two officers for later; her push,
  crawl and camera clips; "Buried", "Drenched", "Startled"; the generic inside cabin with a
  connecting door, the balcony cabin, the duct's look, the towel animals.
- **Playtest:** `region4`: the trunk up, the cart pushed, the card, the honeymooners, the gauntlet
  walked and run, the vent and the duct into deck 8.

## Step 5: Deck 8 forward (region 5)

**Done (2026-11-13).** What changed against this list: `docs/progress-decisions.md`.

A breather. **Scope:** the duct's exit, the one-way lobby door, cabin 8206's book and basket, the
towel-swan cart, the peek cabin, the balloons; the stairs on up through the officers' lobbies;
`cp_8206`. **Systems:** none new. **Art:** the balloons, the swan. **Playtest:** `region5`: out of
the duct, the cabin, the climb to deck 11 without leaving the stairwell.

## Step 6: Lido (region 6)

**Done (2026-11-13),** but for her husband's own character, which waits for the user's photo (a
stand-in sits at his table). What changed against this list: `docs/progress-decisions.md`.

- **Scope:** deck 11 from the forward lobby aft; the socks; the pool's beat and drain, the hatch and
  deck 10's midships hallway; the kid, the wet patch and the deck chair, the gulls over the gap, the
  buffet queue, the cold room; the Great Outdoors: the user's character, the machine, the canister,
  the table scene; book 6; the hot tub, the chess set, the cone for herself; the paw prints; the
  rival under the loungers; the blocks lifted and set (the towel animals lift; the paint, the fans,
  the wedding party stand); the gym's and the pool deck's ambient figures.
- **Systems first seen here:** the wall jump with its clip, the slide, `patrol` with an action, the
  gulls' dive at food and the cone as bait, the machine's swirl meter, the melt meter, the
  heavy-tray rule, the pool drain scene, the ally state.
- **Art:** the user's character from his photo (sit, eat, wave, the moment), the kid (walk, squirt,
  run, eat), the queue's bodies, the fans, the painter, the gym's two, the spa's staff for later; her
  wall jump and slide, the swirl, eating with him, the hot tub, the ice cream; Bumbot's wet shake;
  the three cones, the canister, the deck chair, the wet patch, the lever and hatch, the paw prints;
  "Splashed", "Slipped"; the gulls' swoop and glide.
- **Playtest:** `region6`: the socks, the beat and the drain, the hatch, the kid fed with a perfect
  cone, the refill, the table.

## Step 7: Outside (region 7)

**Done (2026-11-13),** but for the stern's tiers and deck 7's stern strip's slot: she is out of
sight there by the user's rule, so the climb is left out and the slot is on deck 8's first balcony.
What changed against this list: `docs/progress-decisions.md`.

- **Scope:** the balconies of decks 8-10 with partitions, rails, gusts, perched gulls, laundry lines,
  the sunbather; the ajar cabins and the four hallways with their beats (the steward on his rounds,
  the trays and the "Do Not Disturb" chain, the two sprinklers, the swinging doors); the balcony
  guest and book 7; the boat walkway finished (the station locker, the drill, the rival's glimpse);
  the stern tiers; deck 7's stern strip's slot; the hallways' ambient life (ice buckets, trays).
- **Systems first seen here:** gusts, the swoop on lingering, the clatter chain, the drill's swing,
  the hallway's one-way doors from a balcony.
- **Art:** the balcony guest, the sunbather, the drill crew, the steward on rounds; the lines, the
  trays, the swinging boat; "Swooped".
- **Playtest:** `region7`: out of the balcony cabin, up a deck, into a hallway, the guest let in,
  the walkway's ladder down to the promenade.

## Step 8: Top deck + funnel (region 8)

**Done (2026-11-13).** What changed against this list: `docs/progress-decisions.md`.

- **Scope:** deck 12 from Champs aft; the old lady, the cocktail, the engineer and the coffee,
  Teppanyaki's flare, the basketballs, the piñata, the court quirk; the roof, the stairway, the top:
  the horn, the telescope, the engineer's locker; the cascade: the card, the parasol, the gulls off
  the bow; books 8 and 9; the blocks lifted (paint, fans); the sun deck's, the restaurants' and
  Champs' ambient figures.
- **Systems first seen here:** the glide with its clip and gusts, the heat meter, the camera pan of
  the cascade, the horn pull, the telescope's view.
- **Art:** the old lady (sit, read, glare, doze, bolt), the engineer (idle, drink, climb, wave, read),
  the teppanyaki chef, the restaurants' and the court's figures; her glide clips, the horn pull; the
  parasol, the cord, the telescope, the basketball, the flare; "Singed".
- **Playtest:** `region8`: the climb from the machine, the coffee past the flare, the horn, the card
  and the parasol picked up, a glide down the atrium.

## Step 9: The bow (region 9)

- **Scope:** deck 12 forward: the wedding party, the planner, the cake and the pastry chef, the
  chapel's ceremony and slot, the Spinnaker's piano, the kids' pool's slide; the spa with its steam
  and staff; the officers' corridors and the captain's door; the kids' clubs with the fort and the
  ball pit; the bridge: near-catch 6, the alarm, the hatch; book 10 and the nook opened; the gold
  doors.
- **Systems first seen here:** the fragile tray, a crowd that moves on a flag, the alarm scene, the
  nook scene, the wade.
- **Art:** the planner, the guests, the pastry chef, the spa's remaining staff, the toddlers and the
  counsellor, the kids; her piano, wade and knock; the fort, the ball pit, the steam, the alarm's
  lights, the hatch; "Fogged"; the ceremony; the nook finished.
- **Playtest:** `region9`: the cake past the balls, the lobby clears, down the bow with the card,
  the bridge's beat, the hatch open, the nook.

## Step 10: Sunset (region 10) and the end

- **Scope:** the balcony forward of the spa, the sunset sky and sea, the glide with its gusts and two
  gulls, the mooring deck's catch, the way home with the user's character in the cabin, the win
  screen (its message: Later, §6.4), the mooring door.
- **Systems first seen here:** the sunset palette of the sky and sea, her state holding Bumbot, the
  catch's stand-still rule, the epilogue walk with nothing hostile.
- **Art:** her holding him (a state, its walk and stand), Bumbot's jump into her arms, the sunset.
- **Playtest:** `finale`: the hatch, the glide made and missed, the catch, the walk home.

## Step 11: The ship's side

Asked for by the user on 2026-11-13, during step 7: "give the ship's outer body a texture refinement
to make it look a bit more real, rather than just a white wall." Placed after the last region on
purpose: steps 8-10 still add to the outside (the funnel, the roof, the sunset's palette), and the
side is drawn once by the map builder, so one pass at the end covers everything and no region's
checks have to be redone.

- **Scope:** the closed shell as seen from outside and around the cut-away deck: plating seams and
  weld lines along the decks, a slight shade under each overhang and balcony slab, streaks of
  weathering below scuppers and portholes, the white broken into two or three near-whites from the
  palette, rivets or panel joints on the stern's sloped plating and the bow's flare, the boot
  topping at the waterline; the livery left as the user placed it. The balconies' recesses, the
  promenade's back wall and the boat walkway get the same treatment.
- **How:** in `tools/build_ship_map.py`'s shell drawing (and the pieces the game draws itself:
  the stern plating, the sun cover), by rules, in the Resurrect 64 palette; no new PixelLab art
  unless a rule-drawn texture reads flat. Checked at 1:1 in the game and on `tools/render_ship.py`'s
  full picture, zone by zone against `reference/photos/side-full.jpg`.
- **Playtest:** the whole suite (the map is rebuilt); close-ups of the bow, midships, the stern,
  the balconies and the walkway shown to the user for approval before the commit.

## After the regions

- **Sound on:** the synthesised effects for every entity, in the order of the regions; the horn and
  the alarm first.
- **The controller:** the mapping of §3.1 tested on the Xbox pad through the whole route.
- **Tuning:** the checkpoints' spacing, the hazards' periods and the carries' meters from her
  playtest; the tangerine count.
- **Her playtest, and the hidden extras:** the user's pictures into the six slots, the ten titles,
  the name plates.
