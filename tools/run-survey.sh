#!/bin/bash
# run-survey.sh — one command: arsenal chain -> binding evaluation -> scored red/blue.
#
# Phases:
#   1. visor-chain-runner.sh <slug>   (tools + ingest; needs the hits file + VPN)
#   2. binding-runner.py              (classify red/blue tasks from the chain's artifacts)
#   3. visorscuba assess              (AI.* + BLUE-* policy scoring over the ledger)
#   4. combined summary
#
# Usage:
#   bash run-survey.sh <slug>                 full pipeline (passive binding eval)
#   bash run-survey.sh <slug> --active        also run probe-requiring bindings
#   bash run-survey.sh <slug> --skip-chain    re-score an existing survey (no probing)
#   bash run-survey.sh <slug> --recon-dir DIR use a specific recon dir
#
# --skip-chain re-runs only phases 2-4 against an already-collected recon dir —
# safe, no probing. The full pipeline's phase 1 needs /tmp/shodan-<slug>-hits.txt
# and the Mullvad tunnel (visor-chain-runner enforces both).
set -euo pipefail

REPO="$HOME/AI-LLM-Infrastructure-OSINT"
NUCLIDE_DB="${NUCLIDE_DB:-$REPO/data/nuclide.db}"

SLUG="${1:-}"
[[ -z "$SLUG" || "$SLUG" == --* ]] && { echo "usage: run-survey.sh <slug> [--active] [--skip-chain] [--recon-dir DIR]" >&2; exit 1; }
shift || true

ACTIVE=""; SKIP_CHAIN=0; RECON_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --active) ACTIVE="--active" ;;
    --skip-chain) SKIP_CHAIN=1 ;;
    --recon-dir) RECON_DIR="$2"; shift ;;
    *) echo "unknown flag: $1" >&2; exit 1 ;;
  esac
  shift
done

# ── Phase 1: arsenal chain ───────────────────────────────────────────────────
if [[ "$SKIP_CHAIN" != "1" ]]; then
  echo "### PHASE 1: arsenal chain (visor-chain-runner.sh $SLUG)"
  bash "$REPO/data/visor-chain-runner.sh" "$SLUG"
else
  echo "### PHASE 1: skipped (--skip-chain)"
fi

# Locate the recon dir (latest for the slug unless overridden).
if [[ -z "$RECON_DIR" ]]; then
  RECON_DIR="$(ls -d "$HOME/recon/${SLUG}-"* 2>/dev/null | sort | tail -1 || true)"
fi
[[ -z "$RECON_DIR" || ! -d "$RECON_DIR" ]] && { echo "ERROR: no recon dir for slug '$SLUG' (looked in ~/recon/${SLUG}-*)" >&2; exit 1; }
echo "    recon-dir: $RECON_DIR"

# ── Phase 2: binding evaluation ──────────────────────────────────────────────
echo
echo "### PHASE 2: binding evaluation"
python3 "$REPO/tools/binding-runner.py" \
  --recon-dir "$RECON_DIR" --db "$NUCLIDE_DB" $ACTIVE \
  -o "$RECON_DIR/binding-results.json"

# ── Phase 3: visorscuba assess (AI.* + BLUE-*) ───────────────────────────────
echo
echo "### PHASE 3: visorscuba assess (AI.* + BLUE-*)"
~/go/bin/VisorScuba assess --db "$NUCLIDE_DB" --json > "$RECON_DIR/scuba-assess.json" 2>/dev/null || true
python3 - "$RECON_DIR/scuba-assess.json" <<'PY'
import json, sys, collections
try:
    data = json.load(open(sys.argv[1]))
except Exception as e:
    print(f"    (assess output unavailable: {e})"); sys.exit(0)
ctrl = collections.Counter()
blue = collections.Counter()
nodes = len(data)
for e in data:
    r = e.get("Result", {})
    for v in (r.get("violations") or []) + (r.get("info") or []):
        cid = v.get("id", "")
        if cid.startswith("BLUE-"):
            blue[cid] += 1
        elif cid.startswith(("AI.", "FO.")):
            ctrl[cid] += 1
print(f"    nodes assessed (ledger-wide): {nodes}")
print(f"    AI.*/FO.* violations: {sum(ctrl.values())} across {len(ctrl)} controls; top: {dict(ctrl.most_common(5))}")
print(f"    BLUE-* violations:    {sum(blue.values())} across {len(blue)} controls; {dict(blue.most_common(8))}")
PY

# ── Phase 4: combined verdict ────────────────────────────────────────────────
echo
echo "### PHASE 4: survey verdict"
python3 - "$RECON_DIR/binding-results.json" <<'PY'
import json, sys, collections
rep = json.load(open(sys.argv[1]))
c = collections.Counter(r["status"] for r in rep["results"])
findings = [r["task"] for r in rep["results"] if r["status"] == "finding"]
print(f"    red/blue bindings: {dict(c)}")
if findings:
    print(f"    FINDINGS: {findings}")
print(f"    artifacts: {sys.argv[1].rsplit('/',1)[0]}/{{binding-results,scuba-assess}}.json")
PY
echo
echo "### DONE — survey '$SLUG' scored."
