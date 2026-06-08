# Risk & Ethics Review: glance v0.1.0

**Reviewer role:** DoD AI Risk & Ethics Specialist (DCWF AI Work Role 733)
**KSATs exercised:** T5854 (AI risk assessment in adversarial conditions), K7040 (AI risk frameworks), K7051 (AI ethics, governance, accountability)
**Artifact reviewed:** `~/glance/glance.py` (v0.1.0), `CATEGORIES` dictionary, sealed-mode contract
**Posture:** The classifier's correctness IS the ethics surface. False positives mis-route disclosure; false negatives leave genuinely sensitive corpora treated as benign. Names in the dictionary themselves are publishable artifacts and must be audited as such.

---

## 1. Category Dictionary Diversity Audit

The dictionary is overwhelmingly Anglophone, US/UK-coded, and tilted toward Western enterprise vocabulary. This is a population-bias defect: at NuClide's stated population scale (1,000+ host corpora, global), under-coverage outside the Anglosphere produces systematic false negatives that look like clean corpora. The corpora are not clean; the dictionary is blind.

**PII (high gap).** Covers English identifier words and US-specific instruments (`ssn`, `passport`). Misses: `documento_identidad` / `dni` / `nie` (ES, LATAM), `cpf` / `rg` (BR), `aadhaar` / `pan_no` (IN), `mykad` (MY), `nric` (SG), `cedula` (CO/VE/EC), `numero_carnet`, `personnummer` (SE/NO), `bsn` (NL), `tckn` (TR), `身份证` / `shenfenzheng` (CN), `nationalRegistrationNumber` (BE).

**PHI (high gap).** Anglophone clinical vocabulary only. Misses: `paciente` / `historia_clinica` (ES/PT), `dossier_medical` (FR), `klinik` / `krankenakte` (DE), `bolnitsa` / `больница` transliteration (RU), `hasta` (TR), `pasien` (ID), `prontuario` (BR), `nhs_no` (UK — present indirectly via `nhs` is absent), `kanja` (JA romaji). Also misses non-ICD coding systems: `read_codes` (UK), `mkb_10` (RU localized ICD), `gosti` (RU pharmacy codes).

**FINANCE (high gap).** Card/bank/crypto Western framing. Misses entire payment rails: `upi` / `vpa` / `bhim` (IN), `alipay` / `wechat_pay` / `unionpay` (CN), `mpesa` / `airtel_money` (KE/sub-Saharan), `paytm`, `pix` (BR), `sepa_xml` (EU), `ach_routing` (US absent), `iso20022`, `clabe` (MX), `interac` (CA).

**DEFENSE_GOV (high gap).** `.gov` and `.go.[a-z]{2}` cover Anglosphere + JP-style; misses `.gouv.fr`, `.gob.es`, `.gob.mx`, `.gv.at`, `.bund.de`, `.gc.ca`, `.govt.nz`, the entire CN `.gov.cn` (matched only because `.gov\b` is followed; `\.gov\.cn` parses fine — verify), `.gov.il`, `.gov.in`, `.go.id`, `.gov.br`. The `\.go\.[a-z]{2}` pattern catches `.go.jp/.go.kr/.go.th` only; `.gob.*` (Spanish-speaking countries) and `.gouv.*` (Francophone) are uncovered. Agency vocabulary is US-only: missing `mod` (UK), `bundeswehr`, `dgse`, `fsb`, `gru`, `pla`, `mss`, `mod_jp`, `idf`, `mossad`, `raw`, `isi`.

**CRITICAL_INFRA (medium gap).** Protocol coverage is decent (SCADA/Modbus/DNP3/BACnet/IEC-61850), but operator/utility naming is Western. Misses: `gosatomnadzor`, `rosenergo`, `gazprom_*` (RU), `state_grid` / `csg` (CN), `sgcc`, `chinapower`, `pgcil` / `nhpc` (IN), `eskom` (ZA), `petrobras_scada`, `pemex_*`, `aramco_*`. Also misses water-sector Spanish (`acueducto`, `saneamiento`) and Arabic transliteration.

**AI_WORKLOAD (low gap).** This category is the strongest, because the AI/ML ecosystem is largely English by convention. Minor misses: `baichuan`, `qwen`, `glm`, `moonshot`, `deepseek`, `yi_*`, `kimi`, `wenxin`, `tongyi` (CN model families), `paddlepaddle`, `mindspore` (CN frameworks), `bittensor` / `prime_intellect` (decentralized).

**GENERIC_INFRA (low gap).** Tooling is globally Anglophone; this is fine.

**Severity ranking:** PII = critical gap, PHI = critical gap, FINANCE = critical gap, DEFENSE_GOV = high gap, CRITICAL_INFRA = medium gap, AI_WORKLOAD = low gap, GENERIC_INFRA = acceptable.

**Operational impact.** A Latin-American hospital RAG corpus with `paciente_*` collections would presently classify as zero PHI hits. That is the textbook silent-failure mode flagged by Insight #68's verification doctrine: a confidently wrong number is worse than no number.

---

## 2. Triple-Use Risk of the Tool Itself

`glance` is openly described as a corpus characterizer that answers "how much sensitive data is in this corpus, of what kind, without reading it." That capability has three populations:

**Use 1 (defender).** An ops team aims `glance` at their own Chroma / VictoriaMetrics export to audit exposure before publishing dashboards. Beneficial; this is the canonical case.

**Use 2 (NuClide research).** Survey ingest characterizes a sealed corpus to make a category-level disclosure routing decision (PHI -> HHS OCR path, finance -> sector regulator) without violating the no-content-read discipline. Beneficial under the methodology's restraint ethic.

**Use 3 (attacker, the triple-use case).** An adversary who has already exfiltrated data points `glance` at the loot to triage which dump is most valuable. The tool acts as a stolen-data grader: a 50TB dump becomes a sorted hit list ("PHI: 41,000 hits, FINANCE: 12,000 hits, DEFENSE_GOV: 84 hits — sell the third one first"). This is materially worse than a generic grep: the named categories map directly onto market segments (dark-web buyers price PHI vs PII vs payment cards differently), so `glance` operates as a pricing oracle for stolen corpora. The category dictionary is the value; the binary is irrelevant.

**Why the triple-use is structurally hard to mitigate.** The tool's beneficial use cases require the exact same capability the harmful use exploits. There is no algorithmic difference between defender-self-audit and attacker-loot-triage; only the data's origin differs, and the tool has no way to verify origin. Any "authorization check" would be theater.

**Mitigations considered and their honest evaluation:**

- *(a) Add a license requiring authorized-use.* Unenforceable; the README already commits CC0. Not effective.
- *(b) Withhold the dictionary, ship binary only.* Defeats the patches-welcome model and the methodology's "dictionary is the product" stance. Not effective.
- *(c) Watermark outputs.* Trivially stripped. Not effective.
- *(d) Refuse to run on corpora over N hosts.* Defenders run at the same scale as attackers. Not effective.

**Recommended posture: accept publication risk with documented rationale.** The dictionary's substantive content (`patient`, `payment`, `iban`, `scada`) is general knowledge already encoded in dozens of DLP products (Microsoft Purview, Google DLP, Macie). `glance` adds organizational convenience, not novel capability. The marginal uplift to an attacker who already possesses an exfiltrated corpus is small relative to grep + a wordlist they could assemble in an hour. The marginal uplift to defenders and to NuClide research is large, because the integration into the sealed-mode workflow is the actual product. Publish with an explicit dual-use clause in the README and a logged-use audit in the JSON output so accidental misuse leaves a trace.

What does need mitigation is the *attacker convenience* layer — specifically the `--include-samples` flag (see §4) and the leakage of geographically distinctive TLDs (see §4 again).

---

## 3. Dictionary Itself as PII / PHI

Several patterns name specific operators rather than category-generic vocabulary. Publishing them in a CC0 binary effectively ships a *named targeting list* under the cover of a sensitivity classifier. The classifier still works without these — they should move to an external rules file loaded at runtime (e.g., `~/.config/glance/rules.d/defense-contractors.yaml`), not be compiled into the published binary.

**Specific patterns to relocate or remove:**

| Pattern source line | Pattern fragment | Concern |
|---|---|---|
| DEFENSE_GOV L75 | `lockheed\|raytheon\|northrop\|boeing_defense\|general_dynamics` | Named primes. Targeting list. |
| DEFENSE_GOV L76 | `anduril\|palantir\|saic\|leidos\|booz_allen\|caci\|mantech` | Named integrators + product companies. Targeting list. |
| AI_WORKLOAD L99 | `runpod\|coreweave\|lambdalabs\|paperspace\|modal` | Named GPU-cloud operators. Borderline; these are the *category* of cloud-GPU, so generic. Lower concern, but consider moving. |
| AI_WORKLOAD L100 | `runpodip\|user_id.*pod\|safe_runpod\|secure.*pod` | Looks like it was extracted from observed labels in a specific operator's corpus. Risk of revealing past survey targets. |
| FINANCE L70 | `app_(?:btc\|eth\|merchant\|rates\|wallet\|crypto\|trading)` | The `app_*` prefix appears specific to one observed app — fingerprint of a prior survey, not a general financial pattern. |
| FINANCE L71 | `sql_cache_.*_(?:head_office\|branch\|finance)` | Same — looks lifted from a specific bank's schema. Operator-attributing if anyone recognizes it. |
| PHI L63 | `doc_(?:hypertension\|diabetes\|cancer\|cardio\|neuro\|onco)` | Looks lifted from a specific medical-collection naming convention. Possible operator attribution. |

**Proposed remediation:** split CATEGORIES into a `CATEGORIES_GENERIC` (compiled in, ships in the binary, no operator names) and a `CATEGORIES_OPERATOR_DERIVED` (loaded from an optional external YAML, defaulting to empty, with a comment block explaining each entry's provenance). The binary stays publishable; the operator-derived rules stay private to NuClide's internal copy.

---

## 4. Sealed-Mode Bypass in Output

Two leakage channels survive even with `--include-samples=0`:

**Channel A: Top TLD suffixes (`structural_counts` -> `top_tld_suffixes`).** The output prints the most common TLDs without a frequency floor. If a 500-host corpus contains one host whose TLD is `.kp`, `.gov.kr`, `.mil.il`, or `.gov.cn`, that TLD lands in the top-10 list as `.kp 1`, exposing per-host attribution. The README promises "without echoing full hostnames" — TLD-level echo with N=1 is still echo of a uniquely identifying tail in low-cardinality jurisdictions.

**Quantification.** TLD distribution across the public internet is power-law: a corpus of N hosts will have ~30–60% in `.com`, ~5–15% in `.net/.org/.io`, and a long tail. A `.kp` with N=1 in a 500-host corpus is *more* identifying than a `.com` with N=300, because the rare TLD localizes one specific actor.

**Proposed fix:** apply a minimum-frequency floor of `max(5, ceil(0.01 * total))` to `top_tld_suffixes` in sealed mode. Hide everything below the floor under a `(other: N suffixes, suppressed)` bucket. Patch location: `structural_counts` in `glance.py` around line 271.

**Channel B: scrape-pool name suffix outputs.** `scrape_pool_names` is treated as a regular stream and passed through `classify_strings` plus `structural_counts`. If a corpus contains a single pool named `prod-classified-iran-air-defense-fab`, the structural and sensitivity counts won't echo it, but `--include-samples > 0` will. Worse, even without samples, the pool-name stream contributes hits to `sensitivity_categories` at single-string granularity — a single match in DEFENSE_GOV from a 200-pool corpus is itself a finding ("one of these pools is defense"). Combined with the TLD leak from Channel A, an analyst with both outputs can locate that pool.

**Proposed fix:** in sealed mode, suppress sensitivity-category reporting on streams where `count_total < 20` OR where any category's hit count is below a floor (suggest 3). Force the analyst to opt into low-N stream reporting via an explicit flag (`--low-n-streams`). Suffix histograms on scrape-pool names should follow the same floor as TLDs.

**Both fixes have to be defaulted-on.** Sealed mode should be unambiguously sealed; any leak path that requires the user to know about a config knob is a methodology failure waiting to happen.

---

## 5. Disclosure Ethics When `glance` Flags High-Risk Categories

The categorical count is *prior signal*, not proof. Insight #68 (Depth vs Breadth) and the verify-before-asserting rule both apply: `glance` produces candidates; verification produces findings. Disclosure decisions track from the verified layer, not the classifier output. With that gate in place, the per-category cascade:

**PHI hits.** Strongest duty. A non-zero PHI hit count on an unauthenticated exposed corpus triggers HHS OCR for US-attributed hosts and the relevant EU DPA(s) for European hosts. Path: (1) verify the corpus actually contains patient-linked data via *one* minimal sample pull confirming the schema is populated (not the dictionary's regex echo), (2) attribute the operator via cert + WHOIS, (3) notify the operator first with a 7-day acknowledgement window, (4) regulator notification if no operator response or if the operator's posture is non-cooperative. Aggregate-only reports are inappropriate here — PHI duty runs to the specific data subjects' regulator, which requires the operator identity.

**PII hits.** Operator-first disclosure with a 30-day standard window. Regulator escalation only on non-response or on jurisdictional aggravators (children's data -> COPPA/age-verification regulator; biometric -> Illinois BIPA / EU GDPR Art. 9; financial-identifier PII -> sector regulator). Aggregate-only public reports are acceptable after operator remediation.

**FINANCE hits.** Tier on the instrument. Credit-card / IBAN / SWIFT in an exposed cache -> PCI DSS Council notification path plus card-issuer fraud alert if cardholder data is verified. Crypto wallet hits are generally lower duty (public addresses are pseudonymous by design) unless paired with PII linking owners. UPI / Alipay / M-Pesa hits route to the respective national payment regulator (NPCI, PBoC, CBK).

**DEFENSE_GOV hits.** Stop and re-scope before any external mention. Defense / ITAR / CUI exposure is handled per the `feedback_defense_contractor_disclosure_handling` memory note: direct operator contact only, never public disclosure pre-remediation, never regulator-first. A categorical hit in this bucket triggers a manual operator-attribution pass before any further action; aggregate counts must not be published until remediation.

**CRITICAL_INFRA hits.** CISA disclosure path (ICSA advisory route, the same path Nick used for ICSA-25-140-11). Operator-first, with CISA notified in parallel within 7 days if the exposure is internet-facing and unauthenticated. Aggregate counts are publishable post-remediation as research artifact.

**AI_WORKLOAD hits.** Lower-duty category. Operator notification only; no regulator path unless the workload also surfaces PII / PHI / FINANCE (the cross-category overlap is the actual finding).

**GENERIC_INFRA hits.** No disclosure duty from this category alone.

**Stronger-than-routine trigger.** The categorical count crosses from routine-disclosure to elevated-duty when ANY of: (a) PHI count > 0 AND verified-populated, (b) DEFENSE_GOV count > 0, (c) CRITICAL_INFRA count > 0 with protocol-layer match (SCADA/Modbus/DNP3/IEC-61850, not just utility-word vocabulary), or (d) cross-category overlap (PHI ∩ FINANCE ∩ unauth = the EHR-billing-system pattern, near-automatic regulator-direct). Routine = operator-only, 30/60/90-day disclosure window. Elevated = parallel regulator notification within 7 days.

**Aggregate-only reporting.** Acceptable as research output once the per-operator disclosure cascade has concluded (operator notified, remediated or non-responsive past window). Never appropriate as the *first* communication to a regulator with named per-host data behind it.

---

## Recommended-Dictionary-Patches Table

| Category | Action | Proposed addition / removal | Rationale |
|---|---|---|---|
| PII | ADD | `documento_identidad`, `dni`, `nie`, `cpf`, `rg`, `aadhaar`, `pan_no`, `mykad`, `nric`, `cedula`, `numero_carnet`, `personnummer`, `bsn`, `tckn`, `nationalRegistrationNumber`, `shenfenzheng` | Non-English national-ID coverage |
| PHI | ADD | `paciente`, `historia_clinica`, `dossier_medical`, `klinik`, `krankenakte`, `bolnitsa`, `hasta`, `pasien`, `prontuario`, `kanja`, `nhs_no`, `read_codes`, `mkb_10` | Non-English clinical vocabulary + non-ICD coding |
| PHI | REMOVE -> external rules | `doc_(?:hypertension\|diabetes\|cancer\|cardio\|neuro\|onco)` | Pattern fingerprint of a specific past corpus; operator-derived |
| FINANCE | ADD | `upi`, `vpa`, `bhim`, `alipay`, `wechat_pay`, `unionpay`, `mpesa`, `airtel_money`, `paytm`, `pix`, `sepa_xml`, `clabe`, `interac`, `iso20022`, `ach_routing` | Non-Western payment rails |
| FINANCE | REMOVE -> external rules | `app_(?:btc\|eth\|merchant\|rates\|wallet\|crypto\|trading)`, `sql_cache_.*_(?:head_office\|branch\|finance)` | Operator-derived patterns; targeting risk |
| DEFENSE_GOV | ADD | `\.gouv\.[a-z]{2}\b`, `\.gob\.[a-z]{2}\b`, `\.bund\.de\b`, `\.gc\.ca\b`, `\.govt\.nz\b`, `\.gov\.cn\b`, `\.gov\.il\b`, `\.gov\.in\b`, `\.go\.id\b`, `\.gov\.br\b` | TLD coverage outside Anglosphere |
| DEFENSE_GOV | ADD | `mod_uk`, `bundeswehr`, `dgse`, `fsb`, `gru`, `pla`, `mss`, `idf`, `mossad`, `raw`, `isi` | Non-US agency vocabulary |
| DEFENSE_GOV | REMOVE -> external rules | Lines 75–76 (named primes + named integrators) | Operator targeting list; move to operator-derived YAML |
| CRITICAL_INFRA | ADD | `state_grid`, `sgcc`, `csg`, `gazprom`, `rosenergo`, `pgcil`, `eskom`, `petrobras`, `pemex`, `aramco`, `acueducto`, `saneamiento` | Non-Western utility operator vocabulary |
| AI_WORKLOAD | ADD | `qwen`, `baichuan`, `glm`, `deepseek`, `moonshot`, `kimi`, `yi_`, `wenxin`, `tongyi`, `paddlepaddle`, `mindspore`, `bittensor` | Non-Western model families + frameworks |
| AI_WORKLOAD | REMOVE -> external rules | `runpodip\|user_id.*pod\|safe_runpod\|secure.*pod` | Looks operator-derived; provenance unclear |
| (all) | STRUCTURAL | Split `CATEGORIES` into `CATEGORIES_GENERIC` (compiled-in) and `CATEGORIES_OPERATOR_DERIVED` (external YAML, default empty) | Keep operator-attributing patterns out of the published binary |
| (all) | STRUCTURAL | Add minimum-frequency floor `max(5, ceil(0.01 * total))` to TLD histogram and pool-name suffix histogram in sealed mode | Close §4 Channel A leak |
| (all) | STRUCTURAL | Suppress sensitivity-category output on streams with `count_total < 20` unless `--low-n-streams` is explicit | Close §4 Channel B leak |
| (all) | DOC | Add explicit dual-use / authorized-use clause to README; add `glance_run_log` audit field to JSON output (timestamp, corpus_dir, host, user) | §2 documented-risk mitigation |

---

**Reviewer sign-off.** The tool is sound in its restraint-discipline framing. The three priorities for v0.2.0 are: (1) de-Anglo the dictionary across PII / PHI / FINANCE / DEFENSE_GOV, (2) externalize the operator-named patterns currently baked into the binary, (3) close the two sealed-mode bypass channels with default-on frequency floors. The triple-use risk is real but acceptable to publish provided (2) and a dual-use clause ship together.
