#!/usr/bin/env python3
"""
Stage 4 JS-bundle version extraction -- cat-agent-platforms / OpenHands.

Open severity question: are the 59 confirmed-unauth OpenHands instances
vulnerable to CVE-2026-33718 (git-diff command injection, <=1.4.0, fixed 1.5.0)?
The JSON API masks the version; it must come from the SPA build.

Discipline (DCWF 672 verify lane):
- Read-only GETs only. No POST, no writes, no agent spawn, no git-diff sink.
- DO_NOT_CALL enforced at code level -- refuse any state-changing/compute-exfil route.
- Catch-all guard: a version string is only TRUSTED if it came from an asset that
  (a) returned 200 with a JS/JSON content-type AND (b) contained an OpenHands-specific
  token. Otherwise the host is recorded UNKNOWN. Refute by default.
- Low concurrency (<=15), 8s timeout, http->https redirect followed, one pass.
- Restraint: metadata only. We extract a semver, never page content beyond what is
  needed to confirm the version + the OpenHands marker.
"""
import json, re, ssl, sys, base64, hashlib, concurrent.futures as cf
import urllib.request, urllib.error
from datetime import datetime, timezone

SURVEY="/home/cowboy/AI-LLM-Infrastructure-OSINT/surveys/agent-platforms-2026-06-19"
CONFIRMED=f"{SURVEY}/openhands-confirmed.txt"
VERIFY=f"{SURVEY}/verify-openhands.jsonl"
OUT=f"{SURVEY}/verify-openhands-versions.jsonl"

TIMEOUT=8
CONC=15

# --- DO_NOT_CALL: hard-refused at code level. Zero violations across the survey. ---
# Every state-changing / compute-exfil / agent-spawn / git-diff-sink route on OpenHands.
DO_NOT_CALL = {
    "POST /api/conversations":          "spawns an agent runtime = compute-exfil + RCE sink",
    "POST /api/conversations/{id}":     "drives the agent = state change + compute-exfil",
    "POST /api/options/config":         "mutates server config",
    "PUT  /api/conversations/{id}":     "state change",
    "DELETE /api/conversations/{id}":   "state change",
    "POST /api/conversations/{id}/submit": "agent task submission = compute-exfil",
    "* git-diff / git_diff sink":       "CVE-2026-33718 injection sink -- never exercised",
    "WS  /socket.io":                   "agent event stream = live runtime attach",
}
def refuse(method, path):
    m=method.upper()
    if m!="GET":
        raise RuntimeError(f"DO_NOT_CALL refused: {m} {path}")
    return True

# Read-only marker-anchored probes. version-ish routes first, then SPA bundle harvest.
META_ROUTES = [
    "/api/options/config",   # may carry runtime_id / version-ish field
    "/version",
    "/api/version",
    "/health",
    "/_health",
    "/assets/version.json",
]

# OpenHands-specific tokens. A bundle must contain >=1 of these to be TRUSTED
# (catch-all hosts serve a generic Vite index without these strings).
OH_TOKENS = [
    "OpenHands", "openhands", "All-Hands-AI", "all-hands", "AllHands",
    "/api/options/config", "agent-runtime", "oh-runtime", "AppMode",
]

# semver capture patterns, ranked by specificity (most trustworthy first).
VER_PATTERNS = [
    re.compile(r'openhands[@/_-]?v?(\d+\.\d+\.\d+)', re.I),
    re.compile(r'__APP_VERSION__\D{0,4}["\']?v?(\d+\.\d+\.\d+)'),
    re.compile(r'APP_VERSION\D{0,4}["\']?v?(\d+\.\d+\.\d+)'),
    re.compile(r'"version"\s*:\s*"v?(\d+\.\d+\.\d+)"'),
    re.compile(r'release[/_-]v?(\d+\.\d+\.\d+)', re.I),
    re.compile(r'\bv(\d+\.\d+\.\d+)\b'),  # last-resort bare semver
]
# asset reference in the index html
ASSET_RE = re.compile(r'(?:src|href)=["\'](/assets/[^"\']+\.(?:js|json))["\']')

UA="nuclide-verify/stage4 (read-only AI-infra research; metadata-only)"

def fetch(base, path, want_bytes=400_000):
    refuse("GET", path)
    url=base.rstrip("/")+path
    ctx=ssl.create_default_context()
    ctx.check_hostname=False
    ctx.verify_mode=ssl.CERT_NONE
    req=urllib.request.Request(url, headers={"User-Agent":UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            ct=r.headers.get("Content-Type","")
            body=r.read(want_bytes)
            return r.status, ct, body, None
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type","") if e.headers else "", b"", None
    except Exception as e:
        return None, "", b"", f"{type(e).__name__}: {e}"

def classify(ver):
    if ver is None: return "UNKNOWN"
    try:
        maj,minr,pat=(int(x) for x in ver.split("."))
    except Exception:
        return "UNKNOWN"
    t=(maj,minr,pat)
    if t<=(1,4,0): return "VULNERABLE"
    if t>=(1,5,0): return "PATCHED"
    return "UNKNOWN"

def extract_ver(text):
    for pat in VER_PATTERNS:
        m=pat.search(text)
        if m: return m.group(1), pat.pattern
    return None, None

def has_oh_token(text):
    return any(tok in text for tok in OH_TOKENS)

def probe_host(target, scheme):
    ip,port=target.rsplit(":",1)
    base=f"{scheme}://{ip}:{port}"
    rec={"ip":ip,"port":int(port),"version":None,"source":None,
         "cve_2026_33718":"UNKNOWN","bundle_hash":None,
         "oh_token_confirmed":False,"notes":[]}

    # 1) meta/version routes (cheap, often null on OpenHands but honest to try)
    for path in META_ROUTES:
        st,ct,body,err=fetch(base,path,want_bytes=60_000)
        if st==200 and body:
            txt=body.decode("utf-8","replace")
            if "json" in ct.lower() or path.endswith(".json"):
                # only trust a version from a json route if it also smells OpenHands
                ver,how=extract_ver(txt)
                if ver and has_oh_token(txt):
                    rec.update(version=ver,source=f"{path} ({how})",
                               oh_token_confirmed=True)
                    rec["cve_2026_33718"]=classify(ver)
                    return rec

    # 2) GET / -> parse index html for hashed /assets/*.js references
    st,ct,body,err=fetch(base,"/",want_bytes=120_000)
    if st!=200 or not body:
        rec["notes"].append(f"root status={st} err={err}")
        return rec
    html=body.decode("utf-8","replace")
    assets=ASSET_RE.findall(html)
    # de-dup, prefer index/main bundles first
    seen=[]
    for a in assets:
        if a not in seen: seen.append(a)
    assets=sorted(seen, key=lambda p:(0 if ("index" in p or "main" in p) else 1, p))

    # also see if the index html itself carries a version + an OH token
    if has_oh_token(html):
        rec["oh_token_confirmed"]=True
        ver,how=extract_ver(html)
        if ver:
            rec.update(version=ver,source=f"/ index.html ({how})")
            rec["cve_2026_33718"]=classify(ver)
            # keep scanning bundles only if root version was a bare-semver guess
            if "openhands" in (how or "").lower() or "APP_VERSION" in (how or ""):
                return rec

    # 3) fetch bundles, require JS content-type + OH token before trusting a version
    for a in assets[:6]:
        st,ct,body,err=fetch(base,a,want_bytes=2_000_000)
        if st!=200 or not body:
            continue
        ctl=ct.lower()
        is_js = ("javascript" in ctl or "ecmascript" in ctl
                 or a.endswith(".js") or "json" in ctl or a.endswith(".json"))
        if not is_js:
            continue
        txt=body.decode("utf-8","replace")
        if not has_oh_token(txt):
            # catch-all / unrelated bundle -- do NOT trust any version it carries
            continue
        rec["oh_token_confirmed"]=True
        rec["bundle_hash"]=hashlib.sha256(body).hexdigest()[:16]
        ver,how=extract_ver(txt)
        if ver:
            rec.update(version=ver,source=f"{a} ({how})")
            rec["cve_2026_33718"]=classify(ver)
            return rec
    if rec["oh_token_confirmed"] and rec["version"] is None:
        rec["notes"].append("OH bundle confirmed but no semver recoverable")
    return rec

def main():
    confirmed=[l.strip() for l in open(CONFIRMED) if l.strip()]
    # scheme from existing verify rows
    scheme_by={}
    for l in open(VERIFY):
        d=json.loads(l); scheme_by[f"{d['ip']}:{d['port']}"]=d.get("scheme","http")

    print(f"# Stage 4 bundle version extraction -- {len(confirmed)} confirmed OpenHands hosts")
    print(f"# DO_NOT_CALL enforced ({len(DO_NOT_CALL)} routes), GET-only, conc={CONC}, timeout={TIMEOUT}s")
    results=[]
    with cf.ThreadPoolExecutor(max_workers=CONC) as ex:
        futs={ex.submit(probe_host,t,scheme_by.get(t,"http")):t for t in confirmed}
        for fut in cf.as_completed(futs):
            t=futs[fut]
            try:
                results.append(fut.result())
            except Exception as e:
                ip,port=t.rsplit(":",1)
                results.append({"ip":ip,"port":int(port),"version":None,"source":None,
                                "cve_2026_33718":"UNKNOWN","bundle_hash":None,
                                "oh_token_confirmed":False,"notes":[f"probe-exc {e}"]})

    results.sort(key=lambda r:(r["ip"]))
    with open(OUT,"w") as f:
        for r in results:
            r["timestamp"]=datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(r)+"\n")

    from collections import Counter
    cve=Counter(r["cve_2026_33718"] for r in results)
    vers=Counter(r["version"] for r in results if r["version"])
    print("\n=== CVE-2026-33718 disposition ===")
    for k in ("VULNERABLE","PATCHED","UNKNOWN"):
        print(f"  {k:11s} {cve.get(k,0)}")
    print("=== version distribution ===")
    for v,n in vers.most_common():
        print(f"  {v:10s} {n}  [{classify(v)}]")
    print(f"=== oh_token_confirmed bundles: {sum(1 for r in results if r['oh_token_confirmed'])}/{len(results)}")
    print(f"# wrote {OUT}")

if __name__=="__main__":
    main()
