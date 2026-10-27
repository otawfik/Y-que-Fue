# Interfaces

How the pieces hand work to each other, so nobody waits on anybody. Code: `yqf/formats.py`.

```
 ATD / video / Smart Tagging
          │
          ├── Hassan: ball detector ──► ball track CSV ──┐
          │                                              ▼
          ├── Omar: dead-ball detector ─────────► probs CSV ──┐
          ├── nearest-player model ─────────────► probs CSV ──┤
          ├── Hassan: learned model (other games) ► probs CSV ──┤──► Omar: decoder (HMM) ──► <team>.csv
          └── Smart Tagging prior ──────────────► probs CSV ──┘                                │
                                                                                               ▼
                                                                  Julian: yqf.sanity ──► experiments/log.csv
```

## 1. Possession probabilities

`artifacts/probs/<module>_<version>.csv`, one row per tactical video frame (199,319 rows).

| column | type | meaning |
|---|---|---|
| `frame` | int | 0 … 199318, in order |
| `p_H` | float | probability Barcelona has the ball, ball alive |
| `p_A` | float | probability Athletic has the ball, ball alive |
| `p_D` | float | probability the ball is dead |
| `confidence` | float 0–1 | how much the module trusts this row; 0 = no opinion |

`p_H + p_A + p_D = 1` on every row. A module with no opinion on a frame writes `1/3, 1/3, 1/3`
with `confidence = 0`. `formats.write_probs` checks all of this.

## 2. Ball track

`artifacts/ball/<module>_<version>.csv`, one row per tactical video frame.

| column | type | meaning |
|---|---|---|
| `frame` | int | 0 … 199318 |
| `x`, `y` | float | pitch position, normalised 0–1 like the ATD; NaN where unknown |
| `source` | str | `atd`, `interp`, `detector`, … |
| `conf` | float 0–1 | detector confidence; 1 for ATD rows |

## 3. Submission

The official contract — see `SUBMISSION.md`. Written to `evaluation/results/<name>.csv`
(gitignored); the final one is `evaluation/results/Y-que-Fue.csv`.

## Rules for everything under `artifacts/`

- It is gitignored and must stay that way: frame-level derivatives of the match data may not be
  published.
- It must be **regenerable by code**. The final submission is rebuilt from `data/` alone, so any
  artifact the pipeline reads (model weights included) needs a script that recreates it, or must
  be downloadable from a public place the technical document names.
- Same input, same output: fix random seeds.
