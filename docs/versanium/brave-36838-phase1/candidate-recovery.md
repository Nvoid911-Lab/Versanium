# #36838 Phase 1 same-WebContents candidate recovery — 2026-10-28 JST

State: **READY_FOR_36838_PHASE1_PREBUILD_REREVIEW_3**.
**same-WebContents fresh candidate recovery fixed; still NOT compiled/built/device-verified**.
Start HEAD: `ba55d383b964f4a5e2bf1bdc7705094ec484c09c`.
Branch: `next-test/156-zoom-transfer-pip`; PR5 stays Open/Draft/unmerged.

## Root cause and choice

The old candidate rejection snapshot outlived its document observer. Consequently,
same-URL reload reused the same epoch and identities forever. Video ID was absent
from rejection equality, also rejecting a different YouTube watch video.

Compared options:
- Generation or timer alone cannot prove a fresh document. A timeout can admit a
  delayed same-document callback, while generation alone cannot detect reload.
- URL/video ID equality detects another video, but cannot distinguish same-URL reload.
- Chosen: document-scoped tombstone plus a minimal navigation recovery TabObserver,
  using existing committed-navigation, same-document and video ID APIs. This is
  the smallest option that observes same-URL reload after candidate authority ends.
  No new production testing API, navigation token API, imports or source-list changes.

## Lifetime and guards

Candidate terminal discards candidate authority and advances generation before
replacing its observer with recovery-only observation. It removes the locator,
creates no owner terminal token and invokes no owner cleanup. Recovery observation
has no terminal/fullscreen/hidden/media callbacks and no adoption authority.

Recovery requires the exact rejected snapshot, retirement generation, source Tab
and live controller. A committed cross-document navigation (including same-URL
reload), or a changed video ID from committed SPA navigation / onUrlUpdated,
advances epoch and removes both tombstone and recovery observer. Fragment or
same-video query changes and uncommitted/wrong-Tab notifications do not release it.
WC replacement observed through onContentChanged also advances epoch and releases.

A policy-validated fresh capture with different Tab/ID/WC/window/epoch/video ID
releases the old tombstone/observer. This also handles changed video IDs without
a URL callback. Valid explicit entry releases rejection while preserving its
existing independent eligibility policy. Tab destruction and host onDestroy
remove observation and strong snapshot references. Only one tombstone/observer
exists per controller; fresh evidence removes it before another candidate is
installed. There is no clock-based expiry or periodic task. The tombstone lasts
only for the rejected document/session, possibly until destruction if that
session never changes; it cannot permanently block subsequent observed documents.
No session is invented from a transient framework callback or status refresh.

Old dedicated terminal callbacks fail generation/epoch/snapshot checks. Old
recovery callbacks fail tombstone reference/generation checks. Queued old VIDEO
work fails guardDelayed before it can source-match a new same-identity candidate.
The active-owner terminal passthrough/token path is unchanged, including ENTERING.

## Verification

Actual production overlays and composed VIDEO routing run with API doubles:
**359 JVM assertions PASS**, baseline309 retained/updated: **+50** assertions.
The prior observer-removal assertion now verifies replacement by a single recovery
observer and removal of the old authority observer.

Four same-Activity/Tab/WC/window cases PASS: same-URL committed reload;
cross-document different watch URL; same-document different watch video;
video change through onUrlUpdated. Each also checks duplicate terminal idempotence,
synchronous recapture / late framework / provisional rejection, same-video fragment
rejection, rejection after time alone, recovery observer removal, stale dedicated
and recovery callbacks, stale guarded VIDEO terminal work, successful provisional
fresh adoption, no owner cleanup and final lifecycle detach.

Five additional lifecycle cases cover controller destroy, Tab destroy, explicit
entry, observed WC replacement and changed video fresh capture without callback.
Wrong-Tab and uncommitted navigation cannot release rejection; all observers detach.
Only the NavigationHandle double gains a configurable committed result, matching
production hasCommitted semantics. No production test bypass is introduced.

Candidate matrix: CLOSE/CRASH/REPARENT × dedicated-first/upstream-first = **6 PASS**.
Active-owner matrix: 3 reasons × 2 orders × live/dead WC × reentry/no-reentry =
**24 PASS**. Existing transient START/RESUME/LEFT_FULLSCREEN/
WEB_CONTENTS_LEFT_FULLSCREEN suppression and NEW_TAB foreground checks PASS.
No current-tab fallback, entry resume or #33522/#39765 implementation added.

Default-off fixture PASS; structural **5 PASS**; parse-only **5 Java sources PASS**;
Python AST and git diff --check PASS. Structural anchor-drift negative fixture
intentionally prints a patch error and verifies zero partial writes.
Zoom **24 exact ledger SHA256 matches**, retired **34 paths absent**; per-path proof:
[candidate-recovery-validation.json](candidate-recovery-validation.json).
Historical generators are not executed or reused.

## Compile risk and limits

Checked existing fixed-reference TabObserver callbacks: onUrlUpdated(Tab),
onContentChanged(Tab), onDestroyed(Tab), and
onDidFinishNavigationInPrimaryMainFrame(Tab, NavigationHandle). The latter receives
non-null NavigationHandle; hasCommitted/isSameDocument/getUrl are existing API.
NavigationHandle is consumed only synchronously in the callback, never retained.
Observer removal occurs before clearing snapshot references; stale dispatch copies
are guarded. No nullable WC dereference, new dependency, visibility or import change.
No source-list / integration patch change. JVM doubles and syntax parsing cannot
prove actual Chromium dependency resolution, NullAway or Android callback ordering.

Commands (bundled Python, existing scratch JDKs):
```
python tools/youtube_pip_phase1/tests/run_fixture_tests.py --jdk <test-jdk17>
python tools/youtube_pip_phase1/tests/run_fixture_tests.py --jdk <test-jdk17> --gate-off
python -m unittest discover -s tools/youtube_pip_phase1/tests -p test_bundle.py
python tools/youtube_pip_phase1/tests/run_parse_tests.py --jdk <parse-jdk25>
git diff --check
```

No GN regeneration, Chromium/chrome_java/actual NullAway/Gradle/Android compile or
build, Actions, APK/sign/install, saved Run9 access/operation, device verification,
merge/release/tag/Production operation, force push or PR body change. One commit
and normal push only; final commit/PR-head/body comparison receipt in delivery.
