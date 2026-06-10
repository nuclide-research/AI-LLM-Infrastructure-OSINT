#!/usr/bin/env python3
"""
Lane A — paired-probe splitter & statistics.

Reads paired-probe JSONL (output of paired-probe.py) and emits:
  - ips-paired-stable.txt    trustworthy live cohort (T0==T1 sig, both 200)
  - ips-paired-unstable.txt  rewrite/cache/LB signal cohort (excluded)
  - paired-stats.json        full cohort stats + divergence histogram
  - report.md                human-readable Lane A report

A host is in the trustworthy code-loaded set iff:
  stable == True AND code_models_t0 non-empty AND code_models_t0 == code_models_t1
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--label", default="cohort", help="cohort label for report (e.g. code-1217 or corpus-10895)")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    stable_ips: list[str] = []
    unstable_ips: list[str] = []
    div_hist: Counter = Counter()
    code_loaded_stable: list[dict] = []
    code_loaded_unstable: list[dict] = []
    total = 0
    reached_at_least_once = 0
    both_200 = 0

    with open(args.input) as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            total += 1
            div_hist[rec["divergence_kind"]] += 1
            target = f"{rec['ip']}:{rec['port']}"

            if rec["status_t0"] is not None or rec["status_t1"] is not None:
                reached_at_least_once += 1
            if rec["status_t0"] == 200 and rec["status_t1"] == 200:
                both_200 += 1

            if rec["stable"]:
                stable_ips.append(target)
                if rec["code_models_t0"] and rec["code_models_t0"] == rec["code_models_t1"]:
                    code_loaded_stable.append({
                        "target": target,
                        "code_models": rec["code_models_t0"],
                        "model_count": rec["model_count_t0"],
                    })
            else:
                # Only flag hosts that responded — pure dead hosts are noise, not MITM evidence
                if rec["status_t0"] == 200 or rec["status_t1"] == 200:
                    unstable_ips.append(target)
                    # Did one side claim a code model?
                    if rec["code_models_t0"] or rec["code_models_t1"]:
                        code_loaded_unstable.append({
                            "target": target,
                            "code_models_t0": rec["code_models_t0"],
                            "code_models_t1": rec["code_models_t1"],
                            "divergence_kind": rec["divergence_kind"],
                        })

    (outdir / "ips-paired-stable.txt").write_text("\n".join(stable_ips) + "\n")
    (outdir / "ips-paired-unstable.txt").write_text("\n".join(unstable_ips) + "\n")

    stats = {
        "label": args.label,
        "total_probed": total,
        "reached_at_least_once": reached_at_least_once,
        "both_200": both_200,
        "stable_count": len(stable_ips),
        "unstable_count": len(unstable_ips),
        "stable_pct": round(100 * len(stable_ips) / total, 2) if total else 0,
        "unstable_pct_of_responders": round(
            100 * len(unstable_ips) / max(1, reached_at_least_once), 2
        ),
        "divergence_histogram": dict(div_hist.most_common()),
        "trustworthy_code_loaded_count": len(code_loaded_stable),
        "contaminated_code_loaded_count": len(code_loaded_unstable),
    }
    (outdir / "paired-stats.json").write_text(json.dumps(stats, indent=2))

    # ---- human-readable Markdown report
    lines = []
    lines.append(f"# Lane A — paired-probe report ({args.label})")
    lines.append("")
    lines.append(f"- Total probed: **{total}**")
    lines.append(f"- Reached at least once: **{reached_at_least_once}**")
    lines.append(f"- 200 at both T0 and T1: **{both_200}**")
    lines.append(f"- **STABLE** (sig_T0 == sig_T1, both 200): **{len(stable_ips)}** ({stats['stable_pct']}%)")
    lines.append(f"- **UNSTABLE** (responded but flipped): **{len(unstable_ips)}** ({stats['unstable_pct_of_responders']}% of responders)")
    lines.append("")
    lines.append("## Divergence histogram")
    lines.append("")
    for k, v in div_hist.most_common():
        lines.append(f"- `{k}` — {v}")
    lines.append("")
    lines.append("## Code-model cohort")
    lines.append("")
    lines.append(f"- **Trustworthy code-loaded (stable + matching code_models)**: **{len(code_loaded_stable)}**")
    lines.append(f"- Contaminated code-loaded (one side rewrote): {len(code_loaded_unstable)}")
    lines.append("")
    lines.append("## First 10 trustworthy code-loaded hosts")
    lines.append("")
    lines.append("| target | model_count | code_models |")
    lines.append("|---|---|---|")
    for h in code_loaded_stable[:10]:
        cm = ", ".join(h["code_models"])
        lines.append(f"| `{h['target']}` | {h['model_count']} | {cm} |")
    lines.append("")
    lines.append("## Recommended Lane C verify targets")
    lines.append("")
    lines.append("Pick three definitely-real Devstral-loaded hosts (prefer devstral substring, "
                 "then qwen3-coder, then other code-models):")
    devstral = [h for h in code_loaded_stable if any("devstral" in m.lower() for m in h["code_models"])]
    qwen_coder = [h for h in code_loaded_stable if any("qwen" in m.lower() and "coder" in m.lower() for m in h["code_models"])]
    picks = (devstral + qwen_coder + code_loaded_stable)[:3]
    seen = set()
    final_picks = []
    for h in picks:
        if h["target"] in seen:
            continue
        seen.add(h["target"])
        final_picks.append(h)
        if len(final_picks) == 3:
            break
    for h in final_picks:
        lines.append(f"- `{h['target']}` — code_models: {', '.join(h['code_models'])}")
    lines.append("")

    (outdir / f"report-{args.label}.md").write_text("\n".join(lines))

    # ---- console summary
    print(f"=== {args.label} ===")
    print(f"total              {total}")
    print(f"reached            {reached_at_least_once}")
    print(f"both-200           {both_200}")
    print(f"STABLE             {len(stable_ips)} ({stats['stable_pct']}%)")
    print(f"UNSTABLE responders {len(unstable_ips)} ({stats['unstable_pct_of_responders']}%)")
    print(f"trustworthy code   {len(code_loaded_stable)}")
    print(f"contaminated code  {len(code_loaded_unstable)}")
    print("\ndivergence histogram:")
    for k, v in div_hist.most_common():
        print(f"  {k:40s}  {v}")
    print(f"\nWrote: {outdir}/ips-paired-stable.txt, ips-paired-unstable.txt, paired-stats.json, report-{args.label}.md")

if __name__ == "__main__":
    main()
