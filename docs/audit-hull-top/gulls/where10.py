# Finding 10: what stands on the kids' pool's two rims (deck 12, 3240..3530): every shown object's bounds there.
import sys, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import playtest as P
b = P.Browser(stepped=True)
try:
    b.open("?play&at=spinnaker"); b.wait(1.5); b.eval("window.__ship.scareContact = () => false")
    b.teleport(3200, 416); b.wait(1.0)
    out = b.eval("""(() => { const all = []; const walk = l => l.forEach(o => { all.push(o); if (o.list) walk(o.list); });
      walk(window.__ship.children.list);
      return all.filter(o => o.visible && o.getBounds && o.type !== 'Graphics' && o.type !== 'TilemapLayer').map(o => { const r = o.getBounds();
        return [o.type, o.texture?.key, o.frame?.name, Math.round(r.x), Math.round(r.y), Math.round(r.right), Math.round(r.bottom), +o.depth.toFixed(3)]; })
        .filter(r => r[5] > 300 && r[4] < 420 && r[3] > 3200 && r[3] < 3560 && r[6] > 380 && r[6] < 460); })()""")
    for r in sorted(out, key=lambda r: r[3]): print(r)
    print("pool", b.eval("JSON.stringify((window.__ship.world.data.pools || []).filter(p => p.x0 > 3000 && p.x0 < 3600))"))
finally:
    b.close()
