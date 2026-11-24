# The pool's scene remade: log (2026-11-24)

Deck 11's first pool, near-catch 5 (`bb5`): Bumbot at the rim, the kid in the hot tub, the drain's lever, the pool
draining, the hatch in its floor, the drop into deck 10's hallway. Remade by the design session on the user's word, by
the rules of the shaft's remake (`docs/shaft-remake-log.md`): autonomously, with generated art, checked by itself,
everything decided written here. On the branch `pool-scene`, in a worktree of its own
(`../mysterious_female-pool`, server on port 8002), from `main` at `f186d6d`.

## 1. What was asked

> I want you to refine the pool animation from start to finish (Bumbot, kid, the lever, the pool drain). Use the same
> rules as you used yesterday for the linen room refinement. I want it make sense visually, in terms of placement,
> layering, everything. What can be generated with PixelLab—generate it. Just for example, the lever looks very poor
> now. The opening on the pool floor I couldn't find at all. If you're unsure about anything—give me context (also,
> visually if relevant), and ask. Make sure we don't interfere with our work of the Implementation branch, so maybe
> let's work in a separate throwaway worktree.

And, on the first previews:

> 1. Can we repaint the kids gun to be light green with blue lines? Now it's hard to distinguish it from his ice cream
> 2. The lever is way too big. It should be at least half a height.

And on playing it ("Much better than how it was"), seven fixes, decisions 18 to 24:

> 1. Let's make the laundry line (with the laundry) not visible when we're on deck 11.
> 2. Both the hatch and the drain should be much less visible when in the water.
> 3. Shift the hatch 3 pixels down.
> 4. Shift the drain 2 pixels down.
> 5. When the pool is drained, shift the player's ground level 3 pixels down. Now she looks floating in the air.
> 6. Shift the pool ladder down 3 pixels as well (both pools, always).
> 7. When Bumbot is sprayed and jumps into the pool, he is not visible when he is in. Make him visible in the water
>    (same color effect applied as to the player)

`docs/plan-the-rest.md` had the scene waiting for the user as U17 ("it plays and looks very broken"); what U17 says
must be kept is kept (section 4).

## 2. What was found, recording the scene as it was

- **The lever** was a box of 16 x 26 px drawn in code.
- **The hatch** was a lid of 28 x 5 px on the tank's floor line, seen edge-on, at the middle of the pool: 22 px off
  the screen from where the water left her, and not to be told from the floor when on it.
- **Bumbot** went up the pool ladder on his running clip, stood on the lever's knob (a 4 px point), and the lever's
  picture was swapped under him as he left.
- **The kid** was drawn behind the hot tub, not in it, and vanished from it on the screen when the flag came.
- **The water** sank as a flat rectangle with a few white dots over the hatch: the water went where she was to go.
- **The pool ladder** ended at the water: in the dry tank only its hoops were left.
- **The drop** into deck 10 was a fade, and nothing in the hallway's ceiling.
- From the deck, the kid's jet crossed her on its way to Bumbot.

## 3. Decisions

1. **A worktree of its own**, `../mysterious_female-pool`, branch `pool-scene`; tests with their own `TMP`; nothing
   in the shared folder touched (it had the Implementation session's uncommitted work on the shaft).
2. **Bumbot plays it with the clips he has** (`bat`, `sit`, `jump`, `run`, `shake`), placed by rule; none made new.
   Part 6 of the plan makes all his clips again, and the scene takes the new ones as they come. His leaps are
   placed by his paws: his jump's frames carry a rise of their own, measured frame by frame and taken out, so that a
   leap's arc is the scene's.
3. **The scene, from the water** (the way she comes: the pool fills the deck from side to side):
   she glides to the rim under him, nose to nose, and cries; the kid stands up in the hot tub behind him and squirts
   him in the back; out over her head he goes and into the water behind her; he paddles back past her to the rim
   (his running clip with his legs under the surface: his head and back over it, his legs through the water's
   blue), hops out, shakes himself dry; then away aft by the nearest high thing: up onto the lever's grip, which
   goes over under him toward the hot tub and throws him across it, the kid ducking; he lands past the tub and runs
   off along the second pool's far side. The lever thrown, the pool drains.
4. **The lever is thrown by what he does, where it can be seen:** he lands on its grip and it goes over under him.
   Before, he stood on its top and its picture changed as he left.
5. **From the deck between the pools** (GAME_DESIGN's "she lunges, he leaps, she topples into the pool"): she dives
   at him flat (her `tripfall`), he hops over her dive and comes down where he sat, and she is in the pool; she
   comes up under him, and the scene goes on as from the water. So the kid's jet never crosses her. (Standing on
   the rim's edge already, west of him: a grab at the air, a step back, and off it.)
6. **The kid is in the hot tub:** in front of its far rim and its water, behind its near wall (the tub's own
   picture drawn again from its near rim down, only while he is in it). Right down he is out of sight; his cap
   shows over the near rim when he peeks; he stands up to squirt. At the scene's end he is right down again, so
   that his leaving for the aft pool deck is not seen. (He was behind the tub.)
7. **The hot tub 22 px further aft** (132.5 to 132.96 m; `LIDO` in `tools/population.py`, the map's `at11`), for the
   first, tall lever's throw. Left there with the small lever: more room at the rim for Bumbot and it.
8. **The drain's lever is a valve on a stand, generated** (`assets/source/pool/`, `tools/build_pool.py`): a stubby
   steel pedestal bolted to the deck, a hazard stripe, a cap, a lever with a red grip; armed it leans toward the
   pool, thrown it lies toward the hot tub; seven frames (the swing, its rest, its bounce). **Knee-high** (the user:
   the first, 46 px to its grip, was "way too big. It should be at least half a height"): its stand 15 px, its
   grip 20 px over the deck.
9. **One stand in every frame; the arm drawn by rule.** The generator drew the thrown state on another stand, and a
   generated arm turned pixel by pixel came out ragged where it rests; at knee height its own arm is a hair. So:
   the generated stand, and an arm drawn at each frame's angle in the picture's own tones (a steel bar outlined each
   side so that it reads against the pale sky, a red grip a px wider).
10. **The water goes down a drain, not down the hatch:** a generated grate in the tank's floor at its aft end, by the
    lever. A funnel is drawn down into the surface over it with a whirl in it, bubbles come up, the surface sinks
    slowly at first and then steadily (5 s as before), the tank's wall is wet above it with drops running down, and
    puddles lie on the floor after and go one by one (the wet patch's look: on the floor's face, a glint).
11. **The hatch is on the floor, seen a little from above, and in view** (the user: "The opening on the pool floor I
    couldn't find at all"). The tank's floor is already drawn so, a strip of pale tiles under its wall; the hatch
    lies on that strip, 46 px wide: a steel plate with a ring, hinges and a hazard border. It is there from the
    start and shows through the water. Moved from the pool's middle (125 m) to 128.5 m, 120 px from the aft rim: on
    the screen as the water leaves her there, and clear of the tray on deck 10's floor under it (51 px forward of
    it; at the aft end she would have come down on it).
12. **Opening it is seen:** E, she steps beside it, bends to its ring (her `reach`), and the lid stands up against
    the tank's wall behind where she will go down; a dark opening, a ladder's top in it. The lid's picture was cut 6
    rows shorter in its plain middle, so that it tops out at the tank's rim.
13. **Going into it, she is in front of the lid and behind the hatch's near edge** (the shaft's lesson, and the
    lifeboat hatch's): onto the ladder with her back to us, her climbing clip, her picture cut at the near edge's
    line, that edge drawn over her.
14. **No fade into deck 10.** The camera goes down with her; deck 10's side opens while she is out of sight between
    the tank's floor and the hallway's ceiling; she drops out of a ceiling panel (generated: shut before, hanging
    open after) onto the carpet. One way, as it was. The decks' dim holds through it (`dimHeld`: with the view held
    by `viewOverride` the pool deck stood undimmed over the hallway for half a second).
15. **The pool ladders go down to the tanks' floors** (all three of deck 11's): the atlas ladder's own rail-and-rung
    rows repeated, drawn on the tank's wall under the water.
16. **The kid's water pistol light green with blue lines** (the user: "hard to distinguish it from his ice cream").
    Repainted in his own source frames as the people's sheet is built (`"repaint": "pistol"`): no generation, so he
    is the same boy in all 41 frames. Two colour rules on the built sheet were tried first and left patches; found by
    hue and saturation at full size (not his skin, his shirt's stripes, his cap, his cone) it held. Its handle's tip
    stays orange.
17. **Her cry is over before the kid stands up:** its popup is where he and Bumbot are.

18. **A laundry line is not shown while she is inside on the deck over it** (the user): deck 10's washing, on the
    balcony under the pool, hung across the tank's floor. By her height (the open decks have no deck "in view"), and
    held while she goes down the hatch. On the balconies themselves it is as it was.
19. **The hatch and the drain's grate hardly show through the water** (the user: "much less visible when in the
    water"): 28% of themselves under it, clearing as the water goes, whole in the dry tank. They lie on the floor's
    strip of tiles, which the water's blue is not drawn over: that is why they showed whole.
20. **The tank's floor reads as its strip of pale tiles, 3 px under the wall's foot** (the user's four shifts): the
    hatch lies 3 px lower than its rough was drawn, the grate 2 px lower.
21. **In the dry tank her picture is drawn 3 px lower than her body** (the user: at the wall's foot "she looks floating
    in the air"), eased in and out over the last px of a jump into or out of it; her body, and so every rule and
    test of where she stands, is where it was (`world.tankDrop`, the ship scene's `herDrop`).
22. **The pool ladders stand 3 px lower** (the user: "both pools, always"): 15 px under the deck's line where they
    were 12 (the map's `at11`, `prop_ladder_aft`), their lower parts down to the floor's strip.
23. **Bumbot is in sight all the while he is in the water** (the user): after the splash he goes under, all of him
    below the surface and tinted by the water as she is, turns, and comes up paddling. He was taken out of the
    picture for half a second.
24. **She goes 10 px further down the hatch before the view changes** (found measuring 20 and 21): the top of her
    head was still over the near edge.

25. **The pools' water is drawn down to the foot of the tank's wall** (the user: "The water in the pool isn't all the way
    down"): the wall's last row of tiles ends 4 px under the floor she swims over and stands on, and that strip of
    it showed dry under the water, in all three pools and since they were first drawn. The water's picture only
    (`TANK_FOOT`, `pool.foot`); the drain sinks it from there. It also says why she seemed to float at the wall's
    foot (decision 21): the floor's strip starts at that same line.

26. **Under the water the hatch and the grate are washed out, not seen through** (the user, of decision 19's way:
    "they cannot be transparent, they cannot show a pool's floor through them. But they still have to be less
    visible (washed out) when under water"). Each is drawn whole, and over it a copy of itself filled with the
    floor's own pale tile colour at 70%, as the ship's washes are made; the copy thins as the water goes and is put
    away in the dry tank. Made 28% opaque they had let the floor's tile lines through.

27. **In the dry tank her picture is 5 px lower than her body** (the user: "two more pixels down"; decision 21's 3).
28. **The puddles show only as the last of the water goes** (the user: "only to show at the very last moment of the
    water drain"): from 93% of the drain on, fading in; then they dry as before. They had lain on the floor's strip
    under the water from the drain's first moment.
29. **Under him at the rim she looks up out of the water and reaches for him, lying as she swims** (the user: "That
    has to be generated"): a clip of her own, `swim-reach`, PixMiniMax from her swim's first frame on a green ground,
    she cut out by colour (`assets/source/her/swim-reach/`, two tries, 2 generations; seed 4 used). Her head lifts,
    one arm stretches up after him, the other stays on the water; it is held, straining, until the kid's jet sends
    him over her head, and then her arm comes down. Played in both ways into the scene. Its first frame is her
    swim's first to the pixel. She stops 5 px short of the rim for it, so that her hand is a few px short of him: at
    the rim it lay on his chest. This replaces decision 2's "none of her".

## 4. What U17 said to keep, and what became of it

- **The hatch is the only way into deck 10's midships hallway:** kept (`hatch_pool`, needs `drain`). It lands her
  3.3 m further aft in the hallway, on clear wall between two cabin doors, short of the tray.
- **The kid hangs on it:** kept (`npc_kid_tub` until `bb5`, `npc_kid` after).
- **The wet paw prints:** untouched.
- **His exit:** he runs off the screen along the second pool's far side, as before; where the prints start. Not
  changed: decided as it stands.
- **Part 6 remakes `bat` and `shake`:** the scene plays them by name; a leap is paced to its own length whatever
  the clip's.
- **Tests:** `region6` extended, `region6.deck` new, `golden` waits for the landing.

## 5. Not done, and why

- **No new clips of Bumbot** (decision 2), none of her (her own `swim`, `tripfall`, `reach`, `climb`, `fall`).
- **The kid's way out of the tub is not shown** (decision 6): a clip of him climbing out and a way across the
  second pool for him would be a scene of their own.
- **The pool is as shallow as it was** (0.9 m): the tank's depth is the ship's layout.
- **Sound:** the effects there were (`cry`, `giggle`, `jet`, `meow`, `splash`, `lever`, `drain`, `hatch`) and three
  more of the game's own at new moments (`creak` as the lever goes, `clang` at its stop, `rung` on the ladder). I
  cannot hear them: whether they sit right is the user's to say.
- **The shared documents** (GAME_DESIGN, population.md, CLAUDE.md, progression.md, plan-the-rest's U17) are not
  brought to this yet: on the user's word, with the merge.

## 6. Generations

60: her reach up out of the water 2 (`assets/source/her/swim-reach/README.md`), and 58 (`assets/source/pool/README.md` has every job): the first seven pictures 40, the first lever's stand 6, the
knee-high lever twice 12.

## 7. Checked

- Recorded with real keys and looked at, at the game's pixel size and enlarged: the whole scene from the water (150
  frames at a tenth of a second), from the deck aft of him, from the rim's edge; the drain every 0.4 s; the hatch
  frame by frame; each piece next to her in each state (the lever armed and thrown, the hatch shut, pulsing and
  open, the ceiling panel shut and open, the kid's cap in the tub); the outside view; a reload after the scene.
  Found and mended that way: the kid not rising (a peek's tween still running took him down), Bumbot floating over
  the lever (his jump's own rise), the pool deck undimmed over the hallway during the drop, her legs over the
  closed hull for a moment, stale frames in a first storyboard, the first lever's ragged arm.
- All 41 of the kid's frames before and after the repaint; the people's sheet compared cell by cell with the
  committed one: 40 of his cells changed, no one else's.
- `python tools/playtest.py -j 5 boot region6 golden highlight mishaps region7` pass, but for `mishaps.things`'s deck
  9 sprinkler, which fails on `main` too. `region6` checks: the kid in the tub between its far rim and its near
  wall; the hatch and the grate under the water, the lever armed; the hatch within view of the aft rim; the kid
  standing up; Bumbot paddling with his legs under the water; him on the lever as it goes over; the lever thrown;
  the water sinking; the hatch pulsing; its lid up; her on its ladder before the lid and behind its near edge; her
  out of the ceiling panel on deck 10. `region6.deck`: her dive from the deck ends in the pool, he back at the rim,
  the rest as from the water.
- `python tools/check_overlaps.py`: 0 overlaps.
- Not judged by me: how it feels in motion, and how it sounds.

**After the user's play (decisions 18 to 24):** recorded again from the water and looked at: the pool with its water
(the hatch and the grate faint, no laundry line, the ladders lower), Bumbot under the water and coming up, her in the
dry tank on the floor's strip by the hatch, her going down it. `python tools/playtest.py -j 5 boot region6 golden
highlight region7` pass; `region6` checks besides: both pieces under 0.4 of themselves through the water and whole
once the last of it is gone; deck 10's laundry line not shown from deck 11; her picture 3 px lower in the dry tank
and where it always is on deck 10's carpet. `python tools/check_overlaps.py`: 0 overlaps.
