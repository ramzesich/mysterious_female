# Plan: the audit's visual overlaps, to fix

Written 2026-11-15 for another session to carry out (the user: "Write a detailed plan for my other
session to fix your visual overlap findings"). It stands by itself: nothing else has to be read
first, though the findings come from `docs/audit-2026-11-15.md` (committed on branch `the-build`;
a loose copy lies in this folder's `docs/`).

**Five fixes, all small, none needing art or generations.** Three are plain faults (F1 to F3);
two are tidying (F4, F5). Each is a change of a number in the builders' data, then a rebuild.

## 0. Before starting

- **Scope: only what is listed in §1.** Two findings are deliberately left out by the user's
  word (2026-11-15, "Leave as they are for now"): she is hard to see on the Spinnaker's balcony
  (deck 12, 31-44 m) and at the promenade's enclosed ends (deck 6 outside, 100-116 and
  212-231 m). Do not touch those. Three others are not overlaps and are also left out unless the
  user asks: her word's white box has no outline; the evening light tints popups; the party
  cabin's music notes are drawn at the wall's depth.
- **Tangerines stay where they are** (the user, the same day: "Don't change tangerine placement
  meanwhile"). None of these fixes moves one; if a moved thing turns out to stand on a
  tangerine's spot, move the thing somewhere else, not the tangerine.
- Positions are in metres from the bow; a metre is 48 px, x = 480 + 48 x metres. A deck's floor is
  `floor_y(deck)` in `tools/build_ship_map.py` (deck 12 is y 416, each deck below 144 more).
- `maps/ship.json` and `maps/world.json` are **generated**: after any change in
  `tools/population.py` or `tools/build_ship_map.py`, run `python tools/build_ship_map.py`
  (it writes both). If another branch has regenerated them too, regenerate after the merge; do
  not merge them by hand.
- The project's standing rules hold (`CLAUDE.md`): tests muted (the test browser already is),
  never the whole playtest suite unasked, show the result as pictures and stop for the user's
  review, commit by file name (`git add -u` plus new paths, never `-A`).

## 1. The fixes

### F1. The "LOST: CAT" note is hidden behind its own board (deck 4, 190.6 m)

- **What is wrong:** the note's text is not seen at all (measured: 0% of its pixels show). The
  board it is pinned to is the prop `prop_board` and the note is the sign `sign_lostcat`, both at
  (4, 190.6). A sign's text is drawn at the wall's depth (`D.decor + 0.25` = 3.25, the `sign` case
  in `buildEnt()` in `src/world/world.js`); a prop is drawn at `depth - 0.02` = 7.98 (the `prop`
  case). So the board is drawn over the text.
- **The fix (data only):** give the board `back=True`, which draws a prop at `D.decor + 0.11`
  (3.11), under the text, and behind people as a thing on a wall should be:
  `tools/population.py`, `PROPS`:
  `"prop_board": (4, 190.6, "notice-board", 40, dict(back=True)),`
- **Then look at it** (§2): the note is a white box with dark letters, two lines of 4 px type,
  centred 54 px over the floor; the board hangs 40 px up. Check that the note sits on the board
  and not across its frame, and that the board's own drawing (it has a small red notice with a
  cat's shape on it) and the note do not fight. If they do, move the note (`sign_lostcat`'s
  fifth value, its height over the floor) by a few px, or its metre by a tenth, until it lies
  on a clear part of the board. If it cannot be made to read, say so to the user and offer to
  drop the text: the board's art already shows a cat.
- **Do not** change the `sign` case's depth for all signs: plates and posters on bare walls are
  right as they are, and furniture is meant to stand in front of them.

### F2. The wet-floor sign stands behind the lift's door (deck 5, 107.7 m)

- **What is wrong:** `prop_wetfloor` (5, 107.7), the cleaner's yellow A-frame sign, stands inside
  the midship lift's doorway: the lift is at 108.0 m and its two leaves reach about 0.4 m each
  way; the leaves are drawn at depth 8.0, the sign at 7.98. 17% of the sign shows.
- **What is there** (deck 5's midship lobby, 102-110 m): the 5-6 flight comes down to its foot at
  107.0 with the block's rope and its "WET FLOOR" sign across it; the cleaner `blk_cleaner` at
  106.1; the lift's call button at about 106.3 on the wall; the lift at 108.0; the plaque
  "DECK 5" on the wall at 109.0 (56 px up); the wall and door to Shore excursions at 110.0.
- **The fix (data only):** move the sign to the free floor aft of the lift, under the plaque:
  `"prop_wetfloor": (5, 109.2, "wet-floor-sign", 0, dict(until="region:3")),`
- **Then look at it:** the sign must stand clear of the lift's frame on its left and of the wall
  at 110 on its right, and must not hide the plaque (it is low, the plaque is at head height). If
  109.2 is too tight, 109.0 to 109.4 are all candidates. If nothing in that metre looks right,
  drop the prop: the rope's own sign already says WET FLOOR.
- The sign goes with the cleaner (`until="region:3"`): keep that.

### F3. The officers' doors' card readers are on the directory boards (decks 9 and 10, 74.4 m)

- **What is wrong:** on decks 9 and 10 the wall between the forward cabins and the forward lobby
  (at 74 m) has a card lock, `DOOR_LOCKS` `(9, 74)` and `(10, 74)` = `("card", "off", -1)` in
  `tools/ship_layout.py`. The game puts a reader 20 px to the lobby's side of such a wall, 40 px
  up (`reader(b.x + side * 20, b.floor, ...)` in `src/progression.js`): x = 4052. Each lobby of
  decks 8 to 10 also has its directory board, placed by the builder 30 px from the wall, 26 px
  wide, from 72 down to 30 px over the floor (`tools/build_ship_map.py`, the loop under "The
  lobbies: the deck's directory board": `x = col(a) * TILE + 30`; drawn by `drawDirectory()` in
  `src/scenes/ShipScene.js`): x from 4049 to 4075. The reader sits on the board's lower left
  corner. Seen on deck 9; deck 10 has the same numbers.
- **The fix (the builder):** hang the directory further from the wall where that wall has a
  reader on the lobby's side. In that loop, something like:

  ```python
  lock = DOOR_LOCKS.get((deck, a))
  x = col(a) * TILE + (50 if lock and lock[0] == "card" else 30)
  ```

  (`DOOR_LOCKS` is `tools/ship_layout.py`'s; check how the builder imports the layout's names.)
  That moves two boards 20 px aft: from 4069 to 4095 px, the left edge 13 px clear of the
  reader (which is about 8 px wide, centred on x = 4052).
- **Then look at both lobbies:** the board must still be clear of the staircase (the 9-10 and
  10-11 flights' foot is at 75.3 m, about 4096 px; the stairs are drawn in front of the wall) and
  of the exit sign (high up, at 112 px). If the stairs crowd it, the other way is to leave the
  boards and move those two readers instead, but the reader's place is one rule for every card
  wall on the ship, so prefer moving the boards.
- Deck 8's forward lobby has no reader (its wall is a one-way door): leave its board. The midship
  and aft lobbies have none either.
- **The existing checker cannot see this one** (the directory is drawn as shapes, the reader is
  not in its lists): it is checked by eye only.

### F4. People stand over the lobbies' deck signs (three places)

- **What is wrong:** every lobby has a plaque "DECK n" on the wall one metre from the core's aft
  end, centred 56 px over the floor: head height (she is 59 px tall). Whoever stands there for a
  whole region covers it: a fan over "DECK 11" (deck 11, 201 m: `blk_fan_b` at 200.55), the
  wedding party over "DECK 12" (deck 12, 81 m: `amb_wed_bride` at 81.2, a third of the sign
  covered), and she herself whenever she passes.
- **The fix (the builder, one number):** hang the plaques over head height. In
  `tools/build_ship_map.py`, the line that adds `sign-deck-{deck}-{core}` has
  `floor_y(deck) - 56`: make it `floor_y(deck) - 80`. Deck 3's own (`sign-deck-3`, a few hundred
  lines further down, also `- 56`) the same.
- **Then check all of them, not three:** that is 28 plaques (nine decks by three cores, and deck
  3's). At 80 px a plaque is level with the top of a lift's door frame and the lift's own number
  plate, one metre to the side of the lift's middle: it should clear both, but look. Run
  `python tools/check_overlaps.py`: it lists any plaque now lying across a door, a picture or
  another sign, and must list nothing. If a lobby has something at that height (a venue's name
  board, an exit sign), try 76 or 84 before giving up; if no height works everywhere, leave the
  plaques at 56 and tell the user that this one is not worth a special case.
- **Left alone on purpose:** the security officer at his rope on deck 5 (79.55 m) stands over the
  forward lift's small round floor number at 79.4. It is six pixels and he is gone after
  region 1. The fans in front of the aft lift's door on deck 11 read as people waiting for the
  lift.

### F5. The old lady's bag is under her sunbed (deck 12, 129 m)

- **What is wrong:** her duffel bag is two thirds hidden (34% shows) and reads as a tan block; her
  furled parasol stands half behind it. In `src/world/topdeck.js` (the old lady's class, near its
  top) the sunbed is 62 px wide, centred on her (`def.x`, 128.5 m), at depth `D.props + 0.03`;
  the duffel is at `def.x + 30`, depth `D.props + 0.02`: half under the bed's foot end and behind
  it. Her parasol is the prop `prop_lady_parasol` at 129.12 m (`def.x + 30`, depth 7.98) in
  `tools/population.py`; a towel lies at `def.x + 22`.
- **The fix:** stand the bag clear of the bed's end: `def.x + 30` to about `def.x + 46`. The
  parasol stays where it is, leaning on the bed's foot, now with the bag beside it and not over
  it.
- **Then look at it in both states:** with her there (the start of region 8) and after the horn
  (`horn` set: she and her bags are gone, the bed stays, the parasol is now the pickup
  `item_parasol` at the same 129.12 m and her book lies on the bed). The near railing of the sun
  deck is drawn in front of everything there on purpose: a post across the bag is fine, the bag
  under the bed is not. Check that the bag does not land on a railing post so exactly that it
  reads as one thing; shift a few px if so.
- This is the least of the five. If it starts to take more than one try, leave it and say so.

## 2. How to look, and what to run

**After each change:** `python tools/build_ship_map.py`, then a close-up of the spot with her
standing on that deck (so that the deck is cut open as the player has it). `Browser.close_up()`
in `tools/playtest.py` is the tool. A ready scratch script does it for a list of spots and tiles
them into one sheet in `%TEMP%\bumbusik-playtest\`:

```
python %TEMP%\bumbusik-plan\audit\spots.py <sheet name> <start|late|end> deck,metres[,dx[,w,h]] ...
```

(`dx`: how far from the spot she stands, px, default 70; `w,h`: the view in game px, default
240 x 130; `late` and `end` set the story on, as `tools/check_overlaps.py` does.) The spots:

| Fix | Spots |
|---|---|
| F1 | `4,190.6,60,120,90` |
| F2 | `5,108.5,-110,200,110` |
| F3 | `9,74.6,60,140,100` and `10,74.6,60,140,100` |
| F4 | `11,201,-70` `12,81,-70` `5,109,-90` `8,201,-70` `4,81,70` and deck 3's plaque `3,97,-60`; then every other lobby in a sweep |
| F5 | `12,129.1,-60,160,100` at `start` and again at `late` |

If that script is gone, the same few lines are easy to write again: open the game with
`P.Browser()`, `b.open("?reset&play")`, `b.teleport(x + dx, floor_y(deck))`, wait, then
`b.close_up(name, x, floor_y(deck) - 50, w, h, 3)`.

**Look at each picture whole**, not only at the thing fixed (the project's rule): a moved board
may now touch something else.

**By rule:** `python tools/check_overlaps.py` must end "0 overlaps" (it did before these changes).

**The measured way, if wanted:** `%TEMP%\bumbusik-plan\audit\visible.py` shows and hides each
placed thing with the game held still and counts the pixels that change (about twenty minutes for
everything; things that move read as hidden, which is false). For F1 and F2 the reading should go
from 0.00 and 0.17 to near 1 (a text without a background reads about 0.25 at best: only its
letters count).

**Playtests the changes can touch** (never the whole suite): `boot`; `region1` (decks 4 and 5:
F1, F2); `region4` and `region9` (deck 9's and 10's forward lobbies: F3); `region8` (the old
lady, deck 12: F5); F4 touches every lobby's picture and nothing she does, so `stairs` and `lift`
are enough for it. Run them one at a time (`python tools/playtest.py boot region1`), muted as
they are, and say which were run and that the rest were not.

## 3. Showing and recording

- Show the user a before-and-after picture of each fix in the chat, with the link to stand
  there, each with `&tangerines=infinite`:
  - F1, F2: <http://localhost:8000/?play&at=gangway&cards=all&tangerines=infinite>, then aft
    along deck 4 to 190 m (the notice board is just before the aft stairs), and up to deck 5's
    midship lobby.
  - F3: the nearest `?at=` place to deck 9's forward lobby (see `docs/start-links.md`), then to
    the wall forward of the stairs; one deck up for deck 10.
  - F5: <http://localhost:8000/?play&at=champs&cards=all&tangerines=infinite>, aft across the sun
    deck to the sunbed.
- Record what was done in `docs/progress-decisions.md` (a short section: the five, what each
  was, the number changed), and mark V1, V2, V3, V6 and V7 as fixed in
  `docs/audit-2026-11-15.md` if that file is on the branch being worked on.
- One commit for the five is enough; the generated maps go in with it.

## 4. If something does not fit

Each fix above names its fallback (drop the note's text; drop the wet-floor sign; leave the
plaques; leave the bag). Take the fallback and say so, rather than move other things to make
room: the user prefers a thing removed to a thing squeezed in.
