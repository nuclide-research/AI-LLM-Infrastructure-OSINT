# 7. RAG Stacks & Self-Hosted AI Apps

_New in v2 · Section verified: April 2026_

Self-hosted RAG stacks accumulate enterprise document sets as part of normal use. An exposed instance is a document store, the content is the value, the model is the pivot.

| Shodan Query | Notes |
|---|---|
| `"h2oGPT" port:7860` | Self-hosted RAG, auth optional |
| `"Verba" port:8000` | Weaviate-backed RAG UI |
| `"Danswer" OR "Onyx" port:3000` | Enterprise search over connected sources |
| `"Quivr" port:5050` | Personal/team second-brain RAG |
| `"Letta" OR "MemGPT" port:8283` | Stateful agent with persistent memory |
| `"Khoj" port:42110` | Personal AI with email/calendar/notes ingestion |
| `"RAGFlow" port:80 OR port:8080` | Deep-document RAG engine |
| `"FastGPT" port:3000 "fastgpt"` | |
| `"LibreChat" port:3080` | Multi-provider chat UI, often unauth |
| `"Open WebUI" "signup" port:3000` | First-user-becomes-admin pattern |

**The signup-becomes-admin pattern** (Open WebUI, LibreChat, some Danswer deploys) means the first visitor to an exposed instance is promoted to admin of every subsequent user's conversations. Frequently unnoticed because the operator set a password on their own account and assumed the instance was protected.
