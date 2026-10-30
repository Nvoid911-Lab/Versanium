# A/B Test preparation — 2026-10-24 JST

Coverage correction: f4a2601 host comparison matched provenance but only37/40
selected installed files. Three inherited patch.sh edits were missing from the
fixture. See [reproduction](ab-pipeline-coverage-review.md). The regenerated
manifest retains all40 files in installed/A/B; B native hash/diff now use the
correct inherited baseline. Real-host corrected40/40 comparison remains pending.

Review only: no saved source apply, compile, Actions or release authorization.
Keep current branch history. Product selections refer to exact commits:

| Configuration | Composition | Purpose | Future narrow target |
|---|---|---|---|
| installed |60b00375def663584dfd5c6fd249d25498eeafb2, actual Run9 applied record| Diagnostic APK d01c7633 baseline | Already user-built |
| A | installed product + diagnostics.patch from257b37413ef119e249d9d903b8712af5ba919b7b; retain60b zoom patch | First-blocked reason / entered-then-exited sequence | chrome_java |
| B | A + environment_zoom/chromium.patch from3452edda10007ff1bd5c1727791b1dc489a48d8b | Video fullscreen sizing/restoration comparison after A device logs | actual host_zoom_map_impl.cc and web_contents_impl.cc objects from saved graph |

`check_ab_selection.py` builds three temporary selected pinned156 integration
trees from git archives, never checks out/resets the working branch, and asserts
only controller Java differs installed→A, only the two zoom native files A→B.
Baseline metadata is reproduced using the authenticated actual expiry/candidate
pipeline (dc5…), correcting the historical60b fixture omission. All selected
applied file SHA256 values are in `ab-selection-manifest.json`; review diffs are
generated externally alongside it. This is NOT a complete host provenance record.

## Read-only real-host gate (pending)

Start from the actual four-file diagnostic `applied.json` and
`after-apk-provenance.json`, NOT original pre-update inputs. Require applied=true,
product target60b, original repository7d9102f, pins156/Vanadium, original archive
chain, four post-update hashes and unchanged payload/JNI/metadata. Recompute using
the original recorder and require exact equality with after-apk provenance before
any selection. Existing helper verify-applied is pre-compilation-only and cannot
be reused after APK output changes. Never regenerate the baseline to pass.

Compare installed source files to manifest installed hashes. Capture current GN
args/version, depot/clang toolchain, DEPS, complete tracked-source diff, current
Ninja/Siso graph/state and existing output hashes outside the workspace. Check
current idle runner/process state and capacity; old measurements are historical.
Any source/provenance/graph mismatch stops. Real host record bytes were not
provided in this task, so this gate is NOT established by selected-source PASS.

## Future separately authorized application

A changes only controller Java; B only the two native files listed above. Do not
copy complete scratch trees, rerun patch.sh or use old limited apply helpers.
Prepare exact per-file before/after-byte-checked patches from the manifest and
review diff. Before any future apply, back up each affected whole source outside
the tree with its hash, save intent/provenance and current generated-output
hashes. After apply require exact configuration hashes, unchanged all other
selected inputs and generated output bytes, then record a new full source diff
and original-recorder provenance. Original repo HEAD remains7d; link the selected
commits, manifest hash and full source-diff hash to avoid mislabeling it as a full
checkout of the controller. Partial writes stop without automatic rollback/reset.

A requires real chrome_java integration then a separately authorized APK link/
package. After A device evidence, preserve its signed APK and complete evidence;
B starts by rechecking A post-build provenance and manifest A hashes, then the
two actual graph-derived native objects, then separately authorized APK. Record
new after-build provenance, logs/exit statuses and APK SHA. Staging should use
distinct A/B directories with same Test package/version/key and descriptive
filenames. Existing outputs may be updated by compilation, not deleted or moved;
no reuse/time guarantee is implied. Signing remains the existing reviewed path.

Stop for missing records, unsafe path, pre/post hash drift, dirty build input,
wrong toolchain/pins/Test identity, absent/duplicate object edge, failed narrow
target, changed JNI/GN/payload, requested regeneration/sync, or key/package
mismatch. Do not weaken either historical apply controller. No apply-ready host
automation or actual host preflight is claimed here; host evidence review and
exact per-file application remain prerequisites before a future apply.

## Device comparison and restart evidence

A first: match installed Diagnostic APK, phone/YouTube100%, diagnosis/background
ON, compare PiP candidate OFF then ON. Record first failed branch vs confirmed
entry/exit separately, fullscreen/home vs tab switch/inline-home, manual pause
and no crash. Then B repeats those conditions and below/equal/above100% video
fullscreen/exit, rotation and mobile↔DeX, saved values/exports and other sites.
Do not call PiP fixed or video sizing verified before device evidence.

Previous two-condition restart is directly user-reported in the supplied chat.
Restart before future A/B trials is an instruction only until the user reports
its completion; never mark planned steps as performed.

Selected source A and B integration PASS; A actual branch Java with doubles15
and B rendering decision MODEL67 PASS. No new real Chromium compile/device result.
