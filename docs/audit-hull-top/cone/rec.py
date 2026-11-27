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
G = "window.__ship.world.foodGulls.gull_go"
def record(b, tag, secs, step=0.1, extra=None):
    frames = []
    t = 0.0
    while t < secs:
        im = snap(b); st = b.eval(f"{G}.state")
        frames.append((round(t, 1), st, im)); b.wait(step); t += step
    return frames
b = P.Browser(stepped=True)
try:
    b.open("?play&at=icecream"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    print("her", b.eval("[Math.round(window.__ship.player.x), Math.round(window.__ship.player.y)]"), "gull", b.eval(f"[{G}.diver.x, {G}.diver.y, {G}.state]"))
    L = b.eval("window.__ship.world.story.L")
    def at_machine():
        b.teleport(L["machineX"] - 14, L["y"]); b.wait(0.4)
    at_machine()
    # 1. held too long at the machine: it goes over
    b.key("e", True); b.wait(3.2); b.key("e", False)
    f1 = record(b, "topple", 2.6)
    b.wait(5.0)
    f1b = record(b, "back", 2.4, 0.2)
    print("after topple: grabbed", b.eval(f"{G}.grabbed"), "state", b.eval(f"{G}.state"))
    b.wait(3.5)
    # 2. a proper cone, then knocked out of her hands a few steps on
    at_machine()
    b.key("e", True); b.wait(1.75); b.key("e", False); b.wait(0.4)
    print("carrying", b.eval("window.__ship.world.carry?.kind"))
    b.teleport(L["machineX"] - 70, L["y"]); b.wait(0.3)
    b.eval("window.__ship.world.carryBox.spill(window.__ship.player.x + 30)")
    f2 = record(b, "spill", 2.6)
    print("after spill: grabbed", b.eval(f"{G}.grabbed"), "state", b.eval(f"{G}.state"), "errors", b.errors[:3])
    import pickle
    for name, fr in (("topple", f1), ("back", f1b), ("spill", f2)):
        for i, (t, st, im) in enumerate(fr): im.save(os.path.join(OUT, f"{name}-{i:02d}.png"))
        open(os.path.join(OUT, f"{name}.txt"), "w").write("\n".join(f"{t} {st}" for t, st, _ in fr))
finally:
    b.close()
