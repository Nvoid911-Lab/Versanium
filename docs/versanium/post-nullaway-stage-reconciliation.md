# Post-NullAway stage-unused repository reconciliation — 2026-10-27 JST

Primary Nvoid911-Lab/Versanium; Secondary Nvoid911/Versanium.
Branch next-test/156-zoom-transfer-pip, PR5 targeting migration/versanium.
Live start branch/PR HEAD and Secondary branch:3651d1591babe9fcb94e3d1cff07b53bad61bfcf.
PR5 open/draft. No reset/checkout of older product/controller was performed.

## Scope and exact change

The passive crash correction removed candidate logging and callback, leaving
an unused private String stage. At HEAD the generator still emitted it, even
though the local uncommitted fix and the user's saved-host fix existed.
The authoritative patch.sh invokes tools/apply_youtube_candidates.py.

```
private void applyVersaniumYoutubeCandidate(String stage)
→ private void applyVersaniumYoutubeCandidate()
applyVersaniumYoutubeCandidate("show"/"hide"/"load")
→ applyVersaniumYoutubeCandidate()
active.applyVersaniumYoutubeCandidate("environment")
→ active.applyVersaniumYoutubeCandidate()
```

This changes five generator sites only. Four hook positions/count and all guards,
boolean mobile, WeakReference/listener, native/JNI fixed-payload route, generic
CHECK/permission and contents.applyVersaniumYoutubeCandidate(mobile, null) remain.
reportTitaniumYoutubePip(String stage) still uses its label and is unchanged.
No suppression, logging/callback restoration or compiler flag change.

Existing local patch.sh shard2 fix is retained byte-for-byte, but deliberately
not staged in this stage-only commit. Host patch.sh and cloud patch.sh are not
interchangeable. Untracked host preparation helper/text adapter/review files
are preserved and not included. No historical helper or manifest is relaxed.

## Fresh source reproduction

Fresh temporary output, never the saved Run9 workspace, from fixed Chromium
1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775 and selected pinned Vanadium
2ae4335402eabcc6e025f3400185fe25094d8521. Run the current selected source pipeline,
zoom/SAF/F11/common transforms, latest content/PiP generators and flag edits.
This is NOT a full build.sh/patch.sh execution, GN generation or Chromium compile.

Command used:

```bash
python3 tools/youtube_pip/tests/check_source_integration.py \
  --source-tree /tmp/versanium156/source \
  --output-dir /tmp/shard5-post-nullaway-reconciliation-20261027
```

Generated TabImpl SHA256:
`de0b9b1bed2bd411c7ee4d0706ff2f943b082fdae3c76540bd70153095bb5831`
EXACTLY matches user-confirmed post-fix saved-host SHA. Historical pre-fix:
`10f9dd82ad1939ea214b455dae85198937455f39861eddcd8af72964e222f2e4`.

Verified counts: old declaration0, new declaration1, direct no-arg3,
qualified environment no-arg1, total hooks4, old literal calls0 for all four
labels, mobile/null exactly1. Tests also assert each direct hook at its original
method entry. Current generic execution bodies/CHECK and scoped fixed route
are compared by the existing integration checks, not merely a string-only model.

## Historical test correction

Initial full repository test run:95 tests, one error. The historical controller
history positive case accidentally read the current worktree generator while
claiming old content-product invariance. Its rejection was correct.

Only the test fixture changed: copy the exact checked inputs from committed
7b608732d56f3885d5c950715d10709405695e70 into a temporary fixture; use real Git
ancestry/diffs with fixture HEAD bound to that commit. Keep wrong proof/delta
rejections, and explicitly replace the private signature in that fixture and
require Content product changed. No old controller code/gate/hash is modified.

## Host evidence — user reported, not locally re-audited

Preserve these directories read-only. Do not copy their inventories/logs into Git:

- historical shard5: /home/takuma/versanium/nullaway-chrome-shard5-real-20261026-210020
- stage apply: /home/takuma/versanium/shard5-stage-apply-fRAYvNCB
- corrected shard5: /home/takuma/versanium/nullaway-chrome-shard5-reanalysis-corrected-wc2I8NSP
- shard6: /home/takuma/versanium/nullaway-chrome-shard6-analysis-mZWnSct6
- shard7: /home/takuma/versanium/nullaway-chrome-shard7-analysis-bRs3rln3
- family final audit: /home/takuma/versanium/nullaway-chrome-family-final-audit-CLKz9ahR

The user reports the saved-host stage fix was applied and PASS, and supplies
these later shard/family audit references. Their raw receipts, exit/diagnostic
counts and full family coverage were not uploaded here. Do not claim a new
independent host audit or infer native compilation/APK/link/device success.
No analysis output is mixed into product APK output/signing.

## Local checks

- Current fixed-source/selected Vanadium + generated Tab/native/JNI/GN source
  integration assertions: PASS (not actual GN/JNI compilation).
- Repository unittest discovery tools/versanium/tests:95 PASS after the explicit
  historical fixture correction; Java fragment/JNI generator/standalone C++/host
  transaction tests within it remain limited tests, not Chromium compilation.
- Passive logger actual-method Java doubles9 + source scope checks: PASS.
- Actual PiP decision/dismiss method Java doubles15: PASS.
- Candidate DOM model37: PASS.
- Actual native scope method C++ model17 + real pinned GURL header hash/API: PASS;
  standalone model compilation is not real Chromium object compilation.
- actionlint, bash -n patch.sh, changed Python AST and git diff --check: PASS.

## Readiness / publication boundary

Stage-unused reconciliation is ready for review and normal branch push after
remote HEAD is rechecked unchanged. It does not authorize a Test Build.
The separate uncommitted shard2 patch.sh change has not been reconciled into this
commit; fresh whole-pipeline analysis may still encounter the old constant
expression until that reviewed change is independently published. Saved-host
source/graph/tool/output and latest product compatibility, full native/Java/JNI/
APK integration and current capacity need separate review before any reuse/build.
Old apply controllers must continue refusing the changed generator.

PR5 still contains historical UNVERIFIED/no-host-apply claims. Its current-state
summary is an update target: distinguish user-reported later host results from
historical verification limits, and link this reconciliation. Do not globally
rewrite historical run reports. PR6 is untouched. RULES/ARCHITECTURE unchanged:
there is no new stable operating rule or architecture.

No Actions, APK/full Chromium build, saved-tree apply, real-host analysis,
GN generation, dependency sync, clean/reset, merge, Release/tag or Production.
Normal selected-file commit/push and ancestor-checked Secondary synchronization
are authorized by this work unit; no force push or unrelated change inclusion.

## 2026-10-27 JST — Completed saved integration review / current state

This appended checkpoint supersedes the pending shard2/full-script/graph review
items above and in the shard2 reconciliation report; all earlier evidence and
verification limits remain historical. Reviewed product repository identity:
`d1e3261690917bb29d75947c3e9d6bf89c44f728` on Primary
`Nvoid911-Lab/Versanium`, branch `next-test/156-zoom-transfer-pip`.
Stage reconciliation `b69195c810ddf52bfdf94b010ed20ed16bc24742` is ancestral.
Primary branch and PR5 HEAD were read-only verified at the reviewed identity
before this documentation update; PR5 was Draft/Open/unmerged.

The completed saved integration review and the following host facts/hashes are
user-supplied evidence, not a new local replay or independent verification of
Linux evidence bytes. No further graph audit or Siso query is performed here.
Repository tests95 (stage) and99 (shard2) are prior results, not rerun results.

### Saved source / graph / Siso adoption boundary

- ROOT: `/home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951`.
- SRC: `$ROOT/chromium/src`; saved product output: `$SRC/out/Default`.
- Saved Default graph reuse: **PASS**. GN regeneration: **NOT REQUIRED** based
  on completed graph/Siso deps and inputs evidence, scoped to this saved state.
- `gn clean` is **FORBIDDEN** for this saved-workspace path. Preserve saved output,
  graph, args and Siso state; no clean/reset/re-generation or source reapplication.
- Incremental recompilation: **REQUIRED** for current changed sources. Reuse PASS
  is graph compatibility, not proof of successful new Java/JNI/native/link/APK
  integration, PiP correction, device success, or a build-duration guarantee.
- Use the current reconciled saved source as reviewed. Do not re-execute saved
  old `patch.sh` or saved old `tools/apply_youtube_candidates.py`.
- Saved-host patch.sh SHA256:
  `649b208b4ef40529d1aab3ebd3ce0447f24839f89700bf9fc4a00b95c6769ba0`.
- Reviewed repository patch.sh at d1e3261 SHA256:
  `4a9222648de23055b9f314e1e31cbae068980d825d9883bb4f253998063cc881`.
  User-confirmed completed whole-file comparison found only the reviewed shard2
  one-line fix, with no unknown patch.sh differences. Keep both identities;
  do not substitute one historical hash for the other or reapply the script.
- TabImpl.java post-stage SHA256:
  `de0b9b1bed2bd411c7ee4d0706ff2f943b082fdae3c76540bd70153095bb5831`.
- ChromeContextMenuPopulator.java post-shard2 SHA256:
  `89380eab2e93a7c1f47782fa966f993642c2407a13b842518f7204e230e720c5`.
- Default args.gn SHA256:
  `d2096bdd18bfb10c2edb46ef950864bf917351dd5c7b059921b51e8b8e335cf8`.
- Default build.ninja SHA256:
  `12c4790028be212b8810357063a782a7cfdd15c65b310e58a8fc2ac42172f585`.
- Default toolchain.ninja SHA256:
  `ffefe1ba49b1b845d8e8ab2fa388c6cd851373b035bc16212962faff71f23103`.

Siso binary: `$SRC/third_party/siso/cipd/siso`
(`chromium/src/third_party/siso/cipd/siso` relative to ROOT).
Identity: `siso v1.6.3`, `ProdCIPD=true`. Saved state exists in Default:
`.siso_config`, `.siso_deps`, `.siso_fs_state`, `.siso_filegroups`, `.siso_lock`.
Siso state is reusable within the reviewed saved-state boundary.

### Saved Siso deps / inputs audit — PASS

Evidence directory:
`/home/takuma/versanium/saved-siso-deps-inputs-audit-k7pGOgNy`.
`FAIL_COUNT=0`, `REVIEW_COUNT=0`,
`OVERALL=PASS_SAVED_SISO_DEPS_INPUTS_AUDIT`.
All7 target deps queries and all7 target inputs queries returned rc=0.

| C++ source | Input visibility | Freshness |
|---|---|---|
| exclusive_access_context_android.cc | 1 hit | CURRENT |
| exclusive_access_manager_android.cc | 1 hit | CURRENT |
| fullscreen_controller.cc | 1 hit | CURRENT |
| render_frame_host_impl.cc | 1 hit | REBUILD_REQUIRED |
| web_contents_impl.cc | 1 hit | REBUILD_REQUIRED |
| media_web_contents_observer.cc | 1 hit | REBUILD_REQUIRED |

Header visibility: `versanium_fullscreen_diagnostic_scope.h` deps=2/inputs=2;
`versanium_youtube_candidate.h` deps=1/inputs=1.
Java input visibility: `TabImpl.java` hits=3;
`ChromeContextMenuPopulator.java` hits=1.
Freshness indicates pending incremental recompilation, not graph inconsistency.
Protected state was unchanged before/after the query.

Full paths (files remain external; do not copy deps/inputs inventories into Git):

- REPORT: `/home/takuma/versanium/saved-siso-deps-inputs-audit-k7pGOgNy/REPORT.txt`
- FULL_DEPS: `/home/takuma/versanium/saved-siso-deps-inputs-audit-k7pGOgNy/deps.txt`
- FULL_INPUTS: `/home/takuma/versanium/saved-siso-deps-inputs-audit-k7pGOgNy/inputs.txt`
- SHA256SUMS: `/home/takuma/versanium/saved-siso-deps-inputs-audit-k7pGOgNy/SHA256SUMS.txt`

| Evidence file in that directory | SHA256 |
|---|---|
| REPORT.txt | c0f9ad7e3bd65665f373e78065ef67d3fb9842b2a62547febbf95395a654d7fc |
| deps.txt | 40d0a4ff8593accb266738dbe7bcf2b71c59de93827bfca8b0be31641f31ce7e |
| inputs.txt | 845dac4d8c16049338b9e09c1a865df0e8424bcf8e65c7df99a33c815339e279 |
| protected-state-before.txt | 8e8f96fd54a982cfa0f8f32548402cb704b365cafaa8f169c78bc3de8a7d85b1 |
| protected-state-after.txt | 8e8f96fd54a982cfa0f8f32548402cb704b365cafaa8f169c78bc3de8a7d85b1 |

The protected-state digest identifies the hash-list evidence files, not one
aggregate digest assigned to all five Siso state files. No SHA256SUMS.txt digest
was supplied; none is invented.

### Test Build Gate

**Test Build: NOT APPROVED. Next gate:
WAITING_FOR_EXPLICIT_TEST_BUILD_APPROVAL.**
Only explicit user approval in a later step may start a Test Build. This work
unit authorizes Source of Truth documentation, validation and normal commit/push
only. ChatGPT coordinates the gate; Codex edits/collects evidence/commits/pushes;
GitHub Actions is unused in this work unit.

Candidate path for later approval: retain the reviewed current saved source and
reuse saved `out/Default` via Siso/autoninja incremental build of
`chrome_public_apk` only. This is a candidate plan, not an executable instruction
or permission to run any build tool now. No old patch/generator re-execution,
GN gen/clean, dependency sync or fetch into saved Chromium is part of this path.
If saved source/graph/tool identity drifts, stop for review rather than repairing
or regenerating automatically. Before execution, present refreshed Source of
Truth/Context and check actual runner/WSL/memory/disk/concurrency per RULES.md;
prior capacity readings are not current approval.

Actions, APK build, merge, release, tag and Production remain **NOT APPROVED**.
Later saved-local Test Build approval does not automatically authorize Actions,
merge/release/tag/Production. No build/autoninja/siso ninja/GN/Actions/APK,
patch/generator execution, saved source/output write, merge/release/tag/Production
is performed by this documentation work unit. Preserve all historical evidence
and the three pre-existing untracked host helper/review/adapter files; the
separate documentation checkout cannot independently attest their current status.
