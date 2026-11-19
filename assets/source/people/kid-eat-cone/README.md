# The kid eating a soft serve cone (2026-11-19)

His `eat` clip (`assets/source/people/kid/eat/`, built into `assets/sprites/people.png` by `tools/build_people.py`, 7 a
second in `tools/cast.py`) is made here. The one before had him biting his own orange water pistol, the game's cone laid
in front of him in the air (the user: "the kid is holding his water gun while eating. The ice cream is just hanging in
the air in front of him"); it is kept in `raw/old-eat/`.

| File | What | PixelLab |
|---|---|---|
| `start-stand88.png` | His standing frame on the old clip's 88 px canvas, his feet and head where the clip's were | made here |
| `raw/still-s7.png` (used) | `edit_image_pro_flash` of it: a soft serve cone in his fist before his mouth, his pistol tucked in his waistband; `eat/0.png` | `748aa7e6-d7d9-4ecc-a845-74120868de00` (seed 7, 5 generations) |
| `raw/still-s1.png` | The other try: the cone held, his hand unclear | `b903f2aa-4a79-40fa-8b23-6f452c98c1cc` (seed 1, 5) |
| `raw/e1/` | PixMiniMax from `still-s7.png`: three licks, the swirl smaller each time, then a bite of the cone (12 frames, index 0 the input); `eat/1.png` to `eat/12.png` | `996e6b5d-0ea5-4e2b-a7e9-c7e28691d1fb` (1 generation) |

Checked frame by frame: one piece each (no loose specks), his feet on row 74 in every frame, the pistol tucked
throughout. The game hands her cone over into his fist as the first frame holds it (3 px before his middle, its tip
19 px up: `kidHas` in `src/world/lido.js`). 11 generations in all. Not made: a clip of him tucking the pistol away (it
jumps from his hands to his hip as he takes the cone, and back after).
