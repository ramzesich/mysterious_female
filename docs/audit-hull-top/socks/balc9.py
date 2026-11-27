# Finding 9: the Spinnaker balcony's windsock moved left (the user, 2026-11-27: "Move it a little bit to the left"):
# a few places mocked in the running game (pole and sock moved in the page), each in a lull and in a gust.
import sys, io, base64, os
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
BOW = "window.__ship.world.movers.find(m => m.flappers && m.F)"
ph = lambda b: b.eval(f"(g => g.phase(window.__ship.time.now))({BOW})")
def until(b, p):
    for _ in range(400):
        if ph(b) == p: return
        b.wait(0.05)
b = P.Browser(stepped=True)
try:
    b.open("?play&at=bow&did=alarm"); b.wait(1.5); b.eval("window.__ship.scareContact = () => false")
    b.teleport(600, 1136); b.wait(1.0)
    b.eval("(c => { c.stopFollow(); c.centerOn(1700, 520); })(window.__ship.cameras.main)"); b.wait(0.5)
    tiles = []
    for dx in (0, -15, -30, -52):
        b.eval(f"(f => {{ f.pole.x = 1685 + {dx}; f.img.x = 1685 + {dx}; }})(({BOW}).flappers[0])")
        row = []
        for p in ("calm", "blow"):
            until(b, "tell" if p == "calm" else "calm"); until(b, p); b.wait(0.4)
            im = snap(b); v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
            x, y = int(1590 - v[0]), int(470 - v[1])
            row.append(im.crop((x, y, x + 160, y + 100)).resize((480, 300), Image.NEAREST))
        tiles.append(row)
    s = Image.new("RGB", (2 * 486, len(tiles) * 306), "white")
    for r, row in enumerate(tiles):
        for c, t in enumerate(row): s.paste(t, (c * 486, r * 306))
    s.save(os.path.join(OUT, "balcony-left.png"))
    print("errors", b.errors)
finally:
    b.close()
