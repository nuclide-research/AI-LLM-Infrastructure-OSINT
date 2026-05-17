# Meow / Indexrm ransom note + paste.sh content — 2026-05-17

## Identical ransom note across 3 sample hosts (104.197.153.228, 104.248.1.214, 101.44.26.183)

```
Your database has been deleted from your server, but all the information
remains stored on our cluster. The instructions for recovery are as follows:
You must send 0.0041 BTC to the following wallet:
bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r .
Then, you must send an email to wendy.etabw@gmx.com with the following code:
0SH7HH1Q72JL (it is important that you write it correctly, as it corresponds
to your database).
You must also attach the txid (the Bitcoin transaction ID) to the message.
After following these steps, we will send you a zip file with all your
information.
You have 48 hours to complete the steps.
For More Info - https://tli.sh/73x1k
```

The per-host code `0SH7HH1Q72JL` is **identical across all three sample hosts** — the "corresponds to your database" claim is false. This is one actor's broadcast spam.

## paste.sh landing page (decrypted)

URL: `https://tli.sh/73x1k` → `https://paste.sh/3S0XQFln#5h8mVtIQ3_-hvSvhAwstTNLJ`

E2E-encrypted via AES-256-CBC + PBKDF2 (SHA512, iter=1) — paste.sh's idiosyncratic OpenSSL-compatible KDF. Password = `paste.id + serverkey + url-fragment + "https://paste.sh"`.

Decrypted content:

```
Subject: 📋🔐 paste.sh

Email - wendy.etabw@gmx.com

Pay 0.0041 btc to the wallet address bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r

Dont bother trying to contact us before paying.
Contact Us To Negotiate

If you live in China watch some tutorials on how you can buy btc in China
using VPN OR Use P2P platforms to buy btc.

Once you pay, you'll get a download link which you can use to download all
your data back.
```

Two notable signals:
- **Self-contradicting instructions** — "Don't bother trying to contact us before paying" / "Contact Us To Negotiate." Bot template inconsistency, not deliberate strategy.
- **Explicit China-victim awareness** — instructions for circumventing China's cryptocurrency-purchase restrictions (P2P + VPN). Matches our observed wipe-population skew toward Tencent/Aliyun/Huawei Cloud-hosted Chinese operators.

## Wallet activity (per mempool.space, 2026-05-17)

```
address:           bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r
total tx count:    8
incoming payments: 5
total received:    0.01802363 BTC  (~$1,800 USD at ~$100k/BTC)
total sent out:    0.01800927 BTC  (attacker swept; balance dust)
```

5 victims paid out of ~4,411 wiped hosts visible from yesterday's survey — **0.11% pay rate**. Even at a low pay rate, single-actor automated extortion at this scale yields four-figure income per campaign cycle.

## Infrastructure (all clearnet, all third-party, all abuse-reportable)

| Component | Provider | Abuse contact |
|---|---|---|
| `tli.sh` URL shortener | unknown (.sh = Saint Helena ccTLD) | needs investigation |
| `paste.sh` E2E pastebin | Caddy + Cloudflare-fronted | abuse@cloudflare.com |
| `wendy.etabw@gmx.com` | GMX (German free webmail) | abuse@gmx.com / abuse@gmx.net |
| `bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r` | Bitcoin native SegWit address | submitted to: Chainalysis, ID-Ransomware, ransomwhe.re |
