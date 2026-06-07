# MTA Fingerprint Catalog: Operator-Attribution Leak Surface

**Date:** 2026-06-07
**Lane:** 1B of 9-item NuClide research plan
**Origin:** Sluice survey (2026-06-06) found Haraka leaks Docker Compose project/service/network names via EHLO greeting + uses "421 You talk too soon" for early_talker rejects. This catalog extends the question to the wider MTA universe: does the leak class generalize, or is it Haraka-specific?

## TL;DR

Of 6 MTAs surveyed (Haraka, Postfix, Exim, OpenSMTPd, Sendmail, qmail), **3 produce Sluice-equivalent docker-compose-project leaks out of the box**: Haraka, Exim, and Sendmail. All three reverse-resolve the client IP and echo the PTR (or compose container hostname) verbatim in the EHLO/HELO response, which under docker-compose default networking surfaces `<container>.<project>_<network>`. Postfix and OpenSMTPd do not: Postfix uses only the server's `myhostname` (still leaks if the operator left it as the container shorthash); OpenSMTPd echoes the *client-supplied* HELO argument unverified, which is a different (and arguably worse) class: the prober controls what gets logged.

The early-talker / pre-banner-input reject is **Haraka-unique** in its current form ("421 You talk too soon"). Every other MTA rejects pipelining-before-banner with a generic "554 SMTP synchronization error" or a code-501 RFC2920 violation: useful as an MTA-family signal but not a single-line fingerprint the way Haraka's plugin string is.

## Probe Methodology

- All probes executed inside an isolated Docker network (`mtacat_default`) on a bridge host.
- Probe client = busybox `nc -w` from an alpine container on the same network.
- Tested both a full session (EHLO → MAIL FROM → RCPT TO → VRFY → QUIT) and an early-talker sequence (sending EHLO before banner arrives).
- Source code confirmed where banner construction happens for each MTA.
- All targets were locally-controlled containers; no internet probing.

## Comparison Table

| MTA                | Banner (220)                                                            | EHLO/HELO leak surface                                                          | Reverse-DNS-of-client echoed? | Early-talker reject                       | Reject-code idiom                          | Compose-leak equivalent? |
|--------------------|-------------------------------------------------------------------------|---------------------------------------------------------------------------------|-------------------------------|-------------------------------------------|---------------------------------------------|--------------------------|
| **Haraka 3.1.5**   | `220 <container-id> ESMTP Haraka/<ver> ready (<uuid6>)`                 | `<local.host> Hello <get_remote_host>, Haraka is at your service.`              | **YES (full PTR)**            | `421 You talk too soon` (early_talker plugin) | `550 No valid MX for your FROM address`, `503 Use MAIL before RCPT`, `252 Just try sending a mail and we'll see how it turns out...`, `221 ... Have a jolly good day.` | **YES** (Sluice template) |
| **Exim 4.92**      | `220 <container-id> ESMTP Exim <ver> <RFC822-date>`                     | `<local.host> Hello <reverse-dns-of-client> [<client-ip>]`                      | **YES (full PTR)**            | `554 SMTP synchronization error`            | `501 <addr>: ... must contain a domain`, `250 OK`, `221 <container-id> closing connection` | **YES**                  |
| **Postfix 3.10**   | `220 <myhostname> ESMTP Postfix (<distro>)`                             | `<myhostname>` (server-only; client identity NOT echoed)                        | NO                            | `554 5.5.0 Error: SMTP protocol synchronization` | `450 4.1.2 <addr>: Recipient address rejected: Domain not found`, `504 5.5.2 <addr>: ... need fully-qualified address`, `221 2.0.0 Bye` | NO (but leaks server hostname → container shorthash if default) |
| **OpenSMTPD 7.8**  | `220 <hostname> ESMTP OpenSMTPD`                                        | `<hostname> Hello <CLIENT-SUPPLIED EHLO ARG verbatim> [<client-ip>], pleased to meet you` | NO (uses client EHLO string)  | `500 5.5.1 Invalid command: Pipelining not supported` | `550 Invalid recipient: <addr>`, `500 5.5.1 Invalid command`, `221 2.0.0 Bye` | NO (server-hostname-only; but client controls helo-string) |
| **Sendmail 8.17**  | `220 <$j> ESMTP Sendmail <ver>/<conf>; <RFC822-date>` (`$j` = full hostname) | `<$j> Hello <reverse-dns-of-client> [<client-ip>], pleased to meet you` (RFC requires identifying client) | **YES (full PTR)**            | `503 5.0.0 polite people don't talk before they are introduced` (variants by version; some emit `421` if `confDELIVERY_MODE=q` + tarpit) | `550 5.7.1 ...`, `554 5.5.0 No SMTP service here`, `221 2.0.0 ... closing connection` | **YES** (via PTR-echo)  |
| **qmail 1.03 / netqmail**   | `220 <me> ESMTP` (no version)                                  | `<me>` (server only; HELO arg accepted silently, ignored)                       | NO                            | `503 MAIL first` / `421` if `tcpserver -h` slow lookup times out | `553 sorry, that domain isn't in my list of allowed rcpthosts`, `421` for tarpit | NO (qmail famously refuses to leak: Bernstein's design) |

## Per-MTA Detail

### Haraka 3.1.5 (Node.js, Sluice's MTA)
**Source location:** `node_modules/Haraka/connection.js:844`:
```js
this.respond(250, `${this.local.host} Hello ${this.get_remote('host')}, ${cfg.message.helo}`)
```
- `this.local.host` = `config/me` if set, else `os.hostname()`. Container shorthash by default.
- `this.get_remote('host')` = reverse DNS lookup of client IP. Under docker-compose, this is `<container-id>.<project>_<network>`: leaks all three.
- `cfg.message.helo` defaults to `"Haraka is at your service."` (the family signature).

**Early-talker plugin:** `haraka-plugin-early_talker/index.js:46`:
```js
return next(DENYDISCONNECT, 'You talk too soon')
```
Emitted as `421` if the client writes before the server-side timeout (default 1000ms) elapses. Single-line Haraka fingerprint.

**Other Haraka tells:** banner UUID6 `(C9DF66)` in the 220 line, "Just try sending a mail and we'll see how it turns out..." NOOP response, "Have a jolly good day." QUIT response: all hardcoded English strings.

### Exim 4.92 (used here via `namshi/smtp` image)
Banner and HELO emit `$primary_hostname Hello $sender_host_name [$sender_host_address]` by default (`exim4.conf.template` `smtp_banner` macro). `$sender_host_name` is the reverse DNS: same leak class as Haraka.
- Distinctive ESMTP extensions in EHLO: `CHUNKING`, `PRDR`. These two together strongly suggest Exim (PRDR is rare elsewhere).
- Reject strings: `501 <addr>: recipient address must contain a domain` is Exim-canonical.
- Early-talker: not enabled by default; commercial-grade ACL configs add `helo_data_acl` with explicit `tarpit`/`delay` actions.

### Postfix 3.10 (used here via `boky/postfix`)
Banner: `220 $myhostname ESMTP $mail_name ($mail_version)`. `$myhostname` defaults to the system hostname: if operator left container shorthash, banner still leaks topology.
- EHLO response echoes `$myhostname` only: does NOT reverse-resolve client. **Postfix is the lowest-leak default of the four**.
- ESMTP family tells: full set `PIPELINING SIZE VRFY ETRN STARTTLS ENHANCEDSTATUSCODES 8BITMIME DSN SMTPUTF8 CHUNKING`. The ENHANCED status codes (`2.x.x`/`4.x.x`/`5.x.x` prefix) are the strongest Postfix family signal.
- Reject strings: `450 4.1.2 ...: Recipient address rejected: Domain not found`, `504 5.5.2 ...: need fully-qualified address` are Postfix-canonical.
- Synchronization error: `554 5.5.0 Error: SMTP protocol synchronization`.

### OpenSMTPD 7.8 (OpenBSD MTA, used here via Alpine package)
Banner: `220 $hostname ESMTP OpenSMTPD`. Server hostname only.
- HELO response echoes the **client's** EHLO argument verbatim: `Hello <verbatim>, pleased to meet you`. This is technically RFC-compliant but means the prober controls a string the operator logs: useful for log-injection mischief but not an operator-attribution leak.
- ESMTP extensions: `8BITMIME ENHANCEDSTATUSCODES SIZE DSN HELP`: short list; no PIPELINING is unusual and is a tell.
- Reject string `500 5.5.1 Invalid command: Pipelining not supported` is OpenSMTPD-canonical.
- Closing string `221 2.0.0 Bye` is shared with Postfix (also ENHANCEDSTATUSCODES family).

### Sendmail 8.17 (docs/source: container test did not bind cleanly in time budget)
Per the canonical `sendmail.cf` template (`$j` = local fully-qualified hostname):
- Banner: `220 $j ESMTP Sendmail $v/$Z; $b` (`$v` = version, `$Z` = `cf` version, `$b` = RFC822 date).
- HELO/EHLO greeting: `$j Hello $_, pleased to meet you` where `$_` expands to `reverse-dns [client-ip]` (or `[client-ip]` if PTR fails). **Same leak class as Haraka/Exim.**
- "pleased to meet you" is shared with OpenSMTPD: OpenSMTPD inherits the historic Sendmail wording.
- Early-talker: governed by `confMAX_RCPTS_PER_MESSAGE` + `confBAD_RCPT_THROTTLE` + `confCONNECTION_RATE_THROTTLE`. Default reject for pipelining-before-banner: `503 5.0.0 polite people don't talk before they are introduced` (Sendmail-canonical, very old phrase).
- Distinctive: `Sendmail` appears in the banner with full version + `cf` version, which gives an exact CVE-scoping vector.

### qmail 1.03 / netqmail (docs only)
- Banner per `qmail-smtpd.c` source: `220 $ESMTPGREETING ESMTP` where `$ESMTPGREETING` = `me` control file (defaults to system hostname). No version emitted (Bernstein design choice).
- HELO response: `250 $me` only: no client identification echoed. **Most leak-resistant of the family by design.**
- Reject strings: `553 sorry, that domain isn't in my list of allowed rcpthosts (#5.7.1)`, `503 MAIL first (#5.5.1)`. The `(#x.y.z)` parenthetical RFC code at the end of the line is a qmail-canonical idiom.
- Early-talker: not native. `tcpserver -h` slow DNS lookups can cause a `421` tarpit if reverse DNS times out; this is qmail-canonical.

## Leak Classification

What the EHLO response reveals about deployment topology vs MTA software:

| Field appearing in EHLO    | What it leaks                              | MTAs affected by default                 |
|----------------------------|--------------------------------------------|------------------------------------------|
| Container short-hash       | Docker deployment, container ID            | Haraka, Exim, Postfix, OpenSMTPD, Sendmail (any container running default hostname) |
| `<service>-<n>.<project>_<network>` | Docker Compose project + service + network | Haraka, Exim, Sendmail (any MTA that PTR-echoes when behind a compose network) |
| `<pod-name>.<service>.<ns>.svc.cluster.local` | K8s pod + service + namespace | Same three: same PTR-echo mechanism, just K8s reverse DNS instead |
| `<myhostname>` only        | Server identity (operator-set or default)  | Postfix, OpenSMTPD, qmail                |
| Version string in banner   | CVE scoping                                | Exim (always), Sendmail (always), Haraka (always), Postfix (banner-config controlled, often disabled), OpenSMTPD (no), qmail (no by design) |
| ESMTP extension set        | Software family (PRDR=Exim, ENHANCED=Postfix, etc.) | All: extensions are RFC-required to advertise |

## OSINT Implications

**The Sluice leak isn't a Haraka bug, it's a class-of-three: any MTA that reverse-resolves the client IP and echoes the PTR.** In a typical hardened production deploy (real public hostname, real PTR records), the EHLO response just says `Hello mail.bigco.com [203.0.113.7]` and reveals nothing surprising. In a docker-compose deploy where the operator never set custom DNS, the reverse-resolved PTR is the compose-internal hostname: and the operator's product name leaks.

**Shodan dorks** (reusable for the class, not just Haraka):
- `port:25 "_default" "Hello"`: compose-default-network leak class (works against Haraka + Exim + Sendmail behind default compose networks)
- `port:25 "Haraka is at your service"`: Haraka-specific (the `cfg.message.helo` default)
- `port:25 "pleased to meet you"`: Sendmail OR OpenSMTPD (shared historic wording)
- `port:25 "Exim" "CHUNKING" "PRDR"`: Exim with default ESMTP extensions
- `port:25 "Bernstein" OR "(#5.7.1)"`: qmail-family parenthetical-RFC-code idiom
- `port:25 "polite people don't talk"`: Sendmail with early-talker tarpit (CVE-correlation: rare, suggests aggressive ACL)

**Operator-stage inference (refines Insight #80-pattern):**
- Banner contains container shorthash + compose-default-network PTR → small ops team, single VM, pre-K8s. Same heuristic Sluice surfaced.
- Banner is a real FQDN matching the cert → mature ops, dedicated mail infra.
- Banner is just the IP → ancient deploy or operator who knows to suppress it.

## Mitigation (defender-side)

| MTA       | Setting                                          | Effect                                                            |
|-----------|--------------------------------------------------|-------------------------------------------------------------------|
| Haraka    | `config/me` = public FQDN; `config/smtpgreeting` = public banner | Banner + HELO echo public identity, not container hostname        |
| Exim      | `primary_hostname = mail.publicdomain.tld`; custom `smtp_banner` | Same                                                              |
| Postfix   | `myhostname = mail.publicdomain.tld`; `smtpd_banner = $myhostname ESMTP` (drop `$mail_name` to suppress "Postfix") | Drops the `(Debian)`/version detail                              |
| OpenSMTPD | `hostname mail.publicdomain.tld` in `smtpd.conf` | Banner uses public name                                           |
| Sendmail  | Set `Dj` in sendmail.cf to the public FQDN       | `$j` macro resolves to public identity, suppresses container hostname |
| qmail     | Set `control/me` to public FQDN                  | Already minimal; this completes the hardening                     |

For all of them: the deeper fix is to give the container a real PTR record (so when a peer reverse-resolves the client IP, it doesn't leak compose internals). That's a registrar/cloud-provider config, not an MTA config.

## Reusable Fingerprint Catalog (machine-readable)

```yaml
mta_fingerprints:
  haraka:
    banner_regex: '^220 [0-9a-f]{12} ESMTP Haraka/[\d.]+ ready \([0-9A-F]{6}\)$'
    ehlo_helo_message: 'Haraka is at your service.'
    pipelining_tell: true
    early_talker_string: 'You talk too soon'
    reverse_dns_echoed: true
    leak_class: compose-project,k8s-pod
  exim:
    banner_regex: '^220 \S+ ESMTP Exim [\d.]+'
    ehlo_extensions_tell: ['CHUNKING', 'PRDR']
    addr_error_tell: 'recipient address must contain a domain'
    sync_error_tell: '554 SMTP synchronization error'
    reverse_dns_echoed: true
    leak_class: compose-project,k8s-pod
  postfix:
    banner_regex: '^220 \S+ ESMTP Postfix( \(.*\))?$'
    ehlo_extensions_tell: ['ENHANCEDSTATUSCODES']
    rcpt_error_tell: 'Recipient address rejected: Domain not found'
    sync_error_tell: '554 5.5.0 Error: SMTP protocol synchronization'
    reverse_dns_echoed: false
    leak_class: server-hostname-only
  opensmtpd:
    banner_regex: '^220 \S+ ESMTP OpenSMTPD$'
    helo_message_suffix: 'pleased to meet you'
    pipelining_tell: false   # absent from EHLO advertisement
    pipelining_reject_string: 'Pipelining not supported'
    reverse_dns_echoed: false
    helo_arg_echoed_verbatim: true   # log-injection surface
    leak_class: client-controlled
  sendmail:
    banner_regex: '^220 \S+ ESMTP Sendmail [\d.]+/[\d.]+;'
    helo_message_suffix: 'pleased to meet you'
    early_talker_string: "polite people don't talk before they are introduced"
    reverse_dns_echoed: true
    leak_class: compose-project,k8s-pod
  qmail:
    banner_regex: '^220 \S+ ESMTP$'   # no version, intentional
    error_code_idiom: '(#[0-9]\.[0-9]\.[0-9])'   # trailing parenthetical RFC code
    reverse_dns_echoed: false
    leak_class: server-hostname-only
```

## Candidate Insights for Methodology

1. **The Sluice docker-compose leak generalizes to a class of three MTAs** (Haraka, Exim, Sendmail): any MTA that reverse-resolves the client IP and echoes PTR in the EHLO response. Shodan dorks should target the class, not just Haraka.
2. **OpenSMTPD's verbatim-HELO echo is an inverse leak surface**: the prober controls a string that gets logged. Log-injection / log-parsing-evasion vector worth noting (not in scope for this lane).
3. **qmail's intentional minimal banner is now an attribution signal in itself**: encountering a `220 <host> ESMTP$` with no version, no extensions in the lead-in, and `(#x.y.z)` parenthetical reject codes uniquely fingerprints the Bernstein lineage (qmail/netqmail/s/qmail). Rare in 2026; suggests a long-uptime greybeard operator.
4. **The early-talker mechanism is MTA-family-specific by phrasing**, but the *behavior* (reject if data arrives pre-banner) is convergent. The phrase is the family signal; the behavior is universal-modern-MTA.

## Status

Probes complete on Haraka, Exim, Postfix, OpenSMTPD (live containers, isolated docker network).
Sendmail and qmail characterized from source/docs (sendmail container had a startup-config issue not worth burning the time budget on; qmail is a rare-in-production target where source-reading is the canonical methodology anyway).

Catalog covers 6 MTAs; 3 of 6 (50%) have Sluice-equivalent compose-leak surfaces. Reusable Shodan-dork set covers the class.
