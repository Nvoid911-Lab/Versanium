# Configuration A PiP origin investigation — 2026-10-24 JST

## New user evidence supersedes old uncertainty for these A trials

The checkpoint reports successful A apply/recheck, chrome_java/APK compilation,
same-certificate signing and installation. Distribution:
Versanium-156.0.8078.47_Test_ConfigA.apk SHA256
`4cae439199baa0e995cf0fc54c0e67379f7b91de191af2e5b9df2c99b5c18317`.
Evidence `/home/takuma/versanium/config-a-evidence-SaxHs9`. Java controller hash
`5e485b0002d6d78b05e8ebb2c24e9f9b61406bc4833ba925528a02a62ef592a4`.
The user confirms all-flags-OFF launch/playback, with tab stopping, absent PiP
and zoom-linked video size still present. A includes no B zoom candidate.

For the two new log posts, smartphone/YouTube100%, diagnosis/background ON and
restart after settings were the instructed conditions. The posts themselves do
not directly re-report every operation, visible outcome, restart or crash
absence. Different PIDs support separate processes, not full procedural proof.
Earlier Diagnostic APK's directly reported outcomes/restarts remain separate
historical evidence. Do not request repeating these A trials merely to analyze
the logs. Full supplied stage logs are retained in `config-a-pip-device.log`.

### ① PiP candidate OFF: video permission failure, not no fullscreen

19:32:21.627 effective_fullscreen_true → decision_video_disallows.
19:32:28.432 decision_video_disallows → attempt_blocked. In the applied code,
active-effectively-fullscreen passed and the fullscreen-video PiP permission
getter returned false. This is NOT Android app permission denial. At28.514
dismiss6 and28.515 dismiss_inactive6 follow; no entry in this log range. It is
not an entered PiP being closed. HTML disablePictureInPicture, candidate execution,
renderer availability and permission-state updates still need causal evidence.

### ② PiP candidate ON: real exit action and real SYSTEM suspend call

| Time | Relative to entry | Confirmed stage |
|---|---:|---|
|19:34:29.365|0ms|framework_entered, persistent_video_request|
|19:34:29.367|2ms|persistent_video_returned (Java call returned, not renderer completion)|
|19:34:29.385|20ms|effective_fullscreen_true|
|19:34:29.387|22ms|auto_allowed|
|19:34:29.425|60ms|dismiss6, no_active_fullscreen, auto_blocked|
|19:34:29.426|61ms|dismiss_move_request6|
|19:34:29.427|62ms|dismiss_move_true6|
|19:34:29.511|146ms|effective_fullscreen_false, dismiss7, dismiss_inactive7|
|19:34:29.560|195ms|stop_suspend, stop_suspend_called|
|19:34:29.587|222ms|media_stopped|
|19:34:29.635|270ms|framework_exited|

Here moveTaskToBack(true) returned true, followed by the controller's cleanup
path. reason7 encountered an already inactive app-side session and did not cause
the first real exit in this sequence. stop_suspend_called is emitted only after
non-null session + playing passed and MediaSession.suspend(SYSTEM) returned.
The earlier report's uncertainty about actual calls is resolved FOR THIS trial.
Later media_stopped is observed; the log does not uniquely attribute all stop
causality or identify the first fullscreen-exit requester.

At60ms the fixed50ms grace period had elapsed. Extending that time would defer
the same request without distinguishing user exit from PiP transition. Candidate
ON now correlates with passing eligibility/entry versus OFF's permission denial;
do not call it globally ineffective. Combined flags/site state are not an
isolated experiment proving the precise HTML attribute mechanism.

## Fixed156 source trace of reason6

All references below are at Chromium
`1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775`, not latest main.

- `ChromeActivity.onPictureInPictureModeChanged(true)` invokes the PiP controller.
  `setHasPersistentVideo` reaches WebContentsAndroid/WebContentsImpl → observer
  RequestPersistentVideo → renderer SetPersistentState. Blink video updates
  persistent classes/display type; asynchronous layout/media/site reactions can
  occur after the returned marker. Returned is not completion.
- BrowserControlsManager uses FullscreenHtmlApiHandlerFactory. Factory chooses
  Compat when FullscreenInsetsApiMigration is enabled (or automotive migration),
  otherwise Legacy. Both share FullscreenHtmlApiHandlerBase; neither subclass
  overrides its onExitFullscreen or Activity/multiwindow request paths.
- Base.onExitFullscreen accepts the active/fullscreen tab, invokes
  exitPersistentFullscreenMode, and emits observer.onExitFullscreen when prior
  persistent mode or notify-on-next-exit warrants it. The PiP observer then
  invokes dismiss with LEFT_FULLSCREEN=6. Reason6 therefore identifies the
  notification, not its requesting source. TabWebContentsDelegateAndroidImpl
  exitFullscreenModeForTab merely forwards to its supplied delegate; external
  browser/renderer/UI paths are not distinguished by current logs.
- Base's local origins include tab onHidden(null request), destroyed current
  fullscreen tab, non-same-document active primary navigation, Activity STOPPED
  when mExitFullscreenOnStop is true, and multiwindow handling. Delegate may be
  replaced through setFullscreenManagerDelegate, so a local request is not proof
  of immediate synchronous observer dispatch. Native/user/browser paths can also
  enter onExitFullscreen directly.
- Existing multiwindow PiP guard runs only inside
  isDisplayEdgeToEdgeFullscreenFeatureEnabledOn2DDevice() AND
  !sEnableExclusiveAccessManager.isEnabled(). It requests exit only with tab,
  !Activity.isInPictureInPictureMode(), previous !multiwindow and incoming
  multiwindow. It does NOT blanket-protect tab-hidden/navigation/STOPPED or
  external requests. The user's device feature values/selected implementation
  are not known from supplied stage logs or candidate settings.
- Browser fullscreen change may trigger renderer effective-fullscreen loss, but
  the permission/active state is already false when dismiss6 updates auto-PiP
  at29.425; reason7 callback arrives later. This is compatible with asynchronous
  state propagation, not proof that reason7 caused reason6. Activity STOPPED may
  initiate fullscreen cleanup, or may follow the move-to-back; its position is
  not independently logged at that earlier source yet.

The first request source is still unproven. A normal PiP-induced layout change,
YouTube response and real user/navigation/lifecycle exit cannot yet be safely
separated. No unconditional reason6/7 ignore, grace extension, onStop bypass,
forced resume/play loop or permission relaxation is implemented.

## Limited diagnostic candidate: fixed source labels at real request sites

New `apply_fullscreen_origin.py` injects only fixed-label logging calls into the
existing Base handler source. No condition or behavior statement is replaced.
Labels cover:

- origin6_multiwindow_callback / feature_branch / guard_passed;
- origin6_tab_provider_change, tab_hidden, tab_destroyed, primary_navigation;
- origin6_activity_stopped_request;
- origin6_accepted_on_exit, exit_persistent_entry, notify_exit_observer.

The multiwindow guard-passed marker means all EXISTING conditions passed at that
request. The callback marker alone does not. No extra feature/PiP/permission
getter or eligibility call is made. Dispatcher labels localize external requests
when no local request label precedes them, but cannot identify an uninstrumented
native/user caller or prove that a filtered marker never occurred.

The PiP controller provides a static bridge used by the existing Base class.
It looks up the existing controller and requires the event tab to be the current
live non-private tab before delegating to the existing diagnosis/HTTPS exact
YouTube logger. Null/mismatched/private/destroyed tabs safely emit nothing.
For lifecycle events without a tab parameter, the current fullscreen/active tab
is used; tab-specific callbacks pass their actual event tab. No stack trace,
URLs, title, settings dump, feature values, tab/player IDs or arbitrary page text
are logged. Missing/filtered stages do not prove absent events. Existing logger
Activity teardown and normal-profile gates remain unchanged.

Both modified Java classes are listed in fixed chrome/android/chrome_java_sources.gni,
consumed by //chrome/android:chrome_java. The existing separate fullscreen:java
target provides the interface, not this Base implementation. No GN dependency,
resource, JNI API/generation target or new compiled Java source is introduced.
Full Java/NullAway integration is still unverified. No C++ changes are included
in this diagnostic candidate; the prior unbuilt B native changes remain in the
review branch but are NOT applied to saved A or validated by its logs.

Selected output identification (not installed-device hashes): Base handler
`ec1fcc104a40232af1fea47b59e0998571ec51c0c53bc91734d454394a9c3218`,
PiP controller
`ad3efea4a6b741de0816240ac87c4f0784dd4b1fb77c396be9ad67f4822366b7`.
The new applicator script must be included in any future controller/input
provenance review alongside the two resulting Java files; the original saved
recorder/application evidence is preserved, not rewritten as if this were A.

## Verification and build boundary

Fixed Base source SHA256 f14c40e9046171345d2db39ba8c32c7317a3ebe5652cbf78e6f8e2d43e0c2926.
Selected Vanadium does not patch these handler files. Tests remove all injected
fixed-label statements and require byte equality with the original Base,
reject repeated/changed anchors, and compile/run the actual transformed
multiwindow method across64 Java-double cases plus actual bridge6 scope cases.
Existing getter counts and exit-state updates are unchanged. Logger9,
decision/dismiss15, native17 MODEL, DOM37 MODEL and B zoom67 MODEL checks PASS.
Existing migration/recovery/preparation55 tests, actionlint, shell/diff checks
also PASS; the selected-source negative anchor test emits an expected patch error.
These are bounded source/model/Java-double checks, not Android/Chromium native
integration or device success of the new origin candidate.

No saved Run9 access/apply, build/Actions, GN/sync/clean/reset/move, merge,
Release/tag or signing operation occurred. Old one-/four-file apply controllers
and their selection manifests remain unchanged; they must not be relaxed or
used for this new two-Java-file origin diagnostic. Before any separately
authorized future Test, review a new A-plus-origin selection/provenance path and
refresh the information source. Keep B deferred. No repeat of the currently
installed APK is needed to interpret the supplied logs.
