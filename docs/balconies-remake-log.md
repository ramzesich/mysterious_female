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

*(Shown to the user; waiting for the answers.)*

## Decisions

1. Cut from `main`: nothing waits on another branch.
2. The record gives her the socks and the crawl by `P.learn`, as play does, and no `?cards=all` (near-catch 6's
   lesson).

## Generations

None yet.
