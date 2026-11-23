# The shaft, remade: a log

The user, 2026-11-23: redraw the sequence where she goes into the opening in the linen room after Bumbot's
escape, autonomously; everything to look good and make sense (placement, layering, directions); generations
as needed; "Log everything you decided and done, in a separate document." This is that document. It is the
record of this one piece of work: `docs/progress-decisions.md` has a pointer to it.

## 1. What the user asked, in their words

- "What I really dislike about how the sequence starts is that when we enter the opening, we are in 99% cases
  facing right. The sequence starts with us facing left and the shaft going left."
- "If the shaft can be rebuilt going right and us exiting at another place to the right, but still making
  sense story wise: do it."
- On a visible turn inside the shaft: "I don't like the idea of entering and turning, that still interferes
  with the player's sense of direction."
- "If we mirror the laundry room, we have to mirror all the logic and the cart and Bumbot sequence in it. The
  laundry shaft down has also make sense in terms of placement. It still has to lead to the same place down
  on deck 4. If all of that can be done properly, let's mirror the room."
- "If that would make more sense to switch the laundry entrance door (in the corridor) with the next door to
  the right, let's also do that."
- "So when she is crawling inside the shaft, how can she peek down into the room that are not there?"
- "Yes, let's take all our findings into consideration."

## 2. What was there before (for comparison)

- The linen room: door at its left, the racks, Bumbot on the bottle shelf, a small vent (20 x 18 px) drawn
  face-on high on the back wall at the right. She pushed the cart right, jumped on, pressed ↓.
- A fade, and she was in "the duct", turned round to face left: a strip 1,300 px long drawn in code in flat
  purple, laid over the ship between 86 m and 113 m (the lift hall and the atrium), the ship dimmed behind it.
- Four framed pictures hung under the strip as she passed its grilles (a lobby light, a glass dome that the
  ship no longer has, a cabin of balloons, a snoring passenger), over places where no cabin is.
- At its end ↓: a clang, a fade, and she was put 21 m further forward, falling in front of deck 8's closed
  side for a moment before the deck opened.

## 3. Decisions

1. **The shaft goes forward (left).** It cannot truly come out to the right: everything it must lead to
   (deck 8 forward, cabin 8206 at 41 m, the only stairs open up to deck 11) is toward the bow, and from any
   room she can reach on deck 9 at that point (82 to 194 m) that is left. Deck 8 to the right is region 7's
   hallway. The user agreed.
2. **The linen room is mirrored** (the user's choice): the door at its aft end (right), the wide rack and
   Bumbot's shelf forward of it, the shaft's mouth on the forward wall. She comes in, pushes the cart
   forward, climbs in and crawls on, all one way. All its logic is mirrored with it: the cart's start and
   stop, the side she pushes from, where Bumbot sleeps and which way he bolts.
3. **The linen room's door moves one cabin door aft** (the slot at 115.4 m, from 111.4 m; the user's
   thought). Mirrored at the old slot the room would have been drawn over the lift hall's place (it reaches
   3.8 m forward of its door; the hall's wall is at 110 m). It takes the place of the cabin door that stood at that
   slot; the old slot is bare wall now, as the same slot is on decks 8 and 10 (it is too near the lobby's glass door
   for a cabin door, which is why the linen room's door could stand there).
4. **The chute's hatch stands straight over the laundry's cart on deck 4.** The laundry is not touched (the
   same room, the same cart she lands in). With the door moved, the hatch's place over that cart falls
   between the wide rack and the door, so the room's second rack became a narrow one aft of the door. The
   laundry cart she pushes starts parked in front of the hatch, where such a cart would be parked; pushing it
   away uncovers the hatch. (Before, the hatch was 176 px off the cart it leads to.)
5. **The mouth is an opening she goes into sideways, not a vent face-on.** A face-on vent means going away
   from us and then being seen turned: the entering-and-turning the user refused. So the mouth is the end of
   a duct standing out of the forward wall, seen from the side, its cover on its end.
6. **Its floor is level with the laundry cart's rim.** The cart, pushed to its stop, ends against the mouth:
   ↓ puts her on hands and knees on the rim, ← takes her in. No climb to animate, nothing taken out of the
   player's hands, and ↓ = crawl is learned here by using it. The cart is always there when she is: it is
   solid and in her way, so the only way to the wall is to push it to the wall.
7. **No cut, no fade, going in.** The shaft is one picture with the room: the room stays in view behind her,
   the mouth's near side fades away as her head reaches it (the cut-away the decks use), the view scrolls on.
8. **The shaft is at its true place and length.** From the room's forward wall (111.8 m) to the grille at
   66.2 m: 2,200 px, about 25 s at her crawl's 88 px/s (it was 1,300 px, 15 s). She drops out where it ends:
   no jump of 21 m.
9. **It runs in the slab between decks 9 and 8.** Right behind the room's wall it slopes down 48 px, then runs
   with its floor on deck 8's ceiling line. **She slides down the slope** on her front, arms out, as her head
   reaches its lip (she is only just in: the mouth is 22 px deep), and is on her hands and knees again at its foot.
   One way, as the plan always had the duct ("9 to 8, one-way"): a wall at the slope's foot.
10. **The looks down are the ship itself.** The ship round the shaft is dark as round a room, but under each
    grille a cone of light shows deck 8 as it really is below: the midship lift hall (the lift's door, the
    DECK 8 plaque), the atrium's gallery, the atrium's stair and glass lift, its side walk, the forward lift
    hall, the party's door with its balloons and the girl dancing. Nothing is shown that is not there, and
    all of it is live. The four framed pictures are retired (`assets/ship/peeks/` is no longer loaded). The
    snoring passenger went with them: a cabin's inside is behind the corridor's wall and cannot be looked
    down into from over the corridor.
11. **Each grille is over something worth the look, and at the middle of a 2 m length of duct** (the joints
    are laid from the way out), so no joint crosses a grille.
12. **The last grille gives way under her.** It is sprung: it clapped shut behind Bumbot, and under her it
    creaks, sags and drops open; she falls out feet first where the shaft ends, onto deck 8, the deck open
    from the first moment of the fall. No key to press at the end, no kick from all fours. It hangs open
    after, and a later trip through just drops through the opening.
13. **Bumbot** leaps forward from his shelf at the cover, which comes off and ends leaning by the wall under
    the mouth; he goes into the mouth (drawn under its near side, so into it, not across it). In the run his
    eyes keep ahead of her as before, until the last grille. His own new clips are part 6 of the plan and are
    not made here.
14. **The view looks 42 px lower in the shaft**, so that deck 8's floor is in the picture under her.

## 4. How it is built

- **Data:** `SHAFT` and `LINEN` in `tools/population.py`; `LINEN_ROOM` in `tools/ship_layout.py` (the door's
  slot, `door_x`); `shaft_geometry()` in `tools/build_world.py` (written into `maps/world.json` as `duct`); a
  pushable's `goal` (the end it is pushed to, either way).
- **The room:** `tools/draw_linen.py` (drawn mirrored; its corridor door's opening flipped).
- **The shaft's art:** `tools/build_shaft.py` into `assets/ship/shaft/`. The whole shaft is drawn flat by
  rule with a real duct's features (a flanged joint every 2 m, two sheet-metal panels between joints, each
  with its cross-break crease); its pieces are redrawn by PixelLab, which keeps every shape in place and
  gives it worn steel; the build lays the redrawn pieces back along the run and lights it by rule. Sources
  and job ids: `assets/source/shaft/README.md`.
- **The game:** `buildDuct`, `updateDuct`, `shaftSlide`, `shaftDrop` in `src/world/world.js`; `SHAFT` in
  `src/config.js`; `intoTheVent` and `party` in `src/world/story.js`; the linen room's `also: 'duct'` and the
  cut-away's deck in the shaft in `src/scenes/ShipScene.js`.

15. **The mouth is 26 px deep, not 30:** at 30 its flange and cover stood on the rack's upright and the first
    bottles of Bumbot's shelf.
16. **The fallen cover stands by the wall under the mouth**, clear of where the cart parks. Lying where it fell it
    would have been under the cart's wheels.
17. **The exit's grille is the mouth's cover again, the same pixels turned** (shut in deck 8's ceiling, hanging by
    the opening after): the shaft has one kind of cover at both ends. The two pictures drawn in code are retired.
18. **The shaft is put away in the ship's outside view** (O) and in views from afar: found by pressing O inside it,
    where its dark stayed over the whole ship.
19. **The slide's sound, the grille's creak and clang, the cover's rattle** are effects the game already had
    (`slide`, `creak`, `clang`, `rattle`); none was added, so none needs the user's ear.

## 5. Not done, and why

- **Bumbot's own clips** for the leap and the squeeze: part 6 of the plan remakes him whole; he uses his present
  `jump` clip.
- **A snoring passenger:** see decision 10. He could come back truthfully as an open cabin door on deck 8 with a
  sleeper seen through it, lit from the shaft above; not built.
- **`docs/ship-regions.png` and `ship-unlock-order.png`** still draw the linen room at 112 m (it is at 115.4 m
  now): `tools/draw_regions.py` was not run again.
- **The old vent cover's two pictures** (`vent-cover`, `vent-cover-down`) are still in the things atlas, unused:
  taking them out means rebuilding that atlas.
- **A start place inside the shaft** (`?at=`): the links in `docs/start-links.md` start in the linen room, the
  second with the cart already at the mouth.

## 6. Generations

92, each job in `assets/source/shaft/README.md` (90) and `assets/source/her/shaft-slide/README.md` (2). The
balance went from 2,991 to 2,899.

| What | Generations |
|---|---|
| The steel's first tries (three PixFlux, one Pro Flash edit, one from words) | 21 |
| The shaft's seven pieces (three plain lengths, two with a grille, the dead end, the entry) | 49 |
| The mouth in the room's corner (cover on, off, fallen twice) | 20 |
| Her slide (on the dark shaft, then on the green one) | 2 |

## 7. Checked

- **Every generated picture enlarged, before it was used.** The steel: the shapes are where the flat drawing has
  them (the build lays them by its numbers); each piece's tone brought to one mean, measured where no grille's
  light reaches. The mouth: its duct is one picture in every state, only the cover changes. The slide: nine frames
  on a contrast ground, she whole in each, no fringe, her size her sheet's; its first and last frames are her crawl
  frames as the game shows them at those two spots.
- **The sequence played with real keys and looked at frame by frame at the game's pixel size:** the push, Bumbot's
  leap and the cover's fall (sixteen frames), the entry and the slide (twenty-four), the drop (thirty-four), each
  grille from near and from over it. Found and mended that way: a bright flash between the room's dark and the
  shaft's as she went in; deck 8 shown closed during the drop; Bumbot drawn outside the wall as he went in; the
  exit's grille half under the ceiling's shadow.
- **`python tools/playtest.py -j 6 boot linen region4 golden sweep region5 region6 highlight lang deck3 cabin
  deliveries keeps mishaps`** pass, but `mishaps.things`' deck 9 sprinkler, which fails the same way without these
  changes (checked with them stashed); `sound` passes run by itself (in real time it stumbled once among five
  others). `region4` has the new sequence step by step (the hatch over the laundry's cart, the cover on and off, no
  fade going in, the room still in view, the slide, deck 8 open under the shaft, a cone faint from afar and full
  over its grille, the party's grille over the party's door, the drop where the shaft ends); `golden`, `sweep` and
  `linen` were brought to the mirrored room. The whole suite was not run.
- **`python tools/check_overlaps.py`:** 0 overlaps.
- **Not judged by me:** how it feels in motion and how it sounds. That is the user's play.
