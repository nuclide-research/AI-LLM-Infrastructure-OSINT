# aiweather.top — AI Weather Outfit Recommendation — Working Notes

**Host:** 43.143.225.104
**Cloud:** Unknown (likely Tencent Cloud or Alibaba Cloud given CN service + IP range)
**Domain:** aiweather.top (did not resolve within probe window)
**Status:** Initial probe complete
**Priority:** 8

---

## Confirmed Services

| Port | Service | Auth |
|---|---|---|
| 8000 | LangGraph FastAPI — AI天气穿搭推荐API v1.0.0 | NONE |

## Root Response

```json
{
  "service": "AI天气穿搭推荐API",
  "description": "基于LangGraph的智能穿搭推荐系统",
  "version": "1.0.0"
}
```

Translation: "AI Weather Outfit Recommendation API" — "LangGraph-based intelligent outfit recommendation system"

## Endpoints

- `POST /outfit-recommendation` — generates outfit recommendation
- `POST /daily-weather` — daily weather query
- `POST /hourly-weather` — hourly weather query
- `GET /docs` — Swagger UI (open)
- `GET /openapi.json` — full schema (open)

## PII-Adjacent Finding

POST request body includes:
- `cityId` — city identifier
- `openId` — **user identifier** — ties each request to a specific user account

The `openId` field flows through an unauthenticated endpoint. User identity is carried in the request, meaning user activity can be tracked or attributed without the user's knowledge that the endpoint is open.

## Output Fields

- `imgUrl` — generated image URL for the recommended outfit
- `cache_hit` — boolean, indicates whether response was served from cache

The `imgUrl` field: if the URL scheme is predictable (e.g., based on cityId + date + openId), generated images may be enumerable without querying the API.

## Pending Probes

- [ ] GET /openapi.json — full schema, confirm all fields
- [ ] PTR / ASN attribution on 43.143.225.104
- [ ] WHOIS aiweather.top
- [ ] What format is imgUrl? Is the URL scheme enumerable?
- [ ] What backend weather API or LLM is used?
- [ ] Port 3000 — timed out; retry
