#!/usr/bin/env python3
"""Tests for aimap-to-findings.py. Run: python3 test_aimap_to_findings.py
Plain-assert (no pytest dependency)."""
import importlib.util
import json
import os
import sqlite3
import sys
import tempfile

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("a2f", os.path.join(_here, "aimap-to-findings.py"))
a2f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a2f)

PASS = 0
FAIL = 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


SAMPLE = {
    "tool": "aimap",
    "open_ports": [
        {"host": "198.51.100.5", "port": 3000, "status_code": 200,
         "server": "uvicorn", "body_snippet": "langfuse dashboard"},
        {"host": "198.51.100.6", "port": 7860, "status_code": 200, "server": "nginx"},
    ],
    "services": [
        {"host": "198.51.100.5", "port": 3000, "service": "Langfuse", "severity": "high"},
        {"host": "198.51.100.6", "port": 7860, "service": "Langflow", "severity": "critical"},
    ],
    "enum_results": [
        {"host": "198.51.100.5", "port": 3000, "service": "Langfuse",
         "auth_status": "none", "risk_level": "critical",
         "findings": [{"category": "exfil_credential", "title": "Langfuse SDK key exposed", "severity": "critical"}]},
        {"host": "198.51.100.6", "port": 7860, "service": "Langflow",
         "auth_status": "required (HTTP 401)", "risk_level": "high",
         "findings": [{"category": "flows", "title": "flows readable"}]},
    ],
}


def test_dotted_keys_and_categories():
    events = a2f.convert(SAMPLE, "test-src", "test-sector", {})
    check(len(events) == 2, f"expected 2 events, got {len(events)}")
    by_ip = {e["host.ip"]: e for e in events}
    # Dotted ECS keys present (the bug fix).
    e = by_ip["198.51.100.5"]
    for k in ("host.ip", "event.severity", "nuclide.tags", "nuclide.source", "lifecycle.status"):
        check(k in e, f"missing dotted key {k}")
    check(e["host.ip"] == "198.51.100.5", "host.ip wrong")
    # exfil_credential -> EXFIL-CREDENTIAL
    check("EXFIL-CREDENTIAL" in e["nuclide.tags"], f"EXFIL-CREDENTIAL missing: {e['nuclide.tags']}")
    check("LANGFUSE" in e["nuclide.tags"], "platform tag missing")
    check("UNAUTH" in e["nuclide.tags"], "auth_status=none should yield UNAUTH")
    check(e["event.severity"] == "critical", f"severity should be critical, got {e['event.severity']}")
    # Langflow: auth required -> AUTH; flows -> FLOWS
    lf = by_ip["198.51.100.6"]
    check("AUTH" in lf["nuclide.tags"], f"401 should yield AUTH: {lf['nuclide.tags']}")
    check("FLOWS" in lf["nuclide.tags"], f"flows -> FLOWS: {lf['nuclide.tags']}")
    check("LANGFLOW" in lf["nuclide.tags"], "service tag LANGFLOW missing")


def test_favicon_merge():
    db = tempfile.mktemp(suffix=".db")
    con = sqlite3.connect(db)
    con.executescript(
        "CREATE TABLE assets(ip TEXT, port INT, favicon_hash TEXT, notes TEXT);"
        # host .6: hash matches the table directly (no notes marker) -> product resolved
        "INSERT INTO assets VALUES('198.51.100.6',7860,'1727196746','FAVICON-PRESENT');"
        # host .5: favicon present, hash not in table, no marker -> present/no-product
        "INSERT INTO assets VALUES('198.51.100.5',3000,'42','FAVICON-PRESENT');"
        # host .7: hash not in table but a notes marker pre-set -> fallback resolves it
        "INSERT INTO assets VALUES('198.51.100.7',8080,'999','FAVICON-PRESENT DEFAULT-FAVICON:CVAT');"
    )
    con.commit(); con.close()
    table = {1727196746: "Langflow"}  # direct hash->product match
    fav = a2f.load_favicon_markers(db, table)
    check(fav.get("198.51.100.6") == (True, "Langflow"), f"direct table match wrong: {fav.get('198.51.100.6')}")
    check(fav.get("198.51.100.5") == (True, None), f"present-no-product wrong: {fav.get('198.51.100.5')}")
    check(fav.get("198.51.100.7") == (True, "CVAT"), f"notes fallback wrong: {fav.get('198.51.100.7')}")
    events = a2f.convert(SAMPLE, "s", "sec", fav)
    by_ip = {e["host.ip"]: e for e in events}
    lf = by_ip["198.51.100.6"]
    check("FAVICON-PRESENT" in lf["nuclide.tags"], "FAVICON-PRESENT tag missing")
    check(any(t.startswith("DEFAULT-FAVICON") for t in lf["nuclide.tags"]),
          f"DEFAULT-FAVICON tag missing: {lf['nuclide.tags']}")
    check("FAVICON-PRESENT" in by_ip["198.51.100.5"]["nuclide.tags"], "present-only host missing FAVICON-PRESENT")
    check(not any(t.startswith("DEFAULT-FAVICON") for t in by_ip["198.51.100.5"]["nuclide.tags"]),
          "present-only host must not have DEFAULT-FAVICON")
    os.unlink(db)


def test_list_report_shape():
    events = a2f.convert([SAMPLE], "s", "sec", {})
    check(len(events) == 2, "list-wrapped report should yield same events")


if __name__ == "__main__":
    test_dotted_keys_and_categories()
    test_favicon_merge()
    test_list_report_shape()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
