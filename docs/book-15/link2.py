import sys
sys.path.insert(0, r"C:\Users\ramze\Development\mysterious_female-refine\tools")
import playtest as P
b = P.Browser(stepped=True)
try:
    b.open("?play&at=library&books=all", start=None); b.wait(1.5)
    print(b.eval("JSON.stringify({books: Object.keys(window.__ship.save.books).length, x: Math.round(window.__ship.player.x)})"))
    print("errors", b.errors)
finally:
    b.close()
