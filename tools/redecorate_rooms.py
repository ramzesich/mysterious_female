"""The linen room (deck 9) and the laundry (deck 4) redecorated (the user, 2026-11-24: "keeping the exact dimensions and
the layout of the current props, so that we wouldn't affect gameplay"; chosen: linen A, laundry C).

Each room's picture as its builder draws it (tools/draw_linen.py, tools/draw_rooms.py's `laundry`) was redrawn in place by
PixelLab (`edit_image_pro_flash`, every shape kept where it is): the redraws are kept in `assets/source/ship/redeco/` (its
README has the jobs and the tries). This lays them over the builder's picture and pastes back, pixel for pixel, what play
and the clips rest on:

- the linen room: its crew door and the chute's hatch (her `chute-in` clip was made on the hatch's own pixels);
- the laundry: its crew door, the chute's outlet and the cart heaped with towels (both generated earlier, laid in by the
  builder), and its floor and slab (the redraw made the floor glossy with reflections: "way out of the rest of the ship's
  theme", the user).

The laundry is wider than one redraw (256 px): its left half (x 0..192) and right half (from x 148) were redrawn apart, the
right half's colours brought to the left's row by row where they overlap, and the 16 px strip over the join (x 184..200)
inpainted from both sides (`laundry-heal-C.png`, a 256 px window from x 64).

The linen room's door propped open, seen from the corridor, shows the room through its opening: draw_linen.py fills it
from the new picture (the linen on the rack beside the door), so the two agree.

Both builders call this (draw_linen.py's main, draw_rooms.py's `laundry`), so a rebuild keeps the new look; run alone it
re-lays the laundry over its current picture (safe again and again: what it pastes back is the builder's own, which it
never changes): python tools/redecorate_rooms.py
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source" / "ship" / "redeco"
GAME = ROOT / "assets" / "ship"
FLOOR = 128

LINEN_KEEP = [(180 - 15, FLOOR - 81, 180 + 15, FLOOR - 1),        # the door back out (draw_linen's DOOR_X)
              (129 - 16, FLOOR - 45, 129 + 16, FLOOR - 11)]       # the chute's hatch (CHUTE_X)
LAUNDRY_DOOR = (59 - 29 // 2 - 1, FLOOR - 74 - 1, 59 + 29 // 2 + 1, FLOOR - 1)   # draw_rooms' DOOR_X, the crew door's size
LAUNDRY_CART = 200                                               # tools/population.py's LINEN["laundry_cart"]


def paste_boxes(new, old, boxes):
    for x0, y0, x1, y1 in boxes:
        new.paste(old.crop((x0, y0, x1 + 1, y1 + 1)), (x0, y0))


def linen(base):
    """The linen room: the redraw, its door and hatch the builder's."""
    im = Image.open(SRC / "linen-A.png").convert("RGBA")
    assert im.size == base.size, (im.size, base.size)
    paste_boxes(im, base, LINEN_KEEP)
    return im


def laundry(base):
    """The laundry: the two halves and the healed join, then the door, the outlet, the cart and the floor the builder's."""
    L = np.array(Image.open(SRC / "laundry-left-C.png").convert("RGB")).astype(float)
    R = np.array(Image.open(SRC / "laundry-right-C.png").convert("RGB")).astype(float)
    H = np.array(Image.open(SRC / "laundry-heal-C.png").convert("RGB"))
    diff = (L[:, 148:192] - R[:, 0:44]).mean(1)
    k9 = np.ones(9) / 9
    off = np.stack([np.convolve(np.pad(diff[:, c], 4, mode="edge"), k9, mode="valid") for c in range(3)], 1)
    R = np.clip(R + off[:, None, :], 0, 255)
    full = np.zeros((base.height, base.width, 4), np.uint8)
    full[:, :, 3] = 255
    full[:, :192, :3] = L[:, :192]
    full[:, 192:, :3] = R[:, 44:44 + base.width - 192]
    full[:, 184:200, :3] = H[:, 120:136]
    im = Image.fromarray(full)
    paste_boxes(im, base, [LAUNDRY_DOOR, (0, FLOOR, base.width - 1, base.height - 1)])
    # The outlet's and the cart's own pixels, where the builder laid them.
    chute = json.loads((GAME / "chute" / "chute.json").read_text(encoding="utf-8"))
    src = ROOT / "assets" / "source" / "ship" / "laundry-chute"
    mask = np.zeros((base.height, base.width), bool)
    out = np.array(Image.open(src / "outlet.png").convert("RGBA"))[:, :, 3] > 128
    ox, oy = chute["outlet"]["x"], chute["outlet"]["y"]
    mask[oy:oy + out.shape[0], ox:ox + out.shape[1]] |= out
    cart = np.array(Image.open(src / "cart.png").convert("RGBA"))[:, :, 3] > 128
    cx, cy = LAUNDRY_CART - cart.shape[1] // 2, FLOOR - cart.shape[0]
    mask[cy:cy + cart.shape[0], cx:cx + cart.shape[1]] |= cart
    n, b = np.array(im), np.array(base)
    n[mask] = b[mask]
    return Image.fromarray(n)


def main():
    p = GAME / "rooms" / "laundry.png"
    laundry(Image.open(p).convert("RGBA")).save(p)
    print("wrote", p.relative_to(ROOT), "(the linen room: run tools/draw_linen.py)")


if __name__ == "__main__":
    main()
