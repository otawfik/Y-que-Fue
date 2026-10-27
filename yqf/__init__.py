"""Y que Fue -- team code for More than a Hack 2027, Phase 1 (frame-level ball possession).

Everything the team builds lives in this package. The official files at the repository root
(games.py, evaluation/, starter/) are kept untouched so `git pull upstream main` stays clean.

    python -m yqf.check_data          is the data where games.py expects it?
    python -m yqf.pipeline            build the submission
    python -m yqf.sanity <file.csv>   label-free report, appended to experiments/log.csv

See docs/INTERFACES.md for the file formats modules hand to each other.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _path in (ROOT, os.path.join(ROOT, "starter"), os.path.join(ROOT, "evaluation")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Everything we generate (caches, probability tables, ball tracks, model weights, video crops)
# goes here. It is gitignored: frame-level derivatives of the match data may not be published.
ARTIFACTS = os.path.join(ROOT, "artifacts")
RESULTS_DIR = os.path.join(ROOT, "evaluation", "results")
