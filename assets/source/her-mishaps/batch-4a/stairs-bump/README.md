# Gag 21: she bumps down the funnel's stairway on her bottom (2026-11-18; built)

All PixMiniMax, 8 frames, 128 px, 1 generation each; index 0 is the input. Made on the steep flight's own steps
drawn as the game draws them, descending to the east (`raw/stairs.png`; the game flips her: she faces down the
flight, west). The stairs are kept to the pixel in every frame: her pixels are those that differ from them.

| Folder | What | PixelLab |
|---|---|---|
| `raw/sit1/` | From her standing frame (`raw/s21-start.png`): hands over her head, she sits down hard on the step, legs out down the flight | `05da5349-7451-4452-af92-f00c1a46957c` |
| `raw/bump2/` | The bump, in place: knees tucked, a jolt up, a slam down, her hair flying; from and back to sit1's last frame (`raw/bump-first.png`) | `a8dd11ab-0870-4d22-99cd-8867d7c6485c` |
| `raw/foot1/` | At the foot (the lower flight's steps and the roof's floor, `raw/foot-stage.png`): the last two steps and off onto the floor, slumped; its last frame (pinned to her dazed sit) is dropped: it popped her upright | `4359c48f-ae1d-4d6c-b6f4-df17929127b6` |

| `raw/dazed1/` | Her dizzy end (the user, on seeing the gag: "Add the dizzy state after the ride: butterflies"): from her last foot frame with the suitcase gag's two butterflies set over her head (`raw/dazed-start.png`, `raw/dazed-start.py`) to the same: her head wobbles, the butterflies circle; made on an opaque ground (its sky came back flat grey, taken out by `cut.py`). Loops twice | `38e79b90-c901-4166-b835-3e726a22c84f` |

Not used: `raw/bump1/` (`95228fff-2a29-4533-9ad1-c9d31ad48362`), pinned to the next step down: she glided, no bump.

As approved (the user): after the sit, at once, one bump every three frames (bump2's 3, 5, 7; a step down at 5) at
a constant pace all the way to the foot, then the foot clip, then the fade and her checkpoint at the technical door.
`raw/preview3.py` composes it on the real stairway (its rail in front of her); `raw/audit2.py` measured her seat
on the treads in every frame, on both flights. Loose specks of 1 to 2 px in four frames are taken out with the
cut-out. 4 generations.

**Built (2026-11-18):** `cut.py` cuts every clip from its stage into `sit/`, `bump/`, `foot/`, `dazed/` (facing east, as
generated); `tools/build_gags.py` puts them in `assets/sprites/gags.png` as `stairs-sit`, `-bump`, `-foot`, `-dazed`;
the ship scene's `stairsGag` plays them on the stairway flipped, each frame on its step's corner (`stairs` in
`gags.json`). 5 generations in all.
