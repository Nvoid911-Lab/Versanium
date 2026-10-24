# Forward② / ExclusiveAccess investigation — 2026-10-25 JST

User directly confirms settings-change restart; visible result: **PiP briefly
visible, audio stopped, no crash**. Preserve this separately from AOrigin②'s
no-visible-PiP result. Complete supplied log, without normalization, is
`config-a-origin-forward2-device.log` (only a final newline is added if absent).
The installed Forward APK's hash/signing/build evidence was not supplied in
this message; do not invent its exact artifact hash or claim host verification.

## New evidence

|Time|From framework entry|Observation|
|---|---:|---|
|00:28:57.235|0ms|framework_entered; persistent_video_request|
|57.236|1ms|persistent_video_returned: Java/native call returned, NOT renderer completion|
|57.238|3ms|multiwindow_callback only|
|57.262 / .264|27 / 29ms|effective fullscreen true / auto_allowed|
|57.314|79ms|wrapper_forward + activity_delegate_exclusive_forward, twice each|
|57.333|98ms|accepted_on_exit + exit_persistent_entry|
|57.334|99ms|another wrapper/exclusive pair, observer notify and reason6|
|57.335|100ms|actual moveTaskToBack returned true; another observer notify|
|57.394 / .395|159 / 160ms|effective false, reason7, inactive7|
|57.434|199ms|Activity STOPPED request|
|57.449|214ms|SYSTEM suspend returned|
|57.461 / .466|226 / 231ms|tab hidden / media stopped|
|57.596|361ms|framework_exited|

Unlike prior AOrigin logs, a scoped external Java forwarding boundary and the
existing non-null ExclusiveAccessManager branch are now observed BEFORE the
first accepted exit. This excludes the normal Activity delegate branch for
those observed invocations, not every later FullscreenManager call. It does
not prove the EAM native pointer was nonzero, the JNI call ran, or the first
native caller: Java's next method can return early. Log suppression still
makes absent stages inconclusive. Repeated pairs are not independent root
request counts, and duplicate observer labels can be a single observer loop.

The full log also has effective fullscreen true→false→true at52.509/.539/.638,
before entry. That is preserved but not evidence that it caused the later exit.

## Fixed156 source trace

Pin: Chromium1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775.
The source/hash/edge audit `check_exclusive_access_trace.py` covers9 files;
`check_external_fullscreen_trace.py` retains the earlier native/Java ingress
trace. These are pristine fixed-source checks, not a compiled or captured stack.
Selected Vanadium patches and current PiP transforms do not modify the EAM
implementation/controller files examined here. Forward only instruments the
wrapper/Activity/controller; Base contains prior origin labels.

1. ActivityTabWebContentsDelegateAndroid's enabled feature branch forwards
   actual mTab WebContents to ExclusiveAccessManager.exitFullscreenModeForTab.
   Java checks native pointer !=0, clears mLatestFullscreenOptions, calls
   ExclusiveAccessManagerJni.exitFullscreenModeForTab(long,@Nullable WebContents).
2. Native ExclusiveAccessManagerAndroid::ExitFullscreenModeForTab(JNIEnv*,
   const JavaRef<jobject>&) converts FromJavaWebContents, DCHECKs non-null and calls
   eam_.fullscreen_controller()->ExitFullscreenModeForTab(wc). Do not remove or
   weaken the DCHECK, or send null for diagnosis. Native instance is created by
   init and destroyed by Java destroy, which zeros its pointer; diagnosis must
   never retain this pointer beyond the real synchronous call.
3. FullscreenController first handles fullscreen-within-tab, then rejects if
   no window-tab fullscreen/pending, different exclusive tab, or context not
   fullscreen. Those guards are unmeasured in current logs. Tab-caused fullscreen
   calls ExitFullscreenModeInternal; browser fullscreen has another path through
   NotifyTabExclusiveAccessLost and UI restoration.
4. On Android, ExitFullscreenModeInternal calls NotifyTabExclusiveAccessLost
   BEFORE context()->ExitFullscreen(). Notify captures the exclusive WebContents,
   clears exclusive tab/origin/tab-fullscreen state, then invokes
   web_contents->ExitFullscreen(will_cause_resize). That reaches WebContentsImpl
   → native Android delegate → wrapper → Activity → EAM again. Clearing exclusive
   state before calling out makes subsequent guard rejection possible; do not
   model these labels as an infinite loop or distinct initial requests.
5. context()->ExitFullscreen() is ExclusiveAccessContextAndroid::ExitFullscreen,
   which invokes generated Java_ExclusiveAccessContext_exitFullscreenModeForTab.
   Java @CalledByNative checks mActiveTab !=null and directly calls
   mFullscreenManager.onExitFullscreen(mActiveTab). This concretely returns to
   Base's accepted exit despite absence of the normal Activity delegate label.
   Context active tab can differ/change, so scoped callbacks still require actual
   tab/current-controller matching rather than attributing another tab's request.
6. Base's exitPersistentFullscreenMode sets its persistent supplier false and
   exits its stored fullscreen WebContents. Its exitFullscreen helper calls
   webContents.exitFullscreen(): another possible wrapper/EAM forwarding chain
   DURING the first accepted exit, compatible with the57.334 pair. Source
   compatibility is not proof that this exact stack occurred on device.

Native FullscreenController also posts fullscreen-change notifications using a
WeakPtr; context bubble destruction has a deferred weak task to avoid reentrant
deletion. These establish that not every notification is synchronous. Current
logs have no paired native entry/return or stack-scoped nesting evidence, so
they cannot assign the19ms gap or repeated labels to a unique mechanism.

### PiP guard versus persistent-video processing

Base's multiwindow PiP guard is inside edge-to-edge-on-2D AND **!EAM feature**.
Its comment explicitly covers fullscreen→PiP. EAM observed enabled means that
guard is bypassed as designed; callback alone does not request exit. EAM Java
also replaces Base's local FullscreenManagerDelegate: null tab requests call
exitExclusiveAccess, non-null requests deactivateTab. Neither is evidence that
the logged multiwindow callback initiated this exit.

The examined EAM exit method and FullscreenController exit paths do not test
Android PiP/persistent-video state before cleanup. This is a possible policy
interaction, not proof that an unconditional PiP guard belongs there: genuine
renderer/user/security/close requests also use these paths.

WebContentsImpl::SetHasPersistentVideo updates preferences, asks its media
observer to send SetPersistentState to a fullscreen player if present, and
updates RenderWidgetHostViewAndroid. The screen-state handler explicitly says
PiP requires/stays fullscreen and preserves current fullscreen on persistent
entry. Blink can update persistent classes/display type asynchronously. No
explicit EAM exit is called by this setter. Therefore returned does not confirm
renderer handling/fullscreen preservation, and source does not establish that
PiP entry itself should end fullscreen. Page/renderer API, browser cleanup or
another EAM caller still needs discrimination.

## Root cause status and limited fix options

Confirmed downstream mechanism remains accepted fullscreen exit → reason6 →
successful move-to-back/cleanup → SYSTEM suspend and exit. New evidence narrows
the pre-acceptance route to EAM forwarding. First requester and actual EAM guard
branch are **not yet established**.

|Conditional finding needed|Possible limited fix|Risk / gate|
|---|---|---|
|A specific browser PiP-transition-only cleanup initiates the first exit|Guard only that caller/transition, retaining explicit/security/tab-close exits|Must distinguish initiating call from recursive notification and test move/back/return, manual exit, DeX|
|Renderer API ingress initiates the exit|Investigate document/fullscreen/persistent transition; possibly narrow candidate behavior there|A real page exit is not safely suppressible solely because domain is YouTube|
|Only recursive EAM loss notification is mishandled after another valid exit|Correct that proven state/notification interaction|May remove redundant events without preventing the initial undesired exit|

No behavior patch is justified by current evidence. Do not suppress every EAM
exit/reason6/onStop, force feature OFF, or extend grace as a claimed fix. Retain
background candidate's tab playback, explicit pause, DeX and other sites; B is
not selected and no common zoom/PiP cause is established.

## Proposed next native diagnosis — design only, not apply-ready

Use fixed source enum and entry/return/selected-branch labels, not stack/URLs,
titles, cookies, profile IDs, tab IDs or Java/page-provided script. Record an
event only for a live actual request WebContents, normal non-shutdown context,
HTTPS exact allowed YouTube, diagnosis flag, and matching live current Java tab.
Do not invoke fullscreen/permission/eligibility getters again for logging.

|Boundary|Information added|Compile/JNI target|
|---|---|---|
|RenderFrameHostImpl::ExitFullscreen actual API ingress|Renderer API request vs later forwarding|saved render_frame_host_impl.o, content/browser target; current valid primary frame only|
|WebContentsImpl::ExitFullscreen / actual security-drop and renderer-gone branches|Browser entry and specific cleanup origins vs generic dispatch|saved web_contents_impl.o; labels inside already selected branches|
|ExclusiveAccessManagerAndroid JNI entry/return|JNI actually entered, distinguishes Java pointer early return|//chrome/browser/ui/android/exclusive_access:exclusive_access, manager_android object|
|FullscreenController existing guard returns and Android NotifyTabExclusiveAccessLost call sites|Actual rejection/call-out branch; distinguish recursive notification from initiating request|//chrome/browser/ui/exclusive_access:exclusive_access, fullscreen_controller object|
|ExclusiveAccessContextAndroid→Java context call|Native context output that enters Base|Android exclusive_access context object, //chrome/android:chrome_java and generated JNI headers|

For same-thread recursion, pair fixed entry/return labels around the actual
forwarding calls (without arbitrary stacks). A scoped nesting mechanism may be
added only after a destruction-safe implementation review; no global mutable
"last caller" and no propagation across asynchronous tasks by assumption. Scope
absence/suppression still means unknown. If context has already cleared its
exclusive tab, do not substitute an unrelated active tab to authorize a log.

JNI design candidate: typed fixed integer enum and actual Java WebContents
reference, native→Java synchronous static diagnostic reporter in existing
controller. Reporter matches actual live current WebContents/tab then reuses
existing scoped logger. Verify WebContents wrapper identity/conversion API at
the pin BEFORE implementation, and avoid a new content→chrome dependency cycle
(content generic observer route versus existing Android delegate interface needs
separate GN review). EAM/context already depend on chrome_jni_headers, but that
does not authorize adding chrome headers to content. No bridge signature or
generated code has been introduced by this investigation.

Native caller may synchronously destroy WebContents/controller: capture only
local fixed values/Java local references before calls; obtain WeakPtr for any
post-call access and stop if destroyed. Do not retain raw native instance/frame/
tab pointers, create off-thread Java callbacks or access a vanished profile to
complete a return marker. Missing return can mean teardown/filtering, not proof
of a crash or asynchronous completion. Keep existing null/ownership CHECKs.

Before adoption: verify pinned header APIs and JNI type generation, Android-only
build guards/dependencies, actual saved Ninja source/rule/toolchain for each
object (no guessed object names), real chrome_java/NullAway and affected native
object compilation, then APK integration. Existing43-file helper does NOT
authorize these extra files. A future selection/provenance/backup transaction
must start from actually built Forward evidence, not AOrigin/A/installed.

## Verification / untouched scope

Fixed EAM9-file hash/call-edge audit PASS, including drift rejection. Earlier
6-file external trace and existing67 tests/actionlint/diff checks are separately
rerun. This is bounded source/fixture verification; native JNI generation,
Java/NullAway/native compile and a new device fix are unverified. No product,
manifest, old helper, B, identity, signing, Secrets or runner change is made.
No saved-tree access/apply/build, Actions, GN/sync/clean/reset, merge, Release or
tag is performed. Full original user log and visible result are both retained.
