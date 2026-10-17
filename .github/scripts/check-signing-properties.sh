#!/usr/bin/env bash

# Safely inspect the signing certificate stored in GitHub Actions Secrets.
#
# This script NEVER prints:
# - STORE_TEST_JKS
# - LOCAL_TEST_JKS
# - storePassword
# - keyPassword
# - keyAlias
# - private key material
#
# It prints only public certificate information required to identify
# the APK signing certificate.

set +x
set -euo pipefail
umask 077

EXPECTED_SHA256="09:55:40:49:4D:53:F4:8C:A0:51:BC:86:C3:92:C4:6E:DB:29:72:5D:A5:59:2B:D8:AF:3C:3D:02:7B:31:66:BB"

temp_dir="$(mktemp -d)"
properties="$temp_dir/local.properties"
keystore="$temp_dir/test.jks"

cleanup() {
    rm -rf -- "$temp_dir"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "===== Versanium signing certificate check ====="
echo

#
# Check Secrets
#

if [[ -z "${LOCAL_TEST_JKS:-}" ]]; then
    echo "ERROR: LOCAL_TEST_JKS secret is not configured."
    exit 1
fi

if [[ -z "${STORE_TEST_JKS:-}" ]]; then
    echo "ERROR: STORE_TEST_JKS secret is not configured."
    exit 1
fi

echo "LOCAL_TEST_JKS: configured"
echo "STORE_TEST_JKS: configured"

#
# Decode Secrets without printing their contents
#

if ! printf '%s' "$LOCAL_TEST_JKS" | base64 --decode > "$properties" 2>/dev/null; then
    echo "ERROR: Failed to decode LOCAL_TEST_JKS."
    exit 1
fi

if ! printf '%s' "$STORE_TEST_JKS" | base64 --decode > "$keystore" 2>/dev/null; then
    echo "ERROR: Failed to decode STORE_TEST_JKS."
    exit 1
fi

unset LOCAL_TEST_JKS
unset STORE_TEST_JKS

echo "Secrets decoded successfully."

#
# Load signing properties in a subshell and obtain only the
# certificate fingerprint. Passwords and aliases are never printed.
#

result="$(
    PROPERTIES="$properties" \
    KEYSTORE="$keystore" \
    bash --noprofile --norc <<'INNER'
set +x
set -euo pipefail

source "$PROPERTIES"

if [[ -z "${storePassword:-}" ]]; then
    echo "ERROR: storePassword is missing." >&2
    exit 1
fi

if [[ -z "${keyAlias:-}" ]]; then
    echo "ERROR: keyAlias is missing." >&2
    exit 1
fi

fingerprint="$(
    keytool \
        -list \
        -v \
        -keystore "$KEYSTORE" \
        -storepass "$storePassword" \
        -alias "$keyAlias" 2>/dev/null |
    sed -n 's/^[[:space:]]*SHA256:[[:space:]]*//p' |
    head -n 1
)"

if [[ -z "$fingerprint" ]]; then
    echo "ERROR: Could not obtain SHA-256 certificate fingerprint." >&2
    exit 1
fi

printf '%s\n' "$fingerprint"
INNER
)"

if [[ -z "$result" ]]; then
    echo "ERROR: Certificate fingerprint was empty."
    exit 1
fi

ACTUAL_SHA256="$(printf '%s' "$result" | tr '[:lower:]' '[:upper:]')"

echo
echo "===== Certificate SHA-256 ====="
echo "$ACTUAL_SHA256"

echo
echo "===== Expected official Titanium SHA-256 ====="
echo "$EXPECTED_SHA256"

echo
echo "===== Result ====="

if [[ "$ACTUAL_SHA256" == "$EXPECTED_SHA256" ]]; then
    echo "MATCH"
    echo "The GitHub Actions signing key matches the official Titanium signing certificate."
else
    echo "NOT MATCH"
    echo "The GitHub Actions signing key does NOT match the official Titanium signing certificate."
fi

echo
echo "Private key material and passwords were not printed."
