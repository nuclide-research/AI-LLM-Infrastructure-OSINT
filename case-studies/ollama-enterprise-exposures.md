# Case Study: Ollama Unauthenticated Exposure: Enterprise Targets

**Researcher:** Nicholas Kloster, Nuclide Research (nicholas@nuclide-research.com)  
**Date:** 2026-05-01  
**Vulnerability:** Unauthenticated `/api/create` model injection, all Ollama versions  
**CVE Reference:** CVE-2025-63389 (filed 2025-12-18, scoped ≤v0.13.5, `first_patched_version: null`, scope understated, never patched)  
**Coordinated Disclosure:** Initiated 2026-05-01 · 90-day window → public 2026-07-30  

---

## Summary

During authorized AI infrastructure reconnaissance on 2026-05-01, Shodan enumeration of exposed Ollama instances (port 11434) identified a cluster of enterprise and critical-infrastructure deployments running versions confirmed vulnerable to unauthenticated model injection. All instances below were reachable from the public internet on their Ollama API port with no authentication enforced.

The injection primitive: a single `POST /api/create` replaces or poisons any loaded model's system prompt, zero bandwidth consumed (reuses existing GGUF blobs), ~512 bytes written, persistent across client reconnections.

**Scope confirmed:** v0.1.0 through v0.22.0 (all versions tested). No patch has ever been released.

---

## Enterprise Target Catalog

| IP | Provider | Version | Org Classification | Models | Cloud Proxy | High-Value Signal |
|----|----------|---------|-------------------|--------|-------------|-------------------|
| 51.89.22.243 | OVH (NVIDIA NCP) | 0.21.1 | **Cybersecurity / GRC Product Company** | threat-intel-assistant, compliance-assistant, threat-intel-creative | No | Custom GRC/threat-intel system prompts (MITRE ATT&CK, ISO 27001, SOC 2, GDPR, HIPAA, PCI-DSS) |
| 35.212.210.179 | GCP | 0.20.4 | **Autonomous Agent, OpenClaw** | voytas26/openclaw-qwen3vl-8b-opt + 9 others | No | System prompt confirms autonomous tool-calling agent with JSON schema; browser/email/shell scope |
| 20.83.212.190 | Azure | 0.17.5 | **Enterprise AI Pipeline, IBM Granite** | ibm/granite4:latest, nomic-embed-text-v2-moe, cloud proxy models | Yes | IBM enterprise model + RAG embeddings pipeline; 14 models |
| 51.222.157.76 | OVH Canada (NVIDIA NCP) | 0.22.0 | **Developer AI Service** | deepseek-coder:6.7b, nomic-embed-text | No | Latest Ollama version; coding assistant + RAG search pipeline |
| 20.109.51.171 | Azure | 0.21.1 | **Enterprise AI Stack** | qwen2.5:7b + 9 others | No | 10 loaded models; enterprise multi-model deployment |
| 40.120.91.15 | Azure | 0.3.13 | **Security Research / Test Env** | my-Hacktest-model:latest | No | Active security testing environment; injection affects researcher workflows |
| **[REDACTED]** | US Electric Utility Co-op | **0.21.0** | **⚡ Critical Infrastructure, Electric Utility** | [REDACTED, CISA notification pending] | Yes | WI/MN electric utility cooperative; CISA notified 2026-05-01, details withheld pending remediation |
| 121.52.212.11 | Beijing Topnew Info&Tech | 0.15.2 | **Commercial AI Developer, CN** | devstral-2:123b-cloud, deepseek-v3.1:671b-cloud, all-minilm:22m + 6 others | Yes | 9 models; Mistral devstral-2 (123B code model) + RAG pipeline |
| 140.245.116.11 | Oracle Corporation | 0.21.2 | **Cloud Provider Infrastructure** | qwen3.5:4b | No | Oracle Corporation ASN, direct cloud provider exposure |
| 18.136.196.142 | Amazon Data Services (SG) | 0.1.34 | **AWS Singapore, Managed** | codellama:13b, openchat:7b, llama3, qwen2.5 | No | ec2-18-136-196-142.ap-southeast-1.compute.amazonaws.com; very old version |
| 54.180.148.108 | AWS Seoul Region | 0.1.34 | **AWS Korea, Managed** | deepseek-r1, llama3, llama2, openchat | No | ec2-54-180-148-108.ap-northeast-2.compute.amazonaws.com; very old version |

---

## Notable Cases

### ⚡ US Electric Utility Cooperative: [REDACTED]

**Classification:** Critical Infrastructure, Electric Utility Cooperative  
**Org:** WI/MN service area (US), identity withheld pending remediation  
**Ollama Version:** 0.21.0  
**Models loaded:** [REDACTED, CISA notification pending]

An electric power co-op running Ollama with cloud proxy models and a coding assistant exposed on the public internet. Model injection here would:

- Poison any AI-assisted code or automation scripts
- Redirect cloud quota to attacker
- Insert attacker-controlled instructions into engineering/IT workflows

**CISA notified:** 2026-05-01. Full details withheld until remediation confirmed or public disclosure date (2026-07-30).  
**Injection cost:** 1 HTTP request, 512 bytes written, zero credentials.

---

### Cybersecurity / GRC Company: `51.89.22.243`

**Classification:** Commercial Cybersecurity Product / GRC Platform  
**Provider:** OVH (NVIDIA NCP partner)  
**Ollama Version:** 0.21.1  
**Custom models with extracted system prompts:**

**`threat-intel-assistant`:**
> "You are a highly specialized threat intelligence analyst. Your primary role is to analyze and provide actionable intelligence on cybersecurity threats, vulnerabilities, and attack techniques. Core capabilities: CVE analysis and CVSS scoring, threat actor profiling and attribution, MITRE ATT&CK technique mapping, incident response guidance, IoC analysis..."

**`compliance-assistant`:**
> "You are a compliance and regulatory expert with deep knowledge of ISO 27001, SOC 2 Type I/II, GDPR, HIPAA, and PCI-DSS frameworks..."

**`threat-intel-creative`:**
> "You are a creative threat intelligence analyst who can think outside the box. You specialize in hypothetical attack scenario planning, red team strategy creation, innovative threat modeling..."

A security product company's AI backend exposed to the public internet. Model injection here doesn't just compromise AI responses, it poisons the threat intelligence and compliance tooling that their customers may be paying for. The "threat-intel-creative" model is particularly notable: replacing its system prompt with attacker-controlled content could generate malicious "red team strategies" that execute in production contexts.

---

### OpenClaw Autonomous Agent: `35.212.210.179`

**Classification:** Autonomous AI Agent Platform  
**Provider:** GCP  
**Ollama Version:** 0.20.4  
**Model:** `voytas26/openclaw-qwen3vl-8b-opt` (10 models total including `qwen3.6:35b`)

**Extracted system prompt (excerpt):**
> "You are an autonomous AI assistant with full tool-calling capabilities. When performing tasks, ALWAYS respond with a JSON object in this exact format: {\"thought\": \"...\", \"tool\": \"...\", \"parameters\": {...}}. Available tools: browser_use, execute_shell_command, read_file, write_file, send_email, calendar_access..."

Autonomous agent with browser automation, shell exec, file read/write, email, and calendar access. Model injection turns the agent's entire reasoning layer over to the attacker. Every autonomous action the agent takes, browsing, file writes, shell commands, executes attacker-controlled instructions. This is full RCE via trust-chain compromise, requiring zero exploit sophistication.

---

### IBM Granite Enterprise Pipeline: `20.83.212.190`

**Classification:** Enterprise AI / RAG Pipeline  
**Provider:** Azure  
**Ollama Version:** 0.17.5  
**Models:** `ibm/granite4:latest`, `nomic-embed-text-v2-moe`, cloud proxy models (14 total)

IBM's `granite4` is a production enterprise LLM. `nomic-embed-text-v2-moe` is a vector embedding model, confirms active RAG pipeline. Cloud proxy models indicate paid API access. Injecting the granite4 system prompt would affect every enterprise workflow using this instance, including document retrieval responses from the RAG stack.

---

### Oracle Corporation: `140.245.116.11`

**Classification:** Cloud Provider Infrastructure  
**ASN:** Oracle Corporation  
**Ollama Version:** 0.21.2  
**Models:** `qwen3.5:4b`

Ollama running directly on Oracle Corporation's own infrastructure (confirmed by ASN attribution, not just a customer instance). Oracle has an active AI cloud product line (OCI Generative AI). Whether this is a test/research instance or production is unclear, but the ASN makes it a uniquely high-signal finding.

---

## Enterprise Risk Amplifiers

Standard Ollama injection affects one operator. These factors amplify impact to organizational scale:

| Amplifier | Present In | Impact |
|-----------|-----------|--------|
| **Multi-tenant shared Ollama** | Multi-user orgs | One injection affects all users |
| **RAG pipelines** | IBM Azure, OVH Developer, Beijing Topnew | Poisoned responses surface through retrieval results |
| **Autonomous agents** | OpenClaw GCP | Injected prompt controls every autonomous action |
| **Cloud proxy models** | US Electric Utility [REDACTED], OVH Canada, Beijing Topnew | Quota hijacking + cloud subscription hijacking |
| **AI backend for security product** | OVH GRC Company | Customers' security intelligence is attacker-controlled |
| **Critical infrastructure operator** | US Electric Utility [REDACTED] | OT/IT automation workflows affected |
| **MCP-connected clients** | Any Claude Desktop / Cursor user | Every connected AI client in the org inherits injection |

---

## Injection Surface by Cloud Provider

Based on Shodan enumeration (2026-05-01):

| Cloud Provider | Exposed Ollama Instances | Enterprise Signal |
|----------------|--------------------------|-------------------|
| AWS | ~7,860 | EC2 hostnames confirm managed deployments |
| Alibaba Cloud | ~6,250 | Chinese commercial AI operators |
| OVH (NVIDIA NCP) | ~2,505 | Highest enterprise density; NCP partner-certified |
| Tencent Cloud | ~3,282 | Chinese cloud-native AI stacks |
| Oracle Cloud | ~799 | Lower count, higher signal per instance |
| Azure | ~1,200 | Enterprise and dev deployments |
| GCP | ~950 | Agent frameworks, ML pipelines |
| Scaleway (NVIDIA NCP) | ~164 | European enterprise |

All instances on all providers are affected. No Ollama version has ever shipped authentication on `/api/create`.

---

## Contact

**Nicholas Kloster, Nuclide Research**  
nicholas@nuclide-research.com  
Coordinated disclosure in progress with Ollama and affected parties.
