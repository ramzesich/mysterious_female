"""Bumbot's clips as the game builds them: raw/<try>/ to clips/<clip>/ (python assets/source/bumbot/remake/cut.py).

Each clip is the frames the user was shown (README.md), cleaned by rule: loose specks under 12 px off; the shake's
loose drops in water colours (the user: "black droplets, maybe those should be light grey/blue"); the rope taken out
of the rope clip (the game draws its own, behind him); the fishing clip's cat cut from its green set by colour; the
lie-down set on the floor. Every frame keeps its 64 x 64 canvas, the floor under row 55.
"""
from pathlib import Path
import shutil

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
r = lambda a, b: list(range(a, b + 1))
CLIPS = {
    "idle": ("idle-a", r(0, 15)), "walk": ("walk-a", r(1, 16)), "run": ("run-c", r(2, 9)), "jump": ("jump-a", r(0, 16)),
    "look-back": ("lookback-a", r(0, 12)), "turn": ("turn-a", r(0, 12)), "stretch": ("stretch-a", r(0, 16)),
    "shake": ("shake-a", r(0, 12)), "eat": ("eat-a", r(0, 16)), "crawl": ("crawl-a", r(0, 16)), "rope": ("rope-a", r(0, 12)),
    "sit": ("sit-b", r(0, 8)), "sat": ("sitidle-a", r(0, 15)), "stand-up": ("standup-a", r(0, 8)),
    "wash": ("wash-a", r(0, 16)), "bat": ("bat-a", r(0, 12)), "fish": ("fish-green", r(0, 15)),
    "loaf": ("loaf-a", r(0, 6)), "loaf-rest": ("loafidle-a", r(0, 11)), "loaf-up": ("loafup-a", r(0, 8)),
    "lie-down": ("liedown-a", r(0, 16)), "asleep": ("asleep-a", r(0, 15)), "wake": ("wake-a", r(0, 12)),
}
WATER, WATER_SMALL = (0x8f, 0xd3, 0xff, 255), (0xc7, 0xdc, 0xd0, 255)
FLOOR = 56          # the first row under his feet


def parts(a):
    n, lab, st, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    return n, lab, st, 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))


def from_green(a):
    """The cat alone out of the fishing clip's set (green ground, tan floor, blue water): dark and near neutral, his eye."""
    c = a.astype(int); red, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = np.maximum(np.maximum(red, g), b), np.minimum(np.minimum(red, g), b)
    eye = (red > 215) & (g > 215) & (b < 185); eye[50:] = False
    a = a.copy(); a[~((mx < 110) & (mx - mn < 45))] = 0
    n, lab, st, big = parts(a); keep = lab == big
    keep |= eye & (cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    out = np.array(c, dtype=np.uint8); out[~keep] = 0; out[keep, 3] = 255
    return out


def no_rope(a):
    c = a.astype(int); red, g, b = c[..., 0], c[..., 1], c[..., 2]
    a = a.copy(); a[((red - b > 60) | ((red > 150) & (red - b > 35))) & (g < 190)] = 0       # (not his yellow eyes)
    return a


def clean(a, clip):
    if clip == "fish":
        a = from_green(a)
    if clip == "rope":
        a = no_rope(a)
    n, lab, st, big = parts(a)
    for i in range(1, n):
        if i == big:
            continue
        if clip == "shake":
            a[lab == i] = WATER if st[i, cv2.CC_STAT_AREA] > 1 else WATER_SMALL
        elif st[i, cv2.CC_STAT_AREA] < 12 or clip in ("rope", "fish"):
            a[lab == i] = 0
    if clip == "lie-down":
        ys = np.nonzero(a[..., 3])[0]
        if ys.max() >= FLOOR:
            a = np.roll(a, FLOOR - 1 - ys.max(), axis=0)
    return a


if __name__ == "__main__":
    out = HERE / "clips"
    shutil.rmtree(out, ignore_errors=True)
    for clip, (src, frames) in CLIPS.items():
        (out / clip).mkdir(parents=True)
        for k, i in enumerate(frames):
            a = np.array(Image.open(HERE / "raw" / src / f"{i}.png").convert("RGBA"))
            Image.fromarray(clean(a, clip), "RGBA").save(out / clip / f"{k}.png")
    print(f"{len(CLIPS)} clips into {out}")
