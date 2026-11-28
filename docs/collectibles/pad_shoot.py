"""Her massage pad (2026-11-28) on the theatre seat, in the diary's place: the game's view and the seat enlarged."""
import sys, io, base64, os, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
S = "window.__ship"
b = P.Browser(stepped=True)
try:
    b.open("?play&at=theatre", start=None); b.wait(1.0)
    b.eval(f"{S}.scareContact = () => false")
    T = f"{S}.world.things.find(t => t.id === 'keep_pad')"
    t = json.loads(b.eval(f"JSON.stringify((t => ({{x: t.x, y: t.y, route: t.route, b: (r => [r.x, r.y, r.width, r.height])(t.pick.getBounds())}}))({T}))"))
    b.teleport(t["x"] - 40, t["y"], t["route"]); b.wait(1.5)
    b.eval(f"{T}.pick.glintOff = true")
    cam = json.loads(b.eval(f"JSON.stringify([{S}.cameras.main.worldView.x, {S}.cameras.main.worldView.y])"))
    b.eval(f"window.__snap = null; {S}.game.renderer.snapshot(img => {{ window.__snap = img.src; }})")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    im = im.resize((im.width // 2, im.height // 2), Image.NEAREST); im.save(os.path.join(OUT, "pad-seat.png"))
    x, y = t["b"][0] - cam[0] + t["b"][2] / 2, t["b"][1] - cam[1] + t["b"][3] / 2
    c = im.crop((int(x - 60), int(y - 50), int(x + 40), int(y + 20))); c.resize((c.width * 5, c.height * 5), Image.NEAREST).save(os.path.join(OUT, "pad-seat-x5.png"))
    print(t, "errors", b.errors)
finally:
    b.close()
