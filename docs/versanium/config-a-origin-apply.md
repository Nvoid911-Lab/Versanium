# A plus fullscreen-origin diagnosis — execution preparation

2026-10-24 JST. Configuration A on the real host is already applied, built and
signed. Its `applied.json.updated_provenance`, `after-apk-provenance.json` and
current inputs are the baseline. The installed60b/pre-A state is rejected.
This preparation does not authorize or perform saved-tree writes, compile,
Actions or B application.

## Pinned product selection and manifest

`config-a-origin-manifest.json` has two41-file maps: A and AOrigin. The existing
A40 are retained, plus the original FullscreenHtmlApiHandlerBase. The other39
A files, including both native zoom files, are identical before/after. Only:

| File | A SHA256 | AOrigin SHA256 |
|---|---|---|
| PiP controller Java |5e485b0002d6d78b05e8ebb2c24e9f9b61406bc4833ba925528a02a62ef592a4|ad3efea4a6b741de0816240ac87c4f0784dd4b1fb77c396be9ad67f4822366b7|
| FullscreenHtmlApiHandlerBase.java |f14c40e9046171345d2db39ba8c32c7317a3ebe5652cbf78e6f8e2d43e0c2926|ec1fcc104a40232af1fea47b59e0998571ec51c0c53bc91734d454394a9c3218|

The new independent `prepare_config_a_origin.py` reconstructs both from saved
fixed Chromium HEAD in scratch. It applies257b diagnostic patch to reproduce A
controller, then reconstructs with5faa diagnostic patch and exact5faa Base
transform to reproduce AOrigin. All before/after bytes must match the manifest.
The original A manifest and all prior apply helpers are unchanged. Utility-only
functions from prepare_config_a are reused, never its validation/apply paths.

Preflight requires a clean separate controller descending from5faa, exact
selection manifest, original Run9 repo HEAD, preserved paths, completed A record,
after-APK equality, original-recorder/current provenance equality, fixed pins,
arm64 Test identity, GN/clang/depot and all41 source hashes. It records existing
out/Default files byte hashes (including APKs/Ninja/Siso; symlink targets are
recorded), tool binary hashes and all other tracked source diff. This can involve
large reads; use an idle host and current capacity information, not historic ETA.

Explicit --apply records both external original-source backups, intent and full
preflight evidence before writing. Each source still must equal its original
bytes immediately before its write. Post-check requires AOrigin41, other source
diff/tool/provenance fields and generated output unchanged. Only the new complete
source diff is admitted into updated_provenance. Any partial failure leaves
applied=false intent, backups and current source for review; never auto rollback,
reset or retry an ambiguous partial state. --verify is read-only before compile,
requiring the same controller/evidence inputs, paths, selection and output state.

## Copyable read-only command

First update ONLY the separate controller to this PR's final reviewed preparation
SHA. Do not checkout/pull inside the saved Run9 workspace. Keep the same shell
variables for later separately authorized steps. No secret/key/config content is
printed. Use a new evidence directory, never overwrite prior evidence.

```sh
RUN9_WORKSPACE='/home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951'
RUN9_CONTROL='/home/takuma/versanium/run9-control-093f787-3k3yO1'
RUN9_A_BASE='/home/takuma/versanium/config-a-evidence-SaxHs9'
RUN9_ORIGIN_EVIDENCE=$(mktemp -d /home/takuma/versanium/config-a-origin-evidence-XXXXXX)
git -C "$RUN9_CONTROL" rev-parse HEAD
python3 "$RUN9_CONTROL/tools/versanium/prepare_config_a_origin.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --a-applied "$RUN9_A_BASE/applied.json" \
  --after-apk "$RUN9_A_BASE/after-apk-provenance.json" \
  --evidence "$RUN9_ORIGIN_EVIDENCE/read-only.json"
```

The manifest A41 host match has NOT been run here. Existing A40 host success
does not independently verify the new Base41st input. A mismatch is a STOP for
reproduction/review, never a reason to drop an input or accept an observed hash.

## Future explicit apply and pre-compile recheck — not executed/authorized here

```sh
python3 "$RUN9_CONTROL/tools/versanium/prepare_config_a_origin.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --a-applied "$RUN9_A_BASE/applied.json" \
  --after-apk "$RUN9_A_BASE/after-apk-provenance.json" \
  --evidence "$RUN9_ORIGIN_EVIDENCE/applied.json" --apply
python3 "$RUN9_CONTROL/tools/versanium/prepare_config_a_origin.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --a-applied "$RUN9_A_BASE/applied.json" \
  --after-apk "$RUN9_A_BASE/after-apk-provenance.json" \
  --evidence "$RUN9_ORIGIN_EVIDENCE/applied.json" --verify
```

Never repeat --apply on a completed/partial application. Reject wrong A record,
installed60b input, A41 mismatch, repeated application, modified manifest,
unexpected controller delta, missing output state, concurrent builder/process
check failure, changed tools/other inputs or any post-check failure. Process
checks cannot prevent another runner starting later: schedule an idle window.

## Later real chrome_java/NullAway → APK → existing signature

Both modified classes are existing sources of //chrome/android:chrome_java; no
new GN source list/dependency/resource/JNI change. Full Java integration remains
necessary for nullable event tabs and the Base→controller bridge. Later, only
after explicit build authorization and successful apply/recheck:

1. With the existing source/out/depot and DEPOT_TOOLS_UPDATE=0, run the real
   `autoninja -C out/Default -j 6 chrome_java`. Keep pipefail, a new log and exit
   status under origin evidence. This is the actual Java/NullAway gate, not the
   bounded Java doubles already tested. Recompute original recorder provenance
   and require equality with applied.json.updated_provenance. Stop on errors or
   any requested GN regeneration/hooks/sync/toolchain/input change.
2. Only after success and separate APK authorization, run the same output's
   `chrome_public_apk`, retaining new before/after provenance, logs and exit code.
   The source must still be AOrigin41 with installed A zoom, never B. Old --verify
   expects precompile output and is NOT used after compilation; compare source
   hashes and updated provenance instead. Existing out APK can be replaced by
   compilation, so preserve all earlier signed APKs/evidence externally.
3. Before an eventual separately authorized signature, validate unsigned
   io.github.nvoid911.versanium.test /156.0.8078.47 /arm64-v8a and hash. Use the
   existing reviewed common.sh sign_apk flow and existing key only. Correct
   SCRIPT_DIR/$0 handling is required as in successful A signing. Do not print
   keys/local.properties/passwords or recreate signing material.
4. Stage a fresh `signed-test/Versanium-156.0.8078.47_Test_ConfigAOrigin.apk`
   under the NEW origin evidence. Never overwrite ConfigA or previous Diagnostic
   distribution. Verify with existing apksigner; require certificate SHA256
   2e79f4e6597f7ea320b32c4889405c8d93081774a0fd8db4a040def0d54ad120,
   package/version/ABI and new final SHA256, and verify a copied file's hash.
   No automatic upload, Actions result change or Release follows.

The helper does not execute any of these commands/signing operations. Input
hashes, graph state and idle/capacity evidence must be reviewed again before a
future actual build. Neither output retention nor past elapsed times guarantees
reuse/completion. B remains a separate decision AFTER origin A logs.

## Device plan and evidence limits

On the future reviewed APK, first check safe normal launch. Compare known① PiP
candidate OFF and② ON separately, diagnosis/background ON, phone YouTube100%,
fullscreen→home distinct from inline→home/tab switch. Restart before each trial
is an instruction until the user directly reports completion. Current A log posts
did not re-report all instructed conditions; different PIDs alone do not prove
every step. Preserve manual pause, DeX/Twitch/private/other-site behavior.

Collect only cr_VersaniumPiP/VersaniumPiP fixed stage records from before the
first origin6 label to dismiss/actual move/suspend/framework exit. Match local
request labels with accepted/persistent-exit/observer dispatch labels. A
multiwindow guard-passed label proves that actual branch; callback alone does
not. Same-tab/normal/HTTPS/YouTube/null/teardown filters can suppress records:
absence is NOT event absence. No broad logs, settings dumps, URL/title/auth data
or stack are needed. The first external/native caller can still remain unknown
even with local labels; do not assert PiP fixed or ignore all fullscreen exits.

## Local validation

Manifest retains A40 plus Base41 and differs in exactly two files; fixed-source
reconstruction PASS. Fixture transactions cover read-only, apply/recheck,
wrong/repeated state, installed60b rejection, and second-write partial failure
with original backups/intent retained and no rollback. Host validation is mocked
in transaction fixtures. Real saved-host preflight/apply/Java/NullAway/APK and
new device outcome are NOT established here.
