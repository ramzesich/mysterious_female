"""The throw's hint (the user, 2026-11-28): the first tangerine she picks up, keyboard and controller; the second none."""
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
S = "window.__ship"
NEAR = f"(() => {{ const p = {S}.player; return {S}.tangerines.filter(t => t.sprite.active && t.route === {S}.route).sort((a, b) => Math.abs(a.sprite.x - p.x) + Math.abs(a.sprite.y - p.y) - Math.abs(b.sprite.x - p.x) - Math.abs(b.sprite.y - p.y)).map(t => [t.sprite.x, t.sprite.y])[0]; }})()"
def take(b):
    x, y = b.eval(NEAR)
    b.teleport(x, y + 2); b.wait(0.4)
for name, pad in (("keys", False), ("pad", True)):
    b = P.Browser(stepped=True)
    try:
        if pad: b.fake_pad()
        b.open("?play&at=deck4", start=None); b.wait(1.0)
        b.eval(f"{S}.scareContact = () => false")
        if pad: b.pad_tap("A"); b.wait(1.0)
        take(b)
        print(name, b.eval(f"JSON.stringify([{S}.save.tangerines, {S}.alert.visible, {S}.alert.text, {S}.progress.has('hint_throw')])"))
        snap(b).save(os.path.join(OUT, f"hint-{name}.png"))
        if not pad:
            b.wait(4.0); take(b)
            print("second", b.eval(f"JSON.stringify([{S}.save.tangerines, {S}.alert.visible && {S}.alert.text])"))
        print("errors", b.errors)
    finally:
        b.close()
