# Nalu Services -- Unauth RWD on AI Chatbot Knowledge Base (Weaviate)

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** HIGH
**Status:** CONFIRMED -- unauth read (write + delete highly probable; not exercised)

---

## Target

| Field | Value |
|-------|-------|
| IP | 149.28.54.81 |
| Domain | ai-support.naluservices.com |
| Port | 8080 |
| Service | Weaviate 1.28.4 |
| Hosting | Vultr |
| Auth | NONE |

---

## Operator Attribution

**Nalu Services** -- US-based IT services firm operating at naluservices.com.

| Signal | Value |
|--------|-------|
| Contact phone | 1-888-533-8070 |
| Contact email | info@naluservices.com, mail@naluservices.com |
| Services | IT consulting, website development, SEO/digital marketing, e-learning, e-commerce |
| AI product | ai-support.naluservices.com (customer-facing AI support chatbot) |
| Secondary product | "Nalu Endorse" -- business endorsement/listing service (cards, flyers, endorsement links, claimable listings) |

Evidence: two named Weaviate classes (NalumomentsAI, Naluendorse) directly reference Nalu brand names. Domain ai-support.naluservices.com resolves to this IP.

---

## Data

**10 classes, ~767 total objects.**

| Class | Props | Content |
|-------|-------|---------|
| NalumomentsAI | source, text, url, blobType, title | Scraped naluservices.com pages powering the AI chatbot |
| Naluendorse | source, text | Nalu Endorse FAQ (from "FAQ Endorse.docx.pdf") |
| XTCGS | fileName, text | Unknown source document(s) |
| FLJEC | fileName, text | Unknown source document(s) |
| ZDUXL | source, blobType, title, url, text, loc_lines_from, loc_lines_to | Web-scraped content with line-range location metadata |
| AEDII | title, url, text | Web content |
| IJRBB | title, url, text | Web content |
| JXQAQ | title, url, text | Web content |
| FPRRG | title, url, text | Web content |
| XUSIE | fileName, text | Document source(s) |

**NalumomentsAI sample:** naluservices.com service pages, accessibility widget JS, contact info, Facebook Pixel code (fb_pxl_code), third-party tracking scripts -- embedded analytics credentials possible if API keys are inlined in scraped JS.

**Naluendorse sample:** Product FAQ covering endorsement link creation, business card generation, subscription upgrades, and business listing claiming. Full product documentation exposed.

**Obfuscation note:** Eight of ten class names are randomized 5-char strings. Name randomization provides zero access control -- all classes are fully readable via unauthenticated GraphQL.

---

## Access Matrix

| Operation | Result | HTTP |
|-----------|--------|------|
| GET /v1/meta | 200 + version info | 200 |
| GET /v1/schema | 200 + all 10 class schemas | 200 |
| POST /v1/graphql (GetNalumomentsAI) | 200 + records | 200 |
| POST /v1/graphql (GetNaluendorse) | 200 + records | 200 |
| POST /v1/graphql (GetZDUXL, etc.) | 200 + records | 200 |
| POST /v1/objects | Not exercised (write access highly probable) | -- |
| DELETE /v1/objects/{uuid} | Not exercised | -- |

Canary UUID: not injected (restraint posture; access not exercised past read).

---

## PoC

**Read -- enumerate schema:**
```bash
curl -s http://149.28.54.81:8080/v1/schema | jq '.classes[].class'
```

**Read -- pull NalumomentsAI knowledge base:**
```bash
curl -s -X POST http://149.28.54.81:8080/v1/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{Get{NalumomentsAI(limit:10){text url source}}}"}' \
  | jq '.data.Get.NalumomentsAI[]'
```

**Read -- pull Naluendorse FAQ:**
```bash
curl -s -X POST http://149.28.54.81:8080/v1/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{Get{Naluendorse(limit:10){text source}}}"}' \
  | jq '.data.Get.Naluendorse[]'
```

**Write -- inject poisoned chatbot record (not exercised; canary pattern):**
```bash
# Not executed. Structural proof: no auth layer present at POST /v1/objects
# curl -s -X POST http://149.28.54.81:8080/v1/objects \
#   -H 'Content-Type: application/json' \
#   -d '{"class":"NalumomentsAI","properties":{"text":"CANARY","source":"weavscan","url":"http://canary.invalid"}}'
```

**Delete (not exercised):**
```bash
# Not executed.
# curl -s -X DELETE http://149.28.54.81:8080/v1/objects/NalumomentsAI/{uuid}
```

---

## Impact

### Chatbot Knowledge Base Exfiltration
All content powering ai-support.naluservices.com is exposed. Any actor can pull the full indexed corpus -- service descriptions, product documentation, internal FAQ content -- without authentication. The eight obfuscated class names suggest the operator attempted to obscure the structure; the names do not restrict access.

### Naluendorse Product IP
Full FAQ for the Nalu Endorse product is indexed and readable. Competitor extraction of product documentation and feature roadmap language is trivial.

### Analytics Credential Risk
NalumomentsAI records include scraped JS from naluservices.com containing Facebook Pixel code and third-party tracking scripts. If any tracking scripts inline API keys or pixel IDs, those credentials are accessible via the exposed corpus.

### Chatbot Poisoning
No write authentication means an actor can inject false records into NalumomentsAI. Poisoned records surface as AI chatbot responses to Nalu's customers -- misinformation, phishing links, or social engineering content delivered via the operator's own support interface.

### Obfuscated Class Content Unknown
Eight classes with randomized names have not been fully scrolled. ZDUXL includes loc_lines_from / loc_lines_to fields that suggest it may index source code or structured documents with line-level granularity. Full content scope is not established.

---

## Pivot Avenues

1. **ai-support.naluservices.com** -- the chatbot frontend; test for prompt injection via the chat UI using content derived from the exposed KB.
2. **Obfuscated classes full scroll** -- GET all objects in XTCGS / FLJEC / ZDUXL / XUSIE to establish content class; ZDUXL loc_lines fields suggest source-code or structured-doc indexing.
3. **ZDUXL loc_lines_from / loc_lines_to** -- if these reference Nalu internal code, the indexed content is source code, not just web pages.
4. **Scraped JS in NalumomentsAI** -- grep records for api_key, pixel_id, fb_pxl_code, gtm, or _token patterns to surface embedded credentials.
5. **naluservices.com client portal** -- check for CRM, ticketing, or project management surface exposed on the same Vultr allocation.
6. **Adjacent Vultr IPs** -- 149.28.54.x range; check for admin panels or additional Nalu infrastructure on neighboring hosts.

---

## Tool Reference

**weavscan** -- https://github.com/nuclide-research/weavscan

Unauthenticated Weaviate enumeration: schema walk, class object extraction, GraphQL query execution, RWD surface confirmation.
