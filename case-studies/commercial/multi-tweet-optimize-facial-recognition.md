# tweet-optimize.com — 1.21M Facial Embeddings (OnlyFans + Second Dataset) Exposed Unauth on Milvus

_NuClide Research · 2026-05-03_

---

## Summary

A Milvus instance on a Hetzner VPS (Helsinki, FI) exposes two facial-image vector collections — `onlyfans` (897,111 embeddings) and `psos` (313,066 embeddings) — totaling **1,210,177 facial embeddings** with bounding-box coordinates and references to a sibling MongoDB image store. No authentication on the Milvus REST or gRPC endpoints. Port 80 redirects to `https://tweet-optimize.com/` — operator brand identified.

The architecture (`embedding` + `bbox1-4` + `mongo_id` + `image_id` schema) is a standard face-matching pipeline. Combined with the unauthenticated `/v2/vectordb/entities/query` endpoint, any unauthenticated client can submit a face vector and retrieve nearest-neighbor matches across the dataset — i.e., this is a **reverse-image-search service against OnlyFans content, exposed without authentication**. Whether the operator's intended use is creator-protection (legitimate anti-piracy) or third-party identity-matching (doxing-class service), the unauth posture means anyone on the internet can use the matching capability for free.

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

### F1 — Unauthenticated Face-Matching Service (CRITICAL)

The Milvus `/v2/vectordb/entities/query` endpoint returned `code: 0` (success) for the count probe with no auth header. The same endpoint family includes `/v2/vectordb/entities/search`, which performs nearest-neighbor search:

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

Any unauthenticated client can submit a face embedding (computed locally using a publicly available face-recognition model) and receive ranked nearest-neighbor matches from the 897K-record OnlyFans dataset and the 313K-record `psos` dataset.

**Risk:** This is a **functioning doxing primitive**. Workflow:
1. Attacker takes a target's face image (LinkedIn, Instagram, school photo)
2. Attacker computes a face embedding using `face_recognition`, `insightface`, or any pretrained model
3. Attacker submits the embedding to `/v2/vectordb/entities/search`
4. If the embedding model approximately matches what tweet-optimize.com used (most face-recognition models share ResNet/ArcFace-style outputs and produce comparable vectors), Milvus returns the closest matches
5. Attacker fetches the corresponding `mongo_id` to recover the OnlyFans account / image source

The "approximate model match" caveat is real but limited — face embedding models converge on similar feature spaces, and Milvus's L2/IP/cosine similarity will still surface meaningful clusters even with imperfect embedder alignment. An attacker willing to invest one hour can re-embed a small sample of public OnlyFans content with their own model, train a linear projection between their model and the operator's embedder, and then translate any face image into the operator's embedding space.

### F2 — Aggregate Dataset Volume Indicates Production Scraping Operation (CRITICAL)

897,111 OnlyFans-tagged face embeddings is a substantial dataset. At an average of 5-10 face crops per source post, this represents on the order of 100K-180K source posts. OnlyFans terms of service prohibit scraping; the dataset is therefore either:

- **Scraped without OnlyFans authorization** — straight ToS violation, possibly DMCA / CFAA exposure if any portion was behind paywall
- **Submitted by paying creators for anti-piracy monitoring** — a creator-uploads-their-own-content model used by services like Vaultsy or BranditScan
- **Mix of both** — operator originally legit, scope crept

The `psos` collection (313,066 embeddings) is unidentified. Possible interpretations:
- A second platform's scraped face data (Pornhub, Twitter/X NSFW, etc.)
- "Public-source" face data for cross-matching (LinkedIn-style headshots, social media)
- An acronym for something specific to the operator (PSOS = Personnel/Public Safety/etc. — investigation warranted)

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
