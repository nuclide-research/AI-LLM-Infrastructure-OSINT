# SESSION — Cat-34 Self-Hosted LLM-App / RAG Builders

Date: 2026-06-12 | Operator: NuClide (Nick + Claude) | Stance: ai-infra-hunt wardrobe + RAG-poison restraint
Emphasis (Nick's choice): depth on the unauth-default tier + VERIFY (names/schemas, no record/corpus exfil).

## What this survey founded
New category Cat-34: the visual LLM-app / RAG-builder tier (Dify, Langflow, Flowise, RAGFlow, AnythingLLM,
Vanna, Verba, Quivr, PrivateGPT, etc.). 27 platforms characterized into tome. The gap tome didn't cover.

## State of the chain (DONE)
- [-1] OSINT Platoon: 27 platforms -> intel doc + 27 tome JSONs (tome binary rebuilt + PATH-synced) + raw dump.
- [0]  Shodan census: 27 dorks. Insight #104 facet-FP stripped flowise/langflow (144K title -> ~406 real).
       Class verdict (Insight #103): 16/27 quickstart -> unauth UI+API; auth-on-default is the MINORITY.
- [0]  Harvest unauth tier (8 platforms, 47 IPs) -> empire.db (jaxen). hosts.json/ips.txt.
- [0c] scanner: 41/47 live; Insight #77 stripped 5 honeypot/WAF (4 QAnything + 1 Quivr tarpit); shadow
       Qdrant/Ollama/ES/MinIO found under the apps. scan_results.jsonl, scan_classification.json.
- [1b] aimap: 16 services, 2 unauth. [1cm] agent-logging FP scan: Khoj 67%-FP, Langflow/Portainer flagged.
- [3v] VERIFY: refuted Portainer(401)/Langflow(301)/dcm4chee(known FP)/Khoj. 2 HIGH held.
- [0d] Built Vanna aimap fingerprint + restraint enumVanna (SHIPPED, v1.9.54). 6 Vanna auth=none confirmed.
- [0b] Censys BLOCKED (credit bucket). Shodan-dark CONFIRMED 10/11 (Insight #105). FastGPT recovered (noisy).
- [12b] findings-breakdown.txt + continuation-step0d-0b.md written.

## FINDINGS (verified, restraint-held)
- F1 HIGH 95.217.213.59:8080 Weaviate auth=none (Verba RAG store, 7 VERBA_ collections) + Ollama 11434 unauth.
- F2 HIGH 171.225.223.209:6333 Qdrant auth=none (Vanna agent cache); 2nd at 8.138.192.156:6333.
- S2 HIGH-potential 182.92.206.34 Chinese HEALTH platform running Vanna (unauth SQL-exec surface), NOT exercised.
- 11 Vanna instances UI-open (autoinsight.com cluster = 5; exec surface present, not exercised).

## NEXT (queued)
- [3]  aimap-profile on 182.92.206.34 (HIPAA/clinical ethics gate) before anything deeper.
- [2]  VisorGraph cert-pivot on autoinsight.com cluster (operator scope).
- [6/7/8] VisorLog ingest aimap reports -> nuclide.db ; VisorScuba score ; BARE module rank.
- [0b] Censys recovery of the 10 truly-Shodan-dark platforms AFTER bucket reset (2026-07-08) or via FOFA/Quake.
- [13] persist -> GitHub: AWAITS NICK'S GO (not pushed).
- Tool debt: aimap Vanna body-read window (autoinsight miss); aimap Attu/Milvus-admin fingerprint (absent).

## Artifacts (all under this dir)
intel doc: ../../data/platform-intel/cat34-rag-app-builders-osint-2026-06-12.md (+ raw json)
query-log.md, hosts.json, ips.txt, scan_results.jsonl, scan_classification.json,
aimap_report.json, aimap_vanna_verba.json, aimap_fastgpt_attu.json,
findings-breakdown.txt, continuation-step0d-0b.md, empire.db
tome: 27 new platform JSONs in ~/tome/platforms/ ; aimap edits in ~/ai-recon/aimap (uncommitted).
