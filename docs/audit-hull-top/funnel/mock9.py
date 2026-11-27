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
b = P.Browser(stepped=True)
try:
    b.open("?play&at=funnel")
    b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    # A: an end post on both rails at the deck's very end (as every other post), her stop moved 8 px inboard
    b.eval("""(() => { const s = window.__ship, D = s.DEPTH, f = s.world.data.funnel;
      const back = s.add.graphics().setDepth(D.exterior + 0.07), front = s.add.graphics().setDepth(D.player + 0.3);
      for (const g of [back, front]) { const top = g === back ? f.y - 34 : f.y - 30;
        g.fillStyle(0xe8eaec, 1).fillRect(f.x1 - 2, top, 2, f.y - top + (g === front ? 1 : 0)); }
      s.world.add([back, front]);
      const z = s.railingStops[s.railingStops.length - 1]; z.x -= 8; z.body.updateFromGameObject(); })()""")
    f = b.eval("(f => [f.x0, f.x1, f.y])(window.__ship.world.data.funnel)")
    b.teleport(f[1] - 60, f[2]); b.wait(1.0)
    b.hold("right", 1.0); b.wait(0.5)
    print("stopped at", b.eval("window.__ship.player.x"))
    im = snap(b); im.save(os.path.join(OUT, "mock-a.png"))
    vx = b.eval("window.__ship.cameras.main.worldView.x"); vy = b.eval("window.__ship.cameras.main.worldView.y")
    cx, cy = int(f[1] - vx), int(f[2] - vy)
    im.crop((cx - 90, cy - 80, cx + 30, cy + 10)).resize((480, 360), Image.NEAREST).save(os.path.join(OUT, "mock-a-x4.png"))
    b.close(); b = P.Browser(stepped=True)
    b.open("?play&at=funnel"); b.wait(1.5); b.eval("window.__ship.scareContact = () => false")
    b.teleport(f[1] - 60, f[2]); b.wait(1.0); b.hold("right", 1.0); b.wait(0.5)
    im = snap(b)
    vx = b.eval("window.__ship.cameras.main.worldView.x"); vy = b.eval("window.__ship.cameras.main.worldView.y")
    cx, cy = int(f[1] - vx), int(f[2] - vy)
    im.crop((cx - 90, cy - 80, cx + 30, cy + 10)).resize((480, 360), Image.NEAREST).save(os.path.join(OUT, "now-x4.png"))
    print("errors", b.errors)
finally:
    b.close()
