# The spa's masseur (deck 11, the massage scene; the user, 2026-11-22)

The old masseuse (`../masseuse/`, cast id 2fefa59f, out of the cast) was "huge" beside a "tiny" guest; remade with the
massage scene (src/world/spa.js). The user chose a man in a spa uniform.

**The character:** PixelLab pro, size 64, side view, in the drill officer's style (`style_character_id`
3ed991ae-cf74-4ce1-a636-8549344290a6, the men's proportions): **ca46c265-17de-497c-89e4-806181e735c9**, "Spa masseur",
10 generations. 61 px tall to her 59, a head of about 15 px. `east.png`, `south.png`, `north.png`, `west.png` its views.

**His clips** (east unless said; `animate_character`, the job and the group ids):

| Folder | What | Mode | Job / group | Gen. |
|---|---|---|---|---|
| `stretch/` | not used: turned to us, arms out in a T | v3 | 2e4ec320-2c58-44fd-88f6-413fab7dff6d / 6bfa2cc6-0df3-49b8-99ff-a9aa62e083b5 | 1 |
| `stretch-up/` | not used: hands to his face | v3 | a0aab91a-4196-4deb-9fa9-425f0f5d12f0 / 0d71cdf2-fe1c-448f-9bc0-94dff02d1db1 | 1 |
| `stretch-up-pmm/` | not used: hands clasped behind his head | pixminimax | 73902f58-ad1c-4872-ba14-19f096793395 / 028f0ecb-956f-48df-98fc-23d87e785e81 | 1 |
| `stretch-skel/` | not used: the library's `arms_overhead` (approved but for his look) | skeleton-v3 | 6992ec1b-95c4-458d-b77f-789d85a0d548 / 9baab037-703a-446f-a922-177862fe12b4 | 3 |
| `stretch-look/` | **used** (`stretch`): the same, his head tipped up while his hands are up (the user: "he should look up") | skeleton-v3 | 6475e5fc-5d09-4318-97c4-95a87609305c / 8e7b2e6a-a2ea-4430-9434-10e204f18da7 | 3 |
| `massage/south`, `massage/north` | **used**: his bow, two rounds of kneading, his straightening; south behind the table facing us, north his back to us | skeleton-v3, poses | f512b078-5d62-4eba-9d37-ca4ce33fb6b6, 9a5eb394-40f8-41ba-8d0d-689e33495dd0 / b4d98aaa-5ada-4aa5-bffa-f0834845d25e | 6 |
| `walk/` | **used**, its doubled back outline thinned (`walk-clean/`, `thin_back.py`) | skeleton-v3, template `walking` | d9fe3e2a-d505-40fe-9c6d-8d06c564aab8 / 4dae3e94-13db-4ad2-ace1-ab1837281405 | 3 |
| `toss/` | **used**: an underhand toss with both hands, the gun drawn in them by the game (`MASSAGE.toss`) | skeleton-v3, poses | 6f40a975-316e-4422-ad99-4f982fdc6381 / 261c9df7-29fa-409d-8a6e-97bbd81a90a9 | 3 |

31 generations in all. The back view's hands were drawn over his own back (from behind they are hidden in front of
him): painted out and his back made one even white in every frame, `unhands.py` then `cleanback.py` (frame 2's trouser
outline mended by hand, listed there), into `massage-back/`.

The game's folder is `../masseur/` (copies: `stand.png` east, `front.png` south, `back.png` north, `walk/` from
`walk-clean/`, `stretch/` from `stretch-look/east/`, `massage-front/` from `massage/south/`, `massage-back/`, `toss/`);
`tools/cast.py` cuts the massage into bow, kneading and straightening and holds the stretch's hands-up frames 0.6 s each.
`tools/fetch_people.py` leaves him alone (`BY_HAND`). In the game he is 1 px lower but facing us behind the table
(`MASSAGE.lower`).
