#!/bin/bash
# Read-only WSL inspection; does not start, stop, register or clone a runner.
set -eu
printf 'Linux account: '; id -un
printf 'WSL distribution: %s\n' "${WSL_DISTRO_NAME:-not-reported}"
printf 'Kernel: '; uname -sr
awk '/^(MemTotal|MemAvailable|SwapTotal|SwapFree):/ {print}' /proc/meminfo
df -h .
printf 'Runner listener count: '
pgrep -xc Runner.Listener || true
printf 'Compiler process count: '
pgrep -xc clang++ || true
printf '%s\n' 'Confirm the owning Windows account and workspace in the runner service configuration locally. Do not share environment/credential dumps.'
