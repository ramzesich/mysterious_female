# Near-catch 3 remade: the log

The third remake by `docs/sequence-remake-plan.md` (after `docs/near-catch-1-remake-log.md` and
`docs/near-catch-2-remake-log.md`). Branch `near-catch-3`, worktree `../mysterious_female-catch3`, port 8004; started
from `near-catch-2` (approved, not yet merged to `main` when this began), which holds the latest `main` (`18e6035`).

## The prompt, word for word

> Let's work on the next near-catch, same approach

("Same approach": the remake plan, as for near-catches 1 and 2.)

## The scene as it was (recorded 2026-11-24)

Deck 6, the Stardust Lounge's stage, 244 to 254.4 m (the deck ends at the stage's aft curtain). Played with real keys
from `?play&at=light6`, walking aft onto the stage, jumping at him, and from behind him (she can only get there by a
jump over him). Recordings in the scratch folder (`out/old-walk`, `old-jump`, `old-aft`).

What happened: 60 px from him (`BUMBOT.noticeReach`) she was taken, walked to 34 px and bent to him; 280 ms into her
reach the rival was added at the forward wing, walked to a "cable" at 245.75 m, tripped, slid onto the trap door at
246.3 m, sank and faded through it, twelve white squares came up; then Bumbot got up, leapt 46 px aft onto the fly
rope at 249.7 m and rode it up, fading out; she straightened, turned to us, shrugged. **Held 4.75 s.**

### Faults

1. **Bumbot can hardly be seen:** black, sat against the black piano in the dark. The stage's one spotlight is 137 px
   forward of him, on a dancer. (The design: "centre stage in the spotlight washing himself".)
2. **She walks through the rehearsing dancers to reach him,** and they dance on through all of it, the woman over the
   open trap door at the end.
3. **The rival appears out of nothing** in front of the forward curtain, 180 px behind her back, and walks through
   the drum kit and the dancer.
4. **He trips on a cable that is not drawn.**
5. **He sinks through the stage's front edge and fades out:** a fade, and his faint figure shows over the floor's
   face under the stage.
6. **The flour is twelve white squares** (drawn in code).
7. **For 2.2 s she stands bent with her hand out and Bumbot goes on washing 34 px from it,** neither heeding the
   crash behind them.
8. **The rope goes up by itself:** nothing hauls it. He fades out at its top.
9. **The lamp starts to swing at the flag:** nothing in the scene touches it.
10. **The dancers vanish from the stage in one frame** at the flag and stand by the front row, 350 px forward.
11. **A jump across the line is not taken:** she lands past him, is held hung 4 px over the floor for the whole scene,
    reaches at him from behind through the piano's stool, and he leaps through her to the rope.
12. **Held 4.75 s** (near-catch 1: 2.4 s; near-catch 2: 2.6 s).

### Its reach against one screen

The stage is 330 px from the forward curtain's outer edge (12,192) to the aft curtain's (12,510): it fits one screen.
The old scene began with her at 12,360 (view 12,091 to 12,571): everything was in the picture; the trouble was that
its first half played behind her back.

### What hangs on it

- **The flag `bb3`:** the trap door open (`showTrap`; her drop into the galley, `world.js`), the stage's lamp let down
  and swinging (`LIGHTS`, gags 12a and 12b), the stage manager's pills bubble and errand (`pills()`, `item_pills`
  in his cabin needs it), the dancers' places (`until`/`after`), the rival on the galley's flour sacks
  (`riv_galley`), the bow at centre stage (`sec_spotlight`, needs it), deck 7's planned second lamp (plan-the-rest
  §7f, 13).
- **Bumbot's own clip for the rope** (`bumbot-rope`, made with the rope in its picture: the catch, his hind paws into
  the loop, a look back down), placed here when he was made again.
- **Tests:** `golden` and `region3` wait for `bb3` on the stage; `mishaps.light` starts with it set; two presets set it.
- **Cannot move:** the lamp at 245.9 m and the stage manager at the aft curtain (the user's swap, 2026-11-19), the
  trap door at 246.3 m (its landing on the galley's sacks).

## Decisions

1. **The staging** (the user, on the structure's picture and its proposal: "Do as you planned and recommend"): she is
   taken at the stage's forward edge; Bumbot washes at centre stage in a spotlight of his own, the rope's loop over
   him; the rival comes out of the forward wing, leaps at him under the hanging lamp, his net catches the lamp, he
   drops through the trap door; the lamp and the loop are the two ends of one line, so the lamp comes down as Bumbot
   goes up; the lamp is left low and swinging.
2. **Her part** (the same answer; of two offered, the one recommended): she tiptoes toward him, the rival spoils it,
   she starts back and watches, looks up after Bumbot, shrugs. One thing at a time.
3. **The dancers afterwards** (the same): they stay where they rehearsed, by the piano, stopped. Nothing vanishes.
4. **The stage, its props and the people here made again** (the user: "perhaps it is best to regenerate both the
   stage, the props and the people here, to fit your plan more. Not sure about the dancers' looks"): the stage was
   rectangles drawn in code. Now one picture, 320 x 128: its left half drawn flat by rule (curtain with a tie-back,
   swagged valance, a lighting bar with lanterns, a star cloth for the Stardust, boards) and redrawn by PixelLab,
   every shape kept; the right half its mirror; the drum kit and the grand piano redrawn in the stage's own light
   from the game's own pieces at their places, pasted in by their boxes. The guitar and the mic stand are gone (the
   mic's cable was the old gag's). The dancers: two new pairs made beside the present one, for the user to choose.
5. **The stage manager sees the cat, then starts sneezing** (the user: "The stage manager has to react somehow to
   Bumbot and then start sneezing"): he no longer sneezes before the scene. As she is taken he starts back and
   thrusts his clipboard at the cat (a new clip, `notice`); when Bumbot is gone he sneezes for the first time, and
   from then every 5 s until his pills.
6. **She is taken in front of the forward curtain, 154 px from him, and the rival comes out of the wing ahead of her**
   (mine, from the first storyboard: taken 20 px past the curtain's edge, he came out from behind it straight into
   her, his net over her head). She ends 76 px forward of the lamp: outside its swing.
7. **The lamp is a picture now** (generated; it was a circle drawn in code), **and the trap door is where its picture
   has the hole:** 246.58 m (it was 246.3), 33 px aft of the lamp.
8. **The loop rises 1.7 times the lamp's drop** (mine): the lamp comes down 44 px to her head's height, as the hazard
   needs; the loop must take him 75 px up, behind the valance. Both move in the same six frames.
9. **When he lets go, the lamp is dragged out aft and swings from there** (mine): the game's own swing (55 degrees,
   3.2 s) starts from the side he fell to, not from a lamp at rest.
10. **The preview stop:** the pieces, a storyboard of eight moments over the room's own picture with the new stage
    laid in, and the same on its clock as a GIF.
11. **The dancers** (the user, at the preview stop, of three pairs: the present one, A in rehearsal clothes, B in show
    costumes): "On B, the male dancer looks like a waiter, the female one is approved." She is B's (a silver dress,
    blue feathers). "Find a better male dancer first": three more made (a blue waistcoat on a bare chest; a silver
    satin shirt with a blue sash; a blue tailcoat and a silver top hat), and **the second is used** (mine: her silver
    and blue, a dancer and nothing else; the other two are kept beside him for the user). Their clips: a salsa basic
    (`dance`), a hop back (`startle`), standing (`idle`).
12. **No piano** (the user: "The stage: remove the piano"): the aft half of the stage is bare boards under the cloth.
13. **The stage manager and the dancers change places** (the user: "switch places: the stage manager and the
    dancers"): he at 248.5 m, between Bumbot's spot and the dancers, turned to them, so his back is to the cat until
    the scene; they at 249.3 and 250.25 m, he in front of the aft curtain.
14. **The rival's clip is set to his own colours** (mine): on the palette the generator's shades fell on darker
    colours than his sheet's; each pixel takes the nearest of the colours his built frames have.
15. **His run comes out of the wing at his clip's own pace** (mine): 180 px/s (the clip's first frames carry him
    11 px each at 16 a second), his run's frames at 25 a second (its planted foot goes back 7 px a frame).
16. **In the air across the line at any height** (mine): the balcony's front on deck 7 is over the stage's forward
    end, and she can hop it before the scene; taken as she crosses the line, she comes straight down in front of the
    curtain. Taken only near the floor she landed under the lamp, and it struck her as she was freed.
17. **The stage and the theatre round it brought together** (the user, on playing it: "Overall, I like it. ... The
    stages pops out too much. We need to remove a bit of a wash of the props that surround it, and add a bit of a
    wash to the stage, so that everything meets in the middle"): the theatre's own pieces (its seats, its audience,
    its speakers) washed 6%, a twin of their own, `-w6` (they were at 12%; the doors beside them follow, by the
    highlight's rule); the stage's picture, its valance and its hatch washed 12% toward the same wall colour
    (`STAGE_WASH` in `tools/build_stage.py`; it was in full colour). The lamp, the people, the rival's clip and the
    flour are not washed. Six strengths were drawn in the running game (`wash-options.png` in the scratch folder: now,
    6/6, 6/12, 0/12, 6/18, 0/20); 6/12 is in (mine), the others shown to the user by letter.
18. **Slower, with holds where a hold is natural** (the user: "The scene plays too fast in the game and it's hard to
    grasp what just happened. Perhaps, this is the case where things have to be a bit slower and with some delays,
    but in proper places, not to break transitions, where they should be flowing"): 4.35 s (it was 2.65 s). One
    thing after another: the stage manager's start (0.15 s) stops her mid-step (0.35 s) and brings Bumbot's head up
    (0.4 s); the dancers stop (0.45 s); only then the rival (0.75 s), she starts back, Bumbot leaps for the loop;
    the rival's clip on a schedule of its own steps (`STAGE.clip`): its run and its leap at their own pace, then he
    dangles on the lamp, legs kicking, for 0.6 s (its frames 6 and 7, twice over), then the lamp comes down in 0.5 s
    (it was 0.3 s) with the loop going up; the hatch and his fall as they were; a breath, and she looks up 0.6 s
    before her shrug. What flows was left flowing: his run into his clip, the clip's own leap, the lamp's let-go
    into its swing, the fall.
19. **The stage at 18%** (the user, of the six strengths, the game then at 6/12 and the dancers' choice still open
    beside it: "D"): read as the wash's D, the props 6%, the stage 18%; the male dancer is D too, and stays.
    `STAGE_WASH` 0.18.
20. **The stage back at 12%; the male dancer is D** (the user, told the wash had been read from the "D": "No"; asked
    which wash: "Back to 12% (B)"): the "D" was the dancer's letter. The props 6%, the stage 12%, as in decision 17.
    (Mine to learn: two open choices must not share their letters.)
21. **Approved** (the user, on playing it at 4.35 s with the stage at 12%: "Approved"). The documents and the
    lessons are brought to it; merged only on the user's word.

## How it is built

- **Data:** `BEATS["bb3"]` at centre stage (247.29 m); `TRAPDOOR_M` 246.5625; `STAGE` (the wing, the rope, his
  lantern); the stage manager and the dancers' places, the dancers' places afterwards the same; the stage's props
  out of the map (the drum kit is in its picture; the guitar, the mic stand and the piano gone); the place `stage`.
- **Art:** `tools/build_stage.py` to `assets/ship/stage/` (the stage's picture, its valance again, the lamp, the
  hatch shut and open, the rival's clip, the flour, `stage.json`), sources and jobs in `assets/source/stage/`; her
  clips `start-back` and `look-up`; the stage manager's `notice`, the rival's `charge`, the two new dancers, in the
  people's sheet.
- **Code:** `src/world/stage.js` (`setupStage`, `stageAfter`, `updateStage`, `stageBeat`, `drawRope`), mixed into the
  Story; `STAGE` in `src/config.js`; the beat is `custom`. One clock on the scripted update. The ship scene's
  `drawStage` lays the picture; `SwingLight` hangs the lamp's picture and can be held and let go (`hold`,
  `release`). The Story's `rivalTrips` and `upTheRope` are gone; `sneezes` starts with the beat.

## What changes for the player

- The stage looks like a stage; Bumbot is seen from the house, in a spotlight at its centre.
- She is taken as she comes to the stage, not 60 px from him, and held 4.35 s (it was 4.75 s), every part of it seen.
- The stage manager no longer sneezes before she has been there.
- The dancers and the stage manager stand elsewhere; the dancers stay on the stage afterwards.
- The trap door is 13 px further aft; the piano, the guitar and the mic stand are gone.
- Where the scene leaves her, the swinging lamp and the open hatch are between her and the stage manager.

## Checks

- `region3.stage` (new, 49 checks: with the theatre's wash, her stop mid-step, Bumbot up before the rival, the rival's
  dangle and the lamp's slow drop): the stage's picture and what is not on it, his place, the loop, the lantern, the
  hatch, the lamp, the people's places, no sneeze before; the 154 px line, her tiptoe, the stage manager's start, the
  rival out from the proscenium's edge and ahead of her, her start back, the dancers stopped, the whole stage in the
  picture, Bumbot in the loop before the net is on the lamp, the lamp held behind the net, the loop's rise against
  the lamp's drop, the hatch, the lamp let go, nothing of Bumbot over the stage's top, the flour, the first sneeze,
  held under 3 s, the after-state, nine seconds standing where it leaves her; a jump across the line; off the
  balcony; a reload.
- `region3`, `golden` (their steps on the stage changed to the new places), `boot`, `highlight`, `lang`, `region2`,
  `mishaps` but one pass; `sound` passes run alone (among six at a time it failed once on her footsteps, in real time, as it did in near-catch 2). **`mishaps.things` fails on deck 9's sprinkler, and fails the same on the branch
  this one started from:** not this work's.
- `check_overlaps`: 0 (the valance over its own picture is listed as meant).
- By script: a dash across the line; the scene with her hands not free; the stage from the balcony, from deck 5
  under it, from outside. From the balcony deck 6's shell windows show faintly over the theatre: so they did before.
- Not run: the whole suite.
