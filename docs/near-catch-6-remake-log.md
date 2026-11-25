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
6. **The hatch is a 5 px strip.** In play a grey strip 28 px wide lies on the ceiling line before the alarm (with
   `?cards=all` the ladder shows from the start instead); nothing is seen to open; the ladder fades in, pale, in front
   of the console's forward end, and runs into a flat ceiling.
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

15. **Her way out is broken** (found recording the climb): as her head passes deck 11's floor the bridge's side closes
    over her; for half a second her legs hang on the ship's white side, the red light in a band across it, and her
    head rises behind the balcony's glass. The balcony's floor is behind its bulwark: there is no hatch to draw there,
    the fault is how she passes through.

## 3. The structure

Proposed with a rough set up in the running game (the pieces moved, the hatch as flat shapes, the figures in frames
they had). The user's answers, 2026-11-25:

> 1. Just don't use the cry as a call, because that wouldn't make sense. How exactly do you suggest to implement the call?
> 2. Ok
> 3. Do as you proposed

and, to the answer (her own clip: down on her heels, a hand held out, her fingers rubbing; a small speech popup,
«Киць-киць-киць» / "Pss-pss-pss"; a soft sound of its own):

> Do the call as you suggested

So: **she calls him softly and he starts to come** (decision 2: it is the one near-catch where he answers her, and the
ending is his coming to her when she stands still); **only what the scene needs is generated**, the rest of the bridge
stays (decision 3); **all the faults are mended** (decision 4).

## 4. The sequence, beat by beat

World px; the floor at 704, the ceiling at 576. The hatch's column stays at 1864. The console moves 44 px aft (1930),
the helm 84 (2030); the alarm panel's cabinet gives way to **the alarm station** at 1985, hard against the console's
aft end: a pedestal with one big red button on its top and a beacon on a stalk.

| T (s) | What happens |
|---|---|
| before | The hatch's collar under the ceiling at the forward end, its lid shut. Bumbot sits washing on the console's aft end (1944). Behind him, in front of the console, the officer frozen mid-creep on tiptoe (1903), his net raised, wobbling |
| 0 | She is taken at 2050, 65 px from the station (in the air across that line she comes straight down there). The picture is led ahead of her, so the hatch is 80 px inside it |
| 0.15 | She goes down on her heels and holds out a hand |
| 0.95 | Her call: the popup, the soft sound; her fingers rub |
| 1.0 | He stops washing and looks at her |
| 1.3 | He gets up; at 1.9 hops from the console onto the station's top, over its button, toward her hand; there at 2.3, 25 px from her fingers |
| 1.85 | The officer, seeing her get him first, hurries after him on tiptoe: two steps, 42 px, to 1945 |
| 2.77 | He swings. Bumbot springs straight up (2.84) |
| 2.99 | The hoop comes down on the button where he stood: the clang, the shake. At 3.08 the beacon, the whoop, the red light. She starts up onto her feet |
| 3.3 | Bumbot comes down on the officer's cap and looks round; the officer bent over his net, which is stuck on the station |
| 3.45 | At the forward end the hatch's lid drops open; at 3.7 its ladder rattles down, down by 4.3 |
| 4.35 | Bumbot leaps off the cap to the console's top, runs, leaps onto the ladder (4.65) and climbs it paw over paw into the hatch; gone by 5.9 |
| 4.45 | The officer tugs at his net, upright; at 5.55 it comes free, he goes over backward, and it comes down over his own head; sat so at 6.1 |
| 5.0 | She looks up after Bumbot |
| 6.3 | She is hers, facing the ladder. The officer sits under his net, sighing, until the end of the game |

Then her way out: up the ladder into the collar (her picture cut at its mouth: she is behind its near side), the
bridge kept open until her feet are in, her head rising behind the balcony's bulwark; the sunset as it is.

Against the rules: one space, no fade; her way kept (forward, then up); every effect with its cause in the picture
(her call, his coming; her getting him first, the officer's hurry; the hoop on the button, the alarm; the alarm, the
hatch; the stuck net, the fall); she goes into the collar behind its near side; nobody leaves the picture but Bumbot,
up the hatch; the ladder she needs comes down in view and she ends looking at it; nothing waits for a key.

## 5. The preview

Each piece drawn flat at its size into the game's own picture of the place, redrawn by PixelLab, cut by what differs
(`assets/source/bridge/`, its README has every job); each clip made from the sheets' own frames on green, the
officer's main clip and Bumbot's climb on green copies of the place. A storyboard on its clock
(`assets/source/bridge/storyboard.py`), composed offline from the pieces as built and the clips as cut.

Checked frame by frame before showing: the station and the hatch cut clean (no speck, nothing enclosed left empty);
the ladder rebuilt from one clean period (in front of the window the cut had taken the sea's pixels); the lid drawn
at each angle stepped along its longer way (turned pixel by pixel it was ragged; its swing past the vertical kinked
and was left out); her three clips start and end on the frames they should (her stand, the crouch) to the pixel, her
size and colours held; the officer's creep measured (his planted foot slides 5.3 px a frame: 42 px a loop, which
set where he starts); his hoop lands on the station's top in the main clip; Bumbot's first leap was drawn with his
jump's own rise added to the arc (he went through the ceiling): his leap's frames now.

Self-review of the storyboard changed three things: Bumbot sits at the console's aft end, not its middle (the
officer's hands were in front of him); he hops to the station before the officer moves (they overlapped); the
officer's creep is one loop of 8 frames, so he starts 42 px from where he swings.

*(Shown to the user; waiting for the word to build.)*

## Decisions

1. The branch is cut from `near-catch-5` (above).
2. She calls him softly, and he starts to come (the user's choice of the proposal; "Just don't use the cry as a call").
3. Only the scene's own pieces are generated: the hatch, the alarm station; the bridge's look stays.
4. All fifteen faults are mended.
5. The alarm is one big red button on a station of its own, and Bumbot stands over it as the net comes down: the old
   panel was a cabinet of small lights with nothing a net could press.
6. The hatch is a collar under the ceiling with a lid seen edge on and a ladder let down out of it; the lid is drawn
   by rule (a thin turning part), the ladder slid down by rule.
7. Nothing is drawn on deck 11: its floor is behind the balcony's bulwark.
8. The officer's net is one clip from his stalk to sat under it, on a green copy of the place (the plan's rule for a
   key beat), played on a schedule: frames 4 to 6 over and over while Bumbot is on his cap.
9. Bumbot's way forward is over the officer's cap: the officer stands between him and the hatch, in front of the
   console Bumbot must run along.

## Generations

40 so far (`assets/source/bridge/README.md` has every job): the hatch 6, the station 5, her call 4 (three clips, one
try unused), the officer 23 (his stalk 2, its loop 1, his creep 1, the end picture twice 12, his main clip twice 6,
his sigh 1; three of those tries unused), Bumbot's climb 2.
