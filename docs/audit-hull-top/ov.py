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
    return im
b = P.Browser(stepped=True)
try:
    b.open("?play&at=deck12")
    b.wait(1.0)
    for dusk in (0, 1):
        b.eval(f"window.__ship.setDusk({dusk})")
        b.eval("(() => { const s = window.__ship; if (!s.overview) s.enterOverview(); s.uiLayer.setVisible(false); })()")
        b.wait(1.0)
        im = snap(b); im.save(os.path.join(OUT, f"ov-fit-{dusk}.png")); print("fit", im.size)
        # Zoom 1 strips across the top, from above the world's top
        b.eval("window.__ship.cameras.main.setZoom(1)")
        vw, vh = b.eval("[window.__ship.cameras.main.width, window.__ship.cameras.main.height]")
        W = b.eval("window.__ship.map.widthInPixels")
        strip = Image.new("RGB", (W, 700))
        for x in range(0, W, int(vw)):
            b.eval(f"window.__ship.cameras.main.setScroll({x}, -300)")
            b.wait(0.25)
            im = snap(b)
            im = im.resize((int(vw), int(vh)), Image.NEAREST) if im.width != int(vw) else im
            strip.paste(im.crop((0, 0, int(vw), 700)), (x, 0))
        strip.save(os.path.join(OUT, f"strip-{dusk}.png")); print("strip", vw, vh)
        b.eval("window.__ship.leaveOverview()")
        b.wait(0.5)
    print("errors", b.errors)
finally:
    b.close()
