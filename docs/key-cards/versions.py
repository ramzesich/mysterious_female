from PIL import Image, ImageDraw
H = lambda s: tuple(bytes.fromhex(s)) + (255,)
NAVY, WHITE, CHIP, CLIP = H("323353"), H("ffffff"), H("b2ba90"), H("9babb2")
COL = {"deck": ("4d9be6", "4d65b4"), "ent": ("e83b3b", "ae2334"), "hk": ("1ebc73", "239063"), "off": ("f9c22b", "f79617")}

def card(c, whole=False, lanyard=None):
    """Upright card 8 x 12, a clip, and a lanyard (None, 'navy' or 'colour') above."""
    fill, dark = H(COL[c][0]), H(COL[c][1])
    top = 13 if lanyard else 2
    im = Image.new("RGBA", (10 if lanyard else 8, top + 12)); px = im.load()
    ox = 1 if lanyard else 0
    body = fill if whole else WHITE
    for y in range(12):
        for x in range(8):
            edge = x in (0, 7) or y in (0, 11)
            corner = (x in (0, 7)) and (y in (0, 11))
            if corner: continue
            px[ox + x, top + y] = NAVY if edge else body
    for x in range(1, 7):
        for y in (2, 3):
            px[ox + x, top + y] = (WHITE if whole else fill)
    px[ox + 5, top + 5] = CHIP
    # The clip over the card's middle.
    px[ox + 3, top - 1] = CLIP; px[ox + 4, top - 1] = CLIP
    px[ox + 3, top - 2] = NAVY; px[ox + 4, top - 2] = NAVY
    if lanyard:
        lc = NAVY if lanyard == "navy" else dark
        prev = None
        for y in range(top - 2):
            k = (top - 3 - y) * 4 // (top - 2)
            px[ox + 3 - k, y] = lc; px[ox + 4 + k, y] = lc
            if prev is not None and prev != k:   # a step: joined side by side, no gap at a corner
                px[ox + 3 - prev, y] = lc; px[ox + 4 + prev, y] = lc
            prev = k
    return im

def lying(c, whole=False, lanyard=None):
    """Lying flat, seen a little from above: 12 x 4, its top (the stripe) to the left; the lanyard in a loop beside."""
    fill, dark = H(COL[c][0]), H(COL[c][1])
    W = 12 + (9 if lanyard else 0)
    im = Image.new("RGBA", (W, 5)); px = im.load()
    body = fill if whole else WHITE
    for x in range(12):
        for y in range(1, 5):
            edge = y in (1, 4) or x in (0, 11)
            if (x in (0, 11)) and y in (1, 4): continue
            px[x, y] = NAVY if edge else body
    for y in (2, 3):
        px[2, y] = WHITE if whole else fill; px[3, y] = WHITE if whole else fill
    px[8, 2] = CHIP
    if lanyard:
        lc = NAVY if lanyard == "navy" else dark
        for x, y in [(0, 1), (-1, 2), (-2, 3), (-3, 4), (-4, 4), (-5, 4), (-6, 3), (-7, 2), (-7, 1), (-6, 0), (-5, 0), (-4, 0), (-3, 1)]:
            pass
        loop = [(12, 4), (13, 4), (14, 4), (15, 3), (16, 2), (17, 1), (18, 1), (19, 2), (19, 3), (18, 4), (17, 4), (16, 4)]
        for x, y in loop: px[x, y] = lc
        px[12, 3] = CLIP
    return im

VERS = [("1 white, stripe, clip only", dict()),
        ("2 white, stripe, navy lanyard", dict(lanyard="navy")),
        ("3 white, stripe, lanyard in its colour", dict(lanyard="colour")),
        ("4 whole card in its colour, clip only", dict(whole=True)),
        ("5 whole card in its colour, navy lanyard", dict(whole=True, lanyard="navy"))]

if __name__ == "__main__":
    K = 6
    rows = []
    for label, kw in VERS:
        ims = [card(c, **kw) for c in COL] + [lying(c, **kw) for c in COL]
        rows.append(ims)
    cw = 30 * K; rh = 30 * K
    S = Image.new("RGBA", (cw * 8 + 20, rh * len(rows) + 10), (88, 96, 112, 255))
    d = ImageDraw.Draw(S)
    for r, ims in enumerate(rows):
        for i, im in enumerate(ims):
            big = im.resize((im.width * K, im.height * K), Image.NEAREST)
            x = 10 + i * cw + (cw - big.width) // 2; y = 5 + r * rh + (rh - big.height) - 8
            S.alpha_composite(big, (x, y))
        d.text((12, 8 + r * rh), VERS[r][0], fill=(255, 255, 255))
    S.save("versions-x6.png"); print(S.size)
    # In the game's spot: the sun deck, lying at (292, 164), each version's 'off' card, x4 crops side by side.
    base = Image.open("g-floor-clean.png").convert("RGBA")
    tiles = []
    for label, kw in VERS:
        g = base.copy(); im = lying("off", **kw)
        g.alpha_composite(im, (292 - 6, 165 - im.height))
        t = g.crop((215, 100, 335, 175)); tiles.append(t.resize((t.width * 4, t.height * 4), Image.NEAREST))
    T = Image.new("RGBA", (tiles[0].width * 3 + 20, tiles[0].height * 2 + 10), (40, 40, 48, 255))
    for i, t in enumerate(tiles):
        T.alpha_composite(t, (5 + (i % 3) * (t.width + 5), 5 + (i // 3) * (t.height + 5)))
    ImageDraw.Draw(T).text((10, 10), "", fill=(255,255,255))
    T.save("versions-floor-x4.png"); print(T.size)
