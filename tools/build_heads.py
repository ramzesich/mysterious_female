"""Where the head is in every frame of every picture a popup can speak from (the user, 2026-11-20: "The
tip should always come from the relevant person's head ... The placement of the tails must work in all
of the cases in the game"), to `assets/sprites/heads.json`, read by `src/popup.js`:
{ sheet: { clip: [[x, y, top] or null, ...] } }, frame by frame of each clip, in the frame's own px: the
head's middle, and the top of what is on it (her hair, a hat, a turban), where a tail stops short.
**Kept by clip, not by frame number** (the game maps them onto the sheet's numbers from its own data),
so a clip added to a sheet moves nothing; a clip remade with another count of frames is left out until
this is run again. **Run it after rebuilding any of these sheets**; a new clip of hers that is not
upright needs estimating first (`--missing`, then `--from`).

- **Her, in every picture of her** (her sheet, the towel turban's, with Bumbot, her mishaps, the gags,
  the towels'): PixelLab's skeleton estimate of each frame (`tools/estimate_skeleton.py`, 0.1 generations
  a frame), the middle of her eyes and ears, so she is found lying, tumbling, crawling or upside down;
  her upright frames by rule. The estimates are kept by clip in
  `assets/source/popups/heads/estimates.json`, never estimated twice.
- **Bumbot in her arms** (`her-cat-bumbot`, his "Meow!"): his ears' top by rule (the first dark row right
  of her face), the front and the back view by hand (`BUMBOT_BY_HAND`).
- **The people**: always upright (standing or seated), so the head is the figure's top rows; but
  those with a wish (a popup over them) are estimated like her: the steward tugging his trolley stands
  lower than its top.

    python tools/build_heads.py                  # heads.json from the sheets and the estimates
    python tools/build_heads.py --missing DIR    # her frames that need an estimate, as DIR/<sheet>/<clip>~<n>.png
    python tools/estimate_skeleton.py DIR/*/*.png
    python tools/build_heads.py --from DIR       # their estimates kept, heads.json made
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
BUMBOT_BY_HAND = {("front", 0): (46.5, 43, 39), ("back", 0): (53, 44, 40)}       # facing us, and from behind
# Frames whose estimate is off, set by hand (checked on contact sheets): her hold on the funnel
# stairway's rail in a gust (`cling-up`), her head bowed under her blown hair, the estimate swinging
# 7 px frame to frame (a tail would flicker): held where its frames 3 and 4 have it.
BY_HAND = {"her": {("cling-up", k): (48.8, 46.9, 37) for k in (5, 6, 7, 8)}}
# The people estimated: those with a wish (a popup over them) whose top rows are not their head.
PEOPLE_ESTIMATED = {"steward"}
# Her upright frames (standing to her full height, 54 px or more: standing, running, in the air) by
# the upright rule, moved by its mean difference from the estimates of 123 such frames (her hair falls
# behind her head): within 2 px of them. Estimated only where she is lower (crawling, swimming,
# sitting, lying) and in every gag.
HER_UPRIGHT = {"her", "her-towel", "her-cat"}
HER_RULE = (1.7, 1.2)
HAIR_SKIN = {(0x2e, 0x22, 0x2f), (0x45, 0x29, 0x3f), (0xfd, 0xcb, 0xb0), (0xfc, 0xa7, 0x90), (0xf6, 0x81, 0x81)}


def sheet_frames(sheet, cell):
    """{clip: [frame picture, ...]} of a sheet, from its own data (people: `who.clip`)."""
    a = np.array(Image.open(SPRITES / f"{sheet}.png").convert("RGBA"))
    d = json.load(open(SPRITES / f"{sheet}.json"))
    cols = a.shape[1] // cell
    if sheet == "people":
        clips = {f"{w}.{c}": v for w, m in d["people"].items() for c, v in m["anims"].items() if isinstance(v, list)}
        # (Their still poses, single frames outside the clips: `who.@stand`, `@front`, `@back`.)
        clips.update({f"{w}.@{k}": [m[k]] for w, m in d["people"].items() for k in ("stand", "front", "back") if isinstance(m.get(k), int)})
    else:
        clips = {c: v for c, v in d.get("anims", {}).items() if isinstance(v, list)}
    pic = lambda i: a[(i // cols) * cell:(i // cols) * cell + cell, (i % cols) * cell:(i % cols) * cell + cell]
    return {c: [pic(i) for i in fr] for c, fr in clips.items()}


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


def tall(f):
    ys = np.nonzero((f[:, :, 3] > 0).any(axis=1))[0]
    return len(ys) and ys.max() - ys.min() + 1 >= 54


def on_her(f, h):
    """Her hair or skin within 4 px of the head's middle: a frame of the door alone (the start of 13a,
    the "Do Not Disturb" doors) had its estimate on the door's number plate."""
    x, y = int(h[0]), int(h[1])
    box = f[max(0, y - 4):y + 5, max(0, x - 4):x + 5].reshape(-1, 4)
    return any(p[3] and tuple(int(v) for v in p[:3]) in HAIR_SKIN for p in box)


def her_head(sheet, clip, k, f, estimates, cell):
    if (clip, k) in BY_HAND.get(sheet, {}):
        return list(BY_HAND[sheet][(clip, k)])
    if not f[:, :, 3].any():
        return None
    kp = estimates.get(sheet, {}).get(clip, {}).get(str(k))
    h = kp and from_estimate(kp, f, cell)
    if h and not on_her(f, h):
        h = None
    if not h and sheet in HER_UPRIGHT and tall(f):
        h = upright(f, *HER_RULE)
    return h


def needs_estimate(sheet, clip, k, f, estimates):
    """A frame of hers with her in it, no estimate, and not upright (or in a gag)."""
    if not f[:, :, 3].any() or str(k) in estimates.get(sheet, {}).get(clip, {}):
        return False
    if sheet in HER_UPRIGHT and tall(f):
        return False
    rgb = f[:, :, :3][f[:, :, 3] > 0]
    return sum(((rgb == s).all(axis=1)).sum() for s in [(0xfd, 0xcb, 0xb0), (0xfc, 0xa7, 0x90)]) >= 12


def bumbot_heads():
    dark = lambda p: p[3] > 0 and p[0] < 80 and p[1] < 80 and p[2] < 90
    out = {}
    for clip, frames in sheet_frames("her-cat", 84).items():
        row = []
        for k, f in enumerate(frames):
            if (clip, k) in BUMBOT_BY_HAND:
                row.append(list(BUMBOT_BY_HAND[(clip, k)]))
                continue
            top = next((r for r in range(36, 56) if sum(dark(f[r, x]) for x in range(51, 61)) >= 2), None)
            if top is None:
                row.append(None)
                continue
            pts = [x for r in range(top, top + 8) for x in range(49, 60) if dark(f[r, x])]
            row.append([round(sum(pts) / len(pts), 1), top + 4, top])
        out[clip] = row
    return out


def people_heads(estimates):
    out = {}
    for clip, frames in sheet_frames("people", 80).items():
        row = []
        for k, f in enumerate(frames):
            kp = estimates.get("people", {}).get(clip, {}).get(str(k))
            h = kp and from_estimate(kp, f, 80)
            row.append(h or (upright(f) if f[:, :, 3].any() else None))
        out[clip] = row
    return out


def merge_runs(estimates, folder):
    folder = Path(folder)
    for sheet in list(HER) + ["people"]:
        for kp in (folder / sheet).glob("*~*.png.kp.json") if (folder / sheet).exists() else []:
            clip, k = kp.name.split(".png")[0].split("~")
            pts = json.load(open(kp))
            estimates.setdefault(sheet, {}).setdefault(clip, {})[k] = [[p["label"], round(p["x"], 4), round(p["y"], 4)]
                                                                       for p in pts if p["label"] in HEAD_POINTS + ("NOSE",)]
    return estimates


def main():
    estimates = json.load(open(ESTIMATES)) if ESTIMATES.exists() else {}
    if "--missing" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--missing") + 1])
        n = 0
        for sheet, cell in HER.items():
            for clip, frames in sheet_frames(sheet, cell).items():
                for k, f in enumerate(frames):
                    if needs_estimate(sheet, clip, k, f, estimates):
                        (out / sheet).mkdir(parents=True, exist_ok=True)
                        Image.fromarray(f).save(out / sheet / f"{clip}~{k}.png")
                        n += 1
        for clip, frames in sheet_frames("people", 80).items():
            if clip.split(".")[0] in PEOPLE_ESTIMATED:
                for k, f in enumerate(frames):
                    if str(k) not in estimates.get("people", {}).get(clip, {}):
                        (out / "people").mkdir(parents=True, exist_ok=True)
                        Image.fromarray(f).save(out / "people" / f"{clip}~{k}.png")
                        n += 1
        print(n, "frames to estimate in", out)
        return
    if "--from" in sys.argv:
        estimates = merge_runs(estimates, sys.argv[sys.argv.index("--from") + 1])
        ESTIMATES.parent.mkdir(parents=True, exist_ok=True)
        json.dump(estimates, open(ESTIMATES, "w"), separators=(",", ":"))
    heads = {}
    for sheet, cell in HER.items():
        heads[sheet] = {clip: [her_head(sheet, clip, k, f, estimates, cell) for k, f in enumerate(frames)]
                        for clip, frames in sheet_frames(sheet, cell).items()}
    heads["her-cat-bumbot"] = bumbot_heads()
    heads["people"] = people_heads(estimates)
    json.dump(heads, open(SPRITES / "heads.json", "w"), separators=(",", ":"))
    count = {s: sum(1 for row in t.values() for h in row if h) for s, t in heads.items()}
    print("heads.json, frames with a head:", count)


if __name__ == "__main__":
    main()
