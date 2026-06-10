#!/usr/bin/env python3
"""Build deduped tool-name union + per-host distribution from probe results."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2])

per_host = []
tool_counter = Counter()
tool_descriptions = defaultdict(set)
tool_schemas = defaultdict(list)
servers = Counter()
protocol_versions = Counter()
distinct_toolsets = Counter()

for line in src.read_text().splitlines():
    if not line.strip():
        continue
    rec = json.loads(line)
    if not rec.get("init_pass"):
        continue
    init = rec.get("initialize", {}) or {}
    sinfo = init.get("serverInfo", {}) or {}
    servers[f'{sinfo.get("name","?")} {sinfo.get("version","?")}'] += 1
    protocol_versions[init.get("protocolVersion", "?")] += 1

    tools = (rec.get("tools_list") or {}).get("tools", []) or []
    names = tuple(sorted(t.get("name", "") for t in tools))
    distinct_toolsets[names] += 1
    per_host.append({"ip": rec["ip"], "endpoint": rec.get("endpoint"), "tools": list(names)})
    for t in tools:
        n = t.get("name", "")
        tool_counter[n] += 1
        d = t.get("description") or ""
        if d:
            tool_descriptions[n].add(d.strip()[:500])
        sch = t.get("inputSchema") or {}
        if sch and sch not in tool_schemas[n]:
            tool_schemas[n].append(sch)

inventory = {
    "host_count": sum(distinct_toolsets.values()),
    "distinct_toolsets": [{"tools": list(k), "host_count": v} for k, v in distinct_toolsets.most_common()],
    "server_distribution": dict(servers),
    "protocol_versions": dict(protocol_versions),
    "tool_distribution": [
        {
            "name": name,
            "host_count": cnt,
            "descriptions": sorted(tool_descriptions[name]),
            "schemas": tool_schemas[name],
        }
        for name, cnt in tool_counter.most_common()
    ],
}
out.write_text(json.dumps(inventory, indent=2))
print(f"hosts={inventory['host_count']} distinct_toolsets={len(distinct_toolsets)} tools={len(tool_counter)}")
for name, cnt in tool_counter.most_common():
    print(f"  {cnt:>3}x {name}")
print(f"servers: {dict(servers)}")
print(f"protocols: {dict(protocol_versions)}")
