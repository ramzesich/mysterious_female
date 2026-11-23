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
  named place (list in `README.md`, a link for each in `docs/start-links.md`; for testing), `?sound=off` (sound is on; M mutes it in the game), `?lang=ua` (Ukrainian for a session). D is the cry and the lunge, F the throw, in a jump too (`docs/plan-three-uses.md`; `THROW.air*` in the config, her clip `her-airtoss`, the user, 2026-11-20).
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
| `src/intro.js` | **The welcome screen, the start sequence and the intro** (it ends on deck 3's corridor: her door opens, she walks out of it a few steps to the left (her `walk` clip, from behind the door's open leaf), straightens her badge and turns to go on to the left; then the hint how to move and jump, and "E to interact" the first time she walks past her door), all in the ship scene's own picture: one clock (`T`) and everything a function of it (the camera, what is open, what is shown), its parts and their lengths in `PARTS`; `intro.seek(part, k)` shows any moment, Esc ends it, `?play` skips it, `?intro=<part>` starts at a part. A new game gets all of it; a game under way a short way in. While it runs the game holds still (`scene.intro`, `scene.fromAfar`: the ship closed and the sky laid out in the world). **Its sky** (plan-the-rest §7b, the user's B3 of mock-ups, 2026-11-20): a soft sun with its bloom and no rays of its own, generated soft clouds round it and over the ship, god rays worked out from the clouds (built art: `tools/build_sky.py`); nothing between the sun and its path on the water ("looks off"); the path flickers glint by glint (`pathGlints`, `drawGlints` in `src/background.js`) |
| `tools/build_sky.py` | **The sky's art** (plan-the-rest §7b, built by the Refinement session, 2026-11-20): the intro's clouds (where each stands from the sun, its edge toward the sun lit) and sun into the atlas `skyart` (`assets/sprites/sky.png`; the key `sky` is another texture's) with `sky-layout.json`; the god rays worked out from the clouds (`sky-rays.png`: each cloud's shadow lane in the sun's light, so beams show only where clouds break it) and the bloom (`sky-glow.png`), smooth; the far clouds' strip (`sky-strip.png`); the sunset's (`DUSK_*`: its clouds, sun, rays, glow along the horizon and far strip, every colour divided by the evening light, the clouds' edges smoothed by `smooth_edges`). The clouds are generated (`assets/source/sky/tries/`, its README has the jobs), in their own colours, not the palette's (the user) |
| `src/popup.js`, `tools/build_popups.py`, `tools/build_heads.py` | **Every popup over a head** (the user, 2026-11-20, built by the Refinement session): **speech** (her words, "Meow!" from Bumbot's head in her arms), **thought** (a lock with its padlock and card, her hands too full for a ladder, the people's wishes), **shout** (her cry, no tail), **plate** (the hints). Generated frames (`assets/source/popups/`, its README has the jobs) sized to their words by a band whose edges match; generated icons; Galmuri9 (SIL OFL) at its own pixel size; built by `tools/build_popups.py` into `popups.png` + `popup-layout.json`. **The tail comes from the direction of the middle of the speaker's head and stops 3 px over it** ("not connected to it"), in every picture that shows her (her sheet, gags, mishaps, towels) and the people: `assets/sprites/heads.json` by `tools/build_heads.py` (PixelLab skeleton estimates kept in `assets/source/popups/heads/estimates.json`, rules for upright frames, a few by hand), kept **by clip**, mapped onto the sheets' frame numbers by the game. `s.alert`, `s.bubble`, `world.say(text, ms, { kind, from })` and the people's `bubbleItems` are popups with the old calls |
| `src/highlight.js` | **What she can use pulses where E would act on it** (the user, 2026-11-23, plan-the-rest §7c, built by the Refinement session): while she stands where E would act (asked as the ship scene's E chain asks it, the first thing only), the thing's colours pulse between its own state and the other one (1.6 s a pulse) and settle back when she leaves. A full-colour thing pulses down to the wash of the props round it (the nearest washed piece's level, else the map's `washLevels`, `tools/wash_levels.py`'s `table()`); a muted map piece shows its full twin, the wash pulsing off it. **Doors are secrets too** (`restDoors`): at rest every door she can use is washed like the background doors beside it (35%), else like the props round it, inside a room like the room (30% toward its wall), a lone trunk door 20%; the pulse brings it up to full colour. Never: people and Bumbot, a trunk's arrows, the MONEY JACKPOT sign, a pickup's glint; left as they are: the lifts, the glass doors across the deck, deck 11's lone steel one, the balconies' doors, the lifeboat's hatch, the shower's door. A wash is a copy of the picture filled with the wall's colour over it (`hlCopy`, skipped by `tools/check_overlaps.py`), cut as the picture is; things drawn into a room's picture by their own pixels (`IN_ROOM`: the mirror and shower door 40%, the desk by its shapes). `highlight.state()` and the `highlight` playtest |
| `src/signs.js` | **The ship's signs, drawn at their own size** (the user, 2026-11-21, built by the Refinement session): the crew doors' plates (`steel`; `navy` where the wall is dark, the door's `plate_style` in `tools/population.py`), the rope barriers' cards (`rope`, navy and gold, two lines past 40 px), the wall signs (`notice`, `bulletin`, `plaque`, `painted`, `card`: a sign's style in `SIGNS`). A 5 px pixel font of capitals drawn there (`GLYPHS`) and plates drawn by rule (a 1 px rim, a face, a lit edge or a band), each sign one canvas texture `sign:<look>:<text>`, no asset files. `sign(scene, x, y, text, look)` returns an Image; `signText` is what it reads (`tools/check_overlaps.py` counts it as text). The brass name plates (BOSUN, CAPTAIN) and the deck plaques are still text |
| `src/hud.js`, `tools/build_hud.py`, `assets/source/hud/` | **The HUD** (the user's design, 2026-11-20): nothing at the start, each count shows with its first find and stays. One row: the tangerines in a slot of their own on the left (kept free before the first), then the kinds of things to find as **faces** (Bumbot's, generated from his photo; hers, her front view; her husband's, from his character in pyjamas with the bear) and the book, **in the order first found**, each keeping the width of its largest count so nothing moves; under it the four key cards in fixed places, faint outlines until held. Every picture has a light rim; numbers in the popups' lettering, white on a navy outline (an ∞ drawn for `?tangerines=infinite`). The first tangerine flies to its slot (`gainTangerine`, `hud.landed()`); a card flies out of its close-up as that closes, a kind's count pops in then (`hud.expect()`/`release()`, `world.closeup(frame, then)`). The save keeps `hud` (shown, the order). `hud.state()` for the tests. The atlas is built from the approved sources by `tools/build_hud.py`; the generated tries, his character and their ids in `assets/source/hud/README.md` |
| `src/pixeltext.js`, `tools/build_menu.py` | **The welcome screen's menu art** (the user chose brass plates from three mock-ups, 2026-11-14): `assets/source/menu/` (the font and a generated plate) to the atlas `assets/sprites/menu.png`; `pixelText(scene, key, font, text, style)` sets a word in it (`T` the name's lettering, `S` the plates'), filled in bands over the capitals' rows, outlined, shadowed. **The lettering is Press Start 2P** (SIL OFL, `assets/source/menu/PressStart2P-Regular.ttf`; the user's choice of five, 2026-11-21) **with its own Ukrainian capitals**: the build sets every Latin and Ukrainian capital (Ґ Є Ї Й too) at 16 for the name (two art px to one of the font's) and 8 for the plates, each frame trimmed with its place in the font's 8 px cell kept as the trim, and `pixelText` steps by that cell. The menu is in capitals; a new menu word needs its letters there (`missing()`; the `lang` playtest fails otherwise). Where the menu stands is `MENU` in `src/intro.js` (60 px higher than at first, the user, 2026-11-21) |
| `docs/start-links.md` | A localhost link for every place the game can be started at (`?at=`), everything open and D free: add a line when the builder gets a new `place` |
| `src/sfx.js` | **Every sound, synthesised** (step 12): about 130 effects in seven groups, each with a line saying what it is for, made of two voices (`tone`, `noise`) and a few helpers (`bell`, `clank`, `thud`, `voice`, `applause`); `sfx.name()` at her ears, `sfx.at(x, y).name()` from a place in the world (fainter with distance, silent out of earshot); the ambience's five layers; mute (M). Volumes: `SOUND` in `src/config.js` and each effect's own line. **A gag's own sounds** (§3 1.3: `spin`, `bellyFlop`, `tiptoe`, `herCough`, `herSneeze`, `cartBump`, `trolleyRattle`, `headBonk`, `boatThump`, `towelFlump`) play on its clips' frames: `GAGS[...].sounds` in the config (clip key, frame from 1, effect), by the ship scene's `addedtoscene` hook on the gag sheets' sprites, for the gag of her last hit (`lastMishap`) |
| `src/world/soundscape.js` | What nothing in particular makes: the ambience's levels from where she stands (out on deck, inside, how high in the ship, by a pool), her footsteps by what is under her (`floor()`), rungs, a cart's wheels, strokes; the small steady sounds of a few places (`PLACES`) |
| `tools/check_sound.py`, `tools/soundboard.html` | Every effect rendered by the browser without playing it and measured (loudness, length, a spectrogram each on sheets in `%TEMP%/bumbusik-playtest/sound`): must end "all within bounds". The soundboard plays each by a button and has the ambience on sliders: <http://localhost:8000/tools/soundboard.html>, where the user listens |
| `src/sea.js` | The sea, drawn in code: rows of moving waves, foam along the waterline running on past the stern into the wake, the bow wave, the wake (§5.2); its sunset rows (`setDusk`) |
| `src/background.js` | The far background, drawn in code: the Baltic archipelago, the far sea, the clouds (generated: `tools/build_sky.py`'s strip), the far gulls (`FarGulls`, shared by every view), fixed to the screen and laid out each frame, the horizon settling over her floor (`HORIZON_ABOVE`); in the outside view on the waterline. The sea-view windows show a masked copy of it (`addWindowView()` in ShipScene) (§5.2). The sunset (§6.1.9): a second sky (blended, the user's S2) and sea faded over the day's (`setDusk(k)`), the sun, its glow, its god rays and its clouds placed from it (built art, `tools/build_sky.py`), the day's far clouds giving way to the sunset's, and its path of light flickering glint by glint; its colours are drawn divided by the evening light (`DUSK_LIGHT`, the ship scene's multiply wash) so that they look themselves under it |
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
| `assets/source/her-towel/` | Her towel-turban look (after the cabin's shower): PixelLab's "Towel turban" state of her character, `e2632c97-abd6-4f52-886f-ccf10b34b28d`; only the clips she uses in the cabin; built into `assets/sprites/her-towel.png` (the front still a row taller with its turban's top outline put back, `rotations/south-topped.png`; the turban's light blues grey, `grey_top`, the user, 2026-11-23). Her reading on the bed has a towel version, `bed-towel` (`assets/source/her/reading/`, cut by `tools/cut_reading.py`) |
| `tools/estimate_skeleton.py` | PixelLab's skeleton estimate for PNGs (0.1 generations each): poses to give a new state of her character the exact motion of an existing clip |
| `tools/build_ship_art.py` options | Per piece (and `-lt`, a light wash for the theatre's pieces, `LIGHT`; `keep` (from, to): a piece's own canvas columns kept, for pieces that must stand at one spot, the theatre's seat and its ten sitters): `height` shrinks a PixelLab piece to her scale, `join`/`from_x` mend pieces drawn across two frames, `flat` squares a base, `legs` runs short legs down to the floor, `caption` blanks a name the sheet wrote into the frame |
| `tools/draw_chapel.py` | The Chapel (deck 12), drawn by hand from her photo: its inside and its open door (run after `build_ship_art.py`: its chairs and flowers come from the atlas) |
| `tools/draw_linen.py` | The linen room (deck 9; **mirrored 2026-11-23**, the user: its door at its aft end, the wide rack forward of it, the chute's hatch straight over the laundry's cart on deck 4, a narrow rack aft of the door; the shaft's mouth on its forward wall is the game's, `tools/build_shaft.py`), drawn by hand: its inside and its open crew door. What moves is the game's (the user, 2026-11-23): Bumbot asleep on the bottle shelf, the generated vent cover he knocks to the floor (`vent-cover`, `vent-cover-down`, `assets/source/things/vent/`; `bb4Wakes` and `intoTheVent` in `src/world/story.js`), and the generated laundry cart she pushes, solid in her way (`thing:laundry-cart`, `"rim"` in `PUSHABLES`; the drawn cart is retired); its door washed 20% (`ROOM_DOOR_WASH` in `src/highlight.js`) |
| `tools/build_shaft.py`, `assets/source/shaft/`, `docs/shaft-remake-log.md` | **The ventilation shaft from the linen room to deck 8 forward** (the user's remake, 2026-11-23): at its true place and length on the ship (`SHAFT` in `tools/population.py`, `shaft_geometry()` in `tools/build_world.py`, `data.duct`). Its steel: the whole shaft drawn flat by rule (a flanged joint every 2 m, cross-broken panels), its pieces redrawn by PixelLab (`edit_image_pro_flash` keeps every shape in place), laid back along the run and lit by rule, into `assets/ship/shaft/strip.png` and `front.png`; `--mouth` cuts the mouth as the room shows it, its cover on and off, and the exit's grille from generated pictures of the room's corner; her slide down the slope (`assets/source/her/shaft-slide/`: PixMiniMax on a green copy of the shaft's own picture, she cut out by colour) into `slide.png`. In the game (`buildDuct`, `updateDuct`, `shaftSlide`, `shaftDrop` in `src/world/world.js`, `SHAFT` in `src/config.js`): one picture with the linen room, no cut going in (she crawls from the laundry cart's rim into the mouth, the room's `also: 'duct'` keeps it in view); the ship round it dark as round a room but for a cone of light under each grille, where deck 8 shows as it is (`world.lookOpen`); the last grille gives way and she drops out where the shaft ends. Put away in the outside view by the ship scene's cut-away (`shaftAway`) |
| `tools/draw_casino.py` | The casino's roulette and blackjack tables and the Stardust balcony's parapet, drawn by hand in strict side view (PixelLab kept drawing them at three-quarters): `assets/source/ship/casino-drawn/` |
| `tools/draw_lifeboat.py` | The ship's boats, drawn by hand in code (PixelLab's tries didn't read): the lifeboat, the tender, the rescue boat (`assets/ship/lifeboat.png`, `tender.png`, `rescue-boat.png`) |
| `tools/build_livery.py` | The ship's sun livery from its PixelLab tiles (`assets/source/livery/p2-*.png`) to one picture at full size (`assets/source/livery/livery.png`); then `build_ship_map.py` cuts it by deck into `assets/ship/livery.png` + `.json`. Its placement (`SHIFT`, `DROP`, `DISC`) is the user's. Its outlines are smoothed along their length with the tips kept (`sleek()`, `SLEEK`; the user, 2026-11-14); leftover spots are filled by rule (`fill_spots`) or by a point inside them (`SPOTS`); the bow's dark band's bulge evened by `even_band` (the user, 2026-11-23). **The user's own touches: `assets/source/livery/livery-by-hand.png`**, a copy of `livery.png` edited by hand (flat colours, no antialiasing), which `build_ship_map.py` uses in its place while it is there; never write it, and say so when `build_livery.py` is run while it exists (its changes then show only once they are copied over by hand). `tools/livery_photo.py` makes the tiles' generation inputs from the user's side photo |
| `tools/render_ship.py` | The whole ship from outside at full size, every deck closed (`ship-full.png` in `%TEMP%/bumbusik-playtest/exterior`, or the folder given), through the game's own outside view; in the game, O shows it too |
| `tools/shell_paint.py` | **The ship's side painted by rules** (step 11): the plating's seams, butts and shades, the shade under overhangs, weathering, the hull's marks and openings, as a picture the map builder cuts into tiles (after the placeholder ones in `assets/tiles/placeholder.png`, rows of 64); the parts the game draws itself get their pixels as marks (`shellSlopes`' `marks`, `stemMarks`, `plateSeams` in the map). Its colours and spacings are at its top |
| `docs/build-plan.md` | **The build plan**: step 0 the skeleton, then one step per region in play order, each with its scope, systems, art, playtest and exit. **All of it is built** (steps 0 to 12, 2026-11-14); its "After the regions" is carried on in `docs/plan-the-rest.md` |
| `docs/plan-the-rest.md` | **What is left, as one plan** (2026-11-18), in the order to build it: the rest of the mishaps' gags and their `mishaps` playtest; the rest of the twenty things to find, the fourteen books with their covers, cabin 8206's desk; the look-outs and the deliveries; each deck's own look; small faults; what waits for the user; what is done once at the end (the other documents, saving on, the release); what is closed. **The building session works from it and marks what it builds** |
| `docs/plan-three-uses.md` | **The three uses of a tangerine and the decks' life** (the cry and the lunge, the throw, the pocket; the mishaps' table §1.6; the twenty things to find, the look-outs, the deliveries, each deck's look): steps 1 to 4 and most of 4a are built, the rest is in `docs/plan-the-rest.md` |
| `docs/audit-2026-11-15.md`, `docs/plan-visual-fixes.md`, `docs/plan-fast-tests.md` | The user's audit (visual faults, empty decks) and the two plans that came of it and of the slow tests: the visual fixes and the stepped clock, both built whole |
| `docs/population.md` | **The population spec**: every person, hazard, item, secret, room and scene in place (deck, metres, behaviour), the corridors designed beat by beat; the build populates the ship from it (§6.1.13, phase 1) |
| `tools/draw_regions.py` | The progression plan (§6.1) drawn on the real ship (`docs/ship-regions.png`, `docs/ship-unlock-order.png`), from its own lists of regions, routes and steps; needs `tools/render_ship.py`'s picture |
| `tools/palettize.py` | Converts any image to the Resurrect 64 palette (`assets/palette/`); `blouse_grey`, her blouse's sky blue to its grey-blue, in every sheet of hers and the gags; `water_blue`, the water on her kept blue in her wet clips (`WET` in `tools/build_sprites.py`, the gags' `sprinkler-*`), told from the blouse by its cyan tint (the user, 2026-11-23) |
| `tools/population.py` | **The plan's world as data**: rooms behind doors, checkpoints, tangerines, pickups, Bumbot's beats, pushables, grips; `tools/build_world.py` turns it into `maps/world.json` (written with the map by `python tools/build_ship_map.py`). A pickup's options (2026-11-20): `from` (px up she must stand to take it: the plant, from the maid's bed), `cover` (the furniture's near part drawn again over it: the diary under its seat's arm); a ledge (`PLATFORMS`) may be in a room (her bed there) and name what is drawn over her on it; a person's `cycle` plays clips in turn (the maid: her bed-making twice, her stretch) |
| `src/world/world.js`, `verbs.js` | The plan's world in the game: builds everything in `maps/world.json` (rooms, the outside route of promenade, boat walkway and balconies, the duct, the funnel's top, things in place), answers E, ladders and grips; her verbs (crawl, wall jump, glide, push), mixed into the ship scene |
| `src/world/people.js`, `carry.js`, `story.js` | The ship's people (a person's `under`: a frame of theirs drawn behind the map's furniture, her husband's far leg under his table; `cover`: furniture drawn again over them, his chair's near arm (kept as `coverPics`, hidden while he stands for the kiss); a cast's `own_colours` keeps a whole figure off the palette, his; loops, a door on the way opened or turning them back: `door()`, bubbles, what touching them does, what her cry and her lunge do to them: `heard`, `lunged`; eating a tangerine from the hand, bite by bite, the fruit at the fist of each frame of their `bite` clip: `eat()`, `FISTS`; each mover has its own `heard()`/`lunged()`, `world.shout()` and `world.lunged()` pass the word on); carrying a tray and its rules (her hop with a load: `carry-rise`/`-apex`/`-fall`, the load by her fists, `HOP_HOLDS`; a hit with a load is a spill, its things set down on the floor by their height, and only a floor tray plays its gag as well, the user, 2026-11-23; **the deliveries** (§5 3.2): a load's own tray width and `view`, a picture round the screen while she carries it (the vase's flower frame, `assets/source/things/delivery/`, never in a zoomed-out view), `DELIVERIES` in the data and the world's `delivery` door: a hand takes it, a heart, a book; the tea's pot cools as the coffee does, `hot`; a delivery's tray and load gone from its table while she carries them, `lifted`; she holds it out, hands up, until the hand has it; the pillows' three pieces, `stack`, the top one sliding off when she stops short from a run, `slides`, `SLIDE`, put back by E and her crouch, `carry-crouch`, scattered flat by a spill, `soft`; a `thanks` instead of the heart); **whatever she carries is drawn at her depth, one step nearer** (in the lifts, behind a deck's floor on the stairs), turned the way she faces, **and turned to us or away at her middle, in front of her or behind her, her hands raised to it** (her `carry-front`, `carry-back`, `assets/source/her/carry-turn/`; the user, 2026-11-23); the story's own moments, one part per region |
| `src/world/tangerine.js` | A tangerine loose in the world (`LooseTangerines`, the scene's `loose`): thrown (F: `tryThrow`, `THROW` in the config; no hit knocks one out of her pocket since 2026-11-19), it bounces and rolls on her floors by its own route, rests, is kept in `save.loose`, picked up by walking over it, floats in a pool, is lost to the sea; offered each frame, lying or not, to whatever wants it (`world.offered(t)`: the scene's `offeredHere`, a lob into the piñata, each mover's `offered`, `people.offered`, `story.offered`; `loose.near()` is their test, `loose.claim()` hands one over, `world.gullTakes()` is any gull's). Its picture is `FRUIT` in `src/textures.js` (PixelLab's, chosen by the user; raw in `assets/source/tangerine/`) |
| `tools/hold_tangerine.py` | Puts the tangerine in her fist in her toss's frames (`assets/source/her/toss/` to `toss-held/`, which the sprite build uses) and in her throw in the air (`air-throw/raw/` to `held/`, `CLIPS`) |
| `src/world/library.js`, `movers.js` | The Library's books (the return trolley, the shelf with fourteen gaps over the two bookcases, `BOOKS` in the config; **reading**: E at any of the seven armchairs or on her bed in cabin 8206, she sits (`assets/sprites/reading.png`, `tools/build_reading.py`: two generated clips cut over the game's own chair and bed), the books she carries in a row to choose from (`choose()`, `?books=` to start with some), the page; the full-screen panel for a page or a photo slot); things that move by themselves or answer her coming (the delivery robot she rides, the shy gulls, the gull with Bumbot's collar bell on a promenade light that a thrown tangerine makes drop it (`BellGull`), the stage's swinging light, the casino's chips; deck 9's vacuum that darts out, towel stack, sprinkler, door that flies open, "Do Not Disturb" door; region 1's suitcase that rolls with the ship, the dog on a lead that fetches and trips her, the paper rounds, the breakfast round: `Roller`, `Fetcher`, `Skimmer`, `Breakfast`; **the look-outs** (`Lookout`, `LOOKOUTS` in
`tools/population.py`: still on the spot `LOOK.still` s, the camera is the look-out's and eases to the view, the decks it
shows opened by `world.lookOpen`, which the ship scene's cut-away crossfades from the dimmed hull, never undimmed; a drop
under one keeps both decks open as she falls; a `frame` zooms out to it, the ship closed, the far background held at
its size on the screen by `keep` in `src/background.js`, the Great Outdoors' stern; deck 4's aft porthole is by E instead, `PORTHOLES`, `world.lookOutOf`: her
back to us, the outside view, back on a movement key); a door's hand that takes things in is `world.handTakes()`, a round's doors are only those the corridor draws, `realDoors`) |
| `tools/check_corridors.py` | From the data alone: per deck, the longest walk with nothing to do and the longest without a reward (`docs/plan-three-uses.md` §4.7): run at the end of a step that places things on the decks, and give its numbers |
| `src/world/lido.js`, `hazards.js` | Region 6's part of the story, mixed into the Story (the pool's scene and its draining, the kid with the water pistol, the soft serve machine's swirl, the table with her husband (she sits down across from him in the patio chair with her cone: her clips `sit-cone`, `lick-cone`, `sat`, `sit-up`, `assets/source/her/sit-cone/`; his book from his fist, `GIVE_HANDS` in `src/world/world.js`), the chess set, the hot tub); the pool deck's and the hallways' hazards (the wet patch and its deck chair, the gulls that dive at food (no shadow, a 600 ms hover; off the screen with her cone and back, each leg by the clock: `FLIGHT`), the buffet queue, the trays outside a "Do Not Disturb" door) |
| `src/world/outside.js` | Region 7: the balconies' own things (gusts, the gulls perched on the rails, laundry lines across a folded partition, balconies with someone on them), the boat drill on the walkway (it answers her coming, as the flares do: `DRILL` in the config; 15 is 14a's fall with the boat down over her), the steward on his rounds; and its part of the story, mixed into the Story (the ajar balcony doors, the guest locked out on his balcony, the security officer at a tender). The vault over a partition and the climb up its pole are in `verbs.js` |
| `src/world/topdeck.js` | Region 8: deck 12's and the funnel's own things (the old lady's sunbed, the court's basketballs, Teppanyaki's flares (the chef answers her coming: `FLARE` in the config; her gag 19, `Flare.ride`), the funnel's wind and circling gulls, the flocks on the bow) and its part of the story, mixed into the Story (the mojito, the engineer's coffee, the horn and what it sets off, the telescope, the court's shot, **the sushi chef's tin of sardines for a tangerine**, 7: `sushi()` by E, `sushiOffered()` by a throw that reaches him, his palm and fist measured per frame in `SUSHI`). The glide's rules are in `verbs.js` and the ship scene (`overTheRail`) |
| `src/world/bow.js` | Region 9: the bow's own things (the sauna's steam, the kids' club's ball pit, the step class's boards, the bridge's alarm) and its part of the story, mixed into the Story (the wedding planner and the cake, the party into the chapel and the ceremony, the piano, the slide, the captain's door, near-catch 6 with the net on the alarm panel and the hatch's ladder, the Library's odd book and the nook). A fragile load's sway is in `carry.js` (`SWAY`) |
| `src/world/spa.js`, `tools/untable.py` | **The spa's massage** (deck 11, region 9; the user, 2026-11-22), mixed into the Story: the masseur (`amb_masseur`) works on his guest (`amb_massage_guest`) round and round (`MASSAGE.rounds` in the config: behind the table facing us, a stretch at her feet, in front his back to us, a stretch at her head); E at her table (she goes to the sauna's bench and back) or at the empty one (she waits lying): Bumbusik climbs on, gets the round, gets up and, the first time, his toss of Bumbot's massage gun (6). His depth: behind the table under it and whoever lies on it; in front over the table, over Bumbusik while she lies on it, under her while she stands; 1 px lower but facing us behind the table. Every step can be cut short (`run.stop`). The clips made with the game's table in their pictures (her climb, the guest's get-up) have it taken out by `tools/untable.py`, which also keeps her greys off the mauve her sheet turns pink and cuts the pad's leftovers from under the guest |
| `src/world/finale.js` | Region 10 and the end: the wind over the bow and the two crossing gulls; and its part of the story, mixed into the Story (the sunset's scene, Bumbot at the tip who backs off and comes to her standing still, the catch, where a miss puts her back, those who clap her home, cabin 8206's scene, the win screen, and after it the evening going on: the sunset, her husband on the cabin's sofa, the kids' club in bed; the user, 2026-11-23). Her look and rules with Bumbot in her arms are the ship scene's `holding` (`HOLDING` in `src/config.js`; her sheet `assets/sprites/her-cat.png` from `assets/source/her-cat/`, PixelLab state `6905f308-15b1-4a44-ad97-a38a7ad17dff`) |
| `tools/unchair.py` | Takes out a chair PixelLab drew under her in a seated clip (`assets/source/her/<clip>/` to `<clip>-clean/`), so she can sit on the game's own chairs |
| `tools/cast.py`, `fetch_people.py`, `build_people.py` | (Every folder in a person's `assets/source/people/<name>/` is built as a clip: a clip's own sources go beside it, as `kid-eat-cone/`, `sushi-chef-trade/`. A cast's `own`: colours of a clip kept off the palette, a thing the world shows in its own colours: the chef's tin.) The people's PixelLab characters, the download of their frames (`assets/source/people/`; the dog and its owner are kept by hand, `BY_HAND`), and the sheet `assets/sprites/people.png`, every clip's frames set on the floor (`OFF_THE_FLOOR` the ones that leave it); `tools/fetch_her.py <animation>` does the same for a new clip of hers |
| `tools/check_people.py` | The people checked against her: everyone standing next to her, heads against a pixel ruler (`--heads`), every clip of a figure (`--clips`); pictures in `%TEMP%/bumbusik-playtest/`. Run it on every new figure before making its clips |
| `tools/shoot_people.py` | Every person (or those named) in place in the game, close up beside her, tiled into sheets: facing, overlaps, what they stand on (see "Looking closely") |
| `tools/check_overlaps.py` | Overlaps that make no sense, by rule, from the running game: doors, plates, signs and wall pictures against furniture and each other, in four states of the story; `--shots` tiles a close-up of each. Must list nothing at a step's end |
| `tools/draw_rooms.py` | The plan's rooms drawn by hand in code (`assets/ship/rooms/<id>.png`); a room with no drawing is bare in the game. Also the blanket fort drawn in front of her (`adjoin-fort.png`) and the looks down through the duct's grilles (`assets/ship/peeks/`) ; what of a room is in front of the things lying in it (a bowl before its tangerines) is marked with `Room.in_front()` and saved as `<id>-front.png`, drawn over them |
| `tools/build_court.py` | **The court's two players** (deck 12; `assets/source/people/court/`, its README has the ids) to `assets/sprites/court.png` + `.json`: a man in red and a woman in blue, each a pro character with four clips made with the ball (the jump shot, waiting, the pick-up, a dribble), washed 12%. Played by `Balls` in `src/world/topdeck.js`: the round's clock sets their frame and the ball (from the hand through the ring, bouncing back to their feet; it hits her from the throw to its second landing); the game's ball turns to and from `basketball-lt` where it changes hands |
| `tools/build_towels.py` | **The towel stack's own clips** (deck 9; `assets/source/things/towel-fall/`, its README has the ids) to `assets/sprites/towels.png` + `.json`: its fall alone, the fall on her (from her standing, and four from her run's phases), her coming up in a towel turban with a towel swan, and the standing stack and stool apart. Played by `TowelStack`; the fall on her is a gag the thing plays itself (the ship scene's `thingGag`, `ride.play`) |
| `tools/build_gags.py` | **Step 4a's gags, each the thing's own clip with her** (`assets/source/her-mishaps/batch-4a/`, its README has the ids) to `assets/sprites/gags.png` + `.json`: the swinging door alone and slamming her flat (13a) and her slide down the wall, the same swing in full colours for the "Do Not Disturb" doors, her tray ride from four quarters of her stride (3; the world's tray base moved under her by the game, `trayAt`), the deck chair collapsing under her (7b; it cannot happen since the chair stands still, 2026-11-19), her dive face first onto it and her sled on it (7a, `chair-sledge/cut.py`), the gull on her head (20), soaked under a sprinkler, her sneeze and her squelch back (16; the kid's jet plays it too with none on her, `soakRide` in `src/world/movers.js`), her hair a puff out of the sauna's steam, fanning herself and swooning (17), sooty out of Teppanyaki's flare, blinking and coughing out a puff (19; its greys on her hair's charcoal, `SOOT`), bumping down the funnel's stairway on her bottom and dizzy at its foot (21; cut by `stairs-bump/cut.py`, played by the ship scene's `stairsGag`), the parasol blown inside out over the bow, she looking up at it and kicking as she drops (22; `parasol-flip/cut.py`, the ship scene's `parasolGag`). The court's balls, 14a/14b: stiff as a plank onto her back or her face, from her stand or a quarter of her run, then lying so with the butterflies (`ball-*-lie`, set on by `ball.dx`; `starts/ball14/`). The stage light's 12a/12b reuse 9a's spin (and `jog-spin-stand`, from her standing frame) and 9c's belly-flop (`lightSpin`, `lightShoved`). The jogger's four (9a spun like a top, one clip per quarter of her stride; 9b bowled back; 9c shoved onto her belly; 9d 8d's bounce off his back; the ship scene's `jogGag`, his own `sorry` and `scratch` in the people sheet; the sheet is 17 frames wide). Her hands over her eyes at a "Do Not Disturb" door, blushing, and her quick tiptoe off (23; `dnd-sorry/cut.py`, the ship scene's `sorryGag`; the same on an occupied balcony, 24, to the partition ahead: `partitionShort`); the doors' swing is built from `door-burst-dnd/`, the same frames with the doors' sign on the lever's mount (`assets/source/ship/dnd-hanger/`: the sign drawn by hand, `swing.py`; the shut door `assets/ship/door-cabin-dnd.png`, the sign alone `dnd-hanger.png`, also on the occupied balconies' partitions and cabin 8206's door). Each played by its mover (`ride.play`, the ship scene's `thingGag`). The door clips keep their own (muted) colours: only her pixels go on the palette |
| `tools/build_drill.py`, `tools/build_hatch.py`, `src/wire.js` | **The boat walkway's own** (2026-11-21, the user's): the drill's winch and its crewman, one generated clip turned with the boat, and her gag 15 under its boat (on all fours, crawling away: `assets/sprites/drill.png`, the ship scene's `crawlGag`); the lifeboat she enters through a roof hatch (its pieces in the things atlas, her pull-up `mantle-front` of her own character; the ship scene's `roofClimb`/`roofOut`, `ROOF`; a ladder inside she starts on and leaves by, `world.roofLadders`); every boat's cable a wire rope (`wire()`). The boats are drawn in front of her on the walkway (`BOAT_DEPTH`), the walkway's railing between; every red lifeboat in one design (round windows, the boarding hatch's outline), the one she enters as `lifeboat-round` (its hatch open, drawn by the game), the rest with it closed (`tools/draw_lifeboat.py`) |
| `tools/build_closeups.py`, `assets/source/closeups/` | **The close-ups** (the user, 2026-11-19, "A and C"): each thing to find and each key card as a detailed PixelLab picture (about 100 px; its README has the ids), on the palette (the tennis ball keeps its felt) into `assets/sprites/closeups.png` + `.json`, a frame per keep name (`wool`) and `card-<card>` (one card, its stripe recoloured). Shown by `world.closeup()` when she gets one (`take`, `giveKeep`, `progression.open('cards')`): at 2x in the middle of the screen over a dim, a warm light behind, she held and nothing touching her (`scene.viewing`) until any key. **The world's sprite of such a thing is its close-up shrunk** (`FROM_CLOSEUP` in `tools/build_things.py`), a little bigger than life; the playtests skip the moment (`Browser(closeups=False)`, `window.__skipCloseups`) but where it is checked. Every pickup lying in the world (and a key card lying out) glints now and then at its top right corner (`world.glint`, the user, 2026-11-20; not the tangerines). The other pickups have their close-ups too (2026-11-20): the grip socks, the parasol, her pills (her only quest item kept in the pocket), from `take()` for a `verb:` or an `item:`. His guitar pick's (16) is from the user's photo of his own (`tries/pick/`), its world picture built by hand from it, point up so that it rests on its wide edge. His handheld's (15) is a pro redraw of his model's photo (`tries/handheld/`), its world picture the user's own pixels (`handheld-by-hand.png`, never written by a tool). His sleep mask's (14) is try 1 smoothed by rule (`tries/mask/smooth.py`), its world picture its body shrunk and outlined, both in their own colours. His navy t-shirt's close-up (13) is the top half of a shirt with the logo from his photo, built by `tools/draw_tshirt_logo.py` from **the user's own pixel edit of the logo, `assets/source/closeups/tshirt-logo-by-hand.png`: never write it** (`--write-built` writes the built one to `tshirt-logo.png`, which the user once saved over); its world picture is a small generated folded shirt, not it shrunk. The books' covers (§4 2.3) are to come the same way |
| `tools/build_things.py`, `draw_pages.py` | The plan's own things from PixelLab map objects (`assets/source/things/` to `assets/sprites/things.png`: the robot, the gulls (and the bell gull's three frames with the collar drawn in by hand, `gull-bell/`), the promenade's wall lights (`lamps/`), the towel animals, region 1's flags, shelf, laundry cart, basket, a door's hand, the cry's two signs; the tries and their ids in `tries/README.md`); the fourteen books' pages (`draw_pages.py`): each book's real opening in its own script, set in Pixelzone (CC0) from `assets/source/pages/<nn>.txt` (its README: where each came from; all fourteen real, 1, 2, 4, 6 and 14 typed by the user from her copies), and each title for the row (`assets/ship/pages/`) |
| `tools/build_desk.py`, `assets/source/closeups/desk/`, `bed/` | **Cabin 8206 seen close** (§4 2.4, the user's, 2026-11-22): two pictures over the whole screen (`world.seenClose(scene)`), each thing on it from its find (`save.keeps`), bare where one is not found yet and with none. **The desk:** E at it, any time she is in the cabin (`look`: Bumbot in her arms too): the desk under the TV's lower edge, her four things and his four (`DESK_THINGS` in the config). **The bed:** on the day after, E by Bumbot from the floor (he purrs; on the bed E stays her reading): him lying on it, from the user's photo, his eight round him (`BED_THINGS`). Each built from PixelLab's redraw of a rough of the close-ups: the bare picture by rule (flat surfaces filled along the row; the bed's runner from its own pattern, its cushions straight down: `bare_bed`), each thing what differs from it in its box, into `assets/ship/<scene>/`. `?keeps=` (`desk`, `bed`) for testing |
| `tools/build_covers.py`, `tools/pixelzone.py`, `assets/source/covers/` | **The books' covers** (§4 2.3, 2026-11-22): her own copies' covers, photographed by the user (`reference/books/`, git-ignored), straightened, words painted out, redrawn by PixelLab (`image_to_pixelart`, 120 x 180; tries and ids in `assets/source/covers/README.md`), a few colours mended (`MENDS`), and the title and author set back in where her copy has them (`COVERS`: scale, turn, a slant by whole letters, tight letters, outline, Hebrew right to left) into `assets/ship/covers/cover-<n>.png`; shown by `world.cover()` (the close-up's code: a 35% dim, the warm light, a shadow) when she gets a book. The small books' and spines' colours come from them (`BOOK_COLOURS`, `BOOK_ACCENTS`); the row's small covers (`mini-<n>`) are PixelLab's 16 x 22 redraws of the covers' pictures without lettering (`assets/source/covers/mini/`), greyed with a green check (`STAMP` in `src/world/library.js`) once given back. The nook's photo: `tools/recolour_nook_photo.py` (her armchair recoloured, the throw's weave) and `tools/frame_nook_thumb.py` (small, faded, framed on the wall), `assets/source/photos/nook/`. La Cucina's photo (`slot_cucina`, the user's own of the two of them at its window table, on its wall on deck 5 after his table scene): PixelLab's 168 x 224 redraw, shown at 2x, its small framed copy by `tools/frame_nook_thumb.py cucina`, `assets/source/photos/cucina/`. **Pixelzone is always drawn through `tools/pixelzone.py`** (eight times larger, read back: FreeType's hinting at 16 px moves its small parts); its Й/й are mended in the font file (И with a line a row above, the user's choice) |
| `docs/progress-decisions.md` | **The autonomous build's log** (the user's order, 2026-11-13): every change or addition to the plan made while building, with its reason, step by step |
| `tools/playtest.py` | Headless Chrome playtests with real key presses; `python tools/playtest.py [scenario]`. **`region3.lookout`**, **`deck4.porthole`**, **`region6.lookout`**, **`region9.lookout`**: the look-outs (§5 3.1). **`deliveries`** (§5 3.2): the vase, its frame, a tray's spill and ride, the hand at 8215; the tea, off its table, turned to us and away, gone cold, the hand at 10230; the pillows, the low hop, the slide and the crouch, the scatter, the thanks at 9245. **`keeps`** (§4 2.5): the one scenario with the close-ups shown: each count on once its close-up or a book's cover closes (a book's count waits for its cover too), his four places before and after his table scene, the desk and Bumbot's bed seen close, each found thing there and the rest bare. **`mishaps`** (§3 1.3): a case per hazard whose hits had no check of their own, each hit made through the thing's own code (a person's `world.touched`, a round's hit, the hazard met in play from its `?at=` place), none on her and two (`mishap_hit`, `both`: the scenario, its gag's clip, her checkpoint, the count); the table of every hit and where it is checked: `docs/population.md` §2.9. Positions come from the map builder. **On the stepped clock** (`docs/plan-fast-tests.md`, built 2026-11-18): once a page is loaded the test stops the game's loop and steps it itself, a sixtieth of a second a frame, undrawn unless a screenshot is wanted (`takeover`, `Browser.advance`); every wait in a scenario is `wait()`, every deadline `now()`. `-j 6` a process and a browser for each scenario, six at a time (the whole suite in about a minute); `--failed` those that failed last time; `--times` each one's time; `--real` real time, for comparing; `--seed N` the random draws' seed. `boot` and `sound` always run in real time. A scenario's cases: `scenario_region4__towels` is `region4.towels`, and `region4` runs it with the rest. The other tools that use `Browser` (`check_overlaps`, `shoot_people`, `render_ship`) are stepped too, `--real` for the old way; `check_sound` is real |

## Rules that are easy to break

- **Words and pictures over a head are popups** (`src/popup.js`): `world.say` (her words; `{ kind: 'plate' }` for a hint, `{ from: 'bumbot' }` for his), `s.alert`, a person's `bubble` (a wish, a thought cloud); never an `add.text` box. **After rebuilding a sheet of hers, a gag sheet or the people's, run `python tools/build_heads.py`**; a new clip of hers that is not upright, or a gag, needs its heads estimated first (`--missing DIR`, `tools/estimate_skeleton.py`, `--from DIR`, 0.1 generations a frame), or its popups stand over where she is with their tails short of her.
- **A sign on the ship is `sign()` with one of its looks** (`src/signs.js`), never an `add.text` box: kept to its place and about the size of what is round it (the user turned down plates sized to a font: "oversized and do not fit their places"). A new look goes into `SIGN_LOOKS`, a letter it lacks into `GLYPHS`; a new look or a sign in a new kind of place is mocked up beside the old one in the same shot first.
- **Her picture is drawn `PLAYER.sink` (1) px lower than her body's foot** (the user, 2026-11-20): anything new drawn
  in front of her that stands on her floor line must reach that much lower too (`withFoot` for an image, a px
  taller for graphics), or her lowest row shows under it; on the promenade's deck the row is left off.
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
- **Files the user edits by hand are never written by a tool:** `assets/source/livery/livery-by-hand.png`,
  `assets/source/closeups/tshirt-logo-by-hand.png` (the build uses each in place of its built twin) and
  `assets/source/things/handheld-by-hand.png` (his handheld's world picture, the user's Paint edit on white, white
  being empty: `BY_HAND` in `tools/build_things.py`). When the user
  is given a file to edit, a build must not write that file on its next run.
- Sprites face east; west is `flipX`. Background props are muted so they never read as interactive.
  **How much is the place's** (the user, 2026-11-20, chosen deck by deck): a background prop is placed with
  its `-bg` name and `tools/wash_levels.py` gives it its place's twin, `-bg` (35%), `-w20` (20%) or `-lt`
  (12%), in the map builder's `put()` and the world builder's last pass. Most decks are at 20%, the Library,
  Magnum's and the Sports Bar at 12%; **the guest cabin corridors stay at 35%** on every deck (their props are
  laid by the ship scene itself), as do decks 8 and 9 inside, doors she cannot use and railings; the casino's
  slot machines at 12% wherever they stand (`PIECES`, the user, 2026-11-23). A new venue or a change of level
  goes into that table, never a new suffix by hand.
- **What she can use is shown by its pulse, not by its colours** (the user, 2026-11-23, `src/highlight.js`):
  where E would act, the thing pulses. **Every door she can use is washed at rest like what stands round
  it** (the background doors beside it, else the props, inside a room the room), so it reads as a
  background door until she is at it: "they will work like secrets". (It replaces the rule of 2026-11-15,
  every door in its full colours.) The pictures still draw every door she can use in its full colours
  (`Room.full` in `tools/draw_rooms.py`, `keep` in `draw_cabin.py`, `draw_linen.py`, `draw_chapel.py`;
  inside every room she enters the rest above the floor is washed 30% toward the wall, as in cabin 8206):
  the game washes them. A new door is found by `restDoors` by its picture's name (`door` in it); a new
  thing she uses whose picture is a map piece goes into `PIECES` there, one drawn into a room's picture into
  `IN_ROOM` (GAME_DESIGN.md §2.1).

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

Lessons learned (2026-11-23, the shaft remade):

- **A passage is drawn at its true place and length, joined to the room it opens off:** a strip drawn shorter than its
  way and entered by a fade turned her round and showed rooms that were not there (the user: "how can she peek down
  into the room that are not there?"). Laid where it runs, what shows under it is the ship itself, live, and nothing
  needs a cut: she crawls in, and drops out where it ends.
- **Which way a room faces is part of the route:** a way that leads forward is entered facing forward. Mirror the room
  rather than turn her inside the passage (the user: entering and turning "still interferes with the player's sense
  of direction").
- **Steel, walls, long repeated structure: draw it flat by rule with the real thing's features, then have it redrawn**
  (`edit_image_pro_flash`: every shape stays where it is, the surface becomes worn metal). PixFlux img2img returned
  the flat drawing; text alone gave another style and a perspective. Each redrawn piece comes back in a tone of its own:
  bring them to one mean before laying them side by side.
- **A state of a thing is one picture plus the part that changes:** three generated pictures of the mouth (cover on,
  off, fallen) each drew the duct differently; the game uses the open one's duct in every state and cuts only the
  cover from the other.
- **A clip of her made on a dark set is made on that set turned green:** cut from the dark duct by difference she lost
  her navy skirt and dark hair in two frames of nine; on a green copy of the same picture (its shapes kept, so the
  motion still follows the slope) a colour rule took her out whole in every frame.
- **What a world's update shows must also be hidden where that update does not run:** the shaft's dark stayed over the
  ship in the outside view (O), since `world.update` is not called there; the ship scene's cut-away, which runs
  everywhere, puts it away.
- **Never stage a file in the shared folder before the commit:** the index is shared with the other sessions.

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
- **No progression hints; every new mechanic explained once** (the user, 2026-11-14: "Part of the
  game is figuring things out. Labels and namings are not considered hints"; revised 2026-11-20:
  "no game progression hints, like 'go there', or 'jump down here'. But every new mechanic
  introduced, has to be explained once"). Never a text or a sign that says where to go or what to
  do next. But the first time a mechanic is hers, one popup over her says how it is used, in the
  keys or the controller's buttons, whichever she plays with (`hint.*` in `src/lang.js`, both
  languages). Built so far: "← and → to move, Space to jump" as the intro hands her over
  (`hint.move`, `hint.move.pad`), and "E to interact" the first time she walks past her door
  (`hint.interact`). Signs, plates and the people's pictogram bubbles are fine.
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
- **Small text in generated art is drawn by us:** the generator smears letters a few px high into
  a scribble; stamp them in pixel letters over its try (painted out first), anything in front kept
  on top by its colours. Slant small text by whole letters, never through one.
- **UI art from PixelLab:** `create_ui_asset` (10 generations at 256 x 256) draws plates and
  panels to a template of shapes, in the game's palette when it is passed; `create_font` (15)
  gives an atlas of 80 Latin glyphs, eight to a row, and nothing else (no Cyrillic). Use the
  glyphs as shapes and colour them in the game; build what is missing from them by flips where
  the shapes allow (flat shapes only: a flip turns a shaded letter's light upside down).
  Canvas compositing: `source-in` clears everything outside the new shape, so a second band
  wipes the first; bands go on with `source-atop`.
- **A style is chosen from mock-ups of the whole screen**, composed offline over a real
  screenshot, in both languages and with an entry chosen, not from the loose pieces.
- **Show the user the shot, not only the figure, before making its art:** a rough frame of the
  composition first saves generations spent on figures for a shot the user had not described.

Lessons learned (2026-11-14, the intro shown to the user):

- **A cutscene is judged in motion, and I only see stills:** a sequence can look right frame by
  frame and not work at all run. Build the plainest version that runs end to end and show that
  first; make its special art only after the user has watched the plain one.
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

Lessons learned (2026-11-20, the bell gull and the throw in the air):

- **A ship's fitting is what a ship has:** two generated wall lanterns were "on no cruise ship"; look up the real
  fitting (bulkhead lights, embarkation floodlights) and generate that. And the raw tries go into the chat first,
  alone, before any mock-up in the game.
- **A small thing held by a small figure does not survive a shrink:** a generated collar in a 20 px gull's beak
  read as nothing, its close-up shrunk as a scribble; drawn by hand at game size in the close-up's own colours
  it read. Keep the figure's own pixels and add only the thing, so the hand-over (the bell dropped) is one bird.
- **What the player expects to do decides the mechanic:** a lob reached the gull only from 1.25 to 3.5 m, and a
  player walks up close; measure a target's reach by a sweep of throws, then ask what a player would try (a throw
  in a jump). Its arc too is measured, not guessed: a level throw dropped under the target past 1.5 m.
- **An effect on a clock or by her distance, drawn over her layer, shows through the hull from elsewhere:** the
  studio's flash from the promenade and from the deck above, the stage light from the balcony, the steam from the
  deck above. Gate it on her route and her deck, never her distance alone; a sweep of the code found them.
- **A background for a composite is shot without the game's own copy of what is composed** (the gull drawn twice).

Lessons learned (2026-11-20, the popups, the Refinement session):

- **Data about a sheet's frames is kept by clip and frame-in-clip, never by frame number:** a clip added in
  the middle of her sheet (`airtoss`) moved her walk's frames, and a table by number would have put the wrong
  heads on them. The game maps clip data onto the sheet's numbers from `<sheet>-meta`.
- **PixelLab's estimates are throttled when run several at once:** six in parallel came to two a minute with
  dropped connections; two at a time, one per call (`xargs -P 2 -n 1`), about one a second. A stopped run's
  children go on: look for them (`Win32_Process`) before starting another.
- **A frame stretched by repeating its middle smears what is not straight:** a burst's spikes repeated a pixel
  at a time read as stripes. Choose, once, a band whose two edges match over a whole spike or bump, and repeat
  only that (`band` in `tools/build_popups.py`).
- **To read a file as another branch has it, `git show <branch>:<path>`;** `git checkout <branch> -- .` overwrites
  every file of the tree (it undid a merge in progress here; `git merge --abort` and the merge again mended it).

Lessons learned (2026-11-20, the sardines):

- **Questions one at a time, each with its context** (the user: "Give me questions interactively, one by one, with
  the context"): an AskUserQuestion per decision, the facts it rests on in the question itself.
- **Look at what a person's reach crosses at the counter:** the chef's hand landed on the nigiri plate; a prop moved
  behind him (the user's choice) was free, a second edit was not.
- **A thing in its own colours stays so everywhere it is shown:** palettized, the tin's blue silver went purple in
  the close-up, the world's picture and his clip; `OWN_COLOURS` (close-ups, things) and the cast's `own` (a clip).
- **A scenario's cases run in its browser, after it:** a case that opens without `?reset` keeps what the scenario
  did (the bell kept): a case opens with `?reset`, and checks only its own thing.
- **A thing caught from a throw is reached by a sweep, not a guess:** a lob reached the chef from 1.3 m, a throw in
  a jump only from 2.7 m; between, over his head. Say the reach to the user.

Lessons learned (2026-11-21, his t-shirt):

- **Words a few px high in generated art are a scribble:** a logo from a photo (`image_to_pixelart`) kept its shapes
  and colours, never its small word; stamp the words in pixel letters, and when the user wants to touch it, give them
  the file (on a flat ground any editor keeps, five colours named) and read their edit from a `-by-hand` name.
- **The world's picture of a thing is not always its close-up shrunk:** a folded shirt shrunk read as a dark bag;
  a small one generated at its size (and the close-up showing what the world's cannot, the logo) read.
- **A prop near life size reads best at its generated size:** a slatted lounger shrunk 2x went faint, outlined its
  slats became teeth; at 82 px (2.3 m) it was right. Darker by a factor on its washed twins (`SHADE`), not through
  the palette, whose darker greys are purple.
- **"Reached only after" is checked against the regions' order** (`STEPS` in `tools/draw_regions.py`): the linen room
  and the pool deck both come before the table scene; deck 12 only past his table.

Lessons learned (2026-11-21, his sleep mask and the balconies):

- **Phaser 4 crops a picture turned by `flipX` wrong:** its content shifts by width - 2x - w (only a centred crop is
  true). A picture turned by a scale of -1 crops true but moves its physics body: so on the balconies a stand-in of her
  (`balconyPic`) is drawn turned by its scale, her own sprite cropped to nothing. The Mask filter on her sprite hid her
  whole, with the rectangle in world, screen or her own space alike.
- **A copy of the ship's side (`plateCopy`) has only its tiles:** windows and lamps on it are objects of their own, and a
  copy laid over them hid them. Compare the view with the copy on and off before keeping one.
- **A balcony's floor is not a way down by itself:** check what lies one deck under it (rows end at different metres on
  each deck). And the outside route is called `promenade` in `spawnAt` and the data: a test teleported with
  `route="outside"` showed no pickups out there (`shown()` matches the route by name).
- **A bare place a thing must lie on is furnished by hand, not by bending the rule:** `BALCONY_SET` names what stands on
  a balcony and its towel; the rule furnishes the rest as before.

Lessons learned (2026-11-21, the boat walkway and the lifeboat's hatch):

- **A sequence of her is built from her own character's art only:** a generated clip of the whole climb was in another
  drawing (her head, her face, her size) and every joint with her sprite broke; a clip of her character (skeleton-v3,
  poses written for it) and her own sheet's frames, joined by position, held.
- **Her hands are on something in every frame** (memory: hands-hold-something): an in-place climb clip moved up climbs
  the air; her ladder clip over a roof holds rungs that are not there. Hold the hands on the edge in the world and move
  her body from them.
- **In a strict side view, going down into a hole and going down behind a thing look the same:** the roof line cuts her
  either way. The hole must be drawn seen a little from above, wider than her, she in front of its far rim and cut at its
  near lip, its dark showing either side of her; a lid standing in front of her says "behind".
- **Show a sequence as all its frames together, then as a GIF, then record it in the running game, before calling it
  done:** joints that each still passes (a jump of 33 px, two identical frames) show only in a row.
- **A generator matches what it is drawn on:** on the wall's grey her face came out grey and was cut away with the wall;
  generate a figure to be cut out on a ground none of her colours is near (green).
- **A thing moved to another depth leaves the band a check counts it in:** the boats in front of her fell out of
  `check_overlaps`' outside depths and were compared with deck 7's furniture; skip them by name, with the reason.
- **A room entered from outside keeps the ship's side closed round it** (`inDeck` false): cut open, it showed the deck
  behind the hull (the lifeboat showed the casino).
- **A piece of furniture is asked for by its shape, not its name:** "console table" came as two low desks ("None of them
  are consoles though"); "tall slim ... taller than a normal table, thin legs" gave consoles. Tries that differ are shown
  placed in the game side by side (all four, the user's ask), where the choice is made.

Lessons learned (2026-11-21, the books and reading):

- **A book's text from the web comes a couple of sentences at a time:** the fetching tools quote little from a book's
  page, and a longer passage is not to be got round that limit. The user gives longer passages from her own copies;
  where a page shows more (a publisher's sample, a school excerpt), say where each came from (`assets/source/pages/README.md`).
- **A pixel font's strip is cut to every row its letters reach:** a Hebrew lamed and a Ukrainian Ї's dots rise above the
  capitals, a Polish ogonek hangs below; a strip cut to the Latin capitals hid them (the user saw it in a mock-up).
  Measure with the font's own box, and give every title one height so none jumps as the choice moves.
- **A key counts only in the frame it is pressed:** a guard delay after a menu opens ("so the E that opened it does not
  act") ate the next press; it is not needed when the opening key was frames ago.
- **A figure cut out of a generated scene by difference loses what matches behind it** (a white blouse on a white
  bed, dark hair on a dark wall): keep her largest piece and fill what her outline encloses; take off what the
  generator redrew round her by its colour (grey-blue wisps over brown hair).

Lessons learned (2026-11-21, his handheld and Champs):

- **A thing of a few px is built at its size, feature by feature, from a clean picture of it:** the converter at 11 to
  16 px high, or a photo shrunk, gave blobs (the user: "really broken"). A clean front view first (`image_to_pixelart_pro_flash`
  from the photo, its logos painted out), then each feature placed (outline, screen, the sticks' rings, the d-pad), the
  top edge lit to stand off what it lies on; then the user's own Paint edit, read from a `-by-hand` file on white.
- **A real product is drawn from its photo, never from a description:** four described handhelds were "neither"; the
  user's reference of the exact model gave it. Paint out every logo and word before sending (OpenCV inpaint, a screen
  filled with its own gradient where a ghost stayed).
- **A ship's fitting is looked up before it is generated:** the bar came right only after the real Champs Bar's
  photos (honey teak planks under a pale top); "a bar" from text was a pub's. Galleries: cruisedeckplans.com.
- **A person's sources folder takes clips only:** a `tries/` folder beside `stand.png` was read as a clip; tries go in
  `<name>-raw/`. A crowd's new face is an edit of a figure already there, "a different person in exactly the same pose"
  (5 generations), its stool the same pixels.
- **A small thing lying on something rests on a flat side:** a pick drawn point down stood on its tip on the amp; turned point up it rests on its wide edge. Ask what it rests on before choosing which way up it is drawn.
- **A palettized brown went mauve, and pink when lightened:** a piece whose colours the palette spoils is kept in its
  own (`OWN`, `BRIGHTEN` in `tools/build_ship_art.py`).

Lessons learned (2026-11-22, the books' covers):

- **A real thing's picture comes from the user's own copy when the edition matters:** the covers found online were often
  other editions; her own copies, photographed straight on, gave each exactly. Straighten by GrabCut and a warp; paint
  the words out before generating (boxes measured on the cover at its true shape, not on a squashed sheet); set the
  words back in ourselves.
- **A font drawn at its tiny native size can be bent by FreeType's hinting:** Й's dots came a row above their bar, the
  Polish accents a pixel off. Draw it large and sample each pixel's middle (`tools/pixelzone.py`), then look at the
  letters of every script used, enlarged, before trusting a font's small parts.
- **A colour picked by count picks the outlines:** most covers' commonest colour was their black outline; count
  without the darkest unless they are most of the picture.

Lessons learned (2026-11-22, the books given back and the nook):

- **A colour change by a hue rule needs the part found by its outline, not its colour:** the cushion's top half was a
  bluer grey and went to the chair (a diagonal, a yellow tint); a flood fill inside its dark outline took all of it.
- **A cut-off line in a texture is a seam:** flecks stopped at a row made the chair's lower part look broken; keep a
  texture whole or end it at an edge the picture has.
- **A box kept unwashed in a washed room shows as a pale patch:** keep a piece's own pixels, not its box.
- **A word wider than its slot overlaps its neighbours when the row is full:** mock the fullest case first (fourteen
  books), then choose where the word goes.

Lessons learned (2026-11-20, the HUD):

- **A UI is settled on mock-ups over a real shot, at the game's pixel size, one change a round:** the user moved
  the row a pixel at a time, asked for the rim, the order, the slot; each a few seconds composed offline (PIL,
  the game's own glyphs and pictures), then built once.
- **Pixel art is never made smaller by resampling:** shrunk by majority the faces "became distorted" (a bear
  became an x). Cut whole rows and columns where the picture is plain, protecting the features' rows (a cat's
  nose went first), or keep the size.
- **A face from a photo:** cut the subject out first (GrabCut; a dark animal against a light wall by its
  darkness, its ears filled by their hulls, lit fur taken back by brightness) and look at the cut enlarged: the
  user saw a notch and a stray patch at once. At 24 px a generated likeness of a person failed every time ("all
  bad"); a character made from the photo (pro, the cast's style), approved whole, and its face cut from it, held.
- **Inside a Phaser Layer `setDepth` does not reorder:** move a child in its `list` (`Phaser.Utils.Array.MoveBelow`,
  `BringToTop`).
- **Glyphs the lettering lacks** (×, ∞) are drawn in its own stroke, on the rows of the glyph they stand beside.

Lessons learned (2026-11-19, the theatre's audience):

- **"The same chair" means the same pixels:** five people drawn each in a chair of their own read as "similar, but
  different". Take each out of their chair (`edit_image_pro_flash`, "remove the chair, the same pose"), then set them in
  one seat split in two: what is behind them (the backrest, the far arm) and what is in front (the near arm, the seat's
  front). New people for a crowd: edits of those, "a different person in exactly the same pose", 5 generations each.
- **A wash is the user's to set per place:** the background's 35% read as "washed out too much" in the dark theatre.
- **A piece that keeps its canvas counts its empty part in `check_overlaps`:** keep only the columns it needs and cut its
  top to what is drawn (it stands on its bottom row).
