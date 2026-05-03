# tweet-optimize.com — 1.21M Facial Embeddings (OnlyFans + Second Dataset) Exposed Unauth on Milvus

_NuClide Research · 2026-05-03_

---

## Summary

A Milvus instance on a Hetzner VPS (Helsinki, FI) exposes two facial-image vector collections — `onlyfans` (897,111 embeddings) and `psos` (313,066 embeddings) — totaling **1,210,177 facial embeddings** with bounding-box coordinates and references to a sibling MongoDB image store. No authentication on the Milvus REST or gRPC endpoints. Port 80 redirects to `https://tweet-optimize.com/` — apparent operator brand.

**Worst-case interpretation: a doxing-as-a-service backend, fully exposed to the public internet.** Anyone with a target's photo can locally compute a face embedding, send it to the unauthenticated `/v2/vectordb/entities/search` endpoint, and retrieve nearest-neighbor matches across nearly a million OnlyFans face vectors plus a second 313K-record dataset (`psos`, unidentified). Cross-correlate `mongo_id` values out of the response and recover account identifiers, bounding boxes, and image references.

This is the worst-case reading. Multiple legitimate operator intents are also consistent with the same architecture (creator anti-piracy SaaS like Vaultsy/BranditScan/Rulta; DMCA takedown automation; content-moderation research) — and I have no evidence the operator's *intent* is malicious. But the unauth state is operator-intent-independent: regardless of why the index exists, anyone on the internet can query it as a face-matching primitive against OnlyFans creators, including the very creators the operator may have been hired to protect.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 65.108.107.240 |
| Hosting | Hetzner Online GmbH (Helsinki DC, Finland) |
| OS | Ubuntu 24.04 LTS (per OpenSSH 9.6p1 Ubuntu-3ubuntu13.16 banner) |
| Open ports | 22 (SSH), 80 (HTTP→nginx 1.27.4 with 301 to tweet-optimize.com), 9091 (Milvus REST proxy, returns OK on /healthz), 19530 (Milvus gRPC + unified REST) |
| Operator brand | `tweet-optimize.com` (per HTTP 301 redirect) |
| MongoDB | not on standard ports (27017/27018) — sibling on localhost or separate host |
| Discovery date | 2026-05-03 |

---

## Collections

| Collection | Count | Fields |
|---|---|---|
| `onlyfans` | 897,111 | `id, mongo_id, image_id, embedding, bbox1, bbox2, bbox3, bbox4` |
| `psos` | 313,066 | `id, mongo_id, image_id, embedding, bbox1, bbox2, bbox3, bbox4` |

The two collections share the same schema. The `bbox1-4` quartet is a face-detection bounding box (likely top-left x/y + bottom-right x/y in pixel coordinates). The `mongo_id` field is a 24-character ObjectId reference to a parallel MongoDB document — almost certainly containing the source image URL, account identifier, and ingestion metadata.

---

## Findings

### F1 — Unauthenticated Face-Matching Endpoint (CRITICAL)

The Milvus `/v2/vectordb/entities/query` endpoint returned `code: 0` (success) for the count probe with no auth header. The sibling `/v2/vectordb/entities/search` endpoint performs nearest-neighbor face-vector search using the same auth posture:

```json
POST /v2/vectordb/entities/search
{
  "dbName": "default",
  "collectionName": "onlyfans",
  "data": [<query vector>],
  "outputFields": ["mongo_id", "image_id", "bbox1", "bbox2", "bbox3", "bbox4"],
  "limit": 50
}
```

Any unauthenticated client can submit a face embedding (computed locally using a publicly available face-recognition model) and receive ranked nearest-neighbor matches.

**The risk is independent of operator intent.** The dataset exists; it is internet-reachable without credentials. Two attack workflows are enabled by the unauth state alone, regardless of why the operator built the index:

**Reverse face search:**
1. Attacker takes a target's face image (LinkedIn, Instagram, school photo)
2. Attacker computes a face embedding using `face_recognition`, `insightface`, or any pretrained model
3. Attacker submits the embedding to `/v2/vectordb/entities/search`
4. If the embedding model approximately matches the operator's embedder (most face-recognition models converge on similar feature spaces; Milvus's L2/IP/cosine similarity surfaces meaningful clusters even with imperfect embedder alignment), Milvus returns the closest matches
5. Attacker fetches the corresponding `mongo_id` to recover the source

The cross-model gap can be closed with one hour of work: embed a small public-image sample with the attacker's own model, train a linear projection from attacker-space to operator-space, then translate any query into operator-space.

**Inverted use against legitimate creator-protection workflows:** The most generous reading of the operator's intent is that they run an anti-piracy service for OnlyFans creators (Vaultsy/BranditScan/Rulta-style), where creators upload their own content to find leaks. *Even under this reading*, the unauth endpoint inverts the security model: the creators trusted the operator to use their face index to *find leaks*, but the unauth state lets an attacker use the same index to *find creators*. The exact privacy harm the creators were paying to prevent is the harm the unauth state enables.

### F2 — Aggregate Dataset Volume — Scope Without Inferring Provenance (HIGH)

897,111 OnlyFans-tagged face embeddings is a substantial dataset. At an average of 5-10 face crops per source post, this represents on the order of 100K-180K source posts. The provenance is not knowable from the data exposed:

- **Creator-uploaded** — anti-piracy SaaS where creators submit their own content for leak monitoring
- **Scraped from OnlyFans** — would be a ToS violation; possibly DMCA/CFAA exposure if any portion was behind paywall
- **Mix** — operator started one and grew into the other

The `psos` collection (313,066 embeddings) is unidentified. Reasonable hypotheses:

- A second platform's face dataset (Pornhub, Twitter/X NSFW, etc.) for cross-matching
- "Public-source" face data (LinkedIn-style headshots, social media) used for cross-correlation against the OnlyFans set
- An acronym specific to the operator's domain (PSOS = various sectors)

**The provenance question matters legally** (scraped vs. consented, DMCA vs. legitimate processing) but is **secondary** to the actual finding: the index, whatever its origin, is searchable without authentication.

### F3 — Operator Brand Misdirection: tweet-optimize.com (HIGH informational)

Port 80 returns:

```
HTTP/1.1 301 Moved Permanently
Server: nginx/1.27.4
Location: https://tweet-optimize.com/
```

`tweet-optimize.com` is presented as the operator's surface — but the actual workload (face matching against OnlyFans content) is unrelated to "tweet optimization." Possibilities:

1. **Legitimate diversification.** The operator runs both a Twitter/X content optimization SaaS and a creator-protection face-matching backend, and consolidated them onto one VPS for cost.
2. **Misdirection.** The Twitter brand is a cover for the actual face-matching service, which is sold separately or via affiliate networks.
3. **Domain-only landing page.** `tweet-optimize.com` might be a parked or low-content site used to look legitimate to abuse complaints.

WHOIS / surface investigation of `tweet-optimize.com` is the next pivot for operator attribution.

### F4 — Sibling MongoDB Implied But Not Located (HIGH)

The `mongo_id` field references documents in a MongoDB collection. MongoDB on standard ports (27017, 27018, 28017) is not open on this host. Implications:

1. **MongoDB on localhost** — only Milvus and the application backend can reach it. The risk is contained on this host but still a single privilege boundary breach away.
2. **MongoDB on a separate host** — the sibling host is the higher-value target. Each `mongo_id` is the URL/credential to fetch the source image from MongoDB, where the actual sensitive content (image URLs, account names, ingestion metadata) lives. If the sibling MongoDB is also unauth, this is a chain to massively higher-impact data.

The `mongo_id` ObjectId values themselves are not predictable, but a sample of 50 from a `/entities/query` call would reveal the timestamp range of MongoDB writes (ObjectIds embed creation time), telling an attacker how long the operation has been running and roughly how active it is.

### F5 — Root Cause: Default-Off Milvus RBAC (CRITICAL)

Same root cause as the cross-cutting Milvus survey: `authorizationEnabled: false` is the default, and this operator did not flip it. Detailed remediation in [milvus-cloud-survey-2026-05.md](milvus-cloud-survey-2026-05.md).

---

## Disclosure Path

This is the highest-impact individual finding in the cloud sweep so far — facial-recognition primitive over OnlyFans creator content, free and unauthenticated. Disclosure should be aggressive and parallel:

1. **Hetzner abuse@hetzner.com** — operator-agnostic disclosure to the hosting provider. Hetzner is responsive to AUP/abuse complaints; facial-recognition databases of OnlyFans creators arguably violate Hetzner's AUP regardless of how the data was obtained.
2. **OnlyFans (`security@onlyfans.com` / `report@onlyfans.com`)** — OnlyFans operates a takedown/abuse program for scraped creator content. They have the legal standing (and resources) to act against scraping operations.
3. **tweet-optimize.com operator** — via the WHOIS / contact-us / abuse@ on the brand domain. Frame as "your Milvus is publicly readable, anyone can run face matches against your dataset." Even an operator with malicious intent will likely close the auth gap once they realize the unauth state is *also* enabling competitors to read their dataset for free.
4. **EU regulator notification** — under GDPR Article 9 (biometric data is special-category), facial embeddings of EU-resident OnlyFans creators are subject to consent requirements. An operator processing biometric data without lawful basis is exposed regardless of the unauth state. The Finnish DPA (Tietosuojavaltuutettu) has jurisdiction since the data is hosted in Finland.

The Hetzner + OnlyFans disclosure pair is the highest-signal opener because both have established responsiveness.

---

## NuClide Pipeline Artifacts

| Stage | Notes |
|---|---|
| Discovery | Milvus cloud survey 2026-05 |
| Ledger entry | `nuclide.db` record `host.ip = 65.108.107.240`, severity CRITICAL, tags `FACIAL_RECOGNITION,ONLYFANS,IMAGE_MATCHING` |
| Operator brand | `tweet-optimize.com` (per HTTP 301) |
| Compliance score | 0/10 (AI.C1 unauth-baseline) |

---

## References

- Parent survey: [milvus-cloud-survey-2026-05.md](milvus-cloud-survey-2026-05.md)
- Milvus authentication: https://milvus.io/docs/authenticate.md
- Milvus REST search API: https://milvus.io/api-reference/restful/v2.4.x/Vector%20Operations/Search.md
- Cross-survey index: [index.md](index.md)
