# Near-catch 4 remade: the log

The fourth remake by `docs/sequence-remake-plan.md` (after `docs/near-catch-1-remake-log.md`,
`docs/near-catch-2-remake-log.md` and `docs/near-catch-3-remake-log.md`). Branch `near-catch-4`, worktree
`../mysterious_female-catch4`, port 8005; started from `near-catch-3` (approved, not yet merged to `main` when this
began; it holds near-catch 2 and the latest `main`, `18e6035`).

## The prompt, word for word

> Let's tackle the next near catch in the same method

("The same method": the remake plan, as for near-catches 1 to 3. The next is 4, the linen room's.)

## The scene as it was (recorded 2026-11-24)

Deck 9, the linen room (`linen`, 240 px wide, one screen): its door at its aft end, the laundry cart in her way, the
forward rack with Bumbot asleep on its bottle shelf (36 px up), the shaft's mouth with its cover on the forward wall
(its floor 32 px up, the cart's rim's height). **A scene of the user's own design of 2026-11-23** (the shaft's remake,
`docs/shaft-remake-log.md`): "he is off into the vent the moment she, or the laundry cart she pushes, all but touches
him; her walk-up and reach are not played"; the cover's fall is the user's of 2026-11-24 ("let it fall flat on the
ground, rotating while falling").

Played with real keys from `?play&at=linen`: pushing the cart at him (E at its end, then forward), hopping over the
cart and running to him, along the cart's rim; her cry (D) and a throw (F) from the door with the dash learned
(`&did=bb1,bb2,bb3&tangerines=infinite`). Recordings in the scratch folder (`out/old-push`, `old-jump`).

What happened: the cart's front (or her body) 2 px from his body's columns, and in the next frame he was upright in
a leap (`bumbot-leap`, 320 ms) to the mouth, its cover still on; there the cover began its fall (420 ms, a clang, a
hop) and he went in on his belly (`bumbot-crawl`, 420 ms); the flag `bb4` (crawling learned) as he was gone.
**0.8 s in all, and she was never held:** she pushed on, or ran on.

### Faults

1. **Too fast to follow:** 0.8 s, while she goes on pushing; nothing gives the player a moment to see it.
2. **He never wakes:** asleep in one frame, upright in mid-leap in the next. His `wake` clip (made since, with the
   rest of him) is not used.
3. **She does not react at all:** she pushes on through it; on foot she runs on the spot at the forward wall.
4. **The order at the vent:** he is in the mouth while its cover is still on it; the cover falls after he has passed
   through it.
5. **On foot (over the cart at a jump):** she runs through him as he leaps, and the cover falls through her and
   lands across her feet, drawn in front of them.
6. **The line is a touch (2 px):** pushing, the cart's towels are at his nose before anything happens, and nothing
   she can see wakes him.
7. **Her cry does not wake him:** «Кісюнічка!!!» 100 px from him in a small steel room, and he sleeps on. A thrown
   tangerine neither.
8. **Crawling is learned here and never explained** (the rule: every new mechanic explained once): there is no hint
   for it (`hint.dash` has one since near-catch 1).
9. **The cover ends where the cart must park:** the cart rolls over it with no bump and stands on it (5860 to 5896
   under a cart at 5862 to 5906); pale on the pale floor, it is hardly seen there.

### What hangs on the scene

- The flag `bb4`, which gives `verb:crawl` (`FLAG_GIVES` in `tools/population.py`); the world's `vent_cover` (until
  the flag) and `vent_cover_down` (after it); the crawl into the mouth asks for `bb4` (`src/world/world.js`).
- The cart `cart_linen` and its flag (at the mouth); she stands on its rim (32 px), level with the shaft's floor.
- The shaft's sequence after it (approved 2026-11-23/24): untouched.
- Tests: `region4` (the beat by the cart, then the cart to the mouth, the rim, the crawl), `golden`, the lock check
  ("no crawling into the shaft before the beat"), the shaft's case by the parked cart, `linen`.
- Documents: `GAME_DESIGN.md` (region 4's row, the linen room's text, the beats' table), `docs/population.md` §9
  item 5, `docs/progression.md` step 13.

### Its reach

The whole room is one screen (240 px of 480), he, the cart and the mouth all in view from the door: nothing is at
the screen's edge. From the door to him 117 px; the cart starts 29 px from his body.

## The structure, settled with the user (2026-11-24)

Offered: a scene held for about 3.5 s (he wakes, they look at each other, she climbs the cart and grabs for him, he is
off by the cover, she shrugs), with three questions (her grab or only a look; a hint for crawling; the cover left or
shoved by the cart). The user's answer, word for word:

> From your list of faults, let's address only the following:
> 4, 8
> As for the cover, let it just lie lower on the floor, but the cart and the player are still obscure it as now.
> Let's make the scene play like this:
> 1. The laundry cart has stack of pillows on top of it. We cannot jump past it, or on top of it.
> 2. We only have to push it.
> 3. When we push it, Bumbot jumps (like now), the pillows scatter, and we are able to jump on top of the cart and enter the vent

And, on seeing nothing yet but while the stack was being roughed on the cart with its towels:

> Use this cart, but empty. Don't put the pillows on top of the cart linen

## Decisions

1. **Only faults 4 and 8 are mended** (the user): the order at the vent, and crawling explained. The scene stays as
   short as it was and she is not held: he never wakes first, she does not react, her cry does not wake him, the line
   is still a touch. Those are the user's to leave.
2. **A stack of pillows in the cart, too tall to hop** (the user): four plump hotel pillows, their top 76 px over the
   floor (her jump's 68), and the cart's body a wall to the ceiling while they are on it, as the steward's jammed
   trolley is. So she cannot reach him on foot, and fault 5 (running through him, the cover across her feet) cannot
   happen any more.
3. **The cart is the empty one** (the user: "Use this cart, but empty"): `thing:laundry-cart-empty`, in the atlas
   since the pillows' delivery, the same cart without its towels. The pillows sit in its tub, their bottom 3 px under
   its rim.
4. **His leap as now, and it scatters the pillows** (the user: "Bumbot jumps (like now), the pillows scatter"): as he
   springs up off the shelf beside the stack the top two pillows are knocked off and fly aft in a high arc, over her
   and past the door, to land one on the other in front of the aft rack; the lower two ride the cart 0.7 s more and
   slide off behind it, to lie low on the floor. All of them are behind her as she walks. Mine: the cause is his spring
   beside the stack, the first pillows moving 70 ms after he does.
5. **Where they lie, and why not one heap:** a single heap of four (two tries, 31 px tall) lay straight in front of
   the laundry chute's hatch and hid its lower half, handle and all, and its aft end ran across the door's frame. So
   they are scattered: two low under the hatch (17 px at most; the hatch's foot is 11 px up, its handle 19), the door's
   whole span clear, two at the room's aft end; nothing of them past the aft wall.
6. **The cover lies 4 px lower** (the user: "let it just lie lower on the floor, but the cart and the player are still
   obscure it as now"): on the floor's own strip, not at the wall's foot; still behind the cart and her.
7. **The order at the vent (fault 4):** the cover begins its fall as his fore paws reach it (140 ms into his leap), not
   as he is already in the mouth; he goes in over it as it drops away under him. (A 120 ms hang at the lip was tried
   on the storyboard: it stood him on nothing.) Its fall itself is the user's of that morning, untouched.
7a. **The cart bumps his shelf** (mine, for the pillows' places): he goes with the cart's front 6 px past his nose, not
   2 px short of it, 0.2 s later than before; the pillows then land 8 px further forward, clear of the door.
7b. **The pillows in the cart move with the game's own cart, those in the air stay where the room has them:** the clip
   is cut into two layers, and paced (14.3 frames a second) so that the cart, pushed at her 40 px a second, is where
   the clip's own cart stood as the last two pillows leave it.
8. **Crawling explained once (fault 8):** a plate over her as he is gone, "↓ to crawl" (`hint.crawl`, both languages,
   the controller's too), as "D to dash" ends near-catch 1.
9. **His leap's end and his crawl 6 px higher** (the user, at the preview: "Shift Bumbot's crawl higher, it is shown
   from below the entrance"): his belly was at 816, the shaft's floor for her, while the mouth as drawn opens from 779
   to 811 and its box ends at 814: he showed under the box, his paws out below it at the wall. At 811 he is inside the
   opening. (So it was in the game before this remake too.)
10. **The holes in the mouth's near side are filled** (the user, at the preview: "in some frames, on the entrance,
    when Bumbot crawls inside, a black pixel shows"): the near side's picture has 17 px that are empty inside its
    outline, where the wall shows through; one of them, at 5855, 806, is at his height, and he showed through it in
    29 of the crawl's 44 moments. Each is filled with what the room shows there, so nothing changes at rest and
    nothing behind the box shows through it, her neither (`tools/build_shaft.py`).
11. **"Build it"** (the user, on the preview with the crawl raised and the hole mended).
12. **The hint only when she is up on the cart** (the user, as the build ran: "The tooltip has to show (after the
    Bumbot's escape) only when we jump on top of the cart"): the first time she stands on the cart once he is gone,
    wherever it stands, and never again (the flag `hint_crawl`). Decision 8's moment, as he goes, is dropped.
13. **The push goes on by itself for 0.7 s** (mine): from his leap until the last two pillows are off the cart, whatever
    the keys (`pushHeld`), so that they land where they were made to; she is in her push all through, as before.
14. **A game loaded after the beat, the cart not yet at the mouth** (found in the self-check): the cart stood back at
    its start, on top of the two pillows on the floor. It stands where the last pillows left it.
15. **The shaft's mouth is cut against the room as it was** (found building): `tools/build_shaft.py --mouth` cut its
    pieces by what differs from the room's own picture, which was redecorated after they were made; run now, every
    piece came out another shape. The old corner is kept beside the pictures (`assets/source/shaft/gen/room-corner.png`)
    and the build is exact again; the holes' fill and the cover's place are in it.

## The art (to the preview stop)

About 80 generations. In `assets/source/linen-pillows/` (its README has every job).

| What | How | Jobs |
|---|---|---|
| The stack on the cart | a flat rough in the room's own picture, redrawn (`edit_image_pro_flash`, 128 px), cut by what differs | `dab040e7` (used), `2e423939` |
| A heap behind the cart, three takes | roughs on a green set with the cart flat blue, redrawn | `7f95232e`, `907487b5`, `3a7998a7`, `fb97dfe8`, `5a35d40d` (none used: the heap hid the hatch) |
| The topple into a heap | PixMiniMax, both ends pinned, 16 frames | `462fa164`, `8884861f`, `59f34787`, `6d1a54ff`, `a696287d`, `2923c0bf`, `a0c4d41a`, `ed8ac397`, `285859da`, `d85db23e`, `547c27de` (none used) |
| The pillows scattered (the end picture) | a rough on a 208 px green set, redrawn | `3dcda9e2` (used), `4edf67df` |
| The scatter | PixMiniMax toward it, 16 frames, 208 x 128 | `c4bcc5b4` (used; its smeared frame 1 left out), `22c32592`, `4d5f20ae`, `5e71d393` |

## How it is built

- **The pillows:** `tools/build_linen_pillows.py` cuts the clip into `assets/ship/linen-pillows/`: `ride.png` (the
  pillows still in the cart, 10 frames, in the cart's own px), `free.png` (those in the air and on the floor, 16
  frames, in the room's px), `near.png` and `far.png` (as they lie), `pillows.json`. In their own colours.
- **The scene:** `src/world/linen.js`, mixed into the Story (`setupLinen`, `updateLinen`, `linenGoes`, `linenScene`,
  `linenHint`, `coverFalls`); `PILLOWS` in `src/config.js`. One clock from the moment he goes: his leap and crawl
  by it (they were tweens), the cover's fall begun at 140 ms, the clip's frame by it at 14.3 a second.
- **The cart:** `thing:laundry-cart-empty`; `PUSH_WALL` in `tools/population.py` makes it a wall to the ceiling until
  `bb4` (`wall` on the pushable, `unwall()` in `src/world/world.js`); the stack is one of its pictures while it is on
  it (shown, pulsing and moved with it).
- **The vent:** `tools/build_shaft.py`: `COVER_LOW` 4, the near side's holes filled, the room's old corner.
- **The words:** `hint.crawl`, `hint.crawl.pad` in both languages.

## Checks

`region4.pillows` (40 checks, one for each decision: the empty cart, the stack, its height, the wall, three jumps at
it, the bump, the cover before he is in, his height in the mouth, the first pillows, the riding ones on the cart
exactly, the push held, where the four lie against the door and the hatch, the cover 4 px lower, no hole in the mouth,
the cart hers after, the hint on the cart and only once, ten seconds still, a load after the beat). Run with it:
`boot`, `region4`, `golden`, `linen`, `highlight`, `lang`, `deliveries`, `region1`, `sound`: all pass;
`tools/check_overlaps.py`: 0. The whole suite was not run.

Looked at enlarged in the game: the pulse at the cart (the stack pulses with it); the end from the door; her on the
cart with the hint; her on hands and knees into the mouth, before and after (the same, less the dot of her that
showed through the box); the room loaded after the beat; the corridor outside.
