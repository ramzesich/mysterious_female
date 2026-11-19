"""Gag 23's tiptoe as skeletons: her end pose's own (`end-blush.png.kp.json`, estimated) from the hips up in every
frame, and her legs laid out by rule: two tiny steps a cycle of 8 frames, each foot `STEP` px from front to back
while planted, lifted `LIFT` px as it comes forward, the ankles `TOE` px up (on her toes), the pelvis level; knees
forward. Writes `tiptoe.kp.json` (8 skeletons, fractions of the 128 px picture)."""
import json, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
STEP, LIFT, TOE, THIGH, SHIN = 10, 3, 1.5, 11.6, 10.0
base = {k["label"]: k for k in json.load(open(HERE / "end-blush.png.kp.json"))}
P = lambda l: (base[l]["x"] * 128, base[l]["y"] * 128)

def knee(h, a):
    dx, dy = a[0] - h[0], a[1] - h[1]
    d = math.hypot(dx, dy)
    if d > THIGH + SHIN - 0.01:
        k = (THIGH + SHIN - 0.01) / d
        a = (h[0] + dx * k, h[1] + dy * k); dx, dy, d = a[0] - h[0], a[1] - h[1], THIGH + SHIN - 0.01
    t = (THIGH ** 2 - SHIN ** 2 + d ** 2) / (2 * d)
    hgt = math.sqrt(max(0, THIGH ** 2 - t ** 2))
    mx, my = h[0] + dx * t / d, h[1] + dy * t / d
    # (Of the two, the one to the east: knees forward.)
    c1 = (mx - dy * hgt / d, my + dx * hgt / d); c2 = (mx + dy * hgt / d, my - dx * hgt / d)
    return (c1 if c1[0] > c2[0] else c2), a

def foot(hip, phase):
    phase %= 1
    floor = P("RIGHT LEG")[1] - TOE
    if phase < 0.5:
        off = STEP / 2 - STEP * phase / 0.5; lift = 0
    else:
        q = (phase - 0.5) / 0.5
        off = -STEP / 2 + STEP * q; lift = LIFT * math.sin(math.pi * q)
    return (hip[0] + off, floor - lift)

frames = []
for f in range(8):
    kp = {l: list(P(l)) for l in base}
    for side, ph in (("RIGHT", 0.25 + f / 8), ("LEFT", 0.75 + f / 8)):
        h = P(f"{side} HIP")
        k, a = knee(h, foot(h, ph))
        kp[f"{side} KNEE"], kp[f"{side} LEG"] = list(k), list(a)
    frames.append([{"label": l, "x": round(kp[l][0] / 128, 4), "y": round(kp[l][1] / 128, 4), "z_index": base[l]["z_index"]} for l in base])
json.dump(frames, open(HERE / "tiptoe.kp.json", "w"))
for f, fr in enumerate(frames):
    d = {k["label"]: (round(k["x"] * 128, 1), round(k["y"] * 128, 1)) for k in fr}
    print(f, "R knee", d["RIGHT KNEE"], "ankle", d["RIGHT LEG"], "| L knee", d["LEFT KNEE"], "ankle", d["LEFT LEG"])
