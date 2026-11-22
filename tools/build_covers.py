"""The fourteen books' covers (plan-the-rest §2.3; GAME_DESIGN.md §6.1.2): each her own copy's cover, photographed by
the user (`reference/books/`, git-ignored), straightened, its words painted out, redrawn as pixel art by PixelLab
(`image_to_pixelart`, 120 x 180, the redrawn mode: the user's choice of two, 2026-11-22), and its title and author set
back in here, where the cover has them and in its colours, in Pixelzone (CC0, `assets/source/pages/`), the pages'
lettering, which has every script the titles need (drawn exactly as designed: `tools/pixelzone.py`). Words the
generator would smear are never generated.

A cover's picture is its try, `assets/source/covers/tries/<nn>-a.png` (their job ids in `assets/source/covers/README.md`),
with the few mends in `MENDS` (colours the generator changed put back, a leftover of a painted-out word, a band made
room for two lines). Atomic Habits (1) is lettering on white and nothing else: it has no try, its gold dust is drawn here.

Each line of lettering is `L(text, x, y, ...)`: x is its left, middle or right edge by `align` ("l", "c", "r"), y the top
of its letters' box; `scale` whole (2 doubles every pixel); `turn` 90 reads from the bottom up (a spine); `step` lifts
each letter that many px above the one before (a title along a slanted tag: slanted by whole letters, never through
one); `gap` the px between words in place of the font's space; `tight` letters enlarged but 1 px apart (a long title
across a narrow cover); `outline` a 1 px ring in that colour. Hebrew is drawn
right to left.

    python tools/build_covers.py [--preview out.png]

Writes assets/ship/covers/cover-<n>.png (120 x 180; shown at 2x in the middle of the screen when she gets the book),
and mini-<n>.png (18 x 24, the row she chooses from: her cover's picture without its lettering, the same mends, redrawn
by PixelLab at 16 x 22 (`assets/source/covers/mini/<nn>.png`, the user's word, 2026-11-22: "Use the covers without the
text") in a 1 px dark outline).
"""

import random
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import pixelzone

ROOT = Path(__file__).resolve().parent.parent
TRIES = ROOT / "assets" / "source" / "covers" / "tries"
MINI = ROOT / "assets" / "source" / "covers" / "mini"
OUT = ROOT / "assets" / "ship" / "covers"
W, H = 120, 180
HEBREW = re.compile(r"[֐-׿]")


def L(text, x, y, scale=1, colour=(0, 0, 0), align="c", turn=0, step=0, gap=None, outline=None, tight=False):
    return dict(text=text, x=x, y=y, scale=scale, colour=colour, align=align, turn=turn, step=step, gap=gap,
                outline=outline, tight=tight)


INK = (28, 26, 30)
GOLD = (176, 146, 86)
COVERS = {
    1: [L("Tiny Changes,", 60, 12, colour=INK), L("Remarkable Results", 60, 24, colour=INK),
        L("Atomic", 60, 44, 4, GOLD), L("Habits", 60, 86, 4, GOLD),
        L("An Easy & Proven Way", 60, 128, colour=INK), L("to Build Good Habits", 60, 139, colour=INK),
        L("& Break Bad Ones", 60, 150, colour=INK), L("James Clear", 60, 161, 2, INK)],
    2: [L("J.K. ROWLING", 60, 2, colour=(226, 244, 226)), L("HARRY POTTER", 60, 13, 2, (226, 244, 226)),
        L("and the Chamber of Secrets", 60, 34, colour=(226, 244, 226)),
        L("SLYTHERIN", 60, 118, colour=(206, 212, 206))],
    3: [L("ЮРІЙ", 59, 23, colour=(0, 60, 140)), L("ВИННИЧУК", 59, 37, colour=(0, 60, 140)),
        L("ТАНҐО СМЕРТІ", 60, 140, 2, (254, 190, 4))],
    4: [L("Lucy Dillon", 60, 7, 2, (172, 140, 84)), L("unexpected", 60, 32, 2, (178, 28, 40)),
        L("lessons", 60, 54, 2, (178, 28, 40)), L("in", 60, 74, 2, (178, 28, 40)),
        L("love", 60, 92, 2, (178, 28, 40))],
    5: [L("Євгенія Подобна", 60, 30, colour=(240, 240, 232)), L("ЇЇ ВІЙНА", 62, 96, 2, (16, 18, 12)),
        L("25 історій", 56, 127, colour=(240, 240, 232)), L("про сміливість,", 56, 138, colour=(240, 240, 232)),
        L("силу і любов", 56, 149, colour=(240, 240, 232))],
    6: [L("J.K. ROWLING", 60, 2, colour=(96, 222, 172)), L("HARRY POTTER", 60, 13, 2, (96, 222, 172)),
        L("and the Philosopher's Stone", 60, 34, colour=(96, 222, 172)),
        L("SLYTHERIN", 60, 121, colour=(96, 222, 172))],    # (her copy's "PRIDE / AMBITION / CUNNING" left off: the user)
    7: [L("Артем Чапай", 60, 5, 2, (36, 34, 36)), L("ПОНАЇХАЛИ", 26, 82, 2, (196, 28, 36), "l", step=-3)],
    8: [L("Małgorzata", 117, 24, colour=(24, 30, 48), align="r"),
        L("Gutowska-Adamczyk", 117, 34, colour=(24, 30, 48), align="r"),
        L("Niebieskie nitki", 60, 76, 2, (250, 250, 250), gap=5, tight=True)],
    9: [L("АРКАДИЙ", 4, 4, colour=(250, 250, 250), align="l", outline=INK),
        L("ЛЬВОВ", 4, 15, colour=(250, 250, 250), align="l", outline=INK),
        L("ДВОР", 4, 26, 3, (250, 250, 250), "l", outline=INK),
        L("КНИГА ТРЕТЬЯ", 4, 56, colour=(250, 250, 250), align="l", outline=INK)],
    10: [L("Рафаил ГРУГМАН", 117, 8, colour=(30, 24, 20), align="r"),
         L("БОРЯ, ВЫЙДИ С МОРЯ", 6, 170, 2, (30, 24, 20), "l", 90)],
    11: [L("נערה", 60, 28, 2, (122, 30, 34)), L("במעיל", 60, 48, 2, (122, 30, 34)),
         L("כחול", 60, 68, 2, (122, 30, 34)), L("מוניקה הסה", 60, 90, colour=(40, 34, 40))],
    12: [L("Dorota Terakowska", 4, 70, colour=(250, 250, 250), align="l"),
         L("POCZWARKA", 60, 82, 3, (150, 214, 238))],
    13: [L("DAUGHTERS", 60, 20, 3, (250, 250, 248)), L("of", 60, 50, 2, (226, 180, 100), outline=(52, 28, 18)),
         L("WARSAW", 60, 66, 3, (250, 250, 248)), L("MARIA FRANCES", 60, 152, 2, (214, 168, 92))],
    14: [L("PACHINKO", 42, 102, 2, (253, 240, 205)), L("MIN JIN LEE", 42, 126, colour=(253, 240, 205))],
}


# ---- the tries' mends -------------------------------------------------------------------------------------------
def grey_of(a):
    return (a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11)


def mend_3(a):
    # The plate's thin dark rule inside its gold frame, made the plate's cream: room for the author's two lines.
    reg = a[19:51, 26:93]
    reg[reg[..., :3].sum(2) < 300] = a[30, 40]


def mend_5(a):
    # A leftover of the painted-out subtitle (a grey patch) in the dark block, made the block's own colour.
    reg = a[140:172, 22:92]
    block = np.median(reg[reg[..., :3].sum(2) < 120][:, :3], 0)
    reg[(reg[..., :3].sum(2) >= 120), :3] = block


def mend_7(a):
    # The bag came blue; her copy's is grey: its bluish pixels to the grey of their own lightness.
    rgb = a[..., :3].astype(float)
    blue = rgb[..., 2] > rgb[..., 0] + 12
    g = grey_of(rgb)
    for c in range(3):
        rgb[..., c] = np.where(blue, g, rgb[..., c])
    a[..., :3] = rgb.clip(0, 255).astype(np.uint8)


def mend_8(a):
    # The blue bands made tall enough for the author's two lines and the doubled title.
    band = np.array([150, 196, 222])
    rgb = a[..., :3]
    pix = rgb[(rgb[..., 2] > 170) & (rgb[..., 0] < 150) & (rgb[..., 1] > 140)]
    if len(pix):
        band = np.median(pix, 0)
    a[21:46, 42:120, :3] = band
    a[72:95, 0:120, :3] = band


def mend_9(a):
    # The photo came sepia; her copy's is black and white but for the window's blue: everything else to grey.
    rgb = a[..., :3].astype(float)
    keep = rgb[..., 2] > rgb[..., 0] + 15
    g = grey_of(rgb)
    for c in range(3):
        rgb[..., c] = np.where(keep, rgb[..., c], g)
    a[..., :3] = rgb.clip(0, 255).astype(np.uint8)


MENDS = {3: mend_3, 5: mend_5, 7: mend_7, 8: mend_8, 9: mend_9}


def atomic():
    """Book 1: white, with gold dust thickest round its title, as her copy (no try: there is nothing but lettering)."""
    img = Image.new("RGBA", (W, H), (247, 245, 239, 255))
    rnd = random.Random(1)
    golds = [(196, 170, 112), (170, 140, 82), (222, 204, 156)]
    for _ in range(420):
        x, y = rnd.randrange(W), int(rnd.triangular(34, 132, 84))
        img.putpixel((x, y), golds[rnd.randrange(3)] + (255,))
    for _ in range(60):
        img.putpixel((rnd.randrange(W), rnd.randrange(H)), golds[rnd.randrange(3)] + (255,))
    return img


# ---- the lettering ----------------------------------------------------------------------------------------------
def glyphs(text, gap):
    """The line's mask at the font's own size, its words `gap` px apart if given, Hebrew turned right to left."""
    if HEBREW.search(text):
        text = text[::-1]
    if gap is None:
        return pixelzone.mask(text)
    words = [pixelzone.mask(w) for w in text.split(" ")]
    words = [m.crop((0, 0, m.getbbox()[2], m.height)) for m in words]
    out = Image.new("L", (sum(m.width for m in words) + gap * (len(words) - 1), words[0].height), 0)
    x = 0
    for m in words:
        out.paste(m, (x, 0))
        x += m.width + gap
    return out


def line(spec):
    """The lettering's picture: whole pixels, enlarged by `scale`, stepped or turned, ringed if asked."""
    scale, step = spec["scale"], spec["step"]
    mask = glyphs(spec["text"], spec["gap"])
    if step:
        # each letter cut at its advance and lifted `step` px (at the final scale) above the one before
        text = spec["text"]
        rise = abs(step) * (len(text) - 1)
        out = Image.new("L", (mask.width * scale, mask.height * scale + rise), 0)
        for i, ch in enumerate(text):
            x0 = int(pixelzone.FONT.getlength(text[:i]))
            x1 = int(pixelzone.FONT.getlength(text[:i + 1]))
            piece = mask.crop((x0, 0, x1, mask.height)).resize(((x1 - x0) * scale, mask.height * scale), Image.NEAREST)
            y = (rise if step < 0 else 0) + step * i
            out.paste(piece, (x0 * scale, y), piece)
        mask = out
    elif spec["tight"]:
        # each letter's ink enlarged, set 1 px after the one before; a space is `gap` (or 4) px
        text = spec["text"]
        pieces, x = [], 0
        for ch in text:
            if ch == " ":
                x += spec["gap"] or 4
                continue
            m = pixelzone.mask(ch)
            bx = m.getbbox()
            m = m.crop((bx[0], 0, bx[2], m.height)).resize(((bx[2] - bx[0]) * scale, m.height * scale), Image.NEAREST)
            pieces.append((x, m))
            x += m.width + 1
        out = Image.new("L", (x, pieces[0][1].height), 0)
        for px, m in pieces:
            out.paste(m, (px, 0), m)
        mask = out
    elif scale != 1:
        mask = mask.resize((mask.width * scale, mask.height * scale), Image.NEAREST)
    box = mask.getbbox()
    mask = mask.crop(box)
    if spec["turn"]:
        mask = mask.rotate(spec["turn"], expand=True)
    pic = Image.new("RGBA", mask.size, spec["colour"] + (255,))
    pic.putalpha(mask)
    if spec["outline"]:
        m = np.array(mask) > 0
        p = np.pad(m, 1)
        ring = np.zeros_like(p)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ring |= np.roll(np.roll(p, dy, 0), dx, 1)
        ring &= ~p
        o = Image.new("RGBA", (p.shape[1], p.shape[0]), (0, 0, 0, 0))
        oa = np.array(o)
        oa[ring] = spec["outline"] + (255,)
        o = Image.fromarray(oa)
        o.alpha_composite(pic, (1, 1))
        return o, 1
    return pic, 0


def cover(n):
    if n == 1:
        img = atomic()
    else:
        a = np.array(Image.open(TRIES / f"{n:02d}-a.png").convert("RGBA"))
        if n in MENDS:
            MENDS[n](a)
        img = Image.fromarray(a)
    assert img.size == (W, H), (n, img.size)
    for spec in COVERS[n]:
        pic, pad = line(spec)
        x, y = spec["x"], spec["y"]
        if spec["turn"]:            # x is the spine line's left, y its bottom
            left, top = x, y - pic.height
        else:
            left = {"l": x, "c": x - pic.width // 2, "r": x - pic.width}[spec["align"]]
            top = y
        img.alpha_composite(pic, (left - pad, top - pad))
    return img


def main():
    args = sys.argv[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    built = []
    for n in sorted(COVERS):
        if n != 1 and not (TRIES / f"{n:02d}-a.png").exists():
            print(f"cover {n}: no picture yet")
            continue
        img = cover(n)
        img.save(OUT / f"cover-{n}.png")
        built.append((n, img))
        if (MINI / f"{n:02d}.png").exists():
            mini = Image.new("RGBA", (18, 24), (0, 0, 0, 0))
            mini.paste((0x2e, 0x22, 0x2f, 255), (1, 1, 17, 23))
            mini.alpha_composite(Image.open(MINI / f"{n:02d}.png").convert("RGBA"), (1, 1))
            mini.save(OUT / f"mini-{n}.png")
    print(f"wrote {len(built)} covers to assets/ship/covers/")
    if "--preview" in args and built:
        out = Path(args[args.index("--preview") + 1])
        s, per = 2, 6
        rows = (len(built) + per - 1) // per
        sheet = Image.new("RGB", (per * (W * s + 8), rows * (H * s + 8)), "white")
        for k, (n, img) in enumerate(built):
            sheet.paste(img.convert("RGB").resize((W * s, H * s), Image.NEAREST),
                        ((k % per) * (W * s + 8), (k // per) * (H * s + 8)))
        sheet.save(out)
        print("preview", out)


if __name__ == "__main__":
    main()
