"""Fast, cached access to the tactical ATD as numpy arrays, indexed by video frame.

    from yqf.io import load_atd
    atd = load_atd()
    atd["players"]       (n_frames, 46, 2) float32, normalised 0-1, NaN where the slot is empty
    atd["player_speed"]  (n_frames, 46)    float32, m/s
    atd["team"]          (46,)             int8, 0 = home (Barcelona), 1 = away (Athletic)
    atd["ball"]          (n_frames, 2)     float32, normalised 0-1, NaN where the ball is lost
    atd["ball_z"]        (n_frames,)       float32, third ball field as delivered
    atd["pitch"]         (2,)              pitch size in metres, from games.py

Row i is video frame i, i.e. submission row i (the raw file counts from 1; that is handled here).
The first call parses the 196 MB text file once and caches it under artifacts/cache/ (gitignored);
later calls load the cache in about a second.
"""

import os

import numpy as np

from yqf import ARTIFACTS
from games import GAME, GAMES, require, source_frames
from baseline import team_of_each_track

CACHE_DIR = os.path.join(ARTIFACTS, "cache")
# Bump when the cached layout changes, so stale caches are rebuilt rather than misread.
CACHE_VERSION = 1


def _parse_group(group, n_fields):
    """'x,y,s' -> list of floats; 'NaN,...' parses to nan through float()."""
    values = group.split(",")
    return [float(v) for v in values[:n_fields]]


def parse_atd(source="tactical", game=GAME):
    meta_path, raw_path = require(["atd_meta", "atd_raw"], game, source=source)
    team = team_of_each_track(meta_path)
    n_frames = source_frames(source, game)
    n_slots = len(team)

    players = np.full((n_frames, n_slots, 3), np.nan, dtype=np.float32)
    ball = np.full((n_frames, 3), np.nan, dtype=np.float32)

    with open(raw_path) as handle:
        for line in handle:
            parts = line.rstrip("\n").split(":")
            if len(parts) != 3:
                continue
            row = int(parts[0]) - 1  # frame_id counts from 1, video frames from 0
            groups = parts[1].split(";")
            players[row, :len(groups)] = [_parse_group(g, 3) for g in groups]
            ball[row] = _parse_group(parts[2], 3)

    return {
        "players": players[:, :, :2].copy(),
        "player_speed": players[:, :, 2].copy(),
        "team": team,
        "ball": ball[:, :2].copy(),
        "ball_z": ball[:, 2].copy(),
        "pitch": np.array(GAMES[game]["pitch"], dtype=np.float32),
    }


def load_atd(source="tactical", game=GAME, refresh=False):
    path = os.path.join(CACHE_DIR, "{}_{}_atd_v{}.npz".format(game, source, CACHE_VERSION))
    if not refresh and os.path.isfile(path):
        with np.load(path) as cached:
            return {key: cached[key] for key in cached.files}

    atd = parse_atd(source, game)
    os.makedirs(CACHE_DIR, exist_ok=True)
    np.savez(path, **atd)
    return atd


if __name__ == '__main__':
    atd = load_atd(refresh=True)
    ball_seen = ~np.isnan(atd["ball"][:, 0])
    tracked = (~np.isnan(atd["players"][:, :, 0])).sum(axis=1)
    print("frames {}  slots {}  home slots {}  away slots {}".format(
        len(atd["ball"]), atd["players"].shape[1], int(np.sum(atd["team"] == 0)),
        int(np.sum(atd["team"] == 1))))
    print("ball located on {} frames ({:.1f}%)".format(
        int(ball_seen.sum()), 100.0 * ball_seen.mean()))
    print("mean tracked players on frames with any: {:.1f}".format(tracked[tracked > 0].mean()))
