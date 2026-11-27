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

## 3. The structure

Proposed 2026-11-27 with four questions: (1) why she pulls (her own idea with Bumbot on the horn; a valve it takes two
to work; a treat he waves her to), (2) the cascade in a live panel under the top while the horn sounds, or by cuts,
(3) whether the bow's part is kept, (4) which faults are mended. Asked first: "Is this scene optional? How do we get
there?" (it is not: the Officer's card, the parasol and the sunbed's block all hang on it).

**The user's answers, word for word:**

> 1. Remove the engineer from there. Is this path is not optional, that means that one way or the other we will
> eventually end up there on the funnel. Let her just see Bumbot on top of the horn, the cord, and the move is quite
> obvious from there. This makes the scene like a near catch, and I think it fits.
> 2. Let's try to implement your recommendation and see how it works in game. Make it well.
> 3. Do as you would.
> 4. Ok

## 4. The beats (the scene's clock, `HORN` in `src/config.js`; ms from her fist closing on the handle)

| At | What |
|---|---|
| before | Nobody on the top. Bumbot sits on the horn's top bar; the cord's rope and handle pulse where E would pull |
| 0 | She pulls (her `pull`, the handle in her fist) |
| 320 | The horn: one prolonged blast of 6.3 s. The top shakes hard for 0.45 s, then trembles; rings; the pipes cough |
| 320 to 1,200 | Bumbot shoots up off the bar 34 px and 22 px forward (`fright`), comes down on the platform 58 px forward of her, crouches, runs off down the stairway |
| 560 | She lets go and claps her hands over her ears (`ears`), hunched, until it stops; the handle swings back up |
| 1,300 | The panel opens under the top: the sun deck, live |
| 1,600 | The officer, on his knees at the loungers, is off them into the air (`start`); at its top his card leaves his pocket and comes down where it will lie (the world's own card, shown from now), a sparkle |
| 2,000 | The old lady starts (`bolt`), is up, and hurries off forward with her book (`hurry`); her sunbed, parasol, bags and towel stay |
| 3,100 | Bumbot comes through from aft, past the officer, over the sunbed and what stands at its foot |
| 3,430, 3,750 | The officer turns after him; charges; over the sunbed in his stride (`hurdle`); gone forward |
| 4,700 | (Unseen: the windscreen's six gulls set off aft) |
| 5,100 | The panel shuts and opens on the bow: the kids' pool |
| 5,560 | Its six gulls go up; the windscreen's six cross the picture's sky |
| 6,460 | The panel shuts; 6,620 the horn stops |
| 6,770 | Her hands come down; she looks up at the empty bar |
| about 7,960 | She is hers (the flag `horn`), and shrugs |

8.1 s from E (it was 12.3).

## 5. The decisions

1. **The engineer is off the top** (the user). He stays at his door once he has had his coffee: he unhooks the
   ladder's chain and walks back to it (`npc_engineer_break`); `npc_engineer_cord`, `npc_engineer_read`, his horn
   cloud and `engineerBook` are gone. **His book (9) stands against the forward end of his toolbox on the top**, a
   pickup: mine to place, since nobody is up there to lend it. To be confirmed by the user.
2. **The pull is hers.** E at the cord from the first moment she is up; the cord pulses (its rope and handle are the
   thing's pictures now).
3. **The cascade in a live panel** (`src/inset.js`): a second camera on the same world at the game's own pixel size,
   with a sky of its own laid out for it (the backdrop takes a camera), a frame of a light rim and a dark edge, opening
   from its middle row. Under the top's floor, where the screen is the funnel's dark side: it covers nothing. Deck 12 is
   held open for it (`viewOverride`), which changes nothing on the top.
4. **One prolonged blast as long as the scene** (6.3 s), so that everything it sets off happens while it sounds; she
   holds her ears through it, which is why she does not go after Bumbot.
5. **Bumbot ties the places together and gives the officer his reason:** off the horn; through the sun deck, where
   the officer goes after him (he is on the bridge after him in near-catch 6). He is not shown at the bow: he is not
   there yet.
6. **The old lady leaves everything** (the sunbed, the parasol, her bags and towel): they slid along the floor beside
   her. They stay for good, behind her as the sunbed is, and are no block. Mine; to be confirmed by the user.
7. **The bow's part kept, short** (the user: "Do as you would"): one shot of the kids' pool; the windscreen's six,
   1,000 px forward of it, are sent aft across its sky.
8. **The shake** no longer shows past the sky's edge: the sky is laid out 8 px wider than the screen all round.
9. **The officer's and the old lady's clips are a strip of their own** (`assets/ship/horn/clips.png`), each in the
   colours of its own built sheet; hers and Bumbot's go into their sheets.

## 6. The art

`assets/source/horn/README.md` has the jobs: five clips, each from the built sheet's own frame on green, each the
first or second try. 7 generations (8,104 left before them). Checked frame by frame: the officer's start had dust
strokes under him and the hurdle a hurdle drawn in, both cut off as loose pieces; the old lady's steps drifted 1 to 3
px and are set on their lowest pixel; one ears try covered her face.

## 7. The self-check (before the user saw it)

- **The officer's head left the panel's top** in his start and in his hurdle: half and 0.7 of each clip's own rise is
  kept, and the panel shows 85 px over the floor (the floor 7 px over its bottom edge).
- **Bumbot's fall crossed the trumpets' bells:** he goes 22 px forward as he goes up.
- **Bumbot on the sun deck was drawn in front of its railing,** the people behind it: he is on their layer.
- **He and the officer took off inside the bags at the sunbed's foot:** both leave the floor aft of them (70 and 74 px
  from the sunbed's middle).
- **The old lady's last two frames stood 11 px in the air** (she sits that much over the floor): set down in them.
- **The bow's picture had no water in it** with the floor so low: it looks 22 px lower.
- Walked: `?play&at=funnel&did=engineer` from the stairway's side and from the cord's aft side; E in the air (nothing);
  the cord again (a toot). `region8` with its new case `region8.horn`, `golden`, `finale`, `region9`, `lang`,
  `highlight`, `keeps`, `boot`, `sound` pass; `check_overlaps` 0. The whole suite was not run.

Not mended: the card is the world's own 8 px card (a sparkle and its glint mark it); fault 11's book is not shown in
the scene (it appears with the flag, as the pickups do).

## 8. The play stop, round 1 (2026-11-27)

**The user, word for word:**

> Ok, I don't like the panels.
> Let's revert to the view. Keep the new animations
> 1. Keep the moved engineer that still wants his coffee.
> 2. The new book location is fine.
> 3. Regenerate the bags and show me the candidates (also on screenshots in game).
> I want the old sequence view, but polished. It is fine that the horn blow ends. What moves things around is running
> Bumbot, not the horn (that's why the old lady's bags stay in place).
> Let's see what we can improve

And, while it was being rebuilt: "Wait. If the engineer still wants his coffee, then let him give us his book when we
bring him the coffee. Because a lot of books are picked up."

**Decisions:**

10. **No panel** (the user). `src/inset.js` and the backdrop's own camera are gone. The scene is three shots of the
    camera itself: the top, the sun deck, the bow, and back to her.
11. **The shots are cut to, not panned to** (mine: the old pans crossed 12,000 px in 5.1 s, twice through empty sea
    and sky). Each shot's floor is where the top's own floor is on the screen, so the horizon holds across a cut. To be
    judged by the user in play.
12. **Bumbot is the cause of everything** (the user). The blast is 1.5 s and is over before the first cut. On the sun
    deck all is quiet for 0.3 s; then he comes through: the officer is off his knees as he shoots past, the old lady's
    book goes up as he is in the air over her, the officer goes after him. At the bow the kids' pool's gulls come over
    ahead of him, and the windscreen's six go up one by one as he runs along their rail (under it he was behind the
    bulwark: unseen).
13. **The engineer hands her his book with his thanks for the coffee** (the user), before he waves her up; the pickup
    by his toolbox, a few hours old, is gone again.
14. **The old lady's bags stay** (the user confirmed the reason: Bumbot moves things, the horn does not). **They are to
    be generated anew:** six candidates made as map objects at 32 px and brought to the game's size by each pixel's
    commonest colour (a straw tote, a canvas bag with a flower, a burgundy handbag, a teal duffel, a stack of towels,
    a striped towel hung over the sunbed's foot), shown alone beside her and in the running game in three sets. 6
    generations. Awaiting the user's choice; the game still has the old ones.

**The clock now** (ms from her fist on the handle): 320 the blast (1.5 s); Bumbot off the bar and away by about 1,500;
her hands down at 1,970, she turns the way he went; 2,550 the cut to the sun deck; 2,870 Bumbot in; about 3,050 the
officer's start and his card; about 3,390 the old lady's start; about 4,400 the officer's charge, 5,070 his hurdle; the
deck as they left it for 0.4 s; about 6,300 the cut to the bow; 6,600 Bumbot along the rail; about 8,150 the cut back
to her; she shrugs. 8.8 s from E (the first build: 8.1; the old scene: 12.3).

`region8` with `region8.horn` (its checks now: the four shots in order, each a cut; the camera follows her again),
`golden`, `finale`, `highlight`, `boot` pass; `check_overlaps` 0.

## 9. The play stop, round 2 (2026-11-27)

**The user:** "1. Set 2  2. I liked the pans". And, while it was being built: "How long was the horn blow
previously?" (1.5 s in the old scene, 0.5 s the toot; 6.3 s in the panel's build; 1.5 s again now.)

**Decisions:**

15. **The camera pans between the places again** (the user: "I liked the pans"; decision 11's cuts are out), as long as
    the old scene's did: 1.5 s to the sun deck, 1.7 s on to the bow, 1.9 s back to her, eased in and out, by the
    scene's clock. It is at each place 0.2 s before Bumbot comes into it. On its way to the bow it passes the officer,
    still running; Bumbot, ahead of it, is not shown on the way.
16. **The old lady's things are set 2** (the user's choice of three): her canvas bag with the flower at the sunbed's
    head, her burgundy handbag beyond it, her striped towel hung over the bed's foot, her teal duffel. The handbag
    stands 21 px further forward than in the picture shown, so that her two tangerines (after her mojito) lie between
    the two bags, not under one. Built by `tools/build_horn.py` (`BAGS`) into `assets/ship/horn/lady-*.png`; the
    wicker basket, the green duffel and the code-drawn towel are out of her sunbed.

**The clock now:** 2,100 the pan to the sun deck; 3,800 Bumbot in; about 6,850 the officer out of the picture; 7,100 the
pan to the bow; 9,000 Bumbot along the rail; 10,350 the pan back; she is hers at about 12,400 plus her step to the
cord: 13.0 s from E (the old scene: 12.3).

`region8` with `region8.horn` (the camera's way: top, sun deck, bow, top, a pan each; five things at the sunbed),
`golden`, `finale`, `highlight`, `boot` pass; `check_overlaps` 0.

## 10. The play stop, round 3 (2026-11-27)

**The user:** "Wait, why Bumbot doesn't run by the pool?" I had moved the bow's picture from the kids' pool to the
windscreen's rail myself (in the old scene he ran across the pool at the deck's height, over the open water: fault 4),
and had not said so. Three ways offered with a picture of him at five spots along the pool (one long leap over the
water; straight across as the old scene; the rail as built). **The user: "2".** And: "the rival jumps a bit late,
Bumbot is already past him, or so it seems at least".

**Decisions:**

17. **At the bow Bumbot runs by the kids' pool, straight across at the deck's height, as the old scene had him** (the
    user's choice). The picture is the pool's (all six of its gulls in it); each gull goes up as he is 30 px from it;
    the windscreen's six, forward of the picture, go up a moment later, unseen. What the user is not asked about is not
    moved: a place in a scene is the user's, and a change of it is a question with a picture before it is built.
18. **The officer is off his knees as Bumbot is still 100 px aft of him** (it was 14): he leaves the floor as Bumbot
    reaches him and is in the air with him directly under; looked at frame by frame at 20 frames a second.

`region8` with `region8.horn`, `golden`, `finale`, `highlight`, `boot` pass; `check_overlaps` 0.
