import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image, ImageDraw
import playtest as P
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "full"); os.makedirs(OUT, exist_ok=True)
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    return Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
def record(b, name, secs, step=0.1):
    frames, t = [], 0.0
    while t < secs:
        frames.append(snap(b)); b.wait(step); t += step
    frames[0].save(os.path.join(OUT, f"{name}.gif"), save_all=True, append_images=frames[1:], duration=int(step * 1000), loop=0)
    for i in (0, len(frames) // 4, len(frames) // 2): frames[i].save(os.path.join(OUT, f"{name}-{i:02d}.png"))
    print(name, len(frames), "frames")
W = "window.__ship.world"
b = P.Browser(stepped=True)
try:
    b.open("?play&at=icecream&did=bb5"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    L = b.eval(f"{W}.story.L")
    def at_machine():
        b.teleport(L["machineX"] - 14, L["y"]); b.wait(0.6)
    # 1. held too long: it goes over (from the start of the swirl)
    at_machine()
    b.key("e", True)
    frames = []
    for i in range(32): frames.append(snap(b)); b.wait(0.1)
    b.key("e", False)
    for i in range(30): frames.append(snap(b)); b.wait(0.1)
    frames[0].save(os.path.join(OUT, "1-machine.gif"), save_all=True, append_images=frames[1:], duration=100, loop=0)
    print("machine", b.eval(f"{W}.foodGulls.gull_go.grabbed"))
    b.wait(9)
    # 2. a proper cone, a few steps on, knocked out of her hands
    at_machine(); b.key("e", True); b.wait(1.75); b.key("e", False); b.wait(0.4)
    b.teleport(L["machineX"] - 70, L["y"]); b.wait(0.2)
    b.eval(f"{W}.carryBox.spill(window.__ship.player.x + 30)")
    record(b, "2-knocked", 3.0)
    print("knocked", b.eval(f"{W}.foodGulls.gull_go.grabbed"))
    b.wait(9)
    # 3. a stub to the kid at the pool: he turns it down
    at_machine(); b.key("e", True); b.wait(0.9); b.key("e", False); b.wait(0.4)
    kid = f"{W}.people.byId['npc_kid']"
    b.eval(f"{kid}.x = {L['kidA'] + 120}; {kid}.mode = 'patrol'")
    b.teleport(L["kidA"] + 90, L["y"]); b.wait(0.5)
    b.tap("e")
    record(b, "3-kid-stub", 6.0)
    print("kid stub: pool gull grabbed", b.eval(f"{W}.foodGulls.gull_pool.grabbed"), "errors", b.errors[:3])
finally:
    b.close()
