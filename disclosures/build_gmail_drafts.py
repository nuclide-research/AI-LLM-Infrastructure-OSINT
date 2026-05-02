#!/usr/bin/env python3
"""
Convert disclosures/<slug>.md drafts into Gmail-ready JSON.
Outputs disclosures/_gmail_drafts.json with {slug, to, cc, subject, body, severity}.
Excludes already-sent institutions from EXCLUDE list.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "disclosures"

# Already-sent (will be excluded). Update from screenshots.
EXCLUDE = {
    "US-NC-duke",          # Reply confirmed from Anthony Miracle, Duke IT Security
    "KR-POSTECH",          # "18 Cloud Subscriptions including 1 Trillion Parameter Model"
    "IN-shiv-nadar",       # "76 Models including 376GB Local DeepSeek"
    "US-NY-columbia",      # subject names Columbia
    "TH-moph",             # multi-recipient send (icsmph, saraban, thakert)
    "VN-hanoi",            # "Credential Leak — Hanoi University"
    "US-CA-ucsb",          # "3 Live Cloud Proxy Subscriptions"
    "TH-Chulalongkorn",    # "Three Cloud Proxies + Credential Leak — Chulalongkorn"
    "US-NY-rit",           # "18 Cloud Subscriptions" + DGX
    "CN-shandong-med",     # domain sdum.edu.cn unresolvable; no valid contact found
    "KG-krena",            # KRENA — no email path found; NOC contact unverified
}


def parse_draft(path: Path) -> dict:
    text = path.read_text()

    # YAML frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not fm_match:
        raise ValueError(f"no frontmatter in {path}")
    fm_text = fm_match.group(1)
    fm = {}
    for line in fm_text.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip()

    after_fm = text[fm_match.end():].lstrip()

    # Subject (from **Subject:** line)
    subj_match = re.search(r'\*\*Subject:\*\*\s*(.+)', after_fm)
    subject = subj_match.group(1).strip() if subj_match else f"Unauthenticated AI inference endpoint — {fm.get('institution', '')}"

    # Body: drop the "**To:** ... **Subject:** ..." header block (everything before the
    # first standalone "---" separator that precedes "Nicholas Michael Kloster")
    # The case-study draft has structure:
    #   **To:** ...
    #   [**Cc:** ...]
    #   **Subject:** ...
    #
    #   ---
    #
    #   Nicholas Michael Kloster / NuClide Research
    #   ...
    body_start = after_fm.find('Nicholas Michael Kloster / NuClide Research')
    if body_start < 0:
        raise ValueError(f"can't locate body start in {path}")
    body = after_fm[body_start:].rstrip() + '\n'

    return {
        "slug": path.stem,
        "to": fm.get("to", "").strip(),
        "cc": fm.get("cc", "").strip() or None,
        "subject": subject,
        "body": body,
        "severity": fm.get("severity", "HIGH"),
        "ip": fm.get("ip", ""),
        "institution": fm.get("institution", ""),
    }


def main():
    paths = sorted(DRAFTS.glob("*.md"))
    paths = [p for p in paths if p.stem not in ("index",)]

    drafts = []
    excluded = []
    for p in paths:
        if p.stem in EXCLUDE:
            excluded.append(p.stem)
            continue
        try:
            d = parse_draft(p)
            drafts.append(d)
        except Exception as e:
            print(f"[skip] {p.stem}: {e}", file=sys.stderr)

    # Sort: CRITICAL first, then HIGH, then LOW
    sev_order = {"CRITICAL": 0, "HIGH": 1, "LOW": 2}
    drafts.sort(key=lambda d: (sev_order.get(d["severity"], 9), d["slug"]))

    out = DRAFTS / "_gmail_drafts.json"
    out.write_text(json.dumps(drafts, indent=2))

    print(f"\n=== Drafts ready ===")
    print(f"  to send:  {len(drafts)}")
    print(f"  excluded: {len(excluded)} ({', '.join(excluded)})")
    print(f"  output:   {out}")
    print()
    print("=== By severity ===")
    by_sev = {}
    for d in drafts:
        by_sev.setdefault(d["severity"], []).append(d["slug"])
    for sev in ("CRITICAL", "HIGH", "LOW"):
        if sev in by_sev:
            print(f"  {sev}: {len(by_sev[sev])}")
            for s in by_sev[sev]:
                print(f"    - {s}")


if __name__ == "__main__":
    main()
