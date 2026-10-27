# #36838 Phase 1 prebuild HIGH fix — 2026-10-28 JST

State: **READY_FOR_36838_PHASE1_PREBUILD_REREVIEW**.
**HIGH finding fixed but still NOT compiled/built/device-verified.**
Start HEAD: `6b79f124000d8ea0c5d5efdc134ef555c4f03452`.
Branch: `next-test/156-zoom-transfer-pip`; Primary PR5 stays Draft/Open/unmerged.

## Confirmed root cause and design choice

Dedicated CLOSE/CRASH/attachment observers called invalidate(), which drained the
persistent-video leave callbacks. A later VIDEO observer saw no active PiP session;
the hadPipSession-dependent exception could no longer forward terminal dismissal.
Cleanup can also unregister upstream observers when auto-enter is disabled, so
assuming that the later observer will always run is insufficient.

Compared: a reason-only pending flag cannot prove owner/generation identity;
postponing callback drain preserves the session predicate but exposes synchronous
DOM/UI reentry to still-active callbacks. Chosen: one retained owner/generation
terminal token with a consumed bit, separate from callback/session liveness.

- Dedicated terminal observers arm the token **before** cleanup. clear() retains
  its original Owner and generation, validated against the just-retired generation.
  New explicit/auto/provisional entry, NEW_TAB, new intent and destruction reset it.
- VIDEO claims the matching Tab/WebContents/Activity token before auto-candidate
  updates or other external cleanup. It marks consumption before any reentry.
  Duplicate terminal callbacks return immediately. NEW_TAB cannot claim a token.
- Dedicated terminal cleanup then invokes the same VIDEO hook as a fallback,
  guarded by the original owner and generation. This handles removal of upstream
  observers during dispatch; subsequent observer notification is a duplicate.
- leaveUpstreamOnce() retains its early, exactly-once cleanup. Callback lists still
  detach/clear before execution. Terminal responsibility no longer depends on
  their contents, hadPipSession, or WC liveness.
- A claimed owner terminal proceeds directly to the upstream interactive/screen-off
  decision, bypassing its minimum-exit repost. Reposting would discard the local
  one-shot grant after cleanup changed the generation. Nonterminal/unowned delay
  behavior and the upstream screen-off decision remain in place. No screen-lock
  workaround or #39765 implementation is added.
- Null attachment notifications now reach VIDEO for the retained owner as REPARENT;
  unowned/gate-off attachment behavior remains unchanged. Owned CLOSE is dispatched
  only for closing=true; gate-off behavior remains unchanged.
- No current-tab media fallback, entry resume, new JNI/C++, components registry,
  manual toolbar, injector, #33522 or #39765 implementation was added.

## Verification

Actual production Controller/Policy plus the exact two composed VIDEO dismiss
methods run against explicit API/platform doubles, not Chromium dependencies.
The prior fixture cases remain, updated for the new token API.

| Terminal | Dedicated first → upstream | Upstream first → dedicated |
| --- | --- | --- |
| CLOSE | PASS | PASS |
| CRASH | PASS | PASS |
| REPARENT | PASS | PASS |

Each cell runs with live/destroyed WC and without/with synchronous transient and
terminal reentry: **24 cases**. Each asserts one upstream dismiss, one move-to-back,
one controller leave/UI cleanup, duplicate suppression, consume-once, and dead-WC
API avoidance. Dedicated-first cases exercise fallback after callback drain/clear;
they do not rely on a later upstream observer being delivered.

Additional checks cover claim-before-auto-update invalidation, wrong owner,
guarded stale-generation terminal work after a new entry, NEW_TAB foreground
retention and exclusion from terminal tokens. JVM fixture: **255 assertions PASS**.
Default-off fixture: PASS. Five structural/composition tests: PASS, including
unchanged Zoom lifecycle contexts and rejection of anchor drift without writes.
The expected patch failure printed by that negative test is not a suite failure.
Parse-only syntax of all five composed Java sources: PASS.

Commands (standalone scratch JDK17 for fixtures, JDK25 for parser):

```text
python tools/youtube_pip_phase1/tests/run_fixture_tests.py --jdk <scratch-JDK17>
python tools/youtube_pip_phase1/tests/run_fixture_tests.py --jdk <scratch-JDK17> --gate-off
python -m unittest discover -s tools/youtube_pip_phase1/tests -p test_bundle.py
python tools/youtube_pip_phase1/tests/run_parse_tests.py --jdk <scratch-JDK25>
git diff --check
```

Static review: callback interface and constructor/hook signatures agree; all
new inter-class methods/constants are package-visible within the media package;
existing cross-package public hooks remain intact. Nullable source arguments are
identity-checked before token use; terminal dispatch itself requires no WC API.
No new imports or GN source registrations are required. No obvious visibility,
signature, import or nullability issue found; this is not NullAway/Chromium proof.

All **24 Zoom files match every SHA256 in zoom-before.json byte-for-byte**.
All **34 retired candidate paths** listed in the retirement plan remain absent.
Change scope contains only this Phase 1 bundle, its report/validation and project
status. patch.sh, workflows, pins and Zoom inputs are unmodified.
Machine-readable results: [terminal-fix-validation.json](terminal-fix-validation.json).

No GN regeneration, Chromium/chrome_java/NullAway/Gradle/Android build, Actions,
APK/sign/install, saved Run9 access/operation, force push, PR body edit,
merge/release/tag/Production operation or device test. Standalone fixture/parser
utility compilation is the only compilation performed. A separate review and
authorization gate remains required before any real compile/build.
