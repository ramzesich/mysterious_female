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
# Coordinates come from tools/build_slice_map.py: floors at y 240 (deck 5), 368 (deck 4),
# 496 (deck 3); the gangway spawn is x 712.

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
    return check(s["mode"] == "play" and s["y"] == 368, "spawns standing on deck 4 at the gangway", s)


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
    ok &= check(peak < 368 - 30, "jumps", f"y at 0.25s {peak}")
    ok &= check(b.state()["y"] == 368, "lands back on deck 4", b.state())
    return ok


def scenario_stairs(b):
    b.open("?reset&play")
    b.teleport(960, 368)
    b.hold("up", 1.4)
    b.shot("stairs-climbing")
    b.hold("up", 1.6)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == 240, "climbs the stairs to deck 5", s)
    time.sleep(0.2)
    b.hold("down", 1.5)
    b.hold("left", 2.0)  # ← also walks down this flight, and off it onto the deck 4 landing
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == 368 and s["x"] < 960, "walks back down to deck 4 and off along it", s)
    b.teleport(1120, 240)
    b.hold("down", 6.0)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == 496, "holding down carries her through the landing to deck 3", s)
    return ok


def scenario_ladder(b):
    b.open("?reset&play")
    b.teleport(488, 368)
    b.hold("down", 2.6)
    s = b.state()
    ok = check(s["y"] == 496, "climbs down the crew ladder to deck 3", s)
    b.hold("up", 2.6)
    s = b.state()
    ok &= check(s["y"] == 368 and s["mode"] == "play", "climbs back up and stands on deck 4", s)
    b.hold("right", 0.4)
    s = b.state()
    ok &= check(s["y"] == 368, "walks off the ladder top without falling through", s)
    return ok


def scenario_falls(b):
    b.open("?reset&play")
    # One deck: walk off the edge of the deck 5 atrium well onto deck 4.
    b.teleport(1265, 240)
    b.hold("right", 0.35)
    time.sleep(1.0)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == 368, "a one-deck fall is fine", s)
    # Two decks: drop through the middle of the well, where both decks are open.
    b.teleport(1336, 240)
    time.sleep(0.5)
    b.shot("long-fall")
    s = b.state()
    ok &= check(s["mode"] == "scripted", "a two-deck fall is a scare", s)
    time.sleep(2.0)
    s = b.state()
    ok &= check(s["mode"] == "play", "she comes back afterwards", s)
    return ok


def scenario_checkpoint(b):
    b.open("?reset&play")
    b.hold("right", 1.2)  # passes the deck 4 crew cabin door at x 808
    time.sleep(0.15)
    b.shot("checkpoint-lit")
    s = b.state()
    ok = check("cp-d4-gangway" in s["activated"], "passing a crew cabin door activates it", s)
    saved = b.eval("JSON.parse(localStorage.getItem('bumbusik-save-v1')).lastCheckpoint")
    ok &= check(saved == "cp-d4-gangway", "the game auto-saves there", saved)
    return ok


def scenario_vacuum(b):
    b.open("?reset&play")
    b.teleport(730, 496)  # deck 3, the robot vacuum patrols x 704-1024
    b.eval("window.__ship.vacuums[0].sprite.x = 760; window.__ship.vacuums[0].dir = -1")
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
    b.teleport(1470, 496)  # the deck 3 tangerine is at x 1480
    time.sleep(0.3)
    s = b.state()
    ok = check(s["tangerines"] == 1, "picks up a tangerine", s)
    b.tap("shift")
    time.sleep(0.2)
    b.shot("dash-shout")
    s = b.state()
    ok &= check(s["dashing"] and s["tangerines"] == 0, "Shift spends it on a dash", s)
    # Dash left down deck 3, through the vacuum and into the crates.
    b.hold("left", 6.8)
    s = b.state()
    ok &= check(b.eval("window.__ship.vacuums[0].alive") is False, "the dash smashes the vacuum")
    ok &= check(s["x"] < 320, "and breaks through the crates", s)
    return ok


def scenario_overboard(b):
    b.open("?reset&play")
    b.teleport(200, 240)  # the open aft deck, just inside the stern railing
    b.key("left", True)
    b.key("space", True)
    time.sleep(0.5)
    b.key("space", False)
    time.sleep(0.6)
    b.key("left", False)
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
