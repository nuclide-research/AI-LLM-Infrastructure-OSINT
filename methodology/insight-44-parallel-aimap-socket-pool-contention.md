---
type: methodology
insight_number: 44
title: "Parallel aimap passes cannibalize each other's throughput via client-side socket pool contention; default to sequential or staged execution with the largest corpus running alone first."
---

# Insight #44. Parallel aimap passes cannibalize throughput

_Source: LLM orchestration category-01 re-run, 2026-05-19. Six concurrent 30-thread aimap binaries against ~3,500 distinct (host, port) combinations produced zero JSON output after 36+ minutes elapsed. The same workload run sequentially completed in 1m9s per pass on the smallest corpus._

## The rule

Running multiple aimap processes in parallel against large corpora degrades total throughput by roughly 3× compared to sequential execution, and can cause complete hangs (zero output after 36+ minutes). The bottleneck is client-side socket pool exhaustion: N concurrent aimap binaries each opening 30 threads = N × 30 simultaneous outbound connections, saturating the available local socket pool.

The correct execution model for multi-corpus survey sessions:

1. Run the largest corpus alone first (no competing processes)
2. Batch the smaller corpora together at the end (each is small enough that their combined socket load stays within pool limits)
3. Never run more than 2-3 concurrent aimap processes against large corpora regardless of available CPU

## Empirical basis (LLM orchestration re-run, 2026-05-19)

| Configuration | Corpora | Wall time | JSON output |
|---|---|---|---|
| 6 concurrent 30-thread binaries | ollama-side-channel, n8n (~3,500 total hosts) | 36+ min | **ZERO** (all hung) |
| Sequential single binary | Smallest corpus (sub-sample) | **1m9s** | Full JSON ✓ |
| Sequential single binary | n8n corpus | ~4-6 min | Full JSON ✓ |

Five of six parallel passes were killed after 36 minutes with no output. The sequential equivalent of the same work completed without issue.

Secondary observation from the same session: the `[!] no FP candidates for X:Y (port not in any DefaultPorts list)` log message appeared 1,126 times in the n8n corpus alone. These are coverage losses (hosts behind reverse-proxies on non-default ports) that are INDEPENDENT of the socket contention issue. See Insight #42.

## Procedural rules this insight generates

1. **One large corpus at a time.** Any corpus over ~500 distinct (host, port) pairs is "large." Run it alone, sequentially, before launching any other aimap process.

2. **Batch small corpora at the end.** Corpora under ~200 hosts can be run 2-3 at a time. Monitor with `ps aux | grep aimap` and ensure the previous batch exits cleanly before starting the next.

3. **Hung aimap = socket pool symptom.** If a 30-thread aimap run produces no output after 10+ minutes on a corpus that should complete in under 5, assume socket pool exhaustion. Kill, reduce concurrency, and restart. Do NOT wait it out.

4. **JSON output absence ≠ scan failure.** A hung-and-killed aimap run leaves no partial output. If the OSINT pipeline expects JSON for downstream steps (VisorLog ingest, VisorScuba scoring), re-run before proceeding. Absent output is not null-result; it is incomplete-run.

5. **Session planning rule.** When scheduling multiple aimap passes in a survey session, estimate total host × port load first. If combined load exceeds ~1,500 (host, port) pairs, plan sequential single-corpus passes with explicit completion checks between each.

## Relationship to prior insights

- **Insight #42 (aimap DefaultPorts coverage trade)**: companion tooling insight from the same session. Insight #42 is about per-host coverage loss due to port-profile restriction; this insight is about throughput collapse under parallel load. Both are operational discipline issues, not platform fingerprint issues.
- **Insight #14 (yield vs port-class alignment)**: the methodological reason to run exhaustive passes: port-class alignment is only as good as the scan coverage. Socket pool contention silently degrades coverage.

## See also

- `case-studies/commercial/llm-orchestration-rerun-2026-05-19.md` §10 (Stage 7, aimap row: "4 passes still in flight, 2 completed")
- `methodology/insight-42-litellm-model-impersonation-fraud.md`: companion aimap tooling insight (DefaultPorts coverage trade)
