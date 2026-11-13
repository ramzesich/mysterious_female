"""Headless playtest driver: serves the game, opens it in headless Chrome, drives it with real key
events over the DevTools protocol, and reports state, console errors and screenshots.

    python tools/playtest.py [scenario ...]      (no arguments runs them all)

Screenshots go to the system temp folder (printed at the end). Needs Google Chrome and the
`websocket-client` package. Nothing here ships with the game.
"""

import base64
import functools
import http.server
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

import websocket

from build_ship_map import (ATRIUM, CORES, FUNNEL, POOL_OPENING, POOLS, PROMENADE, ROOF_ROW, STAGE, TILE, TRUNKS, col, exact_x,
                            floor_y, region_at, walk_y, x_of)
from ship_layout import CARD_SPOTS, DOOR_LOCKS, END_WALL_LOCKS, FLIGHT_LOCKS

ROOT = Path(__file__).resolve().parent.parent
CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
OUT = Path(tempfile.gettempdir()) / "bumbusik-playtest"

KEYS = {
    "left": (37, "ArrowLeft", "ArrowLeft"), "right": (39, "ArrowRight", "ArrowRight"),
    "up": (38, "ArrowUp", "ArrowUp"), "down": (40, "ArrowDown", "ArrowDown"),
    "space": (32, "Space", " "), "d": (68, "KeyD", "d"),
    "e": (69, "KeyE", "e"), "enter": (13, "Enter", "Enter"), "o": (79, "KeyO", "o"),
}


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Browser:
    def __init__(self):
        self.http_port = free_port()
        handler = functools.partial(Quiet, directory=str(ROOT))
        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", self.http_port), handler)
        self.httpd.handle_error = lambda *a, **k: None      # Chrome dropping a connection is no news
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

        self.debug_port = free_port()
        self.profile = tempfile.mkdtemp(prefix="bumbusik-chrome-")
        self.proc = subprocess.Popen([
            CHROME, "--headless=new", f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={self.profile}", "--window-size=960,540", "--no-first-run",
            "--autoplay-policy=no-user-gesture-required", "--enable-unsafe-swiftshader", "about:blank",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for _ in range(50):
            try:
                targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.debug_port}/json"))
                page = next(t for t in targets if t["type"] == "page")
                break
            except Exception:
                time.sleep(0.2)
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
        self.msg_id = 0
        self.errors = []
        self.send("Runtime.enable")
        self.send("Page.enable")

    def send(self, method, **params):
        self.msg_id += 1
        my_id = self.msg_id
        self.ws.send(json.dumps({"id": my_id, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("method") == "Runtime.exceptionThrown":
                d = msg["params"]["exceptionDetails"]
                self.errors.append(d.get("exception", {}).get("description") or d.get("text"))
            elif msg.get("method") == "Runtime.consoleAPICalled" and msg["params"]["type"] in ("error", "warning"):
                self.errors.append(" ".join(str(a.get("value", a.get("description", ""))) for a in msg["params"]["args"]))
            if msg.get("id") == my_id:
                return msg.get("result", {})

    def open(self, query=""):
        self.send("Page.navigate", url=f"http://127.0.0.1:{self.http_port}/index.html{query}")
        time.sleep(0.3)
        ready = "window.__ship && window.__ship.player" if "play" in query else "document.querySelector('canvas')"
        self.wait_for(ready, timeout=15)
        time.sleep(0.5)

    def eval(self, expr):
        res = self.send("Runtime.evaluate", expression=expr, returnByValue=True)
        if "exceptionDetails" in res:
            raise RuntimeError(res["exceptionDetails"].get("exception", {}).get("description"))
        return res.get("result", {}).get("value")

    def wait_for(self, expr, timeout=10):
        end = time.time() + timeout
        while time.time() < end:
            try:
                if self.eval(f"!!({expr})"):
                    return
            except RuntimeError:
                pass
            time.sleep(0.1)
        raise TimeoutError(f"timed out waiting for: {expr}  errors: {self.errors}")

    def key(self, name, down):
        code, code_name, key = KEYS[name]
        self.send("Input.dispatchKeyEvent", type="rawKeyDown" if down else "keyUp",
                  windowsVirtualKeyCode=code, nativeVirtualKeyCode=code, code=code_name, key=key)

    def hold(self, names, seconds):
        names = [names] if isinstance(names, str) else names
        for n in names:
            self.key(n, True)
        time.sleep(seconds)
        for n in names:
            self.key(n, False)

    def tap(self, name, seconds=0.08):
        self.hold(name, seconds)

    def state(self):
        return self.eval("""(() => { const s = window.__ship, p = s.player;
            return { mode: s.mode, x: Math.round(p.x), y: Math.round(p.y), tangerines: s.save.tangerines,
                     dashing: s.isDashing(), activated: s.save.activated.slice() }; })()""")

    def teleport(self, x, y, route="inside"):
        self.eval(f"window.__ship.spawnAt({{x: {x}, y: {y}, route: '{route}'}})")
        time.sleep(0.3)

    def shot(self, name):
        OUT.mkdir(exist_ok=True)
        data = self.send("Page.captureScreenshot", format="png")["data"]
        path = OUT / f"{name}.png"
        path.write_bytes(base64.b64decode(data))
        return path

    def close(self):
        try:
            self.ws.close()
        finally:
            self.proc.terminate()
            self.httpd.shutdown()


# --- Scenarios -----------------------------------------------------------------------------------
# Positions come from the map builder (tools/build_ship_map.py), in metres from the bow.

D4, D5, D6, D7, D8, D9, D10, D11, D12 = (floor_y(d) for d in (4, 5, 6, 7, 8, 9, 10, 11, 12))
SPAWN_X = x_of(67)
CORE_L = col(CORES["forward"][0]) * TILE + 4 * TILE       # forward core: the 4-5 flight's foot
LADDER_X = (col(FUNNEL[0]) - 3) * TILE + TILE // 2        # the funnel ladder, deck 12 to the roof
ROOF_Y = ROOF_ROW * TILE


def check(cond, label, detail=""):
    print(("  ok    " if cond else "  FAIL  ") + label + (f"  ({detail})" if detail else ""))
    return cond


def scenario_boot(b):
    b.open("?reset")
    b.shot("title")
    b.tap("enter")
    b.wait_for("window.__ship && window.__ship.player")
    time.sleep(0.5)
    s = b.state()
    b.shot("spawn")
    return check(s["mode"] == "play" and s["y"] == D4 and abs(s["x"] - SPAWN_X) < 4,
                 "spawns standing on deck 4 at the gangway", s)


def scenario_run_jump(b):
    b.open("?reset&play")
    time.sleep(0.4)
    x0 = b.state()["x"]
    b.hold("right", 0.6)
    s = b.state()
    ok = check(s["x"] > x0 + 30, "runs right", f"{x0} -> {s['x']}")
    b.key("space", True)
    time.sleep(0.25)
    peak = b.state()["y"]
    b.key("space", False)
    time.sleep(0.8)
    ok &= check(peak < D4 - 30, "jumps", f"y at 0.25s {peak}")
    ok &= check(b.state()["y"] == D4, "lands back on deck 4", b.state())
    return ok


def scenario_stairs(b):
    b.open("?reset&play")
    b.teleport(CORE_L, D4)
    b.hold("up", 1.4)
    b.shot("stairs-climbing")
    b.key("up", True)
    time.sleep(3.0)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == D5, "holding up climbs to deck 5", s)
    locked = b.eval("window.__ship.alert.visible && window.__ship.alert.text")
    b.shot("stairs-locked")
    b.key("up", False)
    ok &= check(bool(locked) and "SEARCH" in locked, "and stops there: the flight up is roped off", locked)
    b.hold("down", 3.0)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D4, "holding down carries her back to deck 4", s)
    b.open("?reset&play&cards=all")
    b.teleport(CORE_L, D4)
    # (Held until she is there: the climb takes about nine seconds, a little more on a slow machine.)
    b.key("up", True)
    end = time.time() + 14
    while time.time() < end and b.state()["y"] > floor_y(8):
        time.sleep(0.05)
    b.key("up", False)
    s = b.state()
    ok &= check(s["y"] <= floor_y(8), "with every card she climbs on past deck 6", s)
    return ok


def scenario_ladder(b):
    b.open("?reset&play")
    b.teleport(LADDER_X, D12)
    b.hold("up", 0.6)
    b.shot("ladder-climbing")
    b.hold("up", 2.0)
    s = b.state()
    ok = check(s["y"] == ROOF_Y and s["mode"] == "play", "climbs the funnel ladder onto the roof", s)
    b.hold("down", 0.3)
    b.shot("ladder-top")
    b.hold("down", 2.2)
    s = b.state()
    ok &= check(s["y"] == D12, "climbs back down to deck 12", s)
    b.teleport(LADDER_X, ROOF_Y)
    b.hold("right", 0.4)
    s = b.state()
    ok &= check(s["y"] == ROOF_Y, "walks off the ladder top without falling through", s)
    return ok


def trunk_x(name):
    return next(x_of(m) for n, m, _, _ in TRUNKS if n == name)


def trunk_door(b, name, deck, field="open"):
    """A trunk door's state: `open`, or the texture of its `up` / `down` arrow lamp."""
    door = f"window.__ship.trunks.find(t => t.id === 'trunk-{name}').doors.find(d => d.y === {floor_y(deck)})"
    return b.eval(f"{door}.open" if field == "open" else f"{door}.{field}.texture.key")


def scenario_trunk(b):
    b.open("?reset&play")
    x = trunk_x("fwd-cabins")
    b.teleport(x, D4)
    b.hold("up", 0.5)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == D4, "a shut trunk door doesn't take ↑", s)
    b.tap("e")
    time.sleep(0.1)
    ok &= check(trunk_door(b, "fwd-cabins", 4), "E opens it")
    b.shot("trunk-open")
    b.hold("up", 0.4)
    b.shot("trunk-entering")
    b.hold("up", 2.0)
    s = b.state()
    ok &= check(s["mode"] == "trunk" and s["y"] == D5, "climbs the shaft up to deck 5", s)
    ok &= check(not trunk_door(b, "fwd-cabins", 4), "the deck 4 door shut behind her")
    ok &= check(trunk_door(b, "fwd-cabins", 5), "and the deck 5 door opened as she reached it")
    b.shot("trunk-arrived")
    b.hold("right", 0.5)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D5 and s["x"] > x + 20, "steps out onto deck 5", s)
    ok &= check(not trunk_door(b, "fwd-cabins", 5), "and that door shuts once she is away")

    # Three decks: letting go just short of the middle door settles her level with it. (The midships
    # trunk wants the Deck card, §6.1.5.)
    x = trunk_x("midships")
    b.eval("window.__ship.save.cards.push('deck')")
    b.teleport(x, D4)
    b.tap("e")
    b.hold("up", 1.7)
    time.sleep(0.5)
    s = b.state()
    ok &= check(s["mode"] == "trunk" and s["y"] == D5, "settles at the middle door, deck 5", s)
    ok &= check(trunk_door(b, "midships", 5, "up") == "arrow-up-on"
                and trunk_door(b, "midships", 5, "down") == "arrow-down-on", "whose arrows show both ways")
    b.key("left", True)
    time.sleep(0.1)
    b.shot("trunk-stepping-out")
    time.sleep(0.3)
    b.key("left", False)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D5 and s["x"] < x - 20, "steps out there", s)

    # Climbing on past a door: it opens as she reaches it and shuts again once she has gone by.
    b.teleport(x, D4)
    b.tap("e")
    b.key("up", True)
    time.sleep(1.85)
    passing = trunk_door(b, "midships", 5)
    time.sleep(2.0)
    b.key("up", False)
    s = b.state()
    ok &= check(passing and not trunk_door(b, "midships", 5) and trunk_door(b, "midships", 6)
                and s["mode"] == "trunk" and s["y"] == D6,
                "the deck 5 door opens and shuts as she climbs past it to deck 6", s)

    # One-way: shut from below until she has come down through it.
    x = trunk_x("theatre")
    b.teleport(x, D4)
    b.tap("e")
    time.sleep(0.1)
    ok &= check(not trunk_door(b, "theatre", 4) and trunk_door(b, "theatre", 4, "up") == "arrow-up",
                "the one-way trunk won't open from below", trunk_door(b, "theatre", 4, "up"))
    b.teleport(x, D6)
    b.tap("e")
    b.hold("down", 4.2)
    s = b.state()
    ok &= check(s["mode"] == "trunk" and s["y"] == D4, "comes down it from deck 6, past deck 5", s)
    b.hold("right", 0.4)
    ok &= check(trunk_door(b, "theatre", 4, "up") == "arrow-up-on", "and from then on it opens from below too")
    b.teleport(x, D4)
    b.tap("e")
    time.sleep(0.1)
    ok &= check(trunk_door(b, "theatre", 4), "it does")

    # Card-locked.
    b.teleport(trunk_x("magnums"), D6)
    b.tap("e")
    time.sleep(0.1)
    locked = b.eval("window.__ship.alert.visible && window.__ship.alert.text")
    b.shot("trunk-locked")
    ok &= check(not trunk_door(b, "magnums", 6) and bool(locked) and "Entertainment" in locked,
                "a card-locked trunk asks for the Entertainment card", locked)
    return ok


LIFT_X = col(CORES["forward"][0]) * TILE + 18 * TILE     # the forward core's elevator
GLASS_X = x_of(sum(ATRIUM["span"]) / 2)             # the atrium's glass elevator


def lift_cursor(b):
    return b.eval("window.__ship.liftRun && window.__ship.liftRun.lift.floors[window.__ship.liftRun.cursor].deck")


def scenario_lift(b):
    b.open("?reset&play")
    b.teleport(LIFT_X, D4)
    b.tap("e")
    time.sleep(0.5)
    ok = check(b.state()["mode"] == "lift" and b.eval("!!window.__ship.liftPanel"), "E opens the doors and shows the panel")
    for _ in range(4):
        b.tap("up")
        time.sleep(0.1)  # separate presses, not one long one
    ok &= check(lift_cursor(b) == 5, "in region 1, ↑ picks no higher than deck 5", lift_cursor(b))
    b.shot("lift-panel")
    b.tap("e")
    time.sleep(0.1)
    ok &= check(not b.eval("window.__ship.liftPanel"), "the panel goes once the deck is chosen")
    time.sleep(0.8)
    b.shot("lift-riding")
    time.sleep(1.8)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D5 and abs(s["x"] - LIFT_X) < 2, "E rides it up to deck 5", s)
    b.shot("lift-arrived")
    b.hold("right", 0.5)
    time.sleep(0.4)
    ok &= check(b.eval("window.__ship.lifts[0].floors.every(f => f.leaves.open === 0)"), "the doors shut once she steps away")

    # Called from deck 4 while it waits on deck 5, the car comes down to her: she stays put.
    b.teleport(LIFT_X, D4)
    b.tap("e")
    ys = []
    for _ in range(12):
        time.sleep(0.15)
        ys.append(b.state()["y"])
    ok &= check(set(ys) == {D4} and b.eval("window.__ship.liftRun.choosing"),
                "called from another deck, the car comes to her and she stays put", sorted(set(ys)))
    b.tap("left")
    time.sleep(0.6)

    b.teleport(LIFT_X, D5)
    b.tap("e")
    b.wait_for("window.__ship.liftRun && window.__ship.liftRun.choosing", timeout=4)  # it comes up first
    b.tap("left")
    time.sleep(0.1)
    ok &= check(b.state()["mode"] == "play" and not b.eval("window.__ship.liftPanel"), "←/→ backs out of the panel")

    # The glass elevator: on deck 5 to start with, it comes up to fetch her on deck 7.
    b.open("?reset&play&cards=all")
    b.teleport(GLASS_X, walk_y(7))
    b.tap("e")
    time.sleep(0.6)
    b.shot("glass-coming")
    time.sleep(1.6)
    ok &= check(b.eval("window.__ship.liftRun.choosing && window.__ship.lifts.find(l => l.glass).carY") == walk_y(7),
                "the glass car comes up to her deck")
    for _ in range(2):
        b.tap("up")
        time.sleep(0.1)
    ok &= check(lift_cursor(b) == 9, "with every card she can pick deck 9", lift_cursor(b))
    b.tap("e")
    time.sleep(1.2)
    b.shot("glass-riding")
    time.sleep(1.8)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == walk_y(9), "and rides it to deck 9", s)
    return ok


ATRIUM_X0 = col(ATRIUM["span"][0]) * TILE                 # where the atrium opens
ATRIUM_X1 = col(ATRIUM["span"][1]) * TILE


def scenario_atrium(b):
    b.open("?reset&play&cards=all")
    # The side walks are floor: she runs straight across the atrium, through the doors at its ends
    # (E opens each: a wall with a door between every two parts of the ship, 2026-11-07).
    b.teleport(ATRIUM_X0 - 20, D7)
    b.tap("e")
    time.sleep(0.3)
    b.hold("right", 7.4)
    b.tap("e")
    time.sleep(0.3)
    b.hold("right", 0.8)
    s = b.state()
    ok = check(s["y"] == D7 and s["x"] > ATRIUM_X1, "she runs straight across the atrium on deck 7", s)

    # The curving staircase, from the atrium floor up to deck 6 and back down.
    flight = b.eval("window.__ship.flights.find(f => f.name === 'stairs-atrium-5-6').bottom")
    b.teleport(flight["x"], floor_y(5))
    b.eval("""(() => { const s = window.__ship, leave = s.leaveLadderOrStairs.bind(s); window.__landed = null;
        s.leaveLadderOrStairs = () => { leave(); window.__landed = window.__landed || { y: s.player.y }; };
    })()""")
    b.hold("up", 3.2)
    landed = b.eval("window.__landed")
    ok &= check(landed and landed["y"] == D6, "the curving staircase climbs to deck 6", landed)
    top = b.eval("window.__ship.flights.find(f => f.name === 'stairs-atrium-5-6').top")
    b.teleport(top["x"], D6)
    b.hold("down", 3.2)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == floor_y(5), "and back down to the atrium floor", s)
    return ok


def scenario_pool(b):
    b.open("?reset&play&cards=all")
    b.eval("window.__ship.cats.forEach(c => { c.gone = true; })")      # Bumbot's beat at the rim is not this test's
    a, z = POOLS[0]
    # Deck 12's side walk over the pool area: along it, and down through it with ↓.
    b.teleport(col(POOL_OPENING[0]) * TILE - 16, D12)
    b.hold("right", (x_of((a + z) / 2) - col(POOL_OPENING[0]) * TILE + 16) / 140)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == D12, "deck 12's side walk is floor over the pools", s)
    b.tap("down")
    time.sleep(1.0)
    s = b.state()
    ok &= check(s["mode"] == "swim", "↓ drops her from it into the pool below", s)
    b.shot("pool-swimming")
    x0 = s["x"]
    b.hold("right", 1.0)
    s = b.state()
    ok &= check(s["mode"] == "swim" and s["x"] > x0 + 40, "she swims breaststroke", s)
    b.hold("right", 8.0)
    b.key("right", True)
    b.tap("space")
    time.sleep(0.4)
    b.key("right", False)
    time.sleep(0.8)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D11 and col(z) * TILE < s["x"] < col(POOLS[1][0]) * TILE,
                "jump climbs her out at the edge", s)
    # Walking off the deck's edge into the water.
    b.teleport(col(a) * TILE - 40, D11)
    b.hold("right", 0.8)
    ok &= check(b.state()["mode"] == "swim", "she can walk straight into a pool too", b.state())
    return ok


def scenario_promenade(b):
    # Deck 6's two routes (§5.3): E at a door crosses between the rooms and the promenade; the
    # promenade's ends are closed.
    door = x_of(PROMENADE["doors"][1])
    route = lambda: b.eval("window.__ship.route")
    b.open("?reset&play&at=promenade")
    ok = check(route() == "promenade", "?at=promenade starts her on the promenade", route())
    b.eval(f"window.__ship.spawnAt({{x: {door + 8}, y: {floor_y(6)}, route: 'promenade'}})")
    b.tap("e")
    time.sleep(0.8)
    s = b.state()
    ok &= check(route() == "inside" and s["mode"] == "play" and s["x"] == door, "E at a door takes her inside", (route(), s))
    b.shot("promenade-inside")
    b.tap("e")
    time.sleep(0.8)
    ok &= check(route() == "promenade", "and E again back out", route())
    b.eval(f"window.__ship.spawnAt({{x: {x_of(PROMENADE['span'][0]) + 120}, y: {floor_y(6)}, route: 'promenade'}})")
    b.hold(["left"], 1.5)
    s = b.state()
    ok &= check(route() == "promenade" and s["x"] >= x_of(PROMENADE["span"][0]) and s["y"] == floor_y(6),
                "its fore end is closed", (route(), s))
    b.shot("promenade-fore")
    return ok


def scenario_cabin(b):
    # Cabin 8206 on deck 8 (§5.3): E at its open door takes her in; its walls hold her; E again
    # takes her back out to the corridor.
    route = lambda: b.eval("window.__ship.route")
    b.open("?reset&play&at=cabin")
    door = b.eval("window.__ship.cabin.door")
    s = b.state()
    ok = check(route() == "cabin" and s["x"] == door and s["y"] == floor_y(8), "?at=cabin starts her inside, by its door", (route(), s))
    b.eval("window.__ship.route = 'inside'")
    b.teleport(door + 6, floor_y(8))
    b.tap("e")
    time.sleep(0.8)
    s = b.state()
    ok &= check(route() == "cabin" and s["mode"] == "play" and s["x"] == door, "E at the open door takes her in", (route(), s))
    b.shot("cabin-desk")
    b.hold(["right"], 0.6)
    time.sleep(0.3)
    b.hold(["right"], 2.0)
    s = b.state()
    ok &= check(route() == "cabin" and door < s["x"] < door + 200 and s["y"] == floor_y(8), "the cabin's far wall holds her", s)
    b.shot("cabin-inside")
    b.hold(["left"], 2.0)
    s = b.state()
    ok &= check(door - 60 < s["x"] < door and s["y"] == floor_y(8), "and so does its near wall", s)
    # She can jump onto the bed (its top 32px over the floor) and stand there.
    b.eval(f"window.__ship.spawnAt({{x: {door + 50}, y: {floor_y(8)}, route: 'cabin'}})")
    time.sleep(0.4)
    b.key("right", True)
    b.tap("space")
    time.sleep(0.5)
    b.key("right", False)
    time.sleep(0.8)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == floor_y(8) - 32, "she jumps onto the bed and stands on it", s)
    b.shot("cabin-bed")
    # Standing still on it a second, she bounces for joy; any key and she stops, still on the bed.
    time.sleep(1.4)
    ys = []
    for _ in range(12):
        ys.append(b.state()["y"])
        time.sleep(0.05)
    ok &= check(b.state()["mode"] == "scripted" and min(ys) < floor_y(8) - 32 - 3 and max(ys) == floor_y(8) - 32,
                "a second still on the bed: she bounces for joy, off it and back", ys)
    b.shot("cabin-bed-joy")
    b.tap("left")
    time.sleep(0.5)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == floor_y(8) - 32, "a key stops it, her feet on the bed", s)
    b.teleport(door, floor_y(8))
    b.eval("window.__ship.route = 'cabin'")
    b.tap("e")
    time.sleep(0.8)
    ok &= check(route() == "inside", "E at the door takes her back out", route())
    b.shot("cabin-door")
    return ok


def scenario_linen(b):
    # The linen room on deck 9 (§5.3): E at its crew door takes her in, its walls hold her, E again
    # takes her back out. (Bumbot's checks went with his spots, 2026-11-07: they come back with him.)
    route = lambda: b.eval("window.__ship.route")
    b.open("?reset&play&at=linen&cards=all")      # its crew door is green (§6.1.5)
    door = b.eval("window.__ship.rooms.find(r => r.route === 'linen').door")
    b.eval("window.__ship.route = 'inside'")
    b.teleport(door + 6, floor_y(9))
    b.tap("e")
    time.sleep(0.8)
    s = b.state()
    ok = check(route() == "linen" and s["x"] == door, "E at the crew door takes her in", (route(), s))
    b.shot("linen-inside")
    b.hold(["left"], 2.0)
    s = b.state()
    ok &= check(door - 60 < s["x"] < door and s["y"] == floor_y(9), "the room's near wall holds her", s)
    b.teleport(door, floor_y(9))
    b.eval("window.__ship.route = 'linen'")
    b.tap("e")
    time.sleep(0.8)
    ok &= check(route() == "inside", "E at the door takes her back out", route())
    return ok


def scenario_bridge(b):
    # The bridge on deck 10 (§5.3): its shut crew door stops her; E opens it; its piece of the ship's
    # side is cut open with the deck's, from either side (LOCKED_PARTS is off for now).
    shell = lambda key: b.eval(f"window.__ship.shellAlpha['{key}']")
    b.open("?reset&play&cards=all")      # its door is gold (§6.1.5)
    bridge = "window.__ship.bulkheads.find(b => b.key === '10:bridge')"
    door = b.eval(f"{bridge}.x")
    b.teleport(door + 60, floor_y(10))
    time.sleep(2.5)    # the cut-away fades over from deck 4
    ok = check(shell("10") < 0.05 and shell("10:bridge") < 0.05, "from the corridor the bridge is in sight",
               (shell("10"), shell("10:bridge")))
    b.hold("left", 0.8)
    s = b.state()
    ok &= check(s["x"] > door, "the shut door stops her", s)
    b.tap("e")
    time.sleep(0.2)
    ok &= check(b.eval(f"{bridge}.open"), "E opens it")
    # Well past the shutting distance (0.6 s left her right at it, and the door open: 2026-11-07).
    b.hold("left", 0.9)
    time.sleep(1.0)
    s = b.state()
    ok &= check(s["x"] < door and shell("10:bridge") < 0.05 and shell("10") < 0.05,
                "on the bridge the deck is cut open too", (s, shell("10"), shell("10:bridge")))
    ok &= check(not b.eval(f"{bridge}.open"), "the door shuts behind her")
    return ok


def scenario_balcony(b):
    # The Stardust Lounge's balcony (deck 7) ends in a railing over the stage: she can hop it and
    # drop one deck onto the stage, no scare (§5.3).
    b.open("?reset&play")
    b.teleport(x_of(STAGE - 1.4), floor_y(7))
    time.sleep(0.4)
    b.key("right", True)
    b.key("space", True)         # (held: a tap can come out as a cut-short hop on a slow machine)
    time.sleep(0.4)
    b.key("space", False)
    time.sleep(1.0)
    b.key("right", False)
    time.sleep(0.8)
    s = b.state()
    b.shot("balcony-hop")
    return check(s["mode"] == "play" and s["y"] == floor_y(6) and s["x"] > x_of(STAGE),
                 "she hops the balcony railing and lands on the stage", s)


def scenario_idle(b):
    b.open("?reset&play")
    b.wait_for("window.__ship && window.__ship.player")
    anim = "(window.__ship.player.anims.isPlaying ? window.__ship.player.anims.currentAnim.key : '')"
    # Timed by the game's own clock: a cold start's first frames are slow, so wall-clock seconds
    # after loading drift (the test failed on main too, 2026-11-11).
    ok = check(b.eval(anim) == "" and b.eval("window.__ship.idleAt - window.__ship.time.now") > 500,
               "stands plainly for the first few seconds")
    b.wait_for(f"{anim}.startsWith('her-idle-')", timeout=8)
    first = b.eval(anim)
    ok &= check(first.startswith("her-idle-"), "an idle plays after standing still", first)
    b.shot("idle")
    b.hold("right", 0.2)
    ok &= check(not b.eval(anim).startswith("her-idle-"), "moving ends the idle at once")
    b.wait_for(f"{anim}.startsWith('her-idle-')", timeout=20)
    second = b.eval(anim)
    ok &= check(second != first, "the next idle is a different one", f"{first} then {second}")
    # Climbing out at the top of the funnel ladder: her hands are on the rim, not reaching for rungs.
    b.teleport(LADDER_X, ROOF_Y)
    b.hold("down", 1.2)
    b.hold("up", 0.8)
    frame = b.eval("window.__ship.player.frame.name")
    out = b.eval("window.__ship.climbOutFrames")
    ok &= check(frame in out, "climbing out at a ladder top uses a climb-out frame", f"frame {frame}")
    b.shot("climb-out")
    return ok


def scenario_falls(b):
    b.open("?reset&play")
    b.eval("window.__ship.cats.forEach(c => { c.gone = true; })")      # (Bumbot at the pool's rim would stop her)
    # One deck: down through deck 12's walk onto deck 11's pool area, aft of the pools.
    b.teleport(x_of(143.5), D12)
    time.sleep(0.3)
    b.tap("down")
    time.sleep(1.2)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == D11, "a one-deck drop into the pool area is fine", s)
    # (Between the pools she comes down on the hot tub's canopy: a roof she can stand on.)
    b.teleport(x_of(132.5), D12)
    time.sleep(0.3)
    b.tap("down")
    time.sleep(1.2)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D11 - 90, "over the hot tub she lands on its canopy", s)
    # Two decks: off deck 12's aft end, past deck 11, onto the deck 10 terrace below.
    b.teleport(x_of(245.5), D12)  # past deck 12's (233 m) and deck 11's (244 m) aft ends
    time.sleep(0.6)
    b.shot("long-fall")
    s = b.state()
    ok &= check(s["mode"] == "scripted", "a two-deck fall is a scare", s)
    time.sleep(2.0)
    s = b.state()
    ok &= check(s["mode"] == "play", "she comes back afterwards", s)
    return ok


def scenario_vacuum(b):
    b.open("?reset&play")
    b.teleport(x_of(120), D4)  # the deck 4 corridor the robot vacuum patrols
    b.eval(f"window.__ship.vacuums[0].sprite.x = {x_of(120) + 40}; window.__ship.vacuums[0].dir = -1")
    time.sleep(0.8)
    b.shot("vacuum-scare")
    s = b.state()
    ok = check(s["mode"] == "scripted", "touching the vacuum is a scare", s)
    time.sleep(2.5)
    s = b.state()
    ok &= check(s["mode"] == "play", "she comes back afterwards", s)
    return ok


def scenario_dash(b):
    b.open("?reset&play")
    b.teleport(x_of(236) + 6, D4)  # behind the crate stack on deck 4
    time.sleep(0.3)
    b.eval("window.__ship.save.tangerines = 1; window.__ship.save.verbs.push('dash')")  # the dash is learned at near-catch 1
    b.eval(f"window.__ship.vacuums[0].sprite.x = {x_of(228)}; window.__ship.vacuums[0].speed = 0")
    b.tap("d")
    time.sleep(0.2)
    b.shot("dash-shout")
    s = b.state()
    ok = check(s["dashing"] and s["tangerines"] == 0, "D spends a tangerine on a dash", s)
    # Dash forward along deck 4, through the crates and into the vacuum.
    b.hold("left", 2.5)
    s = b.state()
    ok &= check(s["x"] < x_of(231), "the dash breaks through the crates", s)
    ok &= check(b.eval("window.__ship.vacuums[0].asideUntil > 0"), "and shoves the vacuum aside, spinning")
    return ok


def scenario_overboard(b):
    b.open("?reset&play")
    b.teleport((col(255) - 1) * TILE - 30, D6)  # deck 6's open aft terrace, just inside the railing
    b.key("right", True)
    time.sleep(0.4)  # up against the railing first: the terrace is only a metre deep
    b.key("space", True)
    time.sleep(0.5)
    b.key("space", False)
    time.sleep(0.6)
    b.key("right", False)
    b.wait_for("window.__ship.mode === 'scripted'", timeout=4)  # a long drop: the hull stands two decks above the sea
    time.sleep(0.6)
    b.shot("overboard")
    s = b.state()
    ok = check(s["mode"] == "scripted", "jumping the stern railing goes overboard", s)
    time.sleep(2.5)
    s = b.state()
    ok &= check(s["mode"] == "play", "she comes back afterwards", s)
    return ok


# --- The progression (§6.1, docs/build-plan.md step 0) --------------------------------------------
# `golden` walks the intended route through every lock built so far; `sweep` tries every lock from
# the wrong side. Both grow with each step of the build.

def save_list(b, name):
    return b.eval(f"window.__ship.save.{name}.slice()")


def go(b, deck, m, route="inside"):
    """Teleport, but only within a region she has already opened: the golden path never skips a lock."""
    n = region_at(deck, m, route)
    assert n in save_list(b, "regions"), f"golden: deck {deck} at {m} m is region {n}, not open yet"
    b.teleport(x_of(m), floor_y(deck))


def alert(b):
    return b.eval("window.__ship.alert.visible && window.__ship.alert.text") or ""


def flight_feet(name):
    """A core flight's foot and top as (x, y): `stairs-<core>-<d>-<d+1>`."""
    _, core, d, _ = name.split("-")
    d = int(d)
    left, right = col(CORES[core][0]) * TILE + 4 * TILE, col(CORES[core][0]) * TILE + 15 * TILE
    x0, x1 = (left, right) if d % 2 == 0 else (right, left)
    return (x0, floor_y(d)), (x1, floor_y(d + 1))


def climb(b, name, seconds=2.6):
    (x0, y0), _ = flight_feet(name)
    b.teleport(x0, y0)
    b.hold("up", seconds)
    return b.state()


def door_open(b, name):
    return b.eval(f"window.__ship.bulkheads.find(d => d.id === '{name}').open")


def use_door(b, deck, m, side):
    """E at a door in a wall across the deck, from the bow side (-1) or the stern side (1)."""
    b.teleport(exact_x(m) + side * 16, floor_y(deck))
    b.tap("e")
    time.sleep(0.15)
    return door_open(b, f"part-door-{deck}-{m:g}")


def take_card(b, card):
    deck, m, _ = CARD_SPOTS[card]
    go(b, deck, m)
    b.tap("e")
    time.sleep(0.2)
    return card in save_list(b, "cards")


def flags(b):
    return save_list(b, "flags")


def route(b):
    return b.eval("window.__ship.route")


def wait_flag(b, flag, timeout=12):
    """A scene sets its flag when it is over."""
    end = time.time() + timeout
    while time.time() < end:
        if flag in flags(b) and b.state()["mode"] == "play":
            return True
        time.sleep(0.2)
    return False


def room(b, name):
    return b.eval(f"(r => ({{ x0: r.def.x0, floor: r.floor, doors: r.doors }}))(window.__ship.world.rooms['{name}'])")


def hold_until(b, keys, cond, timeout=10):
    """Holds keys until `cond(state)`; the state it stopped at."""
    keys = [keys] if isinstance(keys, str) else keys
    for k in keys:
        b.key(k, True)
    end = time.time() + timeout
    s = b.state()
    while time.time() < end and not cond(s):
        time.sleep(0.05)
        s = b.state()
    for k in keys:
        b.key(k, False)
    return s


def scenario_golden(b):
    """The whole route, the gangway to the catch, every lock opened the intended way (step 0 of
    docs/build-plan.md): teleports only within regions she has opened, the mechanics with real keys."""
    b.open("?reset&play")
    ok = check(save_list(b, "regions") == [1] and save_list(b, "cards") == [], "starts in region 1 with no cards",
               save_list(b, "regions"))
    # Region 1: the guest stairs up are roped off; the crew trunk wants the Deck card.
    s = climb(b, "stairs-forward-5-6", 0.6)
    ok &= check(s["y"] == D5 and "SEARCH" in alert(b), "the forward stairs 5-6 are roped off for the search", alert(b))
    go(b, 4, 125)
    b.tap("e")
    time.sleep(0.15)
    ok &= check("Deck" in alert(b), "the midships crew trunk wants the Deck card", alert(b))
    # Near-catch 1 at the Seven Seas: the scream, and the dash is hers.
    b.tap("d")
    ok &= check(not b.state()["dashing"], "no dash before she has seen him")
    go(b, 5, 244)
    b.hold("right", 1.6)
    ok &= check(wait_flag(b, "bb1"), "near-catch 1 at the Seven Seas' pass", flags(b))
    ok &= check("dash" in save_list(b, "verbs"), "the dash is learned there", save_list(b, "verbs"))
    ok &= check(lunch_for_the_officer(b), "his lunch carried to the gangway officer: the Deck card")
    # Region 2: up the crew trunk into Bliss.
    go(b, 4, 125)
    b.tap("e")
    b.hold("up", 5.0)
    b.hold("right", 0.6)
    ok &= check(2 in save_list(b, "regions"), "with it, up the trunk to deck 6: region 2 opens", b.state())
    s = climb(b, "stairs-forward-5-6", 2.6)
    ok &= check(s["mode"] == "stairs", "and the forward stairs' rope is gone", s)
    # The Library's aft door stays shut until Bumbot bolts through it (near-catch 2).
    shut = not use_door(b, 6, 194, -1)
    ok &= check(shut and "QUIET" in alert(b), "the Library's aft door is roped off", alert(b))
    go(b, 6, 177)
    b.hold("right", 1.5)
    ok &= check(wait_flag(b, "bb2"), "near-catch 2 at the reading table", flags(b))
    ok &= check(use_door(b, 6, 194, -1), "then the aft door opens")
    b.hold("right", 1.2)
    ok &= check(3 in save_list(b, "regions"), "region 3 beyond it", b.state())
    # Region 3: the stage, near-catch 3; the card; the trunk from Bliss up to deck 9.
    go(b, 6, 246.9)
    b.hold("right", 0.5)
    ok &= check(wait_flag(b, "bb3", 16), "near-catch 3 on the stage", flags(b))
    ok &= check(pills_for_the_stage_manager(b), "his pills from his cabin on deck 4: the Entertainment card")
    go(b, 6, 118)
    b.tap("e")
    b.hold("up", 7.5)
    s = b.state()
    ok &= check(s["mode"] == "trunk" and s["y"] == D9, "the red trunk from Bliss climbs to deck 9", s)
    b.hold("right", 0.6)
    ok &= check(4 in save_list(b, "regions"), "region 4: deck 9's corridor", b.state())
    # Region 4: the steward's cart fills the corridor until she pushes it free.
    b.hold("right", 1.6)
    s = b.state()
    ok &= check(s["x"] < exact_x(122.6), "the steward's cart blocks the corridor", s)
    b.hold(["right", "space"], 0.7)
    ok &= check(b.state()["x"] < exact_x(122.6), "and can't be hopped where it is jammed", b.state())
    time.sleep(0.5)
    b.hold("right", 0.3)
    linen = b.eval("window.__ship.rooms.find(r => r.route === 'linen').door")
    back = b.state()["x"]
    b.teleport(linen, D9)
    b.tap("e")
    time.sleep(0.15)
    ok &= check("Housekeeping" in alert(b) and route(b) == "inside", "the linen room's crew door wants the Housekeeping card", alert(b))
    time.sleep(0.5)
    b.teleport(back - 6, D9)
    b.hold("right", 0.3)
    b.tap("e")
    b.hold("right", 6.6)
    ok &= check("cart_free" in flags(b), "pushed along to 130 m, it is free", b.state())
    end = time.time() + 12
    while time.time() < end and not ("hk" in save_list(b, "cards") and b.state()["mode"] == "play"):
        time.sleep(0.2)
    ok &= check("hk" in save_list(b, "cards"), "the steward's thanks: the Housekeeping card", save_list(b, "cards"))
    b.hold(["right", "space"], 0.7)
    b.hold("right", 0.4)
    ok &= check(b.state()["x"] > exact_x(130), "and she hops the cart there", b.state())
    b.teleport(linen, D9)
    b.tap("e")
    time.sleep(0.8)
    ok &= check(route(b) == "linen", "with it, into the linen room")
    # Near-catch 4 in the towels; crawling is learned; the laundry cart under the vent, the duct,
    # the drop into deck 8.
    b.hold("right", 0.9)
    ok &= check(wait_flag(b, "bb4"), "near-catch 4 in the towel heap: he is gone into the vent", flags(b))
    ok &= check("crawl" in save_list(b, "verbs"), "crawling is learned there")
    lc = "window.__ship.world.pushables.find(t => t.id === 'cart_linen')"
    b.teleport(b.eval(f"{lc}.x") - 32, D9, "linen")
    time.sleep(0.2)
    b.tap("e")
    ok &= check(b.state()["mode"] == "push", "E at the laundry cart's end: she takes hold", b.state())
    b.hold("right", 2.8)
    ok &= check("cart_linen" in flags(b), "the laundry cart pushed under the vent", b.state())
    b.hold(["right", "space"], 0.45)
    time.sleep(0.5)
    b.hold("down", 0.5)
    time.sleep(0.9)
    ok &= check(route(b) == "duct", "from the cart's top, down on hands and knees: the duct", b.state())
    b.hold("left", 13.6)
    b.tap("down")
    time.sleep(1.6)
    s = b.state()
    ok &= check(route(b) == "inside" and s["y"] == D8 and 5 in save_list(b, "regions"),
                "out of its far grille, down into deck 8 forward: region 5", s)
    # Region 5: the lobby door opens from inside; the forward stairs go on up to deck 11.
    ok &= check(use_door(b, 8, 74, -1), "deck 8's lobby door opens from the corridor")
    (x0, y0), _ = flight_feet("stairs-forward-8-9")
    b.teleport(x0, y0)
    b.hold("up", 9.5)
    s = b.state()
    ok &= check(s["y"] == D11 and 6 in save_list(b, "regions"), "up the forward stairs to deck 11: region 6", s)
    # Region 6: the socks; near-catch 5 drains the pool; the hatch into deck 10.
    go(b, 11, 95.75)
    b.tap("e")
    time.sleep(0.2)
    ok &= check("socks" in save_list(b, "verbs"), "the grip socks, in the gym")
    go(b, 11, 126)
    time.sleep(0.8)
    ok &= check(b.state()["mode"] == "swim", "the first pool: she swims", b.state())
    hold_until(b, "right", lambda s: s["mode"] == "scripted", 8)
    ok &= check(wait_flag(b, "bb5", 16), "near-catch 5, from the water at the pool's rim", flags(b))
    ok &= check("drain" in flags(b), "and the pool drains")
    s = hold_until(b, [], lambda s: s["mode"] == "play" and s["y"] == D11 + 32, 8)
    ok &= check(s["mode"] == "play" and s["y"] == D11 + 32, "she is left standing in the empty tank", s)
    b.teleport(x_of(125), D11 + 32)
    time.sleep(0.3)
    b.tap("e")
    time.sleep(1.6)
    s = b.state()
    ok &= check(s["y"] == D10, "the hatch in its floor drops her into deck 10's hallway", s)
    # Region 8: with the socks, up the sun cover's post at the Great Outdoors, along it to deck 12.
    b.teleport(exact_x(233) + 13, D11)
    b.key("space", True)
    time.sleep(0.34)
    b.key("space", False)
    time.sleep(0.02)
    b.key("left", True)
    b.key("space", True)
    time.sleep(0.2)
    b.key("space", False)
    time.sleep(1.0)
    b.key("left", False)
    s = b.state()
    ok &= check(s["y"] < D11 - 100, "a wall jump up the post lands her on the sun cover", s)
    b.hold("left", 3.4)
    b.hold(["left", "space"], 0.8)
    b.hold("left", 0.5)
    s = b.state()
    ok &= check(s["y"] == D12 and 8 in save_list(b, "regions"), "along the cover and over the rail: deck 12, region 8", s)
    # The funnel: the ladder to the roof, the stairway, the top, the horn.
    b.teleport(LADDER_X, D12)
    b.hold("up", 3.0)
    b.hold("right", 0.5)
    b.hold("up", 8.6)
    s = b.state()
    top = b.eval("window.__ship.world.data.funnel.y")
    ok &= check(s["mode"] == "play" and s["y"] == top, "up the funnel's stairway to its top", s)
    b.teleport(exact_x(186) - 6, top)
    b.tap("e")
    time.sleep(0.3)
    ok &= check("horn" in flags(b), "the horn", flags(b))
    ok &= check(take_card(b, "off"), "the Officer's card, dropped on the sun deck")
    go(b, 12, 130)
    b.tap("e")
    time.sleep(0.2)
    ok &= check("parasol" in save_list(b, "verbs"), "and the parasol, at the empty sunbed")
    # Region 9: the cake clears the forward lobby; down the bow with the gold card to the bridge.
    ok &= check(not use_door(b, 12, 82, 1), "Champs' door to the forward lobby is still shut: the wedding", alert(b))
    go(b, 12, 84)
    b.tap("e")
    time.sleep(0.2)
    ok &= check("wedding" in flags(b) and use_door(b, 12, 82, 1), "the cake delivered, it opens")
    b.hold("left", 1.0)
    ok &= check(9 in save_list(b, "regions"), "region 9: deck 12's forward lobby", b.state())
    _, (x1, y1) = flight_feet("stairs-forward-11-12")
    b.teleport(x1, y1)
    b.hold("down", 1.0)
    ok &= check(b.state()["mode"] == "stairs", "the forward stairs down from deck 12 are clear of the party", b.state())
    go(b, 10, 78)
    ok &= check(use_door(b, 10, 74, 1), "the gold card opens the officers' corridor")
    b.hold("left", 0.8)
    b.teleport(exact_x(40) + 16, D10)
    b.tap("e")
    time.sleep(0.2)
    ok &= check(door_open(b, "bridge-door"), "and the bridge's door")
    b.hold("left", 3.0)
    ok &= check(wait_flag(b, "bb6"), "near-catch 6 on the bridge", flags(b))
    ok &= check("alarm" in flags(b), "the alarm")
    # Region 10: the hatch, the glide down to the bow, the catch.
    hatch = b.eval("window.__ship.world.gates[0].x")
    b.teleport(hatch, D10)
    b.hold("up", 3.4)
    b.hold("left", 0.3)
    s = b.state()
    ok &= check(s["y"] == D11 and 10 in save_list(b, "regions"), "up the hatch's ladder to the balcony forward of the spa", s)
    b.hold("left", 1.6)          # to the front rail
    b.key("left", True)
    b.key("space", True)         # over it, and the parasol opens as she falls
    time.sleep(2.4)
    b.key("left", False)
    s = hold_until(b, [], lambda s: s["y"] >= D7 or s["mode"] != "play", 14)
    b.key("space", False)
    time.sleep(0.5)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D7 and s["x"] < x_of(21), "the parasol carries her down to the mooring deck", s)
    b.shot("golden-bow")
    b.hold("left", 6.0)
    time.sleep(3.6)
    ok &= check("catch" in flags(b), "at the tip of the bow, standing still: the catch", (b.state(), flags(b)))
    b.shot("golden-end")
    return ok


def carrying(b):
    return b.eval("window.__ship.world.carry && window.__ship.world.carry.kind")


def person(b, pid):
    return b.eval(f"(p => p && ({{ x: Math.round(p.x), on: p.on, state: p.state, aside: !!p.aside }}))(window.__ship.world.people.byId['{pid}'])")


def take_lunch(b):
    """A tray of lunch from the Seven Seas' pass."""
    b.teleport(exact_x(248.8) - 12, D5)
    b.tap("e")
    time.sleep(0.2)
    return carrying(b) == "lunch"


def scenario_region1(b):
    """Region 1 (docs/build-plan.md, step 1): the officer's lunch past the waiter, his card, the
    porter, the luggage, the rival at his rope."""
    b.open("?reset&play")
    ok = check(person(b, "npc_officer")["on"] and b.eval("window.__ship.world.people.byId.npc_officer.bubbleItems[0].visible"),
               "the gangway officer shows what he wants: a tray")
    # The Seven Seas' pass has no tray to take until Bumbot has been at it.
    b.teleport(exact_x(248.8) - 70, D5)
    ok &= check(not take_lunch(b), "no lunch at the pass before the beat")
    b.open("?reset&play")
    go(b, 5, 244)
    b.hold("right", 1.6)
    ok &= check(wait_flag(b, "bb1"), "near-catch 1: he bolts from the pass")
    ok &= check(b.eval("window.__ship.tangerines.filter(t => t.id.startsWith('tan_5_bowl') && t.sprite.active).length") == 3,
                "three tangerines from the fruit bowl he knocked over")
    b.shot("region1-pass")
    ok &= check(take_lunch(b), "a tray of lunch from the pass")
    # Tray rules: a low hop, no trunk, no dash; the waiter spills it.
    b.hold("space", 0.5)
    top = b.eval("window.__ship.player.y")
    b.teleport(exact_x(240), D5)
    y0 = b.state()["y"]
    b.key("space", True)
    time.sleep(0.22)
    lifted = y0 - b.state()["y"]
    b.key("space", False)
    time.sleep(0.5)
    ok &= check(0 < lifted < 40 and carrying(b) == "lunch", "with a tray a jump is a low hop", lifted)
    b.eval("window.__ship.save.tangerines = 2")
    b.tap("d")
    ok &= check(not b.state()["dashing"], "and there is no dash")
    waiter = person(b, "haz_waiter")
    b.eval("(p => { p.pausedUntil = 0; p.aside = false; })(window.__ship.world.people.byId.haz_waiter)")
    b.teleport(person(b, "haz_waiter")["x"] + 60, D5)
    b.hold("left", 0.8)
    time.sleep(0.4)
    ok &= check(carrying(b) is None and b.state()["mode"] == "play", "the waiter bumps the tray out of her hands: a spill, no scare", b.state())
    b.shot("region1-spill")
    # At a table he is out of the aisle: she slips past behind him.
    ok &= check(take_lunch(b), "the pass has another")
    b.teleport(person(b, "haz_waiter")["x"] + 300, D5)       # (people only move near her)
    b.eval("(p => { p.x = p.walk.stops[0] - 4; p.dir = 1; p.pausedUntil = 0; })(window.__ship.world.people.byId.haz_waiter)")
    time.sleep(0.4)
    ok &= check(person(b, "haz_waiter")["aside"], "the waiter turns to a table", person(b, "haz_waiter"))
    b.teleport(person(b, "haz_waiter")["x"] + 50, D5)
    b.hold("left", 0.9)
    ok &= check(carrying(b) == "lunch", "and she passes him with the tray")
    # The glimpse at the forward stairs; the rival shakes his head at his rope.
    go(b, 5, 84)
    b.hold("left", 0.6)
    ok &= check("glimpse1" in flags(b), "a glimpse: his tail up the forward stairs", flags(b))
    s = climb(b, "stairs-forward-5-6", 0.5)
    ok &= check(s["y"] == D5 and person(b, "riv_rope")["state"] == "acting", "the security officer shakes his head at his rope",
                person(b, "riv_rope"))
    # Down the stairs with the tray, and to the officer.
    (x0, y0), _ = flight_feet("stairs-forward-4-5")
    _, (x1, y1) = flight_feet("stairs-forward-4-5")
    b.teleport(x1, y1)
    s = hold_until(b, "down", lambda s: s["y"] == D4 and s["mode"] == "play", 6)
    ok &= check(s["y"] == D4 and carrying(b) == "lunch", "stairs are fine with a tray", s)
    b.eval("(p => { p.x = p.walk.a; p.dir = -1; p.pausedUntil = window.__ship.time.now + 60000; })(window.__ship.world.people.byId.haz_porter)")
    b.teleport(exact_x(65.6) + 30, D4)
    b.tap("e")
    end = time.time() + 12
    while time.time() < end and "deck" not in save_list(b, "cards"):
        time.sleep(0.2)
    ok &= check("deck" in save_list(b, "cards") and carrying(b) is None, "he eats, and hands her the Deck card", save_list(b, "cards"))
    time.sleep(0.6)
    ok &= check(not b.eval("window.__ship.world.people.byId.npc_officer.bubbleItems[0].visible"), "his bubble is gone")
    b.shot("region1-card")
    # The porter's cart is a bump without a tray; hopped, it is nothing.
    b.eval("(p => { p.pausedUntil = 0; p.dir = 1; })(window.__ship.world.people.byId.haz_porter)")
    b.teleport(person(b, "haz_porter")["x"] + 90, D4)
    b.hold("left", 0.9)
    time.sleep(0.2)
    ok &= check(b.state()["mode"] == "scripted" and "Ой" in alert(b), "the porter's cart: bumped", alert(b))
    time.sleep(2.5)
    s = b.state()
    ok &= check(s["mode"] == "play" and abs(s["x"] - exact_x(72)) < 30, "and she steps out of the gangway's crew door", s)
    # The luggage stack: hopped, or broken by the dash.
    b.teleport(exact_x(30) + 60, D4)
    b.hold("left", 0.8)
    ok &= check(b.state()["x"] > exact_x(30), "the luggage stack is in the way", b.state())
    b.eval("window.__ship.save.tangerines = 1")
    b.tap("d")
    b.hold("left", 0.6)
    ok &= check("haz_luggage_4" in save_list(b, "broken"), "the dash goes through it", save_list(b, "broken"))
    # A standing cart is hopped.
    b.teleport(exact_x(90) + 50, D4)
    b.hold("left", 0.5)
    ok &= check(b.state()["x"] > exact_x(90), "a room-service cart stands in the way", b.state())
    b.hold(["left", "space"], 0.7)
    ok &= check(b.state()["x"] < exact_x(90), "and is hopped", b.state())
    # The way on: the crew trunk opens with his card; the guest stairs stay roped.
    s = climb(b, "stairs-midship-5-6", 0.5)
    ok &= check(s["y"] == D5 and "WET FLOOR" in alert(b), "the midship stairs: the cleaner's wet floor", alert(b))
    go(b, 4, 125)
    b.tap("e")
    b.hold("up", 5.0)
    b.hold("right", 0.6)
    ok &= check(2 in save_list(b, "regions"), "up the crew trunk with the Deck card: region 2", b.state())
    return ok


def lunch_for_the_officer(b):
    """The first errand, start to end (the golden path's): a tray from the pass, to the gangway, his card."""
    if not take_lunch(b):
        return False
    b.eval("(p => { p.x = p.walk.a; p.dir = -1; p.pausedUntil = window.__ship.time.now + 60000; })(window.__ship.world.people.byId.haz_porter)")
    b.teleport(exact_x(65.6) + 30, D4)
    b.tap("e")
    end = time.time() + 12
    while time.time() < end and "deck" not in save_list(b, "cards"):
        time.sleep(0.2)
    time.sleep(0.8)
    return "deck" in save_list(b, "cards")


def enter_region2(b):
    """A save at region 2's door: near-catch 1 done, the Deck card, region 2 opened (as the golden
    path leaves it), so a region's own playtest need not replay the one before."""
    b.open("?reset&play")
    b.eval("(P => { P.setFlag('bb1'); P.setFlag('lunch'); P.open('cards', 'deck'); P.open('regions', 2); })(window.__ship.progress)")
    b.eval("window.__ship.cats.filter(c => c.flag === 'bb1').forEach(c => { c.gone = true; c.away = true; c.sprite.setVisible(false); })")
    time.sleep(0.2)


def js(b, text):
    return b.eval(text)


def scenario_region2(b):
    """Region 2 (docs/build-plan.md, step 2): deck 6 from the bow to the Library, the promenade and
    the boat walkway's foothold, deck 7's lobbies: the robot, the flash, the jogger, the gulls, the
    glimpses, the lifeboat's book and photo, the books returned and read, near-catch 2 and the door
    it leaves ajar, the blocks on the ways up."""
    enter_region2(b)
    ok = True
    # The glass elevator: Bumbot rides up in it as she comes near, and it comes back empty.
    busy = "window.__ship.lifts.find(l => l.glass).busy"
    ok &= check(js(b, busy) is True, "the glass elevator waits at deck 6, taken")
    b.teleport(exact_x(97), D6)
    b.hold("left", 0.6)
    ok &= check(wait_flag(b, "bb_lift", 10) and js(b, busy) is False, "he rides up in it as she comes near; it comes back hers", flags(b))
    # The delivery robot: it waits while she is in its way, and carries her on its top.
    robot = "window.__ship.world.robots[0]"
    b.teleport(exact_x(34), D6)
    js(b, f"(r => {{ r.x = {exact_x(32)}; r.dir = 1; r.pausedUntil = 0; }})({robot})")
    time.sleep(0.5)
    x0 = js(b, f"{robot}.x")
    time.sleep(0.6)
    ok &= check(abs(js(b, f"{robot}.x") - x0) < 1 and js(b, f"{robot}.beep.visible") is not None, "the robot stops while she stands in its way", x0)
    b.shot("region2-robot")
    b.teleport(exact_x(31), D6)
    time.sleep(0.5)
    x1 = js(b, f"{robot}.x")
    ok &= check(x1 > x0 + 4, "and trundles on when she is behind it", (x0, x1))
    b.hold("right", 0.5)
    ok &= check(b.state()["x"] < js(b, f"{robot}.x"), "it is in the way like a cart", b.state())
    # Onto its top with a hop, and along with it to the tangerine on the hose cabinet.
    js(b, f"(r => {{ r.x = {exact_x(29.5)}; r.dir = -1; r.pausedUntil = 0; }})({robot})")
    top = js(b, f"{robot}.def.y - {robot}.h")
    b.teleport(js(b, f"{robot}.x"), top)
    time.sleep(0.3)
    xa = b.state()["x"]
    time.sleep(1.0)
    s = b.state()
    ok &= check(s["y"] == top and xa - s["x"] > 20, "she rides on its top", (xa, s))
    end = time.time() + 8
    while time.time() < end and b.state()["x"] > exact_x(26.94) + 6:
        time.sleep(0.05)
    b.tap("space")
    time.sleep(0.5)
    ok &= check("tan_6_high" in save_list(b, "collected"), "a hop from its top takes the tangerine on the fire-hose cabinet", b.state())
    # The cabin being made up: a peek.
    maid = room(b, "maid6")
    b.teleport(maid["doors"][0]["outX"], D6)
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "maid6" and person(b, "amb_maid")["on"], "the cabin being made up: in through its open door", route(b))
    b.shot("region2-cabin")
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "inside", "and out again", route(b))
    # Bliss: standing still on the dance floor, she dances.
    b.teleport(exact_x(117.2), D6)
    time.sleep(3.6)
    ok &= check(b.state()["mode"] == "scripted" and js(b, "window.__ship.player.anims.currentAnim.key") == "her-dance",
                "three seconds still on Bliss's dance floor: she dances", b.state())
    b.shot("region2-dance")
    time.sleep(3.4)
    ok &= check(b.state()["mode"] == "play", "and stops", b.state())
    # The Photo Studio's flash: caught in it she poses; no scare.
    b.teleport(exact_x(133.6), D6)
    end = time.time() + 9
    posed = False
    while time.time() < end and not posed:
        posed = b.state()["mode"] == "scripted"
        time.sleep(0.05)
    ok &= check(posed, "caught in the studio's flash she poses")
    b.shot("region2-flash")
    time.sleep(1.4)
    s = b.state()
    ok &= check(s["mode"] == "play" and abs(s["x"] - exact_x(133.6)) < 4, "and that is all: no scare", s)
    # The promenade: the jogger bumps her; standing aside (↑) lets him by.
    jog = "window.__ship.world.people.byId.haz_jogger"
    js(b, f"(p => {{ p.x = {exact_x(180)}; p.pausedUntil = window.__ship.time.now + 600000; }})({jog})")
    b.teleport(exact_x(150), D6, "promenade")
    b.key("up", True)
    time.sleep(0.2)
    js(b, f"(p => {{ p.x = {exact_x(153)}; p.dir = -1; p.pausedUntil = 0; }})({jog})")
    time.sleep(1.8)
    s = b.state()
    b.key("up", False)
    ok &= check(s["mode"] == "play" and person(b, "haz_jogger")["x"] < exact_x(150), "standing aside by the wall (↑), the jogger runs by", (s, person(b, "haz_jogger")))
    b.shot("region2-jogger")
    js(b, f"(p => {{ p.x = {exact_x(153)}; p.dir = -1; p.pausedUntil = 0; }})({jog})")
    time.sleep(1.6)
    ok &= check(b.state()["mode"] == "scripted" and "Ой" in alert(b), "in his lane, he bumps her", alert(b))
    time.sleep(2.6)
    ok &= check(b.state()["mode"] == "play", "a scare: she is back at a checkpoint", b.state())
    # He can be hopped.
    js(b, f"(p => {{ p.x = {exact_x(180)}; p.pausedUntil = window.__ship.time.now + 600000; }})({jog})")
    b.teleport(exact_x(150), D6, "promenade")
    js(b, f"(p => {{ p.x = {exact_x(152.2)}; p.dir = -1; p.pausedUntil = 0; }})({jog})")
    time.sleep(0.58)         # (standing still, the hop wants timing; running at him it is easy)
    b.hold("space", 0.8)
    ok &= check(b.state()["mode"] == "play" and person(b, "haz_jogger")["x"] < exact_x(150), "or hopped", (b.state(), person(b, "haz_jogger")))
    js(b, f"(p => {{ p.pausedUntil = window.__ship.time.now + 600000; }})({jog})")
    # The gulls on the rail fly up as she comes near, and settle again.
    gull = "window.__ship.world.movers.filter(m => m.rise !== undefined)[1]"
    b.teleport(exact_x(170), D6, "promenade")
    time.sleep(0.4)
    ok &= check(js(b, f"{gull}.rise") == 0, "a gull sits on the rail")
    # (On the way: two black ears in a porthole.)
    b.hold("right", 1.6)
    ok &= check("glimpse_window" in flags(b), "two black ears show in a porthole as she passes", flags(b))
    b.teleport(exact_x(174), D6, "promenade")
    time.sleep(0.7)
    ok &= check(js(b, f"{gull}.rise") > 0.5, "and flies up as she comes near", js(b, f"{gull}.rise"))
    b.shot("region2-gull")
    b.teleport(exact_x(185), D6, "promenade")
    time.sleep(3.2)
    ok &= check(js(b, f"{gull}.rise") == 0, "then settles again", js(b, f"{gull}.rise"))
    # The rival under the boats: he hurries off as she comes.
    ok &= check(person(b, "riv_prom")["on"], "the security officer peers under a boat on the promenade", person(b, "riv_prom"))
    b.teleport(exact_x(193.6), D6, "promenade")
    b.shot("region2-rival")
    ok &= check(wait_flag(b, "riv_prom", 6) and not person(b, "riv_prom")["on"], "and hurries off, in at a promenade door, as she comes near", flags(b))
    # The lifeboat station's gate and ladder (the Deck card), the locker, the lifeboat's inside.
    gate = js(b, "window.__ship.world.ladders[0]")
    b.teleport(gate["x"], gate["y0"], "promenade")
    s = hold_until(b, "up", lambda s: s["y"] <= gate["y1"] and s["mode"] == "play", 6)
    ok &= check(s["y"] == gate["y1"] and route(b) == "promenade", "with the Deck card, up the station's ladder to the boat walkway", s)
    boat = room(b, "lifeboat")
    b.teleport(boat["doors"][0]["outX"], boat["floor"], "promenade")
    b.shot("region2-walkway")
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "lifeboat", "the one lifeboat with its hatch open: inside", route(b))
    b.teleport(boat["x0"] + 112, boat["floor"], "lifeboat")
    b.shot("region2-lifeboat")
    b.tap("e")
    time.sleep(0.4)
    ok &= check(js(b, "window.__ship.save.books['2']") == "held", "the second book, on its bench", js(b, "JSON.stringify(window.__ship.save.books)"))
    b.teleport(boat["x0"] + 184, boat["floor"], "lifeboat")
    b.tap("e")
    time.sleep(0.9)
    ok &= check(b.state()["mode"] == "scripted", "the photo in its frame opens over the screen", b.state())
    b.shot("region2-photo")
    b.tap("e")
    time.sleep(0.6)
    ok &= check(b.state()["mode"] == "play" and "slot_lifeboat" in save_list(b, "seen"), "and closes on a key", b.state())
    b.teleport(boat["doors"][0]["x"], boat["floor"], "lifeboat")
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "promenade" and b.state()["y"] == boat["floor"], "out onto the walkway again", (route(b), b.state()))
    # The Library: her bubble while a book is out, the trolley, the shelf, the chair.
    lib = js(b, "window.__ship.world.data.library")
    b.teleport(lib["trolley"]["x"] - 40, D6)
    time.sleep(0.4)
    ok &= check(js(b, "window.__ship.world.people.byId.npc_librarian.bubbleItems[0].visible"), "the librarian shows a book while she carries one")
    b.shot("region2-librarian")
    b.teleport(lib["trolley"]["x"], D6)
    b.tap("e")
    end = time.time() + 6
    while time.time() < end and js(b, "window.__ship.save.books['2']") != "returned":
        time.sleep(0.1)
    time.sleep(0.8)
    ok &= check(js(b, "window.__ship.save.books['2']") == "returned" and b.state()["mode"] == "play", "E at the return trolley: she shelves it",
                js(b, "JSON.stringify(window.__ship.save.books)"))
    ok &= check(not js(b, "window.__ship.world.people.byId.npc_librarian.bubbleItems[0].visible"), "and her bubble is gone")
    b.shot("region2-shelf")
    b.teleport(lib["chair"]["x"], D6)
    b.tap("e")
    time.sleep(2.4)
    ok &= check(b.state()["mode"] == "scripted" and js(b, "window.__ship.player.anims.currentAnim.key") == "her-read", "in the red chair she reads it", b.state())
    b.shot("region2-page")
    b.tap("e")
    time.sleep(0.8)
    ok &= check(b.state()["mode"] == "play" and 2 in save_list(b, "read"), "its page shows, and closes on a key", save_list(b, "read"))
    # Running past her desk: a finger to her lips.
    b.teleport(exact_x(188.5), D6)
    b.hold("right", 0.7)
    ok &= check(person(b, "npc_librarian")["state"] == "acting", "she runs past the desk: the librarian's finger goes to her lips", person(b, "npc_librarian"))
    # Near-catch 2: asleep on the reading table; he knocks the rope stand into the aft door.
    shut = not use_door(b, 6, 194, -1)
    ok &= check(shut and "QUIET" in alert(b), "the Library's aft door is roped off: QUIET PLEASE", alert(b))
    go(b, 6, 177)
    b.hold("right", 1.5)
    ok &= check(wait_flag(b, "bb2"), "near-catch 2: he bolts from the reading table", flags(b))
    b.teleport(exact_x(191), D6)
    time.sleep(0.5)
    ok &= check(door_open(b, "part-door-6-194") and js(b, "window.__ship.world.things.find(t => t.id === 'prop_rope_down').img.visible"),
                "the rope stand lies where he knocked it; the door stands ajar")
    b.shot("region2-door")
    time.sleep(2.0)
    ok &= check(door_open(b, "part-door-6-194"), "and stays so")
    b.hold("right", 1.6)
    ok &= check(3 in save_list(b, "regions"), "through it: region 3", b.state())
    # Deck 7's lobbies: the ways up are busy, each with its own thing.
    for core, sign in (("forward", "DELIVERY"), ("atrium", "CARPET"), ("midship", "ART AUCTION")):
        f = js(b, f"(f => [f.bottom.x, f.bottom.y])(window.__ship.flights.find(g => g.name === 'stairs-{core}-7-8'))")
        b.teleport(f[0], f[1])
        b.hold("up", 0.5)
        ok &= check(b.state()["y"] == f[1] and sign in alert(b), f"deck 7, the {core} flight up: {sign}", alert(b))
    ok &= check(person(b, "blk_fitter")["on"], "the carpet fitter is at his roll")
    b.shot("region2-carpet")
    return ok


def enter_region3(b):
    """A save at region 3's door: regions 1 and 2 done (the Deck card, the Library's door ajar)."""
    b.open("?reset&play")
    b.eval("(P => { ['bb1', 'lunch', 'bb_lift', 'bb2', 'riv_prom', 'glimpse1', 'glimpse_window'].forEach(f => P.setFlag(f));"
           " P.open('cards', 'deck'); P.open('regions', 2); P.open('regions', 3); })(window.__ship.progress)")
    b.eval("window.__ship.cats.filter(c => c.flag === 'bb1' || c.flag === 'bb2').forEach(c => { c.gone = true; c.away = true; c.sprite.setVisible(false); })")
    time.sleep(0.2)


def enter_region4(b):
    """A save at region 4's door: regions 1-3 done (the Deck and Entertainment cards, the stage's
    beat), she has just come up the red trunk to deck 9."""
    b.open("?reset&play")
    b.eval("(P => { ['bb1', 'lunch', 'bb_lift', 'bb2', 'riv_prom', 'glimpse1', 'glimpse_window', 'bb3', 'pills'].forEach(f => P.setFlag(f));"
           " P.open('cards', 'deck'); P.open('cards', 'ent'); [2, 3, 4].forEach(r => P.open('regions', r)); })(window.__ship.progress)")
    b.eval("window.__ship.cats.filter(c => ['bb1', 'bb2', 'bb3'].includes(c.flag)).forEach(c => { c.gone = true; c.away = true; c.sprite.setVisible(false); })")
    b.eval("window.__ship.world.refresh()")
    time.sleep(0.2)


def pills_for_the_stage_manager(b):
    """The second errand, start to end (the golden path's): down the theatre's trunk to deck 4, his
    pills from his cabin, back up, into his hands: the Entertainment card."""
    tx = trunk_x("theatre")
    b.teleport(tx, D6)
    b.tap("e")
    s = hold_until(b, "down", lambda s: s["y"] == D4, 8)
    b.hold("left", 0.5)
    if b.state()["y"] != D4 or b.state()["mode"] != "play":
        return False
    cabin = room(b, "smcabin")
    b.teleport(cabin["doors"][0]["outX"], D4)
    b.tap("e")
    time.sleep(0.9)
    b.teleport(cabin["x0"] + 172, D4, "smcabin")
    b.tap("e")
    time.sleep(0.4)
    if "pills" not in save_list(b, "items"):
        return False
    b.teleport(cabin["doors"][0]["x"], D4, "smcabin")
    b.tap("e")
    time.sleep(0.9)
    b.teleport(tx, D4)
    b.tap("e")
    hold_until(b, "up", lambda s: s["y"] == D6, 8)
    b.hold("left", 0.4)
    b.teleport(exact_x(244.5), D6)
    b.tap("e")
    end = time.time() + 12
    while time.time() < end and "ent" not in save_list(b, "cards"):
        time.sleep(0.2)
    time.sleep(0.8)
    return "ent" in save_list(b, "cards") and b.state()["mode"] == "play"


def scenario_region3(b):
    """Region 3 (docs/build-plan.md, step 3): the theatre and deck 7 aft: the casino's chips, the
    jackpot, the drop onto the stage, near-catch 3 (the rival down the trap door, Bumbot up the fly
    rope), the swinging light, the bow, the pills from deck 4 and the Entertainment card, the
    dressing room's book, the lighting booth's photo, the red trunk to deck 9."""
    enter_region3(b)
    ok = True
    # The ways that open with region 3.
    s = climb(b, "stairs-aft-5-6", 2.6)
    ok &= check(s["mode"] == "stairs", "the aft stairs 5-6: the rehearsal's rope is gone", s)
    ok &= check(use_door(b, 7, 110, -1), "Magnum's door opens from the midship lobby")
    # The casino: a machine pays out over the floor; running on the chips she slips.
    spill = "window.__ship.world.movers.filter(m => m.pour)[0]"
    x = js(b, f"{spill}.def.x")
    b.teleport(x - 150, D7)
    js(b, f"(m => {{ m.state = 'idle'; m.at = 0; }})({spill})")
    time.sleep(0.5)
    ok &= check(js(b, f"{spill}.state") == "tell", "a slot machine's lights race: the tell", js(b, f"{spill}.state"))
    time.sleep(1.4)
    ok &= check(js(b, f"{spill}.state") == "spilled", "then its chips are all over the floor")
    b.shot("region3-chips")
    b.teleport(x - 20, D7)
    time.sleep(0.5)
    ok &= check(b.state()["mode"] == "play", "standing still on them is nothing", b.state())
    half = js(b, f"{spill}.def.half")
    b.teleport(x - half - 50, D7)
    hold_until(b, "right", lambda s: s["x"] >= x - half - 14, 3)
    b.hold(["right", "space"], 0.85)
    ok &= check(b.state()["mode"] == "play" and b.state()["x"] > x + half, "nor is a running jump over them", b.state())
    b.teleport(x + 20, D7)
    js(b, f"(m => {{ m.at = window.__ship.time.now + 4000; }})({spill})")
    b.hold("left", 0.5)
    ok &= check(b.state()["mode"] == "scripted" and "Ой-йой" in alert(b), "running on them: slipped", alert(b))
    time.sleep(2.8)
    js(b, "window.__ship.world.movers.filter(m => m.pour).forEach(m => { m.state = 'idle'; m.chips.clear(); m.at = window.__ship.time.now + 600000; })")
    # The machine with a glint pays her.
    jx = js(b, "window.__ship.world.things.find(t => t.id === 'sec_jackpot').x")
    b.teleport(jx, D7)
    b.tap("e")
    ok &= check(wait_flag(b, "jackpot", 5), "E at the machine with a glint: jackpot", flags(b))
    time.sleep(0.4)
    ok &= check(b.state()["tangerines"] >= 2, "it pays out two tangerines", b.state())
    b.shot("region3-jackpot")
    # The Art Gallery's cat: a double-take.
    b.teleport(exact_x(140.0), D7)
    time.sleep(1.9)
    ok &= check(b.state()["mode"] == "scripted" and js(b, "window.__ship.player.anims.currentAnim.key") == "her-idle-look",
                "a painting of a black cat: she looks twice", b.state())
    b.shot("region3-painting")
    time.sleep(1.9)
    # The lighting booth and the stage door want the Entertainment card.
    booth = room(b, "lighting")
    b.teleport(booth["doors"][0]["outX"], D7)
    b.tap("e")
    time.sleep(0.4)
    ok &= check(route(b) == "inside" and "Entertainment" in alert(b), "the lighting booth wants the Entertainment card", alert(b))
    # Off the balcony's end, down onto the stage: no scare.
    st = js(b, "window.__ship.world.data.stage")
    b.teleport(exact_x(243.0), D7)
    b.hold("right", 0.8)
    ok &= check(b.state()["y"] == D7, "the balcony's front holds her", b.state())
    hold_until(b, ["right", "space"], lambda s: s["y"] == D6, 4)
    time.sleep(0.3)
    s = b.state()
    ok &= check(s["y"] == D6 and s["mode"] == "play", "hopped, she drops onto the stage: no scare", s)
    b.teleport(exact_x(244.4), D6)
    time.sleep(0.4)
    ok &= check(person(b, "npc_stagemanager")["on"] and person(b, "amb_dancer_her")["on"] and not person(b, "amb_dancer_her_sat")["on"],
                "the stage manager at the curtain, the dancers rehearsing")
    b.shot("region3-stage")
    b.teleport(st["trapX"], D6)
    time.sleep(0.5)
    ok &= check(b.state()["y"] == D6 and route(b) == "inside", "the trap door holds before the beat", b.state())
    # Near-catch 3.
    b.teleport(exact_x(246.9), D6)
    b.hold("right", 0.5)
    time.sleep(1.5)
    b.shot("region3-rival")
    ok &= check(wait_flag(b, "bb3", 16), "near-catch 3: the rival goes down the trap door, Bumbot up the fly rope", flags(b))
    ok &= check(js(b, "window.__ship.world.story.trapHole.visible") and not js(b, "window.__ship.world.story.trapSeam.visible"),
                "the trap door stays open")
    ok &= check(not person(b, "amb_dancer_her")["on"] and person(b, "amb_dancer_her_sat")["on"], "the dancers sit it out in front of the stage")
    light = "window.__ship.world.movers.find(m => m.lamp)"
    time.sleep(1.2)
    ok &= check(js(b, f"{light}.lamp.swinging"), "and the stage light swings")
    time.sleep(4.0)
    ok &= check(b.state()["mode"] == "play", "where the scene left her it does not reach her", b.state())
    b.shot("region3-after")
    # He wants his pills; she has none yet.
    b.teleport(exact_x(244.5), D6)
    time.sleep(0.4)
    ok &= check(js(b, "window.__ship.world.people.byId.npc_stagemanager.bubbleItems[0].visible"), "the stage manager shows a pill bottle")
    b.tap("e")
    time.sleep(0.5)
    ok &= check("ent" not in save_list(b, "cards") and b.state()["mode"] == "play", "E without them: nothing yet")
    # The bow, between the open trap door and the swinging light.
    b.teleport(exact_x(247.3), D6)
    time.sleep(3.5)
    ok &= check(b.state()["mode"] == "scripted" and js(b, "window.__ship.player.anims.currentAnim.key") == "her-bow",
                "three seconds still at centre stage: she bows to the house", b.state())
    b.shot("region3-bow")
    time.sleep(2.2)
    # The light at the bottom of its swing.
    b.teleport(js(b, f"{light}.def.x"), D6)
    end = time.time() + 4
    hit = False
    while time.time() < end and not hit:
        hit = b.state()["mode"] == "scripted"
        time.sleep(0.05)
    ok &= check(hit and "Ай" in alert(b), "under the swinging light: bonked", alert(b))
    time.sleep(2.8)
    # The open trap door: one deck down onto the galley's flour sacks, beside the rival.
    b.teleport(st["trapX"], D6)
    time.sleep(1.6)
    ok &= check(route(b) == "galley" and b.state()["mode"] == "play", "into the open trap door: the galley, no scare", (route(b), b.state()))
    ok &= check(person(b, "riv_galley")["on"], "where the security officer sits in the flour")
    b.shot("region3-galley")
    g = room(b, "galley")
    b.teleport(g["doors"][0]["x"], D5, "galley")
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "inside" and b.state()["y"] == D5, "out of the galley on deck 5", b.state())
    # The pills, down the theatre's trunk and back; his card.
    ok &= check(pills_for_the_stage_manager(b), "his pills from his cabin on deck 4: he hands over the Entertainment card", save_list(b, "cards"))
    time.sleep(0.5)
    ok &= check(not js(b, "window.__ship.world.people.byId.npc_stagemanager.bubbleItems[0].visible"), "his bubble is gone")
    b.shot("region3-card")
    # With the card: the dressing room's book, the lighting booth's photo.
    dr = room(b, "dressing")
    b.teleport(dr["doors"][0]["outX"], D6)
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "dressing", "the stage door opens", route(b))
    b.teleport(dr["x0"] + 118, D6, "dressing")
    b.shot("region3-dressing")
    b.tap("e")
    time.sleep(0.4)
    ok &= check(js(b, "window.__ship.save.books['3']") == "held", "the third book, on the make-up table")
    b.teleport(dr["doors"][0]["x"], D6, "dressing")
    b.tap("e")
    time.sleep(0.9)
    b.teleport(booth["doors"][0]["outX"], D7)
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "lighting", "the lighting booth opens", route(b))
    b.teleport(booth["x0"] + 446, D7, "lighting")
    b.shot("region3-catwalk")
    b.tap("e")
    time.sleep(0.9)
    ok &= check(b.state()["mode"] == "scripted", "the photo at the catwalk's end", b.state())
    b.tap("e")
    time.sleep(0.6)
    ok &= check("slot_lighting" in save_list(b, "seen"), "seen")
    b.teleport(booth["doors"][0]["x"], D7, "lighting")
    b.tap("e")
    time.sleep(0.9)
    # The way on: the red trunk from Bliss up to deck 9.
    b.teleport(trunk_x("magnums"), D6)
    b.tap("e")
    hold_until(b, "up", lambda s: s["y"] == D9, 9)
    b.hold("right", 0.6)
    ok &= check(4 in save_list(b, "regions"), "up the red trunk from Bliss to deck 9: region 4", b.state())
    return ok


def scenario_sweep(b):
    b.open("?reset&play")
    b.eval("window.__ship.progress.frozen = true")      # teleporting round the ship opens nothing
    ok = True
    # Every card flight is shut going up without its card, and free coming down (its escape side);
    # every block stops her both ways.
    for (core, deck), lock in FLIGHT_LOCKS.items():
        if core == "atrium":
            continue
        name = f"stairs-{core}-{deck - 1}-{deck}"
        s = climb(b, name, 0.5)
        ok &= check(s["mode"] == "play" and s["y"] == floor_y(deck - 1), f"{name} shut going up ({lock[1]})", alert(b))
        _, (x1, y1) = flight_feet(name)
        b.teleport(x1, y1)
        b.hold("down", 0.5)
        s = b.state()
        ok &= check(s["mode"] == "play", f"{name} coming down: blocked", s)
    # The atrium's blocks, at the foot of each blocked flight.
    for (core, deck), lock in FLIGHT_LOCKS.items():
        if core != "atrium":
            continue
        foot = b.eval(f"(f => [f.bottom.x, f.bottom.y])(window.__ship.flights.find(f => f.name.startsWith('stairs-atrium-{deck - 1}-')))")
        b.teleport(*foot)
        b.hold("up", 0.5)
        s = b.state()
        ok &= check(s["mode"] == "play", f"the atrium's stairs {deck - 1}-{deck} blocked ({lock[1]})", alert(b))
    # Every locked door, from its locked side; a card door opens from its free side.
    for (deck, m), lock in DOOR_LOCKS.items():
        if (deck, m) in ((11, 74), (10, 40)):
            continue      # the spa's and the bridge's own doors, checked by their names below
        sides = [-1, 1] if lock[0] in ("flag", "block") else [s for s in (-1, 1) if s != lock[-1]]
        for side in sides:
            ok &= check(not use_door(b, deck, m, side), f"the door on deck {deck} at {m} m shut from the {'bow' if side < 0 else 'stern'} side ({lock[0]})")
        if lock[0] in ("oneway", "card") and lock[-1]:
            ok &= check(use_door(b, deck, m, lock[-1]), f"and open from the other side")
    for name, deck, m in (("spa-door", 11, 74), ("bridge-door", 10, 40)):
        b.teleport(exact_x(m) + 16, floor_y(deck))
        b.tap("e")
        time.sleep(0.15)
        ok &= check(not door_open(b, name), f"{name}: gold, shut", alert(b))
    # The walls at the decks' ends: walking into a locked face, she stays out.
    for (deck, end), lock in END_WALL_LOCKS.items():
        bx = b.eval(f"window.__ship.progress.barriers.filter(b => b.id === 'end-wall-{deck}-{end}').map(b => b.x)")
        side = 1 if lock[0] != "oneway" or lock[1] < 0 else -1      # the locked side
        x = max(bx) + 40 if side > 0 else min(bx) - 40
        b.teleport(x, floor_y(deck))
        b.hold("left" if side > 0 else "right", 1.0)
        s = b.state()
        held = s["x"] >= max(bx) if side > 0 else s["x"] <= min(bx)
        ok &= check(held, f"deck {deck}'s {end} end wall holds her on its locked side ({lock[0]})", s)
    # The plan's rooms: a card door stays shut without its card; an aired balcony cabin's corridor
    # door is shut from the corridor.
    doors = b.eval("Object.values(window.__ship.world.rooms).filter(r => r.def).flatMap(r => r.doors.filter(d => d.lock).map(d => "
                   "({ id: d.id, x: d.outX, y: d.outY, route: d.outRoute, lock: d.lock })))")
    for d in doors:
        if d["lock"].startswith("flag"):
            continue          # the balcony guest's own door, opened from inside (region 7's step)
        b.teleport(d["x"], d["y"], d["route"])
        b.tap("e")
        time.sleep(0.4)
        ok &= check(route(b) == d["route"], f"the door of {d['id']} shut ({d['lock']})", route(b))
    ok &= check(len(doors) >= 12, "every locked room door was tried", len(doors))
    # The lifeboat station's ladder wants the Deck card from below.
    gate = b.eval("window.__ship.world.ladders[0]")
    b.teleport(gate["x"], gate["y0"], "promenade")
    b.hold("up", 0.5)
    ok &= check(b.state()["mode"] == "play" and "Deck" in alert(b), "the boat walkway's ladder wants the Deck card", alert(b))
    # The bridge's hatch is shut until the alarm.
    hatch = b.eval("window.__ship.world.gates[0].x")
    b.teleport(hatch, D10)
    b.hold("up", 0.6)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D10, "the bridge's hatch is shut before the alarm", s)
    # The Spinnaker balcony's windscreen bars the jump down to the balcony forward of the spa.
    b.teleport(x_of(34), D12)
    b.hold("left", 1.0)
    b.hold(["left", "space"], 0.8)
    b.hold("left", 0.6)
    s = b.state()
    ok &= check(s["y"] == D12, "deck 12's windscreen can't be jumped", s)
    # The verbs are learned: no wall jump without the socks, no glide without the parasol, no crawl
    # before the linen room's beat, no dash before the first sight of him.
    b.teleport(exact_x(233) + 13, D11)
    b.key("space", True)
    time.sleep(0.34)
    b.key("space", False)
    time.sleep(0.02)
    b.hold(["left", "space"], 0.2)
    b.hold("left", 1.0)
    s = b.state()
    ok &= check(s["y"] == D11, "no wall jump up the sun cover's post without the socks", s)
    # (Jump is pressed once she is in the air: pressed on the floor first, she would jump, and
    # could come down on the sun cover's top.)
    b.eval(f"window.__ship.spawnAt({{x: {x_of(238)}, y: {D11 - 110}, route: 'inside'}})")       # in the air over the Great Outdoors
    time.sleep(0.15)
    b.key("space", True)
    time.sleep(0.75)
    s = b.state()
    b.key("space", False)
    ok &= check(s["y"] == D11, "no glide without the parasol: she just falls", s)
    linen = b.eval("window.__ship.rooms.find(r => r.route === 'linen').door")
    b.teleport(linen, D9, "linen")
    b.hold(["down", "right"], 2.4)
    time.sleep(0.6)
    ok &= check(route(b) == "linen" and not b.eval("window.__ship.crawling"), "no crawling into the vent before the beat", route(b))
    # The stage's trap door is shut before the rehearsal's beat.
    trap = b.eval("window.__ship.world.data.trapdoor")
    b.teleport(trap["x"] - 30, trap["y"])
    b.eval("window.__ship.cats.forEach(c => { c.gone = true; })")      # (he would stop her on the way)
    b.hold("right", 0.5)
    time.sleep(0.6)
    ok &= check(route(b) == "inside", "the trap door holds before the beat", route(b))
    # The elevators light only region 1's landings at the start.
    lit = b.eval("window.__ship.lifts.map(l => l.floors.filter(f => window.__ship.progress.regionOpen(f.region)).map(f => f.deck))")
    ok &= check(all(sorted(x) in ([4, 5], [5]) for x in lit), "the elevators light only decks 4-5 at the start", lit)
    return ok


def mover(mid):
    return f"window.__ship.world.movers.find(m => m.def && m.def.id === '{mid}')"


def wait_js(b, text, timeout=8):
    """Waits until an expression is true in the game."""
    end = time.time() + timeout
    while time.time() < end:
        if b.eval(text):
            return True
        time.sleep(0.04)
    return False


def scared(b, word, within=3.0):
    """A fright with `word` in it comes within a while."""
    end = time.time() + within
    while time.time() < end:
        if b.state()["mode"] == "scripted" and word in alert(b):
            return True
        time.sleep(0.04)
    return False


def scenario_region4(b):
    """Region 4 (docs/build-plan.md, step 4): Housekeeping, deck 9's corridor: the steward's cart and
    his card, the honeymooners' picture and the fourth book, the vacuum that darts out, the towel
    stack, the sprinkler, the balcony cabin and the glimpse from its balcony, the door that flies
    open, "Do Not Disturb", the luggage and the adjoining cabins' fort, near-catch 4 into the vent,
    the laundry cart under it, the duct with its grilles down into deck 8, the chute to the laundry."""
    enter_region4(b)
    ok = True
    W = "window.__ship.world"
    now = "window.__ship.time.now"
    tangerines = lambda: b.state()["tangerines"]
    # Up the red trunk: the crew door by it is her checkpoint here.
    b.teleport(trunk_x("magnums"), D9)
    b.hold("right", 0.7)
    ok &= check("cp_9_arrive" in save_list(b, "activated"), "the crew door by the trunk: a checkpoint as she arrives", save_list(b, "activated"))
    # The steward and his jammed cart.
    cart = f"{W}.pushables.find(t => t.id === 'cart_steward')"
    cx = js(b, f"{cart}.x")
    st = person(b, "npc_steward")
    ok &= check(st["on"] and abs(st["x"] - (cx + 35)) < 2, "the steward at his cart's far end", st)
    ok &= check(js(b, f"{W}.people.byId.npc_steward.sprite.anims.currentAnim.key").endswith("tug"), "pulling at it")
    b.hold("right", 1.5)
    ok &= check(b.state()["x"] < cx, "the cart fills the corridor", b.state())
    ok &= check(js(b, f"{W}.people.byId.npc_steward.bubbleItems[0].visible"), "his bubble shows a cart")
    b.shot("region4-steward")
    b.hold(["right", "space"], 0.7)
    ok &= check(b.state()["x"] < cx, "and can't be hopped where it is jammed", b.state())
    linen = b.eval("window.__ship.rooms.find(r => r.route === 'linen').door")
    b.teleport(linen, D9)
    b.tap("e")
    time.sleep(0.2)
    ok &= check("Housekeeping" in alert(b) and route(b) == "inside", "the linen room wants the Housekeeping card", alert(b))
    time.sleep(0.5)
    b.teleport(cx - 26, D9)
    b.hold("right", 0.3)
    b.tap("e")
    b.hold("right", 6.8)
    ok &= check("cart_free" in flags(b), "pushed along to 130 m, the cart is free", b.state())
    time.sleep(1.0)
    b.shot("region4-thanks")
    ok &= check(wait_js(b, "window.__ship.save.cards.includes('hk') && window.__ship.mode === 'play'", 10),
                "he thanks her and hands over the Housekeeping card", save_list(b, "cards"))
    st = person(b, "npc_steward")
    ok &= check(js(b, f"{W}.people.byId.npc_steward.sprite.anims.currentAnim.key").endswith("idle") and st["x"] > exact_x(130),
                "and stands by his cart", st)
    b.hold(["right", "space"], 0.7)
    b.hold("right", 0.5)
    ok &= check(b.state()["x"] > exact_x(130) and b.state()["mode"] == "play", "she hops the cart there", b.state())
    # The honeymooners.
    b.teleport(exact_x(133.6), D9)
    time.sleep(0.4)
    ok &= check(js(b, f"{W}.people.byId.npc_bride.bubbleItems[0].visible"), "the honeymooners hold out a camera")
    b.shot("region4-honeymooners")
    b.tap("e")
    time.sleep(1.75)
    b.shot("region4-photo")
    ok &= check(js(b, "window.__ship.player.anims.currentAnim.key") == "her-camera", "E: she takes their picture", b.state())
    ok &= check(wait_flag(b, "photo", 16), "the flash, their kiss, and in they go", flags(b))
    ok &= check(js(b, "window.__ship.save.books['4']") == "held", "the fourth book is their thanks")
    ok &= check(not person(b, "npc_bride")["on"] and not person(b, "npc_groom")["on"], "they have gone in")
    # The vacuum in the open cabin's doorway.
    vac = mover("haz_vacuum_9")
    vx = js(b, f"{vac}.def.x")
    b.teleport(vx - 160, D9)
    time.sleep(0.3)
    ok &= check(js(b, f"{vac}.state") == "in" and js(b, f"{vac}.armed"), "the vacuum waits in the cabin's doorway")
    b.key("right", True)
    hit = scared(b, "Іііі", 2.5)
    b.key("right", False)
    b.shot("region4-vacuum")
    ok &= check(hit, "running at the doorway: it darts out at her", alert(b))
    time.sleep(2.8)
    ok &= check(b.state()["mode"] == "play" and abs(b.state()["x"] - exact_x(119.6)) < 30, "and she is back at the crew door by the trunk", b.state())
    # A jump as it rattles clears it.
    b.teleport(vx - 160, D9)
    wait_js(b, f"{vac}.state === 'in' && {vac}.armed", 6)
    b.key("right", True)
    wait_js(b, f"{vac}.state === 'wait'", 3)
    b.key("space", True)
    time.sleep(0.75)
    b.key("space", False)
    b.key("right", False)
    time.sleep(0.3)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["x"] > vx - 30, "a jump as it rattles clears it", s)
    stk = mover("haz_towels_9")
    sx = js(b, f"{stk}.def.x")
    ok &= check(js(b, f"{stk}.state") == "up", "and the towel stack still stands", js(b, f"{stk}.state"))
    # Back in, it does nothing while she stands at the door; the cabin being cleaned.
    time.sleep(1.6)
    cl = room(b, "cleanup")
    b.teleport(cl["doors"][0]["outX"], D9)
    time.sleep(0.5)
    ok &= check(b.state()["mode"] == "play", "back in its doorway it leaves her alone", b.state())
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "cleanup" and person(b, "amb_bedmaker")["on"], "the cabin being cleaned: the bedmaker at the stripped bed", route(b))
    b.shot("region4-cleanup")
    b.teleport(cl["doors"][0]["x"], D9, "cleanup")
    b.tap("e")
    time.sleep(0.9)
    # The towel stack: walked past, it wobbles; a jump landed by it brings it down on her.
    # (The vacuum is kept in its doorway for this: beside the stack she is within its reach.)
    wait_js(b, f"{vac}.state === 'in'", 6)
    js(b, f"{vac}.update = () => {{}}")
    b.teleport(sx - 70, D9)
    b.hold("right", 1.0)
    ok &= check(js(b, f"{stk}.state") == "up" and b.state()["mode"] == "play" and b.state()["x"] > sx + 40, "walked past, the towel stack only wobbles", b.state())
    b.teleport(sx - 26, D9)
    time.sleep(0.3)
    b.hold("space", 0.2)
    hit = scared(b, "Мммф", 2.5)
    b.shot("region4-buried")
    ok &= check(hit, "a jump landed beside it: buried", alert(b))
    time.sleep(2.8)
    # The sprinkler: its drip is the tell; under it while it rains she is drenched.
    spr = mover("haz_sprinkler_9")
    px = js(b, f"{spr}.def.x")
    wait_js(b, f"{spr}.phase({now}) === 'on'", 6)
    wait_js(b, f"{spr}.phase({now}) === 'off'", 6)
    b.teleport(px - 80, D9)
    b.hold("right", 1.15)
    ok &= check(b.state()["mode"] == "play" and b.state()["x"] > px + 48, "between its showers she runs under the sprinkler", b.state())
    wait_js(b, f"{spr}.phase({now}) === 'tell'", 6)
    b.teleport(px, D9)
    hit = scared(b, "Бррр", 2.5)
    b.shot("region4-drenched")
    ok &= check(hit, "under it when it rains: drenched", alert(b))
    time.sleep(2.8)
    # The balcony cabin: the green card's door, a checkpoint, the basket, the balcony and who is up there.
    bc = room(b, "balcabin9")
    n = tangerines()
    b.teleport(bc["doors"][0]["outX"], D9)
    time.sleep(0.2)
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "balcabin9" and "cp_balcabin" in save_list(b, "activated"), "the balcony cabin opens with the card: a checkpoint", route(b))
    b.teleport(bc["x0"] + 150, D9, "balcabin9")
    time.sleep(0.4)
    b.shot("region4-balcabin")
    b.hold("space", 0.3)
    time.sleep(0.6)
    ok &= check(tangerines() == n + 1, "a tangerine in its fruit basket", tangerines())
    b.teleport(bc["doors"][1]["x"], D9, "balcabin9")
    b.tap("e")
    time.sleep(1.5)
    b.shot("region4-balcony")
    ok &= check(route(b) == "promenade" and "glimpse_balcony" in flags(b), "out on its balcony: Bumbot on the rail a deck up", (route(b), flags(b)))
    b.tap("e")
    time.sleep(1.0)
    ok &= check(route(b) == "balcabin9", "and back in", route(b))
    b.teleport(bc["doors"][0]["x"], D9, "balcabin9")
    b.tap("e")
    time.sleep(0.9)
    # The door that flies open.
    sw = mover("haz_swing_9")
    wx = js(b, f"{sw}.def.x")
    b.teleport(wx - 200, D9)
    time.sleep(0.2)
    b.key("right", True)
    hit = scared(b, "Ай", 3.0)
    b.key("right", False)
    b.shot("region4-bonked")
    ok &= check(hit, "running past the door that flies open: bonked", alert(b))
    ok &= check(person(b, "haz_swing_9_who")["on"], "the kid with the water pistol looks out")
    time.sleep(2.8)
    ok &= check(abs(b.state()["x"] - bc["doors"][0]["outX"]) < 30, "back at the balcony cabin's door", b.state())
    wait_js(b, f"{sw}.state === 'shut' && {sw}.armed", 6)
    b.teleport(wx - 200, D9)
    b.key("right", True)
    wait_js(b, f"{sw}.state === 'rattle'", 3)
    b.key("right", False)
    wait_js(b, f"{sw}.state === 'open'", 3)
    b.hold("right", 1.6)
    ok &= check(b.state()["mode"] == "play" and b.state()["x"] > wx + 40, "stopping when its handle rattles, then on past it", b.state())
    # "Do Not Disturb".
    dx = js(b, f"{mover('haz_dnd_9')}.def.x")
    b.teleport(dx - 8, D9)
    time.sleep(0.3)
    ok &= check(b.state()["mode"] == "play", "the Do Not Disturb door: left alone, nothing")
    b.tap("e")
    time.sleep(0.35)
    b.shot("region4-startled")
    ok &= check(b.state()["mode"] == "scripted" and "вибачте" in alert(b), "E at it: startled", alert(b))
    time.sleep(3.0)
    # The standing cart and its tangerine; the luggage to the ceiling.
    b.teleport(exact_x(172.6) - 44, D9)
    b.hold(["right", "space"], 0.4)
    time.sleep(0.5)
    b.hold("left", 0.08)
    time.sleep(0.2)
    ok &= check("tan_9_cart" in save_list(b, "collected") and b.state()["mode"] == "play", "onto the standing cart for its tangerine", b.state())
    b.teleport(exact_x(178.4), D9)
    b.hold("right", 1.0)
    b.hold(["right", "space"], 0.8)
    ok &= check(b.state()["x"] < exact_x(180), "the stack of luggage can't be hopped", b.state())
    b.shot("region4-luggage")
    # The adjoining cabins: in at 176; the children's fort bars the way through until she can crawl.
    ad = room(b, "adjoin")
    b.teleport(ad["doors"][0]["outX"], D9)
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "adjoin", "into the first of the adjoining cabins", route(b))
    b.hold("right", 2.2)
    ok &= check(b.state()["x"] < ad["x0"] + 236, "the blanket fort across the way through stops her", b.state()["x"] - ad["x0"])
    b.shot("region4-fort")
    b.teleport(ad["doors"][0]["x"], D9, "adjoin")
    b.tap("e")
    time.sleep(0.9)
    # The dash goes through the luggage.
    b.teleport(exact_x(178.6), D9)
    time.sleep(0.2)
    b.key("right", True)
    b.tap("d")
    time.sleep(1.0)
    b.key("right", False)
    ok &= check("haz_luggage_9" in save_list(b, "broken") and b.state()["x"] > exact_x(180), "the dash goes through the luggage", b.state())
    ok &= check("tan_9_luggage" in save_list(b, "collected"), "and she has the tangerine behind it", save_list(b, "collected"))
    b.teleport(exact_x(191.0), D9)
    b.hold("right", 0.5)
    ok &= check("cp_9_mid" in save_list(b, "activated"), "the crew door before the aft lobby: a checkpoint")
    # The linen room: near-catch 4, into the vent.
    b.teleport(linen, D9)
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "linen", "with the card, into the linen room", route(b))
    b.shot("region4-linen")
    lc = f"{W}.pushables.find(t => t.id === 'cart_linen')"
    b.hold("right", 0.9)
    ok &= check(b.state()["x"] > js(b, f"{lc}.x"), "she walks past the laundry cart", b.state())
    time.sleep(0.9)
    b.shot("region4-vent")
    ok &= check(wait_flag(b, "bb4", 12), "near-catch 4: Bumbot leaps from the towels into the vent", flags(b))
    ok &= check("crawl" in save_list(b, "verbs"), "crawling is learned")
    time.sleep(0.5)
    ok &= check(js(b, f"{W}.story.cartKey.visible"), "the cart shows its key")
    # The cart under the vent, onto it, down on hands and knees: the duct.
    b.teleport(js(b, f"{lc}.x") - 36, D9, "linen")
    b.tap("e")
    ok &= check(b.state()["mode"] == "push", "E by the cart's end: she takes hold", b.state())
    b.hold("right", 2.6)
    ok &= check("cart_linen" in flags(b), "pushed under the vent", flags(b))
    time.sleep(0.3)
    b.shot("region4-cart")
    ok &= check(js(b, f"{W}.story.ventKey.visible"), "and the vent's key shows over it")
    b.hold(["right", "space"], 0.45)
    time.sleep(0.5)
    s = b.state()
    ok &= check(s["y"] == D9 - 36, "she jumps up onto it", s)
    b.shot("region4-on-cart")
    b.hold("down", 0.5)
    time.sleep(0.9)
    ok &= check(route(b) == "duct", "down on hands and knees on it: into the vent", route(b))
    duct = js(b, f"{W}.data.duct")
    time.sleep(0.3)
    ok &= check(js(b, f"{W}.eyesX != null && !{W}.eyesGone && {W}.eyesX < window.__ship.player.x - 100"), "his eyes in the dark ahead of her")
    b.shot("region4-duct")
    ok &= check(js(b, "window.__ship.player.anims.currentAnim.key") == "her-crawl", "crawling has its own clip")
    n = tangerines()
    g = duct["grilles"][3]
    s = hold_until(b, "left", lambda s: s["x"] < g["x"] + 6, 16)
    time.sleep(0.5)
    b.shot("region4-peek")
    ok &= check(js(b, f"{W}.peeks.find(k => k.what === 'snore').items[1].alpha") > 0.9, "over a grille: a look down at who snores below")
    ok &= check(tangerines() == n + 1, "a tangerine lost in the duct", tangerines())
    s = hold_until(b, "left", lambda s: s["x"] < duct["exitX"] + 6, 8)
    ok &= check(js(b, f"{W}.ductKey.visible"), "the far grille shows its key")
    b.tap("down")
    time.sleep(1.7)
    s = b.state()
    ok &= check(route(b) == "inside" and s["y"] == D8 and 5 in save_list(b, "regions"), "kicked out, she drops into deck 8 forward: region 5", s)
    # Now that she crawls: the fort, and what is in it.
    n = tangerines()
    b.teleport(ad["x0"] + 200, D9, "adjoin")
    time.sleep(0.3)
    s = hold_until(b, ["down", "right"], lambda s: s["x"] > ad["x0"] + 330, 5)
    ok &= check(s["x"] > ad["x0"] + 330 and tangerines() == n + 2, "crawling through the blanket fort: two tangerines hidden in it", (s["x"] - ad["x0"], tangerines() - n))
    b.teleport(ad["doors"][1]["x"], D9, "adjoin")
    time.sleep(0.3)
    b.tap("e")
    time.sleep(0.9)
    ok &= check(route(b) == "inside" and abs(b.state()["x"] - exact_x(183.6)) < 12, "and out of the second cabin's door, past the luggage", b.state())
    # The chute.
    b.teleport(js(b, f"{W}.data.linen.chuteX"), D9, "linen")
    time.sleep(0.4)
    b.tap("e")
    time.sleep(1.5)
    b.shot("region4-chute")
    ok &= check(wait_flag(b, "chute", 8) and route(b) == "laundry", "E at the chute's hatch: down to the laundry on deck 4", route(b))
    ok &= check(js(b, f"!!{W}.story.hat"), "a towel on her head")
    ok &= check(person(b, "riv_laundry")["on"], "the security officer in a towel, his uniform in the wash")
    b.shot("region4-laundry")
    return ok


def enter_region5(b):
    """A save at region 5's door: regions 1-4 done (three cards, the crawl), she has just dropped
    out of the duct's far grille into deck 8's forward corridor."""
    b.open("?reset&play")
    b.eval("(P => { ['bb1', 'lunch', 'bb_lift', 'bb2', 'riv_prom', 'glimpse1', 'glimpse_window', 'bb3', 'pills', 'cart_free', 'steward',"
           " 'photo', 'bb4', 'cart_linen', 'duct'].forEach(f => P.setFlag(f));"
           " ['deck', 'ent', 'hk'].forEach(c => P.open('cards', c)); [2, 3, 4, 5].forEach(r => P.open('regions', r)); })(window.__ship.progress)")
    b.eval("window.__ship.cats.filter(c => ['bb1', 'bb2', 'bb3', 'bb4'].includes(c.flag)).forEach(c => { c.gone = true; c.away = true; c.sprite.setVisible(false); })")
    b.eval("window.__ship.world.refresh()")
    time.sleep(0.2)


def enter_region6(b):
    """A save at region 6's door: regions 1-5 done, she has come up the forward stairs to deck 11."""
    enter_region5(b)
    b.eval("(P => { P.open('regions', 6); })(window.__ship.progress)")
    # (The hints of the verbs learned on the way are not on the screen any more.)
    b.eval("window.__ship.world.refresh(); window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    b.teleport(exact_x(79.5), D11)
    time.sleep(0.3)


def scenario_region5(b):
    """Region 5 (docs/build-plan.md, step 5): deck 8 forward, a breather: out of the duct's grille,
    the party's door, the cabin with the sea in its window, her own cabin (a checkpoint, the fifth
    book on the bed, read there), the swan's cart, the lobby door that opens from inside, and the
    forward stairs on up to deck 11 past the officers' lobbies."""
    enter_region5(b)
    ok = True
    W = "window.__ship.world"
    thing = lambda tid: f"{W}.things.find(t => t.id === '{tid}')"
    duct = js(b, f"{W}.data.duct")
    b.teleport(duct["dropX"], D8)
    time.sleep(0.5)
    ok &= check(js(b, f"{thing('prop_grille_open')}.items[0].visible") and not js(b, f"{thing('prop_grille_shut')}.items[0].visible"),
                "the grille she dropped out of hangs open in the ceiling")
    ok &= check(js(b, f"{thing('prop_paws_8')}.items[0].visible"), "paw prints in the dust, toward the lobby's door")
    b.shot("region5-grille")
    # The party.
    px = js(b, f"{thing('amb_party')}.x")
    b.teleport(px - 60, D8)
    time.sleep(1.2)
    ok &= check(person(b, "amb_birthday")["on"], "the birthday girl dances at the door with the balloons")
    ok &= check(js(b, f"{W}.story.noteAt > 0"), "its music comes out into the corridor")
    b.shot("region5-party")
    # The lobby's door opens from the corridor.
    ok &= check(use_door(b, 8, 74, -1), "the lobby's door opens from the corridor")
    # The cabin with the sea in its window: she looks in.
    sx = js(b, f"{thing('amb_peek_sea')}.x")
    b.teleport(sx, D8)
    time.sleep(2.5)
    b.shot("region5-sea")
    ok &= check(b.state()["mode"] == "scripted" and js(b, "window.__ship.player.anims.currentAnim.key") == "her-idle-look",
                "an open cabin, the sea in its window: she looks in", b.state())
    time.sleep(1.9)
    # Her own cabin: a checkpoint at its door; the basket; the fifth book on the bed, read there.
    cabin = b.eval("window.__ship.rooms.find(r => r.route === 'cabin').door")
    b.teleport(cabin - 30, D8)
    b.hold("right", 0.4)
    ok &= check("cp_8206" in save_list(b, "activated"), "her cabin's door: a checkpoint", save_list(b, "activated"))
    b.teleport(cabin, D8)
    b.tap("e")
    time.sleep(1.0)
    ok &= check(route(b) == "cabin", "into cabin 8206", route(b))
    x0 = cabin - 59
    b.teleport(x0 + 104, D8, "cabin")
    time.sleep(0.4)
    ok &= check(b.state()["tangerines"] == 2, "two tangerines in the welcome basket", b.state())
    b.teleport(x0 + 186, D8, "cabin")
    time.sleep(0.3)
    b.shot("region5-bed")
    b.tap("e")
    time.sleep(0.4)
    ok &= check(js(b, "window.__ship.save.books['5']") == "held", "the fifth book, on her bed")
    b.teleport(x0 + 186, D8 - 32, "cabin")
    time.sleep(2.2)
    ok &= check(b.state()["mode"] == "scripted" and js(b, "!!window.__ship.world.library.reading"),
                "standing still on the bed with it, she sits down and reads it there", b.state())
    b.shot("region5-reading")
    time.sleep(1.6)
    b.tap("e")
    time.sleep(1.0)
    ok &= check(5 in save_list(b, "read") and b.state()["mode"] == "play", "its page read", (save_list(b, "read"), b.state()))
    time.sleep(5.2)
    ok &= check(b.state()["mode"] == "scripted" and not js(b, "!!window.__ship.world.library.reading"), "after that the bed is for bouncing again", b.state())
    b.tap("e")
    time.sleep(0.4)
    b.teleport(cabin, D8, "cabin")
    b.tap("e")
    time.sleep(1.0)
    ok &= check(route(b) == "inside", "and out again", route(b))
    # The swan's cart.
    ok &= check(js(b, f"{thing('prop_swan_cart_swan')}.items[0].visible"), "a steward's cart with a towel swan on it")
    b.teleport(exact_x(31.5), D8)
    time.sleep(0.4)
    b.shot("region5-swan")
    # The forward stairs on up: the officers' lobbies stay shut, deck 11 opens.
    (x0, y0), _ = flight_feet("stairs-forward-8-9")
    b.teleport(x0, y0)
    s = hold_until(b, "up", lambda s: s["y"] == D11 and s["mode"] == "play", 12)
    ok &= check(s["y"] == D11 and 6 in save_list(b, "regions"), "up the forward stairs, past decks 9 and 10, to deck 11: region 6", s)
    (x9, y9), _ = flight_feet("stairs-forward-9-10")
    b.teleport(x9, y9)
    time.sleep(0.3)
    ok &= check(not use_door(b, 9, 74, 1) and "Officer" in alert(b), "deck 9's forward lobby: its doors want the Officer's card", alert(b))
    return ok


def scenario_region6(b):
    """Region 6 (docs/build-plan.md, step 6): Lido, deck 11 from the forward lobby aft and deck 10's
    hallway under the pool: the socks and a wall jump, near-catch 5 from the water and the pool
    draining, the hatch, the trays and their door, the kid (a fright, the dash, the cone), the wet
    patch and its deck chair, the buffet queue, the soft serve machine's swirl, the gull, the
    canister from the cold room, the table with her husband and the sixth book, the cone for
    herself, the hot tub, the chess set, the crates."""
    enter_region6(b)
    ok = True
    W, S = "window.__ship.world", "window.__ship"
    thing = lambda tid: f"{W}.things.find(t => t.id === '{tid}')"
    who = lambda pid: f"{W}.people.byId['{pid}']"
    L = js(b, f"{W}.data.lido")
    pool1, pool2 = L["pools"]
    # The forward lobby, the gym.
    cp = js(b, f"{S}.checkpoints.find(c => c.id === 'cp_gym').x")
    b.teleport(cp - 30, D11)
    b.hold("right", 0.4)
    ok &= check("cp_gym" in save_list(b, "activated"), "the gym's crew door: a checkpoint")
    ok &= check(person(b, "amb_treadmill")["on"] and person(b, "amb_weights")["on"], "the gym's two: a runner on a treadmill, a man with dumbbells")
    s = climb(b, "stairs-midship-11-12", 0.6)
    ok &= check(s["y"] == D11 and "WET PAINT" in alert(b) and person(b, "blk_painter")["on"], "the midship flight up: wet paint, and the painter", alert(b))
    ok &= check(js(b, f"{S}.progress.blockLifted('towels')") and not js(b, f"{thing('prop_towels_table')}.items[0].visible"),
                "the towel animals are gone from the midship flight below")
    b.shot("region6-painter")
    time.sleep(0.6)
    b.teleport(exact_x(95.75) - 8, D11)
    time.sleep(0.3)
    b.shot("region6-socks")
    b.tap("e")
    time.sleep(0.3)
    ok &= check("socks" in save_list(b, "verbs") and "kick" in alert(b), "the grip socks, on the rack by the yoga mats; how they are used", alert(b))
    time.sleep(3.2)
    # The chess set.
    b.teleport(L["chessX"] - 20, D11)
    time.sleep(0.3)
    px = js(b, f"{W}.story.pawn.x")
    b.tap("e")
    time.sleep(1.6)
    ok &= check(js(b, f"{W}.story.pawn.x") != px and "sec_chess" in save_list(b, "seen"), "the giant chess set: she moves a pawn")
    b.shot("region6-chess")
    # Near-catch 5: she comes to him swimming; the kid in the hot tub; the pool drains with her in it.
    ok &= check(person(b, "npc_kid_tub")["on"] and not person(b, "npc_kid")["on"], "the kid is in the hot tub, his cap over its rim")
    b.teleport(pool1["x1"] - 230, D11)
    time.sleep(0.8)
    ok &= check(b.state()["mode"] == "swim", "the first pool fills the deck: she swims", b.state())
    hold_until(b, "right", lambda s: s["mode"] == "scripted", 6)
    time.sleep(2.2)
    b.shot("region6-beat")
    ok &= check(wait_js(b, f"{S}.save.flags.includes('bb5')", 14), "near-catch 5: the kid squirts him, he falls in, climbs out over the lever and is gone aft", flags(b))
    ok &= check("drain" in flags(b) and js(b, f"{W}.story.lever.texture.key") == "lever-down", "the drain's lever is down")
    ok &= check(wait_js(b, f"{W}.story.paws.alpha > 0.3", 2), "wet paw prints lead aft")
    ok &= check(b.state()["mode"] == "swim", "she is still in the water as it starts to sink", b.state())
    ok &= check(wait_js(b, f"{S}.mode === 'play' && {S}.player.y === {D11 + 32}", 8), "the water gone, she stands in the empty tank", b.state())
    b.shot("region6-drained")
    ok &= check(not person(b, "npc_kid_tub")["on"] and person(b, "npc_kid")["on"], "the kid has left the hot tub for the aft pool deck")
    # The hatch in the tank's floor; deck 10's hallway: the trays outside a "Do Not Disturb" door.
    hx = js(b, f"{W}.data.hatchPool.x")
    b.teleport(hx, D11 + 32)
    time.sleep(0.3)
    b.tap("e")
    time.sleep(1.6)
    s = b.state()
    ok &= check(s["y"] == D10 and abs(s["x"] - hx) < 4, "the hatch drops her into deck 10's hallway", s)
    trays = js(b, f"{W}.data.ents.find(e => e.kind === 'trays')")
    hold_until(b, "right", lambda s: s["x"] > trays["x0"] + 6, 5)
    ok &= check(scared(b, "вибачте", 3), "the trays clatter under her feet, and their door flies open: startled", alert(b))
    b.shot("region6-trays")
    ok &= check(wait_js(b, f"{S}.mode === 'play'", 8) and "trays_10m" in flags(b), "she comes back at a checkpoint", b.state())
    ok &= check(js(b, f"{S}.tangerines.some(t => t.id === 'tan_10_tray')"), "a tangerine has rolled out from among the trays")
    b.teleport(trays["x0"] - 42, D10)
    time.sleep(0.6)
    b.key("right", True)
    time.sleep(0.2)
    b.key("space", True)
    time.sleep(0.35)
    b.key("space", False)
    time.sleep(0.75)
    b.key("right", False)
    time.sleep(0.6)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["x"] > trays["x1"] and js(b, f"{mover('haz_trays_10m')}.armed"), "a jump clears the trays", s)
    ok &= check(all(js(b, f"!!{mover(m)}") for m in ("haz_swing_10m", "haz_sprinkler_10m", "haz_dnd_10m2")), "further aft: a swinging door, a sprinkler, another door not to knock at")
    b.teleport(exact_x(110) + 16, D10)
    time.sleep(0.4)
    b.tap("e")
    time.sleep(0.3)
    ok &= check(door_open(b, "part-door-10-110"), "the hallway's lobby door opens from inside")
    # Back on deck 11. The hot tub's canopy: up by a wall jump off its post, a tangerine on its roof.
    post = exact_x(131.03)
    had = len(save_list(b, "collected"))
    b.teleport(post + 30, D11)
    time.sleep(0.5)
    b.key("left", True)
    b.key("space", True)
    time.sleep(0.16)
    b.key("space", False)
    time.sleep(0.06)
    b.key("space", True)
    b.key("left", False)
    b.key("right", True)
    time.sleep(0.3)
    b.key("space", False)
    time.sleep(0.12)
    b.key("right", False)
    time.sleep(0.8)
    s = b.state()
    ok &= check(s["y"] == D11 - 90, "a kick off the canopy's post takes her up onto its roof", s)
    b.shot("region6-canopy")
    hold_until(b, "right" if s["x"] < L["tubX"] else "left", lambda s: abs(s["x"] - L["tubX"]) < 6, 3)
    time.sleep(0.2)
    ok &= check(len(save_list(b, "collected")) == had + 1, "and to the tangerine on it")
    # The hot tub.
    b.teleport(L["tubX"] - 10, D11)
    time.sleep(0.5)
    b.tap("e")
    time.sleep(2.4)
    b.shot("region6-hottub")
    ok &= check(b.state()["mode"] == "scripted", "E at the hot tub: she gets in", b.state())
    b.tap("space")
    ok &= check(wait_js(b, f"{S}.mode === 'play'", 4) and "sec_hottub" in save_list(b, "seen"), "and out again at a key")
    # The second pool; the attendant's hut on its aft rim.
    b.teleport(pool2["x1"] - 70, D11)
    time.sleep(0.8)
    b.hold("right", 0.5)
    b.key("right", True)
    b.tap("space")
    time.sleep(1.2)
    b.key("right", False)
    time.sleep(0.2)
    ok &= check(b.state()["y"] == D11 and "cp_pool" in save_list(b, "activated"), "out of the second pool at the pool attendant's hut: a checkpoint", b.state())
    # The kid: his jet; the dash sends him off.
    kid = who("npc_kid")
    ok &= check(person(b, "riv_loungers")["on"], "the security officer on his knees at a lounger")
    b.eval(f"{kid}.x = {L['kidA'] + 190}; {kid}.dir = -1; {kid}.mode = 'patrol'; {kid}.nextSquirt = 0; {kid}.pauseUntil = 0")
    b.teleport(L["kidA"] + 70, D11)
    ok &= check(scared(b, "Ааа", 4), "in front of the kid within four metres: splashed", alert(b))
    b.shot("region6-kid")
    ok &= check(wait_js(b, f"{S}.mode === 'play'", 8) and abs(b.state()["x"] - js(b, f"{S}.checkpoints.find(c => c.id === 'cp_pool').x")) < 30,
                "and back at the hut", b.state())
    b.eval(f"{S}.save.tangerines += 2; {S}.refreshHud()")
    b.eval(f"{kid}.x = {L['kidA'] + 190}; {kid}.dir = -1; {kid}.mode = 'patrol'; {kid}.nextSquirt = {S}.time.now + 1500; {kid}.pauseUntil = 0")
    b.teleport(L["kidA"] + 70, D11)
    time.sleep(0.15)
    b.tap("d")
    time.sleep(0.4)
    ok &= check(js(b, f"{kid}.mode") in ("flee", "hide"), "her shout sends him running to the far end", js(b, f"{kid}.mode"))
    time.sleep(3.0)
    ok &= check(b.state()["mode"] == "play" and js(b, f"{kid}.mode") == "hide", "where he keeps his back turned", js(b, f"{kid}.mode"))
    time.sleep(7.5)
    # The wet patch and its deck chair.
    wet = js(b, f"{W}.data.ents.find(e => e.kind === 'wet')")
    b.eval(f"{kid}.gone = true; {W}.refresh()")
    b.teleport(wet["x0"] - 60, D11)
    time.sleep(0.3)
    b.hold("right", 0.6)
    x1 = b.state()["x"]
    time.sleep(0.3)
    ok &= check(abs(b.state()["x"] - x1) < 12 and b.state()["mode"] == "play", "in the grip socks the wet tiles hold her", (x1, b.state()))
    b.teleport(wet["x0"] - 60, D11)
    b.eval(f"{S}.save.verbs = {S}.save.verbs.filter(v => v !== 'socks')")
    time.sleep(0.4)
    b.hold("right", 0.55)
    x1 = b.state()["x"]
    time.sleep(0.2)
    ok &= check(b.state()["x"] - x1 > 18, "without them she slides on across them", (x1, b.state()))
    ok &= check(scared(b, "Ой", 2), "and the deck chair slides at her: bumped", alert(b))
    b.shot("region6-wet")
    wait_js(b, f"{S}.mode === 'play'", 8)
    time.sleep(2.5)
    b.teleport(wet["x0"] - 60, D11)
    time.sleep(0.4)
    b.key("right", True)
    time.sleep(0.94)
    b.key("space", True)
    time.sleep(0.3)
    b.key("space", False)
    time.sleep(0.8)
    b.key("right", False)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["x"] > wet["x1"], "a jump as it comes clears the chair", s)
    b.eval(f"{S}.progress.learn('socks'); {kid}.gone = false; {W}.refresh()")
    time.sleep(3.3)
    # The Garden Cafe: the queue.
    q = js(b, f"{W}.data.ents.find(e => e.kind === 'queue')")
    line = lambda: sorted(js(b, f"{W}.people.list.filter(p => p.id.startsWith('haz_queue') && p.blocking).map(p => Math.round(p.x))"))
    first = line()[0]
    b.teleport(first - 110, D11)
    time.sleep(0.4)
    b.hold("right", 2.2)
    s = b.state()
    # (Held at someone's back: whoever is next ahead of her is within a step.)
    ok &= check(s["mode"] == "play" and any(0 < x - s["x"] < 30 for x in line()), "the buffet queue holds her back: no fright", (s, line()))
    b.shot("region6-queue")
    hops = 0
    while b.state()["x"] < q["x1"] + 20 and hops < 30:
        b.hold(["right", "space"], 0.55)
        b.hold("right", 0.2)
        hops += 1
    ok &= check(b.state()["x"] > q["x1"] and b.state()["mode"] == "play", "hopped one by one, she is past it", (hops, b.state()))
    # The cold room: the canister is not hers to take yet.
    door = js(b, f"{W}.rooms.coldroom.door")
    cold = js(b, f"{W}.rooms.coldroom.def.x0")
    b.teleport(door, D11)
    b.tap("e")
    time.sleep(1.0)
    ok &= check(route(b) == "coldroom", "the cold room, with the Housekeeping card", route(b))
    b.teleport(cold + 150, D11, "coldroom")
    time.sleep(0.3)
    b.tap("e")
    time.sleep(0.3)
    ok &= check(carrying(b) is None, "the canister stays on its shelf until the machine wants it")
    b.shot("region6-coldroom")
    b.teleport(door, D11, "coldroom")
    b.tap("e")
    time.sleep(1.0)
    # The aft lobby: the fans on the stairs.
    s = climb(b, "stairs-aft-11-12", 0.6)
    ok &= check(s["y"] == D11 and "BIG GAME" in alert(b) and person(b, "blk_fan_a")["on"], "the aft flight up: the Sports Bar's fans", alert(b))
    b.shot("region6-fans")
    time.sleep(0.6)
    # The Great Outdoors: the machine. A short swirl, too long a one, and a proper one.
    ok &= check(person(b, "npc_husband")["on"] and not js(b, f"{who('npc_husband')}.bubbleItems[0].visible"), "her husband at the first table, by the machine")

    def swirl(sec):
        b.teleport(L["machineX"] - 14, D11)
        time.sleep(0.4)
        b.key("e", True)
        time.sleep(sec)
        b.key("e", False)
        time.sleep(0.35)
        return js(b, f"{W}.story.lastSwirl")

    ok &= check(swirl(0.9) == "stub" and carrying(b) == "stub", "E let go early: a stub", carrying(b))
    b.eval(f"{kid}.x = {L['kidA'] + 120}; {kid}.mode = 'patrol'")
    b.teleport(L["kidA"] + 90, D11)
    time.sleep(0.5)
    ok &= check(js(b, f"{kid}.pose") == "stand" and js(b, f"{kid}.bubbleItems[0].visible"), "with a cone in her hands the kid waits for it, his bubble a soft serve")
    b.tap("e")
    time.sleep(3.2)
    ok &= check("kid_fed" not in flags(b) and carrying(b) is None and b.state()["mode"] == "play", "a stub: he drops it on the deck", flags(b))
    b.shot("region6-stub")
    b.eval(f"{kid}.nextSquirt = {S}.time.now + 60000")
    ok &= check(swirl(3.2) == "toppled" and carrying(b) is None, "held too long: it goes over")
    ok &= check(js(b, f"{W}.foodGulls.gull_go.state") == "pounce", "and the gull is on it")
    b.shot("region6-toppled")
    time.sleep(3.5)
    ok &= check(swirl(1.75) == "cone" and carrying(b) == "cone", "let go in the green: a proper cone", carrying(b))
    b.shot("region6-cone")
    ok &= check(0.5 < js(b, f"{W}.carryBox.left()") < 1, "and it is melting")
    # Standing about with it in the open: the gull has it.
    ok &= check(wait_js(b, f"{W}.foodGulls.gull_go.state === 'mark'", 6), "its shadow on the deck")
    ok &= check(wait_js(b, f"!{W}.carry", 4) and js(b, f"{W}.foodGulls.gull_go.stolen") == 1 and b.state()["mode"] == "play", "then the gull has her cone: no fright")
    b.shot("region6-gull")
    time.sleep(1.2)
    # Another; through the queue with it (they let crew with a tray by); to the kid.
    ok &= check(swirl(1.75) == "cone" and carrying(b) == "cone", "another cone")
    b.teleport(q["x1"] + 60, D11)
    time.sleep(0.3)
    s = hold_until(b, "left", lambda s: s["x"] < q["x0"] - 20, 12)
    ok &= check(s["x"] < q["x0"] and carrying(b) == "cone", "the queue turns aside for crew with a tray", (s, carrying(b)))
    b.eval(f"{kid}.x = {L['kidA'] + 120}; {kid}.mode = 'patrol'")
    b.teleport(L["kidA"] + 90, D11)
    time.sleep(0.5)
    b.tap("e")
    time.sleep(1.2)
    b.shot("region6-kid-eats")
    ok &= check(wait_flag(b, "kid_fed", 8) and carrying(b) is None, "a proper cone for the kid: he eats it", flags(b))
    ok &= check(js(b, f"{W}.foodGulls.gull_pool.off()"), "from now on he keeps the gulls off the pool deck")
    time.sleep(3.0)
    ok &= check(b.state()["mode"] == "play", "and never squirts her again", b.state())
    # The machine has run empty; his bubble: the canister; the cold room; no hopping with it.
    ok &= check(swirl(1.5) != "stub" and carrying(b) is None and b.state()["mode"] == "play", "the machine has run empty")
    b.teleport(L["husbandX"] - 40, D11)
    time.sleep(0.5)
    ok &= check(js(b, f"{who('npc_husband')}.bubbleItems[0].visible") and js(b, f"{who('npc_husband')}.bubbleItems[1].texture.key") == "pict-canister",
                "her husband's bubble: the canister")
    b.shot("region6-husband")
    b.teleport(door, D11)
    b.tap("e")
    time.sleep(1.0)
    b.teleport(cold + 150, D11, "coldroom")
    time.sleep(0.3)
    b.tap("e")
    time.sleep(0.3)
    ok &= check(carrying(b) == "canister", "the ice cream mix's canister, from the cold room's shelf", carrying(b))
    y0 = b.state()["y"]
    b.hold("space", 0.3)
    ok &= check(b.state()["y"] == y0, "too heavy to hop with")
    b.teleport(door, D11, "coldroom")
    b.tap("e")
    time.sleep(1.0)
    b.teleport(L["machineX"] - 14, D11)
    time.sleep(0.3)
    b.tap("e")
    time.sleep(1.0)
    b.shot("region6-pour")
    ok &= check(wait_flag(b, "refilled", 6) and carrying(b) is None, "poured into the machine: it has mix for good", flags(b))
    # A proper cone, and the table with him.
    ok &= check(swirl(1.75) == "cone" and carrying(b) == "cone", "a cone again")
    b.teleport(L["husbandX"] - 30, D11)
    time.sleep(0.4)
    ok &= check(js(b, f"{who('npc_husband')}.bubbleItems[1].texture.key") == "pict-softserve", "his bubble now: a soft serve")
    b.tap("e")
    time.sleep(3.0)
    b.shot("region6-table")
    ok &= check(wait_flag(b, "table", 12), "E with it: she sits down with him, and they eat looking at the wake", flags(b))
    ok &= check(js(b, f"{S}.save.books['6']") == "held", "he gives her the sixth book")
    ok &= check(js(b, f"{thing('slot_table')}.items[0].visible"), "their picture stands on the table")
    b.shot("region6-picture")
    # With no errand left, a cone is hers.
    swirl(1.75)
    time.sleep(0.5)
    ok &= check(b.state()["mode"] == "scripted" and carrying(b) is None, "a cone for herself, eaten where she stands", b.state())
    b.shot("region6-herself")
    ok &= check(wait_js(b, f"{S}.mode === 'play'", 5) and "sec_cone" in save_list(b, "seen"), "and done")
    # The crates behind the service station.
    crates = js(b, f"{thing('haz_crates_11')}.x")
    b.eval(f"{S}.save.tangerines += 1; {S}.refreshHud()")
    b.teleport(crates - 90, D11)
    time.sleep(0.3)
    b.tap("d")
    b.hold("right", 0.9)
    ok &= check("haz_crates_11" in save_list(b, "broken") and js(b, f"{S}.tangerines.some(t => t.id.startsWith('tan_11_crates'))"),
                "the dash goes through the crates: two tangerines were behind them", save_list(b, "broken"))
    time.sleep(0.5)
    return ok


SCENARIOS = {name[len("scenario_"):]: fn for name, fn in globals().items() if name.startswith("scenario_")}


def main():
    sys.stdout.reconfigure(errors="replace")  # the Windows console can't print every emoji
    names = sys.argv[1:] or list(SCENARIOS)
    b = Browser()
    all_ok = True
    try:
        for name in names:
            print(name)
            try:
                all_ok &= SCENARIOS[name](b)
            except Exception as e:
                all_ok = False
                print(f"  FAIL  {type(e).__name__}: {e}")
    finally:
        if b.errors:
            all_ok = False
            print("console errors:")
            for e in dict.fromkeys(b.errors):
                print("  ", e)
        b.close()
    print("screenshots:", OUT)
    print("PASS" if all_ok else "FAILED")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
