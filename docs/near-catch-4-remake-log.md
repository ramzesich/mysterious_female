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

## Decisions

(None yet: the structure is with the user.)
