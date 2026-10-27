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
