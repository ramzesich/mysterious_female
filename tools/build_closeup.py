"""The intro's close-up (docs/intro.md; the user, 2026-11-14: "only her profile up from her waist
together with a part of the mirror", "she adjusts her badge (which says Bumbusik)"): her bigger,
finer portrait and the piece of her standing mirror beside it, both eight pixels to one of the
game's, so that at the close-up's zoom (16) a pixel of theirs is two of the screen's, as a pixel of
the game's is in play.

    python tools/build_closeup.py [--preview out.png]

Her portrait: `assets/source/her-close/portrait.png` (256 x 256, her profile from the waist up,
facing the mirror, on a clear ground) and `assets/source/her-close/badge/NN.png` (the same,
animated: her hand comes up to the badge and goes down again). The badge is not the generator's:
it is drawn here on every frame, BUMBUSIK in white on navy, crooked until her hand has been on it
and straight after; wherever the frame has her hand over it, the hand stays on top.
To `assets/sprites/her-close.png` (cells of 256, rows of 8) and `her-close.json` (what the game
needs to place it: src/intro.js). With no portrait in the source folder the json says so and the
intro keeps her game figure in the close-up.

The mirror: drawn here from the same measures as the cabin's (tools/draw_rooms.py `crewcabin`:
change both together), `assets/sprites/close-mirror.png`.
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "her-close"
OUT = ROOT / "assets" / "sprites"
K = 8                       # the close-up's pixels to one of the game's
CELL = 256
# Where the portrait's cell lies from her feet in the game, in the game's px: its left edge and
# its top (her head's top comes 2 px under it, at her figure's 59).
AT = (-141 / 8, -485 / 8)

# --- Her badge -------------------------------------------------------------------------------

GLYPHS = {"B": ["110", "101", "110", "101", "110"], "U": ["101", "101", "101", "101", "111"],
          "M": ["10001", "11011", "10101", "10001", "10001"], "S": ["011", "100", "010", "001", "110"],
          "I": ["1", "1", "1", "1", "1"], "K": ["101", "101", "110", "101", "101"]}
NAVY, EDGE, WHITE, SHINE = (0x32, 0x33, 0x53, 255), (0x1b, 0x1b, 0x33, 255), (0xff, 0xff, 0xff, 255), (0x4d, 0x65, 0xb4, 255)
BADGE_AT = (84, 192)        # its top left on the portrait
BLOUSE = (0xff, 0xfd, 0xf0, 255)
BADGE_W, BADGE_H = 35, 9
CROOKED = 5                 # px its far end hangs low before she straightens it
SKIP = {"02"}               # frames of the animation left out (a dark thing drawn into her fingers)


def badge(skew=0, text="BUMBUSIK"):
    """The badge, and how far above its place its picture starts. Crooked, it steps down between
    its letters, never through one."""
    flat = Image.new("RGBA", (BADGE_W, BADGE_H), NAVY)
    d = ImageDraw.Draw(flat)
    d.rectangle([0, 0, BADGE_W - 1, BADGE_H - 1], outline=EDGE)
    d.line([(1, 1), (BADGE_W - 2, 1)], fill=SHINE)
    x, spans = 2, []
    for ch in text:
        g = GLYPHS[ch]
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == "1":
                    flat.putpixel((x + i, 2 + j), WHITE)
        spans.append((x, x + len(g[0])))
        x += len(g[0]) + 1
    if not skew:
        return flat, 0
    out = Image.new("RGBA", (BADGE_W, BADGE_H + skew), (0, 0, 0, 0))
    for x in range(BADGE_W):
        letter = min(spans, key=lambda s: abs((s[0] + s[1] - 1) / 2 - x))
        mid = (letter[0] + letter[1] - 1) / 2
        out.alpha_composite(flat.crop((x, 0, x + 1, BADGE_H)), (x, round(skew * mid / (BADGE_W - 1))))
    return out, skew // 2


def is_hand(px):
    """Her hand over the badge: skin, or the dark line round it (not the badge's own navy)."""
    r, g, b, a = px
    if a < 128:
        return False
    skin = r > 190 and g > 130 and b > 100 and r - b > 40
    line = r < 60 and g < 40 and b < 50 and r >= b - 6          # the outline's warm black, not navy
    return skin or line


def with_badge(frame, skew):
    """The frame with the badge drawn in its place, her hand (where the frame has it there) kept
    on top of it."""
    out = frame.copy()
    # (First the generator's own try at a badge goes: its navy, anywhere round the badge's place,
    # becomes blouse.)
    for y in range(BADGE_AT[1] - 8, BADGE_AT[1] + BADGE_H + 8):
        for x in range(BADGE_AT[0] - 6, BADGE_AT[0] + BADGE_W + 6):
            r, g, b, a = frame.getpixel((x, y))
            if a and b > r + 12 and r < 120 and g < 130:
                out.putpixel((x, y), BLOUSE)
    art, up = badge(skew)
    x0, y0 = BADGE_AT[0], BADGE_AT[1] - up
    for y in range(art.height):
        for x in range(art.width):
            px = art.getpixel((x, y))
            if px[3] and not is_hand(frame.getpixel((x0 + x, y0 + y))):
                out.putpixel((x0 + x, y0 + y), px)
    return out


def hand_on_badge(frame):
    """How much of the badge's place her hand covers in this frame (0 to 1)."""
    n = sum(is_hand(frame.getpixel((BADGE_AT[0] + x, BADGE_AT[1] + y))) and frame.getpixel((BADGE_AT[0] + x, BADGE_AT[1] + y))[0] > 190
            for y in range(BADGE_H) for x in range(BADGE_W))
    return n / (BADGE_W * BADGE_H)


def portrait():
    """The sheet's frames: the still (the badge crooked), then the animation; the badge straight
    from the frame her hand has been on it longest."""
    still = SRC / "portrait.png"
    if not still.exists():
        return None
    frames = [Image.open(still).convert("RGBA")] + [Image.open(p).convert("RGBA") for p in sorted((SRC / "badge").glob("*.png"))
                                                    if p.stem not in SKIP]
    cover = [hand_on_badge(f) for f in frames]
    fixed = max(range(len(frames)), key=lambda i: cover[i]) if max(cover) > 0.05 else len(frames)
    out = []
    for i, f in enumerate(frames):
        assert f.size == (CELL, CELL), f.size
        # (Not snapped to the game's palette: it has no pale blues, and her blouse's soft shading
        # came out sky blue. The portrait keeps the colours it was drawn in.)
        out.append(with_badge(f, CROOKED if i < fixed else 0))
    return out, fixed


# --- Her standing mirror, finer ----------------------------------------------------------------

FLOOR = 72                  # the mirror's picture: the cabin's x 2..27, from 72 px over its floor down
MIRROR_AT = (2, -FLOOR)     # ...its top left from the cabin's left edge and floor, in the game's px
WOOD, WOOD_DARK, WOOD_LIGHT, WOOD_DEEP = "#ab947a", "#7a4528", "#d8b29a", "#5a3020"
GLASS, GLASS_LIGHT, GLASS_DEEP, BRASS, BRASS_DARK = "#b7dff2", "#d6f0fa", "#9fd0ea", "#f9c22b", "#b9722c"


def mirror():
    w, h = 25 * K, FLOOR * K
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    X = lambda x: round((x - 2) * K)                 # the cabin's x to the picture's
    Y = lambda up: round((FLOOR - up) * K)           # px over the floor to the picture's y
    top, foot = 69, 8
    # The posts, a round knob on each, a foot under each; the stretcher between them.
    for x in (5, 22):
        d.rectangle([X(x), Y(44), X(x + 2) - 1, Y(3)], fill=WOOD_DARK)
        d.rectangle([X(x) + 3, Y(44), X(x) + 6, Y(3)], fill="#96573a")
        d.rectangle([X(x + 2) - 3, Y(44), X(x + 2) - 1, Y(3)], fill=WOOD_DEEP)
        d.ellipse([X(x) - 3, Y(47.4), X(x + 2) + 2, Y(44.2)], fill=WOOD_DARK, outline=WOOD_DEEP)
        d.ellipse([X(x) + 1, Y(47), X(x) + 7, Y(46.2)], fill="#96573a")
        d.rounded_rectangle([X(x - 2), Y(3), X(x + 4) - 1, Y(0) - 1], radius=6, fill=WOOD_DARK, outline=WOOD_DEEP)
        d.line([(X(x - 2) + 5, Y(3) + 3), (X(x + 4) - 6, Y(3) + 3)], fill="#96573a", width=2)
    d.rectangle([X(7), Y(4.6), X(22), Y(3.6)], fill=WOOD_DARK)
    d.line([(X(7), Y(4.6)), (X(22), Y(4.6))], fill="#96573a", width=2)
    # The frame, its far edge (the right one) a little shorter, and the glass in it.
    frame = [(X(8), Y(top)), (X(21), Y(top - 2)), (X(21), Y(foot + 2)), (X(8), Y(foot))]
    d.polygon(frame, fill=WOOD_DARK)
    inset = lambda p, a, b: [(p[0][0] + a, p[0][1] + b), (p[1][0] - a, p[1][1] + b), (p[2][0] - a, p[2][1] - b), (p[3][0] + a, p[3][1] - b)]
    d.polygon(inset(frame, 3, 3), fill=WOOD)
    d.polygon(inset(frame, 5, 5), fill=WOOD_LIGHT)
    d.polygon(inset(frame, 8, 8), fill=WOOD)
    d.polygon(inset(frame, 13, 14), fill=WOOD_DARK)
    glass = inset(frame, 16, 17)
    d.polygon(glass, fill=GLASS)
    # (The light on the glass: paler toward the top, two bright streaks, a deeper foot.)
    gx0, gx1 = glass[0][0], glass[1][0]
    d.polygon([glass[0], glass[1], (gx1, glass[1][1] + 90), (gx0, glass[0][1] + 150)], fill=GLASS_LIGHT)
    d.polygon([(gx0, glass[3][1] - 60), (gx1, glass[2][1] - 34), glass[2], glass[3]], fill=GLASS_DEEP)
    for a, b, wd in (((gx0 + 14, Y(30)), (gx0 + 62, Y(58)), 9), ((gx0 + 34, Y(24)), (gx0 + 70, Y(45)), 4),
                     ((gx0 + 10, Y(14)), (gx0 + 40, Y(31)), 5)):
        d.line([a, b], fill=(255, 255, 255, 255), width=wd)
    # The pivots, brass, where the posts hold the frame.
    for x in (6.6, 22.4):
        d.ellipse([X(x) - 7, Y(38) - 7, X(x) + 7, Y(38) + 7], fill=BRASS, outline=BRASS_DARK)
        d.ellipse([X(x) - 3, Y(38) - 4, X(x), Y(38) - 1], fill="#fbff86")
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    glass = mirror()
    glass.save(OUT / "close-mirror.png")
    meta = {"portrait": False, "perWorld": K, "mirror": {"at": list(MIRROR_AT)}}
    made = portrait()
    if made:
        frames, fixed = made
        cols = 8
        sheet = Image.new("RGBA", (cols * CELL, -(-len(frames) // cols) * CELL), (0, 0, 0, 0))
        for i, f in enumerate(frames):
            sheet.alpha_composite(f, ((i % cols) * CELL, (i // cols) * CELL))
        sheet.save(OUT / "her-close.png")
        meta.update(portrait=True, cell=CELL, at=list(AT), frames={"stand": 0, "badge": list(range(1, len(frames))), "fixed": fixed})
        print(f"her-close.png: {len(frames)} frames, the badge straight from frame {fixed}")
    else:
        print("no portrait in assets/source/her-close: the intro keeps her game figure in the close-up")
    (OUT / "her-close.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    if "--preview" in sys.argv:
        # Everything as the close-up shows it: the mirror and her at their places, two screen px each.
        left, top = -1, 63                     # the view's left edge in the cabin, its top over the floor
        view = Image.new("RGBA", (60 * K, 34 * K), (0xc7, 0xdc, 0xd0, 255))
        view.alpha_composite(glass, ((MIRROR_AT[0] - left) * K, (top + MIRROR_AT[1]) * K))
        if made:
            view.alpha_composite(made[0][-1], (round((34 + AT[0] - left) * K), round((top + AT[1]) * K)))
        view.save(sys.argv[sys.argv.index("--preview") + 1])


if __name__ == "__main__":
    main()
