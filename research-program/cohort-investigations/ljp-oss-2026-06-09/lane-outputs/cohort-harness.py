#!/usr/bin/env python3
"""
cohort-harness.py — per-IP investigation harness for the LJP-OSS cohort.

DCWF 621 (Software Developer) + 671 (System Testing & Evaluation Specialist)
Authorized identity-surface assessment. NO POSTs. Read-only.

Per-IP pipeline (8 stages):
  1. scanner banner re-check    (loaded from cohort-megaset-scan.jsonl; no re-scan)
  2. aimap fingerprint          (-ports-class sub2api, 5s timeout, per-IP)
  3. SPA APP_CONFIG extraction  (window.__APP_CONFIG__ regex + JSON parse)
  4. OpenAPI fetch              (/openapi.json: title, version, route inventory)
  5. /v1/models probe           (credential-pool inventory)
  6. /api/system/config probe   (Sub2API server config)
  7. Identity classifier        (Sub2API/Grok2API/OpenClaw/QClaw/SubConv/Spider2Table/metapi/cousin/unknown)
  8. Host class                 (A=open-reg, B=paid, C=aggregator, D=private, E=auth-gate)
  9. Sensitive substring grep   (.gov/.edu/.mil/.bank/major-bank/major-univ, FP-aware)

Outputs:
  - /home/cowboy/syllabus/cohort-perip/<ip>.json   (one per IP)
  - /home/cowboy/syllabus/cohort-perip-master.json (rolled-up array)
  - /home/cowboy/syllabus/cohort-perip-master.csv  (summary table)
  - /home/cowboy/syllabus/summary-621.md           (DCWF 621+671 synthesis)

Concurrency: 20 workers (override w/ CONCURRENCY env). Per-IP timeout: 25s.
"""

import csv
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path.home() / "syllabus"
OUTDIR = ROOT / "cohort-perip"
OUTDIR.mkdir(exist_ok=True)
AIMAP_TMP = Path("/tmp/aimap-perip")
AIMAP_TMP.mkdir(exist_ok=True)

IPS_FILE_PRIMARY = ROOT / "discovery" / "cohort-master-v2.txt"
IPS_FILE_FALLBACK = ROOT / "cohort-megaset.txt"
SCAN_JSONL = ROOT / "cohort-megaset-scan.jsonl"

CONCURRENCY = int(os.environ.get("CONCURRENCY", "20"))
PER_IP_TIMEOUT = int(os.environ.get("PER_IP_TIMEOUT", "25"))
AIMAP_TIMEOUT = "5s"

# Identity-surface probe set (port -> paths)
WEB_PORTS = [80, 443, 8000, 8080, 8081, 8443, 3000, 5000, 9000]
APP_CONFIG_PATHS = ["/", "/index.html"]
PROBE_PATHS = [
    "/openapi.json",
    "/api/system/config",
    "/v1/models",
    "/healthz",
    "/info",
    "/api/version",
    "/.well-known/openid-configuration",
]

# --- Regexes ---
APP_CONFIG_RE = re.compile(
    r"window\.__APP_CONFIG__\s*=\s*(\{[^<]{20,12000}?\})\s*[;<]"
)
TITLE_RE = re.compile(r"<title[^>]*>([^<]+)</title>", re.IGNORECASE)
GENERATOR_RE = re.compile(
    r'<meta\s+name=["\']generator["\']\s+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
SITE_NAME_RE = re.compile(r'"site_name"\s*:\s*"([^"]+)"')
API_BASE_RE = re.compile(r'"api_base_url"\s*:\s*"([^"]*)"')

# --- Classifier patterns: platform tells (in order; first match wins) ---
PLATFORM_RULES = [
    # (label, openapi_title_re, body_re, score)
    ("Sub2API", re.compile(r"Sub2API", re.I), re.compile(r"Sub2API|sub2api", re.I)),
    ("Grok2API", re.compile(r"Grok2API|grok2api", re.I), re.compile(r"grok2api|Grok2API", re.I)),
    ("OpenClaw", re.compile(r"OpenClaw|openclaw", re.I), re.compile(r"OpenClaw|openclaw", re.I)),
    ("QClaw", re.compile(r"QClaw|qclaw", re.I), re.compile(r"QClaw|qclaw", re.I)),
    ("SubConv", re.compile(r"SubConv|subconv", re.I), re.compile(r"SubConv|subconv", re.I)),
    ("Spider2Table", re.compile(r"Spider2Table|spider2table", re.I), re.compile(r"Spider2Table|spider2table", re.I)),
    ("metapi", re.compile(r"\bmetapi\b", re.I), re.compile(r"\bmetapi\b", re.I)),
]

# OAuth + payment tells
OAUTH_FLAGS = [
    "linuxdo_oauth_enabled",
    "wechat_oauth_enabled",
    "github_oauth_enabled",
    "google_oauth_enabled",
    "oidc_oauth_enabled",
    "dingtalk_oauth_enabled",
    "telegram_oauth_enabled",
    "discord_oauth_enabled",
]
PAYMENT_TELLS = [
    "stripe.com",
    "airwallex",
    "alipay",
    "wechat",
    "easypay",
    "paypal",
    "lemonsqueezy",
    "yipay",
]

# --- Sensitive substrings (bounded, FP-aware) ---
SENSITIVE_PATTERNS = [
    (re.compile(r"\b[a-z0-9-]+\.gov\b", re.I), "gov-domain"),
    (re.compile(r"\b[a-z0-9-]+\.mil\b", re.I), "mil-domain"),
    (re.compile(r"\b[a-z0-9-]+\.edu\b", re.I), "edu-domain"),
    (re.compile(r"\b[a-z0-9-]+\.bank\b", re.I), "bank-domain"),
    (re.compile(r"\bstanford\.edu\b", re.I), "stanford"),
    (re.compile(r"\bberkeley\.edu\b", re.I), "berkeley"),
    (re.compile(r"\bharvard\.edu\b", re.I), "harvard"),
    (re.compile(r"\bmit\.edu\b", re.I), "mit"),
    (re.compile(r"\bprinceton\.edu\b", re.I), "princeton"),
    (re.compile(r"\byale\.edu\b", re.I), "yale"),
    (re.compile(r"\bcolumbia\.edu\b", re.I), "columbia"),
    (re.compile(r"\bnasa\.gov\b", re.I), "nasa"),
    (re.compile(r"\bnavy\.mil\b", re.I), "navy"),
    (re.compile(r"\barmy\.mil\b", re.I), "army"),
    (re.compile(r"\bairforce\.mil\b", re.I), "airforce"),
    (re.compile(r"\bdefense\.gov\b", re.I), "defense"),
    (re.compile(r"\bfederal\b", re.I), "federal-keyword"),
    (re.compile(r"\buniversity\b", re.I), "university-keyword"),
    (re.compile(r"\bwellsfargo\b", re.I), "wellsfargo"),
    (re.compile(r"\bchase\.com\b", re.I), "chase"),
    (re.compile(r"\bciti\b", re.I), "citi"),
    (re.compile(r"\bjpmorgan\b", re.I), "jpmorgan"),
    (re.compile(r"\bbofa\b|\bbankofamerica\b", re.I), "bofa"),
    (re.compile(r"\bhospital\b", re.I), "hospital-keyword"),
]

# FP-aware deny (operator brands that match the regex but aren't actually sensitive)
FP_DOMAINS = {
    "edutools.eu.cc",
    "nadhospital.com",
    "free-edu.com",  # observed dummy domain
}


def curl_get(url, timeout=5, max_bytes=80000):
    """Quiet curl GET. Returns dict(status,body,len,err?). NO POST."""
    try:
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-k",
                "--max-time",
                str(timeout),
                "-o",
                "-",
                "-w",
                "\n---STATUS:%{http_code}---",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 2,
            errors="replace",
        )
        out = result.stdout or ""
        m = re.search(r"---STATUS:(\d+)---", out)
        status = int(m.group(1)) if m else 0
        body = re.sub(r"---STATUS:\d+---$", "", out)
        body = body[:max_bytes]
        return {"status": status, "body": body, "len": len(body)}
    except subprocess.TimeoutExpired:
        return {"status": 0, "body": "", "err": "timeout"}
    except Exception as e:
        return {"status": 0, "body": "", "err": str(e)[:120]}


def run_aimap(ip):
    """Run aimap -target <ip> -ports-class sub2api -o /tmp/aimap-perip/<ip>.json -timeout 5s."""
    out_file = AIMAP_TMP / f"{ip}.json"
    try:
        subprocess.run(
            [
                "aimap",
                "-target",
                ip,
                "-ports-class",
                "sub2api",
                "-o",
                str(out_file),
                "-timeout",
                AIMAP_TIMEOUT,
            ],
            capture_output=True,
            timeout=20,
        )
        if out_file.exists():
            try:
                return json.loads(out_file.read_text())
            except Exception:
                return None
    except subprocess.TimeoutExpired:
        return {"_err": "aimap-timeout"}
    except Exception as e:
        return {"_err": f"aimap-{str(e)[:80]}"}
    return None


def extract_app_config(html):
    """Find window.__APP_CONFIG__={...} and return parsed dict (best-effort)."""
    if not html:
        return None
    m = APP_CONFIG_RE.search(html)
    if not m:
        return None
    raw = m.group(1)
    # Try progressively trimmed lengths
    for cut in [len(raw), 8000, 6000, 4000, 2500, 1500]:
        try:
            return json.loads(raw[:cut])
        except Exception:
            continue
    return None


def classify_platform(openapi_title, all_body):
    """Return platform label from openapi title + body content tells."""
    blob = (openapi_title or "") + " " + (all_body or "")
    for label, title_re, body_re in PLATFORM_RULES:
        if openapi_title and title_re.search(openapi_title):
            return label
    for label, title_re, body_re in PLATFORM_RULES:
        if body_re.search(blob):
            return label
    if "openai" in blob.lower() and "api" in blob.lower():
        return "cousin"
    return "unknown"


def classify_host_class(app_config, openapi, models_data, any_200, all_4xx):
    """
    A = open registration  (registration_enabled true)
    B = paid commercial    (payment_enabled true)
    C = aggregator         (multiple model namespaces, no reg/pay)
    D = private/closed     (reg off, pay off, app present)
    E = auth-gate everywhere (no SPA, no openapi, no models — only 401/403/404)
    """
    if app_config:
        pay = bool(app_config.get("payment_enabled"))
        reg = bool(app_config.get("registration_enabled"))
        if reg:
            return "A_open_registration"
        if pay:
            return "B_commercial_paid"
        if models_data and len(models_data) > 30:
            return "C_aggregator"
        return "D_private_closed_pool"
    # No APP_CONFIG. Check for any 200s or evidence of a working web app.
    if openapi or models_data:
        return "D_private_closed_pool"
    if all_4xx or not any_200:
        return "E_auth_gate_everywhere"
    return "unknown"


def check_sensitive(text):
    """FP-aware sensitive substring grep. Returns list of (label, match)."""
    if not text:
        return []
    tl = text.lower()
    # FP gate: if known operator brand present, skip entirely
    for fp in FP_DOMAINS:
        if fp in tl:
            return []
    hits = []
    seen = set()
    for pat, label in SENSITIVE_PATTERNS:
        for m in pat.finditer(text):
            key = (label, m.group(0).lower())
            if key in seen:
                continue
            # Secondary FP gate: ignore matches inside known FP-substring
            ctx_start = max(0, m.start() - 30)
            ctx_end = min(len(text), m.end() + 30)
            ctx = text[ctx_start:ctx_end].lower()
            if any(fp in ctx for fp in FP_DOMAINS):
                continue
            seen.add(key)
            hits.append({"label": label, "match": m.group(0)[:60]})
            if len(hits) >= 10:
                return hits
    return hits


def probe_one(ip, scanner_record):
    """Per-IP harness: stages 1-9."""
    t0 = time.time()
    rec = {
        "ip": ip,
        "ts": int(t0),
        "scanner": scanner_record,            # stage 1
        "aimap": None,                         # stage 2
        "open_ports_aimap": [],
        "app_config": None,                    # stage 3
        "site_name": None,
        "api_base_url": None,
        "registration_enabled": None,
        "payment_enabled": None,
        "registration_email_suffix_whitelist": None,
        "oidc_oauth_provider_name": None,
        "oauth_flags": {},
        "payment_gateways": [],
        "contact_info": None,
        "purchase_subscription_url": None,
        "openapi": None,                       # stage 4
        "openapi_title": None,
        "openapi_version": None,
        "openapi_route_count": 0,
        "openapi_routes_preview": [],
        "models_data": None,                   # stage 5
        "models_count": 0,
        "models_ids_preview": [],
        "system_config": None,                 # stage 6
        "platform": None,                      # stage 7
        "host_class": None,                    # stage 8
        "sensitive_hits": [],                  # stage 9
        "titles_seen": [],
        "generators_seen": [],
        "probes": {},
        "errors": [],
    }

    # ---- stage 2: aimap ----
    aimap = run_aimap(ip)
    if aimap:
        rec["aimap"] = aimap
        rec["open_ports_aimap"] = sorted({
            p.get("port") for p in (aimap.get("open_ports") or []) if p.get("open")
        })

    # ---- stage 3-6: per-port identity-surface probing ----
    any_200 = False
    all_status = []
    body_blob = []  # for platform classifier later

    # Probe priority: aimap-known-open first, then a small canonical web set as
    # backstop (covers cases where aimap got pre-filtered as honeypot or hit a
    # cold cache). Skip ports the scanner record already showed dead.
    scanner_ports = {r.get("port") for r in scanner_record if isinstance(r, dict)}
    aimap_ports = set(rec["open_ports_aimap"])
    candidate_ports = list(aimap_ports | scanner_ports)
    # If neither aimap nor scanner gave us anything, fall back to canonical web set
    if not candidate_ports:
        candidate_ports = WEB_PORTS
    # Bound to web-ish ports only
    candidate_ports = [p for p in candidate_ports if p in WEB_PORTS or p in (80, 443, 8000, 8080, 8081, 8443, 3000, 5000, 9000)]
    # Dedupe + stable order
    seen_ports = set()
    ordered_ports = []
    for p in candidate_ports:
        if p not in seen_ports:
            seen_ports.add(p)
            ordered_ports.append(p)

    for port in ordered_ports:
        scheme = "https" if port in (443, 8443) else "http"
        # Root probe (APP_CONFIG, title, generator)
        port_alive = False
        for root_path in APP_CONFIG_PATHS:
            url = f"{scheme}://{ip}:{port}{root_path}"
            r = curl_get(url, timeout=3)
            if r["status"] == 0:
                continue
            port_alive = True
            all_status.append(r["status"])
            if r["status"] == 200:
                any_200 = True
            key = f"{port}{root_path}"
            rec["probes"][key] = {
                "status": r["status"],
                "len": r["len"],
                "body_head": r["body"][:300],
            }
            body = r["body"]
            body_blob.append(body[:6000])

            # APP_CONFIG (stage 3)
            if not rec["app_config"]:
                cfg = extract_app_config(body)
                if cfg:
                    rec["app_config"] = cfg
                    rec["site_name"] = cfg.get("site_name")
                    rec["api_base_url"] = cfg.get("api_base_url")
                    rec["registration_enabled"] = cfg.get("registration_enabled")
                    rec["payment_enabled"] = cfg.get("payment_enabled")
                    rec["registration_email_suffix_whitelist"] = cfg.get(
                        "registration_email_suffix_whitelist"
                    )
                    rec["oidc_oauth_provider_name"] = cfg.get("oidc_oauth_provider_name")
                    rec["contact_info"] = cfg.get("contact_info") or cfg.get("contact")
                    rec["purchase_subscription_url"] = cfg.get("purchase_subscription_url")
                    for f in OAUTH_FLAGS:
                        if f in cfg:
                            rec["oauth_flags"][f] = bool(cfg.get(f))

            # Payment tells from body
            for t in PAYMENT_TELLS:
                if t in body.lower() and t not in rec["payment_gateways"]:
                    rec["payment_gateways"].append(t)

            # Title + generator
            tm = TITLE_RE.search(body)
            if tm:
                title = tm.group(1).strip()[:80]
                if title and title not in rec["titles_seen"]:
                    rec["titles_seen"].append(title)
            gm = GENERATOR_RE.search(body)
            if gm:
                gen = gm.group(1).strip()[:80]
                if gen and gen not in rec["generators_seen"]:
                    rec["generators_seen"].append(gen)
            break  # only one root probe per port if it returned anything

        # Skip API probes if root never even answered — port is dead/filtered
        if not port_alive:
            continue

        # API endpoint probes
        for path in PROBE_PATHS:
            url = f"{scheme}://{ip}:{port}{path}"
            r = curl_get(url, timeout=3)
            if r["status"] == 0:
                continue
            all_status.append(r["status"])
            if r["status"] == 200:
                any_200 = True
            key = f"{port}{path}"
            rec["probes"][key] = {
                "status": r["status"],
                "len": r["len"],
                "body_head": r["body"][:200],
            }
            body = r["body"]
            body_blob.append(body[:4000])

            # stage 4: openapi
            if path == "/openapi.json" and r["status"] == 200 and body.strip().startswith("{"):
                try:
                    spec = json.loads(body)
                    info = spec.get("info", {}) or {}
                    paths = spec.get("paths", {}) or {}
                    if rec["openapi"] is None:
                        rec["openapi"] = {
                            "port": port,
                            "info_title": info.get("title", ""),
                            "info_version": info.get("version", ""),
                            "route_count": len(paths),
                        }
                        rec["openapi_title"] = info.get("title", "") or None
                        rec["openapi_version"] = info.get("version", "") or None
                        rec["openapi_route_count"] = len(paths)
                        rec["openapi_routes_preview"] = list(paths.keys())[:20]
                except Exception:
                    pass

            # stage 5: /v1/models
            if path == "/v1/models" and r["status"] == 200 and body.strip().startswith("{"):
                try:
                    md = json.loads(body)
                    data = md.get("data") if isinstance(md, dict) else None
                    if isinstance(data, list) and rec["models_data"] is None:
                        rec["models_data"] = {"port": port, "count": len(data)}
                        rec["models_count"] = len(data)
                        ids = []
                        for entry in data[:30]:
                            if isinstance(entry, dict):
                                ids.append(entry.get("id", ""))
                            elif isinstance(entry, str):
                                ids.append(entry)
                        rec["models_ids_preview"] = ids
                except Exception:
                    pass

            # stage 6: /api/system/config
            if path == "/api/system/config" and r["status"] == 200 and body.strip().startswith("{"):
                try:
                    cfg2 = json.loads(body)
                    if rec["system_config"] is None:
                        # Cap to keep per-IP file size sane
                        rec["system_config"] = {"port": port, "config": cfg2}
                except Exception:
                    pass

    # ---- stage 7: identity classifier ----
    all_body = "\n".join(body_blob)
    rec["platform"] = classify_platform(rec["openapi_title"], all_body)

    # ---- stage 8: host class ----
    all_4xx = bool(all_status) and all(400 <= s < 500 for s in all_status)
    rec["host_class"] = classify_host_class(
        rec["app_config"],
        rec["openapi"],
        rec["models_data"]["count"] if rec["models_data"] else None,
        any_200,
        all_4xx,
    )

    # ---- stage 9: sensitive substring grep ----
    rec["sensitive_hits"] = check_sensitive(all_body)

    rec["elapsed_s"] = round(time.time() - t0, 2)

    # Persist per-IP JSON
    out_file = OUTDIR / f"{ip}.json"
    out_file.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    return rec


def load_scanner_records():
    """Index existing scanner JSONL output by IP."""
    by_ip = {}
    if not SCAN_JSONL.exists():
        return by_ip
    for line in SCAN_JSONL.read_text().splitlines():
        try:
            d = json.loads(line)
            ip = d.get("ip")
            if not ip:
                continue
            by_ip.setdefault(ip, []).append(
                {
                    "port": d.get("port"),
                    "protocol": d.get("protocol"),
                    "version": d.get("version"),
                    "os": d.get("os"),
                    "banner_head": (d.get("banner") or "")[:400],
                }
            )
        except Exception:
            continue
    return by_ip


def load_ips():
    if IPS_FILE_PRIMARY.exists():
        src = IPS_FILE_PRIMARY
    else:
        src = IPS_FILE_FALLBACK
    print(f"Loading IPs from {src}", file=sys.stderr)
    ips = []
    for line in src.read_text().splitlines():
        ip = line.strip()
        if ip and not ip.startswith("#"):
            ips.append(ip)
    # dedupe while preserving order
    seen = set()
    uniq = []
    for ip in ips:
        if ip in seen:
            continue
        seen.add(ip)
        uniq.append(ip)
    return uniq, src


def write_master_csv(results, path):
    cols = [
        "ip",
        "host_class",
        "platform",
        "site_name",
        "registration_enabled",
        "payment_enabled",
        "api_base_url",
        "oidc_oauth_provider_name",
        "openapi_title",
        "openapi_version",
        "openapi_route_count",
        "models_count",
        "open_ports_aimap",
        "titles",
        "payment_gateways",
        "oauth_enabled_flags",
        "sensitive_hits",
        "elapsed_s",
    ]
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in results:
            oa_flags = ",".join(k for k, v in (r.get("oauth_flags") or {}).items() if v)
            sens = ";".join(f"{h['label']}:{h['match']}" for h in r.get("sensitive_hits") or [])
            w.writerow(
                [
                    r.get("ip", ""),
                    r.get("host_class", ""),
                    r.get("platform", ""),
                    r.get("site_name", "") or "",
                    r.get("registration_enabled", ""),
                    r.get("payment_enabled", ""),
                    r.get("api_base_url", "") or "",
                    r.get("oidc_oauth_provider_name", "") or "",
                    r.get("openapi_title", "") or "",
                    r.get("openapi_version", "") or "",
                    r.get("openapi_route_count", 0),
                    r.get("models_count", 0),
                    ",".join(str(p) for p in (r.get("open_ports_aimap") or [])),
                    ";".join(r.get("titles_seen") or [])[:200],
                    ",".join(r.get("payment_gateways") or []),
                    oa_flags,
                    sens[:300],
                    r.get("elapsed_s", 0),
                ]
            )


def write_summary_md(results, source_ips_file, total_ips, alive_count, dead_count, path):
    plats = Counter(r.get("platform") or "unknown" for r in results)
    hcs = Counter(r.get("host_class") or "unknown" for r in results)
    sens_hosts = [r for r in results if r.get("sensitive_hits")]

    # Field counts
    f_appconfig = sum(1 for r in results if r.get("app_config"))
    f_openapi = sum(1 for r in results if r.get("openapi"))
    f_models = sum(1 for r in results if r.get("models_data"))
    f_aimap = sum(1 for r in results if r.get("aimap") and not r["aimap"].get("_err"))

    # api_base_url operator pivots
    op = Counter(r.get("api_base_url") for r in results if r.get("api_base_url"))

    lines = []
    lines.append("# Per-IP Investigation Harness — DCWF 621+671 Synthesis")
    lines.append("")
    lines.append(f"_Generated {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())} by `cohort-harness.py`._")
    lines.append("")
    lines.append(f"Source IP list: `{source_ips_file}` (N={total_ips})")
    lines.append(f"Probed: {len(results)} of {total_ips} (alive={alive_count}, dead={dead_count} skipped at scanner)")
    lines.append("")
    lines.append("## Signal extraction (out of probed)")
    lines.append("")
    lines.append(f"| Signal | Count |")
    lines.append(f"|---|---|")
    lines.append(f"| aimap fingerprint returned | {f_aimap} |")
    lines.append(f"| SPA APP_CONFIG captured | {f_appconfig} |")
    lines.append(f"| /openapi.json parsed | {f_openapi} |")
    lines.append(f"| /v1/models with data array | {f_models} |")
    lines.append("")
    lines.append("## Platform distribution")
    lines.append("")
    lines.append("| Platform | Count |")
    lines.append("|---|---|")
    for k, v in plats.most_common():
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("## Host-class distribution (A/B/C/D/E)")
    lines.append("")
    lines.append("| Class | Count | Meaning |")
    lines.append("|---|---|---|")
    classes_doc = {
        "A_open_registration": "open registration enabled (claimable accounts)",
        "B_commercial_paid": "payment_enabled true (commercial reseller)",
        "C_aggregator": "aggregator (large model namespace, no reg/pay)",
        "D_private_closed_pool": "private/closed (app present, reg off, pay off)",
        "E_auth_gate_everywhere": "auth-gate everywhere (only 4xx, no public surface)",
        "unknown": "indeterminate",
    }
    for k, v in hcs.most_common():
        lines.append(f"| {k} | {v} | {classes_doc.get(k, '')} |")
    lines.append("")
    lines.append("## Distinct operator pivots (`api_base_url` from APP_CONFIG)")
    lines.append("")
    lines.append("| Count | api_base_url |")
    lines.append("|---|---|")
    for k, v in op.most_common(25):
        lines.append(f"| {v} | `{k}` |")
    lines.append("")
    lines.append(f"## Sensitive-substring hits ({len(sens_hosts)} hosts)")
    lines.append("")
    if not sens_hosts:
        lines.append("_No hosts surfaced sensitive substrings under the FP-gated regex set._")
    else:
        lines.append("| IP | site_name | host_class | Hits |")
        lines.append("|---|---|---|---|")
        for r in sens_hosts:
            hits = "; ".join(f"`{h['label']}:{h['match']}`" for h in r["sensitive_hits"])
            lines.append(
                f"| {r['ip']} | {r.get('site_name') or ''} | {r.get('host_class') or ''} | {hits} |"
            )
    lines.append("")
    lines.append("## DCWF stance")
    lines.append("")
    lines.append(
        "Per-IP investigation harness executed across "
        f"{total_ips} cohort hosts. "
        f"{len(results)} alive with banner+aimap+APP_CONFIG+openapi+models signals captured. "
        f"Platform distribution: "
        + ", ".join(f"{k}={v}" for k, v in plats.most_common())
        + ". "
        f"Host-class distribution: "
        + ", ".join(f"{k.split('_')[0]}={v}" for k, v in hcs.most_common())
        + ". "
        f"{len(sens_hosts)} hosts with sensitive substring hits (verbatim listed above)."
    )
    lines.append("")
    lines.append("Per-IP records: `~/syllabus/cohort-perip/<ip>.json`")
    lines.append("Master CSV: `~/syllabus/cohort-perip-master.csv`")
    lines.append("Master JSON: `~/syllabus/cohort-perip-master.json`")
    lines.append("")
    lines.append("Identity-surface only; NO POSTs; Mullvad VPN active throughout.")
    lines.append("")
    path.write_text("\n".join(lines))


def main():
    ips, src = load_ips()
    scanner_by_ip = load_scanner_records()
    alive_ips = [ip for ip in ips if ip in scanner_by_ip]
    dead_ips = [ip for ip in ips if ip not in scanner_by_ip]
    print(
        f"Loaded {len(ips)} IPs (alive={len(alive_ips)}, dead={len(dead_ips)})",
        file=sys.stderr,
    )

    # Allow CLI limit for fast smoke tests
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            alive_ips = alive_ips[:limit]
            print(f"Limit: probing first {len(alive_ips)}", file=sys.stderr)
        except ValueError:
            pass

    results = []
    t_start = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = {
            pool.submit(probe_one, ip, scanner_by_ip.get(ip, [])): ip
            for ip in alive_ips
        }
        done = 0
        for fut in as_completed(futures):
            ip = futures[fut]
            done += 1
            try:
                results.append(fut.result(timeout=PER_IP_TIMEOUT * 2))
            except Exception as e:
                results.append(
                    {
                        "ip": ip,
                        "host_class": "unknown",
                        "platform": "unknown",
                        "errors": [str(e)[:120]],
                    }
                )
            if done % 25 == 0 or done == len(futures):
                rate = done / max(1, (time.time() - t_start))
                print(
                    f"  progress {done}/{len(futures)} ({rate:.1f}/s)",
                    file=sys.stderr,
                )

    # Master JSON + CSV
    master_json = ROOT / "cohort-perip-master.json"
    master_json.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    master_csv = ROOT / "cohort-perip-master.csv"
    write_master_csv(results, master_csv)

    # Synthesis
    summary_md = ROOT / "summary-621.md"
    write_summary_md(
        results,
        src.name,
        len(ips),
        len(alive_ips),
        len(dead_ips),
        summary_md,
    )

    elapsed = time.time() - t_start
    print(f"\nHarness complete. {len(results)} records in {elapsed:.1f}s", file=sys.stderr)
    print(f"  per-IP: {OUTDIR}/", file=sys.stderr)
    print(f"  master.json: {master_json}", file=sys.stderr)
    print(f"  master.csv:  {master_csv}", file=sys.stderr)
    print(f"  summary-621.md: {summary_md}", file=sys.stderr)


if __name__ == "__main__":
    main()
