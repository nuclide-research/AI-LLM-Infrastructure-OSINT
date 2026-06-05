#!/usr/bin/env python3
"""Merge the four extracted CSVs into one master vendor registry.
Primary key = normalized vendor name. aimap is the backbone; dorks +
supplementary enrich. port_classes stays a companion (port-level entity)."""
import csv, re, os
from collections import defaultdict

OUT = "/tmp/port-harvest/out"

def norm(name):
    """Normalize a vendor name to a join key."""
    n = name.lower().strip()
    n = re.sub(r"\b(server|api|db|service|platform)\b", "", n)
    n = re.sub(r"[^a-z0-9]+", "", n)   # drop spaces, dots, slashes, dashes
    return n

# canonical category map: collapse casing/wording/date-tag variants
CAT_SYNONYM = {
    "vector databases": "Vector Databases",
    "vector db stragglers": "Vector Databases",
    "elasticsearch search": "Vector Databases",
    "llm runtimes": "Model Serving / LLM Runtimes",
    "model serving": "Model Serving / LLM Runtimes",
    "llm orchestration": "LLM Orchestration",
    "orchestration ui": "LLM Orchestration",
    "rag knowledge base frameworks": "RAG Stacks",
    "rag framework servers": "RAG Stacks",
    "rag stacks": "RAG Stacks",
    "llm safety guardrail": "AI Safety / Guardrail",
    "llm safety guardrail policy": "AI Safety / Guardrail",
    "ai safety eval guardrails": "AI Safety / Guardrail",
    "ai safety eval": "AI Safety / Guardrail",
    "auth policy engines": "Auth / Policy Engines",
    "ai agent platforms": "Agent Frameworks",
    "agent frameworks": "Agent Frameworks",
    "agent memory backends": "Agent Memory",
    "agent memory": "Agent Memory",
    "image generation diffusion": "Image Generation",
    "image generation": "Image Generation",
    "data labeling platforms": "Data Labeling",
    "data labeling": "Data Labeling",
    "model context protocol servers": "MCP Servers",
    "mcp servers": "MCP Servers",
    "container orchestration tier": "Containers / Infra",
    "containers infra": "Containers / Infra",
    "ml platforms": "ML Platforms",
    "notebooks dev": "Notebooks / Dev",
    "jupyter": "Notebooks / Dev",
    "compute orchestration training tier": "GPU / Compute / Training",
    "gpu compute": "GPU / Compute / Training",
    "training experiments": "GPU / Compute / Training",
    "workflow orchestration extended": "Workflow Orchestration",
    "workflow orchestration": "Workflow Orchestration",
    "bi dashboard visualization": "BI / Dashboards",
    "bi dashboards": "BI / Dashboards",
    "observability infra co deployed with ai stacks": "ML Observability",
    "ml observability": "ML Observability",
    "llm observability stragglers": "ML Observability",
    "code assistants category 09": "Code Assistants",
    "code assistants": "Code Assistants",
    "voice audio ai survey 17": "Voice / Audio AI",
    "voice audio ai": "Voice / Audio AI",
    "embedding services": "Embedding Services",
    "medical edge ai": "Medical / Edge AI",
    "ai gateways": "AI Gateways",
    "ai gateways monitoring": "AI Gateways",
    "specialty data layers analytic olap nosql": "Specialty Data / OLAP",
    "specialty data layers duckdb backed apis": "Specialty Data / OLAP",
    "specialty data clickhouse": "Specialty Data / OLAP",
    "exposed api credentials": "Credential Leaks",
    "credential leaks": "Credential Leaks",
    "ml governance data catalog": "ML Governance",
    "ml governance": "ML Governance",
    "fine tuning frameworks": "Fine-tuning Frameworks",
    "service mesh cluster introspection planes": "Service Mesh / Cluster",
    "browser automation": "Browser Automation",
    "gradio": "UI Frameworks (Gradio/Streamlit)",
    "streamlit": "UI Frameworks (Gradio/Streamlit)",
    "classical ml": "ML Platforms",
    "backup snapshot": "Backup / Snapshot",
    "redis management gui": "Specialty Data / OLAP",
    "chatbot frameworks": "Chatbot Frameworks",
    "whatsapp automation": "Chatbot Frameworks",
    "exposed file servers": "Exposed File Servers",
    "adjacent nonai noted for defender handoff": "Adjacent (non-AI)",
    "fingerprinting": "Fingerprinting",
    "additions v1 1": "uncategorized",
}

def _catkey(s):
    s = re.sub(r"\(.*?\)", "", s)               # strip parenthetical/date noise FIRST
    s = s.replace("──", "")
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())  # / - & . -> space
    return re.sub(r"\s+", " ", s).strip()

# normalize synonym map keys through the same function so lookups actually hit
_CATMAP = { _catkey(k): v for k, v in CAT_SYNONYM.items() }

def canon_cat(c):
    if not c:
        return ""
    key = _catkey(c)
    if key in _CATMAP:
        return _CATMAP[key]
    cleaned = re.sub(r"\(.*?\)", "", c.replace("──", "")).strip()
    return cleaned[:1].upper() + cleaned[1:] if cleaned else "uncategorized"

def load(fn):
    p = os.path.join(OUT, fn)
    if not os.path.exists(p):
        return []
    with open(p, newline="") as f:
        return list(csv.DictReader(f))

aimap = load("aimap.csv")
dorks = load("dorks.csv")
supp  = load("supplementary.csv")

# registry keyed by norm(vendor)
reg = {}

def blank():
    return {
        "vendor": "", "category": "", "default_ports": set(), "protocol": "",
        "shodan_dorks": [], "probe_paths": "", "signature_markers": "",
        "severity": "", "has_enumerator": "", "supp_notes": [], "sources": set(),
    }

def ports_of(s):
    return {p.strip() for p in re.split(r"[;,]", s or "") if p.strip().isdigit()}

# --- backbone: aimap ---
for r in aimap:
    k = norm(r["vendor"])
    e = reg.setdefault(k, blank())
    e["vendor"] = r["vendor"]                 # aimap name is canonical
    e["category"] = canon_cat(r["category"])  # aimap category wins
    e["aimap_cat"] = True
    e["default_ports"] |= ports_of(r["default_ports"])
    e["protocol"] = r.get("protocol", "")
    # merge probe data across same-vendor collisions instead of overwrite
    pp = set(filter(None, (e["probe_paths"] + ";" + r.get("probe_paths","")).split(";")))
    e["probe_paths"] = ";".join(sorted(pp))
    sm = set(filter(None, (e["signature_markers"] + ";" + r.get("signature_markers","")).split(";")))
    e["signature_markers"] = ";".join(sorted(sm))
    e["severity"] = r.get("severity", "")
    e["has_enumerator"] = r.get("has_enumerator", "")
    e["sources"].add("aimap")

# --- enrich: dorks ---
for r in dorks:
    k = norm(r["vendor"])
    e = reg.setdefault(k, blank())
    if not e["vendor"]:
        e["vendor"] = r["vendor"]
    if not e.get("aimap_cat"):              # only fill category if aimap didn't set it
        e["category"] = e["category"] or canon_cat(r.get("category", ""))
    e["default_ports"] |= ports_of(r.get("default_ports", ""))
    d = (r.get("shodan_dork") or "").strip()
    if d and d not in e["shodan_dorks"]:
        e["shodan_dorks"].append(d)
    e["sources"].add(r.get("source_repo", "OSINT"))

# --- enrich: supplementary ---
for r in supp:
    k = norm(r["vendor"])
    e = reg.setdefault(k, blank())
    if not e["vendor"]:
        e["vendor"] = r["vendor"]
    e["default_ports"] |= ports_of(r.get("default_ports", ""))
    if not e["protocol"]:
        e["protocol"] = r.get("protocol", "")
    note = (r.get("notes") or "").strip()
    if note:
        e["supp_notes"].append(f"[{r.get('source_repo','')}] {note}")
    e["sources"].add(r.get("source_repo", "supp"))

def fmt_ports(s):
    return ";".join(str(p) for p in sorted(s, key=lambda x: int(x)))

rows = []
for e in reg.values():
    rows.append({
        "vendor": e["vendor"],
        "category": e["category"] or "uncategorized",
        "default_ports": fmt_ports(e["default_ports"]),
        "protocol": e["protocol"],
        "shodan_dorks": " | ".join(e["shodan_dorks"]),
        "probe_paths": e["probe_paths"],
        "signature_markers": e["signature_markers"],
        "severity": e["severity"],
        "has_enumerator": e["has_enumerator"],
        "supplementary_notes": " | ".join(e["supp_notes"]),
        "sources": ";".join(sorted(e["sources"])),
    })

rows.sort(key=lambda r: (r["category"].lower(), r["vendor"].lower()))

cols = ["vendor","category","default_ports","protocol","shodan_dorks",
        "probe_paths","signature_markers","severity","has_enumerator",
        "supplementary_notes","sources"]

master = "/tmp/port-harvest/out/MASTER-port-vendor-registry.csv"
with open(master, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

# stats
have_dork = sum(1 for r in rows if r["shodan_dorks"])
have_fp   = sum(1 for r in rows if "aimap" in r["sources"])
have_port = sum(1 for r in rows if r["default_ports"])
print(f"master rows         : {len(rows)}")
print(f"  with aimap fp     : {have_fp}")
print(f"  with shodan dork  : {have_dork}")
print(f"  with port(s)      : {have_port}")
print(f"  enumerator=yes    : {sum(1 for r in rows if r['has_enumerator']=='yes')}")
cats = sorted({r['category'] for r in rows})
print(f"distinct categories : {len(cats)}")
print(f"written             : {master}")
