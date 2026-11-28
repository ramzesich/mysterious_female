"""Option B (the user, 2026-11-28): ↓ in the reading row shows the chosen book's cover as when it was got, the row
hidden; a direction or Esc brings the row back with the same book chosen. Driven with real keys; shots of each step."""
import sys, io, base64, os, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
L = "window.__ship.world.library"
def st(b):
    return json.loads(b.eval(f"JSON.stringify({{choosing: !!{L}.choosing, at: {L}.choosing && {L}.choosing.at, viewing: !!window.__ship.viewing, reading: {L}.reading}})"))
b = P.Browser(stepped=True)
try:
    b.open("?play&at=library&books=all", start=None); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false; window.__skipCloseups = false")
    c = b.eval("(t => [t.x, t.y])(window.__ship.world.things.find(t => t.id === 'sec_chair'))")
    b.teleport(c[0], c[1]); b.wait(0.6)
    b.tap("e"); b.wait(2.5); print("row      ", st(b))
    b.tap("left"); b.wait(0.3); print("left     ", st(b))
    b.tap("down"); b.wait(0.6); print("down     ", st(b)); snap(b).save(os.path.join(OUT, "b-cover.png"))
    b.tap("right"); b.wait(0.6); print("right    ", st(b)); snap(b).save(os.path.join(OUT, "b-back.png"))
    b.tap("down"); b.wait(0.6); print("down     ", st(b))
    b.tap("escape"); b.wait(0.6); print("escape   ", st(b))
    b.tap("e"); b.wait(2.0); print("e (read) ", st(b))
    print("errors", b.errors)
finally:
    b.close()
