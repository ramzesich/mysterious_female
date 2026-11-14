"""Overlaps that make no sense, found by rule in the running game (the user, 2026-11-14: a door and
its plate drawn on a speaker stack had passed every check by eye). Every picture and text the game
has on the decks is read with its real bounds, in two states of the story (the start; late, after
the horn), and these pairs are listed:

    door / furniture    a door with something standing in front of it or behind it
    door / door         two doors in one place
    text / anything     a plate, sign or poster across a door, a piece of furniture, a picture
    text / text         two signs across each other
    wall / furniture    a picture, clock or screen on the wall behind something standing (listed
                        last: a few are meant, a TV over its console)

    python tools/check_overlaps.py            the list, by deck and metres from the bow
    python tools/check_overlaps.py --shots    and a close-up of each (overlap-N.png in
                                              %TEMP%/bumbusik-playtest/), tiled into sheets

Things known to be meant are in ALLOWED below, each with its reason. Run it at the end of every
step (CLAUDE.md, "Looking closely"); an empty list is the aim.
"""

import json
import sys
import time

import playtest as P
from build_ship_map import PLAYABLE, floor_y

# Pairs that are meant: (a frame or text's start, another's), in either order.
ALLOWED = [
    ("rope-barrier", "text:"),              # a block's sign hangs on its rope
    ("pool-hut", "door-crew"),              # the pool attendant's hut: the door is the hut's own
    ("linen-door-open", "door-crew"),       # the linen room's door, shut and open: one place
    # Housekeeping's carts and delivered luggage stand at cabin doors: what they are for.
    ("service-cart", "door-cabin"), ("towel-trolley", "door-cabin"), ("suitcases", "door-cabin"),
    # Deck 11's midship lobby has the 10-11 flight's sign and the 11-12 flight's: the first is gone
    # (region 6) before she can stand there.
    ("text:PLEASE DO NOT TOUCH", "text:WET PAINT"), ("text:PLEASE DO NOT TOUCH", "paint-bucket"),
    ("door-crew", "life-ring"),             # the ring hangs on the promenade's rail, outside the foyer's wall
    ("parasol-bg", "sundae-bg"),            # a sundae on a table under its parasol
]
# Things that move, lie flat on the floor or rest on furniture: no fault where they pass or lie.
SKIP_NAMES = ("robot", "vacuum", "paws", "book-", "icon-", "gull-", "rail-towel", "lift-", "tray", "load-")

# Textures that are not things standing on a deck: her, the people (they walk past doors), the cat,
# pickups and their glints, lamps, the weather.
SKIP_KEYS = {"people", "her", "her-towel", "bumbot", "tangerine", "dot", "glow", "lamp", "puff", "livery", "things-gull"}

DUMP = """(() => { const s = window.__ship, out = [];
  const walk = list => { for (const o of list) {
    if (o.type === 'Container' || o.type === 'Layer') { walk(o.list); continue; }
    if (!o.visible || o.alpha === 0 || !o.getBounds || !['Image', 'Sprite', 'Text'].includes(o.type)) continue;
    const b = o.getBounds();
    out.push({ t: o.type, k: o.texture ? o.texture.key : '', f: String(o.frame ? o.frame.name : ''), text: o.text || '',
               d: o.depth, x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height) });
  } };
  walk(s.worldLayer.list); return JSON.stringify(out); })()"""


def name_of(o):
    if o["t"] == "Text":
        return "text:" + o["text"].replace("\n", " ")[:24]
    return o["f"] if o["k"] in ("shipart", "things") and o["f"] not in ("", "__BASE") else o["k"]


def classify(o):
    """door, text, stand (on a deck's floor), wall (hung at least 20 px up), or None."""
    if o["t"] == "Text":
        return "text" if o["text"].strip() else None
    if o["k"] in SKIP_KEYS or o["w"] > 400 or o["h"] > 150 or o["w"] < 4 or o["h"] < 4:
        return None
    n = name_of(o)
    if n.startswith(SKIP_NAMES):
        return None
    bottom = o["y"] + o["h"]
    decks = [d for d in PLAYABLE if -4 <= floor_y(d) - bottom < 140]
    if not decks:
        return None
    lift = floor_y(decks[0]) - bottom
    if "door" in n and o["h"] > 50:
        return "door"
    if lift <= 2:
        return "stand"
    if lift >= 20:
        return "wall"
    return None


def deck_of(o):
    bottom = o["y"] + o["h"]
    return next((d for d in PLAYABLE if -4 <= floor_y(d) - bottom < 140), 0)


def overlap(a, b):
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return (w, h) if w > 0 and h > 0 else None


def allowed(a, b):
    na, nb = name_of(a), name_of(b)
    return any((na.startswith(p) and nb.startswith(q)) or (na.startswith(q) and nb.startswith(p)) for p, q in ALLOWED)


def audit(objs):
    kinds = [(o, classify(o)) for o in objs]
    kinds = [(o, k) for o, k in kinds if k]
    kinds.sort(key=lambda p: p[0]["x"])
    found = []
    for i, (a, ka) in enumerate(kinds):
        for b, kb in kinds[i + 1:]:
            if b["x"] >= a["x"] + a["w"]:
                break
            # (The ship's side and the outside route are drawn over the decks, at their own depths:
            # a balcony's chair and the cabin door behind its wall are never seen together.)
            if deck_of(a) != deck_of(b) or (8.6 <= a["d"] < 9) != (8.6 <= b["d"] < 9):
                continue
            ov = overlap(a, b)
            if not ov or allowed(a, b):
                continue
            pair = tuple(sorted((ka, kb)))
            rule = {("door", "stand"): "door / furniture", ("door", "door"): "door / door", ("door", "text"): "text / door",
                    ("stand", "text"): "text / furniture", ("text", "wall"): "text / wall", ("text", "text"): "text / text",
                    ("stand", "wall"): "wall / furniture"}.get(pair)
            if not rule:
                continue
            w, h = ov
            # (A sliver is no fault; a door's own number or handle plate lies wholly on it.)
            if w < 3 or h < 3:
                continue
            if "text" in pair and pair != ("text", "text"):
                t, other = (a, b) if ka == "text" else (b, a)
                if other["x"] <= t["x"] and t["x"] + t["w"] <= other["x"] + other["w"] and other["y"] <= t["y"] \
                        and t["y"] + t["h"] <= other["y"] + other["h"]:
                    continue
            if rule == "wall / furniture" and (w < 5 or h < 5):
                continue
            # (The same picture twice in one place is one thing drawn again in front: a `cover`.)
            if name_of(a) == name_of(b) and abs(a["x"] - b["x"]) < 2 and abs(a["y"] - b["y"]) < 2:
                continue
            found.append((rule, deck_of(a), round((max(a["x"], b["x"]) - 480) / 48, 1), name_of(a), name_of(b), w, h,
                          max(a["x"], b["x"]) + w // 2, max(a["y"], b["y"]) + h // 2))
    return found


def main():
    b = P.Browser()
    seen, rows = set(), []
    try:
        for state in ("start", "late"):
            if state == "start":
                b.open("?reset&play")
            else:
                P.enter_region8(b)
                b.eval("(P => { ['engineer', 'horn', 'lady'].forEach(f => P.setFlag(f)); })(window.__ship.progress); window.__ship.world.refresh()")
            time.sleep(1.0)
            for row in audit(json.loads(b.eval(DUMP))):
                if row[:5] not in seen:
                    seen.add(row[:5])
                    rows.append(row + (state,))
        order = ["door / furniture", "door / door", "text / door", "text / furniture", "text / wall", "text / text", "wall / furniture"]
        rows.sort(key=lambda r: (order.index(r[0]), r[1], r[2]))
        for rule, deck, m, na, nb, w, h, cx, cy, state in rows:
            print(f"{rule:17} deck {deck:2} {m:6.1f} m  {na}  x  {nb}  ({w}x{h} px, {state})")
        print(len(rows), "overlaps")
        if "--shots" in sys.argv and rows:
            from PIL import Image, ImageDraw
            tiles = []
            late = False
            for i, (rule, deck, m, na, nb, w, h, cx, cy, state) in enumerate(rows):
                if state == "start" and late:
                    continue
                b.teleport(cx + 200, floor_y(deck))
                time.sleep(0.5)
                tile = Image.open(b.close_up("overlap", cx, cy - 10, 200, 110, 2, deck))
                ImageDraw.Draw(tile).text((3, 3), f"{i}: {rule} d{deck} {m} {na} x {nb}"[:66], fill=(255, 255, 0))
                tiles.append(tile)
            for n in range(0, len(tiles), 12):
                part = tiles[n:n + 12]
                sheet = Image.new("RGB", (3 * 400, ((len(part) + 2) // 3) * 220))
                for i, tile in enumerate(part):
                    sheet.paste(tile, ((i % 3) * 400, (i // 3) * 220))
                out = P.OUT / f"overlap-{n // 12}.png"
                sheet.save(out)
                print(out)
    finally:
        b.close()


if __name__ == "__main__":
    main()
