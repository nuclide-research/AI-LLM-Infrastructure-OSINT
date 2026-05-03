# tweet-optimize.com — 1.21M Facial Embeddings (OnlyFans + Second Dataset) Exposed Unauth on Milvus

_NuClide Research · 2026-05-03_

---

## Verification Status (as of 2026-05-03)

| Claim | Method | Result |
|---|---|---|
| Milvus REST + gRPC reachable without auth | `/healthz` + `/v2/vectordb/collections/list` (no header) | ✅ **Confirmed live** at probe time. `:9091/healthz` returns `OK`; `:19530/v2/vectordb/collections/list` returns `["psos","onlyfans"]` |
| Schema is a face-recognition pipeline | `/v2/vectordb/collections/describe` | ✅ **Confirmed**: 512-dim FloatVector (ArcFace family), IP metric, ObjectId-shaped string fields |
| Aggregate volume 1.21M face vectors | `/v2/vectordb/entities/query` count probe | ✅ **Confirmed**: `psos`=313,066, `onlyfans`=897,111 (re-counted at writeup time, unchanged) |
| Search primitive functions unauth | Loopback self-query: pull vector → submit same vector to `/entities/search` | ✅ **Confirmed**: distance 1.0 self-match, neighbors at IP=0.51-0.58 (real face-similarity matches) |
| Data model is N faces per source image | Loopback returned same `mongo_id` with different `image_id` | ✅ **Confirmed** — strong evidence against creator-uploads, consistent with scraped-image indexing |
| Operation has been running ~14 months | ObjectId timestamp prefix `67e16358` decoded | ✅ **Confirmed**: first writes ~2025-03-24, matches tweet-optimize.com domain registration 2025-03-03 + 3-week ramp |
| `tweet-optimize.com` is operator's real product, not lure | HTTPS fetch + WHOIS + cert + page content | ✅ **Confirmed**: SvelteKit Twitter analytics SaaS, Cloudflare-fronted, Danish (Copenhagen) registrant via privacy proxy, valid Google Trust Services TLS cert |
| Sibling MongoDB cluster on adjacent /29 | nmap version detect + pymongo `serverSelection` | ❌ **Refuted**: nmap reports 27017 as `filtered mongod` (not open) on all 10 IPs originally `/dev/tcp/`-flagged; pymongo handshake times out. Earlier "10 sibling MongoDBs" claim walked back |
| MongoDB is inaccessible from public internet | By elimination | ✅ Source-image MongoDB on localhost only; Milvus index is the operator's sole internet exposure |
| Worst-case framing: "doxing-as-a-service backend" | Interpretation, not a probe | ⚠️ **Stays as worst case**, not as confirmed operator intent. Multiple legitimate-operator readings remain consistent with the same empirical picture |

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
| Operator brand | `tweet-optimize.com` — confirmed real Twitter-analytics SaaS (SvelteKit SPA, Cloudflare-fronted, Google Trust Services TLS cert) |
| WHOIS | tweet-optimize.com registered **2025-03-03**, registrar Cloudflare, registrant **Copenhagen, DK** (REDACTED per privacy proxy) |
| Origin/edge | 65.108.107.240 is the **origin** server behind Cloudflare's edge |
| MongoDB | not on standard ports of this host; sibling-host hypothesis refuted (see F4) |
| Discovery date | 2026-05-03 |
| First-data timestamp | **~2025-03-24** (decoded from MongoDB ObjectId timestamp prefix `67e16358` in sampled `mongo_id` reference) — operation ~14 months old |

---

## Collections

| Collection | Count | Schema |
|---|---|---|
| `onlyfans` | 897,111 | `id` (Int64, auto), `mongo_id` (VarChar 25), `image_id` (VarChar 25), `embedding` (FloatVector dim=**512**), `bbox1-4` (Int32) |
| `psos` | 313,066 | identical schema |

**Schema verified via `/v2/vectordb/collections/describe`:**

```
embedding: FloatVector dim=512    → ArcFace / InsightFace `buffalo_l` family
index:     embedding_idx, IP metric → vectors are L2-normalized for cosine similarity
mongo_id:  VarChar(25)            → 24-char hex ObjectId fits, +1 buffer
image_id:  VarChar(25)            → also ObjectId
bbox1-4:   Int32 each             → pixel-space face bounding box (xmin, ymin, xmax, ymax)
```

The 512-dim FloatVector with IP metric is the InsightFace standard. ArcFace/InsightFace face embeddings are widely used, publicly downloadable, and produce L2-normalized vectors — so cross-model translation by an attacker is straightforward: any open-source InsightFace-based pipeline produces vectors directly compatible with this index.

**Structural finding (verified, see F1 evidence below):** Multiple Milvus records share the same `mongo_id` while having different `image_id`s. This means:
- 1 MongoDB document = 1 source image (likely with URL, account, ingestion metadata)
- N Milvus records per MongoDB doc = N faces detected in the image

This is a face indexer over scraped or aggregated source images (one row per detected face), not a creator-self-upload index. Creators uploading their own headshots would produce one face per image and a 1:1 `mongo_id`:`image_id` ratio — observed data shows N:1.

---

## Findings

### F0 — Verification Evidence (Empirical)

NuClide performed the following verification probes against the live Milvus instance to confirm the search primitive works as the schema implies:

**(a) Loopback self-query — psos collection.** Pulled one record's vector via `/v2/vectordb/entities/query` (id=456873519869865714, mongo_id=`67e163587aea7dd92a3e032d`), then submitted that exact vector back via `/v2/vectordb/entities/search` (limit=5):

```json
{
  "code": 0,
  "data": [
    {"distance": 1.0,        "id": 456873519869865714, "image_id": "67e163587aea7dd92a3e0325", "mongo_id": "67e163587aea7dd92a3e032d"},
    {"distance": 0.579362,   "id": 456873519869865716, "image_id": "67e163587aea7dd92a3e0328", "mongo_id": "67e163587aea7dd92a3e032d"},
    {"distance": 0.54010177, "id": 456873519873814009, "image_id": "67e165c7b766a44d904cdf8a", "mongo_id": "67e165c7b766a44d904cdf91"},
    {"distance": 0.52440464, "id": 456873519872035562, "image_id": "67e1659fb766a44d904c3b0c", "mongo_id": "67e1659fb766a44d904c3b13"},
    {"distance": 0.5109482,  "id": 456873519872035534, "image_id": "67e1659fb766a44d904c3b0b", "mongo_id": "67e1659fb766a44d904c3b13"}
  ]
}
```

What this proves:

1. **Distance 1.0 self-match** — the search primitive functions as documented; submit a vector, get the matching record back at perfect similarity.
2. **2nd result, distance 0.58, same `mongo_id`, different `image_id`** — there is *another face* in the same source image whose embedding is similar to the query face. This confirms the N-faces-per-image data model.
3. **3rd-5th results, distance ~0.5, different `mongo_id`s** — semantically similar faces from other source images. With 512-dim L2-normalized ArcFace vectors and IP metric, IP scores ≥ 0.4 are conventionally interpreted as "plausibly same person" — these results are real face-similarity matches, not noise.

**(b) Cross-collection search — psos vector queried against onlyfans.** Submitted the same psos-derived vector to `/v2/vectordb/entities/search` against `onlyfans` (limit=5):

```json
{
  "data": [
    {"distance": 0.34, "image_id": "68ceeda9...d017", "mongo_id": "67e18bd6...8ae6"},
    {"distance": 0.33, "image_id": "67ed39d1...3d78", "mongo_id": "67e17ea9...7a96"},
    {"distance": 0.31, "image_id": "69a61da1...2c86", "mongo_id": "67e19425...30d6"},
    ...
  ]
}
```

The cross-collection query **succeeded** — both `psos` and `onlyfans` use the same embedding space (same model, dimension, and metric), so a vector from one is queryable against the other. Distance scores are lower (0.30-0.34) than same-collection (0.51-0.58), which is expected when the queried face isn't actually present in the cross-collection but the index returns its closest matches by proximity. This empirically confirms an **identity-correlation primitive**: an unauthenticated attacker can submit any face vector and ask "is this person represented in either dataset?" — the structural capability is intact regardless of which dataset the face originated in.

**(c) Internal Milvus management endpoints respond unauth.** Probes against several control-plane endpoints all returned data without credentials:

| Endpoint | Response |
|---|---|
| `POST /v2/vectordb/databases/list` | `{"code":0,"data":["default"]}` |
| `POST /v2/vectordb/users/list` | `{"code":0,"data":["root"]}` — root user *exists* but isn't enforced |
| `POST /v2/vectordb/roles/list` | `{"code":0,"data":["admin","public"]}` |
| `POST /v2/vectordb/aliases/list` | `{"code":0,"data":[]}` |
| `POST /v2/vectordb/partitions/list` | `{"code":0,"data":["_default"]}` |
| `POST /v2/vectordb/indexes/list` | `{"code":0,"data":["embedding_idx"]}` |
| `POST /v2/vectordb/collections/get_load_state` | `{"code":0,"data":{"loadProgress":100,"loadState":"LoadStateLoaded"}}` |

Critical implication: the `users/list` and `roles/list` returning data unauth is *worse* than "auth fully off." The operator has provisioned a `root` user and the standard `admin`/`public` roles in the auth backend — but the data-plane endpoints are not gating against them. This is consistent with `authorizationEnabled: false` in `milvus.yaml` while `etcd` retains pre-existing user/role records, or with a misconfiguration where RBAC was attempted but never validated. The operator may believe the cluster is auth-protected because they "set up auth"; in reality the data endpoints accept anonymous queries.

The search primitive is empirically verified to work as described. An attacker submitting any face vector (locally computed via InsightFace) would receive ranked face matches from the index without authentication.

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

### F4 — Sibling MongoDB: Localhost Only (verified by elimination) (HIGH)

The `mongo_id` field references documents in a MongoDB collection. Verification probes:

- **Origin host (65.108.107.240):** MongoDB on standard ports (27017, 27018, 28017, 27019, 27020, 28018) — all closed per nmap and `/dev/tcp/` connect.
- **Adjacent /29 in 65.108.107.0/24 (.233-.238, .242, .244-.246):** initial `/dev/tcp/` probe returned "open" for all 10 IPs on port 27017 — but follow-up nmap version detection (`-sT -sV --version-intensity 5`) reports all 10 as `27017/tcp filtered mongod`. Filtered = something is dropping or RST-ing probes after the SYN. pymongo `serverSelection` against 4 sampled IPs all timed out with no MongoDB wire-protocol response. One IP (`65.108.107.244`) reverse-resolves to `gw01-hel1.netfactory.de` — a Hetzner-reseller infrastructure gateway, not a customer host.
- **Conclusion:** the sibling MongoDB is **not internet-reachable from any host probed**. It almost certainly runs on localhost of 65.108.107.240, accessible only to the Milvus application stack co-located on the same VPS. The source-image storage layer has correct network isolation; the Milvus index is the operator's only exposure point.

This is a verification-driven correction. An earlier draft of this case study claimed "10 sibling MongoDBs" based on the misleading `/dev/tcp/` results — that claim is **walked back**. Trust the nmap-with-version-detect result, not the bare-TCP-connect result.

This is a defensive win for the operator on the *image-payload* side — the actual face images and account metadata are protected by host-level network isolation. But it does not reduce the severity of the Milvus exposure: the embedding index alone is the doxing primitive; the source images are the secondary harm. A successful unauth face match (`/v2/vectordb/entities/search`) returns the `mongo_id` and `image_id` references — these are 24-char hex pseudo-identifiers that don't directly leak the source image, but their *existence* confirms the face is in the dataset.

ObjectId timestamp decode of sampled `mongo_id` values: first byte sequence `67e16358` = Unix time `1742846808` = **2025-03-24 21:26:48 UTC**. That matches the tweet-optimize.com domain registration (2025-03-03) plus 3 weeks for the ingestion pipeline to come online. The operation has been running ~14 months as of disclosure date.

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
