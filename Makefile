# Y que Fue -- More than a Hack 2027. `make help` lists the targets.

PYTHON311 ?= python3.11
PY        ?= .venv/bin/python
TEAM      ?= Y-que-Fue
SUBMISSION = evaluation/results/$(TEAM).csv

.PHONY: help setup check-data baseline submission validate sanity score all

help:
	@echo "make setup        create .venv (Python 3.11) and install pinned dependencies"
	@echo "make check-data   confirm the data bundle is unpacked into data/"
	@echo "make baseline     rebuild the four official baselines"
	@echo "make submission   build $(SUBMISSION) -- the file we hand in"
	@echo "make validate     run the official validator on it"
	@echo "make sanity       label-free report, appended to experiments/log.csv"
	@echo "make score        official scorer on the public 5 minutes (pipeline check, NOT tuning)"
	@echo "make all          submission + validate + sanity"

setup:
	$(PYTHON311) -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements-lock.txt

check-data:
	$(PY) -m yqf.check_data

baseline:
	$(PY) starter/baseline.py

submission:
	$(PY) -m yqf.pipeline --name $(TEAM)

validate:
	$(PY) evaluation/validate_submission.py $(SUBMISSION)

sanity:
	$(PY) -m yqf.sanity $(SUBMISSION) --note "$(NOTE)"

score:
	$(PY) evaluation/run_evaluation.py

all: submission validate sanity
