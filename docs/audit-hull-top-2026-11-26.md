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

1. **Deck 12's forward pool's tank covers deck 11's windows.** The kids' pool (x 3290 to 3490, about 58.5 to 62.7 m)
   is drawn as a tile block 416 to 466, under deck 12's floor; deck 11's window row starts at 448, so ~18 px of five
   windows' tops are behind it, in every state (closed, open, dimmed). `c-fwdpool.png`, `z-pooltile.png`.
2. **Swimming in that pool flips the deck below.** In the water she is at y 448, under deck 12's floor (416): deck
   11's dim goes off, its band turns to the bright closed hull with faint grey ghosts of deck 11's furniture tops
   in the white plating under the windows (still there after 6 s); out of the pool it is dark again.
   `zz-ghost2.png` (top: swimming; bottom: standing by the pool).
3. **The Great Outdoors' gull stands on air** (`gull_go`, `FOODGULLS` in `tools/population.py`, `FoodGulls` in
   `src/world/hazards.js`): made in its `gull-perched` picture at its stretch's middle (x 10795, 214.9 m) at
   `def.y - 112` = 448, under deck 12's terrace, and only flies to its perch (10603, 514, the rail's forward end)
   once its update runs near her. From afar (the outside view, the intro) it is a sitting gull in mid-air.
   `z-aftgull.png` (bottom left).
4. **The aft terrace's end gull fits neither state** (`gull_terrace`, `TERRACE["gull"] = (220.0, 40)`, x 11040,
   feet at 376). Closed: past the glass screen's end, feet ~8 px under its top bar (366). Open: ~8 px over the end
   post's top (384), on its edge. The two rails differ too: the screen 50 px, the end post 32 px.
   `zz-postout.png` (closed), `zz-post.png` (open, the post).
5. **The closed view's deck 12 glass screen is solid light blue**, so what stands taller than it pokes over its top as
   bumps: people's hair (the court's players, the sun deck's people), a palm's fronds aft, the kids' splash
   mushroom's red cap. The forward terrace's screen shows its palms through it: the two do not match.
   `z-heads.png`, `z-dome.png`.
6. **The rail and the floor change at about 115 m on deck 12** (the `deck12` start, by the stair core): from about
   112 to 115 m no near rail and a thicker grey floor; aft of it a rail and a thin white floor slab. `zz-d12.png`.
   (Lower confidence: may be how the part over the pools is built.)
7. **The forward sun deck stays closed while she walks on it** (about 31 to 44 m): she is seen faintly through the
   glass and a 24 px white band (392 to 416) hides her from the thighs down; reads as wading. May be meant (an open
   terrace keeping the side closed); ask. `csheet-1.png` (top).
8. **The funnel's smoke at sunset reads as extra suns:** flat pale discs beside the setting sun. `d-funnel.png`.
9. **The windsocks hang straight down between gusts** and read as striped posts; the one at the stairway's foot has
   the handrail across it (`sock()` in `src/world/topdeck.js`). `z-funneltop.png`.
10. **The bow's gulls look copied:** two rows of three, one picture, evenly spaced, on the forward glass screen
    (x 2060 to 2521, y 320) and on the pool's rim (x 3248 to 3519, y 416). `csheet-0.png`.

## Checked and fine

The radar platform touches its mast; the tangerine on the hot tub's canopy is placed there on purpose
(`tan_11_canopy`); the fruit crates (`haz_crates_11`), the Great Outdoors sign, the mast, the globe lights, the
funnel's base, stairway, stacks, horn and Bumbot on it; the sunset's colours; the intro's wide views. The sky's
slight blocks at zoom 1 are one colour step apart (not visible).

## Tool note

`tools/render_ship.py` starts its picture at the world's top (y 0), so it leaves out what stands above it: the
funnel's top platform (y about -228), its stacks, the horn and the radar mast's tip. `ov.py` here shoots that band.

## Next

The user's word on which to fix and how; nothing is built.
