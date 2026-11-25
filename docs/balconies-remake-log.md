# The balconies remade: the log

The path through the balconies of decks 8 to 10 (region 7, optional), looked at from start to finish by
`docs/sequence-remake-plan.md` (the sixth by the plan). The user, 2026-11-25:

> In the game, there's a part where we are on the balconies and we are supposed to progress from there, is that optional?

and, told that it is:

> I need you to analyze the path through the balconies, start to finish, in terms of gameplay, visuals and everything. Apply the same sequence remake method.
> For example, jumping down between the balconies, or climbing up.
> I feel like things are broken there.

## 1. Set up

- Branch `balconies` in the worktree `../mysterious_female-balconies`, cut from `main` at `1ea13f0` (fetched today);
  the tests' folder and the scratch scripts and pictures in `%LOCALAPPDATA%\Temp\bumbusik-balconies\` (`scripts`, `out`,
  `tmp`).

## 2. The path as it is

Recorded with real keys on the stepped clock, a frame every 70 ms at the game's pixel size, her place, speed and
frame beside each; the socks and the crawl given as play gives them (`P.learn`), region 6's flags set, **never
`?cards=all`**. From the balcony cabin's door (deck 9, `?at=balcony`): in and out of the door; a jump alone at a
partition; a vault aft and one forward; the climb up to deck 10; the same keys on deck 10; the drops 10 to 9 to 8 to
the boat walkway; a row's forward and aft end on each deck; a drop with nothing under; a laundry line; a perched
gull; the sunbather's balcony; a gust; an ajar door (in, through the cabin, out); the guest locked out; up a column
from the walkway; the parasol from deck 10.

**What there is.** Three rows of balconies, 68 on decks 9 and 10, 66 on deck 8, each 125 px wide, 8,500 px a row.
She comes out of the balcony cabin's door (deck 9, x 7815) in the grip socks. Between balconies stands a partition:
a wall 88 px high for her body (her jump is 68), drawn as a white post 6 px wide. Her three moves are the wall jump's:

- **Along:** a jump, then jump again in the air within 5 px of the partition: a kick sized to clear its top by
  16 px, at her run's speed (`tryWallJump`, the `over` branch).
- **Up:** with ↑ held, each jump beside the partition is a kick straight up; four kicks reach the balcony above
  (the grip runs 140 px up, "a pole on the partition's top").
- **Down:** ↓ and jump: a small hop, and the floor lets her through, where a floor of the route lies one deck under.

On the way: a gust every 7 s (1.5 s, 60 px/s aft on her in the air), ten perched gulls (gag 20), five laundry lines
(a crawl), two balconies with someone on them (gag 24), five ajar balcony doors and the locked-out guest's, four
tangerines, his sleep mask, a photo slot. Under deck 8 the boat walkway, with ten columns and two end walls to kick
up.

### The faults

**Her moves**

1. **The climb goes through a floor.** Kicking up beside the partition she rises in front of the 44 px slab between
   the decks, her head already behind the glass of the balcony above while her legs are still in front of the slab;
   for a frame only her shoes show under its sill. A balcony's floor is solid in the picture and she passes it.
2. **There is nothing to climb.** The "pole on the partition's top" is not drawn: the post ends at 88 px and above
   it the opening is empty. She rises in her jump's pose with a hand up, holding nothing (the user's rule,
   2026-11-21: her hands rest on a drawn edge in every frame).
3. **The climb overshoots.** She arrives 120 px over the floor above and falls back onto it. On deck 10, where
   nothing is above, the same keys carry her 165 px up: she hangs in front of deck 11's slab and its pool deck (the
   palm, the bar) and drops back.
4. **The drop goes through a floor too:** she sinks through the slab, drawn in front of it, having stood behind
   the glass a frame before.
5. **The vault skips.** As her feet pass the panel's top she is moved 40 px sideways in one frame (a usual frame
   moves her 2): `offPartition`, which lifts her off a partition's top, carries her across it. Nothing of her
   touches the partition; the pose is her jump's.
6. **Her picture is cut in half at a partition.** Pressed to one, or sliding down it, half of her is gone: the cut
   made on 2026-11-21 so that she would not show on the next balcony. On the walkway's columns the same, down to a
   sliver.
7. **At a partition she runs on the spot** (her run's cycle against a wall), and her slide down it is her wall
   slide on a 6 px post.
8. **A kick at a row's forward end takes her out of the ship,** on all three decks: the row's first partition stands
   against the end wall, the lift off its top puts her inside that wall, and she comes out past it, falls down the
   ship's side across the windows, and is back at her checkpoint with a fright. (The aft ends hold.)
9. **None of the three moves is ever explained.** No hint for the vault's second press, for ↑ with a jump, for ↓
   with a jump (the rule of 2026-11-20: every new mechanic explained once). The vault needs its second press inside
   about 0.3 s, within 5 px of the post.
10. **The picture goes up and down with every vault:** 68 px up and back in a second; in a climb it scrolls a deck
    and a half and returns.

**What she meets**

11. **Up from the boat walkway she comes through deck 8's floor in the middle of a balcony,** into its furniture
    (the columns stand under the balconies' middles): at 7925 she arrives standing in a chair.
12. **Under the parasol she sinks through the balconies below,** their floors, chairs and tables, behind each glass
    front and in front of each slab in turn. The code means her to be out over the rail (`overTheRail`).
13. **On an occupied balcony she lands on its guest:** on the sunbather's legs, her "Oh, sorry!" said standing in
    his lounger; the screen then fades to her checkpoint.
14. **Bumbot's glimpse:** he washes sat on the top of the 6 px post, 88 px up, leaps and fades out in the air ("gone
    up to the balcony above", through its floor). The plan had him swipe at a gull on a rail and go in at a door.
15. **Furniture is walked through:** loungers, chairs, tables and plants stand across the whole width of a balcony
    she runs along, behind her; where she lands after a vault there is often a chair.

**The look**

16. **The rail is at her eyes:** the balcony's front is 50 px high ("drawn to the ship's scale") against her 59;
    every other railing on the ship is 32. All of her below the hair is seen through its glass.
17. **A partition does not read as a wall:** a thin white post with open air above it. Nothing says why she cannot
    jump it, or that it is a panel seen edge on.
18. **Everything of the balconies is drawn in code:** the fronts (two rectangles and three lines), the posts, the
    ajar doors (a pale rectangle and a curtain: plan-the-rest §7h, the user: "they don't look like doors at all"),
    the towels, and the washing (three flat bars of colour hung from the ceiling; §7i's list). The art rule of
    2026-11-16 has such things generated.
19. **The washing stops her standing like a wall** (she runs on the spot against it) and hangs from the ceiling,
    not from a line between two things.

**The path as a whole**

20. **Long runs of one move.** From her door the nearest way into a hallway is three balconies aft and one down;
    everything else is far: the aft doors 24 to 32 balconies aft, a tangerine 20 forward, the photo slot 30, his
    sleep mask 34 (its place the user's, §7f). A crossing takes 1.2 s at best: the mask is 40 s of the same two
    presses. The walkway under deck 8 runs most of the way with nothing on it but the drill.

### What hangs on it

- **Code:** `tryWallJump` (its `over` and ↑ branches), `updateWallSlide`, `VERBS.vaultClear`/`vaultMin`
  (`src/world/verbs.js`, the config); `offPartition`, `gripAt`, `dropFloorAt`, `balconyRoom`, `buildOutside`
  (`src/world/world.js`); `dropThroughWalk`, `overTheRail`, `partitionShort`, the stand-in `balconyPic` and its crop
  (the ship scene); `Gusts`, `PerchGull`, `Laundry`, `Occupied`, `setupOutside`, `outsideTextures`
  (`src/world/outside.js`); `glimpseBalcony` (`src/world/story.js`).
- **The wall jump itself stays:** the atrium's pillars, the walkway's columns and end walls, deck 12's end wall
  (region 8's way in, on the main route), the funnel's plating use the same kick.
- **Data:** `PARTITION_H` 88, `POLE_H` 140, `UNIT` 125, the grips with `over`, the walls, covers and glass
  (`tools/build_world.py`); `LINES`, `PERCH`, `OCCUPIED`, `GUSTS`, `BALCONY_SET`, `BALCONY_CPS`, `GLIMPSE_BALCONY`
  (`tools/population.py`).
- **The story:** the socks open region 7; the flags `glimpse_balcony` and `guest`; six checkpoints at the balcony
  doors (five after part 10); four tangerines, his sleep mask (14), the photo slot, the guest's book; gags 20 and 24.
- **Tests:** `region7`, `region7.mask`, `balcony`, `mishaps.balcony`; the start places `balcony`, `gull9`,
  `occupied8`, `mask10`.
- **Documents:** `GAME_DESIGN.md` §6.1 (region 7) and its controls' table, `README.md`'s controls, `docs/population.md`,
  `docs/plan-the-rest.md` §7h (part 13, the balconies' doors), §7i (part 14, what is drawn in code), §7f (part 11:
  two gulls and the gusts on the walkway).

### Its reach

One row is 17.7 screens. The view shows 220 px ahead of her: one balcony and three quarters of the next. A deck up
is out of the picture while she stands (the floor above is 20 px under the view's top).

## 3. The structure: proposed, to be settled with the user

**The cause of 1 to 7 is one:** the balconies were given the wall jump, a move made for a wall beside her, and the
picture of a balcony has no such wall: a partition is a panel seen edge on, a floor is a slab, and the only way
from one balcony to another that a person could take is outside the rail. Nothing of that is drawn.

**Proposed: three moves of her own, each on the outside of the rail, drawn** (roughs with her ladder's frames as
stand-ins: `rough-along.png`, `rough-updown.png`):

- **A, along:** Space at a partition (one press, from a run or standing): she swings out over the rail, round the
  partition's outer edge with her hands on it, and in again on the other side, running on. About 0.6 s.
- **B, up:** ↑ and Space at a partition: onto the rail, a hand on the partition; up to the edge of the floor above;
  onto it outside its rail; over the rail and in. About 2 s.
- **C, down:** ↓ and Space at a partition: out over the rail, down to hang from her floor's edge, onto the rail
  below, in. About 1.5 s.

Out there she is in front of the glass, the slab and the partition, whole; in again she is behind the glass. No
floor is passed, nothing cuts her, the picture holds its height in A and follows her once in B and C.

Five questions went with it (the moves; the rail's height; the pieces generated now; the smaller mends; the rows'
length). The user, 2026-11-25:

> 1. As proposed. Take care of visuals. For example, the ladder frames work poorly when the balcony's glass wall finishes, but she still climbs with her hands up in the air.
> 2. As recommended
> 3. Yes
> 4. Ok
> 5. Yes
> Also, she is supposed to use grip socks, but it is very unclear that she actually uses them here. Maybe, during the relevant animations/scenes the grip socks have to be actually worn

and, while the preview was being made:

> The current socks also don't look like grip socks.
> We could regenerate all of the sock sprites and the close up

> I don't like the reflections, because they repeat on each window, the reflection should be continuous, if it is there.
> Perhaps, it is better to generate windows without reflected clouds

So: the three moves as proposed (decision 3); the rail at 32 px (4); the pieces generated (5); the smaller mends, all
(6); the layout left as it is (7); the socks worn out on the balconies and made again as grip socks (8); the doors'
glass plain (9).

## 4. The beats

| Move | Key | What is seen | Held |
|---|---|---|---|
| A, along | Space at a partition, on the floor or in a jump | she jumps to the partition's edge, crosses in front of it with her hands on it and her socks on the wall, drops on its other side and runs on | 0.6 s |
| B, up | ↑ and Space at a partition | she turns to the partition's fin, climbs it hand over hand, her socks on the wall either side, past the slab, over the rail above, turns | about 2 s |
| C, down | ↓ and Space at a partition | over the rail, down the fin the same way, in over the rail below | about 1.6 s |

Each on the rules of the plan's step 4: one continuous space; her direction kept (A ends running the way she went, B and
C end facing as she stood); a cause for every hold (the fin is drawn, deck over deck); outside the rail she is in front
of the glass, the slab and the partition, inside it behind the glass; nothing waits for a second press. A gust while
she is on the fin: she holds on until it drops. The camera holds its height through A and follows her once through B
and C.

## 5. The preview

**The geometry** (in the builders, for the mock-ups; `BALCONY_RAIL_H`, `PARTITION_H` in `tools/build_ship_map.py`,
`RAIL_H` in `tools/build_world.py`, `data.outside.rail`): the front's rail 32 px over the floor (it was 50); the
partition a panel from the floor to the recess's ceiling, 116 px (it was 88, with open air over it); its fin run on
across the slab's face to the balcony above, so that one white post stands deck over deck and her hands have a hold all
the way. The whole ship rendered before and after (`tools/render_ship.py`). **The branch is not playable on the
balconies in this state:** the old kicks meet the new partition; the moves come with the build.

**The pieces:**

- **The recess with the cabin's sliding door,** drawn flat by rule (`assets/source/balconies/roughs.py`: a frame, two
  panes, a handle, curtains drawn back inside; the door's glass now runs to the floor, the lower rail shows it) and
  redrawn in place by PixelLab; a second redraw with plain dark glass after the user's word on the reflections
  (`tries/unit-2.png`); the same door slid open on the lit cabin with a sheer curtain in the doorway
  (`tries/unit-ajar-1.png`), which takes the place of the code-drawn `balcony-ajar` and its curtain (plan-the-rest §7h).
  Every other balcony mirrored, as real cabins are.
- **The grip socks' close-up:** six tries (`assets/source/closeups/tries/socks/`); S1 (`try6.png`) is the approved pair
  redrawn with one sole up, rows of white grip dots on it, and a dotted sole's edge on the other.
- **The socks on her:** by rule, in every frame of her sheet (her shoes found as the small navy pieces with the shoe's
  own colour at a leg's end; pink, a lighter cuff over the ankle, the sole's edge dotted white). Worn while she is out
  on the balconies. (The rule's first form also tinted specks by her eye and in her hair, which a check of her legs
  alone had missed: found before anything was shown, the clips made again from clean frames.)
- **The washing:** two tries; the first, a line between two poles that stand on the floor, reads.

**The clips** (PixMiniMax on a green copy of the game's own picture of two balconies, `assets/source/balconies/sets.py`,
from her sheet's own frames in the socks, each pinned to its end):

- **up** and **down**, 32 frames each on a 128 x 256 canvas, first try: she holds the fin in every frame, her socks on
  the wall either side of it, and steps over the rail at each end.
- **along**, 12 frames on 128 x 128, four tries: the first two put her behind the partition for part of the way; "seen
  from behind ... climbs sideways across the front of the post" kept her in front of it. Her socks came out dark red in
  most of its frames: to be brought to the pink by rule or by one more try in the build.

**The storyboard** on its clock, the whole screen at the game's px (`story.gif`, 7 s: up, down, along), composed over the
real picture with the new look; her picture behind the glass where she stands inside (the glass's tint and the rail's
cap over her), in front of everything while she is outside.

The user, on the preview (2026-11-25):

> Almost all good.
> Look carefully how she transitions from behind the balcony glass to in front of it. I see in some frames that makes less sense

> Socks close up S3, add barbs to the soles (visible only on the bottom)
> On S1 one of the socks covered in barbs entirely, that doesn't make any sense

**The transitions, measured** (her lowest row over the floor and her middle from the partition, frame by frame): in
the first climb she stood on the partition's line with her feet still on the balcony's floor (frame 4), then rose
through 13, 16, 21, 29 px, under the rail's 32, drawn in front of the glass; at the top she came onto deck 10's floor at
the floor's height, through its rail. The storyboard had also drawn the along clip's first and last frames in the air
in front of the glass with her feet under the rail.

**Mended** (decisions 11 and 12):

- **One rule for the layering:** what of her is under the top of the rail of the balcony she is inside of is behind
  its glass (the tint), behind its rail's cap and its sill, and behind its partition; what is over a rail's top is in
  front of the partition and its fin. She is inside the lower balcony until her feet are on its rail, outside on the
  fin, inside the upper one from the moment she leaves its rail.
- **The climb in parts, so that the rule is true of every frame:** the *mount* (8 frames: she takes the partition's
  edge and gets up onto the rail on her own side, her middle 10 to 12 px short of the partition all the way, her feet
  from 0 to 33 px), the *swing* (4 frames: from the rail onto the fin, a foot on the rail each side of it, her feet at
  33 px throughout), the *climb* (24 frames, from that perch on deck 9's rail to the same perch on deck 10's). Up is
  mount, swing, climb, then the swing and the mount backwards on the deck above; down is the same the other way. The
  along clip already crossed above the rail (35 to 36 px); only its layering was wrong.
- **The socks' close-up:** S3 with a row of nubs under each sole (`tries/socks/try7.png`).

*(Shown to the user again.)*

## Decisions

1. Cut from `main`: nothing waits on another branch.
2. The record gives her the socks and the crawl by `P.learn`, as play does, and no `?cards=all` (near-catch 6's
   lesson).

3. The three moves are hers alone and drawn, outside the rail; the wall jump's kick stays everywhere else (the user: "As
   proposed. Take care of visuals").
4. The rail 32 px, as every other railing; the ship's side changes on all 202 balconies (the user: "As recommended").
5. The balconies' pieces are generated now: plan-the-rest §7h (part 13) and the balconies' share of §7i (part 14) are
   taken in here.
6. The smaller mends are all done with it (the rows' ends, a hint a move, the camera, the walkway's columns, the parasol,
   the occupied balcony, Bumbot's glimpse, the furniture, the gusts).
7. The rows' layout and what lies on them stay.
8. The socks are worn out on the balconies, in every frame, and made again as grip socks: the close-up, the world's
   sprite, her feet (the user: "it is very unclear that she actually uses them here"; "The current socks also don't look
   like grip socks").
9. The doors' glass is plain, no reflected sky (the user: "they repeat on each window").
10. The partition is a panel to the ceiling and has a fin up the slab: the climb needs a hold in every frame (the
    user's rule of 2026-11-21, and "she still climbs with her hands up in the air" of the roughs).
11. Her picture's layer at a balcony is a rule of the rail's top (under it: behind the glass, the rail and the partition
    of the balcony she is inside of; over it: in front), never a switch at a frame (the user: "Look carefully how she
    transitions from behind the balcony glass to in front of it").
12. The climb is the mount, the swing and the climb from perch to perch; up and down are the same three clips, the
    mount and the swing played backwards to come in.
13. The socks' close-up is S3 with nubs under the soles (the user; S1's sole covered in dots "doesn't make any sense").

## Generations

62 so far (8,931 to 8,869).

| What | Tool | Job or object | Cost |
|---|---|---|---|
| Socks' close-up, tries 1 to 3 | `create_map_object` | `7546324e`, `1cd1c32e`, `d8901a36` | 3 |
| Socks' close-up, tries 4 and 5 | `create_map_object` | `41b9caa5`, `24f1af54` | 2 |
| Socks' close-up, try 6: the approved pair redrawn (S1) | `edit_image_pro_flash` | `2c2fec19-2466-45d9-b513-9ceb864361b8` | 6 |
| The recess and its door, redrawn (reflected clouds: turned down) | `edit_image_pro_flash` | `54811945-289e-4ea6-9323-2831f50d1e25` | 6 |
| The door ajar | `edit_image_pro_flash` | `6e9fa3d4-2158-47f1-8023-5a894dcacc5b` | 6 |
| The recess and its door, plain glass | `edit_image_pro_flash` | `4d4e1caf-f06e-42ed-8ccd-66dfc65d630c` | 6 |
| along, tries 1 to 3 | `animate_image_pixminimax` | `cfec45f9`, `98d52cfd`, `937e2068` | 6 |
| up, down, try 1 (a pink speck on her head in the start frames) | `animate_image_pixminimax` | `10ff347b`, `cdd58140` | 6 |
| up, down, try 2 | `animate_image_pixminimax` | `3ca4ae79-354b-4a28-9190-dbd997f24526`, `9b7f9914-a4a7-4420-8881-214d0f16182f` | 6 |
| along, try 4 | `animate_image_pixminimax` | `0a7bc7f8-46b5-40df-8a88-58d81044e459` | 2 |
| The washing, tries 1 and 2 | `create_map_object` | `ba46b768`, `613961b8` | 2 |
| The mount, try 1 (on the partition's line before her feet were on the rail) | `animate_image_pixminimax` | `e116100f-e814-4620-a5f4-e6750ae215b9` | 1 |
| The climb from perch to perch | `animate_image_pixminimax` | `731be123-bacd-4ed2-9aef-684041b10de2` | 2 |
| The mount, try 2: onto the rail on her own side | `animate_image_pixminimax` | `47a55585-518f-4c09-a306-db0ab9895720` | 1 |
| The swing from the rail onto the fin | `animate_image_pixminimax` | `8b788abb-bd73-4c6b-ac16-f036e3881c7f` | 1 |
| Socks' close-up, try 7: S3 with nubs under the soles | `edit_image_pro_flash` | `305b0865-4413-4445-9c03-780890f15d18` | 6 |
