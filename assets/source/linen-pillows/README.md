# The linen room's pillows (near-catch 4)

The stack of pillows in the laundry cart and its scatter as Bumbot goes (the user, 2026-11-24: "The laundry cart has
stack of pillows on top of it ... When we push it, Bumbot jumps (like now), the pillows scatter"; "Use this cart, but
empty"). Built by `tools/build_linen_pillows.py` into `assets/ship/linen-pillows/`. The record: `docs/near-catch-4-remake-log.md`.

## What is used

| File | What | PixelLab job |
|---|---|---|
| `stack-rough.png` on `stack-base.png` | a flat rough of the stack in the room's own picture (`scripts/rough_stack.py`) | |
| `stack-s11.png` | its redraw, `edit_image_pro_flash`, 128 px, seed 11: four plump pillows; cut by what differs from the base | `dab040e7-ac70-4a4a-bd22-853fd6ce5065` |
| `scatter5-start.png` | the clip's first picture: a flat green set 208 x 128, the cart a flat blue shape, the stack in it (`scripts/set5.py`) | |
| `scatter5-end-rough.png`, `end5-s77.png` | where the four should lie, flat shapes; its redraw, seed 77: the clip's last picture | `3dcda9e2-58c8-4ed4-9a25-9ef525b0c9e0` |
| `clip/0.png` to `16.png` | the scatter: `animate_image_pixminimax` from the first to the last, 16 frames, seed 5 (frame 1, a smear of the whole stack, is not used) | `c4bcc5b4-b0d0-4d0e-9338-30f88e65b7c6` |

The set's left edge is 35 px forward of the cart picture's left edge as he goes (5887 in the world); its floor is row 116.

## Tries not used (`tries/`)

- `stack-s23.png`: cream pillows, five, flatter: read as towels (`2e423939-1142-4930-94c5-519db8b7ce8c`).
- One heap behind the cart: `end-s11.png` (`7f95232e`; also `907487b5`), narrower `end2-s77.png` (`5a35d40d`; also
  `3a7998a7`, `fb97dfe8`), and the topples toward them, `scatter-s19-sheet.png` (`8884861f`; also `462fa164`),
  `scatter2-*` (`59f34787`, `6d1a54ff`), `scatter3-sheet.png` (`a696287d`, `2923c0bf`, `a0c4d41a`), `scatter4-sheet.png`
  (`ed8ac397`, `285859da`, `d85db23e`, `547c27de`): a heap of four lay straight in front of the laundry chute's hatch and
  hid its lower half, and the first ran across the door's frame. The narrower end also made the generator slide the
  stack off as one stiff fan.
- `end5-s11.png` (`4edf67df`): the scattered end, a little taller under the hatch.
- `scatter5-s19/-s42/-s73-sheet.png` (`22c32592`, `4d5f20ae`, `5e71d393`): the scatter with more smeared frames, or the
  cart tipping.

About 80 generations in all.
