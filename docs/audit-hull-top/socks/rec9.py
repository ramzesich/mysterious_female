# Finding 9: the funnel's windsocks recorded through one whole gust round (5 s, 10 frames a second), as GIFs.
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
def crop(b, im, wx, wy, w, h, k):
    v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
    x, y = int(wx - v[0]), int(wy - v[1])
    return im.crop((x, y, x + w, y + h)).resize((w * k, h * k), Image.NEAREST)
GUSTS = "window.__ship.world.movers.find(m => m.flappers && m.flappers.length === 3 && !m.F)"
def phase(b): return b.eval(f"(g => g.phase(window.__ship.time.now))({GUSTS})")
def record(b, name, box, k=2):
    for _ in range(400):            # from the start of a lull
        if phase(b) != "calm": break
        b.wait(0.05)
    for _ in range(400):
        if phase(b) == "calm": break
        b.wait(0.05)
    frames = []
    for i in range(52):
        frames.append((crop(b, snap(b), *box, k), phase(b)))
        b.wait(0.1 - 1/60)
    frames[0][0].save(os.path.join(OUT, f"{name}.gif"), save_all=True, append_images=[f for f, _ in frames[1:]], duration=100, loop=0)
    pick = frames[::4]
    w, h = pick[0][0].size
    s = Image.new("RGB", (w * len(pick) // 2 + 2 * len(pick), h * 2 + 4), "white")
    for i, (f, _) in enumerate(pick): s.paste(f, ((i % (len(pick) // 2 + len(pick) % 2)) * (w + 2), (i // (len(pick) // 2 + len(pick) % 2)) * (h + 4)))
    s.save(os.path.join(OUT, f"{name}-strip.png"))
    print(name, " ".join(p[0] for _, p in frames))
b = P.Browser(stepped=True)
try:
    b.open("?play&at=stairway"); b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    print("her", b.eval("[window.__ship.player.x, window.__ship.player.y]"))
    record(b, "rec-stairway", (8470, 95, 230, 185))
    b.open("?play&at=funnel"); b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    b.teleport(9690, -228); b.wait(1.0)
    record(b, "rec-top", (9680, -320, 120, 100))
    print("errors", b.errors)
finally:
    b.close()
