# Near-catch 6 remade: the log

The bridge (deck 10 forward, `bb6`), the sixth and last near-catch, remade by `docs/sequence-remake-plan.md` (the
fifth by the plan). The user, 2026-11-25:

> Let's continue to the next near catch in game, apply the remake plan

## 1. Set up

- Branch `near-catch-6` in the worktree `../mysterious_female-catch6`, port 8007, tests' folder
  `%LOCALAPPDATA%\Temp\bumbusik-catch6\tmp`.
- **Cut from `near-catch-5`, not from `main`** (decision 1): that branch is `main` (`1065085`, fetched today) plus the
  pool's update the user approved this morning (`1d73e53`), which waits for the word to merge. Cut from `main` this
  remake would have met it again in every document both touch. Merging this branch therefore takes near-catch 5's
  update with it.

## 2. The scene as it is

Recorded with real keys from the bridge's door (`?at=bridge&cards=all&did=horn`), walking and jumping in, frames
every 100 ms at the game's pixel size; the whole bridge shot before and after; the way up the hatch after it; the
state after a reload; the outside view.

**What happens now** (4.9 s held): at 59 px from Bumbot (he washes on the floor between the helm and the alarm panel)
she is taken by the shared stand-in (`nearCatch` in the ship scene): she walks up and bends to him, standing exactly
in front of the alarm panel. The security officer, who stood upright with his net at the forward end, walks 79 px in
0.6 s to the helm and swings; the net comes down on the floor beside Bumbot. The screen shakes, the room goes red, a
sparkle shows by the panel behind her. Bumbot leaps through the officer onto the helm, runs along the console's top,
"climbs" the ladder that has faded in rung by rung at the forward end, hangs under the ceiling and is gone. The
officer sits down on the floor. She straightens, turns to us, shrugs.

### The faults

1. **The net never touches the alarm panel.** It lands on the floor 34 px forward of it. The alarm has no cause in
   the picture.
2. **She covers the panel.** Her stop is the panel's own x (2009): the thing the scene turns on is behind her body
   from the moment she arrives.
3. **The beacon turns on her head.** It is drawn over her, at her head's height, with two red wedges drawn in code.
4. **Bumbot leaps through the officer** (his body crosses the man's chest and cap), with nothing to spring from.
5. **His climb is a stand-in:** one leap frame slid 100 px up the ladder; then he hangs in the air under the ceiling
   for 0.7 s and vanishes.
6. **There is no hatch.** Nothing in the ceiling before, nothing opens; the ladder fades in, pale, in front of the
   console's forward end, and runs into a flat ceiling. On deck 11 she comes up through the balcony's solid floor.
7. **The scene's ends are at the screen's edge.** At the take-over the view starts at x 1826: the officer (1867) is
   cut by the edge, the ladder (1864) is 38 px from it.
8. **The officer does not creep.** He stands upright in plain view with his net; then a quick walk, a swing held as
   one frozen frame for 2 s, and a sit on the floor that slides 8 px. The plan had him tangled, slumped in the
   captain's chair, waving her on.
9. **Her part is the stand-in:** she bends to a cat on the floor and stays bent for 2.3 s while a man with a net runs
   at them, the alarm goes off and a ladder drops; she looks at none of it, and ends facing us, her back to nothing,
   with the way on (the ladder) behind the officer.
10. **Everything at once:** the swing, the shake, the red light, the whoop, his leap, the ladder and his run fall
    inside one second.
11. **In a jump she lands on him:** taken in the air within 8 px of the floor, at 4 px from him; she then turns her
    back on her way, walks to his forward side, and the officer runs onto her and swings through her.
12. **The red wash shows on the ship's side** for a moment as she climbs out onto deck 11 (it is drawn over her
    layer, and the bridge's cut-away is still fading).
13. **The seated officer covers the helm,** which the plan's text has him sit by; from a reload he is a still.
14. **Bumbot is on the floor;** the plan's text has him on the console.

### What hangs on it

- Flags: `bb6`, which gives `alarm` (`FLAG_GIVES`). `alarm` opens the hatch's ladder (the gate at x 1864, deck 10 to
  deck 11's balcony, `hide: True`), starts the sunset as she stands on the balcony (`src/world/finale.js`), and moves
  where a fright on the mooring deck sends her.
- People: `riv_bridge` (after `horn`, until `bb6`), `riv_bridge_sat` (after `bb6`, until `catch`).
- The alarm: the red wash, the beacon and the whoops (`updateBow`), until `catch`; `rumble('alarm')`.
- On the bridge besides: the captain's book (`book_10`, on the chart table at 2280), the bridge's door (2400),
  `cp_bridge` outside it. Nothing else answers E.
- Tests: `golden` (the flag, the alarm), `region9` (the officer creeping, the flag, the ladder's tiles, the officer
  sat, the book), `region10` and `check_overlaps` set the flags by hand.
- **What cannot move:** the hatch's column (x 1864): deck 11's balcony over it ends at the spa's wall at x 1896, and
  the bridge's forward wall is at 1843.

### Its reach against one screen

She comes in at the door (2400) walking forward; what she sees ahead is 208 px. From the take-over (2034) to the
forward wall is 191 px: it fits, with the officer and the ladder in its last 40 px. The remake leads the picture
ahead of her (as near-catch 2's does).

### The pieces as they stand

All washed 20% (`-w20`): the console (72 x 46) at 1886, under the ladder; the helm (33 x 44) at 1946; the alarm panel
(38 x 59) at 2009; the captain's chair at 2083. Named only by the map builder and the art builder; nothing pulses.
The officer's character has `idle`, `walk`, `peek`, `swat` (cut into `swing`), `lunge`, `charge`, `sit`, `trip`,
`shake`.

## 3. The structure

Proposed to the user with a rough set up in the running game (the pieces moved, the hatch as flat shapes, the
figures in frames they have now): `rough-structure.png`.

*(Waiting for the user's answers.)*

## Decisions

1. The branch is cut from `near-catch-5` (above).

## Generations

None yet.
