"""Her Albuca (2026-11-28) in place: the maid's cabin, up high; she beside the bed it is taken from."""
import sys, io, base64, os, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
S = "window.__ship"
b = P.Browser(stepped=True)
try:
    b.open("?play&at=maid6", start=None); b.wait(1.5)
    b.eval(f"{S}.scareContact = () => false")
    t = json.loads(b.eval(f"JSON.stringify((t => ({{x: t.x, y: t.y, route: t.route, b: (r => [r.x, r.y, r.width, r.height])(t.pick.getBounds())}}))({S}.world.things.find(t => t.id === 'keep_plant')))"))
    b.teleport(t["x"] - 40, t["y"], t["route"]); b.wait(1.5)
    cam = json.loads(b.eval(f"JSON.stringify([{S}.cameras.main.worldView.x, {S}.cameras.main.worldView.y])"))
    b.eval(f"window.__snap = null; {S}.game.renderer.snapshot(img => {{ window.__snap = img.src; }})")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    im = im.resize((im.width//2, im.height//2), Image.NEAREST); im.save(os.path.join(OUT, "plant-maid.png"))
    x, y = t["b"][0] - cam[0] + t["b"][2] / 2, t["b"][1] - cam[1] + t["b"][3] / 2
    c = im.crop((int(x - 70), int(y - 30), int(x + 50), int(y + 70))); c.resize((c.width * 4, c.height * 4), Image.NEAREST).save(os.path.join(OUT, "plant-maid-x4.png"))
    print(t, "errors", b.errors)
finally:
    b.close()
