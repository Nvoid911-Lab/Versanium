# Native device trial: EAM reentry and early media stop — 2026-10-25 JST

The narrow NEXT product diagnosis is now implemented/reviewed in
content-fullscreen-diagnostic-review.md. It is not applied/built on saved Native;
this trial's evidence and unknown signed APK hash remain unchanged.

User conditions: Galaxy S23, Native configuration, diagnosis/background/PiP
candidates ON, browser restart after settings directly confirmed. Visible result:
**PiP briefly displayed, audio stopped, no crash.** Complete supplied72 stage
lines plus header are retained in native-diagnostic-device-2026-10-25.log.
Signed Native APK SHA256: **not reported / unknown**. Do not copy Forward's hash
or infer a binary/source identity from the labels. Source analysis below uses
reported composition and pinned source; it is not binary provenance verification.

## Observed facts, separately from previous Forward

|Time|From entry|Observed stage|
|---|---:|---|
|18:08:43.867 / .868|0 / 1ms|framework entry; persistent true request/returned|
|43.970 / .981|103 / 114ms|effective fullscreen true; auto_allowed|
|43.993|126ms|wrapper→ExclusiveAccess; actual EAM JNI d1→Controller d2→tab-caused exit→notify loss|
|43.993|126ms|nested JNI d3/Controller d4→window-or-tab return|
|43.994|127ms|context exit d2→native Java context→accepted Base exit|
|43.995|128ms|Base persistent exit→second nested d3/d4→same composite return→reason6|
|44.009 / .015|142 / 148ms|move request / moveTaskToBack returned true|
|44.083|216ms|media_stopped|
|44.283 / .293|416 / 426ms|effective false / inactive reason7|
|44.304|437ms|Activity STOPPED request|
|44.330 / .331|463 / 464ms|stop_suspend stage, then stop_not_playing|
|44.347 / .391|480 / 524ms|tab hidden / framework exited|

media_stopped precedes stop_not_playing by248ms. There is NO
stop_suspend_called. In the selected Java code, stop_suspend is logged before
checking session/playing; stop_not_playing means non-null MediaSession and false
controller mIsPlaying, so this onStop branch does NOT call SYSTEM suspend. This
trial's first stop cannot be attributed to that call. Previous Forward② did
log actual SYSTEM suspend; preserve that result as another condition/trial.
Other native MediaSession/audio-focus operations are not excluded by absence of
this particular Java marker.

The controller's mediaStoppedPlaying callback sets its mIsPlaying=false, but
does not expose which player stopped or why. It is not a fresh query of every
player/session. Audio stopping is independently user-reported. Neither the
callback nor the later onStop proves the initial pause source.

## Fixed156 code path, now constrained by actual branch logs

Chromium pin1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775. Native diagnostic
source/labels are the existing16eca product; no product/helper is changed here.

### Initial entry remains upstream of the instrumented EAM boundary

The usual fixed native route is RenderFrameHostImpl::ExitFullscreen API ingress
or WebContentsImpl::ExitFullscreen→ExitFullscreenMode→WebContentsDelegateAndroid
→Java wrapper→Activity exclusive branch→EAM JNI. WebContentsImpl's ExitFullscreenMode
also changes the view's fullscreen state before forwarding and may reenter.
Browser security-drop, navigation/fullscreen cleanup and renderer-gone cleanup
are other possible entrances. Direct wrapper forwarding does not uniquely identify
one native caller; the current diagnostic has no content-side ingress marker.
Multiwindow callback alone is not an exit request. The selected Base PiP guard
requires !EAM and therefore does not execute in the observed exclusive branch.
No earlier accepted exit/local STOPPED/tab-hidden request is present here; filtered
events or other uninstrumented callers still cannot be ruled out by silence.

### Actual outer branch and both synchronous reentries

The outer Controller d2 reached tab_caused_exit. By the unchanged code order,
within-tab early return was not selected, window/pending+tab composite guard
passed, context IsFullscreen was true, then IsFullscreenCausedByTab was true.
These are deductions from already executed branches, not additional getter calls.

The nesting is observed directly; mapping each nested chain to the following
specific call-out is a source-backed inference, not a recorded native stack or
per-instruction call-site label. No independent external-request count follows.

1. ExitFullscreenModeInternal calls Android NotifyTabExclusiveAccessLost before
   context()->ExitFullscreen. The former captures exclusive WebContents, clears
   exclusive tab/origin/tab-fullscreen state and calls WebContents::ExitFullscreen.
   This routes back through delegate/EAM while outer scopes are live: JNI d3,
   Controller d4. The composite window-or-tab guard returns. This corresponds
   to the first observed nested chain following notify_access_lost.
2. The outer call survives its existing WeakPtr guard and context_exit_call d2
   proceeds through ExclusiveAccessContextAndroid JNI→Java context→FullscreenManager
   Base.onExitFullscreen. Base accepts, records persistent exit, sets its
   persistent fullscreen supplier false and calls its stored WebContents exit
   helper. That helper again calls WebContents.exitFullscreen(), corresponding
   to the second d3/d4 before observer notification.

Clearing exclusive tab explains a possible mismatch operand, but d4 logs the
OR guard only: short-circuit window/pending failure vs mismatch is not separately
measured. Do not invent an operand result. Both nested calls return before the
context IsFullscreen branch. There is one observed d1 chain and two observed
nested cycles in this range, NOT evidence of three independent external requests.
Filtered/uninstrumented entrances and asynchronous ancestry remain unknown.

### From accepted fullscreen exit to early PiP cleanup

Base observer invokes reason6. At148ms moveTaskToBack(true) returns true; selected
dismissActivityIfNeeded immediately invokes onExitedPictureInPicture(reason),
even though the framework exit callback arrives much later. Active app-side PiP
is defined by nonempty mOnLeavePipCallbacks. Its cleanup runs stored callbacks
and clears them, so later reason7 can report inactive while Activity still says
inPip=true. This is not a contradiction or proof of a second independent exit.

The entry callback registered setHasPersistentVideo(false) guarded by
!webContents.isDestroyed(). Thus cleanup has a concrete route to persistent-video
false BEFORE framework_exited. The false request/guard outcome was not logged
directly in this trial: source makes it expected on the live-contents path, not
an independently observed false IPC or renderer completion.

WebContentsImpl::SetHasPersistentVideo(false) updates preferences and requests
MediaWebContentsObserver::RequestPersistentVideo(false). That method can return
if no fullscreen_player_ remains (fullscreen changes can clear that player).
Otherwise it sends SetPersistentState to renderer; a sent request is not an ACK.
Blink HTMLVideoElement changes is_auto_picture_in_picture_, persistent CSS and
player display state. GetDisplayType gives video PiP while the auto-PiP bit is
true. Clearing it can remove the renderer's PiP exception. WebMediaPlayerImpl's
SetPersistentState itself updates overlay info; it does NOT directly call pause.
Do not simplify this chain into "persistent false directly stops playback".

WebMediaPlayerImpl handles page/frame-hidden transitions and can execute
PauseVideoIfNeeded→client PausePlayback. ShouldPausePlaybackWhenHidden has a
frame-hidden explicit-pause condition BEFORE its video-PiP exception; PiP is
therefore not a blanket guarantee against every hide policy. Remaining gates
include background-playback setting, audio/capture and background suspend.
Titanium's selected inherited policy already disables IsBackgroundMediaSuspendEnabled
using #if0; enabling another generic background flag is not an established fix.
JS background candidate visibility masking does not change native page visibility,
MediaSession/audio focus or every explicit site pause.

MediaWebContentsObserver::OnMediaPaused leads through PlayerInfo::SetIsStopped
to WebContents::MediaStoppedPlaying; player destruction can also issue a stopped
notification. Android WebContentsObserverProxy forwards only player id to the
Java stopped callback and drops native stopped_reason. Current fixed-label log
contains neither reason nor player identity. MediaSessionImpl has other native
suspend/stop/audio-focus paths as well. Thus44.083 identifies an observed stop,
not its call stack or whether page, browser hide, session, end-of-stream or
player teardown initiated it.

## Is there a safe behavior fix with unknown initial requester?

There is a concrete policy interaction: renderer/Android PiP retaining fullscreen
versus a real EAM tab-fullscreen exit, Base reason6 dismiss and early cleanup.
The code intentionally treats fullscreen exit as PiP cancellation. EAM's
NotifyTabExclusiveAccessLost clears state before call-out and inner guard returns:
the trace shows controlled reentry, not proof of a broken recursion guard.
Fixed WebContentsImpl::EnterFullscreenMode notifies the view's EnterFullscreenMode
BEFORE forwarding to the delegate; EAM selection alone therefore does not prove
the view never entered fullscreen. View/current-screen-state preservation and
renderer application during this run remain unmeasured. The disabled Base
multiwindow guard does not by itself identify a missing EAM fix.

|Candidate|Evidence / decision|
|---|---|
|Guard a proven browser-generated PiP transition exit at its origin|Potentially narrow and useful, but that origin has not been identified. Retain genuine user/security/tab-close exits.|
|Keep persistent-video until actual framework exit|Source supports an early cleanup interval, but delaying this alone does not prevent the successful move-to-back. May retain stale state or alter valid exits; not a proven fix.|
|Ignore reason6/inPip EAM exits, bypass onStop or force feature OFF|Cannot distinguish valid exits, and onStop suspend is absent in this trial. Reject.|
|Extend grace / force play / globally relax visibility/autoplay|Does not explain first exit; affects manual pause/other sites. Reject.|

No production behavior patch is justified from this trace alone. Keep background
tab-playback improvement/manual stop, DeX and other sites; B/video zoom remains a
separate, unapplied candidate with no established shared cause.

## Smallest useful NEXT diagnostic scope, before authorizing another APK

Do NOT repeat already resolved EAM branch/depth instrumentation alone. A combined
candidate would answer two specific remaining questions:

1. Which content ingress starts the first delegate/EAM exit? Fixed enter/return
   enum labels at RenderFrameHostImpl::ExitFullscreen and WebContentsImpl::ExitFullscreen,
   plus actual selected security/navigation/renderer-gone call sites and generic
   ExitFullscreenMode dispatch. Generic dispatch alone cannot answer this.
2. Does app-side cleanup request persistent false before stopped notification,
   and is there still a fullscreen player to receive it? Fixed labels in existing
   guarded cleanup callback and actual RequestPersistentVideo send/no-player
   branch. Returned/sent must not be labelled renderer-completed.

Use an existing content observer boundary rather than a chrome include in
content: fixed native WebContentsObserver event→Android WebContentsObserverProxy
→Java observer→existing current-tab scoped PiP reporter. Fixed pin contains
content/browser/android/web_contents_observer_proxy.cc and its existing content
JNI header. Any new public callback/JNI generation and exact Java signature
requires separate implementation/type/dependency review, not an already available
API. No arbitrary Java strings/scripts/native stack capture. Shared Chrome TLS
header must NOT be included from content. Paired enter/return events use local
WeakPtrs and UI thread; no return callback after destruction, no raw pointer
retention or assumed async parent. Match actual WebContents to live current tab,
normal non-shutdown profile, HTTPS exact YouTube and diagnosis flag at both ends.
Restrict valid originating frame as reviewed; filtered child/destroyed frames
must remain inconclusive. No permission getter repeats or CHECK modifications.

Expected discrimination: renderer API marker vs browser/security/navigation/
renderer-gone marker before first EAM; nested EAM side effects after that; cleanup
false requested vs no fullscreen player. Still cannot identify exact YouTube JS
function, user intent, renderer application time or pause cause. If first origin
proves actionable, evaluate a narrow fix BEFORE adding media diagnostics.

Only if stopping remains a separate question after that: actual browser session
OnSuspendInternal and renderer PauseVideoIfNeeded selected branch need fixed
reason labels (not re-running ShouldPausePlaybackWhenHidden). Renderer reporting
requires a reviewed bounded enum Mojo path to the browser's scoped observer;
unscoped renderer logs cannot safely enforce current-tab/profile restrictions.
This is additional work, not a reason to schedule another diagnosis-only build
without a clear expected distinction. No renderer instrumentation is implemented.

Required future targets: actual graph objects for render_frame_host_impl.cc,
web_contents_impl.cc, web_contents_observer_proxy.cc, media_web_contents_observer.cc
within content/browser target; content public observer/JNI generation and Java
target, chrome_java/NullAway, then APK. Media pause extension also needs the
actual media-session/player renderer targets/Mojo generation. Names/toolchains
must be resolved from fixed GN + actual graph, not guessed Ninja paths. All
public callback/JNI/graph changes need a new selection/transaction review against
the actual built Native evidence. No existing helper is relaxed or reused here.

## Source verification and limits

Fixed156 source reads, selected controller hash86911a7b… correspondence, log
order/nesting assertions, exclusive-tab-clear-before-WebContents-exit and Java
cleanup/stop gates were checked. New fixed source SHA256:

|Source|SHA256|
|---|---|
|web_media_player_impl.cc|6b650cb68e48c50f62e85f88d8892ca3f67615989628c33724a87a4a349538b7|
|media_web_contents_observer.cc|28ec2033b17901278ecd73f5a09ac8f1956ab49eeec1582f716ec085d01196b8|
|media_session_impl.cc|75cf754cd56de9dceea712415e74ae8a262e7e1b9a4a0782ff5b12d93dc28e33|
|web_contents_observer_proxy.cc|26e763acdd195f8e2ab56ad252254dd92c96ce3cb016eb4bd0b8218611e741e3|

This is source/log investigation, not new model/Chromium compilation or a fixed
APK result. Native diagnostic execution on device is user evidence; signed APK
hash and new host provenance are unknown. No product/helper/manifest/identity/
signing/Secrets/runner change, saved-tree access/change, build/GN/Actions/B,
clean/reset/sync/merge/Release/tag operation is performed in this task.
