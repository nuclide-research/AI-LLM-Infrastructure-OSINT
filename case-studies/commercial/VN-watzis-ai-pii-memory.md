---
type: host
---

# Watzis / Calmio: Vietnamese AI Assistant: PII Memory Store Exposed via Unauthenticated Qdrant

_NuClide Research · 2026-05-03_

---

## Summary

A production multi-user Vietnamese AI assistant, likely operating under the "Watzis" or "Calmio" brand, runs a Mem0-backed long-term memory stack on a Vultr VPS with no authentication on port 6333. The Qdrant instance stores persistent per-user memories across sessions. Sampled payloads include national ID card discussions, financial wallet data (VND amounts), student scheduling context, and chemistry lab queries, all indexed by MongoDB ObjectID user identifiers and session metadata. Multiple distinct users confirmed. One user (ObjectID `68761612f3ce1c61575b67cb`) has stored Vietnamese citizen identification card information and financial data in plaintext.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, S7069, T5854
- **overlap (Common AI KSATs (all 5 roles)):** K1157, K1158, K22, K6311, K7003

<!-- ksat-tag:auto-generated:end -->

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 149.28.77.155 |
| Hosting | Vultr |
| Country | Unknown operator (Vietnamese product) |
| Open port | 6333 (Qdrant, public, unauthenticated) |
| Memory framework | Mem0 |
| Likely product | Watzis AI assistant / Calmio |
| Discovery date | 2026-05-03 |
| Disclosure status | Pending |

---

## Collections

| Collection | Purpose |
|---|---|
| `watzis_longterm_memory` | Primary persistent user memory |
| `hybrid_watzis_longterm_memory` | Hybrid retrieval variant of above |
| `longterm_memory` | Secondary long-term store |
| `working_memory` | Session-scoped short-term memory |
| `file_context` | File-derived context embeddings |
| `watzis_file_context` | Watzis-namespaced file context |
| `mem0migrations` | Framework migration state |

---

## Findings

### F1: Plaintext PII in Unauthenticated Vector Memory Store (HIGH)

All records in `watzis_longterm_memory` expose:
- `user_id` (MongoDB ObjectID)
- `session_id`
- `run_id`
- Timestamps
- Plaintext memory payload (Vietnamese and English)

Sample payloads from production records:

| Payload | Translation | Classification |
|---|---|---|
| `ví của tôi có 100000 VND` | "my wallet has 100,000 VND" | Financial data |
| `số định danh cá nhân của tôi là gì` | "what is my personal identification number?" | National ID query |
| `Thông tin trên căn cước công dân` | "information on citizen identification card" | Citizen ID disclosure |
| `Cần chuẩn bị các loại axit` | "need to prepare types of acid" | Chemistry context |
| `Lớp học hóa của tôi bắt đầu vào 7h tối` | "my chemistry class starts at 7pm" | Student PII (schedule) |
| `Đang tìm hiểu về quy định an toàn hóa chất ở trường` | "learning about chemical safety regulations at school" | Student context |
| `Đang khám phá Calmio và ứng dụng AI` | "exploring Calmio and AI application" | Product name attribution |
| `Tôi có kế hoạch đi xe bus` | "I have plans to take a bus" | Behavioral/location context |
| `I am interested in iconic Eiffel Tower photo opportunities` | (English user, travel intent) | User profiling |

User `68761612f3ce1c61575b67cb` is a Vietnamese student who has shared citizen identification card details and wallet balance data with the assistant. These memories persist across sessions in cleartext, accessible to any client that can reach port 6333.

### F2: No Authentication on Production Memory Endpoint (HIGH)

Qdrant's REST API at `http://149.28.77.155:6333` requires no credentials. Any unauthenticated client can:
- Enumerate all collections
- Scroll all stored memory vectors and payloads
- Execute semantic search across all users' memory
- Delete or overwrite any memory record
- Poison the memory store to influence future AI responses

The Mem0 framework writes memory as structured JSON payloads; the vector embeddings are co-stored with the plaintext source. Both layers are readable without auth.

### F3: Cross-User Memory Isolation Unverifiable (MEDIUM)

Multiple distinct `user_id` values confirmed in a single collection. No tenant isolation enforced at the database layer, isolation, if any, is enforced only at the application layer. Any application-layer bypass (IDOR, session confusion, prompt injection escalating to memory read) would expose all users' memories to any single authenticated app user.

### F4: Regulatory Exposure under Vietnam PDPA (MEDIUM)

Vietnam's Personal Data Protection Decree 13/2023 (Nghị định 13/2023/NĐ-CP) classifies national identification numbers and financial data as personal data subject to protection obligations. The exposure of citizen ID card content and VND wallet balance data in an unauthenticated database constitutes a personal data breach. The operator has not implemented basic technical security measures (authentication, encryption at rest) required under the decree.

---

## Remediation

Enable Qdrant's built-in API key authentication:

```yaml
# config.yaml
service:
  api_key: <strong-random-key>
```

Or via environment variable:

```bash
QDRANT__SERVICE__API_KEY=<strong-random-key>
```

Firewall port 6333 to localhost or the application subnet only. Do not expose the vector DB directly to the public internet regardless of auth state. Rotate all session and run IDs after remediation, the existing record set should be considered compromised.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending, operator contact not yet identified
- **Note:** Vietnamese PDPA breach notification obligations may apply. Operator identification via Calmio / Watzis product domains warranted before outreach.
