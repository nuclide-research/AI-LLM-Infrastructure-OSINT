# SharePoint Assistant — Working Notes

**Host:** 51.83.237.63
**Cloud:** Unknown (OVH or Scaleway based on IP range — to confirm)
**Domain:** allergiescleanedbowled.com (TLS cert placeholder — bare nginx default, no app)
**Status:** Initial probe complete
**Priority:** 7

---

## Confirmed Services

| Port | Service | Auth |
|---|---|---|
| 8000 | LangGraph FastAPI — "SharePoint Assistant API - LangGraph Agent" v2.0.0 | NONE |

## Root Response

```json
{
  "service": "SharePoint Assistant API - LangGraph Agent",
  "version": "2.0.0"
}
```

HTTP-only (HTTPS probe returned nothing — HTTP only on :8000).

## Health Endpoint

```json
{"status": "healthy", "agent": "ready", "graph": "initialized"}
```

Graph is live and initialized. The agent is connected and ready.

## Domain Finding

`allergiescleanedbowled.com` resolves to a bare nginx default page. The domain was the TLS cert CN — it is a placeholder, not a real application host. No web app routing configured behind it.

## Prior-Session Finding

Microsoft tenant ID `5b72381b-179a-4941-a3f8-c22cc66c3adf` surfaced in a 401 response body from a SharePoint/Microsoft Graph OAuth flow. The tenant ID persists across credential rotation.

## Pending Probes

- [ ] GET /openapi.json — what SharePoint endpoints does this agent expose?
- [ ] GET /threads — thread history
- [ ] POST /threads (new thread) — what does the agent require as input?
- [ ] Microsoft Graph webhook list — prior survey noted this was readable
- [ ] PTR / ASN attribution on 51.83.237.63
- [ ] Who registered allergiescleanedbowled.com? WHOIS.

## Case Study Angle

Corporate M365 integration. A SharePoint-connected LangGraph agent, exposed without auth. The agent has an initialized graph — it is connected to an organization's SharePoint. The tenant ID is the attribution anchor. The agent's document access scope depends on what OAuth consent was granted — but the conversational interface to that scope is open.
