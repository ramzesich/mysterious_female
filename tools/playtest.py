"""Headless playtest driver: serves the game, opens it in headless Chrome, drives it with real key
events over the DevTools protocol, and reports state, console errors and screenshots.

    python tools/playtest.py [scenario ...]      (no arguments runs them all)
    python tools/playtest.py --real [scenario ...]   (in real time, as before: for comparing)
    python tools/playtest.py -j 6 [scenario ...]     (a process and a browser for each, six at a time)
    python tools/playtest.py --failed                (those that failed in the last run)
    python tools/playtest.py --times                 (every scenario's last time, slowest first)
    python tools/playtest.py --seed 7 region8        (the random draws from another seed; 1 by default)

The stepped clock (docs/plan-fast-tests.md): once a page has loaded, the test stops the game's own
loop and owns its clock (`takeover`): a wait of two seconds is 120 frames of a sixtieth of a second
stepped undrawn (`Browser.advance`), a few milliseconds; a frame is drawn only for a screenshot.
Every wait in the scenarios is `wait(seconds)` and every deadline `now()`, which go to that clock,
or to real time under `--real` and for the scenarios pinned to it (`REAL_TIME`: the sound runs on
the audio context's own clock, and `boot` proves the game's own loop still runs). Tools that use
`Browser` themselves (check_overlaps, shoot_people, render_ship, check_sound) run in real time
unless they ask for `Browser(stepped=True)`.

Screenshots go to the system temp folder (printed at the end). Needs Google Chrome and the
`websocket-client` package. Nothing here ships with the game.
"""

import atexit
import base64
import concurrent.futures
import functools
import http.server
import json
import os
import re
import shutil
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
from ship_layout import CARD_SPOTS, CREW_DECK, DOOR_LOCKS, END_WALL_LOCKS, FLIGHT_LOCKS

ROOT = Path(__file__).resolve().parent.parent
CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
OUT = Path(tempfile.gettempdir()) / "bumbusik-playtest"

KEYS = {
    "left": (37, "ArrowLeft", "ArrowLeft"), "right": (39, "ArrowRight", "ArrowRight"),
    "up": (38, "ArrowUp", "ArrowUp"), "down": (40, "ArrowDown", "ArrowDown"),
    "space": (32, "Space", " "), "d": (68, "KeyD", "d"), "f": (70, "KeyF", "f"),
    "e": (69, "KeyE", "e"), "enter": (13, "Enter", "Enter"), "o": (79, "KeyO", "o"),
    "m": (77, "KeyM", "m"), "escape": (27, "Escape", "Escape"),
}


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Server(http.server.ThreadingHTTPServer):
    # (Python's backlog is 5: with six browsers loading at once one of the game's files was refused,
    # a sheet's data never came, and the boot stopped. Chrome asks for many at a time.)
    request_queue_size = 128
    daemon_threads = True


# The page's side of the stepped clock: the game's loop stopped, `Date.now` and `performance.now`
# reading the stepped time (each keeps its own offset, so the tween manager, which reads `Date.now`,
# and the rumble follow it), and `__advance(frames, draw)` stepping it a sixtieth of a second a frame,
# the cameras moved each frame as drawing would move them, the browser given its turn between frames.
TAKEOVER = """(() => { const g = window.__game;
    if (window.__advance) return window.__t;
    g.loop.stop();
    window.__t = g.loop.now || performance.now();
    const d0 = Date.now() - window.__t;
    Date.now = () => Math.round(window.__t + d0);
    performance.now = () => window.__t;
    // (Between two frames the browser has its turn, as it has between two of the real loop's: the
    // game's scenes await their waits and tweens, and a promise's continuation runs only then. A
    // message on a channel is a turn with no delay of its own, after every pending continuation.)
    const mc = new MessageChannel();
    let turned = null;
    mc.port1.onmessage = () => turned();
    const turn = () => new Promise(r => { turned = r; mc.port2.postMessage(0); });
    window.__advance = async (frames, draw) => {
        for (let i = 0; i < frames; i++) {
            window.__t += 1000 / 60;
            // (The loop's own figures as the real loop keeps them: the cake's sway reads its delta.)
            const L = g.loop;
            L.time = L.now = window.__t;
            L.delta = L.rawDelta = 1000 / 60;
            L.frame++;
            if (draw) g.step(window.__t, 1000 / 60);
            else {
                g.headlessStep(window.__t, 1000 / 60);
                // (Undrawn, the cameras are still moved as drawing moves them: a camera follows her
                // and updates its view in its preRender, and the game reads that view.)
                for (const sc of g.scene.getScenes(true)) for (const c of sc.cameras.cameras) c.preRender();
            }
            await turn();
        }
        return window.__t;
    };
    return window.__t; })()"""
FRAME = 1 / 60
SEED = [1]      # the random draws' seed (`--seed N`)


class Browser:
    current = None      # the one browser of this process, for `wait()` and `now()`

    def __init__(self, stepped=False, closeups=False):
        # (Stepped: each page, once loaded, is taken over, `takeover()`. `closeups`: a thing she gets is
        # shown close and waits for a key, `world.closeup`; off unless that is what is checked.)
        self.stepped = stepped
        self.taken = False
        self.clock = 0.0
        Browser.current = self
        self.http_port = free_port()
        handler = functools.partial(Quiet, directory=str(ROOT))
        self.httpd = Server(("127.0.0.1", self.http_port), handler)
        self.httpd.handle_error = lambda *a, **k: None      # Chrome dropping a connection is no news
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

        self.debug_port = free_port()
        self.profile = tempfile.mkdtemp(prefix="bumbusik-chrome-")
        # (A script stopped by a timeout or an error does not take its browser with it otherwise:
        # five were found still running, 2026-11-18.)
        self.closed = False
        atexit.register(self.close)
        self.proc = subprocess.Popen([
            CHROME, "--headless=new", f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={self.profile}", "--window-size=960,540", "--no-first-run",
            # (Muted: the user heard every test run through their speakers, 2026-11-14: "please test
            # with sound off". The game's sound still runs and is checked; nothing comes out.)
            "--autoplay-policy=no-user-gesture-required", "--enable-unsafe-swiftshader", "--mute-audio", "about:blank",
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
        # (The game's random draws from one seed, so that a failing run can be played again exactly:
        # `--seed`, docs/plan-fast-tests.md §3.6. Installed before the page's own scripts.)
        self.send("Page.addScriptToEvaluateOnNewDocument", source=f"""(() => {{ let a = {SEED[0]} >>> 0;
            Math.random = () => {{ a = (a + 0x6D2B79F5) >>> 0; let t = a;
                t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
                return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }}; }})();""")
        if not closeups:
            self.send("Page.addScriptToEvaluateOnNewDocument", source="window.__skipCloseups = true;")

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

    def open(self, query="", start="gangway"):
        """Opens the game. A scenario that goes straight into play begins where the game began when
        most of them were written: in the gangway lobby on deck 4, its crew door's checkpoint lit
        (`start`). The game's own start, deck 3's crew corridor (the user, 2026-11-14), is
        `start=None`: the `boot` and `deck3` scenarios. (A scenario that picks up a tangerine on its
        way and then checks a gull's swoop (20 to 22) empties her pocket first: with one on her, the
        gull takes it instead of its gag.)"""
        old = bool(start) and "play" in query and "at=" not in query
        if old:
            query += f"&at={start}"
        # (The game as she will get it, whatever `DEV_FRESH` in src/config.js says: its save kept
        # between loads, which some scenarios use.)
        if "real" not in query:
            query += ("&" if "?" in query else "?") + "real"
        # (A new page runs in real time until it is there: loading is the browser's own work.)
        self.taken = False
        before = len(self.errors)
        for attempt in (1, 2):
            self.send("Page.navigate", url=f"http://127.0.0.1:{self.http_port}/index.html{query}")
            time.sleep(0.3)
            # (The welcome screen and the intro are the ship scene's own: it is there whatever the link.)
            try:
                self.wait_for("window.__ship && window.__ship.player && window.__ship.soundscape", timeout=15)
                break
            except TimeoutError:
                # (Once more: a file refused under load is not the game's fault; the game's own fails
                # again, and its errors stay in `errors`.)
                if attempt == 2:
                    raise
                print("  (the page did not come up; loaded again. Its errors:", "; ".join(e.splitlines()[0] for e in self.errors[before:]) + ")")
                del self.errors[before:]
        if self.stepped:
            self.takeover()
        self.wait(0.5)
        if old:
            self.eval("""(s => { const c = s.checkpoints.find(c => c.id === 'cp_gangway');
                if (c && !c.active) { s.lightCheckpoint(c, false); s.save.activated.push(c.id); } })(window.__ship)""")

    def eval(self, expr, settle=False):
        """`settle`: the expression is a promise, and its value is what it settles to."""
        res = self.send("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=settle)
        if "exceptionDetails" in res:
            raise RuntimeError(res["exceptionDetails"].get("exception", {}).get("description"))
        return res.get("result", {}).get("value")

    def wait_for(self, expr, timeout=10):
        end = self.now() + timeout
        while self.now() < end:
            try:
                if self.eval(f"!!({expr})"):
                    return
            except RuntimeError:
                pass
            self.wait(0.1)
        raise TimeoutError(f"timed out waiting for: {expr}  errors: {self.errors}")

    # --- The clock: stepped once the page is taken over, real before and under `--real` ----------

    def takeover(self):
        """Stops the game's own loop and owns its clock (docs/plan-fast-tests.md §3.1), and sows
        Phaser's own random draws from the seed."""
        self.eval(TAKEOVER)
        self.eval(f"Phaser.Math.RND.sow(['{SEED[0]}'])")
        self.taken = True

    def advance(self, seconds, draw=False):
        """Steps the game `seconds` of its time, a sixtieth of a second a frame (at least one),
        undrawn unless `draw`."""
        n = max(1, round(seconds * 60))
        self.eval(f"window.__advance({n}, {str(draw).lower()})", settle=True)
        self.clock += n * FRAME

    def wait(self, seconds):
        if self.taken:
            self.advance(seconds)
        else:
            time.sleep(seconds)

    def now(self):
        return self.clock if self.taken else time.time()

    def key(self, name, down):
        code, code_name, key = KEYS[name]
        self.send("Input.dispatchKeyEvent", type="rawKeyDown" if down else "keyUp",
                  windowsVirtualKeyCode=code, nativeVirtualKeyCode=code, code=code_name, key=key)

    def hold(self, names, seconds):
        names = [names] if isinstance(names, str) else names
        for n in names:
            self.key(n, True)
        self.wait(seconds)
        for n in names:
            self.key(n, False)

    def tap(self, name, seconds=0.08):
        self.hold(name, seconds)

    # --- A fake Xbox controller (headless Chrome has none) -----------------------------------
    # Installed before the page's own scripts: `navigator.getGamepads()` returns it, and Phaser
    # polls that every frame, as it does a real one. Buttons by name, in the standard layout.
    PAD = {"A": 0, "B": 1, "X": 2, "Y": 3, "LB": 4, "RB": 5, "LT": 6, "RT": 7, "VIEW": 8, "MENU": 9,
           "LS": 10, "RS": 11, "UP": 12, "DOWN": 13, "LEFT": 14, "RIGHT": 15}

    def fake_pad(self, on=True, index=0):
        if not on:
            if getattr(self, "pad_script", None):
                self.send("Page.removeScriptToEvaluateOnNewDocument", identifier=self.pad_script)
                self.pad_script = None
            return
        self.pad_script = self.send("Page.addScriptToEvaluateOnNewDocument", source=f"""
            window.__pad = {{ id: 'Xbox Wireless Controller (STANDARD GAMEPAD)', index: {index},
                connected: true, mapping: 'standard', axes: [0, 0, 0, 0],
                buttons: Array.from({{ length: 17 }}, () => ({{ pressed: false, touched: false, value: 0 }})),
                get timestamp() {{ return performance.now(); }},
                vibrationActuator: {{ type: 'dual-rumble', playEffect(type, p) {{
                    window.__rumbles.push([type, p.duration, p.strongMagnitude, p.weakMagnitude]);
                    return Promise.resolve('complete'); }} }} }};
            window.__rumbles = [];
            navigator.getGamepads = () => {{ const a = [null, null, null, null]; a[window.__pad.index] = window.__pad; return a; }};
        """)["identifier"]

    def pad(self, name, down):
        self.eval(f"(b => {{ b.pressed = {str(down).lower()}; b.touched = b.pressed; b.value = b.pressed ? 1 : 0; }})"
                  f"(window.__pad.buttons[{self.PAD[name]}])")

    def pad_tap(self, name, seconds=0.1):
        self.pad(name, True)
        self.wait(seconds)
        self.pad(name, False)
        self.wait(0.05)

    def stick(self, x, y):
        self.eval(f"window.__pad.axes[0] = {x}; window.__pad.axes[1] = {y};")

    def controls(self):
        return self.eval("window.__ship.controls.state")

    def state(self):
        return self.eval("""(() => { const s = window.__ship, p = s.player;
            return { mode: s.mode, x: Math.round(p.x), y: Math.round(p.y), tangerines: s.save.tangerines,
                     lunging: s.isLunging(), safe: s.isSafe(), activated: s.save.activated.slice() }; })()""")

    def teleport(self, x, y, route="inside"):
        self.eval(f"window.__ship.spawnAt({{x: {x}, y: {y}, route: '{route}'}})")
        self.wait(0.3)

    def shot(self, name):
        OUT.mkdir(exist_ok=True)
        if self.taken:
            # (Stepped, nothing is drawn until a picture is wanted: one frame, drawn.)
            self.advance(FRAME, draw=True)
        data = self.send("Page.captureScreenshot", format="png")["data"]
        path = OUT / f"{name}.png"
        path.write_bytes(base64.b64decode(data))
        return path

    def close_up(self, name, x, y, w=240, h=120, zoom=4, deck=None):
        """A close look at a spot (`name`-z.png): the camera on (x, y), the middle w x h game px of
        the view enlarged `zoom` times, hard-edged. `deck`: cut that deck open though she is not on
        it. What every placed person and thing is checked in (CLAUDE.md, "Looking closely")."""
        from PIL import Image
        cut = "null" if deck is None else str(deck)
        self.eval(f"(() => {{ const s = window.__ship, c = s.cameras.main; s.viewOverride = {cut}; c.stopFollow(); c.centerOn({x}, {y}); }})()")
        self.wait(0.8 if deck is not None else 0.4)
        img = Image.open(self.shot(name))
        # (The canvas is fitted into the window, smaller than it: a game px is its width / 480 on
        # the screenshot, about 1.7 px, and its middle is the canvas's, not the window's.)
        r = self.eval("(r => [r.left, r.top, r.width, r.height, window.innerWidth])(document.querySelector('canvas').getBoundingClientRect())")
        s = img.width / r[4]
        k = r[2] * s / 480
        mx, my = (r[0] + r[2] / 2) * s, (r[1] + r[3] / 2) * s
        out = OUT / f"{name}-z.png"
        img.crop((int(mx - w / 2 * k), int(my - h / 2 * k), int(mx + w / 2 * k), int(my + h / 2 * k)))            .resize((w * zoom, h * zoom), Image.NEAREST).save(out)
        self.eval("(() => { const s = window.__ship, c = s.cameras.main; s.viewOverride = null;"
                  " c.startFollow(s.player, true, 0.15, 0.15); c.setFollowOffset(0, s.player.height / 2); })()")
        return out

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            self.ws.close()
        except Exception:
            pass
        finally:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.httpd.shutdown()
            shutil.rmtree(self.profile, ignore_errors=True)


def wait(seconds):
    """A wait in a scenario: game time stepped, or real time (`--real`, `REAL_TIME`)."""
    if Browser.current:
        Browser.current.wait(seconds)
    else:
        time.sleep(seconds)


def now():
    """The clock a scenario's deadlines are read on (seconds): the stepped clock, or real time."""
    return Browser.current.now() if Browser.current else time.time()


# --- Scenarios -----------------------------------------------------------------------------------
# Positions come from the map builder (tools/build_ship_map.py), in metres from the bow.

D4, D5, D6, D7, D8, D9, D10, D11, D12 = (floor_y(d) for d in (4, 5, 6, 7, 8, 9, 10, 11, 12))
D3 = floor_y(3)
SPAWN_X = exact_x(CREW_DECK["cabin"])       # the start: her crew cabin's door on deck 3
CORE_L = col(CORES["forward"][0]) * TILE + 4 * TILE       # forward core: the 4-5 flight's foot
LADDER_X = (col(FUNNEL[0]) - 3) * TILE + TILE // 2        # the funnel ladder, deck 12 to the roof
ROOF_Y = ROOF_ROW * TILE


def check(cond, label, detail=""):
    print(("  ok    " if cond else "  FAIL  ") + label + (f"  ({detail})" if detail else ""))
    return cond


def scenario_boot(b):
    # (Straight into the game: the welcome screen and the intro have their own scenario, `intro`.)
    b.open("?reset&play", start=None)
    wait(0.5)
    s = b.state()
    b.shot("spawn")
    # (A sheet wider or taller than a texture may be is drawn as a black box, and nothing else
    # fails: her own sheet did, at 17,472 px, with every test passing. 8,192 is safe everywhere.)
    big = b.eval("""Object.values(window.__ship.textures.list).flatMap(t => t.source.map(s => [t.key, s.width, s.height]))
        .filter(([k, w, h]) => w > 8192 || h > 8192)""")
    check(not big, "no texture is larger than 8192 px a side", big)
    ok = (not big) and check(s["mode"] == "play" and s["y"] == D3 and abs(s["x"] - SPAWN_X) < 4,
                 "spawns standing on deck 3 at her crew cabin's door", s)
    # The side is painted (step 11): its tiles are many different ones, and each of them that is
    # cut away with its deck is known to the game as one that is.
    kinds = b.eval("""(s => { const ids = new Set(); s.exteriorLayer.forEachTile(t => { if (t.index > 0) ids.add(t.index); });
        return [ids.size, s.cutIds.size, s.map.tilesets[0].total]; })(window.__ship)""")
    ok &= check(kinds[0] > 300 and kinds[1] > 100 and kinds[2] >= kinds[0], "the ship's side is painted: its tiles are of many kinds", kinds)
    # From outside (O), what stands inside a deck in front of her is behind the closed side.
    b.tap("o")
    wait(0.8)
    fronts = b.eval("(s => [!!s.overview, (s.insideFronts || []).length, (s.insideFronts || []).filter(f => f.item.alpha > 0.01).length])(window.__ship)")
    b.shot("outside-view")
    ok &= check(fronts[0] and fronts[1] >= 2 and fronts[2] == 0, "in the outside view nothing inside shows through the closed side", fronts)
    b.tap("o")
    wait(0.5)
    ok &= check(not b.eval("!!window.__ship.overview") and b.state()["mode"] == "play", "and O again is back in the game")
    return ok


def scenario_deck3(b):
    """The start (the user, 2026-11-14): deck 3's crew corridor, her cabin behind the door marked
    Crew, the service ladder up to deck 4. Nothing says what to do."""
    S = "window.__ship"
    a, z = (exact_x(m) for m in CREW_DECK["span"])
    ladder = x_of(CREW_DECK["ladder"])
    b.open("?reset&play", start=None)
    wait(0.8)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == D3 and abs(s["x"] - SPAWN_X) < 4, "the game starts on deck 3 at her cabin's door", s)
    ok &= check(s["activated"] == ["cp_crew"], "that door is the first checkpoint, lit from the start", s["activated"])
    ok &= check(b.eval(f"{S}.viewDeck") == 3 and b.eval(f"{S}.shellAlpha[3]") < 0.05, "the corridor's side is cut open round her")
    ok &= check(1 in save_list(b, "regions"), "deck 3 is region 1's", save_list(b, "regions"))
    ok &= check(not alert(b), "nothing pops up to say what to do", alert(b))
    b.shot("deck3-start")
    # Her cabin: in with E, out with E.
    b.tap("e")
    wait(1.0)
    ok &= check(route(b) == "crewcabin", "E at the door marked Crew: her cabin", route(b))
    b.shot("deck3-cabin")
    # The bowl on her desk (the user, 2026-11-15): its three tangerines are real, hers to take.
    bowl = b.eval(f"{S}.tangerines.filter(t => t.id.startsWith('tan_3_bowl') && t.sprite.visible && t.route === 'crewcabin').map(t => ({{ id: t.id, x: t.sprite.x }}))")
    ok &= check(len(bowl) == 3, "three tangerines in the bowl on her desk", bowl)
    door = b.state()["x"]
    bx = sum(e["x"] for e in bowl) / max(1, len(bowl))
    way = "right" if bx > door else "left"
    hold_until(b, way, lambda s: abs(s["x"] - bx) < 3, 6)
    wait(0.3)
    s = b.state()
    ok &= check(s["tangerines"] == 3 and all(e["id"] in save_list(b, "collected") for e in bowl), "walked to them: all three taken, the count 3", s)
    b.shot("deck3-bowl-empty")
    hold_until(b, "left" if way == "right" else "right", lambda s: abs(s["x"] - door) < 4, 6)
    b.tap("e")
    wait(1.0)
    s = b.state()
    ok &= check(route(b) == "inside" and s["y"] == D3 and s["mode"] == "play", "and E at its door again: back in the corridor", s)
    # A bulkhead at each end; no stairs and no lift come down here.
    b.hold("left", 5.0)
    s = b.state()
    ok &= check(a + 16 <= s["x"] < a + 40 and s["y"] == D3, "the forward bulkhead stops her", (s["x"], a))
    b.shot("deck3-forward")
    hold_until(b, "right", lambda s: s["x"] >= ladder + 60, 12)
    b.hold("right", 1.2)
    s = b.state()
    ok &= check(z - 40 < s["x"] <= z - 16 and s["y"] == D3, "and the aft one", (s["x"], z))
    b.shot("deck3-aft")
    ok &= check(b.eval(f"{S}.lifts.every(l => l.floors.every(f => f.deck >= 4))"), "no lift comes down to deck 3")
    # The way up: the service ladder behind its door.
    b.teleport(ladder, D3)
    b.tap("e")
    wait(0.4)
    b.hold("up", 0.3)
    ok &= check(b.state()["mode"] == "trunk", "E at the ladder's door, then up: she is on the ladder", b.state())
    hold_until(b, "up", lambda s: s["y"] <= D4, 6)
    b.hold("left", 0.5)
    wait(0.9)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D4, "up the ladder and out of its door on deck 4", s)
    ok &= check(b.eval(f"{S}.shellAlpha[3]") > 0.95 and b.eval(f"{S}.shellAlpha[4]") < 0.05, "deck 3 is closed again under her, deck 4 open")
    b.shot("deck3-up-on-4")
    return ok


def scenario_intro(b):
    """The welcome screen, the start sequence and the intro (docs/intro.md, src/intro.js): the
    menu and its two buttons, the camera's way from the sun to her cabin's door, her coming out
    a few steps to the left, the game handed over, and its one hint the first time she walks past
    her door; her cabin's mirror; the short one for a game
    under way; Esc; `?play` past it all."""
    S, I = "window.__ship", "window.__ship.intro"
    menu = f"[{I}.titleText, ...{I}.buttons.map(q => q.text)]"
    b.open("?reset", start=None)
    ok = check(b.eval(f"{I}.stage") == "welcome" and b.eval(f"{I}.full"), "a new game opens on the welcome screen", b.eval(f"{I}.stage"))
    ok &= check(b.eval(menu) == ["BUMBUSIK", "PLAY", "LANGUAGE"], "the game's name and two buttons, PLAY and LANGUAGE", b.eval(menu))
    drawn = b.eval(f"[{I}.title, ...{I}.buttons.map(q => q.label)].map(o => o.texture.key + ':' + (o.width > 20))")
    ok &= check(drawn == ["menu-title:true", "menu-play:true", "menu-language:true"] and b.eval(f"{I}.buttons[0].plate.frame.name") == "plate",
                "in the menu's own lettering, on its plates", drawn)
    ok &= check(b.eval(f"!{S}.uiCam.visible && !{S}.player.visible && {S}.mode") == "scripted", "no HUD, no player, no controls yet")
    ok &= check(b.eval(f"!!{I}.blur && {I}.shade.alpha > 0.2"), "the sky behind is dimmed and out of focus")
    sun = b.eval(f"(c => [Math.abs(c.midPoint.x - {I}.sunX) < 30, Math.abs(c.midPoint.y - {I}.sunY) < 30])({S}.cameras.main)")
    ok &= check(sun == [True, True], "the sun is in the middle of the screen", sun)
    b.shot("intro-welcome")
    b.hold("right", 0.5)
    ok &= check(b.eval(f"{I}.stage") == "welcome" and b.eval(f"{I}.T") == 0, "the movement keys start nothing")
    b.tap("down")
    b.tap("enter")
    wait(0.2)
    ok &= check(b.eval(menu) == ["БУМБУСІК", "ГРАТИ", "МОВА"], "LANGUAGE switches to Ukrainian", b.eval(menu))
    b.shot("intro-welcome-uk")
    b.tap("enter")
    wait(0.2)
    ok &= check(b.eval(menu)[1:] == ["PLAY", "LANGUAGE"] and b.eval("window.__lang.language()") == "en", "and back to English", b.eval(menu))
    b.tap("up")
    b.tap("enter")
    wait(1.2)
    ok &= check(b.eval(f"{I}.stage") == "running" and b.eval(f"{I}.T") > 0.8, "PLAY starts the sequence")
    ok &= check(b.eval(f"{I}.title.alpha") == 0 and b.eval(f"{I}.shade.alpha") < 0.36, "the menu is gone, the shade lifting", b.eval(f"{I}.shade.alpha"))
    wait(1.6)
    ok &= check(b.eval(f"!{I}.blur && {I}.shade.alpha === 0"), "the sky is in focus and at its full brightness")

    def at(part, k=0.5):
        b.eval(f"{I}.seek('{part}', {k})")
        wait(0.5)
        return b.eval(f"(c => ({{ x: c.midPoint.x, y: c.midPoint.y, z: c.zoom }}))({S}.cameras.main)")

    sky, sea = at("sky"), at("sea")
    ok &= check(sea["y"] > sky["y"] + 2000 and abs(sea["x"] - sky["x"]) < 20, "the camera moves down to the sea", (sky, sea))
    water = b.eval(f"(c => ({S}.waterY - c.worldView.y) / c.worldView.height)({S}.cameras.main)")
    ok &= check(0.55 < water < 0.9, "the horizon and the sea are in the picture", water)
    b.shot("intro-sea")
    still = f"[...{S}.backdrop.layers.map(l => l.s.tilePositionX), {S}.backdrop.clouds.tilePositionX, ...{I}.clouds.map(c => c.x), {I}.sun.x]"
    before = b.eval(still)
    wait(1.2)
    ok &= check(b.eval(still) == before, "the islands, the clouds and the sun hold still together: nothing drifts past the sun")
    ship = at("ship")
    ok &= check(ship["x"] > sea["x"] + 8000 and abs(ship["y"] - sea["y"]) < 20, "then right, to the ship", (sea, ship))
    whole = b.eval(f"(v => v.x < {S}.hullMinX && v.right > {S}.hullMaxX)({S}.cameras.main.worldView)")
    ok &= check(whole and b.eval(f"{S}.fromAfar && {S}.shellAlpha['3']") == 1 and b.eval(f"{S}.deckDim.shown") == 0,
                "the whole ship is in view, every deck closed, nothing dimmed")
    t_sea, t_right = b.eval(f"{I}.parts.find(q => q.name === 'sea').len"), b.eval(f"{I}.parts.find(q => q.name === 'right').from")
    ok &= check(t_sea <= 0.6, "the camera goes right soon after the sea has come into view", (t_sea, t_right))
    at("dive", 0.86)         # (its side is opening while the zoom goes from 1.6 to 1.99)
    mid = b.eval(f"[{S}.shellAlpha['3'], {S}.deckDim.shown]")
    ok &= check(0 < mid[0] < 1 and abs((1 - mid[0]) - mid[1]) < 0.25, "the dark round deck 3 comes on as its side opens", mid)
    b.shot("intro-ship")
    corridor = at("corridor")
    ok &= check(abs(corridor["z"] - 2) < 0.01 and abs(corridor["x"] - SPAWN_X) < 2 and abs(corridor["y"] - (D3 - 29.5)) < 1
                and b.eval(f"{S}.shellAlpha['3']") == 0 and b.eval(f"{S}.deckDim.shown") == 1,
                "the camera zooms in on deck 3 and stops at the game's scale, on her cabin's door, the ship dim round the deck",
                (corridor, b.eval(f"{S}.shellAlpha['3']"), b.eval(f"{S}.deckDim.shown")))
    door = f"{S}.world.rooms.crewcabin.outside[0].frame.name"
    ok &= check(b.eval(f"{S}.route") == "inside" and not b.eval(f"{S}.player.visible") and b.eval(door) == "door-crew",
                "the door marked CREW, shut, nobody about")
    b.shot("intro-corridor")
    at("step", 0.6)
    ok &= check(b.eval(door) == "door-crew-ajar" and not b.eval(f"{S}.player.visible"), "her door opens", b.eval(door))
    at("walk", 0.05)
    her = b.eval(f"(p => ({{ shown: p.visible && p.alpha === 1, left: p.flipX, x: p.x, leaf: !!{I}.leaf && {I}.leaf.visible && {I}.leaf.depth > p.depth }}))({S}.player)")
    ok &= check(b.eval(door) == "door-crew-ajar" and her["shown"] and her["left"] and her["leaf"] and SPAWN_X - 10 < her["x"] < SPAWN_X,
                "she walks out of it to the left, its open leaf in front of her", (b.eval(door), her))
    b.shot("intro-step")
    at("walk", 0.6)
    ok &= check(b.eval(door) == "door-crew" and not b.eval(f"{I}.leaf.visible"), "the door shuts behind her")
    her = f"(p => ({{ x: p.x, left: p.flipX, walk: {S}.cache.json.get('her-meta').anims.walk.includes(p.frame.name), stand: p.frame.name === {S}.herFrames.stand, cam: {S}.cameras.main.midPoint.x }}))({S}.player)"
    at("walk", 0.4)
    w = b.eval(her)
    ok &= check(w["left"] and w["walk"] and SPAWN_X - 56 < w["x"] < SPAWN_X - 10, "she walks a few steps to the left", w)
    at("walk", 1)
    w = b.eval(her)
    ok &= check(w["left"] and w["stand"] and abs(w["x"] - (SPAWN_X - 56)) < 1 and abs(w["cam"] - w["x"]) < 1,
                "and stops, the camera on her", w)
    clip, frames = b.eval(f"{S}.cache.json.get('her-meta').anims.badge"), set()
    for k in (0.1, 0.3, 0.5, 0.7, 0.9):
        at("badge", k)
        frames.add(b.eval(f"{S}.player.frame.name"))
    ok &= check(len(frames) >= 4 and frames <= set(clip), "she straightens her name badge", sorted(frames))
    b.shot("intro-badge")
    at("turn", 0.9)
    ok &= check(b.eval(f"{S}.player.frame.name === {S}.herFrames.stand && {S}.player.flipX"), "and turns to go, to the left")
    ok &= check(b.eval(f"{S}.cameras.cameras.length") == 4 and abs(b.eval(f"{S}.cameras.main.midPoint.y") - (D3 - 29.5)) < 1,
                "the camera has not moved since it stopped: no close-up")
    b.eval(f"{I}.seek('turn', 0.5, false)")
    b.wait_for(f"!{I}", timeout=6)
    wait(0.9)
    s = b.state()
    ok &= check(b.eval(f"{S}.mode") == "play" and b.eval(f"{S}.cameras.main.zoom") == 2 and b.eval(f"{S}.uiCam.visible && {S}.uiCam.alpha === 1"),
                "the HUD comes up and the controls are hers", b.eval(f"{S}.mode"))
    ok &= check(b.eval(f"{S}.route") == "inside" and abs(s["x"] - (SPAWN_X - 56)) < 2 and s["y"] == D3
                and b.eval(f"{S}.player.visible && {S}.player.alpha === 1 && {S}.player.flipX"),
                "she stands in the corridor a few steps left of her door, turned to go on to the left", s)
    ok &= check(alert(b) == "← and → to move, Space to jump", "a word over her says how to move and jump", alert(b))
    ok &= check(b.eval(f"{S}.cameras.cameras.length") == 3 and b.eval(f"{S}.save.intro") is True, "nothing of the intro is left; it is saved as seen",
                b.eval(f"{S}.cameras.cameras.length"))
    b.shot("intro-play")
    b.eval(f"{S}.controls.device = 'pad'")
    wait(0.1)
    ok &= check(alert(b) == "Left stick to move, A to jump", "with the controller in use, in its buttons", alert(b))
    b.shot("intro-play-pad")
    b.eval(f"{S}.controls.device = 'keys'")
    wait(0.1)
    ok &= check(alert(b) == "← and → to move, Space to jump", "and back in the keys'", alert(b))
    wait(5.4)
    ok &= check(not alert(b), "it goes after a few seconds", alert(b))
    hold_until(b, "right", lambda q: q["x"] >= SPAWN_X - 30, timeout=3)
    ok &= check(not alert(b), "nothing short of her door", alert(b))
    hold_until(b, "right", lambda q: q["x"] >= SPAWN_X - 12, timeout=3)
    ok &= check(alert(b) == "E to interact" and b.state()["x"] < SPAWN_X, "at her door, a word over her says what E is for", (alert(b), b.state()["x"]))
    b.shot("intro-hint")
    wait(6.2)
    ok &= check(not alert(b), "the hint goes after a few seconds")
    hold_until(b, "left", lambda q: q["x"] <= SPAWN_X - 40, timeout=3)
    hold_until(b, "right", lambda q: q["x"] >= SPAWN_X + 40, timeout=3)
    wait(0.1)
    ok &= check(not alert(b), "and only the first time", alert(b))

    # Her cabin: she stops in front of her mirror; E there turns her to it and she fixes her hair, once a press.
    b.eval(f"{S}.spawnAt({{ x: {SPAWN_X}, y: {D3} }})")
    wait(0.3)
    b.tap("e")
    wait(1.2)
    x0 = b.eval(f"{S}.world.rooms.crewcabin.def.x0")
    ok &= check(b.eval(f"{S}.route") == "crewcabin", "E at her door: into her cabin")
    b.eval(f"window.__hair = 0; {S}.player.on('animationstart', a => {{ if (a.key === 'her-hair') window.__hair++; }})")
    b.hold("left", 1.2)
    stop = b.state()["x"] - x0
    ok &= check(35 <= stop <= 37, "she stops in front of her mirror", stop)
    wait(3.0)
    ok &= check(b.eval("window.__hair") == 0, "standing there alone does nothing", b.eval("window.__hair"))
    b.tap("right")
    wait(0.3)
    off = b.state()["x"] - x0 - 36
    ok &= check(not b.eval(f"{S}.player.flipX") and off < 14, "turned from it, a step off", off)
    b.tap("e")
    wait(0.4)
    ok &= check(b.eval("window.__hair") == 1 and b.eval(f"{S}.player.flipX"), "E: she turns to it and fixes her hair", b.eval("window.__hair"))
    b.shot("mirror-hair")
    wait(4.0)
    ok &= check(b.eval("window.__hair") == 1, "once a press", b.eval("window.__hair"))
    b.tap("e")
    wait(0.4)
    ok &= check(b.eval("window.__hair") == 2, "and again at the next", b.eval("window.__hair"))
    wait(3.0)
    b.hold("right", 1.0)
    b.tap("e")
    wait(0.6)
    ok &= check(b.eval("window.__hair") == 2, "away from it, E does not", b.eval("window.__hair"))
    ok &= check(b.errors == [], "no errors", b.errors)

    # A game under way: the same welcome, a shorter way in, to wherever she is.
    b.eval(f"""(s => {{ const c = s.checkpoints.find(c => c.id === 'cp_gangway'); s.progress.openAll = true; s.spawnAt(c); }})({S})""")
    wait(0.6)
    b.wait_for(f"{S}.save.lastCheckpoint === 'cp_gangway'", timeout=4)
    b.open("", start=None)
    ok &= check(b.eval(f"{I}.stage") == "welcome" and b.eval(f"{I}.full") is False, "a game under way: the welcome screen, and the short way in")
    b.tap("enter")
    wait(0.5)
    b.eval(f"{I}.seek('near', 0.5, false)")
    b.wait_for(f"!{I}", timeout=8)
    wait(1.0)
    s = b.state()
    ok &= check(b.eval(f"{S}.mode") == "play" and abs(s["y"] - D4) < 2 and b.eval(f"{S}.shellAlpha['4']") == 0,
                "it ends where she was: the gangway lobby, deck 4 open", s)
    b.shot("intro-back")
    # Esc ends it at once.
    b.open("", start=None)
    b.tap("enter")
    wait(0.6)
    b.tap("escape")
    wait(1.0)
    ok &= check(b.eval(f"!{I} && {S}.mode") == "play" and b.eval(f"{S}.uiCam.visible"), "Esc ends the intro at once")
    # And ?play goes past the welcome and the intro.
    b.open("?reset&play", start=None)
    ok &= check(b.eval(f"{I}") is None and b.eval(f"{S}.mode") == "play" and b.eval(f"{S}.cameras.cameras.length") == 3, "?play goes straight into the game")
    ok &= check(b.errors == [], "no errors", b.errors)
    return ok


def scenario_lang(b):
    """The two languages (the user, 2026-11-14): every text the game says has an English and a
    Ukrainian version; `?lang=` sets one for a session. And no hint is left to translate."""
    L, S = "window.__lang", "window.__ship"
    texts = "[window.__ship.intro.titleText, ...window.__ship.intro.buttons.map(q => q.text)]"
    # (Every letter of the menu's words has its shape in the menu's lettering: src/pixeltext.js.)
    lost = "(i => [['T', i.titleText], ...i.buttons.map(q => ['S', q.text])].flatMap(([f, s]) => window.__pixeltext.missing(window.__ship, f, s)))(window.__ship.intro)"
    b.open("?reset")
    keys = b.eval(f"{L}.KEYS")
    ok = check(sorted(keys["en"]) == sorted(keys["ua"]) and len(keys["en"]) > 20, "every text has both versions",
               sorted(set(keys["en"]) ^ set(keys["ua"])))
    ok &= check(b.eval(f"{L}.language()") == "en" and b.eval(texts) == ["BUMBUSIK", "PLAY", "LANGUAGE"] and b.eval(lost) == [], "English is the default: the welcome screen", (b.eval(texts), b.eval(lost)))
    b.shot("lang-title-en")
    b.open("?reset&lang=ua")
    ok &= check(b.eval(f"{L}.language()") == "ua" and b.eval(texts) == ["БУМБУСІК", "ГРАТИ", "МОВА"] and b.eval(lost) == [], "?lang=ua: the welcome screen in Ukrainian, every letter drawn", (b.eval(texts), b.eval(lost)))
    b.shot("lang-title-uk")
    said = {}
    for code in ("en", "ua"):
        b.open(f"?reset&play&lang={code}")
        wait(0.4)
        b.eval(f"{S}.lockedUntil = 0; {S}.showLocked('deck')")
        lock = alert(b)
        b.eval(f"{S}.alert.setVisible(false); {S}.lockedUntil = 0; {S}.world.say({L}.t('say.oops'), 600)")
        said[code] = (lock, alert(b), b.eval(f"{L}.t('fright.startled')"), b.eval(f"{L}.t('win.tally', 1, 2, 3, 4, 5, 14)"))
        wait(0.7)
    ok &= check(said["en"][:3] == ("🔒 Deck card", "Oops!", "Oh, sorry!"), "a lock, her word, a fright: in English", said["en"])
    ok &= check(said["ua"][:3] == ("🔒 Палубна картка", "Ой!", "Ой, вибачте!"), "and in Ukrainian", said["ua"])
    ok &= check("1 of 2" in said["en"][3] and "1 з 2" in said["ua"][3], "the win screen's tally takes its numbers in both", (said["en"][3], said["ua"][3]))
    ok &= check(b.eval(f"{S}.bubble.text") == "Кісюнічка!!!", "her shout is hers in both")
    ok &= check(b.eval(f"typeof {S}.world.hint + typeof {S}.world.glyph") == "undefinedundefined", "no hint and no key's cap is left in the game")
    b.open("?reset")
    ok &= check(b.eval(f"{L}.language()") == "en", "a language set by the link is not kept")
    return ok


def scenario_run_jump(b):
    b.open("?reset&play")
    wait(0.4)
    x0 = b.state()["x"]
    b.hold("right", 0.6)
    s = b.state()
    ok = check(s["x"] > x0 + 30, "runs right", f"{x0} -> {s['x']}")
    b.key("space", True)
    wait(0.25)
    peak = b.state()["y"]
    b.key("space", False)
    wait(0.8)
    ok &= check(peak < D4 - 30, "jumps", f"y at 0.25s {peak}")
    ok &= check(b.state()["y"] == D4, "lands back on deck 4", b.state())
    return ok


def scenario_stairs(b):
    b.open("?reset&play")
    b.teleport(CORE_L, D4)
    b.hold("up", 1.4)
    b.shot("stairs-climbing")
    b.key("up", True)
    wait(3.0)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == D5, "holding up climbs to deck 5", s)
    locked = blocked(b)
    said = b.eval("window.__ship.alert.visible && window.__ship.alert.text")
    shrug = b.eval("(() => { const s = window.__ship; return s.time.now - (s.shrugAt ?? -1e9) < 3000; })()")
    b.shot("stairs-locked")
    b.key("up", False)
    ok &= check(bool(locked) and "SEARCH" in locked, "and stops there: the flight up is roped off", locked)
    ok &= check(shrug and not said, "nothing over her: she turns to us and shrugs, the sign lit", (shrug, said))
    b.hold("down", 3.0)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D4, "holding down carries her back to deck 4", s)
    b.open("?reset&play&cards=all")
    b.teleport(CORE_L, D4)
    # (Held until she is there: the climb takes about nine seconds, a little more on a slow machine.)
    b.key("up", True)
    end = now() + 14
    while now() < end and b.state()["y"] > floor_y(8):
        wait(0.05)
    b.key("up", False)
    s = b.state()
    ok &= check(s["y"] <= floor_y(8), "with every card she climbs on past deck 6", s)
    return ok


def scenario_ladder(b):
    b.open("?reset&play")
    # (The technical ladder is chained off until the engineer has had his coffee: region 8.)
    b.eval("window.__ship.progress.setFlag('engineer')")
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
    wait(0.1)
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
    wait(0.5)
    s = b.state()
    ok &= check(s["mode"] == "trunk" and s["y"] == D5, "settles at the middle door, deck 5", s)
    ok &= check(trunk_door(b, "midships", 5, "up") == "arrow-up-on"
                and trunk_door(b, "midships", 5, "down") == "arrow-down-on", "whose arrows show both ways")
    b.key("left", True)
    wait(0.1)
    b.shot("trunk-stepping-out")
    wait(0.3)
    b.key("left", False)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D5 and s["x"] < x - 20, "steps out there", s)

    # Climbing on past a door: it opens as she reaches it and shuts again once she has gone by.
    b.teleport(x, D4)
    b.tap("e")
    b.key("up", True)
    wait(1.85)
    passing = trunk_door(b, "midships", 5)
    wait(2.0)
    b.key("up", False)
    s = b.state()
    ok &= check(passing and not trunk_door(b, "midships", 5) and trunk_door(b, "midships", 6)
                and s["mode"] == "trunk" and s["y"] == D6,
                "the deck 5 door opens and shuts as she climbs past it to deck 6", s)

    # One-way: shut from below until she has come down through it.
    x = trunk_x("theatre")
    b.teleport(x, D4)
    b.tap("e")
    wait(0.1)
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
    wait(0.1)
    ok &= check(trunk_door(b, "theatre", 4), "it does")

    # Card-locked.
    b.teleport(trunk_x("magnums"), D6)
    b.tap("e")
    wait(0.1)
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
    wait(0.5)
    ok = check(b.state()["mode"] == "lift" and b.eval("!!window.__ship.liftPanel"), "E opens the doors and shows the panel")
    for _ in range(4):
        b.tap("up")
        wait(0.1)  # separate presses, not one long one
    ok &= check(lift_cursor(b) == 5, "in region 1, ↑ picks no higher than deck 5", lift_cursor(b))
    b.shot("lift-panel")
    b.tap("e")
    wait(0.1)
    ok &= check(not b.eval("window.__ship.liftPanel"), "the panel goes once the deck is chosen")
    wait(0.8)
    b.shot("lift-riding")
    wait(1.8)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D5 and abs(s["x"] - LIFT_X) < 2, "E rides it up to deck 5", s)
    b.shot("lift-arrived")
    b.hold("right", 0.5)
    wait(0.4)
    ok &= check(b.eval("window.__ship.lifts[0].floors.every(f => f.leaves.open === 0)"), "the doors shut once she steps away")

    # Called from deck 4 while it waits on deck 5, the car comes down to her: she stays put.
    b.teleport(LIFT_X, D4)
    b.tap("e")
    ys = []
    for _ in range(12):
        wait(0.15)
        ys.append(b.state()["y"])
    ok &= check(set(ys) == {D4} and b.eval("window.__ship.liftRun.choosing"),
                "called from another deck, the car comes to her and she stays put", sorted(set(ys)))
    b.tap("left")
    wait(0.6)

    b.teleport(LIFT_X, D5)
    b.tap("e")
    b.wait_for("window.__ship.liftRun && window.__ship.liftRun.choosing", timeout=4)  # it comes up first
    b.tap("left")
    wait(0.1)
    ok &= check(b.state()["mode"] == "play" and not b.eval("window.__ship.liftPanel"), "←/→ backs out of the panel")

    # The glass elevator: on deck 5 to start with, it comes up to fetch her on deck 7.
    b.open("?reset&play&cards=all")
    b.teleport(GLASS_X, walk_y(7))
    b.tap("e")
    wait(0.6)
    b.shot("glass-coming")
    wait(1.6)
    ok &= check(b.eval("window.__ship.liftRun.choosing && window.__ship.lifts.find(l => l.glass).carY") == walk_y(7),
                "the glass car comes up to her deck")
    for _ in range(2):
        b.tap("up")
        wait(0.1)
    ok &= check(lift_cursor(b) == 9, "with every card she can pick deck 9", lift_cursor(b))
    b.tap("e")
    wait(1.2)
    b.shot("glass-riding")
    wait(1.8)
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
    wait(0.3)
    b.hold("right", 7.4)
    b.tap("e")
    wait(0.3)
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
    wait(1.0)
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
    wait(0.4)
    b.key("right", False)
    wait(0.8)
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
    wait(0.8)
    s = b.state()
    ok &= check(route() == "inside" and s["mode"] == "play" and s["x"] == door, "E at a door takes her inside", (route(), s))
    b.shot("promenade-inside")
    b.tap("e")
    wait(0.8)
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
    wait(0.8)
    s = b.state()
    ok &= check(route() == "cabin" and s["mode"] == "play" and s["x"] == door, "E at the open door takes her in", (route(), s))
    b.shot("cabin-desk")
    b.hold(["right"], 0.6)
    wait(0.3)
    b.hold(["right"], 2.0)
    s = b.state()
    ok &= check(route() == "cabin" and door < s["x"] < door + 200 and s["y"] == floor_y(8), "the cabin's far wall holds her", s)
    b.shot("cabin-inside")
    b.hold(["left"], 2.0)
    s = b.state()
    ok &= check(door - 60 < s["x"] < door and s["y"] == floor_y(8), "and so does its near wall", s)
    # She can jump onto the bed (its top 32px over the floor) and stand there.
    b.eval(f"window.__ship.spawnAt({{x: {door + 50}, y: {floor_y(8)}, route: 'cabin'}})")
    wait(0.4)
    b.key("right", True)
    b.tap("space")
    wait(0.5)
    b.key("right", False)
    wait(0.8)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == floor_y(8) - 32, "she jumps onto the bed and stands on it", s)
    b.shot("cabin-bed")
    # Standing still on it a second, she bounces for joy; any key and she stops, still on the bed.
    wait(1.4)
    ys = []
    for _ in range(12):
        ys.append(b.state()["y"])
        wait(0.05)
    ok &= check(b.state()["mode"] == "scripted" and min(ys) < floor_y(8) - 32 - 3 and max(ys) == floor_y(8) - 32,
                "a second still on the bed: she bounces for joy, off it and back", ys)
    b.shot("cabin-bed-joy")
    b.tap("left")
    wait(0.5)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == floor_y(8) - 32, "a key stops it, her feet on the bed", s)
    b.teleport(door, floor_y(8))
    b.eval("window.__ship.route = 'cabin'")
    b.tap("e")
    wait(0.8)
    ok &= check(route() == "inside", "E at the door takes her back out", route())
    b.shot("cabin-door")
    # Its desk seen close (§4 2.4): E at it any time, the bare desk with nothing found, her things and his as found.
    desk = "(() => { const s = window.__ship; const k = s.textures.exists('desk-seen') && s.textures.get('desk-seen').getSourceImage(); return [!!s.viewing, k ? k.width : 0]; })()"
    for q, what in (("", "nothing found: the bare desk"), ("&keeps=flag,pick", "two found"), ("&did=catch,home&keeps=desk", "all eight, the day after")):
        b.open("?reset&play&at=cabin" + q)
        b.teleport(door + 51, floor_y(8))
        b.eval("window.__ship.route = 'cabin'")
        b.tap("e")
        wait(0.6)
        got = b.eval(desk)
        ok &= check(got == [True, 400], f"E at the desk shows it close ({what})", got)
        b.tap("e")
        wait(0.6)
        ok &= check(not b.eval("window.__ship.viewing"), "  and a key closes it", None)
    # Bumbot's bed seen close on the day after (§4 2.4, the user's): E by him from the floor, his things as found, the
    # bare bed with none; on the bed, by her seat 18 px from him, E is her reading. (Book 5, on the bed, taken first.)
    bed = desk.replace("desk-seen", "bed-seen")
    for q, what in (("", "none found: the bare bed"), ("&keeps=ball,car", "two found"), ("&keeps=bed", "all eight")):
        b.open("?reset&play&at=cabin&did=catch,home&books=5" + q)
        cat = b.eval("window.__ship.world.data.finale.home.catX")
        b.teleport(cat - 6, floor_y(8), route="cabin")
        b.tap("e")
        wait(0.6)
        got = b.eval(bed)
        ok &= check(got == [True, 400], f"E by Bumbot from the floor shows the bed close ({what})", got)
        b.tap("e")
        wait(0.6)
        ok &= check(not b.eval("window.__ship.viewing"), "  and a key closes it", None)
    b.teleport(door - 59 + 196, floor_y(8) - 32, route="cabin")
    b.tap("e")
    wait(1.0)
    ok &= check(b.eval("!!window.__ship.world.library.reading") and not b.eval("window.__ship.viewing"),
                "on the bed by him, E is her reading", None)
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
    wait(0.8)
    s = b.state()
    ok = check(route() == "linen" and s["x"] == door, "E at the crew door takes her in", (route(), s))
    b.shot("linen-inside")
    # (Mirrored 2026-11-23: its door at its aft end, the room forward of it; the near wall is aft of the door.)
    b.hold(["right"], 2.0)
    s = b.state()
    ok &= check(door < s["x"] < door + 60 and s["y"] == floor_y(9), "the room's near wall holds her", s)
    b.teleport(door, floor_y(9))
    b.eval("window.__ship.route = 'linen'")
    b.tap("e")
    wait(0.8)
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
    wait(2.5)    # the cut-away fades over from deck 4
    ok = check(shell("10") < 0.05 and shell("10:bridge") < 0.05, "from the corridor the bridge is in sight",
               (shell("10"), shell("10:bridge")))
    b.hold("left", 0.8)
    s = b.state()
    ok &= check(s["x"] > door, "the shut door stops her", s)
    b.tap("e")
    wait(0.2)
    ok &= check(b.eval(f"{bridge}.open"), "E opens it")
    # Well past the shutting distance (0.6 s left her right at it, and the door open: 2026-11-07).
    b.hold("left", 0.9)
    wait(1.0)
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
    wait(0.4)
    b.key("right", True)
    b.key("space", True)         # (held: a tap can come out as a cut-short hop on a slow machine)
    wait(0.4)
    b.key("space", False)
    wait(1.0)
    b.key("right", False)
    wait(0.8)
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
    b.eval("window.__ship.progress.setFlag('engineer')")
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
    wait(0.3)
    b.tap("down")
    wait(1.2)
    s = b.state()
    ok = check(s["mode"] == "play" and s["y"] == D11, "a one-deck drop into the pool area is fine", s)
    # (Between the pools she comes down on the hot tub's canopy: a roof she can stand on.)
    b.teleport(x_of(132.5), D12)
    wait(0.3)
    b.tap("down")
    wait(1.2)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D11 - 90, "over the hot tub she lands on its canopy", s)
    # Two decks: off deck 12's aft end, past deck 11, onto the deck 10 terrace below.
    b.teleport(x_of(245.5), D12)  # past deck 12's (233 m) and deck 11's (244 m) aft ends
    wait(0.6)
    b.shot("long-fall")
    s = b.state()
    ok &= check(s["mode"] == "scripted", "a two-deck fall is a scare", s)
    wait(2.0)
    s = b.state()
    ok &= check(s["mode"] == "play", "she comes back afterwards", s)
    return ok


def scenario_vacuum(b):
    b.open("?reset&play")
    b.teleport(x_of(120), D4)  # the deck 4 corridor the robot vacuum patrols
    b.eval(f"window.__ship.vacuums[0].sprite.x = {x_of(120) + 40}; window.__ship.vacuums[0].dir = -1")
    wait(0.8)
    b.shot("vacuum-scare")
    s = b.state()
    ok = check(s["mode"] == "scripted", "touching the vacuum is a scare", s)
    # (Head-on, 5a: she rides it off too, the other way, turned round onto it: the user, 2026-11-16.)
    ok &= check(b.eval("(g => !!g && g.flipX)(window.__ship.worldLayer.list.find(o => o.texture?.key === 'her-mishaps'))"),
                "head-on: she rides it off the way it was going")
    b.wait_for("window.__ship.mode === 'play'", timeout=6)
    s = b.state()
    ok &= check(s["mode"] == "play", "she comes back afterwards", s)
    # 5b: it catches her from behind as she stands: she rides it off down the corridor, out of the
    # screen (her with it in one picture, its own hidden, no smoke of a choked one), and is back.
    S, G = "window.__ship", "window.__ship.worldLayer.list.find(o => o.texture?.key === 'her-mishaps')"
    b.teleport(x_of(126), D4)
    b.eval(f"(v => {{ v.sprite.x = {x_of(126) - 60}; v.dir = 1; v.minX = {x_of(110)}; v.maxX = {x_of(145)}; }})({S}.vacuums[0]);"
           f" {S}.player.setFlipX(false)")
    b.wait_for(f"{S}.mode === 'scripted'", timeout=6)
    ok &= check(b.eval(f"{S}.lastMishap?.id") == "5b" and b.eval(f"!!{G} && !{S}.vacuums[0].sprite.visible && {S}.vacuums[0].alive"),
                "5b: from behind she rides it off (her with it in one picture; its own hidden)",
                b.eval(f"[{S}.lastMishap?.id, {G}?.anims.currentAnim?.key]"))
    b.wait_for(f"{S}.mode === 'play'", timeout=8)
    ok &= check(b.eval(f"!{G} && {S}.vacuums[0].sprite.visible && !{S}.vacuums[0].ridden && {S}.player.visible"),
                "5b: out of the screen, back at her checkpoint, the vacuum in its place")
    return ok


def scenario_dash(b):
    """D (docs/plan-three-uses.md §1.1): every press costs one tangerine. Before the lunge is learned,
    and with a tray, the cry alone: the porter stops and stands aside, and is deaf to a second cry a
    while. Learned, the lunge with it: through the luggage, the vacuum sent spinning, about a second
    long; a fright by contact refused during it, not after. With none on her, nothing."""
    S, P = "window.__ship", "window.__ship.world.people.byId.haz_porter"
    b.open("?reset&play")
    b.teleport(x_of(50), D4)
    wait(0.3)
    b.eval(f"{S}.save.tangerines = 4; {S}.refreshHud()")
    # The porter held at his forward end, facing her; she two metres from him.
    b.eval(f"(p => {{ p.x = p.walk.a; p.dir = -1; p.pausedUntil = 0; window.__ship.world.people.place(p); }})({P})")
    b.teleport(person(b, "haz_porter")["x"] - 100, D4)
    b.eval(f"{P}.pausedUntil = 0")
    b.tap("d")
    wait(0.15)
    b.shot("dash-cry-porter")
    s = b.state()
    ok = check(s["tangerines"] == 3 and not s["lunging"], "before the lunge is learned D is the cry alone, for one", s)
    ok &= check(b.eval(f"{S}.bubble.visible"), "her bubble: the cry")
    aside = b.eval(f"({P}.aside === true) && {P}.pausedUntil > {S}.time.now + 2000")
    ok &= check(aside, "the porter stops and stands aside", b.eval(f"[{P}.aside, {P}.pausedUntil - {S}.time.now]"))
    until = b.eval(f"{P}.pausedUntil")
    wait(0.8)
    b.tap("d")
    wait(0.15)
    ok &= check(b.state()["tangerines"] == 2, "a second cry costs another", b.state())
    ok &= check(b.eval(f"{P}.pausedUntil") == until, "and the porter is deaf to it", b.eval(f"{P}.pausedUntil - {until}"))
    # With a tray in her hands: the cry alone, even once the lunge is learned.
    b.eval(f"{S}.save.verbs.push('dash'); {S}.world.carryBox.take('lunch')")
    wait(0.8)
    b.tap("d")
    wait(0.15)
    s = b.state()
    ok &= check(s["tangerines"] == 1 and not s["lunging"], "with a tray: the cry alone, for one", s)
    b.eval(f"{S}.world.carryBox.drop()")
    # The lunge: deck 4's stacked luggage (30 m) ahead of her, the vacuum standing beyond it, both
    # within the second of it.
    b.teleport(x_of(33), D4)
    wait(0.3)
    b.eval(f"{S}.save.tangerines = 1; {S}.player.setFlipX(true)")
    b.eval(f"{S}.vacuums[0].sprite.x = {x_of(29)}; {S}.vacuums[0].speed = 0")
    t0 = b.eval(f"{S}.time.now")
    b.tap("d")
    wait(0.1)
    b.shot("dash-lunge")
    s = b.state()
    ok &= check(s["lunging"] and s["tangerines"] == 0, "learned: D cries out and lunges, for one", s)
    length = b.eval(f"{S}.lungeUntil") - t0
    ok &= check(900 <= length <= 1100, "the lunge lasts about a second", length)
    b.hold("left", 1.2)
    s = b.state()
    ok &= check("haz_luggage_4" in save_list(b, "broken") and s["x"] < x_of(29.5), "the lunge breaks through the luggage", (s, save_list(b, "broken")))
    ok &= check(b.eval(f"{S}.vacuums[0].asideUntil > 0") and s["mode"] == "play", "and sends the vacuum spinning", s)
    ok &= check(not s["lunging"], "and is over", s)
    # A fright by contact refused during it; none refused after.
    b.teleport(x_of(200), D4)
    b.eval(f"{S}.save.tangerines = 1")
    b.tap("d")
    wait(0.1)
    b.eval(f"{S}.scareContact({S}.player.x + 10, 'cart')")
    wait(0.1)
    ok &= check(b.state()["mode"] == "play", "in a lunge a bump is nothing", b.state())
    wait(1.5)
    b.eval(f"{S}.scareContact({S}.player.x + 10, 'cart')")
    wait(0.1)
    ok &= check(b.state()["mode"] == "scripted", "after it, a bump is a fright again", b.state())
    b.wait_for(f"{S}.mode === 'play'", timeout=6)
    # With none on her: nothing.
    b.eval(f"{S}.save.tangerines = 0")
    wait(0.7)
    b.tap("d")
    wait(0.1)
    s = b.state()
    ok &= check(not s["lunging"] and s["tangerines"] == 0 and not b.eval(f"{S}.time.now < {S}.bubbleUntil"),
                "with none: D does nothing", s)
    return ok


def scenario_pocket(b):
    """A hit is its gag whatever she carries (docs/plan-the-rest.md §3 1.2a; the user, 2026-11-19):
    with tangerines on her, a paper and a "Do Not Disturb" door are each her mishap
    and her checkpoint, the count as it was and nothing left lying; the porter walking into her tray
    spills it, the count as it was. Only a gull takes one: she ducks, blinks, keeps her place and her
    tray. (The rest: `mishaps`.) A fall is a fright, tangerines or not. A
    tangerine she gets flies to the count."""
    S, P = "window.__ship", "window.__ship.world.people.byId.haz_porter"
    b.open("?reset&play")
    # The porter at his aft end, walking forward her way; she stands in his path with her tray.
    b.teleport(x_of(50), D4)
    wait(0.3)
    b.eval(f"(p => {{ p.x = p.walk.b; p.dir = -1; p.pausedUntil = 0; window.__ship.world.people.place(p); }})({P})")
    b.teleport(person(b, "haz_porter")["x"] - 70, D4)
    b.eval(f"{S}.save.tangerines = 2; {S}.refreshHud(); {S}.world.carryBox.take('lunch'); {S}.player.setFlipX(false)")
    ok = check(wait_js(b, f"!{S}.world.carry", 8), "the porter walks into her tray, two tangerines on her")
    s = b.state()
    ok &= check(s["mode"] == "play" and s["tangerines"] == 2 and b.eval(f"{S}.loose.all.length") == 0,
                "the tray is spilled all the same, none lost, nothing lying", s)
    b.shot("pocket-spill")
    b.eval(f"{P}.pausedUntil = {S}.time.now + 600000")

    def hit(js, n=2, carry=None):
        b.teleport(x_of(48), D4)
        wait(0.3)
        b.eval(f"{S}.save.tangerines = {n}; {S}.refreshHud(); {S}.safeUntil = 0; {S}.flinchUntil = 0; {S}.player.setFlipX(false)")
        if carry:
            b.eval(f"{S}.world.carryBox.take('{carry}')")
        x = b.state()["x"]
        got = b.eval(f"{S}.scareContact({js})")
        wait(0.1)
        return got, x, b.state()

    def mishap(js, want, what):
        got, x, s = hit(js)
        r = check(got == want and s["mode"] == "scripted" and s["tangerines"] == 2 and b.eval(f"{S}.loose.all.length") == 0,
                  f"{what}, two on her: her mishap ({want}), none lost, nothing lying", (got, s))
        b.wait_for(f"{S}.mode === 'play'", timeout=12)
        s = b.state()
        return r & check(abs(s["x"] - x) > 100 and s["tangerines"] == 2, "then her checkpoint, still two", (x, s))
    # (The cart's and a door's hits, and a gull's with none on her, are the `mishaps` cases now, made
    # through their own movers: called from here with no ride, they played the built fall or the old
    # run-off, not their gags (§3 1.3, 2026-11-19).)
    ok &= mishap(f"{S}.player.x + 12, 'papers', {{ vx: -60 }}", "4a", "a paper at her front")
    got, x, s = hit(f"{S}.player.x + 12, 'dnd'")
    ok &= check(got == "23" and s["mode"] == "scripted" and s["tangerines"] == 2 and b.eval(f"{S}.player.anims.currentAnim?.key") != "her-apology",
                "a \"Do Not Disturb\" door: her tiptoe, no tangerine held out", (got, s))
    b.wait_for(f"{S}.mode === 'play'", timeout=12)
    # A gull takes one: she ducks, keeps her place and her tray.
    b.eval(f"window.__gull = {S}.add.image({S}.player.x + 30, {S}.player.y - 60, 'tangerine')")
    got, x, s = hit(f"{S}.player.x + 8, 'railgull', {{ snatch: window.__gull }}", carry="lunch")
    clip = b.eval(f"{S}.player.anims.currentAnim?.key")
    ok &= check(got == "20" and clip == "her-duck" and s["mode"] == "play" and s["safe"] and s["tangerines"] == 1
                and b.eval(f"{S}.loose.all.length") == 0 and b.eval(f"{S}.world.carry?.kind === 'lunch'"),
                "a gull: she ducks, it takes one, she keeps her tray", (got, clip, s))
    b.shot("pocket-gull")
    b.wait_for(f"!{S}.isSafe()", timeout=4)
    ok &= check(abs(b.state()["x"] - x) < 4, "and her place", (x, b.state()["x"]))
    b.eval(f"{S}.world.carryBox.drop()")
    # A tangerine she gets flies to the count, which changes as it lands.
    b.eval(f"{S}.save.tangerines = 0; {S}.refreshHud(); {S}.gainTangerine({S}.player.x + 40, {S}.player.y - 10)")
    shown = b.eval(f"[{S}.save.tangerines, {S}.hud.items.tangerine.value]")
    wait(0.7)
    landed = b.eval(f"{S}.hud.state().tangerine")
    ok &= check(shown == [1, "x 0"] and landed == "x 1", "picked up: hers at once, counted when it lands", (shown, landed))
    # A fall: two decks off deck 12's aft end, with three on her.
    b.eval(f"{S}.save.tangerines = 3")
    b.teleport(x_of(245.5), D12)
    wait(0.6)
    s = b.state()
    ok &= check(s["mode"] == "scripted" and s["tangerines"] == 3, "a long fall is a fright, tangerines or not", s)
    return ok


def scenario_throw(b):
    """The throw (docs/plan-three-uses.md §1.2, §2): F rolls a tangerine, ↑ and F lob it. A roll that
    nothing takes lies where it stops and is hers again by walking over it; deck 4's vacuum swallows
    one and chokes, dead until she has left the deck; a gull at the pool takes one; a lob brings the
    piñata down (three for one); Bumbot at his spot bats one back, and his beat is what it was."""
    S = "window.__ship"
    b.open("?reset&play&cards=all")

    def throw(x, y, face=1, lob=False):
        b.teleport(x, y)
        wait(0.4)
        b.eval(f"{S}.save.tangerines = 3; {S}.refreshHud(); {S}.player.setFlipX({'true' if face < 0 else 'false'})")
        if lob:
            b.key("up", True)
        b.tap("f")
        if lob:
            b.key("up", False)

    def loose():
        return b.eval(f"{S}.loose.all.map(t => ({{ x: Math.round(t.img.x), y: Math.round(t.img.y), resting: t.resting }}))")

    # A roll nothing takes: one less, it lies on the floor some metres off, and is hers again.
    throw(x_of(150), D4)
    x0 = b.state()["x"]
    b.wait_for(f"{S}.loose.all.length === 1 && {S}.loose.all[0].resting", timeout=6)
    t = loose()[0]
    b.shot("throw-roll")
    ok = check(b.state()["tangerines"] == 2, "F throws one: one less", b.state())
    ok &= check(5 * 48 < t["x"] - x0 < 7.5 * 48 and abs(t["y"] + 3 - D4) <= 2, "it rolls about six metres and lies on the floor", (x0, t))
    ok &= check(b.eval(f"{S}.save.loose.length") == 1, "kept in the save where it lies")
    hold_until(b, "right", lambda st: st["tangerines"] == 3, timeout=5)
    ok &= check(b.state()["tangerines"] == 3 and not loose(), "walked over, it is hers again", b.state())

    # A lob: high and short.
    throw(x_of(150), D4, lob=True)
    top = D4
    for _ in range(30):
        y = b.eval(f"(t => t ? t.img.y : null)({S}.loose.all[0])")
        if y is not None:
            top = min(top, y)
        wait(0.03)
    ok &= check(80 < D4 - top < 125, "↑ and F lob it, high", D4 - top)
    b.eval(f"{S}.loose.all.slice().forEach(t => {S}.loose.remove(t))")

    # Deck 4's vacuum: it swallows it and chokes, dead, no fright; alive again once she has left.
    b.eval(f"(v => {{ v.sprite.x = {x_of(150) + 150}; v.dir = 1; v.speed = 0; }})({S}.vacuums[0])")
    throw(x_of(150), D4)
    b.wait_for(f"!{S}.vacuums[0].alive", timeout=5)
    b.shot("throw-vacuum")
    ok &= check(not loose() and b.state()["tangerines"] == 2, "deck 4's vacuum swallows it", loose())
    vx = b.eval(f"{S}.vacuums[0].sprite.x")
    b.teleport(vx, D4)
    wait(0.5)
    ok &= check(b.state()["mode"] == "play", "choked, it frightens nobody", b.state())
    b.teleport(x_of(150), D5)
    wait(0.3)
    ok &= check(b.eval(f"{S}.vacuums[0].alive"), "and it is going again once she has left the deck")
    b.eval(f"{S}.vacuums[0].speed = 40")

    # A gull at the pool: one comes down for it and goes off with it.
    g = f"{S}.world.foodGulls.gull_pool"
    # (From the deck past them, facing back: short of them is the pool.)
    gx1 = b.eval(f"{g}.def.x1")
    throw(gx1 + 150, D11, face=-1)
    # (Its fruit is the one it took; `up` is its flight off with it: there is no `fed` since e4f719c.)
    b.wait_for(f"{g}.fruit", timeout=6)
    ok &= check(b.eval(f"!!{g}.fruit"), "a gull at the pool comes down for it", b.eval(f"{g}.state"))
    wait(0.5)
    b.shot("throw-gull")
    b.wait_for(f"!{g}.fruit && {g}.state === 'up' && {g}.loot.visible", timeout=5)
    ok &= check(not loose() and b.state()["tangerines"] == 2, "and goes off with it", loose())

    # The piñata, by a lob from under it (it hangs in a small room past a wall): down it comes, three
    # for one.
    pin = f"{S}.world.breakables.find(t => t.id === 'sec_pinata')"
    px = b.eval(f"{pin}.x")
    throw(px - 34, D12, lob=True)
    b.wait_for(f"{pin}.done", timeout=5)
    wait(0.4)
    b.shot("throw-pinata")
    ok &= check(b.eval(f"{S}.save.broken.includes('sec_pinata')"), "a lob brings the piñata down")
    ok &= check(b.eval(f"{S}.tangerines.filter(t => t.id.startsWith('tan_12_pinata')).length") == 3,
                "and its three tangerines are there", b.eval(f"{S}.tangerines.map(t => t.id).filter(i => i.startsWith('tan_12'))"))

    # Bumbot at his first spot: he bats it straight back to her, and his beat is what it was.
    cat = f"{S}.cats.find(c => c.name === 'bb1')"
    cx, cf = b.eval(f"[{cat}.sprite.x, {cat}.floor]")
    # (From outside his sight, 200 px: nearer, the near-catch begins. A lob, up onto the pass's counter where he is.)
    throw(cx - 216, cf, lob=True)
    b.wait_for(f"{cat}.batting", timeout=5)
    vx = b.eval(f"(t => t ? t.img.body.velocity.x : 0)({S}.loose.all[0])")
    b.shot("throw-bumbot")
    ok &= check(vx < -50, "Bumbot bats it straight back to her", vx)
    ok &= check(not b.eval(f"{cat}.gone"), "and stays at his spot")
    b.wait_for(f"{S}.loose.all.length === 0 || {S}.loose.all[0].resting", timeout=5)
    hold_until(b, "right", lambda st: b.eval(f"{cat}.gone"), timeout=6)
    ok &= check(b.eval(f"{cat}.gone"), "walking up to him, the near-catch goes as it always did")

    # The gull with Bumbot's collar bell on the promenade's wall light (§4 2.1, thing 4): it keeps its place
    # as she walks under it; her cry sends it up with the bell; a throw in a jump, or a lob from about 2 m, is
    # caught, the bell drops to the deck under its beak, and E takes it (the thing to find).
    G = f"{S}.world.movers.find(m => m.def?.id === 'gull_bell')"
    bell = f"{S}.world.things.find(t => t.id === 'keep_bell')"
    gx = b.eval(f"{G}.def.x")
    b.wait_for(f"{S}.mode === 'play'", timeout=12)        # (the near-catch above played out)
    b.teleport(gx - 120, D6, "promenade")
    wait(0.4)
    ok &= check(not b.eval(f"{bell}.pick.visible"), "the bell gull: the bell in its beak, none on the deck")
    hold_until(b, "right", lambda st: st["x"] > gx + 20, timeout=4)
    ok &= check(b.eval(f"{G}.rise") == 0, "it keeps its light as she walks under it", b.eval(f"{G}.rise"))
    b.eval(f"{S}.save.tangerines = 3; {S}.refreshHud()")
    b.tap("d")
    wait(0.4)
    ok &= check(b.eval(f"{G}.rise") > 0 and not b.eval(f"{G}.gone"), "her cry sends it up, the bell kept", b.eval(f"{G}.rise"))
    b.wait_for(f"{G}.rise === 0", timeout=8)
    # A throw in a jump (the user, 2026-11-20): 1.5 m short, F as she rises; a second F in the same jump
    # throws nothing; she flies on; the gull catches it.
    b.teleport(gx - 72, D6, "promenade")
    wait(0.4)
    b.eval(f"{S}.player.setFlipX(false); {S}.save.tangerines = 3; {S}.refreshHud()")
    b.key("space", True)
    wait(0.2)
    b.key("space", False)
    b.tap("f", 0.05)
    air = b.eval(f"[{S}.player.anims.currentAnim?.key, !{S}.player.body.blocked.down, {S}.throwing?.air]")
    b.tap("f", 0.05)
    ok &= check(air == ["her-airtoss", True, True], "F in a jump: her throw in the air, and she flies on", air)
    b.wait_for(f"{G}.gone", timeout=3)
    ok &= check(b.state()["tangerines"] == 2, "one throw a jump: a second F threw nothing", b.state())
    b.wait_for(f"!{G}.fall && !{G}.away", timeout=4)
    b.shot("throw-bell")
    ok &= check(b.eval(f"{S}.save.flags.includes('bell_dropped')") and b.eval(f"{bell}.pick.visible")
                and abs(b.eval(f"{bell}.pick.y") - D6) < 1, "the gull catches it: the bell drops to the deck",
                b.eval(f"[{bell}.pick.x, {bell}.pick.y, {bell}.pick.visible]"))
    # (Again, by a lob from the deck about 2 m off: the gull put back as it was.)
    b.eval(f"(g => {{ g.gone = false; g.away = null; g.fall = null; g.rise = 0; {S}.save.flags = {S}.save.flags.filter(f => f !== 'bell_dropped');"
           f" g.sprite.setVisible(true).setAlpha(1); g.pose('gull-perched'); g.sprite.setPosition(g.def.x, g.def.y); g.thing.pick.setVisible(false); }})({G})")
    b.wait_for(f"{S}.mode === 'play' && {S}.player.body.blocked.down", timeout=3)
    b.teleport(gx - 117, D6, "promenade")
    wait(0.4)
    b.eval(f"{S}.player.setFlipX(false)")
    b.key("up", True)
    b.tap("f")
    b.key("up", False)
    b.wait_for(f"{G}.gone", timeout=3)
    b.wait_for(f"!{G}.fall && !{G}.away", timeout=4)
    ok &= check(b.eval(f"{S}.save.flags.includes('bell_dropped')") and abs(b.eval(f"{bell}.pick.y") - D6) < 1,
                "or a lob from the deck: caught, the bell drops", b.eval(f"[{bell}.pick.x, {bell}.pick.y, {bell}.pick.visible]"))
    b.teleport(b.eval(f"{bell}.x") - 6, D6, "promenade")
    wait(0.3)
    b.tap("e")
    wait(0.4)
    ok &= check("keep:cat:bell" in b.eval(f"{S}.save.keeps"), "and E takes it", b.eval(f"{S}.save.keeps"))
    return ok


def scenario_throw__sardines(b):
    """The sushi chef's tin of sardines (§4 2.1, thing 7; deck 12): his cloud shows a tangerine once she is near;
    E with none, it hops, nothing else; E with one, she hands it over with a bow, he takes it over his case and hands
    her Bumbot's tin (one tangerine fewer, his cloud gone); again, a lob that reaches him is caught, and he sets the
    tin on his case for E to take."""
    S = "window.__ship"
    C = f"{S}.world.people.byId.amb_sushi_chef"
    tin = f"{S}.world.things.find(t => t.id === 'keep_sardines')"
    b.open("?reset&play&at=sushi")
    cx = b.eval(f"{C}.x")
    b.teleport(cx - 200, D12)
    wait(0.3)
    ok = check(not b.eval(f"{C}.bubbleItems[0].visible"), "the sushi chef's cloud: not from afar")
    b.teleport(cx + 30, D12)
    wait(0.4)
    ok &= check(b.eval(f"{C}.bubbleItems[0].visible"), "near him, his cloud shows a tangerine",
                b.eval(f"{C}.bubbleItems[1].texture.key"))
    b.eval(f"{S}.save.tangerines = 0; {S}.refreshHud()")
    b.tap("e")
    wait(0.5)
    got = b.eval(f"[{S}.mode, {S}.save.keeps.slice(), {C}.state]")
    ok &= check(got[0] == "play" and "keep:cat:sardines" not in got[1], "E with no tangerine: nothing but his cloud's hop", got)
    b.eval(f"{S}.save.tangerines = 2; {S}.refreshHud()")
    b.tap("e")
    b.wait_for(f"{S}.save.keeps.includes('keep:cat:sardines')", timeout=10)
    ok &= check(b.eval(f"{S}.save.keeps.includes('keep:cat:sardines')") and b.state()["tangerines"] == 1,
                "E with one: handed over, the tin is hers, one tangerine fewer", [b.eval(f"{S}.save.keeps"), b.state()["tangerines"]])
    b.shot("sardines-given")
    b.wait_for(f"{S}.mode === 'play' && {C}.state === 'idle'", timeout=6)
    ok &= check(not b.eval(f"{C}.bubbleItems[0].visible") and not b.eval(f"{tin}.pick.visible"),
                "his cloud gone, no tin on the counter")
    # Again, by a lob from the floor about a metre off his front: caught, the tin set on his case.
    b.eval(f"{S}.save.keeps = []; {S}.save.flags = {S}.save.flags.filter(f => !f.startsWith('sushi')); {S}.world.refresh()")
    b.teleport(cx - 45, D12)
    wait(0.4)
    b.eval(f"{S}.player.setFlipX(false); {S}.save.tangerines = 3; {S}.refreshHud()")
    b.key("up", True)
    b.tap("f")
    b.key("up", False)
    b.wait_for(f"{S}.save.flags.includes('sushi')", timeout=3)
    ok &= check(b.eval(f"{S}.save.flags.includes('sushi')"), "a lob that reaches him: caught")
    b.wait_for(f"{S}.save.flags.includes('sushi_tin')", timeout=8)
    b.shot("sardines-counter")
    top = b.eval(f"{tin}.pick.y")
    ok &= check(b.eval(f"{tin}.pick.visible") and abs(top - (D12 - 40)) < 1, "the tin set on his case's top", [top, D12 - 40])
    b.wait_for(f"{C}.state === 'idle'", timeout=4)
    b.teleport(b.eval(f"{tin}.x"), D12)
    wait(0.3)
    b.tap("e")
    wait(0.4)
    ok &= check("keep:cat:sardines" in b.eval(f"{S}.save.keeps"), "and E takes it", b.eval(f"{S}.save.keeps"))
    return ok


def scenario_throw__funnel(b):
    """A tangerine thrown at the funnel's gulls (part 5): rolled off the funnel's top it bounces down the stairway's
    treads (it fell straight through them before) and lies on one; a gull comes down to it only once it lies still,
    stands on its tread, and goes off with it; thrown the other way, out of their reach, it lies on the top."""
    S = "window.__ship"
    W = f"{S}.world.story.funnelWind"
    b.open("?reset&play&at=funnel")
    wait(0.5)
    b.eval(f"{W}.taker = {{}}")     # (the gulls held off at first: where does it go by itself?)
    b.eval(f"{S}.save.tangerines = 3; {S}.refreshHud(); {S}.player.setFlipX(true)")
    b.tap("f")
    b.wait_for(f"{S}.loose.all[0]?.resting", timeout=8)
    t = b.eval(f"(t => [t.img.x, t.img.y + 3])({S}.loose.all[0])")
    top = b.eval(f"{S}.treadTop({t[0]})")
    ok = check(top is not None and abs(t[1] - top) <= 3 and t[1] < D12 - 100, "off the top, it bounces down the stairway and lies on a tread", (t, top))
    b.eval(f"{W}.taker = null")
    ok &= check(wait_js(b, f"!!{W}.taker", 4), "a gull comes down to it")
    b.wait_for(f"{W}.taker?.sprite.frame.name === 'gull-perched'", timeout=4)
    g = b.eval(f"(g => [g.sprite.x, g.sprite.y])({W}.taker)")
    ok &= check(abs(g[1] - b.eval(f"{S}.treadTop({g[0]})")) <= 2, "and stands on a tread, not in a step", g)
    b.shot("throw-funnel-gull")
    ok &= check(wait_js(b, f"!{W}.taker && !{S}.loose.all.length", 6), "and goes off with it")
    # The other way, out of their reach: it lies on the funnel's top.
    b.eval(f"{W}.quietUntil = 0; {S}.player.setFlipX(false)")
    b.tap("f")
    b.wait_for(f"{S}.loose.all[0]?.resting", timeout=8)
    wait(1.0)
    ok &= check(b.eval(f"{S}.loose.all.length") == 1 and not b.eval(f"!!{W}.taker"), "thrown away from them, it lies on the top, untouched")
    return ok


def scenario_throw__tip(b):
    """A tangerine thrown at Bumbot on the tip of the bow (part 5): one rolling at him sends him back along the deck,
    away from it, and once he is cornered at the tip it sends him darting past her; a lob over his head that lands
    behind him and rolls away does nothing (he went after it before)."""
    S = "window.__ship"
    T = f"{S}.world.story"
    b.open("?reset&play&at=bow&did=sunset")
    wait(0.5)
    Mo = b.eval(f"{S}.world.data.finale.mooring")
    cat = lambda: b.eval(f"Math.round({T}.tipCat.x)")
    b.teleport(Mo["catX"] + 250, Mo["y"])
    wait(0.3)
    her = b.state()["x"]
    b.eval(f"{S}.save.tangerines = 3; {S}.refreshHud(); {S}.player.setFlipX(true)")
    b.tap("f")
    ok = check(wait_js(b, f"{T}.tip.spooks >= 1", 3), "a roll at him: he backs off")
    b.wait_for(f"!{T}.tip.busy", timeout=3)
    ok &= check(cat() < Mo["catX"] - 40, "along the deck, away from it", cat())
    ok &= check(wait_js(b, f"{T}.tip.spooks >= 2", 3), "it rolls on at him, cornered")
    wait(1.5)
    ok &= check(cat() > her + 60, "he darts past her", (cat(), her))
    b.open("?reset&play&at=bow&did=sunset")
    wait(0.5)
    b.teleport(Mo["catX"] + 150, Mo["y"])
    wait(0.3)
    b.eval(f"{S}.save.tangerines = 3; {S}.refreshHud(); {S}.player.setFlipX(true)")
    b.key("up", True)
    b.tap("f")
    b.key("up", False)
    b.wait_for(f"{S}.loose.all[0]?.resting", timeout=4)
    ok &= check(b.eval(f"{S}.loose.all[0].img.x") < cat() and b.eval(f"{T}.tip.spooks") == 0,
                "a lob over his head, landing behind him: he takes no notice", (b.eval(f"{S}.loose.all[0].img.x"), cat()))
    return ok


def scenario_deck4(b):
    """Region 1's decks filled (docs/plan-three-uses.md §4.2; step 4): deck 4's suitcase (a bump),
    the dog's lead (held back, never a fright; hopped), its three fetches and the tennis ball, the
    climb by jumps and the feather (not from the floor; knocked down by a lob; taken up there);
    deck 5's wool in the knitter's basket, her flag at the desk, a sliding paper (a slip); the
    HUD's counts, each from its first find."""
    S, W = "window.__ship", "window.__ship.world"
    b.open("?reset&play&cards=all")

    def keeps():
        return b.eval(f"{S}.save.keeps.slice()")

    # The suitcase: walked into, a bump.
    R = f"{W}.movers.find(m => m.def?.id === 'haz_suitcase_4')"
    b.eval(f"{R}.phase = 0")
    b.teleport(exact_x(36), D4)
    s = hold_until(b, "right", lambda st: st["mode"] != "play", timeout=6)
    ok = check(s["mode"] == "scripted", "the suitcase: walked into, a bump", s)
    # (6a: she rides it off too, the user, 2026-11-16.)
    ok &= check(b.eval(f"!!{S}.worldLayer.list.find(o => o.texture?.key === 'her-mishaps')"), "6a: walked into, she rides it off")
    b.wait_for(f"{S}.mode === 'play'", timeout=12)

    # 6b: rolled into her back as she stands facing its way, whatever she carries (1.2a): she rides it to the
    # end of its roll, it tips her off, and she is back at her checkpoint with it in its place.
    G = f"{S}.worldLayer.list.find(o => o.texture?.key === 'her-mishaps')"
    b.eval(f"{R}.phase = Math.PI / 2 - 0.35")
    b.teleport(b.eval(f"{R}.mid - {R}.half * Math.cos(Math.PI / 2 - 0.35)") + 26, D4)
    b.eval(f"{S}.player.setFlipX(false)")
    b.wait_for(f"{S}.mode === 'scripted'", timeout=6)
    ok &= check(b.eval(f"{S}.lastMishap?.id") == "6b" and b.eval(f"!!{G} && !{R}.sprite.visible && !{S}.player.visible"),
                "6b: rolled into her back, she rides it (her with it in one picture; its own hidden)",
                b.eval(f"[{S}.lastMishap?.id, {G}?.anims.currentAnim?.key]"))
    b.wait_for(f"{G}?.anims.currentAnim?.key === 'gag-suitcase-tip'", timeout=8)
    ok &= check(abs(b.eval(f"{G}.x") - b.eval(f"{R}.def.x1")) < 2, "6b: tipped off at the end of its roll",
                (b.eval(f"{G}.x"), b.eval(f"{R}.def.x1")))
    b.wait_for(f"{S}.mode === 'play'", timeout=8)
    ok &= check(b.eval(f"!{G} && {R}.sprite.visible && {S}.player.visible && !{R}.parked"),
                "6b: back at her checkpoint, the suitcase in its place")
    # 6c: standing facing it as it rolls at her: she rides it off too, turned round onto it.
    b.eval(f"{R}.phase = Math.PI / 2 - 0.35; {S}.player.setFlipX(true)")
    b.teleport(b.eval(f"{R}.mid - {R}.half * Math.cos(Math.PI / 2 - 0.35)") + 50, D4)
    b.eval(f"{S}.player.setFlipX(true)")
    b.wait_for(f"{S}.mode === 'scripted'", timeout=6)
    ok &= check(b.eval(f"{S}.lastMishap?.id") == "6c" and b.eval(f"!!{G} && !{G}.flipX"),
                "6c: rolled into her front, she rides it off the way it was going",
                b.eval(f"[{S}.lastMishap?.id, {G}?.flipX]"))
    b.wait_for(f"{S}.mode === 'play'", timeout=12)

    # The dog's lead where it lies on the carpet: run into with no tangerine, she trips and falls flat
    # (a fright: the user, 2026-11-16); hopped, nothing.
    F = f"{W}.movers.find(m => m.def?.id === 'haz_dog_4')"
    # (The dog forward of its owner's door: aft of it, two metres on, is a bulkhead's wall, which its
    # lead stops short of.)
    ok &= check(b.eval(f"{F}.range().hi < {F}.def.x + {F}.def.reach"), "the lead stops short of the bulkhead's wall",
                b.eval(f"[{F}.def.x, {F}.range()]"))
    b.eval(f"(f => {{ f.dog.x = f.def.x - 120; f.go('sit', 60000); }})({F})")
    wait(0.3)
    sag = b.eval(f"{F}.sag().x")
    b.teleport(sag - 60, D4)
    s = hold_until(b, "right", lambda st: st["x"] > sag + 30 or st["mode"] != "play", timeout=3)
    ok &= check(s["mode"] == "scripted" and b.eval(f"{S}.player.anims.currentAnim?.key").startswith("her-tripfall"),
                "run into the lead with none on her: she trips and falls flat", (sag, s, b.eval(f"{S}.player.anims.currentAnim?.key")))
    b.wait_for(f"{S}.player.anims.currentAnim?.key === 'her-dazed-lie'", timeout=3)
    ok &= check(True, "dazed where she fell, butterflies over her head")
    # The dog comes and licks her face: her and it in one picture, its own sprite and her hidden,
    # the lead to its collar there; her checkpoint after it (the dog's together clips, 2026-11-17).
    b.wait_for(f"{F}.state === 'licking'", timeout=5)
    ok &= check(b.eval(f"!!{F}.lickGag && {F}.lickGag.anims.currentAnim?.key === 'gag-dog-lick' && {F}.dog.sprite.alpha === 0"
                       f" && !{S}.player.visible && {S}.mode === 'scripted'"),
                "the dog licks her face (one picture of the two; she waits for it)")
    b.wait_for(f"{S}.mode === 'play'", timeout=8)
    ok &= check(b.eval(f"!{F}.lickGag && {F}.dog.sprite.alpha === 1 && {S}.player.visible"),
                "back at her checkpoint, the dog its own again")
    # With tangerines on her too (every hit since 1.2a; the user, 2026-11-17 first for this one): down and back to her
    # checkpoint, and she keeps them all.
    b.eval(f"(f => {{ f.dog.x = f.def.x - 120; f.go('sit', 60000); }})({F})")
    b.eval(f"{S}.save.tangerines = 3; {S}.refreshHud()")
    b.teleport(sag - 60, D4)
    wait(0.6)
    s = hold_until(b, "right", lambda st: st["x"] > sag + 30 or st["mode"] != "play", timeout=3)
    ok &= check(s["mode"] == "scripted" and b.eval(f"{S}.player.anims.currentAnim?.key").startswith("her-tripfall")
                and s["tangerines"] == 3,
                "with tangerines on her too: she falls flat, and none flies out", (s, b.eval(f"{S}.player.anims.currentAnim?.key")))
    b.wait_for(f"{S}.mode === 'play'", timeout=8)
    ok &= check(b.state()["tangerines"] == 3, "back at her checkpoint with all three", b.state())
    b.eval(f"{S}.save.tangerines = 0; {S}.refreshHud()")
    b.eval(f"(f => {{ f.dog.x = f.def.x - 120; f.go('sit', 60000); }})({F})")
    b.teleport(sag + 60, D4)
    wait(0.3)
    b.key("left", True)
    wait(0.12)
    b.tap("space", 0.25)
    wait(0.7)
    b.key("left", False)
    s = b.state()
    ok &= check(s["x"] < sag and s["mode"] == "play", "hopped, no trip", (sag, s))
    b.shot("deck4-dog")

    # Her cry: it runs to its owner and round her legs (their picture: the dog and the lead in it),
    # stands tied, unwinds, and trots off; no trip on the lead all the while.
    b.eval(f"(f => {{ f.dog.x = f.def.x - 90; f.go('sit', 60000); }})({F})")
    b.teleport(b.eval(f"{F}.def.x") - 150, D4)
    wait(0.4)
    b.eval(f"{S}.save.tangerines = 3; {S}.tryCry({S}.time.now)")
    b.wait_for(f"{F}.state === 'tied'", timeout=6)
    ok &= check(b.eval(f"{F}.together && {F}.dog.sprite.alpha === 0 && {F}.owner.sprite.anims.currentAnim?.key === 'people-dogowner-tied'"
                       f" && {F}.flatUntil === Infinity"),
                "her cry: the dog winds the lead round its owner's legs (their picture), nothing to trip on")
    b.wait_for(f"{F}.state === 'walk'", timeout=10)
    ok &= check(b.eval(f"!{F}.together && {F}.dog.sprite.alpha === 1 && {F}.flatUntil === 0"),
                "unwound, the dog trots off, the lead its own again")

    # Three fetches: each brought back to her, hers again; then the tennis ball.
    for i in range(3):
        b.eval(f"(f => {{ f.go('sit', 0); f.dog.x = f.def.x + 40; }})({F})")
        b.teleport(b.eval(f"{F}.def.x") - 140, D4)
        wait(0.4)
        b.eval(f"{S}.save.tangerines = 3; {S}.player.setFlipX(false)")
        b.tap("f")
        b.wait_for(f"{F}.fetches > {i}", timeout=8)
        wait(0.4)
        ok &= check(b.state()["tangerines"] == 3, f"fetch {i + 1}: brought back to her and hers again", b.state())
    # (Her toss: out of her pocket, held out, a lob to her chest: about two seconds.)
    b.wait_for(f"{S}.save.keeps.includes('keep:cat:ball')", timeout=5)
    ok &= check("keep:cat:ball" in keeps(), "three fetches, and the owner tosses her the tennis ball", keeps())

    # The feather on the climb's shelf: not from the floor; a lob knocks it down, hers from there.
    K = f"{W}.things.find(t => t.id === 'keep_feather')"
    kx = b.eval(f"{K}.x")
    b.teleport(kx, D4)
    wait(0.3)
    b.tap("e")
    wait(0.3)
    ok &= check("keep:cat:feather" not in keeps(), "the feather is not to be had from the floor")
    # (A lob from about four metres back comes down onto the shelf, over the carts.)
    b.teleport(kx - 184, D4)
    wait(0.3)
    b.eval(f"{S}.save.tangerines = 3; {S}.player.setFlipX(false)")
    b.key("up", True)
    b.tap("f")
    b.key("up", False)
    b.wait_for(f"!{K}.high", timeout=3)
    wait(0.6)
    ok &= check(b.eval(f"!{K}.high && Math.abs({K}.pick.y - {K}.y) < 2"), "a lob knocks it down to the floor", b.eval(f"{K}.pick.y - {K}.y"))
    b.eval(f"{S}.loose.all.slice().forEach(t => {S}.loose.remove(t))")
    b.teleport(kx, D4)
    wait(0.3)
    b.tap("e")
    wait(0.3)
    ok &= check("keep:cat:feather" in keeps(), "and it is hers from there", keeps())

    # The climb itself: two steps up by jumps (a new game, the feather back on its shelf).
    b.open("?reset&play&cards=all")
    steps = b.eval(f"['climb_0', 'climb_1'].map(id => {W}.solids.find(t => t.id === id).x)")
    b.teleport(steps[0] - 40, D4)
    wait(0.3)
    heights = []
    for i, sx in enumerate(steps):
        # (To the shelf from the cart's far edge: from its middle the jump falls short, the user's
        # harder gap, 2026-11-17.)
        if i:
            b.key("right", True)
            end = now() + 1.5
            while b.state()["x"] < steps[0] + 16 and now() < end:
                wait(0.01)
        b.key("space", True)
        hold_until(b, "right", lambda st: st["x"] >= sx - 2, timeout=1.5)
        wait(0.25)
        b.key("space", False)
        wait(0.5)
        heights.append(round(D4 - b.state()["y"]))
    ok &= check(heights == [41, 66], "up the climb by jumps: the laundry cart, the shelf", heights)
    b.tap("e")
    wait(0.3)
    ok &= check("keep:cat:feather" in keeps(), "the feather taken up there", keeps())
    b.shot("deck4-climb")

    # Deck 5: the wool, her flag; the HUD's counts.
    ok &= check(b.eval("window.__ship.hud.state().her") == "", "her count is not shown before her first find")
    for tid, what in (("keep_wool", "keep:cat:wool"), ("keep_flag", "keep:her:flag")):
        b.teleport(b.eval(f"{W}.things.find(t => t.id === '{tid}').x"), D5)
        wait(0.3)
        b.tap("e")
        wait(0.3)
        ok &= check(what in keeps(), f"{tid}: taken with E", keeps())
    hud = b.eval("window.__ship.hud.state()")
    hud = {k: hud[k] or None for k in ("cat", "her", "him")} | {"order": hud["order"]}
    ok &= check(hud == {"cat": "2/8", "her": "1/4", "him": None, "order": ["cat", "her"]},
                "the HUD counts each kind from its first find, in the order found", hud)
    b.shot("deck4-hud")

    # The paper round (the user, 2026-11-16 and 17): a paper sliding at a steady speed right to her
    # foot; at her heel she sits with it over her head (4b), at her front she goes down on her belly
    # with it on her back (4a), standing or not; the paper is the one in her gag, the world's gone.
    P = f"{W}.movers.find(m => m.def?.id === 'haz_papers_5')"
    GAG = f"{S}.worldLayer.list.find(o => o.texture?.key === 'her-mishaps')"
    def paper_hit(face_right, label):
        b.wait_for(f"{S}.mode === 'play'", timeout=10)
        b.eval(f"(p => {{ p.x = p.def.x0; p.dir = 1; p.next = 0; p.until = 0; p.papers.forEach(q => q.img.destroy()); p.papers = []; }})({P})")
        b.teleport(b.eval(f"{P}.def.doors[1]") - 40, D5)
        wait(0.2)
        b.eval(f"{S}.player.setFlipX({'false' if face_right else 'true'})")
        b.wait_for(f"{P}.papers.some(q => q.img.x > {S}.player.x - 90)", timeout=12)
        x1 = b.eval(f"{P}.papers[0].img.x"); wait(0.1); x2 = b.eval(f"{P}.papers[0]?.img.x ?? 0")
        hx = b.eval(f"{S}.player.x")
        b.wait_for(f"{S}.mode !== 'play'", timeout=4)
        got = b.eval(f"[{S}.lastMishap?.id, {GAG}?.anims.currentAnim?.key, Math.round({GAG}?.x - {hx}), {P}.papers.length]")
        b.shot(f"deck4-{label}")
        return got, x2 - x1
    got, step = paper_hit(True, "paper-behind")
    ok &= check(150 < step * 10 < 330, "a paper slides at a steady speed as it nears her (px/s)", round(step * 10))
    ok &= check(got[0] == "4b" and got[1] == "gag-paper-behind" and abs(got[2]) <= 4 and got[3] == 0,
                "at her heel as she stands: she sits, the paper over her head; the world's own gone", got)
    b.wait_for(f"{S}.mode === 'play'", timeout=8)
    ok &= check(not b.eval(f"!!{GAG}"), "back at her checkpoint, the gag's picture gone")
    got, _ = paper_hit(False, "paper-front")
    ok &= check(got[0] == "4a" and got[1] == "gag-paper-front" and abs(got[2]) <= 4 and got[3] == 0,
                "at her front as she stands: she slips too, on her belly, the paper on her back", got)
    b.wait_for(f"{S}.mode === 'play'", timeout=8)

    # One lying at its door, not yet taken in: walked onto, the same fall.
    b.eval(f"(p => {{ p.x = p.def.x0; p.dir = 1; p.next = 0; p.until = 0; }})({P})")
    door = b.eval(f"{P}.def.doors[1]")
    b.teleport(door + 150, D5)
    b.wait_for(f"{P}.papers.some(q => q.door === {door} && q.done)", timeout=15)
    b.teleport(door - 30, D5)
    s = hold_until(b, "right", lambda st: st["mode"] != "play", timeout=2)
    got = b.eval(f"[{S}.lastMishap?.id, {GAG}?.anims.currentAnim?.key]")
    ok &= check(s["mode"] == "scripted" and got == ["4a", "gag-paper-front"],
                "a paper lying at its door, not yet taken in: walked onto, on her belly", (s["mode"], got))
    b.wait_for(f"{S}.mode === 'play'", timeout=8)

    # The breakfast round: a plate taken in at a door, the trolley wheeled on; walked into, a fright.
    B = f"{W}.movers.find(m => m.def?.id === 'haz_breakfast_5')"
    # (Watching from past her second door, clear of the first paper round's end at 42 m.)
    b.teleport(b.eval(f"{B}.doors()[1]") + 120, D5)
    b.wait_for(f"{B}.state === 'serving'", timeout=30)
    served = b.eval(f"{B}.i")
    b.wait_for(f"{B}.state === 'push' && {B}.i !== {served}", timeout=30)
    ok &= check(True, "the breakfast round: a tray taken in, the trolley wheeled on to the next door")
    b.eval(f"{B}.until = {S}.time.now + 60000")
    # (From the side away from her trolley: ahead of her while she wheels it, behind her otherwise.)
    side = b.eval(f"{B}.state === 'push' ? -{B}.dir : {B}.dir")
    b.teleport(b.eval(f"{B}.x") + side * 60, D5)
    wait(0.3)
    s = hold_until(b, "left" if side > 0 else "right", lambda st: st["mode"] != "play", timeout=3)
    ok &= check(s["mode"] == "scripted", "walked into, the breakfast stewardess drops her tray: a fright", s)
    b.wait_for(f"{S}.mode === 'play'", timeout=8)
    b.eval(f"{B}.until = 0")

    # A tangerine thrown to the steward: caught, and eaten from his hand, bite by bite.
    b.eval(f"(k => {{ k.x = k.def.x1 - 20; k.dir = -1; k.until = 0; }})({P})")
    b.teleport(b.eval(f"{P}.x") - 45, D5)
    wait(0.4)
    b.eval(f"{S}.save.tangerines = 3; {S}.player.setFlipX(false)")
    b.tap("f")
    b.wait_for(f"{P}.eating", timeout=5)
    ok &= check(not b.eval(f"{S}.loose.all.length") and b.eval(f"{P}.p.sprite.anims.currentAnim?.key").endswith("bite"),
                "a tangerine thrown to the steward: he eats it", b.eval(f"{P}.p.sprite.anims.currentAnim?.key"))
    b.wait_for(f"!{P}.eating", timeout=8)
    return ok


def scenario_overboard(b):
    b.open("?reset&play")
    b.teleport((col(255) - 1) * TILE - 30, D6)  # deck 6's open aft terrace, just inside the railing
    b.key("right", True)
    wait(0.4)  # up against the railing first: the terrace is only a metre deep
    b.key("space", True)
    wait(0.5)
    b.key("space", False)
    wait(0.6)
    b.key("right", False)
    b.wait_for("window.__ship.mode === 'scripted'", timeout=4)  # a long drop: the hull stands two decks above the sea
    wait(0.6)
    b.shot("overboard")
    s = b.state()
    ok = check(s["mode"] == "scripted", "jumping the stern railing goes overboard", s)
    wait(2.5)
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


# A way roped or chained off says nothing over her: she shrugs and its sign lights up (the user, 2026-11-24). What
# stopped her in the last 3 s: the sign's words (`lastBlocked` in the ship scene), else "".
def blocked(b):
    return b.eval("(() => { const s = window.__ship, l = s.lastBlocked; return l && s.time.now - l.at < 3000 ? l.text : ''; })()") or ""


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
    wait(0.15)
    return door_open(b, f"part-door-{deck}-{m:g}")


def take_card(b, card):
    deck, m, _ = CARD_SPOTS[card]
    go(b, deck, m)
    b.tap("e")
    wait(0.2)
    return card in save_list(b, "cards")


def flags(b):
    return save_list(b, "flags")


def route(b):
    return b.eval("window.__ship.route")


def wait_flag(b, flag, timeout=12):
    """A scene sets its flag when it is over."""
    end = now() + timeout
    while now() < end:
        if flag in flags(b) and b.state()["mode"] == "play":
            return True
        wait(0.2)
    return False


def room(b, name):
    return b.eval(f"(r => ({{ x0: r.def.x0, floor: r.floor, doors: r.doors }}))(window.__ship.world.rooms['{name}'])")


def hold_until(b, keys, cond, timeout=10):
    """Holds keys until `cond(state)`; the state it stopped at."""
    keys = [keys] if isinstance(keys, str) else keys
    for k in keys:
        b.key(k, True)
    end = now() + timeout
    s = b.state()
    while now() < end and not cond(s):
        wait(0.05)
        s = b.state()
    for k in keys:
        b.key(k, False)
    return s


def into_the_shaft(b, jump=True):
    """By the laundry cart parked at the shaft's mouth (the linen room): up onto its rim (`jump`), down on hands and
    knees and forward, into the shaft."""
    if jump:
        b.hold(["left", "space"], 0.4)
        wait(0.5)
    b.key("down", True)
    wait(0.2)
    b.key("left", True)
    ok = wait_js(b, "window.__ship.route === 'duct'", 3)
    b.key("left", False)
    b.key("down", False)
    return ok


def through_the_shaft(b, limit=45):
    """Forward along the shaft to its end and out through its last grille: her state once she stands on deck 8."""
    b.key("left", True)
    end = now() + limit
    while now() < end and not (route(b) == "inside" and b.state()["mode"] == "play" and b.state()["y"] == D8):
        wait(0.25)
    b.key("left", False)
    wait(0.3)
    return b.state()


def scenario_golden(b):
    """The whole route, the gangway to the catch, every lock opened the intended way (step 0 of
    docs/build-plan.md): teleports only within regions she has opened, the mechanics with real keys."""
    b.open("?reset&play")
    ok = check(save_list(b, "regions") == [1] and save_list(b, "cards") == [], "starts in region 1 with no cards",
               save_list(b, "regions"))
    # Region 1: the guest stairs up are roped off; the crew trunk wants the Deck card.
    s = climb(b, "stairs-forward-5-6", 0.6)
    ok &= check(s["y"] == D5 and "SEARCH" in blocked(b), "the forward stairs 5-6 are roped off for the search", blocked(b))
    go(b, 4, 125)
    # (A lock's message is not shown again within 0.9 s, `lockedUntil`: the stairs' was just shown.)
    b.wait_for("window.__ship.time.now >= (window.__ship.lockedUntil || 0)", 2)
    b.tap("e")
    wait(0.15)
    ok &= check("Deck" in alert(b), "the midships crew trunk wants the Deck card", alert(b))
    # Near-catch 1 at the Seven Seas: the scream, and the dash is hers.
    b.tap("d")
    ok &= check(not b.state()["lunging"], "no lunge before she has seen him (the cry alone)")
    go(b, 5, 244)
    b.hold("right", 1.6)
    ok &= check(wait_flag(b, "bb1"), "near-catch 1 at the Seven Seas' pass", flags(b))
    ok &= check("dash" in save_list(b, "verbs"), "the lunge is learned there", save_list(b, "verbs"))
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
    ok &= check(shut and "QUIET" in blocked(b), "the Library's aft door is roped off", blocked(b))
    go(b, 6, 188.5)
    b.hold("right", 1.5)
    ok &= check(wait_flag(b, "bb2"), "near-catch 2 at the return trolley", flags(b))
    ok &= check(use_door(b, 6, 194, -1), "then the aft door opens")
    b.hold("right", 1.2)
    ok &= check(3 in save_list(b, "regions"), "region 3 beyond it", b.state())
    # Region 3: the stage, near-catch 3; the card; the trunk from Bliss up to deck 9.
    go(b, 6, 242.5)
    hold_until(b, "right", lambda s: s["mode"] == "scripted", 6)
    ok &= check(wait_flag(b, "bb3", 16), "near-catch 3 on the stage", flags(b))
    ok &= check(pills_for_the_stage_manager(b), "his pills from his cabin on deck 4: the Entertainment card")
    go(b, 6, 118)
    b.tap("e")
    b.hold("up", 7.5)
    s = b.state()
    ok &= check(s["mode"] == "trunk" and s["y"] == D9, "the red trunk from Bliss climbs to deck 9", s)
    b.hold("right", 0.6)
    ok &= check(4 in save_list(b, "regions"), "region 4: deck 9's corridor", b.state())
    # Region 4: the steward's cart fills the corridor at its aft end until she pushes it free
    # (2026-11-18: past the vacuum, the towel stack and the sprinkler; the corridor itself is region4's).
    b.teleport(exact_x(183.4), D9)
    b.hold("right", 1.0)
    s = b.state()
    ok &= check(s["x"] < exact_x(185.2), "the steward's cart blocks the corridor", s)
    b.hold(["right", "space"], 0.7)
    ok &= check(b.state()["x"] < exact_x(185.2), "and can't be hopped where it is jammed", b.state())
    wait(0.5)
    b.hold("right", 0.3)
    linen = b.eval("window.__ship.rooms.find(r => r.route === 'linen').door")
    back = b.state()["x"]
    b.teleport(linen, D9)
    b.tap("e")
    wait(0.15)
    ok &= check("Housekeeping" in alert(b) and route(b) == "inside", "the linen room's crew door wants the Housekeeping card", alert(b))
    wait(0.5)
    b.teleport(back - 6, D9)
    b.hold("right", 0.3)
    b.tap("e")
    b.hold("right", 5.4)
    ok &= check("cart_free" in flags(b), "pushed along to 189 m, it is free", b.state())
    end = now() + 12
    while now() < end and not ("hk" in save_list(b, "cards") and b.state()["mode"] == "play"):
        wait(0.2)
    ok &= check("hk" in save_list(b, "cards"), "the steward's thanks: the Housekeeping card", save_list(b, "cards"))
    b.hold(["right", "space"], 0.7)
    b.hold("right", 0.4)
    ok &= check(b.state()["x"] > exact_x(189.5), "and she walks past it there", b.state())
    b.teleport(linen, D9)
    b.tap("e")
    wait(0.8)
    ok &= check(route(b) == "linen", "with it, into the linen room")
    # The laundry cart in her way: pushed forward up to his shelf it wakes him (near-catch 4); crawling is learned; the
    # cart on to the shaft's mouth, in from its rim, the shaft to its end, the drop into deck 8.
    b.hold("left", 0.9)
    b.tap("e")
    ok &= check(b.state()["mode"] == "push", "E at the laundry cart's end: she takes hold", b.state())
    b.key("left", True)
    ok &= check(wait_flag(b, "bb4"), "near-catch 4 on the bottle shelf: he is gone into the shaft", flags(b))
    ok &= check("crawl" in save_list(b, "verbs"), "crawling is learned there")
    ok &= check(wait_flag(b, "cart_linen", 8), "the laundry cart pushed to the shaft's mouth", b.state())
    b.key("left", False)
    ok &= check(into_the_shaft(b), "from the cart's rim, on hands and knees, into the shaft", b.state())
    s = through_the_shaft(b)
    ok &= check(route(b) == "inside" and s["y"] == D8 and 5 in save_list(b, "regions"),
                "out of its last grille, down into deck 8 forward: region 5", s)
    # Region 5: the lobby door opens from inside; the forward stairs go on up to deck 11.
    ok &= check(use_door(b, 8, 74, -1), "deck 8's lobby door opens from the corridor")
    (x0, y0), _ = flight_feet("stairs-forward-8-9")
    b.teleport(x0, y0)
    b.hold("up", 9.5)
    s = b.state()
    ok &= check(s["y"] == D11 and 6 in save_list(b, "regions"), "up the forward stairs to deck 11: region 6", s)
    # Region 6: the socks; near-catch 5 drains the pool; the hatch into deck 10.
    go(b, 11, 89.19)
    b.tap("e")
    wait(0.2)
    ok &= check("socks" in save_list(b, "verbs"), "the grip socks, in the gym")
    go(b, 11, 126)
    wait(0.8)
    ok &= check(b.state()["mode"] == "swim", "the first pool: she swims", b.state())
    hold_until(b, "right", lambda s: s["mode"] == "scripted", 8)
    ok &= check(wait_flag(b, "bb5", 16), "near-catch 5, from the water at the pool's rim", flags(b))
    ok &= check("drain" in flags(b), "and the pool drains")
    s = hold_until(b, [], lambda s: s["mode"] == "play" and s["y"] == D11 + 32, 8)
    ok &= check(s["mode"] == "play" and s["y"] == D11 + 32, "she is left standing in the empty tank", s)
    b.teleport(js(b, "window.__ship.world.data.hatchPool.x"), D11 + 32)
    wait(0.3)
    b.tap("e")
    s = hold_until(b, [], lambda s: s["mode"] == "play" and s["y"] == D10, 8)
    ok &= check(s["y"] == D10, "the hatch in its floor: down its ladder, and out of deck 10's hallway's ceiling", s)
    # Region 8: with the socks, up the sun cover's post at the Great Outdoors, along it to deck 12.
    b.teleport(exact_x(233) + 13, D11)
    b.key("space", True)
    wait(0.34)
    b.key("space", False)
    wait(0.02)
    b.key("left", True)
    b.key("space", True)
    wait(0.2)
    b.key("space", False)
    wait(1.0)
    b.key("left", False)
    s = b.state()
    ok &= check(s["y"] < D11 - 100, "a wall jump up the post lands her on the sun cover", s)
    # (Up the cover to the rail's foot, however long that takes: a jump begun short of it meets the
    # rail's side. Then over the rail early in a lull of the terrace's gusts: a jump in one falls short.)
    hold_until(b, "left", lambda s: s["x"] < exact_x(220) + 9, 6)
    wait_js(b, "(window.__ship.time.now / 1000) % window.__ship.world.data.topdeck.terrace.gust.every < 2.2", 9)
    b.hold(["left", "space"], 0.8)
    b.hold("left", 0.5)
    s = b.state()
    ok &= check(s["y"] == D12 and 8 in save_list(b, "regions"), "along the cover and over the rail: deck 12, region 8", s)
    # The engineer's coffee; then the ladder to the roof, the funnel's stairway in the lulls of its
    # wind, the top, the horn.
    b.teleport(LADDER_X, D12)
    b.hold("up", 0.6)
    ok &= check(b.state()["mode"] == "play" and "CREW ONLY" in blocked(b), "the technical ladder is chained off: the engineer wants his coffee", blocked(b))
    wait(1.0)
    ok &= check(coffee_for_the_engineer(b), "a hot coffee carried up past Teppanyaki's flares: he drinks it and goes up", flags(b)[-3:])
    wait(0.4)
    b.teleport(LADDER_X, D12)
    b.hold("up", 3.0)
    # (Off the ladder's top to the stairway's foot: until she is there, not for a time.)
    foot = b.eval("window.__ship.world.data.funnel.foot[0]")
    hold_until(b, "right" if b.state()["x"] < foot else "left", lambda s: abs(s["x"] - foot) < 6, 3)
    top = b.eval("window.__ship.world.data.funnel.y")
    gust = "window.__ship.world.story.funnelGusts.phase(window.__ship.time.now)"
    b.eval("(w => { w.def.swoop = 1000; w.nextAt = Infinity; })(window.__ship.world.story.funnelWind)")     # (the gulls are region8's own test)
    end = now() + 60
    # (Until she has stepped off its top, not only reached its height: on the clock stepped the look
    # comes the very frame she is level with it, still on the last step.)
    while now() < end and not ((s := b.state())["y"] <= top and s["mode"] == "play"):
        b.key("up", b.eval(gust) == "calm")
        wait(0.05)
    b.key("up", False)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == top, "up the funnel's stairway to its top", s)
    b.teleport(b.eval("window.__ship.world.data.topdeck.funnel.hornX") - 4, top)
    wait(0.3)
    b.tap("e")
    ok &= check(wait_flag(b, "horn", 20), "the horn, and what it sets off", flags(b))
    ok &= check(take_card(b, "off"), "the Officer's card, dropped on the sun deck")
    lady = b.eval("window.__ship.world.data.topdeck.lady.x")
    b.teleport(lady + 100, D12)
    hold_until(b, "left", lambda s: s["x"] < lady + 40, 3)
    b.tap("e")
    wait(0.2)
    ok &= check("parasol" in save_list(b, "verbs"), "and the parasol, at the empty sunbed")
    b.eval("window.__ship.lockedUntil = 0")
    # Region 9: the cake clears the forward lobby; down the bow with the gold card to the bridge.
    ok &= check(not use_door(b, 12, 82, 1), "Champs' door to the forward lobby is still shut: the wedding", alert(b))
    ok &= check(cake_for_the_planner(b), "the wedding cake from Cagney's to the planner: the party goes into the chapel", flags(b)[-3:])
    ok &= check(use_door(b, 12, 82, 1), "and Champs' door opens")
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
    wait(0.2)
    ok &= check(door_open(b, "bridge-door"), "and the bridge's door")
    b.hold("left", 3.0)
    ok &= check(wait_flag(b, "bb6"), "near-catch 6 on the bridge", flags(b))
    ok &= check("alarm" in flags(b), "the alarm")
    # Region 10 and the end: the hatch, the sunset, the glide down to the bow, the catch, home.
    ok &= check(out_of_the_hatch(b) and 10 in save_list(b, "regions"), "up the hatch's ladder to the balcony forward of the spa: the sunset", b.state())
    s = glide_to_the_bow(b)
    ok &= check(s["mode"] == "play" and s["y"] == D7 and s["x"] < x_of(21), "the parasol carries her down to the mooring deck", s)
    b.shot("golden-bow")
    ok &= check(catch_him(b), "at the tip of the bow, standing still: the catch", (b.state(), flags(b)))
    wait(1.8)
    b.eval("window.__ship.lockedUntil = 0")
    s = hold_until(b, "right", lambda s: s["x"] > exact_x(27), 16)
    ok &= check(s["x"] > exact_x(27), "the mooring deck's door is open: into deck 7 with Bumbot in her arms", s)
    ok &= check(home_with_him(b), "cabin 8206: home, the win screen, and the game goes on", flags(b))
    b.shot("golden-end")
    return ok


def carrying(b):
    return b.eval("window.__ship.world.carry && window.__ship.world.carry.kind")


def person(b, pid):
    return b.eval(f"(p => p && ({{ x: Math.round(p.x), on: p.on, state: p.state, aside: !!p.aside }}))(window.__ship.world.people.byId['{pid}'])")


def take_lunch(b):
    """A tray of lunch from the Seven Seas' pass."""
    b.teleport(exact_x(249.3542) - 12, D5)
    b.tap("e")
    wait(0.2)
    return carrying(b) == "lunch"


def scenario_region1(b):
    """Region 1 (docs/build-plan.md, step 1): the officer's lunch past the waiter, his card, the
    porter, the luggage, the rival at his rope."""
    b.open("?reset&play")
    ok = check(person(b, "npc_officer")["on"] and b.eval("window.__ship.world.people.byId.npc_officer.bubbleItems[0].visible"),
               "the gangway officer shows what he wants: a tray")
    # The Seven Seas' pass: the lunch stands on its counter from the start, hers to take only once Bumbot has been at it.
    lunch = "window.__ship.world.things.find(t => t.id === 'src_lunch')"
    ok &= check(b.eval(f"{lunch}.items.every(i => i.visible) && !{lunch}.interact()"), "the lunch on the pass to see, not hers before the beat")
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
    wait(0.22)
    lifted = y0 - b.state()["y"]
    b.key("space", False)
    wait(0.5)
    ok &= check(0 < lifted < 40 and carrying(b) == "lunch", "with a tray a jump is a low hop", lifted)
    b.eval("window.__ship.save.tangerines = 2")
    b.tap("d")
    ok &= check(not b.state()["lunging"], "and there is no lunge (the cry alone)")
    waiter = person(b, "haz_waiter")
    b.eval("(p => { p.pausedUntil = 0; p.aside = false; })(window.__ship.world.people.byId.haz_waiter)")
    b.teleport(person(b, "haz_waiter")["x"] + 60, D5)
    b.hold("left", 0.8)
    wait(0.4)
    ok &= check(carrying(b) is None and b.state()["mode"] == "play", "the waiter bumps the tray out of her hands: a spill, no scare", b.state())
    b.shot("region1-spill")
    # At a table he is out of the aisle: she slips past behind him.
    ok &= check(take_lunch(b), "the pass has another")
    b.teleport(person(b, "haz_waiter")["x"] + 300, D5)       # (people only move near her)
    b.eval("(p => { p.x = p.walk.stops[0] - 4; p.dir = 1; p.pausedUntil = 0; })(window.__ship.world.people.byId.haz_waiter)")
    wait(0.4)
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
    end = now() + 12
    while now() < end and "deck" not in save_list(b, "cards"):
        wait(0.2)
    ok &= check("deck" in save_list(b, "cards") and carrying(b) is None, "he eats, and hands her the Deck card", save_list(b, "cards"))
    wait(0.6)
    ok &= check(not b.eval("window.__ship.world.people.byId.npc_officer.bubbleItems[0].visible"), "his bubble is gone")
    b.shot("region1-card")
    # The porter's cart is a bump without a tray; hopped, it is nothing.
    b.eval("(p => { p.pausedUntil = 0; p.dir = 1; })(window.__ship.world.people.byId.haz_porter)")
    b.teleport(person(b, "haz_porter")["x"] + 90, D4)
    b.hold("left", 0.9)
    wait(0.2)
    ok &= check(b.state()["mode"] == "scripted" and "Oops" in alert(b), "the porter's cart: bumped", alert(b))
    wait(2.5)
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
    ok &= check(s["y"] == D5 and "WET FLOOR" in blocked(b), "the midship stairs: the cleaner's wet floor", blocked(b))
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
    end = now() + 12
    while now() < end and "deck" not in save_list(b, "cards"):
        wait(0.2)
    wait(0.8)
    return "deck" in save_list(b, "cards")


def enter_region2(b):
    """A save at region 2's door: near-catch 1 done, the Deck card, region 2 opened (as the golden
    path leaves it), so a region's own playtest need not replay the one before."""
    b.open("?reset&play")
    b.eval("(P => { P.setFlag('bb1'); P.setFlag('lunch'); P.open('cards', 'deck'); P.open('regions', 2); })(window.__ship.progress)")
    b.eval("window.__ship.cats.filter(c => c.flag === 'bb1').forEach(c => { c.gone = true; c.away = true; c.sprite.setVisible(false); })")
    wait(0.2)


def js(b, text):
    return b.eval(text)


def scenario_region1__pass(b):
    """Near-catch 1 at the Seven Seas' pass, as remade (docs/near-catch-1-remake-log.md): the counter and what stands
    on it, the cry and the dash at once, his way along the counter into the bowl, the bowl's fall and its three
    tangerines, how long she is held, the hint, the lunch; arriving in a jump; a reload after."""
    S = "window.__ship"
    cat = f"{S}.cats.find(c => c.name === 'bb1')"
    q = f"{S}.world.story.pass"
    b.open("?reset&play&at=pass5")
    cx, cf, top = b.eval(f"[{cat}.sprite.x, {cat}.floor, {cat}.sprite.y]")
    ok = check(cf - top == 33 and b.eval(f"{q}.counter.height") == 33, "he is on the pass's counter, 33 px over the floor", (cf - top))
    ok &= check(b.eval(f"{cat}.sprite.anims.currentAnim.key") == "bumbot-eat" and b.eval(f"Math.abs({q}.plate.x - ({cat}.sprite.x + 22)) < 1"),
                "eating, the plate under his mouth")
    ok &= check(b.eval(f"{q}.bowl.img.visible && {q}.bowl.img.x < {cat}.sprite.x - 40 && !{q}.fall.visible"), "the fruit bowl stands on the counter's forward end")
    ok &= check(b.eval(f"{S}.tangerines.filter(t => t.id.startsWith('tan_5_bowl')).length") == 0, "none of its tangerines out yet")
    ok &= check(b.eval(f"{S}.alert.visible") is not True or "dash" not in alert(b), "no hint yet")
    # Walking in: the scene starts 110 px out, he well in the picture: she stops and cries, and after a little pause
    # dashes (the user).
    hold_until(b, "right", lambda st: b.eval(f"{cat}.gone"), timeout=8)
    t0 = b.eval(f"{S}.time.now")
    x0 = b.state()["x"]
    ok &= check(100 <= cx - x0 <= 112, "the scene begins as she comes within 110 px of him", cx - x0)
    view = b.eval(f"(v => [v.x, v.right])({S}.cameras.main.worldView)")
    ok &= check(view[1] - (cx + 20) >= 60, "he is well inside the picture then, 60 px or more from its edge", view[1] - (cx + 20))
    ok &= check(b.eval(f"{S}.mode") == "scripted" and b.eval(f"{S}.bubbleUntil > {S}.time.now"), "her cry at once")
    b.wait(0.3)
    ok &= check(abs(b.state()["x"] - x0) < 1, "a little pause: 0.3 s after the cry she has not moved", b.state()["x"] - x0)
    ok &= check(b.eval(f"{cat}.sprite.anims.currentAnim.key") == "bumbot-look-back", "he looks back over his shoulder")
    b.wait(0.3)
    ok &= check(b.state()["x"] - x0 > 30, "then her dash", b.state()["x"] - x0)
    b.wait_for(f"{cat}.sprite.anims.currentAnim.key === 'bumbot-run'", timeout=3)
    ok &= check(b.eval(f"{cat}.sprite.flipX && {cat}.sprite.y === {top}"), "he bolts forward along the counter's top")
    ok &= check(b.eval(f"{cat}.sprite.depth < {S}.player.depth"), "behind her dash")
    b.wait_for(f"{q}.fall.visible", timeout=3)
    b.shot("pass-bowl")
    ok &= check(b.eval(f"!{q}.bowl.img.visible && {cat}.sprite.x < {q}.bowl.x + 40"), "the bowl goes off the end as he reaches it",
                b.eval(f"[{cat}.sprite.x, {q}.bowl.x]"))
    ok &= check(b.eval(f"{S}.tangerines.filter(t => t.id.startsWith('tan_5_bowl') && t.sprite.visible).length") == 3, "three tangerines out of it")
    ok &= check(abs(b.state()["x"] - (cx - 6)) < 2, "she is where he was", b.state()["x"] - cx)
    b.wait_for(f"{S}.mode === 'play'", timeout=6)
    held = (b.eval(f"{S}.time.now") - t0) / 1000
    ok &= check(held < 3.3, "she is held under 3.3 s (it was 8.3)", round(held, 2))
    b.shot("pass-after")
    ok &= check(b.eval(f"{cat}.away && !{cat}.sprite.visible"), "he is away, off the screen")
    ok &= check("bb1" in flags(b) and "dash" in save_list(b, "verbs"), "the beat is set, the dash is hers", flags(b))
    ok &= check(alert(b) == "D to dash", "one plate over her: D to dash", alert(b))
    st = b.state()
    ok &= check(abs(st["y"] - cf) < 1 and b.eval(f"{S}.player.body.enable"), "she stands on the floor, hers again", st["y"] - cf)
    rest = b.eval(f"{S}.tangerines.filter(t => t.id.startsWith('tan_5_bowl')).map(t => [Math.round(t.sprite.x - {q}.x0), Math.round(t.sprite.y - {cf})])")
    ok &= check(len(rest) == 3 and all(y == 0 and x < -64 for x, y in rest), "the three tangerines at rest on the floor, forward of the spilled fruit", rest)
    ok &= check(b.eval(f"{q}.fall.visible && {q}.fall.frame.name === {q}.L.fall.frames - 1"), "the bowl lies on the floor, its fruit spilled")
    # (The lunch pulses where E would take it, by its own pictures: its pulse was the old cabinet's.)
    b.teleport(exact_x(249.3542) - 12, D5)
    b.wait(0.5)
    hl = b.eval(f"{S}.highlight.state().filter(e => e.key === 'thing:src_lunch').map(e => e.parts.length)")
    ok &= check(hl == [2], "at the lunch, its tray and its cloche pulse", b.eval(f"JSON.stringify({S}.highlight.state())"))
    ok &= check(take_lunch(b), "the lunch on the counter is hers now")
    lunch = f"{S}.world.things.find(t => t.id === 'src_lunch')"
    ok &= check(b.eval(f"{lunch}.items.every(i => !i.visible)"), "and is off the counter while she carries it")
    b.eval(f"{S}.world.carryBox.give(); {S}.world.refresh()")
    ok &= check(b.eval(f"{lunch}.items.every(i => i.visible)"), "a fresh one stands there if she is left without it")
    b.eval(f"{S}.progress.setFlag('lunch')")
    ok &= check(b.eval(f"{lunch}.items.every(i => !i.visible)"), "and none once the officer has had his")

    # Arriving in a jump across his line of sight: she comes straight down where she crossed it, and the scene begins
    # as she lands; he is never jumped over.
    b.open("?reset&play&at=pass5")
    hold_until(b, "right", lambda st: cx - st["x"] < 160, timeout=8)
    b.key("right", True)
    b.key("space", True)
    b.wait_for(f"{cat}.gone", timeout=4)
    b.key("space", False)
    b.key("right", False)
    st = b.state()
    ok &= check(cf - st["y"] > 4 and 100 <= cx - st["x"] <= 112, "in a jump, she is taken as she crosses his line of sight, in the air", (cx - st["x"], cf - st["y"]))
    b.wait_for(f"{S}.bubbleUntil > {S}.time.now", timeout=3)
    st2 = b.state()
    ok &= check(abs(st2["y"] - cf) < 1 and abs(st2["x"] - st["x"]) < 2, "comes straight down, and cries as she lands, short of him", (st2["x"] - st["x"], st2["y"] - cf))
    b.wait_for(f"{S}.mode === 'play'", timeout=6)
    ok &= check(abs(b.state()["y"] - cf) < 1 and "bb1" in flags(b), "and ends with her on the floor", b.state()["y"] - cf)

    # A reload after it: he is gone, the bowl on the floor, its tangerines where they came to rest.
    b.open("?play&at=pass5")
    ok &= check(b.eval(f"{cat}.away && !{cat}.sprite.visible && {q}.fall.visible && !{q}.bowl.img.visible"), "after a reload: he is gone, the bowl lies fallen")
    ok &= check(b.eval(f"{S}.tangerines.filter(t => t.id.startsWith('tan_5_bowl') && t.sprite.visible).length") == 3, "and its three tangerines lie there")
    hold_until(b, "right", lambda st: st["x"] > cx - 40, timeout=8)
    ok &= check(b.eval(f"{S}.mode") == "play", "and nothing starts when she walks up")
    return ok


def scenario_region2__quiet(b):
    """Near-catch 2 at the Library's aft end, as remade (docs/near-catch-2-remake-log.md): he asleep on the return
    trolley, the scene 64 px from him, the librarian's shush, her tiptoe and her reach at his height, his leap and his
    way through the rope stand, the stand's fall into the door, the door open for good, how long she is held; arriving
    in a jump; a reload after; every lock open."""
    S = "window.__ship"
    cat = f"{S}.cats.find(c => c.name === 'bb2')"
    q = f"{S}.world.story.quiet"
    lib = f"{S}.world.people.byId['npc_librarian']"
    her = f"{S}.player.anims.currentAnim?.key"
    b.open("?reset&play&at=library")
    cx, cf, top = b.eval(f"[{cat}.sprite.x, {cat}.floor, {cat}.sprite.y]")
    trolley = b.eval(f"(t => [t.x, t.items[0].height])({S}.world.things.find(t => t.id === 'src_trolley'))")
    ok = check(cx == trolley[0] and cf - top == trolley[1] == 34, "he is on top of the return trolley, 34 px over the floor", (cx, cf - top, trolley))
    ok &= check(b.eval(f"{cat}.sprite.anims.currentAnim.key") == "bumbot-asleep", "asleep")
    door = b.eval(f"{q}.door.x")
    ok &= check(b.eval(f"{q}.stand.visible && {q}.card.visible && !{q}.fall.visible && !{q}.door.open"), "the rope stands before the shut aft door")
    ok &= check(0 < b.eval(f"{q}.stand.x") - cx < 130 and 0 < door - cx < 160, "the rope and the door within 160 px of him", (b.eval(f"{q}.stand.x") - cx, door - cx))
    # Walking in: taken 64 px from him; the librarian's finger at her lips; on tiptoe to arm's length.
    b.teleport(cx - 190, cf)
    hold_until(b, "right", lambda st: b.eval(f"{cat}.gone"), timeout=8)
    t0 = b.eval(f"{S}.time.now")
    x0 = b.state()["x"]
    ok &= check(58 <= cx - x0 <= 66, "the scene begins as she comes within 64 px of him", cx - x0)
    view = b.eval(f"(v => [v.x, v.right])({S}.cameras.main.worldView)")
    ok &= check(view[1] - (cx + 17) >= 100, "he is well inside the picture then", view[1] - (cx + 17))
    b.wait(0.1)
    ok &= check(b.eval(f"{S}.mode") == "scripted" and b.eval(her) == "her-creep-tiptoe", "she goes on tiptoe", b.eval(her))
    ok &= check(b.eval(f"{lib}.state") == "acting" and "shush" in b.eval(f"{lib}.sprite.anims.currentAnim.key"), "the librarian's finger is at her lips")
    b.wait(0.3)
    crept = b.state()["x"] - x0
    ok &= check(5 < crept < 16, "slowly: some 12 px in 0.4 s", crept)
    ok &= check(b.eval(f"{cat}.sprite.anims.currentAnim.key") == "bumbot-asleep", "he sleeps on")
    b.wait_for(f"{her} === 'her-creep-reach'", timeout=3)
    ok &= check(abs(cx - b.state()["x"] - 39) < 1, "she stops at arm's length, 39 px from him", cx - b.state()["x"])
    b.wait_for(f"{cat}.sprite.anims.currentAnim.key === 'bumbot-wake'", timeout=2)
    ok &= check(b.eval(f"{S}.player.anims.currentFrame.index") <= 3, "he wakes as she reaches", b.eval(f"{S}.player.anims.currentFrame.index"))
    b.wait_for(f"{cat}.sprite.anims.currentAnim.key === 'bumbot-leap'", timeout=2)
    ok &= check(b.eval(f"{S}.player.anims.currentFrame.index") >= 4, "and leaps as her hands arrive", b.eval(f"{S}.player.anims.currentFrame.index"))
    b.wait_for(f"{cat}.sprite.anims.currentAnim.key === 'bumbot-run'", timeout=2)
    ok &= check(b.eval(f"{cat}.sprite.y === {cf} && {cat}.sprite.x > {cx} + 40 && !{cat}.sprite.flipX"), "he lands aft of the trolley and bolts aft")
    ok &= check(b.eval(f"{cat}.sprite.depth > {q}.card.depth && {cat}.sprite.depth < {S}.player.depth"), "on our side of the stand")
    b.wait_for(f"{q}.fall.visible", timeout=2)
    ok &= check(b.eval(f"!{q}.stand.visible && !{q}.card.visible && {q}.drop.visible"), "his nose at the stand: it goes over, its card with it")
    ok &= check(not b.eval(f"{q}.door.open"), "the door still shut")
    b.wait_for(f"{q}.door.open", timeout=2)
    b.shot("quiet-crash")
    at = b.eval(f"[{cat}.sprite.x, {q}.fall.frame.name, {q}.L.door]")
    ok &= check(at[1] >= at[2] and at[0] + 18 <= door + 4, "the door opens as the stand's aft post is into it, and before his nose is there", at)
    view = b.eval(f"(v => [v.x, v.right])({S}.cameras.main.worldView)")
    ok &= check(view[1] - (door + 34) >= 30, "the open door well inside the picture, 30 px or more from its edge", view[1] - (door + 34))
    b.wait_for(f"({lib}.sprite.anims.currentAnim?.key || '').includes('flinch')", timeout=2)
    ok &= check(True, "the librarian starts at the crash")
    b.wait_for(f"{S}.mode === 'play'", timeout=6)
    held = (b.eval(f"{S}.time.now") - t0) / 1000
    ok &= check(held < 3.0, "she is held under 3 s (it was 3.5, and nothing of it was seen)", round(held, 2))
    b.shot("quiet-after")
    ok &= check(b.eval(f"{cat}.away && !{cat}.sprite.visible") and "bb2" in flags(b), "he is away, the beat is set", flags(b))
    ok &= check(b.eval(f"{q}.fall.visible && {q}.fall.frame.name === {q}.L.frames - 1 && {q}.flat.visible && !{q}.drop.visible && !{q}.stand.visible && !{q}.card.visible"),
                "the stand lies in the doorway, its card flat on the floor")
    ok &= check(b.eval(f"{q}.door.open && {q}.door.ajar"), "the door open for good")
    st = b.state()
    ok &= check(abs(st["y"] - cf) < 1 and b.eval(f"{S}.player.body.enable && !{S}.player.flipX && {S}.cameras.main.followOffset.x === 0"),
                "she stands on the floor, hers again, facing the way he went", st["y"] - cf)
    b.wait(2.5)
    ok &= check(b.eval(f"{q}.door.open") and b.eval(f"{lib}.dir") == -1, "the door stays open; the librarian is back at her desk's work")
    hold_until(b, "right", lambda st: st["x"] > door + 60, timeout=6)
    ok &= check(b.state()["x"] > door + 60 and 3 in save_list(b, "regions"), "she walks over the stand and through: region 3", b.state()["x"] - door)

    # Arriving in a jump across his line of sight: she comes straight down where she crossed it, and the scene begins
    # as she lands.
    b.open("?reset&play&at=library")
    b.teleport(cx - 190, cf)
    hold_until(b, "right", lambda st: cx - st["x"] < 105, timeout=8)
    b.key("right", True)
    b.key("space", True)
    b.wait_for(f"{cat}.gone", timeout=4)
    b.key("space", False)
    b.key("right", False)
    st = b.state()
    ok &= check(cf - st["y"] > 4 and 56 <= cx - st["x"] <= 66, "in a jump, she is taken as she crosses his line of sight, in the air", (cx - st["x"], cf - st["y"]))
    b.wait_for(f"{her} === 'her-creep-tiptoe' || {her} === 'her-creep-reach'", timeout=3)
    st2 = b.state()
    ok &= check(abs(st2["y"] - cf) < 1 and abs(st2["x"] - st["x"]) < 3, "comes straight down, and creeps on from there", (st2["x"] - st["x"], st2["y"] - cf))
    b.wait_for(f"{S}.mode === 'play'", timeout=6)
    ok &= check(abs(b.state()["y"] - cf) < 1 and "bb2" in flags(b), "and ends with her on the floor", b.state()["y"] - cf)

    # A reload after it: he is gone, the stand lies in the open door.
    b.open("?play&at=library")
    ok &= check(b.eval(f"{cat}.away && !{cat}.sprite.visible && {q}.fall.visible && {q}.flat.visible && !{q}.stand.visible && {q}.door.open"),
                "after a reload: he is gone, the stand lies fallen, the door is open")
    b.teleport(cx - 100, cf)
    hold_until(b, "right", lambda st: st["x"] > cx - 20, timeout=8)
    ok &= check(b.eval(f"{S}.mode") == "play", "and nothing starts when she walks up")

    # Every lock open (no rope was ever there): he bolts through the door all the same.
    b.open("?reset&play&at=library&cards=all")
    b.teleport(cx - 100, cf)
    hold_until(b, "right", lambda st: b.eval(f"{cat}.gone"), timeout=8)
    b.wait_for(f"{S}.mode === 'play'", timeout=6)
    ok &= check("bb2" in flags(b) and b.eval(f"{cat}.away && !{q}.fall.visible && !{q}.flat.visible && {q}.door.open"),
                "with every lock open: no stand to fall, the door open after him", flags(b))
    return ok


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
    wait(0.5)
    x0 = js(b, f"{robot}.x")
    wait(0.6)
    ok &= check(abs(js(b, f"{robot}.x") - x0) < 1 and js(b, f"{robot}.beep.visible") is not None, "the robot stops while she stands in its way", x0)
    b.shot("region2-robot")
    b.teleport(exact_x(31), D6)
    wait(0.5)
    x1 = js(b, f"{robot}.x")
    ok &= check(x1 > x0 + 4, "and trundles on when she is behind it", (x0, x1))
    b.hold("right", 0.5)
    ok &= check(b.state()["x"] < js(b, f"{robot}.x"), "it is in the way like a cart", b.state())
    # Onto its top with a hop, and along with it to the tangerine on the hose cabinet.
    js(b, f"(r => {{ r.x = {exact_x(29.5)}; r.dir = -1; r.pausedUntil = 0; }})({robot})")
    top = js(b, f"{robot}.def.y - {robot}.h")
    b.teleport(js(b, f"{robot}.x"), top)
    wait(0.3)
    xa = b.state()["x"]
    wait(1.0)
    s = b.state()
    ok &= check(s["y"] == top and xa - s["x"] > 20, "she rides on its top", (xa, s))
    end = now() + 8
    while now() < end and b.state()["x"] > exact_x(26.94) + 6:
        wait(0.05)
    b.tap("space")
    wait(0.5)
    ok &= check("tan_6_high" in save_list(b, "collected"), "a hop from its top takes the tangerine on the fire-hose cabinet", b.state())
    # The cabin being made up: a peek.
    maid = room(b, "maid6")
    b.teleport(maid["doors"][0]["outX"], D6)
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "maid6" and person(b, "amb_maid")["on"], "the cabin being made up: in through its open door", route(b))
    b.shot("region2-cabin")
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "inside", "and out again", route(b))
    # Bliss: standing still on the dance floor, she dances.
    b.teleport(exact_x(117.2), D6)
    wait(3.6)
    ok &= check(b.state()["mode"] == "scripted" and js(b, "window.__ship.player.anims.currentAnim.key") == "her-dance",
                "three seconds still on Bliss's dance floor: she dances", b.state())
    b.shot("region2-dance")
    wait(3.4)
    ok &= check(b.state()["mode"] == "play", "and stops", b.state())
    # The Photo Studio's flash: caught in it she poses; no scare.
    b.teleport(exact_x(133.6), D6)
    end = now() + 9
    posed = False
    while now() < end and not posed:
        posed = b.state()["mode"] == "scripted"
        wait(0.05)
    ok &= check(posed, "caught in the studio's flash she poses")
    b.shot("region2-flash")
    wait(1.4)
    s = b.state()
    ok &= check(s["mode"] == "play" and abs(s["x"] - exact_x(133.6)) < 4, "and that is all: no scare", s)
    # The promenade: the jogger bumps her; standing aside (↑) lets him by.
    jog = "window.__ship.world.people.byId.haz_jogger"
    js(b, f"(p => {{ p.x = {exact_x(180)}; p.pausedUntil = window.__ship.time.now + 600000; }})({jog})")
    b.teleport(exact_x(150), D6, "promenade")
    b.key("up", True)
    wait(0.2)
    js(b, f"(p => {{ p.x = {exact_x(153)}; p.dir = -1; p.pausedUntil = 0; }})({jog})")
    # (Until he is by, not for a time: the 1.8 s this was had real time's slack in it.)
    end = now() + 4
    while now() < end and b.state()["mode"] == "play" and person(b, "haz_jogger")["x"] >= exact_x(150):
        wait(0.1)
    s = b.state()
    b.key("up", False)
    ok &= check(s["mode"] == "play" and person(b, "haz_jogger")["x"] < exact_x(150), "standing aside by the wall (↑), the jogger runs by", (s, person(b, "haz_jogger")))
    b.shot("region2-jogger")
    js(b, f"(p => {{ p.x = {exact_x(153)}; p.dir = -1; p.pausedUntil = 0; }})({jog})")
    wait(1.6)
    ok &= check(b.state()["mode"] == "scripted" and "Oops" in alert(b), "in his lane, he bumps her", alert(b))
    ok &= check(js(b, "window.__ship.worldLayer.list.some(o => o.anims?.currentAnim?.key === 'gags-jog-bowled')")
                and (js(b, f"{jog}.sprite.anims.currentAnim?.key") or "").startswith("people-jogger-s"),
                "9b: bowled back onto her bottom; he stops and scratches the back of his head", js(b, f"{jog}.sprite.anims.currentAnim?.key"))
    wait(2.6)
    b.wait_for("window.__ship.mode === 'play'", 3)
    ok &= check(b.state()["mode"] == "play", "a scare: she is back at a checkpoint", b.state())
    # He can be hopped. (Moved by hand he lets go of a door he was going through first: 9b's gag, 2026-11-19,
    # stops him in the doorway he met her in, and he would be behind a door still his.)
    js(b, f"(p => {{ if (p.through) {{ window.__ship.letGoDoor(p.through, p); p.through = null; }} p.x = {exact_x(180)}; p.pausedUntil = window.__ship.time.now + 600000; }})({jog})")
    b.teleport(exact_x(150), D6, "promenade")
    js(b, f"(p => {{ p.x = {exact_x(152.2)}; p.dir = -1; p.pausedUntil = 0; }})({jog})")
    # (Standing still, the hop wants timing; running at him it is easy. He stops by her for 0.45 s,
    # then runs on: she jumps 0.15 to 0.25 s into that pause (seen within a tenth; it clears him from
    # 0.1 to 0.3 s), so that she is high as he passes. A fixed 0.58 s from his start passed only with
    # real time's slack.)
    b.wait_for(f"{jog}.pausedUntil > window.__ship.time.now", 3)
    wait(0.15)
    b.hold("space", 0.8)
    end = now() + 2     # (until he is by)
    while now() < end and b.state()["mode"] == "play" and person(b, "haz_jogger")["x"] >= exact_x(150):
        wait(0.1)
    ok &= check(b.state()["mode"] == "play" and person(b, "haz_jogger")["x"] < exact_x(150), "or hopped", (b.state(), person(b, "haz_jogger")))
    js(b, f"(p => {{ p.pausedUntil = window.__ship.time.now + 600000; }})({jog})")
    # The gulls on the rail fly up as she comes near, and settle again.
    gull = "window.__ship.world.movers.find(m => m.def?.id === 'gull_prom_2')"
    b.teleport(exact_x(170), D6, "promenade")
    wait(0.4)
    ok &= check(js(b, f"{gull}.rise") == 0, "a gull sits on the rail")
    # (On the way: two black ears in a porthole.)
    b.hold("right", 1.6)
    ok &= check("glimpse_window" in flags(b), "two black ears show in a porthole as she passes", flags(b))
    b.teleport(exact_x(174), D6, "promenade")
    wait(0.7)
    ok &= check(js(b, f"{gull}.rise") > 0.5, "and flies up as she comes near", js(b, f"{gull}.rise"))
    b.shot("region2-gull")
    b.teleport(exact_x(185), D6, "promenade")
    wait(3.2)
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
    # (In through its roof hatch since 2026-11-21, the user: she climbs up behind the boat into it, about 2 s.)
    ok &= check(wait_js(b, "window.__ship.route === 'lifeboat' && window.__ship.mode === 'ladder'", 7) and b.state()["y"] < boat["floor"] - 40,
                "the one lifeboat with its hatch open: up behind it, in through the hatch, on the top of its ladder", (route(b), b.state()))
    s = hold_until(b, "down", lambda s: s["mode"] == "play", 4)
    ok &= check(s["y"] == boat["floor"], "down the ladder to its floor", s)
    b.teleport(boat["x0"] + 46, boat["floor"], "lifeboat")
    b.shot("region2-lifeboat")
    js(b, "window.__skipCloseups = false")      # (this once: the cover's moment, plan-the-rest §2.3)
    b.tap("e")
    wait(0.4)
    ok &= check(js(b, "window.__ship.save.books['2']") == "held", "the second book, on its bench", js(b, "JSON.stringify(window.__ship.save.books)"))
    shown = js(b, "window.__ship.viewing && window.__ship.uiLayer.list.some(o => o.texture && o.texture.key === 'cover-2')")
    b.shot("region2-cover")
    wait(0.5)
    b.tap("e")
    wait(0.5)
    ok &= check(shown and not js(b, "window.__ship.viewing"), "its cover shows over the screen as she takes it, and a key closes it", shown)
    js(b, "window.__skipCloseups = true")
    b.teleport(boat["x0"] + 228, boat["floor"], "lifeboat")
    b.tap("e")
    wait(0.9)
    ok &= check(b.state()["mode"] == "scripted", "the photo in its frame opens over the screen", b.state())
    b.shot("region2-photo")
    b.tap("e")
    wait(0.6)
    ok &= check(b.state()["mode"] == "play" and "slot_lifeboat" in save_list(b, "seen"), "and closes on a key", b.state())
    b.teleport(boat["doors"][0]["x"], boat["floor"], "lifeboat")
    b.key("up", True)
    out = wait_js(b, "window.__ship.route === 'promenade'", 5)
    b.key("up", False)
    ok &= check(out and wait_js(b, "window.__ship.mode === 'play'", 7) and b.state()["y"] == boat["floor"],
                "up the ladder past its top, out of the hatch and down behind the boat onto the walkway again", (route(b), b.state()))
    # The Library. Bumbot is asleep on its return trolley, so near-catch 2 comes first (its own case: `region2.quiet`): asleep on the return trolley; he knocks the rope stand into the aft door.
    shut = not use_door(b, 6, 194, -1)
    ok &= check(shut and "QUIET" in blocked(b), "the Library's aft door is roped off: QUIET PLEASE", blocked(b))
    # Running up to her desk: a finger to her lips (and the scene, 64 px from him).
    b.teleport(exact_x(188.5), D6)
    b.hold("right", 0.7)
    ok &= check(person(b, "npc_librarian")["state"] == "acting", "she runs past the desk: the librarian's finger goes to her lips", person(b, "npc_librarian"))
    ok &= check(wait_flag(b, "bb2"), "near-catch 2: he bolts from the return trolley", flags(b))
    wait(3.0)                   # (the librarian's start at the crash and her look at the door)
    # The Library: her bubble while a book is out, the trolley, the shelf, the chair.
    lib = js(b, "window.__ship.world.data.library")
    b.teleport(lib["trolley"]["x"] - 40, D6)
    wait(0.4)
    ok &= check(js(b, "window.__ship.world.people.byId.npc_librarian.bubbleItems[0].visible"), "the librarian shows a book while she carries one")
    b.shot("region2-librarian")
    b.teleport(lib["trolley"]["x"], D6)
    b.tap("e")
    end = now() + 6
    while now() < end and js(b, "window.__ship.save.books['2']") != "returned":
        wait(0.1)
    wait(0.8)
    ok &= check(js(b, "window.__ship.save.books['2']") == "returned" and b.state()["mode"] == "play", "E at the return trolley: she shelves it",
                js(b, "JSON.stringify(window.__ship.save.books)"))
    ok &= check(not js(b, "window.__ship.world.people.byId.npc_librarian.bubbleItems[0].visible"), "and her bubble is gone")
    b.shot("region2-shelf")
    # With several books on her, the trolley's row: she chooses which goes back (the user, 2026-11-22).
    L2 = "window.__ship.world.library"
    js(b, f"{L2}.got(7); {L2}.got(9)")
    b.tap("e")
    wait_js(b, f"!!{L2}.choosing", 3)
    row = js(b, f"{L2}.choosing && [{L2}.choosing.verb, {L2}.choosing.books]")
    wait(0.3)
    b.tap("e")
    wait_js(b, "window.__ship.save.books['9'] === 'returned'", 5)
    wait_js(b, f"!!{L2}.choosing", 3)
    again = js(b, f"{L2}.choosing && {L2}.choosing.books")
    b.tap("escape")
    wait(0.8)
    ok &= check(row == ["return", [7, 9]] and again == [7] and js(b, "window.__ship.save.books['7']") == "held" and b.state()["mode"] == "play",
                "two books on her: the trolley's row, the chosen goes back, the row again on the other, Esc keeps it", (row, again))
    js(b, "(s => { delete s.books[7]; delete s.books[9]; s.bookOrder = s.bookOrder.filter(n => n !== 7 && n !== 9); })(window.__ship.save)")
    js(b, f"{L2}.refresh()")
    # (Reading, the user, 2026-11-21: she sits facing us in the armchair, the books she carries in a row; E reads.)
    L = "window.__ship.world.library"
    js(b, f"{L}.got(6)")
    b.teleport(lib["chair"]["x"], D6)
    b.tap("e")
    wait_js(b, f"!!{L}.choosing", 3)
    # (Every book she has found is in the row, a given-back one greyed: the user, 2026-11-22; the chosen one the last she
    # can read.)
    ok &= check(js(b, f"JSON.stringify({L}.choosing && {L}.choosing.books)") == "[2,6]" and js(b, f"{L}.choosing.at") == 1
                and not js(b, "window.__ship.player.visible") and js(b, f"{L}.readingPic.frame.name") == "chair-4",
                "in the red chair she sits facing us, the books she found in the row (book 2, given back, greyed), on the one she carries",
                js(b, f"JSON.stringify({L}.choosing && {L}.choosing.books)"))
    js(b, f"(() => {{ {L}.got(2); window.__ship.save.books['2'] = 'returned'; }})()")
    b.tap("e")
    wait_js(b, f"!{L}.choosing && window.__ship.uiLayer.list.some(o => o.texture && o.texture.key === 'page-6')", 3)
    wait(0.6)                   # (a page takes no key for its first 0.45 s: the E that opened it must not close it)
    b.shot("region2-page")
    ok &= check(True, "E: she opens it, its first page shows")
    b.tap("e")
    wait_js(b, f"!!{L}.choosing", 3)
    ok &= check(6 in save_list(b, "read"), "a key closes it and the row is back: she may read again", save_list(b, "read"))
    b.tap("escape")
    wait_js(b, f"!{L}.reading && window.__ship.mode === 'play'", 3)
    ok &= check(b.state()["mode"] == "play" and js(b, "window.__ship.player.visible"), "Esc: she gets up", b.state())
    # The six armchairs at the reading tables are seats too, in full colours.
    chairs = js(b, f"JSON.stringify({L}.data.chairs)")
    ok &= check(len(json.loads(chairs)) == 7, "seven armchairs to read in", chairs)
    b.teleport(json.loads(chairs)[4]["x"], D6)
    b.tap("e")
    wait_js(b, f"!!{L}.choosing", 3)
    ok &= check(js(b, f"{L}.readingPic && {L}.readingPic.x") == json.loads(chairs)[4]["x"] - 34, "and in one at a reading table",
                js(b, f"{L}.readingPic && {L}.readingPic.x"))
    b.tap("escape")
    wait_js(b, f"!{L}.reading && window.__ship.mode === 'play'", 3)
    # (Near-catch 2 was at her first coming to the trolley, above.)
    b.teleport(exact_x(191), D6)
    wait(0.5)
    ok &= check(door_open(b, "part-door-6-194") and js(b, "(q => q.fall.visible && q.fall.frame.name === q.L.frames - 1)(window.__ship.world.story.quiet)"),
                "the rope stand lies where he knocked it; the door stands open")
    b.shot("region2-door")
    wait(2.0)
    ok &= check(door_open(b, "part-door-6-194"), "and stays so")
    b.hold("right", 1.6)
    ok &= check(3 in save_list(b, "regions"), "through it: region 3", b.state())
    # Deck 7's lobbies: the ways up are busy, each with its own thing.
    for core, sign in (("forward", "DELIVERY"), ("atrium", "CARPET"), ("midship", "ART AUCTION")):
        f = js(b, f"(f => [f.bottom.x, f.bottom.y])(window.__ship.flights.find(g => g.name === 'stairs-{core}-7-8'))")
        b.teleport(f[0], f[1])
        b.hold("up", 0.5)
        ok &= check(b.state()["y"] == f[1] and sign in blocked(b), f"deck 7, the {core} flight up: {sign}", blocked(b))
    ok &= check(person(b, "blk_fitter")["on"], "the carpet fitter is at his roll")
    b.shot("region2-carpet")
    return ok


def enter_region3(b):
    """A save at region 3's door: regions 1 and 2 done (the Deck card, the Library's door ajar)."""
    b.open("?reset&play")
    b.eval("(P => { ['bb1', 'lunch', 'bb_lift', 'bb2', 'riv_prom', 'glimpse1', 'glimpse_window'].forEach(f => P.setFlag(f));"
           " P.open('cards', 'deck'); P.open('regions', 2); P.open('regions', 3); })(window.__ship.progress)")
    b.eval("window.__ship.cats.filter(c => c.flag === 'bb1' || c.flag === 'bb2').forEach(c => { c.gone = true; c.away = true; c.sprite.setVisible(false); })")
    wait(0.2)


def enter_region4(b):
    """A save at region 4's door: regions 1-3 done (the Deck and Entertainment cards, the stage's
    beat), she has just come up the red trunk to deck 9."""
    b.open("?reset&play")
    b.eval("(P => { ['bb1', 'lunch', 'bb_lift', 'bb2', 'riv_prom', 'glimpse1', 'glimpse_window', 'bb3', 'pills'].forEach(f => P.setFlag(f));"
           " P.open('cards', 'deck'); P.open('cards', 'ent'); [2, 3, 4].forEach(r => P.open('regions', r)); })(window.__ship.progress)")
    b.eval("window.__ship.cats.filter(c => ['bb1', 'bb2', 'bb3'].includes(c.flag)).forEach(c => { c.gone = true; c.away = true; c.sprite.setVisible(false); })")
    b.eval("window.__ship.world.refresh()")
    wait(0.2)


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
    wait(0.9)
    b.teleport(cabin["x0"] + 172, D4, "smcabin")
    b.tap("e")
    wait(0.4)
    if "pills" not in save_list(b, "items"):
        return False
    b.teleport(cabin["doors"][0]["x"], D4, "smcabin")
    b.tap("e")
    wait(0.9)
    b.teleport(tx, D4)
    b.tap("e")
    hold_until(b, "up", lambda s: s["y"] == D6, 8)
    b.hold("left", 0.4)
    # (He stands aft of centre stage since 2026-11-24, the dancers at the aft curtain: near-catch 3 remade.)
    b.teleport(exact_x(248.5) + 26, D6)
    b.tap("e")
    end = now() + 12
    while now() < end and "ent" not in save_list(b, "cards"):
        wait(0.2)
    wait(0.8)
    return "ent" in save_list(b, "cards") and b.state()["mode"] == "play"


def scenario_region3__stage(b):
    """Near-catch 3 on the Stardust's stage, as remade (docs/near-catch-3-remake-log.md): the stage one picture, Bumbot
    at centre stage in his spotlight under the rope's loop, the stage manager with his back to him and not sneezing,
    the dancers at the aft curtain; the scene 154 px from him, the rival out of the wing ahead of her, the net on the
    lamp, the lamp down as the loop goes up, the hatch, the flour, his first sneeze, how long she is held; where it
    leaves her against the swinging lamp; arriving in a jump, off the balcony; a reload after."""
    S = "window.__ship"
    cat = f"{S}.cats.find(c => c.flag === 'bb3')"
    q = f"{S}.world.story.stage"
    P = f"{S}.world.people.byId"
    sm, dh, dm = f"{P}['npc_stagemanager']", f"{P}['amb_dancer_her']", f"{P}['amb_dancer_him']"
    her = f"{S}.player.anims.currentAnim?.key"
    clip = lambda who: f"({who}.sprite.anims.currentAnim?.key || '')"
    b.open("?reset&play&at=stage")
    st = b.eval(f"{S}.world.data.stage")
    cx, cf = b.eval(f"[{cat}.sprite.x, {cat}.floor]")
    F, top, x0 = st["floor"], st["top"], st["x"]
    ok = check(b.eval(f"{S}.worldLayer.list.some(o => o.texture?.key === 'stage-back' && o.x === {x0} && o.y === {F})"), "the stage is its own picture")
    ok &= check(not b.eval(f"{S}.worldLayer.list.some(o => /^(grand-piano|guitar|mic-stand|drum-kit)/.test(o.frame?.name || '') && Math.abs(o.y - {F}) < 2 && o.x > {x0} && o.x < {x0} + 320)"),
                "no piano, guitar or mic stand on it (the drum kit is in its picture)")
    # (The user, 2026-11-24: the stage "pops out too much": the theatre's pieces washed 6%, they were at 12%; the
    # stage's picture 12%, it was in full colour.)
    names = b.eval(f"[...new Set({S}.worldLayer.list.filter(o => o.texture?.key === 'shipart' && Math.abs(o.y - {F}) < 2 && o.x > {x0} - 1900 && o.x < {x0}).map(o => String(o.frame.name)).filter(n => /^(theatre-seat|audience|speaker-stack)/.test(n)).map(n => n.replace(/^.*-/, '')))]")
    ok &= check(names == ["w6"], "the theatre's seats, its audience and its speakers washed 6%", names)
    px = b.eval(f"(t => {{ const c = document.createElement('canvas'); c.width = 4; c.height = 4; const g = c.getContext('2d'); g.drawImage(t.getSourceImage(), 80, 60, 4, 4, 0, 0, 4, 4); return [...g.getImageData(0, 0, 1, 1).data]; }})({S}.textures.get('stage-back'))")
    ok &= check(px[0] > 35 and px[1] > 35, "the stage's picture washed toward the wall: its star cloth is not near black", px)
    ok &= check(b.eval(f"{cat}.sprite.anims.currentAnim.key") == "bumbot-wash" and abs(cx - (x0 + 158)) <= 2, "Bumbot washes at centre stage", cx - x0)
    ok &= check(abs(st["ropeX"] - 16.5 - cx) <= 1 and b.eval(f"{q}.ropeEnd") == F - 40, "the rope's loop over him, 40 px up", (st["ropeX"] - cx, F - b.eval(f"{q}.ropeEnd")))
    ok &= check(abs(st["spotX"] - cx) < 30, "under a lantern of the lighting bar", st["spotX"] - cx)
    ok &= check(b.eval(f"{q}.shut.visible && !{q}.open.visible"), "the hatch is shut")
    lamp = f"{q}.light"
    ok &= check(b.eval(f"!{lamp}.lamp.swinging && Math.abs({lamp}.lamp.y - ({top} + {lamp}.def.short)) < 1"), "the lamp hauled up, still")
    places = b.eval(f"[{sm}.x, {sm}.dir, {dh}.x, {dm}.x]")
    ok &= check(cx < places[0] < places[2] < places[3] and places[1] == 1, "the stage manager between Bumbot and his dancers, turned to them: his back to the cat", places)
    ok &= check(b.eval(clip(dh)).endswith("-dance") and b.eval(clip(dm)).endswith("-dance"), "the dancers rehearsing at the aft curtain")
    b.teleport(cx - 215, cf)
    sneezed = False
    end = now() + 6
    while now() < end:
        sneezed = sneezed or "sneeze" in b.eval(clip(sm))
        wait(0.1)
    ok &= check(not sneezed, "he does not sneeze before he has seen the cat")

    # Walking in: taken 154 px from him, in front of the forward curtain; the whole stage in the picture.
    hold_until(b, "right", lambda s: b.eval(f"{cat}.gone"), timeout=8)
    t0 = b.eval(f"{S}.time.now")
    hx = b.state()["x"]
    ok &= check(146 <= cx - hx <= 156 and hx < x0 + 36, "the scene begins 154 px from him, she in front of the forward curtain", (cx - hx, hx - x0))
    b.wait(0.1)
    ok &= check(b.eval(f"{S}.mode") == "scripted" and b.eval(her) == "her-creep-tiptoe", "she starts toward him on tiptoe", b.eval(her))
    b.wait(0.15)
    ok &= check("notice" in b.eval(clip(sm)) and b.eval(f"{sm}.dir") == -1, "the stage manager turns and starts at the cat", (b.eval(clip(sm)), b.eval(f"{sm}.dir")))
    # (One thing after another, the user, 2026-11-24: the shout stops her mid-step; Bumbot looks up; then the rival.)
    b.wait(0.3)
    ok &= check(b.eval(her) == "her-creep-tiptoe" and b.eval(f"{S}.player.anims.isPaused") and b.eval(f"!{P}['riv_stage']"),
                "the shout stops her mid-step, before anyone else has come", b.eval(her))
    ok &= check(b.eval(f"{cat}.sprite.anims.currentAnim.key") == "bumbot-stand-up" and b.eval(f"{cat}.sprite.y") == cf, "Bumbot has looked up from his washing, and stands")
    riv = f"{P}['riv_stage']"
    b.wait_for(f"{riv} && {riv}.on", timeout=2)
    tr = b.eval(f"{S}.time.now") - t0
    ok &= check(b.eval(f"{riv}.x") >= st["wingX"] and b.eval(f"{riv}.sprite.isCropped"), "the rival comes out from behind the proscenium's edge")
    ahead, back = True, None
    end = now() + 2
    while now() < end and not b.eval(f"{q}.snag.visible"):
        r = b.eval(f"{riv}.on ? [{riv}.x, {riv}.sprite.frame.cutX + {riv}.sprite.x - 40] : null")
        if r and b.eval(f"{riv}.x") - 18 > x0 + 36:
            ahead = ahead and r[0] - 18 > b.state()["x"] + 8
        if b.eval(her) == "her-start-back" and back is None:
            back = b.eval(f"{S}.time.now") - t0
        wait(0.02)
    ok &= check(ahead, "ahead of her all the way: never across her")
    ok &= check(back is not None and 0 <= back - tr <= 160 and b.state()["x"] - hx < 16, "she starts back as he bursts out, a few steps in", (tr, back, b.state()["x"] - hx))
    ok &= check(tr >= 700, "and he comes only once the stage manager's start has been seen", tr)
    ok &= check(b.eval(f"{dh}.dir === -1 && {dm}.dir === -1") and not b.eval(clip(dh)).endswith("-dance"), "the dancers have stopped and turned", b.eval(clip(dh)))
    view = b.eval(f"(v => [v.x, v.right])({S}.cameras.main.worldView)")
    b.wait_for(f"{q}.snag.frame.name >= 5", timeout=2)
    view = b.eval(f"(v => [v.x, v.right])({S}.cameras.main.worldView)")
    ok &= check(view[0] <= hx - 20 and view[1] >= x0 + 320, "she and the whole stage, to its aft curtain, in the picture", (hx - view[0], view[1] - x0 - 320))
    ok &= check(b.eval(f"{cat}.sprite.anims.currentAnim.key") == "bumbot-rope" and b.eval(f"!{riv}.on"), "Bumbot is in the loop as the net catches the lamp")
    ok &= check(b.eval(f"!!{lamp}.held && {q}.snag.depth > {lamp}.pic.depth"), "the lamp held by his net, behind it")
    b.shot("stage-snag")
    # The lamp down, the loop up: one line.
    pairs = []
    t5 = b.eval(f"{S}.time.now")
    end = now() + 3
    while now() < end and not b.eval(f"{q}.open.visible"):
        pairs.append(b.eval(f"[{lamp}.lamp.y, {q}.ropeEnd, {q}.snag.frame.name, {S}.time.now]"))
        wait(0.02)
    hung = next((t for y, r, f, t in pairs if f >= 8), t5) - t5
    ok &= check(hung >= 500, "he dangles on the lamp half a second and more before it gives", round(hung))
    fell = pairs[-1][3] - next((t for y, r, f, t in pairs if f >= 8), t5)
    ok &= check(fell >= 400, "and it comes down slowly enough to be followed, the loop going up with it", round(fell))
    pairs = [x[:3] for x in pairs]
    lamp0, rope0 = top + b.eval(f"{lamp}.def.short"), F - 40
    worst = max(abs((rope0 - r) - 1.7 * (y - lamp0)) for y, r, f in pairs)
    ok &= check(max(y for y, r, f in pairs) - lamp0 > 25 and worst < 30, "the loop goes up as the lamp comes down, 1.7 px for each of its px", (round(max(y for y, r, f in pairs) - lamp0), round(worst)))
    ok &= check(b.eval(f"{q}.open.visible && !{q}.shut.visible"), "he drops onto the hatch: it gives way")
    b.wait(0.12)
    ok &= check(b.eval(f"{lamp}.lamp.swinging && !{lamp}.held"), "let go, the lamp swings")
    seen = b.eval(f"(k => k.visible ? k.y - k.height + (k.isCropped ? k._crop.y : 0) : null)({cat}.sprite)")
    ok &= check(seen is None or seen >= top, "nothing of Bumbot over the stage's top", seen)
    b.wait_for(f"{q}.puff.visible", timeout=2)
    ok &= check(b.eval(f"!{q}.snag.visible && {cat}.away && !{cat}.sprite.visible"), "the rival is gone down it, Bumbot up into the flies; flour comes up")
    b.shot("stage-flour")
    b.wait_for(f"{clip(sm)}.includes('sneeze')", timeout=2)
    ok &= check(b.eval(f"{S}.mode") == "scripted", "the stage manager's first sneeze, before she is freed")
    b.wait_for(f"{her} === 'her-shrug'", timeout=2)
    b.wait_for(f"{S}.mode === 'play'", timeout=4)
    held = (b.eval(f"{S}.time.now") - t0) / 1000
    ok &= check(3.6 <= held <= 4.8, "she is held about 4.3 s: at 2.65 s it was too fast to follow (the user); it was 4.75 before the remake", round(held, 2))
    b.shot("stage-after")
    ok &= check("bb3" in flags(b) and b.eval(f"!{dh}.on && {P}['amb_dancer_her_off'].on && {P}['amb_dancer_her_off'].x === {places[2]} && {P}['amb_dancer_him_off'].x === {places[3]}"),
                "the beat is set; the dancers stand where they rehearsed")
    ok &= check(b.eval(f"{q}.ropeEnd") < top + 20 and b.eval(f"{sm}.dir") == -1, "the loop is up behind the valance; the stage manager faces the hole", b.eval(f"{q}.ropeEnd") - top)
    s0 = b.state()
    ok &= check(abs(s0["y"] - cf) < 1 and b.eval(f"{S}.player.body.enable && !{S}.player.flipX && {S}.cameras.main.followOffset.x === 0"), "she stands on the floor, hers again, facing aft")
    # Where it leaves her, the swinging lamp does not reach; and he sneezes on.
    sneezed, hit = False, False
    end = now() + 9
    while now() < end:
        sneezed = sneezed or "sneeze" in b.eval(clip(sm))
        hit = hit or b.eval(f"{S}.mode") != "play"
        wait(0.1)
    ok &= check(not hit, "nine seconds standing where it left her: the lamp does not reach her")
    ok &= check(sneezed, "and the stage manager sneezes again")
    ok &= check(b.eval(f"{sm}.bubbleItems[0].visible") is False, "his pills' bubble only when she is near")

    # Arriving in a jump across his line of sight: straight down where she crossed it, and the scene from there.
    b.open("?reset&play&at=stage")
    hold_until(b, "right", lambda s: cx - s["x"] < 195, timeout=8)
    b.key("right", True)
    b.key("space", True)
    b.wait_for(f"{cat}.gone", timeout=4)
    b.key("space", False)
    b.key("right", False)
    s1 = b.state()
    ok &= check(cf - s1["y"] > 4 and 140 <= cx - s1["x"] <= 156, "in a jump, she is taken as she crosses his line of sight, in the air", (cx - s1["x"], cf - s1["y"]))
    b.wait_for(f"{her} === 'her-creep-tiptoe' || {her} === 'her-start-back'", timeout=3)
    s2 = b.state()
    ok &= check(abs(s2["y"] - cf) < 1 and abs(s2["x"] - s1["x"]) < 6, "comes straight down, and the scene from there", (s2["x"] - s1["x"], s2["y"] - cf))
    b.wait_for(f"{S}.mode === 'play'", timeout=6)
    ok &= check(abs(b.state()["y"] - cf) < 1 and "bb3" in flags(b), "and ends with her on the floor")

    # Off the balcony's front onto the stage (every lock open): the scene where she lands.
    b.open("?reset&play&at=stage&cards=all")
    b.teleport(exact_x(243.0), D7)
    hold_until(b, ["right", "space"], lambda s: s["y"] == D6 or b.eval(f"{cat}.gone"), 5)
    b.wait_for(f"{cat}.gone", timeout=4)
    b.wait_for(f"{S}.mode === 'play'", timeout=8)
    s3 = b.state()
    ok &= check(abs(s3["y"] - cf) < 1 and "bb3" in flags(b) and b.eval(f"{q}.open.visible && !{q}.snag.visible"), "off the balcony onto the stage: the scene, and she on the floor after", s3)
    ok &= check(s3["x"] < x0 + 44, "she came straight down in front of the curtain, clear of the lamp", s3["x"] - x0)
    b.wait(6)
    ok &= check(b.state()["mode"] == "play" and abs(b.state()["x"] - s3["x"]) < 2, "where the lamp does not reach her", b.state())

    # A reload after it.
    b.open("?play&at=stage&did=bb3")
    ok &= check(b.eval(f"{cat}.away && !{cat}.sprite.visible && {q}.open.visible && !{q}.shut.visible && {q}.ropeEnd < {top} + 20 && {sm}.dir === -1 && {P}['amb_dancer_her_off'].on"),
                "after a reload: he is gone, the hatch open, the loop up, the dancers stopped")
    b.wait(1.5)
    ok &= check(b.eval(f"{lamp}.lamp.swinging"), "and the lamp swings")
    hold_until(b, "right", lambda s: s["x"] > cx - 150, timeout=8)
    ok &= check(b.eval(f"{S}.mode") == "play", "nothing starts when she walks up")
    return ok


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
    wait(0.5)
    ok &= check(js(b, f"{spill}.state") == "tell", "a slot machine's lights race: the tell", js(b, f"{spill}.state"))
    wait(1.4)
    ok &= check(js(b, f"{spill}.state") == "spilled", "then its chips are all over the floor")
    b.shot("region3-chips")
    b.teleport(x - 20, D7)
    wait(0.5)
    ok &= check(b.state()["mode"] == "play", "standing still on them is nothing", b.state())
    half = js(b, f"{spill}.def.half")
    b.teleport(x - half - 50, D7)
    hold_until(b, "right", lambda s: s["x"] >= x - half - 14, 3)
    b.hold(["right", "space"], 0.85)
    ok &= check(b.state()["mode"] == "play" and b.state()["x"] > x + half, "nor is a running jump over them", b.state())
    b.teleport(x + 20, D7)
    js(b, f"(m => {{ m.at = window.__ship.time.now + 4000; }})({spill})")
    b.hold("left", 0.5)
    ok &= check(b.state()["mode"] == "scripted" and "Whoa" in alert(b), "running on them: slipped", alert(b))
    wait(2.8)
    js(b, "window.__ship.world.movers.filter(m => m.pour).forEach(m => { m.state = 'idle'; m.chips.clear(); m.at = window.__ship.time.now + 600000; })")
    # The machine with a glint pays her.
    jx = js(b, "window.__ship.world.things.find(t => t.id === 'sec_jackpot').x")
    b.teleport(jx, D7)
    b.tap("e")
    ok &= check(wait_flag(b, "jackpot", 5), "E at the machine with a glint: jackpot", flags(b))
    wait(0.4)
    ok &= check(b.state()["tangerines"] >= 2, "it pays out two tangerines", b.state())
    b.shot("region3-jackpot")
    # The Art Gallery's cat: a double-take.
    b.teleport(exact_x(140.0), D7)
    wait(1.9)
    ok &= check(b.state()["mode"] == "scripted" and js(b, "window.__ship.player.anims.currentAnim.key") == "her-idle-look",
                "a painting of a black cat: she looks twice", b.state())
    b.shot("region3-painting")
    wait(1.9)
    # The lighting booth and the stage door want the Entertainment card.
    booth = room(b, "lighting")
    b.teleport(booth["doors"][0]["outX"], D7)
    b.tap("e")
    wait(0.4)
    ok &= check(route(b) == "inside" and "Entertainment" in alert(b), "the lighting booth wants the Entertainment card", alert(b))
    # Off the balcony's end, down onto the stage: no scare.
    st = js(b, "window.__ship.world.data.stage")
    # (Before the beat, from in front of the stage: 154 px from Bumbot she is taken, near-catch 3 as remade,
    # `region3.stage`; so the stage is looked at from the house, and its hatch cannot be stood on yet.)
    b.teleport(exact_x(242.5), D6)
    wait(0.4)
    ok &= check(person(b, "npc_stagemanager")["on"] and person(b, "amb_dancer_her")["on"] and not person(b, "amb_dancer_her_off")["on"],
                "the stage manager with his dancers, rehearsing")
    b.shot("region3-stage")
    stage = "window.__ship.world.story.stage"
    ok &= check(js(b, f"{stage}.shut.visible") and not js(b, f"{stage}.open.visible"), "the stage's hatch is shut before the beat")
    b.teleport(exact_x(243.0), D7)
    b.hold("right", 0.8)
    ok &= check(b.state()["y"] == D7, "the balcony's front holds her", b.state())
    hold_until(b, ["right", "space"], lambda s: s["y"] == D6, 4)
    wait(0.3)
    s = b.state()
    ok &= check(s["y"] == D6 and s["mode"] in ("play", "scripted"), "hopped, she drops onto the stage: no scare", s)
    # Near-catch 3 (where she landed, or as she walks on).
    hold_until(b, "right", lambda s: s["mode"] == "scripted" or "bb3" in flags(b), 4)
    wait(1.0)
    b.shot("region3-rival")
    ok &= check(wait_flag(b, "bb3", 16), "near-catch 3: the rival goes down the trap door, Bumbot up the fly rope", flags(b))
    ok &= check(js(b, f"{stage}.open.visible") and not js(b, f"{stage}.shut.visible"), "the trap door stays open")
    ok &= check(not person(b, "amb_dancer_her")["on"] and person(b, "amb_dancer_her_off")["on"], "the dancers stand where they rehearsed, stopped")
    light = "window.__ship.world.movers.find(m => m.lamp)"
    wait(1.2)
    ok &= check(js(b, f"{light}.lamp.swinging"), "and the stage light swings")
    wait(4.0)
    ok &= check(b.state()["mode"] == "play", "where the scene left her it does not reach her", b.state())
    b.shot("region3-after")
    # He wants his pills; she has none yet. (Aft of centre stage since 2026-11-24.)
    b.teleport(exact_x(248.5) + 26, D6)
    wait(0.4)
    ok &= check(js(b, "window.__ship.world.people.byId.npc_stagemanager.bubbleItems[0].visible"), "the stage manager shows a pill bottle")
    b.tap("e")
    wait(0.5)
    ok &= check("ent" not in save_list(b, "cards") and b.state()["mode"] == "play", "E without them: nothing yet")
    # The bow, between the open trap door and the swinging light.
    b.teleport(exact_x(247.3), D6)
    wait(3.5)
    ok &= check(b.state()["mode"] == "scripted" and js(b, "window.__ship.player.anims.currentAnim.key") == "her-bow",
                "three seconds still at centre stage: she bows to the house", b.state())
    b.shot("region3-bow")
    wait(2.2)
    # The light at the bottom of its swing.
    b.teleport(js(b, f"{light}.def.x"), D6)
    end = now() + 4
    hit = False
    while now() < end and not hit:
        hit = b.state()["mode"] == "scripted"
        wait(0.05)
    ok &= check(hit and "Ouch" in alert(b), "under the swinging light: bonked", alert(b))
    ok &= check(js(b, "window.__ship.worldLayer.list.some(o => /^gags-jog-(spin|shoved)/.test(o.anims?.currentAnim?.key || ''))"),
                "12a or 12b: the jogger's spin or belly-flop (the user, 2026-11-19: reuse)")
    # (Until she is back at her checkpoint, not for a time: the gag is longer than the fall it replaced.)
    b.wait_for("window.__ship.mode === 'play'", 8)
    wait(0.3)
    # The open trap door: one deck down onto the galley's flour sacks, beside the rival.
    b.teleport(st["trapX"], D6)
    wait(1.6)
    ok &= check(route(b) == "galley" and b.state()["mode"] == "play", "into the open trap door: the galley, no scare", (route(b), b.state()))
    ok &= check(person(b, "riv_galley")["on"], "where the security officer sits in the flour")
    b.shot("region3-galley")
    g = room(b, "galley")
    b.teleport(g["doors"][0]["x"], D5, "galley")
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "inside" and b.state()["y"] == D5, "out of the galley on deck 5", b.state())
    # The pills, down the theatre's trunk and back; his card.
    ok &= check(pills_for_the_stage_manager(b), "his pills from his cabin on deck 4: he hands over the Entertainment card", save_list(b, "cards"))
    wait(0.5)
    ok &= check(not js(b, "window.__ship.world.people.byId.npc_stagemanager.bubbleItems[0].visible"), "his bubble is gone")
    b.shot("region3-card")
    # With the card: the dressing room's book, the lighting booth's photo.
    dr = room(b, "dressing")
    b.teleport(dr["doors"][0]["outX"], D6)
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "dressing", "the stage door opens", route(b))
    b.teleport(dr["x0"] + 118, D6, "dressing")
    b.shot("region3-dressing")
    b.tap("e")
    wait(0.4)
    ok &= check(js(b, "window.__ship.save.books['3']") == "held", "the third book, on the make-up table")
    b.teleport(dr["doors"][0]["x"], D6, "dressing")
    b.tap("e")
    wait(0.9)
    b.teleport(booth["doors"][0]["outX"], D7)
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "lighting", "the lighting booth opens", route(b))
    b.teleport(booth["x0"] + 446, D7, "lighting")
    b.shot("region3-catwalk")
    b.tap("e")
    wait(0.9)
    ok &= check(b.state()["mode"] == "scripted", "the photo at the catwalk's end", b.state())
    b.tap("e")
    wait(0.6)
    ok &= check("slot_lighting" in save_list(b, "seen"), "seen")
    b.teleport(booth["doors"][0]["x"], D7, "lighting")
    b.tap("e")
    wait(0.9)
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
        wait(0.15)
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
        wait(0.4)
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
    wait(0.34)
    b.key("space", False)
    wait(0.02)
    b.hold(["left", "space"], 0.2)
    b.hold("left", 1.0)
    s = b.state()
    ok &= check(s["y"] == D11, "no wall jump up the sun cover's post without the socks", s)
    # (Jump is pressed once she is in the air: pressed on the floor first, she would jump, and
    # could come down on the sun cover's top.)
    b.eval(f"window.__ship.spawnAt({{x: {x_of(238)}, y: {D11 - 110}, route: 'inside'}})")       # in the air over the Great Outdoors
    wait(0.15)
    b.key("space", True)
    wait(0.75)
    s = b.state()
    b.key("space", False)
    ok &= check(s["y"] == D11, "no glide without the parasol: she just falls", s)
    linen = b.eval("window.__ship.rooms.find(r => r.route === 'linen').door")
    b.teleport(linen, D9, "linen")
    b.hold(["down", "left"], 2.4)
    wait(0.6)
    ok &= check(route(b) == "linen" and not b.eval("window.__ship.crawling"), "no crawling into the shaft before the beat", route(b))
    # The stage's trap door is shut before the rehearsal's beat.
    trap = b.eval("window.__ship.world.data.trapdoor")
    b.teleport(trap["x"] - 30, trap["y"])
    b.eval("window.__ship.cats.forEach(c => { c.gone = true; })")      # (he would stop her on the way)
    b.hold("right", 0.5)
    wait(0.6)
    ok &= check(route(b) == "inside", "the trap door holds before the beat", route(b))
    # The elevators light only region 1's landings at the start.
    lit = b.eval("window.__ship.lifts.map(l => l.floors.filter(f => window.__ship.progress.regionOpen(f.region)).map(f => f.deck))")
    ok &= check(all(sorted(x) in ([4, 5], [5]) for x in lit), "the elevators light only decks 4-5 at the start", lit)
    return ok


def mover(mid):
    return f"window.__ship.world.movers.find(m => m.def && m.def.id === '{mid}')"


def wait_js(b, text, timeout=8):
    """Waits until an expression is true in the game."""
    end = now() + timeout
    while now() < end:
        if b.eval(text):
            return True
        wait(0.04)
    return False


def scared(b, word, within=3.0):
    """A fright with `word` in it comes within a while."""
    end = now() + within
    while now() < end:
        if b.state()["mode"] == "scripted" and word in alert(b):
            return True
        wait(0.04)
    return False


def restack(b, stk):
    """The towel stack stood up again by hand (once fallen it stays fallen, 2026-11-18)."""
    js(b, f"(t => {{ const sv = window.__ship.save; sv.broken = sv.broken.filter(i => i !== t.def.id); t.state = 'up';"
          f" t.pic.anims.stop(); t.stack.setVisible(true).setAngle(0); t.stool.setVisible(true); t.pic.setVisible(false); }})({stk})")


def scenario_region4__pillows(b):
    """Near-catch 4 in the linen room, as remade on the user's own structure (docs/near-catch-4-remake-log.md): a stack
    of pillows in the emptied cart, too tall to hop and no way past it; pushed, the cart bumps Bumbot's shelf and he is
    off; the cover falls as his paws reach it, before he is in; he goes in at the opening's height; the top pillows fly
    aft, the lower two ride the cart on and slide off; where they lie (clear of the door, low under the chute's hatch);
    the cover lower on the floor; the hint for crawling, once; the cart hers to stand on after; a load with the beat done."""
    S = "window.__ship"
    q = f"{S}.world.story.linen"
    cat = f"{S}.cats.find(c => c.flag === 'bb4')"
    lc = f"{S}.world.pushables.find(t => t.id === 'cart_linen')"
    sh = f"{S}.world.shaft"
    shown = lambda o: b.eval(f"{o}.visible && {o}.alpha > 0.5")
    b.open("?reset&play&at=linen")
    L = b.eval(f"{q}.L")
    floor, duct = b.eval(f"{q}.floor"), b.eval(f"{S}.world.data.duct")
    ok = check(b.eval(f"{lc}.items[0].frame.name") == "laundry-cart-empty", "the cart is the empty one", b.eval(f"{lc}.items[0].frame.name"))
    ok &= check(shown(f"{q}.ride") and b.eval(f"{q}.ride.frame.name") == 0 and b.eval(f"{q}.ride.x === {lc}.x"), "a stack of pillows in it")
    top = L["top"]
    ok &= check(top > 68 and L["ride"]["y"] + L["ride"]["cell"][1] > -32, "its top over her jump's height, its foot in the tub under the rim", (top, L["ride"]))
    ok &= check(b.eval(f"{lc}.zone.body.height") == 128, "the cart with it is a wall to the ceiling", b.eval(f"{lc}.zone.body.height"))
    ok &= check(not shown(f"{q}.near") and not shown(f"{q}.far") and b.eval(f"{sh}.cover.visible"), "no pillows on the floor yet; the cover on the mouth")
    # (We cannot jump past it, or on top of it: three jumps at it, her highest and her furthest forward.)
    cx = b.eval(f"{lc}.x")
    b.key("left", True)
    wait(0.4)
    high, fwd = floor, 1e9
    for _ in range(3):
        b.key("space", True)
        end = now() + 0.75
        while now() < end:
            wait(0.03)
            st = b.state()
            high, fwd = min(high, st["y"]), min(fwd, st["x"])
        b.key("space", False)
        wait(0.1)
    st = b.state()
    ok &= check(st["y"] == floor and fwd > cx + 20 and b.eval(f"{lc}.x") == cx, "jumping at it: neither onto it nor past it, and it does not move", (st, fwd, high))
    ok &= check(not b.eval(f"{cat}.gone"), "he sleeps on", b.eval(f"{cat}.sprite.anims.currentAnim.key"))
    # Pushed: the cart's front past his body's aft end, a bump, and he goes.
    b.tap("e")
    ok &= check(b.state()["mode"] == "push", "E at its end: she takes hold", b.state())
    aft = b.eval(f"{cat}.sprite.x - 32 + 49")
    ok &= check(wait_js(b, f"{cat}.gone", 6), "pushed up to his shelf: he is off")
    t0 = b.eval(f"{q}.T")
    front = b.eval(f"{lc}.x - 22.5")
    ok &= check(aft - 7 <= front <= aft - 5, "as the cart bumps his shelf: its front 6 px past his nose", front - aft)
    b.key("left", False)              # (she lets go as he goes: the push still goes on until the last pillows are off)
    seen = dict(cover=None, lip=None, inside=None, ride=[], flew=None, mode=set(), walled=None)
    end = now() + 3
    while now() < end and not (b.eval(f"!!{q}.over")):
        T = b.eval(f"{S}.time.now - {q}.T")
        v = b.eval(f"[{sh}.cover.visible, {cat}.sprite.x, {cat}.sprite.y, {cat}.sprite.anims.currentAnim.key, {q}.ride.visible && {q}.ride.alpha > 0, {q}.ride.x, {lc}.x, {q}.frame, {S}.mode, {lc}.zone.body.height, {cat}.away]")
        if not v[0] and seen["cover"] is None:
            seen["cover"] = (T, v[1], v[3])
        if v[3] == "bumbot-crawl" and seen["inside"] is None:
            seen["inside"] = (T, v[0], v[2])
        if v[4]:
            seen["ride"].append(abs(v[5] - v[6]))
        if v[7] >= 1 and seen["flew"] is None:
            seen["flew"] = T
        if T < 650:
            seen["mode"].add(v[8])
        if v[9] < 128 and seen["walled"] is None:
            seen["walled"] = (T, v[7])
        wait(1 / 60)
    ok &= check(seen["cover"] and seen["cover"][2] == "bumbot-leap" and seen["cover"][0] < 220 and seen["cover"][1] > duct["mouthX"] + 14,
                "the cover begins its fall while he is still in the air, as his paws reach it", seen["cover"])
    ok &= check(seen["inside"] and not seen["inside"][1] and seen["inside"][0] >= 300, "he goes into the mouth with its cover already off", seen["inside"])
    ok &= check(seen["inside"] and seen["inside"][2] == duct["upper"] - 5, "in at the opening's height, 5 px over the shaft's floor for her", (seen["inside"], duct["upper"]))
    ok &= check(seen["flew"] is not None and seen["flew"] < 120, "the top pillows are knocked off as he springs", seen["flew"])
    ok &= check(seen["ride"] and max(seen["ride"]) == 0, "the pillows still in the cart move with it exactly", max(seen["ride"] or [9]))
    ok &= check(seen["mode"] == {"push"}, "the push goes on by itself until the last pillows are off, her keys let go", seen["mode"])
    ok &= check(seen["walled"] and seen["walled"][1] >= L["release"], "the cart a wall until the last two leave it", seen["walled"])
    ok &= check("crawl" in save_list(b, "verbs") and "bb4" in flags(b), "he is gone: crawling is hers")
    ok &= check(alert(b) == "", "no words over her as he goes", alert(b))
    b.shot("region4-pillows")
    wait(0.6)
    at = b.eval(f"{lc}.x")
    wait(0.3)
    ok &= check(b.state()["mode"] == "push" and b.eval(f"{lc}.x") == at, "and the cart is hers again: it stands where the push ended, her hands on it", (b.state(), at))
    # Where they lie: two low behind where the cart stood, two at the aft rack; the door and the hatch's handle clear.
    box = lambda o: b.eval(f"(o => [o.x, o.y, o.x + o.width, o.y + o.height])({o})")
    near, far = box(f"{q}.near"), box(f"{q}.far")
    ok &= check(shown(f"{q}.near") and shown(f"{q}.far") and not shown(f"{q}.free") and not shown(f"{q}.ride"), "the four lie on the floor, the clip's own pictures put away")
    door = b.eval(f"{S}.rooms.find(r => r.route === 'linen').door")
    ok &= check(near[2] <= door - 21 and far[0] >= door + 16, "the room's door clear of them: its frame runs 21 px forward of its middle, 16 aft", (near, far, door))
    hatch = b.eval(f"{S}.world.data.linen.chuteX")
    ok &= check(near[0] < hatch < near[2] and floor - near[1] <= 18, "the two under the chute's hatch lie low: its handle, 19 px up, is over them", (near, floor - near[1]))
    ok &= check(far[2] <= b.eval(f"{S}.world.rooms.linen.def?.x1 ?? {far[2]}") and far[3] == floor and near[3] == floor, "on the floor, inside the room", (near, far))
    ok &= check(b.eval(f"{q}.near.depth < {lc}.items[0].depth && {q}.near.depth < {S}.player.depth"), "behind the cart and her")
    down = box(f"{sh}.down")
    ok &= check(wait_js(b, f"{sh}.down.visible && {sh}.down.alpha === 1", 2) and down[3] == floor + 4,
                "the cover flat on the floor, 4 px lower than the wall's foot", (down, floor))
    ok &= check(b.eval(f"{sh}.down.depth < {lc}.items[0].depth"), "and still behind the cart")
    # The mouth's near side has no hole for whoever is behind it to show through.
    holes = b.eval(f"""(t => {{ const im = t.getSourceImage(), c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
        const g = c.getContext('2d'); g.drawImage(im, 0, 0); const d = g.getImageData(0, 0, im.width, im.height).data, a = (x, y) => d[(y * im.width + x) * 4 + 3];
        let n = 0; for (let y = 0; y < im.height; y++) for (let x = 0; x < 12; x++) {{ if (a(x, y)) continue;
            let l = 0, r = 0, u = 0, w = 0; for (let i = 0; i < x; i++) l |= a(i, y); for (let i = x + 1; i < 12; i++) r |= a(i, y);
            for (let j = 0; j < y; j++) u |= a(x, j); for (let j = y + 1; j < im.height; j++) w |= a(x, j); if (l && r && u && w) n++; }} return n; }})({S}.textures.get('shaft-mouth'))""")
    ok &= check(holes == 0, "the mouth's near side has no empty pixel inside its outline", holes)
    # The cart is hers again: pushed on to the mouth, and she can stand on it.
    b.key("left", True)
    ok &= check(wait_flag(b, "cart_linen", 8), "the cart, empty, pushed on to the shaft's mouth", flags(b))
    b.key("left", False)
    ok &= check(b.eval(f"{lc}.zone.body.height") == b.eval(f"{S}.world.data.linen.cartTop"), "it is its rim's height again", b.eval(f"{lc}.zone.body.height"))
    wait(0.3)
    b.hold(["left", "space"], 0.4)
    wait(0.5)
    st = b.state()
    ok &= check(st["y"] == duct["upper"], "she jumps onto it, level with the shaft's floor", st)
    # (The user, 2026-11-24: "The tooltip has to show (after the Bumbot's escape) only when we jump on top of the cart".)
    wait(0.2)
    words = alert(b)
    ok &= check("crawl" in words, "up on the cart: the hint over her, how to crawl", words)
    b.shot("region4-pillows-on-cart")
    # Ten seconds standing there: nothing touches her; down and up again, the hint is not said twice.
    wait(10)
    ok &= check(b.state()["mode"] == "play" and alert(b) == "", "ten seconds on: still hers, the words gone", (b.state(), alert(b)))
    b.hold("right", 0.5)
    wait(0.4)
    ok &= check(b.state()["y"] == floor, "down off it", b.state())
    b.hold(["left", "space"], 0.4)
    wait(0.6)
    ok &= check(b.state()["y"] == duct["upper"] and alert(b) == "", "and up on it again: no hint a second time", (b.state(), alert(b)))
    # A game loaded with the beat done: no stack, the pillows lying, the cover down, the cart its rim's height.
    b.open("?reset&play&at=linen&did=bb4")
    ok &= check(not shown(f"{q}.ride") and shown(f"{q}.near") and shown(f"{q}.far") and not shown(f"{q}.free"), "loaded after the beat: the pillows lie on the floor, none in the cart")
    ok &= check(b.eval(f"{lc}.zone.body.height") == b.eval(f"{S}.world.data.linen.cartTop") and b.eval(f"{sh}.down.visible && !{sh}.cover.visible"),
                "the cart its rim's height, the cover down")
    ok &= check(not b.eval(f"{cat}.sprite.visible"), "and no Bumbot on the shelf")
    ok &= check(alert(b) == "", "standing on the floor there: no hint", alert(b))
    near = box(f"{q}.near")
    ok &= check(b.eval(f"{lc}.x + 22.5") <= near[0] and b.eval(f"{lc}.zone.x === {lc}.x"), "the cart where the last pillows left it, forward of the two on the floor",
                (b.eval(f"{lc}.x"), near))
    b.shot("region4-pillows-after")
    return ok


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
    # The steward and his jammed cart, at the corridor's aft end (2026-11-18): the door at 194 m aft
    # of him is shut from the lobby, so that she cannot come up behind him.
    ok &= check(not use_door(b, 9, 194, 1), "the door aft of the steward is shut from the lobby")
    cart = f"{W}.pushables.find(t => t.id === 'cart_steward')"
    cx = js(b, f"{cart}.x")
    ok &= check(abs(cx - exact_x(185.2)) < 2, "his trolley at the corridor's aft end", cx)
    b.teleport(cx - 100, D9)
    wait(0.3)
    st = person(b, "npc_steward")
    ok &= check(st["on"] and abs(st["x"] - (cx + 17)) < 2 and not js(b, f"{cart}.items[0].visible"),
                "the steward at his tall trolley's handle: one picture of the two", st)
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
    wait(0.2)
    ok &= check("Housekeeping" in alert(b) and route(b) == "inside", "the linen room wants the Housekeeping card", alert(b))
    wait(0.5)
    b.teleport(cx - 26, D9)
    b.hold("right", 0.3)
    b.tap("e")
    gap = []
    b.key("right", True)
    wait(1.0)
    for _ in range(3):
        gap.append(js(b, f"{cart}.x - window.__ship.player.x"))
        wait(0.3)
    ok &= check(all(abs(g - 29) < 0.01 for g in gap), "she pushes it at her gap, 29 px from its middle", gap)
    ok &= check(wait_js(b, "window.__ship.save.flags.includes('cart_free')", 6), "pushed along to 189 m, the cart is free", b.state())
    b.key("right", False)
    wait(0.6)
    b.shot("region4-thanks")
    ok &= check(wait_js(b, "window.__ship.save.cards.includes('hk')", 4),
                "he thanks her and tosses her the Housekeeping card, short", save_list(b, "cards"))
    ok &= check(wait_js(b, "window.__ship.world.people.byId.npc_steward.sprite.anims.currentAnim.key.endsWith('idle')", 3),
                "his thanks over")
    st = person(b, "npc_steward")
    ok &= check(st["x"] > exact_x(189) and abs(st["x"] - (js(b, f"{cart}.x") + 35)) < 2 and js(b, f"{cart}.items[0].visible"),
                "and stands by his trolley, stepped back off its handle", st)
    b.hold("right", 1.2)
    ok &= check(b.state()["x"] > exact_x(189.5) and b.state()["mode"] == "play", "she walks past it, back against the wall", b.state())
    ok &= check(js(b, f"{W}.people.byId.npc_steward.dir") == 1, "he has turned to her as she passed him")
    ok &= check(use_door(b, 9, 194, -1), "the door at 194 m opens from the corridor")
    # The honeymooners.
    b.teleport(exact_x(133.6), D9)
    wait(0.4)
    ok &= check(js(b, f"{W}.people.byId.npc_bride.bubbleItems[0].visible"), "the honeymooners hold out a camera")
    b.shot("region4-honeymooners")
    b.tap("e")
    wait(1.75)
    b.shot("region4-photo")
    ok &= check(js(b, "window.__ship.player.anims.currentAnim.key") == "her-camera", "E: she takes their picture", b.state())
    ok &= check(wait_flag(b, "photo", 16), "the flash, their kiss, and in they go", flags(b))
    ok &= check(js(b, "window.__ship.save.books['4']") == "held", "the fourth book is their thanks")
    ok &= check(not person(b, "npc_bride")["on"] and not person(b, "npc_groom")["on"], "they have gone in")
    # The vacuum in the open cabin's doorway.
    vac = mover("haz_vacuum_9")
    vx = js(b, f"{vac}.def.x")
    b.teleport(vx - 160, D9)
    wait(0.3)
    ok &= check(js(b, f"{vac}.state") == "in" and js(b, f"{vac}.armed"), "the vacuum waits in the cabin's doorway")
    b.key("right", True)
    hit = scared(b, "Weeeee", 2.5)
    b.key("right", False)
    b.shot("region4-vacuum")
    ok &= check(hit and js(b, "window.__ship.lastMishap?.id") == "5a" and not js(b, f"{vac}.sprite.visible"),
                "running at the doorway: it darts out at her, and she rides it off (5a)", (alert(b), js(b, "window.__ship.lastMishap?.id")))
    wait_js(b, "window.__ship.mode === 'play'", 8)
    ok &= check(abs(b.state()["x"] - exact_x(119.6)) < 30 and js(b, f"{vac}.state === 'in' && {vac}.sprite.visible"),
                "and she is back at the crew door by the trunk, the vacuum in its doorway", b.state())
    # A jump as it rattles clears it.
    b.teleport(vx - 160, D9)
    wait_js(b, f"{vac}.state === 'in' && {vac}.armed", 6)
    b.key("right", True)
    wait_js(b, f"{vac}.state === 'wait'", 3)
    b.key("space", True)
    wait(0.75)
    b.key("space", False)
    b.key("right", False)
    wait(0.3)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["x"] > vx - 30, "a jump as it rattles clears it", s)
    stk = mover("haz_towels_9")
    sx = js(b, f"{stk}.def.x")
    # (Running on toward the towel stack after it, the stack falls in front of her: its own checks below.)
    # Back in, it does nothing while she stands at the door; the cabin being cleaned.
    wait(1.6)
    cl = room(b, "cleanup")
    b.teleport(cl["doors"][0]["outX"], D9)
    wait(0.5)
    ok &= check(b.state()["mode"] == "play", "back in its doorway it leaves her alone", b.state())
    b.tap("e")
    wait(0.9)
    # (Its stewardess works on deck 10 since 2026-11-20, `makeup10`; her bookmark lies on this bed.)
    ok &= check(route(b) == "cleanup" and js(b, f"{W}.things.some(t => t.id === 'keep_bookmark' && t.route === 'cleanup')"),
                "the cabin being cleaned: the bookmark on its stripped bed", route(b))
    b.shot("region4-cleanup")
    b.teleport(cl["doors"][0]["x"], D9, "cleanup")
    b.tap("e")
    wait(0.9)
    # The towel stack: coming at it, it wobbles and falls the way she goes, onto her as she passes
    # it; stopped short as it wobbles, it falls in front of her and she walks on over the heap.
    # (The vacuum is kept in its doorway for this: beside the stack she is within its reach.)
    wait_js(b, f"{vac}.state === 'in'", 6)
    js(b, f"{vac}.update = () => {{}}")
    b.teleport(sx - 700, D9)
    restack(b, stk)
    b.teleport(sx - 160, D9)
    wait(0.3)
    b.key("right", True)
    hit = scared(b, "Mmmph", 2.5)
    b.key("right", False)
    b.shot("region4-buried")
    ok &= check(hit, "running past the towel stack: it falls on her, buried", alert(b))
    wait_js(b, "window.__ship.mode === 'play'", 8)
    # (Fallen for good, its heap crossed on the way back from the steward: 2026-11-18.)
    b.teleport(sx - 700, D9)
    wait(0.6)
    ok &= check(js(b, f"{stk}.state") == "down" and "haz_towels_9" in save_list(b, "broken"),
                "it stays fallen once she has gone (kept with what she broke)", js(b, f"{stk}.state"))
    # (Stood up again by hand for the other way past it.)
    restack(b, stk)
    b.teleport(sx - 160, D9)
    wait(0.3)
    b.key("right", True)
    wobbled = wait_js(b, f"{stk}.state === 'wobble'", 3)
    b.key("right", False)
    fell = wait_js(b, f"{stk}.state === 'down'", 3)
    ok &= check(wobbled and fell and b.state()["mode"] == "play", "stopped as it wobbles, it falls in front of her", b.state())
    b.hold("right", 1.2)
    ok &= check(b.state()["mode"] == "play" and b.state()["x"] > sx + 40, "and she walks on over the heap", b.state())
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
    hit = scared(b, "Brrr", 2.5)
    b.shot("region4-drenched")
    ok &= check(hit, "under it when it rains: drenched", alert(b))
    wait(2.8)
    # The balcony cabin: the green card's door, a checkpoint, the basket, the balcony and who is up there.
    bc = room(b, "balcabin9")
    n = tangerines()
    b.teleport(bc["doors"][0]["outX"], D9)
    wait(0.2)
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "balcabin9" and "cp_balcabin" in save_list(b, "activated"), "the balcony cabin opens with the card: a checkpoint", route(b))
    b.teleport(bc["x0"] + 150, D9, "balcabin9")
    wait(0.4)
    b.shot("region4-balcabin")
    b.hold("space", 0.3)
    wait(0.6)
    ok &= check(tangerines() == n + 1, "a tangerine in its fruit basket", tangerines())
    b.teleport(bc["doors"][1]["x"], D9, "balcabin9")
    b.tap("e")
    wait(1.5)
    b.shot("region4-balcony")
    ok &= check(route(b) == "promenade" and "glimpse_balcony" in flags(b), "out on its balcony: Bumbot on the rail a deck up", (route(b), flags(b)))
    b.tap("e")
    wait(1.0)
    ok &= check(route(b) == "balcabin9", "and back in", route(b))
    b.teleport(bc["doors"][0]["x"], D9, "balcabin9")
    b.tap("e")
    wait(0.9)
    # The door that flies open (2026-11-18): coming at it from aft, past its hinge, it bursts open and
    # slams her flat on the wall (13a, its own clip); from forward it never hits her.
    sw = mover("haz_swing_9")
    wx = js(b, f"{sw}.def.x")
    b.teleport(wx + 200, D9)
    wait(0.2)
    b.key("left", True)
    hit = scared(b, "Ouch", 3.0)
    b.key("left", False)
    b.shot("region4-bonked")
    ok &= check(hit and js(b, f"{sw}.state") == "squash", "coming at the door that flies open from aft: slammed flat on the wall", (alert(b), js(b, f"{sw}.state")))
    ok &= check(person(b, "haz_swing_9_who")["on"], "the kid with the water pistol looks out")
    wait_js(b, "window.__ship.mode === 'play'", 8)
    wait(0.6)
    ok &= check(abs(b.state()["x"] - bc["doors"][0]["outX"]) < 30, "back at the balcony cabin's door", b.state())
    wait_js(b, f"{sw}.state === 'shut' && {sw}.armed", 6)
    b.teleport(wx + 200, D9)
    b.key("left", True)
    wait_js(b, f"{sw}.state === 'wait'", 3)
    b.key("left", False)
    ok &= check(wait_js(b, f"{sw}.state === 'burst'", 3), "stopping short of it, it bursts open by itself")
    wait(0.3)
    b.hold("left", 1.6)
    ok &= check(b.state()["mode"] == "play" and b.state()["x"] < wx - 40, "then on past it, untouched", b.state())
    b.teleport(wx - 200, D9)
    wait(1.5)
    wait_js(b, f"{sw}.state === 'shut' && {sw}.armed", 6)
    b.hold("right", 2.4)
    ok &= check(b.state()["mode"] == "play" and b.state()["x"] > wx + 40, "from forward: past it, never hit", b.state())
    # "Do Not Disturb".
    dx = js(b, f"{mover('haz_dnd_9')}.def.x")
    b.teleport(dx - 8, D9)
    wait(0.3)
    ok &= check(b.state()["mode"] == "play", "the Do Not Disturb door: left alone, nothing")
    b.tap("e")
    wait(0.35)
    b.shot("region4-startled")
    ok &= check(b.state()["mode"] == "scripted" and "sorry" in alert(b), "E at it: startled", alert(b))
    # (23, 2026-11-19: her hands over her eyes, then off on tiptoe forward, away from the door, to the swinging door
    # there, and her checkpoint.)
    tip = "window.__ship.worldLayer.list.find(o => o.anims?.currentAnim?.key === 'gags-dnd-tiptoe')"
    ok &= check(wait_js(b, f"!!{tip}", 2), "she covers her eyes, then tiptoes off")
    x0 = js(b, f"{tip}.x")
    wait(0.5)
    ok &= check(js(b, f"{tip}?.x ?? 0") < x0 - 35 and js(b, f"{tip}.flipX"), "away from the door, at her quick tiptoe", (x0, js(b, f"{tip}?.x")))
    ok &= check(wait_js(b, "window.__ship.mode === 'play'", 8), "and back at her checkpoint", b.state())
    # The standing cart and its tangerine; the luggage to the ceiling.
    # (Until she is over it, not for a time: the cart's top is 21 px wide, and 0.4 s carried her a
    # hair past it whenever the machine was quick.)
    b.teleport(exact_x(172.6) - 44, D9)
    hold_until(b, ["right", "space"], lambda s: s["x"] >= exact_x(172.6) - 6, 2)
    wait(0.5)
    b.hold("left", 0.08)
    wait(0.2)
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
    wait(0.9)
    ok &= check(route(b) == "adjoin", "into the first of the adjoining cabins", route(b))
    b.hold("right", 2.2)
    ok &= check(b.state()["x"] < ad["x0"] + 236, "the blanket fort across the way through stops her", b.state()["x"] - ad["x0"])
    b.shot("region4-fort")
    b.teleport(ad["doors"][0]["x"], D9, "adjoin")
    b.tap("e")
    wait(0.9)
    # The dash goes through the luggage.
    b.teleport(exact_x(178.6), D9)
    wait(0.2)
    b.key("right", True)
    b.tap("d")
    wait(1.0)
    b.key("right", False)
    ok &= check("haz_luggage_9" in save_list(b, "broken") and b.state()["x"] > exact_x(180), "the dash goes through the luggage", b.state())
    ok &= check("tan_9_luggage" in save_list(b, "collected"), "and she has the tangerine behind it", save_list(b, "collected"))
    b.teleport(exact_x(191.0), D9)
    b.hold("right", 0.5)
    ok &= check("cp_9_mid" in save_list(b, "activated"), "the crew door before the aft lobby: a checkpoint")
    # The linen room: near-catch 4, into the vent.
    b.teleport(linen, D9)
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "linen", "with the card, into the linen room", route(b))
    b.shot("region4-linen")
    lc = f"{W}.pushables.find(t => t.id === 'cart_linen')"
    # (The laundry cart is in her way, solid, hers to push from the start; Bumbot asleep on the bottle shelf is off into
    # the shaft, knocking the cover off its mouth, as the cart all but touches him: the user, 2026-11-23. The room is
    # mirrored since that day: its door aft, the cart pushed forward, the mouth on its forward wall.)
    duct = js(b, f"{W}.data.duct")
    ok &= check(js(b, f"{W}.data.linen.chuteX") == js(b, f"{W}.data.linen.laundryCartX"),
                "the chute's hatch stands straight over the laundry's cart on deck 4", js(b, f"{W}.data.linen"))
    b.hold("left", 0.9)
    ok &= check(b.state()["x"] > js(b, f"{lc}.x"), "the laundry cart stops her", b.state())
    b.tap("e")
    ok &= check(b.state()["mode"] == "push", "E by the cart's end: she takes hold", b.state())
    ok &= check(js(b, f"{W}.things.find(t => t.id === 'vent_cover').items[0].visible"), "the cover on the shaft's mouth")
    b.key("left", True)
    ok &= check(wait_flag(b, "bb4", 12), "the cart all but touching him: near-catch 4, Bumbot leaps into the shaft's mouth", flags(b))
    wait(0.5)
    ok &= check(js(b, f"{W}.things.find(t => t.id === 'vent_cover_down').items[0].visible")
                and not js(b, f"{W}.things.find(t => t.id === 'vent_cover').items[0].visible"), "its cover knocked off, flat on the floor in front of the mouth")
    ok &= check("crawl" in save_list(b, "verbs"), "crawling is learned")
    b.shot("region4-vent")
    # The cart on to the mouth, onto its rim, down on hands and knees, and in: no cut, the room still in view.
    ok &= check(wait_flag(b, "cart_linen", 8), "pushed to the shaft's mouth", flags(b))
    b.key("left", False)
    ok &= check(js(b, f"{lc}.x - {lc}.width / 2 - 2") <= duct["mouthX"] + 1, "its end against the mouth's", js(b, f"{lc}.x"))
    wait(0.3)
    b.shot("region4-cart")
    b.hold(["left", "space"], 0.4)
    wait(0.5)
    s = b.state()
    ok &= check(s["y"] == D9 - js(b, f"{W}.data.linen.cartTop") == duct["upper"], "she jumps up onto its rim, level with the shaft's floor", s)
    b.shot("region4-on-cart")
    # (Standing, the mouth's end is a wall: she does not run off the cart's end into the gap under it.)
    b.hold("left", 0.8)
    s = b.state()
    ok &= check(route(b) == "linen" and s["y"] == duct["upper"] and s["x"] >= duct["mouthX"] + 6,
                "running forward on the cart, standing: the mouth stops her, still on the rim", s)
    b.key("down", True)
    wait(0.25)
    ok &= check(js(b, f"window.__ship.crawling && {W}.shaft.mouth.depth > window.__ship.player.depth && {W}.shaft.mouth.alpha === 1"),
                "on hands and knees at the mouth: its near side is drawn over her")
    b.shot("region4-at-mouth")
    b.key("down", False)
    ok &= check(into_the_shaft(b, jump=False), "down on hands and knees on it and forward: into the shaft", route(b))
    ok &= check(js(b, "window.__ship.player.flipX") and js(b, "!window.__ship.cameras.main.fadeEffect.isRunning"),
                "facing forward as she went in, and no fade")
    ok &= check(js(b, "window.__ship.rooms.find(r => r.route === 'linen').room.visible"), "the linen room still in view behind her")
    b.shot("region4-mouth")
    # The slope behind the wall: her slide, to her hands and knees at its foot, in the slab between the decks.
    b.key("left", True)
    ok &= check(wait_js(b, f"window.__ship.mode === 'scripted' && {W}.shaft.slide.visible", 3), "over the slope's lip: her slide", b.state())
    b.shot("region4-slide")
    ok &= check(wait_js(b, "window.__ship.mode === 'play'", 3) and b.state()["y"] == duct["lower"] and b.state()["x"] < duct["slopeFoot"],
                "down it, on her hands and knees at its foot", b.state())
    ok &= check(js(b, "window.__ship.player.visible && window.__ship.player.anims.currentAnim.key") == "her-crawl", "crawling has its own clip")
    ok &= check(js(b, "window.__ship.shellAlpha[8]") == 0 and js(b, "window.__ship.viewDeck") == 9, "deck 8 open under the shaft")
    wait(0.4)
    b.shot("region4-duct")
    # The grilles: each over what is really below it; a tangerine on the way.
    n = tangerines()
    lit = lambda what: js(b, f"{W}.cones.find(c => c.what === '{what}').lit")
    ok &= check(lit("party") == 0 and lit("atrium") == 0, "no grille open but the one she is over: the rest are lit slats in the floor", (lit("atrium"), lit("party")))
    xs = [duct["exitX"]] + sorted(g["x"] for g in duct["grilles"])
    ok &= check(min(b_ - a_ for a_, b_ in zip(xs, xs[1:])) >= 180, "the grilles one to a place, well apart", xs)
    for what, below in (("hall", "the midship lift hall"), ("atrium", "the atrium"), ("party", "the party's door")):
        g = next(g for g in duct["grilles"] if g["what"] == what)
        s = hold_until(b, "left", lambda s: s["x"] < g["x"] + 4, 16)
        wait(0.6)
        ok &= check(lit(what) > 0.9, f"over the grille at {round((g['x'] - 480) / 48)} m: {below} shows", lit(what))
        b.shot(f"region4-over-{what}")
        b.key("left", True)
    b.key("left", False)
    ok &= check(tangerines() == n + 1, "a tangerine lost in the shaft", tangerines())
    party = js(b, f"{W}.things.find(t => t.id === 'amb_party').x")
    ok &= check(abs(next(g["x"] for g in duct["grilles"] if g["what"] == "party") - party) < 60, "that grille is over the door with the balloons", party)
    # The last grille gives way under her: she drops out where the shaft ends, no cut.
    s = through_the_shaft(b)
    ok &= check(route(b) == "inside" and s["y"] == D8 and abs(s["x"] - duct["exitX"]) < 40 and 5 in save_list(b, "regions"),
                "the last grille gives way: she drops into deck 8 forward where the shaft ends: region 5", s)
    wait(0.6)
    ok &= check("duct" in flags(b) and js(b, f"(t => t.items[0].visible && t.items[0].alpha === 1)({W}.things.find(t => t.id === 'shaft_exit_hang'))"),
                "the grille hanging open after her, by its right edge")
    ok &= check(js(b, f"{W}.ductEyes === undefined"), "nothing of Bumbot in the shaft: he is long gone")
    b.shot("region4-dropped")
    # Now that she crawls: the fort, and what is in it.
    n = tangerines()
    b.teleport(ad["x0"] + 200, D9, "adjoin")
    wait(0.3)
    s = hold_until(b, ["down", "right"], lambda s: s["x"] > ad["x0"] + 330, 5)
    ok &= check(s["x"] > ad["x0"] + 330 and tangerines() == n + 2, "crawling through the blanket fort: two tangerines hidden in it", (s["x"] - ad["x0"], tangerines() - n))
    b.teleport(ad["doors"][1]["x"], D9, "adjoin")
    wait(0.3)
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "inside" and abs(b.state()["x"] - exact_x(183.6)) < 12, "and out of the second cabin's door, past the luggage", b.state())
    # The chute.
    b.teleport(js(b, f"{W}.data.linen.chuteX"), D9, "linen")
    wait(0.4)
    b.tap("e")
    ok &= check(wait_js(b, "window.__ship.route === 'chute'", 4), "E at the chute's hatch: she goes in, and the view drops down the hull")
    b.shot("region4-chute")
    ok &= check(wait_js(b, "window.__ship.route === 'laundry'", 4), "the laundry fades in round the outlet")
    ok &= check(wait_flag(b, "chute", 8) and route(b) == "laundry", "out of it into the cart of towels and out over its side: on deck 4", route(b))
    ok &= check(js(b, f"!!{W}.story.hat"), "a towel on her head")
    wait(0.5)
    ok &= check(js(b, f"!!{W}.story.hat"), "and it stays there while she stands")
    ok &= check(person(b, "riv_laundry")["on"], "the security officer in a towel, his uniform in the wash")
    b.shot("region4-laundry")
    ok &= check(js(b, "window.__ship.viewOverride") is None, "the view no longer held on deck 4 once she is out (the corridor's decks dimmed)")
    ok &= check(js(b, "(() => { const s = window.__ship, d = s.rooms.find(r => r.route === 'laundry').dim; return d.depth > s.DEPTH.player; })()"),
                "the room's dim over the balconies' railings round it, as over all she is under")
    b.hold("left", 0.2)
    ok &= check(not js(b, f"!!{W}.story.hat"), "the towel slides off her head the moment she moves")
    ok &= check(js(b, f"!!{W}.story.towelDown"), "and lies on the laundry's floor")
    door = js(b, f"{W}.rooms.laundry.door")
    b.teleport(door, D4, "laundry")
    wait(0.2)
    b.tap("e")
    ok &= check(wait_js(b, "window.__ship.route === 'inside'", 2) and not js(b, f"!!{W}.story.towelDown"),
                "out in the corridor at once: the towel on the laundry's floor is not there", route(b))
    ok &= check(wait_js(b, "window.__ship.deckDim.shown > 0.9", 2), "the decks round the corridor dimmed", js(b, "window.__ship.deckDim.shown"))
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
    wait(0.2)


def enter_region6(b):
    """A save at region 6's door: regions 1-5 done, she has come up the forward stairs to deck 11."""
    enter_region5(b)
    b.eval("(P => { P.open('regions', 6); })(window.__ship.progress)")
    b.eval("window.__ship.world.refresh(); window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    b.teleport(exact_x(79.5), D11)
    wait(0.3)


def enter_region7(b):
    """A save at region 7's door: region 6 done (the socks, the pool drained, the kid fed, the table
    with her husband), she stands on the balcony of deck 9's balcony cabin."""
    enter_region6(b)
    b.eval("(P => { P.learn('socks'); ['bb5', 'kid_fed', 'refilled', 'table', 'glimpse_balcony'].forEach(f => P.setFlag(f)); })(window.__ship.progress)")
    b.eval("window.__ship.cats.filter(c => c.flag === 'bb5').forEach(c => { c.gone = true; c.away = true; c.sprite.setVisible(false); })")
    wait(0.3)
    b.eval("window.__ship.world.refresh(); window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    bc = room(b, "balcabin9")
    b.teleport(bc["doors"][1]["outX"], D9, "promenade")
    wait(0.4)
    b.eval("window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")


def enter_region8(b):
    """A save at region 8's door: region 7 done (the guest let in, the hallways open), she has climbed
    the sun cover onto deck 12's aft terrace."""
    enter_region7(b)
    b.eval("(P => { ['guest', 'riv_walkway'].forEach(f => P.setFlag(f)); P.open('regions', 7); P.open('regions', 8); })(window.__ship.progress)")
    wait(1.2)
    b.eval("window.__ship.world.refresh(); window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    b.teleport(exact_x(216.6), floor_y(12))
    wait(0.4)
    b.eval("window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")


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
    wait(0.5)
    ok &= check(js(b, f"{thing('shaft_exit_hang')}.items[0].visible") and js(b, f"{thing('shaft_exit_hole')}.items[0].visible"),
                "the grille she dropped out of hangs open by the slot it left in the ceiling")
    b.shot("region5-grille")
    # The party.
    px = js(b, f"{thing('amb_party')}.x")
    b.teleport(px - 60, D8)
    wait(1.2)
    ok &= check(person(b, "amb_birthday")["on"], "the birthday girl dances at the door with the balloons")
    ok &= check(js(b, f"{W}.story.noteAt > 0"), "its music comes out into the corridor")
    b.shot("region5-party")
    # The lobby's door opens from the corridor.
    ok &= check(use_door(b, 8, 74, -1), "the lobby's door opens from the corridor")
    # The cabin with the sea in its window: E, in, and a bounce on its bed, seen
    # through the door (2026-11-18).
    sx = js(b, f"{thing('amb_peek_sea')}.x")
    b.teleport(sx + 16, D8)
    wait(2.5)
    ok &= check(b.state()["mode"] == "play", "standing at the open cabin does nothing by itself", b.state())
    b.tap("e")
    wait(1.3)
    b.shot("region5-sea")
    ok &= check(b.state()["mode"] == "scripted" and b.eval("window.__ship.player.isCropped") and b.state()["y"] < D8 - 15,
                "E: she is in, bouncing on its bed, seen only through the door", b.state())
    ok &= check(wait_js(b, "window.__ship.mode === 'play'", 6) and b.state()["y"] == D8 and not b.eval("window.__ship.player.isCropped"),
                "and back out in the corridor", b.state())
    ok &= check("sec_peek_sea" in save_list(b, "seen"), "a find of hers", save_list(b, "seen"))
    # Her own cabin: a checkpoint at its door; the basket; the fifth book on the bed, read there.
    cabin = b.eval("window.__ship.rooms.find(r => r.route === 'cabin').door")
    b.teleport(cabin - 30, D8)
    b.hold("right", 0.4)
    ok &= check("cp_8206" in save_list(b, "activated"), "her cabin's door: a checkpoint", save_list(b, "activated"))
    b.teleport(cabin, D8)
    b.tap("e")
    wait(1.0)
    ok &= check(route(b) == "cabin", "into cabin 8206", route(b))
    x0 = cabin - 59
    # (On the desk's top since 2026-11-22, §4 2.4: at 118 px, where the basket's 104 is out of her reach.)
    b.teleport(x0 + 118, D8, "cabin")
    wait(0.4)
    ok &= check(b.state()["tangerines"] == 2, "two tangerines on the desk", b.state())
    b.teleport(x0 + 186, D8, "cabin")
    wait(0.3)
    b.shot("region5-bed")
    b.tap("e")
    wait(0.4)
    ok &= check(js(b, "window.__ship.save.books['5']") == "held", "the fifth book, on her bed")
    # (Her bed is a place to read, as the Library's armchairs, the user, 2026-11-21: E on it, standing or bouncing.)
    L = "window.__ship.world.library"
    b.teleport(x0 + 186, D8 - 32, "cabin")
    wait(2.2)
    ok &= check(b.state()["mode"] == "scripted" and not js(b, f"!!{L}.reading"), "standing still on the bed, she bounces", b.state())
    b.tap("e")
    wait_js(b, f"!!{L}.choosing", 3)
    ok &= check(js(b, f"{L}.readingPic.frame.name") == "bed-3" and "5" in js(b, f"JSON.stringify({L}.choosing.books)"),
                "E: she sits up against the pillows, her books in a row", js(b, f"JSON.stringify({L}.choosing.books)"))
    b.shot("region5-reading")
    b.tap("e")
    wait_js(b, f"!{L}.choosing && window.__ship.uiLayer.list.some(o => o.texture && o.texture.key === 'page-5')", 3)
    wait(0.6)
    b.tap("e")
    wait_js(b, f"!!{L}.choosing", 3)
    b.tap("escape")
    wait_js(b, f"!{L}.reading && window.__ship.mode === 'play'", 3)
    ok &= check(5 in save_list(b, "read") and b.state()["mode"] == "play", "its page read, and she stands up on the bed", (save_list(b, "read"), b.state()))
    wait(5.4)                   # (no bounce for 4 s after she gets up, then the bed's own second of stillness)
    ok &= check(b.state()["mode"] == "scripted" and not js(b, f"!!{L}.reading"), "after that the bed is for bouncing again", b.state())
    # With the towel round her hair (after the shower): the bed's clip with it (the user, 2026-11-23: it went from her hair).
    b.eval("window.__ship.setTowel(true)")
    b.tap("e")
    wait_js(b, f"!!{L}.choosing", 3)
    ok &= check(js(b, f"{L}.readingPic.frame.name") == "bed-towel-3", "with the towel on: she sits with it on", js(b, f"{L}.readingPic.frame.name"))
    b.tap("escape")
    wait_js(b, f"!{L}.reading && window.__ship.mode === 'play'", 3)
    ok &= check(js(b, "window.__ship.player.texture.key") == "her-towel", "and stands up in it", js(b, "window.__ship.player.texture.key"))
    b.eval("window.__ship.setTowel(false)")
    b.tap("left")
    wait(0.4)
    b.teleport(cabin, D8, "cabin")
    b.tap("e")
    wait(1.0)
    ok &= check(route(b) == "inside", "and out again", route(b))
    # The swan's cart.
    ok &= check(js(b, f"{thing('prop_swan_cart_swan')}.items[0].visible"), "a steward's cart with a towel swan on it")
    b.teleport(exact_x(31.5), D8)
    wait(0.4)
    b.shot("region5-swan")
    # The forward stairs on up: the officers' lobbies stay shut, deck 11 opens.
    (x0, y0), _ = flight_feet("stairs-forward-8-9")
    b.teleport(x0, y0)
    s = hold_until(b, "up", lambda s: s["y"] == D11 and s["mode"] == "play", 12)
    ok &= check(s["y"] == D11 and 6 in save_list(b, "regions"), "up the forward stairs, past decks 9 and 10, to deck 11: region 6", s)
    (x9, y9), _ = flight_feet("stairs-forward-9-10")
    b.teleport(x9, y9)
    wait(0.3)
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
    ok &= check(s["y"] == D11 and "WET PAINT" in blocked(b) and person(b, "blk_painter")["on"], "the midship flight up: wet paint, and the painter", blocked(b))
    ok &= check(js(b, f"{S}.progress.blockLifted('towels')") and not js(b, f"{thing('prop_towels_table')}.items[0].visible"),
                "the towel animals are gone from the midship flight below")
    b.shot("region6-painter")
    wait(0.6)
    b.teleport(exact_x(89.19) - 8, D11)
    wait(0.3)
    b.shot("region6-socks")
    b.tap("e")
    wait(0.3)
    ok &= check("socks" in save_list(b, "verbs"), "the grip socks, on the free treadmill's belt")
    wait(3.2)
    # The chess set.
    b.teleport(L["chessX"] - 20, D11)
    wait(0.3)
    px = js(b, f"{W}.story.pawn.x")
    b.tap("e")
    wait(1.6)
    ok &= check(js(b, f"{W}.story.pawn.x") != px and "sec_chess" in save_list(b, "seen"), "the giant chess set: she moves a pawn")
    b.shot("region6-chess")
    # Near-catch 5: she comes to him swimming; the kid in the hot tub; the pool drains with her in it.
    ok &= check(person(b, "npc_kid_tub")["on"] and not person(b, "npc_kid")["on"], "the kid is in the hot tub, his cap over its rim")
    # (The pool's scene remade, 2026-11-24, docs/pool-remake-log.md.)
    tubpic = f"{W}.mapPiece('hot-tub', {L['tubX']}, {D11})"
    v = js(b, f"[{who('npc_kid_tub')}.sprite.depth, {tubpic}.depth, {W}.story.tubFront.depth, {W}.story.tubFront.visible, {who('npc_kid_tub')}.sprite.y]")
    ok &= check(v[1] < v[0] < v[2] and v[3] and v[4] > D11 + 15, "he is in it: before its far rim and its water, behind its near wall, right down", v)
    hx = js(b, f"{W}.data.hatchPool.x")
    v = js(b, f"[{W}.pool.shut.obj.visible, {W}.pool.back.obj.visible, {W}.pool.drain.obj.visible, {W}.pool.shut.obj.depth, {S}.DEPTH.poolTank, {S}.DEPTH.poolWater, {W}.story.lever.frame.name]")
    ok &= check(v[0] and not v[1] and v[2] and v[4] < v[3] < v[5] and v[6] == 0,
                "the hatch (shut) and the drain's grate lie on the tank's floor under the water; the lever is armed", v)
    ok &= check(0 < pool1["x1"] - hx < 200 and pool1["x0"] < L["drainX"] < pool1["x1"], "the hatch within view of the aft rim, the grate in the tank", (hx, L["drainX"], pool1))
    v = js(b, f"[{W}.pool.shut.obj.alpha, {W}.pool.drain.obj.alpha, {W}.pool.shutWash.obj.alpha, {W}.pool.drainWash.obj.alpha, {W}.pool.shutWash.obj.visible, {W}.pool.drainWash.obj.visible]")
    ok &= check(v[:2] == [1, 1] and min(v[2:4]) > 0.6 and v[4] and v[5], "under the water both are washed out toward the floor's tiles, not seen through", v)
    line = f"{W}.movers.find(m => m.def && m.def.id === 'haz_line_10a')"
    b.teleport(pool1["x1"] - 230, D11)
    wait(0.5)
    ok &= check(js(b, f"{line}.items.every(i => !i.visible)"), "from deck 11 the laundry line of the balcony under the pool is not shown")
    b.teleport(pool1["x1"] - 230, D11)
    wait(0.8)
    ok &= check(b.state()["mode"] == "swim", "the first pool fills the deck: she swims", b.state())
    hold_until(b, "right", lambda s: s["mode"] == "scripted", 6)
    cat = f"{W}.story.poolCat.sprite"
    ok &= check(wait_js(b, f"['her-swim-reach', 'her-swim-strain'].includes({S}.player.anims.currentAnim && {S}.player.anims.currentAnim.key)", 4),
                "under him at the rim she looks up out of the water and reaches for him")
    b.shot("region6-reach")
    ok &= check(wait_js(b, f"{who('npc_kid_tub')}.sprite.y < {D11 - 5}", 5), "the kid stands up in the hot tub")
    b.shot("region6-beat")
    ok &= check(wait_js(b, f"{cat}.visible && {cat}.depth < {S}.DEPTH.swimmer && {cat}.y > {D11 + 8} && {cat}.x < {pool1['x1']}", 5),
                "squirted into the pool, Bumbot paddles back for the rim, his legs under the water")
    ok &= check(wait_js(b, f"{W}.story.lever.frame.name > 0 && Math.abs({cat}.x - {L['leverX']}) < 40 && {cat}.y < {D11 - 20}", 6),
                "out, shaken dry, and up onto the lever's grip: it goes over under him")
    b.shot("region6-lever")
    ok &= check(wait_js(b, f"{S}.save.flags.includes('bb5')", 14), "near-catch 5: thrown across the hot tub, he is gone aft", flags(b))
    last = js(b, f"{W}.story.leverLay.frames") - 1
    ok &= check("drain" in flags(b) and js(b, f"{W}.story.lever.frame.name") == last, "the drain's lever is thrown")
    ok &= check(wait_js(b, f"{S}.pools.length === 3 && {S}.pools[0].y > {D11 + 8}", 4), "the water sinks", js(b, f"{S}.pools.map(p => p.y)"))
    ok &= check(js(b, f"{W}.pool.puddles.obj.alpha") == 0, "no puddles yet: they show only as the last of it goes", js(b, f"{W}.pool.puddles.obj.alpha"))
    ok &= check(b.state()["mode"] == "swim", "she is still in the water as it starts to sink", b.state())
    ok &= check(wait_js(b, f"{S}.mode === 'play' && {S}.player.y === {D11 + 32}", 8), "the water gone, she stands in the empty tank", b.state())
    wait(0.2)
    ok &= check(js(b, f"{S}.herDropPx()") == 6, "her picture 5 px lower there, on the floor's strip of tiles", js(b, f"{S}.herDropPx()"))
    # (Her feet find the floor while the last of the water is still going.)
    ok &= check(wait_js(b, f"!{W}.pool.shutWash.obj.visible && !{W}.pool.drainWash.obj.visible && {W}.pool.shut.obj.alpha === 1", 5), "the last water gone, the hatch and the grate are clear")
    b.shot("region6-drained")
    ok &= check(not person(b, "npc_kid_tub")["on"] and person(b, "npc_kid")["on"], "the kid has left the hot tub for the aft pool deck")
    # The hatch in the tank's floor; deck 10's hallway: the trays outside a "Do Not Disturb" door.
    b.teleport(hx - 40, D11 + 32)
    wait(0.3)
    hold_until(b, "right", lambda s: abs(s["x"] - hx) < 12, 3)
    wait(0.2)
    ok &= check("thing:hatch_pool" in js(b, f"JSON.stringify({S}.highlight.state())"), "at the hatch it pulses", js(b, f"JSON.stringify({S}.highlight.state())"))
    b.tap("e")
    ok &= check(wait_js(b, f"{W}.pool.back.obj.visible && !{W}.pool.shut.obj.visible && {S}.save.flags.includes('pool_hatch')", 3),
                "E: she heaves its lid up against the tank's wall")
    ok &= check(wait_js(b, f"{S}.player.isCropped && {S}.player.y > {D11 + 40} && {W}.pool.lip.obj.depth > {S}.player.depth && {W}.pool.back.obj.depth < {S}.player.depth", 4),
                "and goes down its ladder: before the lid, behind the hatch's near edge")
    b.shot("region6-hatch")
    s = hold_until(b, [], lambda s: s["mode"] == "play" and s["y"] == D10, 8)
    ok &= check(s["y"] == D10 and abs(s["x"] - hx) < 4 and js(b, f"{W}.pool.ceilOpen.visible && !{W}.pool.ceilShut.visible && !{S}.player.isCropped && {S}.herDropPx() === 1"),
                "out of the hallway's ceiling panel, onto deck 10's carpet, her picture where it always is", s)
    trays = js(b, f"{W}.data.ents.find(e => e.kind === 'trays')")
    # (2026-11-18: one tray, run onto, ridden off down the hallway (3); the door opens after on the
    # guest looking after her.)
    tr = mover("haz_trays_10m")
    hold_until(b, "right", lambda s: js(b, f"!!{tr}.riding") or s["mode"] != "play", 5)
    ok &= check(js(b, f"!!{tr}.riding") and "Whoops" in alert(b), "running onto the tray, she rides it off down the hallway", alert(b))
    b.shot("region6-trays")
    ok &= check(wait_js(b, f"{mover('haz_dnd_10m')}.busy", 5), "and its door opens on the guest looking after her")
    ok &= check(wait_js(b, "window.__ship.mode === 'play'", 8) and "trays_10m" in flags(b), "she comes back at a checkpoint", b.state())
    ok &= check(js(b, f"{S}.tangerines.some(t => t.id === 'tan_10_tray')"), "a tangerine has rolled out from among the trays")
    b.teleport(trays["x0"] - 42, D10)
    wait(0.6)
    b.key("right", True)
    wait(0.2)
    b.key("space", True)
    wait(0.35)
    b.key("space", False)
    wait(0.75)
    b.key("right", False)
    wait(0.6)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["x"] > trays["x1"] and js(b, f"{mover('haz_trays_10m')}.armed"), "a jump clears the trays", s)
    ok &= check(all(js(b, f"!!{mover(m)}") for m in ("haz_swing_10m", "haz_sprinkler_10m", "haz_dnd_10m2")), "further aft: a swinging door, a sprinkler, another door not to knock at")
    b.teleport(exact_x(110) + 16, D10)
    wait(0.4)
    b.tap("e")
    wait(0.3)
    ok &= check(door_open(b, "part-door-10-110"), "the hallway's lobby door opens from inside")
    # Back on deck 11. The hot tub's canopy: up by a wall jump off its post, a tangerine on its roof.
    post = exact_x(131.03)
    had = len(save_list(b, "collected"))
    b.teleport(post + 30, D11)
    wait(0.5)
    b.key("left", True)
    b.key("space", True)
    wait(0.16)
    b.key("space", False)
    wait(0.06)
    b.key("space", True)
    b.key("left", False)
    b.key("right", True)
    wait(0.3)
    b.key("space", False)
    wait(0.12)
    b.key("right", False)
    wait(0.8)
    s = b.state()
    ok &= check(s["y"] == D11 - 90, "a kick off the canopy's post takes her up onto its roof", s)
    b.shot("region6-canopy")
    fruit = exact_x(132.5)       # (the tangerine on the canopy: `tan_11_canopy`)
    hold_until(b, "right" if s["x"] < fruit else "left", lambda s: abs(s["x"] - fruit) < 6, 3)
    wait(0.2)
    ok &= check(len(save_list(b, "collected")) == had + 1, "and to the tangerine on it")
    # The hot tub.
    b.teleport(L["tubX"] - 10, D11)
    wait(0.5)
    b.tap("e")
    wait(2.4)
    b.shot("region6-hottub")
    ok &= check(b.state()["mode"] == "scripted", "E at the hot tub: she gets in", b.state())
    b.tap("space")
    ok &= check(wait_js(b, f"{S}.mode === 'play'", 4) and "sec_hottub" in save_list(b, "seen"), "and out again at a key")
    # The second pool; the attendant's hut on its aft rim.
    b.teleport(pool2["x1"] - 70, D11)
    wait(0.8)
    b.hold("right", 0.5)
    b.key("right", True)
    b.tap("space")
    wait(1.2)
    b.key("right", False)
    wait(0.2)
    ok &= check(b.state()["y"] == D11 and "cp_pool" in save_list(b, "activated"), "out of the second pool at the pool attendant's hut: a checkpoint", b.state())
    # The kid: his jet; the dash sends him off.
    kid = who("npc_kid")
    ok &= check(person(b, "riv_loungers")["on"], "the security officer on his knees at a lounger")
    b.eval(f"{kid}.x = {L['kidA'] + 190}; {kid}.dir = -1; {kid}.mode = 'patrol'; {kid}.nextSquirt = 0; {kid}.pauseUntil = 0")
    b.teleport(L["kidA"] + 70, D11)
    ok &= check(scared(b, "Aaah", 4), "in front of the kid within four metres: splashed", alert(b))
    wait(0.3)
    ok &= check(js(b, f"{S}.worldLayer.list.some(o => (o.anims?.currentAnim?.key || '').startsWith('gags-sprinkler'))"),
                "the wet gag (16's), whatever she carries (1.2a)", js(b, f"{S}.worldLayer.list.filter(o => (o.anims?.currentAnim?.key || '').startsWith('gags')).map(o => o.anims.currentAnim.key).join(',')"))
    b.shot("region6-kid")
    ok &= check(wait_js(b, "window.__ship.mode === 'play'", 8) and abs(b.state()["x"] - js(b, f"{S}.checkpoints.find(c => c.id === 'cp_pool').x")) < 30,
                "and back at the hut", b.state())
    b.eval(f"{S}.save.tangerines += 2; {S}.refreshHud()")
    b.eval(f"{kid}.x = {L['kidA'] + 190}; {kid}.dir = -1; {kid}.mode = 'patrol'; {kid}.nextSquirt = {S}.time.now + 1500; {kid}.pauseUntil = 0")
    b.teleport(L["kidA"] + 70, D11)
    wait(0.15)
    b.tap("d")
    wait(0.4)
    ok &= check(js(b, f"{kid}.mode") in ("flee", "hide"), "her shout sends him running to the far end", js(b, f"{kid}.mode"))
    wait(3.0)
    ok &= check(b.state()["mode"] == "play" and js(b, f"{kid}.mode") == "hide", "where he keeps his back turned", js(b, f"{kid}.mode"))
    wait(7.5)
    # The wet patch and its deck chair.
    wet = js(b, f"{W}.data.ents.find(e => e.kind === 'wet')")
    b.eval(f"{kid}.gone = true; {W}.refresh()")
    b.teleport(wet["x0"] - 60, D11)
    wait(0.3)
    b.hold("right", 0.6)
    x1 = b.state()["x"]
    wait(0.3)
    ok &= check(abs(b.state()["x"] - x1) < 12 and b.state()["mode"] == "play", "in the grip socks the wet tiles hold her", (x1, b.state()))
    b.teleport(wet["x0"] - 60, D11)
    b.eval(f"{S}.save.verbs = {S}.save.verbs.filter(v => v !== 'socks')")
    wait(0.4)
    b.hold("right", 0.55)
    x1 = b.state()["x"]
    wait(0.2)
    ok &= check(b.state()["x"] - x1 > 18, "without them she slides on across them", (x1, b.state()))
    ok &= check(scared(b, "Oops", 2), "and she slides into the deck chair standing at its end: bumped", alert(b))
    # (7a, head on with none on her: face first onto it, and she sleds on it the way she dived.)
    sled = "(() => { const g = window.__ship.worldLayer.list.find(o => o.anims && o.anims.currentAnim && o.anims.currentAnim.key === 'gags-sledge'); return g ? Math.round(g.x) : null; })()"
    x0s = js(b, sled)
    wait(1.4)
    x1s = js(b, sled)
    ok &= check(x0s is not None and x1s is not None and 15 < x1s - x0s and x1s <= wet["x1"] + 14,
                "head on: face first onto the chair, she sleds on it aft, short of the palm", (x0s, x1s, wet["x1"]))
    b.shot("region6-wet")
    wait_js(b, "window.__ship.mode === 'play'", 8)
    wait(2.5)
    b.teleport(wet["x0"] - 60, D11)
    wait(0.4)
    b.key("right", True)
    wait(0.94)
    b.key("space", True)
    wait(0.3)
    b.key("space", False)
    wait(0.8)
    b.key("right", False)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["x"] > wet["x1"], "a jump clears the chair", s)
    # From aft, past the chair onto the tiles: she slides forward, away from it, and nothing trips her.
    wait(1.0)
    b.teleport(wet["chairX"] + 40, D11)
    wait(0.4)
    b.key("left", True)
    hold_until(b, [], lambda s: s["x"] < wet["x1"] - 10, 2)
    b.key("left", False)
    wait(1.2)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["x"] < wet["x0"] + 10, "from aft she slides forward across it, the chair behind her", s)
    b.eval(f"{S}.progress.learn('socks'); {kid}.gone = false; {W}.refresh()")
    wait(3.3)
    # The Garden Cafe: the queue.
    q = js(b, f"{W}.data.ents.find(e => e.kind === 'queue')")
    line = lambda: sorted(js(b, f"{W}.people.list.filter(p => p.id.startsWith('haz_queue') && p.blocking).map(p => Math.round(p.x))"))
    first = line()[0]
    b.teleport(first - 110, D11)
    wait(0.4)
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
    wait(1.0)
    ok &= check(route(b) == "coldroom", "the cold room, with the Housekeeping card", route(b))
    b.teleport(cold + 150, D11, "coldroom")
    wait(0.3)
    b.tap("e")
    wait(0.3)
    ok &= check(carrying(b) is None, "the canister stays on its shelf until the machine wants it")
    b.shot("region6-coldroom")
    b.teleport(door, D11, "coldroom")
    b.tap("e")
    wait(1.0)
    # The aft lobby: the fans on the stairs.
    s = climb(b, "stairs-aft-11-12", 0.6)
    ok &= check(s["y"] == D11 and "BIG GAME" in blocked(b) and person(b, "blk_fan_a")["on"], "the aft flight up: the Sports Bar's fans", blocked(b))
    b.shot("region6-fans")
    wait(0.6)
    # The Great Outdoors: the machine. A short swirl, too long a one, and a proper one.
    ok &= check(person(b, "npc_husband")["on"] and not js(b, f"{who('npc_husband')}.bubbleItems[0].visible"), "her husband at the first table, by the machine")

    def swirl(sec):
        b.teleport(L["machineX"] - 14, D11)
        wait(0.4)
        b.key("e", True)
        wait(sec)
        b.key("e", False)
        wait(0.35)
        return js(b, f"{W}.story.lastSwirl")

    c0 = b.eval("(c => [c.whirr ?? 0, c.whirrDown ?? 0])(window.__sfx.counts)")
    ok &= check(swirl(0.9) == "stub" and carrying(b) == "stub", "E let go early: a stub", carrying(b))
    c1 = b.eval("(c => [c.whirr ?? 0, c.whirrDown ?? 0])(window.__sfx.counts)")
    ok &= check(c1[0] - c0[0] == 1 and c1[1] - c0[1] == 1, "its motor one held sound while E is held, and its run-down at the let-go", (c0, c1))
    b.eval(f"{kid}.x = {L['kidA'] + 120}; {kid}.mode = 'patrol'")
    b.teleport(L["kidA"] + 90, D11)
    wait(0.5)
    ok &= check(js(b, f"{kid}.pose") == "stand" and js(b, f"{kid}.bubbleItems[0].visible"), "with a cone in her hands the kid waits for it, his bubble a soft serve")
    b.tap("e")
    wait(3.2)
    ok &= check("kid_fed" not in flags(b) and carrying(b) is None and b.state()["mode"] == "play", "a stub: he drops it on the deck", flags(b))
    b.shot("region6-stub")
    b.eval(f"{kid}.nextSquirt = {S}.time.now + 60000")
    ok &= check(swirl(3.2) == "toppled" and carrying(b) is None, "held too long: it goes over")
    ok &= check(js(b, f"{W}.foodGulls.gull_go.state") == "pounce", "and the gull is on it")
    b.shot("region6-toppled")
    wait(3.5)
    ok &= check(swirl(1.75) == "cone" and carrying(b) == "cone", "let go in the green: a proper cone", carrying(b))
    b.shot("region6-cone")
    ok &= check(0.5 < js(b, f"{W}.carryBox.left()") < 1, "and it is melting")
    # Standing about with it in the open: the gull has it.
    ok &= check(wait_js(b, f"{W}.foodGulls.gull_go.state === 'mark'", 6), "it hangs over the spot she is at")
    ok &= check(wait_js(b, f"!{W}.carry", 4) and js(b, f"{W}.foodGulls.gull_go.stolen") == 1 and b.state()["mode"] == "play", "then the gull has her cone: no fright")
    b.shot("region6-gull")
    wait(1.2)
    # Another; through the queue with it (they let crew with a tray by); to the kid.
    ok &= check(swirl(1.75) == "cone" and carrying(b) == "cone", "another cone")
    b.teleport(q["x1"] + 60, D11)
    wait(0.3)
    s = hold_until(b, "left", lambda s: s["x"] < q["x0"] - 20, 12)
    ok &= check(s["x"] < q["x0"] and carrying(b) == "cone", "the queue turns aside for crew with a tray", (s, carrying(b)))
    b.eval(f"{kid}.x = {L['kidA'] + 120}; {kid}.mode = 'patrol'")
    b.teleport(L["kidA"] + 90, D11)
    wait(0.5)
    b.tap("e")
    wait(1.2)
    b.shot("region6-kid-eats")
    k = js(b, f"[{kid}.state, Math.round({kid}.x)]")
    ok &= check(b.state()["mode"] == "play" and k[0] == "acting" and abs(b.state()["x"] - k[1]) >= 20,
                "the cone in his hand, she is free, a step from him, while he eats", (b.state(), k))
    ok &= check(wait_flag(b, "kid_fed", 8) and carrying(b) is None, "a proper cone for the kid: he eats it", flags(b))
    ok &= check(js(b, f"{W}.foodGulls.gull_pool.off()"), "from now on he keeps the gulls off the pool deck")
    wait(3.0)
    ok &= check(b.state()["mode"] == "play", "and never squirts her again", b.state())
    # The machine has run empty; his bubble: the canister; the cold room; no hopping with it.
    ok &= check(swirl(1.5) != "stub" and carrying(b) is None and b.state()["mode"] == "play", "the machine has run empty")
    b.teleport(L["husbandX"] - 40, D11)
    wait(0.5)
    ok &= check(js(b, f"{who('npc_husband')}.bubbleItems[0].visible") and js(b, f"{who('npc_husband')}.bubbleItems[1].texture.key") == "pict-canister",
                "her husband's bubble: the canister")
    b.shot("region6-husband")
    b.teleport(door, D11)
    b.tap("e")
    wait(1.0)
    b.teleport(cold + 150, D11, "coldroom")
    wait(0.3)
    b.tap("e")
    wait(0.3)
    ok &= check(carrying(b) == "canister", "the ice cream mix's canister, from the cold room's shelf", carrying(b))
    y0 = b.state()["y"]
    b.hold("space", 0.3)
    ok &= check(b.state()["y"] == y0, "too heavy to hop with")
    b.teleport(door, D11, "coldroom")
    b.tap("e")
    wait(1.0)
    b.teleport(L["machineX"] - 14, D11)
    wait(0.3)
    b.tap("e")
    wait(1.0)
    b.shot("region6-pour")
    ok &= check(wait_flag(b, "refilled", 6) and carrying(b) is None, "poured into the machine: it has mix for good", flags(b))
    # A proper cone, and the table with him.
    ok &= check(swirl(1.75) == "cone" and carrying(b) == "cone", "a cone again")
    b.teleport(L["husbandX"] - 30, D11)
    wait(0.4)
    ok &= check(js(b, f"{who('npc_husband')}.bubbleItems[1].texture.key") == "pict-softserve", "his bubble now: a soft serve")
    b.tap("e")
    wait(3.0)
    b.shot("region6-table")
    ok &= check(wait_flag(b, "table", 12), "E with it: she sits down with him, and they eat looking at the wake", flags(b))
    ok &= check(js(b, f"{S}.save.books['1']") == "held", "he gives her the first book, Atomic Habits")
    ok &= check(js(b, f"{thing('slot_cucina')}.items[0].visible"), "their photo is on La Cucina's wall now")
    b.shot("region6-picture")
    # Every perfect cone while he is at his table: they sit down together again; his book only the first time.
    wait_js(b, f"{S}.mode === 'play'", 10)
    ok &= check(swirl(1.75) == "cone" and carrying(b) == "cone", "another cone: hers to carry while he is at his table", carrying(b))
    b.eval(f"(w => {{ w.__hands = 0; const o = w.handOver.bind(w); w.handOver = (...a) => (w.__hands++, o(...a)); }})({W})")
    b.teleport(L["husbandX"] - 30, D11)
    wait(0.4)
    b.tap("e")
    ok &= check(wait_js(b, f"{S}.mode === 'scripted'", 3) and wait_js(b, f"{S}.mode === 'play'", 16) and carrying(b) is None,
                "E with it: they eat together again", b.state())
    ok &= check(js(b, f"{W}.__hands") == 0 and js(b, f"{S}.save.books['1']") == "held", "no second book")
    # With him away from his table (from the catch on, after the ending too), a cone is hers: eaten where she stands. (The flag
    # set in the save alone, so that the finale's scenes do not start.)
    b.eval(f"{S}.save.flags.push('catch')")
    swirl(1.75)
    wait(0.5)
    ok &= check(b.state()["mode"] == "scripted" and carrying(b) is None, "him away: a cone for herself, eaten where she stands", b.state())
    b.shot("region6-herself")
    ok &= check(wait_js(b, f"{S}.mode === 'play'", 5) and "sec_cone" in save_list(b, "seen"), "and done")
    b.eval(f"{S}.save.flags = {S}.save.flags.filter(f => f !== 'catch')")
    # The crates behind the service station.
    crates = js(b, f"{thing('haz_crates_11')}.x")
    b.eval(f"{S}.save.tangerines += 1; {S}.refreshHud()")
    b.teleport(crates - 90, D11)
    wait(0.3)
    b.tap("d")
    b.hold("right", 0.9)
    ok &= check("haz_crates_11" in save_list(b, "broken") and js(b, f"{S}.tangerines.some(t => t.id.startsWith('tan_11_crates'))"),
                "the dash goes through the crates: two tangerines were behind them", save_list(b, "broken"))
    wait(0.5)
    return ok


def scenario_deliveries(b):
    """The deliveries (plan-the-rest §5 3.2). 1, the vase (deck 8 midships, the user, 2026-11-23): on its table by the aft
    lobby door from the start; E, in her hands on its narrow tray, the flower frame round the screen; gone at once in the
    outside view; a floor tray on the way spills it and plays its ride all the same; E at cabin 8215's door: a hand takes
    it, book 12 hers, the table and its tag gone. 2, the tea (deck 10 midships): see below."""
    S = "window.__ship"
    W = f"{S}.world"
    src = f"{W}.things.find(t => t.id === 'src_vase')"
    b.open("?reset&play&at=hall8")
    wait(0.4)
    ok = check(b.eval(f"{W}.shown({src})"), "the vase on its table from the start")
    x = b.eval(f"{src}.x")
    b.teleport(x - 14, D8)
    wait(0.3)
    b.tap("e")
    wait(0.6)
    v = b.eval(f"[{W}.carry?.kind, {W}.carryBox.items[0]?.texture.key, {W}.carryBox.view?.alpha]")
    ok &= check(v[0] == "vase" and v[1] == "tray-18" and v[2] == 1, "E: the vase on its narrow tray, the flower frame round the screen", v)
    b.tap("o")
    wait(0.3)
    v = b.eval(f"[!!{S}.overview, {W}.carryBox.view?.visible]")
    ok &= check(v == [True, False], "the outside view: no frame", v)
    b.tap("o")
    wait(0.8)
    # The ice bucket's tray: run at it, the vase spills, and she rides the tray off all the same.
    ice = b.eval(f"{W}.movers.find(m => m.def?.id === 'haz_trays_8ice').trays[0].x")
    b.teleport(ice + 110, D8)
    wait(0.3)
    hold_until(b, "left", lambda s: s["mode"] != "play", timeout=4)
    v = b.eval(f"[{S}.lastMishap?.what, !!{W}.movers.find(m => m.def?.id === 'haz_trays_8ice').pic, {W}.carry]")
    ok &= check(v[0] == "trays" and v[1] and v[2] is None, "a floor tray with the vase: spilled, and the ride", v)
    wait_for = now() + 8
    while now() < wait_for and b.eval(f"{S}.mode") != "play":
        wait(0.2)
    # Again, to the door.
    b.teleport(x - 14, D8)
    wait(0.3)
    b.tap("e")
    wait(0.4)
    door = b.eval(f"{W}.things.find(t => t.id === 'dlv_vase').x")
    b.teleport(door + 6, D8)
    wait(0.3)
    b.tap("e")
    wait(3.0)
    v = b.eval(f"[{S}.save.flags.includes('dlv_vase'), {S}.save.books?.['12'], {W}.carry, {W}.shown({src})]")
    ok &= check(v[0] and v[1] == "held" and v[2] is None and not v[3], "E at 8215: taken in, book 12 hers, the table gone", v)
    # 2, the pot of tea (deck 10 midships, the user, 2026-11-23): by the forward lobby door; in her hands its tray and pot
    # leave the table (back on it when it is lost), the HUD's meter orange, steam; turned to us it is at her middle in
    # front of her (her `carry-front`), her back to us behind her (`carry-back`); cold, it is gone; E at 10230: book 13.
    src = f"{W}.things.find(t => t.id === 'src_tea')"
    b.open("?reset&play&at=hall10")
    wait(0.4)
    x = b.eval(f"{src}.x")
    b.teleport(x - 14, D10)
    wait(0.3)
    b.tap("e")
    wait(0.5)
    v = b.eval(f"[{W}.carry?.kind, {W}.carryBox.items[0]?.texture.key, {src}.lifted.map(i => i.visible), {W}.carry?.hot]")
    ok &= check(v[0] == "tea" and v[1] == "tray-22" and v[2] == [False, False] and v[3], "E: the tea on its tray, gone from the table", v)
    v = b.eval(f"(() => {{ const s = {S}, p = s.player; s.mode = 'scripted'; s.pose('front'); {W}.carryBox.update();"
               f" const a = [p.frame.name == s.herFrames['carry-front'], {W}.carryBox.items.every(i => i.x === Math.round(p.x) && i.depth > p.depth)];"
               f" s.pose('back'); {W}.carryBox.update();"
               f" a.push(p.frame.name == s.herFrames['carry-back'], {W}.carryBox.items.every(i => i.x === Math.round(p.x) && i.depth < p.depth));"
               f" s.pose('stand'); s.mode = 'play'; return a; }})()")
    ok &= check(v == [True, True, True, True], "turned to us: at her middle in front, her hands raised; her back to us: behind her", v)
    b.eval(f"{W}.carryBox.until = {S}.time.now")
    wait(0.4)
    v = b.eval(f"[{W}.carry, {src}.lifted.map(i => i.visible)]")
    ok &= check(v[0] is None and v[1] == [True, True], "gone cold: lost, a fresh pot on the table", v)
    b.tap("e")
    wait(0.4)
    door = b.eval(f"{W}.things.find(t => t.id === 'dlv_tea').x")
    b.teleport(door + 6, D10)
    wait(0.3)
    b.tap("e")
    wait(3.0)
    v = b.eval(f"[{S}.save.flags.includes('dlv_tea'), {S}.save.books?.['13'], {W}.carry, {W}.shown({src})]")
    ok &= check(v[0] and v[1] == "held" and v[2] is None and not v[3], "E at 10230: taken in, book 13 hers, the table gone", v)
    # 3, the pillows (deck 9 aft, the user, 2026-11-23): three on the laundry cart by the forward lobby door; the low hop;
    # stopped short from a run the top one slides off ahead and the door will not take the rest; E at it: her crouch puts it
    # back; a spill scatters all three; E at 9245: a thank-you from the crack, no book, no heart.
    src = f"{W}.things.find(t => t.id === 'src_pillows')"
    b.open("?reset&play&at=hall9a")
    wait(0.4)
    x = b.eval(f"{src}.x")
    b.teleport(x - 14, D9)
    wait(0.3)
    b.tap("e")
    wait(0.4)
    v = b.eval(f"[{W}.carry?.kind, {W}.carryBox.items.length, {src}.lifted.map(i => i.visible), {S}.jumpScale()]")
    ok &= check(v[0] == "pillows" and v[1] == 3 and v[2] == [False, False, False] and v[3] < 1, "E: three pillows off the cart, the low hop", v)
    b.hold("left", 0.6)
    wait(0.6)
    v = b.eval(f"[!!{W}.carryBox.fallen, {W}.carryBox.items.length]")
    ok &= check(v == [True, 2], "stopped short from a run: the top one slides off", v)
    b.tap("e")
    wait(1.2)
    v = b.eval(f"[!!{W}.carryBox.fallen, {W}.carryBox.items.length, {S}.mode]")
    ok &= check(v == [False, 3, "play"], "E at it: she crouches and it is back on top", v)
    b.eval(f"{W}.carryBox.spill({S}.player.x - 20)")
    wait(0.3)
    v = b.eval(f"[{W}.carry, {src}.lifted.every(i => i.visible)]")
    ok &= check(v[0] is None and v[1], "a spill: all three scatter, a fresh stack on the cart", v)
    wait(1.0)
    b.teleport(x - 14, D9)
    wait(0.3)
    b.tap("e")
    wait(0.4)
    door = b.eval(f"{W}.things.find(t => t.id === 'dlv_pillows').x")
    b.teleport(door + 6, D9)
    wait(0.3)
    b.tap("e")
    wait(1.4)
    v = b.eval(f"[{S}.popups.list.some(p => p.visible && p.text === 'Thank you!'), {S}.mode]")
    wait(2.0)
    v += b.eval(f"[{S}.save.flags.includes('dlv_pillows'), {W}.carry, {W}.shown({src})]")
    ok &= check(v[0] and v[2] and v[3] is None and not v[4], "E at 9245: taken in with a thank-you, the cart's pillows gone", v)
    return ok


def scenario_region7(b):
    """Region 7 (docs/build-plan.md, step 7): Outside: the balconies of decks 8-10 in the grip socks
    (a vault over a partition, a climb up its pole, gusts, a perched gull, a laundry line, a balcony
    with someone on it), an ajar balcony cabin and the hallway behind it, the guest locked out on
    his balcony and his book, the steward on his rounds, the boat walkway (the drill, the security
    officer, the columns up, the ladder down)."""
    W = "window.__ship.world"
    GUST = f"{W}.gusts.phase(window.__ship.time.now)"
    D7, UNIT = floor_y(7), 125

    def tap2(gap=0.2):
        b.key("space", True); wait(0.08); b.key("space", False)
        wait(gap)
        b.key("space", True); wait(0.08); b.key("space", False)

    def calm(least=2.6):
        """Waits for the lull after a gust."""
        wait_js(b, f"{GUST} === 'calm' && (window.__ship.time.now / 1000) % 7 < {7 - 2.2 - least}", 9)

    def lit():
        return save_list(b, "activated")

    # Without the socks the balcony cabin's balcony is region 4's dead end.
    enter_region6(b)
    bc = room(b, "balcabin9")
    b.teleport(bc["doors"][1]["outX"], D9, "promenade")
    wait(0.4)
    ok = check(7 not in save_list(b, "regions"), "without the socks the balcony is not region 7 yet", save_list(b, "regions"))
    enter_region7(b)
    ok &= check(7 in save_list(b, "regions") and "cp_balc_9" in lit(), "in the socks, out on the balcony: region 7; its door a checkpoint",
                (save_list(b, "regions"), lit()))
    home = b.state()["x"]
    unit = home - home % UNIT - (3500 % UNIT)
    # A vault: at the partition, jump and jump again.
    calm()
    b.key("right", True)
    hold_until(b, [], lambda s: s["x"] > unit + 92, 3)
    tap2()
    wait(1.0)
    b.key("right", False)
    s = b.state()
    ok &= check(s["y"] == D9 and unit + UNIT < s["x"] < unit + 2 * UNIT, "a kick off the partition vaults it onto the next balcony", s)
    b.shot("region7-vault")
    # Up its pole to deck 10, with up held.
    calm()
    b.hold("left", 0.9)
    b.key("up", True)
    for _ in range(4):
        b.key("space", True); wait(0.08); b.key("space", False)
        wait(0.27)
    wait(0.9)
    b.key("up", False)
    s = b.state()
    ok &= check(s["y"] == D10, "kicks with up held climb the pole to the balcony above", s)
    # A gust: in the air she is carried aft.
    b.teleport(unit + UNIT + 60, D10, "promenade")
    wait_js(b, f"{GUST} === 'blow'", 9)
    wait(0.1)
    x0 = b.state()["x"]
    b.key("space", True); wait(0.45); b.key("space", False)
    wait(0.6)
    s = b.state()
    ok &= check(s["x"] - x0 > 20 and s["mode"] == "play", "a gust carries her aft in the air", (x0, s))
    b.shot("region7-gust")
    # Down a deck: down and jump.
    calm(1.5)
    b.key("down", True); wait(0.1)
    b.key("space", True); wait(0.08); b.key("space", False)
    wait(0.2)
    b.key("down", False)
    wait(0.9)
    ok &= check(b.state()["y"] == D9, "down and jump drops her to the balcony below", b.state())
    # The balcony where Bumbot swiped at the gull: a tangerine.
    n = len(save_list(b, "collected"))
    t = js(b, "window.__ship.tangerines.find(t => t.id === 'tan_10_balc').sprite.x")
    b.teleport(t - 30, D10, "promenade")
    b.hold("right", 0.5)
    ok &= check(len(save_list(b, "collected")) == n + 1, "a tangerine on the balcony table a deck up", save_list(b, "collected"))
    # A balcony with someone on it: "Startled", and back at the lit balcony door.
    o = js(b, f"{W}.data.balcony.occupied.find(o => o.id === 'haz_breakfast')")
    b.teleport(o["x0"] - 50, o["y"], "promenade")
    calm(1.2)
    b.key("right", True)
    hold_until(b, [], lambda s: s["x"] > o["x0"] - 30, 3)
    tap2()
    got = scared(b, "sorry", 2.5)
    b.shot("region7-occupied")
    b.key("right", False)
    ok &= check(got, "vaulting onto the breakfast couple's balcony: startled", (b.state(), alert(b)))
    s = hold_until(b, [], lambda s: s["mode"] == "play", 6)
    ok &= check(s["mode"] == "play" and abs(s["x"] - home) < 3 and s["y"] == D9, "she comes to at the balcony cabin's door", s)
    pocket = b.state()["tangerines"]
    b.eval("window.__ship.save.tangerines = 0; window.__ship.refreshHud()")   # (with one on her the gull takes it instead: 1.2a)
    # A perched gull: lingering by it, it goes up over her and swoops; moving on, nothing.
    g = js(b, f"{W}.data.balcony.perch.find(p => p.id === 'gull_10_2')")
    marked = f"{W}.movers.some(m => m.def && m.def.id === 'gull_10_2' && m.state === 'mark')"
    b.teleport(g["x0"] + 50, g["floor"], "promenade")
    ok &= check(wait_js(b, marked, 5), "lingering by a gull on the rail: it goes up over her")
    b.hold("left", 0.45)
    wait(1.6)
    ok &= check(b.state()["mode"] == "play", "a step aside and it comes down on nothing", (b.state(), alert(b)))
    wait(3.2)
    b.teleport(g["x0"] + 50, g["floor"], "promenade")
    wait_js(b, marked, 6)
    got = scared(b, "Shoo", 3.0)
    b.shot("region7-gull")
    ok &= check(got, "standing where its shadow is: swooped", (b.state(), alert(b)))
    hold_until(b, [], lambda s: s["mode"] == "play", 6)
    b.eval(f"window.__ship.save.tangerines = {pocket}; window.__ship.refreshHud()")
    # A laundry line across a folded partition: under it on hands and knees.
    lx = js(b, f"{W}.data.balcony.lines.find(l => l.id === 'haz_line_10b').x")
    b.teleport(lx - 70, D10, "promenade")
    b.hold("right", 0.9)
    b.hold(["right", "space"], 0.7)
    ok &= check(b.state()["x"] < lx - 15, "the washing on the line stops her, walking or jumping", (b.state()["x"], lx))
    b.key("down", True); wait(0.15)
    b.key("right", True); wait(0.5)
    b.shot("region7-line")
    wait(0.9)
    b.key("right", False); b.key("down", False)
    wait(0.3)
    ok &= check(b.state()["x"] > lx + 30, "she crawls under it", (b.state()["x"], lx))
    # The guest locked out on his balcony: he waves, his bubble a door; his door is shut from outside.
    gr = room(b, "guest10")
    gx = gr["doors"][1]["outX"]
    b.teleport(gx - 110, D10, "promenade")
    wait(0.8)
    guest = person(b, "npc_balcony_guest")
    ok &= check(guest["on"] and js(b, f"{W}.people.byId.npc_balcony_guest.bubbleItems[0].visible"), "the guest on his balcony: his bubble shows a door", guest)
    b.shot("region7-guest-out")
    b.teleport(gx, D10, "promenade")
    b.tap("e")
    wait(0.6)
    ok &= check(route(b) == "promenade" and "guest" not in flags(b), "his balcony door doesn't open from outside", route(b))
    ok &= check("cp_balc_guest" in lit(), "(a checkpoint all the same)", lit())
    # The ajar balcony cabin on deck 10 aft: in, and out of its corridor door into the hallway.
    ar = room(b, "balcabin10a")
    b.teleport(ar["doors"][1]["outX"], D10, "promenade")
    wait(0.3)
    b.shot("region7-ajar")
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "balcabin10a" and "cp_balc_10a" in lit(), "the ajar balcony door: into the cabin", (route(b), lit()))
    b.shot("region7-cabin")
    b.teleport(ar["doors"][0]["x"], D10, "balcabin10a")
    b.tap("e")
    wait(0.9)
    s = b.state()
    ok &= check(route(b) == "inside" and s["y"] == D10 and "cp_hall_10a" in lit(), "out of its corridor door into deck 10's aft hallway", (route(b), s, lit()))
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "balcabin10a", "which opens from the hallway now", route(b))
    b.tap("e")
    wait(0.9)
    # The tray by the "Do Not Disturb" door: run onto, she rides it off (3, 2026-11-18); and back at
    # the cabin's door.
    tr = js(b, f"{mover('haz_trays_10a2')}.def")
    b.teleport(tr["x1"] + 40, D10)
    b.hold("left", 0.5)
    got = scared(b, "Whoops", 2.5)
    b.shot("region7-trays")
    ok &= check(got, "running onto the tray by the door, she rides it off", (b.state(), alert(b)))
    s = hold_until(b, [], lambda s: s["mode"] == "play", 6)
    ok &= check(abs(s["x"] - ar["doors"][0]["outX"]) < 3 and route(b) == "inside", "she comes to at the cabin's door in the hallway", s)
    wait(2.0)
    b.teleport(tr["x1"] + 30, D10)
    b.hold(["left", "space"], 0.5)
    # (On until past them, not for a time: 0.25 s ended over them once real time's slack was gone.)
    s = hold_until(b, "left", lambda s: s["mode"] != "play" or s["x"] < tr["x0"], 1.0)
    ok &= check(s["mode"] == "play" and s["x"] < tr["x0"], "a jump clears them", s)
    ok &= check(use_door(b, 10, 202, 1), "the lobby's door opens from the hallway")
    # The door that flies open.
    sw = mover("haz_swing_10a")
    wx = js(b, f"{sw}.def.x")
    b.teleport(wx - 100, D10)
    ok &= check(wait_js(b, f"{sw}.state === 'burst' || {sw}.state === 'open'", 4), "a door flies open as she comes near", js(b, f"{sw}.state"))
    b.shot("region7-swing")
    ok &= check(b.state()["mode"] == "play", "short of it, no harm", b.state())
    # The guest's cabin, with the green card; his balcony door opened from inside: he comes in, the book.
    b.teleport(gr["doors"][0]["outX"], D10)
    wait(0.3)
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "guest10", "his cabin opens with the Housekeeping card", (route(b), alert(b)))
    b.teleport(gr["doors"][1]["x"], D10, "guest10")
    b.tap("e")
    wait(1.4)
    b.shot("region7-guest-in")
    ok &= check(wait_flag(b, "guest", 10), "E at his balcony door: he is let in", flags(b))
    ok &= check(js(b, "window.__ship.save.books['7']") == "held", "his thanks: the seventh book", js(b, "JSON.stringify(window.__ship.save.books)"))
    ok &= check(person(b, "npc_guest_in")["on"] and not person(b, "npc_balcony_guest")["on"], "he is at home in his cabin",
                (person(b, "npc_guest_in"), person(b, "npc_balcony_guest")))
    b.shot("region7-guest-home")
    b.teleport(gr["doors"][1]["x"], D10, "guest10")
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "promenade" and b.state()["y"] == D10, "and his balcony door is a way out, and in, for good", (route(b), b.state()))
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "guest10", "(in)", route(b))
    # Deck 8 midships: its aired cabin, the steward on his rounds across the hallway.
    mr = room(b, "balcabin8m")
    b.teleport(mr["doors"][1]["outX"], D8, "promenade")
    wait(0.3)
    b.tap("e")
    wait(0.9)
    b.teleport(mr["doors"][0]["x"], D8, "balcabin8m")
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "inside" and b.state()["y"] == D8, "through deck 8's aired cabin into its hallway", (route(b), b.state()))
    rd = mover("haz_steward_rounds")
    js(b, f"(r => {{ r.x = r.def.stops[0] + 30; r.dir = 1; r.until = 0; r.aside = false; }})({rd})")
    b.teleport(js(b, f"{rd}.x") - 60, D8)
    b.hold("right", 1.6)
    s = b.state()
    rx = js(b, f"{rd}.x")
    b.shot("region7-rounds")
    ok &= check(s["x"] < rx and s["mode"] == "play", "the steward and his cart fill the hallway: she is held behind them", (s, rx))
    stop = js(b, f"{rd}.def.stops[1]")
    ok &= check(wait_js(b, f"{rd}.aside", 12), "at a door he pulls his cart in", js(b, f"{rd}.x"))
    b.shot("region7-rounds-aside")
    s = hold_until(b, "right", lambda s: s["x"] > stop + 20, 3)
    ok &= check(s["x"] > stop + 20 and s["mode"] == "play", "and she is past him", (s, stop))
    n = len(save_list(b, "collected"))
    t = js(b, "window.__ship.tangerines.find(t => t.id === 'tan_8_mid').sprite.x")
    b.teleport(t - 24, D8)
    b.hold("right", 0.4)
    ok &= check(len(save_list(b, "collected")) == n + 1, "a tangerine in the ice bucket's tray", save_list(b, "collected"))
    # Deck 8 aft's tray far from a door: ridden off as well, and back at a checkpoint.
    far = js(b, f"{mover('haz_trays_8a1')}.def")
    b.teleport(far["x1"] + 30, D8)
    b.hold("left", 0.5)
    ok &= check(scared(b, "Whoops", 2.5), "a tray far from its door: ridden off as well", (b.state(), alert(b)))
    ok &= check(wait_js(b, "window.__ship.mode === 'play'", 8), "and back at a checkpoint", b.state())
    # The first balcony of all: the framed picture.
    sl = js(b, f"(t => ({{ x: t.x, y: t.y }}))({W}.things.find(t => t.id === 'slot_balcony'))")
    b.teleport(sl["x"], D8, "promenade")
    wait(0.3)
    b.shot("region7-slot")
    b.tap("e")
    wait(0.9)
    ok &= check(b.state()["mode"] == "scripted", "the photo on deck 8's first balcony opens", b.state())
    b.tap("e")
    wait(0.6)
    ok &= check(b.state()["mode"] == "play" and "slot_balcony" in save_list(b, "seen"), "and closes on a key", b.state())
    # Down to the boat walkway, and up one of its columns again.
    col_x = exact_x(142.3)
    b.teleport(col_x - 40, D8, "promenade")
    calm(1.0)
    b.key("down", True); wait(0.1)
    b.key("space", True); wait(0.08); b.key("space", False)
    wait(0.2)
    b.key("down", False)
    wait(1.0)
    s = b.state()
    ok &= check(s["y"] == D7 and s["mode"] == "play", "from deck 8's balcony a drop to the boat walkway", s)
    b.hold("right", 0.2)
    b.key("up", True)
    for _ in range(4):
        b.key("space", True); wait(0.08); b.key("space", False)
        wait(0.27)
    wait(1.0)
    b.key("up", False)
    ok &= check(b.state()["y"] == D8, "and up a white column again, kick after kick", b.state())
    # The drill: just hoisted, she runs under it (the lull); running at it after, she sets it off and it
    # comes down on her well under it (15: on all fours, the boat down to her back, she crawls out); and the security
    # officer at the tender.
    d = js(b, f"{W}.data.drill")
    DR = f"{W}.story.drill"
    b.teleport(d["x"] - 50, D7, "promenade")
    wait_js(b, f"(a => a.idle && a.t < 7.2)({DR}.at(window.__ship.time.now))", 12)
    b.hold("right", 2.6)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["x"] > d["x"] + 252, "just hoisted, the drill's boat lets her under it", (s, d))
    # (From 330 px off its middle, as soon as the lull is over: from further the clock's round comes first,
    # and the boat comes down ahead of her and stops her at its end.)
    b.teleport(d["x"] + 126 - 330, D7, "promenade")
    wait_js(b, f"(a => a.idle && a.t > 8.3 && a.t < 8.6)({DR}.at(window.__ship.time.now))", 12)
    b.key("right", True)
    told = wait_js(b, f"{DR}.at(window.__ship.time.now).tell", 3)
    got = scared(b, "Ouch", 3.0)
    b.key("right", False)
    s = b.state()
    ok &= check(told and got and d["x"] + 40 < s["x"] < d["x"] + 212, "running at it, she sets it off: the lamp, and it comes down on her under it", (told, got, s, d))
    # (15 since 2026-11-21, the user: she sinks onto all fours, the boat down to her back, and crawls out from under it.)
    DG = "window.__ship.worldLayer.list.find(o => o.texture && o.texture.key === 'drill' && o.anims && o.anims.currentAnim && o.visible)"
    ok &= check(wait_js(b, f"{DR}.boat.y === {DR}.low - 26 && {DR}.pinned && window.__ship.mode === 'scripted'", 3),
                "on all fours, the boat down to her back", js(b, f"[{DR}.boat.y, {DR}.low, {DR}.pinned]"))
    b.shot("region7-drill")
    ok &= check(wait_js(b, f"(g => g && g.anims.currentAnim.key === 'drill-crawl' && g.x > {s['x']} + 30)({DG})", 4),
                "and she crawls away on all fours the way she was facing", js(b, f"(g => g && [g.anims.currentAnim.key, g.x])({DG})"))
    s = hold_until(b, [], lambda s: s["mode"] == "play", 6)
    ok &= check(route(b) == "promenade", "(she comes to outside)", (route(b), s))
    rv = person(b, "riv_walkway")
    ok &= check(rv["on"], "the security officer looks into a tender on the walkway", rv)
    b.teleport(rv["x"] - 200, D7, "promenade")
    wait(0.5)
    b.shot("region7-rival")
    b.hold("right", 0.6)
    ok &= check(wait_flag(b, "riv_walkway", 6), "seen, he hurries off aft", flags(b))
    # The station's ladder down to the promenade.
    gate = js(b, f"{W}.ladders[0]")
    b.teleport(gate["x"], gate["y1"], "promenade")
    b.hold("down", 2.4)
    s = b.state()
    ok &= check(s["y"] == gate["y0"] and route(b) == "promenade", "down the station's ladder to the promenade", s)
    return ok


def coffee_for_the_engineer(b):
    """Region 8's errand, start to end (the golden path's): a hot cup from the Great Outdoors' coffee
    station, up the aft stairs, through Teppanyaki between its flares, to the engineer at the
    technical ladder."""
    src = b.eval("window.__ship.world.things.find(t => t.id === 'src_coffee').x")
    b.teleport(src - 6, D11)
    wait(0.3)
    b.tap("e")
    wait(0.3)
    if carrying(b) != "coffee":
        return False
    (x0, y0), (x1, y1) = flight_feet("stairs-aft-11-12")
    b.teleport(x0, y0)
    hold_until(b, "up", lambda s: s["y"] == D12 and s["mode"] == "play", 8)
    # Forward through Teppanyaki: past each grill in its lull.
    for i in (1, 0):
        f = b.eval(f"window.__ship.world.data.topdeck.flares[{i}]")
        b.teleport(f["x"] + f["half"] + 14, D12)
        wait_js(b, f"window.__ship.world.story.flares[{i}].phase(window.__ship.time.now)[0] === 'calm'", 8)
        hold_until(b, "left", lambda s: s["x"] < f["x"] - f["half"] - 10, 4)
    if carrying(b) != "coffee":
        return False
    e = person(b, "npc_engineer")
    b.teleport(e["x"] + 40, D12)
    wait(0.3)
    b.tap("e")
    return wait_flag(b, "engineer", 16)


def scenario_region7__mask(b):
    """His sleep mask (§4 2.1, thing 14; deck 10's first balcony, the plan's §7f P3): not there before the table scene;
    after it, on the slats of deck 12's long lounger set on that balcony (the user's placing), and E takes it. The
    balconies' fixes of the same day (the user, 2026-11-21): ↓ and jump drops her only where a floor lies one deck
    under her (none under this balcony: she stays; the next one's drops her onto deck 9's), and her picture is cut at
    a partition and at the row's end (a stand-in of her, `balconyPic`, cropped to the balcony)."""
    S = "window.__ship"
    mask = f"{S}.world.things.find(t => t.id === 'keep_sleepmask')"
    lounger = ("JSON.stringify((() => { const out = []; const walk = l => { for (const o of l) { if (o.list) walk(o.list);"
               " if (o.frame?.name === 'sunlounger-long-w20' && o.y === %d) { const r = o.getBounds(); out.push([Math.round(r.x), Math.round(r.bottom)]); } } };"
               f" walk({S}.children.list); return out; }})())") % D10
    b.open("?reset&play&at=mask10")
    wait(0.4)
    ok = check(not b.eval(f"!!({mask}?.pick?.visible)"), "before the table scene: no mask on the lounger")
    got = json.loads(b.eval(lounger))
    ok &= check([3519, D10] in got, "the long lounger on deck 10's first balcony", got)
    # ↓ and jump: on the first balcony nothing is under her (decks 9 and 8 have none there): she stays on it.
    b.teleport(3610, D10, route="promenade")
    wait(0.3)
    b.key("down", True); b.tap("space"); b.key("down", False)
    wait(1.5)
    s = b.state()
    ok &= check(s["y"] == D10 and s["mode"] == "play", "no drop where no balcony is under her", s)
    b.teleport(3700, D10, route="promenade")
    wait(0.3)
    b.key("down", True); b.tap("space"); b.key("down", False)
    wait(1.5)
    s = b.state()
    ok &= check(s["y"] == D9, "the next balcony's floor drops her onto deck 9's", s)
    # Her picture cut at the partition: walking aft into it, the stand-in reaches no further than the panel.
    b.teleport(3600, D10, route="promenade")
    wait(0.2)
    b.hold("right", 0.5)
    # (Where the stand-in shows: its crop in the frame's columns, counted from the other side when it is turned.)
    cut = json.loads(b.eval(f"JSON.stringify((() => {{ const q = {S}.balconyPic, p = {S}.player, c = q._crop, rw = p.width;"
                            " const left = p.x - p.displayOriginX, b = p.flipX ? rw - c.x : c.x + c.width;"
                            f" return {{ shown: q.visible, right: Math.round(left + b), own: p._crop.width }}; }})())"))
    ok &= check(cut["shown"] and cut["right"] <= 3625 and cut["own"] == 0, "at a partition her picture stops at its panel", cut)
    b.close_up("mask-partition", 3620, D10 - 24, 100, 60, 6)
    b.open("?reset&play&at=mask10&did=table")
    wait(0.4)
    pick = b.eval(f"[{mask}.pick.visible, {mask}.pick.x, {mask}.pick.y]")
    ok &= check(pick == [True, exact_x(64.417), D10 - 12], "after it: on the lounger's slats", pick)
    b.close_up("mask-lounger", 3560, D10 - 24, 120, 60, 6)
    b.teleport(exact_x(64.417), D10, route="promenade")
    wait(0.3)
    b.tap("e")
    wait(0.4)
    ok &= check("keep:him:sleepmask" in b.eval(f"{S}.save.keeps"), "E takes it, his", b.eval(f"{S}.save.keeps"))
    return ok


def scenario_region8(b):
    """Region 8 (docs/build-plan.md, step 8): the climb from the Great Outdoors onto deck 12's aft
    terrace, Los Lobos' pinata, Teppanyaki's flares, the old lady on her sunbed and her mojito, the
    court's balls and its quirk, the engineer's coffee and the technical ladder, the funnel's
    stairway in its gusts, the horn and what it sets off (the card, the parasol, the book), the
    engineer's book, the telescope, and the glide down the atrium."""
    enter_region7(b)
    b.eval("(P => { ['guest', 'riv_walkway'].forEach(f => P.setFlag(f)); P.open('regions', 7); })(window.__ship.progress)")
    wait(1.0)
    b.eval("window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    W, T = "window.__ship.world", "window.__ship.world.data.topdeck"
    NOW = "window.__ship.time.now"
    lit = lambda: save_list(b, "activated")
    # Before region 8: the fans are on the aft stairs, the painter on the midship flight; no coffee yet.
    go(b, 11, 192)
    b.hold("right", 0.3)
    ok = check("cp_garden" in lit(), "the Garden Cafe's service door is lit on the way", lit())
    s = climb(b, "stairs-aft-11-12", 0.8)
    ok &= check(s["y"] == D11 and "BIG GAME" in blocked(b), "the aft flight up to deck 12 is roped off: the fans", blocked(b))
    wait(1.0)
    src = b.eval(f"{W}.things.find(t => t.id === 'src_coffee').x")
    b.teleport(src - 6, D11)
    b.tap("e")
    wait(0.2)
    ok &= check(not carrying(b), "no coffee to take before the engineer has asked", carrying(b))
    # The climb from the machine: a kick up the sun cover's post, along the cover, over the rail.
    # (Early in a lull of the terrace's gusts: a jump in one falls short.)
    tg = f"({NOW} / 1000) % {W}.data.topdeck.terrace.gust.every < 2.2"
    wait_js(b, tg, 9)
    b.teleport(exact_x(233) + 13, D11)
    b.key("space", True)
    wait(0.34)
    b.key("space", False)
    wait(0.02)
    b.key("left", True)
    b.key("space", True)
    wait(0.2)
    b.key("space", False)
    wait(1.0)
    b.key("left", False)
    s = b.state()
    ok &= check(s["y"] < D11 - 100, "a kick off the sun cover's post lands her on the cover", s)
    # (To the rail's foot, however long that takes: a jump begun short of it meets the rail's side.)
    hold_until(b, "left", lambda s: s["x"] < exact_x(220) + 9, 6)
    wait_js(b, tg, 9)
    b.hold(["left", "space"], 0.8)
    b.hold("left", 0.4)
    s = b.state()
    ok &= check(s["y"] == D12 and 8 in save_list(b, "regions"), "along the cover and over the rail: deck 12's aft terrace, region 8", s)
    b.shot("region8-terrace")
    ok &= check(not person(b, "blk_fan_a")["on"] and person(b, "amb_sportsbar_a")["on"], "the fans are off the stairs, in the Sports Bar",
                (person(b, "blk_fan_a"), person(b, "amb_sportsbar_a")))
    ok &= check(not person(b, "blk_painter")["on"], "and the painter has finished", person(b, "blk_painter"))
    pocket = b.state()["tangerines"]
    b.eval("window.__ship.save.tangerines = 0; window.__ship.refreshHud()")   # (with one on her the gull takes it instead: 1.2a)
    # The terrace's gull: lingering by it, a swoop.
    g = b.eval(f"{T}.terrace.gull")
    b.teleport(g["x"] - 40, D12)
    # (Within 8 s: 2 s lingering, 1 s marking her, the dive, and before them its flight back to its
    # rail if it is off it. 6 s ran out 13 ms before the swoop when it was flying back.)
    got = scared(b, "Shoo", 8.0)
    ok &= check(got, "lingering by the gull on the terrace's rail: swooped", "" if got else b.eval(
        f"(g => [g.state, Math.round(g.linger * 10) / 10, Math.round(g.at - window.__ship.time.now), Math.round((g.awayUntil ?? 0) - window.__ship.time.now),"
        f" window.__ship.mode, window.__ship.route, g.route, Math.round(window.__ship.player.x - g.def.x), Math.round(window.__ship.player.y - g.def.floor)])"
        f"(window.__ship.world.movers.find(m => m.def === window.__ship.world.data.topdeck?.terrace?.gull || (m.def && m.def.x === {g['x']} && m.constructor.name === 'PerchGull')))"))
    wait(3.0)
    s = b.state()
    ok &= check(s["y"] == D11 and abs(s["x"] - exact_x(192)) < 40, "she comes back at the Garden Cafe's door, a deck down", s)
    b.eval(f"window.__ship.save.tangerines = {pocket}; window.__ship.refreshHud()")
    # Up the aft stairs now, and aft to Los Lobos: the pinata hangs in the way.
    s = climb(b, "stairs-aft-11-12", 3.4)
    ok &= check(s["y"] == D12, "the aft stairs are free: up to deck 12's lobby", s)
    px = b.eval(f"{W}.breakables.find(t => t.id === 'sec_pinata').x")
    b.teleport(px - 70, D12)
    b.hold("right", 1.0)
    s = b.state()
    ok &= check(abs(s["x"] - (px - 16)) < 6, "walking, the pinata stops her", s["x"] - px)
    b.key("down", True)
    wait(0.15)
    b.key("right", True)
    wait(1.5)
    b.key("right", False)
    b.key("down", False)
    wait(0.3)
    s = b.state()
    ok &= check(s["x"] > px + 40 and "sec_pinata" not in save_list(b, "broken"), "on hands and knees she goes under it", s["x"] - px)
    b.eval("window.__ship.save.tangerines = Math.max(window.__ship.save.tangerines, 1)")
    b.tap("d")
    wait(0.1)
    b.hold("left", 1.1)
    wait(0.4)
    took = [t for t in save_list(b, "collected") if "pinata" in t]
    ok &= check("sec_pinata" in save_list(b, "broken") and len(took) == 3, "the dash goes through it: three tangerines come down", took)
    b.shot("region8-pinata")
    # Teppanyaki: the flares, each after its chef's flourish.
    f = b.eval(f"{T}.flares[1]")
    fl = f"{W}.story.flares[1].phase({NOW})[0]"
    b.teleport(f["x"] + f["half"] + 16, D12)
    wait_js(b, fl + " === 'on'", 9)
    wait(0.4)
    b.shot("region8-flare")
    wait_js(b, fl + " === 'calm'", 4)
    s = hold_until(b, "left", lambda s: s["x"] < f["x"] - f["half"] - 10, 4)
    ok &= check(s["mode"] == "play" and s["x"] < f["x"] - f["half"], "in the lull she walks past the grill", s)
    # (The chef answers her coming: run at a quiet grill, his flourish starts while she is still clear
    # of it, so that the flame is up as she gets there; she stops, and it flares in front of her.)
    FL = f"{W}.story.flares[1]"
    b.teleport(f["x"] + f["half"] + 150, D12)
    wait_js(b, f"{fl} === 'calm' && {NOW} >= {FL}.coolUntil && {FL}.next - {NOW} > 600", 9)
    b.key("left", True)
    end = now() + 1.5
    while now() < end and b.eval(fl) == "calm":
        wait(1 / 30)
    b.key("left", False)
    x = b.state()["x"]
    wait_js(b, fl + " === 'on'", 2)
    ok &= check(x > f["x"] + f["half"] + 40 and b.state()["mode"] == "play",
                "running at a quiet grill: the chef's flourish starts while she is clear of it; stopped, it flares in front of her",
                (x - f["x"], b.state()["mode"]))
    b.teleport(f["x"] + 14, D12)
    got = scared(b, "Hot", 8.0)
    ok &= check(got, "at the grill when it flares: singed")
    # (19, her gag: out of the smoke her face black, her hair on end; she blinks and coughs.)
    GAG = f"{W}.story.flares[1].pic"
    seen_gag = set()
    end = now() + 9
    while now() < end and b.state()["mode"] != "play":
        seen_gag.add(b.eval(f"{GAG}?.anims.currentAnim?.key ?? null"))
        wait(0.1)
    ok &= check({"gags-flare-blink", "gags-flare-cough"} <= seen_gag and b.state()["mode"] == "play",
                "sooty, her hair on end, she blinks and coughs out a puff; then she is back", sorted(k for k in seen_gag if k))
    b.eval(f"{W}.carryBox.take('coffee')")
    b.teleport(f["x"] + 14, D12)
    end = now() + 8
    while now() < end and carrying(b):
        wait(0.1)
    wait(0.4)
    ok &= check(not carrying(b) and b.state()["mode"] == "play", "with a tray a flare only spills it", (carrying(b), b.state()))
    # The engineer at the technical ladder: its chain; his coffee, still hot.
    F = b.eval(f"{T}.funnel")
    b.teleport(F["ladderX"], D12)
    b.hold("up", 0.6)
    ok &= check(b.state()["mode"] == "play" and "CREW ONLY" in blocked(b), "the technical ladder is chained off", blocked(b))
    wait(1.0)
    b.eval(f"{W}.carryBox.take('coffee'); {W}.carryBox.until = {NOW} + 1200")
    wait(1.8)
    ok &= check(not carrying(b), "a coffee gone cold is no use: it is put down", carrying(b))
    ok &= check(coffee_for_the_engineer(b), "a hot coffee from the Great Outdoors, up the aft stairs, past the flares: he drinks it and climbs the ladder",
                (carrying(b), flags(b)[-3:]))
    ok &= check("cp_technical" in lit(), "the technical door is lit on the way", lit())
    b.shot("region8-engineer")
    wait(0.4)
    b.teleport(F["ladderX"], D12)
    b.hold("up", 3.0)
    s = b.state()
    ok &= check(s["y"] == F["roofY"] and s["mode"] == "play", "the chain is off: up the ladder to the roof", s)
    # The old lady, before the horn: a block; a jump clears her sunbed; her mojito.
    L = b.eval(f"{T}.lady")
    b.teleport(L["x"] + 130, D12)
    wait(0.5)
    b.hold("left", 1.2)
    s = b.state()
    ok &= check(abs(s["x"] - (L["x"] + L["half"] + 7)) < 3, "the old lady's sunbed is across the walk", s["x"] - L["x"])
    ok &= check(person(b, "riv_sundeck")["on"], "the security officer is at the loungers", person(b, "riv_sundeck"))
    b.shot("region8-lady")
    wait(2.4)
    b.eval("window.__ship.lockedUntil = 0")
    b.hold(["left", "space"], 1.0)
    wait(0.3)
    s = b.state()
    ok &= check(s["x"] < L["x"] - L["half"] and s["mode"] == "play", "a jump takes her over it", s["x"] - L["x"])
    b.eval(f"{W}.carryBox.drop()")
    go(b, 11, 155.38)
    b.teleport(b.eval(f"{W}.things.find(t => t.id === 'src_cocktail').x") - 4, D11)
    wait(0.3)
    b.tap("e")
    wait(0.3)
    ok &= check(carrying(b) == "cocktail", "a mojito from Topsiders' bar", carrying(b))
    s = climb(b, "stairs-midship-11-12", 3.4)
    ok &= check(s["y"] == D12 and carrying(b) == "cocktail", "up the midship flight with it: the paint is dry", s)
    b.teleport(L["x"] - 120, D12)
    b.hold(["right", "space"], 1.2)
    s = b.state()
    ok &= check(s["x"] < L["x"] - L["half"], "with a tray a hop does not clear the sunbed", s["x"] - L["x"])
    b.tap("e")
    ok &= check(wait_flag(b, "lady", 12), "E with the mojito: she drinks it and dozes off", flags(b)[-3:])
    wait(0.6)
    b.hold("left", 0.7)
    took = [t for t in save_list(b, "collected") if "lady" in t]
    ok &= check(len(took) == 2, "two tangerines out of her bag", took)
    b.shot("region8-lady-doze")
    # The court: a ball off the rim; her own shot.
    bl = b.eval(f"{T}.balls[0]")
    # (14a, whatever she carries: facing the hoop the ball comes off, stiff as a skittle onto her back, and lying so.)
    b.teleport(bl["x"] + 80, D12)
    b.eval("window.__ship.player.setFlipX(true)")
    got = scared(b, "Ouch", 9.0)
    ok &= check(got, "in the way of a ball off the hoop: bonked")
    GK = "(window.__ship.worldLayer.list.find(o => o.anims?.currentAnim?.key.startsWith('gags-ball')))?.anims.currentAnim.key"
    first = b.eval(GK)
    wait_js(b, GK + " === 'gags-ball-back-lie'", 2.0)
    ok &= check(first and first.startswith("gags-ball-back") and b.eval(GK) == "gags-ball-back-lie",
                "a ball in her face: she topples onto her back, and lies there dazed (14a)", (first, b.eval(GK)))
    wait_js(b, "window.__ship.mode === 'play'", 5.0)
    wait(0.5)
    c = b.eval(f"{T}.court")
    b.teleport(c["ballX"] - 6, D12)
    wait(0.3)
    b.tap("e")
    wait(1.0)
    b.shot("region8-court")
    wait(3.2)
    ok &= check("sec_court" in save_list(b, "seen") and b.state()["mode"] == "play", "E at the ball by the court: she shoots", save_list(b, "seen")[-3:])
    # The funnel's stairway: no climbing in a gust. (Its gulls held off meanwhile: by the clock's phase one could
    # dive at her on the stairway; their own check is below.)
    b.eval(f"{W}.story.funnelWind.nextAt = 1e12")
    fn = b.eval(f"{W}.data.funnel")
    G = f"{W}.story.funnelGusts.phase({NOW})"
    b.teleport(fn["foot"][0], fn["foot"][1])
    wait(0.4)
    wait_js(b, G + " === 'calm'", 8)
    b.key("up", True)
    wait_js(b, G + " === 'blow'", 8)
    wait(0.3)
    at = b.state()
    clip = b.eval("window.__ship.player.anims.currentAnim?.key")
    wait(0.6)
    held = b.state()
    b.shot("region8-cling")
    ok &= check(clip and clip.startswith("her-cling-up") and held["y"] == at["y"] and held["x"] == at["x"],
                "climbing into a gust on the stairway: she holds on to the rail and does not move", (clip, at, held))
    wait_js(b, G + " === 'calm'", 8)
    wait_js(b, "!window.__ship.stairCling", 3)
    hold_until(b, [], lambda s: s["y"] < held["y"], 1.5)
    ok &= check(b.state()["y"] < held["y"], "and once it drops, she climbs on", (held, b.state()))
    b.key("up", False)
    # (The gulls: one dives straight at her from its flight; standing still on the stairway, she is
    # swooped.)
    pocket = b.state()["tangerines"]
    b.eval("window.__ship.save.tangerines = 0; window.__ship.refreshHud()")   # (with one on her the gull takes it instead: 1.2a)
    b.eval(f"(w => {{ w.def.swoop = 5; w.nextAt = 0; }})({W}.story.funnelWind)")
    end = now() + 30
    got = False
    while now() < end and not got:
        ph = b.eval(G)
        st = b.eval(f"{W}.story.funnelWind.state")
        b.key("up", ph == "calm" and st == "circle" and b.state()["y"] > fn["shoulder"][1] - 120)
        got = "Ow-ow-ow" in alert(b)
        wait(0.05)
    b.key("up", False)
    ok &= check(got, "standing on the stairway, a gull dives at her: \"Ow-ow-ow!\"", b.state())
    # (Gag 21: on her bottom, a step a bump, down to the foot; then her checkpoint.)
    wait(0.2)
    ok &= check(b.eval("(s => s.mode === 'scripted' && !s.player.visible)(window.__ship)"), "she sits down on the step: her gag, not her own sprite")
    ok &= check(wait_js(b, f"window.__ship.player.x === {fn['foot'][0]} && window.__ship.player.y === {fn['foot'][1]}", 15),
                "she bumps down the stairway on her bottom to its foot", b.state())
    b.shot("region8-bumped")
    wait_js(b, "window.__ship.mode === 'play'", 4)
    b.eval(f"window.__ship.save.tangerines = {pocket}; window.__ship.refreshHud()")
    wait(0.6)
    s = b.state()
    ok &= check(s["y"] == D12 and abs(s["x"] - exact_x(165)) < 30, "she comes back at the technical door", s)
    b.eval(f"(w => {{ w.def.swoop = 1000; w.nextAt = Infinity; }})({W}.story.funnelWind)")
    b.teleport(fn["foot"][0], fn["foot"][1])
    wait(0.4)
    end = now() + 45
    # (Until she has stepped off its top, as in `golden`.)
    while now() < end and not ((s := b.state())["y"] <= fn["y"] and s["mode"] == "play"):
        b.key("up", b.eval(G) == "calm")
        wait(0.05)
    b.key("up", False)
    s = b.state()
    ok &= check(s["y"] == fn["y"] and s["mode"] == "play", "climbing in the lulls she reaches the funnel's top", s)
    b.hold("right", 0.9)
    ok &= check("cp_funnel" in lit(), "the engineer's locker is lit", lit())
    ok &= check(person(b, "npc_engineer_cord")["on"], "he is up there, by the cord", person(b, "npc_engineer_cord"))
    # The horn, and what it sets off.
    b.teleport(F["hornX"] - 4, fn["y"])
    wait(0.4)
    b.shot("region8-horn-before")
    b.tap("e")
    wait(0.5)
    ok &= check(b.state()["mode"] == "scripted", "E at the cord: she pulls it", b.state())
    wait(3.6)
    b.shot("region8-sundeck")
    wait(5.2)
    b.shot("region8-bow")
    ok &= check(wait_flag(b, "horn", 16), "the horn has sounded; the view comes back to her", flags(b)[-3:])
    cam = b.eval("(c => [c.worldView.centerX, c.worldView.centerY])(window.__ship.cameras.main)")
    ok &= check(abs(cam[0] - b.state()["x"]) < 60, "the camera is on her again", (cam, b.state()))
    ok &= check(not person(b, "npc_oldlady")["on"] and not person(b, "riv_sundeck")["on"], "the old lady and the security officer are gone",
                (person(b, "npc_oldlady"), person(b, "riv_sundeck")))
    gone = b.eval(f"{W}.things.filter(t => t.id.startsWith('gull_bow')).every(t => !{W}.shown(t))")
    ok &= check(gone, "the gulls have left the bow")
    b.tap("e")
    wait(1.6)
    ok &= check(b.state()["mode"] == "play" and "horn" in flags(b), "the cord again: a toot, no more", b.state())
    # His book; the telescope.
    e = person(b, "npc_engineer_read")
    ok &= check(e["on"], "the engineer is on his break, reading", e)
    b.teleport(e["x"] - 30, fn["y"])
    wait(0.4)
    b.tap("e")
    wait(2.6)
    ok &= check(b.eval("window.__ship.save.books['9']") == "held", "E: he lends her his book, the ninth", b.eval("window.__ship.save.books"))
    b.teleport(F["telescopeX"] - 4, fn["y"])
    wait(0.3)
    b.tap("e")
    wait(2.8)
    b.shot("region8-telescope")
    cam = b.eval("(c => [c.worldView.centerX, c.worldView.centerY])(window.__ship.cameras.main)")
    ok &= check(abs(cam[0] - F["look"]["x"]) < 40 and abs(cam[1] - F["look"]["y"]) < 60, "E at the telescope: deck 8's first balcony, and the frame on its wall", cam)
    wait(3.2)
    ok &= check(b.state()["mode"] == "play" and "sec_telescope" in save_list(b, "seen"), "and back", b.state())
    # On the sun deck: the card where he dropped it, the parasol and the book at the empty sunbed.
    ok &= check(take_card(b, "off"), "the Officer's card lies on the sun deck")
    b.teleport(L["x"] + 100, D12)
    s = hold_until(b, "left", lambda s: s["x"] < L["x"] + 40, 3)
    b.tap("e")
    wait(0.3)
    ok &= check("parasol" in save_list(b, "verbs"), "her parasol, left leaning on the sunbed", save_list(b, "verbs"))
    b.shot("region8-parasol")
    b.eval("window.__ship.lockedUntil = 0")
    s = hold_until(b, "left", lambda s: s["x"] < L["x"] - 14, 3)
    ok &= check(s["x"] < L["x"], "the sunbed is no block now", s["x"] - L["x"])
    b.tap("e")
    wait(0.3)
    ok &= check(b.eval("window.__ship.save.books['8']") == "held", "and her book, the eighth, on it", b.eval("window.__ship.save.books"))
    # The glide: over an atrium walk's rail on deck 10, down to the atrium's floor on deck 5.
    b.eval("window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    go(b, 10, 92)
    wait(0.6)
    b.key("space", True)
    wait(1.2)
    b.key("space", False)
    wait(0.3)
    ok &= check(b.state()["y"] == D10, "a jump with the key held leaves her on the walk", b.state())
    b.key("down", True)
    wait(0.12)
    b.key("space", True)
    wait(0.1)
    b.key("down", False)
    wait_js(b, "window.__ship.player.body.velocity.y > 0", 2)
    wait(0.1)
    ok &= check(not b.eval("window.__ship.gliding"), "over the rail with jump held on: the parasol stays shut", b.state())
    b.key("space", False)
    wait(0.1)
    b.key("space", True)
    wait(1.0)
    b.shot("region8-glide")
    s = b.state()
    ok &= check(s["y"] > D10 + 30 and b.eval("window.__ship.gliding"), "jump pressed again in the air and held: the parasol opens", s)
    end = now() + 20
    while now() < end and b.state()["y"] < D5:
        wait(0.1)
    b.key("space", False)
    wait(0.4)
    s = b.state()
    ok &= check(s["y"] == D5 and s["mode"] == "play", "and she floats down past five decks to the atrium's floor", s)
    b.shot("region8-atrium-floor")
    ok &= check(not b.errors, "no errors", b.errors[:3])
    return ok


def cake_for_the_planner(b):
    """Region 9's errand (the golden path's): the wedding cake from the pastry chef in Cagney's to
    the planner at Champs' door. (The steady walk past the court is `region9`'s.)"""
    pl = person(b, "npc_planner")
    b.teleport(pl["x"] + 80, D12)
    wait(0.5)
    if "cake_asked" not in flags(b):
        return False
    src = b.eval("window.__ship.world.things.find(t => t.id === 'src_cake').x")
    b.teleport(src + 8, D12)
    wait(0.3)
    b.tap("e")
    wait(0.3)
    if carrying(b) != "cake":
        return False
    b.teleport(pl["x"] + 34, D12)
    wait(0.4)
    b.tap("e")
    return wait_flag(b, "wedding", 30)


def enter_region9(b):
    """A save at region 9's door: region 8 done (the engineer's coffee, the horn, the Officer's card,
    the parasol), she stands in Champs, aft of the wedding planner."""
    enter_region8(b)
    b.eval("(P => { ['engineer', 'horn', 'lady'].forEach(f => P.setFlag(f)); P.open('cards', 'off'); P.learn('parasol'); })(window.__ship.progress)")
    wait(0.8)
    b.eval("window.__ship.world.refresh(); window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    b.teleport(exact_x(95), D12)
    wait(0.4)
    b.eval("window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")


def scenario_region8__tshirt(b):
    """His navy t-shirt (§4 2.1, thing 13; deck 12): not on the sun deck's lounger before the table scene; after it,
    folded on the first of the two new loungers (the user's placing: both 2 px down, the second 4 px aft), and E takes
    it, a thing of his."""
    S = "window.__ship"
    shirt = f"{S}.world.things.find(t => t.id === 'keep_tshirt')"
    loungers = ("JSON.stringify((() => { const out = []; const walk = l => { for (const o of l) { if (o.list) walk(o.list);"
                " if (o.frame?.name === 'sunlounger-long-w20') { const r = o.getBounds(); out.push([Math.round(r.x), Math.round(r.bottom)]); } } };"
                f" walk({S}.children.list); return out.sort((a, b) => a[0] - b[0]); }})())")
    b.open("?reset&play&at=deck12")
    wait(0.4)
    ok = check(not b.eval(f"!!({shirt}?.pick?.visible)"), "before the table scene: no shirt on the lounger")
    # (Deck 12's only: deck 10's first balcony has one too since thing 14.)
    got = [g for g in json.loads(b.eval(loungers)) if abs(g[1] - D12) < 8]
    ok &= check(got == [[exact_x(111.0) - 40, D12 + 2], [exact_x(112.8) - 36, D12 + 2]],
                "the two new loungers where the user put them", got)
    b.open("?reset&play&at=deck12&did=table")
    wait(0.4)
    pick = b.eval(f"[{shirt}.pick.visible, {shirt}.pick.x, {shirt}.pick.y]")
    ok &= check(pick == [True, exact_x(111.25), D12 - 10], "after it: folded on the first lounger's seat", pick)
    b.close_up("tshirt-lounger", exact_x(111.9), D12 - 20, 160, 60, 4)
    b.teleport(exact_x(111.25), D12)
    wait(0.3)
    b.tap("e")
    wait(0.4)
    ok &= check("keep:him:tshirt" in b.eval(f"{S}.save.keeps"), "E takes it, his", b.eval(f"{S}.save.keeps"))
    return ok


def scenario_region8__handheld(b):
    """His handheld (§4 2.1, thing 15; deck 12, Champs): not on the sofa before the table scene; after it, on the left
    seat cushion of the sofa in the aft high table's place (the user's), and E takes it, a thing of his. Champs as the
    user set it, 2026-11-21: the bigger bar with its right end where the old one's was, the sofa under the aft windows,
    the two seated fans at the bar's two ends."""
    S = "window.__ship"
    item = f"{S}.world.things.find(t => t.id === 'keep_handheld')"
    pieces = ("JSON.stringify((() => { const out = {}; const walk = l => { for (const o of l) { if (o.list) walk(o.list);"
              " const f = o.frame?.name; if (typeof f === 'string' && /^(champs-bar-long|sofa-champs)-/.test(f) && o.visible) {"
              " const r = o.getBounds(); out[f] = [Math.round(r.x), Math.round(r.right), Math.round(r.bottom)]; } } };"
              f" walk({S}.children.list); return out; }})())")
    b.open("?reset&play&at=deck12")
    wait(0.4)
    ok = check(not b.eval(f"!!({item}?.pick?.visible)"), "before the table scene: no handheld on the sofa")
    got = json.loads(b.eval(pieces))
    ok &= check(got.get("champs-bar-long-w20", [0, 0])[1] == 4956 and got.get("sofa-champs-w20", [0])[0] == 5156,
                "the bigger bar's right end where the old one's was; the sofa under the aft windows", got)
    fans = json.loads(b.eval(f"JSON.stringify(['amb_champs_c', 'amb_champs_d'].map(id => {{ const p = {S}.world.people.byId[id]; return p ? [Math.round(p.sprite.x), p.sprite.flipX] : null; }}))"))
    ok &= check(fans == [[4972, True], [4832, False]] and not b.eval(f"!!{S}.world.people.byId.amb_champs_a"),
                "the seated fans at the bar's two ends, facing it; the fan in stripes gone", fans)
    b.open("?reset&play&at=deck12&did=table")
    wait(0.4)
    pick = b.eval(f"[{item}.pick.visible, {item}.pick.x, {item}.pick.y]")
    ok &= check(pick == [True, exact_x(97.9167), D12 - 18], "after it: on the sofa's left seat cushion", pick)
    b.close_up("handheld-sofa", exact_x(98.3), D12 - 24, 120, 60, 5)
    b.teleport(exact_x(97.9167), D12)
    wait(0.3)
    b.tap("e")
    wait(0.4)
    ok &= check("keep:him:handheld" in b.eval(f"{S}.save.keeps"), "E takes it, his", b.eval(f"{S}.save.keeps"))
    return ok


def scenario_region9(b):
    """Region 9 (docs/build-plan.md, step 9): the wedding at Champs' door, the cake from Cagney's
    (it sways and goes over; carried steadily it arrives), the party into the chapel and the
    ceremony there, the Spinnaker's bar and piano, the kids' pool's slide, the spa's steam, the
    officers' corridors, the bridge's beat with the alarm and the hatch, the captain's door, the
    kids' clubs' ball pit and fort, and the Library's odd book that opens the nook."""
    enter_region9(b)
    ok = True
    S, W = "window.__ship", "window.__ship.world"
    B = b.eval(f"{W}.data.bow")
    seen = lambda: save_list(b, "seen")
    got = lambda tid: any(t == tid or t.startswith(tid + "#") for t in save_list(b, "collected"))
    # The wedding: the door is roped off, the party beyond it; no cake to take before she is asked.
    src = b.eval(f"{W}.things.find(t => t.id === 'src_cake').x")
    b.teleport(src + 8, D12)
    wait(0.3)
    b.tap("e")
    wait(0.3)
    ok &= check(not carrying(b), "the cake is not hers to take before the planner has asked", carrying(b))
    pl = person(b, "npc_planner")
    # (From the lobby's side: at Champs' side the planner is in reach, and E is hers.)
    b.teleport(exact_x(82) + 60, D12)
    wait(0.3)
    b.hold("left", 0.6)
    s = b.state()
    ok &= check(s["x"] > exact_x(82) and not door_open(b, "part-door-12-82"), "Champs' door to the forward lobby: shut, the wedding's rope across it", s["x"] - exact_x(82))
    ok &= check(person(b, "amb_wed_bride")["on"] and not person(b, "amb_cer_bride")["on"], "the party waits in the lobby", person(b, "amb_wed_bride"))
    b.teleport(pl["x"] + 110, D12)
    wait(0.5)
    ok &= check("cake_asked" in flags(b) and b.eval(f"{W}.people.byId.npc_planner.bubbleItems[0].visible"), "near the planner: her bubble, a cake", flags(b)[-3:])
    b.teleport(pl["x"] + 34, D12)
    wait(0.3)
    b.tap("e")
    wait(0.5)
    ok &= check("wedding" not in flags(b) and b.state()["mode"] == "play", "E without it: nothing yet")
    b.shot("region9-planner")
    # The cake: every start and stop sets it swaying; too much and it goes over.
    b.teleport(src + 8, D12)
    wait(0.3)
    b.tap("e")
    wait(0.3)
    ok &= check(carrying(b) == "cake", "E at the cake on its table: in her hands", carrying(b))
    b.eval("window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    sigh = False
    for _ in range(5):
        b.hold("right", 0.2)
        wait(0.16)
    end = now() + 2.5
    while now() < end and not sigh:
        sigh = b.eval(f"{W}.people.byId.npc_pastrychef.sprite.anims.currentAnim?.key") == "people-pastrychef-sigh"
        wait(0.05)
    ok &= check(not carrying(b), "starts and stops in a row: it goes over", (carrying(b), b.eval(f"{W}.carryBox.wobble")))
    ok &= check(sigh, "the pastry chef sighs", b.eval(f"{W}.people.byId.npc_pastrychef.sprite.anims.currentAnim?.key"))
    wait(1.8)
    # Carried steadily it arrives: one go to the court, a wait while it settles, on to the planner.
    b.teleport(src + 8, D12)
    wait(0.3)
    b.tap("e")
    wait(0.3)
    b.key("left", True)
    wait(0.3)
    w1 = b.eval(f"{W}.carryBox.wobble")
    b.shot("region9-cake")
    s = hold_until(b, "left", lambda s: s["x"] < exact_x(162), 6)
    w2 = b.eval(f"{W}.carryBox.wobble")
    ok &= check(carrying(b) == "cake" and 0.1 < w1 < 0.5, "setting off sets it swaying", w1)
    ok &= check(carrying(b) == "cake" and w2 < w1, "a steady walk to the court settles it", (w1, w2))
    wait(1.2)
    b.teleport(pl["x"] + 200, D12)
    wait(0.3)
    s = hold_until(b, "left", lambda s: s["x"] < pl["x"] + 36, 6)
    ok &= check(carrying(b) == "cake", "and on through Champs to the planner", (carrying(b), b.eval(f"{W}.carryBox.wobble")))
    wait(0.3)
    b.tap("e")
    wait(3.5)
    b.shot("region9-wedding")
    ok &= check(wait_flag(b, "wedding", 30), "E with the cake: the party files into the chapel", flags(b)[-3:])
    ok &= check(not person(b, "amb_wed_bride")["on"] and not person(b, "npc_planner")["on"], "the lobby is clear")
    ok &= check(use_door(b, 12, 82, 1), "and Champs' door opens")
    b.hold("left", 1.0)
    ok &= check(9 in save_list(b, "regions"), "region 9: deck 12's forward lobby", b.state())
    # The chapel: the ceremony, the first time she looks in; then a frame on its wall.
    cp = b.eval(f"{S}.checkpoints.find(c => c.id === 'cp_chapel').x")
    b.teleport(cp + 40, D12)
    hold_until(b, "left", lambda s: s["x"] < cp - 20, 3)
    ok &= check("cp_chapel" in save_list(b, "activated"), "the chapel lobby's crew door: a checkpoint")
    b.teleport(B["wedding"]["chapelX"], D12)
    wait(0.3)
    b.tap("e")
    wait(2.6)
    ok &= check(route(b) == "chapel" and person(b, "amb_cer_bride")["on"], "E at the chapel's door: the couple at the altar, the guests", route(b))
    b.shot("region9-ceremony")
    ok &= check(wait_flag(b, "ceremony", 12), "the ceremony: a kiss", flags(b)[-3:])
    ok &= check(b.eval(f"{W}.things.find(t => t.id === 'slot_chapel').items[0].visible"), "and a frame on the chapel's wall that was not there")
    b.tap("e")
    wait(0.9)
    ok &= check(route(b) == "inside", "out again", route(b))
    # The Spinnaker: two tangerines on the bar, a few notes on the piano.
    b.teleport(exact_x(57), D12)
    hold_until(b, "left", lambda s: s["x"] < exact_x(54.8), 4)
    ok &= check(got("tan_12_spinnaker"), "the Spinnaker's bar: its tangerines", save_list(b, "collected")[-3:])
    b.teleport(B["piano"]["x"] + 5, D12)
    wait(0.3)
    b.tap("e")
    wait(0.9)
    ok &= check(b.state()["mode"] == "scripted" and b.eval(f"{S}.player.anims.currentAnim?.key") == "her-keys", "E at the grand piano: she plays", b.eval(f"{S}.player.anims.currentAnim?.key"))
    b.shot("region9-piano")
    wait(2.4)
    ok &= check("sec_piano" in seen() and b.state()["mode"] == "play", "a few notes, and back")
    # The kids' pool: up the slide's ladder, down its chute, into the water.
    b.teleport(B["slide"]["ladderX"], D12)
    wait(0.3)
    b.tap("e")
    wait(0.9)
    b.shot("region9-slide")
    s = hold_until(b, [], lambda s: s["mode"] == "swim", 5)
    ok &= check(s["mode"] == "swim" and "sec_slide" in seen(), "E at the slide: down it and into the kids' pool", s)
    # The spa (deck 11): open now; the steam up from the sauna's coals (the user, 2026-11-22: no longer out of its door).
    b.teleport(exact_x(74) + 16, D11)
    b.tap("e")
    wait(0.2)
    ok &= check(door_open(b, "spa-door"), "the spa's door opens from the lobby now")
    st = B["steam"]
    b.teleport(st["x"], D11)
    ok &= check(scared(b, "Pfff", 7.0), "by the sauna's stove as its steam rises: fogged")
    # (Her gag, 17: out of the burst with her hair a huge puff, she fans herself, swoons and sits;
    # then her checkpoint.)
    GAG = "window.__ship.world.movers.find(m => m.constructor.name === 'Steam').pic"
    seen_gag = set()
    end = now() + 8
    while now() < end and b.state()["mode"] != "play":
        seen_gag.add(b.eval(f"{GAG}?.anims.currentAnim?.key ?? null"))
        wait(0.1)
    ok &= check({"gags-steam-fan", "gags-steam-swoon"} <= seen_gag and b.state()["mode"] == "play",
                "her hair a puff, she fans herself and swoons; then she is back", sorted(k for k in seen_gag if k))
    b.eval("window.__ship.lockedUntil = 0")
    rec = person(b, "amb_spa_reception")
    b.teleport(rec["x"] + 60, D11)
    wait(0.6)
    ok &= check(b.eval(f"{W}.people.byId.amb_spa_reception.sprite.anims.currentAnim?.key") == "people-spa_reception-bow", "the spa's receptionist bows")
    hold_until(b, "left", lambda s: s["x"] < rec["x"] - 34, 3)
    ok &= check(got("tan_11_spa"), "the tangerine on her desk", save_list(b, "collected")[-3:])
    b.shot("region9-spa")
    # Deck 10: the officers' corridor behind its gold door, an officer walking it, the bridge.
    go(b, 10, 78)
    ok &= check(use_door(b, 10, 74, 1), "the Officer's card opens the officers' corridor on deck 10")
    ok &= check(person(b, "amb_officer_10")["on"], "an officer walks it", person(b, "amb_officer_10"))
    cp = b.eval(f"{S}.checkpoints.find(c => c.id === 'cp_officer').x")
    b.teleport(cp + 40, D10)
    hold_until(b, "left", lambda s: s["x"] < cp - 20, 3)
    ok &= check("cp_officer" in save_list(b, "activated"), "an officer's cabin door: a checkpoint")
    ok &= check(person(b, "riv_bridge")["on"], "on the bridge the security officer is creeping up on him", person(b, "riv_bridge"))
    b.teleport(exact_x(40) + 16, D10)
    b.tap("e")
    wait(0.2)
    ok &= check(door_open(b, "bridge-door"), "the bridge's door")
    b.hold("left", 1.2)
    b.shot("region9-bridge")
    b.hold("left", 2.0)
    wait(1.6)
    b.shot("region9-alarm")
    ok &= check(wait_flag(b, "bb6", 20), "near-catch 6: his net comes down on the alarm panel", flags(b)[-3:])
    ok &= check("alarm" in flags(b) and b.eval(f"{W}.gates.find(g => g.needs === 'alarm').tiles.every(t => t.alpha === 1)"), "the alarm; the hatch's ladder is down")
    ok &= check(person(b, "riv_bridge_sat")["on"] and not person(b, "riv_bridge")["on"], "the security officer sits on the floor, done for the day")
    b.teleport(exact_x(37.5) + 4, D10)
    wait(0.3)
    b.tap("e")
    wait(0.4)
    ok &= check(b.eval(f"{S}.save.books['10']") == "held", "the captain's book on the chart table: the tenth", b.eval(f"{S}.save.books"))
    b.eval("window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    # Deck 9: the officers' corridor, the captain's door.
    go(b, 9, 78)
    ok &= check(use_door(b, 9, 74, 1), "the Officer's card opens deck 9's officers' corridor")
    b.teleport(B["captain"]["x"] + 6, D9)
    wait(0.3)
    b.tap("e")
    wait(0.7)
    ok &= check(b.state()["mode"] == "scripted" and b.eval(f"{S}.player.anims.currentAnim?.key") == "her-knock", "E at the captain's door: a polite knock", b.eval(f"{S}.player.anims.currentAnim?.key"))
    b.shot("region9-knock")
    wait(3.6)
    ok &= check("sec_captain" in seen() and b.state()["mode"] == "play", "nobody answers")
    # The fourteenth book, on the console table at the corridor's end (§4 2.1, 20; the user, 2026-11-21).
    bk = b.eval(f"(t => t && [t.x, t.y])({S}.world.things.find(t => t.id === 'book_14'))")
    b.teleport(bk[0], bk[1])
    wait(0.3)
    b.tap("e")
    wait_js(b, f"{S}.save.books['14'] === 'held'", 4)
    ok &= check(b.eval(f"{S}.save.books['14']") == "held", "the fourteenth book, on the console table at the corridor's end", b.eval(f"{S}.save.books"))
    # Deck 7: the kids' clubs behind the lobby's gold door: the ball pit, the fort.
    go(b, 7, 78)
    ok &= check(use_door(b, 7, 74, 1), "the Officer's card opens the kids' clubs")
    pit = B["pit"]
    b.teleport(pit["x1"] + 40, D7)
    wait(0.3)
    b.hold("left", 0.5)
    s = b.state()
    ok &= check(s["x"] > pit["x1"] - 2, "the ball pit's padded wall stops her feet", s["x"] - pit["x1"])
    b.key("left", True)
    b.tap("space", 0.25)
    wait(0.7)
    x0 = b.state()["x"]
    wait(0.5)
    x1 = b.state()["x"]
    b.shot("region9-ballpit")
    ok &= check(b.eval(f"{S}.wading") and 25 < x0 - x1 < 60, "over it with a hop: she wades, at half her speed", (b.eval(f"{S}.wading"), x0 - x1))
    b.key("left", False)
    # (The hop may carry her over it: back to it through the balls.)
    wait(0.2)
    s = b.state()
    hold_until(b, "right" if s["x"] < pit["tanX"] else "left", lambda s: abs(s["x"] - pit["tanX"]) < 6, 5)
    ok &= check(got("tan_7_ballpit"), "one of the balls is a tangerine", save_list(b, "collected")[-3:])
    hold_until(b, "left", lambda s: s["x"] < pit["x0"] + 16, 5)
    b.key("left", True)
    b.tap("space", 0.25)
    wait(0.8)
    b.key("left", False)
    s = b.state()
    ok &= check(s["x"] < pit["x0"] and not b.eval(f"{S}.wading"), "and out over the far wall", s["x"] - pit["x0"])
    fort = b.eval(f"(t => ({{ x0: t.x0, x1: t.x1 }}))({W}.lows.find(t => t.id === 'haz_fort_7'))")
    b.teleport(fort["x1"] + 60, D7)
    wait(0.3)
    b.hold("left", 0.8)
    s = b.state()
    ok &= check(s["x"] > fort["x1"] - 4, "the pillow fort across Splash Academy stops her", s["x"] - fort["x1"])
    s = hold_until(b, ["down", "left"], lambda s: s["x"] < fort["x0"] - 24, 8)
    b.shot("region9-fort")
    ok &= check(s["x"] < fort["x0"], "on hands and knees she is through it", s["x"] - fort["x0"])
    b.teleport(exact_x(41.2) + 30, D7)
    hold_until(b, "left", lambda s: s["x"] < exact_x(41.2) - 10, 3)
    ok &= check(got("tan_7_splash"), "a tangerine on the kids' table", save_list(b, "collected")[-3:])
    ok &= check(person(b, "amb_counsellor")["on"], "the counsellor cheers the toddlers on")
    # The Library's odd book: stuck while there are gaps on the shelf; with all fourteen back, the nook.
    N = B["nook"]
    b.teleport(N["x"] + 16, D6)
    wait(0.4)
    b.tap("e")
    wait(0.25)
    pulled = b.state()["mode"] == "scripted"
    wait(1.6)
    ok &= check(pulled and "nook" not in flags(b) and b.state()["mode"] == "play", "the odd book on the Library's bookcase: she pulls, it is stuck", (pulled, flags(b)[-2:]))
    b.eval("(s => { for (let n = 1; n <= 14; n++) s.save.books[n] = 'returned'; s.world.library.refresh(); s.progress.setFlag('books_all'); })(window.__ship)")
    wait(0.4)
    b.tap("e")
    b.shot("region9-oddbook")
    ok &= check(wait_flag(b, "nook", 8), "with all fourteen books back: it tips, and the bookcase slides aside", flags(b)[-2:])
    case = b.eval(f"(c => c && c.slide.x - c.home)({S}.world.story.cases)")
    ok &= check(case is not None and case > 50, "behind the other bookcase, the entrance open where it stood", case)
    b.teleport(N["x"], D6)
    wait(0.3)
    b.tap("e")
    wait(1.0)
    b.shot("region9-nook")
    ok &= check(route(b) == "nook", "E in the doorway: the reading nook", route(b))
    ok &= check(b.eval(f"!!{W}.things.find(t => t.id === 'slot_nook')"), "a frame on its wall")
    # Its armchair: all fourteen to read again (the user, 2026-11-22).
    chair = b.eval(f"(t => t && [t.x, t.y])({W}.things.find(t => t.id === 'sec_chair_nook'))")
    b.teleport(chair[0], chair[1], "nook")
    wait(0.3)
    b.tap("e")
    wait_js(b, f"!!{W}.library.choosing", 4)
    row = b.eval(f"{W}.library.choosing && {W}.library.choosing.books.length")
    ok &= check(row == 14, "in its armchair, all fourteen books in the row", row)
    b.tap("escape")
    wait(1.5)
    ok &= check(not b.errors, "no errors", b.errors[:3])
    return ok


def scenario_region9__massage(b):
    """The spa's massage (deck 11; the user, 2026-11-22; src/world/spa.js). The masseur works on his guest round and round.
    E at her table: he goes behind it, she goes to the sauna's bench and sits there; Bumbusik lies down, gets her round and,
    the first time, Bumbot's massage gun (6); the guest comes back and lies down, and his round goes on. E at the empty
    table: he comes over, the guest stays lying on hers; no second gun."""
    S = "window.__ship"
    W = f"{S}.world"
    M, G, ST = f"{W}.people.byId.amb_masseur", f"{W}.people.byId.amb_massage_guest", f"{W}.story.spaState"
    gun = f"{S}.save.keeps.filter(k => k === 'keep:cat:massage').length"
    b.open("?reset&play&at=spa")
    wait(0.4)
    tables = b.eval(f"{W}.story.spaTables().map(t => t.x)")
    home = b.eval(f"{W}.story.spaTable().x")
    ok = check(len(tables) == 2, "two massage tables", tables)
    ok &= check(wait_js(b, f"{M}.sprite.anims.currentAnim?.key === 'people-masseur-mf-knead'", 20),
                "he kneads his guest's back, behind her table", b.eval(f"{M}.sprite.anims.currentAnim?.key"))
    ok &= check(b.eval(f"{gun}") == 0, "no massage gun in the gym any more: none yet")
    # At the guest's table.
    b.teleport(home - 30, floor_y(11) - 32)
    wait(0.3)
    b.tap("e")
    ok &= check(wait_js(b, f"{M}.behind && Math.abs({M}.x - {home}) < 1 && {G}.sprite.anims.currentAnim?.key === 'people-massage_guest-sit'", 20),
                "E: he stands behind her table, she sits on the sauna's bench", (b.eval(f"{M}.x"), b.eval(f"{G}.x")))
    b.shot("region9-massage-sauna")
    ok &= check(wait_js(b, f"{gun} === 1", 90), "her massage, and his massage gun tossed to her", b.eval(f"{S}.save.keeps"))
    ok &= check(wait_js(b, f"!{ST}.busy", 40) and abs(b.eval(f"{G}.x") - home) < 1
                and b.eval(f"{G}.sprite.frame.name === {G}.meta.anims.up[0]"),
                "the guest back on her table, lying", (b.eval(f"{G}.x"), b.eval(f"{ST}.busy")))
    # At the empty table.
    other = [x for x in tables if abs(x - home) > 1][0]
    b.teleport(other - 20, floor_y(11) - 32)
    wait(0.3)
    b.tap("e")
    ok &= check(wait_js(b, f"{M}.behind && Math.abs({M}.x - {other}) < 1", 20), "E at the empty table: he comes behind it",
                b.eval(f"{M}.x"))
    ok &= check(abs(b.eval(f"{G}.x") - home) < 1, "the guest stays lying on hers", b.eval(f"{G}.x"))
    b.shot("region9-massage-other")
    ok &= check(wait_js(b, f"!{ST}.busy", 90) and abs(b.eval(f"{M}.x") - home) < 1, "done: he goes back to her table",
                b.eval(f"{M}.x"))
    ok &= check(b.eval(f"{gun}") == 1, "no second gun")
    return ok


def scenario_region9__pick(b):
    """His guitar pick (§4 2.1, thing 16; deck 12, the Spinnaker Lounge): not on the amp before the table scene; after it,
    on the amp of the new bandstand corner between the cream armchair and the sofa, resting on its wide edge (the user's),
    and E takes it, a thing of his. The lounge as the user set it, 2026-11-21: the corner 2 px down, the piano 8 px
    forward, the two seated guests 2 px down, hers 5 px forward."""
    S = "window.__ship"
    item = f"{S}.world.things.find(t => t.id === 'keep_pick')"
    pieces = ("JSON.stringify((() => { const out = {}; const walk = l => { for (const o of l) { if (o.list) walk(o.list);"
              " const f = o.frame?.name; if (typeof f === 'string' && /^(bandstand-w20|grand-piano-w20|lounge-her|lounge-him)$/.test(f)"
              " && o.visible && Math.abs(o.y - %d) < 30) { const r = o.getBounds(); out[f] = [Math.round(r.x), Math.round(r.bottom)]; } } };"
              f" walk({S}.children.list); return out; }})())") % D12
    b.open("?reset&play&at=deck12")
    wait(0.4)
    ok = check(not b.eval(f"!!({item}?.pick?.visible)"), "before the table scene: no pick on the amp")
    got = json.loads(b.eval(pieces))
    want = {"bandstand-w20": [2777, D12 + 2], "grand-piano-w20": [exact_x(53.8) - 8 - 30, D12], "lounge-her": [2689, D12 + 2],
            "lounge-him": [2965, D12 + 2]}
    ok &= check(all(got.get(k) == v for k, v in want.items()), "the corner, the piano and the two guests where the user put them",
                got)
    b.open("?reset&play&at=deck12&did=table")
    wait(0.4)
    pick = b.eval(f"[{item}.pick.visible, {item}.pick.x, {item}.pick.y]")
    ok &= check(pick == [True, exact_x(47.9375), D12 - 16], "after it: on the amp's top, point up", pick)
    b.close_up("pick-amp", 2790, D12 - 24, 120, 60, 5)
    b.teleport(exact_x(47.9375), D12)
    wait(0.3)
    b.tap("e")
    wait(0.4)
    ok &= check("keep:him:pick" in b.eval(f"{S}.save.keeps"), "E takes it, his", b.eval(f"{S}.save.keeps"))
    return ok


def enter_region10(b):
    """A save at region 10's door: region 9 done (the wedding, the bridge's beat, the alarm), she
    stands on the bridge by the hatch's ladder."""
    enter_region9(b)
    b.eval("(P => { ['cake_asked', 'wedding', 'ceremony', 'bb6', 'alarm'].forEach(f => P.setFlag(f)); })(window.__ship.progress)")
    wait(1.2)
    b.eval("window.__ship.world.refresh(); window.__ship.lockedUntil = 0; window.__ship.alert.setVisible(false)")
    b.teleport(b.eval("window.__ship.world.gates[0].x") + 40, D10)
    wait(0.4)


def out_of_the_hatch(b):
    """Up the bridge's hatch onto the balcony forward of the spa, and the sunset's scene watched
    to its end."""
    b.teleport(b.eval("window.__ship.world.gates[0].x"), D10)
    b.hold("up", 3.4)
    b.hold("left", 0.3)
    if b.state()["y"] != D11:
        return False
    return wait_flag(b, "sunset", 30)


def open_parasol(b):
    """A jump, and jump pressed again in the air as she starts to come down and held: the parasol
    opens and stays open while it is held (the user, 2026-11-19: a jump from the floor held on does
    not open it). The caller lets go of space."""
    b.tap("space", 0.1)
    wait_js(b, "window.__ship.player.body.velocity.y > 0", 2)
    b.key("space", True)


def glide_to_the_bow(b):
    """From the balcony forward of the spa: over its front rail and down under the parasol to the
    mooring deck, the two gulls kept out of her way (`finale` flies into one)."""
    F = b.eval("window.__ship.world.data.finale")
    b.eval("(c => { c.parked = true; c.birds.forEach(g => { g.x = 0; }); })(window.__ship.world.story.crossers)")
    hold_until(b, "left", lambda s: s["x"] < F["balcony"]["x0"] + 10, 5)
    b.key("left", True)
    open_parasol(b)              # over the rail, and jump again in the air: the parasol
    hold_until(b, [], lambda s: s["x"] < exact_x(12) or s["mode"] != "play", 16)
    b.key("left", False)
    hold_until(b, [], lambda s: s["mode"] != "play" or (s["y"] >= D7 - 34 and b.eval("window.__ship.grounded")), 16)
    b.key("space", False)
    wait(0.4)
    return b.state()


def catch_him(b):
    """On the mooring deck: up to a few metres from Bumbot, and then still, until he is in her arms."""
    cat = "window.__ship.world.story.tipCat"
    hold_until(b, "left", lambda s: s["x"] - b.eval(f"{cat}.x") < 4.5 * 48, 8)
    return wait_flag(b, "catch", 30)


def home_with_him(b):
    """The end of the way home: along deck 8 to cabin 8206, in, the scene, the win screen and a
    key; true once the day after has come."""
    H = b.eval("window.__ship.world.data.finale.home")
    b.teleport(exact_x(52), D8)
    wait(0.5)
    hold_until(b, "left", lambda s: s["x"] < H["x0"] + 59 + 3, 10)
    wait(0.3)
    b.tap("e")
    if not wait_js(b, "!!window.__ship.world.story.winItems", 25):
        return False
    wait(2.8)
    b.shot("finale-win")
    b.tap("e")
    return wait_flag(b, "home", 8)


def scenario_finale(b):
    """Region 10 and the end (docs/build-plan.md, step 10): out of the hatch and the sunset; a
    glide into a gull and a jump past the tip, each back to the balcony; a glide made; Bumbot backs
    off, darts past her, and comes when she stands still; the catch; the way home with him in her
    arms (the mooring deck's door, the fort gone, nothing that scares, no hands for anything); the
    cabin, the win screen, the day after."""
    W = "window.__ship.world"
    S = f"{W}.story"
    ok = True
    enter_region10(b)
    F = b.eval(f"{W}.data.finale")
    B, Mo, H = F["balcony"], F["mooring"], F["home"]
    ok &= check(b.eval("window.__ship.dusk") == 0 and not b.eval(f"{S}.tipCat.visible"), "midday on the bridge; nobody at the tip of the bow yet")
    # Out of the hatch: the sky turns, the camera goes to the tip and back.
    b.teleport(b.eval(f"{W}.gates[0].x"), D10)
    b.hold("up", 3.4)
    b.hold("left", 0.3)
    s = b.state()
    ok &= check(s["y"] == D11 and 10 in save_list(b, "regions"), "up the hatch's ladder to the balcony forward of the spa", s)
    ok &= check(wait_js(b, "window.__ship.mode === 'scripted'", 3), "the sunset's scene begins", b.state())
    wait(6.0)
    b.shot("finale-sunset")
    ok &= check(b.eval("window.__ship.dusk") > 0.9, "the sky has turned", b.eval("window.__ship.dusk"))
    ok &= check(abs(b.eval("window.__ship.cameras.main.midPoint.y") - D7) < 80, "the camera is down at the tip of the bow")
    ok &= check(wait_flag(b, "sunset", 20), "and comes back to her", flags(b))
    ok &= check(b.state()["mode"] == "play" and b.eval(f"{S}.tipCat.visible") and abs(b.eval(f"{S}.tipCat.x") - Mo["catX"]) < 3,
                "Bumbot sits at the tip", b.eval(f"[{S}.tipCat.x, {S}.tipCat.visible]"))
    ok &= check(b.eval(f"{S}.crossers.birds.every(g => g.sprite.visible)"), "two gulls cross the air under the balcony")
    b.eval("window.__ship.lockedUntil = 0")

    def fresh_lull():
        wait_js(b, f"({W}.scene.time.now / 1000) % {F['gust']['every']} < 0.4", 6)

    # The wind: in the air, a gust carries her aft.
    wait_js(b, f"{S}.finaleWind.phase({W}.scene.time.now) === 'blow'", 6)
    b.eval("window.__ship.player.body.velocity.y = -330")
    x0 = b.state()["x"]
    wait(0.45)
    ok &= check(b.state()["x"] > x0 + 12, "a gust carries her aft in the air", (x0, b.state()["x"]))
    wait(1.2)
    pocket = b.state()["tangerines"]
    b.eval("window.__ship.save.tangerines = 0; window.__ship.refreshHud()")   # (with one on her the gull takes it instead: 1.2a)
    # A glide into a gull: "Swooped", and back on the balcony.
    b.eval(f"(c => {{ c.parked = true; c.birds[1].x = 0; window.__iv = setInterval(() => {{ c.birds[0].x = window.__ship.player.x; }}, 16); }})({S}.crossers)")
    fresh_lull()
    hold_until(b, "left", lambda s: s["x"] < B["x0"] + 10, 5)
    b.key("left", True)
    open_parasol(b)
    s = hold_until(b, [], lambda s: s["mode"] != "play", 9)
    b.key("left", False)
    b.key("space", False)
    gag = "window.__ship.children.list.some(o => o.texture?.key === 'gags' && o.visible)"
    ok &= check(s["mode"] == "scripted" and alert(b) == "Whoa-whoa-whoa!" and s["y"] > D11 + 100 and b.eval(gag),
                "flown into a gull: the parasol blown inside out, she drops kicking (gag 22)", (s, alert(b)))
    wait(0.5)
    b.shot("finale-gull")
    b.eval(f"window.__ship.save.tangerines = {pocket}; window.__ship.refreshHud()")
    b.eval(f"(c => {{ clearInterval(window.__iv); c.birds[0].x = 0; }})({S}.crossers)")
    wait_js(b, "window.__ship.mode === 'play'", 6)
    wait(0.4)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D11 and abs(s["x"] - B["backX"]) < 4, "and she is back on the balcony", s)
    # Over the rail at the tip: the sea; back on the balcony too.
    b.teleport(Mo["x0"] + 60, D7)
    wait(0.4)
    b.key("left", True)
    for _ in range(8):
        b.tap("space", 0.25)
        wait(0.35)
        if b.state()["mode"] != "play":
            break
    b.key("left", False)
    s = hold_until(b, [], lambda s: s["mode"] != "play", 6)
    ok &= check(s["mode"] == "scripted" and s["x"] < exact_x(0.5), "past the tip: overboard", s)
    wait(4.5)
    s = b.state()
    ok &= check(s["mode"] == "play" and s["y"] == D11 and abs(s["x"] - B["backX"]) < 4, "and back on the balcony", s)
    # (That jump at the tip sent Bumbot off already: back to his place, as if she had not been.)
    b.eval(f"(st => {{ st.tip.spooks = 0; st.tipCat.x = {Mo['catX']}; st.tipCat.setFlipX(true); }})({S})")
    # The glide made.
    fresh_lull()
    s = glide_to_the_bow(b)
    ok &= check(s["mode"] == "play" and s["y"] == D7 and s["x"] < Mo["wallX"], "the parasol carries her down to the mooring deck", s)
    b.shot("finale-landed")
    ok &= check("catch" not in flags(b), "Bumbot is not hers yet")
    # Coming at him, he backs off; cornered at the tip, he darts past her.
    cat = lambda: b.eval(f"Math.round({S}.tipCat.x)")
    hold_until(b, "left", lambda s: b.eval(f"{S}.tip.spooks") >= 1, 12)
    wait(0.6)
    ok &= check(b.eval(f"{S}.tip.spooks") >= 1 and cat() < Mo["catX"] - 20, "she comes at him: he backs off along the deck", (cat(), b.state()))
    hold_until(b, "left", lambda s: cat() > s["x"], 8)
    wait(1.2)
    s = b.state()
    ok &= check(cat() > s["x"] + 100, "cornered at the tip, he darts past her", (cat(), s))
    ok &= check(not alert(b), "and nothing says how he is caught: hers to find out", alert(b))
    b.shot("finale-dart")
    b.eval("window.__ship.lockedUntil = 0")
    # Standing still: he comes; three seconds of it and the catch.
    b.hold("right", 0.25)
    c0 = cat()
    wait(2.2)
    ok &= check(cat() < c0 - 15 and "catch" not in flags(b), "she stands still: he comes, a few steps at a time", (c0, cat()))
    ok &= check(wait_js(b, "window.__ship.mode === 'scripted'", 4), "three seconds of it: the catch's scene")
    wait(2.0)
    b.shot("finale-arms")
    ok &= check(wait_js(b, "window.__ship.holding", 12), "he jumps into her arms")
    b.shot("finale-catch")
    ok &= check(wait_flag(b, "catch", 12), "the catch", flags(b))
    wait(1.6)
    ok &= check(b.state()["mode"] == "play" and b.eval("window.__ship.player.texture.key") == "her-cat", "she stands with Bumbot in her arms", b.state())
    ok &= check(not b.eval(f"{S}.tipCat.visible") and not b.eval(f"{S}.crossers.birds[0].sprite.visible"), "nobody at the tip, no gulls in the air")
    ok &= check(not alert(b), "and nothing says where to", alert(b))
    b.shot("finale-held")
    # The way home: the mooring deck's door, the kids' club with its fort put away; nothing scares.
    b.eval("window.__ship.lockedUntil = 0")
    s = hold_until(b, "right", lambda s: s["x"] > exact_x(27), 16)
    ok &= check(s["x"] > exact_x(27) and s["y"] == D7, "through the mooring deck's door into deck 7", s)
    ok &= check(not b.eval(f"{W}.things.find(t => t.id === 'amb_toddler_blocks').items[0].visible"), "the toddlers have gone to bed")
    s = hold_until(b, "right", lambda s: s["x"] > exact_x(35), 10)
    ok &= check(s["x"] > exact_x(35), "the pillow fort is put away: she walks through where it was", s)
    b.shot("finale-kids")
    v = b.eval("window.__ship.player.body.velocity.x")
    b.key("right", True)
    wait(0.5)
    v = b.eval("window.__ship.player.body.velocity.x")
    b.tap("d")
    wait(0.2)
    ok &= check(90 < v < 125 and not b.state()["lunging"], "a calm walk with him, and no lunge", (v, b.state()))
    b.key("right", False)
    b.hold("down", 0.4)
    ok &= check(not b.eval("window.__ship.crawling"), "no crawling with him in her arms")
    b.eval("window.__ship.scareContact(window.__ship.player.x + 10, 'cart')")
    wait(0.3)
    ok &= check(b.state()["mode"] == "play", "nothing scares her on the way home", b.state())
    # The game closed and opened again on the way home: still evening, he is still in her arms.
    b.open("?play")
    wait(1.2)
    ok &= check(b.eval("window.__ship.holding") and b.eval("window.__ship.dusk") == 1 and b.eval("window.__ship.player.texture.key") == "her-cat",
                "the game opened again on the way home: evening still, Bumbot still in her arms",
                (b.eval("window.__ship.holding"), b.eval("window.__ship.dusk")))
    # Deck 8: those she helped clap her in; the cabin; the win screen; the day after.
    b.teleport(exact_x(52), D8)
    wait(0.6)
    ok &= check(all(person(b, p) and person(b, p)["on"] for p in ("amb_home_steward", "amb_home_manager", "amb_home_engineer", "amb_home_planner")),
                "four of those she helped wait outside her cabin")
    # (Placed by the story, wherever she is: the planner's place is in the chapel, shown only while she is in it.)
    own = ("npc_steward", "npc_stagemanager", "npc_engineer_read", "amb_cer_planner")
    placed = lambda pid: b.eval(f"(p => !!p && !p.gone && !(p.until && {W}.cond(p.until)) && !(p.after && !{W}.cond(p.after)))({W}.people.byId['{pid}'])")
    ok &= check(not any(placed(p) for p in own), "and none of them is at their own place meanwhile", [(p, placed(p)) for p in own])
    hold_until(b, "left", lambda s: s["x"] < exact_x(47.2), 8)
    b.shot("finale-welcome")
    ok &= check(b.eval(f"!!{W}.people.byId['amb_home_manager'].welcoming"), "they clap her in as she comes by")
    hold_until(b, "left", lambda s: s["x"] < H["x0"] + 59 + 3, 8)
    wait(0.3)
    b.tap("e")
    wait(1.2)
    ok &= check(route(b) == "cabin" and b.state()["mode"] == "scripted", "into cabin 8206: the scene", (route(b), b.state()))
    ok &= check(person(b, "npc_husband_home") and person(b, "npc_husband_home")["on"], "her husband is waiting there")
    ok &= check(wait_js(b, f"!!{S}.winItems", 25), "Bumbot curls up on the bed; the win screen")
    wait(2.8)
    b.shot("finale-win")
    ok &= check(not b.eval("window.__ship.holding") and b.eval(f"{S}.bedCat.visible"), "he is on the bed, out of her arms")
    b.tap("e")
    ok &= check(wait_flag(b, "home", 8), "a key: the game goes on", flags(b))
    wait(2.2)
    b.shot("finale-next-day")
    s = b.state()
    # (After the ending the evening goes on, the user, 2026-11-23: the ending's state.)
    ok &= check(s["mode"] == "play" and b.eval("window.__ship.dusk") == 1 and b.eval("window.__ship.player.texture.key") == "her",
                "after the ending: still sunset, she is up, on her own", (s, b.eval("window.__ship.dusk")))
    ok &= check(b.eval(f"{S}.bedCat.visible") and person(b, "npc_husband_home")["on"] and not person(b, "npc_husband")["on"],
                "Bumbot sleeps on the bed; her husband stays on the sofa, his table empty")
    ok &= check(not b.eval(f"{W}.things.find(t => t.id === 'haz_fort_7').items[0].visible"), "the kids' fort still down for the night")
    home = ("amb_home_steward", "amb_home_manager", "amb_home_engineer", "amb_home_planner")
    ok &= check(all(placed(p) for p in own) and not any(placed(p) for p in home),
                "those who clapped her home are back at their own places", [(p, placed(p)) for p in own + home])
    # E by him from the floor: a purr, and the bed seen close (§4 2.4, the user's); on the bed E is her reading.
    # (Book 5 still lies on the bed in this run, by him: the first E takes it, as in play.)
    cat = b.eval(f"{S}.bedCat.x")
    b.teleport(cat - 6, floor_y(8), route="cabin")
    b.tap("e")
    wait(0.6)
    ok &= check(b.eval(f"!!{W}.save.books[5]"), "E by him first takes book 5 off the bed", None)
    b.tap("e")
    wait(0.6)
    seen = "(() => { const s = window.__ship; const k = s.textures.exists('bed-seen') && s.textures.get('bed-seen').getSourceImage(); return [!!s.viewing, k ? k.width : 0]; })()"
    got = b.eval(seen)
    ok &= check(b.state()["mode"] == "play" and got == [True, 400], "E by him from the floor: a purr, the bed seen close", got)
    b.shot("finale-bed-seen")
    b.tap("e")
    wait(0.6)
    ok &= check(not b.eval("window.__ship.viewing"), "  and a key closes it", None)
    ok &= check(not b.errors, "no errors", b.errors[:3])
    return ok


def scenario_sound(b):
    """Step 12, the sound. Nobody hears anything here: what the game asked to be played is counted
    (`sfx.counts`), and what the ambience is set to where she stands is read."""
    S, SC = "window.__sfx", "window.__ship.soundscape"

    def count(name):
        return b.eval(f"{S}.counts[{json.dumps(name)}] || 0")

    b.open("?reset&play")
    wait(0.5)
    if b.eval(f"{S}.muted"):                    # (left muted by a run that broke off)
        b.eval(f"{S}.toggle()")
    # Every effect the code names is one that exists.
    names = set(sum(b.eval(f"Object.values({S}.groups)"), []))
    api = {"at", "listen", "ambience", "toggle", "unlock", "render", "counts", "log", "groups", "layers", "demos", "muted",
           "enabled", "running", "hold"}
    used = {}
    for path in (ROOT / "src").rglob("*.js"):
        if path.name == "sfx.js":
            continue
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"\bsfx(?:\.at\((?:[^()]|\([^()]*\))*\))?\s*\??\.(\w+)\s*(?:\?\.)?\(", text):
            used.setdefault(m.group(1), path.name)
        # (A held one by its name, `sfx.hold('whirr')`; and the tables of sounds on clips' frames and at the intro's
        # moments, each entry's effect named last: `[4, 'sip']`, `['dive', 0.3, 'swell']`.)
        for m in re.finditer(r"\.hold\('(\w+)'", text):
            used.setdefault(m.group(1), path.name)
        for m in re.finditer(r"\b(?:CLIP_SOUNDS|HER_SOUNDS|CUES)\s*=\s*\{", text):
            depth, i = 0, m.end() - 1
            while True:
                depth += {"{": 1, "}": -1}.get(text[i], 0)
                i += 1
                if depth == 0:
                    break
            for n in re.finditer(r",\s*'(\w+)'\s*\]", text[m.end():i]):
                used.setdefault(n.group(1), path.name)
    unknown = {n: f for n, f in used.items() if n not in names and n not in api}
    ok = check(not unknown, "every effect the game asks for exists", unknown)
    spare = sorted(names - set(used))
    print(f"        ({len(names)} effects, {len(names) - len(spare)} of them used; not used: {', '.join(spare) or 'none'})")
    ok &= check(b.eval(f"{S}.enabled") and not b.eval(f"{S}.muted"), "sound is on")
    n = count("step")
    b.hold("right", 1.0)
    wait(0.2)
    ok &= check(b.eval(f"{S}.running"), "the audio runs once a key has been pressed")
    ok &= check(count("step") - n >= 3, "her footsteps as she runs", count("step") - n)
    ok &= check(b.eval(f"{SC}.floor()") == "carpet", "inside, on carpet", b.eval(f"{SC}.floor()"))
    j, l = count("jump"), count("land")
    b.tap("space", 0.2)
    wait(0.9)
    ok &= check(count("jump") == j + 1 and count("land") == l + 1, "a jump and its landing", (count("jump") - j, count("land") - l))
    lv = b.eval(f"{SC}.levels()")
    ok &= check(lv["engine"] > 0.8 and lv["sea"] < 0.2 and lv.get("air", 0) > 0.5,
                "low in the ship: the engines and the ventilation, hardly any sea", lv)
    # M mutes, and M again brings it back.
    b.tap("m")
    wait(0.2)
    ok &= check(b.eval(f"{S}.muted") and b.eval("window.__ship.soundSign.alpha") > 0.9, "M mutes it, and its sign shows")
    b.shot("sound-muted")
    b.tap("m")
    wait(0.2)
    ok &= check(not b.eval(f"{S}.muted") and count("soundOn") == 1, "M again brings it back")
    # An elevator's ride: its doors, its car, its bell.
    b.teleport(LIFT_X, D4)
    b.tap("e")
    wait(0.5)
    b.tap("up")
    wait(0.1)
    b.tap("e")
    wait(3.2)
    got = [count(k) for k in ("doorSlide", "liftMove", "liftDing")]
    ok &= check(b.state()["y"] == D5 and got[0] >= 2 and got[1] == 1 and got[2] == 1, "an elevator: its doors, its car, its bell", got)
    # From outside, the sea.
    b.tap("o")
    wait(0.5)
    lv = b.eval(f"{SC}.levels()")
    ok &= check(lv["sea"] == 1 and lv["wind"] > 0.3, "from outside: the sea and the wind", lv)
    b.tap("o")
    wait(0.4)
    # Up on deck 12, out in the open: planks under her, the wind, less of the engines.
    b.open("?reset&play&at=sundeck&cards=all")
    wait(0.6)
    lv = b.eval(f"{SC}.levels()")
    ok &= check(b.eval(f"{SC}.floor()") == "deck" and lv["wind"] > 0.6 and lv["sea"] > 0.3 and lv["engine"] < 0.2,
                "on deck 12 in the open: planks, the wind, the sea below", (b.eval(f"{SC}.floor()"), lv))
    # A ladder's rungs, and the roof's metal.
    b.teleport(LADDER_X, D12)
    n = count("rung")
    hold_until(b, "up", lambda s: s["mode"] == "play" and s["y"] <= ROOF_Y, 6)
    wait(0.3)
    ok &= check(count("rung") - n >= 3 and b.eval(f"{SC}.floor()") == "metal", "a ladder's rungs, then the roof's metal",
                (count("rung") - n, b.eval(f"{SC}.floor()"), b.state()))
    # And the tools' way: an effect rendered without being played is not silence.
    res = b.send("Runtime.evaluate", awaitPromise=True, returnByValue=True,
                 expression=f"{S}.render('horn', [1], 1.5, 22050).then(([l]) => l.reduce((m, v) => Math.max(m, Math.abs(v)), 0))")
    peak = res.get("result", {}).get("value", 0)
    ok &= check(0.1 < peak < 0.95, "the horn, rendered, is loud and not clipped", peak)
    ok &= check(not b.errors, "no errors", b.errors[:3])
    return ok


def scenario_gamepad(b):
    # The Xbox controller (§3.1), a fake one: everything the keyboard does in play, the welcome
    # menu, the intro's skip and the whole-ship view.
    b.fake_pad()
    try:
        b.open("?reset&play&tangerines=infinite")
        s0 = b.state()
        b.stick(1, 0)
        wait(0.6)
        s = b.state()
        ok = check(s["x"] > s0["x"] + 40, "the left stick runs her", s)
        b.stick(0.9, 0.45)            # tilted a little down while running
        wait(0.2)
        c = b.controls()
        ok &= check(c["right"] and not c["down"], "running with the stick tilted down isn't 'down'", c)
        b.stick(0.3, 0.9)
        wait(0.2)
        ok &= check(b.controls()["down"], "pointed down, it is")
        b.stick(0, 0)
        wait(0.3)
        y0 = b.state()["y"]
        b.pad("A", True)
        wait(0.25)
        ok &= check(b.state()["y"] < y0 - 20, "A jumps", b.state())
        b.pad("A", False)
        wait(0.8)
        door = "part-door-4-74"
        b.teleport(b.eval(f"window.__ship.bulkheads.find(d => d.id === '{door}').x") - 16, D4)
        b.pad_tap("X")
        ok &= check(b.eval(f"window.__ship.bulkheads.find(d => d.id === '{door}').open"), "X opens a door")
        b.eval("window.__ship.save.verbs.push('dash')")      # the lunge is learned at near-catch 1
        b.pad_tap("B")
        ok &= check(b.eval("window.__ship.isLunging()"), "B cries out and lunges")
        # The rumble (§3.1): the lunge's burst on the controller in use.
        wait(0.1)
        ok &= check([120, 0.3] in [r[1:3] for r in b.eval("window.__rumbles")], "and the controller rumbles with it",
                    b.eval("window.__rumbles"))
        n = len(b.eval("window.__rumbles"))
        b.tap("left")                  # back on the keyboard: no rumble
        b.eval("window.__ship.scareFall()")
        wait(0.2)
        ok &= check(len(b.eval("window.__rumbles")) == n, "playing on the keyboard, nothing rumbles", b.eval("window.__rumbles")[n:])
        wait(3.0)
        b.pad_tap("Y")                 # the controller again
        b.eval("window.__ship.scareFall()")
        wait(0.2)
        ok &= check([260, 1] in [r[1:3] for r in b.eval("window.__rumbles")[n:]], "a scare's fall rumbles hard",
                    b.eval("window.__rumbles")[n:])
        wait(3.0)
        wait(0.4)
        b.pad_tap("RS")
        wait(0.4)
        ok &= check(bool(b.eval("!!window.__ship.overview")), "the right stick's click shows the whole ship")
        z0 = b.eval("window.__ship.cameras.main.zoom")
        b.pad_tap("RT")
        wait(0.3)
        ok &= check(b.eval("window.__ship.cameras.main.zoom") > z0, "RT zooms in")
        b.pad_tap("LT")
        wait(0.3)
        ok &= check(b.eval("window.__ship.cameras.main.zoom") < z0 * 1.2, "LT zooms out")
        b.pad_tap("B")
        wait(0.4)
        ok &= check(not b.eval("!!window.__ship.overview"), "B leaves it")
        b.pad_tap("RS")
        wait(0.4)
        b.pad_tap("RS")
        wait(0.4)
        ok &= check(not b.eval("!!window.__ship.overview"), "and so does the right stick's click again")
        b.pad_tap("RS", 0.1)
        # Mute stays on the keyboard only (the user, 2026-11-15): no button changes the sound.
        muted = b.eval("window.__ship.controls.state.mute")
        ok &= check(not muted, "no button mutes")
        b.pad_tap("B")

        # The welcome menu and the intro: A picks PLAY, Menu skips the intro.
        b.open("?reset", start=None)
        stage = "(window.__ship.intro ? window.__ship.intro.stage : 'none')"
        ok &= check(b.eval(stage) == "welcome", "the welcome screen", b.eval(stage))
        b.pad_tap("A")
        wait(0.6)
        ok &= check(b.eval(stage) == "running", "A starts the game: the intro runs", b.eval(stage))
        b.pad_tap("MENU")
        wait(1.0)
        ok &= check(b.eval(stage) in ("done", "none"), "Menu skips the intro", b.eval(stage))

        # A controller the browser puts in another slot still plays.
        b.fake_pad(False)
        b.fake_pad(index=1)
        b.open("?reset&play")
        s0 = b.state()
        b.stick(-1, 0)
        wait(0.6)
        b.stick(0, 0)
        s = b.state()
        ok &= check(s["x"] < s0["x"] - 40, "a pad in the second slot runs her too", s)
    finally:
        b.fake_pad(False)
    return ok


# --- The mishaps (docs/plan-the-rest.md §3 1.3, 2026-11-19) -----------------------------------------
# A case for each scenario of docs/plan-three-uses.md §1.6 that had no check of its own, or one by her
# word alone: made through the thing's own code (the person's touch, the round's hit, the hazard met in
# play), each with none on her and then with two: the scenario, its gag's clip, her checkpoint after,
# the count as it was and nothing left lying (1.2a). 7b and 13b cannot happen (the chair stands, a door
# hits her only facing it): kept in the table, not here. Region 1's papers, suitcase, dog and vacuum,
# 7a, 13a, 14a, 17, 19, 21 and 23 are checked in their regions' scenarios.

MS = "window.__ship"
# (Every gag clip played, in order, and every trip back to a checkpoint: what the cases read.)
WATCH = ("(() => { const S = window.__ship; window.__clips = []; window.__respawns = 0; window.__hits = [];"
         " if (window.__watching) return; window.__watching = true;"
         " const A = Phaser.Animations.AnimationState.prototype, play = A.play;"
         " A.play = function (key, ...rest) { const k = typeof key === 'string' ? key : key?.key;"
         " if (/^(gags?|towels|drill)-/.test(k || '')) window.__clips.push(k); return play.call(this, key, ...rest); };"
         " const r = S.respawn; S.respawn = function (...a) { window.__respawns++; return r.apply(this, a); };"
         " const h = S.scareContact; S.scareContact = function (x, w, o) { const id = h.call(this, x, w, o);"
         " window.__hits.push([w, id, this.mode, Math.round(this.time.now)]); return id; }; })()")
# (A gag of hers, as against the world's own clips: a door's swing, the towels' fall.)
HER_GAG = r"^(gag-|gags-(jog|ball|tray|sprinkler|dnd|gull|chair|steam|flare|stairs|parasol|door-(squash|slide))|towels-(run|bury)|drill-(drop|crawl))"


def mishap_hit(b, label, n, act, want, clip, within=4.0, fresh=None):
    """`act()` makes the hit; then: the scenario `want`, a clip matching `clip` (None: no gag of hers,
    the built fall), and her checkpoint after with `n` on her as before and nothing lying. `fresh()`
    first: a new game."""
    if fresh:
        fresh()
    b.eval(f"{MS}.save.tangerines = {n}; {MS}.refreshHud(); {MS}.lastMishap = null; {MS}.safeUntil = 0; {MS}.flinchUntil = 0")
    b.eval(WATCH)
    act()
    hit = wait_js(b, f"!!{MS}.lastMishap && {MS}.mode !== 'play'", within)
    back = wait_js(b, f"{MS}.mode === 'play' && window.__respawns > 0", 15)
    # (Its clips read once she is back: a gag may play its own after its first, as the tiptoe after the hands.)
    got = b.eval(f"[{MS}.lastMishap?.id ?? null, window.__clips.slice(), window.__hits.slice()]")
    gag = any(re.match(clip, c) for c in got[1]) if clip else not any(re.match(HER_GAG, c) for c in got[1])
    ok = check(hit and got[0] == want and gag, f"{label}, {n} on her: {want}, {clip or 'the built fall'}", got)
    s = b.state()
    ok &= check(back and s["tangerines"] == n and b.eval(f"{MS}.loose.all.length") == 0,
                f"{label}: then her checkpoint, {n} on her as before, nothing lying", s)
    wait(1.0)       # (her step out of the checkpoint's door turns her: done before the next hit is set up)
    return ok


def both(b, label, act, want, clip, within=4.0, fresh=None):
    """The hit with none on her, then with two (1.2a: the same gag, the count as it was)."""
    ok = mishap_hit(b, label, 0, act, want, clip, within, fresh)
    return ok & mishap_hit(b, label, 2, act, want, clip, within, fresh)


def touch(b, pid, floor, route, face, v, his_dir, walking):
    """She and someone of the people 30 px ahead of her on his round: her facing (1 east) and speed, his
    way and whether he walks; then their touch, as the game makes it (`world.touched`)."""
    # (Their own touch held off until this one: he stands, and the cool-down covers the teleport.)
    b.eval(f"(S => {{ const p = S.world.people.byId.{pid}; p.pausedUntil = S.time.now + 600000; S.world.touchCool = S.time.now + 600000; }})({MS})")
    x = person(b, pid)["x"] - 30
    b.teleport(x, floor, route)
    wait(0.3)
    b.eval(f"(S => {{ const p = S.world.people.byId.{pid}; p.x = S.player.x + 30; p.dir = {his_dir};"
           f" p.pausedUntil = {'0' if walking else 'S.time.now + 600000'}; S.world.people.place(p);"
           f" S.player.setFlipX({'true' if face < 0 else 'false'}); S.player.body.setVelocityX({v}); S.world.touchCool = 0;"
           f" S.world.touched(p); }})({MS})")


def scenario_mishaps__porter(b):
    """The porter and his cart (deck 4): 8a she runs into the cart, 8b it pushes into her front, 8c it
    reaches her back, 8d she runs into his back."""
    b.open("?play&at=deck4")
    ok = True
    for want, face, v, his, walking, clip in [("8a", 1, 120, -1, False, "^gag-cart-drape"), ("8b", 1, 0, -1, True, "^gag-cart-push"),
                                               ("8c", -1, 0, -1, True, "^gag-cart-sit"), ("8d", 1, 120, 1, False, "^gag-cart-bounce")]:
        ok &= both(b, f"the porter ({want})", lambda: touch(b, "haz_porter", D4, "inside", face, v, his, walking), want, clip)
    return ok


def scenario_mishaps__jogger(b):
    """The jogger on the promenade (deck 6): 9a she runs into him head-on, 9b he runs into her front, 9c
    into her back, 9d she runs into his back."""
    b.open("?play&at=promenade")
    ok = True
    for want, face, v, his, walking, clip in [("9a", 1, 120, -1, False, "^gags-jog-spin"), ("9b", 1, 0, -1, True, "^gags-jog-bowled"),
                                               ("9c", -1, 0, -1, True, "^gags-jog-shoved"), ("9d", 1, 120, 1, False, "^gag-cart-bounce")]:
        ok &= both(b, f"the jogger ({want})", lambda: touch(b, "haz_jogger", D6, "promenade", face, v, his, walking), want, clip)
    return ok


def scenario_mishaps__breakfast(b):
    """The breakfast round (deck 5): 10a she walks into the stewardess's tray, 10b it meets her back; her
    trolley: 10c over it, 10d back off it (the stewardess just past it), 10e wheeled into her back (the
    built fall); 10f the stewardess, her hands empty."""
    b.open("?play&at=deck5")
    BK = f"{MS}.world.movers.find(m => m.constructor.name === 'Breakfast')"
    y = b.eval(f"{BK}.def.y")
    ok = True

    def bump(face, tray):
        b.eval(f"{BK}.bumpedAt = {MS}.time.now")     # (its own hits held off over the teleport)
        b.teleport(b.eval(f"{BK}.x") - 20, y)
        wait(0.3)
        b.eval(f"(k => {{ const S = {MS}; k.x = S.player.x + 20; k.holding = {str(tray).lower()}; k.giving = false; k.bumpedAt = -1e9;"
               f" S.player.setFlipX({'true' if face < 0 else 'false'}); k.bump(S.player, S.time.now); }})({BK})")

    def trolley(face, v, step, crowded):
        x = b.eval(f"(k => k.cartX - ((k.cart.width - 6) / 2 + {MS}.player.body.width / 2) + 1)({BK})")
        b.eval(f"{BK}.bumpedAt = {MS}.time.now")
        b.teleport(x, y)
        wait(0.3)
        b.eval(f"(k => {{ const S = {MS}; S.player.x = k.cartX - ((k.cart.width - 6) / 2 + S.player.body.width / 2) + 1;"
               f" k.x = k.cartX + {40 if crowded else -200}; k.bumpedAt = -1e9; S.player.setFlipX({'true' if face < 0 else 'false'});"
               f" S.player.body.setVelocityX({v}); k.trolleyHit(S.player, S.time.now, {step}, 1 / 60); }})({BK})")

    ok &= both(b, "the stewardess's tray in front (10a)", lambda: bump(1, True), "10a", "^gag-tray-sit")
    ok &= both(b, "the stewardess's tray at her back (10b)", lambda: bump(-1, True), "10b", "^gag-tray-sit")
    ok &= both(b, "the stewardess, her hands empty (10f)", lambda: bump(1, False), "10f", "^gag-cart-bounce")
    ok &= both(b, "into the trolley, no one past it (10c)", lambda: trolley(1, 120, 0, False), "10c", "^gag-trolley-trip")
    ok &= both(b, "into the trolley, the stewardess past it (10d)", lambda: trolley(1, 120, 0, True), "10d", "^gag-cart-push")
    ok &= both(b, "the trolley wheeled into her back (10e)", lambda: trolley(-1, 0, -2, False), "10e", None)
    return ok


def scenario_mishaps__jet(b):
    """The kid's jet (deck 11, after near-catch 5): 11a in her face, 11b in her back; the wet gag (16's)."""
    b.open("?play&at=jet11&did=bb5")
    L = b.eval(f"{MS}.world.data.lido")
    K = f"{MS}.world.people.byId.npc_kid"
    ok = True

    def squirt(face):
        b.teleport(L["kidA"] + 70, D11)
        wait(0.2)
        b.eval(f"(k => {{ k.x = {L['kidA'] + 190}; k.dir = -1; k.mode = 'patrol'; k.nextSquirt = 0; k.pauseUntil = 0;"
               f" {MS}.player.setFlipX({'true' if face < 0 else 'false'}); }})({K})")

    ok &= both(b, "the kid's jet in her face (11a)", lambda: squirt(1), "11a", "^gags-sprinkler", within=5)
    ok &= both(b, "the kid's jet in her back (11b)", lambda: squirt(-1), "11b", "^gags-sprinkler", within=5)
    return ok


def scenario_mishaps__light(b):
    """The stage's swinging light (deck 6, after near-catch 3): 12a facing it as it comes (9a's spin), 12b
    with her back to it (9c's belly-flop)."""
    b.open("?play&at=light6&did=bb3")
    LT = f"{MS}.world.movers.find(m => m.constructor.name === 'SwingLight')"
    ok = True

    def under(front):
        # (Once the lamp has turned at the aft end of its swing, she stands just forward of the bottom
        # of its arc, facing aft or not: it meets her from aft. Aft of the bottom is the open trap door.)
        cx = b.eval(f"{LT}.def.x")
        end = now() + 8
        while now() < end:
            a = b.eval(f"{LT}.lamp?.x ?? 0")
            wait(1 / 60)
            c = b.eval(f"{LT}.lamp?.x ?? 0")
            if b.eval(f"!!{LT}.lamp?.swinging") and c < a and c > cx + 45:
                break
        b.teleport(cx - 10, D6)
        b.eval(f"{MS}.player.setFlipX({'false' if front else 'true'})")

    ok &= both(b, "the stage's light, facing it (12a)", lambda: under(True), "12a", "^gags-jog-spin", within=3)
    ok &= both(b, "the stage's light at her back (12b)", lambda: under(False), "12b", "^gags-jog-shoved", within=3)
    return ok


def scenario_mishaps__ball(b):
    """The court's balls (deck 12): 14a in her face, 14b on the back of her head."""
    b.open("?play&at=court")
    bl = b.eval(f"{MS}.world.data.topdeck.balls[0]")
    ok = True

    def stand(face):
        b.teleport(bl["x"] + 80, D12)
        b.eval(f"{MS}.player.setFlipX({'true' if face < 0 else 'false'})")

    ok &= both(b, "a ball off the hoop, facing it (14a)", lambda: stand(-1), "14a", "^gags-ball-back", within=9)
    ok &= both(b, "a ball off the hoop, her back to it (14b)", lambda: stand(1), "14b", "^gags-ball-front", within=9)
    return ok


def scenario_mishaps__things(b):
    """Met in play from their start places, checked till now by her word alone: the room-service tray (3),
    the drill's boat (15), a sprinkler (16), the towel stack (18)."""
    ok = True

    def run(place, key, extra="", first=None):
        # (A new game for each (`fresh`): the towel stack stays fallen once it has fallen.)
        def act():
            if first:
                first()
            hold_until(b, key, lambda s: s["mode"] != "play", 6)
            b.key(key, False)
        return dict(act=act, fresh=lambda: b.open(f"?play&reset&at={place}{extra}"))

    DR = f"{MS}.world.story.drill"
    lull = lambda: wait_js(b, f"(a => a.idle && a.t > 8.3)({DR}.at({MS}.time.now))", 14)
    # (Deck 9's sprinkler: she sets off once it rains.)
    SP = f"{MS}.world.movers.filter(m => m.constructor.name === 'Sprinkler').sort((a, c) => Math.abs(a.def.x - {MS}.player.x) - Math.abs(c.def.x - {MS}.player.x))[0]"
    rain = lambda: wait_js(b, f"(m => m.phase({MS}.time.now) === 'on')({SP})", 14)
    ok &= both(b, "the room-service tray (3)", want="3", **run("trays10", "right"), clip="^gags-tray-ride", within=6)
    ok &= both(b, "the drill's boat (15)", want="15", **run("drill7", "right", "&cards=all", lull), clip="^drill-drop", within=8)
    ok &= both(b, "deck 9's sprinkler (16)", want="16", **run("sprinkler9", "right", first=rain), clip="^gags-sprinkler", within=8)
    ok &= both(b, "the towel stack (18)", want="18", **run("towels9", "left"), clip="^towels-(run|bury)", within=6)
    return ok


def scenario_mishaps__balcony(b):
    """Vaulting onto the sunbather's balcony (deck 8): 24, her tiptoe, none on her or two."""
    b.open("?play&at=occupied8&cards=all")
    spot = b.state()

    def vault():
        b.teleport(spot["x"], spot["y"], "promenade")
        wait(0.4)
        b.key("left", True)
        hold_until(b, [], lambda s: s["x"] < spot["x"] - 20, 3)
        b.key("space", True); wait(0.08); b.key("space", False)
        wait(0.2)
        b.key("space", True); wait(0.08); b.key("space", False)
        hold_until(b, [], lambda s: s["mode"] != "play", 3)
        b.key("left", False)

    return both(b, "the sunbather's balcony (24)", vault, "24", "^gags-dnd-tiptoe", within=4)


def scenario_mishaps__gulls(b):
    """The three gulls (20 to 22): with none on her, a gull on a balcony rail is her gag (20); with two,
    each takes one and she keeps her place: on the rail's balcony, on the funnel's stairway, in a glide."""
    ok = True
    b.open("?play&at=gull9")
    spot = b.state()
    def linger():
        b.teleport(spot["x"], spot["y"], "promenade")

    ok &= mishap_hit(b, "a gull on the rail (20)", 0, linger, "20", "^gags-gull", within=14)

    def took(label, want, act, within):
        b.eval(f"{MS}.save.tangerines = 2; {MS}.refreshHud(); {MS}.lastMishap = null; {MS}.safeUntil = 0")
        b.eval(WATCH)
        act()
        hit = wait_js(b, f"{MS}.lastMishap?.id === '{want}'", within)
        wait(0.3)
        s = b.state()
        return check(hit and s["tangerines"] == 1 and b.eval("window.__respawns") == 0 and b.eval(f"{MS}.loose.all.length") == 0
                     and not any(re.match(HER_GAG, c) for c in b.eval("window.__clips")),
                     f"{label}, two on her: it takes one, no gag, her place kept", (b.eval(f"{MS}.lastMishap?.id"), s, b.eval("window.__clips")))

    ok &= took("a gull on the rail (20)", "20", linger, 14)
    wait_js(b, f"!{MS}.isSafe()", 4)
    # The funnel's stairway: a few steps up in a lull (its own gulls held off), a gull dives at her.
    b.open("?play&at=stairway&cards=all")
    b.eval(f"{MS}.world.story.funnelWind.nextAt = 1e12")
    fn = b.eval(f"{MS}.world.data.funnel")
    b.teleport(fn["foot"][0], fn["foot"][1])
    wait(0.4)
    wait_js(b, f"{MS}.world.story.funnelGusts.phase({MS}.time.now) === 'calm'", 8)
    b.key("up", True)
    hold_until(b, [], lambda s: s["mode"] == "stairs", 3)
    wait(0.3)
    b.key("up", False)
    ok &= check(b.state()["mode"] == "stairs", "on the funnel's stairway", b.state())

    def dive():
        b.eval(f"window.__gull = {MS}.add.image({MS}.player.x + 30, {MS}.player.y - 60, 'tangerine');"
               f" {MS}.scareContact({MS}.player.x + 8, 'funnelgull', {{ snatch: window.__gull }})")

    ok &= took("a funnel gull on the stairway (21)", "21", dive, 2)
    ok &= check(b.state()["mode"] == "stairs", "and she is still on the stairway", b.state())
    # A glide off the balcony forward of the spa, and a crossing gull meets her (the game's own call for
    # it, `scareAir`: the gulls' flight is the finale's, checked there).
    b.open("?play&at=sunset&cards=all")

    def glide():
        b.key("left", True)
        open_parasol(b)
        wait_js(b, f"{MS}.gliding", 3)
        b.eval(f"window.__gull = {MS}.add.image({MS}.player.x - 20, {MS}.player.y - 40, 'tangerine');"
               f" {MS}.scareAir('crossgull', {{ snatch: window.__gull }})")

    ok &= took("a gull across her glide (22)", "22", glide, 6)
    b.key("left", False)
    b.key("space", False)
    return ok


# A scenario's cases (docs/plan-fast-tests.md §3.5): `scenario_region4__towels` is `region4.towels`, a
# function that starts from a prepared state (`enter_regionN`, `?at=`) and checks one thing. A new
# check goes in as a case of its own; `region4` runs the old scenario and every case of it.
def scenario_highlight(b):
    """What she can use pulses where E would act on it (src/highlight.js; the user, 2026-11-23): a thing in full colour
    down to the wash of the props round it and back, a muted map piece up to its full twin and back, settling back
    when she leaves; people never; the casino's slot machines at 12%."""
    S = "window.__ship"
    b.open("?reset&play", start=None)
    wait(0.5)
    b.eval(f"(s => {{ s.scareContact = () => null; s.mishap = () => {{}}; }})({S})")      # (no hits on the way)
    H = f"{S}.highlight"
    thing = lambda i: b.eval(f"(t => [t.x, t.y])({S}.world.things.find(t => t.id === '{i}'))")
    def at(x, y, route="inside", settle=0.9):
        b.teleport(x, y - 2, route)
        wait(settle)
        return b.eval(f"{H}.state()")
    ok = True
    # Doors are secrets too: at rest washed like the background doors beside them; at the laundry's (between guest
    # cabin doors, 35%) the wash pulses off it, up to full colour, and back.
    ok &= check(b.eval(f"{H}.rest.size") >= 60 and b.eval(f"{H}.restBox.size") >= 15 and b.eval(f"{H}.skipped.length") == 0,
                "every door she can use is washed at rest, none without a tone", (b.eval(f"{H}.rest.size"), b.eval(f"{H}.restBox.size"), b.eval(f"{H}.skipped")))
    door = b.eval(f"{S}.rooms.find(r => r.route === 'laundry').door")
    st = at(door + 4, D4)
    ok &= check(len(st) == 1 and st[0]["key"].startswith("door:") and st[0]["parts"][0]["mode"] == "rest"
                and abs(st[0]["parts"][0]["k"] - 0.35) < 1e-6 and st[0]["parts"][0]["frame"] == "door-crew",
                "at the laundry's door: washed 35% like the cabin doors beside it, the wash pulsing off", st)
    seen = set()
    for _ in range(20):
        wait(0.08)
        seen.add(round(b.eval(f"{H}.state()[0].parts[0].alpha"), 2))
    ok &= check(max(seen) > 0.3 and min(seen) < 0.05, "and back, again and again while she stands there", sorted(seen))
    at(door + 200, D4, settle=0.8)
    ok &= check(abs(b.eval(f"(o => {H}.rest.get(o).over.alpha)({H}.find(o => o.frame.name === 'door-crew' && Math.abs(o.x - {door}) < 20 && Math.abs(o.y - {D4}) < 4)[0])") - 0.35) < 1e-6,
                "away from it: washed again")
    # Her crew cabin's door: washed like the crew door beside it (the Medical Center's, 35%).
    st = at(SPAWN_X - 6, D3)
    ok &= check(bool(st) and st[0]["key"].startswith("door:") and st[0]["parts"][0]["mode"] == "rest" and abs(st[0]["parts"][0]["k"] - 0.35) < 1e-6,
                "her crew cabin's door: washed 35% at rest, up to full colour", st)
    # Her mirror, drawn into the room's picture: only its own pixels pulse (the wall round it taken out).
    mirror = b.eval(f"{S}.world.rooms.crewcabin.mirror")
    st = at(mirror + 2, D3, route="crewcabin")
    ok &= check(bool(st) and st[0]["key"] == "mirror" and abs(st[0]["parts"][0]["k"] - 0.4) < 1e-6 and b.eval(f"(c => c.width < 30)({H}.on.get('mirror').parts[0].over)"),
                "her mirror pulses on its own, to 40%", st)
    # From inside, the way out is the door drawn in the room's picture: it pulses there (the user: "the doors are not
    # pulsing" inside her crew cabin and cabin 8206).
    st = at(SPAWN_X + 6, D3, route="crewcabin")
    ok &= check(bool(st) and st[0]["key"].startswith("door:") and b.eval(f"{H}.on.get('{st[0]['key']}').parts[0].o.texture.key") == "room-crewcabin"
                and st[0]["parts"][0]["mode"] == "rest" and abs(st[0]["parts"][0]["k"] - 0.3) < 1e-6,
                "inside her crew cabin: its door, in the room's picture, washed 30% like the room, pulses up", st)
    # A muted piece (the ice swan): its full twin while she is there, its muted one again once she has gone.
    x, y = thing("sec_swan")
    st = at(x - 10, y)
    ok &= check(bool(st) and st[0]["key"] == "thing:sec_swan" and st[0]["parts"][0]["mode"] == "muted" and st[0]["parts"][0]["frame"] == "ice-swan",
                "at the ice swan: shown by its full twin, the wash pulsing off it", st)
    at(x - 160, y, settle=0.8)
    ok &= check(b.eval(f"{H}.state()") == [] and b.eval(f"{H}.find(o => o.frame.name === 'ice-swan-w20').length") == 1,
                "away from it: muted again, nothing left over", b.eval(f"{H}.state()"))
    # Only where E would act: the pool bar's mojito is region 8's, so before it nothing pulses there.
    x, y = thing("src_cocktail")
    at(x - 10, y)
    ok &= check(b.eval(f"{H}.state()") == [], "at the pool bar before region 8 (E does nothing there yet): nothing", b.eval(f"{H}.state()"))
    # The casino's slot machines are washed 12%, and the jackpot pair pulses up from that.
    x, y = thing("sec_jackpot")
    ok &= check(b.eval(f"{H}.find(o => o.frame.name === 'slot-pair-w20').length") == 0 and b.eval(f"{H}.find(o => o.frame.name === 'slot-pair-lt').length") >= 6,
                "the casino's slot machines at 12%")
    st = at(x - 8, y)
    ok &= check(bool(st) and st[0]["key"] == "thing:sec_jackpot" and len(st[0]["parts"]) == 1 and abs(st[0]["parts"][0]["k"] - 0.12) < 1e-6,
                "the jackpot pair pulses, its sign does not", st)
    # A trunk's door: the door only, never the arrows over it.
    tx, ty = b.eval(f"(t => [t.x, t.doors[0].y])({S}.trunks.find(t => t.doors.length === 2))")
    st = at(tx - 4, ty)
    ok &= check(bool(st) and st[0]["key"].startswith("trunk:") and [q["frame"] for q in st[0]["parts"]] == ["door-crew"],
                "a trunk's door pulses, its arrows do not", st)
    # People never change: by the sushi chef, nothing.
    cx, cy = b.eval(f"(p => [p.sprite.x, {D12}])({S}.world.people.byId.amb_sushi_chef)")
    at(cx - 30, cy, settle=0.8)
    ok &= check(b.eval(f"{H}.state()") == [], "by the sushi chef: nothing changes", b.eval(f"{H}.state()"))
    # A pickup: the pickup itself, from its full colours, its glint as it was.
    # (Book 6 on the Atrium Café's table since 2026-11-23: book 1 comes from her husband's hand.)
    x, y = thing("book_6")
    st = at(x - 12, y)
    ok &= check(bool(st) and st[0]["key"] == "thing:book_6" and st[0]["parts"][0]["mode"] == "full", "by book 6: the book pulses", st)
    ok &= check(b.errors == [], "no errors", b.errors)
    return ok


def scenario_keeps(b):
    """The things to find, kept (plan-the-rest §4 2.5): nothing counted at the start; each kind's count comes with its
    first find, once its close-up is closed (and the second goes up); a book's cover the same; her husband's four places
    empty before his table scene and holding their things after; each of her things and his on cabin 8206's desk once
    found, and Bumbot's on his bed. (The other scenarios skip the close-ups; this one shows them.)"""
    S = "window.__ship"
    W = f"{S}.world"
    def thing(tid):
        # (Whether it lies there by the story, wherever she is: a balcony's things are drawn only while she is out there.)
        return b.eval(f"(w => (t => t && [t.x, !t.done && w.met(t.needs) && (!t.after || w.cond(t.after)) && !(t.until && w.cond(t.until)),"
                      f" t.pick ? Math.round(t.pick.y) : null])(w.things.find(t => t.id === '{tid}')))({W})")
    def hud():
        h = b.eval(f"{S}.hud.state()")
        return {k: h[k] for k in ("cat", "her", "him", "book")} | {"order": h["order"]}
    shown = (f"(() => {{ const p = {S}.uiLayer.list.find(o => o.active && o.texture && (o.texture.key === 'closeups' || o.texture.key.startsWith('cover-')));"
             " return p ? (p.texture.key === 'closeups' ? p.frame.name : p.texture.key) : null; })()")

    b.open("?reset&play&at=atrium")
    b.eval("window.__skipCloseups = false")
    wait(0.4)
    ok = check(hud() == {"cat": "", "her": "", "him": "", "book": "", "order": []}, "at the start nothing is counted", hud())

    # The first of each kind (and a second): its close-up, the count not yet on; a key closes it, the count comes on.
    first = (("keep_wool", D5, "wool", "cat", "1/8"), ("keep_flag", D5, "flag", "her", "1/4"), ("book_6", D5, "cover-6", "book", "1/14"))
    order = []
    for tid, y, pic, kind, count in first:
        x, vis, _ = thing(tid)
        b.teleport(x, y)
        b.tap("e")
        ok &= check(wait_js(b, f"{S}.viewing", 2) and b.eval(shown) == pic, f"{tid}: E shows it close", b.eval(shown))
        wait(0.3)
        ok &= check(hud()[kind] == "", f"  its count not on while it shows", hud())
        b.shot(f"keeps-{pic}")
        wait(0.4)
        b.tap("e")
        ok &= check(wait_js(b, f"!{S}.viewing", 2), "  a key closes it")
        wait(0.4)
        order.append(kind)
        got = hud()
        ok &= check(got[kind] == count and got["order"] == order, f"  and its count comes on: {count}", got)
    x, _, _ = thing("keep_feather")
    b.teleport(x, D4)
    b.eval(f"{W}.take({W}.things.find(t => t.id === 'keep_feather'))")      # (from the climb's shelf: taken as E would)
    wait_js(b, f"{S}.viewing", 2)
    ok &= check(hud()["cat"] == "1/8", "a second find: the count as it was while it shows", hud())
    wait(0.5)
    b.tap("e")
    wait_js(b, f"!{S}.viewing", 2)
    wait(0.4)
    ok &= check(hud()["cat"] == "2/8", "  and up by one once it is closed", hud())
    b.eval(f"{W}.giveBook(9)")                # (a book handed to her: the engineer's, as from his hand)
    ok &= check(wait_js(b, f"{S}.viewing", 2) and b.eval(shown) == "cover-9", "a book given: its cover shows", b.eval(shown))
    wait(0.5)
    ok &= check(hud()["book"] == "1/14", "  the books' count as it was while it shows", hud())
    b.tap("e")
    wait_js(b, f"!{S}.viewing", 2)
    wait(0.4)
    ok &= check(hud()["book"] == "2/14", "  and up by one once it is closed", hud())

    # His four (§4 2.1): nowhere before his table scene; each in its place after it.
    his = ("keep_tshirt", "keep_sleepmask", "keep_handheld", "keep_pick")
    before = {t: thing(t)[1] for t in his}
    ok &= check(not any(before.values()), "his four places empty before the table scene", before)
    b.eval(f"{S}.progress.setFlag('table')")
    wait(0.3)
    after = {t: thing(t)[1] for t in his}
    ok &= check(all(after.values()), "and each holding its thing after it", after)
    x, _, _ = thing("keep_tshirt")
    b.teleport(x, D12)
    b.tap("e")
    ok &= check(wait_js(b, f"{S}.viewing", 2) and b.eval(shown) == "tshirt", "his t-shirt: E shows it close", b.eval(shown))
    wait(0.7)
    ok &= check(hud()["him"] == "", "  his count not on while it shows", hud())
    b.tap("e")
    wait_js(b, f"!{S}.viewing", 2)
    wait(0.4)
    got = hud()
    ok &= check(got["him"] == "1/4" and got["order"] == ["cat", "her", "book", "him"], "  and his count comes on, last in the row", got)
    b.shot("keeps-hud")

    # The desk and the bed seen close: each found thing's box differs from the bare picture, each other one is bare.
    compare = ("((scene, list) => { const s = window.__ship, L = s.cache.json.get(scene + '-layout');"
               " const px = img => { const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;"
               " const x = c.getContext('2d'); x.drawImage(img, 0, 0); return x; };"
               " const seen = px(s.textures.get(scene + '-seen').getSourceImage()), bare = px(s.textures.get(scene + '-bare').getSourceImage());"
               " const out = {}; for (const k of list) { const t = s.textures.get(scene + '-' + k).getSourceImage();"
               " const a = seen.getImageData(L[k][0], L[k][1], t.width, t.height).data, z = bare.getImageData(L[k][0], L[k][1], t.width, t.height).data;"
               " out[k] = a.some((v, i) => v !== z[i]); } return out; })")
    desk = ["flag", "plant", "bookmark", "diary", "tshirt", "sleepmask", "handheld", "pick"]
    bed = ["massage", "car", "bell", "feather", "snack", "ball", "wool", "sardines"]
    own = b.eval(f"(r => [r.door, r.floor])({S}.rooms.find(r => r.route === 'cabin'))")
    def seen(scene, things, found):
        if scene == "desk":
            b.teleport(own[0] + 51, own[1], route="cabin")
        else:
            b.teleport(b.eval(f"{W}.data.finale.home.catX") - 6, own[1], route="cabin")
        b.tap("e")
        wait_js(b, f"{S}.viewing", 2)
        got = b.eval(f"{compare}('{scene}', {json.dumps(things)})")
        res = check(got == {k: k in found for k in things}, f"the {scene} seen close: {len(found)} found, each there, the rest bare", got)
        b.shot(f"keeps-{scene}-{len(found)}")
        wait(0.5)
        b.tap("e")
        wait_js(b, f"!{S}.viewing", 2)
        wait(0.3)
        return res
    ok &= seen("desk", desk, ["flag", "tshirt"])                       # (what she found above)
    b.eval(f"(s => {{ for (const k of {json.dumps(desk)}) {{ const w = 'keep:' + (['tshirt', 'sleepmask', 'handheld', 'pick'].includes(k) ? 'him' : 'her') + ':' + k;"
           " if (!s.save.keeps.includes(w)) s.save.keeps.push(w); } })(window.__ship)")
    ok &= seen("desk", desk, desk)
    ok &= check(b.errors == [], "no errors", b.errors)
    # Bumbot's bed, on the day after (book 5, on the bed, taken first).
    for q, found in (("ball,car", ["ball", "car"]), ("bed", bed)):
        b.open(f"?reset&play&at=cabin&did=catch,home&books=5&keeps={q}")
        b.eval("window.__skipCloseups = false")
        ok &= seen("bed", bed, found)
    ok &= check(b.errors == [], "no errors", b.errors)
    return ok


def scenario_region3__lookout(b):
    """Look-out 1 (plan-the-rest §5 3.1; the user, 2026-11-23): at the Stardust balcony's rail, half a second standing
    still eases the camera aft and down to the stage, deck 6 opened under deck 7 (both cut open); a step and it comes
    back to her, deck 6 closed again. Hopping the rail, both decks stay open as she falls, nothing after she lands."""
    S = "window.__ship"
    L = f"{S}.world.movers.find(m => m.def?.id === 'look_stardust')"
    b.open("?reset&play&at=balcony7")
    wait(0.4)
    x = b.eval(f"{L}.def.x")
    b.teleport(x - 2, D7)
    ok = check(b.eval(f"{L}.k") == 0, "on the spot, at first: her own view")
    wait(2.6)
    v = b.eval(f"[{L}.k, {S}.shellAlpha[6], {S}.shellAlpha[7], {S}.cameras.main.midPoint.x - {S}.player.x, !!{S}.cameras.main._follow]")
    ok &= check(v[0] == 1 and v[1] == 0 and v[2] == 0 and v[3] > 150 and not v[4],
                "standing still: the camera out over the stage, decks 6 and 7 both open", v)
    b.key("left", True); wait(0.3); b.key("left", False)
    wait(1.2)
    v = b.eval(f"[{L}.k, {S}.shellAlpha[6], JSON.stringify({S}.world.lookOpen), !!{S}.cameras.main._follow]")
    ok &= check(v[0] == 0 and v[1] == 1 and v[2] == "{}" and v[3], "a step: back to her, deck 6 closed, the follow hers", v)
    # Over the rail: both open all the way down.
    b.teleport(x - 2, D7)
    wait(0.2)
    b.key("right", True); b.key("space", True)
    seen = []
    for _ in range(20):
        wait(0.05)
        seen.append(b.eval(f"[{S}.player.x > {L}.def.drop.x0 && {S}.player.y > {D7} + 20 && {S}.player.y < {D6} - 20, {S}.shellAlpha[6], {S}.shellAlpha[7]]"))
        if len(seen) == 6:
            b.key("space", False)
    b.key("right", False); b.key("space", False)
    falling = [q for q in seen if q[0]]
    ok &= check(falling and all(q[1] == 0 and q[2] == 0 for q in falling), "falling to the stage: both decks open the whole way", falling)
    wait(1.5)
    v = b.eval(f"[{S}.player.y, JSON.stringify({S}.world.lookOpen), {S}.shellAlpha[6], {S}.shellAlpha[7]]")
    ok &= check(v[0] == D6 and v[1] == "{}" and v[2] == 0 and v[3] == 1, "landed: the stage hers, deck 7 closed again", v)
    return ok


def scenario_region6__deck(b):
    """Near-catch 5 from the deck between the pools (docs/pool-remake-log.md): she dives at him, he hops over her dive,
    and she is in the pool under him; the scene goes on from there as from the water."""
    S, W = "window.__ship", "window.__ship.world"
    b.open("?reset&play&at=pool&cards=all")
    wait(0.4)
    L = js(b, f"{W}.data.lido")
    rim = L["pools"][0]["x1"]
    b.eval(f"{W}.story.poolCat.gone = true")
    b.teleport(L["leverX"] + 40, D11)
    b.eval(f"{W}.story.poolCat.gone = false")
    ok = check(wait_js(b, f"{S}.mode === 'scripted'", 2), "on the deck beside him: the scene starts")
    ok &= check(wait_js(b, f"{S}.player.depth === {S}.DEPTH.swimmer && {S}.player.x < {rim}", 5), "her dive at him ends in the pool", b.state())
    ok &= check(wait_js(b, f"{W}.story.poolCat.sprite.y === {D11} && Math.abs({S}.player.x - {rim - 23}) < 2", 4),
                "he is back at the rim where he sat, she in the water under him", b.state())
    ok &= check(wait_js(b, f"{S}.save.flags.includes('bb5')", 14) and b.state()["mode"] == "swim", "and the rest as from the water: she is swimming as the pool drains", b.state())
    ok &= check(wait_js(b, f"{S}.mode === 'play' && {S}.player.y === {D11 + 32}", 8), "the water gone, she stands in the empty tank", b.state())
    return ok


def scenario_region6__lookout(b):
    """Look-out 5 (the user, 2026-11-23): at the Great Outdoors' stern rail, half a second standing still zooms the camera
    out aft to the stern's half of the ship and the sea past it, every deck closed as from outside; a step and it is back
    with her, at play's zoom, its bounds as they were."""
    S = "window.__ship"
    L = f"{S}.world.movers.find(m => m.def?.id === 'look_outdoors')"
    b.open("?reset&play&at=diner")
    wait(0.4)
    x = b.eval(f"{L}.def.x")
    b.teleport(x, D11)
    ok = check(b.eval(f"{S}.cameras.main.zoom") == 2, "on the spot, at first: play's zoom")
    wait(2.8)
    v = b.eval(f"[{L}.k, {S}.cameras.main.zoom, {S}.cameras.main.worldView.x, {S}.cameras.main.worldView.right, {S}.viewDeck, {S}.cameras.main.useBounds]")
    x0, x1 = b.eval(f"{L}.def.frame")
    ok &= check(v[0] == 1 and v[1] < 0.2 and abs(v[2] - x0) < 2 and abs(v[3] - x1) < 2 and v[4] is None and not v[5],
                "standing still: zoomed out to its frame, every deck closed", v)
    b.key("left", True); wait(0.3); b.key("left", False)
    wait(1.2)
    v = b.eval(f"[{L}.k, {S}.cameras.main.zoom, !!{S}.cameras.main._follow, {S}.cameras.main.useBounds, {S}.world.lookFar]")
    ok &= check(v == [0, 2, True, True, 0], "a step: back with her, play's zoom and bounds", v)
    return ok


def scenario_region9__lookout(b):
    """Look-out 4 (the user, 2026-11-23): at the Spinnaker's balcony's forward end (from the windscreen to the first
    palm), half a second standing still zooms the camera out forward over the bow (look-out 5's mirror), every deck
    closed; walking off the spot and it is back with her."""
    S = "window.__ship"
    L = f"{S}.world.movers.find(m => m.def?.id === 'look_spinnaker')"
    b.open("?reset&play&cards=all&at=spinnaker")
    wait(0.4)
    x, reach = b.eval(f"[{L}.def.x, {L}.def.reach]")
    b.teleport(x + reach + 40, D12)
    wait(0.3)
    ok = check(b.eval(f"{S}.cameras.main.zoom") == 2, "on the balcony, at first: play's zoom")
    # (Walked into the windscreen, as the user stood: the spot reaches it.)
    hold_until(b, "left", lambda s: False, timeout=2.5)
    wait(2.8)
    v = b.eval(f"[{L}.k, {S}.cameras.main.zoom, {S}.cameras.main.worldView.x, {S}.cameras.main.worldView.right, {S}.viewDeck, {S}.cameras.main.useBounds]")
    x0, x1 = b.eval(f"{L}.def.frame")
    ok &= check(v[0] == 1 and v[1] < 0.2 and abs(v[2] - x0) < 2 and abs(v[3] - x1) < 2 and v[4] is None and not v[5],
                "against the windscreen, still: zoomed out forward over the bow, every deck closed", v)
    hold_until(b, "right", lambda s: s["x"] > x + reach + 8)
    wait(1.2)
    v = b.eval(f"[{L}.k, {S}.cameras.main.zoom, !!{S}.cameras.main._follow, {S}.cameras.main.useBounds, {S}.world.lookFar]")
    ok &= check(v == [0, 2, True, True, 0], "off the spot: back with her, play's zoom and bounds", v)
    return ok


def scenario_deck4__porthole(b):
    """Look-out 2 (the user, 2026-11-23): deck 4's aft porthole by E: she turns her back to us at it, and the outside
    view (O) shows; a movement key brings the camera back to her."""
    S = "window.__ship"
    b.open("?reset&play&at=wake4")
    wait(0.4)
    x = b.eval(f"{S}.world.things.find(t => t.id === 'look_wake').x")
    b.teleport(x - 10, D4)
    wait(0.3)
    b.tap("e")
    wait(0.2)
    v = b.eval(f"[{S}.player.frame.name, {S}.herFrames.back, {S}.player.x]")
    ok = check(v[0] == v[1] and v[2] == x, "E: she steps to the porthole and turns her back to us", v)
    wait(0.6)
    ok &= check(b.eval(f"!!{S}.overview?.porthole"), "the outside view shows")
    b.key("right", True); wait(0.2); b.key("right", False)
    wait(0.3)
    v = b.eval(f"[!!{S}.overview, {S}.mode, !!{S}.cameras.main._follow]")
    ok &= check(not v[0] and v[1] == "play" and v[2], "a movement key: back with her", v)
    return ok


SCENARIOS = {name[len("scenario_"):].replace("__", "."): fn for name, fn in globals().items() if name.startswith("scenario_")}


def expand(names):
    """Each name as asked, or a scenario's name standing for itself and all its cases."""
    out = []
    for n in names:
        group = [k for k in SCENARIOS if k == n or k.startswith(n + ".")] or [n]
        out += [k for k in group if k not in out]
    return out


# Run in real time whatever the flag (docs/plan-fast-tests.md §3.3): the sound keeps the audio
# context's own clock, and `boot` is the proof that the game's own loop still runs.
REAL_TIME = {"sound", "boot"}
LAST = OUT / "last.json"       # the last run: what failed, and every scenario's time


def load_last():
    try:
        return json.loads(LAST.read_text(encoding="utf-8"))
    except Exception:
        return {"failed": [], "times": {}}


def save_last(results, real):
    last = load_last()
    last["failed"] = [n for n, (ok, _) in results.items() if not ok]
    for n, (_, secs) in results.items():
        last["times"][n + (" (real)" if real or n in REAL_TIME else "")] = round(secs, 1)
    OUT.mkdir(exist_ok=True)
    LAST.write_text(json.dumps(last, indent=1), encoding="utf-8")


def clean_leftovers():
    """Closes every test browser whose starting process is gone, and removes the profile folder of
    every test browser that is not running (docs/plan-fast-tests.md §3.4)."""
    import psutil
    norm = lambda d: os.path.normcase(os.path.abspath(d))
    used, closed = set(), 0
    for proc in psutil.process_iter(["name", "cmdline", "ppid"]):
        try:
            if not (proc.info["name"] or "").lower().startswith("chrome"):
                continue
            cmd = proc.info["cmdline"] or []
            prof = next((a.split("=", 1)[1] for a in cmd if a.startswith("--user-data-dir=") and "bumbusik-chrome-" in a), None)
            if not prof:
                continue
            if any(a.startswith("--type=") for a in cmd) or psutil.pid_exists(proc.info["ppid"]):
                used.add(norm(prof))     # (a browser's helper, or a browser whose test still runs)
                continue
            for c in proc.children(recursive=True):
                c.kill()
            proc.kill()
            closed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    gone = 0
    for d in Path(tempfile.gettempdir()).glob("bumbusik-chrome-*"):
        if d.is_dir() and norm(d) not in used:
            shutil.rmtree(d, ignore_errors=True)
            gone += 1
    if closed or gone:
        print(f"(leftover test browsers closed: {closed}; profile folders removed: {gone})")


def run_here(names, real):
    """The scenarios one after another, in this process, one browser."""
    b = Browser()
    results = {}
    try:
        for name in names:
            b.stepped = not real and name not in REAL_TIME
            t0, errors = time.time(), len(b.errors)
            print(name + ("" if b.stepped else "  (real time)"), flush=True)
            try:
                ok = SCENARIOS[name](b)
            except Exception as e:
                ok = False
                print(f"  FAIL  {type(e).__name__}: {e}")
            if len(b.errors) > errors:
                ok = False
                print("  console errors:")
                for e in dict.fromkeys(b.errors[errors:]):
                    print("    ", e)
            results[name] = (bool(ok), time.time() - t0)
            print(f"  ({results[name][1]:.1f} s)", flush=True)
    finally:
        b.close()
    return results


def run_parallel(names, jobs, real):
    """A process and a browser for each scenario, `jobs` at a time; the output of each printed
    whole, in the order asked."""
    def one(name):
        t0 = time.time()
        r = subprocess.run([sys.executable, __file__, "--child", "--seed", str(SEED[0])] + (["--real"] if real else []) + [name],
                           capture_output=True, text=True, errors="replace", cwd=str(ROOT))
        lines = [l for l in (r.stdout + r.stderr).splitlines() if not l.startswith(("screenshots:", "PASS", "FAILED"))]
        return name, "\n".join(lines), r.returncode == 0, time.time() - t0

    results, done, shown = {}, {}, 0
    with concurrent.futures.ThreadPoolExecutor(jobs) as pool:
        for fut in concurrent.futures.as_completed([pool.submit(one, n) for n in names]):
            name, text, ok, secs = fut.result()
            done[name] = (text, ok, secs)
            while shown < len(names) and names[shown] in done:
                text, ok, secs = done[names[shown]]
                print(text, flush=True)
                results[names[shown]] = (ok, secs)
                shown += 1
    return results


def main():
    sys.stdout.reconfigure(errors="replace")  # the Windows console can't print every emoji
    args = sys.argv[1:]
    real, child = "--real" in args, "--child" in args
    if "--seed" in args:
        SEED[0] = int(args[args.index("--seed") + 1])
    jobs = int(args[args.index("-j") + 1]) if "-j" in args else 1
    names = [a for i, a in enumerate(args) if not a.startswith("-") and not (i and args[i - 1] in ("-j", "--seed"))]
    if "--times" in args:
        times = load_last()["times"]
        for n, secs in sorted(times.items(), key=lambda kv: -kv[1]):
            print(f"{secs:8.1f} s  {n}")
        print(f"{sum(times.values()):8.1f} s  in all, one after another")
        return
    if "--failed" in args:
        names = load_last()["failed"]
        if not names:
            print("nothing failed in the last run")
            return
    names = expand(names) if names else list(SCENARIOS)
    unknown = [n for n in names if n not in SCENARIOS]
    if unknown:
        print("no such scenario:", ", ".join(unknown))
        sys.exit(2)
    if not child:
        clean_leftovers()
    t0 = time.time()
    results = run_parallel(names, jobs, real) if jobs > 1 and len(names) > 1 else run_here(names, real)
    all_ok = all(ok for ok, _ in results.values())
    if not child:
        save_last(results, real)
        failed = [n for n, (ok, _) in results.items() if not ok]
        if len(names) > 1:
            print(f"{len(names)} scenarios in {time.time() - t0:.1f} s" + (f"; failed: {', '.join(failed)}" if failed else ""))
    print("screenshots:", OUT)
    print("PASS" if all_ok else "FAILED")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
