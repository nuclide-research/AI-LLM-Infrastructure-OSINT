#!/usr/bin/env bash
# Polls Grafana /api/health and alerts on version change or EOL status.
# Cron: */30 * * * * /path/to/watch_grafana_eol.sh >> /var/log/grafana-watch.log 2>&1

TARGET="https://grafana.atomicmail.ai/api/health"
KNOWN_VERSION="11.5.2"
EOL_SUPPORTED=("11.6" "12.")

response=$(curl -sk --max-time 8 "$TARGET")
version=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null)
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [[ -z "$version" || "$version" == "unknown" ]]; then
    echo "$ts [UNREACHABLE] no valid response from $TARGET"
    exit 0
fi

is_supported=0
for prefix in "${EOL_SUPPORTED[@]}"; do
    [[ "$version" == "$prefix"* ]] && is_supported=1
done

if [[ "$version" != "$KNOWN_VERSION" ]]; then
    echo "$ts [CHANGED] version was $KNOWN_VERSION, now $version"
fi

if [[ "$is_supported" -eq 0 ]]; then
    echo "$ts [EOL] $version not in supported branches: ${EOL_SUPPORTED[*]}"
else
    echo "$ts [OK] $version is in a supported branch"
fi
