"""Where the tools put what they make (screenshots, sheets, the test browsers' profiles).

The system's temp folder; or the folder named in the environment variable BUMBUSIK_TEMP. A
workspace of its own names one (in its `.claude/settings.local.json`, under `env`), so that two
sessions working side by side do not write over each other's screenshots (docs/plan-the-rest.md).
A variable of our own, because Claude Code keeps `TEMP`, `TMP` and `TMPDIR` to itself: a settings
file cannot change those (tried, 2026-11-18).

    python tools/tempdir.py        prints the folder in use
"""
import os
import tempfile
from pathlib import Path


def _temp():
    named = os.environ.get("BUMBUSIK_TEMP")
    if not named:
        return Path(tempfile.gettempdir())
    Path(named).mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = named            # so tempfile.mkdtemp() and its kin follow
    return Path(named)


TEMP = _temp()

if __name__ == "__main__":
    print(TEMP)
