# Close-ups: the things to find and the key cards, seen close

The user, 2026-11-19 (§4 2.1): "Can we use more fine-detailed visuals for the items in the game?"
Chosen: **A and C**. A: in the world each thing is drawn a little bigger than life; C: when she gets
one, its close-up is shown in the middle of the screen over a dim with a warm light behind it (`world.closeup()`), any
key closes it. Each picture here is a PixelLab map object (high detail, about 100 px), approved by the
user; `python tools/build_closeups.py` puts them on the palette (the tennis ball keeps its own felt, as
in the world) into `assets/sprites/closeups.png` + `.json`, shown at 2x (the world's pixel size).

**The world's sprite of a thing is its close-up shrunk** (`FROM_CLOSEUP` in `tools/build_things.py`), so
the two are one picture; except the wool (the close-up shrunk was a plain red blob: a small picture of
its own, `assets/source/things/wool.png`, "10 px with strand") and the bookmark and the plant (shrunk,
then mended by hand: the bookmark's 4 px cat head, the plant's stem; kept finished in `things/`).

| File | Thing | PixelLab id |
|---|---|---|
| `snack.png` | Bumbot's liquid snack in a tube (5) | 4332ac75-5153-461c-ad32-e8312dfbe9ad |
| `massage.png` | Bumbot's massage gun (6) | a7b17480-30c6-4cef-a07d-fc3927a20e74 |
| `car.png` | Bumbot's remote-controlled car (8): beige, two big rubbery cyan wheels (the user); the wheels moved to the palette's brightest cyan by hand (`RECOLOUR`) | 0cd8136e-9888-4697-8246-18b4d721f53a |
| `bookmark.png` | Her bookmark with a cat on top, in its book (10) | b8d0c745-bd56-4681-ae80-10233b1e640c |
| `diary.png` | Her diary, brown leather, a strap with a brass buckle (11; the user chose it over a tan one) | 3c514d91-0778-4411-b724-e52db21d4ea3 |
| `plant.png` | Her small plant in a pot (12) | e091d55d-875d-4f37-ab63-c913b013d391 |
| `ball.png` | Bumbot's old tennis ball (1) | 3a001209-1d9c-45b6-86f8-567896cf266f |
| `wool.png` | Bumbot's ball of wool (2) | 50f9bb72-28b6-4829-a7d8-76bf78135867 |
| `feather.png` | Bumbot's feather teaser (3) | 8ddc8382-b5a9-4398-82a9-68c4cc868738 |
| `flag.png` | Her little flag of Ukraine (9) | 323be526-63d5-40c7-890c-389a09fb326d |
| `socks.png` | Her grip socks (a way to move, the wall jump): recoloured to the world's stronger pink | 7dfab48e-ba85-489a-8184-6aa65c49c76c |
| `pills.png` | The stage manager's pills (her one pocket quest item); its label's print drawn by hand (`MEND`) | e13fda28-1f0d-458f-a1d5-806a9fc48650 |
| `parasol.png` | The old lady's parasol, furled (the glide): set to the world parasol's red and white, its handle's red band painted as the pole (`MEND`) | 0d8aa46f-6029-466f-ac5e-e287d5d6f82b |
| `bell.png` | Bumbot's collar bell (4): a red leather collar, its silver buckle, a gold jingle bell (the user chose it over a thin cord, `tries/bell-cord.png` 8509e7ea-169b-4214-9e6e-1498895c5b81); its yellow ring by the buckle taken out by hand, the strap closed over it (the raw try: `tries/bell-collar-raw.png`). Its world sprite (`collar-bell`, lying on the promenade's deck) is it shrunk to 14 px | e7dfd48b-fe93-4f4f-abfa-533028267ad2 |
| `key-card.png` | The key card on its lanyard: one picture, its stripe recoloured to each card's colour (`CARDS`) | 8ce90882-fedc-4c3a-8d0a-0301aeb82b09 |

Tried and not used (not kept): an open parasol (70b96778), the world parasol redrawn with `image_to_pixelart` (f6b66145), a parasol wrapped in a spiral (fc5737e0); the first, small pictures of 5, 6, 8, 10, 11, 12 (48 px, low detail;
a first bookmark came as a cat sitting on the book, 953b1b7f); a red rally car (a927ee5c, "beige with two
big rubbery cyan wheels", the user); a four-wheeled beige truck (ca2b75f3); a lilac diary (2694e671) and
a tan leather one (1fd61702); a wool ball with knitting needles (1e618d29); the small wool used is
77b5d69c. The world's own tennis ball is put in the dog's owner's toss clip, frames 4 and 5, over her
far hand and under her near one (the user).
