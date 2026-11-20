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
