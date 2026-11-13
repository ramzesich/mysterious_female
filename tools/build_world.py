"""The world of the plan as the game reads it: maps/world.json, built from tools/population.py with
the map builder's positions (called by tools/build_ship_map.py). Rooms behind doors, checkpoints,
tangerines, pickups, Bumbot's beats, switches, the outside route's platforms and walls (the boat
walkway, the balconies and their partitions), grips for wall jumps, ladders between routes, the
funnel's top.
"""

import json

import build_ship_map as B
from population import (DARTERS, DND, GLIMPSE_BALCONY, LINEN, LOWS, OPENDOORS, SPRINKLERS, STACKS, SWINGDOORS)
from population import FOODGULLS, LIDO, PLATFORMS, QUEUES, TRAYS, WETS
from population import BALCONY_CPS, DRILL, GUSTS, LINES, OCCUPIED, PERCH, ROUNDS
from population import BALLS, COURT, FLARES, FLOCKS, FUNNEL_TOP, LADY, TERRACE
from population import (BEAT_LIFT, BEATS, BREAKABLES, CATCH_M, CHECKPOINTS, CHIPS, DUCT, FLAG_GIVES, FLASH, GLIMPSE_WINDOW,
                        GRIPS, GULLS, ITEMS, JACKPOTS, LIBRARY, LIGHTS, PEOPLE, PROPS, PUSHABLES, QUIRKS, ROBOTS, ROOMS, SIGNS,
                        SLOTS, SOLIDS, SOURCES, STAGE, SWITCHES, TANGERINES, TRAPDOOR_LANDS, TRAPDOOR_M)
from ship_layout import EXTENT, FUNNEL, LINEN_ROOM, OUR_CABIN, PROMENADE, VENUES

OUTSIDE = "promenade"       # the game's name for the outside route (deck 6's promenade came first)
ROOM_DOOR_X = 59            # a room's door, in from its left edge (the drawings agree)
PARTITION_H = 88            # a balcony partition: taller than her jump (68)
POLE_H = 140                # the pole on a partition's top, up to the balcony above
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

    # The duct, drawn shorter than the way it stands for (a crawl of about a quarter of a minute):
    # from the linen room's end forward, its grilles evenly along it, the last one the way out.
    dx1 = B.x_of(DUCT["m_in"]) + 40
    dx0 = dx1 - DUCT["length"]
    n = len(DUCT["grilles"]) + 1
    duct = dict(x0=dx0, x1=dx1, floor=B.floor_y(DUCT["deck"]), exitX=dx0 + 70,
                dropX=B.x_of(DUCT["m_out"]), dropY=B.floor_y(DUCT["drop_deck"]),
                grilles=[dict(x=round(dx1 - 120 - (i + 1) * (DUCT["length"] - 250) / n), what=what)
                         for i, what in enumerate(DUCT["grilles"])])

    def spot(where, at):
        """(x, y, route) of a thing on a deck at `at` m, or in a room `at` px from its left edge (in
        the duct: px along it from the linen room's end)."""
        if where == "funnel":
            return B.exact_x(at), funnel_top()["y"], "inside"
        if where == "duct":
            return duct["x1"] - at, duct["floor"], "duct"
        # Outside: the promenade's deck, the boat walkway over it.
        if where in ("prom", "walkway"):
            return B.exact_x(at), B.floor_y(6 if where == "prom" else 7), OUTSIDE
        # On a balcony of deck 8, 9 or 10 ("b8"...).
        if isinstance(where, str) and where[0] == "b" and where[1:].isdigit():
            return B.exact_x(at), B.floor_y(int(where[1:])), OUTSIDE
        if isinstance(where, str):
            return room_x0[where] + at, room_floor[where], where
        return B.exact_x(at), B.floor_y(where), "inside"

    for cid, (deck, m, route, slot) in CHECKPOINTS.items():
        x = slot_x(deck, m) if slot else B.exact_x(m)
        ents.append(dict(kind="checkpoint", id=cid, x=x, y=B.floor_y(deck), route=route_of(route)))
    # On the balconies: at each ajar balcony door, a lamp over it.
    for cid, rid in BALCONY_CPS.items():
        d = next(d for r in rooms if r["id"] == rid for d in r["doors"] if d["kind"] == "balcony")
        ents.append(dict(kind="checkpoint", id=cid, x=d["outX"], y=d["outY"], route=OUTSIDE, bare=True))

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
                         on=on[0] if on else None, frame=on[1] if len(on) > 1 else ""))

    for pid, d in PEOPLE.items():
        x, y, route = spot(*d["at"])
        e = dict(kind="person", id=pid, x=x, y=y, route=route, who=d["who"], face=d.get("face", 1),
                 idle=d.get("idle", ""), layer=d.get("layer", ""), until=d.get("until", ""), after=d.get("after", ""),
                 pose=d.get("pose", ""), still=d.get("still", ""), dy=d.get("dy", 0))
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
    for bid, (where, at, pieces, *opts) in BREAKABLES.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="breakable", id=bid, x=x, y=y, route=route, pieces=pieces, **(opts[0] if opts else {})))
    for sid, (where, at, gives, after, show, *rest) in SOURCES.items():
        x, y, route = spot(where, at)
        # (`when`: it is there to see, but hers to take only then; `until`: gone after.)
        ents.append(dict(kind="source", id=sid, x=x, y=y, route=route, gives=gives, after=after or "", show=show,
                         when=rest[0] if rest else "", until=rest[1] if len(rest) > 1 else ""))
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
    for sid, (where, at, up, *after) in SLOTS.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="slot", id=sid, x=x, y=y, route=route, dy=up, after=after[0] if after else ""))

    for lid, (deck, m, flag, short, long, amp, period) in LIGHTS.items():
        ents.append(dict(kind="light", id=lid, x=B.exact_x(m), top=B.floor_y(deck) - 128, floor=B.floor_y(deck), route="inside",
                         flag=flag, short=short, long=long, amp=amp, period=period))
    for cid, (deck, m, half) in CHIPS.items():
        ents.append(dict(kind="spill", id=cid, x=B.exact_x(m), y=B.floor_y(deck), route="inside", half=round(half * 48), top=64))
    for jid, (deck, m, flag, up) in JACKPOTS.items():
        ents.append(dict(kind="jackpot", id=jid, x=B.exact_x(m), y=B.floor_y(deck), route="inside", flag=flag, dy=up))

    # Region 4's hazards (src/world/movers.js).
    for did, (deck, m, reach, dart) in DARTERS.items():
        ents.append(dict(kind="darter", id=did, x=slot_x(deck, m), y=B.floor_y(deck), route="inside",
                         reach=round(reach * 48), dart=round(dart * 48)))
    for sid, (deck, m) in STACKS.items():
        ents.append(dict(kind="stack", id=sid, x=B.exact_x(m), y=B.floor_y(deck), route="inside"))
    for sid, (deck, m, half, period, on, offset) in SPRINKLERS.items():
        ents.append(dict(kind="sprinkler", id=sid, x=B.exact_x(m), y=B.floor_y(deck), top=B.floor_y(deck) - 128, route="inside",
                         half=round(half * 48), period=period, on=on, offset=offset))
    for sid, (deck, m, reach, delay, who) in SWINGDOORS.items():
        ents.append(dict(kind="swingdoor", id=sid, x=slot_x(deck, m), y=B.floor_y(deck), route="inside",
                         reach=round(reach * 48), delay=delay, who=who))
    for did, (deck, m, who) in DND.items():
        ents.append(dict(kind="dnd", id=did, x=slot_x(deck, m), y=B.floor_y(deck), route="inside", who=who))
    for oid, (deck, m, what) in OPENDOORS.items():
        ents.append(dict(kind="opendoor", id=oid, x=slot_x(deck, m), y=B.floor_y(deck), route="inside", what=what))
    for lid, (where, a, b, frame) in LOWS.items():
        x0, y, route = spot(where, a)
        ents.append(dict(kind="low", id=lid, x=(x0 + spot(where, b)[0]) // 2, x0=x0, x1=spot(where, b)[0], y=y, route=route,
                         frame=frame or ""))

    # Region 6's (src/world/movers.js, src/world/lido.js).
    for pid, (deck, a, b, up) in PLATFORMS.items():
        ents.append(dict(kind="platform", id=pid, x0=B.exact_x(a), x1=B.exact_x(b), y=B.floor_y(deck) - up, route="inside"))
    for wid, (deck, a, b, chair) in WETS.items():
        ents.append(dict(kind="wet", id=wid, x=B.exact_x((a + b) / 2), x0=B.exact_x(a), x1=B.exact_x(b), y=B.floor_y(deck),
                         chairX=B.exact_x(chair), route="inside"))
    for gid, (deck, a, b, count, wait, off) in FOODGULLS.items():
        e = dict(kind="foodgull", id=gid, x=B.exact_x((a + b) / 2), x0=B.exact_x(a), x1=B.exact_x(b), y=B.floor_y(deck),
                 count=count, off=off or "", route="inside")
        if wait != "circle":
            e["perch"] = dict(x=B.exact_x(wait[0]), y=B.floor_y(deck) - wait[1])
        ents.append(e)
    for qid, (deck, a, b, v, who) in QUEUES.items():
        ents.append(dict(kind="queue", id=qid, x=B.exact_x(a), x0=B.exact_x(a), x1=B.exact_x(b), y=B.floor_y(deck), v=v,
                         who=who, route="inside"))
    for tid, (deck, a, b, door, flag) in TRAYS.items():
        ents.append(dict(kind="trays", id=tid, x=B.exact_x((a + b) / 2), x0=B.exact_x(a), x1=B.exact_x(b), y=B.floor_y(deck),
                         door=door, flag=flag, route="inside"))
    # Region 7's (src/world/outside.js).
    for rid, (deck, a, b, v, stops, wait, who) in ROUNDS.items():
        ents.append(dict(kind="rounds", id=rid, x=B.exact_x(a), x0=B.exact_x(a), x1=B.exact_x(b), y=B.floor_y(deck), v=v,
                         stops=[slot_x(deck, m) for m in stops], wait=wait, who=who, route="inside"))

    for bid, (where, at, activity, escape, gone, needs) in BEATS.items():
        x, y, route = spot(where, at)
        exit_x = spot(where, gone)[0]
        ents.append(dict(kind="cat", id=bid, x=x, y=y, route=route, activity=activity, escape=escape, exitX=exit_x,
                         needs=needs or "", lift=lift_of(BEAT_LIFT.get(bid, 0))))

    for pid, (where, at, to, frame, flag, tall, sides, *needs) in PUSHABLES.items():
        x, y, route = spot(where, at)
        ents.append(dict(kind="push", id=pid, x=x, y=y, route=route, min=x, max=spot(where, to)[0], frame=frame,
                         flag=flag or "", tall=tall, sides=sides, needs=needs[0] if needs else ""))

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
    # A laundry line: the partition nearest to it is folded open (no panel, no pole).
    lines = {}
    for lid, (deck, m) in LINES.items():
        ux = min((u for d, u in units if d == deck and (deck, u - UNIT) in units), key=lambda u: abs(u + 3 - B.exact_x(m)))
        lines[(deck, ux)] = lid
    for deck, ux in units:
        y = B.floor_y(deck)
        platforms.append(dict(x0=ux, x1=ux + UNIT, y=y, solid=False, drop=True, id=f"balcony-{deck}-{ux}"))
        glass.append(dict(x0=ux + 6, x1=ux + UNIT, y=y, deck=deck))
        if (deck, ux) in lines:
            glass.append(dict(x0=ux, x1=ux + 6, y=y, deck=deck))
            continue
        walls.append(dict(x=ux + 3, y0=y - PARTITION_H, y1=y, w=6))
        # (The panel is solid; the pole on its top runs up to the balcony above, a grip all the way:
        # a kick off the panel vaults it, kicks with up held climb the pole to the next deck.)
        grips.append(dict(route=OUTSIDE, x=ux + 3, y0=y - POLE_H, y1=y, side=0, w=6, over=True, panel=PARTITION_H))
        # A row's last balcony ends in the ship's wall.
        if (deck, ux + UNIT) not in units:
            walls.append(dict(x=ux + UNIT + 3, y0=y - 128, y1=y, w=6))
        if (deck, ux - UNIT) not in units:
            walls.append(dict(x=ux - 3, y0=y - 128, y1=y, w=6))
    # The recess's end walls: from the walkway up to deck 8's floor, each a grip on its open side;
    # and the white columns between the boats, deck 7's height: kicks with up held climb any of them
    # onto deck 8's balconies.
    for m, side in zip(PROMENADE["span"], (1, -1)):
        walls.append(dict(x=B.x_of(m), y0=B.floor_y(8), y1=B.floor_y(7), w=8))
        grips.append(dict(route=OUTSIDE, x=B.x_of(m), y0=B.floor_y(8) - 6, y1=B.floor_y(7), side=side, w=8))
    for m in PROMENADE["columns"]:
        grips.append(dict(route=OUTSIDE, x=B.exact_x(m), y0=B.floor_y(8) - 6, y1=B.floor_y(7), side=0, w=10))

    # (No grips on the stern's tiers: on the aft terraces she is out of sight behind the stern's
    # plating, the user's rule, so the plan's climb up the stern is left out.)

    # The balconies' own things (src/world/outside.js): the laundry lines, the perched gulls, the
    # balconies with someone on them; towels on the rails (they flap before a gust) and the
    # furniture, by a rule that leaves the balconies with something on them clear.
    def unit_at(deck, m):
        return nearest_balcony(deck, B.exact_x(m))

    perch = [dict(id=gid, x=unit_at(deck, m) + 88, y=B.floor_y(deck) - 50, floor=B.floor_y(deck), x0=unit_at(deck, m))
             for gid, (deck, m) in PERCH.items()]
    occupied = [dict(id=oid, x0=unit_at(deck, m), x1=unit_at(deck, m) + UNIT, y=B.floor_y(deck), frame=frame)
                for oid, (deck, m, frame) in OCCUPIED.items()]
    busy = {(B.floor_y(deck), ux) for (deck, ux) in lines} | {(B.floor_y(deck), ux - UNIT) for (deck, ux) in lines}
    busy |= {(o["y"], o["x0"]) for o in occupied}
    busy |= {(d["outY"], nearest_balcony(r["deck"], d["outX"])) for r in rooms for d in r["doors"] if d["kind"] == "balcony"}
    busy |= {(e["y"], nearest_balcony(deck, e["x"])) for e in ents for deck in (8, 9, 10)
             if e.get("route") == OUTSIDE and e["y"] == B.floor_y(deck) and e["kind"] in ("tangerine", "slot", "person")}
    towels, furniture = [], []
    sets = [[("cafe-chair-bg", 34, False), ("cafe-table-bg", 62, False), ("cafe-chair-bg", 90, True)],
            [("sunlounger-bg", 60, False)], [("deck-chair-bg", 40, False), ("small-plant-bg", 104, False)],
            [("bistro-table-bg", 84, False), ("bistro-chair-bg", 56, False)], [("plant-bg", 100, False)],
            [("sunlounger-2-bg", 74, True), ("side-table-bg", 34, False)], [("deck-chair-2-bg", 82, True)]]
    for deck, ux in units:
        y = B.floor_y(deck)
        h = (ux * 7919 + deck * 104729) % 1000
        if (y, ux) in busy:
            continue
        if h % 10 < 3:
            towels.append(dict(x=ux + 28 + h % 67, y=y - 50, tint=h % 5))
        if (h // 10) % 10 < 6:
            for frame, dx, flip in sets[(h // 100 + deck) % len(sets)]:
                furniture.append(dict(x=ux + dx, y=y, frame=frame, flip=flip))
    balcony = dict(gust=GUSTS, towels=towels, furniture=furniture, perch=perch, occupied=occupied,
                   lines=[dict(id=lid, x=ux + 3, y=B.floor_y(deck)) for (deck, ux), lid in lines.items()],
                   top=B.floor_y(10) - 144, bottom=B.floor_y(8), x0=min(u for _, u in units), x1=max(u for _, u in units) + UNIT)
    drill = dict(x=B.exact_x(DRILL["m"]), y=B.floor_y(7), top=B.floor_y(8), period=DRILL["period"], down=DRILL["down"],
                 tell=DRILL["tell"])

    for route, m, deck, y0, y1, side in GRIPS:
        fy = B.floor_y(deck)
        grips.append(dict(route=route_of(route), x=B.exact_x(m), y0=fy - y1, y1=fy - y0, side=side, w=8))

    # Ladders between routes: the lifeboat station's on the promenade, up its column to the walkway.
    ladders = [dict(id="gate", x=B.x_of(125), y0=B.floor_y(6), y1=B.floor_y(7), routeBottom=OUTSIDE, routeTop=OUTSIDE,
                    lock="card:deck:1", gate=True)]
    # Ladders on the map that open on a flag (the bridge's hatch, after the alarm).
    gates = [dict(x=B.BRIDGE_HATCH_COL * B.TILE + B.TILE // 2, y0=B.floor_y(11), y1=B.floor_y(10), needs="alarm", hide=True)]
    # The technical ladder at Cagney's, up to the roof: chained off until the engineer has had his
    # coffee and gone up it (population: `scn_engineer`).
    ladder_x = B.funnel_ladder_col() * B.TILE + B.TILE // 2
    gates.append(dict(x=ladder_x, y0=B.ROOF_ROW * B.TILE, y1=B.floor_y(12), needs="engineer", hide=False,
                      sign="TECHNICAL\nCREW ONLY"))

    lib_y = B.floor_y(LIBRARY["deck"])
    library = dict(shelf=dict(x0=B.exact_x(LIBRARY["shelf"][0]), y=lib_y - LIBRARY["shelf"][1]),
                   trolley=dict(x=B.exact_x(LIBRARY["trolley"]), y=lib_y), chair=dict(x=B.exact_x(LIBRARY["chair"]), y=lib_y))
    flash = dict(x0=B.exact_x(FLASH[1]), x1=B.exact_x(FLASH[2]), y=B.floor_y(FLASH[0]), period=FLASH[3])
    window = dict(x=B.exact_x(GLIMPSE_WINDOW[0]), y=B.floor_y(6) - GLIMPSE_WINDOW[1], floor=B.floor_y(6))

    stage_y = B.floor_y(STAGE["deck"])
    stage = dict(floor=stage_y, top=stage_y - 128, wingX=B.exact_x(STAGE["wing"]), cableX=B.exact_x(STAGE["cable"]),
                 trapX=B.exact_x(TRAPDOOR_M), ropeX=B.exact_x(STAGE["rope"]))

    linen = dict(ventX=room_x0["linen"] + LINEN["vent"], sill=LINEN["sill"], chuteX=room_x0["linen"] + LINEN["chute"],
                 cartTop=LINEN["cart_top"], laundryCartX=room_x0["laundry"] + LINEN["laundry_cart"])
    gdeck, gm = GLIMPSE_BALCONY
    gx = nearest_balcony(gdeck, slot_x(gdeck, gm))
    glimpse_balcony = dict(x0=gx, x1=gx + UNIT, y=B.floor_y(gdeck), topY=B.floor_y(gdeck) - PARTITION_H)

    ly = B.floor_y(LIDO["deck"])
    pools = [dict(x0=B.col(a) * B.TILE, x1=B.col(b) * B.TILE) for a, b in B.POOLS]
    lido = dict(y=ly, leverX=B.exact_x(LIDO["lever"]), ladderX=B.exact_x(LIDO["ladder"]), tubX=B.exact_x(LIDO["tub"]),
                kidA=B.exact_x(LIDO["kid"][0]), kidB=B.exact_x(LIDO["kid"][1]), loungerX=B.exact_x(LIDO["lounger"]),
                chessX=B.exact_x(LIDO["chess"]), machineX=B.exact_x(LIDO["machine"]), husbandX=B.exact_x(LIDO["husband"]),
                tableX=B.exact_x(LIDO["table"]), pawsA=B.exact_x(LIDO["paws"][0]), pawsB=B.exact_x(LIDO["paws"][1]),
                pools=pools, tankY=ly + B.POOL_DEPTH)

    # Region 8's (src/world/topdeck.js): the old lady's sunbed, the court's balls, the flares, the
    # pinata, the aft terrace's gusts and gull, the funnel's wind, gulls and top, the bow's flocks.
    y12 = B.floor_y(12)
    ft = funnel_top()
    look = next(e for e in ents if e["id"] == FUNNEL_TOP["look"])
    topdeck = dict(
        y=y12,
        lady=dict(x=B.exact_x(LADY["m"]), y=y12, half=LADY["half"], tall=LADY["tall"], rivalX=B.exact_x(LADY["rival"]),
                  cardX=B.exact_x(LADY["card"])),
        balls=[dict(id=bid, x=B.exact_x(m), y=B.floor_y(deck), dir=way, reach=round(reach * 48), period=period, offset=offset)
               for bid, (deck, m, way, reach, period, offset) in BALLS.items()],
        court=dict(ballX=B.exact_x(COURT["ball"]), hoopX=B.exact_x(COURT["hoop"]), y=B.floor_y(COURT["deck"])),
        flares=[dict(id=fid, x=B.exact_x(m), y=B.floor_y(deck), half=round(half * 48), period=period, on=on, offset=offset,
                     chef=chef) for fid, (deck, m, half, period, on, offset, chef) in FLARES.items()],
        terrace=dict(gust=TERRACE["gust"], x0=B.exact_x(TERRACE["span"][0]), x1=B.exact_x(TERRACE["span"][1]),
                     top=y12 - 260, bottom=B.floor_y(11), y=y12,
                     towels=[dict(x=B.exact_x(m), y=y12 - up, tint=i + 1) for i, (m, up) in enumerate(TERRACE["towels"])],
                     gull=dict(id="gull_terrace", x=B.exact_x(TERRACE["gull"][0]), y=y12 - TERRACE["gull"][1], floor=y12)),
        funnel=dict(gust=FUNNEL_TOP["gust"], gulls=FUNNEL_TOP["gulls"], swoop=FUNNEL_TOP["swoop"],
                    hornX=B.exact_x(FUNNEL_TOP["horn"]), toolboxX=B.exact_x(FUNNEL_TOP["toolbox"]),
                    telescopeX=B.exact_x(FUNNEL_TOP["telescope"]), y=ft["y"], roofY=ft["foot"][1], ladderX=ladder_x,
                    x0=ladder_x - 60, x1=ft["x1"] + 40,
                    look=dict(x=look["x"], y=look["y"] - look["dy"], id=look["id"])),
        flocks=[dict(id=fid, x0=B.exact_x(a), x1=B.exact_x(b), y=B.floor_y(deck) - up, n=n)
                for fid, (deck, a, b, n, up) in FLOCKS.items()])

    return dict(rooms=rooms, ents=ents, flagGives=FLAG_GIVES, funnel=funnel_top(), duct=duct, linen=linen, lido=lido,
                topdeck=topdeck,
                glimpseBalcony=glimpse_balcony, balcony=balcony, drill=drill,
                library=library, flash=flash, glimpseWindow=window, stage=stage,
                outside=dict(platforms=platforms, walls=walls, glass=glass, partition=PARTITION_H),
                grips=grips, ladders=ladders, ladderGates=gates,
                hatchPool=dict(x=B.x_of(125), y=B.floor_y(11), toY=B.floor_y(10)),
                trapdoor=dict(x=B.exact_x(TRAPDOOR_M), y=B.floor_y(6), room=TRAPDOOR_LANDS[0],
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
