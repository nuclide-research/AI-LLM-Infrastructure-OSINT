# LLM09:2025 — Misinformation

**OWASP rank 2025:** #9 (renamed and expanded from LLM09:2023 Overreliance)
**OWASP rank 2023:** LLM09 #9

The 2025 rename shifts focus from "user trusts the model too much" to "the model produces false content that propagates downstream." The scope now includes:

- Hallucination exploitation (attacker designs prompts to induce attacker-favorable hallucinations)
- Disinformation campaigns at scale (LLMs as content factories for false content)
- Brand reputation damage (model emits false statements about a specific entity)
- Compliance violations from false content (legal, medical, financial misinformation)

## Description

The model emits content that is **incorrect**, **fabricated**, or **misleading** in a way that has downstream consequences. Distinguished from LLM01 prompt injection by where the false content originates: LLM01 is attacker-induced direct manipulation; LLM09 is structural — the model fabricates because of its training, decoding strategy, or RAG corpus quality.

Subcategories per 2025:
- **Hallucination exploitation** — attacker crafts queries that reliably induce confident-but-wrong answers
- **Citation fabrication** — the model invents non-existent sources (a documented problem in legal AI)
- **Statistical-shift attacks** — repeated misinformation injected into the training corpus until the model adopts it
- **Reputation attacks** — targeted prompts that make the model emit defamatory or incorrect content about a specific person/brand

## Academic citations

The cs* corpora cover the relevant underlying ML reliability and adversarial robustness theory:

- **NN calibration** (in CS 442) — fundamental: when can you trust confidence scores?
- **The "overconfidence" line of adversarial robustness work** — multiple papers across CS 562 and CS 598
- **Carlini hallucination + watermarking** (in CS 598 Fall 2021) — relevant to attribution and content provenance
- **TextFooler / TextAttack family** — adversarial NLP, relevant when attackers target the input to induce reliability failures
- **Constitutional AI** and **RLHF reliability** — post-2022, mostly outside the cs* corpora but referenced in OWASP and AI-Native LLM Security

## Current survey instances

NuClide does not directly survey LLM09 — misinformation findings require:
- Active LLM invocation (operator's budget)
- Output evaluation (correctness ground truth)
- Multi-query iteration

Both cross NuClide restraint policy. However, NuClide surveys produce **enabling conditions** for LLM09 attacks:

- **LiteLLM open proxies** (`surveys/2026-06-06-litellm.md`) — anyone can invoke the operator's `claude-sonnet-4-6` / `gpt-5.4` / `gemini-2.5-pro` via the open gateway, including for misinformation generation at scale, billed to the operator.
- **RAGFlow open registration** — registered tenants can introduce misinformation documents into knowledge bases (overlaps LLM04 poisoning).

## Why LLM09 is the hardest class to survey from outside

Unlike LLM02 (configuration disclosure) or LLM06 (deployed exploit config), LLM09 cannot be detected from the infrastructure layer. It requires output evaluation. The detection methodology is fundamentally different — it lives in evaluation frameworks (HELM, BIG-bench, FactScore, TruthfulQA) rather than in network scanning.

This is a class NuClide flags as **out of scope for current population-survey methodology** while acknowledging the class exists and is enabled by the same auth-permissive-default cohort.

## Defensive controls

- RAG-grounded responses (every claim cited to a retrieved document)
- Confidence calibration in user-facing UX (uncertainty surfaced, not hidden)
- Domain-specific fact-checking layers (especially for legal, medical, financial)
- Watermarking outputs (attribution + tamper detection)
- Post-hoc audit logs (the model's claims are reviewable)

## Related NICE roles

- **541 Vulnerability Assessment Analyst** — surfaces the enabling-condition infrastructure
- **661 R&D Specialist** — would build evaluation frameworks if NuClide expanded into LLM09 directly
- **K0202 KSA: Knowledge of application firewall concepts (single point of authentication/audit/policy enforcement)** — relevant to output-filtering layers

## Insight #76 connection

Same enabling-condition argument as LLM02 / LLM06 / LLM07 / LLM08: the auth-permissive default lets attackers reach the LLM endpoint. What they do with it (LLM09 misinformation, LLM10 denial-of-wallet, LLM06 RCE) depends on the specific platform and the operator's tooling configuration.
