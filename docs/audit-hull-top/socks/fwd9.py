# Finding 9: the stairway foot's windsock forward of where she stood on the user's screenshot (x about 8420), in a lull
# and a gust, the game's full view.
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
G = "window.__ship.world.movers.find(m => m.flappers && m.flappers.length === 3 && !m.F)"
ph = lambda b: b.eval(f"(g => g.phase(window.__ship.time.now))({G})")
def until(b, p):
    for _ in range(400):
        if ph(b) == p: return
        b.wait(0.05)
b = P.Browser(stepped=True)
try:
    b.open("?play&at=stairway"); b.wait(1.5); b.eval("window.__ship.scareContact = () => false")
    for _ in range(60):
        if b.eval("window.__ship.player.x") <= 8422: break
        b.hold("left", 0.05)
    b.wait(0.8)
    print("her", b.eval("[window.__ship.player.x, window.__ship.player.y]"))
    ims = []
    for p in ("calm", "blow"):
        until(b, "tell" if p == "calm" else "calm"); until(b, p); b.wait(0.4)
        ims.append(snap(b))
    w, h = ims[0].size
    s = Image.new("RGB", (w * 2 + 6, h), "white"); s.paste(ims[0], (0, 0)); s.paste(ims[1], (w + 6, 0))
    s.save(os.path.join(OUT, "forward.png"))
    v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
    x, y = int(8330 - v[0]), int(190 - v[1])
    s2 = Image.new("RGB", (2 * 3 * 160 + 6, 3 * 95), "white")
    for i, im in enumerate(ims): s2.paste(im.crop((x, y, x + 160, y + 95)).resize((480, 285), Image.NEAREST), (i * 486, 0))
    s2.save(os.path.join(OUT, "forward-x3.png"))
    print("errors", b.errors)
finally:
    b.close()
