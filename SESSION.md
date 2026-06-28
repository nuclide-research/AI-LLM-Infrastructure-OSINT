# SESSION.md -- AI-LLM-Infrastructure-OSINT
Last updated: 2026-06-28

## Last active survey: Cat-MLflow MLflow Tracking Server (2026-06-28)

### What was done

Full cat-mlflow-2026-06-28 assessment chain run.

**Population:**
- Shodan: 315 indexed (strict), 188 combined unique IPs harvested
- Naabu liveness: 156 live port-5000, 41 live port-8080, 164 unique live

**Key findings:**
- 81 confirmed unauth / 130 conclusive = **62.3% unauth rate**
- 1,551+ experiments exposed across unauth instances
- 82 CRITICAL (CVE-2024-37052 RCE) via aimap
- 4 Docker Registry FPs on port 5000 (distinct finding)
- Live exploitation artifact at 168.138.146.91:
    - pwn_cron_root_d74b03 experiment with artifact_loc=file:///etc/cron.d
    - Complete attack chain documented in experiment log (cve_test -> scan_* -> pwn_cron -> pwn_tmp)
- S3 bucket exposure: s3://mlflow-art/ at 103.242.173.183
- Shared-backend cluster: 12 hosts with gateway/chat-* pattern + shared base58 model IDs
- Two-level auth failure: off by default + default creds admin/password when enabled

**Files:**
  shodan/cat-mlflow-2026-06-28/README.md
  shodan/cat-mlflow-2026-06-28/osint-platoon.md      -- OSINT Platoon intel doc
  shodan/cat-mlflow-2026-06-28/ips.txt               -- 188 combined IPs
  shodan/cat-mlflow-2026-06-28/live-5000.txt         -- 156 live port-5000
  shodan/cat-mlflow-2026-06-28/live-8080.txt         -- 41 live port-8080
  shodan/cat-mlflow-2026-06-28/live-all.txt          -- 164 unique live
  shodan/cat-mlflow-2026-06-28/naabu-live.json       -- liveness scan
  shodan/cat-mlflow-2026-06-28/aimap-5000.json       -- aimap 86 services
  shodan/cat-mlflow-2026-06-28/verify-5000.json      -- manual verify results
  shodan/cat-mlflow-2026-06-28/bare-findings.json    -- BARE input
  shodan/cat-mlflow-2026-06-28/bare-output.json      -- BARE ranked modules
  shodan/cat-mlflow-2026-06-28/visorgraph-out.json   -- VisorGraph passive (0 hits)
  shodan/cat-mlflow-2026-06-28/visor-report.html     -- VisorScuba report
  shodan/cat-mlflow-2026-06-28/findings-breakdown.txt -- FINAL

### Survey status: COMPLETE (2026-06-28)

  - pushed: commit 9d76756
  - Insights 103-108 codified
  - Outstanding: VisorRAG (embedding API 401), Censys (422), dev-browser cert sweep, JS-bundle, separate-run tools

### Previous survey

  cat-33-email-guardrails-2026-06-23: Galileo agent-control unauth, 5 controls disabled
  (see shodan/cat-33-email-guardrails-2026-06-23/findings-breakdown.txt)

  git commit pending from cat-33:
      git add shodan/cat-33-email-guardrails-2026-06-23/ shodan/queries/33-ai-email-guardrails.md shodan/query-log.md case-studies/commercial/galileo-agent-control-unauth-2026-06-23.md
      git commit -m "cat-33: Galileo agent-control unauth -- all 5 controls disabled, SSN surface, financial internals"
      git push
