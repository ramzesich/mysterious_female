"""Download a PixMiniMax job's frames: python fetch.py <job> <folder> <n>."""
import sys, os, urllib.request
job, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(out, exist_ok=True)
for i in range(n + 1):
    rq = urllib.request.Request(f"https://api.pixellab.ai/mcp/images/{job}/download?index={i}", headers={"User-Agent": "Mozilla/5.0"})
    open(f"{out}/{i}.png", "wb").write(urllib.request.urlopen(rq).read())
print(out, "ok")
