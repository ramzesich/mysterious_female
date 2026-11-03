"""Draws by hand, in strict side view, what PixelLab kept drawing at three-quarters (the user,
2026-11-03): the casino's roulette and blackjack tables, and the Stardust balcony's front, a
velvet-padded parapet with a brass rail seen end-on (its height is the railing she hops). Resurrect
64 colours, a one-colour outline like the other pieces on board.

Writes assets/source/ship/casino-drawn/frame_0.png (roulette), frame_1.png (blackjack),
frame_2.png (the balcony's parapet). Run from the repo root: python tools/draw_casino.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "source" / "ship" / "casino-drawn"
OUTLINE = (0x2e, 0x22, 0x2f, 255)


def outlined(im):
    """A one-colour outline round the silhouette."""
    a = im.split()[3].load()
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if a[x, y]:
                continue
            if any(0 <= x + dx < im.width and 0 <= y + dy < im.height and a[x + dx, y + dy]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = OUTLINE
    return im


def chips(d, x, top, colours):
    for i, c in enumerate(colours):
        d.rectangle([x, top - 2 * i - 2, x + 4, top - 2 * i - 1], fill=c)
        d.line([(x, top - 2 * i - 2), (x + 4, top - 2 * i - 2)], fill="#ffffff")


def roulette():
    im = Image.new("RGBA", (62, 38), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in (4, 54):                                         # legs, turned, dark wood
        d.rectangle([x, 22, x + 4, 37], fill="#46291f")
        d.line([(x + 1, 22), (x + 1, 37)], fill="#6e2727")
    d.rectangle([2, 12, 60, 22], fill="#6e2727")              # the apron, mahogany
    d.rectangle([5, 14, 57, 20], fill="#7a3045")
    d.line([(2, 12), (60, 12)], fill="#d9a43b")               # gold trim
    d.line([(2, 22), (60, 22)], fill="#d9a43b")
    d.rectangle([1, 9, 61, 11], fill="#239063")               # the felt's edge
    d.line([(1, 8), (61, 8)], fill="#4c3e24")                 # its wooden rail
    d.rectangle([6, 3, 26, 8], fill="#46291f")                # the wheel's bowl over the top
    d.line([(6, 3), (26, 3)], fill="#d9a43b")
    d.rectangle([9, 4, 23, 5], fill="#ae2334")
    d.rectangle([15, 0, 17, 3], fill="#f9c22b")               # its spindle
    chips(d, 36, 8, ["#e83b3b", "#ffffff", "#e83b3b"])
    chips(d, 44, 8, ["#4d65b4", "#ffffff", "#4d65b4", "#ffffff"])
    return outlined(im)


def blackjack():
    im = Image.new("RGBA", (62, 38), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in (14, 40):                                        # two pedestals on wide feet
        d.rectangle([x, 20, x + 8, 35], fill="#46291f")
        d.line([(x + 2, 20), (x + 2, 35)], fill="#6e2727")
        d.rectangle([x - 3, 35, x + 11, 37], fill="#46291f")
    d.rounded_rectangle([1, 13, 61, 21], radius=4, fill="#6e2727")   # the body, mahogany
    d.line([(4, 20), (58, 20)], fill="#d9a43b")
    d.rounded_rectangle([0, 8, 62, 13], radius=3, fill="#2e222f")    # the padded leather rail
    d.line([(3, 9), (59, 9)], fill="#625565")
    d.line([(4, 7), (58, 7)], fill="#239063")                 # the felt peeking over it
    for x in (24, 31):                                        # two cards standing on the felt
        d.rectangle([x, 2, x + 4, 7], fill="#ffffff")
        d.point((x + 1, 3), fill="#e83b3b")
    chips(d, 44, 7, ["#e83b3b", "#ffffff", "#1ebc73"])
    chips(d, 50, 7, ["#2e222f", "#ffffff"])
    return outlined(im)


def parapet():
    im = Image.new("RGBA", (22, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([2, 6, 19, 31], fill="#ae2334")               # deep red velvet padding
    for x in (6, 10, 14):
        d.line([(x, 8), (x, 29)], fill="#831c5d")             # its folds
    d.rectangle([2, 6, 3, 31], fill="#d9a43b")                # gold trim
    d.rectangle([18, 6, 19, 31], fill="#d9a43b")
    d.line([(2, 29), (19, 29)], fill="#d9a43b")
    d.rounded_rectangle([0, 1, 21, 5], radius=2, fill="#f9c22b")   # the brass handrail on top
    d.line([(1, 5), (20, 5)], fill="#d9a43b")
    d.line([(3, 2), (12, 2)], fill="#fbff86")
    return outlined(im)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for i, draw in enumerate((roulette, blackjack, parapet)):
        draw().save(OUT / f"frame_{i}.png")
    print("wrote", OUT.relative_to(ROOT))
