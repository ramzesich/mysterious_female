# Refinement log

The Refinement session's work (the user, 2026-11-20): a branch of its own, `refinement`, forked
from `main` at `0b49441`, in its own worktree (`../mysterious_female-refinement`, served on port
8001). Refinements of what is built, from later steps of `docs/plan-the-rest.md` or from nothing
planned. Each entry: what the user asked, what was made, what was checked. The shared documents
(`GAME_DESIGN.md`, `docs/plan-the-rest.md`, `docs/progress-decisions.md`, `CLAUDE.md`, `README.md`,
`docs/population.md`) are changed only on the user's word.

## The intro's end: she walks out of her door (2026-11-20, `b56f688`)

- **Asked:** out of her crew cabin's door she walks a few steps to the left, stops, straightens her
  badge; "E to interact" only the first time she walks past her door. Then: "walk, not run"; no
  stop facing us in the doorway, "just straight walking to left"; she stops where the notice board
  hung, the board moved left to where she had stopped; she comes out in front of the door's frame,
  not from behind it; at the end she faces left.
- **Her walk** (6 generations): two skeleton-v3 `walking-8-frames` clips of her character facing
  east, `walk-a` (the template's own) and `walk-b-calm` (stride 0.85, arm swing 0.6); the user
  chose B. In her sheet as `walk` (after her other clips, which kept their places); raw frames in
  `assets/source/her/walk-a/` and `walk-b-calm/`. Checked frame by frame: 57 to 59 px against her
  59, feet on the floor, the far arm's shade her own, A's head dipping 2 px once a cycle (B's bob
  even). Its pace from the planted foot (it rolls back about 4.4 px a frame): 10 frames a second,
  44 px/s; a foot comes down on frames 3 and 7.
- **Built** (`src/intro.js`, `WALK`): the parts `step` 0.4 s (the door opens) and `walk` (she walks
  72 px left, then stands a quarter of a second facing left); the camera eases along with her. The
  open door's leaf (columns 6 on of `door-crew-ajar`; 0 to 5 are the jamb and the light in the gap)
  is drawn over her in a copy cut to it while she is in the doorway; the door shuts at 0.65 s. Her
  footsteps on the clip's frames (`src/world/soundscape.js` keeps quiet while the intro runs). After
  the badge she turns to go on to the left. "E to interact": once, when she is 16 px past her
  door's middle going right in the corridor (`HINT_PAST`), a new game only.
- **Moved:** deck 3's notice board from 88.5 m to 87.98 m (`tools/build_ship_map.py`; the map
  regenerated, that prop the only change); her widest frame is 3 px clear of it.
- **Checked:** `intro` (rewritten for the door, the walk, the stop, the hint past the door and only
  once) and `deck3` pass; the rest not run. `tools/check_overlaps.py`: one overlap, not this
  change's (deck 7, 242 m, the diary of `0b49441` on a theatre seat).

## How to move and jump, once; the rule on hints (2026-11-20)

- **Asked:** "When we get the controls after she faces left, place a one time popup: '← and → to
  move, space to jump'. The popup has to show controller keys if controller is connected." Then,
  the rule: "no game progression hints, like 'go there', or 'jump down here'. But every new
  mechanic introduced, has to be explained once." Recorded in `CLAUDE.md` (it replaces "No hint
  popups ... not a licence for a second one").
- **Built:** `hint.move` and `hint.move.pad` in `src/lang.js` (English and Ukrainian: "← і → —
  рухатися, пробіл — стрибати", "Лівий стік — рухатися, A — стрибати"); shown over her once as the
  intro hands her over, a new game only, for 6 s. The controller's text while the controller is
  the device in use (`controls.device`, touched last: the browser lists a controller only once a
  button on it is pressed), switched over if she takes up the other while it shows. "E to
  interact" takes the bubble over if she passes her door while it is up.
- **Checked:** `intro` (the popup, the controller's text and back, both hints once each), `deck3`,
  `lang` pass; the rest not run.
- **Not changed, the user's to decide:** `GAME_DESIGN.md` §7.1 item 15 ("No hints ... not how a
  new verb is used") and §6.1.3's "New ways to move" row ("how a verb is used is hers to find
  out") now say the opposite of the rule. "E to interact" is in the keys' words with a controller
  too.

## Tuned in play (2026-11-20)

- **The popups shorter:** 6 s, then 4 s ("a bit earlier"), then 3 s ("even a bit earlier"):
  `HINT_MS` in `src/intro.js`, both hints.
- **She stops earlier:** 56 px out of her door instead of 72 (about three steps, 1.3 s); the
  notice board stays where it was moved, she stands between it and her door.
- **"E to interact" in time:** it waited for her 16 px past her door's middle, and running she
  was past the door by then ("with a slight delay"); now as she reaches it, her middle at its
  near edge (`HINT_AT`, -14 px).
- **Checked:** `intro` (the hint before she is at the door's middle) and `deck3` pass.

## The intro's sky: the sun, its light, the clouds (2026-11-20; plan-the-rest §7b, part 7, begun)

- **Asked:** the plan's part 7 ("more realistically-looking sun and reflections, more varied and
  volumetric clouds"). The user's answers: the sun a soft disc with a bloom and no rays, "but also
  with some god rays through the clouds"; on the water only a path of light under the sun; clouds
  all fair-weather heaps, lit tops and shaded bellies; pixel-art shapes, the bloom and the haze
  smooth; and it reaches the game's far background and the sunset too. Warned: §7b is the
  Implementation session's plan item, so the plan needs a note before it builds it (only with the
  user's word); it touches `src/intro.js`, `src/background.js`.
- **Chosen:** mock-up B (of A, B, and C on the palette), each built into the running intro (both
  languages, the welcome's blur); then "too heavy, remove the black underlines, the clouds have to
  be softer": B3, the clouds generated soft (no dark base). Their own colours, not the palette's.
  Then: the light reflected under the sun with a cloud between them "looks off": nothing under the
  sun now, a smaller cloud over its right side ("not on the bottom"), the light turned down a
  little (bloom 85 %, rays 0.7); the big cloud in the pan to the ship made smaller (a cloud of a
  size between, generated), and seven clouds of four sizes over the ship ("not big").
- **Built:** `tools/build_sky.py` (the clouds' layout in screen px from the sun, each cloud's edge
  toward the sun lit; the god rays worked out from the clouds: each casts a shadow lane away from
  the sun, the beams only where they break its light; the bloom; the far clouds' strip; light
  pictures fading to nothing at their borders, or the pan right showed their edge), to
  `assets/sprites/sky.png`/`.json` (atlas `skyart`: the key `sky` was taken), `sky-layout.json`,
  `sky-rays.png`, `sky-glow.png`, `sky-strip.png`; loaded in `BootScene`. `src/intro.js`: the old
  drawn sun, rays, clouds and two-frame glitter gone; the path of light (`pathGlints`, `drawPath`)
  glints on the far sea's rows, each flickering on its own clock and swaying with the ripples; the
  old blinking white squares on the water ("sparks") taken out. `src/background.js`: the far clouds
  are the generated strip (in play, from outside, the intro's far rows), nearly solid (their haze is
  in their colours), the drawn puffs (`cloudStrip`, `cloudTexture`) gone.
- **Art:** 12 PixelLab jobs (`create_image_pro`), 120 generations; every try and its job in
  `assets/source/sky/tries/` (its README).
- **Checked:** `intro` (its "nothing drifts" check reads the new clouds), `boot`, `lang`, `deck3`
  pass; the rest not run. The views shot exactly through the renderer: the welcome, `sky`, `down`,
  `sea`, the pan `right`, `ship`; play on deck 12 and the outside view (O). From outside the far
  clouds stand in a fairly even row, as the old ones did.
- **Still to do for §7b:** the sunset's sun and its path on the sea (a mock-up first); then the
  plan's note and `CLAUDE.md`'s table, on the user's word.

## The sunset's sky (2026-11-20; plan-the-rest §7b done)

- **Asked:** the rest of part 7, the sunset's sun and its path (the user's "how far it reaches": the
  game's background and the sunset too). Mock-ups in the game at the bow and the glide's start: S1
  the sky in bands as it was, S2 smooth; the user: S2, the rays "as shown"; the clouds "a bit
  smaller, they are too prominent now"; then "in some places they have either too prominent or too
  torn-away edges. Let's smooth them" (the sunset's, at the bow and at the glide's start).
- **Built:** `tools/build_sky.py` `DUSK_*`: eight clouds lit by the low sun round it (generated, in
  game px from the sun, fixed with it to the screen as it is), its sun (softer, warmer), its glow
  wide and low along the horizon, god rays up through the clouds' gaps worked out from them (none
  under the horizon), the far strip of small sunset clouds; every colour divided by the evening
  light as `dusk()` does; `smooth_edges`: loose bits under 8% of a cloud dropped, the outline
  rounded, the darker outer ring the generator drew given the inside's colour and made a little
  see-through. `src/background.js`: the sunset's sky blended (`bg-sky-dusk`), its sun, glow, rays and
  clouds placed from the sun wherever the sunset shows (in play, from outside, the windows' views:
  `objects`), the day's far clouds giving way to the sunset's as it comes on (`duskStrip`,
  `duskRows`), its path of light flickering glint by glint; `pathGlints` and `drawGlints` shared with
  the intro's path (moved there from `src/intro.js`).
- **Art:** 4 more jobs, 40 generations (160 for §7b); the tries and their jobs in
  `assets/source/sky/tries/README.md`.
- **Checked:** `finale`, `intro`, `boot`, `lang`, `deck3` pass; the rest not run. Shot exactly: the
  bow, the glide's start, the sun deck, the outside view (the sun behind the bow there, as before),
  cabin 8206's window; the path recorded.
- **Documents, on the user's word ("Yes", 2026-11-20):** `docs/plan-the-rest.md` §7b and its row in
  the parts' table say this session built it and the building session skips it; `CLAUDE.md`'s table
  has `tools/build_sky.py`, and its `src/intro.js` and `src/background.js` rows say what the sky is
  now. On this branch only until it is merged.

## Merged to main (2026-11-20)

- **Asked:** "let's update our branch from the latest main, and merge everything back there, so that
  other sessions see it" (the Implementation session's round merged and pushed first, `c4a8098`).
- **Done:** `main` merged into `refinement` (`e33b18c`): one conflict, `maps/ship.json`, generated:
  rebuilt with `tools/build_ship_map.py` from the merged tools, not merged by hand; it differs from
  `main`'s only by deck 3's notice board (4728 to 4703), `maps/world.json` the same as `main`'s. Then
  `main` fast-forwarded to `refinement`.
- **Checked:** `intro`, `boot`, `lang`, `deck3`, `finale` pass; `tools/check_overlaps.py`: 0 overlaps
  (the deck 7 diary's is mended on `main`); her walk out of her door shot again after `main`'s
  "her picture a pixel lower": as before. The rest not run.

## Every popup's look (2026-11-20)

- **Asked:** "we're refining the looks of every popup in the game"; the user's answers: 1 to 5 of the
  list (the word over her, her cry, the people's pictogram bubbles, the little signs, the sound sign;
  not the full-screen panels, which are the Implementation session's plan, §2.3 and §2.4), a pixel
  font with an open licence, a look for each kind, generated icons; "a nice framing, and differentiate
  between [speech] bubbles and thought clouds". On the mock-up: "The tip should always come from the
  relevant person's head (not connected to it, but come from the direction of the middle of the
  head)", no tail on her cry, more padding; "The placement of the tails must work in all of the cases
  in the game". A knock needs no bubble (left as it was). Approved.
- **Built:** `src/popup.js` (new): four kinds, speech (her words, Bumbot's "Meow!"), thought (a lock
  with its padlock and card, her hands too full for a ladder, the melted or cold thing she carried,
  the people's wishes), shout (her cry, no tail, over her head), plate (the hints). Each frame sized to
  its words by a band whose edges match (a cloud's bump, a burst's spike), repeated or taken out once;
  the tail drawn from the bubble toward the middle of the head, stopping 3 px over it or over what is
  on it (the inside-out parasol, 22); a thought's two circles on the same line; clear of the view's
  edges and of each other (hers first); still through a stride's bob, following a jump at once;
  Bumbot's "Meow!" set out to his side so its tail misses her face. It keeps the API of the text it
  replaced (`setText`, `setVisible`, `text`, `visible`), so the game's calls stand; the people's
  `bubbleItems` are stand-ins taking the old calls (shown, its picture changed, a hop). In the shared
  files only the lines that make the popups changed: `ShipScene.js` (`buildHud`, `showLocked` passes
  the card, the "Meow!" its speaker), `world.js` (`say` passes its options), `people.js` (the bubble's
  block), `intro.js` (the hints are plates), `BootScene.js` (three loads).
- **Art (`tools/build_popups.py`, new):** generated frames (the user's picks of 16 each: speech 9,
  thought 10, shout 2 as 15 had a tail, plate 1), 20 icons and key caps (one sheet of 64), the
  cards cut from their close-ups; the lettering Galmuri9 (SIL OFL 1.1, a subset) at its own pixel size,
  a bold for the cry; `assets/source/popups/README.md` has the jobs. 60 generations.
- **Heads (`tools/build_heads.py`, new):** where the head is in every frame of every picture a popup
  can speak from (`assets/sprites/heads.json`): her sheets, her gags and the towels', and the people
  with a wish by PixelLab's skeleton estimate (about 900 frames, about 100 generations; kept in
  `assets/source/popups/heads/estimates.json`); her upright frames by rule (within 2 px of the
  estimate); the other people by rule; Bumbot in her arms by rule and two by hand. Checked on contact
  sheets: frames of the door alone dropped, four of her clinging in the gust set by hand.
- **Checked:** shot in the game: her standing, running, in the air, crawling in the duct, on stairs,
  on the funnel ladder, swimming, a lock, a ladder with her hands full, "Meow!" with Bumbot, in her
  towel turban, the cart, papers, trays and ball gags, the parasol (22), a gull in the air, the
  steward, the kid, the old lady, the engineer, the planner, the hints in both languages. `boot`,
  `lang`, `deck3`, `stairs`, `trunk`, `mishaps`, `region6` to `region9`, `finale` pass but
  `mishaps.things`: the sprinkler (16) misses her when run with others, as on `main` (not this
  change; the Implementation session's). The rest not run.
- **Open:** the court's ball (15): she lies under a standing player and her tail passes him (asked;
  left as it is). `CLAUDE.md`'s table has no row for the new tools until the user's word.

## Merged to main again (2026-11-20)

- **Asked:** "update from the main branch, but carefully ... Reload the documents from there. Then,
  update the documents, commit, merge your changes back to main, push everything."
- **Done:** the heads kept by clip, not by frame number (`1bd38be`): `main`'s new clip of hers
  (`airtoss`) went in before `walk` and moved its frames; the people's still poses added. `main`
  (the bell gull, her throw in the air) merged in without conflicts; her `airtoss` clip and the
  steward's still poses estimated (11 frames, about 1 generation), `heads.json` rebuilt.
- **Documents, on the user's word:** `CLAUDE.md`: a row for `src/popup.js`, `tools/build_popups.py`,
  `tools/build_heads.py`; a rule (words over a head are popups; run `build_heads.py` after rebuilding
  a sheet of hers or the people's); the lessons. `docs/plan-the-rest.md` "Start here": the popups built
  outside the plan, what a new popup goes through, what was not touched.
- **A slip, mended:** `git checkout origin/main -- .` (meant only to read the documents) overwrote the
  merge in progress; `git merge --abort` and the merge again, every popup edit checked present after.

## The background props' wash, deck by deck (2026-11-20)

- **Asked:** "a visual audit of the background props. At some places they are too much washed out ...
  even out the level of washing out. Take the gym props and the theater chairs as example."
- **First try, reverted:** every `-bg` prop, the rooms and the lifeboats at 12% at once ("Too many changes
  that I don't agree with. Let's revert to the original and maybe go deck by deck, in steps"). Nothing of it
  was kept.
- **Deck by deck:** each place shot in the game at 35% (the old level), 20% and 12% (the gym's), the user
  choosing: decks 3 to 7, 10 to 12 at 20%; the Library, Magnum's (dark wood) and the Sports Bar (dark green)
  at 12%; decks 8 and 9 as they were but their balconies (20%, deck 10's too); **the guest cabin corridors
  (beige walls) as they were on every deck** ("Those guest cabin corridors remain as they were before this
  entire update"). Doors she cannot use, railings, the rooms, the lifeboats untouched.
- **Built:** `tools/wash_levels.py` (the table; `frame()` picks `-bg`, `-w20` or `-lt` by deck and metre);
  `tools/build_ship_art.py` makes `-w20` (20%) and `-lt` (12%) for every piece but doors and railings (every
  old frame unchanged; the atlas 512 x 3945); `put()` in `tools/build_ship_map.py` and a last pass in
  `tools/build_world.py` (the balconies' furniture, the pieces drawn again in front of people) take the
  place's twin. The guest cabin corridors' props are laid by the ship scene itself, still `-bg`.
- **The Library's chairs:** one red reading chair is hers, in full colours, beside two washed ones; the user:
  all five reading chairs in full colours and each one to sit in and read. Written into
  `docs/plan-the-rest.md` §2.3b for the Implementation session (the user's word), not built here.
- **A slip, mended:** the first deck 8 balconies shown were deck 9's (`?at=balcony` is deck 9's); deck 8's
  shown and confirmed after.
- **Checked:** the built game shot at nine spots against the old shots; `boot`, `deck3`, `region2`,
  `region3`, `region6`, `region7`, `region8` pass, no errors; `check_overlaps`: 0 overlaps. The rest not run.
- **On the user's word ("1. Ok 2. Ok"):** a rule in `CLAUDE.md` (a new background prop is placed with `-bg`,
  its place's twin picked by `tools/wash_levels.py`); merged to `main` (a fast-forward: `main` had not moved)
  and pushed.

## The intro: deck 3's side opens later (2026-11-21)

- **First:** `refinement` brought up to `main` (`f7134c6`, a fast-forward: the HUD, the sardines), the user's word.
- **Asked:** the side opening on deck 3's corridor "happens a bit early now. Let's open the corridor a bit later",
  GIFs of the sequence from where the whole ship starts closing in.
- **Shown:** four timings recorded on the stepped clock (the opening's range set in the page only): A as it was
  (zoom 0.7 to 1.7, 3.6 to 4.3 s of the 5.6 s dive), B (1.2 to 1.9), C (1.6 to 1.99, about 4.5 to 5.1 s), D (after
  the camera has stopped). **The user chose C.**
- **Built:** one line in `src/intro.js`; the `intro` playtest's halfway check moved to the dive's 0.86. The built
  game recorded and compared frame by frame with C: the same. `intro`, `deck3`, `boot` pass; the rest not run.

## The signs, drawn at their size (2026-11-21)

- **Asked:** "a similar work as we done to the tooltips, but now it concerns signs ... Show me every plain white
  sign": 13 white (crew door plates, two notes) and 34 cream (30 rope barrier cards, 4 posters), every one a
  Verdana text box.
- **First round, rejected:** 16 generated blank signs (create_1_direction_object, 10 generations), my picks mocked
  up at the game's size with Galmuri7: "all bad, oversized and do not fit their places". The lesson: fit the
  lettering to the sign's place, not the sign to a font. The tries were deleted (the user's word).
- **Second round:** each sign kept to its place and about its old size; a 5 px pixel font drawn by hand, plates drawn
  at size (a 1 px rim, a face, a lit edge or a band); three looks a kind, the old sign beside them in the same shot.
  The user's numbers: brushed steel door plates, navy where the wall is dark (STAGE DOOR, LIGHTING, the PANTRY on
  dark wood); navy and gold rope cards; the yellow notice (SEARCH IN PROGRESS); blue plaques (JOGGING TRACK), words
  painted on the wall (WALKERS), a white notice with a red band (BOAT DRILL), a cream card (JUST MARRIED). Set in
  capitals. BOAT DRILL and JUST MARRIED 2 px higher; JUST MARRIED moved beside its door to clear the bride's wish
  cloud, then put back over it ("where it was on your first preview"): the cloud is drawn over it.
- **Built:** `src/signs.js` (new: the font, the looks, `sign()`, each sign one canvas texture `sign:<look>:<text>`,
  no asset files); one call each in `world.js` (door plates, wall signs; the brass name plates stay text),
  `ShipScene.js` (LINEN), `progression.js` (rope cards); `plate_style` and the signs' looks in `tools/population.py`,
  passed on by `tools/build_world.py`; `tools/check_overlaps.py` counts a sign picture as text (`signText`).
- **Checked:** the game shot at every kind (47 signs, no page errors); `check_overlaps` 0; `boot`, `deck3`,
  `region2`, `region4`, `region9` pass; the rest not run.
- **On the user's word ("Add them"):** a row for `src/signs.js` in `CLAUDE.md`'s table and the rule (a sign is `sign()` with a look,
  never a text box), `f27383c`.

## The menu's font (2026-11-21, approved)

- **Asked:** the welcome screen's lettering changed, in both languages; candidates first.
- **Shown:** five open pixel fonts with their own Cyrillic, each set in the menu's look over a real shot of the
  screen, English beside Ukrainian (Press Start 2P twice, Galmuri11, Fusion Pixel 12, Handjet); left out: Rubik
  Pixels (breaks up), Pixelify Sans and Pixel Code (not on a pixel grid), the thin ones. **Chosen: 1**, Press Start
  2P, the name at twice the font's pixels, the plates' words at its own.
- **Built:** `assets/source/menu/PressStart2P-Regular.ttf` (SIL OFL, `OFL.txt` beside it); `tools/build_menu.py` sets
  every Latin and Ukrainian capital (Ґ Є Ї Й too), digits and signs from it at 16 (`T`) and 8 (`S`), each frame trimmed
  with its place in the font's cell kept as the trim; `src/pixeltext.js` steps by the cell and lays the bands over the
  capitals' rows (H's frame). The two generated letterings (`font-title.png`, `font-sign.png`) stay in the folder,
  unused. No generations.
- **Checked:** the game's menu against the approved mock-up enlarged (the same); `boot`, `intro`, `lang` pass; the rest
  not run.

## The menu 60 px higher (2026-11-21, approved)

- **Asked:** the whole menu a little higher; candidates first.
- **Shown:** the game's own screen with the menu 24, 42 (centred), 60 and 80 px higher. **Chosen: 3**, 60 px.
- **Built:** `MENU` in `src/intro.js`, the name at 118 and the first plate at 276 (from 178 and 336); the second
  plate, the tangerine and the name's drift as it melts follow from them.
- **Checked:** shot in both languages, the same as the candidate; `boot`, `intro`, `lang` pass; the rest not run.
- **Documents, on the user's word ("Update all relevant documents"):** `CLAUDE.md`'s row for `src/pixeltext.js` (the
  font, its own Ukrainian capitals, the trimmed frames, where `MENU` is) and `GAME_DESIGN.md`'s welcome screen (the
  font and the place, Decided). `docs/progress-decisions.md` keeps its account of the old lettering as history.

## `docs/intro.md` brought up to date (2026-11-21, the user's word)

The user asked for their own document to be updated to the game as it is ("Update docs/intro.md to match the
current state of the game"). Their structure and wording kept; what changed: the menu's lettering, plates, place
and keys; the sky's soft sun, clouds and sunbeams, the path of light, nothing drifting; deck 3's side opening late
in the zoom; the cabin close-up at the mirror (dropped on 2026-11-14) replaced by her walk out of the door, the
badge and the turn; the HUD empty at first; the two hint popups; a game under way and Esc. The rule that
`docs/intro.md` is the user's own stays: edited only on their word.

## Her hair at the crew cabin's mirror on E (2026-11-23, approved)

The user: "Make the mirror animation play by pressing E, instead of by standing by it." Her hair (`her-hair`)
no longer plays by itself when she stands at the mirror turned to it; E within 14 px of the spot where she stops
(`MIRROR_REACH`) turns her to it and plays it once, each press once more; not while she carries a thing or holds
Bumbot. `tryMirror` in the ship scene, in the E chain after the shower and before the route's doors; the old
count in `standStill` (`mirrorLooks`) is gone. The `intro` playtest's mirror checks rewritten (standing does
nothing, E once a press, E away from it nothing); `intro` and `deck3` passed. GAME_DESIGN.md's line on the mirror
(§7.1 item 11) updated to match, on the user's word.

## What she can use pulses where E would act (2026-11-23, approved; plan-the-rest §7c, part 8)

The user looked at every interactable (213 of them, sheets of each kind) and chose a mechanic over a colour rule:
while she stands where E would act on a thing, the thing's colours pulse between its own state and the other, and
settle back when she leaves (1.6 s a pulse, 0.27 s back). Mocked up as GIFs of every kind first, then built.

- **Full-colour things** (doors, lifts, trunk doors, pickups, books, key cards, the reading chairs, carts, room
  fixtures) pulse down to the wash of the props round them (the nearest washed map piece's level, else the place's
  from the map's `washLevels`) and back. **Muted map pieces** (the soft serve machine, the pool bar, the jackpot
  pair, the captain's door, the ice swan, the massage tables, the piano, the slide, the hot tub, the coffee and
  lunch stations, the odd book's bookcase) show their full twin, the wash pulsing off it.
- **Never:** people and Bumbot ("People shall not change tones at all"), the arrows over a trunk's door, the
  MONEY JACKPOT sign; a pickup's glint stays as it was.
- **The casino's slot machines are washed 12%, not 20%** ("too washed out"): `PIECES` in `tools/wash_levels.py`.
- **Her crew cabin's door pulses to 40%** from both sides (white on deck 3, it hardly changed at 20%: "40%, but
  only for this door here"); her mirror and cabin 8206's shower door to 40%, other room things to the room's 30%.
- **Things drawn into a room's picture** (the mirror, the shower door, the chute, a room's own door seen from
  inside, cabin 8206's desk) pulse by their own pixels only: the box's wall flooded out from its edge (the user saw
  the mirror's box pulse as a frame), or by the shapes it is drawn with (the desk: its top and body only, the bin in
  it cut out, not the TV or the shelf column: the user circled it). Washed ones are worked back to full colour.
- **Only where E would act**, asked as the ship scene's E chain asks it (the pool bar before region 8: nothing).

`src/highlight.js` (new), two lines in `src/scenes/ShipScene.js`, the map's `washLevels` (`tools/wash_levels.py`'s
`table()`, written by `tools/build_ship_map.py`), `maps/ship.json` rebuilt, the `highlight` playtest. Runs: highlight,
boot, deck3, intro, region4, region6, region9, cabin, linen, lift, trunk, mishaps passed; check_overlaps 0. `region5`
("two tangerines in the welcome basket") fails with and without this change: from main. Not done: the nook's armchair
and the funnel horn (drawn inside larger pictures). A slip: some runs wrote into the shared `bumbusik-playtest`
temp folder (TEMP set from TMP before it changed); the shared `last.json`'s failed list was overwritten and only
my entry taken back out.

## Doors are secrets too (2026-11-23, approved)

The user: "make all doors look like their background neighboring doors. Or, like other background things around
them, if there are no doors. Meaning, they will work like secrets". Every door she can use (208, in 48 kinds, looked
at in sheets) is washed at rest by `restDoors` in `src/highlight.js`: as the background doors beside it (the guest
cabins' 35%), else as the props round it (20% or 12%), inside a room as the room (30% toward its wall); the pulse takes
the wash off, up to full colour, and back. A wash copy follows its door (opened, slid, cut to its leaf as she steps
out of her cabin in the intro: `sameCut`).

The user's answers, one by one: the lifeboat's roof hatch excluded ("already implemented properly"); **every lift
stays as it is**; a trunk's door with nothing round it 20%; **all the glass doors across the deck stay as they are**
(72, the one-way ones too), and deck 11's lone steel one; the balcony doors left as they are ("they don't look like
doors at all": to be worked on next); cabin 8206's shower door stays full. Her crew cabin's door is now washed 35% like
the crew door beside it (its 40% pulse down is gone). `tools/check_overlaps.py` skips the wash copies (`hlCopy`).
Runs: highlight, boot, deck3, intro, region4, region6-9, cabin, linen, trunk, lift, stairs, atrium, promenade, balcony,
bridge passed; check_overlaps 0; region5 fails as on main.

## Merged with main and the docs written (2026-11-23, the user's word)

`main` (the Implementation session's table scene and Great Outdoors, `82521bd`) merged into `refinement` (`529475d`;
`maps/ship.json` rebuilt, not merged by hand). The `highlight` playtest's book moved from book 1 to book 6 (book 1 now
comes from her husband's hand). On the user's word ("Yes, update both"): `docs/plan-the-rest.md` §7c marked built by
this session, `CLAUDE.md` a row for `src/highlight.js`, the door rule rewritten (doors washed at rest, the pulse reveals
them; it replaces 2026-11-15's full-colour doors), the casino's slots in the wash rule. Runs after the merge: highlight,
boot, deck3, intro, region4, region6, region9, cabin, linen, trunk, lift, stairs, promenade, balcony, lang passed;
check_overlaps 0; region5's basket check fails as on main.
