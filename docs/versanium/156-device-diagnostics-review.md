# 156 device follow-up — 2026-10-24 JST

## Evidence and build identity

User-supplied Versanium-Context_v1.9.md sections17–18 supersede earlier unbuilt/unverified Run9 status. User reports successful real RFH object and incremental APK compilation, signing with the existing key, and installation on Galaxy S23 / Android16 / OneUI8.5. Signed Versanium-156.0.8078.47_Test.apk SHA256: `87c5b11aea148856f13cc7aab46a5ac1d2b4a0590ae068c19a2e7a52fa5837cf`. This is a manual recovery of repository7d9102f with the host() correction using controllerebfc81c; it is not a full build of all future controller code. Original Actions Run39951209951 remains failure. No new artifact/Release/tag was created by this work.

Reported normal: branding/F11, environment zoom, export/import, restart persistence, displayed upstream version. Data deletion/reinstallation was used to recover the diagnosis crash; this does NOT demonstrate preservation during an untouched155 upgrade. Default mobile YouTube still fails PiP/tab playback; default DeX works. Diagnostics alone crashes both displays and loops on restart. PiP candidate alone (diagnostics OFF) has no improvement. Background candidate alone (diagnostics OFF) preserves tab playback, but home PiP appears then closes and playback stops. Fullscreen/inline, precise timing and exception/stack were not supplied. Do not infer them.

## Concrete defect and bounded correction

Pinned Chromium1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775:

- [MediaWebContentsObserver](https://github.com/chromium/chromium/blob/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/content/browser/media/media_web_contents_observer.cc#L321) `IsPictureInPictureAllowedForFullscreenVideo()` requires UI thread and CHECKs `fullscreen_player_.has_value()` and `picture_in_picture_allowed_in_fullscreen_.has_value()`. Retrieved file SHA256 `28ec2033b17901278ecd73f5a09ac8f1956ab49eeec1582f716ec085d01196b8`.
- WebContentsImpl forwards the permission query to that observer. The upstream Java controller `canDoPictureInPicture` short-circuits on `hasActiveEffectivelyFullscreenVideo()` first. Our diagnostic string instead called the permission getter unconditionally, including auto_blocked/resume/exit events. No catch in Java can make a native CHECK safe.
- This establishes a reachable invalid diagnostic query, compatible with the report, **not the root cause of the user's crash without its CHECK/stack**. No new crash record was supplied or accessed. Other lifecycle/JS causes are not excluded by static review.

The correction removes fullscreen/permission, AppOps and recent-task probes from the logger. It records only stages already chosen by the controller and Activity inPiP/changing booleans. Existing initialized-library, HTTPS exact YouTube host, regular/live-tab/WebContents gates remain; destroyed/finishing Activity is rejected. No extra PiP decision calls, broad catch, native CHECK removal or playback command is added. Log format is a fixed `%s` with a fixed stage/boolean record, not page text. Existing UI controller hooks remain synchronous; no new worker or observer is introduced.

Diagnostics no longer authorizes TabImpl load/show/hide/environment candidate injection or the native scope. Candidate calls have a null result callback, removing diagnosis-only JSON callbacks and their asynchronous lifecycle. The compiled payload always receives diagnostics=false, including when candidates and diagnostics are both enabled, so diagnosis cannot wrap page pause(). Fixed-code JNI and both native frame/profile/flag gates remain; generic JavaScript permissions remain upstream. The background/PiP DOM implementation is byte-identical to ebfc81c. Its existing play/pause/visibility listeners remain candidate behavior, not enabled by diagnosis alone. No automatic play or additional observer is added. Environment listeners are registered only for an actual candidate.

Recovery direction: an eventual update with the same package/key can avoid the identified getter even if the diagnostics switch was persisted, without clearing data. This is an implementation property awaiting APK/device verification, not a tested recovery recipe. Do NOT ask the user to enable diagnosis on the currently installed affected APK, reproduce the loop, delete data or reinstall again.

## PiP flash/close is a separate unresolved path

Pinned controller source permits only active effectively fullscreen video plus video permission; clearing HTML disablePictureInPicture cannot satisfy those native conditions or Android permission/transition by itself. The user's fullscreen/inline state is unknown, so candidate C does not establish attribute execution/failure or a native-entry cause.

Background candidate alters playing-document hidden/visibility delivery; it does not keep native fullscreen or MediaSession/Activity alive. Source-defined exit routes include:

- `hasEffectivelyFullscreenVideoChange(false)` → dismiss reason7; tab fullscreen exit reason6; tab switch4, reparent5, close2, crash3, start8.
- `onResume()` clears suspend-on-stop and unconditionally exits the PiP session with resume reason0.
- `onEnteredPictureInPictureMode()` sets suspend-on-stop. Later `onStop()`, if that flag and playing are true, requests MediaSession SYSTEM suspension.
- `dismissActivityIfNeeded()` may defer by the minimum-exit interval, then move the task back/exit; screen-off path suspends media. `mediaStoppedPlaying()` updates auto-PiP/playing state but explicitly does not itself dismiss active PiP.

The current code logs decision/entry/exit/dismiss/stop_suspend stages. These distinguish an entry refusal from an entered session subsequently dismissed. They do not establish whether YouTube paused first, native fullscreen was lost first, or Android resumed/stopped first. No measured order/stack exists. Do not disable onStop suspension, force fullscreen, suppress all dismissal, resume manual pauses or add autoplay/play loops on this evidence. No PiP-exit behavior change is included in this correction.

## Local verification and limits

- Exact156 + selectedVanadium/F11/zoom/SAF/PiP patch application PASS. Expected changed-anchor negative test emits a patch error. Generic JS body equality retained.
- Corrected native scope:17 C++ model checks PASS, including diagnosis-only rejection. Not a Chromium translation-unit compile.
- Actual added Java logger method extracted from applied source:9 cases compiled/run with Java doubles using existing ECJ, covering flag/private/destroyed/finishing/scheme/host/dedup. Doubles intentionally lack unsafe permission/task/AppOps APIs. NOT Android/NullAway/JNI integration or a device test. System javac was unavailable; ECJ was used.
- Unchanged DOM candidate:37 model checks PASS; not real playback. Migration/recovery39 tests PASS. Historical Run9 exact-patch test now explicitly uses controllerebfc81c, not future incompatible changes.
- actionlint, YAML/inline shell, bash syntax and git diff checks PASS. No full Chromium build, saved-host apply, Actions or device operation.

**Do not use the Run9 three-token recovery helper for this change.** Its strict controller/diff guards intentionally reject this wider correction; they were not relaxed. Saved Run9 source/out/Ninja/Siso remain untouched. A subsequent reviewed build path and refreshed information-source snapshot are prerequisites.

## Safe next comparison after a separately authorized fixed Test APK

Keep diagnosis OFF for normal acceptance first. Compare defaults vs background-only on the same video, recording mobile/DeX and inline/fullscreen explicitly; test tab switch and home separately, plus manual pause (must stay paused). Check F11, zoom/backup/restart, Twitch, private and same-document mobile→DeX→mobile. PiP-only is a separate test, not all flags together.

Only after the corrected APK is built/reviewed and safe startup is established, optionally collect a short diagnostic-only sample; do not repeat on the affected APK. From an already working rish shell, `logcat -b main -v threadtime -s cr_VersaniumPiP:I VersaniumPiP:I '*:S'` displays only our stage records (Chromium Log adds the cr_ prefix). Record the brief interval from home to exit and stop collection. Share only stage/boolean lines and the explicit test conditions; no URL/title/Cookie/config dump. Existing crash evidence, if already available, should be restricted locally to exception/CHECK and relevant stack with account/URL/path details removed. No broad log dump or new unsafe reproduction is required. This logging procedure is not device-verified.
