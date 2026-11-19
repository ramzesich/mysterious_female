"""The court's two players (deck 12; the user, 2026-11-19: "place two different basketball players on either side
(slightly backgrounded in terms of colors) and make them throw the balls through their respective rings"), from
`assets/source/people/court/<man|woman>/` (its README has the ids) to `assets/sprites/court.png` + `.json`.

Each is a pro character in the cast's style, east-facing on a 96 px canvas (feet on row 93), with four clips made with
the ball (PixMiniMax):
  shoot    from holding the ball at the chest: a jump shot; the ball is over the head in frame 7 and gone from frame 8
           (the generator's ball flying off in frame 8 is cut out: the game's ball takes over from frame 7's spot,
           `release`), landing back on the stand
  idle     the stand, breathing (while the ball is out)
  pick     from the stand with the game's own ball lying at the toes (`rest`, its middle): bending, the ball taken up
           in both hands, back to holding it; the ball is the game's until frame 3 (`grab`): out of frames 0 to 2
  dribble  from holding, one bounce in front of the feet, back to holding
Everything is washed 12% toward the corridor wall, as the theatre's people (the ball in their hands too: the game's
ball changes to and from its own washed picture, `basketball-lt`, at the hand-overs).

python tools/build_court.py"""
import json
from pathlib import Path
from PIL import Image
from palettize import palettize

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "people" / "court"
CELL = 96
WHO = ("man", "woman")
CLIPS = (("shoot", 13), ("idle", 5), ("pick", 9), ("dribble", 9))
WASH = 0.12
WALL = (0xE9, 0xDF, 0xCC)
# The ball over the head at the release (frame 7), and the game's ball lying at the toes in `pick-start.png` (its
# middle), on the canvas; measured from the frames.
BALL = {"man": {"release": [49, 21], "rest": [61, 90]}, "woman": {"release": [47, 26], "rest": [60, 90]}}
GRAB = 3


def pieces(im):
    a = im.load(); w, h = im.size; seen = set(); out = []
    for y in range(h):
        for x in range(w):
            if a[x, y][3] and (x, y) not in seen:
                st = [(x, y)]; seen.add((x, y)); comp = []
                while st:
                    p = st.pop(); comp.append(p)
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            q = (p[0] + dx, p[1] + dy)
                            if 0 <= q[0] < w and 0 <= q[1] < h and q not in seen and a[q][3]:
                                seen.add(q); st.append(q)
                out.append(comp)
    return sorted(out, key=len, reverse=True)


def biggest(im):
    """Only the figure: the ball the generator sent flying off is a piece of its own."""
    out = Image.new("RGBA", im.size); a, o = im.load(), out.load()
    for p in pieces(im)[0]:
        o[p] = a[p]
    return out


def without_ball(im, who):
    """The lying ball taken out (the game draws its own there until the hands take it): its 9 x 9 box at the toes,
    the pixels near its own colours."""
    ball = Image.open(ROOT / "assets" / "source" / "people" / "court" / who / "pick-start.png").convert("RGBA")
    cx, cy = BALL[who]["rest"]
    cols = {ball.getpixel((x, y))[:3] for x in range(cx - 4, cx + 5) for y in range(cy - 4, cy + 5) if ball.getpixel((x, y))[3]}
    out = im.copy(); px = out.load()
    for x in range(cx - 5, cx + 6):
        for y in range(cy - 5, min(cy + 6, CELL)):
            c = px[x, y]
            if c[3] and min(sum((u - v) ** 2 for u, v in zip(c[:3], k)) for k in cols) < 40 ** 2:
                px[x, y] = (0, 0, 0, 0)
    # (And the specks of its edge left loose.)
    for comp in pieces(out)[1:]:
        if len(comp) < 6:
            for q in comp:
                px[q] = (0, 0, 0, 0)
    return out


def washed(img):
    out = img.copy(); px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (*(round(c + (w - c) * WASH) for c, w in zip((r, g, b), WALL)), a)
    return out


def main():
    rows = [(who, clip, n) for who in WHO for clip, n in CLIPS]
    cols = max(n for _, _, n in rows)
    sheet = Image.new("RGBA", (CELL * cols, CELL * len(rows)))
    anims = {who: {} for who in WHO}
    for r, (who, clip, n) in enumerate(rows):
        anims[who][clip] = []
        for i in range(n):
            im = Image.open(SRC / who / clip / f"{i}.png").convert("RGBA")
            if clip == "shoot" and i >= 8:
                im = biggest(im)
            if clip == "pick" and i < GRAB:
                im = without_ball(im, who)
            sheet.alpha_composite(washed(palettize(im)), (i * CELL, r * CELL))
            anims[who][clip].append(r * cols + i)
    out = ROOT / "assets" / "sprites" / "court.png"
    sheet.save(out)
    meta = {"cell": CELL, "feet": 93, "anims": anims, "ball": BALL, "release": 8, "grab": GRAB}
    (ROOT / "assets" / "sprites" / "court.json").write_text(json.dumps(meta))
    print(out, sheet.size)


if __name__ == "__main__":
    main()
