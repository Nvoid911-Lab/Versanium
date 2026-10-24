# Smartphone PiP comparison — 2026-10-24 JST

Historical Diagnostic-APK comparison below remains intact. New ConfigA logs
confirm real reason6 moveTaskToBack(true) success and later returned SYSTEM
suspend for the ON trial, and video permission denial for OFF. See
[ConfigA source-origin follow-up](config-a-pip-origin-review.md). Earlier
uncertainty about actual calls applies only to the old log range, not new A.

These are user-provided results/logs from the installed Diagnostic APK, NOT the
unbuilt video-fullscreen-zoom candidate at3452edd. Both conditions use Galaxy S23
phone display, YouTube zoom100%, diagnostics ON and background candidate ON.
The user reports restarting after each configuration change; no additional
restart confirmation is required or independently established here. Video ID,
exact Android callback source and page event traces were not supplied.

| Condition | PiP candidate OFF | PiP candidate ON |
|---|---|---|
| Video fullscreen → home | Audio continues; no PiP displayed | PiP appears briefly, closes, playback stops |
| Tab switch | Playback continues | Playback continues |
| Non-fullscreen → home | Not reported in this comparison | Playback continues; no PiP |
| Manual pause | Remains paused | Remains paused |
| Crash | None reported | None reported |

## Condition1 — start eligibility failed, not a proven entered-then-closed session

All records have inPip=false/changing=false:

```text
15:55:32.421 resume / dismiss_0 / auto_blocked
15:55:35.105 dismiss_7 / auto_blocked
15:55:38.764 attempt_blocked
15:55:38.848 dismiss_6 / auto_blocked
```

There is no entry-success record in this range. Reason7 denotes the effective
video fullscreen observer's false callback; reason6 denotes the FullscreenManager
exit callback. They also run while no PiP session exists. Neither record alone
proves a PiP close. canDoPictureInPicture tests active fullscreen, then video
permission, device support, optionally current PiP, Activity reconfiguration,
finishing and recent-task exclusions. The existing blocked record does not
identify the false branch. changing=false excludes only the logged Activity
state at log time; it does not establish every other test's result. In particular,
reason7 suggests a lost effective-fullscreen state, but its earlier timestamp
does not prove the exact reason at the later attempt. A permission denial is also
possible. New branch records below distinguish these without extra queries.

## Condition2 — framework entry confirmed, followed by fullscreen loss and exit

All changing=false; inPip values are preserved below:

```text
18:00:22.950 resume inPip=false
18:00:22.950 dismiss_0 inPip=false
18:00:22.950 auto_blocked inPip=false
18:00:24.403 auto_allowed inPip=false
18:00:24.419 dismiss_7 inPip=false
18:00:24.419 auto_blocked inPip=false
18:00:24.519 auto_allowed inPip=false
18:00:28.020 framework_entered inPip=true
18:00:28.104 auto_allowed inPip=true
18:00:28.108 dismiss_6 inPip=true
18:00:28.108 auto_blocked inPip=true
18:00:28.201 dismiss_7 inPip=true
18:00:28.201 auto_blocked inPip=true
18:00:28.348 stop_suspend inPip=true
18:00:28.394 framework_exited inPip=false
18:00:28.605 auto_blocked inPip=false
```

Relative to framework_entered: dismiss6 +88ms, dismiss7 +181ms, stop_suspend
+328ms, framework_exited +374ms. Entry is confirmed by the Activity callback;
completion of controller setup is not guaranteed by its first log alone. The
candidate ON condition changes observed eligibility/entry in this combined setup.
Do not summarize it as "PiP candidate ineffective". This comparison is not an
isolated proof of the DOM attribute's precise causal contribution.

## Applied fixed156 code trace and causal limits

Sources are the exact pin1d17a2e, selected Vanadium overlays and applied diagnostic
patch (same controller behavior as the installed60b0037 product code):

- ChromeActivity.onPictureInPictureModeChanged(true) invokes the controller.
  The controller logs framework_entered, then obtains tab/WebContents, calls
  setHasPersistentVideo(true), installs exit callbacks/observers and sets
  mShouldSuspendMediaOnStop=true. Its startup log precedes those actions.
- WebContentsAndroid → WebContentsImpl.SetHasPersistentVideo sets preferences,
  calls MediaWebContentsObserver.RequestPersistentVideo, and updates the view.
  RequestPersistentVideo sends SetPersistentState only if a fullscreen player
  exists. Blink HTMLVideoElement.SetPersistentStateInternal marks the video/
  ancestors persistent and changes display type; it does not explicitly request
  DOM fullscreen exit here. A layout/media-state reaction or YouTube script is
  possible, not demonstrated. New persistent request/returned markers bracket
  this real call; no duplicate call is made for diagnosis.
- BrowserControlsManager supplies FullscreenHtmlApiHandlerBase through its
  factory. Its onExitFullscreen forwards observer callbacks (reason6) after
  exiting persistent fullscreen. Potential origins include hidden/destroyed tab,
  primary navigation, Activity STOPPED with exit-on-stop, DOM/browser requests,
  and multiwindow changes. The multiwindow observer has a conditional existing
  guard against exiting while Activity.isInPictureInPictureMode(); feature and
  callback ordering matter. It is not valid to assume any fullscreen exit is
  harmless PiP housekeeping, or that this guard was active on this phone.
- MediaWebContentsObserver.OnMediaEffectivelyFullscreenChanged resets its ID/
  permission on kNotEffectivelyFullscreen and notifies WebContents observers
  (reason7). This reports renderer media classification, not a direct user-exit
  intent. It may follow a DOM/viewport/video layout change.
- Both callbacks call dismissActivityIfNeeded. It logs BEFORE checking session
  activity, then recalculates auto-PiP through the existing single call, and
  returns if no app session. An active session is deferred only during the first
  50ms. At +88ms that protection has elapsed. If interactive it calls
  moveTaskToBack(true), then session cleanup regardless of the boolean result;
  screen-off takes a deferred/suspension path. Thus fullscreen notifications can
  initiate exit here, but old dismiss6/7 logs do not prove which branch ran.
- ChromeActivity.onStopWithNative calls controller.onStop. Old stop_suspend
  only establishes the outer should-suspend flag. The actual SYSTEM suspend
  additionally requires a non-null MediaSession AND mIsPlaying. No old log proves
  those conditions or completion. framework_exited proves the later Android
  mode-change callback. No resume record after entry appears in the supplied
  range; that does not prove no other lifecycle event occurred outside the range.

The earliest trigger of fullscreen loss remains unconfirmed. Android viewport/
multiwindow transition, Blink persistent-video relayout, browser fullscreen
policy and YouTube reaction remain distinct hypotheses. Do not substitute log
ordering for a stack or causal trace.

## Narrow diagnostic change, not an exit-policy repair

The patch adds records only inside the actual existing decision branches:
decision_no_active_fullscreen, decision_video_disallows, device_unsupported,
already_in_pip, changing, finishing, recent_task and no_contents. The former
short-circuit expression is split into equivalent consecutive checks: the
permission getter still runs exactly once and ONLY after active fullscreen
passes. No diagnostic invocation of canDoPictureInPicture or permission getter
is added. Private/non-YouTube/destroyed contexts still do not emit logs; therefore
no_contents/finishing can be suppressed by the existing logger safety gates.

Additional stage records distinguish persistent-video request/return, inactive
dismiss, deferred dismiss, move request/boolean return, screen-off dismissal,
effective fullscreen and media started/stopped. stop_suspend_called is emitted
AFTER the actual suspend returns; stop_no_session/stop_not_playing records the
other branches. Existing stop_suspend retains its original pre-call meaning.
Deduplication/safety gates remain, so missing stages alone are not proof of no
event. No URLs, titles, task/component names, configuration, video IDs, exception
messages or player IDs are logged. Java threadtime timestamps provide timing.

No fullscreen dismissal or onStop suppression is implemented. User exits,
tab close, navigation, reparenting and Activity return can all use these paths;
the present logs cannot reliably classify an entry-induced transition. A future
bounded repair would need same-tab/session identity and a verified transition
reason, not just elapsed time or inPip=true. A fixed grace-period increase or
unconditional ignore6/7 would hide user intent and real navigations. Preserve
background tab playback, manual pause, DeX/Twitch/private behavior and no play()
loop/autoplay bypass.

## Zoom work retained

The zoom patch at3452edd is byte-preserved. Its selected-source rendering67
model and persistence checks remain separate. These device logs came from the
earlier Diagnostic APK before the zoom candidate was built, so the new zoom
override cannot explain them. A shared upstream sizing/transition cause is not
proven. The unbuilt zoom candidate's fullscreen-ID reset and UpdateZoom may
interact with PiP layout; this is an explicit future device comparison risk.
Do not call video sizing or PiP solved.

## Verification and next comparison

Actual applied decision/dismiss Java methods compiled/run using ECJ with doubles:
15 branch cases, including guarded getter counts, inactive/deferred/interactive/
screen-off dismissal and unchanged ignored move return behavior. Existing safe
logger9 cases, selected156 integration, native scope17 MODEL, DOM37 MODEL,
video zoom67 MODEL and migration/recovery47 checks PASS. These do not establish
real Android/Chromium integration or device success of the new instrumentation.

On a later separately reviewed/authorized Test APK, repeat the two conditions
independently with reported restart, video fullscreen/inline and zoom100%.
Capture only cr_VersaniumPiP/VersaniumPiP stage records from immediately before
home through exit, and note manual pause/tab-switch behavior. Seek the first
decision failure for OFF; for ON seek persistent markers, exact dismiss branch,
actual suspend completion and framework exit. DeX, other sites and video zoom
acceptance remain separate. No need to repeat the old crashing APK or clear data.
The existing four-file update controller is not applicable to this expanded
patch; its conditions are unchanged. No Actions/build, saved-tree apply,
clean/reset/GN/sync/move, merge, Release/tag or key change occurred here.
