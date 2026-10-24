# AOrigin ② device result and external exit trace — 2026-10-24 JST

The user directly confirms browser restart after changing settings, and visible
result: **no visible PiP, audio stopped, no crash**. This is compatible with an
Android framework PiP entry callback followed by a short exit; framework entry
does not prove the user saw a window. The supplied log is preserved separately
in `config-a-origin2-device.log`. Do not replace the earlier A OFF/ON results.

## Observed sequence, not inferred origin

Entry21:13:34.274; multiwindow callback34.276 (+2ms); accepted_on_exit,
exit_persistent_entry and notify_exit_observer34.378 (+104ms); reason6 at34.379;
moveTaskToBack returned true34.382 (+108ms). Effective fullscreen false and
inactive reason7 follow34.445 (+171ms). Activity STOPPED request34.472 (+198ms),
SYSTEM suspend returned34.479 (+205ms), tab hidden34.481 (+207ms), framework
exit34.511 (+237ms), media stopped34.514 (+240ms).

The first accepted exit lacks a preceding request-specific label. The
multiwindow callback alone proves neither feature branch nor exit guard. The
recorded STOPPED and hidden callbacks are later, so those particular callbacks
cannot explain the first accepted exit. Earlier suppressed requests remain
possible. Two notify_exit_observer records do not prove two separate exit
requests: the logging statement is inside the observer loop.

## Fixed Chromium external path

All source references use Chromium1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775.
`tools/versanium/check_external_fullscreen_trace.py` fetches only the named
fixed files, verifies their recorded hashes and exact call edges. It does not
touch the saved build. This is source verification, not compilation or a runtime
call stack. The selected pipeline's AOrigin Base/controller transformations
do not instrument the following external forwarding edges:

1. `TabImpl` creates a TabWebContentsDelegateAndroidImpl wrapper around
   `mDelegateFactory.createWebContentsDelegate(this)`.
2. `TabbedModeTabDelegateFactory.createWebContentsDelegate` supplies
   ActivityTabWebContentsDelegateAndroid.
3. Native WebContentsImpl::ExitFullscreenMode calls
   delegate_->ExitFullscreenModeForTab(this), with a destruction-safe weak pointer
   around the delegate call. WebContentsDelegateAndroid forwards via generated
   Java_WebContentsDelegateAndroid_exitFullscreenModeForTab when its Java delegate
   exists. TabWebContentsDelegateAndroidImpl.exitFullscreenModeForTab forwards
   directly to mDelegate.exitFullscreenModeForTab().
4. ActivityTabWebContentsDelegateAndroid selects the EXISTING ExclusiveAccessManager
   feature branch. Enabled/non-null manager forwards there; disabled/non-null
   FullscreenManager calls onExitFullscreen(mTab) directly. Neither route emits
   an AOrigin local Base request label before accepted_on_exit.
5. RenderFrameHostImpl::ExitFullscreen (renderer API ingress) calls
   delegate_->ExitFullscreenMode(true). WebContentsImpl::ExitFullscreen also
   funnels into ExitFullscreenMode. Security-drop/opener and renderer-gone paths
   also reach fullscreen cleanup. A Java delegate marker alone cannot distinguish
   a page/renderer API request from browser security/UI cleanup.

Thus the delegate path is a concrete instrumentation gap, **not the established
cause**. Runtime feature selection and the first native caller are unmeasured.
Existing Base logger bridge rejects null, destroyed, private or non-current tabs;
the scoped logger also gates controller/activity/library/HTTPS YouTube/diagnosis.
No preceding label is not proof that no request occurred. The accepted marker
does not retroactively prove that another callback's tab passed its gate.

## Narrow next diagnostic proposal (not applied or built)

Before forwarding, instrument the wrapper exit method with a fixed
`origin6_webcontents_delegate_forward` label using its actual mTab. Instrument
ActivityTabWebContentsDelegateAndroid ONLY inside each existing selected,
non-null manager branch: `origin6_activity_delegate_fullscreen_forward` and
`origin6_activity_delegate_exclusive_forward`. Do not read the feature getter
again. These identify the unmeasured external Java boundary and selected route;
they do not establish its native caller. Retain current privacy gates and mark
absence as inconclusive rather than logging private/null tab identities.

If this boundary is confirmed, distinguish native RenderFrameHostImpl API
ingress, WebContentsImpl::ExitFullscreen and renderer-gone/security-drop callers
with fixed enum labels at their actual branches in a separately reviewed scoped
bridge. Do not add unrestricted native logs, stack/URL/title dumps, eligibility
re-evaluation, or CHECK exceptions. Scope/lifetime/JNI and actual native object
compilation would require a new review; not prepared as an apply-ready patch here.

A browser-generated PiP transition exit might eventually be distinguished from
intentional/security exits using the proven caller and transition state. No
behavioral bypass is justified yet: ignoring all reason6, all onStop, or extending
the50ms grace would also mask valid exits. Preserve background tab playback,
manual pause, DeX and other sites. No play loop/autoplay bypass is proposed.

## Validation and boundary

Fixed-source call edges and bytes: verified by the trace checker. Existing59
preparation/migration tests rerun separately; these are fixtures, not host proof.
No new Java product transformation or selection manifest is introduced. The
already-built AOrigin helper/manifest and all older recovery gates remain intact.
No Java/NullAway/native integration compile or new APK/device behavior is
verified. No saved-host source/output access, apply, B, Actions, build, GN,
dependency sync, clean/reset, merge, Release or tag operation is performed.
