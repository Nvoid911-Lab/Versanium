#!/bin/bash
# Read-only WSL inspection; does not start, stop, register or clone a runner.
set -eu
printf 'Linux account: '; id -un
printf 'WSL distribution: %s\n' "${WSL_DISTRO_NAME:-not-reported}"
if command -v whoami.exe >/dev/null 2>&1; then
    printf 'Windows interop account: '; whoami.exe || printf '%s\n' 'Interop identity unavailable.'
fi
if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -NonInteractive -Command 'Get-Volume | Where-Object DriveType -eq Fixed | Select-Object DriveLetter,SizeRemaining,Size | ConvertTo-Json -Compress' || printf '%s\n' 'Windows fixed-volume query unavailable; inspect locally.'
fi
printf 'Kernel: '
uname -sr
awk '/^(MemTotal|MemAvailable|SwapTotal|SwapFree):/ {print}' /proc/meminfo
df -h .
printf 'Runner listener count: '
pgrep -xc Runner.Listener || true
printf 'Compiler process count: '
pgrep -xc clang++ || true
printf '%s\n' 'Confirm the owning Windows account and workspace in the runner service configuration locally. Do not share environment/credential dumps.'
