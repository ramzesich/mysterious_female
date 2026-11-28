"""Downloads a hit clip's frames (`clips/<name>/fNN.png`) and sheets them on a pale ground (green out), cropped to the
action. Usage: python fetchgag.py <job> <name> <frames>"""
import subprocess, sys
from pathlib import Path
from PIL import Image
HERE = Path(__file__).parent
job, name, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = HERE / "clips" / name
d.mkdir(parents=True, exist_ok=True)
for i in range(n + 1):
    subprocess.run(["curl", "-s", "-o", str(d / f"f{i:02d}.png"), f"https://api.pixellab.ai/mcp/images/{job}/download?index={i}"], check=True)
fr = []
for i in range(n + 1):
    im = Image.open(d / f"f{i:02d}.png").convert("RGB")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            if (g > 140 and r < 90 and b < 90) or (g > r + 30 and g > b + 30):
                px[x, y] = (246, 246, 244)
    fr.append(im.crop((0, 40, 208, 128)))
cols = 5
S = Image.new("RGB", (208 * cols, 88 * ((len(fr) + cols - 1) // cols)), (255, 255, 255))
for i, f in enumerate(fr):
    S.paste(f, ((i % cols) * 208, (i // cols) * 88))
S.resize((S.width * 2, S.height * 2), Image.NEAREST).save(HERE / f"{name}-x2.png")
big = [f.resize((624, 264), Image.NEAREST) for f in fr]
big[0].save(HERE / f"{name}.gif", save_all=True, append_images=big[1:], duration=90, loop=0)
