"""Serves the game locally with browser caching turned off, so a reload always picks up the latest
map, scripts and sprites (plain `python -m http.server` lets Chrome keep stale copies).

    python tools/serve.py [port]      (default 8000), then open http://localhost:8000
"""

import functools
import http.server
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(NoCache, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(("", port), handler) as httpd:
        print(f"serving {ROOT.name} at http://localhost:{port} (no caching); Ctrl+C to stop", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
