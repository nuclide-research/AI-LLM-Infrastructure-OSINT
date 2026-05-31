# Data Labeling / Annotation Systems — Pre-Assessment OSINT

_Generated: 2026-05-31 from a Stage -1 agentic OSINT pass (4 parallel agents, all WebSearch+WebFetch live-verified against primary sources: official docs, GitHub repos, NVD, GitHub Security Advisories)._
_Category: Data Labeling & Annotation. Companion query catalog: `shodan/queries/22-data-labeling.md` (created 2026-05-09)._

---

## Category thesis

Data-labeling platforms sit at the input boundary of every supervised-learning and RLHF pipeline. They hold the raw data being labeled: PII-dense text, documents, facial and medical imagery, support transcripts, and the human-preference pairs that fine-tune LLMs. The data sensitivity is high by construction.

**Auth-on-default holds for the category, but the finding is the misconfiguration.** Unlike the network-placement-as-auth planes (Insight #71), every platform here ships a real authentication layer, and a 2026-05-04 cheap-VPS pass confirmed doccano at 98.9% auth-on (348/348). So this survey is not a "literal no-auth" hunt. It is a test of whether auth-on-default survives the platform's own default-open knobs:

- **Label Studio**: open self-registration by default (`DISABLE_SIGNUP_WITHOUT_LINK=False`). Anyone who reaches the URL registers, gets an API token, and reads every project and task. Effective-unauth (Insight #10), not literal no-auth.
- **Argilla**: documented default credentials (`owner.apikey` / `argilla.apikey` / password `12345678`) that the quickstart and HF-Spaces images ship and never force-rotate. A universally-known key is effective-unauth.
- **Prodigy**: no built-in auth at all by default (commercial; vendor tells operators to add a proxy). `/get_questions` serves the live annotation corpus.
- **CVAT / doccano**: auth-on for data endpoints, but pre-version-cutoff open registration and the unauth presence endpoints (`/api/server/about`, `/v1/health`, `/swagger/`) plus collocated unauth services (CVAT ships an anonymous-admin Grafana on :3000) are the surface.

**Discovery reframe.** The 2026-05-04 pass scanned cheap VPS (Scaleway/OVH/Linode) and found only doccano. Argilla / Label Studio / CVAT / Prodigy returned zero there because they deploy in managed cloud (AWS/GCP/Azure), K8s, and HF Spaces. The unmapped population lives behind ingress on 80/443 and on the platform-default ports, not on cheap VPS. Discovery here needs port+title dorks without the cheap-VPS org filter, plus Censys full-range and (for Argilla/HF) HF-Spaces enumeration.

**Catalog corrections (this pass).** Two CVE references in the existing query file are wrong and are fixed below: **CVE-2023-38686 is Sydent (Matrix), not Argilla**; **CVE-2022-25011 is RESERVED with no public Label Studio association** (the intended ref is likely CVE-2022-36551, the Label Studio SSRF).

---

## Label Studio (HumanSignal/Heartex)

**Default ports:** 8080 (Docker/nginx external), 8085 (nginx internal/Helm targetPort), 8000 (Django internal), 80 (Helm service behind ingress).
**Auth default:** data endpoints require auth (302 to `/user/login` / 403). Three default-open knobs make it effective-unauth: (1) **open self-registration** `DISABLE_SIGNUP_WITHOUT_LINK=False` -> anyone registers -> full API token -> all projects/tasks; (2) `DEBUG=True` default (Django tracebacks); (3) `SSRF_PROTECTION_ENABLED=False` default.
**Primary dork:** `http.title:"Label Studio" port:8080` (FP low-med). **Secondary:** `http.html:"label-studio-os-package" port:8080` (FP low; the JSON key from unauth `/api/version`). **Ingress tier:** `http.title:"Label Studio"` (no port; 80/443, higher noise).
**Verification probe (3-state):**
- Present: `GET /api/version` -> 200 + body `label-studio-os-package` + `edition`.
- Auth-on: `GET /api/projects` -> 302/403/401.
- **Misconfig (open signup, the finding):** `GET /user/signup` -> 200 + body `Create account` (a 302 here = signup locked).
**Data exposure:** `/api/projects/{id}/tasks` = raw labeled data + annotation history + annotator emails. NLP text/PII, documents, medical imagery, RLHF comparisons.
**Key CVEs:** GHSA-cpmr-mw4j-99r7 (UNAUTH nginx alias path-traversal <=1.7.0, `GET /static../settings/label_studio.py` -> SECRET_KEY, no CVE), CVE-2023-43791 (hardcoded SECRET_KEY <1.8.2, 9.8), CVE-2023-47117 (ORM info-exposure 7.5), CVE-2025-25297 (S3 SSRF -> cloud metadata, 7.7), CVE-2026-22033 (stored XSS + token theft <=1.22.0, 8.6). CVE-2022-25011 in the old catalog is [unverified]; use CVE-2022-36551 (auth'd SSRF, effective-unauth via open signup).
**Default creds:** none post-1.8.2 (SECRET_KEY was hardcoded before). `LABEL_STUDIO_USERNAME`/`_PASSWORD` seed admin if set.
**aimap fingerprint:** `/api/version` -> status 200 + body_contains `label-studio-os-package` + body_contains `edition`. Misconfig second probe: `/user/signup` -> 200 + `Create account` + `label-studio`.
**FP traps:** `/api/version` is unauth on ALL versions (presence, NOT a finding). The open-signup `/user/signup` 200 is the finding. Behind ingress `/api/version` may 404 on subpath strip; try `/version` too.

## CVAT (Computer Vision Annotation Tool)

**Default ports:** 8080 (Traefik HTTP, web+API), 8090 (Traefik dashboard, off by default), **3000 (collocated Grafana shipping `GF_AUTH_ANONYMOUS_ENABLED=true` + `ANONYMOUS_ORG_ROLE=Admin` in docker-compose = unauth admin Grafana on the same host)**.
**Auth default:** `IsAuthenticated` on all API except `/api/server/about` (`permission_classes=[]`, unauth by design). Registration disabled by default post-PR#10229; pre-2.0.0 and `IAM_REGISTRATION_ENABLED=true` builds had open self-registration -> any registrant sees all tasks/imagery. No default admin creds (manual `createsuperuser`).
**Primary dork:** `http.title:"Computer Vision Annotation Tool"` (FP low). **Secondary:** `http.html:"cvat-ui"` (FP med).
**Verification probe (3-state):**
- Present: `GET /api/server/about` -> 200, `Content-Type: application/vnd.cvat+json`, JSON `name`="Computer Vision Annotation Tool" + `version`.
- Auth-on: `GET /api/projects?page_size=1` -> 401/403.
- Misconfig: that probe -> 200 with list (pre-2.0.0 / authz misconfig). Registration open: `/api/auth/register` -> 200.
**Data exposure:** CV training data, medical scans, surveillance/facial video, AV sensor footage. `/api/tasks/{id}/annotations` = raw labeled data; task/project list leaks dataset names, label taxonomy, assignee identities.
**Key CVEs:** CVE-2022-31188 (SSRF no-auth 9.8 <2.0.0), CVE-2025-23045 (Nuclio deserialization RCE 8.7 <2.26.0), CVE-2024-47172 (BOLA, any project/task metadata readable, 7.1 <2.19.1), CVE-2025-48381 (DRF browsable-API info disclosure 5.3 <2.38.0), CVE-2026-23526 (staff self-grant superuser 8.5 <2.55.0). No KEV.
**aimap fingerprint (anti-IAP-FP):** `/api/server/about` -> status 200 + json_field `version` + body_contains `Computer Vision Annotation Tool`. A GCP-IAP catch-all returns HTML, not this JSON object, so it cannot satisfy the json_field+marker conjunction (fixes `reference_aimap_cvat_iap_fp`).
**FP traps:** do not fire on bare 200 (the IAP-catch-all class). `/api/server/health` is not a standard endpoint (404). Grafana :3000 is an infra signal/pivot, not a CVAT finding.

## Argilla (Hugging Face)

**Default ports:** 6900 (near-unique), 9200 (Elasticsearch co-located), 6379 (Redis).
**Auth default:** FastAPI guards all data endpoints; `/api/v1/version` + `/api/v1/status` unauth. Header `X-Argilla-API-Key`. The finding is **documented default creds never rotated**: quickstart/server/HF-Spaces ship `owner.apikey` / `admin.apikey` / `argilla.apikey` (legacy `rubrix.apikey`) with password `12345678`. HF-Spaces is public-by-default (any HF user joins the `argilla` workspace).
**Primary dork:** `port:6900 "argilla"` (FP low). **Secondary:** `http.title:"Argilla"`. **Censys:** `services.http.response.html_title="Argilla" and services.port=6900`. HF-Spaces population needs HF-Hub/CT enumeration (not Shodan-indexable).
**Verification probe (3-state):**
- Present: `GET /api/v1/version` -> 200 + json `version` (semver), no auth.
- Auth-on: `GET /api/v1/me` (no key) -> 401.
- Misconfig (INTEL ONLY, do not authenticate against live hosts): `GET /api/v1/me` with `X-Argilla-API-Key: argilla.apikey` -> 200 = default key live. Document the default-key class; do not exercise it.
**Data exposure:** RLHF preference pairs, instruction-tuning corrections, NER/token labels (PII if medical/legal), annotator notes, verbatim production prompts. `/api/v1/me/datasets` -> dataset enumeration -> `/api/v1/records`.
**Key CVEs:** **none in argilla-io GitHub advisories.** The exposure is the default-credential / no-rotation-gate pattern, not a CVE. (CVE-2023-38686 in the old catalog is Sydent/Matrix, NOT Argilla, confirmed via NVD.)
**aimap fingerprint:** port 6900 filter; `/api/v1/version` -> status 200 + json_field `version` + body_contains `version`. Deep-enum signals (unauth): `/api/v1/status` (version + search_engine + memory).
**FP traps:** port 6900 is near-unique (low FP). "Argo" name overlap is a search-term FP only (Argo Workflows is 2746, different). Rely on the `/api/v1/version` semver JSON, not SPA title. HF-gated 401 != secured (do not conflate).

## doccano

**Default ports:** 8000 (Django dev), 80 (nginx prod). Co-deployed Flower (Celery) on 5555 (often `FLOWER_BASIC_AUTH` unset = unauth).
**Auth default:** `ALLOW_SIGNUP="False"` hardcoded in both compose files (signup off). Default creds **admin/password** (documented install example). `/v1/health` (`{"status":"green"}`) and `/swagger/` unauth; `/openapi.json` exposed on 5.7% (20/348 in the 05-04 pass).
**Primary dork:** `http.title:"doccano" port:8000` (FP low; coined name). **Secondary:** `http.html:"doccano" http.status:200`. **Schema tier:** `http.title:"doccano" http.html:"/v1/health"`.
**Verification probe:** Present: `GET /v1/health` -> 200 + json `status` + `/` body `doccano`. Auth-on: `GET /v1/projects` -> 403; misconfig -> 200 + `{"count":`.
**Data exposure:** `/v1/projects/{id}/examples/` = raw labeled docs (PII in clinical/legal/moderation). `/swagger/` = full API schema disclosure.
**Key CVEs:** CVE-2024-40441 (semi-blind SSRF via auto-labeling Custom REST, 6.6, requires project admin; pivots to Flower :5555 / cloud IMDS). SNYK clickjacking <1.0.1. No KEV. Project is maintenance-only (last release 1.8.5, 2026-01).
**aimap fingerprint:** `/v1/health` -> status 200 + json_field `status` + (secondary `/` body_contains `doccano`).
**FP traps:** `ALLOWED_HOSTS=["*"]`, CORS-allow-all in debug. Flower :5555 is a secondary surface, not a doccano finding.

## Prodigy (Explosion AI)

**Default ports:** 8080 (`--port`/prodigy.json), host bind `0.0.0.0` by default. Commercial (license-key; exposed instances are paying customers).
**Auth default:** **none built-in.** `PRODIGY_BASIC_AUTH_USER/PASS` optional, not set by default -> all endpoints unauth. Vendor doc: "anyone with the URL has access to your data."
**Primary dork:** `http.html:"prodigy.js" port:8080` (FP low-med). **Stronger:** `http.html:"prodigy.js" http.html:"get_questions"` (FP very low). **NAME-COLLISION TRAP:** bare `prodigy` collides massively with Prodigy (band)/music/games; never use unanchored.
**Verification probe:** Present: `GET /health` -> 200 + json `status`=`alive`; `GET /project` -> json with `view_id`. Auth: `GET /get_questions` -> 200 (open, serves live tasks) vs 401/407 (basic-auth set).
**Data exposure:** `/get_questions` = live annotation corpus (clinical NER/PHI, legal, moderation incl. CSAM-training text, enterprise docs). `POST /give_answers` = write. `/docs` Swagger unauth.
**Key CVEs:** none assigned; the design (no-auth-default) is the risk. No KEV.
**aimap fingerprint:** `/health` -> status 200 + json_field `status` + body_contains `status`; secondary `/project` json_field `view_id`. Anchor on `prodigy.js`/`view_id`, never bare `prodigy`.
**FP traps:** port 8080 collides with Label Studio + CVAT; discriminate by JSON-field conjuncts, not port. Named sessions are not auth.

---

## Long-tail annotation tools (triage)

| Tool | Public HTTP server | Port | Marker | Auth default | Add? |
|---|---|---|---|---|---|
| Label Sleuth | Yes | 8000 | title "Label Sleuth: Open source no-code..." | **off** (`login_required:false`) | **Y** auth-off-default, text-classification data |
| INCEpTION | Yes | 8080 | Spring Boot, title "INCEpTION" | **admin/admin** default | Y (low) default creds + actuator risk |
| Potato | Yes | 8000 | title "POTATO 2.0..." | configurable, **passwordless mode** | Y (low) passwordless mode |
| BRAT | Yes (standalone.py) | 8001 | experimental Python server | **none** | Y (cond.) zero-auth but unmaintained/small |
| Universal Data Tool | Yes (Docker) | 3000 | React SPA "no sign up" | none | N (low) niche self-host, no API surface |
| Snorkel Flow | enterprise K8s | TLS | license-gated | required | N enterprise-only |
| Kili / Toloka | SaaS only | n/a | n/a | cloud | N no self-hosted surface |

Priority to fingerprint: Label Studio, CVAT, Argilla, doccano, Prodigy (core) + Label Sleuth, INCEpTION, Potato, BRAT (long-tail).

---

## Candidate insights to test this survey

- **Auth-on-default vs default-open-knobs.** The category has auth, so the finding is whether the platform's own default-open setting (open signup, default API key, no-auth-commercial) re-creates effective-unauth at population scale. Prediction: the platforms with a default-open knob (Label Studio signup, Argilla default key, Prodigy no-auth) show a non-trivial effective-unauth rate; the strict ones (doccano, CVAT post-2.0.0) hold. This isolates "ships auth but ships an open default" as its own failure class distinct from #13/#71.
- **Default-credential-as-effective-unauth.** Argilla's documented, un-rotated key is the cleanest test of the default-credential exposure class (enumerate the class; never exercise the key).
- **Discovery-tier bias (again).** The 05-04 cheap-VPS pass blinded the category to its managed-cloud population. Quantify how much the managed-cloud/HF-Spaces tier changes the picture.

## Limitations / honest negative space

- HF-Spaces Argilla population is not Shodan-indexable; needs HF-Hub/CT enumeration.
- Restraint: Argilla default-key and doccano/INCEpTION default creds are documented as intel only and must NOT be exercised against live hosts. Misconfig is confirmed by the auth-state discriminator (401 vs 200 shape), not by logging in.
- Favicon hashes not recovered live (add as conjuncts once observed).

_Provenance: 4 parallel general-purpose(sonnet) Stage -1 lanes, 2026-05-31. Sources: label studio / cvat / argilla / doccano / prodigy official docs + GitHub repos, NVD, GitHub Security Advisories, HF docs, projectdiscovery/nuclei-templates._
