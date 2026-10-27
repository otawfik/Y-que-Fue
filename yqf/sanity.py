"""Label-free report on a submission. How we compare versions without tuning on the public 5 min.

    python -m yqf.sanity evaluation/results/Y-que-Fue.csv
    python -m yqf.sanity evaluation/results/*.csv --note "hmm switch cost 8"

Prints, per half and overall: how many possessions the file claims, how long they last, how many
are implausibly short (flicker), the dead-ball and home shares, and how often the file agrees with
the automatic Smart Tagging team phases. Nothing here reads a ground truth. Each file's numbers are
appended as one row to experiments/log.csv, together with the git commit that produced it.

Smart Tagging is automatic and imperfect, so agreement is evidence, not a score: a version that
agrees more is not automatically better, but a big drop means something broke.
"""

import argparse
import csv
import datetime
import os
import subprocess

import numpy as np

from yqf import ROOT
import possession_metrics as pm
import load_smart_tagging
from games import GAME, GAMES, half_video_blocks

LOG_PATH = os.path.join(ROOT, "experiments", "log.csv")
FPS = GAMES[GAME]["fps"]
SHORT_SPELL_S = 2.0  # possessions shorter than this are mostly flicker

# Phases whose Team tag names the team WITH the ball, and phases whose Team tag names the team
# WITHOUT it. Set pieces, goals and N/A-team instances are left out of the agreement check.
ATTACKING_CODES = {"build up", "progression", "creating chances", "attacking transition",
                   "ball in final third", "ball in the box", "players in the box", "long ball"}
DEFENDING_CODES = {"defending in attacking third", "defending in middle third",
                   "defending in defensive third", "defensive transition"}
TEAM_CODE = {"barcelona": pm.H, "atletic club": pm.A}


def graded_runs():
    """The two halves as half-open [start, stop) video-frame spans."""
    return [(first, last + 1) for _, first, last in half_video_blocks(GAME)]


def tag_expectation(n_frames):
    """Per-frame expected possessor from Smart Tagging (H/A code), X where it says nothing."""
    expected = np.full(n_frames, pm.X, dtype=np.int8)
    set_piece = np.zeros(n_frames, dtype=bool)
    for event in load_smart_tagging.load():
        code = event["code"].strip().lower()
        start, stop = max(0, event["start_frame"]), min(n_frames, event["end_frame"])
        if code == "set pieces":
            set_piece[start:stop] = True
            continue
        team = TEAM_CODE.get((event["tags"].get("Team") or "").strip().lower())
        if team is None:
            continue
        if code in ATTACKING_CODES:
            expected[start:stop] = team
        elif code in DEFENDING_CODES:
            expected[start:stop] = pm.A if team == pm.H else pm.H
    return expected, set_piece


def spell_stats(codes, runs):
    spells = pm.possession_spells(codes, runs)
    lengths = np.array([b - a for a, b, _ in spells], dtype=float) / FPS
    graded = np.concatenate([codes[a:b] for a, b in runs])
    alive = np.isin(graded, (pm.H, pm.A))
    return {
        "possessions": len(spells),
        "mean_s": round(float(lengths.mean()), 1) if len(lengths) else 0.0,
        "median_s": round(float(np.median(lengths)), 1) if len(lengths) else 0.0,
        "short_lt2s": int(np.sum(lengths < SHORT_SPELL_S)),
        "dead_share": round(float(np.mean(graded == pm.D)), 3),
        "abstain_share": round(float(np.mean(graded == pm.X)), 3),
        "home_share": round(float(np.mean(graded[alive] == pm.H)), 3) if alive.any() else 0.0,
    }


def report(path, expected, set_piece):
    codes = pm.label_codes(pm.read_label_csv(path)["label"].values)
    runs = graded_runs()
    filled = pm.fill_abstentions(codes, runs)  # what the official spellF1 actually sees

    row = {"file": os.path.basename(path)}
    for half, run in zip((1, 2), runs):
        for key, value in spell_stats(filled, [run]).items():
            row["h{}_{}".format(half, key)] = value
    row.update(spell_stats(filled, runs))

    graded = np.zeros(len(codes), dtype=bool)
    for a, b in runs:
        graded[a:b] = True
    tagged = graded & (expected != pm.X) & np.isin(filled, (pm.H, pm.A))
    row["tag_agree"] = round(float(np.mean(filled[tagged] == expected[tagged])), 3) \
        if tagged.any() else 0.0
    sp = graded & set_piece
    row["setpiece_dead_share"] = round(float(np.mean(filled[sp] == pm.D)), 3) if sp.any() else 0.0
    return row


def git_commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip()
        return out + ("+dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def append_log(rows, note):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    commit = git_commit()
    fields = ["when", "commit", "note"] + list(rows[0].keys())
    exists = os.path.isfile(LOG_PATH) and os.path.getsize(LOG_PATH) > 0
    with open(LOG_PATH, "a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(dict(row, when=stamp, commit=commit, note=note))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("submissions", nargs="+", help="frame,label CSVs")
    parser.add_argument("--note", default="", help="what changed in this version")
    parser.add_argument("--no-log", action="store_true", help="print only")
    args = parser.parse_args()

    expected, set_piece = tag_expectation(GAMES[GAME]["n_video_frames"])
    rows = [report(path, expected, set_piece) for path in args.submissions]

    columns = ["possessions", "mean_s", "median_s", "short_lt2s", "dead_share", "home_share",
               "tag_agree", "setpiece_dead_share", "h1_possessions", "h2_possessions"]
    width = max(len(r["file"]) for r in rows)
    print("{:<{w}}  ".format("file", w=width) + "  ".join("{:>9}".format(c[:9]) for c in columns))
    for r in rows:
        print("{:<{w}}  ".format(r["file"], w=width)
              + "  ".join("{:>9}".format(r[c]) for c in columns))

    if not args.no_log:
        append_log(rows, args.note)
        print("\nappended {} row(s) to {}".format(len(rows), os.path.relpath(LOG_PATH, ROOT)))
