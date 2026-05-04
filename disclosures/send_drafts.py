#!/usr/bin/env python3
"""
send_drafts.py — Send disclosure emails from _gmail_drafts.json via Gmail SMTP.

Identity: From: Nicholas Michael Kloster <nicholas@nuclide-research.com>
Auth: Gmail App Password (16-char) read from ~/.config/nuclide/nicholas-gmail-app-password
Transport: smtp.gmail.com:587 STARTTLS

Modes:
  --dry-run    (default) Print the To/Subject/Severity table; don't connect to SMTP.
  --test ADDR  Send a single test email to ADDR. Verifies SMTP + From-alias.
  --send       Send all queued drafts (skips ones already in _sent.json).
  --limit N    Cap number of sends this run.
  --only SLUG  Send only one specific slug.
  --severity X Send only drafts of severity X (CRITICAL / HIGH / LOW).
  --throttle S Seconds between sends (default 8). 36 emails @ 8s = ~5 min.
"""
import argparse
import json
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS_JSON = ROOT / "_gmail_drafts.json"
SENT_LOG = ROOT / "_sent.json"
APP_PW_PATH = Path.home() / ".config" / "nuclide" / "nicholas-gmail-app-password"

FROM_ADDR = "nicholas@nuclide-research.com"
FROM_NAME = "Nicholas Michael Kloster"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def load_app_password() -> str:
    if not APP_PW_PATH.exists():
        sys.exit(
            f"FATAL: app password not found at {APP_PW_PATH}\n"
            f"Create it with:\n"
            f"  echo -n 'xxxx xxxx xxxx xxxx' > {APP_PW_PATH}\n"
            f"  chmod 600 {APP_PW_PATH}"
        )
    pw = APP_PW_PATH.read_text().strip().replace(" ", "")
    if len(pw) != 16:
        sys.exit(f"FATAL: app password at {APP_PW_PATH} is {len(pw)} chars; expected 16 (spaces stripped).")
    return pw


def load_drafts() -> list:
    return json.loads(DRAFTS_JSON.read_text())


def load_sent() -> set:
    if SENT_LOG.exists():
        return set(json.loads(SENT_LOG.read_text()))
    return set()


def save_sent(sent: set) -> None:
    SENT_LOG.write_text(json.dumps(sorted(sent), indent=2))


def build_message(to_addr: str, cc: str | None, subject: str, body: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((FROM_NAME, FROM_ADDR))
    msg["To"] = to_addr
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="nuclide-research.com")
    msg["Reply-To"] = FROM_ADDR
    msg.attach(MIMEText(body, "plain", "utf-8"))
    return msg


def smtp_session(app_password: str) -> smtplib.SMTP:
    s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(FROM_ADDR, app_password)
    return s


def dry_run(drafts: list, sent: set, filter_severity=None, only_slug=None, limit=None):
    print(f"=== DRY RUN ===")
    print(f"  Total queue:  {len(drafts)}")
    print(f"  Already sent: {len(sent & {d['slug'] for d in drafts})}")
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
    print(f"\nNo SMTP connection attempted. Run --send to actually send.")


def send_one(server: smtplib.SMTP, draft: dict) -> tuple[bool, str]:
    msg = build_message(draft["to"], draft.get("cc"), draft["subject"], draft["body"])
    rcpts = [r.strip() for r in draft["to"].split(",") if r.strip()]
    if draft.get("cc"):
        rcpts += [r.strip() for r in draft["cc"].split(",") if r.strip()]
    try:
        server.sendmail(FROM_ADDR, rcpts, msg.as_string())
        return True, "ok"
    except smtplib.SMTPRecipientsRefused as e:
        return False, f"refused: {e.recipients}"
    except smtplib.SMTPException as e:
        return False, f"smtp: {e}"
    except Exception as e:
        return False, f"err: {type(e).__name__}: {e}"


def send_test(addr: str):
    pw = load_app_password()
    print(f"Connecting to {SMTP_HOST}:{SMTP_PORT} as {FROM_ADDR}...")
    server = smtp_session(pw)
    print("Login OK. Sending test message...")
    test_msg = build_message(
        addr,
        None,
        "[NuClide test] SMTP relay verification",
        "This is a test message confirming the Gmail SMTP relay for "
        "nicholas@nuclide-research.com is working.\n\n"
        "If you see this with From: Nicholas Michael Kloster <nicholas@nuclide-research.com> "
        "and no 'via gmail.com' indicator, the alias and app-password setup is correct.\n\n"
        "Safe to delete.\n",
    )
    server.sendmail(FROM_ADDR, [addr], test_msg.as_string())
    server.quit()
    print(f"Test sent to {addr}. Check the inbox to confirm From: header.")


def send_all(drafts: list, sent: set, throttle: float, filter_severity=None, only_slug=None, limit=None):
    pw = load_app_password()
    print(f"Connecting to {SMTP_HOST}:{SMTP_PORT} as {FROM_ADDR}...")
    server = smtp_session(pw)
    print("Login OK. Beginning send loop.")

    sent_count = 0
    err_count = 0
    skipped_count = 0
    n = 0

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
        ok, info = send_one(server, d)
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

    server.quit()
    print()
    print(f"=== Summary ===")
    print(f"  Sent OK:  {sent_count}")
    print(f"  Errors:   {err_count}")
    print(f"  Skipped:  {skipped_count} (already in {SENT_LOG.name})")


def main():
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default).")
    grp.add_argument("--send", action="store_true", help="Actually send.")
    grp.add_argument("--test", metavar="ADDR", help="Send single test message to ADDR.")
    ap.add_argument("--limit", type=int, default=None, help="Cap number of sends this run.")
    ap.add_argument("--only", metavar="SLUG", help="Send only this slug.")
    ap.add_argument("--severity", choices=["CRITICAL", "HIGH", "LOW"], help="Filter by severity.")
    ap.add_argument("--throttle", type=float, default=8.0, help="Seconds between sends (default 8).")
    args = ap.parse_args()

    if args.test:
        send_test(args.test)
        return

    drafts = load_drafts()
    sent = load_sent()

    if args.send:
        send_all(drafts, sent, args.throttle,
                 filter_severity=args.severity, only_slug=args.only, limit=args.limit)
    else:
        dry_run(drafts, sent,
                filter_severity=args.severity, only_slug=args.only, limit=args.limit)


if __name__ == "__main__":
    main()
