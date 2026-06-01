#!/usr/bin/env python3
"""
send_drafts_api.py — Send disclosure emails from _gmail_drafts.json via Gmail API (OAuth).

Identity: From: Nicholas Michael Kloster <nicholas@nuclide-research.com>
Auth: OAuth 2.0 client (Desktop app), token cached locally.
  Client secret: ~/.config/nuclide/client_secret.json
  Token cache:   ~/.config/nuclide/nicholas-token.json
Scope: gmail.send (write-only — least privilege; can't read mailbox).

Modes:
  --dry-run    (default) Print queue table; no API connection.
  --auth       Run OAuth flow only (creates token, doesn't send).
  --test ADDR  Send a single test email to ADDR.
  --send       Send all queued drafts (skips ones in _sent.json).
  --limit N    Cap number of sends this run.
  --only SLUG  Send only one specific slug.
  --severity X Send only drafts of severity X (CRITICAL / HIGH / LOW).
  --throttle S Seconds between sends (default 8). 36 emails @ 8s = ~5 min.
"""
import argparse
import base64
import json
import os
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS_JSON = ROOT / "_gmail_drafts.json"
SENT_LOG = ROOT / "_sent.json"
CONFIG_DIR = Path.home() / ".config" / "nuclide"
CLIENT_SECRET = CONFIG_DIR / "client_secret.json"
TOKEN_PATH = CONFIG_DIR / "nicholas-token.json"

FROM_ADDR = "nicholas@nuclide-research.com"
FROM_NAME = "Nicholas Michael Kloster"
# gmail.compose covers BOTH drafts().create() and messages().send().
# (gmail.send alone cannot create drafts.) Changing the scope invalidates
# the cached token — the next run does a fresh OAuth consent.
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def get_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                sys.exit(
                    f"FATAL: client_secret not found at {CLIENT_SECRET}\n"
                    f"Download it from Google Cloud Console (OAuth 2.0 Client ID "
                    f"of type 'Desktop app') and save to that path with mode 600."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0, prompt="consent")
        TOKEN_PATH.write_text(creds.to_json())
        os.chmod(TOKEN_PATH, 0o600)

    return build("gmail", "v1", credentials=creds)


def load_drafts() -> list:
    return json.loads(DRAFTS_JSON.read_text())


def load_sent() -> set:
    if SENT_LOG.exists():
        return set(json.loads(SENT_LOG.read_text()))
    return set()


def save_sent(sent: set) -> None:
    SENT_LOG.write_text(json.dumps(sorted(sent), indent=2))


def build_raw(to_addr: str, cc: str | None, subject: str, body: str,
              html: str | None = None) -> dict:
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((FROM_NAME, FROM_ADDR))
    msg["To"] = to_addr
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="nuclide-research.com")
    msg["Reply-To"] = FROM_ADDR
    # multipart/alternative: plaintext part first, HTML part last — mail
    # clients render the last part they understand.
    msg.attach(MIMEText(body, "plain", "utf-8"))
    if html:
        msg.attach(MIMEText(html, "html", "utf-8"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def dry_run(drafts: list, sent: set, filter_severity=None, only_slug=None, limit=None):
    print("=== DRY RUN ===")
    print(f"  Total queue:   {len(drafts)}")
    print(f"  Already sent:  {len(sent & {d['slug'] for d in drafts})}")
    print()
    print(f"{'#':>3}  {'SEV':<8}  {'STATUS':<6}  {'SLUG':<30}  {'TO':<40}  SUBJECT")
    print("-" * 130)
    n = 0
    by_sev = {}
    for d in drafts:
        slug = d["slug"]
        if filter_severity and d["severity"] != filter_severity:
            continue
        if only_slug and slug != only_slug:
            continue
        if limit and n >= limit:
            break
        n += 1
        status = "SENT" if slug in sent else "queue"
        by_sev[d["severity"]] = by_sev.get(d["severity"], 0) + 1
        print(f"{n:>3}  {d['severity']:<8}  {status:<6}  {slug:<30}  {d['to']:<40}  {d['subject'][:60]}")
    print()
    print(f"=== Severity breakdown (this filter): {by_sev}")
    print("\nNo API connection attempted. Run --send to actually send.")


def send_one(service, draft: dict) -> tuple[bool, str]:
    msg = build_raw(draft["to"], draft.get("cc"), draft["subject"],
                    draft["body"], draft.get("html"))
    try:
        service.users().messages().send(userId="me", body=msg).execute()
        return True, "ok"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def draft_one(service, draft: dict) -> tuple[bool, str]:
    """Create a Gmail draft (not sent). Lands in the Drafts folder."""
    msg = build_raw(draft["to"], draft.get("cc"), draft["subject"],
                    draft["body"], draft.get("html"))
    try:
        result = service.users().drafts().create(
            userId="me", body={"message": msg}).execute()
        return True, result.get("id", "ok")
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def send_test(addr: str):
    print(f"Authenticating as {FROM_ADDR}...")
    service = get_service()
    print("Auth OK. Sending test message...")
    msg = build_raw(
        addr,
        None,
        "[NuClide test] Gmail API verification",
        "This is a test message confirming the Gmail API path for "
        "nicholas@nuclide-research.com is working.\n\n"
        "If you see this with From: Nicholas Michael Kloster <nicholas@nuclide-research.com>, "
        "the OAuth + send-as configuration is correct.\n\n"
        "Safe to delete.\n",
    )
    service.users().messages().send(userId="me", body=msg).execute()
    print(f"Test sent to {addr}. Check the inbox to confirm From: header.")


def send_all(drafts: list, sent: set, throttle: float, filter_severity=None, only_slug=None, limit=None):
    print(f"Authenticating as {FROM_ADDR}...")
    service = get_service()
    print("Auth OK. Beginning send loop.")

    sent_count = err_count = skipped_count = n = 0

    for d in drafts:
        slug = d["slug"]
        if filter_severity and d["severity"] != filter_severity:
            continue
        if only_slug and slug != only_slug:
            continue
        if slug in sent:
            print(f"  [skip] {slug} (already sent)")
            skipped_count += 1
            continue
        if limit and n >= limit:
            break
        n += 1

        print(f"  [{n:>2}] sending {slug:<30} → {d['to']}", end=" ... ", flush=True)
        ok, info = send_one(service, d)
        if ok:
            print("OK")
            sent_count += 1
            sent.add(slug)
            save_sent(sent)
        else:
            print(f"FAIL ({info})")
            err_count += 1

        if n < (limit or len(drafts)):
            time.sleep(throttle)

    print()
    print("=== Summary ===")
    print(f"  Sent OK:  {sent_count}")
    print(f"  Errors:   {err_count}")
    print(f"  Skipped:  {skipped_count} (already in {SENT_LOG.name})")


def draft_all(drafts: list, filter_severity=None, only_slug=None, limit=None):
    """Create Gmail drafts (NOT sent) for the selected queue entries.
    No _sent.json tracking — drafts can be safely re-created."""
    print(f"Authenticating as {FROM_ADDR} (scope: gmail.compose)...")
    service = get_service()
    print("Auth OK. Creating drafts.")

    made = err = n = 0
    for d in drafts:
        slug = d["slug"]
        if filter_severity and d["severity"] != filter_severity:
            continue
        if only_slug and slug != only_slug:
            continue
        if limit and n >= limit:
            break
        n += 1
        print(f"  [{n:>2}] drafting {slug:<40} → {d['to']}", end=" ... ", flush=True)
        ok, info = draft_one(service, d)
        if ok:
            print(f"OK (draft id {info})")
            made += 1
        else:
            print(f"FAIL ({info})")
            err += 1

    print()
    print("=== Summary ===")
    print(f"  Drafts created: {made}")
    print(f"  Errors:         {err}")
    print(f"  → Check the Gmail Drafts folder for {FROM_ADDR}")


def main():
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--dry-run", action="store_true", default=True)
    grp.add_argument("--auth", action="store_true", help="Run OAuth flow only.")
    grp.add_argument("--test", metavar="ADDR")
    grp.add_argument("--send", action="store_true")
    grp.add_argument("--draft", action="store_true",
                     help="Create Gmail drafts (NOT sent). Lands in the Drafts folder.")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--only", metavar="SLUG")
    ap.add_argument("--severity", choices=["CRITICAL", "HIGH", "LOW"])
    ap.add_argument("--throttle", type=float, default=8.0)
    args = ap.parse_args()

    if args.auth:
        get_service()
        print(f"Token saved to {TOKEN_PATH}")
        return
    if args.test:
        send_test(args.test)
        return

    drafts = load_drafts()
    sent = load_sent()

    if args.send:
        send_all(drafts, sent, args.throttle,
                 filter_severity=args.severity, only_slug=args.only, limit=args.limit)
    elif args.draft:
        draft_all(drafts,
                  filter_severity=args.severity, only_slug=args.only, limit=args.limit)
    else:
        dry_run(drafts, sent,
                filter_severity=args.severity, only_slug=args.only, limit=args.limit)


if __name__ == "__main__":
    main()
