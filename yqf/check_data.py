"""Is every data file where games.py expects it, at the size the organisers shipped?

    python -m yqf.check_data

Run this once after unpacking the bundle into data/. It prints file names and sizes only.
"""

import os
import sys

from yqf import ROOT  # noqa: F401  (sets sys.path)
from games import SOURCES, asset_paths

# Byte sizes of the files as delivered on the competition Drive (2026-10-07 bundle).
EXPECTED_BYTES = {
    "BAR-ATH_tactical.mp4": 5222307334,
    "BAR-ATH_tactical_atd.txt": 195714285,
    "BAR-ATH_tactical_atd.xml": 59057,
    "BAR-ATH_tactical_homography.csv": 23187043,
    "BAR-ATH_tactical_smart_tagging.xml": 261055,
    "BAR-ATH_broadcast.mp4": 13962360320,
    "BAR-ATH_broadcast_atd.txt": 141966465,
    "BAR-ATH_broadcast_atd.xml": 64956,
    "BAR-ATH_broadcast_homography.csv": 15401635,
}

# Broadcast is optional; only the tactical set is required to build a submission.
REQUIRED_SOURCES = ("tactical",)


def check():
    ok = True
    for source in SOURCES:
        for asset, path in sorted(asset_paths(source=source).items()):
            name = os.path.basename(path)
            if not os.path.isfile(path):
                status = "MISSING" if source in REQUIRED_SOURCES else "missing (optional)"
                ok = ok and source not in REQUIRED_SOURCES
            elif os.path.getsize(path) != EXPECTED_BYTES.get(name, os.path.getsize(path)):
                status = "WRONG SIZE ({} bytes, expected {})".format(
                    os.path.getsize(path), EXPECTED_BYTES[name])
                ok = False
            else:
                status = "ok"
            print("{:<10} {:<14} {:<38} {}".format(source, asset, name, status))
    return ok


if __name__ == '__main__':
    if check():
        print("\nAll required data present.")
    else:
        print("\nSomething is missing or truncated -- see data/README.md.")
        sys.exit(1)
