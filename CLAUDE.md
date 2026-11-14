# Bumbusik

A browser platformer, a gift for the developer's wife: she plays Bumbusik, a cruise ship crew member
chasing the stowaway cat Bumbot around a Norwegian Sun-like ship. **`GAME_DESIGN.md` is the source of
truth**: read the relevant section before any design or content work, and record new decisions there
(tagged Decided / Proposed / Open / Later).

## Stack and running

- Phaser 4.2.1, vendored (`vendor/phaser.min.js`); plain JS ES modules; no npm, no build.
- Run: `python tools/serve.py` (caching off, so reloads are never stale), open
  <http://localhost:8000>. URL flags: `?play` skip title,
  `?reset` clear save, `?debug` bodies + state, `?cards=all` every key card (key cards are off for now; `?cards=locked` turns them on), `?tangerines=infinite`, `?at=pool` start at a
  named place (list in `README.md`; for testing), `?sound` (sound is off for now). Dash is D.
- Hosted on GitHub Pages from `main` root: every asset path must be relative.

## Layout

| Path | What |
|---|---|
| `src/config.js` | All tuning: scale, speeds, jump, dash |
| `src/scenes/ShipScene.js` | The game: map, objects, player modes (play, ladder, stairs, trunk, lift, scripted), scares, dash, checkpoints, card-locked stairs, escape trunks, elevators, walls with doors between the ship's parts (`bulkhead`), Bumbot's near-catch (his beats: §6.1.8, not placed yet) |
| `src/sea.js` | The sea, drawn in code: rows of moving waves, foam along the waterline running on past the stern into the wake, the bow wave, the wake (§5.2) |
| `src/background.js` | The far background, drawn in code: the Baltic archipelago, the far sea, the clouds, the far gulls (`FarGulls`, shared by every view), fixed to the screen and laid out each frame, the horizon settling over her floor (`HORIZON_ABOVE`); in the outside view on the waterline. The sea-view windows show a masked copy of it (`addWindowView()` in ShipScene) (§5.2) |
| `tools/ship_layout.py` | **The ship's layout**: decks, stair cores, atrium, escape trunks and every venue in metres from the bow (bow on the left). Edit positions here |
| `maps/ship.json` | Tiled-format map of the whole ship (placeholder art), **generated** from the layout by `python tools/build_ship_map.py` |
| `docs/ship-profile.svg` | Side schematic of the ship, drawn from the layout by `python tools/draw_ship_profile.py`; shown in `GAME_DESIGN.md` §5.3 |
| `reference/` | **Git-ignored**: NCL's ship map PDF and its side profile (also flipped to bow-left), the source of real proportions. Copyrighted, never commit |
| `assets/source/<char>/` | Raw PixelLab frames, kept so sprites can be rebuilt without regenerating |
| `assets/sprites/` | Built sheets: run `python tools/build_sprites.py` after changing sources |
| `assets/ship/` | The ship's art atlas (doors, furniture, fittings, each with a muted `-bg` twin), built from `assets/source/ship/` by `python tools/build_ship_art.py` |
| `tools/draw_cabin.py` | Cabin 8206 (the user's own, deck 8), drawn by hand from her photo: its inside and its open door, the shower room's door and the shower scene's pieces (stall, door slid open, see-through glass, the towel on its handle) |
| `assets/source/her-towel/` | Her towel-turban look (after the cabin's shower): PixelLab's "Towel turban" state of her character, `e2632c97-abd6-4f52-886f-ccf10b34b28d`; only the clips she uses in the cabin; built into `assets/sprites/her-towel.png` |
| `tools/estimate_skeleton.py` | PixelLab's skeleton estimate for PNGs (0.1 generations each): poses to give a new state of her character the exact motion of an existing clip |
| `tools/build_ship_art.py` options | Per piece: `height` shrinks a PixelLab piece to her scale, `join`/`from_x` mend pieces drawn across two frames, `flat` squares a base, `legs` runs short legs down to the floor, `caption` blanks a name the sheet wrote into the frame |
| `tools/draw_chapel.py` | The Chapel (deck 12), drawn by hand from her photo: its inside and its open door (run after `build_ship_art.py`: its chairs and flowers come from the atlas) |
| `tools/draw_linen.py` | The linen room (deck 9, a heap of towels on its floor, the vent high on its far wall, the chute's hatch by the door), drawn by hand: its inside, its open crew door, and the laundry cart she pushes under the vent (`assets/ship/linen-cart.png`) |
| `tools/draw_lifeboat.py` | The ship's boats, drawn by hand in code (PixelLab's tries didn't read): the lifeboat, the tender, the rescue boat (`assets/ship/lifeboat.png`, `tender.png`, `rescue-boat.png`) |
| `tools/build_livery.py` | The ship's sun livery from its PixelLab tiles (`assets/source/livery/p2-*.png`) to one picture at full size (`assets/source/livery/livery.png`); then `build_ship_map.py` cuts it by deck into `assets/ship/livery.png` + `.json`. Its placement (`SHIFT`, `DROP`, `DISC`) is the user's. `tools/livery_photo.py` makes the tiles' generation inputs from the user's side photo |
| `tools/render_ship.py` | The whole ship from outside at full size, every deck closed (`ship-full.png` in `%TEMP%/bumbusik-playtest/exterior`); in the game, O shows it too |
| `docs/build-plan.md` | **The build plan**: step 0 the skeleton, then one step per region in play order, each with its scope, systems, art, playtest and exit; §8 names the current step |
| `docs/population.md` | **The population spec**: every person, hazard, item, secret, room and scene in place (deck, metres, behaviour), the corridors designed beat by beat; the build populates the ship from it (§6.1.13, phase 1) |
| `tools/draw_regions.py` | The progression plan (§6.1) drawn on the real ship (`docs/ship-regions.png`, `docs/ship-unlock-order.png`), from its own lists of regions, routes and steps; needs `tools/render_ship.py`'s picture |
| `tools/palettize.py` | Converts any image to the Resurrect 64 palette (`assets/palette/`) |
| `tools/population.py` | **The plan's world as data**: rooms behind doors, checkpoints, tangerines, pickups, Bumbot's beats, pushables, grips; `tools/build_world.py` turns it into `maps/world.json` (written with the map by `python tools/build_ship_map.py`) |
| `src/world/world.js`, `verbs.js` | The plan's world in the game: builds everything in `maps/world.json` (rooms, the outside route of promenade, boat walkway and balconies, the duct, the funnel's top, things in place), answers E, ladders and grips; her verbs (crawl, wall jump, glide, push), mixed into the ship scene |
| `src/world/people.js`, `carry.js`, `story.js` | The ship's people (loops, bubbles, what touching them does); carrying a tray and its rules; the story's own moments, one part per region |
| `src/world/library.js`, `movers.js` | The Library's books (the return trolley, the shelf with ten gaps, the reading chair and its pages, the full-screen panel for a page or a photo slot); things that move by themselves or answer her coming (the delivery robot she rides, the shy gulls, the stage's swinging light, the casino's chips; deck 9's vacuum that darts out, towel stack, sprinkler, door that flies open, "Do Not Disturb" door) |
| `src/world/lido.js`, `hazards.js` | Region 6's part of the story, mixed into the Story (the pool's scene and its draining, the kid with the water pistol, the soft serve machine's swirl, the table with her husband, the chess set, the hot tub); the pool deck's and the hallways' hazards (the wet patch and its deck chair, the gulls that dive at food, the buffet queue, the trays outside a "Do Not Disturb" door) |
| `src/world/outside.js` | Region 7: the balconies' own things (gusts, the gulls perched on the rails, laundry lines across a folded partition, balconies with someone on them), the boat drill on the walkway, the steward on his rounds; and its part of the story, mixed into the Story (the ajar balcony doors, the guest locked out on his balcony, the security officer at a tender). The vault over a partition and the climb up its pole are in `verbs.js` |
| `src/world/topdeck.js` | Region 8: deck 12's and the funnel's own things (the old lady's sunbed, the court's basketballs, Teppanyaki's flares, the funnel's wind and circling gulls, the flocks on the bow) and its part of the story, mixed into the Story (the mojito, the engineer's coffee, the horn and what it sets off, the telescope, the court's shot). The glide's rules are in `verbs.js` and the ship scene (`overTheRail`) |
| `src/world/bow.js` | Region 9: the bow's own things (the sauna's steam, the kids' club's ball pit, the step class's boards, the bridge's alarm) and its part of the story, mixed into the Story (the wedding planner and the cake, the party into the chapel and the ceremony, the piano, the slide, the captain's door, near-catch 6 with the net on the alarm panel and the hatch's ladder, the Library's odd book and the nook). A fragile load's sway is in `carry.js` (`SWAY`) |
| `tools/unchair.py` | Takes out a chair PixelLab drew under her in a seated clip (`assets/source/her/<clip>/` to `<clip>-clean/`), so she can sit on the game's own chairs |
| `tools/cast.py`, `fetch_people.py`, `build_people.py` | The people's PixelLab characters, the download of their frames (`assets/source/people/`), and the sheet `assets/sprites/people.png`; `tools/fetch_her.py <animation>` does the same for a new clip of hers |
| `tools/check_people.py` | The people checked against her: everyone standing next to her, heads against a pixel ruler (`--heads`), every clip of a figure (`--clips`); pictures in `%TEMP%/bumbusik-playtest/`. Run it on every new figure before making its clips |
| `tools/shoot_people.py` | Every person (or those named) in place in the game, close up beside her, tiled into sheets: facing, overlaps, what they stand on (see "Looking closely") |
| `tools/check_overlaps.py` | Overlaps that make no sense, by rule, from the running game: doors, plates, signs and wall pictures against furniture and each other, in two states of the story; `--shots` tiles a close-up of each. Must list nothing at a step's end |
| `tools/draw_rooms.py` | The plan's rooms drawn by hand in code (`assets/ship/rooms/<id>.png`); a room with no drawing is bare in the game. Also the blanket fort drawn in front of her (`adjoin-fort.png`) and the looks down through the duct's grilles (`assets/ship/peeks/`) |
| `tools/build_things.py`, `draw_pages.py` | The plan's own things from PixelLab map objects (`assets/source/things/` to `assets/sprites/things.png`: the robot, the gulls, the towel animals); the ten books' pages drawn in code (`assets/ship/pages/`) |
| `docs/progress-decisions.md` | **The autonomous build's log** (the user's order, 2026-11-13): every change or addition to the plan made while building, with its reason, step by step |
| `tools/playtest.py` | Headless Chrome playtests with real key presses; `python tools/playtest.py [scenario]`. Positions come from the map builder |

## Rules that are easy to break

- Scale: one deck = 144px; she is 59px tall in an 84px cell, feet on the cell's bottom row. Every
  human-sized thing (doors, furniture, railings) is sized to her, never to the ship.
- No death: failures are "scares" (run off, long fall out of frame, life ring overboard). Never use
  the word death, in code or on screen.
- Nothing floats: every object rests on or hangs from something plausible.
- Sprites face east; west is `flipX`. Background props are muted so they never read as interactive.

## Looking closely: the check on everything placed

The user found three things in step 8's screenshots that the build's own checks had passed (the
people's mixed proportions, a parasol that did not read as one and was not in her hand, a runner
with her back to her treadmill's console): the checks had been wide screenshots and tests of
behaviour, and none of these shows in either (2026-11-13). **So every person and thing a step
places is looked at enlarged, next to her, before the step is called done,** and these are asked
of each:

1. **Proportions:** is it drawn to her standard (a person: `python tools/check_people.py`, the
   head ruler; a thing: its real size next to her 59 px)? The same in every frame of its clips?
2. **Does it read?** Shown alone at the game's size, would the user name it without being told?
   A thing drawn in code that is only a few rectangles usually would not: draw it properly or
   make it a PixelLab map object.
3. **Which way does it face?** A person using something faces the end they use (a treadmill's
   console, a bar's counter, a screen, a table's middle). Look at the piece's art to see which
   end that is: the data's `face` is a guess until it is seen.
4. **What does it overlap, and in what order?** Someone inside or at a piece of furniture has
   the part nearer to us drawn in front of them (`cover` in `tools/population.py`: a handrail, a
   counter). A body through a post, a head through a sign, feet in a table are wrong.
5. **Is it held?** For anything in a hand, hers or theirs: find the fist's pixels in every frame
   of the clip, put the thing's grip there, and draw the hand over it (the thing behind the
   figure), not the thing over the hand. Compose the sprite and the thing at the game's offsets
   and look at it at 8x before trusting it.
6. **What holds it up?** Nothing floats, and nothing stands that could not: a furled parasol
   leans on something, a cup is on a surface, a seated person has a seat under them.
7. **Before and after:** look at the spot in each state the story gives it (the old lady there
   and gone), since what a thing leaned on may leave.
8. **What are they doing?** Would the user, shown this person alone, say what they are doing
   and why here? Two dancers sat on the floor of an aisle read as two people fallen over ("they
   look weird and out of place", the user, 2026-11-14); a crewman cranked a winch that was not
   drawn. A pose needs its reason in the picture: the seat, the tool, the person they talk to.
9. **Doors, plates and signs clear of everything:** a door with furniture on it, a plate across
   a speaker stack, a checkpoint's door in a window wall are wrong whichever is drawn on top
   (the user, 2026-11-14: the stage door and its plate on the speakers). This one is checked by
   rule, not by eye: `python tools/check_overlaps.py` must list nothing.

Tools: `Browser.close_up()` in `tools/playtest.py` (a spot enlarged, a deck cut open while she is
elsewhere); `python tools/shoot_people.py [ids]` (every person in place, tiled);
`python tools/check_people.py` (proportions, heads, clips); `python tools/check_overlaps.py
[--shots]` (every door, plate, sign and wall picture against what stands by it, from the real
bounds in the running game; what is meant is listed in its `ALLOWED`, each with its reason).
**When a picture is looked at for one thing, look at all of it:** the stage door's overlap was
in a close-up taken to check the stage manager, and was missed. Composing sprites offline with PIL at
the game's offsets is exact and needs no browser. When one instance of a fault is found, look
for the rest of its kind at once (one chibi figure meant twenty-four; one seated figure too big
meant five).

## Art: PixelLab (MCP)

- Generations cost money (Tier 1 month: 2000 generations until 2026-11-30). **State the cost and
  ask before spending generations.** Several jobs can run at once.
- For her animations use `skeleton-v3` mode: it moves her stored sprite instead of redrawing it, so
  hair and proportions stay consistent. Template mode redraws and drifts.
- Save raw output to `assets/source/`, convert with the palette tools, never commit reference photos.
- Her PixelLab character (all animations come from it): **"Bumbusik (final)"**,
  id `ebd5dadc-1318-4717-b0c0-6f429a7a58f0`, 4 directions, 64px. Earlier tries are kept on PixelLab
  for comparison; don't animate those.
- Bumbot's PixelLab character: **"Bumbot (final)"**, id `81f4c718-6c1b-43aa-b3e0-da0cfdd7c855`, 4
  directions, 48px canvas: our hand-shrunk sprite imported, not generated. The 48px candidate it
  came from (`assets/source/bumbot/pixellab/`) and the other tries are kept for comparison.

Lessons learned (2026-10-31):

- **Never name an object in an animation's `action_description`** unless it should be drawn:
  "bends down to pick up a cat" drew a cat into her hands. Describe only the body.
- Frame URLs come from `get_character` (the job reply has no animation id). Downloading them from
  backblaze.pixellab.ai needs a `User-Agent` header and the URL's `?t=` token, or it returns 403.
- Characters don't come out smaller than ~28px tall, and small redraws lose the likeness. To get a
  smaller sprite, shrink a bigger design ourselves (box-resample, snap to Resurrect 64) and import
  it with `create_character` v3 + `reference_image_url` + `direction_images` (0.25 generations).
- skeleton-v3 custom poses are humanoid only; for Bumbot use template clips (`running-8-frames`,
  `licking`, `jump`, `sitting`, `eating`) in skeleton-v3 mode, or v3 text mode.
- Generated frames sit at slightly different heights: anchor planted-feet clips with `"feet"` in
  `tools/build_sprites.py`, or the clip floats a pixel.
- Upload local images with `get_upload_url` + curl, then pass `upload:<id>`; never inline base64.

Lessons learned (2026-11-06, decks 9-11):

- **Object sheets draw every piece about her height**, whatever it is: give each piece its real
  size with the `height` option in `tools/build_ship_art.py` (a cup is a few px, a console ~46).
  A piece can run across two frames (`join`), or a frame can hold a neighbour's end (`from_x`).
- "Facing left" in a sheet's description is not reliable: check which way chairs face in the game
  (`around()` in the map builder has `faces_left`).
- `create_map_object` with `view: "side"` gives a strict side view when the description says
  "completely flat front elevation, no depth" (1 generation a try); "seen from the side" alone
  drifts to three-quarters.
- **Room views, as the user settled them:** a small room behind a door shows in the corridor's
  place with the deck around it dimmed (cabin 8206, the linen room: `rooms`, `ROOM_DIM`); a part
  of a deck behind a wall across it has its own piece of the ship's side, cut open only while she
  is in it (the bridge, the spa: `shell_rooms()`, `bulkhead` objects, E opens their side-on doors).
  Open terraces past a wall keep the ship's side closed and their sloped plating and floor edge
  always drawn (`outdoors` areas, `on_stern_terrace()`).
- Things that reach below a deck's floor (deck 11's pool tanks, ladders) must not show in the deck
  under it: check the deck below too after placing them.
- Playtest screenshots: `spawnAt` now snaps the cut-away, but give fades a second after moving her
  by hand in a script.

Lessons learned (2026-11-07, deck 12, doors, the outside):

- **Photos of the ship's side are never quite side-on.** Taken from forward of the ship, they show
  the superstructure's front face: its band of bridge windows and its hooded windows are the front's,
  not the side's; don't draw them on the side (the user caught it). They also stretch the bow. A
  trial moving decks 8-12's fronts aft into a slope as in the photos broke too much inside and was
  dropped: the fronts stay where NCL's profile has them.
- The outside's references: the side photo at full size `reference/photos/side-full.jpg` (from
  `side_view_from_outside.heic`; HEIC opens with `pillow_heif`), the user's two videos and a photo
  in `reference/videos/` (frames pulled with OpenCV into `reference/videos/frames/`). Map the photo
  to metres (bow tip to stern) and compare with our render at the same scale, zone by zone.
  Wikimedia Commons has almost no side-on photos of the ship (the user checked); its API rate-limits.
- Don't take a deck's or an area's size from the photos without asking: the layout (deck lengths,
  rooms) is the game's, and the user prefers keeping it to matching a photo.
- **Generated art far bigger than a generation (512 px max), like the livery:** straighten the
  photo, cut it into tiles at a third of the game's scale, generate each (img2img), then a second
  pass from the first with its leftovers (windows) painted over; snap each tile's few exact colours
  to the palette by rules, enlarge each colour smoothly, and fix the rest by hand-set filters
  (exact shapes, like the sun's disc, drawn exactly). Cleaning that deletes pixels makes holes:
  the user saw them at once. Check the result at 1:1 and in the game, not only scaled down.
- **Close-ups for the user** (the sea at the stem or the stern, anything off her route): in a
  playtest script, `cam.stopFollow()` then `cam.centerOn(x, y)` on the spot, wait a moment, shoot,
  and crop and enlarge with PIL to check the pixels.
- A long fall (§5.6) is measured from where she last stood, which can be a bulwark's top 32px over
  its floor: a fall rule's margin must cover anything she can stand on (`LONG_FALL_MARGIN`; the user
  fell through at deck 9's stern bulwark). A headless sweep of jumps from many spots finds such
  "sometimes" bugs fast.
- **Phaser 4 has no `setMask` in WebGL**: use the Mask filter, `obj.enableFilters();
  obj.filters.internal.addMask(gfx)`, with `gfx` from `this.make.graphics({ add: false })` in world
  space (it is redrawn each frame). The windows' live view is a container masked that way.
- `cam.startFollow()` clears the follow offset: set `setFollowOffset(0, HALF)` again after it (the
  outside view lost it, and the camera sat half her height low after it).
- `Graphics.fillPoints` can't fill an outline that crosses itself: it draws stray triangles
  elsewhere (a white wedge over deck 4's corridor came from the bow plating's outline).
- To tell whether a glitch is new, shoot the same spot on `main` from a worktree
  (`git worktree add <temp> main`, run that copy's `tools/playtest.py` helpers); to find which
  object draws a pixel, hide groups of objects in a playtest script and bisect.
- Things drawn over the ship's side straddling the edge of a cut-away (a room's piece of shell, a
  deck's end, the fixed stern plating) are skipped by `span_owner()`: end runs of windows short of
  such edges, or draw a band piece by piece.

Lessons learned (2026-11-08, the background, the windows, the cabin's shower):

- **A new state of her character** (`create_character_state`, 10 generations) keeps her look but
  can lose small features: check its profile against hers at the pixel level (the user caught a
  missing far eye and a changed lower face) and mend it by hand. PixelLab keeps its own copy,
  which template animations of the state use; skeleton-v3 redraws the head slightly in each
  frame, so a fix can't be pasted onto those frames automatically.
- **Giving a state the same motion as her existing clips:** templates (`running-8-frames`,
  `jumping-1`) via `animate_character(mode="skeleton-v3")`; custom clips by estimating each frame's
  skeleton (`tools/estimate_skeleton.py`) and passing them to `animate_with_skeleton_v3` with the
  state's pose padded to the clip's canvas (64 px poses sit in 96 px frames, 16 px all round).
  Check the estimates: one frame came back mirrored (left and right swapped) and was replaced by
  its neighbours' average. The base character's animations can't be extended to a state.
- skeleton-v3 may add things (lather on her hair while she washes it): look at every frame.
- A long Python patch full of quotes, backticks and backslash escapes breaks a bash heredoc:
  write it to a file in %TEMP% and run that.
- **Not every open deck is an `outdoors` area** (the bow's mooring deck, the open parts of decks 11
  and 12 keep their deck cut open): to tell whether she is out in the open, look for a shell tile
  at her column at that deck's height (`updateDeckDim()`). Things on other decks are drawn in front
  of her (`DEPTH.player + ...`), so a dim that must cover them goes above her too and clears the
  part she is in.

Lessons learned (2026-11-13, the people's proportions):

- **Everyone is drawn to her proportions** (the user): a head of 14 to 20 px, hair in and hats out,
  on a figure about 60 px tall (hers: 17 of 59). v3 characters from text come out chibi about one
  time in five (a 22 to 25 px head on a squat body), and no wording prevents it. Check each new
  figure with `python tools/check_people.py --heads <name>` before making clips.
- **What holds the proportions: `create_character(mode="pro", style_character_id=...)`**, size 64,
  view "side" (ten generations): the drill's officer `3ed991ae-cf74-4ce1-a636-8549344290a6` for
  men, the cabin maid `4677d8f1-5586-41e1-b13e-53d9bdd49ffc` for women. Build and things asked
  for in the description still come ("stout, round belly", "holding a net").
- **A seated figure comes as tall as a standing one:** give it `"scale": 0.8` in `tools/cast.py`.
- A template clip (breathing-idle, walking) redraws the figure and may shrink it by half a head;
  `mode="skeleton-v3"` with the same `template_animation_id` (three generations) keeps its size.
- v3 text clips may turn the figure to face us or draw effects (sparks) into the frames: look at
  every frame (`check_people.py --clips`), and ask for "seen from the side the whole time".
- The game plays clips that `tools/cast.py` does not name (its dict is only their speeds): before
  replacing a character, list the clip folders in `assets/source/people/<name>/` and what
  `tools/population.py` and `src/world/*.js` ask of it. The download of a character is refused
  (HTTP 423) while one of its animations is still being made.
- **A held thing is placed by her fist, not by eye:** the parasol sat 8 px off her hand and was
  drawn over it. Her fist in the glide's frames is 6 to 9 px in front of her middle and 49 to 53 px
  over her feet; the shaft comes out of it and the parasol is drawn behind her.
- **A person on a machine:** the gym's runner faced away from her treadmill's console and covered
  its handrail. Check each piece's working end in its art, and give the person `cover` so the
  near part of the machine is in front of them.
- **A thing with stripes is cut shorter, not shrunk** (`CUT_ROWS` in `tools/build_things.py`), and
  PixelLab's muddy reds are swapped for the palette's after the conversion (`RECOLOUR`).

Lessons learned (2026-11-14, the end of the art review):

- **A door the plan adds is placed against what is built there, not by its metre alone:** seven
  of the plan's doors (rooms, checkpoints) stood on built furniture or in a window wall. Before
  placing one, list the builder's pieces within a metre of it; after, run
  `tools/check_overlaps.py`. Where no wall is free, move the furniture a little or take one
  piece out (a seat in a row), rather than squeeze the door in.
- **On the outside route a prop never takes `back`:** that depth is behind the ship's side, and
  the boat drill's rope was never seen. Outside, a thing is behind a person by default.
- **A playtest walks until she is there, not for a time:** `region8`'s climb failed one run in
  three because a fixed 3.2 s walk sometimes ended a few steps short of the rail
  (`hold_until`, not `hold`).
- A person all in dark clothes is not placed on a dark set: the stage manager in black stood
  on the dark stage, in the drum kit; he is in front of the red curtain now.

Lessons learned (2026-11-14, step 9):

- **A sprite sheet is packed in rows, never one strip:** her strip passed 16,384 px with two new
  clips and she drew as a black box while every test passed. `tools/build_sprites.py` packs rows
  of 48 cells; the `boot` playtest fails on any texture over 8,192 px a side.
- **Look at a scenario's screenshots before calling it passed:** that black box, a rope the
  wedding party walked through and a photo frame on a guest's hat were all in pictures of a
  scenario whose checks were green.
- **A close-up's scale comes from the canvas, not the window** (`Browser.close_up()` measures
  it): the game is fitted into the headless window at about 1.7 px a game px, not 2.
- PixelLab map objects: ask for "one ... filling the whole picture from the left edge to the
  right edge" when a long thing must be one piece (a fort came as two tents); a person on
  furniture comes at the right size when the canvas is about what it should measure (a seated
  adult: 40 x 52).
- A scratch script must not be named after a standard module (`bisect.py` broke every script
  beside it); and `git add` takes `-u` plus the new paths by name, never `-A`, which takes in
  files that are not this work's (the user's `docs/intro.md` went into a commit that way; they
  kept it there).

## Working with the user

- **Start each session from `GAME_DESIGN.md` §8 "Next up"**: it records where work stopped. The
  user works on one computer but often starts new sessions, and power outages have cut sessions
  off (2026-11-07), so progress lives in the repo (design doc, this file, commits, pushed to
  `main` once approved), never only in local memory or uncommitted files.
- Design is settled by numbered question lists; the user answers by number.
- **Before furnishing a deck, check NCL's plan** (`reference/norwegian-sun-ship-map.pdf`: its
  profile lists each deck's rooms by part of the ship; `pdftotext -layout` or PyMuPDF's words) and
  the user's photos of that deck, then propose the layout and the art cost.
- When a generated piece doesn't read as intended, offer to drop or replace it rather than re-rolling
  again and again: the user prefers removing it to over-iterating. Free fixes are fine to just do.
- Work on a feature branch; merge to `main` and push only when the user approves.
- **Every game link given to the user includes `&tangerines=infinite`** while we develop, e.g.
  <http://localhost:8000/?play&at=library&tangerines=infinite> (the user's wish). **Whenever you
  ask the user to try or check something, give the link**, starting as near the spot as `?at=`
  allows, and say where to walk from there.
- **After each change, show the result and stop for the user's review** (screenshots in the chat,
  plus the link when there's something to try). Don't carry on into test runs, commits or the next
  change before they answer (the user, 2026-11-06: iterations were too slow, and twice I went on
  without asking). Don't run the whole `tools/playtest.py` suite after cosmetic tweaks; run it once
  a round is approved if gameplay or layout changed (map builder, physics, routes, triggers), and
  always before a merge. Commit and update `GAME_DESIGN.md` once per approved round.
- Do only what was asked: when a request could reach further (another deck, a layout change),
  ask first rather than assume (the user, 2026-11-06).
- The user circles things on screenshots and numbers them; fix each, show the result as
  screenshots in the chat, and say plainly what changed.
- **To approve a piece of art, show the user the image in the chat** (a preview or screenshot) and
  ask; don't send them to launch the game for it.
- Test in headless Chrome (the user uses Chrome, not Edge). Keep image viewing and tool output lean:
  the user watches session usage.
