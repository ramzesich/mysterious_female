"""9b composed over the promenade as the game would play it, behind its railing as the game draws them (2026-11-19), for the user's review: the jogger runs at
her standing (his run, flipped, 105 px/s, 12 frames a second), meets her 16 px from her middle; her clip (`b/clean/`,
14 a second) from her standing frame; he stops where he met her and his sorry (`sorry/clean-<which>/`, flipped, 10 a
second) while she sits; `python compose9b.py w23|w7`. Background: a screenshot of the promenade with both hidden (`prom-bg.png`, its view)."""
import json, os, sys
from PIL import Image, ImageOps
H = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, H + "..")
from starts2 import herf, R
T = os.environ["TEMP"] + "/bb/jog/"
BG = Image.open(T + "prom-bg.png").convert("RGBA"); meta = json.load(open(T + "prom-bg.json"))
VX, VY = meta["view"][0], meta["view"][1]
HX, FY = meta["her"][0] - VX, meta["her"][1] - VY          # her middle, the floor (screen px)
PM = json.load(open(R + "assets/sprites/people.json")); PS = Image.open(R + "assets/sprites/people.png").convert("RGBA")
PC, PCOLS = PM["cell"], PM["cols"]; J = PM["people"]["jogger"]
def cell(i): return PS.crop(((i % PCOLS) * PC, (i // PCOLS) * PC, (i % PCOLS) * PC + PC, (i // PCOLS) * PC + PC))
RUN = [ImageOps.mirror(cell(i)) for i in J["anims"]["run"]]
HER = [Image.open(H + f"b/clean/{i}.png").convert("RGBA") for i in range(13)]
WHICH = sys.argv[1] if len(sys.argv) > 1 else "w23"
SORRY = [ImageOps.mirror(Image.open(H + f"sorry/clean-{WHICH}/{i}.png").convert("RGBA")) for i in range(9)]
# sc23: frames 2 and 3 (his fist swung forward, "a punch") left out; then 6-7-8-7 back and forth, a scratch.
ORDER = [0, 1, 4, 5, 6, 7, 8] if WHICH == "sc23" else list(range(9))
LOOP = [6, 7, 8, 7] if WHICH == "sc23" else [8]
MS, MEET = 70, 16
frames = []
# What the game draws in front of their layer (the promenade's railing): a magenta box at her depth, shot in the
# game (`prom-mask.png`); inside it, whatever is not magenta is in front of them.
MK = Image.open(T + "prom-mask.png").convert("RGB")
FRONT = Image.new("L", BG.size, 0)
mk, fr_ = MK.load(), FRONT.load()
for yy in range(int(FY - 104), int(FY + 4)):
    for xx in range(int(HX - 149), int(HX + 149)):
        r_, g_, b_ = mk[xx, yy]
        if not (r_ > 230 and g_ < 30 and b_ > 230): fr_[xx, yy] = 255
def scene(): return BG.copy()
def front(sc): sc.paste(BG, (0, 0), FRONT); return sc
# A: he runs in from the east.
x = HX + MEET + 84.0
t = 0
while x > HX + MEET:
    sc = scene()
    sc.alpha_composite(herf("stand"), (int(HX - 42), int(FY + 1 - 84)))
    sc.alpha_composite(RUN[int(t / 83.3) % 8], (int(round(x)) - 40, int(FY + 1 - PC)))
    frames.append(front(sc)); x -= 105 * MS / 1000; t += MS
# B: her clip, his sorry from the same moment, he where he met her.
jx = HX + MEET
for k in range(40):
    sc = scene()
    n = int(k * MS / 100)
    s = SORRY[ORDER[n] if n < len(ORDER) else LOOP[(n - len(ORDER)) // 2 % len(LOOP)]]
    sc.alpha_composite(s, (int(jx - (127 - 44)), int(FY - 120)))
    h = HER[min(1 + int(k * MS / 71.4), 12)]
    sc.alpha_composite(h, (int(HX - 84), int(FY - 120)))
    frames.append(front(sc))
crop = (int(HX - 110), int(FY - 85), int(HX + 130), int(FY + 10))
big = [f.crop(crop).resize(((crop[2] - crop[0]) * 3, (crop[3] - crop[1]) * 3), Image.NEAREST).convert("RGB") for f in frames]
big[0].save(T + f"g-9b-{WHICH}-close.gif", save_all=True, append_images=big[1:], duration=MS, loop=0)
full = [f.convert("RGB") for f in frames]
full[0].save(T + f"g-9b-{WHICH}.gif", save_all=True, append_images=full[1:], duration=MS, loop=0)
pick = list(range(0, len(frames), max(1, len(frames) // 15)))[:15]
S = Image.new("RGB", (240 * 5 + 8, 95 * 3 + 4), (30, 30, 36))
for j, q in enumerate(pick): S.paste(frames[q].crop(crop).convert("RGB"), ((j % 5) * 242, (j // 5) * 97))
S.resize((S.width * 2, S.height * 2), Image.NEAREST).save(T + f"strip-9b-{WHICH}.png")
print(len(frames), "frames")
