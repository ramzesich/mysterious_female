# Near-catch 1 remade: log (2026-11-24)

Deck 5 aft, the Seven Seas' pass (`bb1`): Bumbot at the officer's lunch, her cry, his way out, the fruit bowl, the
lunge learned. Remade by the plan in `docs/sequence-remake-plan.md`, on the branch `near-catch-1`, in a worktree of
its own (`../mysterious_female-catch1`, server on port 8003), from `three-uses` at `7f25912` (`main` at `e2d5b1e` and
the plan's document).

## 1. What was asked

> Let's fix the first Bumbot near-catch sequence in the game. Right now it is very much broken, both visually and in
> terms of gameplay: there are delays and glitches.
> Apply the plan and let's go

## 2. What was found, recording the scene as it was

Recorded with real keys from `?play&at=pass5`, a frame every tenth of a second, walking in and arriving in a jump.
She can only come from forward (the deck's end wall is right behind the galley's door).

**How it looks:**

1. **He eats nothing.** He stands on a low cabinet of stacked plates (the background's `service-station`, 28 x 24 px),
   his head hanging past its edge; no lunch is drawn.
2. **She bends to the floor beside the cabinet** (her `reach`); he is on top of it, at her waist. Her hands never go
   toward him.
3. **The cry comes late and covers him.** She walks up, stands, bends, and only then the shout's popup shows, over him
   and the GALLEY plate, for 1.7 s; he leaps up into it.
4. **His leap goes through her.** Straight up 35 px on the spot; then he is on the floor 30 px forward, drawn across
   her back, and runs on.
5. **The bowl falls by itself.** It stands on a dining table 86 px from him and goes over the moment his leap
   starts; it turns as one stiff picture and stays tilted in the air against the chair's back, its fruit in it.
6. **He runs through the furniture:** along the floor, drawn in front of the tables and chairs. (The design has him
   bolt along the counter.)
7. **Things pop in at the end:** the three tangerines in a neat row on the floor 2 m from the bowl, and the lunch's
   tray and cloche on the cabinet, both when the flag is set, 6 s after the bowl fell.

**How it plays:**

8. **She is held 8.3 s.** Her own part ends after 2.9 s; she then stands on her shrug's last frame for 5.4 s, until he
   has run 2,200 px to 203 m, long out of sight.
9. **A hitch going in:** from 60 px out she is slowed to a walk for 26 px.
10. **She can jump over him.** In the air the scene does not start; landing aft of him it does, with her hung 4 px
    over the floor through all of it, bending at the galley's wall.
11. **Nothing says what she has learned.** The lunge is hers from this moment (D now carries her forward); no popup
    says so, though every new mechanic is to be explained once (the user, 2026-11-20).

**What hangs on the scene:** the flag `bb1` (set when he is away) gives the verb `dash`, makes `src_lunch` a source,
shows the bowl's three tangerines (`tan_5_bowl`), and arms the glimpse on the forward stairs. Tests: `region1`,
`golden`, `throw` (a tangerine thrown at him is batted back and he stays), and the scenarios that set the flag by
hand. His cry-answer (`heard`: he looks up) and the trays he knocked down in the restaurant are not this scene's.

## 3. Decisions

The user's, on the findings and a rough of the pass drawn in the running game (2026-11-24):

1. **One serving counter** in place of the small cabinet and the last dining table (the one the bowl stood on):
   "Yes, as you sketched". 136 px long, its top 33 px over the floor (0.9 m next to her 59 px), by the galley's door;
   on it, from forward to aft, the fruit bowl, Bumbot at a plate of the lunch, a fresh lunch under its cloche. The
   GALLEY plate 10 px higher, clear of the cloche.
2. **She cries and dashes at him:** "She has to learn the dash here, so I suggest she cries and dashes at him". No walk
   up, no bend: at the sight of him the cry and the dash at once, as D does in play (its trail, its sound).
3. **The hint:** "D to dash" (both languages, and the controller's button, as appropriate): one plate over her as she
   is free again.

Mine:

4. **He leaves forward** (the glimpse on the forward stairs needs it), along the counter's top behind her dash, into
   the bowl, down off the counter's end and off the screen.
5. **She is free when her own part ends** (about 2.5 s), not when he has reached 203 m.
6. **The bowl falls because he hits it**, off the counter's end, in a clip of its own; three real tangerines come out
   of it and roll forward; the rest of its fruit lies spilled (no oranges among it: only hers to take are orange).
7. **Nothing pops in:** the fresh lunch stands on the counter from the start; E takes it once he is gone.
8. **He cannot be jumped past:** the scene starts from 200 px out, once she is on the floor.

9. **Counter B, the walnut one, and the sequence as its storyboard has it** (the user, on the storyboard over the real
   room: "Build like it is here, I like it"). The counter keeps its own colours as approved: it is not washed 20% as
   the Seven Seas' other furniture is.
10. **No stop at the cry:** the scene is the game pressing D for her: the popup, the dash's sound and trail and her
    run at twice her speed begin in the same frame. From nearer than a dash worth seeing (she landed from a jump close
    to him) the cry comes first and the dash a moment later, so that he is off before she is in front of him.
11. **His part is timed from her arrival:** a look back over his shoulder (his `look-back`, made in part 6 and not
    placed till now), a turn (`turn`), and off 0.1 s before she is there; he passes behind her on the counter's top.
12. **The bowl:** his nose meets it, the game's own bowl is pushed 12 px along the top for 66 ms, then its clip takes
    over (8 frames at 12 a second, the crash on the frame it lands in); its last frame is what lies there for good.
13. **His leap off the counter's end** from the leap's second frame (its first is him reared straight up), over the
    falling bowl, 0.34 s, then his run off the screen.
14. **The tangerines are the game's own three** (`tan_5_bowl_1` to `_3`, each with the place it comes to rest at in the
    data): out of the bowl's mouth as its clip starts, through the air, one small bounce, a roll to rest forward of
    the spilled fruit. They were three in a touching row 2 m off, appearing with the flag.
15. **She turns after him as the bowl goes, to us 0.8 s after she arrived, shrugs** (her `shrug`, the user's of
    2026-11-24), and is free 0.25 s after it, facing the way he went. Held 2.3 s; it was 8.3.
16. **"D to dash"** (`hint.dash`; "B to dash" with the controller, `hint.dash.pad`; in Ukrainian "D — ривок",
    "B — ривок"): a plate over her for 3 s as she is free.
17. **The lunch** (`src_lunch`) stands at the counter's aft end from the start, `when` the flag: there to see, hers
    after. The plate he ate from stays.
18. **The GALLEY plate 10 px higher** (`plate_lift` on the room): the cloche stood under it.

## 4. How it is built

- **Art:** `tools/build_pass.py` from `assets/source/pass/gen/` (its README has the jobs) into `assets/ship/pass/`:
  `counter.png`, `bowl-fall.png` (8 frames of 96 x 64), `plate.png`, `pass.json`.
- **Data:** `tools/population.py`: `BEATS["bb1"]` (his spot on the counter), `BEAT_LIFT` 33, `prop_bowl_7s`,
  `src_lunch`, `tan_5_bowl_1` to `_3`, the galley's `plate_lift`. `tools/build_ship_map.py`: no table under the
  Seven Seas' last window, the cabinet of plates gone.
- **The game:** `src/world/pass.js` (`setupPass`, `updatePass`, `passBeat`, `passAfter`), mixed into the Story; one
  clock, everything a function of it, on the ship scene's scripted update. `PASS` in `src/config.js`. The beat is
  `custom`: the ship scene's `nearCatch` no longer plays it. `world.topple` is gone with the old scene.
- **Beside it:** the galley's door takes its place's wash where nothing washed stands near it (`placed` in
  `src/highlight.js`: the cabinet it took its tone from is gone); his bites sound on his eating clip only (they
  played on the first frame of every clip of his at that spot).

## 5. What changes for the player besides the scene

- **A tangerine thrown at him there** is still batted back, but only a lob from just outside his sight (about 215 px):
  nearer, the scene begins. He is 33 px up now, so a roll along the floor passes under him.
- **The last dining table of the Seven Seas is gone** (the counter stands under its window).

## 6. Checked

- **Recorded with real keys and looked at, at the game's pixel size:** walking in (46 frames at a tenth of a
  second), arriving in a jump (the scene begins as she lands, she on the floor through it), a reload after, the deck
  above and the deck below with her there (nothing of the pass shows), the outside view.
- **Against the nine kinds of correction:** the counter 33 px beside her 59; feet, fruit and bowl on the floor's
  line; he behind her on the counter, the plate in front of his nose; nothing shown that is not there; he in sight
  all the way but for a tenth of a second behind her; her wall at the deck's end tried in a jump; no stand-in clip;
  no pause between the cry and the dash; nothing of it from other decks.
- **`python tools/playtest.py -j 6 boot region1 golden throw lang highlight sound region2 mishaps`:** pass, but
  `mishaps.things`' deck 9 sprinkler (it fails on `main` too) and, six at a time, `sound`'s footsteps once (it
  passes run by itself). `region1.pass` is new: 27 checks of the scene step by step. `highlight` failed first on the
  galley's door (no tone to take): mended as above.
- **`python tools/check_overlaps.py`:** 0 overlaps.
- **Not judged by me:** how it feels in motion (her stop at the dash's end above all), and how it sounds (no new
  effect: `cry`, `lunge`, `lungeEnd`, `mrrp`, `scramble`, `plop`, `crash`, `roll`).

## 7. Generations (PixelLab job ids)

| What | Job | Generations |
|---|---|---|
| The counter redrawn from the flat rough in the room's own picture (160 x 64), A mahogany | `7b19f09a-65ef-4252-933c-b984e689fbf0` | 6 |
| The same, B walnut | `6ee8698c-f9a8-48a0-ad1f-c91a190b8281` | 6 |
| The bowl fallen, its fruit spilled (an edit of the start picture, 96 x 64), try A | `da0a9c8e-c2fb-432b-aefb-dbd618706d33` | 5 |
| The same, try B (used as the fall's end) | `8a44a657-19e9-486a-a80b-40db5bae2944` | 5 |
| The bowl's fall, PixMiniMax from the start to that end, 12 frames, seed 5 (used: frames 0, 3 to 9, 12) | `c58229c5-2780-4001-ad18-442d374effb3` | 2 |
| The same, seed 21 | `77b23cdc-b30c-4ccd-b997-47f3589dbad8` | 2 |
| The lunch's plate (24 x 16) | `370b5991-6836-4e51-b865-2edcfabc2a14` | 5 |

31 in all. The balance after: 2,567.
