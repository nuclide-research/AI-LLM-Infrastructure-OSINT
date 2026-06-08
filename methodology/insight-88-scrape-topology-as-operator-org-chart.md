# Insight #88 — Scrape Topology Disclosure = Operator Org Chart

_NuClide Research · 2026-06-08 · Origin: VictoriaMetrics population survey, 1,176 verified hosts._

---

## Statement

A monitoring system's scrape-target list is the operator's internal infrastructure org chart. It enumerates which services run, in which environment, on which subnet, named by which convention. For attackers and intelligence collectors, the **infrastructure-naming schema** is more actionable than the metric values themselves. An open `/api/v1/targets` is therefore not a leak of operational data; it is a leak of **operational structure**.

## Derivation

Across 884 unauth vmagent hosts, page-1 of `/api/v1/targets` exposed 1,578 distinct scrape-target endpoints:

- 1,039 (66%) are RFC1918 private-network IPs — internal hosts that no external observer should know exist
- 65 (4%) are public IPv4 addresses
- 474 (30%) are DNS hostnames carrying operator-specific naming

Sample disclosed names: `cadvisor-production01.menta.uz`, `arno-contabo-storage-01.infra-cloud.nebre.net`, `app-btc`, `app-merchant`, `app-rates`, `app1.node.cp.teye`, `courageous-rockhopperpenguin.ludiumlab.com`. Each name encodes:

- **Stack layer** (cadvisor = container monitoring → operator runs containers; alertmanager = Prometheus AlertManager → operator's alerting fabric is Prometheus-derived)
- **Environment label** (`production01`, `staging`, `europe-testing` → operator's deployment lifecycle)
- **Business function** (`app-btc`, `app-merchant`, `app-rates` → payments / crypto operator with merchant + rate-aggregation services)
- **Hosting provider** (`infra-cloud.nebre.net` containing `arno-contabo-storage-01` → operator runs Contabo VPS for storage)
- **Hostname-generation convention** (`courageous-rockhopperpenguin` / `darling-bat` → Heroku-style review-app naming; tells the attacker how many other hostnames probably exist and how they're shaped)

## Why this is the org chart, not metric data

A traditional metric leak (numerical values from `/api/v1/query`) tells the attacker the operator's CPU usage at 14:32 UTC. Useful, narrow, time-bound. The scrape-target list tells the attacker:

- What categories of service the operator runs (databases, queues, exporters, business-logic apps)
- How the operator organizes those services into teams and environments
- What naming convention the operator's platform team chose
- Which hosting providers and ASNs the operator depends on
- Which internal subnets the operator uses
- (Often) the relative scale of each service tier from the number of targets per scrapePool

Equivalent to leaving the team Slack workspace's `#channels` directory and the Ansible inventory file on the public internet.

## Action / discrimination

When surveying any monitoring / observability platform with unauth read on a list-of-things endpoint, **count the disclosed-target endpoints as the leakage metric**, alongside whatever raw record count the platform exposes. The list-of-things number is the operationally-useful intel; the record count is data-volume.

This applies beyond VictoriaMetrics: Prometheus `/api/v1/targets`, Datadog Agent `/info`, Telegraf `/inputs`, OpenTelemetry Collector configs, Grafana datasource configurations, Logstash pipelines. Any agent that monitors stuff has a target list, and the target list is the org chart.

## Restraint discipline

We did not query any of the leaked RFC1918 endpoints. We counted them. The count is the finding. Probing inward from the leaked target list would shift posture from research to lateral reconnaissance — outside the NuClide ethic.

## Cross-references

- Insight #76 (auth-permissive baseline): VictoriaMetrics joins the population where "operators leave the default" is the modal deployment choice.
- Insight #87 (canary persistence as monitoring proxy): same operator population that doesn't monitor its data plane also doesn't audit its monitoring infrastructure's exposure.
- The Chroma case (Cat-02): collection names are the attacker's pretext payload for RAG operators. Scrape-target names are the equivalent for ops engineers.

## Tooling

The detection takes a few lines: read `/api/v1/targets` (or platform equivalent), regex-extract host portions of `scrapeUrl`, classify as RFC1918 vs public vs hostname, count distinct values per host. Population-scale tally is a sum-by-state. Reusable for every monitoring agent in the surveyed substrate.
