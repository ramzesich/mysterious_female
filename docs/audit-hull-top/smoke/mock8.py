import sys, io, base64, os, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\ramze\Development\mysterious_female-refine\assets\source\smoke\tries"
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
b = P.Browser(stepped=True)
try:
    b.open("?play&at=funnel")
    b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    b.eval("window.__ship.smoke.forEach(t => { t.pause(); t.targets[0].setVisible(false); })")
    b.eval("window.__ship.cameras.main.stopFollow()"); b.wait(0.5); print("wv", b.eval("(c => [c.worldView.x, c.worldView.y, c.zoom, c.scrollX, c.scrollY])(window.__ship.cameras.main)"))
    for n in "ab":
        data = base64.b64encode(open(os.path.join(SRC, f"puff-{n}.png"), "rb").read()).decode()
        b.eval(f"window.__ship.textures.addBase64('try-{n}', 'data:image/png;base64,{data}')")
    b.wait_for("window.__ship.textures.exists('try-a') && window.__ship.textures.exists('try-b')", timeout=10)
    for n in "ab":
        # at each stack: a fresh wisp on its top, an older one up and aft of it, fainter
        b.eval(f"""(() => {{ const s = window.__ship; (s.__mock || []).forEach(i => i.destroy()); s.__mock = [];
          const pipes = s.smoke.filter((t,i)=>i%3===0).map(t => {{ const d = t.data, g = k => d.find(e => e.key === k); return [g('x').start, g('y').start]; }});
          pipes.forEach(([x, y], i) => {{
            for (const [dx, dy, a] of [[0, 0, 0.9], [70, -55, 0.55], [150, -120, 0.25]]) {{
              const im = s.add.image(x + dx + 22, y + dy + 23, 'try-{n}').setOrigin(0.5, 1).setAlpha(a).setDepth(s.smoke[0].targets[0].depth);
              s.worldLayer.add(im); s.__mock.push(im);
            }}
          }}); }})()""")
        print('mock', b.eval('window.__ship.__mock.slice(0,3).map(i => [i.x, i.y, i.displayHeight, i.parentContainer ? 1 : 0, i.scrollFactorX])'))
        for dusk in (0, 1):
            b.eval(f"window.__ship.setDusk({dusk})"); b.wait(0.3)
            snap(b).save(os.path.join(OUT, f"mock-{n}-{dusk}.png"))
    print("errors", b.errors)
finally:
    b.close()
