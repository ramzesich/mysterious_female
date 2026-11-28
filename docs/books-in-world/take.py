"""At a book: its pulse starts from its wash at rest; taken, no washed copy of it is left behind."""
import sys, json
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import playtest as P
S = "window.__ship"
b = P.Browser(stepped=True)
try:
    b.open("?play&at=deck5", start=None); b.wait(1.0)
    T = f"{S}.world.things.find(t => t.id === 'book_6')"
    t = json.loads(b.eval(f"JSON.stringify((t => [t.x, t.y])({T}))"))
    b.eval(f"window.__pick = {T}.pick; window.__over = {S}.highlight.rest.get(window.__pick).over")
    print("at rest", b.eval("JSON.stringify([window.__over.alpha, window.__over.visible])"))
    b.teleport(t[0], t[1]); b.wait(0.5)
    print("pulsing", b.eval(f"JSON.stringify({S}.highlight.state().map(e => [e.key, e.parts.map(p => p.mode)]))"))
    b.tap("e"); b.wait(1.5)
    print("taken", b.eval(f"JSON.stringify([{S}.save.books['6'], !!window.__pick.scene, !!window.__over.scene, {S}.highlight.rest.has(window.__pick)])"))
    print("errors", b.errors)
finally:
    b.close()
