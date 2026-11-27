# Splash Academy's four kids (plan-the-rest §7f; the user, 2026-11-27)

The toddlers and the counsellor taken out ("let's remove all of kids plus the counselor there"); of four themes the user
took two, "1 and 2": the pillow siege over the pillow castle and tag between the doorway from Entourage and the castle,
the kids 6 to 9. Pro characters in the pool kid's style (`style_character_id` 59b5cce6, the kid with the water pistol),
64 px, side view, 10 generations each; approved as first drawn.

| Cast | Character | Look |
|---|---|---|
| `splash_king` | `bca491aa-ae9e-404b-8756-b3b4adf17d88` | boy, 8, gold paper crown, red towel cape, green T-shirt: the siege's aft side |
| `splash_knight` | `3b9cc743-4249-432d-964c-90ded062d9c6` | girl, 7, silver cardboard knight's helmet, blonde pigtails, dungarees: its forward side |
| `splash_chaser` | `422068f9-c163-4304-8776-cb8e8b4984ce` | boy, 6, ginger curls, striped shirt: tag |
| `splash_runner` | `46e5e7a8-ce29-4f92-823b-ff7bfb953977` | girl, 9, ponytail, pink hoodie: tag |

Clips (`get_character` has their frames; `tools/fetch_people.py` the four, the siege's two only by name, `BY_HAND`):

- the king's and the knight's `duck` (v3, 8 frames, 1 generation each) and `cheer` (v3, 8, 1 each);
- their `throw`: **PixMiniMax** from their stand with the pillow lying at their toes (`throw2/start.png`) to their stand
  (`throw2/end.png`), 16 frames, `de5aee3d-aee8-451b-a28a-925b0a59dbf0` (king), `caf6d4f4-ee83-401b-afb1-e918892e845e`
  (knight), 1 generation each; cut by `throw2/cut.py` (the world's pillow lying still until their hands take it, frames 3
  and 5; from the frame it leaves their hands, 12 and 13, the generator's flying pillow out); `throw2/measure.py` gives
  where it lies and where it leaves the hands (`SIEGE.release` in `src/config.js`) and the world's pillow
  (`assets/source/things/splash-pillow.png`, a stray speck taken out). Their first throw (v3, 16 frames, 2 generations
  each) ended mid-lunge and would have popped back to the stand: `first-throw/`, unused;
- the chaser's and the runner's `run` (skeleton-v3 running-8-frames, 3 each) and `freeze` (v3, 8, 1 each).

All four shrunk whole (`"canvas": True` in `tools/cast.py`, a new option of `tools/build_people.py`'s `shrunk`): shrunk
by their outline's middle, the pillow at the toes moved the figure. 40 generations for the four, 22 for the clips.
