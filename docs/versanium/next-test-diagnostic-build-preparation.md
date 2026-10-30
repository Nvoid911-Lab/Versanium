# Next Test diagnostic correction: preserved Run9 preparation

Date: 2026-10-24 JST. This is a reviewed preparation for target source commit
`60b00375def663584dfd5c6fd249d25498eeafb2`. It does not authorize or record a
source apply, compilation, signing, Actions run, merge, tag, or Release.

## Purpose and current evidence

The next Test APK has two purposes only:

1. verify that the diagnostics-only startup/playback crash loop is no longer
   reachable through the identified unsafe fullscreen-permission probe; and
2. collect the order of existing PiP controller stages when mobile PiP appears
   briefly and closes.

It must not be described as a PiP fix. The background candidate's reported
tab-playback improvement is preserved byte-for-byte. The new code does not
change PiP exit, Activity stop/resume, MediaSession suspension, fullscreen
requirements, autoplay, or play/pause behavior.

User evidence establishes that the preserved Run9 tree already completed the
logged RFH object, `chrome_public_apk`, existing-key signing, and S23 install for
the earlier code. Original Run39951209951 remains failure. See
`156-device-diagnostics-review.md` for exact APK hashes and device results.

## Exact source delta and generated integration boundary

Applying pinned Chromium156 plus selected Vanadium/F11/zoom/PiP inputs at
controller ebfc81c and target60b0037 produced an exact comparison. Only these
four applied Chromium files differ:

| Applied source | Before SHA256 | Target SHA256 | Required validation |
|---|---|---|---|
| `chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java` | `ec5d0045...f91cb88` | `a75358c2...6daa65` | `chrome_java` |
| `chrome/android/java/src/org/chromium/chrome/browser/tab/TabImpl.java` | `c9db6e69...3a9074` | `10f9dd82...2f2e4` | `chrome_java` |
| `content/browser/renderer_host/render_frame_host_impl.cc` | `dc1cd0a4...8feedf9` | `48315bb8...6e3ff4` | exact saved RFH object |
| `chrome/browser/about_flags.cc` | `b12f0b78...4000fca` | `ff15f1be...9acde1` | main-toolchain object discovered from saved graph |

The helper contains and verifies the complete hashes; abbreviations above are
for readability. Its exact transformations reproduce the selected target tree
and reject an already-applied or drifted source.

These integration inputs are byte-identical before/after and are pinned by the
helper: fixed JS UTF-16 header, WebContents JNI C++/Java interface and
implementation, `content/browser/BUILD.gn`, generated final flag metadata, and
public WebContents API. Therefore no JNI signature or GN source-list change is
part of 60b0037. GN regeneration, JNI regeneration as a manually requested target,
and patch.sh reapplication are not preparation steps. `chrome_java` is still
required because two actual Java consumers changed. The two actual C++ objects
must compile before the APK target. `chrome_public_apk` is the later link/package
integration gate.

### Corrected flag-metadata provenance

The first real-host read-only preflight at controller b401856 stopped before
source mutation/compilation because its expected flag-metadata hash was wrong.
Evidence directory:
`/home/takuma/versanium/diagnostic-preflight-b401856-A0I5mG`.
Expected was `293f70fc...4556d`; saved reality was
`dc5a9275...b88b`. The user compared HEAD to the saved file and found only the
11 patch.sh expiry overrides plus the three Versanium flags.

The error was in this preparation's selected-source fixture. It applied the
three candidate records but omitted patch.sh lines36–38. Thus `293f...` is the
fixed HEAD plus only three candidate records—an intermediate state that never
represented the completed Run9 pipeline. It is no longer an allowed hash.

`tools/versanium/flag_metadata_pipeline.py` now reproduces the real order while
preserving every unrelated byte:

1. fixed saved Chromium HEAD: `c1550b2a...c271`;
2. exact ordered11 numeric expiry replacements from target60b patch.sh:
   `47fce4ac...556d`;
3. exact three-record insertion order/format from target60b
   apply_youtube_candidates.py: `dc5a9275...b88b`.

The final reproduced SHA256 exactly equals the user-reported saved-file SHA256.
The actual saved bytes were not uploaded here, so the evidence is an exact
pipeline reproduction plus SHA256 equality, not an independent byte-for-byte
`cmp` performed by this cloud. The next host preflight compares the saved bytes
directly against the reproduced bytes, rather than adding its hash to an
allowlist. Any patch.sh flag-list, HEAD input, intermediate hash, insertion
format, final hash, or direct byte mismatch stops.

## New helper and old-helper boundary

`tools/versanium/prepare_diagnostic_update.py` is independent of
`prepare_run9.py`. The old three-`host()` helper and its tests are unchanged and
remain pinned to their historical controller. They are not relaxed or reused
for this wider four-file update.

The new helper checks, before any source write:

- exact saved Run9 workspace/repository HEAD7d9102f and a separate clean
  controller descending from target60b0037;
- exact original provenance ZIP digest and original Chromium/Vanadium/version;
- prior ebfc81c applied evidence linking the original baseline and corrected RFH
  hash;
- a saved post-object/pre-APK provenance record, recomputed now with the
  original recorder; every field except the expected tracked-source-diff must
  equal the original baseline;
- preserved GN version/args, arm64 Versanium Test identity, depot_tools commit
  and tracked cleanliness, clang/clang++ hash, output directory and required
  Ninja/Siso state;
- all four pre-update source hashes and seven unchanged JNI/GN/payload hashes;
- fixed HEAD flag metadata, exact patch.sh 11-name list, expiry-only intermediate
  hash, final three-record generation hash, and direct final-byte equality;
- exact RFH object from the Run9 log, the main-toolchain `about_flags.cc` C++
  object derived from the saved byte-parsed Ninja graph, and exactly one
  `chrome_java` graph target.

It records current `.ninja`, args and available Ninja/Siso state hashes. Default
preflight writes only a new JSON outside the workspace. A future explicit
`--apply` stores four full source backups outside the workspace, records intent,
writes only those four files, confirms exact target hashes, recomputes
provenance, and requires all generated-output hashes to remain unchanged. It
never compiles. Partial I/O failure is a STOP with evidence/backups retained;
do not reset or automatically roll back.

## Read-only host preflight — next allowed step

Use the same account/distro and canonical saved paths. The controller must be a
separate clean checkout at the reviewed current PR head; do not update code
inside `RUN9_WORKSPACE`. Use an existing post-correction provenance JSON whose
contents were recorded after the RFH correction (`before-apk-provenance.json` or
the independently compared `after-object-provenance.json`). Never synthesize a
replacement record merely to pass validation.

```sh
RUN9_WORKSPACE='/home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951'
RUN9_CONTROL='/absolute/separate/reviewed-current-pr5-controller'
RUN9_ORIGINAL_ZIP='/mnt/c/Users/Nvoid/Downloads/Versanium-build-provenance.zip'
RUN9_PRIOR_EVIDENCE='/home/takuma/versanium/run9-evidence-sknAKy/preflight-ebfc81-eLIR96/applied.json'
RUN9_CURRENT_PROVENANCE='/home/takuma/versanium/run9-evidence-sknAKy/preflight-ebfc81-eLIR96/before-apk-provenance.json'
RUN9_NEXT_EVIDENCE='/absolute/new/evidence-diagnostic-update'

mkdir -p "$RUN9_NEXT_EVIDENCE"
git -C "$RUN9_CONTROL" status --short
git -C "$RUN9_CONTROL" rev-parse HEAD
sha256sum "$RUN9_ORIGINAL_ZIP" "$RUN9_CURRENT_PROVENANCE"

python3 "$RUN9_CONTROL/tools/versanium/prepare_diagnostic_update.py" \
  --workspace "$RUN9_WORKSPACE" \
  --control "$RUN9_CONTROL" \
  --provenance-zip "$RUN9_ORIGINAL_ZIP" \
  --prior-evidence "$RUN9_PRIOR_EVIDENCE" \
  --current-provenance "$RUN9_CURRENT_PROVENANCE" \
  --evidence "$RUN9_NEXT_EVIDENCE/read-only-preflight.json"
```

This work has **not** run that command on the real host. Success must say
`READ-ONLY ... PASS`, list RFH/about_flags/chrome_java targets, and leave saved
source/output unchanged. A new evidence filename is required for every retry.

## Future apply and pre-compile verification — not authorized now

Only after reviewing the real read-only evidence and separately authorizing an
apply, use a fresh evidence name and explicit `--apply`:

```sh
python3 "$RUN9_CONTROL/tools/versanium/prepare_diagnostic_update.py" \
  --workspace "$RUN9_WORKSPACE" \
  --control "$RUN9_CONTROL" \
  --provenance-zip "$RUN9_ORIGINAL_ZIP" \
  --prior-evidence "$RUN9_PRIOR_EVIDENCE" \
  --current-provenance "$RUN9_CURRENT_PROVENANCE" \
  --evidence "$RUN9_NEXT_EVIDENCE/applied.json" \
  --apply

python3 "$RUN9_CONTROL/tools/versanium/prepare_diagnostic_update.py" \
  --workspace "$RUN9_WORKSPACE" \
  --control "$RUN9_CONTROL" \
  --provenance-zip "$RUN9_ORIGINAL_ZIP" \
  --prior-evidence "$RUN9_PRIOR_EVIDENCE" \
  --evidence "$RUN9_NEXT_EVIDENCE/applied.json" \
  --verify-applied
```

The recheck is intentionally before compilation. Normal Ninja/Siso state changes
after a compiler runs make that pre-compile state check historical; do not relax
it or overwrite evidence.

## Required future integration compile order — not run or authorized now

After a separately authorized apply and successful `--verify-applied`, read the
three targets from `applied.json`. In an idle maintenance window, retain the same
source/out/depot_tools and `DEPOT_TOOLS_UPDATE=0`. Request the narrow gates in
this order, with new non-overwriting logs and exit-code files:

1. `chrome_java` — actual Chromium Java/NullAway integration for controller and
   TabImpl. Stop on any Java/API/lifecycle typing failure.
2. the recorded RFH object and recorded about_flags object, preferably one
   requested target at a time with `-j 1`. Stop on any compile, generated-header,
   include or toolchain failure.
3. recompute provenance with the original recorder. It must equal the applied
   evidence's post-update provenance; compilation may change outputs, not source,
   GN args, pins, repository/depot/toolchain or source-diff hash.
4. only after all three narrow gates pass and a separate build authorization,
   run `chrome_public_apk` from the same output. Ninja/Siso decides invalidation;
   preserved files do not guarantee cache reuse, step count, duration, success,
   or free-space sufficiency.
5. verify the unsigned APK package/version/ABI and hash, then use the separately
   reviewed existing Test signing/staging path. Do not regenerate a key, expose
   secrets, publish a Release, or treat local compilation as an Actions success.

If Ninja reports that GN regeneration, hooks, dependency sync, or a different
toolchain is required, STOP before accepting it. Review why the supposedly
unchanged BUILD.gn/args/graph became invalid. Do not run `gn gen`, `gclient`,
`patch.sh`, `build.sh`, clean/reset, or move/delete the tree as a workaround.

## Stop conditions

Stop without applying/compiling if any exact archive/evidence/provenance/source
hash differs; controller is dirty or carries post60b build-input changes; target
pin/ancestry, patched Chromium/depot/GN/args/Test identity/toolchain differs;
unchanged JNI/GN/payload bytes differ; a required output-state file is missing;
native edges are absent/duplicate/wrong-rule/wrong-source; `chrome_java` is not a
single saved target; an evidence/backup/log path already exists; or a builder is
active.

After a future apply, stop on partial write, output hash movement, unexpected
source/provenance difference, failed narrow target, requested regeneration, or
package/signature mismatch. Retain evidence and state for review. Do not call
PiP fixed based on compilation: device acceptance must first show diagnosis no
longer loops, then separately capture stage order for the brief PiP exit while
preserving manual stop, DeX, Twitch/private and background tab playback.

## Validation performed in this preparation

- Exact selected pinned156 old→target transformation of all four files: PASS.
- Full flag-metadata pipeline from fixed HEAD through ordered11 expiry changes and
  exact three candidate insertions: final `dc5a9275...b88b` PASS. This matches
  the reported real file hash; cloud-side direct `cmp` against host bytes was not
  possible. The former `293f...` candidate-only fixture is identified/rejected.
- Repeated application, unrelated source drift, wrong/duplicate native edges,
  implicit-only source, other toolchain and duplicate chrome_java tests: PASS.
- Seven unchanged generated/JNI/GN/payload inputs: exact SHA256 PASS.
- Existing source integration now includes the real expiry-before-candidate
  order; passive logger9 Java-double cases, native scope17
  MODEL cases, DOM37 MODEL cases, migration/recovery39 and the new preparation
  tests: PASS locally. Models/doubles are not Chromium or device integration.
- actionlint, YAML/inline shell, bash/documented command syntax and diff checks:
  PASS. No real host preflight, source apply, compilation, signing or device test.
