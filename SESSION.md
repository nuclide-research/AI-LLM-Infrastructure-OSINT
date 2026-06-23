# SESSION.md -- AI-LLM-Infrastructure-OSINT
Last updated: 2026-06-23

## Last active survey: Cat-33 AI Agent Guardrails (2026-06-23)

### What was done

Full Cat-33 assessment chain run. Primary finding: Galileo agent-control v0.1.0 at 13.68.189.140:8000 (Azure East US) with auth completely off and all 5 policy controls disabled.

43 Shodan dorks executed (see shodan/queries/33-ai-email-guardrails.md). 74 IPs from `http.title:"Agent Control"` dork batch-probed. 3 live, 1 Galileo match.

OSINT Platoon (4 squads) completed. Cascade ran on finding host. aimap fingerprint added for Galileo agent-control. BARE: no corpus coverage (novel class).

### Key findings logged

  case-studies/commercial/galileo-agent-control-unauth-2026-06-23.md -- primary case study
  shodan/cat-33-email-guardrails-2026-06-23/findings-breakdown.txt   -- breakdown
  shodan/cat-33-email-guardrails-2026-06-23/osint-platoon-salute.md  -- SALUTE synthesis
  shodan/cat-33-email-guardrails-2026-06-23/cascade-13.68.189.140.json
  shodan/queries/33-ai-email-guardrails.md (survey results section appended)

### Outstanding (for next session)

  - git commit + push (files staged, user must run):
      cd ~/AI-LLM-Infrastructure-OSINT
      git add shodan/cat-33-email-guardrails-2026-06-23/ shodan/queries/33-ai-email-guardrails.md shodan/query-log.md case-studies/commercial/galileo-agent-control-unauth-2026-06-23.md
      git commit -m "cat-33: Galileo agent-control unauth -- all 5 controls disabled, SSN surface, financial internals"
      git push

  - VisorLog ingest -- needs NDJSON adapter for aimap v2 JSON output
  - VisorCorpus, VisorRAG: TODO (non-blocking)
  - Next category: choose from research program

### Insight candidates

  - SSN-pattern in disabled PII block = strong signal that customer lookup returns SSNs (inference without exfil)
  - deployed-but-disabled is a distinct failure mode: control plane shows as "has guardrails" but active_controls_count=0
  - AWS AgentCore template + Azure deployment + cap modification = third-party operator pattern (not vendor demo)
  - Cat-33 surface is structurally thin: most vendors bind to loopback or are SaaS-only

