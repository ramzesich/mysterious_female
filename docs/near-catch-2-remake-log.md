# Near-catch 2 remade: the log

The Library's near-catch (deck 6, `bb2`), remade by `docs/sequence-remake-plan.md`, the second sequence done by it
(the first: `docs/near-catch-1-remake-log.md`). Branch `near-catch-2`, worktree `../mysterious_female-catch2`, from
`main` at `18e6035`. Scratch: `%LOCALAPPDATA%\Temp\bumbusik-catch2\`.

## The prompt, word for word

The user, 2026-11-24, right after near-catch 1 was merged:

> In this same manner, let's work on the second near-catch

## The scene as it was (step 2)

Recorded with real keys from the Library's start (`?play&at=library`), walking and in a jump; she can only come from
forward, the aft door being roped until this beat. Every tenth of a second at the game's pixel size
(`out/old-walk/`, `out/old-jump/`).

What it was: the ship scene's plain `nearCatch`. 60 px from him she is taken, walks up to 34 px, bends to pick him up;
he wakes, leaps, runs aft at 300 px/s to 193.6 m, where the rope stand turns over and the aft door opens; she
straightens, shrugs, and is free when he is gone.

Faults found:

1. **He hangs in the air.** His spot is "the reading table", lifted by that piece's height, which is its lamp's top
   (29 px): he lies over the lamp, on nothing. The table is 20 px wide, he is 36. There is no book. (The one fault
   the user had named before: "he sleeps over the reading table's lamp".)
2. **She reaches at the floor, through an armchair.** Her stop is in the forward armchair's place; her reach bends
   to the floor, her hands 30 px under him.
3. **His leap goes 70 px straight up,** to the ceiling's height, and the next frame he is on the floor in a run,
   through the aft armchair.
4. **The point of the scene is never seen.** The rope and the door are 12.6 m (605 px) aft of the table; the screen
   shows 220 px ahead of her. He is out of the picture 0.9 s after he bolts; the stand goes over and the door opens
   460 px past the screen's edge.
5. **She is held 3.5 s, the last 1.5 s waiting** for a cat who has already left the picture, on her shrug's last
   frame.
6. **He runs through what stands in his way:** the globe, the chess table, the trolley, the librarian's desk, and
   past the librarian, who does nothing.
7. **The stand's fall is a quarter turn of its picture** by a tween, with a second prop (`prop_rope_down`) appearing
   where it lay; at rest its card covers the rope, so the stand reads as a yellow board on legs.
8. **In a jump the scene takes her in the air:** she hangs 4 px over the floor for the whole scene, and having passed
   him she walks back and reaches at him from aft.
9. Her cry near him turns him round in his sleep (the story's `heard` flips any Bumbot at a spot).

What hangs on the scene: the flag `bb2` (it opens the door `part-door-6-194`, lock `flag:bb2`, whose rope is the
block drawing `flag:bb2` with the sign QUIET PLEASE; `prop_rope_down` after it; `story.leaveAjar()` on a load);
region 3 beyond the door; `BEATS["bb2"]`, `BEAT_LIFT["bb2"]`; the playtests `golden` and `region2` (the door roped,
the beat from 177 m, the door open after, the stand lying); the three reading tables' armchairs are seats she reads
in (`LIBRARY["tables"]`); the librarian's shush as she runs past the desk or cries; the shelf with gaps over the two
bookcases by the desk; the return trolley.

## Decisions

1. **Where the scene plays** (asked with a picture of the Library's aft half, one screen marked: A, he sleeps at the
   aft end, one picture with the rope and the door; B, he stays at the table and she chases him to the door; C, the
   camera runs with him). The user: "He sleeps on top of the book return basket, everything else derived from A".
   So his spot is the return trolley's top (191.04 m, 34 px up: `BEATS`, `BEAT_LIFT`), 2.4 m from the rope and 3 m
   from the door. He is 30 px wide asleep and the trolley 29: he fits. The three reading tables stay as they are.
2. **How she goes for him** (a, she creeps up on tiptoe and reaches at his height; b, a cry and a dash as at the
   pass; c, nothing of hers). The user: "a".
3. **The door swings aft, away from the knock** (mine): by the builder's rule it swung into the Library, toward the
   stand, and a stand knocked into it could not open it. `OWN_SWING` in `tools/build_ship_map.py`. The fallen stand
   lies in the doorway, which is why the door stays open.
4. **The librarian has a part** (mine): her finger to her lips as the scene takes her (her `shush`, which she gives
   anyway to anyone running past her desk: it is the reason for the tiptoe), a start at the crash (a new clip,
   `flinch`), a look at the door.
5. **Her tiptoe and her reach are her own character's** (skeleton-v3 by poses written for it, as her shrug was):
   `creep-tiptoe` (a loop of 8: two small steps on her toes, her hands held in front) and `creep-reach` (8: both
   arms out at chest height, leaning in on her toes; played back to straighten).
6. **The stand's fall** (mine): from the game's own stand to an end picture made of its own pixels (each post a
   quarter turn, lying aft), PixMiniMax between them in the game's picture of the place; the posts cut out along
   their own axes, the rope drawn by rule from ring to ring in every frame (a line whose ends move is not left to
   the generator: it came in pieces). Its card is the game's own, lowered and squashed flat as it turns face up.
   PixelLab's redraw of the end picture merged the two posts into one bar: not used.
7. **The clock** (to be judged in play): taken 64 px from him; tiptoe 0.89 s over 25 px; he wakes as she reaches,
   leaps as her hands arrive (1.2 s), lands 1.54 s, meets the stand 1.65 s, the door opens 1.8 s; she straightens,
   shrugs, and is free 2.7 s after she was taken (it was 3.5 s).

8. **The preview stop:** the pieces enlarged, a storyboard of eight moments composed over shots of the real room, and
   the same on its clock as a GIF. The user: "Go ahead".
9. **The picture goes 40 px ahead of her as she creeps** (mine, from the kinds of correction: the subject at the
   screen's edge): walking aft she is 220 px from the screen's right edge, and at arm's length from him the open
   door's leaf was 5 px from it. `QUIET.ahead`, eased over 0.7 s, given back as she is freed.
10. **He goes through the stand on our side of it** (mine): at his own depth he ran behind its card.
11. **The lobby's wall picture stands 18 px further aft** (mine): the leaf of the door, open into the lobby now, covered
    half of it.
12. **An asleep Bumbot is not turned by her cry** (mine; fault 9): he sleeps on, as he does through a thrown tangerine.
13. **With something in her hands she does not reach** (mine): she stops where she is, he wakes and bolts all the same,
    and she looks after him without the shrug.
14. **A start place of its own, `?at=quiet`** (mine): 6 m short of the trolley; the Library's own start is 31 m from it.

## How it is built

- **Data:** `BEATS["bb2"]` at the trolley's metre, `BEAT_LIFT["bb2"]` 34; `OWN_SWING` for the door at 194 m on deck
  6; the fallen-rope prop `prop_rope_down` and its drawn picture are gone (what lies there is the fall's last frame);
  the lobby picture's shift; the place `quiet`.
- **Art:** `tools/build_quiet.py` to `assets/ship/quiet/` (`stand-fall.png`, six frames of 96 x 64; `quiet.json`),
  sources and jobs in `assets/source/quiet/`; her clips `creep-tiptoe` and `creep-reach` in her sheet
  (`assets/source/her/creep-tiptoe/README.md`); the librarian's `flinch` in the people's sheet.
- **Code:** `src/world/quiet.js` (`setupQuiet`, `quietAfter`, `updateQuiet`, `quietBeat`), mixed into the Story;
  `QUIET` in `src/config.js`; the beat is `custom`. One clock on the scripted update. The Story's `ropeIntoDoor` is
  gone; `leaveAjar` stays.

## What changes for the player

- He is found asleep on the return trolley, by the librarian's desk, not on a reading table 12.6 m forward of it.
- She is held 2.6 s (it was 3.5 s), and all of it is seen: the rope, the door and he are in one picture.
- The trolley takes no book before the beat: she cannot come within 64 px of it without the scene.
- The door stands open into the stair lobby, the stand lying in its doorway; the card "QUIET PLEASE" lies flat and
  can no longer be read.

## Checks

- `region2.quiet` (new, 33 checks): his place, the 64 px line, the librarian's shush, the tiptoe's pace, her stop at
  39 px, his wake and leap against her reach's frames, his depth, the stand and its card, the door opening before his
  nose is at it and 45 px inside the picture, the librarian's start, held under 3 s, the after-state, through the door
  into region 3; a jump across the line; a reload; every lock open.
- `region2` (the beat moved before the trolley's checks: her first coming to the trolley is the scene now), `golden`,
  `boot`, `highlight`, `lang`, `throw`, `region3` pass; `sound` passes run alone (it failed once among six at a time, in
  real time, on her footsteps; with and without this work it passes alone). `check_overlaps`: 0.
- By script: a dash across the line (the scene takes her out of it), a tray in her hands, the place afterwards from
  both sides of the door and with her on the stand, the decks above and below.
- Not run: the whole suite.

## Generations

| What | Tool | Job or group | Cost |
|---|---|---|---|
| Her tiptoe, `creep-tiptoe` | animate_character, skeleton-v3, poses | group `d327f239-a1ed-4f5e-b898-2e2b48927a0a` | 3 |
| Her reach, `creep-reach` | the same | group `83b7dde0-282d-48c0-a124-0c8362a689e8` | 3 |
| The librarian's `flinch` | the same, her character `c7f368e7` | group `975b7e84-ac0c-4aef-828b-e3f3a16bf7ab` | 3 |
| The stand's fall, 8 frames, 96 x 64 | animate_image_pixminimax, start and end pinned, seed 7 | `f90b9b1a-e889-4320-ba12-3c0a87acd2c2` | 1 |
| The stand lying, redrawn (not used) | edit_image_pro_flash | `1898f3ac-217d-42b0-b727-d5964f5231e4` | 5 |
