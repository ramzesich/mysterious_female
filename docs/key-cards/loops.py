from PIL import Image, ImageDraw
from versions import H, NAVY, WHITE, CHIP, CLIP, COL, lying
# Loops above the clip: (x, y) on an 8 px wide card, y counted up from the clip's navy row (0) .
LOOPS = {
    "A small loop": [(3, 1), (4, 1), (2, 2), (5, 2), (1, 3), (6, 3), (1, 4), (6, 4), (2, 5), (3, 5), (4, 5), (5, 5)],
    "B taller loop": [(3, 1), (4, 1), (3, 2), (4, 2), (2, 3), (5, 3), (2, 4), (5, 4), (1, 5), (6, 5), (1, 6), (6, 6), (2, 7), (5, 7), (3, 8), (4, 8)],
    "C strap, loop at its end": [(4, 1), (4, 2), (4, 3), (4, 4), (3, 5), (5, 5), (2, 6), (6, 6), (2, 7), (6, 7), (3, 8), (4, 8), (5, 8)],
}
def upright(c, loop):
    fill = H(COL[c][0])
    up = max(y for _, y in loop)
    top = up + 2
    im = Image.new("RGBA", (8, top + 12)); px = im.load()
    for y in range(12):
        for x in range(8):
            if x in (0, 7) and y in (0, 11): continue
            px[x, top + y] = NAVY if (x in (0, 7) or y in (0, 11)) else fill
    for x in range(1, 7):
        for y in (2, 3): px[x, top + y] = WHITE
    px[5, top + 5] = CHIP
    px[3, top - 1] = CLIP; px[4, top - 1] = CLIP
    px[3, top - 2] = NAVY; px[4, top - 2] = NAVY
    for x, y in loop: px[x, top - 2 - y] = NAVY
    return im
if __name__ == "__main__":
    K = 6
    S = Image.new("RGBA", (1100, 3 * 170 + 20), (88, 96, 112, 255)); d = ImageDraw.Draw(S)
    for r, (name, loop) in enumerate(LOOPS.items()):
        y0 = 10 + r * 170
        d.text((10, y0), name, fill=(255, 255, 255))
        for i, c in enumerate(COL):
            im = upright(c, loop); im.save(f"loop-{name[0]}-{c}.png")
            big = im.resize((im.width * K, im.height * K), Image.NEAREST)
            S.alpha_composite(big, (20 + i * 70, y0 + 160 - big.height))
            S.alpha_composite(im, (320 + i * 14, y0 + 160 - im.height))
        lo = lying("off", whole=True, lanyard="navy")
        big = lo.resize((lo.width * K, lo.height * K), Image.NEAREST)
        S.alpha_composite(big, (420, y0 + 160 - big.height)); S.alpha_composite(lo, (580, y0 + 160 - lo.height))
    S.save("loops-x6.png")
