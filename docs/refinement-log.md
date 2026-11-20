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
