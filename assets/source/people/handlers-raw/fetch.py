"""Downloads a PixMiniMax job's frames into a clip folder, and sheets it with the real painting where its panel is.
Usage: python fetch.py <job id> <folder> <frames>"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
job, folder, n = sys.argv[1], HERE / sys.argv[2], int(sys.argv[3])
folder.mkdir(parents=True, exist_ok=True)
for i in range(n + 1):
    subprocess.run(["curl", "-s", "-o", str(folder / f"f{i:02d}.png"), f"https://api.pixellab.ai/mcp/images/{job}/download?index={i}"], check=True)
name = sys.argv[2].replace("/", "-")
subprocess.run([sys.executable, str(HERE / "cut.py"), sys.argv[2], name], check=True)
subprocess.run([sys.executable, str(HERE / "sheet.py"), name], check=True)
