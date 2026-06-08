#!/usr/bin/env python3
"""
One-time migration of the disclosure-corpus `outcome:` field to the controlled
vocabulary defined in SCHEMA.md. Idempotent: re-running it on already-migrated
files is a no-op.

Run from the disclosures/ directory:

    python3 migrate-outcome-vocab.py [--dry-run]

The mapping is documented in SCHEMA.md ("One-time migration" section).
"""
from __future__ import annotations
import argparse
import glob
import re
import sys

MAPPING = {
    "sent": "sent",
    "pending": "pending",
    "drafted": "pending",
    "acknowledged": "acknowledged",
    "fixed": "fixed",
    "bounced": "bounced",
    "misrouted": "bounced",
    "": None,  # resolved by status
    "declined": "declined",
    "no-response": "no-response",
}

VALID = {"pending", "sent", "acknowledged", "fixed", "declined", "bounced", "no-response"}


def normalize(outcome: str, status: str) -> str | None:
    o = (outcome or "").strip().strip("'\"").lower()
    s = (status or "").strip().strip("'\"").upper()
    if o in VALID:
        return o
    if o in MAPPING:
        mapped = MAPPING[o]
        if mapped is None:
            return "pending" if s == "DRAFT" else "sent"
        return mapped
    return None


def migrate(path: str, dry_run: bool) -> tuple[bool, str]:
    text = open(path).read()
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return False, "no-frontmatter"
    fm = m.group(1)
    outcome_match = re.search(r"^outcome:\s*(.*)$", fm, re.MULTILINE)
    status_match = re.search(r"^status:\s*(.*)$", fm, re.MULTILINE)
    outcome = outcome_match.group(1).strip() if outcome_match else ""
    status = status_match.group(1).strip() if status_match else ""
    new_outcome = normalize(outcome, status)
    if new_outcome is None:
        return False, f"unknown-outcome:{outcome!r}"
    if new_outcome == outcome.strip("'\""):
        return False, "no-change"
    new_fm = re.sub(
        r"^outcome:\s*.*$",
        f"outcome: {new_outcome}",
        fm,
        count=1,
        flags=re.MULTILINE,
    ) if outcome_match else fm + f"\noutcome: {new_outcome}"
    new_text = text.replace(fm, new_fm, 1)
    if dry_run:
        return True, f"WOULD-CHANGE outcome: {outcome!r} → {new_outcome!r}"
    open(path, "w").write(new_text)
    return True, f"CHANGED outcome: {outcome!r} → {new_outcome!r}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    files = sorted(glob.glob("*.md"))
    changed = 0
    skipped = {"no-frontmatter": 0, "no-change": 0}
    errors: list[str] = []
    for f in files:
        ok, note = migrate(f, args.dry_run)
        if ok:
            changed += 1
            print(f"  {f}: {note}")
        elif note in skipped:
            skipped[note] += 1
        else:
            errors.append(f"  {f}: {note}")
    print(f"\nSummary: changed={changed} no-frontmatter={skipped['no-frontmatter']} no-change={skipped['no-change']} errors={len(errors)}")
    if errors:
        print("Errors:")
        for e in errors:
            print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
