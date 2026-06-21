# Cat-13 Backup + Snapshot — Wardrobe + syllabus stance

- Outfit `ai-infra-hunt` (13 atoms) — exercising T0028 (authorized pentest of exposed backup/snapshot endpoints),
  S0001/S0051 (vuln-scan + pentest tooling = scanner/aimap), T0247 (T&E verification of unauth reads),
  T0188 (remediation guidance), K0118 (evidence preservation — snapshot manifests as artifacts, not downloads),
  K0107 (cross-jurisdiction operator-attribution posture).
- Syllabus context: PoisonedRAG (USENIX '25), Was My Data Used for Training? Membership Inference in Open-Source
  LLMs (NDSS), SoK: Neural Network Extraction (USENIX '24) — informed the names-only restraint: a backup/snapshot
  collapses membership-inference and model-stealing to a trivial download, and the restore endpoint is the exact
  write-primitive PoisonedRAG weaponizes.

RESTRAINT: read snapshot/backup listings and manifests only. Never download snapshot contents (exfil).
Never POST a restore (write primitive). Names ARE the finding.

DCWF KSAT: 672 (AI T&E) + 733 (AI Risk/Ethics) standard pair; NICE 541 (T0028/T0188/K0342/S0001/S0051/T0247/K0107/K0118).
