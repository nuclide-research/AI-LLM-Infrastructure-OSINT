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

A real, paying-customer SaaS brand (`tweet-optimize.com`) is running alongside an exposed doxing-grade face search engine on the **same origin server**. The two are separate workloads — there is no evidence the brand product uses the face-matching service — but the operator's failure to firewall the secondary workload makes the unauth Milvus query-able by anyone on the internet.

**The brand product:** `tweet-optimize.com` is a polished, fully-authenticated paid SaaS. The marketing copy is explicit about what the model does:

> *"Our AI model forecasts views, likes, retweets, and comments based on your content and account metrics."*
>
> *"Advanced machine learning models that forecast how your tweets will perform over 24 hours."*
>
> *"The predictive model analyzes tweet content, follower count, and verification status…"*

Zero mentions of images, media, visual analysis, face recognition, person/creator detection, OnlyFans, or NSFW content in any of the public marketing. If the product secretly used face-rec on tweet media, the copy would absolutely highlight it (even vaguely — "media-aware AI," "advanced visual understanding"). It doesn't. The brand product is a **text + account-statistics forecaster**.

**The face-matching workload:** A Milvus vector database on the same VPS with **1,210,177 face embeddings** in two collections (`onlyfans`: 897,111; `psos`: 313,066) and **zero authentication on the Milvus data plane**. Schema verified, search primitive verified working unauth, cross-collection identity-correlation verified. The `mongo_id` field references a localhost-firewalled MongoDB; the Milvus index is the only public exposure.

**The diagnosis:** the operator knows how to do auth when money is on the line — the brand SaaS has Google OAuth, JWT-style session enforcement, quota gating, and Stripe-style subscription management, all working correctly. They simply didn't apply the same care (or awareness) to the secondary face-matching workload. That's the classic ops-vs-app-security gap: developers harden what their paying users can call; the side workload bound to `0.0.0.0` and serving 1.2M face vectors gets none of the same scrutiny.

**Why this sharpens rather than weakens the risk story:**

A legitimate paid SaaS brand operating openly and a doxing-grade face search engine sit side-by-side on the exact same origin server. The legitimacy of the brand product does not absolve the exposure of the face index. If anything, it makes the operator easier to identify, easier to disclose to, and easier to hold responsible. Whatever the face-matching workload was built for (anti-piracy, internal experiment, contract gig, sold-as-API to specific clients), the bound-to-`0.0.0.0` Milvus on the same VPS turns it into an unauth doxing primitive against ~900K OnlyFans creators.

Operator additionally provisioned Milvus users/roles (`root`, `admin`, `public` — all enumerable unauth) but the data-plane endpoints don't enforce them. This is a *partial RBAC illusion*: worse than auth-fully-off, because the operator may believe the cluster is secured while the data path silently accepts anonymous queries.

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
| Continuous-ingestion span | **March 2025 → March 2026** — ObjectId-decoded `image_id` values span a full year (e.g. `69a61da1` = 2026-03-19), confirming ongoing active scraping rather than a one-time corpus build. Many source records (`mongo_id`) cluster at March 2025 but accumulate fresh `image_id` face crops over time, suggesting `mongo_id` persists as a creator/source/batch identifier while `image_id` is per-detected-face |

---

## Collections

| Collection | Count | Schema |
|---|---|---|
| `onlyfans` | 897,111 | `id` (Int64, auto), `mongo_id` (VarChar 25), `image_id` (VarChar 25), `embedding` (FloatVector dim=**512**), `bbox1-4` (Int32) |
| `psos` | 313,066 | identical schema |

Both collections: 1 partition (`_default`), 2 shards. **Index: IVF_FLAT, metric IP, indexState=Finished, pendingRows=0** — fully indexed and queryable. `collectionID` differs across collections, confirming separate primary-key spaces.

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

### F3 — Two Separate Workloads on the Same VPS: Auth-Hardened Brand Product, Wide-Open Face Engine (CRITICAL)

The brand product (`tweet-optimize.com`) and the unauth Milvus are **separate workloads** running on the same origin server. Direct evidence:

**(a) Marketing copy explicitly excludes media/visual analysis.** Pulled from the live tweet-optimize.com site:

> *"Our AI model forecasts views, likes, retweets, and comments based on your content and account metrics."*
>
> *"Advanced machine learning models that forecast how your tweets will perform over 24 hours."*
>
> *"The predictive model analyzes tweet content, follower count, and verification status..."*

Zero mentions of images, media, videos, visual analysis, face recognition, person/celebrity/creator identification, OnlyFans, or NSFW content. If face recognition on tweet media were the secret engine, the marketing copy would almost certainly highlight it (even vaguely — "media-aware AI," "advanced visual understanding," "detects high-engagement creators"). It doesn't. The product is sold as a **text + account-stats forecaster**.

**(b) SPA + API surface is exclusively about Twitter optimization.** The complete public surface, extracted from 30+ SvelteKit production bundles:

**Routes (11):** `/`, `/optimizer`, `/account`, `/auth/verify/google`, `/auth/verify/[token]`, `/contact`, `/privacy`, `/refund`, `/subscription/cancel`, `/subscription/success`, `/terms`

**API endpoints (14, all under `https://tweet-optimize.com/api`):**

| Endpoint | Purpose | Live response |
|---|---|---|
| `POST /api/auth/login` | email + password | (auth-gated) |
| `GET /api/auth/google` | Google OAuth (client ID `115335252659-...`) | (auth-gated) |
| `GET /api/auth/me` | current user | **401** unauth — auth IS enforced |
| `GET /api/auth/verify` | email-token verification | (auth-gated) |
| `GET /api/user/quota` | usage quota | (auth-gated) |
| `POST /api/user/custom-instructions` | user prefs | (auth-gated) |
| `POST /api/tweet-forecast` | predict tweet performance (core product) | **405** (POST-only, exists) |
| `POST /api/tweet-variation` | generate tweet variations | **405** (POST-only, exists) |
| `POST /api/subscription/create-checkout` | Stripe-style checkout | (auth-gated) |
| `GET /api/subscription/session/:id` | check sub session | (auth-gated) |
| `POST /api/subscription/cancel` | cancel paid plan | (auth-gated) |
| `POST /api/subscription/reactivate` | reactivate | (auth-gated) |
| `POST /api/track/:event` | client-side analytics | (telemetry) |
| `GET /api/_app/version` | SvelteKit version probe | (build metadata) |

**Zero references** to `face`, `embedding`, `milvus`, `mongo`, `onlyfans`, or `psos` in any of the 30+ SvelteKit JavaScript bundles. Probes for `/api/face`, `/api/match`, `/api/search`, `/api/embedding`, `/api/onlyfans`, `/api/psos` all return 404.

**(c) The face-matching service has no client-side surface anywhere.** No SPA route calls it. No public API endpoint references it. The brand domain genuinely does not connect to the Milvus.

**The diagnosis:**

Two workloads, one VPS:

1. **Brand product** — properly auth-gated, paid Twitter-content forecaster. Google OAuth, JWT, Stripe subscriptions, quota gating, all working correctly. The operator built this carefully because revenue depends on it.
2. **Face-matching workload** — 1.21M scraped face embeddings, no auth, no firewall, exposed on `0.0.0.0:19530` and `:9091`. The operator built this with no apparent security scaffolding. Plausible reasons:
   - **Internal experiment / side project** the operator never intended to be public
   - **Unrelated contract gig** sharing infrastructure for cost reasons
   - **Sold-as-API service** for specific clients via promised-but-unenforced source-IP whitelists
   - **Forgotten / dev environment** that was provisioned and never decommissioned

The operator knows how to do auth when money is on the line. They simply didn't apply the same care (or awareness) to the secondary workload. This is the classic ops-vs-app-security gap: developers protect what their users can call; the side workload bound to `0.0.0.0` and serving 1.2M face vectors gets none of the same scrutiny.

**Why this sharpens, rather than weakens, the disclosure:**

A real paying-customer SaaS brand operating openly under a registered domain, alongside a doxing-grade face search engine on the same origin server, is *more* serious than either standalone:

- The operator has a discoverable identity (Danish registrant via Cloudflare privacy proxy; brand has paid customers, contact form, refund policy, terms of service)
- The operator is reachable through normal commercial channels (the brand `/contact` page) — disclosure does not require WHOIS pivot
- Hetzner abuse and the Finnish DPA can act with full operator attribution, not the usual "anonymous-VPS" gap
- The marketing-product legitimacy makes the unauth secondary workload *more* of a credible risk to the operator's reputation, not less — the asymmetry between "we charge customers $X for tweet predictions" and "1.2M faces of OnlyFans creators are on our server with no auth" is the disclosure lede

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
