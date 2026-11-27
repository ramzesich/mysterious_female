# The hull's top reviewed (2026-11-26, the Refinement session)

The user: "review the hull's top, all of its states. Inspect visual anomalies, misplacement, etc. Report your
findings." Reported the same day; **nothing fixed yet**, the user continues the next day ("we'll continue next day,
save all of these findings"). Branch `refine` (worktree `../mysterious_female-refine`), on main `cfe7a0e7`.

**Scope taken:** everything from deck 11 up (deck 12, the roofs, the funnel, the masts). States looked at: the
outside view (O) closed, day and sunset (`enterOverview`, and above the world's top at zoom 1); the intro's wide
views (`right`, `ship`, `dive`); play at the thirteen start places on and above deck 12 (`spinnaker`, `chapel`,
`champs`, `deck12`, `sundeck`, `court`, `cagneys`, `sushi`, `teppanyaki`, `bistro`, `terrace`, `stairway`, `funnel`)
and spots between them, day and sunset (`setDusk(1)`). **Not looked at:** the story's states of deck 12 (before and
after the horn, the wedding).

Metres here are `x / 48 - 10` (the world builder's `exact_x`). Evidence pictures are in `docs/audit-hull-top/`,
with the scratch scripts that made them (they write to `%LOCALAPPDATA%/Temp/bumbusik-npc/top/`).

## Findings (most serious first)

1. **DONE 2026-11-27** (the tank drawn a tile thinner; see `docs/progress-decisions.md`). **Deck 12's forward pool's tank covers deck 11's windows.** The kids' pool (x 3290 to 3490, about 58.5 to 62.7 m)
   is drawn as a tile block 416 to 466, under deck 12's floor; deck 11's window row starts at 448, so ~18 px of five
   windows' tops are behind it, in every state (closed, open, dimmed). `c-fwdpool.png`, `z-pooltile.png`.
2. **DONE 2026-11-27** (her deck in the water is the pool's own). **Corrected (2026-11-27):** deck 11 going bright under the kids' pool is the rule, not a fault: out in the open
   nothing is dimmed (GAME_DESIGN.md §5.3, the user, 2026-11-08), and standing on the open pool deck gives the same.
   The real fault is smaller and in all three pools: swimming sets the cut-away's deck to `deckAt(pool.y)`, a
   fraction (11.97 for the kids' pool, 10.97 for deck 11's), so the pool's own deck keeps 3% of its hull over it and
   the deck below shows 3% of its inside through its hull (the faint ghosts). Fix offered: while swimming, her deck is
   the pool's own (`pool.deck`), in `updateCutaway` (`src/scenes/ShipScene.js`). `zz-ghost2.png`, `zz-pools.png`.
3. **DONE 2026-11-27** (made on its perch). **The Great Outdoors' gull stands on air** (`gull_go`, `FOODGULLS` in `tools/population.py`, `FoodGulls` in
   `src/world/hazards.js`): made in its `gull-perched` picture at its stretch's middle (x 10795, 214.9 m) at
   `def.y - 112` = 448, under deck 12's terrace, and only flies to its perch (10603, 514, the rail's forward end)
   once its update runs near her. From afar (the outside view, the intro) it is a sitting gull in mid-air.
   `z-aftgull.png` (bottom left).
4. **DONE 2026-11-27** (on the palm's aft frond, the user's choice). **The aft terrace's end gull fits neither state** (`gull_terrace`, `TERRACE["gull"] = (220.0, 40)`, x 11040,
   feet at 376). Closed: past the glass screen's end, feet ~8 px under its top bar (366). Open: ~8 px over the end
   post's top (384), on its edge. The two rails differ too: the screen 50 px, the end post 32 px.
   `zz-postout.png` (closed), `zz-post.png` (open, the post).
5. **DONE 2026-11-27** (see-through, as the forward terrace's; the end post and a glint seen through it left, the user). **The closed view's deck 12 glass screen is solid light blue**, so what stands taller than it pokes over its top as
   bumps: people's hair (the court's players, the sun deck's people), a palm's fronds aft, the kids' splash
   mushroom's red cap. The forward terrace's screen shows its palms through it: the two do not match.
   `z-heads.png`, `z-dome.png`.
6. **Left as it is 2026-11-27** (by design: the side walk over deck 11's pools, 115 to 145 m, its thin floor and rail for the drop; the user's A; `walk/`). **The rail and the floor change at about 115 m on deck 12** (the `deck12` start, by the stair core): from about
   112 to 115 m no near rail and a thicker grey floor; aft of it a rail and a thin white floor slab. `zz-d12.png`.
   (Lower confidence: may be how the part over the pools is built.)
7. **Left as it is 2026-11-27** (the user's own choice of 2026-11-07, as deck 11's front; the user's A; `front/`). **The forward sun deck stays closed while she walks on it** (about 31 to 44 m): she is seen faintly through the
   glass and a 24 px white band (392 to 416) hides her from the thighs down; reads as wading. May be meant (an open
   terrace keeping the side closed); ask. `csheet-1.png` (top).
8. **DONE 2026-11-27** (drawn as the DJ's fog machine, out of each pipe, more and less by turns; the user's; `smoke/`). **The funnel's smoke at sunset reads as extra suns:** flat pale discs beside the setting sun. `d-funnel.png`.
9. **DONE 2026-11-27** (generated, limp, half filled and full by the wind, the ring on the pole's top; the foot's sock forward of the ladder; the bow's two the same; the user's; `socks/`). **The windsocks hang straight down between gusts** and read as striped posts; the one at the stairway's foot has
   the handrail across it (`sock()` in `src/world/topdeck.js`). `z-funneltop.png`.
10. **DONE 2026-11-27** (four generated poses, each gull placed and posed in the data, now and then changing; the pool's clear of the kid, his bucket and the slide; the user's; `gulls/`). **The bow's gulls look copied:** two rows of three, one picture, evenly spaced, on the forward glass screen
    (x 2060 to 2521, y 320) and on the pool's rim (x 3248 to 3519, y 416). `csheet-0.png`.

11. **DONE 2026-11-27** (the dividers start at the tank's foot; deck 11's tanks kept). **(Found 2026-11-27, with 1.) Deck 10's balcony fins rise into deck 11's pools' tanks:** the white posts of the
    balcony partitions under the Oasis pools run about 24 px up over the tanks' bottom rows, in the closed view and
    while she swims. Fix offered: the fins stop where a pool's tank begins (the map builder knows both). `zz-fins.png`.
12. **By design (the user, 2026-11-27).** **(Found 2026-11-27, checking the dim.) At the `stern` start she is not seen at all:** `?at=stern` puts her on
    deck 9's aft terrace (x 12344, y 848), an outdoors area whose cover (the stern's sloped plating) is drawn in
    front of her; only a padlock's thought popup over her shows. `stern-at.png`.

## The dim checked everywhere (2026-11-27, the user: "check that the dim works everywhere as we agreed")

The rule (GAME_DESIGN.md §5.3): the dim only where she is in an enclosed part of the ship; out in the open none.
Swept: on every deck 3 to 12, every metre she can stand on (2,087 spots), placed there, the dim read and compared
with the map's own `indoor()` (`tools/build_ship_map.py`): **no difference anywhere**. The outside route
(promenade, boat walkway, balconies), the mooring deck, the stern terraces, the pool deck, the Great Outdoors, the
aft terrace, the roof by the funnel's stairway and the funnel's top: off; the Stardust balcony (inside the theatre):
on. `spots.png`. Rooms behind doors keep their own dim (`ROOM_DIM`), not swept. Scripts: `docs/audit-hull-top/`
(`sweep.py`, `compare.py`, `spots.py`).

## Checked and fine

The radar platform touches its mast; the tangerine on the hot tub's canopy is placed there on purpose
(`tan_11_canopy`); the fruit crates (`haz_crates_11`), the Great Outdoors sign, the mast, the globe lights, the
funnel's base, stairway, stacks, horn and Bumbot on it; the sunset's colours; the intro's wide views. The sky's
slight blocks at zoom 1 are one colour step apart (not visible).

## Tool note

`tools/render_ship.py` starts its picture at the world's top (y 0), so it leaves out what stands above it: the
funnel's top platform (y about -228), its stacks, the horn and the radar mast's tip. `ov.py` here shoots that band.

## Next

All twelve answered (2026-11-27): 1 to 5, 8 to 11 done, 6, 7 left as they are, 12 by design; with the funnel's top mended on the way. On branch `refine`, not merged into main (the user's word awaited).
