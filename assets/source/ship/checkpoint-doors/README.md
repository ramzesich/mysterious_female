# The checkpoints' own doors (plan-the-rest §7e, part 10; 2026-11-26)

Four tries, all used (the user: "I like all of them, let's use all"). Each is `edit_image_pro_flash` (5 generations) of
the game's white crew door (`door-crew`, 29 x 74) padded to 40 x 80 on transparency.

| Try | Used for | Job | Description |
|---|---|---|---|
| `tries/B1.png` | `door-theatre-red`, the theatre's foyer (`cp_foyer`) | `e5055d2c-82d3-4bff-86e7-4e5229d4201e` | padded theatre door, dark burgundy leather, brass studs in a diamond pattern, a small round porthole window, seed 11 |
| `tries/B2.png` | `door-theatre-navy`, the Arcade (`cp_7_aft`) | `f1139282-c94d-4472-8110-27de1c662c0d` | the same in dark navy tufted leather, seed 23 |
| `tries/C1.png` | `door-walnut`, the Library (`cp_library`) | `f1b434d0-4188-466e-9942-0bd2b49e340c` | dark walnut service door, two recessed panels, a brass kick plate, seed 31 |
| `tries/C2.png` | `door-mahogany`, Cagney's (`cp_technical`) | `1bc8bf54-3a59-4a7b-82f7-439d980461b2` | dark mahogany door, a wide polished brass kick plate, seed 47 |

`python tools/build_checkpoint_doors.py` sets each leaf (its grey rim taken off) into a doorcase on the crew door's
frame and makes its lit twin by the crew door's ajar geometry (the round windows laid back whole, narrowed by two
columns into ovals: the user), writing `assets/source/ship/<name>/frame_0.png` and `<name>-ajar/frame_0.png`; then
`python tools/build_ship_art.py` (their own colours, `OWN`; the ajar ones' foot 3).
