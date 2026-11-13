"""The world of the plan as the game reads it: maps/world.json, built from tools/population.py with
the map builder's positions (called by tools/build_ship_map.py). Rooms behind doors, checkpoints,
tangerines, pickups, Bumbot's beats, switches, the outside route's platforms and walls (the boat
walkway, the balconies and their partitions), grips for wall jumps, ladders between routes, the
funnel's top.
"""

import json

import build_ship_map as B
from population import (BEAT_LIFT, BEATS, BREAKABLES, CATCH_M, CHECKPOINTS, DUCT, FLAG_GIVES, FLASH, GLIMPSE_WINDOW, GRIPS,
                        GULLS, ITEMS, LIBRARY, PEOPLE, PROPS, PUSHABLES, QUIRKS, ROBOTS, ROOMS, SIGNS, SLOTS, SOLIDS, SOURCES,
                        SWITCHES, TANGERINES, TRAPDOOR_LANDS, TRAPDOOR_M)
from ship_layout import EXTENT, FUNNEL, LINEN_ROOM, OUR_CABIN, PROMENADE, VENUES

OUTSIDE = "promenade"       # the game's name for the outside route (deck 6's promenade came first)
ROOM_DOOR_X = 59            # a room's door, in from its left edge (the drawings agree)
PARTITION_H = 88            # a balcony partition: taller than her jump (68)
UNIT = 125                  # a balcony, px


def cabin_slots(deck):
    """Every cabin door's x on a deck's corridors (the builder's own layout: one every 192 px)."""
    xs = []
    for d, a, b, _name, kind in VENUES:
        if d != deck or kind != "cabins":
            continue
        cols = [c for c in range(B.col(a), B.col(b))
                if B.covered(deck, B.metres(c)) and not B.in_structure(deck, c) and not B.in_end_wall(deck, c)]
        runs = []
        for c in cols:
            if runs and runs[-1][1] == c:
                runs[-1][1] = c + 1
            else:
                runs.append([c, c + 1])
        for c0, c1 in runs:
            xs += [x + 17 for x in range(c0 * B.TILE + 60, c1 * B.TILE - 30, 192)]
    return xs


def slot_x(deck, m):
    """The cabin door nearest to `m` on `deck`."""
    return min(cabin_slots(deck), key=lambda x: abs(x - B.x_of(m)))


def lift_of(what):
    """Px up: a number, or the height of the atlas piece something rests on."""
    if isinstance(what, str):
        art = json.loads((B.ROOT / "assets" / "ship" / "ship.json").read_text(encoding="utf-8"))["frames"]
        return art[what]["frame"]["h"]
    return what


def route_of(name):
    return OUTSIDE if name == "outside" else name


def balcony_units():
    """Each balcony drawn on the shell (deck, x of its forward partition), from the builder's run."""
    return sorted(set(B.BALCONY_UNITS))


def nearest_balcony(deck, x):
    return min((ux for d, ux in balcony_units() if d == deck), key=lambda ux: abs(ux + 6 + (UNIT - 6) / 2 - x))


def build_world():
    rooms, ents = [], []
    room_x0 = {}        # room id -> its drawing's left edge
    room_floor = {}

    def lock(spec):
        return B.lock_text(spec) if spec else ""

    # The rooms built before the plan keep their own code in the game; things in them are placed
    # from their left edge all the same.
    room_x0["cabin"] = slot_x(OUR_CABIN["deck"], OUR_CABIN["m"]) - ROOM_DOOR_X
    room_floor["cabin"] = B.floor_y(OUR_CABIN["deck"])
    room_x0["linen"] = slot_x(LINEN_ROOM["deck"], LINEN_ROOM["m"]) - ROOM_DOOR_X
    room_floor["linen"] = B.floor_y(LINEN_ROOM["deck"])

    for r in ROOMS:
        deck = r["deck"]
        door = slot_x(deck, r["m"]) if r.get("slot") else B.exact_x(r["m"])
        x0 = door - r.get("door_x", ROOM_DOOR_X)
        floor = B.floor_y(deck)
        room_x0[r["id"]], room_floor[r["id"]] = x0, floor
        doors = [dict(id=r["id"], x=door, outX=door, outY=floor, outRoute=route_of(r.get("route", "inside")),
                      kind=r.get("door", "crew"), plate=r.get("plate", ""), lock=lock(r.get("lock")))]
        for i, d in enumerate(r.get("doors", [])):
            if d["to"] == "outside":
                ux = nearest_balcony(d["deck"], door)
                out_x, out_y = ux + 6 + (UNIT - 6) // 2, B.floor_y(d["deck"])
            else:
                out_x = slot_x(d["deck"], d["m"]) if d.get("slot") else B.exact_x(d["m"])
                out_y = B.floor_y(d["deck"])
            doors.append(dict(id=f"{r['id']}-{i + 2}", x=x0 + d["x"], outX=out_x, outY=out_y, outRoute=route_of(d["to"]),
                              kind=d.get("door", "crew"), plate=d.get("plate", ""), lock=lock(d.get("lock"))))
        rooms.append(dict(id=r["id"], deck=deck, x0=x0, floor=floor, width=r["width"], look=r["look"],
                          art=(B.ROOT / "assets" / "ship" / "rooms" / f"{r['id']}.png").exists(),
                          needs=r.get("needs", ""), checkpoint=r.get("checkpoint", ""), doors=doors))

    def spot(where, at):
        """(x, y, route) of a thing on a deck at `at` m, or in a room `at` px from its left edge."""
        if where == "funnel":
            return B.exact_x(at), funnel_top()["y"], "inside"
        # Outside: the promenade's deck, the boat walkway over it.
        if where in ("prom", "walkway"):
            return B.exact_x(at), B.floor_y(6 if where == "prom" else 7), OUTSIDE
        if isinstance(where, str):
            return room_x0[where] + at, room_floor[where], where
        return B.exact_x(at), B.floor_y(where), "inside"

    for cid, (deck, m, route, slot) in CHECKPOINTS.items():
        x = slot_x(deck, m) if slot else B.exact_x(m)
        ents.append(dict(kind="checkpoint", id=cid, x=x, y=B.floor_y(deck), route=route_of(route)))

    for tid, (where, at, count, on, needs) in TANGERINES.items():
        outside = on == "out"
        x, y, route = spot(where, at)
        if outside:
            x = nearest_balcony(where, x) + 40
            route = OUTSIDE
        for k in range(count):
            ents.append(dict(kind="tangerine", id=tid if count == 1 else f"{tid}#{k}", x=x + k * 9 - (count - 1) * 4, y=y,
                             route=route, on="table" if on in ("table", "out") else int(on), needs=needs or "",
                             first=k == 0))

    for iid, (where, at, what, needs, *on) in ITEMS.items():
        x, y, route = spot(where, at)
        # `on`: px up, on a piece already there (a table); else on a side table of its own.
        ents.append(dict(kind="item", id=iid, x=x, y=y, route=route, what=what, needs=needs or "",
                         on=on[0] if on else None))

    for pid, d in PEOPLE.items():
        x, y, route = spot(*d["at"])
        e = dict(kind="person", id=pid, x=x, y=y, route=route, who=d["who"], face=d.get("face", 1),
                 idle=d.get("idle", ""), layer=d.get("layer", ""), until=d.get("until", ""), after=d.get("after", ""),
                 pose=d.get("pose", ""))
        if "walk" in d:
            a, b, v, *clip = d["walk"]
            e["walk"] = dict(a=spot(d["at"][0], a)[0], b=spot(d["at"][0], b)[0], v=v, clip=clip[0] if clip else "walk",
                             stops=[spot(d["at"][0], m)[0] for m in d.get("stops", [])],
                             stopMs=d.get("stop_ms", 2200), endMs=d.get("end_ms", 600))
        if "touch" in d:
            kind, w, h, *rest = d["touch"]
            e["touch"] = dict(kind=kind, w=w, h=h, fright=rest[0] if rest else "", dx=rest[1] if len(rest) > 1 else 0)
        if "carry" in d:
            e["carry"] = [dict(frame=f, dx=dx, dy=dy, front=front) for f, dx, dy, front in d["carry"]]
        if "cover" in d:
            e["cover"] = [dict(frame=f, x=spot(d["at"][0], m)[0], dy=dy) for f, m, dy in d["cover"]]
        if "bubble" in d:
            icon, when, unless, *rng = d["bubble"]
            e["bubble"] = dict(icon=icon, when=when or "", unless=unless or "", range=rng[0] if rng else 4)
        ents.append(e)

    for pid, (where, at, frame, dy, opts) in PROPS.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="prop", id=pid, x=x, y=y, route=route, frame=frame, dy=dy, **opts))
    for sid, (where, at, frame) in SOLIDS.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="solid", id=sid, x=x, y=y, route=route, frame=frame))
    for bid, (where, at, pieces) in BREAKABLES.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="breakable", id=bid, x=x, y=y, route=route, pieces=pieces))
    for sid, (where, at, gives, after, show) in SOURCES.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="source", id=sid, x=x, y=y, route=route, gives=gives, after=after or "", show=show))
    for qid, (where, at, trigger, clip, ms, opts) in QUIRKS.items():
        x, y, route = spot(where, at)
        opts = dict(opts)
        if "glitter" in opts:
            gm, up = opts["glitter"]
            opts["glitter"] = [spot(where, gm)[0], y - up]
        ents.append(dict(kind="quirk", id=qid, x=x, y=y, route=route, trigger=trigger, clip=clip, ms=ms, **opts))
    for sid, (where, at, text, style, dy, opts) in SIGNS.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="sign", id=sid, x=x, y=y, route=route, text=text, style=style, dy=dy, **opts))

    for rid, (deck, a, b, v) in ROBOTS.items():
        ents.append(dict(kind="robot", id=rid, x=B.exact_x(a), y=B.floor_y(deck), route="inside", x0=B.exact_x(a),
                         x1=B.exact_x(b), v=v))
    for gid, (where, at, up) in GULLS.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="gull", id=gid, x=x, y=y - up, route=route))
    for sid, (where, at, up) in SLOTS.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="slot", id=sid, x=x, y=y, route=route, dy=up))

    for bid, (where, at, activity, escape, gone, needs) in BEATS.items():
        x, y, route = spot(where, at)
        exit_x = spot(where, gone)[0]
        ents.append(dict(kind="cat", id=bid, x=x, y=y, route=route, activity=activity, escape=escape, exitX=exit_x,
                         needs=needs or "", lift=lift_of(BEAT_LIFT.get(bid, 0))))

    for pid, (where, at, to, frame, flag, tall, sides) in PUSHABLES.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="push", id=pid, x=x, y=y, route=route, min=x, max=spot(where, to)[0], frame=frame,
                         flag=flag or "", tall=tall, sides=sides))

    for sid, (where, at, flag, needs, label) in SWITCHES.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="switch", id=sid, x=x, y=y, route=route, flag=flag, needs=needs or "", label=label))

    # The outside route (§6.1.3, region 7): the promenade's deck, the boat walkway at deck 7's height,
    # the balconies of decks 8-10: each a floor she lands on from above and can drop through, a
    # partition between two that only a wall jump gets over.
    pa, pb = (B.x_of(m) for m in PROMENADE["span"])
    platforms = [dict(x0=pa, x1=pb, y=B.floor_y(6), solid=True, id="promenade"),
                 dict(x0=pa, x1=pb, y=B.floor_y(7), solid=False, drop=False, id="walkway")]
    walls, grips, glass = [], [], []
    units = balcony_units()
    for deck, ux in units:
        y = B.floor_y(deck)
        platforms.append(dict(x0=ux, x1=ux + UNIT, y=y, solid=False, drop=True, id=f"balcony-{deck}-{ux}"))
        glass.append(dict(x0=ux + 6, x1=ux + UNIT, y=y, deck=deck))
        walls.append(dict(x=ux + 3, y0=y - PARTITION_H, y1=y, w=6))
        grips.append(dict(route=OUTSIDE, x=ux + 3, y0=y - PARTITION_H, y1=y, side=0, w=6))
        # A row's last balcony ends in the ship's wall.
        if (deck, ux + UNIT) not in units:
            walls.append(dict(x=ux + UNIT + 3, y0=y - 128, y1=y, w=6))
        if (deck, ux - UNIT) not in units:
            walls.append(dict(x=ux - 3, y0=y - 128, y1=y, w=6))
    # The recess's end walls: from the walkway up to deck 8's floor (the builder's GRIPS add the grip).
    for m in PROMENADE["span"]:
        walls.append(dict(x=B.x_of(m), y0=B.floor_y(8), y1=B.floor_y(7), w=8))

    for route, m, deck, y0, y1, side in GRIPS:
        fy = B.floor_y(deck)
        grips.append(dict(route=route_of(route), x=B.exact_x(m), y0=fy - y1, y1=fy - y0, side=side, w=8))

    # Ladders between routes: the lifeboat station's on the promenade, up its column to the walkway.
    ladders = [dict(id="gate", x=B.x_of(125), y0=B.floor_y(6), y1=B.floor_y(7), routeBottom=OUTSIDE, routeTop=OUTSIDE,
                    lock="card:deck:1", gate=True)]
    # Ladders on the map that open on a flag (the bridge's hatch, after the alarm).
    gates = [dict(x=B.BRIDGE_HATCH_COL * B.TILE + B.TILE // 2, y0=B.floor_y(11), y1=B.floor_y(10), needs="alarm", hide=True)]

    # The duct, drawn shorter than the way it stands for (a crawl of about a quarter of a minute):
    # from the linen room's end forward, its grilles evenly along it, the last one the way out.
    dx1 = B.x_of(DUCT["m_in"]) + 40
    dx0 = dx1 - DUCT["length"]
    n = len(DUCT["grilles"]) + 1
    duct = dict(x0=dx0, x1=dx1, floor=B.floor_y(DUCT["deck"]), exitX=dx0 + 70,
                dropX=B.x_of(DUCT["m_out"]), dropY=B.floor_y(DUCT["drop_deck"]),
                grilles=[dict(x=round(dx1 - 120 - (i + 1) * (DUCT["length"] - 250) / n), what=what)
                         for i, what in enumerate(DUCT["grilles"])])

    lib_y = B.floor_y(LIBRARY["deck"])
    library = dict(shelf=dict(x0=B.exact_x(LIBRARY["shelf"][0]), y=lib_y - LIBRARY["shelf"][1]),
                   trolley=dict(x=B.exact_x(LIBRARY["trolley"]), y=lib_y), chair=dict(x=B.exact_x(LIBRARY["chair"]), y=lib_y))
    flash = dict(x0=B.exact_x(FLASH[1]), x1=B.exact_x(FLASH[2]), y=B.floor_y(FLASH[0]), period=FLASH[3])
    window = dict(x=B.exact_x(GLIMPSE_WINDOW[0]), y=B.floor_y(6) - GLIMPSE_WINDOW[1], floor=B.floor_y(6))

    return dict(rooms=rooms, ents=ents, flagGives=FLAG_GIVES, funnel=funnel_top(), duct=duct,
                library=library, flash=flash, glimpseWindow=window,
                outside=dict(platforms=platforms, walls=walls, glass=glass, partition=PARTITION_H),
                grips=grips, ladders=ladders, ladderGates=gates,
                hatchPool=dict(x=B.x_of(125), y=B.floor_y(11), toY=B.floor_y(10)),
                trapdoor=dict(x=B.x_of(TRAPDOOR_M), y=B.floor_y(6), room=TRAPDOOR_LANDS[0],
                              landX=room_x0[TRAPDOOR_LANDS[0]] + TRAPDOOR_LANDS[1]),
                catch=dict(x=B.x_of(CATCH_M), y=B.floor_y(7)),
                waterY=(B.WATER_ROW + 1) * B.TILE)


def funnel_top():
    """The funnel's stairway and top (§6.1.10), from the funnel as the game draws it: the roof, the
    casing's shoulder, the lattice's raked front up to its top, the platform along the top."""
    fa = B.x_of(FUNNEL[0]) - 8
    fb = fa + B.x_of(FUNNEL[1]) - B.x_of(FUNNEL[0]) + 16
    base = B.ROOF_ROW * B.TILE
    return dict(foot=[fa - 14, base], shoulder=[fa + 150, base - 108], head=[fa + 560, base - 500],
                x0=fa + 560, x1=fb - 150, y=base - 500)
