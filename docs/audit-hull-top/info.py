import sys, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import playtest as P
b = P.Browser(stepped=True)
try:
    b.open("?play&at=deck12&cards=all"); b.wait(1.0)
    print(b.eval("(() => { const s = window.__ship; return ['deck12','sundeck','court','terrace','stairway','funnel','spinnaker'].map(n => [n, Math.round(s.places[n].x), Math.round(s.places[n].y)]); })()"))
    # every image in the world above y=440 that is a gull or windsock, with position
    print(b.eval("""(() => { const s = window.__ship; const out = [];
      s.children.list.forEach(o => { const k = o.texture?.key, f = o.frame?.name; if (o.y < 450 && o.visible && k && /gull|sock|seagull/i.test(k + ' ' + f)) out.push([k, f, Math.round(o.x), Math.round(o.y), o.originY, Math.round(o.displayHeight)]); });
      return out; })()"""))
finally:
    b.close()
