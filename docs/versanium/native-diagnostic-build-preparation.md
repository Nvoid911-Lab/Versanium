# Native diagnosis: source / graph / compilation gates — 2026-10-25 JST

Preparation only. No saved-host source apply, GN generation, compiler, Actions,
B, reset/clean/sync, merge, Release or tag is executed here.

## Baseline and independent tools

Built/signed Forward evidence:
`/home/takuma/versanium/config-a-origin-forward-evidence-lnxJen`.
Require applied.json configuration AOriginForward/applied=true, its
updated_provenance == after-apk-provenance.json == current original build
recorder. Distribution APK must have SHA256
0264aec79e1389a9165b639e0ce62a92f62818f6d3514b26c34f86017998bce1.
This verifies the supplied distribution file, not a fresh extraction from device.
Do not use A/AOrigin/installed evidence as before state.

New prepare_native_diagnostic.py imports NO historical apply/preflight helper.
It uses only pinned product transform plus the original saved build provenance
recorder/validator (byte-compared with Run9 commit). Existing helpers unchanged.
Pin product16eca84, Chromium1d17a2e, Vanadium2ae4335, saved repo7d9102f.
Exact50/51 manifest retained; Forward43 unchanged, seven additional existing
inputs checked, new scope header must not exist (even as a broken symlink).
Reconstruct seven originals from saved fixed source HEAD in temporary scratch,
compare before hashes, apply exact pinned native product transform and compare
eight after hashes. No observed-file substitution/hash exceptions.

Source preflight also checks canonical paths, clean separate controller/allowed
delta, original pins/ancestry, original recorder/current provenance, args.gn,
GN/clang/clang++/depot, arm64 Test identity and component_build=false.
GN/clang binary hashes must equal Forward applied.tools, not just version strings.
Pin original common.sh/identity configuration source; no keys, local.properties or Secret
values are inspected. Inventory every output file's bytes/mode/size/mtime and symlink target,
including existing graph/Ninja/Siso/APKs. This may be I/O-heavy; no reuse/ETA promise.

## First command: read-only

Update ONLY the separate controller to this preparation's reviewed final SHA.
Do not git pull/checkout inside saved Run9. The APK path below is the previously
specified distribution location: if absent, STOP and supply the actual preserved
Forward APK path; do not substitute another APK or weaken the required hash.

```sh
RUN9_WORKSPACE='/home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951'
RUN9_CONTROL='/home/takuma/versanium/run9-control-093f787-3k3yO1'
RUN9_FORWARD_BASE='/home/takuma/versanium/config-a-origin-forward-evidence-lnxJen'
RUN9_FORWARD_APK="$RUN9_FORWARD_BASE/signed-test/Versanium-156.0.8078.47_Test_ConfigAOriginForward.apk"
RUN9_NATIVE_EVIDENCE=$(mktemp -d /home/takuma/versanium/native-diagnostic-evidence-XXXXXX)
python3 "$RUN9_CONTROL/tools/versanium/prepare_native_diagnostic.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --forward-applied "$RUN9_FORWARD_BASE/applied.json" \
  --after-apk "$RUN9_FORWARD_BASE/after-apk-provenance.json" \
  --forward-apk "$RUN9_FORWARD_APK" \
  --evidence "$RUN9_NATIVE_EVIDENCE/read-only.json"
```

No real-host50 preflight has been run here. The new evidence directory alone is
written. Failure means STOP/review, never drop a file/check or switch baseline.

## Future stage1: explicit source-only apply / verify (not authorized now)

Use the SAME command above with a NEW evidence filename `source-applied.json`
and `--apply-source`. Afterwards repeat that filename with `--verify-source`.
No command here runs GN. Active Runner.Worker/clang++/ninja/siso/gn or failed
process check refuses apply. Schedule idle host; checks cannot lock out a later
runner launch. Review `df -h` on source/output/evidence volumes first.

Before source writes, save seven originals externally plus header-absence intent,
baseline/APK evidence hashes, provenance, all output inventory and tool/config
hashes. Backup existing graph **bytes**, not just hashes: args.gn, every .ninja,
.ninja.d, build.ninja.stamp when present, .ninja_log/.ninja_deps and .siso* state
(including files within such directories). Remaining generated outputs stay
in place with full before inventory, never clean/move them. Source backups and
graph backups are under source-applied.before/source and /output.

Each original is compared immediately before its write; header uses exclusive
creation. Postcheck51/other source diff/tool/config/provenance/output invariant;
record phase SOURCE_ONLY_GRAPH_UNCHANGED only on complete success. Partial
failure keeps source_applied=false intent, backups and actual partial tree.
No automatic rollback/reapply. Verify is BEFORE GN/compile and intentionally
rejects any changed output; do not use it after graph regeneration.

## Is GN generation necessary? Yes

Fixed product modifies chrome/browser/ui/exclusive_access/BUILD.gn to register
the new scope header. That GN file belongs to the already-used exclusive_access
target. Existing graph is generated from the old BUILD.gn; adding header alone
may leave object command bytes identical, but does not make the graph provenance
current. Fixed build.sh line93 explicitly uses `gn gen out/Default` before compile.
Ninja regeneration dependencies cover loaded GN inputs. Do not rely on autoninja
to silently regenerate; source-only completion does not authorize compilation.

## Future stage2: separately reviewed graph generation

Requires completed source-only verify, full external graph backups, idle/capacity
review and explicit authorization lifting the current no-GN condition. Use the
SAME source/output, saved GN binary/version2578 (510ec7992c30), args.gn and frozen
depot. Do not copy repository args over saved args, change --args, toolchains,
Siso settings, hooks or dependencies. Exact command from chromium/src:

```sh
RUN9_SOURCE="$RUN9_WORKSPACE/chromium/src"
export DEPOT_TOOLS_UPDATE=0
export PATH="$RUN9_SOURCE/buildtools/linux64:$RUN9_WORKSPACE/depot_tools:$PATH"
(
  cd "$RUN9_SOURCE" || exit 1
  if (set -o noclobber; "$RUN9_SOURCE/buildtools/linux64/gn" gen out/Default > "$RUN9_NATIVE_EVIDENCE/gn-gen.log" 2>&1); then
    printf '0\n' > "$RUN9_NATIVE_EVIDENCE/gn-gen.status"
  else
    RUN9_GN_STATUS=$?
    printf '%s\n' "$RUN9_GN_STATUS" > "$RUN9_NATIVE_EVIDENCE/gn-gen.status"
    exit "$RUN9_GN_STATUS"
  fi
)
```

This command is documentation, NOT executed. Preserve log/exit status externally;
nonzero status, download/hooks/toolchain request or implicit source change is STOP.
Direct GN gen builds no C++/Java objects, but runs GN scripts: do not run it during
read-only preflight. Never replace the preserved graph with another output tree.

After success collect full JSON descriptions with the SAME GN, cwd and args:

```sh
(
  cd "$RUN9_SOURCE" || exit 1
  "$RUN9_SOURCE/buildtools/linux64/gn" desc out/Default '//chrome/browser/ui/exclusive_access:exclusive_access' --format=json > "$RUN9_NATIVE_EVIDENCE/common-target.json" || exit 1
  "$RUN9_SOURCE/buildtools/linux64/gn" desc out/Default '//chrome/browser/ui/android/exclusive_access:exclusive_access' --format=json > "$RUN9_NATIVE_EVIDENCE/android-target.json" || exit 1
)
```

Read the `toolchain` field from both actual descriptions; require same default
toolchain and set RUN9_TOOLCHAIN to that exact value. Never invent it. Missing or
ambiguous metadata is STOP. Then invoke new read-only audit_native_graph.py with
the same workspace/control/forward-applied/after-apk/forward-apk arguments plus:

```sh
python3 "$RUN9_CONTROL/tools/versanium/audit_native_graph.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --forward-applied "$RUN9_FORWARD_BASE/applied.json" \
  --after-apk "$RUN9_FORWARD_BASE/after-apk-provenance.json" \
  --forward-apk "$RUN9_FORWARD_APK" \
  --source-record "$RUN9_NATIVE_EVIDENCE/source-applied.json" \
  --gn-log "$RUN9_NATIVE_EVIDENCE/gn-gen.log" \
  --gn-status "$RUN9_NATIVE_EVIDENCE/gn-gen.status" \
  --gn-desc "$RUN9_NATIVE_EVIDENCE/common-target.json" \
  --gn-desc "$RUN9_NATIVE_EVIDENCE/android-target.json" \
  --toolchain "$RUN9_TOOLCHAIN" \
  --evidence "$RUN9_NATIVE_EVIDENCE/graph-audited.json"
```

The audit never regenerates GN or compiles. It requires51 source hashes,
source-applied provenance/controller/baseline, other source diff, tools/config,
args.gn and ALL non-graph generated bytes unchanged. Only .ninja/.ninja.d/
build.ninja.stamp differences are admitted and recorded. New/changed generated
headers, objects, jars/APKs, Ninja/Siso histories or unexpected GN logs cause
STOP/review; do not broaden the allowlist from observed output. Original graph
backup remains immutable. mtime-only rewrites are not claimed as byte changes.

Ninja parsing traverses only loaded build.ninja include/subninja graph, as bytes
with continuation support, not UTF-8 lossy decode. It identifies default obj/
cxx object edges by exact resolved source path, then matches GN target/source/
toolchain metadata. Other toolchain copies are not mistaken for ambiguity.
Duplicate output, absent/duplicate source edge, unexpected rule, unresolved
include or missing metadata refuses success. Actual source/rule/toolchain/Ninja
filename/target and loaded graph hashes are saved, not guessed object names.
The three object edge identities must also match the preserved old graph
(relative source paths resolved against original out, not backup directory).
New graph bytes are copied externally. Before compile, review ALL old/new graph
diffs against source-applied.before/output and graph-audited.graphs; unexplained
flags/rules/commands/targets/toolchain changes are STOP even if technical audit
passes. Audit success is not blanket approval of generated command semantics.

## Future stage3: compile gates, no execution now

|Order|Required GN target / source|Selection and check|
|---|---|---|
|1|//chrome/android:chrome_jni_headers|Generate new ExclusiveAccessContext JNI. Derive the build output/alias from actual GN outputs/Ninja graph; do not assume an unverified short alias. Confirm actual WebContents/II→void signature.|
|2|//chrome/android:chrome_java (existing chrome_java alias)|Real Java/NullAway integration, not fragment tests. Stop on errors.|
|3|Android exclusive_access target: exclusive_access_context_android.cc, exclusive_access_manager_android.cc|Use only graph-audited exact object targets; compile those first to catch JNI/API/include failures.|
|4|Common exclusive_access target: fullscreen_controller.cc|Use graph-audited exact object; verify new virtual hook, WeakPtr/TLS/header integration.|
|5|chrome_public_apk|Only after above success, same out/Default; graph may rebuild transitive users of the interface. No reuse/time guarantee.|
|6|Existing key signing|Unchanged reviewed common.sh flow, same Test identity/certificate, new external Test_ConfigAOriginForwardNative APK name; preserve Forward/AOrigin/A/Diagnostic distributions.|

Use saved autoninja/depot with DEPOT_TOOLS_UPDATE=0; target arguments must come
from audited metadata. Retain new log/status/provenance and51 source hashes at
every stage. After compilation outputs are expected to change; precompile
verify/audit output snapshots are not postcompile success checks. Original
recorder inputs/source diff must still equal source-applied updated_provenance;
record new generated-output inventories instead. Stop on implicit GN rerun,
source/toolchain/args/config drift, missing metadata, unexpected target expansion
or failure. No patch.sh, build.sh, clean/reset/sync or tree movement.

Sign only after checking unsigned Test package/version156.0.8078.47/arm64-v8a.
Use unchanged existing key; apksigner certificate must remain
2e79f4e6597f7ea320b32c4889405c8d93081774a0fd8db4a040def0d54ad120.
No Secrets/key values are logged/read by preparation. No upload/Release follows.

Native diagnosis clarifies observed EAM entry/branch/synchronous nesting only;
initial content renderer/browser/security requester remains unknown. It is NOT
a PiP fix. B remains separate and unselected. Model/fixture/JNI generation are
not actual Java/NullAway/native integration compilation or real-host evidence.

Local validation:77 tests PASS (5 new), including fixed source reconstruction,
read/apply/verify fixtures, wrong baseline/APK, header already present/repeated
apply, partial write and output drift with no rollback. Loaded binary Ninja /
multi-toolchain/duplicate fixtures and post-GN non-graph rejection PASS.
Transaction host validation is mocked in those fixtures. actionlint, documented
shell syntax and diff PASS; real host50 check/GN metadata/graph/compile unverified.
