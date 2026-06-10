#!/usr/bin/env bash
# Lane A — paired-probe re-validation runner.
# Cat-Tabby + Devstral re-survey, 2026-06-09.
#
# Run OUTSIDE Mullvad (or via a second, non-suspect exit) — the whole point
# is to compare against the contaminated first survey.
#
# Sequence:
#   1) 1,217 code-loaded suspect cohort  (fast sanity, ~3-4 min @ 80 workers + 8s gap)
#   2) full 10,895 corpus                 (~25-35 min)
#
# Both feed paired-split.py for stable / unstable / stats / report.

set -euo pipefail
cd "$(dirname "$0")"

echo "[lane-a] step 1/4 — suspect cohort (1,217 code-loaded)"
python3 paired-probe.py \
  --input  code-loaded-hosts.jsonl \
  --output paired-code-1217.jsonl \
  --workers 80 --gap 8

echo "[lane-a] step 2/4 — split + report suspect cohort"
python3 paired-split.py \
  --input  paired-code-1217.jsonl \
  --outdir . \
  --label  code-1217

# Rename the per-cohort stable/unstable files so step 4 doesn't clobber them.
mv ips-paired-stable.txt   ips-paired-stable-code-1217.txt
mv ips-paired-unstable.txt ips-paired-unstable-code-1217.txt

echo "[lane-a] step 3/4 — full corpus (10,895)"
python3 paired-probe.py \
  --input  ollama-corpus.txt \
  --output paired-corpus-10895.jsonl \
  --workers 100 --gap 8

echo "[lane-a] step 4/4 — split + report full corpus"
python3 paired-split.py \
  --input  paired-corpus-10895.jsonl \
  --outdir . \
  --label  corpus-10895

mv ips-paired-stable.txt   ips-paired-stable-corpus.txt
mv ips-paired-unstable.txt ips-paired-unstable-corpus.txt

echo "[lane-a] done. canonical trustworthy file: ips-paired-stable-corpus.txt"
