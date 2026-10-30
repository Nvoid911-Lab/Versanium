# AOriginForward execution preparation — 2026-10-24 JST

Purpose: **Java転送経路の確認用。native要求元は未確定。**
This document prepares a later manual operation; no saved-tree apply, compile,
Actions or B application is performed/authorized by this preparation.

## Baseline and bounded transaction

Use built/signed **AOrigin** evidence
`/home/takuma/versanium/config-a-origin-evidence-LfbK0s`:
applied.json.updated_provenance must equal after-apk-provenance.json and the
original saved recorder's current result. Reject A/installed/Forward records.
The43-input manifest is pinned to56e011e. It contains AOrigin41 plus pristine
wrapper and Activity delegate. All43 match before; exactly controller/wrapper/
Activity delegate change; other40 and baseline native zoom hashes remain fixed.
This excludes B. Do not invoke the branch's general patch pipeline on the host.

New prepare_config_a_origin_forward.py is independent of old apply/validate
gates. It reuses only existing utility functions and pinned prior source-byte
reconstruction, not earlier transaction paths. Starting from saved fixed HEAD
in scratch,257b and5faa diagnostics and Base transform reproduce the baseline
AOrigin bytes, including its controller. Wrapper/Activity start from fixed HEAD.
The exact56e delegate transform produces three after files. Before/after hashes
must equal the pinned manifest. No observed hash allowlist is used.

Preflight checks clean separate controller ancestry/allowed delta, original Run9
repository HEAD7d9102f, fixed Chromium/Vanadium ancestry via original validator,
GN/depot/clang tools, Test arm64 identity, provenance and43 source hashes.
It records all generated out/Default files (Ninja/Siso/APKs included), modes and
symlink destinations; this can be I/O-heavy. Use an idle host. Evidence is new
and external. No key/config secrets or browsing data are read into these reports.

Explicit --apply additionally rejects active builder/process-check failure,
backs up all three originals externally, records intent/source/output/tool/
baseline hashes and provenance BEFORE writes, rechecks each original before
writing, then verifies all43, other tracked source diff, tools/output unchanged
and updated provenance. Failure leaves intent applied=false and backups/current
partial state for inspection. No rollback/reset/retry. --verify requires same
controller/baseline evidence, completed record and unchanged precompile output.
Old helper conditions and manifests remain unchanged.

## Default read-only command (the only step currently requested)

Update ONLY the separate controller to the final reviewed preparation SHA first.
Do not pull/checkout inside saved workspace. Keep these variables for later use.

```sh
RUN9_WORKSPACE='/home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951'
RUN9_CONTROL='/home/takuma/versanium/run9-control-093f787-3k3yO1'
RUN9_ORIGIN_BASE='/home/takuma/versanium/config-a-origin-evidence-LfbK0s'
RUN9_FORWARD_EVIDENCE=$(mktemp -d /home/takuma/versanium/config-a-origin-forward-evidence-XXXXXX)
git -C "$RUN9_CONTROL" rev-parse HEAD
python3 "$RUN9_CONTROL/tools/versanium/prepare_config_a_origin_forward.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --origin-applied "$RUN9_ORIGIN_BASE/applied.json" \
  --after-apk "$RUN9_ORIGIN_BASE/after-apk-provenance.json" \
  --evidence "$RUN9_FORWARD_EVIDENCE/read-only.json"
```

Real-host43 preflight has not been executed here. Stop on any mismatch, missing
file, aliased path, unexpected delta, builder, changed graph/tool/output or
ambiguous/partial application. Do not remove inputs, relax hashes or use old A
helpers. Process checks do not prevent another runner starting later.

## Future explicit apply and verify — NOT executed now

```sh
python3 "$RUN9_CONTROL/tools/versanium/prepare_config_a_origin_forward.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --origin-applied "$RUN9_ORIGIN_BASE/applied.json" \
  --after-apk "$RUN9_ORIGIN_BASE/after-apk-provenance.json" \
  --evidence "$RUN9_FORWARD_EVIDENCE/applied.json" --apply
python3 "$RUN9_CONTROL/tools/versanium/prepare_config_a_origin_forward.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --origin-applied "$RUN9_ORIGIN_BASE/applied.json" \
  --after-apk "$RUN9_ORIGIN_BASE/after-apk-provenance.json" \
  --evidence "$RUN9_FORWARD_EVIDENCE/applied.json" --verify
```

## Later manual Java/NullAway → APK → existing-key signature

1. Separately authorize compile only after successful apply/verify and review of
   current idle/capacity/graph state. Preserve previous signed AOrigin/A/Diagnostic
   APKs and evidence externally. Keep source/out paths and frozen depot_tools.
   Use DEPOT_TOOLS_UPDATE=0 and existing depot_tools on PATH; in chromium/src run
   `autoninja -C out/Default -j 6 chrome_java` with pipefail, new external log and
   exit status. This is real chrome_java/NullAway integration for all3 existing
   classes, not fragment/double proof. No new GN/JNI target. Stop on Java or
   NullAway errors, requested regeneration/hooks/sync or toolchain/input changes.
2. Recompute original saved write_build_provenance.py via --repository saved
   workspace --source chromium/src --output new external after-java-provenance.json;
   require equality with Forward applied.json.updated_provenance. Verify Forward43
   source hashes and tools again. Old --verify is PREcompile only and deliberately
   rejects changed generated outputs after a real compile.
3. After successful Java and separate APK authorization, same source/out/depot:
   `autoninja -C out/Default -j 6 chrome_public_apk`. Preserve log/exit status and
   after-apk provenance with the same equality check and43 hashes. Existing
   out APK is a compiler output, so retain prior distribution copies first.
   No C++ source changes are selected, but graph-driven integration is still
   required; do not promise no native work or reuse/completion time.
4. Check unsigned package io.github.nvoid911.versanium.test, version156.0.8078.47,
   arm64-v8a and SHA256. Only then separately authorize the existing common.sh
   sign_apk flow with existing key and correct SCRIPT_DIR/$0 handling as successful
   AOrigin signing. No key recreation, local.properties/password dump or signing
   configuration change. New external destination:
   `signed-test/Versanium-156.0.8078.47_Test_ConfigAOriginForward.apk`.
   Require absent destination; retain AOrigin/A/Diagnostic. Existing apksigner
   must verify certificate SHA256
   2e79f4e6597f7ea320b32c4889405c8d93081774a0fd8db4a040def0d54ad120,
   exact package/version/ABI and final/copied APK hash. No upload/Release/Actions.

The helper performs none of these compilation/signing commands. Review scope
table in config-a-origin-forward-review.md before the future device comparison.
Known①OFF/②ON remain separate; restart is instructed for each future trial
until directly reported. AOrigin② restart was directly confirmed historically.
Capture fixed stage logs through exit/media stop, not URL/title/auth or broad
stack logs. Suppressed/null/mismatched-tab events can be absent. These labels
identify Java forwarding; native renderer/browser/security origin remains unknown.

## Validation boundary

Tests reconstruct exact selected source bytes in temporary scratch and exercise
read-only/apply/verify fixtures, wrong baselines, hash drift/repeated application,
second-write failure and generated-output drift, retaining backups and false
intent without rollback. Transaction host validation is mocked in fixtures;
this is not real-host preflight, Java/NullAway/APK compile or device verification.

Executed locally:67 tests PASS (5 new preparation tests), including all43 real
selected-file bytes in scratch, other40 retention and native-input drift
rejection. actionlint, documented shell syntax (not execution) and diff checks
PASS. No host paths/evidence were read here; current host43 match is unverified.
