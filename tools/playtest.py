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

from build_ship_map import (ATRIUM, CORES, FUNNEL, POOL_OPENING, POOLS, PROMENADE, ROOF_ROW, STAGE, TILE, TRUNKS, col, floor_y,
                            walk_y, x_of)

ROOT = Path(__file__).resolve().parent.parent
CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
OUT = Path(tempfile.gettempdir()) / "bumbusik-playtest"

KEYS = {
    "left": (37, "ArrowLeft", "ArrowLeft"), "right": (39, "ArrowRight", "ArrowRight"),
    "up": (38, "ArrowUp", "ArrowUp"), "down": (40, "ArrowDown", "ArrowDown"),
    "space": (32, "Space", " "), "shift": (16, "ShiftLeft", "Shift"),
    "e": (69, "KeyE", "e"), "enter": (13, "Enter", "Enter"),
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

    def teleport(self, x, y):
        self.eval(f"window.__ship.spawnAt({{x: {x}, y: {y}}})")
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

D4, D5, D6, D7, D9, D10, D11, D12 = (floor_y(d) for d in (4, 5, 6, 7, 9, 10, 11, 12))
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
    b.open("?reset&play&cards=locked")
    b.teleport(CORE_L, D4)
    b.hold("up", 1.4)
    b.shot("stairs-climbing")
    b.key("up", True)
    time.sleep(5.0)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == D6, "holding up climbs through deck 5 to deck 6", s)
    locked = b.eval("window.__ship.alert.visible && window.__ship.alert.text")
    b.shot("stairs-locked")
    b.key("up", False)
    ok &= check(bool(locked) and "Hotel" in locked, "and stops there: the flight up needs the Hotel card", locked)
    b.hold("down", 5.5)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D4, "holding down carries her back to deck 4", s)
    b.open("?reset&play&cards=all")
    b.teleport(CORE_L, D4)
    b.hold("up", 9.0)
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
    b.open("?reset&play&cards=locked")
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

    # Three decks: letting go just short of the middle door settles her level with it.
    x = trunk_x("midships")
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
    ok &= check(not trunk_door(b, "magnums", 6) and bool(locked) and "Hotel" in locked,
                "a card-locked trunk asks for the Hotel card", locked)
    return ok


LIFT_X = col(CORES["forward"][0]) * TILE + 18 * TILE     # the forward core's elevator
GLASS_X = x_of(sum(ATRIUM["span"]) / 2)             # the atrium's glass elevator


def lift_cursor(b):
    return b.eval("window.__ship.liftRun && window.__ship.liftRun.lift.floors[window.__ship.liftRun.cursor].deck")


def scenario_lift(b):
    b.open("?reset&play&cards=locked")
    b.teleport(LIFT_X, D4)
    b.tap("e")
    time.sleep(0.5)
    ok = check(b.state()["mode"] == "lift" and b.eval("!!window.__ship.liftPanel"), "E opens the doors and shows the panel")
    for _ in range(4):
        b.tap("up")
        time.sleep(0.1)  # separate presses, not one long one
    ok &= check(lift_cursor(b) == 6, "with her crew card, ↑ picks no higher than deck 6", lift_cursor(b))
    b.shot("lift-panel")
    b.tap("e")
    time.sleep(0.1)
    ok &= check(not b.eval("window.__ship.liftPanel"), "the panel goes once the deck is chosen")
    time.sleep(0.8)
    b.shot("lift-riding")
    time.sleep(1.8)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D6 and abs(s["x"] - LIFT_X) < 2, "E rides it up to deck 6", s)
    b.shot("lift-arrived")
    b.hold("right", 0.5)
    time.sleep(0.4)
    ok &= check(b.eval("window.__ship.lifts[0].floors.every(f => f.leaves.open === 0)"), "the doors shut once she steps away")

    # Called from deck 4 while it waits on deck 6, the car comes down to her: she stays put.
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

    b.teleport(LIFT_X, D6)
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
    # The side walks are floor: she runs straight across the atrium.
    b.teleport(ATRIUM_X0 - 40, D7)
    b.hold("right", 7.6)
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


def scenario_bow(b):
    b.open("?reset&play&at=bow")
    time.sleep(4.8)
    s = b.state()
    zoom = b.eval("window.__ship.cameras.main.zoom")
    b.shot("bow-view")
    ok = check(s["mode"] == "scripted" and zoom < 1.5, "standing still on the mooring deck draws the camera back", (s, zoom))
    b.tap("right")
    time.sleep(1.0)
    s = b.state()
    zoom = b.eval("window.__ship.cameras.main.zoom")
    ok &= check(s["mode"] == "play" and zoom == 2, "a key brings it back", (s, zoom))
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
    ok &= check(b.state()["tangerines"] == 2, "she picks up the two tangerines on the desk", b.state())
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


def scenario_balcony(b):
    # The Stardust Lounge's balcony (deck 7) ends in a railing over the stage: she can hop it and
    # drop one deck onto the stage, no scare (§5.3).
    b.open("?reset&play")
    b.teleport(x_of(STAGE - 1.4), floor_y(7))
    b.key("right", True)
    b.tap("space")
    time.sleep(1.4)
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
    time.sleep(3.0)
    ok = check(b.eval(anim) == "", "stands plainly for the first few seconds")
    time.sleep(1.8)
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


def scenario_bumbot(b):
    b.open("?reset&play")
    b.wait_for("window.__ship && window.__ship.player")
    cat = "window.__ship.cats.find(c => c.name === 'bumbot-theatre')"
    ok = check(b.eval(f"{cat}.sprite.anims.currentAnim.key") == "bumbot-wash", "Bumbot is washing in the theatre")
    b.teleport(x_of(221), D6)
    b.shot("bumbot-wash")
    b.key("right", True)
    b.wait_for("window.__ship.mode === 'scripted'", timeout=5)
    b.key("right", False)
    b.wait_for("window.__ship.player.anims.currentAnim?.key === 'her-reach'", timeout=5)
    time.sleep(0.3)
    b.shot("bumbot-reach")
    ok &= check(b.eval(f"{cat}.gone"), "getting close starts a near-catch")
    b.wait_for("window.__ship.mode === 'play'", timeout=6)
    s = b.state()
    ok &= check(not b.eval(f"{cat}.sprite.visible") and s["y"] == D6, "he gets away and she can play on", s)
    b.hold("right", 0.3)
    ok &= check(b.state()["mode"] == "play", "no second near-catch once he is gone")
    return ok


def scenario_falls(b):
    b.open("?reset&play")
    # One deck: down through deck 12's walk onto deck 11's pool area, between the pools.
    b.teleport(x_of(132.5), D12)
    time.sleep(0.3)
    b.tap("down")
    time.sleep(1.2)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == D11, "a one-deck drop into the pool area is fine", s)
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
    b.teleport(x_of(236) + 6, D4)  # the tangerine behind the crate stack on deck 4
    time.sleep(0.3)
    s = b.state()
    ok = check(s["tangerines"] == 1, "picks up a tangerine", s)
    b.eval(f"window.__ship.vacuums[0].sprite.x = {x_of(228)}; window.__ship.vacuums[0].speed = 0")
    b.tap("shift")
    time.sleep(0.2)
    b.shot("dash-shout")
    s = b.state()
    ok &= check(s["dashing"] and s["tangerines"] == 0, "Shift spends it on a dash", s)
    # Dash forward along deck 4, through the crates and into the vacuum.
    b.hold("left", 2.5)
    s = b.state()
    ok &= check(s["x"] < x_of(231), "the dash breaks through the crates", s)
    ok &= check(b.eval("window.__ship.vacuums[0].alive") is False, "and smashes the vacuum")
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
