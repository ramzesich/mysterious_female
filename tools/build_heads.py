"""Where the head is in every frame of every picture a popup can speak from (the user, 2026-11-20: "The
tip should always come from the relevant person's head ... The placement of the tails must work in all
of the cases in the game"), to `assets/sprites/heads.json`, read by `src/popup.js`:
{ sheet: { frame: [x, y, top] } }, in the frame's own px: the head's middle, and the top of what is on
it (her hair, a hat, a turban), where a tail stops short.

- **Her, in every picture of her** (her sheet, the towel turban's, with Bumbot, her mishaps, the gags,
  the towels'): PixelLab's skeleton estimate of each frame (`tools/estimate_skeleton.py`, 0.1 generations
  a frame), the middle of her eyes and ears, so she is found lying, tumbling, crawling or upside down.
  The estimates are kept in `assets/source/popups/heads/estimates.json` (`--from DIR` adds the
  `<sheet>/<frame>.png.kp.json` files of a run to it), never estimated twice.
- **Bumbot in her arms** (`her-cat-bumbot`, his "Meow!"): his ears' top by rule (the first dark row right
  of her face), the front and the back view by hand (`BUMBOT_BY_HAND`).
- **The people**: always upright (standing or seated), so the head is the figure's top rows; but
  those with a wish (a popup over them) are estimated like her, every frame of theirs: the steward
  tugging his trolley stands lower than its top.

    python tools/build_heads.py [--from DIR]
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SPRITES = ROOT / "assets" / "sprites"
ESTIMATES = ROOT / "assets" / "source" / "popups" / "heads" / "estimates.json"
HER = {"her": 84, "her-towel": 84, "her-cat": 84, "her-mishaps": 112, "gags": 128, "towels": 128}
HEAD_POINTS = ("LEFT EYE", "RIGHT EYE", "LEFT EAR", "RIGHT EAR")
BUMBOT_BY_HAND = {15: (46.5, 43, 39), 16: (53, 44, 40)}       # facing us, and from behind
# Frames whose estimate is off, set by hand (checked on contact sheets): her hold on the funnel
# stairway's rail in a gust (`cling-up`), her head bowed under her blown hair, the estimate swinging
# 7 px frame to frame (a tail would flicker): held where frames 247 and 248 have it.
BY_HAND = {"her": {249: (48.8, 46.9, 37), 250: (48.8, 46.9, 37), 251: (48.8, 46.9, 37), 252: (48.8, 46.9, 37)}}


def cells(sheet, cell):
    a = np.array(Image.open(SPRITES / f"{sheet}.png").convert("RGBA"))
    cols = a.shape[1] // cell
    for i in range(cols * (a.shape[0] // cell)):
        x, y = (i % cols) * cell, (i // cols) * cell
        f = a[y:y + cell, x:x + cell]
        if f[:, :, 3].any():
            yield i, f


def top_over(f, hx, hy):
    """The top of what is on the head: up from its middle while a band 7 px wide has something in it
    (a row's gap allowed), at most 16 px; past that it is something else over her (a door), not her."""
    a = f[:, :, 3] > 0
    x0, x1 = max(0, int(hx) - 3), min(a.shape[1], int(hx) + 4)
    r, top, gap = int(hy), int(hy), 0
    while r > 0 and hy - r <= 16:
        r -= 1
        if a[r, x0:x1].any():
            top, gap = r, 0
        else:
            gap += 1
            if gap > 1:
                break
    return top if hy - top <= 16 else int(hy) - 9


def from_estimate(kp, f, cell):
    pts = [(x * cell, y * cell) for label, x, y in kp if label in HEAD_POINTS] or \
          [(x * cell, y * cell) for label, x, y in kp if label == "NOSE"]
    if not pts:
        return None
    hx = sum(p[0] for p in pts) / len(pts)
    hy = sum(p[1] for p in pts) / len(pts)
    return [round(hx, 1), round(hy, 1), top_over(f, hx, hy)]


def upright(f, dx=0.0, dy=0.0):
    """An upright figure's head: its top rows' middle, 9 px down (`dx`, `dy`: her own offset)."""
    a = f[:, :, 3] > 0
    top = int(np.nonzero(a.any(axis=1))[0].min())
    ys, xs = np.nonzero(a[top:top + 14])
    return [round(float(xs.mean()) + dx, 1), round(top + 9 + dy, 1), top]


# Her upright frames (standing to her full height, 54 px or more: standing, running, in the air) by
# the upright rule, moved by its mean difference from the estimates of 123 such frames (her hair falls
# behind her head): within 2 px of them. Estimated only where she is lower (crawling, swimming,
# sitting, lying) and in every gag.
HER_UPRIGHT = {"her", "her-towel", "her-cat"}
HER_RULE = (1.7, 1.2)


HAIR_SKIN = {(0x2e, 0x22, 0x2f), (0x45, 0x29, 0x3f), (0xfd, 0xcb, 0xb0), (0xfc, 0xa7, 0x90), (0xf6, 0x81, 0x81)}


def on_her(f, h):
    """Her hair or skin within 4 px of the head's middle: a frame of the door alone (the start of 13a,
    the "Do Not Disturb" doors) had its estimate on the door's number plate."""
    x, y = int(h[0]), int(h[1])
    box = f[max(0, y - 4):y + 5, max(0, x - 4):x + 5].reshape(-1, 4)
    return any(p[3] and tuple(int(v) for v in p[:3]) in HAIR_SKIN for p in box)


def her_heads(estimates):
    out = {}
    for sheet, cell in HER.items():
        table = {}
        for i, f in cells(sheet, cell):
            kp = estimates.get(sheet, {}).get(str(i))
            h = kp and from_estimate(kp, f, cell)
            if h and not on_her(f, h):
                h = None
            if i in BY_HAND.get(sheet, {}):
                h = list(BY_HAND[sheet][i])
            if not h and sheet in HER_UPRIGHT:
                ys = np.nonzero((f[:, :, 3] > 0).any(axis=1))[0]
                if ys.max() - ys.min() + 1 >= 54:
                    h = upright(f, *HER_RULE)
            if h:
                table[str(i)] = h
        out[sheet] = table
    return out


def bumbot_heads():
    dark = lambda p: p[3] > 0 and p[0] < 80 and p[1] < 80 and p[2] < 90
    out = {}
    for i, f in cells("her-cat", 84):
        if i in BUMBOT_BY_HAND:
            out[str(i)] = list(BUMBOT_BY_HAND[i])
            continue
        top = next(r for r in range(36, 56) if sum(dark(f[r, x]) for x in range(51, 61)) >= 2)
        pts = [x for r in range(top, top + 8) for x in range(49, 60) if dark(f[r, x])]
        out[str(i)] = [round(sum(pts) / len(pts), 1), top + 4, top]
    return out


def people_heads(estimates):
    out = {}
    for i, f in cells("people", 80):
        kp = estimates.get("people", {}).get(str(i))
        h = kp and from_estimate(kp, f, 80)
        if h:
            out[str(i)] = h
            continue
        a = f[:, :, 3] > 0
        rows = np.nonzero(a.any(axis=1))[0]
        top = int(rows.min())
        ys, xs = np.nonzero(a[top:top + 12])
        out[str(i)] = [round(float(xs.mean()), 1), top + 9, top]
    return out


def merge_runs(estimates, folder):
    folder = Path(folder)
    for sheet in list(HER) + ["people"]:
        for kp in (folder / sheet).glob("*.png.kp.json") if (folder / sheet).exists() else []:
            i = kp.name.split(".")[0]
            pts = json.load(open(kp))
            estimates.setdefault(sheet, {})[i] = [[p["label"], round(p["x"], 4), round(p["y"], 4)]
                                                  for p in pts if p["label"] in HEAD_POINTS + ("NOSE",)]
    return estimates


def main():
    estimates = json.load(open(ESTIMATES)) if ESTIMATES.exists() else {}
    if "--from" in sys.argv:
        estimates = merge_runs(estimates, sys.argv[sys.argv.index("--from") + 1])
        ESTIMATES.parent.mkdir(parents=True, exist_ok=True)
        json.dump(estimates, open(ESTIMATES, "w"), separators=(",", ":"))
    heads = her_heads(estimates)
    heads["her-cat-bumbot"] = bumbot_heads()
    heads["people"] = people_heads(estimates)
    json.dump(heads, open(SPRITES / "heads.json", "w"), separators=(",", ":"))
    missing = {s: sum(1 for _ in cells(s, c)) - len(heads[s]) for s, c in HER.items()}
    print("heads.json:", {s: len(t) for s, t in heads.items()}, "| her frames without an estimate:", missing)


if __name__ == "__main__":
    main()
