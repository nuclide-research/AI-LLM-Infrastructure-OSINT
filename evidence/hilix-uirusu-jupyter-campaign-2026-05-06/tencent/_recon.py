import subprocess, os
cmds = [
    'whoami',
    'hostname',
    'uname -a',
    'nvidia-smi 2>/dev/null || echo NO_GPU',
    'cat /proc/meminfo 2>/dev/null | head -5',
    'df -h / 2>/dev/null | tail -1',
    'ip addr show 2>/dev/null | grep "inet " | head -5',
    'cat /etc/os-release 2>/dev/null | head -5',
    'ls /home/ 2>/dev/null',
    'cat /etc/passwd 2>/dev/null | grep -v nologin | grep -v false | head -10',
]
for cmd in cmds:
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, timeout=10).strip()
        print(f"[{cmd}]: {out}")
    except Exception as e:
        print(f"[{cmd}]: ERROR {e}")
