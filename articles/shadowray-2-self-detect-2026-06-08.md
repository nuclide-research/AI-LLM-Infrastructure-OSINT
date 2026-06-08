---
type: defender-advisory
date: 2026-06-08
audience: Ray operators + IR
companion: case-studies/commercial/ray-dashboard-shadowray-survey-2026-06-08.md
---

# Are You in the ShadowRay 2.0 Botnet? Five Things to Look For

_NuClide Research · 2026-06-08_

Anyscale Ray ships with no authentication on its Jobs API (CVE-2023-48022, "ShadowRay"). Oligo Security documented an active exploitation campaign in 2024 and a renewed one in November 2025 — ShadowRay 2.0 — where RondoDox, MooBot, KmsdBot integrate the unauth job submission to grow self-propagating cryptojacking and DDoS botnets across the roughly 200,000 internet-visible Ray servers.

This advisory gives any Ray operator five things to look for that distinguish an attacker-controlled Ray host from a clean one. Every signal is metadata-only. You do not need to read job payloads or run a scanner inside the cluster.

## How to check

From outside your own VPC, against your own Ray Dashboard:

```bash
curl -s "http://<your-ray-host>:<port>/api/jobs/" > jobs.json
```

If you get a JSON array back without any auth header, your Ray Dashboard is reachable on the public internet. That is the prerequisite. Now check the five signals.

### 1. Job count is exactly 10

```bash
jq 'length' jobs.json
```

Real workloads have any number of jobs — a fresh cluster has 0, a busy team has hundreds. **Length == 10 across the entire survey corpus we observed.** The cap is uniform because the attacker's submitter ships with a hard-coded job limit. If your Ray returns exactly 10 visible jobs and you did not queue 10 jobs, you are in the fleet.

### 2. Submission IDs match `YYYYMMDDxxxx_aa[N]`

```bash
jq -r '.[] | .submission_id' jobs.json | grep -E '^[0-9]{12}_aa[0-9]+$'
```

Real Ray submissions get Ray-generated UUIDs or the operator's own naming. The attacker's submitter prepends today's date as a 12-digit prefix and suffixes `_aa1`, `_aa2`, `_aa3`, etc. **If any submission ID matches that regex, the host has been used by the campaign.**

### 3. Status mix is balanced thirds

```bash
jq -r '.[] | .status' jobs.json | sort | uniq -c
```

Real workloads skew massively to SUCCEEDED (most jobs eventually finish). The attacker's load generator runs synthetic tasks that produce **roughly equal counts of RUNNING, FAILED, and SUCCEEDED**. If you see something close to a third-third-third split across non-trivial counts, the cluster is being driven by a synthetic worker.

### 4. Your Ray API answers on more than one port

```bash
nmap -p- --open <your-ray-host>
```

A real Ray cluster has one dashboard per cluster on port 8265 (default). The attacker fleet runs Ray dashboards on **dozens of ports per IP** — we observed up to 102 distinct ports on a single host. If your host is answering the Ray API on more than one port and you did not configure that, the box has been provisioned to fanout as relays.

### 5. Your submission ID prefix is shared with hosts you do not own

This one is harder to check yourself but the easiest at scale: if two hosts share the same `YYYYMMDDxxxx` prefix at the same minute, the same operator submitted to both. We observed prefix sharing across two to eight hosts at a time for the same minute — fleet-coordinated submission.

If you operate at multiple Ray instances and they share submission prefixes you did not orchestrate, your fleet has been merged into the attacker's.

## What to do if any signal fires

This is the standard incident-response sequence. Do not skip the forensic step.

1. **Do not restart the Ray service** before you have captured the running container's filesystem and process state. The attacker's persistence may be in-memory only (LD_PRELOAD rootkit class).
2. **Pull the Ray container's filesystem to a separate host** for forensic analysis. Look for unexpected Python packages, custom CUDA modules, and crypto-mining binaries.
3. **Audit your AWS / cloud-provider billing for the past 30 days.** Unexpected GPU instance spin-ups, outbound bandwidth spikes, or cross-region replication you did not configure are attacker-paid-by-you indicators.
4. **Network-isolate the cluster** before bringing it back up. Anyscale's official stance is that Ray must run in a tightly controlled environment; treat the public-internet exposure as the root cause, not the malicious activity.
5. **Notify your IR team or substrate provider's abuse contact.** If the cluster sits on AWS, an unauthenticated public Ray Dashboard violates AWS's Acceptable Use Policy whenever it has been used in the campaign.

## Background

- CVE-2023-48022 reference: https://nvd.nist.gov/vuln/detail/CVE-2023-48022
- Oligo Security ShadowRay (March 2024): https://www.oligo.security/blog/shadowray-attack-ai-workloads-actively-exploited-in-the-wild
- Oligo Security ShadowRay 2.0 (November 2025): https://www.oligo.security/blog/shadowray-2-0-attackers-turn-ai-against-itself-in-global-campaign-that-hijacks-ai-into-self-propagating-botnet
- Anyscale's official guidance: Ray must be deployed in a tightly controlled environment. The unauth Jobs API is by design.

## Restraint statement

This advisory is derived from a metadata-only population survey conducted by NuClide Research on 2026-06-08. We did not submit any jobs, did not read driver_info bodies, did not interact with worker nodes. The survey reads the Ray-defined `/api/jobs/` endpoint exactly as a Ray operator's own management console would. The five signals are observable to any operator running the same metadata check on their own infrastructure.

Full survey: `case-studies/commercial/ray-dashboard-shadowray-survey-2026-06-08.md`
