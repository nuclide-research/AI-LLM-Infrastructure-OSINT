# Cat-34 Continuation — Step 0d (Vanna FP) + Step 0b (Censys/Shodan-dark)  2026-06-12

## Step 0d — built Vanna aimap fingerprint + restraint-bounded enumerator (SHIPPED)

Gap found: Verba/Dify/Flowise/Langflow already in aimap; VANNA was absent -> app layer never enumerated.

Edits to ~/ai-recon/aimap (built, vetted, synced to ~/go/bin/aimap, v1.9.54):
- fingerprints.go: added Vanna fingerprint. DefaultPorts 8000,8001,8010,8080,8084,5000,3000.
  Cross-variant probe: GET / status 200 + body_contains "img.vanna.ai" (vendor-unique CDN, both classic
  vanna-flask and "Vanna Agents Chat" variants embed it; anchored to status per naked-keyword lesson).
- fingerprints.go: widened Verba DefaultPorts 8000 -> 8000,8080,8888 (catches 91.134.133.144:8888).
- enumerators.go: added enumVanna + registered "Vanna" in enumeratorRegistry. RESTRAINT IS STRUCTURAL:
  reads only /api/v0/get_config (app metadata) and root UI; physically does NOT call /api/v0/run_sql,
  /generate_sql, or /get_training_data (the exec/exfil primitives). Codify-every-survey: the survey gap
  became a permanent tool capability with restraint baked in.

Re-run on 14 Vanna+Verba hosts -> 6 Vanna confirmed auth=none (UI open):
  93.186.251.106:8000, 152.136.12.140:8080, 182.92.206.34:8080 (HEALTH platform),
  171.225.223.209:8010 (+unauth Qdrant), 138.68.234.144:8001, 8.138.192.156:8000 (+unauth Qdrant).
  autoinsight cluster (93.125.18.85/102/103/112/117) NOT re-matched: aimap body-read window missed the
  late img.vanna.ai marker in their SPA bundle. Confirmed Vanna via Shodan dork + direct restraint probe
  (93.125.18.117:8000/ -> 200 uvicorn Vanna UI). 11 Vanna instances total, all UI-open, exec NOT exercised.
  KNOWN-GAP: tune aimap body-read window or add a 2nd Vanna probe on /api/v0/get_config for the cluster.

## Step 0b — Censys BLOCKED ; Shodan-dark CONFIRMED ; FastGPT recovered (mostly noise)

Censys (cencli): search 422 "insufficient balance" despite 100-credit display. = the feature-credit bucket
is drained, separate from displayed Free User Credits (ref: reference_cencli_feature_credit_bucket).
Censys recovery DEFERRED to bucket reset (free credits reset 2026-07-08). Not a skip — external block.

Shodan loose-variant retry on the 11 Shodan-dark platforms (bare vendor-unique markers):
  10/11 STILL ZERO even bare: hayhooks, localgpt, cognita, casibase, ragapp, h2ogpt, r2r, morphik,
  lobe-chat, kotaemon. Bare markers ("VITE_QA_FOUNDRY_URL", "yaml_pipeline_deploy", "ktem_app_data",
  "R2R-Application") are globally unique to one codebase; 0 = host set ABSENT from Shodan's index.
  -> "Shodan-dark" promoted from hypothesis to VERIFIED conclusion. Need Censys/FOFA/Quake/active scan.

  fastgpt: bare "FastGPT" = 33 (tight "feConfigs" qualifier was the killer). BUT bare dork is noisy:
    ~7 hosts are "Attu" (Milvus admin UI) — FastGPT uses Milvus; Attu lists a fastgpt collection -> matches.
    1 real FastGPT (152.136.114.118 = fastgpt.inquiry.tq-industrial.com) -> 401 auth-on-default WORKING.
    rest = nginx 301/302 redirects + bare-IP titles (unconfirmable).
  aimap on the 7 Attu + 1 FastGPT host -> "No AI/ML services": Milvus gRPC 19530 firewalled, only the Attu
    web UI exposed, and aimap has no Attu fingerprint. KNOWN-GAP: build an Attu fingerprint (Milvus admin).
    Attu hosts = surface present (Shodan title), backing Milvus access NOT confirmed.

## Candidate Insight #105 (codified)
"tight-dork-zero" vs "bare-unique-marker-zero" distinguishes wrong-dork from wrong-sensor. A tight dork at 0
may be over-tightness (Langflow port:7860 collapsed 74,102 -> 3). A BARE globally-unique marker at 0 proves
the host set is absent from the index = genuinely sensor-dark. One bare-marker query converts maybe -> certainty.

## Tool debt opened this survey
- aimap Vanna fingerprint body-read window (autoinsight cluster missed) — tune or add /api/v0/get_config probe.
- aimap Attu (Milvus admin UI) fingerprint — absent; FastGPT/Milvus backing stores invisible without it.
- tome reconcile: vanna.json should reference the new aimap fingerprint (keep tome+aimap in sync).
