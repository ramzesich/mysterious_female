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
    f = b.eval("(f => [f.x0, f.x1, f.y])(window.__ship.world.data.funnel)")
    shots = []
    for name, x in (("fwd", f[0] + 30), ("mid", (f[0] + f[1]) // 2), ("box", f[1] - 230)):
        b.teleport(x, f[2]); b.wait(1.2); im = snap(b); im.save(os.path.join(OUT, f"after-{name}.png")); shots.append(im)
    b.teleport(f[1] - 60, f[2]); b.wait(1.0); b.hold("right", 1.0); b.wait(0.5)
    print("stopped at", b.eval("window.__ship.player.x"), "post", f[1] - 2)
    im = snap(b); im.save(os.path.join(OUT, "after-end.png")); shots.append(im)
    vx = b.eval("window.__ship.cameras.main.worldView.x"); vy = b.eval("window.__ship.cameras.main.worldView.y")
    cx, cy = int(f[1] - vx), int(f[2] - vy)
    im.crop((cx - 90, cy - 80, cx + 30, cy + 10)).resize((480, 360), Image.NEAREST).save(os.path.join(OUT, "after-end-x4.png"))
    w, h = shots[0].size
    s = Image.new("RGB", (w * 2 + 4, h * 2 + 4), "white")
    for i, im in enumerate(shots): s.paste(im, ((i % 2) * (w + 4), (i // 2) * (h + 4)))
    s.save(os.path.join(OUT, "after-sheet.png"))
    print("errors", b.errors)
finally:
    b.close()
