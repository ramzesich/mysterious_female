# Finding 10: a layout mocked in the running game (the flocks' sprites moved and given poses in the page):
# the windscreen's six at uneven gaps in mixed poses and facings; the pool's six clear of the kid, his bucket and the
# slide: one on the forward rim, one on the slide's top, two on the splash mushroom's cap, two afloat (sitting).
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
SCREEN = [(2072, "look", 0), (2098, "perched", 1), (2121, "preen", 0), (2300, "doze", 1), (2441, "perched", 0), (2508, "sit", 1)]
POOL = [(3246, "look", 0, 416), (3521, "perched", 0, 373), (3577, "doze", 1, 356), (3597, "preen", 0, 356),
        (3345, "sit", 1, 420), (3420, "sit", 0, 420)]
LAY = """((id, lay) => { const f = window.__ship.world.story.flocks.find(f => f.def.id === id);
  f.birds.forEach((b, i) => { const [x, pose, flip, y] = lay[i]; b.sprite.setFrame('gull-' + pose).setFlipX(!!flip).setPosition(x, y ?? f.def.y); b.x = x; b.up = true; }); })"""
b = P.Browser(stepped=True)
try:
    b.open("?play&at=spinnaker"); b.wait(1.5); b.eval("window.__ship.scareContact = () => false")
    b.eval(f"{LAY}('gull_bow_b', {json.dumps(SCREEN)}); {LAY}('gull_bow_a', {json.dumps(POOL)})")
    shots = []
    for hx, x0, y0, w, h in ((2292, 2052, 280, 476, 50), (3425, 3225, 335, 400, 95)):
        b.teleport(hx, 416); b.wait(1.2)
        b.eval(f"{LAY}('gull_bow_b', {json.dumps(SCREEN)}); {LAY}('gull_bow_a', {json.dumps(POOL)})"); b.wait(0.1)
        im = snap(b); v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
        x, y = int(x0 - v[0]), int(y0 - v[1])
        shots.append(im.crop((x, y, x + w, y + h)).resize((w * 2, h * 2), Image.NEAREST))
        im.save(os.path.join(OUT, f"mock-{len(shots)}.png"))
    W = max(s.width for s in shots)
    s = Image.new("RGB", (W, sum(x.height + 6 for x in shots)), "white"); yy = 0
    for x in shots: s.paste(x, (0, yy)); yy += x.height + 6
    s.save(os.path.join(OUT, "mock-layout.png"))
    print("errors", b.errors)
finally:
    b.close()
