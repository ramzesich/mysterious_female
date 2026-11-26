# Splash Academy's new pillow fort (plan-the-rest §7f, P6; 2026-11-26) — IN PROGRESS

The user: the old fort (`old-pillow-fort.png`) "doesn't make any sense, it's 3D, while we just crawl in profile". Then:
"it is unclear that there are openings she is supposed to crawl through", and "The openings should be in profile. Look
how the shaft in the linen room is implemented. We can place something similar here, behind the stack of pillows, on
both sides".

| File | Job | What |
|---|---|---|
| `text-1..3.png` | map objects `4e451d63-bf9a-4ba6-82c2-43da6e5956fa`, `60382be1-656b-434b-b601-8d5acb915a67`, `025bbff7-5c66-44d1-986b-f2f000eb668c` | from text: a rug, a strip, a faint sheet (failed) |
| `rough.png` (`rough.py`) | by rule | two cushion stacks, a blanket roof, its hem at 30 px |
| `redraw-s7.png`, `redraw-s23.png` | `edit_image_pro_flash` `6aa49a00-ae80-403d-bc05-f1a892034475`, `0d7861c9-4bae-4232-92be-ff76dc105632` | s23 approved by the user ("Yes") |
| `arches-s5.png`, `arches-s31.png` | `ade955c8-594a-4eca-bccb-d0b84e3564f9`, `7c033c61-8518-4410-82b2-ee896a1e75bd` | stacks as arches: doorways too small for her (unused) |
| `doors-s31.png`, `doors-s77.png` | `906f41fc-3bbc-4859-921c-9698dd83bfdb`, `46a9ffcb-ebc7-42f6-a270-8ebf23f3f225` | no doorway made (unused) |
| `tall-s31.png`, `tall-s8.png` | `b660ce12-868d-4e0d-9d81-640aa7d50d15`, `e544cdeb-cdec-4358-9cf6-a901c9764e33` | doorways up to the blanket (unused: the user wants openings in profile; `split-doorways-unused.py`) |
| `rough-mouths.png` (`mouths.py rough`) | by rule | the approved fort widened 14 px each end with a tunnel mouth in profile, as the shaft's |
| `mouths-s12.png`, `mouths-s44.png` | `23fa5630-7a71-4fbd-bb53-0b17d011547b`, `9cc755bc-07f5-406e-91ed-c918c7dcfd7e` | **s12 in the game now (not yet shown to the user)**: `mouths.py split` cuts it into `../../pillow-fort.png` (in front of her) and `../../pillow-fort-back.png` (the mouths' dark slots, behind her) |

66 generations for the fort so far.
