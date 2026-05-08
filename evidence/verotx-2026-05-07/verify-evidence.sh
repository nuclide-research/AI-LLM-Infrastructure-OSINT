#!/bin/bash
# Verify the integrity + timestamp authenticity of this evidence bundle.
# Run from the directory containing MANIFEST.sha256.

set -euo pipefail

cd "$(dirname "$0")"

echo "═══ Verifying evidence bundle integrity ═══"
echo

echo "[1/3] SHA-256 manifest check..."
if sha256sum -c MANIFEST.sha256 --quiet 2>&1; then
    echo "      ✓ all files match recorded hashes"
else
    echo "      ✗ FAIL — files have been modified or removed"
    exit 1
fi

echo
echo "[2/3] OpenTimestamps verification..."
if ! command -v ots >/dev/null 2>&1; then
    echo "      ⚠ 'ots' not installed; skip with: pip install opentimestamps-client"
else
    ots upgrade MANIFEST.sha256.ots 2>&1 || true
    ots verify MANIFEST.sha256.ots 2>&1 || true
fi

echo
echo "[3/3] Sanity check — server-asserted Date headers in HTTP captures..."
for f in raw/cap-*.http; do
    date_hdr=$(grep -i "^date:" "$f" 2>/dev/null | head -1 | tr -d '\r')
    echo "      $f  →  $date_hdr"
done

echo
echo "═══ Verification complete ═══"
