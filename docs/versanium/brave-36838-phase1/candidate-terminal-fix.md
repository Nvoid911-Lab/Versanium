# #36838 Phase 1 candidate-only terminal invalidation fix — 2026-10-28 JST

State: **READY_FOR_36838_PHASE1_PREBUILD_REREVIEW_2**.
**candidate-only invalidation regression fixed; still NOT compiled/built/device-verified**.
Start HEAD: `6402367ee059bbf4f2fb466b93b4067478f332ee`.
Branch: `next-test/156-zoom-transfer-pip`; PR5 remains Draft/Open/unmerged.

## Root cause

invalidateTerminal() returned whenever mOwner was null. A live candidate could
survive CLOSE/CRASH/REPARENT and later be provisionally adopted by preserve().
onFrameworkEntered() also recaptured the current tab when no candidate remained,
so merely nulling mCandidate would not prevent late framework adoption.

## Exact design

- Each TabObserver now captures the observed Owner snapshot and generation.
  Candidate refresh allocates a generation and replaces even a same-tab observer.
  Terminal callbacks validate snapshot reference, generation, Activity and document
  epoch; the snapshot carries Tab/ID/WC/window identity. An old observer cannot
  operate on a replacement candidate, including same Tab/WC refreshed generations.
  REPARENT compares the reported new window against the observed original window;
  it does not require that a now-detached source remain live.
- invalidateTerminal explicitly branches: no owner calls discardTerminalCandidate;
  a matching active owner retains the previous reserve/cleanup/fallback sequence.
  Candidate discard first clears the snapshot and advances generation, then removes
  the observer and locator. It never enters beginExit, drains leave callbacks,
  exits DOM/browser fullscreen, suspends media or creates a terminal token.
- VIDEO's existing claim-before-auto-update hook discards a source-matched candidate
  in upstream-first order. A matching retained old owner token is handled only by
  the existing owner-token path and cannot discard a newer candidate.
- A rejected candidate identity tombstone prevents the synchronous auto-status
  update from recapturing the same Activity/Tab/ID/WC/window/document epoch after
  retirement. A new WC/window/document/tab can qualify again; explicit entry keeps
  its existing eligibility path. Destruction releases the rejected snapshot.
- guardDelayed already validates generation and Tab/WC. Advancing generation on
  candidate replacement and discard invalidates queued auto-entry/status work.
- Framework entry adopts only an existing live current candidate. Removed its
  current-tab capture fallback. preserve likewise needs the retained candidate;
  provisional adoption refreshes its observer with the owner generation.
- Only CLOSE/CRASH/REPARENT use terminal logic. NEW_TAB foreground handling and
  active-owner one-shot passthrough are retained. No entry resume, current-tab
  media fallback, #33522/#39765, manual toolbar or script injector implementation.

## Verification

Production Controller/Policy and exact composed VIDEO dismiss methods execute
against explicit platform doubles. JVM **309 assertions PASS**, formerly255:
**54 additional assertions**; prior cases retained. Default-off fixture PASS.

Candidate-only matrix: CLOSE/CRASH/REPARENT × dedicated-first/upstream-first =
**6 cases PASS** using the actual composed VIDEO routing with synchronous candidate
refresh. Covers observer detachment, timer invalidation, no terminal token,
duplicate notification idempotence, late framework rejection, preserve rejection,
no auto-recapture, and zero owner-cleanup/media/UI/dismiss/move side effects.
Replacement WC, window, document epoch, Tab and same-identity new generation survive
old observer delivery. Mismatched WC/Tab tokens and a retired active-owner token do
not clear a new candidate. Replacement WC can qualify after terminal retirement.

Existing active-owner **24 observer-order cases PASS**: all three terminal reasons,
both orders, live/dead WC and with/without synchronous callback reentry. Cleanup
once, upstream dismissal, token consume-once and dead-WC API avoidance retained.
NEW_TAB foreground and limited transient suppression checks remain PASS.

Structural/composition **5 tests PASS**. Expected patch-failure output belongs to
the anchor-drift negative test. Parse-only **5 Java sources PASS**. Python AST and
`git diff --check` PASS. Standalone JDK17 fixture and JDK25 parser utilities only;
this does not establish Chromium signatures/dependencies or NullAway correctness.
Static source inspection found no obvious new signature/visibility/import issue.

All **24 protected Zoom SHA256s equal zoom-before.json**. All **34 retired paths
absent**. Full per-path hashes and absent-path proof are recorded in
[candidate-terminal-fix-validation.json](candidate-terminal-fix-validation.json).
Only Controller, JVM fixture, this report, validation JSON, implementation status
and PROJECT_STATUS change. Existing integration patch and build inputs unchanged.

Commands:

```text
python tools/youtube_pip_phase1/tests/run_fixture_tests.py --jdk <scratch-JDK17>
python tools/youtube_pip_phase1/tests/run_fixture_tests.py --jdk <scratch-JDK17> --gate-off
python -m unittest discover -s tools/youtube_pip_phase1/tests -p test_bundle.py
python tools/youtube_pip_phase1/tests/run_parse_tests.py --jdk <scratch-JDK25>
git diff --check
```

No GN regeneration, Chromium/chrome_java/NullAway/Gradle/Android build, Actions,
APK/sign/install, saved Run9 access/operation, device test, force push, PR body edit,
merge/release/tag or Production operation. One commit and normal push only.
