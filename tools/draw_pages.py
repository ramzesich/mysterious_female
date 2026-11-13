"""Draws the ten books' pages (GAME_DESIGN.md §6.1.2, docs/population.md §2.2): read in the
library's red chair, each book shows a page with a drawing that hints at one hidden thing on the
ship. Drawn, no words: ink on cream paper, a page number in its corner.

    python tools/draw_pages.py [--preview out.png]

Writes assets/ship/pages/page-<n>.png (150 x 100; the game shows them enlarged).
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

from palettize import palettize

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "ship" / "pages"
W, H = 150, 100
PAPER, EDGE, INK, SOFT = "#f3ecdd", "#d8cdb8", "#3e3546", "#9babb2"
RED, ORANGE, YELLOW, BLUE, GREEN = "#ae2334", "#f28c28", "#f9c22b", "#4d9be6", "#1ebc73"


def page(n):
    im = Image.new("RGBA", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK)
    d.rectangle([3, 3, W - 4, H - 4], outline=EDGE)
    d.line([(8, 6), (8, H - 7)], fill=EDGE)                   # the gutter's shadow
    for k in range(n):                                        # the page's number, as dots
        d.rectangle([W - 10 - k * 4, H - 9, W - 9 - k * 4, H - 8], fill=INK)
    return im, d


def tangerine(d, x, y):
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=ORANGE, outline=INK)
    d.point((x, y - 4), fill=GREEN)


def arrow(d, x0, y0, x1, y1, c=RED):
    d.line([(x0, y0), (x1, y1)], fill=c, width=2)
    dx, dy = (1 if x1 > x0 else -1 if x1 < x0 else 0), (1 if y1 > y0 else -1 if y1 < y0 else 0)
    if dy:
        d.polygon([(x1 - 4, y1 - 4 * dy), (x1 + 4, y1 - 4 * dy), (x1, y1 + 2 * dy)], fill=c)
    else:
        d.polygon([(x1 - 4 * dx, y1 - 4), (x1 - 4 * dx, y1 + 4), (x1 + 2 * dx, y1)], fill=c)


def glint(d, x, y, c=YELLOW):
    d.line([(x - 5, y), (x + 5, y)], fill=c)
    d.line([(x, y - 5), (x, y + 5)], fill=c)
    d.line([(x - 3, y - 3), (x + 3, y + 3)], fill=c)
    d.line([(x - 3, y + 3), (x + 3, y - 3)], fill=c)


def dash_lines(d, x, y):
    for k in range(3):
        d.line([(x - 6 - k * 5, y + k * 5 - 5), (x - 16 - k * 5, y + k * 5 - 5)], fill=INK)


def p1(d):
    """The galley's crate behind the Seven Seas' crew door."""
    d.line([(14, 80), (136, 80)], fill=INK)
    d.rectangle([24, 30, 50, 80], outline=INK)                # the crew door
    d.rectangle([33, 38, 41, 46], outline=INK)
    d.rectangle([44, 56, 47, 58], fill=INK)
    for x in (62, 66, 70):                                    # ... behind it ...
        d.rectangle([x, 60, x + 1, 61], fill=INK)
    d.rectangle([86, 54, 116, 80], outline=INK, fill=PAPER)   # the crate
    d.line([(86, 62), (116, 62)], fill=INK)
    d.line([(86, 72), (116, 72)], fill=INK)
    d.line([(96, 54), (96, 80)], fill=INK)
    d.line([(106, 54), (106, 80)], fill=INK)
    tangerine(d, 94, 49)
    tangerine(d, 106, 48)
    dash_lines(d, 84, 66)


def p2(d):
    """The trap door in the stage."""
    d.line([(14, 70), (136, 70)], fill=INK, width=2)          # the stage's edge
    for x, s in ((20, 1), (130, -1)):                         # the curtains
        d.polygon([(x, 14), (x + 14 * s, 14), (x + 8 * s, 70), (x, 70)], outline=INK, fill=RED)
    d.line([(20, 14), (130, 14)], fill=INK)
    for x in range(34, 120, 12):
        d.arc([x, 8, x + 12, 20], 0, 180, fill=INK)
    d.rectangle([64, 66, 88, 74], outline=INK, fill=PAPER)    # a square seam in the boards
    d.line([(64, 66), (88, 74)], fill=SOFT)
    arrow(d, 76, 40, 76, 62)
    d.polygon([(70, 28), (82, 28), (90, 22), (62, 22)], outline=INK)   # the spotlight over it
    d.line([(66, 28), (56, 60)], fill=YELLOW)
    d.line([(86, 28), (96, 60)], fill=YELLOW)


def p3(d):
    """The casino's machine with a glint."""
    d.line([(14, 84), (136, 84)], fill=INK)
    for i, x in enumerate((30, 62, 94)):
        d.rectangle([x, 30, x + 24, 84], outline=INK, fill=PAPER)
        d.rectangle([x + 3, 38, x + 21, 52], outline=INK)
        for k in range(3):
            d.rectangle([x + 5 + k * 6, 41, x + 8 + k * 6, 49], fill=(RED, BLUE, GREEN)[(i + k) % 3])
        d.rectangle([x + 6, 60, x + 18, 64], outline=INK)
        d.line([(x + 24, 44), (x + 29, 38)], fill=INK)
        d.ellipse([x + 27, 34, x + 31, 38], fill=RED, outline=INK)
    glint(d, 74, 26)
    glint(d, 70, 34, ORANGE)
    tangerine(d, 70, 72)
    tangerine(d, 78, 76)


def p4(d):
    """The pantry between the kitchens."""
    d.line([(14, 80), (136, 80)], fill=INK)
    for x in (20, 104):
        d.rectangle([x, 30, x + 24, 80], outline=INK)
        d.rectangle([x + 8, 38, x + 16, 46], outline=INK)
    for y in (40, 54, 68):                                    # shelves between the two doors
        d.line([(52, y), (96, y)], fill=INK)
        for x in range(54, 94, 7):
            d.rectangle([x, y - 6, x + 3, y - 1], fill=(RED, YELLOW, GREEN, BLUE)[(x + y) % 4])
    arrow(d, 46, 88, 102, 88)
    d.ellipse([124, 20, 136, 26], outline=INK)                # a tray: what the way is for
    d.line([(122, 27), (138, 27)], fill=INK)


def p5(d):
    """Deck 7's stern strip."""
    d.line([(10, 88), (140, 88)], fill=BLUE)
    for k in range(5):                                        # the stern's tiers stepping back
        x, y = 100 - k * 14, 78 - k * 14
        d.line([(20, y), (x, y)], fill=INK)
        d.line([(x, y), (x, y + 14)], fill=INK)
        d.line([(x - 8, y - 5), (x, y - 5)], fill=SOFT)
    d.line([(114, 78), (114, 88)], fill=INK)
    d.line([(100, 78), (114, 78)], fill=INK)
    d.line([(101, 72), (111, 82)], fill=RED, width=2)          # X marks the spot, on the lowest ledge
    d.line([(111, 72), (101, 82)], fill=RED, width=2)
    arrow(d, 106, 44, 106, 66)


def p6(d):
    """Los Lobos' piñata."""
    d.line([(14, 12), (136, 12)], fill=INK)
    d.line([(76, 12), (76, 30)], fill=INK)
    d.polygon([(58, 44), (72, 32), (92, 34), (100, 44), (94, 54), (64, 56)], outline=INK, fill=YELLOW)   # a donkey of paper
    d.line([(72, 32), (70, 24)], fill=INK)
    d.line([(78, 33), (78, 25)], fill=INK)
    for x in (66, 74, 86, 92):
        d.line([(x, 55), (x, 66)], fill=INK)
    for x, c in ((62, RED), (70, GREEN), (78, BLUE), (86, RED)):
        d.line([(x, 38), (x + 6, 50)], fill=c)
    dash_lines(d, 50, 48)
    tangerine(d, 70, 80)
    tangerine(d, 82, 84)
    tangerine(d, 92, 78)


def p7(d):
    """The telescope on the funnel."""
    d.line([(10, 90), (140, 90)], fill=INK)
    d.polygon([(40, 90), (60, 26), (104, 26), (112, 90)], outline=INK, fill=PAPER)   # the funnel
    for y in (42, 58, 74):
        d.line([(55 - (y - 26) // 4, y), (106 + (y - 26) // 10, y)], fill=SOFT)
    d.line([(60, 26), (104, 26)], fill=INK, width=2)
    d.line([(84, 26), (84, 16)], fill=INK)                    # the telescope on its stand
    d.line([(76, 18), (96, 10)], fill=INK, width=3)
    d.ellipse([94, 6, 100, 12], outline=INK)
    for k in range(4):                                        # what it looks at: far off, down aft
        d.line([(104 + k * 8, 14 + k * 9), (108 + k * 8, 18 + k * 9)], fill=RED)
    glint(d, 138, 52, RED)
    for x in (66, 78, 90):                                    # smoke
        d.ellipse([x, 2, x + 8, 8], outline=SOFT)


def p8(d):
    """The lighting bridge over the stage."""
    d.line([(14, 84), (136, 84)], fill=INK, width=2)
    d.line([(14, 28), (136, 28)], fill=INK)                   # the catwalk
    d.line([(14, 20), (136, 20)], fill=INK)
    for x in range(18, 136, 12):
        d.line([(x, 20), (x, 28)], fill=INK)
    for x in (40, 76, 112):                                   # lamps hung under it
        d.polygon([(x - 4, 29), (x + 4, 29), (x + 7, 37), (x - 7, 37)], outline=INK, fill=SOFT)
        d.line([(x - 6, 38), (x - 16, 80)], fill=YELLOW)
        d.line([(x + 6, 38), (x + 16, 80)], fill=YELLOW)
    d.rectangle([118, 6, 132, 18], outline=INK, fill=PAPER)   # a frame on the wall at its end
    d.rectangle([121, 9, 129, 15], outline=RED)
    arrow(d, 96, 12, 114, 12)


def p9(d):
    """The chapel's moment."""
    d.line([(14, 84), (136, 84)], fill=INK)
    d.rectangle([52, 26, 98, 84], outline=INK)                # its doors, amber glass
    d.line([(75, 26), (75, 84)], fill=INK)
    d.rectangle([57, 32, 71, 60], outline=INK, fill=YELLOW)
    d.rectangle([79, 32, 93, 60], outline=INK, fill=YELLOW)
    d.arc([48, 8, 102, 44], 180, 360, fill=INK)
    # A heart over the doors.
    d.polygon([(75, 22), (67, 13), (71, 8), (75, 12), (79, 8), (83, 13)], fill=RED, outline=INK)
    for x, y in ((40, 40), (112, 46), (36, 62), (116, 66)):   # petals
        d.ellipse([x, y, x + 3, y + 2], fill="#f68181")


def p10(d):
    """The odd book on the library's top shelf."""
    d.rectangle([24, 14, 110, 86], outline=INK)               # the bookcase
    for y in (32, 50, 68):
        d.line([(24, y), (110, y)], fill=INK)
    cols = (RED, BLUE, GREEN, YELLOW, ORANGE)
    for row, y in enumerate((32, 50, 68, 86)):
        for i, x in enumerate(range(28, 106, 6)):
            if row == 0 and i == 9:
                continue
            d.rectangle([x, y - 13 + (i * 3 + row) % 4, x + 3, y - 1], fill=cols[(i + row * 2) % 5])
    d.rectangle([82, 12, 86, 31], fill=RED, outline=INK)       # the one that sticks out
    glint(d, 84, 8)
    d.line([(118, 86), (104, 18)], fill=INK, width=2)          # the rolling ladder
    d.line([(128, 86), (114, 18)], fill=INK, width=2)
    for k in range(6):
        y = 80 - k * 11
        d.line([(117 - k * 2.3, y), (127 - k * 2.3, y)], fill=INK)


PAGES = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    done = []
    for n, fn in enumerate(PAGES, 1):
        im, d = page(n)
        fn(d)
        im = palettize(im)
        im.save(OUT / f"page-{n}.png")
        done.append(im)
    print("wrote", len(done), "pages in", OUT.relative_to(ROOT))
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        sheet = Image.new("RGBA", (W * 5 + 24, H * 2 + 12), "#1a141c")
        for i, im in enumerate(done):
            sheet.alpha_composite(im, (4 + (i % 5) * (W + 4), 4 + (i // 5) * (H + 4)))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(out)


if __name__ == "__main__":
    main()
