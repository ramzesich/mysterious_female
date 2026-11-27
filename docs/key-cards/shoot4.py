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
def cam(b): return json.loads(b.eval("JSON.stringify([window.__ship.cameras.main.worldView.x, window.__ship.cameras.main.worldView.y])"))
b = P.Browser(stepped=True)
try:
    # The card on the sun deck after the horn.
    b.open("?play&at=sundeck&did=horn"); b.wait(1.0)
    b.eval("window.__ship.scareContact = () => false")
    b.teleport(6860, 416); b.wait(1.5)
    snap(b).save(os.path.join(OUT, "n-floor.png"))
    # The hand-overs, called straight on each giver.
    for at, who, frame, toss, name in [("gangway", "npc_officer", "thing:key-card-deck", None, "deck"),
                                      ("stage", "npc_stagemanager", "thing:key-card-ent", None, "ent"),
                                      ("steward", "npc_steward", "thing:key-card-hk", "{ clip: 'toss', held: { 3: [1, 40], 4: [3, 41] }, release: 5, from: [19, 37] }", "hk")]:
        b.open(f"?play&at={at}"); b.wait(1.0)
        b.eval("window.__ship.scareContact = () => false")
        pos = json.loads(b.eval(f"(() => {{ const q = window.__ship.world.people.byId['{who}']; return JSON.stringify([q.x, q.y, q.dir]); }})()"))
        print(name, pos)
        b.teleport(pos[0] + pos[2] * 34, pos[1]); b.wait(1.0)
        call = (f"window.__ship.world.tossOver(q, '{frame}', null, null, {toss})" if toss else f"window.__ship.world.handOver(q, '{frame}', null)")
        b.eval(f"(() => {{ const q = window.__ship.world.people.byId['{who}']; window.__ship.player.setFlipX(q.dir > 0); {call}; }})()")
        frames = []
        for i in range(6):
            b.wait(0.12)
            im = snap(b); c = cam(b)
            x0 = int(pos[0] - c[0]) - 60; y0 = int(pos[1] - c[1]) - 80
            frames.append(im.crop((x0, y0, x0 + 120, y0 + 90)))
        S = Image.new("RGB", (6 * 120 * 3 + 25, 90 * 3), (20, 20, 28))
        for i, f in enumerate(frames): S.paste(f.resize((360, 270), Image.NEAREST), (i * 365, 0))
        S.save(os.path.join(OUT, f"n-give-{name}.png"))
    print("errors", b.errors)
finally:
    b.close()
