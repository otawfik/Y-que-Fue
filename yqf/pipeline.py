"""Build the submission: data in, <team>.csv out. The one command the repository must reproduce.

    python -m yqf.pipeline                    -> evaluation/results/Y-que-Fue.csv
    python -m yqf.pipeline --name v1_hmm      -> evaluation/results/v1_hmm.csv

v0 is the official baseline_smooth50 routed through our own interfaces (probabilities in
artifacts/, then a decoder). It must reproduce evaluation/results/baseline_smooth50.csv byte for
byte -- that is the plumbing test. Every later version replaces a stage, not the whole thing:

    stage 1  possession probabilities   nearest player today; dead-ball detector, learned model,
                                        Smart Tagging prior next (each writes a probs CSV)
    stage 2  decode                     majority vote today; HMM / Viterbi next
"""

import argparse
import os

import numpy as np

from yqf import ARTIFACTS, RESULTS_DIR
import baseline
from yqf import formats

TEAM_NAME = "Y-que-Fue"
SMOOTH_WINDOW = 50  # frames either side; the published floor's setting


def nearest_player_probs():
    """Stage 1, v0: one-hot probabilities from the baseline's nearest-player rule."""
    codes = baseline.build()
    p_h = (codes == baseline.HOME).astype(np.float32)
    p_a = (codes == baseline.AWAY).astype(np.float32)
    p_d = (codes == baseline.NOBODY).astype(np.float32)
    confidence = np.where(codes == baseline.NOBODY, 0.0, 1.0).astype(np.float32)
    return formats.write_probs(os.path.join(ARTIFACTS, "probs", "nearest_player_v0.csv"),
                               p_h, p_a, p_d, confidence)


def decode_majority(probs_path, window=SMOOTH_WINDOW):
    """Stage 2, v0: argmax per frame, then the baseline's majority vote. To be replaced by HMM."""
    table = formats.read_probs(probs_path)
    probs = table[["p_H", "p_A", "p_D"]].values
    best = probs.argmax(axis=1)
    codes = np.where(best == 0, baseline.HOME,
                     np.where(best == 1, baseline.AWAY, baseline.NOBODY)).astype(np.int8)
    return baseline.smooth(codes, window)


def run(name=TEAM_NAME):
    probs_path = nearest_player_probs()
    labels = decode_majority(probs_path)
    path = baseline.write_submission(os.path.join(RESULTS_DIR, "{}.csv".format(name)), labels)
    print("wrote {}".format(os.path.relpath(path)))
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", default=TEAM_NAME, help="output file stem")
    run(parser.parse_args().name)
