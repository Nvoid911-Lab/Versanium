# Correlated PiP permission and first-pause diagnostics

2026-10-29 JST. Diagnostic implementation only. NEXT=WAIT_FOR_CHATGPT_REVIEW.

## Scope and status

Start `b66a18b035209265162637619744b8dbf0c0a001`, branch
`next-test/156-zoom-transfer-pip`, Primary fetch/local exact match. Diagnostic
startup fix3ce5aac remains included. PR5 stays Open/Draft/unmerged, body read-only.
Native source baseline: Chromium1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775;
Vanadium2ae4335402eabcc6e025f3400185fe25094d8521; Titanium156.0.8078.47.

This commit packages logging for the future reviewed diagnostic build. It does
not apply new source into the existing fresh Chromium workspace. Existing fresh
source/out/args and its preexisting Controller Vanadium helper modification are
preserved. Native `git apply --check` on fresh source passed; that is not an apply,
GN generation or native compilation. No saved workspace or old generator used.

PHASE1_BUILD=PASS is the previous APK's historical result. The user's same-S23,
same-APK MOBILE_DEVICE_TEST=FAIL and DESKTOP_CONTROL_TEST=PASS remain:
mobile fullscreen=true/allowed=false/upstream=false; desktop fullscreen=true/
allowed=true/upstream=true/frameworkPiP=true. New diagnostics have not been built
or device-tested. Attribute setter and first pause root cause remain UNCONFIRMED.

## Implementation and correlation

| Event | Actual observation point | Identity / interpretation |
|---|---|---|
| MEDIA_PLAYER_BOUND | HTMLMediaElement, after existing OnMediaPlayerAdded registration | Frame token + native player ID + navigation document token; captures replacement even without fullscreen |
| PIP_PERMISSION_PRODUCER | HTMLVideoElement::SetIsEffectivelyFullscreen, immediately before existing observer loop | Existing enum + actual disablepictureinpicture presence + fullscreen + main-frame flag |
| MEDIA_PLAYER_BOUND_RECEIVED | MediaWebContentsObserver::OnMediaPlayerAdded, after original validity rejection | Same player, browser frame token, RFH route and owning WC main RFH |
| PIP_PERMISSION_RECEIVED | MediaWebContentsObserver after original fullscreen status switch/storage, before fullscreen callback | Actual stored allowed, received status and matching fullscreen player |
| WEB_CONTENTS_VISIBILITY | WebContentsAndroid::UpdateWebContentsVisibility, before existing call | Old and requested visibility + WC main RFH; request marker, not renderer acknowledgement |
| MEDIA_PLAYER_VISIBILITY | WebMediaPlayerImpl::OnPageHidden / OnPageShown | Actual renderer callback, player ID + page-hidden flag |
| MEDIA_PAUSE_REQUEST | HTMLMediaElement::PauseInternal, before any original action and while !paused_ | Common DOM/policy/browser pause ingress, existing PauseReason, document/frame/player and hidden state |
| MEDIA_PAUSE_REQUEST | WebMediaPlayerImpl::PauseVideoIfNeeded, immediately before client PausePlayback | Actual hidden-policy request, PauseReason and existing background/hidden flags |
| MEDIA_PAUSE_REQUEST | MediaSessionController::OnSuspend, before existing remote RequestPause | Actual browser session-to-player request, native player/frame ID and user-triggered flag |
| MEDIA_PAUSE_APPLY | WebMediaPlayerImpl::Pause while running, before original state mutation | Low-level application marker, same existing PauseReason |
| MEDIA_PAUSED_RECEIVED / MEDIA_PLAYING_RECEIVED | Existing browser player notification paths | Paused notification before SetIsStopped / session OnPause, so distinguish downstream result |
| MEDIA_SESSION_SUSPEND | MediaSessionImpl::OnSuspendInternal after existing early-return guards, before state mutation | Existing SuspendType/new_state, WC main RFH and content_already_paused |

Producer logging is at the real enum sender downstream of
MediaCustomControlsFullscreenDetector::ReportEffectivelyFullscreen. The detector's
attribute-derived calculation and all observer transport calls remain unchanged.
Its synchronous sender reads attribute presence; no script runs or attribute is
modified by the added observation. No fake producer function replaces the real
path. There is no separate PIP_PERMISSION_CHANGED state machine: producer logs
on changed `(player,status)` using two logging-only integer fields. Receiver uses
its existing player/optional-bool state to suppress equal-status repeats. An
unrelated not-fullscreen status rejected by the original return remains rejected.

Use `(frame token, player)` to join renderer producer to browser receiver.
`MEDIA_PLAYER_BOUND` maps renderer PID-local low-level player events to that pair.
Browser receiver records `rfh_child/rfh_route` and `wc_main_child/wc_main_route`;
Java diagnosticPageFields now includes that **existing main RFH global ID** beside
sourceTab/desktop_site/visibility/media fields. Existing Java MEDIA_STARTED/MEDIA_STOPPED now also retain callback player ID
(the native proxy already passes id.player_id). No new JNI method or transport was
added. RFH route alone is not a document ID; renderer document token distinguishes
reload/new-document samples. Browser document=unknown deliberately avoids the
browser document getter's pending/speculative CHECK preconditions.

Player IDs are Chromium media player IDs, not media-session-controller local IDs
or OS PIDs. Frame/document tokens are opaque lifetime identifiers, not URLs,
account data or pointers. WC main global IDs connect subframe players to the
owning Java tab while frame token retains actual player frame identity. Native
events have tick_us from TimeTicks plus normal logcat PID/TID/timestamp. Existing
Java seq is process-local; do not interpret it as a cross-process total sequence.
Use shared logcat timestamps and native tick_us with explicit IPC identities.

## Log format and volume

Java keeps tag VersaniumPiP (normally cr_VersaniumPiP on Android). Native uses
Chromium `LOG(INFO)` and message `VSPIP event=...`; its platform tag may be
chromium. Collect **all VSPIP messages**, not only the Java tag, and preserve
timestamp/PID/TID. No log collection/ADB command was executed here.

Native observations are Android-only and intentionally symmetric for mobile and
desktop. They do not use a mobile-host behavior gate; native media metadata is
observed for other Android media too, without URL/content. Java still supplies
the existing safe URL classification and desktop-site state for the test cases.
No query/video ID/title/account/cookie/token payload, markup, script or UA string
is added. The frame/document opaque tokens are correlation IDs, not credentials.

No frame/timeupdate callback logs. Permission logs deduplicate player/status;
pause ingress/application logs only requests while running, visibility requests
only changed values, renderer visibility callbacks already follow delegate state
transitions, and binding/media/session logs follow lifecycle notifications. Two
integer fields deduplicate logging only; neither participates in product policy.
Normal logging overhead exists; this remains an unbuilt diagnostic package.

## Expected comparison (hypotheses, not new observations)

Permission, mobile:
MEDIA_PLAYER_BOUND -> PIP_PERMISSION_PRODUCER(disable=true,status=disabled)
-> PIP_PERMISSION_RECEIVED(allowed=false) -> Java fullscreenPipAllowed=false
-> upstream rejection. Desktop should instead show disable=false/status=enabled
-> received true -> upstream eligible -> existing framework PiP. If this does not
match, retain the actual player/document identity and timing; do not force the
expected explanation. Cached browser permission can lag DOM changes.

Tab switch, both cases:
existing TAB_UNSELECTED / TAB_SELECTED / outgoing TAB_HIDDEN and WC_VISIBILITY -> native visibility
request -> renderer MEDIA_PLAYER_VISIBILITY -> either continuing playback or
first pause request -> pause apply -> browser paused result -> Java MEDIA_STOPPED
/ MEDIA_SESSION. These are the existing Java callback event names;
correlate them with the native request and renderer-delivery markers.
Java onHidden logging and cross-process visibility delivery may interleave; this
is a causal comparison plan, not a promise of strict text ordering across threads.

Interpret earliest matching request, not latest session callback:

- PauseReason kPageHidden/kFrameHidden with the policy request identifies renderer
  hidden policy. Inspect logged page/frame/background flags.
- kPauseCalled identifies HTMLMediaElement::pause ingress; it does not identify
  a particular YouTube JavaScript or prove script versus native controls.
- Browser MediaSessionController request plus kPauseRequestedByUser/Internally
  identifies session-to-player IPC. The preceding native session event gives
  SuspendType. CONTENT is already-paused result, not a new pause request.
- MEDIA_PAUSE_APPLY without an earlier captured request, missing identity or log
  loss is inconclusive for the first requester; do not manufacture causality.

Pinned WebMediaPlayer::PauseReason integer values:
0 kPageHidden; 1 kFrameFrozen; 2 kFrameHidden; 3 kSuspendedPlayerIdleTimeout;
4 kRemotePlayStateChange; 5 kEndOfPlayback; 6 kPauseCalled;
7 kPauseRequestedByUser; 8 kPauseRequestedInternally; 9 kRemovedFromDocument;
10 kAutoplayAutoPause. SuspendType:0 kSystem,1 kUI,2 kContent. These are existing
enum values, not guessed TAB_HIDE/SITE classifications inserted into decisions.

## Unsafe-getter and behavior review

- Existing Java wc null/destroyed guard and active-fullscreen short-circuit remain
  byte-for-byte. No new permission getter call, native CHECK weakening or fallback.
- Java getMainFrame uses the existing live-WebContents API, then null-guards its
  result; global RFH ID is cached Java data. Startup/non-native/destroyed fixtures
  verify no new RFH read in those cases. Null frame/ID yields -1 sentinels.
- Browser FromID is null-checked for token reads. GetFrameToken is a stored token,
  not GetDocumentToken; no new media-player lookup or fullscreen-player accessor.
  Cache fields are read after existing UI-thread/check guards, optional access is
  short-circuited, and logging precedes callbacks that can destroy owners.
- Renderer Document::Token can allocate lazily for non-navigation documents.
  Therefore the log calls it only for the current frame document with a loader:
  DocumentLoader installs those with WithToken(token_). Detached/non-navigation
  document IDs are unknown. Frame/player nullable values are guarded. Document
  hidden() explicitly handles absent frame/page in the pinned implementation.
- WebMediaPlayer logs follow its existing thread DCHECK. No added async tasks,
  observer, pointer retention, script execution, page/media resume or mutation.
- New native patch is additions-only. Removing marked diagnostic blocks restores
  each of the nine pinned source files byte-for-byte. Original calculations,
  conditions/returns/permission transport/cache writes, eligibility, entry,
  pause and visibility operations are all retained. Only logger dedup fields
  are written by diagnostics. Java changes only diagnostic fields/imports and existing media callback ID fields.
- Existing source lists/BUILD/GN/pins/sign/package/Zoom/F11/branding are untouched.
  Existing files gain Android logging and one protected helper, no new production
  file registration, JNI or component->Chrome dependency. Full compiler/Android
  integration remains unverified because this task prohibits builds.

## Brave read-only comparison

Re-read the same [36838 pin's helper](https://github.com/brave/brave-core/blob/4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2/browser/android/youtube_script_injector/youtube_script_injector_tab_helper.cc),
[native entry helper](https://github.com/brave/brave-core/blob/4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2/android/java/org/chromium/chrome/browser/youtube_script_injector/BraveYouTubeScriptInjectorNativeHelper.java)
and [auto-route rewrite](https://github.com/brave/brave-core/blob/4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2/rewrite/chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java.yaml).
MWEB PiP-blocking configuration script and background visibility supplement run
from document setup; manual fullscreen completion can use independent entry;
normal auto delegation remains after upstream refusal. None is ported here.
YOUTUBE_ATTRIBUTE_SETTER=UNCONFIRMED. FIRST_PAUSE_ROOT_CAUSE=UNCONFIRMED.

## Tests and next-stage boundary

JVM427 (+12 from415) PASS; candidate6 and active-owner24 PASS. Existing diagnostic
startup15 checks retained. Bundle5 PASS; native structural5 PASS (combined10).
Gate-off/default-off fixture PASS (same explicitly disabled-gate run). Parse-only
five composed Java sources PASS. Native structural tests cover exact restoration,
sender/receiver identity/dedup, no unsafe observation/mutation/new JNI/payload,
first-pause ordering and drift failure without partial Java/native writes.
Expected patch errors in negative tests are intentional. These are source/fixture
checks, not actual native/Chromium Java/NullAway compilation or device validation.

Zoom24 canonical Git blobs PASS; retired34 absent. Final clean worktree gate and
normal Primary/Secondary push receipts are in the delivery report. No GN/build/
APK/signing/ADB/device/Actions/saved Run9/merge/release/tag/Production operation.
PR5 remains Open/Draft/unmerged, body unchanged.

The fresh tree already contains Phase1. Do not rerun the fresh installer there:
it now preflights Java hooks and native patch atomically for a fresh installation.
A future reviewed incremental source update needs the native-only patch plus the
diagnostic Policy delta with exact source/hash guards, not whole-Phase1 reapply
or an old Java-only startup build helper. No such apply/build stage is executed.

[Validation hashes](correlated-diagnostics-validation.json).
Source of Truth local Context v1.24 retains all v1.23 history. Commit identity is
the commit containing this document, subject Add correlated diagnostics for
mobile YouTube PiP; exact SHA is in final delivery and local Context after commit.
