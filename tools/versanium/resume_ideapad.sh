#!/bin/bash
# Recovery only: leave the original source/output paths intact.
set -euo pipefail
CONTROL_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
: "${GITHUB_WORKSPACE:?Run through the manual IdeaPad recovery workflow}"
: "${RUNNER_TEMP:?}"
WORKSPACE="$GITHUB_WORKSPACE"
[ "${GITHUB_REPOSITORY:-}" = 'Nvoid911-Lab/Versanium' ] || exit 1
[ "${RUNNER_NAME:-}" = 'versanium-ideapad' ] || exit 1
[ "${VERSANIUM_TEST_BUILD:-}" = 1 ] || exit 1
[ "${VERSANIUM_RELEASE_APPROVED:-}" = false ] || exit 1
# No other recovery job can use this tree, even across workflow names/refs.
exec 9>"$WORKSPACE/.versanium-resume.lock"
flock -n 9 || { echo 'Workspace is already in use' >&2; exit 1; }
python3 "$CONTROL_ROOT/tools/versanium/check_resume.py" --workspace "$WORKSPACE" --control "$CONTROL_ROOT"
export DEPOT_TOOLS_UPDATE=0
export PATH="$WORKSPACE/depot_tools:$PATH"
# Existing build.sh/common.sh are read from the pinned controller; secrets stay
# in a private temporary directory and are created only after compilation.
source "$CONTROL_ROOT/common.sh"
KEY_DIR=$(mktemp -d "$RUNNER_TEMP/versanium-keys.XXXXXX")
export SCRIPT_DIR="$KEY_DIR"
MONITOR_PID=''
cleanup() {
    if [ -n "$MONITOR_PID" ]; then kill "$MONITOR_PID" 2>/dev/null || true; wait "$MONITOR_PID" 2>/dev/null || true; fi
    rm -rf -- "$KEY_DIR"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -p "$CONTROL_ROOT/diagnostics"
vmstat -t 60 > "$CONTROL_ROOT/diagnostics/vmstat.txt" &
MONITOR_PID=$!
cd "$WORKSPACE/chromium/src"
export VERSION=155.0.8059.79
# Limit local compilation pressure on the 12GB WSL instance. This changes
# scheduling only; retain the prepared GN configuration and output tree.
printf 'Recovery local job limit: 6\n'
printf '\nResuming chrome_java at %s\n' "$(date -Is)"
autoninja -C out/Default -j 6 chrome_java
printf '\nResuming chrome_public_apk at %s\n' "$(date -Is)"
autoninja -C out/Default -j 6 chrome_public_apk
APK=out/Default/apks/ChromePublic.apk
[ -s "$APK" ] || { echo 'Expected ChromePublic.apk was not generated' >&2; exit 1; }
: "${LOCAL_TEST_JKS:?Signing properties secret missing}"
: "${STORE_TEST_JKS:?Signing key secret missing}"
umask 077
set_keys
export ANDROID_HOME="$PWD/third_party/android_sdk/public"
export PATH="$PWD/third_party/jdk/current/bin:$PATH"
# Delivery uses a fresh controller-local directory; old APKs cannot be staged.
mkdir -p "$CONTROL_ROOT/resume-release"
sign_apk "$APK" "$CONTROL_ROOT/resume-release/$VERSION-arm64-v8a.apk"
python3 "$CONTROL_ROOT/tools/versanium/package_apk.py" --source "$CONTROL_ROOT/resume-release" --output "$CONTROL_ROOT/dist" --version "$VERSION" --test
