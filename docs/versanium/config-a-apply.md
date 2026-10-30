# Configuration A execution preparation — 2026-10-24 JST

User reports b341e67902e3398cf0cc12b4b17b737d73d83c31 host comparison passed:
applied.json / after-apk-provenance / current inputs equal and installed40/40
match. No A apply/compile occurred. This supersedes the pending comparison status
in older preparation reports. Cloud has not independently read those host bytes.

`prepare_config_a.py` is a new A-only helper. Older helpers and manifest remain
unchanged. The base is the installed diagnostic four-file correction, not the
original unpatched Run9. A changes only PiP controller Java; B is unavailable in
this helper and stays deferred until A device logs.

The source recipe uses fixed saved Chromium HEAD Java, applies the60b diagnostic
patch to verify installed hash, reverses that patch in scratch, then applies the
257b selected diagnostic patch. It requires the resulting A hash in the reviewed
b341 manifest. No replacement is inferred from observed source bytes. All40
installed hashes must match before and all40 A hashes afterward.

Before mutation it recomputes original-recorder provenance and checks equality
with diagnostic applied.post_update_provenance and after-apk record, original
repository/pins, manifest and clean separate controller. It records full output
file bytes hashes (including APKs, Ninja/Siso, GN args; symlinks as link targets),
GN/clang binaries, exact baseline evidence hashes and non-controller tracked
source diff. This full output inventory can be I/O heavy; operate on an idle
host. It cannot prevent a new concurrent process starting after process checks.

An explicit apply saves the original Java externally, then writes intent,
changes exactly one file, verifies A40/40, unchanged other tracked-source diff,
all other recorded provenance fields and full output bytes. New source diff is
recorded as updated_provenance. Partial failure retains intent with applied=false,
backup and any partial/new source. STOP; no automatic reset/rollback/reapply.

## Copyable host commands — not executed here

Update only the separate controller to the final reviewed PR5 SHA. Do not pull,
checkout, clean or reset the saved workspace. Use a fresh external evidence
directory; the helper refuses existing evidence/backup files. The baseline
directory below is the user-confirmed diagnostic build evidence.

```sh
RUN9_WORKSPACE='/home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951'
RUN9_CONTROL='/home/takuma/versanium/run9-control-093f787-3k3yO1'
RUN9_BASE='/home/takuma/versanium/diagnostic-preflight-7f6a921-8mZuLC'
RUN9_A_EVIDENCE=$(mktemp -d /home/takuma/versanium/config-a-evidence-XXXXXX)
git -C "$RUN9_CONTROL" rev-parse HEAD
python3 "$RUN9_CONTROL/tools/versanium/prepare_config_a.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --baseline-applied "$RUN9_BASE/applied.json" \
  --after-apk "$RUN9_BASE/after-apk-provenance.json" \
  --evidence "$RUN9_A_EVIDENCE/read-only.json"
```

Only after reviewing read-only success and a separate apply authorization:

```sh
python3 "$RUN9_CONTROL/tools/versanium/prepare_config_a.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --baseline-applied "$RUN9_BASE/applied.json" \
  --after-apk "$RUN9_BASE/after-apk-provenance.json" \
  --evidence "$RUN9_A_EVIDENCE/applied.json" --apply
python3 "$RUN9_CONTROL/tools/versanium/prepare_config_a.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --baseline-applied "$RUN9_BASE/applied.json" \
  --after-apk "$RUN9_BASE/after-apk-provenance.json" \
  --evidence "$RUN9_A_EVIDENCE/applied.json" --verify
```

`--verify` is read-only and before-compilation only: original output state is
expected unchanged. Normal compiler output changes make it unsuitable afterward.
Never repeat --apply after success. Reject hash drift, repeated application,
dirty controller, changed baseline evidence, wrong source/pins/toolchain/Test
identity, generated-output movement or failed process checks.

## Future separately authorized chrome_java → APK → signing

No compile or signing is performed by this helper. After apply/recheck and a
separate build instruction, use SAME source/out/depot_tools with
DEPOT_TOOLS_UPDATE=0. Run chrome_java first with a reviewed job cap, pipefail and
new log/exit-code files. On success recompute ORIGINAL recorder provenance;
require equality with applied.json.updated_provenance (source must not change).
Stop if Ninja requests GN regeneration/hooks/sync or any compile fails.

Only then a separately authorized chrome_public_apk target may use the same
out/Default. No native source changed in A, but linkage/package target remains
necessary; reuse is decided by Ninja/Siso, not guaranteed by this preparation.
Record before/after APK provenance, exit code and unsigned APK hash. Preserve
installed Diagnostic signed APK and its evidence outside generated output.

For an eventual authorized signature: use existing common.sh sign_apk and
preserved existing key in a separately reviewed signing step, source common.sh
with correct SCRIPT_DIR/$0 as in the successful diagnostic signing procedure.
Do not print local.properties/keys/passwords. Write to a fresh A-specific signed
directory, never overwrite baseline distributions. Verify Test package
io.github.nvoid911.versanium.test, version156.0.8078.47, arm64-v8a and certificate
SHA2562e79f4e6597f7ea320b32c4889405c8d93081774a0fd8db4a040def0d54ad120,
then record final APK SHA. Missing/mismatched key or identity stops; no new key.
No Actions upload/Release follows automatically.

A device comparison retains installed zoom. Restart before each planned trial
is an instruction until directly reported by the user. Earlier restart reports
remain user evidence. Capture PiP candidate OFF vs ON separately with diagnosis/
background ON at100%, fullscreen→home vs inline/tab, manual pause and DeX/other
site safety. PiP remains unresolved. B must wait for A logs and a new reviewed
apply/build decision.

## Verification scope

Actual fixed-source A byte reproduction PASS. Temporary fixtures test read-only,
single-file apply/recheck, mismatched/repeated apply rejection, changed source/
provenance rejection and partial-failure retained intent/backup without rollback.
Host validation is mocked in transaction tests; no real saved-host application,
full native/Java compile or new device outcome is established.
