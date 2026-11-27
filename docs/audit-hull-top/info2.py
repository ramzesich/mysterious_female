import sys, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import playtest as P
b = P.Browser(stepped=True)
try:
    b.open("?play&at=terrace&cards=all"); b.wait(1.0)
    print(b.eval("""(() => { const s = window.__ship; const out = [];
      const walk = (list) => list.forEach(o => { if (o.list) walk(o.list); const k = o.texture?.key, f = o.frame?.name;
        if (k && o.y < 470 && o.y > -400 && /gull|sock/i.test(k + ' ' + f)) out.push([k, String(f), Math.round(o.x), Math.round(o.y), o.originX, o.originY, o.displayWidth, o.displayHeight, o.visible, o.depth]); });
      walk(s.children.list); return out; })()"""))
finally:
    b.close()
