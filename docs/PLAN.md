# Plan

**Target: submitted Sat 14 Nov 2026.** Code freeze Wed 11 Nov. 15–17 Nov is buffer only.

## Milestones

| When | Milestone | Owner |
|---|---|---|
| **Tue 27 – Thu 29 Oct** | Data on every machine, `make check-data` + `make submission` pass for everyone. Interfaces agreed. Team name confirmed. | All (Omar leads) |
| **Sun 1 Nov** | **v1**: valid submission beating 0.2433 — dead-ball rules + nearest player + HMM decoder. Validation report v1. | Omar, Julian |
| **Wed 4 Nov** | Ball detector run over the whole match. Smart Tagging analysis done. Public sample games loaded and noised. | Hassan, Julian |
| **Sun 8 Nov** | **v2**: improved ball track + Smart Tagging prior in the decoder. Learned model plugged in. Full draft of the technical document. | All |
| **Wed 11 Nov** | **Code freeze.** Bug fixes only. | All |
| **Thu 12 Nov** | Clean-clone test on a second machine: same file byte for byte. | Hassan / Julian |
| **Fri 13 Nov** | Final technical document. Validator passes on the exact file to upload. | Julian |
| **Sat 14 Nov** | **Submit** (`Y-que-Fue.csv`, `Y-que-Fue.pdf`, repo URL). | Julian submits, Omar checks |

## Omar — pipeline and decoder

- Dead-ball detector (`yqf/deadball.py`): ball off the pitch, ball static, players static or
  clustered, Smart Tagging set pieces. Frames 110,808–113,742 are always `D`.
- HMM / Viterbi decoder (`yqf/decode.py`) over the probability tables, with a high switching
  cost: possession only changes on a *controlled* touch, which is what `spellF1` rewards.
- `X` policy: free inside a possession, expensive across a hand-over.
- Reproducibility: fixed seeds, pinned dependencies, one command.

## Hassan — computer vision and ML

- Ball detection on the tactical video where the ATD has lost it (41% of graded frames):
  detector fine-tuned on the ball, searched near the expected position, projected to the pitch
  with the homography. Output: a ball-track CSV (docs/INTERFACES.md).
- Learned possession model trained on **other** matches (e.g. Metrica's public sample games
  with tracking + events), with synthetic noise matching ours (ball dropped ~41%, slot swaps).
  Output: a probability CSV.
- All video work local only. Weights must be regenerable or publicly downloadable.

## Julian — validation, insight, write-up

- `make sanity` on every version; keep `experiments/log.csv` meaningful (notes!).
- Smart Tagging analysis: which codes to trust, N/A-team throw-ins, set pieces vs dead balls.
- Watch the public 5 minutes against `evaluation/gt/BAR-ATH_possession_gt_public.csv` to write
  down how loose balls, duels and restarts are labelled (watching is fine; labelling is not).
- Technical document (`docs/technical.md` → PDF): approach, assets used/dropped, training data,
  possession rules, limitations, reproduction. Submission checklist.

## If we add 1–2 people

ML/data engineer → takes the learned model off Hassan. Football analyst → pairs with Julian.
