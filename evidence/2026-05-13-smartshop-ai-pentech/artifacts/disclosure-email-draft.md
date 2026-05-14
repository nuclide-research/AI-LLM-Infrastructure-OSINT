To: abuse@pendc.com
CC: abuse@pendns.net, security@pendns.net
Subject: Security advisory — unauthenticated ML pipeline and production API on 78.135.66.61 (SmartShop AI / amazonrec.space)

Hello PENTECH BILISIM security / abuse team,

I'm an independent security researcher (NuClide Research). On
2026-05-13 my external research identified that the host 78.135.66.61
on your network exposes a customer operator's full MLOps pipeline
without authentication, including the production API of a
recommendation product branded SmartShop AI at api.amazonrec.space.

The host belongs to a single operator who appears to also run
nadorawear.com (mail-side) and the amazonrec.space frontend on Vercel.
This is a coordinated disclosure — no exploitation beyond passive
read-only probes, all single-shot, no automation, no destructive
operations.

Headline findings on 78.135.66.61:

  Port  Service                Severity   Issue
  ----  ----------------------  ---------  -------------------------------------
  443   FastAPI (api.amazonrec  CRITICAL   13 endpoints publicly callable with
        .space)                            zero authentication (OpenAPI spec
                                           components.securitySchemes is empty).
                                           /session/init returns real Amazon-
                                           format user IDs with interaction
                                           history; /interactions/stats reports
                                           15,139 logged interactions, 6,374
                                           Postgres writes, 15,139 S3 writes.
  5000  MLflow tracking         CRITICAL   Unauthenticated tracker exposes
                                           experiment list, run parameters,
                                           artifact URIs.
  6379  Redis                   CRITICAL   Internet-exposed, no auth, tagged
                                           "database", "eol-product".
  8080  Apache Airflow          HIGH       Sign-in page reachable; host carries
                                           11 Airflow CVE references in Shodan
                                           (CVE-2024-25142 + cluster).
  5432  PostgreSQL              HIGH       Internet-exposed.
  25,   Postfix mail            MEDIUM     "eol-product" tag in Shodan.
  110,
  143,
  465,
  587,
  995

The customer-facing API at api.amazonrec.space is the most urgent
issue. It can be reached anonymously by any Internet client and
returns:

  GET /api/v1/session/init  → {"user_id":"AH2IJABKXWIZIO2FYJXNFEXNRR6A",
                              "interaction_count":19,
                              "top_categories":["Buy a Kindle","Books",
                              "Toys & Games"], ...}

  GET /api/v1/interactions/stats  → {"total_logged":15139, "db_writes":6374,
                                     "s3_writes":15139, ...}

The user_id format matches Amazon's customer ID format. The category
pool returned by /session/pool-stats lists "AMAZON FASHION", "Prime
Video", "All Beauty", etc. If this is genuine Amazon catalog and
interaction data, it represents a third-party data-exposure concern
beyond the operator themselves.

Recommended actions (operator side):

  1. Put api.amazonrec.space behind an authentication wall (API key
     header, OAuth, or Cloudflare Access). The FastAPI spec already
     declares "global" security scope — flipping that to require a
     scheme is a one-line change.
  2. Bind Postgres (5432), Redis (6379), MLflow (5000), and Airflow
     (8080) to localhost or a private subnet. They should not be
     reachable from the public Internet.
  3. Patch the Airflow tree to a current release; the host carries
     11 distinct Airflow CVE references including CVE-2024-25142 and
     CVE-2024-26280 which permit DAG-permission bypass.
  4. Upgrade the Postfix install (Shodan tags the install as
     eol-product).

Recommended action (PENTECH side):

  - Forward this report to the operator running 78.135.66.61. The
    operator's identifying detail: hostnames mlflow.amazonrec.space,
    airflow.amazonrec.space, api.amazonrec.space, mail.nadorawear.com.

Timeline: I will publish a redacted technical writeup 14 days from
this email (2026-05-27) per standard coordinated-disclosure practice.
The published version will redact specific user IDs and any
operator-customer data. The customer operator is welcome to respond
with their preferred attribution; I'll accommodate reasonable
requests.

Reply-to for any clarifying questions:
nicholas@nuclide-research.com.

Full technical case study:
https://nuclide-research.com/case-studies/commercial/smartshop-ai-pentech-disclosure-2026-05-13
(currently in our private staging — will be published after the
disclosure window).

Thank you for your time, and for any forwarding you can do to the
operator.

Nicholas Kloster
NuClide Research
https://nuclide-research.com
