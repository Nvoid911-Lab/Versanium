# Phase1 diagnostic logging — 2026-10-28 JST

Start controller: 9ef1c26350042cfe8369357d994fcef143a39ca2.
Branch: next-test/156-zoom-transfer-pip. Diagnostic source ready for explicitly
requested fresh incremental build. This is not a PiP behavior fix.

Previous fresh build logs confirm integration/GN/chrome_java/chrome_public_apk PASS.
Galaxy S23 test FAIL is user-reported: launch and YouTube playback work; switching
tabs stops playback; Home produces no PiP; playback stays stopped. Next=diagnostic
instrumentation, then manual user transfer/logcat collection. No ADB/install here.

## Events

Chromium org.chromium.base.Log.i, tag VersaniumPiP, format
`VSPIP event=<EVENT> key=value ...`. Chromium normalizeTag adds its configured
cr_ prefix, so the actual logcat tag is cr_VersaniumPiP. R8's existing
maximumremovedandroidloglevel=3 retains INFO(4); no logging flags are changed.
No full URL query or video ID logging.
URL scheme/host/path are bounded and sanitized. hasVideoId is a boolean.
Policy eligibility and upstream eligibility are separate events. Log statements never feed eligibility, state or media decisions. The mobile/desktop
follow-up adds at most two passive page probes (no timers), independently of owner
lifecycle; these observe existing Java WC/media callbacks and never issue actions.

- POLICY: scheme/host/path/hasVideoId, Activity support/finishing/destroyed/config,
  upstreamEligible/eligible/reason. Reasons retain strict mobile watch scope:
  non_https, wrong_host, wrong_path, missing_video_id, invalid_authority,
  unsupported_activity, no_tab, no_web_contents, activity_finishing,
  activity_destroyed, configuration_change, upstream_ineligible, eligible, etc.
- UPSTREAM_POLICY: original canDoPictureInPicture result and exact rejection branch
  (no WC, no allowed fullscreen video, no system feature, already PiP, config,
  finishing, recent tasks). Original short-circuit decisions remain unchanged.
- INIT, OWNER_ADOPT/OWNER_REPLACEMENT, CANDIDATE_UPDATE/CANDIDATE_TERMINAL,
  GENERATION, STATE from/to/reason. State wrappers perform the original assignment
  in place; generation increments stay in place. Same-owner/current/foreground
  correlation uses existing Tab IDs, never tab ID lookup for media routing.
- ENTRY_ATTEMPT/ENTRY_REQUESTED/ENTRY_SUPPRESSED, ROLLBACK_REQUESTED/ENTRY_ABORTED,
  ENTRY_BEFORE_FRAMEWORK/ENTRY_RESULT/ENTRY_EXCEPTION, AUTO_ENTRY_STATUS,
  FRAMEWORK_ENTERED/ACTIVE_ADOPTION/FRAMEWORK_EXIT, EXIT/CLEANUP/OWNER_SUSPEND.
  ENTRY_RESULT records the single original enterPictureInPictureMode call result.
  Upstream check is evaluated once per original call; its result is merely cached
  for the entry log. No additional eligibility evaluation or media action.
- USER_LEAVE_HINT, PAUSE, ACTIVITY_START/RESUME/STOP, PIP_MODE_ENTERED/EXITED,
  FULLSCREEN_ENTER/EXIT, TAB_SWITCH oldTab/incomingTab, TAB_DESTROYED, DISMISS,
  VIDEO_DISMISS, TERMINAL_ARM/CLAIM/RESET. Controller events carry state/generation/
  epoch, owner/candidate existence, ownerTab/WC presence, foregroundOwner.

A TAB_SWITCH followed by NEW_TAB DISMISS and cleanup shows the existing path;
an ENTRY_ATTEMPT indicates whether an explicit entry attempt occurred. No automatic
entry is added on tab switch. Home upstream rejection plus absent owner/adoption
can localize where existing fullscreen eligibility prevents Phase1 entry. Android
framework auto-entry is observed through status/callbacks, not a fabricated return.

## Behavior and verification

Existing eligibility conditions, URL scope, short-circuit order, return values,
state assignment order, generation increments, entry/exit/media/owner-token calls
are preserved. Only passive reads and logging are added. No gate change, force
resume, current-tab media fallback, product callback decision, JS/C++/JNI, Brave
#33522/#39765, Zoom/F11/branding/package/signing modification.

JVM400 assertions PASS (359 retained +41 diagnostic contract/lifecycle assertions); candidate6 and
active-owner24 remain PASS. Existing bundle5 PASS, gate-off/default-off PASS,
parse-only5 Java sources PASS. Log double records real emitted production messages;
assertions cover tag/format, state/owner/token events, rejection reasons and no full
URL/video ID values. Zoom exact Git blob gate24 PASS, retired34 absent.
The phase1 patch whitespace attribute only permits mandatory blank context lines,
matching the existing Zoom-patch rule; it does not change source bytes.

## Fresh incremental build boundary

Use only /home/takuma/versanium-fresh/phase1-36838 in Versanium-Ubuntu.
Reviewed Chromium base1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775;
patched Chromium e76ab5fc518ef2df24519c82cec55427870f8bd4;
Titanium156.0.8078.47; Vanadium2ae4335402eabcc6e025f3400185fe25094d8521.
Controller Vanadium helper has the existing four-line failed-patch error formatting
change; snapshot and preserve it. Blob Zoom gate PASS is distinct from its known
submodule dirty worktree result. Never reset/clean this or existing Chromium
branding/resources/subproject/compile compatibility changes.

Create diagnostic-only diff from prior composed Phase1 source, validate all anchors
and current overlay hashes, preserve backups/provenance, apply only that delta.
No full patch.sh or whole Phase1 reapplication. Check Zoom overlays/integration,
logging presence and Controller/Policy GNI registration1/1 before GN.
Run gn gen out/Default, then autoninja -C out/Default -j6 chrome_java, then only
on success chrome_public_apk. Preserve args/test identity and prior signed APK.
Check aapt2 package io.github.nvoid911.versanium.test before signing. Reuse the
existing local phase1-device-test.jks alias versanium-test; no secret in reports.
Verify signed APK and record SHA256/size/paths/free space in the delivery receipt.
No ADB, wireless debugging, Run9, merge/release/tag or Production.

## Same-device mobile versus desktop observation (user report)

Same Galaxy S23, same pre-diagnostic target APK:
- Mobile site FAIL: tab switch stops playback; Home no PiP; playback remains stopped.
- Desktop site PASS: tab switch continues playback; Home enters PiP; PiP keeps playing.
This increases the likelihood of YouTube mobile-site visibility/media behavior,
rather than generic Android PiP API failure. It remains a hypothesis until logs
establish whether visibility-driven pause precedes eligibility/entry evaluation.
No behavior change is made in response to this hypothesis.

Compare CASE_MOBILE_TAB_SWITCH, CASE_MOBILE_HOME, CASE_DESKTOP_TAB_SWITCH,
CASE_DESKTOP_HOME. Cases are user-labeled; the app need not infer the case name.
Every policy/controller/lifecycle snapshot identifies desktop_site and sourceTab
where a readable page exists; otherwise desktop_site=unknown. seq is a monotonic
logging-only counter. PAGE_MODE uses NavigationController.getUseDesktopUserAgent
and tabUaMode uses Tab.getUserAgent (no isDesktopUserAgent API in this revision).
The custom UA override getter is unavailable, so customUaOverride=unavailable;
no UA string is recorded. WC visibility is the existing Chromium visibility enum.

TAB_UNSELECTED / TAB_SELECTED / TAB_SWITCH_AFTER mark the existing selection
callback before/after its cleanup, not an invented pre-selection timestamp.
Existing onHidden/onShown callbacks emit TAB_HIDDEN/TAB_SHOWN. WC_VISIBILITY from
the retained outgoing page survives upstream tab observer cleanup. MEDIA_STARTED/
MEDIA_STOPPED record individual media signals; aggregatePlaying=unknown on stop.
MEDIA_SESSION records existing isControllable/isSuspended callback values;
there is no isActive getter, so sessionActive=unavailable, never inferred.
Fullscreen-video and fullscreen-PiP-allowed getters are sampled read-only.
PAGE_SNAPSHOT carries selected/retainedOutgoing/owner and its triggering event.

Diagnostic observation accepts YouTube watch pages on m./www./bare host purely
for mobile/desktop comparison. Product eligibility remains exact HTTPS m.youtube.com/watch.
The probes are invoked by existing upstream tab registration, so they also work
when Phase1 candidate eligibility is false. At most current+previous pages remain;
third-page rotation, stale Tab/WC identity, WC destruction and Activity destruction
detach observers. Initial synchronous MediaSession state callback, outgoing pause
AFTER switch, stale callbacks, two-page bound and teardown are fixture-tested for
both desktop_site=false/true. Neither probe performs suspend/resume/entry/cleanup.
