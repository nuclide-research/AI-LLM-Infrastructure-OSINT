# 13. Backup / Snapshot Exposure

_Section verified: April 2026_

| Shodan Query | Notes |
|---|---|
| `"qdrant" "/snapshots" port:6333` | Downloadable .snapshot files, full vector DB |
| `"milvus" "MinIO" port:9000 "bucket"` | Raw vectors in object storage |
| `"chroma" "/persist" port:8000` | Persistent directory exposure |
| `"weaviate" "/v1/backups" port:8080` | |
| `"elasticsearch" "/_snapshot" port:9200` | |
| `"/var/lib/docker" "overlay2"` | Container layer paths leaking |
| `"backup.tar" OR "dump.sql" port:80` | HTTP-served backup files |
