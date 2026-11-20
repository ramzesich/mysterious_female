# Bumbusik

A browser platformer, a gift for the developer's wife: she plays Bumbusik, a cruise ship crew member
chasing the stowaway cat Bumbot around a Norwegian Sun-like ship. **`GAME_DESIGN.md` is the source of
truth**: read the relevant section before any design or content work, and record new decisions there
(tagged Decided / Proposed / Open / Later). **What is left to build is in `docs/plan-the-rest.md`**
(2026-11-18: everything the documents still call open, checked against the code, in the order to build it).

## Stack and running

- Phaser 4.2.1, vendored (`vendor/phaser.min.js`); plain JS ES modules; no npm, no build.
- Run: `python tools/serve.py` (caching off, so reloads are never stale), open
  <http://localhost:8000>. URL flags: `?play` skip the welcome screen and the intro, `?intro=<part>` start the intro at a part,
  `?reset` clear save (**nothing is saved for now**, the user, 2026-11-16: every load a new game, `DEV_FRESH` in `src/config.js`; `?real` keeps the save, and every playtest opens with it), `?debug` bodies + state, `?cards=all` every lock open and every verb known (**the locks are on**, since step 0: `KEY_CARDS.required` in `src/config.js`; there is no flag to turn them off but this one), `?did=<flags>` start with story flags set (`README.md` has examples), `?tangerines=infinite`, `?at=pool` start at a
  named place (list in `README.md`, a link for each in `docs/start-links.md`; for testing), `?sound=off` (sound is on; M mutes it in the game), `?lang=ua` (Ukrainian for a session). D is the cry and the lunge, F the throw (`docs/plan-three-uses.md`).
- To be hosted on GitHub Pages from `main` root: every asset path must be relative. **Since
  2026-11-17 Pages serves the orphan branch `placeholder`** (her silhouette, no words): a push to
  `main` does not publish the game, and `placeholder` is never merged. Switching Pages back to
  `main` is a step of the release (`docs/plan-the-rest.md` §6).

## Layout

| Path | What |
|---|---|
| `src/config.js` | All tuning: scale, speeds, jump, the cry and the lunge (`CRY`, `LUNGE`); `MISHAPS`, every obstacle that can hit her by its own name (`scareContact(fromX, name, { vx, dir })`), and `MISHAP_SCENES`, each scenario of a hit (her word, her gag or what stands in for it; **a hit is its gag and her checkpoint whatever she carries**, the user, 2026-11-19; only a gull that comes down on her, `pocket: true`, takes a tangerine instead: the ship scene's `pocket()`); which scenario a hit is, by its side and who was moving: `src/world/mishaps.js` (docs/plan-three-uses.md §1.6); `TALLY`, a tangerine's flight to the count |
| `src/scenes/ShipScene.js` | The game: map, objects, player modes (play, ladder, stairs, trunk, lift, scripted), scares, D (`tryCry`: the cry, and the lunge once learned; `lungeSafe()` turns a fright by contact into `world.lunged()`), checkpoints, card-locked stairs, escape trunks, elevators, walls with doors between the ship's parts (`bulkhead`), Bumbot's near-catches (`nearCatch`; his six beats of §6.1.8 are placed: `BEATS` in `tools/population.py`, his glimpses in `src/world/`) |
| `src/progression.js`, `src/save.js` | The locks and what opens them (the regions she has opened, her cards, the flags; flights of stairs, doors in the walls across the decks, end walls, the lifts' landings: `passes()`), from the map's data; the save (in the browser, written at every checkpoint: what she has activated, collected, broken, opened, her cards, verbs, books, the loose tangerines, the things found, `keeps`). **Nothing is kept between loads for now** (`DEV_FRESH` in `src/config.js`, "set to false before the gift") |
| `src/main.js`, `src/scenes/BootScene.js`, `src/textures.js` | The Phaser config and the page's start; the loading of every sheet, atlas and map; the few sprites still drawn from text pixel maps at boot (the early placeholders, and `FRUIT`, the tangerine's picture) |
| `src/controls.js`, `src/rumble.js` | Keyboard and Xbox controller mapped to the same actions (§3.1; the whole mapping in its table there), the controller in use being whichever was touched last; the rumble's ten moments, only while she plays with the controller. The `gamepad` playtest drives a fake controller (`Browser.fake_pad()`) |
| `src/lang.js` | **Every text the game says, in English and Ukrainian** (the user, 2026-11-14): `t(key)`; the title, the win screen, a lock's popup, her exclamations. A new text goes here in both languages, never as a string where it is shown (the `lang` playtest fails when one language lacks a key). The ship's own signs and plates stay as they are in both, and her «Кісюнічка!!!». `?lang=ua`; the welcome screen's LANGUAGE button switches it |
| `docs/intro.md` | **The user's own document, never edit it**: the welcome screen, the start sequence and the intro's scene. Built 2026-11-14 on the user's word |
| `src/intro.js` | **The welcome screen, the start sequence and the intro** (it ends on deck 3's corridor: her door opens, she steps out, straightens her badge, the hint; a close-up at her mirror was built first and dropped by the user), all in the ship scene's own picture: one clock (`T`) and everything a function of it (the camera, what is open, what is shown), its parts and their lengths in `PARTS`; `intro.seek(part, k)` shows any moment, Esc ends it, `?play` skips it, `?intro=<part>` starts at a part. A new game gets all of it; a game under way a short way in. While it runs the game holds still (`scene.intro`, `scene.fromAfar`: the ship closed and the sky laid out in the world) |
| `src/pixeltext.js`, `tools/build_menu.py` | **The welcome screen's menu art** (the user chose brass plates from three mock-ups, 2026-11-14): `assets/source/menu/` (two generated pixel letterings and a generated plate) to the atlas `assets/sprites/menu.png`; `pixelText(scene, key, font, text, style)` sets a word in it (`T` the name's lettering, `S` the plates'), filled in bands, outlined, shadowed. **The lettering is Latin; the Ukrainian capitals are built from its shapes in the build tool, so the menu is in capitals.** A new menu word needs its letters there (`missing()`; the `lang` playtest fails otherwise) |
| `docs/start-links.md` | A localhost link for every place the game can be started at (`?at=`), everything open and D free: add a line when the builder gets a new `place` |
| `src/sfx.js` | **Every sound, synthesised** (step 12): about 130 effects in seven groups, each with a line saying what it is for, made of two voices (`tone`, `noise`) and a few helpers (`bell`, `clank`, `thud`, `voice`, `applause`); `sfx.name()` at her ears, `sfx.at(x, y).name()` from a place in the world (fainter with distance, silent out of earshot); the ambience's five layers; mute (M). Volumes: `SOUND` in `src/config.js` and each effect's own line. **A gag's own sounds** (§3 1.3: `spin`, `bellyFlop`, `tiptoe`, `herCough`, `herSneeze`, `cartBump`, `trolleyRattle`, `headBonk`, `boatThump`, `towelFlump`) play on its clips' frames: `GAGS[...].sounds` in the config (clip key, frame from 1, effect), by the ship scene's `addedtoscene` hook on the gag sheets' sprites, for the gag of her last hit (`lastMishap`) |
| `src/world/soundscape.js` | What nothing in particular makes: the ambience's levels from where she stands (out on deck, inside, how high in the ship, by a pool), her footsteps by what is under her (`floor()`), rungs, a cart's wheels, strokes; the small steady sounds of a few places (`PLACES`) |
| `tools/check_sound.py`, `tools/soundboard.html` | Every effect rendered by the browser without playing it and measured (loudness, length, a spectrogram each on sheets in `%TEMP%/bumbusik-playtest/sound`): must end "all within bounds". The soundboard plays each by a button and has the ambience on sliders: <http://localhost:8000/tools/soundboard.html>, where the user listens |
| `src/sea.js` | The sea, drawn in code: rows of moving waves, foam along the waterline running on past the stern into the wake, the bow wave, the wake (§5.2); its sunset rows (`setDusk`) |
| `src/background.js` | The far background, drawn in code: the Baltic archipelago, the far sea, the clouds, the far gulls (`FarGulls`, shared by every view), fixed to the screen and laid out each frame, the horizon settling over her floor (`HORIZON_ABOVE`); in the outside view on the waterline. The sea-view windows show a masked copy of it (`addWindowView()` in ShipScene) (§5.2). The sunset (§6.1.9): a second sky and sea faded over the day's (`setDusk(k)`), the sun and its path; its colours are drawn divided by the evening light (`DUSK_LIGHT`, the ship scene's multiply wash) so that they look themselves under it |
| `tools/ship_layout.py` | **The ship's layout**: decks, stair cores, atrium, escape trunks and every venue in metres from the bow (bow on the left). Edit positions here. `CREW_DECK`: deck 3's crew corridor, the one played part of that deck, where the game starts (her cabin's door, the Medical Center's, the service ladder's); `PLAYABLE` stays decks 4 to 12, the ones the stairs and lifts serve |
| `maps/ship.json` | Tiled-format map of the whole ship (placeholder art), **generated** from the layout by `python tools/build_ship_map.py` |
| `docs/ship-profile.svg` | Side schematic of the ship, drawn from the layout by `python tools/draw_ship_profile.py`; shown in `GAME_DESIGN.md` §5.3 |
| `reference/` | **Git-ignored**: NCL's ship map PDF and its side profile (also flipped to bow-left), the source of real proportions. Copyrighted, never commit |
| `assets/source/<char>/` | Raw PixelLab frames, kept so sprites can be rebuilt without regenerating |
| `assets/sprites/` | Built sheets: run `python tools/build_sprites.py` after changing sources |
| `assets/ship/` | The ship's art atlas (doors, furniture, fittings, each with a muted `-bg` twin), built from `assets/source/ship/` by `python tools/build_ship_art.py` |
| `tools/draw_cabin.py` | Cabin 8206 (the user's own, deck 8), drawn by hand from her photo: its inside and its open door, the shower room's door and the shower scene's pieces (stall, door slid open, see-through glass, the towel on its handle) |
| `assets/source/her-mishaps/` | **Her mishap gags, each one picture of her with the thing** (docs/plan-three-uses.md §1.6): states of her character with the thing drawn in, animated v3 (ids in its README); built into `assets/sprites/her-mishaps.png` (`HER_MISHAPS` in `tools/build_sprites.py`, 112 px cells, each clip placed by its thing's middle); played by the ship scene's `rideGag` (`GAGS` in `src/config.js`) for a scenario with `gag`, when the thing that hit her passes `ride` (how it carries her: its way, its floor, `hide()`/`show()`), or by `fallGag` where she stands (the papers: the clip starts with her standing on the world's paper and is set down by where it is, `ride.x`; the breakfast stewardess's tray and trolley, 10a to 10f: on the corridor's floor, `ride.y`, the trolley drawn over her trip, `turn` for a hit at her back), or by `cartGag` with the porter (8a to 8d: he stands, pushes on, wheels her and tips his cap, or turns round). The world's vacuum and suitcase (`assets/source/things/robot-vacuum.png`, `suitcase-rolling.png`) are cut from the same pictures |
| `assets/source/her/stair-cling/` | Her hold on the funnel stairway's rail in a gust, facing up the flight and down it (`cling-up`, `cling-down` in her sheet, played by `updateStairs`); made on the steps with the rail where the game draws it, the generator's own rail taken out frame by frame (its README). `stair-slip/` beside it is retired |
| `assets/source/her-towel/` | Her towel-turban look (after the cabin's shower): PixelLab's "Towel turban" state of her character, `e2632c97-abd6-4f52-886f-ccf10b34b28d`; only the clips she uses in the cabin; built into `assets/sprites/her-towel.png` |
| `tools/estimate_skeleton.py` | PixelLab's skeleton estimate for PNGs (0.1 generations each): poses to give a new state of her character the exact motion of an existing clip |
| `tools/build_ship_art.py` options | Per piece (and `-lt`, a light wash for the theatre's pieces, `LIGHT`; `keep` (from, to): a piece's own canvas columns kept, for pieces that must stand at one spot, the theatre's seat and its ten sitters): `height` shrinks a PixelLab piece to her scale, `join`/`from_x` mend pieces drawn across two frames, `flat` squares a base, `legs` runs short legs down to the floor, `caption` blanks a name the sheet wrote into the frame |
| `tools/draw_chapel.py` | The Chapel (deck 12), drawn by hand from her photo: its inside and its open door (run after `build_ship_art.py`: its chairs and flowers come from the atlas) |
| `tools/draw_linen.py` | The linen room (deck 9, a heap of towels on its floor, the vent high on its far wall, the chute's hatch by the door), drawn by hand: its inside, its open crew door, and the laundry cart she pushes under the vent (`assets/ship/linen-cart.png`) |
| `tools/draw_casino.py` | The casino's roulette and blackjack tables and the Stardust balcony's parapet, drawn by hand in strict side view (PixelLab kept drawing them at three-quarters): `assets/source/ship/casino-drawn/` |
| `tools/draw_lifeboat.py` | The ship's boats, drawn by hand in code (PixelLab's tries didn't read): the lifeboat, the tender, the rescue boat (`assets/ship/lifeboat.png`, `tender.png`, `rescue-boat.png`) |
| `tools/build_livery.py` | The ship's sun livery from its PixelLab tiles (`assets/source/livery/p2-*.png`) to one picture at full size (`assets/source/livery/livery.png`); then `build_ship_map.py` cuts it by deck into `assets/ship/livery.png` + `.json`. Its placement (`SHIFT`, `DROP`, `DISC`) is the user's. Its outlines are smoothed along their length with the tips kept (`sleek()`, `SLEEK`; the user, 2026-11-14); leftover spots are filled by rule (`fill_spots`) or by a point inside them (`SPOTS`). **The user's own touches: `assets/source/livery/livery-by-hand.png`**, a copy of `livery.png` edited by hand (flat colours, no antialiasing), which `build_ship_map.py` uses in its place while it is there; never write it, and say so when `build_livery.py` is run while it exists (its changes then show only once they are copied over by hand). `tools/livery_photo.py` makes the tiles' generation inputs from the user's side photo |
| `tools/render_ship.py` | The whole ship from outside at full size, every deck closed (`ship-full.png` in `%TEMP%/bumbusik-playtest/exterior`, or the folder given), through the game's own outside view; in the game, O shows it too |
| `tools/shell_paint.py` | **The ship's side painted by rules** (step 11): the plating's seams, butts and shades, the shade under overhangs, weathering, the hull's marks and openings, as a picture the map builder cuts into tiles (after the placeholder ones in `assets/tiles/placeholder.png`, rows of 64); the parts the game draws itself get their pixels as marks (`shellSlopes`' `marks`, `stemMarks`, `plateSeams` in the map). Its colours and spacings are at its top |
| `docs/build-plan.md` | **The build plan**: step 0 the skeleton, then one step per region in play order, each with its scope, systems, art, playtest and exit. **All of it is built** (steps 0 to 12, 2026-11-14); its "After the regions" is carried on in `docs/plan-the-rest.md` |
| `docs/plan-the-rest.md` | **What is left, as one plan** (2026-11-18), in the order to build it: the rest of the mishaps' gags and their `mishaps` playtest; the rest of the twenty things to find, the fourteen books with their covers, cabin 8206's desk; the look-outs and the deliveries; each deck's own look; small faults; what waits for the user; what is done once at the end (the other documents, saving on, the release); what is closed. **The building session works from it and marks what it builds** |
| `docs/plan-three-uses.md` | **The three uses of a tangerine and the decks' life** (the cry and the lunge, the throw, the pocket; the mishaps' table §1.6; the twenty things to find, the look-outs, the deliveries, each deck's look): steps 1 to 4 and most of 4a are built, the rest is in `docs/plan-the-rest.md` |
| `docs/audit-2026-11-15.md`, `docs/plan-visual-fixes.md`, `docs/plan-fast-tests.md` | The user's audit (visual faults, empty decks) and the two plans that came of it and of the slow tests: the visual fixes and the stepped clock, both built whole |
| `docs/population.md` | **The population spec**: every person, hazard, item, secret, room and scene in place (deck, metres, behaviour), the corridors designed beat by beat; the build populates the ship from it (§6.1.13, phase 1) |
| `tools/draw_regions.py` | The progression plan (§6.1) drawn on the real ship (`docs/ship-regions.png`, `docs/ship-unlock-order.png`), from its own lists of regions, routes and steps; needs `tools/render_ship.py`'s picture |
| `tools/palettize.py` | Converts any image to the Resurrect 64 palette (`assets/palette/`) |
| `tools/population.py` | **The plan's world as data**: rooms behind doors, checkpoints, tangerines, pickups, Bumbot's beats, pushables, grips; `tools/build_world.py` turns it into `maps/world.json` (written with the map by `python tools/build_ship_map.py`). A pickup's options (2026-11-20): `from` (px up she must stand to take it: the plant, from the maid's bed), `cover` (the furniture's near part drawn again over it: the diary under its seat's arm); a ledge (`PLATFORMS`) may be in a room (her bed there) and name what is drawn over her on it; a person's `cycle` plays clips in turn (the maid: her bed-making twice, her stretch) |
| `src/world/world.js`, `verbs.js` | The plan's world in the game: builds everything in `maps/world.json` (rooms, the outside route of promenade, boat walkway and balconies, the duct, the funnel's top, things in place), answers E, ladders and grips; her verbs (crawl, wall jump, glide, push), mixed into the ship scene |
| `src/world/people.js`, `carry.js`, `story.js` | The ship's people (loops, a door on the way opened or turning them back: `door()`, bubbles, what touching them does, what her cry and her lunge do to them: `heard`, `lunged`; eating a tangerine from the hand, bite by bite, the fruit at the fist of each frame of their `bite` clip: `eat()`, `FISTS`; each mover has its own `heard()`/`lunged()`, `world.shout()` and `world.lunged()` pass the word on); carrying a tray and its rules; the story's own moments, one part per region |
| `src/world/tangerine.js` | A tangerine loose in the world (`LooseTangerines`, the scene's `loose`): thrown (F: `tryThrow`, `THROW` in the config; no hit knocks one out of her pocket since 2026-11-19), it bounces and rolls on her floors by its own route, rests, is kept in `save.loose`, picked up by walking over it, floats in a pool, is lost to the sea; offered each frame, lying or not, to whatever wants it (`world.offered(t)`: the scene's `offeredHere`, a lob into the piñata, each mover's `offered`, `people.offered`, `story.offered`; `loose.near()` is their test, `loose.claim()` hands one over, `world.gullTakes()` is any gull's). Its picture is `FRUIT` in `src/textures.js` (PixelLab's, chosen by the user; raw in `assets/source/tangerine/`) |
| `tools/hold_tangerine.py` | Puts the tangerine in her fist in her toss's frames (`assets/source/her/toss/` to `toss-held/`, which the sprite build uses) |
| `src/world/library.js`, `movers.js` | The Library's books (the return trolley, the shelf with ten gaps, the reading chair and its pages, the full-screen panel for a page or a photo slot); things that move by themselves or answer her coming (the delivery robot she rides, the shy gulls, the stage's swinging light, the casino's chips; deck 9's vacuum that darts out, towel stack, sprinkler, door that flies open, "Do Not Disturb" door; region 1's suitcase that rolls with the ship, the dog on a lead that fetches and trips her, the paper rounds, the breakfast round: `Roller`, `Fetcher`, `Skimmer`, `Breakfast`; a door's hand that takes things in is `world.handTakes()`, a round's doors are only those the corridor draws, `realDoors`) |
| `tools/check_corridors.py` | From the data alone: per deck, the longest walk with nothing to do and the longest without a reward (`docs/plan-three-uses.md` §4.7): run at the end of a step that places things on the decks, and give its numbers |
| `src/world/lido.js`, `hazards.js` | Region 6's part of the story, mixed into the Story (the pool's scene and its draining, the kid with the water pistol, the soft serve machine's swirl, the table with her husband, the chess set, the hot tub); the pool deck's and the hallways' hazards (the wet patch and its deck chair, the gulls that dive at food, the buffet queue, the trays outside a "Do Not Disturb" door) |
| `src/world/outside.js` | Region 7: the balconies' own things (gusts, the gulls perched on the rails, laundry lines across a folded partition, balconies with someone on them), the boat drill on the walkway (it answers her coming, as the flares do: `DRILL` in the config; 15 is 14a's fall with the boat down over her), the steward on his rounds; and its part of the story, mixed into the Story (the ajar balcony doors, the guest locked out on his balcony, the security officer at a tender). The vault over a partition and the climb up its pole are in `verbs.js` |
| `src/world/topdeck.js` | Region 8: deck 12's and the funnel's own things (the old lady's sunbed, the court's basketballs, Teppanyaki's flares (the chef answers her coming: `FLARE` in the config; her gag 19, `Flare.ride`), the funnel's wind and circling gulls, the flocks on the bow) and its part of the story, mixed into the Story (the mojito, the engineer's coffee, the horn and what it sets off, the telescope, the court's shot). The glide's rules are in `verbs.js` and the ship scene (`overTheRail`) |
| `src/world/bow.js` | Region 9: the bow's own things (the sauna's steam, the kids' club's ball pit, the step class's boards, the bridge's alarm) and its part of the story, mixed into the Story (the wedding planner and the cake, the party into the chapel and the ceremony, the piano, the slide, the captain's door, near-catch 6 with the net on the alarm panel and the hatch's ladder, the Library's odd book and the nook). A fragile load's sway is in `carry.js` (`SWAY`) |
| `src/world/finale.js` | Region 10 and the end: the wind over the bow and the two crossing gulls; and its part of the story, mixed into the Story (the sunset's scene, Bumbot at the tip who backs off and comes to her standing still, the catch, where a miss puts her back, those who clap her home, cabin 8206's scene, the win screen, the day after). Her look and rules with Bumbot in her arms are the ship scene's `holding` (`HOLDING` in `src/config.js`; her sheet `assets/sprites/her-cat.png` from `assets/source/her-cat/`, PixelLab state `6905f308-15b1-4a44-ad97-a38a7ad17dff`) |
| `tools/unchair.py` | Takes out a chair PixelLab drew under her in a seated clip (`assets/source/her/<clip>/` to `<clip>-clean/`), so she can sit on the game's own chairs |
| `tools/cast.py`, `fetch_people.py`, `build_people.py` | (Every folder in a person's `assets/source/people/<name>/` is built as a clip: a clip's own sources go beside it, as `kid-eat-cone/`.) The people's PixelLab characters, the download of their frames (`assets/source/people/`; the dog and its owner are kept by hand, `BY_HAND`), and the sheet `assets/sprites/people.png`, every clip's frames set on the floor (`OFF_THE_FLOOR` the ones that leave it); `tools/fetch_her.py <animation>` does the same for a new clip of hers |
| `tools/check_people.py` | The people checked against her: everyone standing next to her, heads against a pixel ruler (`--heads`), every clip of a figure (`--clips`); pictures in `%TEMP%/bumbusik-playtest/`. Run it on every new figure before making its clips |
| `tools/shoot_people.py` | Every person (or those named) in place in the game, close up beside her, tiled into sheets: facing, overlaps, what they stand on (see "Looking closely") |
| `tools/check_overlaps.py` | Overlaps that make no sense, by rule, from the running game: doors, plates, signs and wall pictures against furniture and each other, in four states of the story; `--shots` tiles a close-up of each. Must list nothing at a step's end |
| `tools/draw_rooms.py` | The plan's rooms drawn by hand in code (`assets/ship/rooms/<id>.png`); a room with no drawing is bare in the game. Also the blanket fort drawn in front of her (`adjoin-fort.png`) and the looks down through the duct's grilles (`assets/ship/peeks/`) ; what of a room is in front of the things lying in it (a bowl before its tangerines) is marked with `Room.in_front()` and saved as `<id>-front.png`, drawn over them |
| `tools/build_court.py` | **The court's two players** (deck 12; `assets/source/people/court/`, its README has the ids) to `assets/sprites/court.png` + `.json`: a man in red and a woman in blue, each a pro character with four clips made with the ball (the jump shot, waiting, the pick-up, a dribble), washed 12%. Played by `Balls` in `src/world/topdeck.js`: the round's clock sets their frame and the ball (from the hand through the ring, bouncing back to their feet; it hits her from the throw to its second landing); the game's ball turns to and from `basketball-lt` where it changes hands |
| `tools/build_towels.py` | **The towel stack's own clips** (deck 9; `assets/source/things/towel-fall/`, its README has the ids) to `assets/sprites/towels.png` + `.json`: its fall alone, the fall on her (from her standing, and four from her run's phases), her coming up in a towel turban with a towel swan, and the standing stack and stool apart. Played by `TowelStack`; the fall on her is a gag the thing plays itself (the ship scene's `thingGag`, `ride.play`) |
| `tools/build_gags.py` | **Step 4a's gags, each the thing's own clip with her** (`assets/source/her-mishaps/batch-4a/`, its README has the ids) to `assets/sprites/gags.png` + `.json`: the swinging door alone and slamming her flat (13a) and her slide down the wall, the same swing in full colours for the "Do Not Disturb" doors, her tray ride from four quarters of her stride (3; the world's tray base moved under her by the game, `trayAt`), the deck chair collapsing under her (7b; it cannot happen since the chair stands still, 2026-11-19), her dive face first onto it and her sled on it (7a, `chair-sledge/cut.py`), the gull on her head (20), soaked under a sprinkler, her sneeze and her squelch back (16; the kid's jet plays it too with none on her, `soakRide` in `src/world/movers.js`), her hair a puff out of the sauna's steam, fanning herself and swooning (17), sooty out of Teppanyaki's flare, blinking and coughing out a puff (19; its greys on her hair's charcoal, `SOOT`), bumping down the funnel's stairway on her bottom and dizzy at its foot (21; cut by `stairs-bump/cut.py`, played by the ship scene's `stairsGag`), the parasol blown inside out over the bow, she looking up at it and kicking as she drops (22; `parasol-flip/cut.py`, the ship scene's `parasolGag`). The court's balls, 14a/14b: stiff as a plank onto her back or her face, from her stand or a quarter of her run, then lying so with the butterflies (`ball-*-lie`, set on by `ball.dx`; `starts/ball14/`). The stage light's 12a/12b reuse 9a's spin (and `jog-spin-stand`, from her standing frame) and 9c's belly-flop (`lightSpin`, `lightShoved`). The jogger's four (9a spun like a top, one clip per quarter of her stride; 9b bowled back; 9c shoved onto her belly; 9d 8d's bounce off his back; the ship scene's `jogGag`, his own `sorry` and `scratch` in the people sheet; the sheet is 17 frames wide). Her hands over her eyes at a "Do Not Disturb" door, blushing, and her quick tiptoe off (23; `dnd-sorry/cut.py`, the ship scene's `sorryGag`; the same on an occupied balcony, 24, to the partition ahead: `partitionShort`); the doors' swing is built from `door-burst-dnd/`, the same frames with the doors' sign on the lever's mount (`assets/source/ship/dnd-hanger/`: the sign drawn by hand, `swing.py`; the shut door `assets/ship/door-cabin-dnd.png`, the sign alone `dnd-hanger.png`, also on the occupied balconies' partitions and cabin 8206's door). Each played by its mover (`ride.play`, the ship scene's `thingGag`). The door clips keep their own (muted) colours: only her pixels go on the palette |
| `tools/build_closeups.py`, `assets/source/closeups/` | **The close-ups** (the user, 2026-11-19, "A and C"): each thing to find and each key card as a detailed PixelLab picture (about 100 px; its README has the ids), on the palette (the tennis ball keeps its felt) into `assets/sprites/closeups.png` + `.json`, a frame per keep name (`wool`) and `card-<card>` (one card, its stripe recoloured). Shown by `world.closeup()` when she gets one (`take`, `giveKeep`, `progression.open('cards')`): at 2x in the middle of the screen over a dim, a warm light behind, she held and nothing touching her (`scene.viewing`) until any key. **The world's sprite of such a thing is its close-up shrunk** (`FROM_CLOSEUP` in `tools/build_things.py`), a little bigger than life; the playtests skip the moment (`Browser(closeups=False)`, `window.__skipCloseups`) but where it is checked. The other pickups have theirs too (2026-11-20): the grip socks, the parasol, her pills (her only quest item kept in the pocket), from `take()` for a `verb:` or an `item:`. The books' covers (§4 2.3) are to come the same way |
| `tools/build_things.py`, `draw_pages.py` | The plan's own things from PixelLab map objects (`assets/source/things/` to `assets/sprites/things.png`: the robot, the gulls, the towel animals, region 1's flags, shelf, laundry cart, basket, a door's hand, the cry's two signs; the tries and their ids in `tries/README.md`); the ten books' pages drawn in code (`assets/ship/pages/`) |
| `docs/progress-decisions.md` | **The autonomous build's log** (the user's order, 2026-11-13): every change or addition to the plan made while building, with its reason, step by step |
| `tools/playtest.py` | Headless Chrome playtests with real key presses; `python tools/playtest.py [scenario]`. **`mishaps`** (§3 1.3): a case per hazard whose hits had no check of their own, each hit made through the thing's own code (a person's `world.touched`, a round's hit, the hazard met in play from its `?at=` place), none on her and two (`mishap_hit`, `both`: the scenario, its gag's clip, her checkpoint, the count); the table of every hit and where it is checked: `docs/population.md` §2.9. Positions come from the map builder. **On the stepped clock** (`docs/plan-fast-tests.md`, built 2026-11-18): once a page is loaded the test stops the game's loop and steps it itself, a sixtieth of a second a frame, undrawn unless a screenshot is wanted (`takeover`, `Browser.advance`); every wait in a scenario is `wait()`, every deadline `now()`. `-j 6` a process and a browser for each scenario, six at a time (the whole suite in about a minute); `--failed` those that failed last time; `--times` each one's time; `--real` real time, for comparing; `--seed N` the random draws' seed. `boot` and `sound` always run in real time. A scenario's cases: `scenario_region4__towels` is `region4.towels`, and `region4` runs it with the rest. The other tools that use `Browser` (`check_overlaps`, `shoot_people`, `render_ship`) are stepped too, `--real` for the old way; `check_sound` is real |

## Rules that are easy to break

- Scale: one deck = 144px; she is 59px tall in an 84px cell, feet on the cell's bottom row. Every
  human-sized thing (doors, furniture, railings) is sized to her, never to the ship.
- No death: failures are "scares" (run off, long fall out of frame, life ring overboard). Never use
  the word death, in code or on screen.
- Nothing floats: every object rests on or hangs from something plausible.
- **Doors and walls across a deck stop whatever moves, not only her** (the user, 2026-11-17;
  docs/plan-three-uses.md §1.8): a moving thing stops short of a door's face (`stopShort`,
  `spanOn` in the ship scene), never on it; a person walking a loop opens a door with no lock and
  goes through (`door()` in `src/world/people.js`), a locked one turns them back. A new mover
  uses these, never its own range across a door.
- Sprites face east; west is `flipX`. Background props are muted so they never read as interactive.
- **Every door she can use is drawn in its full colours**, never washed or muted, so it stands out a
  little as something to use (the user, 2026-11-15): in rooms, in corridors, side-on in the walls
  across the decks. Inside every room she enters, the rest above the floor is washed 30% toward the
  wall, as in cabin 8206 (`Room.full` in `tools/draw_rooms.py`, `keep` in `draw_cabin.py`,
  `draw_linen.py`, `draw_chapel.py`): a new room or door follows it (GAME_DESIGN.md §2.1).

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

- Generations cost money (Tier 2, 5,000 a cycle; 4,388 left on 2026-11-18, refilled 2026-12-16;
  `get_balance` says what is left). **State the cost and
  ask before spending generations.** Several jobs can run at once. **Except for pictures (the user,
  2026-11-16): "Don't hesitate to generate new/updated props in order to implement things properly
  visually. Use the generations."** A new or better prop, figure or clip that makes a thing look
  right is made without asking first; say in the report what was made and what it cost, and show
  it enlarged as always.
- **Art is generated, not drawn in code, and not put together from other scenes' props** (the
  user, 2026-11-16: "use generations instead of attempting to draw by itself, or reuse part of
  props from other scenarios"). Code drawing stays for what is flat by nature (a band of colour, a
  wash, a rope's line, a jet of water) and the rooms already drawn that way. Cutting rows out of a
  generated picture to size it, and putting its colours on the palette by hand, are fine.
- **A person with a thing is generated together** (the user, 2026-11-16: "in a specific use case
  that requires some animation or scene, generate people with objects together, that way it looks
  more natural"): her dazed with butterflies over her head is one clip of her with them, a lady in
  her armchair one picture, not a figure with props laid over it in code. Props placed by code stay
  for things truly separate in play (a tangerine that flies off and lands).
- **Every generated picture or clip is checked frame by frame before it is shown as a candidate**
  (the user, 2026-11-18: "Make this a rule. Do it when you're generating imagery, before suggesting
  final versions for my review"), enlarged and measured by pixels, and fixed first: (1) overlaps that
  make no sense; (2) anything that breaks a seamless hand-over, seen (a thing changing shape, colour
  or place between the world's picture and the clip, or frame to frame) or in time (a hold, a delay,
  a jump in speed); (3) anatomy in every frame; (4) spatial alignment (feet and things on the floor
  line, things on what holds them, nothing drifting). Say in the report what was checked and fixed.
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

Lessons learned (2026-11-14, step 10):

- **A light over the whole picture is one multiply rectangle on a camera of its own**
  (`duskWash`, `washCam`), not a tint on thousands of pieces; what must keep its own colours
  under it (the sunset's sky and sea) is drawn divided by the light (`dusk()` in
  `src/background.js`). `Phaser.BlendModes.MULTIPLY` works in this Phaser.
- **Something behind a piece drawn in front of her is hidden:** Bumbot behind the mooring deck's
  railing could hardly be seen; he sits on our side of it. Check a new small thing against the
  `front` pieces where it stands.
- **A fright comes back at the checkpoint nearest by deck:** for a fall through several decks
  that is the wrong place. A stretch with its own way back gives it by rule (`respawnFor` in
  `src/world/finale.js`).
- **A new look of hers needs every pose the game can ask for** (`pose()` falls back to her
  standing with him): list what play uses (stand, run, rise, apex, fall, front, back, the idles)
  before making clips; a template jump may mangle what she holds, and two strides of the walk
  read as a hop.
- **A test that sets a story flag by hand may start that flag's own scene:** wait it out, or the
  scene under test overlaps it (`world.cut` now counts overlapping moments).
- **A gust carries her twice the px a second its data says** (body and picture are both moved):
  tune by what the playtest measures, not by the number.

Lessons learned (2026-11-14, step 11, the ship's side):

- **A texture over the whole ship is painted in the builder and cut into tiles** (identical ones
  shared), not drawn as shapes: the tile layer is culled and costs nothing more. Whatever the game
  draws in the plating's flat white over or beside the tiles (the strips of wall over her at a
  deck's ends, the end walls, the slopes, the stem's edge) must then carry the same pixels:
  `plateTiles()` draws the side's own tiles again; the slopes and the stem get marks from the
  builder.
- **Faint is not enough; the pattern's scale decides how it reads.** Six-metre plates with every
  butt drawn read as brickwork, a solid two-pixel streak read as a pipe. Longer plates, butts
  fainter than seams, streaks that start strong and break up. Look at it at the game's zoom and
  at the whole ship's, not only at 1:1.
- **Smoothing a painted shape by blurring rounds its points away:** smooth each outline along
  its own length, pinned at its sharp turns (`sleek_outline()` in `tools/build_livery.py`).
- **What is drawn in front of her inside a deck is in front of the ship's side too:** it must
  fade with its deck's cut-away (`behindShell()`), or it shows through the closed side from
  outside. The render of the whole ship (`tools/render_ship.py`) shows such things at once: look
  at all of it after a step that adds things drawn over her.
- A tool that drives the game by its internals (cameras, routes) breaks silently as the game
  grows: `render_ship.py` shot the wrong thing for weeks. Drive the game's own modes instead.

Lessons learned (2026-11-14, step 12, sound):

- **I cannot hear.** A sound is written from what it is made of, rendered offline
  (`sfx.render()`, an `OfflineAudioContext`) and measured and drawn (`tools/check_sound.py`):
  that catches silence, clipping, a length or a balance that is off, and a shape that is not
  what was meant. Whether it sounds right is the user's to say, on the soundboard: say so
  plainly whenever sound is shown, and never call a sound good.
- **A note that dies away to nothing is mostly unheard:** an exponential fall to 0.0001 over a
  sound's length left a third of it audible and every effect three times fainter than its
  number. They fall to a fiftieth and are cut. Noise through a narrow filter is far fainter than
  a tone of the same number: balance by measuring, not by the numbers.
- **The Web Audio compressor adds gain of its own** (about a quarter more at these settings):
  measure after it.
- **A new effect goes in three places:** its line in `src/sfx.js` (in its group, with a comment
  saying what it is for), the call (`sfx.at(x, y)` for anything on a clock of its own), and
  nothing else: the soundboard, the checker and the `sound` playtest (which fails on a name that
  does not exist) read the groups themselves.
- **Never a sound each frame:** a state that lasts re-triggers on a timer of its own; a sound
  that takes a length gets the real one in seconds.
- **Work that is the same judgment many times over in files that do not touch** (which effect
  fits each of 250 moments in eleven files) goes well to helpers in parallel from one written
  brief that names what they may not do (no browser, no tools, no other files); read their
  doubts, they found a fault in the engine.

Lessons learned (2026-11-17, the breakfast stewardess):

- **A clip drawn with a world thing that stays in the world** (the trolley she trips over, the
  trolley the stewardess pushes): make it with the game's own picture of the thing in the start
  frame, then take the thing out of every frame (inside its box, a pixel nearer its colours than
  the figure's; then loose specks) and draw the world's own over or under the figure. It never
  changes, whatever the generator did to its copy.
- **Hands that must stay on something while the legs walk:** v3 swings them with the step (5 px,
  then 4 px again); pixminimax (1 generation) held them on one pixel. Measure the hand and the
  planted foot in every frame by colour: a foot that creeps forward and back reads as "dancing";
  two even steps whose planted foot slides back steadily, played at speed / slide frames a second,
  keep pace with the floor.
- **A gag is set on the floor of the place, not at her feet:** stood on a cart's top, she sat in
  the air once it moved on.
- **A GIF saved by PIL merges repeated frames:** count frames from the game's clock, not the GIF.
- **Sliding a thing into a door crosses whoever holds it** when the door's hand is on their side:
  it shrinks a little where it is held and is gone (`handTakes(..., { shrink })`).

Lessons learned (2026-11-17, the art rule looked back over):

- **A thing must read in its place at the game's size, not only enlarged:** a feather toy 6 px
  tall on a thin shelf read as "a shelf glitch"; stood on end with nothing holding it, "stuck in
  the shelf". Compose it at its spot, at 1:1 and enlarged, before showing it.
- **A tiny picture is shrunk by majority colour, not averaged** (`BY_MAJORITY` in
  `tools/build_things.py`): a flag's cloth averaged with its outline went dull. **And a picture
  near its game size is never resampled:** 51 px to 44 deformed a cart; cut rows out of a plain
  part instead (`CUT_ROWS`, or by hand).
- **A strict side view that text will not give:** `edit_image_pro_flash` from the try whose look is
  liked, "redraw this same ... in strict side profile" (5 generations).
- **A pictogram has about 16 px:** a finger to the lips is lost at that size whatever the drawing;
  pick a sign that survives it (a speaker crossed out).
- **A deck's dim reaches 16 px under its floor:** anything that tests her body against a deck
  counts her head past the floor, not into the ceiling below it.

Lessons learned (2026-11-17, the dog and its owner made together):

- **Two things joined by a line that changes length** (a lead, a rope to a moving thing) are not
  one generated picture: make them together once for their look and size, then draw the line
  from ends measured in every frame of both clips, in the picture's own colours, px by px
  (whole px, rows rounded, joined side by side), its depth between them as the picture has it.
- **Map objects don't draw people** (silhouettes, no faces): a person, even with a thing, is a pro
  character in the cast's style.
- **A quadruped's template clips redraw it as another animal**: PixMiniMax from its own approved
  picture holds it (a sit toward the approved sitting picture as its end frame); skeleton-v3
  keeps the look but may stretch the body. Compare every clip with the approved still on one
  floor line before anything else.
- **A person's clips are set on the floor frame by frame** (`OFF_THE_FLOOR` in
  `tools/build_people.py` lists the clips that leave it): PixelLab's frames drift 1 to 4 px.
- **A sound tied to a clip** (footsteps) plays on the clip's own frames, not by a distance that
  only matches it at one speed.
- **An exception to a rule of hits** is a property of its scenario read where the rule is
  applied (`pocket: false`, asked by `pocket()`), never a check at one caller.

Lessons learned (2026-11-17, the dog's together clips):

- **A together clip hands over by its own pictures, not by matching drawn lines to them:** the dog
  runs to the spot where its sprite lies on their picture, and the clip starts; at the end the
  clip's last frame is held until something moves (the dog gets up), and the game's lead takes over
  then. A drawn line made to match a picture's at rest never quite did.
- **A clip played backwards moves things the way they do not face** (the dog would run tail first):
  the way back is a clip of its own, from the end picture to the start one.
- **A thing handed on from a clip to the game** (the ball from her hand): the clip has it until the
  frame the hand opens, and the game's starts moving from where it was held at that very frame; it
  never stands still in the air a frame. Its depth follows what it passes: behind the fingers that
  hold it, in front of whoever it reaches.
- **Phaser's tweens keep a wall clock of their own:** a thing moved by one is not slowed by the
  game's clock (a recording stepped frame by frame showed the ball three times too fast); move it
  on the scene's `update` with `time.now`.
- **Someone who comes to her while she is down holds her checkpoint** (`down.holds` in
  `scareDown`), never a longer fixed wait.

Lessons learned (2026-11-17, the steward's jammed trolley):

- **A block must look like one:** a low cart standing for a wall to the ceiling read as "an invisible
  wall" and the scene as "weird and unclear". What stops her is drawn at the size it stops her (too
  tall to hop, it is taller than her jump).
- **Someone working at a world thing that moves** (a trolley pulled, then pushed) is one picture of
  the two while they are together, the world's thing hidden; the world's own is cut from that clip's
  frame, so the hand-over matches. And a clip for every way they move together: tugging in place,
  and stepping as it rolls (legs still while sliding along read at once).
- **A thing given is tossed, not flown:** `world.tossOver` with the giver's toss clip (in the
  fingers until the hand opens, then a lob); a thing that just crosses the air to her was "just
  flying at her".
- **Before reporting a block, find what it is:** I first showed the user a different trolley (the
  breakfast stewardess's, the same picture) than the one in their screenshot. Match the person in the
  picture before answering.

Lessons learned (2026-11-18, the towel stack's fall):

- **A clip of her caught while she runs starts from her own run frame, and she runs on in it:** one
  from her standing made her "deliberately stop for a fraction of time to let the towels fall"
  (the user). Pinned to an end where she already stands she runs on the spot: start her where the
  thing first reaches her and end where she is caught, so the clip must carry her forward (about her
  run's px a frame), and play its first frames at her run's rate. One clip per phase of her stride
  (four of eight frames), the one whose first frame is the pose she shows next.
- **A thing that falls on her falls when she is where its clip has her**, not on a timer that
  happens to fit one speed; and a sway or wobble eases to the clip's first pose before it takes over.
- **Generated motion of many small pieces: pin the end.** Unpinned, a stack fell as one stiff column
  and landed "like books"; an end picture made of its own pieces lying scattered gave the scatter.
  Generated heaps as map objects came as snow drifts, swans as birds (a beak whitened by hand at
  15 px reads as a towel swan).
- **`edit_animation` restyles a clip and keeps its motion to the px** (4 frames a call at 128 px,
  10 generations each, the same seed and wording for every call): the redrawn first frame becomes
  the thing's standing picture, so the world and its clips stay one.
- **A heap or a prop that lands on the floor is behind her** as she crosses it (the user), with
  whatever is in its picture (the stool).
- **Before placing a thing that grows when it moves, measure what it reaches:** a heap 90 px each
  way does not fit between cabin doors 159 px apart; and look at the wall behind a tall thing (a
  picture hidden behind the stack). Things of the corridor's own rule move out of a world thing's way
  by rule (`drawCabinDoors`), not by hand.

Lessons learned (2026-11-18, step 4a's first gags):

- **A clip starts from the frame the game shows at that moment, taken from her built sheet**
  (`assets/sprites/her.png`, cell 84, feet on its bottom row), never her source frames: they sit
  1 px apart. And from the clip she is actually in (sliding on the wet patch she plays her slip,
  not her stand). Where she can be in several phases, one clip per phase (four quarters of her run).
- **A thing in her clip that the world shows too is the world's own, moved by the game** (the
  tray's base under her feet): then she can land on it anywhere, and it never changes. A thing
  that only sits on her (the gull) is pasted back from the world's picture where it does not move.
- **A world picture with holes looks different on another background:** the cabin door's inset
  lines are holes the wall shows through; over a doorway's dark they turned dark. Fill holes with
  what the world shows through them, and keep the frames that must equal the world's exactly.
- **A muted twin turns back into the full picture exactly** (`c = (m - 0.35 w) / 0.65`, then each
  muted colour's own pair): one generated clip serves both kinds of door.
- **Someone in a doorway is inside the room**: cut to the opening (`People.doorway`, Phaser's
  crop; the Mask filter in world space hid them whole) and on its threshold.
- **A clip's pace is checked in time, not only in pictures:** a first frame played slower than her
  run held her pose while she glided ("a pause"); never slow a hand-over frame, start nearer.
- **Look at what a thing reaches in the world before trusting a scenario:** the deck chair could
  never catch her on so short a patch, and the door burst while she was still too far; both were
  found only by walking at them with real keys.

Lessons learned (2026-11-18, deck 9's corridor, her push):

- **A walking clip is paced by its planted foot:** measure how far it slides back a frame (its lowest
  row, frame by frame); frames a second times that is the speed it must move at, or her shoes slide
  on the floor (the push: 2.5 px a frame at 9 a second while the cart rolled 60 px/s). Generated with
  the world's thing in the start picture, then the thing taken out, the steps come out even.
- **Two things that move together are placed one from the other after the physics**, on the scene's
  `postupdate` (the cart from her, `pushFollow`): set in `update`, the gap read differently by the
  moment. **And a gap of a half px flickers** under `roundPixels` (each sprite is rounded alone): keep
  such gaps whole.
- **A scene started by a flag can be undone by the code that set it:** the push's last step set
  `cart_free` (which started the steward's scene and stopped her), then set her mode back to play. Look
  at what runs after a `setFlag` before trusting a scene to hold her; and a scene that need not hold her
  is better not holding her (the steward turns to her and his card follows her).
- **A variant of a picture the game already has** (the one-way door's push bar on the glass door drawn
  in code): render the game's picture exactly and inpaint only a band of it (`inpaint_image_pro_flash`
  returns every other pixel as it was): the two stay one pair by construction.
- **A thing with a use reads by how it is used, not only by how it looks:** a push-bar door must swing
  away from the side it is pushed from, and a door with nothing on one side must not open from it.
  Before showing a new look, play it both ways.
- **Someone inside a room seen through its door is part of the room:** cut to the opening and washed
  as it is (a copy of the frame filled with the wall's colour at 30% over them; Phaser 4 has no
  `setTintFill`: `setTint(c).setTintMode(Phaser.TintModes.FILL)`).
- **Describe her body, never the cause, in a clip's motion** (16): "water pours down on her" drew a
  thick blue column over her, unlike the game's fine rain; "she gasps and flinches, her hair goes limp
  and slides down over her face" gave the soak alone, the world's own rain over it.
- **A thing drawn above her layer shows through a deck she is not on** (a sprinkler's rain, deck 8's
  right under deck 9's, fell "through the floor"): draw it only while she is on its deck, as
  everything else on another deck stands still.
- **Screenshots of something moving are taken without pausing the game:** a close-up pauses it about a
  second each, so a timed series all caught its start. Shoot the page and crop by the camera's view.

Lessons learned (2026-11-18, Teppanyaki's flares):

- **A hazard on a clock of its own reads wrong to a player running past:** she met the tell, and the
  flame went up behind her ("usually", the user). A timed danger she runs into answers her coming, by
  her speed (the tell starts so that it is at its worst as she gets there), with a lull after it, and
  never once she is too near for it to meet her. With no one near, the clock.
- **Grey on the palette goes green:** Resurrect 64's nearest dark greys to a neutral grey are greenish
  (`#313638`, `#374e4a`); a sooty face read as green in the game, though the strips looked grey. Put
  greys on the palette's purple greys by hand (`SOOT` in `tools/build_gags.py`) and look at the built
  sheet, not the source frames.

## Working with the user

- **Start each session from `docs/plan-the-rest.md`** (what is left, in the order to build it).
  `GAME_DESIGN.md` §8 records how the work went; its last entry's end says where it stopped, its "Next up" heading
  is of 2026-11-03 and many of its boxes are long built. The
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
- **Game links carry what the thing to try needs, nothing by habit** (the user, 2026-11-19, dropping the
  old rule of `&tangerines=infinite` on every link): `&tangerines=infinite` where tangerines are what
  is tried (the cry, the lunge, a throw), and not where a gull's take would get in the way of its gag
  (20 to 22). **Whenever you
  ask the user to try or check something, give the link**, starting as near the spot as `?at=`
  allows, and say where to walk from there.
- **After each change, show the result and stop for the user's review** (screenshots in the chat,
  plus the link when there's something to try). Don't carry on into test runs, commits or the next
  change before they answer (the user, 2026-11-06: iterations were too slow, and twice I went on
  without asking). Commit and update `GAME_DESIGN.md` once per approved round.
- **After each approved step: commit, save and record everything, then say it is safe to compact**
  (the user, 2026-11-16: "Commit, and save and record everything. Tell me when it's safe to compact
  the context without losing anything. Make it a rule after each step"). That is: the step's log
  entry in `docs/progress-decisions.md`, `GAME_DESIGN.md` §8's next-up, this file's table and
  rules, the memory notes (progress, any new rule), the raw art and its ids kept in the repo, the
  commit on the feature branch, the tree clean; then one line: "safe to compact", with what is
  next.
- **The tests are fast now: the stepped clock** (`docs/plan-fast-tests.md`, built 2026-11-18 on
  the user's word: "come up with a smart solution to speed up the development cycle without
  compromising on QA"). The whole suite had become about 65 minutes in real time (the user, 2026-11-14:
  "an impractical amount of time"; it was then no longer run before a merge). Stepped, the 38
  scenarios take about 4 minutes one after another and **55 s six at a time**, every check with the
  same result as in real time (878 compared). **The rule stays as it was** (the user, 2026-11-18,
  asked whether the whole suite should now run before each merge: "The old rule"):
  - **after a change:** the scenarios it can touch, stepped (`python tools/playtest.py boot region9`),
    a few seconds each; say which were run and that the rest were not;
  - **never start the whole suite unasked**, not before a merge either; when the user asks for it,
    `python tools/playtest.py -j 6`, and the real-time set `python tools/playtest.py --real boot
    sound deck3` if asked for (the real loop, the sound's own clock, the game's own start);
  - **whatever is judged by eye** (motion, pace, a gag) is the real game, as before: the user's play,
    and recordings stepped by hand.
  A failure is read, not run again until it passes: `--failed` reruns only those, `--seed N` replays
  the random draws.
- **A wait in a test waits for the thing, not for a time** (found building the stepped clock): a
  fixed wait tuned in real time had real time's slack in it (each call into the page let a frame or
  two pass), and stepped it ended a few frames short: a jogger not yet by, a jump still over the
  trays, her still on the funnel stairway's last step. Wait until the state is reached
  (`hold_until`, `wait_for`, a loop on `now()`), with a limit; time a key press from the thing it
  answers (0.15 s into the jogger's pause), not from the start.
- **Tests run with the sound off** (the user, 2026-11-14: "When you're testing, please test with
  sound off": every headless run had been playing through their speakers). The test browser is
  muted at the browser (`--mute-audio` in `tools/playtest.py`'s `Browser`, which every tool
  uses), so the game's sound still runs and the `sound` scenario still checks it. Never launch
  a browser for a test any other way.
- **No hint popups** (the user, 2026-11-14: "Part of the game is figuring things out. Labels and
  namings are not considered hints"): never add a text or a key's cap that says what to press or
  what to do. Signs, plates and the people's pictogram bubbles are fine. **One exception, which
  the user asked for by name the same day: "E to interact"** over her as the intro hands her
  over (`hint.interact` in `src/lang.js`). It is not a licence for a second one.
- Do only what was asked: when a request could reach further (another deck, a layout change),
  ask first rather than assume (the user, 2026-11-06).
- The user circles things on screenshots and numbers them; fix each, show the result as
  screenshots in the chat, and say plainly what changed.
- **To approve a piece of art, show the user the image in the chat** (a preview or screenshot) and
  ask; don't send them to launch the game for it.
- **Every visual change, update or new prop is approved before it is placed in the game or
  tested** (the user, 2026-11-16: "make me approve visual changes/updates/new props before you
  start placing them in the game and testing them"): a generated picture, a cut-out, a clip, a
  mended edge, shown enlarged (beside what it comes from, or beside her), then stop for the word.
  Only then the sheets, the code, the playtests. (I had cut the world's suitcase from her riding
  picture, squared its rounded corners in the mending, and placed and tested it before the user
  saw it.) **Shown in the chat itself, and a clip in its context** (the user, 2026-11-18: "when
  generating art candidates, show them to me in this session before inserting in the game. If
  that's an animation, show me clips of it, inside the context, when relevant"): the candidates
  read into the chat, a clip as its frames composed over a real screenshot of the spot where it
  plays, at the game's offsets, enlarged (a GIF saved beside it); the game shown after, for play.
- Test in headless Chrome (the user uses Chrome, not Edge). Keep image viewing and tool output lean:
  the user watches session usage.

Lessons learned (2026-11-14, the prep before the intro: deck 3, the languages):

- **A new played part of a closed deck is a few lines in the builder**, because every piece of the
  ship's side follows the owner of its tiles: make the part's shell tiles cuttable
  (`on_crew_deck()` in `build_exterior()`), wall its ends in the solid layer, and the cut-away, its
  shadows, the livery's piece over it and the portholes on it all follow. Give a porthole or a
  window its owner by `span_owner()`, never `"fixed"`, or it stays drawn over the opening.
- **A door in a cabin corridor takes a cabin door's place:** any door within 100 px of a cabin
  door removes it (`CABIN_DOOR_CLEAR`), and the doors are 192 px apart, so a door between two
  removes both. The service ladder's door on deck 4 stands exactly on a cabin door's slot.
- **Moving the start moves every playtest's start:** twenty-six scenarios opened the game and
  walked from the gangway. `Browser.open()` starts them there still (`start="gangway"`, its
  checkpoint lit as it was); only `boot` and `deck3` use the game's own start.
- **A photo to pixel art (`image_to_pixelart`, 1 generation, the size is ours to choose):** cut
  the subject out first (OpenCV's GrabCut with a rough mask) onto a flat pale ground, which also
  keeps the user's room out of what is sent; the default mode redraws cleanly, `faithful` at
  120 to 200 keeps the photo's look but blurs at 32 px. A black cat comes back charcoal or navy
  with orange eyes, and a yellow ground bleeds into yellow eyes: recolour by rule afterwards.
  **Show the user the candidates framed and enlarged, side by side and numbered, before placing
  one** (the user: "Ask me if I like the picture before placing it in the game").
- **A walk in a playtest that must end at a door ends by teleport or by `hold_until` with a few
  px to spare:** polled every fifth of a second, she overshot the ladder's door by 11 px and E
  found nothing.

Lessons learned (2026-11-14, the intro):

- **A sequence of camera moves is one clock and pure functions of it**, not tweens chained on
  each other: any moment can be shown alone (pictures for the user, a playtest's checks), a skip
  is the clock set to its end, and nothing is left half-done. Keep states that a part switches
  (a route, a pose) set from the clock too, each frame, so seeking back undoes them.
- **Phaser 4's blur is a camera filter** (`cam.filters.internal.addBlur(quality, x, y, strength,
  colour, steps)`, removed with `.remove()`); it darkens the picture's edges, so the camera is
  made 48 px bigger all round while it is on. **Change a camera's size before centring it**, or
  the picture jumps for a frame. What must stay sharp over a blurred world goes on a layer and a
  camera of its own, kept at the main one's zoom and centre.
- **Things with scroll factor 0 laid out by hand, and anything else that reads the camera, run
  after the camera is moved**: the intro moves it at the top of `update()`, before the sky.
- **A float that should reach 1 often stops at 0.9999999**: `(1 - 0.55) / 0.45` did, and her
  alpha was never 1. Snap the end.
- **A finer drawing of an existing sprite:** `image_to_pixelart` of the sprite enlarged smoothly
  (64 px to 512, output 256) keeps the likeness and adds the detail; from a description alone
  the figure came out someone else. `create_character` v3 with a reference keeps the reference's
  own size whatever `size` says (hers came back at 64 px, in eight directions, 8 generations).
  `animate_image_pixminimax` animates a loose 256 px picture for 2 generations (16 frames) and
  holds the look well; one frame in sixteen had a stray thing in her fingers (left out).
- **Text in generated art is drawn by us:** the badge's letters are stamped on every frame
  after the generator, over its own try (painted out first), with her hand kept on top by its
  colours. Slant small text by whole letters, never through one.
- **UI art from PixelLab:** `create_ui_asset` (10 generations at 256 x 256) draws plates and
  panels to a template of shapes, in the game's palette when it is passed; `create_font` (15)
  gives an atlas of 80 Latin glyphs, eight to a row, and nothing else (no Cyrillic). Use the
  glyphs as shapes and colour them in the game; build what is missing from them by flips where
  the shapes allow (flat shapes only: a flip turns a shaded letter's light upside down).
  Canvas compositing: `source-in` clears everything outside the new shape, so a second band
  wipes the first; bands go on with `source-atop`.
- **A style is chosen from mock-ups of the whole screen**, composed offline over a real
  screenshot, in both languages and with an entry chosen, not from the loose pieces.
- **Show the user the shot, not only the figure, before making its art:** I made whole-figure
  candidates and two animations (27 generations) before the user described the close-up they
  had in mind (a waist-up profile). A rough frame of the composition first would have saved
  them.

Lessons learned (2026-11-14, the intro shown to the user):

- **A cutscene is judged in motion, and I only see stills:** the close-up at her mirror looked
  right frame by frame, and the user's word on seeing it run was "doesn't work at all". For a
  sequence, build the plainest version that runs end to end and show that first; make its
  special art (35 generations here) only after the user has watched the plain one.
- **UI scale is changed in the art, not in the game:** a menu "smaller" by a factor of 0.75 was
  rebuilt at that size (letter shapes resampled and thresholded, the plate resampled and snapped
  to the palette) and still shown at two screen pixels to one; scaling by 1.5 in the game makes
  pixels of two sizes.
- **A clip of her that shows something on her front is drawn facing us:** her badge is only in
  her south view. skeleton-v3 by poses kept her look; hands in front of the body need their
  elbows pointed down.
- **Motion that stands for the ship being under way belongs to views from the ship:** the far
  background's drift aft looked wrong in the intro's wide views, where the camera stands still
  and a sun stands in the world (the user saw islands and clouds slide past it). In a view from
  afar, far things hold.
- **Two states of one thing share one frame:** a sheet draws an open door and a closed door as
  two pictures, each fitted to a door's height by itself, and their frames come out different
  (the open crew door's 5 px lower and off the floor; the open cabin door's dark and narrower).
  The user sees it the moment one replaces the other. Build the second state from the first's
  frame (`level_frame`, `reframe` in `tools/build_ship_art.py`), and lay the two over each other
  at the game's placing before calling them a pair. A piece may reach under the floor line (an
  open door's leaf swung toward us: the user likes it, "more real"): it says by how much in the
  atlas (`foot`), and the game stands it by its frame (`setDoorArt()`), never by cutting it. And
  check what the two states share besides the frame: which side the handle and the hinges are
  on (both open doors came mirrored against their closed ones), where a plate sits.
- **A state of her character on a bigger canvas can come out bigger than her** (the paper gags'
  stills, a quarter bigger on 80 px; the suitcase's came right): set it beside her standing
  sprite before showing it. **A clip v3 from her own sprite padded into the bigger frame keeps her
  size**, and an end frame (the state's still shrunk to her size, roughly) steers its last pose;
  a thing she meets can be put in that start picture (the paper under her foot). The clip's frames
  are then the stills shown for approval (1 to 2 generations a try).
- **A GIF counts time in hundredths of a second:** 66 ms frames are saved as 60 and play 10%
  fast (the user judged a pace by one). Record at 70 or 100 ms a frame, from game time (the game
  loop slept between grabs), and say where in its range a moving thing met her: a ride from
  halfway is half as long as one from an end.
- **Something kept over her head through a generated loop** (butterflies): set it in the start
  picture, the end frame the same; described alone, v3 had them fly off.
- **Palettizing white paper turns it pale green** (Resurrect 64 has no light neutral grey): put a
  paper's greys on the palette by lightness (`assets/source/things/newspaper-sliding/README.md`).
- **A one-off action tied to a place** (her hair at the mirror) is armed by arriving and
  disarmed only by leaving or turning away: a count drawn on arrival, never a timer that loops.

Lessons learned (2026-11-18, the stepped clock):

- **Undrawn frames skip what Phaser does while drawing:** a camera follows her and updates its view
  in its `preRender`, so stepped undrawn the "out of the screen" test of a ride read a view left at
  the gangway and ended the ride at once. `__advance` calls each camera's `preRender` itself.
- **The game's scenes `await` their waits and tweens** (`world.cut`, `world.wait`, `world.tween`):
  a promise's continuation runs only when the browser gets its turn. Stepped in one go, a batch of
  frames ran all its frames first, and each `await` came late by up to the batch (the chute's fall
  0.2 s late, which only a screenshot showed). Between two frames `__advance` gives the browser its
  turn (a message on a channel: no delay of its own, after every pending continuation).
- **Whatever reads the loop itself must be kept as the loop keeps it:** the cake's sway read
  `game.loop.delta`, frozen once the loop was stopped, and the cake never swayed. `__advance` sets
  the loop's time, delta and frame each frame.
- **A real-time check can pass by luck of timing:** the trunk's "Deck card" passed only because the
  calls into the page let 0.9 s pass after the stairs' own lock message (`lockedUntil`). Stepped,
  such a check fails every time: it is a find; mend the test (or the game), never pad the wait.
- **What is still not the same from one run to the next:** the game's clock at the takeover (how
  long the page took to load) sets every timed thing's phase. A check that must catch a thing in
  its round waits for the round (`wait_js` on its phase), with room for a whole round.
- **Six browsers at once need a server that keeps up:** Python's default backlog of five refused a
  file and a sheet's data never came (`Server.request_queue_size`); a page that does not come up
  is loaded once more, its errors printed as a note.

Lessons learned (2026-11-18, the funnel's stairway):

- **A whole-picture edit (`edit_image_pro_flash`) of her in a scene drops the scene** (the stairs and the rail
  wiped, her hands off the rail); a PixMiniMax clip from the same start picture keeps the world's pixels exactly
  and gives the move into the pose too. For a new pose of hers in a place, animate into it.
- **A generator moves the world's lines it was given** (the handrail drawn 1 px off, dashed, grey): find such a
  line in each frame by its slope and colour, take it out, and fill her across it from her own pixels both sides;
  the game draws its own in front. Cutting her out by "differs from the start" also takes in steps it redrew.
- **A pose placed on a slope needs a picture made on that slope:** her floor slip on 44° stairs put a foot 11 px
  into the steps ("she falls through"). Measure each foot against the tread under it on every flight.
- **Something carried by a flapping sprite follows its frame's own point** (a gull's beak, measured per frame,
  `GULL_BEAKS`), placed on `postupdate`: frames of different sizes moved a fixed offset 5 px every other frame.
- **A hazard that waits over her and marks her spot is rarely met in play** (the user): a gull now dives straight
  from its flight. A reaction coded for `play` only does nothing on stairs: check the modes a hit can come in.
- **Phaser 4 mirrors a flipped frame in place**, its origin still counted from the left of what is drawn: a frame
  anchored at column c, flipped, takes origin `(cell - 1 - c) / cell` (gag 21 first stood 26 to 30 px off). Check a
  placed clip by matching the game's frames to its pixels, not by eye.
- **A gag that plays while she falls is a fall for the cut-away too:** in the air the view keeps the deck she left;
  a scripted fall (`airScare`) had it follow her height, and the bow's plating opened deck by deck at the gull's hit.
  The decks' leaning railings likewise count the deck she last stood on (`floorDeck`), not her height in the air.
- **A thing drawn in front of her runs on under the ship's side** (the mooring deck's railing under deck 7's sloped
  plate): it goes behind the plate while the plate shows (`underSlopes`). An open deck that keeps the side closed is
  an `outdoors` area (the mooring deck now, as deck 11's front), its plate always in front of her.
- **A flapping sprite whose frames differ in size is hung by what stays still** (the crossing gull by its underside):
  by their middles its body jumped 5 px a flap, and at the screen's edge it came and went. The funnel's circling gulls
  still hang by their middles.
- **Say "candidate" only for alternatives to choose from:** for one thing to approve, say what it is (the user
  could not tell what "the candidates" were in a sheet of one clip's frames).

Lessons learned (2026-11-19, gag 23 and the doors' sign):

- **A walk that a generator keeps striding wide is laid out as skeletons by rule** (her tiptoe: four PixMiniMax tries
  took 28 px strides with a bob, "skip-dancing"): estimate her pose once (`tools/estimate_skeleton.py`), hold it from the
  hips up, put the feet where the step should be (two tiny steps, the pelvis level, knees forward, solved per frame) and
  `animate_with_skeleton_v3` from her own picture. Its `z_index` must be whole numbers. Her character's library moves
  ("sneak") redraw her in her character's look, not the picture's.
- **A thing on a door that swings goes with the door's point it hangs from, on the face it is on:** the sign hung on the
  lever's mount of the outer face; once the leaf is past edge-on the clip shows its inner face, and the sign is behind the
  leaf (only what reaches past its edge shows). Measure that edge in each frame below anything that sticks out (the
  handle), since a generated leaf's width wobbles; and go over every frame enlarged, the edge-on ones above all.
- **A world picture that is also a clip's frame keeps a picture of its own** (the shut "Do Not Disturb" door,
  `door-cabin-dnd`, exactly the swing's frame 0): as a frame of the gags sheet it would have dropped out of
  `tools/check_overlaps.py`, which knows a door by its picture's name.

Lessons learned (2026-11-19, 7a and the wet patch):

- **A thing that moves at her needs a cause she can see:** the deck chair slid across the wet tiles at her by itself,
  and she slid toward it; the user could not tell why either moved. Now it stands, and the water is drawn.
- **Water seen edge-on does not read:** a puddle as a strip on the floor's line, against the sea in the windows, was
  invisible. Drawn on the floor's face, as if seen a little from above, with a darker rim and glints, with the shower
  running over it and splashes off her feet, it reads at the game's size. Versions of a look are drawn in the running
  game (a script that draws them in the page), each shot at the same spot, the user choosing.
- **A thing of a deck drawn over her layer is drawn only while she is on that deck** (`onDeck` in
  `src/world/topdeck.js`): the court's ball, near by its distance alone, bounced in front of deck 12's closed side
  from deck 11. A distance test for "near" is not a test for "on its deck".

Lessons learned (2026-11-19, the kid's cone, the pool's gulls, the queue):

- **Look at what a person's clip actually shows before using it with a thing:** the kid's `eat` had him biting his own
  water pistol, and the game laid its cone in the air in front of him; seen in play, at once. A person eating a thing is
  one clip of the two (an edit of his stand with the thing in his fist, then animated), the thing handed over into his
  fist as the first frame holds it.
- **A scene holds her only as long as she must:** handing over a cone held her for his whole meal, standing over him.
  She steps to arm's length, hands it, and is free; what the other does with it plays on by itself (`kidHas`).
- **Someone who makes way does not leave their layer:** the queue turned aside by going 5 depths back, behind the café's
  tables and chairs; and one who has stopped stops the line (they slid on, turned away).
- **Before calling a look wrong, find what is drawn:** the "missing" opening over the pool existed; the gulls flew in
  front of deck 12's band. A mock-up in the running game (a script that moves the things in the page) showed the fix.
- **A test script can start the game's own hazards:** a teleport by the wet patch set off 7a, a stop in the gulls'
  stretch lost the cone; trace who calls `respawn` (a wrapper with the call stack) before blaming the change.

Lessons learned (2026-11-19, the wet gag on the kid's jet):

- **What a gag reads of her is read at the hit, not when it plays:** `thingGag` stops her before the ride plays, and the
  sprinkler's soak read her stride then; it never saw her running, and its four clips from her run never played (since
  gag 16 was built, every check green). Look at a recording of each case a gag has (standing, running), not one.
- **"More visible" is a small step:** a stream twice as thick with a dark outline was "too strong and too thick". Draw a
  few strengths in the running game for the user to choose from, the one before among them.

Lessons learned (2026-11-19, the jogger's gags):

- **A gesture that must read at 60 px is designed by the user, and steered by an end picture:** a jog on the spot with
  palms out read as "weird", a hand by his head as "Hi"; "his hand behind his head" from text alone came as a blob of
  hair. An edit of his standing frame into the pose (`edit_image_pro_flash`), then a clip toward it, gave it; then look
  for the arm the pose took away (his far hand still peeked out at his hip: "three hands").
- **A composite over a screenshot must keep the game's layers:** pasting figures over a shot drew them over the railing
  the game draws in front of them. Shoot the spot once more with a marker box at their depth: what covers the box is in
  front of them.
- **A settings key can be another gag's test:** `GAGS[...].sorry` sent the jogger's gag to gag 23's code. Before naming a
  key, grep for `GAGS[sc.gag].<key>`.
- **A sheet's row is its width:** a clip longer than a row ran off the gags sheet and showed another gag's frames for its
  end (`build_gags.py` now refuses it).
- **Someone who stops mid-way lets go of what he holds:** the jogger stopped in a door he was holding open, its leaf drawn
  in front of her fall.
- **What the user meets first in play is the case to build first:** running is how she meets the jogger, so 9a, not 9b,
  is the one seen; the user took its stand-in for the new gag.

Lessons learned (2026-11-19, the stage):

- **A new piece in a scene is inpainted into the game's own picture of it**, then cut out by what changed: it takes the
  scene's colours and light (the open trap door). The canvas reads back black (WebGL): grab the frame with Phaser's
  `game.renderer.snapshot()`, drawn by a screenshot step, and halve it (the canvas is 2x). Mask only the piece's area,
  keep the world's own props out of it, and move a prop rather than keep a generator's copy of it.
- **A gag that carries her forward goes no further than a wall or door** (`stopShort` in `jogGag`), and a test that waits a
  fixed time after a hit breaks when a gag gets longer: wait for her checkpoint.
- **Before calling a ghost in a shot a fault, check whether a scene was playing:** reaching the stage starts near-catch 3,
  and a shot mid-fall looked like a faint copy of the trap door.

Lessons learned (2026-11-19, the basketballs and the court's players):

- **Her standing frame turned a quarter is not her lying:** it touched the floor with her hair or her chest, and set
  straight it read as tilted (her head tips forward when she stands). A lying pose is an edit of it, "lying flat on her
  back, the back of her head ... on the floor line", and the falls are made again toward that.
- **A red patch on the floor under her face reads as blood:** look at what her own colours do where she lands.
- **A thing thrown from a clip into the world** is the clip's until the frame the hand opens, then the game's from the
  spot it was in the frame before; a thing taken up is the game's until the hands are on it, the clip's lying copy cut
  out before. A washed figure's thing changes colour at the hand-over: fade between the thing's two pictures (0.2 s).
- **Through a ring, only the ring is in front:** behind the hoop's picture the ball vanished behind the board above
  the net; it goes behind only between the rim and the net's foot, and keeps its falling speed through it.
- **A hit in the air waits for her landing** (`gagPending`) and she keeps her jump's arc: a gag that should knock the
  jump out of her says so (`drop` in `GAGS`: stopped, stiff, straight down; the court's balls).
- **A mover's field must not take a mover's method's name:** `this.heard = {}` broke every cry (`heard()`).
- **A test that empties her pocket gives it back**, and a stretch whose time a change moves can meet another timed
  hazard by phase (a funnel gull on the stairway check): hold what the check is not about.

Lessons learned (2026-11-19, the theatre's audience):

- **"The same chair" means the same pixels:** five people drawn each in a chair of their own read as "similar, but
  different". Take each out of their chair (`edit_image_pro_flash`, "remove the chair, the same pose"), then set them in
  one seat split in two: what is behind them (the backrest, the far arm) and what is in front (the near arm, the seat's
  front). New people for a crowd: edits of those, "a different person in exactly the same pose", 5 generations each.
- **A wash is the user's to set per place:** the background's 35% read as "washed out too much" in the dark theatre.
- **A piece that keeps its canvas counts its empty part in `check_overlaps`:** keep only the columns it needs and cut its
  top to what is drawn (it stands on its bottom row).
