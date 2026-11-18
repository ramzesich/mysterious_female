"""The corridors, from the data alone (no browser): along each deck's inside lane, the longest
walk with nothing to do (no reward, no hazard, no errand, no room, no Bumbot, no checkpoint)
and the longest without a reward (docs/plan-three-uses.md §4.7; the audit of 2026-11-15, C9).
Run at the end of a step that places things on the decks, and give its numbers.

    python tools/check_corridors.py [--all]     (--all: every stretch over the limits, not only the longest)
"""
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ship_layout as L  # noqa: E402

w = json.loads((ROOT / "maps" / "world.json").read_text(encoding="utf-8"))
m = json.loads((ROOT / "maps" / "ship.json").read_text(encoding="utf-8"))


def metres(x):
    return round((x - 480) / 48, 1)


def deck_of(y):
    return round(12 - (y - 416) / 144)


# What counts: a reward (something to take), or a beat (something to do or get past).
REWARD = {"tangerine", "item", "slot", "quirk", "jackpot", "keep", "dog"}     # (the dog's: its owner's tennis ball)
BEAT = {"swingdoor", "sprinkler", "trays", "dnd", "spill", "wet", "queue", "darter", "stack", "gull", "foodgull", "robot",
        "light", "low", "breakable", "rounds", "opendoor", "push", "solid", "roller", "fetcher", "skimmer", "climb",
        "source", "cat", "checkpoint"}
LIMITS = {"beat": 20, "reward": 30}

rows = collections.defaultdict(list)            # deck -> [(m, class)]
for e in w["ents"]:
    if "y" not in e or "x" not in e or e.get("route", "inside") != "inside":
        continue
    k, d = e["kind"], deck_of(e["y"])
    if k == "person":
        if e.get("touch") or e.get("bubble") or e.get("walk"):
            rows[d].append((metres(e["x"]), "beat"))
    elif k in REWARD:
        rows[d].append((metres(e["x"]), "reward"))
    elif k in BEAT:
        rows[d].append((metres(e["x"]), "beat"))
for r in w["rooms"]:
    for door in r["doors"]:
        if door.get("outRoute", "inside") == "inside":
            rows[deck_of(door["outY"])].append((metres(door["outX"]), "reward"))
for layer in m["layers"]:
    if layer["type"] != "objectgroup":
        continue
    for o in layer["objects"]:
        if (o.get("type") or o.get("class")) == "vacuum":
            rows[deck_of(o["y"])].append((metres(o["x"]), "beat"))

every = "--all" in sys.argv
for deck in sorted(rows, reverse=True):
    ext = L.EXTENT.get(deck)
    if not ext:
        continue
    beats = sorted(mm for mm, _ in rows[deck])
    rewards = sorted(mm for mm, c in rows[deck] if c == "reward")
    line = [f"deck {deck:2}"]
    for name, pts in (("beat", beats), ("reward", rewards)):
        edges = [ext[0]] + pts + [ext[1]]
        gaps = sorted(((b - a, a, b) for a, b in zip(edges, edges[1:])), reverse=True)
        g, a, b = gaps[0]
        line.append(f"longest without a {name}: {g:5.1f} m ({a:.0f} to {b:.0f})")
        if every:
            for g, a, b in gaps:
                if g > LIMITS[name]:
                    print(f"deck {deck:2}: no {name} for {g:5.1f} m, {a:6.1f} to {b:6.1f}")
    print("   ".join(line))
