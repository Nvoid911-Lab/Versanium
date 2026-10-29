# Fullscreen PiP permission: source trace and mobile/desktop boundary

2026-10-29 JST. Investigation only. No product code, instrumentation or build.

## Result and provenance

SOURCE_TRACE_RESULT=PRODUCER_CONSUMER_CONFIRMED_PAGE_WRITER_AND_FIRST_PAUSE_UNCONFIRMED

Start Controller: `6dd327cfd4daae77272a0e970e760229980a228a`, branch
`next-test/156-zoom-transfer-pip`. Windows Primary, fetched remote and fresh
Controller agree; diagnostic fix `3ce5aac4c370346ee404a6a65e9b94399b89a16c`
is an ancestor. PR5 is Open/Draft/unmerged. No branch switch.
Reviewed Chromium: `1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775`;
fresh patched HEAD: `e76ab5fc518ef2df24519c82cec55427870f8bd4`.
Titanium156.0.8078.47 / Vanadium2ae4335402eabcc6e025f3400185fe25094d8521.

The renderer detector, HTML video/media elements, media Mojo interface, browser
media observer, JNI bridge, renderer background pause implementation and browser
MediaSession files were checked against actual fresh source. Their full-file
SHA256 equals the reviewed Chromium blob. WebContentsImpl C++, TabImpl Java and
upstream Java controller have existing overlays; their relevant methods were read
in the actual source. WebContentsImpl's existing Zoom additions do not replace
the permission getter. See [source hash receipt](fullscreen-pip-source-proof.json).

The 1,316-entry previous post-build inventory matches: 1,314 file hashes and two
inherited directory markers (not recursive content proofs). GN args SHA256 remains
`d2096bdd18bfb10c2edb46ef950864bf917351dd5c7b059921b51e8b8e335cf8`.
Fresh Controller retains its preexisting dirty Vanadium helper; no reset/cleanup.

## Device evidence supplied by the user

These observations are the user's same-Galaxy-S23/same-diagnostic-APK comparison,
not a new device trial or independently replayed raw log capture in this task.

| Field | Mobile m.youtube.com/watch?v=... | Desktop-site www.youtube.com/watch?v=... |
|---|---|---|
| Page/playback/MediaSession/fullscreen detection | PASS | PASS |
| desktop_site | false | true |
| fullscreenVideo | true | true |
| fullscreenPipAllowed | false | true |
| upstreamEligible | false: no_allowed_fullscreen_video | true: eligible |
| Phase1 strict host policy | mobile watch accepted before upstream gate | wrong_host |
| Home | ENTRY_ATTEMPT; ENTRY_SUPPRESSED upstream_ineligible | PIP_MODE_ENTERED; FRAMEWORK_ENTERED |
| frameworkPip | false | true |
| Tab switch | playback stops | playback continues |
| Device outcome | FAIL | PASS |

PHASE1_BUILD=PASS (previous build receipt, not rerun).
MOBILE_DEVICE_TEST=FAIL. DESKTOP_CONTROL_TEST=PASS.
The control falsifies a blanket Android PiP/Manifest/Activity failure hypothesis.
It points to a page/player permission difference for initial entry. It does not
by itself identify the page script, attribute mutation time or first pause cause.

## Producer chain — Q1 and Q2

1. Blink renderer's `MediaCustomControlsFullscreenDetector` observes
   loadedmetadata/fullscreen changes and viewport intersection. It requires the
   video or an ancestor to be the HTML fullscreen element, and sufficient
   intersection/geometry (85% usual case; alternative aspect-ratio heuristic).
   Updates are posted as internal-media tasks, so this is not an atomic Java
   snapshot of the current DOM.
2. `ReportEffectivelyFullscreen(true)` reads exactly
   `!VideoElement().FastHasAttribute(html_names::kDisablepictureinpictureAttr)`.
   It emits `kFullscreenAndPictureInPictureEnabled` when absent and
   `kFullscreenAndPictureInPictureDisabled` when present. Presence is the boolean
   test; an attribute whose text is "false" is still present. False fullscreen
   emits `kNotEffectivelyFullscreen`. [Exact producer](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/third_party/blink/renderer/core/html/media/media_custom_controls_fullscreen_detector.cc#b146).
3. `HTMLVideoElement::SetIsEffectivelyFullscreen(status)` stores a fullscreen
   boolean independent of permission, then forwards the enum to its registered
   `MediaPlayerObserver` associated Mojo remotes and WebMediaPlayer.
   [Renderer sender](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/third_party/blink/renderer/core/html/media/html_video_element.cc#b1164).
4. `HTMLMediaElement` registers its player/observer using
   `MediaPlayerHost.OnMediaPlayerAdded`. Browser `MediaPlayerHostImpl` constructs
   `MediaPlayerId(frame_routing_id_, player_id)`; its observer host retains that
   identity. `OnMediaEffectivelyFullscreenChanged(status)` is a renderer-to-browser
   media Mojo message, not an Android framework permission callback.
   [Mojo contract](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/media/mojo/mojom/media_player.mojom#b86).
5. Browser UI-thread `MediaWebContentsObserver::OnMediaEffectivelyFullscreenChanged`
   receives `(player_id, status)`. Both fullscreen enum cases set
   `fullscreen_player_ = player_id`; enabled sets optional bool
   `picture_in_picture_allowed_in_fullscreen_ = true`, disabled sets false.
   Not-fullscreen resets both only for the matching current player. Player removal
   also clears the stored state. An unrelated player's exit does not clear it.
   [Browser state writer](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/content/browser/media/media_web_contents_observer.cc#b621).
6. `IsPictureInPictureAllowedForFullscreenVideo()` CHECKs that the fullscreen
   player and optional bool exist, then returns that bool unchanged. It does not
   recompute site eligibility or Android capability. The getter must not be called
   without its fullscreen-player precondition (the earlier diagnostic startup
   fix guards this). [Getter and active-fullscreen predicate](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/content/browser/media/media_web_contents_observer.cc#b306).

Ownership: HTML attribute/document in Blink renderer -> per-player media IPC ->
WebContents-owned browser media observer cache -> Java via JNI. MediaSession and
Android do not produce this particular allowed bit.

### Timing and the distinct availability channel

`HTMLVideoElement::AttributeChanged` for disablepictureinpicture invokes
`UpdatePictureInPictureAvailability()` and may exit an existing element PiP.
That sends `OnPictureInPictureAvailabilityChanged(SupportsPictureInPicture())`;
it is distinct from `OnMediaEffectivelyFullscreenChanged(status)`.
The attribute-change handler does not itself assign the browser fullscreen bool.
Consequently the latter means **the last fullscreen status received for the
selected player**, not a guaranteed current-DOM attribute read. Detector updates,
queued IPC, player replacement and attribute mutations must be correlated before
claiming which currently visible element/attribute caused one Java sample.
[Attribute handler](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/third_party/blink/renderer/core/html/media/html_video_element.cc#b1290).

General `PictureInPictureControllerImpl::IsElementAllowed` additionally checks
system settings, Permissions Policy, metadata and video-track availability, etc.
Those checks govern other PiP availability/API paths. They must not be silently
substituted for the simple attribute test producing this fullscreen enum.

## Consumer chain

1. MediaWebContentsObserver getter -> WebContentsImpl C++ getter ->
   WebContentsAndroid -> JNI -> Java WebContentsImpl. These wrappers do not turn
   false into true. [Native public getter](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/content/browser/web_contents/web_contents_impl.cc#b10050), [JNI wrapper](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/content/browser/web_contents/web_contents_android.cc#b817).
2. Actual fresh `FullscreenVideoPictureInPictureController.canDoPictureInPicture`
   requires `hasActiveEffectivelyFullscreenVideo()` AND
   `isPictureInPictureAllowedForFullscreenVideo()`. Failure records
   `no_allowed_fullscreen_video`. Other later checks include device support,
   existing PiP, configuration/finishing and recent-task state.
3. `updateAutoPictureInPictureStatusIfNeeded` passes this allowed value into
   Phase1 `updateCandidate`; false prevents an upstream-eligible candidate.
   It also uses allowed for Android auto-enter parameters.
4. `attemptPictureInPicture` records ENTRY_ATTEMPT, checks canDo, and on false
   returns after ENTRY_SUPPRESSED, before Phase1 beginEntry or framework API.
   On true it builds parameters and reaches enterPictureInPictureMode.
5. Framework callback can use Chromium's existing route independently of a
   Phase1 mobile-only owner. Desktop wrong_host does not block that upstream
   route; ACTIVE_ADOPTION path=upstream_entered is not proof of a Phase1 owner.

See the versioned [Phase1 patch and diagnostic hooks](../../../tools/youtube_pip_phase1/chromium.patch)
and [Phase1 policy](../../../tools/youtube_pip_phase1/java/org/chromium/chrome/browser/media/VersaniumYouTubePictureInPicturePolicy.java).

## Q3: fullscreen true with allowed false

This is an explicitly supported state, not an inconsistency. A video can occupy
the fullscreen presentation and be actively playing while its last renderer
status is FullscreenAndPictureInPictureDisabled. `HasActiveEffectivelyFullscreenVideo`
checks WebContents fullscreen, a recorded player, playing and has_video; it does
not check the allowed bit. The allowed getter returns the independently cached
false. In the normal producer path that disabled enum was selected because the
video carried disablepictureinpicture when sampled. Removing the HTML attribute
later does not prove the cached value already changed.

## Q4–Q6: what explains mobile versus desktop, and what remains unknown?

The code-established boundary is the renderer's attribute-derived fullscreen
status and browser cache. Given the supplied samples, mobile's selected player
last delivered the disabled enum and desktop's the enabled enum. Under the
verified production producer this implies **attribute present versus absent at
the corresponding producer sample**, not a claim about the current DOM or writer.

| Input | Role in this specific bit |
|---|---|
| disablePictureInPicture attribute on sampled video | Direct producer condition |
| HTML fullscreen and viewport geometry | Direct prerequisite for fullscreen enum |
| Per-frame/player identity and latest status | Direct selection/cache identity |
| UA / desktop-site toggle | No direct branch here; correlated site-response/player change is a hypothesis |
| YouTube mweb vs desktop player implementation/experiment flags | Plausible upstream attribute writer; exact writer/version unconfirmed |
| MediaSession detected/active | Not producer of allowed bit; independent media/session state |
| General Permissions Policy / JS PiP API availability | Separate availability paths; not tested by this producer expression |
| Android PiP support | Later browser entry gate; desktop control demonstrates it works in this trial |

Chromium computes fullscreen geometry and consumes the site's/player's HTML
opt-out attribute; it is neither a site-origin allowlist nor an Android permission
grant. The site can supply the attribute in markup or manipulate the reflected
DOM property. This investigation has not captured the live YouTube script or DOM,
so it cannot attribute the setting to a particular YouTube routine/experiment,
prove its current value, or prove that changing UA alone is causal. **That part of
the root cause remains unconfirmed.** No hardcoded mobile/desktop YouTube branch
was found in the traced producer/consumer methods.

## Q7: Phase1 design fit

The current upstream dependency is safe for preserving Chromium's permission
contract. It cannot rescue the reported mobile case: false prevents candidate
creation and entry before session/lifecycle stabilization can help. Phase1's
approved Java-only scope is lifecycle preservation for an eligible session,
not a replacement permission producer or background playback implementation.
Thus it is structurally insufficient as a general mobile YouTube PiP solution
for a player explicitly reporting fullscreen-PiP disabled. This is a scope/design
limitation revealed by the device evidence, not proof that candidate generations
or observer ordering are broken. [Approved scope](approved-design.txt).

## Tab-switch trace and separate pause uncertainty

1. `TabModelSelectorImpl.requestToShowTab` hides the old initialized attached tab
   with CHANGED_TABS before showing the incoming one (around413–429).
2. `TabImpl.hide` marks hidden and updates WebContents visibility before onHidden
   observers (1428–1441); updateWebContentsVisibility maps hidden to HIDDEN,
   subject to offscreen/occlusion conditions (1333–1347).
3. Java WebContents -> native WebContentsAndroid -> WebContentsImpl visibility
   update -> RenderViewHost/PageLifecycleStateManager -> PageBroadcast lifecycle
   IPC -> Blink WebViewImpl visibility notifications. Its observer notification
   reaches RendererWebMediaPlayerDelegate.OnPageVisibilityChanged.
4. That delegate treats visible and hidden-but-painting as shown; hidden calls
   each player's OnPageHidden. WebMediaPlayerImpl then updates background video
   optimization and play state. [Renderer visibility handler](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/content/renderer/media/renderer_web_media_player_delegate.cc#b192).
5. `ShouldPausePlaybackWhenHidden` checks frame policy, audio preservation,
   background-video support, actual video PiP, flinging/capture and background
   suspend/resume settings. It does **not** read disablepictureinpicture or the
   browser's fullscreen allowed bool. If its pause conditions hold,
   PauseVideoIfNeeded -> client PausePlayback(reason) -> HTMLMediaElement
   PauseInternal. [Background pause predicate](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/third_party/blink/renderer/platform/media/web_media_player_impl.cc#b3744).
6. Site JavaScript may separately react to visibilitychange and call pause(),
   which enters PauseInternal(kPauseCalled). MediaSession can also receive a
   UI/system suspend -> MediaSessionController.OnSuspend -> RequestPause.
   Conversely media pause notifies MediaWebContentsObserver.OnMediaPaused ->
   session manager OnPause. MediaSession CONTENT suspension explicitly means
   playback already paused; a session inactive callback alone cannot name the
   first cause. [Session suspend distinction](https://chromium.googlesource.com/chromium/src/+/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/content/browser/media/session/media_session_impl.cc#b985).

`WebMediaPlayerImpl::SetIsEffectivelyFullscreen` reduces both enabled and disabled
fullscreen enums to the same fullscreen=true; it does not retain their permission
distinction as its hidden-playback decision. Existing PiP can protect playback in
some hidden branches, so failure to enter PiP may indirectly affect Home behavior.
That is not evidence of a common initiating cause for tab-switch stopping.

Conclusion: visibility/background policy, site pause and session suspend are
separate candidate paths. The first executed pause caller and relevant per-player
background flags in the mobile/desktop trials remain unknown. Do not equate the
tab-switch defect with the attribute-based PiP gate without that evidence.

## Brave comparison (design only)

Correct reference is [brave/brave-core PR36838](https://github.com/brave/brave-core/pull/36838),
pin `4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2`, not the unrelated
brave-browser issue with that number.

- Its FullscreenVideoPictureInPictureController patch/rewrite inserts the Brave
  delegated attempt immediately before Chromium's existing framework try block;
  it does not remove the earlier canDo false-return. The normal auto route still
  requires upstream fullscreen permission. [Pinned rewrite](https://github.com/brave/brave-core/blob/4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2/rewrite/chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java.yaml).
- Brave also has a distinct manual/native-helper route: the YouTube helper uses
  feature + mobile watch URL + document-loaded eligibility; Java native helper
  checks Activity/config/device and can call framework entry without that same
  canDo predicate. It relies on other page/fullscreen preparation and must not
  be treated as equivalent to the delegated auto path. [Native helper](https://github.com/brave/brave-core/blob/4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2/android/java/org/chromium/chrome/browser/youtube_script_injector/BraveYouTubeScriptInjectorNativeHelper.java).
- At the **same36838 pin**, `youtube_script_injector_tab_helper.cc` already has
  `kYoutubePictureInPictureSupport`. It rewrites the MWEB_WATCH player's serialized
  YouTube experiment flags for PiP blocking on timeupdate, resize, document
  fullscreen and standard API. This changes page configuration, not Chromium's
  browser permission field. It is a concrete complementary mechanism addressing
  mobile player blocking, but not proof of which flag set the attribute in our
  specific trial. The feature is enabled by default at the pin; runtime/site
  execution and effect are not device-verified here. [Pinned helper](https://github.com/brave/brave-core/blob/4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2/browser/android/youtube_script_injector/youtube_script_injector_tab_helper.cc),
  [feature defaults](https://github.com/brave/brave-core/blob/4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2/browser/android/youtube_script_injector/features.cc).
- Its separate background playback script filters visibilitychange listener
  registration and overrides document.visibilityState to visible, gated by
  background feature/preference. This complements background playback and is
  absent from the deliberately restricted Phase1 port.
- [PR33522](https://github.com/brave/brave-core/pull/33522) concerns YouTube
  background playback; historical head fb072ca5a060189992575106ede30c722f522d03
  contains the visibility and PiP-support scripts. Its concerns are broader than
  Java session cleanup. [PR39765](https://github.com/brave/brave-core/pull/39765)
  addresses Chromium153+ onStop/screen-lock suspension/fullscreen retention;
  it does not explain the initial attribute-derived permission false.

The port omitted these preexisting/complementary prerequisites by approved scope,
not by an accidental missing Java line identified in this review. Extracting36838
session management alone does not establish equivalent Brave mobile behavior.
No script/manual/#33522/#39765 functionality is implemented or proposed for
automatic application in this task.

## Safe design candidates, not implementations

A. **Recommended next step:** review a minimal diagnostic plan that correlates
the actual renderer producer, browser receiver and first pause source. Preserve
all eligibility and playback decisions. Select a product fix only after evidence.

B. Retain Chromium's opt-out contract and explicitly scope this Phase1 to already
upstream-eligible sessions. Safe current behavior, but does not solve mobile FAIL.

C. In a separately approved design review, evaluate an explicit user-intent entry
and its independent eligibility/page prerequisites, informed by Brave's complete
architecture. Review site opt-out semantics, user activation, fullscreen/session
ownership and lifecycle separately. This is not approval to force the allowed bit,
blindly bypass eligibility, inject scripts, add toolbar entry or broaden hosts.
None of those changes is made here; no behavior fix can yet be recommended as
proven to solve both entry and tab-switch stopping.

RECOMMENDED_FIX=A_DIAGNOSTIC_PLAN_REVIEW_BEFORE_PRODUCT_FIX

## Additional instrumentation required to finish the unresolved questions

ADDITIONAL_INSTRUMENTATION_REQUIRED=YES (exact page writer/timing and first pause;
NO additional instrumentation is needed to establish the source chain above).

Proposed only, STOP before implementation/build:

- Renderer ReportEffectivelyFullscreen: document/frame/player correlation token,
  monotonic sequence, fullscreen result, attribute-present boolean, output enum.
- Attribute-change notification: same correlation and old/new presence, without
  DOM contents, UA string, video ID/query, account data or page script payload.
  Presence transitions locate timing; exact JS writer would still require a
  controlled renderer stack/DevTools investigation, not guessed attribution.
- Browser receiver: received player/frame identity, status, selected-player change
  and cached allowed value; correlate to Java sample and navigation epoch.
- First pause: renderer hidden-state predicate inputs/background flags and
  PauseReason (page/frame hidden vs pause-called etc.), plus UI/system/content
  suspend origin at the existing media IPC/session boundary. A generic pause
  notification after the fact cannot substitute for this first-caller evidence.

Keep callback lifetimes, native getter preconditions and process correlations
explicit; no behavior changes, force resume, script injection or unguarded getter.
Native diagnostics would exceed this task's source-only scope and need next-step
review. No instrumentation, GN, compilation or APK work has been started.

## Verification and prohibited operations

Zoom protected24 Git blobs PASS at start; retired34 paths absent. Final docs-only
diff must retain all non-Markdown Git blob identities and the fresh source receipt.
Existing JVM415/bundle5/default-off/parse5 are historical PASS, not rerun or claimed
as new tests. No product change warrants a new compile/test build in this task.
Source lists/imports/nullability/observer lifecycle remain unchanged.
ZOOM_PRODUCT_CODE_CHANGED=NO. F11_CHANGED=NO. BRANDING_CHANGED=NO.
No signing/package/pin changes, GN/build/Actions/APK/ADB/install, saved Run9 access,
merge/release/tag/Production or PR-ready transition. PR body is read-only.
Source of Truth: local Versanium-Context_v1.23.md plus repository checkpoint docs;
external ChatGPT Project Sources/Notion replacement is not claimed automatic.
