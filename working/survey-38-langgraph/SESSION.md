# Survey 38 — LangGraph Server · Working Session

**Date:** 2026-05-25
**Status:** Active — 10/10 priority hosts fully mapped, 3 case studies published

---

## Published

| File | Host(s) | Status |
|---|---|---|
| langgraph-deployment-gap-survey-2026-05-25.md | All 16 hosts | LIVE (merged long-form) |
| langgraph-financial-agent-1-15-66-80-2026-05-25.md | 1.15.66.80 | LIVE (case study) |
| collector-scraper-api-langgraph-pii-2026-05-25.md | 51.15.237.90 + 51.158.97.152 | LIVE (case study) |

---

## Fully Mapped Hosts (case study candidates)

| Host | App | Key Finding | Notes File |
|---|---|---|---|
| 20.193.252.230 | Stock.ai (EMOR AI) — Azure Pune | Partial-auth failure; Arihant Capital 62 PDFs open; Weaviate full open; PG TCP open | notes-stock-analyzer-20.193.252.230.md |
| 157.180.21.126 +2 | Assistent Tècnic Intel·ligent (ATI) — Hetzner Helsinki | Vite dev server exposes full TS source; 121 user conversations; 377 knowledge vectors; all agent endpoints open | notes-docu-companion-cluster.md |
| 46.224.86.76 | Airbnb Tenant Agent — Hetzner Nuremberg | CORS wildcard + no auth; WhatsApp webhook; booking thread state open | notes-cors-46.224.86.76.md |
| 137.184.239.176 | Mezbar AI (Arabic content) — DO Santa Clara | 6-agent LangGraph; LLMjacking surface; OpenAI key in use | notes-mezbar-ai-137.184.239.176.md |
| 72.56.96.229 | modengy_v3 — Timeweb Netherlands | 21,589 Qdrant vectors; n8n enforced, LangGraph/Qdrant open | notes-modengy-72.56.96.229.md |
| 138.68.228.98 +1 | Vantage Coach (pharma CRM) — DO Santa Clara | Healthcare client DB via unauth chat; voice endpoints open; Spanish-language | notes-vantage-coach-cluster.md |
| 51.83.237.63 | SharePoint Assistant v2.0 | M365 tenant ID 5b72381b; SharePoint-connected agent open | notes-sharepoint-51.83.237.63.md |
| 43.143.225.104 | AI Weather / aiweather.top | openId in unauth POST; CN Tencent | notes-aiweather-43.143.225.104.md |
| 82.156.182.216 | wuji Sleep Doctor — Tencent Beijing | Sleep health data by WeChat openid; 9,244 log entries open; running as root | notes-wuji-sleep-82.156.182.216.md |
| 138.219.43.172 | Embedding stack (SA timezone) | Ollama embedding-only (multilingual); MinIO; no generative LLM visible | notes-embedding-138.219.43.172.md |

---

## 1.15.66.80 Extended Findings (case study published)

- PersonalCreditReportWorkflow: RAG → identity desensitization node → extract → analyze
- LoanProductExtractionWorkflow: 16 structured fields
- ConsultantWorkflow: ReAct (Perceive → Think → Act → Observe → Respond)
- OCR + image recognition capabilities confirmed
- RAGFlow proxy built into LangGraph server
- Identity desensitization node: raw PII in Redis before strip

---

## Case Studies Queued (not yet written)

1. **Stock.ai / EMOR AI** (20.193.252.230) — partial-auth failure pattern + financial data + third-party PDF exposure
2. **Docu Companion / ATI** (3-node) — Vite dev server in production, 211-tenant platform, all agent endpoints open
3. **Airbnb Tenant Agent** (46.224.86.76) — CORS wildcard + WhatsApp webhook + booking data
4. **Vantage Coach** — pharma/healthcare CRM with voice endpoints open
5. **wuji Sleep Doctor** — Chinese health data by WeChat openid, full request logs exposed

---

## Next Actions

- [ ] Write case study: Stock.ai / EMOR AI (partial-auth failure + Arihant Capital)
- [ ] Write case study: Docu Companion / ATI (Vite dev server + multi-tenant)
- [ ] Write case study: Airbnb Tenant Agent (CORS + WhatsApp + booking)
- [ ] Operator attribution for: modengy (what is it?), Vantage Coach, Docu Companion, Airbnb
- [ ] PostgreSQL probe on 20.193.252.230 — Nick to run: `! PGPASSWORD=postgres psql -h 20.193.252.230 -p 5432 -U postgres -c "\l" --connect-timeout=8`
