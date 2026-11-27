# The horn's scene remade: the log

The seventh sequence remade by `docs/sequence-remake-plan.md`. Branch `horn-scene`, worktree
`../mysterious_female-horn`, from `main` at `203fd0f6` (2026-11-27). Scratch pictures and scripts (not in the
repo): `%LOCALAPPDATA%\Temp\bumbusik-horn\`.

## The user's prompt, word for word (2026-11-27)

> Let's apply the sequence remake plan to the scene at the funnel: when she has to blow the horn, and what it
> triggers, until the scene finishes and the camera and controls are returned to player.
> At first, please remind me briefly, what the idea behind this sequence was. Why can't the guy standing there blow
> the horn by himself

## 1. What the idea was (the answer given)

- **The story** (`docs/progression.md`, `GAME_DESIGN.md` §6.1.3, region 8): the engineer cannot leave his post for a
  coffee; she brings him one; in return he takes her up the funnel and "lets her pull the cord".
- **The design** (§6.1.10): "one blast that changes three places she knows", shown from the top by the camera:
  Bumbot off the horn and away to the bow; the security officer on the sun deck jumps, drops the Officer's card and
  runs for the bridge; the old lady bolts, her sunbed no longer a block, her parasol (the glide) and her book left;
  the gulls off the bow.
- **Why he does not pull it himself:** no document says. Nothing says he cannot; nobody in the story needs the horn
  sounded; everything it opens is an accident of the blast. In the game he stands 2 m aft of the cord with a thought
  cloud of a horn (the popups' sign for a wish), does nothing as she pulls, and does not react to the blast.

## 2. The scene as it is (recorded 2026-11-27)

Recorded with real keys on the stepped clock, a frame every 0.1 s, from `?reset&play&at=funnel&did=engineer` (and
`did=engineer,lady`, from the cord's aft side). Her only way up is the stairway on the funnel's forward face: she
arrives at the top's forward end facing aft, the cord (9364 px) first, the engineer (9468) beyond it, then the
toolbox (9562) and the telescope (9710). E works only on her feet, hands empty, once `engineer` is set.

### Its clock (seconds from E)

| From | To | What |
|---|---|---|
| 0.0 | 0.3 | she steps to the cord and takes the handle |
| 0.3 | 1.8 | the blast: the screen shakes, rings leave the trumpets, the pipes cough smoke; Bumbot leaps off the horn's bar and is across the pipes and off the screen's forward edge by 1.0 |
| 1.8 | 3.3 | the camera goes to the sun deck: 2,566 px forward and 644 px down in 1.5 s; for 0.8 s of it the screen is sea and sky |
| 3.3 | 6.0 | the sun deck: the officer snaps from his knees to standing, jumps (3.65); "!" over the old lady; Bumbot across (3.8 to 4.2); the card out of his pocket; he walks forward and over the sunbed; she bolts with her bags; the deck stands empty from 5.3 |
| 6.0 | 7.7 | the camera to the bow: 3,467 px in 1.7 s, past Champs, the wedding's lobby and the chapel, each cut open |
| 7.7 | 10.4 | the bow: Bumbot across the kids' pool (7.8 to 8.2), its six gulls up (8.1); nothing from 8.8 |
| 10.4 | 12.3 | the camera back to her: 6,033 px in 1.9 s, sea and sky again |
| 12.3 | | she is hers; the flag `horn` is set here |

### The faults

1. **Nobody has a reason for the pull.** The engineer's cloud says he wishes the horn sounded, he stands beside its
   cord, and she pulls it. He makes no sign to her before, does not cover his ears or flinch during, and does nothing
   after.
2. **The blast and what it sets off do not happen together.** The horn sounds from 0.3 to 1.8 s. The officer jumps at
   3.65 s and the old lady at about 3.9 s: 1.8 s after the horn has stopped, at nothing.
3. **Three whip pans, 12,000 px of travel in 5.1 s** (1,700, 2,000 and 3,200 px a second). Twice the screen is empty
   sea and sky; the second pan crosses three cut-open rooms in under a second. 5.1 of the scene's 12.3 s is camera
   travel.
4. **Bumbot is three separate sprites in three places,** each crossing the screen in about 0.4 s. At the top he flies
   270 px through the air across the pipes' tops and is gone within 0.7 s of the pull, while the screen shakes. On the
   sun deck he runs through the old lady's sunbed and her bags. At the bow he runs across the kids' pool at deck
   height, over the open water.
5. **The officer:** from kneeling to standing in one frame; his card is an 8 px tinted square that cannot be read as a
   card; he crosses the sunbed in his walking pose, 42 px up in the air.
6. **The old lady:** her "!" is a text box, not a popup (CLAUDE.md's rule); her three bags slide along the floor
   beside her by themselves; on their way out she and the officer walk through each other.
7. **Empty holds:** the sun deck stands empty for 0.7 s, the bow for 1.6 s, before the camera moves on.
8. **The windscreen's six gulls leave unseen:** they sit 1,000 px forward of the bow's shot, which shows only the
   kids' pool's six.
9. **The engineer changes place and pose in view** as the camera lands back: from standing at 9468 to reading at
   9504, with a book's cloud over him at once.
10. **Dark strips up to 10 px wide at the screen's side edges while the top shakes** (the sky is laid out to the
    screen and the shake moves the picture past it).
11. **Nothing in the scene shows what is now hers to fetch.** The parasol stood at the sunbed before and stands there
    after; the book is not seen; the card is the 8 px square.

Looked at and not faults: the pale rectangle at the screen's bottom right on the top is the funnel's NCL panel; the
camera resting 12 px lower after the scene is its dead zone (40 x 24); the funnel's gulls and gusts act only in play;
the two on the sun deck are taken away out of the camera's view; E in the air does nothing; the second pull is a 0.8 s
toot.

### What hangs on the scene

- **The flag `horn`** (set at the scene's end): the Officer's card on the sun deck (`CARD_SPOTS["off"]`, 134 m);
  `item_parasol` and `book_8` at the sunbed; `npc_oldlady`, her block `blk_oldlady`, `prop_lady_parasol` and
  `riv_sundeck` gone; the bow's two flocks gone; `npc_engineer_cord` gives way to `npc_engineer_read` (book 9);
  Bumbot off the horn (`hornCat`); the sun deck's gusts rock the cake after it (plan-the-rest §7f, 7); near-catch 6
  has the officer on the bridge "who ran up here at the horn".
- **Code:** `horn`, `blast`, `catOffTheHorn`, `cascade`, `pullX`, `cordInFist` in `src/world/topdeck.js`;
  `HORN_FISTS`, `HORN_REST` in `src/config.js`; `sfx.horn`, `sfx.yelp`, `sfx.oh`, `sfx.scrape`, `sfx.scramble`;
  `rumble('horn')`; `smokeBurst` in the ship scene; her clip `her-pull`; the old lady's `bolt` and `fleeing`.
- **Tests:** `region8` (its lines on the horn: the pull, the two shots, the flag, the camera back, the two gone, the
  gulls gone, the toot), the golden path, every scenario opened with `did=horn`.
- **Documents:** `GAME_DESIGN.md` §6.1.3 (region 8), §6.1.10; `docs/population.md` (`sec_horn`, `scn_horn`,
  `riv_sundeck`, `npc_oldlady`); `docs/progression.md`; `docs/progress-decisions.md` (step 8, 11 to 13).

### Its reach against one screen

The sun deck's two are 53 m forward of the cord and 13 m under it; the bow's gulls 72 m further forward. Nothing the
blast sets off can be on her screen. Under the top's floor the screen's lower 105 px is the funnel's dark side.

## 3. The structure (proposed to the user, 2026-11-27)

See the reply of that date: the pull's reason (three ways), the cascade shown in panels under the top while the horn
sounds (`rough-insets.png`) or by cuts, what the bow's part is worth. To be filled in with the user's answers.
