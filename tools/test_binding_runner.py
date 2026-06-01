#!/usr/bin/env python3
"""Tests for binding-runner.py parsers. Run: python3 test_binding_runner.py"""
import importlib.util
import os
import sqlite3
import sys
import tempfile

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("br", os.path.join(_here, "binding-runner.py"))
br = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(br)

PASS = FAIL = 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


POS_AIMAP = [{
    "open_ports": [{"host": "1.1.1.1", "port": 3000, "status_code": 200, "server": "uvicorn"}],
    "services": [{"host": "1.1.1.1", "port": 3000, "service": "Langfuse", "severity": "high"}],
    "enum_results": [{"host": "1.1.1.1", "port": 3000, "service": "Langfuse",
                      "auth_status": "none", "risk_level": "critical",
                      "findings": [{"category": "flows", "title": "flows"},
                                   {"category": "exfil_credential", "title": "key"}]}],
}]
NEG_AIMAP = [{
    "open_ports": [{"host": "2.2.2.2", "port": 443, "status_code": 401, "server": ""}],
    "services": [{"host": "2.2.2.2", "port": 443, "service": "Langfuse", "severity": "low"}],
    "enum_results": [{"host": "2.2.2.2", "port": 443, "service": "Langfuse",
                      "auth_status": "required (HTTP 401)", "risk_level": "low", "findings": []}],
}]


def ctx_with(aimap=None, empire_sql=None, db_events=None, vg=None):
    d = tempfile.mkdtemp()
    empire = None
    if empire_sql:
        ep = os.path.join(d, "empire.db")
        con = sqlite3.connect(ep)
        con.executescript(empire_sql)
        con.commit()
        empire = con
    dbp = os.path.join(d, "nuclide.db")
    con = sqlite3.connect(dbp)
    con.execute("CREATE TABLE events(id INTEGER PRIMARY KEY, host_ip TEXT, source TEXT, tags TEXT, lifecycle_status TEXT)")
    for ip, src in (db_events or []):
        con.execute("INSERT INTO events(host_ip,source,lifecycle_status) VALUES(?,?,'open')", (ip, src))
    con.commit(); con.close()
    if vg:
        os.makedirs(os.path.join(d, "visorgraph"))
        with open(os.path.join(d, "visorgraph", "h.json"), "w") as f:
            f.write(vg)
    return {"recon_dir": d, "aimap": aimap, "empire": empire, "db": dbp, "work": d}


def test_positive():
    c = ctx_with(
        aimap=POS_AIMAP,
        empire_sql="CREATE TABLE assets(ip TEXT,port INT,product TEXT,favicon_hash TEXT,notes TEXT);"
                   "INSERT INTO assets VALUES('1.1.1.1',3000,'Langfuse','1727196746','FAVICON-PRESENT DEFAULT-FAVICON:Langflow');",
        db_events=[("1.1.1.1", "survey")],
        vg='{"graph":{"nodes":{"h":{"type":"cert","attrs":{"sans":["admin.mcp.internal"]}}}}}',
    )
    check(br.p_auth001(c)["status"] == "finding", "AUTH-001 should fire on flows")
    check(br.p_auth003(c)["status"] == "finding", "AUTH-003 should fire on exfil_credential")
    check(br.p_sc001(c)["status"] == "finding", "SC-001 should fire on high severity")
    check(br.p_recon001(c)["status"] == "finding", "RECON-001 should fire on product")
    check(br.p_recon005(c)["status"] == "finding", "RECON-005 should fire on port 3000")
    check(br.p_recon003(c)["status"] == "finding", "RECON-003 should fire on DEFAULT-FAVICON")
    check(br.p_recon004(c)["status"] == "finding", "RECON-004 should fire on admin.mcp SAN")
    check(br.p_det001(c)["status"] == "finding", "DET-001 should fire on attributable event")


def test_negative():
    c = ctx_with(
        aimap=NEG_AIMAP,
        empire_sql="CREATE TABLE assets(ip TEXT,port INT,product TEXT,favicon_hash TEXT,notes TEXT);"
                   "INSERT INTO assets VALUES('2.2.2.2',443,'','99','FAVICON-PRESENT');",
        db_events=[],
        vg='{"graph":{"nodes":{"h":{"type":"cert","attrs":{"sans":["www.example.com"]}}}}}',
    )
    check(br.p_auth001(c)["status"] == "control_held", "AUTH-001 held on clean")
    check(br.p_auth003(c)["status"] == "control_held", "AUTH-003 held on clean")
    check(br.p_sc001(c)["status"] == "control_held", "SC-001 held on low sev")
    check(br.p_recon001(c)["status"] == "control_held", "RECON-001 held on no product")
    check(br.p_recon005(c)["status"] == "control_held", "RECON-005 held off-port")
    check(br.p_recon003(c)["status"] == "control_held", "RECON-003 held favicon-present-not-default")
    check(br.p_recon004(c)["status"] == "control_held", "RECON-004 held no descriptive SAN")
    check(br.p_det001(c)["status"] == "control_held", "DET-001 held empty ledger")


def test_missing_artifacts():
    c = {"recon_dir": "/nonexistent", "aimap": None, "empire": None,
         "db": "/nonexistent/x.db", "work": "/tmp"}
    check(br.p_auth001(c)["status"] == "not_evaluated", "AUTH-001 n/a without aimap")
    check(br.p_recon001(c)["status"] == "not_evaluated", "RECON-001 n/a without empire")


if __name__ == "__main__":
    test_positive()
    test_negative()
    test_missing_artifacts()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
