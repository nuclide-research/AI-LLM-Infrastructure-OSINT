---
to: abuse@hetzner.com
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 65.109.36.121
institution: Hetzner DE — CORRECTION to prior disclosure; operator is WellCalf ML (livestock / veterinary AI, NOT pediatric medical)
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** abuse@hetzner.com
**Cc:** abuse@nuclide-research.com
**Subject:** CORRECTION — operator at 65.109.36.121 is WellCalf ML (livestock / veterinary AI), NOT pediatric medical / HIPAA-class. Metabase setup-token finding stands.

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** Correction to prior disclosure on `65.109.36.121` (sent earlier today)
**IP:** 65.109.36.121 (Hetzner Helsinki)
**Severity:** CRITICAL (Metabase setup-token finding) — same as prior; data-class framing corrected

---

I sent an unsolicited disclosure earlier today framing this customer as a "pediatric medical ML operator" with HIPAA-relevant data. **That framing was wrong.** Deeper enumeration of the MLflow experiment metadata reveals the operator is **WellCalf ML — a LIVESTOCK / VETERINARY AI startup** (cattle, calf, and goat behavioral health classifiers from sensor data). No human-patient data is involved.

This message corrects the prior disclosure. The technical findings stand; the data-class framing is the only thing that changes.

## What the operator actually does

The MLflow experiment metadata at `http://65.109.36.121:5000/api/2.0/mlflow/experiments/search` shows:

- **Source path:** `/home/avudai/avudai/code/wellcalf_ml/wellcalf_ml/models/machine_learning/model_train.py`
- **Classification targets:** `standing_vs_lying` (cattle posture detection from accelerometer data), `sick_vs_hlt` (sick-vs-healthy), feeding pattern detection, ear monitoring, rectal-temperature classification
- **User-tagged farm IDs:** `Farm_1025`, `Farm_1041`, `Olway_Adult`, `Olway` (these are real farm-customer identifiers in the WellCalf product)
- **Animal categories** in experiment names: `calf`, `cow`, `goat`, `adult`, `behaviour`, `feeding`, `milk`, `lying`, `standing`
- **Decoded prefix `beh_ped`:** behavioral classifier for young calves (pediatric in the veterinary sense, NOT human pediatric medicine)
- **Decoded prefix `sic_tmt`** (72 experiments — the dominant category): sick-treatment / sick-vs-healthy treatment-prediction models

Sample-counts on the most-recent experiment (2026-04-28): 3,114,417 "sick" sensor-readings + 814,072 "healthy" — consistent with multi-second sensor data over many cows over many days. Not a per-patient medical-record corpus.

WellCalf ML appears to be a livestock-monitoring IoT product — neck-collar sensors on calves and adult cattle, behavioral patterns ingested for early disease detection. The operator domain `wellcalf.com` is registered (NameCheap) but the public site was not enumerated in this disclosure.

## What the original disclosure got right (still applies — please action)

- **Metabase v0.55.12** at `http://65.109.36.121:3000/api/session/properties` returns `setup-token: "8f504ffb-d62d-4fa3-a03f-053cf7740a32"` UNCLAIMED. Anyone calling `POST /api/setup` with that token claims the Metabase admin slot. **Severity: CRITICAL — pre-auth admin takeover.**
- **MLflow 2.22.1** unauth on port 5000 with 224 experiments visible — confirms full operator-IP exfil at scale (4 years of WellCalf's veterinary-AI development).
- **17 database drivers** configured server-side in Metabase (Databricks, Druid, PostgreSQL, Spark SQL, MongoDB, etc) — once admin is claimed, attacker has SQL access to whichever databases the operator has actually wired up.

## What the original disclosure got wrong

- **Data class framing:** "pediatric medical ML" / "HIPAA-relevant" / "patient-identifiable content" — none of these apply. The data is veterinary sensor data on cattle / calves / goats. HIPAA scope does not include animal data; FDA / USDA frameworks may apply for veterinary-AI products but BAA / OCR notification is not relevant.
- **Severity escalation rationale:** the upgrade from "HIGH" (existing ledger MLflow finding) to "CRITICAL" was based on the Metabase pre-auth admin takeover path — that escalation rationale stands. The "HIPAA-class" framing was an additional incorrect basis.

## Recommended action (unchanged from prior disclosure)

1. Notify customer to claim the Metabase setup-token immediately (race window remains open).
2. Restrict MLflow + Metabase to admin-only network access.
3. Audit Metabase database connections to ensure read-only scoping.

The technical reproduction commands in the prior disclosure are unchanged; please refer to that message for the curl-based verification steps.

## Methodology note

The misattribution traces back to a token-level keyword match — both NuClide's original 2026-05-04 cloud survey and my disclosure today read `beh_ped` as "behavioral pediatric (human)" when the source path `/home/avudai/avudai/code/wellcalf_ml/` makes the veterinary context unambiguous. The error was caught in deeper enumeration (pulling actual experiment runs with their full param + tag set) which surfaced the `Farm_1025` / `Olway_Adult` / `goat` / `calf` / `cow` taxonomy.

Lesson for future disclosures: always pull at least one full run record (with `mlflow.source.name` + custom user tags) before publishing a data-class framing. Token-pattern matching on experiment names is unreliable.

I apologize for the misframing in the prior message. The Metabase setup-token finding remains CRITICAL and the customer notification path is unchanged.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
