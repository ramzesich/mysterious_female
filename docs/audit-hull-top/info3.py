import sys, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import playtest as P
b = P.Browser(stepped=True)
try:
    b.open("?play"); b.wait(1.0)
    b.eval("window.__ship.enterOverview(true)"); b.wait(1.0)
    print(b.eval("""(() => { const s = window.__ship; const out = [];
      const walk = (list) => list.forEach(o => { if (o.list) walk(o.list); const k = o.texture?.key, f = o.frame?.name;
        if (k && o.x > 10700 && o.x < 10900 && o.y > 380 && o.y < 470 && o.visible) out.push([k, String(f), Math.round(o.x), Math.round(o.y), o.originY, o.displayHeight, o.depth]); });
      walk(s.children.list); return out; })()"""))
    print(b.eval("""(() => { const s = window.__ship; const g = (s.world.movers||[]).filter(m => m.constructor && /gull/i.test(m.constructor.name)).map(m => m.constructor.name); return g; })()"""))
finally:
    b.close()
