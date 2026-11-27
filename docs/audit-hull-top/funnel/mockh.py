import sys, io, base64, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
from PIL import Image
import playtest as P
OUT = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\ramze\Development\mysterious_female-refine\assets\source\funnel-top\tries"
def snap(b):
    b.eval("window.__snap = null; window.__ship.game.renderer.snapshot(img => { window.__snap = img.src; })")
    if b.taken: b.advance(1/60, draw=True)
    b.wait_for("window.__snap", timeout=10)
    im = Image.open(io.BytesIO(base64.b64decode(b.eval("window.__snap").split(",",1)[1]))).convert("RGB")
    return im.resize((im.width//2, im.height//2), Image.NEAREST)
# per variant: horn picture, its pole's middle column, the cat's seat row; box picture, the free lid's middle column, its lid row, foot row
V = {"a": ("horn-a", 41.5, 11, "box-a", 27, 15, 29), "b": ("horn-b", 39, 18, "box-b", 27, 14, 27)}
b = P.Browser(stepped=True)
try:
    b.open("?play&at=funnel"); b.wait(1.5)
    b.eval("window.__ship.scareContact = () => false")
    for n in ("horn-a", "horn-b", "box-a", "box-b", "cord-a"):
        data = base64.b64encode(open(os.path.join(SRC, n + ".png"), "rb").read()).decode()
        b.eval(f"window.__ship.textures.addBase64('{n}', 'data:image/png;base64,{data}')")
    b.wait_for("['horn-a','horn-b','box-a','box-b','cord-a'].every(k => window.__ship.textures.exists(k))", timeout=10)
    # the old pieces: the post (exterior + 0.076), the cord (+ 0.077), the toolbox image; the tangerine on it
    info = b.eval("""(() => { const s = window.__ship, D = s.DEPTH, T = s.world.data.topdeck.funnel, top = s.world.data.funnel.y;
        const old = s.worldLayer.list.filter(o => (o.type === 'Graphics' && (Math.abs(o.depth - (D.exterior + 0.076)) < 1e-6 || Math.abs(o.depth - (D.exterior + 0.077)) < 1e-6))
           || (o.texture && o.texture.key === 'toolbox'));
        old.forEach(o => o.setVisible(false)); window.__old = old;
        const tan = s.worldLayer.list.filter(o => o.texture && o.x > T.toolboxX - 20 && o.x < T.toolboxX + 20 && o.y < top && o.y > top - 30 && o.texture.key !== 'toolbox');
        window.__tan = tan;
        return { hidden: old.length, tan: tan.map(o => [o.texture.key, o.x, o.y, o.originY]), hornX: T.hornX, boxX: T.toolboxX, top }; })()""")
    print(info)
    hx, bx, top = info["hornX"], info["boxX"], info["top"]
    for v, (horn, pole, seat, box, lid, lidRow, foot) in V.items():
        b.eval(f"""(() => {{ const s = window.__ship, D = s.DEPTH; (window.__mock || []).forEach(o => o.destroy());
          const h = s.add.image({hx} - {pole}, {top} - 112, '{horn}').setOrigin(0, 0).setDepth(D.exterior + 0.076);
          const c = s.add.image({hx} + 4 - 16, {top} - 112 + {seat} + 8, 'cord-a').setOrigin(0, 0).setDepth(D.exterior + 0.077);
          const bx = s.add.image({bx} - {lid}, {top} - {foot} - 1, '{box}').setOrigin(0, 0).setDepth(D.exterior + 0.08);
          window.__mock = [h, c, bx]; s.worldLayer.add(window.__mock);
          const cat = s.world.story?.hornCat || s.world.hornCat; if (cat) cat.y = {top} - 112 + {seat};
          (window.__tan || []).forEach(t => t.y = {top} - ({foot} - {lidRow} + 1) + (t.__dy ?? (t.__dy = t.y - ({top} - 13))));
        }})()""")
        b.teleport(hx - 70, top); b.wait(1.0)
        snap(b).save(os.path.join(OUT, f"mockh-{v}-horn.png"))
        b.teleport(bx - 60, top); b.wait(1.0)
        snap(b).save(os.path.join(OUT, f"mockh-{v}-box.png"))
    print("errors", b.errors)
finally:
    b.close()
