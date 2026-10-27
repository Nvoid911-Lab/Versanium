# Cleanup result — 2026-10-28 JST

Start HEAD / confirmed Primary PR5 head: `3150c48958575934c17d8ce5de4c430f658d5b9c`.
Local `primary-docs` checkout was clean on next-test/156-zoom-transfer-pip.
PR5 Draft/Open/unmerged; body unchanged. No drift found before editing or final review.

Removed 34 dedicated candidate files: 5 generators/transforms, 3 payload/patch
inputs, 6 candidate tests, 10 apply/selection/recovery tools, 10 dedicated Python
tests. Generated TabImpl hooks, WebContents/JNI/renderer bridge, chrome://flags,
fullscreen diagnostic scope/observer plumbing are no longer emitted. There are
no generated Chromium files tracked here: saved source and APKs remain untouched.
The only shared executable edits are one patch.sh invocation deletion and three
candidate-only provenance recorder lines. No other patch operation changed.

126 protected pre-existing files match before.json hashes, including every Zoom
file, all old docs/evidence/manifests/logs, branding/resources, pins, workflows,
build inputs and identity. F11 embedded code and the context-menu shard2 fix are
unchanged. The four source-of-truth documents retain all historical text and add
a retired/superseded boundary; DECISIONS is append-only. README also gains that
boundary. Historical audit reports and commit history are retained.

Static checks PASS: planned deletions, protected hashes, exact patch/provenance
diff, no executable references to deleted tooling, no old runtime flags/hooks,
28 remaining Python ASTs, Bash5.2 patch.sh syntax (bundled sh.exe), F11 embedded
Python syntax, diff whitespace. Existing revision-gate test: 5 model cases PASS.
Context-menu short-circuit and selected-command coverage tests PASS; unavailable
fixed-source/fixture cases skipped (3 test skips and 8 test/subtest skips).
Migration/resume suites unavailable because PyYAML is absent. JVM Zoom tests
unrun: JDK not available. No dependency installation or browser build performed.

Existing real-asset checker initially FAILS on two CRLF XML worktree files.
Both were identical before cleanup, and their committed LF blobs match the
asset ledger. No branding fix or line-ending rewrite is included.

Residual references are intentional: historical docs, manifests, logs, the new
inventory; fixed-source trace/JNI historical evidence verification utilities;
and the preserved Zoom comment/listener/display APIs. No remaining candidate
caller registers the listener. All Zoom bytes and tests remain unchanged.
Inherited Chromium/Titanium general media/PiP policy is untouched.

No Brave implementation, build, GN, Actions dispatch, APK, merge, release, tag
or Production operation. Workflows are workflow_dispatch only, so normal push
does not schedule a push/PR workflow. PR body is not edited.

Next state: `READY_FOR_BRAVE_36838_33522_39765_READONLY_PORT_ANALYSIS`.
This is a source cleanup checkpoint, not a build or device-success claim.
Project Sources snapshots and Notion are not updated by this repository commit.

## Changed existing files

- `ARCHITECTURE.md`
- `DECISIONS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `RULES.md`
- `patch.sh`
- `tools/versanium/write_build_provenance.py`

## Deleted existing files

- `tools/apply_content_fullscreen_origin.py`
- `tools/apply_fullscreen_delegate_origin.py`
- `tools/apply_fullscreen_native_origin.py`
- `tools/apply_fullscreen_origin.py`
- `tools/apply_youtube_candidates.py`
- `tools/versanium/audit_native_graph.py`
- `tools/versanium/check_ab_selection.py`
- `tools/versanium/flag_metadata_pipeline.py`
- `tools/versanium/prepare_config_a.py`
- `tools/versanium/prepare_config_a_origin.py`
- `tools/versanium/prepare_config_a_origin_forward.py`
- `tools/versanium/prepare_content_diagnostic.py`
- `tools/versanium/prepare_diagnostic_update.py`
- `tools/versanium/prepare_native_diagnostic.py`
- `tools/versanium/prepare_run9.py`
- `tools/versanium/tests/test_config_a.py`
- `tools/versanium/tests/test_config_a_origin.py`
- `tools/versanium/tests/test_config_a_origin_forward.py`
- `tools/versanium/tests/test_content_origin.py`
- `tools/versanium/tests/test_content_preparation.py`
- `tools/versanium/tests/test_delegate_origin.py`
- `tools/versanium/tests/test_diagnostic_update.py`
- `tools/versanium/tests/test_native_origin.py`
- `tools/versanium/tests/test_native_preparation.py`
- `tools/versanium/tests/test_run9.py`
- `tools/youtube_pip/candidate.js`
- `tools/youtube_pip/diagnostics.patch`
- `tools/youtube_pip/execution_scope.patch`
- `tools/youtube_pip/tests/check_execution_scope.py`
- `tools/youtube_pip/tests/check_fullscreen_origins.py`
- `tools/youtube_pip/tests/check_passive_diagnostics.py`
- `tools/youtube_pip/tests/check_pip_branches.py`
- `tools/youtube_pip/tests/check_source_integration.py`
- `tools/youtube_pip/tests/test_candidate.cjs`

## Added evidence

plan.md (written first), before.json (pre-edit byte hashes), references-before.txt
(complete candidate/PiP/diagnostic reference inventory), validation.json,
validate.py (reproducible build-free validation), this report.

Run from the repository with UTF-8 Python and the bundled Bash location available:
`python -B docs/versanium/pip-candidate-retirement-2026-10-28/validate.py`.
It checks the historical hash ledger and runs only the documented available
static checks/tests; it rewrites only validation.json in this evidence directory.
Exact final commit SHA/push result/final Primary and PR heads are reported after
the single commit, outside this commit's self-referential evidence.
