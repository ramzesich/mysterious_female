"""The linen room (deck 9) and the laundry (deck 4) redecorated (the user, 2026-11-24: "keeping the exact dimensions and
the layout of the current props, so that we wouldn't affect gameplay"; chosen: linen A, laundry C); then, the same day,
the dry store (deck 4, A: worn painted steel), the galley (deck 5, A: a working stainless galley) and the maid's cabin
(deck 6, C: its own look, softly panelled).

Each room's picture as its builder draws it (tools/draw_linen.py, tools/draw_rooms.py's `laundry`) was redrawn in place by
PixelLab (`edit_image_pro_flash`, every shape kept where it is): the redraws are kept in `assets/source/ship/redeco/` (its
README has the jobs and the tries). This lays them over the builder's picture and pastes back, pixel for pixel, what play
and the clips rest on:

- the linen room: its crew door and the chute's hatch (her `chute-in` clip was made on the hatch's own pixels);
- the laundry: its crew door, the chute's outlet and the cart heaped with towels (both generated earlier, laid in by the
  builder), and its floor and slab (the redraw made the floor glossy with reflections: "way out of the rest of the ship's
  theme", the user);
- the dry store and the galley: their crew doors and floors (the store's shelf where the tangerines and the snack tube lie
  came back on its row, the galley's flour sacks, range and pass where they were);
- the maid's cabin: its door ajar, its floor, and boxes round the generated pieces stood in it (the luggage rack and
  suitcase, the sea picture, the towel swan; boxes, not their pixels: the redraw's own copies left traces round them).
  `draw_rooms.py` cuts the swan drawn over her on the bed (`maid6-onbed`) from the redecorated picture.

The laundry is wider than one redraw (256 px): its left half (x 0..192) and right half (from x 148) were redrawn apart, the
right half's colours brought to the left's row by row where they overlap, and the 16 px strip over the join (x 184..200)
inpainted from both sides (`laundry-heal-C.png`, a 256 px window from x 64). The galley (336 px) too: halves from x 0 and
x 148, matched row by row, cut at x 178 between the range and the pass, where the tile rows meet and the cut reads as one
more grout line (an inpaint of the strip came back a flat grey pillar: kept in `tries/`, not used).

The linen room's door propped open, seen from the corridor, shows the room through its opening: draw_linen.py fills it
from the new picture (the linen on the rack beside the door), so the two agree.

Both builders call this (draw_linen.py's main, draw_rooms.py's `laundry`), so a rebuild keeps the new look; run alone it
re-lays the laundry, the store, the galley and the maid's cabin over their current pictures (safe again and again: what it pastes back is the builder's own, which it
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
CREW_DOOR = (59 - 29 // 2 - 1, FLOOR - 74 - 1, 59 + 29 // 2 + 1, FLOOR - 1)      # a crew door at draw_rooms' DOOR_X
GALLEY_DOOR = tuple(v if i % 2 else (336 - 1 - 59) + (v - 59) + 1 for i, v in enumerate(CREW_DOOR))   # mirrored: 336 - 59
MAID6_KEEP = [(59 - 34 // 2 - 1, FLOOR - 74 - 1, 59 + 34 // 2 + 1, FLOOR - 1),  # the door ajar (door-cabin-ajar, 34 x 74)
              (86, 74, 121, FLOOR - 1),          # the luggage rack and the suitcase on it (stood at 104)
              (96, 34, 123, 55),                 # the sea picture (at 110, 74 up)
              (175, 80, 204, 108)]               # the towel swan on the bed (at 190, 21 up)


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


def floor(base):
    return (0, FLOOR, base.width - 1, base.height - 1)


def store(base):
    """The dry store: the redraw, its door and floor the builder's."""
    im = Image.open(SRC / "store-A.png").convert("RGBA")
    assert im.size == base.size, (im.size, base.size)
    paste_boxes(im, base, [CREW_DOOR, floor(base)])
    return im


def galley(base):
    """The galley: its halves joined at x 178, its door (at its aft end, the room mirrored) and floor the builder's."""
    L = np.array(Image.open(SRC / "galley-left-A.png").convert("RGB")).astype(float)
    R = np.array(Image.open(SRC / "galley-right-A.png").convert("RGB")).astype(float)
    over, cut = 148, 178
    diff = (L[:, over:] - R[:, :L.shape[1] - over]).mean(1)
    k9 = np.ones(9) / 9
    off = np.stack([np.convolve(np.pad(diff[:, c], 4, mode="edge"), k9, mode="valid") for c in range(3)], 1)
    R = np.clip(R + off[:, None, :], 0, 255)
    full = np.zeros((base.height, base.width, 4), np.uint8)
    full[:, :, 3] = 255
    full[:, :cut, :3] = L[:, :cut]
    full[:, cut:, :3] = R[:, cut - over:cut - over + base.width - cut]
    im = Image.fromarray(full)
    paste_boxes(im, base, [GALLEY_DOOR, floor(base)])
    return im


def maid6(base):
    """The maid's cabin: the redraw, its door, floor and generated pieces the builder's."""
    im = Image.open(SRC / "maid6-C.png").convert("RGBA")
    assert im.size == base.size, (im.size, base.size)
    paste_boxes(im, base, MAID6_KEEP + [floor(base)])
    return clear_glass(im, "maid6")


def clear_glass(im, room):
    """A room's window panes (`windows` in tools/population.py's ROOMS) cleared: the game shows the live sea and sky behind
    them, as in cabin 8206 (the user, 2026-11-24)."""
    from population import ROOMS
    a = np.array(im)
    for x, y, w, h in next(r for r in ROOMS if r["id"] == room).get("windows", ()):
        a[y:y + h, x:x + w, 3] = 0
    return Image.fromarray(a)


# --- The guest cabins (take 3: their own colours, the finish only), the pantry (B) and the blanket fort (3), 2026-11-24 ---

def join(L, R, cut, over0):
    """Two redrawn parts of one room: R (laid from room x over0) brought to L's colours row by row where they overlap,
    then L up to `cut` and R from it."""
    L = np.array(L.convert("RGBA")); Rf = np.array(R.convert("RGB")).astype(float)
    Lf = L[:, :, :3].astype(float)
    n = L.shape[1] - over0
    diff = (Lf[:, over0:] - Rf[:, :n]).mean(1)
    k9 = np.ones(9) / 9
    off = np.stack([np.convolve(np.pad(diff[:, c], 4, mode="edge"), k9, mode="valid") for c in range(3)], 1)
    Rf = np.clip(Rf + off[:, None, :], 0, 255)
    out = np.zeros((L.shape[0], over0 + Rf.shape[1], 4), np.uint8)
    out[:, :, 3] = 255
    out[:, :cut, :3] = Lf[:, :cut]
    out[:, cut:, :3] = Rf[:, cut - over0:]
    return Image.fromarray(out)


def pieces_mask(size, placed):
    """The pixels of atlas pieces stood in a room as draw_rooms' stand() stands them (its middle at x, its foot dy up)."""
    from draw_rooms import atlas
    m = np.zeros((size[1], size[0]), bool)
    for frame, x, dy in placed:
        a = np.array(atlas(frame))[:, :, 3] > 0
        x0, y0 = x - a.shape[1] // 2, FLOOR - dy - a.shape[0]
        m[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] |= a
    return m


# The balcony door's glass (draw_rooms' balcony_door): its panes cleared for the live sea and sky, but for what stands in
# front of the view, the builder's own pixels: the balcony's rail and balusters, the handle; and the curtain blown in
# through a door slid open. (`windows` on the room in tools/population.py are these panes, for the game's mask.)
RAIL = [(243, 94, 38, 2)] + [(x, 95, 1, 32) for x in range(246, 282, 9)]
BALCONY_SHUT = dict(panes=[(243, 45, 18, 82), (263, 45, 18, 82)], bars=RAIL + [(258, 82, 2, 9)], curtain=None)
BALCONY_AJAR = dict(panes=[(243, 45, 19, 82), (264, 45, 8, 82), (274, 45, 7, 82)], bars=RAIL + [(269, 82, 2, 9)],
                    curtain=[(236, 40), (242, 40), (251, 98), (247, 120), (240, 114)])


def balcony_glass(im, base, door):
    from PIL import ImageDraw
    a, b = np.array(im), np.array(base)
    keep = Image.new("L", im.size, 0)
    if door["curtain"]:
        ImageDraw.Draw(keep).polygon(door["curtain"], fill=255, outline=255)
    k = np.array(keep) > 0
    k |= np.roll(k, 1, 1) | np.roll(k, -1, 1)
    for x, y, w, h in door["panes"]:
        sub = a[y:y + h, x:x + w]
        sub[~k[y:y + h, x:x + w], 3] = 0
    for x, y, w, h in door["bars"]:
        a[y:y + h, x:x + w] = b[y:y + h, x:x + w]
    return Image.fromarray(a)


CABIN_DOOR = (44, 47, 74, 124)          # draw_rooms' cabin_door at DOOR_X, a px round it
# Each cabin: its redrawn parts (file, the room x it is laid from), where each joins the one before, its balcony door,
# the generated pieces stood in it (pasted back by their own pixels), and boxes kept as the builder drew them.
CABINS = {
    "balcabin9": dict(parts=[("balcabin9-l2-T3", 0), ("balcabin9-r2-T3", 112)], cuts=[177], door=BALCONY_SHUT,
                      pieces=[("towel-swan", 220, 32)]),
    "balcabin8m": dict(parts=[("balcabin8m-l", 0), ("balcabin8m-r", 112)], cuts=[180], door=BALCONY_AJAR,
                       pieces=[("towel-trolley", 160, 0)]),
    "balcabin8a": dict(parts=[("balcabin8a-l", 0), ("balcabin8a-r", 112)], cuts=[182], door=BALCONY_AJAR,
                       pieces=[("rose-glass", 152, 26)]),
    "balcabin9a": dict(parts=[("balcabin9a-l", 0), ("balcabin9a-r", 112)], cuts=[177], door=BALCONY_AJAR,
                       pieces=[("bucket-spade", 118, 0), ("orange-juice", 150, 26), ("beach-bag", 222, 32), ("swim-ring", 204, 32)]),
    "balcabin10a": dict(parts=[("balcabin10a-l", 0), ("balcabin10a-r", 112)], cuts=[178], door=BALCONY_AJAR,
                        pieces=[("wine-glasses", 146, 26), ("cake-slice", 164, 26), ("champagne-bucket", 116, 0)]),
    "guest10": dict(parts=[("guest10-l", 0), ("guest10-r", 112)], cuts=[181], door=BALCONY_SHUT, pieces=[("table-lamp", 152, 26)]),
    "cleanup": dict(parts=[("cleanup-w", 0)], cuts=[], door=None, pieces=[("towel-trolley", 132, 0)],
                    boxes=[(21, 119, 39, 127)]),                     # the robot vacuum's dock
    "makeup10": dict(parts=[("makeup10-w", 0)], cuts=[], door=None, pieces=[("towel-trolley", 136, 0)]),
    "adjoin": dict(parts=[("adjoin-p1", 0), ("adjoin-p2", 200), ("adjoin-p3", 244)], cuts=[211, 363], door=None,
                   pieces=[("luggage-rack", 128, 0), ("suitcases", 128, 20)], boxes=[(358, 47, 388, 124)]),   # its 2nd door
}


def cabin(name, base):
    """A guest cabin: its parts joined, its doors, floor and generated pieces the builder's, its balcony's glass clear."""
    spec = CABINS[name]
    (first, _), *rest = spec["parts"]
    im = Image.open(SRC / f"{first}.png")
    for (part, x), cut in zip(rest, spec["cuts"]):
        im = join(im, Image.open(SRC / f"{part}.png"), cut, x)
    im = im.convert("RGBA")
    assert im.size == base.size, (name, im.size, base.size)
    paste_boxes(im, base, [CABIN_DOOR, floor(base)] + spec.get("boxes", []))
    a, b = np.array(im), np.array(base)
    m = pieces_mask(base.size, spec["pieces"])
    a[m] = b[m]
    im = Image.fromarray(a)
    return balcony_glass(im, base, spec["door"]) if spec["door"] else im


def pantry(base):
    """The pantry (B): its left part to x 212, past the shelf's right post, its right from x 100; doors and floor kept."""
    im = join(Image.open(SRC / "pantry-L212-B.png"), Image.open(SRC / "pantry-right-B.png"), 212, 100)
    paste_boxes(im, base, [CREW_DOOR, tuple(v + (236 - 59 if i % 2 == 0 else 0) for i, v in enumerate(CREW_DOOR)), floor(base)])
    return im


def fort():
    """The blanket fort drawn in front of her in the adjoining cabins (3): redrawn in place, its outline as it was."""
    return Image.open(SRC / "fort-3.png").convert("RGBA")


def main():
    for name, lay in [("laundry", laundry), ("store", store), ("galley", galley), ("maid6", maid6), ("pantry", pantry)] +             [(n, (lambda n: lambda base: cabin(n, base))(n)) for n in CABINS]:
        p = GAME / "rooms" / f"{name}.png"
        lay(Image.open(p).convert("RGBA")).save(p)
        print("wrote", p.relative_to(ROOT))
    fort().save(GAME / "rooms" / "adjoin-fort.png")
    print("(the linen room: run tools/draw_linen.py; the maid's cabin's swan over her: tools/draw_rooms.py maid6)")


if __name__ == "__main__":
    main()
