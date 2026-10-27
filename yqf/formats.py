"""The two shared formats every module reads or writes. See docs/INTERFACES.md.

1. Possession probabilities: one row per video frame
       frame, p_H, p_A, p_D, confidence
   p_* sum to 1. confidence is 0-1, how much the module trusts its own row (0 = no idea).
   Anything that has an opinion about possession (dead-ball detector, nearest-player model,
   learned model, Smart Tagging prior) writes one of these. The decoder combines them.

2. Ball track: one row per video frame
       frame, x, y, source, conf
   x, y normalised 0-1 like the ATD, NaN where unknown. source says where the row came from
   (atd / interp / detector / ...). Hassan's detector writes one; yqf.io's ATD ball is the
   default one.

Both are CSVs under artifacts/ (gitignored), named <module>_<version>.csv.
"""

import os

import numpy as np
import pandas as pd

from games import source_frames

N_FRAMES = source_frames("tactical")
PROB_COLUMNS = ["frame", "p_H", "p_A", "p_D", "confidence"]
BALL_COLUMNS = ["frame", "x", "y", "source", "conf"]


def _check_frames(table, path):
    if len(table) != N_FRAMES or not np.array_equal(table["frame"].values, np.arange(N_FRAMES)):
        raise ValueError("{}: need frames 0..{} in order, one row each".format(path, N_FRAMES - 1))


def write_probs(path, p_h, p_a, p_d, confidence):
    table = pd.DataFrame({"frame": np.arange(N_FRAMES), "p_H": p_h, "p_A": p_a, "p_D": p_d,
                          "confidence": confidence})
    validate_probs(table, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    table.to_csv(path, index=False, float_format="%.4f")
    return path


def validate_probs(table, path="<probs>"):
    missing = [c for c in PROB_COLUMNS if c not in table.columns]
    if missing:
        raise ValueError("{}: missing columns {}".format(path, missing))
    _check_frames(table, path)
    total = table[["p_H", "p_A", "p_D"]].sum(axis=1).values
    if not np.allclose(total, 1.0, atol=1e-3):
        raise ValueError("{}: p_H + p_A + p_D must be 1 on every row".format(path))


def read_probs(path):
    table = pd.read_csv(path)
    validate_probs(table, path)
    return table


def write_ball(path, x, y, source, conf):
    table = pd.DataFrame({"frame": np.arange(N_FRAMES), "x": x, "y": y, "source": source,
                          "conf": conf})
    validate_ball(table, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    table.to_csv(path, index=False, float_format="%.5f")
    return path


def validate_ball(table, path="<ball>"):
    missing = [c for c in BALL_COLUMNS if c not in table.columns]
    if missing:
        raise ValueError("{}: missing columns {}".format(path, missing))
    _check_frames(table, path)


def read_ball(path):
    table = pd.read_csv(path)
    validate_ball(table, path)
    return table
