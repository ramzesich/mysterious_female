"""Near-catch 6's storyboard on its clock: every moment a function of T (ms from the take-over), composed over the game's
own picture of the bridge's forward end at game px, from the pieces as built and the clips as cut.
    python storyboard.py            -> out/story.gif (70 ms a frame), out/story-strip.png"""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw
REPO = Path(r"C:/Users/ramze/Development/mysterious_female-catch6")
OUT = Path(__file__).resolve().parent.parent / "out"
SRC = REPO / "assets/source/bridge"
BR = json.load(open(REPO / "assets/ship/bridge/bridge.json"))
CL = json.load(open(SRC / "clips/clips.json"))
VX, VY = 1783, 469
D10, CEIL, LADDER = 704, 576, 1864
CONSOLE, STATION, HELM = 1930, 1989, 2030

# --- the clock (ms) -----------------------------------------------------------------------------------------------------
HER = 2050                      # where she is taken (115 px from where he sits)
CAT0, CAT1, CAT2 = 1944, 1989, 1920      # he sits on the console; comes to the station's top; lands back on the console, forward         # he sits on the console; he comes to the station's top
ON_CONSOLE, ON_STATION = 38, 37 # his paws, px over the floor
OFF0, OFF1 = 1903, 1945         # the officer frozen mid-creep; where he swings from
T = dict(
    crouch=150, call=950, callEnd=2350,           # she goes down on her heels; her call's popup
    look=1000, up=1300, walk=1700, hop=1900, there=2300,   # he looks up, stands, walks aft, hops onto the station
    creep=1850, swing=2770,                       # the officer hurries after him on tiptoe (8 frames, 42 px); swings
    spring=2790, clang=2913,                      # he springs; the hoop on the button
    alarm=2913, start=2940,                       # the button down, the beacon, the whoop; she starts up
    onHead=3380, lid=3450, ladder=3700, down=4300,    # he comes down on the console behind the officer; the lid drops; the ladder lets down
    off=4350, climb=4350,                         # the climb: his run along the console, onto the ladder, up it
    tug=4450, fall=5550, sat=6130,                # the officer tugs upright; falls; sits netted
    lookUp=5000, free=6300,
)
CREEP_FPS, SWING_FPS, TUG_FPS, FALL_FPS, CLIMB_FPS, WALK_PX = 8.7, 14, 10, 12, 14, 30


def load(path):
    return Image.open(path).convert("RGBA")


def sheet(name):
    m = json.load(open(REPO / f"assets/sprites/{name}.json")); im = load(REPO / f"assets/sprites/{name}.png")
    return m, im


HERM, HERS = sheet("her"); CATM, CATS = sheet("bumbot")
SHIP = json.load(open(REPO / "assets/ship/ship.json"))["frames"]; ATLAS = load(REPO / "assets/ship/ship.png")


def cell(m, im, n):
    c = m["cell"]; cols = m["cols"]
    return im.crop(((n % cols) * c, (n // cols) * c, (n % cols) * c + c, (n // cols) * c + c))


def piece(name):
    f = SHIP[name].get("frame", SHIP[name])
    return ATLAS.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


def clip(name, i):
    return load(SRC / f"clips/{name}/{i}.png")


PLACE = load(SRC / "rough/place.png")
POP = load(OUT / "popup-en.png"); POP = POP.crop((0, 0, POP.width, 40))


def bg(t):
    im = PLACE.copy()
    def put(p, x, y):
        im.alpha_composite(p, (int(x - VX), int(y - VY)))
    con = piece("bridge-console-w20"); put(con, CONSOLE - con.width // 2, D10 - con.height)
    helm = piece("helm-console-w20"); put(helm, HELM - helm.width // 2, D10 - helm.height)
    st = load(REPO / ("assets/ship/bridge/station-down.png" if t >= T["clang"] else "assets/ship/bridge/station.png")); put(st, STATION + BR["station"]["dx"], D10 + BR["station"]["dy"])
    # the ladder, let down out of the collar
    k = min(1, max(0, (t - T["ladder"]) / (T["down"] - T["ladder"])))
    if k > 0:
        lad = load(REPO / "assets/ship/bridge/ladder.png")
        k = 1 - (1 - k) ** 2 if k < 1 else 1
        shown = round(lad.height * k)
        put(lad.crop((0, lad.height - shown, lad.width, lad.height)), LADDER + BR["ladder"]["dx"], CEIL + BR["ladder"]["top"])
    put(load(REPO / "assets/ship/bridge/collar.png"), LADDER + BR["collar"]["dx"], CEIL + BR["collar"]["dy"])
    lid = load(REPO / "assets/ship/bridge/lid.png"); n = BR["lid"]["frame"]
    f = 0 if t < T["lid"] else min(3, 1 + int((t - T["lid"]) / 70))
    put(lid.crop((f * n, 0, f * n + n, n)), LADDER + BR["lid"]["dx"] - BR["lid"]["hinge"][0], CEIL + BR["lid"]["dy"] - BR["lid"]["hinge"][1])
    return im


def flip(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def her(t):
    """(picture, world x of its left edge, world y of its top): she faces forward (west)."""
    def cellpic(n):
        c = flip(cell(HERM, HERS, n)); return c, HER - 42, D10 - 84 + 1
    def clippic(name, i):
        c = flip(clip(name, i)); return c, HER - (128 - 64), D10 - 98 + 1
    A = HERM["anims"]
    if t < T["crouch"]: return cellpic(A["stand"][0])
    if t < T["call"]: return clippic("her-call", min(8, int((t - T["crouch"]) / 100) + 1))
    if t < T["start"]: return clippic("her-call-loop", int((t - T["call"]) / 125) % 8)
    if t < T["start"] + 640: return clippic("her-call-up", min(8, int((t - T["start"]) / 80) + 1))
    if t < T["lookUp"]: return cellpic(A["stand"][0])
    return cellpic(A["look-up"][min(len(A["look-up"]) - 1, int((t - T["lookUp"]) / 90))])


def officer(t):
    def him(name, i, x):
        c = clip(name, i); return c, x - 64, D10 - 112
    if t < T["creep"]: return him("rival-stalk", int(t / 160) % 8, OFF0)
    if t < T["swing"]:
        f = (t - T["creep"]) / 1000 * CREEP_FPS
        i = min(8, int(f))
        return him("rival-creep", i % 8, OFF0 + min(1, f / 8) * (OFF1 - OFF0))
    def net(i): return clip("rival-net", i), 1880, 592
    if t < T["clang"]: return net(min(3, 1 + int((t - T["swing"]) / 1000 * SWING_FPS)))
    if t < T["tug"]: return net([4, 5, 6, 5][int((t - T["clang"]) / 170) % 4])
    if t < T["fall"]: return net(min(17, 7 + int((t - T["tug"]) / 1000 * TUG_FPS)))
    return net(min(24, 18 + int((t - T["fall"]) / 1000 * FALL_FPS)))


def cat(t):
    """(picture, left, top, in front of the officer?)."""
    A = CATM["anims"]
    def c(n, x, h, west=False, front=False):
        p = cell(CATM, CATS, n)
        return (flip(p) if west else p), x - 32, D10 - h - 64, front
    if t < T["look"]: return c(A["wash"][int(t / 110) % len(A["wash"])], CAT0, ON_CONSOLE)
    if t < T["up"]: return c(A["sat"][int((t - T["look"]) / 150) % len(A["sat"])], CAT0, ON_CONSOLE)
    if t < T["walk"]: return c(A["stand-up"][min(8, int((t - T["up"]) / 50))], CAT0, ON_CONSOLE)
    if t < T["hop"]:
        k = (t - T["walk"]) / (T["hop"] - T["walk"])
        return c(A["walk"][int((t - T["walk"]) / 62) % 16], CAT0 + k * 4, ON_CONSOLE)
    if t < T["there"]:
        k = (t - T["hop"]) / (T["there"] - T["hop"])
        x = CAT0 + 4 + k * (CAT1 - CAT0 - 4); h = ON_CONSOLE + (ON_STATION - ON_CONSOLE) * k + 14 * math.sin(math.pi * k)
        return c(A["leap"][min(16, 4 + int(k * 9))], x, h)
    if t < T["spring"]: return c(A["idle"][int((t - T["there"]) / 120) % 16], CAT1, ON_STATION)
    if t < T["onHead"]:
        k = (t - T["spring"]) / (T["onHead"] - T["spring"])
        # (Up off the station and back over the officer in one long arc, onto the console's top behind him: the user at
        # the preview, of his landing on the officer's cap: "Bumbot's position is in the air between the consoles".)
        x = CAT1 + (CAT2 - CAT1) * k; h = ON_STATION + (ON_CONSOLE - ON_STATION) * k + 52 * math.sin(math.pi * k ** 0.6)
        return c(A["leap"][min(16, 2 + int(k * 12))], x, h, west=k > 0.12, front=True)
    if t < T["climb"]:
        # crouched on the console, his head to the hatch as it opens
        i = A["sat"][0] if t < T["onHead"] + 140 else A["idle"][int((t - T["onHead"]) / 130) % 16]
        return c(i, CAT2, ON_CONSOLE, west=True)
    i = min(16, int((t - T["climb"]) / 1000 * CLIMB_FPS))
    return flip(clip("bumbot-climb", i)), 1960 - 127, 560, False


def frame(t):
    im = bg(t)
    def put(p, x, y):
        im.alpha_composite(p, (int(round(x - VX)), int(round(y - VY))))
    cp, cx, cy, front = cat(t)
    op, ox, oy = officer(t)
    if t >= T["climb"]:
        # into the collar: cut at its mouth
        mouth = CEIL + BR["ladder"]["mouth"]
        cut = int(mouth - cy)
        cp = cp.copy(); cp.paste((0, 0, 0, 0), (0, 0, cp.width, max(0, cut)))
    if not front: put(cp, cx, cy)
    put(op, ox, oy)
    if front: put(cp, cx, cy)
    hp, hx, hy = her(t)
    put(hp, hx, hy)
    # the beacon lit and the red light over the room
    if t >= T["alarm"]:
        k = (math.sin((t - T["alarm"]) / 260) + 1) / 2
        d = ImageDraw.Draw(im, "RGBA")
        lamp = load(REPO / "assets/ship/bridge/beacon.png")
        if k > 0.25 or t < T["clang"] + 300:
            im.alpha_composite(lamp, (STATION + BR["station"]["dx"] + BR["station"]["lamp"][0] - VX, D10 + BR["station"]["dy"] + BR["station"]["lamp"][1] - VY))
            gx, gy = STATION + BR["station"]["dx"] + BR["station"]["lamp"][0] + lamp.width // 2 - VX, D10 + BR["station"]["dy"] + BR["station"]["lamp"][1] + lamp.height // 2 - VY
            glow = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
            gd.ellipse([gx - 9, gy - 9, gx + 9, gy + 9], fill=(255, 96, 80, 46)); gd.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=(255, 140, 110, 70))
            im.alpha_composite(glow)
        if t < T["clang"] + 150:
            # the blow: short rays round the button for two frames
            cx0, cy0 = STATION + BR["station"]["dx"] + BR["station"]["button"][0] - VX, D10 + BR["station"]["dy"] + BR["station"]["button"][1] + 6 - VY
            for ang in (-150, -115, -90, -65, -30):
                a = math.radians(ang); r0, r1 = 9, 15 if t < T["clang"] + 75 else 18
                d.line([cx0 + r0 * math.cos(a), cy0 + r0 * math.sin(a), cx0 + r1 * math.cos(a), cy0 + r1 * math.sin(a)], fill=(251, 255, 134, 255), width=1)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).rectangle([1843 - VX, CEIL - VY, 479, D10 - VY], fill=(232, 59, 59, int(255 * (0.05 + 0.13 * k))))
        im.alpha_composite(ov)
    if T["call"] <= t < T["callEnd"]:
        put(POP, HER - POP.width // 2 - 14, D10 - 40 - POP.height - 4)
    return im.convert("RGB")


if __name__ == "__main__":
    end = T["free"] + 500
    frames = [frame(t) for t in range(-280, end, 70)]
    big = [f.crop((0, 60, 420, 250)).resize((840, 380), Image.NEAREST) for f in frames]
    big[0].save(OUT / "story.gif", save_all=True, append_images=big[1:], duration=70, loop=0, disposal=1, optimize=False)
    marks = [("0.0 s  taken", 60), ("1.2 s  she calls", 1200), ("1.6 s  he gets up", 1600), ("2.2 s  he comes; the officer after him", 2200),
             ("2.6 s  on the station", 2600), ("2.86 s  the swing; he springs", 2860), ("2.95 s  the hoop on the button", 2950), ("3.4 s  back on the console", 3420),
             ("4.0 s  the hatch, the ladder", 4000), ("4.5 s  he runs for it", 4500), ("5.0 s  up the ladder", 5000), ("5.3 s", 5300),
             ("5.6 s  the net comes free", 5650), ("5.9 s", 5900), ("6.2 s  his own net", 6200), ("6.4 s  she is free", 6400)]
    cells = []
    for cap, t in marks:
        c = frame(t).crop((30, 70, 330, 245)).resize((600, 350), Image.NEAREST)
        d = ImageDraw.Draw(c); d.rectangle((0, 0, 600, 14), fill=(20, 20, 28)); d.text((5, 2), cap, fill=(255, 255, 255))
        cells.append(c)
    cols = 4; rows = (len(cells) + cols - 1) // cols
    s = Image.new("RGB", (cols * 604 + 4, rows * 354 + 4), (30, 30, 40))
    for i, c in enumerate(cells): s.paste(c, (4 + (i % cols) * 604, 4 + (i // cols) * 354))
    s.save(OUT / "story-strip.png")
    print(len(frames), "frames", s.size)

    close = [(60, "taken"), (2600, "on the station"), (2860, "the swing; he springs"), (2950, "the hoop on the button: it goes down, the beacon lights"), (3500, "back on the console, behind the officer"), (4950, "to the ladder"), (5250, "up it"), (6350, "the end")]
    cs = []
    for t, cap in close:
        c = frame(t).crop((50, 90, 290, 240)).resize((720, 450), Image.NEAREST)
        d = ImageDraw.Draw(c); d.rectangle((0, 0, 720, 14), fill=(20, 20, 28)); d.text((5, 2), f"{t / 1000:.2f} s  {cap}", fill=(255, 255, 255)); cs.append(c)
    s2 = Image.new("RGB", (2 * 724 + 4, 4 * 454 + 4), (30, 30, 40))
    for i, c in enumerate(cs): s2.paste(c, (4 + (i % 2) * 724, 4 + (i // 2) * 454))
    s2.save(OUT / "story-close.png")
