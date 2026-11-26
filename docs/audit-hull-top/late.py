import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
def snap(b, half=True):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST) if half else im
# intro
b = P.Browser(stepped=True)
try:
    b.open("?intro=focus", start=None)
    b.wait(2.0)
    for part, k in [("right", 0.0), ("right", 0.35), ("right", 0.7), ("right", 1.0), ("ship", 0.5), ("dive", 0.15), ("dive", 0.35)]:
        ok = b.eval(f"window.__ship.intro.seek('{part}', {k})")
        b.wait(0.3)
        im = snap(b, half=False); im.save(os.path.join(OUT, f"in-{part}-{int(k*100)}.png")); print(part, k, ok, im.size)
finally:
    b.close()
# dusk in play
b = P.Browser(stepped=True)
try:
    b.open("?play&at=deck12&cards=all")
    b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    b.eval("window.__ship.setDusk(1)")
    for p in ["deck12", "court", "terrace", "stairway", "funnel", "spinnaker"]:
        b.eval(f"window.__ship.spawnAt(window.__ship.places['{p}'])")
        b.wait(2.0)
        im = snap(b); im.save(os.path.join(OUT, f"d-{p}.png")); print(p)
    print("errors", b.errors)
finally:
    b.close()
