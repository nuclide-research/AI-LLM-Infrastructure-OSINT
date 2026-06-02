#!/usr/bin/env python3
"""
cat32-severity-correction.py — NuClide Research, 2026-06-02

WHY THIS EXISTS
The cat32-visorlog.ndjson feed was generated with one-api and new-api tagged
event.severity=critical on the assumption that the documented default credential
(root/123456) would be live. The Stage-verify default-cred probe (2026-06-01)
returned 0/40 across both platforms (0/20 each): every sampled operator had
rotated the default. Per the standing hard-proof rule (no CRITICAL without hard
proof) and Insight #68 (state the verification rung), a label cannot claim
CRITICAL when the single probe aimed at that claim came back negative.

Confirmed state for one-api / new-api: admin web UI is SURFACE-OPEN, auth holding
on the sample. The CRITICAL ceiling applies only to the unmeasured fraction of the
population that may still run default creds. The verified floor is MEDIUM (exposed
admin UI of a key-brokering gateway; version-leak via X-New-Api-Version is a
secondary signal, not a severity driver).

Root cause: the ndjson generator assigned severity from the documented-default-cred
threat model without gating on the probe result. This transform corrects the
artifact; the generator should gate severity on auth-state verification in future.

WHAT IT DOES
  - ONE-API / NEW-API records: event.severity critical -> medium, append correction note.
  - All other records (ENVOY-ADMIN critical/confirmed-unauth, LITELLM high,
    KONG-MANAGER high, BIFROST medium) pass through unchanged.
  - Writes cat32-visorlog-corrected.ndjson and prints a before/after tally.
"""
import json
import collections

SRC = "cat32-visorlog.ndjson"
DST = "cat32-visorlog-corrected.ndjson"
NOTE = (" | severity corrected critical->medium 2026-06-02: default-cred probe "
        "0/40 negative on sample; CRITICAL only if default creds, unconfirmed at "
        "population scale (hard-proof discipline, Insight #68)")

before = collections.Counter()
after = collections.Counter()
corrected = 0

with open(SRC) as fin, open(DST, "w") as fout:
    for line in fin:
        r = json.loads(line)
        tags = r.get("nuclide.tags", [])
        sev = r.get("event.severity")
        before[sev] += 1
        if ("ONE-API" in tags or "NEW-API" in tags) and sev == "critical":
            r["event.severity"] = "medium"
            r["notes"] = r.get("notes", "") + NOTE
            corrected += 1
        after[r["event.severity"]] += 1
        fout.write(json.dumps(r) + "\n")

print(f"records read: {sum(before.values())}  corrected: {corrected}")
print(f"severity BEFORE: {dict(before)}")
print(f"severity AFTER:  {dict(after)}")
