import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sweep"); TAG = sys.argv[1]
def snap(b, half=False):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST) if half else im
STATES = {"start": "", "mid": "&did=bb1,bb2,bb3,bb4,bb5,table,engineer,horn,lady,wedding", "end": "&did=bb1,bb2,bb3,bb4,bb5,bb6,table,engineer,horn,lady,wedding,alarm,sunset,catch"}
for st, did in STATES.items():
    b = P.Browser(stepped=True)
    try:
        b.open("?play&cards=all" + did); b.wait(1.5)
        b.eval("window.__ship.scareContact = () => false; window.__ship.time.timeScale = 0")
        # 1. The outside view at 1:1 along deck 12's band (y 330 to 440), the whole length.
        b.eval("(() => { const s = window.__ship; s.enterOverview(true); s.uiLayer.setVisible(false); s.cameras.main.setZoom(1); })()"); b.wait(0.5)
        vw = int(b.eval("window.__ship.cameras.main.width")); W = b.eval("window.__ship.map.widthInPixels")
        strip = Image.new("RGB", (W, 140))
        for x in range(0, W, vw):
            b.eval(f"window.__ship.cameras.main.setScroll({x}, 320)"); b.wait(0.05)
            im = snap(b); strip.paste(im.crop((0, 0, min(vw, W - x), 140)), (x, 0))
        strip.save(os.path.join(OUT, f"{TAG}-{st}-outside.png"))
        b.eval("window.__ship.leaveOverview()"); b.wait(0.5)
        # 2. In play from below: on deck 11 under each stretch of deck 12's glass, and inside deck 12's rooms.
        for n, x, y in [("d11-kids", 3400, 560), ("d11-sun", 5900, 560), ("d11-sun2", 6500, 560), ("d11-court", 7600, 560),
                        ("d11-cafe", 8800, 560), ("d11-go", 10700, 560), ("d11-go2", 10950, 560), ("d10-pool", 6500, 704),
                        ("d12-champs", 4600, 416), ("d12-bistro", 10300, 416)]:
            b.teleport(x, y, "inside"); b.wait(1.5)
            snap(b, half=True).save(os.path.join(OUT, f"{TAG}-{st}-{n}.png"))
        print(st, "errors", b.errors[:2])
    finally:
        b.close()
