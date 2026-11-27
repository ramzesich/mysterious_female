# Finding 10: the kids' pool's rims with its flock hidden (what is free to stand on), 3x, with a ruler every 10 px.
import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image, ImageDraw
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
    b.open("?play&at=spinnaker"); b.wait(1.5); b.eval("window.__ship.scareContact = () => false")
    b.teleport(3385, 416); b.wait(1.2)
    b.eval("window.__ship.world.story.flocks.find(f => f.def.id === 'gull_bow_a').birds.forEach(x => x.sprite.setVisible(false))")
    b.wait(0.2)
    im = snap(b); v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
    x0, y0, w, h = 3220, 340, 360, 85
    x, y = int(x0 - v[0]), int(y0 - v[1])
    c = im.crop((x, y, x + w, y + h)).resize((w * 3, h * 3), Image.NEAREST)
    d = ImageDraw.Draw(c)
    for wx in range(x0, x0 + w, 10):
        d.line(((wx - x0) * 3, h * 3 - (12 if wx % 50 == 0 else 5), (wx - x0) * 3, h * 3), fill=(255, 0, 0))
        if wx % 50 == 0: d.text(((wx - x0) * 3 + 2, h * 3 - 24), str(wx), fill=(255, 0, 0))
    c.save(os.path.join(OUT, "rim-free.png"))
    print("errors", b.errors)
finally:
    b.close()
