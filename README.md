# Y que Fue — More than a Hack 2027

Our entry for **More than a Hack 2027, Phase 1** (Metrica Sports × FC Barcelona × MWCapital):
label every frame of Barça vs Athletic Club as `H` / `A` / `D` / `X`, ranked on `spellF1`.

The official challenge docs are unchanged in this repo: [OFFICIAL_README.md](OFFICIAL_README.md),
[CHALLENGE.md](CHALLENGE.md), [DATA.md](DATA.md), [EVALUATION.md](EVALUATION.md),
[RULES.md](RULES.md), [SUBMISSION.md](SUBMISSION.md), [FAQ.md](FAQ.md).
Our plan: [docs/PLAN.md](docs/PLAN.md). How modules talk to each other: [docs/INTERFACES.md](docs/INTERFACES.md).

**Deadline Tue 17 Nov 2026 · our target: submitted Sat 14 Nov · code freeze Wed 11 Nov.**

---

## Setup (once, ~10 minutes)

Needs Python **3.11** (`python3.11 --version`; on Mac: `brew install python@3.11` or Anaconda).

```bash
git clone https://github.com/otawfik/Y-que-Fue.git
cd Y-que-Fue
make setup                     # .venv with the pinned dependencies (requirements-lock.txt)
```

Get the data bundle from the competition Drive link and put the files here, with exactly these
names (Drive may add `-002` etc. to a file name — remove it):

```
data/tactical/   BAR-ATH_tactical.mp4  _atd.xml  _atd.txt  _homography.csv  _smart_tagging.xml
data/broadcast/  BAR-ATH_broadcast.mp4 _atd.xml  _atd.txt  _homography.csv   (optional)
```

Then check it all works:

```bash
make check-data                # every file present, at the delivered size
make submission                # builds evaluation/results/Y-que-Fue.csv
make validate                  # official format check
make sanity                    # label-free report -> experiments/log.csv
make score                     # official scorer on the public 5 minutes
```

Today `make submission` reproduces the official `baseline_smooth50` byte for byte — that is the
plumbing test. Our work replaces its stages one at a time.

No `make` on Windows? Run the commands in the [Makefile](Makefile) directly.

---

## Layout

```
yqf/                  our code
  io.py               fast cached ATD loader -> numpy arrays by video frame
  formats.py          the shared probability / ball-track formats (docs/INTERFACES.md)
  pipeline.py         data in -> evaluation/results/Y-que-Fue.csv out
  sanity.py           label-free report + experiment log
  check_data.py       is the bundle unpacked correctly?
experiments/log.csv   one row per version we try (aggregates only, committed)
docs/                 plan, interfaces, and the technical document as it grows
artifacts/            everything generated: caches, probs, ball tracks, weights (gitignored)
data/                 the match bundle (gitignored, never commit it)
games.py evaluation/ starter/   official, untouched — `git pull upstream main` stays clean
```

## Who owns what

| | owns | lives in |
|---|---|---|
| **Omar** | pipeline, dead-ball detector, HMM/Viterbi decoder, reproducibility | `yqf/pipeline.py`, `yqf/deadball.py`, `yqf/decode.py` |
| **Hassan** | ball detection on the tactical video, learned model trained on other matches | `yqf/ball/`, `yqf/learned/` |
| **Julian** | label-free validation, Smart Tagging analysis, technical document, submission checklist | `yqf/sanity.py`, `notebooks/`, `docs/` |

## How we work

- **Branch, then pull request into `main`.** `main` must always build a valid submission.
- **Every version gets a row in the log:** `make all NOTE="what changed"`. Commit first, so the
  row records a clean commit hash.
- **Choose between versions with `make sanity` and the bootstrap
  (`python evaluation/run_evaluation.py --bootstrap 1000`), never by the public 5 minutes.**
  Tuning on them is against the rules and picks the wrong answer (see EVALUATION.md).
- **Never commit data or anything derived from it frame by frame.** `data/`, `artifacts/` and
  result CSVs are gitignored; keep it that way.
- **Never paste data, video or extracts into a cloud AI** (ChatGPT, Claude, Gemini). AI may write
  code and read summary numbers like the tables `make sanity` prints. Terms of use, not advice.
- **No hand labels on this match, ever** — not for the answer, not to train, not to validate.

## Reproducing our submission

```bash
make setup && make check-data && make submission && make validate
```

produces `evaluation/results/Y-que-Fue.csv`, the file we submitted.

## Updates from the organisers

```bash
git remote add upstream https://github.com/metrica-sports/more-than-a-hack-2027.git   # once
git pull upstream main
```

Code: MIT ([LICENSE](LICENSE)), built on the official starter by Metrica Sports. The match data
is not covered and is not in this repository.
