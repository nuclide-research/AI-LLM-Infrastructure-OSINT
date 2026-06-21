# Cat-13 Backup + Snapshot: vector-DB data-at-rest survey

**Date:** 2026-06-20
**Category:** Cat-13 Backup + Snapshot (AI/LLM data-at-rest exposure)
**Posture:** read-only. Names and counts are the finding. No object, vector, snapshot, or row content was downloaded. No setup, restore, or POST was issued.

## Summary

We surveyed the AI/LLM data-at-rest surface: the backup and snapshot endpoints that hang off self-hosted vector databases and data-versioning layers (Qdrant `/snapshots`, Weaviate `/v1/backups`, Elasticsearch `/_snapshot`, Chroma persistence, lakeFS setup-state). The thesis under test: self-hosted vector DBs still default to no auth, and their snapshot endpoints inherit that open posture, so the data-at-rest is reachable without ever touching the data plane.

The thesis held. Out of 329 probed vector-DB hosts, 260 answered unauthenticated. The clean, reproduced, attributed finding surface after false-positive removal: 56 logical Weaviate operators with readable schemas, 3 Qdrant (one exposing downloadable full-collection snapshots), 11 organic Chroma knowledge bases, 2 ClickHouse, and 32 confirmed lakeFS of which 2 are claimable-admin. The anonymous-S3 layer (136 hosts, 80-plus anonymous root listings) was a clean negative: zero held AI-scope data by name or manifest.

The load-bearing result is what we removed. An 81-host "Milvus/2.3.4" population is a deception fleet, not real Milvus. Verifying that, rather than counting it, is the difference between a survey and a scan.

## Wardrobe + syllabus stance

- Outfit `ai-infra-hunt` (13 atoms). The survey exercised T0028 (pentest surface mapping over the harvested population), K0342/S0001/S0051 (vuln-tooling judgment: built focused deadline-correct readers when aimap deadlocked), T0247 (test and evaluation: the two-read reproduce gate and the Milvus metrics-body discriminator), and K0118 (evidence preservation: names and listings captured, contents never pulled).
- Syllabus context: PoisonedRAG (USENIX '25) and the RAG-extraction dual-path literature anchored the restraint posture. The read primitive on an unauth vector DB sits one URL from the write primitive (scanner-injected `rce-cve-test` collections proved it on the Chroma layer). We read schema and collection names, never `/v1/objects` or a snapshot body, because the literature shows the sample-the-records step is the moment a survey becomes an intrusion.

## Methodology

```
Harvest (Shodan web-UI fetch + objectstore dorks) .... ~590 candidates
  -> scanner (0c) active banner liveness ............. 321 live, 7 catch-all stripped
  -> bucketnames.py  anon-S3 name/manifest read ...... 136 hosts, 0 AI-scope (clean neg)
  -> vectordb_probe.py  grouped-by-port enum ......... 329 hosts, names+counts only
  -> milvus_verify.py  refute the uniform cohort ..... 81 excluded (deception)
  -> lakefs_state.py  read init-state, never POST .... 32 confirmed, 2 claimable
  -> deep_verify.py  reprobe + cert-CN/PTR attribute . 18/18 reproduce, 14 attributed
```

aimap is the standard deep-enumerator. It deadlocked twice on this host set: 576 then 289 sockets held in ESTABLISHED, worker goroutines blocked, no JSON written. Root cause is that its 6-second timeout is connect-only with no per-read deadline, so a tarpit host that accepts a connection and never replies holds a worker forever. We pivoted to focused readers that enforce a per-recv `settimeout` deadline plus a response byte cap, so a tarpit costs one timeout and a bounded buffer, never a hang. They complete the same enumeration in about 60 seconds. Tool humility, documented.

## Discovery: the snapshot is the exfil primitive

The Cat-13 thesis made concrete on one host. Qdrant at `202.66.151.79` (reverse DNS `r79.igt.com.hk`, cert CN `api.b123.be`, a Hong Kong multi-tenant chat SaaS) answered `/collections` unauthenticated: 12 collections, 64,346 vector points, tenant collections named `webetter_chat_tenant_1` through `webetter_chat_tenant_281`. The `/collections/Image/snapshots` and `/collections/Video/snapshots` listings were readable and contained named backup files:

```
full-snapshot-2026-02-27-20-22-49.snapshot
Image-6633880155041475-2026-04-20-00-27-50.snapshot
Video-6633880155041475-2026-04-20-01-07-25.snapshot      (+ 9 more)
```

A snapshot file is a complete, restorable copy of the collection. On an unauthenticated Qdrant the download endpoint `/collections/{c}/snapshots/{name}` is one GET away, and it returns the entire collection, points and payloads, in one request, bypassing any per-query rate limit. We read the listing. We did not download a snapshot. The listing is the finding: it proves the exfil primitive exists without exercising it.

## The load-bearing verification: an 81-host Milvus mirage

The harvest returned 82 hosts bannering `Server: Milvus/2.3.4` on the metrics port 9091. Two tells made us distrust it: zero version spread (a real population of self-hosted Milvus shows many versions), and a perfectly uniform `{"status":"ok"}` healthz body. We built a discriminator on the principle that a host can spoof a header but cannot fake a coherent metrics body.

```
            /healthz            /metrics
real Milvus  200 ok    +    200 with dozens of milvus_* metric families
this fleet   200 ok    +    200 with ZERO milvus_* families   (81 of 81)
```

Every host answered `/metrics` with HTTP 200, so the endpoint exists and responds, but not one emitted a single `milvus_*` metric family. The server header and the healthz response are templated spoofs. This is a deception fleet poisoning the `product:Milvus` and `port:9091` dorks, the same class as the scanner-poisoning fleets we logged earlier this month. Had we counted instead of verified, this survey would report 81 phantom Milvus exposures. We report zero.

The same discipline stripped the Chroma layer. Of 104 unauthenticated Chroma hosts, 77 carried collections injected by third-party scanners: `probe` (38 hosts), `rce-cve-test` (5), `cve202645829_test_probe` (3). Those names are not operator data. They are evidence that someone else is mass-testing Chroma CVE-2026-45829, and incidentally proof that these hosts are unauthenticated-writable. We excluded them from the data inventory and kept the 11 organic knowledge bases (`procurement_docs`, `clinic_knowledge_base`, `avon_artifacts_user_*`, `doctrine_knowledge_base`, the 167-tenant `space_*` UDT deployment).

## Attribution

Reverse DNS and TLS certificate subject CNs attributed 14 of 18 deep-verified hosts to named operators without any active credential use:

| host | platform | operator tell | data inventory (names) |
|------|----------|---------------|------------------------|
| 20.228.169.116 | Weaviate | `*.drivestream.com` | Oracle HCM: `HCMTablesApr26Json`, `OracleStudentKnowledge_v3` |
| 202.66.151.79 | Qdrant | `r79.igt.com.hk` / `api.b123.be` | multi-tenant chat, 12 readable snapshots |
| 162.223.90.155 | Qdrant | `admin.yeksa.ai` | `bot_NN_user_NN` multi-tenant |
| 137.116.75.72 | Chroma | `*.udtonline.com` | 167 `space_<uuid>` tenants |
| 38.77.155.142 | Weaviate | `dev.avatarchatbots.ai` | chatbot KBs |
| 40.71.82.6 | Chroma | `platform-demo.certainti.ai` | `ai_knowledge_base` |
| 178.156.209.29 | Weaviate | Hetzner | golf-industry research (`USGAResearch`, `FootJoyResearch`) |

The legitimacy discriminator that cleared these as organic is the inverse of the Milvus tell: version spread. The Weaviate population ranged 1.28.4 to 1.36.8, each host on its own version, each schema host-unique. Three hosts (`132.243.117.114`, `88.218.123.199`, `89.150.34.22`) shared byte-identical `KB_<cuid2>` class names on identical v1.30.0; since a CUID2 is globally unique, three hosts cannot organically share one, so we deduped them to a single cloned-cluster operator.

## ai-llm-redteam-operator: the adversary path we did not walk

We ran the red-team scenario generator against the finding platforms and produced three read-only packets: `attack_path flowise_to_weaviate_pii_dump`, `platform Weaviate`, and `category leaky_data_stores`. The packets are the value of stopping where we stopped. The Weaviate-PII packet's mapping strategy, step 4, reads:

> GET /v1/objects?limit=5 to sample records and confirm PII data class.

That is the step we did not take. The packet describes what an adversary does next: extract the host from a Flowise flow config, hit `/v1/schema` unauthenticated, then sample objects to confirm the PII class and estimate scale. We confirmed the open surface and read the schema names. We did not sample an object. The gap between our last action and the packet's next action is the restraint ethic in one diff.

## Impact

The exposure is the full content of RAG corpora and their backups, reachable unauthenticated. Concretely: an Oracle HCM consultancy's HR and student tables as embeddings, a chemical-industry knowledge base, procurement documents, a clinic knowledge base, and 281 tenants of a chat product, each with vector payloads that reconstruct to the source text. On the Qdrant host the snapshot listing means an adversary downloads the entire collection in one request rather than scraping it point by point. On the two claimable lakeFS hosts (`52.24.205.248`, `20.31.76.105`) the first POST to the setup endpoint mints an admin and the credentials for the backing object store, which is the whole data lake, not one collection.

## Remediation

- Vector DBs: enable the built-in API-key or auth module and bind the snapshot/backup endpoints behind it. Qdrant `service.api_key`, Weaviate `AUTHENTICATION_APIKEY_ENABLED`, Chroma auth provider. Do not rely on the data port being "internal"; the metrics and REST ports are what Shodan indexes.
- Snapshot endpoints: if snapshots must be enabled, put them behind network policy, not just application auth, because a snapshot bypasses query-level controls.
- lakeFS: never expose an uninitialized instance. Initialize behind the firewall and front the API with auth before it reaches the internet.
- Operators relying on a banner for safety: a `Milvus/2.3.4` header is trivially spoofable and is being spoofed at fleet scale; do not treat a product banner as an inventory signal.

## References

- PoisonedRAG, USENIX Security 2025: the read-to-write proximity that grounds our names-only restraint.
- CVE-2026-45829 (Chroma): the vuln the scanner fleet is mass-testing on the contaminated hosts.
- Prior NuClide scanner-poisoning fleet write-ups (Insight #107 / #108 family): the deception pattern the Milvus cohort matches.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Wardrobe outfit: `ai-infra-hunt`.

- **672 (AI Test & Evaluation Specialist):** T5919, K7044, S7067, T5904 / T5858, K7004
- **733 (AI Risk & Ethics Specialist):** T5893 / T5882, K7040, T5868
- **NICE 541:** T0028, T0188, K0342, S0001, S0051, T0247, K0107, K0118

<!-- ksat-tag:auto-generated:end -->

---

Toolchain provenance: scanner (0c liveness), bucketnames.py / vectordb_probe.py / milvus_verify.py / lakefs_state.py / deep_verify.py (focused deadline-correct readers, built this survey after aimap deadlocked), ai_llm_redteam_operator (read-only scenario packets). Wardrobe outfit: ai-infra-hunt (T0028 / K0342 / S0001 / S0051 / T0247 / K0118). Syllabus context: PoisonedRAG (USENIX '25), RAG-extraction dual-path, informed the names-only restraint on `/v1/schema`, `/collections`, and `/snapshots` responses.
