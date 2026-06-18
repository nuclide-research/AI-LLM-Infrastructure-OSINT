---
type: methodology
insight_number: 106
title: "A 422 on a chat/inference endpoint is a request-format mismatch, not an access denial: probe the payload-shape variants before closing the host as denied"
status: candidate
codified: 2026-06-18
source_survey: Cat-RAG-Framework-Servers 2026-06-17 / 2026-06-18 (re-verification)
falsifiability_tier: high
falsified_by: a host that returns 422 to every documented payload shape AND returns 200-with-data to an authenticated request of the same shape (proving the 422 was an auth gate masquerading as a validation error)
related_insights: [16, 69, 104]
---

# Insight #106 - A 422 is a format mismatch, not an access denial

## The pattern

Verification stage treats 4xx as "closed" by reflex. 401 and 403 are genuine
access verdicts. **422 Unprocessable Entity is not.** A 422 from a chat or
inference endpoint means the request reached application logic, passed any auth
gate, and was rejected at the payload-schema layer: wrong field name, wrong body
shape, missing required key. The endpoint answered. It answered "your JSON is
wrong," not "you may not be here."

Closing a host on a 422 is a false negative. The access surface is open; the
prober just spoke the wrong dialect. The correct move on a 422 is to enumerate
the payload-shape variants, not to log the host as denied.

## Empirical founding case - babbid.com (F6, Cat-RAG-Framework-Servers)

`108.132.72.10:443` (app.babbid.com), a LlamaIndex chat backend, returned 422 to
the first probe shape. Reading the 422 body, not the status code, gave the fix:
the validation error named the missing field in Spanish.

```
POST /api/chat  {"messages":[...]}   -> 422  "El campo mensaje es obligatorio"
POST /api/chat  {"message":"...","chatHistory":[]} -> 200  live LLM reply, zero auth
```

The field was `message` (singular), not the OpenAI-idiomatic `messages` (plural),
and the second field was `chatHistory`, not `history`. One payload-shape swap
turned a presumed-denied host into a confirmed HIGH: a named commercial operator
running unauthenticated LLM inference with stateful UUID sessions. Had the survey
closed on the 422, F6 would never have been found.

## The variant set to probe on a 422

When a chat/inference endpoint returns 422, cycle the body shape before closing:

| Idiom | Body |
|-------|------|
| OpenAI chat | `{"messages":[{"role":"user","content":"..."}]}` |
| Singular message | `{"message":"...","chatHistory":[]}` |
| Query field | `{"query":"..."}` / `{"q":"..."}` |
| Nested data | `{"data":{"message":"..."}}` |
| Prompt field | `{"prompt":"..."}` / `{"input":"..."}` |

Always read the 422 body first. Pydantic/FastAPI (LlamaIndex, LightRAG, most
Python AI backends) emit `{"detail":[{"loc":[...],"msg":"field required"}]}` that
names the missing field outright. The body hands you the schema; you rarely have
to guess past one variant.

## Why this is the request-side dual of Insight #16

Insight #16 says a 200 is identity, not auth state, so read the response body
before declaring a host open. #106 is the same discipline applied to the request
side of a 4xx: a 422 is format state, not access state, so read the response body
(and reshape the request) before declaring a host closed.

| | Insight #16 (response side) | Insight #106 (request side) |
|---|---|---|
| Signal misread | 200 = "open" | 422 = "denied" |
| What it actually is | identity / reachability | payload-schema rejection |
| Correction | probe the data layer behind the 200 | reshape the request, re-probe |
| Failure mode | false positive (over-claim) | false negative (missed finding) |

#16 guards against over-claiming; #106 guards against under-claiming. Both reduce
to the same rule: the status code is a pointer, the body is the verdict.

## How to apply

1. Partition 4xx by meaning, not by the leading `4`. 401/403 = access verdict
   (closed, log as surface-open-not-exercised). 422 (and 400 with a validation
   body) = format verdict (open, re-probe).
2. On a 422, read the body first. Pydantic/FastAPI name the missing field.
   Reshape and re-probe before advancing the host to any closed disposition.
3. Cycle the variant set (table above) once. If every documented shape still
   returns 422, only then is the host closed at this endpoint, and note WHY
   (exhausted variant set), per the no-silent-cap rule.
4. Restraint unchanged: the goal is to confirm the access surface is open
   (a single 200 with a minimal benign payload). Stop at severity confirmation;
   do not extract chat history, traverse files, or read session state.

## Population consequence

Bare-IP / single-shape verifiers systematically under-count unauth chat surfaces:
every host whose backend expects a non-OpenAI payload shape is logged as denied on
the 422. The miss is biased, not random. It tracks the smaller, custom,
often-commercial operators (babbid is a Spanish coworking firm, not a hyperscaler)
who wrote their own request schema instead of cloning the OpenAI contract. That is
exactly the operator class the auth-on-default thesis cares about: the long tail
that inherits framework defaults and ships a bespoke front end. A one-variant
re-probe on every 422 recovers them at near-zero cost.

## Related insights

- Insight #16 - A 200 is identity, not auth state (the response-side dual; #106 is
  the same rule on the request side of a 4xx)
- Insight #69 - A curated-scan negative is not a host negative (a 422 close is a
  scan-technique negative, not a host-access negative)
- Insight #104 - A global auth flag is not an endpoint verdict (sibling
  verification-stage false-disposition guard; #104 over-trusts a flag, #106
  over-trusts a status code)

## Promotion criteria

Confirmed at 1 platform / 1 host (LlamaIndex, babbid.com: 422 on `messages`, 200
on `message`). Promotion to numbered Insight requires a second independent host
where a payload-shape re-probe converts a 422 into a confirmed 200-with-data
finding that a single-shape verifier would have closed.
