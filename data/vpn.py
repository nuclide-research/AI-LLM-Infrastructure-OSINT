"""
vpn.py — Mullvad VPN guard + geo-aware exit selection + rotation

Uses the local mullvad CLI daemon. No Mullvad account API needed.
Verification uses https://am.i.mullvad.net/json (confirms actual exit IP).

Usage in scanners:
    import vpn

    vpn.require(target_country='id')       # guard: connect to Jakarta if needed
    vpn.require()                          # guard: any VPN connection will do
    vpn.connect(target_country='br')       # explicit: connect to São Paulo
    vpn.rotate()                           # pick random exit from relay pool, reconnect
    vpn.rotate(target_country='id')        # rotate within Jakarta pool
    s = vpn.status()                       # dict: connected, ip, exit_country, etc.

    # In a long scan loop — rotate every N probes:
    for i, target in enumerate(targets):
        if i > 0 and i % rotate_every == 0:
            vpn.rotate()
        probe(target)
"""

import subprocess
import json
import time
import sys
import urllib.request
import urllib.error
from typing import Optional

# ── Geo routing table ─────────────────────────────────────────────────────────
# Target country ISO2 → (mullvad_country_code, city_code)
# Priority: in-country > regional > neutral (nl)
# Update as Mullvad adds/removes relays.

GEO_MAP = {
    # Southeast Asia
    'id': ('id', 'jpu'),   # Indonesia → Jakarta
    'sg': ('sg', 'sin'),   # Singapore → Singapore
    'my': ('sg', 'sin'),   # Malaysia → Singapore
    'th': ('sg', 'sin'),   # Thailand → Singapore
    'vn': ('sg', 'sin'),   # Vietnam → Singapore
    'ph': ('sg', 'sin'),   # Philippines → Singapore
    'kh': ('sg', 'sin'),   # Cambodia → Singapore
    'mm': ('sg', 'sin'),   # Myanmar → Singapore
    # East Asia
    'tw': ('jp', 'tyo'),   # Taiwan → Tokyo
    'kr': ('jp', 'tyo'),   # South Korea → Tokyo
    'jp': ('jp', 'tyo'),   # Japan → Tokyo
    'cn': ('jp', 'tyo'),   # China → Tokyo
    'hk': ('jp', 'tyo'),   # Hong Kong → Tokyo
    # South Asia
    'in': ('sg', 'sin'),   # India → Singapore (no IN exit)
    'pk': ('sg', 'sin'),   # Pakistan → Singapore
    'bd': ('sg', 'sin'),   # Bangladesh → Singapore
    'lk': ('sg', 'sin'),   # Sri Lanka → Singapore
    # Pacific
    'au': ('au', 'syd'),   # Australia → Sydney
    'nz': ('au', 'syd'),   # New Zealand → Sydney
    # Latin America
    'br': ('br', 'sao'),   # Brazil → São Paulo
    'ar': ('br', 'sao'),   # Argentina → São Paulo
    'cl': ('br', 'sao'),   # Chile → São Paulo
    'co': ('br', 'sao'),   # Colombia → São Paulo
    'mx': ('us', 'dal'),   # Mexico → Dallas
    # North America
    'us': ('nl', 'ams'),   # US gov targets → Netherlands (attribution break)
    'ca': ('nl', 'ams'),   # Canada → Netherlands
    # Europe
    'gb': ('gb', 'lon'),   # UK → London
    'de': ('de', 'fra'),   # Germany → Frankfurt
    'fr': ('nl', 'ams'),   # France → Amsterdam
    'nl': ('nl', 'ams'),   # Netherlands → Amsterdam
    'se': ('se', 'sto'),   # Sweden → Stockholm
    'no': ('se', 'sto'),   # Norway → Stockholm
    'ru': ('se', 'sto'),   # Russia → Stockholm
    'pl': ('de', 'fra'),   # Poland → Frankfurt
    'cz': ('de', 'fra'),   # Czech Republic → Frankfurt
    'ro': ('de', 'fra'),   # Romania → Frankfurt
    'gr': ('de', 'fra'),   # Greece → Frankfurt
    'sk': ('de', 'fra'),   # Slovakia → Frankfurt
    # MENA
    'eg': ('nl', 'ams'),   # Egypt → Amsterdam
    'ma': ('nl', 'ams'),   # Morocco → Amsterdam
    'dz': ('nl', 'ams'),   # Algeria → Amsterdam
    'sa': ('nl', 'ams'),   # Saudi Arabia → Amsterdam
    'ae': ('nl', 'ams'),   # UAE → Amsterdam
    'tr': ('de', 'fra'),   # Turkey → Frankfurt
    # Africa
    'za': ('nl', 'ams'),   # South Africa → Amsterdam
    'ng': ('nl', 'ams'),   # Nigeria → Amsterdam
    'ke': ('nl', 'ams'),   # Kenya → Amsterdam
    # Default fallback
    '_default': ('nl', 'ams'),
}


def _run(args: list[str]) -> tuple[int, str]:
    """Run mullvad CLI, return (returncode, stdout)."""
    r = subprocess.run(['mullvad'] + args, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def status() -> dict:
    """
    Return current VPN state.

    Returns:
        {
            connected: bool,
            state: str,          # "Connected" | "Disconnected" | "Connecting" | ...
            ip: str | None,      # exit node IP if connected
            exit_country: str | None,
            exit_city: str | None,
            server: str | None,
            verified: bool,      # True if am.i.mullvad.net confirms Mullvad exit
        }
    """
    _, out = _run(['status'])
    connected = out.startswith('Connected')
    state = out.split('\n')[0].strip() if out else 'Unknown'

    result = {
        'connected': connected,
        'state': state,
        'ip': None,
        'exit_country': None,
        'exit_city': None,
        'server': None,
        'verified': False,
    }

    if connected:
        # Parse "Connected to xx-city-wg-001 in City, Country"
        import re
        m = re.search(r'Connected to (\S+) in ([^,]+), (.+)', out)
        if m:
            result['server'] = m.group(1)
            result['exit_city'] = m.group(2).strip()
            result['exit_country'] = m.group(3).strip()

    return result


def verify() -> dict:
    """
    Hit am.i.mullvad.net to confirm actual external IP and Mullvad exit status.
    Returns the JSON response dict, or raises on failure.
    """
    req = urllib.request.Request(
        'https://am.i.mullvad.net/json',
        headers={'User-Agent': 'nuclide-recon/1.0'}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
        return data
    except Exception as e:
        raise RuntimeError(f'VPN verify failed: {e}')


def connect(
    target_country: Optional[str] = None,
    country_code: Optional[str] = None,
    city_code: Optional[str] = None,
    wait: float = 8.0,
    verify_after: bool = True,
) -> dict:
    """
    Connect to VPN.

    Priority:
      1. explicit country_code + city_code
      2. GEO_MAP lookup by target_country
      3. Current relay setting (just run `mullvad connect`)

    Returns status() dict after connecting.
    """
    if country_code and city_code:
        _run(['relay', 'set', 'location', country_code, city_code])
    elif target_country:
        cc_norm = target_country.lower()
        cc, city = GEO_MAP.get(cc_norm, GEO_MAP['_default'])
        _run(['relay', 'set', 'location', cc, city])

    _run(['connect'])
    deadline = time.time() + wait
    while time.time() < deadline:
        time.sleep(1.5)
        s = status()
        if s['connected']:
            break

    s = status()
    if not s['connected']:
        raise RuntimeError(f'VPN failed to connect within {wait}s')

    if verify_after:
        try:
            v = verify()
            s['ip'] = v.get('ip')
            s['verified'] = v.get('mullvad_exit_ip', False)
            s['exit_ip_hostname'] = v.get('mullvad_exit_ip_hostname', '')
        except Exception:
            s['verified'] = False

    return s


def disconnect() -> None:
    """Disconnect from VPN."""
    _run(['disconnect'])


def get_relays(country_code: Optional[str] = None, city_code: Optional[str] = None) -> list[dict]:
    """
    Fetch active WireGuard relay list from Mullvad public API.
    Optionally filtered by country_code and/or city_code.
    Returns list of relay dicts: {hostname, country_code, city_code, ipv4_addr_in, active}
    """
    req = urllib.request.Request(
        'https://api.mullvad.net/www/relays/all/',
        headers={'User-Agent': 'nuclide-recon/1.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        relays = json.loads(resp.read())

    wg = [r for r in relays if r.get('type') == 'wireguard' and r.get('active')]
    if country_code:
        wg = [r for r in wg if r.get('country_code', '').lower() == country_code.lower()]
    if city_code:
        wg = [r for r in wg if r.get('city_code', '').lower() == city_code.lower()]
    return wg


def rotate(
    target_country: Optional[str] = None,
    country_code: Optional[str] = None,
    city_code: Optional[str] = None,
    verify_after: bool = True,
) -> dict:
    """
    Rotate to a new random exit node and reconnect.

    If target_country given, uses GEO_MAP to select the pool.
    If country_code/city_code given, picks from that pool.
    Otherwise picks from all active WireGuard relays.

    Returns status() dict after reconnecting.
    """
    import random

    # Resolve pool
    pool_cc, pool_city = None, None
    if country_code:
        pool_cc, pool_city = country_code, city_code
    elif target_country:
        pool_cc, pool_city = GEO_MAP.get(target_country.lower(), GEO_MAP['_default'])

    try:
        relays = get_relays(country_code=pool_cc, city_code=pool_city)
    except Exception:
        # Fallback: just reconnect with current relay setting
        relays = []

    if relays:
        picked = random.choice(relays)
        hostname = picked['hostname']
        # mullvad relay set hostname <hostname>
        _run(['relay', 'set', 'hostname', hostname])
        label = hostname
    else:
        # No relay list — use geo-map routing
        if pool_cc and pool_city:
            _run(['relay', 'set', 'location', pool_cc, pool_city])
        label = f'{pool_cc}/{pool_city}' if pool_cc else 'random'

    # Reconnect
    _run(['reconnect'])
    deadline = time.time() + 12
    while time.time() < deadline:
        time.sleep(1.5)
        s = status()
        if s['connected']:
            break

    s = status()
    if not s['connected']:
        raise RuntimeError(f'VPN rotation failed to reconnect within 12s')

    if verify_after:
        try:
            v = verify()
            s['ip'] = v.get('ip')
            s['verified'] = v.get('mullvad_exit_ip', False)
            s['exit_ip_hostname'] = v.get('mullvad_exit_ip_hostname', '')
        except Exception:
            s['verified'] = False

    print(f'[vpn] Rotated → {label}  IP: {s.get("ip", "?")}', file=sys.stderr)
    return s


def require(
    target_country: Optional[str] = None,
    auto_connect: bool = True,
    abort_if_unverified: bool = False,
) -> dict:
    """
    Guard: ensure VPN is up before active probing.

    If not connected and auto_connect=True, connects (using GEO_MAP if
    target_country given). If auto_connect=False and not connected, exits.

    If abort_if_unverified=True, also verifies with am.i.mullvad.net.

    Returns final status dict.
    """
    s = status()

    if not s['connected']:
        if not auto_connect:
            print('[vpn] ERROR: VPN not connected. Refusing to probe.', file=sys.stderr)
            sys.exit(1)

        cc_label = f' (geo: {target_country})' if target_country else ''
        print(f'[vpn] Not connected — connecting{cc_label}...', file=sys.stderr)
        s = connect(target_country=target_country)

    if abort_if_unverified:
        try:
            v = verify()
            if not v.get('mullvad_exit_ip'):
                print(f'[vpn] WARNING: External IP {v.get("ip")} is not a Mullvad exit node.',
                      file=sys.stderr)
                if abort_if_unverified:
                    sys.exit(1)
            else:
                s['verified'] = True
                s['ip'] = v.get('ip')
        except RuntimeError as e:
            print(f'[vpn] {e}', file=sys.stderr)
            if abort_if_unverified:
                sys.exit(1)

    return s


def print_status() -> None:
    """Pretty-print VPN state + external IP verification."""
    s = status()
    state_color = '\033[32m' if s['connected'] else '\033[31m'
    reset = '\033[0m'
    print(f'[vpn] State      : {state_color}{s["state"]}{reset}')
    if s['connected']:
        print(f'[vpn] Server     : {s.get("server", "?")}')
        print(f'[vpn] Exit       : {s.get("exit_city", "?")}, {s.get("exit_country", "?")}')

    try:
        v = verify()
        is_mull = v.get('mullvad_exit_ip', False)
        mull_label = f'\033[32mMullvad exit\033[0m' if is_mull else '\033[31mNOT Mullvad exit\033[0m'
        print(f'[vpn] External IP: {v.get("ip")}  ({mull_label})')
        if is_mull:
            print(f'[vpn] Exit node  : {v.get("mullvad_exit_ip_hostname", "?")}')
    except RuntimeError as e:
        print(f'[vpn] Verify     : {e}')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Mullvad VPN guard utility')
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('status', help='Show VPN status + verify external IP')

    c = sub.add_parser('connect', help='Connect to VPN')
    c.add_argument('--target', metavar='CC', help='Target country ISO2 (uses GEO_MAP)')
    c.add_argument('--country', metavar='CC', help='Mullvad country code (overrides GEO_MAP)')
    c.add_argument('--city', metavar='CITY', help='Mullvad city code')

    sub.add_parser('disconnect', help='Disconnect from VPN')

    r = sub.add_parser('require', help='Guard: connect if needed and verify')
    r.add_argument('--target', metavar='CC', help='Target country ISO2')
    r.add_argument('--strict', action='store_true', help='Exit if not verified Mullvad exit')

    g = sub.add_parser('geo', help='Show recommended exit for a target country')
    g.add_argument('country', metavar='CC')

    args = p.parse_args()

    if args.cmd == 'status' or args.cmd is None:
        print_status()
    elif args.cmd == 'connect':
        s = connect(
            target_country=getattr(args, 'target', None),
            country_code=getattr(args, 'country', None),
            city_code=getattr(args, 'city', None),
        )
        print(f'[vpn] Connected — exit IP: {s.get("ip", "?")} verified={s.get("verified")}')
    elif args.cmd == 'disconnect':
        disconnect()
        print('[vpn] Disconnected')
    elif args.cmd == 'require':
        s = require(target_country=getattr(args, 'target', None),
                    abort_if_unverified=getattr(args, 'strict', False))
        print(f'[vpn] Ready — exit IP: {s.get("ip", "?")} server: {s.get("server", "?")}')
    elif args.cmd == 'geo':
        cc, city = GEO_MAP.get(args.country.lower(), GEO_MAP['_default'])
        print(f'{args.country} → mullvad relay: {cc}/{city}')
