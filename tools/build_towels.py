"""The towel stack's sheet (2026-11-18): `assets/sprites/towels.png`, cells of 128 px, one row each of
its clips, then the standing stack and its stool apart (the stack sways on the stool before it
falls). From `assets/source/things/towel-fall/soft/` (its README): PixMiniMax clips from the game's
own stack, its towels then redrawn soft by `edit_animation` (the user, 2026-11-18). Every frame: the
stool's middle at x 36, the floor under row 119; the stack stands on the stool's top, row 108.

  fall    0-8    the stack falls alone and scatters (0: it standing, the stack's own picture)
  bury    9-17   it falls on her standing 36 px past it (0: the same stack; for her caught under
                 it standing, as it falls)
  run0..6 18-53  it falls on her as she runs past it (the user, 2026-11-18: in the standing one she
                 seemed to stop for it): each from one of her own run frames (`her/run-steady/<n>`)
                 6 px past it, she running on into the fall, to the same buried heap; the game takes
                 the one whose first frame is the pose she shows next
  emerge  54-62  her head comes up out of the heap in a towel turban, a towel swan on it
  stack   63     frame 0's stack alone (rows over 108)
  stool   64     frame 0's stool alone

python tools/build_towels.py"""
import json
from pathlib import Path
from PIL import Image
from palettize import palettize

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "things" / "towel-fall" / "soft"
CELL, TOP = 128, 108
CLIPS = ["fall", "bury", "run0", "run2", "run4", "run6", "emerge"]


def main():
    frames = []
    for clip in CLIPS:
        for i in range(9):
            frames.append(palettize(Image.open(SRC / clip / f"{i}.png")))
    first = frames[0]
    stack, stool = first.copy(), first.copy()
    stack.paste((0, 0, 0, 0), (0, TOP, CELL, CELL))
    stool.paste((0, 0, 0, 0), (0, 0, CELL, TOP))
    frames += [stack, stool]
    sheet = Image.new("RGBA", (CELL * 9, CELL * (len(CLIPS) + 1)), (0, 0, 0, 0))
    for k, f in enumerate(frames):
        sheet.alpha_composite(f, ((k % 9) * CELL, (k // 9) * CELL))
    out = ROOT / "assets" / "sprites" / "towels.png"
    sheet.save(out)
    meta = {"cell": CELL, "anims": {c: list(range(9 * n, 9 * n + 9)) for n, c in enumerate(CLIPS)},
            "stack": 9 * len(CLIPS), "stool": 9 * len(CLIPS) + 1, "middle": 36, "floor": 120, "top": TOP}
    (ROOT / "assets" / "sprites" / "towels.json").write_text(json.dumps(meta))
    print(out, sheet.size)


if __name__ == "__main__":
    main()
