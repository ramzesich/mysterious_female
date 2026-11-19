"""The hanger swung with its door (the user, 2026-11-19: "Swing"; then: "The sign should follow its corrected
hanging point, and eventually be partially obscured by the open door"): the "Do Not Disturb" door's own swing
(`her-mishaps/batch-4a/door-burst-full/`, 13 frames) with the hanger (`draw.py`) on the lever's mount of the door's
OUTER face in every frame, to `her-mishaps/batch-4a/door-burst-dnd/`, which `tools/build_gags.py` builds in its
place.

The leaf swings out toward us on its hinge at the right: by frame 1 it is turned about 70 degrees, still showing its
outer face; from frame 2 to 10 it is past edge-on and shows its inner face (the handle the clip draws there is the
inner one), so the sign is on the far side of the leaf: hidden by it, but for what reaches past the leaf's free edge
(it hangs a few px off the face, the rose's depth, which turns sideways as the leaf turns); frame 11 shows the outer
face again. Each frame, measured by hand on the clip's pixels (cell px): the mount's column (the rose; past
edge-on, the lock plate's middle, the same place through the leaf), the lever's row, the leaf's turn (degrees, from
its width against the shut door's), and whether the outer face is toward us. The sign's width is 11 x |cos| (to 9:
its circle's white margins go); seen from behind it is its plain back."""
import math
from pathlib import Path
from PIL import Image
from draw import hanger, O, W, ROWS

HERE = Path(__file__).resolve().parent
CLIPS = HERE.parents[1] / "her-mishaps" / "batch-4a"
DEPTH = 3           # px from the leaf's face to the sign (the rose)
PEEK = 4            # px of the sign past the open leaf's free edge (at most its width there)
#         mount, row, turn, outer face toward us
FRAMES = [(32, 86, 0, True), (44, 87, 70, True), (60, 87, 125, False), (69, 86, 180, False), (70, 86, 137, False),
          (70, 86, 137, False), (69, 86, 180, False), (67, 87, 180, False), (61, 87, 130, False), (51, 87, 107, False),
          (48, 87, 93, False), (41, 87, 49, True), (32, 86, 0, True)]
# (The lever over the sign on the faces that show it: the clip's own pixels on these offsets from the mount.)
LEVER = [(dx, -1) for dx in range(0, 6)] + [(dx, 0) for dx in range(-1, 7)] + [(dx, 1) for dx in range(0, 6)] + [(0, 2), (1, 2)]

def back():
    """The sign's back: its outline and plain card."""
    h = hanger()
    px = h.load()
    for y in range(h.height):
        for x in range(h.width):
            if px[x, y][3] and px[x, y][:3] != O:
                px[x, y] = (*W, 255)
    # (Its hole stays a hole.)
    for r in range(3, 6):
        for c in range(4, 7):
            px[c, r] = (0, 0, 0, 0)
    for c in range(4, 7):
        px[c, 2] = (*O, 255)
        px[c, 6] = (*O, 255)
    return h

def squeezed(h, w):
    if w >= h.width:
        return h
    cols = [0, 2, 3, 4, 5, 6, 7, 8, 10] if w == 9 else [5, 10] if w == 2 else [round(i * (h.width - 1) / (w - 1)) for i in range(w)] if w > 1 else [5]
    out = Image.new("RGBA", (len(cols), h.height))
    for x, c in enumerate(cols):
        out.paste(h.crop((c, 0, c + 1, h.height)), (x, 0))
    return out

def main():
    front, rear = hanger(), back()
    dst = CLIPS / "door-burst-dnd"
    dst.mkdir(exist_ok=True)
    shut = Image.open(HERE / "door-cabin-dnd.png").convert("RGBA")
    for i, (mount, row, turn, outer) in enumerate(FRAMES):
        src = Image.open(CLIPS / "door-burst-full" / f"{i}.png").convert("RGBA")
        if turn == 0:
            # (Shut: the door with the sign exactly.)
            out = src.copy()
            out.paste(shut, (23, 47))
            out.save(dst / f"{i}.png")
            continue
        c = abs(math.cos(math.radians(turn)))
        w = max(1, round(11 * c))
        w = 9 if 8 <= w <= 9 else w
        if outer and turn > 60:
            w = 5           # (frame 1: the leaf's face is 10 px; on it, readable)
        g = squeezed(front if outer else rear, max(w, 2))
        top = row - 3
        if outer:
            # (The hole's middle on the mount.)
            left = round(mount - (g.width - 1) / 2)
        else:
            # (Behind the leaf: its far edge `PEEK` px past the leaf's free edge there, more while the leaf is
            # turned across our view, as the sign's few px off the face turn sideways; the leaf's own edge is
            # measured in each frame, the generated leaf's width wobbling from frame to frame.)
            # (Edge-on, it is a strip against the leaf's side.) The edge measured below the handle, which sticks out.
            edge = max(x for x in range(mount - 15, mount + 16) for y in range(row + 6, top + g.height)
                       if src.getpixel((x, y))[3])
            left = edge + min(PEEK, g.width) - g.width + 1
        out = src.copy()
        gx = g.load()
        for y in range(g.height):
            for x in range(g.width):
                if not gx[x, y][3]:
                    continue
                X, Y = left + x, top + y
                # (Behind the leaf: only where the clip shows nothing there.)
                if not outer and src.getpixel((X, Y))[3]:
                    continue
                out.putpixel((X, Y), gx[x, y])
        if outer and turn > 60:
            # (Frame 1: the lever as the clip draws it, pointing off the free edge, over the sign's top.)
            for X in range(left - 4, left + 1):
                for Y in range(row - 1, row + 2):
                    p = src.getpixel((X, Y))
                    if p[3]:
                        out.putpixel((X, Y), p)
        elif outer:
            for dx, dy in LEVER:
                X = mount + round(dx * c) * (1 if turn < 90 else -1)
                p = src.getpixel((X, row + dy))
                if p[3] and p[:3] != (205, 104, 61):
                    out.putpixel((X, row + dy), p)
        out.save(dst / f"{i}.png")

if __name__ == "__main__":
    main()
