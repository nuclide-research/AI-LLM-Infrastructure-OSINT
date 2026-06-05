#!/usr/bin/env python3
"""Add auth_posture + auth_evidence columns to the master registry.
 - auth_posture : codified label from the curated vendor-port-registry.csv
                  default_auth field (OFF/MIXED/ON/...), aggregated per vendor.
 - auth_evidence: empirical unauth/total counts from the nuclide.db event ledger
                  (tags UNAUTH/AUTH + raw.auth_status + raw.service)."""
import csv, re, json, sqlite3, os
from collections import defaultdict

MASTER  = os.path.expanduser("~/github-analysis/port-vendor-registry/MASTER-port-vendor-registry.csv")
CURATED = os.path.expanduser("~/AI-LLM-Infrastructure-OSINT/data/vendor-port-registry.csv")
DB      = os.path.expanduser("~/AI-LLM-Infrastructure-OSINT/data/nuclide.db")

def norm(name):
    n = name.lower().strip()
    n = re.sub(r"\b(server|api|db|service|platform)\b", "", n)
    n = re.sub(r"[^a-z0-9]+", "", n)
    return n

# ── 1. codified posture from curated registry ────────────────────────
# per vendor: collect base auth states + keep richest qualifier
cur_states = defaultdict(set)        # nkey -> {off, on, mixed, trust}
cur_qual   = defaultdict(list)       # nkey -> raw default_auth strings
with open(CURATED, newline="") as f:
    for r in csv.DictReader(f):
        v = (r.get("vendor") or "").strip()
        da = (r.get("default_auth") or "").strip()
        if not v or not da:
            continue
        k = norm(v)
        u = da.upper()
        if u.startswith("OFF"):   cur_states[k].add("off")
        elif u.startswith("ON"):  cur_states[k].add("on")
        elif u.startswith("MIXED"): cur_states[k].add("mixed")
        elif u.startswith("TRUST"): cur_states[k].add("trust")
        else: cur_states[k].add("other")
        if "(" in da:            # keep qualifier notes like OFF (minioadmin:minioadmin)
            cur_qual[k].append(da)

def posture_label(states):
    if not states: return ""
    if "mixed" in states or len(states - {"trust"}) > 1:
        return "mixed"
    if states <= {"off"}:   return "unauth-on-default"
    if states <= {"on"}:    return "auth-on-default"
    if states <= {"trust"}: return "trust-network-only"
    if "off" in states and "on" in states: return "mixed"
    return "mixed"

# ── 2. empirical counts from the event ledger ────────────────────────
con = sqlite3.connect(DB)
emp_unauth = defaultdict(int)
emp_auth   = defaultdict(int)

# build a vendor-token lookup from the master vendor list for tag matching
master_rows = list(csv.DictReader(open(MASTER, newline="")))
vendor_keys = {norm(r["vendor"]): r["vendor"] for r in master_rows}

def vendor_from_event(service, tags):
    if service:
        k = norm(service)
        if k in vendor_keys: return k
    # else scan tags for a token that maps to a known vendor
    for t in tags:
        k = norm(t)
        if k in vendor_keys and len(k) > 2:
            return k
    if service:                      # service present but not in master: still key it
        return norm(service)
    return None

for tags_s, raw_s in con.execute("SELECT tags, raw FROM events"):
    try:
        tags = json.loads(tags_s) if tags_s else []
    except Exception:
        tags = []
    service = None
    if raw_s:
        m = re.search(r'"service"\s*:\s*"([^"]+)"', raw_s)
        if m:
            service = m.group(1)
    # determine auth signal
    auth = None
    upper = [t.upper() for t in tags]
    if "UNAUTH" in upper: auth = "unauth"
    elif "AUTH" in upper: auth = "auth"
    if auth is None and raw_s:
        m = re.search(r'"auth_status"\s*:\s*"([^"]+)"', raw_s)
        if m:
            val = m.group(1).lower()
            if "unauth" in val or val in ("open","none","no"): auth = "unauth"
            elif "auth" in val: auth = "auth"
    if auth is None:
        continue
    k = vendor_from_event(service, tags)
    if not k:
        continue
    if auth == "unauth": emp_unauth[k] += 1
    else: emp_auth[k] += 1
con.close()

# ── 3. merge into master ─────────────────────────────────────────────
cols = list(master_rows[0].keys())
# insert auth columns right after severity
idx = cols.index("severity") + 1
cols[idx:idx] = ["auth_posture", "auth_evidence"]

matched_codified = 0
matched_empirical = 0
for r in master_rows:
    k = norm(r["vendor"])
    label = posture_label(cur_states.get(k, set()))
    if label:
        matched_codified += 1
        # append a distinctive qualifier if any (dedup, cap length)
        quals = sorted(set(cur_qual.get(k, [])))
        if quals:
            label = label + " [" + "; ".join(quals[:3]) + "]"
    r["auth_posture"] = label
    u, a = emp_unauth.get(k, 0), emp_auth.get(k, 0)
    if u + a > 0:
        matched_empirical += 1
        r["auth_evidence"] = f"ledger {u}/{u+a} unauth"
    else:
        r["auth_evidence"] = ""

with open(MASTER, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(master_rows)

print(f"master rows                 : {len(master_rows)}")
print(f"  with codified auth_posture: {matched_codified}")
print(f"  with empirical evidence   : {matched_empirical}")
print(f"curated vendors (distinct)  : {len(cur_states)}")
print(f"ledger unauth events binned : {sum(emp_unauth.values())}")
print(f"ledger auth events binned   : {sum(emp_auth.values())}")
# posture distribution
from collections import Counter
c = Counter((r['auth_posture'].split(' [')[0] or '(none)') for r in master_rows)
print("posture distribution:")
for k,n in c.most_common():
    print(f"  {n:4d}  {k}")
