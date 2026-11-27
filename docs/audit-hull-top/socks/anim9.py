# Finding 9: each windsock try moving in the running game through a whole gust round (5 s at 10 frames a second):
# limp and swaying slowly in the lull, half filled in the warning, full and fluttering in the gust. The stairway
# foot's sock moved 46 px forward (the user's 3a). C has only a full state: its lull and warning are A's.
import sys, io, base64, os, json
import numpy as np
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(OUT, "..", "..", "..", "assets", "source", "windsock", "tries")
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
def states(name, eyes=None):
    a = np.array(Image.open(os.path.join(SRC, name + ".png")).convert("RGBA"))
    on = a[:, :, 3] >= 128; cols = np.where(on.any(0))[0]
    groups, s0, pv = [], cols[0], cols[0]
    for c in cols[1:]:
        if c != pv + 1: groups.append((s0, pv)); s0 = c
        pv = c
    groups.append((s0, pv)); out = []
    for x0, x1 in groups:
        sub = a[:, x0:x1 + 1]; rows = np.where((sub[:, :, 3] >= 128).any(1))[0]
        sub = sub[rows[0]:rows[-1] + 1].copy(); sub[:, :, 3] = np.where(sub[:, :, 3] >= 128, 255, 0)
        grey = (sub[:, :, 3] > 0) & (np.abs(sub[:, :, 0].astype(int) - sub[:, :, 2]) < 30)
        ys, xs = np.where(grey[:8]); ex, ey = xs.mean() + 0.5, ys.mean() + 0.5
        if eyes: ex, ey = eyes[len(out)]      # (the swivel's eye, its hole's middle, measured by hand)
        buf = io.BytesIO(); Image.fromarray(sub).save(buf, "PNG")
        out.append(dict(data="data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), ox=ex / sub.shape[1], oy=ey / sub.shape[0]))
    return out
B = states("sheet-b", [(3.5, 3.0), (3.5, 3.5), (3.5, 3.5)])
TRIES = {"B": B}
G = "window.__ship.world.movers.find(m => m.flappers && m.flappers.length === 3 && !m.F)"
SETUP = """(tries => {
  const s = window.__ship, g = %s;
  for (const [t, st] of Object.entries(tries)) st.forEach((p, k) => s.textures.addBase64(`ws-${t}-${k}`, p.data));
  window.__ws = { tries, t: 'A' };
  // the stairway foot's sock 46 px forward, its pole with it
  const f3 = g.flappers[2], all = []; const walk = l => l.forEach(o => { all.push(o); if (o.list) walk(o.list); }); walk(s.children.list);
  const pole = all.find(o => o.type === 'Rectangle' && o.width === 2 && o.height === 40 && Math.abs(o.x - (f3.img.x - 1)) < 2);
  pole.x -= 46; f3.img.x -= 46;
  const poles = g.flappers.map(f => [f.img.x - 1, f.img.y - 1]);
  const up = g.update.bind(g);
  g.update = (dt, time) => {
    up(dt, time);
    const ph = g.phase(time), st = window.__ws.tries[window.__ws.t];
    g.flappers.forEach((f, i) => {
      const k = ph === 'calm' ? 0 : ph === 'tell' ? 1 : 2, p = st[k];
      f.img.setTexture(`ws-${window.__ws.t}-${k}`).setOrigin(p.ox, p.oy).setPosition(poles[i][0], poles[i][1]);
      const a = k === 0 ? Math.sin(time / 900 + i * 1.7) * 4 : k === 1 ? Math.sin(time / 260 + i * 1.7) * 5 : Math.sin(time / 55 + i * 1.7) * 3;
      f.img.setAngle(a);
    });
  };
})""" % G
def round_(b, crops, name):
    for _ in range(400):
        if b.eval(f"(g => g.phase(window.__ship.time.now))({G})") != "calm": break
        b.wait(0.05)
    for _ in range(400):
        if b.eval(f"(g => g.phase(window.__ship.time.now))({G})") == "calm": break
        b.wait(0.05)
    frames = []
    for i in range(52):
        im = snap(b); v = b.eval("(c => [c.worldView.x, c.worldView.y])(window.__ship.cameras.main)")
        parts = []
        for (x0, y0, w, h) in crops:
            x, y = int(x0 - v[0]), int(y0 - v[1]); parts.append(im.crop((x, y, x + w, y + h)).resize((w * 2, h * 2), Image.NEAREST))
        frames.append(parts)
        b.wait(0.1 - 1/60)
    return frames
b = P.Browser(stepped=True)
rec = {}
try:
    tries = {k: v for k, v in TRIES.items()}
    for area, url, crops in (("stair", "?play&at=stairway", [(8400, 108, 300, 175)]), ("top", "?play&at=funnel", [(9670, -330, 140, 110)])):
        b.open(url); b.wait(1.5)
        b.eval("window.__ship.scareContact = () => false")
        if area == "stair": b.hold("left", 0.25)
        else: b.teleport(9690, -228)
        b.wait(0.8)
        b.eval(SETUP + "(" + json.dumps(tries) + ")")
        b.wait_for("window.__ship.textures.exists('ws-B-2')", timeout=10)
        for t in ("B",):
            b.eval(f"window.__ws.t = '{t}'"); b.wait(0.2)
            rec[(area, t)] = round_(b, crops, t)
    for t in ("B",):
        out = []
        for fs, ft in zip(rec[("stair", t)], rec[("top", t)]):
            a, c = fs[0], ft[0]
            im = Image.new("RGB", (a.width + c.width + 6, a.height), "white"); im.paste(a, (0, 0)); im.paste(c, (a.width + 6, 0)); out.append(im)
        out[0].save(os.path.join(OUT, f"anim-{t}2.gif"), save_all=True, append_images=out[1:], duration=100, loop=0)
        pick = out[::4]; cols = (len(pick) + 1) // 2; w, h = pick[0].size
        s = Image.new("RGB", (cols * (w + 4), 2 * (h + 4)), "white")
        for i, f in enumerate(pick): s.paste(f, ((i % cols) * (w + 4), (i // cols) * (h + 4)))
        s.save(os.path.join(OUT, f"anim-{t}2-strip.png"))
    print("errors", b.errors)
finally:
    b.close()
