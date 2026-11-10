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
| `tools/draw_linen.py` | The linen room (deck 9, a heap of towels on its floor), drawn by hand: its inside and its open crew door |
| `tools/draw_lifeboat.py` | The ship's boats, drawn by hand in code (PixelLab's tries didn't read): the lifeboat, the tender, the rescue boat (`assets/ship/lifeboat.png`, `tender.png`, `rescue-boat.png`) |
| `tools/build_livery.py` | The ship's sun livery from its PixelLab tiles (`assets/source/livery/p2-*.png`) to one picture at full size (`assets/source/livery/livery.png`); then `build_ship_map.py` cuts it by deck into `assets/ship/livery.png` + `.json`. Its placement (`SHIFT`, `DROP`, `DISC`) is the user's. `tools/livery_photo.py` makes the tiles' generation inputs from the user's side photo |
| `tools/render_ship.py` | The whole ship from outside at full size, every deck closed (`ship-full.png` in `%TEMP%/bumbusik-playtest/exterior`); in the game, O shows it too |
| `docs/population.md` | **The population spec**: every person, hazard, item, secret, room and scene in place (deck, metres, behaviour), the corridors designed beat by beat; the build populates the ship from it (§6.1.13, phase 1) |
| `tools/draw_regions.py` | The progression plan (§6.1) drawn on the real ship (`docs/ship-regions.png`, `docs/ship-unlock-order.png`), from its own lists of regions, routes and steps; needs `tools/render_ship.py`'s picture |
| `tools/palettize.py` | Converts any image to the Resurrect 64 palette (`assets/palette/`) |
| `tools/playtest.py` | Headless Chrome playtests with real key presses; `python tools/playtest.py [scenario]`. Positions come from the map builder |

## Rules that are easy to break

- Scale: one deck = 144px; she is 59px tall in an 84px cell, feet on the cell's bottom row. Every
  human-sized thing (doors, furniture, railings) is sized to her, never to the ship.
- No death: failures are "scares" (run off, long fall out of frame, life ring overboard). Never use
  the word death, in code or on screen.
- Nothing floats: every object rests on or hangs from something plausible.
- Sprites face east; west is `flipX`. Background props are muted so they never read as interactive.

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
