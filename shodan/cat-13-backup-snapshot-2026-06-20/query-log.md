# Cat-13 Backup+Snapshot — Shodan query log (2026-06-20)
# authed web UI in-page fetch, 0 API credits. hit = Total Results.

## Round 1 — NAIVE seed path-dorks (all 0: backup paths are not banner strings; Shodan-dark by path)
  0      | "qdrant" "/snapshots" port:6333
  0      | "weaviate" "/v1/backups" port:8080
  0      | "elasticsearch" "/_snapshot" port:9200
  0      | "chroma" "/persist" port:8000
  0      | "milvus" "MinIO" port:9000 "bucket"
  165    | "/var/lib/docker" "overlay2"   (broad/substrate, rejected)
  0      | "backup.tar" OR "dump.sql" port:80  (broad, rejected)

## Round 2 — platform-banner dorks (corrected)
  21569  | "Server: MinIO" port:9000
  974    | port:8000 "chroma"
  418    | port:8080 "weaviate"
  109    | port:9091 "milvus"
  31     | http.title:"Longhorn"
  15     | port:9200 "lucene_version"
  1      | "rest-server" port:8000

## Round 3 — variants for 0-result / dark-tier
  0      | port:6333 "version" "qdrant"   (Qdrant Shodan-dark -> Censys)
  0      | port:6333 "collections"
  0      | port:9200 "cluster_name" "cluster_uuid"  (too strict)
  1      | "rest-server" port:8000   (restic REST -> 62.171.111.9)
  0      | port:8085 "velero"   (Velero internal -> Censys)
  31     | http.title:"Longhorn"
  0      | port:8200 "Duplicati"
  0      | "kopia" port:51515   (-> Censys)

## Round 2 — object-store layer (2026-06-20, authed web UI)
| dork | total | note |
|---|---|---|
| `"<ListAllMyBucketsResult"` | 121 | anon S3 root listing (all vendors) — 114 unique harvested |
| `"<ListBucketResult"` | 23 | anon bucket key listing — 22 unique |
| `http.html:"lakeFS"` | 94 | lakeFS instances — 91 unique (init-state = claimable-admin) |
| `"Server: SeaweedFS"` | 2,240 | SeaweedFS filer/S3 — defer to AI-narrow/sample |
| `"Server: ScalityS3"` (zenko) | 4 | Zenko CloudServer |
| `http.html:"Ceph Object Gateway"` | 1 | Ceph RGW (header filter=0; html filter works) |
| `http.headers.server:"Ceph Object Gateway"` | 0 | web UI does NOT serve header filters → Censys |
| `"<ListAllMyBucketsResult" "mlflow"` (+models/checkpoints/...) | 0 | Shodan indexes only first banner chunk; AI-narrow at PROBE time not dork |
| `port:6333 "qdrant - vector search engine"` | 0 | health-title not Shodan-indexed; canonical `http.html:"qdrant"` stands |
