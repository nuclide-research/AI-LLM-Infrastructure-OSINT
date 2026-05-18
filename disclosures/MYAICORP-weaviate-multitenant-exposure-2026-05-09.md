# MyAi Corporation: Unauthenticated Multi-Tenant Weaviate Knowledge Base

**Discovered:** 2026-05-09  
**Hosts:** `188.245.173.135:8080` (`www.myaicorp.com`, Hetzner DE), `91.98.226.57:8080` (Hetzner DE)  
**Severity:** HIGH. Multi-tenant enterprise SaaS; named clients' vectorized knowledge bases publicly readable without authentication; 200–203 client-specific collections exposed  
**Status:** Not yet disclosed. No public contact surface found at time of survey

---

## Summary

MyAi Corporation operates a multi-tenant AI chatbot/RAG platform built on Weaviate. Two Hetzner-hosted instances (both `*.myaicorp.com` per TLS cert) expose their entire Weaviate schema, 200–203 named client knowledge-base collections, without authentication on port 8080. Any internet caller can enumerate all client names, read collection schema, and issue semantic search queries over any client's vectorized documents.

The client portfolio spans luxury retail (Dior, Chanel, YSL, Armani, Louboutin), industrial equipment (Wittmann, IKA, Yaskawa, Salicru), Spanish public transport infrastructure (Renfe, TMB, Metro Madrid, FGC), government entities (Generalitat de Catalunya, Qatar University, Riyadh Municipality), cybersecurity vendors (CrowdStrike, Kaspersky), and financial/payment operators (Astropay, Monri, Signifyd).

---

## Technical Detail

**Service:** Weaviate v1.28.4, anonymous access enabled (default)  
**Modules:** `text2vec-openai`, `backup-filesystem`  
**TLS cert:** `*.myaicorp.com` (Sectigo DV, Hetzner-hosted)  
**DNS:** `www.myaicorp.com` → `188.245.173.135`, `api.myaicorp.com` → `server05.myaicorp.com` → `188.245.173.135`

### Exposed endpoints (all unauthenticated)

```
GET  /v1/meta                          → version, module config
GET  /v1/schema                        → all class definitions (client portfolio enumeration)
GET  /v1/nodes                         → cluster health, object count, shard count
POST /v1/graphql                       → full semantic search over any class
POST /v1/{className}/objects           → object listing
GET  /v1/objects?class={name}&limit=N  → object retrieval
```

### Collection namespace (selection from 203 classes on 188.245.173.135)

| Sector | Named clients (class prefix) |
|---|---|
| Luxury / beauty | Dior, Chanel, YSL, Armani, CharolotteTilbury, TomFord, Louboutin, Lancome, Hermes, Byredo, PacoRabanne, Guerlain, Nars, Revlon |
| Industrial equipment | WittmannW40, WittmannR9, WittmannM7_M8, WittmannB8, WittmannTCU, IKA, Salicru, YaskawaCompare, VaccuBrand, Plasmac |
| Public transport | Renfe, TMB, MetroMadrid, Moventis, FGCXatLPS, FGCXatLMT, TurkishCargo |
| Government | Gencat012, QatarUniversity, RiyadhMunicipality, Roshn |
| Cybersecurity | Crowdstrike, Kaspersky, Orange |
| Finance / payments | Astropay, Monri, Signifyd |
| Pharma / health | Probiotical, DataseekersURIAGE |

### Reproduction

```bash
# Enumerate all client names (collection names = client identifiers)
curl http://188.245.173.135:8080/v1/schema | python3 -m json.tool | grep '"class"'

# Check second instance (same schema)
curl http://91.98.226.57:8080/v1/schema | python3 -m json.tool | grep '"class"'
```

### What we verified

- `GET /v1/meta`: version, modules confirmed
- `GET /v1/schema`: full class list on both instances (203 + 200 classes)
- `GET /v1/nodes`: cluster status, node health

### What we did NOT do

- Did not query `/v1/graphql` or issue any semantic search
- Did not read any object content
- Did not access `/v1/modules/text2vec-openai` config endpoint
- Did not test write or delete operations

---

## Impact

| Impact | Description |
|---|---|
| **Client enumeration** | Full client portfolio exposed via collection namespace |
| **Knowledge base read** | Any caller can semantic-search any client's vectorized documents |
| **Compute theft** | `text2vec-openai` module active — unauthenticated queries consume operator's OpenAI API quota |
| **Cross-tenant access** | No tenant isolation — any caller accesses any client's data by specifying the class name |
| **Data injection** | Weaviate's unauthenticated write API allows content injection into any client's knowledge base, corrupting chatbot responses |
| **Object deletion** | `DELETE /v1/objects/{uuid}` allows unauthenticated deletion of indexed documents |

---

## Remediation

1. **Immediate:** Set `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false` in Weaviate config; configure API key auth (`AUTHENTICATION_APIKEY_ENABLED=true`, `AUTHENTICATION_APIKEY_ALLOWED_KEYS`)
2. **Network boundary:** Firewall port 8080 to VPN/office IPs; put Weaviate behind a reverse proxy (Nginx/Caddy) that enforces auth at the edge
3. **Per-tenant isolation:** Implement multi-tenancy via Weaviate's native tenant-per-collection feature with per-tenant API keys, so cross-client data access is impossible even if the outer auth layer fails
4. **Audit:** Review Weaviate access logs for any prior unauthenticated access to client collections

---

## Disclosure Path

- **Primary:** myaicorp.com. No public security contact or contact form found (site returns nginx default page at time of survey). Check LinkedIn for MyAi Corporation contacts.
- **Fallback:** Hetzner abuse (`abuse@hetzner.com`) with IPs `188.245.173.135` and `91.98.226.57`
- **Secondary:** Individual client notification if MyAi Corporation does not respond within 14 days and data class warrants it (Renfe/TMB as transport infrastructure operators; Gencat as government entity)

---

## Discovery Context

Found during NuClide Research Weaviate exposure survey 2026-05-09. Host `188.245.173.135` matched `http.html:"weaviate" port:8080` in Shodan. TLS cert (`*.myaicorp.com`) identified operator. Both Hetzner instances share identical schema. Confirmed production/staging pair for the same platform.
