"""9a's and 9c's starts and ends (2026-11-19), from her built sheet. 9a: her run frames 1, 3, 5, 7 at x 72 (head on into
the jogger, who runs on); the end her dazed sit's first frame at x 64. 9c: her standing frame at x 36 (he runs into her
back); the end her dazed lie's first frame, 50 px further on."""
from starts2 import *
O = R + "assets/source/her-mishaps/batch-4a/starts/jog9/"
for n in (1, 3, 5, 7):
    im = Image.new("RGBA", (128, 128)); put(im, herf("run", n), 72); im.save(O + f"a/start-run{n}.png")
e = Image.new("RGBA", (128, 128)); put(e, herf("dazed-sit", 0), 64); e.save(O + "a/end.png")
s = Image.new("RGBA", (128, 128)); put(s, herf("stand"), 36); s.save(O + "c/start.png")
e2 = Image.new("RGBA", (128, 128)); put(e2, herf("dazed-lie", 0), 86); e2.save(O + "c/end.png")
print(e2.getbbox(), s.getbbox())
row([Image.open(O + f"a/start-run{n}.png") for n in (1, 3, 5, 7)] + [e, s, e2], O + "ac-starts.png", k=2, bg=(200, 200, 205, 255))
