"""Bumbot's massage gun remade (2026-11-28): the masseur's toss frame by frame and its close-up, in the running game."""
import sys, io, base64, os, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
S = "window.__ship"; W = f"{S}.world"; M = f"{W}.people.byId.amb_masseur"
def snap(b):
    b.eval(f"window.__snap = null; {S}.game.renderer.snapshot(img => {{ window.__snap = img.src; }})")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
b = P.Browser(stepped=True)
try:
    b.open("?reset&play&at=spa", start=None); b.wait(0.4)
    b.eval(f"{S}.scareContact = () => false; window.__skipCloseups = false")
    home = b.eval(f"{W}.story.spaTable().x")
    fy = b.eval(f"{S}.player.y")
    b.teleport(home - 30, fy); b.wait(0.3)
    b.tap("e")
    deadline = 120
    t = 0
    while t < deadline and "toss" not in (b.eval(f"{M}.sprite.anims.currentAnim?.key") or ""):
        b.wait(0.05); t += 0.05
    frames = []
    for i in range(16):
        cam = json.loads(b.eval(f"JSON.stringify([{S}.cameras.main.worldView.x, {S}.cameras.main.worldView.y, {M}.sprite.x, {M}.sprite.y])"))
        im = snap(b)
        x, y = cam[2] - cam[0], cam[3] - cam[1]
        frames.append(im.crop((int(x - 70), int(y - 80), int(x + 110), int(y + 10))))
        b.wait(0.06)
    strip = Image.new("RGB", (180 * 8, 90 * 2))
    for i, f in enumerate(frames): strip.paste(f, ((i % 8) * 180, (i // 8) * 90))
    strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST).save(os.path.join(OUT, "gun-toss.png"))
    b.wait_for(f"{S}.viewing", timeout=10); b.wait(0.5)
    snap(b).save(os.path.join(OUT, "gun-closeup.png"))
    print("errors", b.errors)
finally:
    b.close()
