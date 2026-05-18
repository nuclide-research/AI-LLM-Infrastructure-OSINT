---
title: "Operator workload visibility via Ollama /api/show Modelfile SYSTEM prompts"
insight_number: 24
date: 2026-05-15
tags:
  - methodology
  - enumeration
  - ollama
  - sysprompt
  - operator-attribution
related_research:
  - case-studies/commercial/ollama-population-survey-2026-05-15.md
source: case-studies/commercial/ollama-population-survey-2026-05-15.md
---

# Methodology Insight #24: Operator workload visibility via `/api/show` Modelfile SYSTEM

## The insight

When Ollama is unauthenticated, the `/api/tags` endpoint discloses
*what models the operator installed*. That is the canonical finding.

A second attribute axis, undercounted in prior surveys, is the
`POST /api/show {"name": "<model>"}` endpoint, which returns the
**Modelfile**: a structured document including the operator-set
`SYSTEM` directive, the `TEMPLATE` chat template, generation
`PARAMETERS`, the model `LICENSE`, and (in some deployments) inline
environment variables.

The `SYSTEM` block is the discovery surface. It discloses **what the
operator built on top of the framework**: agent persona, role
description, business-context priming, RAG grounding, and on some
deployments embedded credentials. This is fundamentally different
intelligence from "the operator installed `llama3.2:3b`." It is the
fingerprint of an *actual application*, not a model installation.

## The evidence

The 2026-05-15 Ollama population survey probed `/api/show` on 16,473
confirmed-unauth Ollama hosts. **1,007 returned a non-empty SYSTEM
directive (6% of the population).** Distribution after the
canonical-defaults filter:

| SYSTEM string (first ~120 chars) | Count |
|---|---|
| `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.` | 432 |
| `You are a helpful AI assistant named SmolLM, trained by Hugging Face` | 174 |
| `You are a helpful assistant.` | 31 |
| `You are a helpful AI assistant.` | 27 |
| `You are Dolphin, a helpful AI assistant.` | 11 |
| (other model-baked defaults: Deepseek, EXAONE, Hermes, Aya, Mistral) | ~50 |
| **Operator-customized SYSTEM (singletons, unique-once)** | **114** |
| Operator-customized SYSTEM (2–4 instances) | ~19 |

The **114 singleton operator-customized SYSTEMs are the discovery**.
Sample:

| SYSTEM excerpt (first 120 chars) | Operator deployment revealed |
|---|---|
| `IDENTITAS: Anda adalah Bang Ronal, asisten AI resmi Si-JACK (Sistem Informasi Jabatan Fungsional)…` | Indonesian government job-information system AI assistant |
| `You are an expert IBIT options trading analyst. You analyze Bitcoin and IBIT (iShares Bitcoin Trust ETF) market data…` | Bitcoin ETF financial-decision AI |
| `Sen Kansu AI, Turkiye'nin yapay zeka destekli robot fabrikasi uzman modelisin. UZMANLIK: Robot kinematik/dinamik…` | Turkish industrial-robotics expert AI |
| `你的名字叫MiniMind，你是一个乐于助人、知识渊博的AI助手…` | Chinese personal AI assistant |
| `Você é Anna, a assistente da Blue3…` | Brazilian Portuguese business chatbot |
| `Generate CivitAI-style prompts using comma-separated tags…` | AI prompt-engineering helper |
| `You are a Prompt Quality Coach…` | LLM-eval pipeline |
| `You are halo, a friendly and helpful AI assistant created by Shushank.` | Personal AI persona |

These are **real business deployments**, leaked verbatim via a single
unauthenticated POST.

## Why prior surveys missed this

Prior Ollama surveys (`ollama-cloud-survey-2026-05.md` and
`ollama-tier2-cloud-survey-2026-05.md`) confirmed via `/api/tags`
only. Installed models + version. They did not probe `/api/show`,
so SYSTEM-prompt exposure was invisible. aimap's `enumOllama`
function (as of v1.9.3) also covers only `/api/version` +
`/api/tags`, not `/api/show`. The population-walk dropped this
attribute axis.

## The default-filter is load-bearing

The naive count is misleading. **About 80% of "SYSTEM-leak" hosts
return a model-default SYSTEM** ("You are Qwen…", "You are a
helpful assistant…", "You are Llama…"). Those defaults are baked
into the published model on the Ollama Hub. They are not operator
intelligence. The methodology must:

1. Maintain a list of canonical model-default SYSTEMs (extending
   over time as new models ship with new defaults).
2. Frequency-count distinct SYSTEM strings in the population.
3. Filter the top-N most-common as defaults (they appear because the
   model carries them, not because the operator wrote them).
4. The remaining tail, singletons and low-frequency strings, is
   the operator-customized corpus.

Without this filter, the SYSTEM-prompt finding is overcounted ~8×.

## What the SYSTEM corpus enables

For each operator-customized SYSTEM, the methodology yields:

- **Application classification.** Indonesian gov, financial, industrial,
  personal assistant, business chatbot, eval pipeline, prompt-gen
  helper, etc. This is *what the operator is doing*, not just *what
  framework they installed*.
- **Disclosure routing**. A SYSTEM that names a specific brand
  (`Anna, a assistente da Blue3`) or government service
  (`Bang Ronal, Si-JACK`) is direct evidence of which entity owns
  the host. Often more precise than WHOIS.
- **Language / region inference.** SYSTEM prompts in non-English
  (Indonesian, Portuguese, Turkish, Chinese, Korean, Japanese)
  correlate with regional operator demographics.
- **Inlined-secret detection.** Some operators paste API keys, DB
  URIs, or auth headers into the SYSTEM as "context for the model."
  A regex pass over the SYSTEM corpus for `sk-`, `OPENAI_API_KEY`,
  database URIs, etc. yields high-priority disclosure targets.

## How to apply

For any unauth Ollama corpus:

1. Probe `POST /api/show {"name": "<first_installed_model>"}` on every
   confirmed-unauth host.
2. Parse the response for `system` (explicit field) and inline
   `SYSTEM <prompt>` in the Modelfile body.
3. Frequency-count the resulting SYSTEM strings; filter out the
   canonical-model-defaults list.
4. The singletons + low-frequency tail is the operator-deployment
   corpus.
5. Classify by domain (financial, government, industrial, etc.) and
   language for disclosure-routing intel.

For any unauth platform with a similar "what the operator configured"
endpoint (Flowise's `/api/v1/chatflows`, n8n's workflow list, Langflow
flows, OpenWebUI's saved prompts, Anything LLM's workspace
descriptions): the same axis applies. What the operator *built*, not
what they *installed*.

## Pairs with

- [[insight-03-capabilities-object-schema-leak]]. Handshake leaks
  structure even when invocation is gated. SYSTEM is the same class
  of leak at the application layer.
- [[insight-08-auth-bypass-via-misconfiguration-redirects]].
  Effective-unauth beyond literal no-auth. SYSTEM exposure is the
  application-context analogue of model-list exposure.
- [[insight-16-status-code-is-identity-not-auth-state]]. `/api/show`
  returning the SYSTEM body proves the application is operating
  correctly *and* leaking. Separate axes from the 200 status code.

## See also

- `case-studies/commercial/ollama-population-survey-2026-05-15.md`:   the survey this insight was extracted from. Section
  "Discovery Axis. `/api/show` SYSTEM-Prompt Corpus" includes the
  verbatim singleton samples.
- aimap v1.9.4 release notes (github.com/Nicholas-Kloster/aimap).
  The llama.cpp fingerprint + parallel PHASE 3 changes were also
  shipped in this session. A follow-up aimap enumOllama patch should
  add `/api/show` probing to surface this axis natively.
