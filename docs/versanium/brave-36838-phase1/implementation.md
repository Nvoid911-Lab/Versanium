# Current follow-up — terminal observer ordering fix

2026-10-28 JST: **HIGH finding fixed but still NOT compiled/built/device-verified.**
Next: `READY_FOR_36838_PHASE1_PREBUILD_REREVIEW`.
The [terminal fix report](terminal-fix.md) supersedes the prior hadPipSession-only
terminal routing and records 255 JVM assertions, 24 observer-order cases and
the new owner/generation one-shot token. The initial implementation record below
is historical; no real compile/build/device gate has been passed.

# Brave #36838 Phase 1 implementation — 2026-10-28 JST

**Phase 1 implemented but NOT compiled/built/device-verified.**

Next state: `READY_FOR_36838_PHASE1_PREBUILD_REVIEW`.
This is source/fixture readiness, not a build authorization or a demonstrated PiP fix.
A separate Source-of-Truth gate is mandatory before any GN/build/device stage.

Start HEAD: `dd481665361e28baa24a4536d3056dfb3a59e76b`.
Branch: `next-test/156-zoom-transfer-pip`, Primary `Nvoid911-Lab/Versanium`.
PR5 was Open/Draft/unmerged at the start and immediately before publication.
Its body is not edited. Final commit/push/PR-head receipt is supplied with the delivery.

## Source and scope

The [approved design](approved-design.txt) is the implementation specification.
Production Java overlays are in `tools/youtube_pip_phase1/java/org/chromium/chrome/browser/media/`:

- `VersaniumYouTubePictureInPicturePolicy`: strict HTTPS exact mobile watch URL,
  nonempty video ID, normal tabbed Activity, upstream eligibility, owner identity,
  timing and dismiss classification.
- `VersaniumYouTubePictureInPictureController`: INACTIVE/ENTERING/ACTIVE/EXITING,
  monotonic generation, Activity/window/Tab+ID/WC/document identity, candidate
  adoption, weak UI-thread locator, host retention, rollback, observers and cleanup.

Both files preserve the Brave copyright/MPL-2.0 notice and name Brave #36838,
source revision `4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2`.
They are adapted, restricted implementations, not copies of Brave's full controller.
Keep these MPL files and their source provenance available with any distribution;
distribution must provide the MPL-covered modified source and its retrieval method.
The BSD Chromium patch contains independent forwarding/guard code only.

The bundle patches only `chrome_java_sources.gni`, VIDEO, HTML Base and
`ChromeActivity`. New sources target the existing `//chrome/android:chrome_java`.
There is no new C++, JNI, components registry, MediaSessionHelper edit,
toolbar/manual entry, script injector, visibility override or background policy.
#33522 and #39765 remain unimplemented. Old candidates remain retired.
Screen lock follows ordinary stop. Configuration changes terminate safely;
there is no active-session Bundle restore. Entry never resumes MediaSession.

## Integration and ordering

`patch.sh` adds one independent installer invocation after the unchanged Zoom
installer and before the existing branding installer. The new installer checks
the existing fixed Chromium/Vanadium pin gate, verifies every patch hunk and both
absent overlay destinations before writes, then installs the two sources.
Repeated install or anchor drift fails. It never invokes old generators,
GN or compilation. Do not apply it to a saved Run9 tree.

Explicit entry registers ENTERING immediately before the framework call and
rolls back false/exception only for its generation. A 2s orphan timeout confirms
framework PiP or releases the registration without normal fullscreen teardown.
Auto candidates are document-bound, observed snapshots; candidates alone confer
no HTML protection. Framework-reported PiP permits provisional adoption without
claiming that upstream persistent-video entry has already executed.

Activity true processing follows super/CCT/Actor exclusion, owner adoption,
upstream persistent-video entry once, then owner revalidation. False processing
starts EXITING before Actor/VIDEO exit callbacks. New intent ends ownership before
the existing VIDEO exit call. The Activity strongly owns VIDEO, which strongly
owns the dedicated controller; the weak locator is only a lookup aid.

VIDEO updates auto-PiP status before the suppression decision. Only matching-owner
START/RESUME/LEFT_FULLSCREEN/WEB_CONTENTS_LEFT_FULLSCREEN can be suppressed.
Fullscreen observer forwarding carries its actual Tab/WC. NEW_TAB stops and
cleans only the previous owner without moving the incoming foreground tab back.
CLOSE/CRASH/REPARENT continue through upstream dismiss handling even if owner
cleanup has already drained persistent-video callbacks.

Cleanup disables protection first. Owner-only media suspension and DOM exit are
guarded against WC replacement, document change and destruction. Browser fullscreen
ownership is independently tracked by a FullscreenManager observer so cleanup
cannot clear a later tab/document's fullscreen UI. DOM exit notification and the
500ms fallback share one cleanup claim. Effective-video-fullscreen false is not a
DOM completion signal.

One ordering refinement found during integration: owner persistent-video leave
callbacks are detached/cleared before external callback execution and before
DOM/browser cleanup, rather than drained at the end. Otherwise synchronous
fullscreen reentry could see an upstream active session and move the task back
during expand or NEW_TAB. This is an exactly-once cleanup/reentry measure, not an
EXITING-state dismiss suppression. Non-owner callback handling stays upstream.

Framework false starts exit classification without playback resume. Activity
resume confirms expand; stop/destroy confirms close. The 1s fallback checks the
actual Activity state and stops only the retained owner if it is not resumed.
The owner-routing tombstone prevents later media calls from falling back to a
new current tab. Deferred dismiss, unstash and auto-status work checks generation,
Activity, actual Tab/WC and lifecycle before running.

HTML preserves only the exact fullscreen owner, valid document/window, and valid
ENTERING or framework-confirmed ACTIVE state. Only ACTIVITY_HIDDEN may preserve;
switch/reparent/unknown hidden reasons end the owner. STOPPED additionally requires
the handler/callback Activity to match. DESTROYED listener cleanup always executes.

## Commit sequence

All first six commits contain `ENABLED = false`; the final integration commit
enables the single gate and connects the fresh-tree installer.

1. `73a6f447108b47803e35c1b89832dcf8c340f2f0` —
   Add gated YouTube PiP owner policy and source bundle
2. `e8551e2b4941df8663d2dd5caddc06160b95dd24` —
   Add generation guarded owner observers and cleanup transaction
3. `c61c11f22c758b38eeaaf57eec7942eb0adaaf09` —
   Wire explicit fullscreen PiP entry and rollback behind gate
4. `cf7eddc4a6655e0ca8b96cadf809cd49ffc304af` —
   Connect framework PiP adoption lifecycle and new intent ordering
5. `7e8c01086bfa35da23f7e88170ba2f239cbbd450` —
   Route dismiss signals and deferred media work through owner generation
6. `7bc13ee316274130e03436fb5e5c5ad8065129b4` —
   Guard owner HTML fullscreen preservation and provisional auto entry
7. Delivery commit — Enable integrated Phase 1 PiP with fixture validation and prebuild status

The initial test bytecode cache was inadvertently included in commit1 and removed
in commit2 with a local cache ignore rule. No bytecode cache is in the final tree.

## Validation and limits

- Actual two production source files compiled with explicit Android/Chromium API
  doubles under a scratch JDK17; **114 assertions PASS**. Cases cover eligibility,
  owner identities, duplicates, rollback/callback race, timeouts, auto/provisional
  adoption, navigation, all dismiss classes, hidden/stop, expand/close order,
  cleanup-once, DOM/fallback, new-tab isolation and old delayed work.
- Default-off actual-source fixture PASS.
- Five Python bundle/structural tests PASS, including fixed156 + selected
  Vanadium source-list change + unchanged Zoom Activity patch + new bundle,
  repeated-install rejection and no writes after a changed anchor. The expected
  drift-rejection test prints a git patch error; that is a passing negative case.
- Parse-only syntax of all five composed Java sources PASS with scratch JDK25.
  JDK17 could not parse upstream's unnamed-variable syntax; source was not altered
  to accommodate the older parser. Parser execution performs no type resolution.
- All 305 pinned Vanadium patch files were scanned, including two large patches
  fetched separately because the connector returned empty content. Only patch0265
  touches a target: a distant password-manager source-list entry. No matching
  Titanium chromium_src overlay was present. Exact fixtures/pins and scan record
  are in `tests/fixtures/pins.json`. Full patch.sh/build.sh was not executed.
- Existing build-pin test: five metadata-model cases PASS. Existing selected
  pipeline/contextmenu suites: two runnable cases PASS, eleven skips due to absent
  historical Linux fixtures. These tests do not run a compiler.
- The combined existing migration/resume suite did not pass on this Windows
  environment: unavailable Linux font, bash executable and PyYAML access/import
  prevented complete execution. An attempted scratch PyYAML install did not
  resolve sandbox directory access. These are recorded as environment failures,
  not passing tests. Existing tests and their inputs are unchanged.
- Python syntax/AST, shell syntax of patch.sh, MPL/provenance and scoped diff
  checks PASS. Workflows are untouched; actionlint is not applicable to this diff.
- All 24 Zoom source/patch/resource/test/pin files match the pre-change SHA256
  ledger. Both EnvironmentZoom calls have identical text and immediate lifecycle
  context after composed patch application; no statement was moved. Absolute line
  numbers may shift because PiP hooks are inserted elsewhere in the shared file.
  The remaining preexisting repository files outside the listed docs and patch.sh
  are unchanged.

Fixtures do not establish Android/Chromium API type compatibility, NullAway,
ErrorProne, actual graph inclusion, renderer behavior, PiP behavior or Zoom behavior
on a device. There was no actual chrome_java/Gradle/Android/native compilation,
GN regeneration, full build, Actions, APK/sign/install, saved Run9 access/change,
merge, release/tag or Production operation.

## Next Source-of-Truth gate

Review the exact published SHA and PR head against this report and the approved
design. On a separately authorized fresh source tree, review full fixed inputs,
source-list/dependency impact and unchanged Zoom statements. Source registration
means GN regeneration must be considered required for the future tree; do not
reuse an old saved graph as proof. GN, real Java/NullAway/ErrorProne and device
tests each require their own later authorization. Smartphone tests precede DeX.
No source/fixture result here authorizes that next execution stage.


### Phase 1 candidate-only terminal invalidation — 2026-10-28 JST

candidate-only invalidation regression fixed; still NOT compiled/built/device-verified.
JVM309 (+54), candidate terminal6, active-owner observer matrix24, structural5 and parse-only5 PASS.
Zoom24 SHA256 unchanged; retired34 absent. READY_FOR_36838_PHASE1_PREBUILD_REREVIEW_2.
Design/evidence: candidate-terminal-fix.md.
