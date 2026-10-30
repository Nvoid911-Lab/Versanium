# Shard2 repository reconciliation — 2026-10-27 JST

Primary Nvoid911-Lab/Versanium; Secondary Nvoid911/Versanium.
Branch next-test/156-zoom-transfer-pip; PR5→migration/versanium.
Start live Primary/Secondary/PR5/local HEAD:
`b69195c810ddf52bfdf94b010ed20ed16bc24742` (stage reconciliation).
Working tree initially had exactly the reviewed patch.sh line plus three
untracked host helper/review/adapter-test files. No reset, old checkout or bulk add.

## Exact product change

The pre-existing uncommitted patch.sh line is retained unchanged and formalized:

```diff
-sed -i 's|TabUtils.isUsingDesktopUserAgent(mItemDelegate.getWebContents())|(true \|\| TabUtils.isUsingDesktopUserAgent(mItemDelegate.getWebContents()))|' chrome/android/java/src/org/chromium/chrome/browser/contextmenu/ChromeContextMenuPopulator.java
+sed -i '/|| (TabUtils\.isUsingDesktopUserAgent(mItemDelegate\.getWebContents())/{N;s@|| (TabUtils\.isUsingDesktopUserAgent(mItemDelegate\.getWebContents())\n[[:blank:]]*&& mParams\.getSourceType() == MenuSourceType\.LONG_PRESS));@|| mParams.getSourceType() == MenuSourceType.LONG_PRESS);@;}' chrome/android/java/src/org/chromium/chrome/browser/contextmenu/ChromeContextMenuPopulator.java
```

Generated method return:

```java
return (mParams.getSourceType() == MenuSourceType.MOUSE
        || mParams.getSourceType() == MenuSourceType.LONG_PRESS);
```

Original Versanium MOUSE || ((true || desktopUA) && LONG_PRESS) has identical
Boolean result; true|| already short-circuited UA getter. Neither getter side
effects nor source-type evaluation order change. This is NOT a return to
Chromium's desktop-UA-dependent long press. No false&& constant, suppression,
flags/checker relaxation or blanket DevTools change. All unrelated patch.sh
commands (PiP/content/zoom/F11/identity/signing/branding/extensions) stay unchanged.

## Fresh selected source reproduction

Fixed Chromium1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775; selected pinned
Vanadium2ae4335402eabcc6e025f3400185fe25094d8521. The exact pristine context file
SHA256 is f180a74b1d0e13e7c8f4e9c59d11b9b68944ab0ae0c3d0d3c5fc5a8810ec227f.
No selected Vanadium patch changes this file. The old-version developer-menu
command is skipped for fixed156. Extend the current source integration framework
with this file and execute the one actual patch.sh TabUtils command in scratch.
Do NOT run full patch.sh or build.sh. Assert every other byte equals input.

```bash
python3 tools/youtube_pip/tests/check_source_integration.py \
  --source-tree /tmp/versanium156/source \
  --output-dir /tmp/shard2-reconciliation-20261027
```

Fresh context-menu SHA256:
`89380eab2e93a7c1f47782fa966f993642c2407a13b842518f7204e230e720c5`
Matches reported host post-fix EXACTLY. Target true||TabUtils count0, exact
MOUSE/LONG_PRESS return1. Surrounding DevTools/context-menu bytes unchanged.
Sed second application preserves bytes; fresh-source harness rejects stale input.

Fresh TabImpl SHA256 remains:
`de0b9b1bed2bd411c7ee4d0706ff2f943b082fdae3c76540bd70153095bb5831`.
Old stage declaration0, no-arg declaration1, direct3/environment1/total4 hooks,
all four old literal arguments0, mobile/null1. Stage generator is not modified.

Whole repository patch.sh SHA256:
`4a9222648de23055b9f314e1e31cbae068980d825d9883bb4f253998063cc881`.
User-confirmed validation-host patch.sh SHA256:
`649b208b4ef40529d1aab3ebd3ce0447f24839f89700bf9fc4a00b95c6769ba0`.
They are DIFFERENT whole-file identities. Host patch.sh bytes were not supplied;
therefore exact full-script differences/cause cannot be independently explained
here. Do not force the script to that hash or rewrite historical pins. The
semantic argument rests on the exact one-line repository diff and complete
context-menu output equality. Review remaining host/repository script differences
in the next saved integration work unit before source/output reuse approval.

## Tests

Repository unittest discovery99 PASS: previous95 plus4 new context-menu cases.
New cases: actual fixed-source command/whole-file hash/idempotence; reject original
upstream/true-constant/false-constant semantics; reject missing LONG_PRESS; all8
Boolean combinations preserve outcome and never invoke the UA getter.
Selected source integration includes context menu plus stage/current content/PiP
checks. Passive logger Java doubles9, PiP decision/dismiss Java doubles15, candidate
DOM37 and native scope C++ model17 PASS. Real pinned GURL header/API is compared;
model compilation remains distinct from actual Chromium objects.
actionlint, bash -n patch.sh, changed Python AST, git diff --check PASS.
The selected integration's printed failed-patch negative-anchor case is expected;
the enclosing test returns0. No test weakening or historical helper relaxation.

## Host outcomes and evidence limits

User confirms historical corrected shard2 exit0, warning/error diagnostics0,
ComplexBooleanConstant0, OOM0; later chrome0–7/family/final audit PASS. These are
user-reported existing results, NOT analysis performed or receipt re-audit here.
All evidence stays read-only and outside Git. Paths to previous stage/family
receipts remain in post-nullaway-stage-reconciliation.md. No artifact copy into
repository, saved Run9 source write, stage reapply, GN or processor invocation.

## Boundaries / readiness

Commit only patch.sh, new context-menu regression test, current integration test
extension and status/decision/this review. Preserve all three untracked host
helper/review/adapter-test files outside the commit. Before commit AND push verify
Primary still has start HEAD; normal push only. Secondary sync requires actual
ancestry and an unchanged remote tip, then non-force fast-forward. PR6 unchanged.
PR5 body historical verification wording is an update target; no broad body edit
in this work unit. RULES/ARCHITECTURE unchanged (no rule/architecture change).

Ready to proceed to saved source/output/graph/tool/full-integration REVIEW after
reconciliation publication. This is NOT source/output reuse approval or Test
Build approval. In particular whole-script hash differences and full native/JNI/
Java/APK integration provenance remain for that review. No capacity/reuse/time
promise. No Actions/APK/chrome_public_apk/real ErrorProne/NullAway/GN/clean/reset/
sync/source-output deletion/B/merge/Release/tag/Production operation performed.
