import sys, io, base64, os, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__)); TAG = sys.argv[1]
PLACES = ["balcony", "occupied8", "mask10", "gull9", "cabin", "maid6", "crew", "deck4", "deck5", "home", "steward", "officers10", "deck12", "pool"]
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    return Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
STATE = "(() => { const s = window.__ship; return {route: s.route, mode: s.mode, viewDeck: s.viewDeck, dim: +s.deckDim.shown.toFixed(3), shell: s.shellAlpha, under: s.poolsHidden}; })()"
state = {}
b = P.Browser(stepped=True)
try:
    b.open("?play&cards=all"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false; window.__ship.time.timeScale = 0")
    for n in PLACES:
        b.eval(f"window.__ship.spawnAt(window.__ship.places['{n}'])"); b.wait(3)
        state[n] = b.eval(STATE); snap(b).save(os.path.join(OUT, f"{TAG}-{n}.png"))
    # the outside view (O), as the user opens it
    b.eval("window.__ship.spawnAt(window.__ship.places['deck5'])"); b.wait(2)
    b.eval("(() => { const s = window.__ship; s.enterOverview(true); })()"); b.wait(1)
    state["outside"] = b.eval(STATE); snap(b).save(os.path.join(OUT, f"{TAG}-outside.png"))
    b.eval("window.__ship.leaveOverview()"); b.wait(1)
    # the pools: into the water and out again, the states along the way
    seq = []
    for name, x, y in [("kids", 3380, 416), ("oasis", 6480, 560)]:
        b.teleport(x, y, "inside")
        for i in range(8):
            b.wait(0.25); seq.append([name, i, b.eval(STATE)])
    state["pools"] = seq
    json.dump(state, open(os.path.join(OUT, f"{TAG}-state.json"), "w"), indent=1)
    print("errors", b.errors[:3])
finally:
    b.close()
