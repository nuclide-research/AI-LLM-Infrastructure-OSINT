package nuclide_ai_baseline

import future.keywords.in

# NuClide Blue-Team LLM Orchestration Hardening Baseline v1.0
# CC0 — public domain, freely reusable.
#
# 71 BLUE-* controls across 13 domains; 14 are auto+telemetry-scorable today.
# Manual policies (56) are listed in blue_manual_policies but NEVER in
# deny/warn/info — they are excluded from compliance_pct until reviewed.
# BLUE-AUTH-007 was wired 2026-06-01 (aimap exfil_credential / EXFIL-CREDENTIAL
# tag). One stub remains (BLUE-EXP-004): aimap emits no favicon_hash field, so
# the favicon check needs a Shodan facet or a new aimap field — not a sample.
#
# Input fields consumed (all on the Node struct):
#   no_tls, banner_exposed, openapi_docs, browser_control,
#   internal_san_exposed, known_vulnerable, dangerous_endpoint_exposed,
#   is_indexed, authenticated, service_class,
#   no_hitl_approval, no_rate_limit, missing_attribution, no_runtime_detection
#
# Scoring contribution to nuclide_ai_baseline package:
#   deny  → Critical (-3 per violation on the AI baseline score)
#   warn  → High     (-1 per violation)
#   info  → tracked, not scored

# ─── Active auto + telemetry policy IDs (14 total) ───────────────────────────
# Used to compute blue_compliance_pct without counting manual policies.
blue_active_auto_telemetry := {
    "BLUE-NET-001", "BLUE-NET-003", "BLUE-NET-007", "BLUE-NET-008",
    "BLUE-AUTH-001", "BLUE-AUTH-007", "BLUE-SC-001",  "BLUE-AUTHZ-004",
    "BLUE-COST-001", "BLUE-OBS-001", "BLUE-OBS-004",  "BLUE-OBS-006",
    "BLUE-EXP-001",  "BLUE-EXP-002"
}

# ─── Manual policy catalog (56; excluded from scoring) ───────────────────────
blue_manual_policies := {
    "BLUE-NET-002",  "BLUE-NET-004",  "BLUE-NET-005",  "BLUE-NET-006",
    "BLUE-AUTH-002", "BLUE-AUTH-003", "BLUE-AUTH-004", "BLUE-AUTH-005", "BLUE-AUTH-006",
    "BLUE-AUTHZ-001","BLUE-AUTHZ-002","BLUE-AUTHZ-003","BLUE-AUTHZ-005","BLUE-AUTHZ-006","BLUE-AUTHZ-007",
    "BLUE-EGR-001",  "BLUE-EGR-002",  "BLUE-EGR-003",  "BLUE-EGR-004",  "BLUE-EGR-005", "BLUE-EGR-006",
    "BLUE-INJ-001",  "BLUE-INJ-002",  "BLUE-INJ-003",  "BLUE-INJ-004",  "BLUE-INJ-005", "BLUE-INJ-006",
    "BLUE-OUT-001",  "BLUE-OUT-002",  "BLUE-OUT-003",  "BLUE-OUT-004",
    "BLUE-SBX-001",  "BLUE-SBX-002",  "BLUE-SBX-003",  "BLUE-SBX-004",  "BLUE-SBX-005",
    "BLUE-SEC-001",  "BLUE-SEC-002",  "BLUE-SEC-003",  "BLUE-SEC-004",
    "BLUE-SC-002",   "BLUE-SC-003",   "BLUE-SC-004",   "BLUE-SC-005",
    "BLUE-COST-002", "BLUE-COST-003", "BLUE-COST-004",
    "BLUE-RAG-001",  "BLUE-RAG-002",  "BLUE-RAG-003",  "BLUE-RAG-004",
    "BLUE-OBS-002",  "BLUE-OBS-003",  "BLUE-OBS-005",
    "BLUE-EXP-003",  "BLUE-EXP-005"
}

# ─── Stubs ───────────────────────────────────────────────────────────────────
# BLUE-EXP-004: NOT wirable to aimap. Resolved 2026-06-01 — aimap emits no
# favicon_hash field (confirmed from source + empirical run). Favicon-hash
# matching lives in Shodan dorks (http.favicon.hash:), not aimap output. Needs
# a Shodan/Censys favicon facet or a new aimap PortResult.FaviconHash field.
# Stays out of the active set until a real favicon signal exists.

# ─── NET ──────────────────────────────────────────────────────────────────────

# BLUE-NET-001 (High): TLS not enforced on a remote connection.
warn[result] {
    input.no_tls == true
    result := {
        "id":          "BLUE-NET-001",
        "criticality": "High",
        "requirement": "TLS enforced on all endpoints; no plaintext HTTP on any remote connection.",
        "details":     sprintf("Plaintext (no-TLS) connection detected at %v (%v)", [input.host_ip, input.host_hostname]),
    }
}

# BLUE-NET-003 (Critical): dev/inspector tooling (browser-automation backends)
# publicly reachable. Re-uses the browser_control signal that drives AI.C6.
deny[result] {
    input.browser_control == true
    result := {
        "id":          "BLUE-NET-003",
        "criticality": "Critical",
        "requirement": "Dev/inspector tooling not publicly reachable.",
        "details":     sprintf("Browser-automation/inspector backend at %v (%v) — network isolation control missing", [input.host_ip, input.host_hostname]),
    }
}

# BLUE-NET-007 (Low): server/framework version banner exposed.
info[result] {
    input.banner_exposed == true
    result := {
        "id":          "BLUE-NET-007",
        "criticality": "Low",
        "requirement": "Server/framework fingerprints suppressed (no version banners).",
        "details":     sprintf("Version banner exposed at %v — %v", [input.host_ip, input.service_class]),
    }
}

# BLUE-NET-008 (Low): auto-generated API docs (/docs, /redoc, /openapi.json) accessible.
info[result] {
    input.openapi_docs == true
    result := {
        "id":          "BLUE-NET-008",
        "criticality": "Low",
        "requirement": "Auto-generated docs UIs disabled/authenticated in prod (/docs, /redoc, /openapi.json).",
        "details":     sprintf("OpenAPI/Swagger docs endpoint reachable unauthenticated at %v", [input.host_ip]),
    }
}

# ─── AUTH ─────────────────────────────────────────────────────────────────────

# BLUE-AUTH-001 (Critical): endpoint reachable without authentication.
# Fires for any open VisorLog finding where authenticated=false (all open
# survey findings are unauthenticated by definition).
deny[result] {
    input.authenticated == false
    input.service_class != ""
    result := {
        "id":          "BLUE-AUTH-001",
        "criticality": "Critical",
        "requirement": "Every endpoint requires authentication; no public route reaches execution/flow-building.",
        "details":     sprintf("Unauthenticated %v at %v (%v) — BLUE-AUTH-001 hardening control violated", [input.service_class, input.host_ip, input.host_hostname]),
    }
}

# BLUE-AUTH-007 (Critical): an unauthenticated endpoint returned a live auth
# token / session credential. Anchored to aimap's exfil_credential category
# (EXFIL-CREDENTIAL tag). The token value is redacted at the aimap source and
# is never present here — only the boolean presence drives the finding.
deny[result] {
    input.unauth_token_return == true
    result := {
        "id":          "BLUE-AUTH-007",
        "criticality": "Critical",
        "requirement": "No unauthenticated endpoint returns a live auth token/session credential.",
        "details":     sprintf("Unauthenticated endpoint at %v returned a live token/credential (aimap exfil_credential; value redacted at source)", [input.host_ip]),
    }
}

# ─── SUPPLY ───────────────────────────────────────────────────────────────────

# BLUE-SC-001 (High): known-vulnerable version deployed.
warn[result] {
    input.known_vulnerable == true
    result := {
        "id":          "BLUE-SC-001",
        "criticality": "High",
        "requirement": "Core orchestration libs pinned and patched; no known-vulnerable versions deployed.",
        "details":     sprintf("Known-vulnerable version detected at %v (%v) — %v", [input.host_ip, input.host_hostname, input.service_class]),
    }
}

# ─── AUTHZ / TELEMETRY ────────────────────────────────────────────────────────

# BLUE-AUTHZ-004 (Critical, telemetry): consequential action observed with no
# human-approval event preceding it in visorlog.
deny[result] {
    input.no_hitl_approval == true
    result := {
        "id":          "BLUE-AUTHZ-004",
        "criticality": "Critical",
        "requirement": "Human-in-the-loop approval gates on consequential actions (send/delete/transfer/write/spend).",
        "details":     sprintf("Consequential action at %v logged without a preceding human-approval event", [input.host_ip]),
    }
}

# ─── COST / TELEMETRY ─────────────────────────────────────────────────────────

# BLUE-COST-001 (Medium, telemetry): no effective per-key/user throttling.
info[result] {
    input.no_rate_limit == true
    result := {
        "id":          "BLUE-COST-001",
        "criticality": "Medium",
        "requirement": "Per-user/key request and token rate limits enforced at the gateway.",
        "details":     sprintf("No effective per-key/user rate-limiting detected at %v", [input.host_ip]),
    }
}

# ─── OBSERV / TELEMETRY ───────────────────────────────────────────────────────

# BLUE-OBS-001 (High, telemetry): tool call logged without attributable identity.
warn[result] {
    input.missing_attribution == true
    result := {
        "id":          "BLUE-OBS-001",
        "criticality": "High",
        "requirement": "Every tool call/file access/decision logged with the responsible identity.",
        "details":     sprintf("Tool-call/access event at %v has no attributable identity in the ledger", [input.host_ip]),
    }
}

# BLUE-OBS-004 (Medium, telemetry): runtime injection/exfil detection absent.
info[result] {
    input.no_runtime_detection == true
    result := {
        "id":          "BLUE-OBS-004",
        "criticality": "Medium",
        "requirement": "Runtime detection for injection attempts and exfil patterns.",
        "details":     sprintf("No runtime injection/exfil detection coverage at %v", [input.host_ip]),
    }
}

# BLUE-OBS-006 (Medium, auto): known-dangerous framework endpoint reachable.
info[result] {
    input.dangerous_endpoint_exposed == true
    result := {
        "id":          "BLUE-OBS-006",
        "criticality": "Medium",
        "requirement": "WAF blocks unused dangerous framework endpoints.",
        "details":     sprintf("Known-dangerous framework endpoint reachable through the edge at %v", [input.host_ip]),
    }
}

# ─── EXPOSURE ─────────────────────────────────────────────────────────────────

# BLUE-EXP-001 (High, auto): host appears in a public scan index.
# Fires for every open VisorLog finding — presence in the DB implies
# the host was discovered via the survey pipeline (JAXEN/Shodan/Censys).
warn[result] {
    input.is_indexed == true
    result := {
        "id":          "BLUE-EXP-001",
        "criticality": "High",
        "requirement": "No builder UI/dashboard/model endpoint publicly indexed.",
        "details":     sprintf("%v at %v (%v) is publicly indexed and discoverable via passive scan", [input.service_class, input.host_ip, input.host_hostname]),
    }
}

# BLUE-EXP-002 (Low, auto): cert CN/SAN exposes descriptive internal hostname.
info[result] {
    input.internal_san_exposed == true
    result := {
        "id":          "BLUE-EXP-002",
        "criticality": "Low",
        "requirement": "CT logs free of unintended internal hostnames.",
        "details":     sprintf("Descriptive internal SAN/CN in public CT log at %v (%v)", [input.host_ip, input.host_hostname]),
    }
}

# BLUE-EXP-004: STUB — disabled pending RED-RECON-003 sample.
# Survey signal: aimap favicon hash matches a known product default.
# Wire once the aimap favicon_hash field location is confirmed.

# ─── Blue compliance percentage ───────────────────────────────────────────────
# Computed over the 14 active auto+telemetry policies only (the BLUE-EXP-004
# stub and the 56 manual policies are excluded). 100 = none fired on this node.

# Helper: blue_violation_fired(id) is true when any of deny/warn/info
# emitted a result with that id on this input.
blue_violation_fired(id) { v := deny[_]; v.id == id }
blue_violation_fired(id) { v := warn[_]; v.id == id }
blue_violation_fired(id) { v := info[_];  v.id == id }

blue_active_count := count(blue_active_auto_telemetry)

blue_fired_count := count({id | blue_active_auto_telemetry[id]; blue_violation_fired(id)})

blue_compliance_pct := round(((blue_active_count - blue_fired_count) / blue_active_count) * 100)
