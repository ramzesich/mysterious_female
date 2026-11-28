import sys, os
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import playtest as P
b = P.Browser(stepped=True)
try:
    b.open("?play&at=kids&did=catch", start=None); b.wait(1.5)
    print(b.eval("JSON.stringify({holding: window.__ship.holding, x: Math.round(window.__ship.player.x), y: Math.round(window.__ship.player.y), book: (t => t && [Math.round(t.x), Math.round(t.y)])(window.__ship.world.things.find(t => t.id === 'book_15'))})"))
    b.teleport(1632, 1136); b.wait(0.5)
    b.tap("e"); b.wait(1.0)
    print(b.eval("JSON.stringify(window.__ship.save.books)"))
    print("errors", b.errors)
finally:
    b.close()
