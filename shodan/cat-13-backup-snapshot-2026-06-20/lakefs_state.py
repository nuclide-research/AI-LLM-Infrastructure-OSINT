#!/usr/bin/env python3
"""
lakefs_state.py - read-only lakeFS initialization-state verifier (Cat-13).

Cat-13 relevance: lakeFS is a git-for-data layer over an object store holding ML
datasets/model versions. An UNINITIALIZED lakeFS exposes an open setup endpoint:
the first visitor can POST /api/v1/setup_lakefs to create the admin and seize the
whole data-versioning control plane (and the credentials it mints for the backing
bucket). That POST is a TAKEOVER (write primitive) and is OUT OF SCOPE.

This tool only READS the state via GET /api/v1/setup_lakefs (GET returns the current
state without mutating). state == "not_initialized" => admin is claimable =>
finding = "surface open, access not exercised". We never POST. We never set up.
"""
import sys, json, socket, ssl, re, concurrent.futures as cf

CONNECT_T = 4.0
READ_T = 6.0
PORTS = [8000, 80, 443, 8080]
CONC = 14
CAP = 64 * 1024

def get(ip, port, path):
    use_tls = port == 443
    try:
        raw = socket.create_connection((ip, port), timeout=CONNECT_T)
    except Exception:
        return None
    s = raw
    try:
        if use_tls:
            ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(raw, server_hostname=ip)
        s.sendall(("GET %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: nuclide-cat13-verify\r\n"
                   "Accept: application/json\r\nConnection: close\r\n\r\n" % (path, ip)).encode())
        s.settimeout(READ_T)
        buf = b""
        while len(buf) < CAP:
            try: c = s.recv(8192)
            except Exception: break
            if not c: break
            buf += c
        head, _, body = buf.partition(b"\r\n\r\n")
        m = re.match(rb"HTTP/\d\.\d (\d{3})", head)
        return (int(m.group(1)) if m else None, body[:CAP].decode("latin1", "replace"))
    except Exception:
        return None
    finally:
        try: s.close()
        except Exception: pass

def probe(ip):
    out = {"ip": ip, "lakefs": False, "state": None, "claimable": False, "evidence": None, "port": None}
    for port in PORTS:
        r = get(ip, port, "/api/v1/setup_lakefs")
        if not r:
            continue
        status, body = r
        if "state" in body and ("not_initialized" in body or "initialized" in body):
            out["lakefs"] = True; out["port"] = port
            st = "not_initialized" if "not_initialized" in body else "initialized"
            out["state"] = st
            out["claimable"] = (st == "not_initialized")
            out["evidence"] = body[:200].replace("\n", " ")
            return out
        # fall back: config / version endpoints confirm lakeFS even if setup state hidden
        if status and ("lakeFS" in body or "lakefs" in body):
            out["lakefs"] = True; out["port"] = port
            out["evidence"] = body[:160].replace("\n", " ")
    return out

def main():
    hosts = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    res = []
    with cf.ThreadPoolExecutor(max_workers=CONC) as ex:
        futs = {ex.submit(probe, h): h for h in hosts}
        for i, f in enumerate(cf.as_completed(futs), 1):
            try: r = f.result()
            except Exception as e: r = {"ip": futs[f], "error": str(e)}
            res.append(r)
            if r.get("lakefs"):
                tag = "  *CLAIMABLE-ADMIN*" if r.get("claimable") else ""
                print(f"[{i}/{len(hosts)}] {r['ip']:<16} state={r.get('state')} port={r.get('port')}{tag}", flush=True)
    out_f = sys.argv[2] if len(sys.argv) > 2 else "lakefs-state-results.json"
    json.dump(res, open(out_f, "w"), indent=2)
    lf = [r for r in res if r.get("lakefs")]
    claim = [r for r in res if r.get("claimable")]
    print(f"\n=== {len(hosts)} hosts | {len(lf)} confirmed lakeFS | {len(claim)} claimable (not_initialized) ===")
    print(f"wrote {out_f}")

if __name__ == "__main__":
    main()
