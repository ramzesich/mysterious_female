# Close-ups: the things to find and the key cards, seen close

The user, 2026-11-19 (§4 2.1): "Can we use more fine-detailed visuals for the items in the game?"
Chosen: **A and C**. A: in the world each thing is drawn a little bigger than life; C: when she gets
one, its close-up is shown in the middle of the screen over a dim with a warm light behind it (`world.closeup()`), any
key closes it. Each picture here is a PixelLab map object (high detail, about 100 px), approved by the
user; `python tools/build_closeups.py` puts them on the palette (the tennis ball keeps its own felt, as
in the world) into `assets/sprites/closeups.png` + `.json`, shown at 2x (the world's pixel size).

**The world's sprite of a thing is its close-up shrunk** (`FROM_CLOSEUP` in `tools/build_things.py`), so
the two are one picture; except the wool (the close-up shrunk was a plain red blob: a small picture of
its own, `assets/source/things/wool.png`, "10 px with strand") and the bookmark (shrunk, then mended by hand: its
4 px cat head; kept finished in `things/`). Her plant was such too until 2026-11-28; the Albuca is its close-up shrunk.

| File | Thing | PixelLab id |
|---|---|---|
| `snack.png` | Bumbot's liquid snack in a tube (5) | 4332ac75-5153-461c-ad32-e8312dfbe9ad |
| `massage.png` | Bumbot's massage gun (6): **since 2026-11-28 his own**, from the user's photo (`reference/bumbot_massage_gun.heic`, git-ignored), cut out and redrawn (`tries/massage/`: 1 redrawn, **used**, `1bc03cc3-c89e-4ef7-846b-923f06dadb28`; 2 faithful `a8c85471-48fb-4f68-a12f-7525fc31e13b`; 3 pro flash `cb9ab5fc-d132-4a8e-9477-4ed250e4524f`), its ground cut away, in its own colours; its world picture's nozzle given a bump under it as over it (`MEND` in `tools/build_things.py`). On Bumbot's bed seen close it is laid into the redraw (`bed/tries/try-photo2-v3-gun.png`; an inpaint, `37199829`, drew the bed into the box and was dropped). The old gun | a7b17480-30c6-4cef-a07d-fc3927a20e74 |
| `car.png` | Bumbot's remote-controlled car (8): beige, two big rubbery cyan wheels (the user); the wheels moved to the palette's brightest cyan by hand (`RECOLOUR`) | 0cd8136e-9888-4697-8246-18b4d721f53a |
| `bookmark.png` | Her bookmark with a cat on top, in its book (10) | b8d0c745-bd56-4681-ae80-10233b1e640c |
| `pad-by-hand.png` | **Her massage pad (11), since 2026-11-28 in the diary's place**: from the user's photo (`reference/her_massage_pad.heic`), cut out, redrawn (`tries/pad/`: 1 redrawn `82dc0fd7-56b3-4518-bd95-92a6e23412f2`; 2 faithful `4e50b45e-21b3-4699-9b51-8e126ee0d2ae`; 3 pro flash, **used**, `1597b585-7329-42d6-9e36-0fad95baa7c0`), its rosettes 4 px left and one more on the top and the middle rows (`tries/pad/rows.py`), its blue at 65%, then **the user's own touches in Paint: never written by a tool** (magenta empty; `BY_HAND` in `tools/build_closeups.py`). Its world picture lies on a theatre seat's near arm, its rows set by rule (`PAD_ROWS`); on the desk seen close, upright at the right end. (The diary was `diary.png`, 3c514d91-0778-4411-b724-e52db21d4ea3, in git's history.) | |
| `plant.png` | Her plant (12): **since 2026-11-28 an Albuca bracteata** (the user's; from a photo the user found, the bulb almost all in the soil): her old close-up edited with the photo as reference (`tries/plant/`: 1 by text `946d77a1-72c7-454a-a943-58820158be07`; 2 by the photo, **used**, `b5ca99d8-8cbf-481e-99be-6829146750d4`; 3 new `57c32645-f76b-46fa-b57a-1a032b09a831`), the plant moved 5 px right and 5 down behind the picture's own soil and pot (`tries/plant/sink.py`, nothing drawn in), in its own colours. (The sapling was e091d55d-875d-4f37-ab63-c913b013d391.) | |
| `ball.png` | Bumbot's old tennis ball (1) | 3a001209-1d9c-45b6-86f8-567896cf266f |
| `wool.png` | Bumbot's ball of wool (2) | 50f9bb72-28b6-4829-a7d8-76bf78135867 |
| `feather.png` | Bumbot's feather teaser (3) | 8ddc8382-b5a9-4398-82a9-68c4cc868738 |
| `flag.png` | Her little flag of Ukraine (9) | 323be526-63d5-40c7-890c-389a09fb326d |
| `socks.png` | Her grip socks (a way to move, the wall jump): recoloured to the world's stronger pink | 7dfab48e-ba85-489a-8184-6aa65c49c76c |
| `pills.png` | The stage manager's pills (her one pocket quest item); its label's print drawn by hand (`MEND`) | e13fda28-1f0d-458f-a1d5-806a9fc48650 |
| `parasol.png` | The old lady's parasol, furled (the glide): set to the world parasol's red and white, its handle's red band painted as the pole (`MEND`) | 0d8aa46f-6029-466f-ac5e-e287d5d6f82b |
| `bell.png` | Bumbot's collar bell (4): a red leather collar, its silver buckle, a gold jingle bell (the user chose it over a thin cord, `tries/bell-cord.png` 8509e7ea-169b-4214-9e6e-1498895c5b81); its yellow ring by the buckle taken out by hand, the strap closed over it (the raw try: `tries/bell-collar-raw.png`). Its world sprite (`collar-bell`, lying on the promenade's deck) is it shrunk to 14 px | e7dfd48b-fe93-4f4f-abfa-533028267ad2 |
| `sardines.png` | Bumbot's tin of sardines (7): open, silver, the fish packed in; the user chose try 4 of four "as it is" (`tries/sardines/`: 1 `68e240ca-3772-4e28-8b8d-db2b4c1b3057` and 2 `53ac02af-9ddd-434a-a017-f2a146a0d796` closed, 3 `c503d1fc-d2dc-4d8a-9c89-5b19830ba631` open in yellow oil). Kept in its own colours (`OWN_COLOURS`: on the palette it went purple). Its world picture is not it shrunk (a grey blob at 12 px): `assets/source/things/sardine-tin.png`, drawn by hand at 13 x 9 in its colours, the one in the chef's hand too | 05ada285-cefe-4a93-be81-18da4424bf37 |
| `tshirt.png` | Her husband's navy t-shirt (13), **its top half** with the logo from his photo on his left chest ("bluevine cares"; the user's own pixel edit, `tshirt-logo-by-hand.png`; `tshirt-logo.png` is the built one they saved over), built by `tools/draw_tshirt_logo.py`; in its own colours (`OWN_COLOURS`). Its world picture is not it shrunk: a small generated folded shirt (`../things/tshirt-folded.png`). The tries: `tries/tshirt/README.md` | dfea7d46-99a2-4c5e-82df-265610e96253 (the shirt), b9b2b094-4ddc-4bee-9deb-271fd0cd27c4 (the logo) |
| `sleepmask.png` | His sleep mask (14): pink-beige, one strap (the user's description); try 1 of four (`tries/mask/`: 1 `d3b8242f-3d06-45ff-93ad-f17fe5f49f73` used, 2 `d60e52f0-bf23-416f-bd07-2d1a2e674fba` pinker, 3 `a4359c37-b14a-4ce5-a2c5-c66dbc93d0c0` with printed eyes, 4 `e051052e-59e7-434e-bb60-f2087b09d290` dustier), its edges smoothed by rule (`tries/mask/smooth.py`, the 2 px band; the strap's tabs the same size: the user). Its own colours (`OWN_COLOURS`: on the palette the pink went peach). Its world picture `../things/sleepmask.png` is its body shrunk by majority to 12 x 6, outlined in its rose, a pixel of strap each side (16 x 8) | d3b8242f-3d06-45ff-93ad-f17fe5f49f73 |
| `handheld.png` | His handheld (15), his ROG Xbox Ally X: a pro redraw of the user's photo of the model, every logo painted out first (`tries/handheld/9.png`, its white cut away; the tries and ids in `tries/handheld/README.md`). Its own colours (`OWN_COLOURS`). Its world picture is the user's own pixels, `../things/handheld-by-hand.png` | 048aee0d-1cd1-4957-9e1f-300b5082f2ae |
| `pick.png` | His guitar pick (16): his own, red, a Jazz shape with a raised dot grid, from the user's photo (its words and mark painted out first); `tries/pick/6.png` with its edges cleaned (the user's "B"). Its own colours (`OWN_COLOURS`). Its world picture is `../things/guitar-pick.png`, 8 x 9, built by hand from it, point up | 4f72bc5f-2b4f-4177-beef-54cf35e04125 |
| `key-card.png` | The key card on its lanyard: one picture, its stripe recoloured to each card's colour (`CARDS`) | 8ce90882-fedc-4c3a-8d0a-0301aeb82b09 |

Tried and not used (not kept): an open parasol (70b96778), the world parasol redrawn with `image_to_pixelart` (f6b66145), a parasol wrapped in a spiral (fc5737e0); the first, small pictures of 5, 6, 8, 10, 11, 12 (48 px, low detail;
a first bookmark came as a cat sitting on the book, 953b1b7f); a red rally car (a927ee5c, "beige with two
big rubbery cyan wheels", the user); a four-wheeled beige truck (ca2b75f3); a lilac diary (2694e671) and
a tan leather one (1fd61702); a wool ball with knitting needles (1e618d29); the small wool used is
77b5d69c. The world's own tennis ball is put in the dog's owner's toss clip, frames 4 and 5, over her
far hand and under her near one (the user).
