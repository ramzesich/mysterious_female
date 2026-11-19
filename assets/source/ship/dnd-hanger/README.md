# The "Do Not Disturb" sign (2026-11-19; built)

The user: "redraw the door with the dnd sign: The sign should hang from the door handle, have a half round top and in the
middle of the sign it should have visible red circle, crossed"; then "It cannot hang from the tip of the door handle, it
should hang from where the door handle is mounted to the door"; and on the door's swing, "The sign should follow its
corrected hanging point, and eventually be partially obscured by the open door".

- `draw.py`: the sign, drawn by hand pixel by pixel on the palette (11 x 22 px: a pictogram below what a generation draws
  exactly): white, a half-round top with a hole, a red circle crossed, two lines of words. `hanger.png`; and the cabin door
  (`door-cabin.png`, cut from the ship atlas) with it hung on the lever's rose, the bar resting at the hole's top, the lever
  drawn over it: `door-cabin-dnd.png`. Both copied to `assets/ship/` (`dnd-hanger.png`, `door-cabin-dnd.png`).
- `swing.py`: the "Do Not Disturb" door's swing (`her-mishaps/batch-4a/door-burst-full/`, 13 frames) with the sign on the
  lever's mount of the outer face in every frame, to `door-burst-dnd/`, which `tools/build_gags.py` builds in its place.
  Frame 1 (the leaf turned about 70 degrees, its outer face still toward us): on the face, 5 px wide, the lever over it.
  Frames 2 to 10 (past edge-on, the inner face toward us): behind the leaf, its plain back peeking 4 px past the leaf's free
  edge (measured below the handle in each frame: the generated leaf's width wobbles), edge-on a 2 px strip against it.
  Frame 11: back on the outer face. Frames 0 and 12: the shut door with the sign exactly. Shown frame by frame enlarged
  (`swing-strip.png`, `swing.gif`), mended where the sign was misplaced or missing (frames 1, 3, 5 to 7, 9, 10), approved.

Used by: the seven "Do Not Disturb" doors (`DndDoor`, src/world/movers.js: shut `door-cabin-dnd`, the swing from the gags
sheet), the occupied balconies' partitions (`Occupied`, src/world/outside.js: `dnd-hanger`), cabin 8206's door inside
(`tools/draw_cabin.py`).
