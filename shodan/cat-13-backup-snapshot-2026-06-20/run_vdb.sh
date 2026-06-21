#!/bin/bash
cd ~/AI-LLM-Infrastructure-OSINT/shodan/cat-13-backup-snapshot-2026-06-20
for plat in qdrant weaviate chroma elastic clickhouse; do
  echo "===== $plat ($(wc -l < evidence/live-$plat.txt) hosts) $(date +%H:%M:%S) ====="
  python3 vectordb_probe.py $plat evidence/live-$plat.txt vdb/vdb-$plat.json 2>&1
done
echo "ALL VDB PROBES DONE $(date +%H:%M:%S)"
touch vdb/DONE
