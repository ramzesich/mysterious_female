"""The theatre's audience in the one theatre seat (2026-11-19, the user: "Make all of the people in the theatre sit on
the same exact chair as the popcorn guy, and as the empty chairs"; "placed behind the right (closest to the screen)
chair arm, but obscure the left (far) part of the chair").

The seat: `assets/source/ship/theatre-seat-side/frame_0.png` (aud_popcorn's game picture, him taken out). Split at row
`NEAR_FROM`: above it the backrest and the far arm, behind the sitter; from it down the near arm's pad, the seat's front
and its legs, in front. The sitters, each on the same 80 px canvas as the seat: the five named without their own chairs
(`nochair-<name>.png`) and ten others made from them (`new-<k>.png`); all `edit_image_pro_flash`, ids in README.md.

Out: the five named to `assets/source/people/<name>/stand.png` (their PixelLab pictures kept as `stand-own-chair.png`),
the ten to `assets/source/ship/audience/frame_<k-1>.png`. Then `python tools/build_people.py`, `tools/build_ship_art.py`,
`tools/build_ship_map.py`."""
import os, shutil
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__)) + "/"
R = H + "../../../../"
SEAT = Image.open(R + "assets/source/ship/theatre-seat-side/frame_0.png").convert("RGBA")
NEAR_FROM = 60
far, near = SEAT.copy(), SEAT.copy()
far.paste((0, 0, 0, 0), (0, NEAR_FROM, SEAT.width, SEAT.height))
near.paste((0, 0, 0, 0), (0, 0, SEAT.width, NEAR_FROM))


def seated(path):
    c = far.copy()
    c.alpha_composite(Image.open(path).convert("RGBA"))
    c.alpha_composite(near)
    return c


for w in ("aud_popcorn", "aud_gent", "aud_lady", "aud_girl", "aud_granny"):
    pd = R + f"assets/source/people/{w}/"
    if not os.path.exists(pd + "stand-own-chair.png"):
        shutil.copy(pd + "stand.png", pd + "stand-own-chair.png")
    seated(H + f"nochair-{w}.png").save(pd + "stand.png")
os.makedirs(R + "assets/source/ship/audience", exist_ok=True)
for k in range(1, 11):
    seated(H + f"new-{k}.png").save(R + f"assets/source/ship/audience/frame_{k - 1}.png")
print("ok")
