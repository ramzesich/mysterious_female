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
SPOTS = ["promenade", "walkway", "balcony", "bow", "stern", "pool", "diner", "terrace", "stairway", "funnel", "balcony7"]
b = P.Browser(stepped=True)
shots = []
try:
    b.open("?play&cards=all"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    for n in SPOTS:
        b.eval(f"window.__ship.spawnAt(window.__ship.places['{n}'])"); b.wait(3.0)
        st = b.eval("(() => { const s = window.__ship; return [s.route, s.mode, s.viewDeck, +s.deckDim.shown.toFixed(2), +(s.roomDim?.alpha ?? -1).toFixed?.(2) ?? null]; })()")
        im = snap(b); shots.append((n, st, im)); print(n, st)
    W = 480; sh = Image.new("RGB", (W * 3, 270 * 4))
    for i, (n, st, im) in enumerate(shots):
        d = ImageDraw.Draw(im); lab = f"{n}: dim {'ON' if st[3] > 0.5 else 'off'} ({st[0]})"
        d.rectangle((0, 0, 8 + 6 * len(lab), 14), fill=0); d.text((4, 2), lab, fill=(255, 230, 0))
        sh.paste(im, ((i % 3) * W, (i // 3) * 270))
    sh.save(os.path.join(OUT, "spots.png"))
finally:
    b.close()
