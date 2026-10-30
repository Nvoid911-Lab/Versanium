# PiP candidate retirement plan — 2026-10-28 JST

Written before implementation changes. Start local HEAD and Primary PR5 HEAD:
`3150c48958575934c17d8ce5de4c430f658d5b9c`; branch
`next-test/156-zoom-transfer-pip`; clean tracked/untracked status. PR5 Draft/Open/unmerged.
No saved source/workspace, APK or untracked input is part of this change.

## Remove

- Candidate generator, DOM payload, diagnostics/execution patches and dedicated tests:
  TabImpl load/show/hide/environment hooks, three chrome://flags and metadata,
  fixed-payload JNI/WebContents/RenderFrameHost bridge and generated candidate header.
- Fullscreen origin/delegate/native/content diagnostic transforms: Java controller
  hooks, observer transport/JNI, diagnostic scope header and its generated GN entry.
- Dedicated old candidate source-apply/recovery/selection controllers and tests.
  These are executable tooling, not evidence logs. Their historical revisions remain in Git.
- Candidate invocation in patch.sh and candidate-only reads in the shared provenance recorder.

Exact deletion paths follow. The reference inventory includes line numbers and
before.json records all tracked input hashes before any implementation edit.

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

## Preserve

- Every tools/environment_zoom byte (including policy, persistence, backup, SAF
  export/import/settings, phone/DeX separation, rendering behavior and tests),
  apply_environment_zoom.py, revision validator and Chromium156/Vanadium pins.
- Zoom's existing EnvironmentZoom listener/isMobileDisplay API and comment:
  old candidate callers will disappear; retained API is inert without a listener.
  This explicit residue honors the user's stronger no-Zoom-code-change constraint.
- Entire patch.sh except the single old generator invocation; this preserves
  F11, display, context-menu shard2 ErrorProne correction, inherited upstream
  media policy/features, branding, extension handling and all other edits.
- Branding assets/installers, identity, signing, release guards, workflows.
- All existing docs/evidence/manifests/device logs/audit reports byte-for-byte,
  and commit history. The four source-of-truth docs receive a superseding notice;
  historical text is retained. README receives the current retirement boundary.
- Fixed-source historical trace audits, fixed-JNI evidence verifier, generic
  Ninja graph parser and shared selected patch operations remain as historical
  verification utilities. They do not inject candidate product code.

## Dependency proof and validation boundary

patch.sh calls apply_environment_zoom.py independently before the old generator.
Zoom installer consumes only tools/environment_zoom; branding installer consumes
only its own assets/text edits. Old generator imports the four diagnostic transforms,
reads only tools/youtube_pip, then modifies generated Chromium files. It calls
Zoom's listener/display APIs, but Zoom does not import or invoke the generator.
No generated Chromium source checkout exists inside this repository; remove the
generators rather than editing the user's saved Run9 source. Previously applied
saved source/APKs still contain old candidates and are not migrated by this change.
The provenance recorder must stop requiring the now absent generated header.

Future research scope: Brave #36838, #33522, #39765 only. No Brave port, build,
GN, Actions execution, APK, merge, release, tag or Production operation.
Run static reference/integrity checks and available build-free repo tests only.
Commit once and normal-push only; preserve PR5 Draft/Open/unmerged and body.
