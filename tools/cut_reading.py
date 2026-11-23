"""Cuts her out of a reading clip made on the game's own picture (`assets/source/her/reading/raw-<name>/`, the PixMiniMax
frames, 0 the start), by what differs from that picture without her, into `assets/source/her/reading/<name>/` for
`tools/build_reading.py`. Written for the bed's towel clip (the user, 2026-11-23: the towel went from her hair when she
sat to read on the bed); the first clips were cut the same way by hand (their README).

    python tools/cut_reading.py bed-towel

What differs: a channel more than `DIFF` off the room's picture. Left out: where she never is (`SKIP`: the window, which
the generator lit from the night's dark), then all but the largest piece (stray specks), then the holes her outline
encloses filled. Over the wall picture (`PICTURE`) the generator redrew its wisps round her head: there only pixels far
from the picture's own greys (`WISP`) and joined to her below the picture's top count.
"""

import sys
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "her" / "reading"
DIFF = 24
WISPS = False
CLOSE = 2
TUFTS = 44
# name: (the room's picture, its crop, frames, boxes she is never in, the wall picture's box)
CLIPS = {
    "bed-towel": (ROOT / "assets" / "ship" / "cabin-8206.png", (108, 28, 240, 128), range(0, 17),
                  [(30, 0, 74, 62)], (86, 0, 124, 50)),
}


def comps(mask, w, h):
    seen, out = set(), []
    for start in mask:
        if start in seen:
            continue
        q, part = deque([start]), []
        seen.add(start)
        while q:
            x, y = q.popleft()
            part.append((x, y))
            # (Corners count: an outline running diagonally is a staircase of px touching at their corners only.)
            for nx, ny in ((x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy):
                if (nx, ny) in mask and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny))
        out.append(part)
    return out


def fill_holes(keep, w, h):
    outside, q = set(), deque()
    for x in range(w):
        for y in (0, h - 1):
            if (x, y) not in keep:
                q.append((x, y)); outside.add((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if (x, y) not in keep and (x, y) not in outside:
                q.append((x, y)); outside.add((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in keep and (nx, ny) not in outside:
                outside.add((nx, ny)); q.append((nx, ny))
    return {(x, y) for x in range(w) for y in range(h) if (x, y) not in outside}



def grey_top(im, rows):
    """The light blues of the figure's top `rows` (her towel turban) turned to neutral grey of the same lightness: the
    palette's sky blue in its shading read as "water?" (the user, 2026-11-23: "remove the added blue pixels from all the
    with turban on frames"). Dark blues (her eyes) stay."""
    im = im.copy()
    bb = im.getbbox()
    if not bb:
        return im
    for y in range(bb[1], min(bb[3], bb[1] + rows)):
        for x in range(bb[0], bb[2]):
            r, g, b, a = im.getpixel((x, y))
            if a and b - r > 25 and b >= g and (r + g + b) / 3 > 130:
                v = round(0.3 * r + 0.59 * g + 0.11 * b)
                im.putpixel((x, y), (v, v, v, a))
    return im

def cut(name):
    room_path, crop, frames, skip, pic = CLIPS[name]
    room = Image.open(room_path).convert("RGBA").crop(crop)
    w, h = room.size
    greys = {room.getpixel((x, y))[:3] for x in range(pic[0], pic[2]) for y in range(pic[1], pic[3])}

    def wisp(c):
        return min(sum(abs(a - b) for a, b in zip(c, g)) for g in greys) < 60 and max(c) - min(c) < 40

    out = SRC / name
    out.mkdir(exist_ok=True)
    for i in frames:
        im = Image.open(SRC / f"raw-{name}" / f"{i}.png").convert("RGBA")
        mask = set()
        for y in range(h):
            for x in range(w):
                if any(b[0] <= x < b[2] and b[1] <= y < b[3] for b in skip):
                    continue
                a, b = im.getpixel((x, y)), room.getpixel((x, y))
                if max(abs(a[k] - b[k]) for k in range(3)) <= DIFF:
                    continue
                if WISPS and pic[0] <= x < pic[2] and pic[1] <= y < pic[3] and wisp(a[:3]):
                    continue
                mask.add((x, y))
        parts = sorted(comps(mask, w, h), key=len, reverse=True)
        keep = fill_holes(set(parts[0]), w, h) if parts else set()
        # (Over the wall picture's pale ground the towel's inside matches the picture and is not "what differs", and a
        # few of its outline's px are near the picture's greys: there her outline is closed (grown by `CLOSE`, filled,
        # shrunk back) and what it encloses kept from the frame.)
        grown = {(x + dx, y + dy) for x, y in keep for dx in range(-CLOSE, CLOSE + 1) for dy in range(-CLOSE, CLOSE + 1)
                 if 0 <= x + dx < w and 0 <= y + dy < h}
        filled = fill_holes(grown, w, h)
        shut = {(x, y) for x, y in filled if all((x + dx, y + dy) in filled for dx in range(-CLOSE, CLOSE + 1)
                                                  for dy in range(-CLOSE, CLOSE + 1))}
        keep |= {(x, y) for x, y in shut if pic[0] <= x < pic[2] and pic[1] <= y < pic[3]}
        # (Grey and grey-white px over her head outside her dark outline: the generator's tufts over the towel as she sits
        # down and the wall picture's greys flickering at its front as she reads (the user, 2026-11-23), above `TUFTS`
        # rows (her seated head's foot; the book's pages are under it). Inside is what her outline, as the frame draws it,
        # encloses: its dark px grown by 1, filled and shrunk back, or by 2 where 1 leaves the towel open (a third of its grey-whites
        # outside); her skin is not grey-white.)
        def lum(x, y):
            return sum(im.getpixel((x, y))[:3]) / 3

        def greyish(x, y):
            # (And anywhere, the near-white of the bed's pillow redrawn and lifted against her: a blob behind her skirt
            # as she sits down, the user, 2026-11-23.)
            c = im.getpixel((x, y))[:3]
            return max(c) - min(c) < 45 and (lum(x, y) > 200 or (y < TUFTS and lum(x, y) > 100))

        dark0 = {(x, y) for x, y in keep if lum(x, y) < 100}
        greys_ = [(x, y) for x, y in keep if greyish(x, y)]
        for r in (1, 2):
            dark = {(x + dx, y + dy) for x, y in dark0 for dx in range(-r, r + 1) for dy in range(-r, r + 1) if 0 <= x + dx < w and 0 <= y + dy < h}
            filled_ = fill_holes(dark, w, h)
            # (Shrunk back by as much: the grown ring outside the outline is not inside.)
            inside = dark0 | {(x, y) for x, y in filled_ if all((x + dx, y + dy) in filled_ for dx in range(-r, r + 1) for dy in range(-r, r + 1))}
            out_ = [q for q in greys_ if q not in inside]
            if len(out_) < len(greys_) / 3:
                break
        keep -= set(out_)
        # (And over her head a px touching at most one other of hers: a lone speck or a one-px spur.)
        for x, y in [q for q in keep if q[1] < TUFTS]:
            if sum((x + dx, y + dy) in keep for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy) <= 1:
                keep.discard((x, y))
        fig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for x, y in keep:
            fig.putpixel((x, y), im.getpixel((x, y))[:3] + (255,))
        if name.endswith("-towel"):
            fig = grey_top(fig, 18)
        fig.save(out / f"{i}.png")
    print("cut", len(frames), "frames into", out.relative_to(ROOT))


if __name__ == "__main__":
    for n in sys.argv[1:] or list(CLIPS):
        cut(n)
